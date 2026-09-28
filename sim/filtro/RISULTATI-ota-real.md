# LM13700 REALE — modello, self-test e riesame dei core SVF (2026-09-28)

Riferimenti: filtro v0.3 item §9.2 (ramp BBM) e §9.3 (modello LM13700
reale: offset/rumore/swing/THD), 5-way §10.1 coda beta-3 (LM13700 per
notch/THD celle), questione 11 (carattere risonanza), questione 61
(referenze distorsione). Modello condiviso: `sim/lib/lm13700.inc`
(transistor-level, calibrato su datasheet TI SNOSBW2F nov 2015).
Netlist: `ota-selftest-{ac,tran,diode,noise}.cir`, `svf-real-{ac,offset,thd,noise}.cir`,
`svf-noise-{114n,10.8u,397u}.cir` (run ufficiali noise), `bbm-ramp.cir`;
5-way: `param-cell-real{,-thd,-noise}.cir`, `dbg-cell-tran.cir`.

## 1. Il modello (sim/lib/lm13700.inc)

Macromodello transistor-level di UN canale: mirror di coda 1:1 + coppia
differenziale NPN + mirror di uscita PNP (Iout = Ic4 − Ic5 = Iabc·tanh(Vd/2VT))
+ diodi linearizzanti (pin dbp/dbn) + Vos parametrico per istanza.
Calibrazione da datasheet (VS ±15 V, Iabc 500 µA):
- gm = 19,2·Iabc (tab. 6.4: 6,7/9,6/13 mS min/typ/max — tolleranza REALE
  ±30%, il modello dà 19,4 piatto: la dispersione resta compito del trim
  per-core già progettato nel filtro v0.2);
- picco corrente d'uscita ≈ Iabc (350/500/650 µA a 500 µA): IL VINCOLO
  STRUTTURALE del design, vedi §5;
- Vos 0,4 mV typ / 4 mV max + cambio con Iabc 0,1/3 mV; Ib 0,4 µA typ
  (Bf = 500); Vaf = 2000 → ro ≈ 7 MΩ a 500 µA (datasheet: Zout 8 MΩ min;
  con Vaf = 100 il mirror dava gm +20% e corrente d'offset 7%·Iabc = 3,6 mV
  di Vos efficace — artefatti, corretti in calibrazione);
- rail: ±15 V = condizione datasheet. ASSOLUTO ±18 V = limite del chip:
  il dominio ±18 V del progetto NON è ammesso con continuità → rail
  dedicati ±15/±16 V per tutti gli OTA del mixer (nota per questione 20/PSU).
ASSENTI nel modello (verifica a banco): rumore numerico (il datasheet dà
solo la Fig. 15 grafica: il modello genera il LIMITE FISICO della coppia,
die reale verosimilmente 2-5× peggio → letture rumore OTTIMISTICHE),
THD del die (geometrie laterali), CMRR 80-110 dB (modello: ∞), 1/f,
buffer Darlington interni (il progetto usa buffer esterni), crosstalk.

## 2. Self-test del modello (ota-selftest-*)

| Test | Risultato | Contro datasheet |
|---|---|---|
| gm/Iabc (100 nA…500 µA) | 19,4 piatto ±0,5% (−2,5% a 500 µA) | 19,2 typ ✓ (chip reale ±30%) |
| Limite Iout | 485 µA a Iabc 500 µA; 7,33 µA a 7,56 µA | ≈ Iabc (0,7-1,3×) ✓ |
| THD nudo single-ended (Vd) | 0,095% @5 mV · 0,54% @13 mV · 2,0% @26 mV · 6,8% @52 mV · 17,4% @104 mV | tanh(Vd/2VT): THD ≤0,1% solo con Vd ≤ ~5 mV |
| en (rumore, fisico) | 133 nV/√Hz @100 nA · 29 @2 µ · 15 @7,56 µ · 7,3 @31 µ · 4,3 @100 µ · 2,6 @500 µA | nessuna spec numerica TI: limite fisico, die reale 2-5× peggio |
| Offset (Vos param) | gestito per istanza; sweep = inviluppo | 0,4 typ / 4 max + Δ3 mV ✓ |

