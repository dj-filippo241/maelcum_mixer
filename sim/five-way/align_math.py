#!/usr/bin/env python3
"""5-WAY v0.2 — verifica numerica della banca allineata in fase (stdlib pura).

Dimostra: la cascata LR4 a 5 vie CON compensazione allpass (ogni banda
passa gli allpass A2 dei crossover SOPRA la sua banda: SUB 3, KICK 2,
MID 1, HIGH/SUPER 0) somma a |Sigma| = 1 esatto = prodotto dei 4 allpass.
Confronta con:
  - v0.1 troncata stessa polarita' (buchi -3...-5 dB, finding §8.1)
  - v0.1 troncata polarita' alterna (come bank-lr4.cir)
  - varianti "lite" (meno sezioni allpass, errore residuo quantificato)
Frequenze PROVVISORIE (dec. 66 / questione 67): 90 / 350 / 1200 / 3500 Hz.
Uso: python3 align_math.py  (nessuna dipendenza esterna)
"""
import cmath
import math

F1, F2, F3, F4 = 90.0, 350.0, 1200.0, 3500.0
N = 8000
FMIN, FMAX = 5.0, 60e3

freqs = [FMIN * (FMAX / FMIN) ** (i / (N - 1)) for i in range(N)]
S = [2j * math.pi * f for f in freqs]        # s = j*omega
W = [2 * math.pi * f for f in freqs]         # omega reale


def den(s, f0):
    w0 = 2 * math.pi * f0
    return s * s + math.sqrt(2) * w0 * s + w0 * w0


def LP2(s, f0):
    w0 = 2 * math.pi * f0
    return w0 * w0 / den(s, f0)


def HP2(s, f0):
    return s * s / den(s, f0)


def LP4(s, f0):
    return LP2(s, f0) ** 2


def HP4(s, f0):
    return HP2(s, f0) ** 2


def A2(s, f0):
    """Allpass 2° ordine = LP4(f0) + HP4(f0) (proprieta' LR4)."""
    w0 = 2 * math.pi * f0
    return (s * s - math.sqrt(2) * w0 * s + w0 * w0) / den(s, f0)


def db(x):
    return 20 * math.log10(abs(x) + 1e-30)


# --- Bande nested (spina HP condivisa: ogni banda passa TUTTE le HP sotto) ---
SUB = [LP4(s, F1) for s in S]
KICK = [HP4(s, F1) * LP4(s, F2) for s in S]
MID = [HP4(s, F1) * HP4(s, F2) * LP4(s, F3) for s in S]
HIGH = [HP4(s, F1) * HP4(s, F2) * HP4(s, F3) * LP4(s, F4) for s in S]
SUP = [HP4(s, F1) * HP4(s, F2) * HP4(s, F3) * HP4(s, F4) for s in S]

a2 = [A2(s, F2) for s in S]
a3 = [A2(s, F3) for s in S]
a4 = [A2(s, F4) for s in S]
a1 = [A2(s, F1) for s in S]


def zsum(*lists):
    return [sum(vals) for vals in zip(*lists)]


def zmul(*lists):
    out = [complex(1, 0)] * len(freqs)
    for lst in lists:
        out = [a * b for a, b in zip(out, lst)]
    return out


# --- Schema ESATTO v0.2: compensazione completa 3/2/1/0/0 ---
exact = zsum(zmul(SUB, a2, a3, a4), zmul(KICK, a3, a4), zmul(MID, a4), HIGH, SUP)
ref = zmul(a1, a2, a3, a4)                  # somma attesa = prodotto allpass

# --- v0.1 troncata (bande senza HP dei crossover lontani) ---
t_mid = [HP4(s, F2) * LP4(s, F3) for s in S]
t_high = [HP4(s, F3) * LP4(s, F4) for s in S]
t_sup = [HP4(s, F4) for s in S]
trunc = zsum(SUB, KICK, t_mid, t_high, t_sup)
neg_kick = [-x for x in KICK]
neg_high = [-x for x in t_high]
alt = zsum(SUB, neg_kick, t_mid, neg_high, t_sup)

# --- Varianti lite ---
liteA = zsum(zmul(SUB, a2), zmul(KICK, a3), zmul(MID, a4), HIGH, SUP)
liteB = zsum(zmul(SUB, a2, a3), zmul(KICK, a3), zmul(MID, a4), HIGH, SUP)
liteC = zsum(zmul(SUB, a2, a3), zmul(KICK, a3, a4), zmul(MID, a4), HIGH, SUP)


