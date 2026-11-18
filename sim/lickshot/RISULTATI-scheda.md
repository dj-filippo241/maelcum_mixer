# Lickshot — stadi veri della scheda (2026-11-18, todo 382)

Scheda: `pcb/lickshot/lickshot.py` (bozza v0.1, commit 5eda34c). Netlist con gli
stessi nodi e valori del generatore: `scheda.inc`, incluso da `scheda-anello.cir`,
`scheda-anello-47k.cir`, `scheda-giro.cir`, `scheda-mix.cir`. Op-amp TLC2272 a
9 V singolo, VDD/2 da partitore + buffer, comandi come parametri. I netlist
v0.2-v0.3 (`giro-att14.cir`, `mix-uscita.cir`) usavano op-amp ideali riferiti a 0.

Esito: la scheda v0.1 aveva **tre difetti**, corretti nel generatore lo stesso
giorno (§2, §3, §4). Con le correzioni gli stadi veri danno i numeri della v0.2.

## 1. Modello del TLC2272

- Modello TI ufficiale SLOJ080B (Rev. B, «Final 1.1», datasheet SLOS190H) in
  `sim/lib/tlc2272.lib`. Un'istanza sola funziona; con le 8 della scheda il
  `.op` non converge in LTspice 26.0.2 (Newton, Gmin e source stepping falliti;
  anche con `.nodeset` e con `startup`). Uno alla volta, con gli altri ideali,
  ogni stadio converge: il limite è il numero di istanze, non uno stadio.
- Macro semplice `sim/lib/tlc2272s.inc` (GBW 2,2 MHz, slew rate 3,6 V/µs,
  uscita fermata a 30 mV dai rail + 200 Ω, anti-windup), tarata sul modello TI
  nello stesso banco (invertente ×2 a 9 V, carico verso VDD/2, uscita in
  clipping; `tlc-taratura.cir` = TI, `tlc-macro.cir` = macro):

| Carico | TI min | TI max | Macro min | Macro max |
|---|---|---|---|---|
| 2k | 0,39 V | 8,38 V | 0,47 V | 8,53 V |
| 5k | 0,19 V | 8,74 V | 0,24 V | 8,76 V |
| 10k | 0,12 V | 8,85 V | 0,16 V | 8,84 V |

- Con i carichi della scheda (≥ 10k) l'uscita va da 0,16 a 8,84 V: ±4,34 V
  attorno a VDD/2. Il ±4,4 V della v0.2 regge.
- Modo comune d'ingresso (datasheet SLOS190H, VICR a 5 V): fino a VDD+ − 1 V a
  25 °C, VDD+ − 1,5 V su tutta la temperatura: 8,0 e 7,5 V a 9 V. La macro non
  lo modella: si legge sui nodi (§5).

## 2. Guadagno del giro (`scheda-anello*.cir`, anello aperto, 1 kHz)

Si inietta 1 V AC al capo della reazione e si legge FB. Obiettivo (v0.2 e
modello `lickshot.py`): 1,1 × RIPETIZIONI, cioè **+0,83 dB** a fondo corsa.
BBD a 0 dB d'inserzione, resistenza d'uscita 1k (deduzione mia: il datasheet
non la dà). tc = cursore del trimmer di cancellazione del clock.

**Scheda v0.1** (make-up 10k / 49,9k, uscite dei BBD su 47k):

| RIPETIZIONI | tc 0,05 | tc 0,5 | Ideale |
|---|---|---|---|
| 0,25 | −14,3 dB | −15,6 dB | −11,2 dB |
| 0,5 | −8,4 dB | −9,8 dB | −5,2 dB |
| 0,75 | −4,7 dB | −6,1 dB | −1,7 dB |
| 1 | **−1,5 dB** | **−2,9 dB** | +0,8 dB |

- A fondo corsa il giro vale 0,72-0,84 invece di 1,1: le ripetizioni non si
  tengono più da sole, il carattere della v0.2 sparisce.
- Perdite (SUM → POST, che deve valere 0 dB): −2,3 dB col cursore al bordo,
  −3,6 dB al centro. Vengono da: 100k di polarizzazione sull'uscita
  dell'attenuatore (8k di sorgente: −0,7 dB), source follower su 47k, cursore
  del trimmer di cancellazione (~3k di sorgente) davanti ai 10k della make-up
  (−2,1 dB al centro). Il trimmer di cancellazione sposta il giro di 1,4 dB.
- Il guadagno d'inserzione del V3205D vale 0 dB tipico, **−4…+4 dB** per chip
  (datasheet CoolAudio V3205D/SD, «Electrical Characteristics», Li): con due
  chip il giro può cadere ovunque fra −8 e +8 dB. Una make-up fissa non basta.

**Correzione** (generatore, 2026-11-18): uscite dei BBD su **100k** (RL del
datasheet; lo schema d'applicazione mette 100k per uscita e 5,6k + 5,6k per
sommarle, qui il trimmer), make-up con ingresso **47k** e reazione **100k +
trimmer 500k** (taratura a ~280k), accoppiamento 1 µF (3,4 Hz).

| Inserzione dei due BBD | 100k (min) | 280k | 600k (max) |
|---|---|---|---|
| −6 dB (0,71 ciascuno) | −13,9 / −14,3 dB | −4,9 / −5,4 dB | **+1,7 / +1,3 dB** |
| 0 dB | −7,9 / −8,4 dB | +1,0 / +0,6 dB | +7,7 / +7,2 dB |
| +6 dB (1,41 ciascuno) | **−1,9 / −2,4 dB** | +7,0 / +6,6 dB | +13,6 / +13,2 dB |

