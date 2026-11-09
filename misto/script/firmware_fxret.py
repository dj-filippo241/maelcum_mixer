"""Modello del firmware del misto sul FX-RET (misto/03 §3, §4, §8 punto 2; todo 278).

Uso:
    python3 misto/script/firmware_fxret.py            prove R1-R7 (stampa le tabelle)
    python3 misto/script/firmware_fxret.py --pwl      scrive anche i PWL del DAC per LTspice
                                                      (misto/sim/pwl/) e i netlist dei gesti

Catena: manopola θ → ADC 12 bit raziometrico (rumore gaussiano) → media di 4 letture
→ inseguitore con isteresi H → law (tabella) → correzione di taratura e temperatura
→ codice del DAC 16 bit → cella CV (τ 1 ms, in LTspice) → pin EC− del VCA.

Il VCA "vero" del modello: G = −(V_pin − off_i) / (K_i · T/298,15 K), con K_i e off_i
diversi per ogni chip (dispersione del grado C, vca-trim §2). La catena DAC → cella
→ pin è affine nel codice: la taratura a due punti (0 e −40 dB) la chiude esatta,
salvo INL del DAC, errore della misura REW e errore dell'NTC. Questi tre entrano qui.

Numeri dei chip [PROVVISORIO, da verificare sul datasheet del pezzo scelto]: INL del
DAC ±4 LSB a 16 bit (classe DAC8568, ordine di grandezza); rumore dell'ADC 0,5 LSB rms
(classe MCP3208); NTC ±2 °C fra lettura e chip.
"""
import math
import os
import random
import sys

# ------------------------------------------------------------------ law (fx-module §8.3)
TH = [0, .10, .20, .325, .45, .575, .70, .775, .85, .90, .95, .975, 1]
DB = [-100, -70, -40, -30, -20, -15, -10, -7, -4, -2.5, -1, -.5, 0]


def law_reroute(t):
    t = min(max(t, 0.0), 1.0)
    for i in range(len(TH) - 1):
        if t <= TH[i + 1]:
            f = (t - TH[i]) / (TH[i + 1] - TH[i])
            return DB[i] + f * (DB[i + 1] - DB[i])
    return 0.0


def law_fader(t):
    """dec. 126: 40·log10(θ) [PROVVISORIO], fondo a −100 dB (floor del VCA)."""
    return max(-100.0, 40 * math.log10(t)) if t > 0 else -100.0


# ------------------------------------------------------------------ costanti di catena
ADC_BIT = 12
ADC_N = 2 ** ADC_BIT - 1
DAC_BIT = 16
DAC_N = 2 ** DAC_BIT - 1
VREF_DAC = 2.5
LSB_DAC = VREF_DAC / 2 ** DAC_BIT
K_NOM = 6.1e-3          # V/dB al pin a 25 °C (THAT 2181 tipico)
T0 = 298.15             # 25 °C in kelvin: la costante segue kT/q
# cella nominale: V_pin = C_CELL − A_CELL · V_dac (misto/03 §4.3; campo −0,05…+0,80 V)
A_CELL = 0.34
C_CELL = 0.80


# ------------------------------------------------------------------ hardware simulato
class Hardware:
    """Un VCA con la sua cella e il suo canale di DAC, con le tolleranze vere."""

    def __init__(self, rng):
        self.K = K_NOM * (1 + rng.uniform(-1, 1) * 0.0164)   # 6,0…6,2 mV/dB (grado C)
        self.off = rng.uniform(-2.5e-3, 2.5e-3)               # simmetria residua + offset EC
        self.a = A_CELL * (1 + rng.uniform(-1, 1) * 0.002)    # resistori 0,1 %
        self.c = C_CELL + rng.uniform(-1, 1) * 3e-3           # offset op-amp, −REF5, DAC
        self.inl_amp = rng.uniform(-1, 1) * 4                  # LSB, INL a campana
        self.inl_ph = rng.uniform(0, math.pi)

    def inl(self, code):
        x = code / DAC_N
        return self.inl_amp * (math.sin(math.pi * x) + 0.3 * math.sin(3 * math.pi * x + self.inl_ph))

    def vpin(self, code):
        return self.c - self.a * (code + self.inl(code)) * LSB_DAC

    def gain(self, code, t_c):
        g = -(self.vpin(code) - self.off) / (self.K * (t_c + 273.15) / T0)
        return min(max(g, -115.0), 40.0)                     # floor e tetto del VCA


