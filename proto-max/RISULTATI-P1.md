# RISULTATI P1 (parte 1) — MC-FILTRO (2026-10-15)

Piano: `docs/proto-max/piano.md` §2 P1. Generatore:
`proto-max/coefficienti/genera_filtro.py` (numeri in `filtro.py`).
Verifica: `prova_filtro.py`. Parte 2 (DRIVE, pendenza B2): da fare.

## Cosa contiene

- **FREQ** HPF e LPF, curva Xone:96 (dec. 102 a): 10 Hz a 0 %, 20 Hz a
  5 %, 20 kHz a 95 %, 35 kHz a 100 %.
- **RES** HPF e LPF, dec. 102 (b): Q base fino al 90 %, poi fischio.
  gres = 1 − θ/0,9 fino al 90 %; oltre scende a −0,75 a fine corsa.
- **MODO** HPF / OFF / LPF (dec. 101), rampa 1 ms (dec. 80; dissolvenza
  incrociata, non break-before-make).
- **CORE** OTA (a′) / PULITO (c-B), dissolvenza 20 ms (B1).
- SVF 4 poli = sezione Q 0,541 fissa + sezione Q 1,307 con RES e
  limitatore (Butterworth a RES zero) [PROVVISORIO: B2 nella parte 2].
- Banca a 4× (halfband di P0).
- Livelli: 1,0 digitale = 4,36 V di picco; **0 dBu = sinusoide a
  −12 dBFS di picco** [PROVVISORIO, da sentire].
- Non modellati: DRIVE, rumore del core, deriva, offset, servo.

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
