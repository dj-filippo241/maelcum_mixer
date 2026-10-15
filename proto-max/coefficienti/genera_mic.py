"""Genera il dispositivo di P4: MC-MIC.

Uso:  python3 proto-max/coefficienti/genera_mic.py
Scrive in proto-max/: MC-MIC.genexpr, .maxpat, .amxd.

I numeri vengono da mic.py (e da fx.py per EQ2, rail e law di mandata).
Le mandate vanno ai bus di P3 con send~ mcfx_b<n>L / mcfx_b<n>R, come
MC-SEND e MC-RET: il receive~ di MC-BUS le somma.

Regole del codice gen~ (CLAUDE.md, pagate in P1/P2): funzioni con un solo
valore di ritorno; nessun nome esterno uguale a un parametro o a un
locale di funzione (controllo automatico in nomi_in_comune); d0/d1 sono
del downsampling.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import fx  # noqa: E402
import mic  # noqa: E402
from genera import Codice, box, linea  # noqa: E402
from genera_fx import (BUS, Patch, coefficienti_eq, eq_campione,  # noqa: E402
                       funzioni_eq, lisci, scrivi)

RD = fx.RAIL / fx.LIV
FE = mic.RAIL_FE
DIAL = [("gain", "GAIN", 0.0), ("low", "EQ LOW", 50.0),
        ("high", "EQ HIGH", 50.0)] + [(f"snd{n}", f"FX{n}", 0.0)
                                      for n in range(1, 5)]
# colori del LED: spento, verde, giallo, rosso
COLORI = ["0.18 0.18 0.18 1.", "0.1 0.85 0.25 1.", "1. 0.82 0. 1.",
          "1. 0.1 0.1 1."]


def genexpr():
    g = Codice()
    r = g.r
    r("// MC-MIC - prototipo Max P4 (mic-mono-moduli §2-§5, REV dec. 111).")
    r("// GENERATO da proto-max/coefficienti/genera_mic.py: non modificare.")
    r("// in1 = microfono (scheda audio col preamp al minimo); in2 ignorato.")
    r("// INA +30 dB (rail) -> passa-alto 60 Hz -> GAIN 0...+30 dB (rail) ->")
    r("// PRE (LED) -> EQ2 (rail) -> MUTE (1 ms) -> out1 = out2 (mono")
    r("// centrato); out3..out10 = SEND ai bus 1-4 (L, R); out11 = LED")
    r("// (0 spento, 1 verde, 2 giallo, 3 rosso).")
    r()
    funzioni_eq(r)
    for nome, _, ini in DIAL:
        r(f"Param {nome}({ini:g}, min=0, max=100);")
    r("Param mute(0, min=0, max=1);")
    r("History mrm(0);")
    r("History lenv(0);")
    r("History llat(0);")
    r("Data sv(4);")
    r("Data sa(2);")
    pos = len(g.righe)
    r("@@DATA@@")
    lisci(r, [n for n, _, _ in DIAL], {n: ini for n, _, ini in DIAL})
    r("sr4 = samplerate * 4;")
    r("// GAIN: stadio 2 col pot lineare (mic.g2)")
    r("tgn = s_gain / 100;")
    r(f"gst = ({mic.R2_G2!r} + tgn * {mic.P_G2!r}) / ({mic.R1_G2!r}"
      f" + (1 - tgn) * {mic.P_G2!r});")
    r("// passa-alto Sallen-Key 60 Hz (mic.hpf_w0_q)")
    w0, q = mic.hpf_w0_q()
    r(f"gpa = tan({w0 / 2!r} / sr4);")
    r(f"kpa = {1 / q!r};")
    coefficienti_eq(r, "s_low / 100", "s_high / 100")
    r("// MUTE: rampa 1 ms, lineare in dB fino a -100 dB, poi zero")
    r(f"pmu = 1 / ({mic.T_MUTE!r} * samplerate);")
    r("mrm = mrm + min(max(mute - mrm, -pmu), pmu);")
    r("gmu = pow(10, -5 * mrm) * (mrm < 1);")
    r("// SEND: pot curva A (fx.level_send)")
    m = fx.TAPER_A_MID
    for n in range(1, 5):
        r(f"ts{n} = s_snd{n} / 100;")
        r(f"ls{n} = (ts{n} <= 0.5) * {m / 0.5!r} * ts{n} + (ts{n} > 0.5) * "
          f"({m!r} + {(1 - m) / 0.5!r} * (ts{n} - 0.5));")
    r(f"// ingresso: 1,0 = {mic.V_SCHEDA:.4f} V al microfono; uscita: "
      f"1,0 = {fx.LIV:.4f} V")
    g.su("in1", "M_e", "M_o", 1, ("M", "su", 1))
    g.su("M_e", "M_u0", "M_u1", 2, ("M", "su", 2))
    g.su("M_o", "M_u2", "M_u3", 2, ("M", "su", 2))
    r("ppk = 0;")
    for k in range(4):
        r(f"pv = min(max({mic.G_INGRESSO * mic.V_SCHEDA!r} * M_u{k}, "
          f"{-FE!r}), {FE!r});")
        r("pv = svhp(sv, 2, pv, gpa, kpa);")
        r(f"pv = min(max(gst * pv, {-FE!r}), {FE!r});")
        r("ppk = max(ppk, abs(pv));")
        r(f"eq = pv / {fx.LIV!r};")
        eq_campione(r, "eq", 0, 0)
        r(f"M_y{k} = min(max(eq, {-RD!r}), {RD!r});")
    g.giu("M_v0", "M_y0", "M_y1", 2, ("M", "giu", 2))
    g.giu("M_v1", "M_y2", "M_y3", 2, ("M", "giu", 2))
    g.giu("M_w", "M_v0", "M_v1", 1, ("M", "giu", 1))
    r("mo = gmu * M_w;")
    r("// LED al nodo PRE: picco dei 4 campioni, rilascio 0,3 s,")
    r("// rosso con latch 0,5 s (mic.Led)")
    r(f"lcr = exp(-1 / ({mic.T_LED!r} * samplerate));")
    r("lenv = max(ppk, lcr * lenv);")
    v0, v1, v2 = mic.LED_V
    r(f"llat = (ppk >= {v2!r}) * {mic.T_ROSSO!r} + (ppk < {v2!r})"
      f" * max(llat - 1 / samplerate, 0);")
    r(f"lst = (llat > 0) * 3 + (llat <= 0) * ((lenv >= {v0!r})"
      f" + (lenv >= {v1!r}));")
    r("out1 = mo;")
    r("out2 = mo;")
    for n in range(4):
        r(f"out{3 + 2 * n} = ls{n + 1} * mo;")
        r(f"out{4 + 2 * n} = ls{n + 1} * mo;")
    r("out11 = lst;")
    g.righe[pos] = f"Data hb({g.n_hb});"
    return "\n".join(g.righe) + "\n"


def patch(codice):
    p = Patch()
    p.gen(codice, 11)
    for n, b in enumerate(BUS):
        for j, lato in enumerate("LR"):
            id_ = f"obj-s{n}{lato}"
            p.obj(id_, f"send~ {b}{lato}", 1, 0, [20 + 110 * (2 * n + j),
                                                    460, 100, 22], [])
            p.lines.append(linea("obj-gen", 2 + 2 * n + j, id_, 0))
    for j, (ng, nl, ini) in enumerate(DIAL[:3]):
        p.dial(ng, nl, ini, [8 + 60 * j, 8, 54, 48])
    for j, (ng, nl, ini) in enumerate(DIAL[3:]):
        p.dial(ng, nl, ini, [8 + 60 * j, 70, 54, 48])
    p.tab("mute", "MUTE", ["-", "MUTE"], 0, [190, 30, 50, 22])
    # LED: snapshot dello stato -> colore del pannello
    p.obj("obj-snap", "snapshot~ 30", 2, 1, [900, 480, 80, 22], ["float"])
    p.obj("obj-int", "i", 2, 1, [900, 510, 30, 22], ["int"])
    p.obj("obj-chg", "change", 1, 3, [900, 540, 50, 22], ["", "int", "int"])
    p.obj("obj-sel", "sel 0 1 2 3", 5, 5, [900, 570, 100, 22],
          ["bang"] * 4 + [""])
    p.boxes.append(box("obj-led", maxclass="panel", numinlets=1,
                       numoutlets=0, mode=0, rounded=20,
                       bgfillcolor=[float(c) for c in COLORI[0].split()],
                       presentation=1, presentation_rect=[204, 8, 18, 18],
                       patching_rect=[900, 680, 20, 20], varname="LED"))
    p.lines += [linea("obj-gen", 10, "obj-snap", 0),
                linea("obj-snap", 0, "obj-int", 0),
                linea("obj-int", 0, "obj-chg", 0),
                linea("obj-chg", 0, "obj-sel", 0)]
    for k, colore in enumerate(COLORI):
        id_ = f"obj-col{k}"
        p.boxes.append(box(id_, maxclass="message", numinlets=2,
                           numoutlets=1, outlettype=[""],
                           text=f"bgfillcolor {colore}",
                           patching_rect=[900 + 140 * k, 620, 130, 22]))
        p.lines += [linea("obj-sel", k, id_, 0),
                    linea(id_, 0, "obj-led", 0)]
    p.nota("Mic sulla sua traccia, uscita al Master. Preamp della scheda "
           "al minimo. LED pre-EQ, prima del MUTE.", [8, 124, 240, 40])
    return p.json()


def main():
    c = genexpr()
    scrivi("MC-MIC", patch(c), c)


if __name__ == "__main__":
    main()
