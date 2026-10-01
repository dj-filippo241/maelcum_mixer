# 00 — Piano design di sistema (fase 3)

Data: 2026-10-01. Origine: task 1 handoff (voci 18-22 docs/02) + decisione
90 (metering a barre LED a zone, CUE blend, PSU toroidale unico).
Regole: 2 (numeri musicali → ratifica Filippo), 3 (niente valori congelati
prima della topologia — tutto [PROVVISORIO] fino al prototipo), metodo di
simulazione §8.9 five-way (densità 10+ punti, mai INTEG).

## Workstream

| # | Area | Voce | Deliverable | Sim |
|---|---|---|---|---|
| S1 | PSU | q20 | `sistema-psu.md` + `sim/system/psu-*.cir` | ripple/PSRR rail, protezione corto prolungato (tran), rumore CV 61 mV/dB |
| S2 | Grounding | q21 | `sistema-grounding.md` (+ diagramma) | no |
| S3 | Backplane | q22 | `sistema-backplane.md` + pinout | no |
| S4 | Metering | q19 | `sistema-metering.md` + `sim/system/meter-*.cir` | soglie/tarature driver, latch purple |
| S5 | CUE | q18 | `sistema-cue.md` + `sim/system/cue-*.cir` | summing multi-cue, blend, ampli cuffia su 32-250 Ω, crosstalk |

Dipendenze: S1 definisce i rail per tutti; S2/S3 si toccano (la stella di
massa viaggia sul backplane) → stesso esecutore; S4/S5 indipendenti
(usano i tap dei moduli già disegnati).

## Vincoli già bloccati (da non ridiscutere)

- Rail ±18 V audio con regolazione locale LM317/337 + RC/cap-moltiplicator
  (sheet §1); ±15/16 V OTA con LT3045/LT3094 (dec. 54, LM13700 assoluto
  ±18); ±15 V switch/logica (dec. 88/§8.10 five-way: ADG1434-class, max
  ±16,5 V; 3 IC/modulo 5-way + assign FX + LINE/PHONO).
- Mute power-on: i transienti ±15 V all'accensione sono coperti dal mute
  (master-out §3.7) → la PSU deve fornire il controllo mute e il sequencing.
- Corto prolungato master: 106 mA auto-limitati dal bootstrap, Q1 1,0 W
  medi = worst di programma (master-out v0.3) → l'abuso prolungato è
  dominio PSU (dec. 88/90): proteggere senza limitare il programma.
- Metering: ballistica dec. 81 (attacco rapido, release ~0,3 s banco
  0,2-0,5, latch clip 442 ms); peak detector validato `sim/meter/`;
  soglie dec. 90: verde ≤+6, ambra +6…+18, rosso +18…+24, purple ≥+23.
- CUE: punto locked post-EQ/pre-filter/pre-fader; blend CUE↔Master +
  level; 2 uscite parallele; ~1 Vrms su 32-250 Ω (sheet §2).
- Rumore: sistema ≤ −78 dBu A-wtd (dec. 89) — ogni aggiunta (CUE, meter
  pickup, PSU) non deve eroderlo; dominio CV: THAT raccomanda 61 mV/dB
  (10× la nostra 6,1 mV/dB, nota dec. 88c) → analisi in S1.

## Ordine di esecuzione

1. Ondata 1 (parallelo): S1 PSU · S2+S3 grounding/backplane · S4 metering
2. Ondata 2: S5 CUE (dopo S1: rail e mute definiti)
3. Integrazione: decisioni ingegneristiche → docs/01 (se bloccate da
   Filippo), questioni 18-22 aggiornate, sheet §1/§2 se cambia qualcosa,
   CLAUDE.md; review di completezza; commit.

## Stato

- [ ] S1 PSU
- [ ] S2 Grounding
- [ ] S3 Backplane
- [ ] S4 Metering
- [ ] S5 CUE
- [ ] Integrazione + review
