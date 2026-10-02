# RISULTATI simulazioni S5 CUE (2026-10-02)

Quattro netlist: `cue-hp-load.cir` (ampli cuffia su carichi reali),
`cue-blend.cir` (law blend + isolamento), `cue-blend-pol.cir` (polarità
relativa cue/MON), `cue-chain-noise.cir` (rumore catena al jack).
Metodo rumore della casa: densità `.meas FIND V(onoise) AT f` a 12 punti,
integrale trapezoidale di en² in python, MAI `.meas INTEG` (quirk 1 di
RISULTATI-module-noise-v021). A-weight: tabella IEC 61672 interpolata sui
12 punti (normalizzata 0 dB a 1 kHz).

## Test 1 — ampli cuffia (cue-hp-load) — REV 2026-10-02 sera: PRIMA VERSIONE INVALIDATA

**Storia (leggere prima dei numeri)**: la prima stesura di questa sezione
(giri del pomeriggio) era generata da un netlist col Vbe-multiplier
scritto `Qm pb nb bm`: in LTspice i pin dei BJT sono **C-B-E**, quindi
quel collegamento era C-E-B = multiplier SPENTO; il bias cadeva su una
stringa resistiva parassita → idle ~150 mA, che MASCHERAVA il crossover
e faceva leggere THD 0,009-0,055 %. Corretto il pinout (`Qm pb bm nb`),
i numeri veri sono questi e la rete di bias/limitatori è **APERTA**
(task sistema-cue-banco):

Catena: OP1612 unity (feedback su OUTA) + diamond MJE340/350, bias
Vbe-multiplier con trimmer [PROVV] + CCS JFET Idss ~8-10 mA, Re 4,7 Ω
doppi, limitatori Vbe sui Re, Rserie 10 Ω, rail ±18 V.

| Carico | Vjack pk @1,414 in | THD @1 Vrms | Vjack pk @12 Vp | I Rser pk @12 |
|---|---|---|---|---|
| corto 0,01 Ω | 1,4 mV | 1,96 % (clamp) | 11,8 mV | 1,18 A (!) |
| 16 Ω | 0,870 | 4,80 % | 7,39 V | 462 mA (!) |
| 25,8 Ω | 1,019 | 6,06 % | 8,65 V | 335 mA |
| 32 Ω | 1,077 | 6,74 % | 9,15 V | 286 mA |
| 250 Ω | 2,176 (!) | 13,48 % | 11,54 V | 46 mA |

Sintomi che dicono «rete di bias/limitatori malata», non «diamond
sbagliato»: (a) guadagno 1,53 su 250 Ω a livello basso (anello che non
chiude a corrente minima) ma unity esatto sui carichi bassi; (b)
limitatori che NON limitano a 462 mA (dovevano intervenire a ~140);
(c) idle misurato contraddittorio tra I(Vam) sul Re (~75 mA DC) e
pavimento di I(Vp) (~10 mA); (d) THD di crossover 5-13 % a 1 Vrms =
idle reale troppo basso o bias che non traccia. Il diamond nudo
(debug del pomeriggio: senza limitatori, Re 4,7, CCS) dava 0,066 %: la
colpa è nella rete attorno, non nel diamond.

**Stato: APERTO** — prossima sessione: ridisegnare bias+limitatori
(candidati: senso corrente con R dedicato e transistors con base
resistor; oppure limiter separati sul ramo di carico fuori dal nodo
emitter; oppure bias a stringa diodi+trimmer stile master-out §3.3 con
CCS), rerun Test 1 finché THD ≤0,1 % @1 Vrms su 16-250 Ω e clamp a
~140 mA verificato. I numeri di livello (partitore Rser) e il rumore
(Test 4) NON dipendono dal bias e restano validi.

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
5. **PIN DEI BJT IN LTSPICE = C-B-E, sempre**: il Vbe-multiplier scritto
   `Qm pb nb bm` era C-E-B = multiplier spento → idle parassita ~150 mA
   che MASCHERA il crossover e fa passare un Test 1 falso (THD 0,009-
   0,055 % invece di 5-13 %). Regola: dopo ogni wiring di BJT, leggere
   il punto di lavoro dei nodi di bias PRIMA di credere a una THD
   buona; una THD buona con idle incoerente è un red flag, non un
   risultato.
