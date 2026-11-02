#!/usr/bin/env python3
"""GAIN con pot doppio lineare al posto dei VCA (questione A22, todo 219).

Due topologie candidate, per il canale (-inf...0...+10 dB) e per il ritorno
FX (-inf...0...+20 dB). Pot lineare R, cursore a x (0 = fondo corsa CCW).

T1  PARTITORE CARICATO + AMPLI
    pot fra ingresso e massa, Rl dal cursore a massa (resistenza di legge),
    poi non invertente di guadagno A.  G = A * (x*R || Rl) / ((1-x)*R + x*R || Rl)
    Vincoli: G(0,5) = 1, G(1) = A.

T2  POT IN RETROAZIONE (massa virtuale sul cursore) + STADIO K
    invertente: Rin = (1-x)*R + Ra (lato ingresso), Rf = x*R (lato uscita),
    poi invertente di guadagno K (polarita' diritta).
    G = K * x*R / ((1-x)*R + Ra)
    Vincoli: G(0,5) = 1, G(1) = Gmax.  Con a = Ra/R: a = 0,5/(0,5*Gmax - 1), K = Gmax*a.

Tracking L/R: le due piste del pot doppio differiscono per
  - errore di posizione dx (linearita' delle piste, sfasamento dei rotori),
  - resistenza totale dR (la pista di un lato vale R*(1+dR)).
Si calcola l'errore L-R nel caso peggiore (segni opposti) in funzione della
posizione, per tre livelli di selezione. Il criterio di dec. 107 per l'EQ:
"errore del 2 % al centro".

Uso: python3 sim/gain-pot/gain_pot.py
"""
import math

R = 10e3


def db(g):
    return 20 * math.log10(g) if g > 0 else -math.inf


def par(a, b):
    if a <= 0 or b <= 0:
        return 0.0
    return a * b / (a + b)


# ---------------- T1 ----------------
def t1_design(gmax):
    """Rl tale che il partitore a meta' corsa valga 1/gmax."""
    k = 1 / gmax                     # rapporto voluto a x = 0,5
    L = 0.5 * k / (1 - k)            # gamba bassa (in unita' di R) per avere k
    r = 0.5 * L / (0.5 - L)          # Rl/R
    return r * R


def t1_gain(x, gmax, Rl, Rtot=R):
    lo = par(x * Rtot, Rl)
    hi = (1 - x) * Rtot
    if lo + hi == 0:
        return 0.0
    return gmax * lo / (lo + hi)


# ---------------- T2 ----------------
def t2_design(gmax):
    a = 0.5 / (0.5 * gmax - 1)
    return a * R, gmax * a


def t2_gain(x, Ra, K, Rtot=R):
    return K * x * Rtot / ((1 - x) * Rtot + Ra)


# ---------------- curve del prototipo (proto-max/coefficienti) ----------------
def proto_canale(t):
    if t <= 0:
        return -math.inf
    return -100 * (1 - 2 * t) if t < 0.5 else 20 * (t - 0.5)


def proto_ritorno(t):
    if t >= 0.5:
        return 20 * (t - 0.5) / 0.5
    if t >= 0.05:
        return -40 * (0.5 - t) / 0.45
    return db(10 ** (-2) * t / 0.05) if t > 0 else -math.inf


POS = [0.0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.45, 0.5, 0.55, 0.6, 0.7, 0.8, 0.9, 1.0]
SEL = [("selezionati stretti", 0.005, 0.005),
       ("selezionati come dec. 107", 0.01, 0.02),
       ("non selezionati", 0.03, 0.10)]
# (nome, dx assoluto nel caso peggiore per lato, dR relativo fra le piste)


def tracking(fun, x, dx, dRr):
    """Errore L-R peggiore: un lato a x+dx e R(1+dR/2), l'altro a x-dx e R(1-dR/2)."""
    worst = 0.0
    for sx in (1, -1):
        for sr in (1, -1):
            xl = min(max(x + sx * dx, 0), 1)
            xr = min(max(x - sx * dx, 0), 1)
            gl = fun(xl, R * (1 + sr * dRr / 2))
            gr = fun(xr, R * (1 - sr * dRr / 2))
            if gl <= 0 or gr <= 0:
                continue
            worst = max(worst, abs(db(gl) - db(gr)))
    return worst


def tabella(nome, gmax, proto):
    Rl = t1_design(gmax)
    Ra, K = t2_design(gmax)
    f1 = lambda x, Rt=R: t1_gain(x, gmax, Rl, Rt)
    f2 = lambda x, Rt=R: t2_gain(x, Ra, K, Rt)
    print(f"\n=== {nome}: -inf...0...+{db(gmax):.0f} dB ===")
    print(f"T1: Rl = {Rl:.0f} ohm (pot {R/1e3:.0f}k), ampli x{gmax:.3f}")
    print(f"T2: Ra = {Ra:.0f} ohm, K = {K:.3f}")
    print("pos    proto    T1      T2   | tracking peggiore L-R (dB): T1 / T2")
    hdr = "                              | " + " | ".join(s[0] for s in SEL)
    print(hdr)
    for x in POS:
        g1 = db(f1(x))
        g2 = db(f2(x))
        tr = []
        for _, dx, dRr in SEL:
            tr.append(f"{tracking(f1, x, dx, dRr):5.2f}/{tracking(f2, x, dx, dRr):5.2f}")
        print(f"{x:4.2f} {proto(x):7.1f} {g1:7.1f} {g2:7.1f} | " + "   ".join(tr))
    # pendenza al centro (dB per 1 % di corsa)
    s1 = (db(f1(0.505)) - db(f1(0.495)))
    s2 = (db(f2(0.505)) - db(f2(0.495)))
    print(f"pendenza al detent: T1 {s1:.2f} dB/%  T2 {s2:.2f} dB/%  (dB per 1 % di corsa)")
    # effetto della sola resistenza totale (dR) al detent, posizione esatta
    for dRr in (0.01, 0.2):
        e1 = db(f1(0.5, R * (1 + dRr)))
        e2 = db(f2(0.5, R * (1 + dRr)))
        print(f"pista {dRr*100:+.0f} % di R al detent: T1 {e1:+.2f} dB  T2 {e2:+.2f} dB")
    # range utile: dal detent verso il basso, finche' il tracking resta <= 0,5 dB
    for name, f in (("T1", f1), ("T2", f2)):
        for sel, dx, dRr in SEL:
            x = 0.5
            while x > 0.002 and tracking(f, x, dx, dRr) <= 0.5:
                x -= 0.001
            top = max(tracking(f, y / 1000, dx, dRr) for y in range(500, 1001))
            print(f"{name} {sel}: <= 0,5 dB sotto il detent fino a {db(f(x)):6.1f} dB"
                  f" (x = {x:.3f}); sopra il detent max {top:.2f} dB")


if __name__ == "__main__":
    tabella("CANALE", 10 ** (10 / 20), proto_canale)
    tabella("RITORNO FX", 10.0, proto_ritorno)
