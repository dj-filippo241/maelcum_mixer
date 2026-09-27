# FASE 1 — Modulo CANALE CDJ/LINE: design circuitale v0.3

> **v0.3 (2026-09-25)**: SUPERSEDE la v0.2 per §3.3 (EQ in serie, decisioni 76/77 —
> celle a contribuzione bocciate dalla simulazione) e allinea §4-§8 alle misure beta-2
> (`docs/fase1/eq-serie-v0.3.md`). Il resto del documento è invariato dalla v0.2.

> **v0.2 (2026-09-18)**: SUPERSEDE la v0.1 (in storia git). Allineato a: decisioni 58-76,
> gain-staging sheet v1.0, status doc rev2, e validazione matematica dell'EQ
> (`sim/eq_analysis.py` + `sim/eq_results.txt`) — **quest'ultima smentita in parte dalla
> simulazione LTspice (2026-09-24, `sim/cdj-eq/RISULTATI-eq.md`): la math era zero-fase
> per LOW/HIGH → decisione 76, EQ in serie per banda (Baxandall); ridisegno in v0.3.**
> Scope: SOLO line/CDJ — phono Rev A resta
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
[PROVVISORIO — corretto da datasheet 2026-09-27: 218x = SINGLE channel, "dual" sono i
porti di controllo]: 2× THAT 2180/2181 (stessa famiglia del master level — un solo tipo di
VCA in tutto il mixer, ricambio unico; tracking L/R via trim di law o selezione coppie,
voce 37) pilotati da UN pot con detent → shaper di law →
CV 0-5 V (generatore su ±15 V LN). Law: −∞ a full CCW, 0 dB al detent (~50% corsa),
+10 dB a fine CW. **Law e headroom VERIFICATI in simulazione (2026-09-27, §7
item 7)**: detent 0 dB esatto, floor −100 dB, +18 dBu pulito con 5,5 dB di
margine; il tracking L/R richiede trim di law (2181) o selezione di coppia
(2180) — voce 37. Alternativa economica da scartare solo se la sim dice che il VCA
colora: pot doppio selezionato + trim (più lavoro di calibrazione, tracking a rischio).

### 3.3 [C] EQ 4 bande — SERIE per banda, famiglia Baxandall (v0.3, decisioni 76/77)

> **v0.3 (2026-09-25)**: sostituisce integralmente le celle a contribuzione della
> v0.2, bocciate dalla simulazione (fase dei filtri LOW/HIGH —
> `sim/cdj-eq/RISULTATI-eq.md`, questione 62 → decisione 76). Design completo,
> griglie misurate e law del pot: **`docs/fase1/eq-serie-v0.3.md`** (stato beta-3)
> + netlist in `sim/eq-serie/`.

