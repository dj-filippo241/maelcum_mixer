# Limiter fisso del MIC (dec. 145, 2026-10-31)

Netlist: `sim/mic/mic-limiter.cir` (forme nel tempo), `sim/mic/mic-limiter-thd.cir`
(distorsione a regime). Design: `docs/fase4/mic-mono-moduli.md`, REV 2026-10-31.

## Circuito simulato

Il limiter usa il VCA del MUTE (dec. 111): nessun chip di guadagno in più.

```
nodo POST-EQ -> VCA (V2181, 0 dB) -> uscita del modulo (split MSUM + 4 SEND)
uscita -> raddrizzatore a doppia semionda (x0,5) -> picco: attacco Ratt*Ch 1 ms,
          rilascio Rrel*Ch 1 s -> lisciatura Rs*Cs 0,1 ms
       -> errore K*(Vpk - Vth), solo sopra soglia, K = 0,25 -> EC- (pin 3)
MUTE: rampa 1 ms a +0,61 V, sommata sullo stesso pin
```

Anello in retroazione: il rilevatore legge l'uscita del VCA. Raddrizzatore, picco e
somma sono blocchi ideali; la versione con op-amp sta nello schema del modulo.

| Parametro | Valore [PROVVISORIO, da sentire in MC-MIC] |
|---|---|
| Soglia | +12,0 dBu sinusoidale all'uscita del modulo (Vth 2,18 V dopo il x0,5) |
| Guadagno d'anello | K = 0,25 V al pin per V di eccesso |
| Attacco | Ratt 1k, Ch 1 µF (1 ms) |
| Rilascio | Rrel 1 MΩ, Ch 1 µF (1 s) |
| Lisciatura | Rs 100 Ω, Cs 1 µF (0,1 ms) |
| Tetto della riduzione | nessuno: con 0,15 V (~25 dB) i numeri erano identici |

## Risultati (grido: da 0 dBu a +20 dBu per 0,3 s, 1 kHz)

| Misura | Valore |
|---|---|
| Sotto soglia (0 dBu) | guadagno 0 dB, il limiter non tocca niente |
| Grido a +20 dBu, a regime | uscita +12,8 dBu; riduzione 7,2 dB; ~10:1 |
| Primo ~1 ms del grido | passa pieno (+20 dBu, un ciclo a 1 kHz) |
| Da 2 a 5 ms | +13,5 dBu al massimo |
| 50 ms dopo il grido | −4,4 dB (la frase dopo parte un filo più bassa) |
| 300 ms dopo il grido | 0 dB |
| MUTE | −100 dB |

Distorsione a regime, +20 dBu in ingresso (7 dB di riduzione), THD Partial:

| 100 Hz | 150 Hz | 1 kHz | 5 kHz |
|---|---|---|---|
| 0,78 % | 0,52 % | 0,054 % | 0,004 % |

È H3: l'ondulazione del rilevatore modula il guadagno al doppio della frequenza. Vale
solo mentre il limiter lavora; sotto soglia la catena resta quella del modulo.

## Le varianti scartate (scelta di Filippo, 2026-10-31: variante 2)

| Variante | Primi ms | THD 100 / 150 Hz | Dopo il grido |
|---|---|---|---|
| 1. Rilascio 330 ms | tenuto da 2 ms | 2,2 / 1,5 % | normale subito |
| **2. Rilascio 1 s** | **tenuto da 2 ms** | **0,78 / 0,52 %** | **−4,4 dB a 50 ms, normale a 300 ms** |
| 3. Rilascio 1 s, lisciatura 2,2 µF | passa pieno per ~3 ms | 0,48 / 0,32 % | −5,4 dB a 50 ms |

Vicolo cieco: una lisciatura di 3,3 ms (Rs 3,3k) dentro l'anello ritarda il controllo.
Il rilevatore si carica sul grido intero e il VCA scende a −28 dB: un «buco» di volume
di ~100 ms all'inizio del grido. Con 0,1 ms il buco sparisce.

## Non simulati

Raddrizzatore e picco con op-amp e diodi veri, offset del rilevatore (1 mV al pin =
0,16 dB), rumore del VCA a 0 dB (stima −98 dBu A-wtd, REV dec. 111), soglia contro
tolleranze. Banco.
