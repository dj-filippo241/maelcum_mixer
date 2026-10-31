"""Genera il dispositivo MC-CHANNEL (prototipo Max P0).

Uso:  python3 proto-max/coefficienti/genera.py [--semplice]
Scrive in proto-max/:
  MC-CHANNEL.genexpr  codice gen~ (si legge e si confronta)
  MC-CHANNEL.maxpat   patch Max (riserva: si apre e si copia in un dispositivo)
  MC-CHANNEL.amxd     dispositivo Max for Live pronto (doppio clic o trascina in Live)
Con --semplice scrive MC-CHANNEL-S: le scelte d'ascolto di Filippo
(2026-10-21) fissate, senza selettori: INCROCI C (dec. 152, era A), CURVA PIONEER, ISOLATOR.

I numeri vengono da canale.py. Il codice gen~ usa solo assegnazioni,
peek/poke e due funzioni senza stato proprio: cosi prova_gen.py lo traduce
in Python e lo fa suonare (verifica nel tempo, non solo sulla carta).
"""

import json
import math
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(__file__))
import canale  # noqa: E402
import djm  # noqa: E402

QUI = os.path.dirname(os.path.abspath(__file__))
USCITA = os.path.dirname(QUI)
NOME = "MC-CHANNEL"

# (nome del Param gen~, nome in Live, valore iniziale in %)
MANOPOLE = [
    ("gain", "GAIN", 50.0),
    ("low", "LOW", 50.0),
    ("lowmid", "LOW-MID", 50.0),
    ("midhigh", "MID-HIGH", 50.0),
    ("high", "HIGH", 50.0),
]
FADER = ("fader", "FADER", 100.0)
# varianti di incroci nel selettore (B scartata all'ascolto, dec. 114)
VARIANTI = ["A", "C", "D", "E", "G"]
SELETTORE = ("incroci", "INCROCI",
             ["A 500", "C 350", "D 700", "A 400", "A 450"])
CURVA = ("curva", "CURVA", ["LINEARE", "PIONEER"])
# B5 (Filippo 2026-10-15): EQ in serie archiviato come opzione d'ascolto
# 2026-10-31 (Filippo): SERIE ridisegnato sull'EQ del Xone:92 (xone.py),
# poi XONE sostituito dai due modi DJM-900NXS (djm.py): fedele e spinto
EQTIPO = ("eqtipo", "EQ TIPO", ["ISOLATOR", "DJM -26", "DJM SPINTO -40"])
BANDE = ["low", "lowmid", "midhigh", "high"]
# sotto questo peso un blocco non si calcola (-100 dB: inudibile)
SOGLIA_ON = 1e-5
# versione semplice (Filippo 2026-10-21): scelte fissate, niente selettori
SEMPLICE = False
SCELTA_INCROCI = "C"             # 2026-10-31, dec. 152 (era A)


# ---------------------------------------------------------------- gen~ ---

class Codice:
    def __init__(self):
        self.righe = []
        self.n_st = 0   # stati dei biquad (2 per filtro)
        self.n_hb = 0   # stati degli allpass dei halfband (2 per sezione)
        self.hb_base = {}

    def r(self, s=""):
        self.righe.append(s)

    def bq(self, uscita, ingresso, tipo, c):
        """Una sezione biquad; c = prefisso dei coefficienti dell'incrocio."""
        i = self.n_st
        self.n_st += 2
        if tipo == "lp":
            args = f"{c}_lb, 2 * {c}_lb, {c}_lb, {c}_a1, {c}_a2"
        elif tipo == "hp":
            args = f"{c}_n, -2 * {c}_n, {c}_n, {c}_a1, {c}_a2"
        else:
            args = f"{c}_a2, {c}_a1, 1, {c}_a1, {c}_a2"
        self.r(f"{uscita} = bq(st, {i}, {ingresso}, {args});")

    def cammino(self, var, coefs, pari, base):
        """Un ramo del halfband polifase: coefficienti pari o dispari."""
        for idx, cf in enumerate(coefs):
            if idx % 2 == (0 if pari else 1):
                self.r(f"{var} = ap(hb, {base + 2 * idx}, {var}, {cf!r});")

    def stato_hb(self, chiave, stadio):
        """Un solo stato per (lato, stadio, verso): le chiamate in sequenza
        sullo stesso stadio devono condividere la memoria degli allpass."""
        if chiave not in self.hb_base:
            self.hb_base[chiave] = self.n_hb
            self.n_hb += 2 * canale.HALFBAND[stadio][0]
        return self.hb_base[chiave]

    def su(self, x, a, b, stadio, chiave):
        """Su 2x: da x escono a (primo nel tempo) e b."""
        coefs = canale.coef_halfband(*canale.HALFBAND[stadio])
        base = self.stato_hb(chiave, stadio)
        self.r(f"{a} = {x};")
        self.r(f"{b} = {x};")
        self.cammino(a, coefs, True, base)
        self.cammino(b, coefs, False, base)

    def giu(self, y, a, b, stadio, chiave):
        """Giu 2x: da a (primo nel tempo) e b esce y."""
        coefs = canale.coef_halfband(*canale.HALFBAND[stadio])
        base = self.stato_hb(chiave, stadio)
        self.r(f"d0 = {b};")
        self.r(f"d1 = {a};")
        self.cammino("d0", coefs, True, base)
        self.cammino("d1", coefs, False, base)
        self.r(f"{y} = 0.5 * (d0 + d1);")


