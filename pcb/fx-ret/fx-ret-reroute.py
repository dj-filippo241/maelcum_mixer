"""FX-RET, scheda REROUTE: i 4 reroute del ritorno (dec. 91, fx-module §2bis). Bozza v0.1.

Divisione PROVVISORIA della scheda del FX-RET (todo 167, NOTE.md): 410 impronte non stanno su
una 100 x 220. Questa scheda sta affiancata alla scheda segnale (fx-ret.py) sotto lo stesso
pannello (dec. 142) e non ha C96: alimentazioni, RRN e cursori POT_R arrivano dal ponte J1
(ponte.py), le uscite dei driver d'iniezione DIR tornano sullo stesso ponte. Il circuito è
quello di fx-ret.py v0.1 (dec. 144: cambia la scheda, non il circuito), riferimenti invariati.

Per ogni reroute: 2 VCA (L, R) + I/V, driver d'iniezione INVERTENTE 20k/20k (F3), shaper del
reroute (sim/shaper/shaper-reroute.cir) con smoothing 56n (1 ms sulla Rf 18,7k, todo 281), trim di law e d'offset di coppia.
Valori [PROVVISORIO]. Le scelte non scritte nei documenti sono segnate NOTA (pcb/fx-ret/NOTE.md).
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from pcbgen import Design
import celle_vca as cv
from celle_vca import opa2, opa4, vca, iv, shaper, law_trim, CPF
from ponte import ponte

d = Design("fx-ret-reroute", os.path.join(HERE, "reroute"), "maelcum FX-RET reroute (dec. 91) - bozza v0.1",
           board=(100, 220), rev="0.1-bozza")
d.gnd = "AGND"
d.inner_signal = True     # SMD sui due lati (dec. 142), come la scheda segnale
SIDES = ("L", "R")
# NOTA: trimmer SMD Bourns 3214W (5 mm, multigiri: giri da verificare sul datasheet) al posto del
# 3266 a foro passante, solo su questa scheda: così i reroute 3 e 4 vanno interi sul retro, col
# loro trim. Con i 3266 il trim restava davanti e il retro lo allontanava dal VCA (ECR aperte).
cv.TRIM = "Potentiometer_SMD:Potentiometer_Bourns_3214W_Vertical"

# ------------------------------------------------------------ ponte e alimentazione
d.block = "PONTE dalla scheda segnale (J1) e bulk locali"
d.power_nets("AGND", width=0.8)
d.power_nets("+18V", "-18V", "+15LN", "-15LN", width=0.4)   # NOTA: a 0,6 mm Freerouting lascia aperte -18V e +15LN (come il MIC, todo 237)
d.netclass["+REF5"] = 0.3
d.netclass["-REF5"] = 0.3
ponte(d, "J1", (3.5, 110, 0), "NOTA: cavo piatto 2x16 dalla scheda segnale (J4 di fx-ret.py)")
d.CP("+18V", "AGND", "47u 25V", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm", note="NOTA: bulk locale dopo il cavo")
d.CP("AGND", "-18V", "47u 25V", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm", note="NOTA: bulk locale dopo il cavo")
d.C("+15LN", "AGND", "10u 25V", cv.C12, note="NOTA: locale dopo il cavo")
d.C("AGND", "-15LN", "10u 25V", cv.C12, note="NOTA: locale dopo il cavo")
d.C("+REF5", "AGND", "1u", cv.C12, note="NOTA: locale dopo il cavo")
d.C("AGND", "-REF5", "1u", cv.C12, note="NOTA: locale dopo il cavo")
for ref, x, y in (("H1", 5, 5), ("H2", 95, 5), ("H3", 5, 215), ("H4", 95, 215)):
    d.part("H", "Mechanical:MountingHole", "M3", "MountingHole:MountingHole_3.2mm_M3",
           {}, ref=ref, place=(x, y, 0), note="NOTA: fissaggio senza C96 (distanziali isolati), da decidere col telaio")

# ------------------------------------------------------------ reroute (come fx-ret.py v0.1)
for j in range(1, 5):
    t = "R%d" % j
    d.side = "B" if j >= 3 else "F"   # 225 impronte: reroute 3 e 4 (solo SMD) sul retro, dec. 142
    d.block = "REROUTE verso S%d (2 VCA, I/V, driver invertente, shaper reroute, trim)" % j
    base = 10 + 4 * (j - 1)
    for k, s in enumerate(SIDES):
        vca(d, "U%d" % (base + k), "RRN_" + s, "NI%s_%s" % (t, s), "EC%s_%s" % (t, s), "%s%s" % (t.lower(), s.lower()))
        iv(d, "NI%s_%s" % (t, s), "IV%s_%s" % (t, s))
    opa2(d, "U%d" % (base + 2), ("AGND", "NI%s_L" % t, "IV%s_L" % t), ("AGND", "NI%s_R" % t, "IV%s_R" % t),
         note="I/V dei VCA del reroute %d" % j)
    shaper(d, "U%d" % (base + 3), t, *cv.REROUTE, tau="56n C0G")
    law_trim(d, t, "EC%s_L" % t, "EC%s_R" % t)
d.side = "F"
d.block = "DRIVER D'INIEZIONE dei reroute (2 OPA1654, invertenti unity)"
# le 20k del driver stanno nel blocco del driver, davanti: sul retro col reroute NDR3 restava aperta
for j in range(1, 5):
    for s in SIDES:
        d.R("IVR%d_%s" % (j, s), "NDR%d_%s" % (j, s), "20k 0.1%")
        d.R("NDR%d_%s" % (j, s), "DIR%d_%s" % (j, s), "20k 0.1%", note="driver d'iniezione invertente (F3)")
opa4(d, "U26", *[("AGND", "NDR%d_L" % j, "DIR%d_L" % j) for j in range(1, 5)], note="reroute 1-4, lato L")
opa4(d, "U27", *[("AGND", "NDR%d_R" % j, "DIR%d_R" % j) for j in range(1, 5)], note="reroute 1-4, lato R")

d.audio_rules = {
    "sensibili": r"^(NI.*_[LR]|NDR\d_[LR])$",
    "cavo": r"^(RRN_[LR]|DIR\d_[LR])$",
    "rumorose": r"^(POT_.*|CVP_.*|SH_.*)$",
    "regolatori": [],
}

if __name__ == "__main__":
    d.build(route="--no-route" not in sys.argv)
