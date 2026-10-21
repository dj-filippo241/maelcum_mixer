# Sistema metering — barre LED a zone (S4, voce q19)

v0.1 — 2026-10-01. Basi bloccate: SPECIFICA §11 (posizioni, colori, master
20 segmenti/canale), decisione 81 (ballistica Pioneer DJM: attacco rapido,
release ~0,3 s banco 0,2-0,5, latch clip 442 ms), decisione 90(a) (barre a
zone, soglie green ≤+6 / amber…+18 / red +18…+24 / purple latch ≥+23 dBu,
driver LM3915-class [PROVVISORIO]). master-out §3.6: RESTA VALIDO per
catena/purple-diamond/q54; SUPERATO nelle soglie (FS +18 → +24 assoluti,
dec. 90) e nella scala (−42…+18 → +24…−33). Detector di riferimento:
`sim/meter/RISULTATI-peak-det.md` (superdiodo + clamp anti-windup + hold
100 nF VALIDATO); simulazioni di questa versione: `sim/system/meter-*.cir`.

## 1. Zone e punti di presa (SPEC §11 [BLOCCATO])

Scala ASSOLUTA unica: fondo scala (FS) = **+24 dBu** su ogni zona =
saturazione reale del dominio ±18 V; calibrazione identica tra canali
(q54) ottenuta BY CONSTRUCTION (albero riferimenti condiviso §5).

