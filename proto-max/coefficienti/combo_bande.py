"""GROWL D + NASTRO a bande insieme: THD e volume su ogni via.
Uso: python3 proto-max/coefficienti/combo_bande.py [variante NASTRO]"""
import math
import os
import sys
from multiprocessing import Pool

import growl_bande as g
import nastro_bande as n

NV = sys.argv[1] if len(sys.argv) > 1 else "B8"
VIE = n.VIE
CASI = ((1.0, 0.0), (0.0, 1.0), (1.0, 1.0), (0.5, 0.5))   # (GROWL, NASTRO)
AMP = (1.096, 3.466)


def corsa(args):
    mg, mt, amp, f = args
    gr = g.Growl3(g.VAR["D"], mg)
    na = n.Bande(n.FS, n.VAR[NV])
    na.inner.gn = 10 ** (n.al.NL_GMAX_DB * mt / 20)
    m = n.fw.nastro_law(mt)
    nn = int(6.0 * n.FS)
    n0 = nn - int(max(10 / f, 0.02) * n.FS)
    xs, ys = [], []
    for i in range(nn):
        x = amp * math.sin(2 * math.pi * f * i / n.FS)
        y1 = gr.passo(x) if mg > 0 else x
        y = y1 + m * na.passo(y1) if mt > 0 else y1
        if i >= n0:
            xs.append(x)
            ys.append(y)
    a = n.armoniche(ys, f, n.FS, 0)
    thd = 100 * math.sqrt(sum(t * t for t in a[1:])) / a[0]
    return thd, 20 * math.log10(n.rms(ys) / n.rms(xs))


if __name__ == "__main__":
    jobs = [(mg, mt, a, f) for a in AMP for mg, mt in CASI for _, f in VIE]
    with Pool(8) as p:
        r = p.map(corsa, jobs)
    k = 0
    for a, et in zip(AMP, ("0 dBu (mix)", "+10 dBu")):
        print(f"\n{et}: " + " | ".join(v for v, _ in VIE))
        for mg, mt in CASI:
            print(f"  GROWL {int(mg * 100):3d} % NASTRO {int(mt * 100):3d} %  "
                  + " | ".join(n.fmt(*r[k + j]) for j in range(len(VIE))))
            k += len(VIE)
