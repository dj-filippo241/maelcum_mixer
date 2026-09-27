# FASE 2 — Modulo 5-WAY (dub preamp): design v0.2-WIP (2026-09-27)

> **v0.2-WIP (2026-09-27)**: kill bank ALLINEATA IN FASE — soluzione esatta
> dimostrata (math + LTspice): somma piatta −0,0002…−0,008 dB su 5 Hz–60 kHz
> senza kill, all-kill = silenzio assoluto invariato (§3.1, §8.2). Il finding
> v0.1 (buchi −3…−5 dB) è chiuso. Restano per la v0.2 completa: celle
> parametriche complete, converter position, gate ramp, rumore (§10).
>
> **v0.1 (2026-09-25)**: primo design del 5-way performance EQ/dub preamp.
> Copre architettura, matematica del filter bank (questione 8: proposta LR4
> SIMULATA), topologia dell'EQ creativo (questione 9: architettura, law di
> position da decidere), interfaccia drive (questione 10: in attesa referenze
> di Filippo, questione 61). NON congela valori (regola 3). Fase 2: dettaglio
> circuitale completo dopo che la fase 1 ha insegnato (regola 5) — questo
> documento è architettura + funzioni di trasferimento + fattibilità.
> Fonti: SPECIFICA §6, decisioni 24/65/66/73, questioni 61 (referenze drive) e 67 (frequenze), status doc §14-18
> (`docs/export-chatgpt/documento-senza-titolo.txt`), gain-staging sheet.

## 1. Requisiti (BLOCCATO salvo dove indicato)

- Posizione: DJ BUS → 5-WAY → MASTER SUM; FX/mic/generic la bypassano.
- NON è il crossover acustico: quello lo fa il DSP esterno; il 5-way è uno
  STRUMENTO performance ispirato ai preamp dub/soundsystem.
- Riferimento interno −6 dB (pad in / makeup out, decisione 73).
- KILL: 5 sezioni = 5 vie (SUB ~10-90, KICK ~90-350, MID ~350-1,2k,
  HIGH ~1,2-3,5k, SUPER ~3,5-20k [PROVVISORIO dec. 66 — conferma a orecchio
  = questione 67]); 24 dB/ott; overlap deliberato senza buchi; banca
  complementare (somma piatta); kill PRIMA dell'EQ creativo (il boost non
  ripristina materiale killato); kill switch per via (altoparlanti fisici).
- EQ CREATIVO: gain/position/width per banda; gain −∞/0/+15 (EQ1-3), +12
  (EQ4), +9 (EQ5); position: 20-120 / 80-400 / 250-1,5k / 800-5k / 3-20 kHz
  [PROVVISORIO]; width: narrow ~Q3 / medium ~Q1 / broad ~Q0,5; position
  sposta il centro senza stravolgere gain/Q. Casi d'uso (corpus §17):
  broad+gain modesto = tonal shaping; narrow+gain alto = dub hit preciso;
  broad+gain alto = colorazione aggressiva.
- DRIVE: dopo la somma EQ, prima del meter; full CCW = 0 dB pulito, solo gain
  positivo; ~50% = +7 dB pulito; >50% saturazione progressiva che interagisce
  con gain di banda e overdrive filtro; JFET prima / BJT asimmetrico poi.
  Riferimenti operativi (corpus §18): normale −6…0 dBu, hot +10, estremo +18,
  clean headroom ≥+24 dove pratico (sheet: qui il dominio ±18 dà +23, ok).
- METER: dopo drive, prima del master sum (ballistica anche a 10 Hz, dec. 65).
- Controlli: fader = slider, resto = pot (principio bloccato); layout per via
  slider vs rotativi = questione 24 (aperta, pannello = design di Filippo).

## 2. Architettura

```
DJ BUS L/R (0 dBu nom, +16 worst)
  │
  ▼ PAD −6 dB (dec. 73) → buffer
  │
  ▼ KILL BANK (per lato): LR4 5 vie, gate VCA per via + kill switch
  │   SUB ──[gate K1]──┐
  │   KICK ─[gate K2]──┤
  │   MID ──[gate K3]──┤   (banca complementare: somma piatta §3)
  │   HIGH ─[gate K4]──┤
  │   SUPER─[gate K5]──┘
  ▼ EQ CREATIVO: 5 celle parametriche SVF in serie (gain/position/width §4)
  │   (le 5 bande EQ NON sono le 5 vie: ogni cella spazza il suo range)
  ▼ SOMMA → DRIVE JFET (law dec. 24, §5) → METER pickup (§5) →
  ▼ MAKE-UP +6 dB + trim → MASTER SUM (backplane)
```

