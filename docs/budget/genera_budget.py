#!/usr/bin/env python3
# Genera docs/09-budget.md: il costo stimato di ogni modulo e del mixer.
# Uso:  python3 docs/budget/genera_budget.py
# I prezzi stanno in PREZZI, le quantita' nei moduli qui sotto. Quando un
# design doc cambia un conteggio, o arriva un preventivo, si corregge la riga
# e si rilancia lo script. Prezzi in euro, IVA esclusa, per pezzo, ai lotti
# di un esemplare unico (decine di pezzi, non migliaia).
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "09-budget.md")
DATA = "2026-10-22"
IVA = 0.22

# chiave: (descrizione, min, max, fonte). Fonti: vedi FONTI in fondo.
PREZZI = {
    "opa1612":  ("OPA1612 dual op-amp", 5.5, 7.5, "M"),
    "opa1654":  ("OPA1654 quad op-amp", 1.6, 2.8, "M"),
    "dual":     ("op-amp dual generico (servo, detector)", 0.6, 3.0, "S"),
    "vca":      ("VCA CoolAudio V2181L", 2.8, 5.0, "D"),
    "ota":      ("LM13700 dual OTA", 0.6, 2.0, "L"),
    "adg":      ("ADG1434 quad switch", 6.0, 10.0, "M"),
    "lm3915":   ("LM3915 driver di barra", 2.0, 4.5, "M"),
    "lm339":    ("LM339 comparatore quad", 0.3, 0.6, "S"),
    "hc":       ("logica 74HC (74/86/14)", 0.2, 0.6, "S"),
    "lt":       ("LT3045 / LT3094 regolatore low-noise", 4.0, 6.0, "D"),
    "lm317":    ("LM317/337 o 78L15/79L15", 0.5, 1.0, "D"),
    "jfet2":    ("JFET dual abbinato (classe LSK489)", 4.0, 8.0, "S"),
    "trim":     ("trimmer multigiro", 0.8, 2.0, "S"),
    "rk14d":    ("pot 14 mm doppio (Alps RK14K)", 1.1, 2.5, "M"),
    "rk14s":    ("pot 14 mm singolo (Alps RK14K)", 0.9, 2.0, "S"),
    "rk09s":    ("pot 9 mm singolo (Alps RK09K)", 0.35, 0.7, "L"),
    "rk09d":    ("pot 9 mm doppio (Alps RK09)", 0.8, 1.8, "S"),
    "fader":    ("fader 100 mm mono (Alps RS60N)", 8.8, 12.5, "R"),
    "lev3m":    ("levetta sigillata ON-OFF-(ON)", 6.0, 12.0, "S"),
    "lev3":     ("levetta sigillata 3 posizioni fisse", 5.0, 10.0, "S"),
    "lev2":     ("levetta piccola 2 posizioni", 3.0, 6.0, "S"),
    "bott":     ("bottone con luce a ritenuta", 4.0, 9.0, "S"),
    "xlr":      ("XLR Neutrik da pannello", 1.8, 4.5, "M"),
    "jack":     ("jack 6,3 mm Neutrik", 2.0, 4.0, "S"),
    "rca":      ("RCA dorato isolato", 1.5, 3.0, "S"),
    "c96":      ("DIN 41612 C96, coppia", 4.0, 8.0, "D"),
    "led3":     ("LED tricolore", 0.5, 1.5, "S"),
    "led":      ("LED dei meter", 0.08, 0.2, "S"),
    "rele":     ("rele' di segnale", 2.0, 4.0, "D"),
    "ptc":      ("fusibile PTC", 0.3, 0.8, "S"),
    "fus":      ("fusibile con portafusibile", 1.0, 3.0, "S"),
    "ponte":    ("ponte raddrizzatore", 2.0, 5.0, "S"),
    "ventola":  ("ventola 80 mm silenziosa", 12.0, 20.0, "S"),
    "cap2":     ("condensatore di film 2 % abbinato", 0.6, 1.5, "S"),
    "lm334":    ("generatore di corrente (CRD / LM334)", 0.5, 1.5, "S"),
    "dip":      ("DIP switch del pad", 0.8, 1.5, "S"),
    "bjt2":     ("coppia BJT abbinata", 3.0, 8.0, "S"),
}


