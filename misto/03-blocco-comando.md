# MISTO — blocco di comando: requisiti e topologia [PROVVISORIO]

Data: 2026-11-09 (todo 277). Primo caso: il modulo FX-RET (reroute e
fader). Metodo del progetto: requisito → funzione di trasferimento →
topologia. Componenti solo per classe, nessun valore congelato (regola 3):
la simulazione viene dopo (§8).

Fonti: `docs/fase1/fx-module.md` §2bis, §7, §8.3; `docs/fase3/sistema-shaper.md`;
`docs/fase3/sistema-vca-trim.md`; `docs/fase3/sistema-grounding.md` §2;
`docs/fase3/sistema-psu.md` (deriva dei VCA); `pcb/fx-ret/` (generatori e
ponte); `pcb/tools/backplane.py`. Numeri di §5: `misto/script/passi_reroute.py`.

## 1. Cosa fa il blocco

Ogni modulo ha un chip su zoccolo. Il chip legge le manopole con un ADC
(convertitore da tensione a numero), calcola la curva, corregge ogni VCA
con i suoi numeri di taratura e con la temperatura, e scrive la CV con un
DAC (convertitore da numero a tensione). Una cella analogica porta la
tensione del DAC al pin del VCA e la smorza. L'audio non passa mai dal
chip (M2, condizione 1).

**FX-RET, oggi.** Il modulo sta su due schede (segnale col C96, reroute
senza C96, unite dal ponte 2x16). Ha 10 VCA in 5 coppie: 4 reroute (3
cross + SELF) sulla scheda reroute, il fader sulla scheda segnale. Il GAIN
è un pot doppio sul segnale (dec. 162) e resta fuori. Oggi ogni coppia ha
uno shaper a diodi, uno stadio di smoothing (1 ms), un partitore 1k/1k per
lato e le piazzole del trim di law sul lato R.

| Cosa legge il chip | Quanti | Cosa scrive | Quanti |
|---|---|---|---|
| pot REROUTE 1-4 (cursori POT_R) | 4 | CV dei VCA reroute, un canale per VCA | 8 |
| fader del ritorno | 1 | CV dei VCA del fader, un canale per VCA | 2 |
| sensori di temperatura (vicino ai VCA, uno per scheda) | 2 | — | — |

Il meter del ritorno (LM3915) resta com'è: il chip non lo tocca in questo
primo caso (02 §2, riga 11).

## 2. Requisiti

| # | Requisito | Numero | Fonte |
|---|---|---|---|
| R1 | Law del reroute e del fader identica a quella di oggi | 13 punti di fx-module §8.3; fader −12 dB a metà corsa (dec. 126) | fx-module §8.3, shaper §3 |
| R2 | Nessun gradino udibile girando una manopola | passo ≤ 0,05 dB nella zona 0…−15 dB; ≤ 0,1 dB altrove | M2 (3); i due numeri sono deduzione mia, dal passo di 02 §5 |
| R3 | Nessuna oscillazione della CV a manopola ferma | nessun cambio di codice da solo rumore | deduzione mia: un codice che salta fa tremare il guadagno |
| R4 | Ritardo dal gesto alla CV come oggi | ≤ 2 ms, smoothing 1 ms compreso | dec. 80 (1 ms); oggi ~1 ms |
| R5 | Coppia L/R allineata senza trimmer di law | ≤ 0,25 dB da 0 a −60 dB | vca-trim §4 (reroute ≤ 0,5; master ≤ 0,25) |
| R6 | Law ferma con la temperatura del telaio | ≤ 0,1 dB a −15 dB da 20 a 65 °C | obiettivo 2 del misto (M6); oggi +0,7 dB a 40 °C, §5 |
| R7 | Stato sicuro: chip assente, in riavvio, senza alimentazione | VCA chiusi all'accensione; valore tenuto se il chip si riavvia | 02 §5 «Guasto del chip» |
| R8 | Ricambio unico, senza ritaratura | lo stesso chip programmato va in ogni modulo; la taratura resta sulla scheda | M2 (2), M5 |
| R9 | Rumore digitale fuori dall'audio | massa digitale separata; un solo contatto fra AGND e CTRL_GND, alla stella | grounding §2 |
| R10 | Valori modificabili via USB, salvati | curve, taratura, ritardi; nessun display | M4 |

## 3. Funzione di trasferimento

Dalla manopola al pin EC− del VCA (positivo taglia, 6,1 mV/dB a 25 °C):

