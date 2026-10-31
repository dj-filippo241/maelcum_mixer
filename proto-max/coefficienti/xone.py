"""Modello dell'EQ XONE per MC-CHANNEL (selettore EQ TIPO, voce B5).

Filippo, 2026-10-31: «serie ridisegnato in modo tale da essere simile al eq
degli xone». Sostituisce nel prototipo l'EQ in serie archiviato (serie.py,
che resta come archivio). Solo prototipo: l'EQ di progetto resta l'isolator
(dec. 105).

Riferimento: EQ musicale del Xone:92 (user guide AP5345 e guida Limited
Edition di Allen & Heath):
- LO 250 Hz, +6 dB ... kill totale (a fondo corsa passa-alto 12 dB/ottava);
- LO-MID 350 Hz e HI-MID 2 kHz, +6 ... -30 dB, Q larga in taglio, stretta
  in boost;
- HI 2,5 kHz, +6 dB ... kill totale (a fondo corsa passa-basso 12 dB/ottava).

Realizzazione (digitale, a 4x come l'isolator):
- LO = g LP2 - HP2 a 250 Hz, Linkwitz-Riley 2 (Q 0,5): con g = 1 e un
  allpass (modulo piatto), con g = 0 resta solo HP2.
- HI = g HP2 - LP2 a 2,5 kHz, stessa coppia.
- medi = campana RBJ: Q_TAGLIO sotto il centro, Q_BOOST sopra; a 0 dB la Q
  non conta, quindi il passaggio e continuo.
- uscita invertita: le due coppie LR2 invertono, insieme, tutto lo spettro.
Q dei medi [PROVVISORIO]: il Xone non le pubblica, si fissano all'ascolto.

Law delle manopole: quella dell'isolator (g = 2 theta, oppure curva Pioneer
col selettore CURVA); i medi in dB, fermati a -30.
"""

import cmath
import math

F_LO, F_LM, F_MH, F_HI = 250.0, 350.0, 2000.0, 2500.0
Q_LR2 = 0.5
Q_TAGLIO, Q_BOOST = 0.6, 2.0      # [PROVVISORIO]
FONDO_MEDI_DB = -30.0
G_MIN_MEDI = 10 ** (FONDO_MEDI_DB / 20)


def g_band(theta, pioneer=False):
    """Law dell'isolator: 0 = kill, 0,5 = 1, 1 = 2 (+6 dB)."""
    x = 2 * theta
    if pioneer:
        return min(x, 1) ** 1.5 + max(x - 1, 0)
    return x


def db_medi(g):
    return 20 * math.log10(max(g, G_MIN_MEDI))


def biquad_lp(f0, q, fs):
    k = math.tan(math.pi * f0 / fs)
    n = 1 / (1 + k / q + k * k)
    return (k * k * n, 2 * k * k * n, k * k * n, 2 * (k * k - 1) * n, (1 - k / q + k * k) * n)


def biquad_hp(f0, q, fs):
    k = math.tan(math.pi * f0 / fs)
    n = 1 / (1 + k / q + k * k)
    return (n, -2 * n, n, 2 * (k * k - 1) * n, (1 - k / q + k * k) * n)


def campana(f0, gdb, fs):
    """Campana RBJ con Q che dipende dal segno del guadagno."""
    q = Q_TAGLIO if gdb < 0 else Q_BOOST
    a = 10 ** (gdb / 40)
    w = 2 * math.pi * f0 / fs
    al = math.sin(w) / (2 * q)
    a0 = 1 + al / a
    return ((1 + al * a) / a0, -2 * math.cos(w) / a0, (1 - al * a) / a0,
            -2 * math.cos(w) / a0, (1 - al / a) / a0)


def xone_digitale(f, fs, manopole, pioneer=False):
    from canale import risposta
    gl, glm, gmh, gh = (g_band(t, pioneer) for t in manopole)
    h = lambda c: risposta(c, f, fs)  # noqa: E731
    lo = gl * h(biquad_lp(F_LO, Q_LR2, fs)) - h(biquad_hp(F_LO, Q_LR2, fs))
    lm = h(campana(F_LM, db_medi(glm), fs))
    mh = h(campana(F_MH, db_medi(gmh), fs))
    hi = gh * h(biquad_hp(F_HI, Q_LR2, fs)) - h(biquad_lp(F_HI, Q_LR2, fs))
    return -lo * lm * mh * hi


def xone_os(f, fs, manopole, pioneer=False):
    """Catena del gen~: halfband su, celle a 4fs, halfband giu."""
    from canale import HALFBAND, coef_halfband, risposta_halfband
    h1 = risposta_halfband(coef_halfband(*HALFBAND[1]), f, 2 * fs)
    h2 = risposta_halfband(coef_halfband(*HALFBAND[2]), f, 4 * fs)
    return h1 * h2 * xone_digitale(f, 4 * fs, manopole, pioneer) * h2 * h1


def db(z):
    m = abs(z)
    return -999.0 if m == 0 else 20 * math.log10(m)


if __name__ == "__main__":
    fs = 4 * 48000
    print("pos %  LO 60 Hz  LM 350 Hz  MH 2 kHz  HI 10 kHz  (una manopola alla volta)")
    for p in (0, 5, 10, 25, 50, 75, 100):
        t = p / 100
        print(f"{p:5d}  {db(xone_digitale(60, fs, (t, .5, .5, .5))):+8.1f}"
              f"  {db(xone_digitale(350, fs, (.5, t, .5, .5))):+9.1f}"
              f"  {db(xone_digitale(2000, fs, (.5, .5, t, .5))):+8.1f}"
              f"  {db(xone_digitale(10000, fs, (.5, .5, .5, t))):+9.1f}")
    print("tutte al centro, 20 Hz-20 kHz:",
          max(abs(db(xone_digitale(f, fs, (.5, .5, .5, .5)))) for f in (20, 100, 250, 1000, 2500, 10000, 20000)), "dB max")
