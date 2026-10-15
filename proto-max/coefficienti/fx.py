"""Modello di riferimento di P3: MC-SEND, MC-BUS, MC-RET, MC-MASTER.

Fonte unica dei numeri di P3. Le stesse formule stanno nel codice gen~
(genera_fx.py le scrive): se cambia un numero, cambia qui.

Topologia in Live (Filippo, 2026-10-15: pedali = effetti veri di Live):
- MC-SEND su ogni canale, tra MC-CHANNEL e MC-FILTRO (presa post-EQ,
  pre-filter, pre-fader: SPEC §7). L'audio del canale passa intatto;
  EQ2 -> LEVEL -> 4 ASSIGN -> send~ verso i 4 bus (fx-send-module §2).
- 4 tracce FX: MC-BUS (receive~ del bus: somma delle mandate e dei
  reroute, rail del sommatore) -> effetto di Live (il pedale) -> MC-RET
  (GAIN -> EQ2 -> meter -> 4 REROUTE, pre-fader: fx-module §5). Il fader
  della traccia e il fader del ritorno.
- MC-MASTER sulla traccia Master: MONO (M/S, rampa 1 ms) -> MASTER LEVEL
  -> meter (master-out §3.2 e addendum dec. 111).
Piu send~ con lo stesso nome si sommano nel receive~ (refpage di Max):
il bus e la somma di tutte le mandate e di tutti i reroute.

Origine dei numeri:
- EQ2: celle serie di sim/fx/fx-eq2.cir (fx-module §6 e §8.4). LOW shelf
  complementare Rin 1k, Rf 1k, pot 31k (x), C 56n: kill -30 dB, boost +6.
  HIGH sottrattiva: HP2 Sallen-Key (C 10n, 5,23k in retroazione, 2,5k a
  massa: f0 4,40 kHz, Q 0,346), invertitore, pot 10k (thh) tra HP e -HP,
  sommatore 49,9k: uscita = (1 + k HP2) per la LOW.
- Law dell'EQ2 [PROVVISORIO, da sentire]: SPEC §7 dice solo «bassi:
  rapidi solo al taglio estremo; alti: taglio rapido in partenza poi
  graduale; boost +6». LOW: 0 -> -6 dB tra 50 e 20 % di corsa, -6 ->
  -30 negli ultimi 20 % (fx-module §6: «cut negli ultimi ~15-20 %»).
  HIGH: asintoto 0 -> -15 dB tra 50 e 30 %, poi thh lineare fino al
  kill. Boost: 0 -> +6 dB lineare in dB su meta corsa.
- LEVEL di mandata: pot log curva A, -20 dB a meta corsa (dec. 108).
- ASSIGN: rampa 1 ms (dec. 80).
- GAIN del ritorno [PROVVISORIO]: 0 -> +20 dB lineare in dB su meta corsa
  CW; -40 -> 0 dB tra 5 e 50 %; negli ultimi 5 % fino al silenzio.
- REROUTE: law a tratti della SPEC §7 (fx-module §8.3), smoothing 1 ms.
- Rail: sommatori e VCA a +-18 V, clamp +-16,5 V (fx-module §8.5).
- MASTER LEVEL [PROVVISORIO]: -inf, 0 dB al 80 % (detent), +6 a fine
  corsa (master-out §3.2: unity al 75-80 %).
- MONO: S attraverso un VCA che va da 0 a -100 dB in 1 ms, lineare in dB
  (addendum dec. 111).
- Meter: fondo scala +24 dBu, attacco rapido, rilascio 0,3 s, latch del
  clip 479 ms sopra +23 dBu (sistema-metering §1-§4, dec. 81/90).

Livelli: 1,0 nel digitale = 4,36 V di picco, 0 dBu = -12 dBFS (come P0-P2).
Python puro: nessun pacchetto da installare.
"""

import math

LIV = 1.0954 * 10 ** (12 / 20)  # volt per 1,0 digitale
RAIL = 16.5                     # clamp dei sommatori e dei VCA, volt

