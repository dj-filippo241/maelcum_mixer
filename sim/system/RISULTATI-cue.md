# RISULTATI simulazioni S5 CUE (2026-10-02)

Quattro netlist: `cue-hp-load.cir` (ampli cuffia su carichi reali),
`cue-blend.cir` (law blend + isolamento), `cue-blend-pol.cir` (polarità
relativa cue/MON), `cue-chain-noise.cir` (rumore catena al jack).
Metodo rumore della casa: densità `.meas FIND V(onoise) AT f` a 12 punti,
integrale trapezoidale di en² in python, MAI `.meas INTEG` (quirk 1 di
RISULTATI-module-noise-v021). A-weight: tabella IEC 61672 interpolata sui
12 punti (normalizzata 0 dB a 1 kHz).

## Test 1 — ampli cuffia (cue-hp-load)

Catena: OP1612 unity (feedback su OUTA) + diamond MJE340/350, bias
Vbe-multiplier con stringa pilotata da CCS JFET (Idss ~8-10 mA), idle
~20 mA su Re 4,7 Ω, limitatori Vbe sui Re (~140 mA), Rserie 10 Ω verso
il jack, rail ±18 V. Livello = sorgente diretta (level pot al massimo).

| Carico | Vjack pk @1 Vrms in (atteso) | THD @1 Vrms | Vjack pk @12 Vp in | THD @12 Vp | I Rser pk |
|---|---|---|---|---|---|
| corto 0,01 Ω | 1,4 mV (clamp) | — | 1,8 mV | — | 141 / 179 mA |
| 16 Ω (2×32 par) | 0,870 (0,870) | 0,0091 % | 2,76 V (clamp) | — | 54 / 172 mA |
| 25,8 Ω (32+250 par) | 1,019 (1,019) | 0,0117 % | 4,08 V (clamp) | — | 39 / 158 mA |
| 32 Ω | 1,077 (1,078) | 0,0163 % | 4,50 V (clamp I) | — | 34 / 141 mA |
| 250 Ω | 1,360 (1,359) | 0,0549 % | 7,73 V (clip soft) | 29,6 % | 5,4 / 31 mA |

- Livello: partitore Rser/(Rser+RL) ESATTO su tutti i carichi (1 Vrms in
  → 0,762 Vrms su 32 Ω = requisito sheet ~1 Vrms con level ~90 %).
- THD a 1 Vrms ≤ 0,055 % su tutti i carichi: PASS (target < 0,1 %).
- Headroom: clip soft a 7,73 Vp jack su 250 Ω = +20,5 dBu (+14,8 dB sopra
  1 Vrms); su 32 Ω il tetto è il limitatore a 4,50 Vp = 141 mA (+12,4 dB
  sopra 1 Vrms). Programma reale (+20 dBu di picco MON, level max): dentro
  entrambi i tetti.
- Corto franco al jack: clamp 141 mA (knee morbido a ~179 mA su
  overdrive estremo). Dissipazione MJE a corto sostenuto: 141 mA × ~15 V
  ≈ 2,1 W → TO-126 su rame ≥ 4 cm² (pattern master-out); abuso prolungato
  = dominio termico/PSU, filosofia dec. 88/90.
- Corrente rail: pavimento idle+stringa ~30 mA per ramo; picco programma
  (2 jack × 32 Ω × 1 Vrms, L+R simultanei) ~136 mA + pavimento ≈ 170 mA
  per ramo; doppio corto = 340 mA (guasto, non programma). Numeri per la
  riga correnti CUE in sistema-backplane §6.

## Test 2 — law blend (cue-blend)

Due toni (cue 1 kHz, MON 1,5 kHz), `.four` con Ncycles interi (20/30 nella
finestra 20 ms). X = frazione MASTER (X=0 tutto CUE, X=1 tutto MASTER).

