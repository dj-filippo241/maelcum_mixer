# Sistema PSU (q20) — v0.1 [PROVVISORIO — regola 3]

Data: 2026-10-01. Workstream S1 del piano fase 3 (`00-piano-sistema.md`).
Base bloccata: decisione 90(c) — toroidale unico multi-avvolgimento 230 V,
regolazione LOCALE per modulo, fanless; sheet §1 (tre famiglie di rail +
+5 control); dec. 54 (LT3045/LT3094 per i domini ultra-low-noise);
master-out §3.7/[L]/[M] (mute supervisor, PSU locale master, sizing pass).

## 1. Budget assorbimenti per rail

Stime di classe dichiarate (Iq da datasheet-class, non misurati):
OPA1654 ~1,8 mA/canale (7,2/quad) · OPA1612 ~2 mA/canale · THAT 2181
~5,5 mA/chip · LM13700 ~3-5 mA/chip (2×Iabc + bias) · ADG1434 µA-class
(trascurabile) · LM3915 ~5-10 mA + LED.

| Dominio | Moduli | Idle/programma | Picco | Note |
|---|---|---|---|---|
| ±18 V audio (raw ~27 V, reg. locale) | 4× CDJ (~65 mA/canale), 5-way (~300 mA), FX (~180 mA), filtro (~110 mA), riserve mic/generic (~50) | **~0,9 A per ramo** | ~1,0 A | Iq op-amp dominante e costante; picchi di segnale su carichi ≥600 Ω = decine di mA |
| ±24/25 V master HV ([M]) | stadio HV composite ×2 (Iq 40 mA/canale, sizing pass 0,75/1,0/2,7 W — master-out v0.3) + LDO locali ±18/±15/+5 | ~130 mA | ~170 mA (600 Ω a picco) | avvolgimento dedicato |
| ±15/16 V LN/OTA (raw ~22 V, LT3045/94 locali) | filtro: 16 LM13700 (~65-100 mA; riserva (c-B) +16×2181 = +90), phono ×4 (~70), mic (~20), CV gen/dist (~40), **metering ~125** (detector ~25 + follower albero riferimenti ~100, dati S4 `sistema-metering.md` §5/§9, OP1612-class), CUE (idle ~30, picco ~90: 1 Vrms/32 Ω ×2 uscite) | ~280 mA | **~450 mA** | LT3045/94 max 500 mA: il picco va DISTRIBUITO su regolatori locali per dominio (l'albero riferimenti meter ha la sua coppia LT3045/94 dedicata — nessun singolo regolatore vede 450 mA); (c-B) di q70 → +90 mA già nella riserva |
| ±15 V switch/logica | ~30 ADG1434-class (µA) + logica selettori/relay driver | <30 mA | 50 mA | 78L15/79L15 locali dal raw LN (o secondario dedicato se il banco mostra accoppiamento) |
| +5 V control | LED barre 6 zone: **~103 segmenti** (dato S4): worst 5 mA/segmento = ~0,5 A, tipico 2 mA = ~0,2 A; LM3915 V+ ×~10 (~80 mA), relay mute ×3 (~50 mA cad, eccitati in ON = failsafe: diseccitati = mute), logica supervisor/selettori (~50 mA) | ~0,5 A | **~0,9 A** (tutti i segmenti accesi + relay) | alimentato da W4 via 7805 |

## 2. Trasformatore e architettura

Toroidale unico 230 V, **~120 VA**, schermo elettrostatico tra primario e
secondari, fusibile termico integrato, secondari [PROVVISORIO]:

| Avvolgimento | Vrms / A | VA | Destinatari |
|---|---|---|---|
| W1 2×19 V | 1,2 | 45,6 | raw audio ±27 V → LM317/337 locali ±18 (tutti i moduli audio) |
| W2 2×17 V | 0,6 | 20,4 | raw LN/OTA ±22 V → LT3045/94 locali (phono/mic/CV/meter/CUE/OTA filtro) + 78L15/79L15 ±15 switch (picco LN 450 mA + switch ~30: margine ~25%) |
| W3 2×17 V | 0,3 | 10,2 | raw master HV ±24 ([M]: filtrato + LDO locali) |
| W4 8 V | 1,2 | 9,6 | raw +10 V → 7805 +5 control (LED/logica/relay) |
| (totale ~86 VA) | | | margine 120 VA ≈ 40% |

- Rect: ponte per avvolgimento + bulk: W1 2×10.000 µF (ripple ~0,75 V a
  0,9 A), W2/W3 2×4.700 µF, W4 4.700 µF. Raw distribuito sul backplane a
  stella (S2/S3), regolazione LOCALE per modulo (dec. 90): il calore si
  distribuisce invece di concentrarsi.
- Scelta 19 Vrms (non 18): margine dropout alla rete bassa (−10%: raw
  23,4 V − ripple 0,8 = 22,6 V > 19,2+2,5 V richiesti dall'LM317 a 0,9 A)
  restando sotto i 20 Vrms che costerebbero +20% di dissipazione.
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
   fusibile secondari + termico integrato nel toroidale + supervisor:
   raw <16 V per >100 ms → mute generale e LED fault.
Sim §9b dimostra limitazione + intervento supervisor senza trip sui
picchi di programma.

## 5. Budget termico fanless (dec. 90)

| Sorgente | Perdita | Smaltimento |
|---|---|---|
| Reg. locali ±18 (raw 27 → 19,2 V) | (26,9−19,2)×0,9 ≈ **7 W** totali, distribuiti: 5-way 2,3 W, FX 1,4 W, canali 0,5 W cad, filtro 0,8 W | piastra/rame di ciascun modulo (ognuno ≤2,5 W: TO-220 su 10-20 cm² = ΔT ~40-60 °C, ok) |
| Cap-multiplexer follower ±18 | ~1,1 V × 0,9 ≈ 1 W | stessa piastra del modulo |
| 7805 +5 control | (10,7−5)×0,9 ≈ **5,1 W** worst (LED al massimo) | piastra chassis dedicata ≥50 cm² o due 7805 in parallelo con R di ballast [PROVVISORIO] |
| LT3045/94 LN (picco CUE) | (22−15)×0,25 ≈ 1,8 W picco | TO-220 + aletta modulo CUE |
| Toroidale 120 VA a ~83 VA carico | ~8-12 W propri | montaggio su piastra chassis con rondelle termiche, ΔT ~30 °C |
| **Totale chassis** | **~22-27 W** | superficie complessiva ≥700-900 cm² di piastra/alette; verifica a banco con termocamera (task banco-modelli-reali) |

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

- Backplane: raw ±27 (W1), ±22 (W2), ±24 (W3 solo master), +10 (W4) +
  0V stella + ±18/±15/±5 locali restano ON-MODULE (solo i raw viaggiano);
  correnti per ramo nel pinout S3 (W1 fino a 1 A per lato: 2 pin paralleli
  o tracce ≥2 mm²).
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
(c) `psu-cv-hum.cir` — hum 1 mV 50 Hz su CV di THAT 218x (macro law
    scalabile, finestre sugli estremi hum). ESITO: modulazione di gain
    **0,320 dB pp a 6,1 mV/dB** vs **0,032 dB pp a 61 mV/dB** (20 dB esatti,
    analitico confermato: 1 mV/6,1 mV = ±0,164 dB). Dato per la scelta
    §6: a 6,1 il wobble da pickup mV-class è nell'ordine dell'udibile su
    materiale sostenuto in passaggi silenziosi; a 61 è inudibile.

## 10. Stato e aperti

- Design PSU v0.1 completo su architettura dec. 90; valori [PROVVISORIO].
- Sim chiave PASS: rail 18,00 V/~7 µVpp stimati al modulo; protezione
  1,6 A + mute supervisor verificati in tran; CV hum quantificato (§6).
- CHIUSA → dec. 92: CV 6,1 mV/dB + routing curato + test banco (61 = fallback).
- Da banco: termografia chassis, test hum→wobble CV, hold-up/mute timing.
- Da S2: conferma bonding/stella; da S3: pinout raw e sezioni rame.
- Mic/generic non disegnati: riserva 50 mA nel budget (aggiornare quando
  esistono).
- Integrazione S4 metering (2026-10-01): +5 V LED 103 segmenti (worst 0,9 A
  totali) e +100 mA LN per l'albero riferimenti inseriti nel budget —
  fonte `sistema-metering.md` §5/§9.