# ---- law ----
TAPER_A_MID = 0.1               # pot log curva A: 10 % (-20 dB) a meta corsa


def level_send(t):
    if t <= 0.5:
        return TAPER_A_MID * t / 0.5
    return TAPER_A_MID + (1 - TAPER_A_MID) * (t - 0.5) / 0.5


def interp(t, punti):
    """Interpolazione lineare su [(t, valore), ...] crescenti in t."""
    for (t0, v0), (t1, v1) in zip(punti, punti[1:]):
        if t <= t1:
            return v0 + (v1 - v0) * (t - t0) / (t1 - t0)
    return punti[-1][1]


EQ_BOOST_DB = 6.0
LOW_PUNTI = ((0.0, -30.0), (0.2, -6.0), (0.5, 0.0))
HIGH_GIN_DB = -15.0             # fine del tratto rapido degli alti
HIGH_GIN_T = 0.3
R_IN = 1000.0                   # Rin e Rf della cella LOW
R_POT = 31000.0
C_LOW = 56e-9
C_HP = 10e-9
R_HP1 = 5230.0                  # in retroazione
R_HP2 = 2500.0                  # a massa
R_THH = 10000.0
R_SUM = 49900.0
R_MIN = 1e-3                    # il +1m delle piste nel netlist


def low_db(t):
    if t >= 0.5:
        return EQ_BOOST_DB * (t - 0.5) / 0.5
    return interp(t, LOW_PUNTI)


def low_x(t):
    """Posizione del pot LOW per il guadagno in continua voluto:
    G = (Rf + R(1-x)) / (Rin + R x)  ->  x = (32 - G) / (31 (G + 1))."""
    g = 10 ** (low_db(t) / 20)
    a = R_POT / R_IN
    return (a + 1 - g) / (a * (g + 1))


def high_thh(t):
    if t >= 0.5:
        return 0.5 * 10 ** (EQ_BOOST_DB * (t - 0.5) / 0.5 / 20)
    if t >= HIGH_GIN_T:
        d = HIGH_GIN_DB * (0.5 - t) / (0.5 - HIGH_GIN_T)
        return 0.5 * 10 ** (d / 20)
    return 0.5 * 10 ** (HIGH_GIN_DB / 20) * t / HIGH_GIN_T


GAIN_MAX_DB = 20.0
GAIN_KNEE_DB = -40.0
GAIN_KNEE_T = 0.05


def gain_lin(t):
    if t >= 0.5:
        return 10 ** (GAIN_MAX_DB * (t - 0.5) / 0.5 / 20)
    if t >= GAIN_KNEE_T:
        d = GAIN_KNEE_DB * (0.5 - t) / (0.5 - GAIN_KNEE_T)
        return 10 ** (d / 20)
    return 10 ** (GAIN_KNEE_DB / 20) * t / GAIN_KNEE_T


REROUTE_PUNTI = ((0.0, -100.0), (0.2, -40.0), (0.45, -20.0), (0.7, -10.0),
                 (0.85, -4.0), (0.95, -1.0), (1.0, 0.0))


def reroute_db(t):
    return interp(t, REROUTE_PUNTI)


def reroute_lin(t):
    return 10 ** (reroute_db(t) / 20)


MASTER_MAX_DB = 6.0
MASTER_UNITY_T = 0.8
MASTER_KNEE_DB = -60.0
MASTER_KNEE_T = 0.05


def master_lin(t):
    if t >= MASTER_UNITY_T:
        return 10 ** (MASTER_MAX_DB * (t - MASTER_UNITY_T)
                      / (1 - MASTER_UNITY_T) / 20)
    if t >= MASTER_KNEE_T:
        d = MASTER_KNEE_DB * (MASTER_UNITY_T - t) / (MASTER_UNITY_T
                                                      - MASTER_KNEE_T)
        return 10 ** (d / 20)
    return 10 ** (MASTER_KNEE_DB / 20) * t / MASTER_KNEE_T


