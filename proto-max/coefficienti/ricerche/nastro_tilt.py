import math, sys
sys.path.insert(0, "/Users/filippo/Documents/ClaudeCode/maelcum_mixer/proto-max/coefficienti")
from multiprocessing import Pool
import nastro_bande as n
al = n.al
FS = 192000.0
VIE = {"SUB": 50, "KICK": 120, "MID": 500, "HIGH": 3000, "SUPER": 12000}

class Tilt(n.Bande):
    """Bande + inclinazione dei medi: polo fm / zero fm*r prima, inverso dopo."""
    def __init__(self, fs, p, fm, r):
        super().__init__(fs, p)
        self.at = 1 / r
        self.e_t = al.Uno(fm, fs)
        self.d_t = al.Uno(fm * r, fs)   # dopo: lp + r*hp con polo a fm*r? usa la forma di Bande
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
        lp, hp = self.d_t.passo(w); w = lp + (1 / self.at) * hp
        for d in self.d_lo:
            lp, hp = d.passo(w); w = self.gl * lp + hp
        return w - y1

def corsa(a):
    fm, r, fa, rb, nh, via = a
    f = VIE[via]
    p = list(n.VAR["B8"]); p[0], p[1], p[7], p[2], p[3], p[4] = 30, 140, 3, fa, rb * fa, nh
    s = Tilt(FS, tuple(p), fm, r)
    s.inner.gn = 10 ** (12 / 20)
    N = int(1.5 * FS); n0 = N - int(max(10 / f, 0.02) * FS)
    xs, ys = [], []
    for i in range(N):
        x = 1.096 * math.sin(2 * math.pi * f * i / FS)
        y = x + 0.85 * s.passo(x)
        if i >= n0: xs.append(x); ys.append(y)
    h = n.armoniche(ys, f, FS, 0)
    return 100 * math.sqrt(sum(t * t for t in h[1:])) / h[0], 20 * math.log10(n.rms(ys) / n.rms(xs))

if __name__ == "__main__":
    combos = [(1000, 3, fa, rb, 1) for fa in (6000, 9000) for rb in (1.2, 1.35)]
    jobs = [c + (v,) for c in combos for v in ("SUB", "MID", "HIGH", "SUPER")]
    with Pool(8) as pool:
        res = pool.map(corsa, jobs)
    for i, c in enumerate(combos):
        print(c, " | ".join(f"{v} {t:.1f}% {d:+.1f}" for v, (t, d) in zip(("SUB", "MID", "HIGH", "SUPER"), res[4*i:4*i+4])))
