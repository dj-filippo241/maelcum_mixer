"""Fit dello shaper del FADER (dec. 126: fader mono -> CV -> VCA per lato).
Law [PROVVISORIO, cdj-line-channel §3.8]: quadratica in ampiezza,
G = 40 log10(t) (-12 dB a meta corsa), -100 dB a fondo corsa.
Stessa famiglia e stesso cablaggio del reroute, con un quarto ramo per
il fondo corsa (fader rovescio, 61 mV/dB a
scala x10). Uso: python3 sim/shaper/fader_fit.py"""
import math
from shaper_fit import fit
TH = [1, .975, .95, .90, .85, .775, .70, .575, .45, .325, .20, .10, 0]
G = [40 * math.log10(t) if t > 0 else -100.0 for t in TH]
# a fondo corsa si chiede -115 dB: il VCA si ferma al suo floor (~-100),
# cosi il fader chiuso resta muto anche coi diodi caldi (prima stesura:
# target -100 -> -84...-94 dB in LTspice)
G[-1] = -115.0
W = [10, 10, 10, 8, 8, 6, 6, 4, 3, 1.5, 1.5, .3, .5]
p, r = fit("FADER", [1 - t for t in TH], [-g * 0.061 for g in G], [w / 0.061 for w in W], 4,
           [43e3, 67e3, 350e3, 18e3, 35e3, 2e3, 2.8e3, 2e3, 2.2e3])
print("  target dB", " ".join("%+6.1f" % g for g in G))
for lab in r:
    print(" ", lab, " ".join("%+6.2f" % (-a / 0.061 - g) for a, g in zip(r[lab], G)), "(errore dB)")
