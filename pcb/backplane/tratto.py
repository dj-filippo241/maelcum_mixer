"""Un tratto del backplane della disposizione F (todo 269). Bozza v0.1.

Uso (Python di KiCad):
    .../python3 pcb/backplane/tratto.py T2 [--solo-schema]
Esce in pcb/backplane/<tratto>/. Piano, slot, reti e cavi: pcb/backplane/piano_f.py (PIANO.md).

Ogni slot ha il suo C96 femmina verticale, con a1 nello stesso punto del pavimento del pin a1 del
maschio della scheda di modulo. Ogni rail di uno slot passa da una PTC (sistema-psu-esterno §4.3)
e ha 100n + 10u verso AGND dopo la PTC (sistema-backplane §8). Masse: AGND sui piani interni,
CTRL_GND e CHASSIS su piste. I cavi verso gli altri tratti stanno su header fissi (piano_f.CAVI).
Scelte non scritte nei documenti: NOTA (pcb/backplane/NOTE.md).
"""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
sys.path.insert(0, HERE)
from pcbgen import DesignRiprova    # noqa: E402
from backplane import SYM_C96       # noqa: E402
import piano_f as pf                # noqa: E402

FP_C96F = "Connector_DIN:DIN41612_C_3x32_Female_Vertical_THT"
PTC_FP = "Fuse:Fuse_1812_4532Metric"
HOLE = ("Mechanical:MountingHole_Pad", "MountingHole:MountingHole_3.2mm_M3_Pad")

# posizioni fisse (coordinate del pavimento) di cavi, ponticelli e fori: (x, y, rotazione);
# header IDC: 0 = file di pin lungo y, 90 = lungo x
FISSI = {
    "T1": {"C1": (40, 141, 90), "C2": (85, 141, 90), "P2": (150, 136, 0), "P3": (205, 124, 0),
           "C5": (240, 141, 90), "C6": (295, 141, 90), "P4": (405, 116, 0),
           "J5W": (125, 50, 0), "JMS": (130, 24, 0), "JVIE": (155, 24, 90)},
    "T2": {"C1": (120, 160, 90), "C2": (165, 160, 90), "P2": (150, 185, 0),
           "C3": (60, 310, 90), "C4": (160, 310, 90)},
    "T3": {"C3": (14, 535, 0), "P3": (186, 535, 0)},
    "T4": {"C4": (240, 300, 90), "C5": (300, 270, 90), "C6": (360, 300, 90), "P4": (420, 270, 0)},
}
# gruppi PTC + 100n + 10u in posti fissi (coordinate locali del tratto): slot -> (x, y del primo
# rail, passo in y). Su T2 i blocchi automatici finivano sopra i C96 e fuori dalla scheda, e
# Freerouting non chiudeva in un'ora: ogni slot ha il suo spazio fra due connettori (13,3 mm),
# in basso vicino ai pin a1-a8 dei rail; SEND4 e i due FILTRO nella parte alta di uno spazio.
GRUPPI = {
    "T2": {"CH1": (25, 140, -7), "SEND1": (50, 140, -7), "CH2": (75, 140, -7), "SEND2": (100, 140, -7),
           "CH3": (125, 140, -7), "SEND3": (150, 140, -7), "CH4": (175, 140, -7),
           "SEND4": (175, 58, 7), "FIL1": (75, 58, 7), "FIL2": (100, 58, 7)},
}
FORI = {
    "T1": [(5, 14), (445, 14), (5, 144), (445, 100), (225, 80)],
    "T2": [(104, 156), (196, 198), (4, 314), (100, 314), (196, 314)],
    "T3": [(4, 519), (196, 519), (4, 551), (196, 551)],
    "T4": [(251, 200), (434, 200), (251, 390), (434, 390), (330, 330)],
}