```
θ (0…1, letto dall'ADC, filtrato)
  → G = law(θ)                          dB, tabella di R1 con interpolazione
  → V = −G · k_i · (1 + 0,0033·(T − 25)) + b_i      V al pin, per il VCA i
  → codice = (V_chiuso − V) / passo_DAC             la cella inverte (§4.3)
  → DAC → cella CV (×−a, offset, τ 1 ms) → pin EC−
```

- `k_i` e `b_i`: costante e offset del VCA i, misurati sul modulo montato
  (§4.6). Prendono il posto del trimmer di scala, del trimmer d'offset e
  dell'abbinamento sul jig.
- `T`: temperatura letta vicino al VCA. Il fattore compensa la costante
  del 2181 che cresce di 0,33 %/°C (sistema-psu: «la scala in dB si
  stringe col caldo»). Oggi questa compensazione non c'è.
- La cella e i suoi resistori entrano in `k_i` e `b_i`: la taratura si
  misura da capo a capo, quindi le tolleranze dei pezzi non pesano. Pesa
  solo la loro deriva (resistori a film sottile, 25 ppm/°C).

## 4. Topologia

```
            lato digitale (+5V, CTRL_GND)       │  lato analogico (AGND)
                                                │
 USB ── Pico 2 su zoccolo ── EEPROM (taratura)  │
          │  ID modulo (4 pin a massa)          │
          │  bus fra moduli (§7, da decidere)   │
          └── SPI ── isolatore digitale ════════╪══ SPI ──┬── ADC 8 canali ← pot ×5, NTC ×2
                                                │         │     (rif. = +REF5, come i pot)
                                                │         ├── DAC A 8 canali → 8 celle CV → VCA reroute
                                                │         └── DAC B 8 canali → 2 celle CV → VCA fader
                                                │                (6 canali liberi)
                                     +5VA ← LDO ← +15LN
```

### 4.1 Chip su zoccolo

- **Classe:** scheda Raspberry Pi Pico 2 (RP2350) coi pin saldati, su due
  file di zoccoli a 20 poli. È il «classe Pico su zoccolo» di 02 §3. Il
  ricambio è una scheda intera, si cambia senza attrezzi, a mixer spento.
- **Perché:** USB nativa, firmware aperto, calcolo in virgola mobile
  (law e correzioni senza trucchi), watchdog, costo ~5 € [STIMA].
- **Scartato:** microcontrollore in DIP-28 (classe ATmega328): niente USB
  nativa, ADC a 10 bit, poca memoria per le tabelle. L'ADC interno del Pico:
  solo 3-4 canali, e meno bit effettivi di quanto chiede R2 nella zona
  ripida (§5).
- **Un firmware per tutti** (R8): il modulo si riconosce da 4 pin collegati
  a massa sulla scheda (16 tipi di modulo).
- **La taratura sta sulla scheda, non nel chip** (R8): una EEPROM I2C
  (classe 24LC256) sul lato digitale tiene `k_i`, `b_i` e le curve del
  modulo. Il ricambio la legge all'avvio: nessuna ritaratura dopo il cambio.

### 4.2 ADC delle manopole

- **Classe:** SAR esterno, 12 bit senza codici mancanti, 8 canali, SPI,
  ≥ 50 ksps (classe MCP3208). Canali: 4 reroute, 1 fader, 2 NTC, 1 libero
  (controllo del riferimento).
- **Raziometrico:** il riferimento dell'ADC è lo stesso +REF5 che alimenta
  i pot. Se il riferimento si sposta, si spostano insieme: la lettura non
  cambia.
- **Firmware:** media di 4 letture per canale, a ~2 kHz per canale; banda
  morta di ±1 passo a manopola ferma (R3). Con 12 bit il passo peggiore è
  0,07 dB in fondo alla corsa, 0,01 dB nella zona del feedback (§5): sotto
  R2 anche con un bit perso al rumore.
- I cursori arrivano come oggi (cavo J2, poi ponte); l'RC di 100 Ω + 10 nF
  ai pin d'ingresso resta (grounding §6.4).

### 4.3 DAC e cella CV

- **Un canale DAC per VCA**, non per coppia: la correzione di ogni chip
  si fa nei numeri (R5). Spariscono il 909 Ω, il trimmer da 200 Ω, il
  trimmer d'offset da 50k e la 1,5 MΩ di ogni coppia.
