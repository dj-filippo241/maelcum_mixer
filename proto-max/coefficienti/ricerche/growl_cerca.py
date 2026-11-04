import math, sys
sys.path.insert(0, "/Users/filippo/Documents/ClaudeCode/maelcum_mixer/proto-max/coefficienti")
from multiprocessing import Pool
import growl_bande as g
from taratura_sat import armoniche, rms

def corsa(a):
    gl, rsl, rs, f, amp = a
    fl, rf, gm = 250, 10e3, 6.0
    v = dict(g.VAR["D"]); v["FL"] = fl
    m = v["mid"]; v["mid"] = (gm, rf, rs, m[3], m[4], None)
    lo = v["low"]; v["low"] = (gl, lo[1], rsl, lo[3], lo[4], lo[5])
    s = g.Growl3(v, 1.0)
    dur = 2.0 if f < 200 else 0.5
    N = int(dur * g.FS); n0 = N - int(max(10 / f, 0.02) * g.FS)
    xs, ys = [], []
    for i in range(N):
        x = amp * math.sin(2 * math.pi * f * i / g.FS)
        y = s.passo(x)
        if i >= n0: xs.append(x); ys.append(y)
    h = armoniche(ys, f, g.FS, 0)
    return 100 * math.sqrt(sum(t * t for t in h[1:])) / h[0], 20 * math.log10(rms(ys) / rms(xs))

if __name__ == "__main__":
    combos = [(gl, rsl, rs) for gl in (20, 23) for rsl in (470, 150) for rs in (1000, 330)]
    casi = [(50, 1.096), (120, 1.096), (500, 1.096), (120, 3.466)]
    jobs = [c + k for c in combos for k in casi]
    with Pool(8) as pool:
        r = pool.map(corsa, jobs)
    for i, c in enumerate(combos):
        print(c, " | ".join(f"{n} {t:.0f}% {d:+.1f}" for n, (t, d) in zip(("SUB", "KICK", "MID", "KICK+10"), r[4*i:4*i+4])))
