"""MASTER, scheda comandi (todo 270): BOOTH, MASTER, tasto MONO e le due barre da 20 LED.

La scheda sta parallela al pannello (450 x 48 mm) e ne copre solo il tratto coi comandi:
da x 104 a x 346 mm, 242 x 44 mm. Si regge sui dadi dei due pot. Posizioni da
docs/pannelli/coordinate.json, modulo "master" (dec. 176 f: BOOTH a sinistra, meter L e R al
centro col MONO sotto, MASTER a destra).

Due cavi, come scritto in pcb/master/NOTE.md:
- J1, 2x10: verso J3 di master-segnale.py, stesso ordine (letto dal file: una fonte sola).
- J2, 2x2: +5V e CTRL_GND dalla J4 della scheda d'uscita L, pin alternati.

Pot singoli lineari 10k (sistema-comandi.md: singolo lin -> CV). Manopola rovescia: lo shaper
vuole Vx = 5(1 - theta) (sim/shaper/shaper-master.cir), quindi antiorario = +REF5,
orario = AGND. MASTER con scatto al centro (dec. 139); BOOTH senza.
MONO: tasto a ritenuta fra +REF5 e MONO_SW (master-segnale.py); la luce passa dal secondo
contatto, da +5V a CTRL_GND: la corrente del LED resta fuori da AGND e da +REF5 [NOTA].
Meter: 2 LM3915 per lato in cascata, riferimenti VREFA (5,000 V) e VREFB (1,581 V), 20 segmenti
da +24 a -33 dBu (sistema-metering.md §3, §5). CLIP_L e CLIP_R arrivano sul cavo ma il pannello
non ha un LED di clip: restano liberi (pcb/master/NOTE.md, scheda comandi).
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from comandi import Comandi, fili_da

FINESTRA = (104.0, 2.0, 346.0, 46.0)
s = Comandi("master-comandi", os.path.join(HERE, "comandi"), "maelcum MASTER scheda comandi - bozza v0.1",
            "master", FINESTRA)
d = s.d
d.power_nets("+5V", "CTRL_GND", width=0.4)

POT = {"MASTER": ("POT_M", "MASTER: antiorario = silenzio, scatto al centro = 0 dB, orario = +6 dB"),
       "BOOTH": ("POT_B", "BOOTH: antiorario = silenzio")}

d.block = "POT e TASTO MONO (posizioni dal render del pannello)"
for c in s.comandi("manopola"):
    w, nota = POT[c["nome"]]
    s.pot(c, ("+REF5", w, "AGND"), "10k lin", nota + "; manopola rovescia: antiorario = +REF5")
for c in s.comandi("bottone"):
    s.bottone(c, "+REF5", "MONO_SW", luce=(None, "CTRL_GND", "+5V"), rluce="1k5",
              nota="MONO: chiuso = mono (+REF5 su MONO_SW); luce ~2 mA dal secondo contatto")

d.block = "METER L e R: 2 LM3915 in cascata per lato, 20 LED"
for c in s.comandi("meter"):
    x, y = s.xy(c)
    # i due chip sopra la loro metà di barra, coricati: 10 fili corti per chip
    chip = [(x + 1.1 + 14.5 * 3.0, 8.0, 90), (x + 1.1 + 4.5 * 3.0, 8.0, 90)]
    s.meter(c, "MET_" + c["nome"], ["VREFA", "VREFB"], piu="+5V", meno="CTRL_GND", tag=c["nome"], chip=chip)

d.block = "CAVI: J1 verso la scheda di segnale (J3), J2 verso la scheda d'uscita L (J4)"
s.cavo(fili_da(os.path.join(HERE, "master-segnale.py"), "J3"), "J1", 38.0, 38.5,
       nota="stesso ordine di J3 su master-segnale.py; CLIP_L e CLIP_R liberi (nessun LED di clip sul pannello)")
s.cavo(["+5V", "CTRL_GND", "+5V", "CTRL_GND"], "J2", 200.0, 38.5,
       nota="stesso ordine di J4 su master-uscita.py L: pin alternati (pcb/master/NOTE.md)")
s.chiudi()

if __name__ == "__main__":
    d.build(route="--no-route" not in sys.argv)
