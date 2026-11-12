#!/usr/bin/env python3
"""Backplane a tratti per la disposizione F (todo 269): slot, reti, tratti e cavi.

Uso: python3 pcb/backplane/piano_f.py      (Python puro, senza KiCad)
Scrive pcb/backplane/PIANO.md e si ferma con codice 1 se un controllo non passa.

Fonti:
- posizioni delle schede: pcb/tools/piano_schede.py --f (pcb/PIANO-SCHEDE-F.md) e
  docs/pannelli/proposta_f.py; x = 0 a sinistra del pannello, y = 0 dietro, y cresce verso chi suona;
- pin del C96 di ogni scheda: il netlist vero, pcb/<modulo>/out/netlist.xml (J1); 5-way e filtro
  non hanno ancora una scheda: riga b da docs/fase3/sistema-backplane.md §4 (SINTETICO);
- reti per posizione: sistema-backplane.md §4-§5 e REV dec. 130 (il numero del bus di un FX-RET,
  i bit FILT_MODE e i net CUE di un canale li decide lo slot, non la scheda);
- PTC per slot e per rail: sistema-psu-esterno.md §4.3.

Geometria del C96 (impronte KiCad): il maschio ad angolo retto sta a x = 50 della scheda di modulo,
ruotato di 180 gradi, quindi a1 sta a 89,37 mm dall'inizio della scheda e a32 a 10,63. La femmina
verticale del backplane mette a1 nello stesso punto del pavimento. La linea del posto è il piano
medio della scheda di modulo; la fila a della femmina sta 2,11 mm più in là, verso la fila c
(disegno Harting 09 03 196 6921, todo 302: tratto.FILA_A_DAL_PIANO).
"""
import os
import sys
import xml.etree.ElementTree as ET

QUI = os.path.dirname(os.path.abspath(__file__))
PCB = os.path.join(QUI, "..")
sys.path.insert(0, os.path.join(PCB, "tools"))
from backplane import c96, A_STANDARD, RIGA_A   # noqa: E402

A1, A32 = 89.37, 10.63           # a1 e a32 dall'inizio della scheda di modulo (C96 a x = 50, ruotato 180)
RAIL = ["RAW+27", "RAW-27", "RAW+22", "RAW-22", "RAW+26", "RAW-26", "+5V"]
MASSE = ["AGND", "CTRL_GND", "CHASSIS"]

# ------------------------------------------------------------------------------------------------
# Disposizione F (proposta_f.py): colonna sinistra x 0-200 (strisce canale da 50), colonna destra
# x 206-450 (strisce da 61); y: master 0-48, 5-way 48-150, filtro e MIC/MONO da 150, canali 201,
# ritorni 340, CUE 517,85. File delle schede sinistra-destra: piano_schede.py --f.
Y_MAS, Y_5W = 24.0, [60.75, 86.25, 111.75, 137.25]
Y_FIL = [162.75, 188.25]
Y_CUE = 530.85
Y_CAN, Y_MM, Y_RET = 201.0, 150.0, 340.0
X_DES, W_DES = 206.0, 61.0


def lr(x0, y, a1=A1, a32=A32):
    """Scheda sinistra-destra che parte a x0 sulla fila y: C96 lungo x, a1 a destra."""
    return (x0 + a1, y), (x0 + a32, y)


def dd(x, y0):
    """Scheda dietro-davanti sulla linea x che parte a y0: C96 lungo y, a1 verso chi suona."""
    return (x, y0 + A1), (x, y0 + A32)


# ------------------------------------------------------------------------------------------------
# Tratti: rettangoli sul pavimento (x0, y0, x1, y1). Uno per zona; i net che passano da un tratto
# all'altro vanno su un cavo (CAVI sotto). [C, PROVVISORIO]
TRATTI = {
    "T1": ("fondo: MASTER, 5-WAY, PSU-IN", (0.0, 10.0, 450.0, 148.0)),
    "T2": ("canali: FILTRO, 4 CANALI, 4 FX-SEND", (0.0, 152.0, 200.0, 318.0)),
    "T3": ("cuffie: CUE", (0.0, 515.0, 200.0, 555.0)),
    "T4": ("destra: MIC, 3 MONO, 4 FX-RET", (206.0, 150.0, 450.0, 446.0)),
}


