#!/usr/bin/env python3
"""Piano delle schede (#203): quante schede servono a ogni modulo col telaio inclinato.

Uso: python3 pcb/tools/piano_schede.py
Ipotesi (decisioni di Filippo del 2026-10-31, nota del #203):
- pannello 19", 13U; y = 0 in fondo al pannello (lontano da chi suona), y cresce verso chi suona;
- telaio inclinato: alto 215 mm dietro (y = 0) e 150 mm davanti (y = L);
- 30 mm di riserva fra pannello, scheda comandi e fondo col backplane: scheda alta 185 -> 120 mm;
- tetto di riempimento 70 %: 200 componenti su 100 x 220 mm (due lati) = densità di riferimento;
- schede verticali sotto il proprio modulo, lunghe quanto il modulo in y, passo minimo 25 mm.
Conteggi: FX-SEND e MASTER segnale veri (pcb/tools/conta.py); gli altri stimati dalla distinta
del budget (docs/budget/genera_budget.py): 12 impronte per chip (taratura sul FX-SEND: 120 / 10),
più trimmer e parti discrete. Incertezza delle stime: circa +-30 %.
"""
import math

L = 572.5                      # lunghezza del pannello completo in y (setup completo)
H_DIETRO, H_DAVANTI = 185.0, 120.0
DENS = 200 / (100 * 220)       # componenti per mm2 di scheda al 70 %
PASSO = 25.0                   # mm fra due schede affiancate (due lati, trimmer, C96)

# y dei blocchi (da genera_pannelli.setup): banda alta 0-104, poi 6 mm, poi banda bassa 110-564.5
Y_ALTO, Y_BASSO = 0.0, 110.0


def h(y):
    return H_DIETRO - (H_DIETRO - H_DAVANTI) * y / L


def capienza(y0, y1):
    """Componenti al 70 % su una scheda che va da y0 a y1 (trapezio)."""
    return (y1 - y0) * (h(y0) + h(y1)) / 2 * DENS


# nome, copie, componenti (stima), da dove, y0, y1, larghezza del pannello, nota
MODULI = [
    ("5-WAY", 1, 970, "stima: 76 chip, 20 trim, GROWL/NASTRO", 0, 104, 292, ""),
    ("MASTER", 1, 600, "segnale 282 vero + uscite ~320 (dec. 142)", 0, 104, 96, ""),
    ("CUE", 1, 200, "stima: 15 chip, finali e limitatori", 0, 104, 62, ""),
    ("MIC", 1, 215, "stima: 15 chip + limiter dec. 145", 110, 300.5, 36, ""),
    ("MONO", 3, 120, "stima: 10 chip", 110, 300.5, 36, ""),
    ("FX-RET", 4, 300, "stima: 20 chip, 41 trim, shaper", 110, 374.5, 36, ""),
    ("CANALE", 4, 362, "stima: 28 chip, 21 trim, RIAA; +1 switch dec. 159", 110, 402.5, 36, ""),
    ("FX-SEND", 4, 120, "vero (fx-send.py)", 402.5, 489.5, 36, ""),
    ("FILTRO", 1, 450, "stima dec. 159: 33 chip, 27 trim, 16 C di film (era 800 a 8 core)", 489.5, 564.5, 144, ""),
]

# zone di pannello cieco nel setup completo: sotto MIC/MONO e sotto i ritorni FX
CIECHI = [("cieco sotto MIC/MONO", 300.5, 564.5, 144), ("cieco sotto FX-RET", 374.5, 564.5, 144)]