def emetti_djm(g):
    """Coefficienti degli EQ DJM (djm.py): scaffali RBJ S = 1, campana a 1 kHz."""
    r = g.r
    r("// EQ DJM (B5, 2026-10-31, djm.py): sul modello del DJM-900NXS")
    r("// (LOW 70 Hz, MID 1 kHz, HI 13 kHz; -26..+6 dB). LOW = scaffale basso,")
    r("// LOW-MID = campana 1 kHz, HIGH = scaffale alto; MID-HIGH non agisce.")
    r("// F = fondo -26 dB, uno scaffale per lato; P = fondo -40 dB, due in fila.")
    for var, v in djm.VARIANTI.items():
        fondo = 10 ** (v["fondo"] / 20)
        n = v["stadi"]
        for lato, f0, gv, s in (("l", v["f_lo"], "g_low", 1), ("h", v["f_hi"], "g_high", -1)):
            c = f"j{var}{lato}"
            r(f"{c}_A = pow(10, 20 * log10(max({gv}, {fondo!r})) / {n} / 40);")
            r(f"{c}_c = cos(2 * pi * {f0!r} / sr4);")
            r(f"{c}_ra = 2 * sqrt({c}_A) * sin(2 * pi * {f0!r} / sr4) * {math.sqrt(0.5)!r};")
            r(f"{c}_ap = {c}_A + 1;")
            r(f"{c}_am = ({s}) * ({c}_A - 1);")
            r(f"{c}_ai = 1 / ({c}_ap + {c}_am * {c}_c + {c}_ra);")
            r(f"{c}_b0 = {c}_A * ({c}_ap - {c}_am * {c}_c + {c}_ra) * {c}_ai;")
            r(f"{c}_b1 = 2 * {c}_A * ({c}_am - {c}_ap * {c}_c) * {c}_ai;")
            r(f"{c}_b2 = {c}_A * ({c}_ap - {c}_am * {c}_c - {c}_ra) * {c}_ai;")
            r(f"{c}_a1 = -2 * ({c}_am + {c}_ap * {c}_c) * {c}_ai;")
            r(f"{c}_a2 = ({c}_ap + {c}_am * {c}_c - {c}_ra) * {c}_ai;")
        c = f"j{var}m"
        r(f"{c}_A = pow(10, 20 * log10(max(g_lowmid, {fondo!r})) / 40);")
        r(f"{c}_al = sin(2 * pi * {djm.F_MID!r} / sr4) / {2 * v['q_mid']!r};")
        r(f"{c}_ai = 1 / (1 + {c}_al / {c}_A);")
        r(f"{c}_b0 = (1 + {c}_al * {c}_A) * {c}_ai;")
        r(f"{c}_a1 = -2 * cos(2 * pi * {djm.F_MID!r} / sr4) * {c}_ai;")
        r(f"{c}_b2 = (1 - {c}_al * {c}_A) * {c}_ai;")
        r(f"{c}_a2 = (1 - {c}_al / {c}_A) * {c}_ai;")


