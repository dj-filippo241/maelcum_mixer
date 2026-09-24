# CANALE CDJ — risultati simulazioni EQ a celle di contribuzione (2026-09-24)

Riferimento design: `docs/fase1/cdj-line-channel.md` §3.3, math `sim/eq_analysis.py`
(+ `sim/eq_results.txt`). Strumento: LTspice 26.0.2 via `sim/run_ltspice.sh` (batch CLI).

Storia: primo run 2026-09-20 fallito (`.step m=2: RpotL2 Resistance must not be zero` —
il modello del pot andava a 0 ohm a fine corsa). Fix applicato lo stesso giorno in
`eq-circuit.inc` (clamp +1 mohm sulle sezioni) ma mai rieseguito. Re-run completo
2026-09-24: pulito, nessun errore. Aggiunto `eq-src.cir` (test 4) per isolare il
carico di sorgente.

## Stato dei modelli — tutto [PROVVISORIO] (regola 3)

- **OPCELL**: macromodello lineare classe OPA1654 (GBW 20 MHz, polo dominante 20 Hz,
  A0 120 dB, clamp uscita ±16,5 V = swing reale su ±18 V). Rumore via resistenza
  equivalente 2,2 kohm (~6 nV/rtHz [DA VERIFICARE su datasheet]).
- **OPSUM**: stessa struttura, classe OPA1612 (GBW 80 MHz, 73 ohm = 1,1 nV/rtHz).
- Macromodelli lineari: THD non misurabile; clamp duro invece della saturazione
  morbida reale (i test livelli vanno letti come "tocca il rail", non come carattere
  del clipping).
- Pot: due sezioni resistive + clamp 1 mohm (vedi storia). err = mismatch dei percorsi
  ±H e del riferimento: 0 = ideale, 0,002 = resistori 0,1%, 0,02 = 1%.
- Sorgente: 100 ohm serie (ipotesi conservativa di uscita del blocco GAIN/VCA).

## FINDING 1 [CRITICO → questione 62] — la fase dei filtri smentisce la math validata

`eq_analysis.py` modellava LOW e HIGH come **magnitudine a zero-fase**
(`1/sqrt(1+x^4)`, righe 23/27 — valore reale); le bande MID erano invece complesse
(riga 30, corrette). La simulazione lo conferma con una prova incrociata: dove la
math aveva la fase, SPICE combacia (all-kill @150 Hz: math −2,64 dB, SPICE −2,67 dB);
dove la math la ignorava, SPICE diverge. Non è un bug del netlist: è la math che era
ottimista.

Griglia AC misurata, err=0 (dB; ideale = `sim/eq_results.txt`):

| Modo | Freq | Ideale | SPICE | Nota |
|---|---|---|---|---|
| detent | 20 Hz…35 kHz | 0,00 piatto | −0,20…−0,82 | droop = carico sorgente (test 4) |
| detent, sorgente 1 ohm | tutta la banda | 0,00 piatto | **±0,005** | cancellazione esatta CONFERMATA |
| LOW boost | 20 Hz | +6,01 | +5,62 | −0,4 = carico sorgente |
| LOW boost | 70 Hz | +4,65 | +1,57 | fase a −90° dimezza il boost al centro |
| LOW boost | 150 Hz | +1,68 | **−1,73** | il boost TAGLIA sopra il centro |
| LOW kill | 20 Hz | −49,6 | **−8,0** | profondità persa: 40 dB |
| LOW kill | 70 Hz | −10,7 | **+1,5** | bump positivo: il kill alza |
| LOW kill | picco banda | ~0 | **+1,8** | gmax del modo kill |
| all-kill | picco leak | −2,6 | **−0,67** | questione 59 peggiorata |
| all-kill | 35 kHz | −30,1 | −10,1 | |
| all-boost | picco | +6,64 | +5,86 | level plan §4 da correggere |
| all-boost | 5 kHz | +4,89 | **−0,06** | boost HIGH nullo al centro |

Sweep mismatch (0 → 0,1% → 1%): variazioni ≤0,2 dB su tutti i modi. **Il matching non
è il problema**: il pavimento del kill è fisico, non resistivo. La raccomandazione
§3.3 "0,1% per pavimento −60 dB" è priva di fondamento (i −60 dB non esistono).

### Perche' (fisica, in breve)

La cella sottrae: V_out = V_in·(1 − k·H). Il profondo si ha solo dove H ≈ 1 con fase
≈ 0°. Un Butterworth di 2° ordine a 20 Hz (fc 70 Hz) ha già −23° di fase: il residuo
è ~0,4 → −8 dB, e al centro (fase −90°) la sottrazione diventa un bump (+1,5 dB).
Nessun componente reale può risolverlo: |H| a fase zero non è una funzione razionale
realizzabile. Vale per qualunque cella sottrattiva con filtri classici.

### Conseguenza musicale (da mostrare a Filippo — regola 2)

- Il kill del LOW (gesto dub fondamentale) non toglie il basso: lo lascia a −8 dB
  e ALZA di 1,5 dB la zona 70-150 Hz. Suonare "cassa secca" diventa "cassa con
  gobba a 70 Hz".
- Il boost del LOW scava 150 Hz invece di estendere lo shelf.
- Il boost dell'HIGH a 5 kHz sparisce (~0 dB invece di +4,9).
- I medi funzionano solo al centro esatto (kill = notch stretto).
- Il requisito locked §1 "−∞ → 0 → +6 per banda" NON è realizzabile con questa
  topologia per LOW/HIGH. Va cambiata la topologia (questione 62, opzioni A-D).

