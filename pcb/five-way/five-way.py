"""5-WAY (v0.3, dec. 175): quattro schede di segnale, due per lato: A (ricevitore, banca, kill) e
B (celle, GROWL, NASTRO, uscita). Bozza v0.1. I LED di livello vanno sulla scheda comandi (2026-11-15).

Uso: python3 five-way.py LA|LB|RA|RB [--solo-schema] [--no-route]

Catena per lato (docs/fase2/five-way-module.md §2; netlist sim/five-way/module-noise-b9.cir con la
banca agli incroci H di bank-aligned-h.cir):
  DJ BUS (ricevitore a massa virtuale, inverte) -> pad -6 dB + buffer
  -> BANCA allineata agli incroci H 60/250/1,2k/8k (16 Sallen-Key + 6 AP2, §3.2bis)
  -> invertitori di polarita' su SUB e MID (§8.10)
  -> KILL: ADG1434 a pi greco (serie + shunt) per via (§8.10), taglio allo zero della via
     (comparatore LM339 + 74HC86/74HC14 + 74HC74, RISULTATI-kill-zc.md, dec. 164)
  -> somma delle 5 vie
  -> 5 celle parametriche v0.2.2 (integratori op-amp + JFET VCR, §4.2; WIDTH continuo §4.3;
     servo replica per ogni JFET, REV todo 50; POSITION con shaper a diodi per banda)
  -> GROWL A BANDE (growl-bande.cir) -> NASTRO A BANDE B9 (nastro-b9.cir), dec. 165, 166, 175
  -> make-up +6 dB col servo DC (§5bis.7) -> 47R -> 5W_OUT (slot 2, verso MSUM1 del master)
  Ogni scheda B porta la presa del meter (EDRV per 100R) sul cavo: i LED di livello delle 5 vie
  (five-way-led-livello.md, dec. 177) stanno sulla scheda comandi (five-way-comandi.py); la B della L
  porta anche +-15LN e +5VF.

Polarita' (sistema-polarita.md): dal net DJ bus a 5W_OUT -1; il ricevitore [A2] del master raddrizza.
Valori [PROVVISORIO]. Le scelte non scritte nei documenti sono segnate NOTA (pcb/five-way/NOTE.md).
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from pcbgen import DesignRiprova, boxsym
from backplane import c96, SYM_C96, FP_C96, C96_DAL_BORDO
import celle_vca as cv
from celle_vca import C12, SOIC14
from celle_micmono import power_18_sw, power_ln, ADG, LM339
from comune_5w import Parti

ARG = next((a for a in sys.argv[1:] if a in ("LA", "LB", "RA", "RB")), None)
if ARG is None:
    sys.exit("uso: five-way.py LA|LB|RA|RB [--solo-schema] [--no-route]")
s, PARTE = ARG[0], ARG[1]
# PIANO-SCHEDE-F: LB fila 1, RB fila 2, LA e RA fila 3 (la 4 tiene due reroute e il PSU-IN)
L, H = {"LB": (300, 178), "RB": (300, 175), "LA": (206, 172), "RA": (206, 172)}[ARG]   # B a 300: a 272 il retro resta fitto (giro 3)

DESCR = {"A": "ricevitore, banca, kill", "B": "celle, GROWL, NASTRO, uscita"}[PARTE]
d = DesignRiprova("five-way-" + ARG, os.path.join(HERE, ARG),
                  "maelcum 5-WAY scheda di segnale %s, parte %s: %s (v0.3) - bozza v0.1" % (s, PARTE, DESCR),
                  board=(L, H), rev="0.1-bozza")
d.gnd = "AGND"
d.inner_signal = True
d.link_pairs = True
d.link_pairs_masse = True
d.cluster_fuori = True     # passivi senza posto attorno all'op-amp: a blocchi (pcbgen, 2026-11-15)
if PARTE == "B":
    d.route_tries = 6      # LB: 1 aperto (isola di massa) in 2 giri su 4 (giro 5)
    d.fanout_more = True   # LB: 12 pad di massa senza via -> isole di colata (giro 6, come il master)

SOIC8 = "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"
TSSOP14 = "Package_SO:TSSOP-14_4.4x5mm_P0.65mm"
CNP = "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm"
SOT23 = "Package_TO_SOT_SMD:SOT-23"

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
# Pinout: Linear Systems LSK389 A/B/C/D, Doc 201122 Rev A27 (06/23/2023), SOIC 8L Top View (todo 339).
# SS = substrato: il TO-71 6L non lo porta fuori, quindi resta libero anche sul SOIC [deduzione].
JDUAL = boxsym("JFET_DUAL_N", [("1", "S1", "passive"), ("2", "D1", "passive"), ("4", "G1", "passive"), ("3", "SS1", "no_connect")],
               [("5", "S2", "passive"), ("6", "D2", "passive"), ("8", "G2", "passive"), ("7", "SS2", "no_connect")],
               ref="Q", fp=SOIC8, desc="Dual JFET N appaiato LSK389. Pinout Linear Systems Doc 201122 Rev A27, SOIC 8L")

pz = Parti(d)           # riferimenti U, condensatori, quad: comune_5w.py (todo 342)
uref, Cx, Pack = pz.uref, pz.Cx, pz.Pack


def opa2(a, b, note="", value="OPA1612AIDR", vp="+18V", vm="-18V"):
    cv.opa2(d, uref(), a, b, vp, vm, note=note, value=value)


# ------------------------------------------------------------ backplane
d.block = "BACKPLANE C96 (classe 5-WAY, sistema-backplane §4)"
SUM = "5W_SUM_" + s                                     # NOTA: somma delle vie da A a B sul backplane
if PARTE == "A":
    b = {"b1" if s == "L" else "b2": "DJBUS_" + s,      # DJ bus in
         "b7" if s == "L" else "b8": SUM}
else:
    b = {"b7" if s == "L" else "b8": SUM,
         "b4" if s == "L" else "b5": "5W_OUT_" + s}     # verso MSUM1 del master
for k in range(1, 11):
    b["b%d" % (3 * k)] = "AGND"
d.part("J", SYM_C96, "C96 maschio", FP_C96, c96(b), ref="J1", place=(L / 2, H - C96_DAL_BORDO, 180),
       note="DIN 41612 C 3x32, angolo retto; lato %s del 5-way, parte %s" % (s, PARTE))
for ref, x in (("H1", 5), ("H2", L / 2), ("H3", L - 5)):
    d.part("H", "Mechanical:MountingHole_Pad", "CHASSIS", "MountingHole:MountingHole_3.2mm_M3_Pad",
           {1: "CHASSIS"}, ref=ref, place=(x, 5, 0), note="foro di fissaggio, a CHASSIS")

d.block = "ALIMENTAZIONE +-18 audio, +-15 switch, +5, +-15 LN, +-5 riferimento"
power_18_sw(d, base=140)
if PARTE == "B":
    power_ln(d, base=144)
    cv.ref5(d, "U146")
d.power_nets("+18V", "-18V", width=0.4)
d.netclass["CTRL_GND"] = 0.3          # pin TSSOP della logica: pista <= 0,3 mm (canale giro 6-7)

if PARTE == "A":
    # ------------------------------------------------------------ ingresso
    d.block = "INGRESSO: ricevitore del DJ bus (inverte) e pad -6 dB (§2, REV todo 227)"
    d.R("RX", "DJBUS_" + s, "10k 0.1%", note="ricevitore a massa virtuale: unity per sorgente (10k lato canale)")
    d.C("RX", "DJBUS_" + s, "22p C0G", note="NOTA: Cf come i ricevitori a massa virtuale del master")
    d.R("RX", "NPAD", "20k 0.1%", note="pad -6 dB (dec. 73)")
    d.R("NPAD", "AGND", "20k 0.1%")
    opa2(("AGND", "DJBUS_" + s, "RX"), ("NPAD", "VPAD", "VPAD"), note="ricevitore DJ bus e buffer del pad")

    # ------------------------------------------------------------ banca
    d.block = "BANCA allineata agli incroci H 60/250/1,2k/8k (§3.2bis, bank-aligned-h.cir)"
    P = Pack()
    SK = {60: ("100n", "18k7", "37k4"), 250: ("100n", "4k53", "9k09"), 1200: ("10n", "9k31", "18k7"),
          8000: ("4n7", "3k01", "6k04")}      # Cc, R (LP e HP), R a massa dell'HP = 2R
    AP = {250: ("47n", "9k53", "19k1", "14k3"), 1200: ("10n", "9k31", "18k7", "14k0"),
          8000: ("1n5", "9k31", "18k7", "14k0")}   # C, R1, R2, Rf del MFB


    def sklp(t, vin, vout, fc):
        c, r, _ = SK[fc]
        d.R(vin, "A" + t, r + " 0.1%")
        d.R("A" + t, "B" + t, r + " 0.1%")
        Cx("A" + t, vout, c, note="C1 = 2 Cc: due in parallelo (NOTA)")
        Cx("A" + t, vout, c)
        Cx("B" + t, "AGND", c)
        P.add(("B" + t, vout, vout))


    def skhp(t, vin, vout, fc):
        c, r, r2 = SK[fc]
        Cx(vin, "A" + t, c)
        Cx("A" + t, "B" + t, c)
        d.R("A" + t, vout, r + " 0.1%")
        d.R("B" + t, "AGND", r2 + " 0.1%")
        P.add(("B" + t, vout, vout))


    def ap2(t, vin, vout, f0):
        c, r1, r2, rf = AP[f0]
        d.R(vin, "N1" + t, r1 + " 0.1%")
        d.R("N1" + t, "AGND", r2 + " 0.1%")
        Cx("N1" + t, "NM" + t, c, note="C1 = 2C: due in parallelo (NOTA)")
        Cx("N1" + t, "NM" + t, c)
        d.R("NM" + t, "BP" + t, rf + " 0.1%")
        Cx("N1" + t, "BP" + t, c)
        P.add(("AGND", "NM" + t, "BP" + t))
        d.R(vin, "NA" + t, "10k 0.1%")
        d.R("BP" + t, "NA" + t, "4k99 0.1%", note="NOTA: R/2 = 5k, E192 4,99k (-0,2 %)")
        d.R("NA" + t, vout, "10k 0.1%")
        P.add(("AGND", "NA" + t, vout))


    skhp("H1", "VPAD", "R1", 60); skhp("H1b", "R1", "R1B", 60)
    skhp("H2", "R1B", "R2", 250); skhp("H2b", "R2", "R2B", 250)
    skhp("H3", "R2B", "R3", 1200); skhp("H3b", "R3", "R3B", 1200)
    skhp("H4", "R3B", "R4", 8000); skhp("H4b", "R4", "SUPER", 8000)
    sklp("A1", "VPAD", "S1A", 60); sklp("A2", "S1A", "S1B", 60)
    ap2("P1", "S1B", "S1C", 250); ap2("P2", "S1C", "S1D", 1200); ap2("P3", "S1D", "SUB_O", 8000)
    sklp("B1", "R1B", "S2B", 250); sklp("B2", "S2B", "S2C", 250)
    ap2("P4", "S2C", "S2D", 1200); ap2("P5", "S2D", "KICK", 8000)
    sklp("C1", "R2B", "S3C", 1200); sklp("C2", "S3C", "S3D", 1200)
    ap2("P6", "S3D", "MID_O", 8000)
    sklp("D1", "R3B", "S4C", 8000); sklp("D2", "S4C", "HIGH", 8000)
    # invertitori di polarita' (bande DISPARI di AP2, §8.10)
    for v in ("SUB", "MID"):
        d.R(v + "_O", "NI" + v, "2k 0.1%", note="invertitore unity, R appaiate (§8.10)")
        d.R("NI" + v, v, "2k 0.1%")
        P.add(("AGND", "NI" + v, v))
    P.flush("banca agli incroci H")

    # ------------------------------------------------------------ kill
    VIE = ("SUB", "KICK", "MID", "HIGH", "SUPER")
    d.block = "KILL a pi greco (ADG1434) e somma delle 5 vie (§8.10)"
    for k in range(2):
        p = {"VDD": "+15SW", "VSS": "-15SW", "GND": "AGND", "NIC": None}
        for j in range(1, 5):
            n = 4 * k + j
            if n <= 5:
                v = VIE[n - 1]
                p.update({"S%dA" % j: v, "S%dB" % j: "AGND", "D%d" % j: "G_" + v, "IN%d" % j: "KQ%d" % n})
            else:
                p.update({"S%dA" % j: "AGND", "S%dB" % j: "AGND", "D%d" % j: "AGND", "IN%d" % j: "AGND"})
        d.part("U", ADG, "ADG1434YRUZ", "Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm", p, ref=uref(),
               note="SPDT: A = IN alto = via passa, B = shunt a massa (Rev. E tabella 9)")
        d.C("+15SW", "AGND", "100n")
        d.C("AGND", "-15SW", "100n")
    for v in VIE:
        d.R("G_" + v, "NSUM", "10k 0.1%")
    d.R("NSUM", "VSUM", "10k 0.1%")
    P.add(("AGND", "NSUM", "VSUM"))
    P.flush("somma delle vie")
    d.R("VSUM", SUM, "47", note="NOTA: somma delle vie verso la scheda B (b7/b8); 40,2k di carico sulla B")

    d.block = "KILL allo zero della via: LM339, 74HC86, 74HC14, 74HC74 (RISULTATI-kill-zc.md, dec. 164)"
    # per via n: comparatore con isteresi ~11 mV -> C; fronte = C xor C ritardato (2k/1n, ~2 us);
    # MIS = levetta xor stato; tempo massimo 100k/220n (~22 ms) -> TO; CK = fronte OR TO (diodi);
    # il 74HC74 copia la levetta (D) sull'IN dell'ADG al fronte (NOTA: logica da simulare a porte).
    cmp_pins, xor_g, sch_g, ff = [], [], [], []
    for n, v in enumerate(VIE, 1):
        t = str(n)
        d.R(v, "CI" + t, "22k", note="NOTA: 22k + Schottky: l'ingresso del LM339 resta sopra -0,3 V")
        d.part("D", "Device:D_Schottky", "BAT54WS", "Diode_SMD:D_SOD-323", {"A": "CTRL_GND", "K": "CI" + t})
        d.part("D", "Device:D_Schottky", "BAT54WS", "Diode_SMD:D_SOD-323", {"A": "CI" + t, "K": "+5VF"})
        d.R("ZC" + t, "CI" + t, "10M", note="isteresi ~11 mV sulla via (22k/10M x 5 V)")
        d.R("+5VF", "ZC" + t, "10k")
        cmp_pins.append(("CI" + t, "AGND", "ZC" + t))
        d.R("ZC" + t, "ZR" + t, "2k")
        d.C("ZR" + t, "CTRL_GND", "1n C0G", note="ritardo del fronte ~2 us")
        sch_g += [("ZR" + t, "ZN" + t), ("ZN" + t, "ZD" + t)]
        xor_g += [("ZC" + t, "ZD" + t, "PZ" + t), ("KD" + t, "KQ" + t, "MIS" + t), ("TON" + t, "+5VF", "TO" + t)]
        d.R("MIS" + t, "TR" + t, "100k")
        d.C("TR" + t, "CTRL_GND", "220n", note="tempo massimo ~22 ms (via muta)")
        cv.diode(d, "TR" + t, "MIS" + t, note="scarica il tempo massimo")
        sch_g.append(("TR" + t, "TON" + t))
        cv.diode(d, "PZ" + t, "CK" + t, note="NOTA: OR a diodi")
        cv.diode(d, "TO" + t, "CK" + t)
        d.R("CK" + t, "CTRL_GND", "100k")
        d.R("+5VF", "KSW" + t, "10k", note="levetta di kill verso CTRL_GND sulla scheda comandi (chiusa = kill)")
        d.R("KSW" + t, "KD" + t, "10k", note="antirimbalzo 1 ms")
        d.C("KD" + t, "CTRL_GND", "100n")
        ff.append(("KD" + t, "CK" + t, "KQ" + t))
    cmp_pins += [("AGND", "CTRL_GND", "ZCX%d" % k) for k in range(1, 4)]
    for k in range(2):
        q = cmp_pins[4 * k:4 * k + 4]
        p = {"VCC": "+5VF", "GND": "CTRL_GND"}
        for j, (a, bn, o) in enumerate(q, 1):
            p.update({"%dIN+" % j: a, "%dIN-" % j: bn, "%dOUT" % j: o})
        d.part("U", LM339, "LM339DR", SOIC14, p, ref=uref(), note="comparatori dello zero (ingressi riferiti ad AGND)")
        d.C("+5VF", "CTRL_GND", "100n")
    for k in range(1, 4):
        d.R("+5VF", "ZCX%d" % k, "10k", note="uscita libera")
    xor_g += [("CTRL_GND", "CTRL_GND", None)]
    while xor_g:
        q, xor_g = xor_g[:4], xor_g[4:]
        p = {"VCC": "+5VF", "GND": "CTRL_GND"}
        for j, (a, bn, o) in enumerate(q + [("CTRL_GND", "CTRL_GND", None)] * (4 - len(q)), 1):
            p.update({"%dA" % j: a, "%dB" % j: bn, "%dY" % j: o})
        d.part("U", HC86, "74HC86PW", TSSOP14, p, ref=uref(), note="fronti, confronto levetta/stato, inversione del tempo massimo")
        d.C("+5VF", "CTRL_GND", "100n")
    while sch_g:
        q, sch_g = sch_g[:6], sch_g[6:]
        p = {"VCC": "+5VF", "GND": "CTRL_GND"}
        for j, (a, o) in enumerate(q + [("CTRL_GND", None)] * (6 - len(q)), 1):
            p.update({"%dA" % j: a, "%dY" % j: o})
        d.part("U", HC14, "74HC14PW", TSSOP14, p, ref=uref(), note="ritardo del fronte e tempo massimo (Schmitt)")
        d.C("+5VF", "CTRL_GND", "100n")
    ff.append(("CTRL_GND", "CTRL_GND", None))
    while ff:
        q, ff = ff[:2], ff[2:]
        p = {"VCC": "+5VF", "GND": "CTRL_GND"}
        for j, (dd, ck, qq) in enumerate(q, 1):
            p.update({"%dD" % j: dd, "%dCLK" % j: ck, "%dQ" % j: qq, "%dQN" % j: None, "%dPRE" % j: "+5VF", "%dCLR" % j: "+5VF"})
        d.part("U", HC74, "74HC74PW", TSSOP14, p, ref=uref(), note="stato del kill: copia la levetta sull'IN dell'ADG")
        d.C("+5VF", "CTRL_GND", "100n")

if PARTE == "B":
    # ------------------------------------------------------------ celle
    CELLE = [  # (C, R di Ictl, shaper (Rm, Ra1, Rb1, Ra2, Rb2, Ra3, Rb3)) — fiveway.POSIZIONE
        ("680n", "117k", ("24k3", "36k5", "267k", "22k1", "57k6", "13k0", "20k5")),    # EQ1 20-120 Hz (x6)
        ("180n", "110k", ("27k4", "47k5", "340k", "30k1", "76k8", "18k7", "28k7")),    # EQ2 80-400 (x5)
        ("56n", "113k", ("24k3", "36k5", "267k", "22k1", "57k6", "13k0", "20k5")),     # EQ3 250-1500 (x6)
        ("18n", "110k", ("23k7", "34k8", "255k", "20k5", "53k6", "12k1", "18k7")),     # EQ4 800-5000 (x6,25)
        ("4n7", "113k", ("23k2", "32k4", "232k", "18k7", "48k7", "10k7", "16k9")),     # EQ5 3k-20k (x6,67)
    ]
    # celle 3-5 (solo SMD) sul retro: davanti non trovano posto (dec. 142). POSITION davanti: sul
    # retro, con le celle, lasciava 3-8 aperti negli shaper (giro 3)
    d.block = "POSITION: shaper a diodi per banda e riferimento di drain 0,1 V dei replica (REV todo 50)"
    PL = Pack("+15LN", "-15LN")
    d.R("+REF5", "VRDD", "49k9 0.1%", note="Vds dei replica: 5 x 1,02/50,92 = 0,1002 V")
    d.R("VRDD", "AGND", "1k02 0.1%")
    PL.add(("VRDD", "VRD", "VRD"))
    for n, (c, ric, sh) in enumerate(CELLE, 1):
        t = str(n)
        d.R("POSW" + t, "AGND", "100k", note="pot staccato = inizio corsa")
        PL.add(("POSW" + t, "POSX" + t, "POSX" + t))
        rm, ra1, rb1, ra2, rb2, ra3, rb3 = sh
        d.R("POSX" + t, "SJ" + t, rm + " 0.1%", note="shaper_fit.py: f = lo (hi/lo)^theta, entro +-1 % a 35 C" if n == 1 else "")
        for k, (ra, rb) in enumerate(((ra1, rb1), (ra2, rb2), (ra3, rb3)), 1):
            nn = "SN%d_%s" % (k, t)
            d.R("POSX" + t, nn, ra + " 0.1%")
            d.R(nn, "-REF5", rb + " 0.1%")
            cv.diode(d, nn, "SJ" + t)
        d.R("+REF5", "SJ" + t, "49k9 0.1%", note="offset: -1 V a inizio corsa (Ictl minima)")
        d.R("SJ" + t, "SH" + t, "10k 0.1%")
        PL.add(("AGND", "SJ" + t, "SH" + t))
    PL.flush("buffer del pot POSITION, shaper, riferimento di drain")


    def cella(n, c, ric):
        t = str(n)
        vin = SUM if n == 1 else "E%d" % (n - 1)
        out = "E%d" % n
        P = Pack()
        # summer: ingresso 40,2k, LP 10k, damping da -dq 30k, Rf 10k
        d.R(vin, "NS" + t, "40k2 0.1%")
        d.R("LPB" + t, "NS" + t, "10k 0.1%")
        d.R("NDQ" + t, "NS" + t, "30k1 0.1%", note="damping R0: Q = 0,3/alpha (§4.3)")
        d.R("NS" + t, "HP" + t, "10k 0.1%")
        P.add(("AGND", "NS" + t, "HP" + t))
        # due integratori a JFET bootstrappato, ognuno col suo replica nello stesso dual
        for k, (src, st, stb) in enumerate((("HP" + t, "BP" + t, "BPB" + t), ("BPB" + t, "LP" + t, "LPB" + t)), 1):
            tk = "%s_%d" % (t, k)
            d.part("Q", JDUAL, "LSK389 (dual)", SOIC8,
                   {"D1": src, "G1": "GS" + tk, "S1": "NI" + tk, "D2": "VRD", "G2": "GR" + tk, "S2": "SV" + tk, "SS1": None, "SS2": None},
                   note="JFET di segnale (1) e replica (2) nello stesso die (REV todo 50); bin Idss/Vp")
            d.R(src, "GS" + tk, "100k 0.1%", note="gate a (Vd + vc2)/2")
            d.R("VC" + tk, "GS" + tk, "100k 0.1%")
            Cx("NI" + tk, st, c, note="Cint" if k == 1 else "")
            P.add(("AGND", "NI" + tk, st))
            P.add((st, stb, stb))
            # servo replica: Ictl = -SH/R dal nodo SV; integratore 100n
            d.R("VRD", "GR" + tk, "100k 0.1%")
            d.R("VC" + tk, "GR" + tk, "100k 0.1%")
            d.R("SV" + tk, "SH" + t, ric + " 0.1%", note="Ictl = |SH|/R: f0 proporzionale (replica-a.cir)")
            Cx("SV" + tk, "VC" + tk, "100n")
            P.add(("AGND", "SV" + tk, "VC" + tk))
        # WIDTH: pot 1k sul cavo fra BPB e WB, 110 ohm a massa; x10 e invertitore (OPA1612)
        d.R("WB" + t, "AGND", "110 0.1%", note="alpha minima 0,099 (Q 3,0)")
        d.R("DQ" + t, "NW" + t, "1k8 0.1%")
        d.R("NW" + t, "AGND", "200 0.1%", note="x10")
        d.R("DQ" + t, "NIQ" + t, "2k 0.1%")
        d.R("NIQ" + t, "NDQ" + t, "2k 0.1%")
        opa2(("WW" + t, "NW" + t, "DQ" + t), ("AGND", "NIQ" + t, "NDQ" + t), note="WIDTH: x10 e invertitore (§4.3)")
        # GAIN: pot fra DQ e NDQ sul cavo, cursore GW; iniezione 1,62k; somma d'uscita unity
        d.R("GW" + t, "NS2" + t, "1k62 0.1%")
        d.R(vin, "NS2" + t, "10k 0.1%")
        d.R("NS2" + t, out, "10k 0.1%")
        P.add(("AGND", "NS2" + t, out))
        P.flush("cella %d: summer, integratori, buffer, servo replica, uscita" % n)


    for n, (c, ric, _) in enumerate(CELLE, 1):
        d.side = "B" if n >= 3 else "F"
        d.block = "CELLA %d (v0.2.2, §4.2-4.3)" % n
        cella(n, c, ric)
    d.side = "F"

    # ------------------------------------------------------------ GROWL
    d.block = "GROWL A BANDE (dec. 165, 175; growl-bande.cir, module-noise-b9.cir)"
    P = Pack()
    for tg, a, z in (("GA", "E5", "GLP1"), ("GB", "GLP1", "GLOW")):
        d.R(a, tg + "1", "9k31 0.1%", note="NOTA: LP 250 Hz con C E12 100n/47n e R 9,31k (Q 0,73)" if tg == "GA" else "")
        d.R(tg + "1", tg + "2", "9k31 0.1%")
        Cx(tg + "1", z, "100n")
        Cx(tg + "2", "AGND", "47n")
        P.add((tg + "2", z, z))
    d.R("E5", "GRP", "10k 0.1%")
    d.R("GRP", "AGND", "10k 0.1%")
    d.R("GLOW", "GRN", "10k 0.1%")
    d.R("GRN", "GREST", "10k 0.1%")
    P.add(("GRP", "GRN", "GREST"))
    d.R("GREST", "GMC", "9k31 0.1%")
    Cx("GMC", "AGND", "6n8", note="polo 2,5 kHz (9,31k / 6,8n = 2,51 kHz)")
    P.add(("GMC", "GMID", "GMID"))
    # clipper dei bassi: spinta = reostato sul cavo (GLOW -> GLR) + 1k fisso; Rf 47k; 1 / 3 diodi con 470R
    d.R("GLR", "GLGN", "1k 0.1%", note="spinta dei bassi: 1k + reostato 10k sul cavo (11k -> 1k, NOTA)")
    d.R("GLGN", "GLOUT", "47k")
    cv.diode(d, "GLGN", "GLA1")
    d.R("GLA1", "GLOUT", "470")
    cv.diode(d, "GLOUT", "GLB1")
    cv.diode(d, "GLB1", "GLB2")
    cv.diode(d, "GLB2", "GLB3")
    d.R("GLB3", "GLGN", "470")
    P.add(("AGND", "GLGN", "GLOUT"))
    # clipper dei medi: spinta = 4,99k + reostato 5k sul cavo (10k -> 5k); Rf 10k; 3 + 3 diodi con 4,7k
    d.R("GMR", "GMGN", "4k99 0.1%", note="spinta dei medi: 4,99k + reostato 5k sul cavo")
    d.R("GMGN", "GMOUT", "10k")
    cv.diode(d, "GMGN", "GMA1"); cv.diode(d, "GMA1", "GMA2"); cv.diode(d, "GMA2", "GMA3")
    d.R("GMA3", "GMOUT", "4k7")
    cv.diode(d, "GMOUT", "GMB1"); cv.diode(d, "GMB1", "GMB2"); cv.diode(d, "GMB2", "GMB3")
    d.R("GMB3", "GMGN", "4k7")
    P.add(("AGND", "GMGN", "GMOUT"))
    # miscela: bassi e medi puliti meno, saturi piu' (kbl 0,9, kbm 0,501), con blocco della continua
    d.C("GLOUT", "GLAC", "22u NP", CNP, note="NOTA: 22u bipolare (sim 14,3u): polo < 1 Hz")
    d.R("GLAC", "GDN", "11k1 0.1%")
    d.C("GMOUT", "GMAC", "10u NP", CNP, note="NOTA: 10u bipolare (sim 8u)")
    d.R("GMAC", "GDN", "20k 0.1%")
    d.R("GLOW", "GDN", "10k 0.1%")
    d.R("GMID", "GDN", "10k 0.1%")
    d.R("GDN", "DDG", "10k 0.1%")
    P.add(("AGND", "GDN", "DDG"))
    # pot GROWL, tratto della miscela (10k sul cavo: DDG - DWG - AGND) e buffer
    d.R("DWG", "AGND", "1M", note="pot staccato = GROWL a zero")
    P.add(("DWG", "DBG", "DBG"))
    P.flush("GROWL: LP, resto, medi, clipper, miscela, buffer")
    d.R("E5", "DS1N", "2k2 0.1%")
    d.R("DBG", "DS1N", "2k2 0.1%")
    d.R("DS1N", "DY1", "2k2 0.1%")

    # ------------------------------------------------------------ NASTRO
    d.block = "NASTRO A BANDE B9 (dec. 166, 175; nastro-b9.cir, module-noise-b9.cir)"
    P = Pack()
    prev = "DY1"
    for k in (1, 2, 3):        # enfasi: 3 x (zero 30 / polo 140 Hz), rel 36,5k // 150n
        t = "NE%d" % k
        d.R(prev, t, "36k5 0.1%", note="NOTA: 150n E12 (sim 144,7n): fz 28,9 Hz" if k == 1 else "")
        Cx(prev, t, "150n")
        d.R(t, "AGND", "10k 0.1%")
        P.add((t, "NU%d" % k, "NU%d" % k))
        prev = "NU%d" % k
    d.R("NU3", "NE4", "2k 0.1%", note="taglio dei super: polo 10,8k / zero 9k")
    d.R("NE4", "NE4C", "10k 0.1%")
    Cx("NE4C", "AGND", "1n5")
    P.add(("NE4", "NU4", "NU4"))
    d.R("NU4", "NUS", "20k 0.1%", note="inclinazione dei medi (fmt 1 kHz, rt 3)")
    d.R("NUS", "NE5C", "10k 0.1%")
    Cx("NE5C", "AGND", "5n1")
    # spinta non invertente: Rg 1k, Rf = reostato sul cavo (LSP - LSN) con 7,5k in parallelo
    d.R("LSN", "AGND", "1k 0.1%")
    d.R("LSP", "LSN", "7k5", note="NOTA: reostato 5k // 7,5k = 0..3,0k (+12 dB a fine corsa)")
    P.add(("NUS", "LSN", "LSP"))
    # JFET J310 a sorgente comune
    d.R("LSP", "LGATE", "10k")
    d.part("Q", "Transistor_FET:MMBFJ113", "MMBFJ310", SOT23, {"D": "LDRAIN", "G": "LGATE", "S": "LJS1"},
           note="NJ310 in sim; simbolo MMBFJ113 (1 D, 2 S, 3 G) = MMBFJ310L onsemi, SOT-23 case 318 style 10 (todo 339)")
    d.R("+18V", "LDRAIN", "1k5")
    d.R("LJS1", "LJS2", "150")
    d.R("LJS2", "AGND", "910", note="sim 900")
    d.CP("LJS2", "AGND", "2200u 10V", "Capacitor_THT:CP_Radial_D10.0mm_P5.00mm")
    d.CP("LDRAIN", "LTAC", "10u 25V", "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm")
    d.R("LTAC", "LTN", "48k7", note="10k/kt, kt 0,206 (dispersione del JFET: trim a banco, §5bis.6)")
    d.R("LTN", "NWN", "9k53", note="10k kl/kt")
    P.add(("AGND", "LTN", "NWN"))
    # de-enfasi
    d.R("NWN", "ND1", "4k87 0.1%")
    d.R("ND1", "ND1C", "10k 0.1%")
    Cx("ND1C", "AGND", "1n8")
    d.R("NW2", "ND2N", "20k 0.1%")
    d.R("ND2N", "ND2C", "10k 0.1%")
    Cx("ND2C", "AGND", "5n1")
    P.add(("ND1", "ND2N", "NW2"))
    prev = "NW2"
    for k in (3, 4, 5):
        t = "ND%dN" % k
        o = "NW" if k == 5 else "NW%d" % k
        d.R(t, "AGND", "10k 0.1%")
        d.R(o, t, "19k6 0.1%", note="NOTA: 180n E12 (sim 172n): fp 134 Hz" if k == 3 else "")
        Cx(o, t, "180n")
        P.add((prev, t, o))
        prev = o
    # differenza d = kv w - y1
    d.R("NW", "NXP", "10k 0.1%")
    d.R("NXP", "AGND", "4k99 0.1%", note="kv = -3,5 dB")
    d.R("DY1", "NXN", "10k 0.1%")
    d.R("NXN", "DSEL", "10k 0.1%")
    P.add(("NXP", "NXN", "DSEL"))
    # pot NASTRO, tratto della miscela: 1,8k fisso + pot 10k sul cavo (DTP - DWT - AGND)
    d.R("DSEL", "DTP", "1k8", note="mt = 0,85 a fine corsa")
    d.R("DWT", "AGND", "1M", note="pot staccato = NASTRO a zero")
    P.add(("DWT", "DBT", "DBT"))
    P.flush("NASTRO: enfasi, spinta, uscita del JFET, de-enfasi, differenza, buffer")
    d.R("DY1", "DS2N", "2k2 0.1%")
    d.R("DBT", "DS2N", "2k2 0.1%")
    d.R("DS2N", "DY2", "2k2 0.1%")
    opa2(("AGND", "DS1N", "DY1"), ("AGND", "DS2N", "DY2"), note="sommatori di GROWL e NASTRO (OPA1612, 2,2k)")
    d.R("DY2", "EDRV", "33")

    # ------------------------------------------------------------ uscita
    d.block = "MAKE-UP +6 dB, servo DC (§5bis.7) e uscita verso MSUM1"
    d.R("EDRV", "NMU", "10k 0.1%")
    d.R("NMU", "VOUT", "20k 0.1%")
    d.R("VOUT", "SVI", "1M")
    Cx("SVI", "SVO", "100n", note="integratore 1M / 100n film")
    d.R("SVO", "MUP", "100k")
    d.R("MUP", "AGND", "1k", note="partitore del servo: corsa +-385 mV")
    opa2(("MUP", "NMU", "VOUT"), ("AGND", "SVI", "SVO"), note="make-up (A) e servo DC (B, FET)", value="OPA1642AIDR")
    d.R("VOUT", "5W_OUT_" + s, "47", note="NOTA: 47R verso MSUM1 (20k sul master); ponticello J5W sul backplane")
    d.R("EDRV", "5W_MET_" + s, "100", note="presa del meter verso i LED di livello sulla scheda comandi")

# ------------------------------------------------------------ cavo
d.block = "CAVO SCHEDA COMANDI (J2)"


def fili_cavo(s, parte):
    """Ordine dei fili di J2. Letta anche da five-way-comandi.py (comandi.funzione_da): una fonte
    sola, i due connettori non possono divergere. Solo letterali qui dentro."""
    if parte == "A":
        fili = ["KSW1", "KSW2", "KSW3", "KSW4", "KSW5", "CTRL_GND"]
    else:
        fili = ["AGND", "+REF5"]
        for n in range(1, 6):
            t = str(n)
            fili += ["POSW" + t, "BPB" + t, "WW" + t, "WB" + t, "DQ" + t, "GW" + t, "NDQ" + t, "AGND"]
        fili += ["DDG", "DWG", "GLOW", "GLR", "GMID", "GMR", "AGND",
                 "DTP", "DWT", "LSP", "LSN", "AGND", "5W_MET_" + s, "AGND"]
        if s == "L":   # alimentazione dei LED di livello sulla scheda comandi
            fili += ["+15LN", "AGND", "-15LN", "+5VF", "CTRL_GND"]
    if len(fili) % 2:
        fili.append("AGND")
    return fili


FILI = fili_cavo(s, PARTE)
cv.cavo(d, FILI, x=L / 2 - 40 if PARTE == "B" else L / 2 - 20, y=14)

d.audio_rules = {}

if __name__ == "__main__":
    d.build(route="--no-route" not in sys.argv)
