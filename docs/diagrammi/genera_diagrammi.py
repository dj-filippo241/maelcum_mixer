#!/usr/bin/env python3
# Genera lo schema funzionale totale e i diagrammi a blocchi SVG dei moduli
# del maelcum mixer, in italiano e in inglese.
# Uso:  python3 genera_diagrammi.py         (scrive i .svg italiani qui e quelli
#                                            inglesi in en/, stessi nomi file)
#       python3 genera_diagrammi.py --it    (solo italiano)
#       python3 genera_diagrammi.py --en    (solo inglese)
# I contenuti vengono dai design doc: quando un doc cambia, si aggiorna
# la funzione del modulo qui sotto e si rilancia lo script.
# Le etichette inglesi stanno in traduzione_en.py (dizionario italiano ->
# inglese): una riga italiana nuova senza traduzione esce come ATTENZIONE.
# Il dettaglio della cella parametrica 5-way sta in cella-v021.frag e nella
# sua copia inglese cella-v021-en.frag (SVG a mano, v0.2.1 + WIDTH v0.2.2).
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from traduzione_en import EN  # noqa: E402

DATA = "2026-11-04"
LANG = "it"
MISSING = []

AUDIO, CV, FB = "#C05A1B", "#2F6D8E", "#8A4A9E"
GREEN, AMBER, INK = "#1F7A4D", "#D97706", "#141414"

KINDS = {
    #          fill       stroke     sw   titolo     testo    dash
    "std":    ("#fff",    "#1A1A1A", 1.5, "#141414", "#444", None),
    "dark":   ("#141414", "#141414", 1.5, "#fff",    "#ddd", None),
    "ctrl":   ("#EEF3F6", CV,        1.2, CV,        "#444", None),
    "green":  ("#F1F7F3", GREEN,     1.5, GREEN,     "#444", None),
    "purple": ("#F6F1F8", FB,        1.5, FB,        "#444", None),
    "amber":  ("#FDF4EA", AMBER,     1.2, AUDIO,     "#444", None),
    "dashed": ("#F3F2EE", "#888",    1.5, "#444",    "#555", "6 4"),
    "note":   ("#F3F2EE", "#AAA",    1.0, "#141414", "#444", None),
    # schema totale: semantica dei colori come nello schema funzionale JBK
    "jgreen": ("#CFE8C1", "#6AA84F", 1.4, "#24461A", "#2F4F26", None),
    "jgrey":  ("#E3E3E3", "#7F7F7F", 1.4, "#262626", "#3A3A3A", None),
    "jext":   ("#FFFFFF", "#7F7F7F", 1.4, "#262626", "#3A3A3A", "6 4"),
    "jleg":   ("#FFF2CC", "#D6B656", 1.2, "#7F6000", "#444", None),
}

NEUTRO = re.compile(r"^[^A-Za-zÀ-ÿ]*$")     # solo numeri e simboli: uguale nelle due lingue


def tr(s):
    if LANG == "it" or not s or NEUTRO.match(s):
        return s
    if s in EN:
        return EN[s]
    if s not in MISSING:
        MISSING.append(s)
    return s


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Box:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.cx, self.cy = x + w / 2, y + h / 2
        self.l, self.r = (x, self.cy), (x + w, self.cy)
        self.t, self.b = (self.cx, y), (self.cx, y + h)


class Diagram:
    def __init__(self, name, w, h, title, sub, pill=None, pill_color=AMBER):
        self.name, self.w, self.h = name, w, h
        self.o = []
        self.warn = []
        self.o.append(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            'font-family="Helvetica Neue, Helvetica, Arial, sans-serif">\n  <defs>')
        for mid, col, size in (("ar", AUDIO, 7), ("arb", FB, 7), ("arw", CV, 6), ("ark", "#333", 7)):
            self.o.append(
                f'    <marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="{size}" '
                f'markerHeight="{size}" orient="auto-start-reverse">'
                f'<path d="M0,0 L10,5 L0,10 z" fill="{col}"/></marker>')
        self.o.append("  </defs>")
        self.o.append(f'  <rect width="{w}" height="{h}" fill="#FBFAF7"/>')
        self.text(40, 52, title, 24, INK, weight=700)
        self.text(40, 76, sub, 13, "#666")
        if pill:
            pill = tr(pill)
            pw = max(150, int(len(pill) * 6.9) + 30)
            self._chk(sub, 13, w - 80 - pw - 20, "sottotitolo")
            self.o.append(f'  <rect x="{w - 40 - pw}" y="34" width="{pw}" height="24" rx="12" fill="{pill_color}"/>')
            self.text(w - 40 - pw / 2, 50, pill, 12, "#fff", "middle", 600, raw=True)
        else:
            self._chk(sub, 13, w - 80, "sottotitolo")

    def _chk(self, s, size, maxw, where, raw=False):
        if not raw:
            s = tr(s)
        est = len(s) * size * 0.52
        if est > maxw:
            self.warn.append(f"{LANG}/{self.name}: testo largo ~{est:.0f} > {maxw:.0f} in {where}: {s[:50]}")

    def text(self, x, y, s, size=10.5, color="#444", anchor="start", weight=None, raw=False):
        if not raw:
            s = tr(s)
        a = f' text-anchor="{anchor}"' if anchor != "start" else ""
        wgt = f' font-weight="{weight}"' if weight else ""
        self.o.append(f'  <text x="{x:g}" y="{y:g}" font-size="{size:g}"{wgt} fill="{color}"{a}>{esc(s)}</text>')

    def box(self, x, y, w, h, title, lines=(), kind="std", tsize=13, lsize=10.5, align="middle"):
        fill, stroke, sw, tcol, lcol, dash = KINDS[kind]
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.o.append(f'  <rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="6" fill="{fill}" '
                      f'stroke="{stroke}" stroke-width="{sw:g}"{d}/>')
        step = lsize + 5.5
        block = (tsize if title else 0) + len(lines) * step
        ty = y + (h - block) / 2 + (tsize * 0.85 if title else 0)
        if block > h - 8:
            self.warn.append(f"{LANG}/{self.name}: box '{title}' troppo basso ({block:.0f} > {h})")
        tx = x + w / 2 if align == "middle" else x + 18
        if title:
            self.text(tx, ty, title, tsize, tcol, align, 700)
            self._chk(title, tsize * 1.08, w - 10, f"titolo box {title}")
        ly = ty + (step if title else lsize * 0.85)
        for ln in lines:
            col = lcol
            if ln.startswith("!"):          # riga evidenziata (questione/feedback)
                ln, col = ln[1:], FB if kind != "dark" else "#E7B4F2"
            self.text(tx, ly, ln, lsize, col, align)
            self._chk(ln, lsize, w - (8 if align == "middle" else 26), f"box {title}")
            ly += step
        return Box(x, y, w, h)

    def arrow(self, pts, kind="audio", head=True):
        col, sw, mid, dash = {"audio": (AUDIO, 2.5, "ar", None), "cv": (CV, 1.5, "arw", "6 4"),
                              "fb": (FB, 2.2, "arb", None), "k": ("#333", 1.6, "ark", None)}[kind]
        d = "M " + " L ".join(f"{px:g} {py:g}" for px, py in pts)
        ds = f' stroke-dasharray="{dash}"' if dash else ""
        me = f' marker-end="url(#{mid})"' if head else ""
        self.o.append(f'  <path d="{d}" stroke="{col}" stroke-width="{sw:g}" fill="none"{ds}{me}/>')

    def dot(self, x, y):
        self.o.append(f'  <circle cx="{x:g}" cy="{y:g}" r="5" fill="{AUDIO}"/>')

    def circle(self, cx, cy, r, lines, kind="in", size=11.5):
        fill, stroke = {"in": ("#F4B6B4", "#C0504D"), "out": ("#B4CBEF", "#4A72B8")}[kind]
        self.o.append(f'  <circle cx="{cx:g}" cy="{cy:g}" r="{r:g}" fill="{fill}" stroke="{stroke}" stroke-width="1.4"/>')
        step = size + 3
        y = cy - (len(lines) - 1) * step / 2 + size * 0.35
        for ln in lines:
            self.text(cx, y, ln, size, "#1A1A1A", "middle", 600)
            self._chk(ln, size, 2 * r - 8, f"cerchio {lines[0]}")
            y += step
        return Box(cx - r, cy - r, 2 * r, 2 * r)

    def raw(self, s):
        self.o.append(s)

    def legend(self, y, items):
        x = 40
        for kind, label in items:
            label = tr(label)
            if kind in ("audio", "cv", "fb"):
                col, sw, dash = {"audio": (AUDIO, 2.5, None), "cv": (CV, 1.5, "6 4"), "fb": (FB, 2.2, None)}[kind]
                ds = f' stroke-dasharray="{dash}"' if dash else ""
                self.o.append(f'  <path d="M {x} {y} L {x + 50} {y}" stroke="{col}" stroke-width="{sw:g}"{ds}/>')
            elif kind == "dashed":
                self.o.append(f'  <rect x="{x}" y="{y - 9}" width="50" height="18" rx="4" fill="#F3F2EE" '
                              'stroke="#888" stroke-width="1.5" stroke-dasharray="6 4"/>')
            else:
                self.o.append(f'  <rect x="{x}" y="{y - 8}" width="46" height="16" rx="8" fill="{kind}"/>')
            self.text(x + 58, y + 4, label, 11.5, "#333", raw=True)
            x += 58 + int(len(label) * 6.2) + 40
        if x > self.w:
            self.warn.append(f"{LANG}/{self.name}: legenda larga {x} > {self.w}")

    def footer(self, s, data=DATA):
        s = tr(s)
        self.text(40, self.h - 22, s + " · " + data, 10.5, "#999", raw=True)
        self._chk(s, 10.5, self.w - 60, "footer", raw=True)

    def save(self):
        self.o.append("</svg>\n")
        out = HERE if LANG == "it" else os.path.join(HERE, "en")
        os.makedirs(out, exist_ok=True)
        open(os.path.join(out, self.name + ".svg"), "w", encoding="utf-8").write("\n".join(self.o))
        return self.warn


def chain_h(d, boxes, kind="audio"):
    for a, b in zip(boxes, boxes[1:]):
        d.arrow([a.r, (b.x - 2, b.cy)], kind)


def chain_v(d, boxes, kind="audio"):
    for a, b in zip(boxes, boxes[1:]):
        d.arrow([a.b, (b.cx, b.y - 2)], kind)


