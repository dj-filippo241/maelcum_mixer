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
      "curva": genera.CURVA[2].index("LINEARE"), "eqtipo": 0}),
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


def freschi():
    """Todo 207: ogni .genexpr su disco = quello che il generatore scrive oggi.

    Una legge cambiata nel generatore e rigenerata in una sola versione
    lascia l'altra vecchia: il confronto campione per campione la vede solo
    se un caso tocca quel tratto di corsa. Qui la si vede sempre.
    """
    varianti = [(genera, {}), (genera, {"SEMPLICE": True}),
                (gf, {}), (gf, {"SEMPLICE": True}),
                (gf, {"SEMPLICE": True, "BUS": "hp"}),
                (gf, {"SEMPLICE": True, "BUS": "lp"}),
                (g5, {}), (g5, {"SEMPLICE": True})]
    vecchi = 0
    for mod, imp in varianti:
        prima = {k: getattr(mod, k) for k in ("SEMPLICE", "BUS", "NOME")
                 if hasattr(mod, k)}
        nome = prima["NOME"]
        if imp.get("BUS"):
            nome += "-" + imp["BUS"].upper() + "F"
        elif imp.get("SEMPLICE"):
            nome += "-S"
        try:
            for k, v in imp.items():
                setattr(mod, k, v)
            mod.NOME = nome
            atteso = mod.genexpr()
        finally:
            for k, v in prima.items():
                setattr(mod, k, v)
        su_disco = leggi(nome)
        ok = su_disco == atteso
        vecchi += not ok
        print(f"  {'ok  ' if ok else 'VECCHIO'} {nome}.genexpr"
              + ("" if ok else ": rilancia il generatore per questa versione"))
    return vecchi


def main():
    rnd = random.Random(7)
    print("File su disco contro i generatori di oggi")
    errori = freschi()
    for nome, nuovo, manopole, selettori in DISPOSITIVI:
        print(f"{nome}-S contro {nome} con {selettori}")
        errori += confronta(nome, nuovo, manopole, selettori, rnd) > TOLL
    # bus dopo il fader (dec. 159): MC-FILTRO-HPF/-LPF contro -S con MODO
    for sez, modo in (("HPF", 0), ("LPF", 2)):
        semp, bus = leggi("MC-FILTRO-S"), leggi(f"MC-FILTRO-{sez}")
        peggiore = 0.0
        for caso in range(6):
            p = manopole_filtro(rnd)
            p[gf.MODO[0]] = modo
            liv = 1.0954 * 10 ** (rnd.uniform(-20, 12) / 20) / filtro.LIV
            gs, gb = pf.nuovo(semp), pf.nuovo(bus)
            gs.imposta(**p)
            gb.imposta(**{k: v for k, v in p.items()
                          if k.endswith("_" + sez[:2].lower())})
            dmax = 0.0
            for i in range(2400):
                l, r = ingresso(i, liv)
                a, b = gs.campione(l, r), gb.campione(l, r)
                dmax = max(dmax, abs(a[0] - b[0]), abs(a[1] - b[1]))
            peggiore = max(peggiore, dmax)
            print(f"  {'ok  ' if dmax <= TOLL else 'FUORI'} MC-FILTRO-{sez}"
                  f" caso {caso + 1}: scarto massimo {dmax:.1e}")
        errori += peggiore > TOLL
    print("PASS" if errori == 0 else f"FAIL: {errori} dispositivi fuori")
    return 0 if errori == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
