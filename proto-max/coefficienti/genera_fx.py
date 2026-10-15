"""Genera i dispositivi di P3: MC-SEND, MC-BUS, MC-RET, MC-MASTER.

Uso:  python3 proto-max/coefficienti/genera_fx.py
Scrive in proto-max/: MC-SEND, MC-RET, MC-MASTER (.genexpr, .maxpat,
.amxd) e MC-BUS (.maxpat, .amxd: solo oggetti Max, niente gen~).

I numeri vengono da fx.py. Topologia e nomi dei collegamenti nel
docstring di fx.py: le mandate e i reroute vanno ai bus con send~
mcfx_b<n>L / mcfx_b<n>R; piu send~ con lo stesso nome si sommano nel
receive~ di MC-BUS.

Regole del codice gen~ (CLAUDE.md, pagate in P1/P2): funzioni con un solo
valore di ritorno; nessun nome esterno uguale a un parametro o a un
locale di funzione (controllo automatico in nomi_in_comune); d0/d1 sono
del downsampling.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import fx  # noqa: E402
import genera  # noqa: E402
from genera import Codice, box, linea, amxd  # noqa: E402

USCITA = genera.USCITA
BUS = [f"mcfx_b{n}" for n in range(1, 5)]
RD = fx.RAIL / fx.LIV           # rail in unita digitali
ASSIGN_VOCI = ["-", "ON"]


# ---------------- pezzi di codice gen~ ----------------

def funzioni_eq(r):
    r("// allpass del 1o ordine del halfband; stato in m[i] (x), m[i+1] (y)")
    r("ap(m, i, x, c) {")
    r("\ty = c * (x - peek(m, i + 1)) + peek(m, i);")
    r("\tpoke(m, x, i);")
    r("\tpoke(m, y, i + 1);")
    r("\treturn y;")
    r("}")
    r()
    r("// polo singolo TPT, uscita passa-basso; stato in m[i]")
    r("op1(m, i, x, g) {")
    r("\ts = peek(m, i);")
    r("\tv = (x - s) * g / (1 + g);")
    r("\tlo = v + s;")
    r("\tpoke(m, lo + v, i);")
    r("\treturn lo;")
    r("}")
    r()
    r("// SVF 2 poli TPT, uscita passa-alto; stato in m[i], m[i+1]; k = 1/Q")
    r("svhp(m, i, x, g, k) {")
    r("\ts1 = peek(m, i);")
    r("\ts2 = peek(m, i + 1);")
    r("\tfh = (x - (k + g) * s1 - s2) / (1 + g * (k + g));")
    r("\tfb = g * fh + s1;")
    r("\tfl = g * fb + s2;")
    r("\tpoke(m, g * fh + fb, i);")
    r("\tpoke(m, g * fb + fl, i + 1);")
    r("\treturn fh;")
    r("}")
    r()


def lisci(r, nomi, ini):
    for nome in nomi:
        r(f"History s_{nome}({ini.get(nome, 50)});")
    r("t10 = exp(-1 / (0.010 * samplerate));")
    for nome in nomi:
        r(f"s_{nome} = {nome} + t10 * (s_{nome} - {nome});")


def tratti(var, t, punti):
    """Espressione gen~ dell'interpolazione lineare su punti (t, dB)."""
    termini = []
    for j, ((t0, v0), (t1, v1)) in enumerate(zip(punti, punti[1:])):
        cond = []
        if j > 0:
            cond.append(f"({t} >= {t0!r})")
        if j < len(punti) - 2:
            cond.append(f"({t} < {t1!r})")
        tratto = f"({v0!r} + {(v1 - v0) / (t1 - t0)!r} * ({t} - {t0!r}))"
        termini.append(" * ".join(cond + [tratto]))
    return f"{var} = " + " + ".join(termini) + ";"


