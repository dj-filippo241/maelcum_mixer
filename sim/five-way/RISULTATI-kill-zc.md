# RISULTATI — kill del 5-way col taglio sullo zero (2026-11-03)

Richiesta di Filippo (2026-11-03): «secco va bene ma non deve sentirsi
scoppi nelle casse». Oggi (dec. 88, `RISULTATI-gate-switch.md` §4) il
π SPDT taglia nell'istante in cui la levetta cambia: il gradino è il
segnale istantaneo della via, 2,18 V al summer al picco, ~4,4 V in
uscita dopo il make-up. Le vie del 5-way si risommano e il DSP
dell'impianto le divide di nuovo: il gradino del SUB arriva anche alle
trombe come schiocco.

Correzione di una lettura vecchia: il benchmark (`docs/05`) dice solo
che Jah Tubbys, JB e Dub Sonic tagliano con un interruttore per via.
Nessuno dei 9 costruttori dice se il taglio fa click. «Il click è lo
standard della scena» (dec. 88, gate-switch §4) era una deduzione di
Claude, non un dato. Inoltre JB e altri hanno un'uscita per via: il
gradino del SUB va solo al sub, che non riproduce lo schiocco.

Netlist: `sim/five-way/kill-zc.cir`. Variante: un comparatore guarda la
via; la levetta passa all'interruttore solo al primo passaggio per lo
zero (flip-flop clockato dal fronte del comparatore). Ritardo della
catena nel modello ~0,1 µs; reale ~0,3-0,5 µs (comparatore + 74HC74 +
tTRANS ADG1434 140-200 ns). Gesto al picco (caso peggiore del secco),
via a +6 dBu (2,19 Vp), un tono per via.

## Gradino all'istante del taglio (dB rispetto al secco, 2,19 V)

| Via (tono) | Secco | Zero, kill | Zero, riapertura | Zero con ritardo reale 0,4 µs | Ritardo del taglio (richiesta al picco) |
|---|---|---|---|---|---|
| SUB (40 Hz) | 2,19 V | −92 dB | −86 dB | −80 dB (0,2 mV) | 6,25 ms |
| KICK (120 Hz) | 2,19 V | −83 dB | −77 dB | −70 dB (0,7 mV) | 2,1 ms |
| MID (500 Hz) | 2,19 V | −70 dB | −64 dB | −58 dB (2,8 mV) | 0,5 ms |
| HIGH (2 kHz) | 2,19 V | −58 dB | −53 dB | −46 dB (11 mV) | 0,13 ms |
| SUPER (10 kHz) | 2,19 V | −44 dB | −38 dB | −32 dB (55 mV) | 0,025 ms |

Il residuo viene dal ritardo della catena per la pendenza della via
all'incrocio: cresce con la frequenza. Sulle vie alte resta un gradino
di decine di mV dentro un programma di acuti: coperto.

## Sonda del click (HP 2 poli ~1,6 kHz) sulle vie basse

Sulle vie basse la sonda lascia passare poco programma, quindi misura
bene il click (sulle vie alte la sonda vede il programma e non
distingue: vale la tabella sopra).

| Via | Programma alla sonda | Secco | Zero |
|---|---|---|---|
| SUB 40 Hz | 0,015 V | 2,18 V (+43 dB sul programma) | 0,015 V (0 dB: nessun click) |
| KICK 120 Hz | 0,012 V | 2,19 V (+45 dB) | 0,043 V (+11 dB; −34 dB rispetto al secco) |

Sul KICK resta un «tic» piccolo: l'onda si ferma allo zero nel punto
più ripido (spigolo, non gradino). È 34 dB sotto lo scoppio di oggi.

## Ritardo del gesto

Il kill aspetta il prossimo zero della sua via: al massimo mezzo
periodo della frequenza più bassa della via. Con gli incroci E
(80 / 170 / 1,2k / 6k Hz) e il sub fino a ~37 Hz: SUB ≤ 13,5 ms, KICK
≤ 6,3 ms, MID ≤ 2,9 ms, HIGH ≤ 0,4 ms, SUPER ≤ 0,08 ms. In media la
metà. Il taglio resta secco: niente dissolvenza.

**Incroci H (dec. 175, todo 290, 2026-11-10)**: 60 / 250 / 1,2k / 8k Hz,
sub fino a ~37 Hz come prima: SUB ≤ 13,5 ms (invariato), KICK ≤ 8,3 ms
(era 6,3), MID ≤ 2,0 ms (era 2,9), HIGH ≤ 0,42 ms, SUPER ≤ 0,06 ms
(`align_math.py --h`). Il tempo massimo di ~20 ms non cambia. Ascolto in
MC-5WAY con gli incroci H: nessun ritardo udibile (dec. 175 b).

## Circuito [PROVVISORIO]

Per ogni via e per ogni lato (10 in tutto): comparatore con isteresi di
pochi mV sulla via (contro i rimbalzi attorno allo zero) → fronte →
flip-flop D (74HC74) che copia la levetta sul pin IN dell'ADG1434. Un
tempo massimo di ~20 ms (oltre il mezzo periodo del SUB) fa scattare
comunque l'interruttore se la via è muta: senza segnale non c'è
gradino. L e R tagliano ognuno al proprio zero. Conto per modulo: 3
comparatori quad (classe LM339/TLV3404), 5 doppi 74HC74, ~40 passivi.
Nessun VCA: il fruscio del modulo non cambia.

## Non fatto

- Programma musicale vero (qui un tono per via): da sentire nel
  prototipo MC-5WAY.
- Charge injection reale dell'ADG1434 (−50 pC): spike di mV, a banco.
- Tempo massimo che scatta: non simulato (scatta solo a via muta).
