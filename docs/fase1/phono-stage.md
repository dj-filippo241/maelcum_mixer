# FASE 1 — Front-end PHONO MM (RIAA): design v0.1 (2026-09-28) + REV sub-100 Hz (2026-09-30)

> **REV 2026-09-30 (fix residuo sub-100 Hz)**: il residuo della curva v0.1
> (−0,5/−1,4/−3,9 dB a 100/50/20 Hz) è ATTRIBUITO e RISOLTO — colpevole il
> polo del DC block a 15,9 Hz (Rb2 100k): attenuazione diretta + carico del
> nodo d'uscita della rete RIAA. Fix = Rb2 1M (polo 1,59 Hz). Curva ora
> ≤ ±0,05 dB su 100 Hz-20 kHz; sotto i 100 Hz resta la sola subsonica SK
> (come da progetto). Warp invariato; EIN RICALCOLATO con metodo corretto
> (quirk INTEG LTspice): 1,79 µV 10-20k, out −79,8 dBu — 19 dB sotto il
> fruscio vinile. Dettaglio §3, netlist
> `sim/cdj/phono-sub100*.cir` + `phono-noise-fix.cir`.
>
> **v0.1 (2026-09-28)**: chiude la questione 6 (topologia RIAA → decisione 79)
> e realizza la variante phono promessa dalla decisione 56. Scope: testine
> **MM** (decisione 62: DJ standard + MM alta qualità); MC rinviata alla
> questione 7 (popolazione testine) come variante futura (gain ~60 dB e
> loading 10-100 Ω: altro front-end, non un trim di questo).
> Fonti: gain-staging-sheet §2 (out −2 dBu, gain 42 dB, overload ≥ +18 dBu,
> dominio ±15 V LN), questioni 6/7, decisione 56/62.

## 1. Requisiti

- Ingresso MM: 5 mV nominali (3-11 mV), max atteso 11 mV (sheet §2).
- Uscita blocco: −2 dBu nominale, +5 dBu con testina 11 mV; overload
  ≥ +18 dBu puliti (Rev A sheet); clipping a ~+25 dBu (clamp ±13,5 su ±15).
- RIAA di riproduzione: errore ≤ ±0,2 dB su 100 Hz-20 kHz (target interno;
  il vinile reale sta ben peggio).
- Subsonica: proteggere gli stadi dal warp SENZA mangiare il basso dub
  (−1 dB max a 30-40 Hz).
- Loading testina [PROVVISORIO q7]: 47 kΩ || C selezionabile 100/200/300 pF.
- Massa giradischi: terminale GND dedicato → stella analogue-0V (q. 21).
- Selettore LINE/PHONO per canale dopo il blocco (switch analogico di
  precisione, famiglia assign FX; mute breve durante la commutazione).

## 2. Topologia (decisione 79)

Tre blocchi in cascata, RIAA **passiva** tra due stadi piatti:

```
RCA PHONO → Rload 47k || Cload (switch) → [A1] STADIO 1 non-inv ×21
  (OPA1612: testina ~660 Ω = sorgente <100 Ω? no: 660 Ω — vedi nota)
  → [A2] SUBSONICA Sallen-Key HP 2 poli 13 Hz Q 0,707 (unity, OPA1612)
  → [A3] RETE RIAA PASSIVA (R1 21,8k serie; C1 34,8n shunt; R2 3,16k+C2 100n
    shunt; uscita dal nodo R1/C1/R2 — C2 è interno al ramo, NON prelevare da lì)
  → [A4] DC BLOCK 1 polo 1,59 Hz (C3 100n serie + Rb2 1M verso gnd —
    REV 2026-09-30: era 15,9 Hz con Rb2 100k, causa del residuo sub-100 Hz §3)
  → [A5] STADIO 2 non-inv ×60,6 (OPA1654: sorgente ~3 kΩ → regola d'uso FET)
  → [A6] SELETTORE LINE/PHONO → [B] GAIN del canale (catena v0.3)
```

