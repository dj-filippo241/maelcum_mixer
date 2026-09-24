# Decisioni bloccate

> Regola del progetto: una decisione sta qui UNA VOLTA SOLA. Se cambia, si sposta in
> `questioni-aperte.md` con la data e il motivo, e qui si aggiorna. Niente duplicati.
>
> Legenda origine: **[F]** = detta da Filippo il 2026-09-17 · **[R]** = dal resoconto
> ChatGPT (da riverificare sull'export completo) · **[C]** = proposta di Claude accettata da Filippo.

## Scopo e portata

1. **[F]** Esemplare unico, per il soundsystem di Filippo. Nessuna produzione in serie: si ottimizza per qualità sonora e manutenibilità, non per costi.
2. **[F]** Ruolo di Claude: supporto quasi totale — specifica, progettazione circuiti, simulazioni, selezione componenti, schemi.
3. **[F]** Costruzione fisica: da decidere chi la esegue (vedi questioni aperte).
4. **[F]** Ordine di costruzione — **fase 1**: un modulo canale (phono o CDJ/line), un modulo FX, master out, alimentazione di base. **Fase 2**: 5-way preamp e filtro globale. Motivazione: i moduli semplici validano il backplane prima di affrontare i blocchi difficili.
5. **[F]** Metodo: PRIMA revisione completa e critica del lavoro fatto con ChatGPT (appena arriva l'export), POI si progetta. Niente costruzione sulla base del solo resoconto parziale.

## Architettura generale (dal resoconto, da confermare su export)

6. **[R]** 100% analogico per l'audio. Nessun DSP interno. Il DSP esterno resta responsabile di: crossover di sistema, protezione altoparlanti, EQ di sistema, delay/allineamento, gestione finali.
7. **[R]** Livelli: nominale 0 dBu; headroom interna pulita ≥ +24 dBu come requisito DI SISTEMA (non di ogni IC — correzione 1/2 della review).
8. **[R]** Alimentazione: rail di sistema ±24 V con regolazione locale per ogni dominio di tensione degli integrati (es. ±15 V locali).
9. **[R]** Nessun compressore/limiter/AGC nel percorso audio. Le uniche nonlinearità volute: overdrive del filtro globale e drive del 5-way.
10. **[R]** Protezione elettrica ≠ processing dinamico: restano obbligatorie protezioni DC, corto, ESD, mute power-on/off (non sono "dinamica").
11. **[R]** Buffering a bassa impedenza tra stadi/moduli. Ogni uscita (MASTER, BOOTH, REC) ha il suo buffer dedicato: mai un buffer unico splittato.
12. **[R]** Architettura stereo: no pan, controlli linked L/R, tracking ≤ 0,25 dB, mono-compatibile.
13. **[R]** Costruzione modulare su backplane. Il backplane separa fisicamente: bus audio, bus di controllo, alimentazione, ground/reference, chassis/shield. Niente connessioni a nodi interni tra moduli. Niente hot-swap. Test point sui moduli.
14. **[R]** Convenzione d'interfaccia CV 0–5 V sul backplane — è una convenzione di interfaccia, NON la tensione nativa di ogni circuito (ogni stadio può avere la sua legge interna, es. esponenziale per le frequenze).

## Canali DJ

15. **[R]** 4 canali DJ. Catena: input → gain → EQ → split CUE/FX → filtro (selettore locale) → fader → bus.
16. **[F]** Ogni canale può esistere come modulo a sé stante.
17. **[F]** EQ di canale: 4 bande in stile Xone — bassi, medio-bassi, medi, alti. Ogni knob scende fino a −∞ (full CCW = kill della banda).
18. **[F]** Frequenze e comportamenti esatti dell'EQ di canale: da rivedere insieme in seguito (non bloccati).
19. **[R]** Phono: ingressi con RIAA (costanti 3180/318/75 µs come riferimento concettuale — il circuito vero è da progettare), loading/capacità dipendenti dalla testina, terminale di terra dedicato per giradischi.

## 5-way performance EQ (il "preamp")

20. **[R]** Il 5-way sta tra i bus di canale e il master: DJ bus → 5-way → master.
21. **[F]** Le 5 bande (SUB, KICK, MID, HIGH, SUPER HI) corrispondono alle 5 vie fisiche dell'impianto di Filippo.
22. **[F]** I kill switch stanno nella sezione preamp: uno per via, tarati per spegnere interamente il segnale di quella via dell'impianto.
23. **[R]** KILL prima dell'EQ creativo: l'EQ non può ripristinare materiale killato. Il KILL va progettato come filter bank complementare (le 5 bande sommate ricostruiscono risposta piatta senza kill attivi), non come 5 filtri indipendenti.
24. **[F]** Curva del drive — piena CCW = pulito (0); a metà corsa (~50%) il 5-way lavora nel punto ottimale (es. boost +7 dB senza distorsione); oltre il 50% la saturazione entra progressivamente e interagisce con i gain di banda e con l'overdrive del filtro. Da tradurre in taper del pot + gain staging.
25. **[R]** Drive: JFET in prima istanza / BJT asimmetrico in seconda, post-EQ, con input drive e headroom globali. È un dub-preamp su misura, non un parametrico generico.

## Filtro globale

26. **[R]** Controlli: 4 condivisi (freq HPF, freq LPF, risonanza, overdrive) + selettore locale per canale HPF/OFF/LPF. (La versione precedente "controlli locali per canale" è SUPERATA.)
27. **[R]** SVF 4 poli; HPF 20 Hz–1,5 kHz; LPF 500 Hz–20 kHz; risonanza fino all'auto-oscillazione che segue il cutoff (max ~+6/+10 dBu con limiting morbido); overdrive DOPO il filtro.
28. **[F]** Riferimento sonoro: più vicino allo Sherman Filterbank che all'E&S — carattere aggressivo, risonante, personalità marcata.
29. **[F]** Auto-oscillazione usata musicalmente (non solo come colore al limite).

## Sistema FX

30. **[R]** 4 bus FX. Mandate con EQ 2 bande e switch di assegnazione. Ritorni con fader.
31. **[R]** Matrice di feedback tra FX: 12 percorsi diretti, 3 destinazioni per ritorno, niente self-route. Da progettare come rete di routing analogica unica, non come 12 hack indipendenti.
32. **[R]** Reroute PRE-fader: il fader del ritorno taglia l'audio verso il master ma NON il feedback interno.
33. **[R]** VCA analogici per il rerouting (THAT 2180 come candidato reale) con gestione di livello propria (il VCA non eredita automaticamente il +24 dBu di sistema).
34. **[F]** Interfaccia pedali: pronta SIA per pedali chitarra SIA per rack da studio → pad di mandata selezionabile (−20 dB è valore di prototipo, non congelato). Ritorno: alta impedenza (≥ 1 MΩ), alto headroom, protezione.
35. **[F/C]** I controlli della matrice vanno pensati per l'uso dal vivo: utilizzabili mentre si mixa, con via di fuga rapida (il fader taglia subito l'audio). Elettricamente identica alla versione studio.

## Mic e ingressi generici

36. **[F]** Mic: solo dinamici, NIENTE phantom 48 V. Semplifica preamp e protezioni; gain ~40-50 dB.
37. **[R]** Ingressi mono generici: architettura a modulo sorgente generico, non cucita su uno strumento specifico. Mono → stereo conversion, EQ 2 bande, clip warning, FX send.

## Master, uscite, metering

38. **[R]** MASTER LEVEL: −∞ → 0 dB → +6 dB, stadio attivo (non solo pot passivo), stereo-linked, full CCW = mute pratico. Meter DOPO il level (il meter mostra il livello reale in uscita).
39. **[R]** BOOTH: presa da MASTER SUM prima del MASTER LEVEL; −∞ → 0 dB; il master level non influenza il booth.
40. **[R]** REC: presa da MASTER SUM prima di entrambi i level; nessun controllo utente; ≈ 0 dBu al nominale.
41. **[F]** REC out → registratore Zoom (modello esatto da comunicare; implica livello/impedenza/connettore adatti all'ingresso Zoom).
42. **[R]** Uscita master: driver di linea bilanciato attivo, XLR L/R, Z out < 50 Ω ideale, capacità pulita ≥ +24 dBu, protezione corto, niente trasformatore d'uscita, nessuna colorazione intenzionale.
43. **[R]** Metering a 6 zone: blue (poco) → green (safe) → yellow (loud) → amber (hard) → red (extreme) → purple (clipping reale, con clip detector vero sul nodo).
44. **[R]** Banda complessiva target 8 Hz–35 kHz con filtro OFF (il filtro inserito limita volutamente la banda); la tolleranza esatta (es. ±0,1 dB) NON si specifica prima di misurare.

## Alimentazione

45. **[F/C]** PSU: lineare con trasformatore toroidale + regolazione locale per sezione. Nessun vincolo di peso dichiarato. Switching = piano B se il peso diventasse un problema.
46. **[R]** Power-on mute e power-off mute obbligatori. Sequencing e protezione per ramo di modulo. Budget di corrente e termico da calcolare.

## Interfaccia fisica

47. **[F]** Fader = slider; tutto il resto = potenziometri rotativi.
48. **[R]** Il design del pannello frontale è di Filippo; da Claude solo i requisiti elettrici (consumi modulo, pin connector, correnti backplane, contatti di massa, schermature, accessi di servizio/test).

## Modulo MASTER OUT — decisioni di Filippo (2026-09-18)

49. **[F]** MASTER OUT universale: deve lavorare con la maggior parte dei DSP standard, nessun processor specifico di riferimento (XLR bilanciato, 0 dBu nominale, capace di pilotare ingressi pro +4 dBu con trim, Z out < 50 Ω).
50. **[F]** REC OUT universale: compatibile con la maggior parte dei registratori standard (Zoom o equivalente): jack TRS con cablaggio unbalanced-compatible, attenuazione fissa a −10 dBV [PROVVISORIO], jumper −10/−20 dB opzionale sul PCB.
51. **[F]** Connettore BOOTH: XLR bilanciato.
52. **[F]** MASTER LEVEL con detent meccanico a unity. L'hardware di tutte le manopole (marca/modello pot, slider, cap) si rivede globalmente in una sessione dedicata più avanti.
53. **[F]** Metering master alla massima precisione possibile: scala logaritmica 20 segmenti per canale a passi 3 dB (LM3915 in cascata come candidato), attacco < 1 ms, decay regolabile, purple = clip detector indipendente con latch 0,5 s.
54. **[F]** Rail ±15 V low-noise con LT3045/LT3094 confermati (summing, CV del VCA, meter).
55. **[F]** La logica colori/zone del meter NON si reinventa: è definita nel backlog con ChatGPT e si recupera dall'export [EXPORT]. La scala elettrica a 20 segmenti è progettata indipendentemente dai colori.

## Modulo CANALE CDJ/LINE (2026-09-18)

56. **[F]** Scope fase 1 del canale: SOLO ingresso line (CDJ/line). La sezione phono/RIAA non si progetta ora; il modulo lascia spazio a una variante phono futura. Design v0.1 in `docs/fase1/cdj-line-channel.md`.
57. **[R derivato]** Split CUE e FX send sono PRE-FADER (derivato dalla catena bloccata del resoconto, voce 15): canale chiuso non zittisce CUE né FX send.

## Dalle risposte di Filippo ai 12 quesiti + status document (2026-09-18 pomeriggio)

58. **[R2]** Corpus di riferimento CHIUSO: resoconto 00 + i due status doc del 2026-09-18 (`docs/export-chatgpt/`) sono la referenza completa e definitiva. Non è possibile ottenere un export migliore della conversazione; non esiste una "project specification" separata lato ChatGPT. Le voci [EXPORT] si risolvono contro questi documenti o restano aperte in modo definitivo.
59. **[R2]** Dettagli confermati dagli status doc: canali STEREO identici; gain canale −∞→0→+10 dB con detent centrale e tracking ≤0,5 dB; EQ 4 bande −∞→0→+6 dB (LOCKED) con tracking ≤0,25 dB e law "lenta al centro, rapida agli estremi"; frequenze EQ proposte 70/250/1k/5k Hz (LOW/LOW-MID/MID-HIGH/HIGH, Q ~0,7-0,9); assignment FX multiple simultanee con precision analogue switch (JFET scartati); CUE post-EQ/pre-filter/pre-fader; return gain −∞→0→+20 dB; meter DJ completo post-filter/overdrive pre-fader con persistenza e calibrazione identica tra canali; tabella legge di reroute FX.
60. **[F]** Il MODULO FILTRO è ESTERNO ai canali (chiarimento del proprietario, corregge la lettura di docs/03 §3.3): il canale ha SOLO il selettore HPF/OFF/LPF; i 4 core filtro stereo + controlli condivisi (freq HPF, freq LPF, risonanza, overdrive) + stadio overdrive vivono nel modulo filtro dedicato. Tra canale e modulo filtro: send/return audio sul backplane + logica del selettore. L'ipotesi originale del CDJ v0.1 §3.6 è quella valida.
61. **[F]** Build order confermato (nessuno spezzamento 1a/1b necessario, dato il filtro esterno): fase 1 = canale line (senza phono; filtro su OFF/bypass finché il modulo filtro non esiste) + modulo FX + master-out + PSU base; fase 2 = modulo filtro e 5-way. Phono Rev A solo su carta.
62. **[F]** Phono V1: MM-only (copre testine DJ standard e MM di alta qualità); MC fuori scope (eventuale step-up/Rev B). Connettore RCA stereo + ground dedicato; 47 kΩ al connettore; capacità interna selezionabile con default 100 pF, accesso solo tecnico (nessun selettore user). Gain totale 40-42 dB NON congelato: si bilancia nel gain-staging globale. Primo stadio: entrambe le varianti dei documenti restano [PROVVISORIO] (21,3 dB del PDF, grounded sul PhL-100 / 26,0 dB dell'addendum DOCX, che Filippo indica come successivo) — sceglie la simulazione (rumore vs overload).
63. **[F]** REC OUT: 0 dBu nominali fissi, nessun controllo utente («la cosa più semplice e standard»); pad solder-only 0/−10/−20 dB sul PCB per registratori sensibili (accesso tecnico). Supersede la proposta −10 dBV + jumper utente.
64. **[F]** Terza banda EQ = MID-HIGH @ ~1 kHz (è ciò che Filippo chiama «medi»).
65. **[F — REQUISITO NUOVO]** Capacità infrasub ~10 Hz: il mixer deve poter scendere sotto i sub. Specifica derivata: banda complessiva −3 dB a ≤8 Hz (10 Hz entro ±1 dB); territorio del KILL SUB esteso a ~10-90 Hz; nessun accoppiamento AC con corner >5 Hz nel percorso principale (DC servo); metering leggibile anche a 10 Hz (peak detector senza sagging); HPF min esteso a 10 Hz oppure 20 Hz con posizione OFF per l'infrasub → [APERTO-F, nuova voce 49].
66. **[R2]** Riferimento impianto: typologia «5-way dub soundsystem» (i modelli specifici non contano, erano indicativi); crossover di riferimento ~90 Hz / ~350 Hz / ~1,2 kHz / ~3,5 kHz [PROVVISORIO]; espansione futura 4×SUB + 4×KICK annotata come concept.

## Modulo FILTRO — architettura scelta da Filippo (2026-09-18, "B prime")

67. **[F]** Architettura filtro = **B′**: un core filtro dedicato per canale (4 stereo, tutti nel modulo filtro esterno — decisione 60 confermata), con DUE set di parametri indipendenti e condivisi: sezione HPF (freq, resonance, overdrive) e sezione LPF (freq, resonance, overdrive) = **6 knob sul modulo filtro**. Sul modulo canale: **solo switch 3 posizioni HPF/OFF/LPF** (niente BPF — escluso esplicitamente). Tutti i canali nella stessa modalità seguono gli stessi knob. L'overdrive di canale segue il set della sezione selezionata dallo switch. Conseguenza elettrica accettata: 8 core mono (4 canali × L/R) sullo stesso PCB, con trimming per il tracking (voce 51).
68. **[F derivato — veto possibile]** HPF min esteso a **10 Hz** (range 10 Hz–1,5 kHz): conseguenza diretta del requisito infrasub (decisione 65) — con filtro inserito e knob al minimo, l'infrasub a 10 Hz resta udibile. Fattibilità del converter da verificare in simulazione SVF; se impossibile, ripiegare a 20 Hz + posizione OFF e riaprire la questione.
69. **[F]** Phono, conferma risposta "7 rca": pannello = RCA stereo + ground dedicato; loading/capacità solo interni (tecnico). Capacità selezionabile: resta come opzione economica su solder-pad/DIP interno (default ~100 pF) — non è strettamente necessaria (un valore fisso ben scelto + capacità del cavo copre il 90% dei casi MM), ma costa ~2 € e dà margine di rifinitura; se Filippo preferisce eliminarla, fisso ~150 pF.

## Legge dei knob filtro + gain staging (2026-09-18 pomeriggio)

70. **[F]** Legge dei controlli di frequenza del filtro (HPF e LPF): agli estremi della corsa il filtro **cancella tutto** (silenzio); la curva è musicale per ~il 90% centrale e **accelera fortemente negli ultimi ~5% a entrambe le estremità**. Implementazione: shaper di CV a tratti (rete diodi/resistori, tecnica standard da sintetizzatore, rifinitura a banco). Conseguenza ingegneristica [DA CONFERMA ESPLICITA]: entrambe le sezioni spazzano l'intera banda audio ~10 Hz–25 kHz (carattere Sherman) — questo SUPEREREBBE i range dei documenti (HPF 20 Hz–1,5 kHz / LPF 500 Hz–20 kHz). Range gm ~2500:1 con converter esponenziale + tempco (tecnica VCO da synth, fattibilità da verificare in simulazione SVF; niente fallback 20 Hz: Filippo rifiuta il compromesso di base).
71. **[C]** Mappa dei domini di alimentazione (sheet §1): ±24 V solo stadio HV master; ±18 V per tutto l'audio di potenza/percorso; ±15 V ultra-low-noise per phono/mic/CV/metering/CUE; +5 V control. Il gain-staging sheet (`docs/fase1/gain-staging-sheet.md`) è la referenza autorevole dei livelli.
72. **[C]** Gain totale phono: **42 dB** a 1 kHz (bilanciamento di sistema: testina 5 mV → −1,8 dBu ≈ nominale con gain di canale a 0). Split primo stadio (21,3 vs 26 dB) rinviato alla simulazione phono.
73. **[C]** 5-way con riferimento interno −6 dB: pad −6 in ingresso, makeup +6 in uscita — headroom per i boost +15 dB delle bande, nessun effetto udibile (simmetrico).

## Conferma filtro full-range + feedback comunicazione (2026-09-18)

74. **[F]** Conferma e precisione della decisione 70, nelle parole di Filippo: il filtro è fatto di **2 sezioni — una low-pass e una high-pass — entrambe tarate sul range 10 Hz–35 kHz**. Knob con curva musicale nei ~90% centrali e forte accelerazione negli ultimi ~5% a entrambe le estremità; all'estremo di taglio il segnale è cancellato del tutto (HPF in cima alla corsa, LPF in fondo). Il fallback a 20 Hz è DEFINITIVAMENTE TOLTO («di base non lo voglio»). La decisione 68 è assorbita in questa. Nota ingegneristica: range gm ~3500:1 (~11,8 ottave) via converter esponenziale + tempco; la precisione richiesta è più lasca di un VCO (un filtro tollera ±5-10% in frequenza senza che sia udibile come "stonato"); fattibilità da verificare in simulazione (fase 2); le macchine di riferimento (Sherman Filterbank, E&S) coprono range analoghi.
75. **[F — comunicazione]** Feedback di Filippo: linguaggio troppo stringato, in particolare sulle sensazioni sonore. Registrato come regola 8 del CLAUDE.md di progetto: quando si parla di suono, spiegare in modo concreto e disteso cosa si sente e in che situazione.

## Modulo CANALE CDJ — topologia EQ (2026-09-24)

76. **[F]** Topologia EQ del canale CDJ = **serie per banda (famiglia Baxandall / filtri a guadagno variabile in cascata)**. Origine: questione 62 — la simulazione LTspice (`sim/cdj-eq/RISULTATI-eq.md`) ha dimostrato che la cella a contribuzione bipolare non realizza fisicamente il kill/boost locked sulle bande LOW/HIGH (la math validata ignorava la fase dei filtri; misure: kill LOW −8 dB @20 Hz con bump +1,5 dB @70 Hz, boost HIGH ~0 dB al centro, leak all-kill −0,67 dB). Filippo sceglie l'opzione B. Proprietà da realizzare in EQ v0.3 [target ingegneristici PROVVISORI, da confermare in simulazione]: kill profondo e monotono per banda (target −20…−40 dB), boost +6 dB locked (requisito §1 immutato), detent piatto entro ±0,1-0,3 dB (tolleranze componenti — non più "zero esatto per costruzione": sotto la soglia uditiva e sotto il requisito di tracking 0,25 dB, giudicato accettabile), law "lenta al centro, rapida agli estremi" [requisito immutato]. Conseguenze: ridisegno EQ v0.3 (celle, curve, law, BOM §6); il residuo all-kill va quantificato in v0.3 (questione 59 riformulata); il metodo di tracking stereo resta aperto (questione 53: pot doppi selezionati/trim vs VCA per banda). Opzione A (bande parallele Linkwitz-Riley + VCA per banda) archiviata come alternativa documentata se la via serie non rispetterà i requisiti di kill/piattezza; opzioni C/D scartate (rattoppi). La SPECIFICA non cambia: il requisito comportamentale §1 resta, cambia il design che lo realizza.

## Modulo CANALE CDJ — profondità kill EQ (2026-09-24)

77. **[F]** Profondità del kill per banda dell'EQ in serie (celle v0.3, decisione 76) = **−30 dB** (rapporto di rete Rp/R ≈ 31). Scelta tra −30 (raccomandazione di Claude: impedenze basse, rumore contenuto, ~3% di ampiezza residua = il basso sparisce percepito in un mix) e −40 (più margine sulle sovrapposizioni, reti più rumorose). Il silenzio assoluto resta lavoro del fader: il kill è un gesto musicale, non un mute. Dimostrazione misurata: `sim/eq-serie/low-cell.cir` (−29,8 dB monotoni, nessun bump) + `docs/fase1/eq-serie-v0.3.md` §2. La v0.3-beta progetta le reti di tutte e 4 le bande su questa profondità (chiusa la questione 66).

## Prototipazione musicale digitale (2026-09-24)

78. **[F]** Prima del prototipo su millefori si costruisce un **prototipo musicale in Max for Live** (Ableton Live Suite, controllo a mouse) del **mixer completo**: catena canali → EQ serie → filtro globale → 5-way → bus FX con matrice di feedback → master, in fasi giocabili successive. Scopo: validare A ORECCHIO gesto, curve, leggi dei controlli e carattere musicale PRIMA di spendere in componenti; chiudere le questioni musicali pendenti (61 drive/referenze, 63 mux filtro, 64 allineamento 4 poli, review centri EQ, taper) con ascolti A/B immediati. Il metodo della fase circuitale resta intatto: il prototipo M4L valida la MUSICA, non l'elettricità (rumore, saturazione OTA reale, tracking meccanico restano di competenza del millefori e delle misure). Piano: `docs/proto-max/piano.md`; le patch vivono nel repo (`proto-max/`) come .maxpat versionati, assemblati in dispositivi .amxd dentro Live (procedura documentata). Regola pratica: le curve/leggi approvate a orecchio nel prototipo diventano requisito per il design circuitale corrispondente.
