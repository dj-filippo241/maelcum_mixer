"""Modello di riferimento di P4: MC-MIC.

Fonte unica dei numeri di P4. Le stesse formule stanno nel codice gen~
(genera_mic.py le scrive): se cambia un numero, cambia qui.

Catena (mic-mono-moduli §2-§5 e REV dec. 111):
  ingresso -> INA +30 dB fisso (rail) -> passa-alto 60 Hz -> stadio 2
  0...+30 dB col pot GAIN (rail) -> nodo PRE -> LED -> EQ2 (rail) -> MUTE
  (VCA, 0 -> -100 dB in 1 ms) -> uscita L = R (mono centrato) e 4 SEND
  verso i bus di P3 (send~ mcfx_b<n>L/R).

Origine dei numeri:
- INA e stadio 2: sim/mic/mic-pre.inc. INA 1 + 998/32,4; ingresso con
  10 ohm per gamba e carico 2,32k || 2x47k; sorgente 150 ohm (SM58-class,
  come mic-pre-ac.cir). Stadio 2: G2 = (5,36k + x 5k) / (332 + (1-x) 5k),
  pot LINEARE: 29,5...59,3 dB (mic-mono-moduli §3.3). Il taper del pot e
  la voce 40.
- Passa-alto: Sallen-Key 2x220n, 8,45k in retroazione, 16,9k a massa:
  f0 60,5 Hz, Q 0,707 [RATIFICATO dec. 97].
- Rail del front-end (+-15 V LN): taglio a +-13,5 V = +21,8 dBu di sinusoide,
  l'overload dell'INA simulato (§3.3). EQ2 e VCA del MUTE su +-18 V:
  +-16,5 V come P3.
- EQ2: le celle di P3 (fx.Eq2, fx.low_x, fx.high_thh): backend.inc usa
  gli stessi valori di fx-eq2.cir. Law [PROVVISORIO] come P3.
- LED (§5.2), presa al nodo PRE: verde >= -6 dBu, giallo >= +11 dBu,
  rosso >= +17 dBu con latch 0,5 s [PROVVISORIO, B6]. Detector di picco
  con rilascio 0,3 s (sistema-metering §2).
- MUTE: rampa 1 ms lineare in dB fino a -100 dB, poi zero (REV dec. 111,
  stessa cella del MONO del master).
- SEND: pot passivo -inf...0 dB; taper curva A come il LEVEL di P3
  [PROVVISORIO, voce 40].

Ingresso in Live: la scheda audio fa la parte del connettore XLR. Con
il suo preamp al MINIMO, 0 dBFS di picco all'ingresso = SCHEDA_DBU
(sinusoide) al microfono. MC-MIC aggiunge i 30...60 dB del modulo.
Uscita: 1,0 digitale = 4,36 V di picco, 0 dBu = -12 dBFS (come P0-P3).
Python puro: nessun pacchetto da installare.
"""

import math

import fx

# ---- ingresso dalla scheda audio ----
SCHEDA_DBU = 9.0                # [PROVVISORIO] 0 dBFS al preamp minimo
V_SCHEDA = fx.V_DBU * 10 ** (SCHEDA_DBU / 20)   # volt per 1,0 in ingresso

# ---- INA e stadio 2 (mic-pre.inc) ----
R_SORG = 150.0
R_SERIE = 2 * 10.0
R_CARICO = 1 / (1 / 2320.0 + 1 / (2 * 47000.0))
G_INA = 1 + 2 * 499.0 / 32.4
G_INGRESSO = G_INA * R_CARICO / (R_CARICO + R_SORG + R_SERIE)
R1_G2 = 332.0
R2_G2 = 5360.0
P_G2 = 5000.0
RAIL_FE = 13.5                  # +-15 V LN: +21,8 dBu di sinusoide

# ---- passa-alto Sallen-Key ----
C_HPF = 220e-9
R_HPF_FB = 8450.0
R_HPF_GND = 16900.0

# ---- LED ----
LED_DBU = (-6.0, 11.0, 17.0)    # verde, giallo, rosso
LED_V = tuple(fx.V_DBU * 10 ** (d / 20) for d in LED_DBU)
T_LED = 0.3                     # rilascio del detector
T_ROSSO = 0.5                   # latch del rosso

T_MUTE = 0.001