# ------------------------------------------------------------------ firmware
class Canale:
    """Il firmware di un VCA: taratura (q, m) e calcolo del codice."""

    def __init__(self):
        # valori di fabbrica, prima della taratura: dalla cella nominale
        self.m = K_NOM / (A_CELL * LSB_DAC)   # codici per dB (G negativo → codice minore)
        self.q = C_CELL / (A_CELL * LSB_DAC)  # codice di 0 dB

    def codice(self, g_db, t_ntc):
        c = self.q + self.m * g_db * (t_ntc + 273.15) / T0
        return int(min(max(round(c), 0), DAC_N))

    def tara(self, hw, t_banco, err_rew, rng):
        """Banco: il chip porta il VCA a 0 e a −40 dB nominali, REW misura, si risolve."""
        c1, c2 = self.codice(0.0, t_banco), self.codice(-40.0, t_banco)
        g1 = hw.gain(c1, t_banco) + rng.gauss(0, err_rew)
        g2 = hw.gain(c2, t_banco) + rng.gauss(0, err_rew)
        f = (t_banco + 273.15) / T0
        # codice = q + m·G·f  →  due equazioni, due incognite
        self.m = (c1 - c2) / ((g1 - g2) * f)
        self.q = c1 - self.m * g1 * f


class Manopola:
    """ADC + media di N letture + inseguitore con isteresi (banda morta che segue la mano).
    Scelta (prove R2 e R3): N = 8 a 2 kHz per manopola, H = 2 LSB."""

    def __init__(self, rng, sigma_lsb=0.5, isteresi=2.0, media=8):
        self.rng, self.sigma, self.H, self.N = rng, sigma_lsb, isteresi, media
        self.y = None

    def leggi(self, theta):
        x = sum(min(max(round(theta * ADC_N + self.rng.gauss(0, self.sigma)), 0), ADC_N)
                for _ in range(self.N)) / float(self.N)
        if self.y is None:
            self.y = x
        elif x - self.y > self.H:
            self.y = x - self.H
        elif self.y - x > self.H:
            self.y = x + self.H
        # fondo corsa: chiuso davvero, aperto davvero
        if x <= self.H:
            self.y = 0.0
        if x >= ADC_N - self.H:
            self.y = float(ADC_N)
        return self.y / ADC_N


# ------------------------------------------------------------------ prove
def prova_r1():
    """R1: la law del firmware nei 13 punti, col DAC a 16 bit e la cella nominale."""
    ch, hw = Canale(), None
    peggio = 0.0
    for t, g in zip(TH, DB):
        code = ch.codice(law_reroute(t), 25.0)
        vp = C_CELL - A_CELL * code * LSB_DAC
        peggio = max(peggio, abs(-vp / K_NOM - g))
    return peggio


def prova_r2(rng, sigma, H, durata=20.0, f_adc=2000, media=8):
    """R2: giro lentissimo 0 → 1 in `durata` s; passo massimo del guadagno fra due scritture."""
    man, ch = Manopola(rng, sigma, H, media), Canale()
    n = int(durata * f_adc)
    g_prec, zona, medio, fuori = None, 0.0, 0.0, 0.0
    for i in range(n + 1):
        th = man.leggi(i / n)
        g = law_reroute(th)
        code = ch.codice(g, 25.0)
        gv = -(C_CELL - A_CELL * code * LSB_DAC) / K_NOM
        if g_prec is not None and gv != g_prec:
            d = abs(gv - g_prec)
            if g_prec >= -15:
                zona = max(zona, d)
            elif g_prec >= -60:
                medio = max(medio, d)
            else:
                fuori = max(fuori, d)
        g_prec = gv
    return zona, medio, fuori


def prova_r3(rng, sigma, H, secondi=10.0, f_adc=2000, media=8):
    """R3: manopola ferma in 7 posizioni; scritture del DAC dopo 1 s di assestamento."""
    scritte, escursione = 0, 0.0
    for th0 in (0.03, 0.2, 0.5, 0.575, 0.8, 0.95, 0.99):
        man, ch = Manopola(rng, sigma, H, media), Canale()
        code_prec, codes = None, []
        for i in range(int((secondi + 1) * f_adc)):
            code = ch.codice(law_reroute(man.leggi(th0)), 25.0)
            if i >= f_adc:
                if code_prec is not None and code != code_prec:
                    scritte += 1
                codes.append(code)
            code_prec = code
        escursione = max(escursione, (max(codes) - min(codes)) * A_CELL * LSB_DAC / K_NOM)
    return scritte, escursione