def main():
    print(f"{'modulo':9} {'copie':>5} {'comp.':>6} {'y':>13} {'h scheda':>11} {'cap/scheda':>10} "
          f"{'schede':>6} {'max nel pannello':>16}  esito")
    tot = 0
    for nome, copie, n, fonte, y0, y1, larg, _ in MODULI:
        cap = capienza(y0, y1)
        schede = math.ceil(n / cap)
        maxs = max(1, int(larg // PASSO))
        esito = "ok" if schede <= maxs else f"NON STA ({schede} > {maxs})"
        tot += schede * copie
        print(f"{nome:9} {copie:5d} {n:6d} {y0:6.0f}-{y1:5.0f} {h(y0):5.0f}-{h(y1):4.0f} mm {cap:10.0f} "
              f"{schede:6d} {maxs:16d}  {esito}")
    print(f"schede di modulo nel setup completo: {tot}")
    for nome, y0, y1, larg in CIECHI:
        cap = capienza(y0, y1)
        maxs = int(larg // PASSO)
        print(f"{nome}: y {y0:.0f}-{y1:.0f}, {cap:.0f} componenti per scheda, "
              f"{maxs} schede -> {cap * maxs:.0f} componenti")


if __name__ == "__main__" and "--f" not in __import__("sys").argv:
    main()


# ---------------------------------------------------------------------------------------------
# Piano sulla disposizione F (dec. 172), 2026-11-09. Uso: python3 pcb/tools/piano_schede.py --f
# Scrive pcb/PIANO-SCHEDE-F.md. Misure da docs/pannelli/proposta_f.py (unica fonte).
C96_LUNGO = 95.0        # courtyard dell'impronta KiCad DIN41612_C_3x32_Male_Horizontal_THT
LATO_MIN = 100.0        # lato minimo della scheda dove sta il C96 (95 + margini)

# schede vere (pcb/*/NOTE.md) e stime; una riga = una scheda fisica
SCHEDE_F = {
    "canale": [("canale.py (una scheda, C96, dec. 173)", 380, "vero")],
    "fx-send": [("fx-send.py", 120, "vero")],
    "mic": [("mic.py", 206, "vero")],
    "mono": [("mono.py", 127, "vero")],
    "fx-ret": [("fx-ret.py (segnale, C96)", 199, "vero")],
    "reroute": [("fx-ret-reroute.py", 225, "vero")],
    "master": [("master-segnale.py", 283, "vero"), ("master-uscita.py L", 155, "vero"),
               ("master-uscita.py R", 144, "vero")],
    "5-way": [("5-way (da scrivere)", 970, "stima +-30 %")],
    "filtro": [("filtro (da scrivere)", 450, "stima +-30 %")],
    # CUE: 157 impronte ma tante grandi (TO-220, TO-126, 1000 uF, relè, R da 2 W): 177 mm non bastava
    # (giro 1, 113 aperti); lunghezza fissa 196 mm, tutto il pannello da 200 meno 2 mm per lato
    "cue": [("cue.py", 157, "vero", 196.0)],
}


def piano_f():
    import os
    import sys
    qui = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(qui, "..", "..", "docs", "pannelli"))
    import proposta_f as pf
    d = pf.scelta()
    L, y, m = d["L"], d["y"], d["m"]
    W = 450.0

    def hh(yy):
        return H_DIETRO - (H_DIETRO - H_DAVANTI) * yy / L

    righe, avvisi = [], []

    def lungo_y(modulo, copie, y0, y1, larg, schede):
        """Schede da dietro a davanti, affiancate ogni 25 mm; in un posto più schede una dietro
        l'altra, ognuna lunga quanto le serve al 70 % ma almeno LATO_MIN."""
        posti = max(1, int(larg // PASSO))
        usate = [0.0] * posti
        hm = (hh(y0) + hh(y1)) / 2
        for nome, n, fonte in schede:
            for q in range(posti):
                a = y0 + usate[q]
                lun = max(LATO_MIN, n / (hm * DENS))
                for _ in range(5):          # lunghezza al 70 % con l'altezza vera del tratto
                    lun = max(LATO_MIN, n / ((hh(a) + hh(a + lun)) / 2 * DENS))
                if usate[q] + lun <= y1 - y0:
                    usate[q] += lun
                    righe.append((modulo, copie, nome, n, fonte, "dietro-davanti", f"{lun:.0f}",
                                  f"{hh(a):.0f}-{hh(a + lun):.0f}", f"posto {q + 1} di {posti}, y {a:.0f}-{a + lun:.0f}",
                                  n / (lun * (hh(a) + hh(a + lun)) / 2 * DENS) * 70))
                    break
            else:
                avvisi.append(f"{modulo}: {nome} non trova posto ({posti} posti lunghi {y1 - y0:.0f} mm)")

    def lungo_x(modulo, y0, y1, larg, schede):
        """Schede da sinistra a destra, una fila ogni 25 mm in profondità; in una fila più schede
        in fila, ognuna lunga quanto le serve al 70 % ma almeno LATO_MIN."""
        file = max(1, int((y1 - y0) // PASSO))
        usate = [0.0] * file
        for nome, n, fonte, *fisso in schede:
            for f in range(file):
                yf = y0 + (f + 0.5) * (y1 - y0) / file
                lun = fisso[0] if fisso else max(LATO_MIN, n / (hh(yf) * DENS))
                if usate[f] + lun <= larg:
                    usate[f] += lun
                    righe.append((modulo, 1, nome, n, fonte, "sinistra-destra", f"{lun:.0f}", f"{hh(yf):.0f}",
                                  f"fila {f + 1} di {file}, y {yf:.0f}", n / (lun * hh(yf) * DENS) * 70))
                    break
            else:
                avvisi.append(f"{modulo}: {nome} non trova posto in {file} file da {larg:.0f} mm")

    wc, wl = d["wc"], d["wl"]
    lungo_x("MASTER", y["mas"], y["five"], W, SCHEDE_F["master"])
    lungo_x("5-WAY + REROUTE", y["five"], y["five"] + m["five"].h, W,
            SCHEDE_F["5-way"][:0] + [("5-way, parte %d (da scrivere)" % (i + 1), 485, "stima +-30 %") for i in range(2)]
            + SCHEDE_F["reroute"] * 4)
    lungo_x("FILTRO", y["fil"], y["can"], wc, [("filtro, parte %d (da scrivere)" % (i + 1), 225, "stima +-30 %")
                                               for i in range(2)])
    lungo_y("CANALE + FX SEND", 4, y["can"], y["cue"], d["ws"], SCHEDE_F["canale"] + SCHEDE_F["fx-send"])
    lungo_x("CUE", y["cue"], L, wc, SCHEDE_F["cue"])
    lungo_y("MIC", 1, y["mm"], y["ret"], wl / 4, SCHEDE_F["mic"])
    lungo_y("MONO", 3, y["mm"], y["ret"], wl / 4, SCHEDE_F["mono"])
    lungo_y("FX-RET", 4, y["ret"], L, wl / 4, SCHEDE_F["fx-ret"])

    tot = sum(r[1] for r in righe)
    out = ["# Piano delle schede sulla disposizione F (dec. 172)", "",
           "Generato da `pcb/tools/piano_schede.py --f` il 2026-11-09: non modificare a mano. Misure da",
           "`docs/pannelli/proposta_f.py`. Telaio inclinato: schede alte %.0f mm dietro e %.0f davanti (dec. 158);"
           % (H_DIETRO, H_DAVANTI),
           "tetto 70 %% (dec. 156); passo 25 mm; pannello %dU, profondità utile %.0f mm." % (d["n_u"], L), "",
           "Regola nuova: il C96 è lungo %.0f mm (impronta KiCad), quindi il lato della scheda col connettore"
           % C96_LUNGO,
           "è lungo almeno %.0f mm. Sotto i moduli bassi e larghi (MASTER, 5-WAY, FILTRO, CUE) le schede vanno"
           % LATO_MIN,
           "da sinistra a destra; sotto le strisce (canali, MIC, MONO, ritorni) da dietro a davanti. [C, PROVVISORIO]",
           "", "| Modulo | Copie | Scheda | Comp. | Fonte | Verso | Lunga (mm) | Alta (mm) | Dove | Pieno |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for r in righe:
        out.append("| %s | %d | %s | %d | %s | %s | %s | %s | %s | %.0f %% |" % r)
    out += ["", "Schede in tutto: %d." % tot, ""]
    out += ["## Avvisi", ""] + (["- " + a for a in avvisi] or ["- Nessuno: ogni scheda ha il suo posto entro il 70 %."])
    out += ["", "## Aperto", "",
            "- Backplane: quattro tratti, uno per zona (pcb/backplane/PIANO.md, todo 269). PSU-IN nella fila 4 sotto il 5-way.",
            "- 5-way e filtro: stime +-30 %; il 5-way è diviso in due schede da ~485 componenti l'una.",
            "- Schede comandi da disegnare: 5-way, filtro."]
    path = os.path.join(qui, "..", "PIANO-SCHEDE-F.md")   # PIANO-schede.md è il piano del 31/10 (macOS: maiuscole = minuscole)
    open(path, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__" and "--f" in __import__("sys").argv:
    piano_f()
