# CANALE CDJ/LINE: note della bozza v0.1 (todo 167, 2026-11-04)

## Stato al 2026-11-11 (todo 272, dec. 173): scheda sola a trapezio, PASSA

`canale.py` è riscritto su una scheda sola: 287 mm da dietro a davanti, alta 162 → 129 mm,
382 impronte, 242 reti, isolator dentro (banca.py), niente ponte. Filippo tiene i 287 mm (tetto 70 %,
dec. 156; opzione 1 del 9/11). La versione su due schede sta in `archivio/` (segnale e isolator,
rigenerabili). I file KiCad di questa cartella sono ora quelli della scheda sola.

Esito del giro 10 (2026-11-11): **PASSA** al primo dei 4 tentativi. DRC 0 errori; avvisi 52
silk_overlap, 63 silk_over_copper, 4 via_dangling, 58 attesi. ERC 2 avvisi VSS dell'ADG. Controllo
audio A1/A2/A3/A4/A5 = 32 / 35 / 4 / 6 / 2 (A1: C dei regolatori lontani, come le altre schede).
Un PASSA singolo non è una prova: per questo `canale.py` usa `pcbgen.DesignRiprova` (sotto).

Giro 11 (2026-11-11, todo 289: DIFF ripreso, ritardo 68k + diodo, punto 2 sotto): **PASSA** al
secondo tentativo (giro 1: 2 clearance). 383 impronte, 244 reti. DRC 0 errori; avvisi 52
silk_overlap, 61 silk_over_copper, 4 via_dangling. Audio A4 6 → 8 (BUS_LPF_L/R e DJBUS_L vicine a
CTRL_GND e Q1 a 0,35-0,49 mm, ~0,07 pF; K1W_L vicina a BTNC): Freerouting cambia le piste a ogni
giro. Da guardare nel layout vero, non bloccante.

Giri del 9/11:
1-3. Contorno in diagonale passato a Freerouting: fanout 13 volte più lento, un giro non finisce in un'ora,
   uno si arena a 260 aperti. Più un errore mio: foro H2 sopra il cavo J2 (spostato a x 95).
4. Contorno rettangolare per Freerouting e triangolo tagliato a gradini (pcbgen.py): finisce in ~10 min,
   **35 aperti**: CTRL_GND 18, RAW±22 e RAW±27 2 ciascuna, +5V 2, ECF_R 2.

Giri del 10/11:
5. `d.link_pairs = True` (come il MIC): chiusi RAW±22, RAW±27, +5V ed ECF_R. Restano **19 aperti, tutti
   CTRL_GND**: Freerouting non traccia quasi niente di quella rete, nemmeno fra due condensatori vicini.
6. CTRL_GND a 0,25 mm: 15 aperti. 7. A 0,4 mm (come il master, dove passa): 18 aperti. La larghezza non è
   la causa. Nel master e nel MIC la stessa rete passa. Da guardare: i pin vicini dello stesso chip sulla
   rete (U24 pin 12-13, ingressi liberi del 74HC86; U23 pin 13 del 74HC14) e `link_pairs`, che salta le
   reti di massa (`masse`); oppure una colata CTRL_GND attorno alla logica.

Giri dell'11/11:
8. `d.link_pairs_masse = True` (pcbgen, todo 272): lega anche i pin gemelli di CTRL_GND (a23-a24) e
   CHASSIS (a25-a26) del C96. Un gemello aperto faceva disfare a Freerouting 2.5 tutta la rete.
   CTRL_GND chiusa: resta **1 aperto, SKAB2_R** (pista di 0,29 mm staccata dal pad di C88).
9. Stesso file, giro nuovo: Freerouting chiude tutto, ma il DRC trova SN2_F aperta (R142) e una
   distanza di 0,247 mm su 0,25 (via -15LN, pista +18V). Ogni giro sbaglia in un punto diverso.
10. La ripetizione del MIC (fino a 4 tentativi, scheda ricostruita e passate -mp diverse) passa nel
   generatore come `DesignRiprova`; `canale.py` e `mic.py` la usano. **PASSA** al primo tentativo.

Prima (9/11) restava da provare: CTRL_GND più larga o in colata vicino alla logica (oggi 0,3 mm per i pin TSSOP, lunga dalla
logica al C96); blocco ALIMENTAZIONE più vicino ai pin RAW del C96 (`d.power_first`); più giri (non deterministico).


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

## Divisione in due schede (SUPERATA dalla dec. 173, 2026-11-09)

Filippo sceglie una scheda sola, lunga ~287 mm (piano F). La divisione sotto resta come prova
finché `canale.py` non è rigenerato su una scheda col trapezio della dec. 158.


Fatta come scelta di ingegneria: pannello, comandi e backplane non cambiano (dec. 142, 144).
Resta PROVVISORIA fino alla scelta di Filippo (todo 249, `pcb/PROPOSTA-todo170.md` P4).
Ipotesi più neutra:

- **Un C96 solo**, sulla scheda segnale (`canale.py`, 193 impronte: prese, meter e fader sul retro).
- **Scheda isolator** (`canale-isolator.py`, cartella `isolator/`, 197 impronte, tutto davanti):
  le due banche, la somma x10 e il servo (U3-U14, funzioni in `banca.py`, valori invariati).
- **Ponte**: cavo piatto 2x18 (`banca.PONTE`, J4 segnale - J1 isolator): ±18, GO_L/R, EQ_L/R
  e le 16 reti dei pot B (uscite di banda e cursori), con masse fra i gruppi.