(Giro a RIPETIZIONI tutto; i due numeri: tc 0,05 / 0,5.) Il trimmer porta il
giro a +0,8 dB anche con due chip a −3 dB o a +3 dB ciascuno. Il trimmer di
cancellazione ora sposta il giro di 0,4 dB.

- Taratura (deduzione mia, da provare al prototipo): RIPETIZIONI a zero, un
  tono da 1 kHz sul giro, trimmer finché POST ha la stessa ampiezza di SUM.
- RIPETIZIONI caricato dal 12,7k della saturazione (NOTA 4): a fondo corsa
  esatto (+0,83 dB, come il modello), −0,7 dB a 1/4 e 3/4, −0,9 dB a metà.
  La legge del pot diventa un po' più morbida a metà; gli estremi restano.

## 3. VDD/2 scosso dal VCO (`scheda-giro.cir`, primo giro)

Nella scheda v0.1 l'onda quadra del CD4046 (0/9 V) entrava nel colpo per
10 µF → partitore 1k/100 verso VMID → 10k. Il VCO gira sempre, anche a FIRE
aperto: a ogni fronte ±4 mA entrano nel buffer di VMID. Con lo stadio vero VMID
sobbalza di **±0,2 V** e il disturbo arriva a tutti gli stadi riferiti a VDD/2:
a RIPETIZIONI metà il ritorno restava a 0,57 V di picco dopo 1,3 s invece di
spegnersi (v0.2: 0,001 V).

**Correzione**: 100 nF film → 110k direttamente nell'ingresso invertente
(19,1k di reazione: ×0,173). Stesso plateau (4,5 × 19,1/110 = 0,78 V = 0 dBu),
stesso passa-alto (14,5 Hz). Il partitore verso VMID sparisce e con lui il
10 µF ceramico della NOTA 8. VMID resta entro ±10 mV.

## 4. FIRE nel netlist

Il tasto è una resistenza comandata dal tempo (0,05 Ω premuto, 1 GΩ aperto).
Il primo giro usava l'interruttore `SW` di LTspice: il residuo a tasto aperto
sembrava una perdita del tasto, ma restava uguale con la resistenza. Era VMID
(§3).

## 5. Transitori con la scheda corretta

Make-up tarata a 280k, BBD a 0 dB, colpo dal VCO (600 Hz, quadra 0/9 V),
VOLUME tutto.

**Giro** (`scheda-giro.cir`, FIRE 0,2 s, LIVELLO ECO 0):

| RIPETIZIONI | Ingresso BBD (picco) | Somma (picco) | Ritorno dopo 1,3 s | v0.2 |
|---|---|---|---|---|
| 0,5 | 0,28 V | 1,55 V | 0,0006 V (si spegne) | 0,001 V |
| 0,9 | 0,34 V | 1,87 V | 0,35 V | 0,56 V |
| 1 | 0,35 V | 1,91 V | 0,90 V (si tiene) | 0,90 V |

A 0,9 il ritorno è più basso della v0.2 per i −0,7 dB del pot caricato (§2).

**Caso peggiore** (`scheda-mix.cir`, FIRE tenuto 1 s, RIPETIZIONI tutto):

| LIVELLO ECO | Mix min / max | Ritorno (POST) | Ingresso BBD | Jack, efficace a 0,1 s |
|---|---|---|---|---|
| 0 | 3,57 / 5,38 V | 2,39-6,58 V | 0,40 V | 0,78 V (0 dBu) |
| 0,5 | 2,70 / 6,19 V | 2,37-6,69 V | 0,41 V | — |
| 1 | **1,66 / 7,48 V** | 2,17-6,55 V | 0,40 V | — |

- Mix: 3,0 V di picco attorno a VDD/2 contro ±4,34 V: margine **3,3 dB**
  (v0.3 ideale: 2,5 dB su ±4,4 V).
- Ritorno: 2,33 V di picco, margine 5,4 dB. Ingresso del BBD 0,41 V: 1,9 dB
  sotto i 0,51 V di picco del V3205D (0,36 V efficaci a THD 2,5 %).
- Modo comune: l'ingresso + del buffer dopo il passa-alto (HPN, U6B) arriva a
  **7,28 V**. Sotto gli 8,0 V a 25 °C e i 7,5 V garantiti su tutta la
  temperatura, ma con solo 0,22 V di margine e solo in questo caso (tutto al
  massimo, FIRE tenuto). Gli altri ingressi + stanno entro ±2,3 V da VDD/2.
- Un BBD a +4 dB alza l'ingresso del secondo chip di 4 dB: ~0,65 V, sopra il
  limite del datasheet. Deduzione mia: il secondo chip satura un po' prima; è
  carattere del giro, non un guasto. Da sentire al prototipo.

## 6. Cosa non è simulato

- Il clock (V3102) e il suo residuo sulle uscite dei BBD: nessun modello.
  Il trimmer di cancellazione si tara sul pezzo.
- Rumore dei BBD (S/N 60 dB per chip, datasheet).
- Polarizzazione dei BBD: lo schema d'applicazione del V3205D tara l'ingresso
  con un trimmer da 100k «per la minima distorsione»; qui 10k fra +5 V e massa
  + 100k verso l'ingresso. Stessa funzione: si tara sul pezzo.

Verificato in: Python no / LTspice sì (stadi audio con TLC2272 tarato sul
modello TI, BBD ideali) / Live no.
