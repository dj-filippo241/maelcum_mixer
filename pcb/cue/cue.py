"""CUE / cuffie, scheda di SEGNALE col C96 (todo 294). Bozza v0.1.

Catena (docs/fase3/sistema-cue.md v0.2, §2-§8):
 CUE1-4 L/R (slot 1-4) -> 10k -> [A] somma a massa virtuale (Rf 10k, -1) ----------- CS -+
 MON L/R (slot 5, dal buffer [N] del master) -> [B] buffer INVERTENTE 20k/20k (-1) -- MB -+
   -> [C] BLEND (pot doppio 10k lin con scatto, scheda comandi) -> BL -> buffer [C2] -> BLB
   -> [D] LEVEL (pot doppio 10k log, antiorario = massa) -> LV
   -> [E] ampli cuffia v0.2 (OPA1612 + diamond MJE340/350, gain +1, +-18 locali)
   -> [F] Rserie 10 ohm 2 W per jack -> rele' DPDT (uno per jack) -> cavo J3 -> 2 jack sulla
      scheda comandi.
 [G] protezione locale: finestre sui raw +-22 e +-27 + timer 1,8 s -> rele'. Il CUE NON ascolta
     c9 (scelta di Filippo 2026-10-02, §6).

Polarità (sistema-polarita.md, F4): somma -1; buffer MON -1 (REV 2026-11-03: invertente, perché
a [A2] il canale arriva gia' rovesciato dal ricevitore del DJ bus). Al centro del blend lo stesso
programma si somma.

Scelte non scritte nel design doc, segnate NOTA (pcb/cue/NOTE.md):
- le 10k d'iniezione stanno qui: il canale esce con 47 ohm dopo lo switch (canale.py, slot 2);
- buffer [C2] fra BLEND e LEVEL: senza, il LEVEL da 10k carica il cursore del BLEND (fino a
  2,5k) e il centro scende a -8 dB per parte invece dei -6 bloccati (§5);
- 4 resistenze Rserie (una per ramo-jack, come il diagramma §2), non 8 (BOM §10);
- jack sulla scheda comandi, con un cavo loro (J3) e un ritorno loro (HPG): la corrente della
  cuffia non passa sulla massa dei pot.
Rail: [A]-[D] su +-15 LN (LM317/337 a +-16,5 dal raw +-22, poi LT3045/LT3094); [E] su +-18
locali (LM317/337 dal raw +-27 + bulk 1000 uF). Valori [PROVVISORIO].
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from pcbgen import DesignRiprova
from backplane import c96, SYM_C96, FP_C96, C96_DAL_BORDO

L, H = 196, 124        # pcb/PIANO-SCHEDE-F.md: CUE, sinistra-destra; 177 mm al giro 1 (113 aperti), ora tutto il pannello
d = DesignRiprova("cue", HERE, "maelcum CUE / cuffie (sistema-cue v0.2) - bozza v0.1", board=(L, H), rev="0.1-bozza")
d.gnd = "AGND"
d.link_pairs = True       # pad gemelli: C96, linguetta dei SOT-223, cursore e capo dei trimmer
d.link_pairs_masse = True   # anche CTRL_GND (a23-a24, c16-c28): giro 1, 20 aperti su CTRL_GND (come il canale)
d.inner_signal = True       # SMD sui due lati: In2 strato di piste, massa piena su In1 (giro 1: 113 aperti)
d.fanout_more = True        # via di massa anche di traverso

SOIC8 = "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"
SOIC14 = "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm"
SOT23 = "Package_TO_SOT_SMD:SOT-23"
SOT323 = "Package_TO_SOT_SMD:SOT-323_SC-70"
C12 = "Capacitor_SMD:C_1206_3216Metric"
R12 = "Resistor_SMD:R_1206_3216Metric"
OPA = "Amplifier_Operational:OPA1612AxD"
TO126 = "Package_TO_SOT_THT:TO-126-3_Vertical"
TRIM = "Potentiometer_THT:Potentiometer_Bourns_3266W_Vertical"
R2W = "Resistor_THT:R_Axial_DIN0414_L11.9mm_D4.5mm_P15.24mm_Horizontal"
FB = "Inductor_SMD:L_1206_3216Metric"
DIO = ("Diode:1N4148W", "1N4148W", "Diode_SMD:D_SOD-123")

FILI = ["CS_L", "AGND", "MB_L", "BL_L", "BLB_L", "AGND", "LV_L",
        "CS_R", "AGND", "MB_R", "BL_R", "BLB_R", "AGND", "LV_R"]
# J2, cavo dei pot verso la scheda comandi (letto da cue-comandi.py: una fonte sola).
# AGND fra i gruppi e mai su due pin vicini (Freerouting non li collega).
CUFFIE = ["HP1_T", "HPG", "HP1_R", "HP2_T", "HPG", "HP2_R"]
# J3, cavo delle cuffie verso i due jack della scheda comandi; HPG = ritorno delle cuffie.


def opa(ref, a, b, vp="+15LN", vm="-15LN", note=""):
    """OPA1612 doppio. a, b = (ingresso +, ingresso -, uscita) delle due sezioni."""
    d.part("U", OPA, "OPA1612AIDR", SOIC8, {3: a[0], 2: a[1], 1: a[2], 5: b[0], 6: b[1], 7: b[2],
                                            8: vp, 4: vm}, ref=ref, note=note)
    d.C(vp, "AGND", "100n")
    d.C("AGND", vm, "100n")


# ------------------------------------------------------------ backplane
d.block = "BACKPLANE C96 (classe CUE: slot 1-4 = CUE1-4 in, slot 5 = MON in)"
b = {}
for k, n in enumerate(["CUE1", "CUE2", "CUE3", "CUE4", "MON"]):
    b["b%d" % (3 * k + 1)] = n + "_L"
    b["b%d" % (3 * k + 2)] = n + "_R"
    b["b%d" % (3 * k + 3)] = "AGND"
# RAW+-26 (a9-a12) solo per il master; c9 (GLOBAL_MUTE) NON collegato: il CUE non lo ascolta (§6, §8)
d.part("J", SYM_C96, "C96 maschio", FP_C96, c96(b), ref="J1", place=(L / 2, H - C96_DAL_BORDO, 180),
       note="DIN 41612 C 3x32, angolo retto; c9 libero per scelta (sistema-cue §6)")
for ref, x in (("H1", 5), ("H2", L - 5)):
    d.part("H", "Mechanical:MountingHole_Pad", "CHASSIS", "MountingHole:MountingHole_3.2mm_M3_Pad",
           {1: "CHASSIS"}, ref=ref, place=(x, 5, 0), note="foro di fissaggio, a CHASSIS")

# ------------------------------------------------------------ alimentazione
d.power_nets("RAW+27", "RAW-27", "RAW+22", "RAW-22", "AGND", "CHASSIS", width=0.8)
d.power_nets("+18V", "-18V", "V27F+", "V27F-", width=0.8)       # fino a ~340 mA col clamp (§8)
d.power_nets("+5V", "CTRL_GND", width=0.5)
d.power_nets("V22F+", "V22F-", "+16V5", "-16V5", "+15LN", "-15LN", width=0.4)
MSE = "Package_SO:MSOP-12-1EP_3x4.039mm_P0.65mm_EP1.651x2.845mm"

d.block = "ALIMENTAZIONE +18 audio (LM317 dal raw +27, bulk 1000 uF)"
d.part("FB", "Device:FerriteBead_Small", "ferrite 600R 2A", FB, {1: "RAW+27", 2: "V27F+"})
d.CP("V27F+", "AGND", "220u 35V")
d.part("U", "Regulator_Linear:LM317_TO-220", "LM317", "Package_TO_SOT_THT:TO-220-3_Vertical",
       {"VI": "V27F+", "VO": "+18V", "ADJ": "ADJ18+"}, ref="U40", note="+18 V dell'ampli cuffia: 61 mA a riposo, ~0,55 W")
d.R("+18V", "ADJ18+", "120 1%")
d.R("ADJ18+", "AGND", "1k62 1%", note="18,1 V (come master-uscita.py)")
d.CP("ADJ18+", "AGND", "10u 35V", "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm")
d.CP("+18V", "AGND", "1000u 25V", "Capacitor_THT:CP_Radial_D10.0mm_P5.00mm", note="bulk locale dei finali (§5)")
d.part("D", DIO[0], DIO[1], DIO[2], {"K": "+18V", "A": "ADJ18+"}, note="scarica Cadj")
d.part("D", "Device:D", "S1G", "Diode_SMD:D_SMA", {"K": "V27F+", "A": "+18V"}, note="protezione inversa (bulk 1000 uF)")

d.block = "ALIMENTAZIONE -18 audio (LM337 dal raw -27, bulk 1000 uF)"
d.part("FB", "Device:FerriteBead_Small", "ferrite 600R 2A", FB, {1: "RAW-27", 2: "V27F-"})
d.CP("AGND", "V27F-", "220u 35V")
d.part("U", "Regulator_Linear:LM337_TO220", "LM337", "Package_TO_SOT_THT:TO-220-3_Vertical",
       {"VI": "V27F-", "VO": "-18V", "ADJ": "ADJ18-"}, ref="U41")
d.R("-18V", "ADJ18-", "120 1%")
d.R("ADJ18-", "AGND", "1k62 1%")
d.CP("AGND", "ADJ18-", "10u 35V", "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm")
d.CP("AGND", "-18V", "1000u 25V", "Capacitor_THT:CP_Radial_D10.0mm_P5.00mm")
d.part("D", DIO[0], DIO[1], DIO[2], {"A": "-18V", "K": "ADJ18-"})
d.part("D", "Device:D", "S1G", "Diode_SMD:D_SMA", {"A": "V27F-", "K": "-18V"})

d.block = "ALIMENTAZIONE +15 LN (LM317 a +16,5 dal raw +22, poi LT3045)"
d.part("FB", "Device:FerriteBead_Small", "ferrite 600R", FB, {1: "RAW+22", 2: "V22F+"})
d.CP("V22F+", "AGND", "47u 35V", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm")
d.part("U", "Regulator_Linear:LM317_SOT-223", "LM317", "Package_TO_SOT_SMD:SOT-223-3_TabPin2",
       {"VI": "V22F+", "VO": "+16V5", "ADJ": "ADJ16+"}, ref="U42", note="pre-regolatore (§2: +-16,5); ~25 mA")
d.R("+16V5", "ADJ16+", "120 1%")
d.R("ADJ16+", "AGND", "1k47 1%", note="16,6 V")
d.C("+16V5", "AGND", "10u 25V", C12)
d.part("U", "Regulator_Linear:LT3045xMSE", "LT3045EMSE", MSE, {
    1: "+16V5", 2: "+16V5", 3: "+16V5", 4: "+16V5", 5: None, 6: "AGND", 7: "+16V5", 8: "SETP",
    9: "AGND", 10: "+15LN", 11: "+15LN", 12: "+15LN", 13: "AGND"}, ref="U44",
    note="EN/UV a IN; ILIM a massa; PG libero; PGFB a IN (come master-segnale.py)")
d.netclass["SETP"] = 0.3
d.R("SETP", "AGND", "150k 0.1%")
d.C("SETP", "AGND", "4u7 25V", C12, note="rumore del riferimento (datasheet: 4,7 uF)")
d.C("+16V5", "AGND", "4u7 25V", C12)
d.C("+15LN", "AGND", "10u 25V", C12)

d.block = "ALIMENTAZIONE -15 LN (LM337 a -16,5 dal raw -22, poi LT3094)"
d.part("FB", "Device:FerriteBead_Small", "ferrite 600R", FB, {1: "RAW-22", 2: "V22F-"})
d.CP("AGND", "V22F-", "47u 35V", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm")
d.part("U", "Regulator_Linear:LM337_SOT223", "LM337", "Package_TO_SOT_SMD:SOT-223-3_TabPin2",
       {"VI": "V22F-", "VO": "-16V5", "ADJ": "ADJ16-"}, ref="U43")
d.R("-16V5", "ADJ16-", "120 1%")
d.R("ADJ16-", "AGND", "1k47 1%")
d.C("AGND", "-16V5", "10u 25V", C12)
d.part("U", "Regulator_Linear:LT3094xMSE", "LT3094EMSE", MSE, {
    1: "-16V5", 2: "-16V5", 13: "-16V5", 3: "-16V5", 4: None, 5: "-16V5", 6: "AGND", 7: None, 8: "SETN",
    9: "AGND", 10: "-15LN", 11: "-15LN", 12: "-15LN"}, ref="U45",
    note="EN/UV a IN; PG libero; PGFB a IN; ILIM a massa; VIOC libero")
d.netclass["SETN"] = 0.3
d.R("SETN", "AGND", "150k 0.1%")
d.C("AGND", "SETN", "4u7 25V", C12)
d.C("AGND", "-16V5", "4u7 25V", C12)
d.C("AGND", "-15LN", "10u 25V", C12)

# ------------------------------------------------------------ [A] somma CUE, [B] buffer MON
d.block = "[A] CUE SUMMING L/R (massa virtuale, Rf 10k, -1) e [B] MON (invertente 20k/20k, F4)"
for s in ("L", "R"):
    for k in range(1, 5):
        d.R("CUE%d_%s" % (k, s), "NS_" + s, "10k 0.1%",
            note="NOTA: iniezione 10k qui; il canale esce con 47 ohm dopo lo switch (canale.py)")
    d.R("NS_" + s, "CS_" + s, "10k 0.1%")
    d.C("NS_" + s, "CS_" + s, "10p C0G", note="NOTA: come i ricevitori dei bus (Cf 10 pF)")
opa("U1", ("AGND", "NS_L", "CS_L"), ("AGND", "NS_R", "CS_R"), note="[A] somma dei cue")
for s in ("L", "R"):
    d.R("MON_" + s, "NMB_" + s, "20k 0.1%", note="REV 2026-11-03 (F4): buffer MON invertente")
    d.R("NMB_" + s, "MB_" + s, "20k 0.1%")
    d.C("NMB_" + s, "MB_" + s, "10p C0G")
opa("U2", ("AGND", "NMB_L", "MB_L"), ("AGND", "NMB_R", "MB_R"), note="[B] MON dal master, -1")

d.block = "[C2] buffer fra BLEND e LEVEL (NOTA: tiene la law del blend esatta)"
for s in ("L", "R"):
    d.R("BL_" + s, "AGND", "1M", note="tiene l'ingresso a massa a cavo staccato")
opa("U3", ("BL_L", "BLB_L", "BLB_L"), ("BL_R", "BLB_R", "BLB_R"),
    note="inseguitori: il LEVEL da 10k non carica il cursore del BLEND (centro -6 dB per parte)")

# ------------------------------------------------------------ [E] ampli cuffia v0.2
d.side = "F"


def ampli(s):
    """Un lato dell'ampli cuffia v0.2 (sim/system/cue-hp-load.cir); l'op-amp è U4 (sotto).
    Pinout BJT C-B-E; MJE340/350 con l'impronta del BD139/140
    (TO-126, stessa piedinatura E-C-B), come master-uscita.py."""
    lv, fb, uo, nb, pb = "LV_" + s, "FB_" + s, "UO_" + s, "NB_" + s, "PB_" + s
    out, en, ep = "OUTA_" + s, "EN_" + s, "EP_" + s
    d.netclass[out] = 0.6
    d.netclass[en] = 0.6
    d.netclass[ep] = 0.6
    d.R(lv, "AGND", "1M", note="NOTA: tiene l'ingresso a massa a cavo staccato (il cursore del LEVEL basta in uso)")
    d.R(out, fb, "470 1%", note="Rf: retroazione DC da OUTA, prima della Rserie")
    d.C(uo, fb, "330p C0G", note="Cf: incrocio dell'anello esterno ~1 MHz")
    d.R(uo, nb, "1k 1%", note="Rdrv: isola l'op-amp e fissa la corrente che i limitatori vincono")
    # moltiplicatore di Vbe fra le due basi (C = PB, B = TAP, E = NB), 210 ohm nominali = 20 mA
    d.part("Q", "Transistor_BJT:BC847", "BC847B", SOT23, {"C": pb, "B": "TAP_" + s, "E": nb},
           note="moltiplicatore di Vbe: vicino ai finali per l'inseguimento termico (§12)")
    d.R(pb, "RT_" + s, "1k 1%")
    d.part("RV", "Device:R_Potentiometer_Trim", "500", TRIM, {1: "RT_" + s, 2: "TAP_" + s, 3: "TAP_" + s},
           note="trimmer del riposo: 210 ohm = 20 mA (si tara a banco, §12)")
    d.R("TAP_" + s, nb, "1k 1%")
    d.C(pb, nb, "1u film", "Capacitor_THT:C_Rect_L7.2mm_W3.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2",
        note="Cb, film (WIMA MKS2 o simile)")
    # generatori di corrente a JFET (gate sul source), Idss ~8 mA
    d.part("Q", "Transistor_FET:BF245B", "BF245B", "Package_TO_SOT_THT:TO-92_Inline_Wide",
           {"D": "+18V", "G": pb, "S": pb}, note="CRD ~8 mA: Idss da selezionare (BF245B 6-15 mA)")
    d.part("Q", "Transistor_FET:BF245B", "BF245B", "Package_TO_SOT_THT:TO-92_Inline_Wide",
           {"D": nb, "G": "-18V", "S": "-18V"}, note="CRD ~8 mA")
    d.R(pb, "BN_" + s, "22", note="base stopper")
    d.R(nb, "BP_" + s, "22")
    d.part("Q", "Transistor_BJT:BD139", "MJE340", TO126, {"C": "+18V", "B": "BN_" + s, "E": en},
           note="finale +: 0,35 W a riposo, ~3 W in corto; rame >= 4 cm2 (§5)")
    d.part("Q", "Transistor_BJT:BD140", "MJE350", TO126, {"C": "-18V", "B": "BP_" + s, "E": ep},
           note="finale -; rame >= 4 cm2")
    d.R(en, out, "6.8 1%", R12, note="Re: stabilità termica e senso della corrente")
    d.R(ep, out, "6.8 1%", R12)
    # limitatori di Vbe sui Re (clamp 126-168 mA)
    d.R(en, "BLN_" + s, "100")
    d.part("Q", "Transistor_BJT:BC847", "BC847B", SOT23, {"C": pb, "B": "BLN_" + s, "E": out}, note="limitatore +")
    d.R(ep, "BLP_" + s, "100")
    d.part("Q", "Transistor_BJT:BC857", "BC857B", SOT23, {"C": nb, "B": "BLP_" + s, "E": out}, note="limitatore -")
    d.C("+18V", "AGND", "100n", note="ai collettori dei finali")
    d.C("AGND", "-18V", "100n")
    # [F] Rserie fuori anello, una per jack (niente capacità su OUTA prima della Rserie: §5).
    # Blocco a sé: con le R da 2 W dentro, il blocco dell'ampli diventava largo 193 mm
    d.block = "[F] RSERIE %s (10 ohm 2 W, una per jack)" % s
    for j in (1, 2):
        d.R(out, "RS%d_%s" % (j, s), "10 2W", R2W, note="Rserie del jack %d: isola i due jack, stabilità sul carico" % j)


# Un OPA1612 per lato, dentro il blocco del suo ampli (NOTA, pcb/cue/NOTE.md punto 10): con un
# chip solo per L e R il grappolo legava al chip i 28 passivi dei due ampli e il blocco finiva
# fuori scheda (giri 1-2, 97-113 aperti). Seconda sezione libera: inseguitore a massa.
for s, u in (("L", "U4"), ("R", "U8")):
    d.block = "[E] AMPLI CUFFIA %s (OPA1612 + diamond MJE340/350, v0.2)" % s
    opa(u, ("LV_" + s, "FB_" + s, "UO_" + s), ("AGND", "NU_" + s, "NU_" + s), "+18V", "-18V",
        note="gain +1: retroazione da OUTA (Rf 470), compensazione Cf 330p; sezione B libera")
    ampli(s)

# ------------------------------------------------------------ [F] relè
d.block = "[F] RELE' delle cuffie (G6K-2F, 5 V, 237 ohm; eccitati = suono; failsafe)"
G6K = ("Relay:G6K-2", "G6K-2F DC5", "Relay_SMD:Relay_DPDT_Omron_G6K-2F")
# piedinatura dal datasheet Omron G6K (top view, p. 6), come master-uscita.py:
# 1 bobina +, 8 bobina -; contatto 1: COM 3, NO 4; contatto 2: COM 6, NO 5
for j in (1, 2):
    d.part("K", G6K[0], G6K[1], G6K[2], {1: "+5V", 8: "KD", 3: "RS%d_L" % j, 4: "HP%d_T" % j,
                                        6: "RS%d_R" % j, 5: "HP%d_R" % j, 2: None, 7: None},
           note="PHONES %d: L sulla punta, R sull'anello" % j)
d.part("D", DIO[0], DIO[1], DIO[2], {"A": "KD", "K": "+5V"}, note="scarica delle bobine")
d.R("KG0", "KG", "100")
d.part("Q", "Transistor_FET:AO3400A", "AO3400A", SOT23, {"G": "KG", "S": "CTRL_GND", "D": "KD"},
       note="driver dei relè, logic level")
d.netclass["KD"] = 0.4
d.R("HPG", "AGND", "0", R12, note="NOTA: ritorno delle cuffie (J3) unito ad AGND qui, vicino all'ampli")

# ------------------------------------------------------------ [G] protezione locale
d.side = "B"     # giro 2: la protezione (solo SMD) sul retro, il davanti resta all'ampli
d.block = "[G] PROTEZIONE: finestre sui raw +-22 e +-27, timer 1,8 s (il CUE non ascolta c9)"
d.CP("+5V", "CTRL_GND", "47u 10V", "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm", note="riserva dei relè")
d.R("+5V", "VREF", "1k")
d.part("U", "Reference_Voltage:TL431DBZ", "TL431", SOT23, {"K": "VREF", "REF": "VREF", "A": "CTRL_GND"}, ref="U5",
       note="2,495 V")
# positivi: muto sotto 17 V (+22) e 20 V (+27), come la finestra del master
d.R("RAW+22", "D22", "160k 1%", note="+22 < 17,1 V = muto (§6)")
d.R("D22", "CTRL_GND", "27k4 1%")
d.R("RAW+27", "D27", "160k 1%", note="+27 < 20,2 V = muto (§6)")
d.R("D27", "CTRL_GND", "22k6 1%")
# negativi: partitore fra VREF e il raw; il nodo sale verso VREF quando il raw cala.
# Soglia TH = VREF x 10k / 25k = 1,00 V. -22: 10k/120k, scatta a -17,0 V (nodo 0,61 V a -22).
# -27: 10k/140k, scatta a -20,0 V (nodo 0,53 V a -27). NOTA: calcolo, da simulare.
d.R("VREF", "THN", "15k 1%")
d.R("THN", "CTRL_GND", "10k 1%")
d.R("VREF", "N22", "10k 1%", note="-22 > -17,0 V = muto")
d.R("N22", "RAW-22", "120k 1%")
d.R("VREF", "N27", "10k 1%", note="-27 > -20,0 V = muto")
d.R("N27", "RAW-27", "140k 1%")
for n in ("N22", "N27"):
    d.part("D", "Diode:BAT54W", "BAT54W", SOT323, {"A": "CTRL_GND", "K": n, "NC": None},
           note="+5V spento e raw negativo presente: il nodo non scende sotto -0,3 V")
d.part("U", "Comparator:LM339", "LM339", SOIC14, {
    7: "D22", 6: "VREF", 1: "ROK",       # +22 sotto soglia -> ROK basso
    5: "D27", 4: "VREF", 2: "ROK",       # +27 sotto soglia -> ROK basso
    9: "THN", 8: "N22", 14: "ROK",       # -22 sopra soglia -> ROK basso
    11: "THN", 10: "N27", 13: "ROK",     # -27 sopra soglia -> ROK basso
    3: "+5V", 12: "CTRL_GND"}, ref="U6", note="finestre dei quattro raw (uscite in OR)")
d.C("+5V", "CTRL_GND", "100n")
d.R("ROK", "+5V", "10k", note="ROK alto = quattro raw dentro la finestra")
d.R("ROK", "CT", "1M2 1%", note="RT: accensione ~1,8 s (1,5-2 s, §6)")
d.C("CT", "CTRL_GND", "2u2 X7R", C12)
d.part("D", "Diode:BAT54W", "BAT54W", SOT323, {"A": "CT", "K": "ROK", "NC": None},
       note="scarica CT in ~1 ms: i relè aprono subito al calo di un raw")
d.part("U", "Comparator:LM339", "LM339", SOIC14, {
    9: "CT", 8: "VREF", 14: "KG0",       # timer scaduto -> KG0 libero (alto) -> relè eccitati
    7: "CTRL_GND", 6: "VREF", 1: None,   # sezioni libere: ingressi a livelli fissi
    5: "CTRL_GND", 4: "VREF", 2: None,
    11: "CTRL_GND", 10: "VREF", 13: None,
    3: "+5V", 12: "CTRL_GND"}, ref="U7", note="timer dei relè")
d.C("+5V", "CTRL_GND", "100n")
d.R("KG0", "+5V", "10k", note="KG0 alto = cuffie collegate")

# ------------------------------------------------------------ cavi
d.side = "F"
d.block = "CAVI verso la scheda comandi: J2 pot, J3 cuffie"
d.part("J", "Connector_Generic:Conn_02x07_Odd_Even", "2x7 cavo piatto",
       "Connector_PinHeader_2.54mm:PinHeader_2x07_P2.54mm_Vertical",
       {i + 1: n for i, n in enumerate(FILI)}, ref="J2", place=(L / 2 + 30, 5, 90),
       note="pot BLEND e LEVEL (stesso ordine in cue-comandi.py)")
d.part("J", "Connector_Generic:Conn_02x03_Odd_Even", "2x3 cavo",
       "Connector_PinHeader_2.54mm:PinHeader_2x03_P2.54mm_Vertical",
       {i + 1: n for i, n in enumerate(CUFFIE)}, ref="J3", place=(L / 2 - 30, 5, 90),
       note="NOTA: due jack cuffie sulla scheda comandi; HPG = ritorno, unito ad AGND solo qui")

d.audio_rules = {
    "sensibili": r"^(NS_[LR]|NMB_[LR]|FB_[LR]|CUE\d_[LR]|MON_[LR]|BL_[LR])$",
    "cavo": r"^(CS|MB|BL|BLB|LV)_[LR]$",
    "rumorose": r"^(\+5V|CTRL_GND|KD|KG0?|ROK|CT|VREF|THN|D2[27]|N2[27]|RAW.*|V2[27]F[+-]|ADJ\d+[+-])$",
    "regolatori": ["U40", "U41", "U42", "U43", "U44", "U45"],
}

if __name__ == "__main__":
    d.build(route="--no-route" not in sys.argv)
