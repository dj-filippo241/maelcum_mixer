# CLAUDE.md — maelcum_mixer

## Cos'è questo progetto

Mixer dub modulare 100% analogico, **esemplare unico**, per il soundsystem a 5 vie di Filippo (grafico/DJ, non programmatore — spiegare sempre in linguaggio semplice, vedi il suo CLAUDE.md personale). Architettura: 4 canali DJ, filtro globale condiviso (stile Sherman), 5-way performance EQ/dub preamp con kill per via, 4 bus FX con matrice di feedback, mic, moduli mono generici, master/booth/rec, CUE, metering 6 zone. Filosofia: 0 dBu nominale, headroom di sistema ≥ +24 dBu, nessuna dinamica automatica, nonlinearità solo dove voluta.

Il repository non contiene software da compilare né test: contiene documenti di design (`docs/`) e simulazioni di circuito LTspice (`sim/`).

## Regole del progetto

1. **Una decisione, un posto solo.** Le decisioni bloccate stanno in `docs/01-decisioni-bloccate.md`; le aperte in `docs/02-questioni-aperte.md`; la specifica consolidata in `SPECIFICA.md` (v0.1, rev. 2026-10-21: decisioni 76-129; dec. 131 annotata). Quando una questione si chiude: spostarla da 02 a 01 con data e origine [F]/[R]/[C], e aggiornare la specifica.
2. **Non inventare decisioni di design.** Le scelte sonore/ergonomiche sono di Filippo. L'ingegneria (topologie, componenti, simulazioni, calcoli) è di Claude, ma i numeri che vincolano l'uso musicale vanno mostrati e confermati.
3. **Niente valori congelati prima della topologia.** Regola ereditata dalla review: mai fissare valori di componenti prima di aver scelto il circuito. Distinguere sempre [BLOCCATO] / [PROVVISORIO] / [APERTO] / [SUPERATO].
4. **Metodo della fase circuitale**: requisito funzionale → funzione di trasferimento → topologia → componenti → simulazione → vincoli PCB → prototipo → misura → revisione.
5. **Ordine di costruzione rispettato**: fase 1 = modulo canale + FX + master out + PSU base (valida il backplane); fase 2 = 5-way e filtro. Non progettare la fase 2 nei dettagli prima che la fase 1 abbia insegnato qualcosa.
6. **Documenti in italiano**; la terminologia tecnica audio/elettronica resta in inglese dove è standard (headroom, summing, feedback, taper...).
7. Niente emoji nei file (hook attivo).
8. **Lingua e registro (feedback Filippo 2026-09-18)**: quando il discorso tocca l'orecchio — sensazioni sonore, impatto musicale di una scelta tecnica — usare un linguaggio disteso e concreto: spiegare cosa si sente, in che situazione, con che gesto. La sintesi va bene per la contabilità di progetto, non per la musica.
9. **Questo file resta corto.** Qui sta solo lo stato corrente. La cronaca di una sessione (finding, tentativi, numeri superati) va in `docs/storico-sessioni.md` o nel design doc del modulo, non qui.
10. **Archiviato non vuol dire cancellato.** I design superati (drive v0.3, overdrive v0.1, EQ a contribuzione bipolare, VAS discreto) restano nel repository come alternativa o come prova del vicolo cieco.
11. **Dove è verificato.** Ogni consegna del prototipo chiude con la riga «Verificato in: Python / LTspice / Live (sì o no)». Passare le prove in Python non vuol dire funzionare in Live: è successo almeno 6 volte (15/10, 29/10, 31/10). Rapporto BURN del 4/11.

Origine delle decisioni: **[F]** = detta da Filippo · **[R]** = dal resoconto ChatGPT · **[C]** = proposta di Claude accettata da Filippo.

## Comandi

