"""Schema leggibile di una scheda: stesso netlist dello schema del generatore, disegnato per chi legge.

Uso (Python di KiCad):
  .../python3 pcb/tools/leggibile.py pcb/mono/mono.py [altro modulo.py ...]

Esce in pcb/<modulo>/leggibile/: <nome>.kicad_sch, <nome>.pdf, erc.json, riepilogo.json.
Lo schema del generatore (quello che alimenta la PCB) non cambia: questo è un secondo disegno
dello stesso netlist, controllato con lo stesso confronto nei due sensi. Esito LEGGIBILE PASSA /
NON PASSA (codice 1).

Regole del disegno:
- alimentazioni e masse come simboli (freccia, massa), mai etichette;
- i passivi stanno attaccati al pin dell'integrato che toccano, coi fili: in serie lungo il pin,
  in derivazione verso massa o verso un'alimentazione;
- un'etichetta solo dove il filo non arriva: piccola se la rete resta nel blocco, a riquadro se
  va in un altro blocco;
- i blocchi del modulo (d.block) in fila, nell'ordine in cui il modulo li scrive.
"""
import json, math, os, runpy, subprocess, sys, xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbgen
from pcbgen import libsym, uid, uid_seed, _uuid, Q, CLI, dump

G = 2.54
FONT = 1.27
CH = 1.05          # larghezza stimata di un carattere a 1,27 mm


def sn(v, g=1.27):
    return round(round(v / g) * g, 4)


# ------------------------------------------------------------ geometria dei simboli
def rotv(x, y, r):
    """Vettore della libreria (y in su) ruotato di r gradi in senso antiorario."""
    c, s = round(math.cos(math.radians(r))), round(math.sin(math.radians(r)))
    return x * c - y * s, x * s + y * c


def pin_at(sx, sy, r, q):
    x, y = rotv(q["x"], q["y"], r)
    return sn(sx + x), sn(sy - y)


def pin_out(r, q):
    """Direzione verso fuori del pin, in coordinate dello schema (y in giù)."""
    a = math.radians((q["ang"] + 180 + r) % 360)
    return round(math.cos(a)), -round(math.sin(a))


def ang_of(d):
    """Angolo (0 destra, 90 su, 180 sinistra, 270 giù) di un versore dello schema."""
    return {(1, 0): 0, (0, -1): 90, (-1, 0): 180, (0, 1): 270}[d]


# ------------------------------------------------------------ alimentazioni
def kind_of(net, masse):
    if net in masse or "GND" in net:
        return "gnd"
    if net.startswith("-") or net.endswith("-"):
        return "neg"
    return "pos"


PWRSYM = {"gnd": "power:GND", "pos": "power:+15V", "neg": "power:-15V"}


def body_of(k):
    """Dove sta il corpo del simbolo di alimentazione rispetto al suo pin (dalla libreria)."""
    q = libsym(PWRSYM[k]).units[1][0]
    o = pin_out(0, q)
    return (-o[0], -o[1])


