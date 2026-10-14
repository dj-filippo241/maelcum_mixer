# FASE 2 — Modulo FILTRO: design v0.2 + v0.3-WIP (2026-09-28)

> **D5 (2026-10-14, dec. 109, `sim/filtro/RISULTATI-D5.md`) → §5quater**:
> il core (a) nudo di §3 non funziona ai livelli di progetto col chip
> reale (picco di risonanza sotto −12 dBu, oscillazione 3,5 ottave sotto
> FREQ). Core OTA corrente = **(a′)**: partitore 1/30 davanti agli OTA,
> C 1,1 nF, limitatore a perdita non lineare verso il summer. Il soft
> limiter sul nodo BP di §5 è SUPERATO. B1 resta aperta: (a′) o (c-B).
> **v0.3-WIP (2026-09-28, `sim/filtro/RISULTATI-ota-real.md`)**: item §9.2 e
> §9.3 FATTI — (a) ramp BBM validata: τ 1 ms = click −8,4 dB vs brusco,
> 5 ms ≈ baseline; famiglia unica 1 ms con gate 5-way [escluso dec. 88: kill hard-cut a switch] e reroute FX (ratificata:
> decisione 80); il mux di modo resta dopo la questione 63; (b) LM13700
> REALE: modello transistor-level condiviso `sim/lib/lm13700.inc` (calibrato
> datasheet TI SNOSBW2F), law/Q/offset/rumore del core CONFERMATI (fc ≤1,5%,
> Q 0,70-0,71, stati DC 4-5 mV bounded, rumore −107,8…−134,8 dBu PASS — SUPERATO dal rerun 71A: `sim/filtro/RISULTATI-filtro-noise-71A.md`, target ≤−80 A-wtd dec. 89, core nudo al limite a fc max col die reale → input q70);
> FINDING STRUTTURALE: tetto di stato 52 mV a f0 (Iout max ≈ Iabc) → il core
> nudo a 0 dBu è un compressore morbido (~1% THD, collasso a +10 dBu) e lo
> scaling+make-up non soddisfa THD e rumore insieme → **questione 70**
> (topologia core — PoC VALIDATO 2026-09-28: `sim/five-way/RISULTATI-cell-clean.md`;
> per il filtro: scelta musicale (a) carattere nudo vs (c-B) VCA pulito). Vincolo
> PSU: LM13700 raccomandato ±16 V (assoluto ±18) → rail dedicati ±15/±16
> (questione 20).
> **v0.2 (2026-09-25)**: aggiunge alla v0.1 il design SIMULATO della risonanza
> con auto-oscillazione e soft limiting (questione 11: +7,3…+8,6 dBu misurati,
> target SPEC +6…+10 centrato), l'architettura di distribuzione Iabc agli 8 core
> con verifica del tracking (questione 51: mirror bufferizzato ≤1,6%), e la
> specifica del law shaper (dec. 70) con pre-distorsione dell'errore residuo del
> converter. Overdrive ancora in attesa delle referenze di Filippo (questioni
> 12/61). NON congela valori (regola 3): tutto [PROVVISORIO] salvo i requisiti
> [BLOCCATO] citati.
> **v0.1 (2026-09-24)**: architettura, funzioni di trasferimento, topologia del
> core e verifica di fattibilità del converter esponenziale (questione 51,
> condizione della decisione 74).
> Fonti: SPECIFICA §5, decisioni 67/68/70/74, gain-staging sheet §2, `docs/04-...` §9.

## 1. Requisiti (stato: BLOCCATO salvo dove indicato)

