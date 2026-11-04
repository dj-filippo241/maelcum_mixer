"""Legge PIONEER con due piste lineari per lato (pot a 4 sezioni), todo 211.

Legge = prodotto di due partitori lineari caricati (resistenza dal cursore a
massa «b» o al capo alto «t»), con un buffer fra i due. Esito 2026-11-04: col
fine corsa a +6 dB entro 0,3 dB lo scarto massimo dalla curva PIONEER e'
4,7 dB; senza vincolo sul fine corsa 1,8 dB ma il boost sale a +7,8 dB.
Uso: python3 sim/eq-iso/legge_pot_4sezioni.py
"""
import math
def pio(t):
    x = 2*t; return min(x, 1)**1.5 + max(x-1, 0)
TH = [i/100 for i in range(5, 101)]
def db(x): return 20*math.log10(x)
def kb(t, a):  # pista caricata verso massa (a = Rl/Rp)
    return t/(1 + t*(1-t)/a) if a < 1e8 else t
def kt(t, a):  # pista caricata verso il capo alto
    return 1 - kb(1-t, a)
FAM = {"b": kb, "t": kt}
A = [10**(i/20) for i in range(-40, 61)] + [1e9]
best = []
for n1, f1 in FAM.items():
  for n2, f2 in FAM.items():
    for a1 in A:
      for a2 in A:
        F = lambda t: f1(t, a1)*f2(t, a2)
        g5 = F(0.5); g1 = F(1.0)
        e = 0
        for t in TH:
            ee = abs(db(F(t)/g5) - db(pio(t)))
            if t < 0.1: ee *= 0.3
            e = max(e, ee)
        best.append((round(e, 2), round(db(g1/g5) - 6.02, 2), n1, round(a1, 3), n2, round(a2, 3)))
best.sort()
for b in best[:5]: print(b)
ok = [b for b in best if abs(b[1]) < 0.3]
print("con fine corsa +6 entro 0,3 dB:", ok[:3])
