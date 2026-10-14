#!/usr/bin/env python3
"""Riassume i blocchi .four di un log LTspice: per nodo e step stampa
fondamentale, H2, H3 (in % della fondamentale), THD Partial e THD Total.

Regola (RISULTATI-cue §6, 2026-10-12): si leggono SEMPRE entrambe.
Partial = armoniche elencate; Total = tutto il residuo. Se Total supera
Partial di oltre il 50 % lo script stampa «CONTROLLA»: non è distorsione
armonica (oscillazione, toni estranei, leakage della finestra) finché la
forma d'onda non dice il contrario."""
import re, sys
s = open(sys.argv[1], errors='ignore').read()
for blk in re.split(r'Fourier components of ', s)[1:]:
    node = blk.split('\n', 1)[0].strip()
    print(node)
    for st in re.split(r'\nstep\s+', '\n' + blk)[1:] or [blk]:
        n = st.split('\n', 1)[0].strip()
        h = dict((int(a), float(b)) for a, b in re.findall(r'^\s+(\d+)\s+\S+\s+(\S+)\s+\S+\s+\S+°', st, re.M))
        thd = re.search(r'Total Harmonic Distortion:\s+(\S+)%', st)
        par = re.search(r'Partial Harmonic Distortion:\s+(\S+)%', st)
        if 1 in h and thd:
            tot = float(thd.group(1))
            p = float(par.group(1)) if par else float('nan')
            flag = "  CONTROLLA: Total >> Partial" if par and tot > 1.5 * p else ""
            print(f"  step {n:>3}  fond {h[1]:8.4f} V  H2 {100*h.get(2,0)/h[1]:6.2f}%  H3 {100*h.get(3,0)/h[1]:6.2f}%  THD Partial {p:8.4f}%  Total {tot:8.4f}%{flag}")
