"""Conta i componenti di una scheda per blocco, senza generarla.
Uso: python3 pcb/tools/conta.py pcb/master/master-segnale.py
Serve per stimare quante schede servono a un modulo (dec. 142, 144) dal conteggio vero."""
import importlib.util, collections, sys
spec = importlib.util.spec_from_file_location("m", sys.argv[1]); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
c = collections.OrderedDict()
for p in m.d.parts:
    k = c.setdefault(p.block, collections.Counter()); k[p.ref.rstrip("0123456789")] += 1
tot = 0
for b, k in c.items():
    n = sum(k.values()); tot += n
    print(f"{n:4d}  {b}  {dict(k)}")
print(tot)
