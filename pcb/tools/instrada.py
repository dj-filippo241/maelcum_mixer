"""Instradatore dei fili dello schema leggibile (pcb/tools/leggibile.py).

Dopo il disegno di una pagina, le reti spezzate in più pezzi (unite solo dalle etichette) si
collegano con fili veri dove c'è un percorso libero: griglia di 1,27 mm, ostacoli = corpi dei
simboli, linee dei pin, testi, punti di altre reti. Un filo di un'altra rete si può incrociare ad
angolo retto (senza punto di giunzione), mai percorrere per lungo né toccare in un suo estremo.
Un percorso troppo lungo rispetto alla distanza vera si scarta: l'etichetta resta.
"""
import heapq, math

G1 = 1.27


def cell(x, y):
    return (int(round(x / G1)), int(round(y / G1)))


def _num(v):
    return float(v)


def _walk(node, out):
    """Coordinate del disegno di un simbolo (libreria, y in su)."""
    if not isinstance(node, list) or not node:
        return
    k = node[0]
    if k in ("start", "end", "xy", "mid") and len(node) >= 3:
        out.append((_num(node[1]), _num(node[2])))
        return
    if k == "circle":
        c = [n for n in node if isinstance(n, list) and n and n[0] == "center"]
        r = [n for n in node if isinstance(n, list) and n and n[0] == "radius"]
        if c and r:
            cx, cy, rr = _num(c[0][1]), _num(c[0][2]), _num(r[0][1])
            out += [(cx - rr, cy - rr), (cx + rr, cy + rr)]
        return
    if k in ("pin", "text", "property"):
        return
    for n in node[1:]:
        _walk(n, out)


_geo = {}


def geometry(sym, unit):
    """(punti del corpo, [(x, y, ang, lunghezza)] dei pin) dell'unità, in coordinate di libreria."""
    key = (sym.lib_id, unit)
    if key in _geo:
        return _geo[key]
    body, pins = [], []
    for sub in sym.sexpr:
        if not (isinstance(sub, list) and sub and sub[0] == "symbol"):
            continue
        u, st = str(sub[1]).rsplit("_", 2)[-2:]
        if int(st) == 2 or int(u) not in (0, unit):
            continue
        for n in sub[2:]:
            if isinstance(n, list) and n and n[0] == "pin":
                at = [m for m in n if isinstance(m, list) and m and m[0] == "at"][0]
                ln = [m for m in n if isinstance(m, list) and m and m[0] == "length"]
                pins.append((_num(at[1]), _num(at[2]), int(float(at[3])) if len(at) > 3 else 0,
                             _num(ln[0][1]) if ln else 2.54))
            else:
                _walk(n, body)
    _geo[key] = (body, pins)
    return _geo[key]


