"""Modello di riferimento del 5-way MC-5WAY (prototipo Max P2).

Fonte unica dei numeri del P2. Le stesse formule stanno nel codice gen~
(genera_5way.py le scrive in MC-5WAY.genexpr): se cambia un numero,
cambia qui.

Origine dei numeri (five-way-module.md):
- Banca dei kill: LR4 allineata in fase (§3.1). Spina HP4 condivisa ai
  4 crossover; ogni via e una presa sulla spina seguita dal suo LP4 e
  dagli allpass A2 dei crossover sopra di lei. Somma = prodotto dei 4 A2:
  modulo 1 esatto. Crossover 90 / 350 / 1200 / 3500 Hz [PROVVISORIO,
  B3 / q67]. Kill = interruttore, taglio netto (dec. 88).
- EQ creativo: 5 celle a campana in serie dopo la banca (§4):
  H = 1 + b * BP_norm, BP_norm con picco 1 a f0. b = -1 notch, b > 0
  boost (cella v0.2.1, §4.2 punto 4).
  GAIN massimo +15 / +15 / +15 / +12 / +9 dB (§1).
  POSITION: 20-120 / 80-400 / 250-1500 / 800-5000 / 3000-20000 Hz,
  law esponenziale (opzione B, §4; replica servo: f0 proporzionale a
  Ictl dallo shaper).
  WIDTH: Q 3 / 1 / 0,5 (switch, §4.1 punto 2).
- Law del GAIN (§4.1 punto 4, famiglia eq-serie §10) [PROVVISORIO, si
  conferma a orecchio]: meta corsa CW = 0 -> +max lineare in dB; meta
  corsa CCW = 0 -> -27 dB lineare in dB fino al 5 %, poi notch negli
  ultimi 5 % (come le shelf di eq-serie §10). Il -27 dB e preso dalle
  shelf: per le campane del 5-way il design dice solo «accelerazione
  negli ultimi 5 %».
- Riferimento interno -6 dB (dec. 73): pad e make-up si annullano nel
  percorso lineare; contano per i livelli dei saturatori (parte 2).

Livelli: 1,0 nel digitale = 4,36 V di picco, 0 dBu = -12 dBFS (come P1).

Discretizzazione: SVF TPT (Zavalishin), lineare. La bilineare conserva
le identita algebriche: LP4 + HP4 = A2 vale anche nel digitale, quindi la
somma della banca resta piatta esatta. Gira a 4x (oversampling di P0).

Python puro: nessun pacchetto da installare.
"""

import cmath
import math

LIV = 1.0954 * 10 ** (12 / 20)  # volt per 1,0 digitale (0 dBu = -12 dBFS)
PAD = 0.5                       # riferimento interno -6 dB (dec. 73)

CROSSOVER = (90.0, 350.0, 1200.0, 3500.0)
VIE = ("SUB", "KICK", "MID", "HIGH", "SUPER")
Q_BW = 1.0 / math.sqrt(2.0)

BANDE = ("EQ1", "EQ2", "EQ3", "EQ4", "EQ5")
GAIN_MAX = (15.0, 15.0, 15.0, 12.0, 9.0)
POSIZIONE = ((20.0, 120.0), (80.0, 400.0), (250.0, 1500.0),
             (800.0, 5000.0), (3000.0, 20000.0))
WIDTH = ("NARROW", "MEDIUM", "BROAD")
Q_WIDTH = (3.0, 1.0, 0.5)

CUT_KNEE_DB = -27.0             # dove inizia l'accelerazione al notch
CUT_KNEE_TH = 0.05


def gain_db(theta, gmax):
    """GAIN: 0 -> notch, 0,05 -> -27 dB, 0,5 -> 0 dB, 1 -> +gmax."""
    if theta >= 0.5:
        return gmax * (theta - 0.5) / 0.5
    if theta >= CUT_KNEE_TH:
        return CUT_KNEE_DB * (0.5 - theta) / (0.5 - CUT_KNEE_TH)
    return None                 # tratto finale: usare gain_lin


def gain_lin(theta, gmax):
    """Guadagno al centro |1 + b| come numero (0 = notch)."""
    d = gain_db(theta, gmax)
    if d is not None:
        return 10 ** (d / 20)
    return 10 ** (CUT_KNEE_DB / 20) * theta / CUT_KNEE_TH


