#!/usr/bin/env python3
# Genera lo schema funzionale totale e i diagrammi a blocchi SVG dei moduli
# del maelcum mixer.
# Uso:  python3 genera_diagrammi.py      (scrive i .svg in questa cartella)
# I contenuti vengono dai design doc: quando un doc cambia, si aggiorna
# la funzione del modulo qui sotto e si rilancia lo script.
# Il dettaglio della cella parametrica 5-way sta in cella-v021.frag
# (frammento SVG a mano del 2026-09-28, invariato dal design v0.2.1).
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "2026-10-14"

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
        self._chk(sub, 13, w - 80 - (300 if pill else 0), "sottotitolo")
        if pill:
            pw = max(150, int(len(pill) * 6.9) + 30)
            self.o.append(f'  <rect x="{w - 40 - pw}" y="34" width="{pw}" height="24" rx="12" fill="{pill_color}"/>')
            self.text(w - 40 - pw / 2, 50, pill, 12, "#fff", "middle", 600)

    def _chk(self, s, size, maxw, where):
        est = len(s) * size * 0.52
        if est > maxw:
            self.warn.append(f"{self.name}: testo largo ~{est:.0f} > {maxw:.0f} in {where}: {s[:50]}")

    def text(self, x, y, s, size=10.5, color="#444", anchor="start", weight=None):
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
            self.warn.append(f"{self.name}: box '{title}' troppo basso ({block:.0f} > {h})")
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
            self._chk(ln, lsize, w - 8, f"box {title}")
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
            if kind in ("audio", "cv", "fb"):
                col, sw, dash = {"audio": (AUDIO, 2.5, None), "cv": (CV, 1.5, "6 4"), "fb": (FB, 2.2, None)}[kind]
                ds = f' stroke-dasharray="{dash}"' if dash else ""
                self.o.append(f'  <path d="M {x} {y} L {x + 50} {y}" stroke="{col}" stroke-width="{sw:g}"{ds}/>')
            elif kind == "dashed":
                self.o.append(f'  <rect x="{x}" y="{y - 9}" width="50" height="18" rx="4" fill="#F3F2EE" '
                              'stroke="#888" stroke-width="1.5" stroke-dasharray="6 4"/>')
            else:
                self.o.append(f'  <rect x="{x}" y="{y - 8}" width="46" height="16" rx="8" fill="{kind}"/>')
            self.text(x + 58, y + 4, label, 11.5, "#333")
            x += 58 + int(len(label) * 6.2) + 40

    def footer(self, s, data=DATA):
        self.text(40, self.h - 22, s + " · " + data, 10.5, "#999")
        self._chk(s, 10.5, self.w - 60, "footer")

    def save(self):
        self.o.append("</svg>\n")
        open(os.path.join(HERE, self.name + ".svg"), "w", encoding="utf-8").write("\n".join(self.o))
        return self.warn


def chain_h(d, boxes, kind="audio"):
    for a, b in zip(boxes, boxes[1:]):
        d.arrow([a.r, (b.x - 2, b.cy)], kind)


def chain_v(d, boxes, kind="audio"):
    for a, b in zip(boxes, boxes[1:]):
        d.arrow([a.b, (b.cx, b.y - 2)], kind)


# ---------------------------------------------------------------- CANALE
def canale():
    d = Diagram("canale-cdj", 1560, 880, "MODULO CANALE CDJ / LINE",
                "maelcum mixer — design v0.4 · send FX nel micro-modulo (dec. 91a), rail dec. 93, rumore dec. 89 — metà canale L; R identica e linked",
                "phono MM incluso (dec. 79)", GREEN)
    rca = d.box(40, 170, 130, 72, "RCA IN", ["line −10 dBV…+4 dBu"])
    d.text(105, 258, "0 dBu nom / +8 worst", 10, AUDIO, "middle")
    A = d.box(215, 170, 165, 72, "[A] PROT + BUFFER", ["R 100 Ω + TVS low-cap + bead", "OPA1612 unity, Zin ≥ 47k"])
    B = d.box(425, 170, 175, 72, "[B] GAIN", ["VCA THAT 218x stereo link", "−∞ → 0 (detent) → +10 dB"])
    d.text(520, 258, "post: 0 / +10 dBu worst", 10, AUDIO, "middle")
    C = d.box(650, 150, 240, 112, "[C] EQ ISOLATOR 4 BANDE",
              ["bande in parallelo LR4 (dec. 105)", "LOW / LOW-MID / MID-HIGH / HIGH",
               "silenzio … 0 (detent) … +6 dB", "somma non invertente + servo DC"])
    d.text(770, 278, "post: 0 / +16 dBu worst", 10, AUDIO, "middle")
    chain_h(d, [rca, A, B, C])
    cvg = d.box(425, 100, 175, 32, "", ["CV gain (1 per coppia L/R)"], "ctrl", lsize=11)
    d.arrow([cvg.b, (B.cx, B.y - 2)], "cv")
    pots = d.box(650, 84, 240, 32, "", ["4 pot doppi lin. + contatto fondo corsa"], "ctrl", lsize=11)
    d.arrow([pots.b, (C.cx, C.y - 2)], "cv")
    # nodo split
    nx = 935
    d.arrow([C.r, (nx, 206)], head=False)
    d.text(nx - 8, 352, "nodo split post-EQ", 11, INK, "end", 700)
    D = d.box(985, 110, 220, 66, "[D] CUE SEND", ["buffer → switch cue → CUE bus", "post-EQ, pre-filter, pre-fader"])
    E = d.box(985, 196, 220, 86, "[E] SEND TAP (dec. 91a)",
              ["buffer ≤ 50 Ω → backplane slot 3", "!EQ2 + level + assign: non più qui",
               "vivono nel micro-modulo FX-SEND"])
    F = d.box(985, 302, 220, 66, "[F] FILTER I/F", ["send/return al modulo filtro", "switch 3 vie (HPF / OFF / LPF)"])
    d.arrow([(nx, 206), (nx, D.cy), (D.x - 2, D.cy)])
    d.arrow([(nx, 206), (nx, E.cy), (E.x - 2, E.cy)])
    d.arrow([(nx, 206), (nx, F.cy), (F.x - 2, F.cy)])
    d.dot(nx, 206)
    d.text(1220, D.cy + 4, "→ modulo CUE (slot 2)", 10.5, "#777")
    d.text(1220, E.cy + 4, "→ FX-SEND del canale", 10.5, "#777")
    d.text(1220, F.cy - 6, "send 0 dBu pre-fader", 10.5, "#777")
    BT = d.box(985, 420, 220, 70, "BOTTONI ASSIGN S1-S4",
               ["restano sul pannello del canale", "linee logiche +5 V → FX-SEND"], "ctrl", tsize=12)
    d.arrow([BT.r, (1295, BT.cy)], "cv")
    d.text(1213, BT.cy - 8, "→ FX-SEND", 10, CV)
    # colonna uscita
    G = d.box(1330, 440, 190, 66, "[G] METER DJ", ["LM3915 10 seg × 3 dB [PROVV]", "release ~0,3 s (dec. 81) + latch"])
    H = d.box(1330, 536, 190, 66, "[H] FADER", ["−∞ → 0, stereo linked", "tracking ≤ 0,5 dB + buffer"])
    I = d.box(1330, 632, 190, 60, "[I] OUT DRIVER", ["Z ≤ 50 Ω → DJ BUS (slot 1)"])
    d.text(1425, 708, "0 dBu nom / +16 worst", 10, AUDIO, "middle")
    d.arrow([(1150, F.y + F.h), (1150, 394), (G.cx, 394), (G.cx, G.y - 2)])
    d.text(1260, 388, "ritorno filtro", 10.5, "#777")
    chain_v(d, [G, H, I])
    fc = d.box(1330, 100, 190, 32, "", ["slider doppio nel segnale"], "ctrl", lsize=11)
    d.arrow([fc.r, (1542, fc.cy), (1542, H.cy), (H.x + H.w + 2, H.cy)], "cv")
    # phono
    A0 = d.box(40, 330, 205, 104, "[A0] PHONO MM v0.1",
               ["RIAA passiva 42 dB · EIN 1,79 µV", "curva ≤ ±0,05 dB 100 Hz–20 kHz",
                "overload +18 dBu · −0,24 dB a 30 Hz", "phono-stage.md (dec. 79)"], "green", tsize=12.5)
    SEL = d.box(40, 464, 205, 54, "SELETTORE LINE/PHONO", ["switch precisione + mute breve"], "ctrl", tsize=12)
    d.arrow([A0.b, (SEL.cx, SEL.y - 2)])
    d.arrow([SEL.r, (440, SEL.cy), (440, B.y + B.h + 2)])
    d.text(258, SEL.cy - 8, "→ [B] GAIN (stesso nodo del buffer line)", 10, "#777")
    d.box(40, 730, 960, 66, "[H2] PSU LOCALE",
          ["raw ±27 V audio e ±22 V LN in (dec. 93) → ±18 V audio (LM317/337) · ±15,0 V LN (pre-reg ±16,5 → LT3045/94: CV, meter, phono) · +5 V control"],
          "note", align="start")
    d.box(1040, 730, 480, 66, "RUMORE DEL CANALE",
          ["target ≤ −80 dBu A-wtd (dec. 89) · misurato −94,6 con l'EQ isolator (docs/06 §10)"], "note", align="start")
    d.legend(826, [("audio", "percorso audio (livelli annotati in rosso)"), ("cv", "controllo CV / logiche"),
                   (FB, "nota evidenziata")])
    d.footer("Fonte: docs/fase1/cdj-line-channel.md v0.4 (§3.5 REV dec. 91a) + eq-isolator-v0.4.md (dec. 105, §9) + phono-stage.md + gain-staging-sheet.md §2 · 0 dBu = 0,775 Vrms · K4: level_in × gain ≤ +23 dBu")
    return d.save()


