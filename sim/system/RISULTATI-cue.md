# RISULTATI simulazioni S5 CUE (2026-10-02)

Netlist: `cue-hp-load.cir` (ampli cuffia su carichi reali) + `cue-hp-idle/step/ac/20k.cir`
(riposo, stabilità, risposta, 20 kHz: Test 5-8, 2026-10-12),
`cue-blend.cir` (law blend + isolamento), `cue-blend-pol.cir` (polarità
relativa cue/MON), `cue-chain-noise.cir` (rumore catena al jack).
Metodo rumore della casa: densità `.meas FIND V(onoise) AT f` a 12 punti,
integrale trapezoidale di en² in python, MAI `.meas INTEG` (quirk 1 di
RISULTATI-module-noise-v021). A-weight: tabella IEC 61672 interpolata sui
12 punti (normalizzata 0 dB a 1 kHz).

## Test 1 — ampli cuffia (cue-hp-load) — v0.2 CHIUSO 2026-10-12

**Storia (leggere prima dei numeri).** Tre stesure:

1. *02/10 pomeriggio — INVALIDATA.* Netlist col Vbe-multiplier scritto
   `Qm pb nb bm` (C-E-B: in LTspice i pin sono C-B-E) = multiplier
   spento, idle parassita ~150 mA, THD letta 0,009-0,055 %, clamp 141 mA.
2. *02/10 sera (REV 1) — numeri veri, DIAGNOSI SBAGLIATA.* Corretto il
   pinout: «THD 4,8-13,5 % @1 Vrms, guadagno 1,53 su 250 Ω, clamp
   assente (462 mA), idle incoerente», attribuiti a crossover/bias.
3. *12/10 (REV 2) — diagnosi corretta.* Review dei log e rerun a passo
   fine (5 ns):
   - le armoniche 2-9 erano PULITE (Partial 0,0007-0,010 %): il 5-13 %
     era la riga «Total» di LTspice, che conta tutto il residuo;
   - il residuo era un'**oscillazione RF a burst** (~53 MHz, ±0,5 V su
     OUTA, uscita op-amp fino a −11 V) SOLO attorno ai passaggi per lo
     zero; fuori da lì l'errore OUTA−IN era 0,00 V. Non un artefatto
     numerico: 6,72 % a passo 5 ns contro 6,74 % a 5 µs;
   - il «guadagno 1,53 su 250 Ω» non esisteva: fondamentale 1,360 V =
     1,414 × 250/260, unity esatto; il picco 2,18 V era nota + burst;
   - l'«idle incoerente» era la media delle correnti RF;
   - cause, tutte nella rete: (a) l'op-amp pilotava a impedenza zero il
     nodo BASE del multiplier: con Qm interdetto il nodo inferiore
     saliva di 8 mA × Rb = 8 V rispetto all'op-amp (rete non
     funzionante come spreader); (b) nessuna compensazione: un op-amp
     da 80 MHz chiuso a guadagno 1 attorno a un follower discreto;
     (c) limitatori senza resistenza di pilotaggio: contro una sorgente
     ideale non possono limitare (la macro OP1612 non ha limite di
     corrente). I 150 mA della stesura 1 mascheravano l'INSTABILITÀ,
     non il crossover.

**Rete v0.2** (netlist `cue-hp-*.cir`): OP1612 gain +1 con feedback DC
Rf 470 Ω da OUTA e compensazione Cf 330 pF uscita→ingresso invertente
(crossover anello esterno ~1 MHz); Rdrv 1 kΩ tra op-amp e rete di bias;
Vbe-multiplier vero tra le basi (C=pb, B=tap, E=nb; Ra 1 k + trimmer
500 Ω, Rb 1 k) con bypass Cb 1 µF e CCS JFET ~8 mA sopra e sotto; base
stopper 22 Ω; finali MJE340/350 con Re 6,8 Ω; limitatori Vbe sui Re
con 100 Ω in base; Rserie 10 Ω fuori anello; rail ±18 V.

