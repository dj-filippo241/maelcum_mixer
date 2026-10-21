# RISULTATI — alimentatore esterno e PSU-IN (dec. 113, todo 51)

Data: 2026-10-14. Design: `docs/fase3/sistema-psu-esterno.md`.

| netlist | cosa misura |
|---|---|
| `psu-box-ldo-step.cir` | LDO discreto ±22,0 V da raw fisso 25 V: stabilità e gradino di carico 1,0 → 1,7 A |
| `psu-box-w1.cir` | W1 reale (2×21 V 3,5 A, reg. 7 %) → ponte → 10 mF → LDO ±22,0 V → cavo 2 m → 2,2 mF PSU-IN; rete −10 / 0 / +10 % |
| `psu-box-w2.cir` | W2 reale (2×18 V 1,0 A, reg. 10 %) → ponte → 10 mF → LDO ±19 V → cavo → 1 mF PSU-IN |
| `psu-box-off.cir` | spegnimento: rete staccata sul picco a t = 1,2 s; tempo prima che i regolatori locali escano di regolazione; rivelatore AC_OK |
| `psu-box-off15.cir` | come sopra, bulk W1 10 mF contro 15 mF |

Avvertenza di metodo: queste netlist girano **senza `uic`**. Con condizioni
iniziali forzate l'anello dell'LDO parte da uno stato impossibile, il passo
crolla e LTspice non termina (provato: oltre 6 minuti a vuoto, anche su
0,5 ms). Con l'accensione da zero il `.op` è banale e il caso dura 3-13 s.
L'amplificatore d'errore è una macro inline (transconduttanza lineare, A0
1e5, GBW ~1 MHz, clamp a diodi con N = 1): con `limit()` brusco o diodi a
N = 0,05 la simulazione si blocca.

## 1. Gradino di carico (`psu-box-ldo-step.cir`)

| | valore |
|---|---|
| uscita a 1,0 A (al mixer) | 22,68 V (prima della correzione a 22,0; vedi §2) |
| gradino 1,0 → 1,7 A | calo 87 mV, nessuna oscillazione |
| uscita a 1,7 A | 22,66 V (cavo: −25 mV per 0,7 A) |
| ripple a regime | 0,02 mV picco-picco |
| carica d'accensione | a corrente limitata (~2,7 A, PNP su 0,22 Ω): 2,7 mF in ~60 ms |

## 2. Pre-regolatore W1, prima a 22,5 V (`psu-box-w1.cir`, R11 = 39,9 k)

| Caso | Rete | Carico | Raw min | V_DS min | Al mixer min / max |
|---|---|---|---|---|---|
| 1 | −10 % | 1,7 A | 23,54 V | 0,49 V | 22,62 / 22,70 V (**esce di regolazione nella valle**) |
| 2 | nom. | 1,7 A | 26,57 V | 3,45 V | 22,68 V |

A 22,5 V la caduta totale (0,22 Ω × 1,7 A + MOSFET) non entra nella valle
del ripple a rete −10 %. **Correzione: uscita a 22,0 V** (R11 = 38,3 k).

## 3. Pre-regolatori a 22,0 V e 19 V (valori adottati)

W1 ±22,0 V (`psu-box-w1.cir`), bulk 10 mF:

| Caso | Rete | Carico | Raw min | V_DS min | Al mixer | Ripple al mixer | P MOSFET | I avv. eff. |
|---|---|---|---|---|---|---|---|---|
| 1 | −10 % | 1,7 A | 23,54 V | 1,26 V | 21,83 V | 3 mV | 3,2 W | 3,27 A (93 %) |
| 2 | nom. | 1,7 A | 26,57 V | 4,27 V | 21,87 V | 2 mV | 8,3 W | 3,33 A |
| 3 | +10 % | 1,0 A | 31,02 V | 8,82 V | 21,94 V | 1 mV | 9,2 W | 2,18 A |
| 4 | +10 % | 1,7 A | 29,62 V | 7,28 V | 21,90 V | 1 mV | **13,4 W** | 3,39 A (97 %) |

W2 ±19 V (`psu-box-w2.cir`), Rsense 0,56 Ω, bulk 10 mF:

| Caso | Rete | Carico | Raw min | V_DS min | Al mixer | Ripple | P MOSFET | I avv. eff. |
|---|---|---|---|---|---|---|---|---|
| 1 | −10 % | 0,48 A | 20,47 V | 1,32 V | 18,84 V | 1 mV | 0,7 W | 0,89 A |
| 2 | nom. | 0,48 A | 23,13 V | 3,95 V | 18,87 V | 1 mV | 2,0 W | 0,90 A |
| 3 | +10 % | 0,28 A | 27,08 V | 7,98 V | 18,92 V | < 1 mV | 2,3 W | 0,59 A |
| 4 | +10 % | 0,48 A | 25,79 V | 6,59 V | 18,90 V | < 1 mV | **3,2 W** | 0,92 A |