# ---------------------------------------------------------------- CANALE
def canale():
    d = Diagram("canale-cdj", 1560, 900, "MODULO CANALE CDJ / LINE",
                "maelcum mixer — design v0.4 + isolator v0.5 (incroci C) · GAIN a pot doppio (dec. 162) · levetta del filtro col dip del fader (dec. 163) — metà L; R identica",
                "phono MM incluso (dec. 79)", GREEN)
    rca = d.box(40, 170, 130, 72, "RCA IN", ["line −10 dBV…+4 dBu"])
    d.text(105, 258, "0 dBu nom / +8 worst", 10, AUDIO, "middle")
    A = d.box(215, 170, 165, 72, "[A] PROT + BUFFER", ["R 100 Ω + TVS low-cap + bead", "OPA1612 unity, Zin 100k"])
    B = d.box(425, 162, 185, 88, "[B] GAIN (dec. 162)", ["pot doppio lineare selezionato", "Rl 4,30k + non invertente ×3,15",
                                                      "−∞ … 0 (detent) … +10 dB"], tsize=12)
    d.text(517, 266, "post: 0 / +10 dBu worst", 10, AUDIO, "middle")
    C = d.box(650, 150, 250, 112, "[C] EQ ISOLATOR 4 BANDE (v0.5)",
              ["bande in parallelo (dec. 105)", "incroci C: 150 LR2 / 350 / 3150 Hz (152)",
               "fondo corsa −48 dB … 0 (detent) … +6 dB", "somma non invertente + servo DC"], tsize=12)
    d.text(775, 278, "post: 0 / +16 dBu worst", 10, AUDIO, "middle")
    chain_h(d, [rca, A, B, C])
    gpo = d.box(425, 96, 185, 44, "", ["metà sinistra = trim:", "−2/−3 dB a ore 11 (dec. 162)"], "ctrl", lsize=10)
    d.arrow([gpo.b, (B.cx, B.y - 2)], "cv")
    pots = d.box(650, 84, 250, 44, "", ["4 pot doppi lineari B a catalogo (168)", "senza contatto di fondo corsa (127)"],
                 "ctrl", lsize=10)
    d.arrow([pots.b, (C.cx, C.y - 2)], "cv")
    # nodo split
    nx = 945
    d.arrow([C.r, (nx, 206)], head=False)
    d.text(nx - 8, 352, "nodo split post-EQ", 11, INK, "end", 700)
    D = d.box(995, 110, 220, 66, "[D] CUE SEND", ["buffer → switch cue → CUE bus", "post-EQ, pre-filtro, pre-fader"])
    E = d.box(995, 196, 220, 86, "[E] SEND TAP (dec. 91a)",
              ["buffer ≤ 50 Ω → backplane slot 3", "EQ2 + level + assign vivono",
               "nel micro-modulo FX-SEND"])
    d.arrow([(nx, 206), (nx, D.cy), (D.x - 2, D.cy)])
    d.arrow([(nx, 206), (nx, E.cy), (E.x - 2, E.cy)])
    d.dot(nx, 206)
    d.text(1228, D.cy + 4, "→ modulo CUE", 10.5, "#777")
    d.text(1228, E.cy + 4, "→ FX-SEND del canale", 10.5, "#777")
    BT = d.box(995, 302, 220, 70, "BOTTONI CUE + ASSIGN S1-S4",
               ["con luce, a ritenuta (dec. 123)", "linee logiche +5 V → FX-SEND"], "ctrl", tsize=12)
    d.arrow([BT.r, (1300, BT.cy)], "cv")
    d.text(1222, BT.cy - 8, "→ FX-SEND", 10, CV)
    # colonna uscita
    G = d.box(1330, 420, 190, 66, "[G] METER DJ", ["10 seg × 3 dB (LM3915)", "pre-fader, senza filtro (161b)"])
    H = d.box(1330, 516, 190, 76, "[H] FADER → 2 VCA", ["fader mono 100 mm (dec. 126)", "VCA trimmati + I/V",
                                                     "curva «sale piano» (129 G)"])
    I = d.box(1330, 622, 190, 70, "[I] OUT + LEVETTA", ["HPF / OFF / LPF (ADG)", "→ DJ bus / bus HPF / bus LPF",
                                                     "R 10k sui net (dec. 159)"])
    d.text(1425, 708, "0 dBu nom / +16 worst", 10, AUDIO, "middle")
    d.arrow([(nx, 206), (nx, 394), (G.cx, 394), (G.cx, G.y - 2)])
    d.text(1180, 388, "pre-fader, dopo l'EQ, senza filtro", 10.5, "#777")
    chain_v(d, [G, H, I])
    fc = d.box(1330, 100, 190, 44, "", ["slider mono 100 mm", "→ shaper → CV dei 2 VCA"], "ctrl", lsize=10)
    d.arrow([fc.r, (1542, fc.cy), (1542, H.cy), (H.x + H.w + 2, H.cy)], "cv")
    DIP = d.box(985, 520, 300, 150, "LOGICA DEL DIP (dec. 163)",
                ["74HC86 + 74HC14 + 74HC74, antirimbalzo RC", "2 celle RC 10k/50n + buffer → EC− dei VCA",
                 "VCA giù a −100 dB in ~1 ms,", "ADG commuta a ~1,6 ms, su in ~3 ms",
                 "!all'orecchio: respiro di 3-4 ms, niente click", "CUE, send e meter non lo vedono"],
                "ctrl", tsize=12, lsize=10)
    d.arrow([(DIP.x + DIP.w, 554), (H.x - 2, 554)], "cv")
    d.arrow([(DIP.x + DIP.w, 650), (I.x - 2, 650)], "cv")
    d.text(1292, 548, "dip", 10, CV)
    d.text(1292, 644, "ADG", 10, CV)
    # phono
    A0 = d.box(40, 330, 215, 104, "[A0] PHONO MM v0.1",
               ["RIAA passiva 42 dB · EIN 1,79 µV", "curva ≤ ±0,05 dB 100 Hz–20 kHz",
                "subsonica fissa 18 Hz (dec. 138)", "overload +18 dBu · phono-stage.md"], "green", tsize=12.5)
    SEL = d.box(40, 464, 215, 54, "SELETTORE LINE/PHONO", ["levetta (dec. 123) + mute breve"], "ctrl", tsize=12)
    d.arrow([A0.b, (SEL.cx, SEL.y - 2)])
    d.arrow([SEL.r, (440, SEL.cy), (440, B.y + B.h + 2)])
    d.text(268, SEL.cy - 8, "→ [B] GAIN, nodo del buffer line", 10, "#777")
    d.box(40, 730, 600, 84, "[H2] PSU LOCALE",
          ["±22,0 V audio e ±19 V LN dal box esterno (dec. 113)", "→ ±18 V audio (LM317/337) · ±15,0 V LN (pre-reg ±16,5 → LT3045/94)",
           "· +5 V control dal bus"],
          "note", align="start", lsize=10.5, tsize=12)
    d.box(670, 730, 420, 84, "RUMORE DEL CANALE",
          ["−94,5 dBu A-wtd con GAIN a pot (dec. 162)", "target ≤ −80 (dec. 89) · era −92,9 col GAIN a VCA",
           "isolator v0.5: −97,4 al centro (= v0.4)"], "note", align="start", lsize=10.5, tsize=12)
    d.box(1120, 730, 400, 84, "SCHEDE [PROVVISORIO, todo 249]",
          ["segnale col C96 + isolator senza C96", "ponte 2×18 · PCB: tutte e due PASSA",
           "logica 74HC in TSSOP-14"], "note", align="start", lsize=10.5, tsize=12)
    d.legend(846, [("audio", "percorso audio (livelli annotati in rosso)"), ("cv", "comando / CV / logiche"),
                   (FB, "nota evidenziata")])
    d.footer("Fonte: docs/fase1/cdj-line-channel.md v0.4 (§3.2 dec. 162, §3.6 dec. 163, §3.8) + eq-isolator-v0.4.md §10 (v0.5, dec. 152/168) + phono-stage.md + sim/gain-pot/ + sim/cdj/RISULTATI-filtsel-dip.md")
    return d.save()


# ---------------------------------------------------------------- FX-RET
def fx():
    d = Diagram("fx", 1560, 920, "MODULO FX-RET ×4 — BUS + RITORNO + REROUTE",
                "maelcum mixer — design v0.3-WIP: 4 moduli identici, uno per bus (dec. 130) · matrice di feedback 16 coppie VCA con self (dec. 91) · sotto: il modulo del BUS n",
                "v0.3-WIP (dec. 130)")
    y = 150
    src = d.box(40, y - 10, 200, 106, "NET Sn (backplane)",
                ["4 FX-SEND · fino a 4 MIC/MONO", "4 reroute (dai 4 FX-RET)", "12 contributori, multidrop:",
                 "R 10k lato sorgente"], tsize=12)
    SUM = d.box(285, y, 180, 86, "SUMMING BUS n", ["virtual-earth, Cf 10 pF", "worst 12 × 0 dBu: +21,5 dBu"])
    DRV = d.box(510, y, 180, 86, "DRIVER", ["buffer low-Z ≤ 50 Ω (OPA1612)", "!pad fisso 0 dB (dec. 108)"])
    PRO = d.box(735, y, 170, 86, "PROTEZIONE", ["R serie 100 Ω + TVS ≤ 5 pF", "banda 40 kHz verificata §8.4"])
    JS = d.box(950, y, 150, 86, "JACK SEND n", ["→ pedale (L/R)", "mono = sum 2 × 10k"], "dark")
    PED = d.box(1145, y, 110, 86, "PEDALE", ["esterno", "−20…+18 dBu"], "dashed")
    JR = d.box(1300, y, 180, 86, "JACK RETURN n", ["← pedale (L/R, stereo-capable)"], "dark")
    chain_h(d, [src, SUM, DRV, PRO, JS, PED, JR])
    d.text(SUM.cx + 14, y + 104, "margine 7,3 V al clamp ±16,5", 10, AUDIO)
    PDC = d.box(1290, 290, 200, 84, "PROT + DC CONTROL", ["DC servo integrato VALIDATO", "corner 0,05-0,5 Hz, nulling 84 dB"])
    BUF = d.box(1290, 404, 200, 66, "BUFFER HI-Z", ["JFET, Zin ≥ 1 MΩ (bias 1 MΩ §8.4)"])
    GAI = d.box(1290, 500, 200, 96, "GAIN (dec. 162)", ["pot doppio lineare selezionato", "in retroazione (Ra 1,24k)",
                                                     "−∞ → 0 → +20 dB · metà sx = trim", "!niente VCA · K4 (dec. 84)"])
    EQ2 = d.box(1290, 626, 200, 70, "EQ2 RITORNO", ["celle serie v0.3 VALIDATE", "LOW ~120 Hz / HIGH ~4,5 kHz"])
    d.arrow([JR.b, (PDC.cx, PDC.y - 2)])
    chain_v(d, [PDC, BUF, GAI, EQ2])
    MET = d.box(1020, 626, 220, 70, "METER DEL RITORNO", ["barra 10 LED per ritorno (dec. 116)", "release ~0,3 s (dec. 81) · latch clip"])
    NOD = d.box(770, 626, 200, 70, "NODO REROUTE", ["PRE-FADER [BLOCCATO]", "fader giù → il feedback continua"], "ctrl")
    FAD = d.box(520, 626, 200, 70, "FADER ritorno → 2 VCA", ["fader mono 100 mm (dec. 126)", "→ backplane MASTER SUM"])
    d.arrow([EQ2.l, (MET.x + MET.w + 2, MET.cy)])
    d.arrow([MET.l, (NOD.x + NOD.w + 2, NOD.cy)])
    d.arrow([NOD.l, (FAD.x + FAD.w + 2, FAD.cy)])
    OUT = d.box(150, 736, 290, 58, "→ BACKPLANE MASTER SUM", ["un ingresso per ritorno: MSUM2-5 (dec. 94a)"], "dark")
    d.arrow([FAD.l, (OUT.cx, FAD.cy), (OUT.cx, OUT.y - 2)])
    MAT = d.box(660, 390, 420, 150, "REROUTE × 4: 3 CROSS + SELF (dec. 91b)",
                ["4 coppie VCA V2181L per modulo (8 chip); 16 coppie sul mixer",
                 "law a tratti SPEC verificata end-to-end (§8.3)",
                 "driver d'iniezione INVERTENTE unity → net S1-S4 (R 10k)",
                 "!self-route AMMESSO: esce sul proprio net e rientra",
                 "bounded-by-design confermato sul ramo self (§8.5)"], "purple", lsize=10)
    d.arrow([NOD.t, (NOD.cx, MAT.y + MAT.h + 2)], "fb")
    d.arrow([MAT.t, (MAT.cx, 300), (SUM.cx, 300), (SUM.cx, SUM.y + SUM.h + 2)], "fb")
    d.text(SUM.cx + 14, 292, "verso i SUMMING dei 4 bus, INCLUSO il proprio (via backplane) · giro = GAIN + reroute (LEVEL fuori): con GAIN +20 innesca a ~45 % del reroute", 10.5, FB)
    CVB = d.box(290, 400, 320, 130, "CATENA CV REROUTE",
                ["pot 9 mm con scatto al centro (dec. 125)", "→ CV buffer → shaper a tratti (dec. 70)",
                 "→ smoothing 1 ms (dec. 80)", "→ CV 6,1 mV/dB ai VCA (dec. 92)", "1 CV per coppia L/R"], "ctrl", lsize=10)
    d.arrow([CVB.r, (MAT.x - 2, CVB.cy)], "cv")
    d.box(520, 730, 970, 110, "",
          ["±18 V audio (summing/driver/VCA) · ±15 V LN (CV/shaper/servo) · VCA per modulo: 8 reroute + 2 fader = 10 (4 moduli: 40)",
           "mixer ~54 VCA (sistema-vca-trim §4) · rotta clone CoolAudio V2181L, acquisti dopo il prototipo · mute dei send: GLOBAL_MUTE (dec. 94b)",
           "rumore: ritorno −96,1 dBu A (dec. 162) · bus da −101,3 a −91,5 dBu A con le 4 iniezioni dei reroute (target −88)",
           "schede [PROVVISORIO, todo 249]: segnale col C96 + reroute senza C96, ponte 2×16 · PCB: tutte e due PASSA"],
          "note", align="start", lsize=10.5)
    d.legend(866, [("audio", "audio"), ("fb", "feedback (reroute)"), ("cv", "comando / CV"),
                   ("dashed", "esterno al mixer")])
    d.footer("Fonte: docs/fase1/fx-module.md v0.3-WIP (§2bis dec. 130, §5 dec. 162, §7, §8.3-8.5) + sistema-vca-trim.md §4 + sistema-polarita.md + sim/fx/RISULTATI-fx-ret-bus-130.md")
    return d.save()


