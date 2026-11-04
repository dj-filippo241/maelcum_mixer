"""MASTER, schede di USCITA (dec. 142, 143): una per lato, L e R, ognuna col suo C96 di alimentazione.

Uso: python3 master-uscita.py L|R [--solo-schema] [--no-route]

Divisione [C, NOTA, pcb/master/NOTE.md]: le 2 schede d'uscita sono una per lato (L e R), uguali
salvo il mute controller [L] e il relè del REC, che stanno solo sulla L. La R comanda i suoi
relè dalla linea GLOBAL_MUTE (c9) del backplane, che il mute controller della L pilota.

Su ogni scheda (master-out §3.3, §3.4, §3.6, §3.7, ADDENDUM 2026-09-29):
- [F]+[G] 2 stadi d'uscita a bootstrap (dec. 86, v0.3 DEFINITIVA): caldo non invertente, freddo
  invertente, ognuno col suo servo DC (sim/master-out/compB-servo.cir, compB-swing3-env.cir);
- [B3] driver del BOOTH: OPA1612 diretto, caldo a inseguitore e freddo invertente (§3.4);
- clip detector (§3.6): finestra sul caldo, soglia che segue lo statico, tenuta ~0,5 s;
- relè G6K-2F (5 V, 237 ohm) di MASTER e BOOTH, e sulla L quello del REC (§3.7);
- [M] alimentazione: RAW+-26 -> ferrite -> 1000 uF = statici V26F+-; +-18 locali (LM317/337)
  per servo, ricevitore, booth e clip.
Pinout del C96 da pcb/tools/backplane.py; nessun audio sul C96 (dec. 143): l'audio arriva dalla
scheda di segnale sul cavo J2 (stessa piedinatura del suo J2) ed esce verso la schedina dei
connettori sul retro (dec. 141) su J3. Valori [PROVVISORIO].
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from pcbgen import Design
from backplane import c96, SYM_C96, FP_C96

LATO = next((a for a in sys.argv[1:] if a in ("L", "R")), None)
if LATO is None:
    sys.exit("uso: master-uscita.py L|R [--solo-schema] [--no-route]")
s = LATO

d = Design("master-uscita-" + s, os.path.join(HERE, "uscita-" + s),
           "maelcum MASTER scheda di USCITA %s (dec. 142-143) - bozza v0.1" % s, board=(100, 220), rev="0.1-bozza")
d.gnd = "AGND"
d.inner_signal = True
SOIC8 = "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"
C12 = "Capacitor_SMD:C_1206_3216Metric"
R12 = "Resistor_SMD:R_1206_3216Metric"
OPA = "Amplifier_Operational:OPA1612AxD"
TO126 = "Package_TO_SOT_THT:TO-126-3_Vertical"
SOT23 = "Package_TO_SOT_SMD:SOT-23"
DIO = ("Diode:1N4148W", "1N4148W", "Diode_SMD:D_SOD-123")


def opa(ref, a, b, vp="+18V", vm="-18V", note="", decap=True):
    """OPA1612 doppio. a, b = (ingresso +, ingresso -, uscita)."""
    d.part("U", OPA, "OPA1612AIDR", SOIC8, {3: a[0], 2: a[1], 1: a[2], 5: b[0], 6: b[1], 7: b[2],
                                            8: vp, 4: vm}, ref=ref, note=note)
    if decap:
        d.C(vp, "AGND", "100n")
        d.C("AGND", vm, "100n")


def composito(t, freddo, ingresso):
    """Stadio d'uscita a bootstrap (compB-swing3-env.cir + compB-servo.cir). t = etichetta."""
    out, drv, vp, vm = "OUT_" + t, "DRV_" + t, "VP_" + t, "VM_" + t
    inp, inn, sv = "INP_" + t, "INN_" + t, "SV_" + t
    d.netclass[out] = 0.6
    d.power_nets(vp, vm, width=0.4)     # rail flottanti dell'op-amp (PWR_FLAG: li pilotano i pass)
    for n in ("E1_" + t, "E2_" + t):
        d.netclass[n] = 0.4
    # op-amp sui rail che seguono l'uscita. Sezione B: inseguitore di OUT (NOTA: il design
    # dice OPA1612; nessun simbolo OPA1611 in KiCad 10; la sezione B resta dentro i rail flottanti).
    # Niente condensatori fra i rail e OUT: provati e tolti in v0.3c (comb di THD).
    opa({"H": "U11", "C": "U21"}[t], (inp, inn, drv), (out, "UB_" + t, "UB_" + t), vp, vm, decap=False,
        note="composito %s: rail a bootstrap (dec. 86); niente 100n rail-OUT (v0.3c)" % t)
    # bootstrap superiore: CCS a JFET (gate-source a 47 ohm, Id = Idss ~4 mA), pass MJE340, 9 diodi
    d.part("Q", "Transistor_FET:BF245A", "BF245A", "Package_TO_SOT_THT:TO-92_Inline_Wide",
           {"D": "V26F+", "G": "J1S_" + t, "S": "BU_" + t}, note="CCS ~4 mA (NJF245 in sim; Idss da selezionare)")
    d.R("J1S_" + t, "BU_" + t, "47")
    d.part("Q", "Transistor_BJT:BD139", "MJE340", TO126, {"C": "V26F+", "B": "BU_" + t, "E": vp},
           note="pass del rail +: 0,75 W a riposo, rame >= 4 cm2 (v0.3 punto 1); pinout da verificare")
    nodi = ["BU_" + t] + ["S%d_%s" % (k, t) for k in range(1, 9)] + [out]
    for a, k in zip(nodi, nodi[1:]):
        d.part("D", DIO[0], DIO[1], DIO[2], {"A": a, "K": k})
    # bootstrap inferiore
    d.part("Q", "Transistor_FET:BF245A", "BF245A", "Package_TO_SOT_THT:TO-92_Inline_Wide",
           {"D": "NB2_" + t, "G": "J2S_" + t, "S": "V26F-"}, note="CCS ~4 mA")
    d.R("J2S_" + t, "V26F-", "47")
    d.part("Q", "Transistor_BJT:BD140", "MJE350", TO126, {"C": "V26F-", "B": "NB2_" + t, "E": vm},
           note="pass del rail -: 0,75 W a riposo, rame >= 4 cm2; pinout da verificare")
    nodi = [out] + ["T%d_%s" % (k, t) for k in range(1, 9)] + ["NB2_" + t]
    for a, k in zip(nodi, nodi[1:]):
        d.part("D", DIO[0], DIO[1], DIO[2], {"A": a, "K": k})
    # diamond class AB con moltiplicatore di Vbe (Ra 2,2k / Rbm 1k)
    d.part("Q", "Transistor_BJT:BC847", "BC847B", SOT23, {"C": drv, "B": "MID_" + t, "E": "B2_" + t},
           note="moltiplicatore di Vbe (QMULT in sim): vicino a Q1/Q2 per l'inseguimento termico")
    d.R(drv, "MID_" + t, "2k2 1%")
    d.R("MID_" + t, "B2_" + t, "1k 1%")
    d.part("Q", "Transistor_BJT:BD139", "MJE340", TO126, {"C": "V26F+", "B": drv, "E": "E1_" + t},
           note="finale +; corto: 106 mA auto-limitati, 1,0 W medi")
    d.part("Q", "Transistor_BJT:BD140", "MJE350", TO126, {"C": "V26F-", "B": "B2_" + t, "E": "E2_" + t},
           note="finale -")
    d.R("E1_" + t, out, "33 1%", R12)
    d.R("E2_" + t, out, "33 1%", R12)
    # retroazione e servo DC (Test 12): Rf 1k, Rg 1M, iniezione 1M; integratore 220k/15n
    if not freddo:
        d.R(ingresso, inp, "1k 0.1%", note="Rsrc: con Rinj 1M attenua 0,999, Rf/Rg guadagna 1,001")
        d.R(sv, inp, "1M 1%", note="iniezione del servo")
        d.R(out, inn, "1k 0.1%")
        d.R(inn, "AGND", "1M 1%")
    else:
        d.R(ingresso, inn, "1k 0.1%", note="freddo invertente: resistenze appaiate 0,1 % (CMRR ~60 dB)")
        d.R(out, inn, "1k 0.1%")
        d.R(sv, inp, "1M 1%", note="NOTA: servo sul piedino + con partitore 1M/1k (cella dei servo)")
        d.R(inp, "AGND", "1k 0.1%")
    d.part("U", "Amplifier_Operational:TL071", "TL071", SOIC8,
           {"+": "AGND", "-": "SVN_" + t, 6: sv, "V+": "+18V", "V-": "-18V", 1: None, 5: None, 8: None},
           ref={"H": "U12", "C": "U22"}[t], note="servo DC su +-18 statici (FET, Iq bassa: non pesa sul bootstrap)")
    d.C("+18V", "AGND", "100n")
    d.C("AGND", "-18V", "100n")
    d.R(out, "SVN_" + t, "220k 1%")
    d.C("SVN_" + t, sv, "15n C0G", C12, note="fc 0,048 Hz (Test 12)")