Perché passiva e non RIAA in feedback: (1) il warp a 10-20 Hz con RIAA in
feedback dello stadio 1 metterebbe il boost bassissimo DENTRO il loop di
guadagno (clip e recovery lente); con la passiva il boost resta dopo la
subsonica e gli stadi vedono il warp già tagliato; (2) la passiva blocca la
DC verso lo stadio 2 solo se preceduta da un blocco DC: qui è la Sallen-Key
a farlo (gain 0 a DC) → niente condensatori elettrolitici nel percorso;
(3) componenti della rete in rapporto esatto con equazioni chiuse:
τ318 = R2·C2 · τ3180+τ75 = R1C1+R1C2+R2C2 · τ3180·τ75 = R1·R2·C1·C2.
Nota regola d'uso OP1612 (sorgenti <100 Ω): lo stadio 1 vede 660 Ω+load:
DEROGA DOCUMENTATA — con 660 Ω la in della 1612 (2 pA) dà ~1,3 nV: dentro
il budget (EIN misurato 1,79 µV 10-20k, REV 2026-09-30); in alternativa stadio 1 con OPA1654 e
perdita di 3 dB di rumore: scelta rinviata al banco [PROVVISORIO].

## 3. Risultati simulati (`sim/cdj/phono-riaa-*.cir`, 2026-09-28)

- **Curva (REV 2026-09-30, `phono-sub100-fix.cir`)**: errore vs RIAA ideale
  **≤ ±0,05 dB su 100 Hz-20 kHz** (target ±0,2 dB: PASS con 4× di margine);
  −0,06 dB a 50 Hz; −0,24 dB a 30 Hz; −0,83 dB a 20 Hz = sola subsonica
  SK 13 Hz (come da progetto). Requisito «−1 dB max a 30-40 Hz»: PASS.
  **Residuo v0.1 ATTRIBUITO E RISOLTO** (−0,5/−1,4/−3,9 dB a 100/50/20 Hz):
  colpevole il polo del DC block a 15,9 Hz (C3 100n + Rb2 100k), che dava
  (a) attenuazione diretta (−2,13 dB a 20 Hz, −0,42 a 50, −0,11 a 100) e
  (b) CARICO del nodo d'uscita p della rete RIAA (−1,04 dB a 20 Hz, −0,95 a
  50, −0,42 a 100: il ramo C3+Rb2 in parallelo a C1 rompe l'ipotesi di
  terminazione delle equazioni chiuse). SK assolta: −0,69 dB a 20 Hz = teoria.
  Attribution per blocco: `phono-sub100.cir` (misure di nodo s1/s2/p/p2/q/vout).
  **FIX = Rb2 100k → 1M** (polo 1,59 Hz): DC block mantenuto, interazione
  residua trascurabile. INCOERENZA CORRETTA: le netlist rumore/overload v0.1
  non avevano il polo (p collegato diretto ad A5) → EIN e warp documentati
  si riferivano già al circuito corretto; la netlist AC ora è allineata.
  Script confronto: `sim/cdj/riaa_error.py`. Indipendenza da Cload
  100/200/300 pF: ≤0,01 dB.
- **Rumore (riverificato 2026-09-30 con C3+Rb2 1M, `phono-noise-fix.cir`)**:
  la fix non cambia le densità — ma il TOTALE integrato ricalcolato con
  metodo corretto è molto più alto del claim v0.1 (vedi bullet precedente:
  EIN 1,79 µV 10-20k, out −79,8 dBu; il claim 0,36 µV/−93,6 era artefatto
  del quirk INTEG di LTspice).
- **Guadagno**: 42,0 dB a 1 kHz (out 6,13 Vpk per 48,6 mV in = +18,0 dBu
  ESATTI al punto di overload sheet); clip a 13,5 Vpk = +24,9 dBu (6,9 dB
  sopra il punto di overload).
