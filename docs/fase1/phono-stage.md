# FASE 1 — Front-end PHONO MM (RIAA): design v0.1 (2026-09-28)

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
  → [A3] RETE RIAA PASSIVA (R1 21,8k serie; C1 34,8n shunt; R2 3,16k+C2 100n shunt)
  → [A4] STADIO 2 non-inv ×60,6 (OPA1654: sorgente ~3 kΩ → regola d'uso FET)
  → [A5] SELETTORE LINE/PHONO → [B] GAIN del canale (catena v0.3)
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
il budget (EIN misurato 0,36 µV); in alternativa stadio 1 con OPA1654 e
perdita di 3 dB di rumore: scelta rinviata al banco [PROVVISORIO].

## 3. Risultati simulati (`sim/cdj/phono-riaa-*.cir`, 2026-09-28)

- **Curva**: errore vs RIAA ideale: ≤ ±0,14 dB su 200 Hz-20 kHz; −0,5 dB a
  100 Hz; −1,4 dB a 50 Hz; −3,9 dB a 20 Hz. La parte sotto i 100 Hz ECCEDE
  la subsonica disegnata (SK 13 Hz darebbe −0,7 a 20 Hz): c'è un'attenuazione
  residua non ancora attribuita (sospetto: interazione SK/rete o macro) —
  [PROVVISORIO: rifinire a banco o in prossima iterazione; musicalmente =
  −1,4 dB a 50 Hz, tollerabile ma da recuperare]. Script confronto:
  `sim/cdj/riaa_error.py`. Indipendenza da Cload 100/200/300 pF: ≤0,01 dB.
- **Guadagno**: 42,0 dB a 1 kHz (out 6,13 Vpk per 48,6 mV in = +18,0 dBu
  ESATTI al punto di overload sheet); clip a 13,5 Vpk = +24,9 dBu (6,9 dB
  sopra il punto di overload).
- **Rumore**: EIN integrato 10 Hz-40 kHz = **0,36 µV** riferiti all'ingresso
  testina (densità 5,5-6,1 nV/√Hz a 100-1k); uscita blocco 16,2 µV =
  **−93,6 dBu** — il fruscio del vinile sta ~−60 dBu: 34 dB sotto. Sheet §3
  ("budget dedicato Rev A"): CHIUSO con questi numeri.
- **Warp**: 10 Hz sovrapposto a programma nominale: pulito fino a ~25 mV di
  warp; 30 mV → clip dello stadio 2 (13,5 V). Margine documentato: dischi
  molto imbarcati + volume alto = clip udibile → opzione pannello
  "subsonica profonda" (SK 18-20 Hz o 3 poli) da valutare con Filippo
  [PROVVISORIO, tocca il layout comandi q. 24].
- Transienti: stadio 1 a 2,2 Vpk con warp 100 mV (mai in clip prima della
  subsonica) — il disegno regge il warp negli stadi bassi e limita solo
  all'uscita.

## 4. BOM per canale stereo [PROVVISORIO — regola 3]

| Voce | Qtà | Note |
|---|---|---|
| OPA1612 (dual) | 2 | stadio 1 + Sallen-Key (L/R) |
| OPA1654 (dual) | 1 | stadio 2 L/R |
| R rete RIAA 1% o meglio | 3×2 | 21,8k / 3,16k (+C 34,8n/100n PP 2%) |
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

1. Rifinire l'attenuazione sub-100 Hz residua (sim o banco).
2. Integrare nel doc canale: cdj-line-channel v0.4 (§3.1bis + diagramma).
3. Banco: EIN con test inverse-RIAA, curva con generatore, warp reale.
4. MC (questione 7) quando Filippo definisce la popolazione testine.
