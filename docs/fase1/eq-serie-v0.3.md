# EQ SERIE v0.3 — celle Baxandall a law asimmetrica (2026-09-24/25)

> **Stato: BETA-2 (2026-09-25).** ALPHA (cella LOW) + celle MID/HIGH + cascata
> 4 bande con rumore/tracking/livelli (§9) + riferimento interno −6 dB e
> summer 49,9k (§9.6) + specifica law/taper (§10). Resta per beta-3: scelta
> op-amp reali (rumore), trim, ascolto M4L delle questioni 66-68 (prototipo
> IN PAUSA per direzione di Filippo 2026-09-25: prima il design completo).
> Origine: decisione 76 (EQ in serie, famiglia Baxandall) dopo il finding
> critico delle celle a contribuzione (`sim/cdj-eq/RISULTATI-eq.md`).
> Sostituisce CDJ v0.2 §3.3.

## 1. Il vincolo che decide tutto: boost e cut simmetrici non bastano

Cella invertente classica con pot complementare nei due bracci:

    G(s) = −Zf/Zin;  Zin = R + Za(x);  Zf = R + Zb(x)
    Za = (x·Rp) || (1/sC);  Zb = ((1−x)·Rp) || (1/sC)

Proprietà (dimostrate in simulazione):
- **x = 0,5 → G = −1 esatto a ogni frequenza** (Za = Zb per costruzione:
  il detent "piatto assoluto" della v0.2 sopravvive, ±0,02 dB misurati);
- boost e cut elettricamente **simmetrici**: ±20·log(1+Rp/R).

Il requisito è asimmetrico (−∞ → 0 → +6, SPECIFICA §4): con Rp/R = 1 il kill
sarebbe −6 dB. La soluzione NON è nella rete (la simmetria è dimostrabile per
ogni cella complementare a singolo pot) ma nella **legge del pot**: rete
elettrica simmetrica ±X dB, taper meccanico custom che mappa:

    θ ∈ [0,5 → 0]  (cut):   x → 0,5 … ~1,0  (tutta la profondità, −X dB al fondo)
    θ ∈ [0,5 → 1]  (boost): x → 0,5 … x₆    (solo il tratto che serve per +6 dB)

Coerente con la filosofia già bloccata per il filtro (dec. 70: law musicale
al centro, accelerazione agli estremi) e con la sessione hardware pot (voce 40).
In elettronica: la stessa asimmetria si ottiene col pot lineare + le due metà
corsa usate in tratti diversi; il taper custom serve per il feel musicale.

## 2. Cella LOW — proof-of-concept misurato (2026-09-24)

Valori [PROVVISORIO — regola 3]: R = 1 kΩ, Rp = 31 kΩ, C = 100 nF,
op-amp macro ideale. Griglia misurata (`sim/eq-serie/low-cell.cir`):

| x (elettrica) | gesto | 20 Hz | 70 Hz | 150 Hz | 1 kHz | 10 kHz | min banda |
|---|---|---|---|---|---|---|---|
| 0,323 | boost +6 | +5,76 | +4,08 | +1,84 | −0,25 | −0,03 | −0,25 |
| 0,400 | boost medio | +3,16 | +2,19 | +0,93 | −0,14 | −0,02 | −0,14 |
| 0,500 | **DETENT** | −0,02 | −0,02 | −0,02 | −0,02 | −0,02 | −0,02 |
| 0,600 | cut lieve | −3,19 | −2,22 | −0,96 | +0,11 | −0,01 | −3,32 |
| 0,750 | cut medio | −8,55 | −6,24 | −3,09 | +0,34 | +0,00 | −8,87 |
| 0,900 | cut forte | −16,48 | −13,07 | −8,36 | +0,63 | +0,04 | −16,97 |
| 0,970 | cut profondo | −23,57 | −19,77 | −14,65 | −0,87 | +0,19 | −24,14 |
| 0,999 | KILL | −29,23 | −25,29 | −20,09 | −5,42 | +0,12 | −29,84 |

Lettura musicale (cosa si sente):
- **Kill vero**: a fine corsa il basso a 20 Hz è giù di ~30 dB — la cassa
  sparisce, non "si affloscia" come nella v0.2 (−8 dB con gobba). Nessun bump
  a nessuna posizione: il minimo in banda resta sulle basse a ogni x
  (colonna gmin ≈ g20 sempre) → la sottrazione qui è tra impedenze reali
  (partitore), non tra segnali sfasati: il difetto fatale della v0.2 è assente
  per costruzione.
- **Le medie restano vive**: con il kill inserito, 1 kHz sta a −5 dB e 10 kHz
  a 0 — il gesto dub classico (via il basso, hi-hat e voce restano) funziona.