class Router:
    def __init__(self):
        self.hard = set()          # celle vietate a tutti
        self.labtext = {}          # cella -> reti delle etichette il cui testo la copre
        self.pt = {}               # cella -> rete dei punti (pin, estremi, etichette); None = no connect
        self.wh, self.wv = {}, {}  # cella -> rete del filo orizzontale / verticale che la percorre
        self.ends = {}             # cella -> numero di estremi di filo (per le giunzioni)
        self.bbox = None

    # ------------------------------------------------------------ ostacoli
    def _grow(self, c):
        if self.bbox is None:
            self.bbox = [c[0], c[1], c[0], c[1]]
        b = self.bbox
        b[0], b[1], b[2], b[3] = min(b[0], c[0]), min(b[1], c[1]), max(b[2], c[0]), max(b[3], c[1])

    def box(self, x1, y1, x2, y2, net=None):
        a, b = cell(min(x1, x2), min(y1, y2)), cell(max(x1, x2), max(y1, y2))
        for i in range(a[0], b[0] + 1):
            for j in range(a[1], b[1] + 1):
                if net is None:
                    self.hard.add((i, j))
                else:
                    self.labtext.setdefault((i, j), set()).add(net)
        self._grow(a)
        self._grow(b)

    def symbol(self, sym, unit, sx, sy, r, rotv):
        body, pins = geometry(sym, unit)
        pts = []
        for x, y in body:
            dx, dy = rotv(x, y, r)
            pts.append((sx + dx, sy - dy))
        for x, y, ang, ln in pins:
            a = math.radians(ang)
            ix, iy = x + ln * round(math.cos(a)), y + ln * round(math.sin(a))
            dx, dy = rotv(ix, iy, r)
            pts.append((sx + dx, sy - dy))
            ox, oy = rotv(x, y, r)
            # la linea del pin, senza l'estremo esterno
            c0, c1 = cell(sx + ox, sy - oy), cell(sx + dx, sy - dy)
            n = max(abs(c1[0] - c0[0]), abs(c1[1] - c0[1]))
            for k in range(1, n + 1):
                self.hard.add((c0[0] + (c1[0] - c0[0]) * k // n, c0[1] + (c1[1] - c0[1]) * k // n))
        if pts:
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            self.box(min(xs), min(ys), max(xs), max(ys))

    def point(self, x, y, net):
        c = cell(x, y)
        self.pt[c] = net if c not in self.pt or self.pt[c] == net else "#conflitto"
        self._grow(c)

    def seg(self, x1, y1, x2, y2, net):
        a, b = cell(x1, y1), cell(x2, y2)
        self.ends[a] = self.ends.get(a, 0) + 1
        self.ends[b] = self.ends.get(b, 0) + 1
        if a[1] == b[1]:
            for i in range(min(a[0], b[0]), max(a[0], b[0]) + 1):
                self.wh[(i, a[1])] = net
        else:
            for j in range(min(a[1], b[1]), max(a[1], b[1]) + 1):
                self.wv[(a[0], j)] = net
        self._grow(a)
        self._grow(b)

    # ------------------------------------------------------------ ricerca
    def blocked(self, c, net):
        if c in self.hard:
            return True
        lt = self.labtext.get(c)
        if lt and (lt - {net}):
            return True
        p = self.pt.get(c, net)
        return p != net

    def route(self, net, starts, goals, limit):
        """Percorso a costo minimo da una cella di starts a una di goals. Rende la lista di celle."""
        if not goals:
            return None
        b = self.bbox
        gx = [g[0] for g in goals]
        gy = [g[1] for g in goals]
        sx = [s[0] for s in starts]
        sy = [s[1] for s in starts]
        m = 14
        lo_x, hi_x = max(b[0] - 4, min(gx + sx) - m), min(b[2] + 4, max(gx + sx) + m)
        lo_y, hi_y = max(b[1] - 4, min(gy + sy) - m), min(b[3] + 4, max(gy + sy) + m)
        gset = set(goals)

        def h(c):
            return min(abs(c[0] - g[0]) + abs(c[1] - g[1]) for g in goals[:40])

        D = ((1, 0), (-1, 0), (0, 1), (0, -1))
        best = {}
        heap = []
        for s in starts:
            for k in range(4):
                best[(s, k)] = 0
                heapq.heappush(heap, (h(s), 0, s, k, None))
        prev = {}
        while heap:
            f, cost, c, k, par = heapq.heappop(heap)
            if cost > best.get((c, k), 1e9) or cost > limit:
                continue
            if c in gset and par is not None:
                path = [c]
                st = (c, k)
                while st in prev:
                    st = prev[st]
                    path.append(st[0])
                return path[::-1]
            cross_here = c in self.wh and self.wh[c] != net or c in self.wv and self.wv[c] != net
            for k2, (dx, dy) in enumerate(D):
                if par is not None and (dx, dy) == (-D[k][0], -D[k][1]):
                    continue
                turn = par is not None and k2 != k
                if turn and cross_here:
                    continue
                n = (c[0] + dx, c[1] + dy)
                if not (lo_x <= n[0] <= hi_x and lo_y <= n[1] <= hi_y):
                    continue
                if n in gset:
                    # si arriva su un pezzo della rete: non per lungo sopra un suo filo
                    if (dx != 0 and self.wh.get(n) == net and self.wh.get(c) == net) or \
                       (dy != 0 and self.wv.get(n) == net and self.wv.get(c) == net):
                        continue
                    if (dx != 0 and n in self.wh and self.wh[n] != net) or (dy != 0 and n in self.wv and self.wv[n] != net):
                        continue
                    nc = cost + 1 + (4 if turn else 0)
                else:
                    if self.blocked(n, net):
                        continue
                    if n in self.wh or n in self.wv:
                        if self.wh.get(n) == net or self.wv.get(n) == net:
                            continue
                        if dx != 0 and n in self.wh or dy != 0 and n in self.wv:
                            continue          # per lungo su un filo di un'altra rete
                        if n in self.ends:
                            continue          # estremo di un filo di un'altra rete
                        nc = cost + 1 + (4 if turn else 0) + 6
                    else:
                        nc = cost + 1 + (4 if turn else 0)
                if nc < best.get((n, k2), 1e9):
                    best[(n, k2)] = nc
                    prev[(n, k2)] = (c, k)
                    heapq.heappush(heap, (nc + h(n), nc, n, k2, c))
        return None


def segments(path):
    """Celle di un percorso -> segmenti rettilinei (estremi in celle)."""
    segs = []
    a = path[0]
    for i in range(1, len(path) - 1):
        p, c, n = path[i - 1], path[i], path[i + 1]
        if (c[0] - p[0], c[1] - p[1]) != (n[0] - c[0], n[1] - c[1]):
            segs.append((a, c))
            a = c
    segs.append((a, path[-1]))
    return segs
