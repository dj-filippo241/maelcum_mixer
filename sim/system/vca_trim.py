"""Trim di law delle coppie stereo di VCA 2181 / V2181L (todo 17).

Uso:  python3 sim/system/vca_trim.py            calcola i trim e scrive vca-trim-casi.cir
      python3 sim/system/vca_trim.py <log>      legge il log di LTspice e stampa le tabelle

Circuito di una coppia (docs/fase3/sistema-vca-trim.md §3):
  CV (shaper, uno per coppia) -> Rs -> pin EC- ; pin EC- -> Rg -> massa
  lato L: Rs = RS_L fisso;  lato R: Rs = RS_R0 + trimmer di scala (0..RT)
  lato R: offset = cursore di un trimmer fra +-15 V LN -> ROFF -> pin EC-
Chip: G = -Vpin/k + d0 + c*g^2  (g = -Vpin/k), datasheet THAT 2181:
  k 6,0/6,1/6,2 mV/dB, guadagno a CV 0 +-0,2 dB (grado C), linearita 0,5 % typ, 2 % max.
Python puro, nessun pacchetto.
"""

import math
import os
import random
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))

RG = 1000.0          # verso massa
RS_L = 1000.0        # lato L, fisso
RS_R0 = 900.0        # lato R, fisso in serie al trimmer
RT = 200.0           # trimmer di scala, 25 giri
ROFF = 1.5e6         # iniezione dell'offset
VLN = 15.0           # +-15,0 V LN (dec. 93)
K_NOM = 0.0061       # V/dB
A_NOM = RG / (RS_L + RG)
G_TRIM = -40.0       # punto di trim della scala
GRIGLIA = (10, 0, -10, -20, -40, -60, -80)


def lin_c(lin):
    """Linearita del datasheet -> coefficiente quadratico: scarto lin*60 dB a -60 dB."""
    return lin / 60.0


# coppie peggiori: (nome, kL, kR, dL, dR, cL, cR)
CASI = [
    ("THAT C, k e d0 opposti", 0.0060, 0.0062, -0.2, +0.2, 0, 0),
    ("THAT C, rovescio", 0.0062, 0.0060, +0.2, -0.2, 0, 0),
    ("clone 5,8/6,3: fuori campo, si abbina", 0.0058, 0.0063, -0.2, +0.2, 0, 0),
    ("THAT C + linearita 0,5 % typ", 0.0060, 0.0062, -0.2, +0.2, 0, lin_c(0.005)),
    ("THAT C + linearita 2 % max", 0.0060, 0.0062, -0.2, +0.2, 0, lin_c(0.02)),
]


def guadagno(vpin, k, d0, c):
    g = -vpin / k
    return g + d0 + c * g * g


def pin(cv, rs, vw, off=True):
    """Tensione al pin EC-: CV su rs, massa su RG, vw su ROFF (solo lato R)."""
    gs, gg, go = 1 / rs, 1 / RG, (1 / ROFF if off else 0.0)
    return (cv * gs + vw * go) / (gs + gg + go)


def cv_per(g):
    """Uscita dello shaper per il guadagno g sul chip nominale, lato L."""
    return -g * K_NOM / (pin(1.0, RS_L, 0, False))


def risolvi(kL, kR, dL, dR, cL, cR):
    """Trim del lato R: offset a CV 0, scala a G_TRIM. Due passi, poi un ritocco."""
    rs, vw = RS_R0 + RT / 2, 0.0
    for _ in range(4):
        # offset: a CV 0 il lato R deve valere dL
        gl0 = guadagno(pin(0, RS_L, 0, False), kL, dL, cL)
        lo, hi = -VLN, VLN
        for _ in range(60):
            vw = (lo + hi) / 2
            if guadagno(pin(0, rs, vw), kR, dR, cR) > gl0:
                lo = vw
            else:
                hi = vw
        # scala: a G_TRIM i due lati uguali
        cv = cv_per(G_TRIM)
        gl = guadagno(pin(cv, RS_L, 0, False), kL, dL, cL)
        lo, hi = RS_R0, RS_R0 + RT
        for _ in range(60):
            rs = (lo + hi) / 2
            if guadagno(pin(cv, rs, vw), kR, dR, cR) < gl:
                lo = rs
            else:
                hi = rs
    return rs, vw


