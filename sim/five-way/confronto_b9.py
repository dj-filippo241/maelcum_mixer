"""NASTRO A BANDE B9 (todo 245): modello contro LTspice.

Uso:  python3 sim/five-way/confronto_b9.py [base|6s]
  base = sim/five-way/nastro-b9-<f>.log, f = 50/120/500/3000/12000 Hz,
         durata 1,5 s sotto 1 kHz e 0,5 s sopra (come B8, RISULTATI-P2 §14)
  6s   = nastro-b9-500-6s.log e nastro-b9-3000-6s.log (durata delle tabelle
         di nastro_bande.py)
Modello: proto-max/coefficienti/nastro_bande.py, VAR["B9"], con la curva
inversa della manopola (nb.rotazione). Stesse condizioni nelle due parti:
partenza dal punto di lavoro, stessa durata, finestra max(10/f, 20 ms),
8 armoniche. THD Partial e Total dal log, livello = RMS(m)/RMS(y1).
Nei netlist .step amp e il primo (il piu interno): passo = 2*j(th) + k(amp).
Copia per B9 di proto-max/coefficienti/confronto_bande.py (non toccata).
"""
import math
import os
import re
import sys
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, "..", "..", "proto-max", "coefficienti"))
import fiveway as fw  # noqa: E402
import nastro_bande as nb  # noqa: E402
from taratura_sat import armoniche, rms  # noqa: E402

FS = 192000.0
NOME = "B9"
AMP = (1.096, 3.466)                 # 0 / +10 dBu interni (picco)
POS = (0.5, 1.0)
FREQ = (50, 120, 500, 3000, 12000)


def leggi(nome):
    s = open(os.path.join(QUI, nome + ".log"), errors="ignore").read()
    part, tot = {}, {}
    for blk in re.split(r"Fourier components of ", s)[1:]:
        for k, st in enumerate(re.split(r"\nstep\s+", "\n" + blk)[1:]):
            part[k] = float(re.search(r"Partial Harmonic Distortion:\s+(\S+)%", st).group(1))
            tot[k] = float(re.search(r"Total Harmonic Distortion:\s+(\S+)%", st).group(1))
    meas = {}
    for m in re.finditer(r"Measurement: (\w+)\n.*?\n((?:\s+\d+\s+\S+.*\n)+)", s):
        meas[m.group(1).lower()] = [float(r.split()[1]) for r in m.group(2).strip().split("\n")]
    return part, tot, meas


def corsa(args):
    f, pos, amp, dur = args
    s = nb.Bande(FS, nb.VAR[NOME])
    u = nb.rotazione(pos, NOME)
    s.inner.gn = 10 ** (nb.al.NL_GMAX_DB * u / 20)
    m = fw.nastro_law(u)
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


def confronto(freqs, suff, durf, pool):
    jobs = [(f, p, a, durf(f)) for f in freqs for p in POS for a in AMP]
    mod = dict(zip(jobs, pool.map(corsa, jobs)))
    print(f"\nNASTRO {NOME} {nb.VAR[NOME]} ({suff or 'base'})")
    print("modello THD dB | LTspice Partial Total dB, colonne 0 / +10 dBu")
    pg = [0.0, 0.0, "", ""]
    for f in freqs:
        part, tot, meas = leggi(f"nastro-b9-{f}{suff}")
        for j, p in enumerate(POS):
            celle = []
            for k, a in enumerate(AMP):
                tm, lm = mod[(f, p, a, durf(f))]
                st = 2 * j + k
                ll = 20 * math.log10(meas["rm"][st] / meas["xr"][st])
                if abs(tm - part[st]) > pg[0]:
                    pg[0], pg[2] = abs(tm - part[st]), f"{f} Hz {int(p*100)} % {a} V"
                if abs(lm - ll) > pg[1]:
                    pg[1], pg[3] = abs(lm - ll), f"{f} Hz {int(p*100)} % {a} V"
                celle.append(f"{tm:6.2f} {lm:+5.2f} | {part[st]:6.2f} {tot[st]:6.2f} {ll:+5.2f}")
            print(f"  {f:5d} Hz {int(p * 100):3d} %   " + "    ".join(celle))
    print(f"  scarto massimo: THD {pg[0]:.2f} punti ({pg[2]}), "
          f"livello {pg[1]:.2f} dB ({pg[3]})")


def main():
    quali = sys.argv[1:] or ["base", "6s"]
    with Pool(8) as pool:
        if "base" in quali:
            confronto(FREQ, "", lambda f: 1.5 if f < 1000 else 0.5, pool)
        if "6s" in quali:
            confronto((500, 3000), "-6s", lambda f: 6.0, pool)


if __name__ == "__main__":
    main()
