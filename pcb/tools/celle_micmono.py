"""Celle comuni ai moduli MIC e MONO (docs/fase4/mic-mono-moduli.md §5): dal nodo PRE in poi.

I due moduli sono schede separate (dec. 97); qui stanno solo i blocchi che il design doc dice
uguali: EQ2, detector del LED tricolore, driver verso MASTER SUM, 4 mandate con mute globale,
alimentazione. Ogni funzione aggiunge parti al Design che riceve. Valori [PROVVISORIO].
Le scelte non scritte nei documenti sono segnate NOTA e riportate in pcb/mic/NOTE.md.

Pinout verificati sui datasheet:
- LM339 SOIC-14: TI SLCS006 (rev. 2025), figura 5-1 e tabella 5-1, letto il 2026-11-04.
- ADG1434 TSSOP-20: Rev. E tabella 8 (docs/fase1/adg1434-datasheet-verify.md §6).
- V2181 / THAT 2181: tabella 1 (pcb/master/master-segnale.py, sistema-vca-trim.md §2).
- LT3045 / LT3094 MSE-12: Rev. B (pcb/master/master-segnale.py).
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

ADG = boxsym("ADG1434", [
    ("1", "IN1", "input"), ("2", "S1A", "passive"), ("3", "D1", "passive"), ("4", "S1B", "passive"),
    ("5", "VSS", "power_in"), ("6", "GND", "power_in"), ("7", "S2B", "passive"), ("8", "D2", "passive"),
    ("9", "S2A", "passive"), ("10", "IN2", "input")], [
    ("20", "IN4", "input"), ("19", "S4A", "passive"), ("18", "D4", "passive"), ("17", "S4B", "passive"),
    ("16", "VDD", "power_in"), ("15", "NIC", "no_connect"), ("14", "S3B", "passive"), ("13", "D3", "passive"),
    ("12", "S3A", "passive"), ("11", "IN3", "input")],
    fp="Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm",
    desc="Quad SPDT. Pinout TSSOP verificato sul datasheet Rev. E, tabella 8 (2026-10-27)")

VCA = boxsym("V2181", [
    ("1", "IN", "input"), ("2", "EC+", "input"), ("3", "EC-", "input"), ("4", "SYM", "input")], [
    ("8", "OUT", "output"), ("7", "V+", "power_in"), ("6", "GND", "power_in"), ("5", "V-", "passive")],
    fp=SOIC8, desc="VCA singolo. Pinout dal datasheet THAT 2181 tabella 1 (2026-10-28)")

# LM339: comparatore n = (ingresso +, ingresso -, uscita), numerazione di TI tabella 5-1
LM339 = boxsym("LM339", [
    ("7", "1IN+", "input"), ("6", "1IN-", "input"), ("5", "2IN+", "input"), ("4", "2IN-", "input"),
    ("9", "3IN+", "input"), ("8", "3IN-", "input"), ("11", "4IN+", "input"), ("10", "4IN-", "input")], [
    ("1", "1OUT", "open_collector"), ("2", "2OUT", "open_collector"), ("14", "3OUT", "open_collector"),
    ("13", "4OUT", "open_collector"), ("3", "VCC", "power_in"), ("12", "GND", "power_in")],
    fp=SOIC14, desc="Quad comparatore open collector. Pinout TI SLCS006 fig. 5-1, tab. 5-1 (2026-11-04)")


def opa2(d, ref, a, b, vp, vm, note=""):
    """OPA1612 doppio: a, b = (ingresso +, ingresso -, uscita)."""
    d.part("U", OPA1612, "OPA1612AIDR", SOIC8, {3: a[0], 2: a[1], 1: a[2], 5: b[0], 6: b[1], 7: b[2],
                                               8: vp, 4: vm}, ref=ref, note=note)
    d.C(vp, "AGND", "100n")
    d.C("AGND", vm, "100n")


def opa4(d, ref, a, b, c, e, vp, vm, note=""):
    """OPA1654 quad: a, b, c, e = (ingresso +, ingresso -, uscita) delle sezioni A-D."""
    d.part("U", OPA1654, "OPA1654AIDR", SOIC14, {
        3: a[0], 2: a[1], 1: a[2], 5: b[0], 6: b[1], 7: b[2],
        10: c[0], 9: c[1], 8: c[2], 12: e[0], 13: e[1], 14: e[2],
        4: vp, 11: vm}, ref=ref, note=note)
    d.C(vp, "AGND", "100n")
    d.C("AGND", vm, "100n")


def diode(d, a, k, note=""):
    return d.part("D", DIODE, "1N4148W", SOD123, {"A": a, "K": k}, note=note)


# ------------------------------------------------------------ backplane
def backplane(d, msum):
    """Classe MIC/GEN (sistema-backplane §4): slot 1 = MSUM6 o MSUM7, slot 2-5 = S1-S4_OUT."""
    from backplane import c96, SYM_C96, FP_C96, C96_DAL_BORDO
    b = {"b1": msum + "_L", "b2": msum + "_R"}
    for k in range(1, 5):
        b["b%d" % (3 * k + 1)] = "S%d_OUT_L" % k
        b["b%d" % (3 * k + 2)] = "S%d_OUT_R" % k
    for s in range(1, 11):
        b["b%d" % (3 * s)] = "AGND"
    d.part("J", SYM_C96, "C96 maschio", FP_C96, c96(b, c=["c9"]), ref="J1", place=(50, 220 - C96_DAL_BORDO, 180),
           note="DIN 41612 C 3x32, angolo retto")
    for ref, x in (("H1", 5), ("H2", 95)):
        d.part("H", "Mechanical:MountingHole_Pad", "CHASSIS", "MountingHole:MountingHole_3.2mm_M3_Pad",
               {1: "CHASSIS"}, ref=ref, place=(x, 5, 0), note="foro di fissaggio al pannello, a CHASSIS")


# ------------------------------------------------------------ alimentazione
def _sub(d, blocco, nome):
    """Con blocco (stringa) ogni regolatore fa un blocco suo coi suoi condensatori: il
    piazzamento li tiene vicini (A1 del controllo audio, todo 248). Senza: niente cambia."""
    if blocco:
        d.block = "%s: %s" % (blocco, nome)


def power_18_sw(d, base=40, blocco=None):
    """+-18 audio (LM317/337 + cap-moltiplicatore, come fx-send.py), +-15 switch (78L15/79L15), +5VF.
    blocco: vedi _sub (default None = un blocco solo, quello già scritto dal modulo)."""
    d.power_nets("RAW+27", "RAW-27", "RAW+22", "RAW-22", "+5V", "AGND", "CTRL_GND", "CHASSIS", width=0.8)
    d.power_nets("+15SW", "-15SW", "+5VF", width=0.25)
    d.power_nets("+18V", "-18V", "V27F+", "V27F-", "V22F+", "V22F-", width=0.6)
    # con blocco, ogni ferrite va col suo regolatore: il blocco ha un pin del C96 e si piazza
    # vicino al connettore, non al centro della scheda (todo 248)
    sub = {"V27F+": "+18V (LM317 + BD139)", "V27F-": "-18V (LM337 + BD140)",
           "V22F+": "+15SW (78L15)", "V22F-": "-15SW (79L15)", "+5VF": "+5VF"}
    for a, b in (("RAW+27", "V27F+"), ("RAW-27", "V27F-"), ("RAW+22", "V22F+"), ("RAW-22", "V22F-"), ("+5V", "+5VF")):
        _sub(d, blocco, sub[b])
        d.part("FB", "Device:FerriteBead_Small", "ferrite 600R", FB, {1: a, 2: b})
    _sub(d, blocco, "+18V (LM317 + BD139)")
    d.CP("V27F+", "AGND", "220u 35V", CPF)
    _sub(d, blocco, "-18V (LM337 + BD140)")
    d.CP("AGND", "V27F-", "220u 35V", CPF)
    _sub(d, blocco, "+5VF")
    d.CP("+5VF", "CTRL_GND", "47u 10V", "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm")
    _sub(d, blocco, "+18V (LM317 + BD139)")
    d.part("U", "Regulator_Linear:LM317_TO-220", "LM317", "Package_TO_SOT_THT:TO-220-3_Vertical",
           {"VI": "V27F+", "VO": "VREG+", "ADJ": "ADJ+"}, ref="U%d" % base)
    d.R("VREG+", "ADJ+", "120 1%")
    d.R("ADJ+", "AGND", "1k74 1%", note="E96 1,74k = 19,4 V (fx-send NOTE punto 16)")
    d.CP("ADJ+", "AGND", "10u 35V", "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm")
    d.CP("VREG+", "AGND", "47u 35V", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm")
    diode(d, "ADJ+", "VREG+", note="scarica Cadj")
    d.part("D", "Device:D", "S1G", "Diode_SMD:D_SMA", {"K": "V27F+", "A": "VREG+"}, note="protezione inversa")
    d.R("VREG+", "BASE+", "1k", note="NOTA: cap-moltiplicatore come il FX-SEND (~50 mA)")
    d.CP("BASE+", "AGND", "470u 25V", CPF)
    d.part("Q", "Transistor_BJT:BD139", "BD139", "Package_TO_SOT_THT:TO-126-3_Vertical",
           {"C": "VREG+", "B": "BASE+", "E": "+18V"}, ref="Q%d" % base)
    d.CP("+18V", "AGND", "100u 25V", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm")
    _sub(d, blocco, "-18V (LM337 + BD140)")
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
    _sub(d, blocco, "+15SW (78L15)")
    d.part("U", "Regulator_Linear:L78L15_SOT89", "78L15", "Package_TO_SOT_SMD:SOT-89-3",
           {"IN": "V22F+", "GND": "AGND", "OUT": "+15SW"}, ref="U%d" % (base + 2))
    _sub(d, blocco, "-15SW (79L15)")
    d.part("U", "Regulator_Linear:L79L15_SOT89", "79L15", "Package_TO_SOT_SMD:SOT-89-3",
           {"VI": "V22F-", "GND": "AGND", "VO": "-15SW"}, ref="U%d" % (base + 3))
    _sub(d, blocco, "+15SW (78L15)")
    d.C("V22F+", "AGND", "1u 50V", C12)
    _sub(d, blocco, "-15SW (79L15)")
    d.C("AGND", "V22F-", "1u 50V", C12)
    _sub(d, blocco, "+15SW (78L15)")
    d.C("+15SW", "AGND", "1u 25V", C12)
    _sub(d, blocco, "-15SW (79L15)")
    d.C("AGND", "-15SW", "1u 25V", C12)


def power_ln(d, base=44, blocco=None):
    """+-15 LN dal +-18 (LT3045 / LT3094, come master-segnale.py). Il design doc dice «da raw
    +-22», ma LT3045 e LT3094 reggono 20 V in ingresso: NOTA, si parte dal +-18."""
    d.power_nets("+15LN", "-15LN", width=0.6)
    MSE = "Package_SO:MSOP-12-1EP_3x4.039mm_P0.65mm_EP1.651x2.845mm"
    _sub(d, blocco, "+15LN (LT3045)")
    d.part("U", "Regulator_Linear:LT3045xMSE", "LT3045EMSE", MSE, {
        1: "+18V", 2: "+18V", 3: "+18V", 4: "+18V", 5: None, 6: "AGND", 7: "+18V", 8: "SETP",
        9: "AGND", 10: "+15LN", 11: "+15LN", 12: "+15LN", 13: "AGND"}, ref="U%d" % base,
        note="EN/UV a IN; ILIM a massa; PG libero; PGFB a IN (come master-segnale.py)")
    d.netclass["SETP"] = 0.3
    d.netclass["SETN"] = 0.3
    d.R("SETP", "AGND", "150k 0.1%")
    d.C("SETP", "AGND", "4u7 25V", C12, note="rumore del riferimento (datasheet: 4,7 uF)")
    d.C("+18V", "AGND", "4u7 25V", C12)
    d.C("+15LN", "AGND", "10u 25V", C12)
    _sub(d, blocco, "-15LN (LT3094)")
    d.part("U", "Regulator_Linear:LT3094xMSE", "LT3094EMSE", MSE, {
        1: "-18V", 2: "-18V", 13: "-18V", 3: "-18V", 4: None, 5: "-18V", 6: "AGND", 7: None, 8: "SETN",
        9: "AGND", 10: "-15LN", 11: "-15LN", 12: "-15LN"}, ref="U%d" % (base + 1),
        note="EN/UV a IN; PG libero; PGFB a IN; ILIM a massa; VIOC libero")
    d.R("SETN", "AGND", "150k 0.1%")
    d.C("AGND", "SETN", "4u7 25V", C12)
    d.C("AGND", "-18V", "4u7 25V", C12)
    d.C("AGND", "-15LN", "10u 25V", C12)


# ------------------------------------------------------------ EQ2
def eq2(d, ref, vin, vout):
    """EQ2 come fx-send.py, un lato solo: LOW Baxandall 120 Hz (pot 10k, sim/fx/fx-eq2-pot10k.cir)
    + HIGH sottrattiva. Due celle invertenti: l'EQ2 non inverte. Pot sul cavo: NA-NB-NC, VHN-WPH-VHP."""
    d.R(vin, "NA", "324 0.1%")
    d.C("NA", "NB", "180n C0G", C12)
    d.C("NB", "NC", "180n C0G", C12)
    d.R("NC", "VLO", "324 0.1%")
    d.C("VLO", "NHA", "10n C0G", C12)
    d.C("NHA", "NHB", "10n C0G", C12)
    d.R("NHA", "VHP", "4k75 0.1%", note="NOTA: mic-mono §5.1 dice 4,7k/2,25k (~5 kHz); backend.inc 5,23k/2,5k")
    d.R("NHB", "AGND", "2k26 0.1%", note="E96 di 2,25k")
    d.R("VHP", "NVH", "10k 0.1%")
    d.R("NVH", "VHN", "10k 0.1%")
    d.R("VLO", "NSH", "49k9 0.1%")
    d.R("WPH", "NSH", "49k9 0.1%")
    d.R("NSH", vout, "49k9 0.1%")
    opa4(d, ref, ("AGND", "NB", "VLO"), ("NHB", "VHP", "VHP"), ("AGND", "NVH", "VHN"), ("AGND", "NSH", vout),
         "+18V", "-18V", note="EQ2: LOW, HIGH follower, HIGH invertente, HIGH somma")