def netlist_c96(rel):
    """Pin del C96 (J1) di una scheda vera: {pin: rete}, senza i pin liberi."""
    t = ET.parse(os.path.join(PCB, rel, "out", "netlist.xml"))
    out = {}
    for net in t.iter("net"):
        name = net.get("name")
        for node in net.iter("node"):
            if node.get("ref") == "J1" and not name.startswith("unconnected"):
                out[node.get("pin")] = name
    return out


def agnd_b(b):
    for s in range(1, 11):
        b["b%d" % (3 * s)] = "AGND"
    return b


# SINTETICI: schede non ancora scritte (sistema-backplane.md §4). 5-way: slot 1 DJBUS in, slot 2
# MSUM out; seconda scheda solo alimentazione, come le uscite del master (dec. 143). Filtro: slot 1-2
# bus HPF e LPF in, slot 3-4 uscite sul DJ bus, c1-c8 FILT_MODE; seconda scheda solo alimentazione.
SINT = {
    "5w1": c96(agnd_b({"b1": "DJBUS_L", "b2": "DJBUS_R", "b4": "MSUM_OUT_L", "b5": "MSUM_OUT_R"})),
    "5w2": c96({}, a=A_STANDARD),
    "fil1": c96(agnd_b({"b1": "BUS_HPF_L", "b2": "BUS_HPF_R", "b4": "BUS_LPF_L", "b5": "BUS_LPF_R",
                        "b7": "HPF_OUT_L", "b8": "HPF_OUT_R", "b10": "LPF_OUT_L", "b11": "LPF_OUT_R"}),
                c=["c%d" % k for k in range(1, 9)]),
    "fil2": c96({}, a=A_STANDARD),
}

# PTC per slot e per rail: corrente di tenuta in A (psu-esterno §4.3, max di backplane §6).
# NOTA: valori di classe; la PTC regge >= 33 V (raw +-27 a vuoto ~29 V).
PTC = {
    "canale": {"27": 0.3, "22": 0.1, "5": 0.2},
    "fx-send": {"27": 0.1, "22": 0.05, "5": 0.05},
    "fx-ret": {"27": 0.2, "22": 0.1, "5": 0.2},
    "mic": {"27": 0.1, "22": 0.1, "5": 0.1},
    "mono": {"27": 0.1, "22": 0.05, "5": 0.1},
    "cue": {"27": 0.5, "22": 0.1, "5": 0.1},
    "master": {"27": 0.3, "22": 0.1, "5": 0.1},
    "uscita": {"26": 0.2, "5": 0.2},
    "5way": {"27": 0.5, "22": 0.05, "5": 0.1},
    "filtro": {"27": 0.3, "22": 0.3, "5": 0.1},
}


class Slot:
    def __init__(self, nome, tratto, classe, pins, a1, a32, rinomina, ptc, sorgente):
        self.nome, self.tratto, self.classe = nome, tratto, classe
        self.pins_modulo = pins            # pin -> rete come la chiama la scheda di modulo
        self.a1, self.a32 = a1, a32
        self.rinomina, self.ptc, self.sorgente = rinomina, ptc, sorgente

    def rete(self, pin):
        """Rete del backplane su un pin dello slot."""
        n = self.pins_modulo[pin]
        if n in self.rinomina:
            return self.rinomina[n]
        base = n
        if base in RAIL and self.classe != "psu-in":
            if base == "RAW+22" and self.classe == "uscita":
                return base                 # solo lettura del supervisore: niente PTC
            return "%s_%s" % (base, self.nome)
        return base

    def reti(self):
        return {p: self.rete(p) for p in self.pins_modulo}

    def rail(self):
        """Rail che lo slot prende dal tronco attraverso una PTC: {tronco: rete dello slot}."""
        out = {}
        for p, n in self.pins_modulo.items():
            r = self.rete(p)
            if n in RAIL and r != n:
                out[n] = r
        return out


