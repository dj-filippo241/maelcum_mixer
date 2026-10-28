"""MASTER, scheda di SEGNALE (dec. 140): somma, MONO, insert, buffer, VCA MASTER e BOOTH, meter.

Il modulo master è fatto di quattro schede (master-out.md, ADDENDUM 2026-10-28):
questa col C96; la scheda di USCITA sovrapposta (master-uscita.py, J2); la scheda comandi
dietro il pannello (master-comandi.py, J3); la schedina dei connettori sul retro (dec. 141).

Fonti: docs/fase1/master-out.md (§2, §3.1, §3.2, §3.6, ADDENDA 2026-10-02 e 2026-10-14),
sim/master-out/sum-noise-71A.cir (somma), sim/master-out/mono-ms.cir (MONO, blocchi ideali),
sim/shaper/shaper-master.cir e shaper-fader.cir (shaper), docs/fase3/sistema-vca-trim.md §3
(trim), sim/system/meter-det-03s.cir e sistema-metering.md §2, §5 (detector, riferimenti),
docs/fase3/sistema-backplane.md (C96, classe MASTER). Valori [PROVVISORIO].
Le scelte non scritte nei documenti sono segnate NOTA e riportate in pcb/master/NOTE.md.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from pcbgen import Design, boxsym
from backplane import c96, SYM_C96, FP_C96, A_STANDARD

d = Design("master-segnale", os.path.join(HERE, "segnale"), "maelcum MASTER scheda di segnale (dec. 140) - bozza v0.1",
           board=(150, 165), rev="0.1-bozza")
d.gnd = "AGND"
SOIC8 = "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"
C12 = "Capacitor_SMD:C_1206_3216Metric"
OPA = "Amplifier_Operational:OPA1612AxD"
TRIM = "Potentiometer_THT:Potentiometer_Bourns_3266W_Vertical"

# THAT 2181 / CoolAudio V2181L: piedinatura dal datasheet THAT 2181-Series, tabella 1
# (letta il 2026-10-28); il clone ha la stessa (sistema-vca-trim.md §2).
VCA = boxsym("V2181", [
    ("1", "IN", "input"), ("2", "EC+", "input"), ("3", "EC-", "input"), ("4", "SYM", "input")], [
    ("8", "OUT", "output"), ("7", "V+", "power_in"), ("6", "GND", "power_in"), ("5", "V-", "passive")],
    fp=SOIC8, desc="VCA singolo. Pinout dal datasheet THAT 2181 tabella 1 (2026-10-28)")


def opa(ref, a, b, vp="+15LN", vm="-15LN", note=""):
    """OPA1612 doppio. a, b = (ingresso +, ingresso -, uscita) delle due sezioni."""
    d.part("U", OPA, "OPA1612AIDR", SOIC8, {3: a[0], 2: a[1], 1: a[2], 5: b[0], 6: b[1], 7: b[2],
                                            8: vp, 4: vm}, ref=ref, note=note)
    d.C(vp, "AGND", "100n")
    d.C("AGND", vm, "100n")


def vca(ref, inp, iv, ec_m, note=""):
    """VCA: corrente d'ingresso da 20k, uscita sul nodo I/V; trim di simmetria su ogni chip."""
    s = ref.lower()
    d.R(inp, "VIN_" + s, "20k 0.1%")
    d.part("U", VCA, "V2181L", SOIC8, {"IN": "VIN_" + s, "EC+": "AGND", "EC-": ec_m, "SYM": "SYM_" + s,
                                      "OUT": iv, "V+": "+18V", "GND": "AGND", "V-": "VEE_" + s}, ref=ref, note=note)
    d.R("VEE_" + s, "-18V", "6k19", note="NOTA: 5,1k del datasheet a -15 V riscalato a -18 V (2,4 mA)")
    d.C("+18V", "AGND", "100n")
    d.C("AGND", "-18V", "100n")
    # trim di simmetria (vca-trim §3.1): 50k fra +-15 LN -> 150k -> pin 4, 51R a massa
    d.part("RV", "Device:R_Potentiometer_Trim", "50k", TRIM, {1: "+15LN", 2: "SW_" + s, 3: "-15LN"},
           note="trim di simmetria (THD minima)")
    d.R("SW_" + s, "SYM_" + s, "150k")
    d.R("SYM_" + s, "AGND", "51")


