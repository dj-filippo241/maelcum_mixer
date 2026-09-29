# SPECIFICA — MAELCUM MIXER (mixer dub modulare analogico, esemplare unico)

> **v0.1 (2026-09-18, rev. 2026-09-28/29: decisioni 76-85 + esiti simulazioni e sessione decisioni)** — Compilata da: decisioni 1-85 (`docs/01-decisioni-bloccate.md`),
> status doc ChatGPT rev2 (`docs/export-chatgpt/`, corpus chiuso — decisione 58),
> gain-staging sheet (`docs/fase1/gain-staging-sheet.md`), revisione critica (`docs/03`).
> Livello: REQUISITI. Il dettaglio circuitale vive nei design doc di `docs/fase1/` e `docs/fase2/`.
> Stati: [BLOCCATO] deciso · [PROVVISORIO] target di lavoro · [APERTO] da decidere ·
> [SUPERATO] versione vecchia, solo per storia.
> Metodo per la fase circuitale: requisito → funzione di trasferimento → topologia →
> componenti → simulazione → vincoli PCB → prototipo → misura → revisione.

## 1. Vincoli globali di progetto

- [BLOCCATO] Percorso audio 100% analogico. Nessun ADC/DAC/DSP interno. Il DSP esterno resta responsabile di crossover di sistema, protezione altoparlanti, EQ di sistema, delay, gestione finali.
- [BLOCCATO] Stereo L/R ovunque; no pan; nessun controllo L/R separato; controlli linked; mono-compatibile.
- [BLOCCATO] Livelli: nominale 0 dBu (0,775 Vrms); programma caldo ~+10 dBu; estremo interno ~+18 dBu; capability d'uscita pulita ≥ +24 dBu (solo stadio finale master). Referenza autorevole: gain-staging sheet.
- [BLOCCATO] Domini di alimentazione: ±24 V main (SOLO stadio HV uscita master) · ±18 V audio di percorso · ±15 V ultra-low-noise (phono, mic, CV, metering, CUE) · +5 V control. Il ±24 V non alimenta mai un op-amp.
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
                          │ MATRICE FEEDBACK: 3 reroute/ritorno, pre-fader, VCA, no self│
                          ▼                                                             ▼
                          MODULO MASTER: SUMMING → LEVEL(VCA −∞..0..+6) → METER         │
                            → HV ±24V → XLR MASTER · BOOTH (pre-level) → XLR            │
                            · REC (0 dBu fissi) ────────────────────────────────────────┘
 CUE BUS ══► MODULO CUE: somma cue → mix CUE/MASTER → amp cuffia → 2 uscite
 BACKPLANE: bus audio + bus controllo (CV/logiche) + potenza (±24, +5) + ground separati
