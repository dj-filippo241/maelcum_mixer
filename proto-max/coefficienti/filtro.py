"""Modello di riferimento del filtro MC-FILTRO (prototipo Max P1).

Fonte unica dei numeri del P1. Le stesse formule stanno nel codice gen~
(genera_filtro.py le scrive in MC-FILTRO.genexpr): se cambia un numero,
cambia qui.

Origine dei numeri:
- FREQ: dec. 102 (a), curva Xone:96 sul 90 % centrale, 10 Hz / 35 kHz agli
  estremi (filter-module §1).
- RES: dec. 102 (b), gres = 1 - theta/0,9 fino al 90 %; oltre, gres
  negativo fino a -0,75 a fine corsa (RISULTATI-D5 §2: "gres -0,1 poco
  oltre il 90 %", "-0,75 a RES 100 %").
- Core (a'): OTA LM13700 dietro un partitore 1/30 (dec. 109). Ogni
  integratore e l'OTA della RES vedono Vs * tanh(u / Vs), con
  Vs = 2 VT / k = 1,55 V: il tetto di stato di filter-module §5quater.
  Limitatore: perdita non lineare dal buffer BP al summer (4,7k + 2+2
  1N4148), qui una conduttanza che parte sopra VK; G e VK tarati sul D5.
- Core (c-B): stesso SVF con integratori lineari (VCA puliti), stesso
  limitatore. Il D5 non lo ha misurato: il suo fischio e una stima.
- 4 poli: sezione 1 fissa Q 0,541, sezione 2 con la RES (base Q 1,307):
  Butterworth a RES zero. Allineamento [PROVVISORIO]: B2 si sceglie
  nella sessione 2 del P1.

Livelli: 1,0 nel digitale = 4,36 V di picco, cioe 0 dBu = sinusoide a
-12 dBFS di picco [PROVVISORIO, da sentire].

Discretizzazione: SVF TPT (trapezoidale, Zavalishin) con le non linearita
a secante: ogni elemento non lineare diventa un guadagno a(u) = f(u)/u
calcolato sul campione precedente. Gira a 4x (stesso oversampling di P0).

Python puro: nessun pacchetto da installare.
"""

import math

VT = 0.025852
K_PART = 1.0 / 30.0
VS = 2.0 * VT / K_PART          # 1,551 V
LIV = 1.0954 * 10 ** (12 / 20)  # volt per 1,0 digitale (0 dBu = -12 dBFS)

Q1 = 0.5412                     # Butterworth 4 poli, sezione fissa
Q2 = 1.3066                     # sezione con la RES

# limitatore (tarato sul D5, vedi taratura())
G_LIM = 1.7
VK_LIM = 0.82
W_LIM = 0.06                    # ginocchio morbido dei diodi, volt


def freq_law(theta):
    """FREQ: 10 Hz (0 %) - 20 Hz (5 %) - 20 kHz (95 %) - 35 kHz (100 %)."""
    if theta < 0.05:
        return 10.0 * 2.0 ** (theta / 0.05)
    if theta > 0.95:
        return 20000.0 * 1.75 ** ((theta - 0.95) / 0.05)
    return 20.0 * 1000.0 ** ((theta - 0.05) / 0.9)


def res_law(theta):
    """RES: gres 1 (Q base) ... 0 al 90 % ... -0,75 a fine corsa."""
    if theta <= 0.9:
        return 1.0 - theta / 0.9
    return -0.75 * (theta - 0.9) / 0.1


def smorz(gres, q_base):
    """1/Q della sezione: lato positivo scalato sulla Q base, lato
    negativo uguale a quello del D5 (stesso OTA RES): 1/Q = sqrt2 * gres."""
    return gres / q_base if gres > 0 else math.sqrt(2.0) * gres


def a_ota(u, lineare):
    """Guadagno a secante dell'OTA: Vs tanh(u/Vs) / u."""
    if lineare:
        return 1.0
    m = max(abs(u), 1e-6)
    return VS * math.tanh(m / VS) / m


