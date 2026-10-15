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
| LOW, LOW-MID, MID-HIGH, HIGH | banda spenta | 0 dB (piatto) | +6 dB |
| FADER | muto | −12 dB [PROVVISORIO] | 0 dB |

- Il centro (50 %) di ogni manopola vale il detent del pannello vero.
  Per tornarci: clic sulla manopola, poi tasto Canc (Delete). Live la
  riporta al valore iniziale.
- GAIN scende lineare in dB: a 25 % vale −50 dB. Sul pannello vero il
  GAIN ha la stessa law (shaper del VCA, `cdj-line-channel.md` §3.2).
- **INCROCI**: A = 150 / 500 / 2500 Hz (partenza), B = 100 / 630 /
  4000 Hz. Il cambio passa con una dissolvenza di 20 ms, senza click.
  Serve per la voce B7: confrontali a orecchio.
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
   - a destra: GROWL, NASTRO e il selettore CROSSOVER.
3. CROSSOVER esiste solo nel prototipo (B3): A = design attuale
   90/350/1,2k/3,5k; B = Jah Tubbys Devastator 80/200/1,2k/6k; C = JB
   Audio 75/190/2,2k/8k; D = Speakerplans 80/220/1,5k/7k. Cambia i
   confini dei KILL, non l'EQ.
4. Parte trasparente: tutte le vie aperte, GAIN e POS al centro, GROWL
   e NASTRO a zero.
5. Livello: 0 dBu = −12 dBFS di picco, come gli altri dispositivi. Con
   boost forti l'uscita supera 0 dBFS e la scheda audio satura. Abbassa
   il fader del gruppo, che sta dopo il dispositivo. Non abbassare
   l'ingresso: GROWL e NASTRO cambiano carattere col livello.
