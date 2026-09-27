# FASE 2 — Modulo 5-WAY (dub preamp): design v0.1 (2026-09-25)

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

## 3. Kill bank — matematica complementare (questione 8: proposta LR4)

**Scelta [PROVVISORIA]**: crossover Linkwitz-Riley 4° ordine ai 4 punti
(90/350/1,2k/3,5 kHz): ogni edge = due Butterworth 2° ordine (Q 0,707) in
cascata. Proprietà che risponde ai requisiti:
- 24 dB/ott ✓ (4 poli per edge);
- **somma in tensione PIATTA** (proprietà LR: le branche adiacenti sommano
  a −6 dB al crossover con fasi allineate → |Σ| = 1 ±0,1 dB) = "banca
  complementare, somma piatta senza kill" ✓;
- "overlap deliberato senza buchi" = la sovrapposizione −6 dB delle LR ✓;
- bande: SUB = LP4(90) (passa fino a DC/10 Hz: nessun accoppiamento AC,
  requisito infrasub dec. 65 ✓); KICK = HP4(90)·LP4(350); MID = HP4(350)·
  LP4(1,2k); HIGH = HP4(1,2k)·LP4(3,5k); SUPER = HP4(3,5k).
- La somma LR4 esce invertita (fase comune 180°): il make-up d'uscita
  ripristina la polarità assoluta (già invertente per il trim, §2).

Topologia per edge: Sallen-Key biquad unity-gain (1 op-amp per sezione 2 poli;
R da formula con C fissi per decade, 1% + trimmer di allineamento a banco:
la piattezza della banca vive sul matching degli 8 edge). Alternativa MFB
scartata per gli edge LP sotto 100 Hz (rumore gain/2); SK unity è silenzioso
e prevedibile. Conteggio: 16 sezioni 2 poli per lato = 4 quad/lato, 8 per
modulo (solo banca).

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
op-amp (summer + inverter ±BP); per lato ≈ 30 sezioni op-amp in tutto.
Totale modulo: **~18-20 quad** (banca 8, EQ ~10, gate/buffer/make-up)
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
| Quad op-amp low-noise (classe OPA1654/1612) | ~18-20 | banca 8, EQ ~10, buffer/make-up |
| LM13700 (dual OTA) | 10 | celle parametriche (position gm) |
| THAT 2181 (dual VCA) | 5 | gate di kill (10 sezioni) |
| THAT 2181 o JFETmatched | 1-2 | gain drive (stadio 1) |
| JFET saturazione (coppia matched) | 2-4 | stadio 2 drive (post-61) |
| Converter expo position + mirror | 5 sezioni | opzione (B) §4 |
| R 0,1% / C0G-PP / trimmer allineamento | — | banca: 8 edge da allineare |
| Stima costo | ~180-250 € | il modulo più siliconato del mixer |

## 8. Simulazioni v0.1 (`sim/five-way/`)

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

Soluzione per la v0.2: **banca allineata in fase** — allpass di compensazione
per banda (ogni banda attraversa gli allpass dei crossover SOPRA di essa:
SUB 3, KICK 2, MID 1, HIGH/SUPER 0 → +6 sezioni op-amp per lato), tecnica
standard dei crossover attivi quando la somma in tensione deve essere esatta.
Alternativa da ascoltare: allargare le spaziature (le frequenze sono
PROVVISORIE — dec. 66, conferma questione 67). Il requisito "somma piatta
senza buchi" (SPEC §6) resta l'obiettivo; il kill intanto funziona.

### 8.2 Nota di metodo

Tutti i valori [PROVVISORIO]; le misure usano il macromodello op-amp ideale
(GBW 1 GHz): la piattezza fine della banca si verifica coi modelli reali e
soprattutto a banco con trimmer di allineamento (§3).

## 9. Questioni toccate

- **8** (matematica filter bank): RISPOSTA PARZIALE v0.1 — LR4 a 4 crossover
  con gate VCA: kill VALIDATO (silenzio assoluto per via); somma piatta
  ESATTA non ottenuta con la cascata semplice (buchi −3…−5 dB tra crossover
  vicini, §8.1) → v0.2 con allpass di allineamento o spaziature riviste
  (l'ascolto della questione 67 dirà anche questo).
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

0. **Banca allineata in fase**: allpass di compensazione per banda (SUB 3,
   KICK 2, MID 1) + simulazione somma piatta esatta; in parallelo valutare
   spaziature crossover alternative (ascolto questione 67).
1. Simulazione celle parametriche complete (gain/position/width, law,
   interazione tra bande in cascata — stessa metodologia di eq-serie beta).
2. Drive: candidati JFET + spettri armonici (dopo referenze 61).
3. Converter position (opzione B) adattato ai range per banda + mirror.
4. Gate VCA con ramp 1 ms + verifica click (voce 55).
5. Rumore del modulo completo (banca + EQ + drive: il percorso più lungo
   del mixer — budget da sheet §3).
6. Meter pickup e ballistica 10 Hz (con CDJ §7.3).
