"""Verifiche del modello di P3 (fx.py) contro LTspice e contro la SPEC.

Uso:  python3 proto-max/coefficienti/verifica_fx.py
- EQ2: formula analogica contro sim/fx/fx-eq2.log (6 modi x 7 frequenze);
  EQ2 digitale a 4x contro la formula analogica, fino a 20 kHz.
- REROUTE: griglia di 13 punti di fx-module §8.3.
"""

import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import fx  # noqa: E402

QUI = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(QUI, "..", "..", "sim", "fx", "fx-eq2.log")
MODI = {1: (0.5, 0.5), 2: (0.999, 0.5), 3: (0.323, 0.5), 4: (0.5, 0.0),
        5: (0.5, 1.0), 6: (0.999, 0.0)}
FREQ = {"g20": 20, "g120": 120, "g1k": 1000, "g4k5": 4500, "g10k": 10000,
        "g20k": 20000, "g35k": 35000}


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


def risposta(eq, f, fs, x, thh):
    n = int(max(0.05, 40 / f) * fs)
    n0 = n // 2
    ss = sc = cc = a1 = a2 = 0.0
    for i in range(n):
        u = math.sin(2 * math.pi * f * i / fs)
        y = eq.passo(u, x, thh)
        if i >= n0:
            s, c = u, math.cos(2 * math.pi * f * i / fs)
            ss, sc, cc = ss + s * s, sc + s * c, cc + c * c
            a1, a2 = a1 + y * s, a2 + y * c
    det = ss * cc - sc * sc
    a, b = (a1 * cc - a2 * sc) / det, (a2 * ss - a1 * sc) / det
    return fx.db(complex(a, b))


def main():
    lt = leggi_log()
    p_lt = p_dig = 0.0
    fs = 4 * 48000.0
    print("EQ2: analogico | LTspice | digitale 4x (dB)")
    for m, (x, thh) in MODI.items():
        celle = []
        for nome, f in FREQ.items():
            an = fx.db(fx.eq2_analogica(f, x, thh))
            dg = risposta(fx.Eq2(fs), f, fs, x, thh)
            p_lt = max(p_lt, abs(an - lt[(nome, m)]))
            if f <= 20000:      # sopra 24 kHz il halfband taglia comunque
                p_dig = max(p_dig, abs(an - dg))
            celle.append(f"{an:+6.2f}|{lt[(nome, m)]:+6.2f}|{dg:+6.2f}")
        print(f"  modo {m}: " + "  ".join(celle))
    print(f"  scarto massimo: analogico-LTspice {p_lt:.3f} dB, "
          f"digitale-analogico fino a 20 kHz {p_dig:.3f} dB")
    print("REROUTE: griglia 13 punti")
    griglia = ((1, 0), (0.975, -0.5), (0.95, -1), (0.9, -2.5), (0.85, -4),
               (0.775, -7), (0.7, -10), (0.575, -15), (0.45, -20),
               (0.325, -30), (0.2, -40), (0.1, -70), (0, -100))
    pr = max(abs(fx.reroute_db(t) - g) for t, g in griglia)
    print(f"  scarto massimo {pr:.2e} dB")
    # LTspice: op-amp reali, a 35 kHz la banda conta (0,13 dB); il digitale
    # a 4x schiaccia la HP2 verso Nyquist (0,24 dB a 20 kHz)
    ok = p_lt <= 0.15 and p_dig <= 0.3 and pr <= 1e-9
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