class Sheet:
    """Raccoglie gli oggetti dello schema in coordinate assolute."""

    def __init__(self, d):
        self.d = d
        self.items = []
        self.libs = {}
        self.points = []        # (x, y, rete) punti di collegamento
        self.segs = []          # (x1, y1, x2, y2, rete)
        self.labels = []        # (x, y, rete, globale, direzione)
        self.npwr = 0

    def symbol(self, p, u, x, y, r, refpos=None):
        self.libs[p.sym.lib_id] = p.sym.sexpr
        x, y = sn(x), sn(y)
        if refpos is None:
            refpos = (x + 2.54, y - 1.27, "left"), (x + 2.54, y + 1.27, "left")
        (rx, ry, rj), (vx, vy, vj) = refpos
        fa = getattr(self, "field_angle", 0)
        nobom = p.ref.startswith("#") or p.sym.lib_id.startswith(("Mechanical:", "Jumper:SolderJumper"))
        s = ["symbol", ["lib_id", Q(p.sym.lib_id)], ["at", x, y, r], ["unit", u], ["body_style", 1],
             ["exclude_from_sim", "no"], ["in_bom", "no" if nobom else "yes"],
             ["on_board", "no" if p.ref.startswith("#") else "yes"], ["dnp", "no"], ["uuid", uid()],
             prop("Reference", p.ref, rx, ry, rj, ang=fa), prop("Value", p.value, vx, vy, vj, ang=fa),
             prop("Footprint", p.fp, x, y, hide=True), prop("Datasheet", "", x, y, hide=True)]
        if p.note:
            s.append(prop("Nota", p.note, x, y, hide=True))
        for q in p.sym.units[u]:
            s.append(["pin", Q(q["num"]), ["uuid", uid()]])
        s.append(["instances", ["project", Q(self.d.name),
                                ["path", Q("/" + self.root), ["reference", Q(p.ref)], ["unit", u]]]])
        self.items.append(s)
        for q in p.sym.units[u]:
            px, py = pin_at(x, y, r, q)
            self.points.append((px, py, p.nets.get(q["num"])))

    def wire(self, a, b, net):
        if a == b:
            return
        self.items.append(["wire", ["pts", ["xy", a[0], a[1]], ["xy", b[0], b[1]]],
                           ["stroke", ["width", 0], ["type", "default"]], ["uuid", uid()]])
        self.segs.append((a[0], a[1], b[0], b[1], net))

    def junction(self, a):
        self.items.append(["junction", ["at", a[0], a[1]], ["diameter", 0],
                           ["color", 0, 0, 0, 0], ["uuid", uid()]])

    def label(self, a, net, out, glob):
        self.labels.append((a[0], a[1], net, glob, out))

    def power(self, a, net, out, sideways=False):
        """Simbolo di alimentazione al punto a; out = direzione verso fuori del pin o del filo.
        sideways: il simbolo si gira verso fuori (pin fitti di connettori e integrati)."""
        k = kind_of(net, self.d.masse)
        body = body_of(k)
        x, y = a
        r = 0
        if sideways and out[1] == 0:
            q = libsym(PWRSYM[k]).units[1][0]
            r = [rr for rr in (0, 90, 180, 270) if pin_out(rr, q) == (-out[0], -out[1])][0]
            body = out
        elif out == (-body[0], -body[1]):
            # il corpo cadrebbe sopra il pezzo: simbolo capovolto
            r, body = 180, (-body[0], -body[1])
        elif out != body:
            b = (x + out[0] * G, y + out[1] * G)
            self.wire(a, b, net)
            x, y = b
        sym = libsym(PWRSYM[k])
        self.libs[sym.lib_id] = sym.sexpr
        self.npwr += 1
        ref = "#PWR%03d" % self.npwr
        vy = y + (4.6 if body == (0, 1) else -4.6)
        vx, vj = x, "center"
        if body[1] == 0:
            vx, vy, vj = x + body[0] * 5.5, y, ("left" if body[0] > 0 else "right")
        self.items.append(["symbol", ["lib_id", Q(sym.lib_id)], ["at", sn(x), sn(y), r], ["unit", 1],
                           ["body_style", 1], ["exclude_from_sim", "no"], ["in_bom", "yes"], ["on_board", "yes"],
                           ["dnp", "no"], ["uuid", uid()],
                           prop("Reference", ref, x, y, hide=True), prop("Value", net, vx, vy, vj, ang=FIELD_ANGLE.get(r, 0)),
                           prop("Footprint", "", x, y, hide=True), prop("Datasheet", "", x, y, hide=True),
                           ["pin", Q("1"), ["uuid", uid()]],
                           ["instances", ["project", Q(self.d.name),
                                          ["path", Q("/" + self.root), ["reference", Q(ref)], ["unit", 1]]]]])
        self.points.append((sn(x), sn(y), net))

    def text(self, s, x, y, size=3):
        self.items.append(["text", Q(s), ["exclude_from_sim", "no"], ["at", sn(x), sn(y), 0],
                           ["effects", ["font", ["size", size, size], ["bold", "yes"]], ["justify", "left", "bottom"]],
                           ["uuid", uid()]])

    def rect(self, x1, y1, x2, y2):
        self.items.append(["rectangle", ["start", sn(x1), sn(y1)], ["end", sn(x2), sn(y2)],
                           ["stroke", ["width", 0.15], ["type", "dash"]], ["fill", ["type", "none"]], ["uuid", uid()]])


def prop(name, val, x, y, just="left", hide=False, ang=0):
    eff = ["effects", ["font", ["size", FONT, FONT]]]
    if just != "center":
        eff.append(["justify", just])
    if hide:
        eff.append(["hide", "yes"])
    return ["property", Q(name), Q(val), ["at", sn(x), sn(y), ang], eff]


# ------------------------------------------------------------ gruppi di passivi
class Group:
    """Passivi appesi a una rete, disegnati in una cornice canonica:
    a = distanza verso fuori dal punto di partenza, b = lungo il bordo (b in su = verso -b).
    Gli oggetti si tengono astratti e si trasformano alla fine."""

    def __init__(self):
        self.parts = []    # (part, near_pin, (a, b), facing (da, db) = direzione verso fuori del pin vicino)
        self.wires = []    # ((a,b), (a,b), net)
        self.juncs = []
        self.ends = []     # ((a,b), net, out(da,db)) estremi da chiudere con simbolo o etichetta
        self.marks = []    # ((a,b), net) etichette sul filo, per le reti che proseguono altrove
        self.box = [0, 0, 0, 0]   # amin, amax, bmin, bmax

    def grow(self, a, b, ra=0, rb=0):
        self.box[0] = min(self.box[0], a - ra)
        self.box[1] = max(self.box[1], a + ra)
        self.box[2] = min(self.box[2], b - rb)
        self.box[3] = max(self.box[3], b + rb)