def p(chiave, qta, nota=""):
    d, lo, hi, f = PREZZI[chiave]
    return (d, qta, lo, hi, f, nota, True)


def a_corpo(desc, lo, hi, nota="", fonte="S"):
    """Voce a corpo: passivi, minuteria, tutto cio' che non conviene contare."""
    return (desc, 1, lo, hi, fonte, nota, False)


# Ogni modulo: (nome, copie nel setup completo, copie nel ridotto, doc, righe)
MODULI = [
    ("Canale CDJ/line con phono", 4, 2, "cdj-line-channel §6, eq-isolator §5, phono §4", [
        p("opa1654", 12, "isolator, 24 sezioni per lato"),
        p("opa1612", 7, "somme EQ, buffer, fader, out; phono 2+1"),
        p("dual", 1, "servo"),
        p("vca", 2, "fader 2 (dec. 126); GAIN a pot doppio (dec. 162)"),
        p("trim", 15, "trim dei VCA 6, incroci 6, shaper del fader 3"),
        p("hc", 3, "levetta HPF/OFF/LPF col dip del fader (dec. 163)"),
        p("adg", 1, "LINE/PHONO"),
        p("lm317", 2, "regolatori locali"),
        a_corpo("passivi: banca R 0,1 %, ~60 C di precisione, RIAA", 45, 80),
        p("rca", 6, "line 4 + phono 2"),
        a_corpo("morsetto di massa phono", 1, 3),
        p("c96", 1),
        p("rk14d", 1, "GAIN, pot doppio selezionato (dec. 162)"),
        p("rk14d", 4, "EQ, residuo <= 20 ohm (dec. 127)"),
        p("lev2", 1, "LINE/PHONO"),
        p("lev3", 1, "filtro HPF/OFF/LPF"),
        p("adg", 1, "instradamento post-fader DJ / HPF / LPF (dec. 159)"),
        p("bott", 5, "CUE + assign FX 1-4"),
        p("fader", 1),
    ]),
    ("FX-SEND", 4, 2, "fx-send-module §5", [
        p("opa1654", 3),
        p("opa1612", 1),
        p("adg", 2, "assign, dopo la R di iniezione (todo 185)"),
        p("lm339", 1, "taglio allo zero degli assign (todo 224)"),
        p("hc", 4, "74HC74, un flip-flop per assign e lato"),
        p("lm317", 4),
        a_corpo("passivi", 8, 15),
        p("c96", 1),
        p("rk09d", 2, "EQ LOW/HIGH"),
        p("rk14d", 1, "LEVEL"),
    ]),
    ("FX-RET (un bus, dec. 130)", 4, 4, "fx-module §2bis, §9, sistema-vca-trim §4", [
        p("vca", 10, "reroute 8 (4 bus x L/R) + fader 2; GAIN a pot doppio (dec. 162)"),
        p("trim", 35, "3 per VCA + shaper"),
        p("opa1654", 5, "3 + 2 per l'iniezione dei reroute sui net"),
        p("opa1612", 1),
        a_corpo("JFET dei buffer di ritorno (2)", 1, 3),
        a_corpo("shaper delle 4 CV: diodi e resistenze", 3, 6),
        p("lm317", 2),
        a_corpo("passivi", 10, 18),
        p("jack", 4, "mandata e ritorno del pedale, L/R"),
        p("dip", 2, "pad"),
        a_corpo("TVS low-cap", 1, 2),
        p("c96", 1),
        p("rk14d", 1, "GAIN, pot doppio selezionato (dec. 162)"),
        p("rk09d", 2, "EQ"),
        p("fader", 1),
        p("rk09s", 4, "reroute verso gli altri bus e SELF, RK09K113004U"),
    ]),
    ("Filtro, core OTA (a')", 1, 1, "filter-module §7, §5ter, §5quater; dec. 159 (4 core sui bus HPF e LPF)", [
        p("ota", 12, "4 core a 4 poli + RES"),
        p("opa1654", 12, "10 dei core + ricevitori dei bus"),
        p("vca", 4, "overdrive (una cella per lato e sezione)"),
        p("trim", 27, "VCA 12 + frequenza, shaper, RES 15"),
        a_corpo("diodi del limitatore e dello shaper", 2, 4),
        p("cap2", 16, "integratori"),
        p("bjt2", 2, "converter"),
        p("adg", 1, "muto della sezione senza canali (dec. 159)"),
        p("lt", 2),
        p("lm317", 2),
        a_corpo("passivi", 25, 45),
        p("c96", 1),
        p("rk14s", 6, "FREQ, RES, DRIVE x 2"),
    ]),
    ("5-way", 1, 1, "five-way §7, §4.3, §5bis", [
        p("opa1654", 36, "banca, celle, gate"),
        p("opa1612", 11, "WIDTH 10 + recovery"),
        p("dual", 2, "servo"),
        p("jfet2", 20, "celle parametriche"),
        p("adg", 3, "kill"),
        p("lm339", 3, "kill al passaggio per lo zero (dec. 164)"),
        p("hc", 5, "74HC74 doppio, uno per via"),
        a_corpo("GROWL e NASTRO: diodi, R, op-amp", 10, 20),
        p("lt", 2),
        p("lm317", 2),
        a_corpo("passivi: banca R 0,1 %, C di film", 60, 100),
        p("trim", 20),
        p("c96", 1),
        p("rk14d", 12, "GAIN 5 + WIDTH 5 + GROWL/NASTRO 2"),
        p("rk14s", 5, "POSITION"),
        p("lev3m", 5, "KILL"),
    ]),
    ("Master out (con booth e MONO)", 1, 1, "master-out §5", [
        p("vca", 5, "master 2, booth 2, MONO 1"),
        p("trim", 15),
        p("opa1612", 7, "con buffer MON del CUE"),
        p("dual", 2, "servo"),
        a_corpo("transistor diamond e bootstrap, diodi, CRD", 8, 15),
        p("rele", 3, "mute"),
        p("lt", 4),
        p("lm317", 3),
        p("xlr", 4, "master L/R, booth L/R"),
        p("jack", 2, "rec"),
        a_corpo("passivi", 15, 30),
        p("c96", 1),
        p("rk14s", 2, "MASTER, BOOTH"),
        p("bott", 1, "MONO"),
    ]),
    ("CUE e cuffie", 1, 1, "sistema-cue §10", [
        p("opa1612", 3),
        a_corpo("transistor finali e limitatori", 4, 8),
        p("lm334", 4),
        p("lt", 4),
        p("lm317", 4),
        p("rele", 2),
        a_corpo("resistenze di potenza", 4, 8),
        p("rk14d", 1, "BLEND"),
        p("rk09d", 1, "LEVEL"),
        p("jack", 2, "cuffie, dec. 128"),
        a_corpo("passivi", 8, 15),
        p("c96", 1),
    ]),
    ("Metering (tutte le barre)", 1, 1, "sistema-metering §6", [
        p("lm3915", 13),
        p("dual", 12, "detector"),
        p("lm339", 3),
        p("led", 150),
        a_corpo("passivi e trimmer", 12, 25),
    ]),
    ("MIC", 1, 1, "mic-mono-moduli §8", [
        p("opa1612", 3),
        p("opa1654", 3),
        p("adg", 1),
        p("lm339", 1),
        p("vca", 1, "MUTE"),
        p("trim", 3),
        p("lm317", 4),
        p("lt", 2),
        p("led3", 1),
        p("xlr", 1),
        p("bott", 1, "MUTE"),
        p("rk14s", 5, "GAIN (curva C) + SEND 1-4"),
        p("rk09s", 2, "EQ"),
        a_corpo("passivi", 10, 20),
        p("c96", 1),
    ]),
    ("MONO", 3, 1, "mic-mono-moduli §8", [
        p("opa1612", 1),
        p("opa1654", 3),
        p("adg", 1),
        p("lm339", 1),
        p("lm317", 4),
        p("led3", 1),
        p("jack", 1),
        p("rk14s", 5, "GAIN + SEND 1-4"),
        p("rk09s", 2, "EQ"),
        a_corpo("passivi", 8, 15),
        p("c96", 1),
    ]),
    ("Backplane", 1, 1, "sistema-backplane §8", [
        p("ptc", 15, "uno per slot"),
        a_corpo("bypass e bulk per slot", 15, 30),
    ]),
    ("PSU-IN e ventole (nel mixer)", 1, 1, "sistema-psu-esterno §4", [
        a_corpo("TVS di ingresso", 4, 8),
        p("fus", 5, "fusibili di gruppo"),
        a_corpo("condensatori 2,2 mF + 3 x 1 mF", 10, 20),
        a_corpo("supervisor: comparatori, riferimento", 8, 15),
        p("ventola", 2, "dec. 112"),
        a_corpo("termostato delle ventole", 5, 10),
    ]),
    ("Alimentatore esterno (box)", 1, 1, "sistema-psu-esterno §2", [
        a_corpo("toroidale ~420 VA, 4 secondari, schermo, su misura (dec. 131)", 170, 280, fonte="S"),
        a_corpo("bulk: 2 x 22 mF, 3 x 10 mF, 2 x 4,7 mF, 35 V 105 C", 75, 135),
        p("ponte", 4),
        a_corpo("LDO discreti: MOSFET, riferimenti, op-amp", 25, 45),
        a_corpo("aletta, Rth <= 0,43 K/W", 30, 60),
        a_corpo("contenitore metallico", 60, 130),
        a_corpo("presa IEC con filtro, interruttore, fusibile", 15, 30),
        a_corpo("soft-start NTC e rele'", 8, 15),
        p("fus", 6),
        a_corpo("connettore circolare IP65 >= 20 poli + PE, coppia", 60, 130),
        a_corpo("cavo schermato multipolare 2 m", 20, 45),
        a_corpo("rivelatore AC_OK", 3, 6),
    ]),
]

