"""Pannello della lickshot, rack 1U (dec. 188, 190; disposizione approvata, dec. 196).

Uso:  python3 docs/pannelli/lickshot_1u.py
Scrive docs/pannelli/lickshot-1u.svg e docs/pannelli/lickshot-1u.json
(coordinate dei comandi per la scheda, in mm dall'angolo in alto a sinistra
del pannello).

Richiesta di Filippo (2026-11-18): disposizione «simile a quella Klementz».
Del Klementz Lickshot Rack si sa solo cosa dice il benchmark (docs/12,
dec. 188): rack 1U, tutti i comandi su una riga, LED dell'LFO, tasto. Le
foto del rack non sono più in rete (klementz.fr, 18/11). Comandi: solo
quelli della dec. 190, nell'ordine della decisione: ALTEZZA, VELOCITA,
PROFONDITA, VOLUME, TEMPO, RIPETIZIONI, LIVELLO ECO; LED; FIRE.
Scelte di questa bozza (da approvare, la disposizione e di Filippo):
LED accanto a VELOCITA (lampeggia con l'LFO), due gruppi SUONO ed ECO,
FIRE grande a destra. Colori standard come genera_pannelli.py: un colore
per tipo di oggetto. Unita: millimetri.
"""

import json
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
from genera_pannelli import C as C_MIXER, FONT, R14  # noqa: E402

W, H = 482.6, 44.45          # pannello 19" x 1U (EIA)
ORECCHIA = 16.3
FORO_X, FORO_Y = 8.1, 6.35   # asola del rack: dal bordo laterale, da sopra/sotto
Y_POT = 27.0                 # centro delle manopole
Y_ETI = 13.4                 # etichette sopra
D_FIRE = 24.0                # tasto da 24 mm (bozza)

C = dict(C_MIXER)
C.update({
    "p_lickshot": "#e9e4dc",
    "k_lick_suono": "#2f2b27", "k_lick_eco": "#272b2f",
    "b_fire": "#c8352a", "s_fire": "#121210",
    "led_lfo": "#e2492b",
    "s_gruppo": "#7a7a74",
})
assert len(set(v.lower() for v in C.values())) == len(C), "colore ripetuto"
INK, SOFT = C["t_comando"], C["t_piccolo"]

SUONO = [("ALTEZZA", 112.0), ("VELOCITÀ", 146.0), ("PROFONDITÀ", 190.0), ("VOLUME", 224.0)]
LED = ("LFO", 166.0)
ECO = [("TEMPO", 272.0), ("RIPETIZIONI", 306.0), ("LIVELLO ECO", 340.0)]
FIRE = ("FIRE", 404.0)

el, comandi = [], []


def testo(x, y, t, size=2.9, peso="normal", colore=INK, anchor="middle", spazio=0.0):
    el.append(f"<text x='{x:.2f}' y='{y:.2f}' font-size='{size}' font-weight='{peso}' "
              f"letter-spacing='{spazio}' fill='{colore}' text-anchor='{anchor}' {FONT}>{t}</text>")


def manopola(nome, x, tipo):
    r = R14
    comandi.append(dict(tipo="manopola", nome=nome, x=x, y=Y_POT, cappuccio=2 * r))
    el.append(f"<circle cx='{x}' cy='{Y_POT}' r='{r + 1.6:.2f}' fill='none' stroke='{C['s_anello']}' "
              f"stroke-width='0.25' stroke-dasharray='0.6 1.2'/>")
    el.append(f"<circle cx='{x}' cy='{Y_POT}' r='{r}' fill='{C[tipo]}'/>")
    el.append(f"<line x1='{x}' y1='{Y_POT}' x2='{x}' y2='{Y_POT - r + 1}' stroke='{C['k_indice']}' "
              f"stroke-width='0.8' stroke-linecap='round'/>")
    testo(x, Y_ETI, nome)


def gruppo(nome, x0, x1):
    y = 5.6
    el.append(f"<line x1='{x0}' y1='{y}' x2='{x1}' y2='{y}' stroke='{C['s_gruppo']}' stroke-width='0.3'/>")
    w = len(nome) * 1.9 + 4
    xm = (x0 + x1) / 2
    el.append(f"<rect x='{xm - w / 2:.2f}' y='{y - 2:.2f}' width='{w:.2f}' height='4' fill='{C['p_lickshot']}'/>")
    testo(xm, y + 0.9, nome, 2.4, colore=SOFT, spazio=0.4)


# pannello e orecchie
el.append(f"<rect x='0' y='0' width='{W}' height='{H}' rx='0.8' fill='{C['p_lickshot']}' "
          f"stroke='{C['s_pannello']}' stroke-width='0.4'/>")