# ------------------------------------------------------------ backplane
d.block = "BACKPLANE C96 (classe MASTER-OUT, dec. 143): solo alimentazioni"
a_pins = ["a9", "a10", "a11", "a12"] + ["a%d" % k for k in range(13, 27)]
c_pins = ["c9"]
if s == "L":
    a_pins += ["a5", "a6"]      # RAW+22 per la finestra del supervisore (mute-ctrl.cir)
    c_pins += ["c17"]           # AC_OK
pins = c96({}, a=a_pins, c=c_pins)
d.part("J", SYM_C96, "C96 maschio", FP_C96, pins, ref="J1", place=(50, 213.5, 180),
       note="DIN 41612 C 3x32; classe MASTER-OUT (dec. 143): RAW+-26, +5V, CTRL_GND, c9%s" %
       (", c17, RAW+22" if s == "L" else ""))
for k, x in ((1, 5), (2, 95)):
    d.part("H", "Mechanical:MountingHole_Pad", "CHASSIS", "MountingHole:MountingHole_3.2mm_M3_Pad",
           {1: "CHASSIS"}, ref="H%d" % k, place=(x, 5, 0), note="foro di fissaggio, a CHASSIS")

# ------------------------------------------------------------ alimentazione [M]
d.block = "ALIMENTAZIONE [M]: statici +-26 filtrati, +-18 locali (LM317/337)"
d.power_nets("RAW+26", "RAW-26", "V26F+", "V26F-", "AGND", "CHASSIS", width=0.8)
d.power_nets("+5V", "CTRL_GND", width=0.4)
d.power_nets("+18V", "-18V", width=0.4)
FB = "Inductor_SMD:L_1206_3216Metric"
CPB = "Capacitor_THT:CP_Radial_D12.5mm_P5.00mm"
d.part("FB", "Device:FerriteBead_Small", "ferrite 600R 2A", FB, {1: "RAW+26", 2: "V26F+"})
d.part("FB", "Device:FerriteBead_Small", "ferrite 600R 2A", FB, {1: "RAW-26", 2: "V26F-"})
d.CP("V26F+", "AGND", "1000u 35V", CPB, note="bulk locale [M] (master-out §3.8)")
d.CP("AGND", "V26F-", "1000u 35V", CPB)
d.C("V26F+", "AGND", "100n 50V")
d.C("AGND", "V26F-", "100n 50V")
d.part("U", "Regulator_Linear:LM317_TO-220", "LM317", "Package_TO_SOT_THT:TO-220-3_Vertical",
       {"VI": "V26F+", "VO": "+18V", "ADJ": "ADJ+"}, ref="U40", note="NOTA: +-18 locali, ~30 mA")
