# FASE 2 — Modulo 5-WAY (dub preamp): design v0.2-WIP (2026-09-28)

> **CODA BETA-3 CELLE (2026-09-28, `sim/filtro/RISULTATI-ota-real.md` §5)**:
> celle parametriche riesaminate col LM13700 REALE (`sim/lib/lm13700.inc`) —
> piccolo segnale CONFERMATO (detent piatto ±0,0001 dB, boost ±0,02 dB, notch
> vero −67…−78 dB con f0 +1% assorbita dal trim position), rumore cella
> −119,7 dBu (dentro il budget −108,4 di §8.4); **FINDING BLOCCANTE**: il
> tetto di stato degli integratori OTA (52 mV a f0, strutturale) rende la
> cella nuda inutilizzabile ai livelli di progetto (a −6 dBu: gain 1,1-1,3
> contro 5,62, THD 3-6%); scaling+make-up rompe il rumore → **questione 70:
> PoC VALIDATO 2026-09-28 (`sim/five-way/RISULTATI-cell-clean.md`)** —
> raccomandata (c-A) JFET VCR bootstrappato (THD 0,004-0,11%, rumore
> −121,7 dBu, griglia v0.2 confermata, costo ~10-20 €); alternativa (c-B)
> VCA 218x ×2 (law esatta, livelli pieni, +20 chip). Rilascio celle v0.2.1
> su (c-A): §8.7.
>
> **v0.2-WIP (2026-09-27)**: (1) kill bank ALLINEATA IN FASE — soluzione
> esatta dimostrata (math + LTspice): somma piatta −0,0002…−0,008 dB su
> 5 Hz–60 kHz senza kill, all-kill = silenzio assoluto invariato (§3.1,
> §8.2); il finding v0.1 (buchi −3…−5 dB) è chiuso. (2) CELLE PARAMETRICHE +
> CASCATA 5 in serie VALIDATE: detent ±0,005 dB su 10 Hz–40 kHz, boost ±0,005
> dB sui target +9/+12/+15, notch −58…−81 dB, Q = comandata, position via gm
> esatta su 2,6 ottave (§4.1, §8.3); converter di position specificato per
> banda (§4.1). (3) RUMORE del percorso completo SIMULATO: −108,4 dBu contro
> target −90 (sheet §3), margine 18,4 dB (§8.4). (4) GATE VCA + RAMP 1 ms
> VALIDATO col macromodello THAT 218x condiviso (`sim/lib/that2181.inc`):
> click −8,4 dB vs brusco, floor −100 dB (§8.5). CORREZIONE trasversale da
> datasheet: 2180/2181 sono SINGLE channel (10 chip per i gate, non 5) —
> voce 37 aggiornata. Resta per la v0.2 completa: drive (dopo questione 61)
> e modelli reali (beta-3).
>
> **v0.1 (2026-09-25)**: primo design del 5-way performance EQ/dub preamp.
> Copre architettura, matematica del filter bank (questione 8: proposta LR4
> SIMULATA), topologia dell'EQ creativo (questione 9: architettura, law di
> position da decidere), interfaccia drive (questione 10: in attesa referenze
> di Filippo, questione 61). NON congela valori (regola 3). Fase 2: dettaglio
> circuitale completo dopo che la fase 1 ha insegnato (regola 5) — questo
> documento è architettura + funzioni di trasferimento + fattibilità.
> Fonti: SPECIFICA §6, decisioni 24/65/66/73, questioni 61 (referenze drive) e 67 (frequenze), status doc §14-18
> (`docs/export-chatgpt/documento-senza-titolo.txt`), gain-staging sheet.

## 1. Requisiti (BLOCCATO salvo dove indicato)

- Posizione: DJ BUS → 5-WAY → MASTER SUM; FX/mic/generic la bypassano.
- NON è il crossover acustico: quello lo fa il DSP esterno; il 5-way è uno
  STRUMENTO performance ispirato ai preamp dub/soundsystem.
- Riferimento interno −6 dB (pad in / makeup out, decisione 73).
- KILL: 5 sezioni = 5 vie (SUB ~10-90, KICK ~90-350, MID ~350-1,2k,
  HIGH ~1,2-3,5k, SUPER ~3,5-20k [PROVVISORIO dec. 66 — conferma a orecchio
  = questione 67]); 24 dB/ott; overlap deliberato senza buchi; banca
  complementare (somma piatta); kill PRIMA dell'EQ creativo (il boost non
  ripristina materiale killato); kill switch per via (altoparlanti fisici).
- EQ CREATIVO: gain/position/width per banda; gain −∞/0/+15 (EQ1-3), +12
  (EQ4), +9 (EQ5); position: 20-120 / 80-400 / 250-1,5k / 800-5k / 3-20 kHz
  [PROVVISORIO]; width: narrow ~Q3 / medium ~Q1 / broad ~Q0,5; position
  sposta il centro senza stravolgere gain/Q. Casi d'uso (corpus §17):
  broad+gain modesto = tonal shaping; narrow+gain alto = dub hit preciso;
  broad+gain alto = colorazione aggressiva.