def emetti_cella(g, c, uscita, ingresso):
    """Una cella dell'EQ DJM (2 stati in st); c = prefisso dei coefficienti."""
    i = g.n_st
    g.n_st += 2
    a1 = f"{c}_a1"
    b1 = a1 if c.endswith("m") else f"{c}_b1"
    g.r(f"{uscita} = bq(st, {i}, {ingresso}, {c}_b0, {b1}, {c}_b2, {a1}, {c}_a2);")


def genexpr():
    g = Codice()
    r = g.r
    r(f"// {NOME} - prototipo Max P0 del canale maelcum_mixer.")
    r("// GENERATO da proto-max/coefficienti/genera.py: non modificare a mano.")
    r("// GAIN -inf..0..+10 dB, isolator a 4 bande (0..+6 dB, silenzio a")
    r("// fondo corsa), fader. Banca a 4x della frequenza di campionamento.")
    r()
    r("// biquad in forma trasposta II; stato in m[i], m[i+1]")
    r("bq(m, i, x, b0, b1, b2, a1, a2) {")
    r("\ty = b0 * x + peek(m, i);")
    r("\tpoke(m, b1 * x - a1 * y + peek(m, i + 1), i);")
    r("\tpoke(m, b2 * x - a2 * y, i + 1);")
    r("\treturn y;")
    r("}")
    r()
    r("// allpass del 1o ordine del halfband; stato in m[i] (x), m[i+1] (y)")
    r("ap(m, i, x, c) {")
    r("\ty = c * (x - peek(m, i + 1)) + peek(m, i);")
    r("\tpoke(m, x, i);")
    r("\tpoke(m, y, i + 1);")
    r("\treturn y;")
    r("}")
    r()
    for nome, _, ini in MANOPOLE + [FADER]:
        r(f"Param {nome}({ini}, min=0, max=100);")
    if not SEMPLICE:
        r(f"Param {SELETTORE[0]}(0, min=0, max={len(VARIANTI) - 1});")
        r(f"Param {CURVA[0]}(0, min=0, max=1);")
        r(f"Param {EQTIPO[0]}(0, min=0, max={len(EQTIPO[2]) - 1});")
    pos_data = len(g.righe)
    r("@@DATA@@")
    for nome, _, ini in MANOPOLE + [FADER]:
        r(f"History s_{nome}({ini});")
    if not SEMPLICE:
        r("History s_x(0);")
        r("History s_c(0);")
        r("History s_t(0);")
    r()
    r("// manopole lisciate: 10 ms (selettore 20 ms, dissolvenza A/B)")
    r("t10 = exp(-1 / (0.010 * samplerate));")
    r("t20 = exp(-1 / (0.020 * samplerate));")
    for nome, _, _ in MANOPOLE + [FADER]:
        r(f"s_{nome} = {nome} + t10 * (s_{nome} - {nome});")
    if not SEMPLICE:
        r(f"s_x = {SELETTORE[0]} + t20 * (s_x - {SELETTORE[0]});")
        r(f"s_c = {CURVA[0]} + t20 * (s_c - {CURVA[0]});")
        r(f"s_t = {EQTIPO[0]} + t20 * (s_t - {EQTIPO[0]});")
    r()
    r("// GAIN: fondo corsa muto, meta CCW -100..0 dB, meta CW 0..+10 dB")
    r("tg = s_gain / 100;")
    r("g_gain = pow(10, min(200 * tg - 100, 20 * tg - 10) / 20) * (tg > 0);")
    r("// bande: pot lineare x2, oppure curva Pioneer ideale (docs/09 §7):")
    r("// taglio (2 theta)^1,5, boost uguale; a fondo corsa il contatto da silenzio")
    for b in BANDE:
        r(f"x_{b} = 2 * s_{b} / 100;")
        if SEMPLICE:
            r(f"g_{b} = (pow(min(x_{b}, 1), {canale.ESP_PIONEER!r})"
              f" + max(x_{b} - 1, 0)) * max({b} > 0, s_{b} > 0.001);")
            continue
        r(f"g_{b} = ((1 - s_c) * x_{b} + s_c * (pow(min(x_{b}, 1), "
          f"{canale.ESP_PIONEER!r}) + max(x_{b} - 1, 0)))"
          f" * max({b} > 0, s_{b} > 0.001);")
    r("// fader [PROVVISORIO]: curva quadratica, -12 dB a meta corsa")
    r("tf = s_fader / 100;")
    r("g_fader = tf * tf;")
    r()
    r("// coefficienti degli incroci (bilineare con prewarp)")
    r("// LR4: Q 0,7071 due volte; LR2: Q 0,5 una volta")
    r("sr4 = samplerate * 4;")
    varianti = [SCELTA_INCROCI] if SEMPLICE else VARIANTI
    for chiave in varianti:
        freq, pend = canale.INCROCI[chiave], canale.PENDENZE[chiave]
        for j, (f, o) in enumerate(zip(freq, pend), 1):
            c = f"{chiave}{j}"
            inv_q = 1 / (canale.Q_LR2 if o == 2 else canale.Q_BW)
            r(f"{c}_k = tan(pi * {f!r} / sr4);")
            r(f"{c}_kk = {c}_k * {c}_k;")
            r(f"{c}_n = 1 / (1 + {c}_k * {inv_q!r} + {c}_kk);")
            r(f"{c}_a1 = 2 * ({c}_kk - 1) * {c}_n;")
            r(f"{c}_a2 = (1 - {c}_k * {inv_q!r} + {c}_kk) * {c}_n;")
            r(f"{c}_lb = {c}_kk * {c}_n;")
    r()
    if SEMPLICE:
        return genexpr_isolator(g, SCELTA_INCROCI)
    emetti_djm(g)
    r()
    # pesi delle varianti e dell'EQ in serie. Una variante con peso nullo
    # non si calcola (CPU: la traccia gira su un solo core); i suoi stati
    # si azzerano, cosi riparte pulita alla dissolvenza successiva.
    r("// pesi: dissolvenza fra varianti vicine (1 - |s_x - i|) e fra i tipi di EQ")
    for i, chiave in enumerate(VARIANTI):
        r(f"w_{chiave} = max(0, 1 - abs(s_x - {i})) * max(0, 1 - s_t);")
        r(f"on_{chiave} = w_{chiave} > {SOGLIA_ON!r};")
    for i, var in enumerate(djm.VARIANTI, 1):
        r(f"w_{var} = max(0, 1 - abs(s_t - {i}));")
        r(f"on_{var} = w_{var} > {SOGLIA_ON!r};")
    r()
    for lato, ingresso, uscita in (("L", "in1", "out1"), ("R", "in2", "out2")):
        r(f"// ===== lato {lato} =====")
        g.su(ingresso, f"{lato}_e", f"{lato}_o", 1, (lato, "su", 1))
        g.su(f"{lato}_e", f"{lato}_u0", f"{lato}_u1", 2, (lato, "su", 2))
        g.su(f"{lato}_o", f"{lato}_u2", f"{lato}_u3", 2, (lato, "su", 2))
        base_st = g.n_st
        stati = {}   # blocco -> (primo, ultimo + 1) degli stati in st
        for k in range(4):
            # i 4 sotto-campioni passano, in ordine, dagli STESSI filtri
            g.n_st = base_st
            u = f"{lato}_u{k}"
            termini = []
            for chiave in VARIANTI:
                p = f"{lato}{k}{chiave}"
                c1, c2, c3 = (f"{chiave}{j}" for j in (1, 2, 3))
                lr2 = canale.PENDENZE[chiave][0] == 2
                inizio = g.n_st
                g.r(f"{p} = 0;")
                g.r(f"if (on_{chiave}) {{")
                # LOW = LP4(f1) AP(f2) AP(f3)  (LR2: un solo LP, Q 0,5)
                g.bq(f"{p}l", u, "lp", c1)
                if not lr2:
                    g.bq(f"{p}l", f"{p}l", "lp", c1)
                g.bq(f"{p}l", f"{p}l", "ap", c2)
                g.bq(f"{p}l", f"{p}l", "ap", c3)
                # comune ai rami alti: HP4(f1)
                # (LR2: un solo HP, polarita girata: LP2 - HP2 = allpass)
                g.bq(f"{p}h1", u, "hp", c1)
                if lr2:
                    g.r(f"{p}h1 = -{p}h1;")
                else:
                    g.bq(f"{p}h1", f"{p}h1", "hp", c1)
                # LOW-MID = HP4(f1) LP4(f2) AP(f3)
                g.bq(f"{p}lm", f"{p}h1", "lp", c2)
                g.bq(f"{p}lm", f"{p}lm", "lp", c2)
                g.bq(f"{p}lm", f"{p}lm", "ap", c3)
                # comune: HP4(f1) HP4(f2)
                g.bq(f"{p}h2", f"{p}h1", "hp", c2)
                g.bq(f"{p}h2", f"{p}h2", "hp", c2)
                # MID-HIGH = ... LP4(f3); HIGH = ... HP4(f3)
                g.bq(f"{p}mh", f"{p}h2", "lp", c3)
                g.bq(f"{p}mh", f"{p}mh", "lp", c3)
                g.bq(f"{p}hi", f"{p}h2", "hp", c3)
                g.bq(f"{p}hi", f"{p}hi", "hp", c3)
                g.r(f"{p} = g_low * {p}l + g_lowmid * {p}lm"
                    f" + g_midhigh * {p}mh + g_high * {p}hi;")
                g.r("}")
                stati[chiave] = (inizio, g.n_st)
                termini.append(f"w_{chiave} * {p}")
            # EQ DJM (B5, 2026-10-31): LOW -> MID -> HIGH, scaffali ripetuti
            for var, v in djm.VARIANTI.items():
                q = f"{lato}{k}j{var}"
                inizio = g.n_st
                g.r(f"{q} = 0;")
                g.r(f"if (on_{var}) {{")
                g.r(f"{q} = {u};")
                for _ in range(v["stadi"]):
                    emetti_cella(g, f"j{var}l", q, q)
                emetti_cella(g, f"j{var}m", q, q)
                for _ in range(v["stadi"]):
                    emetti_cella(g, f"j{var}h", q, q)
                g.r("}")
                stati[var] = (inizio, g.n_st)
                termini.append(f"w_{var} * {q}")
            g.r(f"{lato}_y{k} = " + " + ".join(termini) + ";")
        # stati dei blocchi spenti a zero: ripartono puliti
        for blocco, (da, a) in stati.items():
            g.r(f"if (on_{blocco} == 0) {{")
            for j in range(da, a):
                g.r(f"poke(st, 0, {j});")
            g.r("}")
        g.giu(f"{lato}_v0", f"{lato}_y0", f"{lato}_y1", 2, (lato, "giu", 2))
        g.giu(f"{lato}_v1", f"{lato}_y2", f"{lato}_y3", 2, (lato, "giu", 2))
        g.giu(f"{lato}_w", f"{lato}_v0", f"{lato}_v1", 1, (lato, "giu", 1))
        r(f"{lato}_out = g_gain * g_fader * {lato}_w;")
        r()
    protezione(g)
    g.righe[pos_data] = (f"Data st({g.n_st});\nData hb({g.n_hb});")
    return "\n".join(g.righe) + "\n"