- **Rumore (RICALCOLATO 2026-09-30 — il claim v0.1 usava `.meas INTEG`, che in
  LTspice 26.0.2 integra en²·√Δf invece di en²·Δf: tutti i totali √INTEG del
  repo sono ~21 dB ottimisti; integrazione corretta a mano dalle densità,
  `phono-noise-fix.cir` + metodo in five-way §8.9)**: EIN integrato
  10 Hz-20 kHz = **1,79 µV** (10-40 kHz = 4,61 µV: la coda ultrasonica
  dell'ingresso RIAA pesa; densità 5,4-6,1 nV/√Hz a 100-1k, 37,7 n a 40k);
  uscita blocco **79,4 µV = −79,8 dBu** (10-20k) — il fruscio del vinile sta
  ~−60 dBu: **19-20 dB sotto** (non 34). Sheet §3 ("budget dedicato Rev A"):
  il blocco phono resta dentro il suo budget con margine comodo; EIN 1,79 µV
  = classe buona per un front-end MM RIAA. La fix Rb2 1M di per sé NON cambia
  il rumore (densità identiche con e senza C3/Rb2: il polo era a 1,59/15,9 Hz,
  fuori banda di misura).
- **Warp**: 10 Hz sovrapposto a programma nominale: pulito fino a ~25 mV di
  warp; 30 mV → clip dello stadio 2 (13,5 V). Margine documentato: dischi
  molto imbarcati + volume alto = clip udibile → opzione pannello
  "subsonica profonda" (SK 18-20 Hz o 3 poli) da valutare con Filippo
  [PROVVISORIO, tocca il layout comandi q. 24]. Nota REV 2026-09-30: questi
  numeri (netlist senza polo 15,9 Hz) valgono per la topologia fixata —
  il margine warp NON cambia con la fix, era la curva AC a essere incoerente.
- Transienti: stadio 1 a 2,2 Vpk con warp 100 mV (mai in clip prima della
  subsonica) — il disegno regge il warp negli stadi bassi e limita solo
  all'uscita.

## 4. BOM per canale stereo [PROVVISORIO — regola 3]

| Voce | Qtà | Note |
|---|---|---|
| OPA1612 (dual) | 2 | stadio 1 + Sallen-Key (L/R) |
| OPA1654 (dual) | 1 | stadio 2 L/R |
| R rete RIAA 1% o meglio | 3×2 | 21,8k / 3,16k (+C 34,8n/100n PP 2%) |
| Rb2 DC block | 1×2 | **1M** (REV 2026-09-30: era 100k → polo 15,9 Hz, residuo sub-100 Hz) |
| C rete + SK PP/C0G | 8 | 34,8n, 100n×2, 100n×2 (SK), Cload switch |
| Rload 47k + switch C 100/200/300p | 1+3 | loading [PROVV. q7] |
| Switch analogico LINE/PHONO | 1 | famiglia assign FX (precision, BBM+mute) |
| RCA phono isolati + GND terminale | 2+1 | massa → stella analogue-0V (q. 21) |

Silicon: +3 dual op-amp per canale stereo rispetto al v0.3 (già a BOM
canale come "spazio variante phono", dec. 56).

## 5. Questioni toccate

- **6 → CHIUSA (decisione 79)**: topologia = stadio piatto + RIAA passiva +
  stadio piatto, subsonica SK pre-rete.
- **7 (popolazione testine)**: loading 47k || 100-300 pF [PROVVISORIO];
  simulato indipendente (≤0,01 dB); MC = variante futura separata.
- **21 (grounding)**: terminale GND phono → stella analogue-0V; loop di
  massa giradischi-mixer da trattare nel design di sistema.
- **24 (layout comandi)**: selettore LINE/PHONO + switch C load + (forse)
  subsonica profonda = 3 comandi nuovi sul pannello canale.
- **62**: confermata come scope MM-only.

## 6. Prossimi passi

1. [FATTO 2026-09-30] Residuo sub-100 Hz attribuito e risolto (§3: Rb2 1M,
   polo DC block 15,9 → 1,59 Hz; curva ≤ ±0,05 dB su 100 Hz-20 kHz, EIN
   e warp invariati — `phono-sub100*.cir`, `phono-noise-fix.cir`).
2. Integrare nel doc canale: cdj-line-channel v0.4 (§3.1bis + diagramma).
3. Banco: EIN con test inverse-RIAA, curva con generatore, warp reale.
4. MC (questione 7) quando Filippo definisce la popolazione testine.