KiCad 10.0.7 sta in `/Applications/KiCad` (copiato dal .dmg: `brew install --cask kicad` vuole sudo e fallisce senza terminale; Homebrew non lo gestisce). CLI: `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`. Schemi e PCB ripartiti il 2026-10-27 (richiesta di Filippo): ogni scheda nasce da `pcb/<modulo>/<modulo>.py` col generatore `pcb/tools/pcbgen.py` (schema, PCB 4 strati, Freerouting, ERC/DRC) e si rigenera, non si ritocca a mano. PCB a PASSA (2026-11-05): FX-SEND, MIC (5 giri su 5, todo 248; con U11 del todo 288 1 tentativo su 5, 2026-11-11), MONO, master (segnale + uscita L e R, todo 204/206), PSU-IN, canale (scheda sola a trapezio da 287 mm, dec. 173, PASSA il 2026-11-11 con `pcbgen.DesignRiprova`: Freerouting ripetuto fino a 4 volte) e FX-RET (segnale + reroute, confermato dalla dec. 173). Schede comandi a PASSA: FX-SEND, MIC, MONO, master (celle in `pcb/tools/comandi.py`, 2026-11-11). Da generare: 5-way, filtro, CUE, metering, backplane, box. Esiti in `pcb/<modulo>/NOTE.md`.

Generare una scheda (Python di KiCad, ~4 min; con `--solo-schema` solo schema, ERC e distinta, esito «SCHEMA PASSA», pochi secondi):

```bash
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 pcb/fx-send/fx-send.py
```

Regole delle PCB (nate il 2026-10-27):

