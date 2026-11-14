"""BOX: scheda del box dell'alimentatore esterno (dec. 113, dec. 131). Bozza v0.1.

Fonte: docs/fase3/sistema-psu-esterno.md §1-§3 (schema a blocchi, LDO discreto, +5 V e V_FAN,
AC_OK, protezioni, cavo), sim/system/RISULTATI-psu-box.md §7 (dec. 131: W1 2x21 V 7,0 A,
W2 2x18 V 1,5 A, Rsense W1 0,15 ohm, bulk W1 22 mF, fusibili W1 T8 A / W2 T2 A, ponte W1 25 A).
Valori dei regolatori da sim/system/psu-box-w1-142-7a.cir e psu-box-w2-142.cir (stessa topologia).

Sulla scheda: morsetti dei secondari, fusibili dei secondari, ponti, bulk, quattro LDO discreti
(W1 +-22,0 V, W2 +-19 V), [M] raw +-27, +5 V (LM1084), V_FAN (raw W4), rivelatore AC_OK,
connettore verso il cavo (stesso ordine del J2 di PSU-IN).
Fuori dalla scheda (cablaggio del box): presa IEC col filtro, interruttore, fusibile del primario
T3,15 A, NTC col relè di bypass, toroidale, terra PE sul telaio. Gli 0 V della scheda non toccano
la terra (§3): i fori di fissaggio sono senza pad.
Pezzi sull'aletta (MOSFET, ponti, LM1084) sul bordo basso della scheda, y = 12.
Valori [PROVVISORIO]. Le scelte non scritte nei documenti sono segnate NOTA (pcb/box/NOTE.md).
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from pcbgen import DesignRiprova as Design

d = Design("box", HERE, "maelcum BOX alimentatore esterno (dec. 113, 131) - bozza v0.1", board=(260, 200),
           rev="0.1-bozza")
d.gnd = "0V_A"
d.inner_signal = True
d.piano_in2 = "CTRL_GND"   # In2 piano pieno del CTRL_GND: con le piste ne restavano aperti 5-7 a ogni giro
d.link_pairs = True          # pin gemelli del J1 (C+22 1-2, C-22 3-4, 0V_A 5-6, C+5 13-14, CTRL_GND 15-16)
d.link_pairs_masse = True    # anche CTRL_GND, che qui non ha colata
d.link_pairs_dmax = 4.5      # Mini-Fit Jr: le due file stanno a 4,2 mm (default 4,0 del C96)

SOT23 = "Package_TO_SOT_SMD:SOT-23"
SOIC8 = "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"
R1206 = "Resistor_SMD:R_1206_3216Metric"
R2512 = "Resistor_SMD:R_2512_6332Metric"
R2W = "Resistor_THT:R_Axial_DIN0414_L11.9mm_D4.5mm_P15.24mm_Horizontal"
TO247 = "Package_TO_SOT_THT:TO-247-3_Vertical"
TO220 = "Package_TO_SOT_THT:TO-220-3_Vertical"
FUSE = "Fuse:Fuseholder_Cylinder-5x20mm_Stelvio-Kontek_PTF78_Horizontal_Open"
FUSE10 = "Fuse:Fuseholder_Cylinder-5x20mm_Schurter_0031_8201_Horizontal_Open"
MKDS3 = "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal"
MKDS2 = "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal"
D35 = "Capacitor_THT:CP_Radial_D35.0mm_P10.00mm_SnapIn"
D30 = "Capacitor_THT:CP_Radial_D30.0mm_P10.00mm_SnapIn"
D25 = "Capacitor_THT:CP_Radial_D25.0mm_P10.00mm_SnapIn"
D10 = "Capacitor_THT:CP_Radial_D10.0mm_P5.00mm"
D63 = "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm"
C1206 = "Capacitor_SMD:C_1206_3216Metric"
Y_ALETTA = 12

# reti di potenza: W1 porta 2,70 A per ramo (5,5 A efficaci nell'avvolgimento)
d.power_nets("W1A", "W1B", "W1A_F", "W1B_F", "RAW1+", "RAW1-", "S1P", "S1N", "C+22", "C-22", "0V_A", width=2.0)
d.power_nets("W2A", "W2B", "W2A_F", "W2B_F", "RAW2+", "RAW2-", "S2P", "S2N", "C+19", "C-19",
             "W3A", "W3B", "W3A_F", "W3B_F", "C+27", "C-27",
             "W4A", "W4B", "W4A_F", "RAW5", "C+5", width=0.8)
# NOTA: masse senza colata a 0,6 mm (con 0,8 Freerouting ne lascia aperte 13); 1,3 A al massimo sul CTRL_GND
d.power_nets("CTRL_GND", "0V_FAN", "0V_LN", "0V_M", width=0.6)

# reti sottili del controllo (dopo i tie da 0 ohm): alimentano pin SOT-23 e SOIC
d.power_nets(*["%s_%s" % (r, n) for r in ("RK", "ZK") for n in ("1P", "1N", "2P", "2N")], "5V_L", "GND_L", width=0.4)

# ------------------------------------------------------------ cavo verso il mixer
d.block = "CAVO VERSO IL MIXER (20 conduttori, §3; stesso ordine del J2 di PSU-IN)"
CAVO = ["C+22", "C+22", "C-22", "C-22", "0V_A", "0V_A", "C+19", "C-19", "0V_LN", "C+27", "C-27",
        "C+5", "C+5", "CTRL_GND", "CTRL_GND", "RAW5", "0V_FAN", "AC_OK", None, None, None, None, None]
d.part("J", "Connector_Generic:Conn_02x12_Odd_Even", "Mini-Fit Jr 2x12",
       "Connector_Molex:Molex_Mini-Fit_Jr_5566-24A2_2x12_P4.20mm_Vertical",
       {i + 1: n for i, n in enumerate(CAVO) if n}, ref="J1", place=(220, 180, 0),
       note="NOTA: cavo interno verso il connettore circolare del box; pin 17 = V_FAN (raw W4), "
            "pin 18 = suo ritorno. La PE va dal connettore al telaio, non passa dalla scheda (§3)")
for ref, (x, y) in (("H1", (5, 5)), ("H2", (255, 5)), ("H3", (5, 195)), ("H4", (255, 195))):
    d.part("H", "Mechanical:MountingHole", "M3", "MountingHole:MountingHole_3.2mm_M3", {}, ref=ref, place=(x, y, 0),
           note="foro senza pad: gli 0 V del box non toccano il telaio (§3)")

# ------------------------------------------------------------ secondari
d.block = "SECONDARI: morsetti dal toroidale (~420 VA, dec. 131) e fusibili lenti prima dei ponti (§2.7)"
d.part("J", "Connector_Generic:Conn_01x03", "W1 2x21 V 7,0 A", MKDS3, {1: "W1A", 2: "0V_A", 3: "W1B"}, ref="J2",
       note="presa centrale = 0 V audio")
d.part("J", "Connector_Generic:Conn_01x03", "W2 2x18 V 1,5 A", MKDS3, {1: "W2A", 2: "0V_LN", 3: "W2B"}, ref="J3")
d.part("J", "Connector_Generic:Conn_01x03", "W3 2x20 V 0,4 A", MKDS3, {1: "W3A", 2: "0V_M", 3: "W3B"}, ref="J4")
d.part("J", "Connector_Generic:Conn_01x02", "W4 9 V 2,5 A", MKDS2, {1: "W4A", 2: "W4B"}, ref="J5")
for a, b, val, fp in (("W1A", "W1A_F", "T8A", FUSE10), ("W1B", "W1B_F", "T8A", FUSE10),
                      ("W2A", "W2A_F", "T2A", FUSE), ("W2B", "W2B_F", "T2A", FUSE),
                      ("W3A", "W3A_F", "T630mA", FUSE), ("W3B", "W3B_F", "T630mA", FUSE),
                      ("W4A", "W4A_F", "T3,15A", FUSE)):
    d.part("F", "Device:Fuse", val, fp, {1: a, 2: b},
           note="NOTA: portafusibile 10 A (Schurter 0031.8201) per il T8 A del W1, da verificare a catalogo"
           if val == "T8A" else "fusibile del secondario (§2.7, dec. 131)")

# ------------------------------------------------------------ ponti e bulk
d.block = "PONTI E BULK (§2.1, dec. 131): sull'aletta i ponti, bulk 105 gradi"
d.part("D", "Diode_Bridge:KBPC2502T", "KBPC2502", "Diode_THT:Diode_Bridge_DIGITRON_KBPC_T",
       {1: "RAW1+", 2: "W1A_F", 3: "RAW1-", 4: "W1B_F"}, place=(25, Y_ALETTA + 8, 0),
       note="ponte del W1 da 25 A (dec. 131), sull'aletta")
for w, pos, neg in (("W2", "RAW2+", "RAW2-"), ("W3", "C+27", "C-27")):
    d.part("D", "Diode_Bridge:GBU4D", "GBU4D", "Diode_THT:Diode_Bridge_Vishay_GBU",
           {1: pos, 2: w + "A_F", 3: w + "B_F", 4: neg}, place=(150 if w == "W2" else 176, Y_ALETTA, 0),
           note="ponte da 4 A (§2.1: 3 A per gli altri), sull'aletta")
d.part("D", "Diode_Bridge:GBU4D", "GBU4D", "Diode_THT:Diode_Bridge_Vishay_GBU",
       {1: "RAW5", 2: "W4A_F", 3: "W4B", 4: "CTRL_GND"}, place=(202, Y_ALETTA, 0),
       note="ponte del W4: il meno e lo 0 V del +5 (CTRL_GND al mixer)")
# NOTA: 50 V e non 35 V sul W1: a vuoto e rete +10 % il picco del W1 vale ~34 V (21 x 1,07 x 1,1 x 1,414 - 0,7)
d.CP("RAW1+", "0V_A", "22000u 50V", D35, note="bulk W1 22 mF (dec. 131). NOTA: 50 V, a vuoto e rete +10 % il picco e ~34 V")
d.CP("0V_A", "RAW1-", "22000u 50V", D35, note="bulk W1 22 mF (dec. 131)")
d.CP("RAW2+", "0V_LN", "10000u 35V", D30, note="bulk W2 10 mF (§2.1): picco ~29 V a vuoto e rete +10 %")
d.CP("0V_LN", "RAW2-", "10000u 35V", D30)
d.part("C", "Device:C_Polarized", "4700u 50V", D25, {1: "C+27", 2: "0V_M"}, place=(160, 45, 0),
       note="bulk W3 4,7 mF: [M] raw, nessun regolatore nel box (§1); accanto al suo ponte")
d.part("C", "Device:C_Polarized", "4700u 50V", D25, {1: "0V_M", 2: "C-27"}, place=(186, 45, 0))
d.part("C", "Device:C_Polarized", "10000u 25V", D25, {1: "RAW5", 2: "CTRL_GND"}, place=(212, 45, 0),
       note="bulk W4 10 mF; NOTA: 25 V per il picco ~15 V a vuoto; accanto al ponte W4 e al LM1084")


# ------------------------------------------------------------ LDO discreti
def tie(power, small, note="NOTA: collegamento Kelvin (0 ohm): la pista larga di potenza non entra nei pin SOT-23/SOIC"):
    """Unisce una rete di potenza larga alla rete sottile del circuito di controllo in un punto solo."""
    d.R(power, small, "0", note=note)
    return small


def ldo(n, raw, zero, out, rsense, rsense_fp, rtop, fet, fet_fp, x, neg=False):
    """LDO a MOSFET del §2.2 (psu-box-w1-142-7a.cir): Rsense, PNP (NPN) di limite, MOSFET di passo,
    Rgs 10k + zener 12 V, NPN (PNP) di pilotaggio con 4,7k d'emettitore, riferimento 2,5 V con
    soft-start 100k/1u, partitore, OPA197 dal raw con integratore 10n + 10k sull'ingresso invertente.
    Le reti larghe (raw, source, uscita, 0 V del W2) arrivano al controllo con un 0 ohm (tie)."""
    g, bd, ed, ea, cz, fb, ref, refs = ("%s_%s" % (t, n) for t in ("G", "BD", "ED", "EA", "CZ", "FB", "REF", "SS"))
    s = "S" + n
    d.R(raw, s, rsense, rsense_fp, note="Rsense del limite di corrente (§2.2, dec. 131)")
    d.part("Q", "Transistor_FET:%s" % ("Q_NMOS_GDS" if neg else "Q_PMOS_GDS"), fet, fet_fp,
           {"G": g, "D": out, "S": s}, place=(x, Y_ALETTA, 0),
           note="MOSFET di passo sull'aletta. NOTA: pinout G-D-S da confermare sul datasheet prima dell'ordine")
    rw = tie(raw, "RK_" + n, "NOTA: Kelvin sul raw prima della Rsense: emettitore del limite, riferimento, op-amp")
    sk = tie(s, "SK_" + n, "NOTA: Kelvin sul source dopo la Rsense: base del limite, Rgs, zener")
    ok = tie(out, "OK_" + n, "NOTA: Kelvin sull'uscita: il partitore legge la tensione al condensatore d'uscita")
    zk = zero if zero == d.gnd else tie(zero, "ZK_" + n)
    d.R(sk, g, "10k", note="Rgs")
    if neg:
        d.part("Q", "Transistor_BJT:BC847", "BC847B", SOT23, {"C": g, "B": sk, "E": rw}, note="limite di corrente (NPN)")
        d.part("D", "Diode:BZX84Cxx", "BZX84C12", SOT23, {"A": sk, "K": g}, note="zener 12 V G-S")
        d.part("Q", "Transistor_BJT:BC857", "BC857B", SOT23, {"C": g, "B": bd, "E": ed}, note="pilotaggio del gate (PNP)")
        d.R(zk, ed, "4k7")
        d.R(ref, rw, "10k", R1206, note="corrente del riferimento: 1,2-3,2 mA")
        d.part("D", "Reference_Voltage:LM4040DBZ-2.5", "LM4040-2.5", SOT23, {"K": zk, "A": ref, "NC": None},
               note="riferimento -2,5 V")
        d.CP(zero, out, "470u 35V", D10, note="uscita nel box (470 uF, ESR ~0,05 ohm in simulazione)")
        sup = {"V+": zk, "V-": rw}
    else:
        d.part("Q", "Transistor_BJT:BC857", "BC857B", SOT23, {"C": g, "B": sk, "E": rw}, note="limite di corrente (PNP)")
        d.part("D", "Diode:BZX84Cxx", "BZX84C12", SOT23, {"A": g, "K": sk}, note="zener 12 V G-S")
        d.part("Q", "Transistor_BJT:BC847", "BC847B", SOT23, {"C": g, "B": bd, "E": ed}, note="pilotaggio del gate (NPN)")
        d.R(ed, zk, "4k7")
        d.R(rw, ref, "10k", R1206, note="corrente del riferimento: 1,2-3,2 mA")
        d.part("D", "Reference_Voltage:LM4040DBZ-2.5", "LM4040-2.5", SOT23, {"K": ref, "A": zk, "NC": None},
               note="riferimento +2,5 V")
        d.CP(out, zero, "470u 35V", D10, note="uscita nel box (470 uF, ESR ~0,05 ohm in simulazione)")
        sup = {"V+": rw, "V-": zk}
    d.R(ea, bd, "1k")
    d.R(ref, refs, "100k", note="soft-start: tau 0,1 s (§2.2)")
    d.C(refs, zk, "1u", C1206)
    d.R(ok, fb, rtop + " 1%")
    d.R(fb, zk, "4k99 1%")
    d.C(ea, cz, "10n", note="integratore della compensazione")
    d.R(cz, fb, "10k")
    pins = {3: refs, 2: fb, 6: ea, 7: sup["V+"], 4: sup["V-"]}
    d.part("U", "Amplifier_Operational:OPA197xD", "OPA197", SOIC8, pins,
           note="amplificatore d'errore dal raw (§2.2). NOTA: OPA197, 36 V di lavoro: il raw del W1 a vuoto "
                "e rete +10 % arriva a ~34 V")
    d.C(sup["V+"], sup["V-"], "100n 50V", note="ai pin d'alimentazione dell'op-amp")


d.block = "LDO W1 +22,0 V (§2.2, dec. 131): Rsense 0,15 ohm, limite ~4 A a freddo"
ldo("1P", "RAW1+", "0V_A", "C+22", "0.15 2W", R2W, "38k3", "IRFP9140N", TO247, 60)
d.block = "LDO W1 -22,0 V"
ldo("1N", "RAW1-", "0V_A", "C-22", "0.15 2W", R2W, "38k3", "IRFP140N", TO247, 85, neg=True)
d.block = "LDO W2 +19 V (§2.2): Rsense 0,56 ohm, limite ~1,1 A"
ldo("2P", "RAW2+", "0V_LN", "C+19", "0.56", R2512, "32k4", "IRF9540N", TO220, 110)
d.block = "LDO W2 -19 V"
ldo("2N", "RAW2-", "0V_LN", "C-19", "0.56", R2512, "32k4", "IRF540N", TO220, 130, neg=True)

# ------------------------------------------------------------ +5 V e V_FAN
d.block = "+5 V (§2.4): LM1084 dal raw W4, sull'aletta; V_FAN = raw W4 sul pin 17"
d.part("U", "Regulator_Linear:LM1084-5.0", "LM1084-5.0", TO220, {"VI": "RAW5", "VO": "C+5", "GND": "CTRL_GND"},
       place=(232, Y_ALETTA, 0), note="1,25 A di dimensionamento, ~7,7 W nel caso peggiore (§2.8)")
d.CP("RAW5", "CTRL_GND", "10u 25V", D63, note="ingresso del LM1084")
d.CP("C+5", "CTRL_GND", "100u 16V", D63, note="NOTA: uscita del LM1084, il datasheet chiede >= 10 uF: 100 uF elettrolitico")
d.C("C+5", "CTRL_GND", "100n")
d.R("CTRL_GND", "0V_FAN", "0", R2512,
    note="NOTA: il ritorno delle ventole parte dal meno del ponte W4; nel mixer va alla stella col suo conduttore")

# ------------------------------------------------------------ AC_OK
d.block = "AC_OK (§2.5): doppia semionda dal W1, 47k/4,7k, 10 uF; soglia 75 % del picco nominale (1,39 V)"
d.part("D", "Diode:1N4148W", "1N4148W", "Diode_SMD:D_SOD-123", {"A": tie("W1A_F", "W1A_K"), "K": "AC1"})
d.part("D", "Diode:1N4148W", "1N4148W", "Diode_SMD:D_SOD-123", {"A": tie("W1B_F", "W1B_K"), "K": "AC1"})
d.R("AC1", "ACD", "47k")
d.R("ACD", "0V_A", "4k7")
d.C("ACD", "0V_A", "10u 16V", C1206, note="tau 42,7 ms con 47k || 4,7k")
tie("C+5", "5V_L", "NOTA: +5 della logica di AC_OK, Kelvin dal +5 del cavo")
tie("CTRL_GND", "GND_L", "NOTA: 0 V della logica di AC_OK")
d.R("5V_L", "REF25", "1k", note="riferimento della soglia: ~2,5 mA")
d.part("D", "Reference_Voltage:LM4040DBZ-2.5", "LM4040-2.5", SOT23, {"K": "REF25", "A": "GND_L", "NC": None})
d.R("REF25", "ACT", "8k06 1%", note="soglia 2,5 x 10 / 18,06 = 1,384 V (§2.5: 1,39 V)")
d.R("ACT", "GND_L", "10k 1%")
d.C("ACT", "GND_L", "100n")
d.R("ACD", "ACP", "10k", note="NOTA: isteresi ~50 mV con 10k / 1M (il documento dice solo «con isteresi»)")
d.R("ACL", "ACP", "1M")
d.R("5V_L", "ACL", "10k", note="pull-up locale della prima sezione")
d.part("U", "Comparator:LM393", "LM393", SOIC8, {3: "ACP", 2: "ACT", 1: "ACL",
                                                  5: "ACL", 6: "REF25", 7: "AC_OK", 8: "5V_L", 4: "GND_L"},
       note="A: rivelatore contro soglia; B: open collector verso il cavo, pull-up 10k nel PSU-IN (c17). "
            "NOTA: il rivelatore sta sullo 0 V audio, il comparatore sul CTRL_GND: si uniscono alla stella del mixer "
            "(differenza <= ~0,1 V, ~3 % della soglia)")
d.C("5V_L", "GND_L", "100n")

d.audio_rules = {"sensibili": r"^$", "cavo": r"^$", "rumorose": r"^$", "regolatori": []}

if __name__ == "__main__":
    d.build(route="--no-route" not in sys.argv)
