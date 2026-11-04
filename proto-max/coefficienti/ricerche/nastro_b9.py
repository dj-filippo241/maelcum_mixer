"""Ricerca B9: NASTRO a bande coi numeri di Filippo (todo 245).
Fine corsa, mix 0 dBu interni, THD e volume per via. Parametri:
(fz, fp, nl, rl, fm, r, rt, fa, fb, nh, rh[, kv dB]): bassi nl celle fz/fp con
de-enfasi ridotta di rl dB in tutto; inclinazione polo fm / zero fm*r
con de-enfasi ridotta di rt dB in alto; super nh celle fa/fb, rh dB."""
import math, sys
sys.path.insert(0, "/Users/filippo/Documents/ClaudeCode/maelcum_mixer/proto-max/coefficienti")
from multiprocessing import Pool
import nastro_bande as n
al = n.al
FS = 192000.0
VIE = {"SUB": 50, "KICK": 120, "MID": 500, "HIGH": 3000, "SUPER": 12000}


class B9:
    def __init__(self, fs, p):
        fz, fp, nl, rl, fm, r, rt, fa, fb, nh, rh = p[:11]
        self.kv = 10 ** ((p[11] if len(p) > 11 else 0.0) / 20)
        self.cl = fz / fp
        self.gl = (fp / fz) * 10 ** (-rl / nl / 20)
        self.at = 1 / r
        self.gt = r * 10 ** (-rt / 20)
        self.ab = fa / fb
        self.gh = (fb / fa) * 10 ** (-rh / nh / 20)
        self.e_lo = [al.Uno(fp, fs) for _ in range(nl)]
        self.e_t = al.Uno(fm, fs)
        self.e_hi = [al.Uno(fa, fs) for _ in range(nh)]
        self.d_hi = [al.Uno(fa * self.gh, fs) for _ in range(nh)]
        self.d_t = al.Uno(fm * self.gt, fs)
        self.d_lo = [al.Uno(fp / self.gl, fs) for _ in range(nl)]
        self.inner = al.Libero(fs)

    def passo(self, y1):
        u = y1
        for e in self.e_lo:
            lp, hp = e.passo(u); u = self.cl * lp + hp
        lp, hp = self.e_t.passo(u); u = lp + self.at * hp
        for e in self.e_hi:
            lp, hp = e.passo(u); u = lp + self.ab * hp
        w = self.inner.passo(u) + u
        for d in self.d_hi:
            lp, hp = d.passo(w); w = lp + self.gh * hp
        lp, hp = self.d_t.passo(w); w = lp + self.gt * hp
        for d in self.d_lo:
            lp, hp = d.passo(w); w = self.gl * lp + hp
        return self.kv * w - y1


def corsa(a):
    p, via, amp, dur = a
    f = VIE[via]
    s = B9(FS, p)
    s.inner.gn = 10 ** (al.NL_GMAX_DB / 20)
    m = n.fw.nastro_law(1.0)
    N = int(dur * FS); n0 = N - int(max(10 / f, 0.02) * FS)
    xs, ys = [], []
    for i in range(N):
        x = amp * math.sin(2 * math.pi * f * i / FS)
        y = x + m * s.passo(x)
        if i >= n0: xs.append(x); ys.append(y)
    h = n.armoniche(ys, f, FS, 0)
    return 100 * math.sqrt(sum(t * t for t in h[1:])) / h[0], 20 * math.log10(n.rms(ys) / n.rms(xs))


def tabella(cands, amp=1.096, dur=1.5):
    jobs = [(c, v, amp, dur) for c in cands for v in VIE]
    with Pool(8) as pool:
        res = pool.map(corsa, jobs)
    for i, c in enumerate(cands):
        print(c, " | ".join(f"{v} {t:.1f}% {d:+.1f}" for v, (t, d) in zip(VIE, res[5*i:5*i+5])), flush=True)


if __name__ == "__main__":
    base = (30, 140, 3, 12.0, 1000, 3, 0.0, 9000, 10800, 1, 7.0)
    tabella([base])