def coefficienti_eq(r, tl, th):
    """Law dell'EQ2 e coefficienti delle celle (fx.low_sezioni, _k_high)."""
    r("// EQ2 LOW: dB voluti -> posizione x del pot (fx.low_x)")
    taglio = tratti("x", tl, fx.LOW_PUNTI)[len("x = "):-1]
    r(f"ldb = ({tl} >= 0.5) * {fx.EQ_BOOST_DB / 0.5!r} * ({tl} - 0.5)"
      f" + ({tl} < 0.5) * ({taglio});")
    r("lgl = pow(10, ldb / 20);")
    a = fx.R_POT / fx.R_IN
    r(f"lx = ({a + 1!r} - lgl) / ({a!r} * (lgl + 1));")
    r("// EQ2 HIGH: posizione thh del pot (fx.high_thh)")
    gin, tg, b = fx.HIGH_GIN_DB, fx.HIGH_GIN_T, fx.EQ_BOOST_DB
    r(f"hth = ({th} >= 0.5) * 0.5 * pow(10, {b / 0.5 / 20!r} * ({th} - 0.5))"
      f" + ({th} < 0.5) * ({th} >= {tg!r}) * 0.5 * pow(10,"
      f" {gin / (0.5 - tg) / 20!r} * (0.5 - {th}))"
      f" + ({th} < {tg!r}) * {0.5 * 10 ** (gin / 20) / tg!r} * {th};")
    c, r1, rm = fx.C_LOW, fx.R_IN, fx.R_MIN
    r(f"lra = {fx.R_POT!r} * lx + {rm!r};")
    r(f"lrb = {fx.R_POT!r} * (1 - lx) + {rm!r};")
    r(f"ala = {r1!r} / ({r1!r} + lrb);")
    r(f"gla = 1 / (2 * sr4 * lrb * {c!r});")
    r(f"alb = ({r1!r} + lra) / {r1!r};")
    r(f"glb = ({r1!r} + lra) / (2 * sr4 * {r1!r} * lra * {c!r});")
    r(f"lgk = ({r1!r} + lrb) / ({r1!r} + lra);")
    r(f"hr1 = {fx.R_THH!r} * hth + {rm!r};")
    r(f"hr2 = {fx.R_THH!r} * (1 - hth) + {rm!r};")
    r(f"hk = (1 / hr2 - 1 / hr1) / (1 / hr1 + 1 / hr2 + {1 / fx.R_SUM!r});")
    w0, q = fx.hp2_w0_q()
    r(f"ghp = tan({w0 / 2!r} / sr4);")
    r(f"khp = {1 / q!r};")


def eq_campione(r, var, sa, sv):
    """Un campione a 4x dell'EQ2 su var (stati: sa[sa], sa[sa+1], sv[sv..])."""
    r(f"{var} = ala * {var} + (1 - ala) * op1(sa, {sa}, {var}, gla);")
    r(f"{var} = alb * {var} + (1 - alb) * op1(sa, {sa + 1}, {var}, glb);")
    r(f"{var} = lgk * {var};")
    r(f"{var} = {var} + hk * svhp(sv, {sv}, {var}, ghp, khp);")


def meter(r, segnale, env, lat):
    r(f"ma = {segnale} * {fx.LIV!r};")
    r(f"{env} = max(ma, mcr * {env});")
    r(f"{lat} = (ma >= {fx.CLIP_V!r}) * {fx.T_LATCH!r} + (ma < "
      f"{fx.CLIP_V!r}) * max({lat} - 1 / samplerate, 0);")


def nomi_in_comune(testo):
    pat = r"^(\w+)\(([^)]*)\)\s*\{\n(.*?)^\}"
    loc = set()
    for _, p, b in re.findall(pat, testo, re.M | re.S):
        loc |= {x.strip() for x in p.split(",")}
        loc |= set(re.findall(r"^\t(\w+)\s*=", b, re.M))
    corpo = re.sub(pat, "", testo, flags=re.M | re.S)
    est = set(re.findall(r"^(\w+)\s*=", corpo, re.M))
    est |= set(re.findall(r"^(?:Param|History|Data)\s+(\w+)", corpo, re.M))
    est.discard("d0")           # del downsampling: scritti solo da giu()
    est.discard("d1")
    return sorted(loc & est)


