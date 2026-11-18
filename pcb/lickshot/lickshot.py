"""LICKSHOT: rack 1U fuori dal mixer (dec. 179-198), nome FLETCHER (dec. 197), scheda unica dietro il pannello. Bozza v0.1.

Catena (docs/fase4/lickshot.md v0.3 §2-§3):
 LFO CD4069 (VELOCITA) -> buffer -> PROFONDITA -> VCO CD4046 (ALTEZZA) -> passa-alto 14,5 Hz
   -> guadagno a 0 dBu -> FIRE -> VOLUME -> buffer = DRY
 DRY + FB -> somma invertente -> attenuatore -14 dB -> BBD (uno, dec. 198) -> make-up tarata (~x5,6) = POST
 POST -> passa-alto 150 Hz -> buffer -> RIPETIZIONI -> diodi -> x2,5 = FB
 DRY + LIVELLO ECO x POST -> mix invertente -> 100 ohm + 10 uF -> jack (sul pannello dietro).

Scheda orizzontale nel rack, bordo davanti (y = 0) contro il pannello: pot Alps RK09L
orizzontali e LED a 90 gradi alle x di docs/pannelli/lickshot-1u.json (dec. 196). FIRE, jack
d'uscita e ingresso DC stanno sui pannelli e arrivano coi fili (J1-J3).
Valori dai netlist di sim/lickshot/ (profondita.cir, giro-att14.cir, mix-uscita.cir) e dal
RISULTATI-lickshot-v02.md. Valori [PROVVISORIO]. Le scelte non scritte nei documenti sono
segnate NOTA (pcb/lickshot/NOTE.md).
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
import pcbgen
from pcbgen import boxsym

SOIC8 = "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"
SOIC14 = "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm"
SOIC16 = "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm"
DIP8 = "Package_DIP:DIP-8_W7.62mm"
C12 = "Capacitor_SMD:C_1206_3216Metric"
TRIM = "Potentiometer_THT:Potentiometer_Bourns_3266W_Vertical"
POT_FP = "Potentiometer_THT:Potentiometer_Alps_RK09L_Single_Horizontal"
POT_ANCORA = (-5.12, 2.5)      # albero sul fronte del corpo (impronta KiCad, riga F.Fab x = -5,12)
LED_FP = "LED_THT:LED_D3.0mm_Horizontal_O1.27mm_Z6.0mm"
LED_ANCORA = (1.27, 5.5)       # punta del LED (corpo da y 1,27 a 5,07 + cupola)
HDR2 = "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical"

# ---------------------------------------------------------------- simboli (pinout: lickshot.md §4)
TLC2272 = boxsym("TLC2272", [
    ("3", "1IN+", "input"), ("2", "1IN-", "input"), ("5", "2IN+", "input"), ("6", "2IN-", "input"),
    ("4", "VDD-/GND", "power_in")], [
    ("1", "1OUT", "output"), ("7", "2OUT", "output"), ("8", "VDD+", "power_in")], fp=SOIC8,
    desc="Op-amp doppio rail-to-rail. Pinout TI SLOS190H (rev. marzo 2016), Pin Configuration and Functions")
CD4069 = boxsym("CD4069UB", [
    ("1", "1A", "input"), ("3", "2A", "input"), ("5", "3A", "input"), ("9", "4A", "input"),
    ("11", "5A", "input"), ("13", "6A", "input"), ("7", "VSS", "power_in")], [
    ("2", "1Y", "output"), ("4", "2Y", "output"), ("6", "3Y", "output"), ("8", "4Y", "output"),
    ("10", "5Y", "output"), ("12", "6Y", "output"), ("14", "VDD", "power_in")], fp=SOIC14,
    desc="Sei invertitori senza buffer. Pinout TI CD4069UB, Pin Configuration and Functions")
CD4046 = boxsym("CD4046B", [
    ("3", "COMP_IN", "input"), ("14", "SIG_IN", "input"), ("9", "VCO_IN", "input"), ("5", "INH", "input"),
    ("6", "C1A", "passive"), ("7", "C1B", "passive"), ("11", "R1", "passive"), ("12", "R2", "passive"),
    ("8", "VSS", "power_in")], [
    ("4", "VCO_OUT", "output"), ("1", "PH_PULSES", "output"), ("2", "PC1_OUT", "output"),
    ("13", "PC2_OUT", "output"), ("10", "DEMOD_OUT", "output"), ("15", "ZENER", "passive"),
    ("16", "VDD", "power_in")], fp=SOIC16,
    desc="PLL usato solo come VCO. Pinout TI SCHS043B (rev. luglio 2003) p. 1, Terminal assignment")
V3205 = boxsym("V3205D", [
    ("7", "IN", "input"), ("6", "CP1", "input"), ("2", "CP2", "input"), ("8", "VGG", "input"),
    ("1", "GND", "power_in")], [
    ("3", "OUT1", "output"), ("4", "OUT2", "output"), ("5", "VDD", "power_in")], fp=DIP8,
    desc="BBD 4096 stadi. Pinout CoolAudio V3205D/SD datasheet, Pin Configuration (copia cricklewoodelectronics.com)")
V3102 = boxsym("V3102", [
    ("7", "OX1", "input"), ("6", "OX2", "output"), ("5", "OX3", "output"), ("3", "GND", "power_in")], [
    ("2", "CP1", "output"), ("4", "CP2", "output"), ("8", "VGG_OUT", "output"), ("1", "VDD", "power_in")],
    fp=DIP8, desc="Clock dei BBD. Pinout dal gemello Panasonic MN3102 p. 107, Terminal Assignments "
                  "(scansione 1998, experimentalistsanonymous.com); da confermare sul foglio CoolAudio (lickshot.md §4)")
POT = boxsym("POT_RK09L_H", [("1", "CCW", "passive"), ("2", "W", "passive"), ("3", "CW", "passive")],
             [("MP", "MP", "passive")], ref="RV", fp=POT_FP,
             desc="Pot singolo Alps RK09L orizzontale (albero parallelo alla scheda); MP = staffe")


class LickDesign(pcbgen.DesignRiprova):
    """Design del generatore con Freerouting ripetuto (DesignRiprova) e una regola locale: sui
    chip col pin di alimentazione all'angolo (SOIC-14, SOIC-16, DIP-8) il 100n esce in
    verticale dal pin e tocca il courtyard del chip (DRC courtyards_overlap, primo giro del
    2026-11-18). Qui il C si sposta in fuori lungo lo stesso asse finché esce dal riquadro."""

    def _attach(self, fps, ic, caps):
        import pcbnew
        super()._attach(fps, ic, caps)
        ux1, uy1, ux2, uy2 = self._bbox(fps[ic])
        c0 = fps[ic].GetPosition()
        for cref, _ in caps:
            cf = fps[cref]
            for _ in range(40):
                x1, y1, x2, y2 = self._bbox(cf)
                if x2 <= ux1 or x1 >= ux2 or y2 <= uy1 or y1 >= uy2:
                    break
                p = cf.GetPosition()
                dx, dy = p.x - c0.x, p.y - c0.y
                # asse dello spostamento: quello su cui il C sta già più fuori dal chip
                if abs(dy) / max(uy2 - uy1, 1e-6) >= abs(dx) / max(ux2 - ux1, 1e-6):
                    cf.SetPosition(pcbnew.VECTOR2I(p.x, p.y + (1 if dy >= 0 else -1) * pcbnew.FromMM(0.25)))
                else:
                    cf.SetPosition(pcbnew.VECTOR2I(p.x + (1 if dx >= 0 else -1) * pcbnew.FromMM(0.25), p.y))


d = LickDesign("lickshot", HERE, "FLETCHER - lickshot rack 1U (dec. 179-198) - bozza v0.1", board=(280, 95), rev="0.1-bozza")
d.gnd = "AGND"
d.route_tries = 6
d.link_pairs = True   # cursore e capo dei trimmer a reostato sulla stessa rete (TMPB, POST)
d.power_nets("+9V", "+5V", "VIN", "VIN5", "RAW12", "AGND")

# pannello: x della scheda = x del pannello - X0 (la scheda va da 100 a 380 mm del pannello)
X0 = 100.0
PAN = json.load(open(os.path.join(ROOT, "docs", "pannelli", "lickshot-1u.json")))
COM = {c["nome"]: c for c in PAN["comandi"]}


def pot(nome, reti, val, nota):
    c = COM[nome]
    return d.part("RV", POT, val, POT_FP, {"1": reti[0], "2": reti[1], "3": reti[2], "MP": "AGND"},
                  place=(c["x"] - X0, 0.0, 270), anchor=POT_ANCORA,
                  note="%s; manopola %s, x %.0f mm sul pannello" % (nota, nome, c["x"]))


def opa(ref, a, b, note=""):
    """TLC2272: a, b = (ingresso +, ingresso -, uscita)."""
    d.part("U", TLC2272, "TLC2272CD", SOIC8, {3: a[0], 2: a[1], 1: a[2], 5: b[0], 6: b[1], 7: b[2],
                                             8: "+9V", 4: "AGND"}, ref=ref, note=note)
    d.C("+9V", "AGND", "100n")


def trim(a, w, b, val, note):
    return d.part("RV", "Device:R_Potentiometer_Trim", val, TRIM, {1: a, 2: w, 3: b}, note=note)


# ---------------------------------------------------------------- alimentazione (§3.1, RISULTATI §6)
d.block = "ALIMENTAZIONE 12 V -> +9 V e +5 V"
d.part("J", "Connector_Generic:Conn_01x02", "ingresso DC (cavo)", HDR2, {1: "RAW12", 2: "AGND"}, ref="J1",
       place=(265, 89, 0), note="NOTA: filo verso la presa DC con blocco sul pannello dietro (dec. 189); "
                                "negativo flottante, la massa arriva dal MONO (RISULTATI §6)")
d.part("D", "Diode:1N5819", "1N5819", "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal", {"A": "RAW12", "K": "VIN"},
       note="protezione contro l'inversione (~0,35 V)")
d.CP("VIN", "AGND", "100u 25V")
d.part("U", "Regulator_Linear:L78L09_TO92", "78L09", "Package_TO_SOT_THT:TO-92_Inline_Wide",
       {"VI": "VIN", "VO": "+9V", "GND": "AGND"}, ref="U10", note="9 V per CMOS e op-amp (61 mW)")
d.C("VIN", "AGND", "330n", note="ingresso del 78L09")
d.C("+9V", "AGND", "100n")
d.CP("+9V", "AGND", "10u 25V", fp="Capacitor_THT:CP_Radial_D5.0mm_P2.00mm")
d.R("VIN", "VIN5", "47", fp="Resistor_SMD:R_1206_3216Metric", note="47 ohm + 100 uF: picchi del clock fuori dal ramo dei 9 V")
d.CP("VIN5", "AGND", "100u 25V")
d.part("U", "Regulator_Linear:L78L05_TO92", "78L05", "Package_TO_SOT_THT:TO-92_Inline_Wide",
       {"VI": "VIN5", "VO": "+5V", "GND": "AGND"}, ref="U11", note="5 V per BBD e clock (0,15 W)")
d.C("+5V", "AGND", "100n")
d.CP("+5V", "AGND", "47u 16V", fp="Capacitor_THT:CP_Radial_D5.0mm_P2.00mm",
     note="NOTA: serbatoio per le correnti del clock (2 x 2800 pF a 100 kHz)")

d.block = "VDD/2: partitore e buffer"
d.R("+9V", "VMIDR", "10k")
d.R("VMIDR", "AGND", "10k")
d.C("VMIDR", "AGND", "10u", C12, note="NOTA: filtra il rumore del partitore (1,6 Hz)")

# ---------------------------------------------------------------- LFO (§3.2, Nold)
d.block = "LFO CD4069UB: trigger di Schmitt + integratore, LED"
d.part("U", CD4069, "CD4069UBM", SOIC14, {1: "SCHIN", 2: "SCHA", 3: "SCHA", 4: "SCH", 5: "INTIN", 6: "RAMP",
                                          9: "AGND", 11: "AGND", 13: "AGND", 7: "AGND", 14: "+9V"},
       ref="U1", note="U1A + U1B trigger di Schmitt, U1C integratore di Miller; U1D-F ingressi a massa")
d.C("+9V", "AGND", "100n")
d.R("RAMP", "SCHIN", "10k", note="R4 di Nold: soglie 6/22 e 16/22 di VDD con R1")
d.R("SCH", "SCHIN", "22k", note="R1 di Nold")
d.C("RAMP", "INTIN", "1u film", "Capacitor_THT:C_Rect_L7.2mm_W4.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2",
    note="C1 dell'integratore, film")
d.R("SCH", "VELA", "33k", note="dec. 195 (Nold: 22k): massimo 33 colpi/s")
d.part("D", "Diode:1N4148", "1N4148", "Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal", {"A": "INTIN", "K": "SCH"},
       note="D3: risalita veloce, discesa lenta (il tono cade a ogni colpo)")
d.part("Q", "Transistor_BJT:2N3904", "2N3904", "Package_TO_SOT_THT:TO-92_Inline_Wide",
       {"B": "RAMP", "C": "+9V", "E": "LEDE"}, note="inseguitore del LED sull'uscita dell'integratore")
d.R("LEDE", "LEDA", "10k")
c = COM["LFO"]
d.part("D", "Device:LED", "LED 3 mm rosso", LED_FP, {1: "AGND", 2: "LEDA"}, place=(c["x"] - X0, 0.3, 180),
       anchor=LED_ANCORA, note="NOTA: LED a 90 gradi; l'altezza Z va fatta coincidere con quella dell'albero dei pot")

# ---------------------------------------------------------------- PROFONDITA (§3.3, profondita.cir)
d.block = "BUFFER DELLA RAMPA, VDD/2 e PROFONDITA (TLC2272)"
opa("U3", ("VMIDR", "VMID", "VMID"), ("RAMP", "RAMPB", "RAMPB"),
    note="A: buffer di VDD/2; B: buffer della rampa (ingresso 2,45-6,55 V, sotto i 7,5 V del modo comune)")
d.R("DEPN", "VMID", "10k", note="RG")
d.R("DEPN", "VCODRV", "5k1", note="RF: G 1,51 a 9 V (lickshot.md §6 punto 1)")
d.R("VCODRV", "VCOIN", "10k", note="R in serie al pin 9")
opa("U4", ("DEPW", "DEPN", "VCODRV"), ("VMID", "GN", "COLPO"),
    note="A: PROFONDITA non invertente riferito a VDD/2; B: guadagno del colpo (invertente)")

# ---------------------------------------------------------------- VCO (§3.4)
d.block = "VCO CD4046B (ALTEZZA)"
d.part("U", CD4046, "CD4046BM", SOIC16, {3: "AGND", 14: "AGND", 9: "VCOIN", 5: "AGND", 6: "VCOC", 7: "VCOC2",
                                         11: "VCOR", 4: "VCOOUT", 8: "AGND", 16: "+9V"}, ref="U2",
       note="solo VCO: R2 (pin 12) aperta, fmin = 0; ingressi dei comparatori e inhibit a massa")
d.C("+9V", "AGND", "100n")
d.C("VCOC", "VCOC2", "100n film", "Capacitor_THT:C_Rect_L7.2mm_W3.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2",
    note="C1 del VCO, film")
d.R("VCOR", "ALTA", "10k", note="R1 fisso: tetto a 700 Hz")

# ---------------------------------------------------------------- colpo e FIRE (§3.5)
d.block = "COLPO: passa-alto 14,5 Hz, guadagno a 0 dBu, FIRE"
d.C("VCOOUT", "HPA", "100n film", "Capacitor_THT:C_Rect_L7.2mm_W3.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2",
    note="passa-alto 14,5 Hz con 110k")
d.R("HPA", "GN", "110k", note="x0,173 col 19k1: 0,78 V di plateau. Niente partitore verso VMID: il VCO "
                              "gira sempre e i suoi fronti scuotevano VDD/2 (RISULTATI-scheda §3)")
d.R("GN", "COLPO", "19k1", note="0,78 V di plateau = 0 dBu (dec. 187)")
d.part("J", "Connector_Generic:Conn_01x02", "FIRE (cavo)", HDR2, {1: "COLPO", 2: "FIREOUT"}, ref="J2",
       place=(268, 22, 0), note="NOTA: fili verso il tasto FIRE da 24 mm sul pannello (premi e tieni, normalmente aperto)")
d.R("FIREOUT", "VMID", "100k", note="NOTA: tasto aperto = VOLUME a VDD/2, niente ingresso flottante")

# ---------------------------------------------------------------- VOLUME e somma (§3.5-§3.6, giro-att14.cir)
d.block = "VOLUME, SOMMA DEL GIRO, ATTENUATORE -14 dB (TLC2272)"
opa("U5", ("VOLW", "DRY", "DRY"), ("VMID", "SUMN", "SUM"),
    note="A: buffer dopo VOLUME; B: somma invertente DRY + FB")
d.R("DRY", "SUMN", "10k")
d.R("FB", "SUMN", "10k")
d.R("SUMN", "SUM", "10k")
d.R("SUM", "ATT", "40k2", note="attenuatore -14 dB (0,2) prima dei BBD")
d.R("ATT", "VMID", "10k")

# ---------------------------------------------------------------- BBD e clock (§3.6)
d.block = "ECO: un V3205D, un V3102 (TEMPO), dec. 198"
d.C("ATT", "BBD1IN", "1u", C12, note="dal dominio 9 V al BBD a 5 V")
trim("+5V", "BIAS1", "AGND", "10k", "NOTA: polarizzazione dell'ingresso del BBD 1, da tarare sul pezzo")
d.R("BIAS1", "BBD1IN", "100k")
d.C("BIAS1", "AGND", "1u", C12, note="NOTA: tiene pulita la polarizzazione")
d.part("U", V3205, "V3205D", DIP8, {7: "BBD1IN", 6: "CP1A", 2: "CP2A", 8: "VGGA", 1: "AGND",
                                    3: "B1O1", 4: "B1O2", 5: "+5V"}, ref="U20", note="BBD 1")
d.C("+5V", "AGND", "100n")
d.R("B1O1", "AGND", "100k", note="carico delle uscite a source follower: RL 100k del datasheet V3205D")
d.R("B1O2", "AGND", "100k")
trim("B1O1", "BBD1OUT", "B1O2", "10k", "cancellazione del clock, BBD 1 (schema d'applicazione BL3102)")
d.part("U", V3102, "V3102", DIP8, {1: "+5V", 2: "CP1A", 3: "AGND", 4: "CP2A", 5: "OSC3", 6: "OSC2",
                                   7: "OSC1", 8: "VGGA"}, ref="U22",
       note="clock, oscilla da solo: R fra OX2 e OX1, C fra OX3 e OX1 (MN3102 p. 107)")
d.C("+5V", "AGND", "100n")
d.C("OSC3", "OSC1", "220p C0G", note="C del clock: 50-5 kHz con 22k...282k, cioe 41-405 ms con un BBD (dec. 198; fit MN3102 Fig. 1 scalato con C, RISULTATI-lickshot-v02 §4)")
d.R("OSC2", "TMPA", "22k", note="fisso: 50 kHz a TEMPO zero (41 ms)")
trim("TMPA", "TMPB", "TMPB", "10k", "fondo scala di TEMPO (reostato)")

# ---------------------------------------------------------------- make-up e giro (giro-att14.cir)
d.block = "MAKE-UP x5, PASSA-ALTO 150 Hz, SATURAZIONE (TLC2272)"
d.C("BBD1OUT", "MKC", "1u", C12, note="accoppiamento dal BBD (3,4 Hz con 47k)")
d.R("MKC", "MKN", "47k", note="47k: il cursore del trimmer di cancellazione (~3k) sposta il guadagno di 0,4 dB, non di 1,4")
d.R("MKN", "MKT", "100k")
d.part("RV", "Device:R_Potentiometer_Trim", "500k", "Potentiometer_SMD:Potentiometer_Bourns_3224W_Vertical",
       {1: "MKT", 2: "POST", 3: "POST"}, note="SMD 4 mm (3224W, 11 giri): col 3266 il blocco cresceva e l'eco perdeva il posto. Taratura del giro: SUM -> POST = 0 dB (~280k in tutto); 100k-600k copre "
     "da -6,6 a +9 dB di guadagno d'inserzione dei due V3205D (datasheet: +-4 dB per chip; RISULTATI-scheda §2)")
d.C("POST", "HPN", "100n film", "Capacitor_THT:C_Rect_L7.2mm_W3.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2",
    note="passa-alto del giro, 150 Hz")
d.R("HPN", "VMID", "10k7")
opa("U6", ("VMID", "MKN", "POST"), ("HPN", "GY", "GY"),
    note="A: make-up; B: buffer dopo il passa-alto")
d.R("RIPW", "SATD", "12k7", note="NOTA: 12,7k/10k = 0,44 (1,1 x 0,4 del netlist) prima dei diodi")
d.R("SATD", "VMID", "10k")
d.part("D", "Diode:1N4148W", "1N4148W", "Diode_SMD:D_SOD-123", {"A": "SATD", "K": "VMID"}, note="saturazione")
d.part("D", "Diode:1N4148W", "1N4148W", "Diode_SMD:D_SOD-123", {"A": "VMID", "K": "SATD"}, note="saturazione")
d.R("SATN", "VMID", "10k")
d.R("SATN", "FB", "15k", note="x2,5 dopo i diodi")

# ---------------------------------------------------------------- mix e uscita (mix-uscita.cir)
d.block = "MIX E USCITA 0 dBu (TLC2272)"
opa("U7", ("SATD", "SATN", "FB"), ("VMID", "MXN", "MIX"),
    note="A: guadagno dopo la saturazione; B: mix invertente")
d.R("DRY", "MXN", "10k")
d.R("ECOW", "MXN", "10k")
d.R("MXN", "MIX", "10k")
d.R("MIX", "OUTR", "100")
d.CP("OUTR", "JOUT", "10u 25V", fp="Capacitor_THT:CP_Radial_D5.0mm_P2.00mm",
     note="NOTA: elettrolitico col + verso il mix (VDD/2), il jack sta a 0 V")
d.R("JOUT", "AGND", "100k", note="scarica: passa-alto 0,17 Hz sul MONO da 1 MOhm")
d.part("J", "Connector_Generic:Conn_01x02", "uscita (cavo)", HDR2, {1: "JOUT", 2: "AGND"}, ref="J3",
       place=(240, 89, 0), note="NOTA: filo verso il jack mono sul pannello dietro (dec. 187)")

# ---------------------------------------------------------------- comandi del pannello (dec. 196)
d.block = "COMANDI DEL PANNELLO (pot orizzontali)"
pot("ALTEZZA", ("AGND", "AGND", "ALTA"), "100k C",
    "reostato fra pin 3 e cursore: R scende in modo esponenziale, ottave uguali e nota che sale in senso orario "
    "(dec. 194); NOTA: logaritmico inverso (C), oppure A con i capi scambiati")
pot("VELOCITÀ", ("INTIN", "INTIN", "VELA"), "500k B",
    "reostato fra cursore e pin 3: R scende in senso orario, colpi più fitti (modello lineare)")
pot("PROFONDITÀ", ("VMID", "DEPW", "RAMPB"), "10k B", "fra VDD/2 e la rampa (dec. 190)")
pot("VOLUME", ("VMID", "VOLW", "FIREOUT"), "10k A", "legge quadratica del modello")
pot("TEMPO", ("TMPB", "OSC1", "OSC1"), "250k B",
    "reostato fra pin 1 e cursore: ritardo che cresce in senso orario (dec. 193, lineare)")
pot("RIPETIZIONI", ("VMID", "RIPW", "GY"), "10k B", "guadagno del giro fino a 1,1")
pot("LIVELLO ECO", ("VMID", "ECOW", "POST"), "10k A", "eco al quadrato del modello")

d.block = "FORI DI FISSAGGIO"
for k, (x, y) in enumerate(((4, 24), (276, 24), (4, 91), (276, 50)), 1):
    d.part("H", "Mechanical:MountingHole", "M3", "MountingHole:MountingHole_3.2mm_M3", {}, ref="H%d" % k,
           place=(x, y, 0), note="NOTA: foro senza pad; massa unica dal MONO (RISULTATI §6)")

d.audio_rules = {
    "sensibili": r"^(SUMN|MKN|MXN|GN|DEPN|SATN|BBD[12]IN|HPN|SATD)$",
    "rumorose": r"^(CP[12][AB]|OSC\d|VGG[AB]|SCH|SCHA|SCHIN|VCOOUT|VCOC2?|RAW12|VIN5?)$",
    "regolatori": ["U10", "U11"],
}

if __name__ == "__main__":
    d.build(route="--no-route" not in sys.argv)