# ------------------------------------------------------------ backplane
d.block = "BACKPLANE C96 (classe MASTER)"
b = {}
slot = ["MSUM1", "MSUM2", "MSUM3", "MSUM4", "MSUM5", "MSUM6", "MSUM7", "MON_OUT", "INS_SEND", "INS_RET"]
for k, n in enumerate(slot):
    b["b%d" % (3 * k + 1)] = n + "_L"
    b["b%d" % (3 * k + 2)] = n + "_R"
    b["b%d" % (3 * k + 3)] = "AGND"
b["b31"], b["b32"] = "VIE_TAP_L", "VIE_TAP_R"
pins = c96(b, a=A_STANDARD + ["a9", "a10", "a11", "a12"], c=["c9", "c17"])
d.part("J", SYM_C96, "C96 maschio", FP_C96, pins, ref="J1", place=(75, 158.5, 180),
       note="DIN 41612 C 3x32, angolo retto; il master popola anche a9-a12 (+-26 V [M])")
d.part("H", "Mechanical:MountingHole_Pad", "CHASSIS", "MountingHole:MountingHole_3.2mm_M3_Pad",
       {1: "CHASSIS"}, ref="H1", place=(5, 5, 0), note="foro di fissaggio al pannello, a CHASSIS")
d.part("H", "Mechanical:MountingHole_Pad", "CHASSIS", "MountingHole:MountingHole_3.2mm_M3_Pad",
       {1: "CHASSIS"}, ref="H2", place=(145, 5, 0), note="foro di fissaggio al pannello, a CHASSIS")

# ------------------------------------------------------------ alimentazione
d.block = "ALIMENTAZIONE +-18 (LM317/337 + cap-moltiplicatore), +-15 LN (LT3045/LT3094)"
d.power_nets("RAW+27", "RAW-27", "RAW+22", "RAW-22", "RAW+26", "RAW-26", "+5V", "AGND", "CTRL_GND", "CHASSIS", width=0.8)
d.power_nets("+18V", "-18V", "+15LN", "-15LN", "V27F+", "V27F-", width=0.6)
FB = "Inductor_SMD:L_1206_3216Metric"
d.part("FB", "Device:FerriteBead_Small", "ferrite 600R", FB, {1: "RAW+27", 2: "V27F+"})
d.part("FB", "Device:FerriteBead_Small", "ferrite 600R", FB, {1: "RAW-27", 2: "V27F-"})
CPF = "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm"
d.CP("V27F+", "AGND", "220u 35V", CPF)
d.CP("AGND", "V27F-", "220u 35V", CPF)
# +-18: come il FX-SEND (sheet §1, psu-rail.cir)
d.part("U", "Regulator_Linear:LM317_TO-220", "LM317", "Package_TO_SOT_THT:TO-220-3_Vertical",
       {"VI": "V27F+", "VO": "VREG+", "ADJ": "ADJ+"}, ref="U40")
