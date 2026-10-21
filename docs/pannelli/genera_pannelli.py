"""Render dei pannelli del mixer (BOZZA): moduli singoli e due setup.

Uso:  python3 docs/pannelli/genera_pannelli.py
Scrive in docs/pannelli/: moduli.svg, setup-ridotto.svg, setup-completo.svg,
pannelli.html e (con Chrome) pannelli.pdf.

Comandi: docs/fase3/sistema-comandi.md + dec. 108 (FX-SEND), 111 (MONO del
master, MUTE del mic). Disposizione, misure e colori sono una BOZZA neutra
(scelte di Filippo del 2026-10-21: larghezza 19", in alto 5-way, master e
CUE; sotto MIC/MONO a sinistra, ritorni FX al centro, canali a destra con
sotto mandate e filtro). Unita: millimetri.
"""

import os
import subprocess

QUI = os.path.dirname(os.path.abspath(__file__))

STRISCIA = 36.0          # larghezza di una striscia verticale
RACK = 482.6             # pannello 19"
ORECCHIA = 16.3          # zona delle viti del rack, per lato
UTILE = RACK - 2 * ORECCHIA
TESTA = 13.0             # fascia del nome del modulo

INK = "#1d1d1b"
SOFT = "#6b6b66"
CLASSE = {               # bozza: palette = voce 40
    "canale": "#dbe6f2", "send": "#e8f0f8", "filtro": "#f2dede",
    "fx": "#e1eedb", "mic": "#f2ead6", "five": "#e8def2",
    "master": "#e1e1df", "cue": "#ebebe8", "cieco": "#f6f6f4",
}
FONT = "font-family='Helvetica Neue, Helvetica, Arial, sans-serif'"


