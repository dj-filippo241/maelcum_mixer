"""GROWL a tre bande (prova): basso forte, medi poco, alti quasi niente.

Struttura (realizzabile con op-amp):
  low  = LP2 Butterworth a FL di x          (come oggi, 350 Hz)
  rest = x - low
  mid  = LP1 a FM di rest                   (medi; sopra FM cala 6 dB/ott)
  high = rest - mid                         (somma esatta: low+mid+high = x)
  d_b  = K_b * HP1(clip_b(g_b * band)) - band   per ogni banda con clipper
  y    = x + m * (d_low + d_mid + d_high)
Manopola m: un tratto del pot doppio fa la miscela, l'altro la spinta
(g_b = 10^(G_b * m / 20), lineare in dB, come il GROWL LIBERO).

Clipper: invertente Rin 10k (spinta = Rin piu piccola), Rf, diodi in
feedback con R serie: 1 diodo in un verso, n nell'altro (asimmetria =
seconda armonica). R serie piccola = il clipper non torna lineare sui
picchi forti (oggi 2,2k: a +10 dBu la THD scende al 7,5 %).

Uso: python3 proto-max/coefficienti/growl_bande.py [variante ...]
"""
import math
import os
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fiveway as fw  # noqa: E402
from taratura_sat import armoniche, rms  # noqa: E402

FS = 192000.0
POS = (0.10, 0.25, 0.50, 0.75, 1.00)
AMP = (0.173, 0.549, 1.096, 3.466)   # -16 / -6 / 0 / +10 dBu di picco


def ramo(i_in, rf, rr, nvt):
    vd = nvt * math.log(1 + i_in / fw.D_IS)
    for _ in range(6):
        ex = math.exp(vd / nvt)
        f = fw.D_IS * (ex - 1) * (1 + rr / rf) + vd / rf - i_in
        df = fw.D_IS * ex / nvt * (1 + rr / rf) + 1 / rf
        vd = vd - f / df
    i = fw.D_IS * (math.exp(vd / nvt) - 1)
    return rf * (i_in - i)


def clip(v, rin, rf, rs, na, nb):
    i_in = v / rin
    ra, rb = rs + na * fw.D_RS, rs + nb * fw.D_RS
    if i_in >= 0:
        return ramo(i_in, rf, ra, na * fw.D_N * fw.VT27)
    return -ramo(-i_in, rf, rb, nb * fw.D_N * fw.VT27)


class Lp1:
    def __init__(self, f, fs=FS):
        self.g = math.tan(math.pi * f / fs)
        self.s = 0.0

    def passo(self, x):
        v = (x - self.s) * self.g / (1 + self.g)
        lp = v + self.s
        self.s = lp + v
        return lp


# varianti: per banda (spinta max dB, Rf, R serie, diodi a, diodi b, K)
# K = None: tarato a pari livello a piccolo segnale con la spinta max.
SCELTA = "D"                     # dec. 165 (Filippo: «250»)
VAR = {
    # il GROWL LIBERO di oggi, per confronto (solo basso)
    "oggi": dict(FL=350, FM=2500,
                 low=(18.0, 47e3, 2200.0, 1, 3, fw.LIB_K),
                 mid=None, high=None),
    # tre bande: basso piu spinto e duro, medi morbidi, alti quasi niente
    "A": dict(FL=350, FM=2500,
              low=(22.0, 47e3, 220.0, 1, 3, 0.62),
              mid=(10.0, 22e3, 1000.0, 2, 2, None),
              high=(0.0, 22e3, 2200.0, 2, 2, None)),
    # B: basso piu duro sui picchi, medi morbidi, alti puliti; LP2 come oggi
    "B": dict(FL=350, FM=2500,
              low=(20.0, 47e3, 470.0, 1, 3, 0.9),
              mid=(6.0, 10e3, 4700.0, 3, 3, None), high=None),
    # C: come B col filtro del basso a 4 poli (i medi non entrano nei diodi del basso)
    "C": dict(FL=350, FM=2500, NL=4,
              low=(20.0, 47e3, 470.0, 1, 3, 0.9),
              mid=(6.0, 10e3, 4700.0, 3, 3, None), high=None),
    "D": dict(FL=250, FM=2500, NL=4,
              low=(20.0, 47e3, 470.0, 1, 3, 0.9),
              mid=(6.0, 10e3, 4700.0, 3, 3, None), high=None),
    "E": dict(FL=200, FM=2500, NL=4,
              low=(20.0, 47e3, 470.0, 1, 3, 0.9),
              mid=(6.0, 10e3, 4700.0, 3, 3, None), high=None),
}