d.R("+18V", "ADJ+", "120 1%")
d.R("ADJ+", "AGND", "1k62 1%", note="18,1 V")
d.CP("ADJ+", "AGND", "10u 35V", "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm")
d.CP("+18V", "AGND", "47u 35V", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm")
d.part("D", DIO[0], DIO[1], DIO[2], {"K": "+18V", "A": "ADJ+"}, note="scarica Cadj")
d.part("D", "Device:D", "S1G", "Diode_SMD:D_SMA", {"K": "V26F+", "A": "+18V"}, note="protezione inversa")
d.part("U", "Regulator_Linear:LM337_TO220", "LM337", "Package_TO_SOT_THT:TO-220-3_Vertical",
       {"VI": "V26F-", "VO": "-18V", "ADJ": "ADJ-"}, ref="U41")
d.R("-18V", "ADJ-", "120 1%")
d.R("ADJ-", "AGND", "1k62 1%")
d.CP("AGND", "ADJ-", "10u 35V", "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm")
d.CP("AGND", "-18V", "47u 35V", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm")
d.part("D", DIO[0], DIO[1], DIO[2], {"A": "-18V", "K": "ADJ-"})
d.part("D", "Device:D", "S1G", "Diode_SMD:D_SMA", {"A": "V26F-", "K": "-18V"})

# ------------------------------------------------------------ ricevitore e BOOTH
d.block = "RICEVITORE del MASTER e DRIVER del BOOTH [B3] (OPA1612 diretto, §3.4)"
opa("U1", ("MAST_" + s, "MRX", "MRX"), ("BOOTH_" + s, "BH", "BH"),
    note="NOTA: ricevitore del cavo J2 (il caldo e il freddo caricano 500 ohm); caldo del booth")
d.R("BOOTH_" + s, "BIN", "10k 0.1%")
d.R("BIN", "BC", "10k 0.1%")
opa("U2", ("AGND", "BIN", "BC"), ("AGND", "NU", "NU"), note="freddo del booth; sezione B libera a massa")
d.R("BH", "BOH", "47", note="NOTA: 47 ohm di uscita prima del relè")
d.R("BC", "BOC", "47")

# ------------------------------------------------------------ stadi d'uscita
d.block = "STADIO D'USCITA caldo [F]+[G] (bootstrap, dec. 86)"
composito("H", False, "MRX")
d.block = "STADIO D'USCITA freddo [F]+[G] (bootstrap, invertente)"
composito("C", True, "MRX")

# ------------------------------------------------------------ clip detector (§3.6)
d.side = "B"
d.block = "CLIP detector: finestra sul caldo, soglia 0,86 x statico, tenuta ~0,5 s (NOTA, da simulare)"
# OUT/11 contro V26F+-/12,8: scatta a 0,86 x statico (statico 23,6 V -> 20,3 V; capability 20,4 V).
d.R("OUT_H", "CLD", "100k 0.1%")
d.R("CLD", "AGND", "10k 0.1%")
d.R("V26F+", "CTP", "118k 1%")
d.R("CTP", "AGND", "10k 1%")
d.R("V26F-", "CTN", "118k 1%")
d.R("CTN", "AGND", "10k 1%")
d.R("+5V", "CHALF", "10k 1%")
d.R("CHALF", "CTRL_GND", "10k 1%")
# LM339 su +-18: uscite open collector verso -18, limitate da 4k7 e fermate a ~-0,3 V da BAT54
d.part("U", "Comparator:LM339", "LM339", "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm", {
    7: "CTP", 6: "CLD", 1: "CLX",            # basso se OUT/11 > soglia +
    5: "CLD", 4: "CTN", 2: "CLX",            # basso se OUT/11 < soglia -
    9: "CHALF", 8: "CLAT", 14: "CLO",        # alto (libero) se CLAT < 2,5 V
    11: "AGND", 10: "CTP", 13: None,         # sezione libera
    3: "+18V", 12: "-18V"}, ref="U3", note="NOTA: clip detector (correzione 20 della review)")
d.C("+18V", "AGND", "100n")
d.C("AGND", "-18V", "100n")
d.R("CLX", "CLAT", "4k7")
d.R("+5V", "CLAT", "680k", note="tenuta: 680k x 1u, soglia a meta' = 0,47 s")
d.C("CLAT", "CTRL_GND", "1u", C12)
d.part("D", "Diode:BAT54W", "BAT54W", "Package_TO_SOT_SMD:SOT-323_SC-70", {"A": "CTRL_GND", "K": "CLAT", "NC": None})
d.R("CLO", "CLIP_" + s, "4k7")
d.R("+5V", "CLIP_" + s, "10k", note="NOTA: CLIP alto = LED acceso (clip)")
d.part("D", "Diode:BAT54W", "BAT54W", "Package_TO_SOT_SMD:SOT-323_SC-70", {"A": "CTRL_GND", "K": "CLIP_" + s, "NC": None})

# ------------------------------------------------------------ relè e mute controller
d.side = "F"
d.block = "RELE' di MASTER e BOOTH (G6K-2F, 5 V, 237 ohm; eccitati = suono, failsafe)"
G6K = ("Relay:G6K-2", "G6K-2F DC5", "Relay_SMD:Relay_DPDT_Omron_G6K-2F")
# piedinatura dal datasheet Omron G6K (top view, p. 6): 1 bobina +, 8 bobina -;
# contatto 1: COM 3, NC 2, NO 4; contatto 2: COM 6, NC 7, NO 5
d.part("K", G6K[0], G6K[1], G6K[2], {1: "+5V", 8: "KD", 3: "OUT_H", 4: "XMH", 6: "OUT_C", 5: "XMC",
                                    2: None, 7: None}, note="MASTER %s caldo e freddo" % s)
d.part("K", G6K[0], G6K[1], G6K[2], {1: "+5V", 8: "KD", 3: "BOH", 4: "XBH", 6: "BOC", 5: "XBC",
                                    2: None, 7: None}, note="BOOTH %s caldo e freddo" % s)
if s == "L":
    d.part("K", G6K[0], G6K[1], G6K[2], {1: "+5V", 8: "KD", 3: "REC_L", 4: "XRL", 6: "REC_R", 5: "XRR",
                                        2: None, 7: None}, note="REC L e R [C3]")
d.part("D", DIO[0], DIO[1], DIO[2], {"A": "KD", "K": "+5V"}, note="scarica delle bobine: 1,0 ms (RISULTATI-mute-ctrl)")
d.R("KG0", "KG", "100")
d.part("Q", "Transistor_FET:AO3400A", "AO3400A", SOT23, {"G": "KG", "S": "CTRL_GND", "D": "KD"},
       note="driver dei relè, logic level")
d.netclass["KD"] = 0.4

if s == "L":
    d.block = "MUTE CONTROLLER [L] (mute-ctrl.cir, RISULTATI-mute-ctrl.md)"
    d.R("AC_OK", "+5V", "10k", note="pull-up di AC_OK (open collector dal box)")
    d.R("+5V", "VREF", "1k")
    d.part("U", "Reference_Voltage:TL431DBZ", "TL431", SOT23, {"K": "VREF", "REF": "VREF", "A": "CTRL_GND"}, ref="U5",
           note="2,495 V")
    d.R("RAW+22", "D22", "160k 1%", note="finestra del +22: < 21,2 V = muto")
    d.R("D22", "CTRL_GND", "21k5 1%")
    d.part("U", "Comparator:LM339", "LM339", "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm", {
        7: "AC_OK", 6: "VREF", 1: "ROK",     # S1: AC_OK basso -> RAILS_OK basso
        5: "D22", 4: "VREF", 2: "ROK",       # S2: +22 fuori finestra -> RAILS_OK basso
        9: "CT", 8: "VREF", 14: "KG0",       # S3: timer -> OKD
        11: "CTRL_GND", 10: "VREF", 13: None,
        3: "+5V", 12: "CTRL_GND"}, ref="U4", note="supervisore e timer")
    d.C("+5V", "CTRL_GND", "100n")
    d.R("ROK", "+5V", "10k")
    d.R("ROK", "CT", "1M2 1%", note="RT: accensione 1,61-1,97 s")
    d.C("CT", "CTRL_GND", "2u2 X7R", C12, note="CT +-10 %")
    d.part("D", "Diode:BAT54W", "BAT54W", "Package_TO_SOT_SMD:SOT-323_SC-70", {"A": "CT", "K": "ROK", "NC": None},
           note="scarica CT: riarmo >= 1,5 s")
    d.R("KG0", "+5V", "10k", note="OKD: alto = suona")
    d.part("Q", "Transistor_FET:2N7002", "2N7002", SOT23, {"G": "KG0", "S": "CTRL_GND", "D": "GLOBAL_MUTE"},
           note="c9: basso = suona, alto (pull-up nei moduli) = muto")
else:
    d.block = "COMANDO DEI RELE' dalla GLOBAL_MUTE (c9): basso = suona"
    d.R("GLOBAL_MUTE", "+5V", "100k", note="pull-up come negli altri moduli: master assente = muto")
    d.R("GLOBAL_MUTE", "GMG", "1k")
    d.part("Q", "Transistor_FET:2N7002", "2N7002", SOT23, {"G": "GMG", "S": "CTRL_GND", "D": "KG0"},
           note="inverte c9: c9 alto (muto) -> relè diseccitati")
    d.R("KG0", "+5V", "10k")

# ------------------------------------------------------------ connettori
d.block = "CONNETTORI: J2 dalla scheda di segnale, J3 verso la schedina dei connettori sul retro"
J2 = ["AGND", "MAST_L", "AGND", "MAST_R", "AGND", "BOOTH_L", "AGND", "BOOTH_R", "AGND", "REC_L", "AGND", "REC_R",
      "CLIP_L", "CLIP_R"]
mio = {"MAST_" + s, "BOOTH_" + s, "CLIP_" + s, "AGND"} | ({"REC_L", "REC_R"} if s == "L" else set())
d.part("J", "Connector_Generic:Conn_02x07_Odd_Even", "2x7 cavo piatto",
       "Connector_PinHeader_2.54mm:PinHeader_2x07_P2.54mm_Vertical",
       {i + 1: (n if n in mio else None) for i, n in enumerate(J2)}, ref="J2", place=(72, 5, 90),
       note="cavo piatto dalla scheda di segnale (stessa piedinatura del suo J2)")
J3 = ["AGND", "XMH", "XMC", "AGND", "XBH", "XBC", "AGND", "XRL", "XRR", "AGND"]
d.part("J", "Connector_Generic:Conn_02x05_Odd_Even", "2x5 cavo",
       "Connector_PinHeader_2.54mm:PinHeader_2x05_P2.54mm_Vertical",
       {i + 1: (n if (s == "L" or n not in ("XRL", "XRR")) else None) for i, n in enumerate(J3)},
       ref="J3", place=(30, 5, 90), note="NOTA: verso la schedina XLR/TRS sul retro (dec. 141)")

if s == "L":
    d.part("J", "Connector_Generic:Conn_02x02_Odd_Even", "2x2 cavo",
           "Connector_PinHeader_2.54mm:PinHeader_2x02_P2.54mm_Vertical",
           {1: "+5V", 2: "CTRL_GND", 3: "+5V", 4: "CTRL_GND"}, ref="J4", place=(50, 5, 90),
           note="NOTA: +5V e CTRL_GND verso la scheda comandi (LED, LM3915): non passano dalla scheda di segnale")
# Pin alternati (+5V, CTRL_GND, +5V, CTRL_GND): con due pin vicini della stessa rete Freerouting lasciava
# aperte TUTTA +5V e TUTTA CTRL_GND (giri 1-2; prova sul .dsn del 2026-11-04: alternati = 0 aperti).

d.audio_rules = {
    "sensibili": r"^(INN_[HC]|INP_[HC]|SVN_[HC]|BIN|MRX)$",
    "cavo": r"^(MAST_[LR]|BOOTH_[LR])$",
    "rumorose": r"^(\+5V|CTRL_GND|GLOBAL_MUTE|AC_OK|CLIP_[LR]|RAW.*|V26F[+-]|KD|KG0?|CL[XO]|CLAT)$",
    "regolatori": ["U40", "U41"],
}

if __name__ == "__main__":
    d.build(route="--no-route" not in sys.argv)
