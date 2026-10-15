# Prototipo Max for Live — piano v0.2 (2026-10-14) [APPROVATO da Filippo il 2026-10-14: decisioni in §6]

Sostituisce il piano v0.1 del 2026-09-24 (`piano-v0.1.md`, archiviato).
Todo 1. Base: decisione 78 (prototipo musicale prima del millefori, Ableton
Live Suite) e lo stato del design alle decisioni 99-113.

## 0. Perché adesso, e cosa cambia dal v0.1

Il design su carta e in simulazione è completo per tutti i moduli. Restano
aperte le decisioni che vogliono l'orecchio (lista B di `docs/02`), e gli
acquisti aspettano il prototipo. Il prototipo è quindi il collo di
bottiglia: ogni fase chiude delle voci B.

Cambia rispetto al v0.1:

| v0.1 | v0.2 | Origine |
|---|---|---|
| EQ di canale a 4 bande in serie, kill −30 dB | **isolator a 4 bande**: ogni banda dal silenzio a +6 dB, contatto di fondo corsa | dec. 105 |
| Filtro con mux single-path / serie da scegliere | un percorso per canale, interruttore HPF / OFF / LPF | dec. 101 |
| SVF ideale in gen~ | core che imita il **chip reale**: picco di risonanza che cala col livello, oscillazione a ~+5 dBu, nota che cala ~6 semitoni tra 90 e 100 % di RES; A/B con il core pulito a VCA | dec. 109-110, B1 |
| Drive 5-way unico (taper dec. 24) | **GROWL** (solo sub e bassi, sotto 350 Hz) e **NASTRO**, in parallelo al pulito, volume fermo | dec. 99 |
| Overdrive filtro candidato | tosatore in parallelo, griglia di `d5-chain.cir` | dec. 99, 110 |
| FX: matrice a 3 reroute | matrice 16 VCA con self-feedback; in mandata solo LEVEL; GAIN sul ritorno | dec. 91, 108 |
| — | **tasto MONO** sul master, **MUTE** del mic, mic con un MC vero | dec. 111 |
| — | prova richiesta dalla review: le 5 parametriche del 5-way bastano senza EQ grafico? (la prova del crossfader è tolta da Filippo il 2026-10-14; il modulo resta predisposto) | dec. 111 |
| Patch .maxpat disegnate a mano | **DSP in codice `gen~` testuale** dentro patch minime (§3) | ingegneria |

