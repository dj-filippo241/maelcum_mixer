# Montaggio in Live — prototipo Max (P0 e seguenti)

Questa guida vale per ogni dispositivo `MC-*` del prototipo. Ogni fase
aggiunge il suo file; la procedura resta questa.

## 1. Metodo veloce: il file `.amxd` (prova questo per primo)

1. Apri Live 12 Suite e un set nuovo.
2. Nel Finder apri la cartella `maelcum_mixer/proto-max/`.
3. Trascina `MC-CHANNEL.amxd` su una traccia audio di Live.
4. Il dispositivo compare in basso, con 5 manopole, un fader e il
   selettore degli incroci.
5. Copia il file nella tua User Library, se vuoi ritrovarlo nel browser
   di Live.

Se Live segnala un errore, o il suono non passa, vai al §3.

## 2. Il pannello di MC-CHANNEL

| Comando | 0 % | 50 % | 100 % |
|---|---|---|---|
| GAIN | muto | 0 dB | +10 dB |
| LOW, LOW-MID, MID-HIGH, HIGH | banda spenta (ISOLATOR) o tagliata (SERIE) | 0 dB (piatto) | +6 dB |
| FADER | muto | −12 dB [PROVVISORIO] | 0 dB |

- Il centro (50 %) di ogni manopola vale il detent del pannello vero.
  Per tornarci: clic sulla manopola, poi tasto Canc (Delete). Live la
  riporta al valore iniziale.
- GAIN scende lineare in dB: a 25 % vale −50 dB. Sul pannello vero il
  GAIN ha la stessa law (shaper del VCA, `cdj-line-channel.md` §3.2).
- **INCROCI**: A = 150 / 500 / 2500 Hz (partenza), C = 150 dolce /
  350 / 3150 Hz, D = 150 dolce / 700 / 3150 Hz (B scartata con A, dec.
  114). Il cambio passa con una dissolvenza di 20 ms, senza click.
  Serve per la voce B7: confrontali a orecchio.
- **CURVA**: LINEARE (pot di serie) o PIONEER (curva ideale dei DJM,
  solo per sentire se la differenza conta).
- **EQ TIPO** (B5, 2026-10-15): ISOLATOR = l'EQ di progetto (dec. 105).
  SERIE = l'EQ in serie archiviato, campane a 70 / 250 / 1k / 5k Hz: a
  0 % LOW taglia ~−29 dB, i medi scavano una buca stretta, HIGH scurisce
  (−3 dB a 10 kHz, −9 a 20 kHz). Nessuna banda spegne: il silenzio è il
  fader. INCROCI e CURVA agiscono solo su ISOLATOR. Dissolvenza 20 ms.
- La law del FADER non è decisa: qui è una curva da pot audio tipico.

Per suonare 4 canali: un `MC-CHANNEL` su ognuna delle 4 tracce.

## 3. Metodo di riserva: la patch `.maxpat`

Serve solo se il `.amxd` non si apre.

1. In Live, dal browser: Max for Live → Max Audio Effect. Trascinalo su
   una traccia.
2. Sul dispositivo clicca l'icona di modifica (Edit). Si apre Max.
3. In Max: File → Open → `proto-max/MC-CHANNEL.maxpat`.
4. Nella patch aperta: Cmd+E per sbloccarla, Cmd+A, Cmd+C.
5. Torna alla finestra del Max Audio Effect, cancella gli oggetti che
   ci sono (Cmd+A, Backspace), poi Cmd+V.
6. Collega `plugin~` → `gen~` → `plugout~` se le linee mancano.
7. Salva (Cmd+S) con il nome `MC-CHANNEL`.

## 4. Cosa controllare la prima volta (2 minuti)

1. **Il codice si compila.** Doppio clic su `gen~` in modalità Edit: se
   la finestra del codice mostra righe rosse, mandami il testo
   dell'errore (anche una foto).
2. **Passa il suono.** Tutte le manopole al 50 % e fader al 100 %: il
   suono deve restare identico a quello senza il dispositivo. Prova
   con il tasto di attivazione del dispositivo (il pallino giallo in
   alto a sinistra).
3. **Il silenzio.** Le quattro bande a 0 %: deve sparire tutto.
4. **La CPU.** Guarda l'indicatore CPU in alto a destra in Live, con
   4 dispositivi accesi. Dimmi il numero.

