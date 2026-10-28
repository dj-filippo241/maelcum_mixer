# Generatore delle PCB: revisione del 2026-10-28

Revisione di `pcb/tools/pcbgen.py` prima del master (#167). Quattro analisi in parallelo
(errori, struttura, qualità audio misurata sulla scheda, coerenza coi documenti), poi le
correzioni. Banco di prova: FX-SEND, rigenerato.

## Cosa cambia

| Prima | Adesso |
|---|---|
| `build()` usciva sempre «tutto bene» (codice 0); gli errori restavano nel JSON | Esito **PASSA / NON PASSA** in fondo e nel `riepilogo.json`; con errori il processo esce con codice 1 |
| Nessun confronto col giro prima | Riga «PEGGIO» per ogni conteggio di ERC, DRC o controllo audio che cresce |
| Report di kicad-cli e `.ses` di Freerouting letti anche se vecchi | Cancellati prima di ogni giro; se un comando non li produce, il generatore si ferma |
| `routing: true` se il file `.ses` esisteva | Collegamenti aperti contati rete per rete dal log: la massa la chiudono le colate, una rete di segnale aperta è un errore |
| Schema confrontato col netlist in un senso solo | Nei due sensi: anche una rete nata nello schema (due pin sullo stesso punto) è un errore |
| `check()`: solo reti con un pin | Anche pin di alimentazione dimenticati, pin dichiarati due volte, riferimenti doppi, nomi di rete quasi uguali (refusi) |
| Classi di rete solo nella scheda in memoria | Scritte anche nel `.kicad_pro`: un ritocco in KiCad le conosce |
| 51 avvisi di parità «net_conflict» mescolati agli altri | Contati a parte come «atteso» (pin liberi del C96, staffe dei pot) |
| Campo «Nota» solo nello schema (19 avvisi) | Copiato sull'impronta; i fori non entrano nella distinta |
| uuid casuali: la PCB cambiava tutta a ogni giro | uuid ripetibili: git mostra solo le differenze vere |
| 100n di disaccoppiamento piazzati col blocco, a 8-13 mm dal pin (fino a 78 mm di pista) | Legati al loro chip in automatico e messi a ~2 mm dal pin, col pad dell'alimentazione verso il pin |
| Via di massa sempre verso l'esterno, anche sopra un altro pad | Prima fuori, poi sotto il corpo del chip; isole di colata tolte |

File nuovi:

- `pcb/tools/backplane.py`: pinout del C96 (righe a e c comuni, §3 e §5 del backplane). Il modulo scrive solo la riga b.
- `pcb/tools/audiocheck.py`: controllo audio dopo il routing (regole A1-A5 sotto). Gira in 0,2 s. Da riga di comando legge le regole da `d.audio_rules` del file del modulo.
- `pcb/fx-send/cavo.py`: l'ordine dei fili del cavo piatto, letto dalle due schede.
- `sim/lint_cir.py`: le regole di simulazione del CLAUDE.md come controllo dei `.cir`.

## Controllo audio (audiocheck.py)

Soglie di partenza, da rivedere con la prima scheda costruita:

| Regola | Cosa | Soglia |
|---|---|---|
| A1 | 100n dal pin di alimentazione | ≤ 3 mm pad-pad, ≤ 5 mm di pista; regolatori ≤ 10 mm |
| A2 | Masse virtuali e ingressi invertenti | ≤ 25 mm di pista, ≤ 1 via; reti del cavo ≤ 40 mm |
| A3 | Passivi di una rete sensibile dal pin dell'op-amp | ≤ 6 mm |
| A4 | Accoppiamento stimato da reti rumorose | ≤ 0,05 pF |
| A5 | Piste sensibili nel riquadro dei regolatori | nessuna (+3 mm) |

Ogni modulo dichiara le sue reti in `d.audio_rules` (esempio in `fx-send.py`). Per ora il
controllo **non ferma** la scheda: misura e segnala i peggioramenti. Diventa un errore quando
il piazzamento a grappolo (sotto) lo rende raggiungibile.

FX-SEND, prima e dopo questa revisione:

| Regola | v0.2 | adesso |
|---|---|---|
| A1 | 24 (tutti gli op-amp a 8-13 mm) | 10 (solo regolatori; ogni op-amp entro 3 mm) |
| A2 | 35 | 29 |
| A3 | 26 | 23 |
| A4 | 4 | 4 |
| A5 | 4 | 3 |

## Correzione di circuito trovata dall'analisi

**Mute degli assign (FX-SEND).** Era un circuito aggiunto disegnando (NOTA), non dal design
doc. Con mute attivo e bottone premuto l'ingresso dell'ADG1434 stava a 1,21 V, fra le soglie
0,8 e 2,0 V: il mute non garantiva lo spegnimento. Da acceso stava a 2,5 V. Ora: 100k a massa
e 1k in serie al FET. Acceso 4,55 V, mute 0,45 V, rampe 0,9 ms e 0,09 ms. Dettagli in
`pcb/fx-send/NOTE.md` punto 12.

## Piazzamento a grappolo (2026-10-28, todo 183)

Ogni R e C (non elettrolitico) si lega a un op-amp: prima per un pin di segnale in
comune (stesso blocco, poi un altro blocco), poi per una rete in comune con un passivo
già legato. Il passivo va accanto al suo pin, sul lato del pin, col pad della rete in
comune verso il pin; se il posto è occupato scorre lungo il lato, poi una fila più in
fuori (spazio `d.cluster_gap`, 0,5 mm). Il grappolo viaggia col chip nel piazzamento a
blocchi. Si spegne con `d.cluster_auto = False`.

FX-SEND, prima e dopo:

| Regola | prima | grappolo 0,2 mm | grappolo 0,5 mm (adesso) |
|---|---|---|---|
| A1 | 10 | 10 | 10 |
| A2 | 29 | 22 | 28 |
| A3 | 23 | 10 | 12 |
| A4 | 4 | 5 | 8 |
| A5 | 3 | 3 | 4 |
| esito | PASSA | NON PASSA (2 aperti di Freerouting) | PASSA |

Con 0,2 mm Freerouting lasciava aperti un filo del cavo e un tratto di +15SW: 0,5 mm
è il compromesso. A3 (passivi lontani dal pin) è risolto. Quello che resta in A2, A4 e
A5 non dipende dalla cella: sono piste lunghe dal C96 (S*_OUT, SEND_IN, 90-130 mm) e
dal cavo dei pot (NA/NB/NC) che passa accanto ai regolatori. Serve il punto 1 sotto.

## Cosa resta (in ordine)

1. **Blocchi vicino al loro connettore.** Oggi i blocchi vanno in colonne nell'ordine
   del file. Le celle che parlano col C96 (iniezione, buffer d'ingresso) vanno sul bordo
   del C96; le celle del cavo sotto J2; l'alimentazione in una fascia lontana dal cavo.
   È la causa di A2, A4 e A5.
2. **Blocchi con riferimenti fissi** (R1xx lato L, R2xx lato R): oggi una resistenza aggiunta
   rinumera tutte quelle dopo.
3. **Fonte dichiarata per ogni valore** (`fonte="sim/fx/x.cir:Rf"`) e uno script che la
   confronta col `.cir`. Avrebbe trovato da solo le discordanze di NOTE.md.
4. **Isola CTRL_GND** per la logica degli assign, vicino a J3 e ai pin c del C96.
5. **Regolatori:** condensatori d'ingresso e d'uscita a ≤ 10 mm (A1 rimasto).
