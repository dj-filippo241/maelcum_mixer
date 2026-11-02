# RISULTATI — levetta HPF/OFF/LPF col dip del VCA del fader (A22bis, 2026-11-02)

Domanda: la levetta HPF/OFF/LPF dopo il fader (dec. 159a) sposta il
segnale fra DJ bus, bus HPF e bus LPF con un ADG (break-before-make). Il
passaggio dell'ADG è secco. Serve una rampa propria, o basta che il VCA del
fader (dec. 126) abbassi il segnale un istante attorno al cambio («dip»)?

Netlist: `sim/cdj/filtsel-dip.cir` (VCA `sim/lib/that2181.inc`, ADG come
interruttore ideale con BBM 1 µs, uscite multidrop 10k). Sonda del click =
HP 2 poli ~1,6 kHz, come five-way §8.5 e `sim/fx/reroute-ramp.cir`.
Segnale 1 kHz, cambio al picco (caso peggiore).

## Click (picco della sonda, in dB sopra il programma puro)

| Caso | +10 dBu, DJ bus (lascia) | +10 dBu, bus HPF (arriva) | +18 dBu, DJ | +18 dBu, HPF |
|---|---|---|---|---|
| 0. Secco (solo ADG) | +7,1 | +14,0 | +7,2 | +14,0 |
| 1. Dip lineare in dB, 1 ms giù / 1 ms su | +2,5 | +0,4 | +2,5 | +0,4 |
| 2. Dip con un RC (τ 1 ms) | +5,4 | sotto il programma | +5,4 | sotto |
| **3. Dip con due RC (2 × 0,5 ms)** | **+1,8** | **sotto il programma (−11)** | **+1,8** | **sotto (−11)** |

Programma puro alla sonda: 0,69 V a +10 dBu, 1,73 V a +18 dBu. Il
riferimento della famiglia «ramp 1 ms» (dec. 80, five-way §8.5) vale +6,1
dB sullo stesso metro: il caso 3 fa meglio.

Lettura:
- Secco: il bus nuovo riceve un gradino dal picco del segnale. È un click
  netto, 14 dB sopra la musica alla sonda.
- Un RC solo parte troppo ripido: in 0,1 ms il VCA scende già di 16 dB, e
  il click resta (+5,4).
- Due RC in fila partono morbidi (CV a S): il click sparisce sul bus che
  riceve e resta un'ombra sul bus che lascia, sotto la rampa validata.
- Il livello non cambia niente: a +18 dBu i rapporti sono gli stessi.

## Tempi del caso 3 (calcolati dalla rete RC)

- Dalla levetta: −20 dB dopo 0,3 ms, −100 dB dopo 1,0 ms. L'ADG commuta a
  1,6 ms (CV a 0,83 V, oltre il floor del VCA).
- Dopo il cambio: −20 dB a ~1,8 ms, −3 dB a ~3 ms, −1 dB a ~3,6 ms,
  −0,1 dB a ~4,9 ms.

All'orecchio: girando la levetta il disco fa un respiro di 3-4 ms, un
buchino che si sente appena come un «tic» morbido, invece del click secco.
La levetta risponde con 1,6 ms di ritardo: impercettibile. CUE, FX SEND e
meter stanno prima del fader e non vedono il dip: in cuffia il disco resta
continuo.

## Circuito (per canale) [PROVVISORIO]

- Logica autotemporizzata: i 2 bit della levetta (con antirimbalzo RC) si
  confrontano coi 2 bit memorizzati che pilotano l'ADG (74HC86 XOR + OR).
  Se differiscono, parte il dip. Un ritardo RC + Schmitt (74HC14, ~1,6 ms)
  dà il clock a due flip-flop (74HC74), che copiano il nuovo stato
  sull'ADG. Gli stati tornano uguali e il dip si rilascia da solo.
- Dip: uscita logica → due celle RC 10k/50n con buffer (mezzo OPA1654) →
  resistenza di somma sul nodo EC− dei 2 VCA del fader (accanto alla CV
  dello shaper, `docs/fase3/sistema-vca-trim.md`). Al pin serve ≥ 0,61 V.
- Conto: 3 chip logici piccoli + mezzo op-amp + ~10 passivi per canale.
  Nessun VCA in più. Una rampa propria vera servirebbe un VCA di mute per
  lato (8 VCA) o un VCA per uscita (24).

## Errore trovato (vecchio, FX-SEND)

`fx-send-module.md` §2 e §3 ottengono la «ramp 1 ms» degli assign
rallentando il fronte sul pin IN dell'ADG1434 (RC 10k/100n), e dicono che
«il Ron attraversa la regione resistiva». Il pin IN di un ADG è un
ingresso logico: l'interruttore scatta tutto alla soglia, in tempi di
centinaia di ns. Un fronte lento non dà la rampa (e senza isteresi può
far ballare l'interruttore attorno alla soglia). Da verificare sul
datasheet ADG1434 Rev. E. Se confermato, gli assign del FX-SEND sono secchi
e la dec. 80 non è rispettata lì: todo a parte.

## Non fatto

- Feedthrough della CV del dip nell'audio (non nel modello): layout della
  CV lontano dall'audio, da misurare a banco.
- Rimbalzo reale della levetta e scelta dell'antirimbalzo.
- Programma musicale vero (qui 1 kHz): il «tic» del buco va sentito.
