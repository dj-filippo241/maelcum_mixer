#!/usr/bin/env python3
"""Linter dei netlist LTspice del progetto (Python 3 puro, nessun pacchetto).

Controlla le «Regole di simulazione» di CLAUDE.md: ogni regola nasce da un
errore già pagato. Il linter segnala, non corregge.

Uso:
    python3 sim/lint_cir.py [file.cir ...] [--solo-errori]

Senza file: tutti i .cir di sim/ tranne le cartelle superate
(sim/cdj-eq/, sim/eq-serie/, sim/master-out/compG-*, sim/five-way/drive-*).
Codice d'uscita 1 se c'è almeno un ERRORE.

ERRORI
  E1  .meas ... INTEG in un netlist con .noise (totali ~21,5 dB ottimisti)
  E2  FIND dB( in un .meas
  E3  .ac list con un solo punto insieme a .meas ac
  E4  SINE con ampiezza uguale a un valore EFFICACE (0.775, 6.16, 1.228)
  E5  uic in un netlist di sim/system/psu-box-*
  E6  .include con percorso assoluto
AVVISI
  W1  .tran con 2+ op-amp della libreria, senza .nodeset/.ic/uic
  W2  sorgente E comportamentale (value=/table) in un netlist con .noise

Esenzione: «* lint-ok: E4 motivo» sulla riga precedente, oppure
«; lint-ok: E4 motivo» in coda alla riga, silenzia quella regola su
quella riga (più codici: «lint-ok: E4,W1»).
"""
import collections
import glob
import math
import os
import re
import sys

SIM = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(SIM, 'lib')

ERRORI = ('E1', 'E2', 'E3', 'E4', 'E5', 'E6')
TUTTE = ERRORI + ('W1', 'W2')

# valori efficaci che non vanno usati come picco in SINE()
EFFICACI = ((0.775, '0 dBu efficace; picco = 1.095'),
            (6.16, '+18 dBu efficace; picco = 8.70'),
            (1.228, '+4 dBu efficace; picco = 1.737'))
TOLL = 0.005

SUFFISSI = {'t': 1e12, 'g': 1e9, 'meg': 1e6, 'k': 1e3, 'm': 1e-3,
            'u': 1e-6, 'µ': 1e-6, 'n': 1e-9, 'p': 1e-12, 'f': 1e-15}


def numero(s):
    """Numero SPICE (1k, 10m, 2.2meg, 1e-3) -> float, oppure None."""
    s = s.strip().strip('{}').lower()
    m = re.fullmatch(r'([-+]?(?:\d+\.?\d*|\.\d+)(?:e[-+]?\d+)?)(meg|[tgkmuµnpf])?[a-z]*', s)
    if not m:
        return None
    return float(m.group(1)) * SUFFISSI.get(m.group(2) or '', 1.0)


def esclusa(path):
    p = path.replace(os.sep, '/')
    return ('/cdj-eq/' in p or '/eq-serie/' in p or '/master-out/compG-' in p
            or '/five-way/drive-' in p)


def subckt_lib():
    """Nomi dei subckt definiti in sim/lib (tutti) e in opamp-audio.inc."""
    tutti, opamp = set(), set()
    for f in glob.glob(os.path.join(LIB, '*')):
        try:
            testo = open(f, errors='ignore').read()
        except OSError:
            continue
        for m in re.finditer(r'^\s*\.subckt\s+(\S+)', testo, re.I | re.M):
            tutti.add(m.group(1).lower())
            if os.path.basename(f).lower().startswith('opamp-audio'):
                opamp.add(m.group(1).lower())
    return tutti, opamp


SUB_LIB, SUB_OPAMP = subckt_lib()


def logiche(testo):
    """Righe logiche: (numero riga, testo senza commento, esenzioni).

    Unisce le continuazioni «+», toglie i commenti «*» e «;».
    Le esenzioni valgono dalla riga commento precedente e dalla coda «;».
    """
    righe = testo.splitlines()
    out = []
    pendenti = set()
    for i, r in enumerate(righe, 1):
        s = r.strip()
        if not s:
            continue
        if s.startswith('*'):
            m = re.search(r'lint-ok\s*:\s*([A-Z0-9, ]+)', s, re.I)
            if m:
                pendenti |= set(re.findall(r'[EW]\d', m.group(1).upper()))
            continue
        codice, _, coda = r.partition(';')
        esenti = set(pendenti)
        pendenti = set()
        m = re.search(r'lint-ok\s*:\s*([A-Z0-9, ]+)', coda, re.I)
        if m:
            esenti |= set(re.findall(r'[EW]\d', m.group(1).upper()))
        codice = codice.strip()
        if codice.startswith('+') and out:
            n0, t0, e0 = out[-1]
            out[-1] = (n0, t0 + ' ' + codice[1:].strip(), e0 | esenti)
        elif codice:
            out.append((i, codice, esenti))
    return out


