# MISTO — inventario dei circuiti di comando e di servizio [APERTO]

Data: 2026-11-09 (todo 263). Base: i design doc della versione analogica
alla data. Nessuna simulazione, nessun preventivo: conteggi letti dai
documenti, costi e spazio sono STIMA di Claude.

Griglia del 6/11, per ogni circuito: **com'è oggi** · **passivo** (si può
togliere l'elettronica?) · **col chip** (cosa fa il chip al suo posto).
Più due colonne: cosa si risparmia, cosa si sente.

Regola di lettura (M2, condizione 1): il chip legge manopole, bottoni e
uscite di comparatori; scrive CV e livelli logici. Non legge e non scrive
mai l'audio.

## 1. Cosa resta analogico in ogni caso

Tutto il percorso del segnale, e i comandi che oggi stanno sul segnale:

- GAIN dei canali e dei ritorni (pot doppio, dec. 162);
- EQ isolator dei canali (pot doppi senza contatto di fondo corsa, dec. 127);
- EQ di FX-SEND, ritorni, MIC e MONO; LEVEL del FX-SEND;
- GAIN, WIDTH, GROWL e NASTRO del 5-way (pot doppi sul segnale, §5bis e §4.3);
- DRIVE del filtro (pot doppio lineare sul segnale, todo 212);
- BLEND e LEVEL del CUE; GAIN, EQ e SEND di MIC e MONO;
- limiter fisso del MIC (dec. 145): è dinamica sull'audio.

Questi comandi sono passati al pot doppio per avere meno rumore e meno VCA
(dec. 162: −16 VCA; todo 212: −4 VCA). Riportarli sotto il chip vuol dire
rimettere VCA nel segnale: rumore e costo in più. Vedi §4, domanda 1.

## 2. Circuiti di comando che il chip può prendere