def two_pin(p):
    ps = list(p.sym.pins().values())
    return len(ps) == 2 and (ps[0]["ang"] - ps[1]["ang"]) % 360 == 180


def span(p):
    """Distanza fra i due pin di un passivo e larghezza del corpo."""
    q = list(p.sym.units[1])
    L = abs(q[0]["x"] - q[1]["x"]) + abs(q[0]["y"] - q[1]["y"])
    return L, 2.54


def end_extent(net, masse, out_along_a, labw):
    """Ingombro (lungo a, lungo b) dell'estremo chiuso da un simbolo o da un'etichetta."""
    return labw


class Layout:
    def __init__(self, d, block, local_nets, power, used):
        self.d, self.block = d, block
        self.local = local_nets       # reti che restano nel blocco
        self.power = power
        self.used = used              # passivi già disegnati
        self.anchor_nets = set()

    def passives_on(self, net):
        return [p for p in self.d.parts if p.block == self.block and p.ref not in self.used
                and two_pin(p) and net in p.nets.values()]

    def other(self, p, num):
        return [k for k in p.nets if k != num][0]

    def chain(self, g, net, a, b, depth=0):
        """Disegna i passivi della rete net a partire da (a, b), verso +a."""
        if net is None or net in self.power:
            g.ends.append(((a, b), net, (1, 0)))
            return
        ps = [] if (depth > 0 and net in self.anchor_nets) else self.passives_on(net)
        if depth > 4:
            ps = []
        if ps and depth > 0:
            g.marks.append(((a, b), net))
        if not ps:
            g.ends.append(((a, b), net, (1, 0)))
            g.grow(a, b)
            return
        for p in ps:
            self.used.add(p.ref)
        # in serie: il passivo che porta avanti il segnale (lontano non di alimentazione)
        ps.sort(key=lambda p: (p.nets[self.other(p, [k for k, n in p.nets.items() if n == net][0])] in self.power))
        series, branches = ps[0], ps[1:]
        x = a
        for i, p in enumerate(branches):
            near = [k for k, n in p.nets.items() if n == net][0]
            far = p.nets[self.other(p, near)]
            if i == 0:
                step = 2 * G
            else:
                q0 = branches[i - 1]
                fn0 = q0.nets[self.other(q0, [k for k, n in q0.nets.items() if n == net][0])] or ""
                fn1 = p.nets[self.other(p, [k for k, n in p.nets.items() if n == net][0])] or ""
                # testo del ramo prima (a destra del corpo) e nomi delle alimentazioni in fondo
                step = sn(max(3 * G, 4.5 + CH * max(len(q0.ref), len(q0.value)),
                              CH * (len(fn0) + len(fn1)) / 2 + 2), G)
                step = math.ceil(step / G) * G
            x += step
            g.wires.append(((x - step, b), (x, b), net))
            g.juncs.append((x, b))
            k = kind_of(far, self.d.masse) if far in self.power else "gnd"
            sb = body_of(k)[1]                     # il ramo va dalla parte del simbolo
            L, _ = span(p)
            g.wires.append(((x, b), (x, b + sb * G), net))
            g.parts.append((p, near, (x, b + sb * G), (0, -sb)))
            fe = (x, b + sb * (G + L))
            g.ends.append((fe, far, (0, sb)))
            g.grow(x, b + sb * (G + L + 5), 2 + CH * max(len(p.ref), len(p.value)), 0)
            g.grow(x, b)
        near = [k for k, n in series.nets.items() if n == net][0]
        far = series.nets[self.other(series, near)]
        L, _ = span(series)
        x0 = x + (sn(max(2 * G, 3 + CH * max(len(branches[-1].ref), len(branches[-1].value))), G) if branches else 2 * G)
        g.wires.append(((x, b), (x0, b), net))
        g.parts.append((series, near, (x0, b), (-1, 0)))
        g.grow(x0 + L / 2, b, L / 2, 5)
        self.chain(g, far, x0 + L, b, depth + 1)


def transform(side, origin):
    """Funzione (a, b) -> (x, y) e (da, db) -> (dx, dy) per il lato del pin."""
    px, py = origin
    if side == (-1, 0):
        return (lambda a, b: (px - a, py + b)), (lambda da, db: (-da, db))
    if side == (1, 0):
        return (lambda a, b: (px + a, py + b)), (lambda da, db: (da, db))
    if side == (0, -1):
        return (lambda a, b: (px + b, py - a)), (lambda da, db: (db, -da))
    return (lambda a, b: (px + b, py + a)), (lambda da, db: (db, da))