Ordine bloccato: kill bank → EQ creativo → drive → meter ("killed material
cannot be restored" — corpus §16; "boost non ripristina materiale killato"
— SPECIFICA §6).

## 3. Kill bank — matematica complementare (questione 8: RISPOSTA v0.2)

**Scelta [PROVVISORIA — frequenze = questione 67]**: crossover Linkwitz-Riley
4° ordine ai 4 punti (90/350/1,2k/3,5 kHz): ogni edge = due Butterworth 2°
ordine (Q 0,707) in cascata. Proprietà che risponde ai requisiti:
- 24 dB/ott ✓ (4 poli per edge);
- "overlap deliberato senza buchi" = la sovrapposizione −6 dB delle LR ✓;
- bande: SUB = LP4(90) (passa fino a DC/10 Hz: nessun accoppiamento AC,
  requisito infrasub dec. 65 ✓); KICK = HP4(90)·LP4(350); MID = HP4(350)·
  LP4(1,2k); HIGH = HP4(1,2k)·LP4(3,5k); SUPER = HP4(3,5k);
- **somma in tensione PIATTA**: la proprietà LR a 2 vie NON basta a 5 vie —
  il finding v0.1 (§8.1) ha misurato buchi −3…−5 dB dalla fase non allineata.
  La v0.2 risolve con la banca allineata in fase (§3.1): |Σ| = 1 ESATTA,
  validata in simulazione (§8.2). La somma esce invertita (fase comune):
  il make-up ripristina la polarità assoluta (dec. 73, §2).

### 3.1 v0.2 — Banca allineata in fase (somma piatta esatta)

Identità LR4: `LP4(f) + HP4(f) = A2(f)` — allpass del 2° ordine a Q 0,707
(modulo 1 esatto, fase 0→−360°). La somma telescopica a 5 vie è esatta se
ogni banda arriva al summer con la stessa fase di riferimento = prodotto dei
4 allpass: ogni banda passa gli A2 dei crossover SOPRA la sua banda passante.

| Banda | Percorso | Allpass di compensazione | Polarità netta |
|---|---|---|---|
| SUB | LP4(90) dall'ingresso | A2(350) · A2(1,2k) · A2(3,5k) | − (3 sezioni) |
| KICK | HP4(90) → LP4(350) | A2(1,2k) · A2(3,5k) | + |
| MID | HP4(90) → HP4(350) → LP4(1,2k) | A2(3,5k) | − |
| HIGH | … → HP4(1,2k) → LP4(3,5k) | — | + |
| SUPER | … → HP4(3,5k) (fine spina) | — | + |

Somma = A2(90)·A2(350)·A2(1,2k)·A2(3,5k) → modulo 1 a ogni frequenza
(dimostrato: `sim/five-way/align_math.py`, errore 1,1e-15; validato in
LTspice: §8.2). Struttura a **spina HP condivisa**: il segnale attraversa
una cascata HP4(90) → HP4(350) → HP4(1,2k) → HP4(3,5k); ogni banda è una
presa sulla spina seguita dal suo LP4. Le HP4 non sono duplicate per banda:
la spina costa quanto la banca v0.1 (16 sezioni SK per lato).

Sezione allpass AP2 (2 op-amp): MFB bandpass invertente Q 0,707 + summer
−(1×Vin + 2×Vbp) = −A2(s) esatto. Vincoli: C1 = 2C (n1→n−), C2 = C (n1→out),
R1 = 1/(√2·ω0·C) (in→n1), R2 = 2·R1 (n1→gnd), Rf = 1,5·R1 (n−→out); summer
con Rf/Ra = 1 e Rf/Rb = 2 (coppie 0,1%). Il segno − di ogni sezione sparisce
nella polarità comune di banca (make-up, dec. 73); le bande con numero
DISPARI di allpass (SUB, MID) escono invertite: il gate corregge il segno.
MFB è appropriato qui (350 Hz–3,5 kHz, Q fisso): lo scarto v0.1 dell'MFB
riguardava gli edge LP sotto 100 Hz (rumore gain/2), non i BP.

