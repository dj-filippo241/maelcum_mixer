import math, sys, itertools
sys.path.insert(0, "/Users/filippo/Documents/ClaudeCode/maelcum_mixer/proto-max/coefficienti")
from multiprocessing import Pool
import nastro_bande as n
FS = 192000.0
VIE = {"SUB": 50, "KICK": 120, "MID": 500, "HIGH": 3000, "SUPER": 12000}

def corsa(a):
    p, kw, mm, via, dur = a
    f = VIE[via]
    s = n.Bande(FS, p)
    s.inner.gn = 10 ** (12 / 20)
    N = int(dur * FS); n0 = N - int(max(10 / f, 0.02) * FS)
    xs, ys = [], []
    for i in range(N):
        x = 1.096 * math.sin(2 * math.pi * f * i / FS)
        d = s.passo(x)
        y = x + mm * (kw * (d + x) - x)
        if i >= n0: xs.append(x); ys.append(y)
    h = n.armoniche(ys, f, FS, 0)
    return 100 * math.sqrt(sum(t * t for t in h[1:])) / h[0], 20 * math.log10(n.rms(ys) / n.rms(xs))

if __name__ == "__main__":
    base = list(n.VAR["B8"])
    vie = sys.argv[1].split(",")
    dur = float(sys.argv[2])
    combos = eval(sys.argv[3])   # lista di (fz, fp, nl, fa, rb, nh, kw, mm)
    jobs, keys = [], []
    for c in combos:
        fz, fp, nl, fa, rb, nh, kw, mm = c
        p = base[:]; p[0], p[1], p[7], p[2], p[3], p[4] = fz, fp, nl, fa, fa * rb, nh
        for v in vie:
            jobs.append((tuple(p), kw, mm, v, dur)); keys.append((c, v))
    with Pool(8) as pool:
        r = pool.map(corsa, jobs)
    cur = None
    for (c, v), (t, d) in zip(keys, r):
        if c != cur:
            print(); print(c, end="  "); cur = c
        print(f"{v} {t:.1f}% {d:+.1f}", end=" | ")
    print()
