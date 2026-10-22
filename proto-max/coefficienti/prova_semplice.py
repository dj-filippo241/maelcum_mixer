"""Confronta le versioni semplici (-S) con gli originali, campione per campione.

Uso:  python3 proto-max/coefficienti/prova_semplice.py
Ogni -S deve suonare come l'originale con i selettori sulle scelte fissate
(SCELTA_* dei generatori): stesse manopole, stesso ingresso, stessa uscita.
Suona i due lati con ingressi diversi, a piu posizioni delle manopole, e
con manopole che si muovono durante la prova (lisciatura compresa).

Non prova la sintassi di gen~: quella la controlla Max all'apertura.
"""

import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
import filtro  # noqa: E402
import genera  # noqa: E402
import genera_5way as g5  # noqa: E402
import genera_filtro as gf  # noqa: E402
import prova_filtro as pf  # noqa: E402
from prova_gen import Gen  # noqa: E402

QUI = os.path.dirname(os.path.abspath(__file__))
CARTELLA = os.path.dirname(QUI)
FS = 48000.0
# scarto massimo accettato: rumore di arrotondamento, ben sotto -200 dBFS
TOLL = 1e-12


def leggi(nome):
    return open(os.path.join(CARTELLA, f"{nome}.genexpr")).read()


def canale_nuovo(testo):
    return Gen(testo, FS)


def manopole_canale(rnd):
    p = {n: rnd.uniform(0, 100) for n, _, _ in genera.MANOPOLE}
    p[genera.FADER[0]] = rnd.uniform(0, 100)
    if rnd.random() < 0.3:
        # contatto di fondo corsa di una banda (silenzio)
        p[rnd.choice(genera.BANDE)] = 0.0
    return p


def manopole_filtro(rnd):
    p = {n: rnd.uniform(0, 100) for n, _, _ in gf.MANOPOLE}
    p[gf.MODO[0]] = rnd.choice((0, 1, 2))
    if gf.con_limitatore():
        p[gf.LIMIT[0]] = rnd.choice(range(len(gf.LIMIT[2])))
    return p


def manopole_5way(rnd):
    p = {n: rnd.choice((0, 1)) for n, _ in g5.KILL}
    for n, _ in g5.GAIN + g5.POS + g5.SAT:
        p[n] = rnd.uniform(0, 100)
    for n, _ in g5.WID:
        p[n] = rnd.uniform(0, 100)  # WIDTH continuo (dec. 117)
    return p


DISPOSITIVI = [
    ("MC-CHANNEL", canale_nuovo, manopole_canale,
     {"incroci": genera.VARIANTI.index(genera.SCELTA_INCROCI),
      "curva": genera.CURVA[2].index("PIONEER"), "eqtipo": 0}),
    ("MC-FILTRO", pf.nuovo, manopole_filtro,
     {"core": int(gf.SCELTA_CORE == "c"), "pend": gf.SCELTA_PEND}),
    ("MC-5WAY", pf.nuovo, manopole_5way,
     {"xo": g5.SCELTA_XO, "gv": g5.SCELTA_GV, "nver": g5.SCELTA_NV}),
]


def ingresso(i, liv):
    """Tre toni diversi per lato: basso, medio, alto."""
    t = i / FS
    l = (math.sin(2 * math.pi * 61 * t) + 0.5 * math.sin(2 * math.pi * 997 * t)
         + 0.25 * math.sin(2 * math.pi * 7001 * t))
    r = (math.sin(2 * math.pi * 113 * t) + 0.5 * math.sin(2 * math.pi * 2003 * t)
         + 0.25 * math.sin(2 * math.pi * 11003 * t))
    return liv * l, liv * r


def confronta(nome, nuovo, manopole, selettori, rnd, n_casi=6, n=2400):
    orig, semp = leggi(nome), leggi(f"{nome}-S")
    peggiore = 0.0
    for caso in range(n_casi):
        p = manopole(rnd)
        # livelli: da -20 a +12 dBu (+12 dBu = 4,4 V picco)
        liv = 1.0954 * 10 ** (rnd.uniform(-20, 12) / 20) / filtro.LIV
        go, gs = nuovo(orig), nuovo(semp)
        go.imposta(**p, **selettori)
        gs.imposta(**p)
        # a meta prova le manopole saltano: lisciatura uguale nei due
        salto = manopole(rnd)
        dmax = 0.0
        for i in range(n):
            if i == n // 2:
                for k, v in salto.items():
                    go.ns[k] = float(v)
                    gs.ns[k] = float(v)
            l, r = ingresso(i, liv)
            ol, orr = go.campione(l, r)
            sl, sr = gs.campione(l, r)
            dmax = max(dmax, abs(ol - sl), abs(orr - sr))
        peggiore = max(peggiore, dmax)
        print(f"  {'ok  ' if dmax <= TOLL else 'FUORI'} {nome} caso {caso + 1}:"
              f" scarto massimo {dmax:.1e}")
    return peggiore


def main():
    rnd = random.Random(7)
    errori = 0
    for nome, nuovo, manopole, selettori in DISPOSITIVI:
        print(f"{nome}-S contro {nome} con {selettori}")
        errori += confronta(nome, nuovo, manopole, selettori, rnd) > TOLL
    print("PASS" if errori == 0 else f"FAIL: {errori} dispositivi fuori")
    return 0 if errori == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
