"""Generatore di schema e PCB KiCad 10 da un netlist scritto in Python.

Uso: il file di un modulo (pcb/<modulo>/<modulo>.py) costruisce un Design e
chiama design.build(). Gira col Python di KiCad (serve pcbnew):
  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 pcb/<modulo>/<modulo>.py

Passi: controllo del netlist -> schema (.kicad_sch, etichette sui pin) -> ERC e
netlist da kicad-cli -> confronto nei due sensi col netlist voluto -> PCB a 4 strati
(pezzi fissi, 100n accanto al pin, passivi a grappolo attorno all'op-amp, blocchi in
colonne) -> Freerouting -> colate di massa -> DRC -> controllo audio (audiocheck.py).
Esito PASSA / NON PASSA (codice 1) in out/riepilogo.json, coi peggioramenti sul giro prima.
Stato e piano: pcb/NOTE-generatore.md.
"""
import difflib, json, math, os, re, subprocess, sys, uuid, xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(__file__))
from sexpr import parse, dump, find, first, Q

KICAD = "/Applications/KiCad/KiCad.app/Contents"
CLI = KICAD + "/MacOS/kicad-cli"
SYMDIR = KICAD + "/SharedSupport/symbols"
FPDIR = KICAD + "/SharedSupport/footprints"
JAVA = "/opt/homebrew/opt/openjdk/bin/java"
FREEROUTING = os.path.expanduser("~/Documents/ClaudeCode/kicad-prova/tools/freerouting-2.5.0.jar")
G = 1.27

# uuid ripetibili: lo stesso netlist dà lo stesso file, così git mostra solo le differenze vere
_UIDNS = uuid.UUID("5d1c0a6e-6d61-656c-6375-6d2d70636267")
_uidstate = {"seme": "pcbgen", "n": 0}


def uid_seed(seme):
    _uidstate["seme"], _uidstate["n"] = seme, 0


def _uuid():
    _uidstate["n"] += 1
    return str(uuid.uuid5(_UIDNS, "%s/%d" % (_uidstate["seme"], _uidstate["n"])))


def uid():
    return Q(_uuid())


def _fresh(*paths):
    """Toglie i report del giro prima: un file vecchio non deve passare per un risultato nuovo."""
    for p in paths:
        if os.path.exists(p):
            os.remove(p)


def _need(path, cosa):
    if not os.path.exists(path):
        raise SystemExit("manca %s: %s" % (cosa, path))


def snap(v, g=G):
    return round(round(v / g) * g, 4)


# ---------------------------------------------------------------- simboli
_libcache = {}


def _lib(name):
    if name not in _libcache:
        with open(os.path.join(SYMDIR, name + ".kicad_sym")) as f:
            tree = parse(f.read())
        _libcache[name] = {x[1]: x for x in find(tree, "symbol")}
    return _libcache[name]


def _flatten(libname, symname):
    syms = _lib(libname)
    s = syms[symname]
    ext = first(s, "extends")
    if not ext:
        return [x for x in s]
    parent = _flatten(libname, ext[1])
    props = {p[1]: p for p in find(s, "property")}
    out = []
    for x in parent:
        if isinstance(x, list) and x[0] == "property" and x[1] in props:
            out.append(props.pop(x[1]))
        elif isinstance(x, list) and x[0] == "symbol":
            sub = list(x)
            sub[1] = Q(symname + sub[1][len(ext[1]):])
            out.append(sub)
        else:
            out.append(x)
    out[1] = Q(symname)
    out.extend(props.values())
    return out


class Symbol:
    """Simbolo appiattito: sexpr per lib_symbols e pin per unità."""

    def __init__(self, lib_id, sexpr):
        self.lib_id = lib_id
        self.sexpr = list(sexpr)
        self.sexpr[1] = Q(lib_id)
        self.units = {}          # unit -> list of pins
        self.common = []
        for sub in find(sexpr, "symbol"):
            name = sub[1]
            u, st = name.rsplit("_", 2)[-2:]
            u, st = int(u), int(st)
            if st == 2:
                continue
            for p in find(sub, "pin"):
                at = first(p, "at")
                num = first(p, "number")[1]
                nm = first(p, "name")[1]
                hidden = any(x == "hide" for x in p) or (first(p, "hide") is not None and first(p, "hide")[1] == "yes")
                pin = dict(num=str(num), name=str(nm), x=float(at[1]), y=float(at[2]),
                           ang=int(float(at[3])) if len(at) > 3 else 0, type=p[1], hidden=hidden)
                (self.common if u == 0 else self.units.setdefault(u, [])).append(pin)
        if not self.units:
            self.units[1] = []
        for u in self.units:
            self.units[u] = self.units[u] + self.common

    def pins(self):
        return {p["num"]: p for ps in self.units.values() for p in ps}


_symcache = {}


def libsym(lib_id):
    if lib_id not in _symcache:
        lib, name = lib_id.split(":")
        _symcache[lib_id] = Symbol(lib_id, _flatten(lib, name))
    return _symcache[lib_id]


def _prop(name, val, x=0, y=0, hide=False):
    p = ["property", Q(name), Q(val), ["at", x, y, 0], ["effects", ["font", ["size", 1.27, 1.27]]]]
    if hide:
        p[4].append(["hide", "yes"])
    return p


def boxsym(name, left, right, ref="U", fp="", desc=""):
    """Simbolo rettangolare: left/right = liste di (numero, nome, tipo)."""
    n = max(len(left), len(right))
    h = (n + 1) * 2.54 / 2
    w = 12.7
    body = ["symbol", Q(name + "_0_1"),
            ["rectangle", ["start", -w, snap(h, 2.54)], ["end", w, -snap(h, 2.54)],
             ["stroke", ["width", 0.254], ["type", "default"]], ["fill", ["type", "background"]]]]
    pins = ["symbol", Q(name + "_1_1")]
    for side, lst in ((0, left), (1, right)):
        for i, (num, nm, typ) in enumerate(lst):
            y = snap(h, 2.54) - 2.54 * (i + 1)
            x, ang = (-w - 5.08, 0) if side == 0 else (w + 5.08, 180)
            pins.append(["pin", typ, "line", ["at", x, y, ang], ["length", 5.08],
                         ["name", Q(nm), ["effects", ["font", ["size", 1.27, 1.27]]]],
                         ["number", Q(num), ["effects", ["font", ["size", 1.27, 1.27]]]]])
    s = ["symbol", Q(name), ["pin_names", ["offset", 1.016]], ["exclude_from_sim", "no"],
         ["in_bom", "yes"], ["on_board", "yes"],
         _prop("Reference", ref, 0, h + 2.54), _prop("Value", name, 0, -h - 2.54),
         _prop("Footprint", fp, 0, 0, True), _prop("Datasheet", "", 0, 0, True),
         _prop("Description", desc, 0, 0, True), body, pins]
    sym = Symbol("maelcum:" + name, s)
    _symcache["maelcum:" + name] = sym
    return sym


def _smd(fp):
    """Impronta a montaggio superficiale: l'unica che può stare sul retro."""
    lib = fp.split(":")[0]
    return not ("THT" in lib or "PinHeader" in lib or "PinSocket" in lib or "MountingHole" in lib
                or fp.split(":")[1].startswith("CP_Radial"))


# ---------------------------------------------------------------- design
class Part:
    def __init__(self, ref, sym, value, fp, nets, block, note="", place=None, anchor=None, side="F"):
        self.ref, self.sym, self.value, self.fp = ref, sym, value, fp
        self.nets, self.block, self.note, self.place = nets, block, note, place
        self.anchor = anchor     # punto dell'impronta (es. l'albero del pot) da mettere in place
        self.side = side         # "F" lato componenti, "B" retro (solo SMD, dec. 142)
        self.uuids = {}