# ---------------- MC-SEND ----------------

SEND_DIAL = [("low", "EQ LOW", 50.0), ("high", "EQ HIGH", 50.0),
             ("level", "LEVEL", 0.0)]
SEND_TAB = [(f"as{n}", f"FX{n}") for n in range(1, 5)]


def genexpr_send():
    g = Codice()
    r = g.r
    r("// MC-SEND - prototipo Max P3 (FX-SEND, fx-send-module §2).")
    r("// GENERATO da proto-max/coefficienti/genera_fx.py: non modificare.")
    r("// L'audio del canale passa intatto (out1, out2). EQ2 -> LEVEL ->")
    r("// 4 ASSIGN (rampa 1 ms) -> out3..out10 = bus 1-4, L e R.")
    r()
    funzioni_eq(r)
    for nome, _, ini in SEND_DIAL:
        r(f"Param {nome}({ini:g}, min=0, max=100);")
    for nome, _ in SEND_TAB:
        r(f"Param {nome}(0, min=0, max=1);")
        r(f"History r_{nome}(0);")
    r("Data sv(4);")
    r("Data sa(4);")
    pos = len(g.righe)
    r("@@DATA@@")
    lisci(r, [n for n, _, _ in SEND_DIAL], {"level": 0})
    r("sr4 = samplerate * 4;")
    coefficienti_eq(r, "s_low / 100", "s_high / 100")
    r("tv = s_level / 100;")
    m = fx.TAPER_A_MID
    r(f"lev = (tv <= 0.5) * {m / 0.5!r} * tv + (tv > 0.5) * ({m!r} + "
      f"{(1 - m) / 0.5!r} * (tv - 0.5));")
    r(f"pr = 1 / ({fx.T_ASSIGN!r} * samplerate);")
    for nome, _ in SEND_TAB:
        r(f"r_{nome} = r_{nome} + min(max({nome} - r_{nome}, -pr), pr);")
    for lato, ingresso in (("L", "in1"), ("R", "in2")):
        b = 0 if lato == "L" else 2
        r(f"// ===== lato {lato} =====")
        g.su(ingresso, f"{lato}_e", f"{lato}_o", 1, (lato, "su", 1))
        g.su(f"{lato}_e", f"{lato}_u0", f"{lato}_u1", 2, (lato, "su", 2))
        g.su(f"{lato}_o", f"{lato}_u2", f"{lato}_u3", 2, (lato, "su", 2))
        for k in range(4):
            r(f"eq = {lato}_u{k};")
            eq_campione(r, "eq", b, b)
            r(f"{lato}_y{k} = eq;")
        g.giu(f"{lato}_v0", f"{lato}_y0", f"{lato}_y1", 2, (lato, "giu", 2))
        g.giu(f"{lato}_v1", f"{lato}_y2", f"{lato}_y3", 2, (lato, "giu", 2))
        g.giu(f"{lato}_w", f"{lato}_v0", f"{lato}_v1", 1, (lato, "giu", 1))
    r("out1 = in1;")
    r("out2 = in2;")
    for n, (nome, _) in enumerate(SEND_TAB):
        r(f"out{3 + 2 * n} = r_{nome} * lev * L_w;")
        r(f"out{4 + 2 * n} = r_{nome} * lev * R_w;")
    g.righe[pos] = f"Data hb({g.n_hb});"
    return "\n".join(g.righe) + "\n"


# ---------------- MC-RET ----------------

RET_DIAL = [("gain", "GAIN", 50.0), ("low", "EQ LOW", 50.0),
            ("high", "EQ HIGH", 50.0)]
RET_RR = [(f"rr{n}", f"> FX{n}") for n in range(1, 5)]