class Pannello:
    """Un modulo: larghezza, altezza e i suoi elementi in coordinate locali."""

    def __init__(self, nome, classe, w):
        self.nome, self.classe, self.w = nome, classe, w
        self.el = []
        self.y = TESTA + 4

    # --- elementi ---
    def testo(self, x, y, t, size=2.9, peso="normal", colore=INK, anchor="middle"):
        t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.el.append(f"<text x='{x:.2f}' y='{y:.2f}' font-size='{size}' font-weight='{peso}' "
                       f"fill='{colore}' text-anchor='{anchor}' {FONT}>{t}</text>")

    def manopola(self, x, y, nome, r=7.5, detent=False):
        self.el.append(f"<circle cx='{x:.2f}' cy='{y:.2f}' r='{r + 1.6:.2f}' fill='none' "
                       f"stroke='{SOFT}' stroke-width='0.25' stroke-dasharray='0.6 1.2'/>")
        if detent:
            self.el.append(f"<line x1='{x:.2f}' y1='{y - r - 2.6:.2f}' x2='{x:.2f}' y2='{y - r - 1.2:.2f}' "
                           f"stroke='{INK}' stroke-width='0.5'/>")
        self.el.append(f"<circle cx='{x:.2f}' cy='{y:.2f}' r='{r:.2f}' fill='#2a2a28'/>")
        self.el.append(f"<line x1='{x:.2f}' y1='{y:.2f}' x2='{x:.2f}' y2='{y - r + 1:.2f}' "
                       f"stroke='#f4f4f0' stroke-width='0.8' stroke-linecap='round'/>")
        self.testo(x, y + r + 4.0, nome, 2.7)

    def selettore(self, x, y, posizioni, nome=None):
        n = len(posizioni)
        w = 7.0 * n + 2
        self.el.append(f"<rect x='{x - w / 2:.2f}' y='{y - 2.6:.2f}' width='{w:.2f}' height='5.2' rx='2.6' "
                       f"fill='#fbfbf9' stroke='{INK}' stroke-width='0.35'/>")
        cx = x - w / 2 + 1 + 3.5
        self.el.append(f"<circle cx='{cx + 7.0 * (n // 2):.2f}' cy='{y:.2f}' r='2.0' fill='#2a2a28'/>")
        for i, p in enumerate(posizioni):
            self.testo(cx + 7.0 * i, y + 6.2, p, 2.0, colore=SOFT)
        if nome:
            self.testo(x, y - 4.2, nome, 2.5)

    def bottone(self, x, y, nome, w=9.0, h=6.0, sotto=True):
        self.el.append(f"<rect x='{x - w / 2:.2f}' y='{y - h / 2:.2f}' width='{w:.2f}' height='{h:.2f}' rx='1.2' "
                       f"fill='#fbfbf9' stroke='{INK}' stroke-width='0.4'/>")
        if sotto:
            self.testo(x, y + h / 2 + 3.2, nome, 2.4)
        else:
            self.testo(x, y + 0.9, nome, 2.2)

    def fader(self, x, y, corsa=60.0, nome="FADER"):
        self.el.append(f"<rect x='{x - 0.9:.2f}' y='{y:.2f}' width='1.8' height='{corsa:.2f}' rx='0.9' fill='#2a2a28'/>")
        for i in range(11):
            yy = y + corsa * i / 10
            self.el.append(f"<line x1='{x - 4.5:.2f}' y1='{yy:.2f}' x2='{x - 2.6:.2f}' y2='{yy:.2f}' "
                           f"stroke='{SOFT}' stroke-width='0.25'/>")
        self.el.append(f"<rect x='{x - 5:.2f}' y='{y + corsa * 0.2 - 3.5:.2f}' width='10' height='7' rx='1' "
                       f"fill='#3a3a37'/>")
        self.el.append(f"<line x1='{x - 5:.2f}' y1='{y + corsa * 0.2:.2f}' x2='{x + 5:.2f}' y2='{y + corsa * 0.2:.2f}' "
                       f"stroke='#f4f4f0' stroke-width='0.6'/>")
        self.testo(x, y + corsa + 5.0, nome, 2.6)

    def meter(self, x, y, n, passo=3.0, orizz=False, nome=None):
        for i in range(n):
            f = i / max(n - 1, 1)
            col = "#3f9d4a" if f < 0.6 else ("#e0a526" if f < 0.85 else "#d2452f")
            if orizz:
                self.el.append(f"<rect x='{x + i * passo:.2f}' y='{y:.2f}' width='{passo - 0.8:.2f}' height='2.2' "
                               f"rx='0.4' fill='{col}'/>")
            else:
                yy = y + (n - 1 - i) * passo
                self.el.append(f"<rect x='{x:.2f}' y='{yy:.2f}' width='2.6' height='{passo - 0.8:.2f}' "
                               f"rx='0.4' fill='{col}'/>")
        if nome:
            if orizz:
                self.testo(x + n * passo / 2, y - 1.5, nome, 2.2, colore=SOFT)
            else:
                self.testo(x + 1.3, y + n * passo + 3.2, nome, 2.0, colore=SOFT)

    def led3(self, x, y, nome="LED"):
        for i, c in enumerate(("#3f9d4a", "#e0a526", "#d2452f")):
            self.el.append(f"<circle cx='{x - 4 + 4 * i:.2f}' cy='{y:.2f}' r='1.4' fill='{c}'/>")
        self.testo(x, y + 4.4, nome, 2.3)

    def jack(self, x, y, nome):
        self.el.append(f"<circle cx='{x:.2f}' cy='{y:.2f}' r='4.2' fill='#c9c9c4' stroke='{INK}' stroke-width='0.4'/>")
        self.el.append(f"<circle cx='{x:.2f}' cy='{y:.2f}' r='1.8' fill='#2a2a28'/>")
        self.testo(x, y + 8.0, nome, 2.4)

    def chiudi(self, h=None):
        self.h = h if h else self.y + 4
        return self

    # --- disegno ---
    def svg(self, ox, oy, h=None):
        h = h or self.h
        out = [f"<g transform='translate({ox:.2f},{oy:.2f})'>",
               f"<rect x='0' y='0' width='{self.w:.2f}' height='{h:.2f}' fill='{CLASSE[self.classe]}' "
               f"stroke='{INK}' stroke-width='0.45'/>"]
        if self.classe != "cieco":
            out.append(f"<rect x='0' y='0' width='{self.w:.2f}' height='{TESTA - 3:.2f}' fill='{INK}' fill-opacity='0.07'/>")
            out.append(f"<text x='{self.w / 2:.2f}' y='{TESTA - 5.4:.2f}' font-size='3.1' font-weight='bold' "
                       f"fill='{INK}' text-anchor='middle' {FONT}>{self.nome}</text>")
        else:
            out.append(f"<text x='{self.w / 2:.2f}' y='{h / 2:.2f}' font-size='2.6' fill='{SOFT}' "
                       f"text-anchor='middle' {FONT}>{self.nome}</text>")
        # viti del pannello
        for vx, vy in ((2.6, 2.6), (self.w - 2.6, 2.6), (2.6, h - 2.6), (self.w - 2.6, h - 2.6)):
            out.append(f"<circle cx='{vx:.2f}' cy='{vy:.2f}' r='0.9' fill='none' stroke='{SOFT}' stroke-width='0.3'/>")
        out += self.el
        out.append("</g>")
        return "\n".join(out)