## 5. Per gli sviluppi (nota per Claude)

I file `MC-*.genexpr`, `.maxpat` e `.amxd` NON si modificano a mano:
si rigenerano con `python3 proto-max/coefficienti/genera.py`. Prima di
consegnare: `verifica.py` (modello contro LTspice) e `prova_gen.py`
(codice gen~ contro modello) devono dire PASS.

## MC-FILTRO (P1)

1. Trascina `MC-FILTRO.amxd` sulla stessa traccia, **dopo** MC-CHANNEL.
2. Pannello: HPF FREQ, HPF RES, HPF DRIVE, LPF FREQ, LPF RES, LPF
   DRIVE; MODO HPF / OFF / LPF; CORE OTA (a′) / PULITO (c-B); PENDENZA
   Butterworth / Linkwitz-Riley / Bessel.
3. Parte in OFF: suono invariato. Metti MODO su LPF e abbassa LPF FREQ.
4. RES oltre il 90 %: il filtro fischia da solo, anche senza musica.
5. Livello: 0 dBu del mixer = −12 dBFS di picco. Il core OTA cambia
   carattere col livello: con GAIN di MC-CHANNEL più alto la risonanza
   si schiaccia di più.


## MC-5WAY (P2)

1. Il 5-way sta sul DJ BUS, dopo la somma dei canali. In Live: seleziona
   le tracce dei canali, Cmd+G per raggrupparle, poi trascina
   `MC-5WAY.amxd` sulla traccia del gruppo. Con una traccia sola va bene
   anche sulla traccia stessa, dopo MC-FILTRO.