**Diodi linearizzanti — FINDING**: nel nostro contesto (OTA pilotato in
TENSIONE da summer op-amp, bias diodi resistivo da vcc) la cancellation
NON avviene — THD misurato identico al nudo (Rin 26 Ω) o peggiore
(Rin 260 Ω: H2 24% da degenerazione + asimmetria ln). La cancellation
esatta (Iout = Iabc·Is/ID, datasheet §7.3.2) richiede drive IN CORRENTE
differenziale con bias a bassa Z: nel nostro SVF l'ingresso è low-Z in
tensione → diodi inerti. Anche in configurazione corretta il trade-off è
sfavorevole: gittata lineare = ID·Rin/2 con gm_eff = Iabc/(2·Rin·ID) →
per ±1 V lineari servono Iabc ≈ 2·gm·Vlin ≈ 290 µA-1 mA per OTA (fuori
dalla finestra 2-31 µA delle celle) + ID ≈ mA di bias per diodo.
**Scartati per i core integratori** (restano utili per VCA piccoli segnali).

## 3. Core SVF filtro con OTA reale (svf-real-*)

Struttura = feas-svf v0.1 (summer + buffer di stato + 2 integratori OTA,
C 33 nF), buffer/summer ora OP1654 reali, rail ±15 V.

**Law e Q intatte** (AC, griglia Iabc 114 n…397 µ):

| Iabc | fc ideale | fc misurata | err | Q (bpk) |
|---|---|---|---|---|
| 114 n | 10,58 Hz | 10,59 | +0,1% | 0,702 |
| 1,08 µ | 100,2 | 100,9 | +0,7% | 0,706 |
| 10,8 µ | 1002 | 1010 | +0,8% | 0,707 |
| 108 µ | 10020 | 10116 | +1,0% | 0,708 |
| 397 µ | 36868 | 37410 | +1,5% | 0,713 |

Errore ≤1,5% (α/mirror del modello; il chip reale ±30% si assorbe col
trim per-core del design v0.2 — invariato). Converter/mirror/shaper del
filtro v0.2 RESTANO VALIDI con qualsiasi topologia di core che usi gm ∝ Iabc.

**Offset DC** (.dc, Vin = 0, Vos 0,4/4 mV × Iabc 114 n/10,8 µ/397 µ):
stati a regime 3,9-4,6 mV (bp), 4,4-4,6 mV (lp), hp −10 mV — LIMITATI,
nessuna deriva a saturazione (il loop SVF ha feedback DC), insensibili a
Vos ×10 (dominano le correnti residue di mirror, non Vos). A valle:
irrilevanti (mV DC su dominio 0 dBu). Nessun trim DC necessario.

**THD a fc = 1 kHz** (tran, .four; istanza nuda vs scalata 1/20 + make-up ×20):

| Vin (picco) | nudo: THD | nudo: stato bp_b | scalato: THD | scalato: out |
|---|---|---|---|---|
| 52 mV | 0,87% | 37 mV (lineare) | 0,003% | 69 mV |
| 104 mV | 1,32% | 63 mV (compress.) | 0,012% | 106 mV |
| 388 mV (0 dBu int.) | 0,85% | 78 mV (saturo, gain −3,5×) | 0,155% | 305 mV |
| 775 mV (0 dBu) | 1,25% | 81 mV (saturo) | 0,55% | 551 mV ✓ |
| 2,45 V (+10 dBu) | 37,5% | 102 mV (saturo duro) | 1,24% | 976 mV (limite) |
| 6,16 V (+18 dBu) | 94,3% | 110 mV (collasso) | 0,88% | 1,01 V (saturo) |

