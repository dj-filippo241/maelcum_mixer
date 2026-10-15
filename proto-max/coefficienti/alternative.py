"""Alternative al NASTRO per il prototipo P2 (Filippo, 2026-10-15:
«nastro, exciter e transistor»). Solo prototipo: si confrontano a
orecchio con il NASTRO di oggi (selettore NASTRO VER). Tutte in
parallelo al pulito come il NASTRO: y2 = y1 + mt * d, con la stessa
manopola (taper A x NASTRO_MAX).

- COMPLETO: il JFET del NASTRO tra enfasi (prima) e de-enfasi (dopo) degli
  acuti, shelf del 1o ordine zero 1,5 kHz / polo 5 kHz (+10,5 dB): sulle
  parti forti gli acuti saturano prima. Nel ramo saturato una gobba fissa
  +3 dB a 80 Hz (head bump), che cresce con la manopola.
- EXCITER: passa-alto 2 poli a 3 kHz -> clipper invertente Rin 10k,
  Rf 100k (+20 dB), ramo 1 diodo + 1k / 2 diodi + 1k -> passa-alto 1 polo
  a 3 kHz -> miscela che si SOMMA (non sostituisce).
- CLASSE A: un NPN a emettitore comune (classe 2N3904), Rc 3,3k, Re 100
  in serie + 900 bypassata, ingresso attenuato x 0,4 sopra la
  polarizzazione (attenuazione 0,4, non 1/10); uscita dal collettore AC-coupled nel sommatore, kc a
  pari livello RMS al nominale (1 kHz). Satura verso il basso (Vce sat) e
  verso l'alto (interdizione).

Livelli in volt del dominio interno, come Saturatori in fiveway.py.
"""

import math

import fiveway as fw

# --- filtri lineari del 1o ordine TPT ---


class Uno:
    """Polo singolo TPT: restituisce (lp, hp)."""

    def __init__(self, f, fs, s0=0.0):
        self.g = math.tan(math.pi * f / fs)
        self.s = s0

    def passo(self, x):
        v = (x - self.s) * self.g / (1 + self.g)
        lp = v + self.s
        self.s = lp + v
        return lp, x - lp


# ---- COMPLETO ----
EN_FZ = 1500.0
EN_FP = 5000.0
HB_F = 80.0
HB_Q = 1.0
HB_A = 10 ** (3 / 20) - 1


class Completo:
    def __init__(self, fs):
        self.fs = fs
        self.pre = Uno(EN_FP, fs)
        self.de = Uno(EN_FZ, fs)
        self.hb = fw.Svf()
        self.g_hb = fw.g_di(HB_F, fs)
        self.vs2, self.idd, vd = fw.jfet_riposo()
        self.vc = vd
        self.k_cb = 1 / (fs * fw.J_CB)
        self.k_c = 1 / (fs * 10e-6 * fw.J_RTS)

    def passo(self, y1):
        lp, hp = self.pre.passo(y1)
        u = lp + EN_FP / EN_FZ * hp                     # enfasi
        self.idd, vd = fw.jfet_passo(u, self.vs2, self.vc, self.idd)
        vtac = vd - self.vc
        self.vs2 += self.k_cb * (self.idd - self.vs2 / fw.J_RSB)
        self.vc += self.k_c * vtac
        w = -fw.KT * vtac
        lp, hp = self.de.passo(w)
        w = lp + EN_FZ / EN_FP * hp                     # de-enfasi
        bp = self.hb.passo(w, self.g_hb, 1 / HB_Q)[1]
        w = w + HB_A * bp / HB_Q                        # head bump
        return w - y1


# ---- generico: corrente in un ramo diodi + R (Newton dall'alto) ----

def diodo_r(v, r, nvt, iss=fw.D_IS, passi=fw.NEWTON):
    """Corrente i >= 0 con v = nvt ln(1 + i/Is) + r i."""
    if v <= 0:
        return 0.0
    vd = min(v, nvt * math.log(1 + v / (r * iss)))
    for _ in range(passi):
        ex = math.exp(vd / nvt)
        f = vd + r * iss * (ex - 1) - v
        df = 1 + r * iss * ex / nvt
        vd = vd - f / df
    return iss * (math.exp(vd / nvt) - 1)


