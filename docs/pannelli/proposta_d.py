"""Proposta D di disposizione (todo 203, 2026-11-09). BOZZA.

Uso:  python3 docs/pannelli/proposta_d.py
Scrive docs/pannelli/proposta-D.svg e stampa il piano delle schede.
NON tocca coordinate.json né i render dei moduli (genera_pannelli.py): le PCB prendono
le posizioni da lì (dec. 135) e i render nuovi aspettano l'ok di Filippo.

Regole di Filippo del 2026-11-09 (dec. 170):
- rack 19": larghezza fissa (dec. 157);
- filtro largo come 4 canali; 5-way largo fino a tutta la larghezza;
- CUE in basso, vicino a un angolo;
- connettori tutti dietro, come un mixer DJ; MIC e MONO davanti solo sul bordo,
  dove i cavi non disturbano i comandi;
- tecniche miste: i moduli suonati tanto hanno le schede sotto il pannello; un modulo
  grosso con pochi comandi (master) può stare lontano dai suoi comandi.
Taglie dei comandi: dec. 169 (docs/fase3/sistema-comandi.md).

Ingegneria [C, PROVVISORIA]:
- schede verticali, passo 25 mm, alte 185 mm dietro e 120 mm davanti (dec. 158), tetto 70 %
  (dec. 156) = densità di pcb/tools/piano_schede.py;
- conteggi VERI dove la scheda esiste (pcb/*/NOTE.md), stime per 5-way, CUE e filtro;
- mandata e ritorno dello stesso bus uno sopra l'altro: una scheda per bus sotto i due;
- sotto il 5-way (in fondo, schede alte, vicino al pannello posteriore) stanno anche le
  schede del master (comandi solo CV) e 2 dei 4 reroute (pot → CV); gli altri 2 reroute
  sotto i comandi del master;
- MIC e MONO hanno le prese dietro come tutti (la deroga del bordo davanti non serve);
- RIAA del phono sulla scheda delle prese, dietro: il segnale phono (pochi mV) non
  attraversa il backplane.
"""
import math
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, "..", "..", "pcb", "tools"))
import genera_pannelli as g  # noqa: E402
import piano_schede as ps  # noqa: E402

U = 44.45
S = g.STRISCIA

# taglie della dec. 169: raggio del cappuccio disegnato e passo verticale in colonna
MG, GR, ME, PI, MP = 12.0, 7.5, 6.0, 5.5, 3.0
PASSO_T = {MG: 26.0, GR: 17.0, ME: 15.5, PI: 14.0, MP: 10.5}
BOT_G, BOT_P = (12.0, 8.0), (8.0, 6.0)        # bottone grande / piccolo (w, h)

# componenti per modulo
N = {
    "5-WAY": (970, "stima (piano_schede)"),
    "MASTER": (582, "vero: segnale 283 + uscite 155 + 144"),
    "CUE": (200, "stima"),
    "MIC": (206, "vero"),
    "MONO": (127, "vero"),
    "FX-RET": (199, "vero, scheda di segnale; reroute 225 sotto il 5-way"),
    "REROUTE": (225, "vero (fx-ret-reroute)"),
    "CANALE": (350, "vero 390 meno la RIAA (~40, stima) che va sulla scheda prese"),
    "FX-SEND": (120, "vero"),
    "FILTRO": (450, "stima dec. 159"),
}


class P(g.Pannello):
    def colonna(self, c, voci, r=GR, passo=None):
        for i, voce in enumerate(voci):
            nome, tipo, det = voce[:3]
            rr = voce[3] if len(voce) > 3 else r
            sx = i % 2 == 0
            x = c - g.DX if sx else c + g.DX
            self.manopola(x, self.y + rr + 3, nome, tipo, rr, det, "dx" if sx else "sx")
            self.y += PASSO_T[rr]
        self.y += rr + 4


