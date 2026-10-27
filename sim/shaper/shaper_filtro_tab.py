#!/usr/bin/env python3
"""Tabella dello shaper di frequenza del filtro (law dec. 102) dal log di
shaper-filtro-freq.cir (sezione LPF) o, con --hp, di shaper-filtro-freq-hpf.cir
(sezione HPF, law dec. 137: 20 Hz a 0 %). Zero e fondo scala tarati a 35 C su 25 % e 75 %
di corsa (zona a sole resistenze). Stampa frequenza ed errore a 20/35/50 C."""
import re, math, sys
s = open([a for a in sys.argv[1:] if a != '--hp'][0], errors='ignore').read()
HP = '--hp' in sys.argv
pts = [0, 0.025, 0.05, 0.085, 0.10, 0.25, 0.40, 0.50, 0.60, 0.75, 0.90, 0.95, 0.975, 1.0]
def tgt(t):
    if HP and t <= 0.95: return 20 * 1000 ** (t / 0.95)
    if t <= 0.05: return 10 * 2 ** (t / 0.05)
    if t <= 0.95: return 20 * 1000 ** ((t - 0.05) / 0.9)
    return 20000 * 1.75 ** ((t - 0.95) / 0.05)
V = {}
for p in list(pts):
    if 'Measurement: v%04d\n' % int(p * 1000) not in s:
        pts.remove(p); continue
    b = s.split('Measurement: v%04d\n' % int(p * 1000))[1].split('Measurement')[0]
    V[p] = [float(x) for x in re.findall(r'^\s+\d+\s+(\S+)', b, re.M)]
a, c = V[0.25][1], V[0.75][1]
k = math.log2(tgt(0.75) / tgt(0.25)) / (a - c)
print('V/ottava: %.4f   uscita a 0 %% / 100 %%: %+.3f / %+.3f V' % (1 / k, V[0][1], V[1.0][1]))
print('theta    target       20 C              35 C              50 C')
for p in pts:
    row = []
    for i in range(3):
        f = tgt(0.25) * 2 ** ((a - V[p][i]) * k)
        row.append('%8.1f (%+5.1f%%)' % (f, 100 * (f / tgt(p) - 1)))
    print('%5.1f%% %8.1f  ' % (100 * p, tgt(p)) + '  '.join(row))