- **Boost shelf liscio**: +5,8 dB a 20 Hz che sfuma con pendenza di shelf,
  niente buchi a 150 Hz (la v0.2 scavava −1,7 dB).
- **Detent assoluto**: −0,02 dB piatti su tutta la banda: la traccia passa
  come registrata (valore centrale della v0.2 preservato).
- Effetto cosmetico noto: cut profondi portano +0,3…+0,6 dB intorno a 1 kHz
  (interazione di fase degli zeri/poli della cella) — sotto la soglia di
  udibilità dentro il gesto del kill; la cascata a 4 bande lo riduce ancora
  (verifica in v0.3-beta).

## 3. Tracking stereo — numeri per la questione 53

`low-cell-track.cir`, mismatch tra sezioni del pot doppio (err = ±0,5/1% per lato):

| mismatch sezioni | deviazione dal nominale | L−R worst (stima ×2) | requisito ≤0,25 dB |
|---|---|---|---|
| 1 % | ≤0,08 dB (detent/boost LF) | ~0,16 dB | PASSA |
| 2 % | ≤0,17 dB (detent LF) | ~0,34 dB | al limite |

Conclusioni: pot doppi con tracking ≤1% (conduttivo-plastica di precisione,
selezione) bastano; a 2% serve trim. La zona sensibile è il detent sulle basse
(dove Za/Zb sono massime). Alternativa elettronica (VCA per banda + CV unica:
tracking perfetto by design) resta la via di fuga se la meccanica delude —
decisione dentro la voce 53, costo +4 VCA/canale.

## 4. Estensione alle altre bande (v0.3-beta, principio fissato)

- **HIGH**: duale della LOW (scambio R↔C nelle reti Za/Zb): shelf alta,
  kill −X sulle alte, identica struttura.
- **MID (250, 1k)**: celle a campana — reti Za/Zb con rami serie C-R-C
  (o twin-T) che portano Zb a un minimo reale alla frequenza centrale:
  il cut ha uno ZERO sull'asse jω → −X dB profondo e stretto al centro,
  gonne controllate; il boost è la campana duale (+6). Stessa law asimmetrica.
  Derivazione esatta e simulazione = v0.3-beta (la famiglia Baxandall "mid"
  classica copre esattamente questo caso).
- **Cascata**: 4 celle in serie, 1 sezione op-amp ciascuna = 1 quad per canale
  (vs 10 sezioni della v0.2). Quattro stadi invertenti → polarità assoluta
  preservata. Interazione tra bande adiacenti: è il carattere classico degli
  EQ in serie (le curve si sommano in dB con mutua influenza sulle gonne) —
  va mostrato a Filippo sulle curve complete (v0.3-beta).
- **All-kill (questione 59)**: il residuo non è più un leak di cancellazione
  (−0,67 dB!) ma il prodotto dei cut: nelle zone di sovrapposizione tra bande
  il residuo stimato è −15…−25 dB. Misura esatta sulla cascata in v0.3-beta;
  l'auto-mute probabilmente non serve più (il fader resta il silenzio totale).

## 5. Scelte aperte (a Filippo — regola 2)

1. **Profondità di kill — DECISA 2026-09-24 (decisione 77 [F])**: **−30 dB**
   (Rp/R ≈ 31). Il silenzio assoluto resta lavoro del fader. Reti della
   v0.3-beta dimensionate su questa profondità per tutte e 4 le bande.
2. **Taper custom**: conferma la law asimmetrica (cut: tutta la corsa;
   boost: +6 in ~metà corsa elettrica) — dettaglio feel nella sessione
   hardware (voce 40).
3. **Tracking**: pot meccanici di precisione (raccomandato, con selezione)
   vs VCA per banda (perfetto, +costo) — questione 53.
4. **EQ2 di FX send/return (questione 65)**: stessa famiglia di celle
   (2 bande, reti shelf) — conferma in v0.3-beta.

## 6. Rumore e livelli (stime, verifica in v0.3-beta)

- Rumore: 4 celle cascata, resistori ≤31 kΩ nei bracci (domina la termica
  di Za alla massima profondità): stima densità equivalente ~5-10 nV/√Hz
  per cella → integrato ben sotto il target −92 dBu (la v0.2 misurava
  −124,8 dBu con 10 op-amp: qui 4 sezioni ma resistori più grandi — la
  simulazione formale chiude il conto).
- Livelli: boost max ×2 (+6 dB) sulla banda bassa: +16 dBu in → +22 dBu out
  di cella = 13,7 Vp < 16,5 V (clamp del dominio ±18 V) — stesso margine
  della v0.2; il cut non crea headroom issues (≤1).