- **Cavo dei pot J2 invariato**: le 16 reti dei pot fanno ponte + J2. Alternativa da valutare
  col primo prototipo: un cavo diretto isolator - scheda comandi (cursori più corti).
- Scheda isolator senza C96: 4 fori M3 senza rete (distanziali isolati), NOTA. Bulk 2x 47u.
- Circuito identico (distinte sommate = prima + ponte e bulk, controllato). Polarità invariata.
- Correzioni trovate col piazzamento: J3 (RCA) sul foro H2, spostato a y 12; la logica 74HC
  passa a TSSOP-14 (stesso pinout): in SOIC-14 il 100n del pin 14 cadeva sul corpo del chip.
  CTRL_GND a 0,3 mm (pin TSSOP).

Divisione di partenza (proposta originale):

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
   NOT(Q0 xor Q1). Dip: DIFF → due RC 10k/50n bufferizzati → 4,99k nel nodo di somma dello
   shaper del fader (REV 2026-11-10, todo 281: prima 3,01k su ogni EC−, 1,38 V al pin col
   fader chiuso, oltre il ±1 V del 2181). Il dip satura lo stadio del partitore: 0,70-0,80 V
   al pin (serve ≥ 0,61). `sim/system/RISULTATI-ec-pin.md`.
   **REV 2026-11-11 (todo 289)**: simulato con la logica vera (RISULTATI-filtsel-dip §5).
   DIFF ripreso da 74HC14 sez. 6 + 74HC86 sez. 4 (DIFFB): RC del dip e ritardo partono da
   DIFFB. Ritardo 68k/47n + diodo DLY → DIFFB. Prima: rilascio di ~40 ms e canale muto se la
   levetta tornava indietro col CLK alto. Da provare al banco.
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
- ~~Cavo J2 (36 fili) e scheda comandi~~: scheda comandi fatta il 2026-11-11 (sezione in fondo).

## Esito della PCB (2026-11-04)

Divise in due schede (sopra), ±18 a 0,4 mm (a 0,6 Freerouting lasciava -18V aperta, come il MIC).

| Scheda | Impronte | Esito | DRC | Controllo audio A1/A2/A3/A4/A5 |
|---|---|---|---|---|
| `canale.py` (segnale, col C96) | 193 | **PASSA** al 1o giro | 0 errori; 15 silk_overlap, 11 silk_over_copper, 58 attesi | 29 / 37 / 6 / 2 / 0 |
| `canale-isolator.py` | 197 | **PASSA** al 2o giro (1o: SKAH2_R aperta) | 0 errori; 29 silk_overlap, 44 silk_over_copper | 0 / 27 / 11 / 0 / 0 |

Un PASSA singolo non è una prova (Freerouting cambia a ogni giro). A2 alto: le reti dei pot e
del ponte fanno strada lunga (cavo). Polo RC d'ingresso, TVS e C in parallelo della banca
restano come le NOTE sopra.

## Scheda comandi (todo 270, 2026-11-11)

`canale-comandi.py`, file in `comandi/`, celle in `pcb/tools/comandi.py`. 48 × 262,4 mm, parallela
al pannello (50 × 266,4), retta dai dadi dei pot. Posizioni da `coordinate.json`, modulo «canale».

- Pezzi: GAIN pot doppio 10k lin selezionato (AGND - GW - BUF, dec. 162); HIGH, MID-HIGH,
  LOW-MID, LOW pot doppi lineari B 10k (AGND - KnW - banda: antiorario = kill, dec. 168);
  levetta FILTRO (comune CTRL_GND, HPF = FSW0, LPF = FSW1); levetta LINE/PHONO senza reti;
  bottoni FX1-4 e CUE con luce; barra da 10 LED con un LM3915 (RHI = +REF5, +24...-3 dBu);
  fader PTA6043 (+REF5 in cima, POT_F, AGND).
- Cavi: J2 2×18 verso J2 di `canale.py` (ordine letto dal file); J3 1×6 verso J3 di `fx-send.py`
  (+5VF, BTN1-4, CTRL_GND).
- **PASSA** al 1o giro, e di nuovo al 2o e al 3o (2026-11-11): 34 componenti, 56 reti, 0 aperti,
  ERC pulito, DRC 0 errori. A1: resta il pin 9 (MODE) dell'LM3915 a ~16 mm dal 100n.

NOTA della scheda comandi (da verificare):

1. **Bottoni FX con reti proprie** (+5VF_FXS, GND_FXS): il +5VF del canale e quello del FX-SEND
   non si toccano, e i due cavi non chiudono un anello di masse sulla scheda comandi.
2. **RHI del meter = +REF5 dei pot**: il partitore interno dell'LM3915 carica il riferimento dei
   pot e del fader. Il master usa un follower dedicato (VREFA). Da misurare a banco; se serve, un
   follower sulla scheda di segnale e un filo in più sul cavo.
3. **LINE/PHONO**: la levetta si monta ma non ha fili; arrivano col front-end PHONO di Rev B.
4. Levette e bottoni: impronte segnaposto (NKK G1xJP, GW12LJP), pinout da rifare col pezzo scelto.
   Verso della levetta FILTRO (HPF in alto) dal render: da verificare sul pezzo.
5. Pot di classe 14 mm dell'isolator su impronta RK09L (KiCad non ha l'RK14): ingombro da 14 mm
   tenuto nel controllo del piazzamento, come FX-SEND e MIC.
