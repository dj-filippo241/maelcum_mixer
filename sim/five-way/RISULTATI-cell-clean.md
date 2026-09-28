# PoC QUESTIONE 70 — celle parametriche "pulite": VCA-in-loop vs JFET VCR (2026-09-28)

Riferimenti: questione 70 (topologia core dopo il finding del tetto 52 mV,
`sim/filtro/RISULTATI-ota-real.md` §6), five-way §4.1/§8.3/§8.7, filtro §9.
Netlist: `cell-vca-{ac,law}.cir`, `param-cell-jfet-{law,grid,thd,noise}.cir`,
`sim/filtro/vcr-jfet.cir`. Obiettivo: core SVF che regga i livelli di
progetto (THD bassa) restando dentro il budget rumore (−90 dBu sheet §3;
modulo −108,4 v0.2), con position via controllo esterno e Q/width/detent
della v0.2 invariati.

## 0. Perché non "op-amp + OTA scalatore" (correzione dello schizzo iniziale)

Lo schizzo scritto in questione 70 (OTA come scalatore gm a piccolo segnale)
NON funziona, per un muro doppio:
- **muro del rumore**: ogni architettura che divide il segnale di k e lo
  rimoltiplica riferisce l'en dell'elemento di controllo ×k. L'OTA ha
  en ≥ 2,6 nV/√Hz (500 µA) e per THD ≤0,1% serve k ≥ 155 → ≥ 400 nV/√Hz
  riferiti ≈ −83 dBu integrati: FAIL strutturale, indipendente da k.
- **muro THD×rumore**: THD ∝ 1/k² e rumore ∝ k² → il prodotto è costante:
  nessun k soddisfa entrambi (verificato anche numericamente in
  RISULTATI-ota-real §6: N=20 → −82 dBu FAIL; N=40 → −76 peggiore).
L'elemento variabile deve essere un RESISTORE a 2 terminali (rumore =
solo termica) o un moltiplicatore nel loop (VCA) che non scala il segnale.
Due candidati verificati in simulazione: **(c-B) VCA THAT 218x negli
integratori** e **(c-A) JFET come VCR linearizzato**.

## 1. (c-B) Cella con VCA THAT 218x nel loop SVF — VALIDATA

Struttura: summer v0.2 invariato; hp → VCA1(g) → R 10k/C → bp; bp_b →
VCA2(g) → R 10k/C → lp; damping da −bp_b (l'invertitore del pot ±bp_b,
già a BOM — CON UN SOLO VCA: Q ∝ 1/√g, inaccettabile; con due: Q esatta).

| Verifica | Risultato |
|---|---|
| Law position | f0 = g·700 Hz, g = 10^(Vc/0,122): misurata 284,1/445,8/699,8/1099,0/1725,4 Hz contro atteso 284,0/445,9/700/1099/1725 — ESATTA (5 cifre), esponenziale nativa 36,7 mV/ottava |
| Q invariante | bpk = 1,000 ±0,09% su ±1,3 ottave |
| Detent | −0,0001 dB (piatto costruttivo confermato) |
| Boost | +9,006…+9,008 e +14,996…+14,999 dB (±0,008 dB) |
| Notch | −64,2…−74,8 dB centrato ESATTO a 700 Hz (nessuno shift: law esatta) |
| Livelli | stati a −6 dBu di riferimento (dec. 73 INVARIATO): il VCA lavora a livello pieno, niente scaling |
| THD | non misurabile (moltiplicatore ideale nel modello): datasheet 0,0025% (A) / 0,005% (C) a livello line |
| Rumore | assente nel modello: classe da datasheet (floor −94 dBV, noise modulation 4 dB) → previsione ≥ classe OTA (−119,7), verifica a banco |