- La generazione finisce con PASSA o NON PASSA (codice 1): un NON PASSA non si committa. Le righe PEGGIO confrontano col giro prima. Controllo audio: `pcb/tools/audiocheck.py`, regole in `d.audio_rules`. Pinout del C96 solo da `pcb/tools/backplane.py`. Stato e piano: `pcb/NOTE-generatore.md`.
- La forma del telaio non limita la funzione (dec. 144): se un circuito non sta, cambia la scheda o il telaio, non il circuito. Schede alte 220 mm, SMD sui due lati con `d.side = "B"`, più schede affiancate sotto un pannello (dec. 142). Una 100 × 220 porta ~160 impronte su un lato, ~280 coi due. Si stima dal conteggio vero (trimmer, 100n, regolatori, ponticelli), non dai circuiti del design doc.
- Trapezio della dec. 158: `board=(L, H_dietro, H_davanti)`, x = 0 dietro, `d.ytop(x)` per i pezzi vicino al pannello. Misure da `pcb/PIANO-SCHEDE-F.md` (tetto 70 %, dec. 156). A Freerouting va il rettangolo col taglio a gradini: col contorno in diagonale non finisce in un'ora (canale, 2026-11-09).
- Schema leggibile (in inglese, per lettori e costruttori): `pcb/tools/leggibile.py` coi file di tutte le schede dà `pcb/<scheda>/leggibile/` e il documento unico `pcb/schematics-readable.pdf`. Stesso netlist della PCB, confronto nei due sensi. Si rilancia a mano dopo ogni modifica di una scheda; traduzioni in `pcb/tools/leggibile_en.py` (una voce mancante ferma il giro).
- Le reti che toccano pin TSSOP (passo 0,65) vogliono piste ≤ 0,3 mm: con 0,6 Freerouting non le collega.
- Freerouting non collega due pin vicini dello stesso componente sulla stessa rete (pad doppi, pin doppi del C96, cursore e capo dei trimmer): pin alternati o `link_pairs` (pcbgen.py). Freerouting non è deterministico: un PASSA singolo non è una prova; il MIC fa fino a 4 tentativi.
- Grappolo attorno all'op-amp: `d.cluster_gap` 0,5 mm. Con 0,2 mm Freerouting lascia reti aperte (FX-SEND: NON PASSA).
- Il C96 è lungo 95 mm (impronta KiCad): il lato della scheda col connettore è lungo almeno 100 mm. Sotto i moduli bassi e larghi (master, 5-way, filtro, CUE) le schede vanno da sinistra a destra. Due pot da 9 mm in colonna sfalsata vogliono 14 mm di passo anche col cappuccio da 6 mm (DRC delle schede comandi).
- macOS non distingue maiuscole e minuscole nei nomi: `PIANO-SCHEDE.md` sovrascrive `PIANO-schede.md`. Prima di scrivere un file nuovo, `ls` senza badare alle maiuscole.
- I datasheet di analog.com non si scaricano da qui (timeout, errore HTTP/2). Copia funzionante: la pagina radiolocman del pezzo → link «Download PDF» su rlocman.ru (così è arrivato l'ADG1434 Rev. E; il PDF è l'URL dentro `rs.php?u=`, con curl `-L`). Alps (tech.alpsalpine.com) e il catalogo Alpha (taiwanalpha.com.tw/downloads) si scaricano. Pinout sempre dal datasheet, mai a memoria.

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
python3 sim/raw_finestre.py <raw> 0.1 "V(a),I(R1)"  # min/max a finestre da un .raw binario (senza numpy)
python3 sim/lint_cir.py [file.cir ...]             # regole di simulazione come controllo; prima di simulare un netlist nuovo
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
- `SINE` vuole il valore di picco: 0 dBu = 1,095 Vp, non 0,775; +18 dBu = 8,70 Vp (6,16 V è l'efficace: come picco vale +15 dBu, errore trovato il 2026-10-22, todo 125).
- THD: leggere sempre Partial E Total (`fourier_tab.py` li stampa entrambi). Total molto sopra Partial non è distorsione armonica: guardare la forma d'onda.
- `.meas ac`: `FIND V(nodo)`, mai `FIND dB(V(nodo))`. Serve uno sweep (`.ac dec ...`), non `.ac list` con un punto solo.
- `.tran` con anelli di retroazione: `.nodeset` obbligatorio. Macro op-amp in due varianti: specchio lineare per `.ac`/`.noise`, `abs` per `.tran`.
- Sallen-Key high-pass: R_fb = R_gnd/2 per Q 0,707.
- La macro `OP1612` di `opamp-audio.inc` ha un polo solo: è sempre stabile. Per la stabilità (nodi a massa virtuale lunghi, carichi capacitivi) serve un secondo polo inline (`sim/fx/fx-ret-bus-ac-130.cir`). Corrente dell'OPA1612: 3,6 mA per canale, non 2.
- Alimentatori: simulare il trasformatore con EMF a vuoto e resistenza d'avvolgimento, mai ideale (corrente efficace d'avvolgimento ~1,9× la DC).
- SVF con OTA della RES a Iabc quasi zero: il `.op` non converge (9 minuti a vuoto). Usare `.tran ... uic` e misurare il segnale con `PP`, non `RMS`: col partitore l'offset dell'OTA sale di 1/k.
- Regolatori in anello (LDO del box, `sim/system/psu-box-*`): mai `uic`; accensione da zero, così il `.op` è banale. Con `uic`, con `limit()` brusco o con diodi a N 0,05, LTspice non termina.
- `perl -e 'alarm ...'` ferma lo script ma non `LTspice.exe` dentro wine: il processo resta al 300 % di CPU. Controllare con `ps aux | grep -i LTspice.exe` e chiuderlo per PID. Un processo rimasto appeso continua a scrivere il log dello stesso netlist e sporca il giro dopo (NASTRO B9, 2026-11-04).
- Op-amp ideale `limit(1e5*...)` senza polo in un ramo non lineare (NASTRO B9): il passo collassa. Macro con polo: A0 1e5, R 1e10, C 0,1592 pF (100 Hz, GBW 10 MHz). Con 159 pF la banda è 10 kHz e i numeri sopra 1 kHz sono falsi.
- Modello Python dei saturatori: THD a 12 kHz solo a 192 kHz (a 96 kHz le armoniche si ripiegano: 107 % falso). Script con `multiprocessing` sempre con `if __name__ == "__main__"`.
- `.step param x list ...`: LTspice esegue i valori in ordine crescente, non in quello scritto. Leggere le misure con quell'ordine (MONO del master, todo 200).
- Un `.param` scritto due volte in un netlist con `.step`: `.four` non stampa niente e il log non dà errore.
- Non fermare LTspice con `pkill -f <nome netlist>`: uccide anche lo script. `drive2-chain` a 150 Hz non termina (causa ignota): usare 50 Hz o 1 kHz.
- Nomi delle istanze senza maiuscole: `Vs1` e `VS1` sono la stessa («Instance already defined»). Un `PWL file=` con due punti allo stesso tempo ferma il giro (misto/sim, 2026-11-09).
- Passo che collassa a t ~ns subito dopo il `.op` (migliaia di «tolerance relaxed»): `.options cshunt=1e-15`. 1 fF non sposta il polo della macro; `method=gear` e la macro senza anti-windup non bastano (NASTRO B9, todo 256).
- Logica nei netlist: un flip-flop a fronte va modellato master-slave; un latch trasparente nasconde i blocchi. Click di una commutazione: leggere l'attenuazione del VCA all'istante dell'ADG, non il massimo della sonda su una finestra lunga (levetta del canale, todo 289).
- Superdiodo (rivelatore di picco): la macro `OPDET` di `sim/meter/` ferma solo l'uscita, lo stato del polo corre a ~-1e4 V e sotto ~+3 dBu l'hold non si carica. Usare `OPDETC`/`OPDETN` di `sim/five-way/led-livello.inc` (stato fermato coi diodi). I numeri del meter restano validi: misurati a fondo scala (LED 5-way, 2026-11-11).

