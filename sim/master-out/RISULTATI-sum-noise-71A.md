# RISULTATI — Master summing + level VCA: budget rumore (coda 71A, 2026-10-01)

Netlist: `sum-noise-71A.cir`. Metodo §8.9: densità .noise 10 punti
20 Hz-20 kHz + trapezoidale python + A-wtd IEC 61672. Mai INTEG.
Macro OP1612 reale (Rn 73). Lo stadio finale composite NON è incluso:
già misurato −119,2 dBu (Test 10, compB-noise.cir, VALIDO).

## Punto di misura e condizioni

- **vsum** = uscita [A2] MASTER SUMMING (master-out.md §3.1): inverting
  OPA1612, 8 ingressi R_in 20k, Rf 20k unity, Cf 10p. Contributori
  terminati = segnale nullo da uscite a Z bassa: ogni ramo = 0 V → 20k →
  virtual earth (la Rs 20k aggiuntiva vale solo per gli ingressi NON
  usati — qui il caso peggiore, tutti e 8 i rami attivi-terminati).
- **vml** = dopo [D] MASTER LEVEL: THAT 218x a unity (0 dB, detent),
  floor datasheet −98 dBV 20-20k (Rout 20k, senza I/V) → Rvn 476k
  (88,9 nV/√Hz), iniezione E lineare 4 nodi; carico = Rsrc 1k del
  composite. Composizione summing+VCA analitica (sorgenti incorrelate):
  √(54,6² + 88,9²) = 104,3 nV/√Hz.

## Risultati

| Nodo | Densità | Unweighted | A-weighted |
|---|---|---|---|
| vsum (solo summing) | 54,6 nV/√Hz piatta | 7,72 µV = **−100,0 dBu** | **−101,9 dBu A-wtd** |
| level VCA da solo (modello datasheet) | 88,9 nV/√Hz | 12,57 µV = −95,8 dBu | −97,7 dBu A-wtd |
| **vml (summing + level VCA)** | 104,3 nV/√Hz | 14,75 µV = **−94,4 dBu** | **−96,3 dBu A-wtd** |

Ripartizione summing (analitica, conferma 54,6): 8 rami 20k (51,5 nV,
87% potenza) · Rf 20k (18,2 nV, 11%) · op-amp NG 9 (9,9 nV, 3%).

## Verdetto sull'assunzione docs/06 §2

**TRASCRURABILE: confermato.** Il sistema alla XLR sta ≈ −78 dBu A-wtd
(docs/06 §2): summing + level VCA a −96,3 sono **18,3 dB sotto** →
+0,06 dB al totale. Il summing da solo è 24 dB sotto. Il level VCA è il
pezzo più "rumoroso" del modulo master ma resta ininfluente sul sistema
(il master out residuo −119,2 pure).

## Assunzioni

- Master level a unity (detent): a +6 dB il floor VCA sale di 6 dB e il
  gain del summing a valle no → il contributo relativo peggiora di 6 dB
  (−90,3 A-wtd): resta 12 dB sotto il sistema. A −30 dB migliora.
- Il VCA è modellato al floor −98 dBV SENZA I/V (config §3.2: il VCA
  pilota Rsrc 1k, non un I/V 10k): se il design finale mettesse un I/V,
  il floor scenderebbe a −104 dBV (−3,7 dB sul composto).
- Booth (presa pre-level, §3.2 doc): vede solo il summing (−101,9 A-wtd).
- Prima stesura del netlist aveva una Rs 20k spuria per ramo (errore di
  lettura del doc: −3 dB ottimistico, −104,1 A-wtd il summing): corretta
  e rerunnata; i numeri qui sopra sono della versione corretta.