def rot_for(p, num, out):
    q = p.sym.pins()[num]
    for r in (0, 90, 180, 270):
        if pin_out(r, q) == out:
            return r
    raise ValueError("%s: nessuna rotazione porta il pin %s verso %s" % (p.ref, num, out))


FIELD_ANGLE = {0: 0, 180: 0, 90: 90, 270: 90}


def place_two_pin(sh, p, near, pt, out):
    """Mette un passivo col pin near nel punto pt, rivolto verso out."""
    r = rot_for(p, near, out)
    q = p.sym.pins()[near]
    dx, dy = rotv(q["x"], q["y"], r)
    sx, sy = pt[0] - dx, pt[1] + dy
    horiz = out[1] == 0
    if horiz:
        refpos = (sx, sy - 2.54, "center"), (sx, sy + 2.54, "center")
    else:
        refpos = (sx + 2.0, sy - 1.27, "left"), (sx + 2.0, sy + 1.27, "left")
    sh.field_angle = FIELD_ANGLE.get(r, 0)
    sh.symbol(p, 1, sx, sy, r, refpos)
    sh.field_angle = 0


def emit(sh, g, f, fd):
    for (p, near, (a, b), facing) in g.parts:
        place_two_pin(sh, p, near, f(a, b), fd(*facing))
    for (a1, b1), (a2, b2), net in g.wires:
        sh.wire(tuple(map(sn, f(a1, b1))), tuple(map(sn, f(a2, b2))), net)
    for (a, b) in g.juncs:
        sh.junction(tuple(map(sn, f(a, b))))


def close_end(sh, pt, net, out, power, local, sideways=False):
    if net is None:
        sh.items.append(["no_connect", ["at", pt[0], pt[1]], ["uuid", uid()]])
    elif net in power:
        sh.power(pt, net, out, sideways)
    else:
        sh.label(pt, net, out, net not in local)


