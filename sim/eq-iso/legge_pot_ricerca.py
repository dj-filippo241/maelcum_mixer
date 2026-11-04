"""Legge PIONEER con un pot lineare: ricerca a caso delle reti realizzabili (todo 211).

Rete: 1 pista lineare (residuo 20 ohm) + 1 op-amp ideale + 3-6 resistenze
fra due nodi qualsiasi (ingresso, massa, capi e cursore del pot, piedini e
uscita dell'op-amp). Vincoli: silenzio a fondo corsa, centro = 0 dB, fine
corsa = +6 dB, anello stabile. Punteggio: scarto massimo in dB dalla curva
PIONEER (canale.py, banda_pioneer) fra theta 0,05 e 1 (sotto 0,1 pesato 0,3).
Esito 2026-11-04 (semi 2-9, 20000 topologie ciascuno): il migliore fa 7,0 dB,
cioe' lo scarto del pot lineare nudo. Nessuna rete batte il lineare.

Uso: python3 sim/eq-iso/legge_pot_ricerca.py <seme> <numero topologie>
"""
import math, random, sys
random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
def pio(t):
    x = 2*t; return min(x, 1)**1.5 + max(x-1, 0)
TH = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6, 0.75, 0.9, 1.0]
NODES = ["VIN", "GND", "T", "B", "W", "P", "N", "O"]
UNK = ["T", "B", "W", "P", "N", "O"]
PAIRS = [(a, b) for i, a in enumerate(NODES) for b in NODES[i+1:]
         if not (a in ("VIN", "GND") and b in ("VIN", "GND"))]
REND = 0.002  # residuo del pot (20 ohm su 10k)

def solve(M, v):
    n = len(v); M = [row[:] + [v[i]] for i, row in enumerate(M)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        if abs(M[p][c]) < 1e-14: return None
        M[c], M[p] = M[p], M[c]
        for r in range(n):
            if r != c:
                f = M[r][c] / M[c][c]
                if f:
                    for k in range(c, n+1): M[r][k] -= f*M[c][k]
    return [M[i][n]/M[i][i] for i in range(n)]

def net(res, th, vin=1.0, drive_o=None):
    g = dict(res)
    g[("T", "W")] = g.get(("T", "W"), 0) + 1/(1-th+REND)
    g[("B", "W")] = g.get(("B", "W"), 0) + 1/(th+REND)
    unk = UNK if drive_o is None else UNK[:-1]
    idx = {n: i for i, n in enumerate(unk)}
    known = {"VIN": vin, "GND": 0.0}
    if drive_o is not None: known["O"] = drive_o
    n = len(unk); M = [[0.0]*n for _ in range(n)]; v = [0.0]*n
    for (a, b), G in g.items():
        for x, y in ((a, b), (b, a)):
            if x in idx and x != "O":
                M[idx[x]][idx[x]] += G
                if y in idx: M[idx[x]][idx[y]] -= G
                else: v[idx[x]] += G*known[y]
    if drive_o is None:
        r = idx["O"]; M[r] = [0.0]*n; M[r][idx["P"]] = 1; M[r][idx["N"]] = -1; v[r] = 0
    s = solve(M, v)
    if s is None: return None
    return dict(zip(unk, s))

def gain(res, th):
    s = net(res, th)
    return None if s is None else s["O"]

def stable(res):
    for th in (0.0, 0.25, 0.5, 0.75, 1.0):
        s = net(res, th, vin=0.0, drive_o=1.0)
        if s is None or s["N"] - s["P"] <= 1e-3: return False
    return True

def cost(res):
    g0 = gain(res, 0.0); g5 = gain(res, 0.5); g1 = gain(res, 1.0)
    if g0 is None or g5 is None or g1 is None or abs(g5) < 1e-9: return 1e9, None
    pen = 100*abs(g0/g5) + 50*abs(g1/g5 - 2)
    err = 0
    for t in TH:
        g = gain(res, t)
        if g is None or g/g5 <= 0: return 1e9, None
        e = abs(20*math.log10(g/g5) - 20*math.log10(pio(t)))
        if t < 0.1: e *= 0.3
        err = max(err, e)
    return err + pen, err

def rnd_topo():
    k = random.randint(3, 6)
    res = {}
    for p in random.sample(PAIRS, k):
        res[p] = 10**random.uniform(-2, 2)
    return res

best = (1e9, None, None)
for it in range(int(sys.argv[2]) if len(sys.argv) > 2 else 3000):
    res = rnd_topo()
    if not any("P" in p for p in res) or not any("N" in p for p in res): continue
    if not any("O" in p for p in res): continue
    try:
        c, e = cost(res)
    except ZeroDivisionError:
        continue
    if c > 1e8: continue  # ogni rete valida passa alla discesa locale
    # discesa locale sui log dei valori
    step = 0.5
    while step > 0.01:
        moved = False
        for p in list(res):
            for f in (10**step, 10**-step):
                trial = dict(res); trial[p] *= f
                try: c2, e2 = cost(trial)
                except ZeroDivisionError: continue
                if c2 < c: res, c, e, moved = trial, c2, e2, True
        if not moved: step /= 2
    if c < best[0] and stable(res):
        best = (c, e, res)
        print(round(c, 3), round(e, 3), {k: round(1/v, 4) for k, v in res.items()}, flush=True)
