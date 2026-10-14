# CLAUDE.md — maelcum_mixer

## Cos'è questo progetto

Mixer dub modulare 100% analogico, **esemplare unico**, per il soundsystem a 5 vie di Filippo (grafico/DJ, non programmatore — spiegare sempre in linguaggio semplice, vedi il suo CLAUDE.md personale). Architettura: 4 canali DJ, filtro globale condiviso (stile Sherman), 5-way performance EQ/dub preamp con kill per via, 4 bus FX con matrice di feedback, mic, moduli mono generici, master/booth/rec, CUE, metering 6 zone. Filosofia: 0 dBu nominale, headroom di sistema ≥ +24 dBu, nessuna dinamica automatica, nonlinearità solo dove voluta.

Il repository non contiene software da compilare né test: contiene documenti di design (`docs/`) e simulazioni di circuito LTspice (`sim/`).

## Regole del progetto

1. **Una decisione, un posto solo.** Le decisioni bloccate stanno in `docs/01-decisioni-bloccate.md`; le aperte in `docs/02-questioni-aperte.md`; la specifica consolidata in `SPECIFICA.md` (v0.1, rev. 2026-10-14: decisioni 76-111). Quando una questione si chiude: spostarla da 02 a 01 con data e origine [F]/[R]/[C], e aggiornare la specifica.
2. **Non inventare decisioni di design.** Le scelte sonore/ergonomiche sono di Filippo. L'ingegneria (topologie, componenti, simulazioni, calcoli) è di Claude, ma i numeri che vincolano l'uso musicale vanno mostrati e confermati.
3. **Niente valori congelati prima della topologia.** Regola ereditata dalla review: mai fissare valori di componenti prima di aver scelto il circuito. Distinguere sempre [BLOCCATO] / [PROVVISORIO] / [APERTO] / [SUPERATO].
4. **Metodo della fase circuitale**: requisito funzionale → funzione di trasferimento → topologia → componenti → simulazione → vincoli PCB → prototipo → misura → revisione.
5. **Ordine di costruzione rispettato**: fase 1 = modulo canale + FX + master out + PSU base (valida il backplane); fase 2 = 5-way e filtro. Non progettare la fase 2 nei dettagli prima che la fase 1 abbia insegnato qualcosa.
6. **Documenti in italiano**; la terminologia tecnica audio/elettronica resta in inglese dove è standard (headroom, summing, feedback, taper...).
7. Niente emoji nei file (hook attivo).
8. **Lingua e registro (feedback Filippo 2026-09-18)**: quando il discorso tocca l'orecchio — sensazioni sonore, impatto musicale di una scelta tecnica — usare un linguaggio disteso e concreto: spiegare cosa si sente, in che situazione, con che gesto. La sintesi va bene per la contabilità di progetto, non per la musica.
9. **Questo file resta corto.** Qui sta solo lo stato corrente. La cronaca di una sessione (finding, tentativi, numeri superati) va in `docs/storico-sessioni.md` o nel design doc del modulo, non qui.
10. **Archiviato non vuol dire cancellato.** I design superati (drive v0.3, overdrive v0.1, EQ a contribuzione bipolare, VAS discreto) restano nel repository come alternativa o come prova del vicolo cieco.

Origine delle decisioni: **[F]** = detta da Filippo · **[R]** = dal resoconto ChatGPT · **[C]** = proposta di Claude accettata da Filippo.

## Comandi

Simulare un netlist (LTspice 26.0.2 in batch; avvio 30-60 s; il log esce accanto al netlist e viene stampato):

```bash
sim/run_ltspice.sh sim/five-way/module-noise-v04.cir
# con limite di tempo (su macOS `timeout` non esiste):
perl -e 'alarm shift; exec @ARGV' 120 sim/run_ltspice.sh sim/filtro/od2-chain.cir
```

Leggere un log (Python puro, nessun pacchetto da installare):

```bash
python3 sim/mic/noise_total.py <log> [<log> ...]   # totali di rumore piatto e A-wtd da 16 punti di densità
python3 sim/fourier_tab.py <log>                   # THD, H2, H3 dai blocchi .four
python3 sim/drive2_tab.py <log>                    # griglia drive v0.4 (log di drive2-chain*)
python3 sim/shaper/shaper_fit.py                   # fit dei valori di uno shaper a diodi
python3 docs/diagrammi/genera_diagrammi.py         # rigenera gli SVG: SOLO se Filippo lo chiede
```