def genexpr_ret():
    g = Codice()
    r = g.r
    r("// MC-RET - prototipo Max P3 (ritorno FX, fx-module §5 e §7).")
    r("// GENERATO da proto-max/coefficienti/genera_fx.py: non modificare.")
    r("// GAIN (VCA, rail) -> EQ2 (rail) -> meter -> 4 REROUTE pre-fader.")
    r("// out1-2 al fader; out3..out10 = reroute ai bus 1-4 (L, R);")
    r("// out11 meter (1 = +24 dBu), out12 clip (latch 479 ms).")
    r()
    funzioni_eq(r)
    for nome, _, ini in RET_DIAL:
        r(f"Param {nome}({ini:g}, min=0, max=100);")
    for nome, _ in RET_RR:
        r(f"Param {nome}(0, min=0, max=100);")
        r(f"History c_{nome}(0);")
    r("History menv(0);")
    r("History mlat(0);")
    r("Data sv(4);")
    r("Data sa(4);")
    pos = len(g.righe)
    r("@@DATA@@")
    lisci(r, [n for n, _, _ in RET_DIAL], {})
    r("sr4 = samplerate * 4;")
    r("tg = s_gain / 100;")
    gm, gk, tk = fx.GAIN_MAX_DB, fx.GAIN_KNEE_DB, fx.GAIN_KNEE_T
    r(f"gnl = (tg >= 0.5) * pow(10, {gm / 0.5 / 20!r} * (tg - 0.5))"
      f" + (tg < 0.5) * (tg >= {tk!r}) * pow(10, {gk / (0.5 - tk) / 20!r}"
      f" * (0.5 - tg)) + (tg < {tk!r}) * {10 ** (gk / 20) / tk!r} * tg;")
    coefficienti_eq(r, "s_low / 100", "s_high / 100")
    r(f"// REROUTE: law a tratti della SPEC §7, CV lisciato 1 ms")
    r(f"ccr = exp(-1 / ({fx.T_REROUTE!r} * samplerate));")
    for nome, _ in RET_RR:
        r(tratti(f"q_{nome}", f"{nome} / 100", fx.REROUTE_PUNTI))
        r(f"l_{nome} = pow(10, q_{nome} / 20);")
        r(f"c_{nome} = l_{nome} + ccr * (c_{nome} - l_{nome});")
    for lato, ingresso in (("L", "in1"), ("R", "in2")):
        b = 0 if lato == "L" else 2
        r(f"// ===== lato {lato} =====")
        g.su(ingresso, f"{lato}_e", f"{lato}_o", 1, (lato, "su", 1))
        g.su(f"{lato}_e", f"{lato}_u0", f"{lato}_u1", 2, (lato, "su", 2))
        g.su(f"{lato}_o", f"{lato}_u2", f"{lato}_u3", 2, (lato, "su", 2))
        for k in range(4):
            r(f"eq = min(max(gnl * {lato}_u{k}, {-RD!r}), {RD!r});")
            eq_campione(r, "eq", b, b)
            r(f"{lato}_y{k} = min(max(eq, {-RD!r}), {RD!r});")
        g.giu(f"{lato}_v0", f"{lato}_y0", f"{lato}_y1", 2, (lato, "giu", 2))
        g.giu(f"{lato}_v1", f"{lato}_y2", f"{lato}_y3", 2, (lato, "giu", 2))
        g.giu(f"{lato}_w", f"{lato}_v0", f"{lato}_v1", 1, (lato, "giu", 1))
    r("// meter del ritorno: una barra, mono centrato (sistema-metering §1)")
    r(f"mcr = exp(-1 / ({fx.T_RILASCIO!r} * samplerate));")
    meter(r, "max(abs(L_w), abs(R_w))", "menv", "mlat")
    r("out1 = L_w;")
    r("out2 = R_w;")
    for n, (nome, _) in enumerate(RET_RR):
        r(f"out{3 + 2 * n} = c_{nome} * L_w;")
        r(f"out{4 + 2 * n} = c_{nome} * R_w;")
    r(f"out11 = menv / {fx.METER_FS!r};")
    r("out12 = mlat > 0;")
    g.righe[pos] = f"Data hb({g.n_hb});"
    return "\n".join(g.righe) + "\n"


