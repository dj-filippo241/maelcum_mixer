"""Celle comuni a CANALE e FX-RET (todo 167): VCA col trim, shaper a diodi, trim di law,
alimentazione +-18 senza i +-15 switch, riferimenti +-5 V, EQ2 stereo.

Copiate da pcb/master/master-segnale.py (VCA, shaper, law_trim, riferimenti) e da
pcb/fx-send/fx-send.py (EQ2, alimentazione), così le schede nuove non toccano i file del
master e del FX-SEND. Ogni funzione aggiunge parti al Design che riceve. Valori [PROVVISORIO].

Pinout verificati sui datasheet:
- V2181 / THAT 2181: tabella 1 (come master-segnale.py, sistema-vca-trim.md §2).
- OPA1612, OPA1642 SOIC-8: coppia standard. OPA1642: TI SBOS484D p. 4, «Pin Functions:
  OPA1642» (scaricato e letto il 2026-11-04): 1 OUT A, 2 -IN A, 3 +IN A, 4 V-, 5 +IN B,
  6 -IN B, 7 OUT B, 8 V+.
- OPA1654 SOIC-14: quad standard (simbolo TL074, come fx-send.py).
"""
from pcbgen import boxsym

SOIC8 = "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"
SOIC14 = "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm"
C12 = "Capacitor_SMD:C_1206_3216Metric"
OPA1612 = "Amplifier_Operational:OPA1612AxD"
OPA1654 = "Amplifier_Operational:TL074"      # stesso pinout quad standard (come fx-send.py)
TRIM = "Potentiometer_THT:Potentiometer_Bourns_3266W_Vertical"
DIODE = "Diode:1N4148W"
SOD123 = "Diode_SMD:D_SOD-123"
CPF = "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm"
FB = "Inductor_SMD:L_1206_3216Metric"

VCA = boxsym("V2181", [
    ("1", "IN", "input"), ("2", "EC+", "input"), ("3", "EC-", "input"), ("4", "SYM", "input")], [
    ("8", "OUT", "output"), ("7", "V+", "power_in"), ("6", "GND", "power_in"), ("5", "V-", "passive")],
    fp=SOIC8, desc="VCA singolo. Pinout dal datasheet THAT 2181 tabella 1 (2026-10-28)")


def opa2(d, ref, a, b, vp="+18V", vm="-18V", note="", value="OPA1612AIDR"):
    """Op-amp doppio standard: a, b = (ingresso +, ingresso -, uscita)."""
    d.part("U", OPA1612, value, SOIC8, {3: a[0], 2: a[1], 1: a[2], 5: b[0], 6: b[1], 7: b[2],
                                       8: vp, 4: vm}, ref=ref, note=note)
    d.C(vp, "AGND", "100n")
    d.C("AGND", vm, "100n")


def opa4(d, ref, a, b, c, e, vp="+18V", vm="-18V", note=""):
    """OPA1654 quad: a, b, c, e = (ingresso +, ingresso -, uscita) delle sezioni A-D."""
    d.part("U", OPA1654, "OPA1654AIDR", SOIC14, {
        3: a[0], 2: a[1], 1: a[2], 5: b[0], 6: b[1], 7: b[2],
        10: c[0], 9: c[1], 8: c[2], 12: e[0], 13: e[1], 14: e[2],
        4: vp, 11: vm}, ref=ref, note=note)
    d.C(vp, "AGND", "100n")
    d.C("AGND", vm, "100n")


def diode(d, a, k, note=""):
    return d.part("D", DIODE, "1N4148W", SOD123, {"A": a, "K": k}, note=note)