| Zona | Tap (locked) | Nominale / max | Guadagno d'ingresso al detector |
|---|---|---|---|
| MASTER L/R | post-level VCA, pre-stadio HV | 0 / +24 dBu | g = 0,288 (FS→5,00 V hold) |
| DJ ×4 | post-filter/overdrive, pre-fader (§3.7 cdj) | 0 / +20 (drive inserito) | g = 0,288 (identici tra canali) |
| 5-way | post-drive, pre-master-sum (rif. interno −6 dB) | −6 / +10 | g = 0,576 (×2 = dominio assoluto post-makeup) |
| FX return ×4, uno per ritorno (dec. 116; era ×1), mono centrato | post-gain/EQ2, pre-fader | 0 / +23 (regola K) | g = 0,288 |
| mic / mono | WARNING-ONLY, nodo PRE (dopo il preamp, prima dell'EQ2) | 0 / +17 | **UN LED a tre colori (dec. 97)**: verde = segnale ok (≥ −6 dBu), giallo = vicino al clip (≥ +11), rosso = clip (≥ +17, latch) — soglie [PROVVISORIO]; rosso a +17 e non +23 perché il front-end mic su ±15 V clippa prima e l'EQ2 aggiunge fino a +6 (`docs/fase4/mic-mono-moduli.md` §5.2) |

Niente meter per booth/rec/cuffie/send (SPEC §11). Barre totali: master 2 +
DJ 4 + FX 4 + 5-way 1 = **11 barre** + warning mic/generic (REV dec. 116,
2026-10-21: era FX 1 = 8 barre).

**REV dec. 116 (2026-10-21)**: un meter da 10 segmenti per ogni ritorno FX.
Segmenti ~103 → ~133; LM3915 10 → 13; detector 8 → 11 canali (+3 × 3
sezioni = ~2 quad op-amp in più sul LN, +10-20 mA); comparatori purple
+3 (LM339 2 → 3). Corrente LED: worst case 133 × 5 mA ≈ 0,67 A (era
0,5): il +5 V sale a ~1,15 A di picco contro 1,25 A di dimensionamento
(margine 9 %). Con LED alta efficienza a 2 mA: ~0,27 A, nessun problema.
Raccomandazione: I_LED 2 mA (Rprog), da confermare a banco con la
leggibilità al sole (ambiente all'aperto, dec. 111 e).

## 2. Catena per zona (detector ri-tarato dec. 81)

```
tap → [g-in + trim calibrazione ±2%] buffer (OPA1612-class, ±15 V LN)
    → superdiodo OPDET + 1N4148 (clamp anti-windup −1,5 V; Rcomp 1k +
      Ccomp 47p — rete validata peak-det-hfclip)
    → C hold 100 nF (niente altro sul nodo: lezione sim/meter)
    → R release 2M fisso + 3,3M trimmer = τ 0,2…0,53 s (dec. 81: banco)
    → buffer out → { LM3915 ladder §3 ; comparator purple §4 }
```

Misure (`meter-det-03s.cir`, τ = 0,3 s, scala FS 5 V): attacco 99% =
**0,23 ms** (SPEC "attacco <1 ms" ✓); hold al picco **5,0001 V** = +24,00 dBu
(errore +0,001 dB sul segnale scalato); droop 10 Hz = **−2,901 dB/ciclo**
(identico al dato validato dec. 81: a 0,3 s la pulsazione è informazione
musicale, non difetto). Limite noto del macromodello: dinamica di cattura
HF (35 kHz) non simulabile → banco (già documentato in peak-det §2).

## 3. Driver LM3915 — segmenti e colori

LM3915 = 10 segmenti log 3 dB/step, modo bar. Cascata 2 chip/canale
(Vrefhi_B = Vrefhi_A·10^−1,5) = **20 segmenti, +24…−33 dBu** per il MASTER
(SPEC §11 [BLOCCATO]). Zone: **10 segmenti, +24…−3 dBu** (1 chip)
[PROVVISORIO — il blue profondo (<−6) sulle zone resta spento: sotto −3 dBu
la barra è buia; se il pannello vuole zone a 20 segmenti = 2° chip per zona,
scelta layout → voce 40].

Mappatura colori (6 zone semantiche SPEC §11 [BLOCCATO] con gli ancoraggi
numerici dec. 90; soglie [PROVVISORIE] da validare a banco, §11:140):

| Colore | Banda assoluta | Segmenti master (20) | Zone (10) |
|---|---|---|---|
| BLUE | < −6 dBu (poco) | −9…−33 (9 segmenti) | nessun blue: sotto −3 dBu la barra è spenta (scelta densità → voce 40) |
| GREEN | −6…+6 (safe: programma attorno a 0) | −6…+6 (5) | −3,0,+3,+6 (4) |
| YELLOW | +6…+12 (loud) | +9,+12 (2) | +9,+12 (2) |
| AMBER | +12…+18 (hard) | +15,+18 (2) | +15,+18 (2) |
| RED | +18…+24 (extreme) | +21,+24 (2) | +21,+24 (2) |
| PURPLE | latch clip (§4) | LED dedicato | LED dedicato |

Nota dec. 90: la sua "ambra +6…+18" = yellow+amber di questa tabella (la
semantica 6 colori SPEC è [BLOCCATO-F]: lo split yellow/amber a +12 è la
proposta [PROVVISORIA]; i confini dec. 90 — verde fino a +6, rosso da +18,
purple da +23 — sono rispettati esattamente).

Verifica soglie (`meter-thresholds.cir`, macromodello comportamentale da
equazioni datasheet: segmento k acceso ⇔ Vin ≥ Vrefhi·10^(−3k/20)): le
20 soglie cadono a −3,000 dB di passo con errore ≤0,005 dB (risoluzione
sweep); vrefA 4,99999857 V, vrefB 1,58114 V. L'accuratezza reale è quella
del chip (±0,5-1 dB/segmento, §3.6) → calibrazione a banco con tone a
livelli noti (procedura q54).

**FINDING di design (dalla sim)**: il partitore di riferimento NUDO si
carica (Rt3/Rt4 del secondo stadio): vrefA scende a 4,07 V invece di 5,00.
Nel design ogni nodo dell'albero riferimenti ha il suo follower (OP1612,
±15 LN) — §5.

## 4. Purple — clip latch

- **Zone (±18 V)**: comparator (LM339) sull'hold a **4,4528 V = +23 dBu**
  assoluti (dec. 90) + one-shot RC 7M/100n (τ 0,7 s) validato in
  peak-det-latch. Misura (`meter-latch-purple.cir`): burst +24 dBu →
  flag **479 ms** sopra 2,5 V (finestra SPEC 300-500 ✓); la durata varia
  440-480 ms secondo l'overshoot (hold attraversa la soglia prima con
  τ 0,3 s: il dato storico 442 ms era a τ 3 s). Retrigger: dimostrato
  nel test storico (meccanismo invariato).