def canale(n):
    p = P(f"CDJ {n}", "canale", S)
    c = S / 2
    p.levetta(c, p.y + 5, "l_linea", "LINE", "PHONO", piccola=True); p.y += 14
    p.colonna(c, [("GAIN", "k_gain", True, PI)] +
              [(b, "k_eq_canale", True, GR) for b in ("HIGH", "MID-HIGH", "LOW-MID", "LOW")])
    p.levetta(c + 4, p.y + 6, "l_filtro", "HPF", "LPF", "OFF", "FILTRO"); p.y += 18
    for i, (dx, dy) in enumerate(((-7, 0), (7, 0), (-7, 10), (7, 10))):
        p.bottone(c + dx, p.y + 5 + dy, f"FX{i + 1}", "fx", *BOT_G)
    p.y += 22
    p.bottone(c, p.y + 4, "CUE", "cue", *BOT_P); p.y += 11
    p.meter(c - 13.5, p.y + 2, 10, passo=6.0, nome="METER")
    p.fader(c + 4, p.y + 2, 60.0); p.y += 72
    return p.chiudi()


def send(n):
    p = P(f"FX-SEND {n}", "send", S)
    p.colonna(S / 2, [("EQ HIGH", "k_eq_9mm", False, MP), ("EQ LOW", "k_eq_9mm", False, MP),
                      ("LEVEL", "k_level_send", False, ME)])
    return p.chiudi()


def fx_ret(r):
    p = P(f"FX RET {r + 1}", "fx", S)
    c = S / 2
    p.colonna(c, [("GAIN", "k_gain", False, PI), ("EQ HIGH", "k_eq_9mm", False, PI),
                  ("EQ LOW", "k_eq_9mm", False, PI)])
    p.colonna(c, [("SELF" if b == r else f"> FX{b + 1}", "k_reroute", True, ME) for b in range(4)])
    y = p.y
    p.meter(c - 13.5, y + 2, 10, passo=4.5, nome="METER")
    p.fader(c + 4, y + 2, 45.0)
    p.y = y + 57
    return p.chiudi()


def micmono(tipo):
    p = P(tipo, "mic", S)
    c = S / 2
    if tipo == "MIC":
        p.colonna(c, [("GAIN", "k_gain", False, PI), ("EQ HIGH", "k_eq_9mm", False, MP),
                      ("EQ LOW", "k_eq_9mm", False, MP)])
    else:
        p.colonna(c, [("GAIN", "k_gain", False, GR), ("EQ HIGH", "k_eq_9mm", False, PI),
                      ("EQ LOW", "k_eq_9mm", False, PI)])
    p.colonna(c, [(f"SEND {i + 1}", "k_send_mic", False, ME) for i in range(4)])
    p.led3(c, p.y + 3); p.y += 11
    if tipo == "MIC":
        p.bottone(c, p.y + 5, "MUTE", "mute", 14.0, 9.0); p.y += 13
    p.y += 2
    return p.chiudi()


def filtro(w):
    p = P("FILTRO (bus HPF e LPF)", "filtro", w)
    for riga, sez in enumerate(("HPF", "LPF")):
        y = p.y + 9 + riga * 24
        p.testo(7, y + 1, sez, 2.8, "bold", anchor="start")
        for i, (nm, r) in enumerate((("FREQ", GR), ("RES", ME), ("DRIVE", ME))):
            p.manopola(w * (0.33 + 0.24 * i), y, nm, "k_filtro", r)
    p.y += 48
    return p.chiudi()


def five(w):
    p = P("5-WAY", "five", w)
    bande = ("SUB", "KICK", "MID", "HIGH", "SUPER")
    col = (w - 56) / 5
    y0 = p.y
    for i, b in enumerate(bande):
        x = col * i + col / 2 + 2
        p.y = y0
        p.testo(x, p.y + 2, b, 2.7, "bold"); p.y += 9
        p.levetta(x, p.y + 4, "l_kill", "FISSO", "MOLLA", nome="KILL"); p.y += 16
        p.manopola(x, p.y + MG + 2, "GAIN", "k_5w_gain", MG, True); p.y += 2 * MG + 10
        p.manopola(x - 11, p.y + GR, "POSITION", "k_5w_pos", GR)
        p.manopola(x + 11, p.y + GR, "WIDTH", "k_5w_width", GR)
        p.y += 2 * GR + 8
    y = p.y
    x = w - 32
    p.manopola(x, y0 + 16, "GROWL", "k_sat")
    p.manopola(x, y0 + 46, "NASTRO", "k_sat")
    p.meter(w - 10, y0 + 2, 10, passo=5.0, nome="METER")
    p.y = max(y, y0 + 60)
    return p.chiudi()