## Stato corrente (2026-11-10, decisioni 1-176)

Il design teorico (carta + simulazione) è completo per tutti i moduli. Il prototipo musicale in Max for Live (dec. 78) precede il millefori: P0 (`MC-CHANNEL`), P1 (`MC-FILTRO`, canale R corretto il 2026-10-15) e P2 (`MC-5WAY`: CROSSOVER A-E con E = impianto di Filippo 80/170/1,2k + 6k, GROWL VER DEC.99/LIBERO, NASTRO VER OGGI/COMPLETO/EXCITER/CLASSE A/LIBERO) costruiti, verificati e in ascolto da Filippo; P3 e P4 costruiti e verificati, da caricare in Live (P4 = `MC-MIC`: GAIN, EQ2, FX1-4 verso i bus di P3, MUTE, LED; pedali = effetti di Live: `MC-SEND` per canale, `MC-BUS` → effetto → `MC-RET` su 4 tracce FX, `MC-MASTER`; bus con `send~`/`receive~` che si sommano) (`proto-max/RISULTATI-P*.md`). Il blocco dei salti (todo 76) è superato: Prova 0 passata il 2026-10-31. Primo giro del libretto (`proto-max/tutorial-live.html`) fatto: decisioni 146-155 (isolator con curva PIONEER e incroci C; filtro OTA Butterworth, RES e DRIVE nuovi; 5-way E e GROWL LIBERO; EQ in serie scartato). Filtro sui bus dopo il fader nel prototipo: `MC-FILTRO-HPF` e `MC-FILTRO-LPF` sulle tracce BUS del gruppo, levetta = menu Audio To (todo 216, montaggio.md). `prova_semplice.py` controlla anche che ogni .genexpr su disco sia quello del generatore di oggi. Aperti: NASTRO (todo 213, versione COMPL. MEDI nuova), bus FX da rifare con l'instradamento di Live (todo 209: `send~`/`receive~` fra dispositivi M4L in Live sono muti). Generatori e prove in `proto-max/coefficienti/`: i `.genexpr/.maxpat/.amxd` non si toccano a mano. Gli acquisti sono sospesi fino al prototipo.

