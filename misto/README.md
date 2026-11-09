# MISTO — versione mista digitale/analogica del maelcum mixer

Data di nascita: 2026-11-09 (richiesta di Filippo, dec. 174). Supera la
pausa del 6/11: il misto parte ora, accanto alla versione analogica
completa.

Progetto parallelo, come `cheap/`. Il progetto principale (`docs/`, `sim/`,
`pcb/`, `SPECIFICA.md`) NON si modifica da qui: MISTO legge e copia, non
scrive fuori da `misto/`. Una decisione del misto che cambia il principale
passa da `docs/01` con un numero suo.

## Cosa è il misto

Lo stesso mixer, con lo stesso pannello, gli stessi comandi e le stesse
funzioni. L'audio resta analogico. Un piccolo chip in ogni modulo legge le
manopole e scrive le tensioni di comando (CV) dei VCA, dei filtri e delle
celle: fa il lavoro che oggi fanno gli shaper a diodi e molti trimmer di
taratura.

Obiettivi (M6, rivede l'ordine di M1 dopo l'inventario):

1. meno taratura a banco (meno trimmer);
2. curve esatte a ogni temperatura;
3. cambiare via USB i valori che sono già una CV.

Costo e spazio, i primi obiettivi di M1, restano circa pari alla versione
analogica (`02-inventario-comandi.md` §3).

## Regole

1. **Le tre condizioni di Filippo (6/11, M2):**
   - l'audio non passa mai per numeri: il chip muove solo le CV;
   - chip comune su zoccolo, ricambio già programmato nel flight case,
     firmware aperto;
   - nessun gradino udibile girando una manopola.
2. Le regole del `CLAUDE.md` del progetto valgono anche qui (metodo,
   simulazioni, [BLOCCATO]/[PROVVISORIO]/[APERTO]/[SUPERATO]).
3. Pannello, comandi e funzioni restano quelli della versione analogica.
   Il pannello cambia un po' solo se l'elettronica diventa più piccola (M3).
4. I valori modificabili si cambiano da un computer via USB. Nessun
   display sul mixer (M4).
5. Un chip per modulo (M5).
6. Le scelte del misto stanno in `misto/01-decisioni-misto.md`, numerate
   M1, M2… Ogni risparmio si misura contro la versione analogica completa.
7. Simulazioni del misto in `misto/sim/`, con le librerie condivise di
   `sim/lib/` (`.include ../../sim/lib/...`).

## File

```
misto/README.md                 questo file
misto/01-decisioni-misto.md     le scelte di Filippo (M1, M2…)
misto/02-inventario-comandi.md  ogni circuito di comando: com'è oggi, cosa fa il chip, cosa si risparmia
misto/03-blocco-comando.md      requisiti e topologia del blocco del chip (primo caso: FX-RET)
misto/script/                   calcoli (area delle impronte, passi di ADC e DAC)
```
