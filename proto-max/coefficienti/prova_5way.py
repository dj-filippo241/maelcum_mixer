"""Fa suonare MC-5WAY.genexpr tradotto in Python, campione per campione.

Uso:  python3 proto-max/coefficienti/prova_5way.py
Verifica il codice gen~ VERO contro il modello di fiveway.py (Completo a
4x della frequenza di Live, senza halfband). Il modello e gia stato
confrontato con le formule analogiche (fiveway.py) e con la griglia
LTspice dei saturatori (taratura_sat.py).

Suona sempre i due canali: la prova del P1 suonava solo out1 e non ha
visto il canale R rotto (RISULTATI-P1 §7).

Non prova la sintassi di gen~: quella la controlla Max all'apertura.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import fiveway as fw  # noqa: E402
import prova_filtro as pf  # noqa: E402
from prova_gen import ampiezza, db  # noqa: E402

QUI = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(os.path.dirname(QUI), "MC-5WAY.genexpr")
FS = 48000.0
A0 = 1.0954 / fw.LIV            # 0 dBu in unita digitali
VIE = [v.lower() for v in fw.VIE]


def gen_param(kill=(1,) * 5, gain=(50,) * 5, pos=(50,) * 5, width=(1,) * 5,
              growl=0, nastro=0, xo=0):
    p = {f"k_{v}": 1 - k for v, k in zip(VIE, kill)}
    for i in range(5):
        p[f"g_{i + 1}"] = gain[i]
        p[f"p_{i + 1}"] = pos[i]
        p[f"w_{i + 1}"] = width[i]
    p.update(growl=growl, nastro=nastro, xo=xo)
    return p


def suona_gen(testo, f, amp, durata, coda, destra=1.0, **kw):
    g = pf.nuovo(testo)
    g.imposta(**gen_param(**kw))
    n = int(durata * FS)
    sl, sr = [], []
    for i in range(n):
        x = amp * math.sin(2 * math.pi * f * i / FS)
        a, b = g.campione(x, destra * x)
        sl.append(a)
        sr.append(b)
    return sl, sr, n - int(coda * FS)


def suona_mod(f, amp, durata, coda, kill=(1,) * 5, gain=(50,) * 5,
              pos=(50,) * 5, width=(1,) * 5, growl=0, nastro=0, xo=0):
    fs4 = 4 * FS
    m = fw.Completo(fs4, list(fw.VARIANTI_XO.values())[xo])
    n = int(durata * fs4)
    y = []
    for i in range(n):
        x = amp * math.sin(2 * math.pi * f * i / fs4)
        y.append(m.passo(x, kill, [t / 100 for t in gain],
                         [t / 100 for t in pos], width,
                         growl / 100, nastro / 100))
    return y, n - int(coda * fs4)


def main():
    testo = open(FILE).read()
    errori = 0

    def controlla(nome, misurato, atteso, toll):
        nonlocal errori
        ok = abs(misurato - atteso) <= toll
        errori += not ok
        print(f"  {'ok  ' if ok else 'FUORI'} {nome}: gen~ {misurato:+.2f}, "
              f"atteso {atteso:+.2f} (toll. {toll})")

    def caso(nome, f, toll=0.05, amp=A0 * 0.1, durata=None, coda=None,
             **kw):
        durata = durata or max(0.12, 12 / f)
        coda = coda or min(0.04, durata / 3)
        sl, sr, n0 = suona_gen(testo, f, amp, durata, coda, **kw)
        ym, m0 = suona_mod(f, amp, durata, coda, **kw)
        # sotto -120 dB e silenzio: il notch esatto da residui numerici
        # diversi (-230...-320 dB) che non vanno confrontati
        gl = max(db(ampiezza(sl, f, FS, n0) / amp), -120.0)
        gr = max(db(ampiezza(sr, f, FS, n0) / amp), -120.0)
        gm = max(db(ampiezza(ym, f, 4 * FS, m0) / amp), -120.0)
        controlla(f"{nome} L", gl, gm, toll)
        controlla(f"{nome} R", gr, gm, toll)
        return sl, sr, n0

    print("Tutto al centro: trasparente (somma della banca piatta)")
    for f in (30, 200, 1000, 8000):
        caso(f"{f} Hz", f)

    print("KILL di una via alla volta, variante A")
    for v in range(5):
        kill = tuple(0 if j == v else 1 for j in range(5))
        for f in (60, 200, 700, 2000, 6000):
            caso(f"KILL {fw.VIE[v]} {f} Hz", f, kill=kill)

    print("CROSSOVER B, C, D: KILL KICK e KILL SUPER")
    for xo in (1, 2, 3):
        for v in (1, 4):
            kill = tuple(0 if j == v else 1 for j in range(5))
            for f in (120, 5000):
                caso(f"variante {xo} KILL {fw.VIE[v]} {f} Hz", f, kill=kill,
                     xo=xo)

    print("EQ: GAIN, POSITION, WIDTH (sul centro della campana)")
    for i in range(5):
        for th, w in ((100, 0), (100, 2), (75, 1), (25, 1), (0, 1), (3, 1)):
            pos = [50] * 5
            pos[i] = 30
            f0 = fw.posizione(0.3, i)
            gain = [50] * 5
            gain[i] = th
            width = [1] * 5
            width[i] = w
            caso(f"EQ{i + 1} GAIN {th} % WIDTH Q{fw.Q_WIDTH[w]}"
                 f" a {f0:.0f} Hz", f0, toll=0.1 if th < 5 else 0.05,
                 gain=gain, pos=pos, width=width)

    print("GROWL e NASTRO (50 Hz, 0 dBu e +10 dBu)")
    for growl, nastro in ((100, 0), (0, 100), (50, 50)):
        for dbu in (0, 10):
            caso(f"GROWL {growl} NASTRO {nastro} {dbu:+d} dBu", 50, toll=0.05,
                 amp=A0 * 10 ** (dbu / 20), durata=0.3, coda=0.1,
                 growl=growl, nastro=nastro)

    print("Canali indipendenti: R muto, L intero")
    sl, sr, n0 = suona_gen(testo, 1000, A0, 0.1, 0.03, destra=0.0,
                           growl=50, nastro=50)
    controlla("R con ingresso zero, picco x 1e6",
              max(abs(t) for t in sr) * 1e6, 0.0, 1.0)

    print("PASS" if errori == 0 else f"FAIL: {errori} punti fuori")
    return 0 if errori == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