Conteggio silicon per lato: 16 sezioni SK (spina 8 + LP 8) + 6 AP2 × 2
op-amp = 28 sezioni ≈ 7 quad/lato → **14 quad/modulo** per la banca (era 8
in v0.1). Variante "lite" (3 AP2/lato — 1 allpass per banda, il più vicino):
worst −0,125 dB invece di −0,008 dB, risparmio 3 quad/modulo [APERTO — se il
costo conta; raccomandazione ingegneria: banca completa, è il cuore del
modulo e 0,125 dB è già al limite del requisito ±0,1 dB].

Topologia per edge: Sallen-Key biquad unity-gain (1 op-amp per sezione 2
poli; R da formula con C fissi per decade, 1% + trimmer di allineamento a
banco: la piattezza vive sul matching degli 8 edge e delle 6 sezioni AP2).
Se un trimmer sposta un edge di ±10% senza muovere l'allpass corrispondente,
l'errore di somma resta ≈0,02 dB (calcolo in §8.2): i trim NON devono essere
accoppiati meccanicamente.

**Group delay della somma (dato nuovo v0.2)**: la somma allineata è un
allpass dell'8° ordine: τ ≈ 6,9 ms @10 Hz, picco 7,9 ms @58 Hz, 2,2 ms @350,
0,66 ms @1,2k, 0,19 ms @3,5k, 0,02 ms @10 kHz. Non è un costo nuovo
dell'allineamento: la banca v0.1 (non allineata) aveva già τ ≈ 7,3 ms di
picco — è il prezzo dei 24 dB/ott. La differenza v0.1→v0.2 è +0,6 ms al
picco. In ascolto: l'energia sotto ~100 Hz arriva ~7 ms dopo il medio-alto,
dentro la finestra di fusione (~20 ms) — comportamento normale di un
crossover ripido; il DSP acustico a valle fa il suo allineamento. Comunque
dato da confermare a orecchio (questione 67, ascolto M4L).