# ---------------------------------------------------------------- FX
def fx():
    d = Diagram("fx", 1560, 900, "MODULO FX — 4 BUS + MATRICE FEEDBACK 16×",
                "maelcum mixer — design v0.3-WIP (dec. 91): self-feedback ammesso, send di canale nei micro-moduli FX-SEND · sotto: UNA delle 4 sezioni identiche (BUS n)",
                "v0.3-WIP (dec. 91)")
    y = 150
    src = d.box(40, y - 10, 200, 106, "DAI MICRO-MODULI FX-SEND",
                ["4 canali × assign S1-S4 (dec. 91a)", "+ mic / generic", "net multidrop per bus:",
                 "10k lato sorgente"], tsize=12)
    SUM = d.box(285, y, 180, 86, "SUMMING BUS n", ["virtual-earth", "worst 12 × 0 dBu: +21,5 dBu"])
    DRV = d.box(510, y, 180, 86, "DRIVER", ["buffer low-Z ≤ 50 Ω (OPA1612)", "!pad fisso 0 dB (dec. 108)"])
    PRO = d.box(735, y, 170, 86, "PROTEZIONE", ["R serie 100 Ω + TVS ≤ 5 pF", "banda 40 kHz verificata §8.4"])
    JS = d.box(950, y, 150, 86, "JACK SEND n", ["→ pedale (L/R)", "mono = sum 2 × 10k"], "dark")
    PED = d.box(1145, y, 110, 86, "PEDALE", ["esterno", "−20…+18 dBu"], "dashed")
    JR = d.box(1300, y, 180, 86, "JACK RETURN n", ["← pedale (L/R, stereo-capable)"], "dark")
    chain_h(d, [src, SUM, DRV, PRO, JS, PED, JR])
    d.text(SUM.cx + 14, y + 104, "margine 7,3 V al clamp ±16,5", 10, AUDIO)
    PDC = d.box(1290, 290, 200, 84, "PROT + DC CONTROL", ["DC servo integrato VALIDATO", "corner 0,05-0,5 Hz, nulling 84 dB"])
    BUF = d.box(1290, 404, 200, 66, "BUFFER HI-Z", ["JFET, Zin ≥ 1 MΩ (bias 1 MΩ §8.4)"])
    GAI = d.box(1290, 500, 200, 84, "GAIN VCA 218x", ["−∞ → 0 → +20 dB", "!compensa LEVEL in mandata (108)", "senza limite: K4 (dec. 84)"])
    EQ2 = d.box(1290, 614, 200, 70, "EQ2 RITORNO", ["celle serie v0.3 VALIDATE", "LOW ~120 Hz / HIGH ~4,5 kHz"])
    d.arrow([JR.b, (PDC.cx, PDC.y - 2)])
    chain_v(d, [PDC, BUF, GAI, EQ2])
    MET = d.box(1020, 614, 220, 70, "METER pickup", ["detector condiviso (CDJ §7)", "release ~0,3 s (dec. 81) · latch clip"])
    NOD = d.box(770, 614, 200, 70, "NODO REROUTE", ["PRE-FADER [BLOCCATO]", "fader giù → il feedback continua"], "ctrl")
    FAD = d.box(520, 614, 200, 70, "FADER ritorno", ["stereo linked → buffer", "→ backplane MASTER SUM"])
    d.arrow([EQ2.l, (MET.x + MET.w + 2, MET.cy)])
    d.arrow([MET.l, (NOD.x + NOD.w + 2, NOD.cy)])
    d.arrow([NOD.l, (FAD.x + FAD.w + 2, FAD.cy)])
    OUT = d.box(150, 720, 290, 58, "→ BACKPLANE MASTER SUM", ["un ingresso per ritorno: MSUM2-5 (dec. 94a)"], "dark")
    d.arrow([FAD.l, (OUT.cx, FAD.cy), (OUT.cx, OUT.y - 2)])
    MAT = d.box(690, 390, 360, 140, "MATRICE FEEDBACK 16× (dec. 91b)",
                ["4 × VCA 218x per ritorno: 3 cross + 1 SELF (quarto pot)", "law a tratti SPEC verificata end-to-end (§8.3)",
                 "!self-route AMMESSO: il divieto v0.2 è revocato",
                 "bounded-by-design confermato sul ramo self (§8.5)"], "purple")
    d.arrow([NOD.t, (MAT.cx, MAT.y + MAT.h + 2)], "fb")
    d.arrow([MAT.t, (MAT.cx, 300), (SUM.cx, 300), (SUM.cx, SUM.y + SUM.h + 2)], "fb")
    d.text(SUM.cx + 14, 292, "loop di feedback verso i SUMMING dei 4 bus, INCLUSO il proprio · giro = GAIN + reroute (LEVEL fuori): con GAIN +20 innesca a ~45 % del reroute", 10.5, FB)
    CVB = d.box(300, 400, 300, 120, "CATENA CV REROUTE",
                ["pot → CV buffer → shaper a tratti", "(famiglia law filtro, dec. 70) →",
                 "smoothing 1 ms (dec. 80) →", "CV 6,1 mV/dB ai VCA (dec. 92), 1 per coppia L/R"], "ctrl")
    d.arrow([CVB.r, (MAT.x - 2, CVB.cy)], "cv")
    d.box(520, 720, 970, 58, "",
          ["±18 V audio (summing/driver/VCA) · ±15 V LN (CV/shaper/servo) · VCA 218x = SINGLE: 20 chip in questo modulo (16 reroute + 4 gain)",
           "mixer ~34-36 chip · rotta clone CoolAudio V2181L, acquisti dopo il prototipo M4L (voce 37) · mute dei send: GLOBAL_MUTE sui FX-SEND (dec. 94b)"],
          "note", align="start", lsize=11)
    d.legend(826, [("audio", "audio"), ("fb", "feedback (matrice reroute)"), ("cv", "controllo CV"),
                   ("dashed", "esterno al mixer")])
    d.footer("Fonte: docs/fase1/fx-module.md v0.3-WIP (§2/§4 REV dec. 108/§7/§8.3-8.5) + fx-send-module.md + sim/fx/ · livelli worst: summing +21,5 dBu, loop +20,2 dBu (mai ai rail)")
    return d.save()


