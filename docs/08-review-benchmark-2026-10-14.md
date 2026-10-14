# REVIEW DEL PROGETTO CONTRO IL BENCHMARK (sessione 2026-10-14)

> Base: `docs/05` (9 preamp dub) + `docs/07` (benchmark esteso, 41 modelli).
> Formato: Claude fa una domanda alla volta, Filippo risponde. Le risposte
> qui sono **orientamenti di review**, non decisioni bloccate: diventano
> decisioni in `docs/01` solo quando Filippo lo dice, a fine sessione o dopo
> l'eventuale scelta sul fork.

## Mappa iniziale (punti aperti dalla review)

- Forze: F1 combinazione unica (nessuno dei 41 ha DJ + filtro + 5-way +
  matrice FX + mic/mono); F2 headroom +25,4 dBu nel gruppo dei migliori
  (Xone:464 +26, Radius ±27, API 1608 e Model 1 +28); F3 modularità nella
  tradizione Bozak / UREI 1620 / Xone:464; F4 numeri dichiarati.
- Debolezze: D1 S/N ~83 dB A contro ~89-90 dei mixer da club (sopra la
  scena dub: Ligwa ~84); D2 stereo ovunque in una scena mono; D3 filtro
  che auto-oscilla fino a 10-30 Hz senza protezione dei sub nel mixer
  (il Model 1 riduce la RES da solo quando l'HPF scende); D4 complessità
  (109 manopole, ~34-36 VCA).
- Mancanze possibili: M1 crossfader; M2 tasto mono sul master; M3 basso in
  mono; M4 EQ grafico suonato; M5 limiter e mute sul mic; M6 sirena ed eco
  integrati; M7 requisiti di ambiente e trasporto; M8 accoppiamento tra le
  bande del 5-way e gli incroci del DSP esterno.
- Identità: I1 che oggetto è; I2 uscita verso DSP o verso i finali.

## Risposte di Filippo

| # | Domanda | Risposta (2026-10-14) | Conseguenze da discutere |
|---|---|---|---|
| 1 | I1 — gesto centrale: mixer DJ con dub, preamp da sound system, banco da dub live? | **Tutti e tre, in parti uguali**: ibrido voluto, compromessi accettati | ogni mancanza va pesata per tutte e tre le famiglie; la questione del fork resta aperta |
| 2 | I2 — uscita verso DSP o verso i finali? | **Uscita full-range stereo adesso (com'è); modulo «uscite per via» come opzione futura**. Filippo voleva entrambe; temeva la complessità e chiedeva come riprogrammare gli incroci per impianti diversi | il modulo per vie non è un'uscita del 5-way: ritorni FX, mic e mono entrano dopo, nel master. Serve un secondo crossover dopo la somma del master. Metodi analogici per gli incroci: fissi (Mostec), schede a innesto (Klementz, Ras EFX), commutatore a scatti, pot continuo (Moses: tracking difficile). Da progettare dopo la fase 1 (regola 5). M8 (ombra tra kill e crossover del DSP) si attenua con le bande del 5-way vicine agli incroci tipici: entra nella B3 |
| 3 | D2 / M2 / M3 — mono e stereo sul master | **Solo il tasto MONO sul master** (somma L+R su tutte le uscite). Basso mono (fisso o commutabile): no | piccolo circuito nel modulo master; dove agisce (master, booth, rec, cuffie) da definire nel design |
| 4 | M1 — crossfader | **Modulo crossfader opzionale**: il backplane lo prevede, si costruisce dopo se manca. Prova nel prototipo Max con e senza | conseguenza d'ingegneria: il segnale post-fader dei 4 canali deve poter uscire verso il modulo e rientrare prima del DJ bus (loop sul backplane, pin da riservare in S3); assegnazione A / off / B per canale da decidere solo se il modulo nasce |
| 5 | M4 — EQ grafico suonato | **Modulo grafico opzionale**, inseribile più tardi sul master o sul 5-way; il prototipo Max dice se le 5 parametriche bastano | serve un punto d'inserzione (insert) sul backplane, sul master e/o dopo il 5-way: da riservare in S3 insieme al loop del crossfader |
| 6 | M5 — mic dell'MC | **Tasto MUTE sul modulo MIC**; niente limiter (resta da valutare dopo l'ascolto di un MC vero sul prototipo) | aggiunta di Filippo ai comandi della dec. 97; commutazione nella famiglia BBM + ramp 1 ms (dec. 80); MUTE **solo sul MIC**, non sul MONO (risposta di Filippo) |
| 7 | D3 — auto-oscillazione del filtro nei sub-bassi | **Per ora com'è: protezione delegata al DSP esterno, da scrivere come requisito d'impianto** | fatti chiariti: accade con RES ≥ 90 % e FREQ nel primo ~10-15 % (≤ ~40 Hz, nota −6 semitoni), in HPF e in LPF; è il gesto dub dell'«affondo», non un errore. Alternative restate aperte: RES che cala sotto ~40 Hz (tocca dec. 102), passa-alto fisso ~20 Hz sul master (perdite: contenuto < 25 Hz, piccolo ritardo di fase; non ferma le armoniche a 30-45 Hz se l'overdrive satura l'onda a 15 Hz), range LPF accorciato (l'HPF deve restare a 10 Hz per essere trasparente a riposo, dec. 74) |
| 8 | M7 — ambiente e trasporto | **Sound system all'aperto**: flight case, connettori robusti, pot sigillati, telaio rigido, tropicalizzazione (vernice protettiva sulle schede), lavoro fino a 40 °C ambiente, pannello protetto da polvere e liquidi | conseguenze d'ingegneria da verificare: deriva del converter e dello shaper finora verificate fino a 50 °C *interni*: con 40 °C fuori l'interno sale oltre (budget termico PSU fanless, S1 §5, da rifare a 40 °C); vernice sui nodi ad alta impedenza (phono 47k, ingresso MONO 1 MΩ, servo); condensa al cambio di temperatura; scelta di pot e connettori nella sessione hardware (voce 40) |
| 9 | M6 — sirena ed eco integrati | **Tutto esterno, com'è**: sirene nei moduli MONO, eco nei loop FX | un modulo sirena analogico resta possibile dopo, come MONO qualunque sul backplane |
| 10 | D1 — rumore di fondo contro i mixer da club | **Accettato com'è**: S/N ~83 dB A a filtri spenti (~79 con 4 filtri) contro ~89-90 dei mixer da club; target −78 dBu della dec. 89 invariato | motivo: sul sound system all'aperto (risposta 8) il soffio resta a ~25-35 dB SPL, sotto il rumore d'ambiente; si sente solo in cuffia nelle pause, a casa a basso volume, o in registrazione alzata dopo |
| 11 | Colore dell'uscita (trasformatori Isonoe/API/Euphonia, valvole Radius 4V) | **Pulito com'è.** Filippo: il NASTRO del 5-way è stato messo lì apposta per questo | precisazione: il NASTRO colora solo il DJ bus; ritorni FX, mic e mono si sommano dopo e restano puliti (un trasformatore d'uscita colorerebbe tutto) |
| 12 | Numero di canali DJ (Xone:464: 6 stereo + 4 mono; Model 1 e Xone:96: 6; rotary: 4) | **4 canali DJ, com'è** (backplane non predisposto per 6) | — |
| 13 | D4 / I1 — fork del progetto? | **Nessun fork.** Un solo progetto; **tutto predisposto** per aggiungere i moduli discussi senza grosse modifiche (uscite per via, crossfader, EQ grafico, sirena come MONO) | le «versioni» diventano configurazioni dello stesso mixer; ordine di costruzione invariato (fase 1, poi fase 2) |

## Sintesi delle conseguenze (da trasformare in decisioni se Filippo conferma)

Aggiunte al design:
- tasto MONO sul master (somma L+R; punti d'azione da definire);
- tasto MUTE sul modulo MIC (non sul MONO), famiglia BBM + ramp 1 ms;
- requisiti d'ambiente da sound system all'aperto (40 °C, tropicalizzazione,
  pot sigillati, connettori robusti, flight case, pannello protetto);
- requisito d'impianto scritto in SPECIFICA: il DSP esterno protegge i sub
  (auto-oscillazione del filtro fino a ~15-30 Hz, feedback FX, GROWL).

Predisposizioni nel backplane (S3) e nell'alimentatore, senza costruire i
moduli:
- loop post-fader dei 4 canali verso un modulo crossfader e ritorno prima
  del DJ bus;
- punti d'inserzione per un EQ grafico sul master e/o dopo il 5-way;
- presa dopo la somma del master per un modulo «uscite per via» con crossover
  proprio (incroci a scatti o a schede);
- slot MONO per un eventuale modulo sirena (già esistente);
- margine di corrente nell'alimentatore per questi moduli.

Restano com'è: uscita full-range stereo, rumore (target dec. 89), uscita
pulita (colore dal NASTRO), 4 canali DJ, sirena ed eco esterni, nessun
limiter sul mic, niente basso mono.
