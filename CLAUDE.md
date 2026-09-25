# CLAUDE.md — maelcum_mixer

## Cos'è questo progetto

Mixer dub modulare 100% analogico, **esemplare unico**, per il soundsystem a 5 vie di Filippo (grafico/DJ, non programmatore — spiegare sempre in linguaggio semplice, vedi il suo CLAUDE.md personale). Architettura: 4 canali DJ, filtro globale condiviso (stile Sherman), 5-way performance EQ/dub preamp con kill per via, 4 bus FX con matrice di feedback, mic, moduli mono generici, master/booth/rec, CUE, metering 6 zone. Filosofia: 0 dBu nominale, headroom di sistema ≥ +24 dBu, nessuna dinamica automatica, nonlinearità solo dove voluta.

## Fase attuale

**Corpus ChatGPT CHIUSO (2026-09-18).** Non arriverà un export migliore: resoconto (`docs/00-...`) + due status doc (`docs/export-chatgpt/`) = referenza completa (decisione 58). Revisione critica FATTA: `docs/03-revisione-critica.md`. Architettura filtro decisa: `docs/04-architettura-filtro-e-diagramma.md` + decisioni 67/70/74 (B′, 2 sezioni full-range 10 Hz–35 kHz). Gain-staging sheet FATTO: `docs/fase1/gain-staging-sheet.md` (chiude questioni 31/47/52, gain phono 42 dB, mappa domini). SPECIFICA.md v0.1 FATTA. Simulazioni LTspice dell'EQ FATTE (2026-09-24, `sim/cdj-eq/RISULTATI-eq.md`): **finding critico** — la cella a contribuzione bipolare non può fisicamente realizzare il kill/boost LOW/HIGH (la math validata ignorava la fase dei filtri); Filippo ha deciso: **EQ in serie per banda, famiglia Baxandall (decisione 76)**. EQ v0.3-ALPHA FATTA (2026-09-24, `docs/fase1/eq-serie-v0.3.md` + `sim/eq-serie/`): cella LOW dimostrata — detent −0,02 dB, kill −29,8 dB monotono senza bump, boost +5,8 dB shelf liscio; profondità kill decisa −30 dB (**decisione 77**). **Decisione 78**: prototipo MUSICALE del mixer completo in Max for Live PRIMA del millefori — piano fasi P0-P4 in `docs/proto-max/piano.md` (valida a orecchio curve/law/carattere; chiude 61/63/64/67; il millefori resta la porta elettrica). Design modulo filtro v0.1 FATTO (2026-09-24, `docs/fase2/filter-module.md`): fattibilità del core SVF OTA + converter esponenziale tempcompensato DIMOSTRATA in simulazione (questione 49 chiusa, 51 aggiornata; due nuove voci APERTO-F nel documento §8).

**Deroga registrata (2026-09-18)**: Filippo ha autorizzato l'avvio del design di fase 1 SENZA attendere l'export. Si lavora solo su sezioni già giudicate solide dalla review o con architettura bloccata. Stato design: **MASTER OUT v0.2** (risposte di Filippo integrate, decisioni 49-55) e **CANALE CDJ/LINE v0.2** (phono escluso per ora, decisione 56; §3.3 EQ SUPERATO in parte → decisione 76; ridisegno in `docs/fase1/eq-serie-v0.3.md`, alpha fatta) in `docs/fase1/`, **MODULO FILTRO v0.1** in `docs/fase2/`. Export chiuso (decisione 58): le voci [EXPORT] sono risolte dalla revisione critica o definitivamente aperte.

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
    │   ├── cdj-line-channel.md             ← design modulo canale CDJ/line (v0.2; §3.3 EQ SUPERATO in parte → decisione 76)
    │   ├── eq-serie-v0.3.md                ← ridisegno EQ in serie Baxandall (ALPHA: cella LOW dimostrata; dec. 76/77)
    │   └── gain-staging-sheet.md           ← tabella unica livelli e domini (referenza)
    ├── fase2/
    │   └── filter-module.md                ← design modulo filtro (v0.1 + fattibilità dimostrata)
    ├── proto-max/
    │   └── piano.md                        ← piano prototipo Max for Live (dec. 78, fasi P0-P4)
    └── (radice) sim/                       ← analisi e simulazioni: eq_analysis.py (math, zero-fase su LOW/HIGH: superata), cdj-eq/ (LTspice EQ + RISULTATI-eq.md), eq-serie/ (celle serie v0.3), filtro/ (feas-svf.cir), master-out/, run_ltspice.sh (wrapper CLI)
```

## Prossimo passo concreto

FATTI: gain-staging sheet, SPECIFICA.md v0.1 (rev. decisioni 76-78), CDJ v0.2, LTspice via wrapper `sim/run_ltspice.sh` (il launcher ufficiale perde i flag CLI), simulazioni master-out composite (questione 60), simulazioni EQ CDJ (finding critico → decisione 76), EQ v0.3-ALPHA cella LOW (decisione 77: kill −30 dB), design filtro v0.1 + fattibilità converter (49 chiusa), piano prototipo Max for Live (decisione 78). IN ATTESA: decisioni di Filippo su questioni 53 (tracking pot vs VCA), 59 (residuo all-kill, dopo v0.3-beta), 60 (swing master), 61 (referenze distorsione), 63/64 (mux filtro, allineamento 4 poli — si chiudono a orecchio nel prototipo M4L), 65 (EQ2 FX), 67 (freq 5-way). Poi (in ordine): **EQ v0.3-beta** (celle MID/HIGH, cascata 4 bande, rumore/livelli, integrazione CDJ v0.3), **prototipo M4L P0** (`MC-CHANNEL` + montaggio in Live), modulo filtro v0.2, simulazioni restanti CDJ §7 (VCA THAT 2181, peak detector, summing DJ BUS).
