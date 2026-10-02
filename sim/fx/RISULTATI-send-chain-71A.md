# RISULTATI — rumore SEND CHAIN FX a canali vivi (coda 71A, S5-sessione 2026-10-02)

Netlist: `send-chain-noise.cir`. Task: verificare/riffinare la stima
«−95 dBu per canale» di `fx-send-module.md` §6 [PROVVISORIO]. Metodo
casa: densità a 12 punti, integrale trapezoidale di en² in python,
A-weight IEC sui punti, MAI `.meas INTEG`.

## Catena simulata (un canale, detent EQ2, level al massimo = worst)

tap di canale (47 Ω) → buffer IN OP1612 → EQ2 (LOW shelf 120 Hz 1×
OP1654 + HIGH sottrattiva 4,5 kHz 3× OP1654, valori scalati da
`fx-eq2.cir`) → level pot 10k log al max → assign ON (Ron 4,7) → buffer
di iniezione OP1654 → R 10k → net multidrop → summing virtual-earth del
modulo FX (Rf 10k). Altri contributori del bus terminati (switch aperti).

## Risultato per canale

| Grandezza | Valore |
|---|---|
| Densità all'uscita summing bus, 1 send vivo | 53,7 nV/√Hz (piatta; 58,3 a 10 Hz) |
| di cui catena send sola (tolto il floor Rf+op) | 52,1 nV/√Hz |
| Integrato A-wtd al jack send (riferimento di −100,8) | **−98,5 dBu A-wtd** |
| Stima §6 da verificare | −95 dBu per canale [PROVVISORIO] |
| Esito stima | **confermata conservativa: reale 3,5 dB MEGLIO** |

Ripartizione: il dominatore è la cella HIGH sottrattiva: il trio
Rah/Rbh/Rfh da 49,9k versa ciascuno il proprio en (28,3 nV/√Hz) a guadagno
1 sul nodo di somma della cella → ~49 nV/√Hz; la cella LOW (noise gain
~2 al detent) e il resto stanno sotto ~16 nV. Floor indipendente dal
level: buffer iniezione + coppia Rinj/Rf 10k ≈ 19,3 nV/√Hz per send.

## Conseguenza di sistema (FINDING, aperto)

Il floor e la catena vivono sul bus solo quando un assign è ON; con
assign OFF il send è terminato (shunt π a GND) e vale il floor del bus
misurato in `RISULTATI-fx-noise-71A.md` (−100,8 A-wtd). Trasferendo il
bus ai ritorni (guadagno ~0 dB) e al MASTER SUM:

| Condizione send | Rumore al jack send | Sistema A-wtd (stimato sul budget docs/06 §7) |
|---|---|---|
| tutti OFF (terminati) | −100,8 dBu | −80,5 dBu (misurato, PASS 2,5) |
| 1 send vivo, level −20 dB | ~−99 dBu | ~−79,5 dBu (≈ target −78) |
| 4 send vivi, level −20…−10 dB | −97,7 dBu | **−73…−71,5 dBu (FAIL 5-6,5 dB su −78)** |
| 4 send vivi, level 0 dB | −92,6 dBu | **−66,6 dBu (FAIL 11,4 dB)** |

Lettura: il contributo indipendente dal level (19,3 nV vs 12,9 del
terminato) basta a portare il sistema ~5 dB sopra il target appena UN
send è assegnato; a level alti la cella HIGH aggiunge il resto. Nel club
il floor −73 dBu resta mascherato (≈ 27 dB SPL equivalenti contro 22 del
target); in ambiente quieto è fruscio udibile quando un FX è assegnato.

## Leve di fix (ingegneria, non ancora attuate)

1. Cella HIGH: bufferizzare il wiper del pot HIGH e scalare il trio
   sottrattivo 49,9k → 4,99k (en ÷3,16; law del pot più pulita perché
   scarico): toglie la parte level-dipendente (−66,6 → −73,4 a level max).
   Richiede rerun di `fx-eq2.cir` (curve invariate: solo rapporti) + REV
   fx-send-module §2/§6.
2. Convenzione di iniezione FX (10k multidrop): ridurla a 4,7k dimezza il
   floor della coppia ma rompe la convenzione house (driver, crosstalk,
   pinout): NON raccomandata.
3. Deroga d'uso: registrare che il target −78 vale a send NON assegnati;
   con FX in uso il floor di sistema è −73 dBu A-wtd (−67 a level max),
   accettato come carattere del caso d'uso (disciplina operatore: level
   send quanto serve). Costo zero, onesto, coerente con K4.

Stato: FINDING APERTO → decisione di Filippo (deroga vs fix 1 vs banco).
Voce 71A: la coda «send chain a canali vivi» passa da [PROVVISORIO] a
MISURATA con questo doc; la decisione sul floor resta aperta.