def protezione(g):
    """Solo prototipo (2026-10-31): un campione non valido (NaN, infinito o
    oltre +36 dBFS) azzera tutti gli stati ed esce silenzio. Senza, un solo
    NaN avvelena il mixer della traccia di Live (va cancellata la traccia)."""
    r = g.r
    r("// protezione del prototipo: campione non valido -> stati a zero, silenzio")
    r("bad = isnan(L_out) + isnan(R_out) + (abs(L_out) > 64) + (abs(R_out) > 64);")
    r("if (bad > 0) {")
    for j in range(g.n_st):
        r(f"poke(st, 0, {j});")
    for j in range(g.n_hb):
        r(f"poke(hb, 0, {j});")
    r("L_out = 0;")
    r("R_out = 0;")
    r("}")
    r("out1 = L_out;")
    r("out2 = R_out;")


def genexpr_isolator(g, chiave):
    """Versione semplice: una sola banca isolator, senza pesi ne blocchi."""
    r = g.r
    c1, c2, c3 = (f"{chiave}{j}" for j in (1, 2, 3))
    lr2 = canale.PENDENZE[chiave][0] == 2
    for lato, ingresso, uscita in (("L", "in1", "out1"), ("R", "in2", "out2")):
        r(f"// ===== lato {lato} =====")
        g.su(ingresso, f"{lato}_e", f"{lato}_o", 1, (lato, "su", 1))
        g.su(f"{lato}_e", f"{lato}_u0", f"{lato}_u1", 2, (lato, "su", 2))
        g.su(f"{lato}_o", f"{lato}_u2", f"{lato}_u3", 2, (lato, "su", 2))
        base_st = g.n_st
        for k in range(4):
            # i 4 sotto-campioni passano, in ordine, dagli STESSI filtri
            g.n_st = base_st
            u = f"{lato}_u{k}"
            p = f"{lato}{k}{chiave}"
            g.bq(f"{p}l", u, "lp", c1)
            if not lr2:
                g.bq(f"{p}l", f"{p}l", "lp", c1)
            g.bq(f"{p}l", f"{p}l", "ap", c2)
            g.bq(f"{p}l", f"{p}l", "ap", c3)
            g.bq(f"{p}h1", u, "hp", c1)
            if lr2:
                g.r(f"{p}h1 = -{p}h1;")
            else:
                g.bq(f"{p}h1", f"{p}h1", "hp", c1)
            g.bq(f"{p}lm", f"{p}h1", "lp", c2)
            g.bq(f"{p}lm", f"{p}lm", "lp", c2)
            g.bq(f"{p}lm", f"{p}lm", "ap", c3)
            g.bq(f"{p}h2", f"{p}h1", "hp", c2)
            g.bq(f"{p}h2", f"{p}h2", "hp", c2)
            g.bq(f"{p}mh", f"{p}h2", "lp", c3)
            g.bq(f"{p}mh", f"{p}mh", "lp", c3)
            g.bq(f"{p}hi", f"{p}h2", "hp", c3)
            g.bq(f"{p}hi", f"{p}hi", "hp", c3)
            g.r(f"{lato}_y{k} = g_low * {p}l + g_lowmid * {p}lm"
                f" + g_midhigh * {p}mh + g_high * {p}hi;")
        g.giu(f"{lato}_v0", f"{lato}_y0", f"{lato}_y1", 2, (lato, "giu", 2))
        g.giu(f"{lato}_v1", f"{lato}_y2", f"{lato}_y3", 2, (lato, "giu", 2))
        g.giu(f"{lato}_w", f"{lato}_v0", f"{lato}_v1", 1, (lato, "giu", 1))
        r(f"{lato}_out = g_gain * g_fader * {lato}_w;")
        r()
    pos_data = g.righe.index("@@DATA@@")
    protezione(g)
    g.righe[pos_data] = (f"Data st({g.n_st});\nData hb({g.n_hb});")
    return "\n".join(g.righe) + "\n"