# ---- EQ2: risposta analogica esatta (riferimento) ----

def _k_high(thh):
    """Peso di HP2 al sommatore, col carico della 49,9k sul cursore."""
    r1 = R_THH * thh + R_MIN       # verso -HP
    r2 = R_THH * (1 - thh) + R_MIN  # verso +HP
    return (1 / r2 - 1 / r1) / (1 / r1 + 1 / r2 + 1 / R_SUM)


def hp2_w0_q():
    w0 = 1 / (C_HP * math.sqrt(R_HP1 * R_HP2))
    q = 0.5 * math.sqrt(R_HP2 / R_HP1)
    return w0, q


def eq2_analogica(f, x, thh):
    s = 2j * math.pi * f
    ra = R_POT * x + R_MIN
    rb = R_POT * (1 - x) + R_MIN
    zin = R_IN + ra / (1 + s * ra * C_LOW)
    zf = R_IN + rb / (1 + s * rb * C_LOW)
    lo = zf / zin                  # le due inversioni si annullano
    w0, q = hp2_w0_q()
    hp = s * s / (s * s + s * w0 / q + w0 * w0)
    return lo * (1 + _k_high(thh) * hp)


# ---- EQ2 digitale (TPT, bilineare senza prewarp: gira a 4x) ----

def primo_ordine(b0, b1, a1):
    """H(s) = (b0 + b1 s) / (1 + a1 s) = b1/a1 + (b0 - b1/a1) LP.
    Restituisce (tau = a1, alto = b1/a1, basso = b0)."""
    return a1, b1 / a1, b0


def low_sezioni(x):
    """La cella LOW come due sezioni del primo ordine.
    zf/zin = [(R1+Rb + s R1 Rb C) / (1 + s Rb C)]
           * [(1 + s Ra C) / (R1+Ra + s R1 Ra C)]."""
    ra = R_POT * x + R_MIN
    rb = R_POT * (1 - x) + R_MIN
    c = C_LOW
    # sezione A: (1 + s R1 Rb C/(R1+Rb)) / (1 + s Rb C), guadagno (R1+Rb)
    sa = primo_ordine(1.0, R_IN * rb * c / (R_IN + rb), rb * c)
    # sezione B: (1 + s Ra C) / (1 + s R1 Ra C/(R1+Ra)), guadagno 1/(R1+Ra)
    sb = primo_ordine(1.0, ra * c, R_IN * ra * c / (R_IN + ra))
    return sa, sb, (R_IN + rb) / (R_IN + ra)


class Lp1:
    """Polo singolo TPT senza prewarp: g = T / (2 tau)."""

    def __init__(self):
        self.s = 0.0

    def passo(self, x, g):
        v = (x - self.s) * g / (1 + g)
        lp = v + self.s
        self.s = lp + v
        return lp


class Svf:
    def __init__(self):
        self.s1 = self.s2 = 0.0

    def hp(self, x, g, k):
        hp = (x - (k + g) * self.s1 - self.s2) / (1 + g * (k + g))
        bp = g * hp + self.s1
        lp = g * bp + self.s2
        self.s1 = g * hp + bp
        self.s2 = g * bp + lp
        return hp


class Eq2:
    def __init__(self, fs):
        self.fs = fs
        self.a = Lp1()
        self.b = Lp1()
        self.hp = Svf()
        w0, q = hp2_w0_q()
        self.g_hp = math.tan(w0 / (2 * fs))
        self.k_hp = 1 / q

    def passo(self, v, x, thh):
        sa, sb, gk = low_sezioni(x)
        y = v
        for lp, (tau, alto, basso) in ((self.a, sa), (self.b, sb)):
            y = alto * y + (basso - alto) * lp.passo(y, 1 / (2 * self.fs * tau))
        y = gk * y
        return y + _k_high(thh) * self.hp.hp(y, self.g_hp, self.k_hp)