def slots():
    S = []
    ch = netlist_c96("canale")
    fs = netlist_c96("fx-send")
    fr = netlist_c96("fx-ret")
    for i in range(4):
        n = i + 1
        x = 50.0 * i
        a1, a32 = dd(x + 12.5, Y_CAN)
        S.append(Slot("CH%d" % n, "T2", "canale", ch, a1, a32,
                      {"CUE_OUT_L": "CUE%d_L" % n, "CUE_OUT_R": "CUE%d_R" % n,
                       "SEND_TAP_L": "SEND_TAP%d_L" % n, "SEND_TAP_R": "SEND_TAP%d_R" % n,
                       "FILT_MODE1_0": "FILT_MODE%d_0" % n, "FILT_MODE1_1": "FILT_MODE%d_1" % n},
                      PTC["canale"], "pcb/canale (netlist)"))
        a1, a32 = dd(x + 37.5, Y_CAN)
        rin = {"SEND_IN_L": "SEND_TAP%d_L" % n, "SEND_IN_R": "SEND_TAP%d_R" % n}
        for k in range(1, 5):
            rin.update({"S%d_OUT_L" % k: "S%d_L" % k, "S%d_OUT_R" % k: "S%d_R" % k})
        S.append(Slot("SEND%d" % n, "T2", "fx-send", fs, a1, a32, rin, PTC["fx-send"], "pcb/fx-send (netlist)"))
    for k, y in enumerate(Y_FIL):
        a1, a32 = lr(0.0, y)
        rin = {"HPF_OUT_L": "DJBUS_L", "HPF_OUT_R": "DJBUS_R", "LPF_OUT_L": "DJBUS_L", "LPF_OUT_R": "DJBUS_R"}
        S.append(Slot("FIL%d" % (k + 1), "T2", "filtro", SINT["fil%d" % (k + 1)], a1, a32, rin, PTC["filtro"],
                      "SINTETICO (backplane §4, dec. 159)"))
    a1, a32 = lr(2.0, Y_CUE, A1 + 48.0, A32 + 48.0)       # CUE: C96 a L/2 = 98 su 196 mm (cue.py)
    S.append(Slot("CUE", "T3", "cue", netlist_c96("cue"), a1, a32, {"MON_L": "MON_L", "MON_R": "MON_R"},
                  PTC["cue"], "pcb/cue (netlist)"))
    for i in range(4):
        xl = X_DES + W_DES * i + W_DES / 4
        a1, a32 = dd(xl, Y_MM)
        rin = {}
        for k in range(1, 5):
            rin.update({"S%d_OUT_L" % k: "S%d_L" % k, "S%d_OUT_R" % k: "S%d_R" % k})
        if i == 0:
            S.append(Slot("MIC", "T4", "mic", netlist_c96("mic"), a1, a32, rin, PTC["mic"], "pcb/mic (netlist)"))
        else:
            S.append(Slot("MONO%d" % i, "T4", "mono", netlist_c96("mono"), a1, a32, rin, PTC["mono"],
                          "pcb/mono (netlist)"))
        a1, a32 = dd(xl, Y_RET)
        n = i + 1
        rin2 = dict(rin)
        rin2.update({"BUS_IN_L": "S%d_L" % n, "BUS_IN_R": "S%d_R" % n,
                     "RET_OUT_L": "MSUM%d_L" % (n + 1), "RET_OUT_R": "MSUM%d_R" % (n + 1)})
        S.append(Slot("RET%d" % n, "T4", "fx-ret", fr, a1, a32, rin2, PTC["fx-ret"], "pcb/fx-ret (netlist)"))
    # fondo: master (segnale 0-171, uscita L 171-271, uscita R 271-371), 5-way, PSU-IN
    ms = netlist_c96(os.path.join("master", "segnale"))
    a1, a32 = lr(0.0, Y_MAS)
    S.append(Slot("MAS", "T1", "master", ms, a1, a32,
                  {"MSUM1_L": "MSUM1_L", "MON_OUT_L": "MON_L", "MON_OUT_R": "MON_R"},
                  PTC["master"], "pcb/master/segnale (netlist)"))
    for lato, x0 in (("L", 171.0), ("R", 271.0)):
        a1, a32 = lr(x0, Y_MAS)
        S.append(Slot("OUT_" + lato, "T1", "uscita", netlist_c96(os.path.join("master", "uscita-" + lato)),
                      a1, a32, {}, PTC["uscita"], "pcb/master/uscita-%s (netlist)" % lato))
    for k in range(2):
        a1, a32 = lr(0.0, Y_5W[k])
        S.append(Slot("5W%d" % (k + 1), "T1", "5way", SINT["5w%d" % (k + 1)], a1, a32,
                      {"MSUM_OUT_L": "5W_OUT_L", "MSUM_OUT_R": "5W_OUT_R"}, PTC["5way"],
                      "SINTETICO (backplane §4)"))
    a1, a32 = lr(350.0, Y_5W[3])     # fila 4 sotto il 5-way, libera; vicino alla colonna destra
    S.append(Slot("PSU", "T1", "psu-in", netlist_c96("psu-in"), a1, a32, {}, {}, "pcb/psu-in (netlist)"))
    return S