# ---------------------------------------------------------------- FX-SEND
def fx_send():
    d = Diagram("fx-send", 1560, 700, "MICRO-MODULO FX-SEND (×4, uno per canale)",
                "maelcum mixer — design v0.1-WIP (dec. 91a): EQ2 + level + assign escono dal canale CDJ · 4× stesso PCB · metà L; R identica",
                "nuovo modulo (dec. 91a)", GREEN)
    IN = d.box(40, 170, 195, 96, "SEND TAP L/R", ["dal canale CDJ, blocco [E]", "post-EQ, pre-filter, pre-fader",
                                               "backplane slot 3 del canale"], "dark")
    BUF = d.box(280, 178, 150, 80, "BUFFER IN", ["OPA1612 unity", "isola il driver di canale"])
    EQ = d.box(475, 160, 235, 116, "EQ2 — celle serie",
               ["LOW shelf ~120 Hz", "HIGH sottrattiva ~4,5 kHz (q. 68)", "−∞ → 0 → +6, law dedicate",
                "pot doppi 10k custom taper"])
    LEV = d.box(755, 170, 175, 96, "LEVEL", ["pot doppio 10k log (curva A)", "−∞ … 0 dB, mai gain positivo", "!unico livello al pedale (108)"])
    ASG = d.box(975, 160, 215, 116, "ASSIGN × 4 (S1-S4)",
                ["π SPDT classe ADG1434", "serie + shunt a GND da off", "multipli e simultanei",
                 "BBM + ramp 1 ms (dec. 80)"])
    INJ = d.box(1235, 160, 285, 116, "BUFFER DI INIEZIONE × 8",
                ["OPA1654 quad × 2 (unity)", "+ R 10k di iniezione per linea", "OUT S1-S4 L/R = 8 linee"])
    chain_h(d, [IN, BUF, EQ, LEV, ASG, INJ])
    BUS = d.box(1235, 340, 285, 70, "→ BUS FX 1-4 (backplane)",
                ["summing virtual-earth del modulo FX", "net multidrop, come il DJ bus"], "dark")
    d.arrow([INJ.b, (BUS.cx, BUS.y - 2)])
    BT = d.box(640, 350, 260, 92, "BOTTONI ASSIGN S1-S4",
               ["sul pannello del CANALE (gesto invariato)", "linee logiche +5 V via harness frontale",
                "l'audio non passa mai dai contatti"], "ctrl", tsize=12)
    RMP = d.box(985, 356, 195, 80, "RAMP", ["R 10k + C 100 nF sul pin IN", "τ ≈ 0,5-1 ms: click −9 dB"], "ctrl", tsize=12)
    d.arrow([BT.r, (RMP.x - 2, RMP.cy)], "cv")
    d.arrow([RMP.t, (ASG.cx, ASG.y + ASG.h + 2)], "cv")
    GM = d.box(1235, 460, 285, 70, "GLOBAL_MUTE (linea c9)",
               ["dal mute controller [L] del master", "muta i buffer d'iniezione (dec. 94b)"], "ctrl", tsize=12)
    d.arrow([GM.l, (1212, GM.cy), (1212, 258), (INJ.x - 2, 258)], "cv")
    d.box(40, 340, 550, 190, "PERCHÉ UN MICRO-MODULO",
          ["Il canale CDJ resta più semplice: gli resta solo il SEND TAP.",
           "Comportamenti LOCKED invariati (SPECIFICA §2): punto di presa,",
           "bande e law dell'EQ2, level senza gain, assign multipli.",
           "Rumore del send chain: −98,5 dBu A-wtd per canale.",
           "Con un assign ON il floor di sistema sale a ~−73 dBu A-wtd",
           "(−66,6 con 4 send a level max): deroga d'uso, decisione 95."],
          "note", align="start", lsize=11)
    d.legend(590, [("audio", "audio"), ("cv", "controllo: logiche +5 V / mute")])
    d.footer("Fonte: docs/fase1/fx-send-module.md v0.1-WIP (§2-§6) + sistema-backplane.md (classe FX-SEND) + sim/fx/RISULTATI-send-chain-71A.md + decisioni 91/94b/95/108")
    return d.save()


# ---------------------------------------------------------------- MASTER
def master():
    d = Diagram("master-out", 1560, 940, "MODULO MASTER OUT",
                "maelcum mixer — design v0.2 + stadio finale v0.3 DEFINITIVA (bootstrap, dec. 86) + summing (dec. 94a) + MON verso CUE · rami indipendenti dallo stesso nodo",
                "stadio finale v0.3 chiuso", GREEN)
    CON = d.box(40, 120, 215, 150, "MASTER SUM: 7 CONTRIBUTORI",
                ["5-way (MSUM1)", "ritorni FX 1-4 (MSUM2-5)", "mic · generic", "stereo, single-ended 0 dBu",
                 "(dec. 94a)"], "dark", tsize=12)
    A2 = d.box(300, 130, 220, 84, "[A]+[A2] MASTER SUMMING × 2",
               ["invertente su massa virtuale", "OPA1612, unity, ±15 V LN"], tsize=12)
    d.arrow([(CON.x + CON.w, A2.cy), (A2.x - 2, A2.cy)])
    by = 238                         # bus del nodo programma
    cols = {"main": 410, "booth": 665, "rec": 915, "mon": 1165}
    d.arrow([A2.b, (410, by), (cols["mon"], by)], head=False)
    d.dot(410, by)
    d.text(540, by - 8, "nodo programma: post-summing, pre-master-level", 10.5, "#777")
    # colonna master
    D = d.box(300, 262, 220, 92, "[D] MASTER LEVEL × 1",
              ["2 × VCA THAT 218x (L/R), un CV", "−∞ → 0 (detent ~75-80 %) → +6 dB", "CV: pot 10k → shaper → buffer"])
    E = d.box(300, 378, 220, 60, "[E] METER PICKUP", ["20 seg × 3 dB, release ~0,3 s, latch"], lsize=10)
    F = d.box(300, 462, 220, 60, "[F] OUT FRONT × 2", ["OPA1612, composito con [G]"])
    G = d.box(300, 546, 220, 124, "[G] STADIO HV BOOTSTRAP × 2",
              ["!rail OPA1612 flottanti OUT ± 5,3 V", "stringa 9 × 1N4148 + pass MJE340/350",
               "+25,4…+25,6 dBu · THD 0,00012 % a +24", "corto 106 mA limitato · servo DC 30 µV"], tsize=12, lsize=10)
    H = d.box(300, 694, 220, 60, "[H] MUTE + PROTEZIONE", ["relay, comandato da [L]"])
    I = d.box(300, 778, 220, 60, "[I] XLR MASTER L/R", ["bilanciato, +24 dBu capable"], "dark")
    d.arrow([(410, by), (410, D.y - 2)])
    chain_v(d, [D, E, F, G, H, I])
    d.text(286, 304, "dominio ±18 V:", 10, AUDIO, "end")
    d.text(286, 318, "+23 dBu max (K4)", 10, AUDIO, "end")
    d.text(286, 604, "+24 dBu reali SOLO qui", 10, AUDIO, "end")
    d.text(286, 618, "statici [M] (dec. 93)", 10, AUDIO, "end")
    # booth
    B = d.box(560, 262, 210, 60, "[B] BOOTH BUFFER × 2", ["±18 V"])
    B2 = d.box(560, 346, 210, 66, "[B2] BOOTH LEVEL", ["VCA 218x singoli (L/R)", "−∞ → 0 dB, pot dedicato"])
    B3 = d.box(560, 436, 210, 60, "[B3] BOOTH DRIVER × 2", ["±18 V"])
    B4 = d.box(560, 520, 210, 60, "[B4] BOOTH MUTE", ["comandato da [L]"])
    B5 = d.box(560, 604, 210, 60, "[B5] USCITA BOOTH", ["XLR (risposta di Filippo 09-18)"], "dark", lsize=10)
    d.arrow([(B.cx, by), (B.cx, B.y - 2)])
    chain_v(d, [B, B2, B3, B4, B5])
    # rec
    C = d.box(810, 262, 210, 60, "[C] REC BUFFER × 2", ["±15 V LN (decisione 63)"])
    C2 = d.box(810, 346, 210, 66, "[C2] ATTENUATORE", ["fisso, partitore di precisione", "livello adatto allo Zoom"])
    C3 = d.box(810, 436, 210, 60, "[C3] REC MUTE", ["comandato da [L]"])
    C4 = d.box(810, 520, 210, 60, "[C4] USCITA REC", ["TRS / mini-jack [APERTO-F]"], "dark")
    d.arrow([(C.cx, by), (C.cx, C.y - 2)])
    chain_v(d, [C, C2, C3, C4])
    # mon
    N = d.box(1060, 262, 210, 84, "[N] MON BUFFER × 2",
              ["!nuovo (design S5, 2026-10-02)", "OPA1612 unity non invertente", "uscita ≤ 50 Ω"], "std")
    NO = d.box(1060, 370, 210, 70, "→ BACKPLANE slot 8", ["MON out L/R → modulo CUE", "non passa da [L]: cuffia sempre viva"], "dark", lsize=10)
    d.arrow([(N.cx, by), (N.cx, N.y - 2)])
    chain_v(d, [N, NO])
    # mute controller + psu
    L = d.box(1310, 470, 215, 110, "[L] MUTE CONTROLLER",
              ["analogico: supervisore rail + timer", "power-on: attesa 1,5-2 s", "power-off: relay aperti in < 10 ms"], "ctrl", tsize=12, lsize=10)
    d.arrow([(L.x, 490), (C3.x + C3.w + 2, 490)], "cv")
    d.text(1040, 484, "mute → [C3]", 10, CV)
    busy = 724
    d.arrow([(L.x, 560), (1290, 560), (1290, busy), (H.x + H.w + 2, busy)], "cv")
    d.arrow([(790, busy), (790, B4.cy), (B4.x + B4.w + 2, B4.cy)], "cv")
    d.text(620, busy - 8, "mute → [H]", 10, CV)
    d.text(798, 640, "mute → [B4]", 10, CV)
    GMU = d.box(1310, 612, 215, 70, "GLOBAL_MUTE (c9)",
                ["!linea backplane (dec. 94b)", "relay dei moduli + buffer FX-SEND"], "dark", tsize=12, lsize=10)
    d.arrow([L.b, (GMU.cx, GMU.y - 2)], "cv")
    d.box(1310, 120, 215, 250, "[M] PSU LOCALE",
          ["raw ±26 V [M] in", "(W3 dedicato, dec. 93)", "→ statici ±23,6…29,2 V", "   stadio HV [G]",
           "→ ±18 V LM317/337", "   front / VCA / booth", "→ ±15 V LT3045/94", "   summing, meter, REC",
           "+5 V control dal bus", "   LED, logica mute"], "note", align="start", lsize=10.5)
    d.legend(876, [("audio", "audio"), ("cv", "controllo / mute"), (FB, "modifica rispetto al 2026-09-28"),
                   (INK, "connettore / backplane")])
    d.footer("Fonte: docs/fase1/master-out.md v0.2 + ADDENDA (REC dec. 63, bootstrap dec. 83→86, [N] MON 2026-10-02) + sim/master-out/RISULTATI-composite.md Test 7-12 + decisioni 93/94")
    return d.save()


