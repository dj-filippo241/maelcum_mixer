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
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from pcbgen import Design
import celle_micmono as cm
from celle_micmono import opa2, opa4, diode, C12, VCA, TRIM

d = Design("mic", HERE, "maelcum MIC (dec. 97) - bozza v0.1", board=(100, 220), rev="0.1-bozza")
d.gnd = "AGND"

from cavo import CAVO as FILI     # ordine dei fili: cavo.py, letto anche dalla scheda comandi

d.block = "BACKPLANE C96 (classe MIC/GEN, MSUM6)"
cm.backplane(d, "MSUM6")

d.block = "ALIMENTAZIONE +-18 audio, +-15 switch, +5, +-15 LN"
cm.power_18_sw(d)
cm.power_ln(d)
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