# ------------------------------------------------------------ disegno di un blocco
def draw_block(sh, d, block, power, local_of, used, x0, y0):
    """Disegna il blocco con l'angolo in alto a sinistra in (x0, y0). Rende (larghezza, altezza)."""
    parts = [p for p in d.parts if p.block == block]
    local = local_of[block]
    lay = Layout(d, block, local, power, used)
    anchors = [(p, u) for p in parts if not two_pin(p) and len(p.sym.pins()) > 1 for u in sorted(p.sym.units)]
    for p, u in anchors:
        for q in p.sym.units[u]:
            if p.nets.get(q["num"]):
                lay.anchor_nets.add(p.nets[q["num"]])
    # 1. per ogni unità: gruppi dei pin, poi corsie
    plans = []
    for p, u in anchors:
        pins = [q for q in p.sym.units[u]]
        sides = {}
        for q in pins:
            sides.setdefault(pin_out(0, q), []).append(q)
        unit = {"p": p, "u": u, "sides": {}}
        for side, qs in sides.items():
            # ordinati lungo il bordo
            key = (lambda q: -q["y"]) if side[1] == 0 else (lambda q: q["x"])
            qs = sorted(qs, key=key)
            groups = []
            dense = len(qs) > 3
            for q in qs:
                net = p.nets.get(q["num"])
                g = Group()
                g.dense = dense
                if dense:
                    g.ends.append(((0, 0), net, (1, 0)))
                    groups.append((q, net, g))
                    continue
                lay.chain(g, net, 0, 0)
                if net in power and side[1] == 0:
                    # simbolo di alimentazione sul pin: occupa il bordo dalla parte del suo corpo
                    bd = body_of(kind_of(net, d.masse))[1]
                    g.grow(G, bd * 7.5)
                    g.grow(G + len(net) * CH, 0)
                groups.append((q, net, g))
            unit["sides"][side] = groups
        plans.append(unit)
    # 2. corsie: lungo il bordo, i gruppi non si sovrappongono; i pin scendono con una deviazione
    placed = []
    cx, rowy, rowh = x0, y0 + 8, 0
    maxw = 0
    for unit in plans:
        p, u = unit["p"], unit["u"]
        # misura dell'unità: corpo + gruppi
        pins = p.sym.units[u]
        xs = [q["x"] for q in pins] or [0]
        ys = [-q["y"] for q in pins] or [0]
        lanes = {}
        ext = {"L": 0, "R": 0, "T": 0, "B": 0}
        for side, groups in unit["sides"].items():
            n = len(groups)
            prev_bottom = None
            lst = []
            for i, (q, net, g) in enumerate(groups):
                lab = (len(net) * CH + 4) if net and net not in power else 6
                amin, amax, bmin, bmax = g.box
                amax = max(amax, max([e[0][0] for e in g.ends] + [0]) + lab)
                bmin, bmax = min(bmin, -1.5), max(bmax, 1.5)
                pos = q["y"] * -1 if side[1] == 0 else q["x"]
                lane = pos if (prev_bottom is None or getattr(g, "dense", False)) \
                    else max(pos, prev_bottom - bmin + 1.27)
                lane = sn(lane)
                prev_bottom = lane + bmax
                s = G * (1 + sum(1 for j in range(i + 1, n)))     # deviazione: i primi escono di più
                lst.append((q, net, g, lane, s, amax))
            lanes[side] = lst
            far = max([s + amax for (_, _, _, _, s, amax) in lst] + [0])
            lo = min([lane + g.box[2] - 1.5 for (_, _, g, lane, _, _) in lst] + [0])
            hi = max([lane + g.box[3] + 1.5 for (_, _, g, lane, _, _) in lst] + [0])
            if side == (-1, 0):
                ext["L"] = max(ext["L"], -min(xs) + far)
                ext["T"], ext["B"] = max(ext["T"], -lo), max(ext["B"], hi)
            elif side == (1, 0):
                ext["R"] = max(ext["R"], max(xs) + far)
                ext["T"], ext["B"] = max(ext["T"], -lo), max(ext["B"], hi)
            elif side == (0, -1):
                ext["T"] = max(ext["T"], -min(ys) + far)
                ext["L"], ext["R"] = max(ext["L"], -lo), max(ext["R"], hi)
            else:
                ext["B"] = max(ext["B"], max(ys) + far)
                ext["L"], ext["R"] = max(ext["L"], -lo), max(ext["R"], hi)
        ext["L"] = max(ext["L"], -min(xs) + 3)
        ext["R"] = max(ext["R"], max(xs) + 3)
        ext["T"] = max(ext["T"], -min(ys) + 5)
        ext["B"] = max(ext["B"], max(ys) + 5)
        w, h = ext["L"] + ext["R"], ext["T"] + ext["B"]
        if cx + w > x0 + 420 and cx > x0:
            cx, rowy, rowh = x0, rowy + rowh + 8, 0
        ax, ay = sn(cx + ext["L"], G), sn(rowy + ext["T"], G)
        placed.append((unit, lanes, ax, ay))
        cx += w + 10
        rowh = max(rowh, h)
        maxw = max(maxw, cx - x0)
    for unit, lanes, ax, ay in placed:
        p, u = unit["p"], unit["u"]
        if p.ref.startswith("J") and len(p.sym.pins()) > 20:
            refpos = (ax, ay - 2.54 - (max(-q["y"] for q in p.sym.units[u]) if False else 0), "left"), (ax, ay, "left")
        sh.symbol(p, u, ax, ay, 0, None if not (len(p.sym.pins()) > 2) else
                  ((ax - 3, ay + min([-q["y"] for q in p.sym.units[u]] + [0]) - 2.54, "left"),
                   (ax - 3, ay + max([-q["y"] for q in p.sym.units[u]] + [0]) + 2.54, "left")))
        for side, lst in lanes.items():
            for (q, net, g, lane, s, amax) in lst:
                px, py = pin_at(ax, ay, 0, q)
                if side[1] == 0:
                    pos = py - ay
                    start_b = lane - pos
                else:
                    pos = px - ax
                    start_b = lane - pos
                f, fd = transform(side, (px, py))
                if not g.parts and not g.wires:
                    # solo un estremo: simbolo o etichetta sul pin, o in fondo alla deviazione
                    (pt, n, out) = g.ends[0]
                    if abs(start_b) < 0.01 or n is None:
                        close_end(sh, (px, py), n, side, power, local, getattr(g, "dense", False))
                    else:
                        e1, e2 = tuple(map(sn, f(s, 0))), tuple(map(sn, f(s, start_b)))
                        sh.wire((px, py), e1, n)
                        sh.wire(e1, e2, n)
                        close_end(sh, e2, n, side, power, local)
                    continue
                # uscita dal pin, deviazione, poi il gruppo a partire da (s, start_b)
                net0 = net
                if abs(start_b) < 0.01:
                    sh.wire((px, py), tuple(map(sn, f(s, 0))), net0)
                else:
                    sh.wire((px, py), tuple(map(sn, f(s, 0))), net0)
                    sh.wire(tuple(map(sn, f(s, 0))), tuple(map(sn, f(s, start_b))), net0)
                g2 = Group()
                g2.parts = [(pp, nn, (a + s, b + start_b), fc) for (pp, nn, (a, b), fc) in g.parts]
                g2.wires = [((a1 + s, b1 + start_b), (a2 + s, b2 + start_b), n) for (a1, b1), (a2, b2), n in g.wires]
                g2.juncs = [(a + s, b + start_b) for (a, b) in g.juncs]
                for (a, b), n in g.marks:
                    sh.label(tuple(map(sn, f(a + s, b + start_b))), n, fd(1, 0), n not in local)
                emit(sh, g2, f, fd)
                # etichetta della rete del pin, sul filo d'uscita: sparisce se la rete è tutta qui
                if net0 and net0 not in power:
                    sh.label(tuple(map(sn, f(s, 0))), net0, side, net0 not in local)
                for (a, b), n, out in g.ends:
                    close_end(sh, tuple(map(sn, f(a + s, b + start_b))), n, fd(*out), power, local)
    # 3. i passivi rimasti (fra due alimentazioni, fra due reti senza integrato): in fila, in verticale
    ry = rowy + rowh + 10 if placed else y0 + 12
    gx, gy, gh = x0 + 5, ry, 0
    while True:
        free = [p for p in parts if two_pin(p) and p.ref not in used
                and any(n and n not in power for n in p.nets.values())]
        if not free:
            break
        p0 = free[0]
        net = [n for n in p0.nets.values() if n and n not in power][0]
        g = Group()
        lay.chain(g, net, 0, 0)
        lab = len(net) * CH + 5
        amax = max([e[0][0] for e in g.ends] + [g.box[1]]) + 8
        w, h = lab + amax, (g.box[3] - g.box[2]) + 8
        if gx + w > x0 + 420 and gx > x0 + 5:
            gx, gy, gh = x0 + 5, gy + gh + 6, 0
        o = (sn(gx + lab, G), sn(gy - g.box[2] + 4, G))
        f, fd = transform((1, 0), o)
        emit(sh, g, f, fd)
        for (a, b), n in g.marks:
            sh.label(tuple(map(sn, f(a, b))), n, fd(1, 0), n not in local)
        sh.label(o, net, (-1, 0), net not in local)
        for (a, b), n, out in g.ends:
            close_end(sh, tuple(map(sn, f(a, b))), n, fd(*out), power, local)
        gx += w + 6
        gh = max(gh, h)
        maxw = max(maxw, gx - x0)
    if gy != ry or gx != x0 + 5:
        ry = gy + gh + 10
    rest = [p for p in parts if (two_pin(p) or len(p.sym.pins()) == 1) and p.ref not in used]
    rx = x0 + 5
    ry0 = ry
    for p in rest:
        used.add(p.ref)
        nums = sorted(p.nets) if len(p.nets) == 2 else list(p.sym.pins())
        if len(p.sym.pins()) == 1:
            q = list(p.sym.pins().values())[0]
            sh.symbol(p, 1, rx, ry, 0)
            pt = pin_at(rx, ry, 0, q)
            close_end(sh, pt, p.nets.get(q["num"]), pin_out(0, q), power, local)
            rx += 15
            continue
        # il pin verso l'alimentazione positiva in alto, la massa in basso
        a_, b_ = list(p.sym.pins())
        na, nb = p.nets.get(a_), p.nets.get(b_)
        def rank(n):
            if n in power:
                return {"pos": 0, "neg": 2, "gnd": 3}[kind_of(n, d.masse)]
            return 1
        top = a_ if rank(na) <= rank(nb) else b_
        bot = b_ if top == a_ else a_
        L, _ = span(p)
        pt_top = (sn(rx, G), sn(ry, G))
        place_two_pin(sh, p, top, pt_top, (0, -1))
        close_end(sh, pt_top, p.nets.get(top), (0, -1), power, local)
        pt_bot = (pt_top[0], sn(pt_top[1] + L))
        close_end(sh, pt_bot, p.nets.get(bot), (0, 1), power, local)
        lw = max(len(p.nets.get(top) or ""), len(p.nets.get(bot) or ""), len(p.value) + 4) * CH
        rx += max(12.7, lw + 5)
        if rx > x0 + 420:
            rx, ry = x0 + 5, ry + 30
    height = (ry + 30 if rest else ry) - y0
    width = max(maxw, (rx - x0) if not rest or ry == ry0 else 420) + 5
    if rest:
        width = max(width, min(rx - x0, 430))
    return max(width, 60), max(height, 30)