# ---------------------------------------------------------------- FX-SEND
def fx_send():
    d = Diagram("fx-send", 1560, 720, "MICRO-MODULO FX-SEND (×4, uno per canale)",
                "maelcum mixer — design v0.1-WIP + PCB v0.2 (dec. 91a, 133-136): EQ2 + level + assign fuori dal canale CDJ · 4× stesso PCB · metà L; R identica",
                "PCB v0.2 PASSA", GREEN)
    IN = d.box(40, 170, 195, 96, "SEND TAP L/R", ["dal canale CDJ, blocco [E]", "post-EQ, pre-filtro, pre-fader",
                                               "backplane slot 3 del canale"], "dark")
    BUF = d.box(275, 178, 150, 80, "BUFFER IN", ["OPA1612 unity", "isola il driver di canale"])
    EQ = d.box(465, 160, 240, 116, "EQ2 — celle serie",
               ["LOW shelf ~120 Hz (Baxandall,", "un pot doppio 10k per la cella)", "HIGH sottrattiva ~4,5 kHz (q. 68)",
                "−∞ → 0 → +6 · pot lineare + R (129 A3)"], lsize=10)
    LEV = d.box(745, 170, 185, 96, "LEVEL", ["pot doppio 10k log A", "−20 dB a metà, mai gain > 0", "!unico livello al pedale (108)"])
    INJ = d.box(970, 160, 230, 116, "BUFFER DI INIEZIONE",
                ["OPA1654 quad × 2 (unity)", "8 sezioni: S1-S4 × L/R", "+ R 10k di iniezione per linea",
                 "![PROVV] 1 buffer per lato: stesso rumore"], lsize=10)
    ASG = d.box(1240, 160, 280, 116, "ASSIGN × 4 (S1-S4)",
                ["π SPDT ADG1434 DOPO la R 10k:", "sul nodo a massa virtuale del bus", "(vede ~8 mV: niente clip a +22 dBu)",
                 "multipli e simultanei [BLOCCATO]"], lsize=10)
    chain_h(d, [IN, BUF, EQ, LEV, INJ, ASG])
    BUS = d.box(1240, 340, 280, 70, "→ BUS FX 1-4 (net S1-S4)",
                ["summing virtual-earth dei FX-RET", "net multidrop, come il DJ bus"], "dark")
    d.arrow([ASG.b, (BUS.cx, BUS.y - 2)])
    BT = d.box(640, 350, 260, 92, "BOTTONI ASSIGN S1-S4",
               ["sul pannello del CANALE, con luce", "a ritenuta (dec. 123) · +5 V su cavo",
                "l'audio non passa mai dai contatti"], "ctrl", tsize=12)
    ZC = d.box(935, 340, 245, 112, "TAGLIO ALLO ZERO (todo 224)",
               ["1 comparatore per lato + 74HC74", "bottone → D, clock dal comparatore", "!gradino −51/−54 dB, ritardo 20-80 µs",
                "(il pin IN è logico: un RC non fa rampa)"], "ctrl", tsize=12, lsize=10)
    d.arrow([BT.r, (ZC.x - 2, BT.cy)], "cv")
    d.arrow([(ZC.x + ZC.w, ZC.cy), (1205, ZC.cy), (1205, 300), (1262, 300), (1262, ASG.y + ASG.h + 2)], "cv")
    GM = d.box(1240, 480, 280, 70, "GLOBAL_MUTE (linea c9)",
               ["dal mute controller [L] del master", "muta i buffer d'iniezione (dec. 94b)"], "ctrl", tsize=12)
    d.arrow([GM.l, (918, GM.cy), (918, 300), (1060, 300), (1060, INJ.y + INJ.h + 2)], "cv")
    d.box(40, 340, 560, 210, "PERCHÉ UN MICRO-MODULO",
          ["Il canale CDJ resta più semplice: gli resta solo il SEND TAP.",
           "Comportamenti LOCKED invariati (SPECIFICA §2): punto di presa,",
           "bande e law dell'EQ2, level senza gain, assign multipli.",
           "Rumore (todo 184): un send assegnato −101,7 dBu A al bus",
           "a LEVEL max, floor −111,2. Sistema con 4 send al massimo",
           "su ogni bus: −81,8 dBu A, PASS: la deroga della dec. 95 non serve.",
           "Pot su scheda comandi dietro il pannello, cavo 2×12 (dec. 136)."],
          "note", align="start", lsize=11)
    d.legend(610, [("audio", "audio"), ("cv", "comando: logiche +5 V / mute")])
    d.footer("Fonte: docs/fase1/fx-send-module.md (§2 REV 2026-11-03, §3-§6) + sim/fx/RISULTATI-fx-send-assign.md + RISULTATI-send-chain-v2.md + pcb/fx-send/NOTE.md + decisioni 91/94b/108/123/136")
    return d.save()


# ---------------------------------------------------------------- MASTER
def master():
    d = Diagram("master-out", 1560, 960, "MODULO MASTER OUT",
                "maelcum mixer — design v0.2 + stadio finale v0.3 DEFINITIVA (dec. 86) + MONO M/S e inserzione (dec. 111) + schede (dec. 142-143) · rami indipendenti dallo stesso nodo",
                "stadio finale v0.3 chiuso", GREEN)
    CON = d.box(40, 110, 215, 150, "MASTER SUM: 7 CONTRIBUTORI",
                ["5-way (MSUM1)", "ritorni FX 1-4 (MSUM2-5)", "mic (MSUM6) · mono (MSUM7)", "stereo, single-ended 0 dBu",
                 "(dec. 94a, 97)"], "dark", tsize=12)
    A2 = d.box(300, 120, 210, 80, "[A2] MASTER SUMMING × 2",
               ["invertente su massa virtuale", "OPA1612, unity, ±15 V LN"], tsize=12)
    A3 = d.box(545, 112, 265, 96, "[A3] MONO (tasto, dec. 111d)",
               ["M = (L+R)/2 · S = (L−R)/2", "1 VCA su S: tasto → −100 dB in 1 ms", "separazione −38 dB worst (todo 200)",
                "agisce su tutte le uscite"], tsize=12, lsize=10)
    INS = d.box(845, 120, 220, 80, "INS_SEND / INS_RET", ["EQ grafico opzionale (dec. 111b)", "senza modulo: ponticello JMS"], tsize=12)
    d.arrow([(CON.x + CON.w, A2.cy), (A2.x - 2, A2.cy)])
    chain_h(d, [A2, A3, INS])
    by = 238                         # bus del nodo programma
    cols = {"main": 410, "booth": 665, "rec": 915, "mon": 1165}
    d.arrow([INS.b, (INS.cx, by)], head=False)
    d.arrow([(410, by), (cols["mon"], by)], head=False)
    d.dot(INS.cx, by)
    d.text(540, by - 8, "nodo programma: dopo MONO e inserzione, pre-master-level", 10.5, "#777")
    # colonna master
    D = d.box(300, 262, 220, 92, "[D] MASTER LEVEL × 1",
              ["2 × VCA V2181L (L/R), una CV", "−∞ → 0 (scatto al centro) → +6 dB", "shaper a 4 rami (dec. 139)"])
    E = d.box(300, 378, 220, 60, "[E] METER PICKUP", ["2 × 20 seg × 3 dB, release ~0,3 s, latch"], lsize=10)
    F = d.box(300, 462, 220, 60, "[F] OUT FRONT × 2", ["OPA1612, composito con [G]"])
    G = d.box(300, 546, 220, 124, "[G] STADIO HV BOOTSTRAP",
              ["!rail OPA1612 flottanti OUT ± 5,3 V", "stringa 9 × 1N4148 + pass MJE340/350",
               "+25,4…+25,6 dBu · THD 0,00012 % a +24", "caldo e freddo di L e R: 4 stadi"], tsize=12, lsize=10)
    H = d.box(300, 694, 220, 60, "[H] MUTE + PROTEZIONE", ["relè G6K-2F, comandati da [L]"])
    I = d.box(300, 778, 220, 60, "[I] XLR MASTER L/R", ["bilanciato, +24 dBu, sul retro"], "dark")
    d.arrow([(410, by), (410, D.y - 2)])
    chain_v(d, [D, E, F, G, H, I])
    V = d.box(40, 290, 200, 76, "[V] VIE_TAP", ["driver ≤ 50 Ω, 0 dBu nom", "→ b31-b32: uscite per via", "(modulo opzionale, 111b)"],
              tsize=12, lsize=10)
    d.arrow([(D.x, V.cy), (V.x + V.w + 2, V.cy)])
    d.text(286, 404, "dominio ±18 V:", 10, AUDIO, "end")
    d.text(286, 418, "+23 dBu max (K4)", 10, AUDIO, "end")
    d.text(286, 604, "+24 dBu reali SOLO qui", 10, AUDIO, "end")
    d.text(286, 618, "statici [M] (dec. 93)", 10, AUDIO, "end")
    # booth
    B = d.box(560, 262, 210, 60, "[B] BOOTH BUFFER × 2", ["±18 V"])
    B2 = d.box(560, 346, 210, 66, "[B2] BOOTH LEVEL", ["VCA V2181L (L/R), una CV", "−∞ → 0 dB, curva del fader"])
    B3 = d.box(560, 436, 210, 60, "[B3] BOOTH DRIVER × 2", ["±18 V"])
    B4 = d.box(560, 520, 210, 60, "[B4] BOOTH MUTE", ["comandato da [L]"])
    B5 = d.box(560, 604, 210, 60, "[B5] USCITA BOOTH", ["XLR, sul retro (dec. 141)"], "dark", lsize=10)
    d.arrow([(B.cx, by), (B.cx, B.y - 2)])
    chain_v(d, [B, B2, B3, B4, B5])
    # rec
    C = d.box(810, 262, 210, 60, "[C] REC BUFFER × 2", ["±15 V LN (decisione 63)"])
    C2 = d.box(810, 346, 210, 66, "[C2] PAD DEL REC", ["0 / −10 / −20 dB a ponticello", "partitore di precisione (dec. 63)"])
    C3 = d.box(810, 436, 210, 60, "[C3] REC MUTE", ["comandato da [L]"])
    C4 = d.box(810, 520, 210, 60, "[C4] USCITA REC", ["TRS, sul retro (dec. 141)"], "dark")
    d.arrow([(C.cx, by), (C.cx, C.y - 2)])
    chain_v(d, [C, C2, C3, C4])
    # mon
    N = d.box(1060, 262, 210, 84, "[N] MON BUFFER × 2",
              ["OPA1612 unity non invertente", "uscita ≤ 50 Ω", "→ modulo CUE"], "std")
    NO = d.box(1060, 370, 210, 70, "→ BACKPLANE slot 8", ["MON out L/R → modulo CUE", "non passa da [L]: cuffia sempre viva"], "dark", lsize=10)
    d.arrow([(N.cx, by), (N.cx, N.y - 2)])
    chain_v(d, [N, NO])
    # mute controller + psu
    L = d.box(1310, 470, 215, 110, "[L] MUTE CONTROLLER",
              ["supervisore rail + timer", "accensione 1,61-1,97 s", "GLOBAL_MUTE alta in < 0,07 ms"], "ctrl", tsize=12, lsize=10)
    d.arrow([(L.x, 490), (C3.x + C3.w + 2, 490)], "cv")
    d.text(1040, 484, "mute → [C3]", 10, CV)
    busy = 720
    d.arrow([(L.x, 560), (1290, 560), (1290, busy), (H.x + H.w + 2, busy)], "cv")
    d.arrow([(790, busy), (790, B4.cy), (B4.x + B4.w + 2, B4.cy)], "cv")
    d.text(620, busy - 8, "mute → [H]", 10, CV)
    d.text(798, 640, "mute → [B4]", 10, CV)
    GMU = d.box(1310, 612, 215, 70, "GLOBAL_MUTE (c9)",
                ["basso = suona · alto = muto", "relè dei moduli + mandate FX"], "dark", tsize=12, lsize=10)
    d.arrow([L.b, (GMU.cx, GMU.y - 2)], "cv")
    d.box(1310, 110, 215, 270, "[M] PSU LOCALE",
          ["raw [M] dal W3 (dec. 93)", "non regolato nel box", "→ statici 23,3…30,3 V", "   stadio HV [G]",
           "→ ±18 V LM317/337", "   front / VCA / booth", "→ ±15 V LT3045/94", "   summing, meter, REC",
           "+5 V control dal bus", "   LED, relè, logica mute"], "note", align="start", lsize=10.5)
    d.box(560, 744, 730, 96, "SCHEDE (dec. 142-143, pcb/master/NOTE.md)",
          ["segnale col C96: [A2] [A3] INS [A] [B] [C] [N] [D] [B2] [V] e detector [E]",
           "uscita L e uscita R col loro C96 (3 slot): [F]+[G], [B3], relè, [L], [M]",
           "+ scheda comandi dietro il pannello + scheda connettori sul retro · PCB: tutte PASSA"],
          "note", align="start", lsize=10.5, tsize=12)
    d.legend(892, [("audio", "audio"), ("cv", "controllo / mute"), (INK, "connettore / backplane")])
    d.footer("Fonte: docs/fase1/master-out.md v0.2 + ADDENDA (REC dec. 63, bootstrap dec. 86, [N] MON, dec. 111 MONO/INS/VIE_TAP, schede dec. 140-143) + sim/master-out/RISULTATI-mono-ms-comp.md + RISULTATI-mute-ctrl.md + dec. 139")
    return d.save()