Regole di simulazione (ognuna nasce da un errore già pagato; il contesto sta nello storico):

- `.log`, `.raw` e `.db` sono fuori da git (`.gitignore`). Un risultato esiste solo se è trascritto in un `sim/<cartella>/RISULTATI-*.md` o nel design doc, col nome del netlist che lo produce.
- I netlist includono le librerie condivise con percorso relativo (`.include ../lib/opamp-audio.inc`, `that2181.inc`, `lm13700.inc`). Un modello corretto in `sim/lib/` vale per tutti; le macro copiate inline vanno corrette a mano.
- Rumore: mai `.meas INTEG` su `.noise` (LTspice 26.0.2 restituisce en²·√Δf: totali ~21,5 dB ottimisti). Si misura la densità `V(onoise)` a 10-16 punti e si integra con `noise_total.py`. Metodo: five-way §8.9. I totali √INTEG nei documenti anteriori al 2026-09-30 sono invalidi; valgono quelli di `docs/06`.
- Sorgenti di rumore e op-amp: solo sorgenti `E` lineari a 4 nodi. Una `E` comportamentale non propaga il rumore nel `.noise`.
- Subckt del VCA insieme alla banca Sallen-Key: errore di parse («Instance already defined»). Mettere il VCA inline con nomi unici.
- `SINE` vuole il valore di picco: 0 dBu = 1,095 Vp, non 0,775.
- THD: leggere sempre Partial E Total (`fourier_tab.py` li stampa entrambi). Total molto sopra Partial non è distorsione armonica: guardare la forma d'onda.
- `.meas ac`: `FIND V(nodo)`, mai `FIND dB(V(nodo))`. Serve uno sweep (`.ac dec ...`), non `.ac list` con un punto solo.
- `.tran` con anelli di retroazione: `.nodeset` obbligatorio. Macro op-amp in due varianti: specchio lineare per `.ac`/`.noise`, `abs` per `.tran`.
- Sallen-Key high-pass: R_fb = R_gnd/2 per Q 0,707.
- Alimentatori: simulare il trasformatore con EMF a vuoto e resistenza d'avvolgimento, mai ideale (corrente efficace d'avvolgimento ~1,9× la DC).
- SVF con OTA della RES a Iabc quasi zero: il `.op` non converge (9 minuti a vuoto). Usare `.tran ... uic` e misurare il segnale con `PP`, non `RMS`: col partitore l'offset dell'OTA sale di 1/k.
- Non fermare LTspice con `pkill -f <nome netlist>`: uccide anche lo script. `drive2-chain` a 150 Hz non termina (causa ignota): usare 50 Hz o 1 kHz.

## Stato corrente (2026-10-14, decisioni 1-111)

Il design teorico (carta + simulazione) è completo per tutti i moduli. Il prototipo musicale in Max for Live (dec. 78) è in pausa e precede il millefori. Gli acquisti sono sospesi fino al prototipo.

| Modulo | Versione corrente | Documento | Simulazioni |
|---|---|---|---|
| Canale CDJ/line | v0.4; EQ = ISOLATOR a 4 bande v0.4-beta (dec. 105: bande in parallelo, contatto di fondo corsa per banda; incroci 150/500/2500 Hz di partenza, da sentire). Integrato nel canale: somma non invertente, polarità diritta (eq-isolator §9) | `docs/fase1/cdj-line-channel.md`, `eq-isolator-v0.4.md` | `sim/cdj/`, `sim/eq-iso/` |
| Phono MM | v0.1 + REV 2026-09-30 (RIAA passiva 42 dB, dec. 79) | `docs/fase1/phono-stage.md` | `sim/cdj/phono-*` |
| FX + FX-SEND ×4 | v0.3-WIP (matrice 16× VCA con self-feedback, dec. 91) | `docs/fase1/fx-module.md`, `fx-send-module.md` | `sim/fx/` |
| Master out | v0.3 DEFINITIVA (bootstrap rail OPA1612, dec. 83/86) | `docs/fase1/master-out.md` | `sim/master-out/compB-*` |
| Filtro | v0.2; un percorso per canale (dec. 101, 8 core); law Xone:96 (dec. 102); overdrive v0.2 §5ter (dec. 99); core OTA (a′) con partitore 1/30 §5quater (dec. 109: il core nudo non funziona col chip reale; B1 aperta); numeri col chip reale accettati (dec. 110: oscillazione ~+5 dBu, calo di nota = carattere) | `docs/fase2/filter-module.md` | `sim/filtro/` |
| 5-way | v0.3; celle v0.2.1; kill a switch §8.10 (dec. 88); drive v0.4 GROWL + NASTRO §5bis (dec. 99) | `docs/fase2/five-way-module.md` | `sim/five-way/` |
| Mic e Mono | v0.1, due moduli separati, max 4 (dec. 97) | `docs/fase4/mic-mono-moduli.md` | `sim/mic/` |
| Sistema | PSU ~250 VA (dec. 93/98/106; W1 3,5 A per i moduli opzionali, dec. 111; ~114-131 W da smaltire senza ventola), grounding, backplane, metering (dec. 81/90), CUE (dec. 96), shaper, inventario comandi | `docs/fase3/` | `sim/system/`, `sim/meter/`, `sim/shaper/` |