def coppia_tarata(rng, err_rew, t_banco=25.0):
    hl, hr = Hardware(rng), Hardware(rng)
    cl, cr = Canale(), Canale()
    cl.tara(hl, t_banco, err_rew, rng)
    cr.tara(hr, t_banco, err_rew, rng)
    return (hl, cl), (hr, cr)


def prova_r5(rng, err_rew, n=500):
    """R5: differenza L/R da 0 a −60 dB dopo la taratura, a 25 °C. Ritorna (p99, max)."""
    diffs = []
    for _ in range(n):
        (hl, cl), (hr, cr) = coppia_tarata(rng, err_rew)
        peggio = 0.0
        for g in range(0, -61, -1):
            gl = hl.gain(cl.codice(g, 25.0), 25.0)
            gr = hr.gain(cr.codice(g, 25.0), 25.0)
            peggio = max(peggio, abs(gl - gr))
        diffs.append(peggio)
    diffs.sort()
    return diffs[int(0.99 * n) - 1], diffs[-1]


def prova_r5_assoluto(rng, err_rew, n=500):
    """Errore assoluto della law dopo la taratura (0…−60 dB), il peggiore su n chip."""
    peggio = 0.0
    for _ in range(n):
        hw, ch = Hardware(rng), Canale()
        ch.tara(hw, 25.0, err_rew, rng)
        for g in range(0, -61, -1):
            peggio = max(peggio, abs(hw.gain(ch.codice(g, 25.0), 25.0) - g))
    return peggio


def prova_r6(rng, err_ntc, compensa=True, n=300):
    """R6: errore a −15 dB fra 20 e 65 °C, taratura a 25 °C, NTC con errore ±err_ntc."""
    peggio = 0.0
    for _ in range(n):
        hw, ch = Hardware(rng), Canale()
        ch.tara(hw, 25.0, 0.0, rng)
        for t in range(20, 66, 5):
            t_letta = t + rng.uniform(-err_ntc, err_ntc) if compensa else 25.0
            peggio = max(peggio, abs(hw.gain(ch.codice(-15.0, t_letta), t) + 15))
    return peggio


def prova_r7(rng, n=500):
    """R7: codice zero (DAC appena acceso) → guadagno del VCA, a 20 e 65 °C."""
    peggio = -200.0
    for _ in range(n):
        hw = Hardware(rng)
        for t in (20, 65):
            peggio = max(peggio, hw.gain(0, t))
    return peggio


# ------------------------------------------------------------------ gesti per LTspice
def gesto(nome, t):
    """θ(t) dei gesti della simulazione (s). Inizio a 5 ms per lasciar partire la cella."""
    if nome == "apre100":      # fader/reroute da chiuso ad aperto in 100 ms
        return min(max((t - 5e-3) / 0.1, 0.0), 1.0)
    if nome == "feedback50":   # spinta del feedback dub da −15 a 0 dB in 50 ms
        return 0.575 + 0.425 * min(max((t - 5e-3) / 0.05, 0.0), 1.0)
    if nome == "scatto":       # chiusura di scatto (come reroute-ramp.cir), a 12,25 ms
        return 1.0 if t < 12.25e-3 else 0.0
    raise ValueError(nome)


def v_dac_ideale(th):
    """Tensione di DAC della cella continua (θ → law → codice reale, senza gradini)."""
    return (C_CELL + law_reroute(th) * K_NOM) / A_CELL


def pwl_firmware(nome, modo, durata, rng):
    """Uscita del DAC nel tempo, come la scrive il firmware.
    modo: 'zoh1k' (ADC e DAC a 1 kHz), 'zoh8k' (ADC e DAC a 8 kHz),
          'int8k' (ADC a 2 kHz, DAC a 8 kHz con interpolazione lineare: 03 §4.3)."""
    f_adc, f_dac = {"zoh1k": (1000, 1000), "zoh8k": (8000, 8000), "int8k": (2000, 8000)}[modo]
    man, ch = Manopola(rng), Canale()
    k = f_dac // f_adc
    punti, v_prec = [], None
    prec = ch.codice(law_reroute(man.leggi(gesto(nome, 0.0))), 25.0)
    n_adc = int(durata * f_adc)
    for i in range(n_adc):
        t_adc = i / f_adc
        nuovo = ch.codice(law_reroute(man.leggi(gesto(nome, t_adc))), 25.0)
        for j in range(k):
            t = t_adc + j / f_dac
            code = round(prec + (nuovo - prec) * (j + 1) / k) if modo == "int8k" else nuovo
            v = code * LSB_DAC
            if v != v_prec:
                if punti:
                    punti.append((t, v_prec))
                punti.append((t + 1e-7, v))
                v_prec = v
        prec = nuovo
    return punti