- DRIVE: dopo la somma EQ, prima del meter; full CCW = 0 dB pulito, solo gain
  positivo; ~50% = +7 dB pulito; >50% saturazione progressiva che interagisce
  con gain di banda e overdrive filtro; JFET prima / BJT asimmetrico poi.
  Riferimenti operativi (corpus §18): normale −6…0 dBu, hot +10, estremo +18,
  clean headroom ≥+24 dove pratico (sheet: qui il dominio ±18 dà +23, ok).
- METER: dopo drive, prima del master sum (ballistica anche a 10 Hz, dec. 65).
- Controlli: fader = slider, resto = pot (principio bloccato); layout per via
  slider vs rotativi = questione 24 (aperta, pannello = design di Filippo).

## 2. Architettura

```
DJ BUS L/R (0 dBu nom, +16 worst)
  │
  ▼ PAD −6 dB (dec. 73) → buffer
  │
  ▼ KILL BANK (per lato): LR4 5 vie, gate VCA per via + kill switch
  │   SUB ──[gate K1]──┐
  │   KICK ─[gate K2]──┤
  │   MID ──[gate K3]──┤   (banca complementare: somma piatta §3)
  │   HIGH ─[gate K4]──┤
  │   SUPER─[gate K5]──┘
  ▼ EQ CREATIVO: 5 celle parametriche SVF in serie (gain/position/width §4)
  │   (le 5 bande EQ NON sono le 5 vie: ogni cella spazza il suo range)
  ▼ SOMMA → DRIVE JFET (law dec. 24, §5) → METER pickup (§5) →
  ▼ MAKE-UP +6 dB + trim → MASTER SUM (backplane)
```

Ordine bloccato: kill bank → EQ creativo → drive → meter ("killed material
cannot be restored" — corpus §16; "boost non ripristina materiale killato"
— SPECIFICA §6).

## 3. Kill bank — matematica complementare (questione 8: RISPOSTA v0.2)

**Scelta [PROVVISORIA — frequenze = questione 67]**: crossover Linkwitz-Riley
4° ordine ai 4 punti (90/350/1,2k/3,5 kHz): ogni edge = due Butterworth 2°
ordine (Q 0,707) in cascata. Proprietà che risponde ai requisiti:
- 24 dB/ott ✓ (4 poli per edge);
- "overlap deliberato senza buchi" = la sovrapposizione −6 dB delle LR ✓;
- bande: SUB = LP4(90) (passa fino a DC/10 Hz: nessun accoppiamento AC,
  requisito infrasub dec. 65 ✓); KICK = HP4(90)·LP4(350); MID = HP4(350)·
  LP4(1,2k); HIGH = HP4(1,2k)·LP4(3,5k); SUPER = HP4(3,5k);
- **somma in tensione PIATTA**: la proprietà LR a 2 vie NON basta a 5 vie —
  il finding v0.1 (§8.1) ha misurato buchi −3…−5 dB dalla fase non allineata.
  La v0.2 risolve con la banca allineata in fase (§3.1): |Σ| = 1 ESATTA,
  validata in simulazione (§8.2). La somma esce invertita (fase comune):
  il make-up ripristina la polarità assoluta (dec. 73, §2).

### 3.1 v0.2 — Banca allineata in fase (somma piatta esatta)

Identità LR4: `LP4(f) + HP4(f) = A2(f)` — allpass del 2° ordine a Q 0,707
(modulo 1 esatto, fase 0→−360°). La somma telescopica a 5 vie è esatta se
ogni banda arriva al summer con la stessa fase di riferimento = prodotto dei
4 allpass: ogni banda passa gli A2 dei crossover SOPRA la sua banda passante.

| Banda | Percorso | Allpass di compensazione | Polarità netta |
|---|---|---|---|
| SUB | LP4(90) dall'ingresso | A2(350) · A2(1,2k) · A2(3,5k) | − (3 sezioni) |
| KICK | HP4(90) → LP4(350) | A2(1,2k) · A2(3,5k) | + |
| MID | HP4(90) → HP4(350) → LP4(1,2k) | A2(3,5k) | − |
| HIGH | … → HP4(1,2k) → LP4(3,5k) | — | + |
| SUPER | … → HP4(3,5k) (fine spina) | — | + |

Somma = A2(90)·A2(350)·A2(1,2k)·A2(3,5k) → modulo 1 a ogni frequenza
(dimostrato: `sim/five-way/align_math.py`, errore 1,1e-15; validato in
LTspice: §8.2). Struttura a **spina HP condivisa**: il segnale attraversa
una cascata HP4(90) → HP4(350) → HP4(1,2k) → HP4(3,5k); ogni banda è una
presa sulla spina seguita dal suo LP4. Le HP4 non sono duplicate per banda:
la spina costa quanto la banca v0.1 (16 sezioni SK per lato).

Sezione allpass AP2 (2 op-amp): MFB bandpass invertente Q 0,707 + summer
−(1×Vin + 2×Vbp) = −A2(s) esatto. Vincoli: C1 = 2C (n1→n−), C2 = C (n1→out),
R1 = 1/(√2·ω0·C) (in→n1), R2 = 2·R1 (n1→gnd), Rf = 1,5·R1 (n−→out); summer
con Rf/Ra = 1 e Rf/Rb = 2 (coppie 0,1%). Il segno − di ogni sezione sparisce
nella polarità comune di banca (make-up, dec. 73); le bande con numero
DISPARI di allpass (SUB, MID) escono invertite: il gate corregge il segno.
MFB è appropriato qui (350 Hz–3,5 kHz, Q fisso): lo scarto v0.1 dell'MFB
riguardava gli edge LP sotto 100 Hz (rumore gain/2), non i BP.

