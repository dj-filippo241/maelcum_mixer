"""Confronta GROWL e NASTRO di fiveway.py con la griglia LTspice.

Uso:  python3 proto-max/coefficienti/taratura_sat.py
Riferimento: sim/five-way/drive2-chain.cir (50 Hz) e drive2-chain-1k.cir,
letti con sim/drive2_tab.py (five-way §5bis.3). Stesse condizioni del
netlist: Vs2 parte da 2,1 V, 3 s di transitorio, misura sulle ultime
10 periodi; THD da 8 armoniche.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import fiveway as fw  # noqa: E402

FS4 = 4 * 48000.0
POS = (0.05, 0.10, 0.25, 0.50, 0.75, 1.00)
AMP = (0.173, 0.549, 1.096, 3.466)          # -16 / -6 / 0 / +10 dBu

# griglia LTspice (THD %, livello dB) [posizione][livello]
LT_GROWL_50 = [
    [(0.31, 0.12), (0.94, -0.02), (0.76, -0.14), (0.37, -0.29)],
    [(0.61, 0.24), (1.89, -0.04), (1.55, -0.29), (0.77, -0.59)],
    [(1.46, 0.58), (4.77, -0.10), (4.09, -0.74), (2.16, -1.55)],
    [(2.74, 1.12), (9.65, -0.17), (8.99, -1.53), (5.36, -3.39)],
    [(3.87, 1.63), (14.66, -0.23), (14.94, -2.36), (10.46, -5.65)],
    [(4.88, 2.12), (19.79, -0.26), (22.29, -3.22), (19.46, -8.42)]]
LT_GROWL_1K = [
    [(0.00, -0.02), (0.00, -0.02), (0.02, -0.01), (0.11, -0.00)],
    [(0.00, -0.03), (0.00, -0.03), (0.03, -0.03), (0.22, -0.00)],
    [(0.00, -0.08), (0.01, -0.08), (0.09, -0.07), (0.55, -0.01)],
    [(0.00, -0.16), (0.02, -0.16), (0.18, -0.15), (1.11, -0.02)],
    [(0.00, -0.24), (0.03, -0.24), (0.27, -0.22), (1.67, -0.02)],
    [(0.01, -0.32), (0.04, -0.32), (0.36, -0.29), (2.23, -0.03)]]
LT_NASTRO = [
    [(0.08, 0.00), (0.27, -0.01), (0.81, -0.07), (0.99, -0.25)],
    [(0.15, 0.01), (0.54, -0.02), (1.64, -0.13), (2.04, -0.50)],
    [(0.38, 0.01), (1.35, -0.04), (4.20, -0.33), (5.59, -1.30)],
    [(0.77, 0.03), (2.70, -0.07), (8.75, -0.66), (13.35, -2.78)],
    [(1.15, 0.04), (4.08, -0.11), (13.70, -0.98), (24.89, -4.49)],
    [(1.53, 0.06), (5.46, -0.14), (19.09, -1.29), (43.82, -6.39)]]


def armoniche(y, f, fs, n0):
    """Ampiezze delle armoniche 1-8 su un numero intero di periodi."""
    per = fs / f
    n = int(int((len(y) - n0) / per) * per)
    seg = y[len(y) - n:]
    off = len(y) - n
    out = []
    for h in range(1, 9):
        s = c = 0.0
        for i, v in enumerate(seg):
            ph = 2 * math.pi * h * f * (i + off) / fs
            s += v * math.sin(ph)
            c += v * math.cos(ph)
        out.append(2 * math.hypot(s, c) / n)
    return out


def rms(v):
    return math.sqrt(sum(t * t for t in v) / len(v))


def corsa(f, amp, quale):
    """Una corsa di 3 s; restituisce per ogni posizione (THD %, dB)."""
    sat = fw.Saturatori(FS4)
    # .ic del netlist: Vs2 = 2,1 V, il resto al suo punto di lavoro
    sat.vs2 = 2.1
    sat.idd, sat.vc = fw.jfet_passo(0.0, 2.1, 0.0, 2e-3)
    for _ in range(50):
        sat.idd, sat.vc = fw.jfet_passo(0.0, 2.1, sat.vc, sat.idd)
    n = int(3.0 * FS4)
    n0 = n - int(10 / f * FS4)
    xs, ds = [], []
    for i in range(n):
        x = amp * math.sin(2 * math.pi * f * i / FS4)
        y, dg, dt = sat.passo(x, 0.0, 0.0)
        if i >= n0:
            xs.append(x)
            ds.append(dg if quale == "g" else dt)
    ris = []
    for m in POS:
        y = [x + m * d for x, d in zip(xs, ds)]
        a = armoniche(y, f, FS4, 0)
        thd = 100 * math.sqrt(sum(t * t for t in a[1:])) / a[0]
        ris.append((thd, 20 * math.log10(rms(y) / rms(xs))))
    return ris


def main():
    peggio = {"thd": 0.0, "db": 0.0}
    for nome, f, quale, rif in (("GROWL 50 Hz", 50, "g", LT_GROWL_50),
                                ("GROWL 1 kHz", 1000, "g", LT_GROWL_1K),
                                ("NASTRO 50 Hz", 50, "t", LT_NASTRO)):
        print(f"{nome}: modello | LTspice  (THD % . dB)")
        col = [corsa(f, a, quale) for a in AMP]
        for p, m in enumerate(POS):
            riga = []
            for li in range(4):
                th, lv = col[li][p]
                rt, rl = rif[p][li]
                peggio["thd"] = max(peggio["thd"], abs(th - rt))
                peggio["db"] = max(peggio["db"], abs(lv - rl))
                riga.append(f"{th:5.2f} {lv:+.2f}|{rt:5.2f} {rl:+.2f}")
            print(f"  {int(m * 100):3d} %  " + "   ".join(riga))
    print(f"scarto massimo: THD {peggio['thd']:.2f} punti, "
          f"livello {peggio['db']:.2f} dB")


if __name__ == "__main__":
    main()