La voce B5 (centri dell'EQ in serie 70 / 250 / 1k / 5k Hz) non è più
l'EQ di progetto dopo la dec. 105: la scelta principale è B7 (incroci
dell'isolator). 2026-10-15, Filippo: B5 resta come opzione d'ascolto,
possibile variante di MC-CHANNEL.

## 1. Cosa valida e cosa no (invariato, dec. 78)

**Valida a orecchio**: gesto, law delle manopole, curve, carattere dei
saturatori, risonanza, scelte di banda, workflow dub mentre mixi.

**Non valida**: rumore, headroom reale, THD dei componenti, tracking dei pot,
derive termiche. Quelle restano al millefori e alle misure.

Regola: ciò che approvi a orecchio diventa requisito del circuito
corrispondente, con una voce in `docs/01`.

## 2. Fasi, in ordine di valore

Ogni fase finisce con un set di Live suonabile, una sessione d'ascolto tua e
le risposte alle voci B della fase.

### P0 — Canale (1 sessione mia)

> **[2026-10-14: COSTRUITO e verificato fuori da Max** (`proto-max/RISULTATI-P0.md`):
> `MC-CHANNEL.amxd` generato da `proto-max/coefficienti/genera.py`; modello
> contro LTspice ≤ 0,07 dB (incroci A) e ≤ 0,44 dB (B); codice gen~ contro
> modello ≤ 0,002 dB. FINDING: la banca gira a 4× (oversampling halfband),
> senza la bilineare sbagliava fino a 3,2 dB. Il «trim» del piano coincide
> con GAIN: il canale non ha un trim separato. Caricato in Live da Filippo
> il 2026-10-14: compila, trasparente al centro, silenzio a bande chiuse,
> CPU 4 % con 4 dispositivi. Resta l'ascolto per B7.]

`MC-CHANNEL` ×4: trim, GAIN (law −∞ … 0 … +10), **isolator a 4 bande**
(incroci di partenza 150 / 500 / 2500 Hz, +6 dB, law lineare, silenzio a
fondo corsa), fader.

Chiude a orecchio:
- **B7**: incroci, boost e law dell'isolator. Il pannello del prototipo
  porta un selettore 150 / 500 / 2500 contro 100 / 630 / 4000 Hz, per il
  confronto con un DJM a memoria.
  [2026-10-14 sera, dec. 114: +6 e GAIN confermati; A e B scartate; il
  selettore porta A, C = 150 dolce / 350 / 3150 Hz e D = 150 dolce / 700 /
  3150 Hz (come i mixer DJ, docs/09),
  `proto-max/RISULTATI-P0.md` §Variante C. Curva: solo pot di serie.]

Serve anche a montare l'infrastruttura (procedura di montaggio, set di
prova): le fasi dopo costano meno.

### P1 — Filtro (2 sessioni)

`MC-FILTRO` (pannello: FREQ, RES, overdrive, law Xone:96, dec. 102) e un
core per canale.

Chiude a orecchio:
- **B1**: carattere del filtro, core OTA (a′) contro core pulito a VCA
  (c-B), con un interruttore A/B in tempo reale. Il core (a′) del
  prototipo riproduce i quattro numeri della dec. 110.
- **B2**: pendenza a 4 poli, Butterworth / Bessel / Linkwitz-Riley in A/B.
- **B6**, parte filtro: la griglia dell'overdrive.

Sblocca il todo 11 (prototipo del filtro su millefori), fermo su B1.

[2026-10-15: P1 COSTRUITO — `MC-FILTRO` con FREQ, RES, DRIVE, MODO,
CORE (a′)/(c-B), PENDENZA; core tarato sul D5 (≤ 0,3 dB, fischio
≤ 0,6 dB / 0,3 st), overdrive su od2-chain (≤ 0,1 dB), gen~ contro
modello PASS; `proto-max/RISULTATI-P1.md`. Manca l'ascolto di Filippo.]

### P2 — 5-way (2 sessioni)

`MC-5WAY` sul gruppo DJ BUS: 5 bande con kill a interruttore, EQ creativo
position / width, GROWL e NASTRO, riferimento interno −6 dB (dec. 73).

Chiude a orecchio:
- **B3**: frequenze delle 5 bande (ora ~90 / 350 / 1,2k / 3,5k Hz).
- **B6**, parte 5-way: carattere e curve di GROWL e NASTRO.
- **EQ grafico**: le 5 parametriche bastano da sole? (dec. 111)

[2026-10-15: P2 COSTRUITO — `MC-5WAY` con KILL per via, EQ a 5 campane
(GAIN / POS / WIDTH), GROWL e NASTRO, selettore CROSSOVER A-E per B3
(benchmark + E = impianto di Filippo 80/170/1,2k + 6k); dopo tre ascolti:
GROWL VER DEC.99 / LIBERO, NASTRO VER OGGI / COMPLETO / EXCITER / CLASSE A /
LIBERO, NASTRO log all'85 %; tutto contro LTspice, gen~ PASS 203/203 sui due
canali; `proto-max/RISULTATI-P2.md`. Ascolto di Filippo in corso.]

### P3 — FX e master (2 sessioni)

`MC-FX` (4 bus, ritorno con GAIN, matrice di feedback 16 VCA con
self-feedback, pedale = segnaposto: delay e saturazione semplici) e
`MC-MASTER` (MASTER LEVEL, tasto MONO, meter a 6 zone con le soglie della
SPECIFICA §11).

Verifica: dove parte il feedback rispetto a GAIN e reroute (dec. 108), se
il loop resta governabile con le mani, e la latenza tra i dispositivi
(`send~` / `receive~`: un buffer di ritardo, da sentire).

[2026-10-15: P3 COSTRUITO — scelta di Filippo: pedali = effetti veri di
Live. Quattro dispositivi invece di uno: `MC-SEND` (EQ2, LEVEL, FX1-4 per
canale), `MC-BUS` → effetto di Live → `MC-RET` (GAIN, EQ2, meter, 4
REROUTE pre-fader) su 4 tracce FX, `MC-MASTER` (MASTER, MONO, meter).
EQ2 contro LTspice ≤ 0,13 dB, reroute esatto sulla SPEC, gen~ PASS
139/139 sui due canali; `proto-max/RISULTATI-P3.md`. Da caricare in
Live e ascoltare.]

### P4 — Mic (1 sessione)

`MC-MIC`: il modulo mic con MUTE (rampa 1 ms) e la sua catena. Prova con un
MC vero sopra il mix.

Chiude a orecchio: **serve un limiter sul mic?** (idea della review, non
discussa) e **B6**, parte mic: soglie dei LED.

[2026-10-15: P4 COSTRUITO — `MC-MIC` con GAIN (30-60 dB, pot lineare
del circuito), passa-alto 60 Hz, EQ2, FX1-FX4 verso i bus di P3, MUTE
(1 ms) e LED a tre colori; preamp contro `mic-pre-ac` ≤ 0,06 dB, gen~
PASS 106/106; `proto-max/RISULTATI-P4.md`. Da caricare in Live e
ascoltare.]

**Totale stimato: ~8 sessioni mie, 5 sessioni d'ascolto tue.** Le fasi
sono indipendenti dopo P0: l'ordine di P1-P4 si può cambiare.

## 3. Come lo costruisco (ingegneria)

- **DSP in `gen~` codebox**: codice testuale (GenExpr) dentro una patch
  Max minima: manopole `live.dial`, un oggetto `gen~`, ingressi e uscite.
  Il codice testuale si genera, si confronta e si versiona meglio di una
  patch disegnata.
- **Curve e law dai numeri del design**: uno script Python nel repo
  (`proto-max/coefficienti/`) genera tabelle e costanti dalle stesse
  formule dei design doc (law Xone:96, isolator LR4, griglie dei
  saturatori). Così il prototipo e il circuito partono dagli stessi numeri.
- **Ogni dispositivo ha un tasto «riferimento»**: suono del design
  attuale contro alternativa, per gli A/B senza toccare altro.
- **Controllo di verifica**: per ogni dispositivo confronto la risposta
  del prototipo con la simulazione LTspice (rumore rosa e analisi in
  frequenza dentro Max). Se non coincidono entro ~0,5 dB, la patch non
  esce.

Limiti onesti: il core del filtro e i saturatori sono **modelli di
comportamento** tarati sulle simulazioni, non il circuito. Imitano il
carattere misurato (tetto, calo di nota, griglia di distorsione), non
ogni dettaglio.

## 4. Cosa devi fare tu

1. **Una volta per dispositivo, ~10 minuti la prima volta**: in Live crei
   un Max Audio Effect vuoto, apri il file che ti preparo, copi e incolli,
   salvi. Ti guido passo passo (`proto-max/montaggio.md`, scritto in P0).
2. **Set di prova**: 4 tracce con loop dub e reggae tuoi, più qualche
   traccia moderna «senza anima» per il NASTRO.
3. **Ascolto**: una sessione a fine fase, con le domande della fase in
   chat, una alla volta.

## 5. Struttura dei file

```
proto-max/
├── montaggio.md                ← procedura di assemblaggio in Live (P0)
├── coefficienti/               ← script Python: law, curve, tabelle
├── MC-CHANNEL.maxpat + .genexpr   P0
├── MC-FILTRO.maxpat + .genexpr    P1
├── MC-5WAY.maxpat + .genexpr      P2
├── MC-FX.maxpat + .genexpr        P3
├── MC-MASTER.maxpat               P3
└── MC-MIC.maxpat + .genexpr       P4
```

## 6. Decisioni di Filippo per partire

1. **[DECISO da Filippo il 2026-10-14: P0 → P1 filtro → P2 5-way → P3 → P4]**
   **Ordine delle fasi**: P0 → P1 filtro → P2 5-way → P3 → P4, oppure un
   altro. Raccomandazione: P0 per primo, poi il filtro, perché B1 tiene
   fermo il todo 11.
2. **[DECISO da Filippo il 2026-10-14: prima il mouse, il controller MIDI
   dopo]** Le manopole si mappano in Live (MIDI Map) senza toccare le patch.
   **Controllo**: solo mouse (dec. 78), oppure un controller MIDI che hai
   già. Con un controller senti il gesto vero (due manopole insieme,
   una spazzata veloce); a mouse no.
3. **[DECISO da Filippo il 2026-10-14: in cuffia]** Conseguenza: le
   scelte sui bassi prese in P2 (GROWL, banda a ~90 Hz di B3) restano
   provvisorie fino a un ascolto su un impianto con sub.
   **Dove ascolti**: cuffie, monitor da studio o un impianto con sub.
   Le decisioni sui bassi (GROWL, banda a ~90 Hz, B3) chiedono un sub
   vero, almeno per la sessione finale di P2.