# ------------------------------------------------------------ detector e LED
def detector(d, pre):
    """Partitore g = 0,199 e superdiodo come master-segnale.py (meter-det-03s.cir): HOLD 100n,
    release 3M (0,3 s). Ritorna le due sezioni op-amp da mettere in un quad: (superdiodo, buffer).
    NOTA: g = 0,199 tiene MET <= 3,3 V col PRE in clip (16,5 Vp), dentro il modo comune del
    LM339 a +5 V (0 ... Vcc - 1,5 V)."""
    d.R(pre, "MG", "10k 0.1%")
    d.R("MG", "AGND", "2k49 0.1%")
    d.R("DOUT", "D1A", "1k")
    diode(d, "D1A", "HOLD")
    d.C("DOUT", "HOLD", "47p C0G")
    d.C("HOLD", "AGND", "100n C0G", C12, note="hold: niente altro sul nodo (sim/meter)")
    d.R("HOLD", "AGND", "3M", note="release 0,3 s (dec. 81)")
    return ("MG", "HOLD", "DOUT"), ("HOLD", "MET", "MET")


def led3(d, rail, rtop):
    """LED tricolore (dec. 97): verde >= -6, giallo >= +11, rosso >= +17 dBu al PRE, rosso con
    latch ~0,5 s. LED bicolore ad anodo comune (+5VF), giallo = verde + rosso. NOTA (logica):
      C1: MET > VR -> scarica LT (1u, 750k verso +5VF): latch, 0,52 s fino a VTL = 2,5 V
      C2: LT < VTL -> LQ basso = rosso tenuto (diodo dal catodo rosso) e verde spento (2N7002)
      C3: MET > VY -> catodo rosso: giallo (col verde) o rosso
      C4: MET > VG -> catodo verde, attraverso il 2N7002 comandato da LQ
    Soglie da partitore sul rail analogico (rtop verso VR): si tarano cambiando una resistenza."""
    d.R(rail, "VR", rtop + " 0.1%")
    d.R("VR", "VY", "7k68 0.1%")
    d.R("VY", "VG", "6k65 0.1%")
    d.R("VG", "AGND", "1k1 0.1%")
    for n in ("VR", "VY", "VG"):
        d.C(n, "AGND", "100n")
    d.R("+5VF", "VTL", "10k")
    d.R("VTL", "CTRL_GND", "10k")
    d.C("VTL", "CTRL_GND", "100n")
    d.R("+5VF", "LT", "750k", note="latch del rosso: 0,69 x 750k x 1u = 0,52 s")
    d.C("LT", "CTRL_GND", "1u 25V", C12)
    d.R("+5VF", "LQ", "10k")
    d.part("U", LM339, "LM339DR", SOIC14, {
        "1IN+": "VR", "1IN-": "MET", "1OUT": "LT",
        "2IN+": "LT", "2IN-": "VTL", "2OUT": "LQ",
        "3IN+": "VY", "3IN-": "MET", "3OUT": "KR",
        "4IN+": "VG", "4IN-": "MET", "4OUT": "KG",
        "VCC": "+5VF", "GND": "CTRL_GND"}, ref="U30",
        note="NOTA: GND a CTRL_GND (correnti dei LED fuori da AGND); ingressi riferiti ad AGND")
    d.C("+5VF", "CTRL_GND", "100n")
    diode(d, "KR", "LQ", note="rosso acceso durante il latch")
    d.part("Q", "Transistor_FET:2N7002", "2N7002", "Package_TO_SOT_SMD:SOT-23",
           {"D": "GFD", "S": "KG", "G": "LQ"}, note="spegne il verde durante il latch del rosso")
    d.R("LKR", "KR", "1k", note="~2,8 mA nel rosso (LED alta efficienza, metering §1)")
    d.R("LKG", "GFD", "1k", note="~2,8 mA nel verde")


