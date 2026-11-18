"""LICKSHOT - modello di riferimento (dec. 179-189), un campione alla volta.

Fonte unica dei numeri per MC-LICKSHOT (genera_lickshot.py) e per la
LICKSHOT del banco web (web/strumenti.js, stessi numeri copiati a mano:
prova_lickshot.py li confronta).

Nucleo di Nold («Lickshot-I», 2016), collegamenti dal KiCad di Orald-0
(github.com/Orald-0/lickshot_dub_siren, «DA SBROGLIARE»):
  LFO   CD4069: trigger di Schmitt (22k / 10k) + integratore di Miller
        C 1 uF, R = 22k + VELOCITA 500k. Soglie 6/22 e 16/22 di VDD.
        Discesa lenta T = 0,909 R C; risalita dal diodo (D3 fisso: il tono
        cade a ogni colpo, dec. 184 senza FORMA).
  VCO   CD4046: R1 = 10k + ALTEZZA 50k, C1 100 nF, R2 aperta.
        f0 (VCOin = VDD/2) ~ 0,7 / (R1 C1): Fig. 4 del datasheet TI
        SCHS043B. Legge lineare, zero a VOFF.
  PROFONDITA (dec. 190, al posto di LFO ON/OFF): pot fra la rampa e VDD/2,
        buffer con guadagno verso il VCOin; 0 = tono fisso, 100 = ~4 ottave.
  uscita onda quadra -> C 1 uF su 1k + 100 ohm: passa-alto 145 Hz -> tasto.
Eco (dec. 182, 185, 186): due BBD da 4096 stadi in fila, T = 8192 / (2 fclk);
filtri anti-alias a 2 poli prima e dopo, taglio fclk/4 (max 8 kHz); nel
giro passa-alto 150 Hz e saturazione morbida. TEMPO, RIPETIZIONI,
LIVELLO ECO.

Deduzioni mie (da ascoltare o da simulare, regola 3): VDD 8,6 V, VOFF 1 V,
risalita 0,5 ms, taglio anti-alias fclk/4, passa-alto del giro 150 Hz,
saturazione tanh a 1,5 V, guadagno del giro fino a 1,1 (oltre 1 l'eco si
autoalimenta), TEMPO esponenziale 41-410 ms, liscio del tempo 50 ms
(l'effetto «fionda» quando si gira), VOLUME e LIVELLO ECO a legge
quadratica (pot logaritmico), livello 0 dBu (0,775 V) sul plateau.
"""

import math

VDD = 8.6
LO = 6 / 22 * VDD
HI = 16 / 22 * VDD
VOFF = 1.0
K_F0 = 0.7
C_VCO = 100e-9
R_VCO = 10e3
P_VCO = 50e3
C_LFO = 1e-6
R_LFO = 22e3
P_LFO = 500e3
T_SU = 5e-4
F_HP_OUT = 145.0
V_NOM = 0.775
V_LED = 2.4

N_BBD = 8192
T_MIN = N_BBD / (2 * 100e3)   # clock 100 kHz
T_MAX = N_BBD / (2 * 10e3)    # clock 10 kHz
K_FC = 0.25
FC_MAX = 8000.0
F_HP_GIRO = 150.0
V_SAT = 1.5
G_MAX = 1.1
T_LISCIO = 0.05

# PROFONDITA (dec. 190): VCOin = VDD/2 + prof * A_MAX * rampa normalizzata;
# A_MAX da 16 = (VDD/2 - VOFF + A) / (VDD/2 - VOFF - A): 4 ottave a fondo corsa.
A_MAX = 15 / 17 * (VDD / 2 - VOFF)
INIZIALI = {"alt": 80.0, "vel": 50.0, "prof": 67.0, "vol": 100.0, "trig": 0.0,
            "tempo": 60.0, "rip": 40.0, "eco": 40.0}


def f0(alt):
    return K_F0 / ((R_VCO + (1 - alt / 100) * P_VCO) * C_VCO)


def periodo_lfo(vel):
    r = R_LFO + (1 - vel / 100) * P_LFO
    return (HI - LO) * r * C_LFO / (VDD / 2) + T_SU


def tempo_eco(t):
    return T_MIN * (T_MAX / T_MIN) ** (t / 100)


def fc_bbd(tempo):
    return min(K_FC * N_BBD / (2 * tempo), FC_MAX)


