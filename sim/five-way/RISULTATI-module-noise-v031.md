# RISULTATI — Module-noise v0.31 consolidato (coda voce 71A)

Data: 2026-10-01. Netlist: `module-noise-v031.cir` (rilasciato) +
varianti di ripartizione `module-noise-v031a.cir` (solo Rvn) e
`module-noise-v031b.cir` (Rvn + invertitori), tutte `.step th LIST 0 0.5`.
Base `module-noise-v03.cir` (intatto) con tre correzioni già decise:
(1) Rvn 240k→133k (47 nV/√Hz = −104 dBV esatto per I/V 10k); (2) gate
π SPDT reali (Ron 4,7 Ω + Coff 30p, five-way §8.10); (3) 2 invertitori
unity SUB/MID (R 2k, macro OPA1654-class, §8.10).
Metodo §8.9: densità 10 punti 20 Hz-20 kHz, trapezoidale python, A-wtd
IEC 61672 post, MAI INTEG. `.nodeset` ereditato: convergenza OK su
entrambi i θ in tutte e tre le run.

## Totali (punto di misura: out modulo, ingressi terminati, gain nominali)

| Run | θ | unweighted | A-wtd |
|---|---|---|---|
| **v031 (finale)** | **θ0** | **−82,3 dBu** | **−83,9 dBu** |
| v031 | θ50 | −77,9 | −79,4 |
| v03 (riferimento storico) | θ0 | −81,0 | −83,2 |
| v03 | θ50 | −77,4 | −79,6 |

**Target ≤ −80 dBu A-wtd (dec. 88/89) a θ0: PASS con margine 3,9 dB**
(v03 diceva 3,2). A θ50 il rumore sale di +4,5 dB a fronte di +7 dB di
segnale (law del drive): SNR migliora, come documentato in dec. 88.

## Ripartizione del delta vs v03 (A-wtd)

| Correzione | θ0 | θ50 |
|---|---|---|
| (1) Rvn 240k→133k | **−0,77 dB** | +0,16 (entro il rumore dei numeri, vedi nota) |
| (3) Invertitori SUB/MID | +0,02 | +0,03 |
| (2) Switch π (4,7+Coff vs 33 Ω) | +0,01 | +0,01 |
| Totale | −0,7 | +0,2 |

Invertitori e switch π: impatto di rumore trascurabile (+0,03 dB in due) —
la stima "+~0,3 dB" della vigilia era cautelativa e smentita in meglio
(sorgenti a bassa Z, R 2k piccole).

## CORREZIONE IMPORTANTE all'estrapolazione del 30/09

Il "Finding di metodo" (`sim/cdj/RISULTATI-channel-noise-71A.md`) e i doc
del 30/09 stimavano il 5-way reale ≈ **−85,5 dBu A-wtd (margine ~5,5 dB)**
applicando al v03 la quota drive dell'87% misurata in v021 (6 VCA). È
SBAGLIATO: nell'architettura switch del v03 il drive pesa solo ~32% della
potenza a θ0 (277 nV su ~489 nV totali), quindi l'errore Rvn sposta il
totale di −0,8 dB, non −2,3. **Numero corretto: −83,9 A-wtd θ0, margine
3,9 dB.** Da propagare nei doc (channel RISULTATI finding, docs/06 §1/§4,
CLAUDE.md) — a cura del parent (questo fork non tocca doc condivisi).

## Dominanza (verifica richiesta)

Il drive VCA **non è più il dominante a θ0**: con Rvn 133k contribuisce
~206 nV/√Hz su 442 totali = **~22% di potenza**; banca + celle v0.2.1
passano a ~78% (in v03 col Rvn gonfiato sembrava 32/68). A θ50 il drive
risale a ~35% (guadagno +7 dB) = primo contributore singolo ma non
maggioranza. L'asserzione v03 "dominante residua: VCA del drive" va letta
come "primo contributore singolo a θ50", non come maggioranza a θ0.

## Note

- θ50 A-wtd +0,2 dB col Rvn corretto: la densità a θ50 cala verso HF
  (805→627 nV tra 2k e 20k, band-limiting del drive a guadagno alto); la
  pesatura A sposta il peso su HF dove il Rvn pesa meno — il +0,2 è
  entro l'accuratezza del metodo (±0,2), non un peggioramento reale.
- Errore di trapezoidale su spettro quasi-piatto con griglia a decadi:
  < 0,1 dB (stima v021 §1 confermata dal confronto unwt/A-wtd).
- Regola di metodo confermata: Rvn si deriva dal dBV datasheet della
  CONFIGURAZIONE in uso (R = en²/4kT: 133k ↔ −104 dBV con I/V 10k;
  476k ↔ −98 dBV con Rout 20k), mai copiato tra configurazioni.