Costo: **+2 THAT 218x per cella** (10 celle → +20 chip: conteggio mixer
~54-56 → pesa sulla voce 37, il clone V2181 diventa quasi obbligatorio)
+ 2 sezioni op-amp per cella (integratori; totale celle 7 sez. vs 5).
Converter: la distribuzione Iabc diventa distribuzione Vc (buffer follower
+ trim: PIÙ SEMPLICE dei mirror bufferizzati, stessa precisione di tracking).
Tempco law: 0,33%/°C del gain impostato (dB) — comune a tutti i chip
(absolute f0 deriva, tracking L/R e tra celle stretto) → trim assorbe.

## 2. (c-A) Cella con integratori op-amp + VCR JFET bootstrappato — VALIDATA

Struttura: stessi integratori op-amp; il resistore d'ingresso è il JFET in
triode (d=hp, s=nodo virtuale), gate bootstrappato a Vcm + vds/2 (2 R 100k;
la cancellation della quadraticità è ESATTA per legge square-law). Position:
f0 = 1/(2π·rds·C) con rds = 1/(2β(Vcm−Vt)) → **law lineare in frequenza**
(lo shaper θ→Vcm genera l'esponenziale: famiglia law dec. 70 già a design).

Caratterizzazione VCR (`sim/filtro/vcr-jfet.cir`, NJF Vto −2/Beta 173µ/λ 5m):

| punto | gate rigido (THD) | bootstrappato (THD) |
|---|---|---|
| vds 39 mV, V−Vt 150 mV | 6,50% (= A/4(V−Vt), formula esatta) | 0,0047% |
| vds 233 mV, V−Vt 150 mV | 35,6% | 0,028% |
| vds 388 mV, V−Vt 150 mV | 45,0% | 0,67% (oltre finestra 2(V−Vt)=300 mV) |
| vds 1,16 V, V−Vt 900 mV | 31,4% | 0,14% (finestra 1,8 V ✓) |

Regola: **vds ≤ 2(Vcm−Vt)** e THD ≤ ~0,03%. rds lineare ±5% fino a 233 mV.

Cella completa (f0 700 Hz, C 22,8n, Vcm −1,711 → V−Vt 289 mV, rds 10k):

| Verifica | Risultato |
|---|---|
| Law position | f0 ∝ (Vcm−Vt): 283,5/405,9/699,2/982,9/1718,6 Hz contro atteso 282,8/398,8/698,6/983,8/1718,6 — entro ±1,8% (trim per banda assorbe; ±0,2% sui 4 punti su 5) |
| Q invariante | bpk = 1,000 ±0,07% su ±1,3 ottave |
| Detent | −0,0001 dB |
| Boost | +9,006 e +14,996…+14,997 dB (±0,008) |
| Notch | hmin −63,6…−76,3 dB; centro a 698,6 Hz (−0,2%: tolleranza C, non shift di law — il trim Vcm lo azzera) |
| THD (Q3, boost max, tono a f0) | core −20 dBu (77,5 mV): **0,004%**; worst programma +10 dBu (245 mV): **0,11%**; core −6 dBu (388 mV): 0,51% (fuori finestra: conferma che il riferimento del core va abbassato) |
| Rumore (boost max, core full-scale) | Q1: **−121,7 dBu** · Q3: **−124,9 dBu** (integrati 20 Hz-20 kHz; meglio della cella OTA reale −119,7/−122,7) |
| Riferimento core proposto | **−12…−18 dBu locale** (THD ≤0,03…0,1% al worst +10 dBu), make-up ×4…×8 assorbito dal gain del summer d'uscita (Rf2/Rain: ZERO silicon extra — il summer esiste già). Penalità rumore ×4…×8: −121,7+12…18 = −109,7…−103,7 dBu per cella worst-boost → modulo ~−100…−95 contro target −90: PASS con ≥10 dB anche nel worst case |

Costo: 2 JFET matched per cella (dual SOT-23 classe MMBF5457/BAV199…:
~10-20 € totali), −10 LM13700, +2 sezioni op-amp per cella (integratori),
distribuzione Vcm = follower + trim (2-4 sezioni per lato, shared).
Tempco: Vt ≈ −2 mV/°C → f0 assoluto 0,3-1,7%/°C (trim); **coppia matched
stesso die: ΔVt ~0,1-0,3 mV → tracking L/R 0,03-0,1%/°C** = ≤17 cent su
±10 °C — dentro il requisito ≤27 cent con margine [PROVVISORIO: verifica
a banco sulla coppia reale].

## 3. Segni e convenzioni (per il design v0.2.1)

Gli integratori op-amp invertono due volte: la struttura algebrica della
cella è IDENTICA alla v0.2 salvo (1) il damping che prende −bp_b
(l'invertitore del pot, già a BOM) e (2) il segno di b: H(f0) = |1+b|
(notch a b = −1, boost a b positivo) → **il pot si cabla sul terminale
opposto**: gesto musicale e taper (eq-serie §10) invariati.

## 4. Per il FILTRO globale (11,8 ottave — contesto diverso)

- (c-B) VCA: span necessario 3500:1 = 70,9 dB ✓ dentro il range 218x;
  +16 chip (8 core × 2) +16 sezioni op-amp; law esponenziale nativa dal
  converter PTAT esistente (ΔV → Vc via buffer): tempco comune assorbita
  dal trim per core (già a design v0.2).
- (c-A) JFET: range rds utile ~200:1 = 7,6 ottave < 11,8 → richiede
  C-switching a 2 gamme (6 ottave ciascuna, mux BBM già in famiglia §9.2)
  — fattibile ma più complesso; deriva assoluta 0,3-1,7%/°C contro
  tolleranza ±5-10% (dec. 74) con trim per core ✓.
- (a) core OTA nudo = CARATTERE: zero modifiche, zero costi, compressione
  morbida ~1% THD a 0 dBu che cresce col livello (famiglia Sherman) —
  opzione MUSICALMENTE legittima per il filtro, da ascoltare contro (c-B)
  al prototipo (61/64). Il vincolo ±15/±16 V rail (questione 20) vale
  per tutte le opzioni OTA.

## 5. Raccomandazione (ingegneria — la parola "carattere" resta a Filippo)

- **Celle 5-way: (c-A) JFET VCR** — costi 5× sotto (c-B), THD 0,004-0,11%
  ai livelli reali, rumore dentro budget con ≥10 dB, law/trim già in
  famiglia; riferimento core locale −12…−18 dBu con make-up nel summer
  d'uscita. Alternativa (c-B) se il banco smentisce il tracking JFET o se
  l'ascolto dello shaper lineare-in-f delude. Rilascio: celle v0.2.1.
- **Filtro: decisione musicale** tra (a) carattere OTA nudo e (c-B) VCA
  pulito — entrambe progettate e quantificate; ascoltare al prototipo con
  61/64. (c-A)+C-switching solo come fallback. Il millefori (item §9.4)
  prototipa la variante (a) che è il design v0.2 invariato; la variante
  (c-B) si prototipa sullo stesso PCB di base con adattatore.

## 6. Lezioni (si aggiungono a RISULTATI-ota-real §7)

1. `.meas ... WHEN x=MAX(y)` NON esiste in batch: per la frequenza di picco
   usare i due attraversamenti a 0,707 (CROSS=1/2) + PARAM sqrt(f_lo·f_hi).
2. Due integratori invertenti nel loop SVF: il damping deve prendere lo
   stato INVERTITO (−bp_b) altrimenti il loop ha poli a destra (l'AC
   linearizzato sembra sano, il tran esplode ai rail — verificare SEMPRE
   con un tran prima di fidarsi di un'AC su loop ristrutturato).
3. `.four`/THD su netlist con istanza doppia: i blocchi di log sono
   raggruppati per misura (tutti gli step della prima, poi della seconda),
   NON interleave per step.
4. JFET VCR: il bootstrap gate=vds/2 cancella ESATTA la quadraticità
   (square-law); resta λ e la finestra triode vds ≤ 2(Vgs−Vt) — il prodotto
   rds·vds_max = 1/β è costante: rds alta (f0 bassa) e segnale grande sono
   incompatibili → il riferimento del core si abbassa, non si tira il JFET.