# ------------------------------------------------------------ uscite
def msum_drivers(d, ref, post, msum):
    """REV todo 227 (sistema-polarita F2): due driver invertenti unity 20k/20k 0,1 %, poi la R di
    somma 20k lato sorgente sul net multidrop MSUM6/MSUM7 (master [A2]: Rf 20k)."""
    for s in ("L", "R"):
        d.R(post, "NDR_" + s, "20k 0.1%")
        d.R("NDR_" + s, "DRV_" + s, "20k 0.1%")
        d.C("NDR_" + s, "DRV_" + s, "10p C0G", note="NOTA: Cf come i ricevitori a massa virtuale")
        d.R("DRV_" + s, "%s_%s" % (msum, s), "20k 0.1%", note="R di somma lato sorgente (dec. 97)")
    opa2(d, ref, ("AGND", "NDR_L", "DRV_L"), ("AGND", "NDR_R", "DRV_R"), "+18V", "-18V",
         note="driver MSUM invertenti (F2)")


def sends(d, ref_adg, ref_inj):
    """4 pot SEND (sul cavo: AGND - SWk - POST), mute globale ADG1434 e 4 buffer d'iniezione con
    due R 10k (L e R) sul net del bus. NOTA: 2k2 in serie fra cursore e ADG: il nodo del cursore
    può superare i +-15 V dello switch (MONO fino a +23 dBu); la 2k2 limita la corrente nei diodi
    di protezione a ~1 mA. Mute = SxB a massa: -53 dB col pot tutto aperto."""
    p = {"VDD": "+15SW", "VSS": "-15SW", "GND": "AGND", "NIC": None}
    for k in range(1, 5):
        d.R("SW%d" % k, "SIN%d" % k, "2k2")
        p["IN%d" % k] = "SMUTE_N"
        p["S%dA" % k] = "SIN%d" % k     # A = IN alto = suona (datasheet tabella 9)
        p["D%d" % k] = "SIN%d" % k
        p["S%dB" % k] = "AGND"
    d.part("U", ADG, "ADG1434YRUZ", "Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm", p, ref=ref_adg,
           note="mute globale delle mandate (dec. 94b): D e SxA sul nodo, SxB a massa")
    d.C("+15SW", "AGND", "100n")
    d.C("AGND", "-15SW", "100n")
    d.R("+5VF", "SMUTE_N", "10k", note="IN alto = suona (VIH 2,0 V)")
    d.part("Q", "Transistor_FET:2N7002", "2N7002", "Package_TO_SOT_SMD:SOT-23",
           {"D": "SMUTE_N", "S": "CTRL_GND", "G": "MUTE_G"}, note="GLOBAL_MUTE alto = muto")
    d.R("GLOBAL_MUTE", "MUTE_G", "1k")
    d.R("MUTE_G", "+5VF", "100k", note="senza master il modulo resta muto (fail-safe, fx-send NOTE 5)")
    opa4(d, ref_inj, *[("SIN%d" % k, "INJ%d" % k, "INJ%d" % k) for k in range(1, 5)], "+18V", "-18V",
         note="buffer d'iniezione, non invertenti")
    for k in range(1, 5):
        d.R("INJ%d" % k, "S%d_OUT_L" % k, "10k 0.1%")
        d.R("INJ%d" % k, "S%d_OUT_R" % k, "10k 0.1%")


