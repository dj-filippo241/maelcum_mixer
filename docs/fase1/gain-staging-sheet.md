# GAIN-STAGING SHEET GLOBALE — v1.0 (2026-09-18)

> La tabella unica dei livelli: ogni nodo del mixer, dal suo nominale al suo estremo,
> con il dominio di alimentazione che lo ospita. Richiesta esplicita di Filippo:
> «tutti i gain vanno bilanciati col resto del progetto». Questo documento È quel
> bilanciamento. I valori [P] sono provvisori finché la simulazione non li conferma.
> Riferimenti: 0 dBu = 0,775 Vrms; +24 dBu = 12,28 Vrms = 17,4 Vpk.

## 1. Mappa dei domini di alimentazione [C — proposta ingegneristica; REV decisione 93 2026-10-01: raw dedicati per dominio]

| Dominio | Generazione | Cosa alimenta | Capability sine (conservativa, carico medio) |
|---|---|---|---|
| ±26 V raw [M] (W3 dedicato, dec. 93) | PSU principale, ferrite + bulk locale nel modulo master; statici ±23,6…29,2 V su rete ±10% | SOLO stadio HV d'uscita master | worst (rete −10%, statici 23,6): +25,2…+25,5 dBu VERIFICATO in sim (Test 13); rete nominale/alta: ≥+26,3 dBu |
| ±18 V audio | LM317/LM337 a 19,2 V + cap-moltiplicatore **dal raw ±27 V** (W1, dec. 93) | percorso canale, filtro, 5-way, summing FX e master, master level VCA (sezione audio), front out, generic | ~+23 dBu |
| ±15 V ultra-low-noise | pre-reg LM317/337 ±16,5 V **dal raw ±22 V** (W2) → LT3045/LT3094 → ±15,0 V (decisioni 54/93: LT3045 Vin max 20 V, Vout max 15 V) | front-end phono, primo stadio mic, generatori e distribuzione CV, metering, CUE/cuffia, OTA filtro | ~+20 dBu |
| ±15 V switch/logica | 78L15/79L15 diretti dal raw ±22 V (dec. 90c/93) | switch π SPDT kill/assign/LINE-PHONO (ADG14xx-class), logica | — |
| +5 V control | 7805/LM2940-class **nel modulo PSU** da W4 (dec. 93: sul backplane viaggia il +5 V regolato) | LED, logiche selettori, relay mute | — |

Regola: nessun raw entra mai in un op-amp (correzione 1 della review; dec. 93:
±27/±22 passano solo dai regolatori locali, ±26 [M] solo dallo stadio discreto).
Il +24 dBu vero esiste solo all'uscita XLR, dove lo stadio discreto lavora
sugli statici [M].

## 2. Catena principale — livelli per nodo

### Ingressi
| Nodo | Nominale | Max atteso | Estremo (user error) | Dominio | Note |
|---|---|---|---|---|---|
| Phono: testina MM | 5 mV (3-11 mV) | 11 mV | — | — | DJ standard + MM alta qualità (dec. 62) |
| Phono: out blocco RIAA | −2 dBu (5 mV × 42 dB) | +5 dBu (11 mV) | — | ±15 V LN | gain totale **42 dB** [P — risolve 40 vs 42: con 42, testina 5 mV arriva quasi a nominale; split primo stadio 21,3/26 dB rinviato alla simulazione phono]; overload ≥ +18 dBu dal blocco (Rev A) |
| Line/CDJ RCA | 0 dBu (sorgenti −10 dBV…+4 dBu) | +8 dBu | — | ±18 V | |
| Mic dinamico | 1 mV | 10 mV | — | ±15 V LN | gain 30-60 dB; regola operativa: con sorgenti calde NON servire 60 dB (warning LED) |
| Generic mono | 0 dBu | +8 dBu | +18 dBu tollerati senza danno | ±18 V | Z ≥ 100 k |

