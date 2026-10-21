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
- Core (c-B): stesso SVF con integratori lineari (VCA puliti). Limitatore
  tarato su `sim/filtro/RISULTATI-cb-4p.md` §RES (2026-10-21): 2+2 o 3+3
  diodi, selettore LIMITATORE del prototipo (scelta di Filippo
  all'ascolto). Prima di allora il PULITO usava il limitatore del (a′) e
  oscillava a +8,0 dBu invece di +4,4. Terza voce "OTA" (todo 126,
  Filippo 2026-10-21): niente diodi, il tetto e la tanh dell'OTA della
  RES dietro un partitore 1/15, che toglie smorzamento solo quanto vale
  la RES: a RES zero il programma forte resta lineare
  (RISULTATI-cb-4p §Limitatore che si spegne con la RES).
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

# Pendenze a 4 poli per B2 (q64): (Q1, f1/fc, Q2, f2/fc), -3 dB sul taglio
# salvo LR4 (-6 dB). Tabelle classiche (Bessel normalizzato a -3 dB).
# Nell'HPF le frequenze delle sezioni si dividono invece di moltiplicarsi.
ALLINEAMENTI = {
    "BUTTERWORTH": (0.5412, 1.0, 1.3066, 1.0),
    "LINKWITZ-RILEY": (0.7071, 1.0, 0.7071, 1.0),
    "BESSEL": (0.5219, 1.4192, 0.8055, 1.5912),
}

# limitatore del core (a′) (tarato sul D5, vedi taratura())
G_LIM = 1.7
VK_LIM = 0.82
W_LIM = 0.06                    # ginocchio morbido dei diodi, volt
LIM_OTA = (G_LIM, VK_LIM, W_LIM)
# limitatore del core (c-B): (G, VK, W). G = 10k/4,7k, la conduttanza del
# circuito. Tarato su LTspice cb-4p-res-*.cir / cb-4p-res33-*.cir:
# oscillazione +4,5 / +6,7 dBu (LTspice +4,4 / +6,8), risonanza sul
# programma entro 1 dB (2+2) e 1,6 dB (3+3).
LIM_PULITO = {"2+2": (2.13, 0.72, 0.06), "3+3": (2.13, 0.93, 0.09),
              "OTA": None}
# voce OTA: partitore dell'OTA della RES, tetto Vs = 2 VT / k (0,776 V)
K_RES = 1.0 / 15.0
VS_RES = 2.0 * VT / K_RES


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


def a_tanh(u, vs):
    """Guadagno a secante di una tanh: vs tanh(u/vs) / u."""
    m = max(abs(u), 1e-6)
    return vs * math.tanh(m / vs) / m


def a_lim(v, lim=LIM_OTA):
    """Conduttanza a secante del limitatore: L(v) / v."""
    g, vk, w = lim
    m = max(abs(v), 1e-6)
    sp = w * (softplus((m - vk) / w) - softplus(-vk / w))
    return g * sp / m


def softplus(z):
    return z if z > 30 else math.log1p(math.exp(z))


class Sezione:
    """Una sezione SVF 2 poli TPT con OTA (o lineare) e limitatore."""

    def __init__(self, lineare, limitatore, lim=LIM_OTA):
        self.lineare = lineare
        self.limitatore = limitatore
        self.lim = lim
        self.s1 = self.s2 = 0.0
        self.hp = self.bp = 0.0

    def passo(self, x, g, d, qb=None):
        """x in volt, g = tan(pi fc / fs), d = 1/Q. Ritorna hp, bp, lp.
        qb = 1/Q base: serve solo alla voce OTA (smorzamento fisso)."""
        a1 = a_ota(self.hp, self.lineare)
        a2 = a_ota(self.bp, self.lineare)
        ar = a_ota(self.bp, self.lineare)
        if self.limitatore and self.lim is None:
            # smorzamento fisso qb meno quello che toglie l'OTA della RES
            r = qb - (qb - d) * a_tanh(self.bp, VS_RES)
        else:
            r = d * ar + (a_lim(self.bp, self.lim) if self.limitatore
                          else 0.0)
        g1, g2 = g * a1, g * a2
        bp = (g1 * (x - self.s2) + self.s1) / (1.0 + g1 * g2 + g1 * r)
        hp = x - self.s2 - (g2 + r) * bp
        lp = g2 * bp + self.s2
        self.s1 = bp + g1 * hp
        self.s2 = lp + g2 * bp
        self.hp, self.bp = hp, bp
        return hp, bp, lp


class Core:
    """4 poli: sezione 1 (Q fissa) poi sezione 2 (RES), pendenza a scelta."""

    def __init__(self, lineare, fs, allineamento="BUTTERWORTH", lim="2+2"):
        self.a = Sezione(lineare, False)
        self.b = Sezione(lineare, True,
                         LIM_PULITO[lim] if lineare else LIM_OTA)
        self.fs = fs
        self.al = ALLINEAMENTI[allineamento]

    def passo(self, x, fc, gres, modo):
        q1, m1, q2, m2 = self.al
        if modo == "hp":
            m1, m2 = 1 / m1, 1 / m2
        g1 = math.tan(math.pi * fc * m1 / self.fs)
        g2 = math.tan(math.pi * fc * m2 / self.fs)
        hp, _, lp = self.a.passo(x, g1, 1.0 / q1)
        hp2, _, lp2 = self.b.passo(hp if modo == "hp" else lp, g2,
                                   smorz(gres, q2), 1.0 / q2)
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


# ------------------------------------------------------- overdrive ---
# Overdrive v0.2 (filter-module §5ter, dec. 99/110): y = x + m (k CLIP(2x) - x)
# CLIP = 2,2k + 2+2 1N4148 a massa (modello di od2-chain.cir), m = theta^2,5.
OD_K = 1.171
OD_R = 2200.0
OD_IS = 2.52e-9
OD_A = 2 * 1.752 * 0.025865     # due diodi in serie, N 1,752, 27 C
OD_ESP = 2.5


def clip(v):
    """Tensione sui diodi: (v - w)/R = 2 Is sinh(w/A), due passi di Newton."""
    s = 1.0 if v >= 0 else -1.0
    a = abs(v)
    w = min(a, OD_A * math.asinh(a / (2 * OD_IS * OD_R)))
    for _ in range(3):
        e = math.exp(w / OD_A)
        f = (a - w) / OD_R - OD_IS * (e - 1 / e)
        df = -1 / OD_R - OD_IS * (e + 1 / e) / OD_A
        w = w - f / df
    return s * w


def overdrive(x, theta):
    m = theta ** OD_ESP
    return x + m * (OD_K * clip(2 * x) - x)
