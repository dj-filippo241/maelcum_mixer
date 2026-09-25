# CLAUDE.md — maelcum_mixer

## Cos'è questo progetto

Mixer dub modulare 100% analogico, **esemplare unico**, per il soundsystem a 5 vie di Filippo (grafico/DJ, non programmatore — spiegare sempre in linguaggio semplice, vedi il suo CLAUDE.md personale). Architettura: 4 canali DJ, filtro globale condiviso (stile Sherman), 5-way performance EQ/dub preamp con kill per via, 4 bus FX con matrice di feedback, mic, moduli mono generici, master/booth/rec, CUE, metering 6 zone. Filosofia: 0 dBu nominale, headroom di sistema ≥ +24 dBu, nessuna dinamica automatica, nonlinearità solo dove voluta.

## Fase attuale

**Corpus ChatGPT CHIUSO (2026-09-18).** Non arriverà un export migliore: resoconto (`docs/00-...`) + due status doc (`docs/export-chatgpt/`) = referenza completa (decisione 58). Revisione critica FATTA: `docs/03-revisione-critica.md`. Architettura filtro decisa: `docs/04-architettura-filtro-e-diagramma.md` + decisioni 67/70/74 (B′, 2 sezioni full-range 10 Hz–35 kHz). Gain-staging sheet FATTO: `docs/fase1/gain-staging-sheet.md` (chiude questioni 31/47/52, gain phono 42 dB, mappa domini). SPECIFICA.md v0.1 FATTA. Simulazioni LTspice dell'EQ FATTE (2026-09-24, `sim/cdj-eq/RISULTATI-eq.md`): **finding critico** — la cella a contribuzione bipolare non può fisicamente realizzare il kill/boost LOW/HIGH (la math validata ignorava la fase dei filtri); Filippo ha deciso: **EQ in serie per banda, famiglia Baxandall (decisione 76)**. EQ v0.3 **BETA-2 FATTA** (2026-09-25, `docs/fase1/eq-serie-v0.3.md` + `sim/eq-serie/`): celle LOW/MID/HIGH + cascata 4 bande — detent ±0,02 dB, kill −30 dB (decisione 77), riferimento interno −6 dB, law/taper specificata; integrata in `cdj-line-channel.md` **v0.3**. **Decisione 78**: prototipo MUSICALE del mixer completo in Max for Live PRIMA del millefori — piano fasi P0-P4 in `docs/proto-max/piano.md` (valida a orecchio curve/law/carattere; chiude 61/63/64/67/68; il millefori resta la porta elettrica). **IN PAUSA per direzione Filippo 2026-09-25: prima finire tutto il design.** Design modulo filtro **v0.2** FATTO (`docs/fase2/filter-module.md`): converter 10 Hz–35 kHz dimostrato, risonanza→auto-oscillazione +7,3…+8,6 dBu con soft limiter SIMULATA (questione 11), distribuzione mirror bufferizzati tracking ≤1,6% (51), law shaper specificato. Modulo **FX v0.1** FATTO (`docs/fase1/fx-module.md`): loop feedback bounded-by-design simulato, matrice 12× THAT 2181. **5-WAY v0.1** FATTO (`docs/fase2/five-way-module.md`): kill bank LR4 + gate VCA validato (all-kill = silenzio assoluto); finding: la somma piatta richiede banca allineata in fase (v0.2). Fix trasversale 2026-09-25: SK high-pass vuole R_fb = R_gnd/2 per Q 0,707 (bug ereditato da v0.2, corretto ovunque).

**Deroga registrata (2026-09-18)**: Filippo ha autorizzato l'avvio del design di fase 1 SENZA attendere l'export. Si lavora solo su sezioni già giudicate solide dalla review o con architettura bloccata. Stato design: **MASTER OUT v0.2** (risposte di Filippo integrate, decisioni 49-55) e **CANALE CDJ/LINE v0.2** (phono escluso per ora, decisione 56; §3.3 EQ in serie — v0.3, decisioni 76/77) e **FX v0.1** in `docs/fase1/`, **MODULO FILTRO v0.2** e **5-WAY v0.1** in `docs/fase2/`. Export chiuso (decisione 58): le voci [EXPORT] sono risolte dalla revisione critica o definitivamente aperte.

## Regole del progetto

