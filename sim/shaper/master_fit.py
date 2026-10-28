"""Fit dello shaper del MASTER (dec. 139: scatto al centro = 0 dB).
Law [PROVVISORIO, dec. 129]: sopra il centro +6 dB lineari in dB (0 -> +6 da 50 a 100 %);
sotto il centro come il fader, G = 40 log10(2 theta) (-12 dB al 25 %); fondo corsa
chiesto a -140 dB (il VCA si ferma al suo floor; cosi' a freddo resta sotto -90). Pot rovescio (x = 1 - theta): sopra
il centro i diodi sono spenti e la curva dipende solo da resistenze. CV bipolare
(sistema-vca-trim §3.2): +6 dB = uscita positiva (negativa = taglio, come il fader),
da un ramo d'offset verso -5 V. Lo scatto (50 %) pesa 50: li' lo 0 dB deve essere esatto.
Scala 61 mV/dB (x10). Uso: python3 sim/shaper/master_fit.py"""
import math
from shaper_fit import fit
TH = [1, .9, .8, .7, .6, .55, .5, .47, .45, .4, .35, .3, .25, .2, .15, .1, .05, 0]
def law(t):
    if t >= .5:
        return 6 * (t - .5) / .5
    return 40 * math.log10(2 * t) if t > 0 else -140.0
G = [law(t) for t in TH]
W = [10, 10, 10, 10, 10, 50, 50, 10, 10, 8, 6, 5, 4, 3, 1.5, .8, .3, .3]
Y = [-(g - G[0]) * 0.061 for g in G]          # |Vout| relativa a theta = 1
p, r = fit("MASTER", [1 - t for t in TH], Y, [w / 0.061 for w in W], 4,
           [69e3, 20e3, 48e3, 20e3, 32e3, 1.9e3, 2.5e3, 300, 320])
off = 10e3 * 5 / (G[0] * 0.061)
print("  ramo d'offset verso -5 V: %.0f ohm (uscita +%.3f V a fine corsa)" % (off, G[0] * 0.061))
print("  target dB", " ".join("%+6.1f" % g for g in G))
for lab in r:
    print(" ", lab, " ".join("%+6.2f" % (-(a / 0.061) + G[0] - g) for a, g in zip(r[lab], G)), "(errore dB)")
