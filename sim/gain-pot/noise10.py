#!/usr/bin/env python3
"""Totali di rumore dai log a 10 punti (nd20 ... nd20k) dei netlist del
ritorno FX: stesso metodo di sim/mic/noise_total.py (five-way §8.9), ma con
i punti 20/50/100/200/500/1k/2k/5k/10k/20k. Trapezi in scala logaritmica di
frequenza (0,5 * (a+b) su df, densita' quasi piatta: errore < 0,1 dB).
Uso: python3 sim/gain-pot/noise10.py <log> [<log> ...]"""
import math
import sys

F = [20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000]
N = ["nd20", "nd50", "nd100", "nd200", "nd500", "nd1k", "nd2k", "nd5k", "nd10k", "nd20k"]


def aw(f):
    f2 = f * f
    ra = (12194 ** 2 * f2 * f2) / ((f2 + 20.6 ** 2) * math.sqrt((f2 + 107.7 ** 2) * (f2 + 737.9 ** 2)) * (f2 + 12194 ** 2))
    return ra * 10 ** (2.0 / 20)


def dbu(v):
    return 20 * math.log10(v / 0.7746)


def tab(log):
    import re
    s = open(log, errors="ignore").read()
    out = {}
    for m in re.finditer(r"Measurement: (\w+)\n.*\n((?:\s+\d+\t.*\n)+)", s):
        out[m.group(1)] = [float(l.split("\t")[1]) for l in m.group(2).strip().split("\n")]
    return out


for log in sys.argv[1:]:
    t = tab(log)
    print(log)
    for s in range(len(t[N[0]])):
        d = [t[n][s] for n in N]
        flat = wtd = 0.0
        for i in range(len(F) - 1):
            df = F[i + 1] - F[i]
            flat += 0.5 * (d[i] ** 2 + d[i + 1] ** 2) * df
            wtd += 0.5 * ((d[i] * aw(F[i])) ** 2 + (d[i + 1] * aw(F[i + 1])) ** 2) * df
        g = t.get("g1k", [float("nan")] * 99)[s]
        print("  step %d: gain@1k %.3f | den@1k %6.1f nV/rtHz | out %6.1f dBu / %6.1f dBu A"
              % (s + 1, g, d[5] * 1e9, dbu(math.sqrt(flat)), dbu(math.sqrt(wtd))))
