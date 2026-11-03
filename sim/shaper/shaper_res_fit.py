"""Fit dello SHAPER della RES del filtro (dec. 153, todo 212).
Law (prototipo, filtro.res_law): gres = 8^(-theta/0,9) fino al 90 %, poi
lineare fino a -0,25 a fine corsa; fischio da ~93 %.
Hardware: gres = gpos - gneg, due OTA (filter-module §5).
  gpos = 8^(-theta/0,9) su TUTTA la corsa -> OTA che smorza.
         Shaper della famiglia unica (sistema-shaper.md), manopola cablata
         ROVESCIA: x = 1 - theta, Vx = 5 x; gpos = 0,0990 * 10^(1,003 x),
         esponenziale che accelera verso l'alto come POSITION. Uscita 5 V *
         gpos (0,495 V a fine corsa, 5 V a RES 0). Vicino al fischio
         (x < 0,1) i diodi sono spenti: la curva dipende solo da resistenze.
  gneg = 0,349 * max(0, theta - 0,9) / 0,1 -> OTA che innesca.
         Raddrizzatore di precisione sulla stessa Vx: max(0, 0,5 V - Vx),
         soglia dal riferimento della manopola (raziometrico, niente diodi
         nella soglia). Con gpos(1) = 0,099: gres(1) = -0,25.
Taratura a 35 C; errore a 20/35/50 C. Uso: python3 sim/shaper/shaper_res_fit.py"""
import math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shaper_fit import fit

def law_proto(t):
    if t <= 0.9: return 8 ** (-t / 0.9)
    return 0.125 + (t - 0.9) / 0.1 * (-0.25 - 0.125)
def gpos(t): return 8 ** (-t / 0.9)
A = gpos(1.0) + 0.25            # pendenza del ramo negativo: gneg(1) = A
def gneg(t): return A * max(0.0, t - 0.9) / 0.1

if __name__ == "__main__":
    print("gneg(1) = %.4f; gres hardware vs prototipo, ideale:" % A)
    for t in (0.9, 0.92, 0.93, 0.94, 0.96, 1.0):
        print("  theta %.2f  hw %+.4f  proto %+.4f" % (t, gpos(t) - gneg(t), law_proto(t)))
    TX = [i / 20 for i in range(21)]                 # x = 1 - theta
    Y = [5 * (gpos(1 - x) - gpos(1.0)) for x in TX]
    W = [1 / (5 * gpos(1 - x)) for x in TX]          # errore relativo su gpos
    for nb, p0 in ((2, [25e3, 40e3, 300e3, 20e3, 60e3]), (3, [25e3, 40e3, 300e3, 20e3, 60e3, 10e3, 15e3])):
        p, r = fit("RES gpos %d rami" % nb, TX, Y, W, nb, p0)
        for lab in r:
            print("  %s" % lab, " ".join("%+5.1f" % (100 * ((a + 5 * gpos(1.0)) / (5 * gpos(1 - x)) - 1)) for a, x in zip(r[lab], TX)), "(errore % di gpos; theta da 100 a 0 %)")
