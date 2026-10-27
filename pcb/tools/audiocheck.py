"""Controllo audio di una PCB (sola lettura): disaccoppiamento, reti sensibili,
passivi vicini all'op-amp, accoppiamento capacitivo, distanza dai regolatori.

Uso come modulo (dal file di una scheda, pcb/<modulo>/<modulo>.py):
    import audiocheck
    r = audiocheck.check("pcb/fx-send/fx-send.kicad_pcb", rules={...})
    # r = {"regole": {"A1": [violazioni], ...}, "misure": {...}, "conteggio": {"A1": n, ...}}

Uso da riga di comando (Python di KiCad, serve pcbnew):
    <python di KiCad> pcb/tools/audiocheck.py <scheda.kicad_pcb>

Regole (soglie di default in SOGLIE, sostituibili con rules["soglie"]):
  A1 disaccoppiamento: ogni pin di alimentazione di ogni IC ha un C sulla stessa
     rete a <= 3 mm pad-pad (centro-centro) e <= 5 mm di pista; regolatori <= 10 mm
     pad-pad (la pista dei regolatori non e' vincolata).
  A2 reti sensibili: pista <= 25 mm e <= 1 via; reti del cavo <= 40 mm e <= 1 via.
  A3 passivi (R, C) sulle reti sensibili a <= 6 mm dal pin dell'op-amp.
  A4 somma delle C mutue stimate dalle reti rumorose verso una rete sensibile <= 0,05 pF.
  A5 nessuna pista sensibile dentro il riquadro di un regolatore allargato di 3 mm.
Ogni violazione e' un dict: regola, oggetto (rete o ref.pin), misura, soglia, nota.

Chiavi di rules (tutte facoltative):
  sensibili     regex dei nomi di rete sensibili (masse virtuali, ingressi invertenti)
  cavo          regex delle reti che viaggiano su un cavo (soglia di lunghezza piu' larga)
  rumorose      regex delle reti rumorose (commutazioni, logica, alimentazioni grezze)
  alimentazioni set dei nomi delle reti di alimentazione degli IC
  regolatori    lista dei riferimenti dei regolatori (anche transistor di passo)
  soglie        dict che sostituisce voci di SOGLIE

Default (euristiche, quando rules non dice niente):
  - IC = impronte col riferimento U*, piu' i regolatori.
  - alimentazioni = reti che toccano un pad di un IC, non sono masse (nome con
    "GND", oppure "0") e hanno un nome da tensione: comincia con +/- seguito da
    cifra (+18V, -15SW), contiene <cifre>V (+5VF, 3V3), oppure comincia con
    V<cifra>/VREG/VCC/VDD/VEE/VSS (V27F+, VREG-). I pin dei simboli KiCad
    generati da pcbgen non portano il tipo "power", quindi si guarda il nome.
    Restano fuori ADJ+, BASE+ e simili (nodi interni dei regolatori).
  - regolatori = impronte U* o Q* con al piu' 5 pad, di cui almeno due su
    alimentazioni diverse (ingresso e uscita: LM317, 78xx, transistor di passo).
  - sensibili e cavo: nessuna (A2, A3, A4, A5 non hanno oggetti da controllare).
  - rumorose: regex DEF_RUMOROSE (commutazioni, logica, bottoni, LED, rete grezza).

Modello fisico (stima, serve a confrontare layout, non a firmare un numero):
stackup 4 strati 1,6 mm tipo JLC 7628, piano a 0,21 mm sotto gli strati esterni;
C mutua fra piste parallele ~0,010 pF/mm a 0,25 mm di bordo, decade con
costante 0,25 mm, nulla oltre 2 mm; solo piste sullo stesso strato.
"""
import collections, heapq, math, re, sys, time

import pcbnew

TOMM = pcbnew.ToMM

