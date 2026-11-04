import math, sys
sys.path.insert(0, "/Users/filippo/Documents/ClaudeCode/maelcum_mixer/proto-max/coefficienti")
from multiprocessing import Pool
import nastro_bande as n

LEGGI = {"oggi": lambda t: t, "inversa": lambda t: 1 - (1 - t) ** 2}

def corsa(a):
    legge, pos, f = a
    u = LEGGI[legge](pos)
    s = n.Bande(n.FS, n.VAR["B8"])
    s.inner.gn = 10 ** (n.al.NL_GMAX_DB * u / 20)
    m = n.fw.nastro_law(u)
    N = int(4.0 * n.FS); n0 = N - int(max(10 / f, 0.02) * n.FS)
    xs, ys = [], []
    for i in range(N):
        x = 1.096 * math.sin(2 * math.pi * f * i / n.FS)
        y = x + m * s.passo(x)
        if i >= n0: xs.append(x); ys.append(y)
    h = n.armoniche(ys, f, n.FS, 0)
    return legge, pos, f, 100 * math.sqrt(sum(t * t for t in h[1:])) / h[0], 20 * math.log10(n.rms(ys) / n.rms(xs))

if __name__ == "__main__":
    jobs = [(l, p, f) for l in LEGGI for p in (0.25, 0.5, 0.75) for f in (120, 500, 3000)]
    with Pool(8) as pool:
        for l, p, f, t, d in pool.map(corsa, jobs):
            print(f"{l:8s} {int(p*100):3d} % {f:5d} Hz  {t:5.2g} %  {d:+.1f} dB")