# ------------------------------------------------------------ etichette, con le reti tutte a filo tolte
def finish_labels(sh):
    par = {}

    def find(a):
        while par.setdefault(a, a) != a:
            par[a] = par[par[a]]
            a = par[a]
        return a

    def union(a, b):
        par[find(a)] = find(b)

    for x1, y1, x2, y2, n in sh.segs:
        union((x1, y1), (x2, y2))
    comps = {}
    for x, y, n in sh.points:
        if n:
            comps.setdefault(n, set()).add(find((x, y)))
    for x, y, n, glob, out in sh.labels:
        comps.setdefault(n, set()).add(find((x, y)))
    for x, y, n, glob, out in sh.labels:
        if len(comps.get(n, ())) <= 1:
            continue      # rete tutta a filo in un pezzo: l'etichetta non serve
        la = ang_of(out)
        just = "right" if la in (180, 270) else "left"
        if glob:
            sh.items.append(["global_label", Q(n), ["shape", "passive"], ["at", x, y, la], ["fields_autoplaced", "yes"],
                             ["effects", ["font", ["size", 1.0, 1.0]], ["justify", just]], ["uuid", uid()]])
        else:
            sh.items.append(["label", Q(n), ["at", x, y, la], ["fields_autoplaced", "yes"],
                             ["effects", ["font", ["size", FONT, FONT]], ["justify", just, "bottom"]], ["uuid", uid()]])


