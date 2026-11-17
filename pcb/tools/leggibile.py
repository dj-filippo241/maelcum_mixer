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
import leggibile_en as en
import instrada
from pcbgen import libsym, uid, uid_seed, _uuid, Q, CLI, dump

MISSING = []      # testi senza traduzione inglese: fermano il giro


def t_block(b):
    if b == DECOUP:
        return "POWER DECOUPLING: supply pins of the chips, bypass capacitors, unused op-amp units"
    e = en.block(b)
    if e is None:
        MISSING.append("blocco: " + b)
        return b
    return e


def t_value(v):
    e = en.value(v)
    if e is None:
        MISSING.append("valore: " + v)
        return v
    return e

G = 2.54
UNIT_BLOCK = {}    # (ref, unità) -> blocco del disegno, se diverso da quello del pezzo
DECOUP = "POWER DECOUPLING"
BUDGET = 225      # altezza utile di una pagina A3 sotto il titolo
BANDW = 370       # larghezza di una fascia di stadi: una pagina A3 coi margini
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
        self.R = instrada.Router()
        self.juncs = set()
        self.wireitems = []
        self.kept = []          # (x, y) delle etichette rimaste

    def tbox(self, s, x, y, just, ang=0, size=FONT):
        """Ingombro di un testo, come ostacolo per i fili."""
        w, hh = len(s) * CH * size / FONT, 0.8 * size / FONT
        if just == "left":
            a, b = 0, w
        elif just == "right":
            a, b = -w, 0
        else:
            a, b = -w / 2, w / 2
        if ang == 90:
            self.R.box(x - hh, y - b, x + hh, y - a)
        else:
            self.R.box(x + a, y - hh, x + b, y + hh)

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
             prop("Reference", p.ref, rx, ry, rj, ang=fa), prop("Value", t_value(p.value), vx, vy, vj, ang=fa),
             prop("Footprint", p.fp, x, y, hide=True), prop("Datasheet", "", x, y, hide=True)]
        if p.note:
            s.append(prop("Nota", p.note, x, y, hide=True))
        for q in p.sym.units[u]:
            s.append(["pin", Q(q["num"]), ["uuid", uid()]])
        s.append(["instances", ["project", Q(self.d.name),
                                ["path", Q("/" + self.root), ["reference", Q(p.ref)], ["unit", u]]]])
        self.items.append(s)
        self.R.symbol(p.sym, u, x, y, r, rotv)
        self.tbox(p.ref, rx, ry, rj, fa)
        self.tbox(t_value(p.value), vx, vy, vj, fa)
        for q in p.sym.units[u]:
            px, py = pin_at(x, y, r, q)
            self.points.append((px, py, p.nets.get(q["num"])))
            self.R.point(px, py, p.nets.get(q["num"]))

    def wire(self, a, b, net):
        if a == b:
            return
        it = ["wire", ["pts", ["xy", a[0], a[1]], ["xy", b[0], b[1]]],
              ["stroke", ["width", 0], ["type", "default"]], ["uuid", uid()]]
        self.items.append(it)
        self.wireitems.append(it)
        self.segs.append((a[0], a[1], b[0], b[1], net))
        self.R.seg(a[0], a[1], b[0], b[1], net)

    def junction(self, a):
        self.juncs.add((sn(a[0]), sn(a[1])))
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
        self.R.point(sn(x), sn(y), net)
        self.R.box(x, y, x + body[0] * 3.8 + (1.3 if body[0] == 0 else 0), y + body[1] * 3.8 + (1.3 if body[1] == 0 else 0))
        self.R.box(x - (1.3 if body[0] == 0 else 0), y - (1.3 if body[1] == 0 else 0), x, y)
        self.tbox(net, vx, vy, vj, FIELD_ANGLE.get(r, 0))

    def nc(self, pt):
        self.items.append(["no_connect", ["at", pt[0], pt[1]], ["uuid", uid()]])
        self.R.point(pt[0], pt[1], None)

    def text(self, s, x, y, size=3):
        self.R.box(x, y - size, x + len(s) * size * 0.9, y)
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
        sh.nc(pt)
    elif net in power:
        sh.power(pt, net, out, sideways)
    else:
        sh.label(pt, net, out, net not in local)


# ------------------------------------------------------------ ordine del segnale
def pin_role(q):
    nm = str(q["name"]).upper()
    if q["type"] in ("output", "tri_state") or nm.startswith("OUT") or nm in ("~", "Q", "VOUT", "EO"):
        return "out"
    if q["type"] == "input" or nm in ("+", "-") or nm.startswith(("IN", "+IN", "-IN", "EC", "SIG")):
        return "in"
    return None