# ---------------- MC-MASTER ----------------

def genexpr_master():
    g = Codice()
    r = g.r
    r("// MC-MASTER - prototipo Max P3 (master-out §3.2, addendum dec. 111).")
    r("// GENERATO da proto-max/coefficienti/genera_fx.py: non modificare.")
    r("// MONO (M/S, S in un VCA da 0 a -100 dB in 1 ms) -> MASTER LEVEL ->")
    r("// meter L e R (out3-4, 1 = +24 dBu) e clip (out5-6).")
    r()
    r(f"Param level({fx.MASTER_UNITY_T * 100:g}, min=0, max=100);")
    r("Param mono(0, min=0, max=1);")
    r("History mrp(0);")
    for nome in ("menl", "menr", "mlal", "mlar"):
        r(f"History {nome}(0);")
    lisci(r, ["level"], {"level": fx.MASTER_UNITY_T * 100})
    r(f"pm = 1 / ({fx.T_MONO!r} * samplerate);")
    r("mrp = mrp + min(max(mono - mrp, -pm), pm);")
    r("mgs = pow(10, -5 * mrp) * (mrp < 1);")
    r("mmid = 0.5 * (in1 + in2);")
    r("mside = 0.5 * (in1 - in2) * mgs;")
    r("tm = s_level / 100;")
    u, mx = fx.MASTER_UNITY_T, fx.MASTER_MAX_DB
    kd, kt = fx.MASTER_KNEE_DB, fx.MASTER_KNEE_T
    r(f"mgl = (tm >= {u!r}) * pow(10, {mx / (1 - u) / 20!r} * (tm - {u!r}))"
      f" + (tm < {u!r}) * (tm >= {kt!r}) * pow(10, {kd / (u - kt) / 20!r}"
      f" * ({u!r} - tm)) + (tm < {kt!r}) * {10 ** (kd / 20) / kt!r} * tm;")
    r("mol = mgl * (mmid + mside);")
    r("mor = mgl * (mmid - mside);")
    r(f"mcr = exp(-1 / ({fx.T_RILASCIO!r} * samplerate));")
    meter(r, "abs(mol)", "menl", "mlal")
    meter(r, "abs(mor)", "menr", "mlar")
    r("out1 = mol;")
    r("out2 = mor;")
    r(f"out3 = menl / {fx.METER_FS!r};")
    r(f"out4 = menr / {fx.METER_FS!r};")
    r("out5 = mlal > 0;")
    r("out6 = mlar > 0;")
    return "\n".join(g.righe) + "\n"


# ---------------- patch ----------------

