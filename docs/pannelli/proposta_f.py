"""Proposta F di disposizione (todo 203, 2026-11-09; moduli rifatti da Filippo il 2026-11-10).

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

2026-11-10 (dec. 176): Filippo ridisegna i moduli in Illustrator (moduli-filippo-2026-11-10.pdf);
le posizioni vengono da quel PDF, messe in passo da Claude. La variante col CUE a destra
(proposta-F-cue-destra.svg) resta come archivio e non si rigenera più.

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
from proposta_d import N, P, PI, GR, ME, MP, MG, BOT_G, BOT_P  # noqa: E402

U = e.U
GAP = e.GAP
PASSO = e.ps.PASSO


# Moduli disegnati da Filippo (docs/pannelli/moduli-filippo-2026-11-10.pdf, 2026-11-10): posizioni
# lette dal PDF e messe in passo da Claude (stessi passi, gruppi centrati). Misure in mm dall'angolo
# in alto a sinistra del pannello. Altezze: strisce 317, MIC e MONO 190, ritorni 230, filtro 51,
# CUE 52, master 48, 5-way 102 (13U con master e 5-way in fondo).
PASSO_EQ = 25.86        # colonna EQ del canale
PASSO_SEND = 18.94      # SEND e reroute in colonna sfalsata


def canale_send(n, w, h):
    """Striscia unica canale + mandata (dec. 171). GAIN in alto a sinistra con LINE/PHONO accanto;
    EQ in colonna sfalsata (dec. 118); sezione FX SEND: LEVEL sopra, HIGH e LOW affiancati."""
    p = P(f"CDJ {n}", "canale", w)
    c = w / 2
    p.manopola(12.0, 24.5, "GAIN", "k_gain", PI, True, "dx")
    p.levetta(40.0, 24.5, "l_linea", "LINE", "PHONO", piccola=True)
    for i, b in enumerate(("HIGH", "MID-HIGH", "LOW-MID", "LOW")):
        dx = g.DX if i % 2 == 0 else -g.DX
        p.manopola(c + dx, 43.4 + PASSO_EQ * i, b, "k_eq_canale", GR, True, "sx" if dx > 0 else "dx")
    p.levetta(c + 4, 142.9, "l_filtro", "HPF", "LPF", "OFF", "FILTRO")
    for i, (dx, dy) in enumerate(((-7, 0), (7, 0), (-7, 10), (7, 10))):
        p.bottone(c + dx, 159.9 + dy, f"FX{i + 1}", "fx", *BOT_G)
    p.bottone(c, 182.1, "CUE", "cue", *BOT_P)
    p.meter(c - 13.5, 194.85, 10, passo=6.0, nome="METER")
    p.fader(c + 4, 194.85, 60.0)
    # sezione FX SEND, separata da una linea; y_send e i_send servono a coordinate.json
    p.y_send, p.i_send = 266.4, len(p.comandi)
    p.el.append(f"<line x1='4' y1='{p.y_send:.2f}' x2='{w - 4:.2f}' y2='{p.y_send:.2f}' "
                f"stroke='{g.C['s_pannello']}' stroke-width='0.5'/>")
    p.testo(c, p.y_send + 5, "FX SEND", 2.8, "bold")
    p.manopola(c - 3, 283.6, "LEVEL", "k_level_send", ME, lato="dx")
    p.manopola(c - 15, 302.1, "EQ HIGH", "k_eq_9mm", MP, lato="dx", etichetta="HIGH")
    p.manopola(c + 5, 302.1, "EQ LOW", "k_eq_9mm", MP, lato="dx", etichetta="LOW")
    return p.chiudi(h)


def testa_mm(p, tipo_gain, c):
    """GAIN in alto a sinistra, EQ HIGH ed EQ LOW in colonna sfalsata attorno al centro."""
    p.manopola(18.0, 25.9, "GAIN", "k_gain", GR, lato="dx")
    p.manopola(c + g.DX, 48.3, "EQ HIGH", "k_eq_9mm", PI, lato="sx")
    p.manopola(c - g.DX, 67.3, "EQ LOW", "k_eq_9mm", PI, lato="dx")


def colonna_send(p, c, voci, tipo, det):
    """SEND (o reroute) in colonna sfalsata: sinistra, destra, ... etichetta sotto."""
    for i, nome in enumerate(voci):
        p.manopola(c - 10 if i % 2 == 0 else c + 10, 92.4 + PASSO_SEND * i, nome, tipo, ME, det)


def micmono(tipo, w, h=190.0):
    """MIC e MONO uguali; il MIC ha il MUTE accanto al GAIN."""
    p = P(tipo, "mic", w)
    c = w / 2
    testa_mm(p, tipo, c)
    if tipo == "MIC":
        p.bottone(46.0, 25.9, "MUTE", "mute", 14.0, 9.0)
    colonna_send(p, c, [f"SEND {i + 1}" for i in range(4)], "k_send_mic", False)
    p.led3(c, 171.3)
    return p.chiudi(h)


def fx_ret(r, w, h):
    """Come MIC e MONO in alto; reroute in colonna sfalsata; fader 45 mm col meter."""
    p = P(f"FX RET {r + 1}", "fx", w)
    c = w / 2
    testa_mm(p, "RET", c)
    colonna_send(p, c, ["SELF" if b == r else f"> FX{b + 1}" for b in range(4)], "k_reroute", True)
    p.meter(c - 13.5, 170.93, 10, passo=4.5, nome="METER")
    p.fader(c + 4, 170.93, 45.0)
    return p.chiudi(h)


def filtro(w, h=51.0):
    """Per sezione: FREQ grande al centro e più in alto, RES a sinistra, DRIVE a destra."""
    p = g.Pannello("FILTRO (bus HPF e LPF)", "filtro", w)
    p.el.append(f"<line x1='{w / 2:.2f}' y1='{g.TESTA + 2:.2f}' x2='{w / 2:.2f}' y2='{h - 6:.2f}' "
                f"stroke='{g.C['s_pannello']}' stroke-width='0.6'/>")
    for meta, sez in enumerate(("HPF", "LPF")):
        x0 = meta * w / 2
        p.testo(x0 + 6, 20.0, sez, 3.4, "bold", anchor="start")
        p.manopola(x0 + w / 2 * 0.215, 35.5, "RES", "k_filtro", ME)
        p.manopola(x0 + w / 2 * 0.5, 25.5, "FREQ", "k_filtro", GR)
        p.manopola(x0 + w / 2 * 0.785, 35.5, "DRIVE", "k_filtro", ME)
    return p.chiudi(h)


def cue(w, h=52.0):
    """Cuffie a sinistra, BLEND e LEVEL a destra: due gruppi centrati sui quarti del pannello."""
    p = g.Pannello("CUE", "cue", w)
    for dx, nome in ((-10, "PHONES 1"), (10, "PHONES 2")):
        p.jack(w / 4 + dx, 26.0, nome)
    p.manopola(3 * w / 4 - 10, 27.0, "BLEND", "k_cue", GR, True)
    p.manopola(3 * w / 4 + 10, 27.0, "LEVEL", "k_cue", ME)
    return p.chiudi(h)


def master(w, h=48.0):
    """BOOTH a sinistra, meter L e R al centro col MONO sotto, MASTER a destra; gruppo centrato."""
    p = g.Pannello("MASTER", "master", w)
    c = w / 2
    lm = 20 * 3.0 - 0.8           # larghezza di un meter da 20 segmenti
    p.manopola(c - 106.5, 26.5, "BOOTH", "k_master", GR)
    p.meter(c - 2.4 - lm, 21.0, 20, nome="L", orizz=True)
    p.meter(c + 2.4, 21.0, 20, nome="R", orizz=True)
    p.bottone(c, 32.8, "MONO", "mono", *BOT_G)
    p.manopola(c + 106.5, 26.5, "MASTER", "k_master", MG, True)
    return p.chiudi(h)


def five(w, h=102.0):
    """Una colonna per via a passo costante: nome, LED, GAIN molto grande con la levetta del kill
    a destra, POSITION e WIDTH sotto. GROWL e NASTRO in colonna a destra, meter sul bordo."""
    p = g.Pannello("5-WAY", "five", w)
    passo = 79.4
    for i, b in enumerate(("SUB", "KICK", "MID", "HIGH", "SUPER")):
        x = 39.5 + passo * i
        p.testo(x, 19.0, b, 2.7, "bold")
        if b in LED_5WAY:
            p.led3(x, 23.4)
        p.levetta(x + 29.0, 35.0, "l_kill", "FISSO", "MOLLA")
        p.manopola(x, 46.0, f"GAIN {b}", "k_5w_gain", MG, True, etichetta="GAIN")
        p.manopola(x - 14.75, 78.1, f"POSITION {b}", "k_5w_pos", GR, etichetta="POSITION")
        p.manopola(x + 14.75, 78.1, f"WIDTH {b}", "k_5w_width", GR, etichetta="WIDTH")
    p.manopola(419.0, 29.9, "GROWL", "k_sat", MG)
    p.manopola(419.0, 73.2, "NASTRO", "k_sat", MG)
    p.meter(441.9, 19.0, 10, passo=5.0, nome="METER")
    return p.chiudi(h)


# LED tricolore per via (PDF del 2026-11-10: su quattro vie, SUPER senza) [APERTO]
LED_5WAY = ("SUB", "KICK", "MID", "HIGH")
WS = 50.0               # striscia CDJ


def disponi(ws=WS):
    W = g.UTILE
    wc, wl = 4 * ws, W - 4 * ws - GAP
    mas, fv = master(W), five(W)
    top = mas.h + fv.h
    fil, cu = filtro(wc), cue(wc)
    mm0 = micmono("MIC", wl / 4)
    n_u = math.ceil((top + fil.h + 316.8 + cu.h + 8) / U)   # striscia ~317 mm: 13U
    L = n_u * U - 8
    hc = L - top - fil.h - cu.h              # striscia: 316,85 mm
    hr = L - top - mm0.h                     # ritorno: 229,85 mm
    m = dict(mas=mas, five=fv, fil=fil, cue=cu,
             can=[canale_send(i + 1, ws, hc) for i in range(4)],
             mm=[mm0] + [micmono("MONO", wl / 4) for _ in range(3)],
             ret=[fx_ret(r, wl / 4, hr) for r in range(4)])
    y = dict(mas=0.0, five=mas.h)
    y["fil"] = y["mm"] = top
    y["can"] = top + fil.h
    y["cue"] = y["can"] + hc
    y["ret"] = top + mm0.h
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
    return dict(ws=ws, wc=wc, wl=wl, m=m, y=y, hc=hc, n_u=n_u, L=L, P=P,
                ok=all(r["ok"] for r in P))


def main():
    disegna(scelta())


def scelta(prove=None):
    """Disposizione F coi moduli del 2026-11-10: strisce da 50 mm (misure di Filippo)."""
    return disponi()


def disegna(d, file=None, titolo=None, sotto=None, n_can=4, n_mono=3, stampa=True):
    """Disegna la disposizione; n_can e n_mono < 4 e 3 lasciano posti liberi (setup ridotto)."""
    if stampa:
        _stampa(d)
    corpo, eti = [], []
    _disegna(d, corpo, eti, n_can, n_mono, file, titolo, sotto)


def _stampa(d):
    ws, wl, n_u, L = d["ws"], d["wl"], d["n_u"], d["L"]
    print(f"\nscelta: striscia {ws:.0f} mm, canali {d['wc']:.0f} mm, colonna destra {wl:.0f} mm, "
          f"{n_u}U = {n_u * U:.0f} mm (utile {L:.0f})")
    print(f"{'modulo':12} {'copie':>5} {'comp.':>5} {'y':>11} {'schede':>6} {'max':>4} {'pieno':>6}  dove")
    tot = 0
    for r in d["P"]:
        tot += r["k"] * r["copie"]
        print(f"{r['nome']:12} {r['copie']:5d} {r['n']:5d} {r['y0']:5.0f}-{r['y1']:4.0f} {r['k']:6d} "
              f"{r['kmax']:4d} {r['pieno']:5.0f}%  {r['dove']}")
    print(f"schede di modulo: {tot}")


def _disegna(d, corpo, eti, n_can, n_mono, file, titolo, sotto):
    m, L, n_u, y = d["m"], d["L"], d["n_u"], d["y"]
    ox, oy = 14.0, 34.0
    x0 = ox + g.ORECCHIA
    xa, xb = x0, x0 + d["wc"] + GAP
    ws, wl = d["ws"], d["wl"]
    by = {r["nome"]: r for r in d["P"]}
    tot = sum(r["k"] * r["copie"] for r in d["P"])

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
        if i < n_can:
            metti(m["can"][i], xa + i * ws, y["can"], d["hc"], by["CANALE+SEND"])
        else:
            corpo.append(g.cieco(ws, d["hc"], f"posto CDJ {i + 1}").svg(xa + i * ws, oy + y["can"]))
    metti(m["cue"], xa, y["cue"], L - y["cue"], by["CUE"])
    for i, p in enumerate(m["mm"]):
        if i <= n_mono:
            metti(p, xb + i * wl / 4, y["mm"], p.h, by["MIC"] if i == 0 else by["MONO"])
        else:
            corpo.append(g.cieco(wl / 4, p.h, "posto MONO").svg(xb + i * wl / 4, oy + y["mm"]))
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
    note = [
        f"Pannello {n_u}U ({n_u * U:.0f} mm). Nessun pannello cieco. Schede di modulo: {tot}.",
        "Moduli disegnati da Filippo il 2026-11-10 (moduli-filippo-2026-11-10.pdf), messi in passo da Claude.",
        "MASTER e 5-WAY larghi 19\". Reroute dei ritorni (pot -> CV) nei posti liberi sotto il 5-way.",
        "Canali con la colonna sfalsata (dec. 118); SEND e reroute a due a due; HPF e LPF affiancati; cuffie davanti.",
    ]
    yn = oy + L + 20
    corpo.append(f"<text x='14' y='{yn:.2f}' font-size='3' font-weight='bold' fill='{g.C['t_foglio']}' "
                 f"{g.FONT}>verde = sta sotto il suo pannello al 70 % · rosso = no</text>")
    for i, t in enumerate(note):
        corpo.append(f"<text x='14' y='{yn + 5 * (i + 1):.2f}' font-size='2.9' fill='{g.C['t_foglio']}' "
                     f"{g.FONT}>{t}</text>")
    svg = g.foglio(titolo or "Proposta F: master e 5-way larghi 19\", niente ciechi",
                   sotto or ("richiesta di Filippo del 9/11 · comandi e taglie della dec. 169 · telaio inclinato "
                             "(dec. 158) · tetto 70 % (dec. 156)"),
                   ox + g.RACK + 16, yn + 5 * len(note) + 10, "\n".join(corpo))
    nome = file or "proposta-F.svg"
    open(os.path.join(QUI, nome), "w", encoding="utf-8").write(svg)


if __name__ == "__main__":
    main()
