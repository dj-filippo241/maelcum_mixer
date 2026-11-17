"""FILTRO (v0.2, dec. 159): due schede di segnale, una per sezione. HPF = parte 1 (fila 1 della
colonna FILTRO), LPF = parte 2 (fila 2). Ogni scheda porta il core stereo della sua sezione (L, R),
la CV di frequenza, la RES, l'overdrive col DRIVE a pot doppio, il muto e l'uscita sul DJ bus.
Bozza v0.1.

Uso: python3 filtro.py HPF|LPF [--solo-schema] [--no-route]

Catena per lato (docs/fase2/filter-module.md §2bis, §5quater, §5ter):
  BUS_<S> (net multidrop dai canali) -> ricevitore a massa virtuale Rf 10k, Cf 10p (inverte)
  -> CORE (a') a 4 poli, k 1/30 (partitore 2,87k/100), C 1,1 nF (d5c-sum-pass*.cir, d5b-4p-chain.cir):
     sezione 1 Q 0,541 fissa, sezione 2 Q 1,307 con RES (OTA P e N) e limitatore 4,7k + 2+2 diodi
  -> OVERDRIVE v0.2 col pot doppio sul segnale (od2-pot-tran.cir) + servo DC (od2-servo-dc.cir):
     y = -(x + m d), uscita invertita (sistema-polarita F1)
  -> MUTO (ADG1434): la sezione tace se nessun canale la sceglie (bit FILT_MODE, §2bis)
  -> driver non invertente -> 10k -> <S>_OUT (il backplane lo porta sul DJ bus)
CV:
  FREQ: buffer del pot -> shaper (sistema-shaper §3, dec. 102 / 137) -> offset e partitore con
     tempco -> 4 converter esponenziali THAT 320 + LM334 PTAT (RISULTATI-conv-that320.md)
  RES: shaper gpos (manopola rovescia) e raddrizzatore gneg (shaper-res.cir, dec. 153) ->
     4 sorgenti op-amp + PNP verso gli OTA P e N (§5 «RES dec. 153»)

Polarita' (sistema-polarita.md F1): ricevitore -1, core +1 (due sezioni invertenti), overdrive -1,
driver +1: dal bus a <S>_OUT +1, come un canale verso il DJ bus.
Valori [PROVVISORIO]. Le scelte non scritte nei documenti sono segnate NOTA (pcb/filtro/NOTE.md).
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
sys.path.insert(0, os.path.join(HERE, "..", "five-way"))
from pcbgen import DesignRiprova, boxsym
from backplane import c96, SYM_C96, FP_C96, C96_DAL_BORDO
import celle_vca as cv
from celle_vca import C12, SOIC8, TRIM
from celle_micmono import power_18_sw, power_ln, ADG
from comune_5w import Parti

S = next((a for a in sys.argv[1:] if a in ("HPF", "LPF")), None)
if S is None:
    sys.exit("uso: filtro.py HPF|LPF [--solo-schema] [--no-route]")
HP = S == "HPF"
# PIANO-SCHEDE-F: parte 1 fila 1 (149 x 166), parte 2 fila 2 (151 x 164)
L, H = (149, 166) if HP else (151, 164)

d = DesignRiprova("filtro-" + S, os.path.join(HERE, S),
                  "maelcum FILTRO scheda di segnale %s: core a' 4 poli, CV, RES, overdrive, muto (v0.2) - bozza v0.1" % S,
                  board=(L, H), rev="0.1-bozza")
d.gnd = "AGND"
d.inner_signal = True
d.link_pairs = True
d.link_pairs_masse = True
d.cluster_fuori = True
d.route_tries = 10  # HPF: 6 tentativi, migliore 1 aperto; LPF: migliore 2 (aperti casuali, -15LN e U9)
d.fanout_more = True   # HPF giro 1: 28 pad di massa senza via -> isola di colata

SOIC16 = "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm"
SOIC14 = "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm"
SOT23 = "Package_TO_SOT_SMD:SOT-23"
CNP = "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm"

# Pinout: TI SNOSBW2F (rev. nov 2015) §5, figura «D or NFG Package» e Pin Functions. Diodi
# linearizzanti e buffer Darlington non usati (buffer op-amp esterni, filter-module §3). Uscite
# «passive»: sono uscite in corrente, le due della RES vanno sullo stesso nodo.
OTA = boxsym("LM13700", [("3", "INP_A", "input"), ("4", "INN_A", "input"), ("1", "IABC_A", "input"),
                         ("2", "DIODE_A", "no_connect"), ("7", "BUFIN_A", "no_connect"), ("8", "BUFOUT_A", "no_connect"),
                         ("11", "V+", "power_in")],
             [("14", "INP_B", "input"), ("13", "INN_B", "input"), ("16", "IABC_B", "input"),
              ("15", "DIODE_B", "no_connect"), ("10", "BUFIN_B", "no_connect"), ("9", "BUFOUT_B", "no_connect"),
              ("5", "OUT_A", "passive"), ("12", "OUT_B", "passive"), ("6", "V-", "power_in")],
             fp=SOIC16, desc="OTA doppio. Pinout TI SNOSBW2F rev. nov 2015, §5 (2026-11-16)")
# Pinout: THAT Corporation Doc 600041 Rev 04, Figure 2 «320 Pinout» (2026-11-16): Q1 C1 B2 E3,
# Q2 C14 B13 E12, Q3 E5 B6 C7, Q4 E10 B9 C8, SUB 4 e 11 (a massa: «ac-grounded», p. 1).
THAT320 = boxsym("THAT320", [("1", "C1", "passive"), ("2", "B1", "passive"), ("3", "E1", "passive"),
                             ("5", "E3", "passive"), ("6", "B3", "passive"), ("7", "C3", "passive"), ("4", "SUB", "passive")],
                 [("14", "C2", "passive"), ("13", "B2", "passive"), ("12", "E2", "passive"),
                  ("10", "E4", "no_connect"), ("9", "B4", "no_connect"), ("8", "C4", "no_connect"), ("11", "SUB2", "passive")],
                 ref="Q", fp=SOIC14, desc="4 PNP appaiati THAT 320S14-U. Pinout THAT Doc 600041 Rev 04, Figure 2")
# Pinout: TI SNVS746E (rev. maggio 2013), Figure 2 «SOIC-8 Alternative Pinout» (LM334SM): un pin
# per funzione (la Figure 1 ha V- su quattro pin vicini, che Freerouting non collega).
LM334 = boxsym("LM334SM", [("3", "V+", "passive"), ("2", "R", "passive"), ("1", "V-", "passive")],
               [("4", "NC1", "no_connect"), ("5", "NC2", "no_connect"), ("6", "NC3", "no_connect"),
                ("7", "NC4", "no_connect"), ("8", "NC5", "no_connect")],
               fp=SOIC8, desc="Sorgente di corrente PTAT. Pinout TI SNVS746E Figure 2 (LM334SM)")
# Pinout: onsemi MMBT3906LT1/D Rev. 15, SOT-23 case 318 style 6: 1 B, 2 E, 3 C.
PNP = boxsym("MMBT3906", [("1", "B", "passive"), ("2", "E", "passive")], [("3", "C", "passive")],
             ref="Q", fp=SOT23, desc="PNP. Pinout onsemi MMBT3906LT1/D Rev. 15, style 6")

pz = Parti(d)
uref, Cx = pz.uref, pz.Cx
SIDES = ("L", "R")


def opa2(a, b, note="", value="OPA1612AIDR", vp="+18V", vm="-18V"):
    cv.opa2(d, uref(), a, b, vp, vm, note=note, value=value)


def diode(a, k, note=""):
    cv.diode(d, a, k, note=note)


def trim(a, b, val, note=""):
    """Trimmer come resistenza variabile: capo 1 su a, cursore e capo 3 su b."""
    d.part("RV", "Device:R_Potentiometer_Trim", val, TRIM, {1: a, 2: b, 3: b}, note=note)


# ------------------------------------------------------------ backplane
d.block = "BACKPLANE C96 (classe FILTRO, sistema-backplane §4, dec. 159)"
if HP:
    b = {"b1": "BUS_HPF_L", "b2": "BUS_HPF_R", "b7": "HPF_OUT_L", "b8": "HPF_OUT_R"}
    bit, cpin = 0, ["c1", "c3", "c5", "c7"]
else:
    b = {"b4": "BUS_LPF_L", "b5": "BUS_LPF_R", "b10": "LPF_OUT_L", "b11": "LPF_OUT_R"}
    bit, cpin = 1, ["c2", "c4", "c6", "c8"]
for k in range(1, 11):
    b["b%d" % (3 * k)] = "AGND"
d.part("J", SYM_C96, "C96 maschio", FP_C96, c96(b, c=cpin), ref="J1", place=(L / 2, H - C96_DAL_BORDO, 180),
       note="DIN 41612 C 3x32, angolo retto; sezione %s del filtro" % S)
for ref, x in (("H1", 5), ("H2", L / 2), ("H3", L - 5)):
    d.part("H", "Mechanical:MountingHole_Pad", "CHASSIS", "MountingHole:MountingHole_3.2mm_M3_Pad",
           {1: "CHASSIS"}, ref=ref, place=(x, 5, 0), note="foro di fissaggio, a CHASSIS")

d.block = "ALIMENTAZIONE +-18 audio, +-15 switch, +5, +-15 LN (core e CV), +-5 riferimento"
power_18_sw(d, base=140)
power_ln(d, base=144)
cv.ref5(d, "U146")
d.power_nets("+18V", "-18V", width=0.4)
d.netclass["CTRL_GND"] = 0.3

# ------------------------------------------------------------ CV di frequenza
d.block = "FREQ: buffer del pot, shaper (sistema-shaper §3), offset, partitore tempco (RISULTATI-conv-that320)"
PF = pz.Pack("+15LN", "-15LN")
d.R("FW", "AGND", "100k", note="pot staccato = inizio corsa")
PF.add(("FW", "VXF", "VXF"))
if HP:   # dec. 137: senza ramo basso
    d.R("VXF", "VGF", "9k53 0.1%", note="shaper-filtro-freq-hpf.cir")
    d.R("VXF", "NHF", "17k8 0.1%")
    d.R("NHF", "-REF5", "21k5 0.1%")
    diode("NHF", "VGF")
else:    # dec. 102
    d.R("VXF", "VGF", "9k09 0.1%", note="shaper-filtro-freq.cir")
    d.R("VXF", "NHF", "20k 0.1%")
    d.R("NHF", "-REF5", "24k3 0.1%")
    diode("NHF", "VGF")
    d.R("VXF", "NLF", "11k3 0.1%")
    d.R("NLF", "-REF5", "80k6 0.1%")
    diode("VGF", "NLF", note="ramo basso: diodo rovesciato (sistema-shaper §3)")
d.R("VGF", "SHF", "10k 0.1%")
PF.add(("AGND", "VGF", "SHF"))
# w = -(sh + 5,40 V): w = 0 a 35 kHz
d.R("SHF", "NWF", "10k 0.1%")
d.R("+REF5", "RZF", "8k87 0.1%", note="offset 5,40 V: 9,26k = 8,87k + trimmer (zero)")
trim("RZF", "NWF", "1k", note="ZERO della frequenza (RISULTATI-conv-that320)")
d.R("NWF", "WF", "10k 0.1%")
PF.add(("AGND", "NWF", "WF"))
d.R("WF", "RSF", "24k3 0.1%", note="26,7k = 24,3k + trimmer (scala, ottave)")
trim("RSF", "VBD", "5k", note="SCALA della frequenza")
d.R("VBD", "AGND", "1k +3300ppm/K", "Resistor_SMD:R_1206_3216Metric",
    note="NOTA: tempco +3300 ppm/K, incollata ai THAT 320 (RISULTATI-conv-that320)")
PF.add(("VBD", "VB1", "VB1"))
PF.flush("FREQ: buffer del pot, shaper, offset, buffer della base dei Q1")

# ------------------------------------------------------------ converter
d.block = "CONVERTER ESPONENZIALI: THAT 320 + LM334 PTAT, uno per sezione 2 poli (RISULTATI-conv-that320)"
CONV = []
for s in SIDES:
    for k in (1, 2):
        t = "%s%d" % (s, k)
        d.part("Q", THAT320, "THAT320S14-U", SOIC14,
               {"C1": "CR" + t, "B1": "VB1", "E1": "EX" + t, "C2": "IA%s_1" % t, "B2": "AGND", "E2": "EX" + t,
                "C3": "IA%s_2" % t, "B3": "AGND", "E3": "EX" + t, "C4": None, "B4": None, "E4": None,
                "SUB": "AGND", "SUB2": "AGND"},
               note="Q1 riferimento, Q2 e Q3 verso i pin Iabc della sezione %d, lato %s; Q4 libero" % (k, s))
        d.part("U", LM334, "LM334SM", SOIC8, {"V+": "CR" + t, "R": "RS" + t, "V-": "-15LN"}, ref=uref(),
               note="Iref PTAT dal collettore di Q1 verso -15 V (filter-module §4, todo 50)")
        d.R("RS" + t, "RT" + t, "150 0.1%")
        trim("RT" + t, "-15LN", "100", note="fondo scala del converter (Iref 271-451 uA)")
        d.C("OL" + t, "CR" + t, "1n C0G", C12, note="compensazione dell'anello (taglio ~72 kHz)")
        d.R("OL" + t, "EX" + t, "2k2")
        diode("AGND", "EX" + t, note="protegge la giunzione E-B all'accensione")
        CONV.append(("AGND", "CR" + t, "OL" + t))
for i in range(0, 4, 2):
    opa2(CONV[i], CONV[i + 1], note="anelli dei converter (FET: niente corrente nel nodo cr)",
         value="OPA1642AIDR", vp="+15LN", vm="-15LN")

# ------------------------------------------------------------ RES
d.side = "B"      # NOTA: RES sul retro (giro 3: davanti servivano 8 mm); il trimmer resta davanti
d.block = "RES dec. 153: shaper gpos, raddrizzatore gneg, sorgenti P e N (filter-module §5, shaper-res.cir)"
PR = pz.Pack("+15LN", "-15LN")
d.R("RW", "+REF5", "1M", note="pot staccato = RES a zero (manopola rovescia: Vx 5 V)")
PR.add(("RW", "VXR", "VXR"))
d.R("VXR", "SJR", "34k 0.1%")
d.R("VXR", "N1R", "24k3 0.1%")
d.R("N1R", "-REF5", "113k 0.1%")
diode("N1R", "SJR")
d.R("VXR", "N2R", "10k 0.1%")
d.R("N2R", "-REF5", "18k2 0.1%")
diode("N2R", "SJR")
d.R("+REF5", "RRF", "95k3 0.1%", note="Rref 102k = 95,3k + trimmer: il fischio parte al 93 %")
trim("RRF", "SJR", "10k", note="taratura della RES: «il fischio parte al 93 %»")
d.R("SJR", "VPN", "10k 0.1%")
PR.add(("AGND", "SJR", "VPN"))
d.R("VXR", "SRR", "10k 0.1%")
d.R("-REF5", "SRR", "100k 0.1%", note="soglia 0,5 V")
diode("SRR", "ARR")
diode("ARR", "VNG")
d.R("VNG", "SRR", "34k8 0.1%")
d.R("VNG", "AGND", "100k")
PR.add(("AGND", "SRR", "ARR"))
d.R("VNG", "NIG", "10k 0.1%", note="NOTA: invertitore, la sorgente PNP vuole un comando negativo")
d.R("NIG", "VNN", "10k 0.1%")
PR.add(("AGND", "NIG", "VNN"))
for s in SIDES:
    for pol, ctl in (("P", "VPN"), ("N", "VNN")):
        t = pol + s
        d.R("ER" + t, "AGND", "41k7 0.1%", note="NOTA: 5 V = 119,7 uA = gres 1 sulla sezione Q 1,307 (d5b-4p: 22,6k x 1,848)")
        d.part("Q", PNP, "MMBT3906", SOT23, {"B": "BR" + t, "E": "ER" + t, "C": "IR" + t},
               note="sorgente: spinge Iabc nel pin dell'OTA %s" % t)
        PR.add((ctl, "ER" + t, "BR" + t))
PR.flush("RES: buffer del pot, shaper, raddrizzatore, invertitore, 4 sorgenti")
d.side = "F"

# ------------------------------------------------------------ core
RA, RD = "2k87 0.1%", "100 0.1%"     # partitore k 1/30: 2,9k nel sim, E96 2,87k (k 1/29,7)
CORE_OUT = {}
for s in SIDES:
    d.side = "B"      # NOTA: i due core sul retro (giro 1: davanti servivano 105 mm in piu', giro 2 col solo R: 57)
    d.block = "RICEVITORE del bus e CORE (a') 4 poli, lato %s (d5c-sum-pass%s.cir)" % (s, "-hp" if HP else "")
    P = pz.Pack("+15LN", "-15LN")
    rx = "RX_" + s
    d.R(rx, "BUS_%s_%s" % (S, s), "10k 0.1%", note="ricevitore a massa virtuale (sistema-backplane §4)")
    d.C(rx, "BUS_%s_%s" % (S, s), "10p C0G")
    opa2(("AGND", "BUS_%s_%s" % (S, s), rx), ("YM_" + s, "OD_" + s, "OD_" + s),
         note="ricevitore del bus (A) e driver d'uscita (B), lato " + s)
    d.R("OD_" + s, "%s_OUT_%s" % (S, s), "10k 0.1%", note="R lato sorgente sul DJ bus (dec. 159)")
    chips = []
    for k in (1, 2):
        t = "%s%d" % (s, k)
        vin = rx if k == 1 else (("HP" + s + "1") if HP else ("LPB" + s + "1"))
        ns, hp, hk, bp, bpb, bk, lp, lpb = ("NS" + t, "HP" + t, "HK" + t, "BP" + t, "BPB" + t, "BK" + t,
                                             "LP" + t, "LPB" + t)
        d.R(vin, ns, "10k 0.1%")
        d.R(lpb, ns, "10k 0.1%")
        d.R(ns, hp, "10k 0.1%")
        P.add(("AGND", ns, hp))
        if k == 1:
            d.R(bpb, ns, "5k41 0.1%", note="NOTA: Q 0,541 con una R (d = 1,848) al posto dell'OTA a Iabc fissa del sim")
        d.R(hp, hk, RA)
        d.R(hk, "AGND", RD)
        Cx(bp, "AGND", "1n1", note="C 33n x k, C0G 1 % appaiati (§5quater)")
        P.add((bp, bpb, bpb))
        d.R(bpb, bk, RA)
        d.R(bk, "AGND", RD)
        Cx(lp, "AGND", "1n1")
        P.add((lp, lpb, lpb))
        d.part("U", OTA, "LM13700M", SOIC16,
               {"INP_A": hk, "INN_A": "AGND", "OUT_A": bp, "IABC_A": "IA%s_1" % t,
                "INP_B": bk, "INN_B": "AGND", "OUT_B": lp, "IABC_B": "IA%s_2" % t,
                "DIODE_A": None, "DIODE_B": None, "BUFIN_A": None, "BUFOUT_A": None, "BUFIN_B": None, "BUFOUT_B": None,
                "V+": "+15LN", "V-": "-15LN"}, ref=uref(), note="integratori della sezione %d, lato %s" % (k, s))
        d.C("+15LN", "AGND", "100n")
        d.C("AGND", "-15LN", "100n")
    # RES e limitatore sulla sezione 2
    t = s + "2"
    d.part("U", OTA, "LM13700M", SOIC16,
           {"INP_A": "BK" + t, "INN_A": "AGND", "OUT_A": "NS" + t, "IABC_A": "IRP" + s,
            "INP_B": "AGND", "INN_B": "BK" + t, "OUT_B": "NS" + t, "IABC_B": "IRN" + s,
            "DIODE_A": None, "DIODE_B": None, "BUFIN_A": None, "BUFOUT_A": None, "BUFIN_B": None, "BUFOUT_B": None,
            "V+": "+15LN", "V-": "-15LN"}, ref=uref(), note="RES: OTA P smorza, OTA N innesca (gres = gpos - gneg)")
    d.C("+15LN", "AGND", "100n")
    d.C("AGND", "-15LN", "100n")
    d.R("BPB" + t, "NL" + s, "4k7", note="limitatore (§5quater, d5a-res153-osc.cir)")
    diode("NL" + s, "NLA" + s)
    diode("NLA" + s, "NS" + t)
    diode("NS" + t, "NLB" + s)
    diode("NLB" + s, "NL" + s)
    P.flush("core lato %s: summer e buffer di stato" % s)
    CORE_OUT[s] = ("HP" + s + "2") if HP else ("LPB" + s + "2")
d.side = "F"

# ------------------------------------------------------------ overdrive
d.block = "OVERDRIVE v0.2 col DRIVE a pot doppio e servo DC (§5ter, od2-pot-tran.cir, od2-servo-dc.cir)"
PO = pz.Pack()
SERVO = []
for s in SIDES:
    x = CORE_OUT[s]
    d.R(x, "GN" + s, "10k 0.1%")
    d.R("GN" + s, "A" + s, "20k 0.1%")
    PO.add(("AGND", "GN" + s, "A" + s))
    d.R("A" + s, "W" + s, "2k2", note="tosatore: 2+2 1N4148 a massa")
    diode("W" + s, "WP" + s)
    diode("WP" + s, "AGND")
    diode("AGND", "WQ" + s)
    diode("WQ" + s, "W" + s)
    PO.add(("W" + s, "WB" + s, "WB" + s))
    d.R(x, "DN" + s, "10k 0.1%")
    d.R("WB" + s, "DN" + s, "8k56 0.1%", note="10k/k, k 1,171 (E192 8,56k: k 1,168)")
    d.R("DN" + s, "VD" + s, "10k 0.1%")
    PO.add(("AGND", "DN" + s, "VD" + s))
    d.C("VD" + s, "PT" + s, "22u NP", CNP, note="niente continua sul pot (taglio 0,7 Hz)")
    d.R("DW" + s, "AGND", "1M", note="pot staccato = DRIVE a zero")
    PO.add(("DW" + s, "WO" + s, "WO" + s))
    d.R("WO" + s, "SN" + s, "10k 0.1%")
    d.R(x, "SN" + s, "10k 0.1%")
    d.R("SN" + s, "Y" + s, "10k 0.1%", note="y = -(x + m d)")
    PO.add(("VP" + s, "SN" + s, "Y" + s))
    d.R("Y" + s, "SI" + s, "1M", note="servo DC: integratore 1M / 47n, polo 0,05 Hz")
    Cx("SI" + s, "SO" + s, "47n")
    d.R("SO" + s, "VP" + s, "100k")
    d.R("VP" + s, "AGND", "1k")
    SERVO.append(("AGND", "SI" + s, "SO" + s))
PO.flush("overdrive: x2, buffer del tosatore, differenza, buffer del cursore, I/V")
opa2(SERVO[0], SERVO[1], note="servo DC dell'overdrive (FET)", value="OPA1642AIDR")

# ------------------------------------------------------------ muto
d.block = "MUTO della sezione (bit FILT_MODE, §2bis) e driver verso il DJ bus"
for n, c in enumerate(cpin, 1):
    net = "FILT_MODE%d_%d" % (n, bit)
    d.R(net, "CTRL_GND", "100k", note="pull-down lato filtro (sistema-backplane §5)")
    d.part("D", "Device:D_Schottky", "BAT54WS", "Diode_SMD:D_SOD-323", {"A": net, "K": "MUTEN"},
           note="OR: la sezione suona se almeno un canale la sceglie")
d.R("MUTEN", "CTRL_GND", "100k")
p = {"VDD": "+15SW", "VSS": "-15SW", "GND": "AGND", "NIC": None}
for j, s in ((1, "L"), (2, "R")):
    p.update({"S%dA" % j: "Y" + s, "S%dB" % j: "AGND", "D%d" % j: "YM_" + s, "IN%d" % j: "MUTEN"})
for j in (3, 4):
    p.update({"S%dA" % j: "AGND", "S%dB" % j: "AGND", "D%d" % j: "AGND", "IN%d" % j: "AGND"})
d.part("U", ADG, "ADG1434YRUZ", "Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm", p, ref=uref(),
       note="NOTA: muto secco (A = IN alto = suona, B = massa); il fischio della RES tagliato puo' fare click")
d.C("+15SW", "AGND", "100n")
d.C("AGND", "-15SW", "100n")
d.netclass["MUTEN"] = 0.3

# ------------------------------------------------------------ cavo
d.block = "CAVO SCHEDA COMANDI (J2)"


def fili_cavo(sez):
    """Ordine dei fili di J2: FREQ (pot fra +REF5 e AGND), RES (pot rovescio), DRIVE (pot doppio:
    capo PT, cursore DW, altro capo AGND). Solo letterali: la scheda comandi lo leggera' da qui."""
    return ["AGND", "FW", "+REF5", "RW", "AGND", "PTL", "DWL", "AGND", "PTR", "DWR", "AGND", "+REF5"]


cv.cavo(d, fili_cavo(S), x=L / 2, y=14)

d.audio_rules = {}

if __name__ == "__main__":
    d.build(route="--no-route" not in sys.argv)
