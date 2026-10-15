"""Fa suonare MC-SEND, MC-RET e MC-MASTER (.genexpr) tradotti in Python.

Uso:  python3 proto-max/coefficienti/prova_fx.py
Verifica il codice gen~ VERO contro il modello di fx.py (EQ2 a 4x della
frequenza di Live, senza halfband), sui due canali. Il modello e gia
stato confrontato con LTspice e con la SPEC (verifica_fx.py).

Non prova la sintassi di gen~: quella la controlla Max all'apertura.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import fx  # noqa: E402
import prova_filtro as pf  # noqa: E402
from prova_gen import ampiezza, db  # noqa: E402

QUI = os.path.dirname(os.path.abspath(__file__))
CART = os.path.dirname(QUI)
FS = 48000.0
A0 = fx.V_DBU / fx.LIV          # 0 dBu in unita digitali


def nuovo(nome, **p):
    g = pf.nuovo(open(os.path.join(CART, f"{nome}.genexpr")).read())
    g.ns["min"] = min
    g.imposta(**p)
    return g


def suona(g, f, amp, durata, destra=1.0, uscite=(1, 2)):
    n = int(durata * FS)
    ys = {u: [] for u in uscite}
    for i in range(n):
        x = amp * math.sin(2 * math.pi * f * i / FS)
        g.campione(x, destra * x)
        for u in uscite:
            ys[u].append(g.ns[f"out{u}"])
    return ys, n - int(min(0.04, durata / 3) * FS)


def eq_modello(f, low, high):
    fs4 = 4 * FS
    e = fx.Eq2(fs4)
    x, thh = fx.low_x(low / 100), fx.high_thh(high / 100)
    n = int(max(0.12, 12 / f) * fs4)
    ys = [e.passo(math.sin(2 * math.pi * f * i / fs4), x, thh)
          for i in range(n)]
    return db(ampiezza(ys, f, fs4, n - int(min(0.04, n / fs4 / 3) * fs4)))


def main():
    errori = 0

    def controlla(nome, misurato, atteso, toll):
        nonlocal errori
        ok = abs(misurato - atteso) <= toll
        errori += not ok
        print(f"  {'ok  ' if ok else 'FUORI'} {nome}: gen~ {misurato:+.3f}, "
              f"atteso {atteso:+.3f} (toll. {toll})")

    print("MC-SEND: passaggio intatto del canale")
    g = nuovo("MC-SEND", level=100, as1=1)
    ys, n0 = suona(g, 1000, A0, 0.02, destra=0.5, uscite=(1, 2))
    err = max(abs(ys[1][i] - A0 * math.sin(2 * math.pi * 1000 * i / FS))
              for i in range(len(ys[1])))
    controlla("out1 = in1, errore x 1e9", err * 1e9, 0.0, 1e-3)

    print("MC-SEND: EQ2 e LEVEL sul bus 1 (L e R), poi ogni ASSIGN")
    casi = [(50, 50, 100, 1000), (0, 50, 100, 30), (20, 50, 100, 60),
            (10, 50, 100, 120), (100, 50, 100, 40), (50, 0, 100, 10000),
            (50, 30, 100, 8000), (50, 15, 100, 15000), (50, 100, 100, 15000),
            (50, 50, 50, 1000), (50, 50, 75, 1000), (50, 50, 25, 1000)]
    for low, high, level, f in casi:
        g = nuovo("MC-SEND", low=low, high=high, level=level, as1=1)
        ys, n0 = suona(g, f, A0 * 0.1, max(0.12, 12 / f), uscite=(3, 4))
        att = eq_modello(f, low, high) + db(fx.level_send(level / 100))
        for u, lato in ((3, "L"), (4, "R")):
            controlla(f"LOW {low} HIGH {high} LEVEL {level} {f} Hz {lato}",
                      db(ampiezza(ys[u], f, FS, n0) / (A0 * 0.1)), att, 0.05)
    for n in range(4):
        p = {f"as{j + 1}": int(j == n) for j in range(4)}
        g = nuovo("MC-SEND", level=100, **p)
        ys, n0 = suona(g, 1000, A0, 0.1, uscite=range(3, 11))
        for j in range(4):
            a = ampiezza(ys[3 + 2 * j], 1000, FS, n0) / A0
            controlla(f"ASSIGN FX{n + 1}: bus {j + 1} (1 = acceso)", a,
                      float(j == n), 0.005)

    print("MC-RET: GAIN, EQ2 e REROUTE")
    for gain in (100, 75, 50, 25, 10, 3):
        g = nuovo("MC-RET", gain=gain, rr1=100)
        ys, n0 = suona(g, 1000, A0 * 0.05, 0.1, uscite=(1, 2, 3))
        att = db(fx.gain_lin(gain / 100)) + eq_modello(1000, 50, 50)
        for u, nome in ((1, "uscita L"), (2, "uscita R"), (3, "> FX1 L")):
            controlla(f"GAIN {gain} % {nome}",
                      db(ampiezza(ys[u], 1000, FS, n0) / (A0 * 0.05)), att,
                      0.05)
    for low, high, f in ((0, 50, 30), (100, 50, 40), (50, 0, 10000),
                         (50, 100, 15000)):
        g = nuovo("MC-RET", low=low, high=high)
        ys, n0 = suona(g, f, A0 * 0.1, max(0.12, 12 / f))
        att = eq_modello(f, low, high)
        for u, lato in ((1, "L"), (2, "R")):
            controlla(f"EQ LOW {low} HIGH {high} {f} Hz {lato}",
                      db(ampiezza(ys[u], f, FS, n0) / (A0 * 0.1)), att, 0.05)
    for t in (100, 97.5, 90, 70, 45, 20):
        for n in range(4):
            g = nuovo("MC-RET", **{f"rr{n + 1}": t})
            ys, n0 = suona(g, 1000, A0, 0.08, uscite=(3 + 2 * n, 4 + 2 * n))
            for u, lato in ((3 + 2 * n, "L"), (4 + 2 * n, "R")):
                controlla(f"REROUTE > FX{n + 1} {t} % {lato}",
                          db(ampiezza(ys[u], 1000, FS, n0) / A0)
                          - eq_modello(1000, 50, 50),
                          fx.reroute_db(t / 100), 0.05)

    print("MC-RET: rail, meter e clip")
    g = nuovo("MC-RET", gain=100)
    ys, n0 = suona(g, 100, A0 * 2, 0.1, uscite=(1, 2))
    picco = max(abs(v) for v in ys[1][n0:]) * fx.LIV
    controlla("picco col rail (+26 dBu chiesti), volt", picco, fx.RAIL, 0.5)
    for dbu, clip in ((0, 0), (20, 0), (24, 1)):
        g = nuovo("MC-RET")
        ys, n0 = suona(g, 1000, A0 * 10 ** (dbu / 20), 0.15,
                       uscite=(11, 12))
        livello = max(ys[11][n0:])
        atteso = min(fx.V_DBU * 10 ** (dbu / 20), fx.RAIL) / fx.METER_FS
        controlla(f"meter a {dbu:+d} dBu (1 = +24 dBu)", livello, atteso,
                  0.01 * atteso)
        controlla(f"clip a {dbu:+d} dBu", float(max(ys[12][n0:])), clip, 0)

    print("MC-MASTER: MASTER LEVEL e MONO")
    for t in (100, 90, 80, 50, 20, 3):
        g = nuovo("MC-MASTER", level=t)
        ys, n0 = suona(g, 1000, A0, 0.05)
        for u, lato in ((1, "L"), (2, "R")):
            controlla(f"MASTER {t} % {lato}",
                      db(ampiezza(ys[u], 1000, FS, n0) / A0),
                      db(fx.master_lin(t / 100)), 0.01)
    for mono, attl, attr in ((0, 1.0, 0.0), (1, 0.5, 0.5)):
        g = nuovo("MC-MASTER", mono=mono)
        ys, n0 = suona(g, 1000, A0, 0.05, destra=0.0)
        controlla(f"MONO {mono}: solo L in ingresso, uscita L",
                  ampiezza(ys[1], 1000, FS, n0) / A0, attl, 1e-4)
        controlla(f"MONO {mono}: solo L in ingresso, uscita R",
                  ampiezza(ys[2], 1000, FS, n0) / A0, attr, 1e-4)
    g = nuovo("MC-MASTER", mono=1)
    ys, n0 = suona(g, 1000, A0, 0.05, destra=1.0)
    controlla("MONO 1: L = R, uscita invariata",
              ampiezza(ys[1], 1000, FS, n0) / A0, 1.0, 1e-4)

    print("PASS" if errori == 0 else f"FAIL: {errori} punti fuori")
    return 0 if errori == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