def conta(chiave):
    return sum(q * n for (_, n, _, _, righe) in MODULI for (d, q, *_r) in righe if d == PREZZI[chiave][0])


N_VCA, N_TRIM = conta("vca"), conta("trim")

# Circuiti stampati: un giro di prototipo = 5 copie per disegno + spedizione.
PCB = [
    ("canale CDJ", 35, 70), ("FX-SEND", 20, 45), ("ritorno FX (un disegno, 4 copie)", 35, 80),
    ("filtro (4 strati)", 70, 150), ("5-way (4 strati)", 70, 150),
    ("master out", 35, 70), ("CUE", 20, 45), ("metering", 35, 70),
    ("MIC", 20, 45), ("MONO", 20, 45), ("backplane (~75 cm, in due pezzi)", 80, 200),
    ("PSU-IN", 20, 45), ("box", 25, 50),
]

COMUNI = [
    a_corpo("cablaggio pannello-schede: cavetti, connettori, schermati", 120, 250),
    a_corpo("minuteria: viti, distanziali, staffe", 50, 100),
    a_corpo("cappucci delle 115 manopole, stampa 3D (dec. 124)", 20, 40),
    a_corpo("scorte: 22 VCA in piu' (lotto ~100), passivi di riserva", 110, 200),
]

TELAIO = [
    a_corpo("pannelli frontali in alluminio incisi (~0,3 m2, Schaeffer)", 800, 1500, fonte="W"),
    a_corpo("struttura interna e fondo in alluminio", 200, 450),
    a_corpo("flight case su misura", 250, 600, fonte="W"),
]

