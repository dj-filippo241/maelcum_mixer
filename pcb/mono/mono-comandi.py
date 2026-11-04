"""MONO, scheda comandi: pot e LED dietro il pannello (dec. 133, come il FX-SEND).

Ogni albero cade sul foro del render (docs/pannelli/coordinate.json, modulo "mono"). Il cavo
piatto J1 va a J2 di mono.py, stesso ordine (cavo.py).

Pot singoli Alps RK09L verticali. Estremi: 1 = antiorario, 2 = cursore, 3 = orario.
- GAIN 10k A (todo 131): partitore AGND - GW - BUF, poi make-up +10 dB.
- EQ HIGH / LOW 10k: come fx-send-comandi.py. SEND 1-4 10k: AGND - SWk - POST.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from celle_micmono import scheda_comandi
from cavo import CAVO

RETI = {
    "GAIN": ("AGND", "GW", "BUF", "10k A", "GAIN: tutto antiorario = silenzio (todo 131)"),
    "EQ HIGH": ("VHN", "WPH", "VHP", "10k", "HIGH: tutto antiorario = kill"),
    "EQ LOW": ("NC", "NB", "NA", "10k", "LOW Baxandall: cursore = massa virtuale"),
}
for k in range(1, 5):
    RETI["SEND %d" % k] = ("AGND", "SW%d" % k, "POST", "10k", "SEND %d: tutto antiorario = silenzio" % k)

d = scheda_comandi(HERE, "mono", "maelcum MONO scheda comandi - bozza v0.1", CAVO, RETI)

if __name__ == "__main__":
    d.build(route="--no-route" not in sys.argv)