# ------------------------------------------------------------------------------------------------
# Ponticelli di continuità sul tratto (dec. 111): si tolgono quando c'è il modulo opzionale.
PONTICELLI = {
    "T1": [("J5W", ["5W_OUT_L", "MSUM1_L", "5W_OUT_R", "MSUM1_R"], "5-way -> MSUM1 (EQ grafico dopo il 5-way)"),
           ("JMS", ["INS_SEND_L", "INS_RET_L", "INS_SEND_R", "INS_RET_R"], "inserzione del master (EQ grafico)"),
           ],
}
# Prese di predisposizione (dec. 111): uscite per via dal master; nessuno slot nella disposizione F.
PRESE = {"T1": [("JVIE", ["VIE_TAP_L", "AGND", "VIE_TAP_R"], "VIE_TAP del master (UTIL-VIE, dec. 111)")]}

# Cavi fra tratti. Un cavo di segnale porta o solo net a massa virtuale (VE) o solo linee pilotate:
# mai insieme (backplane §4 REV todo 133: <= 0,2 pF fra un net VE e una linea pilotata). Nel cavo
# piatto ogni filo di segnale sta fra due fili di massa. Alimentazione su cavi suoi, uno per tratto,
# ognuno col suo ritorno AGND fino al tratto del PSU-IN (stella, grounding §2).
CAVI = [
    ("C1", "T1", "T2", "VE", ["DJBUS_L", "DJBUS_R"]),
    ("C2", "T1", "T2", "pilotato", ["MON_L", "MON_R", "GLOBAL_MUTE"]),
    ("C3", "T2", "T3", "pilotato", ["CUE1_L", "CUE1_R", "CUE2_L", "CUE2_R", "CUE3_L", "CUE3_R",
                                    "CUE4_L", "CUE4_R", "MON_L", "MON_R"]),
    ("C4", "T2", "T4", "VE", ["S1_L", "S1_R", "S2_L", "S2_R", "S3_L", "S3_R", "S4_L", "S4_R"]),
    ("C5", "T1", "T4", "VE", ["MSUM6_L", "MSUM6_R", "MSUM7_L", "MSUM7_R"]),
    ("C6", "T1", "T4", "pilotato", ["MSUM2_L", "MSUM2_R", "MSUM3_L", "MSUM3_R", "MSUM4_L", "MSUM4_R",
                                    "MSUM5_L", "MSUM5_R", "GLOBAL_MUTE"]),
]
POTENZA = ["RAW+27", "RAW-27", "RAW+22", "RAW-22", "+5V", "AGND", "AGND", "AGND", "CTRL_GND", "CHASSIS"]
CAVI_POTENZA = [("P2", "T1", "T2"), ("P3", "T1", "T3"), ("P4", "T1", "T4")]