Architettura per lato: 4 celle in cascata + buffer, **12 sezioni op-amp** (3 quad):
buffer in −6 dB (riferimento interno, principio dec. 73) → LOW shelf complementare
(R 1k / Rp 31k: kill −29,3 dB a gonna larga, boost +6 shelf liscio) → LM campana
250 Hz sottrattiva `−(1−b·BP)` (notch esatto −45 dB al centro) → MH campana 1 kHz
(stessa famiglia) → HIGH sottrattiva `−(1−b·HP2)` (boost +6 shelf; kill: bump +2 dB al corner,
−9…−14 dB a 20-35 kHz → questione 68) → make-up +6 dB con trim (azzera l'offset di detent).

Proprietà misurate (LTspice, macromodelli — dettagli e griglie in eq-serie-v0.3.md §9):
1. Detent piatto: ±0,02 dB relativo su 20 Hz–35 kHz (offset costante −0,12 dB → trim).
2. Boost +6,0 dB per banda [requisito locked rispettato]; worst all-boost +7,5 dB @250.
3. Kill: shelf −30 dB (LOW: −29,3 con gonna fino a 1 kHz; HIGH: bump +2/−9…−14 → questione 68),
   campane: notch −45/−66 dB al centro, larghezza da Q. (Numeri aggiornati alla correzione Q HP2=0,707 del 2026-09-25.)
4. **All-kill ≠ silenzio**: residuo +1,1 dB @5 kHz (tra le gonne dei notch e il kill
   HIGH debole) → il fader resta il muto vero; auto-mute = questione 59 (numeri
   definitivi registrati).
5. Curva dub (LOW+HIGH su, medi giù): +5,6 / −45 / −46 / +5,5 dB — estetica target.
6. Rumore: −110,7 dBu integrato (target ≤−92: margine 18,7 dB; migliora con op-amp reali).
7. Livelli: picco interno 7,6 V a +16 dBu all-boost (riferimento −6 dB); estremo
   +18 dBu = saturazione d'uscita intenzionale, niente clipping a metà catena.
8. Tracking stereo: pot doppi ≤1% → L−R ≤0,16 dB (PASS ≤0,25); 2% → 0,32 (limite,
   trim) — questione 53; alternativa VCA documentata.

Law del pot (specifica eq-serie-v0.3.md §10): asimmetrica — boost +6 in mezza corsa
(lineare), cut −30 dB con accelerazione negli ultimi 5% (filosofia dec. 70); detent
meccanico con click a metà. Taper custom su pot doppi conduttivo-plastica → sessione
hardware voce 40. Validazione a orecchio della law sul prototipo M4L (dec. 78,
IN PAUSA fino a design completo — direzione Filippo 2026-09-25).

EQ2 di FX send/return (questione 65): stessa famiglia di celle (2 bande: shelf LOW
~120 Hz + campana/shelf HIGH ~4,5 kHz, law dedicate) — design nel modulo FX.

### 3.4 [D] CUE send
Punto locked: post-EQ, pre-filter, pre-fader. Buffer dedicato → switch CUE di canale →
CUE bus. Nessuna elaborazione.

### 3.5 [E] FX send
EQ 2 bande (**nota 2026-09-24**: il v0.2 diceva "celle a contribuzione semplificate,
stesse math della §3.3" — quelle math sono smentite dalla simulazione (fase dei filtri
shelf, §3.3) e la decisione 76 passa alla topologia in serie: EQ2 da allineare in EQ
v0.3, questione 65) con law dedicate [BLOCCATO dai doc]: LOW "tiene i bassi per quasi tutta
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
| Post-EQ | 0 dBu | +16 dBu | saturazione d'uscita intenzionale (worst all-boost misurato +7,5 dB; il rail ±16,5 V = +23,5 dBu fa da tetto). EQ con riferimento interno −6 dB: picchi interni ≤7,6 V a +16 dBu (`sim/eq-serie/cascade-b2-level.cir`) | ±18 V (+23) |
| Filter return | 0 dBu | +16…+20 (drive inserito) | saturazione voluta | ±18 V |
| Post-FADER / out | 0 dBu | +16 dBu | — | ±18 V |

## 5. Rumore (target sheet §3: ≤−92 dBu A-wtd all'out driver)

**Misurato v0.3 beta-3** (`sim/eq-serie/cascade-b3-noise.cir`, cascata EQ al detent,
20 Hz–20 kHz, macro reali OPA1654/OPA1612 da `sim/lib/opamp-audio.inc`):
**−110,7 dBu** integrato → margine 18,7 dB sul target (la macro "uniforme" di beta-2
era già calibrata vicina alla OPA1654 reale: numero CONFERMATO, non solo stimato).
Regole confermate: pot 10 kΩ sulle celle (voce 48), summer a 49,9 kΩ (non 100 k),
bracci shelf ≤31 kΩ; OPA1612 solo su nodi a bassa Z (regola in libreria: bipolare,
sorgenti <100 Ω). Restano da aggiungere: VCA di gain (a monte, già nel budget del
GAIN — macro THAT 218x pronto in `sim/lib/that2181.inc`) e out driver.

## 6. BOM di massima v0.3 (esclusi pot/fader/connettori/pannello)

