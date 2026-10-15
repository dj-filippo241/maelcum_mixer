"""Genera il dispositivo MC-FILTRO (prototipo Max P1, parte 1).

Uso:  python3 proto-max/coefficienti/genera_filtro.py
Scrive in proto-max/: MC-FILTRO.genexpr, .maxpat, .amxd

I numeri vengono da filtro.py; oversampling e contenitore .amxd da
genera.py (P0). Come in P0, il codice gen~ usa solo assegnazioni,
peek/poke e funzioni senza stato proprio: prova_filtro.py lo traduce in
Python e lo fa suonare.

Pannello: FREQ, RES e DRIVE per HPF e LPF (dec. 67/102/99/110), MODO
HPF / OFF / LPF (dec. 101), CORE (a') OTA / PULITO (c-B) per B1,
PENDENZA Butterworth / Linkwitz-Riley / Bessel per B2 (q64).
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import filtro  # noqa: E402
import genera  # noqa: E402
from genera import Codice, box, linea, patcher_gen, amxd  # noqa: E402

USCITA = genera.USCITA
NOME = "MC-FILTRO"

MANOPOLE = [
    ("freq_hp", "HPF FREQ", 0.0),
    ("res_hp", "HPF RES", 0.0),
    ("drive_hp", "HPF DRIVE", 0.0),
    ("freq_lp", "LPF FREQ", 100.0),
    ("res_lp", "LPF RES", 0.0),
    ("drive_lp", "LPF DRIVE", 0.0),
]
MODO = ("modo", "MODO", ["HPF", "OFF", "LPF"], 1)
CORE = ("core", "CORE", ["OTA (a')", "PULITO (c-B)"], 0)
PENDENZA = ("pend", "PENDENZA", list(filtro.ALLINEAMENTI), 0)


def funzioni(r):
    vs = filtro.VS
    r("// allpass del 1o ordine del halfband; stato in m[i] (x), m[i+1] (y)")
    r("ap(m, i, x, c) {")
    r("\ty = c * (x - peek(m, i + 1)) + peek(m, i);")
    r("\tpoke(m, x, i);")
    r("\tpoke(m, y, i + 1);")
    r("\treturn y;")
    r("}")
    r()
    r("// guadagno a secante dell'OTA: Vs tanh(u/Vs)/u; lin = 1 -> lineare")
    r("aota(u, lin) {")
    r("\tm = max(abs(u), 0.000001);")
    r(f"\treturn lin + (1 - lin) * {vs!r} * tanh(m / {vs!r}) / m;")
    r("}")
    r()
    r("// softplus limitato (niente overflow)")
    r("spl(z) {")
    r("\treturn log(1 + exp(min(z, 30))) + max(z - 30, 0);")
    r("}")
    r()
    r("// conduttanza a secante del limitatore a diodi (4,7k + 2+2 1N4148)")
    r("alim(v) {")
    r("\tm = max(abs(v), 0.000001);")
    w, vk, g = filtro.W_LIM, filtro.VK_LIM, filtro.G_LIM
    r(f"\treturn {g!r} * {w!r} * (spl((m - {vk!r}) / {w!r})"
      f" - spl({-vk / w!r})) / m;")
    r("}")
    r()
    r("// tosatore dell'overdrive: 2,2k + 2+2 1N4148, tre passi di Newton")
    r("clipd(v) {")
    r("\ta = abs(v);")
    k2 = 2 * filtro.OD_IS * filtro.OD_R
    r(f"\tt = a / {k2!r};")
    r(f"\tw = min(a, {filtro.OD_A!r} * log(t + sqrt(t * t + 1)));")
    for _ in range(3):
        r(f"\tex = exp(w / {filtro.OD_A!r});")
        r(f"\tf = (a - w) / {filtro.OD_R!r} - {filtro.OD_IS!r} * (ex - 1 / ex);")
        r(f"\tdf = -1 / {filtro.OD_R!r}"
          f" - {filtro.OD_IS!r} * (ex + 1 / ex) / {filtro.OD_A!r};")
        r("\tw = w - f / df;")
    r("\treturn w * ((v >= 0) * 2 - 1);")
    r("}")
    r()
    r("// sezione SVF 2 poli TPT; stato in m[i..i+3] = s1, s2, hp, bp")
    r("// d = 1/Q; lin 1 = integratori lineari; lim 1 = limitatore")
    r("sez(m, i, x, g, d, lin, lim) {")
    r("\ts1 = peek(m, i);")
    r("\ts2 = peek(m, i + 1);")
    r("\tbpv = peek(m, i + 3);")
    r("\tg1 = g * aota(peek(m, i + 2), lin);")
    r("\tg2 = g * aota(bpv, lin);")
    r("\trr = d * aota(bpv, lin) + lim * alim(bpv);")
    r("\tbp = (g1 * (x - s2) + s1) / (1 + g1 * g2 + g1 * rr);")
    r("\thp = x - s2 - (g2 + rr) * bp;")
    r("\tlp = g2 * bp + s2;")
    r("\tpoke(m, bp + g1 * hp, i);")
    r("\tpoke(m, lp + g2 * bp, i + 1);")
    r("\tpoke(m, hp, i + 2);")
    r("\tpoke(m, bp, i + 3);")
    r("\treturn hp, lp;")
    r("}")
    r()


def genexpr():
    g = Codice()
    r = g.r
    r(f"// {NOME} - prototipo Max P1 (parte 1) del filtro maelcum_mixer.")
    r("// GENERATO da proto-max/coefficienti/genera_filtro.py: non modificare.")
    r("// SVF 4 poli (Q 0,541 fissa + Q 1,307 con RES), core OTA (a') col")
    r("// tetto di 1,55 V o pulito (c-B), limitatore a diodi. Banca a 4x.")
    r()
    funzioni(r)
    for nome, _, ini in MANOPOLE:
        r(f"Param {nome}({ini}, min=0, max=100);")
    r(f"Param {MODO[0]}({MODO[3]}, min=0, max=2);")
    r(f"Param {CORE[0]}({CORE[3]}, min=0, max=1);")
    r(f"Param {PENDENZA[0]}({PENDENZA[3]}, min=0, max=2);")
    pos_data = len(g.righe)
    r("@@DATA@@")
    for nome, _, ini in MANOPOLE:
        r(f"History s_{nome}({ini});")
    r(f"History s_{MODO[0]}({MODO[3]});")
    r(f"History s_{CORE[0]}({CORE[3]});")
    r(f"History s_{PENDENZA[0]}({PENDENZA[3]});")
    r()
    r("// manopole lisciate 10 ms; MODO 1 ms (rampa, dec. 80); CORE 20 ms")
    r("t1 = exp(-1 / (0.001 * samplerate));")
    r("t10 = exp(-1 / (0.010 * samplerate));")
    r("t20 = exp(-1 / (0.020 * samplerate));")
    for nome, _, _ in MANOPOLE:
        r(f"s_{nome} = {nome} + t10 * (s_{nome} - {nome});")
    r("s_modo = modo + t1 * (s_modo - modo);")
    r("s_core = core + t20 * (s_core - core);")
    r("s_pend = pend + t20 * (s_pend - pend);")
    r("w_hp = max(0, 1 - abs(s_modo));")
    r("w_off = max(0, 1 - abs(s_modo - 1));")
    r("w_lp = max(0, 1 - abs(s_modo - 2));")
    r()
    r("sr4 = samplerate * 4;")
    r("// PENDENZA: Q e frequenze delle due sezioni, scivolano in 20 ms")
    al = list(filtro.ALLINEAMENTI.values())
    for j in range(3):
        r(f"wp{j} = max(0, 1 - abs(s_pend - {j}));")
    for nome, idx, inv in (("q1i", 0, True), ("m1", 1, False),
                           ("q2i", 2, True), ("m2", 3, False)):
        termini = " + ".join(
            f"wp{j} * {(1 / a[idx] if inv else a[idx])!r}"
            for j, a in enumerate(al))
        r(f"{nome} = {termini};")
    r("dq1 = q1i;")
    for sez in ("hp", "lp"):
        r(f"// sezione {sez.upper()}: FREQ dec. 102 (a), RES dec. 102 (b)")
        r(f"th = s_freq_{sez} / 100;")
        r(f"f_{sez} = (th < 0.05) * 10 * pow(2, th / 0.05)"
          f" + (th >= 0.05) * (th <= 0.95) * 20 * pow(1000, (th - 0.05) / 0.9)"
          f" + (th > 0.95) * 20000 * pow(1.75, (th - 0.95) / 0.05);")
        op = "/" if sez == "hp" else "*"
        r(f"g_{sez}1 = tan(pi * f_{sez} {op} m1 / sr4);")
        r(f"g_{sez}2 = tan(pi * f_{sez} {op} m2 / sr4);")
        r(f"od_{sez} = pow(s_drive_{sez} / 100, {filtro.OD_ESP!r});")
        r(f"tr = s_res_{sez} / 100;")
        r(f"gr = (tr <= 0.9) * (1 - tr / 0.9)"
          f" + (tr > 0.9) * (-0.75 * (tr - 0.9) / 0.1);")
        r(f"d_{sez} = (gr > 0) * gr * q2i"
          f" + (gr <= 0) * {2 ** 0.5!r} * gr;")
    r()
    r(f"// livelli: 1,0 digitale = {filtro.LIV:.3f} V (0 dBu = -12 dBFS)")
    n_st = 0
    for lato, ingresso, uscita in (("L", "in1", "out1"), ("R", "in2", "out2")):
        r(f"// ===== lato {lato} =====")
        g.su(ingresso, f"{lato}_e", f"{lato}_o", 1, (lato, "su", 1))
        g.su(f"{lato}_e", f"{lato}_u0", f"{lato}_u1", 2, (lato, "su", 2))
        g.su(f"{lato}_o", f"{lato}_u2", f"{lato}_u3", 2, (lato, "su", 2))
        base = n_st
        for k in range(4):
            u = f"{lato}_u{k}"
            # i 4 sotto-campioni passano, in ordine, dagli STESSI stati
            r(f"x = {u} * {filtro.LIV!r} + noise() * 0.00001;")
            i = base
            out = {}
            for lin, nome_c in ((0, "a"), (1, "c")):
                for sez in ("hp", "lp"):
                    p = f"{nome_c}{sez}"
                    r(f"{p}h, {p}l = sez(st, {i}, x, g_{sez}1, dq1,"
                      f" {lin}, 0);")
                    a = f"{p}h" if sez == "hp" else f"{p}l"
                    r(f"{p}h, {p}l = sez(st, {i + 4}, {a}, g_{sez}2,"
                      f" d_{sez}, {lin}, 1);")
                    out[(nome_c, sez)] = f"{p}h" if sez == "hp" else f"{p}l"
                    i += 8
            for sez in ("hp", "lp"):
                r(f"o{sez} = (1 - s_core) * {out[('a', sez)]}"
                  f" + s_core * {out[('c', sez)]};")
                r(f"o{sez} = o{sez} + od_{sez} * ({filtro.OD_K!r}"
                  f" * clipd(2 * o{sez}) - o{sez});")
            r(f"{lato}_y{k} = (w_off * x + w_hp * ohp + w_lp * olp)"
              f" / {filtro.LIV!r};")
        n_st = base + 32
        g.giu(f"{lato}_v0", f"{lato}_y0", f"{lato}_y1", 2, (lato, "giu", 2))
        g.giu(f"{lato}_v1", f"{lato}_y2", f"{lato}_y3", 2, (lato, "giu", 2))
        g.giu(f"{lato}_w", f"{lato}_v0", f"{lato}_v1", 1, (lato, "giu", 1))
        r(f"{uscita} = {lato}_w;")
        r()
    g.righe[pos_data] = f"Data st({n_st});\nData hb({g.n_hb});"
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
            extra.update(numoutlets=3, outlettype=["", "", "float"],
                         num_lines_patching=1, num_lines_presentation=1)
        else:
            extra.update(numoutlets=2, outlettype=["", "float"])
        boxes.append(box(id_, maxclass=maxclass, parameter_enable=1,
                         patching_rect=[x, 80, 44, 48],
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
        comando(i, f"obj-d{i}", ng, nl, "live.dial",
                [8 + 56 * i, 8, 50, 48],
                {"parameter_type": 0, "parameter_mmax": 100.0,
                 "parameter_initial": [ini], "parameter_unitstyle": 5})
    for j, (ng, nl, voci, ini) in enumerate((MODO, CORE, PENDENZA)):
        comando(6 + j, f"obj-t{j}", ng, nl, "live.tab",
                [8, 60 + 24 * j, 330, 20],
                {"parameter_type": 2, "parameter_enum": voci,
                 "parameter_mmax": float(len(voci) - 1),
                 "parameter_initial": [ini], "parameter_unitstyle": 0})
    boxes.append(box("obj-nota", maxclass="live.comment", numinlets=1,
                     numoutlets=0, presentation=1,
                     presentation_rect=[8, 134, 330, 30],
                     patching_rect=[20, 440, 330, 30], linecount=2,
                     text="FREQ 0-100 % = 10 Hz-35 kHz (Xone:96). RES oltre "
                          "90 % = fischio. 0 dBu = -12 dBFS."))
    p = {"patcher": {
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
