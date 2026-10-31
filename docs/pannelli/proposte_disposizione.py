"""Proposte di disposizione dei moduli sul pannello (todo 203, 2026-10-31). BOZZA.

Uso:  python3 docs/pannelli/proposte_disposizione.py   (lo lancia anche genera_pannelli.py)
Scrive docs/pannelli/proposta-*.svg. Ogni foglio mostra il setup completo e, su ogni modulo,
quante schede servono e quanto sono piene, col telaio inclinato (dec. 158) e il tetto 70 %
(dec. 156). Calcolo e ipotesi: pcb/tools/piano_schede.py. I moduli non cambiano: cambia solo
dove stanno. coordinate.json resta quello di genera_pannelli.py (posizioni dentro i moduli).
"""
import math
import os
import sys

import genera_pannelli as g

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, "..", "..", "pcb", "tools"))
import piano_schede as ps  # noqa: E402

U = 44.45
# colori propri dei fogli di proposta (non toccano la palette dei pannelli)
P = {"ok": "#2f7d3a", "stretto": "#c27a12", "no": "#b8322a", "estesa": "#5a7fb0", "rampa": "#9a9a94"}
assert not set(v.lower() for v in P.values()) & set(v.lower() for v in g.C.values())

# componenti per modulo: stessi numeri di pcb/tools/piano_schede.py
N = {nome: n for nome, _, n, *_ in ps.MODULI}
CHIAVE = {"canale": "CANALE", "send": "FX-SEND", "filtro": "FILTRO", "fx": "FX-RET",
          "five": "5-WAY", "master": "MASTER", "cue": "CUE"}


def chiave(p):
    if p.classe == "mic":
        return "MIC" if p.nome == "MIC" else "MONO"
    return CHIAVE.get(p.classe)


def h_scheda(y):
    """Altezza della scheda a distanza y dal bordo in fondo al pannello (dec. 158, stessa pendenza)."""
    return ps.H_DIETRO - (ps.H_DIETRO - ps.H_DAVANTI) * y / ps.L