def cavo(d, fili, ref="J2"):
    """Cavo piatto verso la scheda comandi (pot, LED, tasto): 2 file, passo 2,54."""
    n = len(fili) // 2
    d.part("J", "Connector_Generic:Conn_02x%02d_Odd_Even" % n, "2x%d cavo piatto" % n,
           "Connector_PinHeader_2.54mm:PinHeader_2x%02d_P2.54mm_Vertical" % n,
           {i + 1: f for i, f in enumerate(fili)}, ref=ref, place=(50, 5, 90),
           note="cavo piatto corto (<= 10 cm) verso la scheda comandi dietro il pannello (dec. 133)")


# ------------------------------------------------------------ scheda comandi
POT1_FP = "Potentiometer_THT:Potentiometer_Alps_RK09L_Single_Vertical"
POT1 = boxsym("POT_SINGLE", [
    ("1", "CCW", "passive"), ("2", "W", "passive"), ("3", "CW", "passive"), ("MP", "MP", "passive")], [],
    ref="RV", fp=POT1_FP,
    desc="Pot singolo, Alps RK09L verticale; 1 = antiorario, 2 = cursore, 3 = orario (catalogo Alps "
         "RK09L rev. 2510, come pcb/fx-send/NOTE.md punto 10); MP = staffe, a telaio attraverso il pannello")
