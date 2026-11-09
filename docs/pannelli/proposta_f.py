"""Proposta F di disposizione (todo 203, 2026-11-09). BOZZA.

Uso:  python3 docs/pannelli/proposta_f.py
Scrive docs/pannelli/proposta-F.svg e stampa la ricerca e il piano delle schede.
NON tocca coordinate.json né i render dei moduli (dec. 135).

Richiesta di Filippo del 2026-11-09, dopo la proposta E:
- MASTER largo 19" in fondo, poi 5-WAY largo 19";
- sotto, le due colonne della E (filtro, canali, mandate, CUE | MIC e MONO, ritorni);
- canale e mandata su un pannello unico, schede separate (dec. 171);
- nessun pannello cieco: lo spazio che avanza va ai moduli più fitti (mandate, CUE,
  MIC e MONO, ritorni), che diventano più alti; il mixer può diventare più profondo.
Ordine dei comandi invariato (canale in colonna sfalsata, dec. 118); taglie della dec. 169.

Ingegneria [C, PROVVISORIA]: reroute dei ritorni (pot -> CV) nei posti liberi sotto il
5-way; il resto sotto il proprio pannello. Schede come in proposta_d.py.
"""
import math
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import genera_pannelli as g  # noqa: E402
import proposta_e as e  # noqa: E402
from proposta_d import N, P, PI, GR, ME, MP, BOT_G, BOT_P  # noqa: E402

U = e.U
GAP = e.GAP
PASSO = e.ps.PASSO


def canale_send(n, w, aria=0.0):
    """Striscia unica canale + mandata (dec. 171): sopra il canale com'è oggi (dec. 118),
    sotto la sezione FX SEND (EQ HIGH, EQ LOW, LEVEL). Schede separate come nella dec. 91.
    aria = mm in più nella sezione della mandata."""
    p = P(f"CDJ {n}", "canale", w)
    c = w / 2
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
    # sezione FX SEND, separata da una linea
    p.y += aria / 3
    p.el.append(f"<line x1='4' y1='{p.y:.2f}' x2='{w - 4:.2f}' y2='{p.y:.2f}' stroke='{g.C['s_pannello']}' "
                f"stroke-width='0.5'/>")
    p.testo(c, p.y + 5, "FX SEND", 2.8, "bold"); p.y += 9 + aria / 3
    p.manopola(c - 10, p.y + MP + 2, "EQ HIGH", "k_eq_9mm", MP)
    p.manopola(c + 10, p.y + MP + 2, "EQ LOW", "k_eq_9mm", MP)
    p.y += 2 * MP + 12 + aria / 3
    p.manopola(c, p.y + ME + 2, "LEVEL", "k_level_send", ME)
    p.y += 2 * ME + 11
    return p.chiudi()


