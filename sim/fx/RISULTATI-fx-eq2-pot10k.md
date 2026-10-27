# EQ2 del FX-SEND con un pot doppio per il LOW (2026-10-27, todo 165)

Netlist: `sim/fx/fx-eq2-pot10k.cir` (copia di `fx-eq2.cir` con la sola cella LOW cambiata).

**Perché.** La cella LOW di `fx-eq2.cir` ha due reostati complementari (Rza fra NA e NB,
Rzb fra NC e l'uscita) che non hanno un nodo in comune: servono due sezioni di pot per lato,
quattro in stereo. Un pot a 4 sezioni da 9 mm non esiste.

**Cosa cambia.** Nel ramo di retroazione Rf e Zb stanno in serie senza altri collegamenti in
mezzo: scambiarli non cambia la funzione di trasferimento. Con Zb prima di Rf, Za e Zb hanno in
comune il nodo NB (la massa virtuale): diventano le due metà di UN pot, col cursore su NB. È la
disposizione Baxandall. Pot 10k (come dice `fx-send-module.md`, al posto dei 31k fuori
catalogo): le resistenze scalano da 1k a 324 Ω, i condensatori da 56n a 180n C0G (valore di
serie: incrocio circa 3 % più basso).

**Esito** (dB, originale / nuova cella):

| Misura | detent | kill LOW | boost LOW | kill HIGH | boost HIGH | due kill |
|---|---|---|---|---|---|---|
| 20 Hz | 0,00 / 0,00 | −29,63 / −29,58 | 5,93 / 5,93 | 0,00 / 0,00 | 0,00 / 0,00 | −29,63 / −29,58 |
| 120 Hz | 0,00 / 0,00 | −25,51 / −25,27 | 4,20 / 4,11 | 0,01 / 0,01 | −0,01 / −0,01 | −25,50 / −25,26 |
| 1 kHz | 0,00 / 0,00 | −9,52 / −9,21 | −0,12 / −0,14 | 0,32 / 0,32 | −0,32 / −0,32 | −9,21 / −8,90 |
| 4,5 kHz | 0,00 / 0,00 | −1,27 / −1,17 | −0,12 / −0,11 | 0,47 / 0,47 | 0,55 / 0,55 | −0,80 / −0,70 |
| 20 kHz | 0,00 / 0,00 | 0,16 / 0,16 | −0,01 / −0,01 | −5,11 / −5,11 | 5,07 / 5,07 | −4,95 / −4,95 |
| minimo | −0,01 / −0,01 | −29,78 / −29,74 | | −13,99 / −13,99 | | −29,78 / −29,74 |
| massimo | | | 5,99 / 5,98 | | 5,90 / 5,90 | |

Differenze ≤ 0,31 dB, tutte dalla C di serie. Il gesto resta lo stesso: kill a −30 dB, boost +6,
detent piatto. La curva del pot resta [PROVVISORIO] (dec. 129). Rumore: impedenze 3 volte più
basse, quindi non peggiora (non rimisurato).
