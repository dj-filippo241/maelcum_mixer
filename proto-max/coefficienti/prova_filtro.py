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
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import filtro  # noqa: E402
from prova_gen import Gen, ampiezza, db  # noqa: E402

QUI = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(os.path.dirname(QUI), "MC-FILTRO.genexpr")
FS = 48000.0


def funzioni_gen(testo):
    """Traduce in Python le funzioni del .genexpr (righe semplici)."""
    out, dentro = [], False
    for riga in testo.splitlines():
        riga = riga.split("//")[0].rstrip()
        m = re.match(r"^(\w+)\((.*)\)\s*\{$", riga)
        if m:
            out.append(f"def {m.group(1)}({m.group(2)}):")
            dentro = True
            continue
        if dentro:
            if riga.strip() == "}":
                dentro = False
                continue
            out.append("    " + riga.strip().rstrip(";"))
    return "\n".join(out)


def poke(m, v, i):
    m[i] = v


def nuovo(testo):
    g = Gen(testo, FS)
    rnd = random.Random(1)
    g.ns.update(peek=lambda m, i: m[i], poke=poke, tanh=math.tanh,
                log=math.log, sqrt=math.sqrt,
                noise=lambda: rnd.uniform(-1, 1))
    # solo le funzioni scritte nel .genexpr: niente aiuti da prova_gen
    for nome in ("bq", "ap"):
        g.ns.pop(nome, None)
    exec(funzioni_gen(testo), g.ns)
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