SOGLIE = {
    "dec_padpad": 3.0,     # A1: C di disaccoppiamento, distanza pad-pad (mm)
    "dec_pista": 5.0,      # A1: C di disaccoppiamento, lunghezza di pista (mm)
    "reg_padpad": 10.0,    # A1: regolatori, distanza pad-pad (mm)
    "sens_len": 25.0,      # A2: pista di una rete sensibile (mm)
    "sens_via": 1,         # A2: via di una rete sensibile o del cavo
    "cavo_len": 40.0,      # A2: pista di una rete del cavo (mm)
    "passivo": 6.0,        # A3: passivo dal pin dell'op-amp, pad-pad (mm)
    "cm_pf": 0.05,         # A4: somma delle C mutue verso le reti rumorose (pF)
    "reg_margine": 3.0,    # A5: margine attorno al riquadro di un regolatore (mm)
    "passo": 0.25,         # campionamento delle piste sensibili (mm)
}

DEF_RUMOROSE = r"(SW|CLK|PWM|BTN|LED|MUTE|RAW|DIG|LOGIC)"
_VOLT_RE = re.compile(r"^[+-]\d|\d+V|^V(\d|REG|CC|DD|EE|SS)", re.I)

CM_MAX_GAP = 2.0       # oltre questa distanza bordo-bordo la C mutua vale zero


def c_mutual_pf_mm(s):
    """C mutua fra due piste parallele sopra un piano a 0,21 mm, a distanza
    bordo-bordo s (mm). Stima grezza: 0,010 pF/mm a 0,25 mm, decade con 0,25 mm."""
    return 0.010 * math.exp(-(s - 0.25) / 0.25) if s < CM_MAX_GAP else 0.0


def is_ground(net):
    return net == "0" or "GND" in net.upper()


def _seg_dist(px, py, ax, ay, cx, cy):
    """Distanza punto-segmento, tutto in mm."""
    dx, dy = cx - ax, cy - ay
    L = dx * dx + dy * dy
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(ax + t * dx - px, ay + t * dy - py)


