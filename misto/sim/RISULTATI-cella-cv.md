# MISTO — cella CV del FX-RET: risultati [PROVVISORIO]

Data: 2026-11-09 (todo 278). Fa i punti 1 e 2 di misto/03 §8.

File:

- `misto/script/firmware_fxret.py`: modello del firmware e prove R1-R7. Con `--pwl`
  scrive anche l'uscita del DAC nel tempo (`misto/sim/pwl/`, fuori da git).
- `misto/sim/cella-cv-gradini.cir`: gradini del DAC, 3 gesti × 4 modi di scrittura.
- `misto/sim/cella-cv-rumore.cir`: rumore al pin EC− con tre uscite della cella.

Cella simulata (03 §4.3): DAC 0…2,5 V → invertente con offset da −REF5, C su Rf
(10k × 100n = τ 1 ms) → uscita → pin EC−. V_pin = 0,80 − 0,34·V_dac: codice zero
= +0,80 V = VCA chiuso. Op-amp OP1654 (FET: Rin e Ro sono decine di kΩ).

## 1. Gradini del DAC (`cella-cv-gradini.cir`)

I quattro modi di scrittura:

- **ideale**: la law continua, senza gradini (la catena analogica di oggi);
- **zoh1k**: ADC e DAC a 1 kHz;
- **zoh8k**: ADC e DAC a 8 kHz;
- **int8k**: ADC a 2 kHz, DAC a 8 kHz con interpolazione lineare (proposta di 03 §4.3).

Ondulazione della CV al pin durante il gesto (passa-alto 2 poli a 300 Hz; 6,1 mV = 1 dB).
Il valore «ideale» è la forma del gesto stesso: conta solo l'eccesso.

| Gesto | ideale | zoh1k | zoh8k | int8k |
|---|---|---|---|---|
| apre100: da chiuso ad aperto in 100 ms | 1,49 mV (0,24 dB) | 1,80 mV (0,30 dB) | 1,49 mV | 1,47 mV |
| feedback50: da −15 a 0 dB in 50 ms | 0,058 mV (0,009 dB) | 0,149 mV (0,024 dB) | 0,059 mV | 0,058 mV |

Click della chiusura di scatto (sonda HP 2 poli ~1,6 kHz, tono 0 dBu a 1 kHz) e ritardo
dal gesto al 63 % della CV:

| | ideale | zoh1k | zoh8k | int8k |
|---|---|---|---|---|
| Picco della sonda | 0,33 V | 0,22 V | 0,33 V | 0,22 V |
| Ritardo al 63 % | 1,00 ms | 1,74 ms | 0,99 ms | 1,44 ms |

Programma che attraversa la sonda prima del gesto: 0,22 V.

Lettura:

- **Il banco è giusto**: la chiusura ideale dà 0,33 V, come la catena analogica
  in fx-module §8.3 (`sim/fx/reroute-ramp.cir`).
- **A 8 kHz il DAC non si distingue dalla catena continua**, con e senza
  interpolazione. A 1 kHz resta un'ondulazione in più: 0,015 dB nella zona del
  feedback, 0,05 dB nella zona ripida sotto −70 dB. Sulla sonda dell'audio
  (tono a 100 Hz) i quattro modi danno lo stesso picco, 4,3 mV: l'ondulazione
  sta sotto il tono che passa dalla sonda.
- **Click**: nessun modo peggiora la catena di oggi. Lo 0,22 V di zoh1k e int8k
  non è un click più piccolo: il gradino arriva più tardi, in un'altra fase del tono.
- **Ritardo (R4, ≤ 2 ms)**: tutti dentro. int8k aggiunge 0,44 ms; zoh1k 0,74 ms.
- **Scelta**: int8k. zoh8k ha ritardo zero, ma vuole l'ADC a 8 kHz con la media
  di 8 letture: 64 ksps per manopola, oltre il convertitore della classe MCP3208.

Cosa si sente, in parole: girando il reroute o il fader, nessun tremolio e nessuno
zip; chiudendo di scatto, lo stesso «tac» smorzato di oggi, mezzo millisecondo dopo.

