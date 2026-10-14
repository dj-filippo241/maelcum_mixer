# RISULTATI — Iref PTAT del converter (todo 50)

Data: 2026-10-14. Netlist: `ota-iref-ptat.cir` (modello LM13700 reale,
`../lib/lm13700.inc`). Design: `docs/fase2/filter-module.md` §4, REV todo 50.

gm dell'OTA con Iabc fissa (k = 0) contro Iabc ∝ T assoluta (k = 1),
taratura a 35 °C. Deriva rispetto a 35 °C:

| Iabc a 35 °C | Iref fissa 50 °C | Iref fissa 65 °C | Iref PTAT 50 °C | Iref PTAT 65 °C |
|---|---|---|---|---|
| 7,56 µA (fondo corsa) | −4,6 % | −8,9 % | 0,00 % | 0,00 % |
| 100 µA | −4,6 % | −8,8 % | −0,02 % | −0,04 % |
| 500 µA (cima) | −4,6 % | −8,6 % | −0,11 % | −0,23 % |

Iref fissa: −8,6…−8,9 % = ~1,6 semitoni da 35 a 65 °C. Iref PTAT: ≤ 0,23 %
= ≤ 0,04 semitoni. Il residuo a 500 µA viene dagli effetti di secondo
ordine del modello (beta finito del mirror di coda).

Limite del modello: la sorgente PTAT è ideale (B-source ∝ T). Nel circuito
la classe LM334 è PTAT per fisica (227 µV/K × T / Rset); l'errore vero è il
gradiente termico tra l'LM334 e gli LM13700: 0,33 % per ogni kelvin di
differenza.