class Growl3:
    def __init__(self, v, m, fs=FS):
        self.v = v
        self.lp = fw.Svf()
        self.lp2 = fw.Svf() if v.get("NL", 2) == 4 else None
        self.g_lp = fw.g_di(v["FL"], fs)
        self.lm = Lp1(v["FM"], fs)
        self.hp = [fw.Hp1(1.0, fs) for _ in range(3)]
        self.imposta(m)

    def imposta(self, m):
        """Manopola GROWL (0-1): miscela e spinta insieme (pot doppio)."""
        v = self.v
        self.m = m
        self.par = []
        for b in ("low", "mid", "high"):
            p = v[b]
            if p is None:
                self.par.append(None)
                continue
            gmax, rf, rs, na, nb, k = p
            g = 10 ** (gmax * m / 20)
            rin = 10e3 / g
            if k is None:                    # pari livello a piccolo segnale
                k = 1 / (rf / 10e3 * 10 ** (gmax / 20))
            self.par.append((rin, rf, rs, na, nb, k))

    def passo(self, x):
        return x + self.m * self.delta(x)

    def delta(self, x):
        """Il ramo sporco meno il pulito, prima della miscela m."""
        low = self.lp.passo(x, self.g_lp, 1 / fw.Q_BW)[0]
        if self.lp2 is not None:
            low = self.lp2.passo(low, self.g_lp, 1 / fw.Q_BW)[0]
        rest = x - low
        mid = self.lm.passo(rest)
        high = rest - mid
        d = 0.0
        for j, band in enumerate((low, mid, high)):
            p = self.par[j]
            if p is None:
                continue
            rin, rf, rs, na, nb, k = p
            d += k * self.hp[j].passo(clip(band, rin, rf, rs, na, nb)) - band
        return d


def corsa(args):
    nome, pos, amp, f = args
    s = Growl3(VAR[nome], pos)
    dur = 3.0 if f < 200 else 0.5
    n = int(dur * FS)
    n0 = n - int(max(10 / f, 0.02) * FS)
    xs, ys = [], []
    for i in range(n):
        x = amp * math.sin(2 * math.pi * f * i / FS)
        y = s.passo(x)
        if i >= n0:
            xs.append(x)
            ys.append(y)
    a = armoniche(ys, f, FS, 0)
    thd = 100 * math.sqrt(sum(t * t for t in a[1:])) / a[0]
    return thd, 20 * math.log10(rms(ys) / rms(xs))


def fmt(t, d):
    return (f"{t:.2g} %" if t < 10 else f"{t:.0f} %") + f" · {d:+.1f}"


if __name__ == "__main__":
    nomi = sys.argv[1:] or list(VAR)
    freqs = (50, 120, 500, 1000, 3000, 12000)
    with Pool(8) as pool:
        for nome in nomi:
            jobs = [(nome, p, a, f) for f in freqs for p in POS for a in AMP]
            r = pool.map(corsa, jobs)
            k = 0
            for f in freqs:
                print(f"\n{nome}, {f} Hz   (-16 / -6 / 0 / +10 dBu)")
                for p in POS:
                    print(f"  {int(p * 100):3d} %  " + "  |  ".join(
                        fmt(*r[k + j]) for j in range(4)))
                    k += 4
