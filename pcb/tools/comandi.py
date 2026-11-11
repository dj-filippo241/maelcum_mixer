"""Celle delle schede comandi sulla disposizione F (todo 270, dec. 133, 172, 176).

Una scheda comandi sta parallela al pannello e si regge sui dadi dei pot. Ogni pezzo cade sul
foro del render: le posizioni vengono da docs/pannelli/coordinate.json (solo lettura). Un cavo
piatto la collega alla scheda di segnale: stesso ordine dei pin sui due connettori.

Modello: pcb/fx-send/fx-send-comandi.py e celle_micmono.scheda_comandi (FX-SEND, MIC, MONO).
Qui in più: pot doppi, fader, levette, bottoni con luce, barre LED con LM3915, jack.

Pezzi e impronte (tutte della libreria di KiCad: il generatore non ne carica altre):
- Pot: Alps RK09L verticale, singolo o doppio. Pin 1 = fine corsa antiorario, 2 = cursore,
  3 = orario (catalogo Alps RK09L rev. 2510, disegni 7-8: pcb/fx-send/NOTE.md punto 10).
  I pot di classe 14 mm (RK14K, sistema-comandi.md) usano la stessa impronta: KiCad non ha
  l'RK14. Il riquadro d'ingombro tiene conto del corpo da 14 mm. [NOTA, come FX-SEND e MIC]
- Fader: Bourns PTA6043 (corsa 60) e PTA4543 (corsa 45), mono. Pin 1 e 3 = capi, 2 = cursore;
  pin 1 e 2 allo stesso capo (datasheet Bourns pta.pdf, pagina 2). [NOTA: sistema-comandi.md
  non nomina il pezzo; è il fader mono a catalogo con l'impronta in KiCad]
- Levetta: impronta NKK G1xJP (ultra-miniatura, 6 pin a passo 2,54). SEGNAPOSTO: il pezzo
  non è scelto (sistema-comandi.md: «levetta sigillata», «levetta sub-miniatura») e il
  datasheet NKK non si scarica da qui. Pinout da rifare col pezzo vero.
- Bottone con luce a ritenuta: impronta NKK GW12LJP (6 pin a passo 2,54). SEGNAPOSTO: il
  pezzo non è scelto. Simbolo TASTO_LUCE: due contatti e il LED.
- Barra LED: LED rettangolari 5 x 2 mm a foro passante, uno per segmento, e un LM3915 per
  10 segmenti (sistema-metering.md §3). Pinout dell'LM3915 dal simbolo KiCad LM3914N
  (stesso contenitore DIP-18; il datasheet TI non si scarica da qui: da verificare).
- LED di livello a tre colori: LED bicolore a 3 pin, come MIC e MONO (celle_micmono).
- Jack cuffie: Neutrik NJ3FD-V verticale (pad T, R, S dell'impronta KiCad).
"""
import ast, json, math, os, sys
from pcbgen import Design, DesignRiprova, boxsym, FPDIR

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")

POT1_FP = "Potentiometer_THT:Potentiometer_Alps_RK09L_Single_Vertical"
POT2_FP = "Potentiometer_THT:Potentiometer_Alps_RK09L_Double_Vertical"
POT1 = boxsym("POT_SINGLE", [("1", "CCW", "passive"), ("2", "W", "passive"), ("3", "CW", "passive")],
              [("MP", "MP", "passive")], ref="RV", fp=POT1_FP,
              desc="Pot singolo, Alps RK09L verticale; MP = staffe, a massa telaio attraverso il pannello")
POT2 = boxsym("POT_DUAL", [
    ("1", "A_CCW", "passive"), ("2", "A_W", "passive"), ("3", "A_CW", "passive"), ("MP", "MP", "passive")], [
    ("4", "B_CCW", "passive"), ("5", "B_W", "passive"), ("6", "B_CW", "passive")],
    ref="RV", fp=POT2_FP,
    desc="Pot doppio, Alps RK09L verticale; MP = staffe, a massa telaio attraverso il pannello")