PROTOTIPO = [
    a_corpo("millefori, zoccoli, fili per la fase 1 (canale, FX, master, PSU)", 120, 250),
    a_corpo("secondo giro di PCB (rev. B, stima: 60 % del primo)", 0, 0),  # calcolato sotto
]

OPZIONALI = [
]

STRUMENTI = [
    a_corpo("oscilloscopio a 4 canali di fascia bassa", 350, 500),
    a_corpo("multimetro", 60, 150),
    a_corpo("stazione saldante", 80, 200),
    a_corpo("alimentatore da banco duale", 100, 200),
    a_corpo("trasformatore d'isolamento o variac", 120, 250),
]

FONTI = {
    "M": "Mouser / DigiKey, prezzi letti il 2026-10-22 (pezzo singolo e lotto da 100)",
    "L": "LCSC, prezzi letti il 2026-10-22",
    "R": "RS Components, prezzi letti il 2026-10-22",
    "W": "listini e gallerie di Schaeffer AG e di negozi di flight case, letti il 2026-10-22",
    "D": "prezzi gia' raccolti nei documenti del progetto (settembre-ottobre 2026)",
    "S": "stima di Claude, senza preventivo",
}


def somma(righe):
    lo = sum(min(q * a, q * b) for _, q, a, b, *_ in righe)
    hi = sum(max(q * a, q * b) for _, q, a, b, *_ in righe)
    return lo, hi