def schede(n, y0, y1, larg):
    cap = (y1 - y0) * (h_scheda(y0) + h_scheda(y1)) / 2 * ps.DENS
    k = math.ceil(n / cap)
    kmax = max(1, int(larg // ps.PASSO))
    return k, kmax, n / (k * cap) * 70


def proposta(titolo, sotto, file, alto, blocchi, estendi, note):
    """blocchi: tre liste di righe (sinistra, centro, destra); riga = moduli affiancati.
    estendi: classi di modulo le cui schede scendono sotto il pannello cieco che hanno sotto."""
    ox, oy = 14.0, 34.0
    x0 = ox + g.ORECCHIA
    corpo, rett = [], []
    h_alto = max(p.h for p in alto)
    x = x0
    for p in alto:
        corpo.append(p.svg(x, oy, h_alto))
        rett.append((p, x, oy, h_alto, None))
        x += p.w
    y_basso = oy + h_alto + 6
    alt_blocco = [sum(max(p.h for p in r) for r in b) for b in blocchi]
    h_basso = max(alt_blocco)
    # pannello in unità rack intere (dec. 157): il resto va in pannello cieco in fondo ai blocchi
    n_u = math.ceil((y_basso + h_basso - oy + 8) / U)
    h_basso += n_u * U - (y_basso + h_basso - oy + 8)
    xb = [x0, x0 + g.BLOCCO + g.GAP, x0 + 2 * (g.BLOCCO + g.GAP)]
    for bx, righe in zip(xb, blocchi):
        y = y_basso
        for riga in righe:
            hr = max(p.h for p in riga)
            x = bx
            for p in riga:
                corpo.append(p.svg(x, y, hr))
                rett.append((p, x, y, hr, y_basso + h_basso if p.classe in estendi else None))
                x += p.w
            if x < bx + g.BLOCCO - 0.5:
                corpo.append(g.cieco(bx + g.BLOCCO - x, hr).svg(x, y))
            y += hr
        if y < y_basso + h_basso - 0.5:
            corpo.append(g.cieco(g.BLOCCO, y_basso + h_basso - y).svg(bx, y))
    h_tot = n_u * U - 8
    # schede di ogni modulo
    righe_tab, tot = [], 0
    for p, x, y, h, y_fine in rett:
        k_ = chiave(p)
        if not k_:
            continue
        y0, y1 = y - oy, (y_fine or y + h) - oy
        k, kmax, pieno = schede(N[k_], y0, y1, p.w)
        tot += k
        stato = "ok" if k <= kmax and pieno <= 70.5 else "no"
        if y_fine:
            corpo.append(f"<rect x='{x + 1.2:.2f}' y='{y + h:.2f}' width='{p.w - 2.4:.2f}' "
                         f"height='{y_fine - y - h - 1.2:.2f}' fill='none' stroke='{P['estesa']}' "
                         f"stroke-width='0.5' stroke-dasharray='2 1.2'/>")
            corpo.append(f"<text x='{x + p.w / 2:.2f}' y='{y_fine - 4:.2f}' font-size='2.3' fill='{P['estesa']}' "
                         f"text-anchor='middle' {g.FONT}>schede {p.nome.split(' ')[0]}</text>")
        etichetta = f"{k} sch. · {pieno:.0f}%" if p.w < 60 else f"{k} schede · {pieno:.0f} % (max {kmax})"
        if k > kmax:
            etichetta += " NON STA" if p.w >= 60 else " !"
        corpo.append(f"<rect x='{x + 1:.2f}' y='{y + h - 6.2:.2f}' width='{p.w - 2:.2f}' height='5.2' rx='1' "
                     f"fill='{P[stato]}'/>")
        corpo.append(f"<text x='{x + p.w / 2:.2f}' y='{y + h - 2.6:.2f}' font-size='2.5' font-weight='bold' "
                     f"fill='#ffffff' text-anchor='middle' {g.FONT}>{etichetta}</text>")
    # telaio e rampa delle altezze
    tel = [f"<rect x='{ox:.2f}' y='{oy - 4:.2f}' width='{g.RACK:.2f}' height='{h_tot + 8:.2f}' rx='2' "
           f"fill='{g.C['rack']}' stroke='{g.C['s_rack']}' stroke-width='0.5'/>"]
    for lato in (ox + g.ORECCHIA / 2, ox + g.RACK - g.ORECCHIA / 2):
        yy = oy + 6
        while yy < oy + h_tot - 4:
            tel.append(f"<rect x='{lato - 3.2:.2f}' y='{yy:.2f}' width='6.4' height='3.4' rx='1.7' "
                       f"fill='{g.C['rack_foro']}' stroke='{g.C['s_rack']}' stroke-width='0.3'/>")
            yy += U
    xr = ox + g.RACK + 6
    rampa = [f"<polygon points='{xr:.2f},{oy:.2f} {xr + 8:.2f},{oy:.2f} {xr + 8 * h_scheda(h_tot) / ps.H_DIETRO:.2f},"
             f"{oy + h_tot:.2f} {xr:.2f},{oy + h_tot:.2f}' fill='{P['rampa']}'/>",
             f"<text x='{xr:.2f}' y='{oy - 2:.2f}' font-size='2.5' fill='{g.C['t_quote']}' {g.FONT}>"
             f"schede {h_scheda(0):.0f} mm</text>",
             f"<text x='{xr:.2f}' y='{oy + h_tot + 4:.2f}' font-size='2.5' fill='{g.C['t_quote']}' {g.FONT}>"
             f"{h_scheda(h_tot):.0f} mm</text>",
             f"<text x='{xr:.2f}' y='{oy + h_tot + 8:.2f}' font-size='2.5' fill='{g.C['t_quote']}' {g.FONT}>"
             f"chi suona ↓</text>"]
    corpo = tel + corpo + rampa
    corpo.append(g.quota_v(ox - 4, oy - 4, oy + h_tot + 4, f"{n_u}U = {n_u * U:.0f} mm"))
    larg = ox + g.RACK + 34
    alt = oy + h_tot + 30 + 5 * len(note)
    yn = oy + h_tot + 16
    corpo.append(f"<text x='14' y='{yn:.2f}' font-size='3' font-weight='bold' fill='{g.C['t_foglio']}' {g.FONT}>"
                 f"Schede di modulo: {tot} · verde = sta sotto il suo pannello al 70 %, rosso = no · "
                 f"tratteggio blu = schede sotto il pannello cieco</text>")
    for i, t in enumerate(note):
        corpo.append(f"<text x='14' y='{yn + 5 * (i + 1):.2f}' font-size='2.9' fill='{g.C['t_foglio']}' "
                     f"{g.FONT}>{t}</text>")
    svg = g.foglio(titolo, sotto, larg, alt, "\n".join(corpo))
    open(os.path.join(QUI, file), "w", encoding="utf-8").write(svg)
    return file, n_u, tot


def completo():
    can = [g.canale(i + 1) for i in range(4)]
    snd = [g.send(i + 1) for i in range(4)]
    ret = [g.fx_ret(r) for r in range(4)]
    mm = [g.micmono("MIC")] + [g.micmono("MONO") for _ in range(3)]
    return can, snd, ret, mm, g.filtro(g.BLOCCO)


def banda_alta(w_master=96.0, w_cue=62.0, con_master=True):
    """5-WAY, (MASTER), CUE in fondo al pannello: il 5-WAY prende la larghezza che resta."""
    w_five = g.UTILE - w_cue - (w_master if con_master else 0)
    return [g.five(w_five)] + ([g.master(w_master)] if con_master else []) + [g.cue(w_cue)]


def tutte():
    out = []
    can, snd, ret, mm, fil = completo()
    out.append(proposta(
        "Oggi, con le schede", "disposizione del 21/10 · telaio inclinato (dec. 158) · tetto 70 % (dec. 156)",
        "proposta-0-oggi.svg", banda_alta(), [[mm], [ret], [can, snd, [fil]]], set(),
        ["Il filtro ha schede basse (vicino a chi suona) e solo 75 mm di pannello: gli servono 6 schede, ne stanno 5 (4 core, dec. 159).",
         "Il FX-SEND supera il tetto. Il master chiede 4 schede in 96 mm."]))
    can, snd, ret, mm, fil = completo()
    out.append(proposta(
        "Proposta A: filtro al centro, sotto i ritorni FX", "canali a destra come oggi · master largo 108 mm, "
        "5-way 280 mm",
        "proposta-A.svg", banda_alta(108), [[mm], [ret, [fil]], [can, snd]], {"filtro", "send"},
        ["Il filtro scende sotto i ritorni FX: le sue schede usano il pannello cieco che ha sotto.",
         "Il FX-SEND finisce in basso nella colonna dei canali: la sua scheda scende fino al bordo.",
         "Il master guadagna 12 mm dal 5-way: 4 schede col passo di 25 mm. Il pannello scende a 12U."]))
    can, snd, ret, mm, fil = completo()
    out.append(proposta(
        "Proposta B: master e filtro larghi, davanti", "in fondo solo 5-way (largo 388 mm) e CUE · "
        "filtro sotto MIC e MONO · master sotto i ritorni FX",
        "proposta-B.svg", banda_alta(con_master=False),
        [[mm, [fil]], [ret, [g.master(g.BLOCCO)]], [can, snd]], {"filtro", "master", "send"},
        ["Master e filtro diventano larghi 144 mm, come un blocco di quattro strisce: 5 schede affiancate ciascuno.",
         "Il master sta al centro, davanti, sotto i ritorni FX: è il modulo più vicino a chi suona.",
         "Il 5-way prende tutta la banda in fondo (388 mm): più aria fra le cinque vie. Il pannello resta 12U."]))
    can, snd, ret, mm, fil = completo()
    out.append(proposta(
        "Proposta C: canali al centro, master a destra", "ritorni FX e filtro a sinistra · MIC, MONO e master "
        "a destra, sotto il CUE · 5-way largo 388 mm",
        "proposta-C.svg", banda_alta(con_master=False),
        [[ret, [fil]], [can, snd], [mm, [g.master(g.BLOCCO)]]], {"filtro", "master", "send"},
        ["I canali stanno al centro, come su molti mixer DJ. Master e CUE stanno sullo stesso lato, a destra.",
         "Filtro largo 144 mm sotto i ritorni FX, master largo 144 mm sotto MIC e MONO: 5 schede possibili ciascuno.",
         "Il 5-way prende tutta la banda in fondo (388 mm). Il pannello resta 12U."]))
    return out


if __name__ == "__main__":
    for f, n_u, tot in tutte():
        print(f"{f}: {n_u}U, {tot} schede di modulo")