# ---------------------------------------------------------------- 5-WAY
def five_way():
    d = Diagram("five-way", 1560, 1460, "MODULO 5-WAY — DUB PREAMP",
                "maelcum mixer — design v0.3 · kill a switch tagliato allo zero (dec. 164) · GROWL e NASTRO a bande (dec. 165-166) · ordine BLOCCATO: kill → EQ → drive → meter",
                "drive a bande PROVVISORIO", AMBER)
    x, w = 40, 340
    BUSI = d.box(x, 100, w, 60, "DJ BUS L/R (dal backplane)", ["0 dBu nom · worst +12 dBu (4 × correlati)"], "dark")
    PAD = d.box(x, 190, w, 66, "RICEVITORE + PAD −6 dB", ["massa virtuale del DJ bus (inverte, sistema-polarita)",
                                                         "riferimento interno −6 dBu (dec. 73)"])
    KB = d.box(x, 286, w, 320, "KILL BANK (per lato)",
               ["LR4 5 vie ALLINEATA IN FASE:", "somma piatta −0,004…−0,011 dB",
                "incroci E 80 / 170 / 1,2k / 6k Hz (dec. 150)", "",
                "SUB ── inv ── [switch K1]", "KICK ──────── [switch K2]", "MID ── inv ── [switch K3]",
                "HIGH ──────── [switch K4]", "SUPER ─────── [switch K5]", "",
                "gate = switch π SPDT ADG1434 (dec. 88)", "!taglia e riapre allo zero della via (164)",
                "2 invertitori unity (SUB/MID) per la polarità", "ALL-KILL = silenzio assoluto"], lsize=10)
    EQ = d.box(x, 636, w, 150, "EQ CREATIVO — 5 CELLE v0.2.1",
               ["parametriche SVF in serie (dettaglio a destra)", "gain −∞…0…+15/12/9 dB · WIDTH Q3…Q0,3 (dec. 117)",
                "position 2,6 ottave/banda · 5 pot rotativi (dec. 85)",
                "le 5 bande EQ NON sono le 5 vie", "range 20-120 / 80-400 / 250-1,5k / 800-5k / 3-20k"], "green", lsize=10)
    DR = d.box(x, 816, w, 130, "DRIVE: GROWL + NASTRO A BANDE",
               ["due blend in serie sul pulito (dec. 99)", "!circuito a bande: dec. 165-166 [PROVVISORIO]",
                "niente VCA: pot doppi sul segnale", "dettaglio in alto a destra"], "green")
    ME = d.box(x, 976, w, 60, "METER pickup", ["detector condiviso · release ~0,3 s (dec. 81)"])
    MU = d.box(x, 1066, w, 60, "MAKE-UP +6 dB + TRIM", ["servo DC (§5bis.7) · uscita 0 dBu nominale"])
    OUT = d.box(x, 1156, w, 56, "→ MASTER SUM (MSUM1, backplane)", [], "dark", tsize=12.5)
    chain_v(d, [BUSI, PAD, KB, EQ, DR, ME, MU, OUT])
    # zoom drive
    zx = 420
    d.raw(f'  <rect x="{zx}" y="100" width="1100" height="320" rx="10" fill="#fff" stroke="{GREEN}" stroke-width="1.5"/>')
    d.text(zx + 30, 134, "ZOOM — DRIVE A BANDE: GROWL + NASTRO (five-way §5bis REV 2026-11-03, per lato)", 16, GREEN, weight=700)
    d.text(zx + 30, 154, "ogni manopola dosa il segnale «differenza» (saturato meno pulito): a manopola chiusa l'uscita è l'ingresso esatto", 11.5, "#666")
    X = d.box(zx + 30, 176, 150, 128, "SOMMA EQ", ["−6 dBu nominale", "percorso pulito", "DC-coupled"], tsize=12, lsize=10)
    G = d.box(zx + 210, 176, 300, 128, "GROWL A BANDE (dec. 165)",
              ["basso: LP Butterworth 4 poli a 250 Hz", "→ clipper Rf 47k, 1 / 3 diodi + 470 Ω",
               "medi: banda fino al polo a 2,5 kHz", "→ clipper morbido 3 + 3 diodi + 4,7k",
               "alti sopra 2,5 kHz puliti", "una manopola: miscela + spinta (0 → +20 dB)"], "amber", tsize=12, lsize=10)
    T = d.box(zx + 540, 176, 290, 128, "NASTRO A BANDE (dec. 166)",
              ["JFET + spinta +12 dB (NASTRO LIBERO)", "enfasi: 2 × zero 80 / polo 400 Hz",
               "(taglia i bassi) e 2 × polo 5k / zero 10k", "(taglia i super) davanti al JFET",
               "de-enfasi inversa dopo il JFET", "a piccolo segnale il ramo è piatto"], "amber", tsize=12, lsize=10)
    O = d.box(zx + 860, 176, 210, 128, "→ METER → MAKE-UP",
              ["fine corsa, mix 0 dBu:", "GROWL: SUB 28 % · KICK 42 %", "500 Hz 23 % · 1 kHz 6 %",
               "NASTRO: SUB 1,6 % · KICK 2,8 %", "MID 30 % · HIGH 36 % · SUPER 26 %"], tsize=12, lsize=10)
    chain_h(d, [X, G, T, O])
    d.box(zx + 30, 322, 1040, 80, "",
          ["Insieme a fine corsa sub e kick arrivano al 52 % e al 77 % sul mix: gesto estremo accettato (dec. 166e).",
           "LTspice = modello di MC-5WAY entro 0,03 punti (todo 234). Rumore del modulo a fine corsa: GROWL −78,2, NASTRO −79,1,",
           "insieme −71,1 dBu A-wtd; a metà corsa −85,5 / −85,6; manopole chiuse −85,9 (docs/06 §10). Da sentire in MC-5WAY."],
          "note", align="start", lsize=10.5)
    # zoom kill
    d.raw(f'  <rect x="{zx}" y="440" width="1100" height="196" rx="10" fill="#fff" stroke="{CV}" stroke-width="1.5"/>')
    d.text(zx + 30, 474, "ZOOM — KILL A SWITCH TAGLIATO ALLO ZERO (dec. 88, 164; §8.10-8.11)", 16, CV, weight=700)
    K1 = d.box(zx + 30, 494, 220, 124, "KILL A LEVETTA (dec. 121)", ["ON-OFF-(ON): su fisso, giù a molla", "OR dei 2 contatti",
                                                             "→ 74HC74: copia la levetta", "al fronte del comparatore",
                                                             "(isteresi pochi mV, max ~20 ms)"], "ctrl", tsize=12, lsize=10)
    K2 = d.box(zx + 290, 494, 250, 124, "π SPDT classe ADG1434",
               ["serie + shunt a GND da off", "Ron 4,7 Ω · rail ±15 V dedicato", "off-isolation −95 dB a 20 kHz",
                "L e R tagliano al proprio zero", "3 comparatori quad + 5 doppi 74HC74"], tsize=12, lsize=10)
    d.arrow([K1.r, (K2.x - 2, K2.cy)], "cv")
    d.box(zx + 580, 494, 490, 124, "COSA CAMBIA ALL'ASCOLTO",
          ["Taglio netto, senza dissolvenza, ma senza scoppio nelle trombe.",
           "Gradino da −92 dB (SUB) a −44 dB (SUPER) rispetto al secco.",
           "Il kill aspetta lo zero: al massimo SUB 13,5 ms, KICK 6,3 ms,",
           "MID 2,9 ms, HIGH e SUPER sotto 0,5 ms. Nessun VCA, fruscio invariato.",
           "!Da sentire nel prototipo MC-5WAY [PROVVISORIO]."],
          "note", align="start", lsize=10.5, tsize=12)
    # zoom cella (frammento a mano, traslato)
    fname = "cella-v021.frag" if LANG == "it" else "cella-v021-en.frag"
    frag = open(os.path.join(HERE, fname), encoding="utf-8").read()
    d.raw(f'  <g transform="translate(0,546)">\n{frag}\n  </g>')
    d.box(zx, 1236, 1100, 84, "",
          ["Perché non gli OTA LM13700 nelle celle: tetto di stato strutturale 52 mV a f0 → la cella nuda collassava (THD 3-6 %).",
           "Il JFET VCR è un resistore controllato: core a −12 dBu locale, THD 0,005 % nominale / 0,125 % worst — morbida, territorio drive.",
           "Silicio THAT 218x / V2181L nel modulo: nessuno (kill a switch, drive a pot). I numeri di rumore per cella con INTEG sono invalidati."],
          "note", align="start", lsize=11)
    d.legend(1360, [("audio", "audio"), ("cv", "controllo (position/width/kill)"), (FB, "nota evidenziata")])
    d.footer("Fonte: docs/fase2/five-way-module.md (§2, §4.2-4.3, §5bis REV 2026-11-03, §8.10-8.11) + proto-max/RISULTATI-P2.md §12-14 + sim/five-way/RISULTATI-kill-zc.md + decisioni 88/117/150/164/165/166")
    return d.save()


