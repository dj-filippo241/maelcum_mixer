"""NASTRO LIBERO e NASTRO LIBERO A BANDE: THD su ogni via del 5-way.

Vie (crossover E 80/170/1,2k/6k): SUB 50 Hz, KICK 120 Hz, MID 500 Hz,
HIGH 3 kHz, SUPER 12 kHz.

A bande = enfasi prima del JFET e de-enfasi inversa dopo (nel ramo
saturato): a piccolo segnale il ramo resta piatto, ma ogni frequenza
arriva al JFET con un livello diverso, quindi distorce di piu o di meno.
  E = E_low * E_high
  E_low : taglio dei bassi, shelf 1o ordine zero FZ / polo FP (sotto FZ
          -20 log(FP/FZ) dB, sopra FP 0 dB)
  E_high: taglio dei super, polo FA / zero FB (sopra FB -20 log(FB/FA))
Uso: python3 proto-max/coefficienti/nastro_bande.py [variante ...]
"""
import math
import os
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fiveway as fw  # noqa: E402
import alternative as al  # noqa: E402
from taratura_sat import armoniche, rms  # noqa: E402

FS = 192000.0
VIE = (("SUB", 50), ("KICK", 120), ("MID", 500), ("HIGH", 3000),
       ("SUPER", 12000))
POS = (0.25, 0.50, 0.75, 1.00)
AMP = (0.549, 1.096, 3.466)          # -6 / 0 / +10 dBu di picco

SCELTA = "B8"                    # dec. 166
VAR = {
    "LIBERO": None,
    # (FZ, FP, FA, FB)
    "B1": (80.0, 640.0, 5000.0, 15000.0),
    "B2": (60.0, 600.0, 4000.0, 16000.0),
    "B3": (100.0, 600.0, 6000.0, 18000.0),
    # (FZ, FP, FA, FB, celle alte, riduzione de-enfasi bassi dB, alti dB)
    "B4": (80.0, 640.0, 5000.0, 10000.0, 2, 7.0, 7.0),
    "B5": (80.0, 640.0, 5000.0, 10000.0, 2, 5.0, 5.0),
    # + celle basse (taglio a 2 celle = 12 dB/ottava)
    "B6": (100.0, 400.0, 5000.0, 10000.0, 2, 7.0, 7.0, 2),
    "B7": (80.0, 400.0, 5000.0, 10000.0, 2, 7.0, 7.0, 2),
    # B7 col volume di sub e kick riportato giu (de-enfasi bassi -12 dB)
    "B8": (80.0, 400.0, 5000.0, 10000.0, 2, 12.0, 7.0, 2),
}


class Bande:
    def __init__(self, fs, p):
        fz, fp, fa, fb = p[:4]
        nh, rl, rh = (p[4], p[5], p[6]) if len(p) > 4 else (1, 0.0, 0.0)
        nl = p[7] if len(p) > 7 else 1
        rl = rl / nl
        self.cl = fz / fp
        self.ab = fa / fb
        self.gl = (fp / fz) * 10 ** (-rl / 20)   # guadagno DC della de-enfasi
        self.gh = (fb / fa) * 10 ** (-rh / 20)   # guadagno HF della de-enfasi
        self.e_lo = [al.Uno(fp, fs) for _ in range(nl)]
        self.e_hi = [al.Uno(fa, fs) for _ in range(nh)]
        self.d_lo = [al.Uno(fp / self.gl, fs) for _ in range(nl)]
        self.d_hi = [al.Uno(fa * self.gh, fs) for _ in range(nh)]  # polo resta a FA
        self.inner = al.Libero(fs)

    def passo(self, y1):
        u = y1
        for e in self.e_lo:
            lp, hp = e.passo(u)
            u = self.cl * lp + hp                   # taglio dei bassi
        for e in self.e_hi:
            lp, hp = e.passo(u)
            u = lp + self.ab * hp                   # taglio dei super
        w = self.inner.passo(u) + u                 # ramo saturato (pulito = u)
        for d in self.d_hi:
            lp, hp = d.passo(w)
            w = lp + self.gh * hp                   # de-enfasi super
        for d in self.d_lo:
            lp, hp = d.passo(w)
            w = self.gl * lp + hp                   # de-enfasi bassi
        return w - y1


def corsa(args):
    nome, pos, amp, f = args
    p = VAR[nome]
    s = al.Libero(FS) if p is None else Bande(FS, p)
    (s if p is None else s.inner).gn = 10 ** (al.NL_GMAX_DB * pos / 20)
    m = fw.nastro_law(pos)
    dur = 6.0
    n = int(dur * FS)
    n0 = n - int(max(10 / f, 0.02) * FS)
    xs, ys = [], []
    for i in range(n):
        x = amp * math.sin(2 * math.pi * f * i / FS)
        y = x + m * s.passo(x)
        if i >= n0:
            xs.append(x)
            ys.append(y)
    a = armoniche(ys, f, FS, 0)
    thd = 100 * math.sqrt(sum(t * t for t in a[1:])) / a[0]
    return thd, 20 * math.log10(rms(ys) / rms(xs))


def fmt(t, d):
    return (f"{t:.2g} %" if t < 10 else f"{t:.0f} %") + f" {d:+.1f}"


if __name__ == "__main__":
    nomi = sys.argv[1:] or list(VAR)
    with Pool(8) as pool:
        for nome in nomi:
            jobs = [(nome, p, a, f) for a in AMP for p in POS
                    for _, f in VIE]
            r = pool.map(corsa, jobs)
            k = 0
            for a, et in zip(AMP, ("-6 dBu", "0 dBu (mix)", "+10 dBu")):
                print(f"\n{nome} {VAR[nome]}, {et}: " +
                      " | ".join(v for v, _ in VIE))
                for p in POS:
                    print(f"  {int(p * 100):3d} %  " + " | ".join(
                        fmt(*r[k + j]) for j in range(len(VIE))))
                    k += len(VIE)
