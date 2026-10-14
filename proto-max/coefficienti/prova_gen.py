"""Fa suonare MC-CHANNEL.genexpr tradotto in Python, campione per campione.

Uso:  python3 proto-max/coefficienti/prova_gen.py
Verifica il codice gen~ VERO (non le formule): sinusoidi in ingresso,
ampiezza in uscita, confronto con la risposta del modello (canale.py), che
verifica.py ha gia confrontato con LTspice. Prova anche law di GAIN e
fader, il selettore A/B e la separazione dei due lati.

Non prova la sintassi di gen~: quella la controlla Max all'apertura.
"""

import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import canale  # noqa: E402

QUI = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(os.path.dirname(QUI), "MC-CHANNEL.genexpr")
FS = 48000.0


def bq(st, i, x, b0, b1, b2, a1, a2):
    y = b0 * x + st[i]
    st[i] = b1 * x - a1 * y + st[i + 1]
    st[i + 1] = b2 * x - a2 * y
    return y


def ap(hb, i, x, c):
    y = c * (x - hb[i + 1]) + hb[i]
    hb[i] = x
    hb[i + 1] = y
    return y


class Gen:
    """Traduzione riga per riga del sottoinsieme di GenExpr che usa genera.py."""

    def __init__(self, testo, fs):
        self.ns = {"bq": bq, "ap": ap, "tan": math.tan, "exp": math.exp,
                   "pow": math.pow, "pi": math.pi, "samplerate": fs}
        corpo, in_funzione = [], False
        for riga in testo.splitlines():
            riga = riga.split("//")[0].strip()
            if not riga:
                continue
            if re.match(r"^\w+\(.*\)\s*\{$", riga):
                in_funzione = True
                continue
            if in_funzione:
                in_funzione = riga != "}"
                continue
            m = re.match(r"^(Param|History) (\w+)\(([-\d.]+)", riga)
            if m:
                self.ns[m.group(2)] = float(m.group(3))
                continue
            m = re.match(r"^Data (\w+)\((\d+)\);$", riga)
            if m:
                self.ns[m.group(1)] = [0.0] * int(m.group(2))
                continue
            if not riga.endswith(";"):
                raise ValueError(f"riga non tradotta: {riga}")
            corpo.append(riga[:-1])
        self.codice = compile("\n".join(corpo), FILE, "exec")

    def imposta(self, **p):
        """Param e stato lisciato gia al valore: niente rampa iniziale."""
        for k, v in p.items():
            self.ns[k] = float(v)
            if k == "incroci":
                self.ns["s_x"] = float(v)
            else:
                self.ns[f"s_{k}"] = float(v)

    def campione(self, l, r):
        self.ns["in1"], self.ns["in2"] = l, r
        exec(self.codice, self.ns)
        return self.ns["out1"], self.ns["out2"]


def ampiezza(y, f, fs, n0):
    """Fit ai minimi quadrati di a*sin + b*cos sugli ultimi campioni."""
    ss = sc = cc = ys = yc = 0.0
    for n in range(n0, len(y)):
        s, c = math.sin(2 * math.pi * f * n / fs), math.cos(2 * math.pi * f * n / fs)
        ss, sc, cc = ss + s * s, sc + s * c, cc + c * c
        ys, yc = ys + y[n] * s, yc + y[n] * c
    det = ss * cc - sc * sc
    a, b = (ys * cc - yc * sc) / det, (yc * ss - ys * sc) / det
    return math.hypot(a, b)


def suona(testo, f, durata=0.12, coda=0.04, destra=0.0, **p):
    g = Gen(testo, FS)
    g.imposta(**p)
    n = int(durata * FS)
    sl, sr = [], []
    for i in range(n):
        x = math.sin(2 * math.pi * f * i / FS)
        a, b = g.campione(x, destra * x)
        sl.append(a)
        sr.append(b)
    n0 = n - int(coda * FS)
    return ampiezza(sl, f, FS, n0), ampiezza(sr, f, FS, n0)


def db(x):
    return -999.0 if x <= 0 else 20 * math.log10(x)


def main():
    testo = open(FILE).read()
    errori = 0

    def controlla(nome, misurato, atteso, toll=0.05):
        nonlocal errori
        ok = abs(misurato - atteso) <= toll or (atteso < -60 and misurato < -60)
        errori += not ok
        print(f"  {'ok  ' if ok else 'FUORI'} {nome}: gen~ {misurato:+.3f} dB, "
              f"atteso {atteso:+.3f} dB")

    print("Isolator (fs 48 kHz, gen~ contro modello canale.isolator_os)")
    casi = [
        ("tutte al centro", (50, 50, 50, 50), 0, [80, 500, 2500, 8000]),
        ("LOW a zero", (0, 50, 50, 50), 0, [80, 150, 274]),
        ("LOW-MID a zero", (50, 0, 50, 50), 0, [274, 500]),
        ("MID-HIGH a zero", (50, 50, 0, 50), 0, [1118, 2500]),
        ("HIGH a zero", (50, 50, 50, 0), 0, [2500, 5000, 8000]),
        ("tutte al massimo", (100, 100, 100, 100), 0, [150, 5000]),
        ("tutte a zero", (0, 0, 0, 0), 0, [500]),
        ("B: HIGH a zero", (50, 50, 50, 0), 1, [5000, 8000]),
        ("B: LOW-MID a zero", (50, 0, 50, 50), 1, [250]),
    ]
    for nome, man, sel, freq in casi:
        inc = canale.INCROCI["AB"[sel]]
        for f in freq:
            p = dict(zip(["low", "lowmid", "midhigh", "high"], man))
            a, _ = suona(testo, f, incroci=sel, **p)
            atteso = canale.db(canale.isolator_os(
                f, FS, inc, [m / 100 for m in man]))
            controlla(f"{nome}, {f} Hz", db(a), atteso)

    print("GAIN (1 kHz)")
    for pos, atteso in [(0, -999.0), (25, -50.0), (50, 0.0), (75, 5.0), (100, 10.0)]:
        a, _ = suona(testo, 1000, durata=0.03, coda=0.01, gain=pos)
        controlla(f"GAIN {pos} %", db(a), atteso)

    print("FADER (1 kHz)")
    for pos, atteso in [(0, -999.0), (50, -12.04), (100, 0.0)]:
        a, _ = suona(testo, 1000, durata=0.03, coda=0.01, fader=pos)
        controlla(f"FADER {pos} %", db(a), atteso)

    print("Lati separati (1 kHz in L, R a -20 dB)")
    a, b = suona(testo, 1000, durata=0.03, coda=0.01, destra=0.1)
    controlla("L", db(a), 0.0)
    controlla("R", db(b), -20.0)

    print("PASS" if errori == 0 else f"FAIL: {errori} punti fuori")
    return 0 if errori == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