def scarti(kL, kR, dL, dR, cL, cR, rs, vw):
    out = []
    for g in GRIGLIA:
        cv = cv_per(g)
        out.append(guadagno(pin(cv, rs, vw), kR, dR, cR)
                   - guadagno(pin(cv, RS_L, 0, False), kL, dL, cL))
    return out


def scrivi_netlist(trims):
    righe = [
        "* vca-trim-casi.cir — GENERATO da sim/system/vca_trim.py: non modificare.",
        "* Trim di law di una coppia stereo di VCA 2181 / V2181L (todo 17,",
        "* docs/fase3/sistema-vca-trim.md). Lato L fisso, lato R con trimmer di",
        "* scala (Rs) e di offset (cursore su ROFF). tr=0: trimmer a meta corsa;",
        "* tr=1: trimmer ai valori calcolati. Misura L e R a 1 kHz per ogni g.",
        "* Chip: legge del datasheet THAT 2181 con k, d0 e linearita per chip",
        "* (macro comportamentale, stessa forma di sim/lib/that2181.inc).",
        f".param g=-40 caso=1 tr=0",
        f".param cv={{-g*{K_NOM}/{A_NOM!r}}}",
    ]
    def tab(nome, valori):
        coppie = ", ".join(f"{i + 1}, {v!r}" for i, v in enumerate(valori))
        return f".param {nome}={{table(caso, {coppie})}}"
    for i, nome in enumerate(("kL", "kR", "dL", "dR", "cL", "cR")):
        righe.append(tab(nome, [c[i + 1] for c in CASI]))
    righe.append(tab("rsT", [t[0] for t in trims]))
    righe.append(tab("vwT", [t[1] for t in trims]))
    righe += [
        f".param rsR={{if(tr, rsT, {RS_R0 + RT / 2!r})}}",
        ".param vwR={if(tr, vwT, 0)}",
        "Vcv cv 0 DC {cv}",
        "Vw w 0 DC {vwR}",
        "Vin in 0 DC 0 AC 1",
        f"RsL cv pl {RS_L!r}",
        f"RgL pl 0 {RG!r}",
        "RsR cv pr {rsR}",
        f"RgR pr 0 {RG!r}",
        f"RoR w pr {ROFF!r}",
        "* chip: guadagno in dB dal pin EC-, ingresso ad alta impedenza (I bias trascurata)",
        "Bl outl 0 V={V(in)*10**((-V(pl)/kL + dL + cL*(V(pl)/kL)**2)/20)}",
        "Br outr 0 V={V(in)*10**((-V(pr)/kR + dR + cR*(V(pr)/kR)**2)/20)}",
        ".step param tr LIST 0 1",
        f".step param caso 1 {len(CASI)} 1",
        ".step param g LIST " + " ".join(str(g) for g in GRIGLIA),
        ".ac lin 3 900 1.1k",
        ".meas ac gl FIND mag(V(outl)) AT 1k",
        ".meas ac gr FIND mag(V(outr)) AT 1k",
        ".end",
    ]
    with open(os.path.join(QUI, "vca-trim-casi.cir"), "w") as f:
        f.write("\n".join(righe) + "\n")


def scarti_libero(kL, kR, dL, dR):
    """Coppia senza trimmer: tutti e due i lati come il lato L."""
    return [guadagno(pin(cv_per(g), RS_L, 0, False), kR, dR, 0)
            - guadagno(pin(cv_per(g), RS_L, 0, False), kL, dL, 0) for g in GRIGLIA]


def leggi_log(percorso):
    testo = open(percorso, encoding="utf-8", errors="replace").read().replace("\x00", "")
    out = {}
    for nome in ("gl", "gr"):
        blocco = testo.split(f"Measurement: {nome}")[1].split("Measurement:")[0]
        vals = []
        for riga in blocco.splitlines():
            m = re.match(r"\s*(\d+)\s+\(([-\d.e+]+)dB", riga)
            if m:
                vals.append(float(m.group(2)))
        out[nome] = vals
    return out


