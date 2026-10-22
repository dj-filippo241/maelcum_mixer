"""Render dei pannelli del mixer (BOZZA): moduli singoli e due setup.

Uso:  python3 docs/pannelli/genera_pannelli.py
Scrive in docs/pannelli/: moduli.svg, setup-ridotto.svg, setup-completo.svg,
pannelli.html e (con Chrome) pannelli.pdf.

Comandi: docs/fase3/sistema-comandi.md + dec. 108 (FX-SEND), 111 (MONO del
master, MUTE del mic), 117 (WIDTH continuo), 118-124 (sessione manopole:
14 mm disassate come sul Xone:DB4, EQ secondari 9 mm senza scatto, fader
100 mm, levette per kill/filtro/LINE-PHONO, bottoni con luce, cappucci).
Colori standard: un colore per tipo di oggetto (tabella C, chiave nel foglio
dei moduli), da ridisegnare da Filippo. Disposizione e misure: BOZZA
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

# Colori standard (Filippo 2026-10-22): ogni tipo di oggetto ha un colore suo
# e solo suo, cosi in Illustrator Seleziona > Stesso > Colore riempimento (o
# traccia) prende tutti gli oggetti uguali in un colpo. Nessun valore si
# ripete: lo controlla l'assert sotto. La palette vera e di Filippo (dec. 94c).
C = {
    # fondo dei pannelli, per classe di modulo
    "p_canale": "#dbe6f2", "p_send": "#e8f0f8", "p_filtro": "#f2dede",
    "p_fx": "#e1eedb", "p_mic": "#f2ead6", "p_five": "#e8def2",
    "p_master": "#e1e1df", "p_cue": "#ebebe8", "p_cieco": "#f6f6f4",
    "p_testa": "#d4d4cf",
    # manopole (corpo), per funzione; 14 mm salvo dove indicato
    "k_gain": "#2a2a28", "k_eq_canale": "#2b2a33", "k_eq_9mm": "#3b3a36",
    "k_level_send": "#2c3329", "k_reroute": "#33292b", "k_filtro": "#3a2a2a",
    "k_5w_gain": "#2a2f3a", "k_5w_pos": "#2f2a3a", "k_5w_width": "#2a3a37",
    "k_sat": "#3a332a", "k_master": "#262626", "k_cue": "#30302c",
    "k_send_mic": "#2d2d34",
    "k_indice": "#f4f4f0",
    # fader
    "f_binario": "#2e2e2b", "f_cursore": "#3a3a37", "f_riga": "#f2f2ee",
    # levette: ghiera per funzione, leva comune
    "l_kill": "#8a8a84", "l_filtro": "#8d8780", "l_linea": "#86868e",
    "l_leva": "#1f1f1e",
    # bottoni con luce: corpo e luce per funzione
    "b_cue": "#fbfbf9", "b_fx": "#f9fbfb", "b_mono": "#fbf9fb", "b_mute": "#fbfbf7",
    "luce_cue": "#e8c547", "luce_fx": "#4fa3e0", "luce_mono": "#e07a4f",
    "luce_mute": "#d23a3a",
    # meter a zone (schematico) e LED tricolore
    "m_blu": "#3f6fd2", "m_verde": "#3f9d4a", "m_giallo": "#e6d23a",
    "m_ambra": "#e0a526", "m_rosso": "#d2452f", "m_viola": "#8e3fd2",
    "led_verde": "#41a04c", "led_giallo": "#e2a828", "led_rosso": "#d44731",
    # jack
    "j_ghiera": "#c9c9c4", "j_foro": "#252523",
    # telaio e foglio
    "rack": "#cfcfca", "rack_foro": "#fefefe", "foglio": "#ffffff",
    # testi (riempimento)
    "t_comando": "#1d1d1b", "t_piccolo": "#6b6b66", "t_modulo": "#1c1c1a",
    "t_foglio": "#1e1e1c", "t_quote": "#6c6c67", "t_bozza": "#b23b2a",
    # tracce
    "s_pannello": "#1b1b19", "s_anello": "#6a6a65", "s_detent": "#1a1a18",
    "s_bottone": "#191917", "s_levetta": "#181816", "s_tacche": "#696964",
    "s_quote": "#6d6d68", "s_viti": "#68686e", "s_jack": "#171715",
    "s_rack": "#161614", "s_legenda": "#151513",
}
assert len(set(v.lower() for v in C.values())) == len(C), "colore ripetuto"
INK = C["t_comando"]
SOFT = C["t_piccolo"]
CLASSE = {k[2:]: v for k, v in C.items() if k.startswith("p_") and k != "p_testa"}
FONT = "font-family='Helvetica Neue, Helvetica, Arial, sans-serif'"
# manopole: classe 14 mm (Alps RK14K) e 9 mm (RK09), dec. 118; raggio del
# cappuccio disegnato
R14 = 7.5
R9 = 5.5
# disassato come sul Xone:DB4 (dec. 118): colonne a zig-zag
DX = 5.5                  # spostamento laterale dal centro della colonna
PASSO = 17.0              # passo verticale fra due manopole disassate


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

    def manopola(self, x, y, nome, tipo, r=R14, detent=False, lato=None):
        """lato None: etichetta sotto; "dx"/"sx": etichetta a fianco
        (colonne disassate)."""
        self.el.append(f"<circle cx='{x:.2f}' cy='{y:.2f}' r='{r + 1.6:.2f}' fill='none' "
                       f"stroke='{C['s_anello']}' stroke-width='0.25' stroke-dasharray='0.6 1.2'/>")
        if detent:
            self.el.append(f"<line x1='{x:.2f}' y1='{y - r - 2.6:.2f}' x2='{x:.2f}' y2='{y - r - 1.2:.2f}' "
                           f"stroke='{C['s_detent']}' stroke-width='0.5'/>")
        self.el.append(f"<circle cx='{x:.2f}' cy='{y:.2f}' r='{r:.2f}' fill='{C[tipo]}'/>")
        self.el.append(f"<line x1='{x:.2f}' y1='{y:.2f}' x2='{x:.2f}' y2='{y - r + 1:.2f}' "
                       f"stroke='{C['k_indice']}' stroke-width='0.8' stroke-linecap='round'/>")
        if lato == "dx":
            self.testo(x + r + 2.0, y + 1.0, nome, 2.5, anchor="start")
        elif lato == "sx":
            self.testo(x - r - 2.0, y + 1.0, nome, 2.5, anchor="end")
        else:
            self.testo(x, y + r + 4.0, nome, 2.7)

    def colonna(self, c, voci, r=R14, passo=PASSO):
        """Manopole disassate a zig-zag (dec. 118, come il Xone:DB4): la
        prima a sinistra, la seconda a destra, ... Etichetta sul lato
        libero. voci = (nome, tipo, detent)."""
        for i, (nome, tipo, det) in enumerate(voci):
            sx = i % 2 == 0
            x = c - DX if sx else c + DX
            self.manopola(x, self.y + r + 3, nome, tipo, r, det, "dx" if sx else "sx")
            self.y += passo if r == R14 else passo - 3
        self.y += r + 4

    def levetta(self, x, y, tipo, su, giu, centro=None, nome=None, piccola=False):
        """Levetta vista dall'alto: ghiera e leva. su/giu/centro = etichette
        delle posizioni (dec. 121, 122, 123)."""
        rg = 2.6 if piccola else 3.4
        self.el.append(f"<circle cx='{x:.2f}' cy='{y:.2f}' r='{rg:.2f}' fill='{C[tipo]}' "
                       f"stroke='{C['s_levetta']}' stroke-width='0.35'/>")
        self.el.append(f"<circle cx='{x:.2f}' cy='{y:.2f}' r='{rg * 0.45:.2f}' fill='{C['l_leva']}'/>")
        self.testo(x, y - rg - 1.4, su, 2.1, colore=SOFT)
        self.testo(x, y + rg + 3.0, giu, 2.1, colore=SOFT)
        if centro:
            self.testo(x + rg + 1.6, y + 0.8, centro, 2.1, colore=SOFT, anchor="start")
        if nome:
            self.testo(x - rg - 1.6, y + 0.8, nome, 2.4, anchor="end")

    def bottone(self, x, y, nome, tipo, w=9.0, h=6.0):
        """Bottone con luce a ritenuta (dec. 123): corpo e striscia di luce."""
        self.el.append(f"<rect x='{x - w / 2:.2f}' y='{y - h / 2:.2f}' width='{w:.2f}' height='{h:.2f}' rx='1.2' "
                       f"fill='{C['b_' + tipo]}' stroke='{C['s_bottone']}' stroke-width='0.4'/>")
        self.el.append(f"<rect x='{x - w / 2 + 1.2:.2f}' y='{y - h / 2 + 0.8:.2f}' width='{w - 2.4:.2f}' "
                       f"height='1.1' rx='0.5' fill='{C['luce_' + tipo]}'/>")
        self.testo(x, y + 1.6, nome, 2.2)

    def fader(self, x, y, corsa=100.0, nome="FADER"):
        self.el.append(f"<rect x='{x - 0.9:.2f}' y='{y:.2f}' width='1.8' height='{corsa:.2f}' rx='0.9' "
                       f"fill='{C['f_binario']}'/>")
        for i in range(11):
            yy = y + corsa * i / 10
            self.el.append(f"<line x1='{x - 4.5:.2f}' y1='{yy:.2f}' x2='{x - 2.6:.2f}' y2='{yy:.2f}' "
                           f"stroke='{C['s_tacche']}' stroke-width='0.25'/>")
        self.el.append(f"<rect x='{x - 5:.2f}' y='{y + corsa * 0.2 - 3.5:.2f}' width='10' height='7' rx='1' "
                       f"fill='{C['f_cursore']}'/>")
        self.el.append(f"<line x1='{x - 5:.2f}' y1='{y + corsa * 0.2:.2f}' x2='{x + 5:.2f}' y2='{y + corsa * 0.2:.2f}' "
                       f"stroke='{C['f_riga']}' stroke-width='0.6'/>")
        self.testo(x, y + corsa + 5.0, nome, 2.6)

    def meter(self, x, y, n, passo=3.0, orizz=False, nome=None):
        # zone schematiche (dec. 90a): blu, verde, giallo, ambra, rosso, viola
        zone = ("m_blu", "m_verde", "m_verde", "m_verde", "m_verde", "m_giallo",
                "m_giallo", "m_ambra", "m_rosso", "m_viola")
        for i in range(n):
            col = C[zone[min(int(i * 10 / n), 9)]]
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
        for i, c in enumerate(("led_verde", "led_giallo", "led_rosso")):
            self.el.append(f"<circle cx='{x - 4 + 4 * i:.2f}' cy='{y:.2f}' r='1.4' fill='{C[c]}'/>")
        self.testo(x, y + 4.4, nome, 2.3)

    def jack(self, x, y, nome):
        self.el.append(f"<circle cx='{x:.2f}' cy='{y:.2f}' r='4.2' fill='{C['j_ghiera']}' "
                       f"stroke='{C['s_jack']}' stroke-width='0.4'/>")
        self.el.append(f"<circle cx='{x:.2f}' cy='{y:.2f}' r='1.8' fill='{C['j_foro']}'/>")
        self.testo(x, y + 8.0, nome, 2.4)

    def chiudi(self, h=None):
        self.h = h if h else self.y + 4
        return self

    # --- disegno ---
    def svg(self, ox, oy, h=None):
        h = h or self.h
        out = [f"<g transform='translate({ox:.2f},{oy:.2f})'>",
               f"<rect x='0' y='0' width='{self.w:.2f}' height='{h:.2f}' fill='{CLASSE[self.classe]}' "
               f"stroke='{C['s_pannello']}' stroke-width='0.45'/>"]
        if self.classe != "cieco":
            out.append(f"<rect x='0' y='0' width='{self.w:.2f}' height='{TESTA - 3:.2f}' fill='{C['p_testa']}'/>")
            out.append(f"<text x='{self.w / 2:.2f}' y='{TESTA - 5.4:.2f}' font-size='3.1' font-weight='bold' "
                       f"fill='{C['t_modulo']}' text-anchor='middle' {FONT}>{self.nome}</text>")
        else:
            out.append(f"<text x='{self.w / 2:.2f}' y='{h / 2:.2f}' font-size='2.6' fill='{SOFT}' "
                       f"text-anchor='middle' {FONT}>{self.nome}</text>")
        # viti del pannello
        for vx, vy in ((2.6, 2.6), (self.w - 2.6, 2.6), (2.6, h - 2.6), (self.w - 2.6, h - 2.6)):
            out.append(f"<circle cx='{vx:.2f}' cy='{vy:.2f}' r='0.9' fill='none' stroke='{C['s_viti']}' "
                       f"stroke-width='0.3'/>")
        out += self.el
        out.append("</g>")
        return "\n".join(out)


# ---------------- moduli ----------------

def canale(n):
    p = Pannello(f"CDJ {n}", "canale", STRISCIA)
    c = STRISCIA / 2
    p.levetta(c, p.y + 5, "l_linea", "LINE", "PHONO", piccola=True); p.y += 14
    p.colonna(c, [("GAIN", "k_gain", True)] +
              [(b, "k_eq_canale", True) for b in ("HIGH", "MID-HIGH", "LOW-MID", "LOW")])
    p.levetta(c + 4, p.y + 6, "l_filtro", "HPF", "LPF", "OFF", "FILTRO"); p.y += 18
    for i, (dx, dy) in enumerate(((-6, 0), (6, 0), (-6, 9), (6, 9))):
        p.bottone(c + dx, p.y + 4 + dy, f"FX{i + 1}", "fx")
    p.y += 19
    p.bottone(c, p.y + 4, "CUE", "cue", w=14); p.y += 12
    p.meter(c - 13.5, p.y + 2, 10, passo=6.0, nome="METER")
    p.fader(c + 4, p.y + 2, 100.0); p.y += 112
    return p.chiudi()


def send(n):
    p = Pannello(f"FX-SEND {n}", "send", STRISCIA)
    c = STRISCIA / 2
    # EQ a 9 mm senza scatto (dec. 118), LEVEL a 14 mm
    p.colonna(c, [("EQ HIGH", "k_eq_9mm", False), ("EQ LOW", "k_eq_9mm", False)], r=R9)
    p.colonna(c, [("LEVEL", "k_level_send", False)])
    return p.chiudi()


def filtro(w):
    p = Pannello("FILTRO (4 canali)", "filtro", w)
    for riga, sez in enumerate(("HPF", "LPF")):
        y = p.y + 9 + riga * 27
        p.testo(7, y + 1, sez, 2.8, "bold", anchor="start")
        for i, nm in enumerate(("FREQ", "RES", "DRIVE")):
            p.manopola(w * (0.33 + 0.24 * i), y, nm, "k_filtro")
    p.y += 54
    return p.chiudi()


def fx(w):
    p = Pannello("FX — 4 RITORNI", "fx", w)
    p.y += 2
    col = w / 4
    y0 = p.y
    for r in range(4):
        x = col * r + col / 2
        p.y = y0
        p.testo(x, p.y + 2, f"RET {r + 1}", 2.6, "bold"); p.y += 5
        p.colonna(x, [("GAIN", "k_gain", True)])
        p.colonna(x, [("EQ HIGH", "k_eq_9mm", False), ("EQ LOW", "k_eq_9mm", False)], r=R9)
        p.colonna(x, [("SELF" if b == r else f"> FX{b + 1}", "k_reroute", False) for b in range(4)])
        y = p.y
        p.meter(x - 13.5, y + 2, 10, passo=6.0, nome="METER")
        p.fader(x + 4, y + 2, 100.0)
        p.y = y + 112
    return p.chiudi()


def micmono(tipo):
    p = Pannello(tipo, "mic", STRISCIA)
    c = STRISCIA / 2
    p.colonna(c, [("GAIN", "k_gain", False)])
    p.colonna(c, [("EQ HIGH", "k_eq_9mm", False), ("EQ LOW", "k_eq_9mm", False)], r=R9)
    p.colonna(c, [(f"SEND {i + 1}", "k_send_mic", False) for i in range(4)])
    p.led3(c, p.y + 3); p.y += 12
    if tipo == "MIC":
        p.bottone(c, p.y + 4, "MUTE", "mute", w=14)
    p.y += 12
    return p.chiudi()


def five(w):
    p = Pannello("5-WAY", "five", w)
    bande = ("SUB", "KICK", "MID", "HIGH", "SUPER")
    col = (w - 40) / 5
    y0 = p.y
    for i, b in enumerate(bande):
        x = col * i + col / 2 + 2
        p.y = y0
        p.testo(x, p.y + 2, b, 2.7, "bold"); p.y += 9
        # kill a levetta ON-OFF-(ON) (dec. 121)
        p.levetta(x, p.y + 4, "l_kill", "FISSO", "MOLLA", nome="KILL"); p.y += 16
        p.colonna(x, [("GAIN", "k_5w_gain", True), ("POSITION", "k_5w_pos", False),
                      ("WIDTH", "k_5w_width", False)])  # dec. 117: WIDTH continuo Q3...Q0,3
        # sotto la manopola WIDTH (terza della colonna: a sinistra)
        p.testo(x - DX, p.y - PASSO + R14 + 3.5, "Q3 … Q.3", 2.0, colore=SOFT)
    y = p.y
    x = w - 26
    p.manopola(x, y0 + 14, "GROWL", "k_sat")
    p.manopola(x, y0 + 40, "NASTRO", "k_sat")
    p.meter(w - 9, y0 + 2, 10, passo=5.0, nome="METER")
    p.y = max(y, y0 + 56)
    return p.chiudi()


def master(w):
    p = Pannello("MASTER", "master", w)
    x = w * 0.36
    p.manopola(x, p.y + 10, "MASTER", "k_master", r=8.0, detent=True)
    p.manopola(x, p.y + 38, "BOOTH", "k_master")
    p.bottone(x, p.y + 60, "MONO", "mono", w=14)
    p.meter(w - 17, p.y + 1, 20, passo=3.2, nome="L")
    p.meter(w - 11, p.y + 1, 20, passo=3.2, nome="R")
    p.y += 72
    return p.chiudi()


def cue(w):
    p = Pannello("CUE", "cue", w)
    x = w / 2
    p.manopola(x, p.y + 10, "BLEND", "k_cue", detent=True)
    p.manopola(x, p.y + 34, "LEVEL", "k_cue")
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
            f"<rect width='100%' height='100%' fill='{C['foglio']}'/>\n"
            f"<text x='12' y='16' font-size='7' font-weight='bold' fill='{C['t_foglio']}' {FONT}>{titolo}</text>\n"
            f"<text x='12' y='23' font-size='3.4' fill='{C['t_foglio']}' {FONT}>{sottotitolo}</text>\n"
            f"<text x='{larg - 12:.1f}' y='16' font-size='4' font-weight='bold' fill='{C['t_bozza']}' "
            f"text-anchor='end' {FONT}>BOZZA</text>\n"
            f"<text x='{larg - 12:.1f}' y='22' font-size='2.8' fill='{C['t_foglio']}' text-anchor='end' {FONT}>"
            f"colori standard: un colore per tipo di oggetto, da ridisegnare (dec. 94c)</text>\n"
            + corpo + "\n</svg>\n")


def quota(x1, x2, y, testo):
    return (f"<line x1='{x1:.2f}' y1='{y:.2f}' x2='{x2:.2f}' y2='{y:.2f}' stroke='{C["s_quote"]}' stroke-width='0.3'/>"
            f"<line x1='{x1:.2f}' y1='{y - 1.5:.2f}' x2='{x1:.2f}' y2='{y + 1.5:.2f}' stroke='{C["s_quote"]}' stroke-width='0.3'/>"
            f"<line x1='{x2:.2f}' y1='{y - 1.5:.2f}' x2='{x2:.2f}' y2='{y + 1.5:.2f}' stroke='{C["s_quote"]}' stroke-width='0.3'/>"
            f"<text x='{(x1 + x2) / 2:.2f}' y='{y - 1.6:.2f}' font-size='2.8' fill='{C["t_quote"]}' text-anchor='middle' {FONT}>{testo}</text>")


def quota_v(x, y1, y2, testo):
    return (f"<line x1='{x:.2f}' y1='{y1:.2f}' x2='{x:.2f}' y2='{y2:.2f}' stroke='{C["s_quote"]}' stroke-width='0.3'/>"
            f"<line x1='{x - 1.5:.2f}' y1='{y1:.2f}' x2='{x + 1.5:.2f}' y2='{y1:.2f}' stroke='{C["s_quote"]}' stroke-width='0.3'/>"
            f"<line x1='{x - 1.5:.2f}' y1='{y2:.2f}' x2='{x + 1.5:.2f}' y2='{y2:.2f}' stroke='{C["s_quote"]}' stroke-width='0.3'/>"
            f"<text x='{x - 2:.2f}' y='{(y1 + y2) / 2:.2f}' font-size='2.8' fill='{C["t_quote"]}' text-anchor='middle' "
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
        corpo.append(f"<text x='{x + p.w / 2:.2f}' y='{y + p.h + 5:.2f}' font-size='2.8' fill='{C['t_quote']}' "
                     f"text-anchor='middle' {FONT}>{p.w:.0f} × {p.h:.0f} mm</text>")
        x += p.w + 12
        hmax = max(hmax, p.h)
    larg = x + 2
    x, y = 14.0, y + hmax + 22
    h2 = 0
    for p in tutti[6:]:
        corpo.append(p.svg(x, y))
        corpo.append(quota(x, x + p.w, y - 3, f"{p.w:.0f}"))
        corpo.append(f"<text x='{x + p.w / 2:.2f}' y='{y + p.h + 5:.2f}' font-size='2.8' fill='{C['t_quote']}' "
                     f"text-anchor='middle' {FONT}>{p.w:.0f} × {p.h:.0f} mm</text>")
        x += p.w + 12
        h2 = max(h2, p.h)
    larg = max(larg, x + 2)
    alt = y + h2 + 20
    corpo.append(legenda(14, alt - 6))
    chiave, h_chiave = chiave_colori(14, alt + 6, larg)
    corpo.append(chiave)
    alt += h_chiave + 12
    return foglio("Moduli singoli", "Ogni modulo con i comandi dell'inventario (sistema-comandi.md, dec. 108, 111 e 116). "
                  "Strisce da 36 mm. Manopole 14 mm, EQ secondari 9 mm, disassate (dec. 118); fader 100 mm (dec. 120).", larg, alt, "\n".join(corpo))


def legenda(x, y):
    """Classi di modulo (fondo dei pannelli), in una riga."""
    voci = (("canale", "canali CDJ"), ("send", "FX-SEND"), ("filtro", "filtro"), ("fx", "ritorni FX"),
            ("mic", "MIC / MONO"), ("five", "5-way"), ("master", "master"), ("cue", "CUE"))
    out = []
    for i, (k, t) in enumerate(voci):
        xx = x + i * 34
        out.append(f"<rect x='{xx:.2f}' y='{y - 3:.2f}' width='5' height='3.4' fill='{CLASSE[k]}' "
                   f"stroke='{C['s_legenda']}' stroke-width='0.3'/>")
        out.append(f"<text x='{xx + 7:.2f}' y='{y:.2f}' font-size='2.8' fill='{C['t_foglio']}' {FONT}>{t}</text>")
    return "\n".join(out)


def chiave_colori(x, y, larg):
    """Ogni colore della tabella C con il suo nome: un campione per tipo.
    Il campione ha lo stesso colore degli oggetti, quindi selezionarlo
    in Illustrator con Stesso colore prende anche tutti quegli oggetti."""
    out = [f"<text x='{x:.2f}' y='{y:.2f}' font-size='3.4' font-weight='bold' fill='{C['t_foglio']}' "
           f"{FONT}>Chiave dei colori (un colore = un tipo di oggetto)</text>"]
    passo_x, passo_y = 46.0, 6.0
    n_col = max(int((larg - 2 * x) // passo_x), 1)
    for i, (k, v) in enumerate(C.items()):
        xx = x + (i % n_col) * passo_x
        yy = y + 6 + (i // n_col) * passo_y
        if k.startswith("s_"):
            out.append(f"<rect x='{xx:.2f}' y='{yy - 3:.2f}' width='5' height='3.4' fill='none' "
                       f"stroke='{v}' stroke-width='0.6'/>")
        elif k.startswith("t_"):
            out.append(f"<text x='{xx:.2f}' y='{yy:.2f}' font-size='3.2' font-weight='bold' fill='{v}' "
                       f"{FONT}>Aa</text>")
        else:
            out.append(f"<rect x='{xx:.2f}' y='{yy - 3:.2f}' width='5' height='3.4' fill='{v}'/>")
        out.append(f"<text x='{xx + 7:.2f}' y='{yy:.2f}' font-size='2.5' fill='{C['t_quote']}' "
                   f"{FONT}>{k} {v}</text>")
    righe = (len(C) + n_col - 1) // n_col
    return "\n".join(out), 8 + righe * passo_y


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
           f"fill='{C['rack']}' stroke='{C['s_rack']}' stroke-width='0.5'/>"]
    for lato in (ox + ORECCHIA / 2, ox + RACK - ORECCHIA / 2):
        yy = oy + 6
        while yy < oy + h_tot - 4:
            tel.append(f"<rect x='{lato - 3.2:.2f}' y='{yy:.2f}' width='6.4' height='3.4' rx='1.7' "
                       f"fill='{C['rack_foro']}' stroke='{C['s_rack']}' stroke-width='0.3'/>")
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
