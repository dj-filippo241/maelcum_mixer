# Trim dei VCA 2181 / V2181L — v0.1 (2026-10-21, todo 17)

Stato: [PROVVISORIO] su carta e in simulazione. Si chiude a banco, sul
lotto vero di chip (dec. 37: rotta clone CoolAudio V2181L).

Simulazioni: `sim/system/vca_trim.py` (calcolo dei trim, abbinamento
Monte Carlo, generatore del netlist) e `sim/system/vca-trim-casi.cir`
(LTspice). Numeri in `sim/system/RISULTATI-vca-trim.md`.

## 1. Il problema in una riga

Due VCA di una coppia stereo ricevono la stessa CV ma non danno lo
stesso guadagno: ogni chip ha la sua costante (mV/dB) e il suo guadagno a
CV zero. L'errore cresce con l'attenuazione: a −40 dB la coppia peggiore
del datasheet sbaglia di 1,7 dB fra L e R. L'immagine stereo si sposta
mentre giri la manopola.

## 2. Dati dei chip

**CoolAudio V2181 (datasheet Rev. 1.0, 8 pagine).** Nessuna tabella di
caratteristiche elettriche: solo grafici e schemi.
- Fig. 2: −90 dB a −540 mV, cioè ~6,0 mV/dB a 25 °C.
- Pin: 1 IN, 2 EC+, 3 EC−, 4 EC+ (SYM), 5 V−, 6 GND, 7 V+, 8 OUT. È la
  piedinatura del THAT 2181.
- Trim di simmetria (fig. 4, 10): cursore di un 50 kΩ fra ±15 V →
  Rsym 150 kΩ → pin 4, con 51 Ω dal pin 4 a massa. Escursione ±5,1 mV.
- Fig. 3: la THD sale da ~0,005 % a ~0,3 % con 2 mV di errore di
  simmetria. **Il trim di simmetria è obbligatorio su ogni chip.**
- Distorsione dichiarata: 0,008 % a 0 dB, 0,035 % a +15 dB. È il grado C
  del THAT.

**THAT 2181 (datasheet 600030 Rev 02), il riferimento dei numeri:**

| Parametro | A | B | C |
|---|---|---|---|
| Costante di controllo | 6,0 / 6,1 / 6,2 mV/dB | uguale | uguale |
| Deriva della costante | +0,33 %/°C, la law ruota attorno a 0 dB | | |
| Linearità della law (−60…+40 dB) | 0,5 % typ, 2 % max | | |
| Guadagno a CV 0 | ±0,1 dB | ±0,15 dB | ±0,2 dB |
| Tensione di simmetria | ±0,5 mV | ±1,5 mV | ±2,5 mV |
| ΔEc massimo assoluto | ±1 V | | |

**Assunzione di lavoro:** il clone vale come un THAT grado C. La
dispersione vera della costante del clone non è pubblicata: si misura sul
lotto (§6).

## 3. Circuito

### 3.1 Per ogni chip: trim di simmetria

Come il datasheet del clone: cursore di un trimmer 50 kΩ multigiro fra
±15,0 V LN → 150 kΩ → pin 4; 51 Ω dal pin 4 a massa; pin 2 a massa.
Escursione ±5,1 mV: copre due volte il grado C. Il rumore dei ±15 V LN
arriva al pin diviso per ~2900: trascurabile.

### 3.2 Per ogni coppia: trim di law (lato R)

La CV entra solo dal pin 3 (EC−), **bipolare**: positiva taglia, negativa
alza. Un porto solo per tutta la corsa, così il trim vale anche per il
boost (§5.3).

```
            lato L (riferimento)            lato R (trimmato)
CV ──┬── 1,00k ──┬── pin 3 L      CV ── 900 ── trimmer 200 Ω ──┬── pin 3 R
     │           1,00k                        25 giri          1,00k
     │           │                                             │
     │          GND                    trimmer 50k ±15 V ── 1,5M ──┘
     │                                  (offset)               GND
     └── (stessa CV per i due lati: un solo shaper per coppia)
```

| Elemento | Valore | Cosa fa |
|---|---|---|
| Partitore L | 1,00k / 1,00k (0,1 %) | a = 0,500 |
| Partitore R | 900 + trimmer 0-200 Ω / 1,00k | a = 0,476…0,526: scala ±5 % |
| Offset R | cursore 50k fra ±15 V LN → 1,5 MΩ → pin | ±0,82 dB a ogni guadagno |
| Shaper | uscita ×2 rispetto ai design attuali | la CV al pin resta quella di oggi |

Perché 1 kΩ e non 100-200 Ω: con un partitore basso l'escursione
dell'offset dipende dalla posizione del trimmer di scala (varia di 3×).
Con 1 kΩ varia del ±5 %: i due trimmer sono quasi indipendenti.

