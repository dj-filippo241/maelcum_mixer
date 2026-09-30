# 06 — Ritaratura rumore sheet §3 (voce 71A) — PROPOSTA per ratifica

Data: 2026-09-30. Stato: COMPLETA nei numeri (canale + filtro + FX send +
5-way + master), in attesa della ratifica di Filippo (regola 2: i target di rumore vincolano il
risultato musicale → decisione sua). Origine: decisione 88 ha ratificato
il target 5-way (≤ −80 dBu A-wtd) e ha lasciato aperti i target di canale,
FX e sistema, invalidati dal quirk INTEG di LTspice (§8.9 five-way).

## 1. Numeri nuovi (campagna 2026-09-30, metodo corretto: densità 10+ punti, trapezoidale, mai INTEG)

| Blocco | Punto di misura | Unweighted | A-wtd | Target sheet attuale | Esito |
|---|---|---|---|---|---|
| Canale CDJ completo | out driver, carico 10k, gain nominali, ingressi terminati | −88,4 dBu | **−90,3 dBu** | ≤ −92 A-wtd | FAIL 1,7 dB (`sim/cdj/RISULTATI-channel-noise-71A.md`) |
| EQ β3 (sola) | uscita EQ | −89,2 dBu | — | — | 82% della potenza di canale |
| GAIN VCA 218x (solo) | — | −98 dBV datasheet | — | — | 18% della potenza di canale |
| 5-way modulo | out modulo (dec. 88) | −81,0 | **−83,2** (−85,5 stimato col fix Rvn, §4) | ≤ −80 A-wtd RATIFICATO | PASS 3,2 dB (5,5 col fix) |
| Filtro core OTA nudo (a) | buffer LP, fc max 37 kHz | **−90,3** | −91,4 | ≤ −90 (send 0 dBu) | sim ideale AL LIMITE; die reale −84…−76 = FAIL 6-14 dB (`sim/filtro/RISULTATI-filtro-noise-71A.md`) |
| Filtro a fc basse (10 Hz-1 kHz) | idem | −126…−103,7 | −139…−117 | — | PASS largo (spettro 1/f) |
| FX bus (send, jack L) | contributori terminati, pad 0 dB, carico 10k | −98,9 dBu | **−100,8 dBu** | ≤ −88 | PASS 12,8 dB (`sim/fx/RISULTATI-fx-noise-71A.md`); dominante: 3 VCA reroute ~60% (ipotesi conservativa floor −98 dBV sempre) |
| Master out (stadio) | XLR | −119,2 (VALIDO, integrazione già manuale) | — | ≤ −92 | PASS 19 dB; non è lui il limite |

## 2. Sintesi di sistema (calcolo di potenza, condizioni dichiarate)

Condizioni: 4 canali CDJ terminati e attivi, DJ bus, 5-way in catena,
4 ritorni FX terminati, drive θ0, fader unity, out XLR. Contributi:
4× canale (−90,3 → −84,3 di somma) ⊕ 5-way (−83,2) ⊕ 4× FX bus
([−88 → −82] in attesa) ⊕ master (−119,2 trascurabile):

**Sistema stimato ≈ −78…−79 dBu A-wtd**. Nota: il contributo FX al sistema
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

## 3. Proposta di ritaratura sheet §3 (da ratificare)

| Riga sheet | Target attuale | PROPOSTA | Nota |
|---|---|---|---|
| Out driver di canale | ≤ −92 A-wtd | **≤ −90 A-wtd** + fix (a) e/o (b) sotto | misurato −90,3: −90 è onesto solo CON le fix; in alternativa deroga ≤ −88 senza fix |
| Bus FX (send) | ≤ −88 | **≤ −88 confermato** (PASS 12,8 dB misurato; opzione: stringere a −95 senza fix) | il ritorno FX va al master: budget dedicato in coda |
| Filtro (send 0 dBu) | ≤ −90 | **≤ −90 confermato MA con vincolo topologico**: la scelta musicale (a) OTA nudo NON lo rispetta a fc max col die reale (−84…−76) | se (a): riga filtro ≤ −76 a fc max (deroga esplicita) oppure (c-B) VCA nel loop che riporta il rumore in target (input nuovo per q70 — l'ascolto resta sovrano) |
| 5-way | ≤ −80 A-wtd (dec. 88) | invariato | margine reale ~5,5 dB col fix Rvn (§4) |
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
5-way è conservativo di ~2,3 dB (reale ≈ −85,5). Direzione sicura, nessun
redesign; il rerun consolidato (Rvn corretto + invertitori gate §8.10 +
eventuale I/V) va fatto nella coda 71A. Regola: il valore Rvn va derivato
dal dBV del datasheet (R = en²/4kT), non copiato tra configurazioni.

## 5. Coda operativa dopo ratifica

1. Aggiornare sheet §3 con i target ratificati (punto di misura e pesatura
   dichiarati per ogni riga, criterio dec. 88).
2. Fix canale (a)/(b) se ratificate → nuovo run di conferma.
3. Rerun consolidato module-noise-v03 (Rvn + invertitori §8.10).
4. Rumore del filtro: entra nell'ascolto q70 come dato (non decide da solo).
5. Budget canale di RITORNO FX (vero contributo FX al sistema): coda 71A.
6. Budget summer DJ bus/master: al design di sistema (task 7) o a banco.
7. Cleanup residui run interrotta: sim/fx/dbg-bus-noise.* (voce 14: chiedere
   prima di cancellare).