- Pilotaggio: il finding 2 della v0.2 (carico di sorgente) qui pesa meno
  (Zin ≥ 1 kΩ + Za ≥ ~1 kΩ in serie), ma resta la regola: pilotare da
  bassa impedenza (≤10 Ω) — il buffer/VCA di GAIN lo garantisce.

## 7. BOM di massima (coppia di canali, [PROVVISORIO])

| Voce | Qtà | Note |
|---|---|---|
| Op-amp quad low-noise (classe OPA1654) | 2 | 1 per canale (4 celle) |
| Pot doppi conduttivo-plastica, taper custom | 4 | 1 per banda (sessione voce 40) |
| R/C reti (0,1% dove il detent dipende) | ~48 | Za/Zb matched per banda |
| Stima costo | ~30-45 € | vs 70-95 € della v0.2 |

## 8. Prossimi passi (v0.3-beta2)

1. FATTO in beta-1 (§9): celle MID/HIGH, cascata 4 bande, residuo all-kill,
   rumore, tracking, livelli.
2. Headroom interno: picco 15,2 V a +16 dBu in all-boost (1,3 V dal clamp);
   a +18 dBu lo stadio MH clippa a metà catena. Soluzione candidata:
   riferimento interno −6 dB con make-up in uscita (stesso principio della
   decisione 73 per il 5-way).
3. Rumore: −114,6 dBu (PASS, 22 dB di margine) ma i summer a 100 kΩ dominano
   (122 nV/√Hz a 1 kHz): scendere a 25-49,9 kΩ in beta-2 (verificando il
   carico sul wiper del pot).
4. Scelte di Filippo: 68 (profondità kill HIGH, §9.3), 53 (tracking: pot
   precision vs VCA), taper (voce 40). Profondità kill shelf DECISA: −30 dB
   (decisione 77).
5. Integrazione in `cdj-line-channel.md` v0.3 (sostituisce §3.3, aggiorna
   §6 BOM e §4 level plan); allineamento EQ2 FX (questione 65: le celle
   shelf/campana di questa famiglia si applicano tali e quali a 2 bande).
6. Law del pot e taper custom (mappatura θ→x elettrica: boost +6 in metà
   corsa, cut −30 accelerato agli estremi — filosofia dec. 70).

## 9. Risultati v0.3-BETA-1 (2026-09-25, `sim/eq-serie/`)

### 9.1 Cella MID a campana (mid-cell.cir, 250 Hz Q 0,8) — VALIDATA

