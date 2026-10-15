"""Modello dell'EQ IN SERIE archiviato (v0.3 beta-3) per MC-CHANNEL.

Voce B5 (docs/02): Filippo, 2026-10-15, tiene i centri 70 / 250 / 1k / 5k
come opzione d'ascolto accanto all'isolator (selettore EQ TIPO). L'EQ di
progetto resta l'isolator (dec. 105): questo modello serve solo al
confronto a orecchio.

Fonte: sim/eq-serie/cascade-b3.cir (componenti) e docs/fase1/eq-serie-v0.3.md
§9 (topologia) e §10 (law delle manopole). Op-amp ideali: il netlist usa i
macromodelli reali, lo scarto atteso e di centesimi di dB.

Catena: buffer -0,5 -> LOW -> LOW-MID -> MID-HIGH -> HIGH -> make-up -2.
Sei inversioni: polarita diritta, guadagno 0,5 x 2 = 1.
- LOW: Baxandall a shelf, G = (R + Zb) / (R + Za), Za = x Rp || C,
  Zb = (1 - x) Rp || C.
- LOW-MID, MID-HIGH: G = 1 + c BP, BP = passa-banda MFB invertente
  (al centro vale circa -1: c = 1 notch, c = -1 boost +6 dB).
- HIGH: G = 1 - c HP2, HP2 = Sallen-Key a guadagno 1.
- c = pot da 10k con cursore caricato dai 49,9k del summer.

Python puro: nessun pacchetto da installare.
"""

import cmath
import math

# --- componenti di cascade-b3.cir ---
R_LOW, RP_LOW, C_LOW = 1e3, 31e3, 100e-9
# MFB: R1 ingresso, R2 a massa, C1 verso il nodo invertente, C2 verso
# l'uscita, R3 retroazione
MFB = {
    "lm": (5.11e3, 18.2e3, 100e-9, 100e-9, 10.2e3),   # 250 Hz, Q 0,8
    "mh": (4.32e3, 6.98e3, 33e-9, 33e-9, 8.66e3),     # 1 kHz, Q 0,9
}
# Sallen-Key passa-alto: C1, C2 in serie, R1 al ritorno dall'uscita,
# R2 a massa
SK_HP = (10e-9, 10e-9, 2.3e3, 4.6e3)                  # ~4,9 kHz, Q 0,707
R_POT, R_SUMMER = 10e3, 49.9e3

# --- law delle manopole (eq-serie §10) ---
# Shelf (LOW, HIGH): posizione elettrica x a tratti lineari.
X_KILL, X_CUT, X_DETENT, X_BOOST = 0.999, 0.970, 0.5, 0.323
THETA_CUT = 0.05


def x_shelf(theta):
    """theta 0..1 -> x della cella LOW: kill negli ultimi 5 % di corsa."""
    if theta <= THETA_CUT:
        return X_KILL + (X_CUT - X_KILL) * theta / THETA_CUT
    if theta <= 0.5:
        return X_CUT + (X_DETENT - X_CUT) * (theta - THETA_CUT) / (0.5 - THETA_CUT)
    return X_DETENT + (X_BOOST - X_DETENT) * (theta - 0.5) / 0.5


def g_shelf(x):
    """Guadagno in continua della cella LOW: profondita dello shelf."""
    return (R_LOW + (1 - x) * RP_LOW) / (R_LOW + x * RP_LOW)


def c_pot(t):
    """Cursore del pot da 10k caricato dal summer: 1 (t = 0) ... -1 (t = 1)."""
    k = R_POT / R_SUMMER
    return (1 - 2 * t) / (1 + k * t * (1 - t))


def c_high(theta):
    """HIGH: stessa law delle shelf. La profondita in cima segue quella
    della LOW (in dB), normalizzata perche gli estremi diano c = 1 e -1
    come il netlist (thh = 0 e 1)."""
    g = g_shelf(x_shelf(theta))
    if theta <= 0.5:
        return (1 - g) / (1 - g_shelf(X_KILL))
    return -(g - 1) / (g_shelf(X_BOOST) - 1)


# --- funzioni di trasferimento in s: (n0, n1, n2), (d0, d1, d2) ---