FADER_FP = {60.0: "Potentiometer_THT:Potentiometer_Bourns_PTA6043_Single_Slide",
            45.0: "Potentiometer_THT:Potentiometer_Bourns_PTA4543_Single_Slide"}
FADER_ANCORA = {60.0: (36.75, 1.75), 45.0: (29.25, 1.75)}      # centro della corsa
FADER = boxsym("FADER_MONO", [("1", "CAPO_1", "passive"), ("2", "W", "passive"), ("3", "CAPO_3", "passive")],
               [("MP", "MP", "passive")], ref="RV",
               desc="Fader mono Bourns PTA; pin 1 e 2 allo stesso capo, pin 3 all'altro")
LEV_FP = "Button_Switch_THT:SW_NKK_G1xJP"
LEVETTA = boxsym("LEVETTA", [("1", "A1", "passive"), ("2", "A_COM", "passive"), ("3", "A3", "passive")],
                 [("6", "B1", "passive"), ("5", "B_COM", "passive"), ("4", "B3", "passive")], ref="SW", fp=LEV_FP,
                 desc="Levetta a due vie; SEGNAPOSTO, pinout da rifare col pezzo scelto")
BOT_FP = "Button_Switch_THT:SW_NKK_GW12LJP"
BOTTONE = boxsym("TASTO_LUCE", [("1", "P1A", "passive"), ("2", "P1B", "passive"), ("3", "LED_A", "passive")],
                 [("4", "P2A", "passive"), ("5", "P2B", "passive"), ("6", "LED_K", "passive")], ref="SW", fp=BOT_FP,
                 desc="Bottone con luce a ritenuta, due contatti; SEGNAPOSTO, pinout da rifare col pezzo scelto")
LED3_FP = "LED_THT:LED_D3.0mm-3"
LED3 = boxsym("LED_BICOLORE_CA", [("1", "K_VERDE", "passive"), ("2", "A", "passive")],
              [("3", "K_ROSSO", "passive")], ref="D", fp=LED3_FP,
              desc="LED bicolore ad anodo comune: giallo = verde + rosso")
LEDR_FP = "LED_THT:LED_Rectangular_W5.0mm_H2.0mm"
DIP18 = "Package_DIP:DIP-18_W7.62mm"
JACK_FP = "Connector_Audio:Jack_6.35mm_Neutrik_NJ3FD-V_Vertical"
JACK = boxsym("JACK_STEREO", [("T", "T", "passive"), ("R", "R", "passive")], [("S", "S", "passive")],
              ref="J", fp=JACK_FP, desc="Jack stereo 6,3 mm Neutrik NJ3FD-V verticale")
R0805, C0805 = "Resistor_SMD:R_0805_2012Metric", "Capacitor_SMD:C_0805_2012Metric"


def pannello(modulo):
    return json.load(open(os.path.join(ROOT, "docs", "pannelli", "coordinate.json")))["moduli"][modulo]


def fili_da(percorso, nome="FILI"):
    """La lista dei fili di un cavo, letta dal file della scheda di segnale senza eseguirlo:
    una fonte sola, i due connettori non possono divergere."""
    for nodo in ast.walk(ast.parse(open(percorso).read())):
        if isinstance(nodo, ast.Assign) and any(getattr(t, "id", None) == nome for t in nodo.targets):
            return ast.literal_eval(nodo.value)
    raise ValueError("%s: lista %s non trovata" % (percorso, nome))


def _ruota(px, py, rot):
    a = math.radians(rot)
    return px * math.cos(a) + py * math.sin(a), -px * math.sin(a) + py * math.cos(a)


_ingombri = {}


