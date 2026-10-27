"""FX-SEND: micro-modulo send FX (dec. 91a), un canale stereo, 4x lo stesso PCB.

Fonti: docs/fase1/fx-send-module.md, sim/fx/fx-eq2.cir, sim/fx/send-chain-noise.cir,
docs/fase3/sistema-backplane.md (pinout C96), sim/system/psu-rail.cir (ramo +-18).
Valori [PROVVISORIO]. Le scelte non scritte nei documenti sono segnate NOTA
e riportate in pcb/fx-send/NOTE.md.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from pcbgen import Design, boxsym

d = Design("fx-send", HERE, "maelcum FX-SEND (dec. 91a) - bozza", board=(160, 100))
d.gnd = "AGND"
SOIC8 = "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"
SOIC14 = "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm"
R06 = "Resistor_SMD:R_0805_2012Metric"
R12 = "Resistor_SMD:R_1206_3216Metric"
C12 = "Capacitor_SMD:C_1206_3216Metric"

ADG = boxsym("ADG1434", [
    ("1", "IN1", "input"), ("2", "S1A", "passive"), ("3", "D1", "passive"), ("4", "S1B", "passive"),
    ("5", "VSS", "power_in"), ("6", "GND", "power_in"), ("7", "S4B", "passive"), ("8", "D4", "passive"),
    ("9", "S4A", "passive"), ("10", "IN4", "input")], [
    ("20", "IN2", "input"), ("19", "S2A", "passive"), ("18", "D2", "passive"), ("17", "S2B", "passive"),
    ("16", "NC", "no_connect"), ("15", "VDD", "power_in"), ("14", "S3B", "passive"), ("13", "D3", "passive"),
    ("12", "S3A", "passive"), ("11", "IN3", "input")],
    fp="Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm",
    desc="Quad SPDT. PINOUT 6-20 DA VERIFICARE sul datasheet Rev. E (confermati 1-5)")

# ------------------------------------------------------------ backplane
d.block = "BACKPLANE C96 (classe FX-SEND)"
pins = {}
for i in (1, 2): pins["a%d" % i] = "RAW+27"
for i in (3, 4): pins["a%d" % i] = "RAW-27"
for i in (5, 6): pins["a%d" % i] = "RAW+22"
for i in (7, 8): pins["a%d" % i] = "RAW-22"
for i in range(13, 21): pins["a%d" % i] = "AGND"
for i in (21, 22): pins["a%d" % i] = "+5V"
for i in (23, 24): pins["a%d" % i] = "CTRL_GND"
for i in (25, 26): pins["a%d" % i] = "CHASSIS"
pins.update({"b1": "SEND_IN_L", "b2": "SEND_IN_R"})
for k in range(1, 5):
    pins["b%d" % (3 * k + 1)] = "S%d_OUT_L" % k
    pins["b%d" % (3 * k + 2)] = "S%d_OUT_R" % k
for s in range(1, 11):
    pins["b%d" % (3 * s)] = "AGND"
pins["c9"] = "GLOBAL_MUTE"
for i in (16, 20, 24, 28): pins["c%d" % i] = "CTRL_GND"
d.part("J", "Connector:DIN41612_03x32_C_Split", "C96 maschio", "Connector_DIN:DIN41612_C_3x32_Male_Horizontal_THT",
       pins, ref="J1", place=(80, 93.5, 180), note="DIN 41612 C 3x32, angolo retto")
d.part("H", "Mechanical:MountingHole_Pad", "CHASSIS", "MountingHole:MountingHole_3.2mm_M3_Pad",
       {1: "CHASSIS"}, ref="H1", place=(5, 5, 0), note="foro di fissaggio al pannello, a CHASSIS")
d.part("H", "Mechanical:MountingHole_Pad", "CHASSIS", "MountingHole:MountingHole_3.2mm_M3_Pad",
       {1: "CHASSIS"}, ref="H2", place=(155, 5, 0), note="foro di fissaggio al pannello, a CHASSIS")

# ------------------------------------------------------------ alimentazione
d.block = "ALIMENTAZIONE +-18 audio, +-15 switch, +5"
d.power_nets("RAW+27", "RAW-27", "RAW+22", "RAW-22", "+5V", "AGND", "CTRL_GND", "CHASSIS", width=0.8)
d.power_nets("+15SW", "-15SW", "+5VF", width=0.3)
d.power_nets("+18V", "-18V", "V27F+", "V27F-", "V22F+", "V22F-", width=0.6)
FB = "Inductor_SMD:L_1206_3216Metric"
d.part("FB", "Device:FerriteBead_Small", "ferrite 600R", FB, {1: "RAW+27", 2: "V27F+"})
d.part("FB", "Device:FerriteBead_Small", "ferrite 600R", FB, {1: "RAW-27", 2: "V27F-"})
d.part("FB", "Device:FerriteBead_Small", "ferrite 600R", FB, {1: "RAW+22", 2: "V22F+"})
d.part("FB", "Device:FerriteBead_Small", "ferrite 600R", FB, {1: "RAW-22", 2: "V22F-"})
d.part("FB", "Device:FerriteBead_Small", "ferrite 600R", FB, {1: "+5V", 2: "+5VF"})
CPF = "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm"
d.CP("V27F+", "AGND", "220u 35V", CPF)
d.CP("AGND", "V27F-", "220u 35V", CPF)
d.CP("+5VF", "CTRL_GND", "47u 10V", "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm")
# +18: LM317 a 19,2 V + cap-moltiplicatore (sheet §1, psu-rail.cir)
d.part("U", "Regulator_Linear:LM317_TO-220", "LM317", "Package_TO_SOT_THT:TO-220-3_Vertical",
       {"VI": "V27F+", "VO": "VREG+", "ADJ": "ADJ+"}, ref="U10")
d.R("VREG+", "ADJ+", "120 1%")
d.R("ADJ+", "AGND", "1k72 1%", note="1,72k: 19,2 V; E96 1,74k = 19,4 V")
d.CP("ADJ+", "AGND", "10u 35V", "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm")
d.CP("VREG+", "AGND", "47u 35V", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm")
d.part("D", "Diode:1N4148W", "1N4148W", "Diode_SMD:D_SOD-123", {"K": "VREG+", "A": "ADJ+"}, note="scarica Cadj")
d.part("D", "Diode:1N4148W", "S1G", "Diode_SMD:D_SMA", {"K": "V27F+", "A": "VREG+"}, note="protezione inversa")
d.R("VREG+", "BASE+", "1k", note="NOTA: cap-moltiplicatore scalato a ~50 mA (sim: 47R/10mF per 0,85 A)")
d.CP("BASE+", "AGND", "470u 25V", "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm")
d.part("Q", "Transistor_BJT:BD139", "BD139", "Package_TO_SOT_THT:TO-126-3_Vertical",
       {"C": "VREG+", "B": "BASE+", "E": "+18V"})
d.CP("+18V", "AGND", "100u 25V", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm")
# -18: LM337 + cap-moltiplicatore PNP
d.part("U", "Regulator_Linear:LM337_TO220", "LM337", "Package_TO_SOT_THT:TO-220-3_Vertical",
       {"VI": "V27F-", "VO": "VREG-", "ADJ": "ADJ-"}, ref="U11")
d.R("VREG-", "ADJ-", "120 1%")
d.R("ADJ-", "AGND", "1k72 1%")
d.CP("AGND", "ADJ-", "10u 35V", "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm")
d.CP("AGND", "VREG-", "47u 35V", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm")
d.part("D", "Diode:1N4148W", "1N4148W", "Diode_SMD:D_SOD-123", {"A": "VREG-", "K": "ADJ-"})
d.part("D", "Diode:1N4148W", "S1G", "Diode_SMD:D_SMA", {"A": "V27F-", "K": "VREG-"})
d.R("VREG-", "BASE-", "1k")
d.CP("AGND", "BASE-", "470u 25V", "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm")
d.part("Q", "Transistor_BJT:BD140", "BD140", "Package_TO_SOT_THT:TO-126-3_Vertical",
       {"C": "VREG-", "B": "BASE-", "E": "-18V"})
d.CP("AGND", "-18V", "100u 25V", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm")
# +-15 switch: 78L15 / 79L15 dal raw +-22 (dec. 88/90)
d.part("U", "Regulator_Linear:L78L15_SOT89", "78L15", "Package_TO_SOT_SMD:SOT-89-3",
       {"IN": "V22F+", "GND": "AGND", "OUT": "+15SW"}, ref="U12")
d.part("U", "Regulator_Linear:L79L15_SOT89", "79L15", "Package_TO_SOT_SMD:SOT-89-3",
       {"VI": "V22F-", "GND": "AGND", "VO": "-15SW"}, ref="U13")
d.C("V22F+", "AGND", "1u 50V", C12)
d.C("AGND", "V22F-", "1u 50V", C12)
d.C("+15SW", "AGND", "1u 25V", C12)
d.C("AGND", "-15SW", "1u 25V", C12)

# ------------------------------------------------------------ catena audio per lato
OPA1654 = "Amplifier_Operational:TL074"     # stesso pinout quad standard
OPA1612 = "Amplifier_Operational:OPA1612AxD"
d.block = "BUFFER IN (OPA1612)"
d.part("U", OPA1612, "OPA1612AIDR", SOIC8, {3: "SEND_IN_L", 2: "VPRE_L", 1: "VPRE_L",
                                           5: "SEND_IN_R", 6: "VPRE_R", 7: "VPRE_R",
                                           8: "+18V", 4: "-18V"}, ref="U1")
d.R("SEND_IN_L", "AGND", "100k", note="NOTA: tiene l'ingresso a massa senza canale")
d.R("SEND_IN_R", "AGND", "100k")
d.C("+18V", "AGND", "100n")
d.C("AGND", "-18V", "100n")

for side, ueq, uinj in (("L", "U2", "U4"), ("R", "U3", "U5")):
    s = "_" + side
    d.block = "EQ2 lato %s (LOW 120 Hz + HIGH 4,5 kHz, fx-eq2.cir)" % side
    # cella LOW shelf: Za = pot (gang a) // 56n fra NA e NB, Zb = pot (gang b) // 56n fra NC e VLO
    d.R("VPRE" + s, "NA" + s, "1k 0.1%")
    d.C("NA" + s, "NB" + s, "56n C0G", C12)
    d.R("NB" + s, "NC" + s, "1k 0.1%")
    d.C("NC" + s, "VLO" + s, "56n C0G", C12)
    # cella HIGH sottrattiva
    d.C("VLO" + s, "NHA" + s, "10n C0G", C12)
    d.C("NHA" + s, "NHB" + s, "10n C0G", C12)
    d.R("NHA" + s, "VHP" + s, "5k23 0.1%")
    d.R("NHB" + s, "AGND", "2k49 0.1%", note="sim 2,5k: E96 2,49k")
    d.R("VHP" + s, "NVH" + s, "10k 0.1%")
    d.R("NVH" + s, "VHN" + s, "10k 0.1%")
    d.R("VLO" + s, "NSH" + s, "49k9 0.1%")
    d.R("WPH" + s, "NSH" + s, "49k9 0.1%")
    d.R("NSH" + s, "VHI" + s, "49k9 0.1%")
    d.part("U", OPA1654, "OPA1654AIDR", SOIC14, {
        3: "AGND", 2: "NB" + s, 1: "VLO" + s,                # LOW
        5: "NHB" + s, 6: "VHP" + s, 7: "VHP" + s,           # HIGH follower
        10: "AGND", 9: "NVH" + s, 8: "VHN" + s,             # HIGH invertente
        12: "AGND", 13: "NSH" + s, 14: "VHI" + s,           # HIGH somma
        4: "+18V", 11: "-18V"}, ref=ueq)
    d.C("+18V", "AGND", "100n")
    d.C("AGND", "-18V", "100n")
    d.block = "INIEZIONE lato %s (OPA1654 + 10k verso i bus)" % side
    d.part("U", OPA1654, "OPA1654AIDR", SOIC14, {
        3: "SW1" + s, 2: "INJ1" + s, 1: "INJ1" + s,
        5: "SW2" + s, 6: "INJ2" + s, 7: "INJ2" + s,
        10: "SW3" + s, 9: "INJ3" + s, 8: "INJ3" + s,
        12: "SW4" + s, 13: "INJ4" + s, 14: "INJ4" + s,
        4: "+18V", 11: "-18V"}, ref=uinj)
    d.C("+18V", "AGND", "100n")
    d.C("AGND", "-18V", "100n")
    for k in range(1, 5):
        d.R("INJ%d%s" % (k, s), "S%d_OUT%s" % (k, s), "10k 0.1%")

# ------------------------------------------------------------ assign
d.block = "ASSIGN S1-S4 (ADG1434 pi SPDT, soft-switch 1 ms, mute globale)"
for side, ref in (("L", "U6"), ("R", "U7")):
    s = "_" + side
    p = {"VDD": "+15SW", "VSS": "-15SW", "GND": "AGND", "NC": None}
    for k in range(1, 5):
        p["IN%d" % k] = "ASG%d" % k
        p["S%dA" % k] = "LVL_W" + s        # NOTA: A = serie (IN alto), da verificare
        p["S%dB" % k] = "AGND"             # shunt a massa da off
        p["D%d" % k] = "SW%d%s" % (k, s)
    d.part("U", ADG, "ADG1434YRUZ", "Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm", p, ref=ref,
           note="pinout 6-20 e tabella di verità DA VERIFICARE")
    d.C("+15SW", "AGND", "100n")
    d.C("AGND", "-15SW", "100n")
for k in range(1, 5):
    d.R("BTN%d" % k, "ASG%d" % k, "10k")
    d.C("ASG%d" % k, "CTRL_GND", "100n")
    d.R("ASG%d" % k, "CTRL_GND", "10k")
    d.R("ASG%d" % k, "MD%d" % k, "4k7", note="NOTA: rampa del mute ~0,5 ms")
    d.part("Q", "Transistor_FET:2N7002", "2N7002", "Package_TO_SOT_SMD:SOT-23",
           {"D": "MD%d" % k, "S": "CTRL_GND", "G": "MUTE_G"})
d.R("GLOBAL_MUTE", "MUTE_G", "1k")
d.R("MUTE_G", "+5VF", "100k", note="NOTA: polarità c9 provvisoria, alto = muto (fail-safe)")

# ------------------------------------------------------------ harness verso il pannello
d.block = "HARNESS PANNELLO (pot LOW 4 sezioni, HIGH 2, LEVEL 2, 4 bottoni)"
h = ["AGND", "NA_L", "NB_L", "NC_L", "VLO_L", "AGND", "NA_R", "NB_R", "NC_R", "VLO_R",
     "AGND", "VHN_L", "WPH_L", "VHP_L", "VHN_R", "WPH_R", "VHP_R", "AGND",
     "VHI_L", "LVL_W_L", "AGND", "VHI_R", "LVL_W_R", "AGND",
     "+5VF", "BTN1", "BTN2", "BTN3", "BTN4", "CTRL_GND", "CHASSIS", "AGND", "AGND", "AGND"]
d.part("J", "Connector_Generic:Conn_02x17_Odd_Even", "IDC 2x17", "Connector_IDC:IDC-Header_2x17_P2.54mm_Vertical",
       {i + 1: n for i, n in enumerate(h)}, ref="J2", place=(80, 6, 90),
       note="NOTA: pot fuori scheda; NB_x e NSH vicini alla massa virtuale")

if __name__ == "__main__":
    d.build(route="--no-route" not in sys.argv)