def clipper(i_in, rf, ra, na, rb, nb):
    """Clipper invertente con due rami di diodi: |uscita| con il segno
    dell'ingresso (come clipper_growl, generalizzato)."""
    a = abs(i_in)
    rr, nv = (ra, na) if i_in >= 0 else (rb, nb)
    vd = nv * math.log(1 + a / fw.D_IS)
    for _ in range(fw.NEWTON):
        ex = math.exp(vd / nv)
        f = fw.D_IS * (ex - 1) * (1 + rr / rf) + vd / rf - a
        df = fw.D_IS * ex / nv * (1 + rr / rf) + 1 / rf
        vd = vd - f / df
    i = fw.D_IS * (math.exp(vd / nv) - 1)
    return rf * (a - i) * (1 if i_in >= 0 else -1)


# ---- EXCITER ----
EX_F = 3000.0
EX_RIN = 10e3
EX_RF = 100e3
EX_RA = 1000.0 + fw.D_RS
EX_RB = 1000.0 + 2 * fw.D_RS
EX_NA = fw.D_N * fw.VT27
EX_NB = 2 * fw.D_N * fw.VT27
EX_K = 0.30509                  # +3 dB su 5 kHz a -16 dBu, fine corsa (taratura_alt)


class Exciter:
    def __init__(self, fs):
        self.hp = fw.Svf()
        self.g = fw.g_di(EX_F, fs)
        self.hp2 = Uno(EX_F, fs)

    def passo(self, y1):
        h = self.hp.passo(y1, self.g, 1 / fw.Q_BW)[2]
        e = clipper(h / EX_RIN, EX_RF, EX_RA, EX_NA, EX_RB, EX_NB)
        return EX_K * self.hp2.passo(e)[1]


# ---- CLASSE A (NPN) ----
B_IS = 6.734e-15
B_N = 1.0
B_VAF = 74.03
B_VCC = 18.0
B_RC = 3300.0
B_REU = 100.0
B_REB = 900.0
B_CE = 2200e-6
B_VB = 2.65                     # partitore di base
B_ATT = 0.4                     # ingresso attenuato: 0,4 = THD come il NASTRO OGGI sul mix
B_VSAT = 0.15
B_K = 0.0895                    # pari livello RMS al nominale, 1 kHz (taratura_alt)
B_RTS = 10e3 / B_K


B_BF = 416.4
B_IKF = 66.78e-3
B_W = 0.05                      # morbidezza del ginocchio di saturazione, volt


def bjt_ic(vb, ve2, vcap, rts, passi=6):
    """NPN, Gummel-Poon ridotto (modello 2N3904 di LTspice): alta
    iniezione (IKF) ed Early (VAF) dentro la giunzione, corrente di base;
    Newton su Vbe con Reu. Restituisce (Ic, Vc, Ie)."""
    vt = B_N * fw.VT27
    rp = B_RC * rts / (B_RC + rts)
    vth = rp * (B_VCC / B_RC + vcap / rts)
    vbe = 0.66
    vc = vth - rp * 2e-3
    ic = 2e-3
    for _ in range(passi):
        ex = math.exp(vbe / vt)
        q1 = 1 / (1 - (vb - vc) / B_VAF)
        q2 = B_IS * (ex - 1) / B_IKF
        qb = 0.5 * q1 * (1 + math.sqrt(1 + 4 * q2))
        ic = B_IS * (ex - 1) / qb
        ie = ic * (1 + 1 / B_BF)
        f = vbe + B_REU * ie + ve2 - vb
        df = 1 + B_REU * ie / vt / math.sqrt(1 + 4 * q2)
        vbe = min(max(vbe - f / df, 0.3), 0.9)
        # Early solo in zona attiva: Vc non sotto Ve + VSAT
        vc = max(vth - rp * ic, ve2 + B_REU * ie + B_VSAT)
    # saturazione: la base impone ancora Ie; il collettore non scende sotto
    # Ve1 + VSAT e segue l'emettitore (l'eccesso arriva dalla base)
    ie = ic * (1 + 1 / B_BF)
    va = vth - rp * ic
    vs = ve2 + B_REU * ie + B_VSAT
    w = B_W
    vc = 0.5 * (va + vs + math.sqrt((va - vs) ** 2 + w * w))
    return (vth - vc) / rp, vc, ie