2. Pannello, da sinistra:
   - riga in alto: KILL SUB, KICK, MID, HIGH, SUPER (ON = via aperta,
     KILL = via tagliata di netto, col click come l'interruttore vero);
   - colonne EQ1-EQ5: GAIN (centro = piatto, destra = boost, sinistra =
     taglio fino al notch), POS (frequenza della campana), WIDTH
     Q3 stretta / Q1 media / Q0.5 larga;
   - a destra: GROWL, NASTRO e il selettore CROSSOVER;
   - GROWL VER (solo prototipo): DEC.99 = il GROWL del design, LIBERO =
     spinta e miscela insieme, il basso cresce;
   - NASTRO VER (solo prototipo): OGGI / COMPLETO / EXCITER / CLASSE A /
     LIBERO, tutte comandate dalla manopola NASTRO. LIBERO = il NASTRO di
     oggi con la spinta che sale con la manopola: piu sporco, e il
     programma piano cresce.
3. CROSSOVER esiste solo nel prototipo (B3): A = design attuale
   90/350/1,2k/3,5k; B = Jah Tubbys Devastator 80/200/1,2k/6k; C = JB
   Audio 75/190/2,2k/8k; D = Speakerplans 80/220/1,5k/7k; E = gli
   incroci del tuo impianto 80/170/1,2k + 6k. Cambia i confini dei
   KILL, non l'EQ.
4. Parte trasparente: tutte le vie aperte, GAIN e POS al centro, GROWL
   e NASTRO a zero.
5. Livello: 0 dBu = −12 dBFS di picco, come gli altri dispositivi. Con
   boost forti l'uscita supera 0 dBFS e la scheda audio satura. Abbassa
   il fader del gruppo, che sta dopo il dispositivo. Non abbassare
   l'ingresso: GROWL e NASTRO cambiano carattere col livello.

## P3 — FX e master (MC-SEND, MC-BUS, MC-RET, MC-MASTER)

I pedali sono effetti veri di Live. Ogni bus FX ha una traccia sua.

1. **Mandate**: su ogni traccia canale trascina `MC-SEND.amxd` **tra**
   MC-CHANNEL e MC-FILTRO. L'audio del canale passa intatto. Comandi:
   EQ LOW, EQ HIGH, LEVEL (al pedale) e i quattro bottoni FX1-FX4.
2. **Tracce FX**: crea 4 tracce audio (non tracce Return), una per bus.
   Su ciascuna:
   - `MC-BUS.amxd` per primo, e scegli il suo BUS (FX1 sulla prima
     traccia, FX2 sulla seconda, e così via);
   - poi il tuo effetto (Echo, Reverb, quello che vuoi). Per il gesto dub
     metti l'eco al **100 % wet** e, dopo l'eco, un **Saturator**: fa la
     parte della saturazione del pedale vero;
   - per ultimo `MC-RET.amxd`: GAIN, EQ LOW, EQ HIGH, meter e i quattro
     REROUTE (> FX1 … > FX4: il bus verso cui rimanda, anche se stesso).
   - Monitor della traccia su **In**, ingresso **No Input**: il suono
     arriva da MC-BUS, non dalla scheda audio.
3. Il **fader della traccia FX** è il fader del ritorno. Il reroute sta
   prima del fader: abbassi il fader e il feedback continua.
4. **Master**: trascina `MC-MASTER.amxd` sulla traccia Master. MASTER a
   80 % = 0 dB (detent), MONO somma L e R.
5. **Protezione per le orecchie** (solo per la prova, non fa parte del
   design): un Limiter di Live per ultimo sul Master. Sopra unity, senza
   Saturator, il loop sale fino al rail del bus (+11,5 dBFS).
6. Meter di MC-RET e MC-MASTER: 0 in cima = +24 dBu, −24 = 0 dBu. La
   striscia sottile accanto è il clip (latch di mezzo secondo).

## P4 — Mic (MC-MIC)

1. Crea una traccia audio per il microfono. Ingresso: il canale della
   scheda audio dove è collegato il mic, **mono**. Monitor su **In**.
   Uscita: Master.
2. **Preamp della scheda audio al minimo.** Il guadagno lo dà la manopola
   GAIN di MC-MIC (30-60 dB, come il modulo vero). Se il preamp della scheda
   è alto, il mic suona più forte di quanto dice la manopola.
3. Trascina `MC-MIC.amxd` sulla traccia. Comandi: GAIN, EQ LOW, EQ HIGH,
   FX1-FX4 (quanto mic va a ciascun bus FX di P3), MUTE e il LED.
4. LED: grigio = niente, verde = segnale ok, giallo = vicino al clip,
   rosso = clip (resta acceso mezzo secondo). Guarda il segnale prima
   dell'EQ e prima del MUTE.
5. MUTE spegne il mic verso il Master e verso i bus FX insieme.
6. Il fader della traccia non fa parte del modulo (il modulo vero non ha
   fader): lascialo a 0 dB.
7. **Cuffie, non casse**: con un mic aperto vicino alle casse parte il
   larsen. Prova il MUTE proprio lì.

## Versioni semplici (MC-CHANNEL-S, MC-FILTRO-S, MC-5WAY-S)

Scelte d'ascolto di Filippo del 2026-10-21, fissate nel codice. I
selettori non ci sono più; i comandi del pannello vero restano.

| Dispositivo | Scelte fissate | Comandi |
|---|---|---|
| `MC-CHANNEL-S` | ISOLATOR, INCROCI A 150/500/2500, CURVA PIONEER | GAIN, 4 bande, FADER |
| `MC-FILTRO-S` | CORE PULITO (c-B), PENDENZA BUTTERWORTH | FREQ, RES, DRIVE ×2, MODO, LIMITATORE (2+2 / 3+3, da ascoltare) |
| `MC-5WAY-S` | CROSSOVER E 80/170/1,2k/6k, GROWL LIBERO, NASTRO EXCITER | KILL, GAIN, POS, WIDTH ×5, GROWL, NASTRO |

Si montano come gli originali: al posto di MC-CHANNEL, MC-FILTRO e
MC-5WAY sulla traccia del canale. Il codice calcola solo la versione
scelta: righe gen~ 1029 → 329 (canale), 590 → 374 (filtro), 1587 → 815
(5-way).

Generatori: `genera.py`, `genera_filtro.py`, `genera_5way.py` con
`--semplice`. Senza l'opzione i file originali escono identici. Prova:
ogni copia contro l'originale impostato sulle stesse scelte, con le
manopole in movimento e a fondo corsa: scarto 0 su 8 casi (picco fino a
1,5 dBFS).

Attenzione al livello: GROWL LIBERO + NASTRO alti superano 0 dBFS (prova
con picchi d'ingresso a circa +8 dBu: uscita +3,7 dBFS). Sopra 0 dBFS
l'uscita della scheda taglia l'onda.