def ingombro(fp):
    """Riquadro del cortile dell'impronta, a rotazione 0, nelle coordinate dell'impronta."""
    if fp not in _ingombri:
        import pcbnew
        lib, name = fp.split(":")
        f = pcbnew.FootprintLoad(os.path.join(FPDIR, lib + ".pretty"), name)
        x1, y1, x2, y2 = Design._bbox(f)
        _ingombri[fp] = tuple(v for v in (x1, y1, x2, y2))
    return _ingombri[fp]


class Comandi:
    """Una scheda comandi. finestra = (x0, y0, x1, y1) in mm del pannello: il pezzo di pannello
    che la scheda copre; senza, tutto il pannello meno 1 mm ai lati e 2 sopra e sotto."""

    def __init__(self, nome, outdir, titolo, modulo, finestra=None, rev="0.1-bozza", riprova=False):
        """riprova: Freerouting ripetuto fino a 4 volte (pcbgen.DesignRiprova)."""
        self.pan = pannello(modulo)
        if finestra is None:
            finestra = (1.0, 2.0, self.pan["larghezza"] - 1.0, self.pan["altezza"] - 2.0)
        self.x0, self.y0 = finestra[0], finestra[1]
        self.W, self.H = finestra[2] - finestra[0], finestra[3] - finestra[1]
        self.d = d = (DesignRiprova if riprova else Design)(nome, outdir, titolo, board=(self.W, self.H), rev=rev)
        d.gnd = "AGND"
        d.power_nets("AGND", width=0.5)
        d.link_pairs = True
        self.occupato = []          # (x1, y1, x2, y2, ref): ingombri dei pezzi fissi
        self.usate = set()
        self.avvisi = []
        self.contati = 0            # comandi del pannello messi sulla scheda

    # ---------------------------------------------------------------- posizioni
    def comandi(self, tipo=None, dentro=True):
        """I comandi del pannello che cadono nella finestra della scheda."""
        for c in self.pan["comandi"]:
            if tipo and c["tipo"] != tipo:
                continue
            x, y = c["x"] - self.x0, c["y"] - self.y0
            if dentro and not (0 <= x <= self.W and 0 <= y <= self.H):
                continue
            yield c

    def xy(self, c):
        return c["x"] - self.x0, c["y"] - self.y0

    def _riquadro(self, fp, anchor, x, y, rot, extra=0.0):
        bx1, by1, bx2, by2 = ingombro(fp)
        ax, ay = _ruota(*anchor, rot)
        pts = [_ruota(px, py, rot) for px in (bx1, bx2) for py in (by1, by2)]
        xs = [x - ax + p[0] for p in pts]
        ys = [y - ay + p[1] for p in pts]
        box = [min(xs), min(ys), max(xs), max(ys)]
        if extra:                       # corpo vero più grande dell'impronta (pot da 14 mm)
            box = [min(box[0], x - extra), min(box[1], y - extra), max(box[2], x + extra), max(box[3], y + extra)]
        return box

    def _libero(self, box, m=0.3):
        if box[0] < 0.6 or box[1] < 0.6 or box[2] > self.W - 0.6 or box[3] > self.H - 0.6:
            return False
        return not any(box[0] < o[2] + m and o[0] < box[2] + m and box[1] < o[3] + m and o[1] < box[3] + m
                       for o in self.occupato)

    def metti(self, prefix, sym, val, fp, pins, anchor, x, y, rots, note="", ref=None, extra=0.0):
        """Pezzo fisso con l'ancora in (x, y): la prima rotazione di rots che sta nella scheda
        senza toccare un altro pezzo fisso. Se nessuna sta, la prima, con un avviso."""
        scelta = None
        for rot in rots:
            box = self._riquadro(fp, anchor, x, y, rot, extra)
            if self._libero(box):
                scelta = rot
                break
        if scelta is None:
            scelta = rots[0]
            box = self._riquadro(fp, anchor, x, y, scelta, extra)
            self.avvisi.append("%s %s a (%.1f, %.1f): nessuna rotazione libera" % (prefix, val, x, y))
        p = self.d.part(prefix, sym, val, fp, pins, anchor=anchor, place=(x, y, scelta), note=note, ref=ref)
        self.occupato.append(tuple(box) + (p.ref,))
        self.usate.update(n for n in pins.values() if n)
        return p

    # ---------------------------------------------------------------- pezzi
    def _rot_pot(self, x, rots):
        # i pin stanno a sinistra dell'albero: nella metà sinistra il pot si gira, così i pin
        # vanno verso il centro e non sul bordo; poi le altre tre rotazioni
        if rots:
            return rots
        return (180, 0, 270, 90) if x < self.W / 2 else (0, 180, 270, 90)

    def pot(self, c, reti, val, nota, rots=None):
        """Pot singolo. reti = (antiorario, cursore, orario)."""
        x, y = self.xy(c)
        self.contati += 1
        return self.metti("RV", POT1, val, POT1_FP, {"1": reti[0], "2": reti[1], "3": reti[2]}, (7.5, 2.5), x, y,
                          self._rot_pot(x, rots), extra=7.0 if c.get("pot") == 14 else 0.0,
                          note="%s; manopola %s, pot di classe %s mm, cappuccio %s mm" % (
                              nota, c["nome"], c.get("pot"), c.get("cappuccio")))

    def pot2(self, c, a, b, val, nota, rots=None):
        """Pot doppio. a, b = (antiorario, cursore, orario) della sezione A (lato L) e B (lato R)."""
        x, y = self.xy(c)
        self.contati += 1
        pins = {"1": a[0], "2": a[1], "3": a[2], "4": b[0], "5": b[1], "6": b[2]}
        return self.metti("RV", POT2, val, POT2_FP, pins, (10.0, 2.5), x, y, self._rot_pot(x, rots),
                          extra=7.0 if c.get("pot") == 14 else 0.0,
                          note="%s; manopola %s, pot di classe %s mm, cappuccio %s mm" % (
                              nota, c["nome"], c.get("pot"), c.get("cappuccio")))

    def fader(self, c, alto, cursore, basso, val="10k lin", nota=""):
        """Fader verticale. Pin 3 in alto (rotazione 90), pin 1 e 2 in basso."""
        x, y = self.xy(c)
        self.contati += 1
        corsa = float(c["corsa"])
        sym = boxsym("FADER_MONO_%d" % corsa, [("1", "CAPO_1", "passive"), ("2", "W", "passive"),
                                             ("3", "CAPO_3", "passive")], [("MP", "MP", "passive")], ref="RV",
                     fp=FADER_FP[corsa], desc="Fader mono Bourns PTA, corsa %d mm" % corsa)
        return self.metti("RV", sym, val, FADER_FP[corsa], {"1": basso, "2": cursore, "3": alto},
                          FADER_ANCORA[corsa], x, y, (90,),
                          note="%s; fader %s, corsa %d mm (Bourns PTA%d43, NOTA: pezzo da confermare)" % (
                              nota, c["nome"], corsa, corsa))

    def levetta(self, c, su, comune, giu, nota=""):
        """Levetta verticale. Leva in su = comune col pin in basso (3), leva in giù = comune col
        pin in alto (1): è il verso solito delle levette, da verificare sul pezzo scelto."""
        x, y = self.xy(c)
        self.contati += 1
        return self.metti("SW", LEVETTA, "levetta " + "/".join(c.get("posizioni", [])), LEV_FP,
                          {"1": giu, "2": comune, "3": su, "4": None, "5": None, "6": None}, (1.27, 2.54), x, y,
                          (0, 180), note="%s; levetta %s; NOTA: impronta segnaposto (NKK G1xJP)" % (nota, c["nome"]))

    def bottone(self, c, a, b, luce=None, rluce="1k", nota=""):
        """Bottone con luce a ritenuta. a-b = contatto 1. luce = (rete che accende, ritorno) col
        LED in serie a una resistenza, oppure (rete, ritorno, c2a) per accendere dal contatto 2:
        c2a - contatto 2 - resistenza - LED - ritorno."""
        x, y = self.xy(c)
        self.contati += 1
        pins = {"1": a, "2": b, "3": None, "4": None, "5": None, "6": None}
        if luce:
            la = "LA_" + c["nome"].replace(" ", "")
            if len(luce) == 3:
                pins["4"], pins["5"] = luce[2], "LS_" + c["nome"].replace(" ", "")
                self.d.R(pins["5"], la, rluce, note="luce del bottone %s dal secondo contatto" % c["nome"])
            else:
                self.d.R(luce[0], la, rluce, note="luce del bottone %s" % c["nome"])
            pins["3"], pins["6"] = la, luce[1]
        return self.metti("SW", BOTTONE, "bottone " + c["nome"], BOT_FP, pins, (2.54, 1.27), x, y, (0, 90),
                          note="%s; bottone %s a ritenuta con luce; NOTA: impronta segnaposto (NKK GW12LJP)" % (
                              nota, c["nome"]))

    def led3(self, c, verde, rosso, anodo="+5VF", nota=""):
        x, y = self.xy(c)
        self.contati += 1
        return self.metti("D", LED3, "LED bicolore VR 3 mm", LED3_FP, {"1": verde, "2": anodo, "3": rosso},
                          (2.54, 0), x, y, (0, 90),
                          note="%s; NOTA: un LED bicolore al centro (giallo = verde + rosso); il render mostra "
                               "tre punti a passo 4 mm" % nota)

    def jack(self, c, t, r, s, nota=""):
        x, y = self.xy(c)
        self.contati += 1
        return self.metti("J", JACK, "jack stereo 6,3", JACK_FP, {"T": t, "R": r, "S": s}, (0, 5.72), x, y,
                          (0, 180, 90, 270), note="%s; %s (dec. 128)" % (nota, c["nome"]))

    def meter(self, c, met, rhi, piu="+5VF", meno="CTRL_GND", tag="", chip=None, rprog="6k2"):
        """Barra LED: un LM3915 ogni 10 segmenti, modo barra (sistema-metering.md §3, §5).
        rhi = riferimenti alti, uno per chip, dal più alto (segmenti in cima) al più basso.
        chip = posizioni (x, y, rot) dei chip, una per chip; senza, li piazza il generatore.
        Segmento 1 = soglia più bassa. Verticale: il più alto in cima; orizzontale: a destra."""
        d = self.d
        self.contati += 1
        n, passo, orizz = c["segmenti"], c["passo"], c["orizzontale"]
        x, y = self.xy(c)
        assert n == 10 * len(rhi), "un riferimento ogni 10 segmenti"
        from pcbgen import libsym
        lm = libsym("Driver_LED:LM3914N")
        for k, ref_alto in enumerate(rhi):
            t = "%s%d" % (tag, k + 1) if len(rhi) > 1 else tag
            pins = {"V+": piu, "V-": meno, "RLO": "AGND", "SIG": met, "RHI": ref_alto, "MODE": piu,
                    "REFOUT": "MREF" + t, "REFADJ": meno}
            for s in range(1, 11):
                pins["LED%d" % s] = "MK%s_%d" % (t, s)
            nota = ("barra %s, 10 segmenti da 3 dB sotto %s; modo barra (MODE a V+); V- a %s: le correnti "
                    "dei LED restano fuori da AGND" % (c["nome"], ref_alto, meno))
            if chip:
                cx, cy, rot = chip[k]
                self.metti("U", lm, "LM3915N-1", DIP18, pins, (3.81, 10.16), cx, cy, (rot,), note=nota)
            else:
                d.part("U", lm, "LM3915N-1", DIP18, pins, note=nota)
                self.usate.update(v for v in pins.values() if v)
            d.R("MREF" + t, meno, rprog, note="NOTA: corrente dei LED ~2 mA (metering §1): I = 12,5 V / R, "
                                              "formula del datasheet LM3915 da verificare")
            if chip:
                # 100n fuori dalla fila dei pin 1-9, all'altezza dei pin 2 (V-) e 3 (V+); se lì c'è
                # un altro pezzo, oltre la testa del DIP. Piazzato dal generatore cadeva a ~30 mm
                # (controllo audio A1, canale-comandi 2026-11-11)
                for px, py in ((-7.0, -6.35), (0.0, -13.5)):
                    ox, oy = _ruota(px, py, rot)
                    box = self._riquadro(C0805, (0.0, 0.0), cx + ox, cy + oy, rot + 90)
                    if self._libero(box):
                        break
                self.metti("C", "Device:C", "100n", C0805, {1: piu, 2: meno}, (0.0, 0.0), cx + ox, cy + oy,
                           (rot + 90, rot), note="disaccoppiamento dell'LM3915 %s" % t)
            else:
                d.C(piu, meno, "100n")
            for s in range(1, 11):
                i = (len(rhi) - 1 - k) * 10 + (s - 1)       # 0 = soglia più bassa di tutta la barra
                if orizz:
                    lx, ly, rot = x + (passo - 0.8) / 2 + i * passo, y + 1.1, 90
                else:
                    lx, ly, rot = x + 1.3, y + (passo - 0.8) / 2 + (n - 1 - i) * passo, 0
                self.metti("D", "Device:LED", "LED 5x2", LEDR_FP, {"K": "MK%s_%d" % (t, s), "A": piu},
                           (1.27, 0), lx, ly, (rot,),
                           note="barra %s, segmento %d di %d (1 = soglia più bassa); colore: metering §3" % (
                               c["nome"], i + 1, n))
        d.C(piu, meno, "2u2 16V", "Capacitor_SMD:C_1206_3216Metric",
            note="NOTA: riserva locale dei LED (cavo lungo)")
        self.usate.update((piu, meno, met))

    def cavo(self, fili, ref, x, y, rot=90, nota="stesso ordine del connettore sulla scheda di segnale"):
        """Connettore del cavo piatto, 2 file a passo 2,54. I fili che la scheda non usa restano
        liberi; AGND sempre collegata."""
        n = len(fili) // 2
        pins = {i + 1: (f if f and (f in self.usate or f == "AGND") else None) for i, f in enumerate(fili)}
        fp = "Connector_PinHeader_2.54mm:PinHeader_2x%02d_P2.54mm_Vertical" % n
        return self.metti("J", "Connector_Generic:Conn_02x%02d_Odd_Even" % n, "2x%d cavo piatto" % n, fp, pins,
                          (1.27, (n - 1) * 1.27), x, y, (rot,), note=nota, ref=ref)

    def fila(self, fili, ref, x, y, rot=90, nota=""):
        """Connettore a una fila, passo 2,54 (bottoni assign verso il FX-SEND)."""
        n = len(fili)
        pins = {i + 1: (f if f and (f in self.usate or f == "AGND") else None) for i, f in enumerate(fili)}
        return self.metti("J", "Connector_Generic:Conn_01x%02d" % n, "1x%d" % n,
                          "Connector_PinHeader_2.54mm:PinHeader_1x%02d_P2.54mm_Vertical" % n, pins,
                          (0, (n - 1) * 1.27), x, y, (rot,), note=nota, ref=ref)

    def chiudi(self):
        """Avvisi del piazzamento nelle note del riepilogo; ritorna il Design."""
        for a in self.avvisi:
            self.d.notes.append("AVVISO piazzamento: " + a)
            print("AVVISO piazzamento: " + a, file=sys.stderr)
        self.d.notes.append("comandi del pannello sulla scheda: %d" % self.contati)
        return self.d
