#!/usr/bin/env python3
"""Deriva degli shaper a caldo (todo 49, dec. 111): confronta i log
*-hot (50/65/75 C) con la taratura a 35 C del log originale (colonna 2 di
20/35/50). Reroute e drive in dB (61 mV/dB a scala x10 = 0,061 V/dB),
position in % di frequenza (f ~ 1 + V(0) - V), filtro in % di frequenza
(0,5 V/ottava, taratura come shaper_filtro_tab.py)."""
import re, math
def meas(path):
    s = open(path, errors='ignore').read(); out = {}
    for name, body in re.findall(r'Measurement: (\S+)\n(.*?)(?=\nMeasurement|\Z)', s, re.S):
        out[name] = [float(x) for x in re.findall(r'^\s+\d+\s+(\S+)', body, re.M)]
    return out
def key(n): return int(re.sub(r'\D', '', n) or 0)
for n in ('reroute', 'drive'):
    o, h = meas('shaper-%s.log' % n), meas('shaper-%s-hot.log' % n)
    print('%s: dB a 35 C | deriva dB a 50 / 65 / 75 C' % n)
    for m in sorted(o, key=key):
        r = o[m][1] / 0.061
        print('  %-4s %8.2f | %+5.2f %+5.2f %+5.2f' % ((m, r) + tuple(v / 0.061 - r for v in h[m])))
o, h = meas('shaper-position.log'), meas('shaper-position-hot.log')
off = o['m0'][1]
print('position: deriva di frequenza %% a 50 / 65 / 75 C rispetto a 35 C')
for m in sorted(o, key=key):
    ref = 1 + off - o[m][1]
    print('  %-4s %+5.1f %+5.1f %+5.1f' % ((m,) + tuple(100 * ((1 + off - v) / ref - 1) for v in h[m])))
o, h = meas('shaper-filtro-freq.log'), meas('shaper-filtro-freq-hot.log')
print('filtro FREQ: deriva %% a 50 / 65 / 75 C rispetto a 35 C (2 V = 1 ottava? no: 0,5 V/ottava)')
for m in sorted(o, key=key):
    ref = o[m][1]
    print('  %-6s %+6.1f %+6.1f %+6.1f' % ((m,) + tuple(100 * (2 ** ((ref - v) / 0.5) - 1) for v in h[m])))