def scrivi_pwl(cartella, rng):
    os.makedirs(os.path.join(cartella, "pwl"), exist_ok=True)
    durate = {"apre100": 0.13, "feedback50": 0.08, "scatto": 0.025}
    for nome, d in durate.items():
        ideale = [(0.0, v_dac_ideale(gesto(nome, 0.0)))]
        passo = 1e-5
        for i in range(1, int(d / passo) + 1):
            t = i * passo
            if nome == "scatto" and ideale[-1][0] < 12.25e-3 <= t:
                ideale.append((12.25e-3 - 1e-8, v_dac_ideale(1.0)))
                ideale.append((12.26e-3, v_dac_ideale(0.0)))
            if t > ideale[-1][0] + 1e-9:
                ideale.append((t, v_dac_ideale(gesto(nome, t))))
        serie = {"ideale": ideale}
        for modo in ("zoh1k", "zoh8k", "int8k"):
            serie[modo] = pwl_firmware(nome, modo, d, rng)
        for modo, pts in serie.items():
            with open(os.path.join(cartella, "pwl", "%s-%s.txt" % (nome, modo)), "w") as f:
                for t, v in pts:
                    f.write("%.7e %.7e\n" % (t, v))


def main():
    rng = random.Random(278)
    print("Modello del firmware FX-RET (misto/03), seme 278\n")
    print("R1  law del firmware nei 13 punti (DAC 16 bit): errore massimo %.4f dB" % prova_r1())
    print("\nR2  passo del guadagno, giro lentissimo (20 s), ADC 12 bit a 2 kHz")
    print("    media  rumore ADC  isteresi H   0…−15 dB    −15…−60 dB   sotto −60 dB")
    for n in (4, 8, 16):
        for s in (0.5, 1.0):
            z, m, f = prova_r2(random.Random(1), s, 2.0, media=n)
            print("    %2d     %.1f LSB     %.1f LSB      %.4f dB   %.4f dB    %.4f dB" % (n, s, 2.0, z, m, f))
    print("\nR3  manopola ferma, 7 posizioni × 10 s: scritture del DAC e oscillazione")
    print("    media  rumore ADC  isteresi H   scritture   oscillazione del guadagno")
    for n in (4, 8):
        for s in (0.5, 1.0, 2.0):
            for h in (1.0, 2.0, 3.0):
                w, e = prova_r3(random.Random(2), s, h, media=n)
                print("    %2d     %.1f LSB     %.1f LSB      %5d       %.4f dB" % (n, s, h, w, e))
    print("\nR5  coppia L/R dopo la taratura a due punti (0 e −40 dB), 0…−60 dB, 500 coppie")
    print("    errore REW   diff. L/R p99   diff. L/R max   errore assoluto max")
    for e in (0.0, 0.01, 0.03):
        p99, mx = prova_r5(random.Random(3), e)
        ab = prova_r5_assoluto(random.Random(4), e)
        print("    %.2f dB      %.3f dB        %.3f dB        %.3f dB" % (e, p99, mx, ab))
    print("\nR6  errore a −15 dB, telaio 20…65 °C, taratura a 25 °C")
    print("    senza compensazione: %.2f dB" % prova_r6(random.Random(5), 0, compensa=False))
    for e in (1.0, 2.0, 4.0):
        print("    NTC ±%.0f °C:          %.3f dB" % (e, prova_r6(random.Random(5), e)))
    print("\nR7  codice zero (DAC appena acceso), peggior chip a 20 e 65 °C: %.1f dB" % prova_r7(random.Random(6)))
    print("\nR4  ritardo del firmware: lettura ADC 0,5 ms (2 kHz) + interpolazione 0,5 ms = 1,0 ms;"
          "\n    la cella aggiunge τ 1 ms: misura in LTspice (misto/sim/RISULTATI-cella-cv.md).")
    if "--pwl" in sys.argv:
        cartella = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sim")
        scrivi_pwl(os.path.normpath(cartella), random.Random(7))
        print("\nPWL scritti in misto/sim/pwl/")


if __name__ == "__main__":
    main()
