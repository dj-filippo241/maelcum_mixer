# CANALE CDJ/LINE: note della bozza v0.1 (todo 167, 2026-11-04)

Schema da `canale.py` (generatore `pcb/tools/pcbgen.py`, celle in `pcb/tools/celle_vca.py`).
Esito: **SCHEMA PASSA** (ERC 0 errori; 2 avvisi VSS dell'ADG, come il FX-SEND). PCB: vedi in fondo.

## Conteggio vero

380 impronte (358 SMD, 22 a foro passante), 30 chip, 56 condensatori da 100n, 4 trimmer
(2 di simmetria, 1 di law, 1 d'offset), 8 regolatori.

| Blocco | Chip |
|---|---|
| Ingresso e GAIN T1 | OPA1612 ×2 |
| Isolator incroci C: 20 sezioni per lato | OPA1654 ×10 |
| Somma dell'isolator, servo | OPA1612, OPA1642 |
| Buffer CUE e SEND TAP, meter | OPA1612 ×2, OPA1654 |
| Fader: 2 VCA, I/V, shaper, dip | V2181 ×2, OPA1612 ×3 |
| Levetta e CUE | 74HC14, 74HC86, 74HC74, ADG1434 ×2 |
| Alimentazione | LM317/337, 78L15/79L15, LT3045/3094, LM4040, OPA1612 |

La stima del PIANO (~362) era vicina. Ma una 100 × 220 porta ~280 impronte coi due lati:
**il canale non sta su una scheda.** L'isolator da solo vale ~190 impronte (C di precisione
in 1206/1210, 27 per lato).

## Proposta di divisione (da confermare: cambia il telaio, dec. 144)

1. **CANALE segnale** (col C96): ingresso, GAIN, somma dell'isolator, prese, fader, dip,
   levetta, alimentazione. ~190 impronte.
2. **CANALE isolator**: la banca dei due lati (10 quad) e i buffer dei pot. ~190 impronte.
   Riceve GO_L/R, rende i 4 rami per lato (o la somma). Cavo corto fra le due.

## Scelte segnate NOTA (non scritte nei documenti)

1. **R della banca**: E192 0,1 % più vicine ai valori calcolati di RISULTATI-incroci-C §1
   (scarto ≤ 1 %: 4,82k → 4,81k, 3,22k → 3,20k, 6,43k → 6,42k, 6,84k → 6,81k, 2,38k → 2,37k,
   5,07k → 5,05k; 5k dell'allpass → 4,99k). Le C 200n, 94n, 20n, 9n4, 21n15 sono un pezzo
   solo nello schema: coppie in parallelo da fissare col layout (RISULTATI §1).
   **Da risimulare** con questi valori prima del prototipo.
2. **Dip (dec. 163)**: la logica è descritta, non disegnata, in RISULTATI-filtsel-dip.
   Circuito scelto: antirimbalzo 10k/100n + 74HC14; 74HC86 confronta levetta e stato; OR a
   diodi = DIFF; ritardo 33k/47n + due Schmitt = clock dei 74HC74 a ~1,5 ms; DJSEL =
   NOT(Q0 xor Q1). Dip: DIFF → due RC 10k/50n bufferizzati → 3,01k su ogni EC−.
   Al pin 0,73 V (serve ≥ 0,61). Le R verso massa dei partitori del fader passano da 1k a
   1,5k: 1,5k // 3,01k = 1,00k, così la law del fader resta quella simulata.
   **Da simulare** (filtsel-dip.cir con la logica vera) e da provare al banco.
3. **CUE**: tasto a ritenuta verso +5VF (come gli assign del FX-SEND), switch sulla quarta
   sezione dell'ADG di ogni lato, 47 Ω verso lo slot 2. Il documento dice solo «switch CUE
   di canale».
4. **Bit di modo** (FILT_MODE, riga c): il canale li scrive su c1-c2 con 1k; il backplane li
   porta al pin giusto per posizione.
5. **Meter**: una barra per canale, (L+R)/2 come il FX-RET. cdj §3.7 diceva «per lato»
   [PROVVISORIO]; il metering conta 4 barre DJ. LM3915 sulla scheda comandi.
6. **TVS** da scegliere; polo RC > 100 kHz all'ingresso non disegnato (la C del TVS lo fa).
7. **Ingressi RCA su un cavo (J3)** verso la schedina dei connettori (dec. 141).
8. Il front-end **PHONO** (Rev B, phono-stage.md) non è su questa scheda.
9. Cap-moltiplicatore ±18 a ~50 mA come il FX-SEND: da riscalare (~28 op-amp e 2 VCA).

## Da fare

- Divisione in due schede, poi PCB.
- Cavo J2 (36 fili) e scheda comandi: GAIN doppio, 4 pot doppi B dell'isolator, fader,
  levetta, tasto CUE, LM3915.