# ---------------------------------------------------------------- FILTRO
def filtro():
    d = Diagram("filtro", 1560, 940, "MODULO FILTRO GLOBALE",
                "maelcum mixer — design v0.2 + D5 · dopo il fader, sui bus HPF e LPF: 4 core mono (dec. 159) · HPF 20 Hz–35 kHz, LPF 10 Hz–35 kHz (dec. 137)",
                "core (a′) Butterworth 4 poli (dec. 148)", GREEN)
    y = 120
    IN = d.box(40, y, 200, 86, "DAL BACKPLANE", ["bus HPF e bus LPF (net)", "= somma dei canali assegnati,",
                                              "dopo il fader (dec. 159)"], "dark")
    BI = d.box(285, y, 150, 86, "RICEVITORI", ["2 bus stereo", "virtual-earth Rf 10k", "(inverte)"])
    CO = d.box(480, y - 20, 330, 126, "CORE SVF 4 POLI × 4 (mono)",
               ["2 sezioni (a′): Q 0,541 + Q 1,307 (Butterworth)", "!OTA LM13700 + partitore 1/30 (dec. 109, 148)",
                "C integratori 1,1 nF · uscita max +2,9 dBu", "(c-B) pulito: progettato e archiviato (dec. 148)"], lsize=10)
    DV = d.box(855, y - 20, 270, 126, "OVERDRIVE v0.2 (§5ter)",
               ["tosatore 2,2k + 2+2 diodi, blend sul pulito", "DRIVE: pot doppio lineare, m = θ (dec. 155a)",
                "niente VCA (todo 212) · servo DC", "esce invertito: rimedio polarità F1"], "green", lsize=10)
    MX = d.box(1170, y, 180, 86, "MUTO DI SEZIONE", ["tace se nessun canale", "la sceglie", "(bit FILT_MODE, dec. 159)"])
    RE = d.box(1395, y, 125, 86, "USCITA", ["2 uscite", "→ DJ bus (R 10k)"])
    chain_h(d, [IN, BI, CO, DV, MX, RE])
    d.text(1457, y + 104, "max +2,9 dBu (core)", 10.5, AUDIO, "middle")
    RS = d.box(565, 262, 440, 140, "RISONANZA dec. 153 (§5, todo 212)",
               ["gres = gpos − gneg: due OTA, metà dello stesso LM13700",
                "pot RES lineare cablato rovescio → shaper a diodi → OTA che smorza",
                "!sopra il 90 %: raddrizzatore di precisione → OTA che innesca",
                "Q da 1× a 8× la base fino al 90 %, fischio dal 93,4 %",
                "fischio col chip vero: +0,2…+0,5 dBu, −2,1…−2,4 semitoni",
                "limitatore: 4,7k + 2+2 1N4148 verso il summer"], "purple", lsize=10)
    d.arrow([(700, RS.y), (700, CO.y + CO.h + 2)], "fb")
    d.box(1035, 262, 485, 126, "SOMMA DEI CANALI (todo 215, RISULTATI-D5 §7)",
          ["Ricevitore a guadagno 1 per canale: 2 correlati +6, 4 correlati +12 dBu.",
           "In banda la somma passa senza perdite fino a +12 dBu.",
           "Sul taglio il core ha un tetto fra −1 e +1,2 dBu: con 2 canali correlati",
           "!la risonanza sul programma sparisce: da sentire (docs/02 A23).",
           "DRIVE a fine corsa: 19 / 29 / 34 % a 0 / +6 / +12 dBu (dec. 159d)."],
          "note", align="start", lsize=10.5, tsize=12)
    # sezione controllo
    d.raw(f'  <rect x="40" y="420" width="1480" height="304" rx="10" fill="#EEF3F6" stroke="{CV}" stroke-width="1.2"/>')
    d.text(66, 452, "SEZIONE CONTROLLO — 6 manopole: FREQ, RES, DRIVE per la sezione HPF e per la LPF", 15, CV, weight=700)
    cy = 476
    b1 = d.box(66, cy, 225, 90, "LAW SHAPER", ["law Xone:96 (dec. 102)", "HPF 20 Hz · 1000^(θ/0,95) (137)",
                                              "LPF 10 Hz–35 kHz"], tsize=12, lsize=10)
    b2 = d.box(336, cy, 235, 90, "CONVERTER EXPO", ["coppia BJT matched, ΔVbe PTAT:", "Iabc 114 nA…397 µA = 10,6 Hz…37 kHz",
                                                 "deriva ≤ 2,4 % (0-50 °C)"], tsize=12, lsize=10)
    b3 = d.box(616, cy, 235, 90, "DISTRIBUZIONE", ["mirror bufferizzati + trim/core", "2 rami per sezione (dec. 159)",
                                                "tracking ≤ 1,6 % PASS"], tsize=12, lsize=10)
    b4 = d.box(906, cy, 270, 90, "RES: SHAPER + RADDRIZZATORE", ["pot lineare rovescio, +5 V di riferimento",
                                                              "soglia del fischio = rapporto di R", "da 20 a 50 °C: ≤ 1,6 %"], tsize=12, lsize=10)
    b5 = d.box(1221, cy, 273, 90, "DRIVE A POT DOPPIO", ["una manopola = una coppia di celle", "m = θ esatto, senza shaper",
                                                      "22 µF: niente continua sul pot"], tsize=12, lsize=10)
    chain_h(d, [b1, b2, b3], "cv")
    d.arrow([(b3.cx, cy), (b3.cx, 412), (530, 412), (530, CO.y + CO.h + 2)], "cv")
    d.text(520, 300, "Iabc →", 10, CV, "end")
    d.text(520, 314, "integratori", 10, CV, "end")
    d.box(66, 586, 1428, 118, "VERIFICATO COL MODELLO REALE DELL'LM13700",
          ["Core (a) nudo SCARTATO: picco di risonanza sotto −12 dBu, programma 0 dBu −23 dB sul taglio, oscillazione 3,5 ottave sotto FREQ.",
           "Core (a′) 1/30: piccolo segnale esatto · risonanza piena a −30 dBu · THD core 1,5-2 % a 0 dBu · offset ×30 dentro la corsa del servo.",
           "Rumore del sistema a DRIVE chiuso: −78,0 dBu A con HPF e LPF in uso, −79,2 solo HPF, −80,6 solo LPF (docs/06 §16): entro il −78.",
           "DRIVE aperto: −72,0 con le due sezioni, nella condizione d'uso accettata (dec. 100). Il FAIL dei 4 core in serie (A18) sparisce."],
          "green", align="start", lsize=10.5, tsize=12)
    d.box(40, 744, 900, 66, "",
          ["RAIL: tutti gli OTA su ±15,0 V ultra-low-noise dal ±19 V LN (pre-reg ±16,5 → LT3045/94) — LM13700 assoluto ±18",
           "BOM: 12 LM13700 (8 core + 4 RES) · ~12 quad · C 1,1 nF C0G/PP matched · 0 VCA (DRIVE a pot) · ~450 componenti [STIMA]"],
          "note", align="start", lsize=10.5)
    d.box(980, 744, 540, 66, "",
          ["PROTOTIPO: MC-FILTRO-HPF e -LPF sulle tracce BUS (todo 216)",
           "valori dei componenti [PROVVISORIO] fino al banco"],
          "amber", align="start", lsize=10.5)
    d.legend(850, [("audio", "audio (bus → DJ bus)"), ("cv", "controllo CV / Iabc"),
                   ("fb", "risonanza / nota evidenziata")])
    d.footer("Fonte: docs/fase2/filter-module.md (§2bis, §4, §5 RES dec. 153, §5ter DRIVE a pot, §5quater) + sim/filtro/RISULTATI-D5.md §7 + docs/06 §16 + decisioni 102/109/137/148/153/155/159")
    return d.save()


# ---------------------------------------------------------------- CUE
def cue():
    d = Diagram("cue", 1560, 800, "MODULO CUE / CUFFIE",
                "maelcum mixer — design S5 v0.2 (ampli cuffia 2026-10-12, polarità REV 2026-11-03) · standard: classe cuffie Pioneer DJM (dec. 96) · metà L; R identica",
                "S5 v0.2", GREEN)
    CI = d.box(40, 130, 200, 84, "CUE 1-4 L/R", ["dai canali DJ, slot 1-4", "post-EQ, pre-filtro, pre-fader"], "dark")
    MI = d.box(40, 290, 200, 84, "MON IN L/R", ["dal master, buffer [N], slot 5", "post-summing, pre-master-level"], "dark")
    A = d.box(290, 130, 215, 84, "[A] CUE SUMMING", ["massa virtuale, Rf 10k, guadagno −1", "più cue attivi = sommati"])
    Bm = d.box(290, 290, 215, 84, "[B] MON BUFFER", ["!invertente 20k/20k 0,1 % (todo 227)", "carico per [N] ≤ 50 Ω [PROVV]"])
    C = d.box(560, 200, 200, 104, "[C] BLEND CUE ↔ MASTER",
              ["pot doppio 10k lineare", "CCW = cue · CW = master", "centro = 50/50 (−6 / −6 dB)"], tsize=12)
    Dv = d.box(810, 212, 160, 80, "[D] LEVEL", ["pot doppio 10k log", "CCW = silenzio vero"])
    E = d.box(1020, 150, 250, 204, "[E] AMPLI CUFFIA v0.2",
              ["OP1612 gain +1, Rf 470 Ω + Cf 330 pF", "Rdrv 1 kΩ verso la rete di bias", "Vbe-multiplier + trimmer: idle 20 mA",
               "finali MJE340/350, Re 6,8 Ω", "limitatori: 126-142 mA (corto 168)", "THD 1 Vrms: 0,005 % su 16 Ω",
               "max su 32 Ω: 2,85 Vrms = 254 mW", "rail ±18 V locali (non sul LN)"], "green", lsize=10.5)
    Fo = d.box(1320, 190, 200, 124, "[F] USCITE", ["Rserie 10 Ω × 4 (fuori anello)", "relè DPDT × 2",
                                                 "a riposo = cuffia muta", "→ 2 jack stereo 6,3 mm (128)"], "dark")
    d.arrow([CI.r, (A.x - 2, A.cy)])
    d.arrow([MI.r, (Bm.x - 2, Bm.cy)])
    d.arrow([A.r, (530, A.cy), (530, 232), (C.x - 2, 232)])
    d.arrow([Bm.r, (530, Bm.cy), (530, 272), (C.x - 2, 272)])
    chain_h(d, [C, Dv, E, Fo])
    d.text(1145, 372, "stesso mix su entrambe le uscite", 10.5, "#777", "middle")
    Gc = d.box(1320, 400, 200, 110, "[G] CONTROLLO LOCALE",
               ["supervisore rail + timer 1,5-2 s", "power-off: relè aperti < 10 ms", "analogico, niente MCU"], "ctrl", tsize=12, lsize=10)
    d.arrow([Gc.t, (Fo.cx, Fo.y + Fo.h + 2)], "cv")
    d.box(40, 430, 620, 130, "POLARITÀ E FASE DEL BLEND",
          ["!REV todo 227: il canale arriva a [A2] già rovesciato dal ricevitore del DJ bus;",
           "!con MON diritto il centro del blend cancellava: buffer [B] invertente.",
           "Fase: il master attraversa la banca 5-way (ritardi fino a ~2,5 ms), il cue no.",
           "Cue di un canale già in programma, al centro del blend = comb filtering: accettato."],
          "note", align="start", lsize=10.5)
    d.box(700, 430, 580, 130, "GLOBAL_MUTE: IL CUE NON LO ASCOLTA",
          ["Scelta di Filippo (2026-10-02): durante power-on/off e guasti rail del master",
           "la cuffia resta viva: si continua a preascoltare anche se il master è muto.",
           "I transienti PROPRI del modulo li toglie [G] con i relè d'uscita.",
           "Il blend non segue la manopola master (stile DJM-900NXS2)."],
          "note", align="start", lsize=10.5)
    d.box(40, 590, 1480, 84, "PSU LOCALE + NUMERI",
          ["±19 V LN dal box → pre-reg ±16,5 → LT3045/94 → ±15,0 V LN per [A][B][C][D] · ±22,0 V audio → LM317/337 → ±18 V per [E] (~61 mA a riposo, ≤ ~340 mA col clamp) · +5 V dal bus per [G]",
           "Rumore al jack −114,5 dBu A-wtd (target −90) · isolamento blend agli estremi −116 dB · stabilità: nessun picco ad anello chiuso, quadra pulita fino a 2 nF di cavo"],
          "note", align="start", lsize=10.5)
    d.legend(716, [("audio", "audio"), ("cv", "controllo locale"), (FB, "nota evidenziata")])
    d.footer("Fonte: docs/fase3/sistema-cue.md v0.2 (§2-§9, §7 REV 2026-11-03) + sistema-polarita.md F4 + sim/system/RISULTATI-cue.md + master-out.md ADDENDUM [N] + decisioni 96/128")
    return d.save()


