# RISULTATI — WIDTH continuo della cella EQ (decisione 117, 2026-10-21)

Cella v0.2.1 (EQ3, C 56n, Vcm −1,2881 = 700 Hz) con il solo damping cambiato.
Design: `docs/fase2/five-way-module.md` §4.3.

## Topologia provata

Pot WIDTH 1k come partitore su bp_b (alpha 0,1…1) → buffer non invertente ×10
(OPA1612, 1,8k/200) → dq = 10·alpha·bp_b → invertitore OPA1612 (2k/2k) → −dq.
Damping da −dq con R0 30k: Q = R0/(10·alpha·Rf) = 0,3/alpha. Il pot GAIN sta
tra +dq e −dq, iniezione Rbw 1,623k fissa. dq vale già 3·BP_norm: il boost non
dipende da Q, senza secondo deck.

## AC — `cell-v022-width.cir`

Q misurato dalla banda a −3 dB di bp. Boost = massimo di vout.

| alpha | Q | notch (b −1) | detent (b 0) | +9 (b 1,82) | +12 (b 3,0) | +15 (b 4,62) | 20 Hz / 20 kHz a +15 |
|---|---|---|---|---|---|---|---|
| 0,1 | 3,00 | −47,7 dB | 0,000 | 8,98 | 12,01 | 14,97 | +0,01 / +0,01 |
| 0,15 | 2,00 | −47,3 | 0,000 | 8,98 | 12,01 | 14,96 | +0,03 / +0,03 |
| 0,3 | 1,00 | −46,9 | 0,000 | 8,98 | 12,01 | 14,96 | +0,11 / +0,15 |
| 0,6 | 0,50 | −46,7 | 0,000 | 8,98 | 12,01 | 14,96 | +0,41 / +0,58 |
| 1 | 0,30 | −46,6 | 0,000 | 8,98 | 12,01 | 14,96 | +1,05 / +1,47 |

- Q segue 0,3/alpha entro lo 0,1 %.
- Boost identico su tutto WIDTH (±0,005 dB): il secondo deck non serve.
- Notch −46,6…−47,7 dB, come la v0.2.1 (spec kill −30).
- A Q0,3 e +15 dB la campana a 700 Hz alza anche gli estremi di banda di 1-1,5 dB: è la larghezza voluta, non un errore.

## Rumore — `cell-v021-width-noise.cir` (riferimento), `cell-v022-width-noise.cir` (A), `cell-v022b-width-noise.cir` (B)

Uscita della cella, A-wtd, `noise_total.py` (16 punti). Iniezione con E lineare.

| caso | v0.2.1 switch | v0.2.2 A (pot 10k, OP1654) | v0.2.2 B (pot 1k, OPA1612) |
|---|---|---|---|
| detent, ogni Q | −91,0…−102,4 | −102,4 | −102,4 |
| +15 dB, Q3 | −96,6 | −83,8 | −91,8 |
| +15 dB, Q1 | −89,0 | −82,3 | −88,9 |
| +15 dB, Q0,5 | −82,9 | −81,6 | −86,1 |
| +15 dB, Q0,3 | — | −82,2 | −83,9 |

- Perché A peggiora: il partitore attenua il segnale prima del buffer, poi il buffer amplifica segnale e rumore insieme. Il rapporto segnale/rumore in dq vale 0,3·v/en, contro Q·v/en della v0.2.1: −20 dB a Q3.
- B (pot a bassa impedenza, op-amp da 1,1 nV): pari a Q1, meglio a Q0,5, −4,8 dB a Q3. Scelta: **B**.
- A detent il rumore non cambia con WIDTH e non peggiora: il target di modulo (misurato a gain nominale) resta valido.
- Il −91,0 della v0.2.1 a detent e Q0,5 è un artefatto: con l'iniezione ideale la Rbw piccola (270 Ω) alza il noise gain del summer d'uscita. Nel circuito vero c'è l'impedenza del wiper.
