"""Taratura e griglia delle alternative al NASTRO (alternative.py).

Uso:  python3 proto-max/coefficienti/taratura_alt.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import alternative as al  # noqa: E402
import fiveway as fw  # noqa: E402
from taratura_sat import armoniche, rms  # noqa: E402

FS = 192000.0
LIV = {"piano -16": 0.173, "nominale -6": 0.549, "mix 0": 1.096,
       "picchi +10": 3.466}


def corsa(classe, amp, f, mt, dur=None):
    dur = dur or max(0.3, 30 / f)
    s = classe(FS)
    n = int(dur * FS)
    n0 = n - int(max(10 / f, 0.02) * FS)
    xs, ys = [], []
    for i in range(n):
        x = amp * math.sin(2 * math.pi * f * i / FS)
        y = x + mt * s.passo(x)
        if i >= n0:
            xs.append(x)
            ys.append(y)
    a = armoniche(ys, f, FS, 0)
    thd = 100 * math.sqrt(sum(t * t for t in a[1:])) / a[0]
    return thd, 20 * math.log10(rms(ys) / rms(xs))


def tara_classe_a():
    """kc a pari livello RMS del ramo saturato al nominale, 1 kHz."""
    lo, hi = 0.05, 2.0
    for _ in range(30):
        al.B_K = (lo + hi) / 2
        al.B_RTS = 10e3 / al.B_K
        s = al.ClasseA(FS)
        n = int(0.05 * FS)
        sx = sw = 0.0
        for i in range(n):
            x = 0.549 * math.sin(2 * math.pi * 1000 * i / FS)
            w = s.passo(x) + x
            if i > n // 2:
                sx += x * x
                sw += w * w
        if sw < sx:
            lo = al.B_K
        else:
            hi = al.B_K
    return al.B_K


def tara_exciter():
    """+3 dB su un 5 kHz a -16 dBu interni, manopola a fine corsa."""
    lo, hi = 0.001, 1.0
    mt = fw.NASTRO_MAX
    for _ in range(30):
        al.EX_K = (lo + hi) / 2
        if corsa(al.Exciter, 0.173, 5000, mt)[1] < 3.0:
            lo = al.EX_K
        else:
            hi = al.EX_K
    return al.EX_K


def libero_a(pos):
    """Classe del NASTRO LIBERO con la spinta della posizione pos (0-1)."""
    def fa(fs):
        s = al.Libero(fs)
        s.gn = 10 ** (al.NL_GMAX_DB * pos / 20)
        return s
    return fa


def livello_regime(pos, amp, f=1000, fs=48000.0, dur=6.0):
    """Livello del NASTRO LIBERO a regime: la polarizzazione del JFET
    (Cb 2200 uF su 900) si assesta in ~4,5 s; si misura l'ultimo mezzo
    secondo di 6."""
    s = libero_a(pos)(fs)
    mt = fw.nastro_law(pos)
    n = int(dur * fs)
    sx = sy = 0.0
    for i in range(n):
        x = amp * math.sin(2 * math.pi * f * i / fs)
        y = x + mt * s.passo(x)
        if i >= n - int(0.5 * fs):
            sx, sy = sx + x * x, sy + y * y
    return 10 * math.log10(sy / sx)


def griglia_libero(f=1000, fs=96000.0, dur=6.0):
    """Griglia del NASTRO LIBERO a regime (THD % e livello)."""
    print(f"LIBERO a regime, {f} Hz (THD % . dB)  colonne {list(LIV)}")
    for pos in (0.25, 0.5, 0.75, 1.0):
        celle = []
        for amp in LIV.values():
            s = libero_a(pos)(fs)
            mt = fw.nastro_law(pos)
            n = int(dur * fs)
            n0 = n - int(max(10 / f, 0.02) * fs)
            xs, ys = [], []
            for i in range(n):
                x = amp * math.sin(2 * math.pi * f * i / fs)
                y = x + mt * s.passo(x)
                if i >= n0:
                    xs.append(x)
                    ys.append(y)
            a = armoniche(ys, f, fs, 0)
            celle.append((100 * math.sqrt(sum(t * t for t in a[1:])) / a[0],
                          20 * math.log10(rms(ys) / rms(xs))))
        print(f"  {int(pos * 100):3d} % | " + " | ".join(
            f"{t:5.2f} {d:+5.2f}" for t, d in celle))


def tara_libero():
    """+3 dB a regime sul mix di Filippo (0 dBu interni, 1 kHz), fine corsa."""
    lo, hi = 0.1, 0.3
    for _ in range(14):
        al.NL_K = (lo + hi) / 2
        if livello_regime(1.0, 1.096) < 3.0:
            lo = al.NL_K
        else:
            hi = al.NL_K
    return al.NL_K


def griglia(nome, classe, freq):
    print(f"{nome} a {freq} Hz (THD % . dB)  colonne {list(LIV)}")
    for pos in (0.25, 0.5, 0.75, 1.0):
        mt = fw.nastro_law(pos)
        cl = classe(pos) if classe is libero_a else classe
        celle = [corsa(cl, a, freq, mt) for a in LIV.values()]
        print(f"  {int(pos * 100):3d} % | " + " | ".join(
            f"{t:5.2f} {d:+5.2f}" for t, d in celle))


if __name__ == "__main__":
    print(f"CLASSE A: kc = {tara_classe_a():.4f}")
    print(f"EXCITER: ke = {tara_exciter():.5f}")
    griglia("COMPLETO", al.Completo, 1000)
    griglia("COMPLETO", al.Completo, 8000)
    griglia("COMPLETO", al.Completo, 80)
    griglia("EXCITER", al.Exciter, 5000)
    griglia("EXCITER", al.Exciter, 1000)
    griglia("CLASSE A", al.ClasseA, 1000)
    print(f"LIBERO: kl = {tara_libero():.4f}")
    griglia_libero(1000)
    griglia_libero(50)