def disponi(ws):
    W = g.UTILE
    wc, wl = 4 * ws, W - 4 * ws - GAP
    mas, fv = e.master(W), e.five(W)
    fil = e.filtro(wc)
    h0 = canale_send(1, ws).h
    nat = dict(snd=h0 - e.canale(1, ws).h, cue=e.cue(wc).h, mm=max(e.micmono(t, wl / 4).h for t in ("MIC", "MONO")),
               ret=e.fx_ret(0, wl / 4).h)
    top = mas.h + fv.h
    col_a = fil.h + h0 + nat["cue"]
    col_b = nat["mm"] + nat["ret"]
    n_u = math.ceil((top + max(col_a, col_b) + 8) / U)
    L = n_u * U - 8
    # aria: colonna dei canali -> mandate e CUE; colonna destra -> MIC/MONO e ritorni,
    # in proporzione all'altezza naturale
    xa, xb = L - top - col_a, L - top - col_b
    aria = dict(snd=xa * nat["snd"] / (nat["snd"] + nat["cue"]),
                cue=xa * nat["cue"] / (nat["snd"] + nat["cue"]),
                mm=xb * nat["mm"] / col_b, ret=xb * nat["ret"] / col_b)
    can = [canale_send(i + 1, ws, aria["snd"]) for i in range(4)]
    hc = can[0].h
    m = dict(mas=mas, five=fv, fil=fil, can=can,
             cue=e.cue(wc, aria["cue"]),
             mm=[e.micmono("MIC", wl / 4, aria["mm"])] + [e.micmono("MONO", wl / 4, aria["mm"]) for _ in range(3)],
             ret=[e.fx_ret(r, wl / 4, aria["ret"]) for r in range(4)])
    y = dict(mas=0.0, five=mas.h)
    y["fil"] = y["mm"] = top
    y["can"] = top + fil.h
    y["cue"] = y["can"] + hc
    y["ret"] = top + m["mm"][0].h
    P = []

    def riga(nome, n, y0, y1, larg, copie=1, dove="sotto il suo pannello", kmax=None):
        cap = e.capienza(y0, y1, L)
        k = math.ceil(n / cap)
        kmax = kmax if kmax is not None else max(1, int(larg // PASSO))
        P.append(dict(nome=nome, n=n, copie=copie, y0=y0, y1=y1, k=k, kmax=kmax,
                      pieno=n / (k * cap) * 70, dove=dove, ok=k * (copie if larg is None else 1) <= kmax))
    riga("MASTER", N["MASTER"][0], 0, y["five"], W)
    riga("5-WAY", N["5-WAY"][0], y["five"], top, W)
    liberi = P[1]["kmax"] - P[1]["k"]
    riga("REROUTE", N["REROUTE"][0], y["five"], top, None, 4, "posti liberi sotto il 5-way", kmax=liberi)
    riga("FILTRO", N["FILTRO"][0], top, y["can"], wc)
    riga("CANALE+SEND", N["CANALE"][0] + N["FX-SEND"][0], y["can"], y["cue"], ws, 4, "sotto la striscia (schede separate)")
    riga("CUE", N["CUE"][0], y["cue"], L, wc)
    riga("MIC", N["MIC"][0], top, y["ret"], wl / 4)
    riga("MONO", N["MONO"][0], top, y["ret"], wl / 4, 3)
    riga("FX-RET", N["FX-RET"][0], y["ret"], L, wl / 4, 4)
    return dict(ws=ws, wc=wc, wl=wl, m=m, y=y, hc=hc, n_u=n_u, L=L, P=P, aria=aria,
                ok=all(r["ok"] for r in P))


def main():
    prove = [disponi(ws) for ws in [36 + 2 * i for i in range(13)]]
    print("striscia   U   schede ok   aria: mandate  CUE  MIC/MONO  ritorni (mm)")
    for d in prove:
        a = d["aria"]
        print(f"{d['ws']:6.0f} mm {d['n_u']:3d}   {str(d['ok']):5}       {a['snd']:5.0f} {a['cue']:5.0f} "
              f"{a['mm']:7.0f} {a['ret']:8.0f}")
    buone = [d for d in prove if d["ok"]]
    d = min(buone, key=lambda d: (d["n_u"], -(d["P"][4]["kmax"] - d["P"][4]["k"]), d["ws"]))
    disegna(d)


def disegna(d):
    m, L, n_u, y = d["m"], d["L"], d["n_u"], d["y"]
    ox, oy = 14.0, 34.0
    x0 = ox + g.ORECCHIA
    xa, xb = x0, x0 + d["wc"] + GAP
    ws, wl = d["ws"], d["wl"]
    by = {r["nome"]: r for r in d["P"]}
    print(f"\nscelta: striscia {ws:.0f} mm, canali {d['wc']:.0f} mm, colonna destra {wl:.0f} mm, "
          f"{n_u}U = {n_u * U:.0f} mm (utile {L:.0f})")
    print(f"{'modulo':12} {'copie':>5} {'comp.':>5} {'y':>11} {'schede':>6} {'max':>4} {'pieno':>6}  dove")
    tot = 0
    for r in d["P"]:
        tot += r["k"] * r["copie"]
        print(f"{r['nome']:12} {r['copie']:5d} {r['n']:5d} {r['y0']:5.0f}-{r['y1']:4.0f} {r['k']:6d} "
              f"{r['kmax']:4d} {r['pieno']:5.0f}%  {r['dove']}")
    print(f"schede di modulo: {tot}")
    corpo, eti = [], []

    def metti(p, x, yy, h, r=None, testo=None):
        corpo.append(p.svg(x, oy + yy, h))
        if r or testo:
            if testo:
                t, col = testo, "#5a7fb0"
            else:
                t = f"{r['k']} sch. · {r['pieno']:.0f}%" if p.w < 70 else \
                    f"{r['k']} schede · {r['pieno']:.0f} % (max {r['kmax']})"
                col = "#2f7d3a" if r["ok"] and r["pieno"] <= 70.5 else "#b8322a"
            eti.append(f"<rect x='{x + 1:.2f}' y='{oy + yy + h - 6.2:.2f}' width='{p.w - 2:.2f}' height='5.2' "
                       f"rx='1' fill='{col}'/><text x='{x + p.w / 2:.2f}' y='{oy + yy + h - 2.6:.2f}' "
                       f"font-size='2.2' font-weight='bold' fill='#ffffff' text-anchor='middle' {g.FONT}>{t}</text>")

    metti(m["mas"], x0, y["mas"], m["mas"].h, by["MASTER"])
    metti(m["five"], x0, y["five"], m["five"].h, by["5-WAY"])
    metti(m["fil"], xa, y["fil"], m["fil"].h, by["FILTRO"])
    for i in range(4):
        metti(m["can"][i], xa + i * ws, y["can"], d["hc"], by["CANALE+SEND"])
    metti(m["cue"], xa, y["cue"], L - y["cue"], by["CUE"])
    for i, p in enumerate(m["mm"]):
        metti(p, xb + i * wl / 4, y["mm"], p.h, by["MIC"] if i == 0 else by["MONO"])
    for i, p in enumerate(m["ret"]):
        metti(p, xb + i * wl / 4, y["ret"], L - y["ret"], by["FX-RET"])
    corpo.append(g.cieco(GAP, L - y["fil"], "").svg(xa + d["wc"], oy + y["fil"]))

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
                 f"REC, jack dei pedali, MIC, MONO, alimentazione) · davanti: cuffie</text>")
    corpo = tel + corpo + eti
    corpo.append(g.quota_v(ox - 4, oy - 4, oy + L + 4, f"{n_u}U = {n_u * U:.0f} mm"))
    corpo.append(g.quota(xa, xa + d["wc"], oy + L + 9, f"canali {d['wc']:.0f} mm (strisce da {ws:.0f})"))
    corpo.append(g.quota(xb, xb + wl, oy + L + 9, f"{wl:.0f} mm"))
    a = d["aria"]
    note = [
        f"Pannello {n_u}U ({n_u * U:.0f} mm). Proposta E: 10U. Nessun pannello cieco. Schede di modulo: {tot}.",
        f"Aria in più: sezione FX SEND delle strisce +{a['snd']:.0f} mm, CUE +{a['cue']:.0f} mm, MIC e MONO +{a['mm']:.0f} mm, "
        f"ritorni +{a['ret']:.0f} mm.",
        "MASTER e 5-WAY larghi 19\". Reroute dei ritorni (pot -> CV) nei posti liberi sotto il 5-way.",
        "Canali con la colonna sfalsata (dec. 118); SEND e reroute a due a due; HPF e LPF affiancati; cuffie davanti.",
    ]
    yn = oy + L + 20
    corpo.append(f"<text x='14' y='{yn:.2f}' font-size='3' font-weight='bold' fill='{g.C['t_foglio']}' "
                 f"{g.FONT}>verde = sta sotto il suo pannello al 70 % · rosso = no</text>")
    for i, t in enumerate(note):
        corpo.append(f"<text x='14' y='{yn + 5 * (i + 1):.2f}' font-size='2.9' fill='{g.C['t_foglio']}' "
                     f"{g.FONT}>{t}</text>")
    svg = g.foglio("Proposta F: master e 5-way larghi 19\", niente ciechi",
                   "richiesta di Filippo del 9/11 · comandi e taglie della dec. 169 · telaio inclinato "
                   "(dec. 158) · tetto 70 % (dec. 156)",
                   ox + g.RACK + 16, yn + 5 * len(note) + 10, "\n".join(corpo))
    open(os.path.join(QUI, "proposta-F.svg"), "w", encoding="utf-8").write(svg)


if __name__ == "__main__":
    main()