def signal_columns(d, block, anchors, power):
    """Colonna e ordine di ogni unità: dall'ingresso all'uscita, seguendo i passivi in serie."""
    par = {}

    def find(a):
        while par.setdefault(a, a) != a:
            par[a] = par[par[a]]
            a = par[a]
        return a

    for p in d.parts:
        if p.block == block and two_pin(p):
            ns = [n for n in p.nets.values() if n and n not in power]
            if len(ns) == 2:
                par[find(ns[0])] = find(ns[1])
    keys = [(p.ref, u) for p, u in anchors]
    outs, ins = {}, {}
    for p, u in anchors:
        for q in p.sym.units[u]:
            n = p.nets.get(q["num"])
            if not n or n in power:
                continue
            r = pin_role(q)
            if r == "out":
                outs.setdefault(find(n), set()).add((p.ref, u))
            elif r == "in":
                ins.setdefault(find(n), set()).add((p.ref, u))
    succ = {k: [] for k in keys}
    for c, ss in outs.items():
        for s_ in ss:
            for t in ins.get(c, ()):
                if t != s_ and t not in succ[s_]:
                    succ[s_].append(t)
    # archi all'indietro (retroazioni fra unità) tolti con una visita in profondità
    state, dag = {}, {k: [] for k in keys}

    def visit(k):
        state[k] = 1
        for t in succ[k]:
            if state.get(t) == 1:
                continue
            dag[k].append(t)
            if t not in state:
                visit(t)
        state[k] = 2

    roots = [k for k in keys if not any(k in v for v in succ.values())] + keys
    for k in roots:
        if k not in state:
            visit(k)
    col = {k: 0 for k in keys}
    for _ in range(len(keys)):
        ch = False
        for k in keys:
            for t in dag[k]:
                if col[t] < col[k] + 1:
                    col[t], ch = col[k] + 1, True
        if not ch:
            break
    linked = {k for k in keys if succ[k]} | {t for v in succ.values() for t in v}
    # catene indipendenti (lato L, lato R ...): ognuna nella sua fascia
    cp = {k: k for k in keys}

    def cf(a):
        while cp[a] != a:
            cp[a] = cp[cp[a]]
            a = cp[a]
        return a

    for k in keys:
        for t in succ[k]:
            cp[cf(k)] = cf(t)
    first = {}
    for k in keys:
        first.setdefault(cf(k) if k in linked else None, keys.index(k))
    comp = {k: (first[cf(k)] if k in linked else 10 ** 6) for k in keys}
    return col, succ, comp