def a_lim(v):
    """Conduttanza a secante del limitatore: L(v) / v."""
    m = max(abs(v), 1e-6)
    sp = W_LIM * (softplus((m - VK_LIM) / W_LIM)
                  - softplus(-VK_LIM / W_LIM))
    return G_LIM * sp / m


def softplus(z):
    return z if z > 30 else math.log1p(math.exp(z))


class Sezione:
    """Una sezione SVF 2 poli TPT con OTA (o lineare) e limitatore."""

    def __init__(self, lineare, limitatore):
        self.lineare = lineare
        self.limitatore = limitatore
        self.s1 = self.s2 = 0.0
        self.hp = self.bp = 0.0

    def passo(self, x, g, d):
        """x in volt, g = tan(pi fc / fs), d = 1/Q. Ritorna hp, bp, lp."""
        a1 = a_ota(self.hp, self.lineare)
        a2 = a_ota(self.bp, self.lineare)
        ar = a_ota(self.bp, self.lineare)
        r = d * ar + (a_lim(self.bp) if self.limitatore else 0.0)
        g1, g2 = g * a1, g * a2
        bp = (g1 * (x - self.s2) + self.s1) / (1.0 + g1 * g2 + g1 * r)
        hp = x - self.s2 - (g2 + r) * bp
        lp = g2 * bp + self.s2
        self.s1 = bp + g1 * hp
        self.s2 = lp + g2 * bp
        self.hp, self.bp = hp, bp
        return hp, bp, lp


class Core:
    """4 poli: sezione 1 (Q1 fissa) poi sezione 2 (RES)."""

    def __init__(self, lineare):
        self.a = Sezione(lineare, False)
        self.b = Sezione(lineare, True)

    def passo(self, x, g, gres, modo):
        hp, _, lp = self.a.passo(x, g, 1.0 / Q1)
        hp2, _, lp2 = self.b.passo(hp if modo == "hp" else lp, g,
                                   smorz(gres, Q2))
        return hp2 if modo == "hp" else lp2


# ------------------------------------------------------------ misure ---

def sinusoide(sez_o_core, f_tono, fc, fs, amp_v, dur, coda, passo):
    """Suona un tono, ritorna (ampiezza della fondamentale, rms) in coda."""
    g = math.tan(math.pi * fc / fs)
    n = int(dur * fs)
    n0 = n - int(coda * fs)
    ys = []
    for i in range(n):
        x = amp_v * math.sin(2 * math.pi * f_tono * i / fs)
        ys.append(passo(sez_o_core, x, g))
    ss = sc = cc = ys_ = yc = 0.0
    for i in range(n0, n):
        s = math.sin(2 * math.pi * f_tono * i / fs)
        c = math.cos(2 * math.pi * f_tono * i / fs)
        ss, sc, cc = ss + s * s, sc + s * c, cc + c * c
        ys_, yc = ys_ + ys[i] * s, yc + ys[i] * c
    det = ss * cc - sc * sc
    a, b = (ys_ * cc - yc * sc) / det, (yc * ss - ys_ * sc) / det
    return math.hypot(a, b)


def oscillazione(core_o_sez, fc, fs, dur, coda, passo):
    """Senza ingresso (seme 1 uV): livello rms in dBu e nota in semitoni."""
    g = math.tan(math.pi * fc / fs)
    n = int(dur * fs)
    n0 = n - int(coda * fs)
    ys = []
    for i in range(n):
        x = 1e-6 if i < 10 else 0.0
        ys.append(passo(core_o_sez, x, g))
    seg = ys[n0:]
    rms = math.sqrt(sum(v * v for v in seg) / len(seg))
    # periodo dai passaggi per zero in salita (interpolati)
    zc = []
    for i in range(1, len(seg)):
        if seg[i - 1] < 0 <= seg[i]:
            zc.append(i - 1 + seg[i - 1] / (seg[i - 1] - seg[i]))
    if len(zc) < 3 or rms < 1e-4:
        return -999.0, 0.0
    f = (len(zc) - 1) * fs / (zc[-1] - zc[0])
    return (20 * math.log10(rms / 0.775), 12 * math.log2(f / fc))
