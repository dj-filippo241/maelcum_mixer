# RISULTATI P1 — MC-FILTRO (2026-10-15)

Piano: `docs/proto-max/piano.md` §2 P1. Generatore:
`proto-max/coefficienti/genera_filtro.py` (numeri in `filtro.py`).
Verifica: `prova_filtro.py`. Parte 1 (core) e parte 2 (DRIVE, PENDENZA)
fatte nella stessa notte, su richiesta di Filippo («tutto P1»).

## Cosa contiene

- **FREQ** HPF e LPF, curva Xone:96 (dec. 102 a): 10 Hz a 0 %, 20 Hz a
  5 %, 20 kHz a 95 %, 35 kHz a 100 %.
- **RES** HPF e LPF, dec. 102 (b): Q base fino al 90 %, poi fischio.
  gres = 1 − θ/0,9 fino al 90 %; oltre scende a −0,75 a fine corsa.
- **MODO** HPF / OFF / LPF (dec. 101), rampa 1 ms (dec. 80; dissolvenza
  incrociata, non break-before-make).
- **CORE** OTA (a′) / PULITO (c-B), dissolvenza 20 ms (B1).
- SVF 4 poli = sezione fissa + sezione con RES e limitatore. Q e
  frequenze secondo la PENDENZA (Butterworth: 0,541 / 1,307).
- Banca a 4× (halfband di P0).
- Livelli: 1,0 digitale = 4,36 V di picco; **0 dBu = sinusoide a
  −12 dBFS di picco** [PROVVISORIO, da sentire].
- **DRIVE** HPF e LPF: overdrive v0.2 (dec. 99/110), dopo il core;
  in OFF non agisce.
- **PENDENZA** Butterworth / Linkwitz-Riley / Bessel (B2, q64): Q e
  frequenze delle due sezioni scivolano in 20 ms.
- Non modellati: rumore del core, deriva, offset, servo DC.

## 1. Modello del core

- (a′): ogni integratore e l'OTA della RES vedono Vs·tanh(u/Vs),
  Vs = 2·VT·30 = 1,55 V (partitore 1/30, dec. 109).
- Limitatore (perdita dal buffer BP al summer): conduttanza
  G·softplus((|v| − VK)/W)·W/|v|, tarata sul fischio del D5:
  **G 1,7, VK 0,82 V, W 0,06 V**.
- (c-B): integratori e RES lineari, stesso limitatore. Il fischio del
  core pulito non è mai stato simulato in LTspice: è una stima.
- Discretizzazione: SVF TPT con le non linearità a secante, calcolate
  sul campione precedente.

## 2. Modello contro LTspice (D5, sezione 2 poli Q 0,707, k 1/30)

Tono a 1 kHz sul taglio, uscita LP, dB uscita/ingresso; modello a
400 kHz.

| RES | modello −30 / −10 / 0 dBu | D5 (`d5a-core2.cir`) |
|---|---|---|
| 0 % | −3,0 / −3,0 / −3,3 | −3,0 / −3,0 / −3,5 |
| 50 % | +4,0 / +4,0 / −0,7 | +4,0 / +3,8 / −0,5 |
| 70 % | +10,1 / +7,3 / 0,0 | +9,9 / +7,2 / +0,3 |
| 85 % | +21,3 / +8,4 / +0,4 | +21,3 / +8,5 / +0,7 |

Scarto massimo 0,3 dB.

Fischio senza ingresso (D5 `d5a-nl-k30.cir`: −1,8 dBu −1,3 st poco oltre
il 90 %, +4,9 dBu −5,7 st a fine corsa):

| taglio | gres −0,1 | gres −0,75 |
|---|---|---|
| 100 Hz | −1,2 dBu · −1,6 st | +4,8 dBu · −5,7 st |
| 1 kHz | −1,3 · −1,6 | +4,7 · −5,6 |
| 10 kHz | −1,6 · −1,3 | +4,1 · −4,6 |

Scarto ≤ 0,6 dB e ≤ 0,3 semitoni fino a qualche kHz. Sopra ~3 kHz la
discretizzazione a secante accorcia il calo di nota (−4,6 st a 10 kHz
invece di −5,7) e abbassa il fischio di ~0,6 dB: limite noto del
prototipo, il D5 dice livello e nota uguali su tre decadi.

Core pulito (c-B), stessa tabella: risonanza come l'ideale fino a
−10 dBu, poi frenata solo dal limitatore (+3,1 dB a RES 85 % su 0 dBu,
contro +0,4 del core OTA); fischio +8,1 dBu, nota ferma (−0,3 st).

## 3. Codice gen~ contro modello (`prova_filtro.py`)

Testo di `MC-FILTRO.genexpr` tradotto in Python e suonato a 48 kHz,
contro `filtro.Core` (4 poli) a 192 kHz senza halfband: **PASS**.