def check_overlaps(sh):
    """Un punto di un'altra rete sopra un filo lo collega: qui lo si trova prima di KiCad."""
    pts = [(x, y, n) for x, y, n in sh.points] + [(x, y, n) for x, y, n, _, _ in sh.labels]
    for x1, y1, x2, y2, n in sh.segs:
        pts += [(x1, y1, n), (x2, y2, n)]
    bad = []
    for x1, y1, x2, y2, n in sh.segs:
        lo_x, hi_x, lo_y, hi_y = min(x1, x2), max(x1, x2), min(y1, y2), max(y1, y2)
        for x, y, m in pts:
            if m == n or m is None and n is None:
                continue
            if lo_x - 1e-6 <= x <= hi_x + 1e-6 and lo_y - 1e-6 <= y <= hi_y + 1e-6:
                bad.append("filo di %s tocca %s in (%.2f, %.2f)" % (n, m, x, y))
    return bad


# ------------------------------------------------------------ schema intero
def build(modpath):
    """modpath = file del modulo; «file.py:L» passa L come argomento (master-uscita.py:L)."""
    modpath, _, arg = modpath.partition(":")
    sys.path.insert(0, os.path.dirname(os.path.abspath(modpath)))
    argv = sys.argv
    sys.argv = [modpath] + ([arg] if arg else [])
    try:
        g = runpy.run_path(modpath, run_name="leggibile")
    finally:
        sys.argv = argv
        sys.path.pop(0)
    d = g["d"]
    out = os.path.join(d.outdir, "leggibile")
    os.makedirs(out, exist_ok=True)
    uid_seed(d.name + "/leggibile")
    sh = Sheet(d)
    sh.root = _uuid()
    power = set(d.power) | set(d.masse)
    blocks = []
    for p in d.parts:
        if p.block not in blocks:
            blocks.append(p.block)
    netblocks = {}
    for p in d.parts:
        for n in p.nets.values():
            if n:
                netblocks.setdefault(n, set()).add(p.block)
    local_of = {b: {n for n, bs in netblocks.items() if bs == {b}} for b in blocks}
    used = set()
    sizes, tused = {}, set()
    st = dict(pcbgen._uidstate)
    for b in blocks:
        trial = Sheet(d)
        trial.root = sh.root
        w, h = draw_block(trial, d, b, power, local_of, tused, 0, 0)
        sizes[b] = (max(w, len(b) * 2.8 + 10), h)
    pcbgen._uidstate.update(st)
    area = sum(w * h for w, h in sizes.values())
    pagew = sn(max(max(w for w, h in sizes.values()) + 40, math.sqrt(area * 1.6)), 10)
    x, y, rowh = 20.0, 30.0, 0
    for b in blocks:
        w, h = sizes[b]
        if x + w > pagew and x > 20:
            x, y, rowh = 20.0, y + rowh + 15, 0
        sh.text(b, x, y + 4)
        draw_block(sh, d, b, power, local_of, used, x, y + 6)
        h += 6
        sh.rect(x - 4, y - 2, x + w, y + h)
        x += w + 15
        rowh = max(rowh, h)
    # PWR_FLAG sulle alimentazioni che nessun pin guida, come nello schema del generatore
    flag = libsym("power:PWR_FLAG")
    driven = {p.nets.get(q["num"]) for p in d.parts for ps in p.sym.units.values()
              for q in ps if q["type"] == "power_out"}
    fy = y + rowh + 25
    sh.text("PWR_FLAG (per il controllo ERC)", 20, fy - 6, 2)
    for i, net in enumerate(sorted((d.power | {d.gnd}) - driven)):
        if net not in {n for p in d.parts for n in p.nets.values()}:
            continue
        fx = 25 + (i % 12) * 30
        fyy = fy + (i // 12) * 20
        fake = pcbgen.Part("#FLG%02d" % (i + 1), flag, "PWR_FLAG", "", {"1": net}, "")
        sh.symbol(fake, 1, fx, fyy, 0, ((fx, fyy - 4, "center"), (fx, fyy - 6, "center")))
        q = flag.units[1][0]
        sh.power(pin_at(fx, fyy, 0, q), net, pin_out(0, q))
    finish_labels(sh)
    bad = check_overlaps(sh)
    paper_h = max(420, sn(fy + 60))
    sch = ["kicad_sch", ["version", 20260101], ["generator", Q("eeschema")], ["generator_version", Q("10.0")],
           ["uuid", Q(sh.root)], ["paper", Q("User"), pagew + 40, paper_h],
           ["title_block", ["title", Q(d.title + " - schema leggibile")], ["rev", Q(d.rev)],
            ["comment", 1, Q("Generato da pcb/tools/leggibile.py dallo stesso netlist della PCB: non modificare a mano")]],
           ["lib_symbols"] + list(sh.libs.values())] + sh.items + \
          [["sheet_instances", ["path", Q("/"), ["page", Q("1")]]], ["embedded_fonts", "no"]]
    path = os.path.join(out, d.name + ".kicad_sch")
    with open(path, "w") as f:
        f.write(dump(sch) + "\n")
    # progetto minimo e tabella dei simboli: i simboli maelcum stanno nella cartella della scheda
    with open(os.path.join(out, d.name + ".kicad_pro"), "w") as f:
        json.dump({"meta": {"filename": d.name + ".kicad_pro", "version": 3}}, f, indent=2)
    with open(os.path.join(out, "sym-lib-table"), "w") as f:
        f.write('(sym_lib_table\n\t(version 7)\n\t(lib (name "maelcum")(type "KiCad")'
                '(uri "${KIPRJMOD}/../maelcum.kicad_sym")(options "")(descr "simboli di maelcum"))\n)\n')
    return d, path, out, bad


def verify(d, path, out, bad):
    rep, xmlp, pdf = (os.path.join(out, n) for n in ("erc.json", "netlist.xml", d.name + ".pdf"))
    for f in (rep, xmlp, pdf):
        if os.path.exists(f):
            os.remove(f)
    subprocess.run([CLI, "sch", "erc", "--format", "json", "--severity-all", "-o", rep, path], capture_output=True)
    subprocess.run([CLI, "sch", "export", "netlist", "--format", "kicadxml", "-o", xmlp, path], capture_output=True)
    subprocess.run([CLI, "sch", "export", "pdf", "--black-and-white", "-o", pdf, path], capture_output=True)
    counts = {}
    for s in json.load(open(rep)).get("sheets", []):
        for v in s.get("violations", []):
            k = "%s/%s" % (v["severity"], v["type"])
            counts[k] = counts.get(k, 0) + 1
    got = set()
    for n in ET.parse(xmlp).getroot().iter("net"):
        c = tuple(sorted((x.get("ref"), x.get("pin")) for x in n.iter("node") if not x.get("ref").startswith("#")))
        if c:
            got.add(c)
    os.remove(xmlp)
    want = {k: tuple(sorted(v)) for k, v in d.netmap().items()}
    diff = ["manca: %s" % k for k, v in want.items() if v not in got]
    wantsets = set(want.values())
    diff += ["rete in più: %s" % (v,) for v in got if len(v) > 1 and v not in wantsets]
    err = diff + ["ERC %s: %d" % (k, v) for k, v in counts.items() if k.startswith("error")] + bad
    res = {"modulo": d.name, "erc": counts, "reti_diverse": diff, "fili_sovrapposti": bad,
           "pdf": os.path.relpath(pdf, d.outdir), "esito": "LEGGIBILE NON PASSA" if err else "LEGGIBILE PASSA"}
    with open(os.path.join(out, "riepilogo.json"), "w") as f:
        json.dump(res, f, indent=1, ensure_ascii=False)
    print("%s: %s  (ERC %s)" % (d.name, res["esito"], counts))
    for e in err[:30]:
        print("  ERRORE  " + e)
    return not err


if __name__ == "__main__":
    if len(sys.argv) == 2:
        sys.exit(0 if verify(*build(sys.argv[1])) else 1)
    # più moduli: un processo per modulo. Tre moduli hanno un cavo.py: nello stesso processo
    # Python riuserebbe quello del primo (sys.modules) e lo schema prenderebbe i fili sbagliati.
    ok = True
    for m in sys.argv[1:]:
        ok &= subprocess.run([sys.executable, __file__, m]).returncode == 0
    sys.exit(0 if ok else 1)