### Canale DJ (per canale, stereo)
| Nodo | Nominale | Max programma | Estremo | Dominio | Margine | Note |
|---|---|---|---|---|---|---|
| Post-GAIN (−∞…0…+10, detent 0) | 0 dBu | +10 dBu | +18 dBu | ±18 V | 5 dB | l'estremo = sorgente calda + gain +10 (user error): saturazione morbida OPA1612, recuperabile |
| Post-EQ (bande +6 max) | 0 dBu | +16 dBu | +20 dBu | ±18 V | 3 dB | +20 = boost multipli su programma già caldo: intenzionalmente al limite (filosofia progetto) |
| Filter send | 0 dBu | +16 dBu | — | ±18 V | | pre-fader, post-EQ |
| Filter return (post-drive) | 0 dBu | +16…+20 dBu (drive inserito) | saturazione voluta | ±18 V | | vedi modulo filtro |
| Post-FADER (−∞…0) | 0 dBu | +16 dBu | — | ±18 V | | slider linked ≤0,5 dB |
| Out driver → DJ BUS | 0 dBu | +16 dBu | — | ±18 V | | Z ≤ 50 Ω |

### Modulo filtro (B′, decisione 67)
| Nodo | Nominale | Max | Dominio | Note |
|---|---|---|---|---|
| Core SVF in/out | 0 dBu | +16 dBu | ±18 V | 8 core mono (4 stereo) |
| Picco di risonanza | — | +10 dBu sopra il livello (oscillazione +6…+10 dBu, locked) | ±18 V | soft limiting |
| Overdrive (per sezione HPF/LPF) | 0 dBu in | uscita fino a saturazione VOLUTA | ±18 V | colore intenzionale |
| Recovery post-drive | 0 dBu | **+23 dBu clean** (non +24: il dominio ±18 qui basta; il +24 vero vive solo al master) | ±18 V | raffinamento [P] del target documenti "≥+24 where practical" — qui NOT practical, e va bene così |
| Low-Z out → return | 0 dBu | +20 dBu | ±18 V | 20-50 Ω |

### DJ BUS → 5-way
| Nodo | Nominale | Max | Dominio | Note |
|---|---|---|---|---|
| DJ BUS (somma 4 canali) | 0 dBu | +12 dBu (4 canali correlati a 0) | ±18 V | doc: somma correlata +12 dB |
| 5-way IN pad **−6 dB** [C] | −6 dBu | +6 dBu | ±18 V | il pad libera headroom per i boost di banda; makeup +6 in uscita → nessun effetto udibile |
| Celle banda (+15 max) | −6 dBu | +15 dBu interno (boost estremi) | ±18 V | worst +21 dBu: entro capability +23 |
| Drive 5-way (taper da decisione 24: CCW=0, 50%=ottimale +7 clean, >50%=saturazione progressiva) | — | saturazione voluta | ±18 V | taper da tradurre in law elettrica (dec. 24) |
| 5-way OUT makeup **+6 dB** [C] | 0 dBu | +18 dBu | ±18 V | → MASTER SUM |

### Modulo FX
| Nodo | Nominale | Max | Dominio | Note |
|---|---|---|---|---|
| Bus summing (12 contributori stereo) | 0 dBu | +10,8 dBu (incorrelato) / +21,6 (correlato worst) | ±18 V (+23) | margine 1,4 dB sul worst assoluto: raro e a saturazione morbida; i resistori di injection si calibrano in simulazione |
| Loop di feedback (reroute max 0 dB) | — | oscillazione autosostenuta = BY DESIGN | ±18 V | gain di anello ≤ 1 per costruzione (reroute max unity); eccessi (gain interno del pedale) limitati dalla saturazione morbida del bus: non distruttiva, recovery misurabile |
| Send pad → pedale | 0 dBu bus | −20 dBu al pedale (pad prototipo, selezionabile 0/−10/−20 [P]) | ±18 V | hot bus +18 → pedale −2 dBu |
| Return in (≥1 MΩ) | −20 dBu (pedale tipico) | +18 dBu tollerati | ±18 V | **REGOLA (K4)**: livello_in × gain ≤ +23 dBu del dominio; la violazione = clipping morbido + clip warning, mai danno |
| Return gain −∞…0…+20 | out 0 dBu con pedale a −20 e gain +20 | — | ±18 V | il +20 serve per riportare a nominale i ritorni deboli, non per spingere |
| Reroute VCA (solo attenuazione, law a tratti doc, smoothing 1-5 ms) | — | — | ±18 V audio / CV ±15 LN | |