# ---------------- moduli ----------------

def canale(n):
    p = Pannello(f"CDJ {n}", "canale", STRISCIA)
    c = STRISCIA / 2
    p.selettore(c, p.y + 4, ["LINE", "PHONO"]); p.y += 16
    p.manopola(c, p.y + 8, "GAIN", detent=True); p.y += 24
    for b in ("HIGH", "MID-HIGH", "LOW-MID", "LOW"):
        p.manopola(c, p.y + 8, b, detent=True); p.y += 24
    p.selettore(c, p.y + 6, ["HPF", "OFF", "LPF"], "FILTRO"); p.y += 18
    for i, (dx, dy) in enumerate(((-6, 0), (6, 0), (-6, 10), (6, 10))):
        p.bottone(c + dx, p.y + 4 + dy, f"FX{i + 1}", w=9, h=6, sotto=False)
    p.y += 20
    p.bottone(c, p.y + 4, "CUE", w=14, h=6, sotto=False); p.y += 12
    p.meter(c - 13.5, p.y + 2, 10, passo=6.0, nome="METER")
    p.fader(c + 4, p.y + 2, 60.0); p.y += 72
    return p.chiudi()


def send(n):
    p = Pannello(f"FX-SEND {n}", "send", STRISCIA)
    c = STRISCIA / 2
    for b in ("EQ HIGH", "EQ LOW", "LEVEL"):
        p.manopola(c, p.y + 8, b); p.y += 24
    return p.chiudi()


def filtro(w):
    p = Pannello("FILTRO (4 canali)", "filtro", w)
    for riga, sez in enumerate(("HPF", "LPF")):
        y = p.y + 9 + riga * 27
        p.testo(7, y + 1, sez, 2.8, "bold", anchor="start")
        for i, nm in enumerate(("FREQ", "RES", "DRIVE")):
            p.manopola(w * (0.33 + 0.24 * i), y, nm, r=7.0)
    p.y += 54
    return p.chiudi()


def fx(w):
    p = Pannello("FX — 4 RITORNI", "fx", w)
    p.y += 2
    col = w / 4
    y0 = p.y
    for r in range(4):
        x = col * r + col / 2
        y = y0
        p.testo(x, y + 2, f"RET {r + 1}", 2.6, "bold"); y += 6
        for nm, det in (("GAIN", True), ("EQ HIGH", True), ("EQ LOW", True)):
            p.manopola(x, y + 8, nm, r=7.0, detent=det); y += 22
        for b in range(4):
            nome = "SELF" if b == r else f"> FX{b + 1}"
            p.manopola(x, y + 7, nome, r=6.0); y += 19
        p.meter(x - 13.5, y + 2, 10, passo=6.0, nome="METER")
        p.fader(x + 4, y + 2, 60.0)
        p.y = y + 72
    return p.chiudi()


def micmono(tipo):
    p = Pannello(tipo, "mic", STRISCIA)
    c = STRISCIA / 2
    p.manopola(c, p.y + 8, "GAIN", r=7.0); p.y += 22
    for b in ("EQ HIGH", "EQ LOW"):
        p.manopola(c, p.y + 8, b, r=7.0, detent=True); p.y += 22
    for i in range(4):
        p.manopola(c, p.y + 7, f"SEND {i + 1}", r=6.0); p.y += 19
    p.led3(c, p.y + 3); p.y += 12
    if tipo == "MIC":
        p.bottone(c, p.y + 4, "MUTE", w=14, h=6, sotto=False)
    p.y += 12
    return p.chiudi()


