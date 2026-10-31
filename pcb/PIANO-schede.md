# Piano delle schede (todo 203) — bozza del 2026-10-31

Calcolo: `python3 pcb/tools/piano_schede.py`. Ipotesi nel file: dec. 156-158, setup completo,
schede verticali sotto il proprio modulo, passo minimo 25 mm fra schede affiancate.

## Il telaio

- Pannello 19" × 13U (577,85 mm), già disegnato così (`docs/pannelli/setup-completo.svg`).
- Inclinato: ~215 mm dietro, ~150 mm davanti (dec. 158). Schede a trapezio da ~185 a ~120 mm.
- In fondo al pannello (schede più alte): 5-WAY, MASTER, CUE. Verso chi suona: MIC/MONO, FX-RET,
  canali, FX-SEND, FILTRO (il più vicino a chi suona, schede più basse).

## Conteggio e schede per modulo

Conteggi veri: FX-SEND 120 (`fx-send.py`), MASTER segnale 282 (`master-segnale.py`). Gli altri
sono stime dalla distinta del budget: 12 impronte per chip, tarate sul FX-SEND, più trimmer e
parti discrete. Incertezza ±30 %.

| Modulo | Copie | Componenti | Scheda (h) | Capienza al 70 % | Schede che servono | Ne stanno sotto il pannello | Esito |
|---|---|---|---|---|---|---|---|
| 5-WAY | 1 | ~970 | 185 → 173 | 169 | 6 | 11 | ok |
| MASTER | 1 | ~600 | 185 → 173 | 169 | 4 | 3 (96 mm) | **stretto** |
| CUE | 1 | ~200 | 185 → 173 | 169 | 2 | 2 | ok, al limite |
| MIC | 1 | ~215 | 173 → 151 | 280 | 1 | 1 | ok (77 %) |
| MONO | 3 | ~120 | 173 → 151 | 280 | 1 | 1 | ok |
| FX-RET | 4 | ~300 | 173 → 142 | 379 | 1 | 1 | ok (79 %) |
| CANALE | 4 | ~350 | 173 → 139 | 415 | 1 | 1 | ok (84 %): da tenere d'occhio |
| FX-SEND | 4 | 120 | 139 → 129 | 106 | 2 | 1 | **stretto** |
| FILTRO | 1 | ~800 | 129 → 121 | 85 | 10 | 5 (144 mm) | **non sta** |

Le percentuali dicono quanta parte della capienza al 70 % è usata.

## I tre casi stretti e le strade

**Spazio libero che c'è già.** Nel setup completo due zone di pannello sono cieche: sotto MIC/MONO
(144 × 264 mm) e sotto i ritorni FX (144 × 190 mm). Sotto ci stanno ~1.600 e ~1.100 componenti.

1. **FILTRO** (~800 componenti, ne stanno 425). Strada proposta: le sue schede vanno sotto il
   pannello cieco dei ritorni FX, accanto (4 schede, capienza ~900). I pot restano sul pannello
   del filtro, con la scheda comandi e un cavo piatto (dec. 136). Il pannello non cambia.
2. **FX-SEND** (120 contro 106). Se il filtro va nel cieco, lo spazio sotto il pannello del filtro
   si libera: la scheda del FX-SEND si allunga fino al bordo davanti (y 402-564) e porta ~190
   componenti. Il FX-SEND resta una scheda sola, al 62 %.
3. **MASTER** (4 schede in 96 mm). Strade: (a) passo 24 mm invece di 25, con le parti alte su un
   lato solo; (b) le due schede d'uscita sotto un'altra zona libera, collegate col cavo J2;
   (c) misurare prima il conteggio vero delle schede d'uscita (#206): la stima ~320 può scendere.

## Proposte di disposizione (31/10, Filippo: «puoi spostare la posizione di tutti i moduli»)

Fogli in `docs/pannelli/pannelli.pdf` (pagine 4-7), da `docs/pannelli/proposte_disposizione.py`.
Ogni modulo porta il numero di schede e quanto sono piene; i moduli restano com'erano.

| Foglio | Disposizione | Pannello | Schede | Casi rossi |
|---|---|---|---|---|
| Oggi | come il 21/10 | 13U | 42 | filtro, FX-SEND, master |
| A | filtro al centro sotto i ritorni FX; master 108, 5-way 280 | 12U | 33 | nessuno |
| B | filtro a sinistra sotto MIC/MONO; centro cieco libero | 12U | 31 | nessuno |
| C | canali al centro; ritorni FX e filtro a sinistra; MIC/MONO a destra | 12U | 33 | nessuno |

Spostare il filtro dalla colonna dei canali libera 75 mm: il pannello scende da 13U a 12U.

## Conseguenze

- **Backplane.** Le schede si innestano a y diverse (fondo, metà, davanti) e il fondo resta
  piatto: il backplane da ~75 cm in due pezzi (budget) va ridisegnato come più strisce sul fondo.
  Da fare dopo le scelte qui sopra.
- **Moduli opzionali** (crossfader, EQ grafico, uscite per via, dec. 111): oggi senza posto
  sul pannello. Le zone cieche sono il posto naturale anche per loro: le schede del filtro ne
  occupano una.
- **Setup ridotto** (2 canali, 1 MONO): più pannello cieco, nessun caso nuovo.
- Totale schede di modulo nel setup completo, con le strade 1 e 2: **32**, più backplane,
  PSU-IN, schede comandi e schedina dei connettori sul retro.

## Da verificare con i conteggi veri

Canale (84 %) e FX-RET (79 %) sono le stime più vicine al tetto: il primo `conta.py` vero va su
di loro, prima di disegnarle.