Conteggio silicon per lato: 16 sezioni SK (spina 8 + LP 8) + 6 AP2 × 2
op-amp = 28 sezioni ≈ 7 quad/lato → **14 quad/modulo** per la banca (era 8
in v0.1). Variante "lite" (3 AP2/lato — 1 allpass per banda, il più vicino):
worst −0,125 dB invece di −0,008 dB, risparmio 3 quad/modulo [APERTO — se il
costo conta; raccomandazione ingegneria: banca completa, è il cuore del
modulo e 0,125 dB è già al limite del requisito ±0,1 dB].

Topologia per edge: Sallen-Key biquad unity-gain (1 op-amp per sezione 2
poli; R da formula con C fissi per decade, 1% + trimmer di allineamento a
banco: la piattezza vive sul matching degli 8 edge e delle 6 sezioni AP2).
Se un trimmer sposta un edge di ±10% senza muovere l'allpass corrispondente,
l'errore di somma resta ≈0,02 dB (calcolo in §8.2): i trim NON devono essere
accoppiati meccanicamente.

**Group delay della somma (dato nuovo v0.2)**: la somma allineata è un
allpass dell'8° ordine: τ ≈ 6,9 ms @10 Hz, picco 7,9 ms @58 Hz, 2,2 ms @350,
0,66 ms @1,2k, 0,19 ms @3,5k, 0,02 ms @10 kHz. Non è un costo nuovo
dell'allineamento: la banca v0.1 (non allineata) aveva già τ ≈ 7,3 ms di
picco — è il prezzo dei 24 dB/ott. La differenza v0.1→v0.2 è +0,6 ms al
picco. In ascolto: l'energia sotto ~100 Hz arriva ~7 ms dopo il medio-alto,
dentro la finestra di fusione (~20 ms) — comportamento normale di un
crossover ripido; il DSP acustico a valle fa il suo allineamento. Comunque
dato da confermare a orecchio (questione 67, ascolto M4L).