class Design:
    def __init__(self, name, outdir, title, board=(160, 100), rev="0.1-bozza"):
        self.name, self.outdir, self.title, self.rev = name, outdir, title, rev
        # board=(L, H) rettangolo; board=(L, H_x0, H_xL) trapezio della dec. 158 (proposta P3 del
        # todo 170): il lato in basso (C96, backplane) resta dritto, quello in alto scende in
        # diagonale sotto il pannello inclinato. x = 0 e' il lato con H_x0 (dietro, piu' alto).
        # self.board resta (L, H massima); self.cut = di quanto il bordo in alto scende ai due capi.
        if len(board) == 3:
            L, h0, h1 = board
            hm = max(h0, h1)
            board, self.cut = (L, hm), (hm - h0, hm - h1)
        else:
            self.cut = (0.0, 0.0)
        self.parts, self.board, self.power = [], board, set()
        self.netclass = {}       # net -> (larghezza pista mm, nome classe)
        self.counters = {}
        self.block = "GENERALE"
        self.side = "F"          # il modulo scrive d.side = "B" prima dei blocchi da mettere sul retro
        self.notes = []
        self.gnd = "AGND"        # rete delle colate; il modulo la può cambiare

    def ytop(self, x):
        """y del bordo in alto alla distanza x dal lato sinistro (0 per un rettangolo).
        I pezzi fissi vicino al bordo in alto si mettono a d.ytop(x) + margine."""
        W = self.board[0]
        c0, c1 = self.cut
        return c0 + (c1 - c0) * min(max(x, 0.0), W) / W

    def _outline(self, X0, Y0, m=0.0):
        """Contorno della scheda (rettangolo o trapezio), rientrato di m mm su tutti i lati."""
        W, H = self.board
        c0, c1 = self.cut
        k = math.hypot(1.0, (c1 - c0) / W)       # il bordo in diagonale rientra di m in perpendicolare
        ya = lambda x: Y0 + c0 + (c1 - c0) * (x - X0) / W + m * k
        return [(X0 + m, ya(X0 + m)), (X0 + W - m, ya(X0 + W - m)), (X0 + W - m, Y0 + H - m), (X0 + m, Y0 + H - m)]

    def _cut_boxes(self, X0, Y0, step=4.0, pad=1.5):
        """Il triangolo tagliato via dal trapezio, come scalini di rettangoli: ostacoli per il
        piazzamento (che conosce solo rettangoli). pad = distanza minima dei pezzi dal bordo."""
        W, H = self.board
        if not any(self.cut):
            return []
        out, x = [], 0.0
        while x < W - 1e-9:
            x2 = min(W, x + step)
            y = max(self.ytop(x), self.ytop(x2))
            if y > 0:
                out.append((X0 + x, Y0 - 1, X0 + x2, Y0 + y + pad))
            x = x2
        return out

    @property
    def masse(self):
        """Le reti di riferimento: mai alimentazione, mai segnale."""
        return {self.gnd, "CTRL_GND", "CHASSIS"}

    # --- costruzione
    def part(self, prefix, lib_id, value, fp, pins, note="", place=None, ref=None, anchor=None):
        sym = libsym(lib_id) if isinstance(lib_id, str) else lib_id
        if ref is None:
            self.counters[prefix] = self.counters.get(prefix, 0) + 1
            ref = "%s%d" % (prefix, self.counters[prefix])
        allpins = sym.pins()
        nets = {}
        for k, net in pins.items():
            k = str(k)
            if k not in allpins:
                byname = [p["num"] for p in allpins.values() if p["name"] == k]
                if len(byname) != 1:
                    raise ValueError("%s: pin %s inesistente in %s" % (ref, k, sym.lib_id))
                k = byname[0]
            if k in nets:
                raise ValueError("%s: pin %s dichiarato due volte (per numero e per nome?)" % (ref, k))
            nets[k] = net
        if any(q.ref == ref for q in self.parts):
            raise ValueError("riferimento %s usato due volte" % ref)
        side = self.side
        if side == "B" and (place or not _smd(fp)):
            side = "F"           # i pezzi a foro passante e quelli fissi restano sul lato componenti
        p = Part(ref, sym, value, fp, nets, self.block, note, place, anchor, side)
        self.parts.append(p)
        return p

    def R(self, a, b, val, fp="Resistor_SMD:R_0805_2012Metric", note=""):
        return self.part("R", "Device:R", val, fp, {1: a, 2: b}, note)

    def C(self, a, b, val, fp="Capacitor_SMD:C_0805_2012Metric", note=""):
        return self.part("C", "Device:C", val, fp, {1: a, 2: b}, note)

    def CP(self, plus, minus, val, fp="Capacitor_THT:CP_Radial_D8.0mm_P3.50mm", note=""):
        return self.part("C", "Device:C_Polarized", val, fp, {1: plus, 2: minus}, note)

    def power_nets(self, *nets, width=0.8):
        for n in nets:
            self.power.add(n)
            self.netclass[n] = width

    # --- netlist
    def netmap(self):
        nm = {}
        for p in self.parts:
            for pin, net in p.nets.items():
                if net:
                    nm.setdefault(net, []).append((p.ref, pin))
        return nm

    def check(self):
        """Errori del netlist voluto, prima di disegnare: reti con un pin solo, pin di
        alimentazione dimenticati, nomi di rete quasi uguali (refusi)."""
        errs = []
        nm = self.netmap()
        for net, conns in nm.items():
            if len(conns) < 2:
                errs.append("rete %s con un solo pin: %s" % (net, conns))
        for p in self.parts:
            for q in p.sym.pins().values():
                if q["type"] in ("power_in", "power_out") and q["num"] not in p.nets:
                    errs.append("%s: pin di alimentazione %s (%s) non collegato" % (p.ref, q["num"], q["name"]))
        names = sorted(nm)
        for i, a in enumerate(names):
            for b in difflib.get_close_matches(a, names[i + 1:], n=3, cutoff=0.9):
                # stessi nomi a parte cifre o lato (S1/S2, _L/_R) sono voluti
                if re.sub(r"\d|_[LR]$|[+-]", "", a) != re.sub(r"\d|_[LR]$|[+-]", "", b):
                    errs.append("reti dai nomi quasi uguali: %s / %s (refuso?)" % (a, b))
        return errs

    # --- schema
    def write_schematic(self):
        uid_seed(self.name)
        root = _uuid()
        libs, items = {}, []
        for p in self.parts:
            libs[p.sym.lib_id] = p.sym.sexpr
        flag = libsym("power:PWR_FLAG")
        libs[flag.lib_id] = flag.sexpr
        blocks = []
        for p in self.parts:
            if p.block not in blocks:
                blocks.append(p.block)
        # griglia dei blocchi
        x0, y0, colw, maxh = 25.4, 38.1, 0, 0
        bx, by = x0, y0
        sheet_w = 1100
        for b in blocks:
            units = []
            for p in self.parts:
                if p.block != b:
                    continue
                for u, pins in sorted(p.sym.units.items()):
                    units.append((p, u, pins))
            # misura ogni unità
            cells = []
            for p, u, pins in units:
                xs = [q["x"] for q in pins] or [0]
                ys = [q["y"] for q in pins] or [0]
                lab = max([len(p.nets.get(q["num"], "") or "") for q in pins] + [2]) * 1.0 + 3
                w = (max(xs) - min(xs)) + 2 * lab + 7.62
                h = (max(ys) - min(ys)) + 10.16
                cells.append((p, u, pins, w, h, min(xs) - lab - 2.54, max(ys) + 5.08))
            # impacchetta il blocco in righe larghe al massimo 380 mm
            rowx, rowy, rowh, bw = 0, 0, 0, 0
            placed = []
            for c in cells:
                if rowx + c[3] > 380 and rowx > 0:
                    rowy += rowh
                    rowx, rowh = 0, 0
                placed.append((c, rowx, rowy))
                rowx += c[3]
                rowh = max(rowh, c[4])
                bw = max(bw, rowx)
            bh = rowy + rowh + 10
            if bx + bw > sheet_w and bx > x0:
                bx = x0
                by += maxh + 10
                maxh = 0
            items.append(["text", Q(b), ["exclude_from_sim", "no"], ["at", snap(bx), snap(by), 0],
                          ["effects", ["font", ["size", 3, 3], ["bold", "yes"]], ["justify", "left", "bottom"]],
                          ["uuid", uid()]])
            for (p, u, pins, w, h, ox, oy), rx, ry in placed:
                sx = snap(bx + rx - ox, 2.54)
                sy = snap(by + 7.62 + ry + oy, 2.54)
                items.append(self._sym_instance(p, u, sx, sy, root))
                for q in pins:
                    px, py = snap(sx + q["x"]), snap(sy - q["y"])
                    net = p.nets.get(q["num"])
                    if net:
                        items.append(self._label(net, px, py, q["ang"]))
                    else:
                        items.append(["no_connect", ["at", px, py], ["uuid", uid()]])
            bx += bw + 15
            maxh = max(maxh, bh)
        # PWR_FLAG sulle reti di alimentazione
        fx, fy = x0, by + maxh + 20
        driven = {p.nets.get(q["num"]) for p in self.parts for ps in p.sym.units.values()
                  for q in ps if q["type"] == "power_out"}
        for i, net in enumerate(sorted(self.power - driven)):
            sx, sy = snap(fx + (i % 12) * 30, 2.54), snap(fy + (i // 12) * 15, 2.54)
            fake = Part("#FLG%02d" % (i + 1), flag, "PWR_FLAG", "", {"1": net}, "")
            items.append(self._sym_instance(fake, 1, sx, sy, root))
            q = flag.units[1][0]
            items.append(self._label(net, snap(sx + q["x"]), snap(sy - q["y"]), q["ang"]))
        sch = ["kicad_sch", ["version", 20260101], ["generator", Q("eeschema")],
               ["generator_version", Q("10.0")], ["uuid", Q(root)], ["paper", Q("User"), 1189, max(841, snap(fy + 60))],
               ["title_block", ["title", Q(self.title)], ["rev", Q(self.rev)],
                ["comment", 1, Q("Generato da pcb/tools/pcbgen.py: non modificare a mano, rigenerare")]],
               ["lib_symbols"] + list(libs.values())] + items + \
              [["sheet_instances", ["path", Q("/"), ["page", Q("1")]]], ["embedded_fonts", "no"]]
        self.root = root
        path = os.path.join(self.outdir, self.name + ".kicad_sch")
        with open(path, "w") as f:
            f.write(dump(sch) + "\n")
        self._write_project()
        return path

    def _sym_instance(self, p, u, x, y, root):
        su = _uuid()
        p.uuids[u] = su
        nobom = p.ref.startswith("#") or p.sym.lib_id.startswith(("Mechanical:", "Jumper:SolderJumper"))
        s = ["symbol", ["lib_id", Q(p.sym.lib_id)], ["at", x, y, 0], ["unit", u], ["body_style", 1],
             ["exclude_from_sim", "no"], ["in_bom", "no" if nobom else "yes"],
             ["on_board", "no" if p.ref.startswith("#") else "yes"], ["dnp", "no"], ["uuid", Q(su)],
             _prop("Reference", p.ref, x, y - 3.81), _prop("Value", p.value, x, y + 3.81),
             _prop("Footprint", p.fp, x, y, True), _prop("Datasheet", "", x, y, True)]
        if p.note:
            s.append(_prop("Nota", p.note, x, y, True))
        for q in p.sym.units[u]:
            s.append(["pin", Q(q["num"]), ["uuid", uid()]])
        s.append(["instances", ["project", Q(self.name), ["path", Q("/" + root), ["reference", Q(p.ref)], ["unit", u]]]])
        return s

    def _label(self, net, x, y, ang):
        la = {0: 180, 180: 0, 90: 270, 270: 90}[ang % 360]
        just = "right" if la in (180, 270) else "left"
        return ["global_label", Q(net), ["shape", "passive"], ["at", x, y, la], ["fields_autoplaced", "yes"],
                ["effects", ["font", ["size", 1.0, 1.0]], ["justify", just]], ["uuid", uid()]]

    @staticmethod
    def _classname(w):
        return "P%03d" % round(w * 100)

    @staticmethod
    def _classrules(w):
        """Distanza, via e foro di una classe di pista larga w: una fonte sola per la scheda
        e per il .kicad_pro. Piste sottili (passo fine, logica): via e distanze come il
        default; con la via da 1 mm Freerouting non chiudeva SETP, +5V e CTRL_GND (master).
        Prima il .kicad_pro dava 0,25 mm anche alle sottili: Freerouting tracciava a 0,2 e il
        DRC contava 36 errori di distanza (FX-SEND, 2026-11-04)."""
        thin = w < 0.6
        return {"clearance": 0.2 if thin else 0.25, "via_diameter": 0.8 if thin else 1.0,
                "via_drill": 0.4 if thin else 0.5}

    def _write_project(self):
        # le classi di rete vanno nel progetto: se si ritocca in KiCad, router e DRC le conoscono
        classes = [{"name": "Default", "clearance": 0.2, "track_width": 0.25,
                    "via_diameter": 0.8, "via_drill": 0.4}]
        for w in sorted(set(self.netclass.values())):
            c = {"name": self._classname(w), "track_width": w}
            c.update(self._classrules(w))
            classes.append(c)
        assign = [{"netclass": self._classname(w), "pattern": net} for net, w in sorted(self.netclass.items())]
        pro = {"meta": {"filename": self.name + ".kicad_pro", "version": 3},
               "board": {"design_settings": {"defaults": {}, "rules": {"min_clearance": 0.2, "min_track_width": 0.12,
                                                                      "min_copper_edge_clearance": 0.3}}},
               "net_settings": {"classes": classes, "netclass_patterns": assign, "meta": {"version": 4}}}
        with open(os.path.join(self.outdir, self.name + ".kicad_pro"), "w") as f:
            json.dump(pro, f, indent=2)
        custom = [s.sexpr for s in _symcache.values() if s.lib_id.startswith("maelcum:")]
        lib = ["kicad_symbol_lib", ["version", 20251024], ["generator", Q("pcbgen")]]
        for s in custom:
            s2 = list(s)
            s2[1] = Q(str(s[1]).split(":")[1])
            lib.append(s2)
        with open(os.path.join(self.outdir, "maelcum.kicad_sym"), "w") as f:
            f.write(dump(lib) + "\n")
        with open(os.path.join(self.outdir, "sym-lib-table"), "w") as f:
            f.write('(sym_lib_table\n\t(version 7)\n\t(lib (name "maelcum")(type "KiCad")(uri "${KIPRJMOD}/maelcum.kicad_sym")(options "")(descr "simboli di maelcum"))\n)\n')

    # --- verifica dello schema con kicad-cli
    def erc_and_compare(self, sch):
        out = os.path.join(self.outdir, "out")
        os.makedirs(out, exist_ok=True)
        rep = os.path.join(out, "erc.json")
        xmlp = os.path.join(out, "netlist.xml")
        _fresh(rep, xmlp)
        subprocess.run([CLI, "sch", "erc", "--format", "json", "--severity-all", "-o", rep, sch],
                       capture_output=True)
        _need(rep, "il report ERC (kicad-cli non è partito?)")
        erc = json.load(open(rep))
        counts = {}
        for sh in erc.get("sheets", []):
            for v in sh.get("violations", []):
                key = (v["severity"], v["type"])
                counts[key] = counts.get(key, 0) + 1
        subprocess.run([CLI, "sch", "export", "netlist", "--format", "kicadxml", "-o", xmlp, sch],
                       capture_output=True)
        _need(xmlp, "il netlist esportato dallo schema")
        tree = ET.parse(xmlp)
        got = {}
        for n in tree.getroot().iter("net"):
            conns = sorted((nd.get("ref"), nd.get("pin")) for nd in n.iter("node") if not nd.get("ref").startswith("#"))
            if conns:
                got[n.get("name").lstrip("/")] = conns
        want = {k: sorted(v) for k, v in self.netmap().items()}
        # confronto nei due sensi: una rete voluta che manca, e una rete nata nello schema
        # (due pin finiti sullo stesso punto). I pin liberi (reti a un pin) non contano.
        diff = []
        gotsets = {tuple(v) for v in got.values()}
        wantsets = {tuple(v) for v in want.values()}
        for k, v in want.items():
            if tuple(v) not in gotsets:
                diff.append("manca nello schema: " + k)
        for k, v in got.items():
            if len(v) > 1 and tuple(v) not in wantsets:
                diff.append("rete in più nello schema: %s %s" % (k, v))
        return counts, diff

    # --- PCB
    def build_pcb(self, layers=4):
        import pcbnew
        mm = pcbnew.FromMM
        W, H = self.board
        X0, Y0 = 50.0, 50.0
        b = pcbnew.BOARD()
        b.SetCopperLayerCount(layers)
        # inner_signal (dec. 142, SMD sui due lati): In2 diventa uno strato di piste, la massa
        # resta piena su In1; con i due lati pieni di pezzi F e B non bastano per le piste
        sig2 = getattr(self, "inner_signal", False)
        if layers == 4:
            b.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)
            b.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_SIGNAL if sig2 else pcbnew.LT_POWER)
        ds = b.GetDesignSettings()
        ds.m_TrackMinWidth = mm(0.15)
        ds.m_CopperEdgeClearance = mm(0.3)
        ds.m_MinClearance = mm(0.2)
        nets = {}
        for net in sorted(self.netmap()):
            ni = pcbnew.NETINFO_ITEM(b, net)
            b.Add(ni)
            nets[net] = ni
        # classi di rete
        try:
            ns = ds.m_NetSettings
            classes = {}
            for net, w in self.netclass.items():
                cname = self._classname(w)
                if cname not in classes:
                    nc = pcbnew.NETCLASS(cname)
                    nc.SetTrackWidth(mm(w))
                    cr = self._classrules(w)
                    nc.SetClearance(mm(cr["clearance"]))
                    nc.SetViaDiameter(mm(cr["via_diameter"]))
                    nc.SetViaDrill(mm(cr["via_drill"]))
                    ns.SetNetclass(cname, nc)
                    classes[cname] = nc
                ns.SetNetclassPatternAssignment(net, cname)
            dflt = ns.GetDefaultNetclass()
            dflt.SetTrackWidth(mm(0.25))
            dflt.SetClearance(mm(0.2))
            dflt.SetViaDiameter(mm(0.8))
            dflt.SetViaDrill(mm(0.4))
        except Exception as e:
            self.notes.append("classi di rete non impostate: %s" % e)
        # impronte
        fps = {}
        for p in self.parts:
            lib, name = p.fp.split(":")
            fp = pcbnew.FootprintLoad(os.path.join(FPDIR, lib + ".pretty"), name)
            if fp is None:
                raise ValueError("impronta mancante: " + p.fp)
            fp.SetReference(p.ref)
            fp.SetValue(p.value)
            fp.SetFPIDAsString(p.fp)
            if p.note:
                # la nota sta anche sull'impronta: sennò il DRC segnala la differenza di campi
                fp.SetField("Nota", p.note)
                try:
                    fp.GetField("Nota").SetVisible(False)
                except Exception:
                    pass
            if p.uuids:
                fp.SetPath(pcbnew.KIID_PATH("/" + p.uuids[min(p.uuids)]))
            for pad in fp.Pads():
                n = p.nets.get(pad.GetNumber())
                if n:
                    pad.SetNet(nets[n])
            b.Add(fp)
            fps[p.ref] = fp
        self._place(b, fps, X0, Y0, W, H, mm)
        # contorno
        pts = self._outline(X0, Y0)
        for i in range(4):
            s = pcbnew.PCB_SHAPE(b)
            s.SetShape(pcbnew.SHAPE_T_SEGMENT)
            s.SetStart(pcbnew.VECTOR2I(mm(pts[i][0]), mm(pts[i][1])))
            s.SetEnd(pcbnew.VECTOR2I(mm(pts[(i + 1) % 4][0]), mm(pts[(i + 1) % 4][1])))
            s.SetLayer(pcbnew.Edge_Cuts)
            s.SetWidth(mm(0.1))
            b.Add(s)
        gnd = self.gnd
        if layers == 4:
            self._fanout(b, nets[gnd], mm, pcbnew)
        if getattr(self, "link_pairs", False):
            self._link_pairs(b, mm, pcbnew)
        zl = ([pcbnew.In1_Cu] if sig2 else [pcbnew.In1_Cu, pcbnew.In2_Cu]) if layers == 4 else []
        for layer in zl:
            self._zone(b, nets[gnd], layer, X0, Y0, W, H, mm, pcbnew)
        self._edge_keepout(b, X0, Y0, W, H, mm, pcbnew, cut=self.cut)
        path = os.path.join(self.outdir, self.name + ".kicad_pcb")
        b.Save(path)
        return path

    @staticmethod
    def _edge_keepout(b, X0, Y0, W, H, mm, pcbnew, m=0.8, cut=(0.0, 0.0)):
        """Fascia di 0,8 mm lungo il bordo senza piste né via: Freerouting non conosce la
        distanza dal bordo (0,3 mm) e ci passava a 0,28 (master segnale, 2026-10-28).
        Col trapezio la fascia in alto copre il triangolo tagliato a gradini da 4 mm, solo
        rettangoli: con un poligono in diagonale Freerouting non finiva in un'ora (canale, 9/11)."""
        c0, c1 = cut
        k = m * math.hypot(1.0, (c1 - c0) / W)
        tops, x = [], 0.0
        while x < W - 1e-9:
            x2 = min(W, x + 4.0)
            tops.append((X0 + x, Y0, X0 + x2, Y0 + max(c0 + (c1 - c0) * x / W, c0 + (c1 - c0) * x2 / W) + k))
            x = x2
        for x1, y1, x2, y2 in tops + [(X0, Y0 + H - m, X0 + W, Y0 + H),
                                      (X0, Y0, X0 + m, Y0 + H), (X0 + W - m, Y0, X0 + W, Y0 + H)]:
            z = pcbnew.ZONE(b)
            z.SetIsRuleArea(True)
            z.SetLayerSet(pcbnew.LSET.AllCuMask())
            z.SetDoNotAllowTracks(True)
            z.SetDoNotAllowVias(True)
            z.SetDoNotAllowZoneFills(False)
            z.SetDoNotAllowPads(False)
            z.SetDoNotAllowFootprints(False)
            ol = z.Outline()
            ol.NewOutline()
            for x, y in ((x1, y1), (x2, y1), (x2, y2), (x1, y2)):
                ol.Append(mm(x), mm(y))
            b.Add(z)

    def _fanout(self, b, net, mm, pcbnew):
        """Via di massa accanto a ogni pad SMD di massa: il piano interno fa il resto."""
        n, saltate, messe = 0, 0, []
        altri = [pd for f in b.GetFootprints() for pd in f.Pads() if pd.GetNetCode() != net.GetNetCode()]
        for fp in b.GetFootprints():
            c = fp.GetPosition()
            for pad in fp.Pads():
                if pad.GetNetCode() != net.GetNetCode() or pad.GetAttribute() != pcbnew.PAD_ATTRIB_SMD:
                    continue
                pp = pad.GetPosition()
                dx, dy = pp.x - c.x, pp.y - c.y
                sz = pad.GetSize()
                if abs(dx) >= abs(dy):
                    sgn, half = math.copysign(1, dx or 1), sz.x / 2
                    offs = [pcbnew.VECTOR2I(int(sgn * (half + mm(0.75))), 0),
                            pcbnew.VECTOR2I(int(-sgn * (half + mm(0.75))), 0)]
                else:
                    sgn, half = math.copysign(1, dy or 1), sz.y / 2
                    offs = [pcbnew.VECTOR2I(0, int(sgn * (half + mm(0.75)))),
                            pcbnew.VECTOR2I(0, int(-sgn * (half + mm(0.75))))]
                # d.fanout_more (default spento): se i due posti sull'asse sono occupati, anche di
                # traverso e piu' lontano. Un pad di massa senza via resta un'isola di colata
                # (master, giri 9 e 11: C78, C53 -> unconnected_items)
                if getattr(self, "fanout_more", False):
                    hx, hy = sz.x / 2, sz.y / 2
                    for dist in (0.75, 1.1, 1.5):
                        for ux, uy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            offs.append(pcbnew.VECTOR2I(int(ux * (hx + mm(dist))), int(uy * (hy + mm(dist)))))
                # prima verso l'esterno; se cade su un pad di un'altra rete (es. il pin di massa
                # dell'ADG1434 accanto al suo 100n) verso l'interno, sotto il corpo del chip
                vp = None
                for off in offs:
                    cand = pcbnew.VECTOR2I(pp.x + off.x, pp.y + off.y)
                    mid = pcbnew.VECTOR2I((pp.x + cand.x) // 2, (pp.y + cand.y) // 2)
                    if any(o.HitTest(cand, mm(0.3 + 0.25)) or o.HitTest(mid, mm(0.2 + 0.2)) for o in altri):
                        continue
                    if any((cand.x - q.x) ** 2 + (cand.y - q.y) ** 2 < mm(0.85) ** 2 for q in messe):
                        continue
                    vp = cand
                    break
                if vp is None:
                    saltate += 1
                    continue
                messe.append(vp)
                v = pcbnew.PCB_VIA(b)
                v.SetPosition(vp)
                v.SetWidth(mm(0.6))
                v.SetDrill(mm(0.3))
                v.SetNet(net)
                b.Add(v)
                t = pcbnew.PCB_TRACK(b)
                t.SetStart(pp)
                t.SetEnd(vp)
                t.SetWidth(mm(0.4))
                t.SetLayer(pad.GetLayer() if pad.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu)
                t.SetNet(net)
                b.Add(t)
                n += 1
        self.notes.append("fanout di massa: %d via, %d senza posto libero" % (n, saltate))

    def _link_pairs(self, b, mm, pcbnew, dmax=4.0):
        """d.link_pairs = True (default spento): unisce con una pista dritta due pad vicini della
        stessa impronta e della stessa rete, a foro passante (pin doppi del C96, cursore e capo di un trimmer).
        Freerouting li lascia spesso aperti (master, 2026-11-04: RV4-2/RV4-3, J1-a3/a4, J4).
        La pista si salta se passa a meno di 0,3 mm da un pad di un'altra rete. Masse escluse."""
        n = 0
        tutti = [pd for f in b.GetFootprints() for pd in f.Pads()]
        for fp in b.GetFootprints():
            per = {}
            for pad in fp.Pads():
                net = pad.GetNetname()
                # solo foro passante: Freerouting conta come aperta una pista fra due pin SMD
                # che non ha tracciato lui (giro 11 del master: 11 falsi aperti), il DRC no
                if pad.GetAttribute() != pcbnew.PAD_ATTRIB_PTH:
                    continue
                if net and net not in self.masse and not net.startswith("unconnected-"):
                    per.setdefault(net, []).append(pad)
            for net, pads in per.items():
                for a, c in zip(pads, pads[1:]):
                    pa, pc = a.GetPosition(), c.GetPosition()
                    if math.hypot(pa.x - pc.x, pa.y - pc.y) > mm(dmax):
                        continue
                    w = mm(self.netclass.get(net, 0.25))
                    lay = pcbnew.F_Cu if a.IsOnLayer(pcbnew.F_Cu) and c.IsOnLayer(pcbnew.F_Cu) else (
                        pcbnew.B_Cu if a.IsOnLayer(pcbnew.B_Cu) and c.IsOnLayer(pcbnew.B_Cu) else None)
                    if lay is None:
                        continue
                    ok = True
                    for k in range(1, 20):
                        q = pcbnew.VECTOR2I(pa.x + (pc.x - pa.x) * k // 20, pa.y + (pc.y - pa.y) * k // 20)
                        if any(o.GetNetCode() != a.GetNetCode() and o.IsOnLayer(lay) and o.HitTest(q, w // 2 + mm(0.3))
                               for o in tutti):
                            ok = False
                            break
                    if not ok:
                        continue
                    t = pcbnew.PCB_TRACK(b)
                    t.SetStart(pa)
                    t.SetEnd(pc)
                    t.SetWidth(w)
                    t.SetLayer(lay)
                    t.SetNet(a.GetNet())
                    b.Add(t)
                    n += 1
                    self._linked = getattr(self, "_linked", set())
                    ra, rc = "%s-%s" % (fp.GetReference(), a.GetNumber()), "%s-%s" % (fp.GetReference(), c.GetNumber())
                    self._linked |= {(ra, rc), (rc, ra)}
        self.notes.append("piste fra pad gemelli: %d" % n)

    def _zone(self, b, net, layer, X0, Y0, W, H, mm, pcbnew, prio=0):
        z = pcbnew.ZONE(b)
        z.SetLayer(layer)
        z.SetNet(net)
        z.SetAssignedPriority(prio)
        ol = z.Outline()
        ol.NewOutline()
        for x, y in self._outline(X0, Y0, 0.5):
            ol.Append(mm(x), mm(y))
        z.SetLocalClearance(mm(0.3))
        z.SetMinThickness(mm(0.25))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetThermalReliefGap(mm(0.3))
        z.SetThermalReliefSpokeWidth(mm(0.4))
        # i pezzi di colata staccati da tutto (isole) si tolgono: rame flottante e
        # «collegamenti mancanti» fra frammenti della stessa zona
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        b.Add(z)
        return z

    def _place(self, b, fps, X0, Y0, W, H, mm):
        """Pezzi fissi: place=(x, y, rot) = centro dei pad. Gli altri: blocchi in colonne."""
        import pcbnew
        gap = getattr(self, "gap", 2.0)
        free, fixed_boxes = [], []
        for p in self.parts:
            fp = fps[p.ref]
            if p.place and p.anchor:
                # place = posizione dell'ancora (coordinate dell'impronta, rotazione 0)
                x, y, rot = p.place
                fp.SetOrientationDegrees(rot)
                a = math.radians(rot)
                ax, ay = p.anchor
                rx, ry = ax * math.cos(a) + ay * math.sin(a), -ax * math.sin(a) + ay * math.cos(a)
                fp.SetPosition(pcbnew.VECTOR2I(mm(X0 + x - rx), mm(Y0 + y - ry)))
                fixed_boxes.append(self._bbox(fp))
            elif p.place:
                x, y, rot = p.place
                fp.SetOrientationDegrees(rot)
                px = [pd.GetPosition() for pd in fp.Pads()]
                cx = (min(v.x for v in px) + max(v.x for v in px)) / 2e6
                cy = (min(v.y for v in px) + max(v.y for v in px)) / 2e6
                pos = fp.GetPosition()
                fp.SetPosition(pcbnew.VECTOR2I(mm(X0 + x - cx + pos.x / 1e6), mm(Y0 + y - cy + pos.y / 1e6)))
                fixed_boxes.append(self._bbox(fp))
            else:
                free.append(p)
        # trapezio: il triangolo tagliato e' un ostacolo come i pezzi fissi
        fixed_boxes += self._cut_boxes(X0, Y0)
        # disaccoppiamento: i 100n legati a un chip escono dal piazzamento a blocchi e
        # viaggiano col loro chip, a ~2 mm dal pin di alimentazione
        groups = self._decaps()
        for ic, caps in groups.items():
            self._attach(fps, ic, caps)
        # grappoli: i passivi di una cella attorno al pin del loro op-amp
        if getattr(self, "cluster_auto", True):
            for ic, items in self._clusters(groups).items():
                self._cluster_place(fps, ic, items, groups.get(ic, []))
                groups.setdefault(ic, []).extend((r, pin) for r, pin, _ in items)
        attached = {c for caps in groups.values() for c, _ in caps}
        free = [p for p in free if p.ref not in attached]
        # retro (dec. 142): i gruppi col chip sul retro si ribaltano attorno al chip, poi si
        # piazzano dopo il lato componenti, lontano dai pezzi a foro passante
        side = {p.ref: p.side for p in self.parts}
        fpn = {p.ref: p.fp for p in self.parts}
        back = [p for p in free if side[p.ref] == "B"
                and all(_smd(fpn[r]) for r in [c for c, _ in groups.get(p.ref, [])])]
        back_refs = {p.ref for p in back}
        free = [p for p in free if p.ref not in back_refs]
        for p in back:
            c = fps[p.ref].GetPosition()
            for r in [p.ref] + [c2 for c2, _ in groups.get(p.ref, [])]:
                fps[r].Flip(c, pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        # blocchi vicino al loro connettore (todo 196); se uno non trova posto, colonne
        # nell'ordine del file come prima (d.place_mode = "colonne" le forza)
        placed = False
        if getattr(self, "place_mode", "connettori") == "connettori":
            placed = self._place_near(fps, free, groups, fixed_boxes, X0, Y0, W, H, mm, gap)
        if not placed:
            self._place_columns(fps, free, groups, fixed_boxes, X0, Y0, W, H, mm, gap)
        if back:
            self._place_back(fps, back, groups, X0, Y0, W, H, mm, gap)

    def _place_columns(self, fps, free, groups, fixed_boxes, X0, Y0, W, H, mm, gap):
        """Blocchi in colonne da sinistra, nell'ordine del file (piazzamento fino al 2026-11-03)."""
        import pcbnew
        top, bot = Y0 + 2, Y0 + H - 2
        for (x1, y1, x2, y2) in fixed_boxes:
            if (y1 + y2) / 2 < Y0 + H / 2:
                top = max(top, y2 + 2)
            else:
                bot = min(bot, y1 - 2)
        blocks = []
        for p in free:
            if p.block not in blocks:
                blocks.append(p.block)
        cols, col, colh = [], [], 0
        for blk in blocks:
            items = [p for p in free if p.block == blk]
            sizes = self._sizes(fps, items, groups, gap)
            area = sum(w * h for w, h in sizes)
            bw = max(max(w for w, _ in sizes), math.sqrt(area * 1.2))
            pos, used, bh = self._rows(sizes, items, bw)
            if col and colh + bh > bot - top:
                cols.append(col)
                col, colh = [], 0
            col.append((pos, used, bh, colh))
            colh += bh + 3
        if col:
            cols.append(col)
        widths = [max(u for _, u, _, _ in c) for c in cols]
        spare = (W - 4) - sum(widths)
        if spare < 0:
            self.overflow = True
            self.notes.append("piazzamento: servono %.0f mm in più di larghezza" % -spare)
            spare = 0
        sep = spare / max(1, len(cols) + 1)
        bx = X0 + 2 + sep
        for c, cw in zip(cols, widths):
            hsum = c[-1][3] + c[-1][2]
            vsep = max(0, (bot - top) - hsum) / (len(c) + 1)
            for i, (pos, used, bh, y0) in enumerate(c):
                for p, rx, ry in pos:
                    x1, y1, x2, y2 = self._gbox(fps, p.ref, groups)
                    dx = bx + rx + gap / 2 - x1
                    dy = top + vsep * (i + 1) + y0 + ry + gap / 2 - y1
                    for r in [p.ref] + [c for c, _ in groups.get(p.ref, [])]:
                        fp = fps[r]
                        q = fp.GetPosition()
                        fp.SetPosition(pcbnew.VECTOR2I(int(q.x + mm(dx)), int(q.y + mm(dy))))
            bx += cw + sep

    def _sizes(self, fps, items, groups, gap):
        out = []
        for p in items:
            x1, y1, x2, y2 = self._gbox(fps, p.ref, groups)
            out.append((x2 - x1 + gap, y2 - y1 + gap))
        return out

    @staticmethod
    def _rows(sizes, items, bw):
        """Pezzi di un blocco in file larghe bw: [(pezzo, x, y)], larghezza usata, altezza."""
        rx, ry, rh, used = 0, 0, 0, 0
        pos = []
        for (w, h), p in zip(sizes, items):
            if rx + w > bw and rx > 0:
                ry += rh
                rx, rh = 0, 0
            pos.append((p, rx, ry))
            rx += w
            rh = max(rh, h)
            used = max(used, rx)
        return pos, used, ry + rh

    def _place_near(self, fps, free, groups, fixed_boxes, X0, Y0, W, H, mm, gap):
        """Ogni blocco nel posto libero più vicino ai pin dei connettori fissi con cui ha una
        rete in comune (C96, cavo dei pot, bottoni); un blocco senza connettori va vicino ai
        blocchi già messi con cui parla. Prima i blocchi più legati ai connettori; il blocco
        dei regolatori per ultimo, lontano dal cavo (d.power_from_cable mm, 60 di default).
        Ritorna False, senza toccare niente, se un blocco non trova posto."""
        import pcbnew
        quiet = self.masse
        rules = getattr(self, "audio_rules", None) or {}
        regs = set(rules.get("regolatori", [])) or {p.ref for p in self.parts
                                                     if p.sym.lib_id.startswith("Regulator_")}
        cavo = re.compile(rules["cavo"]) if rules.get("cavo") else None
        nets = {p.ref: p.nets for p in self.parts}
        fixpads = []
        for p in self.parts:
            if p.place:
                for pd in fps[p.ref].Pads():
                    n = p.nets.get(pd.GetNumber())
                    if n and n not in quiet:
                        q = pd.GetPosition()
                        fixpads.append((n, q.x / 1e6, q.y / 1e6))
        cable = [(x, y) for n, x, y in fixpads if cavo and cavo.match(n)]
        blocks = []
        for p in free:
            if p.block not in blocks:
                blocks.append(p.block)
        members = {b: [r for p in free if p.block == b for r in [p.ref] + [c for c, _ in groups.get(p.ref, [])]]
                   for b in blocks}
        # reti dei pezzi del blocco: un passivo legato al chip di un altro blocco non sposta il suo
        bnets = {b: {n for p in self.parts if p.block == b for n in p.nets.values() if n and n not in quiet}
                 for b in blocks}
        links = {b: [(x, y) for n, x, y in fixpads if n in bnets[b]] for b in blocks}
        power = [b for b in blocks if any(r in regs for r in members[b])]
        order = sorted([b for b in blocks if b not in power], key=lambda b: -len(links[b]))
        # d.power_first: i regolatori scelgono per primi (vicino ai pin RAW); di default per ultimi
        order = power + order if getattr(self, "power_first", False) else order + power
        saved = {r: fps[r].GetPosition() for b in blocks for r in members[b]}
        obst = [(x1 - 1, y1 - 1, x2 + 1, y2 + 1) for x1, y1, x2, y2 in fixed_boxes]
        placedpads = []
        lim = getattr(self, "power_from_cable", 60.0)
        m, step = getattr(self, "block_margin", 3.0), 1.5     # corridoio per le piste fra due blocchi

        def near(px, py, x1, y1, x2, y2):
            dx = max(x1 - px, 0, px - x2)
            dy = max(y1 - py, 0, py - y2)
            return math.hypot(dx, dy)

        for b in order:
            items = [p for p in free if p.block == b]
            # pin dei connettori peso 3, pin dei blocchi già messi peso 1
            pts = [(x, y, 3.0) for x, y in links[b]] + [(x, y, 1.0) for n, x, y in placedpads
                                                         if n in bnets[b] and n not in self.power]
            if not pts:
                pts = [(X0 + W / 2, Y0 + H / 2, 1.0)]
            wsum = sum(k for _, _, k in pts)
            sizes = self._sizes(fps, items, groups, gap)
            base = math.sqrt(sum(w * h for w, h in sizes) * 1.2)
            minw = max(w for w, _ in sizes)
            best, shapes = None, {}
            for f in (0.5, 0.75, 1.0, 1.5, 2.2, 3.2):
                bw = min(max(minw, base * f), max(minw, W - 4))
                pos, used, bh = self._rows(sizes, items, bw)
                shapes[(round(used, 1), round(bh, 1))] = (pos, used + m, bh + m)
            # un blocco grande stretto e lungo fa da muro alle piste: lati al più 1:3, le forme
            # più lunghe solo se nessun'altra trova posto (FX-SEND, alimentazione 24 x 120: -18V aperta)
            asp = getattr(self, "block_aspect", 3.0)
            good = [s for s in shapes.values() if max(s[1], s[2]) <= 40 or max(s[1] / s[2], s[2] / s[1]) <= asp]
            bad = [s for s in shapes.values() if s not in good]
            for tier in (good, bad):
                if best is not None:
                    break
                for pos, w, h in tier:
                    x = X0 + 1
                    while x + w <= X0 + W - 1 + 1e-6:
                        y = Y0 + 1
                        while y + h <= Y0 + H - 1 + 1e-6:
                            hit = [o for o in obst if x < o[2] and o[0] < x + w and y < o[3] and o[1] < y + h]
                            if hit:
                                y = max(y + step, min(o[3] for o in hit))
                                continue
                            cost = sum(k * near(px, py, x, y, x + w, y + h) for px, py, k in pts) / wsum
                            if b in power and cable:
                                dc = min(near(px, py, x, y, x + w, y + h) for px, py in cable)
                                cost += 2 * max(0.0, lim - dc)
                            if best is None or cost < best[0] - 1e-9:
                                best = (cost, x, y, w, h, pos)
                            y += step
                        x += step
            if best is None:
                for r, q in saved.items():
                    fps[r].SetPosition(q)
                self.notes.append("piazzamento vicino ai connettori: nessun posto per «%s», colonne" % b)
                return False
            cost, bx, by, w, h, pos = best
            for p, rx, ry in pos:
                x1, y1, x2, y2 = self._gbox(fps, p.ref, groups)
                dx = bx + m / 2 + rx + gap / 2 - x1
                dy = by + m / 2 + ry + gap / 2 - y1
                for r in [p.ref] + [c for c, _ in groups.get(p.ref, [])]:
                    q = fps[r].GetPosition()
                    fps[r].SetPosition(pcbnew.VECTOR2I(int(q.x + mm(dx)), int(q.y + mm(dy))))
            obst.append((bx, by, bx + w, by + h))
            for r in members[b]:
                for pd in fps[r].Pads():
                    n = nets[r].get(pd.GetNumber())
                    if n and n not in quiet:
                        q = pd.GetPosition()
                        placedpads.append((n, q.x / 1e6, q.y / 1e6))
            self.notes.append("blocco «%s»: x %.0f-%.0f, y %.0f-%.0f, %d pin di connettore"
                              % (b[:40], bx - X0, bx + w - X0, by - Y0, by + h - Y0, len(links[b])))
        return True

    def _place_back(self, fps, back, groups, X0, Y0, W, H, mm, gap):
        """Retro: ogni gruppo nel primo posto libero, colonna per colonna da sinistra, nell'ordine
        del netlist (i blocchi restano insieme). Ostacoli: i pezzi a foro passante del lato
        componenti (i loro pin escono sotto) e i gruppi già messi sul retro."""
        import pcbnew
        mine = {r for p in back for r in [p.ref] + [c for c, _ in groups.get(p.ref, [])]}
        obst = list(self._cut_boxes(X0, Y0))
        for p in self.parts:
            if p.ref not in mine and (not _smd(p.fp) or p.place):
                x1, y1, x2, y2 = self._bbox(fps[p.ref])
                obst.append((x1 - 1, y1 - 1, x2 + 1, y2 + 1))
        step = 1.0
        for p in back:
            x1, y1, x2, y2 = self._gbox(fps, p.ref, groups)
            w, h = x2 - x1 + gap, y2 - y1 + gap
            spot, x = None, X0 + 2
            while spot is None and x + w <= X0 + W - 2:
                y = Y0 + 2
                while y + h <= Y0 + H - 2:
                    hit = [o for o in obst if x < o[2] and o[0] < x + w and y < o[3] and o[1] < y + h]
                    if not hit:
                        spot = (x, y)
                        break
                    y = max(o[3] for o in hit)
                x += step
            if spot is None:
                self.overflow = True
                self.notes.append("retro: nessun posto per %s" % p.ref)
                continue
            dx, dy = spot[0] + gap / 2 - x1, spot[1] + gap / 2 - y1
            for r in [p.ref] + [c for c, _ in groups.get(p.ref, [])]:
                q = fps[r].GetPosition()
                fps[r].SetPosition(pcbnew.VECTOR2I(int(q.x + mm(dx)), int(q.y + mm(dy))))
            obst.append((spot[0], spot[1], spot[0] + w, spot[1] + h))
        self.notes.append("retro: %d gruppi" % len(back))

    def _decaps(self):
        """Lega ogni 100n fra un'alimentazione e la massa al chip dello stesso blocco che ha
        quella alimentazione su un pin, nell'ordine in cui sono scritti nel netlist.
        Ritorna {ref del chip: [(ref del C, pin del chip), ...]}."""
        if not getattr(self, "decap_auto", True):
            return {}
        gnds = self.masse
        free_pins = {}           # (blocco, rete) -> [(chip, pin)] ancora senza C
        groups = {}
        for p in self.parts:
            if p.ref.startswith("U") and not p.place:
                for q in p.sym.pins().values():
                    net = p.nets.get(q["num"])
                    if q["type"] == "power_in" and net and net not in gnds:
                        free_pins.setdefault((p.block, net), []).append((p.ref, q["num"]))
            elif p.ref.startswith("C") and p.value.startswith("100n") and not p.place:
                nets = [n for n in p.nets.values() if n]
                sup = [n for n in nets if n not in gnds]
                if len(nets) == 2 and len(sup) == 1:
                    cand = free_pins.get((p.block, sup[0]))
                    if cand:
                        ic, pin = cand.pop(0)
                        groups.setdefault(ic, []).append((p.ref, pin))
        return groups

    def _attach(self, fps, ic, caps):
        """Mette ogni C accanto al suo pin, verso l'esterno del chip, col pad
        dell'alimentazione rivolto al pin. Due C sullo stesso lato si scalano in fuori."""
        import pcbnew
        mm = pcbnew.FromMM
        u = fps[ic]
        c0 = u.GetPosition()
        nets = {pt.ref: pt.nets for pt in self.parts if pt.ref in [c for c, _ in caps]}
        side_n = {}
        for cref, pin in caps:
            pad = [pd for pd in u.Pads() if pd.GetNumber() == pin][0]
            pp = pad.GetPosition()
            dx, dy = pp.x - c0.x, pp.y - c0.y
            horiz = abs(dx) >= abs(dy)
            sgn = 1 if (dx if horiz else dy) >= 0 else -1
            k = side_n[(horiz, sgn)] = side_n.get((horiz, sgn), -1) + 1
            cf = fps[cref]
            cf.SetOrientationDegrees(0 if horiz else 90)
            cf.SetPosition(pcbnew.VECTOR2I(0, 0))
            cpads = list(cf.Pads())
            span = max(abs(p.GetPosition().x if horiz else p.GetPosition().y) +
                       (p.GetSize().x / 2) for p in cpads)
            half_ic = (pad.GetSize().x if horiz else pad.GetSize().y) / 2
            off = half_ic + mm(0.6) + span + k * (2 * span + mm(0.6))
            if horiz:
                tgt = pcbnew.VECTOR2I(int(pp.x + sgn * off), pp.y)
            else:
                tgt = pcbnew.VECTOR2I(pp.x, int(pp.y + sgn * off))
            cf.SetPosition(tgt)
            sup = [n for n in nets[cref].values() if n not in self.masse][0]
            near = min(cf.Pads(), key=lambda p: (p.GetPosition().x - pp.x) ** 2 + (p.GetPosition().y - pp.y) ** 2)
            if near.GetNetname() != sup and nets[cref].get(near.GetNumber()) != sup:
                cf.SetOrientationDegrees(180 if horiz else 270)
        self.notes.append("disaccoppiamento: %s con %s" % (ic, ", ".join(c for c, _ in caps)))

    def _clusters(self, groups):
        """Assegna ogni R e C (non elettrolitico) a un op-amp: prima per un pin di segnale
        in comune (stesso blocco, poi un altro blocco), poi per una rete in comune con un
        passivo già nel grappolo (stesso blocco). Ritorna {chip: [(ref, pin, padre)]}:
        pin = pin del chip a cui si lega, padre = passivo intermedio o None."""
        regs = set((getattr(self, "audio_rules", None) or {}).get("regolatori", []))
        taken = {c for caps in groups.values() for c, _ in caps}
        blk = {p.ref: p.block for p in self.parts}
        quiet = self.power | self.masse
        ics = [p for p in self.parts if p.ref.startswith("U") and not p.place
               and p.ref not in regs and len(p.nets) >= 8]
        sig = {}
        for p in ics:
            for pin, net in sorted(p.nets.items(), key=lambda kv: int(kv[0]) if kv[0].isdigit() else 0):
                if net and net not in quiet:
                    sig.setdefault(net, []).append((p.ref, pin))
        pas = [p for p in self.parts if p.ref[0] in "RC" and not p.place and p.ref not in taken
               and len(p.nets) == 2 and p.sym.lib_id != "Device:C_Polarized"]
        clus, member = {}, {}
        for p in pas:
            hits = [h for n in p.nets.values() if n in sig for h in sig[n]]
            hits.sort(key=lambda h: blk[h[0]] != p.block)
            if hits:
                ic, pin = hits[0]
                clus.setdefault(ic, []).append((p.ref, pin, None))
                member[p.ref] = ic
        bynet = {}
        for p in pas:
            for n in p.nets.values():
                if n and n not in quiet:
                    bynet.setdefault(n, []).append(p)
        for p in pas:
            if p.ref in member:
                continue
            for n in p.nets.values():
                par = [q for q in bynet.get(n, []) if q.ref in member and q.block == p.block]
                if par:
                    ic = member[par[0].ref]
                    clus[ic].append((p.ref, None, par[0].ref))
                    member[p.ref] = ic
                    break
        return clus

    def _cluster_place(self, fps, ic, items, caps):
        """Ogni passivo accanto al suo pin (o al passivo padre), sul lato del pin, col pad
        della rete in comune verso il pin. Se il posto è occupato prova più in là lungo il
        lato, poi una fila più in fuori."""
        import pcbnew
        mm = pcbnew.FromMM
        u = fps[ic]
        c0 = u.GetPosition()
        nets = {p.ref: p.nets for p in self.parts}
        boxes = [self._bbox(u)] + [self._bbox(fps[c]) for c, _ in caps]
        info = {}            # ref -> (punto di partenza, direzione verso fuori)

        def free_at(cf):
            x1, y1, x2, y2 = self._bbox(cf)
            g = getattr(self, "cluster_gap", 0.5)    # spazio per le piste fra due passivi
            return all(x2 + g <= a or x1 - g >= c or y2 + g <= b or y1 - g >= d
                       for a, b, c, d in boxes)

        for ref, pin, par in sorted(items, key=lambda it: it[2] is not None):
            cf = fps[ref]
            if par is None:
                pad = [pd for pd in u.Pads() if pd.GetNumber() == pin][0]
                pp = pad.GetPosition()
                dx, dy = pp.x - c0.x, pp.y - c0.y
                horiz = abs(dx) >= abs(dy)
                sgn = 1 if (dx if horiz else dy) >= 0 else -1
                start = (pp.x / 1e6, pp.y / 1e6)
                lead = ((pad.GetSize().x if horiz else pad.GetSize().y) / 2e6) + 0.5
                shared = nets[ic][pin]
            else:
                if par not in info:
                    continue
                (sx, sy), horiz, sgn, plead = info[par]
                pf = fps[par]
                far = max(pf.Pads(), key=lambda q: sgn * (q.GetPosition().x if horiz else q.GetPosition().y))
                start = (far.GetPosition().x / 1e6, far.GetPosition().y / 1e6)
                lead = 0.6
                shared = [n for n in nets[ref].values() if n in nets[par].values() and n not in self.masse][0]
            cf.SetOrientationDegrees(0 if horiz else 90)
            cf.SetPosition(pcbnew.VECTOR2I(0, 0))
            half = max(abs(q.GetPosition().x if horiz else q.GetPosition().y) +
                       (q.GetSize().x / 2) for q in cf.Pads()) / 1e6
            length = 2 * half + getattr(self, "cluster_gap", 0.5) + 0.4
            ok = False
            for row in range(6):
                out = lead + half + row * length
                for k in range(0, 13):
                    side = (k + 1) // 2 * (1 if k % 2 else -1) * 0.75
                    x = start[0] + (sgn * out if horiz else side)
                    y = start[1] + (side if horiz else sgn * out)
                    cf.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
                    if free_at(cf):
                        ok = True
                        break
                if ok:
                    break
            near = min(cf.Pads(), key=lambda q: (q.GetPosition().x / 1e6 - start[0]) ** 2 +
                       (q.GetPosition().y / 1e6 - start[1]) ** 2)
            if nets[ref].get(near.GetNumber()) != shared:
                cf.SetOrientationDegrees((0 if horiz else 90) + 180)
            boxes.append(self._bbox(cf))
            info[ref] = (start, horiz, sgn, lead)
        self.notes.append("grappolo: %s con %d passivi" % (ic, len(items)))

    def _gbox(self, fps, ref, groups):
        """Riquadro di un pezzo, o del chip col suoi condensatori."""
        boxes = [self._bbox(fps[r]) for r in [ref] + [c for c, _ in groups.get(ref, [])]]
        return (min(b[0] for b in boxes), min(b[1] for b in boxes),
                max(b[2] for b in boxes), max(b[3] for b in boxes))

    @staticmethod
    def _bbox(fp):
        import pcbnew
        try:
            fp.BuildCourtyardCaches()
            bb = fp.GetCourtyard(pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd).BBox()
            if bb.GetWidth() == 0:
                raise ValueError
        except Exception:
            bb = fp.GetBoundingBox(False)
        return (bb.GetLeft() / 1e6, bb.GetTop() / 1e6, bb.GetRight() / 1e6, bb.GetBottom() / 1e6)

    def route(self, pcb, passes=40):
        """Freerouting. Ritorna {"ok", "aperti": {rete: n}}: i collegamenti lasciati aperti.
        Quelli di massa li chiudono le colate; quelli di segnale sono un errore."""
        import pcbnew
        _need(JAVA, "Java (brew install openjdk)")
        _need(FREEROUTING, "il jar di Freerouting")
        out = os.path.join(self.outdir, "out")
        dsn, ses = os.path.join(out, self.name + ".dsn"), os.path.join(out, self.name + ".ses")
        log = os.path.join(out, "freerouting.log")
        _fresh(dsn, ses, log)
        b = pcbnew.LoadBoard(pcb)
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        pcbnew.ExportSpecctraDSN(b, dsn)
        if any(self.cut):
            # trapezio: per Freerouting il contorno è il rettangolo che lo contiene; il triangolo
            # tagliato lo chiudono le fasce a gradini di _edge_keepout. Col contorno in diagonale
            # Freerouting era 3-13 volte più lento e non finiva (canale, 9/11)
            W, H = self.board
            txt = open(dsn).read()
            rect = "(boundary\n      (path pcb 0  %d %d  %d %d  %d %d  %d %d  %d %d)\n    )" % (
                50000, -50000, 50000 + W * 1000, -50000, 50000 + W * 1000, -(50000 + H * 1000),
                50000, -(50000 + H * 1000), 50000, -50000)
            txt, n = re.subn(r"\(boundary\s*\(path pcb 0[^)]*\)\s*\)", rect, txt, count=1)
            if n != 1:
                raise ValueError("contorno non trovato nel .dsn")
            open(dsn, "w").write(txt)
        try:
            r = subprocess.run([JAVA, "-jar", FREEROUTING, "-de", dsn, "-do", ses, "-mp", str(passes)],
                               capture_output=True, text=True, timeout=3600)
        except subprocess.TimeoutExpired:
            return {"ok": False, "aperti": {}, "errore": "Freerouting non ha finito in un'ora"}
        with open(log, "w") as f:
            f.write(r.stdout + r.stderr)
        if r.returncode != 0 or not os.path.exists(ses):
            return {"ok": False, "aperti": {}, "errore": "Freerouting uscito con codice %d" % r.returncode}
        # l'ultimo elenco «Net 'X' (n unrouted connections)» del log
        aperti = {}
        for m in re.finditer(r"Net '([^']+)' \((\d+) unrouted", r.stdout + r.stderr):
            aperti[m.group(1)] = int(m.group(2))
        # le piste di _link_pairs Freerouting le conta come aperte anche se ci sono (il DRC no):
        # quei collegamenti si tolgono dal conto. Senza d.link_pairs non cambia niente.
        linked = getattr(self, "_linked", set())
        if linked:
            aperti = {}
            for m in re.finditer(r"Net '([^']+)' \(\d+ unrouted[^\n]*\n((?:\s+- [^\n]+\n)*)", r.stdout + r.stderr):
                conn = re.findall(r"- (\S+)\s+->\s+(\S+)", m.group(2))
                k = sum(1 for c in conn if c not in linked)
                if k:
                    aperti[m.group(1)] = k
                else:
                    aperti.pop(m.group(1), None)
        b = pcbnew.LoadBoard(pcb)
        pcbnew.ImportSpecctraSES(b, ses)
        b.Save(pcb)
        return {"ok": True, "aperti": aperti}

    def pours(self, pcb):
        """Massa anche sui due strati esterni, poi riempimento di tutte le zone."""
        import pcbnew
        mm = pcbnew.FromMM
        b = pcbnew.LoadBoard(pcb)
        W, H = self.board
        gnd = b.FindNet(self.gnd)
        for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
            z = self._zone(b, gnd, layer, 50.0, 50.0, W, H, mm, pcbnew)
            z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        b.Save(pcb)

    # avvisi di parità che il generatore produce apposta: pin liberi del connettore
    # (lo schema li chiama «unconnected-…», il pad resta senza rete) e staffe dei pot
    ATTESI = (("schematic_parity", "net_conflict", re.compile(r"\(unconnected-")),
              ("schematic_parity", "net_conflict", re.compile(r"pad MP ")),)

    def drc(self, pcb):
        out = os.path.join(self.outdir, "out", "drc.json")
        _fresh(out)
        subprocess.run([CLI, "pcb", "drc", "--format", "json", "--severity-all", "--schematic-parity",
                        "-o", out, pcb], capture_output=True)
        _need(out, "il report DRC")
        d = json.load(open(out))
        counts = {}
        for key in ("violations", "unconnected_items", "schematic_parity"):
            for v in d.get(key, []):
                text = v.get("description", "") + " " + " ".join(i.get("description", "") for i in v.get("items", []))
                atteso = any(key == a and v.get("type") == t and rx.search(text) for a, t, rx in self.ATTESI)
                k = ("atteso" if atteso else key, v.get("severity"), v.get("type"))
                counts[k] = counts.get(k, 0) + 1
        return counts

    def bom(self):
        rows = {}
        for p in self.parts:
            if p.ref.startswith("#") or p.sym.lib_id.startswith(("Mechanical:", "Jumper:SolderJumper")):
                continue     # fori e ponticelli a stagno: rame della scheda, non pezzi da comprare
            k = (p.value, p.fp, p.note)
            rows.setdefault(k, []).append(p.ref)
        path = os.path.join(self.outdir, "bom.csv")
        with open(path, "w") as f:
            f.write("quantita;valore;impronta;riferimenti;nota\n")
            for (v, fp, note), refs in sorted(rows.items(), key=lambda r: r[1][0]):
                f.write("%d;%s;%s;%s;%s\n" % (len(refs), v, fp.split(":")[1], " ".join(refs), note))
        return path

    def verdetto(self, res, prev):
        """Gli errori che fermano la scheda, e cosa è peggiorato rispetto al giro prima."""
        colate = (self.gnd, "CHASSIS")     # reti che chiudono le colate e i fori
        err = list(res["controllo_netlist"]) + list(res["reti_diverse_schema"])
        err += ["ERC %s: %d" % (k, v) for k, v in res["erc"].items() if k.startswith("error")]
        r = res["routing"]
        if isinstance(r, dict):
            if not r["ok"]:
                err.append("routing non riuscito: %s" % r.get("errore", ""))
            sig = {n: c for n, c in r["aperti"].items() if n not in colate}
            if sig:
                err.append("Freerouting ha lasciato aperte reti di segnale: %s" % sig)
        for k, v in res["drc"].items():
            if k.startswith("violations/error") or k.startswith("unconnected_items"):
                err.append("DRC %s: %d" % (k, v))
            elif k.startswith("schematic_parity/"):
                err.append("parità schema-PCB inattesa %s: %d" % (k, v))
        peggio = []
        if prev:
            for sez in ("erc", "drc"):
                for k, v in res[sez].items():
                    if not k.startswith("atteso") and v > prev.get(sez, {}).get(k, 0):
                        peggio.append("%s %s: %d -> %d" % (sez, k, prev.get(sez, {}).get(k, 0), v))
            a, p = res.get("controllo_audio", {}).get("conteggio", {}), prev.get("controllo_audio", {}).get("conteggio", {})
            for k, v in a.items():
                if v > p.get(k, v):
                    peggio.append("controllo audio %s: %d -> %d" % (k, p[k], v))
        return err, peggio

    def audio(self, pcb):
        """Controllo audio dopo il routing (pcb/tools/audiocheck.py), con le regole del modulo."""
        try:
            import audiocheck
        except ImportError:
            return {"saltato": "manca pcb/tools/audiocheck.py"}
        return audiocheck.check(pcb, getattr(self, "audio_rules", None))

    def build_schema(self):
        """Solo schema, ERC, confronto col netlist e distinta: nessuna PCB. Riepilogo a parte
        (riepilogo-schema.json), così un giro di solo schema non si confronta con uno completo."""
        os.makedirs(os.path.join(self.outdir, "out"), exist_ok=True)
        rp = os.path.join(self.outdir, "out", "riepilogo-schema.json")
        prev = json.load(open(rp)) if os.path.exists(rp) else None
        res = {"modulo": self.name, "componenti": len(self.parts), "reti": len(self.netmap())}
        res["controllo_netlist"] = self.check()
        sch = self.write_schematic()
        erc, diff = self.erc_and_compare(sch)
        res["erc"] = {"%s/%s" % k: v for k, v in erc.items()}
        res["reti_diverse_schema"] = diff
        res["routing"], res["drc"] = "saltato (solo schema)", {}
        res["bom"] = os.path.relpath(self.bom(), self.outdir)
        res["note"] = self.notes
        err, peggio = self.verdetto(res, prev)
        res["esito"] = "SCHEMA NON PASSA" if err else "SCHEMA PASSA"
        res["errori"], res["peggiorato"] = err, peggio
        with open(rp, "w") as f:
            json.dump(res, f, indent=1, ensure_ascii=False)
        print(json.dumps(res, indent=1, ensure_ascii=False))
        print("\n%s: %s" % (self.name, res["esito"]))
        for e in err:
            print("  ERRORE  " + e)
        for e in peggio:
            print("  PEGGIO  " + e)
        if err:
            sys.exit(1)
        return res

    def build(self, route=True, passes=40, pcb=None):
        """Tutta la catena. Esce con codice 1 se la scheda non passa: un errore non resta
        sepolto nel JSON. Con pcb=False (o --solo-schema) si ferma a schema, ERC e distinta:
        l'esito dice «SCHEMA PASSA», non che la scheda passa."""
        if pcb is None:
            pcb = "--solo-schema" not in sys.argv
        if not pcb:
            return self.build_schema()
        os.makedirs(os.path.join(self.outdir, "out"), exist_ok=True)
        rp = os.path.join(self.outdir, "out", "riepilogo.json")
        prev = json.load(open(rp)) if os.path.exists(rp) else None
        res = {"modulo": self.name, "componenti": len(self.parts), "reti": len(self.netmap())}
        res["controllo_netlist"] = self.check()
        sch = self.write_schematic()
        erc, diff = self.erc_and_compare(sch)
        res["erc"] = {"%s/%s" % k: v for k, v in erc.items()}
        res["reti_diverse_schema"] = diff
        pcb = self.build_pcb()
        res["routing"] = self.route(pcb, passes) if route else "saltato"
        self.pours(pcb)
        res["drc"] = {"%s/%s/%s" % k: v for k, v in self.drc(pcb).items()}
        if route:
            res["controllo_audio"] = self.audio(pcb)
        res["bom"] = os.path.relpath(self.bom(), self.outdir)
        res["note"] = self.notes
        err, peggio = self.verdetto(res, prev)
        res["esito"] = "NON PASSA" if err else "PASSA"
        res["errori"], res["peggiorato"] = err, peggio
        with open(rp, "w") as f:
            json.dump(res, f, indent=1, ensure_ascii=False)
        print(json.dumps(res, indent=1, ensure_ascii=False))
        print("\n%s: %s" % (self.name, res["esito"]))
        for e in err:
            print("  ERRORE  " + e)
        for e in peggio:
            print("  PEGGIO  " + e)
        if err:
            sys.exit(1)
        return res
