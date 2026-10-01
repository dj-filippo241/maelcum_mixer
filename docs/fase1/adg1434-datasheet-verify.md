# ADG1434 — verifica datasheet e second source (task 2 handoff)

Data: 2026-10-01. Fonti: datasheet ufficiale ADG1433/ADG1434 **Rev. E (8/2016)**
(letto da copia mirror: analog.com diretto in timeout) + fetch diretti DigiKey
+ EngineerZone ADI (raggiungibile solo via motore di ricerca). Marcature:
[VERIFICATO] da datasheet/distributore · [INCERTO] fonti contraddittorie ·
[NON TROVATO] assente dalle fonti raggiungibili.
Vale per: gate kill 5-way (π SPDT, five-way §8.10), assign FX nei
micro-moduli FX-SEND (dec. 91a), selettore LINE/PHONO (cdj).

## 1. Dati chiave Rev. E

| Voce | Valore | Marcatura |
|---|---|---|
| Revisione datasheet | Rev. E (8/2016) = **ultima** (history si ferma a E) | [VERIFICATO] |
| Ron @ ±15 V, 25 °C | 4,0 Ω typ / **4,7 Ω max** (VS ±10 V, IS −10 mA) | [VERIFICATO] |
| Ron max su temperatura | 5,7 Ω @85 °C · 6,7 Ω @125 °C | [VERIFICATO] |
| Ron flatness / match | 0,5 Ω typ (0,72-0,92 max) / 0,5 Ω typ | [VERIFICATO] |
| Coff | CS(off) 12 pF · CD(off) 22 pF · on 72 pF (1 MHz) | [VERIFICATO] |
| Charge injection | −50 pC typ @±15 V (−10 pC @+12 V, −100 pC @±5 V) | [VERIFICATO] |
| Range alimentazioni | **±4,5 … ±16,5 V** dual (abs max VDD-VSS 35 V) → "max ±16,5" dec. 90c CONFERMATO; rail ±15 V switch (dec. 93) dentro con margine | [VERIFICATO] |
| Pin VL | **NON ESISTE** su ADG1434: soglie logiche fisse GND-referenced, VIH 2,0 V min / VIL 0,8 V max | [VERIFICATO] |
| Pilotaggio +5 V via 10k | Dentro specifica: caduta ≈0,65 V (IDD ~260 µA typ con IN a 5 V) → IN ≈4,3 V ≥ VIH | [VERIFICATO] |
| Corrente continua/canale | 100 mA max @25 °C (65 @85 °C) — il "115 mA" delle pagine marketing è dell'ADG1433 | [VERIFICATO] |
| Off isolation / THD+N | −70 dB typ @1 MHz (switch singolo; Fig. 20: ≈−100 dB @20 kHz) · THD+N 0,025 % typ in banda audio | [VERIFICATO] |
| Switching | tTRANS 140/230 ns · BBM 40 ns typ | [VERIFICATO] |
| Package | **TSSOP-20 (YRUZ, SENZA pin EN)** · LFCSP-20 4×4 (YCPZ, CON EN) · niente SOIC | [VERIFICATO] |
| ESD HBM | nessun numero nel datasheet (solo ESD CAUTION); EngineerZone contraddittorio (2 kV vs 8 kV) | [NON TROVATO]/[INCERTO] |

## 2. Verifica dei numeri di progetto

| Numero di progetto | Riscontro | Esito |
|---|---|---|
| Ron ~4,7 Ω usato nelle sim (five-way §8.10, fx-send) | 4,7 Ω = **max @25 °C** (typ 4,0): conservativo a temperatura ambiente; su range esteso il max sale a 5,7 Ω @85 °C | CONFERMATO con caveat temperatura |
| "ADG1434-class max ±16,5" (dec. 90c) | ±4,5…±16,5 V operativo | CONFERMATO |
| Off-isolation π SPDT −95 dB @20 kHz (misurato in sim §8.10) | Fig. 20: ≈−100 dB @20 kHz già per switch singolo → −95 in π coerente | CONFERMATO (coerenza) |
| Pilotaggio +5 V, serie 10k + 100n, ramp τ≈0,5-1 ms (dec. 80/91a) | Dentro specifica logica; τ 1 ms ≫ tON 230 ns = rallentamento VOLUTO (soft-switch audio), non un problema | CONFERMATO |
| Regola backplane "modulo spento: <1 mA dai pin audio" (S3 §7.3) | Clamp interni con limite 30 mA: 1 mA è sotto il limite MA il caso power-off NON è garantito dal datasheet (non è un part "power-off protected"; EZ avverte di possibile danno) | [INCERTO] — la regola di servizio "mai alimentare segnali esterni col mixer spento" resta OBBLIGATORIA |