# ---------------------------------------------------------------- 5-WAY
def five_way():
    d = Diagram("five-way", 1560, 1400, "MODULO 5-WAY — DUB PREAMP",
                "maelcum mixer — design v0.3: kill a switch (dec. 88), drive v0.4 GROWL + NASTRO (dec. 99), celle v0.2.1 · ordine BLOCCATO: kill → EQ → drive → meter",
                "drive v0.4 + kill a switch", GREEN)
    x, w = 40, 340
    BUSI = d.box(x, 100, w, 60, "DJ BUS L/R (dal backplane)", ["0 dBu nom · worst +12 dBu (4 × correlati)"], "dark")
    PAD = d.box(x, 190, w, 60, "PAD −6 dB + BUFFER", ["riferimento interno −6 dBu (dec. 73)"])
    KB = d.box(x, 280, w, 300, "KILL BANK (per lato)",
               ["LR4 5 vie ALLINEATA IN FASE:", "somma piatta −0,004…−0,011 dB", "",
                "SUB ── inv ── [switch K1]", "KICK ──────── [switch K2]", "MID ── inv ── [switch K3]",
                "HIGH ──────── [switch K4]", "SUPER ─────── [switch K5]", "",
                "!gate = SWITCH π SPDT hard-cut (dec. 88)", "!10 VCA 218x rimossi dai gate",
                "2 invertitori unity (SUB/MID) per la polarità", "ALL-KILL = silenzio assoluto"])
    EQ = d.box(x, 610, w, 150, "EQ CREATIVO — 5 CELLE v0.2.1",
               ["parametriche SVF in serie (dettaglio a destra)", "gain −∞(notch)…0…+15/12/9 dB · Q 3/1/0,5",
                "position 2,6 ottave/banda · gain: 5 pot rotativi (dec. 85)",
                "le 5 bande EQ NON sono le 5 vie", "freq. centri ~90/350/1,2k/3,5k [PROVV — q. 67]"], "green", lsize=10)
    DR = d.box(x, 790, w, 130, "DRIVE v0.4: GROWL + NASTRO",
               ["due saturatori in parallelo al pulito (dec. 99)", "due manopole, il volume resta fermo",
                "niente fuzz, niente VCA · griglia confermata", "dettaglio in alto a destra"], "green")
    ME = d.box(x, 950, w, 60, "METER pickup", ["detector condiviso · release ~0,3 s (dec. 81)"])
    MU = d.box(x, 1040, w, 60, "MAKE-UP +6 dB + TRIM", ["uscita 0 dBu nominale"])
    OUT = d.box(x, 1130, w, 56, "→ MASTER SUM (MSUM1, backplane)", [], "dark", tsize=12.5)
    chain_v(d, [BUSI, PAD, KB, EQ, DR, ME, MU, OUT])
    # zoom drive
    zx = 420
    d.raw(f'  <rect x="{zx}" y="100" width="1100" height="300" rx="10" fill="#fff" stroke="{GREEN}" stroke-width="1.5"/>')
    d.text(zx + 30, 134, "ZOOM — DRIVE v0.4 GROWL + NASTRO (five-way §5bis, per lato)", 16, GREEN, weight=700)
    d.text(zx + 30, 154, "ogni manopola dosa il segnale «differenza» (saturato meno pulito): a manopola chiusa l'uscita è l'ingresso esatto", 11.5, "#666")
    X = d.box(zx + 30, 180, 170, 112, "SOMMA EQ", ["−6 dBu nominale", "percorso pulito", "DC-coupled"], tsize=12, lsize=10)
    G = d.box(zx + 240, 180, 250, 112, "GROWL (sotto 350 Hz)",
              ["LP 2 poli a 350 Hz → clipper", "diodi asimmetrici 1 × / 3 × 1N4148", "2ª e 3ª armonica · kg 0,613",
               "pot lineare GROWL dosa la differenza"], "amber", tsize=12, lsize=10)
    T = d.box(zx + 530, 180, 250, 112, "NASTRO (tutto il segnale)",
              ["CS JFET, Rs divisa 150 + 900 Ω", "curvatura morbida da subito", "quasi solo 2ª armonica · kt 0,206",
               "pot lineare NASTRO dosa la differenza"], "amber", tsize=12, lsize=10)
    O = d.box(zx + 820, 180, 250, 112, "R 33 Ω → METER → MAKE-UP",
              ["nominale: volume fermo ± 0,2 dB", "picchi caldi tenuti giù (fino a −8 dB)", "a fine corsa: NASTRO 5,5 %,",
               "GROWL 20 % al nominale"], tsize=12, lsize=10)
    chain_h(d, [X, G, T, O])
    d.box(zx + 30, 318, 1040, 66, "",
          ["Niente THAT 218x nel drive (−2 chip rispetto alla v0.3): le manopole sono pot doppi lineari sul segnale, non CV.",
           "Rumore del drive −112,3…−103,7 dBu A-wtd; modulo intero −85,9 dBu A-wtd (target ≤ −80, docs/06 §10). La catena v0.3 col fuzz resta archiviata."],
          "note", align="start", lsize=10.5)
    # zoom kill
    d.raw(f'  <rect x="{zx}" y="420" width="1100" height="190" rx="10" fill="#fff" stroke="{CV}" stroke-width="1.5"/>')
    d.text(zx + 30, 454, "ZOOM — GATE DI KILL A SWITCH (dec. 88, §8.10)", 16, CV, weight=700)
    K1 = d.box(zx + 30, 478, 200, 104, "KILL SWITCH pannello", ["5 interruttori, uno per via", "+5 V via 10k (logica)",
                                                             "l'audio non passa dai contatti"], "ctrl", tsize=12, lsize=10)
    K2 = d.box(zx + 290, 478, 250, 104, "π SPDT classe ADG1434",
               ["serie + shunt a GND da off", "Ron 4,7 Ω · rail ±15 V dedicato", "off-isolation −95 dB a 20 kHz",
                "(serie semplice bocciata: −22…−52)"], tsize=12, lsize=10)
    d.arrow([K1.r, (K2.x - 2, K2.cy)], "cv")
    d.box(zx + 590, 478, 480, 104, "COSA CAMBIA ALL'ASCOLTO",
          ["Taglio netto, come nei preamp della scena dub (benchmark su 9 costruttori).",
           "Il click di hard-cut (2,18 V al summer) è accettato: standard di scena.",
           "In cambio: rumore modulo −85,9 dBu A-wtd (target ≤ −80: PASS 5,9 dB, docs/06 §10).",
           "Con i VCA nei gate era −77,3 dBu: fallito di 10-15 dB sul vecchio target."],
          "note", align="start", lsize=10.5, tsize=12)
    # zoom cella (frammento invariato, traslato)
    frag = open(os.path.join(HERE, "cella-v021.frag"), encoding="utf-8").read()
    d.raw(f'  <g transform="translate(0,520)">\n{frag}\n  </g>')
    d.box(zx, 1210, 1100, 84, "",
          ["Perché non gli OTA LM13700 nelle celle: tetto di stato strutturale 52 mV a f0 → la cella nuda collassava (THD 3-6 %).",
           "Il JFET VCR è un resistore controllato: core a −12 dBu locale, THD 0,005 % nominale / 0,125 % worst — morbida, territorio drive.",
           "Silicio THAT 218x nel modulo: nessuno (kill a switch, drive v0.4 a pot). I vecchi numeri di rumore per cella sono invalidati dal quirk INTEG: vale il −85,9 del modulo."],
          "note", align="start", lsize=11)
    d.legend(1330, [("audio", "audio"), ("cv", "controllo (position/width/kill)"), (FB, "nota evidenziata")])
    d.footer("Fonte: docs/fase2/five-way-module.md (§2, §4.2, §5bis, §8.9-8.10) + sim/five-way/RISULTATI-gate-switch.md + docs/06 §10 + decisioni 85/88/89/99")
    return d.save()