# Reti a massa virtuale (ricevitore a massa virtuale, R di somma lato sorgente): backplane §4,
# master-segnale.py (MSUM6/7 dritti sul nodo). MSUM1-5 hanno la R sul master: linee pilotate.
VE = {"DJBUS", "BUS_HPF", "BUS_LPF", "S1", "S2", "S3", "S4", "MSUM6", "MSUM7"}


def fili(segnali, massa="AGND"):
    """Ordine dei fili di un cavo piatto: massa, segnale, massa, ... massa (numero pari: un filo
    di massa in più alla fine se serve). GLOBAL_MUTE ha CTRL_GND accanto."""
    out = []
    for s in segnali:
        out.append("CTRL_GND" if s == "GLOBAL_MUTE" else massa)
        out.append(s)
    out.append(massa)
    if len(out) % 2:
        out.append(massa)
    while len(out) < 10:             # header IDC più piccolo: 2x5
        out += [massa, massa]
    return out


def reti_tratto(S, t):
    """Rete -> lista di (oggetto, pin) sul tratto t: slot, ponticelli, prese, cavi."""
    nm = {}
    for s in S:
        if s.tratto == t:
            for p, n in s.reti().items():
                nm.setdefault(n, []).append((s.nome, p))
    for ref, nets, _ in PONTICELLI.get(t, []) + PRESE.get(t, []):
        for k, n in enumerate(nets):
            nm.setdefault(n, []).append((ref, k + 1))
    for nome, a, b, _, seg in CAVI:
        if t in (a, b):
            for k, n in enumerate(fili(seg)):
                nm.setdefault(n, []).append((nome, k + 1))
    return nm


def controlla(S):
    """Errori: rete di segnale con un capo solo, rete che serve in due tratti senza cavo, cavo che
    porta una rete che un capo non usa, cavo VE con linee pilotate o il contrario."""
    err = []
    usate = {}
    for s in S:
        for n in s.reti().values():
            usate.setdefault(n, set()).add(s.tratto)
    for t in TRATTI:
        for ref, nets, _ in PONTICELLI.get(t, []) + PRESE.get(t, []):
            for n in nets:
                usate.setdefault(n, set()).add(t)
    sorgenti = {n for n in usate}
    for nome, a, b, tipo, seg in CAVI:
        for n in seg:
            if n not in sorgenti:
                err.append("%s: %s non è su nessuno slot" % (nome, n))
                continue
            base = n.rsplit("_", 1)[0]
            if (tipo == "VE") != (base in VE):
                err.append("%s (%s) porta %s, che è %s" % (nome, tipo, n, "VE" if base in VE else "pilotata"))
    # connettività: per ogni rete di segnale, i tratti che la usano devono essere uniti dai cavi
    for n, ts in usate.items():
        if n in MASSE or n.split("_")[0] in RAIL or n in RAIL:
            continue
        legati = {next(iter(ts))}
        cambia = True
        while cambia:
            cambia = False
            for nome, a, b, _, seg in CAVI:
                if n in seg and (a in legati) != (b in legati):
                    legati |= {a, b}
                    cambia = True
        if not ts <= legati:
            err.append("rete %s usata in %s ma i cavi la portano solo in %s" % (n, sorted(ts), sorted(legati)))
    for nome, a, b, _, seg in CAVI:
        for n in seg:
            for t in (a, b):
                nm = reti_tratto(S, t)
                if len([c for c in nm.get(n, []) if c[0] != nome]) == 0:
                    # il tratto passa la rete solo da un cavo all'altro: va bene se ce n'è un secondo
                    altri = [c for c in nm.get(n, []) if c[0] != nome]
                    if not altri:
                        err.append("%s: %s arriva in %s ma lì non la usa nessuno" % (nome, n, t))
    # reti di segnale con un solo pin in tutto il backplane
    tot = {}
    for t in TRATTI:
        for n, c in reti_tratto(S, t).items():
            tot.setdefault(n, []).extend(c)
    for n, c in tot.items():
        if len(c) < 2:
            err.append("rete %s con un solo capo: %s" % (n, c))
    # ogni slot deve stare dentro il suo tratto
    for s in S:
        x0, y0, x1, y1 = TRATTI[s.tratto][1]
        for (x, y) in (s.a1, s.a32):
            if not (x0 + 3 <= x <= x1 - 3 and y0 + 3 <= y <= y1 - 3):
                err.append("slot %s: pin a %.1f, %.1f fuori dal tratto %s" % (s.nome, x, y, s.tratto))
    return err