# ---------------------------------------------------------------- MIC / MONO
def mic_mono():
    d = Diagram("mic-mono", 1720, 960, "MODULI MIC e MONO — due moduli separati",
                "maelcum mixer — architettura v0.1 + REV 2026-11-04 · comandi: GAIN, EQ 2 bande, 4 pot send, 1 LED; sul MIC anche il tasto MUTE (dec. 97, 111, 167) · massimo 4 moduli",
                "MUTE a ritenuta (dec. 167)", GREEN)

    def banda(y, etichetta, front, msum, mute):
        d.text(40, y - 12, etichetta, 12, "#666", weight=700)
        bx = [d.box(40 + k * 210, y, 175, 96, t, ln, kind) for k, (t, ln, kind) in enumerate(front)]
        chain_h(d, bx)
        cy = bx[0].cy
        EQ = d.box(695, y, 190, 96, "EQ 2 BANDE", ["LOW shelf ~120 Hz", "HIGH ~5 kHz", "−∞ → 0 → +6 (celle serie)"])
        d.arrow([bx[-1].r, (EQ.x - 2, cy)])
        d.dot(665, cy)
        LED = d.box(530, y + 126, 250, 88, "LED (uno, cambia colore)",
                    ["presa pre-EQ [BLOCCATO]", "verde ≥ −6 · giallo ≥ +11 dBu", "rosso = clip ≥ +17 (latch) [PROVV]"], "ctrl", tsize=12)
        d.arrow([(665, cy), (665, LED.y - 2)], "cv")
        if mute:
            MU = d.box(915, y, 230, 96, "MUTE + LIMITER", ["VCA V2181L mono, rampa 1 ms", "tasto a ritenuta (dec. 167)",
                                                       "limiter fisso +12 dBu (dec. 145)", "rilascio 1 s, nessun comando"],
                       "amber", tsize=12, lsize=10)
            d.arrow([EQ.r, (MU.x - 2, cy)])
            d.arrow([MU.r, (1173, cy)], head=False)
        else:
            d.arrow([EQ.r, (1173, cy)], head=False)
            d.text(1030, cy - 8, "(niente MUTE)", 10, "#777", "middle")
        d.dot(1175, cy)
        DR = d.box(1205, y, 180, 96, "DRIVER L + DRIVER R", ["invertenti 20k/20k (todo 227)", "due buffer separati", "mai hard-short L/R"])
        MS = d.box(1415, y, 170, 96, "→ MASTER SUM", [msum, "multidrop, 7 contributori"], "dark")
        d.arrow([(1175, cy), (DR.x - 2, cy)])
        d.arrow([DR.r, (MS.x - 2, cy)])
        AS = d.box(1205, y + 126, 180, 88, "SEND × 4 (pot)", ["uno per bus FX, −∞ … 0 dB", "presa post-EQ" + (" e post-MUTE" if mute else ""),
                                                          "2k2 → ADG1434"])
        INJ = d.box(1415, y + 126, 140, 88, "INIEZIONE × 4", ["OPA1654 quad", "2 × R 10k", "(net L e R)"])
        BUS = d.box(1580, y + 126, 120, 88, "→ BUS FX 1-4", ["net multidrop", "slot 2-5"], "dark")
        d.arrow([(1175, cy), (1175, AS.cy), (AS.x - 2, AS.cy)])
        chain_h(d, [AS, INJ, BUS])
        GM = d.box(820, y + 126, 230, 88, "GLOBAL_MUTE (c9)", ["ADG1434 sulle mandate", "a power-on/off (dec. 94b)", "non è un comando di pannello"], "ctrl", tsize=12)
        d.arrow([GM.b, (GM.cx, y + 230), (AS.x + 30, y + 230), (AS.x + 30, AS.y + AS.h + 2)], "cv")

    banda(140, "MODULO MIC — front-end su ±15 V LN",
          [("XLR + PROTEZIONE", ["bilanciato, NO phantom", "RFI, R 10 + clamp ai rail", "Zin 2,26k · CM 47k/gamba"], "dark"),
           ("INA +30 dB FISSO", ["coppia OPA1612", "Rf 2×499 · Rg 32,4", "+ passa-alto 60 Hz (dec. 97)"], "std"),
           ("GAIN 0 … +30 dB", ["OPA1654, pot 5k", "totale 29,5 … 59,3 dB", "curva inversa C (129 E2)"], "std")],
          "net MSUM6", True)
    banda(436, "MODULO MONO — dominio ±18 V",
          [("JACK + PROTEZIONE", ["mono, tollera +18 dBu", "R 1k + clamp + TVS", "C film 100 nF (1,6 Hz)"], "dark"),
           ("BUFFER FET", ["OPA1654 unity", "Zin 1 MΩ"], "std"),
           ("GAIN −∞ → 0 → +10", ["pot 10k passivo", "+ make-up +10 dB"], "std")],
          "net MSUM7", False)
    d.box(40, 712, 800, 150, "NUMERI SIMULATI (sim/mic/)",
          ["MIC: EIN −126,5 dBu su 150 Ω, uguale a ogni posizione del GAIN · passa-alto −3,1 dB a 60 Hz",
           "MIC: CMRR 74 dB con sorgente sbilanciata di 10 Ω · overload 300 mV rms al microfono",
           "MIC: uscita modulo −97,3 / −90,0 / −69,3 dBu A-wtd a 30 / 38 / 59 dB di gain",
           "MIC limiter (variante 2): un grido a +20 dBu esce a +12,8 dBu, attacco ~2 ms",
           "MONO: banda −0,19 dB a 10 Hz, −0,08 a 35 kHz · uscita −101,3 dBu A-wtd",
           "Mandate: pot chiuso −111,2 dBu A-wtd sul bus · mute globale −53 dB col pot aperto"],
          "note", align="start", lsize=10.5)
    d.box(870, 712, 830, 150, "DECISIONI 97, 111, 145, 167 E APERTI",
          ["Due moduli separati: GAIN, EQ 2 bande, 4 pot send, 1 LED; sul MIC anche il tasto MUTE.",
           "Massimo 4 moduli MIC/MONO: i bus FX arrivano a 12 contributori (caso già verificato).",
           "MUTE a ritenuta (dec. 167) · limiter fisso nel VCA del MUTE, solo sul MIC (dec. 145) [PROVV].",
           "Schema: SCHEMA PASSA per MIC e MONO; PCB del MIC PASSA, al limite (pcb/mic/NOTE.md).",
           "!Aperto: soglie del LED (−6 / +11 / +17 dBu, sistema-metering §1)",
           "!Aperto: HIGH dell'EQ2 ~5 kHz (§5.1) o ~4,5 kHz come il FX-SEND"],
          "note", align="start", lsize=10.5)
    d.legend(898, [("audio", "audio"), ("cv", "controllo / LED / mute")])
    d.footer("Fonte: docs/fase4/mic-mono-moduli.md v0.1 + REV dec. 111 / 145 / 2026-11-04 + sim/mic/RISULTATI-mic-mono.md + RISULTATI-mic-limiter.md + sistema-polarita.md F2 + decisioni 97/111/145/167")
    return d.save()