class ClasseA:
    def __init__(self, fs):
        self.ve2 = 0.0
        self.vcap = 0.0
        self.k_ce = 1 / (fs * B_CE)
        self.k_c = 1 / (fs * 10e-6 * B_RTS)
        # punto di lavoro: iterazione smorzata
        ve2, vcap = 1.5, 10.0
        for _ in range(400):
            ic, vc, ie = bjt_ic(B_VB, ve2, vcap, B_RTS)
            ve2 += 0.2 * (B_REB * ie - ve2)
            vcap = vc
        self.ve2, self.vcap = ve2, vcap

    def passo(self, y1):
        ic, vc, ie = bjt_ic(B_VB + B_ATT * y1, self.ve2, self.vcap, B_RTS)
        vtac = vc - self.vcap
        self.ve2 += self.k_ce * (ie - self.ve2 / B_REB)
        self.vcap += self.k_c * vtac
        return -B_K * vtac - y1


# ---- LIBERO (Filippo, 2026-10-15: «metti anche nastro con scelta libero») ----
# Il NASTRO di oggi senza la dec. 99, come il GROWL LIBERO: uno stadio di
# spinta (op-amp non invertente, un tratto del pot doppio) davanti alla
# 10k del gate, 0 -> +12 dB lineare in dB con la rotazione. Con +12 dB i
# picchi +10 dBu interni arrivano a 13,9 V: sotto il rail (16 V). Il gate
# del JFET va in conduzione (diodo gate-source, Is 10f di NJ310) e si
# appoggia sulla source: il lato positivo si schiaccia sulla 10k, quello
# negativo va in interdizione. Drain caricato come oggi (10k/KT); il
# sommatore ha Rto = Rtl = 10k * kl / KT: dl = -kl * vtac - y1. kl tarato a
# +3 dB a fine corsa sul mix di Filippo (0 dBu interni, 1 kHz).
NL_GMAX_DB = 12.0
NL_K = 0.1977                   # +3 dB a regime sul mix di Filippo, fine corsa (taratura_alt)
NL_RG = 10e3
NL_IS = 10e-15
NL_RAIL = 16.0
NL_PASSI_G = 4


def gate_v(vin, vs):
    """Tensione di gate: vin dietro 10k, diodo gate-source verso vs.
    Newton dall'alto (la partenza sta sempre a destra della radice)."""
    vt = fw.VT27
    vg = vs + vt * math.log(1 + max(vin - vs, 0.0) / (NL_RG * NL_IS))
    for _ in range(NL_PASSI_G):
        ex = math.exp((vg - vs) / vt)
        f = vg + NL_RG * NL_IS * (ex - 1) - vin
        df = 1 + NL_RG * NL_IS * ex / vt
        vg = vg - f / df
    return vg


class Libero:
    def __init__(self, fs):
        self.vs2, self.idd, vd = fw.jfet_riposo()
        self.vc = vd
        self.ig = 0.0
        self.k_cb = 1 / (fs * fw.J_CB)
        self.k_c = 1 / (fs * 10e-6 * fw.J_RTS)
        self.gn = 1.0           # spinta (fattore), la scrive Saturatori

    def passo(self, y1):
        vin = min(max(self.gn * y1, -NL_RAIL), NL_RAIL)
        idd, ig = self.idd, self.ig
        for _ in range(fw.NEWTON):
            vg = gate_v(vin, self.vs2 + fw.J_RSU * (idd + ig))
            ig = (vin - vg) / NL_RG
            idd, vd = fw.jfet_passo(vg, self.vs2 + fw.J_RSU * ig,
                                    self.vc, idd)
        self.idd, self.ig = idd, ig
        vtac = vd - self.vc
        self.vs2 += self.k_cb * (idd + ig - self.vs2 / fw.J_RSB)
        self.vc += self.k_c * vtac
        return -NL_K * vtac - y1
