"""Verifica del P0: il modello digitale dell'isolator contro LTspice.

Uso:  python3 proto-max/coefficienti/verifica.py
Legge sim/eq-iso/iso-c-ac.log (incroci A, col contatto di fondo corsa) e
sim/eq-iso/iso-ac-b.log (incroci B, senza contatto: fondo a -54 dB).
I .log sono fuori da git: se mancano, rilanciare i due netlist.

Criterio (piano v0.2 §3): scarto <= 0,5 dB dove LTspice sta sopra -40 dB;
sotto -40 dB basta che anche il modello stia sotto -40 (un taglio cosi
profondo e silenzio per l'orecchio, e lo scarto in dB non ha senso).
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import canale  # noqa: E402

RADICE = os.path.join(os.path.dirname(__file__), "..", "..")
# kcase -> posizione delle 4 manopole (stessa tabella dei netlist)
CASI = {
    0: ((0.5, 0.5, 0.5, 0.5), "tutte al centro"),
    1: ((0, 0.5, 0.5, 0.5), "LOW a zero"),
    2: ((0.5, 0, 0.5, 0.5), "LOW-MID a zero"),
    3: ((0.5, 0.5, 0, 0.5), "MID-HIGH a zero"),
    4: ((0.5, 0.5, 0.5, 0), "HIGH a zero"),
    5: ((0, 0, 0, 0), "tutte a zero"),
    10: ((1, 1, 1, 1), "tutte al massimo"),
    12: ((0, 0, 0.5, 0.5), "LOW + LOW-MID a zero"),
    13: ((0.5, 0.5, 0, 0), "MID-HIGH + HIGH a zero"),
}
# incroci -> (log, step del netlist, frequenze misurate)
LOG = {
    "A": ("sim/eq-iso/iso-c-ac.log", [0, 1, 2, 3, 4, 5, 10, 12, 13],
          [20, 50, 80, 150, 274, 500, 1118, 2500, 5000, 8000, 20000, 35000]),
    "B": ("sim/eq-iso/iso-ac-b.log", [0, 1, 2, 3, 4, 5],
          [20, 50, 80, 150, 250, 500, 1600, 2500, 5000, 8000, 20000, 35000]),
}
SOGLIA = -40.0
TOLL = 0.5


def leggi_log(percorso):
    """{nome misura: [dB per step]} dai blocchi Measurement del log."""
    testo = open(percorso, encoding="latin-1").read()
    misure = {}
    for blocco in re.split(r"\nMeasurement: ", testo)[1:]:
        nome = blocco.split("\n", 1)[0].strip()
        valori = re.findall(r"^\s*\d+\s+\(([-\d.e+]+)dB,", blocco, re.M)
        misure[nome] = [float(v) for v in valori]
    return misure


def main():
    peggiore = 0.0
    errori = 0
    for chiave, (rel, steps, freq) in LOG.items():
        percorso = os.path.join(RADICE, rel)
        if not os.path.exists(percorso):
            print(f"MANCA {rel}: rilanciare il netlist")
            errori += 1
            continue
        misure = leggi_log(percorso)
        incroci = canale.INCROCI[chiave]
        print(f"\nIncroci {chiave} {incroci} - {rel}")
        for fs in (44100.0, 48000.0, 96000.0):
            peg_fs = 0.0
            for i, kcase in enumerate(steps):
                manopole, nome = CASI[kcase]
                for f in freq:
                    if f > 0.45 * fs:
                        continue
                    ref = misure[f"g{f}"][i]
                    mod = canale.db(canale.isolator_os(f, fs, incroci, manopole))
                    if ref >= SOGLIA:
                        d = abs(mod - ref)
                        peg_fs = max(peg_fs, d)
                        if d > TOLL:
                            errori += 1
                            print(f"  FUORI fs {fs:.0f} {nome} {f} Hz: "
                                  f"LTspice {ref:+.2f}, modello {mod:+.2f}")
                    elif mod >= SOGLIA:
                        errori += 1
                        print(f"  FUORI fs {fs:.0f} {nome} {f} Hz: LTspice "
                              f"{ref:+.1f}, modello {mod:+.1f} (sopra {SOGLIA})")
            peggiore = max(peggiore, peg_fs)
            print(f"  fs {fs:.0f} Hz: scarto massimo {peg_fs:.3f} dB")
    print(f"\nScarto massimo complessivo: {peggiore:.3f} dB (tolleranza {TOLL})")
    print("PASS" if errori == 0 else f"FAIL: {errori} punti fuori")
    return 0 if errori == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