```

- [BLOCCATO] FX returns, mic e generic mono NON passano dal 5-way (solo il DJ BUS sì).
- [BLOCCATO] Master chain: SUM → LEVEL → METER (post-level) → OUT.

## 3. Moduli e backplane

Moduli [BLOCCATO dai doc §33, consolidamento [PROVVISORIO]]: DJ CH1-4 · FILTRO · 5-WAY · FX (bus/pedali/ritorni/matrice; i doc elencano 4 moduli FX RETURN separati — accorpamento in un modulo FX da ratificare in fase di layout) · MIC · GENERIC MONO (1..n) · MASTER · CUE/CUFFIE · PSU · utility/future.

- [BLOCCATO] Bus audio: DJ L/R, FX1-4 L/R, 5-WAY L/R, MASTER L/R, CUE L/R, filter send/return per canale.
- [BLOCCATO] Bus potenza sul backplane: ±24 V, +5 V control, analogue 0 V, control ground, chassis/shield. [C-PROVVISORIO, miglioria rispetto ai doc] I rail ±18 V audio e ±15 V low-noise si generano LOCALMENTE in ogni modulo (non distribuiti sul backplane): ogni modulo isola il proprio rumore.
- [BLOCCATO] Separazione fisica audio/controllo/potenza/ground sul backplane; schermature; nessun bus floating; ogni modulo ha uno stato inattivo definito; connettori robusti card-edge/board-to-board con keying.
- [APERTO] Pinout, famiglia connettori, impedenze di bus, comportamento a modulo rimosso (questioni 22/38).

## 4. Canale DJ (modulo ×4, stereo identici)

Catena [BLOCCATO]: RCA stereo → protezione → front-end (LINE; PHONO MM v0.1 con front-end dedicato + selettore, decisione 79, `docs/fase1/phono-stage.md`) → GAIN → EQ 4 bande → nodo split post-EQ: (1) CUE, (2) FX SEND, (3) dry → FILTER SEND/RETURN → METER → FADER → out driver ≤50 Ω → DJ BUS.

- GAIN [BLOCCATO]: −∞ → 0 (detent) → +10 dB; stereo linked; tracking ≤0,5 dB.
- EQ 4 bande [BLOCCATO nel comportamento]: LOW / LOW-MID / MID-HIGH / HIGH; ogni knob −∞ → 0 (flat, detent) → +6 dB; tracking stereo ≤0,25 dB; law: lenta al centro, rapida agli estremi. **[rev. decisione 77, 2026-09-24]** l'estremo "−∞" si intende come kill di banda a **−30 dB** (profondità misurata della cella serie): il silenzio assoluto del canale resta compito del fader — il kill è un gesto musicale, non un mute. Stato beta-3 (2026-09-27, `docs/fase1/eq-serie-v0.3.md` §9.7): griglia confermata con op-amp reali OPA1654/1612 (kill LOW −29,2 @20 Hz, gonna larga; notch MID −44,2 @1 kHz); offset detent RISOLTO (−0,0001 dB con coppia 0,1%, trim multi-giro non serve); rumore −110,7 dBu PASS; kill HIGH = bump +2 dB al corner e −9…−14 dB a 20-35 kHz → questione 68 aperta (accettare il gesto "scurente" o cella crossfade-LP2).
- EQ frequenze [PROVVISORIO — review con Filippo aperta]: 70 Hz (Q~0,7) / 250 Hz (Q~0,8) / 1 kHz (Q~0,9) / 5 kHz (Q~0,7). Topologia: [SUPERATO 2026-09-24] celle a contribuzione (reference + contributo di banda), kill = contribuzione zero — bocciata dalla simulazione LTspice per le bande LOW/HIGH (fase dei filtri: `sim/cdj-eq/RISULTATI-eq.md`, questione 62). Topologia scelta: **EQ in serie per banda, famiglia Baxandall** (decisione 76) — design in CDJ v0.3 (`docs/fase1/eq-serie-v0.3.md`); comportamento locked immutato salvo l'estremo di cut: −30 dB per banda (decisione 77). Stesso finding si applica alle EQ2 di FX send/return (questione 65).
- CUE [BLOCCATO]: post-EQ, pre-filter, pre-fader; switch per canale → CUE bus.
- FX SEND [BLOCCATO]: pre-fader, pre-filter; EQ 2 bande (LOW ~120 Hz, HIGH ~4,5 kHz, −∞→0→+6) con law dedicate (bassi: rapidi solo al taglio estremo; alti: taglio rapido in partenza poi graduale); level −∞→0 (niente gain positivo); assign a S1-S4 MULTIPLO e simultaneo con precision analogue switch (JFET scartati); soppressione transiente di commutazione [BLOCCATO: break-before-make + ramp 1 ms, famiglia unica per tutte le commutazioni CV — decisione 80].
- Filtro [BLOCCATO]: solo switch 3 posizioni HPF/OFF/LPF sul canale; l'audio va al modulo filtro (send/return); break-before-make + ramp 1 ms nel modulo filtro (famiglia unica, decisione 80).
- METER DJ [BLOCCATO]: post-filter/overdrive, pre-fader; peak con persistenza; calibrazione identica tra canali (procedura di calibrazione: questione 54); colori = §11.
- FADER [BLOCCATO]: slider DJ-style conduttivo-plastica, −∞→0, stereo linked ≤0,5 dB, seguito da buffer ≤50 Ω.
- PHONO MM (v0.1 FATTO 2026-09-28 — decisione 79, chiude q6; design e numeri: `docs/fase1/phono-stage.md`) [BLOCCATO nei requisiti]: MM-only (DJ + MM alta qualità, dec. 62); RCA + ground dedicato giradischi (stella analogue-0V, q. 21); load 47 kΩ || C selezionabile 100/200/300 pF [PROVVISORIO q7]; gain totale 42 dB @1 kHz (dec. 72); topologia dec. 79: stadio piatto OPA1612 ×21 + subsonica Sallen-Key 13 Hz Q 0,707 + RIAA PASSIVA (rete a equazioni chiuse) + stadio OPA1654 ×60,6, rail ±15 V LN; accuratezza ±0,14 dB su 200 Hz-20 kHz (sotto i 100 Hz agisce la subsonica: −0,5/−1,4/−3,9 dB a 100/50/20 Hz, residuo da rifinire [PROVVISORIO]); overload +18 dBu puliti (≈20 dB sopra 5 mV ✓ Rev A), clip +24,9 dBu; EIN 0,36 µV integrati (−93,6 dBu out); warp pulito fino a ~25 mV @10 Hz; MC = variante futura separata (q. 7).
- Dominio: ±18 V audio, ±15 V LN per phono. Livelli: gain-staging sheet §2.

## 5. Modulo filtro (B′) — requisiti

- [BLOCCATO] Architettura: un core dedicato per canale (4 stereo = 8 mono, stesso PCB), DUE sezioni di parametri condivise: HPF (freq, res, overdrive) e LPF (freq, res, overdrive) = 6 knob sul pannello del modulo. Ogni canale con switch HPF/OFF/LPF segue i knob della sua sezione. BPF escluso.
- [BLOCCATO] Range: entrambe le sezioni **10 Hz–35 kHz** (decisione 74); pendenza 24 dB/ottava (4 poli: 2 sezioni 2-poli SVF in cascata, controllo di frequenza matched); overlapping utilizzabile HPF/LPF.
- [BLOCCATO] Legge dei knob: musicale nei ~90% centrali, accelerazione forte negli ultimi ~5% a entrambe le estremità; all'estremo di taglio = cancellazione totale (HPF in cima, LPF in fondo). Implementazione: shaper CV a tratti, punti di piega regolabili a banco.
- [BLOCCATO] Risonanza: 0-70% normale, 70-90% aggressiva, 90-100% auto-oscillazione che segue il cutoff; livello oscillazione ~+6…+10 dBu con soft limiting (non clamp a diodi crudi); carattere musicale, riferimento Sherman Filterbank.
- [BLOCCATO] Overdrive: dopo filtro/risonanza, prima del meter di canale; 0 = pulito ~unity; progressione clean → subtle → warm → gritty → aggressive → hard dub overload; referenza sonora = Sherman Filterbox, raschio acido che cresce con la risonanza (decisione 82); prototipi JFET (prima) e BJT asimmetrico (poi); recovery low-Z 20-50 Ω, clean +23 dBu (raffinamento del "+24 where practical": il ±18 V del modulo non dà +24 — decision sheet §2); nessun makeup compression.
- [PROVVISORIO/INGEGNERIA] Converter di frequenza: esponenziale + tempco, range gm ~3500:1; tolleranza accettabile ±5-10% (più lasca di un VCO); core in tracking tra canali ≤2% a pari CV con trim per core; CV bufferizzati, distribuzione a stella, smoothing.
- [APERTO in parte — aggiornato 2026-09-28] Topologia SVF concreta: il LM13700 reale ha un tetto di stato strutturale (52 mV a f0) → il core OTA nudo a 0 dBu comprime morbido (~1% THD, collasso a +10 dBu): **questione 70** — scelta MUSICALE di Filippo tra (a) carattere OTA nudo (design v0.2 invariato, famiglia Sherman) e (c-B) integratori op-amp + VCA 218x (pulito, +16 chip), entrambe quantificate (`sim/filtro/RISULTATI-ota-real.md` + `sim/five-way/RISULTATI-cell-clean.md`); le CELLE parametriche 5-way hanno già adottato la variante pulita (c-A) JFET VCR (design v0.2.1, five-way §4.2). Fattibilità converter esponenziale 10 Hz–35 kHz DIMOSTRATA (`docs/fase2/filter-module.md` §6 — questione 51 aggiornata, 49 chiusa; con (c-B) la distribuzione diventa Vc a buffer, più semplice). Restano aperti: loop di risonanza/limiting (questione 11), curva esatta del drive (questioni 12/61), interpretazione mux CV e allineamento 4 poli (questioni 63/64).

## 6. Modulo 5-way (dub preamp) — requisiti

- [BLOCCATO] Posizione: DJ BUS → 5-WAY → MASTER SUM. Riferimento interno −6 dB (pad in / makeup out, decisione 73).
- [BLOCCATO] KILL: 5 sezioni = 5 vie dell'impianto; mappa [PROVVISORIO]: SUB ~10-90 Hz (esteso a 10 Hz per infrasub — decisione 65), KICK ~90-350, MID ~350-1,2k, HIGH ~1,2-3,5k, SUPER HI ~3,5-20k; 24 dB/ottava iniziali, overlap deliberato senza buchi; filter bank complementare (somma piatta senza kill); KILL prima dell'EQ creativo (il boost non ripristina materiale killato); kill switch per via (uno per altoparlanti fisici).
- [BLOCCATO] EQ creativo 5 bande: gain/position/width per banda (comandi gain = 5 pot rotativi, decisione 85); −∞/0/+15 (bande 1-3), +12 (banda 4), +9 (banda 5); range [PROVVISORIO]: 20-120 / 80-400 / 250-1,5k / 800-5k / 3-20 kHz; width: narrow ~Q3, medium ~Q1, broad ~Q0,5; position sposta il centro senza stravolgere gain/Q.
- [BLOCCATO] Drive: dopo la somma EQ, prima del meter; full CCW = 0 dB (pulito), solo gain positivo CW; ~50% = punto ottimale (+7 dB senza distorsione), 50→80% = saturazione progressiva calda stile nastro, 80→100% = territorio fuzz (decisione 82); interagisce con gain di banda e overdrive filtro; JFET prima / BJT asimmetrico poi.
- [BLOCCATO] Meter: dopo il drive, prima del master sum.
- [PROPOSTA v0.2.1 2026-09-28 — celle EQ ridisegnate su JFET VCR (q. 70 chiusa lato celle); banca/gate invariati] Matematica del filter bank, topologie celle EQ, circuiti position/width, taper esatto del drive (questioni 8/9/10): design in `docs/fase2/five-way-module.md` — kill bank LR4 + gate VCA VALIDATO (all-kill = silenzio assoluto); **somma piatta ESATTA OTTENUTA in v0.2**: banca allineata in fase (spina HP condivisa + compensazione allpass A2, §3.1) validata −0,0002…−0,008 dB su 5 Hz–60 kHz (questione 8: matematica risolta; frequenze restano questione 67); EQ creativo = parametriche SVF: algebra VALIDATA v0.2 (§4.1/§8.3) e topologia RIDISEGNATA **v0.2.1** (§4.2/§8.8, questione 70: il LM13700 ha tetto di stato 52 mV → integratori op-amp + JFET VCR bootstrappato, core −12 dBu locale) — verificata: detent ±0,0001 dB, boost ±0,02 dB sui target +9/+15, notch −46…−47 dB (spec −30 ✓), law position ±0,03% su 2,6 ottave, THD 0,005%/0,125% worst, rumore modulo ~−101 (target −90 ✓); pot gain nel dominio del segnale (cablato sul terminale opposto: gesto invariato); law/taper = ascolto M4L; drive in attesa referenze (questione 61).

## 7. Modulo FX — requisiti

- [BLOCCATO] 4 bus FX (FX1-4); sorgenti: canali DJ, mic, generic mono, ritorni FX (cross-routing permesso; self-route FXn→FXn proibito fisicamente).
- [BLOCCATO] Summing di bus: attivo virtual-earth, nominale ~0 dBu, dominio ±18 V; 10k/10k [PROVVISORIO]; ~12 contributori stereo pianificati; worst correlato +21,6 dBu entro capability con saturazione morbida (sheet §2).
- [BLOCCATO] Interfaccia pedali: bus → driver high-headroom → pad selezionabile (prototipo −20 dB) → protezione → pedale → protezione/DC-control → ritorno hi-Z ≥1 MΩ; tolleranza ritorno −20…+18 dBu; bandwidth interfaccia ~5 Hz–40 kHz; mono pedal = controlled mono sum (mai hard-short L/R); stereo pedal = L/R indipendenti; pronta per pedali chitarra E rack studio.
- [BLOCCATO] Ritorni: stereo-capable (mono centrato); gain −∞→0→+20 dB; EQ 2 bande (LOW ~100-150 Hz, HIGH ~4-6 kHz, −∞→0→+6, broad, no risonanza/saturazione); meter dopo gain+EQ, prima del fader (detector rapido, clip latch ~300-500 ms); fader stereo linked; REGOLA: livello_in × gain ≤ +23 dBu (sheet §2) — rispetto affidato alla disciplina dell'operatore, nessun selettore di sensitivity né limite interno (decisione 84).
- [BLOCCATO] Rerouting/feedback: ogni ritorno ha 3 destinazioni (gli altri bus), no self; level −∞→0 dB con law a tratti (0-20%: −∞…−40; 20-45%: −40…−20; 45-70%: −20…−10; 70-85%: −10…−4; 85-95%: −4…−1; 95-100%: −1…0 dB) = controllo finissimo vicino all'apertura; tecnologia VCA/attenuatore (solo attenuazione); catena controllo: pot → CV buffer → mappa non lineare → smoothing 1-5 ms → VCA; niente limiter.
- [BLOCCATO] Comportamento live: fader del ritorno = udibilità verso MASTER, NON tocca il loop interno (reroute pre-fader): fader giù, il feedback continua; controlli usabili mentre si mixa; loop unity = oscillazione autosostenuta bounded by design.
- [APERTO → PROPOSTA v0.2 2026-09-27/28] VCA esatto, switch esatti, valori resistori bus, protezione (questioni 13/14/37/52): design v0.2 in `docs/fase1/fx-module.md` — THAT 2180/2181 SINGOLI ×16 (voce 37 critica: ~34-36 chip in tutto il mixer — "dual" del nome = porti di controllo, datasheet 2026-09-27), bus 10k [PROVVISORIO], protezione R+TVS low-cap (banda 40 kHz VERIFICATA §8.4: il polo lo fa la Z sorgente, TVS ≤5 pF buona pratica), DC servo sui ritorni VALIDATO (§8.4, corner libero 0,05-0,5 Hz); law a tratti del reroute VERIFICATA end-to-end (§8.3, smoothing 1 ms raccomandato); stabilità del loop di feedback SIMULATA ("bounded by design" = saturazione del pedale, mai ai rail; margine g_loop ≤ +3 dB). Aperto: sensitivity ritorni (questione 69).

## 8. Mic e generic mono — requisiti

- [BLOCCATO] MIC: XLR mono bilanciato; preamp 30-60 dB, Z_in ~2 kΩ, low-noise, high CMRR, fast recovery; NO phantom (V1); EQ 2 bande (LOW ~120 / HIGH ~5 kHz, −∞→0→+6, broad); meter warning-only dopo preamp prima di EQ; niente CUE/filtro/5-way/fader; → MASTER SUM.
- [BLOCCATO] GENERIC MONO: jack mono; buffer hi-Z ≥100 kΩ; gain −∞→0→+10; tollera +18 dBu; EQ 2 bande come mic; mono→stereo distribuito propriamente (mai hard-short); warning-only; niente CUE/filtro/5-way/fader; → MASTER SUM. Modulo generico, non cucito su uno strumento specifico; numero di varianti [APERTO].

## 9. Master, Booth, Rec — requisiti

Design circuitale: `docs/fase1/master-out.md` v0.2 + addendum (valido salvo stadio finale: bootstrap delle alimentazioni OPA1612 per decisioni 83→86 → v0.3).

- [BLOCCATO] SUMMING nel modulo master (contributori: 5-WAY, 4 FX returns, MIC, GENERIC) → MASTER LEVEL VCA −∞→0(detent)→+6 dB, stereo-linked tracking ≤0,25 dB (VCA a singola CV) → METER (post-level, il più preciso) → front ±18 V → stadio HV composito ±24 V con alimentazioni OPA1612 in BOOTSTRAP sull'uscita (decisioni 83→86: il VAS discreto a guadagno è bocciato dalla simulazione; follower e stabilità v0.2 invariati, swing atteso ±21 V = +25 dBu contro il follower nudo che misurava +23,2) → XLR bilanciati attivi (Z out <50 Ω, ≥+24 dBu clean, no trasformatore, no colorazione).
- [BLOCCATO] BOOTH: presa pre-level, −∞→0, linked, buffer dedicato, XLR.
- [BLOCCATO] REC: presa pre-tutto, 0 dBu fissi, buffer dedicato, pad solder-only 0/−10/−20 dB.
- [BLOCCATO] Protezioni: corto/DC/RF/transienti al connettore; mute power-on (~1,5-2 s) e power-off (<10-20 ms) con relay + controller analogico; DC servo (niente cap in serie al segnale).

## 10. CUE / cuffie — requisiti

- [BLOCCATO] CUE solo sui canali DJ (post-EQ/pre-filter/pre-fader); più CUE attivi sommati; 2 uscite cuffia, level condiviso, amp dedicato high-current con alimentazione/ground isolati; mix CUE/MASTER: CCW=cue, centro=50/50, CW=master (stesso mix su entrambe le uscite); niente CUE per FX/mic/generic; niente meter cuffia.

## 11. Metering — requisiti

- [BLOCCATO] Semantica colori universale: BLUE=poco · GREEN=safe · YELLOW=loud · AMBER=hard · RED=extreme · PURPLE=clipping reale (clip detector dedicato, latch ~300-500 ms).
- [BLOCCATO] Posizioni: DJ (post-filter/drive, pre-fader; identica calibrazione) · 5-way (post-drive, pre-master-sum) · MASTER (post-level; il più preciso: scala log 20 segmenti ×3 dB/canale, LM3915 in cascata, attacco <1 ms, release ~0,3 s ballistica viva stile Pioneer DJM — decisioni 53/81, costante da affinare a banco 0,2-0,5 s) · FX returns (post-gain/EQ, pre-fader) · mic/generic warning-only. Niente meter per booth/rec/cuffie/send.
- [PROVVISORIO] Soglie numeriche delle zone (proposta master-out §3.6) — da validare a banco; a 10 Hz leggibilità a zone con ballistica viva (decisione 81, che revisiona la parte metering della decisione 65).

## 12. Alimentazione — requisiti

- [BLOCCATO] Lineare con toroidale + regolazione locale (decisione 45); domini §1; backplane porta ±24 V e +5 V; ±18/±15 LN locali per modulo (miglioria §3).
- [BLOCCATO] Mute power-on/off; sequencing; protezione per ramo di modulo; budget correnti/termico [APERTO — da calcolo a moduli definiti].
- [BLOCCATO] Rail low-noise LT3045/LT3094 per summing/CV/metering (decisione 54).

## 13. Grounding / EMC — requisiti

- [BLOCCATO] La strategia di massa va progettata come SISTEMA unico (analogue 0 V, control ground, chassis/shield, PE, masse pedali e giradischi): niente "terre separate a caso". Bonding point unico chassis/0V; trattamento schermi XLR (pin1 → rete RC → star) e RCA (rondella isolata dedicata); [APERTO] topologia esatta (questione 21).

## 14. Rumore e banda — target

- [PROVVISORIO] Allocazione per stadio (sheet §3): canale ≤−92 dBu · bus FX ≤−88 · 5-way ≤−90 · XLR master ≤−92 (sistema ≤−90 con margine) · isolamento control→audio ≥100 dB · phono: budget dedicato al design. Tutto da validare in simulazione+misura (il −90 dBu "globale" dei doc resta target, non garanzia — correzione 13 review).
- [BLOCCATO] Banda: §1 (8 Hz–35 kHz; 10 Hz ±1 dB infrasub).

## 15. Interfaccia meccanica/elettrica

- [BLOCCATO] Il design del pannello è di Filippo; l'elettronica fornisce: consumi per modulo, pin count/famiglia connettori, correnti backplane, contatti di massa, schermature, accessi di servizio/test. Fader = slider, resto = pot rotativi; hardware manopole = sessione dedicata (questione 40). [APERTO] ingombri/telaio (questione 29).

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
