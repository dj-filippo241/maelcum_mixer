"""Generatore di schema e PCB KiCad 10 da un netlist scritto in Python.

Uso: il file di un modulo (pcb/<modulo>/<modulo>.py) costruisce un Design e
chiama design.build(). Gira col Python di KiCad (serve pcbnew):
  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 pcb/<modulo>/<modulo>.py

Passi: schema (.kicad_sch, etichette sui pin) -> ERC e netlist da kicad-cli
-> confronto col netlist voluto -> PCB a 4 strati (piazzamento per blocchi)
-> Freerouting -> riempimento zone -> DRC. I report finiscono in out/.
"""
import json, math, os, subprocess, sys, uuid, xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(__file__))
from sexpr import parse, dump, find, first, Q

KICAD = "/Applications/KiCad/KiCad.app/Contents"
CLI = KICAD + "/MacOS/kicad-cli"
SYMDIR = KICAD + "/SharedSupport/symbols"
FPDIR = KICAD + "/SharedSupport/footprints"
JAVA = "/opt/homebrew/opt/openjdk/bin/java"
FREEROUTING = os.path.expanduser("~/Documents/ClaudeCode/kicad-prova/tools/freerouting-2.5.0.jar")
G = 1.27


def uid():
    return Q(str(uuid.uuid4()))


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


# ---------------------------------------------------------------- design
class Part:
    def __init__(self, ref, sym, value, fp, nets, block, note="", place=None, anchor=None):
        self.ref, self.sym, self.value, self.fp = ref, sym, value, fp
        self.nets, self.block, self.note, self.place = nets, block, note, place
        self.anchor = anchor     # punto dell'impronta (es. l'albero del pot) da mettere in place
        self.uuids = {}