Impedenza vista dal pin: ~500 Ω. Il rumore termico (2,9 nV/√Hz) modula il
guadagno in modo trascurabile. Lo shaper eroga al massimo 1,22 V su
~2 kΩ per lato: 0,6 mA.

### 3.3 Dove non serve il trim di law

VCA singoli, senza un compagno da inseguire: MONO del master (VCA sul
canale S) e MUTE del mic. Basta la simmetria.

## 4. Inventario dei VCA

| Ruolo | Chip | Coppie stereo | Tracking richiesto |
|---|---|---|---|
| GAIN canale CDJ ×4 | 8 | 4 | ≤ 0,5 dB (cdj §3.2) |
| MASTER LEVEL | 2 | 1 | ≤ 0,25 dB (SPEC) |
| BOOTH LEVEL | 2 | 1 | ≤ 0,25 dB [PROVVISORIO, come il master] |
| GAIN ritorno FX ×4 | 8 | 4 | ≤ 0,5 dB [PROVVISORIO] |
| REROUTE FX (4 ritorni × 4 bus) | 32 | 16 | ≤ 0,5 dB [PROVVISORIO] |
| Overdrive filtro (una cella per lato) | 8 | 4 | ≤ 0,5 dB [PROVVISORIO] |
| MONO master (canale S) | 1 | — | — |
| MUTE mic | 1 per modulo mic | — | — |
| Crossfader (modulo opzionale, dec. 111) | 8 | 4 | ≤ 0,5 dB [PROVVISORIO] |

Totale: **62 chip** nel mixer base con un mic (più 8 col crossfader).
**[REV 2026-10-22, dec. 126]** +16 VCA dei fader (4 canali + 4 ritorni,
stereo): **~78 chip**, lotto ~95-105 pezzi (`sim/cdj/RISULTATI-fader-vca.md`).
Ogni coppia ha **una CV sola** (dec. 91: «stereo linked»).

**FINDING — conteggio dei VCA del modulo FX.** `fx-module.md` §7 conta
«8 sezioni VCA per ritorno = 32 sezioni = 16× THAT 2181». È il conto coi
chip «dual», corretto ovunque il 2026-09-27 tranne qui: il 2181 è
singolo, 32 sezioni = **32 chip**. Anche il GAIN dei 4 ritorni stereo è 8
chip, non 4. Il modulo FX ha 40 VCA, non 20. Il totale del mixer passa
da ~34-36 a ~62. Conseguenze: lotto d'acquisto (voce 37: 56-64 pezzi
dichiarati con scorte, ora servono ~70-80), corrente del modulo FX
(+20 chip: da +48 a +110 mA per ramo sui ±18 V), costo. Riportato il
2026-10-21 (todo 114) in `fx-module.md`, `sistema-psu.md` (REV
2026-10-21: W1 3,5 A al 98-100 % con tutti gli opzionali) e voce 37 di
`docs/02`.

## 5. Numeri

### 5.1 Escursione e risoluzione dei trimmer

| Trimmer | Escursione | Un giro (25 giri) |
|---|---|---|
| Scala (200 Ω) | −5,2 / +4,8 % di k | 0,16 dB a −40 dB |
| Offset (50k su 1,5 MΩ) | ±0,82 dB | 0,066 dB |
| Simmetria (50k su 150k/51 Ω) | ±5,1 mV | 0,4 mV |

Il grado C chiede al massimo ±3,3 % di k (6,0 contro 6,2) e ±0,4 dB di
offset fra i due chip: dentro, con margine.

### 5.2 Coppie peggiori, scarto R − L in dB (LTspice = calcolo)

Trim a due punti: offset a CV 0, scala a −40 dB.

| Coppia | +10 | 0 | −20 | −40 | −60 | −80 |
|---|---|---|---|---|---|---|
| THAT C, k 6,0/6,2, offset −0,2/+0,2: senza trim | +0,07 | +0,40 | +1,06 | +1,73 | +2,39 | +3,05 |
| idem, dopo il trim | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 |
| + linearità 0,5 % typ, dopo il trim | +0,04 | 0,00 | −0,04 | 0,00 | +0,10 | +0,28 |
| + linearità 2 % max, dopo il trim | +0,18 | 0,00 | −0,14 | 0,00 | +0,43 | +1,13 |
| clone 5,8/6,3 (±4 %): fuori dal campo del trimmer | −0,33 | 0,00 | +0,66 | +1,31 | +1,97 | +2,63 |

Lettura:
- Il trim azzera la parte lineare dell'errore (costante e offset).
- La non linearità non si trimma. Con il valore tipico la coppia resta
  entro 0,28 dB fino a −80 dB. Con il valore massimo del datasheet esce a
  −60 dB (0,43) e a −80 dB (1,13): lì serve scartare il chip, non girare
  un trimmer.
- Una coppia con le costanti a più del 5 % non entra nel campo del
  trimmer. Si evita abbinando i chip prima del montaggio (§6).

