"""Controlla le regole gen~ di CLAUDE.md nei .genexpr del prototipo: funzioni con un solo
valore di ritorno e nessun nome esterno uguale a un parametro o locale di funzione.

Uso:  python3 proto-max/coefficienti/regole_gen.py
Falso allarme noto: una virgola dentro min()/max() nel return (es. spl) conta come ritorno doppio.
"""
import os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import re,sys,glob
for f in sorted(glob.glob('MC-*.genexpr')):
    t=open(f).read(); righe=t.splitlines()
    funz={}; cur=None; main=set(); multi=[]
    decl=set()
    for r in righe:
        r=r.split('//')[0].rstrip()
        m=re.match(r'^(\w+)\(([^)]*)\)\s*\{$',r)
        if m and not r.startswith('if'):
            cur=m.group(1); funz[cur]=set(a.strip() for a in m.group(2).split(',') if a.strip()); continue
        if cur:
            if r=='}': cur=None; continue
            a=re.match(r'^\s*([\w, ]+?)\s*=[^=]',r)
            if a: funz[cur]|=set(x.strip() for x in a.group(1).split(','))
            if re.match(r'^\s*return [^;]*,',r): multi.append(cur)
            continue
        m=re.match(r'^(Param|History|Data|Buffer) (\w+)',r)
        if m: decl.add(m.group(2)); continue
        a=re.match(r'^\s*([\w, ]+?)\s*=[^=]',r)
        if a: main|=set(x.strip() for x in a.group(1).split(','))
    loc=set().union(*funz.values()) if funz else set()
    coll=sorted((main|decl)&loc)
    print(f, '| ritorni multipli:',sorted(set(multi)) or 'no','| nomi in collisione:',coll or 'no')