# ------------------------------------------------------------- patch ---

def box(id_, **kw):
    b = {"id": id_}
    b.update(kw)
    return {"box": b}


def linea(src, out, dst, inl):
    return {"patchline": {"destination": [dst, inl], "source": [src, out]}}


def patcher_gen(codice):
    """Il patcher dentro gen~: in 1, in 2, codebox, out 1, out 2."""
    boxes = [
        box("obj-1", maxclass="newobj", text="in 1", numinlets=0,
            numoutlets=1, outlettype=[""], patching_rect=[20, 20, 30, 22]),
        box("obj-2", maxclass="newobj", text="in 2", numinlets=0,
            numoutlets=1, outlettype=[""], patching_rect=[400, 20, 30, 22]),
        box("obj-3", maxclass="codebox", code=codice, numinlets=2,
            numoutlets=2, outlettype=["", ""], fontface=0,
            fontname="<Monospaced>", fontsize=12.0,
            patching_rect=[20, 60, 600, 500]),
        box("obj-4", maxclass="newobj", text="out 1", numinlets=1,
            numoutlets=0, patching_rect=[20, 580, 37, 22]),
        box("obj-5", maxclass="newobj", text="out 2", numinlets=1,
            numoutlets=0, patching_rect=[400, 580, 37, 22]),
    ]
    lines = [linea("obj-1", 0, "obj-3", 0), linea("obj-2", 0, "obj-3", 1),
             linea("obj-3", 0, "obj-4", 0), linea("obj-3", 1, "obj-5", 0)]
    return {
        "fileversion": 1,
        "appversion": {"major": 9, "minor": 0, "revision": 0,
                       "architecture": "x64", "modernui": 1},
        "classnamespace": "dsp.gen",
        "rect": [60.0, 60.0, 700.0, 640.0],
        "bglocked": 0, "openinpresentation": 0,
        "default_fontsize": 12.0, "default_fontface": 0,
        "default_fontname": "Arial",
        "gridonopen": 1, "gridsize": [15.0, 15.0], "gridsnaponopen": 1,
        "objectsnaponopen": 1, "statusbarvisible": 2, "toolbarvisible": 1,
        "boxanimatetime": 200, "enablehscroll": 1, "enablevscroll": 1,
        "devicewidth": 0.0, "description": "", "digest": "", "tags": "",
        "style": "",
        "boxes": boxes, "lines": lines,
    }