### 5.3 Perché un porto solo

Il GAIN dei canali oggi usa EC− per il taglio ed EC+ per il boost
(`sim/cdj/vca-law.cir`). Un trim sul solo EC− lascerebbe il boost senza
correzione: a +10 dB la coppia peggiore del grado C sbaglia di 0,33 dB.
Con la CV bipolare su EC− un trim copre −100…+10 dB. Lo stesso vale per
il MASTER (+6 dB a fine corsa). Lo shaper diventa un sommatore con uscita
bipolare: cambia l'implementazione, non la law.

### 5.4 Temperatura

- La costante cambia di +0,33 %/°C, uguale per i due chip se stanno alla
  stessa temperatura. 1 °C di differenza fra L e R vale 0,13 dB a
  −40 dB. **Regola di layout:** i due chip di una coppia affiancati, lontani
  da regolatori e dissipatori, stesso flusso d'aria.
- Trimmer cermet ±100 ppm/°C su 200 Ω: 0,01 % di scala su 30 °C,
  trascurabile.
- La compensazione termica di `sistema-psu.md` (resistenza a
  +3300 ppm/K nella scala della CV) entra al posto della 1,00k verso
  massa, su tutti e due i lati: il trim resta valido.

## 6. Strategia: abbinare, poi trimmare dove serve

Monte Carlo (`vca_trim.py`): lotto di 62 chip, costante uniforme ±3 %,
offset ±0,2 dB, misura a banco a due punti e abbinamento per vicinanza.
Senza nessun trim di law: **86 % delle coppie entro 0,25 dB, 100 % entro
0,5 dB** da +10 a −60 dB.

Proposta [PROVVISORIO, si conferma sul lotto]:
1. **Simmetria: trimmer su ogni chip.** Obbligatorio, 62 trimmer.
2. **Abbinamento su una scheda di prova (jig)**: per ogni chip si
   misurano il guadagno a CV 0 e a −40 dB. Si formano le coppie per
   costante vicina, poi per offset vicino. I chip con la law curva
   (linearità fuori) vanno scartati.
3. **Trim di law popolato solo dove la richiesta è ≤ 0,25 dB**: MASTER e
   BOOTH, 2 coppie, 4 trimmer. Sugli altri moduli il circuito del §3.2
   ha le piazzole sul PCB; il trimmer si monta solo se la coppia misurata
   esce di tolleranza. Il lato R senza trimmer monta 1,00k fisse come L.

Costo del lavoro a banco: un jig, una sessione di misura del lotto, 62
trim di simmetria, 2-4 trim di law.

## 7. Procedura a banco

Strumenti: generatore 1 kHz (anche la scheda audio), scheda audio con
REW per livello e THD, multimetro con portata mV. È la lista di A11.

**Jig (una volta, sul lotto):**
1. Zoccolo SIP-8, I/V con 20 kΩ come il datasheet, alimentazione ±15 V.
2. Ogni chip: trim di simmetria (sotto), poi livello d'uscita a CV 0 e a
   CV −40 dB, con lo stesso ingresso. Annota i due numeri sul chip.
3. Coppie: costante vicina, poi offset vicino. Scarta i chip più lontani
   dalla media.

**Simmetria (ogni chip, a modulo montato):**
1. CV a 0 (manopola al detent o al punto di 0 dB del ruolo).
2. Ingresso 1 kHz, ~1 V (0 dBV).
3. Gira il trimmer di simmetria fino al minimo della THD sull'uscita.

**Law (coppie col trimmer):**
1. Simmetria fatta su L e R.
2. Stesso segnale 1 kHz su L e R, manopola al punto di 0 dB.
3. Trimmer di offset: L − R = 0 entro 0,02 dB.
4. Manopola al punto di −40 dB.
5. Trimmer di scala: L − R = 0 entro 0,05 dB.
6. Ricontrolla il punto 3: l'interazione vale meno di 0,02 dB.
7. Verifica a +6/+10, −20 e −60 dB. Se a −60 lo scarto supera 0,25 dB,
   la coppia ha la law curva: cambia un chip.

## 8. Cosa resta

- Lotto vero: dispersione della costante e linearità del clone. Se il
  clone è più largo del ±3 %, il Monte Carlo va rifatto e il trimmer di
  scala va allargato (400 Ω: ±10 %, 0,32 dB a giro).
- Corrente di bias dei pin EC: non è in nessun datasheet. Su 500 Ω, 1 µA
  vale 0,08 dB di offset: lo assorbe il trimmer di offset o l'abbinamento.
- Shaper dei moduli: uscita ×2 e CV bipolare su EC− (cdj §3.2,
  master-out §3, fx §8.3, filter §5ter). Si applica quando si disegna lo
  shaper reale.
- W1 senza margine con tutti gli opzionali (`sistema-psu.md` REV
  2026-10-21): scelta di Filippo, 3,5 A o 4,0 A.
