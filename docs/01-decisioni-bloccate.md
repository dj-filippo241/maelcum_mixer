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
