# GAIN-STAGING SHEET GLOBALE — v1.0 (2026-09-18)

> La tabella unica dei livelli: ogni nodo del mixer, dal suo nominale al suo estremo,
> con il dominio di alimentazione che lo ospita. Richiesta esplicita di Filippo:
> «tutti i gain vanno bilanciati col resto del progetto». Questo documento È quel
> bilanciamento. I valori [P] sono provvisori finché la simulazione non li conferma.
> Riferimenti: 0 dBu = 0,775 Vrms; +24 dBu = 12,28 Vrms = 17,4 Vpk.

## 1. Mappa dei domini di alimentazione [C — proposta ingegneristica]

| Dominio | Generazione | Cosa alimenta | Capability sine (conservativa, carico medio) |
|---|---|---|---|
| ±24 V raw | PSU principale, ferrite + bulk locale | SOLO stadio HV d'uscita master | ~+25 dBu |
| ±18 V audio | LM317/LM337 + post-filtro RC/cap-moltiplicator | percorso canale, filtro, 5-way, summing FX e master, master level VCA (sezione audio), front out, generic | ~+23 dBu |
| ±15 V ultra-low-noise | LT3045/LT3094 (decisione 54) | front-end phono, primo stadio mic, generatori e distribuzione CV, metering, CUE/cuffia | ~+20 dBu |
| +5 V control | LDO da rail controllo | LED, logiche selettori, relay mute | — |

Regola: il ±24 V non entra mai in un op-amp (correzione 1 della review). Il +24 dBu
vero esiste solo all'uscita XLR, dove lo stadio discreto lavora su ±24 V.

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
| Drive 5-way (taper决策: CCW=0, 50%=ottimale +7 clean, >50%=saturazione progressiva) | — | saturazione voluta | ±18 V | taper da tradurre in law elettrica (dec. 24) |
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
| Front ±18 V → HV ±24 V (composite) | 0 dBu | +24 dBu | ±24 V out | XLR capability ~+25 dBu ✓ requisito |
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
| Out driver di canale | ≤ −92 dBu |
| Bus FX (contributori terminati) | ≤ −88 dBu |
| Out 5-way | ≤ −90 dBu |
| XLR MASTER (fader unity) | ≤ −92 dBu → sistema ≤ −90 dBu con margine |
| Isolamento control→audio | ≥ 100 dB (verso corretto: il controllo resta 100 dB sotto l'audio) |
| Phono | budget dedicato al design Rev A/B (input-referred, test inverse-RIAA) |

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
- Futuro `filter-module.md`: recovery +23 dBu, CV shaper per la legge dei knob (decisione 70).
