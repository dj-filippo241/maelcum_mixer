#!/usr/bin/env python3
"""Scrive web/pannello.json: la disposizione F (dec. 172, moduli della dec. 176) con la posizione
assoluta di ogni comando, in mm dall'angolo in alto a sinistra dell'area utile del rack.
Legge docs/pannelli/proposta_f.py, la stessa fonte di coordinate.json e dei render.
Uso: python3 web/tools/pannello.py
"""
import json
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
PANNELLI = os.path.normpath(os.path.join(QUI, "..", "..", "docs", "pannelli"))
sys.path.insert(0, PANNELLI)
import proposta_f as f  # noqa: E402


def main():
    d = f.disponi()
    m, y = d["m"], d["y"]
    ws, wc, wl = d["ws"], d["wc"], d["wl"]
    xb = wc + f.GAP
    moduli = []

    def metti(tipo, i, titolo, p, x, yy, h=None):
        moduli.append(dict(
            tipo=tipo, i=i, titolo=titolo, x=round(x, 2), y=round(yy, 2),
            w=round(p.w, 2), h=round(h if h is not None else p.h, 2),
            comandi=[dict(c, x=round(x + c["x"], 2), y=round(yy + c["y"], 2)) for c in p.comandi]))

    metti("master", 0, "MASTER", m["mas"], 0.0, y["mas"])
    metti("five", 0, "5-WAY", m["five"], 0.0, y["five"])
    metti("filtro", 0, "FILTRO (bus HPF e LPF)", m["fil"], 0.0, y["fil"])
    for i, p in enumerate(m["can"]):
        metti("canale", i, f"CDJ {i + 1}", p, i * ws, y["can"], d["hc"])
    metti("cue", 0, "CUE", m["cue"], 0.0, y["cue"], d["L"] - y["cue"])
    for i, p in enumerate(m["mm"]):
        metti("mic" if i == 0 else "mono", i, "MIC" if i == 0 else f"MONO {i}", p, xb + i * wl / 4, y["mm"])
    for i, p in enumerate(m["ret"]):
        metti("ret", i, f"FX RET {i + 1}", p, xb + i * wl / 4, y["ret"], d["L"] - y["ret"])

    out = dict(
        nota="GENERATO da web/tools/pannello.py (proposta_f.py, disposizione F): non modificare a mano.",
        larghezza=round(f.g.UTILE, 2), altezza=round(d["L"], 2), moduli=moduli)
    dest = os.path.join(QUI, "..", "pannello.json")
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"pannello.json: {len(moduli)} moduli, {sum(len(x['comandi']) for x in moduli)} comandi, "
          f"{out['larghezza']} x {out['altezza']} mm")


if __name__ == "__main__":
    main()
