# SPECIFICA — MAELCUM MIXER (mixer dub modulare analogico, esemplare unico)

> **v0.1 (2026-09-18, rev. 2026-09-28/01-10: decisioni 76-93; REV 2026-10-13: decisioni 97-106 recepite nei §4-6 come note in testa ai punti toccati + esiti simulazioni e sessione decisioni; REV 2026-10-14: decisioni 107-114; REV 2026-10-21: decisioni 115-118)** — Compilata da: decisioni 1-118 (`docs/01-decisioni-bloccate.md`; 103 e 104 revocate),
> status doc ChatGPT rev2 (`docs/export-chatgpt/`, corpus chiuso — decisione 58),
> gain-staging sheet (`docs/fase1/gain-staging-sheet.md`), revisione critica (`docs/03`).
> Livello: REQUISITI. Il dettaglio circuitale vive nei design doc di `docs/fase1/` e `docs/fase2/`.
> Stati: [BLOCCATO] deciso · [PROVVISORIO] target di lavoro · [APERTO] da decidere ·
> [SUPERATO] versione vecchia, solo per storia.
> Metodo per la fase circuitale: requisito → funzione di trasferimento → topologia →
> componenti → simulazione → vincoli PCB → prototipo → misura → revisione.

## 1. Vincoli globali di progetto