1 Vrms in ingresso (1,414 Vp), 1 kHz, passo 50 ns:

| Carico | Vjack pk | THD Partial | THD Total | max \|OUTA−IN\| |
|---|---|---|---|---|
| 16 Ω | 0,870 | 0,0052 % | 0,0052 % | 1,2 mV |
| 25,8 Ω | 1,019 | 0,0013 % | 0,0013 % | 1,0 mV |
| 32 Ω | 1,077 | 0,0008 % | 0,0008 % | 0,9 mV |
| 250 Ω | 1,360 | 0,00002 % | 0,00015 % | 0,5 mV |

Acceptance THD ≤0,1 % su 16-250 Ω: **PASS** (margine ≥ 19×); Total =
Partial = nessun contenuto non armonico.

Al limite (12 Vp in ingresso):

| Carico | Vjack pk +/− | I uscita pk +/− | P media Q1 |
|---|---|---|---|
| corto 0,01 Ω | — | 168 / 151 mA | 0,93 W |
| 16 Ω | 2,27 / 2,20 V | 142 / 138 mA | 0,76 W |
| 25,8 Ω | 3,38 / 3,34 V | 131 / 130 mA | 0,69 W |
| 32 Ω | 4,03 / 3,91 V | 126 / 122 mA | 0,65 W |
| 250 Ω | 11,54 / 10,89 V | 46 / 44 mA | 0,25 W |

Clamp verificato: **126-142 mA sui carichi reali, 168 mA in corto
franco** (target ~140: PASS; il limitatore è morbido, parte da ~110 mA).
Massimo pulito su 32 Ω: 2,67 Vp al jack con THD 0,007 % (83 mA); clip
di corrente a ~4,0 Vp = 2,85 Vrms = 254 mW. Su 250 Ω pulito fino a
8,65 Vp (THD 0,0002 %); a 12 Vp il semiperiodo negativo si ferma a
−10,9 V (corrente dei CCS attraverso Rdrv). Dissipazione: idle 0,35 W
per finale; corto DC sostenuto = 18 V × 0,17 A ≈ 3,0 W (dominio termico,
come master-out v0.3).

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

## Test 4 — rumore catena al jack (cue-chain-noise) — rerun v0.2 2026-10-12

1 cue attivo + 3 stub aperti, blend al centro, level al massimo, jack
32 Ω, ampli cuffia v0.2. Densità PIATTA **8,76 nV/√Hz** da 10 Hz a
20 kHz (v0.1: 8,50; +0,26 dB = Rf 470 Ω e Rdrv della rete nuova).

- Totale 10-20k non pesato: 1,24 µVrms = −115,9 dBu.
- A-wtd col metodo della casa (stessa tabella della v0.1, scalata sul
  rapporto di densità): **−114,5 dBu A-wtd** vs target ≤ −90: PASS con
  24,5 dB di margine.