- **MASTER**: purple = sensing del diamond d'uscita (rail−2 V ≈ ±22 V,
  §3.6 master-out [BLOCCATO]: scatta solo quando lo stadio HV arriva
  davvero al limite) + stesso one-shot. [Punto per voce 40: tenere il
  doppio criterio master (HV sensing) o uniformare a +23 dBu.]

## 5. Albero riferimenti condiviso (calibrazione identica by construction)

+15 V LN → partitore 10k/5k 0,1% → **follower** → vrefA 5,000 V (FS +24
dBu, 8 barre) → partitore 10k/4,625k 0,1% → **follower** → vrefB 1,581 V
(cascate master). R 0,1% → errore ratio ≤0,14% = ±0,012 dB ≪ budget.
Trim di calibrazione per zona = trimmer ±2% sul guadagno d'ingresso (§2),
NON sui riferimenti (l'albero è unico: le zone restano allineate tra loro).
Corrente: LM3915 V+ = **+5 V control** (LED isolati dal rail LN — il
rumore dei LED non tocca l'analogico); I_LED 2-5 mA per chip (Rprog);
budget worst-case ~103 segmenti × 5 mA ≈ **0,5 A su +5 V** → dichiarato
a S1/PSU (con LED alta efficienza 2 mA bastano: 0,2 A). Detector +
riferimenti su ±15 V LN (LT3045/94, dec. 54): ~8 canali × 3 sezioni +
2 buffer ref ≈ 6 quad op-amp, Iq ≈ 40-80 mA.

## 6. BOM di massima [molto PROVVISORIA — regola 3]

| Voce | Qtà | Note |
|---|---|---|
| LM3915 (o clone/alternativa §7) | 13 | master 4 (2×2 cascata) + zone 9 (REV dec. 116: +3 ritorni FX) |
| OPA1612-class dual | ~12 (o 6 quad) | detector 3 sez./canale × 8 + ref tree |
| LM339 quad comparator | 3 (REV dec. 116) | purple zone ×6 + warning mic/generic |
| LED alta efficienza | ~133 segmenti + 11 purple + warning (REV dec. 116) | colori per §3; voce 40 |
| 1N4148, R 0,1%/1%, C hold 100n C0G/PP, trimmer | — | detector/latch |

Stima: ~50-80 € totali. Reperibilità LM3915 → task dedicato (voce 9).

## 7. Alternativa se LM3915 irreperibile

Ladder di comparator discreti: LM339 ×3 per barra (10 soglie) + riferimenti
da LM4040/divisori buffered — funziona, ma ~10× i chip per barra e la
taratura diventa critica (20 riferimenti/barra). Raccomandazione: LM3915
primario, alternativa solo se la ricerca reperibilità fallisce.

## 8. Simulazioni eseguite (2026-10-01)

| Netlist | Esito |
|---|---|
| `sim/system/meter-det-03s.cir` | attacco 0,23 ms ✓; hold 5,0001 V (+24,00 dBu) ✓; droop −2,901 dB/ciclo 10 Hz ✓ (dec. 81) |
| `sim/system/meter-thresholds.cir` | 20 soglie a −3,000 dB ±0,005; albero buffered ✓; FINDING partitore nudo carico (4,07 V) → follower obbligatori |
| `sim/system/meter-latch-purple.cir` | flag 479 ms in finestra SPEC 300-500 ✓; soglia +23 dBu assoluti ✓ |

Metodo: tran/.dc (nessun INTEG — §8.9 n.a. qui); macro OPDET/OP1612 da
`sim/lib/opamp-audio.inc` (clamp anti-windup −1,5 V).

## 9. Aperti (voce 40 / q54, non bloccano l'ingegneria)

1. Pannello: posizione delle 8 barre + warning, densità (zone 10 vs 20
   segmenti), luminosità (I_LED 2 vs 5 mA), colore fisico dei segmenti.
2. Purple master: doppio criterio (HV sensing §3.6 + +23 dBu) o uno solo.
3. Procedura di calibrazione q54 (tone a livelli noti, ordine zone).
4. Interfaccia S1: +5 V ≥1 A (0,5 worst LED), ±15 LN +~100 mA metering,
   mute/sequencing (i meter seguono il mute? proposta: sì, LED spenti in
   mute).
