"""CUE, scheda comandi (todo 270, 294): BLEND, LEVEL e i due jack delle cuffie.

La scheda sta parallela al pannello (200 x 52 mm) e lo copre tutto meno i bordi: 198 x 48 mm.
Si regge sui dadi dei pot e dei jack. Posizioni da docs/pannelli/coordinate.json, modulo "cue"
(cuffie a sinistra, BLEND e LEVEL a destra).

Due cavi verso cue.py, ordine letto da quel file (una fonte sola):
- J3, 2x7: FILI, i pot (verso J2 di cue.py).
- J4, 2x3: CUFFIE, i jack (verso J3 di cue.py); HPG = ritorno delle cuffie, separato da AGND
  su questa scheda e unito ad AGND solo sulla scheda di segnale [NOTA, pcb/cue/NOTE.md].

Pot doppi (sistema-cue.md §5): sezione A = L, sezione B = R.
- BLEND 10k lineare con scatto al centro: antiorario = cue (CS), orario = master (MB).
- LEVEL 10k logaritmico: antiorario = AGND (silenzio vero), orario = BLB (blend bufferizzato),
  cursore = LV verso l'ampli.
Jack J1 e J2 (PHONES 1 e 2): punta = L, anello = R, manicotto = HPG.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from comandi import Comandi, fili_da

s = Comandi("cue-comandi", os.path.join(HERE, "comandi"), "maelcum CUE scheda comandi - bozza v0.1", "cue",
            riprova=True)
d = s.d
d.power_nets("HPG", width=0.5)

d.block = "POT BLEND e LEVEL, JACK delle cuffie (posizioni dal render del pannello)"
for c in s.comandi("manopola"):
    if c["nome"] == "BLEND":
        s.pot2(c, ("CS_L", "BL_L", "MB_L"), ("CS_R", "BL_R", "MB_R"), "10k lin, scatto al centro",
               "BLEND: antiorario = cue, centro = 50/50 (-6 dB per parte), orario = master")
    else:
        s.pot2(c, ("AGND", "LV_L", "BLB_L"), ("AGND", "LV_R", "BLB_R"), "10k log",
               "LEVEL: antiorario = silenzio vero (cursore a massa)")
for c in s.comandi("jack"):
    j = c["nome"][-1]
    s.jack(c, "HP%s_T" % j, "HP%s_R" % j, "HPG", nota="punta L, anello R, manicotto HPG")

d.block = "CAVI: J3 pot (J2 di cue.py), J4 cuffie (J3 di cue.py)"
s.cavo(fili_da(os.path.join(HERE, "cue.py"), "FILI"), "J3", 115.0, 24.0,
       nota="stesso ordine di J2 su cue.py (FILI)")
s.cavo(fili_da(os.path.join(HERE, "cue.py"), "CUFFIE"), "J4", 90.0, 24.0,
       nota="stesso ordine di J3 su cue.py (CUFFIE)")
s.chiudi()

d.audio_rules = {
    "sensibili": r"^(LV|BL)_[LR]$",
    "cavo": r"^(CS|MB|BL|BLB|LV)_[LR]$",
    "rumorose": r"^(HP\d_[TR]|HPG)$",
    "regolatori": [],
}

if __name__ == "__main__":
    d.build(route="--no-route" not in sys.argv)
