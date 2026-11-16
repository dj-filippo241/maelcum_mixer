"""5-WAY, scheda comandi (todo 270, 335): tutti i comandi del pannello del 5-way e i LED di livello.

La scheda sta parallela al pannello (450 x 102 mm) e lo copre tutto, meno 1 mm ai lati e 2 sopra e
sotto: 448 x 98 mm. Si regge sui dadi dei pot. Posizioni da docs/pannelli/coordinate.json, modulo
"five-way" (dec. 176).

Quattro cavi, uno per scheda di segnale. L'ordine dei fili viene da five-way.py, funzione
fili_cavo(lato, parte), letta senza eseguire il file (comandi.funzione_da): una fonte sola.
- J1 (2x31) verso J2 della LB: pot del lato L, presa 5W_MET_L, +-15LN, +5VF e CTRL_GND dei LED.
- J2 (2x28) verso J2 della RB: pot del lato R, presa 5W_MET_R.
- J3 (2x3) verso J2 della LA: levette di kill del lato L.
- J4 (2x3) verso J2 della RA: levette di kill del lato R.
Reti per cavo [NOTA]: le masse dei quattro cavi restano separate sulla scheda (AGND = LB,
AGNDR = RB, CTRL_GND = LB, CTRL_GND_A_L e CTRL_GND_A_R), così i cavi non chiudono anelli di massa
attraverso il backplane. Le reti della RB prendono il suffisso R senza trattino (DQ1R: con DQ1_R il
controllo dei refusi confonde DQ e NDQ), quelle delle A _L e _R.

Comandi (sistema-comandi.md; versi da five-way-module.md §4.2-4.3 e five-way.py):
- GAIN della via, pot doppio 10k (sezione A = L, B = R), scatto al centro: antiorario = NDQ
  (notch), cursore GW, orario = DQ (+15 dB) (cell-v022-width.cir: b > 0 verso dq). Taper custom:
  resistenze di legge dopo l'ascolto (todo 132), qui il pot lineare nudo.
- WIDTH, pot doppio 1k: antiorario = WB (alpha 0,1, Q3), cursore WW, orario = BPB (alpha 1,
  Q0,3): «CW = più largo» (§4.3). NOTA: il doppio 1k di classe 14 mm è da trovare (sistema-comandi).
- POSITION, pot singolo 10k lin -> CV (sistema-comandi): antiorario = AGND, orario = +REF5 della
  LB; il cursore POSWn va alle due schede B. NOTA: il +REF5 della RB resta libero sul cavo; lo
  scarto fra i due riferimenti sposta la frequenza della R di quanto differiscono (0,1 %).
- KILL, levetta ON-OFF-(ON) a due poli (dec. 121): su = kill fisso, giù = kill a molla; in tutte e
  due le posizioni KSWn va a CTRL_GND della sua scheda A (five-way.py: pull-up 10k, chiusa = kill).
  Polo A = LA, polo B = RA.
- GROWL, pot a 6 sezioni (3 per lato, five-way-module §5bis: miscela + due spinte), lineare:
  miscela 10k (antiorario AGND, cursore DWG, orario DDG); spinta dei bassi, reostato 10k fra GLOW e
  GLR (orario = 0 ohm, antiorario = 10k); spinta dei medi, reostato 5k fra GMID e GMR (uguale).
- NASTRO, pot a 4 sezioni (2 per lato), log A: miscela 10k (antiorario AGND, cursore DWT, orario
  DTP); spinta, reostato 5k fra LSP e LSN (antiorario = 0 ohm, orario = 5k).
  NOTA: i pot a 6 e 4 sezioni con valori diversi per sezione non esistono nella libreria di KiCad;
  il pezzo è da scegliere (classe Alps RK27 a più sezioni, o su ordinazione). Impronta segnaposto:
  un pin header coi capi delle sezioni, al centro dell'albero; il pot si collega coi fili.
- LED di livello delle 5 vie e barra METER: il circuito di five-way-led-livello.md (dec. 177), sul
  retro (solo SMD, dec. 142), alimentato dal cavo della LB.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from pcbgen import boxsym
from comandi import Comandi, funzione_da, POT1, POT1_FP
import celle_vca as cv
from celle_vca import C12
from celle_micmono import LM339
from comune_5w import Parti

VIE = ("SUB", "KICK", "MID", "HIGH", "SUPER")
fili_cavo = funzione_da(os.path.join(HERE, "five-way.py"), "fili_cavo")

s = Comandi("five-way-comandi", os.path.join(HERE, "comandi"), "maelcum 5-WAY scheda comandi - bozza v0.1",
            "five-way", riprova=True)
d = s.d
d.power_nets("+5VF", "CTRL_GND", "+15LN", "-15LN", width=0.4)
d.link_pairs_masse = True
d.cluster_fuori = True

pz = Parti(d, primo=100, nu_col_ref=True)     # comune_5w.py (todo 342)
uref, Cx = pz.uref, pz.Cx


def Pack():
    """Sezioni op-amp in quad OPA1654 sul +-15 LN."""
    return pz.Pack("+15LN", "-15LN")


def via(c):
    """Indice 0-4 della via di un comando, dalla colonna del pannello (passo 79,4 mm)."""
    return min(4, max(0, int(round((c["x"] - 39.5) / 79.4))))


# ------------------------------------------------------------ comandi
d.block = "GAIN, POSITION, WIDTH delle 5 vie (pot doppi: sezione A = L, B = R)"
for c in s.comandi("manopola"):
    nome = c["nome"].split()
    if nome[0] in ("GROWL", "NASTRO"):
        continue
    t = str(VIE.index(nome[1]) + 1)
    if nome[0] == "GAIN":
        s.pot2(c, ("NDQ" + t, "GW" + t, "DQ" + t), ("NDQ%sR" % t, "GW%sR" % t, "DQ%sR" % t),
               "10k lin doppio, scatto",
               "GAIN %s: antiorario = notch (NDQ), centro = piatto, orario = +15 dB (DQ); NOTA: resistenze "
               "di legge dopo l'ascolto (todo 132)" % nome[1])
    elif nome[0] == "WIDTH":
        s.pot2(c, ("WB" + t, "WW" + t, "BPB" + t), ("WB%sR" % t, "WW%sR" % t, "BPB%sR" % t),
               "1k log doppio",
               "WIDTH %s: antiorario = stretto (Q3), orario = largo (Q0,3), §4.3; NOTA: doppio 1k da trovare, "
               "taper log 10 o 20 %% da scegliere (dec. 117)" % nome[1])
    else:
        s.pot(c, ("AGND", "POSW" + t, "+REF5"), "10k lin",
              "POSITION %s: antiorario = frequenza bassa, orario = alta; cursore alle due schede B" % nome[1])

d.block = "GROWL (6 sezioni) e NASTRO (4 sezioni): pot sul segnale, segnaposto"


def multipot(c, sezioni, valore, nota):
    """Pot a più sezioni: header 2xN coi capi (antiorario, cursore, orario) di ogni sezione."""
    x, y = s.xy(c)
    s.contati += 1
    n = len(sezioni) * 3
    pins, sym_pins = {}, []
    for k, (a, w, b) in enumerate(sezioni):
        for j, (nome, rete) in enumerate((("CCW", a), ("W", w), ("CW", b))):
            p = 3 * k + j + 1
            pins[str(p)] = rete
            sym_pins.append((str(p), "S%d_%s" % (k + 1, nome), "passive"))
    meta = len(sym_pins) // 2
    sym = boxsym("POT_%dSEZ" % len(sezioni), sym_pins[:meta], sym_pins[meta:], ref="RV",
                 fp="Connector_PinHeader_2.54mm:PinHeader_2x%02d_P2.54mm_Vertical" % (n // 2),
                 desc="Pot a %d sezioni sullo stesso albero; SEGNAPOSTO: pezzo da scegliere, collegato coi fili"
                      % len(sezioni))
    fp = "Connector_PinHeader_2.54mm:PinHeader_2x%02d_P2.54mm_Vertical" % (n // 2)
    return s.metti("RV", sym, valore, fp, pins, (1.27, (n // 2 - 1) * 1.27), x, y, (90, 270), extra=7.0,
                   note="%s; manopola %s, classe 14 mm, cappuccio %s mm; NOTA: impronta segnaposto (header)"
                        % (nota, c["nome"], c.get("cappuccio")))


for c in s.comandi("manopola"):
    if c["nome"] == "GROWL":
        multipot(c, [("AGND", "DWG", "DDG"), ("GLR", "GLR", "GLOW"), ("GMR", "GMR", "GMID"),
                     ("AGNDR", "DWGR", "DDGR"), ("GLRR", "GLRR", "GLOWR"), ("GMRR", "GMRR", "GMIDR")],
                 "10k/10k/5k lin x2",
                 "GROWL (§5bis, dec. 165): sezioni 1-3 = L (miscela, spinta bassi 10k, spinta medi 5k), 4-6 = R; "
                 "orario = tutto GROWL (spinte a 0 ohm)")
    elif c["nome"] == "NASTRO":
        multipot(c, [("AGND", "DWT", "DTP"), ("LSP", "LSN", "LSN"),
                     ("AGNDR", "DWTR", "DTPR"), ("LSPR", "LSNR", "LSNR")],
                 "10k/5k log A x2",
                 "NASTRO (§5bis, dec. 166): sezioni 1-2 = L (miscela, spinta 5k), 3-4 = R; orario = tutto NASTRO "
                 "(spinta 5k, +12 dB)")

d.block = "KILL: levette ON-OFF-(ON) a due poli (polo A = LA, polo B = RA)"
for c in s.comandi("levetta"):
    t = str(via(c) + 1)
    s.levetta(c, "KSW%s_L" % t, "CTRL_GND_A_L", "KSW%s_L" % t, b=("KSW%s_R" % t, "CTRL_GND_A_R", "KSW%s_R" % t),
              nota="KILL %s (dec. 121): su = fisso, giù = a molla; chiusa = KSW a massa = kill" % VIE[int(t) - 1])

d.block = "LED di livello delle 5 vie (LED bicolore, giallo = verde + rosso)"
for c in s.comandi("led3"):
    i = via(c) + 1
    s.led3(c, "LEDG%d" % i, "LEDR%d" % i, anodo="+5VF", nota="LED di livello della via %s (dec. 176-177)" % VIE[i - 1])

# ------------------------------------------------------------ circuito dei LED (da five-way.py, 2026-11-15)
d.side = "B"
d.block = "LED DI LIVELLO: somma L+R, banco d'analisi, rivelatori (five-way-led-livello.md, dec. 177)"
PL = Pack()
d.R("5W_MET_L", "SNL", "20k 0.1%")
d.R("5W_MET_R", "SNL", "20k 0.1%")
d.R("SNL", "SOL", "5k76 0.1%", note="(L+R)/2 x 0,576 (metering: g = 0,576)")
d.C("SNL", "SOL", "100p C0G")
PL.add(("AGND", "SNL", "SOL"))
LP2 = {"SUB": ("17k8", "220n", "100n"), "KICK": ("19k6", "47n", "22n"), "MID": ("19k6", "10n", "4n7"),
       "HIGH": ("13k3", "2n2", "1n")}
HP2 = {"KICK": ("100n", "18k7", "37k4"), "MID": ("22n", "20k5", "41k2"), "HIGH": ("4n7", "20k", "40k2"),
       "SUPER": ("1n", "14k", "28k")}
for i, v in enumerate(VIE, 1):
    x = "SOL"
    if v in HP2:
        cc, rfb, rg = HP2[v]
        t = "AH%d" % i
        Cx(x, t + "1", cc); Cx(t + "1", t + "2", cc)
        d.R(t + "1", t, rfb + " 0.1%"); d.R(t + "2", "AGND", rg + " 0.1%")
        PL.add((t + "2", t, t))
        x = t
    if v in LP2:
        r, c1, c2 = LP2[v]
        t = "AL%d" % i
        d.R(x, t + "1", r + " 0.1%"); d.R(t + "1", t + "2", r + " 0.1%")
        Cx(t + "1", t, c1); Cx(t + "2", "AGND", c2)
        PL.add((t + "2", t, t))
        x = t
    # rivelatore di picco (cella del metering): superdiodo, hold 100n, release 3M, buffer
    d.R("DO" + v, "DA" + v, "1k")
    cv.diode(d, "DA" + v, "HO" + v)
    d.C("DO" + v, "HO" + v, "47p C0G")
    d.C("HO" + v, "AGND", "100n C0G", C12, note="hold")
    d.R("HO" + v, "AGND", "3M", note="release 0,3 s (dec. 81)")
    PL.add((x, "HO" + v, "DO" + v))
    PL.add(("HO" + v, "MET" + v, "MET" + v))
# barra del meter del modulo: stesso segnale della somma, rivelatore uguale
d.R("DOM", "DAM", "1k")
cv.diode(d, "DAM", "HOM")
d.C("DOM", "HOM", "47p C0G")
d.C("HOM", "AGND", "100n C0G", C12, note="hold della barra del 5-way")
d.R("HOM", "AGND", "3M")
PL.add(("SOL", "HOM", "DOM"))
PL.add(("HOM", "MET", "MET"))
PL.flush("LED: somma L+R, banco d'analisi, rivelatori")

d.block = "LED DI LIVELLO: soglie comuni, latch e comparatori (dec. 177)"
d.R("+15LN", "VR", "127k 0.1%")
d.R("VR", "VY", "12k7 0.1%")
d.R("VY", "VG", "12k4 0.1%")
d.R("VG", "AGND", "402 0.1%")
for n in ("VR", "VY", "VG"):
    d.C(n, "AGND", "100n")
d.R("+5VF", "VTL", "10k")
d.R("VTL", "CTRL_GND", "10k")
d.C("VTL", "CTRL_GND", "100n")
for i, v in enumerate(VIE, 1):
    m = "MET" + v
    d.R("+5VF", "LT" + v, "750k", note="latch del rosso 0,52 s")
    d.C("LT" + v, "CTRL_GND", "1u 25V", C12)
    d.R("+5VF", "LQ" + v, "10k")
    d.part("U", LM339, "LM339DR", cv.SOIC14, {
        "1IN+": "VR", "1IN-": m, "1OUT": "LT" + v, "2IN+": "LT" + v, "2IN-": "VTL", "2OUT": "LQ" + v,
        "3IN+": "VY", "3IN-": m, "3OUT": "KR" + v, "4IN+": "VG", "4IN-": m, "4OUT": "KG" + v,
        "VCC": "+5VF", "GND": "CTRL_GND"}, ref=uref(), note="LED3 della via %s (celle_micmono.led3)" % v)
    d.C("+5VF", "CTRL_GND", "100n")
    cv.diode(d, "KR" + v, "LQ" + v, note="rosso acceso durante il latch")
    d.part("Q", "Transistor_FET:2N7002", "2N7002", "Package_TO_SOT_SMD:SOT-23",
           {"D": "GF" + v, "S": "KG" + v, "G": "LQ" + v}, note="spegne il verde durante il latch")
    d.R("LEDR%d" % i, "KR" + v, "1k", note="~2,8 mA nel rosso")
    d.R("LEDG%d" % i, "GF" + v, "1k", note="~2,8 mA nel verde")
for a, b in (("+15LN", "AGND"), ("AGND", "-15LN"), ("+5VF", "CTRL_GND")):
    d.C(a, b, "10u 25V", "Capacitor_SMD:C_1206_3216Metric", note="NOTA: riserva locale del cavo lungo")
d.side = "F"

d.block = "METER: un LM3915, 10 LED (zona del 5-way, g = 0,576, RHI = +REF5 della LB)"
for c in s.comandi("meter"):
    x, y = s.xy(c)
    s.meter(c, "MET", ["+REF5"], piu="+5VF", meno="CTRL_GND", tag="M", chip=[(x - 1.0, 82.0, 0)])

# ------------------------------------------------------------ cavi
d.block = "CAVI: J1 LB, J2 RB, J3 LA, J4 RA (ordine da five-way.py, fili_cavo)"
s.usate.update(n for p in d.parts for n in p.nets.values() if n)   # anche le reti del circuito dei LED


def rinomina(fili, lato, parte):
    """Reti della scheda di segnale -> reti di questa scheda (vedi le note in testa)."""
    out = []
    for f in fili:
        if parte == "A":
            out.append("%s_A_%s" % (f, lato) if f == "CTRL_GND" else "%s_%s" % (f, lato))
        elif lato == "L" or f in ("5W_MET_R",) or f.startswith("POSW"):
            out.append(f)
        elif f == "AGND":
            out.append("AGNDR")
        else:
            out.append(f + "R")
    return out


for ref, lato, parte, x in (("J1", "L", "B", 80.0), ("J2", "R", "B", 238.0), ("J3", "L", "A", 160.0),
                            ("J4", "R", "A", 318.0)):
    fili = rinomina(fili_cavo(lato, parte), lato, parte)
    s.cavo(fili, ref, x, 6.0,
           nota="stesso ordine di J2 su five-way.py %s%s (fili_cavo); reti rinominate per lato" % (lato, parte))
s.chiudi()

if __name__ == "__main__":
    d.build(route="--no-route" not in sys.argv)