def five(w):
    p = Pannello("5-WAY", "five", w)
    bande = ("SUB", "KICK", "MID", "HIGH", "SUPER")
    col = (w - 40) / 5
    y0 = p.y
    for i, b in enumerate(bande):
        x = col * i + col / 2 + 2
        y = y0
        p.testo(x, y + 2, b, 2.7, "bold"); y += 5
        p.bottone(x, y + 4, "KILL", w=12, h=6, sotto=False); y += 13
        p.manopola(x, y + 8, "GAIN", r=7.5, detent=True); y += 24
        p.manopola(x, y + 8, "POSITION", r=7.0); y += 22
        p.manopola(x, y + 8, "WIDTH", r=7.0)  # dec. 117: continuo Q3...Q0,3
        p.testo(x - 9.5, y + 15.5, "Q3", 2.0, colore=SOFT)
        p.testo(x + 9.5, y + 15.5, "Q.3", 2.0, colore=SOFT); y += 22
        p.y = y
    x = w - 26
    p.manopola(x, y0 + 14, "GROWL", r=7.5)
    p.manopola(x, y0 + 40, "NASTRO", r=7.5)
    p.meter(w - 9, y0 + 2, 10, passo=5.0, nome="METER")
    return p.chiudi()


def master(w):
    p = Pannello("MASTER", "master", w)
    x = w * 0.36
    p.manopola(x, p.y + 10, "MASTER", r=8.0, detent=True)
    p.manopola(x, p.y + 38, "BOOTH", r=7.0)
    p.bottone(x, p.y + 60, "MONO", w=14, h=6, sotto=False)
    p.meter(w - 17, p.y + 1, 20, passo=3.2, nome="L")
    p.meter(w - 11, p.y + 1, 20, passo=3.2, nome="R")
    p.y += 72
    return p.chiudi()


def cue(w):
    p = Pannello("CUE", "cue", w)
    x = w / 2
    p.manopola(x, p.y + 10, "BLEND", r=7.0, detent=True)
    p.manopola(x, p.y + 34, "LEVEL", r=7.0)
    p.jack(x - 9, p.y + 56, "PHONES 1")
    p.jack(x + 9, p.y + 56, "PHONES 2")
    p.y += 70
    return p.chiudi()


def cieco(w, h, testo="pannello cieco"):
    p = Pannello(testo, "cieco", w)
    p.h = h
    return p


# ---------------- fogli ----------------

def foglio(titolo, sottotitolo, larg, alt, corpo):
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {larg:.1f} {alt:.1f}' "
            f"width='{larg:.1f}mm' height='{alt:.1f}mm'>\n"
            f"<rect width='100%' height='100%' fill='#ffffff'/>\n"
            f"<text x='12' y='16' font-size='7' font-weight='bold' fill='{INK}' {FONT}>{titolo}</text>\n"
            f"<text x='12' y='23' font-size='3.4' fill='{SOFT}' {FONT}>{sottotitolo}</text>\n"
            f"<text x='{larg - 12:.1f}' y='16' font-size='4' font-weight='bold' fill='#b23b2a' "
            f"text-anchor='end' {FONT}>BOZZA</text>\n"
            f"<text x='{larg - 12:.1f}' y='22' font-size='2.8' fill='{SOFT}' text-anchor='end' {FONT}>"
            f"disposizione, misure e colori da decidere (voce 40, A10)</text>\n"
            + corpo + "\n</svg>\n")


def quota(x1, x2, y, testo):
    return (f"<line x1='{x1:.2f}' y1='{y:.2f}' x2='{x2:.2f}' y2='{y:.2f}' stroke='{SOFT}' stroke-width='0.3'/>"
            f"<line x1='{x1:.2f}' y1='{y - 1.5:.2f}' x2='{x1:.2f}' y2='{y + 1.5:.2f}' stroke='{SOFT}' stroke-width='0.3'/>"
            f"<line x1='{x2:.2f}' y1='{y - 1.5:.2f}' x2='{x2:.2f}' y2='{y + 1.5:.2f}' stroke='{SOFT}' stroke-width='0.3'/>"
            f"<text x='{(x1 + x2) / 2:.2f}' y='{y - 1.6:.2f}' font-size='2.8' fill='{SOFT}' text-anchor='middle' {FONT}>{testo}</text>")


def quota_v(x, y1, y2, testo):
    return (f"<line x1='{x:.2f}' y1='{y1:.2f}' x2='{x:.2f}' y2='{y2:.2f}' stroke='{SOFT}' stroke-width='0.3'/>"
            f"<line x1='{x - 1.5:.2f}' y1='{y1:.2f}' x2='{x + 1.5:.2f}' y2='{y1:.2f}' stroke='{SOFT}' stroke-width='0.3'/>"
            f"<line x1='{x - 1.5:.2f}' y1='{y2:.2f}' x2='{x + 1.5:.2f}' y2='{y2:.2f}' stroke='{SOFT}' stroke-width='0.3'/>"
            f"<text x='{x - 2:.2f}' y='{(y1 + y2) / 2:.2f}' font-size='2.8' fill='{SOFT}' text-anchor='middle' "
            f"transform='rotate(-90 {x - 2:.2f} {(y1 + y2) / 2:.2f})' {FONT}>{testo}</text>")