# ---------------------------------------------------------------- lettura della scheda
class _Board:
    """Dati della scheda in mm, letti una volta sola."""

    def __init__(self, path):
        self.b = pcbnew.LoadBoard(path)
        self.pads = []   # (ref, num, net, x, y, pad)
        self.fps = {}
        for fp in self.b.GetFootprints():
            ref = fp.GetReference()
            self.fps[ref] = fp
            for p in fp.Pads():
                pos = p.GetPosition()
                self.pads.append((ref, p.GetNumber(), p.GetNetname(),
                                  TOMM(pos.x), TOMM(pos.y), p))
        self.tracks = []  # (net, layer, ax, ay, cx, cy, w, L, oggetto)
        self.vias = collections.Counter()
        self.via_obj = collections.defaultdict(list)
        for t in self.b.GetTracks():
            cls = t.GetClass()
            if cls == "PCB_TRACK":
                a, c = t.GetStart(), t.GetEnd()
                self.tracks.append((t.GetNetname(), t.GetLayer(), TOMM(a.x), TOMM(a.y),
                                    TOMM(c.x), TOMM(c.y), TOMM(t.GetWidth()),
                                    TOMM(t.GetLength()), t))
            elif cls == "PCB_VIA":
                self.vias[t.GetNetname()] += 1
                self.via_obj[t.GetNetname()].append(t)
        self.tr_by_net = collections.defaultdict(list)
        for t in self.tracks:
            self.tr_by_net[t[0]].append(t)
        self.pads_by_net = collections.defaultdict(list)
        for p in self.pads:
            self.pads_by_net[p[2]].append(p)
        self.zone_nets = {z.GetNetname() for z in self.b.Zones()}
        self.nets = sorted(n for n in set(self.tr_by_net) | set(self.pads_by_net) if n)
        self._graphs = {}

    # grafo del rame di una rete: nodi = pad, via, estremi di pista; archi = piste
    def graph(self, net):
        if net in self._graphs:
            return self._graphs[net]
        adj = collections.defaultdict(list)
        key = lambda x, y: (round(x, 3), round(y, 3))
        ends = []
        for _, lay, ax, ay, cx, cy, w, L, t in self.tr_by_net[net]:
            a, c = key(ax, ay), key(cx, cy)
            adj[a].append((c, L))
            adj[c].append((a, L))
            ends.append((a, t.GetStart(), lay))
            ends.append((c, t.GetEnd(), lay))
        for ref, num, _, x, y, p in self.pads_by_net[net]:
            pk = ("pad", ref, num)
            for k, pt, lay in ends:
                if p.IsOnLayer(lay) and p.HitTest(pt):
                    adj[pk].append((k, 0.0))
                    adj[k].append((pk, 0.0))
        for v in self.via_obj[net]:
            vp = v.GetPosition()
            vk = ("via", key(TOMM(vp.x), TOMM(vp.y)))
            for k, pt, lay in ends:
                if v.HitTest(pt):
                    adj[vk].append((k, 0.0))
                    adj[k].append((vk, 0.0))
        self._graphs[net] = adj
        return adj

    def path_len(self, net, src, dst):
        """Lunghezza di pista minima fra due pad della stessa rete (Dijkstra); None se
        le piste non li collegano."""
        adj = self.graph(net)
        dist = {src: 0.0}
        q = [(0.0, 0, src)]
        i = 1
        while q:
            dd, _, u = heapq.heappop(q)
            if u == dst:
                return dd
            if dd > dist.get(u, 1e9):
                continue
            for v, w in adj[u]:
                nd = dd + w
                if nd < dist.get(v, 1e9):
                    dist[v] = nd
                    heapq.heappush(q, (nd, i, v))
                    i += 1
        return None

    def bbox(self, ref):
        bb = self.fps[ref].GetBoundingBox(False, False)
        return (TOMM(bb.GetLeft()), TOMM(bb.GetTop()), TOMM(bb.GetRight()), TOMM(bb.GetBottom()))


def _viol(regola, oggetto, misura, soglia, nota=""):
    return {"regola": regola, "oggetto": oggetto, "misura": misura, "soglia": soglia, "nota": nota}


def _r1(x):
    return None if x is None else round(x, 2)


# ---------------------------------------------------------------- euristiche di default
def _default_alimentazioni(B, ic_like):
    nets = set()
    for ref, num, net, x, y, p in B.pads:
        if net and ref in ic_like and not is_ground(net) and _VOLT_RE.search(net):
            nets.add(net)
    return nets


def _default_regolatori(B, alim):
    regs = []
    for ref, fp in B.fps.items():
        if ref[:1] not in "UQ":
            continue
        pads = [p for p in B.pads if p[0] == ref]
        if len(pads) > 5:
            continue
        if len({p[2] for p in pads if p[2] in alim}) >= 2:
            regs.append(ref)
    return sorted(regs)


