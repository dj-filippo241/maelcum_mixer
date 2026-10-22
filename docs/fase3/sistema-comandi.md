# Sistema — inventario dei comandi di pannello (base per la voce 40) — 2026-10-13

> Elenco di manopole, slider, bottoni e LED che i design elettrici
> chiedono oggi, modulo per modulo. Serve alla sessione hardware (voce
> 40): dice quanti pezzi servono, di che tipo elettrico e con che curva.
> NON decide marca, modello, forma, colore, disposizione: sono di Filippo.
> Fonte: i documenti di design alla data. «Singolo» = una pista;
> «doppio» = due piste sullo stesso albero (stereo). «→ CV» = la manopola
> dà solo una tensione di controllo: basta un pot lineare qualunque, la
> curva la fa l'elettronica.

## Per modulo

| Modulo | Comando | Qtà | Tipo elettrico | Note |
|---|---|---|---|---|
| **Canale CDJ** (×4) | GAIN | 1 | singolo 10k lin → CV | detent a 0 dB |
| | EQ LOW / LOW-MID / MID-HIGH / HIGH | 4 | doppio 10k LINEARE, residuo ≤ 20 Ω, SENZA contatto di fondo corsa (dec. 127) [REV 2026-10-13, dec. 105: isolator, prima taper custom] | detent al centro; tracking ≤ 0,25 dB; eq-isolator §5 e §8 |
| | LINE / PHONO | 1 | levetta piccola 2 posizioni (dec. 123) | |
| | Filtro HPF / OFF / LPF | 1 | levetta 3 posizioni fisse ON-OFF-ON, logica (dec. 122) | su HPF, centro OFF, giù LPF |
| | CUE | 1 | bottone con luce a ritenuta, logico (dec. 123) | |
| | Assign FX 1-4 | 4 | bottoni con luce a ritenuta, logici (dec. 123) | pilotano il micro-modulo FX-SEND |
| | Fader | 1 | slider MONO 100 mm → CV → VCA per lato (dec. 120, 126) | tracking ≤ 0,5 dB dai VCA |
| | Meter | 1 | barra 10 LED | |
| **FX-SEND** (×4) | EQ LOW / HIGH | 2 | doppio 10k, taper custom | |
| | LEVEL | 1 | doppio 10k log | |
| **FX** (4 bus) | GAIN ritorno | 4 | singolo → CV | |
| | EQ LOW / HIGH ritorno | 8 | doppio 10k, taper custom | |
| | Fader ritorno | 4 | slider MONO 100 mm → CV → VCA per lato (dec. 120, 126) | |
| | Reroute e self-feedback | 16 | singolo lin → CV | cablati rovesci (shaper) |
| | Meter | 4 | barra 10 LED, una per ritorno | dec. 116 (2026-10-21), era 1 |
| **Filtro** | HPF freq / res / drive | 3 | singolo lin → CV | |
| | LPF freq / res / drive | 3 | singolo lin → CV | |
| **5-way** | GAIN di banda | 5 | doppio 10k, taper custom | rotativi (dec. 85), detent |
| | POSITION di banda | 5 | singolo lin → CV | |
| | WIDTH di banda | 5 | doppio 1k, taper log da scegliere | dec. 117 (2026-10-21): continuo Q3…Q0,3, era selettore 3 posizioni |
| | KILL di banda | 5 | levetta 3 posizioni ON-OFF-(ON), logica (dec. 121) | su = kill fisso, giù = kill a molla |
| | GROWL e NASTRO (dec. 99; era DRIVE ×1) | 2 | doppio lin, diretto sul segnale (v0.4, niente CV) | primo 5-10 % quasi inerte |
| | Meter | 1 | barra 10 LED | |
| **Master** | MASTER | 1 | singolo lin → CV | detent a 0 dB |
| | BOOTH | 1 | singolo lin → CV | |
| | Meter | 2 | barre 20 LED | |
| **CUE** | BLEND cue ↔ master | 1 | doppio 10k lin | centro = 50/50 |
| | LEVEL cuffie | 1 | doppio 10k log | |
| | Uscite cuffia | 2 | jack stereo 6,3 mm (dec. 128) | |
| **MIC** (dec. 97) | GAIN | 1 | singolo 5k | nel percorso del segnale |
| | EQ LOW / HIGH | 2 | singolo 10k, taper custom | |
| | SEND 1-4 | 4 | singolo 10k | |
| | LED | 1 | tricolore verde / giallo / rosso | |
| **MONO** (dec. 97) | GAIN | 1 | singolo 10k | nel percorso del segnale |
| | EQ LOW / HIGH | 2 | singolo 10k, taper custom | |
| | SEND 1-4 | 4 | singolo 10k | |
| | LED | 1 | tricolore | |

Comandi interni, non di pannello: capacità di carico phono, pad di
mandata ai pedali, trimmer di taratura.

## Totali per il primo prototipo (4 canali, 1 MIC + 3 MONO)

