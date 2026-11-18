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

## 5. Mix e stadio d'uscita (`mix-uscita.cir`, v0.3)

Caso peggiore: FIRE tenuto 1 s, onda quadra ±0,775 V (0 dBu sul plateau,
VOLUME tutto), RIPETIZIONI tutto, giro con attenuatore −14 dB. Mix:
somma invertente riferita a VDD/2, asciutto e eco con 10k, reazione 10k
(eco a guadagno 1 a LIVELLO ECO tutto, come `lickshot.py`: uscita =
asciutto + eco² × ritorno). Uscita: 100 Ω + 10 µF verso il jack, 100k di
scarica, carico 1 MΩ (ingresso del MONO, `docs/fase4/mic-mono-moduli.md`).

| LIVELLO ECO (elettrico) | Picco del mix | Ritorno dei BBD (picco) | Jack, efficace a eco 0 |
|---|---|---|---|
| 0 | 0,775 V | 2,43 V | 0,774 V (0 dBu) |
| 0,5 | 2,29 V | 3,02 V | — |
| 1 | **3,31 V** | 2,54 V | — |

- Il colpo da solo esce a 0 dBu, il valore della dec. 187.
- Picco massimo del mix 3,31 V contro ±4,4 V del TLC2272 a 9 V: margine
  **2,5 dB** nel caso peggiore (tutto al massimo e FIRE tenuto). Con FIRE
  tenuto il giro sale a 2,5-3,0 V di picco al ritorno, più dei 2,09 V del
  colpo breve (§2): l'asciutto continua a entrare nel giro. Il ritorno
  resta sotto il rail (3,02 V).
- Al jack: +7,6 dBu di picco al massimo; il MONO regge +18 dBu.
- Passa-alto dell'uscita: 10 µF su 91k (100k ∥ 1 MΩ) = 0,17 Hz.
- Il mix inverte la polarità del colpo. Ininfluente: la lickshot è una
  sorgente sola su un MONO (deduzione mia; la dec. 187 non chiede una
  polarità).

## 6. Alimentazione (calcolo, v0.3)

Correnti massime dai datasheet, dove ci sono:

| Ramo | Parte | Corrente | Fonte |
|---|---|---|---|
| 9 V | 5 × TLC2272 | 15 mA (3 mA max ciascuno) | TI SLOS190H, «Electrical Characteristics», IDD |
| 9 V | CD4069UB con porte in zona lineare | ≤ 5 mA | deduzione mia: porte senza buffer in zona lineare assorbono corrente; da misurare |
| 9 V | CD4046B (solo VCO), LED, partitori | ≤ 3 mA | deduzione mia |
| 5 V | 2 × V3102 a vuoto | 1 mA (0,5 mA tip.) | MN3102 p. 106, IDD |
| 5 V | 2 × carico del clock (2800 pF × 5 V × 100 kHz × 2 fasi) | 5,6 mA | V3205D (capacità del clock) e calcolo |
| 5 V | 2 × V3205D | ≤ 20 mA | deduzione mia (10 mA per chip): IDD da rileggere sul datasheet V3205D |

Totale: 9 V ≤ 23 mA, 5 V ≤ 27 mA, ~60 mA dall'ingresso coi due
regolatori a riposo.

- Ingresso: 12 V da alimentatore stabilizzato, 1N5819 in serie (~0,35 V),
  100 µF / 25 V. Alimentatore da almeno **200 mA** (come il Klementz,
  < 200 mA dichiarati): 3 volte il consumo.
- **78L09** dall'ingresso: (11,65 − 9) V × 23 mA = 61 mW.
- **78L05** dall'ingresso attraverso **47 Ω + 100 µF**: il resistore
  scarica 1,3 V e il condensatore tiene i picchi del clock lontani dal
  ramo dei 9 V (i due regolatori non sono in fila). (10,4 − 5) V × 27 mA
  = 0,15 W: ~30 °C sopra l'ambiente in TO-92 (θJA ~200 °C/W, deduzione mia
  da rileggere sul datasheet del regolatore scelto).
- Margine di caduta: il 78L09 vuole ~1,7 V (deduzione mia); a 12 V − 5 %
  restano 11,05 V: 0,35 V di margine. Un alimentatore non stabilizzato
  a vuoto sale sopra 12 V: va bene, il 78L09 regge fino a 30 V.
- Massa: il negativo dell'alimentatore è flottante (dec. 189); la massa
  arriva dal MONO con la calza del cavo.

Verificato in: Python no / LTspice sì (PROFONDITÀ, giro, mix) / Live no.