d.R("VREG+", "ADJ+", "120 1%")
d.R("ADJ+", "AGND", "1k72 1%", note="19,2 V")
d.CP("ADJ+", "AGND", "10u 35V", "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm")
d.CP("VREG+", "AGND", "47u 35V", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm")
d.part("D", "Diode:1N4148W", "1N4148W", "Diode_SMD:D_SOD-123", {"K": "VREG+", "A": "ADJ+"}, note="scarica Cadj")
d.part("D", "Device:D", "S1G", "Diode_SMD:D_SMA", {"K": "V27F+", "A": "VREG+"}, note="protezione inversa")
d.R("VREG+", "BASE+", "1k", note="NOTA: cap-moltiplicatore come il FX-SEND (~150 mA qui)")
d.CP("BASE+", "AGND", "470u 25V", CPF)
d.part("Q", "Transistor_BJT:BD139", "BD139", "Package_TO_SOT_THT:TO-126-3_Vertical",
       {"C": "VREG+", "B": "BASE+", "E": "+18V"}, ref="Q40")
d.CP("+18V", "AGND", "100u 25V", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm")
d.part("U", "Regulator_Linear:LM337_TO220", "LM337", "Package_TO_SOT_THT:TO-220-3_Vertical",
       {"VI": "V27F-", "VO": "VREG-", "ADJ": "ADJ-"}, ref="U41")
d.R("VREG-", "ADJ-", "120 1%")
d.R("ADJ-", "AGND", "1k72 1%")
d.CP("AGND", "ADJ-", "10u 35V", "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm")
d.CP("AGND", "VREG-", "47u 35V", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm")
d.part("D", "Diode:1N4148W", "1N4148W", "Diode_SMD:D_SOD-123", {"A": "VREG-", "K": "ADJ-"})
d.part("D", "Device:D", "S1G", "Diode_SMD:D_SMA", {"A": "V27F-", "K": "VREG-"})
d.R("VREG-", "BASE-", "1k")
d.CP("AGND", "BASE-", "470u 25V", CPF)
d.part("Q", "Transistor_BJT:BD140", "BD140", "Package_TO_SOT_THT:TO-126-3_Vertical",
       {"C": "VREG-", "B": "BASE-", "E": "-18V"}, ref="Q41")
d.CP("AGND", "-18V", "100u 25V", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm")
# +-15 LN dal +-18 (master-out §3.8, dec. 93): SET = 15 V / 100 uA = 150k.
# Pinout dal simbolo KiCad LT3045xMSE / LT3093xMSE: DA VERIFICARE sul datasheet (NOTE.md).
MSE = "Package_SO:MSOP-12-1EP_3x4.039mm_P0.65mm_EP1.651x2.845mm"
d.part("U", "Regulator_Linear:LT3045xMSE", "LT3045EMSE", MSE, {
    1: "+18V", 2: "+18V", 3: "+18V", 4: "+18V", 5: None, 6: "AGND", 7: "AGND", 8: "SETP",
    9: "AGND", 10: "+15LN", 11: "+15LN", 12: "+15LN", 13: "AGND"}, ref="U42",
    note="EN/UV a IN; ILIM a massa = limite massimo; PG libero, PGFB a massa: NOTA da verificare")
d.R("SETP", "AGND", "150k 0.1%")
d.C("SETP", "AGND", "4u7 25V", C12, note="rumore del riferimento (datasheet: 4,7 uF)")
d.C("+18V", "AGND", "4u7 25V", C12)
d.C("+15LN", "AGND", "10u 25V", C12)
d.part("U", "Regulator_Linear:LT3094xMSE", "LT3094EMSE", MSE, {
    1: "-18V", 2: "-18V", 13: "-18V", 3: "-18V", 4: None, 5: "AGND", 6: "AGND", 7: None, 8: "SETN",
    9: "AGND", 10: "-15LN", 11: "-15LN", 12: "-15LN"}, ref="U43",
    note="EN/UV a IN; VIOC libero; PG libero: NOTA da verificare")
d.R("SETN", "AGND", "150k 0.1%")
d.C("AGND", "SETN", "4u7 25V", C12)
d.C("AGND", "-18V", "4u7 25V", C12)
d.C("AGND", "-15LN", "10u 25V", C12)
# +-5 V di riferimento per pot e shaper (sistema-shaper §2): LM4040-5,0 + follower, -5 = inverso
d.R("+15LN", "REF5K", "1k5", note="NOTA: ~6,7 mA nel riferimento")
d.part("D", "Reference_Voltage:LM4040DBZ-5", "LM4040-5.0", "Package_TO_SOT_SMD:SOT-23",
       {"K": "REF5K", "A": "AGND", "NC": None})
d.C("REF5K", "AGND", "1u", C12)
d.R("+REF5", "NREF5I", "10k 0.1%")
d.R("NREF5I", "-REF5", "10k 0.1%")
opa("U30", ("REF5K", "+REF5", "+REF5"), ("AGND", "NREF5I", "-REF5"), note="+5 e -5 V di riferimento")

# ------------------------------------------------------------ somma e MONO
d.block = "MASTER SUMMING [A2] (invertente, 20k/20k/10p, sum-noise-71A.cir)"
opa("U1", ("AGND", "NS_L", "SUM_L"), ("AGND", "NS_R", "SUM_R"))
for s in ("L", "R"):
    for k in range(1, 6):
        d.R("MSUM%d_%s" % (k, s), "NS_" + s, "20k 0.1%")
    # MSUM6/7: multidrop, R di somma lato sorgente (dec. 97): entrano dritti sulla massa virtuale
    d.R("MSUM6_" + s, "NS_" + s, "0", note="MSUM6 (mic) dritto sul nodo: R di somma nei moduli (dec. 97)")
    d.R("MSUM7_" + s, "NS_" + s, "0", note="MSUM7 (mono) dritto sul nodo: R di somma nei moduli (dec. 97)")
    d.R("NS_" + s, "SUM_" + s, "20k 0.1%")
    d.C("NS_" + s, "SUM_" + s, "10p C0G")

d.block = "MONO [A3] (matrice M/S + VCA su S, mono-ms.cir; resistenze NOTA)"
# M = -(L+R)/2 ; S = (L-R)/2 ; Sv = -S dal VCA + I/V ; L' = -(M + Sv) = L ; R' = Sv - M = R
# (somma invertente di prima: la catena [A2]+[A3] resta invertente, come [A2] da solo)
d.R("SUM_L", "NM", "20k 0.1%")
d.R("SUM_R", "NM", "20k 0.1%")
d.R("NM", "MID", "10k 0.1%")
d.R("SUM_L", "SDP", "20k 0.1%")
d.R("SDP", "AGND", "10k 0.1%")
d.R("SUM_R", "SDN", "20k 0.1%")
d.R("SDN", "SIDE", "10k 0.1%")
opa("U2", ("AGND", "NM", "MID"), ("SDP", "SDN", "SIDE"), note="M e S")
vca("U9", "SIDE", "NSV", "ECM_MONO", note="VCA del MONO: 0 dB a tasto spento, -100 dB a tasto premuto")
d.R("NSV", "SV", "20k 0.1%")
d.C("NSV", "SV", "22p C0G")
d.R("MID", "NLO", "20k 0.1%")
d.R("SV", "NLO", "20k 0.1%")
d.R("NLO", "LO_L", "20k 0.1%")
d.R("SV", "RDP", "20k 0.1%")
d.R("RDP", "AGND", "20k 0.1%")
d.R("MID", "RDN", "20k 0.1%")
d.R("RDN", "LO_R", "20k 0.1%")
opa("U3", ("AGND", "NSV", "SV"), ("AGND", "NLO", "LO_L"), note="I/V del VCA di S e uscita L'")
# tasto MONO: chiuso = +5 V -> RC 1 ms -> follower -> 0,61 V su EC- = -100 dB (mono-ms.cir)
d.R("MONO_SW", "AGND", "10k", note="NOTA: tasto a ritenuta verso +5 REF; aperto = stereo")
d.R("MONO_SW", "MRC", "10k")
d.C("MRC", "AGND", "100n C0G", note="rampa 1 ms (dec. 80, senza BBM)")
d.R("MBUF", "ECM_MONO", "7k15 0.1%")
d.R("ECM_MONO", "AGND", "1k 0.1%", note="5 V x 1/8,15 = 0,613 V = -100 dB")
opa("U4", ("RDP", "RDN", "LO_R"), ("MRC", "MBUF", "MBUF"), note="uscita R' e follower della rampa MONO")

# ------------------------------------------------------------ insert del grafico (dec. 111 b)
d.block = "INS_SEND driver + INS_RET buffer (slot 9-10, ponticello JMS sul backplane)"
opa("U5", ("LO_L", "ISD_L", "ISD_L"), ("LO_R", "ISD_R", "ISD_R"), note="driver <= 50 ohm")
d.R("ISD_L", "INS_SEND_L", "47", note="NOTA: 47 ohm di uscita, stabilità sul cavo del backplane")
d.R("ISD_R", "INS_SEND_R", "47")
d.R("INS_RET_L", "AGND", "100k", note="ricevitore >= 100k; tiene l'ingresso senza ponticello")
d.R("INS_RET_R", "AGND", "100k")
opa("U6", ("INS_RET_L", "PROG_L", "PROG_L"), ("INS_RET_R", "PROG_R", "PROG_R"), note="nodo di programma")

# ------------------------------------------------------------ quattro buffer dal nodo di programma
d.block = "BUFFER [A] [B] [C] [N] (un buffer per uscita, voce 11)"
opa("U7", ("PROG_L", "BA_L", "BA_L"), ("PROG_R", "BA_R", "BA_R"), "+18V", "-18V", note="[A] verso MASTER LEVEL")
opa("U8", ("PROG_L", "BB_L", "BB_L"), ("PROG_R", "BB_R", "BB_R"), "+18V", "-18V", note="[B] verso BOOTH LEVEL")
# [C] REC: pad a ponticelli 0/-10/-20 dB davanti al follower (dec. 63); di serie 0 dB
for s in ("L", "R"):
    d.R("PROG_" + s, "PAD_" + s, "6k81 0.1%")
    d.part("JP", "Jumper:SolderJumper_2_Bridged", "0 dB", "Jumper:SolderJumper-2_P1.3mm_Bridged_RoundedPad1.0x1.5mm",
           {1: "PROG_" + s, 2: "PAD_" + s}, note="REC 0 dB (chiuso di serie, dec. 63)")
    d.R("PAD_" + s, "P10_" + s, "3k16 0.1%")
    d.part("JP", "Jumper:SolderJumper_2_Open", "-10 dB", "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm",
           {1: "P10_" + s, 2: "AGND"}, note="REC -10 dB: aprire il 0 dB e chiudere questo")
    d.R("PAD_" + s, "P20_" + s, "757 0.1%")
    d.part("JP", "Jumper:SolderJumper_2_Open", "-20 dB", "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm",
           {1: "P20_" + s, 2: "AGND"}, note="REC -20 dB")
opa("U10", ("PAD_L", "RECD_L", "RECD_L"), ("PAD_R", "RECD_R", "RECD_R"), note="[C] REC")
d.R("RECD_L", "REC_L", "47")
d.R("RECD_R", "REC_R", "47")
opa("U11", ("PROG_L", "MONB_L", "MONB_L"), ("PROG_R", "MONB_R", "MONB_R"), note="[N] MON verso il CUE")
d.R("MONB_L", "MON_OUT_L", "47")
d.R("MONB_R", "MON_OUT_R", "47")

# ------------------------------------------------------------ MASTER LEVEL e BOOTH LEVEL
d.block = "MASTER LEVEL [D]: 2 VCA, shaper (shaper-master.cir), trim di law (vca-trim §3.2)"
vca("U12", "BA_L", "NIM_L", "ECM_ML")
vca("U13", "BA_R", "NIM_R", "ECM_MR")
for s in ("L", "R"):
    d.R("NIM_" + s, "MAST_" + s, "20k 0.1%")
    d.C("NIM_" + s, "MAST_" + s, "22p C0G")
opa("U14", ("AGND", "NIM_L", "MAST_L"), ("AGND", "NIM_R", "MAST_R"), "+18V", "-18V", note="I/V MASTER")


def shaper(tag, rm, rami, roff=None):
    """Shaper a diodi (sistema-shaper §2): pot 0-5 V su X, rami verso -5 V, Rf 10k.
    Poi lo stadio del partitore: invertente x(-1/5), così con 1k/1k la CV al pin è out/10."""
    x, sj, out = "POT_" + tag, "SJ_" + tag, "SH_" + tag
    d.R(x, sj, rm + " 0.1%")
    if roff:
        d.R("-REF5", sj, roff + " 0.1%", note="ramo d'offset per il +6 dB (shaper-master.cir)")
    for k, (ra, rb) in enumerate(rami, 1):
        n = "SN%d_%s" % (k, tag)
        d.R(x, n, ra + " 0.1%")
        d.R(n, "-REF5", rb + " 0.1%")
        d.part("D", "Diode:1N4148W", "1N4148W", "Diode_SMD:D_SOD-123", {"A": n, "K": sj})
    d.R(sj, out, "10k 0.1%")
    d.R(out, "NP_" + tag, "10k 0.1%")
    d.R("NP_" + tag, "CVP_" + tag, "2k 0.1%", note="NOTA: stadio del partitore x(-1/5): CV al pin = out/10")
    opa("U%d" % {"M": 15, "B": 16}[tag], ("AGND", sj, out), ("AGND", "NP_" + tag, "CVP_" + tag), note="shaper " + tag)
    d.R(x, "AGND", "100k", note="NOTA: pot staccato = shaper a 0 V = taglio massimo")


def law_trim(tag, cvp, ecl, ecr):
    """Partitori di coppia (vca-trim §3.2): L 1,00k/1,00k; R 900 + trimmer 200 ohm / 1,00k + offset."""
    d.R(cvp, ecl, "1k 0.1%")
    d.R(ecl, "AGND", "1k 0.1%")
    d.R(cvp, "LT_" + tag, "909 0.1%", note="E96: 909 (doc: 900)")
    d.part("RV", "Device:R_Potentiometer_Trim", "200", TRIM, {1: "LT_" + tag, 2: ecr, 3: ecr},
           note="trim di law, 25 giri (vca-trim §3.2)")
    d.R(ecr, "AGND", "1k 0.1%")
    d.part("RV", "Device:R_Potentiometer_Trim", "50k", TRIM, {1: "+15LN", 2: "OF_" + tag, 3: "-15LN"},
           note="trim d'offset di coppia")
    d.R("OF_" + tag, ecr, "1M5")


shaper("M", "68.1k", [("1.91k", "2.43k"), ("16.9k", "38.3k"), ("1.82k", "2.43k"), ("1.96k", "2.61k")], roff="137k")
law_trim("M", "CVP_M", "ECM_ML", "ECM_MR")

d.block = "BOOTH LEVEL [B2]: 2 VCA, shaper del fader (shaper-fader.cir), trim di law"
vca("U17", "BB_L", "NIB_L", "ECM_BL")
vca("U18", "BB_R", "NIB_R", "ECM_BR")
for s in ("L", "R"):
    d.R("NIB_" + s, "BOOTH_" + s, "20k 0.1%")
    d.C("NIB_" + s, "BOOTH_" + s, "22p C0G")
opa("U19", ("AGND", "NIB_L", "BOOTH_L"), ("AGND", "NIB_R", "BOOTH_R"), "+18V", "-18V", note="I/V BOOTH")
shaper("B", "43.2k", [("68.1k", "357k"), ("20.0k", "38.3k"), ("976", "1.33k")])
law_trim("B", "CVP_B", "ECM_BL", "ECM_BR")

# ------------------------------------------------------------ VIE_TAP (dec. 111 b)
d.block = "VIE_TAP [V]: driver dopo MASTER LEVEL verso b31-b32"
opa("U20", ("MAST_L", "VTD_L", "VTD_L"), ("MAST_R", "VTD_R", "VTD_R"), "+18V", "-18V")
d.R("VTD_L", "VIE_TAP_L", "47")
d.R("VTD_R", "VIE_TAP_R", "47")

# ------------------------------------------------------------ meter [E]
d.block = "METER [E]: detector di picco L/R (meter-det-03s.cir) e albero dei riferimenti (metering §5)"
for s, u1, u2 in (("L", "U21", "U22"), ("R", "U23", "U24")):
    d.R("MAST_" + s, "MG_" + s, "10k 0.1%", note="g = 0,287 (FS +24 dBu -> 5,00 V; doc 0,288)")
    d.R("MG_" + s, "AGND", "4k02 0.1%")
    d.R("DOUT_" + s, "D1A_" + s, "1k")
    d.part("D", "Diode:1N4148W", "1N4148W", "Diode_SMD:D_SOD-123", {"A": "D1A_" + s, "K": "HOLD_" + s})
    d.C("DOUT_" + s, "HOLD_" + s, "47p C0G")
    d.C("HOLD_" + s, "AGND", "100n C0G", C12, note="hold: niente altro sul nodo (sim/meter)")
    d.R("HOLD_" + s, "AGND", "3M", note="release 0,3 s (dec. 81)")
    opa(u1, ("MG_" + s, "MGB_" + s, "MGB_" + s), ("MGB_" + s, "HOLD_" + s, "DOUT_" + s),
        note="follower di scala e superdiodo")
    opa(u2, ("HOLD_" + s, "MET_" + s, "MET_" + s), ("AGND", "NU_" + s, "NU_" + s),
        note="buffer dell'hold verso gli LM3915; seconda sezione libera, a inseguitore a massa")
d.R("+15LN", "VRA0", "10k 0.1%")
d.R("VRA0", "AGND", "5k 0.1%")
d.R("VREFA", "VRB0", "10k 0.1%")
d.R("VRB0", "AGND", "4k64 0.1%", note="doc 4,625k: E96 4,64k = 1,585 V (+0,02 dB)")
opa("U25", ("VRA0", "VREFA", "VREFA"), ("VRB0", "VREFB", "VREFB"), note="vrefA 5,000 V e vrefB 1,58 V")

# ------------------------------------------------------------ connettori verso le altre schede
d.block = "CONNETTORI: J2 verso la scheda di USCITA, J3 verso la scheda COMANDI"
J2 = ["RAW+26", "RAW+26", "RAW-26", "RAW-26", "RAW+27", "RAW-27", "AGND", "AGND",
      "MAST_L", "AGND", "MAST_R", "AGND", "BOOTH_L", "AGND", "BOOTH_R", "AGND", "REC_L", "AGND", "REC_R", "AGND",
      "+5V", "CTRL_GND", "GLOBAL_MUTE", "AC_OK", "CLIP_L", "CLIP_R"]
d.part("J", "Connector_Generic:Conn_02x13_Odd_Even", "2x13 scheda-scheda",
       "Connector_PinHeader_2.54mm:PinHeader_2x13_P2.54mm_Vertical",
       {i + 1: n for i, n in enumerate(J2)}, ref="J2", place=(120, 80, 90),
       note="NOTA: connettore verso la scheda di uscita sovrapposta (dec. 140); AGND fra i segnali")
J3 = ["POT_M", "AGND", "POT_B", "AGND", "+REF5", "AGND", "MONO_SW", "AGND",
      "MET_L", "AGND", "MET_R", "AGND", "VREFA", "VREFB", "CLIP_L", "CLIP_R", "+5V", "+5V", "CTRL_GND", "CTRL_GND"]
d.part("J", "Connector_Generic:Conn_02x10_Odd_Even", "2x10 cavo piatto",
       "Connector_PinHeader_2.54mm:PinHeader_2x10_P2.54mm_Vertical",
       {i + 1: n for i, n in enumerate(J3)}, ref="J3", place=(50, 5, 90),
       note="cavo piatto corto verso la scheda comandi (pot, MONO, LED)")

d.audio_rules = {
    "sensibili": r"^((NS|NIM|NIB|PROG|INS_RET|MSUM\d)_[LR]|NM|NSV|NLO|SDN|SDP|RDN|RDP|VIN_u\d+)$",
    "cavo": r"^(POT_M|POT_B|MONO_SW)$",
    "rumorose": r"^(\+5V|CTRL_GND|GLOBAL_MUTE|AC_OK|CLIP_[LR]|RAW.*|V27F[+-]|VREG[+-]|BASE[+-])$",
    "regolatori": ["U40", "U41", "U42", "U43", "Q40", "Q41"],
}

if __name__ == "__main__":
    d.build(route="--no-route" not in sys.argv)