def modello(f, fc, amp_v, res, modo, lin, durata=0.12, coda=0.04,
            al="BUTTERWORTH", drive=0.0, lim="2+2"):
    """Core e overdrive di filtro.py a 4x, senza halfband: volt."""
    fs4 = 4 * FS
    c = filtro.Core(lin, fs4, al, lim)
    gres = filtro.res_law(res / 100)
    return filtro.sinusoide(
        c, f, fc, fs4, amp_v, durata, coda,
        lambda c, x, g: filtro.overdrive(c.passo(x, fc, gres, modo),
                                         drive / 100))


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

    print("LIMITATORE 3+3 del PULITO, risonanza: gen~ contro modello")
    for modo, nm in ((2, "lp"), (0, "hp")):
        for res in (70, 85):
            for dbu in (-10, 0, 6):
                av = 1.0954 * 10 ** (dbu / 20)
                p = {f"freq_{nm}": theta_freq(1000), f"res_{nm}": res,
                     "modo": modo, "core": 1, "lim": 1}
                y, n0 = suona(testo, 1000, av / liv, **p)
                gen_db = db(ampiezza(y, 1000, FS, n0) * liv / av)
                mod_db = db(modello(1000, 1000, av, res, nm, 1, lim="3+3")
                            / av)
                controlla(f"3+3 {nm.upper()} RES {res} % {dbu} dBu",
                          gen_db, mod_db, 0.3)

    print("PENDENZA a piccolo segnale (-30 dBu, sul taglio, 1 kHz)")
    attesi = {"BUTTERWORTH": -3.01, "LINKWITZ-RILEY": -6.02, "BESSEL": -3.01}
    for j, (al, att) in enumerate(attesi.items()):
        for modo, nm in ((2, "lp"), (0, "hp")):
            a = 1.0954 * 10 ** (-30 / 20) / liv
            y, n0 = suona(testo, 1000, a, modo=modo, pend=j,
                          **{f"freq_{nm}": theta_freq(1000)})
            controlla(f"{al} {nm.upper()}", db(ampiezza(y, 1000, FS, n0) / a),
                      att, 0.1)
            y, n0 = suona(testo, 2000, a, modo=modo, pend=j,
                          **{f"freq_{nm}": theta_freq(1000)})
            mod = db(modello(2000, 1000, a * liv, 0, nm, 0, al=al) / (a * liv))
            controlla(f"{al} {nm.upper()} a 2 kHz contro modello",
                      db(ampiezza(y, 2000, FS, n0) / a), mod, 0.05)

    print("DRIVE, LPF sul taglio, RES 85 %: gen~ contro modello")
    for dr in (50, 100):
        for dbu in (-10, 0):
            av = 1.0954 * 10 ** (dbu / 20)
            y, n0 = suona(testo, 1000, av / liv, modo=2, res_lp=85,
                          drive_lp=dr, freq_lp=theta_freq(1000))
            gen_db = db(ampiezza(y, 1000, FS, n0) * liv / av)
            mod_db = db(modello(1000, 1000, av, 85, "lp", 0, drive=dr) / av)
            controlla(f"DRIVE {dr} % {dbu} dBu", gen_db, mod_db, 0.3)
    av = 1.0954 * 10 ** (16 / 20)
    y, n0 = suona(testo, 1000, av / liv, modo=1, drive_lp=100)
    controlla("OFF con DRIVE 100 %: resta trasparente",
              db(ampiezza(y, 1000, FS, n0) * liv / av), 0.0, 0.01)
    y, n0 = suona(testo, 200, av / liv, modo=2, drive_lp=100, res_lp=85,
                  freq_lp=theta_freq(1000), durata=0.1, coda=0.05)
    picco = max(abs(v) for v in y[n0:]) * liv
    print(f"  info: +16 dBu a 200 Hz, RES 85 %, DRIVE 100 %: picco {picco:.2f} V"
          f" (tetto overdrive 1,59 V + passante)")

    print("Fischio (RES 100 %, senza ingresso): gen~ contro modello")
    for lin, nome_c, lim in ((0, "OTA (a')", "2+2"),
                             (1, "PULITO (c-B) 2+2", "2+2"),
                             (1, "PULITO (c-B) 3+3", "3+3")):
        for fc in (200, 1000, 5000):
            g = nuovo(testo)
            g.imposta(freq_lp=theta_freq(fc), res_lp=100, modo=2, core=lin,
                      lim=int(lim == "3+3"))
            n = int(0.35 * FS)
            y = [g.campione(0.0, 0.0)[0] for _ in range(n)]
            rms, f = nota(y, n - int(0.08 * FS), FS)
            c = filtro.Core(lin, 4 * FS, lim=lim)
            ym = [c.passo(1e-6 if i < 10 else 0.0, fc, -0.75, "lp")
                  for i in range(int(0.35 * 4 * FS))]
            rms_m, f_m = nota(ym, len(ym) - int(0.08 * 4 * FS), 4 * FS)
            controlla(f"{nome_c} fc {fc} Hz livello dBu",
                      20 * math.log10(rms * liv / 0.775),
                      20 * math.log10(rms_m / 0.775), 0.5)
            controlla(f"{nome_c} fc {fc} Hz nota (semitoni dal taglio)",
                      12 * math.log2(f / fc), 12 * math.log2(f_m / fc), 0.3)

    # Il primo MC-FILTRO usava d1 sia per la Q sia per il downsampling:
    # il lato R leggeva come Q un campione audio del lato L. Le prove
    # sopra suonano solo out1; qui out2 deve uguagliare out1, a meno del
    # seme di rumore, diverso per lato (pochi 1e-6). Il guasto dava 0,25-3,8.
    print("Canale R uguale al canale L (stesso ingresso, -10 dBu, 1 kHz)")
    a = 1.0954 * 10 ** (-10 / 20) / liv
    for p in ({"modo": 2, "res_lp": 85}, {"modo": 0, "res_hp": 85},
              {"modo": 2, "core": 1, "pend": 2, "drive_lp": 50},
              {"modo": 0, "core": 1, "pend": 1, "drive_hp": 50}):
        g = nuovo(testo)
        g.imposta(freq_lp=theta_freq(1000), freq_hp=theta_freq(1000), **p)
        dmax = 0.0
        for i in range(int(0.05 * FS)):
            x = a * math.sin(2 * math.pi * 1000 * i / FS)
            l, r = g.campione(x, x)
            dmax = max(dmax, abs(l - r))
        controlla(f"R - L {p}, scarto massimo x 1e6", dmax * 1e6, 0.0, 20.0)

    print("PASS" if errori == 0 else f"FAIL: {errori} punti fuori")
    return 0 if errori == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