LED_FP = "LED_THT:LED_D3.0mm-3"
LED2 = boxsym("LED_BICOLORE_CA", [("1", "K_VERDE", "passive"), ("2", "A", "passive")],
              [("3", "K_ROSSO", "passive")], ref="D", fp=LED_FP,
              desc="LED bicolore verde/rosso 3 mm ad anodo comune. NOTA: pezzo non scelto, pinout "
                   "da verificare sul suo datasheet")
SW_FP = "Button_Switch_THT:SW_PUSH_6mm"
SW = boxsym("TASTO", [("1", "1", "passive")], [("2", "2", "passive")], ref="SW", fp=SW_FP,
            desc="Tasto MUTE. NOTA: impronta di un tasto 6 mm; ritenuta o momentaneo da decidere (voce 40)")


def scheda_comandi(here, modulo, titolo, cavo, reti, tasto=None):
    """Scheda comandi dietro il pannello, come pcb/fx-send/fx-send-comandi.py: pot, LED e tasto
    alle posizioni di docs/pannelli/coordinate.json, cavo piatto J1 in alto (stesso ordine di J2).
    reti = {nome manopola: (antiorario, cursore, orario, valore, nota)}; tasto = (rete a, rete b).
    Le reti del cavo che la scheda comandi non usa restano libere (no-connect)."""
    import json, os
    from pcbgen import Design
    root = os.path.join(here, "..", "..")
    pan = json.load(open(os.path.join(root, "docs", "pannelli", "coordinate.json")))["moduli"][modulo]
    mx, my = 1.0, 2.0                       # scheda più piccola del pannello: 1 mm per lato, 2 sopra e sotto
    w, h = pan["larghezza"] - 2 * mx, pan["altezza"] - 2 * my
    d = Design(modulo + "-comandi", os.path.join(here, "comandi"), titolo, board=(w, h), rev="0.1-bozza")
    d.gnd = "AGND"
    d.power_nets("AGND", width=0.5)
    usate = set()
    d.block = "COMANDI (posizioni dal render del pannello)"
    for c in pan["comandi"]:
        x, y = c["x"] - mx, c["y"] - my
        if c["tipo"] == "manopola":
            ccw, wi, cw, val, nota = reti[c["nome"]]
            usate.update((ccw, wi, cw))
            # i pin stanno 7,5 mm a sinistra dell'albero: nella colonna di sinistra il pot si gira,
            # così i pin vanno verso il centro e non sul bordo
            d.part("RV", POT1, val, POT1_FP, {"1": ccw, "2": wi, "3": cw}, anchor=(7.5, 2.5),
                   place=(x, y, 180 if x < w / 2 else 0),
                   note="%s; manopola %s, pot di classe %s mm (RK09L: KiCad non ha l'RK14)" % (nota, c["nome"], c["pot"]))
        elif c["tipo"] == "led3":
            usate.update(("+5VF", "LKG", "LKR"))
            d.part("D", LED2, "LED bicolore VR 3 mm", LED_FP, {"1": "LKG", "2": "+5VF", "3": "LKR"},
                   anchor=(2.54, 0), place=(x, y, 0),
                   note="NOTA: un LED bicolore al centro (giallo = verde + rosso, celle_micmono.led3); "
                        "il render del pannello mostra tre punti a passo 4 mm")
        elif c["tipo"] == "bottone" and tasto:
            usate.update(tasto)
            d.part("SW", SW, "tasto " + c["nome"], SW_FP, {"1": tasto[0], "2": tasto[1]},
                   anchor=(3.25, 2.25), place=(x, y, 0), note="NOTA: tasto a ritenuta fra +5VF e MUTE_SW")
    d.block = "CAVO VERSO LA SCHEDA PRINCIPALE"
    n = len(cavo) // 2
    d.part("J", "Connector_Generic:Conn_02x%02d_Odd_Even" % n, "2x%d cavo piatto" % n,
           "Connector_PinHeader_2.54mm:PinHeader_2x%02d_P2.54mm_Vertical" % n,
           {i + 1: (f if f in usate or f == "AGND" else None) for i, f in enumerate(cavo)},
           ref="J1", place=(w / 2, 9.0, 90), note="stesso ordine di J2 sulla scheda principale (cavo.py)")
    return d
