# CLAUDE.md — maelcum_mixer

## Cos'è questo progetto

Mixer dub modulare 100% analogico, **esemplare unico**, per il soundsystem a 5 vie di Filippo (grafico/DJ, non programmatore — spiegare sempre in linguaggio semplice, vedi il suo CLAUDE.md personale). Architettura: 4 canali DJ, filtro globale condiviso (stile Sherman), 5-way performance EQ/dub preamp con kill per via, 4 bus FX con matrice di feedback, mic, moduli mono generici, master/booth/rec, CUE, metering 6 zone. Filosofia: 0 dBu nominale, headroom di sistema ≥ +24 dBu, nessuna dinamica automatica, nonlinearità solo dove voluta.

## Fase attuale

**In attesa dell'export completo di ChatGPT.** Il progetto nasce da mesi di conversazioni con ChatGPT; il resoconto parziale ricevuto il 2026-09-17 è in `docs/00-resoconto-chatgpt-2026-09-17.md`. Quando arriva l'export: revisione critica completa, poi si compila `SPECIFICA.md`.

**Deroga registrata (2026-09-18)**: Filippo ha autorizzato l'avvio del design di fase 1 SENZA attendere l'export. Si lavora solo su sezioni già giudicate solide dalla review o con architettura bloccata. Primo modulo: **MASTER OUT** — design v0.1 in `docs/fase1/master-out.md`; resta da verificare contro l'export (in particolare: chi esegue il summing, standard I/O del backplane, posizione del meter).

## Regole del progetto

1. **Una decisione, un posto solo.** Le decisioni bloccate stanno in `docs/01-decisioni-bloccate.md`; le aperte in `docs/02-questioni-aperte.md`; la specifica consolidata in `SPECIFICA.md` (ora scheletro). Quando una questione si chiude: spostarla da 02 a 01 con data e origine [F]/[R]/[C], e aggiornare la specifica.
2. **Non inventare decisioni di design.** Le scelte sonore/ergonomiche sono di Filippo. L'ingegneria (topologie, componenti, simulazioni, calcoli) è di Claude, ma i numeri che vincolano l'uso musicale vanno mostrati e confermati.
3. **Niente valori congelati prima della topologia.** Regola ereditata dalla review: mai fissare valori di componenti prima di aver scelto il circuito. Distinguere sempre [BLOCCATO] / [PROVVISORIO] / [APERTO] / [SUPERATO].
4. **Metodo della fase circuitale**: requisito funzionale → funzione di trasferimento → topologia → componenti → simulazione → vincoli PCB → prototipo → misura → revisione.
5. **Ordine di costruzione rispettato**: fase 1 = modulo canale + FX + master out + PSU base (valida il backplane); fase 2 = 5-way e filtro. Non progettare la fase 2 nei dettagli prima che la fase 1 abbia insegnato qualcosa.
6. **Documenti in italiano**; la terminologia tecnica audio/elettronica resta in inglese dove è standard (headroom, summing, feedback, taper...).
7. Niente emoji nei file (hook attivo).

## Struttura

```
maelcum_mixer/
├── CLAUDE.md              ← questo file (contesto per Claude)
├── SPECIFICA.md           ← specifica consolidata (ora scheletro, si compila post-export)
└── docs/
    ├── 00-resoconto-chatgpt-2026-09-17.md  ← materiale grezzo parziale
    ├── 01-decisioni-bloccate.md            ← cosa è deciso (48 voci)
    ├── 02-questioni-aperte.md              ← cosa manca + roadmap
    └── fase1/
        └── master-out.md                   ← design circuitale modulo master (v0.1)
```

## Prossimo passo concreto

Appena Filippo consegna l'export di ChatGPT: salvarlo in `docs/export-chatgpt/`, leggerlo tutto, produrre `docs/03-revisione-critica.md` (coerente / contraddittorio / mancante / superato), poi iniziare a compilare `SPECIFICA.md` capitolo per capitolo, mostrandoli uno alla volta.
