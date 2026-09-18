# FASE 1 — Modulo CANALE CDJ/LINE: design circuitale v0.2

> **v0.2 (2026-09-18)**: SUPERSEDE la v0.1 (in storia git). Allineato a: decisioni 58-75,
> gain-staging sheet v1.0, status doc rev2, e **validazione matematica dell'EQ**
> (`sim/eq_analysis.py` + `sim/eq_results.txt`). Scope: SOLO line/CDJ — phono Rev A resta
> su carta (decisioni 56/61), il front-end dedicato + selettore PHONO/LINE arriverà in Rev B
> del modulo senza cambiare il resto della catena (status doc PDF §6: "dedicated PHONO and
> LINE front ends → selector → common DJ GAIN").

## 1. Requisiti (valori locked aggiornati)

- Catena [BLOCCATO]: RCA stereo → protezione → buffer → GAIN → EQ 4 bande → split post-EQ:
  (1) CUE, (2) FX SEND, (3) dry → FILTER SEND/RETURN (modulo filtro esterno, decisione 60)
  → METER DJ → FADER → out driver ≤50 Ω → DJ BUS
- GAIN [BLOCCATO]: −∞ → 0 (detent) → +10 dB; stereo linked; tracking ≤0,5 dB
- EQ [BLOCCATO nel comportamento]: 4 bande LOW/LOW-MID/MID-HIGH/HIGH; −∞ → 0 (flat, detent)
  → +6 dB; tracking stereo ≤0,25 dB; law lenta al centro e rapida agli estremi
- EQ frequenze [PROVVISORIO — review con Filippo aperta]: 70 Hz Q~0,7 (shelf) /
  250 Hz Q~0,8 (bell) / 1 kHz Q~0,9 (bell) / 5 kHz Q~0,7 (shelf)
- CUE [BLOCCATO]: post-EQ, pre-filter, pre-fader
- FX SEND [BLOCCATO]: pre-fader, pre-filter; EQ2 (LOW ~120 Hz, HIGH ~4,5 kHz, −∞..0..+6);
  level −∞..0; assign MULTIPLI simultanei S1-S4 con precision analogue switch
- Filtro [BLOCCATO]: switch 3 vie HPF/OFF/LPF sul canale; audio via send/return al modulo
  filtro; break-before-make + ramp 1-5 ms (nel modulo filtro)
- METER DJ [BLOCCATO]: post-filter/overdrive, pre-fader; peak con persistenza; calibrazione
  identica tra canali (trim di calibrazione previsti)
- FADER [BLOCCATO]: slider conduttivo-plastica stereo linked ≤0,5 dB; buffer ≤50 Ω
- Livelli: gain-staging sheet §2 (dominio audio ±18 V; ±15 V LN per CV/meter/phono futura)

## 2. Diagramma a blocchi (metà canale L; R identica e linked)

```
[RCA IN] ─► [A] PROT+BUFFER ─► [B] GAIN (VCA stereo, detent unity) ─► [C] EQ 4 BANDE
                                                                          │
                                          ┌───────────────────────────────┼──────────────────┐
                                          │                               │                  │
                                   [D] CUE SEND                    [E] FX SEND          [F] FILTER I/F
                                    (buffer → CUE bus)         (EQ2 → level → assign     (send/return al
                                                                multipli S1-S4 → bus)     modulo filtro;
                                          │                        │                      switch 3 vie)
                                          ▼                        ▼                          │
                                     (modulo CUE)             (modulo FX)              ritorno filtro
                                          └────────────────────────┴──────────────────────────┤
                                                                                              ▼
                                                                              [G] METER DJ (pickup)
                                                                                              ▼
                                                                              [H] FADER + buffer
                                                                                              ▼
                                                                              [I] OUT DRV → DJ BUS
[H2] PSU locale: ±24 in → ±18 audio (LM317/337 + post-filtro) · ±15 LN (LT3045/3094:
     CV, meter, phono futura) · +5 control (LED/logiche)
```

## 3. Design per stadio

### 3.1 [A] Ingresso line + protezione
Invariato dalla v0.1: RCA dorato isolato da chassis (rondella dedicata); R serie 100 Ω +
TVS low-cap + bead; polo RC >100 kHz; buffer OPA1612 unity, Z_in ≥47 kΩ, dominio ±18 V.

### 3.2 [B] GAIN — raccomandazione: VCA stereo a singola CV
Il tracking ≤0,5 dB esclude il pot doppio meccanico diretto (±1-2 dB tipici). Raccomandato
[PROVVISORIO]: THAT 2181 (doppio VCA, stessa famiglia del master level — un solo tipo di
VCA in tutto il mixer, ricambio unico) pilotato da UN pot con detent → shaper di law →
CV 0-5 V (generatore su ±15 V LN). Law: −∞ a full CCW, 0 dB al detent (~50% corsa),
+10 dB a fine CW. Alternativa economica da scartare solo se la sim dice che il VCA
colora: pot doppio selezionato + trim (più lavoro di calibrazione, tracking a rischio).

### 3.3 [C] EQ 4 bande — celle a contribuzione bipolare (VALIDATA MATEMATICAMENTE)
**Topologia** (per banda, per lato): il segnale di banda H_i·V viene presentato al pot in
DUE polarità (+H_i e −H_i); il wiper del pot (lineare, 10 kΩ) sta al centro esatto
(k=0) e va al nodo di summing. Il riferimento (V_in via −1) completa la somma:

    V_out(f) = V_in(f) · [ 1 + Σ k_i · H_i(f) ]     k_i ∈ [−1, +1], 0 al detent

**Proprietà dimostrate dall'analisi** (`sim/eq_results.txt`, op-amp ideali):
1. Detent = piatto ESATTO (0,00 dB a ogni frequenza, per costruzione: k=0 annulla ogni
   dipendenza dai componenti delle celle) — la traccia passa come registrata
2. Boost massimo = +6,02 dB al centro banda (1+1=2) ✓ requisito locked
3. Kill mono-banda: −49,6 dB @20 Hz (LOW), profondità limitata in pratica dal matching
   delle due polarità: resistori 0,1% → pavimento ~−60 dB; 1% → ~−40 dB. Raccomandato
   0,1% sui percorsi ±H
4. Worst boost con 4 bande a +6: picco +6,64 dB (le bande si sommano poco: sono ben
   separate) → headroom eccellente, molto meglio della stima pessimistica del sheet
5. **FINDING — all-kill leak**: con tutte e 4 le bande a −∞ il canale NON tace: restano
   ~−2,6 dB @2,5 kHz e ~−2,6 dB @150 Hz. Causa: le sottrazioni complesse (fase ruotata
   dalle celle) si cancellano tra loro invece di cancellare il riferimento. Mitigazioni:
   (a) il fader esiste apposta per il silenzio totale (comportamento documentato);
   (b) opzione [C-PROVVISORIO]: auto-mute — 4 switch di fine corsa rilevano "tutti i pot
   a CCW" → FET shunt a massa sull'uscita EQ; costo ~2 €; da ratificare;
   (c) scartata la partizione complementare in fase (è il mestiere del 5-way, decisione 22)

**Implementazione** [PROVVISORIO]: per lato ~10 sezioni op-amp (4 filtri di banda +
4 inverter di polarità + 1 inverter riferimento + 1 summing). Candidati: OPA1654 (quad)
per celle/inverter + OPA1612 (dual, bipolare low-noise) per il summing. Law del pot:
shaper a tratti (stessa famiglia di curve del filtro: lenta al centro, rapida agli
estremi) realizzato sulla CV se si usa il pot come controllo di un VCA di banda, oppure
taper custom sul partitore — decide la simulazione (voce 53: tracking stereo).

**Tracking stereo ≤0,25 dB**: il pot bipolare è meccanico → due sezioni devono inseguirsi.
Metodo [APERTO — voce 53]: (a) pot doppi selezionati + misura/trim, oppure (b) celle di
contribuzione a VCA (k generato da CV unica per banda, come il gain). (b) garantisce il
tracking elettrico ma raddoppia i VCA per canale (4 bande × 1 VCA stereo): costo +~25 €.

### 3.4 [D] CUE send
Punto locked: post-EQ, pre-filter, pre-fader. Buffer dedicato → switch CUE di canale →
CUE bus. Nessuna elaborazione.

### 3.5 [E] FX send
EQ 2 bande (topologia celle a contribuzione semplificata: 2 bande invece di 4, stesse
math della §3.3) con law dedicate [BLOCCATO dai doc]: LOW "tiene i bassi per quasi tutta
la corsa, li toglie rapido solo al taglio estremo"; HIGH "taglia subito in partenza, poi
graduale". Level −∞..0. Assign multipli simultanei S1-S4: precision analogue switch
(candidati [PROVVISORIO]: famiglia ADG14xx/DG4xx low-RON low-charge-injection), uno per
destinazione, pilotati dagli switch del pannello con break-before-make + ramp 1-5 ms
(stesso metodo del selettore filtro — da ratificare, voce 55). Iniezione bufferizzata
sui bus FX (mai collegamento passivo diretto: decisione "buffered signal injection").

### 3.6 [F] Interfaccia filtro (modulo esterno)
Send/return stereo via backplane + 2 bit di modo (HPF/OFF/LPF) sulla sezione control.
Il break-before-make e la rampa vivono nel modulo filtro. **Nota fase 1**: finché il
modulo filtro non esiste, il prototipo canale si collauda con send e return ponticellati
sul backplane (bypass) — il canale funziona dry, tutto il resto si valida lo stesso.

### 3.7 [G] Meter DJ
Post-filter (return), pre-fader. Peak detector attacco <1 ms, persistenza/hold con decay
lento; [PROVVISORIO] 10 segmenti ×3 dB per lato (LM3915, range −24…+12 dBu) + LED purple
di clip con latch 300-500 ms. Trim di calibrazione per l'identicità tra canali (voce 54).
Numero segmenti definitivo: al design del modulo metering.

### 3.8 [H] Fader + [I] out driver
Slider doppio conduttivo-plastica (hardware: sessione dedicata, voce 40), −∞..0,
tracking ≤0,5 dB con selezione/trim; buffer OPA1612 ≤50 Ω → DJ BUS (injection 10 kΩ
[PROVVISORIO dai doc §24/35]). Fallback VCA come §3.2 se il tracking meccanico delude.

## 4. Level plan (da gain-staging sheet §2, corretto con i risultati EQ)

| Nodo | Nominale | Max programma | Estremo | Dominio |
|---|---|---|---|---|
| Ingresso RCA | 0 dBu | +8 dBu | — | ±18 V |
| Post-GAIN | 0 dBu | +10 dBu | +18 dBu (user error: sorgente calda + gain max) | ±18 V |
| Post-EQ | 0 dBu | +16 dBu | **+18,6 dBu** (worst boost misurato +6,64 dB) | ±18 V (+23) |
| Filter return | 0 dBu | +16…+20 (drive inserito) | saturazione voluta | ±18 V |
| Post-FADER / out | 0 dBu | +16 dBu | — | ±18 V |

## 5. Rumore (target sheet §3: ≤−92 dBu A-wtd all'out driver)

Contribuenti principali stimati: termica dei pot a wiper centrale (~2,5 kΩ equivalenti),
catena di ~20 sezioni op-amp, VCA di gain. Il budget numerico si fa in LTspice quando
installato (voce strumentazione 30). Regola anti-errore: pot a 10 kΩ (non 47 k) sulle
celle EQ — il rumore del wiper scala con la resistenza (voce 48 chiusa da questa scelta
salvo smentita della simulazione).

## 6. BOM di massima v0.2 (esclusi pot/fader/connettori/pannello)

| Voce | Qtà approx | Costo |
|---|---|---|
| OPA1654 quad (celle EQ, inverter) | 5-6 | ~25-30 € |
| OPA1612 dual (summing, buffer, driver) | 3-4 | ~15-20 € |
| THAT 2181 (VCA gain; + eventuali VCA di banda se tracking (b)) | 1-3 | ~6-18 € |
| LM3915 ×2 + clip detector | 3 | ~3 € |
| Switch analogici assign FX | 4 | ~6-10 € |
| Regolatori locali (LM317/337 + LT3045/3094) + passivi | — | ~12-15 € |
| **Totale stimato per canale stereo** | | **~70-95 €** (era 35-55 nella v0.1: la differenza è l'EQ validato a celle bipolari + meter completo + VCA — il prezzo dei requisiti locked di tracking e persistenza) |

## 7. Simulazioni in coda (LTspice — installazione da autorizzare)

1. Cella EQ completa con componenti reali: THD, rumore, interazione con impedenza di sorgente
2. VCA THAT 2181: law dB/V, distorsione vs livello a +18 dBu, margine
3. Peak detector: ballistica a 10 Hz (requisito infrasub) e a 35 kHz
4. Summing DJ BUS a 4 canali: crosstalk e worst-case
5. Tracking: sensibilità del kill depth al mismatch 0,1% vs 1%

## 8. Questioni generate/aggiornate da questa v0.2

- 53 (tracking EQ stereo): opzioni (a)/(b) descritte in §3.3 — decide la simulazione + costo
- 59 NUOVA: all-kill leak −2,6 dB: ratificare mitigazione (a) documentata e/o (b) auto-mute
- 55 (transiente assign FX): proposta uniformata al metodo filtro (break-before-make + ramp)
- 40 (hardware pot/fader): immutata, sessione dedicata
- Review frequenze EQ con Filippo: immutata (baseline validata come TOPOLOGIA, non come centri)