def eur(x):
    s = f"{round(x):,}".replace(",", ".")
    return f"{s} €"


def forchetta(lo, hi):
    return f"{eur(lo)} – {eur(hi)}"


def tabella(righe):
    out = ["| Voce | Qtà | € al pezzo | Totale | Fonte | Note |",
           "|---|---|---|---|---|---|"]
    for d, q, a, b, f, n, al_pezzo in righe:
        unit = f"{a:.2f} – {b:.2f}".replace(".", ",") if al_pezzo else "a corpo"
        lo, hi = sorted((q * a, q * b))
        out.append(f"| {d} | {q} | {unit} | {forchetta(lo, hi)} | {f} | {n} |")
    lo, hi = somma(righe)
    out.append(f"| **Totale** | | | **{forchetta(lo, hi)}** | | |")
    return "\n".join(out), lo, hi


def main():
    t = []
    w = t.append
    w("# 09 — Budget dei moduli e del mixer completo [STIMA]")
    w("")
    w(f"Data: {DATA}. Generato da `docs/budget/genera_budget.py`: i prezzi e le")
    w("quantità si correggono lì, poi si rilancia lo script. Non a mano qui.")
    w("")
    w("Cosa è: il costo dei materiali per costruire **un** esemplare, modulo per")
    w("modulo, con una forchetta minimo – massimo. Le quantità vengono dai design")
    w(f"doc alla data (~{N_VCA} VCA, 115 manopole, 4 canali). Gli acquisti restano")
    w("sospesi fino al prototipo in Live (voce 37, A12): questo documento non")
    w("ordina niente.")
    w("")
    w("Prezzi: euro per pezzo, **IVA esclusa**, per lotti da decine di pezzi.")
    w("L'IVA (22 %) si aggiunge nel riepilogo. Le fonti sono in fondo: dove la")
    w("fonte è S il prezzo è una stima, senza preventivo.")
    w("")

    blocchi = []
    for nome, n_full, n_rid, doc, righe in MODULI:
        tab, lo, hi = tabella(righe)
        blocchi.append((nome, n_full, n_rid, doc, tab, lo, hi))

    pcb_lo = sum(a for _, a, _ in PCB)
    pcb_hi = sum(b for _, _, b in PCB)
    com_lo, com_hi = somma(COMUNI)
    tel_lo, tel_hi = somma(TELAIO)
    pro_lo, pro_hi = somma(PROTOTIPO[:1])
    pro_lo += 0.6 * pcb_lo
    pro_hi += 0.6 * pcb_hi

    full_lo = sum(lo * n for _, n, _, _, _, lo, _ in blocchi)
    full_hi = sum(hi * n for _, n, _, _, _, _, hi in blocchi)
    rid_lo = sum(lo * n for _, _, n, _, _, lo, _ in blocchi)
    rid_hi = sum(hi * n for _, _, n, _, _, _, hi in blocchi)

    def totale(el_lo, el_hi):
        lo = el_lo + pcb_lo + com_lo + tel_lo + pro_lo
        hi = el_hi + pcb_hi + com_hi + tel_hi + pro_hi
        return lo, hi

    tf = totale(full_lo, full_hi)
    tr = totale(rid_lo, rid_hi)

    w("## 1. Riepilogo")
    w("")
    w("| Modulo | € per modulo | Copie (completo) | Completo | Copie (ridotto) | Ridotto |")
    w("|---|---|---|---|---|---|")
    for nome, n_full, n_rid, _, _, lo, hi in blocchi:
        w(f"| {nome} | {forchetta(lo, hi)} | {n_full} | {forchetta(lo * n_full, hi * n_full)} "
          f"| {n_rid} | {forchetta(lo * n_rid, hi * n_rid)} |")
    w(f"| **Elettronica dei moduli** | | | **{forchetta(full_lo, full_hi)}** | | **{forchetta(rid_lo, rid_hi)}** |")
    w(f"| Circuiti stampati, un giro (§4) | | | {forchetta(pcb_lo, pcb_hi)} | | {forchetta(pcb_lo, pcb_hi)} |")
    w(f"| Cablaggio, minuteria, cappucci, scorte (§5) | | | {forchetta(com_lo, com_hi)} | | {forchetta(com_lo, com_hi)} |")
    w(f"| Telaio, pannelli, flight case (§6) | | | {forchetta(tel_lo, tel_hi)} | | {forchetta(tel_lo, tel_hi)} |")
    w(f"| Prototipo: millefori e secondo giro di PCB (§7) | | | {forchetta(pro_lo, pro_hi)} | | {forchetta(pro_lo, pro_hi)} |")
    w(f"| **Totale IVA esclusa** | | | **{forchetta(*tf)}** | | **{forchetta(*tr)}** |")
    w(f"| **Totale IVA inclusa (22 %)** | | | **{forchetta(tf[0] * (1 + IVA), tf[1] * (1 + IVA))}** | | "
      f"**{forchetta(tr[0] * (1 + IVA), tr[1] * (1 + IVA))}** |")
    w("")
    w("Setup completo: 4 canali con 4 FX-SEND, 1 MIC, 3 MONO. Setup ridotto: 2")
    w("canali con 2 FX-SEND, 1 MIC, 1 MONO (come i disegni in `docs/pannelli/`).")
    w("Il telaio è contato uguale nei due: la larghezza è 19\" in entrambi.")
    w("")
    w("**Fuori dal totale**: manodopera di montaggio (dipende da chi costruisce,")
    w("A8), moduli opzionali (§8), strumenti di misura (§9), spedizioni dei singoli")
    w("ordini (~15-30 € per ordine sotto la soglia di spedizione gratuita).")
    w("")

    w("## 2. Dove vanno i soldi")
    w("")
    pesi = sorted(((n * (lo + hi) / 2, nome) for nome, n, _, _, _, lo, hi in blocchi), reverse=True)
    tot_mid = (tf[0] + tf[1]) / 2
    for val, nome in pesi[:5]:
        w(f"- **{nome}**: ~{eur(val)} al centro della forchetta, "
          f"{100 * val / tot_mid:.0f} % del totale IVA esclusa.")
    w(f"- **Telaio e pannelli**: ~{eur((tel_lo + tel_hi) / 2)}, "
      f"{100 * (tel_lo + tel_hi) / 2 / tot_mid:.0f} %. Sono la voce singola più grande:")
    w("  i pannelli incisi a misura costano più di tutto il silicio di un modulo.")
    w("")
    w("Tre fatti che pesano:")
    w("")
    w(f"1. **I VCA e i loro trimmer.** ~{N_VCA} chip a 2,80-5 € fanno {N_VCA*2.8:.0f}-{N_VCA*5:.0f} €; ogni")
    w(f"   chip vuole 3 trimmer di taratura (`sistema-vca-trim.md`): ~{N_TRIM} trimmer")
    w("   in tutto il mixer. I 4 FX-RET portano 10 VCA ciascuno, 40 in tutto.")
    w("2. **I prezzi del VCA clone sono deboli.** Non ho trovato oggi un listino")
    w("   europeo aggiornato del V2181L: il prezzo viene dai documenti di settembre")
    w("   e da un annuncio eBay (~4,30 € a pezzo). Lo stock è a lotti (voce 37).")
    w("3. **Il core del filtro (B1) sposta il conto.** Col core PULITO (c-B) il")
    w("   filtro sale (§3.1): +16 VCA e +48 trimmer.")
    w("")

    w("## 3. Moduli, riga per riga")
    w("")
    for i, (nome, n_full, n_rid, doc, tab, lo, hi) in enumerate(blocchi):
        w(f"### {nome}")
        w("")
        w(f"Fonte delle quantità: {doc}. Copie: {n_full} nel completo, {n_rid} nel ridotto.")
        w("")
        w(tab)
        w("")
        if nome.startswith("Filtro"):
            var = [p("vca", 16, "2 per sezione, 4 per core"), p("trim", 48),
                   p("opa1654", 4, "integratori"),
                   ("LM13700 in meno (resta solo la RES)", -8, 0.6, 2.0, "L", "", True)]
            vt, vlo, vhi = tabella(var)
            w("#### 3.1 Variante: core PULITO (c-B) a 4 poli")
            w("")
            w("Differenza rispetto al core (a′), se B1 sceglie il PULITO")
            w(f"(`sim/filtro/RISULTATI-cb-4p.md`). I VCA del mixer salgono da ~{N_VCA} a")
            w(f"~{N_VCA+16}: da riverificare anche W1 dell'alimentatore.")
            w("")
            w(vt)
            w("")
            w(f"Filtro col core PULITO: {forchetta(lo + vlo, hi + vhi)}.")
            w("")

    w("## 4. Circuiti stampati")
    w("")
    w("Un giro di prototipo: 5 copie per disegno (il minimo dei produttori come")
    w("JLCPCB), 2 strati salvo dove indicato, spedizione e dazio compresi.")
    w("Stima di Claude: i listini a superficie non valgono per schede così grandi.")
    w("")
    w("| Scheda | € |")
    w("|---|---|")
    for nome, a, b in PCB:
        w(f"| {nome} | {forchetta(a, b)} |")
    w(f"| **Totale** | **{forchetta(pcb_lo, pcb_hi)}** |")
    w("")

    w("## 5. Voci comuni")
    w("")
    tab, _, _ = tabella(COMUNI)
    w(tab)
    w("")
    w("Cappucci: se invece di stamparli si comprano a catalogo, 1,5-3 € l'uno,")
    w("cioè 170-350 € per 115 manopole.")
    w("")

    w("## 6. Telaio")
    w("")
    tab, _, _ = tabella(TELAIO)
    w(tab)
    w("")
    w("Pannelli: Schaeffer chiede ~140 € IVA inclusa per un pannello inciso di")
    w("18 × 18 cm, cioè ~0,35-0,45 € al cm² IVA esclusa. Il frontale del")
    w("mixer completo è ~45 × 65 cm. Alternativa da chiedere: un'officina CNC")
    w("locale con stampa UV, forse metà prezzo. Il flight case di serie per")
    w("mixer da 19\" inclinato costa ~250-300 €; su misura per la profondità del")
    w("mixer, di più. Misure e nome sul telaio restano dopo il prototipo (A10).")
    w("")

    w("## 7. Prototipo")
    w("")
    w("Regola 5 del progetto: fase 1 su millefori (canale, FX, master, PSU base)")
    w("prima di qualunque PCB. I componenti della fase 1 si riusano. Il secondo")
    w("giro di PCB (rev. B) è prudente: quasi ogni scheda nuova ne chiede uno.")
    w("")
    w(f"- millefori e minuteria: {forchetta(*somma(PROTOTIPO[:1]))}")
    w(f"- secondo giro di PCB, 60 % del primo: {forchetta(0.6 * pcb_lo, 0.6 * pcb_hi)}")
    w("")

    w("## 8. Moduli opzionali (dec. 111)")
    w("")
    for nome, righe in OPZIONALI:
        tab, lo, hi = tabella(righe)
        w(f"### {nome}")
        w("")
        w(tab)
        w("")
    w("EQ grafico, uscite per via e sirena: non progettati, quindi non stimati.")
    w("")

    w("## 9. Strumenti di misura (A11, rinviata)")
    w("")
    w("Non fanno parte del mixer: servono al banco. Lo Zoom e una scheda audio con")
    w("REW bastano per le misure audio (voce 30).")
    w("")
    tab, _, _ = tabella(STRUMENTI)
    w(tab)
    w("")

    w("## 10. Cosa può cambiare il conto")
    w("")
    w("- **B1, core del filtro**: il PULITO aggiunge la cifra del §3.1.")
    w("- **Prezzo e stock del VCA clone**: ±1 € a pezzo vale ±100 € sul lotto.")
    w("- **Pannelli**: Schaeffer o officina locale, una forchetta da centinaia di euro.")
    w("- **Chi monta (A8)**: montaggio SMT dal produttore delle PCB toglie ore di")
    w("  saldatura ma costa a parte, da preventivare.")
    w("- **Pot doppio da 1k del WIDTH**: se non esiste a 14 mm, il circuito passa")
    w("  a 10k (todo aperto in five-way §4.3), costo quasi uguale.")
    w(f"- **Taratura**: nessun costo di materiale, ma ~{N_TRIM} trimmer da regolare a")
    w("  banco sono giorni di lavoro.")
    w("")

    w("## Fonti")
    w("")
    for k, v in FONTI.items():
        w(f"- **{k}**: {v}.")
    w("")
    w("Pagine lette il 2026-10-22: Mouser OPA1612AID ($7,63-8,47 a 1 pz),")
    w("OPA1654 ($2,81 a 1 pz, ~$1,5 a 500), Alps RK14K1240036 (Mouser FR")
    w("~2,24 € a 1 pz), Alps RK09K113004U (LCSC $0,31-0,67), Alps RS60N 100 mm")
    w("(RS NL 12,46 € a 1 pz, 8,83 € a 100), Neutrik NC3FAH ($1,90), ADG1434YRUZ")
    w("(Richardson $6,69), LM3915N-1 (Win Source ~$2, Farnell ~$3,35), LM13700")
    w("(LCSC $0,60), toroidale Block 300 VA 2 × 18 V (RS 137 €), Schaeffer AG")
    w("galleria prezzi, ProDJuser Slant 19\" (259 €).")
    w("")

    with open(OUT, "w") as f:
        f.write("\n".join(t))
    print(f"scritto {os.path.normpath(OUT)}")
    print(f"completo: {forchetta(*tf)} IVA esclusa, {forchetta(tf[0] * 1.22, tf[1] * 1.22)} IVA inclusa")
    print(f"ridotto:  {forchetta(*tr)} IVA esclusa, {forchetta(tr[0] * 1.22, tr[1] * 1.22)} IVA inclusa")
    for nome, n, _, _, _, lo, hi in blocchi:
        print(f"  {nome}: {forchetta(lo, hi)} x{n}")
    print(f"  PCB {forchetta(pcb_lo, pcb_hi)}, comuni {forchetta(com_lo, com_hi)}, "
          f"telaio {forchetta(tel_lo, tel_hi)}, prototipo {forchetta(pro_lo, pro_hi)}")


if __name__ == "__main__":
    main()
