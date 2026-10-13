#!/usr/bin/env python3
"""Griglia del drive v0.4 da un log di drive2-chain: per ogni nodo di mix
(g = GROWL, t = NASTRO; 05…99 = posizione manopola %) e per ogni livello
di programma stampa THD % e variazione di livello RMS in dB rispetto
all'ingresso."""
import re, sys, math
s = open(sys.argv[1], errors='ignore').read()
def meas(n):
    b = s.split('Measurement: ' + n + '\n')[1].split('Measurement')[0]
    return [float(x) for x in re.findall(r'^\s+\d+\s+(\S+)', b, re.M)]
thd = {}
for blk in re.split(r'Fourier components of ', s)[1:]:
    node = blk.split('\n', 1)[0].strip()[2:-1]
    thd[node] = [float(x) for x in re.findall(r'Total Harmonic Distortion:\s+(\S+)%', blk)]
    h = []
    for st in re.split(r'\nstep\s+', '\n' + blk)[1:]:
        d = dict((int(a), float(b)) for a, b in re.findall(r'^\s+(\d+)\s+\S+\s+(\S+)\s+\S+\s+\S+°', st, re.M))
        h.append((100*d[2]/d[1], 100*d[3]/d[1]))
    thd[node + 'h'] = h
xr = meas('xr')
lev = ['-16', ' -6', '  0', '+10']
for fam in 'gt':
    print('GROWL' if fam == 'g' else 'NASTRO', '— THD % (H2/H3) | livello dB, colonne = programma', lev, 'dBu')
    for m in ['05', '10', '25', '50', '75', '99']:
        n = fam + m
        r = meas(n + 'r')
        print(f"  {m}%  " + '   '.join(f"{thd[n][i]:5.2f} ({thd[n+'h'][i][0]:4.1f}/{thd[n+'h'][i][1]:4.1f}) {20*math.log10(r[i]/xr[i]):+5.2f}" for i in range(len(xr))))
for n in ['g99max', 'g99min', 'g99dc', 't99max', 't99min', 't99dc']:
    print(n, ['%.3f' % v for v in meas(n)])