| Voce | Qtà approx | Costo |
|---|---|---|
| OPA1654 quad (celle EQ serie: 3 per canale) | 6 | ~30-36 € |
| OPA1612 dual (buffer in/make-up EQ, out driver) | 2-3 | ~10-15 € |
| THAT 2181 (VCA gain; + eventuali VCA di banda se tracking 53 sceglie VCA) | 1-3 | ~6-18 € |
| Reti RC celle (0,1% bracci shelf, C0G/PP campane e HP2) | — | ~10-15 € |
| LM3915 ×2 + clip detector | 3 | ~3 € |
| Switch analogici assign FX | 4 | ~6-10 € |
| Regolatori locali (LM317/337 + LT3045/3094) + passivi | — | ~12-15 € |
| **Totale stimato per canale stereo** | | **~80-110 €** (v0.2: 70-95; delta = buffer/make-up + reti. Fuori tabella: 4 pot doppi taper custom dell'EQ → voce 40) |

## 7. Simulazioni — stato (aggiornamento 2026-09-27)

FATTE:
1. Celle a contribuzione (v0.2): `sim/cdj-eq/RISULTATI-eq.md` — finding critico
   di fase → decisione 76, topologia serie. THD: non misurabile coi macromodelli
   lineari, si verifica al prototipo col modello TI reale.
5. Tracking/mismatch: fatto per entrambe le topologie. Serie: pot doppi ≤1% →
   L−R ≤0,16 dB PASS; 2% → 0,32 limite (`low-cell-track.cir`, `cascade-track.cir`).
6. **EQ serie v0.3 completa (beta-3)**: celle LOW/MID/HIGH + cascata 4 bande +
   riferimento interno −6 dB + summer 49,9k: `sim/eq-serie/` (9 netlist),
   griglie e finding in `docs/fase1/eq-serie-v0.3.md` §9.

7. **GAIN VCA THAT 218x FATTO (2026-09-27, `sim/cdj/vca-law.cir` +
   `vca-headroom.cir`)**: law dB(θ) via shaper a tratti VERIFICATA (−100…0…+10
   dB esatti ai θ di progetto, detent 0 dB a 1e-8, costante 6,1 mV/dB);
   headroom: +18 dBu a GAIN 0 passa pulito (8,70 V out, margine 5,5 dB sul
   clamp ±16,5); a GAIN +10 su +18 = violazione regola K4 → clamp a 16,5 V
   (user error documentato, non guasto di design); tracking L/R SENZA trim di
   law: ±1,3 dB in attenuazione profonda, ±0,83 a −50 dB, 0 al detent, ±0,17
   a +10 → il trim di law del 2181 azzera (dati per 53/40/voce 37). THD non
   misurabile in macro lineare: stima da datasheet, verifica al prototipo
   (stesso trattamento di eq-serie §9.7).

8. **Summing DJ BUS 4 canali FATTO (2026-09-27, `sim/cdj/djbus-level.cir` +
   `djbus-crosstalk.cir`)**: worst sheet CONFERMATO — 4×0 dBu correlati →
   +12,0 dBu (4,36 Vpk, margine 11,6 dB sul clamp ±16,5); singolo canale
   +16 dBu → 8,66 Vpk (margine 5,6 dB); estremo 4×+16 correlati (+28 dBu =
   violazione K4) → clamp ±16,5 V (user error documentato, non guasto).
   Crosstalk via nodo di bus (virtual earth, classe OP1612, topologia
   [PROVVISORIO] R 10k + driver 47 Ω): −98 dB @1 kHz, −78 @10 kHz, −72
   @20 kHz, −67 @35 kHz — degrada 6 dB/ott col loop gain, inudibile;
   nella pratica comanderà l'accoppiamento PCB (design di sistema, 21).

RESTANTI:
3. Peak detector: ballistica a 10 Hz (requisito infrasub) e a 35 kHz —
   condiviso col metering FX v0.2; requisiti = questione 19 (aperta)
9. Variante cella HIGH crossfade-LP2: solo se la questione 68 la sceglie

## 8. Questioni generate/aggiornate da questa v0.3 (stato 2026-09-25)

- 53 (tracking EQ stereo): numeri misurati — pot doppi ≤1% → L−R ≤0,16 dB PASS;
  2% → 0,32 limite/trim; alternativa VCA documentata. Scelta: sessione hardware (40)
- 59 (all-kill): numeri DEFINITIVI dalla cascata — residuo +1,1 dB @5 kHz:
  l'all-kill non è silenzio; fader o auto-mute (b). Ratifica dopo la 68
- 68 NUOVA (APERTO-F): profondità kill HIGH — cella sottrattiva (bump +2/−9…−14 dB,
  zero silicon extra) vs crossfade-LP2 (−24…−30 dB, +2-3 sezioni/canale). Ascolto
  sul prototipo M4L quando riparte
- 65 (EQ2 FX send/return): allineata — stessa famiglia di celle serie (2 bande),
  design nel modulo FX
- 55 (transiente assign FX): immutata, proposta uniformata al metodo filtro
- 40 (hardware pot/fader): ora include i 4 pot doppi taper custom dell'EQ
  (specifica law: `docs/fase1/eq-serie-v0.3.md` §10)
- Review frequenze EQ con Filippo: centri 70/250/1k/5k [PROVVISORI] — le curve
  misurate della serie sono la base; ascolto sul prototipo M4L
- 62 CHIUSA → decisione 76 (EQ in serie); 66 CHIUSA → decisione 77 (kill −30 dB)
