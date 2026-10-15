"""Verifiche del modello di P4 (mic.py) contro LTspice.

Uso:  python3 proto-max/coefficienti/verifica_mic.py
- Preamp: formula analogica contro sim/mic/mic-pre-ac.log (11 posizioni
  del pot GAIN x 6 frequenze, 20 Hz-20 kHz).
- Preamp digitale a 4x (passa-alto) contro la formula analogica.
"""

import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import fx  # noqa: E402
import mic  # noqa: E402
from verifica_fx import risposta  # noqa: E402

QUI = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(QUI, "..", "..", "sim", "mic", "mic-pre-ac.log")
FREQ = {"g20": 20, "g40": 40, "g60": 60, "g100": 100, "g1k": 1000,
        "g20k": 20000}
PASSI = [i / 10 for i in range(11)]
FS = 48000.0


def leggi_log():
    s = open(LOG, errors="ignore").read()
    out = {}
    for m in re.finditer(r"Measurement: (\w+)\n.*?\n((?:\s+\d+\s+\(.*\n)+)", s):
        if m.group(1) in FREQ:
            for riga in m.group(2).strip().split("\n"):
                p = riga.split()
                out[(m.group(1), int(p[0]))] = float(
                    re.search(r"\(([-\d.e+]+)dB", riga).group(1))
    return out


class Pre:
    """Solo il preamp del modello digitale, fino al nodo PRE."""

    def __init__(self, fs4):
        self.m = mic.Mic(fs4)

    def passo(self, v, t, _):
        return self.m.passo(v * 1e-3, t, 0.5, 0.5, 0)[0] / 1e-3


def main():
    log = leggi_log()
    assert len(log) == len(FREQ) * len(PASSI), f"log incompleto: {len(log)}"
    peggio = 0.0
    print("Preamp, formula contro mic-pre-ac.log (dB)")
    for (nome, step), spice in sorted(log.items(), key=lambda k: (k[0][1],
                                                                  FREQ[k[0][0]])):
        t = PASSI[step - 1]
        mod = fx.db(mic.pre_analogico(FREQ[nome], t))
        peggio = max(peggio, abs(mod - spice))
        if FREQ[nome] in (60, 1000):
            print(f"  GAIN {t * 100:3.0f} % {FREQ[nome]:5d} Hz: modello "
                  f"{mod:7.3f}, LTspice {spice:7.3f}")
    print(f"  scarto massimo su {len(log)} punti: {peggio:.3f} dB")
    ok = peggio <= 0.1

    print("Preamp digitale a 4x contro la formula (GAIN 0 e 100 %)")
    peggio_d = 0.0
    for t in (0.0, 1.0):
        for f in (20, 40, 60, 100, 1000, 10000, 20000):
            d = risposta(Pre(4 * FS), f, 4 * FS, t, None)
            a = fx.db(mic.pre_analogico(f, t))
            peggio_d = max(peggio_d, abs(d - a))
    print(f"  scarto massimo: {peggio_d:.3f} dB")
    ok = ok and peggio_d <= 0.1

    print("LED: soglie al nodo PRE, volt di picco",
          ", ".join(f"{d:+.0f} dBu = {v:.3f} V" for d, v in
                    zip(mic.LED_DBU, mic.LED_V)))
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
