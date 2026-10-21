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
| | EQ LOW / LOW-MID / MID-HIGH / HIGH | 4 | doppio 10k LINEARE + contatto di fondo corsa (chiude a massa) [REV 2026-10-13, dec. 105: isolator, prima taper custom] | detent al centro; tracking ≤ 0,25 dB; eq-isolator §5 e §8 |
| | LINE / PHONO | 1 | selettore 2 posizioni | |
| | Filtro HPF / OFF / LPF | 1 | selettore 3 posizioni, logico | |
| | CUE | 1 | bottone, logico | |
| | Assign FX 1-4 | 4 | bottoni, logici | pilotano il micro-modulo FX-SEND |
| | Fader | 1 | slider stereo conduttivo-plastica | tracking ≤ 0,5 dB |
| | Meter | 1 | barra 10 LED | |
| **FX-SEND** (×4) | EQ LOW / HIGH | 2 | doppio 10k, taper custom | |
| | LEVEL | 1 | doppio 10k log | |
| **FX** (4 bus) | GAIN ritorno | 4 | singolo → CV | |
| | EQ LOW / HIGH ritorno | 8 | doppio 10k, taper custom | |
| | Fader ritorno | 4 | slider stereo | |
| | Reroute e self-feedback | 16 | singolo lin → CV | cablati rovesci (shaper) |
| | Meter | 4 | barra 10 LED, una per ritorno | dec. 116 (2026-10-21), era 1 |
| **Filtro** | HPF freq / res / drive | 3 | singolo lin → CV | |
| | LPF freq / res / drive | 3 | singolo lin → CV | |
| **5-way** | GAIN di banda | 5 | doppio 10k, taper custom | rotativi (dec. 85), detent |
| | POSITION di banda | 5 | singolo lin → CV | |
| | WIDTH di banda | 5 | selettore 3 posizioni a più vie | commuta resistenze 0,1 % |
| | KILL di banda | 5 | bottoni o levette, logici | |
| | GROWL e NASTRO (dec. 99; era DRIVE ×1) | 2 | doppio lin, diretto sul segnale (v0.4, niente CV) | primo 5-10 % quasi inerte |
| | Meter | 1 | barra 10 LED | |
| **Master** | MASTER | 1 | singolo lin → CV | detent a 0 dB |
| | BOOTH | 1 | singolo lin → CV | |
| | Meter | 2 | barre 20 LED | |
| **CUE** | BLEND cue ↔ master | 1 | doppio 10k lin | centro = 50/50 |
| | LEVEL cuffie | 1 | doppio 10k log | |
| | Uscite cuffia | 2 | jack stereo | |
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
| Slider stereo | 8 |
| Selettori 3 posizioni | 9 |
| Selettori 2 posizioni | 4 |
| Bottoni / levette logici | 25 |
| Barre LED | 9 da 10 + 2 da 20 (dec. 116: +3 ritorni FX) |
| LED tricolore | 4 |

Manopole in tutto: 110 (dec. 99: +1 sul 5-way). Con 4 moduli MIC/MONO al posto di 4 il conto non
cambia; ogni modulo MIC/MONO in meno toglie 7 pot singoli.

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