def clamp(v):
    return min(max(v, -RAIL), RAIL)


# ---- dispositivi (un lato; volt del dominio analogico) ----

T_ASSIGN = 0.001                # rampa degli ASSIGN, secondi
T_REROUTE = 0.001               # smoothing del CV di reroute
T_MONO = 0.001


class Mandata:
    """MC-SEND: EQ2 -> LEVEL -> 4 ASSIGN (rampa 1 ms) -> 4 bus."""

    def __init__(self, fs):
        self.fs = fs
        self.eq = Eq2(fs)
        self.a = [0.0] * 4

    def passo(self, v, low, high, level, assign):
        y = self.eq.passo(v, low_x(low), high_thh(high)) * level_send(level)
        passo_r = 1 / (T_ASSIGN * self.fs)
        out = []
        for i in range(4):
            self.a[i] += min(max(assign[i] - self.a[i], -passo_r), passo_r)
            out.append(self.a[i] * y)
        return out


class Ritorno:
    """MC-RET: GAIN (VCA, rail) -> EQ2 (rail) -> meter -> 4 REROUTE."""

    def __init__(self, fs):
        self.fs = fs
        self.eq = Eq2(fs)
        self.r = [0.0] * 4
        self.cr = math.exp(-1 / (T_REROUTE * fs))

    def passo(self, v, gain, low, high, reroute):
        y = clamp(gain_lin(gain) * v)
        y = clamp(self.eq.passo(y, low_x(low), high_thh(high)))
        rr = []
        for i in range(4):
            self.r[i] = reroute_lin(reroute[i]) + self.cr * (
                self.r[i] - reroute_lin(reroute[i]))
            rr.append(self.r[i] * y)
        return y, rr


class Master:
    """MC-MASTER, due lati: MONO (M/S) -> MASTER LEVEL."""

    def __init__(self, fs):
        self.fs = fs
        self.m = 0.0            # rampa del MONO, 0 = stereo, 1 = mono

    def passo(self, l, r, level, mono):
        p = 1 / (T_MONO * self.fs)
        self.m += min(max(mono - self.m, -p), p)
        gs = 10 ** (-5 * self.m)  # -100 dB lineari in dB sulla rampa
        mm, ss = 0.5 * (l + r), 0.5 * (l - r) * gs
        if self.m >= 1:
            ss = 0.0
        g = master_lin(level)
        return g * (mm + ss), g * (mm - ss)


# ---- meter (sistema-metering) ----
V_DBU = 1.0954                  # picco di 0 dBu
METER_FS = V_DBU * 10 ** (24 / 20)
CLIP_V = V_DBU * 10 ** (23 / 20)
T_RILASCIO = 0.3
T_LATCH = 0.479


class Meter:
    def __init__(self, fs):
        self.fs = fs
        self.env = 0.0
        self.latch = 0.0
        self.cr = math.exp(-1 / (T_RILASCIO * fs))

    def passo(self, v):
        a = abs(v)
        self.env = max(a, self.cr * self.env)
        self.latch = T_LATCH if a >= CLIP_V else max(self.latch - 1 / self.fs, 0)
        return self.env / METER_FS, float(self.latch > 0)


def db(x):
    return 20 * math.log10(max(abs(x), 1e-30))


if __name__ == "__main__":
    print("REROUTE, griglia di fx-module §8.3")
    for t, g in ((1, 0), (0.975, -0.5), (0.95, -1), (0.9, -2.5), (0.85, -4),
                 (0.775, -7), (0.7, -10), (0.575, -15), (0.45, -20),
                 (0.325, -30), (0.2, -40), (0.1, -70), (0, -100)):
        print(f"  {t:5.3f}: {reroute_db(t):+7.2f} dB (atteso {g:+.1f})")
    print("EQ2 LOW x: kill", round(low_x(0), 4), "detent", round(low_x(0.5), 4),
          "boost", round(low_x(1), 4))