# ---------------------------------------------------------------- FILTRO
def filtro():
    d = Diagram("filtro", 1560, 920, "MODULO FILTRO GLOBALE",
                "maelcum mixer — design v0.2 + D5 (dec. 109-110) · stile Sherman: 2 sezioni full-range 10 Hz–35 kHz, 8 core mono, un percorso per canale (dec. 101)",
                "B1: (a′) OTA o (c-B) pulito — ascolto")
    y = 120
    IN = d.box(40, y, 200, 86, "DAL BACKPLANE", ["4 × send stereo (pre-fader,", "post-EQ canale) + bit di modo",
                                              "0 dBu / +16 worst"], "dark")
    BI = d.box(290, y, 140, 86, "BUFFER IN", ["× 4 sezioni stereo", "(CH1…CH4 L/R)"])
    CO = d.box(480, y - 20, 330, 126, "CORE SVF 4 POLI × 8 (mono)",
               ["2 sezioni 2 poli in cascata (allineamento = q. 64)", "!(a′) OTA LM13700 + partitore 1/30 (dec. 109)",
                "C integratori 1,1 nF · tetto di stato 1,56 V", "(c-B) op-amp + VCA: alternativa pulita (B1)"], lsize=10)
    MX = d.box(860, y, 180, 86, "MUX MODO", ["HPF / OFF (bypass) / LPF", "un percorso per canale", "BBM + ramp 1 ms (dec. 80)"])
    DV = d.box(1090, y - 20, 260, 126, "OVERDRIVE v0.2 (§5ter)",
               ["tosatore in parallelo al pulito (dec. 99)", "1 VCA 218x per cella sulla differenza",
                "law θ^2,5: morde nell'ultimo quarto", "tetto +5,5 dBu · servo DC"], "green", lsize=10)
    RE = d.box(1400, y, 120, 86, "USCITA", ["R serie 33 Ω", "→ return canale"])
    chain_h(d, [IN, BI, CO, MX, DV, RE])
    d.text(1460, y + 104, "0 dBu nom · max +5,5 dBu", 10.5, AUDIO, "middle")
    RS = d.box(560, 262, 390, 110, "RISONANZA + LIMITATORE (dec. 109-110)",
               ["OTA nel summer: 1/Q = Rf · gm_res (Iabc 221 µA × |gres|)", "!limitatore = perdita non lineare dal buffer BP:",
                "!4,7k + 2+2 1N4148 → summer (livello uguale a ogni FREQ)",
                "auto-osc. ~+5 dBu (requisito, dec. 110); nota −6 semitoni = carattere"], "purple", lsize=10)
    d.arrow([(700, RS.y), (700, CO.y + CO.h + 2)], "fb")
    d.box(990, 262, 530, 110, "D5: COSA ARRIVA ALL'OVERDRIVE (sim/filtro/RISULTATI-D5.md)",
          ["Il fischio arriva a −1,5…+2 dBu, non a +8: il chip reale lo comprime.",
           "Fine corsa: 15-20 % di THD sul fischio (griglia dec. 99: 31 %), e sale.",
           "Il primo sporco (1,3-2 %) lo fa il core; programma e fischio insieme.",
           "!Dec. 110: griglia, law RES e oscillazione ACCETTATE come partenza."],
          "note", align="start", lsize=10.5, tsize=12)
    # sezione controllo
    d.raw(f'  <rect x="40" y="410" width="1480" height="300" rx="10" fill="#EEF3F6" stroke="{CV}" stroke-width="1.2"/>')
    d.text(66, 442, "SEZIONE CONTROLLO — 6 knob: FREQ, RES, DRIVE per la sezione HPF e per la LPF (0-5 V)", 15, CV, weight=700)
    cy = 466
    b1 = d.box(66, cy, 215, 90, "LAW SHAPER", ["law Xone:96 (dec. 102):", "expo 20 Hz–20 kHz sul 90 %,",
                                              "10 Hz / 35 kHz negli ultimi 5 %"], tsize=12, lsize=10)
    b2 = d.box(331, cy, 235, 90, "CONVERTER EXPO", ["coppia BJT matched, ΔVbe PTAT:", "Iabc 114 nA…397 µA = 10,6 Hz…37 kHz",
                                                 "deriva ≤ 2,4 % (0-50 °C)"], tsize=12, lsize=10)
    b3 = d.box(616, cy, 235, 90, "DISTRIBUZIONE", ["mirror bufferizzati × 8 + trim/core", "tracking ≤ 1,6 % PASS",
                                                "(mappa invariata col partitore)"], tsize=12, lsize=10)
    b4 = d.box(901, cy, 260, 90, "RAMP BBM (VALIDATA)", ["commutazione modo al picco +18 dBu:", "τ 1 ms = click −8,4 dB",
                                                     "famiglia unica 1 ms (dec. 80)"], tsize=12, lsize=10)
    b5 = d.box(1211, cy, 283, 90, "RES + DRIVE CV", ["RES: law Xone, oscillazione sul 90-100 %", "DRIVE: SPDT per canale sceglie la sezione",
                                                   "attiva (dec. 101) · smoothing 1 ms"], tsize=12, lsize=10)
    chain_h(d, [b1, b2, b3, b4, b5], "cv")
    d.arrow([(b3.cx, cy), (b3.cx, 392), (520, 392), (520, CO.y + CO.h + 2)], "cv")
    d.text(510, 300, "Iabc →", 10, CV, "end")
    d.text(510, 314, "integratori", 10, CV, "end")
    d.box(66, 576, 1428, 112, "VERIFICATO COL MODELLO REALE DELL'LM13700 (fix 2026-10-14: mirror d'uscita completo)",
          ["Core (a) nudo SCARTATO: picco di risonanza sotto −12 dBu, programma 0 dBu −23 dB sul taglio, oscillazione 3,5 ottave sotto FREQ.",
           "Core (a′) 1/30: piccolo segnale esatto (2 poli Q 0,707) · risonanza piena a −30 dBu, +8,5 dB a −10 dBu, ~+1 dB a 0 dBu · THD core 1,5-2 % a 0 dBu.",
           "Rumore core −87,4 dBu A-wtd a fc max · sistema con 4 filtri inseriti e overdrive chiuso −79,0 (target −78: PASS 1,0, docs/06 §11).",
           "Offset in continua ×30 sugli stati: 3,9 mV tipico, ~40 mV col Vos massimo, dentro la corsa del servo (83 mV)."],
          "green", align="start", lsize=10.5, tsize=12)
    d.box(40, 732, 900, 66, "",
          ["RAIL: tutti gli OTA su ±15,0 V ultra-low-noise dal raw ±22 V (pre-reg ±16,5 → LT3045/94, dec. 93) — LM13700 assoluto ±18",
           "BOM v0.1: 20 LM13700 (filter-module §7) + partitori 2,9k/100 Ω + C 1,1 nF C0G/PP matched · overdrive: 8 VCA 218x"],
          "note", align="start", lsize=10.5)
    d.box(980, 732, 540, 66, "",
          ["PROTOTIPO MILLEFORI: 1 core + converter + RES + overdrive",
           "ascolto (a′) contro (c-B): chiude B1 e q. 64; rifinitura B6."],
          "amber", align="start", lsize=10.5)
    d.legend(836, [("audio", "audio (send → return)"), ("cv", "controllo CV / Iabc"),
                   ("fb", "risonanza / nota evidenziata")])
    d.footer("Fonte: docs/fase2/filter-module.md (§2-§5ter, §5quater) + sim/filtro/RISULTATI-D5.md + decisioni 80/89/93/99/101/102/109/110")
    return d.save()


