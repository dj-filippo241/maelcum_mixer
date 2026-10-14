"""Modello di riferimento del canale MC-CHANNEL (prototipo Max P0).

Fonte unica dei numeri del P0. Le stesse formule stanno nel codice gen~
(genera.py le scrive in MC-CHANNEL.genexpr): se cambia un numero, cambia qui.

Origine dei numeri:
- GAIN: cdj-line-channel.md §3.2 e sim/cdj/vca-law.cir (shaper a tratti):
  meta CCW lineare in dB da -100 a 0, meta CW da 0 a +10, -100 = muto.
- Isolator: eq-isolator-v0.4.md §3 e §9 (sim/eq-iso/iso-c-ac.cir):
  banca Linkwitz-Riley 24 dB/ott, allpass del 2o ordine, pot lineare
  con contatto di fondo corsa, somma x2.
- Fader: law [PROVVISORIA, non decisa] = curva quadratica (meta corsa
  -12 dB), la law di un pot audio tipico. La SPECIFICA dice solo -inf..0.

Python puro: nessun pacchetto da installare.
"""

import cmath
import math

# Incroci dell'isolator (B7, da sentire). A = partenza, B = alternativa
# (scartate entrambe all'ascolto, dec. 114), C = proposta dopo l'ascolto.
INCROCI = {
    "A": (150.0, 500.0, 2500.0),
    "B": (100.0, 630.0, 4000.0),
    "C": (150.0, 350.0, 3150.0),
    "D": (150.0, 700.0, 3150.0),
}
# Pendenza di ogni incrocio: 4 = LR4 (24 dB/ott), 2 = LR2 (12 dB/ott).
# C: primo incrocio dolce, LOW e LOW-MID si accavallano di piu (dec. 114).
# D: come C, ma HI-MID parte da 700 Hz come nei mixer DJ (docs/09: confine
# implicito 620-760 Hz) e non contiene il colpo del kick.
# LR2 solo sul primo incrocio: LP2 - HP2 (Q 0,5) = allpass del 1o ordine,
# quindi i rami alti girano di polarita e la somma resta piatta senza
# allpass in piu sugli altri rami.
PENDENZE = {
    "A": (4, 4, 4),
    "B": (4, 4, 4),
    "C": (2, 4, 4),
    "D": (2, 4, 4),
}
Q_LR2 = 0.5
Q_BW = 1.0 / math.sqrt(2.0)   # Butterworth: due in cascata = LR4
BOOST_MAX = 2.0               # somma x2: pot a fine corsa = +6 dB


# --- law dei comandi (theta = posizione della manopola, 0...1) ---

def gain_lin(theta):
    """GAIN: -inf (fondo corsa) ... 0 dB (centro) ... +10 dB (fine corsa)."""
    if theta <= 0.0:
        return 0.0
    if theta < 0.5:
        db = -100.0 * (1.0 - 2.0 * theta)
    else:
        db = 20.0 * (theta - 0.5)
    return 10.0 ** (db / 20.0)


def banda_lin(theta):
    """Manopola di banda: pot lineare x2. 0 = silenzio, 0,5 = 0 dB, 1 = +6 dB."""
    return BOOST_MAX * theta


def fader_lin(theta):
    """Fader [PROVVISORIO]: theta^2, cioe -12 dB a meta corsa."""
    return theta * theta


# --- biquad: trasformata bilineare con prewarp sulla frequenza propria ---

def biquad(tipo, f0, fs, q=Q_BW):
    """Coefficienti (b0, b1, b2, a1, a2), a0 = 1. Stesse formule del gen~."""
    k = math.tan(math.pi * f0 / fs)
    norm = 1.0 / (1.0 + k / q + k * k)
    a1 = 2.0 * (k * k - 1.0) * norm
    a2 = (1.0 - k / q + k * k) * norm
    if tipo == "lp":
        b0 = k * k * norm
        return (b0, 2.0 * b0, b0, a1, a2)
    if tipo == "hp":
        return (norm, -2.0 * norm, norm, a1, a2)
    if tipo == "ap":
        return (a2, a1, 1.0, a1, a2)
    raise ValueError(tipo)


def risposta(coef, f, fs):
    b0, b1, b2, a1, a2 = coef
    z1 = cmath.exp(-2j * math.pi * f / fs)
    return (b0 + b1 * z1 + b2 * z1 * z1) / (1.0 + a1 * z1 + a2 * z1 * z1)


