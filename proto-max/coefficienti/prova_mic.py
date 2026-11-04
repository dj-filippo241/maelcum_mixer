"""Fa suonare MC-MIC (.genexpr) tradotto in Python.

Uso:  python3 proto-max/coefficienti/prova_mic.py
Verifica il codice gen~ VERO contro il modello di mic.py (a 4x della
frequenza di Live, senza halfband), su tutte e due le uscite. Il modello
e gia stato confrontato con LTspice (verifica_mic.py).

Non prova la sintassi di gen~: quella la controlla Max all'apertura.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import fx  # noqa: E402
import mic  # noqa: E402
from prova_fx import FS, nuovo  # noqa: E402
from prova_gen import ampiezza, db  # noqa: E402

V1 = 1e-3                       # 1 mV di picco al microfono


def suona(g, f, v_mic, durata, destra=1.0, uscite=(1, 2)):
    """v_mic: volt di picco al microfono. Restituisce le uscite in volt."""
    a = v_mic / mic.V_SCHEDA
    n = int(durata * FS)
    ys = {u: [] for u in uscite}
    for i in range(n):
        x = a * math.sin(2 * math.pi * f * i / FS)
        g.campione(x, destra * x)
        for u in uscite:
            ys[u].append(g.ns[f"out{u}"] * (fx.LIV if u < 11 else 1))
    return ys, n - int(min(0.04, durata / 3) * FS)


def modello(f, v_mic, gain, low=50, high=50, mute=0):
    fs4 = 4 * FS
    m = mic.Mic(fs4)
    n = int(max(0.15, 15 / f) * fs4)
    lim = mic.Limiter(fs4)    # dec. 145: stesso anello, a 4x
    ys = []
    for i in range(n):
        y = lim.guadagno() * m.passo(v_mic * math.sin(2 * math.pi * f * i
                                                      / fs4), gain / 100,
                                     low / 100, high / 100, mute)[1]
        lim.dopo(y)
        ys.append(y)
    return ampiezza(ys, f, fs4, n - int(min(0.04, n / fs4 / 3) * fs4))


def main():
    errori = 0

    def controlla(nome, misurato, atteso, toll):
        nonlocal errori
        ok = abs(misurato - atteso) <= toll
        errori += not ok
        print(f"  {'ok  ' if ok else 'FUORI'} {nome}: gen~ {misurato:+.3f}, "
              f"atteso {atteso:+.3f} (toll. {toll})")

    print("GAIN, passa-alto ed EQ2 (uscite 1 e 2, in volt)")
    casi = [(0, 50, 50, 1000), (50, 50, 50, 1000), (100, 50, 50, 1000),
            (25, 50, 50, 1000), (75, 50, 50, 1000), (0, 50, 50, 40),
            (0, 50, 50, 60), (0, 50, 50, 100), (50, 0, 50, 120),
            (50, 100, 50, 120), (50, 50, 0, 10000), (50, 50, 100, 10000)]
    for gain, low, high, f in casi:
        g = nuovo("MC-MIC", gain=gain, low=low, high=high)
        ys, n0 = suona(g, f, V1, max(0.15, 15 / f))
        att = db(modello(f, V1, gain, low, high) / V1)
        for u, lato in ((1, "L"), (2, "R")):
            controlla(f"GAIN {gain} LOW {low} HIGH {high} {f} Hz {lato}",
                      db(ampiezza(ys[u], f, FS, n0) / V1), att, 0.05)

    print("Ingresso destro ignorato (mic mono su in1)")
    g = nuovo("MC-MIC", gain=50)
    ys, n0 = suona(g, 1000, V1, 0.1, destra=0.0)
    g2_ = nuovo("MC-MIC", gain=50)
    ys2, _ = suona(g2_, 1000, V1, 0.1, destra=-3.0)
    err = max(abs(a - b) for a, b in zip(ys[1], ys2[1]))
    controlla("differenza con in2 cambiato, volt x 1e9", err * 1e9, 0.0, 1e-3)

    # Il picco dell'onda tosata non si confronta: il halfband del ritorno
    # a 48 kHz aggiunge Gibbs (15,6 V di picco su un taglio a 13,5 V).
    # Si confronta la fondamentale, che il taglio fissa.
    print("Rail del front-end: GAIN 100 %, 100 mV al microfono (tosato)")
    g = nuovo("MC-MIC", gain=100)
    ys, n0 = suona(g, 1000, 0.1, 0.1)
    for u, lato in ((1, "L"), (2, "R")):
        controlla(f"fondamentale tosata {lato}, dB su 1 V",
                  db(ampiezza(ys[u], 1000, FS, n0)),
                  db(modello(1000, 0.1, 100)), 1.2)
    # toll. 1,2 dB dal limiter (todo 208): il rilevatore del gen~ legge i
    # picchi di Gibbs del halfband (15,6 V su 13,5) e limita ~1 dB in piu;
    # nell'hardware il picco e quello vero. Solo col front-end tosato.

    print("MUTE")
    for mute in (0, 1):
        g = nuovo("MC-MIC", gain=50, mute=mute)
        ys, n0 = suona(g, 1000, V1, 0.1)
        att = modello(1000, V1, 50, mute=mute) / V1
        for u, lato in ((1, "L"), (2, "R")):
            controlla(f"MUTE {mute} {lato}, guadagno lineare",
                      ampiezza(ys[u], 1000, FS, n0) / V1, att, 1e-3 * att
                      + 1e-9)

    print("SEND: ogni manopola accende solo il suo bus (L e R)")
    for n in range(4):
        for t in (100, 50):
            g = nuovo("MC-MIC", gain=50, **{f"snd{n + 1}": t})
            ys, n0 = suona(g, 1000, V1, 0.1, uscite=range(1, 11))
            uscita = ampiezza(ys[1], 1000, FS, n0)
            for j in range(4):
                for k, lato in ((0, "L"), (1, "R")):
                    a = ampiezza(ys[3 + 2 * j + k], 1000, FS, n0) / uscita
                    att = mic.send_lin(t / 100) if j == n else 0.0
                    controlla(f"FX{n + 1} {t} %: bus {j + 1} {lato}", a, att,
                              1e-3)
    g = nuovo("MC-MIC", gain=50, snd1=100, mute=1)
    ys, n0 = suona(g, 1000, V1, 0.1, uscite=(3,))
    controlla("MUTE spegne anche le mandate, bus 1", ampiezza(
        ys[3], 1000, FS, n0) / V1, 0.0, 1e-6)

    print("LED al nodo PRE (0 spento, 1 verde, 2 giallo, 3 rosso)")
    g_pre = 10 ** (mic.gain_db(0) / 20)
    for dbu, stato in ((-10, 0), (0, 1), (14, 2), (18, 3)):
        for mute in (0, 1):
            g = nuovo("MC-MIC", gain=0, mute=mute)
            v = fx.V_DBU * 10 ** (dbu / 20) / g_pre
            ys, n0 = suona(g, 1000, v, 0.2, uscite=(11,))
            controlla(f"PRE {dbu:+d} dBu, MUTE {mute}", ys[11][-1], stato, 0)
    print("LED: latch del rosso dopo un colpo a +18 dBu")
    g = nuovo("MC-MIC", gain=0)
    v = fx.V_DBU * 10 ** (18 / 20) / g_pre
    suona(g, 1000, v, 0.05, uscite=(11,))
    ys, _ = suona(g, 1000, 0.0, 0.7, uscite=(11,))
    controlla("rosso dopo 0,4 s di silenzio", ys[11][int(0.4 * FS)], 3, 0)
    controlla("non piu rosso dopo 0,6 s", float(ys[11][int(0.6 * FS)] < 3),
              1, 0)

    print("Limiter fisso (dec. 145): grido da 0 a +20 dBu per 0,3 s, 1 kHz")
    g_pre = 10 ** (mic.gain_db(0) / 20)

    def grido(passo):
        """passo(x volt all'uscita senza limiter) -> uscita in volt."""
        n0, n1, n2 = int(0.1 * FS), int(0.4 * FS), int(0.8 * FS)
        ys = []
        for i in range(n2):
            a = fx.V_DBU * (10 if n0 <= i < n1 else 1)
            ys.append(passo(a * math.sin(2 * math.pi * 1000 * i / FS)))
        ciclo = int(FS / 1000)

        def gdb(t, a):
            k = int(t * FS)
            return db(max(abs(v) for v in ys[k:k + ciclo]) / a)
        reg = db(max(abs(v) for v in ys[n1 - 4 * ciclo:n1]) / fx.V_DBU)
        k2, k5 = int(0.102 * FS), int(0.105 * FS)
        mx = db(max(abs(v) for v in ys[k2:k5]) / fx.V_DBU)
        return (reg, mx,
                gdb(0.4 + 0.05, fx.V_DBU), gdb(0.4 + 0.3, fx.V_DBU))

    lim = mic.Limiter(FS)

    def passo_mod(x):
        y = lim.guadagno() * x
        lim.dopo(y)
        return y
    mod = grido(passo_mod)
    nomi = ("a regime, dBu", "massimo da 2 a 5 ms, dBu",
            "50 ms dopo, guadagno dB", "300 ms dopo, guadagno dB")
    # LTspice (RISULTATI-mic-limiter): +12,8 dBu; <= +13,5 da 2 a 5 ms;
    # -4,4 dB a 50 ms; 0 dB a 300 ms
    for nome, m, att, toll in zip(nomi, mod, (12.8, None, -4.4, 0.0),
                                  (0.3, None, 0.6, 0.3)):
        if att is None:  # LTspice da solo un tetto: <= +13,5 dBu
            controlla(f"modello contro LTspice: {nome} sotto +13,5",
                      float(m <= 13.5), 1.0, 0)
            continue
        controlla(f"modello contro LTspice: {nome}", m, att, toll)
    g = nuovo("MC-MIC", gain=0)
    a_mic = 1 / g_pre / mic.V_SCHEDA
    gen = grido(lambda x: (g.campione(x * a_mic, 0.0),
                           g.ns["out1"] * fx.LIV)[1])
    # il halfband del gen~ sposta di qualche campione la finestra dei
    # primi ms: li' vale il tetto di LTspice, non lo scarto dal modello
    for i, (nome, m, att) in enumerate(zip(nomi, gen, mod)):
        if i == 1:
            controlla(f"gen~: {nome} sotto +13,5", float(m <= 13.5), 1.0, 0)
            continue
        controlla(f"gen~ contro modello: {nome}", m, att, 0.1)

    print("PASS" if errori == 0 else f"FAIL: {errori} punti fuori")
    return 0 if errori == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