# ---------------------------------------------------------------- SCHEMA TOTALE
def schema_totale():
    d = Diagram("schema-totale", 1720, 1600, "SCHEMA FUNZIONALE TOTALE",
                "maelcum mixer — percorso del segnale da tutti gli ingressi a tutte le uscite · stato decisioni 1-168 · un canale DJ e un bus FX disegnati, gli altri identici",
                "decisioni 1-168", FB)
    g, p = "jgreen", "jgrey"

    def bx(x, y, w, h, t, lines=(), kind=g, ts=12.5, ls=10.5):
        return d.box(x, y, w, h, t, lines, kind, tsize=ts, lsize=ls)

    K = "k"
    # ===================== CANALE DJ (colonna sinistra)
    d.text(40, 112, "CANALE DJ 1 (2, 3, 4 identici)", 13, INK, weight=700)
    LN = d.circle(110, 175, 46, ["LINE", "RCA"])
    PH = d.circle(250, 175, 46, ["PHONO", "MM"])
    PP = bx(185, 250, 130, 50, "phono preamp", ["RIAA 42 dB · sub 18 Hz"], p, 11.5, 9.5)
    SEL = bx(55, 330, 220, 56, "levetta line/phono")
    d.arrow([LN.b, (110, SEL.y - 2)], K)
    d.arrow([PH.b, (PP.cx, PP.y - 2)], K)
    d.arrow([PP.b, (PP.cx, SEL.y - 2)], K)
    GA = bx(55, 416, 220, 56, "GAIN (pot doppio)", ["−∞ … 0 … +10 dB"])
    EQ = bx(55, 502, 220, 70, "EQ ISOLATOR 4 bande", ["incroci 150 / 350 / 3150 Hz", "−48 … 0 … +6 dB (pot lineare)"])
    chain = [SEL, GA, EQ]
    for a, b in zip(chain, chain[1:]):
        d.arrow([a.b, (b.cx, b.y - 2)], K)
    sx, sy = 165, 610                       # nodo split post-EQ
    d.arrow([EQ.b, (sx, sy)], K, head=False)
    d.o.append(f'  <circle cx="{sx}" cy="{sy}" r="4.5" fill="#333"/>')
    ME = bx(55, 650, 220, 46, "meter DJ", ["pre-fader"], p, 12, 10)
    d.arrow([(sx, sy), (sx, ME.y - 2)], K)
    FA = bx(55, 726, 220, 56, "FADER → 2 VCA", ["−∞ … 0 dB"])
    DO = bx(55, 812, 220, 46, "driver d'uscita", [], p, 12)
    FS = bx(55, 888, 220, 56, "levetta HPF / OFF / LPF", ["dip del VCA del fader (163)"])
    for a, b in zip([ME, FA, DO], [FA, DO, FS]):
        d.arrow([a.b, (b.cx, b.y - 2)], K)
    FI = bx(330, 850, 230, 96, "MODULO FILTRO", ["4 core OTA (a′) 4 poli", "FREQ · RES · DRIVE × 2 sezioni",
                                                  "sui bus HPF e LPF"], ts=13)
    d.arrow([(FS.x + FS.w, 905), (FI.x - 2, 905)], K)
    d.text(302, 899, "bus", 9.5, "#555", "middle")
    d.arrow([(FI.cx, FI.y + FI.h), (FI.cx, 996), (277, 996)], K)
    d.text(FI.cx + 6, 975, "uscite HPF e LPF", 9.5, "#555")
    # cue e fx-send dal nodo split
    CU = bx(330, 470, 230, 56, "CUE (bottone con luce)", ["pre-fader, pre-filtro"], ts=12)
    FX = bx(330, 548, 230, 66, "MICRO-MODULO FX-SEND", ["EQ2 · LEVEL · assign S1-S4"], ts=12)
    d.arrow([(sx, sy), (300, sy), (300, CU.cy), (CU.x - 2, CU.cy)], K)
    d.arrow([(300, sy), (300, FX.cy), (FX.x - 2, FX.cy)], K)
    # DJ bus
    DJ = bx(55, 990, 220, 56, "DJ BUS", ["somma dei 4 canali"], p)
    d.arrow([FS.b, (DJ.cx, DJ.y - 2)], K)
    for i, yy in enumerate((1004, 1018, 1032)):
        d.arrow([(330, yy), (DJ.x + DJ.w + 2, yy)], K)
    d.text(338, 1022, "dai canali 2, 3, 4", 10, "#555")
    # 5-way
    FW = bx(55, 1080, 220, 120, "5-WAY dub preamp", ["kill × 5 vie (allo zero)", "EQ creativo 5 celle",
                                                    "GROWL + NASTRO a bande", "meter · make-up"], ts=13)
    d.arrow([DJ.b, (FW.cx, FW.y - 2)], K)
    # ===================== MIC / MONO
    d.text(660, 112, "MIC e MONO (fino a 4 moduli)", 13, INK, weight=700)
    MI = d.circle(720, 175, 46, ["MIC", "XLR"])
    MO = d.circle(880, 175, 46, ["MONO", "jack"])
    MIM = bx(650, 250, 140, 110, "MIC", ["gain +30…+59", "HPF 60 Hz · EQ2", "MUTE + limiter", "4 send"], ts=12.5, ls=10)
    MOM = bx(810, 250, 140, 110, "MONO", ["gain −∞…+10", "EQ2", "4 send"], ts=12.5, ls=10)
    d.arrow([MI.b, (MIM.cx, MIM.y - 2)], K)
    d.arrow([MO.b, (MOM.cx, MOM.y - 2)], K)
    # ===================== FX
    d.text(752, 576, "nel modulo FX-RET n (×4)", 10, "#555")
    FB_ = bx(650, 470, 190, 90, "BUS FX n (1 di 4)", ["somma: FX-SEND, mic,", "mono, reroute"], p)
    d.arrow([(FX.x + FX.w, FX.cy), (FB_.x - 2, FX.cy)], K)
    d.arrow([(MIM.cx, MIM.y + MIM.h), (MIM.cx, FB_.y - 2)], K)
    d.arrow([(MOM.cx, MOM.y + MOM.h), (MOM.cx, 440), (800, 440), (800, FB_.y - 2)], K)
    SE = d.circle(940, 515, 44, ["FX SEND", "n"], "out")
    d.arrow([FB_.r, (SE.x - 2, 515)], K)
    PE = bx(1010, 490, 120, 50, "PEDALE", ["esterno"], "jext", 12, 10)
    d.arrow([(SE.x + SE.w, 515), (PE.x - 2, 515)], K)
    RT = d.circle(1210, 515, 44, ["FX", "RETURN n"])
    d.arrow([PE.r, (RT.x - 2, 515)], K)
    RG = bx(1130, 600, 160, 66, "GAIN + EQ2", ["pot doppio, −∞…+20 dB"], ls=10)
    d.arrow([RT.b, (RG.cx, RG.y - 2)], K)
    RR = bx(1130, 696, 160, 76, "REROUTE × 4", ["3 cross + SELF, VCA", "pre-fader"], ts=12)
    d.arrow([RG.b, (RR.cx, RR.y - 2)], K)
    d.arrow([RR.l, (745, RR.cy), (745, FB_.y + FB_.h + 2)], "fb")
    d.text(760, RR.cy - 8, "feedback verso i 4 bus FX", 10, FB)
    RF = bx(1130, 802, 160, 56, "FADER → 2 VCA", [], ts=12)
    d.arrow([RR.b, (RF.cx, RF.y - 2)], K)
    # ===================== MASTER SUM
    MS = bx(55, 1250, 1300, 56, "MASTER SUM + MONO", ["7 ingressi: 5-way · 4 ritorni FX · mic · mono (dec. 94a) · tasto MONO M/S su tutte le uscite (dec. 111)"], p, 13)
    d.arrow([FW.b, (FW.cx, MS.y - 2)], K)
    d.arrow([RF.b, (RF.cx, MS.y - 2)], K)
    d.arrow([MIM.l, (620, MIM.cy), (620, MS.y - 2)], K)
    d.arrow([MOM.r, (997, MOM.cy), (997, MS.y - 2)], K)
    d.text(628, 1236, "mic", 9.5, "#555")
    d.text(1005, 1236, "mono", 9.5, "#555")
    # ===================== USCITE
    ML = bx(55, 1350, 200, 56, "MASTER LEVEL", ["−∞ … 0 (scatto) … +6 dB"], ls=10)
    BL = bx(300, 1350, 200, 56, "BOOTH LEVEL", ["−∞ … 0 dB"])
    RA = bx(545, 1350, 200, 56, "pad REC", ["0 / −10 / −20 dB"], p)
    MB = bx(790, 1350, 200, 56, "buffer MON", ["verso il CUE"], p)
    for b in (ML, BL, RA, MB):
        d.arrow([(b.cx, MS.y + MS.h), (b.cx, b.y - 2)], K)
    for b, lab in ((ML, ["MASTER", "XLR"]), (BL, ["BOOTH", "XLR"]), (RA, ["REC", "TRS"])):
        c = d.circle(b.cx, 1490, 44, lab, "out")
        d.arrow([b.b, (b.cx, c.y - 2)], K)
    # ===================== CUE
    d.text(1400, 1110, "CUE / CUFFIE", 13, INK, weight=700)
    CB = bx(1400, 1130, 260, 56, "somma CUE", ["cue dei 4 canali"], p)
    d.arrow([CU.r, (592, CU.cy), (592, 1215), (1370, 1215), (1370, CB.cy), (CB.x - 2, CB.cy)], K)
    d.text(1360, 1207, "cue dei canali", 9.5, "#555", "end")
    BLD = bx(1400, 1350, 260, 66, "BLEND cue ↔ master + LEVEL", ["pot doppio + pot level"], ts=12)
    d.arrow([CB.b, (CB.cx, BLD.y - 2)], K)
    d.arrow([MB.r, (BLD.x - 2, MB.cy)], K)
    AH = bx(1400, 1440, 260, 46, "ampli cuffia", [], p, 12)
    d.arrow([BLD.b, (AH.cx, AH.y - 2)], K)
    HP = d.circle(1530, 1545, 40, ["CUFFIE", "2 jack"], "out", 11)
    d.arrow([AH.b, (1530, HP.y - 2)], K)
    # ===================== LEGENDA
    d.box(1330, 100, 350, 300, "", [], "jleg")
    d.o.append('  <rect x="1350" y="116" width="110" height="28" rx="4" fill="#B4A7D6"/>')
    d.text(1405, 136, "Legenda", 14, "#1A1A1A", "middle", 700)
    d.circle(1395, 205, 38, ["ingresso"], "in", 11)
    d.circle(1505, 205, 38, ["uscita"], "out", 11)
    d.box(1565, 172, 100, 66, "", ["modulo con", "comandi"], g, lsize=10.5)
    d.box(1360, 270, 100, 56, "", ["passivo", "(senza comandi)"], p, lsize=10)
    d.box(1480, 270, 80, 56, "", ["esterno"], "jext", lsize=10.5)
    d.o.append('  <path d="M 1585 288 L 1645 288" stroke="#333" stroke-width="1.6" marker-end="url(#ark)"/>')
    d.text(1615, 308, "segnale", 10, "#333", "middle")
    d.o.append(f'  <path d="M 1585 340 L 1645 340" stroke="{FB}" stroke-width="2.2" marker-end="url(#arb)"/>')
    d.text(1615, 360, "feedback", 10, FB, "middle")
    d.text(1350, 386, "Stereo ovunque salvo mic e mono.", 10, "#555")
    d.footer("Fonte: SPECIFICA.md + docs/01 (dec. 1-168) + docs/fase1-fase4 · comandi dal pannello (sistema-comandi.md) · meter: 11 barre (sistema-metering.md, dec. 116), non disegnate")
    return d.save()


# ---------------------------------------------------------------- PSU
def psu():
    d = Diagram("psu", 1560, 960, "SISTEMA PSU — ALIMENTAZIONE",
                "maelcum mixer — alimentatore ESTERNO con pre-regolatori (dec. 113) · riserva (dec. 131) · regolazione finale nei moduli (dec. 93) · 2 ventole a termostato (dec. 112)",
                "box esterno · toroidale ~420 VA", GREEN)
    # i due contenitori: box esterno e mixer, uniti dal cavo
    for x, w, label in ((20, 885, "BOX ESTERNO (dec. 113) — vicino al banco, a terra su piedini"),
                        (950, 590, "MIXER — modulo PSU-IN e regolazione nei moduli")):
        d.raw(f'  <rect x="{x}" y="88" width="{w}" height="792" rx="10" fill="none" '
              'stroke="#888" stroke-width="1.5" stroke-dasharray="6 4"/>')
        d.text(x + 12, 104, label, 11, "#555", weight=700)
    RE = d.box(40, 130, 150, 90, "RETE 230 V", ["IEC + filtro EMC", "interruttore bipolare"], "dark")
    IN = d.box(220, 120, 210, 110, "INGRESSO RETE", ["fusibile T3,15 A (dec. 131)", "NTC 10-20 Ω anti-inrush",
                                                  "+ relè di bypass dopo 0,5 s"])
    TR = d.box(470, 110, 190, 130, "TOROIDALE ~420 VA", ["unico, 4 secondari", "schermo primario/secondari",
                                                       "termico integrato", "(dec. 131; catalogo 500 VA)"], "green")
    chain_h(d, [RE, IN, TR])
    d.box(690, 110, 200, 130, "CALORE NEL BOX", ["~70 W nel caso peggiore", "aletta Rθ ≤ 0,43 K/W",
                                                 "senza ventola", "chiuso: pioggia e polvere"],
          "note", tsize=12, lsize=10)
    d.box(965, 110, 560, 130, "CAVO ≤ 2 m E CONNETTORE (§3)",
          ["20 conduttori da 0,5 mm² + schermo · circolare metallico a vite, IP65, classe 24 poli",
           "±22 audio 2+2 · ±19 LN 1+1 · ±27 [M] 1+1 · +5 2 · V_FAN 1+1 · AC_OK 1 · PE 1",
           "ogni 0 V su conduttori propri fino alla stella · cadute ≤ 60 mV"],
          "note", tsize=12, lsize=10.5)
    rows = [
        ("W1 2×21 V 7,0 A", ["ponte 25 A + bulk 2 × 22 mF", "T8 A"],
         "LDO MOSFET ±22,0 V", ["Rsense 0,15 Ω: limite ~3,3-4 A", "soft-start 0,3 s · ripple ≤ 3,7 mV"],
         ["PSU-IN: TVS · T2,5 A · 2,2 mF", "modulo: LM317/337 → 19,2 V + cap mult. → ±18"],
         ["canali · 5-way · FX-RET · filtro · FX-SEND", "CUE · mic/mono · moduli opzionali",
          "!2,12 A base · 2,44 opzionali · 2,70 progetto"]),
        ("W2 2×18 V 1,5 A", ["ponte + bulk 2 × 10 mF", "T2 A"],
         "LDO MOSFET ±19 V", ["limite ~1,1 A (0,56 Ω)", "al mixer 18,84-18,92 V"],
         ["PSU-IN: TVS · T1 A · 1 mF", "modulo: pre-reg ±16,5 → LT3045/94 → ±15,0",
          "+ 78L15/79L15 ±15 per gli switch"],
         ["phono · mic · CV · meter · CUE", "OTA filtro · switch kill/assign", "!progetto 0,60 A (picco 0,55)"]),
        ("W3 2×20 V 0,4 A", ["ponte + bulk 2 × 4,7 mF", "T630 mA"],
         "RAW ±27 V [M]", ["non regolato nel box", "30,3 V a rete +10 %"],
         ["PSU-IN: TVS · T500 mA · 1 mF", "master: statici HV + LDO locali"],
         ["solo master out: +24 dBu reali", "!~130-170 mA"]),
        ("W4 9 V 2,5 A", ["ponte + bulk 10 mF", "T3,15 A"],
         "+5 V E V_FAN", ["+5: LM1084/LM2940 nel box", "V_FAN: raw W4 non regolato"],
         ["PSU-IN: TVS · T2 A · 1 mF sul +5", "V_FAN: T500 mA → driver ventole"],
         ["LED dei meter · logiche · relè", "supervisor · 2 ventole", "!+5 worst ~1,15 A · ventole 0,3 A"]),
    ]
    d.text(790, 280, "pre-regolazione nel box", 10.5, "#777", "middle")
    d.text(1095, 280, "nel mixer: PSU-IN e modulo", 10.5, "#777", "middle")
    d.text(1390, 280, "chi lo usa · corrente per ramo", 10.5, "#777", "middle")
    d.arrow([TR.b, (TR.cx, 590 - 14)], head=False)
    y = 290
    for wn, wl, reg, rl, mix, dest in rows:
        W = d.box(470, y, 190, 76, wn, wl, tsize=12, lsize=10)
        R = d.box(690, y, 200, 76, reg, rl, "dark", tsize=12, lsize=10)
        M = d.box(965, y, 260, 76, "", mix, "amber", lsize=10)
        U = d.box(1255, y, 270, 76, "", dest, "note", lsize=10)
        d.arrow([(TR.cx, y - 14), (W.cx, W.y - 2)])
        chain_h(d, [W, R, M, U])
        y += 100
    d.box(40, 290, 390, 176, "PROTEZIONI (§2.7, §4.3)",
          ["rete: interruttore bipolare · T3,15 A · NTC + relè",
           "secondari: fusibili lenti prima dei ponti",
           "   (T8 A · T2 A · T630 mA · T3,15 A) · termico",
           "uscite: limite di corrente degli LDO (corto nel cavo)",
           "nel mixer: TVS + fusibile di gruppo per rail (PSU-IN)",
           "   + PTC per slot e per rail sul backplane [PROVV]"],
          "note", align="start", lsize=10.5, tsize=12)
    d.box(40, 490, 390, 176, "TERRA E 0 V (§3, §4.2)",
          ["terra di rete → telaio del box",
           "→ conduttore PE dedicato (chiude per primo) + schermo",
           "→ telaio del mixer",
           "nel box gli 0 V non toccano la terra: ogni 0 V",
           "viaggia separato fino alla stella nel PSU-IN",
           "(unico bond telaio ↔ AGND, sistema-grounding §2)"],
          "note", align="start", lsize=10.5, tsize=12)
    AC = d.box(40, 700, 850, 80, "RIVELATORE AC_OK (§2.5, §2.6)",
               ["doppia semionda dal W1 · τ 42,7 ms · soglia al 75 % del picco · open-collector, alto = rete presente",
                "mute in ≤ 12,7 ms; con bulk 22 mF i regolatori locali escono a ≥ 25,1 ms (rete −10 %): margine ≥ 12,4 ms"],
               "ctrl", tsize=12, lsize=10.5)
    S = d.box(965, 690, 270, 176, "SUPERVISOR E MUTE (§4.4)",
              ["vive sul +5 del box, sente i rail regolati", "±22 < 21,2 / > 23,5 V · ±19 < 18,3 / > 20,5",
               "[M] < 22,0 V (5 ms) · +5 < 4,6 / > 5,5 V", "AC_OK basso → mute subito (filtro 1 ms)",
               "riarmo 1,5-2 s dopo il rientro", "cavo staccato = relè rilasciati, niente pop",
               "→ GLOBAL_MUTE (c9) + relè del master"],
              "ctrl", align="start", lsize=10, tsize=12)
    d.arrow([AC.r, (S.x - 2, AC.cy)], "cv")
    d.box(1255, 690, 270, 176, "VENTOLE E CALORE (§4.5, §5)",
          ["2 ventole: NTC sulla barra dei regolatori ±18", "driver lineare da V_FAN, niente PWM",
           "spente < 35 °C · ~6 V a 35 °C · max a 50 °C", "ventola ferma > 45 °C → LED guasto, no mute",
           "calore nel mixer ~118 W · ~132 W opzionali", "aria interna ~+4 K sopra l'ambiente"],
          "note", align="start", lsize=10, tsize=12)
    d.legend(910, [("audio", "potenza (rail)"), ("cv", "mute e supervisione"), (AMBER, "regolazione nel mixer"),
                   ("dashed", "contenitore")])
    d.footer("Fonte: docs/fase3/sistema-psu-esterno.md v0.1 (§1-§5, REV dec. 131) + sim/system/RISULTATI-psu-box.md §7 + pcb/psu-in/NOTE.md + decisioni 90/93/112/113/131")
    return d.save()


