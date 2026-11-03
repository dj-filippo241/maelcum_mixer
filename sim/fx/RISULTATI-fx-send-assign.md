# RISULTATI — assign del FX-SEND: rampa e headroom (todo 224 e 185, 2026-11-03)

## 1. La «ramp 1 ms» sul pin IN non esiste (todo 224)

`fx-send-module.md` §2-§3 otteneva la ramp della dec. 80 rallentando il
fronte sul pin IN dell'ADG1434 (R 10k + C 100 nF): «il Ron attraversa la
regione resistiva». Datasheet ADG1433/ADG1434 Rev. E (copia rlocman,
letta il 2026-11-03), Tabella 1 e funzioni dei pin:

- INx = «Logic Control Input», sezione DIGITAL INPUTS: VIH 2,0 V min,
  VIL 0,8 V max, corrente d'ingresso ±0,005 µA;
- tTRANS 140 ns typ (±15 V); nessun parametro di comando analogico,
  nessuna isteresi dichiarata.

Esito: l'interruttore scatta tutto alla soglia, in centinaia di ns. Un
fronte lento non dà la rampa. Senza isteresi può anche far scattare
l'interruttore più volte attorno alla soglia (rumore sul fronte lento).
Oggi gli assign del FX-SEND sono quindi secchi: click nel bus FX, e il
delay lo ripete.

**Rimedio**: taglio al passaggio per lo zero, come il kill del 5-way
(dec. 164, `sim/five-way/RISULTATI-kill-zc.md`). Il segnale è lo stesso
per le 4 destinazioni: basta un comparatore per lato (2 per modulo) e
un flip-flop per assign e lato (8 = 4 doppi 74HC74). Il pin IN torna
pilotato da un fronte netto. È la stessa tecnica dei controlli di
volume digitali con rilevazione dello zero.

Netlist: `sim/fx/fx-send-assign-zc.cir` (copia di `kill-zc.cir`),
programma a banda piena 60 Hz 1,1 Vp + 1 kHz 0,8 Vp + 8 kHz 0,4 Vp
(picco ~2,2 V), bottone premuto in un istante qualsiasi.

| | Secco (oggi) | Zero |
|---|---|---|
| Gradino all'apertura dell'assign | 0,34 V | 1,0 mV (−51 dB) |
| Gradino alla chiusura | 0,84 V | 1,6 mV (−54 dB) |
| Sonda del click, dopo l'apertura (programma 0,51 V) | 0,67 V (+2,3 dB) | 0,41 V (sotto il programma) |
| Sonda del click, alla chiusura | 0,84 V (+4,3 dB) | 0,51 V (0 dB: nessun click) |
| Ritardo del gesto | 0,1 µs | 20-80 µs |

Col programma a banda piena gli zeri sono fitti: il ritardo è di
decine di µs, non si sente. Col ritardo reale della catena (~0,4 µs)
il gradino sale di circa 4 volte, ~−40 dB: resta sotto il programma.

## 2. L'ADG1434 a ±15 V tosa sopra ~+22,5 dBu (todo 185)

Datasheet Rev. E, Tabella 1: «Analog Signal Range VSS to VDD». Oltre
le alimentazioni conducono i diodi interni di protezione (massimi
assoluti VSS − 0,3 V … VDD + 0,3 V o 30 mA). Rail dello switch:
±15 V (78L15/79L15, ±4 %: fino a ±14,4 V).

- Limite del segnale allo switch: 14,4-15 Vp = **+22,4…+22,7 dBu**.
- Requisito di sistema: +24 dBu = 17,4 Vp. **Non passa**: 1,3-1,6 dB
  sotto. Il «nessun clip fino a +21,5 dBu» del design doc §7 era vero
  ma non arriva al requisito.
- Sopra il limite i diodi tosano duro e il segnale esce dai massimi
  assoluti del chip.

**Rimedio [PROVVISORIO]**: spostare il π SPDT dopo la R 10k di
iniezione, fra la R e il pin del backplane. Lì la linea è il nodo a
massa virtuale del summer del bus (multidrop con la R lato sorgente,
fx-module §3): lo switch vede solo I × Ron (≤ 1,8 mA × 4,7 Ω ≈ 8 mV a
+24 dBu). Spento: la serie apre e lo shunt mette a massa il lato della
R. Nessun limite di headroom dallo switch, rail ±15 V invariato.
Effetti collaterali:
- Ron in serie a 10k: errore di guadagno 0,05 %, ±0,4 Ω fra chip.
- Charge injection (−50 pC) nel nodo virtuale: impulso Q × Rf =
  5e-7 V·s col summer 10k/10 pF, in banda audio quanto un gradino di
  pochi mV. Trascurabile; si conferma a banco.
- Bonus possibile: un buffer d'iniezione per lato invece di uno per
  linea (8 → 2 sezioni), perché lo switch sta dopo la R. Da decidere
  col rumore (todo 184).