- **Classe del DAC:** 8 canali, 16 bit, riferimento interno 2,5 V,
  **accensione a codice zero** (classe DAC8568 / AD5668, variante a zero).
  Due chip: A sulla scheda reroute (8 VCA), B per il fader (6 canali
  liberi per i moduli che ne chiedono di più). 12 bit bastano già per R2
  (0,034 dB); 16 bit lasciano margine alle correzioni.
- **Campo al pin:** −0,05…+0,80 V. Copre la law (0…+0,61 V a −100 dB), la
  correzione dei chip (±5 % di scala, ±5 mV d'offset, oltre il campo dei
  trimmer di oggi) e la temperatura (+13 % a 65 °C).
- **Cella:** uno stadio invertente con offset, come lo stadio del partitore
  di oggi (`celle_vca.py`, ×−1/5):

  ```
  DAC ── Rin ──┬── Rf ──┬── (partitore 1k/1k, o R serie) ── pin EC−
               │   C    │
  −REF5 ── Ro ─┤        │      V_out = −(Rf/Rin)·V_dac + (Rf/Ro)·5 V
               └─ −\    │      DAC a 0 V → V_out massimo → VCA chiuso
                 +/ ────┘      C su Rf: τ 1 ms (dec. 80)
               AGND
  ```

  Il verso è voluto: **codice zero = VCA chiuso** (R7). DAC appena acceso,
  DAC senza alimentazione o pin scollegato danno tutti la stessa cosa:
  reroute e fader chiusi.
- **Partitore 1k/1k**: oggi serve al trimmer. Senza trimmer forse basta
  una R in serie verso il pin: da decidere in simulazione (§8).
- **Gradini da aggiornamento**: il DAC scrive a passi. Con 1 kHz e τ 1 ms
  un gesto rapido lascia un'ondulazione della CV a 1 kHz [STIMA,
  deduzione mia: ~0,16 dB con il fader aperto in 100 ms]. Rimedio: il
  firmware interpola e scrive a ≥ 8 kHz, l'ADC resta a 2 kHz. Da misurare
  in simulazione (§8).

### 4.4 Temperatura

- Un NTC 10k all'1 % per scheda, in mezzo ai VCA (reroute: fra le 4
  coppie; segnale: accanto alla coppia del fader), letto dall'ADC in modo
  raziometrico. Basta ±2 °C: a −15 dB l'errore resta sotto 0,1 dB (R6).
- Regola di layout di vca-trim §5.4 invariata: i due chip di una coppia
  affiancati, stessa aria.

### 4.5 Masse e alimentazioni

- **Lato digitale:** Pico, EEPROM, lato A dell'isolatore. Alimentato dal +5V
  del backplane (a21-a22), ritorno su CTRL_GND (a23-a24, riga c). Il Pico
  assorbe ~25-40 mA [STIMA].
- **Lato analogico:** ADC, DAC, celle, NTC, lato B dell'isolatore. +5VA da
  un LDO locale sul +15LN; masse su AGND.
- **Isolatore digitale** (classe ISO77xx / ADuM14xx, 6 canali: clock,
  dati in, dati out, 3 selezioni) fra i due lati. Così il modulo non ha un
  secondo contatto fra AGND e CTRL_GND (R9): il contatto resta unico, alla
  stella (grounding §2). Uscite a riposo alte: senza il lato digitale, le
  selezioni restano spente e i DAC tengono il valore (R7).
- **Traffico SPI solo quando serve:** a manopola ferma il firmware non
  scrive i DAC. A riposo il lato analogico non vede fronti di clock.

### 4.6 Stato sicuro e taratura

| Caso | Cosa succede | Si sente |
|---|---|---|
| Accensione del mixer | DAC a codice zero → VCA chiusi; il chip legge i pot, poi apre con τ 1 ms | niente, poi l'apertura dolce |
| Chip in riavvio (watchdog) | DAC tengono l'ultimo valore; al riavvio il chip legge prima i pot, poi scrive | niente |
| Chip tolto o rotto | DAC tengono l'ultimo valore fino allo spegnimento | i comandi del modulo restano fermi |
| +5V del backplane assente | come il chip tolto | come sopra |
| ±15LN assente | il modulo è spento | — |