# ---------------------------------------------------------------- METERING
def metering():
    d = Diagram("metering", 1560, 960, "SISTEMA METERING — BARRE LED A ZONE",
                "maelcum mixer — design S4 v0.1 · ballistica Pioneer DJM (dec. 81) · soglie assolute (dec. 90): fondo scala +24 dBu uguale su ogni barra",
                "11 barre + LED mic/mono", GREEN)
    # punti di presa
    d.text(40, 122, "PUNTI DI PRESA (SPECIFICA §11, bloccati)", 13, INK, weight=700)
    taps = [("MASTER L/R", ["post master level,", "pre stadio HV", "2 barre da 20 segm."]),
            ("DJ × 4", ["post EQ, pre-fader,", "senza filtro (dec. 161b)", "4 barre da 10 segm."]),
            ("5-WAY", ["post drive, pre", "master sum (g × 2)", "1 barra da 10 segm."]),
            ("RITORNI FX × 4", ["post gain/EQ2, pre-fader", "uno per ritorno (dec. 116)", "4 barre da 10 segm."]),
            ("MIC / MONO", ["dopo il preamp,", "prima dell'EQ2", "solo LED tricolore"])]
    for i, (t, ln) in enumerate(taps):
        d.box(40 + i * 300, 136, 270, 86, t, ln, "dark", tsize=12.5, lsize=10.5)
    # catena per zona
    d.text(40, 268, "CATENA PER BARRA (§2) — una per ogni barra, detector su ±15 V LN", 13, INK, weight=700)
    y = 284
    c1 = d.box(40, y, 220, 96, "INGRESSO", ["guadagno g + trim ±2 %", "(calibrazione per zona)", "buffer OPA1612"], tsize=12, lsize=10)
    c2 = d.box(300, y, 220, 96, "SUPERDIODO", ["OPA + 1N4148", "clamp anti-windup −1,5 V", "attacco 0,23 ms"], tsize=12, lsize=10)
    c3 = d.box(560, y, 220, 96, "HOLD + RELEASE", ["C 100 nF da solo sul nodo", "R 2M + trimmer 3,3M", "τ 0,2…0,53 s (0,3 tipico)"], tsize=12, lsize=10)
    c4 = d.box(820, y, 200, 96, "BUFFER", ["hold al picco +24,00 dBu", "droop −2,9 dB/ciclo", "a 10 Hz (dec. 81)"], tsize=12, lsize=10)
    c5 = d.box(1060, y - 30, 220, 76, "LM3915 (scala)", ["10 segm. × 3 dB · master:", "2 chip in cascata = 20"], "green", tsize=12, lsize=10)
    c6 = d.box(1060, y + 70, 220, 76, "PURPLE (clip latch)", ["LM339 a +23 dBu", "one-shot 0,7 s → 479 ms"], "purple", tsize=12, lsize=10)
    chain_h(d, [c1, c2, c3, c4])
    d.arrow([c4.r, (1040, c4.cy), (1040, c5.cy), (c5.x - 2, c5.cy)])
    d.arrow([(1040, c4.cy), (1040, c6.cy), (c6.x - 2, c6.cy)])
    d.dot(1040, c4.cy)
    led = d.box(1320, y - 30, 200, 176, "LED", ["LM3915 sul +5 V control", "(LED isolati dal rail LN)", "2-5 mA per segmento",
                                             "worst ~0,67 A (5 mA)", "~0,27 A con LED da 2 mA", "master purple: sensing",
                                             "dello stadio HV [aperto]"], "note", tsize=12, lsize=10)
    d.arrow([c5.r, (led.x - 2, c5.cy)])
    d.arrow([c6.r, (led.x - 2, c6.cy)])
    # scala colori
    d.text(40, 470, "SCALA E COLORI (§3) — soglie dec. 90 rispettate, split giallo/ambra a +12 [PROVV]", 13, INK, weight=700)
    bands = [("BLU", "< −6 dBu", "#3B6FB6", "solo master (9 segm.)"),
             ("VERDE", "−6 … +6", "#2E9E4F", "programma attorno a 0"),
             ("GIALLO", "+6 … +12", "#E3C21B", "forte"),
             ("AMBRA", "+12 … +18", "#E88A1A", "molto forte"),
             ("ROSSO", "+18 … +24", "#D2322D", "estremo"),
             ("VIOLA", "≥ +23 latch", "#8A4A9E", "clip, LED dedicato")]
    x = 40
    for name, rng, col, note in bands:
        d.o.append(f'  <rect x="{x}" y="490" width="236" height="40" rx="6" fill="{col}"/>')
        d.text(x + 118, 515, name, 13, "#fff" if name != "GIALLO" else "#141414", "middle", 700)
        d.text(x + 118, 550, rng, 11.5, INK, "middle", 600)
        d.text(x + 118, 568, note, 10.5, "#666", "middle")
        x += 248
    d.text(40, 598, "Zone a 10 segmenti: +24 … −3 dBu (sotto −3 la barra è spenta). Master a 20 segmenti: +24 … −33 dBu.", 11, "#444")
    # albero riferimenti
    d.box(40, 630, 720, 110, "ALBERO DEI RIFERIMENTI CONDIVISO (§5)",
          ["+15 V LN → partitore 10k/5k 0,1 % → follower → vrefA 5,000 V = fondo scala +24 dBu (tutte le barre)",
           "→ partitore 10k/4,625k 0,1 % → follower → vrefB 1,581 V (secondo chip delle cascate master)",
           "!follower obbligatori: il partitore nudo caricato scendeva a 4,07 V (finding sim)",
           "calibrazione identica per costruzione: errore ≤ ±0,012 dB"], "ctrl", align="start", lsize=10.5, tsize=12)
    d.box(800, 630, 720, 110, "MIC / MONO: UN LED TRICOLORE (dec. 97)",
          ["verde = segnale ok (≥ −6 dBu) · giallo = vicino al clip (≥ +11) · rosso = clip (≥ +17, latch)",
           "rosso a +17 e non +23: il front-end mic su ±15 V clippa prima, e l'EQ2 aggiunge fino a +6",
           "soglie [PROVVISORIO] · comparatori LM339 condivisi col purple delle zone"],
          "note", align="start", lsize=10.5, tsize=12)
    d.box(40, 770, 1480, 92, "BOM E APERTI",
          ["BOM di massima: 13 LM3915 · ~12 OPA1612 · 3 LM339 · ~133 LED + 11 purple · ~50-80 € [molto PROVVISORIA]. Alternativa a LM3915: ladder di LM339 (10× i chip).",
           "Niente meter su booth, rec, cuffie e mandate (SPECIFICA §11). Aperti (voce 40 / q54): posizione delle barre, 10 o 20 segmenti per zona,",
           "luminosità 2 o 5 mA (consigliata 2 mA), purple del master a doppio criterio o uno solo, procedura di calibrazione con toni a livelli noti."],
          "note", align="start", lsize=10.5, tsize=12)
    d.legend(892, [("audio", "segnale"), ("cv", "riferimenti / logica")])
    d.footer("Fonte: docs/fase3/sistema-metering.md v0.1 (§1-§9, REV dec. 116) + sim/system/meter-*.cir + sim/meter/RISULTATI-peak-det.md + decisioni 81/90/97/116/161")
    return d.save()


DIAGRAMMI = (schema_totale, canale, fx, fx_send, master, five_way, filtro, cue, mic_mono, psu, metering)

if __name__ == "__main__":
    lingue = [lg for lg in ("it", "en") if f"--{lg}" in sys.argv] or ["it", "en"]
    warn = []
    for LANG in lingue:
        for f in DIAGRAMMI:
            warn += f()
        print(f"scritti {len(DIAGRAMMI)} SVG ({LANG}) in", HERE if LANG == "it" else os.path.join(HERE, "en"))
    for w in warn:
        print("ATTENZIONE:", w)
    for s in MISSING:
        print("SENZA TRADUZIONE:", s)