def b_di(theta, gmax):
    return gain_lin(theta, gmax) - 1.0


def posizione(theta, banda):
    lo, hi = POSIZIONE[banda]
    return lo * (hi / lo) ** theta


class Svf:
    """SVF TPT lineare: restituisce (lp, bp, hp); k = 1/Q."""

    def __init__(self):
        self.s1 = self.s2 = 0.0

    def passo(self, x, g, k):
        hp = (x - (k + g) * self.s1 - self.s2) / (1 + g * (k + g))
        bp = g * hp + self.s1
        lp = g * bp + self.s2
        self.s1 = g * hp + bp
        self.s2 = g * bp + lp
        return lp, bp, hp


def g_di(f, fs):
    return math.tan(math.pi * f / fs)


class Banca:
    """Banca LR4 allineata in fase, 5 vie, kill a interruttore."""

    def __init__(self, fs, crossover=CROSSOVER):
        self.fs = fs
        self.g = [g_di(f, fs) for f in crossover]
        self.k = 1 / Q_BW
        # spina: 2 sezioni HP per crossover
        self.spina = [[Svf(), Svf()] for _ in range(4)]
        # LP4 per le vie 0-3
        self.lp = [[Svf(), Svf()] for _ in range(4)]
        # allpass: SUB 3 (c2, c3, c4), KICK 2, MID 1
        self.ap = [[Svf() for _ in range(3 - v)] for v in range(3)]

    def passo(self, x, kill=(1, 1, 1, 1, 1)):
        k = self.k
        prese = [x]
        s = x
        for c in range(4):
            for sez in self.spina[c]:
                s = sez.passo(s, self.g[c], k)[2]
            prese.append(s)
        vie = []
        for v in range(4):
            y = prese[v]
            for sez in self.lp[v]:
                y = sez.passo(y, self.g[v], k)[0]
            if v < 3:
                for j, sez in enumerate(self.ap[v]):
                    bp = sez.passo(y, self.g[v + 1 + j], k)[1]
                    y = y - 2 * k * bp
            vie.append(y)
        vie.append(prese[4])
        return sum(kv * y for kv, y in zip(kill, vie)), vie


class Cella:
    """Campana H = 1 + b * k * BP (picco del BP normalizzato a 1)."""

    def __init__(self):
        self.svf = Svf()

    def passo(self, x, f0, q, b, fs):
        k = 1 / q
        bp = self.svf.passo(x, g_di(f0, fs), k)[1]
        return x + b * k * bp


class Modulo:
    """Percorso lineare: banca -> 5 celle in serie. Ingresso e uscita in
    unita digitali (il pad e il make-up si annullano)."""

    def __init__(self, fs, crossover=CROSSOVER):
        self.fs = fs
        self.banca = Banca(fs, crossover)
        self.celle = [Cella() for _ in range(5)]

    def passo(self, x, kill, gain, pos, width):
        y, _ = self.banca.passo(x, kill)
        for i, c in enumerate(self.celle):
            y = c.passo(y, posizione(pos[i], i), Q_WIDTH[width[i]],
                        b_di(gain[i], GAIN_MAX[i]), self.fs)
        return y


# ---- GROWL e NASTRO (five-way §5bis, sim/five-way/drive2-chain.cir) ----
# Livelli in volt del dominio interno (-6 dBu nominale = 0,549 Vp).
# y1 = x + mg * (kg * HP(W(LP(x))) - LP(x));  y2 = y1 + mt * dt.
# Manopole = pot lineari (§5bis.2).

VT27 = 0.025865
D_IS = 2.52e-9
D_N = 1.752
D_RS = 0.568
FX_GROWL = 350.0                # dec. 99 (g)
KG = 0.613
KT = 0.206
G_RIN = 10e3
G_RF = 22e3
G_RA = 2200.0 + D_RS            # ramo 1 diodo
G_RB = 2200.0 + 3 * D_RS        # ramo 3 diodi
G_NA = D_N * VT27
G_NB = 3 * D_N * VT27
F_HP_G = 1 / (2 * math.pi * 10e-6 * (10e3 / KG))     # 0,98 Hz
J_BETA = 5e-3
J_VTO = -3.0
J_LAMBDA = 6e-3
J_RD = 1500.0
J_RSU = 150.0
J_RSB = 900.0
J_CB = 2200e-6
J_VCC = 18.0
F_HP_T = 1 / (2 * math.pi * 10e-6 * (10e3 / KT))     # 0,33 Hz
NEWTON = 4