for x in (FORO_X, W - FORO_X):
    for y in (FORO_Y, H - FORO_Y):
        el.append(f"<rect x='{x - 3.25:.2f}' y='{y - 1.6:.2f}' width='6.5' height='3.2' rx='1.6' "
                  f"fill='{C['rack_foro']}' stroke='{C['s_viti']}' stroke-width='0.3'/>")
for x in (ORECCHIA, W - ORECCHIA):
    el.append(f"<line x1='{x}' y1='2' x2='{x}' y2='{H - 2}' stroke='{C['s_quote']}' "
              f"stroke-width='0.2' stroke-dasharray='1 1'/>")

# nome
testo(26, 27.5, "LICKSHOT", 7.5, "bold", C["t_modulo"], "start", 0.6)
testo(26.4, 34.5, "maelcum", 3.0, colore=SOFT, anchor="start", spazio=0.5)

gruppo("SUONO", 96, 240)
gruppo("ECO", 256, 356)
for nome, x in SUONO:
    manopola(nome, x, "k_lick_suono")
for nome, x in ECO:
    manopola(nome, x, "k_lick_eco")

# LED dell'LFO
nome, x = LED
comandi.append(dict(tipo="led", nome=nome, x=x, y=Y_POT, diametro=3))
el.append(f"<circle cx='{x}' cy='{Y_POT}' r='1.5' fill='{C['led_lfo']}' stroke='{C['s_bottone']}' stroke-width='0.3'/>")
testo(x, Y_ETI, nome, 2.4, colore=SOFT)

# separatore e FIRE
el.append(f"<line x1='372' y1='9' x2='372' y2='{H - 6}' stroke='{C['s_gruppo']}' stroke-width='0.3'/>")
nome, x = FIRE
yf = Y_POT - 1.5
comandi.append(dict(tipo="tasto", nome=nome, x=x, y=yf, diametro=D_FIRE, funzione="premi e tieni"))
el.append(f"<circle cx='{x}' cy='{yf}' r='{D_FIRE / 2 + 1.2}' fill='none' stroke='{C['s_fire']}' stroke-width='0.5'/>")
el.append(f"<circle cx='{x}' cy='{yf}' r='{D_FIRE / 2 - 0.5}' fill='{C['b_fire']}'/>")
testo(x - D_FIRE / 2 - 5, yf + 1.4, "FIRE", 3.6, "bold", anchor="end", spazio=0.4)

# foglio: pannello piu didascalia e quote
M = 10.0
FW, FH = W + 2 * M, H + 2 * M + 26
pan = "\n".join(el)
quote = []


def qt(x, y, t, size=2.6, colore=None, anchor="start", peso="normal"):
    quote.append(f"<text x='{x:.2f}' y='{y:.2f}' font-size='{size}' font-weight='{peso}' "
                 f"fill='{colore or C['t_quote']}' text-anchor='{anchor}' {FONT}>{t}</text>")


qt(M, M - 3, "LICKSHOT · rack 1U · disposizione approvata (dec. 196, 2026-11-18)", 3.2, C["t_bozza"], peso="bold")
y0 = M + H + 7
qt(M, y0, f"Pannello {W} × {H} mm (19\" × 1U). Orecchie da {ORECCHIA} mm con le asole del rack (linee tratteggiate).")
qt(M, y0 + 4.5, "Comandi della dec. 190, su una riga come il Klementz Lickshot Rack (dec. 188): "
   "4 manopole SUONO, LED dell'LFO accanto a VELOCITÀ, 3 manopole ECO, FIRE da 24 mm a destra.")
qt(M, y0 + 9, "Manopole: cappuccio da 15 mm, passo 34 mm. Dietro: jack d'uscita e DC, niente sul pannello. "
   "Colori: un colore per tipo di oggetto, da ridisegnare in Illustrator.")
qt(M, y0 + 13.5, "Fonte: docs/fase4/lickshot.md §1 e §5; generato da docs/pannelli/lickshot_1u.py.")

svg = (f"<svg xmlns='http://www.w3.org/2000/svg' width='{FW}mm' height='{FH}mm' viewBox='0 0 {FW} {FH}'>\n"
       f"<rect width='{FW}' height='{FH}' fill='{C['foglio']}'/>\n"
       f"<g transform='translate({M},{M})'>\n{pan}\n</g>\n" + "\n".join(quote) + "\n</svg>\n")

with open(os.path.join(QUI, "lickshot-1u.svg"), "w") as f:
    f.write(svg)
with open(os.path.join(QUI, "lickshot-1u.json"), "w") as f:
    json.dump(dict(pannello=dict(w=W, h=H), comandi=comandi), f, ensure_ascii=False, indent=1)
print("scritti lickshot-1u.svg e lickshot-1u.json:", len(comandi), "comandi")
