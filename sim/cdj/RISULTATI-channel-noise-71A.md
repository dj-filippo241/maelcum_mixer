# RISULTATI — Budget rumore canale DJ completo (voce 71A)

Data: 2026-09-30. Netlist: `channel-noise-71A.cir`. Metodo §8.9 five-way:
densità `.noise` a 10 punti (20 Hz-20 kHz), integrazione trapezoidale
python, MAI `.meas INTEG` (quirk LTspice 26.0.2). Macro op-amp reali
`opamp-audio.inc` (OPA1654 4,5 nV / OPA1612 1,1 nV).

## Punto di misura e condizioni

**Out driver di canale** (sheet §3), carico = iniezione DJ bus 10k,
guadagni nominali (GAIN al detent 0 dB, EQ al detent, fader unity),
sorgente = terminazione (nessun segnale). Catena simulata: [A] prot+buffer
→ [B] GAIN VCA 218x (rumore datasheet −98 dBV a 0 dB, Rout 20k →
Rvn 476k = 89 nV/√Hz, iniezione E lineare 4 nodi) → [C] EQ β3 4 celle
(celle copy esatta di `cascade-b3-noise.cir`) → diramazioni send/meter
come carico 20k [ASSUNZIONE] → [H] fader pot 10k unity [PROVVISORIO —
valore reale voce 40] + buffer → [I] out driver 47 Ω.

## Risultato

| Grandezza | Valore |
|---|---|
| Densità out (piatta 20 Hz-20 kHz) | **210 nV/√Hz** |
| Integrato 20-20k unweighted | 29,6 µV = **−88,4 dBu** |
| Integrato 20-20k **A-weighted** | 23,8 µV = **−90,3 dBu A-wtd** |
| Target sheet §3 | ≤ −92 dBu A-wtd |
| Esito | **FAIL di 1,7 dB** (il target è superato dalla sola EQ, come da voce 71A) |

Ripartizione di potenza: **EQ β3 82%** (190 nV/√Hz, già misurata in
`cascade-b3-noise.cir`), **GAIN VCA 18%** (89 nV/√Hz = floor datasheet),
fader + buffer + out driver ≈ 0% (OPA1612 1,1 nV + R piccole).

## Fix ingegneristiche disponibili (nessun impatto musicale)

| Fix | Effetto | Costo/vincolo |
|---|---|---|
| (a) Scala R dell'EQ ×0,5 (summer 49,9k→24,9k, bracci ≤15,5k, C ×2) | EQ 190→~134 nV; canale → ~−90,6 unwt / −92,8 A-wtd PASS | pot custom 10k→5k (voce 40 da riaprire), OPA1654 carica ok |
| (b) I/V 10k all'uscita GAIN VCA (regola datasheet, come drive) | VCA 89→47 nV; canale → −88,8/−90,7: +0,4 dB solo (EQ domina) | 1 R + regola già usata nel 5-way |
| (a)+(b) | ~−91,6 unwt / −93,8 A-wtd: PASS con 1,8 dB | somma dei costi |
| (c) Ritaratura target (voce 71A, ratifica Filippo) | target −90 A-wtd: margine 0 dB; −88: margine 2,4 dB | decisione di specifica, non di circuito |

Nota: −90,3 dBu A-wtd ≈ −88 unweighted = già dentro la fascia migliore
della scena (benchmark docs/05: unico numero pubblicato Ligwa −80 dB
unweighted; nessun costruttore pubblica l'out driver di canale).

## Finding di metodo — Rvn in `module-noise-v03.cir`

v03 modella il rumore del VCA drive con Rvn **240k** (= 63 nV/√Hz =
−101 dBV integrato) ma il commento dice "47 nV/√Hz" (= 133k = −104 dBV,
la configurazione I/V 10k del drive). 240k sovrastima il rumore del drive
di ~2,6 dB; essendo il drive dominante (87% di potenza), il totale modulo
−83,2 dBu A-wtd è **pessimista di ~2,3 dB** (reale stimato ≈ −85,5):
direzione conservativa, nessun redesign; da correggere/riconfermare nella
campagna 71A (margine 5-way sul target −80 sale da 3,2 a ~5,5 dB).
Qui per il GAIN si è usato il valore esatto 476k = −98 dBV (senza I/V).

## Stato

Budget canale FATTO. Per la ritaratura sheet §3 (71A) mancano: FX bus
(run parallela) e il sistema master (somma canali+5-way+ritorni: calcolo
di sintesi a valle dei budget). Rerun filtro: FATTO (fork parallelo,
`sim/filtro/RISULTATI-filtro-noise-71A.md`).