| Tipo | Quantità |
|---|---|
| Pot singoli | 66 (38 → CV lineari, 28 sui moduli MIC/MONO) |
| Pot doppi | 43 (di cui 21 con taper custom e 16 lineari con contatto di fondo corsa per l'EQ dei canali, dec. 105; detent dove indicato) |
| Slider mono → VCA (dec. 126) | 8 |
| Selettori 3 posizioni | 9 |
| Selettori 2 posizioni | 4 |
| Bottoni / levette logici | 25 |
| Barre LED | 9 da 10 + 2 da 20 (dec. 116: +3 ritorni FX) |
| LED tricolore | 4 |

Manopole in tutto: 115 (dec. 99: +1 sul 5-way; dec. 117: +5 WIDTH continui). Con 4 moduli MIC/MONO al posto di 4 il conto non
cambia; ogni modulo MIC/MONO in meno toglie 7 pot singoli.

## Scelte hardware (sessione del 2026-10-21, dec. 118)

- Rotativi principali: classe 14 mm (Alps RK14K o equivalente), disposti
  disassati come sul Xone:DB4. Vale per GAIN e EQ dei canali, 5-way,
  filtro, FX (GAIN, reroute), master, CUE.
- EQ di FX-SEND, ritorni FX, MIC e MONO (24 pot: 8 doppi FX-SEND, 8
  doppi ritorni, 8 singoli MIC/MONO): classe 9 mm (Alps RK09 o
  equivalente), senza scatto al centro.
- Polvere (dec. 119, 2026-10-22): pot a corpo chiuso, protezione dal
  pannello (guarnizioni, coperchio del flight case), pot sostituibili
  senza rifare la scheda.
- Fader (dec. 120, 2026-10-22): corsa 100 mm per canali e ritorni FX.
  Tracking stereo ≤ 0,5 dB da risolvere (fader selezionati o fader → VCA).
- Kill del 5-way (dec. 121, 2026-10-22): levette sigillate ON-OFF-(ON).
- Selettore del filtro di canale (dec. 122): levetta sigillata a tre
  posizioni fisse.
- Bottoni di canale (dec. 123): CUE e assign FX con luce a ritenuta,
  LINE/PHONO a levetta piccola.
- Cappucci (dec. 124, PROVVISORIO): gommati; probabile stampa 3D di
  Filippo. Tutti i rotativi con albero 6 mm a D e poche altezze d'albero.
- Da verificare: codici a magazzino della RK14K doppia 10k B con detent
  (alcune versioni hanno ordine minimo 1000 pezzi).

## Taglia e scatto per comando (dec. 125, 2026-10-22)

Grande = pot 14 mm · media = pot 14 mm con cappuccio ~12 mm · piccola = pot 9 mm.

| Comando | Qtà | Taglia | Scatto |
|---|---|---|---|
| GAIN canale CDJ | 4 | grande | 0 dB |
| EQ canale CDJ | 16 | grande | centro |
| EQ di FX-SEND | 8 | piccola | no |
| LEVEL di FX-SEND | 4 | grande | no |
| GAIN dei ritorni FX | 4 | grande | no |
| EQ dei ritorni FX | 8 | piccola | no |
| Reroute e SELF | 16 | piccola | centro (pezzo da verificare) |
| Filtro FREQ, RES, DRIVE | 6 | grande | no |
| GAIN delle 5 vie | 5 | grande | centro |
| POSITION | 5 | media | no |
| WIDTH | 5 | media | no |
| GROWL e NASTRO | 2 | grande | no |
| MASTER | 1 | grande | 0 dB |
| BOOTH | 1 | grande | no |
| BLEND del CUE | 1 | grande | centro |
| LEVEL cuffie | 1 | piccola | no |
| GAIN di MIC e MONO | 4 | grande | no |
| SEND 1-4 di MIC e MONO | 16 | grande | no |
| EQ di MIC e MONO | 8 | piccola | no |

Totale 115 manopole: 64 grandi, 10 medie, 41 piccole.

## Ingegneria dei comandi (2026-10-22, dopo le dec. 117-125) [PROPOSTA di Claude]

### Curve dei pot: tre famiglie

| Famiglia | Pot | Pezzo |
|---|---|---|
| Lineare standard (B) | tutti i pot → CV (GAIN canale, filtro, reroute/SELF, GAIN ritorni, POSITION, MASTER, BOOTH), EQ canale (dec. 105), GROWL/NASTRO, BLEND | RK14K / RK09 lineari a catalogo; reroute: RK09K singolo con scatto al centro (es. RK09K113004U, verticale, 10k B) |
| Logaritmica standard (A) | LEVEL di FX-SEND (fx-module: «curva A 10 % basta»), LEVEL cuffie, SEND 1-4 di MIC/MONO (B9), GAIN di MIC/MONO (B9: col lineare l'ultimo 10 % vale 8,4 dB) | A a catalogo; la scelta A contro B per MIC/MONO resta all'ascolto (B9) |
| Curva asimmetrica | EQ di FX-SEND, ritorni, MIC e MONO; GAIN delle 5 vie | vedi sotto |
| Da scegliere (dec. 117) | WIDTH: log 10 % (centro ~Q1,6) o ~20 % (centro ~Q1) | ⚠ il WIDTH è un doppio 1k: la RK14 a catalogo parte da 5k; se il 1k non c'è, partitore riscalato su 10k (da rifare in five-way §4.3) |

**Curve asimmetriche (cut su quasi tutta la corsa, boost nell'ultimo
tratto).** Strade:
1. **Pot lineare + 1-2 resistenze di legge** fra cursore ed estremi:
   pezzi standard, curva approssimata, valori calcolati cella per cella.
2. Pista su misura dal costruttore: curva esatta, ordine minimo e mesi.
3. Pot → CV → VCA: curva esatta dallo shaper, ma un VCA per lato e
   rumore in più.

Raccomandazione: **1**. Gli EQ secondari non hanno più lo scatto
(dec. 118 c, 125): il centro non deve cadere esatto su 0 dB. I valori
delle resistenze si calcolano quando le curve sono confermate
all'ascolto (B6, B8, B9; regola 3: niente valori prima). Il GAIN delle 5
vie ha lo scatto al centro: lì la cella è piatta per costruzione, la
resistenza di legge non lo sposta se è simmetrica rispetto al centro.

**Scelte di Filippo (dec. 129, 2026-10-22, PROVVISORIE fino all'ascolto):**
A3 (EQ secondari: lineare + resistenze, bassi e alti diversi), B2 (GAIN
5 vie: lineare + resistenze), C2 (WIDTH log ~20 %), D1 (LEVEL log A 10 %),
E2 e F1 (MIC/MONO GAIN e SEND log A), G fader «come Pioneer DJM».

### Contatto di fondo corsa dell'EQ di canale (16 pot)

- Un pot doppio 10k lineare con scatto al centro E interruttore a fondo
  corsa non l'ho trovato a catalogo: sarebbe un pezzo su misura.
- Senza contatto il silenzio dipende dal residuo del pot: Alps dichiara
  ≤ 20 Ω su 10k per la RK14J (da verificare per la RK14K) → banda chiusa
  a circa −54 dB, tutte e quattro chiuse circa −54 dB (eq-isolator §5,
  §8: col contatto −100 dB).
- Alternativa elettronica (comparatore sulla continua del cursore +
  interruttore analogico, 32 per i 4 canali): complicata, sporca il
  percorso con una continua da togliere. Scartata.
- **Deciso: niente contatto** (dec. 127, 2026-10-22), pot con residuo garantito ≤ 20 Ω. Una
  banda chiusa a −54 dB sotto le altre tre è coperta; il muto vero del
  canale resta il fader. ⚠ Cambia una proprietà dell'isolator (dec. 105:
  «tutte a fondo corsa = canale muto»): da confermare da Filippo.

### Tracking dei fader da 100 mm (dec. 59: ≤ 0,5 dB fra L e R)

- Fader doppi a catalogo: Penny & Giles PGF8000 ±1,0 dB (0…−40 dB);
  PGF3000 ±3 dB; Alps RS60 ±3 dB. Nessuno sta sotto 0,5 dB.
- Strade: (a) **fader singolo (mono) → CV → VCA, come il Xone:92**:
  tracking dato dai VCA trimmati, fader qualunque (anche a carbone),
  curva libera nello shaper; +16 VCA (4 canali + 4 ritorni, stereo),
  ~78 chip in tutto, +20…45 mA per ramo sul W1 (oggi all'88 %), un po'
  di rumore in più a fader aperto (da ricalcolare in docs/06); (b) fader
  doppi selezionati a coppie dal lotto; (c) accettare ±1 dB con i PGF8000.
- **Deciso (a)** (dec. 126, 2026-10-22).

### Jack e connettori

Già nei design: RCA dorati isolati per CDJ, RCA phono + morsetto di
massa, XLR mic (solo dinamici), jack TS per MONO, XLR master L/R e booth
L/R (Neutrik NC3FAH o equivalente), TRS rec, jack TS per mandate e
ritorni dei pedali, 2 jack cuffia stereo, circolare IP65 ≥ 20 contatti +
PE per l'alimentatore (dec. 113). Proposta per l'aperto (dec. 111 e):
connettori a corpo metallico con guarnizione verso il pannello, XLR con
blocco. Uscite cuffia: entrambe 6,3 mm (dec. 128, 2026-10-22).

## Aperto per la sessione hardware

- Taper custom: quante famiglie diverse servono davvero (EQ2, gain 5-way,
  EQ mic/mono) e se un solo fornitore le copre. L'EQ dei canali non ne ha
  più bisogno (dec. 105): 16 pot doppi lineari con detent e contatto di
  fondo corsa. Il contatto deve chiudere solo all'ultimo grado di corsa.
- Dec. 99 (2026-10-13): il 5-way ha 2 manopole di saturazione al posto di
  1 (totale manopole 110); nessuna manopola di livello dopo il drive: i
  saturatori si autoregolano. Il filtro resta a 2 manopole drive.
- Dipende da A4 (voce 63): HPF e LPF in serie non aggiungono manopole,
  cambiano il selettore di canale.