def monte_carlo(n_chip=62, prove=200, seme=1):
    """Lotto di chip con k +-3 % e d0 +-0,2 dB uniformi, abbinati per vicinanza:
    quante coppie restano entro 0,25 e 0,5 dB su -60..+10 senza trim di law."""
    rnd = random.Random(seme)
    entro25 = entro50 = tot = 0
    for _ in range(prove):
        chip = [(K_NOM * (1 + rnd.uniform(-0.03, 0.03)), rnd.uniform(-0.2, 0.2))
                for _ in range(n_chip)]
        # misura a banco a due punti: d0 e guadagno a -40; ordina per k, poi per d0 a gruppi
        chip.sort(key=lambda c: c[0])
        coppie = []
        for i in range(0, n_chip - 1, 4):
            gruppo = sorted(chip[i:i + 4], key=lambda c: c[1])
            coppie += [(gruppo[j], gruppo[j + 1]) for j in range(0, len(gruppo) - 1, 2)]
        for (kL, dL), (kR, dR) in coppie:
            peggio = max(abs(e) for e in scarti_libero(kL, kR, dL, dR)[:-1])
            tot += 1
            entro25 += peggio <= 0.25
            entro50 += peggio <= 0.5
    return entro25 / tot, entro50 / tot


def main():
    if len(sys.argv) > 1:
        log = leggi_log(sys.argv[1])
        print(f"{'caso':34s} " + " ".join(f"{g:>+7d}" for g in GRIGLIA))
        for tr in (0, 1):
            print("trimmer a meta corsa" if tr == 0 else "trimmer ai valori calcolati")
            for c in range(len(CASI)):
                riga = []
                for j in range(len(GRIGLIA)):
                    # .step: il primo (tr) cambia piu in fretta, poi caso, poi g
                    i = (j * len(CASI) + c) * 2 + tr
                    riga.append(log["gr"][i] - log["gl"][i])
                print(f"  {CASI[c][0]:32s} " + " ".join(f"{e:+7.3f}" for e in riga))
        return
    trims = []
    print(f"divisore nominale a = {A_NOM:.4f}; shaper x {1 / A_NOM:.4f}")
    print(f"{'caso':34s} {'Rs R':>7s} {'giri':>5s} {'Vw':>7s} {'giri':>5s}  scarti dopo il trim (dB) a "
          + " ".join(str(g) for g in GRIGLIA))
    for nome, *p in CASI:
        rs, vw = risolvi(*p)
        trims.append((rs, vw))
        e = scarti(*p, rs, vw)
        print(f"  {nome:32s} {rs:7.1f} {25 * (rs - RS_R0) / RT:5.1f} {vw:+7.2f} "
              f"{25 * (vw + VLN) / (2 * VLN):5.1f}  " + " ".join(f"{x:+.3f}" for x in e))
    scrivi_netlist(trims)
    # risoluzione dei trimmer
    cv = cv_per(G_TRIM)
    d_rs = 8.0  # un giro del 200 ohm a 25 giri
    passo_s = abs(guadagno(pin(cv, RS_R0 + RT / 2 + d_rs, 0), K_NOM, 0, 0)
                  - guadagno(pin(cv, RS_R0 + RT / 2, 0), K_NOM, 0, 0))
    passo_o = abs(guadagno(pin(0, RS_R0 + RT / 2, 1.2), K_NOM, 0, 0))
    print(f"un giro: scala {passo_s:.3f} dB a {G_TRIM:.0f} dB; offset {passo_o:.3f} dB a ogni guadagno")
    rng = [guadagno(pin(cv, r, 0), K_NOM, 0, 0) - G_TRIM for r in (RS_R0, RS_R0 + RT)]
    print(f"escursione della scala: {rng[0]:+.2f} / {rng[1]:+.2f} dB a {G_TRIM:.0f} dB "
          f"= {100 * rng[0] / -G_TRIM:+.1f} / {100 * rng[1] / -G_TRIM:+.1f} % di k")
    print(f"escursione dell'offset: +-{guadagno(pin(0, RS_R0 + RT / 2, -VLN), K_NOM, 0, 0):.2f} dB")
    p25, p50 = monte_carlo()
    print(f"abbinamento senza trim (lotto 62, k +-3 %, d0 +-0,2): entro 0,25 dB {100 * p25:.0f} %, "
          f"entro 0,5 dB {100 * p50:.0f} % delle coppie")


if __name__ == "__main__":
    main()
