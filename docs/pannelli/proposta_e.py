"""Proposta E di disposizione (todo 203, 2026-11-09). BOZZA.

Uso:  python3 docs/pannelli/proposta_e.py
Scrive docs/pannelli/proposta-E.svg e stampa la ricerca delle misure e il piano delle schede.
NON tocca coordinate.json né i render dei moduli (dec. 135).

Richiesta di Filippo del 2026-11-09, dopo la proposta D:
- una colonna: filtro, 4 canali CDJ, sotto di loro le FX-SEND, in fondo il CUE;
- accanto: MASTER in cima, poi 5-WAY, poi MIC e MONO, poi i ritorni FX;
- tutte le misure dei moduli libere; fissi solo i comandi e le loro taglie (dec. 169);
- regole della dec. 170 (19", connettori dietro, CUE in un angolo in basso).

Ingegneria [C, PROVVISORIA]: i comandi di ogni modulo si dispongono a file, nell'ordine
dei moduli di oggi, quante ne stanno nella larghezza; la ricerca prova le larghezze della
striscia dei canali e tiene quella col pannello più corto in unità rack intere; a pari U,
quella che lascia due posti scheda al canale (oggi canale e isolator sono due schede).
Schede come in proposta_d.py (passo 25 mm, 185 -> 120 mm, tetto 70 %).
"""
import math
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, "..", "..", "pcb", "tools"))
import genera_pannelli as g  # noqa: E402
import piano_schede as ps  # noqa: E402
from proposta_d import MG, GR, ME, PI, MP, BOT_G, BOT_P, N  # noqa: E402

U = 44.45
GAP = 6.0            # fra le due colonne


def k(nome, tipo, r, det=False):
    return dict(t="k", nome=nome, tipo=tipo, r=r, det=det, w=max(2 * r + 6, 16.0), h=2 * r + 11)


def lev(tipo, su, giu, centro=None, piccola=False):
    return dict(t="lev", tipo=tipo, su=su, giu=giu, centro=centro, piccola=piccola, w=20.0, h=21.0)


def bot(nome, tipo, wh):
    return dict(t="bot", nome=nome, tipo=tipo, bw=wh[0], bh=wh[1], w=wh[0] + 3, h=wh[1] + 4)


def led():
    return dict(t="led", w=16.0, h=11.0)


def jack(nome):
    return dict(t="jack", nome=nome, w=20.0, h=17.0)


def meter_h(nome, n, passo=3.0):
    return dict(t="mh", nome=nome, n=n, passo=passo, w=n * passo + 4, h=9.0)


BR = dict(t="br", w=0, h=0)


def modulo(nome, classe, w, voci, fader=None):
    """Pannello largo w coi comandi in file, poi l'eventuale fader col meter."""
    p = g.Pannello(nome, classe, w)
    disp = w - 6
    righe, riga, somma = [], [], 0.0
    for v in voci:
        if v["t"] == "br" or (riga and somma + v["w"] > disp):
            if riga:
                righe.append(riga)
            riga, somma = [], 0.0
            if v["t"] == "br":
                continue
        riga.append(v)
        somma += v["w"]
    if riga:
        righe.append(riga)
    for riga in righe:
        tot = sum(v["w"] for v in riga)
        x = (w - tot) / 2
        rh = max(v["h"] for v in riga)
        for v in riga:
            cx = x + v["w"] / 2
            y = p.y
            if v["t"] == "k":
                p.manopola(cx, y + v["r"] + 2, v["nome"], v["tipo"], v["r"], v["det"])
            elif v["t"] == "lev":
                p.levetta(cx, y + 8, v["tipo"], v["su"], v["giu"], v["centro"], piccola=v["piccola"])
            elif v["t"] == "bot":
                p.bottone(cx, y + v["bh"] / 2 + 1, v["nome"], v["tipo"], v["bw"], v["bh"])
            elif v["t"] == "led":
                p.led3(cx, y + 3)
            elif v["t"] == "jack":
                p.jack(cx, y + 5, v["nome"])
            elif v["t"] == "mh":
                p.meter(x + 2, y + 4, v["n"], passo=v["passo"], orizz=True, nome=v["nome"])
            x += v["w"]
        p.y += rh + 1
    if fader:
        c = w / 2
        p.meter(c - 12, p.y + 2, 10, passo=fader / 10, nome="METER")
        p.fader(c + 4, p.y + 2, fader)
        p.y += fader + 13
    return p.chiudi()


