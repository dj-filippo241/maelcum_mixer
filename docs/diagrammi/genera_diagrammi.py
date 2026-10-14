#!/usr/bin/env python3
# Genera i diagrammi a blocchi SVG dei moduli del maelcum mixer.
# Uso:  python3 genera_diagrammi.py      (scrive i .svg in questa cartella)
# I contenuti vengono dai design doc: quando un doc cambia, si aggiorna
# la funzione del modulo qui sotto e si rilancia lo script.
# Il dettaglio della cella parametrica 5-way sta in cella-v021.frag
# (frammento SVG a mano del 2026-09-28, invariato dal design v0.2.1).
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "2026-10-12"

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
        for mid, col, size in (("ar", AUDIO, 7), ("arb", FB, 7), ("arw", CV, 6)):
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
                              "fb": (FB, 2.2, "arb", None)}[kind]
        d = "M " + " L ".join(f"{px:g} {py:g}" for px, py in pts)
        ds = f' stroke-dasharray="{dash}"' if dash else ""
        me = f' marker-end="url(#{mid})"' if head else ""
        self.o.append(f'  <path d="{d}" stroke="{col}" stroke-width="{sw:g}" fill="none"{ds}{me}/>')

    def dot(self, x, y):
        self.o.append(f'  <circle cx="{x:g}" cy="{y:g}" r="5" fill="{AUDIO}"/>')

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

    def footer(self, s):
        self.text(40, self.h - 22, s + " · " + DATA, 10.5, "#999")
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
    pots = d.box(660, 84, 220, 32, "", ["4 pot doppi lin. + contatto fondo corsa"], "ctrl", lsize=11)
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
          ["target ≤ −80 dBu A-wtd (dec. 89) · misurato −90,3 (EQ 82 % + GAIN VCA 18 %)"], "note", align="start")
    d.legend(826, [("audio", "percorso audio (livelli annotati in rosso)"), ("cv", "controllo CV / logiche"),
                   (FB, "modifica rispetto al diagramma del 2026-09-28")])
    d.footer("Fonte: docs/fase1/cdj-line-channel.md v0.4 (§3.5 REV dec. 91a) + eq-serie-v0.3.md BETA-3 + phono-stage.md + gain-staging-sheet.md §2 · 0 dBu = 0,775 Vrms · K4: level_in × gain ≤ +23 dBu")
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
    DRV = d.box(510, y, 180, 86, "DRIVER + PAD", ["buffer low-Z ≤ 50 Ω (OPA1612)", "pad −20 / −10 / 0 dB (DIP)"])
    PRO = d.box(735, y, 170, 86, "PROTEZIONE", ["R serie 100 Ω + TVS ≤ 5 pF", "banda 40 kHz verificata §8.4"])
    JS = d.box(950, y, 150, 86, "JACK SEND n", ["→ pedale (L/R)", "mono = sum 2 × 10k"], "dark")
    PED = d.box(1145, y, 110, 86, "PEDALE", ["esterno", "−20…+18 dBu"], "dashed")
    JR = d.box(1300, y, 180, 86, "JACK RETURN n", ["← pedale (L/R, stereo-capable)"], "dark")
    chain_h(d, [src, SUM, DRV, PRO, JS, PED, JR])
    d.text(SUM.cx + 14, y + 104, "margine 7,3 V al clamp ±16,5", 10, AUDIO)
    PDC = d.box(1290, 290, 200, 84, "PROT + DC CONTROL", ["DC servo integrato VALIDATO", "corner 0,05-0,5 Hz, nulling 84 dB"])
    BUF = d.box(1290, 404, 200, 66, "BUFFER HI-Z", ["JFET, Zin ≥ 1 MΩ (bias 1 MΩ §8.4)"])
    GAI = d.box(1290, 500, 200, 84, "GAIN VCA 218x", ["−∞ → 0 → +20 dB", "!senza limite: K4 = operatore (dec. 84)"])
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
    d.text(SUM.cx + 14, 292, "loop di feedback: verso i SUMMING dei 4 bus, INCLUSO il proprio — dry loop senza pedale = clamp ±16,5 V, disciplina K4", 10.5, FB)
    CVB = d.box(300, 400, 300, 120, "CATENA CV REROUTE",
                ["pot → CV buffer → shaper a tratti", "(famiglia law filtro, dec. 70) →",
                 "smoothing 1 ms (dec. 80) →", "CV 6,1 mV/dB ai VCA (dec. 92), 1 per coppia L/R"], "ctrl")
    d.arrow([CVB.r, (MAT.x - 2, CVB.cy)], "cv")
    d.box(520, 720, 970, 58, "",
          ["±18 V audio (summing/driver/VCA) · ±15 V LN (CV/shaper/servo) · VCA 218x = SINGLE: 20 chip in questo modulo (16 reroute + 4 gain)",
           "mixer ~28-30 chip · rotta clone CoolAudio V2181L, acquisti dopo il prototipo M4L (voce 37) · mute dei send: GLOBAL_MUTE sui FX-SEND (dec. 94b)"],
          "note", align="start", lsize=11)
    d.legend(826, [("audio", "audio"), ("fb", "feedback (matrice reroute)"), ("cv", "controllo CV"),
                   ("dashed", "esterno al mixer")])
    d.footer("Fonte: docs/fase1/fx-module.md v0.3-WIP (§2/§7/§8.3-8.5) + fx-send-module.md + sim/fx/ · livelli worst: summing +21,5 dBu, loop +20,2 dBu (mai ai rail)")
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
    LEV = d.box(755, 178, 175, 80, "LEVEL", ["pot doppio 10k log", "−∞ … 0 dB (mai gain positivo)"])
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
    d.footer("Fonte: docs/fase1/fx-send-module.md v0.1-WIP (§2-§6) + sistema-backplane.md (classe FX-SEND) + sim/fx/RISULTATI-send-chain-71A.md + decisioni 91/94b/95")
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
              ["!rail OPA1612 flottanti OUT ± 5,3 V (d. 86)", "stringa 9 × 1N4148 + pass MJE340/350",
               "+25,4…+25,6 dBu · THD 0,00012 % a +24", "corto 106 mA auto-limitato · servo DC 30 µV"], tsize=12, lsize=10)
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
                "maelcum mixer — design v0.3: kill a switch (dec. 88), drive validato (dec. 82/87), celle v0.2.1 · ordine BLOCCATO: kill → EQ → drive → meter",
                "drive v0.3 + kill a switch", GREEN)
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
    DR = d.box(x, 790, w, 130, "DRIVE v0.3 VALIDATO",
               ["«prima nastro, ultimi 20 % fuzz» (dec. 82)", "law 0 / +7 / +12 / +16 dB a θ 0/50/80/100 %",
                "griglia §5.3 confermata da Filippo (dec. 87)", "dettaglio in alto a destra"], "green")
    ME = d.box(x, 950, w, 60, "METER pickup", ["detector condiviso · release ~0,3 s (dec. 81)"])
    MU = d.box(x, 1040, w, 60, "MAKE-UP +6 dB + TRIM", ["uscita 0 dBu nominale"])
    OUT = d.box(x, 1130, w, 56, "→ MASTER SUM (MSUM1, backplane)", [], "dark", tsize=12.5)
    chain_v(d, [BUSI, PAD, KB, EQ, DR, ME, MU, OUT])
    # zoom drive
    zx = 420
    d.raw(f'  <rect x="{zx}" y="100" width="1100" height="300" rx="10" fill="#fff" stroke="{GREEN}" stroke-width="1.5"/>')
    d.text(zx + 30, 134, "ZOOM — DRIVE v0.3 (tutto DC-coupled, per lato)", 16, GREEN, weight=700)
    d.text(zx + 30, 154, "soglie fisse, gain variabile: la manopola spinge il segnale dentro due saturatori in cascata · polarità totale non invertente", 11.5, "#666")
    V = d.box(zx + 30, 180, 230, 112, "[1] VCA THAT 218x",
              ["gain pulito, law dB-lineare", "θ 0/50/80/100 % =", "−9,4 / −2,4 / +2,6 / +6,6 dB",
               "a θ0 attenua PRIMA del saturatore"], tsize=12, lsize=10)
    T = d.box(zx + 300, 180, 230, 112, "[2a] NASTRO",
              ["JFET common-source nudo", "ginocchio morbido 0,7-1,0 Vp", "asimmetrico: + comprime, − aperto",
               "entra da θ ≈ 50-65 %"], "amber", tsize=12, lsize=10)
    FZ = d.box(zx + 570, 180, 230, 112, "[2b] FUZZ",
               ["diff pair PNP single-ended", "clip duro asimmetrico ±1,9 V", "ceiling ±2,79 V (+11,9 dBu)",
                "entra da θ ≈ 80-100 %"], "amber", tsize=12, lsize=10)
    RC = d.box(zx + 840, 180, 230, 112, "[3] RECOVERY + SERVO DC",
               ["invertente 2k/2k (OPA1612)", "servo 2 op-amp classe OPA2134", "fc 0,31 Hz, residuo −65 µV",
                "→ meter → make-up"], tsize=12, lsize=10)
    chain_h(d, [V, T, FZ, RC])
    CVD = d.box(zx + 30, 322, 500, 56, "", ["pot DRIVE 0-5 V → shaper PWL 3 tratti → CV 6,1 mV/dB (dec. 92) → smoothing 1 ms (dec. 80)"], "ctrl", lsize=10.5)
    d.arrow([(V.cx, CVD.y), (V.cx, V.y + V.h + 2)], "cv")
    d.text(zx + 560, 346, "Rumore drive: VCA dominante (I/V 10k, −104 dBV).", 10.5, "#666")
    d.text(zx + 560, 362, "D5 (drive × risonanza filtro) resta aperto: dopo l'ascolto q. 70.", 10.5, FB)
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
           "In cambio: rumore modulo −83,9 dBu A-wtd a drive 0 (target ≤ −80: PASS 3,9 dB).",
           "Con i VCA nei gate era −77,3 dBu: fallito di 10-15 dB sul vecchio target."],
          "note", align="start", lsize=10.5, tsize=12)
    # zoom cella (frammento invariato, traslato)
    frag = open(os.path.join(HERE, "cella-v021.frag"), encoding="utf-8").read()
    d.raw(f'  <g transform="translate(0,520)">\n{frag}\n  </g>')
    d.box(zx, 1210, 1100, 84, "",
          ["Perché non gli OTA LM13700 nelle celle: tetto di stato strutturale 52 mV a f0 → la cella nuda collassava (THD 3-6 %).",
           "Il JFET VCR è un resistore controllato: core a −12 dBu locale, THD 0,005 % nominale / 0,125 % worst — morbida, territorio drive.",
           "Silicio THAT 218x nel modulo: 2 (solo i drive). I vecchi numeri di rumore per cella (−121,7 dBu) sono invalidati dal quirk INTEG: vale il −83,9 del modulo."],
          "note", align="start", lsize=11)
    d.legend(1330, [("audio", "audio"), ("cv", "controllo (position/width/drive/kill)"), (FB, "modifica rispetto al 2026-09-28")])
    d.footer("Fonte: docs/fase2/five-way-module.md (§2, §4.2, §5.2-5.3, §8.9-8.10) + sim/five-way/RISULTATI-gate-switch.md + RISULTATI-module-noise-v031.md + decisioni 82/85/87/88/89")
    return d.save()


