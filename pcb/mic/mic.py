"""MIC: modulo microfono (dec. 97), scheda principale col C96. Bozza v0.1.

Catena (docs/fase4/mic-mono-moduli.md §2, §3, §5, REV dec. 111 e dec. 145):
 XLR -> RFI + clamp -> INA +30 dB fisso -> differenziale -> passa-alto 60 Hz -> GAIN 0...+30 dB
     -> PRE (detector del LED) -> EQ2 -> POSTEQ -> VCA del MUTE e del limiter -> POST
     -> driver MSUM6 L/R (invertenti, todo 227) + 4 mandate.

Polarità (sistema-polarita.md): differenziale -1 (caldo sull'ingresso -, come sim/mic/mic-pre.inc:
lo scambio della REV dec. 145 è tolto, todo 227), stadio 2 -1, EQ2 +1, VCA + I/V +1 (datasheet
THAT 2181 Rev 03 p. 7) -> POST +1. Driver MSUM -1, [A2] -1 -> +1 all'XLR del master.

Pot, LED e tasto MUTE stanno sulla scheda comandi dietro il pannello (cavo J2, da disegnare:
pcb/mic/NOTE.md). XLR su un cavo a J3: la sua posizione sul pannello non è decisa.
Fonti: sim/mic/mic-pre.inc, sim/mic/mic-limiter.cir, sim/fx/fx-eq2-pot10k.cir, master-segnale.py.
Valori [PROVVISORIO]. Le scelte non scritte nei documenti sono segnate NOTA (pcb/mic/NOTE.md).
"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
import pcbgen
from pcbgen import Design
import celle_micmono as cm
from celle_micmono import opa2, opa4, diode, C12, VCA, TRIM

class MicDesign(Design):
    """Design del generatore più una regola di piazzamento locale (todo 248): i C a montaggio
    superficiale di un regolatore U (stesso blocco, una rete non di massa su un pin del
    regolatore) si legano a quel pin come i 100n degli op-amp, e viaggiano col chip. Prima
    il piazzamento a file li metteva a 13-20 mm dal pin (A1 del controllo audio)."""

    def _decaps(self):
        groups = super()._decaps()
        regs = set(self.audio_rules.get("regolatori", []))
        taken = {c for caps in groups.values() for c, _ in caps}
        for u in self.parts:
            if u.ref not in regs or not u.ref.startswith("U") or u.place:
                continue
            used = {pin for _, pin in groups.get(u.ref, [])}
            for c in self.parts:
                if not c.ref.startswith("C") or c.block != u.block or c.place or c.ref in taken \
                        or not pcbgen._smd(c.fp):
                    continue
                sup = [n for n in c.nets.values() if n and n not in self.masse]
                if len(sup) != 1 or sup[0] not in self.power:
                    continue      # solo i C di un'alimentazione: SETP/SETN lasciano posto al fanout del pin 9
                pins = [k for k, n in sorted(u.nets.items()) if n == sup[0] and k not in used]
                if pins:
                    groups.setdefault(u.ref, []).append((c.ref, pins[0]))
                    self._regpins[c.ref] = pins
                    used.add(pins[0])
                    taken.add(c.ref)
        return groups

    _regpins = {}

    def route(self, pcb, passes=40):
        """Freerouting fino a d.route_tries volte (4), finché non resta niente di aperto (todo 248).

        Perché cambia da un giro all'altro: il piazzamento è identico, ma la scheda scritta da
        build_pcb tiene pezzi e pin in un ordine diverso a ogni costruzione, il .dsn lo eredita e
        Freerouting dà un risultato diverso per ogni ordine. Rileggere lo stesso file dà lo stesso
        ordine e lo stesso risultato (tre tentativi sulla stessa scheda: tre volte lo stesso
        aperto; anche esportando il .dsn in un processo nuovo). Per questo ogni nuovo tentativo
        ricostruisce la scheda con build_pcb e cambia il numero massimo di passate (-mp 40, poi
        20, 30): Freerouting oscilla fra due stati dalla passata ~14 e si ferma in uno diverso.
        Il controllo è il DRC di kicad-cli sugli errori (aperti e distanze), con le colate di
        massa come nel giro vero e le classi del .kicad_pro. Resta il tentativo che passa (o
        l'ultimo). Un PASSA al secondo o terzo tentativo è scritto nelle note del riepilogo."""
        import shutil
        import pcbnew
        import json
        import subprocess
        prova = os.path.join(self.outdir, "out", "prova-routing.kicad_pcb")
        prova_pro, prova_drc = prova[:-len(".kicad_pcb")] + ".kicad_pro", prova + ".drc.json"
        tries = getattr(self, "route_tries", 4)
        esiti = []
        for k in range(tries):
            if k:
                n = len(self.notes)
                pcb = self.build_pcb()
                del self.notes[n:]          # le note del piazzamento sono già scritte
            mp = passes if k == 0 else (20, 30, 15)[(k - 1) % 3]
            res = super().route(pcb, mp)
            sig = {n: c for n, c in res.get("aperti", {}).items() if n not in (self.gnd, "CHASSIS")}
            shutil.copy(pcb, prova)
            shutil.copy(os.path.join(self.outdir, self.name + ".kicad_pro"), prova_pro)
            self.pours(prova)
            subprocess.run([pcbgen.CLI, "pcb", "drc", "--format", "json", "--severity-error",
                            "-o", prova_drc, prova], capture_output=True)
            rep = json.load(open(prova_drc)) if os.path.exists(prova_drc) else {}
            unc = len(rep.get("unconnected_items", []))
            tipi = {}
            for v in rep.get("violations", []):
                if v.get("severity") == "error":
                    tipi[v.get("type")] = tipi.get(v.get("type"), 0) + 1
            dist = sum(tipi.values())
            esiti.append("giro %d (-mp %d): %s, DRC %d aperti, errori %s" % (k + 1, mp, sig or "Freerouting chiuso", unc, tipi or 0))
            if res.get("ok") and not sig and unc == 0 and dist == 0 and rep:
                break
        for f in (prova, prova_pro, prova_drc, prova[:-len(".kicad_pcb")] + ".kicad_prl"):
            if os.path.exists(f):
                os.remove(f)
        self.notes.append("Freerouting (mic.py, %d tentativi al più): %s" % (tries, "; ".join(esiti)))
        res["tentativi"] = len(esiti)
        return res

    def _attach(self, fps, ic, caps):
        """Il C di un regolatore va sul pin d'angolo (il più lontano dal centro) fra quelli della
        sua rete: sul pin di mezzo copriva il pin 9 di massa dell'LT3094, che restava senza via."""
        c0, used, out = fps[ic].GetPosition(), set(), []
        pads = {pd.GetNumber(): pd.GetPosition() for pd in fps[ic].Pads()}
        for cref, pin in caps:
            cand = [k for k in self._regpins.get(cref, []) if k in pads and k not in used]
            if cand:
                pin = max(cand, key=lambda k: (pads[k].x - c0.x) ** 2 + (pads[k].y - c0.y) ** 2)
            used.add(pin)
            out.append((cref, pin))
        super()._attach(fps, ic, out)

    def _fanout(self, b, net, mm, pcbnew):
        """Fanout del generatore, poi una seconda ricerca per i pad di massa rimasti senza via
        (todo 248): un pad di massa senza via lascia un'isola di colata su F.Cu o B.Cu, e il DRC
        dava «unconnected» a giri alterni (U45.9, C56, C61, il pad esposto di U44).
        - pad esposto (lato corto >= 1,5 mm): via al centro;
        - altri: 8 direzioni, distanze crescenti fino a 2,5 mm, con gli stessi controlli del
          generatore (niente pad di altre reti sulla via o sulla pista, 0,85 mm da un'altra via)."""
        super()._fanout(b, net, mm, pcbnew)
        code = net.GetNetCode()
        vias = [t.GetPosition() for t in b.GetTracks() if t.GetClass() == "PCB_VIA" and t.GetNetCode() == code]
        altri = [pd for f in b.GetFootprints() for pd in f.Pads() if pd.GetNetCode() != code]
        X0, Y0, (W, H) = 50.0, 50.0, self.board
        n_ep = n = saltate = 0

        def add(pad, vp, track):
            v = pcbnew.PCB_VIA(b)
            v.SetPosition(vp)
            v.SetWidth(mm(0.6))
            v.SetDrill(mm(0.3))
            v.SetNet(net)
            b.Add(v)
            vias.append(vp)
            if track:
                t = pcbnew.PCB_TRACK(b)
                t.SetStart(pad.GetPosition())
                t.SetEnd(vp)
                t.SetWidth(mm(0.4))
                t.SetLayer(pcbnew.F_Cu if pad.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu)
                t.SetNet(net)
                b.Add(t)

        for fp in b.GetFootprints():
            for pad in fp.Pads():
                if pad.GetNetCode() != code or pad.GetAttribute() != pcbnew.PAD_ATTRIB_SMD:
                    continue
                pp, sz = pad.GetPosition(), pad.GetSize()
                reach = max(sz.x, sz.y) / 2 + mm(1.0)
                if any((v.x - pp.x) ** 2 + (v.y - pp.y) ** 2 <= reach ** 2 for v in vias):
                    continue
                if min(sz.x, sz.y) >= mm(1.5):
                    add(pad, pp, False)
                    n_ep += 1
                    continue
                vp = None
                for dist in (0.75, 1.0, 1.3, 1.7, 2.1, 2.5):
                    for k in range(8):
                        a = math.radians(45 * k)
                        ex = abs(math.cos(a)) * sz.x / 2 + abs(math.sin(a)) * sz.y / 2
                        r = ex + mm(dist)
                        cand = pcbnew.VECTOR2I(int(pp.x + r * math.cos(a)), int(pp.y + r * math.sin(a)))
                        if not (X0 + 1.2 < cand.x / 1e6 < X0 + W - 1.2 and Y0 + 1.2 < cand.y / 1e6 < Y0 + H - 1.2):
                            continue
                        mids = [pcbnew.VECTOR2I(pp.x + (cand.x - pp.x) * j // 4, pp.y + (cand.y - pp.y) * j // 4)
                                for j in (1, 2, 3)]
                        lay_ok = lambda o: o.IsOnLayer(pcbnew.F_Cu if pad.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu)
                        if any(o.HitTest(cand, mm(0.3 + 0.25)) for o in altri):
                            continue
                        if any(lay_ok(o) and o.HitTest(q, mm(0.2 + 0.2)) for o in altri for q in mids):
                            continue
                        if any((cand.x - q.x) ** 2 + (cand.y - q.y) ** 2 < mm(0.85) ** 2 for q in vias):
                            continue
                        vp = cand
                        break
                    if vp:
                        break
                if vp is None:
                    saltate += 1
                    continue
                add(pad, vp, True)
                n += 1
        self.notes.append("fanout di massa, seconda ricerca (mic.py): %d via, %d nei pad esposti, %d ancora senza"
                          % (n, n_ep, saltate))

d = MicDesign("mic", HERE, "maelcum MIC (dec. 97) - bozza v0.1", board=(100, 220), rev="0.1-bozza")
d.gnd = "AGND"
d.inner_signal = True     # SMD sui due lati (dec. 142): In2 strato di piste, massa piena su In1, come master e canale
d.cluster_gap = 0.8      # 0,5 di default: SMB e MUTE_CV (U7, retro) restavano aperte (todo 248)
d.link_pairs = True   # pin gemelli del C96 (+5V, CTRL_GND): Freerouting li lasciava aperti (todo 248)

from cavo import CAVO as FILI     # ordine dei fili: cavo.py, letto anche dalla scheda comandi

d.block = "BACKPLANE C96 (classe MIC/GEN, MSUM6)"
cm.backplane(d, "MSUM6")

d.block = "ALIMENTAZIONE +-18 audio, +-15 switch, +5, +-15 LN"
cm.power_18_sw(d, blocco="ALIM")   # un blocco per regolatore coi suoi C: A1 (todo 248)
cm.power_ln(d, blocco="ALIM")
d.power_nets("+18V", "-18V", width=0.4)   # NOTA: a 0,6 mm Freerouting lasciava -18V aperta (todo 237)

# ------------------------------------------------------------ ingresso
d.block = "INGRESSO XLR: RFI, clamp, carico 2,32k, bias 2x47k (mic-pre.inc)"
d.part("J", "Connector_Generic:Conn_01x03", "XLR (cavo)", "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical",
       {1: "CHASSIS", 2: "XHOT", 3: "XCOLD"}, ref="J3", place=(85, 5, 90),
       note="NOTA: cavo verso l'XLR femmina; pin 1 a CHASSIS al connettore (grounding §4)")
for x, f, i in (("XHOT", "HF", "IH"), ("XCOLD", "CF", "IC")):
    d.part("FB", "Device:FerriteBead_Small", "ferrite 600R", cm.FB, {1: x, 2: f})
    d.C(f, "CHASSIS", "100p C0G", note="RFI verso il telaio")
    d.R(f, i, "10 1%", note="limita la corrente dei clamp")
    diode(d, i, "+15LN", note="NOTA: clamp 1N4148W al posto del BAV199 (pinout non verificato)")
    diode(d, "-15LN", i)
    d.R(i, "AGND", "47k 1%", note="bias di modo comune (CMRR 74 dB)")
d.R("IH", "IC", "2k32 1%", note="Zin differenziale 2,26 kOhm")

d.block = "INA +30,05 dB e differenziale unity (OPA1612)"
d.R("O1", "F1", "499 0.1%")
d.R("O2", "F2", "499 0.1%")
d.R("F1", "F2", "32.4 0.1%", note="Rg: G1 = 1 + 998/32,4 = 31,8")
opa2(d, "U1", ("IH", "F1", "O1"), ("IC", "F2", "O2"), "+15LN", "-15LN", note="coppia INA")
d.R("O1", "DN", "1k 0.1%", note="caldo sull'ingresso -: il differenziale inverte (todo 227)")
d.R("DN", "S1", "1k 0.1%")
d.R("O2", "DP", "1k 0.1%")
d.R("DP", "AGND", "1k 0.1%")
opa2(d, "U2", ("DP", "DN", "S1"), ("AGND", "NU2", "NU2"), "+15LN", "-15LN",
     note="differenziale; seconda sezione libera, inseguitore a massa")

d.block = "PASSA-ALTO 60 Hz, STADIO 2 (0...+30 dB), DETECTOR del LED (OPA1654)"
d.C("S1", "K1", "220n C0G", "Capacitor_SMD:C_1210_3225Metric")
d.C("K1", "K2", "220n C0G", "Capacitor_SMD:C_1210_3225Metric")
d.R("K1", "HP", "8k45 0.1%")
d.R("K2", "AGND", "16k9 0.1%", note="R_fb = R_gnd/2: Butterworth")
d.R("HP", "GP1", "332 0.1%")
d.R("GP2", "PRE", "5k36 0.1%")
d.C("GINV", "PRE", "22p C0G")
sd, sb = cm.detector(d, "PRE")
opa4(d, "U3", ("K2", "HP", "HP"), ("AGND", "GINV", "PRE"), sd, sb, "+15LN", "-15LN",
     note="passa-alto, stadio 2 (pot GAIN 5k sul cavo: GP1-GINV-GP2), superdiodo e buffer del LED")

d.side = "B"  # 206 impronte: LED e VCA/limiter (solo SMD) sul retro, dec. 142 (todo 237)
d.block = "LED tricolore (LM339)"
cm.led3(d, "+15LN", "133k")

d.side = "F"   # EQ2 davanti: sul retro -18V restava aperta (11 tratti)
d.block = "EQ2 (+-18)"
cm.eq2(d, "U4", "PRE", "POSTEQ")
d.side = "B"

# ------------------------------------------------------------ VCA del MUTE e limiter
d.block = "VCA del MUTE e del limiter (dec. 111, 145; sim/mic/mic-limiter.cir)"
d.R("POSTEQ", "VIN", "20k 0.1%")
d.part("U", VCA, "V2181L", cm.SOIC8, {"IN": "VIN", "EC+": "AGND", "EC-": "ECM", "SYM": "SYM",
                                      "OUT": "NIV", "V+": "+15LN", "GND": "AGND", "V-": "VEE"}, ref="U5")
d.R("VEE", "-15LN", "5k1", note="valore del datasheet a -15 V (master: 6,19k a -18 V)")
d.C("+15LN", "AGND", "100n")
d.C("AGND", "-15LN", "100n")
d.part("RV", "Device:R_Potentiometer_Trim", "50k", TRIM, {1: "+15LN", 2: "SWSYM", 3: "-15LN"},
       note="trim di simmetria (vca-trim §3.1)")
d.R("SWSYM", "SYM", "150k")
d.R("SYM", "AGND", "51")
d.R("NIV", "POST", "20k 0.1%")
d.C("NIV", "POST", "47p C0G")
# raddrizzatore a doppia semionda: HW = -POST per POST > 0; RECT = 0,5 |POST|
d.R("POST", "RAN", "10k 0.1%")
d.R("RAN", "HW", "10k 0.1%")
diode(d, "HW", "RAO")
diode(d, "RAO", "RAN")
d.R("POST", "RBN", "20k 0.1%")
d.R("HW", "RBN", "10k 0.1%")
d.R("RBN", "RECT", "10k 0.1%")
# picco: superdiodo, Ratt 1k, Ch 1u, Rrel 1M; lisciatura Rs 100, Cs 1u
diode(d, "SDO", "SDK", note="diodo del superdiodo")
d.R("SDK", "PK", "1k", note="attacco 1 ms")
d.C("PK", "AGND", "1u C0G", C12, note="Ch: C0G o film")
d.R("PK", "AGND", "1M", note="rilascio 1 s (variante 2)")
d.R("PK", "SM", "100")
d.C("SM", "AGND", "1u C0G", C12, note="Cs: lisciatura 0,1 ms")
opa4(d, "U6", ("AGND", "NIV", "POST"), ("AGND", "RAN", "RAO"), ("AGND", "RBN", "RECT"), ("RECT", "SDK", "SDO"),
     "+15LN", "-15LN", note="I/V del VCA, raddrizzatore A e B, superdiodo")
# errore: D = 0,625 (VTH - SM), VTH = 2,18 V; LIM = max(-D, 0)
d.R("SMB", "SUBN", "16k 0.1%", note="NOTA: inseguitore su SM, così il sottrattore non carica Ch")
d.R("SUBN", "DSUB", "10k 0.1%", note="G = 10k/16k = 0,625")
d.R("+15LN", "SUBP", "169k 0.1%", note="SUBP = 0,838 V = VTH x 10/26: VTH 2,179 V")
d.R("SUBP", "AGND", "10k 0.1%")
d.C("SUBP", "AGND", "100n")
d.R("DSUB", "HN", "10k 0.1%")
d.R("HN", "LIM", "10k 0.1%", note="Rf: a riposo LIM a massa virtuale (11k con Ra)")
diode(d, "HO", "LIM")
diode(d, "HN", "HO")
# MUTE: tasto (sul cavo, verso +5VF) -> partitore 10k/10k -> 220n (1,1 ms) -> inseguitore -> 2,5 V
d.R("MUTE_SW", "MRC", "10k", note="NOTA: tasto a ritenuta fra +5VF e MUTE_SW, come il MONO del master")
d.R("MRC", "AGND", "10k")
d.C("MRC", "AGND", "220n C0G", C12, note="rampa 1,1 ms (dec. 111)")
opa4(d, "U7", ("SM", "SMB", "SMB"), ("SUBP", "SUBN", "DSUB"), ("AGND", "HN", "HO"), ("MRC", "MUTE_CV", "MUTE_CV"),
     "+15LN", "-15LN", note="inseguitore di SM, sottrattore, mezza onda, inseguitore del MUTE")
d.R("LIM", "ECM", "1k 0.1%", note="Ra")
d.R("MUTE_CV", "ECM", "2k 0.1%", note="Rb: MUTE 2,5 V -> +0,79 V al pin = -129 dB")
d.R("ECM", "AGND", "1k 0.1%", note="Rc")

d.side = "F"
# ------------------------------------------------------------ uscite
d.block = "DRIVER MSUM6 L/R (invertenti, todo 227)"
cm.msum_drivers(d, "U8", "POST", "MSUM6")
d.block = "MANDATE S1-S4 (pot sul cavo, mute globale, iniezione)"
cm.sends(d, "U9", "U10")

d.block = "CAVO SCHEDA COMANDI (J2)"
cm.cavo(d, FILI)

d.audio_rules = {
    "sensibili": r"^(NB|NSH|NVH|NHB|GINV|F1|F2|DN|DP|IH|IC|VIN|NIV|NDR_[LR]|INJ\d|S\d_OUT_[LR]|MSUM6_[LR])$",
    "cavo": r"^(NA|NB|NC|GP1|GINV|GP2|VHN|WPH|VHP|SW\d)$",
    "rumorose": r"^(\+15SW|-15SW|SMUTE_N|MUTE_G|GLOBAL_MUTE|\+5VF?|LT|LQ|KR|KG|GFD|LK[RG]|MUTE_SW|V27F[+-]|VREG[+-]|BASE[+-]|RAW.*|CTRL_GND)$",
    "regolatori": ["U40", "U41", "U42", "U43", "U44", "U45", "Q40", "Q41"],
}

if __name__ == "__main__":
    d.build(route="--no-route" not in sys.argv)
