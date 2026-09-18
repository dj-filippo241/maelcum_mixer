#!/usr/bin/env python3
"""
MAELCUM MIXER — Analisi EQ canale DJ a celle di contribuzione bipolare
Fase 1, validazione matematica della topologia (non sostituisce lo SPICE:
qui gli op-amp sono ideali; rumore/THD/componenti reali si validano dopo).

Topologia per banda:
  V_out(f) = V_in(f) * [ 1 + somma_i k_i * H_i(f) ]
  - k_i = posizione del pot della banda i, da -1 (full CCW) a +1 (full CW), 0 al detent
  - H_i = filtro di banda normalizzato a guadagno massimo 1 (shelf o bell)
  - implementazione: pot collegato tra +H_i*V e -H_i*V (wiper al nodo di summing)

Proprieta' strutturali (esatte, non approssimate):
  - detent (k=0 per tutte) => risposta IDENTICAMENTE piatta a ogni frequenza
  - k=+1 al centro banda => 1+1 = 2 = +6.02 dB (boost massimo locked)
  - k=-1 al centro banda => 1-1 = 0 = -inf dB (kill locked)
Frequenze baseline [PROVVISORIO]: 70 / 250 / 1000 / 5000 Hz (decisione: review aperta).
"""
import cmath, math

def low_shelf(f, f0=70.0):
    x = f / f0
    return 1.0 / cmath.sqrt(complex(1 + x**4, 0))

def high_shelf(f, f0=5000.0):
    x = f0 / f
    return 1.0 / cmath.sqrt(complex(1 + x**4, 0))

def bell(f, f0, Q):
    return 1.0 / (1.0 + 1j * (f / f0 - f0 / f) / Q)

BANDS = [
    ("LOW      (shelf 70 Hz)",       lambda f: low_shelf(f, 70.0)),
    ("LOW-MID  (bell 250 Hz Q0.8)",  lambda f: bell(f, 250.0, 0.8)),
    ("MID-HIGH (bell 1 kHz Q0.9)",   lambda f: bell(f, 1000.0, 0.9)),
    ("HIGH     (shelf 5 kHz)",       lambda f: high_shelf(f, 5000.0)),
]

def T(f, ks):
    s = 1.0 + 0j
    for (_, H), k in zip(BANDS, ks):
        s = s + k * H(f)
    return s

def db(z):
    m = abs(z)
    return 20 * math.log10(m) if m > 1e-9 else -180.0

FREQS = [10, 20, 35, 50, 70, 100, 150, 250, 400, 700, 1000, 1400,
         2500, 3500, 5000, 8000, 12000, 20000, 35000]

CASES = [
    ("detent — tutti i knob a 0 (deve essere piatto esatto)", [0, 0, 0, 0]),
    ("LOW kill (k=-1)",                        [-1, 0, 0, 0]),
    ("LOW boost +6 (k=+1)",                    [+1, 0, 0, 0]),
    ("LOW-MID kill",                           [0, -1, 0, 0]),
    ("MID-HIGH boost +6",                      [0, 0, +1, 0]),
    ("HIGH kill",                              [0, 0, 0, -1]),
    ("tutte le bande a +6 (worst boost)",      [+1, +1, +1, +1]),
    ("tutte le bande kill (worst cut)",        [-1, -1, -1, -1]),
    ("dub classico: LOW+HIGH su, medi giu",    [+1, -1, -1, +1]),
    ("half boost LOW (k=+0.5 => +3.5dB nom.)", [+0.5, 0, 0, 0]),
]

out = []
def pr(s=""):
    out.append(s)
    print(s)

pr("MAELCUM MIXER — EQ 4 bande, celle a contribuzione bipolare")
pr("Baseline [PROVVISORIO]: 70/250/1k/5k Hz — analisi del " + "2026-09-18")
pr()
for name, ks in CASES:
    pr(f"=== {name} ===")
    pr("   f[Hz]    dB")
    for f in FREQS:
        v = db(T(f, ks))
        mark = " <-" if abs(v + 180) < 1e-6 else ""
        pr(f"  {f:6d}  {v:7.2f}{mark}")
    pr()

# verifiche strutturali automatiche
pr("=== VERIFICHE STRUTTURALI ===")
flat_err = max(abs(db(T(f, [0,0,0,0]))) for f in FREQS)
pr(f"1. Piattezza al detent: errore max = {flat_err:.2e} dB (atteso 0 esatto)")
low_boost = db(T(20, [+1,0,0,0]))
pr(f"2. Boost LOW a 20 Hz: {low_boost:+.2f} dB (atteso ~+6)")
low_kill = db(T(20, [-1,0,0,0]))
pr(f"3. Kill LOW a 20 Hz: {low_kill:.1f} dB (atteso molto profondo)")
mid_boost = db(T(1000, [0,0,+1,0]))
pr(f"4. Boost MID-HIGH a 1 kHz: {mid_boost:+.2f} dB (atteso +6.02)")
worst = max(db(T(f, [+1,+1,+1,+1])) for f in FREQS)
pr(f"5. Worst boost (4 bande a +6): picco {worst:+.2f} dB (sovrapposizione bande)")
worst_cut = max(db(T(f, [-1,-1,-1,-1])) for f in FREQS)
pr(f"6. Worst cut (4 bande kill): residuo massimo {worst_cut:.1f} dB nelle sovrapposizioni")

with open("sim/eq_results.txt", "w") as fh:
    fh.write("\n".join(out) + "\n")
print("\nRisultati salvati in sim/eq_results.txt")