def canale(n, w):
    return modulo(f"CDJ {n}", "canale", w, [
        lev("l_linea", "LINE", "PHONO", piccola=True), k("GAIN", "k_gain", PI, True), BR,
        k("HIGH", "k_eq_canale", GR, True), k("MID-HIGH", "k_eq_canale", GR, True),
        k("LOW-MID", "k_eq_canale", GR, True), k("LOW", "k_eq_canale", GR, True), BR,
        lev("l_filtro", "HPF", "LPF", "OFF"), BR,
        bot("FX1", "fx", BOT_G), bot("FX2", "fx", BOT_G), bot("FX3", "fx", BOT_G), bot("FX4", "fx", BOT_G), BR,
        bot("CUE", "cue", BOT_P)], fader=60.0)


def send(n, w):
    return modulo(f"FX-SEND {n}", "send", w, [
        k("EQ HIGH", "k_eq_9mm", MP), k("EQ LOW", "k_eq_9mm", MP), k("LEVEL", "k_level_send", ME)])


def filtro(w):
    return modulo("FILTRO (bus HPF e LPF)", "filtro", w, [
        k("HPF FREQ", "k_filtro", GR), k("HPF RES", "k_filtro", ME), k("HPF DRIVE", "k_filtro", ME),
        k("LPF FREQ", "k_filtro", GR), k("LPF RES", "k_filtro", ME), k("LPF DRIVE", "k_filtro", ME)])


def cue(w):
    return modulo("CUE", "cue", w, [k("BLEND", "k_cue", GR, True), k("LEVEL", "k_cue", ME),
                                   jack("PHONES 1"), jack("PHONES 2")])


def master(w):
    return modulo("MASTER", "master", w, [
        k("MASTER", "k_master", GR, True), k("BOOTH", "k_master", ME), bot("MONO", "mono", BOT_G),
        meter_h("L", 20), meter_h("R", 20)])


def micmono(tipo, w):
    if tipo == "MIC":
        v = [k("GAIN", "k_gain", PI), k("EQ HIGH", "k_eq_9mm", MP), k("EQ LOW", "k_eq_9mm", MP)]
    else:
        v = [k("GAIN", "k_gain", GR), k("EQ HIGH", "k_eq_9mm", PI), k("EQ LOW", "k_eq_9mm", PI)]
    v += [BR] + [k(f"SEND {i + 1}", "k_send_mic", ME) for i in range(4)] + [BR, led()]
    if tipo == "MIC":
        v.append(bot("MUTE", "mute", (14.0, 9.0)))
    return modulo(tipo, "mic", w, v)


def fx_ret(r, w):
    return modulo(f"FX RET {r + 1}", "fx", w, [
        k("GAIN", "k_gain", PI), k("EQ HIGH", "k_eq_9mm", PI), k("EQ LOW", "k_eq_9mm", PI), BR] +
        [k("SELF" if b == r else f"> FX{b + 1}", "k_reroute", ME, True) for b in range(4)], fader=45.0)


def five(w):
    """5-WAY: una colonna per via (KILL, GAIN, POSITION, WIDTH), GROWL e NASTRO a destra.
    Se la colonna è stretta, POSITION e WIDTH stanno una sopra l'altra."""
    p = g.Pannello("5-WAY", "five", w)
    bande = ("SUB", "KICK", "MID", "HIGH", "SUPER")
    col = (w - 40) / 5
    y0 = p.y
    for i, b in enumerate(bande):
        x = col * i + col / 2 + 2
        p.y = y0
        p.testo(x, p.y + 2, b, 2.7, "bold"); p.y += 9
        p.levetta(x, p.y + 4, "l_kill", "FISSO", "MOLLA"); p.y += 15
        p.manopola(x, p.y + MG + 2, "GAIN", "k_5w_gain", MG, True); p.y += 2 * MG + 10
        if col >= 40:
            p.manopola(x - 11, p.y + GR, "POSITION", "k_5w_pos", GR)
            p.manopola(x + 11, p.y + GR, "WIDTH", "k_5w_width", GR)
            p.y += 2 * GR + 8
        else:
            for nm, tp in (("POSITION", "k_5w_pos"), ("WIDTH", "k_5w_width")):
                p.manopola(x, p.y + GR, nm, tp, GR)
                p.y += 2 * GR + 9
    y = p.y
    p.manopola(w - 24, y0 + 16, "GROWL", "k_sat")
    p.manopola(w - 24, y0 + 46, "NASTRO", "k_sat")
    p.meter(w - 8, y0 + 2, 10, passo=5.0, nome="METER")
    p.y = max(y, y0 + 60)
    return p.chiudi()