Struttura sottrattiva `G = −(1 − b·BP)`, b = 1−2θ: MFB bandpass + invertitore
di polarità + pot crossfade tra ±BP + summer 100 kΩ. Al centro BP è reale
(fase 0 dopo l'inversione): il notch è ESATTO, non una cancellazione di fase.

| θ | gesto | 125 Hz | 250 Hz | 500 Hz | 1 kHz |
|---|---|---|---|---|---|
| 0 | kill | −2,34 | **−45,5** | −2,31 | −0,48 |
| 0,5 | DETENT | −0,03 | −0,03 | −0,03 | −0,03 |
| 1 | boost | +3,45 | **+5,97** | +3,43 | +1,10 |

Kill = notch profondo e stretto (−2,3 dB a ±1 ottava): larghezza governata
dalla Q — è il comportamento documentato e accettato dei medi (stesso della
math v0.2, che per i medi era corretta). Boost +6 esatto al centro.

### 9.2 Cella HIGH — il duale serie-RC è BOCCIATO, valida la sottrattiva

Tentativo 1 (duale serie RC della cella LOW): in kill la Xc del condensatore
serie domina sull'armatura minima (4 kΩ contro 31 Ω a 20 kHz): si ferma a
−18 dB e lo scaling delle impedenze è invariante. BOCCIATO (registrato).

Tentativo 2 (VALIDATO): stessa famiglia della MID con W = HP2 (Sallen-Key
~5 kHz): `G = −(1 − b·HP2)`. Misura (high-cell.cir):

| θ | gesto | 1 kHz | 5 kHz | 10 kHz | 20 kHz | 35 kHz | max banda |
|---|---|---|---|---|---|---|---|
| 0 | kill | +0,31 | +1,66 | −2,98 | −9,14 | −14,07 | +2,05 |
| 0,5 | DETENT | −0,03 | −0,03 | −0,02 | −0,02 | −0,02 | −0,02 |
| 1 | boost | −0,38 | +1,92 | +5,26 | +5,85 | +5,95 | +5,98 |

(Correzione 2026-09-25: HP2 con Q 0,707 VERO — R_fb deve essere META di R_gnd
in SK HP; la prima versione usava il rapporto inverso, Q 0,354. Bug ereditato
da v0.2, trovato col bank 5-way.)

Boost +6 shelf monotono ✓; detent esatto ✓; **kill**: −9,1 dB a 20 kHz e
−14,1 a 35 kHz (profondo in cima alla banda), ma bump +2,1 dB al corner
(5 kHz): la fase residua di HP2 impedisce l'azzeramento vicino al corner.
→ questione 68.

### 9.3 Cascata 4 bande (cascade-b2.cir, 10 modi — griglia aggiornata al fix Q HP2; cascade.cir = versione beta-1, valori corretti, run di riferimento = b2) — VALIDATA con due finding

| modo | 20 | 70 | 150 | 250 | 500 | 1k | 2,5k | 5k | 10k | 20k | 35k |
|---|---|---|---|---|---|---|---|---|---|---|---|
| detent | −0,09 | −0,10 | −0,10 | −0,10 | −0,10 | −0,10 | −0,10 | −0,10 | −0,09 | −0,09 | −0,09 |
| LOW kill | **−29,3** | −25,4 | −20,2 | −16,1 | −10,5 | −5,5 | −1,4 | −0,3 | 0,0 | +0,1 | +0,1 |
| LM kill | −0,1 | −0,7 | −3,9 | **−45,5** | −2,4 | −0,6 | −0,2 | −0,1 | −0,1 | −0,1 | −0,1 |
| MH kill | −0,1 | −0,1 | −0,2 | −0,5 | −2,0 | **−44,7** | −1,2 | −0,3 | −0,2 | −0,1 | −0,1 |
| HIGH kill | −0,1 | −0,1 | −0,1 | −0,1 | −0,1 | +0,2 | +1,4 | +1,6 | −3,1 | −9,2 | −14,2 |
| **ALL-KILL** | **−29,4** | −26,0 | −24,1 | **−61,8** | −14,6 | **−50,3** | −1,0 | **+1,1** | −3,0 | −9,0 | −14,0 |
| all-boost | +5,8 | +5,5 | +6,5 | +7,5 | +6,3 | +6,4 | +0,6 | +2,5 | +5,3 | +5,8 | +5,9 |
| dub | +5,6 | +3,4 | −2,2 | −45,2 | −4,5 | −45,8 | −2,9 | +1,5 | +5,1 | +5,7 | +5,9 |

- **Detent**: piatto ±0,02 dB relativo su tutta la banda; offset costante
  −0,10 dB (guadagno d'anello finito dei summer) → trim di make-up, o
  riferimento interno −6 dB (punto 2 di §8).
- **LOW kill**: −29 dB a 20 Hz con gonna larga (−16 a 250, −5,5 a 1 kHz):
  il gesto dub principale è pieno e musicale.
- **Curva dub** (LOW+HIGH su, medi giù): +5,6 sotto, −45 ai due centri medi,
  +5,5 in cima: esattamente l'estetica richiesta.
- **FINDING all-kill (→ questione 59, numeri definitivi)**: profondo ai
  centri banda (−29/−62/−50) ma **resta aperto intorno a 5 kHz (+1,1 dB, gmax +1,2)**:
  la zona 2,5-10 kHz è tra le gonne dei notch medi e il kill HIGH debole.
  All-kill NON è silenzio: il fader (o l'auto-mute, opzione 59b) è necessario
  per il silenzio vero. Coerente con la filosofia "kill = gesto, fader = muto".
- **FINDING HIGH kill (→ questione 68)**: bump +2,1 dB al corner (5 kHz), −9…−14 dB
a 20-35 kHz: nella zona 5-10 kHz "scurisce" invece di "togliere".

### 9.4 Rumore, tracking, livelli

- **Rumore** (cascade-noise.cir, detent, 20-20k): 1,45 µV = **−114,6 dBu**
  (target ≤ −92 A-wtd: PASS, 22 dB margine). Densità 1 kHz: 122 nV/√Hz
  (dominano i 100 kΩ dei summer: −8 dB possibili scendendo a 25-49,9 kΩ).
- **Tracking** (cascade-track.cir, mismatch sezioni ±err/2): detent con
  err=1% → deviazione ≤0,08 dB (L−R ≤0,16: PASS ≤0,25); err=2% → 0,16 dB
  (L−R ~0,32: limite, serve trim). All-kill: insensibile (≤0,01 dB).
  Conferma in cascata dei numeri alpha → questione 53.
- **Livelli** (cascade-level.cir, 1 kHz +16 dBu, all-boost): uscita ±14,7 V
  pulita; picco interno 15,2 V (stadio MH, +6,3 dB su segnale già caldo):
  1,3 V dal clamp. Estremo +18 dBu: il MH clippa a metà catena (19 V teorici)
  → riferimento interno −6 dB raccomandato in beta-2 (principio dec. 73).

### 9.5 Silicon e BOM (aggiornamento §7)

Per canale: 1 (LOW) + 3 (LM) + 3 (MH) + 3 (HIGH) + 2 (buffer in/make-up,
§9.6) = **12 sezioni op-amp** (3 quad per canale, 6 per coppia). Pot: 4 doppi
per coppia (1 per banda, taper custom §10). La cella HIGH in variante
crossfade-LP2 (questione 68, se scelta) aggiunge 2-3 sezioni per canale.

### 9.6 Beta-2: riferimento interno −6 dB + summer 49,9k (cascade-b2*.cir)

Cambiamenti: buffer d'ingresso gain −0,5 e make-up d'uscita gain −2 (due
inversioni: polarità assoluta ancora preservata, 6 inversioni totali); summer
delle celle sottrattive 100k → 49,9k (Thevenin del pot ≤2,5k → errore di law
≤5%, da trimmare nel taper). Principio: stesso riferimento interno −6 dB del
5-way (decisione 73).

Risultati:
- **Livelli RISOLTI**: picco interno massimo 7,60 V (era 15,23) a +16 dBu
  all-boost; estremo +18 dBu: interni 9,54 V (nessun clipping a metà catena),
  l'uscita clippa a ±16,5 V (saturazione intenzionale, coerente col sheet §2).
- **Curve invariate**: griglia identica alla beta-1 entro 0,03 dB.
- **Detent**: offset costante −0,12 dB (guadagni d'anello finiti + make-up
  2,004): si azzera col trim del make-up (Rf 100k → multi-giro o coppia
  matched) — piattezza relativa ±0,02 dB confermata.
- **Rumore**: −110,7 dBu integrato (era −114,6): le DUE sezioni op-amp in più
  (buffer/make-up) pesano nel macromodello uniforme a ~6 nV/√Hz. Nel design
  reale buffer e make-up sono OPA1612 (1,1 nV/√Hz): il contributo extra crolla.
  Margine sul target −92 dBu: 18,7 dB → PASS anche così. Densità @1 kHz:
  189 nV/√Hz (beta-3: ricalcolare con modelli reali).
- All-kill, kill per banda, boost: immutati (finding 59/68 validi).

## 10. Law del pot e taper (specifica per voce 40 e per il prototipo M4L)

Rotazione θ (0→1, detent meccanico a θ=0,5 con click) → posizione elettrica:

**Celle shelf (LOW, HIGH)** — asimmetrica (la rete è ±30 dB simmetrica,
la law no; filosofia decisione 70: musicale al centro, rapida agli estremi):
- θ ∈ [0,50 → 1,00] (boost): x lineare 0,500 → 0,323 = 0 → +6,0 dB.
  Corsa ampia, ~12 dB per metà giro: regolazione fine.
- θ ∈ [0,05 → 0,50] (cut): x 0,970 → 0,500 = −27 → 0 dB: il 90% della
  mezza corsa copre quasi tutto il cut (~0,6 dB per % di rotazione).
- θ ∈ [0 → 0,05] (fine corsa): x 0,999 → 0,970 = −30 → −27 dB: il kill
  completo negli ultimi 5% — lo "scatto" finale del gesto dub.
- Fine corsa meccanico CCW = −30 dB (non −∞: il silenzio è il fader).

**Celle campana (LM, MH)** — simmetrica:
- b = 1−2θ lineare (θ=0 kill/notch, θ=0,5 detent, θ=1 boost +6).
- La profondità del notch satura in fretta (θ<0,1 → già −15 dB al centro):
  se all'ascolto (M4L, quando riparte) risulta brusca, introdurre legge a
  tratti come per le shelf. [PROVVISORIO in attesa di ascolto]

**Realizzazione**: taper custom su pot conduttivo-plastica doppio (sessione
hardware voce 40: marca/modello/albero/click centrale). Tabella θ→x qui sopra
= specifica di produzione della pista. Nel prototipo M4L la law si applica
in software (mapping del knob) e si valida a orecchio PRIMA di ordinare i pot.

**Tracking stereo**: sezioni dello stesso pot doppio; requisito ≤1% (misura
§9.4: 1% → L−R ≤0,16 dB PASS, 2% → 0,32 dB limite). Selezione/trim se la
produzione delude; alternativa VCA (questione 53) resta documentata.
