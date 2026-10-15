"""Verifica dell'EQ in serie (B5): modello serie.py contro LTspice.

Uso:  python3 proto-max/coefficienti/verifica_serie.py
Legge sim/eq-serie/cascade-b3.log (10 modi, step Rfmv 99,8k = coppia 0,1 %
del make-up). Il .log e fuori da git: se manca, rilanciare
sim/eq-serie/cascade-b3.cir.

Criterio (come verifica.py): scarto <= 0,5 dB dove LTspice sta sopra
-40 dB; sotto, anche il modello sotto -40 dB.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import serie  # noqa: E402
from verifica import leggi_log  # noqa: E402

RADICE = os.path.join(os.path.dirname(__file__), "..", "..")
LOG = "sim/eq-serie/cascade-b3.log"
FREQ = [20, 70, 125, 150, 250, 500, 1000, 2500, 5000, 10000, 20000, 35000]
NOMI_F = ["g20", "g70", "g125", "g150", "g250", "g500", "g1k", "g2k5",
          "g5k", "g10k", "g20k", "g35k"]
# modo m del netlist -> (xl, tlm, tmh, thh)
MODI = {
    1: ("detent", (0.5, 0.5, 0.5, 0.5)),
    2: ("LOW kill", (0.999, 0.5, 0.5, 0.5)),
    3: ("LOW-MID kill", (0.5, 0, 0.5, 0.5)),
    4: ("MID-HIGH kill", (0.5, 0.5, 0, 0.5)),
    5: ("HIGH kill", (0.5, 0.5, 0.5, 0)),
    6: ("ALL-KILL", (0.999, 0, 0, 0)),
    7: ("all-boost", (0.323, 1, 1, 1)),
    8: ("dub", (0.323, 0, 0, 1)),
    9: ("LOW boost", (0.323, 0.5, 0.5, 0.5)),
    10: ("HIGH boost", (0.5, 0.5, 0.5, 1)),
}
SOGLIA, TOLL = -40.0, 0.5


def el(xl, tlm, tmh, thh):
    # nel netlist thh = 0 e il kill: c = c_pot(thh) come per i medi
    return (xl, serie.c_pot(tlm), serie.c_pot(tmh), serie.c_pot(thh))


def main():
    percorso = os.path.join(RADICE, LOG)
    if not os.path.exists(percorso):
        print(f"MANCA {LOG}: rilanciare il netlist")
        return 1
    misure = leggi_log(percorso)
    errori, peggiore = 0, {}
    for fs in (None, 44100.0, 48000.0, 96000.0):
        etichetta = "analogico" if fs is None else f"fs {fs:.0f}"
        peg = 0.0
        for m, (nome, man) in MODI.items():
            step = 2 * (m - 1)          # passo con Rfmv 99,8k
            riga = []
            for f, nf in zip(FREQ, NOMI_F):
                ref = misure[nf][step]
                if fs is None:
                    mod = serie.db(serie.serie_analogico(f, el(*man)))
                else:
                    if f > 0.45 * fs:
                        continue
                    mod = serie.db(_os(f, fs, el(*man)))
                riga.append(f"{mod - ref:+.2f}")
                if ref >= SOGLIA:
                    d = abs(mod - ref)
                    peg = max(peg, d)
                    if d > TOLL:
                        errori += 1
                        print(f"  FUORI {etichetta} {nome} {f} Hz: "
                              f"LTspice {ref:+.2f}, modello {mod:+.2f}")
                elif mod >= SOGLIA:
                    errori += 1
                    print(f"  FUORI {etichetta} {nome} {f} Hz: LTspice "
                          f"{ref:+.1f}, modello {mod:+.1f} (sopra {SOGLIA})")
            if fs is None:
                print(f"  {nome:14s} " + " ".join(riga))
        peggiore[etichetta] = peg
        print(f"{etichetta}: scarto massimo {peg:.3f} dB")
    print("PASS" if errori == 0 else f"FAIL: {errori} punti fuori")
    return 0 if errori == 0 else 1


def _os(f, fs, man_el):
    from canale import HALFBAND, coef_halfband, risposta_halfband
    h1 = risposta_halfband(coef_halfband(*HALFBAND[1]), f, 2 * fs)
    h2 = risposta_halfband(coef_halfband(*HALFBAND[2]), f, 4 * fs)
    return h1 * h2 * serie.serie_digitale(f, 4 * fs, man_el) * h2 * h1


if __name__ == "__main__":
    sys.exit(main())