def patcher_gen_n(codice, nin, nout):
    boxes = [box(f"obj-i{j}", maxclass="newobj", text=f"in {j + 1}",
                 numinlets=0, numoutlets=1, outlettype=[""],
                 patching_rect=[20 + 60 * j, 20, 30, 22]) for j in range(nin)]
    boxes.append(box("obj-cb", maxclass="codebox", code=codice,
                     numinlets=nin, numoutlets=nout,
                     outlettype=[""] * nout, fontface=0,
                     fontname="<Monospaced>", fontsize=12.0,
                     patching_rect=[20, 60, 700, 500]))
    boxes += [box(f"obj-o{j}", maxclass="newobj", text=f"out {j + 1}",
                  numinlets=1, numoutlets=0,
                  patching_rect=[20 + 55 * j, 580, 40, 22])
              for j in range(nout)]
    lines = [linea(f"obj-i{j}", 0, "obj-cb", j) for j in range(nin)]
    lines += [linea("obj-cb", j, f"obj-o{j}", 0) for j in range(nout)]
    return {
        "fileversion": 1,
        "appversion": {"major": 9, "minor": 0, "revision": 0,
                       "architecture": "x64", "modernui": 1},
        "classnamespace": "dsp.gen",
        "rect": [60.0, 60.0, 760.0, 640.0],
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


class Patch:
    def __init__(self):
        self.boxes, self.lines, self.parametri = [], [], {}
        self.n = 0
        self.boxes.append(box("obj-in", maxclass="newobj", text="plugin~",
                              numinlets=2, numoutlets=2,
                              outlettype=["signal", "signal"],
                              patching_rect=[20, 20, 60, 22]))
        self.boxes.append(box("obj-out", maxclass="newobj", text="plugout~",
                              numinlets=2, numoutlets=2,
                              outlettype=["signal", "signal"],
                              patching_rect=[20, 700, 60, 22]))

    def obj(self, id_, testo, nin, nout, rect, tipi=None):
        self.boxes.append(box(id_, maxclass="newobj", text=testo,
                              numinlets=nin, numoutlets=nout,
                              outlettype=tipi or ["signal"] * nout,
                              patching_rect=rect))

    def gen(self, codice, nout):
        self.boxes.append(box("obj-gen", maxclass="newobj", text="gen~",
                              numinlets=2, numoutlets=nout,
                              outlettype=["signal"] * nout,
                              patching_rect=[20, 400, 600, 22],
                              patcher=patcher_gen_n(codice, 2, nout)))
        self.lines += [linea("obj-in", 0, "obj-gen", 0),
                       linea("obj-in", 1, "obj-gen", 1),
                       linea("obj-gen", 0, "obj-out", 0),
                       linea("obj-gen", 1, "obj-out", 1)]

    def comando(self, nome_gen, nome_live, maxclass, rect, valueof,
                verso="obj-gen"):
        i = self.n
        self.n += 1
        id_ = f"obj-c{i}"
        x = 100 + 90 * (i % 12)
        y = 80 + 140 * (i // 12)
        attr = {"parameter_longname": nome_live,
                "parameter_shortname": nome_live,
                "parameter_initial_enable": 1}
        attr.update(valueof)
        extra = {"numinlets": 1}
        if maxclass == "live.tab":
            extra.update(numoutlets=3, outlettype=["", "", "float"],
                         num_lines_patching=1, num_lines_presentation=1)
        else:
            extra.update(numoutlets=2, outlettype=["", "float"])
        self.boxes.append(box(id_, maxclass=maxclass, parameter_enable=1,
                              patching_rect=[x, y, 44, 48],
                              presentation=1, presentation_rect=rect,
                              saved_attribute_attributes={"valueof": attr},
                              varname=nome_live, **extra))
        self.parametri[id_] = [nome_live, nome_live, 0]
        if nome_gen is not None:
            pid = f"{id_}-pre"
            self.boxes.append(box(pid, maxclass="newobj",
                                  text=f"prepend {nome_gen}", numinlets=1,
                                  numoutlets=1, outlettype=[""],
                                  patching_rect=[x, y + 60, 85, 22]))
            self.lines.append(linea(id_, 0, pid, 0))
            self.lines.append(linea(pid, 0, verso, 0))
        return id_

    def tab(self, nome_gen, nome_live, voci, ini, rect):
        return self.comando(nome_gen, nome_live, "live.tab", rect,
                            {"parameter_type": 2, "parameter_enum": voci,
                             "parameter_mmax": float(len(voci) - 1),
                             "parameter_initial": [ini],
                             "parameter_unitstyle": 0})

    def dial(self, nome_gen, nome_live, ini, rect):
        return self.comando(nome_gen, nome_live, "live.dial", rect,
                            {"parameter_type": 0, "parameter_mmax": 100.0,
                             "parameter_initial": [ini],
                             "parameter_unitstyle": 5})

    def meter(self, id_, uscita, rect, nome):
        self.boxes.append(box(id_, maxclass="live.meter~", numinlets=1,
                              numoutlets=2, outlettype=["list", "list"],
                              presentation=1, presentation_rect=rect,
                              patching_rect=[700 + 30 * len(self.boxes) % 300,
                                             480, 20, 100],
                              display_range=[-60.0, 0.0], varname=nome))
        self.lines.append(linea("obj-gen", uscita, id_, 0))

    def nota(self, testo, rect):
        self.boxes.append(box(f"obj-nota{len(self.boxes)}",
                              maxclass="live.comment", numinlets=1,
                              numoutlets=0, presentation=1,
                              presentation_rect=rect,
                              patching_rect=[20, 760, rect[2], 18],
                              text=testo))

    def json(self):
        p = {"patcher": {
            "fileversion": 1,
            "appversion": {"major": 9, "minor": 0, "revision": 0,
                           "architecture": "x64", "modernui": 1},
            "classnamespace": "box",
            "rect": [100.0, 100.0, 1200.0, 800.0],
            "openrect": [0.0, 0.0, 0.0, 169.0],
            "bglocked": 0, "openinpresentation": 1,
            "default_fontsize": 10.0, "default_fontface": 0,
            "default_fontname": "Arial Bold",
            "gridonopen": 1, "gridsize": [8.0, 8.0], "gridsnaponopen": 1,
            "objectsnaponopen": 1, "statusbarvisible": 2,
            "toolbarvisible": 1, "boxanimatetime": 500,
            "enablehscroll": 1, "enablevscroll": 1,
            "devicewidth": 0.0, "description": "", "digest": "", "tags": "",
            "style": "",
            "boxes": self.boxes, "lines": self.lines,
            "parameters": self.parametri,
            "dependency_cache": [], "latency": 0, "autosave": 0,
        }}
        p["patcher"]["project"] = {
            "version": 1, "amxdtype": 1633771873, "readonly": 0,
            "devpathtype": 0, "devpath": ".", "contents": {"patchers": {}},
            "layout": {}, "searchpath": {}, "detailsvisible": 0,
            "autoorganize": 1, "hideprojectwindow": 1, "showdependencies": 1,
            "autolocalize": 0, "sortmode": 0, "viewmode": 0,
        }
        return p


def patch_send(codice):
    p = Patch()
    p.gen(codice, 10)
    for n, b in enumerate(BUS):
        for j, lato in enumerate("LR"):
            id_ = f"obj-s{n}{lato}"
            p.obj(id_, f"send~ {b}{lato}", 1, 0, [20 + 110 * (2 * n + j),
                                                    460, 100, 22], [])
            p.lines.append(linea("obj-gen", 2 + 2 * n + j, id_, 0))
    for j, (ng, nl, ini) in enumerate(SEND_DIAL):
        p.dial(ng, nl, ini, [8 + 60 * j, 8, 54, 48])
    for j, (ng, nl) in enumerate(SEND_TAB):
        p.tab(ng, nl, ASSIGN_VOCI, 0, [8 + 46 * j, 64, 42, 18])
    p.nota("Presa post-EQ, pre-filtro, pre-fader: tra MC-CHANNEL e "
           "MC-FILTRO. L'audio del canale passa intatto.", [8, 90, 200, 40])
    return p.json()


def patch_bus():
    p = Patch()
    rd = round(RD, 6)
    for j, lato in enumerate("LR"):
        x = 20 + 200 * j
        p.obj(f"obj-r{lato}", f"receive~ {BUS[0]}{lato}", 1, 1,
              [x, 200, 110, 22])
        p.obj(f"obj-p{lato}", "+~", 2, 1, [x, 260, 40, 22])
        p.obj(f"obj-k{lato}", f"clip~ {-rd} {rd}", 3, 1, [x, 320, 120, 22])
        p.obj(f"obj-f{lato}", f"sprintf set {BUS[0][:-1]}%ld{lato}", 1, 1,
              [x, 140, 160, 22], [""])
        p.lines += [linea("obj-in", j, f"obj-p{lato}", 0),
                    linea(f"obj-r{lato}", 0, f"obj-p{lato}", 1),
                    linea(f"obj-p{lato}", 0, f"obj-k{lato}", 0),
                    linea(f"obj-k{lato}", 0, "obj-out", j),
                    linea(f"obj-f{lato}", 0, f"obj-r{lato}", 0)]
    tab = p.tab(None, "BUS", ["FX1", "FX2", "FX3", "FX4"], 0,
                [8, 8, 120, 18])
    p.obj("obj-piu", "+ 1", 2, 1, [20, 100, 40, 22], ["int"])
    p.obj("obj-dev", "live.thisdevice", 1, 3, [200, 40, 90, 22],
          ["bang", "int", "int"])
    p.lines += [linea(tab, 0, "obj-piu", 0),
                linea("obj-piu", 0, "obj-fL", 0),
                linea("obj-piu", 0, "obj-fR", 0),
                linea("obj-dev", 0, tab, 0)]
    p.nota("Primo dispositivo della traccia FX: somma delle mandate e dei "
           "reroute del bus scelto, rail +-16,5 V. Poi il tuo effetto, "
           "poi MC-RET.", [8, 32, 300, 40])
    return p.json()


def patch_ret(codice):
    p = Patch()
    p.gen(codice, 12)
    for n, b in enumerate(BUS):
        for j, lato in enumerate("LR"):
            id_ = f"obj-s{n}{lato}"
            p.obj(id_, f"send~ {b}{lato}", 1, 0, [20 + 110 * (2 * n + j),
                                                    460, 100, 22], [])
            p.lines.append(linea("obj-gen", 2 + 2 * n + j, id_, 0))
    for j, (ng, nl, ini) in enumerate(RET_DIAL):
        p.dial(ng, nl, ini, [8 + 60 * j, 8, 54, 48])
    for j, (ng, nl) in enumerate(RET_RR):
        p.dial(ng, nl, 0.0, [8 + 60 * j, 70, 54, 48])
    p.meter("obj-met", 10, [250, 8, 14, 110], "METER")
    p.meter("obj-clip", 11, [268, 8, 6, 110], "CLIP")
    p.nota("REROUTE pre-fader (law SPEC §7). Meter: 0 = +24 dBu, "
           "-24 = 0 dBu.", [8, 124, 280, 30])
    return p.json()


def patch_master(codice):
    p = Patch()
    p.gen(codice, 6)
    p.dial("level", "MASTER", fx.MASTER_UNITY_T * 100, [8, 8, 60, 52])
    p.tab("mono", "MONO", ["STEREO", "MONO"], 0, [8, 66, 60, 36])
    p.boxes[-2]["box"]["num_lines_presentation"] = 2
    p.boxes[-2]["box"]["num_lines_patching"] = 2
    p.meter("obj-ml", 2, [80, 8, 12, 110], "METER L")
    p.meter("obj-mr", 3, [94, 8, 12, 110], "METER R")
    p.meter("obj-cl", 4, [108, 8, 5, 110], "CLIP L")
    p.meter("obj-cr", 5, [115, 8, 5, 110], "CLIP R")
    p.nota("Unity all'80 % (detent). Meter: 0 = +24 dBu, -24 = 0 dBu.",
           [8, 124, 200, 30])
    return p.json()


def scrivi(nome, pj, codice=None):
    if codice is not None:
        comuni = nomi_in_comune(codice)
        assert not comuni, f"{nome}: nomi in comune {comuni}"
        with open(os.path.join(USCITA, f"{nome}.genexpr"), "w") as f:
            f.write(codice)
    testo = json.dumps(pj, indent="\t")
    with open(os.path.join(USCITA, f"{nome}.maxpat"), "w") as f:
        f.write(testo)
    with open(os.path.join(USCITA, f"{nome}.amxd"), "wb") as f:
        f.write(amxd(testo))
    righe = f" ({codice.count(chr(10))} righe gen~)" if codice else ""
    print(f"scritto {nome}{righe}")


def main():
    cs, cr, cm = genexpr_send(), genexpr_ret(), genexpr_master()
    scrivi("MC-SEND", patch_send(cs), cs)
    scrivi("MC-BUS", patch_bus())
    scrivi("MC-RET", patch_ret(cr), cr)
    scrivi("MC-MASTER", patch_master(cm), cm)


if __name__ == "__main__":
    main()