def _ramo(i_in, rr, nvt):
    """Corrente nel ramo diodi+R del clipper, data la corrente d'ingresso
    i_in >= 0: i * (1 + rr/RF) + vd/RF = i_in, i = Is (e^(vd/nvt) - 1).
    Newton sulla tensione dei diodi, partendo da sopra (converge)."""
    vd = nvt * math.log(1 + i_in / D_IS)
    for _ in range(NEWTON):
        ex = math.exp(vd / nvt)
        f = D_IS * (ex - 1) * (1 + rr / G_RF) + vd / G_RF - i_in
        df = D_IS * ex / nvt * (1 + rr / G_RF) + 1 / G_RF
        vd = vd - f / df
    i = D_IS * (math.exp(vd / nvt) - 1)
    return G_RF * (i_in - i)    # tensione sul feedback = |uscita|


def clipper_growl(low):
    """Uscita invertita e cambiata di segno (W = -gout): stesso segno
    dell'ingresso, guadagno 2,2 a piccolo segnale."""
    i_in = low / G_RIN
    if i_in >= 0:
        return _ramo(i_in, G_RA, G_NA)
    return -_ramo(-i_in, G_RB, G_NB)


J_RTS = 10e3 / KT                 # sommatore: carico AC sul drain
J_RP = J_RD * J_RTS / (J_RD + J_RTS)


def jfet_ids(vgs, vds):
    """Shichman-Hodges (modello NJF di LTspice): corrente e derivate."""
    vov = vgs - J_VTO
    if vov <= 0:
        return 0.0, 0.0, 0.0
    cl = 1 + J_LAMBDA * vds
    if vds >= vov:                                   # saturazione
        i = J_BETA * vov * vov * cl
        return i, 2 * J_BETA * vov * cl, J_BETA * vov * vov * J_LAMBDA
    q = vds * (2 * vov - vds)                        # triodo
    return (J_BETA * q * cl, 2 * J_BETA * vds * cl,
            J_BETA * ((2 * vov - 2 * vds) * cl + q * J_LAMBDA))


def jfet_passo(vg, vs2, vc, idd):
    """Risolve Id del CS JFET (Newton da idd del campione prima).
    Drain: Rd verso Vcc, e il sommatore (Rts) dietro il condensatore
    carico a vc. Restituisce (Id, Vd)."""
    for _ in range(NEWTON):
        vd = J_RP * (J_VCC / J_RD + vc / J_RTS - idd)
        vs = vs2 + J_RSU * idd
        i, dgs, dds = jfet_ids(vg - vs, vd - vs)
        f = idd - i
        df = 1 + dgs * J_RSU + dds * (J_RP + J_RSU)
        idd = max(idd - f / df, 0.0)
    return idd, J_RP * (J_VCC / J_RD + vc / J_RTS - idd)


def jfet_riposo():
    """Punto di lavoro a ingresso zero: (Vs2, Id, Vd)."""
    vs2, idd = 2.1, 2e-3
    for _ in range(300):
        vc = J_VCC - J_RD * idd                      # condensatore carico
        idd, vd = jfet_passo(0.0, vs2, vc, idd)
        vs2 += 0.2 * (J_RSB * idd - vs2)       # smorzato: diretto oscilla
    return vs2, idd, vd


class Hp1:
    """Passa-alto del 1o ordine TPT (condensatore di accoppiamento)."""

    def __init__(self, f, fs, x0=0.0):
        self.g = math.tan(math.pi * f / fs)
        self.s = x0             # stato = livello in continua gia caricato

    def passo(self, x):
        v = (x - self.s) * self.g / (1 + self.g)
        lp = v + self.s
        self.s = lp + v
        return x - lp