def report(name, sig, ref_sig=None):
    if ref_sig is None:
        d = [db(x) for x in sig]
    else:
        d = [db(x / r) for x, r in zip(sig, ref_sig)]
    i_max = max(range(N), key=lambda i: d[i])
    i_min = min(range(N), key=lambda i: d[i])
    print(f"{name:36s} max {d[i_max]:+7.3f} dB @{freqs[i_max]:8.1f} Hz | "
          f"min {d[i_min]:+7.3f} dB @{freqs[i_min]:8.1f} Hz")


print("Somma normalizzata al riferimento (|ref| = 1 per costruzione):")
report("ESATTO v0.2 (allpass 3/2/1/0/0)", exact, ref)
report("v0.1 troncata stessa polarita'", trunc)
report("v0.1 troncata polarita' alterna", alt)
report("Lite A: 1 allpass/banda (3 sez/lato)", liteA)
report("Lite B: SUB2 KICK1 MID1 (4 sez/lato)", liteB)
report("Lite C: esatto meno A2(F4) su SUB (5)", liteC)

print()
print("Variante lite vs ESATTO (deviazione dalla piattezza perfetta):")
for name, sig in [("Lite A", liteA), ("Lite B", liteB), ("Lite C", liteC)]:
    ratio = [x / e for x, e in zip(sig, exact)]
    d = [db(x) for x in ratio]
    i_max = max(range(N), key=lambda i: d[i])
    i_min = min(range(N), key=lambda i: d[i])
    print(f"{name:8s} max {d[i_max]:+7.3f} dB @{freqs[i_max]:8.1f} Hz | "
          f"min {d[i_min]:+7.3f} dB @{freqs[i_min]:8.1f} Hz")

# --- Verifica identita' algebrica ---
err = max(abs(x - r) for x, r in zip(exact, ref))
print(f"\nIdentita' Sigma_esatto == A2(F1)A2(F2)A2(F3)A2(F4): err max {err:.2e}")

# --- Group delay della somma esatta (prodotto di 4 allpass) ---
phi = []
prev = None
for r in ref:
    a = cmath.phase(r)
    if prev is not None:
        while a - prev > math.pi:
            a -= 2 * math.pi
        while a - prev < -math.pi:
            a += 2 * math.pi
    phi.append(a)
    prev = a

tau = [0.0] * N
for i in range(N):
    lo = max(i - 1, 0)
    hi = min(i + 1, N - 1)
    tau[i] = -(phi[hi] - phi[lo]) / (W[hi] - W[lo])

i_pk = max(range(N), key=lambda i: tau[i])
print(f"Group delay somma esatta: picco {tau[i_pk]*1e3:.2f} ms @{freqs[i_pk]:.0f} Hz")
for probe in (10, 30, 90, 350, 1200, 3500, 10000, 20000):
    i = min(range(N), key=lambda k: abs(freqs[k] - probe))
    fase = math.degrees(phi[i]) % 360
    if fase > 180:
        fase -= 360
    print(f"  tau({probe:6.0f} Hz) = {tau[i]*1e3:7.3f} ms   fase {fase:+7.1f} deg")

# --- Kill: somma residua con banda killata (gate, nessuna cancellazione) ---
print()
bands = [("SUB", zmul(SUB, a2, a3, a4)), ("KICK", zmul(KICK, a3, a4)),
         ("MID", zmul(MID, a4)), ("HIGH", HIGH), ("SUPER", SUP)]
for name, killed in bands:
    resid = [e - k for e, k in zip(exact, killed)]
    d = [db(x) for x in resid]
    i_max = max(range(N), key=lambda i: d[i])
    i_min = min(range(N), key=lambda i: d[i])
    print(f"Kill {name:5s}: residua max {d[i_max]:+6.2f} dB @{freqs[i_max]:7.0f} Hz, "
          f"min {d[i_min]:+6.2f} dB @{freqs[i_min]:7.0f} Hz")


# --- Group delay per variante (costo temporale della compensazione) ---
def group_delay(sig):
    phi = []
    prev = None
    for r in sig:
        a = cmath.phase(r)
        if prev is not None:
            while a - prev > math.pi:
                a -= 2 * math.pi
            while a - prev < -math.pi:
                a += 2 * math.pi
        phi.append(a)
        prev = a
    tau = [0.0] * N
    for i in range(N):
        lo = max(i - 1, 0)
        hi = min(i + 1, N - 1)
        tau[i] = -(phi[hi] - phi[lo]) / (W[hi] - W[lo])
    return tau


print()
print("Group delay per variante (ms):")
print(f"{'variante':10s} {'10 Hz':>8s} {'50 Hz':>8s} {'90 Hz':>8s} {'350 Hz':>8s} "
      f"{'1,2k':>8s} {'3,5k':>8s} {'10k':>8s}  picco")
