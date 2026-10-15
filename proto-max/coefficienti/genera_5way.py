"""Genera il dispositivo MC-5WAY (prototipo Max P2).

Uso:  python3 proto-max/coefficienti/genera_5way.py
Scrive in proto-max/: MC-5WAY.genexpr, .maxpat, .amxd

I numeri vengono da fiveway.py; oversampling e contenitore .amxd da
genera.py (P0). Come in P0 e P1, il codice gen~ usa solo assegnazioni,
peek/poke e funzioni di righe semplici: prova_5way.py lo traduce in
Python e lo fa suonare.

Pannello (five-way §1 e §9, dec. 85/88/99): per ogni via un KILL
(taglio netto); per ogni banda EQ GAIN, POSITION e WIDTH; GROWL e
NASTRO. Solo prototipo: CROSSOVER A/B/C/D per B3 (q67).

Nomi: le variabili d0 e d1 appartengono al downsampling di genera.py
(Codice.giu). Il P1 le ha usate per altro e ha rotto il canale R.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import fiveway as fw  # noqa: E402
import genera  # noqa: E402
from genera import Codice, box, linea, patcher_gen, amxd  # noqa: E402

USCITA = genera.USCITA
NOME = "MC-5WAY"

KILL = [(f"k_{v.lower()}", f"KILL {v}") for v in fw.VIE]
GAIN = [(f"g_{i + 1}", f"EQ{i + 1} GAIN") for i in range(5)]
POS = [(f"p_{i + 1}", f"EQ{i + 1} POS") for i in range(5)]
WID = [(f"w_{i + 1}", f"EQ{i + 1} WIDTH") for i in range(5)]
SAT = [("growl", "GROWL"), ("nastro", "NASTRO")]
XO = ("xo", "CROSSOVER", list(fw.VARIANTI_XO))
WIDTH_VOCI = ["Q3", "Q1", "Q0.5"]
KILL_VOCI = ["ON", "KILL"]

# stati nel Data sv: 2 per SVF. Per lato: spina 8, LP 8, AP 6, celle 5,
# GROWL 1 = 28 SVF. Nel Data sa: HP del GROWL (1), HP-JFET non serve
# (il condensatore e vc), JFET: vs2, idd, vc come scarti dal riposo.
SVF_LATO = 28
SA_LATO = 4
VS20, ID0, VD0 = fw.jfet_riposo()


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
        r(f"Param {nome}(1, min=0, max=2);")
    for nome, _ in SAT:
        r(f"Param {nome}(0, min=0, max=100);")
    r(f"Param {XO[0]}(0, min=0, max={len(XO[2]) - 1});")
    r(f"Data sv({2 * 2 * SVF_LATO});")
    r(f"Data sa({2 * SA_LATO});")
    pos_data = len(g.righe)
    r("@@DATA@@")
    lisci = [n for n, _ in GAIN + POS + WID + SAT] + [XO[0]]
    for nome in lisci:
        ini = {"w": 1, "g": 50, "p": 50}.get(nome[0], 0)
        r(f"History s_{nome}({ini});")
    r()
    r("// manopole lisciate 10 ms; WIDTH 1 ms; CROSSOVER 20 ms; KILL netti")
    r("t1 = exp(-1 / (0.001 * samplerate));")
    r("t10 = exp(-1 / (0.010 * samplerate));")
    r("t20 = exp(-1 / (0.020 * samplerate));")
    for nome in lisci:
        t = {"w": "t1", "x": "t20"}.get(nome[0], "t10")
        r(f"s_{nome} = {nome} + {t} * (s_{nome} - {nome});")
    r("sr4 = samplerate * 4;")
    r()
    r("// CROSSOVER: le 4 varianti di B3, frequenze che scivolano in 20 ms")
    varianti = list(fw.VARIANTI_XO.values())
    for j in range(len(varianti)):
        r(f"wx{j} = max(0, 1 - abs(s_xo - {j}));")
    for c in range(4):
        termini = " + ".join(f"wx{j} * {v[c]!r}"
                             for j, v in enumerate(varianti))
        r(f"gx{c} = tan(pi * ({termini}) / sr4);")
    r()
    r("// KILL: 1 = via aperta (interruttore, taglio netto: dec. 88)")
    for v, (nome, _) in enumerate(KILL):
        r(f"a{v} = 1 - {nome};")
    r()
    r("// celle EQ: GAIN (famiglia eq-serie §10), POSITION esponenziale,")
    r("// WIDTH Q 3 / 1 / 0,5")
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
        wq = [1 / q for q in fw.Q_WIDTH]
        r(f"ke{n} = max(0, 1 - abs(s_w_{n})) * {wq[0]!r}"
          f" + max(0, 1 - abs(s_w_{n} - 1)) * {wq[1]!r}"
          f" + max(0, 1 - abs(s_w_{n} - 2)) * {wq[2]!r};")
    r(f"mg = s_growl / 100;")
    r(f"mt = s_nastro / 100;")
    r(f"glp = tan(pi * {fw.FX_GROWL!r} / sr4);")
    r(f"ghg = tan(pi * {fw.F_HP_G!r} / sr4);")
    r(f"kcb = 1 / (sr4 * {fw.J_CB!r});")
    r(f"kc = 1 / (sr4 * {10e-6 * fw.J_RTS!r});")
    kq = 1 / fw.Q_BW
    liv = fw.LIV * fw.PAD
    r()
    r(f"// livelli: 1,0 digitale = {fw.LIV:.3f} V; dominio interno -6 dB")
    for lato, ingresso, uscita in (("L", "in1", "out1"), ("R", "in2", "out2")):
        b0 = 0 if lato == "L" else 2 * SVF_LATO
        sa0 = 0 if lato == "L" else SA_LATO
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
            r("ya = a0 * v0 + a1 * v1 + a2 * v2 + a3 * v3 + a4 * p4;")
            r("// EQ creativo: 5 campane in serie")
            for n in range(1, 6):
                r(f"ya = ya + b{n} * ke{n} * svbp(sv, {i}, ya, ge{n}, ke{n});")
                i += 2
            r("// GROWL (sotto 350 Hz) e NASTRO, volt del dominio interno")
            r(f"xa = ya * {liv!r};")
            r(f"lw = svlp(sv, {i}, xa, glp, {kq!r});")
            i += 2
            r(f"dg = {fw.KG!r} * hp1(sa, {sa0}, clipg(lw), ghg) - lw;")
            r("y1 = xa + mg * dg;")
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
            r(f"{lato}_y{k} = (y1 + mt * dt) / {liv!r};")
            assert i == b0 + 2 * SVF_LATO
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
        dial(GAIN[i][0], GAIN[i][1], 50.0, [8 + col * i, 24, 54, 48])
        dial(POS[i][0], POS[i][1], 50.0, [8 + col * i, 74, 54, 48])
        tab(WID[i][0], WID[i][1], WIDTH_VOCI, 1, [8 + col * i, 126, 54, 18])
    for j, (ng, nl) in enumerate(SAT):
        dial(ng, nl, 0.0, [312 + 60 * j, 24, 54, 48])
    tab(XO[0], XO[1], XO[2], 0, [312, 78, 114, 66])
    boxes[-2]["box"]["num_lines_presentation"] = 4
    boxes[-2]["box"]["num_lines_patching"] = 4
    boxes.append(box("obj-nota", maxclass="live.comment", numinlets=1,
                     numoutlets=0, presentation=1,
                     presentation_rect=[8, 148, 420, 18],
                     patching_rect=[20, 520, 420, 18],
                     text="KILL per via; EQ a campana; GROWL < 350 Hz. "
                          "CROSSOVER solo prototipo (B3). 0 dBu = -12 dBFS."))
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
