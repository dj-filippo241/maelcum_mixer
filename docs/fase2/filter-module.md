# FASE 2 — Modulo FILTRO: design v0.2 + v0.3-WIP (2026-09-28)

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
| Legge knob | musicale ~90% centrale, accelerazione ultimi ~5%; estremo di taglio = silenzio totale | dec. 70/74 |
| Risonanza | 0-70% normale; 70-90% aggressiva; 90-100% auto-oscillazione che segue il cutoff, +6…+10 dBu con soft limiting (carattere Sherman) | SPECIFICA §5 |
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
  - Legge target (θ = rotazione knob 0→1): musicale = esponenziale nei ~90% centrali
    con f(0,05) = 14 Hz e f(0,95) = 25 kHz (10,8 ottave); ultimi 5% per lato con
    accelerazione ~4× agli estremi veri (10 Hz / 35 kHz = silenzio per superamento
    della banda). Tabella θ→f = riferimento per taper e per il prototipo M4L.
  - **Pre-distorsione**: l'errore residuo misurato del converter (§6: −3,6% → −9,4%,
    curva liscia monotona) si compensa nello shaper: vc* = vc_ideale − e(vc)/2,355
    (correzione ≤ 40 mV agli estremi) — la law risultante è esponenziale pura entro
    ~±1%.
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
- **Modo OFF**: bypass secco del core (return = send) con break-before-make + ramp
  1 ms generata nel modulo (SPECIFICA §4, decisione 80). Switch analogici famiglia ADG14xx
  [PROVVISORIO, stessi candidati dell'assign FX — metodo decisione 80].
- Livelli interni: send 0 dBu nom/+16 max → buffer in → core (picco risonanza
  +10 dBu sopra il livello, sheet) → drive → recovery → return. Il dominio ±18 V
  del canale resta valido su tutto il modulo (sheet §2).

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
