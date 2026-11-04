"""CANALE CDJ/LINE, scheda ISOLATOR: banca incroci C dei due lati, somma x10 e servo DC. Bozza v0.1.

Divisione PROVVISORIA della scheda del canale (todo 167, NOTE.md): 380 impronte non stanno su
una 100 x 220. Questa scheda sta affiancata alla scheda segnale (canale.py) sotto lo stesso
pannello (dec. 142) e non ha C96: ±18, GO e le reti dei pot arrivano dal ponte J1, EQ torna
sullo stesso ponte (banca.PONTE). Circuito e valori come canale.py v0.1 (dec. 144: cambia la
scheda, non il circuito), riferimenti U3-U14 invariati. Fonti in testa a canale.py.
Valori [PROVVISORIO]. Le scelte non scritte nei documenti sono segnate NOTA (pcb/canale/NOTE.md).
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from pcbgen import Design
from celle_vca import C12
from banca import banca, ponte

d = Design("canale-isolator", os.path.join(HERE, "isolator"), "maelcum CANALE isolator (dec. 152) - bozza v0.1",
           board=(100, 220), rev="0.1-bozza")
d.gnd = "AGND"
d.inner_signal = True     # SMD sui due lati (dec. 142)

d.block = "PONTE dalla scheda segnale (J1) e bulk locali"
d.power_nets("AGND", width=0.8)
d.power_nets("+18V", "-18V", width=0.4)   # NOTA: a 0,6 mm Freerouting lascia -18V aperta (come il MIC, todo 237)
ponte(d, "J1", (3.5, 100, 0), "NOTA: cavo piatto 2x18 dalla scheda segnale (J4 di canale.py)")
d.CP("+18V", "AGND", "47u 25V", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm", note="NOTA: bulk locale dopo il cavo")
d.CP("AGND", "-18V", "47u 25V", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm", note="NOTA: bulk locale dopo il cavo")
for ref, x, y in (("H1", 5, 5), ("H2", 95, 5), ("H3", 5, 215), ("H4", 95, 215)):
    d.part("H", "Mechanical:MountingHole", "M3", "MountingHole:MountingHole_3.2mm_M3",
           {}, ref=ref, place=(x, y, 0), note="NOTA: fissaggio senza C96 (distanziali isolati), da decidere col telaio")

banca(d)

d.audio_rules = {
    "sensibili": r"^(SP_[LR]|NGS_[LR])$",
    "cavo": r"^(GO|EQ|LOO|LMO|MHO|HIO|K\dW)_[LR]$",
    "rumorose": r"^$",
    "regolatori": [],
}

if __name__ == "__main__":
    d.build(route="--no-route" not in sys.argv)