def bande(f, fs, incroci, pendenze=(4, 4, 4)):
    """Le quattro strade dell'isolator, come in eq-isolator §3."""
    f1, f2, f3 = incroci
    assert pendenze[1:] == (4, 4), "LR2 solo sul primo incrocio"
    h = lambda t, f0, q=Q_BW: risposta(biquad(t, f0, fs, q), f, fs)
    if pendenze[0] == 2:
        lp1, hp1 = h("lp", f1, Q_LR2), -h("hp", f1, Q_LR2)
    else:
        lp1, hp1 = h("lp", f1) ** 2, h("hp", f1) ** 2
    lp2, hp2 = h("lp", f2) ** 2, h("hp", f2) ** 2
    lp3, hp3 = h("lp", f3) ** 2, h("hp", f3) ** 2
    ap2, ap3 = h("ap", f2), h("ap", f3)
    low = lp1 * ap2 * ap3
    lowmid = hp1 * lp2 * ap3
    midhigh = hp1 * hp2 * lp3
    high = hp1 * hp2 * hp3
    return low, lowmid, midhigh, high


def isolator(f, fs, incroci, manopole, pendenze=(4, 4, 4)):
    return sum(banda_lin(t) * b
               for t, b in zip(manopole, bande(f, fs, incroci, pendenze)))


def db(x):
    m = abs(x)
    return -999.0 if m == 0.0 else 20.0 * math.log10(m)


# --- oversampling 4x: due stadi 2x con halfband polifase (schema hiir) ---
# Serve perche la bilineare stringe le pendenze vicino a fs/2: a 48 kHz,
# HIGH chiusa con incroci B, 8 kHz usciva a -27 dB contro -24 di LTspice.
# A 4x la banca lavora a 176-384 kHz e lo scarto cade sotto 0,5 dB.

OVERSAMPLING = 4
# (numero di coefficienti, banda di transizione normalizzata al rate alto)
HALFBAND = {
    1: (12, 0.04),   # fs -> 2fs: passa 20 kHz anche a 44,1 kHz
    2: (4, 0.25),    # 2fs -> 4fs: transizione larga, bastano 4
}


def _parametri_transizione(tw):
    k = math.tan((1.0 - tw * 2.0) * math.pi / 4.0)
    k *= k
    kksqrt = (1.0 - k * k) ** 0.25
    e = 0.5 * (1.0 - kksqrt) / (1.0 + kksqrt)
    e4 = e ** 4
    q = e * (1.0 + e4 * (2.0 + e4 * (15.0 + 150.0 * e4)))
    return k, q


def _somma(q, order, c, num):
    acc, i, j = 0.0, (0 if num else 1), (1 if num else -1)
    while True:
        if num:
            t = q ** (i * (i + 1)) * math.sin((i * 2 + 1) * c * math.pi / order) * j
        else:
            t = q ** (i * i) * math.cos(i * 2 * c * math.pi / order) * j
        acc += t
        j, i = -j, i + 1
        if abs(t) <= 1e-100:
            return acc


def coef_halfband(n, tw):
    """Coefficienti degli allpass del halfband polifase (de Soras, hiir)."""
    k, q = _parametri_transizione(tw)
    order = n * 2 + 1
    out = []
    for idx in range(n):
        c = idx + 1
        num = _somma(q, order, c, True) * q ** 0.25
        den = _somma(q, order, c, False) + 0.5
        ww2 = (num / den) ** 2
        x = math.sqrt((1.0 - ww2 * k) * (1.0 - ww2 / k)) / (1.0 + ww2)
        out.append((1.0 - x) / (1.0 + x))
    return out


def risposta_halfband(coefs, f, fs_alto):
    """H(z) = (A0(z^2) + z^-1 A1(z^2)) / 2; A0 = coef pari, A1 = dispari."""
    z1 = cmath.exp(-2j * math.pi * f / fs_alto)
    z2 = z1 * z1
    a = [1.0, 1.0]
    for i, c in enumerate(coefs):
        a[i % 2] *= (c + z2) / (1.0 + c * z2)
    return 0.5 * (a[0] + z1 * a[1])


def isolator_os(f, fs, incroci, manopole, pendenze=(4, 4, 4)):
    """Catena del gen~: su 2x, su 4x, banca a 4fs, giu 4x, giu 2x."""
    h1 = risposta_halfband(coef_halfband(*HALFBAND[1]), f, 2 * fs)
    h2 = risposta_halfband(coef_halfband(*HALFBAND[2]), f, 4 * fs)
    return (h1 * h2 * isolator(f, 4 * fs, incroci, manopole, pendenze)
            * h2 * h1)
