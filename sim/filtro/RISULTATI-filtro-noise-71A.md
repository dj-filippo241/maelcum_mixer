# RISULTATI — Rerun rumore filtro (voce 71A, metodo corretto)

Data: 2026-09-30. Netlist: `svf-noise-71A-{114n,10.8u,397u}.cir` (uscita A,
core nudo) e `svf-noise-71A-B-{114n,10.8u,397u}.cir` (uscita B, scalato
1/20 + make-up ×20). Circuiti IDENTICI agli one-shot storici
`svf-noise-{114n,10.8u,397u}.cir` (conservati): cambia solo il metodo di
misura. Integrazione: densità a 31 punti (griglia 1/6 ottava, 20 Hz-20 kHz)
da `.meas FIND V(onoise)`, trapezoidale in python3 sul dominio en². MAI
`.meas INTEG` (quirk LTspice 26.0.2: integra en²·√Δf, five-way §8.9 e
`RISULTATI-module-noise-v021.md` §1). Pesatura A calcolata in post
(IEC 61672, normalizzata a 1 kHz). Errore di trapezoidale su spettro
1/f² con griglia 1/6 ottava: ≈ +0,02 dB (trascurabile). Punto di misura
dichiarato: A = voutA (buffer dello stato LP, gain ~1 in banda, core nudo,
ingresso V1 terminato su RvinA 10k); B = voutB (make-up ×20). Banda
dichiarata 20 Hz-20 kHz (sotto 20 Hz escluso, coerente col metodo
module-noise).

## 1. Istanza A — core nudo (i numeri "ufficiali" invalidati)

| Iabc | fc | den @20 Hz | den @1 kHz | den @20 kHz | en integrato | dBu unwt | dBu A-wtd | INTEG (invalido) | delta |
|---|---|---|---|---|---|---|---|---|---|
| 114 n | 10,6 Hz | 90,1 nV | 1,7 nV | 0,1 nV | 0,389 µV | **−126,0** | −139,2 | −134,8 | +8,8 |
| 10,8 µ | 1 kHz | 1086 nV | 20,3 nV | 0,6 nV | 5,07 µV | **−103,7** | −117,4 | −112,7 | +9,1 |
| 397 µ | 37 kHz | 598 nV | 432 nV | 29,2 nV | 23,7 µV | **−90,3** | −91,4 | −107,7 | +17,5 |

## 2. Istanza B — scalato 1/20 + make-up ×20 (proposta SUPERATA, solo contabilità)

| Iabc | fc | den @1 kHz | en integrato | dBu unwt | dBu A-wtd | INTEG (invalido) | delta |
|---|---|---|---|---|---|---|---|
| 114 n | 10,6 Hz | 266 nV | 38,1 µV | −86,2 | −88,4 | −106,4 | +20,2 |
| 10,8 µ | 1 kHz | 565 nV | 44,0 µV | −84,9 | −86,9 | −105,2 | +20,2 |
| 397 µ | 37 kHz | 555 nV (piatta) | 78,0 µV | −79,9 | −81,9 | −101,4 | +21,5 |

Il doc citava B = −81,8 dBu (derivato analitico A×20 dal caso INTEG 37 kHz):
il valore corretto misurato è **−79,9 dBu unwt / −81,9 A-wtd** — la proposta
scalata resta bocciata dal muro del rumore (`RISULTATI-cell-clean.md` §0),
numeri aggiornati per completezza.

## 3. FINDING — la correzione stimata "2-6 dB" era sbagliata due volte

1. **Lo spettro NON è LP band-limited come assunto**: per fc ≤ 1 kHz la
   densità scende ~1/f su TUTTA la banda (es. 10,8 µ: 1086 nV @20 Hz →
   20 nV @1 kHz), dominio LF (Rb 100Meg + impedenze di loop OTA: 100 MΩ
   = 40,7 µV/√Hz termici sagomati dall'anello). Il quirk INTEG su spettro
   1/f dà **+8,8…+9,1 dB**, non 2-6.
2. **Il caso fc alta è quasi bianco in banda**: a 37 kHz lo spettro è
   quasi piatto fino a ~1 kHz → correzione **+17,5 dB** ≈ il 21,5 dB del
   caso bianco puro (il roll-off oltre fc ne lima ~4).

## 4. Impatto sui target (per la ritaratura 71A)

- **Core nudo a fc massima (35-37 kHz): −90,3 dBu unwt / −91,4 A-wtd contro
  il target sheet "send 0 dBu ≤ −90" → margine ≈ 0…−1,4 dB: AL LIMITE, e
  solo in SIMULAZIONE con en OTA fisico ideale.** Il claim storico "die
  reale 2-5× peggio: ~−94, ancora PASS" NON REGGE più sul numero corretto:
  +6…+14 dB di peggioramento die su −90,3 → **−84…−76 dBu = FAIL 6-14 dB**.
  Il rumore del core OTA nudo (scelta musicale (a) di q70) deve entrare
  nella ritaratura sheet §3 / nel design di sistema; l'alternativa (c-B)
  VCA nel loop (questione 70 lato filtro) torna rilevante anche per il
  rumore, non solo per la pulizia THD.
- A fc basse il core è largamente sotto target (−126…−104 dBu): il rumore
  del filtro cresce con fc (banda passante + en OTA che scende con Iabc ma
  non quanto la banda sale).
- I delta INTEG misurati (+8,8 / +9,1 / +17,5) sostituiscono la "correzione
  stimata 2-6 dB" nella voce 71A.

## 5. Note di metodo

- Run one-shot per Iabc (con `.step` la linearizzazione `.noise` cade nel
  ramo DC falso del loop SVF bistabile → zero: lezione già documentata
  nell'header dei netlist storici, rispettata).
- `.nodeset` sugli stati + `.options gmin=1e-9 abstol=1e-11 vntol=1e-8`
  (come storici). Macro OPX senza clamp (il `limit()` di opamp-audio.inc
  rende il loop bistabile in DC) con Rn 1223 = 4,5 nV/√Hz.
- La riga `.meas INTEG` è stata lasciata nei netlist 71A SOLO come
  riferimento per il delta (colonna "INTEG (invalido)").
- LM13700 model = `sim/lib/lm13700.inc` (en fisico re = 2VT/Iabc; il die
  reale è stimato 2-5× peggio — header `RISULTATI-ota-real.md`).
