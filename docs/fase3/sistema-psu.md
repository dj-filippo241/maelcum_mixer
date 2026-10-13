# Sistema PSU (q20) — v0.2 + REV 2026-10-13 (trasformatore 200 VA, dec. 98) [PROVVISORIO — regola 3; rail RATIFICATI dec. 93]

Data: 2026-10-01 (v0.2 stessa data: TASK 0 riconciliazione rail, dec. 93).
Workstream S1 del piano fase 3 (`00-piano-sistema.md`).
Base bloccata: decisione 90(c) — toroidale unico multi-avvolgimento 230 V,
regolazione LOCALE per modulo, fanless; **decisione 93 — set unico rail
raw/correnti (TASK 0 chiuso: S1↔S3↔SPECIFICA §3↔grounding allineati)**;
sheet §1 (tre famiglie di rail + +5 control); dec. 54 (LT3045/LT3094 per i
domini ultra-low-noise); master-out §3.7/[L]/[M] (mute supervisor, PSU
locale master, sizing pass).
Delta v0.2 (dec. 93): W3 ridimensionato 2×17→**2×20 V** (statici master);
LN a **due stadi** (pre-reg ±16,5 → LT3045/94 → ±15,0 V esatti — il timore
«LT3045 Vin max 15 V» era una premessa errata: Vin max **20 V**, 15 V è
l'uscita max); +5 V **regolato nella PSU** (il «+10 raw sul backplane»
della v0.1 §8 era un errore); correnti +5 riconciliate (worst 1,0 A,
dimensionamento 1,25 A); supervisor a **finestre per avvolgimento**.

## REV 2026-10-13 — trasformatore RIDIMENSIONATO (decisione 98) [sostituisce i numeri di §1 ramo audio e la tabella §2]

Due errori della v0.2, trovati riverificando il budget con i moduli MIC/MONO:

1. **Budget del ramo audio incompleto.** I 0,9 A non contavano i 4
   micro-moduli FX-SEND (dec. 91: 4×40 mA) né l'ampli cuffia v0.2 sui
   ±18 V (61 mA a riposo), e la riserva mic/mono era 50 mA contro
   ~120 mA reali con 4 moduli.
2. **Trasformatore trattato come ideale.** Le tensioni raw erano
   calcolate come Vrms×1,414, senza la resistenza degli avvolgimenti, e
   la corrente nominale del secondario era confrontata con la corrente
   DC. Con ponte e condensatore la corrente efficace nell'avvolgimento è
   ~1,9 volte la corrente DC.

**[REV 2026-10-13, dec. 105 — EQ isolator]** Il ramo audio sale a ~1,4 A (+24 quad op-amp nei 4 canali): W1 2×21 V 2,5 A va al 105-107 %. Candidato 2×21 V 3,0 A (90-92 %, raw min 23,8 V), trasformatore ~225 VA: RATIFICATO → DECISIONE 106 ( `sim/system/psu-w1-iso.cir`).

Budget del ramo audio ±18 V (per ramo, tipico): 4 canali 260 + 5-way 300
+ FX 180 + filtro 110 + 4 FX-SEND 160 + CUE 61 + MIC/MONO fino a 120
= **~1,2 A** (era 0,9).