# ------------------------------------------------------------ disegno di un blocco
def draw_block(sh, d, block, power, local_of, used, x0, y0, only=None, rest_too=True, budget=1e9):
    """Disegna il blocco con l'angolo in alto a sinistra in (x0, y0). Rende (larghezza, altezza, altro):
    only = le unità da disegnare (None: tutte); rest_too = anche i passivi rimasti, finché l'altezza
    resta sotto budget; altro = True se ne restano per una pagina dopo."""
    more = False
    parts = [p for p in d.parts if p.block == block]
    local = local_of[block]
    lay = Layout(d, block, local, power, used)
    anchors = [(p, u) for p in d.parts if not two_pin(p) and len(p.sym.pins()) > 1 for u in sorted(p.sym.units)
               if UNIT_BLOCK.get((p.ref, u), p.block) == block]
    col, succ, comp = signal_columns(d, block, anchors, power)
    if only is not None:
        anchors = [a for a in anchors if (a[0].ref, a[1]) in only]
    idx = {(p.ref, u): i for i, (p, u) in enumerate(anchors)}
    anchors.sort(key=lambda a: (comp[(a[0].ref, a[1])], col[(a[0].ref, a[1])], idx[(a[0].ref, a[1])]))
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
            dense = len(qs) > 3 and (p.ref.startswith("J") or len(qs) > 12)
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
        placed.append([unit, lanes, ext, w, h])
    # colonne nell'ordine del segnale; in colonna, l'ordine dei predecessori
    groups = {}
    for it in placed:
        k = (it[0]["p"].ref, it[0]["u"])
        groups.setdefault(comp[k], {}).setdefault(col[k] if comp[k] < 10 ** 6 else 0, []).append(it)
    rowof = {}
    cx, bottom, band = x0, y0 + 8, y0 + 8
    seq = []
    for g_ in sorted(groups):
        for c in sorted(groups[g_]):
            seq.append((g_, c, groups[g_][c]))
    lastg = None
    sh.bands = []           # [chiavi delle unità, altezza] di ogni fascia, per l'impaginazione
    cur = None

    def close_band():
        if cur and cur[0]:
            cur[1] = bottom - cur[2]
            sh.bands.append(cur)

    for g_, c, its in seq:
        if lastg is not None and g_ != lastg:
            close_band()
            cx, band = x0, bottom + 6
            cur = None
        lastg = g_
        def key(it):
            k = (it[0]["p"].ref, it[0]["u"])
            ps = [rowof[s_] for s_ in rowof if k in succ.get(s_, [])]
            return (sum(ps) / len(ps) if ps else 1e9, idx[k])
        its.sort(key=key)
        # una colonna più alta di una pagina continua a destra
        subs, sub, hh = [], [], 0
        for it in its:
            if sub and hh + it[4] > BUDGET - 20:
                subs.append(sub)
                sub, hh = [], 0
            sub.append(it)
            hh += it[4] + 10
        subs.append(sub)
        for sub in subs:
            cw = max(it[3] for it in sub)
            if cx + cw > x0 + BANDW and cx > x0:
                # fascia nuova sotto: il segnale riprende da sinistra
                close_band()
                cx, band = x0, bottom + 6
                cur = None
            if cur is None:
                cur = [[], 0, band]
            cy = band
            for n, it in enumerate(sub):
                unit, lanes, ext, w, h = it
                ax, ay = sn(cx + ext["L"], G), sn(cy + ext["T"], G)
                it[:] = [unit, lanes, ax, ay]
                rowof[(unit["p"].ref, unit["u"])] = n
                cur[0].append((unit["p"].ref, unit["u"]))
                cy += h + 10
            bottom = max(bottom, cy)
            cx += cw + 18
            maxw = max(maxw, cx - x0)
    close_band()
    rowy, rowh = bottom - 10, 0
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
    while rest_too:
        if gy - y0 > budget:
            more = True
            break
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
        if gx + w > x0 + BANDW and gx > x0 + 5:
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
    rest = [p for p in parts if (two_pin(p) or len(p.sym.pins()) == 1) and p.ref not in used] \
        if rest_too and not more else []
    rx = x0 + 5
    ry0 = ry
    for p in rest:
        if ry - y0 > budget:
            more = True
            break
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
        if rx > x0 + BANDW:
            rx, ry = x0 + 5, ry + 30
    height = (ry + 30 if rest else ry) - y0
    width = max(maxw, (rx - x0) if not rest or ry == ry0 else BANDW) + 5
    if rest:
        width = max(width, min(rx - x0, BANDW + 10))
    return max(width, 60), max(height, 30), more


# ------------------------------------------------------------ fili al posto delle etichette
def components(sh, net):
    """Pezzi della rete net sulla pagina: insiemi di celle unite da fili, pin ed etichette."""
    par = {}

    def find(a):
        while par.setdefault(a, a) != a:
            par[a] = par[par[a]]
            a = par[a]
        return a

    cells = set()
    for x1, y1, x2, y2, n in sh.segs:
        if n != net:
            continue
        a, b = instrada.cell(x1, y1), instrada.cell(x2, y2)
        line = [(i, a[1]) for i in range(min(a[0], b[0]), max(a[0], b[0]) + 1)] if a[1] == b[1] else \
               [(a[0], j) for j in range(min(a[1], b[1]), max(a[1], b[1]) + 1)]
        for c in line:
            par[find(c)] = find(line[0])
            cells.add(c)
    for x, y, n in sh.points:
        if n == net:
            cells.add(instrada.cell(x, y))
    labs = {}
    for i, (x, y, n, glob, out) in enumerate(sh.labels):
        if n == net:
            c = instrada.cell(x, y)
            cells.add(c)
            labs.setdefault(c, []).append(i)
    groups = {}
    for c in cells:
        groups.setdefault(find(c), set()).add(c)
    return list(groups.values()), labs


def label_cells(sh, i):
    x, y, n, glob, out = sh.labels[i]
    w = len(n) * CH + (3 if glob else 1)
    ex, ey = x + out[0] * w, y + out[1] * w
    if out[1] == 0:
        return (min(x, ex), y - (1.6 if not glob else 0.9), max(x, ex), y + (0 if not glob else 0.9))
    return (x - (1.6 if not glob else 0.9), min(y, ey), x + (0 if not glob else 0.9), max(y, ey))