def master_comandi(w):
    p = P("MASTER", "master", w)
    x = w * 0.33
    p.manopola(x, p.y + 10, "MASTER", "k_master", GR, True)
    p.manopola(x, p.y + 34, "BOOTH", "k_master", ME)
    p.bottone(x, p.y + 52, "MONO", "mono", *BOT_G)
    p.meter(w - 15, p.y + 1, 20, passo=3.0, nome="L")
    p.meter(w - 9, p.y + 1, 20, passo=3.0, nome="R")
    p.y += 66
    return p.chiudi()


def cue(w):
    p = P("CUE", "cue", w)
    x = w / 2
    p.manopola(x, p.y + 10, "BLEND", "k_cue", GR, True)
    p.manopola(x, p.y + 32, "LEVEL", "k_cue", ME)
    p.jack(x - 9, p.y + 52, "PHONES 1")
    p.jack(x + 9, p.y + 52, "PHONES 2")
    p.y += 66
    return p.chiudi()


# ---------------- disposizione ----------------

def capienza(y0, y1, L):
    def h(y):
        return ps.H_DIETRO - (ps.H_DIETRO - ps.H_DAVANTI) * y / L
    return (y1 - y0) * (h(y0) + h(y1)) / 2 * ps.DENS


def main():
    ox, oy = 14.0, 34.0
    x0 = ox + g.ORECCHIA
    W = g.UTILE
    B = 4 * S                       # blocco di quattro strisce: 144 mm
    gap = (W - 3 * B) / 2
    fv, fil = five(W), filtro(B)
    can = [canale(i + 1) for i in range(4)]
    snd = [send(i + 1) for i in range(4)]
    ret = [fx_ret(r) for r in range(4)]
    mm = [micmono("MIC")] + [micmono("MONO") for _ in range(3)]
    wc = B / 2
    ma, cu = master_comandi(wc), cue(wc)
    y_b = fv.h + 4
    xs = [x0, x0 + B + gap, x0 + 2 * (B + gap)]
    h_fil, h_can = fil.h, max(p.h for p in can)
    h_snd, h_ret = max(p.h for p in snd), max(p.h for p in ret)
    h_mm, h_cm = max(p.h for p in mm), max(cu.h, ma.h)
    # colonne: sinistra = mandata sopra ritorno (stesso bus); centro = filtro e canali;
    # destra = MIC e MONO, poi MASTER e CUE nell'angolo davanti a destra
    fondi = {"sinistra": y_b + h_snd + h_ret, "centro": y_b + h_fil + h_can, "destra": y_b + h_mm + h_cm}
    n_u = math.ceil((max(fondi.values()) + 8) / U)

    def piano(L):
        R = []

        def riga(nome, k_n, y0, y1, larg, copie=1, dove="sotto il suo pannello", n=None):
            n_, fonte = N[k_n]
            n = n or n_
            cap = capienza(y0, y1, L)
            k = math.ceil(n / cap)
            kmax = None if larg is None else max(1, int(larg // ps.PASSO))
            R.append(dict(nome=nome, copie=copie, n=n, y0=y0, y1=y1, k=k, kmax=kmax,
                          pieno=n / (k * cap) * 70, dove=dove))
        riga("5-WAY", "5-WAY", 0, fv.h, W)
        riga("FILTRO", "FILTRO", y_b, y_b + h_fil, B)
        riga("CANALE", "CANALE", y_b + h_fil, L, S, 4, "sotto canale e pannello cieco")
        riga("FX-SEND+RET", "FX-RET", y_b, L, S, 4, "una scheda per bus, sotto mandata e ritorno",
             n=N["FX-RET"][0] + N["FX-SEND"][0])
        riga("MIC", "MIC", y_b, y_b + h_mm, S)
        riga("MONO", "MONO", y_b, y_b + h_mm, S, 3)
        riga("CUE", "CUE", y_b + h_mm, L, wc, 1, "sotto CUE e pannello cieco")
        riga("REROUTE", "REROUTE", y_b + h_mm, L, wc, 2, "2 sotto i comandi del MASTER")
        riga("REROUTE", "REROUTE", 0, fv.h, None, 2, "2 sotto il 5-way")
        riga("MASTER", "MASTER", 0, fv.h, None, 1, "sotto il 5-way (comandi solo CV)")
        return R

    while True:
        L = n_u * U - 8
        R = piano(L)
        if all(r["kmax"] is None or r["k"] <= r["kmax"] for r in R):
            break
        n_u += 1
    posti = int(W // ps.PASSO)
    dietro = sum(r["k"] * r["copie"] for r in R if r["kmax"] is None) + R[0]["k"]
    tot = sum(r["k"] * r["copie"] for r in R)
    print(f"pannello {n_u}U = {n_u * U:.0f} mm (utile {L:.0f}); fondo delle colonne: "
          + ", ".join(f"{k} {v:.0f}" for k, v in fondi.items()))
    print(f"altezze: 5-way {fv.h:.0f}, filtro {h_fil:.0f}, canale {h_can:.0f}, send {h_snd:.0f}, "
          f"ritorno {h_ret:.0f}, MIC/MONO {h_mm:.0f}, CUE/MASTER {h_cm:.0f}")
    print(f"{'modulo':11} {'copie':>5} {'comp.':>5} {'y':>11} {'schede':>6} {'max':>4} {'pieno':>6}  dove")
    for r in R:
        print(f"{r['nome']:11} {r['copie']:5d} {r['n']:5d} {r['y0']:5.0f}-{r['y1']:4.0f} {r['k']:6d} "
              f"{r['kmax'] if r['kmax'] else '-':>4} {r['pieno']:5.0f}%  {r['dove']}")
    print(f"sotto il 5-way: {dietro} schede su {posti} posti; schede di modulo: {tot}")

    corpo, eti = [], []

    def metti(p, x, y, h, r=None, testo=None, blu=False):
        corpo.append(p.svg(x, oy + y, h))
        if r is not None or testo:
            if testo:
                t, col = testo, "#5a7fb0"
            else:
                t = f"{r['k']} sch. · {r['pieno']:.0f}%" if p.w < 60 else \
                    f"{r['k']} schede · {r['pieno']:.0f} % (max {r['kmax']})"
                col = "#2f7d3a" if r["pieno"] <= 70.5 else "#b8322a"
            eti.append(f"<rect x='{x + 1:.2f}' y='{oy + y + h - 6.2:.2f}' width='{p.w - 2:.2f}' height='5.2' "
                       f"rx='1' fill='{col}'/><text x='{x + p.w / 2:.2f}' y='{oy + y + h - 2.6:.2f}' "
                       f"font-size='2.2' font-weight='bold' fill='#ffffff' text-anchor='middle' {g.FONT}>{t}</text>")

    def cieco(x, y, w, h, t="pannello cieco"):
        if h > 1:
            corpo.append(g.cieco(w, h, t).svg(x, oy + y))

    by = {r["nome"]: r for r in R}
    metti(fv, x0, 0, fv.h, by["5-WAY"])
    # sinistra
    for i in range(4):
        metti(snd[i], xs[0] + i * S, y_b, h_snd)
        metti(ret[i], xs[0] + i * S, y_b + h_snd, h_ret, by["FX-SEND+RET"])
    cieco(xs[0], fondi["sinistra"], B, L - fondi["sinistra"], "cieco: sotto ci sono le schede dei bus")
    # centro
    metti(fil, xs[1], y_b, h_fil, by["FILTRO"])
    for i in range(4):
        metti(can[i], xs[1] + i * S, y_b + h_fil, h_can, by["CANALE"])
    cieco(xs[1], fondi["centro"], B, L - fondi["centro"], "cieco: sotto, schede dei canali")
    # destra
    for i, p in enumerate(mm):
        metti(p, xs[2] + i * S, y_b, h_mm, by["MIC"] if i == 0 else by["MONO"])
    cieco(xs[2], y_b + h_mm, B, L - h_cm - y_b - h_mm, "cieco: sotto, schede di CUE e reroute")
    metti(ma, xs[2], L - h_cm, h_cm, testo="2 reroute sotto · schede master dietro")
    metti(cu, xs[2] + wc, L - h_cm, h_cm, by["CUE"])
    for x in (x0 + B, x0 + 2 * B + gap):
        cieco(x, y_b, gap, L - y_b, "")

    h_tot = L
    tel = [f"<rect x='{ox:.2f}' y='{oy - 4:.2f}' width='{g.RACK:.2f}' height='{h_tot + 8:.2f}' rx='2' "
           f"fill='{g.C['rack']}' stroke='{g.C['s_rack']}' stroke-width='0.5'/>"]
    for lato in (ox + g.ORECCHIA / 2, ox + g.RACK - g.ORECCHIA / 2):
        yy = oy + 6
        while yy < oy + h_tot - 4:
            tel.append(f"<rect x='{lato - 3.2:.2f}' y='{yy:.2f}' width='6.4' height='3.4' rx='1.7' "
                       f"fill='{g.C['rack_foro']}' stroke='{g.C['s_rack']}' stroke-width='0.3'/>")
            yy += U
    corpo.append(f"<text x='{ox + g.RACK / 2:.2f}' y='{oy - 6:.2f}' font-size='2.8' fill='{g.C['t_quote']}' "
                 f"text-anchor='middle' {g.FONT}>dietro: tutte le prese (RCA con la RIAA, XLR master e booth, "
                 f"REC, jack dei pedali, MIC, MONO, alimentazione)</text>")
    corpo = tel + corpo + eti
    corpo.append(g.quota_v(ox - 4, oy - 4, oy + h_tot + 4, f"{n_u}U = {n_u * U:.0f} mm"))
    note = [
        f"Pannello {n_u}U ({n_u * U:.0f} mm, prima 12-13U). Schede di modulo: {tot}; sotto il 5-way {dietro} su {posti} posti.",
        "Mandata e ritorno dello stesso bus una sopra l'altro: una scheda per bus sotto i due pannelli.",
        "Master: comandi davanti a destra (solo CV), schede sotto il 5-way vicino alle XLR. Sotto i suoi comandi, 2 schede reroute.",
        "Canali: schede sotto canale e cieco; la RIAA del phono sta sulla scheda delle prese, dietro. CUE nell'angolo davanti a destra.",
    ]
    yn = oy + h_tot + 14
    corpo.append(f"<text x='14' y='{yn:.2f}' font-size='3' font-weight='bold' fill='{g.C['t_foglio']}' "
                 f"{g.FONT}>verde = sta al 70 % · blu = schede altrove · rosso = sopra il 70 %</text>")
    for i, t in enumerate(note):
        corpo.append(f"<text x='14' y='{yn + 5 * (i + 1):.2f}' font-size='2.9' fill='{g.C['t_foglio']}' "
                     f"{g.FONT}>{t}</text>")
    larg = ox + g.RACK + 16
    alt = yn + 5 * len(note) + 10
    svg = g.foglio("Proposta D: 5-way largo dietro, tecniche miste",
                   "regole di Filippo del 9/11 (dec. 170) · taglie della dec. 169 · telaio inclinato "
                   "(dec. 158) · tetto 70 % (dec. 156)", larg, alt, "\n".join(corpo))
    open(os.path.join(QUI, "proposta-D.svg"), "w", encoding="utf-8").write(svg)


if __name__ == "__main__":
    main()
