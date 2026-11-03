# RISULTATI — rumore della send chain FX, scheda v0.2 (todo 184, 2026-11-03)

Netlist: `send-chain-noise-v2.cir`. Rifà `send-chain-noise.cir` (2026-10-02),
che descrive la cella LOW vecchia e lo switch prima della R di iniezione.
Metodo §8.9: densità a 16 punti, `noise_total.py`, mai `.meas INTEG`.

## 1. Cosa cambia nel circuito

- Cella LOW Baxandall col pot doppio 10k (R 324, C 180n C0G), come
  `fx-eq2-pot10k.cir` e `pcb/fx-send/fx-send.py`. Detent xl 0,5.
- Cella HIGH sottrattiva invariata (trio 49k9). Detent thh 0,5.
- Switch π SPDT dopo la R 10k di iniezione (todo 185): spento, la serie
  apre e il nodo del bus non vede più la sorgente.
- Tre topologie (`topo`):
  0 = vecchia: switch prima del buffer. Gli assign spenti degli altri 3
  canali restano sul bus con buffer vivo e R 10k (il netlist del
  2026-10-02 li lasciava flottanti: era ottimista).
  1 = nuova, un buffer d'iniezione per linea (scheda attuale).
  2 = nuova, un buffer per lato che pilota le 4 R (8 → 2 sezioni).

## 2. Risultato all'uscita del summer del bus (1 canale vivo, 1 assign ON)

| LEVEL | topo 0 (vecchia) | topo 1 (nuova) | topo 2 (buffer comune) |
|---|---|---|---|
| al massimo (0 dB) | −101,0 dBu A | **−101,7 dBu A** | −101,7 dBu A |
| −20 dB | −106,8 dBu A | **−110,7 dBu A** | −110,7 dBu A |
| tutto giù (floor) | −107,0 dBu A | **−111,2 dBu A** | −111,2 dBu A |
| densità a 1 kHz, LEVEL max | 61,3 nV/√Hz | 56,3 nV/√Hz | 56,3 nV/√Hz |

Lettura:
- La cella LOW nuova non pesa: a LEVEL al massimo domina ancora il trio
  49k9 della cella HIGH.
- Lo switch dopo la R guadagna 4 dB sul floor: gli assign spenti degli
  altri canali escono dal nodo del bus e non alzano più il suo noise gain.
- Il buffer comune per lato (topo 2) ha lo stesso rumore della scheda
  attuale. Carico: 4 R 10k in parallelo = 2,5 kΩ, a +24 dBu 7 mA di
  picco: l'OPA1654 li regge. Risparmio: 2 OPA1654 quad per modulo
  (8 per i 4 moduli). Effetto: un guasto al buffer spegne tutti e 4 gli
  assign di quel lato. [PROVVISORIO: scelta di scheda, non sonora.]

## 3. Cosa arriva al sistema

Ipotesi: pedale a guadagno 0 dB e senza rumore proprio; ritorno al detent
(−96,2 dBu A, RISULTATI-gain-pot §5); sistema a filtri OFF −82,9 (docs/06
§14); floor del bus a send spenti −100,7 (docs/06 §8) oppure −91,5 coi
reroute a peso 1 (dec. 130).

| Condizione | Floor bus −100,7: 1 bus in uso | 4 bus in uso | Floor −91,5: 1 bus | 4 bus |
|---|---|---|---|---|
| nessun send | −82,8 | −82,6 | −82,3 | −81,0 |
| 1 send, LEVEL −20 dB | −82,8 | −82,6 | −82,3 | −81,0 |
| 1 send, LEVEL max | −82,8 | −82,4 | −82,3 | −80,8 |
| 4 send su ogni bus, LEVEL max | −82,6 | **−81,8** | −82,1 | **−80,4** |

Il caso peggiore resta 2,4 dB sotto il target ≤ −78 (dec. 89).

## 4. Correzione dei numeri della dec. 95

`RISULTATI-send-chain-71A.md` dava −73 dBu A al sistema con un send
assegnato e −66,6 con 4 send a LEVEL 0 dB. Quei numeri non seguono dai
dati dello stesso documento: il bus a −92,6 dBu (4 send al massimo),
riportato al master con guadagno ~0 dB, non può portare il sistema
sopra −81 circa. Per arrivare a −66,6 servirebbero ~26 dB di guadagno
fra jack send e master. La causa dell'errore non è ricostruita.

Con i numeri giusti, anche la vecchia scheda passava (−82,4 con 4 send al
massimo su ogni bus). La deroga d'uso della dec. 95 resta valida ma non
serve più: il target vale anche con gli FX in uso, nell'ipotesi di un
pedale a 0 dB. Il rumore proprio del pedale resta fuori dal conto.

## 5. Limiti

- Il conto del §3 somma potenze; 4 sorgenti vive sullo stesso bus alzano
  il noise gain del summer (da 2 a 5): la parte del summer (OPA1612 +
  Rf 10k) resta circa 10 dB sotto i 4 send (stima a mano, non simulata).
- Pedale con guadagno: il suo rumore e quello dei send salgono insieme al
  segnale. Non è un costo del mixer.