1. **Una decisione, un posto solo.** Le decisioni bloccate stanno in `docs/01-decisioni-bloccate.md`; le aperte in `docs/02-questioni-aperte.md`; la specifica consolidata in `SPECIFICA.md` (v0.1, rev. 2026-09-24: decisioni 76-78). Quando una questione si chiude: spostarla da 02 a 01 con data e origine [F]/[R]/[C], e aggiornare la specifica.
2. **Non inventare decisioni di design.** Le scelte sonore/ergonomiche sono di Filippo. L'ingegneria (topologie, componenti, simulazioni, calcoli) è di Claude, ma i numeri che vincolano l'uso musicale vanno mostrati e confermati.
3. **Niente valori congelati prima della topologia.** Regola ereditata dalla review: mai fissare valori di componenti prima di aver scelto il circuito. Distinguere sempre [BLOCCATO] / [PROVVISORIO] / [APERTO] / [SUPERATO].
4. **Metodo della fase circuitale**: requisito funzionale → funzione di trasferimento → topologia → componenti → simulazione → vincoli PCB → prototipo → misura → revisione.
5. **Ordine di costruzione rispettato**: fase 1 = modulo canale + FX + master out + PSU base (valida il backplane); fase 2 = 5-way e filtro. Non progettare la fase 2 nei dettagli prima che la fase 1 abbia insegnato qualcosa.
6. **Documenti in italiano**; la terminologia tecnica audio/elettronica resta in inglese dove è standard (headroom, summing, feedback, taper...).
7. Niente emoji nei file (hook attivo).
8. **Lingua e registro (feedback Filippo 2026-09-18)**: quando il discorso tocca l'orecchio — sensazioni sonore, impatto musicale di una scelta tecnica — usare un linguaggio disteso e concreto: spiegare cosa si sente, in che situazione, con che gesto. La sintesi va bene per la contabilità di progetto, non per la musica.

## Struttura

```
maelcum_mixer/
├── CLAUDE.md              ← questo file (contesto per Claude)
├── SPECIFICA.md           ← specifica consolidata (v0.1, rev. 2026-09-24: decisioni 76-78)
└── docs/
    ├── 00-resoconto-chatgpt-2026-09-17.md  ← materiale grezzo parziale
    ├── 01-decisioni-bloccate.md            ← cosa è deciso (78 voci)
    ├── 02-questioni-aperte.md              ← cosa manca + roadmap
    ├── 03-revisione-critica.md             ← analisi status doc (findings + correzioni)
    ├── export-chatgpt/                     ← PDF/DOCX di stato + estrazioni testo
    ├── fase1/
    │   ├── master-out.md                   ← design modulo master out (v0.2 + addendum REC)
    │   ├── cdj-line-channel.md             ← design modulo canale CDJ/line (v0.3: EQ in serie, dec. 76/77)
    │   ├── eq-serie-v0.3.md                ← ridisegno EQ in serie Baxandall (BETA-2: celle + cascata + law/taper)
    │   ├── fx-module.md                    ← design modulo FX (v0.1: bus/pedali/matrice feedback, loop simulato)
    │   └── gain-staging-sheet.md           ← tabella unica livelli e domini (referenza)
    ├── fase2/
    │   ├── filter-module.md                ← design modulo filtro (v0.2: risonanza/distribuzione/shaper simulati)
    │   └── five-way-module.md              ← design 5-way dub preamp (v0.1: kill bank LR4 validato)
    ├── proto-max/
    │   └── piano.md                        ← piano prototipo Max for Live (dec. 78, fasi P0-P4 — IN PAUSA: prima il design)
    └── (radice) sim/                       ← analisi e simulazioni: eq_analysis.py (math superata), cdj-eq/ (+RISULTATI-eq.md), eq-serie/ (celle serie beta-2), filtro/ (converter+risonanza+mirror), fx/ (loop+summing), five-way/ (bank LR4), master-out/, run_ltspice.sh (wrapper CLI)
```

## Prossimo passo concreto

FATTI (al 2026-09-25): gain-staging sheet, SPECIFICA.md v0.1 (rev. decisioni 76-78), CDJ v0.3, LTspice via wrapper `sim/run_ltspice.sh` (il launcher ufficiale perde i flag CLI), simulazioni master-out (questione 60), EQ CDJ v0.2 (finding critico → decisione 76), EQ serie beta-1/beta-2 (decisione 77: kill −30 dB), filtro v0.2 (risonanza/oscillazione/mirror/shaper), FX v0.1 (loop feedback, summing), 5-way v0.1 (kill bank LR4 validato; fix trasversale Q HP2), piano M4L (decisione 78, IN PAUSA: prima tutto il design — direzione Filippo 2026-09-25). **Tutti i moduli principali hanno un design v0.x.** IN ATTESA: decisioni di Filippo su questioni 53/59/60/61/63/64/68/69 + ratifica 55. Poi (in ordine): **5-way v0.2** (banca allineata in fase — sblocca il requisito somma piatta; parametriche complete), EQ beta-3 (op-amp reali, trim), FX v0.2, filtro v0.3 (mux + ramp), simulazioni CDJ §7 residue (VCA THAT 2181, peak detector, summing), design di sistema (PSU/CUE/metering/backplane), poi ripresa M4L P0.
