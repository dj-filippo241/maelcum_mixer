"""MIC, scheda comandi: pot, LED e tasto MUTE dietro il pannello (dec. 133, come il FX-SEND).

La scheda sta parallela al pannello e si regge sui dadi dei pot. Ogni albero cade sul foro del
render (docs/pannelli/coordinate.json, modulo "mic"). Il cavo piatto J1 va a J2 di mic.py, stesso
ordine (cavo.py). Le reti dei pot vengono da mic.py e da celle_micmono.py (eq2, sends).

Pot singoli Alps RK09L verticali. Estremi: 1 = antiorario, 2 = cursore, 3 = orario.
- GAIN 5k (curva C, todo 131): reostato dello stadio 2, GP2-GINV-GP1. Orario = cursore verso GP1:
  ingresso 332, retroazione 5k36 + 5k = +29,9 dB; antiorario = 0 dB.
- EQ HIGH / LOW 10k: come fx-send-comandi.py (VHN-WPH-VHP, NC-NB-NA).
- SEND 1-4 10k: AGND - SWk - POST.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from celle_micmono import scheda_comandi
from cavo import CAVO

RETI = {
    "GAIN": ("GP2", "GINV", "GP1", "5k C", "GAIN 0...+30 dB: orario = cursore verso GP1 (curva C, todo 131)"),
    "EQ HIGH": ("VHN", "WPH", "VHP", "10k", "HIGH: tutto antiorario = kill"),
    "EQ LOW": ("NC", "NB", "NA", "10k", "LOW Baxandall: cursore = massa virtuale"),
}
for k in range(1, 5):
    RETI["SEND %d" % k] = ("AGND", "SW%d" % k, "POST", "10k", "SEND %d: tutto antiorario = silenzio" % k)

d = scheda_comandi(HERE, "mic", "maelcum MIC scheda comandi - bozza v0.1", CAVO, RETI, tasto=("+5VF", "MUTE_SW"))

if __name__ == "__main__":
    d.build(route="--no-route" not in sys.argv)
