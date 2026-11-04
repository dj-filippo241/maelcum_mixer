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

## Proposta di divisione (da confermare: cambia il telaio, dec. 144)

Due schede affiancate sotto il pannello del ritorno, come il master (dec. 140):

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
- Cavo J2 (36 fili) e scheda comandi: pot GAIN doppio, EQ2 ×2 doppi, 4 reroute, fader, LM3915.
- Polarità ricontata da capo a capo dopo la divisione (sistema-polarita §4).

## Esito della PCB (2026-11-04)

Un giro completo (tutto sul lato componenti, nessun blocco col retro): Freerouting è rimasto
acceso 55 minuti senza finire ed è stato fermato. Nessuna PCB salvata: la scheda va prima
divisa (sopra). Lo schema passa.