# ---------------------------------------------------------------- CUE
def cue():
    d = Diagram("cue", 1560, 800, "MODULO CUE / CUFFIE",
                "maelcum mixer — design S5 v0.2 (ampli cuffia ridisegnato 2026-10-12) · standard: classe cuffie Pioneer DJM, serve per mixare (dec. 96) · metà L; R identica",
                "nuovo modulo (S5)", GREEN)
    CI = d.box(40, 130, 200, 84, "CUE 1-4 L/R", ["dai canali DJ, slot 1-4", "post-EQ, pre-filter, pre-fader"], "dark")
    MI = d.box(40, 290, 200, 84, "MON IN L/R", ["dal master, buffer [N], slot 5", "post-summing, pre-master-level"], "dark")
    A = d.box(290, 130, 215, 84, "[A] CUE SUMMING", ["massa virtuale, Rf 10k, guadagno −1", "più cue attivi = sommati"])
    Bm = d.box(290, 290, 215, 84, "[B] MON BUFFER", ["follower diretto, guadagno +1", "niente R serie (rumore)"])
    C = d.box(560, 200, 200, 104, "[C] BLEND CUE ↔ MASTER",
              ["pot doppio 10k lineare", "CCW = cue · CW = master", "centro = 50/50 (−6 / −6 dB)"], tsize=12)
    Dv = d.box(810, 212, 160, 80, "[D] LEVEL", ["pot doppio 10k log", "CCW = silenzio vero"])
    E = d.box(1020, 150, 250, 204, "[E] AMPLI CUFFIA v0.2",
              ["OP1612 gain +1, Rf 470 Ω + Cf 330 pF", "Rdrv 1 kΩ verso la rete di bias", "Vbe-multiplier + trimmer: idle 20 mA",
               "finali MJE340/350, Re 6,8 Ω", "limitatori: 126-142 mA (corto 168)", "THD 1 Vrms: 0,005 % su 16 Ω",
               "max su 32 Ω: 2,85 Vrms = 254 mW", "rail ±18 V locali (non sul LN)"], "green", lsize=10.5)
    Fo = d.box(1320, 190, 200, 124, "[F] USCITE", ["Rserie 10 Ω × 4 (fuori anello)", "relay DPDT × 2",
                                                 "a riposo = cuffia muta", "→ 2 JACK stereo in parallelo"], "dark")
    d.arrow([CI.r, (A.x - 2, A.cy)])
    d.arrow([MI.r, (Bm.x - 2, Bm.cy)])
    d.arrow([A.r, (530, A.cy), (530, 232), (C.x - 2, 232)])
    d.arrow([Bm.r, (530, Bm.cy), (530, 272), (C.x - 2, 272)])
    chain_h(d, [C, Dv, E, Fo])
    d.text(1145, 372, "stesso mix su entrambe le uscite", 10.5, "#777", "middle")
    Gc = d.box(1320, 400, 200, 110, "[G] CONTROLLO LOCALE",
               ["supervisore rail + timer 1,5-2 s", "power-off: relay aperti < 10 ms", "analogico, niente MCU"], "ctrl", tsize=12, lsize=10)
    d.arrow([Gc.t, (Fo.cx, Fo.y + Fo.h + 2)], "cv")
    d.box(40, 430, 620, 130, "POLARITÀ E FASE DEL BLEND",
          ["Cue summer −1 e MON +1 (il summing master inverte a monte): al centro i due lati SOMMANO.",
           "Fase: il percorso master attraversa la banca 5-way (ritardi fino a ~2,5 ms a 90 Hz), il cue no.",
           "Cue di un canale già in programma, al centro del blend = comb filtering udibile.",
           "Comportamento normale dei crossfade cue/master (DJM, Xone): accettato, non compensato."],
          "note", align="start", lsize=10.5)
    d.box(700, 430, 580, 130, "GLOBAL_MUTE: IL CUE NON LO ASCOLTA",
          ["Scelta di Filippo (2026-10-02): durante power-on/off e guasti rail del master",
           "la cuffia resta viva: si continua a preascoltare anche se il master è muto.",
           "I transienti PROPRI del modulo li toglie [G] con i relay d'uscita.",
           "Blend non segue la manopola master (stile DJM-900NXS2)."],
          "note", align="start", lsize=10.5)
    d.box(40, 590, 1480, 84, "PSU LOCALE + NUMERI",
          ["raw ±22 V → pre-reg ±16,5 → LT3045/94 → ±15,0 V LN per [A][B][C][D] · raw ±27 V → LM317/337 → ±18 V audio per [E] (~61 mA a riposo, ≤ ~340 mA col clamp su entrambi i canali) · +5 V dal bus per [G]",
           "Rumore al jack −114,5 dBu A-wtd (target −90) · isolamento blend agli estremi −116 dB · stabilità: nessun picco ad anello chiuso, quadra pulita fino a 2 nF di cavo · nessuna capacità su OUTA prima della Rserie"],
          "note", align="start", lsize=10.5)
    d.legend(716, [("audio", "audio"), ("cv", "controllo locale")])
    d.footer("Fonte: docs/fase3/sistema-cue.md v0.2 (§2-§9) + sim/system/RISULTATI-cue.md (Test 1-8) + master-out.md ADDENDUM [N] + decisioni 90b/94b/96")
    return d.save()


# ---------------------------------------------------------------- MIC / MONO
def mic_mono():
    d = Diagram("mic-mono", 1610, 930, "MODULI MIC e MONO — due moduli separati",
                "maelcum mixer — architettura v0.1 (2026-10-13, dec. 97): comandi = GAIN, EQ 2 bande, 4 pot send, 1 LED · massimo 4 moduli nel sistema",
                "nuovo (dec. 97)", GREEN)

    def banda(y, etichetta, front, msum):
        d.text(40, y - 12, etichetta, 12, "#666", weight=700)
        bx = [d.box(40 + k * 210, y, 175, 96, t, ln, kind) for k, (t, ln, kind) in enumerate(front)]
        chain_h(d, bx)
        cy = bx[0].cy
        EQ = d.box(705, y, 200, 96, "EQ 2 BANDE", ["LOW shelf ~120 Hz", "HIGH ~5 kHz", "−∞ → 0 → +6 (celle serie)"])
        d.arrow([bx[-1].r, (EQ.x - 2, cy)])
        d.dot(670, cy)
        LED = d.box(450, y + 126, 240, 88, "LED (uno, cambia colore)",
                    ["presa pre-EQ [BLOCCATO]", "verde ≥ −6 · giallo ≥ +11 dBu", "rosso = clip ≥ +17 (latch) [PROVV]"], "ctrl", tsize=12)
        d.arrow([(670, cy), (670, LED.y - 2)], "cv")
        DR = d.box(985, y, 180, 96, "DRIVER L + DRIVER R", ["OPA1612, due buffer separati", "mai hard-short L/R"])
        MS = d.box(1200, y, 170, 96, "→ MASTER SUM", [msum, "multidrop, 7 contributori"], "dark")
        d.arrow([EQ.r, (DR.x - 2, cy)])
        d.dot(950, cy)
        d.arrow([DR.r, (MS.x - 2, cy)])
        AS = d.box(985, y + 126, 180, 88, "SEND × 4 (pot)", ["uno per bus FX, 10k passivo", "−∞ … 0 dB, presa post-EQ", "come in un live mixer"])
        INJ = d.box(1200, y + 126, 170, 88, "INIEZIONE × 4", ["OPA1654 quad", "2 × R 10k (net L e R)"])
        BUS = d.box(1405, y + 126, 165, 88, "→ BUS FX 1-4", ["net multidrop", "backplane slot 2-5"], "dark")
        d.arrow([(950, cy), (950, AS.cy), (AS.x - 2, AS.cy)])
        chain_h(d, [AS, INJ, BUS])
        GM = d.box(725, y + 126, 200, 88, "MUTE GLOBALE (c9)", ["apre le mandate a power-on/off", "(dec. 94b) — non è un comando", "di pannello"], "ctrl", tsize=12)
        d.arrow([GM.b, (GM.cx, y + 230), (INJ.cx, y + 230), (INJ.cx, INJ.y + INJ.h + 2)], "cv")

    banda(140, "MODULO MIC — front-end su ±15 V LN",
          [("XLR + PROTEZIONE", ["bilanciato, NO phantom", "RFI, R 10 + clamp ai rail", "Zin 2,26k · CM 47k/gamba"], "dark"),
           ("INA +30 dB FISSO", ["coppia OPA1612", "Rf 2×499 · Rg 32,4", "+ passa-alto 60 Hz (dec. 97)"], "std"),
           ("GAIN 0 … +30 dB", ["OPA1654, pot 5k", "totale 29,5 … 59,3 dB"], "std")],
          "net MSUM6")
    banda(420, "MODULO MONO — dominio ±18 V",
          [("JACK + PROTEZIONE", ["mono, tollera +18 dBu", "R 1k + clamp + TVS", "C film 100 nF (1,6 Hz)"], "dark"),
           ("BUFFER FET", ["OPA1654 unity", "Zin 1 MΩ"], "std"),
           ("GAIN −∞ → 0 → +10", ["pot 10k passivo", "+ make-up +10 dB"], "std")],
          "net MSUM7")
    d.box(40, 690, 760, 132, "NUMERI SIMULATI (sim/mic/)",
          ["MIC: EIN −126,5 dBu su 150 Ω, uguale a ogni posizione del GAIN · passa-alto −3,1 dB a 60 Hz · −0,04 dB a 35 kHz",
           "MIC: CMRR 74 dB con sorgente sbilanciata di 10 Ω · overload 300 mV rms al microfono (~138 dB SPL su SM58)",
           "MIC: uscita modulo −97,3 / −90,0 / −69,3 dBu A-wtd a 30 / 38 / 59 dB · sistema entro −78 fino a ~46 dB di gain",
           "MONO: banda −0,19 dB a 10 Hz, −0,08 a 35 kHz · uscita −101,3 dBu A-wtd · send chiuso: −111,2 dBu A-wtd sul bus"],
          "note", align="start", lsize=10.5)
    d.box(830, 690, 740, 132, "DECISIONE 97 (Filippo, 2026-10-13) E DOMANDE APERTE",
          ["Due moduli separati. Su ciascuno solo: GAIN, EQ 2 bande, 4 pot send, 1 LED di metering (rosso = clip).",
           "Massimo 4 moduli MIC/MONO nel sistema: i bus FX arrivano a 12 contributori (caso già verificato).",
           "!Aperto: soglie del LED tricolore (verde −6 / giallo +11 / rosso +17 dBu, sistema-metering §1)",
           "!Aperto: «massimo 4» letto come 4 in totale tra MIC e MONO"],
          "note", align="start", lsize=10.5)
    d.legend(864, [("audio", "audio"), ("cv", "controllo / LED")])
    d.footer("Fonte: docs/fase4/mic-mono-moduli.md v0.1 (2026-10-13) + sim/mic/RISULTATI-mic-mono.md + SPECIFICA §8 + decisioni 36/37/91/94/95/97")
    return d.save()


