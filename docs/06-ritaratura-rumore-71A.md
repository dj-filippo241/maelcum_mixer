# 06 — Ritaratura rumore sheet §3 (voce 71A) — RATIFICATA (decisione 89)

Data: 2026-09-30. Stato: **RATIFICATA → decisione 89** (target canale −80 senza fix,
filtro −80 con input q70, FX send −88 confermato, sistema −78; esito in §6). Origine: decisione 88 ha ratificato
il target 5-way (≤ −80 dBu A-wtd) e ha lasciato aperti i target di canale,
FX e sistema, invalidati dal quirk INTEG di LTspice (§8.9 five-way).

## 1. Numeri nuovi (campagna 2026-09-30, metodo corretto: densità 10+ punti, trapezoidale, mai INTEG)

| Blocco | Punto di misura | Unweighted | A-wtd | Target sheet attuale | Esito |
|---|---|---|---|---|---|
| Canale CDJ completo | out driver, carico 10k, gain nominali, ingressi terminati | −88,4 dBu | **−90,3 dBu** | ≤ −92 A-wtd | FAIL 1,7 dB (`sim/cdj/RISULTATI-channel-noise-71A.md`) |
| EQ β3 (sola) | uscita EQ | −89,2 dBu | — | — | 82% della potenza di canale |
| GAIN VCA 218x (solo) | — | −98 dBV datasheet | — | — | 18% della potenza di canale |
| 5-way modulo | out modulo (dec. 88) | −81,0 v03 / −82,3 v031 | **−83,2** v03 / **−83,9** v031 (rerun consolidato 2026-10-01) | ≤ −80 A-wtd RATIFICATO | PASS 3,9 dB misurato (v031) |
| Filtro core OTA nudo (a) | buffer LP, fc max 37 kHz | **−90,3** | −91,4 | ≤ −90 (send 0 dBu) | sim ideale AL LIMITE; die reale −84…−76 = FAIL 6-14 dB (`sim/filtro/RISULTATI-filtro-noise-71A.md`) |
| Filtro a fc basse (10 Hz-1 kHz) | idem | −126…−103,7 | −139…−117 | — | PASS largo (spettro 1/f) |
| FX bus (send, jack L) | contributori terminati, pad 0 dB, carico 10k | −98,9 dBu | **−100,8 dBu** | ≤ −88 | PASS 12,8 dB (`sim/fx/RISULTATI-fx-noise-71A.md`); dominante: 3 VCA reroute ~60% (ipotesi conservativa floor −98 dBV sempre) |
| Master out (stadio) | XLR | −119,2 (VALIDO, integrazione già manuale) | — | ≤ −92 | PASS (27 dB su −92; il '19 dB' storico era contro il vecchio target interno −100); non è lui il limite |

## 2. Sintesi di sistema (calcolo di potenza, condizioni dichiarate)

Condizioni: 4 canali CDJ terminati e attivi, DJ bus, 5-way in catena,
4 ritorni FX terminati, drive θ0, fader unity, out XLR. Contributi:
4× canale (−90,3 → −84,3 di somma) ⊕ 5-way (−83,2) ⊕ 4× FX bus
([−88 → −82] in attesa) ⊕ master (−119,2 trascurabile):

**Sistema stimato ≈ −78…−79 dBu A-wtd** [VERIFICATO 2026-10-01 coi budget reali: **−80,5 dBu A-wtd = PASS 2,5 dB**, §7]. Nota: il contributo FX al sistema
passa dal canale di RITORNO (buffer JFET hi-Z + GAIN VCA + EQ2 + servo +
fader → MASTER SUM), mai simulato — il bus send misurato (−100,8) è il
punto più pulito della catena. Stima provvisoria del ritorno: classe
−88…−92 (VCA+EQ2 dominanti) → budget reale del ritorno = coda 71A.