Simulazione col trasformatore reale (`sim/system/psu-w1…w4-real.cir`:
tensione a vuoto = nominale × (1 + regolazione), resistenza equivalente
dell'avvolgimento, ponte, bulk invariati; rete −10 % / nominale / +10 %):

| Avv. | v0.2 | Esito v0.2 a rete −10 % | NUOVO | Raw min / nom / max | Requisito min | Margine | Carico avv. |
|---|---|---|---|---|---|---|---|
| W1 audio | 2×19 V 1,2 A | 19,0 V (serve ≥21,7) **FAIL**, avvolgimento al 163 % | **2×21 V 2,5 A** | 23,8 / 26,9 / 31,3 V | ≥ 21,7 V (LM317 → 19,2) | 2,1 V | 93 % |
| W2 LN/OTA | 2×17 V 0,6 A | 17,7 V (serve ≥18,5) **FAIL**, 132 % | **2×18 V 1,0 A** | 20,5 / 24,0 / 27,3 V | ≥ 18,5 V (pre-reg → 16,5) | 2,0 V | 88 % |
| W3 master HV | 2×20 V 0,3 A | 22,3 V (punto verificato 23,6) | **2×20 V 0,4 A** | 23,3 / 27,1 / 30,3 V | ≥ ~22 V per +24 dBu | vedi sotto | 78 % |
| W4 +5 V | 8 V 1,2 A | 6,6 V (serve ≥7,0) **FAIL**, 133 % | **9 V 2,0 A** | 8,5 / 10,7 / 12,7 V | ≥ 7,0 V (7805-class) | 1,5 V | 88 % |

Totale ~175 VA → **toroidale da 200 VA** (era 120 VA). Resta un
toroidale unico, fanless (dec. 90c invariata).

Conseguenze:
- I nomi dei rail restano quelli di dec. 93 (±27 audio, ±22 LN, ±26 [M],
  +5). I valori reali: audio ~27 V nominali (invariato), LN ~24 V
  (era 22), [M] ~27 V (era 26).
- Calore nei regolatori locali: ramo audio (26,9 − 19,2) × 1,2 A × 2 =
  ~18 W distribuiti sui moduli (la v0.2 ne contava ~14); pre-regolatori
  LN (24 − 16,5) × 0,34 × 2 = ~5 W (erano ~3,7).
- Master [M]: statici 23,3…30,3 V. **RIVERIFICATO in sim (Test 17,
  `sim/master-out/RISULTATI-composite.md`)**: a 23,3 V capability
  +25,1 dBu (requisito ≥ +24: PASS 1,1 dB); a 30,3 V corto 106,5 mA,
  Q1 1,34 W medi / 2,84 W di picco → rame ≥ 5 cm² per transistor
  (era ≥ 4).
- Tensione dei condensatori bulk: ≥ 35 V su W1 e W3 (già così), W2 a 35 V.
- Fusibile primario: T1,6 A → T2 A [PROVVISORIO].
- Protezione a 1,6 A per ramo e supervisor: soglie da riallineare ai
  nuovi raw (finestre per avvolgimento).

## 1. Budget assorbimenti per rail

Stime di classe dichiarate (Iq da datasheet-class, non misurati):
OPA1654 ~1,8 mA/canale (7,2/quad) · OPA1612 ~2 mA/canale · THAT 2181
~5,5 mA/chip · LM13700 ~3-5 mA/chip (2×Iabc + bias) · ADG1434 µA-class
(trascurabile) · LM3915 ~5-10 mA + LED.

| Dominio | Moduli | Idle/programma | Picco | Note |
|---|---|---|---|---|
| ±18 V audio (raw ~27 V, reg. locale) | 4× CDJ (~65 mA/canale), 5-way (~300 mA), FX (~180 mA), filtro (~110 mA), riserve mic/generic (~50) | **~0,9 A per ramo** | ~1,0 A | Iq op-amp dominante e costante; picchi di segnale su carichi ≥600 Ω = decine di mA |
| ±26 V master HV ([M], raw W3 dedicato — dec. 93) | stadio HV composite ×2 (Iq 40 mA/canale, sizing pass 0,75/1,0/2,7 W — master-out v0.3) + LDO locali ±18/±15/+5 | ~130 mA | ~170 mA (600 Ω a picco) | statici ±23,6…29,2 V su rete ±10%: il punto VERIFICATO ±23,7 V (capability +25,4…+25,6 dBu) è il worst case a rete −10% |
| ±15 V LN/OTA (raw ±22 → pre-reg LM317/337 ±16,5 → **LT3045/94 → ±15,0 V esatti** — due stadi, dec. 93/54) | filtro: 16 LM13700 (~65-100 mA; riserva (c-B) +16×2181 = +90), phono ×4 (~70), mic (~20), CV gen/dist (~40), **metering ~125** (detector ~25 + follower albero riferimenti ~100, dati S4 `sistema-metering.md` §5/§9, OP1612-class), CUE (idle ~30, picco ~90: 1 Vrms/32 Ω ×2 uscite) | ~280 mA | **~450 mA** | LT3045/94: Vin max **20 V**, Vout max 15 V, 500 mA, dropout max 0,45 V (datasheet — la premessa v0.1 «Vin max 15 V» era errata); il pre-reg ±16,5 lascia 1,5 V di headroom; il picco va DISTRIBUITO su regolatori locali per dominio (l'albero riferimenti meter ha la sua coppia LT3045/94 dedicata — nessun singolo regolatore vede 450 mA); (c-B) di q70 → +90 mA già nella riserva |
| ±15 V switch/logica | ~30 ADG1434-class (µA) + logica selettori/relay driver | <30 mA | 50 mA | 78L15/79L15 locali dal raw LN (o secondario dedicato se il banco mostra accoppiamento) |
| +5 V control | LED barre 6 zone: **~103 segmenti** (dato S4): worst 5 mA/segmento = ~0,5 A, tipico 2 mA = ~0,2 A; LM3915 V+ ×~10 (~80 mA), relay mute ×3 (~50 mA cad, eccitati in ON = failsafe: diseccitati = mute), logica supervisor/selettori (~50 mA) | ~0,55 A | **~1,0 A** (tutti i segmenti accesi + relay + logiche di modulo: LED 0,5 + LM3915 0,1 + relay 0,15 + logiche 0,25 — ricalcolo dec. 93; dimensionamento **1,25 A** = margine 25%) | regolato nel MODULO PSU (W4 → 7805/LM2940-class, dec. 93): sul backplane viaggia solo il +5 V regolato |

## 2. Trasformatore e architettura

[TABELLA SUPERATA dalla REV 2026-10-13 in testa al documento: 200 VA, secondari nuovi] Toroidale unico 230 V, **~120 VA**, schermo elettrostatico tra primario e
secondari, fusibile termico integrato, secondari [PROVVISORIO]:

| Avvolgimento | Vrms / A | VA | Destinatari |
|---|---|---|---|
| W1 2×19 V | 1,2 | 45,6 | raw audio ±27 V → LM317/337 locali ±18 (tutti i moduli audio) |
| W2 2×17 V | 0,6 | 20,4 | raw LN/OTA ±22 V → pre-reg LM317/337 ±16,5 → LT3045/94 locali → ±15,0 V (phono/mic/CV/meter/CUE/OTA filtro; due stadi dec. 93) + 78L15/79L15 ±15 switch DIRETTI dal raw (picco LN 450 mA + switch ~30: margine ~25%) |
| W3 **2×20 V** [REV dec. 93: era 2×17] | 0,3 | 12,0 | raw master HV **±26 V** ([M]: filtrato ferrite+bulk → statici 23,6-29,2 V + LDO locali; il 2×17 dava raw 22,4 V < statici ±23,7 richiesti dallo swing master-out v0.3 VERIFICATO) |
| W4 8 V | 1,2 | 9,6 | raw +10 V → 7805/LM2940-class **nel modulo PSU** → +5 V control regolato sul backplane (LED/logica/relay; bulk 10 mF, dec. 93) |
| (totale ~88 VA) | | | margine 120 VA ≈ 27% |

- Rect: ponte per avvolgimento + bulk: W1 2×10.000 µF (ripple ~0,9 V a
  1,0 A), **W2 2×10.000 µF** [REV dec. 93: 4.700 dava ripple 1,1 V e
  margine pre-reg solo 0,7 V a rete −10%; con 10 mF: 0,5 V e 1,2 V],
  W3 2×4.700 µF (ripple 0,36 V a 0,17 A), **W4 10.000 µF** [REV dec. 93:
  ripple 1,0 V a 1,0 A worst]. Raw distribuito sul backplane a
  stella (S2/S3), regolazione LOCALE per modulo (dec. 90): il calore si
  distribuisce invece di concentrarsi.
- Scelta 19 Vrms (non 18): margine dropout alla rete bassa (−10%: raw
  23,4 V − ripple 0,8 = 22,6 V > 19,2+2,5 V richiesti dall'LM317 a 0,9 A)
  restando sotto i 20 Vrms che costerebbero +20% di dissipazione.
- Rete bassa (−10%) verificata su TUTTI i raw (dec. 93): ±27 min ~22,5 V
  (LM317→19,2 chiede ≥21,7: margine 0,8-1,6 V); ±22 min ~19,7 V
  (pre-reg→16,5 chiede ≥18,5: margine 1,2 V; 78L15→15 chiede ≥17,5:
  margine 2,2 V); [M] statici min ~23,6 V: capability +25,2…+25,5 dBu
  PASS a rete −10% (VERIFICATO in sim — Test 13, master-out
  RISULTATI-composite); +10 min ~8,5 V (7805/LM2940
  chiede ≥7: margine 1,5 V). Rete alta (+10%): statici [M] ~29,2 V —
  dissipazione Q1 su corto sostenuto +28% (1,00→1,28 W medi, limite
  106 mA invariato, sempre dentro rame ≥4 cm²), capability master
  ≥+26,3 dBu (level plan worst +22 dentro).
- Regolatori locali ±18 tarati a **19,2 V pre-cap-moltiplicatore**: il
  follower (Rb 47 + Cb 10m, drop ~1,2 V) porta il modulo a ~18,0 V e
  moltiplica la reiezione al ripple (sim §9a).
- Inrush: NTC 10-20 Ω in serie primario (o relay bypass dopo 500 ms);
  fusibile primario T1,6 A + interruttore bipolare.

## 3. Sequencing e mute

Nessun sequencing attivo richiesto (tutto analogico, i transienti di
power-on sono coperti dal mute — master-out §3.7). Il supervisor [L]
(master-out) vigila i raw (W1/W2/W3) con comparatori a finestra alimentati
dal +5 control: relay mute [H]/[B4]/[C3] **failsafe diseccitati = mute**;
eccitazione dopo delay 1,5-2 s con tutti i raw in finestra. Power-off: il
bulk +5 (≥4.700 µF) tiene vivo il supervisor ~50 ms dopo il collasso raw →
rilascio pulito dei relay (niente pop). Hold-up rail ±18: 10 mF × 6,5 V
utilizzabili / 0,9 A ≈ 70 ms > tempo di rilascio relay.

## 4. Protezione abuso corto prolungato (master)

Tre strati, nessuno limita il programma:
1. **Caso di progetto** (corto uscita master auto-limitato 106 mA, Q1
   1,0 W medi): dentro il dimensionamento esistente (pass MJE340/350 su
   ≥4 cm² rame, master-out v0.3) e dentro il budget rail (0,9 A + 0,1 A):
   nessuna azione, sopravvivenza indefinita.
2. **Corto franco in un modulo**: il regolatore LOCALE (LM317/337) limita
   a ~1,5-2,2 A e va in protezione termica interna; gli altri moduli non
   sono toccati (regolazione locale = disaccoppiamento); fusibile di ramo
   T500 mA slow-blow sul raw del modulo isola il guasto persistente.
3. **Persistenza/sistema**: fusibili di ramo per modulo sul raw (canali
   T315, 5-way T630, FX T400, filtro T315, master T500 [PROVVISORIO]) +
   fusibile secondari + termico integrato nel toroidale + supervisor a
   **finestre per avvolgimento** (dec. 93): ±27 <20 V, ±22 <17 V,
   ±26[M] <21 V, +10 pre-regolatore <7 V — ciascuno per >100 ms → mute
   generale e LED fault [PROVVISORIO — soglie da raffinare a banco; la
   finestra unica 16 V della sim `psu-protect` dimostrava il meccanismo
   sull'ipotesi v0.1 a raw singolo].
Sim §9b dimostra limitazione + intervento supervisor senza trip sui
picchi di programma.

## 5. Budget termico fanless (dec. 90)

| Sorgente | Perdita | Smaltimento |
|---|---|---|
| Reg. locali ±18 (raw 27 → 19,2 V) | (26,9−19,2)×0,9 ≈ **7 W** totali, distribuiti: 5-way 2,3 W, FX 1,4 W, canali 0,5 W cad, filtro 0,8 W | piastra/rame di ciascun modulo (ognuno ≤2,5 W: TO-220 su 10-20 cm² = ΔT ~40-60 °C, ok) |
| Cap-multiplexer follower ±18 | ~1,1 V × 0,9 ≈ 1 W | stessa piastra del modulo |
| 7805/LM2940 +5 control (nella PSU, dec. 93) | (10,6−5)×1,0 ≈ **5,6 W** worst (LED al massimo + logiche) | piastra chassis dedicata ≥50 cm² o due regolatori in parallelo con R di ballast [PROVVISORIO] |
| LN due stadi: pre-reg ±16,5 + LT3045/94 | pre-reg (22−16,5)×I + LDO 1,5×I: totale picco ≈ 2,7 + 0,7 = **3,4 W** distribuiti (dominio filtro worst: ~0,4+0,3 W) | piastra/TO-220 di ciascun modulo (nessun pre-reg oltre ~1,2 W) |
| Toroidale 120 VA a ~88 VA carico | ~8-12 W propri | montaggio su piastra chassis con rondelle termiche, ΔT ~30 °C |
| **Totale chassis** | **~25-29 W** | superficie complessiva ≥800-1000 cm² di piastra/alette; verifica a banco con termocamera (task banco-modelli-reali) |

## 6. Rumore CV: 6,1 vs 61 mV/dB (nota dec. 88c) — PROPOSTA per Filippo

Analisi (sim §9c + conti):
- **Rumore intrinseco** della catena CV (LT3045 ~1 nV/√Hz + filtro RC +
  Johnson dei pot ~6 nV/√Hz su ~2,5 k equivalenti → 2-10 µV integrati): errore di
  gain 0,3-1,6 **mdB** a 6,1 mV/dB → irrilevante in entrambe le scale.
  Il tema NON è il rumore del rail, è l'immunità della LINEA CV da
  pannello (pickup hum, mV-class).
- **Worst case pickup**: 1 mV 50 Hz sulla linea CV → modulazione di gain
  ±0,164 dB (0,33 dB pp) a 6,1 mV/dB = wobble/sideband potenzialmente
  udibile su materiale sostenuto in passaggi silenziosi; a 61 mV/dB
  ±0,016 dB = inudibile (20 dB di immunità in più).
- Lo smoothing esistente (famiglia 1 ms dec. 80, fc ~160 Hz) attenua
  50 Hz solo ~3 dB: non basta da solo.

Opzioni (la scelta tocca territory dec. 82/87 validato = parola a Filippo):
- **(A) Resta 6,1 mV/dB + disciplina di routing** (twisted pair, CV gnd a
  stella, corse brevi, schermo dove lungo): zero redesign, law/trim/griglia
  drive intatte; verifica a banco (test hum→wobble) sul prototipo.
- **(B) Migra a 61 mV/dB**: guadagno ×10 su shaper/buffer CV (drive §5.2,
  position 5-way, reroute FX, gain/fader CDJ); legge musicale IDENTICA
  (si rimisura end-to-end), +20 dB immunità; costo: lavoro ingegneristico
  + re-trim, nessun cambiamento sonoro.
- **(C) Ibrido**: 61 mV/dB solo sulle corse lunghe pannello→modulo, 6,1
  in locale.
Raccomandazione ingegneria: **(A) ora, (B) come fallback documentato se il
banco mostra wobble** — i numeri validati (dec. 82/87) non si toccano senza
misura contraria. [CHIUSA 2026-10-01 → DECISIONE 92: opzione (A) 6,1 mV/dB + routing curato + test hum→wobble a banco; 61 = fallback documentato]

Rail/filtraggio CV: il dominio CV vive sul ±15 LN (sheet §1: "generatori e
distribuzione CV") con LT3045 + RC dedicato per gruppo di pot + stella CV
gnd separata dalla stella audio (S2): il rumore CV non è un tema di rail.

## 7. EMC ingresso rete

Inlet IEC con filtro integrato (X + Y 2 stadi); toroidale con schermo
elettrostatico; 0V secondari a stella sul punto di bonding chassis UNICO
(assunzione S2, da confermare in `sistema-grounding.md`); Y-cap 4,7 nF
 chassis-0V; NTC inrush; nessun switching (dec. 90) = niente RF condotta
di modo comune oltre il filtro inlet.

## 8. Conseguenze per S2/S3 (grounding/backplane)

- Backplane (dec. 93): raw ±27 (W1), ±22 (W2), **±26 [M]** (W3 solo
  master), **+5 V REGOLATO** (W4 → 7805/LM2940 nel modulo PSU — il «+10
  raw sul backplane» della v0.1 era un errore) + 0V stella;
  ±18/±16,5/±15/±15sw locali restano ON-MODULE (solo i raw viaggiano);
  correnti per ramo e pinout in S3 v0.2 §3/§6 (±27: fino a 1,1 A/lato,
  2 pin per rail).
- Grounding: punto di bonding = stella secondari sul telaio presso il
  toroidale; fusibili di ramo accessibili dall'alto (manutenzione).
- Supervisor mute: segnale OK_RAIL distribuito al modulo master ([L] vive
  lì) + eventuale override manuale di pannello (voce 40).

## 9. Simulazioni (`sim/system/psu-*.cir`)

(a) `psu-rail.cir` — raw 27,5 V + 2,5 Vpp/100 Hz → REG317 comportamentale
    19,2 V → cap-moltiplicatore → carico 0,85 A. ESITO: v18 = **18,00 V**
    a 0,849 A; ripple vreg = 5,7 µVpp, v18 = sotto il pavimento numerico
    (macro ideale senza limiti di PSRR = floor ottimista). Tetto onesto
    da datasheet (PSRR LM317 ~62 dB a 120 Hz): 2,5 Vpp → ~2 mVpp su vreg
    → cap-moltiplicatore (Xc 0,16 Ω vs Rb 47 a 100 Hz = −49 dB + follower)
    → **~7 µVpp al modulo**: target <1 mVpp PASS con >40 dB.
(b) `psu-protect.cir` — corto franco 0,5 Ω da t=0,5 s su rail con limit
    comportamentale + supervisor a finestra 16 V. ESITO: normale 18,00 V
    (0,85 A, nessun intervento); al corto: **limitazione a 1,60-1,62 A**,
    rail a 0,80 V, **supervisor flag = 0 (mute)** ✓. Il caso di progetto
    (106 mA sostenuti ≈ 1,0 A totali) sta sotto il limit: nessuna azione.
    Picchi di programma ~1,0 A: idem. Limit a 1,6 A = ~2× il programma.
    (Finestra 16 V = demo v0.1 su raw singolo: con dec. 93 il supervisor
    ha finestre per avvolgimento, §4 — meccanismo invariato, soglie da
    ritarare a banco.)
(c) `psu-cv-hum.cir` — hum 1 mV 50 Hz su CV di THAT 218x (macro law
    scalabile, finestre sugli estremi hum). ESITO: modulazione di gain
    **0,320 dB pp a 6,1 mV/dB** vs **0,032 dB pp a 61 mV/dB** (20 dB esatti,
    analitico confermato: 1 mV/6,1 mV = ±0,164 dB). Dato per la scelta
    §6: a 6,1 il wobble da pickup mV-class è nell'ordine dell'udibile su
    materiale sostenuto in passaggi silenziosi; a 61 è inudibile.

## 10. Stato e aperti

- Design PSU **v0.2** completo su architettura dec. 90/93; valori [PROVVISORIO].
- **TASK 0 CHIUSO (dec. 93, 2026-10-01)**: set unico rail raw/correnti
  ratificato — W3 2×20 V (statici master worst = punto verificato ±23,7 V),
  LN due stadi ±16,5 → LT3045/94 → ±15,0 V esatti (datasheet: Vin max 20 V,
  Vout max 15 V — dec. 54 intatta), +5 V regolato nella PSU (worst 1,0 A,
  dimensionamento 1,25 A), supervisor a finestre per avvolgimento.
  Doc allineati: SPECIFICA §1/§2/§3/§10/§12, S3 v0.2, grounding §6,
  sheet §1, master-out [M].
- Sim chiave PASS: rail 18,00 V/~7 µVpp stimati al modulo; protezione
  1,6 A + mute supervisor verificati in tran; CV hum quantificato (§6).
- CHIUSA → dec. 92: CV 6,1 mV/dB + routing curato + test banco (61 = fallback).
- Da banco: termografia chassis, test hum→wobble CV, hold-up/mute timing,
  soglie finestre supervisor, ripple/PSRR su PSU reale (task master-out-banco).
- Da S2: conferma bonding/stella; S3 v0.2: pinout raw e sezioni rame ALLINEATI (dec. 93).
- Mic/mono (dec. 97, fino a 4 moduli): ~22 mA (mic) e ~30 mA (mono) sul
  ramo audio, ~20 mA LN per mic. RIVERIFICATO 2026-10-13 → REV in testa
  al documento e decisione 98 (trasformatore 200 VA).
- Integrazione S4 metering (2026-10-01): +5 V LED 103 segmenti (worst 0,9 A
  totali) e +100 mA LN per l'albero riferimenti inseriti nel budget —
  fonte `sistema-metering.md` §5/§9.