**Taratura a banco** (sostituisce vca-trim §7, «Law»): il computer chiede
al chip, via USB, di portare ogni VCA a 0 e a −40 dB; REW misura L e R; il
computer calcola `k_i` e `b_i` e li scrive nella EEPROM. Nessun cacciavite.
Il trim di **simmetria** (THD) resta un trimmer su ogni chip (02 §2, riga 8).
Il jig serve ancora per scartare i chip con la law curva; l'abbinamento
per costante vicina non serve più.

## 5. Numeri (`misto/script/passi_reroute.py`)

Passo dell'ADC sulla law del reroute (bit effettivi):

| Bit | Passo peggiore (fondo corsa) | Zona 0…−15 dB |
|---|---|---|
| 9 | 0,59 dB | 0,078 dB |
| 10 | 0,29 dB | 0,039 dB |
| 12 | 0,073 dB | 0,010 dB |
| 16 | 0,005 dB | 0,0006 dB |

Passo del DAC al pin (campo 0,85 V): 12 bit 0,21 mV = 0,034 dB; 14 bit
0,0085 dB; 16 bit 0,0021 dB.

Errore della law senza compensazione termica (taratura a 25 °C):

| Telaio | a −15 dB | a −40 dB | a −100 dB |
|---|---|---|---|
| 40 °C | +0,71 dB | +1,9 dB | +4,7 dB |
| 55 °C | +1,35 dB | +3,6 dB | +9,0 dB |
| 65 °C | +1,75 dB | +4,7 dB | +11,7 dB |

Lettura: è l'errore di oggi, in tutti i VCA del mixer analogico, e si
aggiunge all'errore degli shaper (shaper §3). A caldo il reroute a −15 dB
diventa −13,3: l'eco dura più a lungo. Col chip si corregge con un NTC e
una moltiplicazione. È il guadagno più concreto dell'obiettivo 2 (M6).

## 6. Cosa cambia sulle schede del FX-RET [STIMA, deduzione mia]

- **Tolti:** 4 shaper del reroute e quello del fader, trim di law e
  d'offset di 5 coppie (~95 impronte, 02 §3).
- **Aggiunti:** zoccoli del Pico, ADC, 2 DAC, isolatore, EEPROM, LDO, 2 NTC,
  ID, 10 celle CV (~75 impronte le celle, ~20 il resto).
- **Saldo:** circa pari. Lo diceva già M6: il misto non va avanti per lo
  spazio. Si conta col generatore quando la topologia è chiusa.
- **Dove sta il blocco:** sulla scheda reroute, che ha 8 dei 10 VCA e
  riceve già i cursori dal ponte. Sul ponte viaggiano solo tensioni ferme:
  +5V e CTRL_GND, il cursore del fader, le 2 CV del fader e l'NTC della
  scheda segnale. Il ponte passa da 2x16 a 2x20 [STIMA]. Nessun clock sul
  cavo vicino alle uscite DIR.

## 7. Domanda per Filippo

**Dove si attacca il computer.** M4 dice «via USB», non dove. Due strade:

1. **Una presa USB sul retro, sul master.** I chip dei moduli parlano fra
   loro su due fili del backplane (pin liberi della riga c: c18, c19,
   c21-c23 e altri). Un cavo solo per cambiare tutto.
2. **Una presa per modulo.** Il Pico ha già la sua presa sulla scheda: si
   raggiunge a modulo estratto, o con una presa per modulo sul retro.

Consiglio: **1**. Un cavo, un programma, tutti i moduli; la presa del Pico
resta per caricare il firmware a banco. Costo: due fili di backplane e un
transceiver per modulo.
Fonte: backplane.py (pin liberi); il resto è deduzione mia.

## 8. Cosa resta (ingegneria, Claude)

1. **Simulazione della cella CV** (`misto/sim/`, LTspice): gradini del DAC
   a 1 e 8 kHz con τ 1 ms, misura del click col metodo di `reroute-ramp.cir`
   (fx-module §8.3); partitore 1k/1k contro R in serie; rumore della CV.
2. **Modello del firmware in Python:** law, correzioni, temperatura, banda
   morta; prova che R2-R6 tornano coi numeri veri di ADC e DAC.
3. **Conteggio delle impronte** col generatore, dopo 1 e 2.
4. Gli altri moduli dopo il FX-RET: master (stato sicuro del MASTER: chiuso
   all'accensione va bene, chiuso al riavvio del chip no), canali (fader e
   dip della levetta, dec. 163), filtro (frequenza e RES), 5-way (POSITION,
   kill allo zero).

Verificato in: Python sì (solo i passi di §5) / LTspice no / Live no.
