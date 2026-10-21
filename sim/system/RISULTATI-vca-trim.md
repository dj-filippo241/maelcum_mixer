# RISULTATI — trim di law delle coppie di VCA (2026-10-21, todo 17)

Design: `docs/fase3/sistema-vca-trim.md`.

## File

- `vca_trim.py`: calcola i trim di ogni coppia peggiore, scrive
  `vca-trim-casi.cir`, legge il suo log, fa il Monte Carlo
  dell'abbinamento. Python puro.
- `vca-trim-casi.cir`: GENERATO. Coppia L/R con partitore 1,00k/1,00k
  (L) e 900 + trimmer 200 Ω / 1,00k (R), offset da ±15 V su 1,5 MΩ.
  Chip comportamentale: G = −Vpin/k + d0 + c·g² (k, d0, linearità per
  chip, dal datasheet THAT 2181). `.step` su trimmer (metà corsa /
  calcolati), 5 coppie, 7 guadagni; `.ac` a 1 kHz.

Comandi:

```bash
python3 sim/system/vca_trim.py
sim/run_ltspice.sh sim/system/vca-trim-casi.cir
python3 sim/system/vca_trim.py sim/system/vca-trim-casi.log
```

## 1. Trimmer

| | Valore |
|---|---|
| Divisore nominale | a = 0,500 (shaper ×2) |
| Escursione scala | −5,2 / +4,8 % di k |
| Un giro di scala | 0,159 dB a −40 dB |
| Escursione offset | ±0,82 dB |
| Un giro di offset | 0,066 dB |

## 2. Scarto R − L (dB), LTspice

```
caso                                   +10      +0     -10     -20     -40     -60     -80
trimmer a meta corsa
  THAT C, k e d0 opposti            +0.069  +0.400  +0.731  +1.062  +1.725  +2.387  +3.050
  THAT C, rovescio                  -0.075  -0.400  -0.725  -1.049  -1.698  -2.347  -2.997
  clone 5,8/6,3: fuori campo        -0.438  +0.400  +1.238  +2.076  +3.752  +5.428  +7.103
  THAT C + linearita 0,5 % typ      +0.077  +0.400  +0.739  +1.095  +1.854  +2.678  +3.566
  THAT C + linearita 2 % max        +0.101  +0.400  +0.763  +1.191  +2.241  +3.548  +5.114
trimmer ai valori calcolati
  THAT C, k e d0 opposti            -0.000  -0.000  -0.000  -0.000  +0.000  +0.000  +0.000
  THAT C, rovescio                  +0.000  +0.000  +0.000  +0.000  +0.000  -0.000  -0.000
  clone 5,8/6,3: fuori campo        -0.328  +0.000  +0.328  +0.657  +1.313  +1.970  +2.626
  THAT C + linearita 0,5 % typ      +0.043  -0.000  -0.026  -0.035  +0.000  +0.104  +0.278
  THAT C + linearita 2 % max        +0.177  -0.000  -0.106  -0.142  +0.000  +0.425  +1.134
```

Il calcolo in Python dà gli stessi numeri alla terza cifra: il carico
della 1,5 MΩ e del partitore è nel netlist e nel calcolo.

Posizioni dei trimmer (giri su 25): coppia 1 scala 4,4 / offset 18,9;
coppia 2 scala 20,7 / offset 6,7. Coppia 3: scala a fondo corsa.

## 3. Abbinamento senza trim di law (Monte Carlo)

Lotto 62 chip, k uniforme ±3 % attorno a 6,1 mV/dB, d0 uniforme
±0,2 dB, 200 lotti. Abbinamento: ordina per k, gruppi di 4, dentro il
gruppo per d0. Scarto massimo da +10 a −60 dB: **86 % delle coppie
≤ 0,25 dB, 100 % ≤ 0,5 dB**. Non include la linearità.

## Non verificato

- Il modello non ha THD, rumore, feedthrough della CV: la simmetria si
  tara a banco sulla THD.
- Dispersione vera del clone: non pubblicata. Il ±3 % del Monte Carlo è
  un'ipotesi (il THAT dichiara ±1,6 %).
- Corrente di bias dei pin EC: non modellata (§8 del design).
