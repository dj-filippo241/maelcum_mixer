"""GROWL a bande (dec. 165) e NASTRO a bande (dec. 166): modello contro LTspice.

Uso:  python3 proto-max/coefficienti/confronto_bande.py [growl|nastro|op]
  6s = NASTRO a 500 e 3000 Hz con 6 s (nastro-bande-<f>-6s), la durata
       di nastro_bande.py e delle tabelle di RISULTATI-P2 par. 12
  op = op-amp ideale (growl-bande-<f>) contro OP1654 di libreria
       (growl-bande-op-<f>): stesso circuito.
Legge sim/five-way/growl-bande-<f>.log e nastro-bande-<f>.log (todo 234).
Stesse condizioni nelle due parti: partenza dal punto di lavoro, stessa
durata (GROWL 3 s sotto 200 Hz e 0,5 s sopra; NASTRO 1,5 s sotto 1 kHz e
0,5 s sopra), finestra max(10/f, 20 ms), 8 armoniche, THD Partial.
Nei netlist .step amp e il primo (il piu interno): passo = 3*j(th) + k(amp).
Il modello si legge da growl_bande.VAR[SCELTA] e nastro_bande.VAR[SCELTA]:
se quei parametri cambiano, vanno cambiati anche i .param dei netlist.
"""
import math
import os
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fiveway as fw  # noqa: E402
import growl_bande as gb  # noqa: E402
import nastro_bande as nb  # noqa: E402
from confronto_alt import leggi_log  # noqa: E402
from taratura_sat import armoniche, rms  # noqa: E402

FS = 192000.0
AMP = (0.549, 1.096, 3.466)          # -6 / 0 / +10 dBu interni (picco)
POS = (0.5, 1.0)
GROWL_F = (50, 120, 500, 1000, 3000, 12000)
NASTRO_F = (50, 120, 500, 3000, 12000)


def misura(xs, ys, f):
    a = armoniche(ys, f, FS, 0)
    thd = 100 * math.sqrt(sum(t * t for t in a[1:])) / a[0]
    return thd, 20 * math.log10(rms(ys) / rms(xs))


def corsa(args):
    tipo, f, pos, amp = args[:4]
    if tipo == "growl":
        s = gb.Growl3(gb.VAR[gb.SCELTA], pos, FS)
        dur = 3.0 if f < 200 else 0.5
        fn = s.passo
    else:
        s = nb.Bande(FS, nb.VAR[nb.SCELTA])
        s.inner.gn = 10 ** (nb.al.NL_GMAX_DB * pos / 20)
        m = fw.nastro_law(pos)
        dur = args[4] if len(args) > 4 else (1.5 if f < 1000 else 0.5)

        def fn(x):
            return x + m * s.passo(x)
    n = int(dur * FS)
    n0 = n - int(max(10 / f, 0.02) * FS)
    xs, ys = [], []
    for i in range(n):
        x = amp * math.sin(2 * math.pi * f * i / FS)
        y = fn(x)
        if i >= n0:
            xs.append(x)
            ys.append(y)
    return misura(xs, ys, f)