Assunzioni dichiarate: rumore dei summer (DJ bus, master sum) trascurabile
(resistenze basse, mai simulato — coda 71A/banco); nessun contributo da
mic/generic (moduli non ancora disegnati); pesatura A su spettro bianco
(−2,2 dB vs unweighted).

Contesto scena (docs/05): unico numero pubblicato = Ligwa −80 dB
unweighted su un EQ; SN relativa ~84 dB. Un sistema completo a −78 dBu
A-wtd (≈ −76 unweighted, SN ~76-78 dB su nominale 0 dBu) sta nella
fascia alta documentata della categoria, con VCA e drive in percorso.

## 3. Proposta di ritaratura sheet §3 [SUPERATA dall'esito ratificato → §5: dec. 89 = canale −80 SENZA fix, filtro −80]

| Riga sheet | Target attuale | PROPOSTA | Nota |
|---|---|---|---|
| Out driver di canale | ≤ −92 A-wtd | **≤ −90 A-wtd** + fix (a) e/o (b) sotto | misurato −90,3: −90 è onesto solo CON le fix; in alternativa deroga ≤ −88 senza fix |
| Bus FX (send) | ≤ −88 | **≤ −88 confermato** (PASS 12,8 dB misurato; opzione: stringere a −95 senza fix) | il ritorno FX va al master: budget dedicato in coda |
| Filtro (send 0 dBu) | ≤ −90 | **≤ −90 confermato MA con vincolo topologico**: la scelta musicale (a) OTA nudo NON lo rispetta a fc max col die reale (−84…−76) | se (a): riga filtro ≤ −76 a fc max (deroga esplicita) oppure (c-B) VCA nel loop che riporta il rumore in target (input nuovo per q70 — l'ascolto resta sovrano) |
| 5-way | ≤ −80 A-wtd (dec. 88) | invariato | margine misurato v031: **3,9 dB** (−83,9 A-wtd; la stima ~5,5 era sbagliata, §4) |
| XLR master / sistema | ≤ −92 / ≤ −90 | **sistema ≤ −78 dBu A-wtd** alle condizioni dichiarate §2 | −92 era irrealistico post-quirk: il master è dominato dal monte |

Fix ingegneristiche canale (nessun impatto musicale):
- (a) scala R dell'EQ ×0,5 (summer 24,9k, C ×2): EQ 190→~134 nV/√Hz;
  costo: pot custom 10k→5k → riapre voce 40 (percorso meccanico invariato);
- (b) I/V 10k all'uscita del GAIN VCA (regola datasheet, già usata nel
  drive): +0,4 dB da sola (l'EQ domina);
- (a)+(b): −93,8 A-wtd stimato → PASS con 3,8 dB di margine su −90.

## 4. Finding di metodo (da applicare trasversalmente)

`module-noise-v03.cir` usava Rvn 240k (−101 dBV) col commento "47 nV"
(= 133k = −104 dBV): il drive era sovrastimato ~2,6 dB → il −83,2 del
5-way è conservativo di ~2,3 dB (reale ≈ −85,5 [STIMA SBAGLIATA → rerun v031 2026-10-01: −83,9 A-wtd, margine 3,9 dB — il fix Rvn sposta il totale di −0,77 dB, non −2,3: la quota drive con gli switch è ~22-32%, non l'87% del v021 a 6 VCA]). Direzione sicura, nessun
redesign; il rerun consolidato (Rvn corretto + invertitori gate §8.10 +
eventuale I/V) va fatto nella coda 71A. Regola: il valore Rvn va derivato
dal dBV del datasheet (R = en²/4kT), non copiato tra configurazioni.

## 5. ESITO RATIFICA (2026-09-30 sera → decisione 89, docs/01)

- Canale CDJ: **≤ −80 dBu A-wtd**, NESSUNA fix (le opzioni (a)/(b) §3 sono
  respinte: pot 10k restano, voce 40 invariata). Misurato −90,3 = 10,3 dB.
- Filtro: **≤ −80 dBu A-wtd**; core nudo (a) al limite nel worst case die
  a fc max (−76…−84): dato d'input per l'ascolto q70, non un veto.
- FX bus send: **≤ −88 confermato** (misurato −100,8).
- Sistema XLR: **≤ −78 dBu A-wtd** alle condizioni §2. Stadio master ≤ −92.
- 5-way: invariato ≤ −80 (dec. 88).

## 6. Coda operativa dopo ratifica

1. [FATTO 2026-09-30] Sheet §3 aggiornata con i target ratificati (punto di
   misura e pesatura dichiarati, criterio dec. 88).
2. [RESPINTO da dec. 89] Fix canale (a)/(b): nessuna fix (target −80,
   misurato −90,3 = PASS 10,3 dB).
3. [FATTO 2026-10-01] Rerun consolidato `module-noise-v031.cir`: −82,3/−83,9 A-wtd θ0 (θ50 −77,9/−79,4), margine 3,9 dB; invertitori +0,02 dB, switch π +0,01 (stima +0,3 cautelativa).
4. Rumore del filtro: entra nell'ascolto q70 come dato (non decide da solo).
5. [FATTO 2026-10-01] Budget ritorno FX: −94,5/−96,4 A-wtd per ritorno (GAIN VCA 75%); 4 ritorni al master sum = −90,4 (`sim/fx/RISULTATI-fx-return-noise-71A.md`).
6. [FATTO 2026-10-01] Summer: DJ bus −105,6/−107,5 A-wtd; master summing −100,0/−101,9; summing+level VCA −94,4/−96,3 → trascurabili (+0,02/+0,06 dB al sistema): assunzione §2 CONFERMATA.
7. Cleanup residui run interrotta: sim/fx/dbg-bus-noise.* (regola globale: chiedere a Filippo prima di
   cancellare).

## 7. CHIUSURA CODA 71A (2026-10-01) — sistema verificato

Budget mancanti completati: ritorno FX (−96,4 A-wtd ×4 = −90,4), summer
DJ bus (−107,5) e master summing+level VCA (−96,3) = trascurabili, rerun
5-way v031 (−83,9 A-wtd θ0, margine 3,9 dB — la stima "reale −85,5" è
corretta: il fix Rvn sposta −0,77 dB, quota drive ~22-32% con gli switch).

**Sistema ricalcolato (potenze, condizioni §2)**: 4 canali −84,3 ⊕ 5-way
−83,9 ⊕ 4 ritorni −90,4 ⊕ summer (−107,5/−96,3) ⊕ stadio master −119,2 =
**−80,5 dBu A-wtd → PASS 2,5 dB sul target ≤ −78 (dec. 89 confermata)**.
Dominanti: 5-way 45%, 4 canali 42%, ritorni FX 10%. Voce 71A: coda CHIUSA.

**ADDENDUM 2026-10-02 (send chain a canali vivi)**: il −80,5 vale con gli
assign FX NON attivi (ritorni simulati col bus terminato). Misurato il
send chain vivo (`sim/fx/send-chain-noise.cir`,
`sim/fx/RISULTATI-send-chain-71A.md`): −98,5 dBu A-wtd per canale al jack
(la stima −95 di fx-send-module §6 era conservativa), ma il floor
indipendente dal level porta il SISTEMA a ~−73 dBu A-wtd con send
assegnati (−66,6 con 4 send a level 0 dB) contro target −78: FINDING
CHIUSO da DECISIONE 95 (2026-10-02): DEROGA D'USO ratificata da Filippo
(target −78 vale a send non assegnati; con FX in uso floor −73…−66,6
accettato come carattere del caso d'uso, disciplina level send K4).

## 8. RICALCOLO 2026-10-13 — quirk 3 (en degli op-amp assente dal `.noise`) → voce 73 CHIUSA

Causa: nelle macro OP1654/OP1612 lo stadio d'ingresso era una sorgente
comportamentale e LTspice 26.0.2 non propagava il rumore di tensione del
chip (dettaglio: `sim/mic/RISULTATI-mic-mono.md` §4). Corretti la
libreria `sim/lib/opamp-audio.inc` e le macro copiate in 17 netlist
(five-way/module-noise-v03*, param-cell-real-noise, fx/fx-return-noise-71A,
fx-dc-servo, filtro/svf-*). Metodo: ogni netlist di rumore rilanciato
con libreria vecchia e nuova; totali 20 Hz–20 kHz, trapezoidale, pesatura
A. Lo script riproduce i numeri ufficiali vecchi entro 0,05 dB.

| Blocco | A-wtd prima | A-wtd ora | Δ | Target | Esito |
|---|---|---|---|---|---|
| Canale CDJ | −90,3 | **−90,0** | +0,26 | ≤ −80 | PASS 10,0 dB |
| EQ β3 sola (unweighted) | −89,2 | −88,9 | +0,31 | — | — |
| 5-way v031, θ0 | −83,9 | **−83,2** | +0,73 | ≤ −80 | PASS 3,2 dB (era 3,9) |
| 5-way v031, θ50 | −79,4 | −78,2 | +1,20 | — | dato |
| Bus FX send | −100,8 | −100,7 | +0,09 | ≤ −88 | PASS 12,7 dB |
| Ritorno FX (uno) | −96,4 | −96,3 | +0,13 | — | 4 ritorni = −90,3 |
| Send chain a canali vivi | −98,5 | −98,1 | +0,43 | — | dec. 95 invariata |
| Summer DJ bus | −107,5 | −107,3 | +0,16 | — | trascurabile |
| Summing master | −101,9 | −101,8 | +0,14 | — | trascurabile |
| CUE (catena) | −114,5 | −114,4 | +0,09 | ≤ −90 | PASS 24 dB |
| Filtro (a) ideale, fc max | −91,4 | **−89,9** | +1,47 | ≤ −80 | PASS 9,9 dB |
| Filtro (a) ideale, fc media | −117,4 | −115,8 | +1,60 | ≤ −80 | PASS largo |
| Filtro (a) ideale, fc minima | −139,2 | −123,6 | +15,6 | ≤ −80 | PASS largo (prima il floor era quasi solo OTA) |
| Filtro variante B, fc max | −81,9 | **−80,6** | +1,30 | ≤ −80 | PASS 0,6 dB (era 1,9) |
| Phono, uscita (unweighted 10 Hz–20 kHz) | −79,8 | −78,8 | +1,02 | — | EIN 1,79 → ~2,0 µV; ~18 dB sotto il fruscio del vinile (era 19) |
| Drive 5-way (D6) | −87,6 | −87,6 | 0 | — | invariato (domina il VCA) |
| Stadio master | −119,2 | −119,2 | — | ≤ −92 | macro propria senza Rn: integrazione già manuale, non toccato |

**Sistema ricalcolato (potenze, condizioni §2)**: 4 canali −84,0 ⊕ 5-way
−83,2 ⊕ 4 ritorni −90,3 ⊕ summer (−107,3 / −96,2) ⊕ master −119,2 =
**−80,0 dBu A-wtd → PASS 2,0 dB sul target ≤ −78** (era −80,5 / 2,5 dB).
Nessun esito si ribalta. Margini più stretti da tenere d'occhio: 5-way
(3,2 dB) e filtro variante B a fc max (0,6 dB, dato d'ingresso per q70).

Con i moduli MIC/MONO del primo prototipo (1 MIC a 30 dB + 3 MONO,
mandate chiuse): −79,8 dBu A-wtd. Il MIC a 45 dB porta a ~−78,4.

I numeri dei RISULTATI dei singoli moduli restano come storico: fa fede
questa tabella. Non ricalcolati (netlist senza misure a punti, storici o
superati): eq-serie/cascade-noise e -b2, filtro/svf-noise-* senza 71A,
five-way/module-noise e -bank, param-cell-*, master-out/compB-noise.

