# Converter esponenziale a componenti (todo 337, 2026-11-16) [SIMULATO, PROVVISORIO]

Il §4 di `docs/fase2/filter-module.md` aveva il converter solo come sorgente ideale
(`feas-svf.cir`: ΔV da una sorgente B, collettore di Q2 verso un pin che restituisce
corrente). Per la scheda serve il circuito vero. Due fatti lo vincolano:

- il pin Iabc dell'LM13700 **assorbe** corrente (datasheet TI SNOSBW2F; modello
  `sim/lib/lm13700.inc`): un collettore NPN non può alimentarlo, serve una sorgente
  che spinge, cioè un PNP o un mirror PNP;
- il mirror bufferizzato del §4 vuole fino a 5 uscite appaiate per core (4 OTA + il
  riferimento): nessun array a 5 transistor appaiati sullo stesso die è a catalogo.

## Circuito (`conv-that320.cir`)

Un converter per sezione 2 poli (due OTA), quindi due per core e quattro per scheda.

```
sh (shaper, 0,5 V/ottava, -5,40 V a 35 kHz) ─ 10k ─┐
+5 V rif ─ 8,87k + trimmer 1k (zero) ──────────────┼─ Xw (Rf 10k): w = -(sh + 5,40 V)
w ─ 24,3k + trimmer 5k (scala) ─┬─ 1k tempco +3300 ppm/K ─ massa
                                └─ buffer ─► basi dei Q1 (4 converter della scheda)
THAT 320: Q1 rif. (B = comando, C = cr), Q2 e Q3 uscite (B a massa, C ─► pin Iabc)
cr ─ LM334 (Rset 150 Ω + trimmer 100 Ω, PTAT) ─ -15 V
OPA1642: + a massa, - su cr, uscita ─ 2,2k ─ emettitori; 1n uscita-cr; diodo massa → emettitori
```

- Il comando entra sulla base del riferimento: Ic2 = Iref · exp(Vb1/VT). Le basi delle
  uscite stanno a massa, le loro correnti di base non toccano il comando. La corrente di
  base di Q1 è costante (Q1 porta sempre Iref): finisce nello zero.
- Un buffer solo per scheda pilota le quattro basi Q1: L e R vedono lo stesso comando.
- Taratura per converter: un trimmer su Rset (fondo scala). Per scheda: zero e scala.

## Misure

Corrente nel pin Iabc (μA) lungo la corsa, Rset 169 Ω:

| sh | Frequenza | 20 °C | 35 °C | 50 °C | Rapporto 50/20 |
|---|---|---|---|---|---|
| +0,5 V | 10 Hz | 0,134 | 0,144 | 0,153 | 1,144 |
| 0 V | 20 Hz | 0,269 | 0,288 | 0,307 | 1,141 |
| -1,5 V | 158 Hz | 2,19 | 2,33 | 2,47 | 1,130 |
| -2,83 V | 1 kHz | 14,0 | 14,8 | 15,7 | 1,120 |
| -4,49 V | 10 kHz | 140 | 148 | 156 | 1,109 |
| -5,40 V | 35 kHz | 485 | 509 | 534 | 1,103 |

- **PTAT**: il rapporto ideale è 323,15/293,15 = 1,102 (gm costante). In cima 1,103;
  in fondo 1,144: +3,8 % in 30 K a 10 Hz, ±2 % attorno a 35 °C. Dentro la tolleranza
  ±5-10 % (dec. 74). Una tempco da +3500 ppm/K lo stringe.
- **Ottave**: 10 → 20 Hz ×2,006; 1 → 10 kHz ×9,98 (atteso 9,99); 20 Hz → 1 kHz +1,8 %
  (trimmer di scala); in cima −2,5 % (resistenze di base ed emettitore a 500 μA).
- **Fondo scala**: con w = 0 la corrente è 1,23 × Iref (effetto Early: Vce di Q2 ~14 V,
  Vaf 60 V nel modello, il datasheet non lo dà). Il trimmer di Rset (150 + 100 Ω,
  Iref 271-451 μA) copre Vaf da 60 V a infinito.
- **Q2 e Q3 uguali** nel modello (transistor identici); il datasheet dà |VBE1-VBE2| 0,5 mV
  tipici solo per le coppie 1-2 e 3-4: 0,5 mV = 2 % fra i due OTA di una sezione, cioè
  1 % sul Q. Inudibile.
- **Anello** (`conv-that320-tran.cir`, gradino 158 Hz ↔ 35 kHz a 35 °C): nessuna
  sovraelongazione (509,47 contro 509,47 μA), emettitori mai sotto +0,52 V. Taglio
  dell'anello ~72 kHz (2,2k · 1n), lontano dal GBW dell'OPA1642 (11 MHz): la macro a un
  polo qui non nasconde niente.

## Cosa resta

- Vaf e β veri del THAT 320 a banco (trimmer già dimensionati).
- La resistenza tempco: valore e coefficiente da confermare con la reperibilità (todo 13).
  Va incollata termicamente ai THAT 320; sulla scheda sta in mezzo ai quattro.
- Pre-distorsione del §4: non serve più come rete a parte (errore residuo ≤ 2,5 %).