for name, sig in [("ESATTO", exact), ("Lite A", liteA), ("Lite C", liteC),
                  ("v0.1 trunc", trunc)]:
    t = group_delay(sig)
    row = []
    for probe in (10, 50, 90, 350, 1200, 3500, 10000):
        i = min(range(N), key=lambda k: abs(freqs[k] - probe))
        row.append(f"{t[i]*1e3:8.2f}")
    i_pk = max(range(N), key=lambda i: t[i])
    print(f"{name:10s} {' '.join(row)}  {t[i_pk]*1e3:5.2f} @{freqs[i_pk]:.0f} Hz")


# --- Sezione allpass reale: MFB bandpass + summer invertente (2 op-amp) ---
# MFB BP: R1 in->n1, R2 n1->gnd, C1 n1->n-, Rf n->Vout, C2 n1->Vout.
# Vincolo Q=0,707 con C1 = 2C, C2 = C:
#   R1 = 1/(sqrt2*w0*C)   R2 = 2*R1   Rf = 1,5*R1
# Summer: Vout = -(1*Vin + 2*Vbp) -> sezione = -A2(s) (polarita' comune,
# ripristinata dal make-up: dec. 73).
print()
print("Sezione allpass reale (MFB BP + summer 1x/2x), C base per f0:")
print(f"{'f0':>6s} {'C':>8s} {'C1=2C':>8s} {'R1':>9s} {'R2=2R1':>9s} "
      f"{'Rf=1,5R1':>9s}  (E96 vicini)")


def e96(r):
    """Resistenza E96 piu' vicina."""
    from math import log10, floor
    dec = floor(log10(r))
    m = r / 10**dec
    table = [1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27,
             1.30, 1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, 1.58, 1.62, 1.65,
             1.69, 1.74, 1.78, 1.82, 1.87, 1.91, 1.96, 2.00, 2.05, 2.10, 2.15,
             2.21, 2.26, 2.32, 2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80,
             2.87, 2.94, 3.01, 3.09, 3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65,
             3.74, 3.83, 3.92, 4.02, 4.12, 4.22, 4.32, 4.42, 4.53, 4.64, 4.75,
             4.87, 4.99, 5.11, 5.23, 5.36, 5.49, 5.62, 5.76, 5.90, 6.04, 6.19,
             6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 7.32, 7.50, 7.68, 7.87, 8.06,
             8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53, 9.76]
    best = min(table, key=lambda t: abs(log10(t) - log10(m)))
    return best * 10**dec


for f0, C in ((350.0, 22e-9), (1200.0, 10e-9), (3500.0, 2.2e-9)):
    w0 = 2 * math.pi * f0
    R1 = 1 / (math.sqrt(2) * w0 * C)
    R2 = 2 * R1
    Rf = 1.5 * R1
    print(f"{f0:6.0f} {C*1e9:6.0f}nF {2*C*1e9:6.0f}nF {R1:8.0f}R {R2:8.0f}R "
          f"{Rf:8.0f}R  ({e96(R1):.0f}/{e96(R2):.0f}/{e96(Rf):.0f})")

# verifica numerica della sezione (f0=1200, C=10n): |H| = 1 e fase = -2*atan
f0, C = 1200.0, 10e-9
w0 = 2 * math.pi * f0
R1 = 1 / (math.sqrt(2) * w0 * C)
R2, Rf = 2 * R1, 1.5 * R1
Ra, Rb, Rfs = 10e3, 5e3, 10e3            # summer: 1x Vin, 2x Vbp
print()
print("Verifica sezione (f0=1200 Hz): |H| e fase contro A2 ideale")
worst_mag = 0.0
for probe in (100, 350, 600, 1200, 2400, 3500, 10000, 20000):
    s = 2j * math.pi * probe
    G = 1 / R1 + 1 / R2
    Dp = s * s + s * (2 * C) / (2 * C * C * Rf) / 1.0 + G / (2 * C * C * Rf)
    # forma corretta: D' = s^2 + s*(C1+C2)/(C1*C2*Rf) + G/(C1*C2*Rf), C1=2C, C2=C
    Dp = s * s + s * (3 * C) / (2 * C * C * Rf) + G / (2 * C * C * Rf)
    Hbp = -(s / (R1 * C)) / Dp           # Vout/Vin del MFB BP (C2 = C)
    Hsec = -(Rfs / Ra + Rfs / Rb * Hbp)  # summer invertente
    ideal = -A2(s, f0)
    worst_mag = max(worst_mag, abs(abs(Hsec) - 1))
    print(f"  {probe:6.0f} Hz: |H| {abs(Hsec):.6f}  fase {math.degrees(cmath.phase(Hsec/ideal)):+8.4f} deg vs -A2 ideale")
print(f"  deviazione |H| da 1: max {worst_mag:.2e}")