def clamp_uscita(t):
    """E di uscita come nella macro di sim/lib: value={V(n)} o
    value={limit(V(n), ...)}. È la forma che la libreria tiene dopo il
    fix del 2026-10-13 (il rumore passa): non è segnalata."""
    m = re.search(r'value\s*=\s*\{\s*(.*)\}\s*$', t)
    if not m:
        return False
    x = re.sub(r'\s', '', m.group(1))
    return bool(re.fullmatch(r'v\(\w+\)|limit\(v\(\w+\),[^,]+,[^,]+\)', x))


def riconosciuti(testo):
    """Valori efficaci che un commento del file dichiara già come picco.

    Esempio: «6,16 Vp = +15 dBu» o «0,775 = -3 dBu»: il numero è seguito,
    entro 30 caratteri, dal livello in dBu giusto per un PICCO
    (20·log10(v / 1,095)). Chi ha scritto così sa che è un picco.
    """
    noti = set()
    for r in testo.splitlines():
        c = r.strip()
        if not c.startswith('*') and ';' not in c:
            continue
        c = c.replace(',', '.').replace('\u2212', '-')
        for eff, _ in EFFICACI:
            giusto = 20 * math.log10(eff / (0.775 * math.sqrt(2)))
            for m in re.finditer(r'(?<![\d.])%s(?!\d)(.{0,30}?)([-+]?\d+(?:\.\d+)?)\s*dbu'
                                 % re.escape(('%g' % eff)), c.lower()):
                if abs(float(m.group(2)) - giusto) < 0.6:
                    noti.add(eff)
    return noti