Il nudo comprime MORBIDO (tanh + limite di corrente = saturazione dolce,
gain −3,5× a 388 mV senza THD esplosiva: 0,85-1,25%) — carattere da
filtro OTA classico (famiglia Sherman/MS-20), collasso solo oltre +6 dBu.
Lo scalato 1/20 resta pulito fino a ~1 V core-in (limite 52 mV × 20),
THD 0,55% a 0 dBu — pulito ma non "0,1%".

**Rumore** (core nudo, uscita LP, integrato 20 Hz-20 kHz, en OTA fisico):

| fc | rumore | vs target sheet (≤−90 dBu) |
|---|---|---|
| 10,6 Hz | −134,8 dBu | PASS 44,8 dB |
| 1 kHz | −112,7 dBu | PASS 22,7 dB |
| 37 kHz | −107,8 dBu | PASS 17,8 dB (die reale 5× peggio: ~−94, ancora PASS) |

Variante scalata + make-up ×20: rumore riferito ×20 (+26 dB) → −81,8 dBu
a fc alta: **FAIL**. (Densità uscita a fc 37k: 61 nV/√Hz, dominata da
R/OP1654, non dall'OTA.)

## 4. Commutazione di modo BBM + ramp (bbm-ramp.cir) — item §9.2 FATTO

Meccanismo (indipendente dalla questione 63): fade-out VCA THAT 218x del
percorso uscente → gap muto 50 µs (BBM, classe ADG14xx [PROVVISORIO]) →
fade-in del percorso entrante, ramp CV τ variabile. Worst: commutazione
al picco di +18 dBu (6,16 Vp, 1 kHz). Sonda click = HP 2 poli 1,6 kHz
(pattern gate-ramp 5-way; baseline programma = 0,613 V).

| τ ramp | picco sonda click | vs brusco | vs baseline | gestualità (2τ+gap) |
|---|---|---|---|---|
| 1 µs (brusco) | 3,22 V | — | +14,4 dB | click pieno |
| 0,3 ms | 1,90 V | −4,6 dB | +9,8 dB | udibile |
| 1 ms | 1,23 V | −8,4 dB | +6,1 dB | ~2 ms: trasparente |
| 5 ms | 0,68 V | −13,5 dB | +0,9 dB ≈ baseline | ~10 ms: "soft mute" percepibile |

Durante il gap l'uscita è muta (BBM = interruzione, non crossfade):
residuo = floor del modello (−100 dB). Raccomandazione [PROVVISORIA]:
**τ = 1 ms** (click −8,4 dB = sotto il programma, gesto ~2 ms trasparente)
coerente col gate 5-way (stesso −8,4 dB @1 ms) e col reroute FX (−9,6 dB):
FAMIGLIA UNICA 1 ms per tutte le commutazioni CV del mixer → dati per la
ratifica della voce 55. τ = 5 ms solo se l'ascolto (63/64) preferisce il
"buco" morbido. Circuito: stesso generatore di rampa del gate 5-way
(gate-ramp validato), CV condivisa.

## 5. Cella parametrica 5-way con OTA reale (param-cell-real*) — coda beta-3

**Piccolo segnale (AC)** — la griglia v0.2 regge:
- detent: −0,0001…−0,00003 dB (PIATTO ESATTO anche col modello reale:
  l'insensibilità è costruttiva, b = 0 esclude gli stati);
- boost: +9,005/+9,005/+8,993 dB (b −1,82; Q 3/1/0,5) e +14,995/+14,995/
  +14,982 (b −4,62): entro ±0,02 dB dal target (solo Q 0,5 a +15 esce
  di poco dal ±0,005 v0.2: −0,018 dB);
- notch: profondità VERA −67…−78 dB (hmin, Q 3/1/0,5) contro −63…−81
  ideale; f0 spostata +1% (mirror/α) → a 700 Hz fissi si legge −25…−41 dB:
  il trim per-banda del converter position (già a design, §4.1 opzione B)
  la assorbe interamente.

**Livelli reali (tran, tono a f0 = 700 Hz) — FINDING BLOCCANTE**:
a riferimento interno −6 dBu (388 mVp) la cella NUDA collassa:

| caso | gain misurato | atteso | THD | stato bp_b |
|---|---|---|---|---|
| Q1, 388 mV | 1,34 | 5,62 | 6,4% | 79 mV (saturo) |
| Q3, 388 mV | 1,11 | 5,62 | 2,8% | 95 mV (saturo) |
| Q1, 2,45 V | 1,08 | 5,62 | 1,5% | 118 mV (saturo) |
| Q3, 2,45 V | 1,04 | 5,62 | 0,54% | 138 mV (saturo) |

Causa strutturale (§6): a Iabc = 7,56 µA l'OTA eroga ~7,5 µA; lo stato
Q·388 mV su C 33 nF a 700 Hz ne chiede 168-500 µA (22-66×). La v0.2 non
lo vedeva: il modello comportamentale G = 19,2·Iabc·V non ha limite di
corrente (e l'AC linearizza senza limite). dbg-cell-tran.cir = reproducer.

**Rumore cella** (boost massimo = worst case iniezione, en OTA fisico):
Q1 −119,7 dBu · Q3 −122,7 dBu integrati 20 Hz-20 kHz. Dentro il budget
di module-noise v0.2 (−108,4 senza OTA): il contributo OTA non sposta il
totale nemmeno con die reale 5× peggiore (+14 dB → −105,7 per cella;
5 celle ≈ −98,7 contro un percorso −108,4 dominato da altri stadi →
totale ~−98: sempre PASS vs −90). **Il rumore NON è il problema della
cella; il livello sì.**

## 6. FINDING STRUTTURALE — il tetto dei 52 mV

Per QUALSIQUE integratore LM13700 a f = f0: Vstato_max = Iout_max/(2π·f0·C)
= Iabc/(gm·2πf0C/ω0…) = **1/19,2 = 52 mV**, indipendente da Iabc, da C e
da f0 (il limite di corrente cresce come gm). Sopra: compressione morbida
(tanh) poi clipping. I livelli interni del progetto (−6 dBu = 388 mV;
send 0 dBu = 775 mV; stati Q3 = 1,16 V) stanno 7-22× oltre. Conseguenze:
1. **cella 5-way nuda: inutilizzabile ai livelli di progetto** (gain −14 dB
   e THD 3-6% già a −6 dBu);
2. **core filtro nudo: compressore morbido** ~1% THD a 0 dBu, collasso a
   +10 dBu — utilizzabile SOLO come carattere voluto (questione 61/64);
3. **scalare + make-up non basta**: THD ∝ 1/N² ma rumore OTA ∝ N →
   N = 20: THD 0,55% e rumore −82 dBu (FAIL); N = 40: THD ~0,14% e
   rumore −76 dBu (FAIL peggiore). Non esiste N che soddisfi entrambi;
4. **diodi linearizzanti: non applicabili** in drive di tensione (§2) e
   comunque costosi (290 µA-1 mA per OTA per ±1 V lineari).

**Opzioni per core puliti a livello di progetto** (questione 70):
[SUPERATA — vedi §0 di `sim/five-way/RISULTATI-cell-clean.md`] lo schizzo (c) "OTA scalatore gm" è BOCCIATO dall'analisi: ogni divisione k del segnale con make-up ×k riferisce l'en dell'OTA ×k (muro del rumore ≥ −83 dBu per k ≥ 155) e il prodotto THD×rumore è costante in k. Le varianti pulite PoC-validate sono:
- **(c-B) VALIDATA — VCA THAT 218x ×2 nel loop SVF** (integratori op-amp): law esatta 5 cifre, Q invariante, griglia v0.2 confermata, livelli pieni; +2 chip per core (`sim/five-way/cell-vca-*.cir`, RISULTATI-cell-clean §1).
- **(c-A) VALIDATA — JFET VCR bootstrappato** (integratori op-amp): THD 0,004-0,11% ai livelli reali con core −12…−18 dBu locale, rumore −121,7 dBu, costo quasi nullo (`sim/five-way/param-cell-jfet-*.cir` + `sim/filtro/vcr-jfet.cir`, RISULTATI-cell-clean §2). RACCOMANDATA per le celle.
- (b) diodi + Iabc alto: fattibile sulla carta per il filtro (12-24 mA
  totali), fuori finestra per le celle — scartata.
- (a) carattere OTA nudo: per il FILTRO è un'opzione musicalmente legittima
  (compressione morbida ~1% a 0 dBu che cresce col livello: la firma
  Sherman/MS-20) — da ascoltare contro (c-B) al prototipo, intrecciata con
  61 (referenze) e 64 (allineamento). Per le celle EQ: NON accettabile
  (l'EQ deve restare pulito; il drive è uno stadio separato e voluto).

## 7. Lezioni LTspice (nuove, si aggiungono a quelle cumulate)

1. **Rbias dei nodi integratore deve essere >> ro dell'OTA** (ro = Vaf/Iabc
   ≈ 7 MΩ a 397 µA): con Rb = 10 MΩ la Ioff di mirror (~1%·Iabc) crea un
   SECONDO equilibrio DC (stati = Ioff·Rb, follower saturi) che il solver
   può preferire. Usare 100 MΩ+.
2. **Mai macro con limit()/clamp dentro un loop SVF per analisi .noise**:
   la clamp rende il loop DC-bistabile; se la linearizzazione cade nel
   ramo falso (stati saturi) il .noise restituisce ZERI silenziosamente
   (nessun errore nel log). Per il rumore: variante della macro senza
   clamp (OPX in svf-real-noise.cir). Il .tran non ha questo problema
   (parte dall'op ma evolve: verificare comunque i picchi stato).
3. **.step + .noise su circuito bistabile = inaffidabile**: anche con
   .nodeset e .options; fare run ONE-SHOT per punto (sed sul .param).
4. **Il .op in batch non stampa i nodi nel log** (li salva nel .raw):
   per leggere il DC usare .dc fittizio + .meas dc FIND ... AT.
5. Vaf del modello OTA: con Vaf = 100 il mirror di uscita dà gm +20% e
   corrente d'offset 7%·Iabc (= 3,6 mV di Vos efficace) — sempre tarare
   Vaf sulla Zout datasheet (ro = Vaf/Ic).

## 8. Verdetto

- Filtro v0.3 item 2 (ramp BBM): **FATTO** — famiglia 1 ms confermata,
  dati per ratifica voce 55. Item 3 (LM13700 reale): **FATTO** — modello
  validato, offset/rumore OK, ma THD/swing rivelano il tetto dei 52 mV →
  la topologia del core va decisa (questione 70) PRIMA del prototipo
  millefori (item 4). Item 6 (rumore modulo completo): dato parziale
  (core −108…−135 dBu: PASS) — il modulo completo segue la topologia 70.
- 5-way coda beta-3: **FATTA** — griglia piccolo segnale confermata
  (detent piatto, boost ±0,02 dB, notch −67…−78 con trim f0), rumore
  dentro budget; MA la cella nuda non regge i livelli di progetto →
  questione 70 — PoC c-A/c-B VALIDATI in `sim/five-way/RISULTATI-cell-clean.md` (raccomandazione: JFET VCR per le celle; filtro = scelta musicale (a) vs (c-B)).
- Trasversale: rail OTA ±15/±16 dedicati (±18 = limite assoluto LM13700)
  → questione 20 (PSU); gm reale ±30% → trim per-core confermato.