| # | Circuito | Dove | Quanti | Com'è oggi | Passivo | Col chip | Si risparmia | Cosa si sente |
|---|---|---|---|---|---|---|---|---|
| 1 | Shaper del REROUTE e self-feedback | FX-RET ×4 | 16 CV | shaper a diodi, 3 rami, pot rovescio (sistema-shaper §3) | no: la law −100 dB non si fa con un pot | il chip calcola la law, un DAC scrive la CV | diodi e reti di resistenze; trimmer di zero e fondo scala | law esatta anche sotto −30 dB (oggi fino a +6,9 dB d'errore) e ferma con la temperatura |
| 2 | Shaper del fader (dec. 126) | canali ×4, ritorni ×4 | 8 CV | shaper a diodi, 3 rami, fader rovescio | no | law del fader in tabella; il dip della levetta HPF/OFF/LPF (dec. 163) diventa un'aggiunta alla CV | shaper e le due reti RC del dip | curva del fader cambiabile via USB; dip uguale su tutti i canali |
| 3 | Shaper MASTER e BOOTH | master | 2 CV | shaper a 4 rami + offset (MASTER), shaper del fader (BOOTH) | no | law in tabella, scatto al centro letto come 0 dB esatti | 2 shaper, trimmer d'offset | sparisce l'errore fino a +3 dB fra −16 e −28 dB |
| 4 | Shaper della frequenza del filtro | filtro | 2 CV | shaper a diodi + converter esponenziale con compensazione PTAT (filter §4) | no | law Xone:96 in tabella; la deriva del converter si corregge con un sensore di temperatura | shaper; pre-distorsione a banco (≤ 40 mV) e i suoi trimmer | spariscono i ginocchi a −12 % (5 %) e +14 % (95 %) a caldo |
| 5 | Shaper della RES del filtro | filtro | 2 CV | 2 rami + raddrizzatore di precisione, fischio dal 93,4 % (dec. 153) | no | law e punto del fischio in tabella | shaper e raddrizzatore | punto del fischio cambiabile via USB |
| 6 | Shaper della POSITION | 5-way | 5 CV | shaper a 3 rami θ → Vcm del JFET, un trimmer per banda (shaper §3, five-way §4.2) | no | law e campo di ogni banda in tabella | 5 shaper, 5 trimmer | campo delle POSITION cambiabile via USB; errore oggi +3,6 % a 50 °C |
| 7 | Trim di law delle coppie di VCA | master, booth (montati); piazzole su ~25 coppie | 4 trimmer + piazzole | trimmer di scala 200 Ω e d'offset 50k per coppia, abbinamento dei chip su un jig (vca-trim §3.2, §6) | — | correzione per chip in tabella: due numeri misurati a banco e salvati via USB | trimmer di law; forse l'abbinamento dei chip | stereo entro 0,05 dB fino a dove la law del chip è dritta |
| 8 | Trim di simmetria dei VCA | ogni VCA | 54 trimmer | cursore di un 50k fra ±15 V → 150k → pin 4 (vca-trim §3.1) | — | possibile con un canale DAC per chip; la taratura resta a orecchio o con REW | poco: 54 canali DAC costano più di 54 trimmer | niente | 
| 9 | Kill allo zero del 5-way (dec. 164) | 5-way | 5 vie × 2 lati | comparatore con isteresi + 74HC74 + tempo massimo (five-way §8.11) | no | i comparatori restano; il chip legge le loro uscite e comanda l'ADG1434 | 74HC74 e la logica del tempo massimo | ritardo massimo e levetta a molla cambiabili via USB |
| 10 | Rampe e logica dei bottoni | canali (CUE, assign ×4), master (MONO), MIC (MUTE), levette | ~30 bottoni e levette | ritenuta, LED, rampa RC sul pin di controllo (fx-send §2, dec. 80) | in parte: levette a ritenuta meccanica | ritenuta, LED, antirimbalzo e rampe nel chip | RC e logica sparsa | rampe uguali ovunque; durata cambiabile via USB |
| 11 | Meter (dec. 81, 90, 116) | canali, ritorni, 5-way, master | 11 barre, 133 segmenti | detector a superdiodo + hold → 13 LM3915 + LM339 per il viola; trimmer di calibrazione e di release (metering §2-4) | no | detector analogici restano; il chip legge la tensione di hold e accende i LED (driver a corrente costante) | 13 LM3915, LM339, trimmer di calibrazione e di release | ballistica e soglie cambiabili via USB; calibrazione identica fra canali senza trimmer |
| 12 | Supervisor, AC_OK, ventole (psu-esterno §2.5, §4.4) | master / box | 1 | comparatori e logica per mute all'accensione e allo spegnimento; termostato delle ventole | no | il chip del master fa supervisor e termostato | poca logica | niente, se il mute resta più veloce del calo dei rail |

Conteggio: **35 CV** oggi fatte da shaper a diodi (16 + 8 + 2 + 2 + 2 + 5).
Lo shaper doc ne contava ~26 prima dei fader (dec. 126): oggi sono ~9 quad
op-amp.

## 3. Costo e spazio [STIMA, deduzione di Claude]

**Per ogni CV.** Shaper di oggi: 1 sezione di op-amp, 2-3 diodi, 6-8
resistenze, a volte un trimmer: ~1-3 €. Col chip: 1 canale di DAC, 1
sezione di op-amp per scala e filtro, 2-3 resistenze: ~1-3 €. **Sulla
singola CV il costo resta circa uguale.** L'op-amp resta in tutti e due i
casi.

**Per modulo, in più:** il chip (classe Raspberry Pi Pico su zoccolo, ~5 €),
un multiplexer o un ADC per leggere le manopole, il riferimento di
tensione, la presa USB, un regolatore digitale: ~10-20 € a modulo, una
quindicina di moduli.

**Dove si guadagna davvero:**

- **taratura**: dei ~253 trimmer del mixer (docs/09) il chip ne toglie
  ~60-80 (shaper, law, meter). I 54 di simmetria restano. Sono giorni di
  banco in meno, non molti euro;
- **meter**: il comparatore del viola e i trimmer di calibrazione e di release (gli LM3915 diventano driver di LED, stessi pezzi);
- **precisione**: curve esatte su tutta la corsa e ferme con la
  temperatura (40 °C all'aperto, dec. 111);
- **valori cambiabili via USB** quasi gratis per tutto ciò che è già una CV.

**Spazio:** gli shaper sono piccoli (SMD). Il guadagno di spazio sta nei
trimmer tolti e nei meter. Il chip, i DAC e la presa USB ne occupano una
parte. Saldo atteso: poco, da contare scheda per scheda col generatore.

**Spazio, contato il 2026-11-09** (`misto/script/area_impronte.py` col Python di KiCad, `pcbnew` sulle
PCB generate di al commit e4f6f29). Impronte di shaper e trim di law
(resistenze, diodi, trimmer, condensatori sulle reti SN, SJ, SH, NP, LT,
OF, POT), senza gli op-amp:

| Scheda | Impronte totali | Di shaper e trim | Col chip [STIMA] | Saldo |
|---|---|---|---|---|
| FX-RET reroute (4 CV) | 225 | 76 | 20 celle DAC + 12 blocco chip | −44 |
| FX-RET segnale (fader) | 199 | 19 | 5 | −14 |
| MASTER segnale (MASTER, BOOTH) | 283 | 40 | 10 + 12 | −18 |
| Canale (fader) | 193 | 18 | 5 + 12 | −1 |
| Filtro (4 CV, non generato) | — | ~64 | 20 + 12 | ~−32 |
| 5-way POSITION (5 CV, non generato) | — | ~75 | 25 + 12 | ~−38 |

Totale: **~150 impronte in meno su tutto il mixer**, circa mezza scheda
(una 100 × 220 ne porta ~280 sui due lati). Nessuna scheda sparisce: il
ritorno FX resta su due schede (199 + 225 − 58 = 366 > 280), il canale resta
su una. Il pannello non cambia: lo dimensionano le manopole, che restano
le stesse (M3). I meter non danno spazio: i driver di LED del chip (16
uscite) sono tanti quanti gli LM3915 (10 segmenti).

**Prima conclusione.** Il misto non abbassa molto il costo dei pezzi.
Abbassa il lavoro di taratura e rende le curve esatte e modificabili. Il
risparmio vero di costo e spazio sta nelle opzioni di `cheap/`, che
restano a parte (M3).

## 4. Domande per Filippo: chiuse il 2026-11-09

1. GROWL, NASTRO e DRIVE restano sul segnale, fuori dall'USB (M7).
2. Incroci del 5-way e dell'isolator fissi (M8).
3. Il misto va avanti per la taratura e la precisione, non per costo e
   spazio (M6).

## 5. Punti tecnici da verificare (ingegneria, Claude)

Risposte di primo giro (gradini, ritardo, rumore digitale, guasto,
ricambio) in `03-blocco-comando.md`, sul caso del FX-RET.

- **Gradini (M2, condizione 3).** Con le CV progettate a livello di volt e
  divise per 10 al VCA (sistema-shaper §2), un DAC a 12 bit su ~12 V dà
  ~0,3 mV al pin: ~0,05 dB a 6,1 mV/dB. Il pot letto a 12 bit nel tratto
  ripido di una curva (fader in fondo, reroute vicino a −100) può dare
  passi più grandi: serve interpolazione nel firmware e un filtro RC.
- **Ritardo.** Lettura e scrittura a ~1 kHz danno ~1 ms fra il gesto e la
  CV. Da verificare sui tagli veloci col fader.
- **Rumore digitale.** Clock e USB vicino all'audio: massa digitale
  separata (sistema-grounding), chip lontano dal segnale, USB isolata o
  scollegata durante la serata.
- **Guasto del chip.** Stato sicuro delle CV quando il chip si spegne o si
  riavvia (per esempio: fader e reroute chiusi, master fermo).
- **Ricambio (M2, condizione 2).** Stesso chip in ogni modulo; il firmware
  riconosce il modulo da un piedino di codice, così un ricambio solo serve
  tutti.
