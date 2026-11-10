"""FX-RET: modulo di ritorno di un bus FX (dec. 130), 4x la stessa scheda. Bozza v0.1.

Catena (docs/fase1/fx-module.md §2bis, §3, §4, §5 REV dec. 162 e todo 220, §7, §8.3):
  bus Sn (slot 1, massa virtuale, Rf 10k, Cf 10p) -> driver del pedale -> 100R + TVS -> jack SEND
  jack RETURN -> 100R + TVS + 1M -> buffer JFET a guadagno 1 (servo DC sul nodo FB)
     -> GAIN T2 (1,24k + pot 10k lin in retroazione, poi invertente x1,24) -> EQ2 -> nodo REROUTE
     -> 4 reroute (VCA + I/V + driver d'iniezione invertente + 10k sui net S1-S4, slot 2-5)
     -> fader (2 VCA + I/V) -> 47R -> RET_OUT (slot 6, verso MSUM n+1 del master)
  meter: (L+R)/2 dal nodo REROUTE -> detector di picco -> MET sul cavo (LM3915 sulla scheda comandi).

Polarità (sistema-polarita.md): ricevitore del bus -1, driver del pedale +1; ritorno +1 (buffer,
due invertenti del GAIN T2, EQ2, VCA + I/V); reroute VCA + I/V +1 e driver d'iniezione
INVERTENTE 20k/20k (F3, fx-module §2bis.1 REV 2026-11-03).

Fonti dei valori: sim/gain-pot/ritorno-buffer-g1.cir (buffer, servo, GAIN T2), sim/fx/fx-eq2-pot10k.cir
(EQ2, come fx-send.py), sim/shaper/shaper-reroute.cir e shaper-fader.cir (shaper),
docs/fase3/sistema-vca-trim.md §3 (trim), sim/system/meter-det-03s.cir e sistema-metering.md
(detector, g = 0,288), sim/fx/fx-ret-bus-ac-130.cir (somma del bus, Cf 10p).
Valori [PROVVISORIO]. Le scelte non scritte nei documenti sono segnate NOTA (pcb/fx-ret/NOTE.md).
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from pcbgen import Design
from backplane import c96, SYM_C96, FP_C96
import celle_vca as cv
from celle_vca import opa2, opa4, vca, iv, shaper, law_trim, C12
from celle_micmono import power_ln
from ponte import ponte

d = Design("fx-ret", HERE, "maelcum FX-RET (dec. 130) - bozza v0.1", board=(100, 220), rev="0.1-bozza")
d.gnd = "AGND"
d.inner_signal = True     # SMD sui due lati (dec. 142), come il master
SIDES = ("L", "R")

# ------------------------------------------------------------ backplane
d.block = "BACKPLANE C96 (classe FX-RET, dec. 130)"
b = {"b1": "BUS_IN_L", "b2": "BUS_IN_R", "b16": "RET_OUT_L", "b17": "RET_OUT_R"}
for k in range(1, 5):
    b["b%d" % (3 * k + 1)] = "S%d_OUT_L" % k
    b["b%d" % (3 * k + 2)] = "S%d_OUT_R" % k
for s in range(1, 11):
    b["b%d" % (3 * s)] = "AGND"
d.part("J", SYM_C96, "C96 maschio", FP_C96, c96(b), ref="J1", place=(50, 213.5, 180),
       note="DIN 41612 C 3x32, angolo retto")
for ref, x in (("H1", 5), ("H2", 95)):
    d.part("H", "Mechanical:MountingHole_Pad", "CHASSIS", "MountingHole:MountingHole_3.2mm_M3_Pad",
           {1: "CHASSIS"}, ref=ref, place=(x, 5, 0), note="foro di fissaggio al pannello, a CHASSIS")

d.block = "ALIMENTAZIONE +-18 audio, +5, +-15 LN, +-5 riferimento"
cv.power_18(d)
power_ln(d)
cv.ref5(d, "U46")
d.power_nets("+18V", "-18V", width=0.4)   # NOTA: a 0,6 mm Freerouting lascia -18V aperta (come il MIC, todo 237)
d.power_nets("V27F+", "V27F-", width=0.4)   # NOTA: via da 1 mm di V27F+ a 0,22 mm dal pad di U30 (DRC)

# ------------------------------------------------------------ bus e mandata al pedale
d.block = "SOMMA DEL BUS (slot 1, Rf 10k, Cf 10p) e DRIVER DEL PEDALE"
for s in SIDES:
    d.R("BUS_IN_" + s, "BSUM_" + s, "10k 0.1%")
    d.C("BUS_IN_" + s, "BSUM_" + s, "10p C0G", note="Cf obbligatorio sul net lungo (fx-module §2bis.4)")
    d.R("PDRV_" + s, "SEND_" + s, "100", note="R serie verso il jack (fx-module §4)")
    d.part("D", "Device:D_TVS", "TVS bidir <=5 pF", "Diode_SMD:D_SOD-323", {1: "SEND_" + s, 2: "AGND"},
           note="NOTA: parte da scegliere (TVS bidirezionale low-cap, fx-module §8.4)")
opa2(d, "U1", ("AGND", "BUS_IN_L", "BSUM_L"), ("AGND", "BUS_IN_R", "BSUM_R"), note="somma del bus, invertente")
opa2(d, "U2", ("BSUM_L", "PDRV_L", "PDRV_L"), ("BSUM_R", "PDRV_R", "PDRV_R"),
     note="driver del pedale, inseguitore (pad fisso 0 dB, dec. 108)")

# ------------------------------------------------------------ ritorno
d.block = "RITORNO: protezione, buffer JFET g=1, servo DC (ritorno-buffer-g1.cir)"
for s in SIDES:
    d.R("JRET_" + s, "RIN_" + s, "100", note="Rprot")
    d.part("D", "Device:D_TVS", "TVS bidir <=5 pF", "Diode_SMD:D_SOD-323", {1: "RIN_" + s, 2: "AGND"},
           note="NOTA: parte da scegliere (<= 5 pF)")
    d.R("RIN_" + s, "AGND", "1M", note="Rbias 1 Mohm (fx-module §4)")
    d.R("BOUT_" + s, "NFB_" + s, "10k 0.1%", note="Rf2: inseguitore, servo sul nodo FB")
    d.R("VINT_" + s, "NFB_" + s, "1M", note="Rinj")
    d.R("O2A_" + s, "SINT_" + s, "1M", note="Rsi: il servo legge il primo invertente (fx-module §5)")
    d.C("SINT_" + s, "VINT_" + s, "15n C0G", C12, note="integratore 1M/15n")
opa2(d, "U3", ("RIN_L", "NFB_L", "BOUT_L"), ("RIN_R", "NFB_R", "BOUT_R"), value="OPA1642AIDR",
     note="buffer JFET hi-Z (OPA1642, SBOS484D)")
opa2(d, "U4", ("AGND", "SINT_L", "VINT_L"), ("AGND", "SINT_R", "VINT_R"), note="servo DC L e R")

d.block = "GAIN T2 (pot doppio 10k lin sul cavo, dec. 162; x1,24 todo 220) e EQ2"
for s, ug, ueq in (("L", "U5", "U7"), ("R", "U6", "U8")):
    d.R("BOUT_" + s, "GA_" + s, "1k24 0.1%", note="Ra")
    d.R("O2A_" + s, "VK2_" + s, "3k24 0.1%")
    d.R("VK2_" + s, "G2_" + s, "4k02 0.1%", note="x1,24 (todo 220)")
    opa2(d, ug, ("AGND", "GW_" + s, "O2A_" + s), ("AGND", "VK2_" + s, "G2_" + s),
         note="GAIN T2: cursore a massa virtuale, poi invertente x1,24")
    cv.eq2(d, ueq, "_" + s, "G2_" + s, "RRN_" + s)

# ------------------------------------------------------------ meter
d.side = "B"   # METER e FADER (solo SMD) sul retro: davanti l'alimentazione non trova posto (dec. 142)
d.block = "METER del ritorno (mono centrato, g = 0,288; detector meter-det-03s.cir)"
d.R("RRN_L", "MG", "20k 0.1%", note="NOTA: (L+R)/2 con due 20k: 10k equivalenti")
d.R("RRN_R", "MG", "20k 0.1%")
d.R("MG", "AGND", "4k02 0.1%", note="g = 4,02/14,02 = 0,287 (doc 0,288), come il master")
d.R("DOUT", "D1A", "1k")
cv.diode(d, "D1A", "HOLD")
d.C("DOUT", "HOLD", "47p C0G")
d.C("HOLD", "AGND", "100n C0G", C12, note="hold: niente altro sul nodo (sim/meter)")
d.R("HOLD", "AGND", "3M", note="release 0,3 s (dec. 81)")
opa4(d, "U9", ("MG", "MGB", "MGB"), ("MGB", "HOLD", "DOUT"), ("HOLD", "MET", "MET"), ("AGND", "NU9", "NU9"),
     note="inseguitore di scala, superdiodo, buffer dell'hold; quarta sezione libera")

# ------------------------------------------------------------ reroute (scheda a parte)
# Divisione PROVVISORIA (NOTE.md): VCA, I/V, shaper, trim e driver d'iniezione dei 4 reroute
# stanno su fx-ret-reroute.py. Qui restano le 10k verso i net dei bus, accanto al C96.
d.block = "PONTE verso la scheda REROUTE (J4) e 10k verso i bus S1-S4"
for j in range(1, 5):
    for s in SIDES:
        d.R("DIR%d_%s" % (j, s), "S%d_OUT_%s" % (j, s), "10k 0.1%",
            note="R lato sorgente sul net del bus (driver d'iniezione sulla scheda reroute)")
ponte(d, "J4", (94, 110, 0), "NOTA: cavo piatto 2x16 verso la scheda reroute (divisione PROVVISORIA, NOTE.md)")

# ------------------------------------------------------------ fader e uscita
d.block = "FADER (2 VCA, shaper del fader, dec. 126) e USCITA verso MSUM (slot 6)"
for k, s in enumerate(SIDES):
    vca(d, "U%d" % (28 + k), "RRN_" + s, "NIF_" + s, "ECF_" + s, "f" + s.lower())
    iv(d, "NIF_" + s, "FAD_" + s)
    d.R("FAD_" + s, "RET_OUT_" + s, "47", note="NOTA: l'I/V fa da buffer d'uscita (<= 50 ohm), 47R verso il backplane")
opa2(d, "U30", ("AGND", "NIF_L", "FAD_L"), ("AGND", "NIF_R", "FAD_R"), note="I/V del fader")
shaper(d, "U31", "F", *cv.FADER, tau="56n C0G")
law_trim(d, "F", "ECF_L", "ECF_R")

d.side = "F"

# ------------------------------------------------------------ cavi
d.block = "CAVO SCHEDA COMANDI (J2) e JACK DEL PEDALE (J3)"
FILI = ["AGND", "GA_L", "GW_L", "O2A_L", "AGND", "GA_R", "GW_R", "O2A_R",
        "AGND", "NA_L", "NB_L", "NC_L", "VHN_L", "WPH_L", "VHP_L", "AGND",
        "NA_R", "NB_R", "NC_R", "VHN_R", "WPH_R", "VHP_R", "AGND", "+REF5",
        "POT_R1", "POT_R2", "POT_R3", "POT_R4", "POT_F", "AGND", "MET", "AGND",
        "+5VF", "CTRL_GND", "AGND", "AGND"]
cv.cavo(d, FILI)
d.part("J", "Connector_Generic:Conn_01x07", "1x7 jack pedale", "Connector_PinHeader_2.54mm:PinHeader_1x07_P2.54mm_Vertical",
       {1: "SEND_L", 2: "SEND_R", 3: "AGND", 4: "JRET_L", 5: "JRET_R", 6: "AGND", 7: "CHASSIS"}, ref="J3",
       place=(88, 12, 90), note="NOTA: cavo verso i jack SEND/RETURN del pedale; posizione dei jack non decisa")

d.audio_rules = {
    "sensibili": r"^(BUS_IN_[LR]|NFB_[LR]|RIN_[LR]|GW_[LR]|VK2_[LR]|NB_[LR]|NSH_[LR]|NVH_[LR]|NHB_[LR]|NIF_[LR]|S\d_OUT_[LR])$",
    "cavo": r"^((GA|GW|O2A|NA|NB|NC|VHN|WPH|VHP)_[LR]|RRN_[LR]|DIR\d_[LR])$",
    "rumorose": r"^(\+5VF?|MET|POT_.*|CVP_.*|SH_.*|V27F[+-]|VREG[+-]|BASE[+-]|RAW.*|CTRL_GND)$",
    "regolatori": ["U40", "U41", "U44", "U45", "Q40", "Q41"],
}

if __name__ == "__main__":
    d.build(route="--no-route" not in sys.argv)
