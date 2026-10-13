# RISULTATI — moduli MIC e MONO, architettura v0.1 (2026-10-13, REV dec. 97)

Design: `docs/fase4/mic-mono-moduli.md`. Macro op-amp: `sim/lib/opamp-audio.inc`
DOPO il fix del quirk 3 (vedi §4). Metodo rumore: densità a 16 punti
(20 Hz–20 kHz), integrale trapezoidale e pesatura A in `noise_total.py`,
mai `.meas INTEG`.

## 1. Preamp MIC (`mic-pre.inc`)

| Test | Netlist | Risultato |
|---|---|---|
| Law del gain, pot lineare 0…100% | `mic-pre-ac.cir` | 29,47 / 31,10 / 32,76 / 34,48 / 36,30 / 38,29 / 40,51 / 43,11 / 46,36 / 50,90 / 59,30 dB |
| Banda a 59,3 dB | idem | 20 kHz −0,01 dB · 35 kHz −0,04 dB |
| Passa-alto 60 Hz (ratificato dec. 97) | idem | 100 Hz −0,55 dB · 60 Hz −3,15 dB · 40 Hz −7,96 dB · 20 Hz −19,3 dB |
| EIN, 150 Ω | `mic-pre-noise.cir` | −126,4 / −126,6 / −126,6 dBu a 0 / 50 / 100% (2,61…2,56 nV/√Hz) |
| EIN, 300 Ω | `mic-pre-noise-rs300.cir` | −124,6…−124,8 dBu |
| EIN, 600 Ω | `mic-pre-noise-rs600.cir` | −122,1…−122,2 dBu |
| Uscita preamp A-wtd, 150 Ω | `mic-pre-noise.cir` | −98,9 / −90,2 / −69,3 dBu |
| CMRR, R diff 0,1% | `mic-pre-cmrr.cir` | 95,5 dB |
| CMRR + sorgente sbilanciata 10 Ω | idem | 74,2 dB (con bias 2×10k: 60,3 dB → bias portato a 2×47k) |
| CMRR + bias 47k all'1% | idem | 73,5 dB |

Corrente di rumore OPA1612 (1,7 pA/√Hz) non nel macro: +0,03 dB a 150 Ω,
+0,13 dB a 600 Ω (calcolo).

## 2. Modulo MIC completo (preamp + EQ2 al detent + driver)

`mic-module-noise.cir`, 150 Ω: **−97,3 / −90,0 / −69,3 dBu A-wtd** a
0 / 50 / 100% del gain (29,5 / 38,3 / 59,3 dB). A guadagno basso pesa
l'EQ2 (cella HIGH, trio 49,9k), sopra ~38 dB domina il microfono.

## 3. Modulo MONO completo

| Test | Netlist | Risultato |
|---|---|---|
| Guadagno pot a 0 dB / max | `gen-ac.cir` | −0,08 / +9,93 dB |
| Banda | idem | 5 Hz −0,50 dB · 10 Hz −0,19 dB · 35 kHz −0,08 dB (sorgente 1 kΩ) |
| Rumore uscita, pot chiuso / 0 dB / +10 | `gen-module-noise.cir` | −101,8 / −101,3 / −101,1 dBu A-wtd |

EQ2 simulata coi valori del send (HIGH 4,5 kHz); il modulo adotta 5 kHz
(valori del canale): da rifare nella suite completa.

## 4. QUIRK 3 LTspice 26.0.2 — la en degli op-amp spariva dal `.noise`

Sintomo: il preamp dava EIN −128,9 dBu, sotto il conto a mano. Test
minimo (OP1612 non invertente G = 31,8, Rg noiseless, Rf 499):

| Macro | V(onoise) a 1 kHz |
|---|---|
| libreria com'era (`E1 … value={A*(V(inx)-V(inn))}`) | 5,0 nV/√Hz |
| E1 lineare a 4 nodi (`E1 xx 0 inx inn A`) | 35,3 nV/√Hz = 1,1 nV × 31,8 ✓ |

Fix applicato alla libreria il 2026-10-13 (funzione di trasferimento
identica). Impatto stimato sugli altri netlist di rumore: docs/02 voce 73.

## 5. Mandata: rumore portato su un bus FX (`send-bus-noise.cir`)

Modulo MONO → pot SEND passivo → buffer di iniezione → R 10k → summing
del bus (Rf 10k). Uscita del bus, A-wtd:

| Pot SEND | Rumore sul bus |
|---|---|
| chiuso | −111,2 dBu (18,9 nV/√Hz) |
| metà | −105,6 dBu |
| aperto | −100,8 dBu |

Senza switch il buffer resta sempre sul bus. Con 4 moduli a pot chiusi:
bus da −100,8 (dec. 89) a circa −99,5 dBu A-wtd (target −88: PASS).

## 6. Non simulato (prossimo passo)

THD e clip reali, clamp d'ingresso, EQ2 a 5 kHz, detector del LED,
mute globale delle mandate.

Storia della giornata: scheda unica, manopola SEND unica + bottoni e
bottone MIC ON della prima stesura sono stati rimossi (dec. 97). Il
passa-alto a 60 Hz, tolto e poi ratificato da Filippo, è nel circuito:
EIN, guadagni e CMRR identici nelle due versioni.