### Master
| Nodo | Nominale | Max | Dominio | Note |
|---|---|---|---|---|
| MASTER SUM (5-way + 4 FX ret + mic + generic) | 0 dBu | +16…+18 dBu | ±18 V | margine ≥5 dB |
| MASTER LEVEL VCA (−∞…0…+6) | 0 dBu | +16 dBu tipico; +6 su worst +18 = saturazione morbida intenzionale | ±18 V | **risolve questione 31**: uso normale ampio margine; l'estremo +6 su programma già estremo è user error e satura morbido (THAT 218x, verifica in sim) |
| Meter pickup (post-level) | — | scala −42…+18 dBu, 20 segm × 3 dB | — | decisione 53 |
| Front ±18 V → HV [M] (composite) | 0 dBu | +24 dBu | statici [M] out | XLR capability +25,4…+25,6 dBu VERIFICATA (dec. 86; dec. 93: worst rete −10% = statici ±23,7 V, PASS) ✓ requisito |
| BOOTH (pre-level, −∞…0) | 0 dBu | +18 dBu | ±18 V | XLR |
| REC (pre-tutto, unity) | **0 dBu fissi** | segue il sum | ±18 V | decisione 63; pad solder 0/−10/−20 per registratori sensibili |

### CUE / cuffie
| Nodo | Nominale | Note |
|---|---|---|
| CUE bus (somma cue attivi) | 0 dBu | ±15 V LN |
| Mix CUE/MASTER (CCW=cue, centro=50/50, CW=master) | — | pot passivo + buffer |
| Amp cuffia | ~1 Vrms su 32-250 Ω | 2 uscite, level condiviso, isolamento alimentazione |

## 3. Allocazione rumore (target [P] — validazione in simulazione, correzione 13 review)