## FINDING 2 [moderato, ingegneristico] — carico di sorgente (test 4, eq-src.cir)

Detent con sorgente 1 ohm: piatto ±0,005 dB (10 Hz-40 kHz). Con 100 ohm: −0,20 dB
@20 Hz → −0,82 dB @35 kHz, monotono. Causa: l'impedenza d'ingresso della rete EQ
(~6,6 kohm a LF, dominata da Chi1 10n a HF) partiziona con Rsrc. Non è un problema
delle celle: si risolve a monte. Regola di design: **l'EQ va pilotata da bassa
impedenza (≤10 ohm → droop ≤0,1 dB)** — verificare l'impedenza d'uscita reale del
blocco GAIN (VCA THAT 2181 + stadio seguente), oppure scalare le impedenze della
cella ×10 (rumore ×3,2: il budget ha 33 dB di margine, fattibile). Da decidere
nell'EQ v0.3 insieme alla topologia (questione 62).

## Test 2 — Livelli (eq-levels.cir, all-boost, transient 100-200 ms)

| Config | Ingresso | Out picco | Nodo interno max | Esito |
|---|---|---|---|---|
| 1: 1 kHz +16 dBu (max programma normale) | 6,93 Vp | ±13,60 V | MH ±6,54 V | pulito, 2,9 V al clamp |
| 2: 1 kHz +18 dBu (user error estremo) | 8,69 Vp | ±16,50 V (clamp) | MH ±8,21 V | satura in uscita |
| 3: 20 Hz +18 dBu (estremo infrasub) | 8,69 Vp | ±16,50 V (clamp) | LOW ±8,47 V | satura in uscita |

- Il caso normale worst (+16 dBu, tutte le bande a +6) passa pulito con margine.
- L'estremo (sine continua +18 dBu + all-boost = +24 dBu teorici) tocca il rail:
  territorio "saturazione intenzionale" del gain-staging sheet §2 — coerente con la
  filosofia, e con programma reale (crest ≥10 dB) non accade quasi mai. Il clamp del
  macromodello è duro; l'op-amp reale satura morbido (da verificare col modello TI).
- Nessun nodo interno clippa prima dell'uscita (max 8,5 V = metà clamp): il level
  plan regge, la saturazione avviene solo sullo stadio finale di summing.
- Correzione level plan §4: il worst boost reale è +5,9 dB (non +6,64 della math
  zero-fase) → post-EQ estremo teorico +23,9 dBu, ma il rail (±16,5 V = +23,5 dBu)
  fa da tetto prima. Coerente con la discussione della questione 60.

## Test 3 — Rumore (eq-noise.cir, detent, 20 Hz-20 kHz) [PASS]

- Integrato: sqrt(1,985e-13) = **0,45 µVrms = −124,8 dBu** (non pesato).
- Densità @1 kHz: 37,5 nV/rtHz.
- Target sheet §3: ≤−92 dBu A-wtd → **margine ~33 dB**. PASS largo.
- Include termica di tutti i resistori/pot e rumore equivalente dei 10 op-amp.
  Mancano: rumore in corrente (trascurabile su sorgente bassa Z) e contributo VCA
  di gain (a monte). Ordine di grandezza valido anche se cambia la topologia
  (domina il nodo di summing).

## Riepilogo esiti

| Test | Esito |
|---|---|
| Detent piatto esatto (proprietà 1 §3.3) | CONFERMATO (±0,005 dB con sorgente bassa Z) |
| Boost +6,02 al centro (proprietà 2) | SOLO LOW profondo in banda; HIGH ~0 dB al centro; LOW scavato a 150 Hz |
| Kill profondo (proprietà 3) | FALSO per LOW/HIGH (−8 dB + bump); MID = notch stretto |
| Worst boost +6,64 (proprietà 4) | +5,9 reale (meglio per headroom) |
| All-kill leak −2,6 dB (proprietà 5 / questione 59) | −0,67 dB reale (peggio) |
| Rumore | PASS −124,8 dBu (target −92) |
| Livelli normali | PASS (2,9 V margine); estremo = clamp voluto |
| Matching 0,1% vs 1% | Irrilevante (≤0,2 dB) — il pavimento è la fase |

## Azioni generate

1. Questione 62 (topologia EQ LOW/HIGH) → decisione di Filippo: opzioni A (bande
   parallele LR + VCA), B (EQ in serie classe Baxandall), C (tenere + limiti),
   D (compensazione allpass). Vedi `docs/02-questioni-aperte.md`.
2. Questione 59: ratifica SOSPESA in attesa della 62 (numeri aggiornati).
3. Questione 53 (tracking): il mismatch resistivo conta poco; resta il tracking
   meccanico dei pot doppi. Da rivalutare con la nuova topologia.
4. §3.3 e §4 di `docs/fase1/cdj-line-channel.md`: marcati/corretti.
5. EQ v0.3 dopo la decisione 62: includere impedenza di pilotaggio (finding 2).

## Riproduzione

```bash
sim/run_ltspice.sh sim/cdj-eq/eq-ac.cir      # 5 modi x 3 matching (~1 min/run)
sim/run_ltspice.sh sim/cdj-eq/eq-levels.cir
sim/run_ltspice.sh sim/cdj-eq/eq-noise.cir
sim/run_ltspice.sh sim/cdj-eq/eq-src.cir     # detent: Rsrc 1 vs 100 ohm
# risultati nei .log accanto ai netlist
```