Il ramo negativo è lo specchio esatto (stessi numeri col segno opposto).

## 4. Spegnimento (`psu-box-off.cir`, `psu-box-off15.cir`)

Rete staccata sul picco, carico costante. «Locali fuori» = la tensione al
mixer scende sotto 20,9 V (LM317 → 19,2 V esce di regolazione).

| Bulk W1 | Rete | Carico | LDO del box sotto 21,5 V | Locali fuori |
|---|---|---|---|---|
| 10 mF | −10 % | 1,7 A | 13,6 ms | **18,3 ms** |
| 10 mF | nom. | 1,7 A | 31,6 ms | 36,2 ms |
| 10 mF | nom. | 1,0 A | 66,7 ms | 74,1 ms |
| **15 mF** | −10 % | 1,7 A | 19,6 ms | **25,9 ms** |
| 15 mF | +10 % | 1,7 A | 73,5 ms | 79,7 ms |

Con 15 mF l'avvolgimento non cambia (3,27 A efficaci a rete −10 %) e il raw
minimo sale da 23,53 a 23,75 V.

Rivelatore AC_OK (doppia semionda dal W1, partitore 47 k / 4,7 k, 10 µF:
τ = 42,7 ms). Picco simulato: 1,66 V a rete −10 %, 1,85 V nominale,
2,04 V a +10 %; minimo a regime 0,95 × picco. Con soglia **fissa al 75 %
del picco nominale (1,39 V)**, il tempo d'allarme dopo il distacco vale
τ·ln(picco/soglia):

| Rete | Allarme AC_OK | + relè (≤ 5 ms) | Locali fuori (15 mF, 1,7 A) | Margine |
|---|---|---|---|---|
| −10 % | 7,7 ms | ≤ 12,7 ms | 25,9 ms | ≥ 13 ms |
| nom. | 12,3 ms | ≤ 17,3 ms | > 36 ms | ≥ 19 ms |
| +10 % | 16,4 ms | ≤ 21,4 ms | 79,7 ms | ≥ 58 ms |

A regime, a rete −10 %, il minimo del rivelatore (1,58 V) resta il 12 %
sopra la soglia. AC_OK scatta se la rete scende sotto ~−21 %.

Nota: «locali fuori» non vuol dire pop. Il moltiplicatore di capacità dopo
ogni LM317 filtra ancora il ripple, e i rail ±18 scendono di 1 V solo ~6 ms
dopo. È il criterio prudente: il mute arriva prima che l'audio veda
qualunque cosa.

## 5. REV 2026-10-21 — dec. 115: W1 4,0 A, carico 1,81 A

Il modulo FX ha 40 VCA, non 20 (todo 114): il ramo audio sale a 1,81 A
per ramo con tutti i moduli opzionali. Netlist: `psu-box-w1-115.cir`
(come `psu-box-w1.cir`, W1 2×21 V 4,0 A, bulk 15 mF) e
`psu-box-off-115.cir` (come `psu-box-off15.cir`, W1 4,0 A, 1,81 A).

| Caso | Rete | Carico | Raw min | V_DS min | Al mixer | Ripple | P MOSFET | I avv. eff. |
|---|---|---|---|---|---|---|---|---|
| 1 | −10 % | 1,81 A | 23,86 V | 1,56 V | 21,83 V | 2,4 mV | 3,6 W | 3,52 A (88 %) |
| 2 | nom. | 1,81 A | 26,91 V | 4,57 V | 21,87 V | 1,3 mV | 9,1 W | 3,58 A (90 %) |
| 3 | +10 % | 1,0 A | 31,36 V | 9,16 V | 21,94 V | 0,6 mV | 9,4 W | 2,22 A |
| 4 | +10 % | 1,81 A | 29,96 V | 7,60 V | 21,90 V | 0,8 mV | **14,5 W** | 3,64 A (91 %) |

Il MOSFET ha più margine di prima (1,56 V contro 1,26 V): il W1 più
robusto e il bulk da 15 mF alzano la valle più di quanto la corrente in
più la abbassi. Il calore peggiore per MOSFET sale da 13,4 a 14,5 W.

Spegnimento (rete staccata sul picco, 15 mF, 1,81 A):

| Rete | LDO del box sotto 21,5 V | Locali fuori | Allarme AC_OK + relè (§4) | Margine |
|---|---|---|---|---|
| −10 % | 19,3 ms | **25,3 ms** | ≤ 12,7 ms | ≥ 12,6 ms |
| nom. | 44,6 ms | 50,6 ms | ≤ 17,3 ms | ≥ 33 ms |
| +10 % | 70,0 ms | 75,9 ms | ≤ 21,4 ms | ≥ 54 ms |

Il mute arriva sempre prima che i regolatori locali escano di regolazione.