def route_sheet(sh):
    """Collega con fili i pezzi delle reti che hanno etichette, dove il percorso è corto e libero."""
    R = sh.R
    for i, (x, y, n, glob, out) in enumerate(sh.labels):
        x1, y1, x2, y2 = label_cells(sh, i)
        c0 = instrada.cell(x, y)
        R.box(x1, y1, x2, y2, net=n)
        R.labtext.get(c0, set()).discard(n)
    nets = []
    for x, y, n, glob, out in sh.labels:
        if (n, glob) not in nets:
            nets.append((n, glob))
    order = []
    for n, glob in nets:
        comps, _ = components(sh, n)
        if len(comps) < 2:
            continue
        cs = [c for g in comps for c in g]
        spread = (max(c[0] for c in cs) - min(c[0] for c in cs)) + (max(c[1] for c in cs) - min(c[1] for c in cs))
        order.append((glob, spread, n))
    order.sort()
    done = 0
    for glob, spread, n in order:
        tried = set()
        while True:
            comps, _ = components(sh, n)
            if len(comps) < 2:
                break
            comps.sort(key=len, reverse=True)
            ok = False
            for k, tree in enumerate(comps):
                if k in tried:
                    continue
                goals = [c for j, g in enumerate(comps) if j != k for c in g]
                d0 = min(abs(a[0] - b[0]) + abs(a[1] - b[1]) for a in list(tree)[:200] for b in goals[:200])
                path = R.route(n, list(tree), goals, 1.5 * d0 + 40)
                if path:
                    for a, b in instrada.segments(path):
                        sh.wire((sn(a[0] * G / 2), sn(a[1] * G / 2)), (sn(b[0] * G / 2), sn(b[1] * G / 2)), n)
                    ok = True
                    done += 1
                    tried = set()
                    break
                tried.add(k)
            if not ok:
                break
    # giunzioni: dove un estremo di filo cade su un altro filo o su un pin già collegato
    for net in {n for *_, n in sh.segs}:
        deg = {}
        for x1, y1, x2, y2, n in sh.segs:
            if n != net:
                continue
            a, b = instrada.cell(x1, y1), instrada.cell(x2, y2)
            deg[a] = deg.get(a, 0) + 1
            deg[b] = deg.get(b, 0) + 1
            line = [(i, a[1]) for i in range(min(a[0], b[0]) + 1, max(a[0], b[0]))] if a[1] == b[1] else \
                   [(a[0], j) for j in range(min(a[1], b[1]) + 1, max(a[1], b[1]))]
            for c in line:
                deg[c] = deg.get(c, 0) + 2
        ends = {instrada.cell(x, y) for x1, y1, x2, y2, n in sh.segs if n == net for x, y in ((x1, y1), (x2, y2))}
        for x, y, n in sh.points:
            if n == net:
                c = instrada.cell(x, y)
                deg[c] = deg.get(c, 0) + 1
        for c in ends:
            if deg.get(c, 0) >= 3:
                pt = (sn(c[0] * G / 2), sn(c[1] * G / 2))
                if pt not in sh.juncs:
                    sh.junction(pt)
    return done


def prune(sh):
    """Toglie i pezzi di filo rimasti appesi (portavano un'etichetta che non serve più)."""
    while True:
        anchors = {}
        for x, y, n in sh.points:
            anchors[(x, y)] = anchors.get((x, y), 0) + 1
        for xy in sh.kept:
            anchors[xy] = anchors.get(xy, 0) + 1
        ends = {}
        for x1, y1, x2, y2, n in sh.segs:
            for xy in ((x1, y1), (x2, y2)):
                ends[xy] = ends.get(xy, 0) + 1
        changed = False
        for i, (x1, y1, x2, y2, n) in enumerate(sh.segs):
            for a, b in (((x1, y1), (x2, y2)), ((x2, y2), (x1, y1))):
                if ends[a] > 1 or a in anchors or a in sh.juncs:
                    continue
                # punto più vicino ad a, lungo il filo, dove c'è qualcosa
                def on(pt):
                    return min(a[0], b[0]) - 1e-6 <= pt[0] <= max(a[0], b[0]) + 1e-6 and \
                           min(a[1], b[1]) - 1e-6 <= pt[1] <= max(a[1], b[1]) + 1e-6 and pt != a
                stops = [pt for pt in list(anchors) + list(sh.juncs) + list(ends) if on(pt)]
                stops = [pt for pt in stops if pt != b or ends[b] > 1 or b in anchors or b in sh.juncs]
                it = sh.wireitems[i]
                if not stops:
                    sh.items.remove(it)
                    del sh.wireitems[i], sh.segs[i]
                else:
                    c = min(stops, key=lambda pt: abs(pt[0] - a[0]) + abs(pt[1] - a[1]))
                    sh.segs[i] = (c[0], c[1], b[0], b[1], n)
                    it[1] = ["pts", ["xy", c[0], c[1]], ["xy", b[0], b[1]]]
                    if c == b:
                        sh.items.remove(it)
                        del sh.wireitems[i], sh.segs[i]
                changed = True
                break
            if changed:
                break
        if not changed:
            break
    # giunzioni con meno di tre rami
    deg = {}
    for x1, y1, x2, y2, n in sh.segs:
        for xy in ((x1, y1), (x2, y2)):
            deg[xy] = deg.get(xy, 0) + 1
        for j in list(sh.juncs):
            if j not in ((x1, y1), (x2, y2)) and min(x1, x2) <= j[0] <= max(x1, x2) and min(y1, y2) <= j[1] <= max(y1, y2):
                deg[j] = deg.get(j, 0) + 2
    for x, y, n in sh.points:
        deg[(x, y)] = deg.get((x, y), 0) + 1
    for it in [it for it in sh.items if it[0] == "junction"]:
        j = (it[1][1], it[1][2])
        if deg.get(j, 0) < 3:
            sh.items.remove(it)
            sh.juncs.discard(j)