| Modulo | Versione corrente | Documento | Simulazioni |
|---|---|---|---|
| Canale CDJ/line | v0.4; EQ = ISOLATOR a 4 bande v0.4-beta (dec. 105: bande in parallelo; niente contatto di fondo corsa, dec. 127; incroci C 150 LR2 / 350 / 3150 Hz e curva PIONEER, dec. 152 e 146: hardware da riallineare, todo 211). Integrato nel canale: somma non invertente, polarità diritta (eq-isolator §9). GAIN a pot doppio selezionato, niente VCA, metà sinistra = trim (dec. 162, `sim/gain-pot/`). Levetta HPF/OFF/LPF col dip del VCA del fader (dec. 163) | `docs/fase1/cdj-line-channel.md`, `eq-isolator-v0.4.md` | `sim/cdj/`, `sim/eq-iso/` |
| Phono MM | v0.1 + REV 2026-09-30 (RIAA passiva 42 dB, dec. 79); subsonica fissa 18 Hz (dec. 138) | `docs/fase1/phono-stage.md` | `sim/cdj/phono-*` |
| FX-RET ×4 + FX-SEND ×4 | v0.3-WIP (matrice 16× VCA con self-feedback, dec. 91; un modulo per bus, dec. 130; GAIN del ritorno a pot doppio, dec. 162) | `docs/fase1/fx-module.md`, `fx-send-module.md` | `sim/fx/` |
| Master out | v0.3 DEFINITIVA (bootstrap rail OPA1612, dec. 83/86) | `docs/fase1/master-out.md` | `sim/master-out/compB-*` |
| Filtro | v0.2; **dopo il fader, sulla somma dei canali assegnati: 4 core sui bus HPF e LPF (dec. 159, §2bis)**; un percorso per canale (dec. 101); law Xone:96 (dec. 102), HPF da 20 Hz (dec. 137); overdrive v0.2 §5ter (dec. 99); core OTA (a′) con partitore 1/30 §5quater (dec. 109: il core nudo non funziona col chip reale; B1 aperta); numeri col chip reale accettati (dec. 110: oscillazione ~+5 dBu, calo di nota = carattere); core PULITO (c-B) a 4 poli progettato (RISULTATI-cb-4p): limitatore 2+2 / 3+3 / nell'OTA della RES (si spegne a RES zero), selettore LIMITATORE nel prototipo; RES della dec. 153 in hardware (shaper a manopola rovescia + raddrizzatore, fischio da 93,4 %) e DRIVE a pot doppio lineare sul segnale, senza VCA (§5, §5ter, todo 212) | `docs/fase2/filter-module.md` | `sim/filtro/` |
| 5-way | v0.3; **incroci H 60/250/1,2k/8k, GROWL BANDE (metà corsa 30 %) e NASTRO BANDE B9 scelti all'ascolto (dec. 175); banca ancora agli incroci E, todo 290**; celle v0.2.1; kill a switch §8.10 (dec. 88), tagliato allo zero della via §8.11 (dec. 164); drive v0.4 GROWL + NASTRO §5bis (dec. 99), ora GROWL e NASTRO a bande §5bis REV 2026-11-03 (dec. 165-166, PROVVISORI: modello Python, non ancora LTspice né ascolto); WIDTH continuo Q3…Q0,3 §4.3 (dec. 117) | `docs/fase2/five-way-module.md` | `sim/five-way/` |
| Mic e Mono | v0.1, due moduli separati, max 4 (dec. 97); MIC: MUTE (dec. 111) e limiter fisso nel VCA del MUTE (dec. 145, REV 2026-10-31) | `docs/fase4/mic-mono-moduli.md` | `sim/mic/` |
| Sistema | PSU ~420 VA con riserva (dec. 131: W1 7,0 A, W2 1,5 A, ramo audio 2,12-2,70 A ricontato dal basso; prima dec. 93/98/106/115; alimentatore ESTERNO con pre-regolatori, dec. 113, progettato in `sistema-psu-esterno.md`: LDO discreti ±22,0/±19 V, AC_OK, PSU-IN; ~83-97 W nel mixer, due ventole a termostato, dec. 112), grounding, backplane, metering (dec. 81/90), CUE (dec. 96), shaper, inventario comandi | `docs/fase3/` | `sim/system/` (box: `psu-box-*`, senza `uic`), `sim/meter/`, `sim/shaper/` |

Hardware dei comandi (dec. 118-129 e 169): cinque taglie di manopola (dec. 169), colonne sfalsate come sul Xone:DB4 in tutte le strisce, SEND e reroute a due a due; fader mono che comandano 2 VCA (dec. 126), 60 mm sui canali e 45 sui ritorni (dec. 169), kill a levetta ON-OFF-(ON), EQ di canale senza contatto di fondo corsa (dec. 127), curve dei pot provvisorie fino all'ascolto (dec. 129). Tabella: `docs/fase3/sistema-comandi.md`; render con colori standard (un colore per tipo di oggetto, per Illustrator): `docs/pannelli/`.