BLOCCO = 4 * STRISCIA                      # 144 mm: quattro strisce
GAP = (UTILE - 3 * BLOCCO) / 2             # spazio fra i tre blocchi bassi


def moduli_singoli():
    tutti = [canale(1), send(1), micmono("MIC"), micmono("MONO"), filtro(BLOCCO), fx(BLOCCO),
             five(UTILE - 96 - 62 - 4), master(96), cue(62)]
    # due righe: strisce + fx + filtro, poi 5-way/master/cue
    corpo, x, y = [], 14.0, 34.0
    riga1 = tutti[:6]
    hmax = 0
    for p in riga1:
        corpo.append(p.svg(x, y))
        corpo.append(quota(x, x + p.w, y - 3, f"{p.w:.0f}"))
        corpo.append(f"<text x='{x + p.w / 2:.2f}' y='{y + p.h + 5:.2f}' font-size='2.8' fill='{SOFT}' "
                     f"text-anchor='middle' {FONT}>{p.w:.0f} × {p.h:.0f} mm</text>")
        x += p.w + 12
        hmax = max(hmax, p.h)
    larg = x + 2
    x, y = 14.0, y + hmax + 22
    h2 = 0
    for p in tutti[6:]:
        corpo.append(p.svg(x, y))
        corpo.append(quota(x, x + p.w, y - 3, f"{p.w:.0f}"))
        corpo.append(f"<text x='{x + p.w / 2:.2f}' y='{y + p.h + 5:.2f}' font-size='2.8' fill='{SOFT}' "
                     f"text-anchor='middle' {FONT}>{p.w:.0f} × {p.h:.0f} mm</text>")
        x += p.w + 12
        h2 = max(h2, p.h)
    larg = max(larg, x + 2)
    alt = y + h2 + 20
    corpo.append(legenda(14, alt - 6))
    return foglio("Moduli singoli", "Ogni modulo con i comandi dell'inventario (sistema-comandi.md, dec. 108, 111 e 116). "
                  "Strisce da 36 mm.", larg, alt, "\n".join(corpo))


def legenda(x, y):
    voci = (("canale", "canali CDJ"), ("send", "FX-SEND"), ("filtro", "filtro"), ("fx", "ritorni FX"),
            ("mic", "MIC / MONO"), ("five", "5-way"), ("master", "master"), ("cue", "CUE"))
    out = []
    for i, (k, t) in enumerate(voci):
        xx = x + i * 34
        out.append(f"<rect x='{xx:.2f}' y='{y - 3:.2f}' width='5' height='3.4' fill='{CLASSE[k]}' "
                   f"stroke='{INK}' stroke-width='0.3'/>")
        out.append(f"<text x='{xx + 7:.2f}' y='{y:.2f}' font-size='2.8' fill='{INK}' {FONT}>{t}</text>")
    return "\n".join(out)