def finish_labels(sh):
    """Un'etichetta per pezzo di rete; nessuna se la rete locale è tutta a filo."""
    nets = []
    for x, y, n, glob, out in sh.labels:
        if n not in nets:
            nets.append(n)
    for n in nets:
        comps, labs = components(sh, n)
        glob = any(l[2] == n and l[3] for l in sh.labels)
        if len(comps) <= 1 and not glob:
            continue
        for g in comps:
            idx = sorted(i for c in g for i in labs.get(c, []))
            if not idx:
                continue
            x, y, n, glob, out = sh.labels[idx[0]]
            sh.kept.append((x, y))
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
PAPERS = (("A4", 297, 210), ("A3", 420, 297), ("A2", 594, 420), ("A1", 841, 594))


def paper_for(w, h):
    for name, pw, ph in PAPERS:
        if w + 30 <= pw and h + 50 <= ph:
            return name, pw, ph
    return "User", sn(w + 40, 10), sn(h + 60, 10)


def sheet_file(d, sh, paper, title, page, comment):
    pp = [Q(paper[0])] if paper[0] != "User" else [Q("User"), paper[1], paper[2]]
    return ["kicad_sch", ["version", 20260101], ["generator", Q("eeschema")], ["generator_version", Q("10.0")],
            ["uuid", Q(sh.fileuuid)], ["paper"] + pp,
            ["title_block", ["title", Q(title)], ["rev", Q(en.rev(d.rev))], ["comment", 1, Q(comment)],
             ["comment", 2, Q("Page %d" % page)]],
            ["lib_symbols"] + list(sh.libs.values())] + sh.items