Disposizione dei pannelli (dec. 170-172, 2026-11-09): proposta F, 13U. MASTER e 5-WAY larghi 19" in fondo; colonna FILTRO → strisce CDJ da 50 mm con la sezione FX SEND (dec. 171, schede separate) → CUE con le cuffie davanti; a destra MIC/MONO, poi ritorni. Connettori dietro. Moduli ridisegnati da Filippo in Illustrator (dec. 176, `docs/pannelli/moduli-filippo-2026-11-10.pdf`): in `proposta_f.py` le posizioni sono fisse, lette dal PDF e messe in passo; LED di livello su ognuna delle 5 vie. Render e `coordinate.json` nascono da `docs/pannelli/proposta_f.py` via `genera_pannelli.py`; piano schede in `pcb/PIANO-SCHEDE-F.md` (`piano_schede.py --f`). Dopo un cambio di `coordinate.json` si rigenerano le schede comandi (FX-SEND, MIC, MONO).

Review contro il benchmark (dec. 111): ibrido DJ / sound system / live, nessun fork, moduli opzionali predisposti (uscite per via, EQ grafico, sirena; crossfader tolto, dec. 161), tasto MONO master, MUTE mic, ambiente da sound system all'aperto (`docs/07`, `docs/08`).

Documenti trasversali: `docs/fase1/gain-staging-sheet.md` (livelli e domini, referenza unica), `docs/06-ritaratura-rumore-71A.md` (budget di rumore e target ratificati), `docs/proto-max/piano.md` (prototipo Max).

