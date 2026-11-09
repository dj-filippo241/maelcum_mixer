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
| **Canale CDJ** (×4) | GAIN | 1 | doppio 10k lin selezionato, nel percorso del segnale (dec. 162; era singolo → CV) | detent a 0 dB |
| | EQ LOW / LOW-MID / MID-HIGH / HIGH | 4 | doppio 10k LINEARE, residuo ≤ 20 Ω, SENZA contatto di fondo corsa (dec. 127) [REV 2026-10-13, dec. 105: isolator, prima taper custom] | detent al centro; tracking ≤ 0,25 dB; eq-isolator §5 e §8 |
| | LINE / PHONO | 1 | levetta piccola 2 posizioni (dec. 123) | |
| | Filtro HPF / OFF / LPF | 1 | levetta 3 posizioni fisse ON-OFF-ON, logica (dec. 122) | su HPF, centro OFF, giù LPF |
| | CUE | 1 | bottone con luce a ritenuta, logico (dec. 123) | |
| | Assign FX 1-4 | 4 | bottoni con luce a ritenuta, logici (dec. 123) | pilotano il micro-modulo FX-SEND |
| | Fader | 1 | slider MONO 100 mm → CV → VCA per lato (dec. 120, 126) | tracking ≤ 0,5 dB dai VCA |
| | Meter | 1 | barra 10 LED | |
| **FX-SEND** (×4) | EQ LOW / HIGH | 2 | doppio 10k, taper custom | |
| | LEVEL | 1 | doppio 10k log | |
| **FX-RET** (×4, un modulo per bus, dec. 130) | GAIN ritorno | 1 | doppio 10k lin selezionato, nel percorso del segnale (dec. 162; era singolo → CV) | |
| | EQ LOW / HIGH ritorno | 2 | doppio 10k, taper custom | |
| | Fader ritorno | 1 | slider MONO corto → CV → VCA per lato (dec. 126; corto dalla dec. 169, era 100 mm) | |
| | Reroute e self-feedback | 4 | singolo lin → CV | cablati rovesci (shaper) |
| | Meter | 1 | barra 10 LED | dec. 116 (2026-10-21) |
| **Filtro** | HPF freq / res / drive | 3 | singolo lin → CV | |
| | LPF freq / res / drive | 3 | singolo lin → CV | |
| **5-way** | GAIN di banda | 5 | doppio 10k, taper custom | rotativi (dec. 85), detent |
| | POSITION di banda | 5 | singolo lin → CV | |
| | WIDTH di banda | 5 | doppio 1k, taper log da scegliere | dec. 117 (2026-10-21): continuo Q3…Q0,3, era selettore 3 posizioni |
| | KILL di banda | 5 | levetta 3 posizioni ON-OFF-(ON), logica (dec. 121) | su = kill fisso, giù = kill a molla |
| | GROWL e NASTRO (dec. 99; era DRIVE ×1) | 2 | doppi diretti sul segnale (v0.4, niente CV): GROWL lineare, NASTRO log A 10 % (five-way §5bis, prototipo `fiveway.py`; Filippo 2026-10-22) | primo 5-10 % quasi inerte |
| | Meter | 1 | barra 10 LED | |
| **Master** | MASTER | 1 | singolo lin → CV | detent al centro = 0 dB (dec. 139) |
| | BOOTH | 1 | singolo lin → CV | |
| | MONO | 1 | bottone con luce a ritenuta, logico (dec. 111, 151) | |
| | Meter | 2 | barre 20 LED | |
| **CUE** | BLEND cue ↔ master | 1 | doppio 10k lin | centro = 50/50 |
| | LEVEL cuffie | 1 | doppio 10k log | |
| | Uscite cuffia | 2 | jack stereo 6,3 mm (dec. 128) | |
| **MIC** (dec. 97) | GAIN | 1 | singolo 5k | nel percorso del segnale |
| | EQ LOW / HIGH | 2 | singolo 10k, taper custom | |
| | SEND 1-4 | 4 | singolo 10k | |
| | MUTE | 1 | bottone con luce a ritenuta (dec. 111, 167) | rampa 1 ms, limiter fisso (dec. 145) |
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
| Pot doppi | 43 (di cui 21 con taper custom e 16 lineari SENZA contatto di fondo corsa per l'EQ dei canali, dec. 105 e 127; detent dove indicato) |
| Slider mono → VCA (dec. 126) | 8: 4 lunghi (canali), 4 corti (ritorni, dec. 169) |
| Selettori 3 posizioni | 9 |
| Selettori 2 posizioni | 4 |
| Bottoni / levette logici | 27 (+ MUTE del MIC e MONO del master) |
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

## Taglia e scatto per comando (dec. 169, 2026-11-09; era dec. 125)

Scelte di Filippo del 2026-11-09 (todo 218). La tabella della dec. 125
(64 grandi, 10 medie, 41 piccole) è superata.

### Scala delle taglie [C, PROVVISORIO fino al piano schede, todo 203]

| Taglia | Pot | Cappuccio | Passo verticale | Note |
|---|---|---|---|---|
| molto grande | 14 mm (o 27 mm) | ~22-25 mm | ~26 mm | riferimento: isolator rotativi con Alps RK27 e manopole larghe (Omnitronic ISO-23 MK2). Le misure dei preamp del benchmark non sono pubblicate: da misurare su un pezzo vero |
| grande | 14 mm (Alps RK14K) | 15 mm | 17 mm | come oggi |
| media | 14 mm | ~12 mm | 15,5 mm | come oggi |
| piccola | 9 mm (Alps RK09K/L, Alpha RD902F) | 11 mm | 14 mm | come oggi |
| molto piccola | 9 mm | ~8 mm, zigrinato | ~11 mm | si gira con due dita; da verificare un cappuccio a catalogo per albero 6 mm a D |

Levette: grande = levetta sigillata standard; piccola = levetta
sub-miniatura. Bottoni: grande ~12-15 mm, piccolo ~8 mm. Fader: lungo
100 mm, corto 45 o 60 mm (da scegliere, todo 203). Il fader è mono → CV
→ VCA (dec. 126): la lunghezza non tocca il tracking. Fonte: deduzione
mia, pezzi da confermare a catalogo.

### Tabella

| Modulo | Comando | Qtà | Taglia | Scatto | Pezzo da verificare |
|---|---|---|---|---|---|
| Canale CDJ | GAIN | 4 | piccola | 0 dB | doppio 9 mm lineare con scatto (RK09L): tracking del lotto selezionato |
| | EQ | 16 | grande | centro | come oggi (dec. 127, 168) |
| | LINE/PHONO | 4 | levetta piccola | — | |
| | FILTRO HPF/OFF/LPF | 4 | levetta grande | — | |
| | Assign FX 1-4 | 16 | bottone grande | — | |
| | CUE | 4 | bottone piccolo | — | |
| | Fader | 4 | lungo 100 mm | — | come oggi |
| FX-SEND | LEVEL | 4 | media | no | doppio 14 mm log A |
| | EQ LOW/HIGH | 8 | molto piccola | no | doppio 9 mm (todo 217) |
| FX-RET | GAIN | 4 | piccola | no | doppio 9 mm lineare senza scatto (Alpha RD902F): tracking del lotto selezionato |
| | EQ LOW/HIGH | 8 | piccola | no | come oggi |
| | Reroute e SELF | 16 | media | centro | singolo 14 mm lineare con scatto al centro |
| | Fader | 4 | corto | — | 45 o 60 mm |
| Filtro | FREQ | 2 | grande | no | |
| | RES | 2 | media | no | |
| | DRIVE | 2 | media | no | doppio lineare sul segnale (todo 212) |
| 5-way | GAIN delle vie | 5 | molto grande | centro | doppio lineare con scatto; cappuccio largo |
| | POSITION | 5 | grande | no | era media |
| | WIDTH | 5 | grande | no | era media; doppio 1k ancora da trovare (§curve) |
| | GROWL e NASTRO | 2 | grande | no | come oggi |
| | KILL | 5 | levetta grande | — | ON-OFF-(ON) (dec. 121) |
| Master | MASTER | 1 | grande | 0 dB al centro | come oggi |
| | BOOTH | 1 | media | no | |
| | MONO | 1 | bottone grande | — | |
| CUE | BLEND | 1 | grande | centro | come oggi |
| | LEVEL cuffie | 1 | media | no | doppio 14 mm log A (era 9 mm) |
| MIC (1) | GAIN | 1 | piccola | no | singolo 9 mm 5k curva C: da trovare |
| | EQ LOW/HIGH | 2 | molto piccola | no | |
| | SEND 1-4 | 4 | media | no | |
| | MUTE | 1 | bottone grande | — | a ritenuta (dec. 167) |
| MONO (3) | GAIN (livello) | 3 | grande | no | |
| | EQ LOW/HIGH | 6 | piccola | no | |
| | SEND 1-4 | 12 | media | no | |

Totale 115 manopole: 5 molto grandi, 35 grandi, 42 medie, 23 piccole,
10 molto piccole. Nessun comando aggiunto né tolto.

## Ingegneria dei comandi (2026-10-22, dopo le dec. 117-125) [PROPOSTA di Claude]

### Curve dei pot: tre famiglie

| Famiglia | Pot | Pezzo |
|---|---|---|
| Lineare standard (B) | tutti i pot → CV (filtro, reroute/SELF, POSITION, MASTER, BOOTH), EQ canale (dec. 105), GAIN di canali e ritorni (doppi selezionati nel percorso, dec. 162; prima → CV), GROWL, BLEND (NASTRO: log A, riga sotto) | RK14K / RK09 lineari a catalogo; reroute: RK09K singolo con scatto al centro (es. RK09K113004U, verticale, 10k B) |
| Logaritmica standard (A) | NASTRO (five-way §5bis), LEVEL di FX-SEND (fx-module: «curva A 10 % basta»), LEVEL cuffie, SEND 1-4 di MIC/MONO (B9), GAIN del MONO (todo 131, 2026-10-26: partitore passivo prima del make-up, la A dà dB regolari; mic-mono-moduli §4) |
| Logaritmica inversa (C 20 %) | GAIN del MIC (dec. 129 E2: col lineare l'ultimo 10 % vale 8,4 dB, con la C i dB sono quasi uguali su tutta la corsa); GAIN del MONO: NON qui, vedi riga sopra (todo 131) | A a catalogo; la scelta A contro B per MIC/MONO resta all'ascolto (B9) |
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
E2 (GAIN MIC curva inversa C 20 %, vedi tabella), F1 (SEND MIC/MONO log A), G fader «come Pioneer DJM», curva graduale (circa −12 dB a metà corsa, già simulata).

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