def patch(codice):
    boxes, lines, parametri = [], [], {}
    boxes.append(box("obj-in", maxclass="newobj", text="plugin~",
                     numinlets=2, numoutlets=2,
                     outlettype=["signal", "signal"],
                     patching_rect=[20, 20, 60, 22]))
    boxes.append(box("obj-gen", maxclass="newobj", text="gen~",
                     numinlets=2, numoutlets=2,
                     outlettype=["signal", "signal"],
                     patching_rect=[20, 300, 300, 22],
                     patcher=patcher_gen(codice)))
    boxes.append(box("obj-out", maxclass="newobj", text="plugout~",
                     numinlets=2, numoutlets=2,
                     outlettype=["signal", "signal"],
                     patching_rect=[20, 360, 60, 22]))
    lines += [linea("obj-in", 0, "obj-gen", 0),
              linea("obj-in", 1, "obj-gen", 1),
              linea("obj-gen", 0, "obj-out", 0),
              linea("obj-gen", 1, "obj-out", 1)]

    def comando(i, id_, nome_gen, nome_live, maxclass, rect, valueof):
        x = 100 + 90 * i
        attr = {"parameter_longname": nome_live,
                "parameter_shortname": nome_live,
                "parameter_initial_enable": 1}
        attr.update(valueof)
        extra = {"numinlets": 1}
        if maxclass == "live.tab":
            righe = 1 if len(valueof["parameter_enum"]) <= 2 else 2
            extra.update(numoutlets=3, outlettype=["", "", "float"],
                         num_lines_patching=righe,
                         num_lines_presentation=righe)
        else:
            extra.update(numoutlets=2, outlettype=["", "float"])
        boxes.append(box(id_, maxclass=maxclass, parameter_enable=1,
                         patching_rect=[x, 80, 44, 48 if maxclass ==
                                        "live.dial" else 90],
                         presentation=1, presentation_rect=rect,
                         saved_attribute_attributes={"valueof": attr},
                         varname=nome_live, **extra))
        pid = f"{id_}-pre"
        boxes.append(box(pid, maxclass="newobj", text=f"prepend {nome_gen}",
                         numinlets=1, numoutlets=1, outlettype=[""],
                         patching_rect=[x, 200, 85, 22]))
        lines.append(linea(id_, 0, pid, 0))
        lines.append(linea(pid, 0, "obj-gen", 0))
        parametri[id_] = [nome_live, nome_live, 0]

    for i, (ng, nl, ini) in enumerate(MANOPOLE):
        comando(i, f"obj-d{i}", ng, nl, "live.dial", [8 + 50 * i, 8, 44, 48],
                {"parameter_type": 0, "parameter_mmax": 100.0,
                 "parameter_initial": [ini], "parameter_unitstyle": 5})
    ng, nl, ini = FADER
    comando(5, "obj-fad", ng, nl, "live.slider", [262, 8, 40, 150],
            {"parameter_type": 0, "parameter_mmax": 100.0,
             "parameter_initial": [ini], "parameter_unitstyle": 5})
    if SEMPLICE:
        boxes.append(box("obj-nota", maxclass="live.comment", numinlets=1,
                         numoutlets=0, presentation=1,
                         presentation_rect=[8, 62, 250, 40],
                         patching_rect=[20, 440, 250, 36], linecount=3,
                         text="50% = 0 dB. Versione semplice: ISOLATOR, "
                              "INCROCI C 150d/350/3150, CURVA PIONEER."))
        return finestra(boxes, lines, parametri)
    ng, nl, voci = SELETTORE
    comando(6, "obj-sel", ng, nl, "live.tab", [8, 62, 240, 30],
            {"parameter_type": 2, "parameter_enum": voci,
             "parameter_mmax": float(len(voci) - 1),
             "parameter_initial": [0], "parameter_unitstyle": 0})
    ng, nl, voci = CURVA
    comando(7, "obj-cur", ng, nl, "live.tab", [8, 96, 240, 18],
            {"parameter_type": 2, "parameter_enum": voci,
             "parameter_mmax": float(len(voci) - 1),
             "parameter_initial": [0], "parameter_unitstyle": 0})
    ng, nl, voci = EQTIPO
    comando(8, "obj-eqt", ng, nl, "live.tab", [8, 118, 240, 18],
            {"parameter_type": 2, "parameter_enum": voci,
             "parameter_mmax": float(len(voci) - 1),
             "parameter_initial": [0], "parameter_unitstyle": 0})
    boxes.append(box("obj-nota", maxclass="live.comment", numinlets=1,
                     numoutlets=0, presentation=1,
                     presentation_rect=[8, 140, 250, 28],
                     patching_rect=[20, 440, 250, 36], linecount=2,
                     text="50% = 0 dB. DJM: LOW, LOW-MID = MID 1k, HIGH; "
                          "MID-HIGH e INCROCI solo per ISOLATOR."))
    return finestra(boxes, lines, parametri)