- NOTA DI METODO APERTA: il rerun con la formula analitica IEC 61672
  sugli stessi 12 punti dà −118,0 dBu A-wtd. Il valore della casa è
  quindi ~3 dB PESSIMISTA (un rumore bianco pesato A deve stare ~2 dB
  SOTTO il non pesato, non sopra). Margine reale maggiore; la tabella
  A-weight usata nella campagna 71A va riverificata (non cambia nessun
  PASS: l'errore è dal lato sicuro).
- In cuffia 32 Ω / 100 dB/mW: ~−2 dB SPL: inudibile.
- Contributori dominanti invariati: Rf summer 10k, Rin 10k, partitore
  blend al centro (4,9 nV/√Hz ciascuno), level pot al max (~2,6).
- Lezione applicata: buffer MON SENZA resistenza serie 100k.

## Test 5 — idle vs trimmer e temperatura (cue-hp-idle) — 2026-10-12

Ingresso a zero; multiplier e finali alla stessa temperatura.

| Trimmer | 27 °C | 50 °C | 75 °C |
|---|---|---|---|
| 0 Ω | 11,1 mA | 11,6 | 12,1 |
| 100 Ω | 15,2 | 15,5 | 15,8 |
| **210 Ω (nominale)** | **19,99** | **19,96** | **19,93** |
| 300 Ω | 24,0 | 23,8 | 23,5 |
| 500 Ω | 33,3 | 32,5 | 31,6 |

Idle nominale 20 mA a metà corsa, deriva ±0,03 mA su 48 °C. Coerenza
tra misure: I(Vp) = 30,6 mA = idle 20,0 + CCS J1 10,6 (Idss 8 mA ×
(1 + λ·Vds)): **l'idle torna tra le due letture**.

## Test 6 — onda quadra e carico capacitivo (cue-hp-step) — 2026-10-12

Quadra 10 kHz, fronti 100 ns, 32 Ω, capacità AL JACK (dietro Rserie):

| C al jack | ±50 mV | ±1 V |
|---|---|---|
| 0 | 0 % sovraelong., 0,46 µs | 0 %, 0,47 µs |
| 2 nF (cavo ≥ 7 m) | 0 %, 0,27 µs | 0 %, 0,27 µs |
| 22 nF (abuso) | 17 %, 1,6 µs | 13 %, 1,1 µs |

Nessuno squillo sostenuto in nessun caso. Fuori netlist (prova in
area temporanea): C direttamente su OUTA 1 nF → 24 %, 10 nF → 79 %
smorzato in 45 µs: **mai capacità su OUTA prima della Rserie** (vincolo
di layout).

## Test 7 — risposta ad anello chiuso (cue-hp-ac) — 2026-10-12

16 punti: carico 16/32/250/100k × polarizzazione DC 0/0,03/0,3/1,5 V.
**Picco massimo 0,000 dB** (roll-off monotono ovunque), −3 dB tra
0,94 MHz (16 Ω) e 31,6 MHz (a vuoto); a 20 kHz −0,001…−0,004 dB.

## Test 8 — 20 kHz a 1 Vrms (cue-hp-20k) — informativo

| Carico | THD (Partial = Total) |
|---|---|
| 16 Ω | 0,105 % |
| 32 Ω | 0,015 % |
| 250 Ω | 0,0004 % |

A 20 kHz il guadagno d'anello è ~50 (crossover 1 MHz): il prezzo della
stabilità. Armoniche a 40 kHz e oltre = fuori banda udibile; **ACCETTATO
da Filippo (decisione 96: standard classe cuffie DJM, non audiofilo)**. Leva documentata se servisse: Cf più
piccolo (crossover più alto) da rivalidare coi Test 6-7.

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
6. **THD: leggere SEMPRE Partial E Total** (2026-10-12). `.four` di
   LTspice stampa due righe: Partial = armoniche elencate, Total =
   tutto il residuo. Total ≫ Partial NON è distorsione armonica: è
   contenuto non armonico (oscillazione RF, toni estranei, leakage).
   Davanti a quel divario: guardare la forma d'onda e la misura
   `MAX abs(V(out)-V(in))` prima di parlare di crossover.
7. **Mai un op-amp veloce a guadagno 1 attorno a un buffer discreto
   senza compensazione, né un op-amp sul nodo base di un multiplier.**
   Pattern v0.2: Rdrv tra op-amp e rete di bias, Rf + Cf per il
   crossover dell'anello esterno, multiplier tra le basi con bypass.
8. **La macro OP1612 non ha limite di corrente**: ogni test di clamp
   che lasci l'op-amp pilotare la rete senza resistenza è falso per
   costruzione. E `.meas MAX db(...)` su dati `.ac` complessi dà
   numeri non interpretabili: il modulo si legge dal `.raw`.