def g2(x):
    """Stadio 2 col pot GAIN lineare (x da 0 a 1)."""
    return (R2_G2 + x * P_G2) / (R1_G2 + (1 - x) * P_G2)


# Pot GAIN a curva inversa C 20 % (dec. 129 E2, 2026-10-22; era lineare):
# x = 0,8 a meta corsa. Lo stadio 2 da gia piu dB in alto (col lineare
# l'ultimo 10 % vale 8,4 dB): la curva C li spalma quasi uguali su tutta la
# corsa (29,5 / 36,3 / 46,4 / 50,9 / 59,3 dB a 0/25/50/75/100 %). La
# curva A li avrebbe ammassati ancora di piu in alto (31,1 dB a meta).
TAPER_C_MID = 0.2


def gain_x(t):
    """Rotazione t del pot GAIN -> posizione elettrica x (curva C)."""
    u = 1 - t
    a = TAPER_C_MID * u / 0.5 if u <= 0.5 else \
        TAPER_C_MID + (1 - TAPER_C_MID) * (u - 0.5) / 0.5
    return 1 - a


def gain_db(t):
    """Guadagno del preamp a centro banda, dB, dal microfono al nodo PRE;
    t = posizione elettrica del pot (x), come in LTspice."""
    return 20 * math.log10(G_INGRESSO * g2(t))


def hpf_w0_q():
    w0 = 1 / (C_HPF * math.sqrt(R_HPF_FB * R_HPF_GND))
    q = 0.5 * math.sqrt(R_HPF_GND / R_HPF_FB)
    return w0, q


def pre_analogico(f, t):
    """Risposta dal microfono al nodo PRE (complessa)."""
    s = 2j * math.pi * f
    w0, q = hpf_w0_q()
    hp = s * s / (s * s + s * w0 / q + w0 * w0)
    return G_INGRESSO * g2(t) * hp


def clamp_fe(v):
    return min(max(v, -RAIL_FE), RAIL_FE)


class Mic:
    """MC-MIC a 4x della frequenza di Live; volt del dominio analogico.
    passo() prende un campione in volt al microfono e restituisce
    (nodo PRE, uscita dopo il MUTE)."""

    def __init__(self, fs4):
        self.fs = fs4
        self.hpf = fx.Svf()
        w0, q = hpf_w0_q()
        self.g_hpf = math.tan(w0 / (2 * fs4))
        self.k_hpf = 1 / q
        self.eq = fx.Eq2(fs4)
        self.m = 0.0            # rampa del MUTE, 0 = aperto, 1 = muto

    def passo(self, v, gain, low, high, mute):
        y = clamp_fe(G_INGRESSO * v)
        y = self.hpf.hp(y, self.g_hpf, self.k_hpf)
        pre = clamp_fe(g2(gain_x(gain)) * y)
        y = fx.clamp(self.eq.passo(pre, fx.low_x(low), fx.high_thh(high)))
        p = 1 / (T_MUTE * self.fs)
        self.m += min(max(mute - self.m, -p), p)
        gm = 10 ** (-5 * self.m) if self.m < 1 else 0.0
        return pre, y * gm


def send_lin(t):
    return fx.level_send(t)


class Led:
    """Detector di picco al nodo PRE e tre soglie; 0 = spento, 1 verde,
    2 giallo, 3 rosso. Gira alla frequenza di Live sul picco dei 4
    campioni."""

    def __init__(self, fs):
        self.fs = fs
        self.env = 0.0
        self.latch = 0.0
        self.cr = math.exp(-1 / (T_LED * fs))

    def passo(self, picco):
        self.env = max(picco, self.cr * self.env)
        if picco >= LED_V[2]:
            self.latch = T_ROSSO
        else:
            self.latch = max(self.latch - 1 / self.fs, 0.0)
        if self.latch > 0:
            return 3
        return int(self.env >= LED_V[0]) + int(self.env >= LED_V[1])


if __name__ == "__main__":
    print(f"Ingresso: G_INA {G_INA:.3f}, con la sorgente {G_INGRESSO:.3f}")
    for t in (0, 0.5, 1):
        print(f"  GAIN {t * 100:3.0f} %: {gain_db(t):.2f} dB")
    w0, q = hpf_w0_q()
    print(f"Passa-alto: f0 {w0 / 2 / math.pi:.1f} Hz, Q {q:.3f}")