- OFF trasparente: 0,00 dB.
- Taglio a piccolo segnale, HPF e LPF a 100 Hz / 1 kHz / 10 kHz:
  −3,01 dB (Butterworth 4 poli), scarto 0,00.
- Risonanza, 4 poli, 36 punti (due core, HPF e LPF, RES 0-85 %,
  −30 / −10 / 0 dBu): scarto ≤ 0,01 dB.
- Fischio a 200 Hz / 1 kHz / 5 kHz, due core: livello ≤ 0,03 dB,
  nota ≤ 0,01 semitoni.

Numeri a 4 poli, core OTA, LPF sul taglio (per l'ascolto):

| RES | −30 dBu | −10 dBu | 0 dBu |
|---|---|---|---|
| 0 % | −3,0 | −3,0 | −3,5 |
| 50 % | +4,0 | +3,8 | −1,5 |
| 70 % | +10,1 | +6,7 | −1,0 |
| 85 % | +20,4 | +7,5 | −0,6 |

Fischio a 4 poli: OTA +4,7 dBu, −5,5 st (1 kHz); pulito +8,1 dBu.

## Non verificato

- Sintassi gen~ e CPU: si vedono all'apertura in Live.
- Il fischio parte da un seme di rumore a −98 dBu (`noise()`), come il
  circuito vero parte dal suo rumore.

## 4. DRIVE (overdrive v0.2)

y = x + m·(1,171·CLIP(2x) − x), m = θ^2,5; CLIP = 2,2k + 2+2 1N4148
(Is 2,52 nA, N 1,752, modello di `od2-chain.cir`), risolto con tre passi
di Newton.

Modello contro LTspice (`od2-chain.cir`, tono 1 kHz, 24 caselle della
griglia di filter-module §5ter): livello ≤ 0,1 dB, THD entro 1 punto
percentuale (es. 100 % su +8 dBu: 31,4 % · +4,5 dBu contro 31 % · +4,6;
tetto 1,59 V).

gen~ contro modello (LPF sul taglio, RES 85 %): ≤ 0,01 dB a DRIVE 50 e
100 %, −10 e 0 dBu. Con +16 dBu, RES 85 % e DRIVE 100 % il picco
d'uscita resta 1,56 V. In OFF il DRIVE non agisce (0,00 dB).

## 5. PENDENZA (B2)

| Pendenza | Q1 · f1/fc | Q2 · f2/fc | sul taglio | LPF a 2 kHz (fc 1 kHz) |
|---|---|---|---|---|
| Butterworth | 0,541 · 1 | 1,307 · 1 | −3,0 dB | −24,1 dB |
| Linkwitz-Riley | 0,707 · 1 | 0,707 · 1 | −6,0 dB | −24,6 dB |
| Bessel | 0,522 · 1,419 | 0,806 · 1,591 | −3,1 dB | −13,6 dB |

Nell'HPF le frequenze delle sezioni si dividono. La RES agisce sulla
sezione 2: il suo lato positivo segue la Q della pendenza, il lato del
fischio è uguale per tutte (stesso OTA RES del D5). gen~ contro modello
≤ 0,01 dB.

## 6. Errore trovato e corretto

Il primo `MC-FILTRO.genexpr` chiamava `ap()` (allpass dell'oversampling)
senza definirla: in Live non avrebbe compilato. La prova non lo vedeva,
perché `prova_gen.Gen` fornisce `ap` e `bq` già pronte. Ora
`prova_filtro.py` toglie quelle due e traduce in Python le funzioni
scritte davvero nel `.genexpr`.


## 7. Secondo errore: canale destro rotto (2026-10-15)

Segnalato da Filippo all'ascolto («il filtro è rotto»). Il generatore
chiamava `d1` la Q della prima sezione (`d1 = q1i`), ma il downsampling
usa `d0`/`d1` come variabili di lavoro. Il lato L sovrascriveva `d1` con
un proprio campione audio; il lato R lo leggeva come 1/Q della prima
sezione. Risultato: canale R sbagliato e instabile con filtro inserito
(LPF a 1 kHz, 0 dBu: L −3,5 dB, R +1,9 dB; HPF: L −1,8 dB, R +8,5 dB).
In OFF i due lati erano uguali, per questo il guasto non si sentiva
subito. Il lato L era giusto.

Correzione: la variabile si chiama `dq1`. La prova suonava solo `out1`;
ora `prova_filtro.py` confronta R con L in 4 casi (HPF/LPF, due core,
pendenze, DRIVE): scarto ≤ 5·10⁻⁶ (seme di rumore diverso per lato),
contro 0,25-3,8 del file guasto. PASS.

Controlli fatti nella stessa sessione, senza altri errori:

- Nessun'altra variabile passa da L a R, né in MC-FILTRO né in
  MC-CHANNEL (controllo automatico sulle letture del lato R).
- Patch: ogni comando arriva al suo `Param`; codice nella patch uguale
  al `.genexpr`; struttura del `gen~` uguale a MC-CHANNEL.
- Stress: comandi mossi a caso ogni 40 ms (RES 100 %, FREQ agli estremi,
  DRIVE, MODO, CORE, PENDENZA), quadra a 0 dBFS, a 44,1 / 48 / 96 kHz:
  nessun valore non finito. Picco d'uscita fino a ~2,9 (+9 dBFS): con
  ingressi forti e RES alta l'uscita supera 0 dBFS e satura la scheda
  audio. Il circuito vero arriva più in alto (rail), quindi non è un
  errore del modello, ma va tenuto basso il volume d'ingresso.

## CPU (2026-10-15 sera)

Stesso finding di RISULTATI-P0 §CPU. MC-FILTRO calcolava per ogni
sotto-campione otto sezioni (due core × HP e LP), ognuna con tre `tanh`
e il limitatore, più due tosatori a Newton, anche dove il peso era zero.
Ora (suono invariato):
- quattro funzioni di sezione senza rami morti: il core pulito non
  calcola `tanh`, il limitatore solo nella seconda sezione;
  `aota(bpv)` una volta sola;
- si calcola solo il core scelto (l'altro solo durante i 20 ms di
  CORE); gli stati del core spento vanno a zero;
- il tosatore solo con overdrive > 1e-9.
Funzioni trascendenti per sotto-campione: ~68 → ~16 (core OTA, DRIVE
chiuso). HP e LP restano sempre calcolati: al cambio di MODO (rampa
1 ms, gesto) un ramo ripartito da fermo suonerebbe diverso.
`prova_filtro.py` PASS invariata.

## Regole gen~ (2026-10-21, segnalazione della sessione maelcum-mixer-bd)

MC-FILTRO violava due regole del codice gen~ dalla prima versione:
le funzioni di sezione `sez_*` avevano due valori di ritorno (`return hp, lp`,
lo stesso errore del 5-way, RISULTATI-P2 §5) e il codice principale usava
`x`, che è anche parametro delle funzioni. Correzione in `genera_filtro.py`:
otto funzioni a uscita singola (`sez_a0_hp`, `sez_a0_lp`, ...) e `xin` al
posto di `x`. Vale anche per MC-FILTRO-S. La traduzione Python suona
identica a prima (scarto 0 su 22 casi, manopole in movimento);
prova_filtro PASS. Possibile causa dei salti in Live (todo 76): da
verificare all'ascolto.

## LIMITATORE del PULITO (2026-10-21, Filippo: «dopo l'ascolto»)

Nuovo selettore LIMITATORE = PULITO 2+2 / PULITO 3+3 in MC-FILTRO e
MC-FILTRO-S. Agisce solo sul core PULITO (c-B); l'OTA (a′) tiene il suo.
Taratura su LTspice (`sim/filtro/RISULTATI-cb-4p.md` §RES), conduttanza
fisica 10k/4,7k = 2,13:

| | ginocchio · morbidezza | oscillazione a fine corsa | LTspice |
|---|---|---|---|
| 2+2 | 0,72 V · 0,06 V | +4,5 dBu | +4,4 dBu |
| 3+3 | 0,93 V · 0,09 V | +6,7 dBu | +6,8 dBu |

Risonanza sul programma entro 1 dB (2+2) e 1,6 dB (3+3) da LTspice. La
nota a fine corsa cala di 0,6-0,8 semitoni (LTspice 1,1): il modello a
secante non coglie tutto il rallentamento dei diodi.

**Prima di oggi il PULITO usava il limitatore tarato sul core (a′) e
oscillava a +8,0 dBu**, 3,6 dB sopra il circuito progettato. Gli ascolti
del PULITO precedenti avevano un fischio più forte del vero.

Prove: prova_filtro PASS (2+2, valore di partenza); 3+3 gen~ contro
modello ≤ 0,01 dB e ≤ 0,01 semitoni su MC-FILTRO e MC-FILTRO-S; regole
gen~ pulite (un ritorno per funzione, nessun nome in collisione).

Dal 2026-10-21 (todo 119) la prova del 3+3 sta in `prova_filtro.py`:
risonanza LP/HP a RES 70 e 85 %, -10/0/+6 dBu, gen~ contro modello entro
0,01 dB; fischio a 200 Hz, 1 kHz, 5 kHz +6,78 / +6,67 / +6,32 dBu (2+2:
+4,54 / +4,47 / +4,11). Il confronto -S contro originali sta in
`prova_semplice.py`. Nel generatore il LIMITATORE esce dal -S se la
scelta fissata è il core (a′): lì non serve.

