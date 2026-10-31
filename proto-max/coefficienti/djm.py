"""Modello degli EQ DJM per MC-CHANNEL (selettore EQ TIPO, voce B5).

Filippo, 2026-10-31: «isolator ok, ma voglio un'opzione eq che tagli
tantissimo, prova con modalita djm 900 nxs al posto di xone»; poi «dammi sia
1 che 2». Sostituisce XONE (xone.py resta come archivio). Solo prototipo:
l'EQ di progetto resta l'isolator (dec. 105).

Riferimento: manuale del DJM-900NXS, caratteristica dell'EQ di canale:
HI 13 kHz, MID 1 kHz, LOW 70 Hz, ognuna -26 ... +6 dB. Pioneer non
pubblica dove partono gli scaffali ne la larghezza della campana: quei
numeri sono scelte di Claude [PROVVISORIO], da sentire.

Tre bande su quattro manopole: LOW = scaffale basso, LOW-MID = campana a
1 kHz, HIGH = scaffale alto. MID-HIGH non agisce nei modi DJM.

Due varianti:
- FEDELE: fondo -26 dB come il manuale; uno scaffale per lato, posto in
  modo che il fondo sia raggiunto a 70 Hz e a 13 kHz.
- SPINTO: fondo -40 dB; due scaffali uguali in fila per lato (pendenza
  doppia), piu larghi: il LOW toglie anche la cassa a 150 Hz.

Celle RBJ (Audio EQ Cookbook), S = 1 per gli scaffali. Law delle manopole:
quella dell'isolator (g = 2 theta, oppure curva Pioneer), poi in dB,
fermata al fondo della variante; +6 dB a fine corsa.
"""

import math

F_MID = 1000.0
VARIANTI = {
    #        scaffale LOW, scaffale HIGH, stadi per lato, Q campana, fondo dB
    "F": dict(f_lo=300.0, f_hi=3600.0, stadi=1, q_mid=0.7, fondo=-26.0),
    "P": dict(f_lo=320.0, f_hi=3000.0, stadi=2, q_mid=0.5, fondo=-40.0),
}


def g_band(theta, pioneer=False):
    """Law dell'isolator: 0 = fondo, 0,5 = 1, 1 = 2 (+6 dB)."""
    x = 2 * theta
    if pioneer:
        return min(x, 1) ** 1.5 + max(x - 1, 0)
    return x


def db_banda(g, fondo):
    return 20 * math.log10(max(g, 10 ** (fondo / 20)))


def scaffale(tipo, f0, gdb, fs):
    """Scaffale RBJ con S = 1; tipo 'lo' o 'hi'. Ritorna b0 b1 b2 a1 a2."""
    a = 10 ** (gdb / 40)
    w = 2 * math.pi * f0 / fs
    c, al = math.cos(w), math.sin(w) / 2 * math.sqrt(2)
    ra = 2 * math.sqrt(a) * al
    s = 1 if tipo == "lo" else -1
    b0 = a * ((a + 1) - s * (a - 1) * c + ra)
    b1 = 2 * s * a * ((a - 1) - s * (a + 1) * c)
    b2 = a * ((a + 1) - s * (a - 1) * c - ra)
    a0 = (a + 1) + s * (a - 1) * c + ra
    a1 = -2 * s * ((a - 1) + s * (a + 1) * c)
    a2 = (a + 1) + s * (a - 1) * c - ra
    return (b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0)


def campana(f0, q, gdb, fs):
    a = 10 ** (gdb / 40)
    w = 2 * math.pi * f0 / fs
    al = math.sin(w) / (2 * q)
    a0 = 1 + al / a
    return ((1 + al * a) / a0, -2 * math.cos(w) / a0, (1 - al * a) / a0,
            -2 * math.cos(w) / a0, (1 - al / a) / a0)


def djm_digitale(f, fs, manopole, variante, pioneer=False):
    from canale import risposta
    v = VARIANTI[variante]
    gl, glm, _gmh, gh = (g_band(t, pioneer) for t in manopole)
    n = v["stadi"]
    lo = risposta(scaffale("lo", v["f_lo"], db_banda(gl, v["fondo"]) / n, fs), f, fs)
    hi = risposta(scaffale("hi", v["f_hi"], db_banda(gh, v["fondo"]) / n, fs), f, fs)
    mid = risposta(campana(F_MID, v["q_mid"], db_banda(glm, v["fondo"]), fs), f, fs)
    return lo ** n * mid * hi ** n


def djm_os(f, fs, manopole, variante, pioneer=False):
    """Catena del gen~: halfband su, celle a 4fs, halfband giu."""
    from canale import HALFBAND, coef_halfband, risposta_halfband
    h1 = risposta_halfband(coef_halfband(*HALFBAND[1]), f, 2 * fs)
    h2 = risposta_halfband(coef_halfband(*HALFBAND[2]), f, 4 * fs)
    return h1 * h2 * djm_digitale(f, 4 * fs, manopole, variante, pioneer) * h2 * h1


def db(z):
    m = abs(z)
    return -999.0 if m == 0 else 20 * math.log10(m)


if __name__ == "__main__":
    fs = 4 * 48000
    for var in ("F", "P"):
        print(f"--- {var}: una manopola a 0 %, le altre al centro")
        print("LOW   ", " ".join(f"{f}:{db(djm_digitale(f, fs, (0, .5, .5, .5), var)):+.1f}"
                                 for f in (30, 70, 100, 150, 250, 500, 1000)))
        print("MID   ", " ".join(f"{f}:{db(djm_digitale(f, fs, (.5, 0, .5, .5), var)):+.1f}"
                                 for f in (150, 300, 500, 1000, 2000, 4000)))
        print("HIGH  ", " ".join(f"{f}:{db(djm_digitale(f, fs, (.5, .5, .5, 0), var)):+.1f}"
                                 for f in (1000, 2000, 3500, 5000, 8000, 13000)))
        print("piatto:", max(abs(db(djm_digitale(f, fs, (.5, .5, .5, .5), var)))
                             for f in (20, 100, 1000, 10000, 20000)))
        print("pos %  LOW 70  MID 1k  HIGH 13k")
        for p in (10, 25, 50, 100):
            t = p / 100
            print(f"{p:5d} {db(djm_digitale(70, fs, (t, .5, .5, .5), var)):+7.1f}"
                  f" {db(djm_digitale(1000, fs, (.5, t, .5, .5), var)):+7.1f}"
                  f" {db(djm_digitale(13000, fs, (.5, .5, .5, t), var)):+7.1f}")
