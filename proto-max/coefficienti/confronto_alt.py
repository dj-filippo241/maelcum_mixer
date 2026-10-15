"""Alternative al NASTRO: modello (alternative.py) contro LTspice.

Uso:  python3 proto-max/coefficienti/confronto_alt.py
Legge sim/five-way/alt-*.log (stesse condizioni: partenza dal punto di
lavoro, stessa durata, stessa finestra, 8 armoniche, THD Partial).
"""

import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import alternative as al  # noqa: E402
from taratura_sat import armoniche, rms  # noqa: E402

QUI = os.path.dirname(os.path.abspath(__file__))
SIM = os.path.join(QUI, "..", "..", "sim", "five-way")
FS = 192000.0
AMP = (0.173, 0.549, 1.096, 3.466)
MISCELE = (("25 %", "m25", "r25", 0.0425), ("50 %", "m50", "r50", 0.085),
           ("75 %", "m75", "r75", 0.4675), ("100 %", "m99", "r99", 0.85))
CASI = (("COMPLETO 1 kHz", "alt-completo", al.Completo, 1000, 1.5),
        ("COMPLETO 8 kHz", "alt-completo-8000", al.Completo, 8000, 1.5),
        ("COMPLETO 80 Hz", "alt-completo-80", al.Completo, 80, 1.5),
        ("EXCITER 5 kHz", "alt-exciter", al.Exciter, 5000, 0.3),
        ("CLASSE A 1 kHz", "alt-classe-a", al.ClasseA, 1000, 1.5))


def leggi_log(nome):
    s = open(os.path.join(SIM, nome + ".log"), errors="ignore").read()
    thd = {}
    for blk in re.split(r"Fourier components of ", s)[1:]:
        nodo = blk.split("\n", 1)[0].strip().lower()
        for k, st in enumerate(re.split(r"\nstep\s+", "\n" + blk)[1:]):
            p = re.search(r"Partial Harmonic Distortion:\s+(\S+)%", st)
            thd[(nodo, k)] = float(p.group(1))
    meas = {}
    for m in re.finditer(r"Measurement: (\w+)\n.*?\n((?:\s+\d+\s+\S+.*\n)+)",
                         s):
        vals = [float(r.split()[1]) for r in m.group(2).strip().split("\n")]
        meas[m.group(1).lower()] = vals
    return thd, meas


def modello(classe, f, dur, amp):
    s = classe(FS)
    n = int(dur * FS)
    n0 = n - int(max(10 / f, 0.02) * FS)
    xs, ds = [], []
    for i in range(n):
        x = amp * math.sin(2 * math.pi * f * i / FS)
        d = s.passo(x)
        if i >= n0:
            xs.append(x)
            ds.append(d)
    out = []
    for _, _, _, m in MISCELE:
        y = [x + m * d for x, d in zip(xs, ds)]
        a = armoniche(y, f, FS, 0)
        out.append((100 * math.sqrt(sum(t * t for t in a[1:])) / a[0],
                    20 * math.log10(rms(y) / rms(xs))))
    return out


def main():
    peggio = {}
    for nome, log, classe, f, dur in CASI:
        thd, meas = leggi_log(log)
        print(f"{nome}: modello | LTspice (THD % . dB), colonne -16/-6/0/+10")
        mod = [modello(classe, f, dur, a) for a in AMP]
        p = [0.0, 0.0]
        for j, (et, nodo, rr, _) in enumerate(MISCELE):
            celle = []
            for k in range(4):
                tm, lm = mod[k][j]
                tl = thd[(f"v({nodo})", k)]
                ll = 20 * math.log10(meas[rr][k] / meas["xr"][k])
                p = [max(p[0], abs(tm - tl)), max(p[1], abs(lm - ll))]
                celle.append(f"{tm:5.2f} {lm:+5.2f}|{tl:5.2f} {ll:+5.2f}")
            print(f"  {et:>5} " + "  ".join(celle))
        peggio[nome] = p
        print(f"  scarto massimo: THD {p[0]:.2f} punti, livello {p[1]:.2f} dB")
    return peggio


if __name__ == "__main__":
    main()
