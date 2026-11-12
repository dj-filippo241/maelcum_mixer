"""Genera il dispositivo MC-5WAY (prototipo Max P2).

Uso:  python3 proto-max/coefficienti/genera_5way.py [--semplice]
Scrive in proto-max/: MC-5WAY.genexpr, .maxpat, .amxd
Con --semplice scrive MC-5WAY-S: le scelte d'ascolto di Filippo
(2026-10-21) fissate, senza selettori: CROSSOVER E, GROWL LIBERO,
NASTRO EXCITER.

I numeri vengono da fiveway.py; oversampling e contenitore .amxd da
genera.py (P0). Come in P0 e P1, il codice gen~ usa solo assegnazioni,
peek/poke e funzioni di righe semplici: prova_5way.py lo traduce in
Python e lo fa suonare.

Pannello (five-way §1 e §9, dec. 85/88/99): per ogni via un KILL
(taglio netto); per ogni banda EQ GAIN, POSITION e WIDTH; GROWL e
NASTRO. Solo prototipo: CROSSOVER A-E per B3 (q67), GROWL VER, NASTRO VER.
GROWL VER e NASTRO VER hanno anche la voce BANDE (dec. 165 e 166,
modelli growl_bande.py e nastro_bande.py): blocchi che si calcolano solo
quando il selettore li pesa, con gli stati a zero quando sono spenti.

Nomi: le variabili d0 e d1 appartengono al downsampling di genera.py
(Codice.giu). Il P1 le ha usate per altro e ha rotto il canale R.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import fiveway as fw  # noqa: E402
import alternative as al  # noqa: E402
import growl_bande as gbm  # noqa: E402
import nastro_bande as nbm  # noqa: E402
import genera  # noqa: E402
from genera import Codice, box, linea, patcher_gen, amxd  # noqa: E402

USCITA = genera.USCITA
NOME = "MC-5WAY"

KILL = [(f"k_{v.lower()}", f"KILL {v}") for v in fw.VIE]
GAIN = [(f"g_{i + 1}", f"EQ{i + 1} GAIN") for i in range(5)]
POS = [(f"p_{i + 1}", f"EQ{i + 1} POS") for i in range(5)]
WID = [(f"w_{i + 1}", f"EQ{i + 1} WIDTH") for i in range(5)]
SAT = [("growl", "GROWL"), ("nastro", "NASTRO")]
GV = ("gv", "GROWL VER", ["DEC.99", "LIBERO", "BANDE"])
NV = ("nver", "NASTRO VER", ["OGGI", "COMPLETO", "EXCITER", "CLASSE A",
                            "LIBERO", "COMPL. MEDI", "BANDE"])
XO = ("xo", "CROSSOVER", list(fw.VARIANTI_XO))
KILL_VOCI = ["ON", "KILL"]

# stati nel Data sv: 2 per SVF. Per lato: spina 8, LP 8, AP 6, celle 5,
# GROWL 1 = 28 SVF. Nel Data sa: HP del GROWL (1), HP-JFET non serve
# (il condensatore e vc), JFET: vs2, idd, vc come scarti dal riposo.
SVF_VECCHI = 30                 # + head bump del COMPLETO, passa-alto EXCITER
SVF_LATO = SVF_VECCHI + 2       # + GROWL A BANDE: LP4 del basso (2 SVF)
SA_VECCHI = 23                  # + COMPLETO 5, EXCITER 1, CLASSE A 4, LIBERO 4, MEDI 5
SA_GB = SA_VECCHI               # GROWL A BANDE: LP1 dei medi, 2 HP (3)
SA_NB = SA_GB + 3               # NASTRO A BANDE: poli di enfasi e de-enfasi, LIBERO 4
GB = gbm.VAR[gbm.SCELTA]        # dec. 165
NB = nbm.Bande(192000.0, nbm.VAR[nbm.SCELTA])   # dec. 166: solo i numeri
SA_LATO = SA_NB + 2 * (len(NB.e_lo) + len(NB.e_hi) + len(NB.e_t)) + 4
VS20, ID0, VD0 = fw.jfet_riposo()
_CA = al.ClasseA(48000.0)
VE20, VCAP0 = _CA.ve2, _CA.vcap
# versione semplice (Filippo 2026-10-21): scelte fissate, niente selettori.
# Scelte della dec. 175 (2026-11-10): prima E, LIBERO, EXCITER.
SEMPLICE = False
SCELTA_XO = 6                   # H 60/250/1,2k/8k
SCELTA_GV = 2                   # GROWL A BANDE (dec. 165)
SCELTA_NV = 6                   # NASTRO A BANDE B9 (dec. 166)


def funzioni(r):
    r("// allpass del 1o ordine del halfband; stato in m[i] (x), m[i+1] (y)")
    r("ap(m, i, x, c) {")
    r("\ty = c * (x - peek(m, i + 1)) + peek(m, i);")
    r("\tpoke(m, x, i);")
    r("\tpoke(m, y, i + 1);")
    r("\treturn y;")
    r("}")
    r()
    # Un solo valore di ritorno per funzione: la prima versione usava
    # svf() con tre ritorni (lp, bp, hp) e in Live passava solo il SUB
    # (la spina usa il terzo). P1 usa solo funzioni a uno o due ritorni.
    for nome, uscita in (("svlp", "fl"), ("svbp", "fb"), ("svhp", "fh")):
        r(f"// SVF 2 poli TPT lineare, uscita {nome[2:].upper()}; stato in "
          "m[i], m[i+1]; k = 1/Q")
        r(f"{nome}(m, i, x, g, k) {{")
        r("\ts1 = peek(m, i);")
        r("\ts2 = peek(m, i + 1);")
        r("\tfh = (x - (k + g) * s1 - s2) / (1 + g * (k + g));")
        r("\tfb = g * fh + s1;")
        r("\tfl = g * fb + s2;")
        r("\tpoke(m, g * fh + fb, i);")
        r("\tpoke(m, g * fb + fl, i + 1);")
        r(f"\treturn {uscita};")
        r("}")
        r()
    r("// passa-alto del 1o ordine TPT (condensatore di accoppiamento)")
    r("hp1(m, i, x, g) {")
    r("\ts = peek(m, i);")
    r("\tv = (x - s) * g / (1 + g);")
    r("\tlo = v + s;")
    r("\tpoke(m, lo + v, i);")
    r("\treturn x - lo;")
    r("}")
    r()
    r("// clipper del GROWL: 10k in, 22k || (1 diodo + 2,2k) || (3 diodi +")
    r("// 2,2k); Newton sulla tensione dei diodi del ramo che conduce")
    r("clipg(low) {")
    r(f"\tii = low / {fw.G_RIN!r};")
    r("\tpos = ii >= 0;")
    r("\ta = abs(ii);")
    r(f"\trr = pos * {fw.G_RA!r} + (1 - pos) * {fw.G_RB!r};")
    r(f"\tnv = pos * {fw.G_NA!r} + (1 - pos) * {fw.G_NB!r};")
    r(f"\tvd = nv * log(1 + a / {fw.D_IS!r});")
    for _ in range(fw.NEWTON):
        r("\tex = exp(vd / nv);")
        r(f"\tf = {fw.D_IS!r} * (ex - 1) * (1 + rr / {fw.G_RF!r})"
          f" + vd / {fw.G_RF!r} - a;")
        r(f"\tdf = {fw.D_IS!r} * ex / nv * (1 + rr / {fw.G_RF!r})"
          f" + 1 / {fw.G_RF!r};")
        r("\tvd = vd - f / df;")
    r(f"\tid = {fw.D_IS!r} * (exp(vd / nv) - 1);")
    r(f"\treturn {fw.G_RF!r} * (a - id) * (pos * 2 - 1);")
    r("}")
    r()
    for banda in ("low", "mid"):
        _, rf, rs, na, nb, _ = GB[banda]
        ra, rb = rs + na * fw.D_RS, rs + nb * fw.D_RS
        va, vb = na * fw.D_N * fw.VT27, nb * fw.D_N * fw.VT27
        r(f"// GROWL A BANDE, clipper del {'basso' if banda == 'low' else 'medio'}:"
          f" Rin variabile (spinta), Rf {rf:g}, {na} / {nb} diodi con {rs:g}")
        r(f"clipb{banda[0]}(cbx, cbrin) {{")
        r("	cbi = cbx / cbrin;")
        r("	cbp = cbi >= 0;")
        r("	cba = abs(cbi);")
        r(f"	cbr = cbp * {ra!r} + (1 - cbp) * {rb!r};")
        r(f"	cbn = cbp * {va!r} + (1 - cbp) * {vb!r};")
        r(f"	cbd = cbn * log(1 + cba / {fw.D_IS!r});")
        for _ in range(6):          # come ramo() di growl_bande.py
            r("	cbe = exp(cbd / cbn);")
            r(f"	cbf = {fw.D_IS!r} * (cbe - 1) * (1 + cbr / {rf!r})"
              f" + cbd / {rf!r} - cba;")
            r(f"	cbg = {fw.D_IS!r} * cbe / cbn * (1 + cbr / {rf!r})"
              f" + 1 / {rf!r};")
            r("	cbd = cbd - cbf / cbg;")
        r(f"	cbq = {fw.D_IS!r} * (exp(cbd / cbn) - 1);")
        r(f"	return {rf!r} * (cba - cbq) * (cbp * 2 - 1);")
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
    r("// clipper dell'EXCITER: 10k in, 100k || (1 diodo + 1k) || (2 diodi + 1k)")
    r("clipe(h) {")
    r(f"\tii = h / {al.EX_RIN!r};")
    r("\tpos = ii >= 0;")
    r("\ta = abs(ii);")
    r(f"\trr = pos * {al.EX_RA!r} + (1 - pos) * {al.EX_RB!r};")
    r(f"\tnv = pos * {al.EX_NA!r} + (1 - pos) * {al.EX_NB!r};")
    r(f"\tvd = nv * log(1 + a / {fw.D_IS!r});")
    for _ in range(fw.NEWTON):
        r("\tex = exp(vd / nv);")
        r(f"\tf = {fw.D_IS!r} * (ex - 1) * (1 + rr / {al.EX_RF!r})"
          f" + vd / {al.EX_RF!r} - a;")
        r(f"\tdf = {fw.D_IS!r} * ex / nv * (1 + rr / {al.EX_RF!r})"
          f" + 1 / {al.EX_RF!r};")
        r("\tvd = vd - f / df;")
    r(f"\tid = {fw.D_IS!r} * (exp(vd / nv) - 1);")
    r(f"\treturn {al.EX_RF!r} * (a - id) * (pos * 2 - 1);")
    r("}")
    r()
    vt = al.B_N * fw.VT27
    r("// CLASSE A: un passo di Newton su Vbe (Gummel-Poon ridotto, 2N3904);")
    r("// m[i] = Vc stimata, m[i+1] = Ic")
    r("bstep(m, i, vbe, vb, ve2, vth, rp) {")
    r(f"\tex = exp(vbe / {vt!r});")
    r(f"\tq1 = 1 / (1 - (vb - peek(m, i)) / {al.B_VAF!r});")
    r(f"\tq2 = {al.B_IS!r} * (ex - 1) / {al.B_IKF!r};")
    r("\tsq = sqrt(1 + 4 * q2);")
    r("\tqb = 0.5 * q1 * (1 + sq);")
    r(f"\tic = {al.B_IS!r} * (ex - 1) / qb;")
    r(f"\tie = ic * {1 + 1 / al.B_BF!r};")
    r(f"\tf = vbe + {al.B_REU!r} * ie + ve2 - vb;")
    r(f"\tdf = 1 + {al.B_REU!r} * ie / {vt!r} / sq;")
    r(f"\tpoke(m, max(vth - rp * ic, ve2 + {al.B_REU!r} * ie + {al.B_VSAT!r}), i);")
    r("\tpoke(m, ic, i + 1);")
    r("\treturn min(max(vbe - f / df, 0.3), 0.9);")
    r("}")
    r()
    vt, rg, gis = fw.VT27, al.NL_RG, al.NL_IS
    r("// NASTRO LIBERO: gate dietro 10k, diodo gate-source verso gvs;")
    r("// Newton dall'alto")
    r("gatev(gin, gvs) {")
    r(f"\tgvg = gvs + {vt!r} * log(1 + max(gin - gvs, 0) / {rg * gis!r});")
    for _ in range(al.NL_PASSI_G):
        r(f"\tgax = exp((gvg - gvs) / {vt!r});")
        r(f"\tgf = gvg + {rg * gis!r} * (gax - 1) - gin;")
        r(f"\tgdf = 1 + {rg * gis / vt!r} * gax;")
        r("\tgvg = gvg - gf / gdf;")
    r("\treturn gvg;")
    r("}")
    r()
    b, vto, lam = fw.J_BETA, fw.J_VTO, fw.J_LAMBDA
    rp, rts, rsu = fw.J_RP, fw.J_RTS, fw.J_RSU
    r("// un passo di Newton sulla corrente del JFET (Shichman-Hodges,")
    r("// saturazione o triodo); drain su Rd e sul sommatore (vc)")
    r("jstep(vg, vs2, vc, idd) {")
    r(f"\tvd = {rp!r} * ({fw.J_VCC / fw.J_RD!r} + vc / {rts!r} - idd);")
    r(f"\tvs = vs2 + {rsu!r} * idd;")
    r(f"\tvov = max(vg - vs - ({vto!r}), 0);")
    r("\tvds = vd - vs;")
    r("\tsat = vds >= vov;")
    r(f"\tcl = 1 + {lam!r} * vds;")
    r("\tq = vds * (2 * vov - vds);")
    r(f"\ti = sat * {b!r} * vov * vov * cl + (1 - sat) * {b!r} * q * cl;")
    r(f"\tdgs = sat * {2 * b!r} * vov * cl + (1 - sat) * {2 * b!r} * vds * cl;")
    r(f"\tdds = sat * {b * lam!r} * vov * vov"
      f" + (1 - sat) * {b!r} * ((2 * vov - 2 * vds) * cl + q * {lam!r});")
    r(f"\tdf = 1 + dgs * {rsu!r} + dds * ({rp + rsu!r});")
    r("\treturn max(idd - (idd - i) / df, 0);")
    r("}")
    r()


def libero(r, p, ingresso, s0, gn="gnl"):
    """NASTRO LIBERO: spinta gn, gate che conduce, JFET di oggi. Stati in
    sa[s0 .. s0 + 3]; uscita {p}tac (tensione sul condensatore d'uscita)."""
    r(f"{p}vin = min(max({gn} * {ingresso}, {-al.NL_RAIL!r}), {al.NL_RAIL!r});")
    r(f"{p}vs2 = {VS20!r} + peek(sa, {s0});")
    r(f"{p}id = {ID0!r} + peek(sa, {s0 + 1});")
    r(f"{p}vc = {VD0!r} + peek(sa, {s0 + 2});")
    r(f"{p}ig = peek(sa, {s0 + 3});")
    for _ in range(fw.NEWTON):
        r(f"{p}vg = gatev({p}vin, {p}vs2 + {fw.J_RSU!r} * ({p}id + {p}ig));")
        r(f"{p}ig = ({p}vin - {p}vg) / {al.NL_RG!r};")
        for _ in range(fw.NEWTON):
            r(f"{p}id = jstep({p}vg, {p}vs2 + {fw.J_RSU!r} * {p}ig, {p}vc,"
              f" {p}id);")
    r(f"{p}vd = {fw.J_RP!r} * ({fw.J_VCC / fw.J_RD!r} + {p}vc / "
      f"{fw.J_RTS!r} - {p}id);")
    r(f"{p}tac = {p}vd - {p}vc;")
    r(f"poke(sa, {p}vs2 + kcb * ({p}id + {p}ig - {p}vs2 / {fw.J_RSB!r})"
      f" - {VS20!r}, {s0});")
    r(f"poke(sa, {p}id - {ID0!r}, {s0 + 1});")
    r(f"poke(sa, {p}vc + kc * {p}tac - {VD0!r}, {s0 + 2});")
    r(f"poke(sa, {p}ig, {s0 + 3});")


def growl_bande(r, b0, sa0, kq):
    """GROWL A BANDE (dec. 165, growl_bande.Growl3): basso e medi, ognuno
    nel suo clipper; si calcola solo se GROWL VER lo pesa (wgb > 0)."""
    i = b0 + 2 * SVF_VECCHI
    s = sa0 + SA_GB
    lo_, mi_ = GB["low"], GB["mid"]
    km = mi_[5] if mi_[5] is not None else \
        1 / (mi_[1] / 10e3 * 10 ** (mi_[0] / 20))
    r("// GROWL A BANDE (dec. 165)")
    r("dgb = 0;")
    r("if (wgb > 0) {")
    r(f"gbl = svlp(sv, {i}, xa, gbf, {kq!r});")
    r(f"gbl = svlp(sv, {i + 2}, gbl, gbf, {kq!r});")
    r(f"gbm = op1(sa, {s}, xa - gbl, gbfm);")
    r(f"dgb = {lo_[5]!r} * hp1(sa, {s + 1}, clipbl(gbl, rbl), gbh) - gbl"
      f" + {km!r} * hp1(sa, {s + 2}, clipbm(gbm, rbm), gbh) - gbm;")
    r("}")
    r("dg = dg + wgb * (dgb - dg);")


def nastro_bande(r, sa0):
    """NASTRO A BANDE (dec. 166, nastro_bande.Bande): poli di enfasi (bassi,
    super, inclinazione dei medi), LIBERO con la spinta gnb della curva
    sua, de-enfasi inversa, guadagno del ramo; solo se NASTRO VER lo pesa."""
    s = sa0 + SA_NB
    r("// NASTRO A BANDE (dec. 166)")
    r("dnb = 0;")
    r(f"if (wn{len(NV[2]) - 1} > 0) {{")
    r("nbu = y1;")
    j = s
    for _ in NB.e_lo:
        r(f"nbp = op1(sa, {j}, nbu, gnp);")
        r(f"nbu = {NB.cl!r} * nbp + nbu - nbp;")
        j += 1
    for _ in NB.e_hi:
        r(f"nbp = op1(sa, {j}, nbu, gna);")
        r(f"nbu = nbp + {NB.ab!r} * (nbu - nbp);")
        j += 1
    for _ in NB.e_t:
        r(f"nbp = op1(sa, {j}, nbu, gnt);")
        r(f"nbu = nbp + {NB.at!r} * (nbu - nbp);")
        j += 1
    libero(r, "q", "nbu", j, "gnb")
    j += 4
    r(f"nbw = -{al.NL_K!r} * qtac;")
    for _ in NB.d_hi:
        r(f"nbp = op1(sa, {j}, nbw, gnh);")
        r(f"nbw = nbp + {NB.gh!r} * (nbw - nbp);")
        j += 1
    for _ in NB.d_t:
        r(f"nbp = op1(sa, {j}, nbw, gnu);")
        r(f"nbw = nbp + {NB.gt!r} * (nbw - nbp);")
        j += 1
    for _ in NB.d_lo:
        r(f"nbp = op1(sa, {j}, nbw, gnq);")
        r(f"nbw = {NB.gl!r} * nbp + nbw - nbp;")
        j += 1
    assert j == sa0 + SA_LATO
    r(f"dnb = {NB.kv!r} * nbw - y1;")
    r("}")


def spegni(r, b0, sa0):
    """Stati dei blocchi a bande spenti a zero: ripartono puliti."""
    r("if (wgb == 0) {")
    for j in range(b0 + 2 * SVF_VECCHI, b0 + 2 * SVF_LATO):
        r(f"poke(sv, 0, {j});")
    for j in range(sa0 + SA_GB, sa0 + SA_NB):
        r(f"poke(sa, 0, {j});")
    r("}")
    r(f"if (wn{len(NV[2]) - 1} == 0) {{")
    for j in range(sa0 + SA_NB, sa0 + SA_LATO):
        r(f"poke(sa, 0, {j});")
    r("}")


def genexpr():
    g = Codice()
    r = g.r
    r(f"// {NOME} - prototipo Max P2 del 5-way maelcum_mixer.")
    r("// GENERATO da proto-max/coefficienti/genera_5way.py: non modificare.")
    r("// Banca LR4 allineata in fase (5 vie, kill netti), 5 celle a campana,")
    r("// GROWL e NASTRO in parallelo al pulito. Tutto a 4x.")
    r()
    funzioni(r)
    for nome, _ in KILL:
        r(f"Param {nome}(0, min=0, max=1);")
    for nome, _ in GAIN + POS:
        r(f"Param {nome}(50, min=0, max=100);")
    for nome, _ in WID:
        r(f"Param {nome}(50, min=0, max=100);")  # dec. 117: continuo
    for nome, _ in SAT:
        r(f"Param {nome}(0, min=0, max=100);")
    if not SEMPLICE:
        r(f"Param {XO[0]}(0, min=0, max={len(XO[2]) - 1});")
        r(f"Param {GV[0]}(0, min=0, max={len(GV[2]) - 1});")
        r(f"Param {NV[0]}(0, min=0, max={len(NV[2]) - 1});")
    # il -S tiene gli indici del completo: gli stati dei NASTRO non scelti restano allocati
    nsv = SVF_LATO
    nsa = SA_LATO
    r(f"Data sv({2 * 2 * nsv});")
    r(f"Data sa({2 * nsa});")
    r("Data zk(30);  // kill allo zero: per lato e via stato, campione prima, conteggio")
    pos_data = len(g.righe)
    r("@@DATA@@")
    lisci = [n for n, _ in GAIN + POS + WID + SAT]
    if not SEMPLICE:
        lisci += [XO[0], GV[0], NV[0]]
    for nome in lisci:
        ini = {"w": 50, "g": 50, "p": 50}.get(nome[0], 0)
        r(f"History s_{nome}({ini});")
    r()
    r("// manopole lisciate 10 ms (WIDTH compreso); CROSSOVER 20 ms; KILL netti")
    r("t1 = exp(-1 / (0.001 * samplerate));")
    r("t10 = exp(-1 / (0.010 * samplerate));")
    r("t20 = exp(-1 / (0.020 * samplerate));")
    for nome in lisci:
        t = {"w": "t1", "x": "t20"}.get(nome[0], "t10")
        t = "t20" if nome in (GV[0], NV[0]) else t
        r(f"s_{nome} = {nome} + {t} * (s_{nome} - {nome});")
    r("sr4 = samplerate * 4;")
    r()
    varianti = list(fw.VARIANTI_XO.values())
    if SEMPLICE:
        r(f"// CROSSOVER {XO[2][SCELTA_XO]}")
        for c in range(4):
            r(f"gx{c} = tan(pi * {varianti[SCELTA_XO][c]!r} / sr4);")
    else:
        r(f"// CROSSOVER: le {len(varianti)} varianti di B3, frequenze che"
          " scivolano in 20 ms")
        for j in range(len(varianti)):
            r(f"wx{j} = max(0, 1 - abs(s_xo - {j}));")
        for c in range(4):
            termini = " + ".join(f"wx{j} * {v[c]!r}"
                                 for j, v in enumerate(varianti))
            r(f"gx{c} = tan(pi * ({termini}) / sr4);")
    r()
    r("// KILL: 1 = via aperta (interruttore, dec. 88). La levetta scatta al")
    r("// primo passaggio per lo zero della via, o dopo 20 ms (dec. 164)")
    for v, (nome, _) in enumerate(KILL):
        r(f"a{v} = 1 - {nome};")
    r(f"ztm = {fw.KILL_ZC_TMAX!r} * sr4;")
    r()
    r("// celle EQ: GAIN (famiglia eq-serie §10), POSITION esponenziale,")
    r("// WIDTH continuo Q3...Q0,3, taper log 20 % (fw.q_width; dec. 117, 129)")
    kn = fw.CUT_KNEE_DB
    lin_k = 10 ** (kn / 20)
    for i in range(5):
        n = i + 1
        lo, hi = fw.POSIZIONE[i]
        r(f"th = s_g_{n} / 100;")
        r(f"gl = (th >= 0.5) * pow(10, {fw.GAIN_MAX[i] / 20!r} * (th - 0.5)"
          f" / 0.5) + (th < 0.5) * (th >= {fw.CUT_KNEE_TH!r})"
          f" * pow(10, {kn / 20!r} * (0.5 - th) / {0.5 - fw.CUT_KNEE_TH!r})"
          f" + (th < {fw.CUT_KNEE_TH!r}) * {lin_k!r} * th"
          f" / {fw.CUT_KNEE_TH!r};")
        r(f"b{n} = gl - 1;")
        r(f"ge{n} = tan(pi * {lo!r} * pow({hi / lo!r}, s_p_{n} / 100)"
          f" / sr4);")
        mw, am = fw.WIDTH_TAPER, fw.WIDTH_ALPHA_MIN
        r(f"tw = s_w_{n} / 100;")
        r(f"aw = (tw <= 0.5) * {mw / 0.5!r} * tw + (tw > 0.5) * "
          f"({mw!r} + {(1 - mw) / 0.5!r} * (tw - 0.5));")
        r(f"ke{n} = ({am!r} + {1 - am!r} * aw) / {fw.WIDTH_Q0!r};")
    r(f"// GROWL: curva lenta, mg = t^{fw.GROWL_ESP:g}")
    r(f"mg = pow(s_growl / 100, {fw.GROWL_ESP!r});")
    tn = "s_nastro / 100"
    r(f"tn = {tn};")
    r(f"mt = {fw.NASTRO_MAX!r} * ((tn <= 0.5) * {fw.TAPER_A_MID!r} * tn / 0.5"
      f" + (tn > 0.5) * ({fw.TAPER_A_MID!r} + {1 - fw.TAPER_A_MID!r}"
      f" * (tn - 0.5) / 0.5));")
    r(f"// NASTRO LIBERO: spinta 0 -> +{al.NL_GMAX_DB:g} dB con la manopola")
    r(f"gnl = pow(10, {al.NL_GMAX_DB / 20!r} * tn);")
    if True:
        inv = nbm.SCELTA in nbm.INVERSA
        r("// NASTRO A BANDE: manopola a curva "
          + (f"inversa, tb = 1 - (1 - tn)^{nbm.INV_ESP:g}" if inv
             else "lineare"))
        r(f"tb = 1 - pow(1 - tn, {nbm.INV_ESP!r});" if inv else "tb = tn;")
        r(f"mtb = {fw.NASTRO_MAX!r} * ((tb <= 0.5) * {fw.TAPER_A_MID!r} * tb"
          f" / 0.5 + (tb > 0.5) * ({fw.TAPER_A_MID!r} + "
          f"{1 - fw.TAPER_A_MID!r} * (tb - 0.5) / 0.5));")
        r(f"gnb = pow(10, {al.NL_GMAX_DB / 20!r} * tb);")
    if SEMPLICE:
        assert SCELTA_GV == 2
        r("// GROWL A BANDE (dec. 165, 175): solo questo, il LIBERO non si calcola;")
        r("// con la manopola a zero il blocco non si calcola e i suoi stati vanno a zero")
        r("wgb = s_growl > 0.001;")
    else:
        r("// GROWL VER: 0 = dec. 99, 1 = LIBERO (spinta 0 -> +18 dB col pot),")
        r("// 2 = A BANDE (dec. 165), in dissolvenza dal LIBERO")
        r("glib = min(s_gv, 1);")
        r("wgb = max(s_gv - 1, 0);")
        r(f"gg = 1 + glib * (pow(10, {fw.LIB_GMAX_DB / 20!r} * mg) - 1);")
        r(f"kk = {fw.KG!r} + glib * {fw.LIB_K - fw.KG!r};")
    if True:
        lo_, mi_ = GB["low"], GB["mid"]
        r(f"// GROWL A BANDE: LP4 {GB['FL']} Hz al basso, LP1 {GB['FM']} Hz ai"
          f" medi; spinta 0 -> +{lo_[0]:g} / +{mi_[0]:g} dB col pot")
        r(f"rbl = 10000 / pow(10, {lo_[0] / 20!r} * mg);")
        r(f"rbm = 10000 / pow(10, {mi_[0] / 20!r} * mg);")
        r(f"gbf = tan(pi * {float(GB['FL'])!r} / sr4);")
        r(f"gbfm = tan(pi * {float(GB['FM'])!r} / sr4);")
        r("gbh = tan(pi * 1.0 / sr4);")
    r(f"glp = tan(pi * {fw.FX_GROWL!r} / sr4);")
    r(f"ghg = tan(pi * {fw.F_HP_G!r} / sr4);")
    r(f"kcb = 1 / (sr4 * {fw.J_CB!r});")
    r(f"kc = 1 / (sr4 * {10e-6 * fw.J_RTS!r});")
    if SEMPLICE:
        assert SCELTA_NV == 6
        r("// NASTRO A BANDE B9 (dec. 166, 175): solo questo; a manopola zero non si calcola")
        r(f"wn{len(NV[2]) - 1} = s_nastro > 0.001;")
    else:
        r("// NASTRO VER: 0 OGGI, 1 COMPLETO, 2 EXCITER, 3 CLASSE A, 4 LIBERO,"
          " 5 COMPLETO MEDI, 6 A BANDE"
          " (20 ms)")
        for j in range(len(NV[2])):
            r(f"wn{j} = max(0, 1 - abs(s_nver - {j}));")
    if True:
        fz, fp, fa, fb = nbm.VAR[nbm.SCELTA][:4]
        r(f"// NASTRO A BANDE: enfasi (bassi {fz:g}/{fp:g} Hz e super"
          f" {fa:g}/{fb:g} Hz tagliati) davanti al LIBERO, de-enfasi dopo")
        poli = [("gnp", fp), ("gna", fa), ("gnh", fa * NB.gh),
                ("gnq", fp / NB.gl)]
        if NB.e_t:
            fm = nbm.VAR[nbm.SCELTA][8]
            r(f"// inclinazione dei medi: polo {fm:g} Hz / zero"
              f" {fm * NB.gt:g} Hz prima del JFET, inversa dopo")
            poli += [("gnt", fm), ("gnu", fm * NB.gt)]
        for nome, f in poli:
            r(f"{nome} = tan(pi * {f!r} / sr4);")
    r(f"gcp = tan(pi * {al.EN_FP!r} / sr4);")
    r(f"gcz = tan(pi * {al.EN_FZ!r} / sr4);")
    r(f"gmp = tan(pi * {al.EM_FP!r} / sr4);")
    r(f"gmz = tan(pi * {al.EM_FZ!r} / sr4);")
    r(f"ghb = tan(pi * {al.HB_F!r} / sr4);")
    r(f"gex = tan(pi * {al.EX_F!r} / sr4);")
    r(f"kce = 1 / (sr4 * {al.B_CE!r});")
    r(f"kcc = 1 / (sr4 * {10e-6 * al.B_RTS!r});")
    kq = 1 / fw.Q_BW
    liv = fw.LIV * fw.PAD
    r()
    r(f"// livelli: 1,0 digitale = {fw.LIV:.3f} V; dominio interno -6 dB")
    for lato, ingresso, uscita in (("L", "in1", "out1"), ("R", "in2", "out2")):
        b0 = 0 if lato == "L" else 2 * nsv
        sa0 = 0 if lato == "L" else nsa
        r(f"// ===== lato {lato} =====")
        g.su(ingresso, f"{lato}_e", f"{lato}_o", 1, (lato, "su", 1))
        g.su(f"{lato}_e", f"{lato}_u0", f"{lato}_u1", 2, (lato, "su", 2))
        g.su(f"{lato}_o", f"{lato}_u2", f"{lato}_u3", 2, (lato, "su", 2))
        for k in range(4):
            i = b0
            r(f"xa = {lato}_u{k};")
            r("// banca: spina HP4 ai 4 crossover")
            r("p0 = xa;")
            for c in range(4):
                src = f"p{c}"
                for s in range(2):
                    r(f"p{c + 1} = svhp(sv, {i},"
                      f" {src if s == 0 else f'p{c + 1}'}, gx{c}, {kq!r});")
                    i += 2
            r("// vie: LP4 dalla presa e allpass dei crossover sopra")
            for v in range(4):
                r(f"ya = p{v};")
                for s in range(2):
                    r(f"ya = svlp(sv, {i}, ya, gx{v}, {kq!r});")
                    i += 2
                for c in range(v + 1, 4) if v < 3 else ():
                    r(f"ya = ya - {2 * kq!r} * svbp(sv, {i}, ya, gx{c},"
                      f" {kq!r});")
                    i += 2
                r(f"v{v} = ya;")
            zb = 0 if lato == "L" else 15
            for v in range(5):
                b = zb + 3 * v
                r(f"zv = {'p4' if v == 4 else f'v{v}'};")
                r(f"zs = peek(zk, {b});")
                r(f"zn = peek(zk, {b + 2});")
                r(f"zt = 1 - a{v};")
                r("zc = abs(zt - zs) > 0.5;")
                r("zn = zc * (zn + 1);")
                r(f"zw = zc * max(peek(zk, {b + 1}) * zv <= 0, zn >= ztm);")
                r("zs = zs + zw * (zt - zs);")
                r(f"poke(zk, zs, {b});")
                r(f"poke(zk, zv, {b + 1});")
                r(f"poke(zk, zn, {b + 2});")
                r(f"z{v} = 1 - zs;")
            r("ya = z0 * v0 + z1 * v1 + z2 * v2 + z3 * v3 + z4 * p4;")
            r("// EQ creativo: 5 campane in serie")
            for n in range(1, 6):
                r(f"ya = ya + b{n} * ke{n} * svbp(sv, {i}, ya, ge{n}, ke{n});")
                i += 2
            r("// GROWL (sotto 350 Hz) e NASTRO, volt del dominio interno")
            r(f"xa = ya * {liv!r};")
            if not SEMPLICE:
                r(f"lw = svlp(sv, {i}, xa, glp, {kq!r});")
            i += 2
            if SEMPLICE:
                # GROWL A BANDE da solo: il clipper del LIBERO non si calcola
                r("dg = 0;")
            else:
                r(f"dg = kk * hp1(sa, {sa0}, clipg(gg * lw), ghg) - lw;")
            growl_bande(r, b0, sa0, kq)
            r("y1 = xa + mg * dg;")
            if SEMPLICE:
                # solo il NASTRO A BANDE: gli altri NASTRO non si scrivono, ma i
                # loro stati restano allocati (stessi indici del completo)
                assert SCELTA_NV == 6
                i += 4
                nastro_bande(r, sa0)
                r(f"{lato}_y{k} = (y1 + mtb * dnb) / {liv!r};")
                assert i == b0 + 2 * SVF_VECCHI
                continue
            r(f"jvs = {VS20!r} + peek(sa, {sa0 + 1});")
            r(f"jvc = {VD0!r} + peek(sa, {sa0 + 3});")
            r(f"jid = {ID0!r} + peek(sa, {sa0 + 2});")
            for _ in range(fw.NEWTON):
                r("jid = jstep(y1, jvs, jvc, jid);")
            r(f"vdr = {fw.J_RP!r} * ({fw.J_VCC / fw.J_RD!r} + jvc / "
              f"{fw.J_RTS!r} - jid);")
            r("vtac = vdr - jvc;")
            r(f"poke(sa, jvs + kcb * (jid - jvs / {fw.J_RSB!r}) - {VS20!r},"
              f" {sa0 + 1});")
            r(f"poke(sa, jid - {ID0!r}, {sa0 + 2});")
            r(f"poke(sa, jvc + kc * vtac - {VD0!r}, {sa0 + 3});")
            r(f"dt = -{fw.KT!r} * vtac - y1;")
            r("// NASTRO COMPLETO: enfasi, JFET, de-enfasi, head bump")
            r(f"cpl = op1(sa, {sa0 + 4}, y1, gcp);")
            r(f"cen = cpl + {al.EN_FP / al.EN_FZ!r} * (y1 - cpl);")
            r(f"cvs = {VS20!r} + peek(sa, {sa0 + 5});")
            r(f"cvc = {VD0!r} + peek(sa, {sa0 + 7});")
            r(f"cid = {ID0!r} + peek(sa, {sa0 + 6});")
            for _ in range(fw.NEWTON):
                r("cid = jstep(cen, cvs, cvc, cid);")
            r(f"cvd = {fw.J_RP!r} * ({fw.J_VCC / fw.J_RD!r} + cvc / "
              f"{fw.J_RTS!r} - cid);")
            r("ctac = cvd - cvc;")
            r(f"poke(sa, cvs + kcb * (cid - cvs / {fw.J_RSB!r}) - {VS20!r},"
              f" {sa0 + 5});")
            r(f"poke(sa, cid - {ID0!r}, {sa0 + 6});")
            r(f"poke(sa, cvc + kc * ctac - {VD0!r}, {sa0 + 7});")
            r(f"cw = -{fw.KT!r} * ctac;")
            r(f"cdl = op1(sa, {sa0 + 8}, cw, gcz);")
            r(f"cw2 = cdl + {al.EN_FZ / al.EN_FP!r} * (cw - cdl);")
            r(f"cw3 = cw2 + {al.HB_A / al.HB_Q!r} * svbp(sv, {i}, cw2, ghb,"
              f" {1 / al.HB_Q!r});")
            i += 2
            r("dco = cw3 - y1;")
            r("// EXCITER: passa-alto 3 kHz, clipper, passa-alto, si somma")
            r(f"exh = svhp(sv, {i}, y1, gex, {kq!r});")
            i += 2
            r(f"dex = {al.EX_K!r} * hp1(sa, {sa0 + 9}, clipe(exh), gex);")
            r("// CLASSE A: NPN a emettitore comune")
            rp = al.B_RC * al.B_RTS / (al.B_RC + al.B_RTS)
            r(f"cav2 = {VE20!r} + peek(sa, {sa0 + 10});")
            r(f"cacp = {VCAP0!r} + peek(sa, {sa0 + 11});")
            r(f"cath = {rp!r} * ({al.B_VCC / al.B_RC!r} + cacp / {al.B_RTS!r});")
            r(f"cab = {al.B_VB!r} + {al.B_ATT!r} * y1;")
            r(f"poke(sa, cath - {rp * 2e-3!r}, {sa0 + 12});")
            r("cabe = 0.66;")
            for _ in range(6):
                r(f"cabe = bstep(sa, {sa0 + 12}, cabe, cab, cav2, cath, {rp!r});")
            r(f"caic = peek(sa, {sa0 + 13});")
            r(f"caie = caic * {1 + 1 / al.B_BF!r};")
            r(f"cava = cath - {rp!r} * caic;")
            r(f"cavs = cav2 + {al.B_REU!r} * caie + {al.B_VSAT!r};")
            r(f"cavc = 0.5 * (cava + cavs + sqrt((cava - cavs) * (cava - cavs)"
              f" + {al.B_W * al.B_W!r}));")
            r("catac = cavc - cacp;")
            r(f"poke(sa, cav2 + kce * (caie - cav2 / {al.B_REB!r}) - {VE20!r},"
              f" {sa0 + 10});")
            r(f"poke(sa, cacp + kcc * catac - {VCAP0!r}, {sa0 + 11});")
            r(f"dca = -{al.B_K!r} * catac - y1;")
            r("// NASTRO LIBERO: spinta, gate che conduce, JFET di oggi")
            libero(r, "l", "y1", sa0 + 14)
            r(f"dli = -{al.NL_K!r} * ltac - y1;")
            r("// COMPLETO MEDI: enfasi 300 Hz / 600 Hz, JFET, de-enfasi")
            r(f"mpl = op1(sa, {sa0 + 18}, y1, gmp);")
            r(f"men = mpl + {al.EM_FP / al.EM_FZ!r} * (y1 - mpl);")
            r(f"mvs = {VS20!r} + peek(sa, {sa0 + 19});")
            r(f"mid_ = {ID0!r} + peek(sa, {sa0 + 20});")
            r(f"mvc = {VD0!r} + peek(sa, {sa0 + 21});")
            for _ in range(fw.NEWTON):
                r("mid_ = jstep(men, mvs, mvc, mid_);")
            r(f"mvd = {fw.J_RP!r} * ({fw.J_VCC / fw.J_RD!r} + mvc / "
              f"{fw.J_RTS!r} - mid_);")
            r("mtac = mvd - mvc;")
            r(f"poke(sa, mvs + kcb * (mid_ - mvs / {fw.J_RSB!r}) - {VS20!r},"
              f" {sa0 + 19});")
            r(f"poke(sa, mid_ - {ID0!r}, {sa0 + 20});")
            r(f"poke(sa, mvc + kc * mtac - {VD0!r}, {sa0 + 21});")
            r(f"mw = -{fw.KT!r} * mtac;")
            r(f"mdl = op1(sa, {sa0 + 22}, mw, gmz);")
            r(f"dme = mdl + {al.EM_FZ / al.EM_FP!r} * (mw - mdl) - y1;")
            nastro_bande(r, sa0)
            r("dn = wn0 * dt + wn1 * dco + wn2 * dex + wn3 * dca + wn4 * dli"
              " + wn5 * dme;")
            r(f"{lato}_y{k} = (y1 + mt * dn + mtb * wn6 * dnb) / {liv!r};")
            assert i == b0 + 2 * SVF_VECCHI
        spegni(r, b0, sa0)
        g.giu(f"{lato}_v0", f"{lato}_y0", f"{lato}_y1", 2, (lato, "giu", 2))
        g.giu(f"{lato}_v1", f"{lato}_y2", f"{lato}_y3", 2, (lato, "giu", 2))
        g.giu(f"{lato}_w", f"{lato}_v0", f"{lato}_v1", 1, (lato, "giu", 1))
        r(f"{uscita} = {lato}_w;")
        r()
    g.righe[pos_data] = f"Data hb({g.n_hb});"
    return "\n".join(g.righe) + "\n"


def patch(codice):
    boxes, lines, parametri = [], [], {}
    boxes.append(box("obj-in", maxclass="newobj", text="plugin~",
                     numinlets=2, numoutlets=2,
                     outlettype=["signal", "signal"],
                     patching_rect=[20, 20, 60, 22]))
    boxes.append(box("obj-gen", maxclass="newobj", text="gen~",
                     numinlets=2, numoutlets=2,
                     outlettype=["signal", "signal"],
                     patching_rect=[20, 400, 300, 22],
                     patcher=patcher_gen(codice)))
    boxes.append(box("obj-out", maxclass="newobj", text="plugout~",
                     numinlets=2, numoutlets=2,
                     outlettype=["signal", "signal"],
                     patching_rect=[20, 460, 60, 22]))
    lines += [linea("obj-in", 0, "obj-gen", 0),
              linea("obj-in", 1, "obj-gen", 1),
              linea("obj-gen", 0, "obj-out", 0),
              linea("obj-gen", 1, "obj-out", 1)]
    n = [0]

    def comando(nome_gen, nome_live, maxclass, rect, valueof):
        i = n[0]
        n[0] += 1
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
        boxes.append(box(id_, maxclass=maxclass, parameter_enable=1,
                         patching_rect=[x, y, 44, 48],
                         presentation=1, presentation_rect=rect,
                         saved_attribute_attributes={"valueof": attr},
                         varname=nome_live, **extra))
        pid = f"{id_}-pre"
        boxes.append(box(pid, maxclass="newobj", text=f"prepend {nome_gen}",
                         numinlets=1, numoutlets=1, outlettype=[""],
                         patching_rect=[x, y + 60, 85, 22]))
        lines.append(linea(id_, 0, pid, 0))
        lines.append(linea(pid, 0, "obj-gen", 0))
        parametri[id_] = [nome_live, nome_live, 0]

    def tab(nome_gen, nome_live, voci, ini, rect):
        comando(nome_gen, nome_live, "live.tab", rect,
                {"parameter_type": 2, "parameter_enum": voci,
                 "parameter_mmax": float(len(voci) - 1),
                 "parameter_initial": [ini], "parameter_unitstyle": 0})

    def dial(nome_gen, nome_live, ini, rect):
        comando(nome_gen, nome_live, "live.dial", rect,
                {"parameter_type": 0, "parameter_mmax": 100.0,
                 "parameter_initial": [ini], "parameter_unitstyle": 5})

    col = 60
    for v, (ng, nl) in enumerate(KILL):
        tab(ng, nl, KILL_VOCI, 0, [8 + col * v, 4, 54, 18])
    for i in range(5):
        dial(GAIN[i][0], GAIN[i][1], 50.0, [8 + col * i, 24, 54, 40])
        dial(POS[i][0], POS[i][1], 50.0, [8 + col * i, 66, 54, 40])
        dial(WID[i][0], WID[i][1], 50.0, [8 + col * i, 108, 54, 40])
    for j, (ng, nl) in enumerate(SAT):
        dial(ng, nl, 0.0, [312 + 60 * j, 24, 54, 48])
    if SEMPLICE:
        boxes.append(box("obj-nota", maxclass="live.comment", numinlets=1,
                         numoutlets=0, presentation=1,
                         presentation_rect=[8, 150, 490, 18],
                         patching_rect=[20, 520, 490, 18],
                         text="Semplice (dec. 175): CROSSOVER H 60/250/1,2k/8k, "
                              "GROWL BANDE, NASTRO BANDE B9. 0 dBu = -12 dBFS."))
        return finestra(boxes, lines, parametri)
    tab(XO[0], XO[1], XO[2], 0, [312, 78, 114, 66])
    boxes[-2]["box"]["num_lines_presentation"] = len(XO[2])
    boxes[-2]["box"]["num_lines_patching"] = len(XO[2])
    tab(GV[0], GV[1], GV[2], 0, [432, 4, 64, 42])
    boxes[-2]["box"]["num_lines_presentation"] = len(GV[2])
    boxes[-2]["box"]["num_lines_patching"] = len(GV[2])
    tab(NV[0], NV[1], NV[2], 0, [432, 50, 64, 114])
    boxes[-2]["box"]["num_lines_presentation"] = len(NV[2])
    boxes[-2]["box"]["num_lines_patching"] = len(NV[2])
    boxes.append(box("obj-nota", maxclass="live.comment", numinlets=1,
                     numoutlets=0, presentation=1,
                     presentation_rect=[8, 150, 420, 18],
                     patching_rect=[20, 520, 420, 18],
                     text="KILL per via; EQ a campana; GROWL < 350 Hz. "
                          "CROSSOVER solo prototipo (B3). 0 dBu = -12 dBFS."))
    return finestra(boxes, lines, parametri)


def finestra(boxes, lines, parametri):
    p = {"patcher": {
        "fileversion": 1,
        "appversion": {"major": 9, "minor": 0, "revision": 0,
                       "architecture": "x64", "modernui": 1},
        "classnamespace": "box",
        "rect": [100.0, 100.0, 1200.0, 600.0],
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
    p["patcher"]["project"] = {
        "version": 1, "amxdtype": 1633771873, "readonly": 0,
        "devpathtype": 0, "devpath": ".", "contents": {"patchers": {}},
        "layout": {}, "searchpath": {}, "detailsvisible": 0,
        "autoorganize": 1, "hideprojectwindow": 1, "showdependencies": 1,
        "autolocalize": 0, "sortmode": 0, "viewmode": 0,
    }
    return p


def main():
    global SEMPLICE, NOME
    if "--semplice" in sys.argv[1:]:
        SEMPLICE, NOME = True, NOME + "-S"
    codice = genexpr()
    with open(os.path.join(USCITA, f"{NOME}.genexpr"), "w") as f:
        f.write(codice)
    testo = json.dumps(patch(codice), indent="\t")
    with open(os.path.join(USCITA, f"{NOME}.maxpat"), "w") as f:
        f.write(testo)
    with open(os.path.join(USCITA, f"{NOME}.amxd"), "wb") as f:
        f.write(amxd(testo))
    print(f"scritti {NOME}.genexpr ({codice.count(chr(10))} righe), "
          f".maxpat, .amxd in {USCITA}")


if __name__ == "__main__":
    main()