def analizza(path):
    try:
        testo = open(path, errors='ignore').read()
    except OSError as e:
        return [(0, 'E6', 'file illeggibile: %s' % e)]
    L = logiche(testo)
    trovati = []

    def segnala(riga, codice, msg, esenti):
        if codice not in esenti:
            trovati.append((riga, codice, msg))

    low = [(n, t.lower(), e) for n, t, e in L]
    ha_noise = any(re.match(r'\.noise\b', t) for _, t, _ in low)
    ha_meas_ac = any(re.match(r'\.meas(ure)?\s+ac\b', t) for _, t, _ in low)
    ha_nodeset = any(re.match(r'\.(nodeset|ic)\b', t) for _, t, _ in low)
    ha_uic = any(re.match(r'\.tran\b', t) and re.search(r'\buic\b', t)
                 for _, t, _ in low)

    # parametri: .param nome=numero e .step param nome LIST ...
    # un .step sostituisce il valore di default del .param
    param = collections.defaultdict(list)   # nome -> [(valore, riga)]
    passo = collections.defaultdict(list)
    for n, t, _ in low:
        if re.match(r'\.param\b', t):
            for m in re.finditer(r'(\w+)\s*=\s*(\{[^}]*\}|[^\s=]+)', t[6:]):
                v = numero(m.group(2))
                if v is not None:
                    param[m.group(1)].append((v, n))
        m = re.match(r'\.step\s+param\s+(\w+)\s+list\s+(.*)', t)
        if m:
            for tok in m.group(2).split():
                v = numero(tok)
                if v is not None:
                    passo[m.group(1)].append((v, n))
    param.update(passo)
    noti = riconosciuti(testo)

    sottocircuito = None
    psu_box = '/system/psu-box' in os.path.abspath(path).replace(os.sep, '/').lower()

    for n, t, es in low:
        m = re.match(r'\.subckt\s+(\S+)', t)
        if m:
            sottocircuito = m.group(1)
            continue
        if re.match(r'\.ends\b', t):
            sottocircuito = None
            continue

        # E1
        if ha_noise and re.match(r'\.meas(ure)?\b', t) and re.search(r'\binteg\b', t):
            segnala(n, 'E1', 'INTEG su .noise: totali ~21,5 dB ottimisti, usare noise_total.py', es)
        # E2
        if re.match(r'\.meas(ure)?\b', t) and re.search(r'\bfind\s+db\s*\(', t):
            segnala(n, 'E2', 'FIND dB(...): usare FIND V(nodo)', es)
        # E3
        m = re.match(r'\.ac\s+list\s+(.*)', t)
        if m and ha_meas_ac and len(m.group(1).split()) <= 1:
            segnala(n, 'E3', '.ac list con un punto solo e .meas ac: serve uno sweep (.ac dec ...)', es)
        # E5
        if psu_box and re.search(r'\buic\b', t):
            segnala(n, 'E5', 'uic nel box PSU: LTspice non termina, accendere da zero', es)
        # E6
        m = re.match(r'\.(include|inc|lib)\s+"?([^"\s]+)', t)
        if m:
            p = m.group(2)
            if p.startswith(('/', '~', '\\')) or re.match(r'[a-z]:[\\/]', p):
                segnala(n, 'E6', 'include assoluto: usare ../lib/... relativo', es)
        # E4
        for m in re.finditer(r'\bsin(?:e)?\s*\(([^)]*)\)', t):
            arg = m.group(1).split()
            if len(arg) < 2:
                continue
            tok = arg[1]
            nome = tok.strip('{}')
            if re.fullmatch(r'[a-z_]\w*', nome):
                valori = param.get(nome, [])
                origine = ' (%s)' % nome
            else:
                v = numero(tok)
                valori = [(v, n)] if v is not None else []
                origine = ''
            for v, rp in valori:
                for eff, nota in EFFICACI:
                    if abs(abs(v) - eff) / eff < TOLL and eff not in noti:
                        esenti = es | dict((r, e) for r, _, e in low).get(rp, set())
                        dove = '' if rp == n else ', riga %d' % rp
                        segnala(n, 'E4', 'SINE con %g%s%s come picco: è il valore %s'
                                % (v, origine, dove, nota), esenti)
        # W2
        if (ha_noise and re.match(r'e\w*\s', t)
                and re.search(r'\bvalue\s*=|\btable\s*[=(]', t)
                and not (sottocircuito and sottocircuito in SUB_LIB)
                and not clamp_uscita(t)):
            segnala(n, 'W2', 'sorgente E comportamentale in .noise: non propaga il rumore', es)

    # W1
    if not ha_nodeset and not ha_uic:
        # un op-amp solo (buffer, summer) converge da sé: servono almeno
        # due op-amp perché ci sia un anello tra stadi
        opamp = 0
        for n, t, _ in low:
            if t.startswith('x'):
                tok = [x for x in t.split() if '=' not in x and x != 'params:']
                if tok and tok[-1] in SUB_OPAMP:
                    opamp += 1
        if opamp >= 2:
            for n, t, es in low:
                if re.match(r'\.tran\b', t):
                    segnala(n, 'W1', '.tran con op-amp senza .nodeset (anelli di retroazione)', es)
    return trovati


def main(argv):
    solo_err = '--solo-errori' in argv
    args = [a for a in argv if a != '--solo-errori']
    if args:
        files = args
    else:
        files = sorted(f for f in glob.glob(os.path.join(SIM, '**', '*.cir'), recursive=True)
                       if not esclusa(f))
    conti = collections.Counter()
    file_err = []
    for f in files:
        ris = analizza(f)
        if solo_err:
            ris = [r for r in ris if r[1] in ERRORI]
        if not ris:
            continue
        nome = os.path.relpath(f)
        if nome.startswith('..'):
            nome = os.path.abspath(f)
        for riga, cod, msg in sorted(ris):
            print('%s:%d  %s  %s' % (nome, riga, cod, msg))
            conti[cod] += 1
        if any(c in ERRORI for _, c, _ in ris):
            file_err.append(nome)
    print()
    print('Riepilogo (%d file controllati, %d con errori):' % (len(files), len(file_err)))
    for c in TUTTE:
        if c in conti:
            print('  %s  %d' % (c, conti[c]))
    if not conti:
        print('  nessuna segnalazione')
    return 1 if file_err else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