def capienza(y0, y1, L):
    def h(y):
        return ps.H_DIETRO - (ps.H_DIETRO - ps.H_DAVANTI) * y / L
    return (y1 - y0) * (h(y0) + h(y1)) / 2 * ps.DENS


def disponi(ws):
    """ws = larghezza di una striscia dei canali. Ritorna moduli, posizioni e piano."""
    W = g.UTILE
    wc = 4 * ws
    wl = W - wc - GAP
    m = dict(fil=filtro(wc), can=[canale(i + 1, ws) for i in range(4)],
             snd=[send(i + 1, ws) for i in range(4)], cue=cue(wc),
             mas=master(wl), five=five(wl), mm=[micmono("MIC", wl / 4)] + [micmono("MONO", wl / 4) for _ in range(3)],
             ret=[fx_ret(r, wl / 4) for r in range(4)])
    hc = max(p.h for p in m["can"])
    hs = max(p.h for p in m["snd"])
    hm = max(p.h for p in m["mm"])
    hr = max(p.h for p in m["ret"])
    ya = dict(fil=0.0, can=m["fil"].h, snd=m["fil"].h + hc)
    fondo_a = ya["snd"] + hs + m["cue"].h
    yb = dict(mas=0.0, five=m["mas"].h, mm=m["mas"].h + m["five"].h)
    yb["ret"] = yb["mm"] + hm
    fondo_b = yb["ret"] + hr
    n_u = math.ceil((max(fondo_a, fondo_b) + 8) / U)
    L = n_u * U - 8
    ya["cue"] = L - m["cue"].h
    P = []

    def riga(nome, n, y0, y1, larg, copie=1, dove="sotto il suo pannello"):
        cap = capienza(y0, y1, L)
        kk = math.ceil(n / cap)
        kmax = max(1, int(larg // ps.PASSO))
        P.append(dict(nome=nome, n=n, copie=copie, y0=y0, y1=y1, k=kk, kmax=kmax,
                      pieno=n / (kk * cap) * 70, dove=dove, ok=kk <= kmax))
    riga("FILTRO", N["FILTRO"][0], 0, ya["can"], wc)
    riga("CANALE+SEND", N["CANALE"][0] + N["FX-SEND"][0], ya["can"], ya["cue"], ws, 4,
         "sotto canale, mandata e cieco")
    riga("CUE", N["CUE"][0], ya["cue"], L, wc)
    riga("MASTER", N["MASTER"][0], 0, yb["five"], wl)
    riga("5-WAY", N["5-WAY"][0], yb["five"], yb["mm"], wl)
    riga("MIC", N["MIC"][0], yb["mm"], yb["ret"], wl / 4)
    riga("MONO", N["MONO"][0], yb["mm"], yb["ret"], wl / 4, 3)
    riga("FX-RET", N["FX-RET"][0], yb["ret"], L, wl / 4, 4, "sotto ritorno e cieco")
    # reroute (pot -> CV), tecniche miste: sotto ogni MONO resta un posto libero; lì la scheda
    # del reroute scende dal MONO fino al bordo davanti. Quello del bus sotto il MIC (che usa
    # due posti) va nei posti liberi sotto il 5-way.
    nr, cap_lungo = N["REROUTE"][0], capienza(yb["mm"], L, L)
    mono, ret, five_r = P[6], P[7], P[4]
    sotto_mono = mono["k"] + 1 <= mono["kmax"] and ret["k"] + 1 <= ret["kmax"] and nr <= cap_lungo
    cap5 = capienza(yb["five"], yb["mm"], L)
    k5 = math.ceil(nr / cap5)
    if sotto_mono and five_r["k"] + k5 <= five_r["kmax"]:
        P.append(dict(nome="REROUTE", n=nr, copie=3, y0=yb["mm"], y1=L, k=1, kmax=1,
                      pieno=nr / cap_lungo * 70, dove="posto libero sotto MONO e ritorno", ok=True))
        P.append(dict(nome="REROUTE bus 1", n=nr, copie=1, y0=yb["five"], y1=yb["mm"], k=k5,
                      kmax=five_r["kmax"] - five_r["k"], pieno=nr / (k5 * cap5) * 70,
                      dove="bus del MIC: sotto il 5-way", ok=True))
    else:
        P.pop()
        riga("FX-RET+REROUTE", N["FX-RET"][0] + nr, yb["ret"], L, wl / 4, 4, "sotto ritorno e cieco")
    return dict(ws=ws, wc=wc, wl=wl, m=m, ya=ya, yb=yb, hc=hc, hs=hs, hm=hm, hr=hr, n_u=n_u, L=L,
                P=P, ok=all(r["ok"] for r in P), fondo_a=fondo_a, fondo_b=fondo_b)


def main():
    prove = [disponi(ws) for ws in [36 + 2 * i for i in range(20)]]
    print("striscia  colonna canali  colonna destra   U   schede ok")
    for d in prove:
        print(f"{d['ws']:6.0f} mm {d['fondo_a']:10.0f} {d['fondo_b']:14.0f} {d['n_u']:6d}   {d['ok']}")
    buone = [d for d in prove if d["ok"]]
    d = min(buone, key=lambda d: (d["n_u"], -(d["P"][1]["kmax"] - d["P"][1]["k"]), d["ws"]))
    disegna(d)


def disegna(d):
    m, L, n_u = d["m"], d["L"], d["n_u"]
    ox, oy = 14.0, 34.0
    x0 = ox + g.ORECCHIA
    xa, xb = x0, x0 + d["wc"] + GAP
    ws, wl = d["ws"], d["wl"]
    by = {r["nome"]: r for r in d["P"]}
    print(f"\nscelta: striscia {ws:.0f} mm, canali {d['wc']:.0f} mm, colonna destra {wl:.0f} mm, "
          f"{n_u}U = {n_u * U:.0f} mm (utile {L:.0f})")
    print(f"{'modulo':15} {'copie':>5} {'comp.':>5} {'y':>11} {'schede':>6} {'max':>4} {'pieno':>6}  dove")
    tot = 0
    for r in d["P"]:
        tot += r["k"] * r["copie"]
        print(f"{r['nome']:15} {r['copie']:5d} {r['n']:5d} {r['y0']:5.0f}-{r['y1']:4.0f} {r['k']:6d} "
              f"{r['kmax']:4d} {r['pieno']:5.0f}%  {r['dove']}")
    print(f"schede di modulo: {tot}")
    corpo, eti = [], []

    def metti(p, x, y, h, r=None):
        corpo.append(p.svg(x, oy + y, h))
        if r:
            t = f"{r['k']} sch. · {r['pieno']:.0f}%" if p.w < 70 else \
                f"{r['k']} schede · {r['pieno']:.0f} % (max {r['kmax']})"
            col = "#2f7d3a" if r["ok"] and r["pieno"] <= 70.5 else "#b8322a"
            eti.append(f"<rect x='{x + 1:.2f}' y='{oy + y + h - 6.2:.2f}' width='{p.w - 2:.2f}' height='5.2' "
                       f"rx='1' fill='{col}'/><text x='{x + p.w / 2:.2f}' y='{oy + y + h - 2.6:.2f}' "
                       f"font-size='2.2' font-weight='bold' fill='#ffffff' text-anchor='middle' {g.FONT}>{t}</text>")

    def cieco(x, y, w, h, t="pannello cieco"):
        if h > 1:
            corpo.append(g.cieco(w, h, t).svg(x, oy + y))

    ya, yb = d["ya"], d["yb"]
    metti(m["fil"], xa, ya["fil"], m["fil"].h, by["FILTRO"])
    for i in range(4):
        metti(m["can"][i], xa + i * ws, ya["can"], d["hc"], by["CANALE+SEND"])
        metti(m["snd"][i], xa + i * ws, ya["snd"], d["hs"])
    cieco(xa, ya["snd"] + d["hs"], d["wc"], ya["cue"] - ya["snd"] - d["hs"], "cieco: sotto, schede dei canali")
    metti(m["cue"], xa, ya["cue"], m["cue"].h, by["CUE"])
    metti(m["mas"], xb, yb["mas"], m["mas"].h, by["MASTER"])
    metti(m["five"], xb, yb["five"], m["five"].h, by["5-WAY"])
    for i, p in enumerate(m["mm"]):
        metti(p, xb + i * wl / 4, yb["mm"], d["hm"], by["MIC"] if i == 0 else by["MONO"])
    for i, p in enumerate(m["ret"]):
        metti(p, xb + i * wl / 4, yb["ret"], d["hr"], by.get("FX-RET+REROUTE") or by["FX-RET"])
    cieco(xb, yb["ret"] + d["hr"], wl, L - yb["ret"] - d["hr"], "cieco: sotto, schede dei ritorni")
    cieco(xa + d["wc"], 0, GAP, L, "")

    tel = [f"<rect x='{ox:.2f}' y='{oy - 4:.2f}' width='{g.RACK:.2f}' height='{L + 8:.2f}' rx='2' "
           f"fill='{g.C['rack']}' stroke='{g.C['s_rack']}' stroke-width='0.5'/>"]
    for lato in (ox + g.ORECCHIA / 2, ox + g.RACK - g.ORECCHIA / 2):
        yy = oy + 6
        while yy < oy + L - 4:
            tel.append(f"<rect x='{lato - 3.2:.2f}' y='{yy:.2f}' width='6.4' height='3.4' rx='1.7' "
                       f"fill='{g.C['rack_foro']}' stroke='{g.C['s_rack']}' stroke-width='0.3'/>")
            yy += U
    corpo.append(f"<text x='{ox + g.RACK / 2:.2f}' y='{oy - 6:.2f}' font-size='2.8' fill='{g.C['t_quote']}' "
                 f"text-anchor='middle' {g.FONT}>dietro: tutte le prese (RCA con la RIAA, XLR master e booth, "
                 f"REC, jack dei pedali, MIC, MONO, alimentazione)</text>")
    corpo = tel + corpo + eti
    corpo.append(g.quota_v(ox - 4, oy - 4, oy + L + 4, f"{n_u}U = {n_u * U:.0f} mm"))
    corpo.append(g.quota(xa, xa + d["wc"], oy + L + 9, f"canali {d['wc']:.0f} mm (strisce da {ws:.0f})"))
    corpo.append(g.quota(xb, xb + wl, oy + L + 9, f"{wl:.0f} mm"))
    note = [
        f"Pannello {n_u}U ({n_u * U:.0f} mm). Proposta D: 11U. Schede di modulo: {tot}.",
        f"Strisce dei canali larghe {ws:.0f} mm: sotto ogni striscia la scheda del canale e quella della sua mandata.",
        "Master in cima. Reroute (pot -> CV): sotto ogni MONO un posto libero, la scheda scende fino al ritorno; quello del bus 1 sotto il 5-way.",
        "Le misure sono il risultato della ricerca: i comandi si dispongono a file nell'ordine di oggi.",
    ]
    yn = oy + L + 20
    corpo.append(f"<text x='14' y='{yn:.2f}' font-size='3' font-weight='bold' fill='{g.C['t_foglio']}' "
                 f"{g.FONT}>verde = sta sotto il suo pannello al 70 % · rosso = no</text>")
    for i, t in enumerate(note):
        corpo.append(f"<text x='14' y='{yn + 5 * (i + 1):.2f}' font-size='2.9' fill='{g.C['t_foglio']}' "
                     f"{g.FONT}>{t}</text>")
    svg = g.foglio("Proposta E: colonna dei canali, master in cima",
                   "richiesta di Filippo del 9/11 · misure libere, comandi e taglie della dec. 169 · "
                   "telaio inclinato (dec. 158) · tetto 70 % (dec. 156)",
                   ox + g.RACK + 16, yn + 5 * len(note) + 10, "\n".join(corpo))
    open(os.path.join(QUI, "proposta-E.svg"), "w", encoding="utf-8").write(svg)


if __name__ == "__main__":
    main()