def build(modpath):
    """modpath = file del modulo; «file.py:L» passa L come argomento (master-uscita.py:L).
    Esce uno schema gerarchico: la pagina 1 è l'indice dei blocchi, poi una pagina per blocco."""
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
    for f in os.listdir(out):
        if f.endswith(".kicad_sch"):
            os.remove(os.path.join(out, f))
    uid_seed(d.name + "/leggibile")
    root = _uuid()
    power = set(d.power) | set(d.masse)
    # disaccoppiamento: condensatori fra due alimentazioni e unità di sola alimentazione, su una pagina
    for p in d.parts:
        if two_pin(p) and p.nets and all(n in power for n in p.nets.values() if n) and \
                any(n and kind_of(n, d.masse) == "gnd" for n in p.nets.values()) and p.ref.startswith("C"):
            p.block = DECOUP
        if len(p.sym.units) > 1:
            for u, qs in p.sym.units.items():
                if qs and all(q["type"] in ("power_in", "power_out") for q in qs) and \
                        len({q["num"] for q in qs}) < len(p.sym.pins()):
                    UNIT_BLOCK[(p.ref, u)] = DECOUP
    # unità non usate (ingressi a massa, uscita sull'ingresso -): stanno col disaccoppiamento
    nm = d.netmap()
    for p in d.parts:
        if len(p.sym.units) < 2:
            continue
        for u, qs in p.sym.units.items():
            mine = {q["num"] for q in qs}
            sig = [p.nets.get(q["num"]) for q in qs if q["type"] not in ("power_in", "power_out")]
            if sig and all(n is None or n in power or all(r == p.ref and k in mine for r, k in nm.get(n, []))
                           for n in sig) and (p.ref, u) not in UNIT_BLOCK:
                UNIT_BLOCK[(p.ref, u)] = DECOUP
    blocks = []
    for p in d.parts:
        if p.block not in blocks and p.block != DECOUP:
            blocks.append(p.block)
    if any(p.block == DECOUP for p in d.parts) or UNIT_BLOCK:
        blocks.append(DECOUP)
    netblocks = {}
    for p in d.parts:
        for u, qs in p.sym.units.items():
            b = UNIT_BLOCK.get((p.ref, u), p.block)
            for q in qs:
                n = p.nets.get(q["num"])
                if n:
                    netblocks.setdefault(n, set()).add(b)
    local_of = {b: {n for n, bs in netblocks.items() if bs == {b}} for b in blocks}
    used = set()
    bad, pages, nroute = [], [], 0
    flag = libsym("power:PWR_FLAG")
    driven = {p.nets.get(q["num"]) for p in d.parts for ps in p.sym.units.values()
              for q in ps if q["type"] == "power_out"}
    allnets = {n for p in d.parts for n in p.nets.values()}
    flagpage = {}
    for n in sorted((d.power | {d.gnd}) - driven):
        if n in allnets:
            flagpage[n] = next(b for b in blocks if b in netblocks.get(n, ()))
    def new_sheet(b, part):
        sh = Sheet(d)
        sh.sheetuuid = _uuid()
        sh.fileuuid = _uuid()
        sh.root = root + "/" + sh.sheetuuid
        sh.block = b
        sh.title = t_block(b) + ("" if part == 1 else "  (continued, %d)" % part)
        sh.text(sh.title, 15, 22, 4)
        return sh

    # 1. disegno: un blocco su una o più pagine A3, spezzato fra le catene indipendenti
    sheets = []
    for b in blocks:
        anchors = [(p, u) for p in d.parts if not two_pin(p) and len(p.sym.pins()) > 1
                   for u in sorted(p.sym.units) if UNIT_BLOCK.get((p.ref, u), p.block) == b]
        # fasce del blocco disegnato per intero su una pagina di prova, poi messe in pagine A3
        st = dict(pcbgen._uidstate)
        trial = Sheet(d)
        trial.root = root
        draw_block(trial, d, b, power, local_of, set(used), 0, 0, rest_too=False)
        pcbgen._uidstate.update(st)
        packs, cur, curh = [], [], 0
        for ks, hh, _ in trial.bands:
            if cur and curh + hh > BUDGET:
                packs.append(cur)
                cur, curh = [], 0
            cur += ks
            curh += hh + 6
        packs.append(cur)
        part = 1
        for j, ks in enumerate(packs):
            sh = new_sheet(b, part)
            last = j == len(packs) - 1
            w, h, more = draw_block(sh, d, b, power, local_of, used, 15, 26, only=set(ks), rest_too=last, budget=BUDGET)
            sheets.append(sh)
            part += 1
            while last and more:
                sh = new_sheet(b, part)
                w, h, more = draw_block(sh, d, b, power, local_of, used, 15, 26, only=set(), budget=BUDGET)
                sheets.append(sh)
                part += 1
    # 2. reti presenti su più pagine: le loro etichette sono globali
    netpages = {}
    for i, sh in enumerate(sheets):
        for x, y, n in sh.points:
            if n:
                netpages.setdefault(n, set()).add(i)
        for x, y, n, glob, o_ in sh.labels:
            netpages.setdefault(n, set()).add(i)
    for i, sh in enumerate(sheets):
        sh.labels = [(x, y, n, len(netpages[n]) > 1, o_) for x, y, n, glob, o_ in sh.labels]
    # PWR_FLAG sulle alimentazioni che nessun pin guida, sulla prima pagina che le usa:
    # l'ERC di KiCad conta il flag collegato solo con un altro simbolo della rete sulla pagina
    flagnets = [n for n in sorted((d.power | {d.gnd}) - driven) if n in allnets]
    for i, sh in enumerate(sheets):
        mine = [n for n in flagnets if min(netpages.get(n, {i})) == i]
        if not mine:
            continue
        fy = sh.R.bbox[3] * 1.27 + 16
        sh.text("PWR_FLAG (for the ERC check only)", 15, fy - 6, 2)
        for k, net in enumerate(mine):
            fx = 20 + (k % 12) * 30
            fyy = fy + (k // 12) * 20
            fake = pcbgen.Part("#FLG%02d" % (flagnets.index(net) + 1), flag, "PWR_FLAG", "", {"1": net}, "")
            sh.symbol(fake, 1, fx, fyy, 0, ((fx, fyy - 4, "center"), (fx, fyy - 6, "center")))
            q = flag.units[1][0]
            sh.power(pin_at(fx, fyy, 0, q), net, pin_out(0, q))
    # 3. fili, etichette, file
    for i, sh in enumerate(sheets):
        nroute += route_sheet(sh)
        finish_labels(sh)
        prune(sh)
        bad += ["%s: %s" % (sh.title, e) for e in check_overlaps(sh)]
        bb = sh.R.bbox
        w = max(bb[2] * 1.27 - 15, len(sh.title) * 3.6)
        h = bb[3] * 1.27 - 26
        paper = paper_for(w + 15, h + 26)
        fname = "%s-%02d.kicad_sch" % (d.name, i + 2)
        with open(os.path.join(out, fname), "w") as f:
            f.write(dump(sheet_file(d, sh, paper, sh.title, i + 2,
                                    en.title(d.title) + " - readable schematic")) + "\n")
        pages.append((sh.block, sh, fname))
    # PWR_FLAG sulle alimentazioni che nessun pin guida, sulla pagina dell'indice
    top = Sheet(d)
    top.root = root
    top.fileuuid = root
    flag = libsym("power:PWR_FLAG")
    driven = {p.nets.get(q["num"]) for p in d.parts for ps in p.sym.units.values()
              for q in ps if q["type"] == "power_out"}
    allnets = {n for p in d.parts for n in p.nets.values()}
    top.text(en.title(d.title), 15, 25, 5)
    top.text("Readable schematic: one or more pages per functional block, in signal order. Page 1 is this index.", 15, 33, 2.5)
    top.text("Generated by pcb/tools/leggibile.py from the same netlist as the PCB and checked against it.", 15, 38, 2.5)
    cols, bw, bh = 3, 118, 13
    first = {}
    for i, (b, sh, fname) in enumerate(pages):
        first.setdefault(b, i + 2)
    for i, (b, sh, fname) in enumerate(pages):
        x, y = 15 + (i % cols) * (bw + 12), 52 + (i // cols) * (bh + 9)
        name = "p.%d  %s" % (i + 2, sh.title)
        others = sorted({ob for n in netblocks for ob in netblocks[n] if b in netblocks[n] and ob != b
                         and n not in power}, key=blocks.index)
        top.items.append(["sheet", ["at", x, y], ["size", bw, bh], ["exclude_from_sim", "no"], ["in_bom", "yes"],
                          ["on_board", "yes"], ["dnp", "no"], ["stroke", ["width", 0.3], ["type", "solid"]],
                          ["fill", ["color", 0, 0, 0, 0.0]], ["uuid", Q(sh.sheetuuid)],
                          ["property", Q("Sheetname"), Q(name[:95]), ["at", x, y - 0.7, 0],
                           ["effects", ["font", ["size", 1.4, 1.4], ["bold", "yes"]], ["justify", "left", "bottom"]]],
                          ["property", Q("Sheetfile"), Q(fname), ["at", x, y + bh + 0.6, 0],
                           ["effects", ["font", ["size", 1.27, 1.27]], ["justify", "left", "top"], ["hide", "yes"]]],
                          ["instances", ["project", Q(d.name), ["path", Q("/" + root), ["page", Q(str(i + 2))]]]]])
        lines, cur = [], "linked to:"
        for ob in others:
            nm = "p.%d" % first[ob]
            if len(cur) + len(nm) > 60:
                lines.append(cur)
                cur = ""
            cur += " " + nm
        lines.append(cur)
        for k, l in enumerate(lines[:2]):
            top.text(l.strip(), x + 3, y + 5.5 + k * 4.5, 1.8)
    fy = 52 + ((len(pages) - 1) // cols + 1) * (bh + 9)
    paper = paper_for(cols * (bw + 12) - 30, fy + 20)
    sch = sheet_file(d, top, paper, en.title(d.title) + " - readable schematic", 1,
                     "Generated by pcb/tools/leggibile.py from the same netlist as the PCB: do not edit by hand")
    sch += [["sheet_instances", ["path", Q("/"), ["page", Q("1")]]], ["embedded_fonts", "no"]]
    path = os.path.join(out, d.name + ".kicad_sch")
    with open(path, "w") as f:
        f.write(dump(sch) + "\n")
    print("  fili aggiunti dall'instradatore: %d" % nroute)
    # progetto minimo e tabella dei simboli: i simboli maelcum stanno nella cartella della scheda
    with open(os.path.join(out, d.name + ".kicad_pro"), "w") as f:
        json.dump({"meta": {"filename": d.name + ".kicad_pro", "version": 3}}, f, indent=2)
    with open(os.path.join(out, "sym-lib-table"), "w") as f:
        f.write('(sym_lib_table\n\t(version 7)\n\t(lib (name "maelcum")(type "KiCad")'
                '(uri "${KIPRJMOD}/../maelcum.kicad_sym")(options "")(descr "simboli di maelcum"))\n)\n')
    return d, path, out, bad


def verify(d, path, out, bad):
    bad = bad + ["senza traduzione inglese (leggibile_en.py) - " + m for m in dict.fromkeys(MISSING)]
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


def document(mods, dest="pcb/schematics-readable.pdf"):
    """Un PDF solo: copertina con l'indice, poi una pagina per scheda nell'ordine dato."""
    infos = []
    for m in mods:
        rp = json.loads(subprocess.run([sys.executable, __file__, "--info", m],
                                       capture_output=True, text=True).stdout)
        infos.append(rp)
    cover = os.path.join(os.path.dirname(dest), "schematics-cover.kicad_sch")
    uid_seed("copertina")
    root = _uuid()
    items = []

    def txt(s, x, y, size, bold=False):
        eff = ["effects", ["font", ["size", size, size]] + ([["bold", "yes"]] if bold else []),
               ["justify", "left", "bottom"]]
        items.append(["text", Q(s), ["exclude_from_sim", "no"], ["at", x, y, 0], eff, ["uuid", uid()]])

    npages = []
    for i in infos:
        out = subprocess.run(["/opt/homebrew/bin/pdfinfo", i["pdf"]], capture_output=True, text=True).stdout
        npages.append(int([l.split()[-1] for l in out.splitlines() if l.startswith("Pages:")][0]))
    txt("maelcum mixer - readable schematics of the generated boards", 25, 40, 6, True)
    txt("Each board opens with an index page, then one page per functional block, in signal order. Each drawing", 25, 52, 3)
    txt("is generated from the same netlist as the board's PCB and checked against it in both directions", 25, 58, 3)
    txt("(pcb/tools/leggibile.py). Values are PROVISIONAL drafts.", 25, 64, 3)
    txt("Page  Board", 25, 76, 3.5, True)
    page = 2
    for i, (m, info) in enumerate(zip(mods, infos)):
        txt("%3d   %s  (%d parts, %d pages)" % (page, info["title"], info["parts"], npages[i]), 25, 83 + i * 5.6, 2.6)
        page += npages[i]
    y = 83 + len(mods) * 5.6 + 10
    txt("How to read the drawings", 25, y, 3.5, True)
    legend = [
        "Signal flows from left to right; long chains wrap into bands, one under the other, and resume on the left.",
        "Arrow and ground symbols are power rails and grounds; the name under the symbol is the rail (AGND, +18V, -15SW ...).",
        "A plain name on a wire is a net that continues elsewhere on the same page; a name in a box goes to another page.",
        "Bypass capacitors, chip supply pins and unused op-amp units are collected on the POWER DECOUPLING page.",
        "Connectors and many-pin chips (C96, LM339, ADG1434) carry only names. Net names are the PCB identifiers.",
    ]
    for i, l in enumerate(legend):
        txt("- " + l, 25, y + 9 + i * 6.5, 2.6)
    sch = ["kicad_sch", ["version", 20260101], ["generator", Q("eeschema")], ["generator_version", Q("10.0")],
           ["uuid", Q(root)], ["paper", Q("A3"), "portrait"],
           ["title_block", ["title", Q("maelcum mixer - readable schematics")],
            ["comment", 1, Q("Generated by pcb/tools/leggibile.py")]],
           ["lib_symbols"]] + items + [["sheet_instances", ["path", Q("/"), ["page", Q("1")]]], ["embedded_fonts", "no"]]
    with open(cover, "w") as f:
        f.write(dump(sch) + "\n")
    cpdf = cover.replace(".kicad_sch", ".pdf")
    subprocess.run([CLI, "sch", "export", "pdf", "--black-and-white", "-o", cpdf, cover], capture_output=True)
    os.remove(cover)
    pdfs = [cpdf] + [i["pdf"] for i in infos]
    subprocess.run(["/opt/homebrew/bin/pdfunite"] + pdfs + [dest], check=True)
    os.remove(cpdf)
    print("documento: %s (%d pagine)" % (dest, len(pdfs)))


def info(m):
    path, _, arg = m.partition(":")
    sys.path.insert(0, os.path.dirname(os.path.abspath(path)))
    sys.argv = [path] + ([arg] if arg else [])
    d = runpy.run_path(path, run_name="leggibile")["d"]
    print(json.dumps({"title": en.title(d.title), "rev": en.rev(d.rev), "parts": len(d.parts),
                      "pdf": os.path.join(d.outdir, "leggibile", d.name + ".pdf")}))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--info":
        info(sys.argv[2])
        sys.exit(0)
    if len(sys.argv) == 2:
        sys.exit(0 if verify(*build(sys.argv[1])) else 1)
    # più moduli: un processo per modulo. Tre moduli hanno un cavo.py: nello stesso processo
    # Python riuserebbe quello del primo (sys.modules) e lo schema prenderebbe i fili sbagliati.
    ok = True
    for m in sys.argv[1:]:
        ok &= subprocess.run([sys.executable, __file__, m]).returncode == 0
    if ok:
        document(sys.argv[1:])
    sys.exit(0 if ok else 1)
