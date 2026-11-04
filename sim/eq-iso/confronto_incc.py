#!/usr/bin/env python3
"""Confronta l'isolator hardware a incroci C (iso-incc-ac.cir) col modello del
prototipo Max (proto-max/coefficienti/canale.py: INCROCI C, banda_pioneer).

Uso:  python3 sim/eq-iso/confronto_incc.py sim/eq-iso/iso-incc-ac.log

Python puro. Il prototipo si valuta a fs = 192 kHz (48 kHz x 4, come in gen~).
Per ogni caso e frequenza stampa: hardware lineare (law 0), hardware con taper
PIONEER ideale (law 1), prototipo PIONEER, e lo scarto law1 - prototipo
(modulo in dB, fase in gradi). Lo scarto law0 - prototipo e' la distanza fra il
pot che esiste a catalogo e la curva scelta all'ascolto.
"""
import math
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, "..", "..", "proto-max", "coefficienti"))
import canale  # noqa: E402

FS = 192000.0
CASI = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 21, 22, 23, 24, 25, 26, 30, 31]
C = 0.5
MANOPOLE = {0: (C, C, C, C), 1: (0, C, C, C), 2: (C, 0, C, C), 3: (C, C, 0, C),
            4: (C, C, C, 0), 5: (0, 0, 0, 0), 6: (1, C, C, C), 7: (C, 1, C, C),
            8: (C, C, 1, C), 9: (C, C, C, 1), 10: (1, 1, 1, 1), 20: (.05,) * 4,
            21: (.1,) * 4, 22: (.2,) * 4, 23: (.25,) * 4, 24: (.3,) * 4,
            25: (.4,) * 4, 26: (.75,) * 4, 30: (0, 0, C, C), 31: (C, C, 0, 0)}
NOMI = {0: "centro", 1: "LOW a zero", 2: "LOW-MID a zero", 3: "MID-HIGH a zero",
        4: "HIGH a zero", 5: "tutte a zero", 6: "LOW al massimo",
        7: "LOW-MID al massimo", 8: "MID-HIGH al massimo", 9: "HIGH al massimo",
        10: "tutte al massimo", 20: "tutte a 0,05", 21: "tutte a 0,1",
        22: "tutte a 0,2", 23: "tutte a 0,25", 24: "tutte a 0,3", 25: "tutte a 0,4",
        26: "tutte a 0,75", 30: "LOW + LOW-MID a zero", 31: "MID-HIGH + HIGH a zero"}
FREQ = [20, 50, 80, 150, 229, 350, 1050, 3150, 5000, 8000, 20000]


def leggi(log):
    testo = open(log, encoding="utf-8", errors="replace").read()
    out = {}
    for m in re.finditer(r"Measurement: g(\d+)\n.*?\n((?:\s+\d+\t\(.*\n)+)", testo):
        f = int(m.group(1))
        for riga in m.group(2).strip().splitlines():
            n, val = riga.split("\t")[:2]
            mag, fase = re.match(r"\(([-\d.e+]+)dB,([-\d.e+]+)", val).groups()
            out[(f, int(n))] = (float(mag), float(fase))
    return out


def proto(f, man, law):
    h = canale.isolator(f, FS, canale.INCROCI["C"], man, canale.PENDENZE["C"], law)
    return 20 * math.log10(max(abs(h), 1e-12)), math.degrees(math.atan2(h.imag, h.real))


def main():
    hw = leggi(sys.argv[1])
    peggio1 = peggio0 = 0.0
    for i, k in enumerate(CASI):
        print(f"\n## caso {k}: {NOMI[k]}")
        print("f        HW lin   HW PIO   proto PIO  scarto(PIO)  dfase   scarto(lin)")
        for f in FREQ:
            h0 = hw[(f, 2 * i + 1)]
            h1 = hw[(f, 2 * i + 2)]
            p = proto(f, MANOPOLE[k], canale.banda_pioneer)
            d1 = h1[0] - p[0]
            d0 = h0[0] - p[0]
            df = (h1[1] - p[1] + 180) % 360 - 180
            if p[0] > -40:
                peggio1 = max(peggio1, abs(d1))
                peggio0 = max(peggio0, abs(d0))
            print(f"{f:<7} {h0[0]:8.2f} {h1[0]:8.2f} {p[0]:9.2f} {d1:+10.2f} {df:+8.1f} {d0:+10.2f}")
    print(f"\nScarto massimo (dove il prototipo sta sopra -40 dB): "
          f"HW con taper PIONEER {peggio1:.2f} dB, HW lineare {peggio0:.2f} dB")


if __name__ == "__main__":
    main()
