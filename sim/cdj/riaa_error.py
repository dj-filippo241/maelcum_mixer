#!/usr/bin/env python3
"""Confronto risposta RIAA misurata (log LTspice phono-riaa-ac) vs curva ideale.
Uso: python3 riaa_error.py [log]   (default: phono-riaa-ac.log)
Legge le .meas g20..g20k (dB o lineari), riferisce a 1 kHz e stampa l'errore
in dB contro la RIAA di riproduzione ideale (tau 3180/318/75 us)."""
import math, re, sys

TAU1, TAU2, TAU3 = 3180e-6, 318e-6, 75e-6

def riaa_db(f):
    w = 2 * math.pi * f
    s = 1j * w
    H = (1 + s * TAU2) / ((1 + s * TAU1) * (1 + s * TAU3))
    w1 = 2 * math.pi * 1000.0
    s1 = 1j * w1
    H1 = (1 + s1 * TAU2) / ((1 + s1 * TAU1) * (1 + s1 * TAU3))
    return 20 * math.log10(abs(H / H1))

def parse_db(val):
    """Le .meas ac su mag() escono in dB nel log: '(xx.xdB,0°)' oppure lineare."""
    m = re.match(r'\(?(-?[\d.eE+]+)dB', val.strip())
    if m:
        return float(m.group(1))
    return 20 * math.log10(float(val))

log = sys.argv[1] if len(sys.argv) > 1 else 'phono-riaa-ac.log'
txt = open(log).read()
# blocca per step (Cload 100/200/300p)
steps = re.split(r'(?=Measurement: g20\b)', txt)
freqs = [20, 30, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000]
meas = {}
for blk in txt.split('Measurement: ')[1:]:
    name = blk.split()[0]
    if not re.fullmatch(r'g\d+k?', name):
        continue
    for line in blk.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2 and parts[0].isdigit():
            meas.setdefault(int(parts[0]), {})[name] = parse_db(parts[1])
for step in sorted(meas):
    d = meas[step]
    ref = d.get('g1k')
    if ref is None:
        continue
    print(f'--- step {step} (Cload) ---')
    print(f"{'f [Hz]':>7} {'gain rel 1k [dB]':>17} {'ideale [dB]':>12} {'errore [dB]':>12}")
    worst = 0.0
    for f in freqs:
        key = {20:'g20',30:'g30',50:'g50',100:'g100',200:'g200',500:'g500',
               1000:'g1k',2000:'g2k',5000:'g5k',10000:'g10k',20000:'g20k'}[f]
        if key not in d:
            continue
        rel = d[key] - ref
        err = rel - riaa_db(f)
        worst = max(worst, abs(err))
        print(f'{f:7d} {rel:+17.3f} {riaa_db(f):+12.3f} {err:+12.3f}')
    print(f'errore massimo |20-20k|: {worst:.3f} dB')