- [BLOCCATO] Percorso audio 100% analogico. Nessun ADC/DAC/DSP interno. Il DSP esterno resta responsabile di crossover di sistema, protezione altoparlanti, EQ di sistema, delay, gestione finali. [DEC. 111 (c, f), 2026-10-14: uscita full-range stereo confermata. REQUISITO D'IMPIANTO: il DSP esterno deve proteggere i sub dai contenuti infrasonici del mixer (auto-oscillazione del filtro fino a ~15-30 Hz, giri di feedback FX, GROWL): passa-alto e limiter per via.]
- [DEC. 111 (e), 2026-10-14] Ambiente: sound system all'aperto. Funzionamento fino a 40 °C ambiente; schede tropicalizzate (vernice protettiva); pot sigillati; connettori robusti; telaio rigido; trasporto in flight case; pannello protetto da polvere e liquidi. [Conseguenza termica 2026-10-14, `docs/fase3/sistema-psu.md` REV dec. 111: ~114 W dentro il telaio (~131 W coi moduli opzionali); senza ventola serve ventilazione naturale a camino (prese in basso e sul retro, nessuna feritoia sul pannello superiore), regolatori dei moduli caldi sul telaio; obiettivo interno ≤ 55 °C a 40 °C fuori. Trasformatore ~250 VA, W1 2×21 V 3,5 A.] [DEC. 112, 2026-10-14: due ventole a termostato (spente sotto ~35 °C interni, controllo lineare, filtri sulle prese; il mixer lavora a ventole ferme fino a ~30 °C ambiente): interno ~45 °C a 40 °C fuori. W4 9 V 2,5 A.] [DEC. 113, 2026-10-14: ALIMENTATORE ESTERNO — box con toroidale, raddrizzatori, bulk, pre-regolatori ±22,5 V (audio) e ±19 V (LN), [M] raw, +5 V; cavo ≤ 2 m con connettore circolare IP65; regolazione finale locale, stella e fusibili di ramo restano nel mixer (`docs/fase3/sistema-psu.md`). Calore nel mixer ~95-100 W, indipendente dalla rete.] [Todo 51, 2026-10-14, `docs/fase3/sistema-psu-esterno.md`: pre-regolatore audio ±22,0 V (non 22,5) con LDO discreto a MOSFET, bulk W1 15 mF, linea AC_OK per il mute allo spegnimento, conduttore PE nel cavo (20 contatti, classe 24 poli), fusibili di gruppo nel PSU-IN + PTC per modulo; calore box ~48/63 W (nominale / rete +10 %), mixer ~83 W base, ~97 W coi moduli opzionali.]
- [DEC. 111 (b), 2026-10-14] Moduli opzionali PREDISPOSTI (non costruiti): uscite per via (crossover dopo la somma del master), crossfader (loop post-fader dei 4 canali), EQ grafico (inserzione sul master e/o dopo il 5-way), sirena (slot MONO). Backplane e alimentazione li prevedono senza grosse modifiche.
- [BLOCCATO] Stereo L/R ovunque; no pan; nessun controllo L/R separato; controlli linked; mono-compatibile.
- [BLOCCATO] Livelli: nominale 0 dBu (0,775 Vrms); programma caldo ~+10 dBu; estremo interno ~+18 dBu; capability d'uscita pulita ≥ +24 dBu (solo stadio finale master). Referenza autorevole: gain-staging sheet.
- [BLOCCATO, REV decisione 93 2026-10-01] Domini di alimentazione: **raw ±27 V audio · raw ±22 V LN/OTA · raw ±26 V [M] (SOLO stadio HV uscita master)** distribuiti sul backplane + **+5 V control** (regolato nel modulo PSU). Generazione LOCALE per modulo: ±18 V audio di percorso (LM317/337 dal raw ±27) · ±15 V ultra-low-noise (phono, mic, CV, metering, CUE: pre-reg ±16,5 V + LT3045/LT3094 dal raw ±22, dec. 54) · ±15 V switch/kill/assign (78L15/79L15 dal raw ±22, dec. 90c). Nessun raw alimenta mai un op-amp; il raw [M] alimenta solo lo stadio discreto HV master. (Il dominio «±24 V main unico» del consolidamento 2026-09-18 è SUPERATO: attuazione della dec. 90(c) — secondari dedicati audio/OTA/switch-logica.)
- [BLOCCATO] Banda complessiva: −3 dB a ≤8 Hz … 35 kHz con filtri OFF; requisito infrasub: 10 Hz entro ±1 dB; nessun accoppiamento AC con corner >5 Hz nel percorso principale (DC servo).
- [BLOCCATO] Nessun compressore/limiter/AGC. Protezione elettrica ≠ dinamica audio: protezioni DC/corto/ESD/RF e mute power-on/off obbligatorie.
- [BLOCCATO] Nonlinearità intenzionali solo in: overdrive del filtro, drive del 5-way. Setting estremi permessi, elettricamente non distruttivi, saturazione morbida e recuperabile.
- [BLOCCATO] Buffering low-Z tra stadi/moduli; buffer dedicato per ogni uscita (mai splittati).
- [BLOCCATO] Costruzione modulare su backplane; nessun accesso a nodi interni tra moduli; no hot-swap; test point su ogni modulo.
- [BLOCCATO] CV 0-5 V = convenzione d'interfaccia sul backplane, non formato nativo di ogni circuito.
- [BLOCCATO] Esemplare unico: si ottimizza per qualità sonora e manutenibilità, non per costi.

## 2. Diagramma del segnale — autorevole

```
 SORGENTI            MODULI CANALE (×4, stereo)                 MODULO FILTRO            MODULO 5-WAY
═══════════        ═══════════════════════════════            ═══════════════          ═══════════════

 CDJ/LINE ──► PROTEZ → BUFFER → GAIN → EQ 4 BANDE ──┬── (1) CUE ──► CUE BUS ═══╗
 (phono Rev B                                       │                           ║
  futura: front-end                                 ├── (2) FX SEND ──► ═══╗    ║
  dedicato + selettore)                             │    (EQ2+assign+level)║    ║
                                                    └── (3) FILTER SEND ══►║────╫──► CORE PER CANALE
                                                            ▲            ║    ║    (2 sezioni shared:
                                                            ║ ritorno    ║    ║     HPF e LPF full-range)
                                                     FILTER RETURN ◄═════╝    ║    + res + overdrive
                                                            │                ║
                                                     METER → FADER → OUT DRV ║
                                                            │                ║
                                                            ▼                ║
                                                        DJ BUS L/R ══════════╬══► KILL bank 5 vie
                                                                             ║    + EQ creativo + DRIVE
 MIC ──► MODULO MIC (30-60 dB, no phantom, EQ2) ═════════════════════════════╬══► + meter
                                                                             ║         │
 GENERIC MONO ──► MODULO SORGENTE (hi-Z, gain, EQ2, mono→stereo) ════════════╬══►      │
                                                                             ║         │
                          MODULO FX ◄═════════════════════════════════════════╝         │
                          │ BUS 1-4 → pad → PEDALI OUT                                  │
                          │ PEDALI IN (≥1MΩ) → gain → EQ2 → meter → FADER → MASTER SUM  │
                          │ MATRICE FEEDBACK: 4 reroute/ritorno (3 cross + 1 self, dec. 91), VCA │
                          ▼                                                             ▼
                          MODULO MASTER: SUMMING → LEVEL(VCA −∞..0..+6) → METER         │
                            → HV±26[M] → XLR MASTER · BOOTH (pre-level) → XLR           │
                            · REC (0 dBu fissi) ────────────────────────────────────────┘
 CUE BUS ══► MODULO CUE: somma cue → mix CUE/MASTER → amp cuffia → 2 uscite
 BACKPLANE: bus audio + bus controllo (CV/logiche) + potenza (raw ±27/±22/±26[M], +5) + ground separati
```

- [BLOCCATO] FX returns, mic e generic mono NON passano dal 5-way (solo il DJ BUS sì).
- [BLOCCATO] Master chain: SUM → LEVEL → METER (post-level) → OUT.

## 3. Moduli e backplane

Moduli [BLOCCATO dai doc §33, consolidamento [PROVVISORIO]]: DJ CH1-4 · FILTRO · 5-WAY · FX (bus/pedali/ritorni/matrice; i doc elencano 4 moduli FX RETURN separati — accorpamento in un modulo FX da ratificare in fase di layout) · MIC · GENERIC MONO (1..n) · MASTER · CUE/CUFFIE · PSU · utility/future.

- [BLOCCATO] Bus audio: DJ L/R, FX1-4 L/R, 5-WAY L/R, MASTER L/R, CUE L/R, filter send/return per canale.
- [BLOCCATO, REV decisione 93 2026-10-01] Bus potenza sul backplane: **raw ±27 V audio, raw ±22 V LN/OTA, raw ±26 V [M] HV (popolato solo dal master), +5 V control** (regolato nella PSU), analogue 0 V, control ground, chassis/shield. Tabella avvolgimenti/correnti: `docs/fase3/sistema-psu.md` v0.2 §2; pinout riga a: `docs/fase3/sistema-backplane.md` v0.2 §3. [BLOCCATO] I rail ±18 V audio e ±15 V low-noise si generano LOCALMENTE in ogni modulo (non distribuiti sul backplane): ogni modulo isola il proprio rumore — ciascuno dal SUO raw dedicato (±18: LM317/337 da ±27; ±15,0 V: pre-reg ±16,5 + LT3045/LT3094 da ±22).
- [BLOCCATO] Separazione fisica audio/controllo/potenza/ground sul backplane; schermature; nessun bus floating; ogni modulo ha uno stato inattivo definito; connettori robusti card-edge/board-to-board con keying.
- [BLOCCATO decisione 94(a) 2026-10-01] Standard elettrico I/O tra moduli: single-ended 0 dBu, bilanciato solo verso l'esterno (XLR master/mic). MASTER SUM: 7 contributori stereo (5-way, 4 ritorni FX, mic, generic), summing nel modulo master (§10).
- [PROVVISORIO → design S3 v0.2] Pinout e famiglia connettori (DIN 41612 tipo C — q29 meccanica), impedenze di bus, comportamento a modulo rimosso: disegnati in `docs/fase3/sistema-backplane.md` (dec. 93/94). Resto della questione 22: reperibilità connettori.

## 4. Canale DJ (modulo ×4, stereo identici)

Catena [BLOCCATO]: RCA stereo → protezione → front-end (LINE; PHONO MM v0.1 con front-end dedicato + selettore, decisione 79, `docs/fase1/phono-stage.md`) → GAIN → EQ 4 bande → nodo split post-EQ: (1) CUE, (2) FX SEND, (3) dry → FILTER SEND/RETURN → METER → FADER → out driver ≤50 Ω → DJ BUS.

- GAIN [BLOCCATO]: −∞ → 0 (detent) → +10 dB; stereo linked; tracking ≤0,5 dB.
- [SUPERATO dalla dec. 105: l'EQ dei canali è l'isolator, vedi più sotto; questa riga e la seguente descrivono l'EQ in serie archiviato. Restano validi il boost +6 dB e il tracking stereo (dec. 107). I centri 70/250/1k/5k restano come opzione d'ascolto B5 (docs/02).] EQ 4 bande [BLOCCATO nel comportamento]: LOW / LOW-MID / MID-HIGH / HIGH; ogni knob −∞ → 0 (flat, detent) → +6 dB; tracking stereo ≤0,25 dB; law: lenta al centro, rapida agli estremi. **[rev. decisione 77, 2026-09-24]** l'estremo "−∞" si intende come kill di banda a **−30 dB** (profondità misurata della cella serie): il silenzio assoluto del canale resta compito del fader — il kill è un gesto musicale, non un mute. Stato beta-3 (2026-09-27, `docs/fase1/eq-serie-v0.3.md` §9.7): griglia confermata con op-amp reali OPA1654/1612 (kill LOW −29,2 @20 Hz, gonna larga; notch MID −44,2 @1 kHz); offset detent RISOLTO (−0,0001 dB con coppia 0,1%, trim multi-giro non serve); rumore: il claim −110,7 dBu INVALIDATO dal quirk INTEG LTspice → reale −89,2 dBu (den 190 nV/√Hz piatta, 20-20k) — target canale −92 superato dalla sola EQ → ritaratura sistema, voce 71; kill HIGH = bump +2 dB al corner e −9…−14 dB a 20-35 kHz → questione 68 aperta (accettare il gesto "scurente" o cella crossfade-LP2). [DEC. 107, 2026-10-14: tracking stereo con pot doppi lineari selezionati, niente VCA per banda]
- [SUPERATO dalla dec. 105, vedi la riga sopra] EQ frequenze [PROVVISORIO — review con Filippo aperta]: 70 Hz (Q~0,7) / 250 Hz (Q~0,8) / 1 kHz (Q~0,9) / 5 kHz (Q~0,7). Topologia: [SUPERATO 2026-09-24] celle a contribuzione (reference + contributo di banda), kill = contribuzione zero — bocciata dalla simulazione LTspice per le bande LOW/HIGH (fase dei filtri: `sim/cdj-eq/RISULTATI-eq.md`, questione 62). Topologia scelta: **EQ in serie per banda, famiglia Baxandall** (decisione 76) — design in CDJ v0.3 (`docs/fase1/eq-serie-v0.3.md`); comportamento locked immutato salvo l'estremo di cut: −30 dB per banda (decisione 77). Stesso finding si applica alle EQ2 di FX send/return (questione 65).
- CUE [BLOCCATO]: post-EQ, pre-filter, pre-fader; switch per canale → CUE bus.
- FX SEND [BLOCCATO]: pre-fader, pre-filter; EQ 2 bande (LOW ~120 Hz, HIGH ~4,5 kHz, −∞→0→+6) con law dedicate (bassi: rapidi solo al taglio estremo; alti: taglio rapido in partenza poi graduale); level −∞→0 (niente gain positivo); assign a S1-S4 MULTIPLO e simultaneo con precision analogue switch (JFET scartati); soppressione transiente di commutazione [BLOCCATO: break-before-make + ramp 1 ms, famiglia unica per tutte le commutazioni CV — decisione 80]. **[REV decisione 91a, 2026-10-01: EQ2+level+assign vivono nel micro-modulo FX-SEND ×4 (`docs/fase1/fx-send-module.md`); al canale restano il send tap bufferizzato e i 4 bottoni (harness logico +5 V). Comportamenti locked INVARIATI.]**
- Filtro [BLOCCATO]: solo switch 3 posizioni HPF/OFF/LPF sul canale; l'audio va al modulo filtro (send/return); break-before-make + ramp 1 ms nel modulo filtro (famiglia unica, decisione 80).
- METER DJ [BLOCCATO]: post-filter/overdrive, pre-fader; peak con persistenza; calibrazione identica tra canali (procedura di calibrazione: questione 54); colori = §11.
- FADER [BLOCCATO]: slider DJ-style conduttivo-plastica, −∞→0, stereo linked ≤0,5 dB, seguito da buffer ≤50 Ω.
- PHONO MM (v0.1 FATTO 2026-09-28 — decisione 79, chiude q6; design e numeri: `docs/fase1/phono-stage.md`) [BLOCCATO nei requisiti]: MM-only (DJ + MM alta qualità, dec. 62); RCA + ground dedicato giradischi (stella analogue-0V, q. 21); load 47 kΩ || C selezionabile 100/200/300 pF [PROVVISORIO q7]; gain totale 42 dB @1 kHz (dec. 72); topologia dec. 79: stadio piatto OPA1612 ×21 + subsonica Sallen-Key 13 Hz Q 0,707 + RIAA PASSIVA (rete a equazioni chiuse) + stadio OPA1654 ×60,6, rail ±15 V LN; accuratezza ≤ ±0,05 dB su 100 Hz-20 kHz (REV 2026-09-30: residuo sub-100 Hz v0.1 attribuito al polo DC block 15,9 Hz e risolto con Rb2 100k→1M; sotto i 100 Hz agisce la sola subsonica SK 13 Hz come da progetto: −0,06/−0,24/−0,83 dB a 50/30/20 Hz; requisito «−1 dB max a 30-40 Hz» PASS; warp invariato; EIN RICALCOLATO 2026-09-30 con integrazione corretta — quirk LTspice INTEG, il claim v0.1 0,36 µV era ~13× ottimistico: EIN 1,79 µV 10-20k, out −79,8 dBu, 19 dB sotto il fruscio vinile); overload +18 dBu puliti (≈20 dB sopra 5 mV ✓ Rev A), clip +24,9 dBu; warp pulito fino a ~25 mV @10 Hz; MC = variante futura separata (q. 7).
- Dominio: ±18 V audio, ±15 V LN per phono. Livelli: gain-staging sheet §2.

## 5. Modulo filtro (B′) — requisiti

- [BLOCCATO] Architettura: un core dedicato per canale (4 stereo = 8 mono, stesso PCB), DUE sezioni di parametri condivise: HPF (freq, res, overdrive) e LPF (freq, res, overdrive) = 6 knob sul pannello del modulo. Ogni canale con switch HPF/OFF/LPF segue i knob della sua sezione. BPF escluso.
- [BLOCCATO] Range: entrambe le sezioni **10 Hz–35 kHz** (decisione 74); pendenza 24 dB/ottava (4 poli: 2 sezioni 2-poli SVF in cascata, controllo di frequenza matched); overlapping utilizzabile HPF/LPF.
- [DECISIONE 105, 2026-10-13 — REVOCA la 104 qui sotto] EQ 4 bande dei canali DJ = ISOLATOR: bande in parallelo, ogni manopola dal silenzio a 0 dB (centro) a +6 dB; quattro bande chiuse = canale muto. Design: `docs/fase1/eq-isolator-v0.4.md`. [DEC. 114, 2026-10-14: boost +6 dB confermato; curva da rifare con pot di serie; incroci A e B scartati, da ridefinire a orecchio.]
- [SUPERATO dalla dec. 105] [DECISIONE 104, 2026-10-13 — vale per il canale DJ §4] EQ 4 bande = in serie v0.3 beta-3 CONFERMATO (dec. 76/77, kill −30 dB per banda) + MUTO A FINE CORSA: con tutte e quattro le manopole a zero un interruttore spegne il canale. Circuito del muto da fare. (La dec. 103 «isolator» è stata revocata lo stesso giorno.)
- [DECISIONE 102, 2026-10-13 — punto di partenza, revisione dopo il prototipo M4L] Law FREQ e RES = Xone:96: FREQ 20 Hz–20 kHz esponenziale tra 5 % e 95 % di corsa, ultimi 5 % per lato fino a 10 Hz / 35 kHz; RES curva Xone sul primo 90 % (da sottile a un passo dall'oscillazione), auto-oscillazione nell'ultimo 10 %. Tabella: `filter-module.md` §4.
- [BLOCCATO] Legge dei knob: musicale nei ~90% centrali, accelerazione forte negli ultimi ~5% a entrambe le estremità; all'estremo di taglio = cancellazione totale (HPF in cima, LPF in fondo). Implementazione: shaper CV a tratti, punti di piega regolabili a banco.
- [BLOCCATO] Risonanza: 0-70% normale, 70-90% aggressiva, 90-100% auto-oscillazione che segue il cutoff; livello oscillazione ~+6…+10 dBu con soft limiting (non clamp a diodi crudi); carattere musicale, riferimento Sherman Filterbank. [D5 2026-10-14, dec. 109: col core (a′) l'oscillazione segue il cutoff ma sta a +4,9 dBu a fine corsa e cala di ~6 semitoni tra 90 % e 100 %; da riconfermare, voce A17] [DEC. 110, 2026-10-14: requisito del livello di oscillazione abbassato a ~+5 dBu; calo di nota a fine corsa accettato come carattere; picco di risonanza +7…+9 dB su −10 dBu e ~+1-2 dB su 0 dBu accettato (Xone-like); griglia overdrive = `d5-chain.cir`]
- [REV 2026-10-13 — DECISIONE 99] Overdrive: circuito e carattere diversi dal drive 5-way; rende più drammatici e violenti i transienti di filtro; meno aggressivo dello Sherman; estremi a fine corsa, curva che accelera nel tratto finale. Design v0.2 SIMULATO (`filter-module.md` §5ter: tosatore simmetrico in parallelo, 1 VCA per cella, tetto d'uscita ~+5,5 dBu a fine corsa (alzato di 3 dB [F]), law m = θ^2,5) [griglia DA CONFERMARE-F]; posizione invariata.
- [SUPERATO per referenza e law] Overdrive: dopo filtro/risonanza, prima del meter di canale; 0 = pulito ~unity; progressione clean → subtle → warm → gritty → aggressive → hard dub overload; referenza sonora = Sherman Filterbox, raschio acido che cresce con la risonanza (decisione 82); prototipi JFET (prima) e BJT asimmetrico (poi); recovery low-Z 20-50 Ω, clean +23 dBu (raffinamento del "+24 where practical": il ±18 V del modulo non dà +24 — decision sheet §2); nessun makeup compression.
- [PROVVISORIO/INGEGNERIA] Converter di frequenza: esponenziale + tempco, range gm ~3500:1; tolleranza accettabile ±5-10% (più lasca di un VCO); core in tracking tra canali ≤2% a pari CV con trim per core; CV bufferizzati, distribuzione a stella, smoothing.
- [DECISIONE 109, 2026-10-14 — core OTA; B1 resta aperta] Il core (a) nudo è scartato: col chip reale non funziona ai livelli di progetto. Opzione OTA corrente = **(a′)**, partitore 1/30 davanti agli OTA, C 1,1 nF, limitatore a perdita non lineare verso il summer; rumore core −87,4 dBu A-wtd a fc max, sistema con 4 filtri inseriti −79,0 (`filter-module.md` §5quater, `sim/filtro/RISULTATI-D5.md`). B1 = (a′) contro (c-B).
- [APERTO in parte — aggiornato 2026-09-28] Topologia SVF concreta: il LM13700 reale ha un tetto di stato strutturale (52 mV a f0) → il core OTA nudo a 0 dBu comprime morbido (~1% THD, collasso a +10 dBu): **questione 70** — scelta MUSICALE di Filippo tra (a) carattere OTA nudo (design v0.2 invariato, famiglia Sherman) e (c-B) integratori op-amp + VCA 218x (pulito, +16 chip), entrambe quantificate (`sim/filtro/RISULTATI-ota-real.md` + `sim/five-way/RISULTATI-cell-clean.md`); le CELLE parametriche 5-way hanno già adottato la variante pulita (c-A) JFET VCR (design v0.2.1, five-way §4.2). Fattibilità converter esponenziale 10 Hz–35 kHz DIMOSTRATA (`docs/fase2/filter-module.md` §6 — questione 51 aggiornata, 49 chiusa; con (c-B) la distribuzione diventa Vc a buffer, più semplice). Restano aperti: loop di risonanza/limiting (questione 11), curva esatta del drive (questioni 12/61), interpretazione mux CV e allineamento 4 poli (questioni 63/64).

## 6. Modulo 5-way (dub preamp) — requisiti

- [BLOCCATO] Posizione: DJ BUS → 5-WAY → MASTER SUM. Riferimento interno −6 dB (pad in / makeup out, decisione 73).
- [BLOCCATO] KILL: 5 sezioni = 5 vie dell'impianto; mappa [PROVVISORIO]: SUB ~10-90 Hz (esteso a 10 Hz per infrasub — decisione 65), KICK ~90-350, MID ~350-1,2k, HIGH ~1,2-3,5k, SUPER HI ~3,5-20k; 24 dB/ottava iniziali, overlap deliberato senza buchi; filter bank complementare (somma piatta senza kill); KILL prima dell'EQ creativo (il boost non ripristina materiale killato); kill switch per via (uno per altoparlanti fisici).
- [BLOCCATO] EQ creativo 5 bande: gain/position/width per banda (comandi gain = 5 pot rotativi, decisione 85); −∞/0/+15 (bande 1-3), +12 (banda 4), +9 (banda 5); range [PROVVISORIO]: 20-120 / 80-400 / 250-1,5k / 800-5k / 3-20 kHz; width: narrow ~Q3, medium ~Q1, broad ~Q0,5 [SUPERATO dec. 117: manopola continua Q3…Q0,3, five-way §4.3]; position sposta il centro senza stravolgere gain/Q.
- [REV 2026-10-13 — DECISIONE 99] Drive = due saturatori con due manopole: GROWL (valvola spinta forte, solo sub e bassi) e NASTRO (JFET tape); niente fuzz; livello autoregolato (non alzano il volume); nessun boost pulito; primo 5-10 % di corsa quasi inerte. Design v0.4 SIMULATO (`five-way-module.md` §5bis: saturatori in parallelo al pulito, pot diretti, nessun VCA; volume ±0,2 dB al nominale; NASTRO 5,5 % e GROWL 20 % a fine corsa) GROWL sotto 350 Hz [F] [griglia DA CONFERMARE-F]. Il testo che segue descrive la v0.3, ARCHIVIATA come alternativa.
- [SUPERATO, archiviato] Drive: dopo la somma EQ, prima del meter; full CCW = 0 dB (pulito), solo gain positivo CW; ~50% = punto ottimale (+7 dB senza distorsione), 50→80% = saturazione progressiva calda stile nastro, 80→100% = territorio fuzz (decisione 82); interagisce con gain di banda e overdrive filtro; JFET prima / BJT asimmetrico poi.
- [BLOCCATO] Meter: dopo il drive, prima del master sum.
- [PROPOSTA v0.2.1 2026-09-28 — celle EQ ridisegnate su JFET VCR (q. 70 chiusa lato celle); banca invariata; gate → SWITCH hard-cut (dec. 88)] Matematica del filter bank, topologie celle EQ, circuiti position/width, taper esatto del drive (questioni 8/9/10): design in `docs/fase2/five-way-module.md` — kill bank LR4 VALIDATA [gate VCA SUPERATO dec. 88: switch hard-cut π SPDT classe ADG1434 (serie+shunt GND), off-isolation MISURATA −95 dB @20 kHz / all-kill ≤ −85,5 dB = sotto il floor del modulo, polarità con 2 invertitori unity/lato su SUB/MID, flatness −0,004…−0,011 dB preservata, rail ±15 V dedicato, click = gradino segnale istantaneo (accettato dec. 88) — five-way §8.10]; **somma piatta ESATTA OTTENUTA in v0.2**: banca allineata in fase (spina HP condivisa + compensazione allpass A2, §3.1) validata −0,0002…−0,008 dB su 5 Hz–60 kHz (questione 8: matematica risolta; frequenze restano questione 67); EQ creativo = parametriche SVF: algebra VALIDATA v0.2 (§4.1/§8.3) e topologia RIDISEGNATA **v0.2.1** (§4.2/§8.8, questione 70: il LM13700 ha tetto di stato 52 mV → integratori op-amp + JFET VCR bootstrappato, core −12 dBu locale) — verificata: detent ±0,0001 dB, boost ±0,02 dB sui target +9/+15, notch −46…−47 dB (spec −30 ✓), law position ±0,03% su 2,6 ottave, THD 0,005%/0,125% worst, rumore modulo: il ~−101 v0.2.1 era viziato dal quirk INTEG LTspice (~21,5 dB ottimista); con 6 218x reali −77,3/−73,0 dBu → target −90 FALLITO → **DECISIONE 88 (2026-09-30): kill a SWITCH analogici hard-cut (10 VCA rimossi dai gate, dec. 80 revocata per il kill; fade perso = click accettato, standard di scena), drive mantiene 218x con I/V 10k (−104 dBV), fix servo OPA2134-class + banca op-amp reali; TARGET NUOVO ≤ −80 dBu A-wtd (out modulo, ingressi terminati, gain nom., drive θ0) — misurato −83,2, margine 3,2 dB** (five-way §8.9 + docs/05-benchmark); pot gain nel dominio del segnale (cablato sul terminale opposto: gesto invariato); law/taper = ascolto M4L; **DRIVE v0.3 VALIDATO 2026-09-29** (referenze dec. 82 → questione 10 chiusa per il design: 218x con law end-to-end misurata esatta 0/+7/+9,5/+12/+14/+16 dB → JFET CS «nastro» (ginocchio 0,7-1,0 Vp) → diff pair PNP «fuzz» (ceiling ±2,79 V) → recovery invertente + servo DC −65 µV; griglia musicale THD θ×programma in five-way §5.3 — CONFERMATA da Filippo 2026-09-30, decisione 87: valori bloccati come punto di partenza, review dei valori «estetici» a orecchio sul prototipo M4L; D6 rumore FATTO 2026-09-30: drive −85,7 dBu pre-makeup, VCA 218x dominante — target rumore modulo → voce 71; D5 risonanza pendente).

## 7. Modulo FX — requisiti

- [BLOCCATO] 4 bus FX (FX1-4); sorgenti: canali DJ, mic, generic mono, ritorni FX (cross-routing permesso; self-route FXn→FXn: **REV decisione 91b, 2026-10-01 = AMMESSO come quarto pot per ritorno**, prima proibito fisicamente).
- [BLOCCATO] Summing di bus: attivo virtual-earth, nominale ~0 dBu, dominio ±18 V; 10k/10k [PROVVISORIO]; ~12 contributori stereo pianificati; worst correlato +21,6 dBu entro capability con saturazione morbida (sheet §2).
- [BLOCCATO] Interfaccia pedali: bus → driver high-headroom → pad selezionabile (prototipo −20 dB) [SUPERATO dalla DECISIONE 108, 2026-10-14: pad fisso 0 dB, il livello al pedale lo fa solo LEVEL del micro-modulo FX-SEND, compensazione col GAIN del ritorno −∞…+20] → protezione → pedale → protezione/DC-control → ritorno hi-Z ≥1 MΩ; tolleranza ritorno −20…+18 dBu; bandwidth interfaccia ~5 Hz–40 kHz; mono pedal = controlled mono sum (mai hard-short L/R); stereo pedal = L/R indipendenti; pronta per pedali chitarra E rack studio.
- [BLOCCATO] Ritorni: stereo-capable (mono centrato); gain −∞→0→+20 dB; EQ 2 bande (LOW ~100-150 Hz, HIGH ~4-6 kHz, −∞→0→+6, broad, no risonanza/saturazione); meter dopo gain+EQ, prima del fader (detector rapido, clip latch ~300-500 ms); fader stereo linked; REGOLA: livello_in × gain ≤ +23 dBu (sheet §2) — rispetto affidato alla disciplina dell'operatore, nessun selettore di sensitivity né limite interno (decisione 84).
- [BLOCCATO — REV decisione 91b, 2026-10-01: destinazioni 4 = 3 cross + self, stessa law per il quarto pot] Rerouting/feedback: ogni ritorno ha 4 destinazioni (gli altri 3 bus + se stesso); level −∞→0 dB con law a tratti (0-20%: −∞…−40; 20-45%: −40…−20; 45-70%: −20…−10; 70-85%: −10…−4; 85-95%: −4…−1; 95-100%: −1…0 dB) = controllo finissimo vicino all'apertura; tecnologia VCA/attenuatore (solo attenuazione); catena controllo: pot → CV buffer → mappa non lineare → smoothing 1-5 ms → VCA; niente limiter.
- [BLOCCATO] Comportamento live: fader del ritorno = udibilità verso MASTER, NON tocca il loop interno (reroute pre-fader): fader giù, il feedback continua; controlli usabili mentre si mixa; loop unity = oscillazione autosostenuta bounded by design.
- [APERTO → PROPOSTA v0.2 2026-09-27/28] VCA esatto, switch esatti, valori resistori bus, protezione (questioni 13/14/37/52): design v0.3-WIP in `docs/fase1/fx-module.md` + micro-moduli FX-SEND (dec. 91a, `fx-send-module.md`) — THAT 2180/2181 SINGOLI ×20 nel modulo FX (matrice 16× con self-FB dec. 91b + ritorni) (voce 37: ~28-30 chip in tutto il mixer post-dec. 91, era ~24-26 post-dec. 88 / ~34-36 — "dual" del nome = porti di controllo, datasheet 2026-09-27), bus 10k [PROVVISORIO], protezione R+TVS low-cap (banda 40 kHz VERIFICATA §8.4: il polo lo fa la Z sorgente, TVS ≤5 pF buona pratica), DC servo sui ritorni VALIDATO (§8.4, corner libero 0,05-0,5 Hz); law a tratti del reroute VERIFICATA end-to-end (§8.3, smoothing 1 ms raccomandato); stabilità del loop di feedback SIMULATA ("bounded by design" = saturazione del pedale, mai ai rail; margine g_loop ≤ +3 dB). Aperto: sensitivity ritorni (questione 69).

## 8. Mic e generic mono — requisiti

- [BLOCCATO] MIC: XLR mono bilanciato; preamp 30-60 dB, Z_in ~2 kΩ, low-noise, high CMRR, fast recovery; NO phantom (V1); EQ 2 bande (LOW ~120 / HIGH ~5 kHz, −∞→0→+6, broad); meter warning-only dopo preamp prima di EQ; niente CUE/filtro/5-way/fader; → MASTER SUM.
- [DEC. 111 (d), 2026-10-14] Il modulo MIC ha in più un tasto MUTE (BBM + ramp 1 ms, dec. 80); il MONO no.
- [BLOCCATO decisione 97, 2026-10-13] MIC e MONO sono due moduli SEPARATI. Comandi di ciascuno, e nessun altro: GAIN, EQ 2 bande, 4 pot send (uno per bus FX, −∞…0 dB, presa post-EQ, nessun bottone), un LED di metering a tre colori (verde = segnale ok, giallo = vicino al clip, rosso = clip; presa pre-EQ; soglie [PROVVISORIO] −6 / +11 / +17 dBu). MIC: passa-alto fisso a 60 Hz. Massimo 4 moduli MIC/MONO nel sistema, in qualunque combinazione; primo prototipo: 1 MIC + 3 MONO.
- [ARCHITETTURA v0.1, 2026-10-13 — `docs/fase4/mic-mono-moduli.md`, valori PROVVISORI] MIC: instrumentation amp OPA1612 a 30 dB fissi + stadio 0…+30 dB — EIN −126,5 dBu (150 Ω), CMRR 74 dB con sorgente sbilanciata 10 Ω, overload 300 mV rms. MONO: buffer FET 1 MΩ + pot passivo + make-up +10 dB — rumore modulo −101,3 dBu A-wtd. Entrambi: EQ2 a celle serie, due driver separati verso MASTER SUM L/R (MIC in multidrop su MSUM6, MONO su MSUM7: i contributori restano 7).
- [BLOCCATO] GENERIC MONO: jack mono; buffer hi-Z ≥100 kΩ; gain −∞→0→+10; tollera +18 dBu; EQ 2 bande come mic; mono→stereo distribuito propriamente (mai hard-short); warning-only; niente CUE/filtro/5-way/fader; → MASTER SUM. Modulo generico, non cucito su uno strumento specifico; numero di varianti [APERTO].

## 9. Master, Booth, Rec — requisiti

- [DEC. 111 (d), 2026-10-14] Tasto MONO sul master: somma L+R; su quali uscite agisce (master, booth, rec, MON verso il CUE) da definire nel design.

Design circuitale: `docs/fase1/master-out.md` **v0.3 (2026-09-29: stadio finale BOOTSTRAP verificato — suite completa Test 7-12 in `sim/master-out/RISULTATI-composite.md`)**; resto del modulo = v0.2 + addendum REC.

- [BLOCCATO] SUMMING nel modulo master (contributori: 5-WAY, 4 FX returns, MIC, GENERIC) → MASTER LEVEL VCA −∞→0(detent)→+6 dB, stereo-linked tracking ≤0,25 dB (VCA a singola CV) → METER (post-level, il più preciso) → front ±18 V → stadio HV composito [M] (raw ±26 V dedicato, statici ±23,6…29,2 V su rete ±10% — REV dec. 93: worst case a rete −10% VERIFICATO in sim Test 13, requisito ≥+24 dBu PASS con margine ≥1,2 dB in ogni condizione di rete) con alimentazioni OPA1612 in BOOTSTRAP sull'uscita (decisioni 83→86: il VAS discreto a guadagno è bocciato dalla simulazione; follower e stabilità v0.2 invariati) — **v0.3 VALIDATA 2026-09-29 con Iq reale 40 mA**: swing ±20,4-20,9 V = +25,4…+25,6 dBu (requisito ≥+24 PASS, margine 1,4-1,6 dB; follower nudo: +23,2), THD a +24 dBu 0,00012 %@1 kHz / 0,0042 %@35 kHz (PASS <0,005), rumore −119 dBu, banda 8 Hz-35 kHz ±0,008 dB, corto auto-limitato 106 mA (Q1 1,0 W medi = worst di programma), servo DC 30 µV (fc 0,048 Hz); pass bootstrap ≈1 W medi → rame ≥4 cm² o alettina → XLR bilanciati attivi (Z out <50 Ω, ≥+24 dBu clean, no trasformatore, no colorazione).
- [BLOCCATO] BOOTH: presa pre-level, −∞→0, linked, buffer dedicato, XLR.
- [BLOCCATO] REC: presa pre-tutto, 0 dBu fissi, buffer dedicato, pad solder-only 0/−10/−20 dB.
- [BLOCCATO] Protezioni: corto/DC/RF/transienti al connettore; mute power-on (~1,5-2 s) e power-off (<10-20 ms) con relay + controller analogico; DC servo (niente cap in serie al segnale).

## 10. CUE / cuffie — requisiti

- [BLOCCATO decisione 96, 2026-10-12] Standard di qualità del percorso cuffie: classe sistema cuffie Pioneer DJM (strumento per mixare, nessun requisito audiofilo).
- [BLOCCATO] CUE solo sui canali DJ (post-EQ/pre-filter/pre-fader); più CUE attivi sommati; 2 uscite cuffia, level condiviso, amp dedicato high-current con alimentazione/ground isolati; mix CUE/MASTER: CCW=cue, centro=50/50, CW=master (stesso mix su entrambe le uscite); niente CUE per FX/mic/generic; niente meter cuffia.
- [DESIGN FATTO 2026-10-02 → `docs/fase3/sistema-cue.md` v0.1 (S5, ultimo workstream fase 3): requisiti invariati; tap MON = post-summing master pre-level (scelta di Filippo 2026-10-02, comportamento DJM-900NXS2); CUE indipendente da GLOBAL_MUTE con protezione power locale (scelta di Filippo, chiude la materia dec. 94b); numeri verificati in sim: rumore −114,5 dBu A-wtd (PASS 24,5 dB su −90), law blend e polarità. Design di sistema COMPLETO. [REV 2026-10-12: i numeri «THD ≤0,055 %, clamp 141 mA» del primo Test 1 erano INVALIDI (netlist col Vbe-multiplier spento); ampli cuffia RIDISEGNATO v0.2 e CHIUSO in sim: THD @1 Vrms 0,005 % su 16 Ω / 0,0008 % su 32 Ω, clamp 126-168 mA, idle 20 mA, nessun picco ad anello chiuso — `sim/system/RISULTATI-cue.md` Test 1 e 5-8]]

## 11. Metering — requisiti

[REV dec. 90a 2026-10-01: barre LED a zone; soglie verde ≤+6 / ambra +6…+18 / rosso +18…+24 / purple latch ≥+23 dBu; master 2×20 segmenti, zone 10; detector release ~0,3 s (dec. 81), latch 479 ms — design in `docs/fase3/sistema-metering.md`; la proposta master-out §3.6 per il purple master è SUPERATA/doppio criterio → voce 40]

- [BLOCCATO] Semantica colori universale: BLUE=poco · GREEN=safe · YELLOW=loud · AMBER=hard · RED=extreme · PURPLE=clipping reale (clip detector dedicato, latch ~300-500 ms).
- [DEC. 116, 2026-10-21] Un meter da 10 segmenti per OGNI ritorno FX (4 barre, come i canali DJ; era 1). `docs/fase3/sistema-metering.md` REV dec. 116.
- [BLOCCATO] Posizioni: DJ (post-filter/drive, pre-fader; identica calibrazione) · 5-way (post-drive, pre-master-sum) · MASTER (post-level; il più preciso: scala log 20 segmenti ×3 dB/canale, LM3915 in cascata, attacco <1 ms, release ~0,3 s ballistica viva stile Pioneer DJM — decisioni 53/81, costante da affinare a banco 0,2-0,5 s) · FX returns (post-gain/EQ, pre-fader) · mic/generic warning-only. Niente meter per booth/rec/cuffie/send.
- [PROVVISORIO] Soglie numeriche delle zone (proposta master-out §3.6) — da validare a banco; a 10 Hz leggibilità a zone con ballistica viva (decisione 81, che revisiona la parte metering della decisione 65).

## 12. Alimentazione — requisiti

[REV dec. 115, 2026-10-21: toroidale ~270 VA, W1 2×21 V 4,0 A — il modulo FX ha 40 VCA, `docs/fase3/sistema-psu.md` REV 2026-10-21] [REV dec. 90c/92 2026-10-01: PSU toroidale unico da 200 VA [REV dec. 106, 2026-10-13: ~225 VA, avvolgimento audio 2×21 V 3,0 A] (REV dec. 98, 2026-10-13: era ~120 VA; secondari 2×21 V 2,5 A · 2×18 V 1,0 A · 2×20 V 0,4 A · 9 V 2,0 A) multi-avvolgimento + regolazione locale, fanless, protezione corto 3 strati — design in `docs/fase3/sistema-psu.md`; CV VCA resta 6,1 mV/dB + routing curato + test banco (dec. 92; 61 = fallback). Riconciliazione rail raw sul backplane con §3: APERTA (review 01/10)]

- [BLOCCATO] Lineare con toroidale + regolazione locale (decisioni 45/90c); domini §1; backplane porta raw ±27/±22/±26[M] e +5 V regolato nella PSU (REV decisione 93: tabella in `docs/fase3/sistema-psu.md` v0.2); ±18/±15 LN locali per modulo (miglioria §3).
- [BLOCCATO] Mute power-on/off; sequencing; protezione per ramo di modulo; budget correnti/termico [APERTO — da calcolo a moduli definiti].
- [BLOCCATO] Rail low-noise LT3045/LT3094 per summing/CV/metering (decisione 54).

## 13. Grounding / EMC — requisiti

- [BLOCCATO] La strategia di massa va progettata come SISTEMA unico (analogue 0 V, control ground, chassis/shield, PE, masse pedali e giradischi): niente "terre separate a caso". Bonding point unico chassis/0V; trattamento schermi XLR (pin1 → rete RC → star) e RCA (rondella isolata dedicata); [APERTO] topologia esatta (questione 21).

## 14. Rumore e banda — target

- [PROVVISORIO] Allocazione per stadio (sheet §3): canale ≤−80 dBu A-wtd (dec. 89, misurato −94,6 con l'EQ isolator [docs/06 §10]; era −90,0 con l'EQ in serie) · bus FX send ≤−88 A-wtd (dec. 89, misurato −100,7) · filtro ≤−80 A-wtd (dec. 89: core nudo al limite a fc max col die reale → input q70) · **5-way ≤−80 dBu A-wtd (dec. 88, 2026-09-30: misurato −83,2 v031 al ricalcolo 2026-10-13 (era −83,9); out modulo, ingressi terminati, gain nominali, drive θ0)** · stadio XLR master ≤−92 (misurato −119,2 VALIDO; sistema ≤−78 A-wtd, dec. 89, condizioni docs/06 §2; VERIFICATO −82,9 = PASS 4,9 dB al ricalcolo 2026-10-13 sera con 5-way v0.4 e canale con isolator, docs/06 §10; era −80,0) · isolamento control→audio ≥100 dB · phono: budget dedicato al design. Tutto da validare in simulazione+misura (il −90 dBu "globale" dei doc resta target, non garanzia — correzione 13 review).
- [BLOCCATO] Banda: §1 (8 Hz–35 kHz; 10 Hz ±1 dB infrasub).

## 15. Interfaccia meccanica/elettrica

- [BLOCCATO] Il design del pannello è di Filippo; l'elettronica fornisce: consumi per modulo, pin count/famiglia connettori, correnti backplane, contatti di massa, schermature, accessi di servizio/test. Fader = slider, resto = pot rotativi; hardware manopole = sessione dedicata (questione 40). [APERTO] ingombri/telaio (questione 29).
- [DEC. 118, 2026-10-21] Rotativi principali classe 14 mm (Alps RK14K o equivalente), disposti disassati come sul Xone:DB4; EQ di FX-SEND, ritorni FX, MIC e MONO classe 9 mm senza scatto al centro. `docs/fase3/sistema-comandi.md` §Scelte hardware.
- [DEC. 119, 2026-10-22, precisa la dec. 111 (e)] Pot a corpo chiuso (senza grado IP); la protezione da polvere e liquidi la fanno guarnizioni del pannello e coperchio del flight case; pot sostituibili senza rifare la scheda.
- [DEC. 120, 2026-10-22] Fader dei canali e dei ritorni FX: corsa 100 mm. Tracking stereo ≤ 0,5 dB (dec. 59) da risolvere in ingegneria: fader selezionati o fader → VCA.
- [DEC. 121, 2026-10-22] Kill del 5-way = levette sigillate a tre posizioni ON-OFF-(ON): su = kill fisso, giù = kill a molla.
- [DEC. 122, 2026-10-22] Modo del filtro di canale = levetta sigillata a tre posizioni fisse: su HPF, centro OFF, giù LPF.
- [DEC. 123, 2026-10-22] Canale: CUE e assign FX 1-4 = bottoni con luce a ritenuta; LINE/PHONO = levetta piccola.
- [DEC. 124, 2026-10-22, PROVVISORIO] Cappucci gommati (probabile stampa 3D di Filippo); rotativi tutti con albero 6 mm a D.
- [DEC. 125, 2026-10-22] Taglia e scatto di ogni manopola: tabella in `docs/fase3/sistema-comandi.md` §Taglia e scatto (115 manopole: 64 grandi 14 mm, 10 medie = 14 mm con cappuccio ~12 mm, 41 piccole 9 mm).
- [DEC. 126, 2026-10-22, precisa la dec. 59] Fader di canali e ritorni = fader mono → CV → VCA per lato (come il Xone:92); tracking ≤ 0,5 dB dai VCA trimmati; +16 VCA (~78 nel mixer).
- [DEC. 127, 2026-10-22, precisa la dec. 105] EQ isolator del canale senza contatto di fondo corsa: banda chiusa a circa −54 dB (residuo del pot ≤ 20 Ω); il muto vero del canale è il fader.
- [DEC. 128, 2026-10-22] Uscite cuffia: due jack stereo 6,3 mm.
- [DEC. 129, 2026-10-22, PROVVISORIO] Curve dei pot: EQ secondari e GAIN 5 vie = pot lineare + resistenze di legge; WIDTH log ~20 %; LEVEL FX-SEND e cuffie log A 10 %; GAIN e SEND di MIC/MONO log A; fader «come Pioneer DJM», curva graduale (circa −12 dB a metà corsa). Da sentire nel prototipo.

- [CONDIZIONI D'USO DEL TARGET DI RUMORE] Il target di sistema ≤ −78 dBu A-wtd vale a send FX non assegnati (dec. 95: con FX in uso il floor −73…−66,6 è accettato, disciplina del level) e a overdrive del filtro chiuso (dec. 100: a 4 filtri inseriti −78,5 a overdrive chiuso, −74,8 tutto aperto in silenzio, accettato). Standard cuffie = classe Pioneer DJM (dec. 96).
- [SUPERATO al punto (1) dalla dec. 99: overdrive corrente = v0.2, vedi §5] [INGEGNERIA 2026-10-13 — design teorico completo] (1) Overdrive del filtro = cella drive del 5-way riusata con pad −6 dB e make-up +6 dB, 8 celle, mux del CV per sezione attiva (`docs/fase2/filter-module.md` §5bis); law [DA CONFERMARE-F]; con overdrive il canale filtro è −83,1 dBu A-wtd (core a) e il sistema con 4 filtri inseriti −75,3 (target −78 definito a filtri OFF) [DA DECIDERE-F]. (2) Shaper a tratti = 1 op-amp + rami diodo, verificato tra 20 e 50 °C (`docs/fase3/sistema-shaper.md`). (3) Audit infrasub: aggiunti blocco della continua all'ingresso line (0,72 Hz) e servo sul make-up EQ; percorso −0,03 dB a 10 Hz (gain-staging sheet §6). (4) Griglia del drive 5-way CORRETTA (livelli 3 dB più alti di quanto etichettato): dec. 87 da riconfermare (five-way §5.3bis). (5) Inventario comandi: `docs/fase3/sistema-comandi.md`. Lista delle decisioni che restano a Filippo: `docs/02-questioni-aperte.md`, in testa.

## 16. Roadmap di costruzione

1. [BLOCCATO decisione 61] Fase 1 — prototipi: canale CDJ/line (senza phono; filtro su OFF/bypass) + modulo FX (1 bus completo: send/pedale/return) + master-out + PSU base → validano backplane e metodo.
2. Fase 1b: secondo bus FX con feedback controllato; integrazione phono Rev A/B sui canali (dopo risposte §5 phono del PDF: le 4 domande restano aperte).
3. Fase 2: modulo filtro (SVF full-range + risonanza + overdrive) e 5-way (filter bank + EQ creativo + drive) — i due blocchi difficili, con simulazione e prototipo prima di qualunque PCB.
4. Poi: mic, generic, CUE/cuffie, metering completo, telaio definitivo, integrazione, taratura sul soundsystem.
5. Regola trasversale: nessun PCB senza topologia → simulazione → prototipo → misura. **[agg. decisione 78, 2026-09-24]** Prima del prototipo circuitale (millefori) il gesto, le curve, le leggi dei controlli e il carattere musicale si validano A ORECCHIO sul prototipo Max for Live (`docs/proto-max/piano.md`): le scelte musicali approvate sul prototipo diventano requisiti del design circuitale corrispondente. Il prototipo digitale NON valida l'elettricità (rumore, saturazione reale, tracking meccanico).

## Appendice A — Storia delle correzioni

- Versioni superate: doc §38/§18 (controlli filtro locali → condivisi; master mono → stereo; pad −20 dB congelato → selezionabile; RC RIAA → non un circuito; 0-5 V nativo → convenzione; ±24 V universale → errato).
- Letture errate corrette in corso d'opera: `docs/03-revisione-critica.md` §3 e §8 (filter core: da "per canale nel canale" a "per canale nel modulo filtro").
- Contraddizione phono DOCX-vs-PDF: risolta in "entrambe le varianti [PROVVISORIO], decide la simulazione" (decisioni 62/72; addendum dichiarato successivo dal proprietario).

## Appendice B — BOM e costi

- Stima materiali macchina completa: 3.000-4.000 € (±50%) · fase 1: 700-1.300 € · master-out ~60-90 € · canale ~35-55 € (esclusi pot/fader). BOM vere: a topologie scelte, modulo per modulo.
