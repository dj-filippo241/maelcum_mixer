# RISULTATI — conseguenze della decisione 111 (todo 47, 48, 49)

Data: 2026-10-14. Netlist e script:

| todo | netlist / script | cosa misura |
|---|---|---|
| 49 | `sim/shaper/shaper-{reroute,drive,position,filtro-freq}-hot.cir` + `sim/shaper/shaper_hot_tab.py` | shaper a 50 / 65 / 75 °C interni contro la taratura a 35 °C |
| 49 | `sim/filtro/ota-selftest-ac-temp.cir` | gm dell'LM13700 reale a Iabc fissa, 25 / 45 / 65 °C |
| 47 | `sim/system/psu-w1-opt.cir` | avvolgimento audio W1 col carico dei moduli opzionali (~1,7 A per ramo) |
| 48 | `sim/master-out/mono-ms.cir` | tasto MONO: matrice M/S + VCA sulla larghezza, rampa 1 ms |

## 1. Shaper a caldo (deriva rispetto alla taratura a 35 °C)

| Shaper | zona | 50 °C | 65 °C | 75 °C |
|---|---|---|---|---|
| Reroute FX | 0 … −15 dB (zona del feedback) | ≤ 0,14 dB | ≤ 0,28 dB | ≤ 0,36 dB |
| Reroute FX | −20 / −30 dB | −0,35 / −0,58 dB | −0,76 / −1,15 | −1,05 / −1,54 |
| Reroute FX | sotto −40 dB (ritorno quasi chiuso) | −1,7 … −3,7 | −3,8 … −7,5 | −5,4 … −10 |
| Drive 5-way | tutta la corsa | ≤ 0,06 dB | ≤ 0,12 dB | ≤ 0,15 dB |
| Position 5-way | tutta la corsa | ≤ +1,7 % | ≤ +3,3 % | ≤ +4,5 % |
| Frequenza filtro | 10 … 90 % della corsa | ≤ 0,8 % | ≤ 2,2 % | ≤ 3,5 % |
| Frequenza filtro | estremi (0-5 %, 95-100 %) | −4,4 / +3,9 % | −8,7 / +8,1 % | −11,5 / +11,0 % |

Lettura: gli shaper reggono un interno a 65 °C. Nella zona che si suona la
deriva resta sotto 0,3 dB e sotto il 3 %. Agli estremi del filtro la
deriva arriva a ±8 % a 65 °C, dentro la tolleranza ±5-10 % della dec. 74.

## 2. OTA LM13700 reale: gm a Iabc fissa

| Die | gm / Iabc | contro 25 °C |
|---|---|---|
| 25 °C | −34,14 dB | — |
| 45 °C | −34,70 dB | −6,3 % |
| 65 °C | −35,23 dB | −11,8 % |

(stesso valore a 7,56 µA e a 100 µA: la dipendenza è gm = Iabc / 2V_T,
V_T ∝ T assoluta). **Finding**: il converter del filtro compensa la sua
coppia (ΔV scalato PTAT), ma la corrente di riferimento Iref = 400 µA è
fissa; quindi la frequenza di taglio di tutti i core scende con il caldo
come 1/T: −9 % da 35 a 65 °C, cioè ~1,6 semitoni. La simulazione di
fattibilità (`feas-svf.cir`) non lo vedeva: usava un OTA con gm = 19,2·Iabc
senza temperatura. Rimedio: Iref proporzionale alla temperatura assoluta
(Iref = V_PTAT / R, dallo stesso generatore PTAT che scala ΔV). Annotato in
filter-module §4.

## 3. Avvolgimento audio W1 coi moduli opzionali (2×21 V, reg. 7 %)

| Caso | Avvolgimento | Rete | Carico DC per ramo | I efficace avv. | Raw min | Esito |
|---|---|---|---|---|---|---|
| 1 | 3,0 A (attuale, dec. 106) | −10 % | 1,7 A | 3,19 A (106 %) | 23,2 V | **sovraccarico** |
| 2 | **3,5 A** | −10 % | 1,7 A | 3,26 A (**93 %**) | **23,5 V** | PASS (≥ 21,7 V) |
| 3 | 4,0 A | −10 % | 1,7 A | 3,33 A (83 %) | 23,8 V | PASS |
| 4 | 3,5 A | +10 % | 1,0 A | 2,17 A | max 31,8 V | tensione massima |
| 5 | 4,0 A | +10 % | 1,0 A | 2,21 A | max 32,0 V | tensione massima |

Scelta [PROVVISORIO]: **W1 2×21 V 3,5 A**, trasformatore **~250 VA**.

**REV 2026-10-21 (todo 114, `psu-w1-vca.cir`, bulk 15 mF)**: il modulo FX ha
40 VCA, non 20 → caso peggiore 1,81 A per ramo.

| Caso | Avvolgimento | Rete | Carico DC | I efficace avv. | Raw min |
|---|---|---|---|---|---|
| 1 | 3,5 A | −10 % | 1,81 A | 3,44 A (98 %) | 23,6 V |
| 2 | 3,5 A | nominale | 1,81 A | 3,50 A (100 %) | 26,6 V |
| 3 | 4,0 A | −10 % | 1,81 A | 3,51 A (88 %) | 23,9 V |
| 4 | 3,5 A | −10 % | 1,70 A (riferimento) | 3,27 A (93 %) | 23,8 V |

## 4. Tasto MONO (matrice M/S + VCA sulla larghezza)

Caso peggiore: +18 dBu (6,16 Vp) tutto sul canale sinistro, commutazione
al picco. Sonda HP 2 poli ~1,6 kHz; baseline del programma 1,23 V.

| Rampa | Picco sonda | Sopra il programma |
|---|---|---|
| secco (1 µs) | 3,41 V | +8,9 dB (click) |
| 0,3 ms | 1,81 V | +3,3 dB |
| **1 ms** | **1,31 V** | **+0,55 dB** (nessun click) |

- Normale (w = 0 dB): L' = 6,160 Vp, R' = 0,15 mV (separazione −92 dB,
  limitata nel modello dal polo del VCA; nel circuito la limita
  l'appaiamento delle R della matrice: ~60 dB con R 0,1 %).
- MONO: L' = R' = 3,080 Vp. Una sorgente tutta su un lato scende di 6 dB
  su entrambe le uscite; una sorgente al centro resta identica; due lati
  scorrelati scendono di 3 dB.
- Costo: 1 VCA THAT 218x (o V2181L) + 4 op-amp per il modulo master. Il
  VCA sta sempre nel percorso a 0 dB: aggiunge ~−96 dBu non pesati al
  master, cioè ~+0,2 dB sul sistema (−82,9 → ~−82,7 dBu A-wtd) [STIMA dal
  datasheet: −98 dBV a 0 dB].
