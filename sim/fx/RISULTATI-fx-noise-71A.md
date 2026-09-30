# RISULTATI — Budget rumore bus FX (voce 71A)

Data: 2026-09-30. Netlist: `fx-bus-noise-71A.cir` (prima simulazione di
rumore del bus FX — mai fatto prima). Metodo §8.9 five-way: densità
`.noise` a 10 punti 20 Hz-20 kHz, integrazione trapezoidale python, MAI
`.meas INTEG` (quirk LTspice 26.0.2). Macro op-amp reali
`opamp-audio.inc` (OPA1612 1,1 nV/√Hz).

## Punto di misura e condizione

**JACK SEND di un bus** (sezione L; R identica), pad 0 dB, carico 10k
[ASSUNZIONE: ingresso pedale/rack tipico], condizione sheet §3
"contributori terminati": i 6 send di canale (4 DJ + mic + generic,
fx-module §2) terminati a GND via i loro 10k — nessun rumore esterno.
Contributori INTERNI inclusi: rete di summing (9×10k + Rf 10k, §3),
3 VCA di reroute della matrice (§7), op-amp di bus OPA1612, pad driver +
driver pedale, R 47 + R 100 di protezione.

## Assunzioni [PROVVISORIO — regola 3]

1. **VCA reroute al floor datasheet −98 dBV SEMPRE** (Rvn 476k = 89
   nV/√Hz, iniezione E lineare 4 nodi) indipendentemente dalla posizione
   del pot: conservativo — il datasheet THAT non dà il rumore vs gain; a
   reroute chiuso (uso normale a pedale spento) il contributo reale è
   inferiore. Connessione VCA→bus: Rout 20k + 10k di summing = peso 1/3
   (l'interfaccia matrice→bus non è ancora a doc: da fissare nel design
   di dettaglio).
2. EQ2 e DC servo NON nel percorso bus (vivono lato canale e lato
   ritorno: il loro rumore appartiene ai rispettivi budget — canale
   già misurato in `sim/cdj/RISULTATI-channel-noise-71A.md`; ritorno =
   sistema/master, mai simulato).
3. TVS esclusa (capacitiva, non rumorosa in banda). Bus stereo = 2
   sezioni indipendenti identiche; il "controlled mono sum" L+R (§2)
   somma potenze non correlate: **+3 dB al jack mono** (notato sotto).

## Risultato

| Grandezza | Valore |
|---|---|
| Densità al jack (piatta 20 Hz-20 kHz) | **62 nV/√Hz** |
| Integrato 20-20k unweighted | 8,76 µV = **−98,9 dBu** |
| Integrato 20-20k **A-weighted** | 7,05 µV = **−100,8 dBu A-wtd** |
| Mono sum L+R (+3 dB) | −95,9 / −97,8 dBu |
| Target sheet §3 | ≤ −88 dBu |
| Esito | **PASS con 12,8 dB di margine** (anche il mono sum passa con 9,8) |

Ripartizione di potenza (breakdown analitico, confermato dal totale
misurato 62 vs 66 nV stimato): **3 VCA reroute ~60%** (51 nV equivalente,
ciascuno 89 nV × peso 1/3), **rete di summing ~37%** (41 nV = 10 R da
10k), op-amp ~3%. Con reroute chiusi (pot CCW, caso d'uso a pedale
spento) il bus reale sta sotto −102 dBu circa (solo summing+op-amp).

## Lettura per la ritaratura 71A

- Il target −88 del sheet era largamente conservativo: il bus FX non è
  un collo di bottiglia del sistema (12,8 dB di margine con l'ipotesi
  più severa sui VCA).
- Se la ritaratura vorrà stringere il target, −95 A-wtd resta raggiunto
  senza alcuna fix; sotto, le leve sono: peso dei VCA sul bus (Rin più
  alte riducono il contributo ma anche il livello di reroute — trade-off
  da design) o R di summing più basse (10k→4,7k: −3 dB sul 37%).
- Il rumore che conta per il master è quello del CANALE DI RITORNO
  (buffer JFET hi-Z + GAIN VCA + EQ2 + servo + fader): mai simulato,
  entra nel budget di sistema (suggerito come coda 71A: `fx-return`
  analogo al canale DJ).

## Nota sui file

`dbg-bus-noise.*` in questa cartella = residui di debug di una run
interrotta (git-ignorati, candidati al cleanup voce 14 handoff — non
cancellati senza conferma, regola repo).