# ------------------------------------------------------------ VCA
def vca(d, ref, inp, iv, ec_m, tag):
    """VCA come master-segnale.py: 20k d'ingresso, uscita in corrente sul nodo I/V, 6,19k sul
    V- a -18 V, trim di simmetria 50k fra +-15 LN -> 150k -> pin 4, 51 ohm a massa (vca-trim §3.1)."""
    d.R(inp, "VIN_" + tag, "20k 0.1%")
    d.part("U", VCA, "V2181L", SOIC8, {"IN": "VIN_" + tag, "EC+": "AGND", "EC-": ec_m, "SYM": "SYM_" + tag,
                                      "OUT": iv, "V+": "+18V", "GND": "AGND", "V-": "VEE_" + tag}, ref=ref)
    d.R("VEE_" + tag, "-18V", "6k19", note="5,1k del datasheet a -15 V riscalato a -18 V (come il master)")
    d.C("+18V", "AGND", "100n")
    d.C("AGND", "-18V", "100n")
    d.part("RV", "Device:R_Potentiometer_Trim", "50k", TRIM, {1: "+15LN", 2: "SW_" + tag, 3: "-15LN"},
           note="trim di simmetria (THD minima)")
    d.R("SW_" + tag, "SYM_" + tag, "150k")
    d.R("SYM_" + tag, "AGND", "51")


def iv(d, node, out, cf="22p C0G"):
    """Resistenza e condensatore dell'I/V (come master-segnale.py: 20k, 22p)."""
    d.R(node, out, "20k 0.1%")
    d.C(node, out, cf)


# ------------------------------------------------------------ shaper e trim di law
def shaper(d, ref, tag, rm, rami, roff=None, tau=None):
    """Shaper a diodi (sistema-shaper §2): pot 0-5 V su POT_tag, rami verso -5 V, Rf 10k.
    Poi lo stadio del partitore x(-1/5) (come master-segnale.py): con 1k/1k la CV al pin = out/10.
    tau: condensatore sul 2k dello stadio del partitore per lo smoothing (fx-module §8.3, 1 ms)."""
    x, sj, out = "POT_" + tag, "SJ_" + tag, "SH_" + tag
    d.R(x, sj, rm + " 0.1%")
    if roff:
        d.R("-REF5", sj, roff + " 0.1%")
    for k, (ra, rb) in enumerate(rami, 1):
        n = "SN%d_%s" % (k, tag)
        d.R(x, n, ra + " 0.1%")
        d.R(n, "-REF5", rb + " 0.1%")
        diode(d, n, sj)
    d.R(sj, out, "10k 0.1%")
    d.R(out, "NP_" + tag, "10k 0.1%")
    d.R("NP_" + tag, "CVP_" + tag, "2k 0.1%", note="stadio del partitore x(-1/5): CV al pin = out/10")
    if tau:
        d.C("NP_" + tag, "CVP_" + tag, tau, "Capacitor_SMD:C_1210_3225Metric",
            note="NOTA: smoothing 1 ms (dec. 80) come C sul 2k: 2k x 470n = 0,94 ms")
    opa2(d, ref, ("AGND", sj, out), ("AGND", "NP_" + tag, "CVP_" + tag), "+15LN", "-15LN",
         note="shaper " + tag)
    d.R(x, "AGND", "100k", note="pot staccato = shaper a 0 V (come il master)")


def law_trim(d, tag, ecl, ecr, rbot="1k 0.1%", nota=""):
    """Partitori di coppia (vca-trim §3.2): L 1,00k/1,00k; R 909 + trimmer 200 ohm / 1,00k + offset.
    rbot: resistenza verso massa (il canale la cambia per la R del dip, vedi canale.py)."""
    cvp = "CVP_" + tag
    d.R(cvp, ecl, "1k 0.1%")
    d.R(ecl, "AGND", rbot, note=nota)
    d.R(cvp, "LT_" + tag, "909 0.1%", note="E96: 909 (doc: 900)")
    d.part("RV", "Device:R_Potentiometer_Trim", "200", TRIM, {1: "LT_" + tag, 2: ecr, 3: ecr},
           note="trim di law, 25 giri (vca-trim §3.2): montato solo se la coppia esce da 0,5 dB")
    d.R(ecr, "AGND", rbot, note=nota)
    d.part("RV", "Device:R_Potentiometer_Trim", "50k", TRIM, {1: "+15LN", 2: "OF_" + tag, 3: "-15LN"},
           note="trim d'offset di coppia")
    d.R("OF_" + tag, ecr, "1M5")