def header(n):
    """Simbolo e impronta di un cavo piatto da n fili (n pari, almeno 10)."""
    return ("Connector_Generic:Conn_02x%02d_Odd_Even" % (n // 2),
            "Connector_IDC:IDC-Header_2x%02d_P2.54mm_Vertical" % (n // 2))


def main():
    t = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "T1"
    cosa, (fx0, fy0, fx1, fy1) = pf.TRATTI[t]
    W, H = fx1 - fx0, fy1 - fy0
    loc = lambda x, y: (x - fx0, y - fy0)
    out = os.path.join(HERE, t.lower())
    os.makedirs(out, exist_ok=True)
    d = DesignRiprova("backplane-" + t.lower(), out, "maelcum backplane %s (%s) - bozza v0.1" % (t, cosa),
                      board=(W, H), rev="0.1-bozza")
    d.gnd = "AGND"
    d.link_pairs = True        # pin gemelli del C96 (a1/a2, a3/a4 ...): Freerouting li lascia aperti
    # T2: le reti dei bus attraversano otto C96 in fila (un muro di pin ogni 25 mm): con due strati
    # di piste Freerouting girava 40 minuti a tentativo senza chiudere. In2 strato di piste, massa su In1
    d.inner_signal = t == "T2"
    # T2: anche i gemelli di massa (CTRL_GND a23-a24, CHASSIS a25-a26): un gemello aperto fa disfare
    # a Freerouting tutta la rete (giro 3 di T2: CTRL_GND 57 aperti su 60 pin, come il canale il 10/11)
    d.link_pairs_masse = t == "T2"
    S = [s for s in pf.slots() if s.tratto == t]

    usate = set(pf.reti_tratto(pf.slots(), t)) | set(pf.POTENZA) | {tr for s in S for tr in s.rail()}
    tronco = [n for n in ("RAW+27", "RAW-27", "RAW+22", "RAW-22", "RAW+26", "RAW-26") if n in usate]
    d.power_nets(*tronco, width=1.2)
    d.power_nets("+5V", "CHASSIS", width=0.8)
    d.power_nets("CTRL_GND", width=0.5)
    for s in S:
        d.power_nets(*s.rail().values(), width=0.6)

    # ------------------------------------------------------------ slot
    for s in S:
        d.block = "SLOT %s (%s)" % (s.nome, s.classe)
        x, y = loc(*s.a1)
        # a1 -> a32 verso -x (sinistra-destra: file a -> c verso +y) o verso -y (dietro-davanti: file
        # a -> c verso -x); a1 si sposta di una fila perché la fila b stia sulla linea del posto
        if s.a1[1] == s.a32[1]:
            rot, y = 270, y - 2.54
        else:
            rot, x = 180, x + 2.54
        d.part("J", SYM_C96, "C96 femmina %s" % s.nome, FP_C96F, s.reti(), ref="J" + s.nome,
               place=(x, y, rot), anchor=(0, 0),
               note="slot %s, classe %s; pin da %s. NOTA: distanza fila-scheda da leggere sul disegno "
                    "del connettore vero" % (s.nome, s.classe, s.sorgente))
        g = GRUPPI.get(t, {}).get(s.nome)
        for i, (tr, rs) in enumerate(sorted(s.rail().items())):
            k = tr.strip("RAW+-V") or "5"
            a = s.ptc.get(k)
            gx, gy = (g[0], g[1] + i * g[2]) if g else (None, None)
            d.part("F", "Device:Polyfuse", "PTC %.2g A" % a, PTC_FP, {1: tr, 2: rs},
                   note="PTC di slot (psu-esterno §4.3); NOTA: tenuta %.2g A, >= 33 V, 1812" % a,
                   place=(gx - 2.6, gy, 90) if g else None)
            neg = "-" in tr
            pin = {1: "AGND" if neg else rs, 2: rs if neg else "AGND"}
            d.part("C", "Device:C", "100n 50V", "Capacitor_SMD:C_0805_2012Metric", pin,
                   note="bypass di slot (backplane §8)", place=(gx + 2.6, gy + 1.6, 0) if g else None)
            d.part("C", "Device:C", "10u 50V X7R", "Capacitor_SMD:C_1206_3216Metric", pin,
                   note="bulk di slot (backplane §8); NOTA: MLCC 50 V", place=(gx + 2.6, gy - 1.5, 0) if g else None)

    # ------------------------------------------------------------ cavi, ponticelli, prese
    fx = FISSI[t]
    for nome, a, b, tipo, seg in pf.CAVI:
        if t not in (a, b):
            continue
        d.block = "CAVO %s" % nome
        fl = pf.fili(seg)
        while len(fl) < 10:
            fl += ["AGND", "AGND"]
        sym, fp = header(len(fl))
        x, y = loc(*fx[nome][:2])
        d.part("J", sym, "cavo %s %s-%s (%s)" % (nome, a, b, tipo), fp, {k + 1: n for k, n in enumerate(fl)},
               ref="J" + nome, place=(x, y, fx[nome][2]),
               note="NOTA: cavo piatto, ogni segnale fra due fili di massa; %s" %
                    ("solo net a massa virtuale" if tipo == "VE" else "solo linee pilotate"))
    for nome, a, b in pf.CAVI_POTENZA:
        if t not in (a, b):
            continue
        d.block = "POTENZA %s" % nome
        x, y = loc(*fx[nome][:2])
        d.part("J", "Connector_Generic:Conn_02x05_Odd_Even", "potenza %s %s-%s" % (nome, a, b),
               "Connector_Molex:Molex_Mini-Fit_Jr_5566-10A2_2x05_P4.20mm_Vertical",
               {k + 1: n for k, n in enumerate(pf.POTENZA)}, ref="J" + nome, place=(x, y, fx[nome][2]),
               note="NOTA: Mini-Fit Jr 2x5; radiale AGND del tratto fino alla stella del PSU-IN (grounding §2)")
    for ref, nets, cosa_p in pf.PONTICELLI.get(t, []):
        d.block = "PONTICELLI"
        x, y = loc(*fx[ref][:2])
        d.part("J", "Connector_Generic:Conn_02x02_Odd_Even", "ponticello " + ref,
               "Connector_PinHeader_2.54mm:PinHeader_2x02_P2.54mm_Vertical",
               {k + 1: n for k, n in enumerate(nets)}, ref=ref, place=(x, y, fx[ref][2]),
               note="ponticello di continuità (dec. 111): %s; due cavallotti 1-2 e 3-4" % cosa_p)
    for ref, nets, cosa_p in pf.PRESE.get(t, []):
        d.block = "PONTICELLI"
        x, y = loc(*fx[ref][:2])
        d.part("J", "Connector_Generic:Conn_01x%02d" % len(nets), "presa " + ref,
               "Connector_PinHeader_2.54mm:PinHeader_1x%02d_P2.54mm_Vertical" % len(nets),
               {k + 1: n for k, n in enumerate(nets)}, ref=ref, place=(x, y, fx[ref][2]),
               note="NOTA: predisposizione %s, nessuno slot nella disposizione F" % cosa_p)
    for k, (hx, hy) in enumerate(FORI[t]):
        x, y = loc(hx, hy)
        d.part("H", HOLE[0], "CHASSIS", HOLE[1], {1: "CHASSIS"}, ref="H%d" % (k + 1), place=(x, y, 0),
               note="fissaggio al fondo del telaio, a CHASSIS (bond con AGND solo nel PSU-IN)")
    d.build()


if __name__ == "__main__":
    main()