def confronto(tipo, freqs, nodo, rr, pool):
    jobs = [(tipo, f, p, a) for f in freqs for p in POS for a in AMP]
    mod = dict(zip(jobs, pool.map(corsa, jobs)))
    par = gb.VAR[gb.SCELTA] if tipo == "growl" else nb.VAR[nb.SCELTA]
    print(f"\n{tipo.upper()} A BANDE {par}")
    print("modello | LTspice (THD % . livello dB), colonne -6 / 0 / +10 dBu")
    peggio = [0.0, 0.0, "", ""]
    for f in freqs:
        thd, meas = leggi_log(f"{tipo}-bande-{f}")
        for j, p in enumerate(POS):
            celle = []
            for k, a in enumerate(AMP):
                tm, lm = mod[(tipo, f, p, a)]
                st = 3 * j + k
                tl = thd[(nodo, st)]
                ll = 20 * math.log10(meas[rr][st] / meas["xr"][st])
                if abs(tm - tl) > peggio[0]:
                    peggio[0], peggio[2] = abs(tm - tl), f"{f} Hz {int(p*100)} % {a} V"
                if abs(lm - ll) > peggio[1]:
                    peggio[1], peggio[3] = abs(lm - ll), f"{f} Hz {int(p*100)} % {a} V"
                celle.append(f"{tm:6.2f} {lm:+5.2f}|{tl:6.2f} {ll:+5.2f}")
            print(f"  {f:5d} Hz {int(p * 100):3d} %  " + "   ".join(celle))
    print(f"  scarto massimo: THD {peggio[0]:.2f} punti ({peggio[2]}), "
          f"livello {peggio[1]:.2f} dB ({peggio[3]})")
    return peggio


def op_reale():
    """Op-amp ideale contro OP1654 (GBW 20 MHz, rail +-16,5 V)."""
    print("\nop-amp ideale | OP1654 (THD % . livello dB), colonne -6 / 0 / +10 dBu")
    casi = [("growl", f, "v(y)", "yr") for f in (120, 1000, 12000)]
    # NASTRO con OP1654: LTspice non termina (passo che collassa), vedi RISULTATI-P2 par. 14
    p = [0.0, 0.0]
    for tipo, f, nodo, rr in casi:
        ti, mi = leggi_log(f"{tipo}-bande-{f}")
        to, mo = leggi_log(f"{tipo}-bande-op-{f}")
        for j, pos in enumerate(POS):
            celle = []
            for k in range(3):
                st = 3 * j + k
                a = (ti[(nodo, st)], 20 * math.log10(mi[rr][st] / mi["xr"][st]))
                b = (to[(nodo, st)], 20 * math.log10(mo[rr][st] / mo["xr"][st]))
                p = [max(p[0], abs(a[0] - b[0])), max(p[1], abs(a[1] - b[1]))]
                celle.append(f"{a[0]:6.2f} {a[1]:+5.2f}|{b[0]:6.2f} {b[1]:+5.2f}")
            print(f"  {tipo:6s} {f:5d} Hz {int(pos * 100):3d} %  " + "   ".join(celle))
    print(f"  scarto massimo: THD {p[0]:.2f} punti, livello {p[1]:.2f} dB")


def sei_secondi(pool):
    """NASTRO a 6 s: le condizioni delle tabelle di nastro_bande.py."""
    print("\nNASTRO 6 s: modello | LTspice (THD % . livello dB), colonne -6 / 0 / +10 dBu")
    jobs = [("nastro", f, p, a, 6.0) for f in (500, 3000) for p in POS for a in AMP]
    mod = dict(zip(jobs, pool.map(corsa, jobs)))
    for f in (500, 3000):
        thd, meas = leggi_log(f"nastro-bande-{f}-6s")
        for j, p in enumerate(POS):
            celle = []
            for k, a in enumerate(AMP):
                tm, lm = mod[("nastro", f, p, a, 6.0)]
                st = 3 * j + k
                tl = thd[("v(m)", st)]
                ll = 20 * math.log10(meas["rm"][st] / meas["xr"][st])
                celle.append(f"{tm:6.2f} {lm:+5.2f}|{tl:6.2f} {ll:+5.2f}")
            print(f"  {f:5d} Hz {int(p * 100):3d} %  " + "   ".join(celle))


def main():
    quali = sys.argv[1:] or ["growl", "nastro", "op", "6s"]
    if "op" in quali:
        op_reale()
    with Pool(8) as pool:
        if "growl" in quali:
            confronto("growl", GROWL_F, "v(y)", "yr", pool)
        if "nastro" in quali:
            confronto("nastro", NASTRO_F, "v(m)", "rm", pool)
        if "6s" in quali:
            sei_secondi(pool)


if __name__ == "__main__":
    main()
