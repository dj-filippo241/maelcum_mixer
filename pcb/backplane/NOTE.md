# Backplane a tratti, disposizione F: note della bozza v0.1 (todo 269, 2026-11-11)

Piano, slot, reti e cavi: `piano_f.py` (Python puro) scrive `PIANO.md` e controlla le reti.
Schede: `tratto.py T1|T2|T3|T4` (Python di KiCad) scrive `t1/` … `t4/`. Origine [C, PROVVISORIO].

## Perché a tratti

Nella disposizione F le schede di modulo stanno in due versi (`pcb/PIANO-SCHEDE-F.md`):
sinistra-destra sotto MASTER, 5-WAY, FILTRO e CUE; dietro-davanti sotto le strisce. Un backplane
unico coprirebbe tutto il fondo (450 x 570 mm, quasi tutto vuoto). Quattro tratti, uno per zona:

| Tratto | Zona | Slot |
|---|---|---|
| T1 | fondo, 450 x 138 | MASTER segnale, uscite L e R, 5-WAY 1 e 2, PSU-IN |
| T2 | canali, 200 x 166 | FILTRO 1 e 2, 4 canali, 4 FX-SEND |
| T3 | cuffie, 200 x 40 | CUE |
| T4 | destra, 244 x 296 | MIC, 3 MONO, 4 FX-RET |

MIC/MONO e ritorni stanno su un tratto solo: i bus S1-S4 (massa virtuale) li usano tutti e due;
separati, i bus passerebbero su un cavo in più.

## Da dove vengono le reti

- Ogni slot prende i pin dal netlist vero della sua scheda (`pcb/<modulo>/out/netlist.xml`, J1).
  Una scheda rigenerata con un pin nuovo: si rilancia `piano_f.py`, poi i tratti.
- 5-WAY e FILTRO non hanno ancora una scheda: righe b da `sistema-backplane.md` §4 (SINTETICO).
  La seconda scheda di ognuno ha solo l'alimentazione, come le uscite del master (dec. 143). NOTA.
- Le reti che decide la posizione: canale n → CUEn, SEND_TAPn, FILT_MODEn (c1-c2 del canale vanno
  a c(2n-1)-c(2n) del filtro); FX-RET n → BUS_IN su Sn, RET_OUT su MSUM(n+1) (dec. 130).
- Ponticelli di continuità (dec. 111): J5W (5-way → MSUM1) e JMS (inserzione del master) su T1.
  VIE_TAP del master su una presa JVIE (nessuno slot UTIL nella disposizione F). NOTA.

## Scelte segnate NOTA

1. **Verso del C96.** La femmina mette a1 nello stesso punto del maschio della scheda di modulo
   (maschio a x = 50, ruotato 180: a1 a 89,37 mm dall'inizio della scheda). La fila b sta sulla
   linea del posto. La distanza vera fra la scheda di modulo e le file va letta sul disegno del
   connettore (TE/Harting/ept), insieme a quale fila sta dal lato componenti: oggi non verificato.
2. **Posti delle schede dietro-davanti**: posto q a x_striscia + (q + 0,5) x larghezza / posti
   (canale 12,5 e FX-SEND 37,5 nella striscia da 50; MIC, MONO, FX-RET a 15,25 nella striscia da 61).
3. **PSU-IN** nella fila 4 sotto il 5-way, x 350-450: è libera nel piano F e sta vicino alla colonna
   destra. Il PSU-IN è la stella: ogni tratto riceve il suo radiale AGND su un cavo di potenza.
4. **PTC per slot e per rail** (psu-esterno §4.3), tenuta per classe in `piano_f.PTC`: canale 0,3 A sui
   ±27, 5-way 0,5, CUE 0,5 (clamp fino a ~340 mA, backplane §6: il documento diceva 0,1-0,2),
   filtro 0,3 anche sui ±22 (OTA), FX-RET 0,2, FX-SEND / MIC / MONO 0,1, uscite del master 0,2 sui
   [M]. Sui ±22 e sul +5V 0,05-0,2 A (tabella). 1812, almeno 33 V. Il RAW+22 della scheda d'uscita L è solo lettura del supervisore: niente PTC.
5. **Bypass di slot** dopo la PTC: 100n + 10u MLCC 50 V 1206 per rail (backplane §8).
6. **Cavi fra tratti**: cavo piatto IDC, ogni segnale fra due fili di massa (GLOBAL_MUTE fra
   CTRL_GND). Un cavo porta solo net a massa virtuale (VE: DJBUS, S1-S4, MSUM6-7) o solo linee
   pilotate, mai insieme (backplane §4 REV todo 133, ≤ 0,2 pF fra VE e una linea pilotata).
   I fili di massa sono uniti ai due capi: la corrente di ritorno del segnale corre accanto al
   segnale. Il cavo di potenza dello stesso tratto va legato ai cavi di segnale (anello piccolo).
7. **Cavi di potenza**: Mini-Fit Jr 2x5 da T1 a ogni tratto: RAW±27, RAW±22, +5V, 3 AGND,
   CTRL_GND, CHASSIS. Correnti massime: T2 ~1,0 A sui ±27 (4 canali, 4 FX-SEND, filtro), T4 ~0,5 A.
8. **Piste**: tronco dei rail 1,2 mm, rail di slot 0,6 mm, +5V e CHASSIS 0,8, CTRL_GND 0,5. Su T1
   il tronco porta tutta la corrente del mixer (fino a 2,7 A sul ±22 pre-regolato): 1,2 mm su 35 µm
   scalda ~10 °C (IPC-2221, strato esterno; calcolo mio) e vale ~0,12 ohm ogni 30 cm: ~0,1 V
   con l'1 A che va a T2. Da rifare con colate di potenza (come la NOTA 5 del PSU-IN).
9. **Fori**: M3 a CHASSIS, fissaggio al fondo del telaio. Il bond CHASSIS-AGND resta solo nel PSU-IN.
10. Righe c libere (c10-c15 CV, LED_DIM, SVC): nessun modulo le usa oggi, il backplane non le porta.
11. **Gruppi PTC fissi su T2** (`tratto.GRUPPI`): coi blocchi automatici PTC e condensatori finivano
    sopra i C96 e fuori dal bordo, e Freerouting non chiudeva in un'ora. Ogni slot ha il suo spazio
    fra due connettori (13,3 mm), in basso vicino ai pin a1-a8 dei rail; SEND4 e i due FILTRO stanno
    nella parte alta di uno spazio. Foro H1 a x 104 (a 110 toccava il cavo C1).
12. **T2 a tre strati di piste** (`inner_signal`, massa piena su In1): i bus attraversano otto C96
    in fila. Con due strati Freerouting girava 40 minuti a tentativo. Anche `link_pairs_masse`:
    senza, CTRL_GND restava aperto su 57 pin su 60 (un gemello a23-a24 aperto fa disfare la rete,
    come sul canale il 10/11). T1, T3 e T4 restano come sono: passano senza.

## Esito

Dettagli in `t<n>/out/riepilogo.json`.

| Tratto | Pezzi | Esito |
|---|---|---|
| T1 | 75 | PASSA al primo tentativo di Freerouting, DRC 0 |
| T2 | 170 | PASSA al primo tentativo, DRC 0, al quinto giro di lavoro (NOTE 11 e 12) |
| T3 | 22 | PASSA al primo tentativo, DRC 0 |
| T4 | 137 | PASSA al primo tentativo, DRC 0 |

Verificato in: KiCad (ERC, DRC). Live: no. Il verso del C96 (NOTA 1) resta da leggere sul disegno.
