# RISULTATI — rumore del core PULITO (c-B) a 4 poli

Data: 2026-10-21. Todo 116, voce A18 di `docs/02`. Scopo: confrontare B1
alla pari col core (a′) di `RISULTATI-D5.md` §6.3 (−84,3 dBu A-wtd per
core a 4 poli, sistema −77,0 con 4 filtri inseriti, FAIL 1,0 sul −78).

## Circuito

Cella (c-B) di `sim/five-way/cell-vca-ac.cir` (law esatta, Q invariante,
`sim/five-way/RISULTATI-cell-clean.md` §1): summer, due integratori op-amp
ognuno preceduto da un THAT 218x, buffer di stato. Due sezioni Butterworth
(Q 0,541 + Q 1,307, RES al minimo), smorzamento con resistenza dal ramo
−bp_b (invertitore op-amp reale). Overdrive v0.2b a valle
(`od2-noise-b.cir`). Uscita LP. Op-amp: OP1654 della libreria condivisa.

**Rumore del VCA.** Il modello `that2181.inc` non ne ha. Dal datasheet
THAT 2181 (output noise, 20 Hz-20 kHz):

- −98 dBV a 0 dB con I/V da 20k; con 10k −104 dBV (44,6 nV/√Hz);
- +15 dB di guadagno: −88 dBV, cioè +10 dB d'uscita ogni +15 dB.

Iniettato come corrente nel nodo dell'integratore: 44,6 nV/√Hz /10k ×
max(1, g^(2/3)). In attenuazione tenuto piatto (prudente: la curva di
Figure 4 del datasheet sotto 0 dB non è letta; il floor reale può
scendere).

**Posizione del guadagno.** f0 = g·f1, con f1 = frequenza a cui il VCA sta
a 0 dB (Cint = 1/(2π·f1·10k)). Il VCA in attenuazione ha il floor
costante e il loop lo ricompensa (rumore ∝ 1/g); in guadagno il rumore
cresce meno di g. Va scelto f1.

## Risultati

| netlist | f1 | fc 37 kHz | 10 kHz | 1 kHz | 100 Hz | peggiore |
|---|---|---|---|---|---|---|
| `cb-4p-noise.cir` (floor −98 dBV, piatto) | 37 kHz | −89,2 | — | −68,7 | — | −68,7 |
| `cb-4p-noise-b.cir` | 37 kHz | −93,7 | — | −74,4 | — | −74,4 |
| `cb-4p-noise-b.cir` | 1 kHz | −82,7 | — | −100,6 | — | −82,7 |
| `cb-4p-noise-b2.cir` | 3 kHz | −88,7 | −93,7 | −95,2 | −97,5 | −88,7 |
| `cb-4p-noise-b2.cir` | **6 kHz** | −91,9 | −94,3 | −89,9 | −92,6 | **−89,9** |
| `cb-4p-noise-b2.cir` | 12 kHz | −93,9 | −92,5 | −84,1 | −87,0 | −84,1 |

dBu A-wtd, overdrive chiuso. Con f1 ~5-6 kHz il caso peggiore è
**−89,9**, 5,6 dB sotto il core (a′) (−84,3). Il VCA della RES, se
aggiunto, pesa +0,6 dB col floor −98 (`cb-4p-noise.cir`, resn = 1).

**Sistema** (−82,9 a filtri OFF ⊕ 4 canali filtro, f1 6 kHz): **−80,4**
con l'overdrive chiuso (PASS 2,4 sul −78), −79,8 con DRIVE a metà,
−77,1 a fondo. Col core (a′) k 1/30: −77,0 / −75,6 / −70,6.

## Lettura

- Col floor del datasheet e f1 ben scelto, il PULITO rientra nel target
  con margine. Il FAIL di A18 riguarda solo il core (a′).
- Il numero dipende dal floor del VCA in attenuazione (letto piatto) e
  dalla curva in guadagno (estrapolata oltre +15 dB). Verifica a banco.

## Non fatto

- **Headroom del VCA in guadagno.** Con f1 6 kHz il VCA arriva a +16 dB
  (fc 37 kHz): la corrente d'uscita del 218x va controllata contro il
  programma a +18 dBu. Può chiedere una resistenza d'ingresso più alta,
  che sposta il rumore. Da fare prima di fissare f1.
- Risonanza, auto-oscillazione e overdrive del (c-B) col chip: nel
  modello il VCA è un moltiplicatore ideale.
- Rumore in modo HPF.