def main():
    S = slots()
    err = controlla(S)
    righe = ["# Backplane a tratti, disposizione F (todo 269)", "",
             "Generato da `pcb/backplane/piano_f.py`: non modificare a mano. Coordinate sul fondo del telaio,",
             "x da sinistra, y da dietro (mm). [C, PROVVISORIO]", "",
             "## Tratti", "", "| Tratto | Cosa | x | y | Misura (mm) | Slot |", "|---|---|---|---|---|---|"]
    for t, (cosa, (x0, y0, x1, y1)) in TRATTI.items():
        ss = [s.nome for s in S if s.tratto == t]
        righe.append("| %s | %s | %.0f-%.0f | %.0f-%.0f | %.0f x %.0f | %s |" % (
            t, cosa, x0, x1, y0, y1, x1 - x0, y1 - y0, " ".join(ss)))
    righe += ["", "## Slot", "", "| Slot | Tratto | Classe | Pin a1 (x, y) | Verso | Rail con PTC (A) | Reti di segnale | Fonte |",
              "|---|---|---|---|---|---|---|---|"]
    for s in S:
        verso = "lungo x" if s.a1[1] == s.a32[1] else "lungo y"
        rail = ", ".join("%s %.2g" % (k, s.ptc.get(k.strip("RAW+-V") or "5", 0)) for k in sorted(s.rail()))
        sig = sorted({n for n in s.reti().values() if n not in MASSE and not any(n.startswith(r) for r in RAIL)})
        righe.append("| %s | %s | %s | %.1f, %.1f | %s | %s | %s | %s |" % (
            s.nome, s.tratto, s.classe, s.a1[0], s.a1[1], verso, rail or "-", " ".join(sig) or "-", s.sorgente))
    righe += ["", "## Cavi fra tratti", "", "| Cavo | Da | A | Tipo | Fili (in ordine) |", "|---|---|---|---|---|"]
    for nome, a, b, tipo, seg in CAVI:
        righe.append("| %s | %s | %s | %s | %s |" % (nome, a, b, tipo, " ".join(fili(seg))))
    for nome, a, b in CAVI_POTENZA:
        righe.append("| %s | %s | %s | potenza (Mini-Fit Jr 2x5) | %s |" % (nome, a, b, " ".join(POTENZA)))
    righe += ["", "## Controllo", ""] + (["- " + e for e in err] or ["- PASSA: ogni rete ha i suoi capi, "
                                                                     "ogni rete fra tratti ha il suo cavo."])
    open(os.path.join(QUI, "PIANO.md"), "w", encoding="utf-8").write("\n".join(righe) + "\n")
    print("\n".join(righe))
    if err:
        sys.exit(1)


if __name__ == "__main__":
    main()
