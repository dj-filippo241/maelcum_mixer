#!/usr/bin/env python3
"""regole_gen.py - controlla le regole gen~ "pagate" del prototipo (CLAUDE.md, «Codice gen~» e
«Prototipo in Live»). Legge e basta.

Uso:  python3 proto-max/coefficienti/regole_gen.py [cartella]   (default: proto-max/)

  R1  funzioni con un solo valore di ritorno (niente "return a, b;" ne' "a, b = f(...)")
  R2  nessun nome esterno uguale a un parametro o a una locale di una funzione
  R3  d0/d1 sono del downsampling: non vanno usati dentro una funzione
  R4  niente send~/receive~ nei .maxpat (in Live i bus fra dispositivi M4L sono muti).
      AVVISO finche' il todo 209 e' aperto (MC-BUS, MC-MIC, MC-RET, MC-SEND li usano ancora);
      poi diventa ERRORE: R4_ERRORE = True.
  R5  coefficienti enormi (|x| >= 1e7): indizio di polinomio di ordine alto nella bilineare
  (R6, versione -S allineata: la controlla prova_semplice.py confrontando il codice, non le date.)

Esito: 0 = PASSA, 1 = NON PASSA (almeno un ERRORE), 2 = uso sbagliato. Gli AVVISI non fanno fallire.
Origine: prototipo lint_gen di BURN (4/11/2026), unito qui il 2026-11-10 (todo 267).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

PAROLE_GEN = {
    "if", "else", "for", "while", "return", "break", "continue", "Param", "History", "Data",
    "Buffer", "Delay", "in", "out", "samplerate", "pi", "twopi", "halfpi", "e", "int", "float",
}
DICHIARAZIONE = re.compile(r"^\s*(Param|History|Data|Buffer|Delay)\s+(\w+)")
FUNZIONE = re.compile(r"^(\w+)\s*\(([^)]*)\)\s*\{")
ASSEGNA = re.compile(r"^\s*(\w+)\s*=(?!=)")
ASSEGNA_MULTI = re.compile(r"^\s*\w+\s*,\s*\w+(\s*,\s*\w+)*\s*=(?!=)")
NUMERO = re.compile(r"(?<![\w.])(\d+\.?\d*(?:[eE][+-]?\d+)?)")
MAX_COEFF = 1e7
R4_ERRORE = False  # todo 209: True quando i bus FX non usano piu' send~/receive~


def senza_commenti(testo: str) -> str:
    testo = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), testo, flags=re.S)
    return "\n".join(r.split("//", 1)[0] for r in testo.split("\n"))


def virgola_fuori_parentesi(espr: str) -> bool:
    livello = 0
    for c in espr:
        if c in "([":
            livello += 1
        elif c in ")]":
            livello -= 1
        elif c == "," and livello == 0:
            return True
    return False


def analizza(file: Path) -> list:
    """Torna una lista di (livello, regola, riga, messaggio)."""
    righe = senza_commenti(file.read_text(encoding="utf-8", errors="replace")).split("\n")
    esiti = []
    funzioni = {}   # nome -> {"riga", "nomi": {nome: riga}}
    esterni = {}    # nome -> riga
    corrente, profondita = None, 0
    for n, riga in enumerate(righe, 1):
        if corrente is None:
            m = FUNZIONE.match(riga)
            if m and m.group(1) not in PAROLE_GEN:
                nome, argomenti = m.group(1), m.group(2)
                corrente = {"riga": n, "nomi": {}}
                funzioni[nome] = corrente
                for a in (x.strip() for x in argomenti.split(",")):
                    if a:
                        corrente["nomi"].setdefault(a, n)
                profondita = riga.count("{") - riga.count("}")
                if profondita <= 0:
                    corrente = None
                continue
            d = DICHIARAZIONE.match(riga)
            if d:
                esterni.setdefault(d.group(2), n)
            else:
                a = ASSEGNA.match(riga)
                if a and a.group(1) not in PAROLE_GEN:
                    esterni.setdefault(a.group(1), n)
            if ASSEGNA_MULTI.match(riga):
                esiti.append(("ERRORE", "R1", n, "assegnazione multipla da funzione: " + riga.strip()))
        else:
            profondita += riga.count("{") - riga.count("}")
            a = ASSEGNA.match(riga)
            if a and a.group(1) not in PAROLE_GEN:
                corrente["nomi"].setdefault(a.group(1), n)
            r = re.match(r"^\s*return\b(.*);", riga)
            if r and virgola_fuori_parentesi(r.group(1)):
                esiti.append(("ERRORE", "R1", n, "return con piu' valori: " + riga.strip()))
            if ASSEGNA_MULTI.match(riga):
                esiti.append(("ERRORE", "R1", n, "assegnazione multipla: " + riga.strip()))
            for parola in ("d0", "d1"):
                if re.search(rf"\b{parola}\b", riga):
                    esiti.append(("ERRORE", "R3", n, f"{parola} usato dentro una funzione (e' del downsampling)"))
            if profondita <= 0:
                corrente = None
        for num in NUMERO.findall(riga):
            try:
                if abs(float(num)) >= MAX_COEFF:
                    esiti.append(("AVVISO", "R5", n, f"coefficiente {num}: polinomio di ordine alto?"))
            except ValueError:
                pass
    for fnome, f in funzioni.items():
        for nome, riga_f in f["nomi"].items():
            if nome in esterni:
                esiti.append(("ERRORE", "R2", riga_f,
                              f"'{nome}' in {fnome}() ha lo stesso nome di un nome esterno (riga {esterni[nome]})"))
    return esiti


def controlla_maxpat(file: Path) -> list:
    esiti = []
    for n, riga in enumerate(file.read_text(encoding="utf-8", errors="replace").split("\n"), 1):
        m = re.search(r'"text"\s*:\s*"((?:send~|receive~)[^"]*)"', riga)
        if m:
            esiti.append(("ERRORE" if R4_ERRORE else "AVVISO", "R4", n, f"oggetto '{m.group(1)}': in Live i bus fra dispositivi M4L sono muti"))
    return esiti


def main(argv: list) -> int:
    if len(argv) > 2:
        print(__doc__)
        return 2
    cartella = Path(argv[1]).expanduser() if len(argv) == 2 else Path(__file__).resolve().parent.parent
    if not cartella.is_dir():
        print(f"Cartella non trovata: {cartella}")
        return 2
    tutti = []
    for f in sorted(cartella.glob("*.genexpr")):
        tutti += [(f.name, *e) for e in analizza(f)]
    for f in sorted(cartella.glob("*.maxpat")):
        tutti += [(f.name, *e) for e in controlla_maxpat(f)]

    errori = [e for e in tutti if e[1] == "ERRORE"]
    avvisi = [e for e in tutti if e[1] == "AVVISO"]
    for nome, livello, regola, riga, msg in tutti:
        dove = f"{nome}:{riga}" if riga else nome
        print(f"{livello:6} {regola}  {dove}  {msg}")
    n_file = len(list(cartella.glob("*.genexpr"))) + len(list(cartella.glob("*.maxpat")))
    esito = "NON PASSA" if errori else "PASSA"
    print(f"\n{esito}: {len(errori)} errori, {len(avvisi)} avvisi su {n_file} file.")
    return 1 if errori else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