# ---------------------------------------------------------------- A1
def _a1(B, ics, regs, alim, S, out, misure):
    worst_pp, worst_L = (0.0, ""), (0.0, "")
    for ref, num, net, x, y, p in B.pads:
        if ref not in ics or net not in alim:
            continue
        ogg = "%s.%s (%s)" % (ref, num, net)
        is_reg = ref in regs
        cands = [(math.hypot(x2 - x, y2 - y), r2, n2) for r2, n2, _, x2, y2, _p in B.pads_by_net[net]
                 if r2.startswith("C") and r2 != ref]
        if not cands:
            out.append(_viol("A1", ogg, None, S["reg_padpad"] if is_reg else S["dec_padpad"],
                             "nessun condensatore sulla rete"))
            continue
        dpp, cr, cn = min(cands)
        if is_reg:
            if dpp > S["reg_padpad"]:
                out.append(_viol("A1", ogg, _r1(dpp), S["reg_padpad"], "regolatore, C piu' vicino %s" % cr))
            continue
        L = B.path_len(net, ("pad", ref, num), ("pad", cr, cn))
        if dpp > worst_pp[0]:
            worst_pp = (dpp, "%s -> %s" % (ogg, cr))
        if L is not None and L > worst_L[0]:
            worst_L = (L, "%s -> %s" % (ogg, cr))
        if dpp > S["dec_padpad"]:
            out.append(_viol("A1", ogg, _r1(dpp), S["dec_padpad"],
                             "pad-pad verso %s, pista %s mm" % (cr, "%.1f" % L if L is not None else "n/c")))
        elif L is None and net not in B.zone_nets:
            out.append(_viol("A1", ogg, None, S["dec_pista"], "%s non collegato da piste" % cr))
        elif L is not None and L > S["dec_pista"]:
            out.append(_viol("A1", ogg, _r1(L), S["dec_pista"], "pista verso %s (pad-pad %.1f mm)" % (cr, dpp)))
    misure["A1_padpad_max_mm"] = (_r1(worst_pp[0]), worst_pp[1])
    misure["A1_pista_max_mm"] = (_r1(worst_L[0]), worst_L[1])


# ---------------------------------------------------------------- A2
def _a2(B, sens, cavo_re, S, out, misure):
    wl, wv = (0.0, ""), (0, "")
    for n in sens:
        L = sum(t[7] for t in B.tr_by_net[n])
        nv = B.vias[n]
        lim = S["cavo_len"] if cavo_re and cavo_re.match(n) else S["sens_len"]
        if L > wl[0]:
            wl = (L, n)
        if nv > wv[0]:
            wv = (nv, n)
        if L > lim:
            out.append(_viol("A2", n, _r1(L), lim, "lunghezza di pista (mm)"))
        if nv > S["sens_via"]:
            out.append(_viol("A2", n, nv, S["sens_via"], "numero di via"))
    misure["A2_lunghezza_max_mm"] = (_r1(wl[0]), wl[1])
    misure["A2_via_max"] = wv


# ---------------------------------------------------------------- A3
def _a3(B, sens, opamps, S, out, misure):
    worst = (0.0, "")
    for n in sens:
        pp = B.pads_by_net[n]
        op = [(r, num, x, y) for r, num, _, x, y, _p in pp if r in opamps]
        pas = [(r, num, x, y) for r, num, _, x, y, _p in pp if r[:1] in "RC" and not r.startswith("CP")]
        if not op or not pas:
            continue
        for r, num, x, y in pas:
            dd, o = min((math.hypot(x - ox, y - oy), (orf, onum)) for orf, onum, ox, oy in op)
            if dd > worst[0]:
                worst = (dd, "%s.%s -> %s.%s (%s)" % (r, num, o[0], o[1], n))
            if dd > S["passivo"]:
                L = B.path_len(n, ("pad", o[0], o[1]), ("pad", r, num))
                out.append(_viol("A3", "%s.%s (%s)" % (r, num, n), _r1(dd), S["passivo"],
                                 "dal pin %s.%s, pista %s mm" % (o[0], o[1], "%.1f" % L if L is not None else "n/c")))
    misure["A3_distanza_max_mm"] = (_r1(worst[0]), worst[1])