## 2. Rumore al pin (`cella-cv-rumore.cir`)

Rumore del DAC: 100 nV/√Hz piatti [PROVVISORIO, ordine di grandezza della classe
DAC8568: da verificare sul datasheet del pezzo]. −REF5 ideale (stesso percorso
dello shaper di oggi). Integrale 20 Hz-20 kHz con `sim/mic/noise_total.py`.

| Uscita della cella | Rumore al pin | Rumore di modulazione sotto il segnale | ΔEc con l'op-amp in saturazione |
|---|---|---|---|
| v1: partitore 1k/1k (oggi) | 0,75 µV (−120,3 dBu) | −97,0 dB | ±6,75 V |
| v2: R in serie 100 Ω | 0,88 µV (−118,9 dBu) | −95,6 dB | ±13,5 V |
| v3: partitore 15k/1k | 0,77 µV (−120,1 dBu) | −96,8 dB | ±0,84 V |

Il rumore della CV moltiplica il segnale: un segnale a 0 dBu porta con sé un fruscio
di modulazione 97 dB più basso, e solo mentre suona. Il rumore non sceglie fra le tre.

Sceglie il pin: **ΔEc massimo assoluto ±1 V** (THAT 2181 datasheet, `docs/fase3/sistema-vca-trim.md`
§2). Con l'op-amp in saturazione (accensione, guasto) solo il partitore 15k/1k resta
sotto il limite. Saturazione presa dal modello della libreria (rail − 1,5 V: ±13,5 V).

**Scelta: v3, partitore 15k/1k** (D = 16). La cella lavora 16 volte più in alto:
Rin = 1,84k, Ro = 3,91k, Rf 10k, C 100n. A codice zero l'uscita dell'op-amp sta a
+12,8 V. [Da verificare sul datasheet dell'op-amp scelto: escursione d'uscita sui
±15 V LN con 16 kΩ di carico.] Il valore resta PROVVISORIO fino al prototipo.

Trovato per il mixer analogico (deduzione mia, non simulato): lo stadio del partitore
di oggi (`pcb/tools/celle_vca.py`, ×−1/5 poi 1k/1k) porta fino a ±6,75 V al pin se
il suo op-amp satura. Verificato e corretto il 2026-11-10 (todo 281): `sim/system/RISULTATI-ec-pin.md`.

## 3. Modello del firmware (`firmware_fxret.py`)

Catena: ADC 12 bit raziometrico → media di N letture → inseguitore con isteresi H
(banda morta che segue la mano) → law → taratura e temperatura → DAC 16 bit.
Il VCA del modello ha la sua costante (6,0-6,2 mV/dB), il suo offset (±2,5 mV) e
la costante che cresce con la temperatura assoluta (+0,33 %/°C). La cella ha le
tolleranze dei resistori, l'offset dell'op-amp e l'INL del DAC (±4 LSB).

| Req. | Prova | Esito |
|---|---|---|
| R1 | law nei 13 punti, DAC 16 bit | 0,0009 dB: passa |
| R2 | giro lentissimo (20 s), N = 8, H = 2 LSB, rumore ADC 0,5 / 1 LSB | 0…−15 dB: 0,021 dB; −15…−60 dB: 0,064 / 0,100 dB; sotto −60: 0,072 / 0,100 dB: passa |
| R3 | manopola ferma, 7 posizioni × 10 s, N = 8, H = 2 LSB | 0 scritture con rumore 0,5 e 1 LSB. Con 2 LSB: 629 scritture (0,11 dB) a H = 2, 6 a H = 3: un ADC così rumoroso va scartato |
| R4 | ritardo | 1,44 ms con int8k (LTspice, §1): passa |
| R5 | coppia L/R tarata a 0 e −40 dB, 0…−60 dB, 500 coppie | errore REW 0,01 dB: 0,07 dB; 0,03 dB: 0,19 dB: passa se REW misura entro 0,03 dB |
| R6 | errore a −15 dB, 20…65 °C | senza NTC 1,78 dB; NTC ±1 °C 0,05 dB; ±2 °C 0,10 dB (al limite); ±4 °C 0,21 dB |
| R7 | codice zero, peggior chip | −113 dB: chiuso |

