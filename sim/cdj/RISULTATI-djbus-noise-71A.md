# RISULTATI — DJ bus: budget rumore (coda 71A, 2026-10-01)

Netlist: `djbus-noise-71A.cir`. Metodo §8.9: densità .noise 10 punti
20 Hz-20 kHz + trapezoidale python + A-wtd IEC 61672. Mai INTEG.
Macro OP1612 reale (Rn 73 = 1,1 nV/√Hz).

## Punto di misura e condizioni

Uscita DJ bus (vout del summer invertente), 4 canali TERMINATI: out
driver 47 Ω verso GND a segnale nullo (struttura = djbus-level.cir,
topologia [PROVVISORIO] di quel netlist: 47 Ω + 10k per canale →
virtual earth, Rf 10k, unity per ingresso).

## Risultato

Densità piatta **28,7 nV/√Hz** su 20 Hz-20 kHz (variazione <0,01 dB):

| Grandezza | Valore |
|---|---|
| Integrato 20-20k unweighted | 4,06 µV = **−105,6 dBu** |
| Integrato 20-20k A-weighted | **−107,5 dBu A-wtd** |

Ripartizione analitica (conferma la misura): 4 rami 10k+47 (25,7 nV,
79% potenza) · Rf 10k (12,9 nV, 20%) · op-amp NG 3,5 (3,9 nV, 1%).

## Verdetto sull'assunzione docs/06 §2

**TRASCRURABILE: confermato.** Al nodo DJ bus il contributo dominante è
la somma dei 4 canali (−90,3 A-wtd ciascuno → −84,3): il bus sta
**23,2 dB sotto** → aggiunge +0,02 dB al totale di potenza. Anche nel
caso (non nominale) di canali silenziati, il bus resta sotto ogni
contributore attivo della catena.

## Assunzioni

- Terminazione canale = 47 Ω (out driver ≤50 Ω del doc §3.8): valori
  più alti la renderebbero ancora più trascurabile (più attenuazione
  verso il virtual earth).
- CUE/meter pickup dal bus: buffer dedicati, non caricano il rumore.
- Stereo: identico per lato (nessun accoppiamento L/R nella rete).