# ---------------------------------------------------------------- SCHEMA TOTALE
def schema_totale():
    d = Diagram("schema-totale", 1720, 1600, "SCHEMA FUNZIONALE TOTALE",
                "maelcum mixer — percorso del segnale da tutti gli ingressi a tutte le uscite · stato decisioni 1-110 · un canale DJ disegnato, gli altri tre identici",
                "decisioni 1-110", FB)
    g, p = "jgreen", "jgrey"

    def bx(x, y, w, h, t, lines=(), kind=g, ts=12.5, ls=10.5):
        return d.box(x, y, w, h, t, lines, kind, tsize=ts, lsize=ls)

    K = "k"
    # ===================== CANALE DJ (colonna sinistra)
    d.text(40, 112, "CANALE DJ 1 (2, 3, 4 identici)", 13, INK, weight=700)
    LN = d.circle(110, 175, 46, ["LINE", "RCA"])
    PH = d.circle(250, 175, 46, ["PHONO", "MM"])
    PP = bx(185, 250, 130, 50, "phono preamp", ["RIAA 42 dB"], p, 11.5, 10)
    SEL = bx(55, 330, 220, 56, "selettore line/phono")
    d.arrow([LN.b, (110, SEL.y - 2)], K)
    d.arrow([PH.b, (PP.cx, PP.y - 2)], K)
    d.arrow([PP.b, (PP.cx, SEL.y - 2)], K)
    GA = bx(55, 416, 220, 56, "GAIN", ["−∞ … 0 … +10 dB"])
    EQ = bx(55, 502, 220, 70, "EQ ISOLATOR 4 bande", ["silenzio … 0 … +6 dB", "bande in parallelo (dec. 105)"])
    chain = [SEL, GA, EQ]
    for a, b in zip(chain, chain[1:]):
        d.arrow([a.b, (b.cx, b.y - 2)], K)
    sx, sy = 165, 610                       # nodo split post-EQ
    d.arrow([EQ.b, (sx, sy)], K, head=False)
    d.o.append(f'  <circle cx="{sx}" cy="{sy}" r="4.5" fill="#333"/>')
    FS = bx(55, 650, 220, 56, "switch HPF / OFF / LPF")
    d.arrow([(sx, sy), (sx, FS.y - 2)], K)
    FI = bx(330, 630, 230, 96, "MODULO FILTRO", ["globale, 8 core OTA (a′)", "FREQ · RES · DRIVE × 2 sezioni",
                                                  "overdrive v0.2"], ts=13)
    d.arrow([(FS.x + FS.w, 668), (FI.x - 2, 668)], K)
    d.arrow([(FI.x, 692), (FS.x + FS.w + 2, 692)], K)
    d.text(302, 662, "send", 9.5, "#555", "middle")
    d.text(302, 708, "return", 9.5, "#555", "middle")
    ME = bx(55, 740, 220, 46, "meter DJ", [], p, 12)
    FA = bx(55, 816, 220, 56, "FADER", ["−∞ … 0 dB"])
    DO = bx(55, 902, 220, 46, "driver d'uscita", [], p, 12)
    for a, b in zip([FS, ME, FA, DO], [ME, FA, DO]):
        d.arrow([a.b, (b.cx, b.y - 2)], K)
    # cue e fx-send dal nodo split
    CU = bx(330, 470, 230, 56, "CUE (pulsante)", ["pre-fader, pre-filtro"])
    FX = bx(330, 548, 230, 66, "MICRO-MODULO FX-SEND", ["EQ2 · LEVEL · assign S1-S4"], ts=12)
    d.arrow([(sx, sy), (300, sy), (300, CU.cy), (CU.x - 2, CU.cy)], K)
    d.arrow([(300, sy), (300, FX.cy), (FX.x - 2, FX.cy)], K)
    # DJ bus
    DJ = bx(55, 990, 220, 56, "DJ BUS", ["somma dei 4 canali"], p)
    d.arrow([DO.b, (DJ.cx, DJ.y - 2)], K)
    for i, yy in enumerate((1004, 1018, 1032)):
        d.arrow([(330, yy), (DJ.x + DJ.w + 2, yy)], K)
    d.text(338, 1022, "dai canali 2, 3, 4", 10, "#555")
    # 5-way
    FW = bx(55, 1080, 220, 120, "5-WAY dub preamp", ["kill × 5 vie (switch)", "EQ creativo 5 celle",
                                                    "GROWL + NASTRO", "meter · make-up"], ts=13)
    d.arrow([DJ.b, (FW.cx, FW.y - 2)], K)
    # ===================== MIC / MONO
    d.text(660, 112, "MIC e MONO (fino a 4 moduli)", 13, INK, weight=700)
    MI = d.circle(720, 175, 46, ["MIC", "XLR"])
    MO = d.circle(880, 175, 46, ["MONO", "jack"])
    MIM = bx(650, 250, 140, 96, "MIC", ["gain +30…+59", "HPF 60 Hz", "EQ2 · 4 send"], ts=12.5, ls=10)
    MOM = bx(810, 250, 140, 96, "MONO", ["gain −∞…+10", "EQ2 · 4 send"], ts=12.5, ls=10)
    d.arrow([MI.b, (MIM.cx, MIM.y - 2)], K)
    d.arrow([MO.b, (MOM.cx, MOM.y - 2)], K)
    # ===================== FX
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
    RG = bx(1130, 600, 160, 66, "GAIN + EQ2", ["−∞ … 0 … +20 dB"])
    d.arrow([RT.b, (RG.cx, RG.y - 2)], K)
    RR = bx(1130, 696, 160, 76, "MATRICE REROUTE", ["16 VCA, self ammesso", "pre-fader"], ts=12)
    d.arrow([RG.b, (RR.cx, RR.y - 2)], K)
    d.arrow([RR.l, (745, RR.cy), (745, FB_.y + FB_.h + 2)], "fb")
    d.text(760, RR.cy - 8, "feedback verso i 4 bus FX", 10, FB)
    RF = bx(1130, 802, 160, 56, "FADER ritorno", [])
    d.arrow([RR.b, (RF.cx, RF.y - 2)], K)
    # ===================== MASTER SUM
    MS = bx(55, 1250, 1300, 56, "MASTER SUM", ["7 ingressi: 5-way · 4 ritorni FX · mic · mono (dec. 94a)"], p, 13)
    d.arrow([FW.b, (FW.cx, MS.y - 2)], K)
    d.arrow([RF.b, (RF.cx, MS.y - 2)], K)
    d.arrow([MIM.l, (620, MIM.cy), (620, MS.y - 2)], K)
    d.arrow([MOM.r, (997, MOM.cy), (997, MS.y - 2)], K)
    d.text(628, 1236, "mic", 9.5, "#555")
    d.text(1005, 1236, "mono", 9.5, "#555")
    # ===================== USCITE
    ML = bx(55, 1350, 200, 56, "MASTER LEVEL", ["−∞ … 0 … +6 dB"])
    BL = bx(300, 1350, 200, 56, "BOOTH LEVEL", ["−∞ … 0 dB"])
    RA = bx(545, 1350, 200, 56, "attenuatore REC", ["fisso"], p)
    MB = bx(790, 1350, 200, 56, "buffer MON", ["verso il CUE"], p)
    for b in (ML, BL, RA, MB):
        d.arrow([(b.cx, MS.y + MS.h), (b.cx, b.y - 2)], K)
    for b, lab in ((ML, ["MASTER", "XLR"]), (BL, ["BOOTH", "XLR"]), (RA, ["REC"])):
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
    d.footer("Fonte: SPECIFICA.md + docs/fase1-fase4 · comandi dal pannello (sistema-comandi.md) · meter: 8 barre (sistema-metering.md), non disegnate")
    return d.save()


