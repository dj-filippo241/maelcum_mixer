# MISTO — decisioni

Scelte di Filippo sul misto. Formato: numero M, data, origine [F]/[C],
testo. Origine come in `docs/01`: [F] detta da Filippo, [C] proposta di
Claude accettata.

M1. **[F — 2026-11-09, «1 e parzialmente 2»] Obiettivi.** Prima costare
meno e occupare meno spazio. Poi, se costa poco, cambiare alcuni valori
senza saldare: incroci del 5-way, incroci dell'isolator, valori di NASTRO,
GROWL e overdrive. Non interessano: memorie di scena, MIDI, movimenti a
tempo.

M2. **[F — 2026-11-06, dialogo BURN; confermata il 2026-11-09] Tre
condizioni per il digitale.** (1) L'audio non passa mai per numeri: il chip
muove solo le CV. (2) Chip comune su zoccolo, ricambio programmato nel
flight case, firmware aperto. (3) Nessun gradino udibile girando una
manopola.

M3. **[F — 2026-11-09, «1 si uguale»] Stesso pannello, stessi comandi e
funzioni della versione analogica completa.** Il pannello si può ritoccare
solo se l'elettronica diventa più piccola. Le opzioni di `cheap/` restano
una scelta a parte.

M4. **[C — 2026-11-09, «1»] Valori modificabili da computer via USB.**
Nessun display sul mixer; i valori restano salvati nel chip.

M5. **[C — 2026-11-09, «1»] Un chip per modulo.** Un guasto ferma solo quel
modulo; un ricambio solo, uguale per tutti; CV corte (dec. 92: il ronzio
raccolto dalle linee CV lunghe).

M6. **[F — 2026-11-09, «2»; precisa M1] Il misto va avanti per la
taratura e la precisione, non per costo e spazio.** Dopo l'inventario
(`02-inventario-comandi.md` §3): costo pari (−190…+165 €), ~150 impronte
in meno su tutto il mixer, nessuna scheda tolta, pannello uguale. Guadagno
vero: ~60-80 trimmer in meno, curve esatte a ogni temperatura, valori
modificabili via USB per ciò che è già una CV.

M7. **[C — 2026-11-09, «1»] GROWL, NASTRO e DRIVE del filtro restano sul
segnale, fuori dall'USB.** Pot doppi come nella versione analogica (dec.
162, todo 212): rimetterli sotto VCA o OTA porta rumore e chip. Via USB si
cambia solo ciò che è già una CV.

M8. **[C — 2026-11-09, «1»] Incroci del 5-way e dell'isolator fissi.** Si
scelgono a orecchio nel prototipo in Live (todo 60, dec. 152) e restano
saldati. Scartati: serie di resistenze a switch (~60 resistenze per serie,
switch dentro i filtri) e incroci continui con VCA/OTA (rumore, decine di
chip).

M9. **[C — 2026-11-10, «1 usb sul master»; todo 279] Una presa USB sul
retro, sul master.** I chip dei moduli parlano fra loro su due fili del
backplane (pin liberi della riga c). Un cavo e un programma per tutti i
moduli. La presa del Pico resta per caricare il firmware a banco. Costo: due
fili di backplane e un transceiver per modulo (`03-blocco-comando.md` §7).