# ---------------------------------------------------------------- A4 + A5
def _a4_a5(B, sens, noisy_re, regs, S, out4, out5, misure):
    """Campiona ogni pista sensibile ogni S['passo'] mm. Per ogni rete rumorosa sullo
    stesso strato prende la distanza bordo-bordo minima e somma la C mutua stimata.
    Prefiltro: solo le piste rumorose il cui riquadro tocca quello della pista
    sensibile allargato di 2 mm (oltre, la C mutua e' zero)."""
    noisy = [t for t in B.tracks if noisy_re and noisy_re.match(t[0])]
    nbox = [(t, min(t[2], t[4]) - t[6] / 2, min(t[3], t[5]) - t[6] / 2,
             max(t[2], t[4]) + t[6] / 2, max(t[3], t[5]) + t[6] / 2) for t in noisy]
    rboxes = []
    for r in regs:
        if r in B.fps:
            l, tp, rt, bt = B.bbox(r)
            rboxes.append((r, l, tp, rt, bt))
    step, marg = S["passo"], S["reg_margine"]
    worst_cm, worst_reg = (0.0, ""), (99.0, "")
    for n in sens:
        cm = collections.defaultdict(float)
        gapmin = {}
        dreg = (99.0, "")
        for _, lay, ax, ay, cx, cy, w, L, _t in B.tr_by_net[n]:
            m = CM_MAX_GAP + w / 2
            bx0, by0 = min(ax, cx) - m, min(ay, cy) - m
            bx1, by1 = max(ax, cx) + m, max(ay, cy) + m
            near = [(t[0], t[2], t[3], t[4], t[5], t[6]) for t, x0, y0, x1, y1 in nbox
                    if t[1] == lay and x0 <= bx1 and x1 >= bx0 and y0 <= by1 and y1 >= by0]
            k = max(1, int(L / step))
            dl = L / k
            for i in range(k):
                f = (i + 0.5) / k
                px, py = ax + f * (cx - ax), ay + f * (cy - ay)
                best = {}
                for nn, nax, nay, ncx, ncy, nw in near:
                    g = _seg_dist(px, py, nax, nay, ncx, ncy) - (w + nw) / 2
                    if g < best.get(nn, 99.0):
                        best[nn] = g
                for nn, g in best.items():
                    if g < gapmin.get(nn, 99.0):
                        gapmin[nn] = g
                    cm[nn] += c_mutual_pf_mm(max(g, 0.2)) * dl
                for r, l, tp, rt, bt in rboxes:
                    qx, qy = min(max(px, l), rt), min(max(py, tp), bt)
                    dd = math.hypot(px - qx, py - qy)
                    if dd < dreg[0]:
                        dreg = (dd, r)
        tot = sum(cm.values())
        top = sorted(cm.items(), key=lambda kv: -kv[1])[:2]
        nota = "; ".join("%s %.3f pF (gap %.2f mm)" % (k, v, gapmin[k]) for k, v in top if v > 0)
        if tot > worst_cm[0]:
            worst_cm = (tot, n)
        if tot > S["cm_pf"]:
            out4.append(_viol("A4", n, round(tot, 4), S["cm_pf"], nota))
        if dreg[0] < worst_reg[0]:
            worst_reg = (dreg[0], "%s vicino a %s" % (n, dreg[1]))
        if dreg[0] <= marg:
            out5.append(_viol("A5", n, _r1(dreg[0]), marg, "distanza dal riquadro di %s (mm)" % dreg[1]))
    misure["A4_cm_max_pf"] = (round(worst_cm[0], 4), worst_cm[1])
    misure["A5_distanza_min_mm"] = (_r1(worst_reg[0]), worst_reg[1])