## 3. Stato produzione e reperibilità

- **ACTIVE** (nessun annuncio EOL/NRND): DigiKey ADG1434YRUZ stock ~2.000 pz.
- Prezzo: $11,67 @1 · $9,14 @10 (DigiKey, 2026-10-01). Mouser in timeout.
- Conteggio progetto [PROVV — ricalcolo a BOM]: ~3 (5-way kill) + 8 (FX-SEND 2×4)
  + 1-2 (assign/line-phono per canale) ≈ **15-20 pz + scorte**. Budget indicativo
  ~$150-250 a listino attuale.
- Lezione voce 37 (THAT EOL) applicata: in casa ADI **non esiste** un quad SPDT
  ±15 V low-Ron pin-compatibile alternativo → all'acquisto (post-M4L, finestra
  dec. 37/78) prendere **lotto + scorte in un colpo solo**, come per i V2181L.

## 4. Second source — FINDING: nessuna è drop-in

| | ADG1434 (rif.) | ADG1634L | ADG1334 |
|---|---|---|---|
| Supply dual | ±4,5…±16,5 V | **±3,3…±8 V (abs max 18 V totali): a ±15 V si DISTRUGGE** | ±13,5…±16,5 V |
| Ron | 4/4,7 Ω | 4,7 Ω typ @±5 V | **130/200 Ω** |
| Logica | soglie fisse 2,0/0,8 V, no VL | pin VL 1,1-1,95 V (JEDEC 1,2/1,8) | soglie fisse 2,0/0,8 V, no VL |
| Package | TSSOP-20 / LFCSP-20 | 24-LFCSP | 20-SSOP (pinout con sospetto swap pin 3/4 [INCERTO]) |
| Drop-in su ±15 V? | — | **NO (guasto certo)** | **NO** (PCB diverso + Ron 43× peggiore) |

Conclusione: ADG1334 è l'unico backup FUNZIONALE a ±15 V (stesse soglie logiche)
ma richiede redesign PCB e degrada insertion loss/flatness — non adatto al π del
kill né ai path FX dove Ron conta. Strategia = scorte a lotto (§3), non second
source. Se un giorno servisse protezione over-voltage: valutare famiglia
fault-protected ADG54xxF (Ron più alta, verifica a parte).

## 5. Azioni sul design

1. **Package**: TSSOP-20 YRUZ (senza EN — il design usa solo le linee IN):
   preferito per l'esemplare unico (saldabilità manuale migliore del LFCSP).
2. **Terminologia "VL"**: il pin VL non esiste — nei doc la linea "+5 V con
   10k+100n" resta corretta, ma va intesa come pilotaggio diretto degli IN
   (soglie fisse GND-referenced).
3. **Ron su temperatura**: se le misure a banco mostrano flatness/insertion
   loss peggiori del previsto a caldo, la causa nota è Ron 5,7 Ω @85 °C
   (le sim a 4,7 Ω sono il worst a 25 °C).
4. **ESD in assemblaggio**: rating HBM non pubblicato e contraddittorio →
   trattare come part sensibile (braccialetto, nessuna Deruga a secco).
5. **Power-off**: rafforzata la regola S3 §7.3 (mai segnali esterni col mixer
   spento): il clamp a 30 mA copre il nostro <1 mA ma fuori specifica.

## Fonti

- Datasheet ADG1433/ADG1434 Rev. E: analog.com/media/en/technical-documentation/data-sheets/ADG1433_1434.pdf (letto da mirror)
- DigiKey ADG1434YRUZ (stato/prezzo/stock): digikey.com/en/products/detail/1246086
- DigiKey ADG1334BRSZ: digikey.com/en/products/detail/1530754
- DigiKey ADG1634LYCPZ-REEL7: digikey.ca/en/products/detail/16538515
- EngineerZone ADI: powered-down 77044 · ESD 77189 (contraddittorio)
- Datasheet ADG1634L / ADG1334: analog.com (percorsi data-sheets)
