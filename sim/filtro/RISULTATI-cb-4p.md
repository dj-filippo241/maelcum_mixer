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
con l'overdrive chiuso (PASS 2,4 sul −78), −79,5 con DRIVE a metà,
−75,6 a fondo (stima: core + guadagno dell'overdrive). Col core (a′) k 1/30: −77,0 / −75,6 / −70,6.

## Variante C: curva di rumore del datasheet e headroom (2026-10-21, pomeriggio)

Letti dal datasheet THAT 2181 (Doc. 600030 Rev 03):

- **Figure 4, rumore contro guadagno** (20 kHz NBW, I/V 20k): piatto a
  ~−110 dBV sotto −30 dB, −98 dBV a 0 dB, ~−75 dBV a +30 dB. Il floor
  «piatto a −98/−104» delle righe sopra era 12 dB pessimista proprio in
  attenuazione. Modello (`cb-4p-noise-c.cir`, I/V 10k): g ≤ 1 →
  √(floor² + (a·g)²) col floor 12 dB sotto lo 0 dB; g > 1 → g^(2/3).
- **Recommended Operating Conditions**: Iin + Iout ≤ 2,5 mA (Iset 2,4 mA).

| f1 (VCA a 0 dB) | fc 37 kHz | 10 kHz | 1 kHz | 100 Hz | peggiore | guadagno max del VCA |
|---|---|---|---|---|---|---|
| 6 kHz | −91,9 | −94,3 | −97,2 | −100,5 | −91,9 | +15,8 dB |
| **12 kHz** | −93,9 | −93,6 | −92,1 | −95,1 | **−92,1** | +9,8 dB |
| 20 kHz | −94,3 | −92,8 | −87,9 | −90,8 | −87,9 | +5,3 dB |
| 37 kHz | −93,7 | −90,2 | −82,6 | −85,6 | −82,6 | 0 dB |

Headroom (`cb-4p-headroom.cir`): tono a +18 dBu (6,16 Vp) a f = fc e
fc/2, RES al minimo, corrente Iin + Iout del VCA più carico:

| f1 | fc 20 kHz, f = fc | fc 37 kHz, f = fc | fc/2 (peggiore) |
|---|---|---|---|
| 12 kHz | 1,18 mA | 1,84 mA | 1,26 mA |
| 20 kHz | 0,89 mA | 1,29 mA | 0,88 mA |

Tutti sotto 2,5 mA. Il caso a 1,84 mA è un tono a +18 dBu a 37 kHz,
fuori dalla banda audio.

**Scelta di ingegneria: f1 = 12 kHz** (Cint = 1/(2π·12 kHz·10k) ≈ 1,33 nF,
VCA da −42 dB a fc 100 Hz… a +9,8 dB a fc 37 kHz) [PROVVISORIO].

**Sistema** (−82,9 ⊕ 4 canali filtro): **−81,2** con l'overdrive chiuso
(PASS 3,2 sul −78), −80,5 con DRIVE a metà, −77,3 a fondo (stima: core +
guadagno dell'overdrive). Core (a′) k 1/30: −77,0 / −75,6 / −70,6.

## Lettura

- Col floor del datasheet e f1 = 12 kHz il PULITO a 4 poli fa −92,1 dBu
  A-wtd nel caso peggiore, 7,8 dB sotto il core (a′). Il sistema con 4
  filtri passa con 3,2 dB di margine. Il FAIL di A18 riguarda solo il
  core (a′).
- La posizione del VCA conta più di tutto: in attenuazione il suo floor
  resta e il loop lo ricompensa; in guadagno il rumore cresce meno del
  guadagno, ma serve corrente. 12 kHz bilancia le due cose.
- La tabella del mattino (righe con f1 3k/6k/12k e floor piatto) è
  SUPERATA dalla variante C.

## Non fatto

- RES alta nel (c-B): gli stati crescono di Q volte e servono un
  limitatore e un VCA (o OTA) della RES progettati per questo core.
  Risonanza, auto-oscillazione e overdrive del (c-B) col chip: nel
  modello il VCA è un moltiplicatore ideale (niente THD vs corrente).
- Rumore in modo HPF.
- Verifica a banco della curva di Figure 4 sul clone V2181L (il datasheet
  è del THAT originale).
