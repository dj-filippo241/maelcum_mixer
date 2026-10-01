# RISULTATI — Budget rumore canale di RITORNO FX (coda 71A)

Data: 2026-10-01. Netlist: `fx-return-noise-71A.cir`. Metodo §8.9 five-way:
densità `.noise` a 10 punti (20 Hz-20 kHz), trapezoidale python, MAI INTEG
(quirk LTspice 26.0.2), A-weighting IEC 61672 in post. Macro reali
(`opamp-audio.inc`: OP1654/OP1612) + OP1642-class 5,1 nV da
`fx-dc-servo.cir`. Primo budget del ritorno: mai simulato prima.

## Punto di misura e condizioni

**vret = uscita buffer del ritorno** (47 Ω + carico 10k = iniezione MASTER
SUM; la rete di summing del master sta nel suo budget, non qui). Jack
return terminato su sorgente rack ~100 Ω (condizione sheet "contributori
terminati"), GAIN VCA THAT 2181 al detent 0 dB, EQ2 al detent, fader unity.

Catena simulata (topologie validate del doc): protezione R 100 + TVS 5p +
**R bias (sweep 100k/220k/1M)** → buffer gain-2 OP1642-class con nodo FB →
DC servo (§8.4 VALIDATO: Rsi 1M/Ci 15n, Rinj 1M) → I/V 10k/5k = stadio
d'ingresso VCA (gain −0,5) → GAIN VCA (copia E lineare + rumore datasheet
−98 dBV a 0 dB senza I/V d'uscita → Rvn 476k = 89 nV/√Hz, E 4 nodi) →
EQ2 celle scalate (§8.4 VALIDATO, detent) → METER pickup 100k → REROUTE
(pre-fader, hi-Z) → FADER unity (track 10k + wiper 1k) → buffer out.

## Risultato

| Grandezza | Valore |
|---|---|
| Densità out (piatta; 105 nV @20 Hz → 103 nV @20 kHz) | **~103 nV/√Hz** |
| Integrato 20-20k unweighted | 14,5 µV = **−94,5 dBu** |
| Integrato 20-20k **A-weighted** | 11,7 µV = **−96,4 dBu A-wtd** |
| Mono sum L+R (+3 dB) | −91,5 / −93,4 |
| **4 ritorni al MASTER SUM (+6 dB)** | **−90,4 dBu A-wtd** |
| Stima provvisoria docs/06 | −88…−92 → il misurato sta in cima alla stima |

Ripartizione di potenza: **GAIN VCA 75%** (89 nV = floor datasheet −98 dBV:
configurazione in tensione senza I/V d'uscita), **front-end 25%** (buffer
gain-2 + Rf2/Rg 10k + servo + I/V + EQ2 detent + fader ≈ 52 nV combinati).
Nessun dominante anomalo: il ritorno è più pulito del canale CDJ (−90,3
A-wtd) perché l'EQ2 (2 celle) pesa meno dell'EQ β3 (4 celle).

## Finding — R bias 1 MΩ NON è un problema di rumore

Sweep 100k/220k/1M: densità identica a 7 cifre. Motivo: col return
terminato il nodo d'ingresso è a bassa Z (100 Ω sorgente + 100 Ω protezione
= 200 Ω verso GND in AC) → il rumore termico della R bias (129 nV/√Hz su
1 MΩ) resta diviso per Zs/(Zs+Rb) ≈ 2e-4. Anche nel caso peggiore reale
(pedalboard/guitar, sorgente 10 kΩ): coupling ≈ 1% = 1,3 nV, sotto il
termico della sorgente stessa (12,9 nV). La R bias 1 MΩ del doc §4 resta
giusta per l'hi-Z; nessuna fix necessaria.

## Assunzioni dichiarate (alcune da fissare nel design di dettaglio)

1. Carico d'iniezione MASTER SUM 10k [coerente col canale CDJ].
2. METER pickup = carico 100k, nessun contributo attivo (detector condiviso,
   design CDJ §7 item 6).
3. REROUTE pre-fader: i 3 VCA verso altri bus sono carico hi-Z e non
   contribuiscono a QUESTA uscita (la macro VCAM sensa tensione; il 2181
   reale presenta impedenza d'ingresso finita — il loro rumore va sui bus
   di destinazione, già coperto dal budget send). Da verificare a banco.
4. Rumore 218x = floor datasheet a gain 0 anche in configurazione tensione
   (il datasheet non dà rumore vs gain); a gain VCA > 0 dB il contributo
   cresce come il segnale: il rumore del ritorno segue la law del gain
   (stesso comportamento del drive 5-way, dec. 88d).
5. Fader pot 10k [PROVVISORIO voce 40, come i canali].
6. Sorgente rack 100 Ω terminata; caso guitar/pedal (10 kΩ): +10 dB di
   termico sorgente sul front-end, margine resta ampio.

## Impatto sistema (per la sintesi 71A)

4 ritorni a −90,4 dBu A-wtd sostituiscono la stima provvisoria (−82 con
classe −88 per bus) nella somma di sistema docs/06 §2: sistema stimato
≈ **−80,3 dBu A-wtd** (era −78,3 con la stima) → il target ratificato
sistema ≤ −78 (dec. 89) passa con ~2,3 dB di margine.
