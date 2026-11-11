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

## Circuito (per canale) [PROVVISORIO; REV 2026-11-11: DIFF ripreso, ritardo 68k + diodo, §5]

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

## 5. Logica vera e catena del fader della scheda (todo 289, 2026-11-11)

Dopo il todo 281 il dip entra nel nodo di somma dello shaper del fader (4,99k), non più sul
pin EC−. Qui la catena è quella di `pcb/canale/canale.py` e `celle_vca.py`, con la logica
vera: XOR, OR a diodi, ritardo RC + due Schmitt, 74HC74 a fronte (master-slave), ADG con BBM.
Op-amp con lo stato del polo fermato ai rail. Soglie del 74HC14 a 5 V dal datasheet TI
SCLS085L (rev. febbraio 2025), interpolate fra 4,5 e 6 V: VT+ 1,73 / 2,77 / 3,49 V
(min / tip / max), VT− 1,00 / 1,73 / 2,70 V.

Netlist: `filtsel-dip-logica.inc` (circuito), `filtsel-dip-logica.cir` (click e tempi, 72 casi),
`filtsel-dip-flick.cir` (levetta che torna indietro), `filtsel-dip-rdl.cir` (R del ritardo).
Varianti: **com'è disegnato** = RC del dip e ritardo 33k appesi al nodo dei diodi;
**ripreso** = DIFF ripreso da due porte libere (74HC14 sez. 6, 74HC86 sez. 4 con B a +5 V);
**correzione** = ripreso + ritardo 68k/47n + diodo di scarica in parallelo al 68k.

### Due guasti del circuito disegnato

1. **Rilascio lento.** Quando il flip-flop copia la levetta, l'XOR scende e il diodo si apre.
   Il nodo DIFF resta con 50n + 47n appesi e scende solo dal 100k a massa. Il VCA torna a −20 dB
   dopo ~20 ms e a −3 dB dopo ~40 ms (fader aperto). Il buco nella musica passa da 3-4 ms a
   ~40 ms: un vuoto netto, non un respiro.
2. **Canale muto se la levetta torna indietro.** Il 74HC74 copia solo sul fronte di salita del
   CLK. Col nodo DIFF lento il CLK resta alto decine di ms. Se in quel tempo la levetta torna
   indietro (un colpo avanti e indietro, o un rimbalzo lungo), il flip-flop non vede il ritorno,
   DIFF resta alto e il dip non si rilascia: canale a −127 dB per 40-80 ms
   (`filtsel-dip-flick.cir`: −3 dB a 79 ms). Con la sola porta di ripresa il blocco resta,
   più corto (~37 ms, soglie tipiche).

Terzo punto, sulle soglie: col ritardo 33k e VT+ minima l'ADG commuta a 0,66-0,76 ms, quando
il VCA è solo a −62…−66 dB. Click a ~−48 dB sotto la musica: debole, ma fuori dal criterio.

### Correzione [PROVVISORIO fino al banco]

- DIFF ripreso: 74HC14 sez. 6 (ingresso DIFF, uscita NDIFF) e 74HC86 sez. 4 (NDIFF xor +5 V =
  DIFFB). Le due celle RC del dip e il ritardo partono da DIFFB. Nessun chip in più.
- Ritardo 68k/47n (prima 33k) e diodo DLY → DIFFB: al rilascio il ritardo si scarica in pochi µs,
  il CLK scende e il flip-flop è pronto per il colpo dopo.
- Il "satura lo stadio del partitore" del todo 281 non conta: a fader aperto DIPCV arriva a
  3,7-5,0 V prima del rilascio, il pin a 0,72-0,77 V (≥ 0,61), lo stadio satura solo dopo l'ADG.

| R del ritardo, soglie min / tip / max | ADG dopo la levetta | VCA quando l'ADG commuta |
|---|---|---|
| 47k | 0,94 / 1,79 / 2,65 ms | −92 / −127 / −127 dB |
| 56k | 1,12 / 2,13 / 3,16 ms | −107 / −127 / −127 dB |
| **68k** | **1,36 / 2,59 / 3,83 ms** | **−124 / −127 / −127 dB** |

68k tiene −100 dB anche con le soglie minime e la R·C a −5 %. Costa 0,5 ms di buco rispetto a 56k.

### Tempi della correzione (fader aperto, dalla levetta; soglie min / tip / max)

| Punto | Prima (§1, dip ideale) | Ora |
|---|---|---|
| −20 dB in discesa | 0,3 ms | 0,3 ms |
| −100 dB | ~1,0 ms | 1,03 ms |
| ADG | 1,6 ms | 1,4 / 2,6 / 3,8 ms |
| −20 dB in risalita | ~3,4 ms | 3,1 / 4,4 / 5,7 ms |
| −3 dB | ~4,6 ms | 4,3 / 5,6 / 6,8 ms |
| −1 dB | ~5,2 ms | 4,9 / 6,2 / 7,5 ms |

Colonna «Prima»: i tempi del §1 contati dal cambio dell'ADG, qui riportati alla levetta
(+1,6 ms). Contata dall'ADG, la risalita è la stessa di prima (−1 dB 3,6 ms dopo): cambia solo
quando arriva l'ADG.

Click (sonda HP ~1,6 kHz, +18 dBu; uguale a +10 dBu): bus che lascia +0,2…+2,3 dB sopra il
programma secondo la fase (prima +1,8); bus che riceve sotto il programma in tutti i casi.
Levetta che torna indietro: nessun blocco, il dip si chiude a −3 dB in 8-9 ms.

All'orecchio: il respiro del disco sul bus passa da ~3 ms sotto −20 dB a ~4 ms (tipico; da 3 a
5,5 ms con le soglie estreme). La levetta risponde con 2,6 ms di ritardo invece di 1,6.

Verificato in: Python no / LTspice sì (.tran, logica a interruttori) / Live no (il dip non è nel
prototipo).

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