# ---------------------------------------------------------------- PSU
def psu():
    d = Diagram("psu", 1560, 960, "SISTEMA PSU — ALIMENTAZIONE",
                "maelcum mixer — alimentatore ESTERNO con pre-regolatori (dec. 113) · regolazione finale nei moduli (dec. 93) · 2 ventole a termostato (dec. 112)",
                "box esterno · toroidale ~270 VA", GREEN)
    # i due contenitori: box esterno e mixer, uniti dal cavo
    for x, w, label in ((20, 885, "BOX ESTERNO (dec. 113) — vicino al banco, a terra su piedini"),
                        (950, 590, "MIXER — modulo PSU-IN e regolazione nei moduli")):
        d.raw(f'  <rect x="{x}" y="88" width="{w}" height="792" rx="10" fill="none" '
              'stroke="#888" stroke-width="1.5" stroke-dasharray="6 4"/>')
        d.text(x + 12, 104, label, 11, "#555", weight=700)
    RE = d.box(40, 130, 150, 90, "RETE 230 V", ["IEC + filtro EMC", "interruttore bipolare"], "dark")
    IN = d.box(220, 120, 210, 110, "INGRESSO RETE", ["fusibile T2 A [PROVV]", "NTC 10-20 Ω anti-inrush",
                                                  "+ relè di bypass dopo 0,5 s"])
    TR = d.box(470, 110, 190, 130, "TOROIDALE ~270 VA", ["unico, 4 secondari", "schermo primario/secondari",
                                                       "termico integrato", "(dec. 106/111/115)"], "green")
    chain_h(d, [RE, IN, TR])
    d.box(690, 110, 200, 130, "CALORE NEL BOX (§2.8)", ["~48 W · ~63 W a rete +10 %", "aletta Rθ ≤ 0,6 K/W",
                                                      "senza ventola", "chiuso: pioggia e polvere"],
          "note", tsize=12, lsize=10)
    d.box(965, 110, 560, 130, "CAVO ≤ 2 m E CONNETTORE (§3)",
          ["20 conduttori da 0,5 mm² + schermo · circolare metallico a vite, IP65, classe 24 poli",
           "±22 audio 2+2 · ±19 LN 1+1 · ±27 [M] 1+1 · +5 2 · V_FAN 1+1 · AC_OK 1 · PE 1",
           "ogni 0 V su conduttori propri fino alla stella · cadute ≤ 60 mV · marca: voce 40"],
          "note", tsize=12, lsize=10.5)
    rows = [
        ("W1 2×21 V 4,0 A", ["ponte + bulk 2 × 15 mF", "T5 A per ramo"],
         "LDO MOSFET ±22,0 V", ["limite 2,7 A · soft-start 0,3 s", "ripple al mixer ≤ 3 mV pp"],
         ["PSU-IN: TVS · T2,5 A · 2,2 mF", "modulo: LM317/337 → 19,2 V + cap mult. → ±18"],
         ["canali · 5-way · FX · filtro · FX-SEND", "CUE · mic/mono · moduli opzionali",
          "!~1,5 A base · ~1,8 A con gli opzionali"]),
        ("W2 2×18 V 1,0 A", ["ponte + bulk 2 × 10 mF", "T1,25 A"],
         "LDO MOSFET ±19 V", ["limite 1,1 A", "ripple al mixer ≤ 1 mV pp"],
         ["PSU-IN: TVS · T1 A · 1 mF", "modulo: pre-reg ±16,5 → LT3045/94 → ±15,0",
          "+ 78L15/79L15 ±15 per gli switch"],
         ["phono · mic · CV · meter · CUE", "OTA filtro · switch kill/assign", "!picco LN ~0,48 A"]),
        ("W3 2×20 V 0,4 A", ["ponte + bulk 2 × 4,7 mF", "T630 mA"],
         "RAW ±27 V [M]", ["non regolato nel box", "30,3 V a rete +10 %"],
         ["PSU-IN: TVS · T500 mA · 1 mF", "master: statici HV + LDO locali"],
         ["solo master out: +24 dBu reali", "!~130-170 mA"]),
        ("W4 9 V 2,5 A", ["ponte + bulk 10 mF", "T3,15 A"],
         "+5 V E V_FAN", ["+5: LM1084/LM2940 nel box", "V_FAN: raw W4 non regolato"],
         ["PSU-IN: TVS · T2 A · 1 mF sul +5", "V_FAN: T500 mA → driver ventole"],
         ["LED dei meter · logiche · relè", "supervisor · 2 ventole", "!+5 worst 1,3 A · ventole 0,3 A"]),
    ]
    d.text(790, 280, "pre-regolazione nel box", 10.5, "#777", "middle")
    d.text(1095, 280, "nel mixer: PSU-IN e modulo", 10.5, "#777", "middle")
    d.text(1390, 280, "chi lo usa · corrente", 10.5, "#777", "middle")
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
          ["rete: interruttore bipolare · T2 A · NTC + relè di bypass",
           "secondari: fusibili lenti prima dei ponti",
           "   (T5 A · T1,25 A · T630 mA · T3,15 A) · termico",
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
                "scatta in ≤ 12,7-21,4 ms, prima che i regolatori locali escano (≥ 25,9 ms) · anche sotto ~−21 % di rete"],
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
           "calore nel mixer ~83 W · ~97 W con opzionali", "aria interna ~+3 K sopra l'ambiente"],
          "note", align="start", lsize=10, tsize=12)
    d.legend(910, [("audio", "potenza (rail)"), ("cv", "mute e supervisione"), (AMBER, "regolazione nel mixer"),
                   ("dashed", "contenitore")])
    d.footer("Fonte: docs/fase3/sistema-psu-esterno.md v0.1 (§1-§5) + sistema-psu.md REV dec. 113 + decisioni 90/93/106/111/112/113/115 + sim/system/psu-*.cir",
             "2026-10-21")
    return d.save()


# ---------------------------------------------------------------- METERING
def metering():
    d = Diagram("metering", 1560, 960, "SISTEMA METERING — BARRE LED A ZONE",
                "maelcum mixer — design S4 v0.1 · ballistica Pioneer DJM (dec. 81) · soglie assolute (dec. 90): fondo scala +24 dBu uguale su ogni barra",
                "8 barre + LED mic/mono", GREEN)
    # punti di presa
    d.text(40, 122, "PUNTI DI PRESA (SPECIFICA §11, bloccati)", 13, INK, weight=700)
    taps = [("MASTER L/R", ["post master level,", "pre stadio HV", "2 barre da 20 segm."]),
            ("DJ × 4", ["post filtro/overdrive,", "pre-fader", "4 barre da 10 segm."]),
            ("5-WAY", ["post drive, pre", "master sum (g × 2)", "1 barra da 10 segm."]),
            ("RITORNO FX", ["post gain/EQ2,", "pre-fader", "1 barra da 10 segm."]),
            ("MIC / MONO", ["dopo il preamp,", "prima dell'EQ2", "solo LED tricolore"])]
    tb = []
    for i, (t, ln) in enumerate(taps):
        tb.append(d.box(40 + i * 300, 136, 270, 86, t, ln, "dark", tsize=12.5, lsize=10.5))
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
                                             "worst ~0,5 A su +5 V", "", "master purple: sensing", "dello stadio HV [aperto]"], "note", tsize=12, lsize=10)
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
    ref = d.box(40, 630, 720, 110, "ALBERO DEI RIFERIMENTI CONDIVISO (§5)",
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
          ["BOM di massima: 10 LM3915 · ~12 OPA1612 · 2 LM339 · ~103 LED + 8 purple · ~50-80 € [molto PROVVISORIA]. Alternativa a LM3915: ladder di LM339 (10× i chip).",
           "Niente meter su booth, rec, cuffie e mandate (SPECIFICA §11). Aperti (voce 40 / q54): posizione delle barre, 10 o 20 segmenti per zona,",
           "luminosità 2 o 5 mA, purple del master a doppio criterio o uno solo, procedura di calibrazione con toni a livelli noti."],
          "note", align="start", lsize=10.5, tsize=12)
    d.legend(892, [("audio", "segnale"), ("cv", "riferimenti / logica")])
    d.footer("Fonte: docs/fase3/sistema-metering.md v0.1 (§1-§9) + sim/system/meter-*.cir + sim/meter/RISULTATI-peak-det.md + decisioni 81/90/97")
    return d.save()


if __name__ == "__main__":
    warn = []
    for f in (schema_totale, canale, fx, fx_send, master, five_way, filtro, cue, mic_mono, psu, metering):
        warn += f()
    print("scritti 11 SVG in", HERE)
    for w in warn:
        print("ATTENZIONE:", w)
