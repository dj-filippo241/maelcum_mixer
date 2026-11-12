# FX-RET: note della bozza v0.1 (todo 167, 2026-11-04)

Schema da `fx-ret.py` (generatore `pcb/tools/pcbgen.py`, celle in `pcb/tools/celle_vca.py`).
Esito: **SCHEMA PASSA** (ERC 0 errori). PCB: vedi «Esito della PCB» in fondo.

## Conteggio vero

410 impronte (372 SMD, 38 a foro passante), 34 chip, 64 condensatori da 100n,
20 trimmer 3266 (10 di simmetria, 5 di law, 5 d'offset di coppia), 6 regolatori.

| Blocco | Cosa | Chip |
|---|---|---|
| Somma del bus + driver del pedale | OPA1612 ×2 | 2 |
| Ritorno: buffer JFET, servo, GAIN T2 | OPA1642 + OPA1612 ×3 | 4 |
| EQ2 L/R | OPA1654 ×2 | 2 |
| Meter (detector) | OPA1654 | 1 |
| 4 reroute: 8 VCA, 4 I/V, 4 shaper | V2181 ×8, OPA1612 ×8 | 16 |
| Driver d'iniezione (F3) | OPA1654 ×2 | 2 |
| Fader: 2 VCA, I/V, shaper | V2181 ×2, OPA1612 ×2 | 4 |
| Alimentazione e riferimenti | LM317/337, LT3045/3094, LM4040, OPA1612 | 6 + 1 |

La stima del PIANO (~300 impronte) era bassa del 37 %: i 5 shaper (15 pezzi l'uno), i 20
trimmer e i 10 VCA col loro trim (7 pezzi l'uno) pesano più di «12 per chip». Una 100 × 220
porta ~280 impronte coi due lati: **il FX-RET non sta su una scheda.**

## Divisione in due schede (CONFERMATA dalla dec. 173, 2026-11-09)

Sotto la striscia non c'è posto per una scheda sola: il reroute sta sotto il 5-way (piano F).


Fatta come scelta di ingegneria: pannello, comandi e backplane non cambiano (dec. 142: più
schede affiancate sotto un pannello; dec. 144: cambia la scheda, non il circuito). Resta
PROVVISORIA finché Filippo non sceglie il foglio di disposizione e conferma le due schede
affiancate (todo 249, `pcb/PROPOSTA-todo170.md` P4). Ipotesi più neutra:

- **Un C96 solo**, sulla scheda segnale. La scheda reroute non tocca il backplane.
- **Ponte**: cavo piatto 2x16 (`ponte.py`, J4 segnale - J1 reroute). Porta ±18, ±15LN, ±REF5,
  RRN_L/R, le 8 uscite DIR dei driver d'iniezione e i 4 cursori POT_R. Solo reti a bassa
  impedenza: le 10k verso i net dei bus S1-S4 restano sulla scheda segnale, accanto al C96.
- **Cavo dei pot J2 invariato**: i POT_R passano dalla scheda segnale al ponte.
- Scheda reroute senza C96: 4 fori M3 senza rete (distanziali isolati), NOTA da decidere col
  telaio. Bulk locali dopo il cavo (2x 47u, 2x 10u, 2x 1u): le uniche parti nuove.
- Circuito identico: le distinte delle due schede sommate = la distinta di prima + ponte e
  bulk (controllato). Polarità invariata (stessi stadi, stesso ordine).

Schede: `fx-ret.py` (segnale, 199 impronte: METER e FADER sul retro) e `fx-ret-reroute.py`
(cartella `reroute/`, 225 impronte: reroute 3 e 4 sul retro, trimmer SMD 3214W, NOTA sotto). Correzione: J3 (jack del
pedale) si sovrapponeva al foro H2, spostato da y 5 a y 12.

Divisione di partenza (proposta originale):

1. **FX-RET segnale** (col C96): somma del bus, driver del pedale, ritorno, GAIN, EQ2, meter,
   fader, alimentazione. ~200 impronte.
2. **FX-RET reroute**: 8 VCA dei reroute, I/V, driver d'iniezione, 4 shaper, 12 trimmer.
   ~210 impronte. Riceve RRN_L/R e i 4 cursori, rende S1-S4_OUT: le iniezioni vanno al C96
   con un cavo corto o con un secondo C96 (da decidere col backplane, PIANO-schede §Conseguenze).

## Scelte segnate NOTA (non scritte nei documenti)

1. **Jack del pedale su un cavo (J3)**: la posizione dei jack SEND/RETURN non è decisa.
2. **TVS**: parte da scegliere (bidirezionale, ≤ 5 pF, fx-module §8.4).
3. **Pedale mono** (controlled mono sum, fx-module §2): non c'è sulla scheda. Serve un
   interruttore o un jack con contatto: decisione di pannello.
4. **Smoothing 1 ms del reroute** (dec. 80): C 470n sul 2k dello stadio del partitore,
   τ 0,94 ms, al posto dell'RC 1k/1µ della simulazione (un RC in serie caricava lo stadio).
   Da rifare in LTspice prima del prototipo.
5. **Uscita verso MSUM**: l'I/V del fader fa da buffer (≤ 50 Ω), 47 Ω verso il backplane.
   Il documento dice «buffer out»: un OPA1612 in meno.
6. **Meter mono centrato**: (L+R)/2 con due 20k e 4,02k: g = 0,287 (doc 0,288). LM3915 sulla
   scheda comandi, MET sul cavo.
7. **EQ2 del ritorno = cella del FX-SEND** (fx-eq2-pot10k.cir, HIGH 5,23k/2,49k): fx-module §6
   dice «stessa famiglia».
8. **Cap-moltiplicatore ±18** scalato a ~50 mA come il FX-SEND: questa scheda tira di più
   (10 VCA, 25 op-amp). Da riscalare sulla corrente vera.
9. **GLOBAL_MUTE** (c9) non usato: il documento non dà un mute ai ritorni.
10. ±15 LN dal +18 V (come MIC e master), non dal raw ±22: LT3045/3094 reggono 20 V.

## Da fare

- Divisione in due schede (sopra), poi PCB di ognuna.
- ~~Cavo J2 (36 fili) e scheda comandi~~: fatta il 2026-11-11, sezione «Scheda comandi» in fondo.
- Polarità ricontata da capo a capo dopo la divisione (sistema-polarita §4).

## Esito della PCB (2026-11-04)

Primo giro a scheda unica: Freerouting acceso 55 minuti senza finire, fermato. Poi la divisione.

| Scheda | Impronte | Esito | DRC | Controllo audio A1/A2/A3/A4/A5 |
|---|---|---|---|---|
| `fx-ret.py` (segnale, col C96) | 199 | **PASSA** al 3o giro | 0 errori; 2 via_dangling, 10 silk_overlap, 14 silk_over_copper, 52 attesi | 19 / 67 / 27 / 3 / 4 |
| `fx-ret-reroute.py` | 225 | **PASSA** al 4o giro | 0 errori; 8 silk_overlap, 24 silk_over_copper | 8 / 20 / 8 / 2 / 0 |

Giri della scheda segnale: ±18 a 0,6 mm = -18V aperta (23); ±18 a 0,4 = 1 errore di distanza
(via da 1 mm di V27F+ a 0,22 mm da un pad di U30); anche V27F± a 0,4 = PASSA.

Giri della scheda reroute: ±18/±15LN a 0,6 = +15LN aperta (19); a 0,4 = ECR3_R ed ECR1_R aperte:
i trimmer 3266 a foro passante restano davanti, il retro mette il VCA lontano (fino a 115 mm).
Con trimmer SMD i reroute 3 e 4 vanno interi sul retro: NDR3 aperta; le 20k del driver
d'iniezione nel blocco del driver (davanti) = PASSA.

NOTA nuove della divisione:

11. **Trimmer SMD Bourns 3214W** sulla scheda reroute (12 pezzi: simmetria, law, offset) al posto
    del 3266W. I giri (vca-trim §3.2 chiede 25 giri per il law) vanno verificati sul datasheet.
12. **±18, ±15LN e V27F± a 0,4 mm** (come il MIC): 0,4 mm porta ~1 A, il ramo qualche centinaio di mA.

A2 alto sulla scheda segnale (67): reti del cavo dei pot e del ponte lunghe. Un PASSA singolo
non è una prova (Freerouting cambia a ogni giro).

## Scheda comandi (todo 270, 2026-11-11)

`fx-ret-comandi.py`, file in `comandi/`, celle in `pcb/tools/comandi.py`. 59 × 225,85 mm, parallela
al pannello (61 × 229,85), retta dai dadi dei pot. Posizioni da `coordinate.json`, modulo «fx-ret».
Una scheda sola per i 4 ritorni (dec. 130).

- Pezzi: GAIN pot doppio 10k lin selezionato (T2: antiorario = O2A, cursore GW, orario = GA;
  verso da `sim/gain-pot/ritorno-buffer-g1.cir`, xg = 0 = retroazione zero = silenzio); EQ HIGH ed
  EQ LOW pot doppi 10k (reti del FX-SEND); SELF, > FX2, > FX3, > FX4 pot singoli 10k lin con scatto,
  rovesci (+REF5 - POT_Rj - AGND, sistema-comandi.md); barra da 10 LED con un LM3915 (RHI = +REF5,
  chip a sinistra della barra); fader PTA4543 (+REF5 in cima, POT_F, AGND).
- Cavo: J2 2×18 verso J2 di `fx-ret.py` (ordine letto dal file), sul bordo destro.
- Esito: 23 componenti, 39 reti. Tre giri senza ripetizione: due PASSA, uno NON PASSA (14 aperti).
  Ora con `riprova=True` (`DesignRiprova`, fino a 4 tentativi). A1: il pin 9 (MODE) dell'LM3915
  resta lontano dal 100n, come sul canale; il pin 3 (V+) a 3,2 mm.

NOTA della scheda comandi (da verificare):

1. **Ordine dei reroute nei 4 moduli.** La scheda è una sola: il pot in posizione j (dall'alto)
   va a POT_R1-R4, cioè al bus Sj. Il pannello di `proposta_f.py` fa lo stesso: in posizione j
   scrive «> FXj», e «SELF» nella posizione del bus del modulo. `coordinate.json` riporta il ritorno
   FX1. Nessun cavo diverso fra i moduli.
2. **RHI del meter = +REF5 dei pot**, come il canale (canale/NOTE.md, nota 2): da misurare a banco.
3. Pot di classe 14 mm (GAIN, reroute) su impronta RK09L, con l'ingombro da 14 mm.
4. Fader PTA4543: pezzo a catalogo con l'impronta in KiCad, da confermare.

## C96 a 5,3 mm dal bordo (2026-11-12, todo 303)

Il C96 maschio sta a y = H - `backplane.C96_DAL_BORDO` (7,84: fila b; fila a a 5,3 mm dal bordo,
disegno Harting e riga «Board edge» dell'impronta). Prima y = H - 6,5 metteva la fila a a 3,96 mm.
Esito: segnale PASSA al 4o giro (giro 2 PASSA con A5 7, giro 3 NON PASSA con 3 aperti, giro 4 PASSA con A5 12, tenuto il giro 5: A1/A2/A3/A4/A5 19/67/27/4/0).

Verificato in: KiCad (ERC, DRC). Live: no.