**Gate di kill**: 1 VCA per via per lato (THAT 2181, famiglia unica — voce 37):
5×2 = 10 sezioni = 5 dual. Kill switch fisico (5, uno per via di altoparlanti)
+ slider/mute: il gate chiude con ramp ~1 ms (famiglia voce 55, no click).
Kill = g→0: **silenzio VERO della via** (gate, non sottrazione: qui nessuna
cancellazione di fase — il kill del 5-way è assoluto by design, a differenza
dell'EQ di canale che è scultoreo; le due cose si completano: via killata =
l'altoparlante tace; EQ creativo = gesto sul materiale vivo).

**Verifica simulata** (`sim/five-way/bank-lr4.cir`, gate ideali): [RISULTATI §8]

## 4. EQ creativo — 5 celle parametriche (questione 9: architettura)

Ogni banda = cella parametrica a SVF, riuso dei due building block già
dimostrati nel progetto:
- **Core**: la cella a campana sottrattiva dell'EQ serie v0.3
  (`G = −(1 − b·BP)`, notch esatto al centro, detent piatto per costruzione,
  boost = 1+b) con BP da SVF OTA;
- **Position**: ω0 dello SVF via gm = 19,2·Iabc — stessa tecnica del modulo
  filtro; range per banda ~2,3-2,7 ottave.
- **Width**: Q della cella via damping nel summer: switch 3 posizioni
  (narrow Q3 / medium Q1 / broad Q0,5) su 3 resistori matched 0,1% —
  ripetibile, senza pot che interagiscono (SPEC chiede 3 comportamenti
  discreti, non continui).
- **Gain**: b dal pot con law dB (−∞/0/+max): b = +1 → notch (il −∞ del
  requirement = notch profondo al centro, larghezza da Q — la rimozione
  TOTALE di una regione è lavoro della kill bank a monte, coerente con la
  filosofia a due stadi); b negativo → boost: +15 dB → b = −4,62
  (1+|b| = 5,62); +12 → b = −3,0; +9 → b = −1,82. Summer con rapporto
  Rf/Rb fino a 4,62 [PROVVISORIO].
- **Position senza stravolgere gain/Q**: proprietà naturale dello SVF
  (ω0 = gm/C indipendente dal damping) ✓ requisito esplicito del corpus.

Converter di position: due opzioni [APERTO — ascolto M4L, come questione 67]:
- (A) Iabc LINEARE nel pot: semplice (1 generatore V-I per banda), ma la
  frequenza risulta lineare nella corsa (bassi compressi a inizio corsa);
- (B) converter esponenziale (tecnologia del modulo filtro, mirror inclusi):
  law a ottave uniforme — feel coerente coi knob del filtro. Raccomandazione:
  (B), costo ~5 converter + mirror.

Silicon per banda per lato: 1 LM13700 (2 OTA integratori) + 2-3 sezioni
op-amp (summer + inverter ±BP). Totale modulo (v0.2: banca allineata = 14
quad): **~24-26 quad** (banca 14, EQ ~10, gate/buffer/make-up)
**+ 10 LM13700 + 5 THAT 2181** [PROVVISORIO, BOM §7].

## 5. Drive e meter (questione 10 — v0.1 = interfaccia, design dopo referenze 61)

- **Struttura in due stadi** che realizza la law bloccata senza compressione:
  stadio 1 = gain pulito variabile 0…+7 dB (CCW→50%, law dB lineare via
  CV); stadio 2 = saturatore morbido a soglia fissa (JFET soft-sat, poi
  BJT asimmetrico — corpus §18): oltre il 50% il segnale entra progressivamente
  nella saturazione. L'"interazione con gain di banda e overdrive filtro"
  è automatica: le bande spinte e il filtro saturo arrivano già caldi qui.
  Carattere = sound design: **aspetta le referenze di Filippo (questione 61)**;
  v0.2 con modelli JFET reali + spettro armonico per candidato.
- Interfaccia elettrica: dominio ±18 V; ingresso tollera +18 dBu clean
  (stadio 1 a JFET, headroom); uscita recovery low-Z 20-50 Ω, clean +23 dBu
  (sheet: il +24 vero vive solo al master); nessun makeup compression (SPEC).
- **Meter**: pickup post-drive; detector condiviso col design di canale
  (CDJ §7.3, simulazione peak detector in coda lì): ballistica a 10 Hz
  (dec. 65: no sagging), clip latch 300-500 ms, segmenti = design modulo
  metering (questione 19/54).

## 6. Headroom e livelli (sheet §2, dec. 73)

- Pad −6 dB in ingresso: nominale interno −6 dBu; worst programma +16 dBu
  → interno +10 dBu.
- Boost creativo massimo +15 dB su una banda: worst teorico +25 dBu interni
  = oltre il dominio (+23): **saturazione intenzionale del drive/stadi** —
  coerente con la filosofia "estremo = colore voluto" (voce 31, quest 61):
  il 5-way spinto È il suono dub, non un guasto. Con programma reale
  (crest ≥10 dB) non accade quasi mai.
- Regola K4 adattata: level_in × gain_creativo ≤ +23 dBu per uso clean;
  oltre = territorio drive.

## 7. BOM di massima v0.1 [molto PROVVISORIA — regola 3]

| Voce | Qtà | Note |
|---|---|---|
| Quad op-amp low-noise (classe OPA1654/1612) | ~24-26 | banca 14 (v0.2 allineata in fase: 16 SK + 12 allpass), EQ ~10, buffer/make-up |
| LM13700 (dual OTA) | 10 | celle parametriche (position gm) |
| THAT 2181 (dual VCA) | 5 | gate di kill (10 sezioni) |
| THAT 2181 o JFETmatched | 1-2 | gain drive (stadio 1) |
| JFET saturazione (coppia matched) | 2-4 | stadio 2 drive (post-61) |
| Converter expo position + mirror | 5 sezioni | opzione (B) §4 |
| R 0,1% / C0G-PP / trimmer allineamento | — | banca: 8 edge + 6 sezioni allpass per lato |
| Stima costo | ~200-280 € | il modulo più siliconato del mixer |

## 8. Simulazioni (`sim/five-way/`)

### 8.1 Bank LR4 + gate di kill (`sim/five-way/bank-lr4.cir`, 7 casi × 12 freq)

**Funzione KILL: VALIDATA.** Ogni via killata scende nella sua banda con le
code LR4 (KILL SUB: −76 dB @10 Hz; KILL KICK: −24 dB @200; KILL MID: −21
@700; KILL HIGH: −15 @2,5k; KILL SUPER: −51 @15k, −68 @25k) e le altre vie
restano intatte; ALL-KILL = −inf (silenzio assoluto by design: il gate VCA
non ha i limiti di fase delle celle sottrattive — a differenza dell'EQ di
canale, qui il kill È muto).

**FINDING — la somma piatta richiede allineamento di fase (questione 8,
parzialmente aperta).** Due bug trovati e corretti durante la verifica
(diagnostica di debug: `sim/five-way/bank-debug.cir`, run STORICO con la Q
pre-fix — il run di riferimento è `bank-lr4.cir`):
1. SK HP con R invertiti → Q 0,354 invece di 0,707 (1/Q = ω0·R_fb·(C1+C2):
   R_fb deve essere META di R_gnd per Q 0,707). Bug ereditato da v0.2 —
   corretta anche la cella HIGH di eq-serie (numeri aggiornati là).
2. La somma telescopica LR4 a N vie NON è esattamente piatta con sole
   bande in fase: la proprietà |LP4+HP4| = 1 vale per la coppia a 2 vie;
   in cascata a 5 vie le fasi accumulate tra crossover vicini (spaziature
   1,55-1,96 ottave alle frequenze PROVVISORIE) producono buchi di somma
   −3…−5 dB (misurato: −4,8 dB @1,2 kHz). La polarità alterna peggiora
   (−8,9 @90 Hz).

Soluzione v0.2 = §3.1 (banca allineata in fase), realizzata e VALIDATA in
§8.2. Alternativa musicale ancora aperta: allargare le spaziature (frequenze
PROVVISORIE — dec. 66, conferma questione 67); lo schema di allineamento
funziona a qualsiasi set di frequenze, quindi la scelta di 67 non è vincolata.

### 8.2 v0.2 — Banca allineata in fase (`bank-aligned.cir`, `align_math.py`)

**SOMMA PIATTA ESATTA: VALIDATA.** Due verifiche indipendenti che combaciano
al centesimo di dB:
- math (`align_math.py`, stdlib): Σ bande compensate = A2(f1)A2(f2)A2(f3)A2(f4)
  con errore 1,1e-15; riproduce anche i buchi v0.1 (−4,73 dB @1,27 kHz stessa
  polarità; −8,92 @87 Hz polarità alterna) = doppia conferma del finding §8.1;
- LTspice (`bank-aligned.cir`, circuito completo: spina HP + LP + 6 AP2 reali
  MFB/summer + gate + summer, 7 casi kill × 12 freq): senza kill −0,0002…
  −0,008 dB su 5 Hz–60 kHz (requisito ±0,1 dB, margine 12×); ai crossover la
  somma resta piatta (−0,0004 dB @90 Hz).

| Caso | v0.2 (allineata) | v0.1 (troncata) | Nota |
|---|---|---|---|
| nessun kill, worst | −0,008 dB | −4,73 dB @1,27k | requisito SPEC §6 ✓ |
| KILL SUB | −76,3 dB @10 Hz | −76 | invariato |
| KILL KICK | −18,4 dB (min @~180) | −24 @200 | vedi nota sotto |
| KILL MID | −16,4 dB (min @~650) | −21 @700 | vedi nota sotto |
| KILL HIGH | −14,0 dB (min @~2k) | −15 @2,5k | vedi nota sotto |
| KILL SUPER | −50,5 @15k / −68,2 @25k | −51 / −68 | invariato |
| ALL-KILL | −inf (silenzio assoluto) | −inf | gate VCA, invariato |

Nota sui kill interni "meno profondi": i numeri v0.1 erano gonfiati dalla
cancellazione di fase (le bande residue si sommavano fuori fase e scavavano
anche materiale vivo — gli stessi buchi che rovinavano la somma piatta). La
v0.2 è onesta: il residuo al centro banda è la coda di overlap delle bande
adiacenti in fase (−12·s dB circa, s = spaziatura in ottave). Conseguenza
musicale per la questione 67: spaziature più larghe = kill più profondi
(~6 dB in più per mezza ottava) oltre che bande più distinte.

Altri risultati:
- Group delay: §3.1 (picco 7,9 ms @58 Hz; la v0.1 aveva già 7,3 ms — costo
  dei 24 dB/ott, non dell'allineamento).
- Trimmer: edge spostato ±10% senza muovere l'allpass → errore di somma
  ≈0,02 dB: i trim di edge e allpass NON vanno accoppiati.
- Variante lite (3 AP2/lato): worst −0,125 dB (align_math.py) — sconsigliata:
  al limite del requisito, risparmio solo 3 quad.
- Macromodello: classe OPA1654 (A0 120 dB, GBW 20 MHz). Il macromodello v0.1
  (A0 60 dB) introduceva da solo ~0,15 dB di errore di loop: i numeri assoluti
  v0.1 vanno letti con quel pavimento (i buchi −3…−9 dB erano comunque reali).
- Idea collegata (da valutare nel design di sistema, questione 18 CUE): le
  prese di banda allineate in fase sono utili anche per un monitoring CUE
  coerente in fase.

### 8.3 Nota di metodo

Tutti i valori [PROVVISORIO]; le misure usano il macromodello op-amp classe
OPA1654 (A0 120 dB, GBW 20 MHz, lineare): la piattezza fine della banca si
verifica coi modelli reali (rumore/THD in beta-3) e soprattutto a banco con
trimmer di allineamento (§3). I gate sono ideali (g = 0/1): THAT 2181 reale
+ ramp 1 ms = §10 punto 4.

## 9. Questioni toccate

- **8** (matematica filter bank): RISPOSTA v0.2 — banca ALLINEATA IN FASE:
  somma piatta ESATTA dimostrata in math (Σ = prodotto dei 4 allpass, |Σ| = 1,
  errore 1e-15) e validata in simulazione (−0,0002…−0,008 dB su 5 Hz–60 kHz,
  §8.2); kill invariato (all-kill = silenzio assoluto). Lo schema funziona con
  qualunque frequenze di crossover: resta aperta solo la scelta musicale
  (questione 67 — dato nuovo: spaziature più larghe = kill più profondi,
  ~6 dB per mezza ottava) e le frequenze dell'impianto di Filippo.
- **9** (EQ creativo): architettura scelta [PROVVISORIO] (parametric SVF
  sottrattivo + position gm + width a switch); APERTO: law di position
  (lineare vs esponenziale — opzione A/B §4, ascolto M4L); legge del gain
  (taper dB); verifica simulata delle celle complete = v0.2.
- **10** (drive): struttura a due stadi definita; taper esatto e carattere
  DOPO le referenze di Filippo (61).
- **24** (layout comandi): invariata — il pannello è design di Filippo;
  l'elettronica fornisce: 5 kill switch + 5 slider/pot gain + 5 pot position
  + 5 switch width + drive pot + (meter).
- **67** (frequenze 5 vie): la banca è progettata con trimmer per edge →
  le frequenze restano spostabili a banco ±10% senza redesign.

## 10. Prossimi passi (v0.2)

0. [FATTO 2026-09-27] **Banca allineata in fase**: soluzione esatta
   dimostrata e validata (§3.1, §8.2 — `bank-aligned.cir` + `align_math.py`).
   Le spaziature non sono più vincolate dalla matematica: l'ascolto per la
   questione 67 è libero (dato: spaziature più larghe = kill più profondi).
1. Simulazione celle parametriche complete (gain/position/width, law,
   interazione tra bande in cascata — stessa metodologia di eq-serie beta).
2. Drive: candidati JFET + spettri armonici (dopo referenze 61).
3. Converter position (opzione B) adattato ai range per banda + mirror.
4. Gate VCA con ramp 1 ms + verifica click (voce 55).
5. Rumore del modulo completo (banca + EQ + drive: il percorso più lungo
   del mixer — budget da sheet §3).
6. Meter pickup e ballistica 10 Hz (con CDJ §7.3).
