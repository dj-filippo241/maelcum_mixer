"""Prova di MC-LICKSHOT: il .genexpr tradotto in Python contro lickshot.py.

Uso:  python3 proto-max/coefficienti/prova_lickshot.py [--web dump.json]
1. gen~ e modello campione per campione (stessi comandi, comandi mossi).
2. Numeri: gamma del colpo, colpi al secondo, ritardo dell'eco, tetto della
   saturazione con RIPETIZIONI al massimo.
3. Con --web: il dump del banco web (web/tools/dump_lickshot.mjs) contro il
   modello.
Non prova la sintassi di gen~ ne la Delay vera di gen~: la Delay qui e la
stessa del modello (lettura prima della scrittura, interpolazione lineare).
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import fx  # noqa: E402
import lickshot as L  # noqa: E402
from prova_gen import Gen  # noqa: E402

QUI = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(os.path.dirname(QUI), "MC-LICKSHOT.genexpr")
FS = 48000.0


class Delay:
    def __init__(self, n):
        self.n, self.b, self.w = n, [0.0] * n, 0

    def read(self, d, interp="linear"):
        rpos = self.w - d
        while rpos < 0:
            rpos += self.n
        i0 = int(rpos)
        fr = rpos - i0
        return self.b[i0 % self.n] * (1 - fr) + self.b[(i0 + 1) % self.n] * fr

    def write(self, x):
        self.b[self.w] = x
        self.w = (self.w + 1) % self.n


def gen_lickshot():
    testo = open(FILE).read()
    righe = [x for x in testo.splitlines() if not x.startswith("Delay ")]
    g = Gen("\n".join(righe), FS)
    g.ns.update(min=min, tanh=math.tanh, dl=Delay(int(0.5 * FS) + 4))
    return g


def copione():
    """(secondi, comandi) in ordine: tasto, comandi mossi a meta."""
    return [(0.0, {"trig": 1}), (0.6, {"alt": 30, "vel": 90}),
            (0.9, {"tempo": 20, "rip": 80, "eco": 90}), (1.3, {"trig": 0}),
            (1.5, {"prof": 0, "trig": 1}), (1.7, {"trig": 0, "prof": 100}),
            (1.9, {"vol": 40, "trig": 1})]


def suona_gen(durata):
    g = gen_lickshot()
    passi, out, j = copione(), [], 0
    for i in range(int(durata * FS)):
        while j < len(passi) and i >= passi[j][0] * FS:
            for k, v in passi[j][1].items():
                g.ns[k] = float(v)
            j += 1
        g.campione(0.0, 0.0)
        out.append(g.ns["out1"] * fx.LIV)
    return out


def suona_modello(durata, fs=FS):
    m = L.Lickshot(fs)
    passi, out, j = copione(), [], 0
    for i in range(int(durata * fs)):
        while j < len(passi) and i >= passi[j][0] * fs:
            m.p.update({k: float(v) for k, v in passi[j][1].items()})
            j += 1
        out.append(m.campione())
    return out


def frequenze(y, fs):
    fr, last = [], -1
    for i in range(1, len(y)):
        if y[i - 1] < 0 <= y[i]:
            if last > 0:
                fr.append(fs / (i - last))
            last = i
    return fr


def main():
    errori = 0

    def controlla(nome, ok, testo):
        nonlocal errori
        errori += not ok
        print(f"  {'ok  ' if ok else 'FUORI'} {nome}: {testo}")

    print("1. gen~ contro modello (2,2 s, comandi mossi)")
    a, b = suona_gen(2.2), suona_modello(2.2)
    d = max(abs(x - y) for x, y in zip(a, b))
    controlla("scarto massimo", d < 1e-9, f"{d:.2e} V")
    controlla("niente valori non numerici", all(math.isfinite(x) for x in a), "")

    print("2. numeri")
    for prof, ott in ((67, 2.0), (100, 4.0)):
        m = L.Lickshot(FS, alt=100, vel=0, eco=0, trig=1, prof=prof)
        fi, giri = [], 0
        for _ in range(int(3 * FS)):
            su = m.su
            m.campione()
            fi.append(m.f)
            giri += su and not m.su
        fi = fi[int(FS):]
        a = prof / 100 * L.A_MAX
        alto = L.f0(100) * (L.VDD / 2 + a - L.VOFF) / (L.VDD / 2 - L.VOFF)
        basso = L.f0(100) * (L.VDD / 2 - a - L.VOFF) / (L.VDD / 2 - L.VOFF)
        mis = math.log2(max(fi) / min(fi))
        controlla(f"colpo, ALTEZZA 100, PROFONDITA {prof}", abs(max(fi) / alto - 1) < 0.01
                  and abs(min(fi) / basso - 1) < 0.01 and abs(mis - ott) < 0.1,
                  f"{max(fi):.0f} -> {min(fi):.0f} Hz, {mis:.2f} ottave (calcolo {alto:.0f} -> {basso:.0f})")
    controlla("colpi al secondo, VELOCITA 0", abs(giri / 3 - 1 / L.periodo_lfo(0)) < 0.4,
              f"{giri / 3:.2f} (calcolo {1 / L.periodo_lfo(0):.2f})")
    m = L.Lickshot(FS, alt=100, vel=0, eco=0, trig=1, prof=67)
    y = [m.campione() for _ in range(int(3 * FS))]
    fr = frequenze(y[int(FS):], FS)
    alto = L.f0(100) * (L.HI - L.VOFF) / (L.VDD / 2 - L.VOFF)
    controlla("quadra in uscita, cima del colpo", abs(max(fr) / alto - 1) < 0.02,
              f"{max(fr):.0f} Hz (calcolo {alto:.0f})")
    m = L.Lickshot(FS, prof=0, trig=1, eco=0)
    y = [m.campione() for _ in range(int(1 * FS))]
    fr = frequenze(y[int(0.5 * FS):], FS)
    controlla("PROFONDITA 0 = tono fisso", max(fr) / min(fr) < 1.01,
              f"{min(fr):.1f}-{max(fr):.1f} Hz (f0 {L.f0(80):.1f})")
    # ritardo dell'eco: un colpo di 20 ms, poi solo eco
    for tt in (0, 60, 100):
        m = L.Lickshot(FS, tempo=tt, rip=0, eco=100, vol=100, prof=0, trig=1)
        y = []
        for i in range(int(0.6 * FS)):
            m.p["trig"] = 1.0 if i < 0.02 * FS else 0.0
            y.append(m.campione())
        soglia = 0.2 * max(abs(v) for v in y[: int(0.02 * FS)])
        dopo = next(i for i in range(int(0.025 * FS), len(y)) if abs(y[i]) > soglia)
        atteso = L.tempo_eco(tt)
        controlla(f"ritardo dell'eco, TEMPO {tt}", abs(dopo / FS - atteso) < 0.004,
                  f"{1000 * dopo / FS:.1f} ms (calcolo {1000 * atteso:.1f} ms)")
    m = L.Lickshot(FS, rip=100, eco=100, tempo=30, trig=1)
    y = [m.campione() for _ in range(int(4 * FS))]
    pk = max(abs(v) for v in y[int(3 * FS):])
    controlla("RIPETIZIONI al massimo: l'eco resta limitata", pk < 4.0,
              f"picco {pk:.2f} V nell'ultimo secondo (rail del MONO +-16,5 V)")
    m.p["trig"] = 0.0
    y = [m.campione() for _ in range(int(3 * FS))]
    pk2 = max(abs(v) for v in y[int(2 * FS):])
    controlla("tasto lasciato, RIPETIZIONI al massimo: l'eco si autoalimenta",
              pk2 > 0.05, f"picco {pk2:.2f} V dopo 2 s")

    if "--web" in sys.argv:
        print("3. banco web contro modello")
        web = json.load(open(sys.argv[sys.argv.index("--web") + 1]))
        d = max(abs(x - y) for x, y in zip(web, b))
        controlla("scarto massimo", d < 1e-6, f"{d:.2e} V su {len(web)} campioni")

    print("PROVA PASSA" if not errori else f"PROVA NON PASSA ({errori})")
    sys.exit(1 if errori else 0)


if __name__ == "__main__":
    main()