class Saturatori:
    def __init__(self, fs):
        self.fs = fs
        self.lp = Svf()
        self.g_lp = g_di(FX_GROWL, fs)
        self.hp_g = Hp1(F_HP_G, fs)
        self.vs2, self.idd, vd = jfet_riposo()
        self.vc = vd                                 # condensatore d'uscita
        self.k_cb = 1 / (fs * J_CB)
        self.k_c = 1 / (fs * 10e-6 * J_RTS)

    def passo(self, x, mg, mt):
        """x in volt; restituisce (y2, dg, dt)."""
        low = self.lp.passo(x, self.g_lp, 1 / Q_BW)[0]
        dg = KG * self.hp_g.passo(clipper_growl(low)) - low
        y1 = x + mg * dg
        self.idd, vd = jfet_passo(y1, self.vs2, self.vc, self.idd)
        vtac = vd - self.vc
        self.vs2 += self.k_cb * (self.idd - self.vs2 / J_RSB)
        self.vc += self.k_c * vtac
        dt = -KT * vtac - y1
        return y1 + mt * dt, dg, dt


# ---- risposte analogiche ideali (riferimento delle prove) ----

def _lp2(s, w):
    return w * w / (s * s + s * w / Q_BW + w * w)


def _hp2(s, w):
    return s * s / (s * s + s * w / Q_BW + w * w)


def _ap2(s, w):
    return (s * s - s * w / Q_BW + w * w) / (s * s + s * w / Q_BW + w * w)


def vie_analogiche(f, crossover=CROSSOVER):
    s = 2j * math.pi * f
    w = [2 * math.pi * c for c in crossover]
    spina = [1.0]
    for c in range(4):
        spina.append(spina[-1] * _hp2(s, w[c]) ** 2)
    vie = []
    for v in range(4):
        y = spina[v] * _lp2(s, w[v]) ** 2
        for c in range(v + 1, 4):
            y *= _ap2(s, w[c])
        vie.append(y)
    vie.append(spina[4])
    return vie


def cella_analogica(f, f0, q, b):
    s = 2j * math.pi * f
    w = 2 * math.pi * f0
    bpn = (s * w / q) / (s * s + s * w / q + w * w)
    return 1 + b * bpn


def db(x):
    return 20 * math.log10(max(abs(x), 1e-30))


def risposta_digitale(passo, f, fs, n=None, coda=None):
    """Ampiezza complessa di un sistema a campioni (fit sin/cos)."""
    n = n or int(max(0.25, 30 / f) * fs)
    coda = coda or n // 2
    ys = []
    for i in range(n):
        ys.append(passo(math.sin(2 * math.pi * f * i / fs)))
    ss = sc = cc = a1 = a2 = 0.0
    for i in range(n - coda, n):
        sn = math.sin(2 * math.pi * f * i / fs)
        cs = math.cos(2 * math.pi * f * i / fs)
        ss, sc, cc = ss + sn * sn, sc + sn * cs, cc + cs * cs
        a1, a2 = a1 + ys[i] * sn, a2 + ys[i] * cs
    det = ss * cc - sc * sc
    a, b = (a1 * cc - a2 * sc) / det, (a2 * ss - a1 * sc) / det
    return complex(a, b)        # y = a sin + b cos -> H = a + j b


if __name__ == "__main__":
    # controllo rapido: somma piatta e kill, contro le formule analogiche
    fs = 4 * 48000.0
    print("Banca: somma e singole vie, digitale (4x 48 kHz) contro analogico")
    for f in (10, 40, 90, 200, 350, 700, 1200, 2500, 3500, 8000, 16000):
        m = Banca(fs)
        h = risposta_digitale(lambda x: m.passo(x)[0], f, fs)
        va = vie_analogiche(f)
        print(f"  {f:6.0f} Hz  somma {db(h):+.4f} dB  "
              f"(analogica {db(sum(va)):+.4f})")
    print("Cella EQ3 a 700 Hz, +15 / notch, Q 3 / 1 / 0,5")
    for qi, q in enumerate(Q_WIDTH):
        for th in (1.0, 0.0):
            b = b_di(th, 15)
            c = Cella()
            h = risposta_digitale(lambda x: c.passo(x, 700, q, b, fs), 700, fs)
            print(f"  Q {q}: theta {th}  {db(h):+.2f} dB  "
                  f"(analogica {db(cella_analogica(700, 700, q, b)):+.2f})")