class Svf:
    """Passa-basso a 2 poli, Q 0,707 (SVF trapezoidale), taglio variabile."""

    def __init__(self):
        self.i1 = self.i2 = 0.0

    def __call__(self, x, g):
        k = math.sqrt(2)
        a1 = 1 / (1 + g * (g + k))
        a2 = g * a1
        a3 = g * a2
        v3 = x - self.i2
        v1 = a1 * self.i1 + a2 * v3
        v2 = self.i2 + a2 * self.i1 + a3 * v3
        self.i1 = 2 * v1 - self.i1
        self.i2 = 2 * v2 - self.i2
        return v2


def blep(t, dt):
    if t < dt:
        t /= dt
        return t + t - t * t - 1
    if t > 1 - dt:
        t = (t - 1) / dt
        return t * t + t + t + 1
    return 0.0


class Lickshot:
    def __init__(self, fs, **p):
        self.fs = fs
        self.p = dict(INIZIALI, **p)
        self.s = {k: self.p[k] for k in ("alt", "vel", "prof", "vol", "tempo", "rip", "eco")}
        self.vi, self.su, self.fase = VDD / 2, False, 0.0
        self.hpx = self.hpy = 0.0
        self.gx = self.gy = 0.0
        self.pre, self.post = Svf(), Svf()
        self.n = int(0.5 * fs) + 4
        self.buf = [0.0] * self.n
        self.w = 0
        self.td = tempo_eco(self.p["tempo"]) * fs
        self.led = 0.0

    def campione(self):
        p, s, fs = self.p, self.s, self.fs
        t10 = math.exp(-1 / (0.010 * fs))  # come lisci() di genera_fx
        for k in s:
            s[k] = p[k] + t10 * (s[k] - p[k])
        r1 = R_VCO + (1 - s["alt"] / 100) * P_VCO
        fz = K_F0 / (r1 * C_VCO)
        rl = R_LFO + (1 - s["vel"] / 100) * P_LFO
        giu = VDD / 2 / (rl * C_LFO) / fs
        su = (HI - LO) / T_SU / fs
        if self.su:
            self.vi += su
            if self.vi >= HI:
                self.vi, self.su = HI, False
        else:
            self.vi -= giu
            if self.vi <= LO:
                self.vi, self.su = LO, True
        vco = VDD / 2 + s["prof"] / 100 * A_MAX * (self.vi - VDD / 2) / ((HI - LO) / 2)
        f = fz * max(0.0, vco - VOFF) / (VDD / 2 - VOFF)
        self.f = f
        dt = max(f / fs, 1e-9)
        t = self.fase
        x = (1.0 if t < 0.5 else -1.0) + blep(t, dt)
        t2 = t + 0.5 - (t + 0.5 >= 1)
        x -= blep(t2, dt)
        self.fase += f / fs
        if self.fase >= 1:
            self.fase -= 1
        khp = 1 / (1 + 2 * math.pi * F_HP_OUT / fs)
        self.hpy = khp * (self.hpy + x - self.hpx)
        self.hpx = x
        vv = s["vol"] / 100
        dry = self.hpy * (p["trig"] > 0.5) * V_NOM * vv * vv
        # eco
        tm = tempo_eco(s["tempo"])
        self.td += (tm * fs - self.td) * (1 - math.exp(-1 / (T_LISCIO * fs)))
        g = math.tan(math.pi * fc_bbd(self.td / fs) / fs)
        rpos = self.w - self.td
        while rpos < 0:
            rpos += self.n
        i0 = int(rpos)
        fr = rpos - i0
        rd = self.buf[i0 % self.n] * (1 - fr) + self.buf[(i0 + 1) % self.n] * fr
        post = self.post(rd, g)
        kg = 1 / (1 + 2 * math.pi * F_HP_GIRO / fs)
        self.gy = kg * (self.gy + post - self.gx)
        self.gx = post
        fb = V_SAT * math.tanh(G_MAX * s["rip"] / 100 * self.gy / V_SAT)
        self.buf[self.w] = self.pre(dry + fb, g)
        self.w = (self.w + 1) % self.n
        ve = s["eco"] / 100
        self.led = max(0.0, min(1.0, (self.vi - V_LED) / (HI - V_LED)))
        return dry + ve * ve * post