def setup(nome, sotto, n_canali, n_mono, file):
    ox, oy = 14.0, 34.0
    x0 = ox + ORECCHIA
    corpo = []
    # banda alta: 5-way, master, CUE
    w_master, w_cue = 96.0, 62.0
    alto = [five(UTILE - w_master - w_cue), master(w_master), cue(w_cue)]
    h_alto = max(p.h for p in alto)
    x = x0
    for p in alto:
        corpo.append(p.svg(x, oy, h_alto))
        x += p.w
    y_basso = oy + h_alto + 6
    # sinistra: MIC + MONO
    sinistra = [micmono("MIC")] + [micmono("MONO") for _ in range(n_mono)]
    # centro: FX
    centro = fx(BLOCCO)
    # destra: canali, sotto le mandate, sotto il filtro
    canali = [canale(i + 1) for i in range(n_canali)]
    mandate = [send(i + 1) for i in range(n_canali)]
    filt = filtro(BLOCCO)
    h_can = canali[0].h
    h_dx = h_can + mandate[0].h + filt.h
    h_basso = max(h_dx, centro.h, sinistra[0].h)
    # blocco sinistro
    x = x0
    for p in sinistra:
        corpo.append(p.svg(x, y_basso))
        x += p.w
    vuoto = BLOCCO - len(sinistra) * STRISCIA
    if vuoto > 0:
        corpo.append(cieco(vuoto, sinistra[0].h).svg(x, y_basso))
    corpo.append(cieco(BLOCCO, h_basso - sinistra[0].h).svg(x0, y_basso + sinistra[0].h))
    # blocco centrale
    xc = x0 + BLOCCO + GAP
    corpo.append(centro.svg(xc, y_basso))
    if h_basso > centro.h + 1:
        corpo.append(cieco(BLOCCO, h_basso - centro.h).svg(xc, y_basso + centro.h))
    # blocco destro
    xd = xc + BLOCCO + GAP
    x = xd
    for p in canali:
        corpo.append(p.svg(x, y_basso))
        x += p.w
    vuoto = BLOCCO - n_canali * STRISCIA
    if vuoto > 0:
        corpo.append(cieco(vuoto, h_can + mandate[0].h).svg(x, y_basso))
    x = xd
    for p in mandate:
        corpo.append(p.svg(x, y_basso + h_can))
        x += p.w
    corpo.append(filt.svg(xd, y_basso + h_can + mandate[0].h, h_basso - h_can - mandate[0].h))
    # telaio 19" con le orecchie
    h_tot = y_basso + h_basso - oy
    tel = [f"<rect x='{ox:.2f}' y='{oy - 4:.2f}' width='{RACK:.2f}' height='{h_tot + 8:.2f}' rx='2' "
           f"fill='#cfcfca' stroke='{INK}' stroke-width='0.5'/>"]
    for lato in (ox + ORECCHIA / 2, ox + RACK - ORECCHIA / 2):
        yy = oy + 6
        while yy < oy + h_tot - 4:
            tel.append(f"<rect x='{lato - 3.2:.2f}' y='{yy:.2f}' width='6.4' height='3.4' rx='1.7' "
                       f"fill='#ffffff' stroke='{INK}' stroke-width='0.3'/>")
            yy += 44.45
    corpo = tel + corpo
    corpo.append(quota(ox, ox + RACK, oy - 8, f"19\" = {RACK} mm"))
    corpo.append(quota(x0, x0 + UTILE, oy + h_tot + 10, f"utile {UTILE:.0f} mm"))
    corpo.append(quota_v(ox - 4, oy - 4, oy + h_tot + 4, f"{h_tot + 8:.0f} mm"))
    larg = ox + RACK + 14
    alt = oy + h_tot + 28
    corpo.append(legenda(14, alt - 4))
    svg = foglio(nome, sotto, larg, alt, "\n".join(corpo))
    open(os.path.join(QUI, file), "w", encoding="utf-8").write(svg)
    return h_tot + 8


def main():
    open(os.path.join(QUI, "moduli.svg"), "w", encoding="utf-8").write(moduli_singoli())
    h1 = setup("Setup ridotto", "2 canali CDJ con 2 FX-SEND · 1 MIC · 1 MONO · FX 4 ritorni · filtro · 5-way · "
               "master · CUE", 2, 1, "setup-ridotto.svg")
    h2 = setup("Setup completo", "4 canali CDJ con 4 FX-SEND · 1 MIC · 3 MONO · FX 4 ritorni · filtro · 5-way · "
               "master · CUE", 4, 3, "setup-completo.svg")
    print(f"altezza del pannello: ridotto {h1:.0f} mm, completo {h2:.0f} mm")
    html = ["<meta charset='utf-8'><title>Pannelli maelcum mixer</title>",
            "<style>@page{size:A3 portrait;margin:10mm} body{margin:0} "
            "img{display:block;width:100%;max-height:400mm;object-fit:contain;break-after:page}</style>"]
    for f in ("moduli.svg", "setup-ridotto.svg", "setup-completo.svg"):
        html.append(f"<img src='{f}'>")
    open(os.path.join(QUI, "pannelli.html"), "w", encoding="utf-8").write("\n".join(html))
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if os.path.exists(chrome):
        subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={os.path.join(QUI, 'pannelli.pdf')}",
                        "file://" + os.path.join(QUI, "pannelli.html")],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        print("PDF:", os.path.join(QUI, "pannelli.pdf"))


if __name__ == "__main__":
    main()