Con la media di 4 letture (03 §4.2) R2 fallisce fra −15 e −60 dB (0,11-0,15 dB) e
R3 dà scritture a manopola ferma. **La media sale a 8 letture**: 5 manopole × 8 × 2 kHz
= 80 ksps sull'ADC, gli NTC letti piano. [Da verificare sul datasheet della classe
MCP3208: velocità massima a 5 V.]

Il punto debole è la temperatura: l'NTC va tenuto entro ±2 °C dal chip, meglio ±1,5.
L'altro è la taratura: REW deve misurare entro 0,03 dB (media lunga sul tono).

## 4. Cosa cambia in misto/03

- §4.2: media di 8 letture (non 4), isteresi 2 LSB che segue la mano (non banda morta fissa).
- §4.3: partitore 15k/1k, non 1k/1k né R in serie; DAC a 8 kHz con interpolazione.
- §4.4: NTC entro ±2 °C dal chip (R6 al limite).

Resta aperto: il guasto del −REF5 (senza offset la cella apre i VCA) e la saturazione
negativa dell'op-amp (−0,84 V al pin = VCA al massimo). Oggi lo shaper ha lo stesso
legame col −REF5. Da guardare quando si fa la scheda.

Verificato in: Python sì / LTspice sì (gradini, click, ritardo, rumore) / Live no.

## 5. Guasti e saturazione negativa (`cella-cv-guasti.cir`, todo 280, 2026-11-10)

Prima: offset da −REF5 (Ro 3,91k), nessun clamp. Se il −REF5 muore (o Ro si apre) la cella
scende in negativo: −0,84 V al pin = VCA aperto al massimo (+138 dB nominali), reroute in
autooscillazione.

Correzione [PROVVISORIO]:

1. **Offset dal −15LN**, il rail dell'op-amp della cella: Ro 11,8k (Rf/Ro × 15 V = 12,71 V,
   0,795 V al pin a codice zero). Se il −15LN manca, l'op-amp della cella è spento con lui:
   non esiste più un guasto «riferimento perso, cella viva» fuori da Ro aperta.
2. **Clamp in retroazione**: un diodo a bassa perdita (classe BAS416) fra nodo di somma
   (anodo) e uscita (catodo). L'uscita non scende sotto ~−0,6…−0,95 V: il pin sotto −0,06 V.
   A uscita alta (+12,7 V) il diodo è in inversa: perdita di pA, errore trascurabile.

| Caso (DAC 0 → 2,5 V) | Prima: pin a codice 0 / fondo scala | Dopo |
|---|---|---|
| Nominale | +0,799 / −0,050 V | +0,794 / −0,046 V |
| Offset perso (Ro aperta, riferimento a 0 V) | 0 / **−0,844 V** (+138 dB) | 0 / −0,060 V (+9,8 dB al massimo) |
| DAC ad alta impedenza | +0,799 V: chiuso | +0,794 V: chiuso |
| Riferimento del DAC morto (uscite a 0 V) | +0,799 V: chiuso | +0,794 V: chiuso |

Il clamp toglie il campo sotto −0,046 V al pin (+7,5 dB). Serve solo −5 mV (correzione d'offset,
03 §4.3): resta margine.

Resta un guasto che apre: Ro aperta o −15LN a 0 V con l'op-amp ancora vivo, fino a +9,8 dB.
Sul reroute un +9,8 dB col SELF alto può innescare: è un guasto di saldatura, si trova a banco.

Da verificare:
- deriva del −15LN (regolatore LT3094: corrente di SET ±1 % su tutto il campo, datasheet da
  leggere). Se serve, il chip legge il −15LN con l'ADC e corregge l'offset (un canale ADC);
- rumore: l'offset passa con Rf/Ro = 0,85 invece di 2,56, e il −15LN è un rail a basso rumore:
  rumore al pin uguale o più basso (deduzione mia, non simulato).

Verificato in: LTspice sì (.dc, 8 casi) / Python no / Live no.