Numeri di sistema: rumore −82,9 dBu A-wtd a filtri OFF col fader a VCA e il GAIN a pot doppio (docs/06 §14, dec. 162: canale −94,5, ritorno −96,1, 5-way −85,9; prima −81,9 col GAIN a VCA) (target ≤ −78, dec. 89; condizioni d'uso accettate con overdrive aperti, dec. 100; con FX in uso il sistema resta a −81,8, la deroga della dec. 95 non serve più, todo 184; filtri sui bus a overdrive chiuso −78,0 con HPF e LPF in uso, docs/06 §16, todo 215); master +25,4…+25,6 dBu (requisito ≥ +24). VCA: THAT 218x fuori produzione, rotta clone CoolAudio V2181L, ~54 chip (reroute FX 32 + 16 dei fader, dec. 126; crossfader tolto, dec. 161; GAIN di canali e ritorni a pot doppio, dec. 162; DRIVE del filtro a pot doppio, todo 212), trim in `docs/fase3/sistema-vca-trim.md`.

Trappole di lettura:

- **Superati, non usare come base**: `sim/cdj-eq/` e `sim/eq_analysis.py` (EQ a contribuzione bipolare), `sim/eq-serie/` e `eq-serie-v0.3.md` (EQ in serie, archiviato dalla dec. 105; le dec. 103 e 104 sono revocate), `sim/master-out/compG-*` (VAS discreto), `sim/five-way/drive-*` (drive v0.3, archiviato), filter-module §5bis (overdrive v0.1), griglia drive dec. 87.
- **ADG1434 e famiglia**: il pin IN è logico (VIH 2,0 / VIL 0,8 V, tTRANS 140 ns). Un RC sul pin IN non dà una rampa: l'interruttore scatta secco. Per togliere il click: taglio al passaggio per lo zero (dec. 164) o dip di un VCA (dec. 163). Il segnale allo switch sta fra le sue alimentazioni (±15 V = +22,5 dBu): oltre, switch sul nodo a massa virtuale.
- **Pin EC− del VCA: ±1 V massimo assoluto** (THAT 2181 Rev 02). Ogni CV arriva al pin da un partitore alto (18,2k/1k, `celle_vca.py`): un op-amp al rail non deve portare oltre 0,8 V. Una CV sommata direttamente sul pin (il dip del canale, 1,38 V) lo sfora in uso normale. Corretti canale, ritorni, master e MONO/MUTE (`sim/system/RISULTATI-ec-pin.md` §2 e §4, todo 281 e 288): un circuito nuovo che tocca il pin si controlla al rail.
- **VCA THAT 2181 / V2181**: VCA + I/V è NON invertente (datasheet Rev 03 p. 7). Nei netlist il VCA a tensione (`that2181.inc`) + R, o una `F` che spinge corrente nel nodo dell'I/V, hanno il segno opposto al chip. Nel MONO del master scambiava L e R; nell'overdrive del filtro cambia il suono (todo 227).
- **Kill del 5-way e casse**: nell'impianto (VENU360 LR4 80/170) il kill KICK abbassa la cassa di ~6 dB, non la spegne. Filtri più ripidi nel 5-way non aiutano (LR8: −7,4). Nemmeno una via più larga: con la banca risommata 40-400 Hz lascia −23 dB sulla cassa (`sim/five-way/kill_casse.py`). Solo un'uscita per via spegne la cassa (`docs/09` §4, `docs/07` §6).
- **Polarità**: ogni ricevitore a massa virtuale (DJ bus, bus HPF/LPF, bus FX, MASTER SUM, CUE sum) inverte. Un percorso nuovo si conta da capo a capo in `docs/fase3/sistema-polarita.md`, non solo dentro il modulo (todo 227: filtro, MIC/MONO, anello del reroute e CUE erano rovesciati).
- **Servo DC**: filtro (overdrive §5ter), 5-way (§5bis.7) ed EQ isolator (§8) usano la stessa cella: integratore invertente che entra dal piedino + dello stadio attraverso un partitore. Iniettare nel nodo di somma dà retroazione positiva.
- **Diagrammi**: gli SVG di 5-way, filtro e mic/mono sono vecchi. Si rigenerano solo su richiesta di Filippo.
- **Codice gen~ (prototipo)**: la traduzione Python delle prove accetta cose che gen~ non regge. Regole pagate in P1/P2: funzioni con un solo valore di ritorno; nessun nome esterno uguale a un parametro, locale, `Param` o `History` di funzione; `d0`/`d1` sono del downsampling; la prova suona sempre i due canali. Lo stato delle funzioni va in `Data` (peek/poke). Una legge di manopola cambiata in `filtro.py` va cambiata anche in `theta_freq` di `prova_filtro.py`: altrimenti la prova dà punti FUORI falsi. A 4× i sotto-campioni passano dagli STESSI stati dei filtri, in ordine (stati separati = incroci divisi per 4). CPU: i dispositivi di una traccia girano su un solo core; un blocco con peso zero non si calcola (`if`, stati a zero). Un generatore scrive il dispositivo O la sua versione -S (`--semplice`): una legge cambiata vuole due lanci, e `prova_semplice.py` non se ne accorge (MC-FILTRO-S rimasto all'HPF vecchio fino al 2026-10-29, todo 207).
- **Prototipo in Live (2026-10-31)**: NON usare `send~`/`receive~` fra dispositivi M4L (Live non li supporta: bus muti). NON passare polinomi in s di ordine alto alla bilineare in gen~ (EQ SERIE v1: coefficienti ~1e8, traccia di Live avvelenata): solo celle del 1o e 2o ordine con prewarp.
- Il modulo mic/mono è un precedente: una prima stesura con comandi decisi da Claude è stata bocciata. Pannello, comandi e divisione in moduli li decide Filippo.

## Prossimo passo

La coda vive in tre posti, non qui:

- **Decisioni di Filippo e ingegneria residua**: liste A, B e C in testa a `docs/02-questioni-aperte.md`.
- **Todo**: `arturo todo --progetto .`
- **Ultima sessione**: handoff in `~/.claude/data/handoffs/maelcum-mixer/`.

## Dove sta cosa

```
SPECIFICA.md                  specifica consolidata
docs/01-decisioni-bloccate.md cosa è deciso (141 voci; 103 e 104 revocate)
docs/02-questioni-aperte.md   cosa manca: liste A/B/C in testa, storico delle voci sotto
docs/03 … 08                  revisione critica, architettura filtro, benchmark, rumore, review
docs/09-budget.md             costi per modulo e totale (generato da docs/budget/genera_budget.py)
cheap/                        progetto parallelo CHEAP (versione economica): non tocca docs/ e sim/
misto/                        progetto parallelo MISTO (chip che muove solo le CV, dec. 174): non tocca docs/, sim/, pcb/
docs/storico-sessioni.md      cronaca delle sessioni fino al 2026-10-13
docs/fase1 … fase4/           design doc per modulo (tabella sopra)
docs/diagrammi/               SVG generati da genera_diagrammi.py
docs/export-chatgpt/, docs/00 materiale d'origine, chiuso (dec. 58)
sim/lib/                      modelli condivisi: op-amp, THAT 2181, LM13700
sim/<modulo>/                 netlist .cir + RISULTATI-*.md
sim/run_ltspice.sh            wrapper per LTspice in batch
```