Review contro il benchmark (dec. 111): ibrido DJ / sound system / live, nessun fork, moduli opzionali predisposti (uscite per via, crossfader, EQ grafico, sirena), tasto MONO master, MUTE mic, ambiente da sound system all'aperto (`docs/07`, `docs/08`).

Documenti trasversali: `docs/fase1/gain-staging-sheet.md` (livelli e domini, referenza unica), `docs/06-ritaratura-rumore-71A.md` (budget di rumore e target ratificati), `docs/proto-max/piano.md` (prototipo Max).

Numeri di sistema: rumore −82,9 dBu A-wtd a filtri OFF (docs/06 §10: canale con isolator −94,6, 5-way −85,9) (target ≤ −78, dec. 89; condizioni d'uso accettate con FX e overdrive aperti, dec. 95/100); master +25,4…+25,6 dBu (requisito ≥ +24). VCA: THAT 218x fuori produzione, rotta clone CoolAudio V2181L, ~34-36 chip.

Trappole di lettura:

- **Superati, non usare come base**: `sim/cdj-eq/` e `sim/eq_analysis.py` (EQ a contribuzione bipolare), `sim/eq-serie/` e `eq-serie-v0.3.md` (EQ in serie, archiviato dalla dec. 105; le dec. 103 e 104 sono revocate), `sim/master-out/compG-*` (VAS discreto), `sim/five-way/drive-*` (drive v0.3, archiviato), filter-module §5bis (overdrive v0.1), griglia drive dec. 87.
- **Servo DC**: filtro (overdrive §5ter), 5-way (§5bis.7) ed EQ isolator (§8) usano la stessa cella: integratore invertente che entra dal piedino + dello stadio attraverso un partitore. Iniettare nel nodo di somma dà retroazione positiva.
- **Diagrammi**: gli SVG di 5-way, filtro e mic/mono sono vecchi. Si rigenerano solo su richiesta di Filippo.
- Il modulo mic/mono è un precedente: una prima stesura con comandi decisi da Claude è stata bocciata. Pannello, comandi e divisione in moduli li decide Filippo.

## Prossimo passo

La coda vive in tre posti, non qui:

- **Decisioni di Filippo e ingegneria residua**: liste A, B e C in testa a `docs/02-questioni-aperte.md`.
- **Todo**: `arturo todo --progetto .`
- **Ultima sessione**: handoff in `~/.claude/data/handoffs/maelcum-mixer/`.

## Dove sta cosa

```
SPECIFICA.md                  specifica consolidata
docs/01-decisioni-bloccate.md cosa è deciso (111 voci; 103 e 104 revocate)
docs/02-questioni-aperte.md   cosa manca: liste A/B/C in testa, storico delle voci sotto
docs/03 … 08                  revisione critica, architettura filtro, benchmark, rumore, review
docs/storico-sessioni.md      cronaca delle sessioni fino al 2026-10-13
docs/fase1 … fase4/           design doc per modulo (tabella sopra)
docs/diagrammi/               SVG generati da genera_diagrammi.py
docs/export-chatgpt/, docs/00 materiale d'origine, chiuso (dec. 58)
sim/lib/                      modelli condivisi: op-amp, THAT 2181, LM13700
sim/<modulo>/                 netlist .cir + RISULTATI-*.md
sim/run_ltspice.sh            wrapper per LTspice in batch
```