def finestra(boxes, lines, parametri):
    return {"patcher": {
        "fileversion": 1,
        "appversion": {"major": 9, "minor": 0, "revision": 0,
                       "architecture": "x64", "modernui": 1},
        "classnamespace": "box",
        "rect": [100.0, 100.0, 900.0, 520.0],
        "openrect": [0.0, 0.0, 0.0, 169.0],
        "bglocked": 0, "openinpresentation": 1,
        "default_fontsize": 10.0, "default_fontface": 0,
        "default_fontname": "Arial Bold",
        "gridonopen": 1, "gridsize": [8.0, 8.0], "gridsnaponopen": 1,
        "objectsnaponopen": 1, "statusbarvisible": 2, "toolbarvisible": 1,
        "boxanimatetime": 500, "enablehscroll": 1, "enablevscroll": 1,
        "devicewidth": 0.0, "description": "", "digest": "", "tags": "",
        "style": "",
        "boxes": boxes, "lines": lines,
        "parameters": parametri,
        "dependency_cache": [], "latency": 0, "autosave": 0,
    }}


def amxd(dati_json):
    """Contenitore .amxd: 'ampf', tipo 'aaaa' (audio effect), meta, ptch."""
    corpo = dati_json.encode("utf-8") + b"\x00"
    return (b"ampf" + struct.pack("<I", 4) + b"aaaa"
            + b"meta" + struct.pack("<I", 4) + b"\x00\x00\x00\x00"
            + b"ptch" + struct.pack("<I", len(corpo)) + corpo)


def main():
    global SEMPLICE, NOME
    if "--semplice" in sys.argv[1:]:
        SEMPLICE, NOME = True, NOME + "-S"
    codice = genexpr()
    with open(os.path.join(USCITA, f"{NOME}.genexpr"), "w") as f:
        f.write(codice)
    p = patch(codice)
    p["patcher"]["project"] = {
        "version": 1, "amxdtype": 1633771873, "readonly": 0,
        "devpathtype": 0, "devpath": ".", "contents": {"patchers": {}},
        "layout": {}, "searchpath": {}, "detailsvisible": 0,
        "autoorganize": 1, "hideprojectwindow": 1, "showdependencies": 1,
        "autolocalize": 0, "sortmode": 0, "viewmode": 0,
    }
    testo = json.dumps(p, indent="\t")
    with open(os.path.join(USCITA, f"{NOME}.maxpat"), "w") as f:
        f.write(testo)
    with open(os.path.join(USCITA, f"{NOME}.amxd"), "wb") as f:
        f.write(amxd(testo))
    print(f"scritti {NOME}.genexpr ({codice.count(chr(10))} righe), "
          f".maxpat, .amxd in {USCITA}")


if __name__ == "__main__":
    main()