**Gate di kill**: 1 VCA per via per lato (THAT 2180/2181 — SINGLE channel:
il "dual" del nome sono i porti di controllo EC+/EC−, verifica datasheet
2026-09-27; famiglia unica — voce 37): 5×2 = **10 chip singoli**. Kill
switch fisico (5, uno per via di altoparlanti) + slider/mute: il gate chiude
con ramp ~1 ms (famiglia voce 55) — VALIDATA in simulazione (§8.5): fade
esponenziale senza kink, transiente HF −8,4 dB vs interruzione brusca.
Kill = g→0: **silenzio della via** (gate, non sottrazione: nessuna
cancellazione di fase — a differenza dell'EQ di canale che è scultoreo; via
killata = l'altoparlante tace; EQ creativo = gesto sul materiale vivo).
Nel reale il floor non è −inf ma il feedthrough del VCA (~−90…−100 dB dopo
trim, datasheet): comunque silenzio pratico, sotto il rumore del modulo.

**Verifica simulata** (`sim/five-way/bank-lr4.cir`, gate ideali): [RISULTATI §8]

## 4. EQ creativo — 5 celle parametriche (questione 9: architettura)

Ogni banda = cella parametrica a SVF, riuso dei due building block già
dimostrati nel progetto:
- **Core**: la cella a campana sottrattiva dell'EQ serie v0.3
  (`G = −(1 − b·BP)`, notch esatto al centro, detent piatto per costruzione,
  boost = 1+b) con BP da SVF OTA;
- **Position**: ω0 dello SVF via gm = 19,2·Iabc — stessa tecnica del modulo
  filtro; range per banda ~2,3-2,7 ottave.
- **Width**: Q della cella via damping nel summer: switch 3 posizioni
  (narrow Q3 / medium Q1 / broad Q0,5) su 3 resistori matched 0,1% —
  ripetibile, senza pot che interagiscono (SPEC chiede 3 comportamenti
  discreti, non continui).
- **Gain**: b dal pot con law dB (−∞/0/+max): b = +1 → notch (il −∞ del
  requirement = notch profondo al centro, larghezza da Q — la rimozione
  TOTALE di una regione è lavoro della kill bank a monte, coerente con la
  filosofia a due stadi); b negativo → boost: +15 dB → b = −4,62
  (1+|b| = 5,62); +12 → b = −3,0; +9 → b = −1,82. Summer con rapporto
  Rf/Rb fino a 4,62 [PROVVISORIO].
- **Position senza stravolgere gain/Q**: proprietà naturale dello SVF
  (ω0 = gm/C indipendente dal damping) ✓ requisito esplicito del corpus.

Converter di position: due opzioni [APERTO — ascolto M4L, come questione 67]:
- (A) Iabc LINEARE nel pot: semplice (1 generatore V-I per banda), ma la
  frequenza risulta lineare nella corsa (bassi compressi a inizio corsa);
- (B) converter esponenziale (tecnologia del modulo filtro, mirror inclusi):
  law a ottave uniforme — feel coerente coi knob del filtro. Raccomandazione:
  (B), costo ~5 converter + mirror.

### 4.1 v0.2 — Circuito della cella VALIDATO (`sim/five-way/param-cell.cir`)

Circuito completo per cella (per lato):
1. **Core SVF**: summer invertente (Vin 10k, feedback LP 10k, damping da
   bp_b via Rq, Rf 10k) + 2 integratori OTA (gm = 19,2·Iabc, LM13700) con
   C di banda + **buffer di stato obbligatori** (lezione filtro v0.1):
   f0 = 19,2·Iabc/(2π·C);
2. **Q (width)**: 1/Q = Rf/Rq — switch 3 posizioni su Rq = Q·10k
   (30k/10k/5k per Q3/Q1/Q0,5, 0,1%);
3. **Gain (b)**: pot collegato tra +bp_b e −bp_b (buffer + invertitore):
   il pot È il moltiplicatore, nel dominio del segnale — nessuna CV nella
   catena gain (niente rumore di controllo, niente law-Shaper attivo).
   Wiper → R_b = Q·10k/4,62 (SECONDO deck dello stesso switch width, 0,1%)
   → summer d'uscita (10k/10k): H = −(1 − b·BP_norm) con b = ±4,62 a fine
   corsa. Detent = centro fisico: b = 0 → cella = invertitore puro, piatto
   per costruzione (misurato: ±0,0001 dB);
4. **Law/taper** [PROVVISORIO — conferma a orecchio in M4L]: eredita la
   famiglia eq-serie §10 — CW: 0→+max dB lineare-in-dB su mezza corsa;
   CCW: 0→notch con accelerazione negli ultimi 5% (notch a fine corsa).
   L'asimmetria di b (+1 per il notch vs −4,62 per +15 dB) sta nel taper
   custom del pot, NON in gain diversi sui due lati. Pot doppi stereo-
   linked tracking ≤1% = stessa classe componenti di eq-serie (voci 37/40);
5. **Position (opzione B, specificata)**: converter master esponenziale
   (design filtro v0.2, law dec. 70) → mirror BUFFERIZZATI per banda e lato
   (tracking ≤1,6% dimostrato in filtro v0.2 → disallineamento L/R ≤27 cent,
   trim a banco). C per banda [PROVVISORIO] scelti per tenere Iabc nella
   finestra 2-31 µA: EQ1 330n (20-120 Hz), EQ2 100n (80-400), EQ3 33n
   (250-1,5k), EQ4 10n (800-5k), EQ5 4,7n (3-20k); rapporto mirror
   0,05-0,6 dalla finestra master 40-240 µA.

Conteggio reale per cella: 1 LM13700 + **5 sezioni op-amp** (summer, buffer
BP, buffer LP, invertitore −bp_b, summer d'uscita) — la stima v0.1 (2-3)
dimenticava buffer di stato e invertitore. Per lato: 5 celle = 25 sezioni =
6,25 quad + 5 LM13700.

Livelli: picco bp_b = Q × riferimento interno (−6 dBu nom, dec. 73); boost
worst +15 dB su programma +10 dBu interni → territorio drive (§6:
saturazione intenzionale, invariato). Rumore: il pot nel percorso segnale
tra due nodi low-Z aggiunge termica + rumore di wiper — da quantificare
nell'item rumore (§10.5).

Silicon totale modulo (v0.2): banca 14 quad (§3.1) + EQ 12,5 quad +
gate/buffer/make-up ≈ **~28-30 quad + 10 LM13700 + 12 THAT 218x singoli**
(10 gate + 2 drive) [PROVVISORIO, BOM §7].

## 5. Drive e meter (questione 10 — v0.1 = interfaccia, design dopo referenze 61)

- **Struttura in due stadi** che realizza la law bloccata senza compressione:
  stadio 1 = gain pulito variabile 0…+7 dB (CCW→50%, law dB lineare via
  CV); stadio 2 = saturatore morbido a soglia fissa (JFET soft-sat, poi
  BJT asimmetrico — corpus §18): oltre il 50% il segnale entra progressivamente
  nella saturazione. L'"interazione con gain di banda e overdrive filtro"
  è automatica: le bande spinte e il filtro saturo arrivano già caldi qui.
  Carattere = sound design: **aspetta le referenze di Filippo (questione 61)**;
  v0.2 con modelli JFET reali + spettro armonico per candidato.
- Interfaccia elettrica: dominio ±18 V; ingresso tollera +18 dBu clean
  (stadio 1 a JFET, headroom); uscita recovery low-Z 20-50 Ω, clean +23 dBu
  (sheet: il +24 vero vive solo al master); nessun makeup compression (SPEC).
- **Meter**: pickup post-drive; detector condiviso col design di canale
  (CDJ §7 item 6 — peak detector SIMULATO 2026-09-27: `sim/meter/RISULTATI-peak-det.md`,
  droop 10 Hz e latch clip quantificati, dati alla questione 19): ballistica a 10 Hz
  (dec. 65: no sagging), clip latch 300-500 ms, segmenti = design modulo
  metering (questione 19/54).

## 6. Headroom e livelli (sheet §2, dec. 73)

- Pad −6 dB in ingresso: nominale interno −6 dBu; worst programma +16 dBu
  → interno +10 dBu.
- Boost creativo massimo +15 dB su una banda: worst teorico +25 dBu interni
  = oltre il dominio (+23): **saturazione intenzionale del drive/stadi** —
  coerente con la filosofia "estremo = colore voluto" (voce 31, quest 61):
  il 5-way spinto È il suono dub, non un guasto. Con programma reale
  (crest ≥10 dB) non accade quasi mai.
- Regola K4 adattata: level_in × gain_creativo ≤ +23 dBu per uso clean;
  oltre = territorio drive.

## 7. BOM di massima v0.1 [molto PROVVISORIA — regola 3]

| Voce | Qtà | Note |
|---|---|---|
| Quad op-amp low-noise (classe OPA1654/1612) | ~28-30 | banca 14 (v0.2 allineata in fase: 16 SK + 12 allpass), EQ 12,5 (5 sezioni/cella × 10, §4.1), gate/buffer/make-up |
| LM13700 (dual OTA) | 10 | celle parametriche (position gm) |
| THAT 2180/2181 (SINGLE VCA — datasheet 2026-09-27) | 10 | gate di kill (1 per via per lato); 2162 dual scartato: ±16 V max e THD 0,05% |
| THAT 2180/2181 o JFET matched | 2 | gain drive (stadio 1, 1 per lato) |
| JFET saturazione (coppia matched) | 2-4 | stadio 2 drive (post-61) |
| Converter expo position + mirror | 5 sezioni | opzione (B) §4 |
| R 0,1% / C0G-PP / trimmer allineamento | — | banca: 8 edge + 6 sezioni allpass per lato |
| Stima costo | ~220-300 € | il modulo più siliconato del mixer |

## 8. Simulazioni (`sim/five-way/`)

### 8.1 Bank LR4 + gate di kill (`sim/five-way/bank-lr4.cir`, 7 casi × 12 freq)

**Funzione KILL: VALIDATA.** Ogni via killata scende nella sua banda con le
code LR4 (KILL SUB: −76 dB @10 Hz; KILL KICK: −24 dB @200; KILL MID: −21
@700; KILL HIGH: −15 @2,5k; KILL SUPER: −51 @15k, −68 @25k) e le altre vie
restano intatte; ALL-KILL = −inf (silenzio assoluto by design: il gate VCA
non ha i limiti di fase delle celle sottrattive — a differenza dell'EQ di
canale, qui il kill È muto).

**FINDING — la somma piatta richiede allineamento di fase (questione 8,
parzialmente aperta).** Due bug trovati e corretti durante la verifica
(diagnostica di debug: `sim/five-way/bank-debug.cir`, run STORICO con la Q
pre-fix — il run di riferimento è `bank-lr4.cir`):
1. SK HP con R invertiti → Q 0,354 invece di 0,707 (1/Q = ω0·R_fb·(C1+C2):
   R_fb deve essere META di R_gnd per Q 0,707). Bug ereditato da v0.2 —
   corretta anche la cella HIGH di eq-serie (numeri aggiornati là).
2. La somma telescopica LR4 a N vie NON è esattamente piatta con sole
   bande in fase: la proprietà |LP4+HP4| = 1 vale per la coppia a 2 vie;
   in cascata a 5 vie le fasi accumulate tra crossover vicini (spaziature
   1,55-1,96 ottave alle frequenze PROVVISORIE) producono buchi di somma
   −3…−5 dB (misurato: −4,8 dB @1,2 kHz). La polarità alterna peggiora
   (−8,9 @90 Hz).

Soluzione v0.2 = §3.1 (banca allineata in fase), realizzata e VALIDATA in
§8.2. Alternativa musicale ancora aperta: allargare le spaziature (frequenze
PROVVISORIE — dec. 66, conferma questione 67); lo schema di allineamento
funziona a qualsiasi set di frequenze, quindi la scelta di 67 non è vincolata.

### 8.2 v0.2 — Banca allineata in fase (`bank-aligned.cir`, `align_math.py`)

**SOMMA PIATTA ESATTA: VALIDATA.** Due verifiche indipendenti che combaciano
al centesimo di dB:
- math (`align_math.py`, stdlib): Σ bande compensate = A2(f1)A2(f2)A2(f3)A2(f4)
  con errore 1,1e-15; riproduce anche i buchi v0.1 (−4,73 dB @1,27 kHz stessa
  polarità; −8,92 @87 Hz polarità alterna) = doppia conferma del finding §8.1;
- LTspice (`bank-aligned.cir`, circuito completo: spina HP + LP + 6 AP2 reali
  MFB/summer + gate + summer, 7 casi kill × 12 freq): senza kill −0,0002…
  −0,008 dB su 5 Hz–60 kHz (requisito ±0,1 dB, margine 12×); ai crossover la
  somma resta piatta (−0,0004 dB @90 Hz).

| Caso | v0.2 (allineata) | v0.1 (troncata) | Nota |
|---|---|---|---|
| nessun kill, worst | −0,008 dB | −4,73 dB @1,27k | requisito SPEC §6 ✓ |
| KILL SUB | −76,3 dB @10 Hz | −76 | invariato |
| KILL KICK | −18,4 dB (min @~180) | −24 @200 | vedi nota sotto |
| KILL MID | −16,4 dB (min @~650) | −21 @700 | vedi nota sotto |
| KILL HIGH | −14,0 dB (min @~2k) | −15 @2,5k | vedi nota sotto |
| KILL SUPER | −50,5 @15k / −68,2 @25k | −51 / −68 | invariato |
| ALL-KILL | −inf (silenzio assoluto) | −inf | gate VCA, invariato |

Nota sui kill interni "meno profondi": i numeri v0.1 erano gonfiati dalla
cancellazione di fase (le bande residue si sommavano fuori fase e scavavano
anche materiale vivo — gli stessi buchi che rovinavano la somma piatta). La
v0.2 è onesta: il residuo al centro banda è la coda di overlap delle bande
adiacenti in fase (−12·s dB circa, s = spaziatura in ottave). Conseguenza
musicale per la questione 67: spaziature più larghe = kill più profondi
(~6 dB in più per mezza ottava) oltre che bande più distinte.

Altri risultati:
- Group delay: §3.1 (picco 7,9 ms @58 Hz; la v0.1 aveva già 7,3 ms — costo
  dei 24 dB/ott, non dell'allineamento).
- Trimmer: edge spostato ±10% senza muovere l'allpass → errore di somma
  ≈0,02 dB: i trim di edge e allpass NON vanno accoppiati.
- Variante lite (3 AP2/lato): worst −0,125 dB (align_math.py) — sconsigliata:
  al limite del requisito, risparmio solo 3 quad.
- Macromodello: classe OPA1654 (A0 120 dB, GBW 20 MHz). Il macromodello v0.1
  (A0 60 dB) introduceva da solo ~0,15 dB di errore di loop: i numeri assoluti
  v0.1 vanno letti con quel pavimento (i buchi −3…−9 dB erano comunque reali).
- Idea collegata (da valutare nel design di sistema, questione 18 CUE): le
  prese di banda allineate in fase sono utili anche per un monitoring CUE
  coerente in fase.

### 8.3 v0.2 — Celle parametriche + cascata (`param-cell.cir`, `param-cascade.cir`)

Cella singola (griglia Q 0,5/1/3 × b 0/+1/−1,82/−3,0/−4,62, f0 = 700 Hz;
probe diretti: `param-cell-q.cir`, `param-cell-pos.cir`):
- **detent (b=0): ±0,0001 dB piatto** su 20 Hz–20 kHz per ogni Q —
  "piatto per costruzione" confermato;
- **boost: +9,005 / +12,041 / +14,995 dB** (target 9,006 / 12,041 / 14,995):
  errore ≤0,005 dB, picco esattamente a f0 per ogni Q;
- **notch (b=+1): −81 dB (Q0,5) / −76 (Q1) / −63 (Q3)** @700 Hz con gm
  ideale — con LM13700 reale attendersi valori di classe eq-serie
  (−45…−60): da riverificare coi modelli reali (coda EQ beta-3);
- **Q: misurata = comandata** (|bp_b| a f0 = Q, errore <0,001 dB); gonne a
  ±0,58 ottave combaciano con la teoria del 2° ordine (<0,01 dB);
- **position**: f0 via gm = 19,2·Iabc/(2πC) comandata a 250/450/700/1100/
  1500 Hz: picco +14,99 dB alla frequenza esatta (±0,005 dB su 2,6 ottave).

Cascata 5 celle in serie (centri PROVVISORI 60/180/600/2k/8k Hz):
- **tutto a detent: −0,0003…−0,005 dB su 10 Hz–40 kHz** — la cascata non
  degrada il detent (meglio di eq-serie ±0,02: qui niente summer condiviso);
- **"curva dub"** (EQ1 +12 @60 Q1, EQ3 notch @600 Q3, EQ5 +9 @8k Q0,5):
  12,03 / −58,5 / 9,01 dB come comandato; gonne fisicamente coerenti
  (+1,6 dB @10 Hz = coda della campana EQ1); nessuna interazione indesiderata
  tra bande.

Lezioni LTspice cumulate (si aggiungono alla lista di sessione): nodo
integratore pilotato solo da G-source vuole Rbias a massa (100 MΩ: senza,
"floating node" e OP fallito → AC piatto); V-source di sola lettura su nodo
isolato dà I = 0 (gm morto — usare .param direttamente nell'espressione);
.step LIST esegue in ordine CRESCENTE (leggere i log di conseguenza);
nomi .meas duplicati = run rifiutato.

### 8.4 v0.2 — Rumore del percorso completo (`module-noise.cir`)

Catena mono completa: pad −6 dB → banca allineata (28 sezioni, gate g=1) →
summer → 5 celle parametriche a detent (pot gain REALE 10k incluso) → drive
placeholder → make-up +6 dB. Metodologia eq-serie: macromodello op-amp
uniforme ~6 nV/√Hz (conservativo: OPA1654 reale 4,5, OPA1612 1,1),
integrazione 20 Hz–20 kHz NON A-pesata (conservativo vs target A-wtd).

**PASS: −108,4 dBu** (2,93 µV) contro target sheet §3 ≤ −90 dBu → **18,4 dB
di margine**. Il percorso più lungo del mixer resta 16 dB sotto il budget del
singolo canale CDJ: contributo al sistema trascurabile.

| Sezione | Integrato 20-20k | Quota |
|---|---|---|
| Totale percorso | −108,4 dBu | 100% |
| Banca + pad + make-up (`module-noise-bank.cir`) | −109,9 dBu | 72% |
| 5 celle + drive | −113,9 dBu | 28% |

Densità spettrale d'uscita: 288 nV/√Hz @100 Hz, 298 @1 kHz, 222 @10 kHz
(piatta: niente code 1/f nel macromodello — i reali peggiorano sotto ~100 Hz,
beta-3). Assenti dal conteggio (documentati come in eq-serie): rumore
LM13700 (10 OTA nel percorso + Rout dei nodi integratori), THAT 2181 (gate
e drive), rumore di wiper dei pot. Con modelli reali la cifra può solo
muoversi di qualche dB: il margine 18,4 dB assorbe la stima.

### 8.5 v0.2 — Gate VCA THAT 218x + ramp anti-click (`gate-ramp.cir`)

Macromodello condiviso `sim/lib/that2181.inc` (law Blackmer ±6,1 mV/dB da
datasheet, gain range −100…+40 dB, polo 20 MHz, clamp rail): un modello,
tre usi (gate 5-way, matrice FX v0.2, VCA CDJ §7). Test: programma worst
+10 dBu (3,46 Vp) a 1 kHz, kill al PICCO (worst case per il click), CV su
EC− con ramp lineare-in-V = lineare-in-dB (fade esponenziale = gesto
musicale, nessun kink d'inviluppo):

| Ramp τ | Picco HF (sonda click) | vs brusco | Residuo post-fade |
|---|---|---|---|
| 1 µs (brusco) | 3,64 V | — | 49 mV |
| 0,3 ms | 2,15 V | −4,6 dB | 19 mV |
| **1 ms (voce 55)** | **1,39 V** | **−8,4 dB** | **1,8 mV** |
| 3 ms | 0,90 V | −12,1 dB | 7 µV |

Floor del gain raggiunto ESATTAMENTE a ogni τ: 34,6 µV = −100 dB (law del
modello verificata). Sonda click = HP 2 poli ~1,6 kHz (baseline del
programma puro: 0,69 V). Lettura: 1 ms è il compromesso del gesto dub —
lo snap resta immediato, il click da gradino sparisce; 3 ms inizia a
sembrare pigro (dati a supporto della ratifica voce 55). Nel reale restano
da verificare a banco: feedthrough EC→audio durante la ramp (~−85…−100 dB
dopo trim) e click da accoppiamento CV (non nel modello) — il layout CV
lontano dall'audio è la mitigazione (design di sistema, questione 21).

### 8.6 Nota di metodo

Tutti i valori [PROVVISORIO]; le misure usano il macromodello op-amp classe
OPA1654 (A0 120 dB, GBW 20 MHz, lineare): la piattezza fine della banca si
verifica coi modelli reali (rumore/THD in beta-3) e soprattutto a banco con
trimmer di allineamento (§3). Gate: nelle sim di banca sono ideali (g = 0/1);
il THAT 218x reale con ramp 1 ms è validato a parte (§8.5).

### 8.7 Coda beta-3 — celle con LM13700 REALE (`sim/five-way/param-cell-real*.cir`, 2026-09-28)

Risultati completi in `sim/filtro/RISULTATI-ota-real.md` §5-§6 (il modello
OTA è condiviso col filtro). Sintesi per la cella (f0 = 700 Hz, Iabc = 7,56 µA):

- **Piccolo segnale: la griglia v0.2 REGGE** — detent −0,0001…−0,00003 dB
  (piatto costruttivo confermato col modello reale), boost +9,005/+14,995 dB
  (±0,02; solo Q 0,5 a +15 esce a −0,018), notch VERO −67…−78 dB (hmin) con
  f0 spostata +1% (α/mirror: a 700 Hz fissi si leggerebbe −25…−41) → assorbita
  dal trim per-banda del converter position (§4.1 opzione B, già a design).
- **Rumore (worst case boost massimo)**: −119,7 dBu (Q1) / −122,7 (Q3)
  integrati 20 Hz-20 kHz con en OTA fisico (15 nV/√Hz a 7,56 µA; die reale
  2-5× peggio → anche +14 dB resta dentro il budget §8.4). Il rumore NON è
  il problema della cella.
- **FINDING BLOCCANTE (livelli)**: a −6 dBu (388 mVp) la cella nuda collassa —
  gain misurato 1,1-1,3 contro 5,62, THD 2,8-6,4%: lo stato Q·Vin su C 33n a
  700 Hz chiede 168-500 µA all'OTA che ne eroga ~7,5 (tetto strutturale
  Vstato(f0) = 1/19,2 = 52 mV, indipendente da Iabc/C). La v0.2 non lo vedeva:
  il modello comportamentale non ha limite di corrente e l'AC linearizza.
  Riproduttore: `sim/five-way/dbg-cell-tran.cir`. Scaling+make-up bocciato
  (rumore ×N: −93,7 dBu per cella → modulo ~−85, FAIL §8.4) → **questione 70:
  PoC delle topologie pulite FATTO E VALIDATO (2026-09-28,
  `sim/five-way/RISULTATI-cell-clean.md`)** — lo schizzo "OTA scalatore" è
  bocciato dall'analisi (muro del rumore en×k); raccomandata **(c-A) JFET
  VCR bootstrappato**: integratori op-amp + JFET in triode come resistore
  controllato (gate a Vcm+vds/2: quadraticità cancellata esatta), THD
  0,004% (core −20 dBu) / 0,11% (worst +10 dBu), rumore −121,7/−124,9 dBu
  (meglio della cella OTA), law position lineare-in-f ±1,8% (shaper θ→Vcm
  famiglia dec. 70), detent −0,0001 dB e boost ±0,008 dB (griglia v0.2
  confermata), Q invariante ±0,07%; riferimento core locale −12…−18 dBu con
  make-up nel summer d'uscita (zero silicon extra). Alternativa (c-B) VCA
  218x ×2 validata (law esatta 5 cifre, livelli pieni dec. 73 invariata,
  +20 chip → voce 37). Prossimo rilascio: celle v0.2.1 (design dettagliato
  su (c-A): C per banda rivisti, distribuzione Vcm a follower+trim, coppia
  JFET matched per lato; segno di b invertito = pot sul terminale opposto).

## 9. Questioni toccate

- **8** (matematica filter bank): RISPOSTA v0.2 — banca ALLINEATA IN FASE:
  somma piatta ESATTA dimostrata in math (Σ = prodotto dei 4 allpass, |Σ| = 1,
  errore 1e-15) e validata in simulazione (−0,0002…−0,008 dB su 5 Hz–60 kHz,
  §8.2); kill invariato (all-kill = silenzio assoluto). Lo schema funziona con
  qualunque frequenze di crossover: resta aperta solo la scelta musicale
  (questione 67 — dato nuovo: spaziature più larghe = kill più profondi,
  ~6 dB per mezza ottava) e le frequenze dell'impianto di Filippo.
- **9** (EQ creativo): circuito cella VALIDATO v0.2 (§4.1, §8.3):
  detent/boost/notch/Q/position esatti in simulazione; pot gain nel dominio
  del segnale (tra ±bp_b, niente CV). APERTO: law di position (lineare vs
  esponenziale — opzione A/B §4, ascolto M4L); law del gain (taper custom,
  famiglia eq-serie §10 [PROVVISORIO — ascolto M4L]); profondità notch con
  OTA reali e rumore del modulo (§10.4/§10.5).
- **10** (drive): struttura a due stadi definita; taper esatto e carattere
  DOPO le referenze di Filippo (61).
- **24** (layout comandi): invariata — il pannello è design di Filippo;
  l'elettronica fornisce: 5 kill switch + 5 slider/pot gain + 5 pot position
  + 5 switch width + drive pot + (meter).
- **67** (frequenze 5 vie): la banca è progettata con trimmer per edge →
  le frequenze restano spostabili a banco ±10% senza redesign.

## 10. Prossimi passi (v0.2)

0. [FATTO 2026-09-27] **Banca allineata in fase**: soluzione esatta
   dimostrata e validata (§3.1, §8.2 — `bank-aligned.cir` + `align_math.py`).
   Le spaziature non sono più vincolate dalla matematica: l'ascolto per la
   questione 67 è libero (dato: spaziature più larghe = kill più profondi).
1. [FATTO 2026-09-27] Celle parametriche complete + cascata 5 celle
   VALIDATE (§4.1, §8.3). [CODA BETA-3 FATTA 2026-09-28 (§8.7)]: LM13700
   reale — piccolo segnale e rumore confermati, notch −67…−78 dB con trim
   f0; FINDING: tetto di stato 52 mV → cella nuda inutilizzabile a −6 dBu
   → **questione 70: PoC VALIDATO (c-A JFET VCR raccomandata,
   RISULTATI-cell-clean.md)** → celle v0.2.1. Law del gain da confermare a
   orecchio in M4L.
2. Drive: candidati JFET + spettri armonici (dopo referenze 61).
3. [SPECIFICATO 2026-09-27] Converter position (opzione B): C per banda e
   finestra Iabc 2-31 µA, mirror ratio 0,05-0,6 (§4.1); realizzazione =
   riuso filtro v0.2 (converter master + mirror bufferizzati ≤1,6%).
4. [FATTO 2026-09-27] Gate VCA THAT 218x con ramp 1 ms VALIDATO (§8.5,
   `gate-ramp.cir`): click −8,4 dB vs brusco, floor −100 dB esatto. Modello
   condiviso `sim/lib/that2181.inc` (pronto per FX v0.2 + CDJ §7). A banco:
   feedthrough EC→audio e click da accoppiamento CV.
5. [FATTO 2026-09-27] Rumore del modulo completo: −108,4 dBu contro target
   −90 (sheet §3), margine 18,4 dB (§8.4). Beta-3 [PARZIALE 2026-09-28]:
   contributo celle con LM13700/OPA16xx reali MISURATO (§8.7: −119,7 dBu
   worst-case boost, dentro budget anche con die 5× peggiore); restano
   THAT 2181 (gate/drive: modello senza rumore) e A-pesatura. Il totale
   definitivo segue la topologia della questione 70.
6. Meter pickup e ballistica 10 Hz (con CDJ §7 item 6).