class Design:
    def __init__(self, name, outdir, title, board=(160, 100), rev="0.1-bozza"):
        self.name, self.outdir, self.title, self.rev = name, outdir, title, rev
        self.parts, self.board, self.power = [], board, set()
        self.netclass = {}       # net -> (larghezza pista mm, nome classe)
        self.counters = {}
        self.block = "GENERALE"
        self.notes = []

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
            nets[k] = net
        p = Part(ref, sym, value, fp, nets, self.block, note, place, anchor)
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
        errs = []
        for net, conns in self.netmap().items():
            if len(conns) < 2:
                errs.append("net %s con un solo pin: %s" % (net, conns))
        return errs

    # --- schema
    def write_schematic(self):
        root = str(uuid.uuid4())
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
        su = str(uuid.uuid4())
        p.uuids[u] = su
        s = ["symbol", ["lib_id", Q(p.sym.lib_id)], ["at", x, y, 0], ["unit", u], ["body_style", 1],
             ["exclude_from_sim", "no"], ["in_bom", "no" if p.ref.startswith("#") else "yes"],
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

    def _write_project(self):
        pro = {"meta": {"filename": self.name + ".kicad_pro", "version": 3},
               "board": {"design_settings": {"defaults": {}, "rules": {"min_clearance": 0.2, "min_track_width": 0.12,
                                                                      "min_copper_edge_clearance": 0.3}}},
               "net_settings": {"classes": [{"name": "Default", "clearance": 0.2, "track_width": 0.25,
                                             "via_diameter": 0.8, "via_drill": 0.4}], "meta": {"version": 4}}}
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
        subprocess.run([CLI, "sch", "erc", "--format", "json", "--severity-all", "-o", rep, sch],
                       capture_output=True)
        erc = json.load(open(rep))
        counts = {}
        for sh in erc.get("sheets", []):
            for v in sh.get("violations", []):
                key = (v["severity"], v["type"])
                counts[key] = counts.get(key, 0) + 1
        xmlp = os.path.join(out, "netlist.xml")
        subprocess.run([CLI, "sch", "export", "netlist", "--format", "kicadxml", "-o", xmlp, sch],
                       capture_output=True)
        tree = ET.parse(xmlp)
        got = {}
        for n in tree.getroot().iter("net"):
            conns = sorted((nd.get("ref"), nd.get("pin")) for nd in n.iter("node") if not nd.get("ref").startswith("#"))
            if conns:
                got[n.get("name").lstrip("/")] = conns
        want = {k: sorted(v) for k, v in self.netmap().items()}
        diff = []
        gotsets = {tuple(v) for v in got.values()}
        for k, v in want.items():
            if tuple(v) not in gotsets:
                diff.append(k)
        return counts, diff

    # --- PCB
    def build_pcb(self, layers=4):
        import pcbnew
        mm = pcbnew.FromMM
        W, H = self.board
        X0, Y0 = 50.0, 50.0
        b = pcbnew.BOARD()
        b.SetCopperLayerCount(layers)
        if layers == 4:
            b.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)
            b.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_POWER)
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
                cname = "P%03d" % int(w * 100)
                if cname not in classes:
                    nc = pcbnew.NETCLASS(cname)
                    nc.SetTrackWidth(mm(w))
                    nc.SetClearance(mm(0.25))
                    nc.SetViaDiameter(mm(1.0))
                    nc.SetViaDrill(mm(0.5))
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
        pts = [(X0, Y0), (X0 + W, Y0), (X0 + W, Y0 + H), (X0, Y0 + H)]
        for i in range(4):
            s = pcbnew.PCB_SHAPE(b)
            s.SetShape(pcbnew.SHAPE_T_SEGMENT)
            s.SetStart(pcbnew.VECTOR2I(mm(pts[i][0]), mm(pts[i][1])))
            s.SetEnd(pcbnew.VECTOR2I(mm(pts[(i + 1) % 4][0]), mm(pts[(i + 1) % 4][1])))
            s.SetLayer(pcbnew.Edge_Cuts)
            s.SetWidth(mm(0.1))
            b.Add(s)
        gnd = getattr(self, "gnd", "AGND")
        if layers == 4:
            self._fanout(b, nets[gnd], mm, pcbnew)
        zl = [pcbnew.In1_Cu, pcbnew.In2_Cu] if layers == 4 else []
        for layer in zl:
            self._zone(b, nets[gnd], layer, X0, Y0, W, H, mm, pcbnew)
        path = os.path.join(self.outdir, self.name + ".kicad_pcb")
        b.Save(path)
        return path

    def _fanout(self, b, net, mm, pcbnew):
        """Via di massa accanto a ogni pad SMD di massa: il piano interno fa il resto."""
        n = 0
        for fp in b.GetFootprints():
            c = fp.GetPosition()
            for pad in fp.Pads():
                if pad.GetNetCode() != net.GetNetCode() or pad.GetAttribute() != pcbnew.PAD_ATTRIB_SMD:
                    continue
                pp = pad.GetPosition()
                dx, dy = pp.x - c.x, pp.y - c.y
                sz = pad.GetSize()
                if abs(dx) >= abs(dy):
                    off = pcbnew.VECTOR2I(int(math.copysign(sz.x / 2 + mm(0.75), dx or 1)), 0)
                else:
                    off = pcbnew.VECTOR2I(0, int(math.copysign(sz.y / 2 + mm(0.75), dy or 1)))
                vp = pcbnew.VECTOR2I(pp.x + off.x, pp.y + off.y)
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
        self.notes.append("fanout di massa: %d via" % n)

    def _zone(self, b, net, layer, X0, Y0, W, H, mm, pcbnew, prio=0):
        z = pcbnew.ZONE(b)
        z.SetLayer(layer)
        z.SetNet(net)
        z.SetAssignedPriority(prio)
        ol = z.Outline()
        ol.NewOutline()
        m = 0.5
        for x, y in ((X0 + m, Y0 + m), (X0 + W - m, Y0 + m), (X0 + W - m, Y0 + H - m), (X0 + m, Y0 + H - m)):
            ol.Append(mm(x), mm(y))
        z.SetLocalClearance(mm(0.3))
        z.SetMinThickness(mm(0.25))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetThermalReliefGap(mm(0.3))
        z.SetThermalReliefSpokeWidth(mm(0.4))
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
            sizes = []
            for p in items:
                x1, y1, x2, y2 = self._bbox(fps[p.ref])
                sizes.append((x2 - x1 + gap, y2 - y1 + gap))
            area = sum(w * h for w, h in sizes)
            bw = max(max(w for w, _ in sizes), math.sqrt(area * 1.2))
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
            bh = ry + rh
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
                    fp = fps[p.ref]
                    x1, y1, x2, y2 = self._bbox(fp)
                    cx, cy = fp.GetPosition().x / 1e6, fp.GetPosition().y / 1e6
                    tx = bx + rx + (cx - x1) + gap / 2
                    ty = top + vsep * (i + 1) + y0 + ry + (cy - y1) + gap / 2
                    fp.SetPosition(pcbnew.VECTOR2I(mm(tx), mm(ty)))
            bx += cw + sep

    @staticmethod
    def _bbox(fp):
        import pcbnew
        try:
            fp.BuildCourtyardCaches()
            bb = fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
            if bb.GetWidth() == 0:
                raise ValueError
        except Exception:
            bb = fp.GetBoundingBox(False)
        return (bb.GetLeft() / 1e6, bb.GetTop() / 1e6, bb.GetRight() / 1e6, bb.GetBottom() / 1e6)

    def route(self, pcb, passes=40):
        import pcbnew
        out = os.path.join(self.outdir, "out")
        dsn, ses = os.path.join(out, self.name + ".dsn"), os.path.join(out, self.name + ".ses")
        b = pcbnew.LoadBoard(pcb)
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        pcbnew.ExportSpecctraDSN(b, dsn)
        r = subprocess.run([JAVA, "-jar", FREEROUTING, "-de", dsn, "-do", ses, "-mp", str(passes)],
                           capture_output=True, text=True, timeout=3600)
        with open(os.path.join(out, "freerouting.log"), "w") as f:
            f.write(r.stdout + r.stderr)
        if not os.path.exists(ses):
            return False
        b = pcbnew.LoadBoard(pcb)
        pcbnew.ImportSpecctraSES(b, ses)
        b.Save(pcb)
        return True

    def pours(self, pcb):
        """Massa anche sui due strati esterni, poi riempimento di tutte le zone."""
        import pcbnew
        mm = pcbnew.FromMM
        b = pcbnew.LoadBoard(pcb)
        W, H = self.board
        gnd = b.FindNet(getattr(self, "gnd", "AGND"))
        for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
            z = self._zone(b, gnd, layer, 50.0, 50.0, W, H, mm, pcbnew)
            z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        b.Save(pcb)

    def drc(self, pcb):
        out = os.path.join(self.outdir, "out", "drc.json")
        subprocess.run([CLI, "pcb", "drc", "--format", "json", "--severity-all", "--schematic-parity",
                        "-o", out, pcb], capture_output=True)
        d = json.load(open(out))
        counts = {}
        for key in ("violations", "unconnected_items", "schematic_parity"):
            for v in d.get(key, []):
                k = (key, v.get("severity"), v.get("type"))
                counts[k] = counts.get(k, 0) + 1
        return counts

    def bom(self):
        rows = {}
        for p in self.parts:
            if p.ref.startswith("#"):
                continue
            k = (p.value, p.fp, p.note)
            rows.setdefault(k, []).append(p.ref)
        path = os.path.join(self.outdir, "bom.csv")
        with open(path, "w") as f:
            f.write("quantita;valore;impronta;riferimenti;nota\n")
            for (v, fp, note), refs in sorted(rows.items(), key=lambda r: r[1][0]):
                f.write("%d;%s;%s;%s;%s\n" % (len(refs), v, fp.split(":")[1], " ".join(refs), note))
        return path

    def build(self, route=True, passes=40):
        os.makedirs(self.outdir, exist_ok=True)
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
        res["bom"] = self.bom()
        res["note"] = self.notes
        with open(os.path.join(self.outdir, "out", "riepilogo.json"), "w") as f:
            json.dump(res, f, indent=1, ensure_ascii=False)
        print(json.dumps(res, indent=1, ensure_ascii=False))
        return res
