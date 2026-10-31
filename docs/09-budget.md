# 09 — Budget dei moduli e del mixer completo [STIMA]

Data: 2026-10-22. Generato da `docs/budget/genera_budget.py`: i prezzi e le
quantità si correggono lì, poi si rilancia lo script. Non a mano qui.

Cosa è: il costo dei materiali per costruire **un** esemplare, modulo per
modulo, con una forchetta minimo – massimo. Le quantità vengono dai design
doc alla data (~74 VCA, 115 manopole, 4 canali). Gli acquisti restano
sospesi fino al prototipo in Live (voce 37, A12): questo documento non
ordina niente.

Prezzi: euro per pezzo, **IVA esclusa**, per lotti da decine di pezzi.
L'IVA (22 %) si aggiunge nel riepilogo. Le fonti sono in fondo: dove la
fonte è S il prezzo è una stima, senza preventivo.

## 1. Riepilogo

| Modulo | € per modulo | Copie (completo) | Completo | Copie (ridotto) | Ridotto |
|---|---|---|---|---|---|
| Canale CDJ/line con phono | 200 € – 368 € | 4 | 802 € – 1.470 € | 2 | 401 € – 735 € |
| FX-SEND | 39 € – 69 € | 4 | 156 € – 276 € | 2 | 78 € – 138 € |
| FX-RET (un bus, dec. 130) | 123 € – 244 € | 4 | 493 € – 978 € | 4 | 493 € – 978 € |
| Filtro, core OTA (a') | 126 € – 265 € | 1 | 126 € – 265 € | 1 | 126 € – 265 € |
| 5-way | 364 € – 661 € | 1 | 364 € – 661 € | 1 | 364 € – 661 € |
| Master out (con booth e MONO) | 133 € – 244 € | 1 | 133 € – 244 € | 1 | 133 € – 244 € |
| CUE e cuffie | 66 € – 116 € | 1 | 66 € – 116 € | 1 | 66 € – 116 € |
| Metering (tutte le barre) | 58 € – 151 € | 1 | 58 € – 151 € | 1 | 58 € – 151 € |
| MIC | 68 € – 123 € | 1 | 68 € – 123 € | 1 | 68 € – 123 € |
| MONO | 38 € – 70 € | 3 | 115 € – 211 € | 1 | 38 € – 70 € |
| Backplane | 20 € – 42 € | 1 | 20 € – 42 € | 1 | 20 € – 42 € |
| PSU-IN e ventole (nel mixer) | 56 € – 108 € | 1 | 56 € – 108 € | 1 | 56 € – 108 € |
| Alimentatore esterno (box) | 480 € – 914 € | 1 | 480 € – 914 € | 1 | 480 € – 914 € |
| **Elettronica dei moduli** | | | **2.937 € – 5.560 €** | | **2.382 € – 4.546 €** |
| Circuiti stampati, un giro (§4) | | | 485 € – 1.065 € | | 485 € – 1.065 € |
| Cablaggio, minuteria, cappucci, scorte (§5) | | | 300 € – 590 € | | 300 € – 590 € |
| Telaio, pannelli, flight case (§6) | | | 1.250 € – 2.550 € | | 1.250 € – 2.550 € |
| Prototipo: millefori e secondo giro di PCB (§7) | | | 411 € – 889 € | | 411 € – 889 € |
| **Totale IVA esclusa** | | | **5.383 € – 10.654 €** | | **4.828 € – 9.640 €** |
| **Totale IVA inclusa (22 %)** | | | **6.567 € – 12.997 €** | | **5.890 € – 11.760 €** |

Setup completo: 4 canali con 4 FX-SEND, 1 MIC, 3 MONO. Setup ridotto: 2
canali con 2 FX-SEND, 1 MIC, 1 MONO (come i disegni in `docs/pannelli/`).
Il telaio è contato uguale nei due: la larghezza è 19" in entrambi.

**Fuori dal totale**: manodopera di montaggio (dipende da chi costruisce,
A8), moduli opzionali (§8), strumenti di misura (§9), spedizioni dei singoli
ordini (~15-30 € per ordine sotto la soglia di spedizione gratuita).

## 2. Dove vanno i soldi

- **Canale CDJ/line con phono**: ~1.136 € al centro della forchetta, 14 % del totale IVA esclusa.
- **FX-RET (un bus, dec. 130)**: ~735 € al centro della forchetta, 9 % del totale IVA esclusa.
- **Alimentatore esterno (box)**: ~697 € al centro della forchetta, 9 % del totale IVA esclusa.
- **5-way**: ~513 € al centro della forchetta, 6 % del totale IVA esclusa.
- **FX-SEND**: ~216 € al centro della forchetta, 3 % del totale IVA esclusa.
- **Telaio e pannelli**: ~1.900 €, 24 %. Sono la voce singola più grande:
  i pannelli incisi a misura costano più di tutto il silicio di un modulo.

Tre fatti che pesano:

1. **I VCA e i loro trimmer.** ~74 chip a 2,80-5 € fanno 210-370 €; ogni
   chip vuole 3 trimmer di taratura (`sistema-vca-trim.md`), cioè ~220
   trimmer. I 4 FX-RET ne portano 12 ciascuno, 48 in tutto.
2. **I prezzi del VCA clone sono deboli.** Non ho trovato oggi un listino
   europeo aggiornato del V2181L: il prezzo viene dai documenti di settembre
   e da un annuncio eBay (~4,30 € a pezzo). Lo stock è a lotti (voce 37).
3. **Il core del filtro (B1) sposta il conto.** Col core PULITO (c-B) il
   filtro sale (§3.1): +16 VCA e +48 trimmer.

## 3. Moduli, riga per riga

### Canale CDJ/line con phono

Fonte delle quantità: cdj-line-channel §6, eq-isolator §5, phono §4. Copie: 4 nel completo, 2 nel ridotto.

| Voce | Qtà | € al pezzo | Totale | Fonte | Note |
|---|---|---|---|---|---|
| OPA1654 quad op-amp | 12 | 1,60 – 2,80 | 19 € – 34 € | M | isolator, 24 sezioni per lato |
| OPA1612 dual op-amp | 7 | 5,50 – 7,50 | 38 € – 52 € | M | somme EQ, buffer, fader, out; phono 2+1 |
| op-amp dual generico (servo, detector) | 1 | 0,60 – 3,00 | 1 € – 3 € | S | servo |
| VCA CoolAudio V2181L | 4 | 2,80 – 5,00 | 11 € – 20 € | D | GAIN 2 + fader 2 (dec. 126) |
| trimmer multigiro | 21 | 0,80 – 2,00 | 17 € – 42 € | S | trim dei VCA 12, incroci 6, shaper del fader 3 |
| ADG1434 quad switch | 1 | 6,00 – 10,00 | 6 € – 10 € | M | LINE/PHONO |
| LM317/337 o 78L15/79L15 | 2 | 0,50 – 1,00 | 1 € – 2 € | D | regolatori locali |
| passivi: banca R 0,1 %, ~60 C di precisione, RIAA | 1 | a corpo | 45 € – 80 € | S |  |
| RCA dorato isolato | 6 | 1,50 – 3,00 | 9 € – 18 € | S | line 4 + phono 2 |
| morsetto di massa phono | 1 | a corpo | 1 € – 3 € | S |  |
| DIN 41612 C96, coppia | 1 | 4,00 – 8,00 | 4 € – 8 € | D |  |
| pot 14 mm singolo (Alps RK14K) | 1 | 0,90 – 2,00 | 1 € – 2 € | S | GAIN |
| pot 14 mm doppio (Alps RK14K) | 4 | 1,10 – 2,50 | 4 € – 10 € | M | EQ, residuo <= 20 ohm (dec. 127) |
| levetta piccola 2 posizioni | 1 | 3,00 – 6,00 | 3 € – 6 € | S | LINE/PHONO |
| levetta sigillata 3 posizioni fisse | 1 | 5,00 – 10,00 | 5 € – 10 € | S | filtro HPF/OFF/LPF |
| ADG1434 quad switch | 1 | 6,00 – 10,00 | 6 € – 10 € | M | instradamento post-fader DJ / HPF / LPF (dec. 159) |
| bottone con luce a ritenuta | 5 | 4,00 – 9,00 | 20 € – 45 € | S | CUE + assign FX 1-4 |
| fader 100 mm mono (Alps RS60N) | 1 | 8,80 – 12,50 | 9 € – 12 € | R |  |
| **Totale** | | | **200 € – 368 €** | | |

### FX-SEND

Fonte delle quantità: fx-send-module §5. Copie: 4 nel completo, 2 nel ridotto.

| Voce | Qtà | € al pezzo | Totale | Fonte | Note |
|---|---|---|---|---|---|
| OPA1654 quad op-amp | 3 | 1,60 – 2,80 | 5 € – 8 € | M |  |
| OPA1612 dual op-amp | 1 | 5,50 – 7,50 | 6 € – 8 € | M |  |
| ADG1434 quad switch | 2 | 6,00 – 10,00 | 12 € – 20 € | M | assign |
| LM317/337 o 78L15/79L15 | 4 | 0,50 – 1,00 | 2 € – 4 € | D |  |
| passivi | 1 | a corpo | 8 € – 15 € | S |  |
| DIN 41612 C96, coppia | 1 | 4,00 – 8,00 | 4 € – 8 € | D |  |
| pot 9 mm doppio (Alps RK09) | 2 | 0,80 – 1,80 | 2 € – 4 € | S | EQ LOW/HIGH |
| pot 14 mm doppio (Alps RK14K) | 1 | 1,10 – 2,50 | 1 € – 2 € | M | LEVEL |
| **Totale** | | | **39 € – 69 €** | | |

### FX-RET (un bus, dec. 130)

Fonte delle quantità: fx-module §2bis, §9, sistema-vca-trim §4. Copie: 4 nel completo, 4 nel ridotto.

| Voce | Qtà | € al pezzo | Totale | Fonte | Note |
|---|---|---|---|---|---|
| VCA CoolAudio V2181L | 12 | 2,80 – 5,00 | 34 € – 60 € | D | reroute 8 (4 bus x L/R) + GAIN 2 + fader 2 |
| trimmer multigiro | 41 | 0,80 – 2,00 | 33 € – 82 € | S | 3 per VCA + shaper |
| OPA1654 quad op-amp | 5 | 1,60 – 2,80 | 8 € – 14 € | M | 3 + 2 per l'iniezione dei reroute sui net |
| OPA1612 dual op-amp | 1 | 5,50 – 7,50 | 6 € – 8 € | M |  |
| JFET dei buffer di ritorno (2) | 1 | a corpo | 1 € – 3 € | S |  |
| shaper delle 5 CV: diodi e resistenze | 1 | a corpo | 4 € – 8 € | S |  |
| LM317/337 o 78L15/79L15 | 2 | 0,50 – 1,00 | 1 € – 2 € | D |  |
| passivi | 1 | a corpo | 10 € – 18 € | S |  |
| jack 6,3 mm Neutrik | 4 | 2,00 – 4,00 | 8 € – 16 € | S | mandata e ritorno del pedale, L/R |
| DIP switch del pad | 2 | 0,80 – 1,50 | 2 € – 3 € | S | pad |
| TVS low-cap | 1 | a corpo | 1 € – 2 € | S |  |
| DIN 41612 C96, coppia | 1 | 4,00 – 8,00 | 4 € – 8 € | D |  |
| pot 14 mm singolo (Alps RK14K) | 1 | 0,90 – 2,00 | 1 € – 2 € | S | GAIN |
| pot 9 mm doppio (Alps RK09) | 2 | 0,80 – 1,80 | 2 € – 4 € | S | EQ |
| fader 100 mm mono (Alps RS60N) | 1 | 8,80 – 12,50 | 9 € – 12 € | R |  |
| pot 9 mm singolo (Alps RK09K) | 4 | 0,35 – 0,70 | 1 € – 3 € | L | reroute verso gli altri bus e SELF, RK09K113004U |
| **Totale** | | | **123 € – 244 €** | | |

### Filtro, core OTA (a')

Fonte delle quantità: filter-module §7, §5ter, §5quater; dec. 159 (4 core sui bus HPF e LPF). Copie: 1 nel completo, 1 nel ridotto.

| Voce | Qtà | € al pezzo | Totale | Fonte | Note |
|---|---|---|---|---|---|
| LM13700 dual OTA | 12 | 0,60 – 2,00 | 7 € – 24 € | L | 4 core a 4 poli + RES |
| OPA1654 quad op-amp | 12 | 1,60 – 2,80 | 19 € – 34 € | M | 10 dei core + ricevitori dei bus |
| VCA CoolAudio V2181L | 4 | 2,80 – 5,00 | 11 € – 20 € | D | overdrive (una cella per lato e sezione) |
| trimmer multigiro | 27 | 0,80 – 2,00 | 22 € – 54 € | S | VCA 12 + frequenza, shaper, RES 15 |
| diodi del limitatore e dello shaper | 1 | a corpo | 2 € – 4 € | S |  |
| condensatore di film 2 % abbinato | 16 | 0,60 – 1,50 | 10 € – 24 € | S | integratori |
| coppia BJT abbinata | 2 | 3,00 – 8,00 | 6 € – 16 € | S | converter |
| ADG1434 quad switch | 1 | 6,00 – 10,00 | 6 € – 10 € | M | muto della sezione senza canali (dec. 159) |
| LT3045 / LT3094 regolatore low-noise | 2 | 4,00 – 6,00 | 8 € – 12 € | D |  |
| LM317/337 o 78L15/79L15 | 2 | 0,50 – 1,00 | 1 € – 2 € | D |  |
| passivi | 1 | a corpo | 25 € – 45 € | S |  |
| DIN 41612 C96, coppia | 1 | 4,00 – 8,00 | 4 € – 8 € | D |  |
| pot 14 mm singolo (Alps RK14K) | 6 | 0,90 – 2,00 | 5 € – 12 € | S | FREQ, RES, DRIVE x 2 |
| **Totale** | | | **126 € – 265 €** | | |

#### 3.1 Variante: core PULITO (c-B) a 4 poli

Differenza rispetto al core (a′), se B1 sceglie il PULITO
(`sim/filtro/RISULTATI-cb-4p.md`). I VCA del mixer salgono da ~74 a
~90: da riverificare anche W1 dell'alimentatore.

| Voce | Qtà | € al pezzo | Totale | Fonte | Note |
|---|---|---|---|---|---|
| VCA CoolAudio V2181L | 16 | 2,80 – 5,00 | 45 € – 80 € | D | 2 per sezione, 4 per core |
| trimmer multigiro | 48 | 0,80 – 2,00 | 38 € – 96 € | S |  |
| OPA1654 quad op-amp | 4 | 1,60 – 2,80 | 6 € – 11 € | M | integratori |
| LM13700 in meno (resta solo la RES) | -8 | 0,60 – 2,00 | -16 € – -5 € | L |  |
| **Totale** | | | **74 € – 182 €** | | |

Filtro col core PULITO: 200 € – 447 €.

### 5-way

Fonte delle quantità: five-way §7, §4.3, §5bis. Copie: 1 nel completo, 1 nel ridotto.

| Voce | Qtà | € al pezzo | Totale | Fonte | Note |
|---|---|---|---|---|---|
| OPA1654 quad op-amp | 36 | 1,60 – 2,80 | 58 € – 101 € | M | banca, celle, gate |
| OPA1612 dual op-amp | 11 | 5,50 – 7,50 | 60 € – 82 € | M | WIDTH 10 + recovery |
| op-amp dual generico (servo, detector) | 2 | 0,60 – 3,00 | 1 € – 6 € | S | servo |
| JFET dual abbinato (classe LSK489) | 20 | 4,00 – 8,00 | 80 € – 160 € | S | celle parametriche |
| ADG1434 quad switch | 3 | 6,00 – 10,00 | 18 € – 30 € | M | kill |
| GROWL e NASTRO: diodi, R, op-amp | 1 | a corpo | 10 € – 20 € | S |  |
| LT3045 / LT3094 regolatore low-noise | 2 | 4,00 – 6,00 | 8 € – 12 € | D |  |
| LM317/337 o 78L15/79L15 | 2 | 0,50 – 1,00 | 1 € – 2 € | D |  |
| passivi: banca R 0,1 %, C di film | 1 | a corpo | 60 € – 100 € | S |  |
| trimmer multigiro | 20 | 0,80 – 2,00 | 16 € – 40 € | S |  |
| DIN 41612 C96, coppia | 1 | 4,00 – 8,00 | 4 € – 8 € | D |  |
| pot 14 mm doppio (Alps RK14K) | 12 | 1,10 – 2,50 | 13 € – 30 € | M | GAIN 5 + WIDTH 5 + GROWL/NASTRO 2 |
| pot 14 mm singolo (Alps RK14K) | 5 | 0,90 – 2,00 | 4 € – 10 € | S | POSITION |
| levetta sigillata ON-OFF-(ON) | 5 | 6,00 – 12,00 | 30 € – 60 € | S | KILL |
| **Totale** | | | **364 € – 661 €** | | |

### Master out (con booth e MONO)

Fonte delle quantità: master-out §5. Copie: 1 nel completo, 1 nel ridotto.

| Voce | Qtà | € al pezzo | Totale | Fonte | Note |
|---|---|---|---|---|---|
| VCA CoolAudio V2181L | 5 | 2,80 – 5,00 | 14 € – 25 € | D | master 2, booth 2, MONO 1 |
| trimmer multigiro | 15 | 0,80 – 2,00 | 12 € – 30 € | S |  |
| OPA1612 dual op-amp | 7 | 5,50 – 7,50 | 38 € – 52 € | M | con buffer MON del CUE |
| op-amp dual generico (servo, detector) | 2 | 0,60 – 3,00 | 1 € – 6 € | S | servo |
| transistor diamond e bootstrap, diodi, CRD | 1 | a corpo | 8 € – 15 € | S |  |
| rele' di segnale | 3 | 2,00 – 4,00 | 6 € – 12 € | D | mute |
| LT3045 / LT3094 regolatore low-noise | 4 | 4,00 – 6,00 | 16 € – 24 € | D |  |
| LM317/337 o 78L15/79L15 | 3 | 0,50 – 1,00 | 2 € – 3 € | D |  |
| XLR Neutrik da pannello | 4 | 1,80 – 4,50 | 7 € – 18 € | M | master L/R, booth L/R |
| jack 6,3 mm Neutrik | 2 | 2,00 – 4,00 | 4 € – 8 € | S | rec |
| passivi | 1 | a corpo | 15 € – 30 € | S |  |
| DIN 41612 C96, coppia | 1 | 4,00 – 8,00 | 4 € – 8 € | D |  |
| pot 14 mm singolo (Alps RK14K) | 2 | 0,90 – 2,00 | 2 € – 4 € | S | MASTER, BOOTH |
| bottone con luce a ritenuta | 1 | 4,00 – 9,00 | 4 € – 9 € | S | MONO |
| **Totale** | | | **133 € – 244 €** | | |

### CUE e cuffie

Fonte delle quantità: sistema-cue §10. Copie: 1 nel completo, 1 nel ridotto.

| Voce | Qtà | € al pezzo | Totale | Fonte | Note |
|---|---|---|---|---|---|
| OPA1612 dual op-amp | 3 | 5,50 – 7,50 | 16 € – 22 € | M |  |
| transistor finali e limitatori | 1 | a corpo | 4 € – 8 € | S |  |
| generatore di corrente (CRD / LM334) | 4 | 0,50 – 1,50 | 2 € – 6 € | S |  |
| LT3045 / LT3094 regolatore low-noise | 4 | 4,00 – 6,00 | 16 € – 24 € | D |  |
| LM317/337 o 78L15/79L15 | 4 | 0,50 – 1,00 | 2 € – 4 € | D |  |
| rele' di segnale | 2 | 2,00 – 4,00 | 4 € – 8 € | D |  |
| resistenze di potenza | 1 | a corpo | 4 € – 8 € | S |  |
| pot 14 mm doppio (Alps RK14K) | 1 | 1,10 – 2,50 | 1 € – 2 € | M | BLEND |
| pot 9 mm doppio (Alps RK09) | 1 | 0,80 – 1,80 | 1 € – 2 € | S | LEVEL |
| jack 6,3 mm Neutrik | 2 | 2,00 – 4,00 | 4 € – 8 € | S | cuffie, dec. 128 |
| passivi | 1 | a corpo | 8 € – 15 € | S |  |
| DIN 41612 C96, coppia | 1 | 4,00 – 8,00 | 4 € – 8 € | D |  |
| **Totale** | | | **66 € – 116 €** | | |

### Metering (tutte le barre)

Fonte delle quantità: sistema-metering §6. Copie: 1 nel completo, 1 nel ridotto.

| Voce | Qtà | € al pezzo | Totale | Fonte | Note |
|---|---|---|---|---|---|
| LM3915 driver di barra | 13 | 2,00 – 4,50 | 26 € – 58 € | M |  |
| op-amp dual generico (servo, detector) | 12 | 0,60 – 3,00 | 7 € – 36 € | S | detector |
| LM339 comparatore quad | 3 | 0,30 – 0,60 | 1 € – 2 € | S |  |
| LED dei meter | 150 | 0,08 – 0,20 | 12 € – 30 € | S |  |
| passivi e trimmer | 1 | a corpo | 12 € – 25 € | S |  |
| **Totale** | | | **58 € – 151 €** | | |

### MIC

Fonte delle quantità: mic-mono-moduli §8. Copie: 1 nel completo, 1 nel ridotto.

| Voce | Qtà | € al pezzo | Totale | Fonte | Note |
|---|---|---|---|---|---|
| OPA1612 dual op-amp | 3 | 5,50 – 7,50 | 16 € – 22 € | M |  |
| OPA1654 quad op-amp | 3 | 1,60 – 2,80 | 5 € – 8 € | M |  |
| ADG1434 quad switch | 1 | 6,00 – 10,00 | 6 € – 10 € | M |  |
| LM339 comparatore quad | 1 | 0,30 – 0,60 | 0 € – 1 € | S |  |
| VCA CoolAudio V2181L | 1 | 2,80 – 5,00 | 3 € – 5 € | D | MUTE |
| trimmer multigiro | 3 | 0,80 – 2,00 | 2 € – 6 € | S |  |
| LM317/337 o 78L15/79L15 | 4 | 0,50 – 1,00 | 2 € – 4 € | D |  |
| LT3045 / LT3094 regolatore low-noise | 2 | 4,00 – 6,00 | 8 € – 12 € | D |  |
| LED tricolore | 1 | 0,50 – 1,50 | 0 € – 2 € | S |  |
| XLR Neutrik da pannello | 1 | 1,80 – 4,50 | 2 € – 4 € | M |  |
| bottone con luce a ritenuta | 1 | 4,00 – 9,00 | 4 € – 9 € | S | MUTE |
| pot 14 mm singolo (Alps RK14K) | 5 | 0,90 – 2,00 | 4 € – 10 € | S | GAIN (curva C) + SEND 1-4 |
| pot 9 mm singolo (Alps RK09K) | 2 | 0,35 – 0,70 | 1 € – 1 € | L | EQ |
| passivi | 1 | a corpo | 10 € – 20 € | S |  |
| DIN 41612 C96, coppia | 1 | 4,00 – 8,00 | 4 € – 8 € | D |  |
| **Totale** | | | **68 € – 123 €** | | |

### MONO

Fonte delle quantità: mic-mono-moduli §8. Copie: 3 nel completo, 1 nel ridotto.

| Voce | Qtà | € al pezzo | Totale | Fonte | Note |
|---|---|---|---|---|---|
| OPA1612 dual op-amp | 1 | 5,50 – 7,50 | 6 € – 8 € | M |  |
| OPA1654 quad op-amp | 3 | 1,60 – 2,80 | 5 € – 8 € | M |  |
| ADG1434 quad switch | 1 | 6,00 – 10,00 | 6 € – 10 € | M |  |
| LM339 comparatore quad | 1 | 0,30 – 0,60 | 0 € – 1 € | S |  |
| LM317/337 o 78L15/79L15 | 4 | 0,50 – 1,00 | 2 € – 4 € | D |  |
| LED tricolore | 1 | 0,50 – 1,50 | 0 € – 2 € | S |  |
| jack 6,3 mm Neutrik | 1 | 2,00 – 4,00 | 2 € – 4 € | S |  |
| pot 14 mm singolo (Alps RK14K) | 5 | 0,90 – 2,00 | 4 € – 10 € | S | GAIN + SEND 1-4 |
| pot 9 mm singolo (Alps RK09K) | 2 | 0,35 – 0,70 | 1 € – 1 € | L | EQ |
| passivi | 1 | a corpo | 8 € – 15 € | S |  |
| DIN 41612 C96, coppia | 1 | 4,00 – 8,00 | 4 € – 8 € | D |  |
| **Totale** | | | **38 € – 70 €** | | |

### Backplane

Fonte delle quantità: sistema-backplane §8. Copie: 1 nel completo, 1 nel ridotto.

| Voce | Qtà | € al pezzo | Totale | Fonte | Note |
|---|---|---|---|---|---|
| fusibile PTC | 15 | 0,30 – 0,80 | 4 € – 12 € | S | uno per slot |
| bypass e bulk per slot | 1 | a corpo | 15 € – 30 € | S |  |
| **Totale** | | | **20 € – 42 €** | | |

### PSU-IN e ventole (nel mixer)

Fonte delle quantità: sistema-psu-esterno §4. Copie: 1 nel completo, 1 nel ridotto.

| Voce | Qtà | € al pezzo | Totale | Fonte | Note |
|---|---|---|---|---|---|
| TVS di ingresso | 1 | a corpo | 4 € – 8 € | S |  |
| fusibile con portafusibile | 5 | 1,00 – 3,00 | 5 € – 15 € | S | fusibili di gruppo |
| condensatori 2,2 mF + 3 x 1 mF | 1 | a corpo | 10 € – 20 € | S |  |
| supervisor: comparatori, riferimento | 1 | a corpo | 8 € – 15 € | S |  |
| ventola 80 mm silenziosa | 2 | 12,00 – 20,00 | 24 € – 40 € | S | dec. 112 |
| termostato delle ventole | 1 | a corpo | 5 € – 10 € | S |  |
| **Totale** | | | **56 € – 108 €** | | |

### Alimentatore esterno (box)

Fonte delle quantità: sistema-psu-esterno §2. Copie: 1 nel completo, 1 nel ridotto.

| Voce | Qtà | € al pezzo | Totale | Fonte | Note |
|---|---|---|---|---|---|
| toroidale ~420 VA, 4 secondari, schermo, su misura (dec. 131) | 1 | a corpo | 170 € – 280 € | S |  |
| bulk: 2 x 22 mF, 3 x 10 mF, 2 x 4,7 mF, 35 V 105 C | 1 | a corpo | 75 € – 135 € | S |  |
| ponte raddrizzatore | 4 | 2,00 – 5,00 | 8 € – 20 € | S |  |
| LDO discreti: MOSFET, riferimenti, op-amp | 1 | a corpo | 25 € – 45 € | S |  |
| aletta, Rth <= 0,43 K/W | 1 | a corpo | 30 € – 60 € | S |  |
| contenitore metallico | 1 | a corpo | 60 € – 130 € | S |  |
| presa IEC con filtro, interruttore, fusibile | 1 | a corpo | 15 € – 30 € | S |  |
| soft-start NTC e rele' | 1 | a corpo | 8 € – 15 € | S |  |
| fusibile con portafusibile | 6 | 1,00 – 3,00 | 6 € – 18 € | S |  |
| connettore circolare IP65 >= 20 poli + PE, coppia | 1 | a corpo | 60 € – 130 € | S |  |
| cavo schermato multipolare 2 m | 1 | a corpo | 20 € – 45 € | S |  |
| rivelatore AC_OK | 1 | a corpo | 3 € – 6 € | S |  |
| **Totale** | | | **480 € – 914 €** | | |

## 4. Circuiti stampati

Un giro di prototipo: 5 copie per disegno (il minimo dei produttori come
JLCPCB), 2 strati salvo dove indicato, spedizione e dazio compresi.
Stima di Claude: i listini a superficie non valgono per schede così grandi.

| Scheda | € |
|---|---|
| canale CDJ | 35 € – 70 € |
| FX-SEND | 20 € – 45 € |
| ritorno FX (un disegno, 4 copie) | 35 € – 80 € |
| filtro (4 strati) | 70 € – 150 € |
| 5-way (4 strati) | 70 € – 150 € |
| master out | 35 € – 70 € |
| CUE | 20 € – 45 € |
| metering | 35 € – 70 € |
| MIC | 20 € – 45 € |
| MONO | 20 € – 45 € |
| backplane (~75 cm, in due pezzi) | 80 € – 200 € |
| PSU-IN | 20 € – 45 € |
| box | 25 € – 50 € |
| **Totale** | **485 € – 1.065 €** |

## 5. Voci comuni

| Voce | Qtà | € al pezzo | Totale | Fonte | Note |
|---|---|---|---|---|---|
| cablaggio pannello-schede: cavetti, connettori, schermati | 1 | a corpo | 120 € – 250 € | S |  |
| minuteria: viti, distanziali, staffe | 1 | a corpo | 50 € – 100 € | S |  |
| cappucci delle 115 manopole, stampa 3D (dec. 124) | 1 | a corpo | 20 € – 40 € | S |  |
| scorte: 22 VCA in piu' (lotto ~100), passivi di riserva | 1 | a corpo | 110 € – 200 € | S |  |
| **Totale** | | | **300 € – 590 €** | | |

Cappucci: se invece di stamparli si comprano a catalogo, 1,5-3 € l'uno,
cioè 170-350 € per 115 manopole.

## 6. Telaio

| Voce | Qtà | € al pezzo | Totale | Fonte | Note |
|---|---|---|---|---|---|
| pannelli frontali in alluminio incisi (~0,3 m2, Schaeffer) | 1 | a corpo | 800 € – 1.500 € | W |  |
| struttura interna e fondo in alluminio | 1 | a corpo | 200 € – 450 € | S |  |
| flight case su misura | 1 | a corpo | 250 € – 600 € | W |  |
| **Totale** | | | **1.250 € – 2.550 €** | | |

Pannelli: Schaeffer chiede ~140 € IVA inclusa per un pannello inciso di
18 × 18 cm, cioè ~0,35-0,45 € al cm² IVA esclusa. Il frontale del
mixer completo è ~45 × 65 cm. Alternativa da chiedere: un'officina CNC
locale con stampa UV, forse metà prezzo. Il flight case di serie per
mixer da 19" inclinato costa ~250-300 €; su misura per la profondità del
mixer, di più. Misure e nome sul telaio restano dopo il prototipo (A10).

## 7. Prototipo

Regola 5 del progetto: fase 1 su millefori (canale, FX, master, PSU base)
prima di qualunque PCB. I componenti della fase 1 si riusano. Il secondo
giro di PCB (rev. B) è prudente: quasi ogni scheda nuova ne chiede uno.

- millefori e minuteria: 120 € – 250 €
- secondo giro di PCB, 60 % del primo: 291 € – 639 €

## 8. Moduli opzionali (dec. 111)

### Crossfader (dec. 111)

| Voce | Qtà | € al pezzo | Totale | Fonte | Note |
|---|---|---|---|---|---|
| VCA CoolAudio V2181L | 8 | 2,80 – 5,00 | 22 € – 40 € | D |  |
| trimmer multigiro | 24 | 0,80 – 2,00 | 19 € – 48 € | S |  |
| OPA1654 quad op-amp | 2 | 1,60 – 2,80 | 3 € – 6 € | M |  |
| fader 100 mm mono (Alps RS60N) | 1 | 8,80 – 12,50 | 9 € – 12 € | R |  |
| passivi + PCB | 1 | a corpo | 30 € – 60 € | S |  |
| **Totale** | | | **84 € – 166 €** | | |

EQ grafico, uscite per via e sirena: non progettati, quindi non stimati.

## 9. Strumenti di misura (A11, rinviata)

Non fanno parte del mixer: servono al banco. Lo Zoom e una scheda audio con
REW bastano per le misure audio (voce 30).

| Voce | Qtà | € al pezzo | Totale | Fonte | Note |
|---|---|---|---|---|---|
| oscilloscopio a 4 canali di fascia bassa | 1 | a corpo | 350 € – 500 € | S |  |
| multimetro | 1 | a corpo | 60 € – 150 € | S |  |
| stazione saldante | 1 | a corpo | 80 € – 200 € | S |  |
| alimentatore da banco duale | 1 | a corpo | 100 € – 200 € | S |  |
| trasformatore d'isolamento o variac | 1 | a corpo | 120 € – 250 € | S |  |
| **Totale** | | | **710 € – 1.300 €** | | |

## 10. Cosa può cambiare il conto

- **B1, core del filtro**: il PULITO aggiunge la cifra del §3.1.
- **Prezzo e stock del VCA clone**: ±1 € a pezzo vale ±100 € sul lotto.
- **Pannelli**: Schaeffer o officina locale, una forchetta da centinaia di euro.
- **Chi monta (A8)**: montaggio SMT dal produttore delle PCB toglie ore di
  saldatura ma costa a parte, da preventivare.
- **Pot doppio da 1k del WIDTH**: se non esiste a 14 mm, il circuito passa
  a 10k (todo aperto in five-way §4.3), costo quasi uguale.
- **Taratura**: nessun costo di materiale, ma ~230 trimmer da regolare a
  banco sono giorni di lavoro.

## Fonti

- **M**: Mouser / DigiKey, prezzi letti il 2026-10-22 (pezzo singolo e lotto da 100).
- **L**: LCSC, prezzi letti il 2026-10-22.
- **R**: RS Components, prezzi letti il 2026-10-22.
- **W**: listini e gallerie di Schaeffer AG e di negozi di flight case, letti il 2026-10-22.
- **D**: prezzi gia' raccolti nei documenti del progetto (settembre-ottobre 2026).
- **S**: stima di Claude, senza preventivo.

Pagine lette il 2026-10-22: Mouser OPA1612AID ($7,63-8,47 a 1 pz),
OPA1654 ($2,81 a 1 pz, ~$1,5 a 500), Alps RK14K1240036 (Mouser FR
~2,24 € a 1 pz), Alps RK09K113004U (LCSC $0,31-0,67), Alps RS60N 100 mm
(RS NL 12,46 € a 1 pz, 8,83 € a 100), Neutrik NC3FAH ($1,90), ADG1434YRUZ
(Richardson $6,69), LM3915N-1 (Win Source ~$2, Farnell ~$3,35), LM13700
(LCSC $0,60), toroidale Block 300 VA 2 × 18 V (RS 137 €), Schaeffer AG
galleria prezzi, ProDJuser Slant 19" (259 €).
