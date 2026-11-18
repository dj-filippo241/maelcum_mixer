# Lickshot — risultati v0.2 (2026-11-18)

Design doc: `docs/fase4/lickshot.md` (v0.2). Op-amp ideali (sorgenti E):
si misurano i livelli dei nodi e si confrontano coi rail e coi datasheet.

## 1. PROFONDITÀ (`profondita.cir`)

VDD 9 V, rampa dell'integratore fra 6/22 e 16/22 di VDD (2,45-6,55 V),
buffer, pot lineare fra rampa e VDD/2, non invertente G = 1 + 5,1k/10k
= 1,51 riferito a VDD/2.

| PROFONDITÀ | VCOin min | VCOin max | Ingresso max dell'op-amp |
|---|---|---|---|
| 0 | 4,50 V | 4,50 V | 4,50 V |
| metà | 2,96 V | 6,04 V | 5,52 V |
| tutta | 1,41 V | 7,59 V | 6,55 V |

- A fondo corsa: (7,59 − VOFF) / (1,41 − VOFF) = 16,1 con VOFF 1 V
  (`lickshot.py`): **4,0 ottave**, come il modello (`A_MAX`).
- Uscita dentro 0,1-8,9 V (uscita ai rail del TLC2272 a carico leggero).
- Ingressi sotto 7,5 V = VDD+ − 1,5 V (modo comune del TLC2272, TI
  SLOS190H, «Recommended Operating Conditions»): margine 0,95 V.

## 2. Giro dell'eco (`giro.cir`, `giro-att14.cir`)

Colpo da 0 dBu (1,095 V di picco, 600 Hz, 0,2 s), BBD come ritardo
ideale da 100 ms, passa-alto 150 Hz, saturazione a diodi 1N4148
(partitore × 0,4, guadagno 2,5: ginocchio a ~1,5 V al livello di linea).
RIPETIZIONI = guadagno del giro 1,1 × rip.

| Attenuatore | rip | Picco all'ingresso BBD | Picco somma (linea) | Ritorno dopo 1,3 s |
|---|---|---|---|---|
| −12 dB (0,25) | 0,5 | 0,43 V | 1,70 V | 0,001 V (si spegne) |
| −12 dB | 0,9 | 0,51 V | 2,04 V | 0,56 V |
| −12 dB | 1,0 | 0,52 V | 2,09 V | 0,90 V (si autoalimenta) |
| **−14 dB (0,2)** | 0,5 | 0,34 V | 1,70 V | 0,001 V |
| **−14 dB** | 0,9 | 0,41 V | 2,04 V | 0,56 V |
| **−14 dB** | 1,0 | 0,42 V | 2,09 V | 0,90 V |

- Il V3205D dà 0,36 V efficaci (0,51 V di picco su un seno) a THD 2,5 %
  (datasheet CoolAudio V3205D/SD, VDD 5 V). Con −12 dB il giro arriva
  esattamente lì; con **−14 dB** resta a 0,42 V, 1,7 dB sotto. Scelta:
  −14 dB [PROVVISORIO]. Costo: 2 dB di rumore dei BBD in più (S/N 60 dB
  per chip).
- Picco massimo al livello di linea 2,09 V: coi rail a ±4,4 V attorno a
  VDD/2 (VDD 9 V) il margine è 6,5 dB.
- A rip tutto il giro si tiene da solo a 0,90 V di picco al ritorno. Il
  modello (`lickshot.py`, tanh a 1,5 V, G 1,1) si tiene a ~0,8 V
  (punto fisso di x = 1,5 tanh(1,1 x / 1,5)): stessa forma, il ginocchio
  dei diodi è un po' più duro. Deduzione mia: all'orecchio non cambia, da
  confermare al prototipo.

## 3. Clock (calcolo, non simulato)

- V3205D: capacità d'ingresso del clock fino a 2800 pF, salita e discesa
  ≤ 500 ns, incrocio delle fasi fra 0 e 0,3 VCPH (datasheet V3205D/SD).
- MN3102 (Panasonic, gemello del V3102): pilota direttamente un BBD fino a
  4096 stadi; sotto 7 V la dissipazione resta nei 200 mW (datasheet p. 108).
  Due V3205D sono 8192 stadi: il doppio. Quindi **un V3102 per BBD**: il
  primo oscilla con R e C, il secondo è pilotato dal primo (OX1 dal suo
  OX3, OX2 e OX3 aperti: «separate excitation», datasheet p. 107).
- Scartato: un solo V3102 + driver TC4427 (Microchip DS20001422G). A 5 V
  sale in ~95 ns su 2200 pF (Fig. 2-2), quindi ~240 ns su 5600 pF: va bene
  per la salita, ma due fronti lenti e uguali si incrociano a metà, sopra
  0,3 VCPH. Servirebbe un generatore di non sovrapposizione in più.
- Fase del secondo V3102: il suo divisore per 2 può partire in fase o in
  controfase col primo. Deduzione mia: con OUT1 + OUT2 sommati il BBD 1
  dà un segnale tenuto in tutte e due le fasi, e la controfase sposta il
  campionamento del BBD 2 di mezzo periodo (5-50 µs). Da verificare al
  prototipo.

## 4. Legge di TEMPO (calcolo)

Fit sulla Fig. 1 del MN3102 (C 100 pF, VDD 5 V; punti 5k → 260 kHz e
1M → 3,2 kHz): fcp ≈ 3,22e9 / (R + 7,4k). Per 100 kHz → R = 24,8k; per
10 kHz → R = 315k. Ritardo ∝ R + 7,4k: un reostato da 250k + 22k fisso +
trimmer 10k copre 41-~360 ms (fcp minimo 3,22e9 / 282k = 11,4 kHz). Per
arrivare a 410 ms il condensatore sale a ~115 pF e il fisso scende in
proporzione. La curva del datasheet è un esempio: gli estremi si tarano
sul pezzo.

| Corsa | Modello (esponenziale) | Pot A 10 % | Pot A 15 % | Pot A 20 % | Pot lineare |
|---|---|---|---|---|---|
| 0 | 41 ms | 41 | 41 | 41 | 41 |
| 25 % | 73 ms | 59 | 69 | 78 | 133 |
| 50 % | 130 ms | 78 | 96 | 115 | 226 |
| 75 % | 231 ms | 244 | 253 | 262 | 318 |
| 100 % | 410 ms | 410 | 410 | 410 | 410 |

Scelta: **pot lineare** (dec. 193). Pot A modellato a due tratti (x % a metà corsa). Il valore a metà corsa
dipende dal costruttore: si legge sul datasheet del pot scelto.

Verificato in: Python no / LTspice sì (PROFONDITÀ, giro) / Live no.