# shaper del fader (sim/shaper/shaper-fader.cir, dec. 126) e del reroute (shaper-reroute.cir)
FADER = ("43.2k", [("68.1k", "357k"), ("20.0k", "38.3k"), ("976", "1.33k")])
REROUTE = ("37.4k", [("43.2k", "1M"), ("18.7k", "40.2k"), ("2.61k", "3.83k")])


# ------------------------------------------------------------ alimentazione
def power_18(d, base=40):
    """+-18 audio (LM317/337 + cap-moltiplicatore, come fx-send.py) e +5VF per la scheda comandi.
    Niente +-15 switch (nessun ADG1434 sulla scheda)."""
    d.power_nets("RAW+27", "RAW-27", "RAW+22", "RAW-22", "+5V", "AGND", "CTRL_GND", "CHASSIS", width=0.8)
    d.power_nets("+5VF", width=0.25)
    d.power_nets("+18V", "-18V", "V27F+", "V27F-", width=0.6)
    for a, b in (("RAW+27", "V27F+"), ("RAW-27", "V27F-"), ("+5V", "+5VF")):
        d.part("FB", "Device:FerriteBead_Small", "ferrite 600R", FB, {1: a, 2: b})
    d.CP("V27F+", "AGND", "220u 35V", CPF)
    d.CP("AGND", "V27F-", "220u 35V", CPF)
    d.CP("+5VF", "CTRL_GND", "47u 10V", "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm")
    d.part("U", "Regulator_Linear:LM317_TO-220", "LM317", "Package_TO_SOT_THT:TO-220-3_Vertical",
           {"VI": "V27F+", "VO": "VREG+", "ADJ": "ADJ+"}, ref="U%d" % base)
    d.R("VREG+", "ADJ+", "120 1%")
    d.R("ADJ+", "AGND", "1k74 1%", note="E96 1,74k = 19,4 V (fx-send NOTE punto 16)")
    d.CP("ADJ+", "AGND", "10u 35V", "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm")
    d.CP("VREG+", "AGND", "47u 35V", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm")
    diode(d, "ADJ+", "VREG+", note="scarica Cadj")
    d.part("D", "Device:D", "S1G", "Diode_SMD:D_SMA", {"K": "V27F+", "A": "VREG+"}, note="protezione inversa")
    d.R("VREG+", "BASE+", "1k", note="NOTA: cap-moltiplicatore come il FX-SEND (~50 mA): da riscalare sulla corrente vera")
    d.CP("BASE+", "AGND", "470u 25V", CPF)
    d.part("Q", "Transistor_BJT:BD139", "BD139", "Package_TO_SOT_THT:TO-126-3_Vertical",
           {"C": "VREG+", "B": "BASE+", "E": "+18V"}, ref="Q%d" % base)
    d.CP("+18V", "AGND", "100u 25V", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm")
    d.part("U", "Regulator_Linear:LM337_TO220", "LM337", "Package_TO_SOT_THT:TO-220-3_Vertical",
           {"VI": "V27F-", "VO": "VREG-", "ADJ": "ADJ-"}, ref="U%d" % (base + 1))
    d.R("VREG-", "ADJ-", "120 1%")
    d.R("ADJ-", "AGND", "1k74 1%")
    d.CP("AGND", "ADJ-", "10u 35V", "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm")
    d.CP("AGND", "VREG-", "47u 35V", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm")
    diode(d, "VREG-", "ADJ-")
    d.part("D", "Device:D", "S1G", "Diode_SMD:D_SMA", {"A": "V27F-", "K": "VREG-"})
    d.R("VREG-", "BASE-", "1k")
    d.CP("AGND", "BASE-", "470u 25V", CPF)
    d.part("Q", "Transistor_BJT:BD140", "BD140", "Package_TO_SOT_THT:TO-126-3_Vertical",
           {"C": "VREG-", "B": "BASE-", "E": "-18V"}, ref="Q%d" % (base + 1))
    d.CP("AGND", "-18V", "100u 25V", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm")


def ref5(d, ref):
    """+-5 V di riferimento per pot e shaper (sistema-shaper §2), come master-segnale.py."""
    d.netclass["+REF5"] = 0.3
    d.netclass["-REF5"] = 0.3
    d.R("+15LN", "REF5K", "1k5", note="NOTA: ~6,7 mA nel riferimento (come il master)")
    d.part("D", "Reference_Voltage:LM4040DBZ-5", "LM4040-5.0", "Package_TO_SOT_SMD:SOT-23",
           {"K": "REF5K", "A": "AGND", "NC": None})
    d.C("REF5K", "AGND", "1u", C12)
    d.R("+REF5", "NREF5I", "10k 0.1%")
    d.R("NREF5I", "-REF5", "10k 0.1%")
    opa2(d, ref, ("REF5K", "+REF5", "+REF5"), ("AGND", "NREF5I", "-REF5"), "+15LN", "-15LN",
         note="+5 e -5 V di riferimento")


# ------------------------------------------------------------ EQ2
def eq2(d, ref, s, vin, vout):
    """EQ2 di fx-send.py, un lato (suffisso s = "_L" / "_R"): LOW Baxandall 120 Hz (pot 10k,
    sim/fx/fx-eq2-pot10k.cir) + HIGH sottrattiva 5,23k/2,49k, 10n (fx-module §6, §8.4).
    Due celle invertenti: l'EQ2 non inverte. Pot sul cavo: NA-NB-NC, VHN-WPH-VHP."""
    d.R(vin, "NA" + s, "324 0.1%")
    d.C("NA" + s, "NB" + s, "180n C0G", C12)
    d.C("NB" + s, "NC" + s, "180n C0G", C12)
    d.R("NC" + s, "VLO" + s, "324 0.1%")
    d.C("VLO" + s, "NHA" + s, "10n C0G", C12)
    d.C("NHA" + s, "NHB" + s, "10n C0G", C12)
    d.R("NHA" + s, "VHP" + s, "5k23 0.1%")
    d.R("NHB" + s, "AGND", "2k49 0.1%", note="sim 2,5k: E96 2,49k")
    d.R("VHP" + s, "NVH" + s, "10k 0.1%")
    d.R("NVH" + s, "VHN" + s, "10k 0.1%")
    d.R("VLO" + s, "NSH" + s, "49k9 0.1%")
    d.R("WPH" + s, "NSH" + s, "49k9 0.1%")
    d.R("NSH" + s, vout, "49k9 0.1%")
    opa4(d, ref, ("AGND", "NB" + s, "VLO" + s), ("NHB" + s, "VHP" + s, "VHP" + s),
         ("AGND", "NVH" + s, "VHN" + s), ("AGND", "NSH" + s, vout),
         note="EQ2: LOW, HIGH follower, HIGH invertente, HIGH somma")


def cavo(d, fili, ref="J2", x=50):
    """Cavo piatto verso la scheda comandi (pot, fader, meter): 2 file, passo 2,54."""
    n = len(fili) // 2
    d.part("J", "Connector_Generic:Conn_02x%02d_Odd_Even" % n, "2x%d cavo piatto" % n,
           "Connector_PinHeader_2.54mm:PinHeader_2x%02d_P2.54mm_Vertical" % n,
           {i + 1: f for i, f in enumerate(fili)}, ref=ref, place=(x, 5, 90),
           note="cavo piatto corto verso la scheda comandi dietro il pannello (dec. 133)")