# ---------------------------------------------------------------- FILTRO
def filtro():
    d = Diagram("filtro", 1560, 900, "MODULO FILTRO GLOBALE",
                "maelcum mixer — design v0.2 + v0.3-WIP · stile Sherman: 2 sezioni full-range 10 Hz–35 kHz (dec. 74), 8 core mono, risonanza → auto-oscillazione",
                "q. 70: carattere (a) OTA vs pulito (c-B) — ascolto")
    y = 120
    IN = d.box(40, y, 200, 86, "DAL BACKPLANE", ["4 × send stereo (pre-fader,", "post-EQ canale) + 2 bit modo",
                                              "0 dBu / +16 worst"], "dark")
    BI = d.box(300, y, 150, 86, "BUFFER IN", ["× 4 sezioni stereo", "(CH1…CH4 L/R)"])
    CO = d.box(510, y - 20, 330, 126, "CORE SVF 4 POLI × 8 (mono)",
               ["2 sezioni 2-poli in cascata (Butterworth o", "Bessel/LR — allineamento = q. 64) · HP e LP",
                "!(a) OTA LM13700 = carattere (~1 % THD morbido", "!a 0 dBu) OPPURE (c-B) op-amp + VCA = pulito"], lsize=10)
    MX = d.box(900, y, 190, 86, "MUX MODO", ["HPF / OFF (bypass) / LPF", "BBM + ramp 1 ms (dec. 80)",
                                           "!single-path vs serie = q. 63"])
    DV = d.box(1150, y, 170, 86, "DRIVE (per sez.)", ["referenza: Sherman", "Filterbox (dec. 82)",
                                                  "!D5 dopo l'ascolto q. 70"], "dashed")
    RE = d.box(1380, y, 140, 86, "RECOVERY", ["low-Z 20-50 Ω", "clean +23 dBu"])
    chain_h(d, [IN, BI, CO, MX, DV, RE])
    d.text(1450, y + 104, "→ return canale (0 dBu)", 10.5, AUDIO, "middle")
    RS = d.box(570, 262, 300, 96, "RISONANZA (v0.2 SIMULATA)",
               ["iniezione OTA nel summer: 1/Q = Rf·gm_res", "0-90 % corsa = Q 0,707→∞ · 90-100 % = auto-osc.",
                "+7,3…+8,6 dBu con soft limiter 3 × 1N4148"], "purple", lsize=10)
    d.arrow([RS.t, (RS.cx, CO.y + CO.h + 2)], "fb")
    # sezione controllo
    d.raw(f'  <rect x="40" y="400" width="1480" height="300" rx="10" fill="#EEF3F6" stroke="{CV}" stroke-width="1.2"/>')
    d.text(66, 432, "SEZIONE CONTROLLO — FREQ (2 knob: HPF e LPF, 0-5 V)", 15, CV, weight=700)
    cy = 456
    b1 = d.box(66, cy, 215, 90, "LAW SHAPER", ["piecewise attivo (dec. 70):", "expo 90 % centrale + accelerazione",
                                              "estremi + pre-distorsione errore"], tsize=12, lsize=10)
    b2 = d.box(331, cy, 235, 90, "CONVERTER EXPO", ["coppia BJT matched, ΔVbe PTAT:", "Iabc 114 nA…397 µA = 10,6 Hz…37 kHz",
                                                 "deriva ≤ 2,4 % (0-50 °C)"], tsize=12, lsize=10)
    b3 = d.box(616, cy, 235, 90, "DISTRIBUZIONE", ["mirror bufferizzati × 8 + trim/core", "tracking ≤ 1,6 % PASS",
                                                "(mirror semplice scartato)"], tsize=12, lsize=10)
    b4 = d.box(901, cy, 260, 90, "RAMP BBM (VALIDATA)", ["commutazione modo al picco +18 dBu:", "τ 1 ms = click −8,4 dB",
                                                     "!famiglia unica 1 ms: ratificata dec. 80"], tsize=12, lsize=10)
    b5 = d.box(1211, cy, 283, 90, "RES + DRIVE CV", ["RES: distribuzione a stella bufferizzata", "DRIVE: mux per canale segue il bit modo",
                                                   "smoothing 1 ms (dec. 80)"], tsize=12, lsize=10)
    chain_h(d, [b1, b2, b3, b4, b5], "cv")
    d.arrow([(b3.cx, cy), (b3.cx, 382), (535, 382), (535, CO.y + CO.h + 2)], "cv")
    d.text(300, 374, "Iabc (o Vc se c-B) → integratori dei core", 10, CV)
    d.box(66, 566, 1428, 112, "VERIFICATO CON LM13700 REALE (sim/filtro/RISULTATI-ota-real.md) + RERUN RUMORE 71A",
          ["law fc: errore ≤ 1,5 % su 10,6 Hz–37,4 kHz · Q 0,702-0,713 · offset DC stati 4-5 mV bounded (nessun trim)",
           "FINDING: tetto di stato 52 mV a f0 (strutturale per ogni OTA) → il core nudo è un compressore morbido (~1 % THD a 0 dBu, collasso a +10 dBu): è il CARATTERE dell'opzione (a)",
           "RUMORE (dec. 89): target ≤ −80 dBu A-wtd · core ideale −90,3…−126 · die reale stimato −84…−76 a fc max = al limite → è un input in più per la scelta q. 70",
           "i vecchi numeri −107,8…−134,8 dBu sono invalidati (quirk INTEG) · opzione pulita (c-B): VCA 218x × 2 per core (+16 chip)"],
          "green", align="start", lsize=10.5, tsize=12)
    d.box(40, 722, 900, 66, "",
          ["RAIL: tutti gli OTA su ±15,0 V ultra-low-noise dal raw ±22 V (pre-reg ±16,5 → LT3045/94, dec. 93) — LM13700 assoluto ±18",
           "BOM v0.1: 20 LM13700 + ~14 quad + 48 diodi limiter + ~30 trimmer + C integratori 33n C0G/PP matched 2 %"],
          "note", align="start", lsize=10.5)
    d.box(980, 722, 540, 66, "",
          ["PROTOTIPO MILLEFORI: 1 core + converter + RES — confronto a ORECCHIO",
           "(a) carattere OTA vs (c-B) pulito; chiude anche le questioni 11 e 64."],
          "amber", align="start", lsize=10.5)
    d.legend(826, [("audio", "audio (send → return)"), ("cv", "controllo CV / Iabc"),
                   ("fb", "risonanza / aperto su ascolto"), ("dashed", "provvisorio / in attesa")])
    d.footer("Fonte: docs/fase2/filter-module.md v0.2 + v0.3-WIP (§2-§6, §9) + sim/filtro/RISULTATI-filtro-noise-71A.md + decisioni 80/82/89/93 · core 0 dBu in/out, picco risonanza +6…+10 dBu")
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
                    ["presa pre-EQ [BLOCCATO]", "ROSSO = clip (soglia +17 dBu)", "!altri colori: da definire"], "ctrl", tsize=12)
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
           "!Aperto: colori e livelli del LED sotto il rosso · conferma soglia rosso +17 dBu",
           "!Aperto: «massimo 4» letto come 4 in totale tra MIC e MONO"],
          "note", align="start", lsize=10.5)
    d.legend(864, [("audio", "audio"), ("cv", "controllo / LED")])
    d.footer("Fonte: docs/fase4/mic-mono-moduli.md v0.1 (2026-10-13) + sim/mic/RISULTATI-mic-mono.md + SPECIFICA §8 + decisioni 36/37/91/94/95/97")
    return d.save()


if __name__ == "__main__":
    warn = []
    for f in (canale, fx, fx_send, master, five_way, filtro, cue, mic_mono):
        warn += f()
    print("scritti 8 SVG in", HERE)
    for w in warn:
        print("ATTENZIONE:", w)