def low_s(x):
    ra, rb = RP_LOW * x + 1e-3, RP_LOW * (1 - x) + 1e-3
    a0, a1, ta = R_LOW + rb, R_LOW * rb * C_LOW, ra * C_LOW
    b0, b1, tb = R_LOW + ra, R_LOW * ra * C_LOW, rb * C_LOW
    return (a0, a1 + a0 * ta, a1 * ta), (b0, b1 + b0 * tb, b1 * tb)


def bp_s(chiave):
    """MFB invertente: H = -s C1 R3 / R1 / (s^2 C1 C2 R3 + s (C1 + C2) + G1 + G2)."""
    r1, r2, c1, c2, r3 = MFB[chiave]
    return (0.0, -c1 * r3 / r1, 0.0), (1 / r1 + 1 / r2, c1 + c2, c1 * c2 * r3)


def hp_s():
    """SK passa-alto: H = s^2 C1 C2 R2 / (s^2 C1 C2 R2 + s (C1 + C2) + G1)."""
    c1, c2, r1, r2 = SK_HP
    return (0.0, 0.0, c1 * c2 * r2), (1 / r1, c1 + c2, c1 * c2 * r2)


def valuta(nd, s):
    (n0, n1, n2), (d0, d1, d2) = nd
    return (n0 + n1 * s + n2 * s * s) / (d0 + d1 * s + d2 * s * s)


def bilineare(nd, fs):
    """Biquad digitale (b0, b1, b2, a1, a2) con s = 2 fs (1 - z^-1)/(1 + z^-1).
    Senza prewarp: a 4x (176-384 kHz) lo scarto a 20 kHz e trascurabile."""
    (n0, n1, n2), (d0, d1, d2) = nd
    k = 2 * fs
    kk = k * k
    a0 = d0 + d1 * k + d2 * kk
    return ((n0 + n1 * k + n2 * kk) / a0, (2 * n0 - 2 * n2 * kk) / a0,
            (n0 - n1 * k + n2 * kk) / a0, (2 * d0 - 2 * d2 * kk) / a0,
            (d0 - d1 * k + d2 * kk) / a0)


def _celle(h, manopole_el):
    """manopole_el = (x LOW, c LOW-MID, c MID-HIGH, c HIGH)."""
    x, c_lm, c_mh, c_hi = manopole_el
    return (h(low_s(x)) * (1 + c_lm * h(bp_s("lm")))
            * (1 + c_mh * h(bp_s("mh"))) * (1 - c_hi * h(hp_s())))


def elettriche(manopole):
    """Posizioni delle manopole (0..1) -> valori elettrici delle celle."""
    t_low, t_lm, t_mh, t_hi = manopole
    return x_shelf(t_low), c_pot(t_lm), c_pot(t_mh), c_high(t_hi)


def serie_analogico(f, manopole_el):
    s = 2j * math.pi * f
    return _celle(lambda nd: valuta(nd, s), manopole_el)


def serie_digitale(f, fs, manopole_el):
    from canale import risposta
    return _celle(lambda nd: risposta(bilineare(nd, fs), f, fs), manopole_el)


def serie_os(f, fs, manopole):
    """Catena del gen~: halfband su, celle a 4fs, halfband giu."""
    from canale import HALFBAND, coef_halfband, risposta_halfband
    h1 = risposta_halfband(coef_halfband(*HALFBAND[1]), f, 2 * fs)
    h2 = risposta_halfband(coef_halfband(*HALFBAND[2]), f, 4 * fs)
    return h1 * h2 * serie_digitale(f, 4 * fs, elettriche(manopole)) * h2 * h1


def db(z):
    m = abs(z)
    return -999.0 if m == 0 else 20 * math.log10(m)


if __name__ == "__main__":
    # tabella della law: dB della cella da sola nel punto piu toccato
    print("pos %   LOW 20 Hz   LM 250 Hz   MH 1 kHz   HIGH 20 kHz")
    for p in (0, 5, 10, 20, 30, 40, 50, 75, 100):
        t = p / 100
        x, cl, cm, ch = elettriche((t, t, t, t))
        print(f"{p:5d}  {db(serie_analogico(20, (x, 0, 0, 0))):+9.1f}"
              f"  {db(serie_analogico(250, (0.5, cl, 0, 0))):+10.1f}"
              f"  {db(serie_analogico(1000, (0.5, 0, cm, 0))):+9.1f}"
              f"  {db(serie_analogico(20000, (0.5, 0, 0, ch))):+11.1f}")