# ---------------------------------------------------------------- API
def check(pcb_path, rules=None):
    """Controlla la scheda e ritorna {"regole", "misure", "conteggio"} (vedi in testa)."""
    rules = rules or {}
    S = dict(SOGLIE)
    S.update(rules.get("soglie") or {})
    B = _Board(pcb_path)

    sens_re = re.compile(rules["sensibili"]) if rules.get("sensibili") else None
    cavo_re = re.compile(rules["cavo"]) if rules.get("cavo") else None
    noisy_re = re.compile(rules.get("rumorose") or DEF_RUMOROSE)

    u_refs = {r for r in B.fps if r.startswith("U")}
    if rules.get("alimentazioni"):
        alim = set(rules["alimentazioni"])
    else:
        alim = _default_alimentazioni(B, u_refs | {r for r in B.fps if r.startswith("Q")})
    regs = list(rules["regolatori"]) if rules.get("regolatori") else _default_regolatori(B, alim)
    ics = u_refs | set(regs)
    opamps = u_refs - set(regs)

    # sensibili: quelle della regex, piu' quelle del cavo (controllate con la soglia larga)
    sens = [n for n in B.nets if (sens_re and sens_re.match(n)) or (cavo_re and cavo_re.match(n))]

    regole = {k: [] for k in ("A1", "A2", "A3", "A4", "A5")}
    misure = {"alimentazioni": sorted(alim), "regolatori": regs, "reti_sensibili": len(sens)}
    _a1(B, ics, set(regs), alim, S, regole["A1"], misure)
    _a2(B, sens, cavo_re, S, regole["A2"], misure)
    _a3(B, sens, opamps, S, regole["A3"], misure)
    _a4_a5(B, sens, noisy_re, regs, S, regole["A4"], regole["A5"], misure)
    return {"regole": regole, "misure": misure,
            "conteggio": {k: len(v) for k, v in regole.items()}}


# ---------------------------------------------------------------- riassunto
NOMI = {
    "A1": "disaccoppiamento degli IC",
    "A2": "lunghezza e via delle reti sensibili",
    "A3": "passivi vicino al pin dell'op-amp",
    "A4": "accoppiamento verso reti rumorose",
    "A5": "piste sensibili vicino ai regolatori",
}


def _peggiore(regola, vv):
    num = [v for v in vv if isinstance(v["misura"], (int, float))]
    if not num:
        return vv[0]
    if regola == "A5":
        return min(num, key=lambda v: v["misura"])
    return max(num, key=lambda v: v["misura"] / v["soglia"] if v["soglia"] else v["misura"])


def riassunto(res):
    """Testo leggibile: una riga per regola."""
    righe = []
    for k in ("A1", "A2", "A3", "A4", "A5"):
        vv = res["regole"][k]
        if not vv:
            righe.append("%s %-38s OK" % (k, NOMI[k]))
            continue
        w = _peggiore(k, vv)
        righe.append("%s %-38s %3d violazioni; peggiore %s: %s (soglia %s) %s" % (
            k, NOMI[k], len(vv), w["oggetto"], w["misura"], w["soglia"], w["nota"]))
    return "\n".join(righe)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("uso: audiocheck.py <scheda.kicad_pcb>")
    path = sys.argv[1]
    rules = None
    if path.endswith("fx-send.kicad_pcb"):
        # regole di PROVA per FX-SEND: il posto giusto e' pcb/fx-send/fx-send.py
        rules = {
            "sensibili": r"^(NB|NSH|NVH|NHB|VPRE|SEND_IN|INJ\d|S\d_OUT)_[LR]$",
            "cavo": r"^(NA|NB|NC)_[LR]$",
            "rumorose": r"^(\+15SW|-15SW|ASG\d|MUTE_G|GLOBAL_MUTE|\+5VF?|BTN\d|MD\d|SW\d_[LR]"
                        r"|V27F[+-]|VREG[+-]|BASE[+-]|RAW.*|CTRL_GND)$",
            "regolatori": ["U10", "U11", "U12", "U13", "Q1", "Q2"],
        }
    t0 = time.time()
    res = check(path, rules)
    dt = time.time() - t0
    m = res["misure"]
    print("scheda:", path)
    print("alimentazioni:", ", ".join(m["alimentazioni"]) or "-")
    print("regolatori:", ", ".join(m["regolatori"]) or "-", "| reti sensibili:", m["reti_sensibili"])
    print(riassunto(res))
    print("misure peggiori:")
    for k, v in m.items():
        if k[:2] in ("A1", "A2", "A3", "A4", "A5"):
            print("  %-20s %s" % (k, v))
    print("tempo: %.1f s" % dt)
