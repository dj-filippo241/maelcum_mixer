"""CANALE CDJ/LINE (v0.4, dec. 105, 152, 162, 163, 168), 4x la stessa scheda. Bozza v0.1.

Catena per lato (docs/fase1/cdj-line-channel.md §2-§3.8, REV dec. 159-163):
  RCA (cavo J3) -> ferrite + 100R + TVS -> 2,2u film + 100k -> buffer OPA1612
  -> GAIN T1 (pot 10k lin sul cavo, Rl 4,30k, non invertente x3,15; dec. 162)
  -> ISOLATOR incroci C (dec. 152; pot lineare B sul cavo, dec. 168) -> somma non invertente
     x10 con servo DC (eq-isolator §9, §10) = nodo EQ
  -> CUE (buffer, switch ADG, 47R, slot 2) · SEND TAP (buffer, 47R, slot 3) · meter (pre-fader)
  -> FADER (2 VCA + I/V, shaper del fader, dec. 126) -> levetta HPF/OFF/LPF: ADG1434 verso
     DJ bus / bus HPF / bus LPF con 10k lato sorgente (slot 1, 4, 5; dec. 159)
  Dip del VCA del fader al cambio della levetta (dec. 163, sim/cdj/RISULTATI-filtsel-dip.md).

Polarità (sistema-polarita.md): ingresso, GAIN, isolator, prese +1; fader VCA + I/V +1.

Fonti: sim/eq-iso/iso-incc-banca.inc e RISULTATI-incroci-C.md §1 (isolator), sim/gain-pot/
RISULTATI-gain-pot.md (T1), sim/shaper/shaper-fader.cir, docs/fase3/sistema-vca-trim.md §3,
sim/cdj/RISULTATI-filtsel-dip.md (dip), sistema-metering.md (g = 0,288).
Valori [PROVVISORIO]. Le R della banca: E192 0,1 % più vicine ai valori calcolati del
RISULTATI §1. Le scelte non scritte nei documenti sono segnate NOTA (pcb/canale/NOTE.md).
Il front-end PHONO (phono-stage.md) è una variante di Rev B: non è su questa scheda.

Scheda sola (dec. 173): 287 mm da dietro a davanti, alta 162 mm dietro e 129 davanti (trapezio
della dec. 158, pcb/PIANO-SCHEDE-F.md). x = 0 è il lato di dietro. La versione su due schede col
ponte 2x18 sta in archivio/ (canale-segnale.py, canale-isolator.py).
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from pcbgen import Design, boxsym
from backplane import c96, SYM_C96, FP_C96
import celle_vca as cv
from celle_vca import opa2, opa4, vca, iv, shaper, law_trim, C12, SOIC14
from celle_micmono import power_18_sw, power_ln, ADG
from banca import banca

L, H_DIETRO, H_DAVANTI = 287, 162, 129     # PIANO-SCHEDE-F, dec. 173
d = Design("canale", HERE, "maelcum CANALE CDJ/LINE (v0.4) - bozza v0.1", board=(L, H_DIETRO, H_DAVANTI), rev="0.2-bozza")
d.gnd = "AGND"
d.inner_signal = True     # SMD sui due lati (dec. 142)
C10 = "Capacitor_SMD:C_1210_3225Metric"
# NOTA: logica in TSSOP-14 (stesso pinout del SOIC): in SOIC-14 il pin VCC (14) sta nell'angolo e il
# 100n legato al pin cadeva sul corpo del chip (DRC courtyards_overlap, 2026-11-04)
TSSOP14 = "Package_SO:TSSOP-14_4.4x5mm_P0.65mm"
SIDES = ("L", "R")

# 74HC: pinout dai datasheet TI letti il 2026-11-04 (SCLS100F, SCLS085L, SCLS094F), SOIC-14
HC86 = boxsym("74HC86", [("1", "1A", "input"), ("2", "1B", "input"), ("4", "2A", "input"), ("5", "2B", "input"),
                         ("9", "3A", "input"), ("10", "3B", "input"), ("12", "4A", "input"), ("13", "4B", "input")],
              [("3", "1Y", "output"), ("6", "2Y", "output"), ("8", "3Y", "output"), ("11", "4Y", "output"),
               ("14", "VCC", "power_in"), ("7", "GND", "power_in")],
              fp=SOIC14, desc="Quad XOR. Pinout TI SCLS100F fig. 5-1 (2026-11-04)")
HC14 = boxsym("74HC14", [("1", "1A", "input"), ("3", "2A", "input"), ("5", "3A", "input"), ("9", "4A", "input"),
                         ("11", "5A", "input"), ("13", "6A", "input")],
              [("2", "1Y", "output"), ("4", "2Y", "output"), ("6", "3Y", "output"), ("8", "4Y", "output"),
               ("10", "5Y", "output"), ("12", "6Y", "output"), ("14", "VCC", "power_in"), ("7", "GND", "power_in")],
              fp=SOIC14, desc="Sei inverter Schmitt. Pinout TI SCLS085L, Pin Functions (2026-11-04)")
HC74 = boxsym("74HC74", [("1", "1CLR", "input"), ("2", "1D", "input"), ("3", "1CLK", "input"), ("4", "1PRE", "input"),
                         ("13", "2CLR", "input"), ("12", "2D", "input"), ("11", "2CLK", "input"), ("10", "2PRE", "input")],
              [("5", "1Q", "output"), ("6", "1QN", "output"), ("9", "2Q", "output"), ("8", "2QN", "output"),
               ("14", "VCC", "power_in"), ("7", "GND", "power_in")],
              fp=SOIC14, desc="Due flip-flop D. Pinout TI SCLS094F, Pin Functions (2026-11-04)")

# ------------------------------------------------------------ backplane
d.block = "BACKPLANE C96 (classe CDJ, REV dec. 159)"
b = {"b1": "DJBUS_L", "b2": "DJBUS_R", "b4": "CUE_OUT_L", "b5": "CUE_OUT_R", "b7": "SEND_TAP_L", "b8": "SEND_TAP_R",
     "b10": "BUS_HPF_L", "b11": "BUS_HPF_R", "b13": "BUS_LPF_L", "b14": "BUS_LPF_R"}
for s in range(1, 11):
    b["b%d" % (3 * s)] = "AGND"
d.part("J", SYM_C96, "C96 maschio", FP_C96, c96(b, c=["c1", "c2"]), ref="J1", place=(50, H_DIETRO - 6.5, 180),
       note="DIN 41612 C 3x32, angolo retto")
# NOTA: C96 dietro (x 2,5-97,5), alla stessa profondità di quello del FX-SEND accanto; la posizione
# vera la fissa il backplane della disposizione F (todo 269)
for ref, x in (("H1", 5), ("H2", 95), ("H3", L - 5)):     # H2 lontano dal cavo J2 (x 120-166)
    d.part("H", "Mechanical:MountingHole_Pad", "CHASSIS", "MountingHole:MountingHole_3.2mm_M3_Pad",
           {1: "CHASSIS"}, ref=ref, place=(x, d.ytop(x) + 5, 0),
           note="foro di fissaggio al pannello, a CHASSIS (NOTA: tre fori sui 287 mm)")

d.block = "ALIMENTAZIONE +-18 audio, +-15 switch, +5, +-15 LN, +-5 riferimento"
power_18_sw(d)
power_ln(d)
cv.ref5(d, "U46")
d.power_nets("+18V", "-18V", width=0.4)   # NOTA: a 0,6 mm Freerouting lascia -18V aperta (come il MIC, todo 237)
d.netclass["CTRL_GND"] = 0.3   # NOTA: pin TSSOP della logica (passo 0,65): pista <= 0,3 mm

# ------------------------------------------------------------ ingresso e GAIN
d.block = "INGRESSO LINE [A] e GAIN T1 [B] (dec. 162)"
for s in SIDES:
    d.part("FB", "Device:FerriteBead_Small", "ferrite 600R", cv.FB, {1: "IN_" + s, 2: "INF_" + s})
    d.R("INF_" + s, "INP_" + s, "100", note="R serie (cdj §3.1)")
    d.part("D", "Device:D_TVS", "TVS bidir <=5 pF", "Diode_SMD:D_SOD-323", {1: "INP_" + s, 2: "AGND"},
           note="NOTA: parte da scegliere (TVS low-cap)")
    d.C("INP_" + s, "INC_" + s, "2u2 film", "Capacitor_SMD:C_1812_4532Metric", note="blocco della continua (voce 58)")
    d.R("INC_" + s, "AGND", "100k", note="polo 0,72 Hz, Zin 100k")
    d.R("GW_" + s, "AGND", "4k30 0.1%", note="Rl dal cursore a massa (T1)")
    d.R("GO_" + s, "NG_" + s, "2k15 0.1%")
    d.R("NG_" + s, "AGND", "1k 0.1%", note="x3,15")
opa2(d, "U1", ("INC_L", "BUF_L", "BUF_L"), ("INC_R", "BUF_R", "BUF_R"), note="buffer d'ingresso")
opa2(d, "U2", ("GW_L", "NG_L", "GO_L"), ("GW_R", "NG_R", "GO_R"), note="GAIN T1, non invertente x3,15")


# ------------------------------------------------------------ isolator (dec. 173: sulla stessa scheda)
# Banca dei due lati, somma x10 e servo (banca.py, riferimenti U3-U14)
banca(d)

# ------------------------------------------------------------ prese pre-fader
d.side = "B"   # prese, meter e fader (solo SMD) sul retro: davanti l'alimentazione non trova posto (dec. 142)
d.block = "CUE [D], SEND TAP [E] e METER [G] (pre-fader)"
for s in SIDES:
    d.R("STB_" + s, "SEND_TAP_" + s, "47", note="driver <= 50 ohm verso il FX-SEND (slot 3)")
    d.R("CUED_" + s, "CUE_OUT_" + s, "47", note="NOTA: 47R dopo lo switch CUE (slot 2)")
opa2(d, "U15", ("EQ_L", "CUEB_L", "CUEB_L"), ("EQ_L", "STB_L", "STB_L"), note="buffer CUE e SEND TAP, L")
opa2(d, "U16", ("EQ_R", "CUEB_R", "CUEB_R"), ("EQ_R", "STB_R", "STB_R"), note="buffer CUE e SEND TAP, R")
d.R("EQ_L", "MG", "20k 0.1%", note="NOTA: barra unica del canale, (L+R)/2 con due 20k")
d.R("EQ_R", "MG", "20k 0.1%")
d.R("MG", "AGND", "4k02 0.1%", note="g = 0,287 (doc 0,288), come il master")
d.R("DOUT", "D1A", "1k")
cv.diode(d, "D1A", "HOLD")
d.C("DOUT", "HOLD", "47p C0G")
d.C("HOLD", "AGND", "100n C0G", C12, note="hold: niente altro sul nodo (sim/meter)")
d.R("HOLD", "AGND", "3M", note="release 0,3 s (dec. 81)")
opa4(d, "U17", ("MG", "MGB", "MGB"), ("MGB", "HOLD", "DOUT"), ("HOLD", "MET", "MET"), ("AGND", "NU17", "NU17"),
     note="inseguitore di scala, superdiodo, buffer dell'hold (LM3915 sulla scheda comandi)")

# ------------------------------------------------------------ fader, dip, levetta
d.block = "FADER [H] (2 VCA, shaper del fader, dec. 126) e DIP (dec. 163)"
for k, s in enumerate(SIDES):
    vca(d, "U%d" % (18 + k), "EQ_" + s, "NIF_" + s, "ECF_" + s, "f" + s.lower())
    iv(d, "NIF_" + s, "FAD_" + s)
opa2(d, "U20", ("AGND", "NIF_L", "FAD_L"), ("AGND", "NIF_R", "FAD_R"), note="I/V del fader, pilota i 10k dei bus")
shaper(d, "U21", "F", *cv.FADER)
law_trim(d, "F", "ECF_L", "ECF_R", rbot="1k5 0.1%",
         nota="NOTA: 1k5 // 3,01k del dip = 1,00k: il partitore resta 1/2 a riposo")
# dip: DIFF (logica) -> due RC 10k/50n bufferizzati -> 3,01k su ciascun EC- (al pin 0,73 V >= 0,61)
d.R("DIFF", "DP1", "10k")
d.C("DP1", "AGND", "50n C0G", C12, note="NOTA: 50n = 47n + 3n3 in parallelo; tau 0,5 ms")
d.R("DPB1", "DP2", "10k")
d.C("DP2", "AGND", "50n C0G", C12, note="NOTA: 50n = 47n + 3n3 in parallelo")
opa2(d, "U22", ("DP1", "DPB1", "DPB1"), ("DP2", "DIPCV", "DIPCV"), "+15LN", "-15LN",
     note="due celle RC del dip con buffer (RISULTATI-filtsel-dip caso 3)")
d.R("DIPCV", "ECF_L", "3k01 0.1%", note="NOTA: 4,4 V x 600/3610 = 0,73 V al pin")
d.R("DIPCV", "ECF_R", "3k01 0.1%")

d.side = "F"
d.block = "LEVETTA HPF/OFF/LPF: logica autotemporizzata (74HC14, 74HC86, 74HC74) e ADG1434"
for k in (0, 1):
    d.R("+5VF", "FSW%d" % k, "10k", note="levetta verso CTRL_GND sulla scheda comandi")
    d.R("FSW%d" % k, "FR%d" % k, "10k", note="NOTA: antirimbalzo 1 ms")
    d.C("FR%d" % k, "CTRL_GND", "100n")
d.part("U", HC14, "74HC14PW", TSSOP14, {"1A": "FR0", "1Y": "D0", "2A": "FR1", "2Y": "D1",
                                      "3A": "DLY", "3Y": "NCLK", "4A": "NCLK", "4Y": "CLK",
                                      "5A": "XQ", "5Y": "DJSEL", "6A": "CTRL_GND", "6Y": None,
                                      "VCC": "+5VF", "GND": "CTRL_GND"}, ref="U23",
       note="NOTA: antirimbalzo, ritardo Schmitt e DJSEL = NOT(Q0 xor Q1)")
d.C("+5VF", "CTRL_GND", "100n")
d.part("U", HC86, "74HC86PW", TSSOP14, {"1A": "D0", "1B": "Q0", "1Y": "X0", "2A": "D1", "2B": "Q1", "2Y": "X1",
                                      "3A": "Q0", "3B": "Q1", "3Y": "XQ", "4A": "CTRL_GND", "4B": "CTRL_GND", "4Y": None,
                                      "VCC": "+5VF", "GND": "CTRL_GND"}, ref="U24", note="NOTA: confronto levetta / stato")
d.C("+5VF", "CTRL_GND", "100n")
d.part("U", HC74, "74HC74PW", TSSOP14, {"1D": "D0", "1CLK": "CLK", "1Q": "Q0", "1QN": None, "1PRE": "+5VF", "1CLR": "+5VF",
                                      "2D": "D1", "2CLK": "CLK", "2Q": "Q1", "2QN": None, "2PRE": "+5VF", "2CLR": "+5VF",
                                      "VCC": "+5VF", "GND": "CTRL_GND"}, ref="U25", note="NOTA: stato dell'ADG")
d.C("+5VF", "CTRL_GND", "100n")
cv.diode(d, "X0", "DIFF", note="NOTA: OR a diodi")
cv.diode(d, "X1", "DIFF")
d.R("DIFF", "CTRL_GND", "100k")
d.R("DIFF", "DLY", "33k", note="NOTA: 33k x 47n, soglia dello Schmitt a ~1,5 ms (doc: ADG a 1,6 ms)")
d.C("DLY", "CTRL_GND", "47n")
d.R("Q0", "FILT_MODE1_0", "1k", note="NOTA: bit di modo sulla riga c; il backplane li porta per posizione")
d.R("Q1", "FILT_MODE1_1", "1k")
# CUE: tasto verso +5VF sul cavo, come i bottoni assign del FX-SEND
d.R("BTNC", "CUESEL", "10k", note="NOTA: tasto CUE a ritenuta verso +5VF")
d.R("CUESEL", "CTRL_GND", "100k")
d.C("CUESEL", "CTRL_GND", "100n")
for s, ref in (("L", "U26"), ("R", "U27")):
    p = {"VDD": "+15SW", "VSS": "-15SW", "GND": "AGND", "NIC": None,
         "IN1": "DJSEL", "IN2": "Q0", "IN3": "Q1", "IN4": "CUESEL"}
    for k, (src, dst) in enumerate((("FAD_", "DJD_"), ("FAD_", "HPD_"), ("FAD_", "LPD_"), ("CUEB_", "CUED_")), 1):
        p["S%dA" % k] = src + s
        p["S%dB" % k] = "AGND"
        p["D%d" % k] = dst + s
    d.part("U", ADG, "ADG1434YRUZ", "Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm", p, ref=ref,
           note="SPDT: A = IN alto, B = shunt a massa (datasheet Rev. E tabella 9)")
    d.C("+15SW", "AGND", "100n")
    d.C("AGND", "-15SW", "100n")
    d.R("DJD_" + s, "DJBUS_" + s, "10k 0.1%", note="R lato sorgente sul DJ bus")
    d.R("HPD_" + s, "BUS_HPF_" + s, "10k 0.1%", note="R lato sorgente sul bus HPF")
    d.R("LPD_" + s, "BUS_LPF_" + s, "10k 0.1%", note="R lato sorgente sul bus LPF")

# ------------------------------------------------------------ cavi
d.block = "CAVO SCHEDA COMANDI (J2) e INGRESSI RCA (J3)"
FILI = ["AGND", "BUF_L", "GW_L", "AGND", "BUF_R", "GW_R", "AGND",
        "LOO_L", "K1W_L", "LMO_L", "K2W_L", "MHO_L", "K3W_L", "HIO_L", "K4W_L", "AGND",
        "LOO_R", "K1W_R", "LMO_R", "K2W_R", "MHO_R", "K3W_R", "HIO_R", "K4W_R", "AGND",
        "+REF5", "POT_F", "AGND", "MET", "FSW0", "FSW1", "BTNC", "+5VF", "CTRL_GND", "AGND", "AGND"]
# NOTA: cavo dei pot a metà scheda, sotto la striscia dei comandi (la scheda comandi è il todo 270)
cv.cavo(d, FILI, x=143, y=d.ytop(143 + 25) + 5)
d.part("J", "Connector_Generic:Conn_01x05", "1x5 ingressi", "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical",
       {1: "IN_L", 2: "AGND", 3: "IN_R", 4: "AGND", 5: "CHASSIS"}, ref="J3", place=(22, d.ytop(22 + 7) + 6, 90),
       note="NOTA: cavo verso gli RCA sulla schedina dei connettori (dec. 141)")

d.audio_rules = {
    "sensibili": r"^(INC_[LR]|NG_[LR]|GW_[LR]|NIF_[LR]|DJBUS_[LR]|BUS_[HL]PF_[LR]|CUE_OUT_[LR])$",
    "cavo": r"^(BUF|GW|LOO|LMO|MHO|HIO|K\dW)_[LR]$",
    "rumorose": r"^(\+15SW|-15SW|\+5VF?|MET|FSW\d|FR\d|D\d|Q\d|X\d|XQ|DIFF|DLY|N?CLK|DJSEL|CUESEL|BTNC|DP.*|DIPCV|POT_F|CVP_F|SH_F|V27F[+-]|V22F[+-]|VREG[+-]|BASE[+-]|RAW.*|CTRL_GND)$",
    "regolatori": ["U40", "U41", "U42", "U43", "U44", "U45", "Q40", "Q41"],
}

if __name__ == "__main__":
    d.build(route="--no-route" not in sys.argv)
