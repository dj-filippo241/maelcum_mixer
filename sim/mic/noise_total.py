#!/usr/bin/env python3
"""Totali di rumore dai log LTspice (metodo casa, five-way §8.9):
densita' V(onoise) a 16 punti -> integrale trapezoidale di en^2 su 20 Hz-20 kHz,
piatto e pesato A (IEC 61672). MAI .meas INTEG (quirk LTspice 26.0.2).
Uso: python3 noise_total.py <log> [<log> ...]"""
import re, sys, math
F = [20, 31.5, 50, 80, 125, 200, 315, 500, 800, 1250, 2000, 3150, 5000, 8000, 12500, 20000]
def aw(f):
    f2 = f * f
    ra = (12194**2 * f2 * f2) / ((f2 + 20.6**2) * math.sqrt((f2 + 107.7**2) * (f2 + 737.9**2)) * (f2 + 12194**2))
    return ra * 10 ** (2.0 / 20)
def dbu(v): return 20 * math.log10(v / 0.7746)
def tab(log):
    s = open(log, errors="ignore").read(); out = {}
    for m in re.finditer(r"Measurement: (\w+)\n.*\n((?:\s+\d+\t.*\n)+)", s):
        out[m.group(1)] = [float(l.split("\t")[1]) for l in m.group(2).strip().split("\n")]
    return out
for log in sys.argv[1:]:
    t = tab(log); n = len(t["on1"]); print(log)
    for s in range(n):
        d = [t["on%d" % (i + 1)][s] for i in range(16)]
        flat = wtd = 0.0
        for i in range(15):
            df = F[i + 1] - F[i]
            flat += 0.5 * (d[i] ** 2 + d[i + 1] ** 2) * df
            wtd += 0.5 * ((d[i] * aw(F[i])) ** 2 + (d[i + 1] * aw(F[i + 1])) ** 2) * df
        g = t["g1k"][s]
        ein = dbu(math.sqrt(flat) / g) if g > 1e-3 else float("nan")
        print("  step %d: gain@1k %8.3f (%6.2f dB) | den@1k %7.1f nV/rtHz (in-ref %5.2f nV) | out %6.1f dBu / %6.1f dBu A | EIN %6.1f dBu"
              % (s + 1, g, 20 * math.log10(max(g, 1e-9)), d[9 - 1 + 0] * 1e9 if False else t["on9"][s] * 1e9 * 0 + d[8] * 1e9,
                 d[8] * 1e9 / max(g, 1e-9), dbu(math.sqrt(flat)), dbu(math.sqrt(wtd)), ein))