| X | cue (1k) | MON (1,5k) |
|---|---|---|
| 0 | 0 dB (0,5905) | −138,7 dB |
| 0,25 | −2,50 dB (0,750 esatto) | −12,04 dB (0,250) |
| 0,5 | −6,02 dB (0,500) | −6,02 dB (0,500) |
| 0,75 | −12,04 dB (0,250) | −2,50 dB (0,750) |
| 1 | −137,8 dB | 0 dB (0,5905) |

Law lineare in tensione ESATTA (pesi 1/0,75/0,5/0,25/0); centro = 50/50
con −6 dB per parte [BLOCCATO SPEC §10 confermato]. Isolamento agli
estremi −138 dB nella macro (Zo = 0): stima reale con Zo closed-loop
OP1612 a 20 kHz (~15 mΩ, T ≈ 4000) ≈ −116 dB; verifica a banco.

## Test 3 — polarità relativa cue/MON (cue-blend-pol)

Stesso programma sui due percorsi: cue entra nel summer come S, MON entra
nel buffer come −S (il summing master [A2] inverte; buffer MON
non-invertente per design).

| POL | X=0,25 | X=0,5 | X=0,75 |
|---|---|---|---|
| −1 (design) | 0,5904 (somma piena) | 0,5904 | 0,5904 |
| +1 (controllo) | 0,2952 (differenza) | 3,7e-6 (cancellazione −104 dB) | 0,2952 |

Il centro SOMMA a livello pieno con la polarità di design: nessuna
cancellazione quando si cue-a un canale già in programma. (Resta il
gruppo-di Ritardo diverso dei due percorsi: vedi sistema-cue.md §7.)

## Test 4 — rumore catena al jack (cue-chain-noise)

1 cue attivo + 3 stub aperti, blend al centro, level al massimo, jack
32 Ω. Densità PIATTA 8,50 nV/√Hz da 10 Hz a 20 kHz (nessun 1/f nella
macro, documentato in opamp-audio.inc).

- Totale 10-20k non pesato: 1,20 µVrms = −116,2 dBu.
- Totale A-wtd: 1,42 µVrms = **−114,8 dBu A-wtd** vs target ≤ −90 dBu:
  PASS con 24,8 dB di margine.
- In cuffia 32 Ω / 100 dB/mW: −102 dBm → ~−2 dB SPL: inudibile.
- Contributori dominanti (RSS a mano, coerente con 8,5 nV misurati):
  Rf summer 10k e Rin 10k (4,9 nV/√Hz ciascuno riferiti al jack),
  partitore blend al centro (4,9), level pot al max (~2,6), resto < 1.
- Lezione applicata: buffer MON SENZA resistenza serie 100k (avrebbe
  iniettato 40,7 nV/√Hz); il requisito S3 «ricevitore ≥ 100k» è
  soddisfatto dall'impedenza d'ingresso del follower (pA), col ritorno
  DC garantito dal driver d'uscita del master.

## Lezioni di metodo (da tenere)

1. **.four con N-Period di default = 1 ciclo**: con un secondo tono a
   cicli non interi nella finestra da 1 ms il leakage contamina i bin
   (law del blend letta male, THD fantasma 18-75 %). Fissare sempre
   Ncycles intero per OGNI tono presente: `.four 1k 9 20`, `.four 1.5k 9 30`.
2. **Bias del diamond da resistore al rail = starvation a uscita alta**:
   (18−12,7)/2k2 = 2,4 mA di stringa a +12 V di uscita → crossover,
   THD 5-57 % dipendente dal carico. La stringa va pilotata da CCS
   (JFET CRD Idss ~8 mA), non da resistore.
3. **Limitatori Vbe: pinout esatto o la giunzione B-C inietta nella
   stringa**: con collettore/base scambiati la B-C passa in diretta a
   0,73 V e modula il bias col segnale → THD 10-40 % sul carico basso.
   Forma corretta: NPN c=base-diamond-N, b=capo alto di Re, e=OUTA;
   PNP c=base-diamond-P, b=capo basso di Re, e=OUTA.
4. **run_ltspice.sh fallisce sui .step a valore singolo** (warning
   «only one step» → exit diverso da 0): per run singoli fissare i
   valori nel netlist, non nella lista .step.
