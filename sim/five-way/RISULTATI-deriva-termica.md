# RISULTATI — deriva termica delle celle JFET e servo replica (todo 50)

Data: 2026-10-14. Design: `docs/fase2/five-way-module.md` §4.2, REV todo 50.

| netlist | cosa misura |
|---|---|
| `cell-v021-temp.cir` | cella v0.2.1 attuale, Vcm fisso, 35 / 50 / 65 °C |
| `cell-v021-replica-a.cir` | servo replica, replica nello stesso chip del JFET di segnale |
| `cell-v021-replica-b.cir` | servo replica, un replica per banda su un altro chip (ΔVt +20 mV, coefficienti termici −10 %) |

Coefficienti di classe dei JFET (dual N a basso rumore): Vtotc = −2,2 mV/K,
Betatce = −0,6 %/K. Non sono il datasheet di un pezzo: vanno misurati a banco.
Tnom = 35 °C (taratura). Banda EQ3, C = 56 nF.

## 1. Cella attuale: le due derive hanno segno opposto

g = 2β(Vcm − Vt). A caldo la soglia scende (l'overdrive Vcm − Vt cresce) e β
cala. Le due si annullano a overdrive ~0,37 V.

| f0 a 35 °C | Vcm − Vt | 50 °C | 65 °C | 65 °C in semitoni |
|---|---|---|---|---|
| 250 Hz | 0,25 V | +3,3 % | +5,3 % | +0,90 |
| 375 Hz | 0,38 V | −0,7 % | −1,9 % | −0,34 |
| 700 Hz | 0,71 V | −4,3 % | −8,7 % | −1,57 |
| 1000 Hz | 1,02 V | −5,6 % | −11,0 % | −2,01 |
| 1500 Hz | 1,53 V | −6,6 % | −12,8 % | −2,37 |

Il finding di `sim/system/RISULTATI-dec111.md` contava solo la soglia
(«fino a ~4 semitoni a inizio corsa»). Con β la deriva è minore in basso e
maggiore in alto. Il rimedio proposto allora (JFET di riferimento a soglia
nel buffer Vcm) toglie solo la parte della soglia: resterebbe il −16 % di β
ovunque (~−3 semitoni). **Scartato.**

## 2. Servo replica

Un JFET replica, bootstrappato come le celle, lavora con Vds fisso 100 mV.
Un op-amp integratore regola vc2 (= 2 Vcm) finché la corrente del replica
vale Ictl (dallo shaper, V/R di precisione). Allora g = Ictl / 100 mV:
soglia e β escono dal conto. Ictl per banda EQ3: 8,80 / 13,19 / 24,63 /
35,19 / 52,78 µA.

| f0 a 35 °C | Oggi, 65 °C | A: replica stesso chip | B: replica altro chip |
|---|---|---|---|
| 250 Hz | +0,90 semit. | 0,00 | −0,86 (f0 statico 269,5 Hz: offset da tarare) |
| 375 Hz | −0,34 | 0,00 | −0,69 |
| 700 Hz | −1,57 | 0,00 | −0,51 |
| 1000 Hz | −2,01 | 0,00 | −0,45 |
| 1500 Hz | −2,37 | 0,00 | −0,41 |

- Variante A: law esatta (249,9 / 374,8 / 699,8 / 999,6 / 1499,5 Hz) e
  deriva nulla nel modello. Nel componente vero il limite è l'appaiamento
  termico dentro il dual (classe 1 %): ~0,05 semitoni stimati.
- Variante B: la differenza di coefficienti tra due chip resta. Con il 10 %
  di differenza (caso sfavorevole) la deriva vale −0,4…−0,9 semitoni:
  meglio di oggi in alto, peggio in basso.
- Nota di simulazione: il `.op` delle varianti replica fallisce il Newton
  diretto e il Gmin stepping, poi converge (source stepping). I valori di f0
  coincidono con la law teorica: il punto di lavoro è quello giusto.
