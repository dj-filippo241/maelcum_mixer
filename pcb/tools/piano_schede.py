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


if __name__ == "__main__":
    main()