| Punto di misura (ingressi terminati, gain nominali) | Target residuo A-wtd |
|---|---|
| Out driver di canale | **≤ −80 dBu A-wtd** (dec. 89, 2026-09-30: out driver, ingressi terminati, gain nominali; misurato −90,3 = margine 10,3 dB, nessuna fix) |
| Bus FX send (contributori terminati) | **≤ −88 dBu A-wtd** (dec. 89 conferma: misurato −98,9/−100,8 = margine 12,8 dB; ritorno FX = coda 71A) |
| Filtro (send 0 dBu, out core) | **≤ −80 dBu A-wtd** (dec. 89: core nudo (a) ideale −91,4 PASS, die reale −84…−76 a fc max = al limite → input per l'ascolto q70; (c-B) in target) |
| Out 5-way | **≤ −80 dBu A-wtd** (dec. 88, 2026-09-30: out modulo, ingressi terminati, gain nominali, drive θ0; misurato −83,2 v03 / −83,9 v031 rerun 2026-10-01, margine 3,9 dB; il rumore segue la law del drive: +3,6 dB a θ50 con +7 dB di segnale) |
| XLR MASTER (fader unity) | stadio ≤ −92 (misurato −119,2 VALIDO); **sistema ≤ −78 dBu A-wtd** (dec. 89, condizioni dichiarate docs/06 §2) |
| Isolamento control→audio | ≥ 100 dB (verso corretto: il controllo resta 100 dB sotto l'audio) |
| Phono | budget dedicato al design Rev A/B (input-referred, test inverse-RIAA) |

Nota di verifica (2026-09-27): 5-way out SIMULATO a −108,4 dBu (integrato
20 Hz–20 kHz non A-pesato, macro uniforme ~6 nV, LM13700/THAT 2181 assenti)
= 18,4 dB di margine sul target −90; banca 72% del contributo, celle 28%.
Dettagli: `docs/fase2/five-way-module.md` §8.4 (`sim/five-way/module-noise.cir`).

**[REVISIONE 2026-09-30 — la nota sopra è INVALIDA DUE VOLTE]** (righe Out driver canale ≤−92, Bus FX ≤−88 e XLR MASTER ≤−92: **DA RITARARE** dopo i budget mancanti — EQ β3 reale −89,2 dBu supera da sola il −92 di canale; voce 71A docs/02): (1) quirk
LTspice `.meas INTEG` → tutti i totali √INTEG del repo ~21,5 dB ottimisti;
(2) il rumore dei THAT 218x era assente. Misura corretta con 6 218x reali
nel percorso mono (5 gate + drive, −98 dBV datasheet): **5-way out −77,3 dBu
(θ0) / −73,0 (θ50) — il target −90 di questa tabella è irraggiungibile con
l'architettura bloccata**; realistico con fix ingegneristiche −83…−86 A-wtd.
Target 5-way RISOLTO: **≤ −80 dBu A-wtd ratificato (decisione 88)** dopo
benchmark su 9 costruttori della scena (`docs/05-benchmark-preamp-scena-
2026-09-30.md`). Restano **DA RITARARE (voce 71A)**: canale, bus FX, XLR
master — dopo la simulazione dei budget mancanti [→ FATTA 2026-09-30:
decisione 89, righe §3 aggiornate + docs/06; sistema VERIFICATO
2026-10-01: −80,5 dBu A-wtd = PASS 2,5 dB (docs/06 §7)]. Dettagli: five-way §8.9 + `sim/five-way/RISULTATI-module-noise-v021.md`.
Impatto sistema: il 5-way domina il rumore della catena master → anche
XLR MASTER ≤−92 va ritarato sulla voce 71A (budget canale/FX/master) [FATTO: dec. 89 → stadio ≤−92 confermato, sistema ≤−78 A-wtd].
**RITARATURA FATTA (decisione 89, 2026-09-30)**: canale ≤ −80, FX send
≤ −88 confermato, filtro ≤ −80 (nuova riga), sistema ≤ −78 — budget e
sintesi in `docs/06-ritaratura-rumore-71A.md`.

## 4. Questioni chiuse da questo sheet

- **31** (margine VCA master): RISOLTA — dominio ±18 V, uso normale con ≥5 dB di margine, estremo = saturazione morbida documentata (verifica sim).
- **47** (headroom canale): RISOLTA — dominio ±18 V invece di ±15: worst user error +18 con 5 dB di margine.
- **52** (headroom bus FX + regola ritorni, K3/K4): RISOLTA — bus su ±18 V, loop unity bounded by design, regola scritta "in × gain ≤ +23 dBu".
- **Phono 40 vs 42 dB**: RISOLTA a livello di sistema — **42 dB** (5 mV → −1,8 dBu, quasi nominale a gain di canale 0). Split primo stadio: alla simulazione phono.
- **K5** (dominio overdrive): RISOLTA — modulo filtro su ±18 V, recovery +23 dBu clean (il "+24 where practical" dei documenti qui non è practical: rilassamento documentato, il +24 vero sta solo al master).
- **Nuova [C]**: 5-way con riferimento interno −6 dB (pad in / makeup out) — protegge i boost +15 dB senza effetto udibile.

## 5. Conseguenze per i design doc esistenti

- `master-out.md`: summing e VCA passano da ±15/±18 misti a **±18 V unici per la sezione audio** (il ±15 LN resta per CV/meter); REC confermato 0 dBu (addendum già presente).
- `cdj-line-channel.md` v0.2: dominio audio ±18 V (non ±15); level plan da aggiornare con i valori di questo sheet.
- `docs/fase2/filter-module.md` (v0.1, 2026-09-24): recovery +23 dBu recepito; CV shaper per la legge dei knob (decisione 70) = design v0.2.