| Requisito | Valore | Fonte |
|---|---|---|
| Architettura | B′: core dedicato per canale, 4 stereo = 8 mono, stesso PCB | dec. 67 |
| Sezioni | HPF e LPF indipendenti, entrambe full-range **10 Hz–35 kHz** | dec. 74 |
| Pendenza | 24 dB/ott (4 poli = 2 sezioni 2-poli in cascata per core) | SPECIFICA §5 |
| Pannello | 6 knob: FREQ/RES/DRIVE per sezione; per canale solo switch HPF/OFF/LPF | dec. 67 |
| Legge knob | curva Xone:96 (20 Hz–20 kHz esponenziale) nel 90 % centrale; ultimi 5 % per lato fino a 10 Hz / 35 kHz; estremo di taglio = silenzio totale | dec. 70/74/102 |
| Risonanza | 0-90 % curva Xone:96 (da sottile a un passo dall'oscillazione: Q = 0,707/(1 − θ/0,9) → picco per sezione ~0 / +4 / +10 / +16 / +22 dB a 25 / 50 / 70 / 80 / 85 %); 90-100 % auto-oscillazione che segue il cutoff, +6…+10 dBu con soft limiting | SPECIFICA §5, dec. 102 |
| Overdrive | dopo filtro, prima del meter di canale; clean → hard dub overload; JFET prima / BJT asimmetrico poi; recovery low-Z 20-50 Ω, +23 dBu clean | SPECIFICA §5, sheet §2 |
| Tracking | ≤2% in frequenza tra core a pari CV; trim per core; CV bufferizzate a stella | dec. 67, voce 51 |
| Tolleranza freq | ±5-10% (più lasca di un VCO: un filtro non deve essere "intonato") | dec. 74 |
| Commutazione | break-before-make + ramp 1-5 ms, nel modulo filtro | SPECIFICA §4 |
| Livelli | send 0 dBu nom / +16 max; dominio ±18 V audio, ±15 V LN per CV | sheet §2 |
| Range gm | ~3500:1 (11,8 ottave) via converter esponenziale + tempco | dec. 74 |

## 2. Architettura del modulo

```
                    MODULO FILTRO (v0.1)
 IN from backplane (4× stereo send + 2 bit modo per canale)
  │
  ├─ CH1 L/R ─► buffer in ─► CORE 1L/1R ─┬─► mux modo ─► drive HPF/LPF ─► recovery ─► buffer out ─► return CH1
  ├─ CH2 L/R ─► buffer in ─► CORE 2L/2R ─┤   (HPF/OFF/     (mux CV: la sezione attiva
  ├─ CH3 L/R ─► buffer in ─► CORE 3L/3R ─┤    LPF/OFF+bypass)  decide il set di drive)
  └─ CH4 L/R ─► buffer in ─► CORE 4L/4R ─┘
  SEZIONE CV HPF ┐ 6 knob (0-5 V) ─► law shaper (dec. 70) ─► converter expo (§4)
  SEZIONE CV LPF ┘        ├─► FREQ: 1 master per sezione → distribuzione a 8 core + trim
                          ├─► RES: distribuzione a stella bufferizzata [v0.2]
                          └─► DRIVE: mux per canale segue il bit di modo [v0.2]
  Commutazione modo: break-before-make + ramp 1-5 ms (generatore di rampa nel modulo)
```

- Ogni core mono = SVF 4 poli (2 sezioni 2-poli in cascata): produce HP e LP
  contemporaneamente; il mux di canale sceglie HP, LP o OFF (bypass). BPF escluso (dec. 67).
- Le due sezioni di un core condividono la stessa frequenza? NO: HPF e LPF sono sezioni
  indipendenti con FREQ proprie — il core fisico lavora nella modalità selezionata dal
  canale: la CV di frequenza arriva dal master della sezione attiva (mux CV prima del core).
  Un solo percorso filtro attivo per canale alla volta (HPF oppure LPF), coerente con
  "switch 3 posizioni sul canale" (dec. 67). [Interpretazione da confermare con Filippo:
  la alternativa è core doppio per canale (HPF e LPF sempre attivi in serie) = 16 core.]

## 3. Core SVF — funzione di trasferimento e topologia

Sezione 2-poli, stato HP/BP/LP (solo HP e LP usati; BP serve alla risonanza):

    HP(s) = −Vin·s²/D(s)    BP(s) = +Vin·ω0·s/D(s)    LP(s) = −Vin·ω0²/D(s)
    D(s)  = s² + s·ω0/Q + ω0²    ω0 = gm/C = 19,2·Iabc/C    Q = R_in,Rf del summer

- **Integratori**: OTA (LM13700 [PROVVISORIO]) su C = 33 nF [PROVVISORIO, C0G/PP
  matched 2%]: Iabc 114 nA → fc 10,6 Hz; Iabc 397 µA → fc 37 kHz.
- **BUFFER DI STATO OBBLIGATORI** (lezione dalla simulazione, §6): le uscite OTA vedono
  solo il condensatore (Z = 1/sC); i resistori del summer le caricano e creano un polo
  parassita a 1/(2π·R·C) ≈ 500-700 Hz che sotto quella soglia rompe l'integrazione
  (misurato: −8% in banda, fc compressa del 35%). Con buffer follower sui nodi bp/lp
  il loop torna esatto: Q misurata = 0,707 (±0,001) su tutti i 78 punti della griglia.
- **Summer**: op-amp invertente, 3 ingressi (Vin, LP, BP/Q); Q fissato dai resistori
  (0,1%): Q = 0,707 nella simulazione di fattibilità; il controllo RES è design v0.2
  (candidati: OTA come resistenza controllata in tensione sul percorso BP, oppure
  VCA — questione 11).
- Cascata per i 4 poli: sezione 1 (Q1) → sezione 2 (Q2) [allineamento esatto v0.2:
  Butterworth 4 poli = Q 0,541/1,307, oppure Bessel/LR a seconda del carattere —
  scelta musicale da proporre a Filippo con curve d'ascolto].
- Conteggio silicon per sezione 2-poli: 1 LM13700 (2 OTA) + 3 sezioni op-amp
  (summer + 2 buffer). Per core 4 poli: 2 LM13700 + 6 sezioni op-amp.
  Modulo: 8 core = **16 LM13700 + 48 sezioni op-amp** (~12 quad) + CV + drive.
  Conferma la "conseguenza elettrica accettata" della decisione 67.

## 4. Controllo di frequenza — converter esponenziale tempcompensato

> **[REV 2026-10-14, dec. 111, todo 49 — FINDING]** Il converter compensa
> la sua coppia (ΔV scalato PTAT), ma non la gm degli OTA: nell'LM13700
> reale gm = Iabc/2V_T, e a Iabc fissa scende dell'11,8 % da 25 a 65 °C
> (`sim/filtro/ota-selftest-ac-temp.cir`). Con Iref = 400 µA fissa tutti i
> core scendono di ~1,6 semitoni da 35 a 65 °C interni, mentre il mixer si
> scalda (40 °C ambiente, dec. 111 e). **Iref va resa PTAT** (Iref =
> V_PTAT/R, dallo stesso generatore che scala ΔV): allora Iabc ∝ T e gm
> resta costante. La deriva «≤ 2,4 % su 0-50 °C» del §6 vale solo per
> l'OTA ideale della simulazione di fattibilità. Da progettare e
> simulare col modello reale (todo).

Problema: spazzare 10 Hz–35 kHz (3500:1 = 11,8 ottave) con law esponenziale
(1 ottava = ΔV fisso) e deriva termica entro ±5-10% (dec. 74). La fisica: in un
bipolare Ic ∝ exp(Vbe/V_T) e V_T = kT/q cresce +0,085%/K → senza compensazione
le 11,8 ottave derivano del ~70% su 0-50 °C (misurato, §6).

**Topologia scelta [PROVVISORIA]** (classica da sintesi analogica):

```
            +15V
             │
            Iref 400 µA          BJT matched Q1/Q2 (stesso die, stesso T)
             ├──┐                ΔV = Vbe1 − Vbe2 (comando, scalato PTAT)
             │  │                Ic2 = Ic1·exp(−ΔV/V_T)  ← Is SI CANCELLA
        ┌────┴──┴────┐           (rapporto puro: il drift di Is/T non entra)
        │ Q1 (diodo) │
        va───────────┤ΔV (B: PTAT-scaled)
        │ Q2         ├──► vb2
        └─ c: iabc ──┘   Vce2 = 0,5 V FISSO da rail dedicato (NON da va!)
             │
          [Vabc 0V] → Iabc = Ic2 → mirror/trim → OTA dei core
             │
            GND
```

- ΔV span: 0…211 mV = V_T·ln(3500) a 300 K → **scaling PTAT** (ΔV generato proporzionale
  a T assoluta: moltiplicatore ΔVbe/bandgap, tecnica standard) → la law esponenziale
  resta identica a ogni temperatura. Misurato: deriva residua ~±0,5% su 0-50 °C (§6).
- **Due trappole evitate** (entrambe trovate in simulazione, §6):
  1. il differential pair single-ended comprime le ottave alte contro la corrente di
     coda (Ic ≤ I_tail): legge esponenziale persa sopra ~1 ottava dal fondo scala;
  2. alimentare il collettore di Q2 dal nodo di riferimento (va) fa sì che Iref debba
     fornire ANCHE Ic2 → stessa compressione rientra dalla finestra (misurato: −27…−53%
     a vc alto). Il collettore va alimentato da un rail proprio a Vce fisso.
- ΔV viene dal CV bus (0-5 V) attraverso: law shaper a tratti (dec. 70) → divisore di
  precisione (~1/24) → stadio PTAT.
- **Law shaper — SPECIFICA v0.2** [PROVVISORIO, rifinitura a banco come da dec. 70]:
  - **Legge target — DECISIONE 102 (2026-10-13): curva della Xone:96 nel 90 %
    centrale.** θ = rotazione 0→1. Per 0,05 ≤ θ ≤ 0,95: f = 20 Hz · 1000^((θ − 0,05)/0,9)
    (20 Hz → 20 kHz, 10 ottave, 1,11 ottave ogni 10 % di corsa). Ultimi 5 % per
    lato, esponenziali: 20 → 10 Hz (1 ottava in 5 %: ×1,8) e 20 → 35 kHz (0,81
    ottave in 5 %: ×1,45). Tabella θ → f: 0 % 10 Hz · 5 % 20 Hz · 10 % 29 Hz ·
    25 % 93 Hz · 40 % 294 Hz · 50 % 632 Hz · 60 % 1,36 kHz · 75 % 4,31 kHz ·
    90 % 13,6 kHz · 95 % 20 kHz · 100 % 35 kHz. Riferimento per shaper e
    prototipo M4L. [SUPERATO: f(0,05) = 14 Hz, f(0,95) = 25 kHz, «~4×» agli
    estremi — in ottave gli estremi risultavano più lenti del centro.]
  - **Pre-distorsione**: l'errore residuo misurato del converter (§6: −3,6% → −9,4%,
    curva liscia monotona) si compensa nello shaper: vc* = vc_ideale − e(vc)/2,355
    (correzione ≤ 40 mV agli estremi) — la law risultante è esponenziale pura entro
    ~±1%.
  - [CIRCUITO E VALORI 2026-10-13 → `docs/fase3/sistema-shaper.md` §3: Rm 9,09k + ramo alto 20k/24,3k + ramo basso 11,3k/80,6k; law dec. 102 esatta dal 10 al 90 %, ginocchi entro −12 %…+8 % a 50 °C]
  - Circuito: generatore piecewise-lineare ATTIVO a tratti (2 sezioni op-amp per
    sezione CV: stadio a guadagno commutato da rami diodi-resistori in feedback +
    invertitore), riferimenti di piega da partitori sui rail ±15 V LN con trimmer
    (2 endpoint + 2 breakpoint + gain PTAT = 5 trim per sezione, "rifinitura a banco"
    della dec. 70). Simulazione/verifica della rete = al prototipo (tecnica standard
    da sintetizzatore; la curva matematica qui sopra è il requisito).
- **Distribuzione Iabc — DESIGN v0.2 SIMULATO** (`sim/filtro/mirror.cir`, questione 51):
  1 converter master per sezione (HPF, LPF) → **mirror bufferizzati** (servo op-amp
  che forza Vbe del ramo di uscita = Vbe del ramo di riferimento: le correnti di base
  non passano dal segnale) → 8 rami + trim per core. Misure (β da 50 a 300, estremi
  108 nA / 380 µA):
  - mirror SEMPLICE: errore variabile 2,8-3,2 punti % al variare di β → tracking
    fuori target (≤2%) — SCARTATO;
  - mirror BUFFERIZZATO: variazione tra rami ≤1,6 punti % → **tracking PASS ≤2%**;
    errore assoluto −3…−7% (α del ramo di ingresso a corrente bassa) = comune a
    tutti i core → si assorbe col trim di endpoint del converter, non intacca il
    tracking.
  Regole costruttive: transistor dei mirror in quad matched sullo stesso die, PCB
  simmetrico termicamente (converter e mirror lontani da stadi caldi), trim per core
  (10 giri) in produzione/calibrazione. Alternativa scartata: converter per core
  (8 coppie matched + ΔV distribuito: budget di offset 0,5 mV → 2%, troppo stretto
  senza trim dedicati).
- Coppia matched: candidati [reperibilità DA VERIFICARE, come voce 37 per THAT 2181]:
  MAT12 (ADI), SSM2212 (legacy), DMMT3904W (Diodes Inc.), BC847BPDW; in subordine
  coppia discreta selezionata + accoppiamento termico (stessa piazzola, colla termica).

## 5. Risonanza, overdrive, commutazione (design v0.2 — requisiti qui sotto)

- **RES — DESIGN v0.2 SIMULATO** (`sim/filtro/res-osc.cir`, questione 11): Q variabile
  via **iniezione OTA nel summer** — 1 sezione LM13700 di riserva per core (stessa
  famiglia e tecnica gm/Iabc del controllo frequenza; niente VCA aggiuntivi):
  `1/Q = Rf · gm_res`, gm_res = 19,2·Iabc_res. Law del knob RES [PROVVISORIA]:
  θ 0→0,9: gm_res da +141 µS (Q 0,707) verso 0 (Q→∞, "aggressiva" 70-90% della
  SPECIFICA); θ 0,9→1,0: gm_res passa a NEGATIVO (−106…−141 µS) = l'anello guadagna
  invece di smorzare → **auto-oscillazione** che segue il cutoff (proprietà naturale
  dell'SVF). Il gm differenziale dell'OTA accetta lo steering oltre il balance:
  nessun trucco di polarità nel circuito.
- **Soft limiting**: sul nodo BP, Rlim 1 kΩ + due stringhe antiparallele 3×1N4148
  (soglie ~1,7 V, conduzione graduale — niente clamp crudi, SPECIFICA §5).
  L'ampiezza di oscillazione è l'equilibrio tra margine d'anello e assorbimento
  del limiter — NON dalle condizioni iniziali (lezione simulata: servono perdite
  d'anello realistiche nel modello, Q_loss ≈ 400).
- **Misure** (fc ≈ 1 kHz, tran 3 s, regime):

  | margine (gres) | ampiezza BP | livello |
  |---|---|---|
  | 0 (Q→∞, solo perdite) | 0,90 Vp | −1,7 dBu |
  | −0,35 | 1,93 Vp | +4,9 dBu |
  | −0,50 | 2,15 Vp | +5,8 dBu |
  | **−0,75 (nominale)** | **2,53 Vp** | **+7,3 dBu** |
  | −1,0 | 2,96 Vp | +8,6 dBu |

  Target SPECIFICA (+6…+10 dBu) centrato con range di trim a banco. Sotto soglia
  il picco di risonanza segue Q esattamente (verificato: Q 8,8 → +18,9 dB sul
  segnale di prova). Carattere della sinusoide limitata: da ascoltare al
  prototipo (riferimento Sherman — questione 61 per le referenze).
  Innesco reale: dal rumore proprio, <1 ms (in simulazione via .ic).
- **DRIVE/overdrive** (questioni 12/61): JFET prima / BJT asimmetrico poi (SPECIFICA §5);
  dominio ±18 V, recovery low-Z 20-50 Ω con +23 dBu clean (sheet §2/K5). La curva
  clean→gritty→hard dub è sound design: aspetta le referenze di Filippo (questione 61).
  Mux CV: il drive di canale segue la sezione attiva (dec. 67).
- **OVERDRIVE — DESIGN v0.1 (2026-10-13) → §5bis** (sostituisce la riga
  qui sopra: le referenze sono arrivate con la decisione 82).
- **Modo OFF**: bypass secco del core (return = send) con break-before-make + ramp
  1 ms generata nel modulo (SPECIFICA §4, decisione 80). Switch analogici famiglia ADG14xx
  [PROVVISORIO, stessi candidati dell'assign FX — metodo decisione 80].
- Livelli interni: send 0 dBu nom/+16 max → buffer in → core (picco risonanza
  +10 dBu sopra il livello, sheet) → drive → recovery → return. Il dominio ±18 V
  del canale resta valido su tutto il modulo (sheet §2).

## 5bis. Overdrive — design v0.1 (2026-10-13, chiude la questione 12 lato ingegneria)

> **[SUPERATO — DECISIONE 99, 2026-10-13]** Filippo non vuole lo stesso
> circuito del drive 5-way («se no diventa ridondante»). Requisiti nuovi:
> rendere più drammatici e violenti i transienti di filtro; meno aggressivo
> dello Sherman; estremi accessibili a fine corsa; curva che accelera nel
> tratto finale. Il §5bis qui sotto resta come storico e come dato di rumore
> di riferimento. **Design corrente = §5ter (v0.2).**

Requisiti (SPECIFICA §5, dec. 82): dopo il filtro, prima del meter di
canale; da pulito a «hard dub overload»; JFET prima, BJT asimmetrico poi;
referenza Sherman Filterbox, raschio che cresce con la risonanza; due
manopole DRIVE (una per sezione HPF, una per LPF) condivise dai canali.

### Topologia: la cella DRIVE del 5-way, riusata identica

```
uscita core (0 dBu nom, picco di risonanza fino a +8…+10 dBu)
  ▼ THAT 218x — guadagno variabile; la law include un pad fisso di −6 dB
  ▼ JFET common-source «nastro» (ginocchio 0,7-1,0 Vp)
  ▼ diff pair PNP «fuzz» (ceiling +2,79 / −4,06 V)
  ▼ recovery invertente + servo DC
  ▼ make-up +6 dB → R serie 33 Ω → return al canale
```

- È la catena già validata in `drive-chain8.cir` (five-way §5.2): nessuna
  topologia nuova, stessi componenti, stesse lezioni.
- **Pad −6 dB e make-up +6 dB**: la cella è nata per un nominale di
  −6 dBu. Nel filtro il nominale è 0 dBu: senza pad i picchi musicali
  toccherebbero il ceiling anche a manopola chiusa. Guadagno netto a
  manopola chiusa: 0 dB.
- 8 celle (4 canali stereo): **+8 THAT 218x** rispetto al conteggio della
  voce 37, + 8 JFET, 16 PNP, ~12 doppi op-amp.
- **Mux del CV**: 2 shaper (uno per manopola, `sistema-shaper.md`) → 2 bus
  CV → per ogni canale uno switch SPDT (classe ADG1434) sceglie il CV
  della sezione attiva (dec. 67) → smoothing 1 ms (dec. 80) → i due VCA
  L/R del canale. In OFF il modulo è in bypass e la cella è fuori percorso.

### Griglia misurata (`sim/filtro/od-chain.cir`) — THD %, 1 kHz

Law di partenza = quella del 5-way (0 / +7 / +9,5 / +12 / +14 / +16 dB a
θ 0 / 50 / 65 / 80 / 90 / 100 %). Livelli riferiti al filtro:

| θ \ segnale | 0 dBu (programma nom) | +8 dBu (picco di risonanza) | +16 dBu (max) |
|---|---|---|---|
| 0 % | 0,10 | 0,26 | 6,9 |
| 50 % | 0,23 | 3,3 | 26 |
| 65 % | 0,33 | 12 | 31 |
| 80 % | 0,53 | 19 | 35 |
| 90 % | 1,1 | 24 | 38 |
| 100 % | 6,9 | 28 | 40 |

Lettura: a manopola chiusa il filtro resta pulito anche col picco di
risonanza (0,26 %). Aprendo, è la RISONANZA a sporcarsi per prima: a
metà corsa il programma è ancora pulito (0,2 %) mentre il picco è già
al 3 %, e a 65 % è al 12 %. È il comportamento della referenza: il
raschio nasce sul fischio del filtro e cresce con lui. Uscita massima
dopo il make-up: +5,6 / −8,1 V di picco.

**Law, range e punto in cui finisce il pulito sono numeri musicali: da
confermare da Filippo (regola 2).** Vale anche qui la domanda della
questione 72 (distorcere senza salire di volume).

### Rumore

Cella drive con I/V del VCA a 10k, come già deciso per il drive 5-way
(dec. 88): −90,1 dBu A-wtd prima del make-up (`drive-noise.cir` caso 4,
conservativo) → −84,1 dopo il make-up. Canale filtro = core ⊕ overdrive:

| Core | Solo core (docs/06 §8) | Con overdrive | Target ≤ −80 |
|---|---|---|---|
| (a) OTA nudo, fc max | −89,9 | **−83,1** | PASS 3,1 dB |
| variante B, fc max | −80,6 | **−79,0** | FAIL 1,0 dB |

Con l'overdrive nel percorso domina lui, non più il core. Sistema con
tutti e 4 i filtri inseriti (core a): −80,0 ⊕ 4 canali filtro =
**−75,3 dBu A-wtd**. Il target ≤ −78 è definito a filtri OFF (docs/06
§2): con i filtri inseriti lo si supera di 2,7 dB. Dato da mettere
davanti a Filippo: condizione d'uso come per le mandate (dec. 95).

### Non fatto

D5 (interazione fine tra risonanza e overdrive col modello OTA reale):
resta dopo la scelta q70. Shaper delle due manopole DRIVE: stessa rete
del drive 5-way (`sim/shaper/shaper-drive.cir`).

## 5ter. Overdrive v0.2 — tosatore in parallelo con tetto fisso (DECISIONE 99, 2026-10-13) [SIMULATO, valori PROVVISORI — griglia da confermare da Filippo]

Sostituisce il §5bis come design corrente.

### Requisiti (decisione 99)

Circuito e carattere diversi dal drive 5-way; rende più drammatici e
violenti i transienti di filtro; meno aggressivo dello Sherman (non deve
assordare né rompere l'impianto); settaggi estremi a fine corsa; curva
che accelera nel tratto finale. Posizione invariata: dopo il core, prima
del return al canale. Due manopole DRIVE (HPF, LPF) condivise dai canali.

### Topologia

```
x = uscita core (0 dBu nom, picco di risonanza +8…+10 dBu)
  ▼ op-amp invertente ×2 (10k/20k): a = −2x ──────────────┐
  ▼ R 2,2k → diodi 2+2 a massa → buffer: wb = −CLIP(2x)   │ 20k
  ▼ ingresso THAT 218x = somma in corrente:               │
      x via 10k + wb via 10k/k (k = 1,171) = −d/10k       │
  ▼ I/V del VCA (10k, invertente) ◄───────────────────────┘
      y = x + m·d      (non invertente, 3 op-amp per cella)
  ▼ R serie 33 Ω → return al canale
```

Schema a blocchi equivalente: y = x + m·(k·CLIP(2x) − x). Polarità
VERIFICATA diritta (`od2-pol-b.cir`: fase 0° a 1 kHz per ogni m).

- **Diverso dal 5-way**: tosatore simmetrico e duro = armoniche dispari
  (terza dominante, seconda assente): il «raschio». NASTRO e GROWL del
  5-way sono asimmetrici e morbidi (seconda armonica).
- **Tetto fisso**: il ramo saturato non può superare 1,56 V di picco.
  A manopola tutta aperta l'uscita resta sotto ~+5,5 dBu qualunque cosa
  entri. È la protezione dell'impianto, senza limitatori automatici.
- **Tetto alzato di 3 dB su richiesta di Filippo (2026-10-13: «alza il
  tetto senza esagerare»)**: la prima stesura (k = 0,829, pari volume al
  nominale) teneva il tetto a +2,5 dBu e il picco di risonanza a +1,6.
  Prove O3/O4 (`od2-explore2/3.cir`): cambiare diodi o guadagno sposta il
  tetto di soli 0,5 dB (a pari volume nominale un tosatore duro lega il
  tetto al livello del programma); un ginocchio morbido lo alza ma
  toglie sporco (risonanza 18 % invece di 31). Scelta: stesso tosatore,
  ramo saturato +3 dB. Costo: a fine corsa anche il programma sale di
  3 dB.
- **Un VCA per cella sul segnale differenza** (8 in tutto, come la v0.1):
  le manopole sono condivise da 4 canali, serve un elemento comandato da
  CV. A manopola chiusa il VCA è chiuso: percorso pulito esatto e rumore
  del ramo overdrive fuori dal canale.
- Tutto DC-coupled; il tosatore simmetrico non genera continua. Niente
  pad −6 / make-up +6 della v0.1.
- Mux del CV e smoothing 1 ms invariati (§5bis).

### Law della manopola (accelera a fine corsa)

m = θ^2,5 → θ 25 / 50 / 65 / 80 / 90 / 100 % = m 0,03 / 0,18 / 0,34 /
0,57 / 0,77 / 1 (VCA −30 / −15 / −9,4 / −4,8 / −2,3 / 0 dB). Metà corsa
usa meno di un quinto dell'effetto: lo spazio per lavorare fine sta
all'inizio, gli estremi nell'ultimo quarto. Shaper: `sistema-shaper.md`.

### Griglia misurata (`sim/filtro/od2-chain.cir`) — THD % · livello d'uscita in dBu

| Manopola | Passaggio piano (−10 dBu) | Programma nominale (0 dBu) | Picco di risonanza (+8 dBu) | Massimo (+16 dBu) |
|---|---|---|---|---|
| 25 % | 0,03 · −9,7 | 0,8 · +0,1 | 0,6 · +7,9 | 0,3 · +15,8 |
| 50 % | 0,16 · −8,2 | 4,5 · +0,6 | 3,8 · +7,4 | 2,1 · +14,8 |
| 65 % | 0,27 · −6,8 | 8,2 · +1,1 | 7,8 · +6,9 | 4,7 · +13,6 |
| 80 % | 0,37 · −5,1 | 13 · +1,8 | 15 · +6,1 | 10 · +11,4 |
| 90 % | 0,43 · −3,9 | 16 · +2,4 | 21 · +5,4 | 18 · +9,1 |
| 100 % | 0,49 · −2,7 | 20 · +3,0 | 31 · +4,6 | 37 · +5,5 |

Lettura: il programma nominale sale poco e solo in fondo alla corsa
(+0,6 dB a metà, +3 dB al massimo). Il picco di risonanza, aprendo la
manopola, si sporca e viene frenato: a fine corsa è un'onda quasi
quadra (31 %) che esce a +4,6 dBu invece di +8, ancora sopra il
programma. I passaggi piani salgono fino a +7 dB: il filtro «riempie». Guadagno ×2 scelto tra ×1 (programma solo
5,5 % a fine corsa: non estremo) e ×4 (programma già al 10 % nei piani).

### Numeri musicali da confermare (regola 2)

1. ~~Il tetto~~ → alzato di 3 dB su richiesta di Filippo (dec. 99 h);
   resta da sentire a orecchio se basta.
2-3. ~~Morso a fine corsa e law~~ → **CONFERMATI da Filippo il
   2026-10-13 come punto di partenza** (dec. 99 i).
   [SUPERATA la griglia dalla dec. 110: col chip reale il fischio arriva a
   −1,5…+2 dBu, non a +8; griglia di riferimento in §5quater.]

### Rumore MISURATO (`sim/filtro/od2-noise.cir`, 2026-10-13)

Blocco overdrive da solo (core escluso), topologia a 3 op-amp
(`od2-noise-b.cir`), VCA col rumore di datasheet a 0 dB tenuto costante
anche da chiuso (prudente):

| Manopola | Guadagno a piccolo segnale | Blocco, dBu A-wtd |
|---|---|---|
| 0 % | 0 dB | −102,6 |
| 50 % | +1,9 dB | −102,1 |
| 80 % | +5,0 dB | −100,7 |
| 100 % | +7,4 dB | −99,0 |

Il blocco in sé è silenzioso (la v0.1 dava −84,1). **Ma la stima fatta
in giornata era ottimista in un punto**: un tosatore amplifica i segnali
piccoli, e il rumore del core è un segnale piccolo. A manopola aperta e
senza musica il soffio del core sale del guadagno a piccolo segnale.
Canale filtro (core a, −89,9) e sistema con 4 filtri inseriti:

| Manopola overdrive | Canale filtro | Sistema, 4 filtri inseriti | Target −78 |
|---|---|---|---|
| 0 % | −89,7 | **−78,5** | PASS 0,5 dB |
| 50 % | −87,9 | −77,8 | FAIL 0,2 dB |
| 100 % | −82,4 | −74,8 | FAIL 3,2 dB |

Con l'overdrive chiuso il sistema rientra nel target anche a filtri
inseriti (era −75,3). Con l'overdrive tutto aperto, e in silenzio, si
torna a −74,8: è il soffio di un overdrive aperto, coperto dal segnale
appena c'è musica. **ACCETTATO da Filippo il 2026-10-13 (decisione
100)**: «il caso in cui il drive è aperto al massimo e senza musica
sarebbe pressoché impossibile».

### Non fatto

**Servo DC**: FATTO il 2026-10-13, vedi «Servo DC» qui sotto.

Rumore del VCA a guadagni diversi da 0 dB (dato di datasheet mancante); D5 FATTO il 2026-10-14 (§5quater); deriva termica dei
diodi (il tetto scende ~2 mV/°C per diodo); interazione col soft
limiter della risonanza.

### Servo DC (2026-10-13) [SIMULATO, valori PROVVISORI]

L'overdrive v0.1 azzerava la continua del core col suo servo; la v0.2 era
nata senza (finding della pulizia, sheet §6). Aggiunto sullo stadio di
somma finale (Xs), un op-amp per cella:

- integratore invertente 1 MΩ / 47 nF (film) che legge l'uscita y,
  op-amp FET classe OPA2134;
- la sua uscita va al piedino + di Xs attraverso un partitore
  100 kΩ / 1 kΩ. Iniettare nel nodo di somma darebbe retroazione
  positiva: il piedino + dà il segno giusto senza un invertitore in più;
- polo 0,050 Hz; corsa di correzione ±193 mV in uscita.

Misure (`sim/filtro/od2-servo-dc.cir`, `od2-servo-noise.cir`):

| Continua in ingresso (offset del core) | Uscita senza servo, m = 0 / 0,57 / 1 | Uscita col servo |
|---|---|---|
| 30 mV | 30 / 53 / 70 mV | 2,0 mV |
| 60 mV | 60 / 106 / 140 mV | 2,0 mV |

- Il residuo di 2,0 mV è l'offset dell'op-amp del servo, messo al massimo
  di datasheet (tipico 0,5 mV). Sotto questo valore il servo non scende.
- Il core dà 4-5 mV di continua (§6): la corsa basta con margine ≥ 16×
  anche a overdrive tutto aperto (limite: 83 mV in ingresso a m = 1).
- Piattezza: −0,0001 dB a 10 Hz, −0,0004 dB a 5 Hz.
- Rumore: invariato. −102,6 / −102,1 / −100,6 / −98,9 dBu A-wtd a
  m = 0 / 0,18 / 0,57 / 1 (senza servo: −102,6 / −102,1 / −100,7 / −99,0).
  I numeri di §9 di `docs/06` restano validi.

Conteggio: 8 celle = 4 doppi op-amp, 8 condensatori film 47 nF.
A banco: il colpo del VCA quando si muove la manopola (il servo recupera
in ~3 s, non lo toglie); una continua del core sposta di poco la
simmetria del tosatore (5 mV contro una soglia di ~1,2 V).

## 5quater. Core (a′) e D5: risonanza + overdrive col chip reale (2026-10-14, DECISIONE 109) [SIMULATO, valori PROVVISORI]

Dati completi e netlist: `sim/filtro/RISULTATI-D5.md`. Qui la sintesi.

### Perché

Col modello reale dell'LM13700 il core (a) di §3 (OTA pilotati dal
segnale pieno) satura sul tetto dei 52 mV (`RISULTATI-ota-real.md` §6).
Misurato (RISULTATI-D5 §1): picco di risonanza sotto ~−12 dBu a
qualunque livello d'ingresso; programma a 0 dBu −23 dB sul taglio;
auto-oscillazione ~3,5 ottave sotto FREQ. La v0.2 non lo vedeva: usava
OTA ideali senza limite di corrente.

### Topologia (a′)

```
summer ─hp─► 2,9k ─┬─► OTA1 ─► 1,1 nF ─► buffer ─bp_b─► 2,9k ─┬─► OTA2 ─► 1,1 nF ─► buffer ─► LP
                   100 Ω                                       100 Ω
                                                              └─► OTA RES ± (Iabc 221 uA·|gres|) ─► summer
bp_b ─► 4,7k ─► 2+2 1N4148 antiparallele ─► summer   (limitatore)
```

- **Partitore 1/30** davanti agli ingressi degli OTA: il tetto di stato
  sul taglio sale a 1,56 V. Rumore e offset dell'OTA riferiti agli stati
  crescono di 30×.
- **C = 33 nF/30 = 1,1 nF** (C0G/PP, matched): la mappa Iabc → fc resta
  quella di §4. Converter, mirror, shaper (dec. 102) invariati.
- **RES**: OTA nel summer come in §5, ingresso dallo stesso partitore,
  Iabc ×30 (221 uA per gres = 1). Due OTA a polarità opposta in
  simulazione per il segno di gres; nel circuito vale la soluzione di §5.
- **Limitatore**: perdita non lineare dal buffer BP (bassa impedenza) al
  summer. Il soft limiter sul nodo BP di §5 prendeva corrente dall'OTA, e
  l'ampiezza cambiava col taglio (+3,5 dB per decade): SUPERATO.

### Misure (fc ~1 kHz, tono sul taglio)

- Piccolo segnale: risposta di un 2 poli Q 0,707 esatta.
- Risonanza sul taglio, uscita/ingresso: a −30 dBu come l'ideale
  (+21 dB a RES 85 %); a −10 dBu +7,2 dB a RES 70 % e +8,5 a 85 %; a
  0 dBu ~+1 dB al massimo. THD del core a 0 dBu 1,5-2 %.
- Auto-oscillazione: −1,8 dBu poco oltre il 90 % di RES, +4,9 dBu a
  fine corsa; nota −1,3 / −5,7 semitoni rispetto al taglio. Livello e
  nota uguali su tre decadi (100 Hz-10 kHz).
- Rumore: −87,4 dBu A-wtd a fc max (`d5a-noise-k30-397u.cir`); sistema
  con 4 filtri inseriti e overdrive chiuso −79,0 (docs/06 §11).
- Offset in continua all'uscita LP: 3,9 mV con Vos tipico; ~40 mV
  stimati col Vos massimo, dentro la corsa del servo dell'overdrive
  (83 mV a m = 1).

### D5: core (a′) + overdrive v0.2 (`d5-chain.cir`)

THD % · uscita dBu rms, manopola DRIVE 0 / 50 / 100 %:

| RES · ingresso | 0 % | 50 % | 100 % |
|---|---|---|---|
| 85 % · −10 dBu | 1,3 · −1,5 | 3,4 · −0,7 | 15,7 · +2,5 |
| 85 % · 0 dBu | 1,8 · +0,7 | 3,5 · +1,1 | 20,0 · +3,1 |
| 0 % · 0 dBu | 0,6 · −3,5 | 2,8 · −2,3 | 11,3 · +1,8 |

- Il fischio arriva all'overdrive a −1,5…+2 dBu, non a +8 come nella
  griglia di §5ter: l'overdrive lo sporca meno (15-20 % invece di 31 %)
  e lo alza invece di frenarlo.
- Il primo sporco sul fischio lo fa il core (1,3-2 %); l'overdrive lo
  allarga. Programma e fischio si sporcano quasi insieme.
- Tetto rispettato: uscita massima misurata +5,4 dBu.

**CONFERMATI da Filippo il 2026-10-14 come punto di partenza (DECISIONE
110, chiude A17)**: questa griglia sostituisce quella di §5ter; picco di
risonanza come misurato sopra (Xone-like); oscillazione ~+5 dBu
(requisito abbassato); calo di nota a fine corsa = carattere.

## 6. Simulazione di fattibilità (2026-09-24, `sim/filtro/`)

### Stato dei modelli — [PROVVISORIO] (regola 3)

- OTA: [SUPERATO 2026-09-28] macromodello comportamentale gm = 19,2·Iabc senza
  limiti propri → SOSTITUITO dal modello transistor-level reale
  `sim/lib/lm13700.inc` (datasheet TI SNOSBW2F: gm 19,4·Iabc ±0,5%, limite
  Iout ≈ Iabc, rumore fisico, Vos parametrico): il comportamento a grande
  segnale (tetto 52 mV, compressione morbida) è ora visibile — risultati in
  `sim/filtro/RISULTATI-ota-real.md` (questione 70). La verifica del carattere
  sonoro resta al prototipo.
- BJT: 2N3904 discreti (modello SPICE standard) → in v0.2 coppia monolitica matched.
- Buffer/summer: macromodello op-amp 1 polo GBW ~1 GHz (ideale audio) → la scelta
  op-amp reale (rumore, offset, GBW minimo) è v0.2.
- PTAT: sorgente comportamentale ∝ T assoluta → assume moltiplicatore ΔVbe reale
  (tecnica standard, da disegnare in v0.2). Q fisso 0,707 (il controllo RES è v0.2).
- File: `feas-svf.cir` (griglia completa), `debug1.cir` / `debug2-conv.cir` (diagnostica
  converter), `res-osc.cir` (risonanza → auto-oscillazione + limiter, v0.2),
  `mirror.cir` (distribuzione Iabc, v0.2). Modelli v0.2: 1N4148 con .model esplicito
  (batch non carica le librerie), perdite d'anello Q_loss≈400 incluse (senza,
  l'ampiezza oscillante resta quella iniziale invece dell'equilibrio col limiter).

### Metodo

Griglia 78 punti: 13 valori di CV (ottave 10,6 Hz → 37 kHz) × temperatura 0/27/50 °C
× PTAT on/off. Misure: fc = attraversamento −3 dB di |LP| (esatto per Q = 0,707);
Q_eff dal picco di |BP|. Legge target: fc(vc) = 10,6·2^(vc/0,4247) Hz.

### Risultati

78/78 step validi. Q_eff = 0,707 esatta (±0,001) su tutta la griglia: con i buffer
di stato il loop SVF è ideale da 10 Hz a 37 kHz.

fc misurata (PTAT attivo, 27 °C) al variare del CV 0-5 V:

| CV [V] | 0 | 0,42 | 0,85 | 1,27 | 1,70 | 2,12 | 2,55 | 2,97 | 3,40 | 3,82 | 4,25 | 4,67 | 5,00 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fc [Hz] | 10 | 20 | 41 | 81 | 162 | 324 | 647 | 1291 | 2573 | 5115 | 10134 | 19957 | 33500 |

- Spaziatura a ottave esatta nella parte centrale (rapporti 1,99-2,00 per step).
- Errore contro la legge esponenziale ideale (27 °C): −3,6% a 10 Hz, −4,4% a centro
  corsa, −9,4% a 33,5 kHz. Curva liscia e monotona → si assorbe con la calibrazione
  dello shaper (dec. 70: punti di piega regolabili a banco) + trim degli endpoint.
- Dopo calibrazione endpoint (10 Hz e 35 kHz esatti agli estremi): residuo stimato
  ±2-3% su tutta la corsa → dentro la tolleranza ±5-10% della decisione 74.
- Temperatura 0→50 °C a pari CV: deriva ≤2,4% (PTAT attivo). Senza PTAT: −57% a 0 °C,
  +73% a 50 °C → la compensazione PTAT è indispensabile, e funziona.

### Verdetto

**Fattibilità DIMOSTRATA**: il converter esponenziale tempcompensato + core SVF OTA
copre 10 Hz–35 kHz con law e stabilità termica entro la tolleranza della decisione 74,
con procedura di calibrazione a banco. La condizione della questione 51 (e quindi
della 49) è soddisfatta. Resta per la v0.2: mirror e distribuzione a 8 core con trim,
controllo RES, law shaper concreto, modello OTA reale, prototipo su millefori.

### Lezioni registrate (oneste, per il prototipo)

1. Il diff pair single-ended comprime le ottave alte (limite di coda) → NO.
2. Collettore del ramo exp alimentato dal nodo di riferimento → ricompressione → NO:
   Vce fisso da rail dedicato.
3. I resistori del summer caricano i nodi di stato OTA → buffer obbligatori.
4. Convenzione LTspice: I(Vxxx) uscente dal nodo + → gm = −19,2·I(Vabc).

## 7. BOM di massima v0.1 [molto PROVVISORIA — regola 3]

| Voce | Qtà | Note |
|---|---|---|
| LM13700 (dual OTA) | 20 | 8 core × (4 integratori + 1 risonanza) = 5 OTA/core [PROVVISORIO] |
| Quad op-amp low-noise (classe OPA1654) | ~14 | summer + buffer di stato (48 sez.) + servo mirror + shaper |
| 1N4148 (limiter risonanza) | 48 | 6 per core, stringhe 3S antiparallele |
| Trimmer (freq per core, endpoint shaper, RES) | ~30 | calibrazione a banco |
| Coppia BJT matched | 2 (+ selezione) | MAT12/DMMT3904W [reperibilità da verificare] |
| Switch analogici (mux modo, mux drive CV) | ~6 | ADG14xx [PROVVISORIO] |
| C integratori C0G/PP 33 nF 2% matched | 32 | tracking L/R e tra sezioni |
| R 0,1% (summer/Q, scala PTAT) + trimmer per core | ~16 | tracking ≤2% (voce 51) |
| Rete law shaper (diodi/R) + riferimento PTAT | 2 sezioni | dec. 70, punti di piega a banco |
| Stadio drive JFET + recovery (per sezione) | 2 | questioni 12/61 |
| Stima costo | ~100-140 € | esclusi pannello/connettori/PSU |

## 8. Questioni toccate da questa v0.1

- **51** (tracking/converter): CHIUSA la parte elettrica — converter dimostrato (v0.1)
  + distribuzione a mirror bufferizzati simulata (v0.2: tracking tra rami ≤1,6%,
  PASS ≤2%; mirror semplice scartato). Restano: simmetria termica del PCB, procedura
  di calibrazione per core al banco, conferma a 8 core fisici al prototipo.
- **49** (HPF min 10 Hz): la condizione "se la simulazione conferma il converter" è
  soddisfatta → CHIUSA come assorbita dalla decisione 74 (full-range 10 Hz–35 kHz).
- **11** (SVF/risonanza): RISPOSTA in v0.2 — risonanza via iniezione OTA + limiter
  3S morbido; oscillazione +7,3…+8,6 dBu misurata (target +6…+10 ✓), segue il cutoff.
  Resta la ratifica a ORECCHIO del carattere (riferimento Sherman) al prototipo,
  con le referenze di Filippo (questione 61). Law RES θ→gm_res [PROVVISORIA]:
  0-90% corsa = Q 0,707→∞, 90-100% = oscillazione (margine −0,75…−1,0 nominale,
  trim a banco). **DATO v0.3 (2026-09-28, RISULTATI-ota-real §3/§6)**: col
  modello reale il core nudo comprime morbido già a 0 dBu (~1% THD, gain −3,5×
  a +10 dBu interni): il "carattere OTA" esiste ed è misurato — opzione (a)
  della questione 70, da ascoltare contro l'opzione pulita (c) con 61/64.
- **12** (overdrive): requisiti recepiti; topologia dopo le referenze (questione 61).
- NUOVA da §2: **conferma interpretazione mux CV** — un solo percorso attivo per canale
  (HPF oppure LPF) vs sezioni sempre in serie. La dec. 67 dice "tutti i canali nella
  stessa modalità seguono gli stessi knob" e lo switch è a 3 vie: l'interpretazione
  single-path è la lettura naturale, ma va confermata [APERTO-F].
- NUOVA da §3: **allineamento 4 poli** (Butterworth vs Bessel vs LR) = carattere del
  filtro: da proporre a Filippo con curve e ascolti [APERTO-F].

## 9. Prossimi passi (v0.3)

FATTI in v0.2: RES/oscillazione/limiter (11), shaper law + pre-distorsione (dec. 70),
distribuzione mirror + tracking (51).

1. Overdrive JFET/BJT dopo le referenze di Filippo (questioni 12/61).
2. [FATTO 2026-09-28 — ramp; mux dopo 63] Generatore di ramp BBM VALIDATO
   (`sim/filtro/bbm-ramp.cir`, RISULTATI §4): τ 1 ms = click −8,4 dB vs
   brusco (gesto ~2 ms trasparente), 5 ms ≈ baseline (gesto ~10 ms "soft
   mute"); gap BBM 50 µs muto (floor −100 dB). FAMIGLIA UNICA 1 ms con gate
   5-way e reroute FX → ratificata (decisione 80). Circuito = generatore ramp del
   gate 5-way (gate-ramp validato; dal 2026-09-30 il kill è a switch per dec. 88 — il circuito resta riferimento per gli altri usi della famiglia). Il mux di modo (HPF/OFF/LPF) resta
   BLOCCATO su 63 (single-path vs serie).
3. [FATTO 2026-09-28] Modello LM13700 reale (`sim/lib/lm13700.inc`,
   RISULTATI §1-§3): offset (stati DC 4-5 mV bounded su tutta la sweep,
   nessun trim), rumore a Iabc 114 n…397 µ (−134,8…−107,8 dBu integrati — INVALIDATI quirk INTEG → rerun 71A: −126,0/−103,7/−90,3 dBu unwt ideali, die reale −84…−76 a fc max, dec. 89:
   PASS ≥17,8 dB anche con die 5× peggiore), swing/THD → FINDING: tetto di
   stato 52 mV a f0 → core nudo = compressore morbido ~1% a 0 dBu (opzione
   carattere) ma collasso a +10 dBu; scaling+make-up = trade-off perdente
   (rumore ×N) → **questione 70: topologia core da decidere PRIMA del
   prototipo** — PoC VALIDATO 2026-09-28 (`sim/five-way/RISULTATI-cell-clean.md`):
   lo schizzo OTA-scaler è bocciato (muro del rumore); varianti pulite validate
   (c-B) VCA 218x e (c-A) JFET VCR; per il filtro decide l'ascolto (a) vs (c-B). THD oscillatore/limiter: resta ascolto (61/64).
4. Prototipo su millefori di UN core + converter + RES — SBLOCCATO PARZIALE
   (questione 70: PoC topologie pulite VALIDATO, `sim/five-way/RISULTATI-cell-clean.md`):
   il prototipo confronta a ORECCHIO il core OTA nudo (a — design v0.2
   invariato, costo zero, ~1% THD morbido = carattere Sherman) contro la
   variante pulita (c-B) VCA 218x ×2 (validata in sim: law esatta, Q
   invariante; +16 chip); (c-A) JFET solo come fallback (7,6 ottave < 11,8
   senza C-switching). Taratura law, verifica tracking 8 core reali, ascolto
   risonanza/oscillazione e carattere (61/63/64/70 a orecchio).
5. Layout termico PCB (simmetria converter/mirror/core) e procedura di
   calibrazione. Invariato da 70 (converter/mirror validi con qualsiasi
   core a gm ∝ Iabc).
6. [PARZIALE 2026-09-28] Rumore: CORE nudo −107,8…−134,8 dBu (PASS,
   RISULTATI §3); il modulo completo (pad/make-up/drive esclusi) segue la
   topologia della questione 70 (variante scalata: FAIL −82 dBu).
