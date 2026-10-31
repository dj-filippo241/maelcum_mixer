"""Fa suonare MC-CHANNEL.genexpr tradotto in Python, campione per campione.

Uso:  python3 proto-max/coefficienti/prova_gen.py
Verifica il codice gen~ VERO (non le formule): sinusoidi in ingresso,
ampiezza in uscita, confronto con la risposta del modello (canale.py), che
verifica.py ha gia confrontato con LTspice. Prova anche law di GAIN e
fader, il selettore A/C/D e la separazione dei due lati.

Non prova la sintassi di gen~: quella la controlla Max all'apertura.
"""

import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import canale  # noqa: E402
import djm  # noqa: E402

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
                   "pow": math.pow, "max": max, "isnan": lambda v: float(math.isnan(v)), "log10": math.log10, "sin": math.sin, "cos": math.cos, "sqrt": math.sqrt, "abs": abs, "pi": math.pi, "samplerate": fs,
                   "poke": lambda d, v, i: d.__setitem__(int(i), v)}
        corpo, in_funzione, liv = [], False, 0
        for riga in testo.splitlines():
            riga = riga.split("//")[0].strip()
            if not riga:
                continue
            if not in_funzione:
                # blocchi if del codice principale -> rientri Python
                m = re.match(r"^if \((.*)\) \{$", riga)
                if m:
                    corpo.append("    " * liv + f"if {m.group(1)}:")
                    liv += 1
                    continue
                if riga == "}" and liv > 0:
                    liv -= 1
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
            corpo.append("    " * liv + riga[:-1])
        self.codice = compile("\n".join(corpo), FILE, "exec")

    def imposta(self, **p):
        """Param e stato lisciato gia al valore: niente rampa iniziale."""
        for k, v in p.items():
            self.ns[k] = float(v)
            if k == "incroci":
                self.ns["s_x"] = float(v)
            elif k == "curva":
                self.ns["s_c"] = float(v)
            elif k == "eqtipo":
                self.ns["s_t"] = float(v)
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
        ("C: tutte al centro", (50, 50, 50, 50), 1, [80, 350, 3150]),
        ("C: LOW a zero", (0, 50, 50, 50), 1, [50, 80, 150]),
        ("C: LOW-MID a zero", (50, 0, 50, 50), 1, [150, 230, 350]),
        ("C: MID-HIGH a zero", (50, 50, 0, 50), 1, [1148, 3150]),
        ("C: HIGH a zero", (50, 50, 50, 0), 1, [5000, 8000]),
        ("C: LOW al massimo", (100, 50, 50, 50), 1, [50, 300]),
        ("C: tutte a zero", (0, 0, 0, 0), 1, [150]),
        ("D: tutte al centro", (50, 50, 50, 50), 2, [150, 700, 3150]),
        ("D: LOW-MID a zero", (50, 0, 50, 50), 2, [367, 700]),
        ("D: MID-HIGH a zero", (50, 50, 0, 50), 2, [250, 1514]),
        ("D: solo MID-HIGH", (0, 0, 50, 0), 2, [250, 700]),
        ("A 400: tutte al centro", (50, 50, 50, 50), 3, [150, 400, 2500]),
        ("A 400: MID-HIGH a zero", (50, 50, 0, 50), 3, [400, 1000]),
        ("A 400: solo MID-HIGH", (0, 0, 50, 0), 3, [250, 400, 1000]),
        ("A 450: MID-HIGH a zero", (50, 50, 0, 50), 4, [450, 1060]),
        ("A 450: solo MID-HIGH", (0, 0, 50, 0), 4, [250, 450, 1000]),
    ]
    for nome, man, sel, freq in casi:
        var = "ACDEG"[sel]
        inc, pend = canale.INCROCI[var], canale.PENDENZE[var]
        for f in freq:
            p = dict(zip(["low", "lowmid", "midhigh", "high"], man))
            a, _ = suona(testo, f, incroci=sel, **p)
            atteso = canale.db(canale.isolator_os(
                f, FS, inc, [m / 100 for m in man], pend))
            controlla(f"{nome}, {f} Hz", db(a), atteso)

    casi_s = [
        ("tutte al centro", (50, 50, 50, 50), [40, 300, 1000, 2500, 8000]),
        ("LOW a zero", (0, 50, 50, 50), [40, 150, 300, 1000]),
        ("LOW al 10 %", (10, 50, 50, 50), [70]),
        ("LOW al massimo", (100, 50, 50, 50), [70, 300]),
        ("MID a zero", (50, 0, 50, 50), [300, 1000, 3000]),
        ("MID al 25 %", (50, 25, 50, 50), [1000]),
        ("MID al massimo", (50, 100, 50, 50), [1000]),
        ("MID-HIGH a zero (non agisce)", (50, 50, 0, 50), [2000]),
        ("HIGH a zero", (50, 50, 50, 0), [2000, 5000, 13000]),
        ("HIGH al massimo", (50, 50, 50, 100), [13000]),
        ("dub (LOW e HIGH su, MID a zero)", (100, 0, 0, 100),
         [40, 1000, 10000]),
        ("tutte a zero", (0, 0, 0, 0), [70, 1000, 13000]),
    ]
    for tipo, var in ((1, "F"), (2, "P")):
        print(f"EQ TIPO = DJM {var} (gen~ contro djm.djm_os, CURVA PIONEER; "
              "INCROCI non agisce)")
        for nome, man, freq in casi_s:
            for f in freq:
                p = dict(zip(["low", "lowmid", "midhigh", "high"], man))
                a, _ = suona(testo, f, eqtipo=tipo, incroci=2, curva=1, **p)
                atteso = djm.db(djm.djm_os(f, FS, [m / 100 for m in man], var,
                                           pioneer=True))
                controlla(f"{nome}, {f} Hz", db(a), atteso)

    print("Cambi di selettore (blocchi spenti non calcolati, stati a zero)")
    # A -> D -> DJM F -> DJM P -> ISOLATOR C, 1 kHz, MID-HIGH a zero: dopo ogni cambio
    # e 250 ms di assestamento (rampa 20 ms: residuo e^-12) l'uscita deve valere quella del modello.
    g = Gen(testo, FS)
    g.imposta(midhigh=0)
    passi = [(dict(incroci=0, eqtipo=0), ("ACD", 0)),
             (dict(incroci=2), ("ACD", 2)),
             (dict(incroci=4), ("ACDEG", 4)),
             (dict(eqtipo=1), ("F", 0)),
             (dict(eqtipo=2), ("P", 0)),
             (dict(incroci=1, eqtipo=0), ("ACD", 1))]
    n, f, picco, i = int(0.25 * FS), 1000.0, 0.0, 0
    for cambi, (tipo, sel) in passi:
        for k, v in cambi.items():
            g.ns[k] = float(v)          # solo il Param: la rampa gira
        y = []
        for _ in range(n):
            x = math.sin(2 * math.pi * f * i / FS)
            a, _ = g.campione(x, x)
            picco = max(picco, abs(a))
            y.append(a)
            i += 1
        man = [0.5, 0.5, 0.0, 0.5]
        if tipo in djm.VARIANTI:
            atteso = djm.db(djm.djm_os(f, FS, man, tipo))
        else:
            var = tipo[sel]
            atteso = canale.db(canale.isolator_os(
                f, FS, canale.INCROCI[var], man, canale.PENDENZE[var]))
        # il fit vuole la fase da campione 0: si rifa sugli ultimi 40 ms
        ss = [math.sin(2 * math.pi * f * (i - n + j) / FS) for j in range(n)]
        cc = [math.cos(2 * math.pi * f * (i - n + j) / FS) for j in range(n)]
        j0 = n - int(0.04 * FS)
        a_ = sum(y[j] * ss[j] for j in range(j0, n)) * 2 / (n - j0)
        b_ = sum(y[j] * cc[j] for j in range(j0, n)) * 2 / (n - j0)
        controlla(f"dopo {cambi}", db(math.hypot(a_, b_)), atteso)
    ok = picco < 1.5
    errori += not ok
    print(f"  {'ok  ' if ok else 'FUORI'} picco durante i cambi: {picco:.3f}"
          " (ingresso 1,0; MID-HIGH a zero)")

    print("CURVA PIONEER (D, MID-HIGH, 1514 Hz)")
    inc, pend = canale.INCROCI["D"], canale.PENDENZE["D"]
    for pos in (5, 20, 40, 50, 75, 100):
        man = (50, 50, pos, 50)
        a, _ = suona(testo, 1514, incroci=2, curva=1, low=50, lowmid=50,
                     midhigh=pos, high=50)
        atteso = canale.db(canale.isolator_os(
            1514, FS, inc, [m / 100 for m in man], pend,
            canale.banda_pioneer))
        controlla(f"MID-HIGH {pos} %", db(a), atteso)

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
