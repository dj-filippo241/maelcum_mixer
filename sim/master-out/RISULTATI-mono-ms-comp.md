# RISULTATI — matrice MONO del master coi componenti (todo 200, 2026-11-03)

Netlist: `mono-ms-comp-ac.cir` (separazione, Monte Carlo) e
`mono-ms-comp-noise.cir` (rumore). Circuito: `pcb/master/master-segnale.py`,
blocco «MONO [A3]» (NOTE.md punto 4). `mono-ms.cir` (blocchi ideali, click
del tasto) resta valido per la rampa.

## 1. Polarità del VCA: le uscite erano scambiate

Datasheet THAT 2181 Series, Document 600030 Rev 03 (thatcorp.com, letto il
2026-11-03), p. 7: «The signal path through the VCA and the output opamp is
non-inverting». Con 20k nel pin IN e I/V 20k: Sv = +S.

Il generatore presumeva Sv = −S. Con Sv = +S:

- uscita del sommatore U3B: −(M + Sv) = **R**, non L;
- uscita del differenziale U4A: Sv − M = **L**, non R.

A tasto spento il master usciva con L e R scambiati. Simulazione in
continua: 1 V su SUM_L → 0,99999 V su «LO_R», 0,08 µV su «LO_L».

**Correzione** (generatore, 2026-11-03): U3B esce su LO_R, U4A su LO_L.
Costo zero. Polarità assoluta invariata: la catena [A2]+[A3] resta
invertente, come [A2] da solo. Schema: SCHEMA PASSA.

## 2. Separazione L/R a tasto spento

Monte Carlo, 20 giri, resistenze 0,1 % uniformi. Errore di guadagno del
VCA a EC 0 V dal datasheet p. 4: ±0,1 dB (2181A), ±0,15 (B), ±0,2 (C).
Il clone V2181L non ha un dato pubblico letto qui: si assume classe C.

| Errore VCA | C sul 10k di M | 1 kHz | 10 kHz | 20 kHz |
|---|---|---|---|---|
| 0 dB | nessuno (scheda di prima) | −54…−57 dB | −37 dB | −31 dB |
| 0 dB | 44 pF | −52…−89 dB | −52…−86 dB | −52…−82 dB |
| +0,1 dB | 44 pF | −42…−47 dB | uguale | uguale |
| −0,2 dB | 44 pF | −38…−40 dB | uguale | uguale |

Lettura:
- Il 22 pF dell'I/V del VCA mette un polo a 362 kHz sul solo ramo S: a
  20 kHz la separazione scende a −31 dB. Un condensatore uguale sul ramo M
  (44 pF sul 10k; in scheda 47 pF, E12: −54 dB a 20 kHz) rende la
  separazione piatta. Aggiunto al generatore.
- Il limite vero è l'errore di guadagno del VCA: **−38 dB nel caso
  peggiore** (classe C, −0,2 dB), −45 dB in classe A. Il design doc
  diceva ~60 dB: valeva solo per le resistenze.
- −38 dB di separazione stanno sopra il vinile (25-30 dB tipici). Un
  trimmer sull'EC− (±1,2 mV = ±0,2 dB) riporterebbe a −52 dB: non
  aggiunto, perché non serve all'ascolto. [PROVVISORIO]

## 3. Livelli in MONO

Invariati rispetto a `mono-ms.cir` (la matrice è lineare e la prova in
continua conferma i coefficienti): sorgente su un lato −6 dB su entrambe
le uscite, al centro invariata.

## 4. Rumore

Valori nominali, C 44 pF, VCA col floor del datasheet p. 8 (−98 dBV
20 Hz-20 kHz con I/V 20k = 88,9 nV/√Hz, iniettato con G lineare; il floor
del datasheet comprende già le resistenze del circuito di prova: stima
prudente). Ingressi terminati.

| Uscita | Densità a 1 kHz | Totale | A-wtd |
|---|---|---|---|
| L (differenziale U4A) | 103,5 nV/√Hz | −94,5 dBu | **−96,4 dBu A** |
| R (sommatore U3B) | 102,0 nV/√Hz | −94,6 dBu | **−96,6 dBu A** |

Domina il VCA (~89 di 103 nV). Sul sistema a filtri OFF (−82,9, docs/06
§14): −82,9 ⊕ −96,4 = −82,7 dBu A, **+0,2 dB**, come la stima del design
doc (master-out, addendum dec. 111).

## 5. Headroom

Tutti i nodi della matrice stanno entro max(|L|, |R|): S = (L−R)/2 vale al
massimo un ingresso intero (L = −R). Nessun limite nuovo oltre quello del
dominio ±15 V del sommatore (+19 dBu, master-out §3). Corrente nel VCA a
+19 dBu: 0,73 mA in ingresso + 0,73 in uscita = 1,46 mA, sotto i 2,5 mA
di «Signal Current» del datasheet (ISET 2,4 mA).
