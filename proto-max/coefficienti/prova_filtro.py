"""Fa suonare MC-FILTRO.genexpr tradotto in Python, campione per campione.

Uso:  python3 proto-max/coefficienti/prova_filtro.py
Verifica il codice gen~ VERO contro il modello di filtro.py (Core a 4x
della frequenza di Live, senza halfband). Il modello e gia stato
confrontato col D5 di LTspice (RISULTATI-P1.md §2).

Non prova la sintassi di gen~: quella la controlla Max all'apertura.
"""

import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
import filtro  # noqa: E402
from prova_gen import Gen, ampiezza, db  # noqa: E402

QUI = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(os.path.dirname(QUI), "MC-FILTRO.genexpr")
FS = 48000.0


def aota(u, lin):
    m = max(abs(u), 0.000001)
    return lin + (1 - lin) * filtro.VS * math.tanh(m / filtro.VS) / m


def spl(z):
    return math.log(1 + math.exp(min(z, 30))) + max(z - 30, 0)


def alim(v):
    m = max(abs(v), 0.000001)
    w, vk = filtro.W_LIM, filtro.VK_LIM
    return filtro.G_LIM * w * (spl((m - vk) / w) - spl(-vk / w)) / m


def sez(st, i, x, g, d, lin, lim):
    s1, s2, bpv = st[i], st[i + 1], st[i + 3]
    g1 = g * aota(st[i + 2], lin)
    g2 = g * aota(bpv, lin)
    rr = d * aota(bpv, lin) + lim * alim(bpv)
    bp = (g1 * (x - s2) + s1) / (1 + g1 * g2 + g1 * rr)
    hp = x - s2 - (g2 + rr) * bp
    lp = g2 * bp + s2
    st[i], st[i + 1], st[i + 2], st[i + 3] = bp + g1 * hp, lp + g2 * bp, hp, bp
    return hp, lp


def nuovo(testo):
    g = Gen(testo, FS)
    rnd = random.Random(1)
    g.ns.update(sez=sez, tanh=math.tanh, log=math.log,
                noise=lambda: rnd.uniform(-1, 1))
    return g


def theta_freq(fc):
    return 100 * (0.05 + 0.9 * math.log(fc / 20) / math.log(1000))


def suona(testo, f, amp, durata=0.12, coda=0.04, **p):
    g = nuovo(testo)
    g.imposta(**p)
    n = int(durata * FS)
    y = []
    for i in range(n):
        x = amp * math.sin(2 * math.pi * f * i / FS)
        y.append(g.campione(x, x)[0])
    return y, n - int(coda * FS)


def modello(f, fc, amp_v, res, modo, lin, durata=0.12, coda=0.04):
    """Core di filtro.py a 4x, senza halfband: ampiezza in volt."""
    fs4 = 4 * FS
    c = filtro.Core(lin)
    gres = filtro.res_law(res / 100)
    return filtro.sinusoide(
        c, f, fc, fs4, amp_v, durata, coda,
        lambda c, x, g: c.passo(x, g, gres, modo))


def nota(y, n0, fs):
    seg = y[n0:]
    rms = math.sqrt(sum(v * v for v in seg) / len(seg))
    zc = [i - 1 + seg[i - 1] / (seg[i - 1] - seg[i])
          for i in range(1, len(seg)) if seg[i - 1] < 0 <= seg[i]]
    f = (len(zc) - 1) * fs / (zc[-1] - zc[0])
    return rms, f


def main():
    testo = open(FILE).read()
    errori = 0

    def controlla(nome, misurato, atteso, toll):
        nonlocal errori
        ok = abs(misurato - atteso) <= toll
        errori += not ok
        print(f"  {'ok  ' if ok else 'FUORI'} {nome}: gen~ {misurato:+.2f}, "
              f"atteso {atteso:+.2f} (toll. {toll})")

    liv = filtro.LIV
    print("OFF: trasparente (1 kHz, 0 dBu)")
    a0 = 1.0954 / liv
    y, n0 = suona(testo, 1000, a0, modo=1)
    controlla("OFF 1 kHz", db(ampiezza(y, 1000, FS, n0) / a0), 0.0, 0.01)

    print("Taglio a piccolo segnale (-30 dBu, RES 0): -3 dB sul taglio")
    for modo, nm in ((2, "lp"), (0, "hp")):
        for fc in (100, 1000, 10000):
            a = 1.0954 * 10 ** (-30 / 20) / liv
            p = {f"freq_{nm}": theta_freq(fc), "modo": modo}
            y, n0 = suona(testo, fc, a, durata=0.25 if fc < 300 else 0.12,
                          **p)
            controlla(f"{nm.upper()} fc {fc} Hz", db(ampiezza(y, fc, FS, n0)
                                                     / a), -3.01, 0.15)

    print("Risonanza sul taglio, gen~ contro modello (dB uscita/ingresso)")
    for lin, nome_c in ((0, "OTA (a')"), (1, "PULITO (c-B)")):
        for modo, nm in ((2, "lp"), (0, "hp")):
            for res in (0, 50, 70, 85):
                for dbu in (-30, -10, 0):
                    if nm == "hp" and dbu == -30:
                        continue
                    av = 1.0954 * 10 ** (dbu / 20)
                    p = {f"freq_{nm}": theta_freq(1000), f"res_{nm}": res,
                         "modo": modo, "core": lin}
                    y, n0 = suona(testo, 1000, av / liv, **p)
                    gen_db = db(ampiezza(y, 1000, FS, n0) * liv / av)
                    mod_db = db(modello(1000, 1000, av, res, nm, lin) / av)
                    controlla(f"{nome_c} {nm.upper()} RES {res} % {dbu} dBu",
                              gen_db, mod_db, 0.3)

    print("Fischio (RES 100 %, senza ingresso): gen~ contro modello")
    for lin, nome_c in ((0, "OTA (a')"), (1, "PULITO (c-B)")):
        for fc in (200, 1000, 5000):
            g = nuovo(testo)
            g.imposta(freq_lp=theta_freq(fc), res_lp=100, modo=2, core=lin)
            n = int(0.35 * FS)
            y = [g.campione(0.0, 0.0)[0] for _ in range(n)]
            rms, f = nota(y, n - int(0.08 * FS), FS)
            c = filtro.Core(lin)
            gm = math.tan(math.pi * fc / (4 * FS))
            ym = [c.passo(1e-6 if i < 10 else 0.0, gm, -0.75, "lp")
                  for i in range(int(0.35 * 4 * FS))]
            rms_m, f_m = nota(ym, len(ym) - int(0.08 * 4 * FS), 4 * FS)
            controlla(f"{nome_c} fc {fc} Hz livello dBu",
                      20 * math.log10(rms * liv / 0.775),
                      20 * math.log10(rms_m / 0.775), 0.5)
            controlla(f"{nome_c} fc {fc} Hz nota (semitoni dal taglio)",
                      12 * math.log2(f / fc), 12 * math.log2(f_m / fc), 0.3)

    print("PASS" if errori == 0 else f"FAIL: {errori} punti fuori")
    return 0 if errori == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
