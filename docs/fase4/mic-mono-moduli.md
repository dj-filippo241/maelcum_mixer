# FASE 4 — Moduli MIC e MONO: architettura v0.1 (2026-10-13, REV decisione 97)

> **Stato: v0.1 — architettura dei DUE moduli chiusa.** Chiude le
> questioni 15 (mic preamp) e 16 (moduli mono generici) a livello di
> catena, topologia, livelli, rumore e interfacce. Requisiti funzionali
> di SPECIFICA §8 [BLOCCATO] invariati. Valori dei componenti
> [PROVVISORIO — regola 3].
> **Decisione 97 (Filippo, 2026-10-13)**: MIC e MONO sono due moduli
> SEPARATI; su ciascuno ci sono SOLO: GAIN, EQ 2 bande, **4 pot send**
> (uno per bus FX, come in un normale live mixer), un LED di metering
> che cambia colore (rosso = clip); nel sistema ci sono al massimo 4 di
> questi moduli. Sul mic: passa-alto fisso a 60 Hz RATIFICATO.
> La prima stesura di questo documento (stessa data) conteneva scelte
> non richieste — scheda unica, manopola SEND unica + bottoni, bottone
> MIC ON, 3 LED — RIMOSSE.
> Numeri SIMULATI (`sim/mic/` + `RISULTATI-mic-mono.md`): preamp mic
> EIN **−126,5 dBu** (150 Ω), guadagno 29,5…59,3 dB, banda −0,04 dB a
> 35 kHz, passa-alto −3,1 dB a 60 Hz, CMRR 74 dB con sorgente sbilanciata di
> 10 Ω; modulo mono **−101,3 dBu A-wtd** in uscita.
> Finding trasversale: quirk 3 della libreria op-amp → docs/02 voce 73.

## 1. Requisiti

| Voce | Modulo MIC | Modulo MONO | Origine |
|---|---|---|---|
| Ingresso | XLR mono bilanciato, solo dinamici, NO phantom | jack mono | SPEC §8, dec. 36 |
| Impedenza | ~2 kΩ | ≥100 kΩ, meglio di più | SPEC §8 |
| GAIN | 30–60 dB | −∞ → 0 → +10 dB, tollera +18 dBu | SPEC §8 |
| EQ 2 bande | LOW ~120 Hz / HIGH ~5 kHz, −∞→0→+6 | uguale | SPEC §8 |
| Mandata FX | 4 pot send, uno per bus (FX1-4) | uguale | dec. 97 |
| LED | uno, di metering: verde = segnale ok, giallo = vicino al clip, rosso = clip | uguale | dec. 97 |
| Passa-alto | fisso a 60 Hz | — | dec. 97 |
| Assenti | CUE, filtro, 5-way, fader, bottoni | uguale | SPEC §8, dec. 97 |
| Destinazioni | MASTER SUM + bus FX | uguale; mono su L/R senza hard-short | SPEC §7/§8 |
| Quantità | massimo 4 moduli MIC/MONO nel sistema, in qualunque combinazione; primo prototipo: 1 MIC + 3 MONO | | dec. 97 |

Pannello di ciascun modulo: **7 manopole** (GAIN, LOW, HIGH, SEND 1-4)
e **1 LED**. Nient'altro.

## 2. Catene

```
MODULO MIC
 XLR → RFI + clamp → INA +30 dB fisso → passa-alto 60 Hz → GAIN 0…+30 dB
     → nodo PRE ──► detector LED (pre-EQ)
     → EQ2 → nodo POST ─┬─► driver L + driver R → MASTER SUM
                        └─► 4 pot SEND → 4 buffer di iniezione
                            → bus FX 1-4 (L e R)

MODULO MONO
 JACK → R serie + clamp → C film → buffer FET 1 MΩ → pot GAIN
      → make-up +10 dB → nodo PRE ──► detector LED (pre-EQ)
      → EQ2 → nodo POST ─┬─► driver L + driver R → MASTER SUM
                         └─► 4 pot SEND → 4 buffer di iniezione
                             → bus FX 1-4 (L e R)
```

Due moduli, due schede. Dal nodo PRE in poi i due usano le stesse celle
circuitali (EQ2, detector, uscite): è riuso di circuiti già validati,
come l'EQ2 che vive identica in FX-SEND e nei ritorni.

## 3. Modulo MIC — front-end

### 3.1 Topologia: instrumentation amp a guadagno FISSO + stadio variabile

```
XLR pin 1 → CHASSIS al connettore (sistema-grounding §4)
pin 2/3 → ferrite + 100 pF C0G verso chassis (RFI)
        → R serie 10 Ω per gamba + diodi clamp ai rail (BAV199-class)
        → carico differenziale 2,32k + bias 2×47k verso AGND
          (Zin differenziale 2,26 kΩ; modo comune 47k per gamba)
        → INA: coppia OPA1612, Rf 2×499 Ω, Rg 32,4 Ω
          G1 = 1 + 998/32,4 = 31,8 = +30,05 dB FISSO
        → differenziale unity 4×1k 0,1% (OPA1612) → single-ended
        → PASSA-ALTO Sallen-Key 2° ordine 60 Hz (2×220 nF,
          8,45k/16,9k; regola R_fb = R_gnd/2) [RATIFICATO dec. 97]
          — toglie anche l'offset DC dell'INA
        → STADIO 2 invertente (OPA1654): pot GAIN 5k col cursore al
          nodo invertente, R1 332 Ω, R2 5,36k:
          G2 = (R2 + x·P)/(R1 + (1−x)·P) = 0 … +30 dB
        → nodo PRE
```

Dominio: front-end su **±15 V LN** (sheet §1: «primo stadio mic»).
Polarità: differenziale e stadio 2 invertono entrambi, le due celle EQ2
invertono entrambe → modulo NON invertente.

### 3.2 Perché questa topologia

| Alternativa | Esito | Motivo |
|---|---|---|
| INA con Rg variabile (pot reverse-log su Rg) | scartata | a guadagno basso la Rg alta porta rumore; serve un condensatore da migliaia di µF in serie a Rg; pot reverse-log da 500 Ω difficile da trovare |
| Chip dedicato (classe THAT 1510/1512, INA217) | riserva | EIN ~2 dB migliore, ma è un chip in più fuori dalla famiglia in BOM |
| VCA 218x come stadio di gain | scartata | il rumore del VCA starebbe sopra il rumore del microfono già amplificato di 30 dB |
| **INA fisso + stadio variabile** | **adottata** | EIN costante a ogni posizione della manopola; nessun elettrolitico nel percorso (dec. 65); solo OPA1612/OPA1654 già in libreria; overload identico alle alternative, perché il minimo 30 dB è [BLOCCATO] |

Recupero rapido: ingresso accoppiato in DC (senza phantom non servono
condensatori d'ingresso).

### 3.3 Numeri simulati (`sim/mic/mic-pre-*.cir`)

**Guadagno** (pot LINEARE, 1 kHz, sorgente 150 Ω):

| Corsa | 0% | 10 | 20 | 30 | 40 | 50 | 60 | 70 | 80 | 90 | 100% |
|---|---|---|---|---|---|---|---|---|---|---|---|
| dB | 29,5 | 31,1 | 32,8 | 34,5 | 36,3 | 38,3 | 40,5 | 43,1 | 46,4 | 50,9 | 59,3 |

Range 30–60 dB coperto. Con pot lineare l'ultimo 10% di corsa fa
8,4 dB: il taper del pot è materia della voce 40, il circuito non cambia.

**Banda** (a ogni guadagno): −0,01 dB a 20 kHz, −0,04 dB a 35 kHz.
**Passa-alto**: −3,1 dB a 60 Hz, −0,55 dB a 100 Hz, −8 dB a 40 Hz,
−19 dB a 20 Hz. Toglie colpi di mano, «p» esplosive e rimbombo prima
dei sub; sulla voce perde mezzo dB a 100 Hz.

**Rumore** (densità a 16 punti, integrale 20 Hz–20 kHz, mai `.meas INTEG`):

| Sorgente | EIN | Uscita preamp a 30 / 38 / 59 dB (A-wtd) |
|---|---|---|
| 150 Ω (SM58-class) | **−126,5 dBu** (2,58 nV/√Hz, NF 4,3 dB) | −98,9 / −90,2 / −69,3 dBu |
| 300 Ω | −124,7 dBu | −97,7 / −88,9 / −67,9 |
| 600 Ω | −122,2 dBu | −96,1 / −87,3 / −66,3 |

Limite fisico di una sorgente da 150 Ω: −130,9 dBu. La corrente di
rumore dell'OPA1612 (non nel macro) aggiunge +0,03 dB a 150 Ω e
+0,13 dB a 600 Ω.

**CMRR** (modo comune 1 V, piatto da 50 Hz a 10 kHz):

| Caso | CMRR |
|---|---|
| sola tolleranza 0,1% del differenziale | 95,5 dB |
| + sorgente sbilanciata di 10 Ω | **74,2 dB** |
| + bias 47k all'1% | 73,5 dB |

Lezione: comanda lo sbilanciamento del microfono contro l'impedenza di
modo comune. Con bias 2×10k il CMRR era 60 dB; con 2×47k sale a 74.
Costo: offset all'uscita dell'INA (~40 mV tipici, ~0,3 V nel caso
peggiore), tolto dal passa-alto.

**Overload**: l'INA satura a ~+21,8 dBu d'uscita = **300 mV rms al
microfono** (circa 138 dB SPL su un SM58). Un segnale di linea
bilanciato a +24 dBu infilato per errore resta dentro i rail: clip,
nessun guasto.

## 4. Modulo MONO — front-end

```
JACK TS → R serie 1k + diodi clamp ai rail (BAV199-class) + TVS low-cap
        → C film 100 nF + bias 1 MΩ (polo 1,6 Hz)
        → buffer unity FET-input (OPA1654): Zin 1 MΩ
        → pot GAIN 10k passivo (−∞ … 0 dB)
        → make-up non invertente +10 dB (OPA1654, 2,15k/1k)
        → nodo PRE
```

- Dominio ±18 V audio. +18 dBu in ingresso = 8,7 Vp: il buffer unity
  li passa senza clip (rail utile ±16,5 V).
- Zin 1 MΩ: stessa classe del ritorno FX.
- Il pot è PRIMA del make-up: con ingresso caldo si abbassa la manopola
  e lo stadio a guadagno non satura.
- Nessun VCA: in mono non c'è tracking L/R da garantire. 0 dB cade a
  1/3 dell'escursione elettrica del pot; la posizione meccanica
  dipende dal taper (voce 40).
- Una sola variante elettrica (risposta alla questione 16).

Simulato (`gen-ac.cir`, `gen-module-noise.cir`, sorgente 1 kΩ):
guadagno −0,08 / +9,93 dB; banda −0,50 dB a 5 Hz, −0,19 dB a 10 Hz,
−0,08 dB a 35 kHz; rumore del modulo in uscita **−101,3 dBu A-wtd**
a ogni posizione del pot (domina la cella HIGH dell'EQ2).

## 5. Blocchi dal nodo PRE in poi (uguali nei due moduli)

### 5.1 EQ2

Celle serie già validate (fx-module §6, `sim/fx/fx-eq2.cir`): LOW shelf
~120 Hz (C 56 nF, 1 sezione) + HIGH sottrattiva ~5 kHz (3 sezioni,
valori del canale: Rh1/Rh2 4,7k/2,25k), −∞→0→+6, law dedicate
[BLOCCATO]. Mono: 4 sezioni = 1 quad OPA1654. Dominio ±18 V.
La questione 68 (bump del kill HIGH) vale anche qui.

### 5.2 LED di metering (uno, cambia colore)

- Punto di presa: nodo PRE [BLOCCATO: dopo il preamp, prima dell'EQ].
- Circuito: detector di picco condiviso (sistema-metering §2) +
  comparatori (LM339) che pilotano un LED multicolore.
- Tre stati (dec. 97):

  | Colore | Significato | Soglia al nodo PRE [PROVVISORIO] |
  |---|---|---|
  | verde | segnale ok | ≥ −6 dBu |
  | giallo | vicino al clip | ≥ +11 dBu |
  | rosso (latch ~0,5 s) | clip | ≥ +17 dBu |

- Perché rosso a +17 e non a +23: il front-end mic su ±15 V satura a
  ~+20 dBu e l'EQ può aggiungere +6 dB (uscita ≤ +23 dBu sui ±18 V).
  A +17 dBu il rosso si accende 3-4 dB prima della saturazione vera;
  il giallo avvisa 6 dB prima del rosso.
- I colori sono decisi; i tre numeri sono di ingegneria e si tarano
  cambiando una resistenza per soglia (partitore dei comparatori).
  Verifica a orecchio e a banco sul prototipo.

### 5.3 Uscita verso MASTER SUM

Nodo POST → due buffer unity separati (OPA1612 dual) → L e R. Due
driver indipendenti = mono centrato «distribuito propriamente», mai
hard-short [BLOCCATO]. Livello 0 dBu nominale (dec. 94a).

Con fino a 4 moduli, MASTER SUM resta a 7 contributori (dec. 94a): i
moduli MIC si sommano sul net MSUM6 e i moduli MONO sul net MSUM7, in
multidrop come il DJ bus. Ogni modulo porta la propria resistenza di
somma lato sorgente; nel master gli ingressi MSUM6/MSUM7 entrano
direttamente sulla massa virtuale (modifica di dettaglio a master-out
§A2, da riportare alla prossima revisione del master).

### 5.4 Mandata ai bus FX (4 pot send)

```
nodo POST → 4 × pot SEND 10k passivo (−∞ … 0 dB), uno per bus
          → 4 buffer di iniezione (OPA1654 quad), ciascuno con DUE
            R 10k: una verso il net L e una verso il net R del bus
          → slot 2-5 = S1_OUT…S4_OUT
```

- Come in un normale live mixer (dec. 97): ogni manopola dosa quanto
  segnale del modulo va a quel bus. Tutta chiusa = niente; tutta aperta
  = livello pieno (0 dB, mai guadagno positivo). Presa dopo l'EQ.
- Nessun bottone e nessuno switch nel percorso audio.
- Un buffer pilota le due R: i bus sono masse virtuali, L e R restano
  isolati (nessun hard-short).
- GLOBAL_MUTE (linea c9, dec. 94b): un quad ADG1434 mette a massa gli
  ingressi dei 4 buffer durante accensione, spegnimento e guasti. Non è
  un comando: non compare sul pannello.
- Carico sui bus: 4 canali + 4 ritorni + 4 moduli MIC/MONO = 12
  contributori = esattamente il caso già verificato (12 sorgenti in
  fase a 0 dBu, nessun clip — fx-module §3).
- Rumore portato sul bus (`send-bus-noise.cir`, modulo MONO, uscita del
  summing di bus, A-wtd): pot chiuso **−111,2 dBu**, a metà −105,6,
  tutto aperto −100,8. Senza switch il buffer resta sempre collegato:
  con 4 moduli a pot chiusi il bus passa da −100,8 (dec. 89) a circa
  −99,5 dBu A-wtd. Target bus ≤ −88: PASS con 11 dB.
- Taper dei 4 pot: voce 40.

## 6. Rumore e sistema (dati, a mandate chiuse)

Base di sistema senza MIC/MONO: −80,0 dBu A-wtd (ricalcolo 2026-10-13,
docs/06 §8).

| Modulo | Condizione | Uscita verso MASTER SUM (A-wtd) | Sistema |
|---|---|---|---|
| MONO ×1 | qualunque gain | −101,3 dBu | −80,0 |
| MONO ×4 | qualunque gain | −95,3 dBu | −79,9 |
| MIC ×1 | gain 30 dB | −97,3 dBu | −79,9 |
| MIC ×1 | gain 38 dB | −90,0 dBu | −79,6 |
| MIC ×1 | gain 45 dB | ~−83,3 dBu | ~−78,3 |
| MIC ×1 | gain 59 dB | −69,3 dBu | −69,0 |
| **Prototipo: 1 MIC a 30 dB + 3 MONO** | | −93,9 dBu | **−79,8** |

Il mic non ha fader né spegnimento: il suo rumore è sempre sul master,
al livello fissato dalla manopola GAIN. Fino a ~45 dB di guadagno il
sistema resta dentro il target ≤ −78 dBu A-wtd; sopra lo supera. È il
rumore termico del microfono amplificato: nessun circuito lo toglie.
Dato da tenere presente per la condizione di misura del target (dec. 89/95).

## 7. Interfacce di sistema

**Backplane — fino a 4 slot di classe MIC/MONO, riga b**:

| Slot | Segnale |
|---|---|
| 1 | MSUM out L/R (net MSUM6 per i MIC, net MSUM7 per i MONO) |
| 2-5 | S1_OUT … S4_OUT L/R (net multidrop dei bus FX, stesse posizioni della classe FX-SEND) |
| 6-10 | spare |

Riga a e riga c: mappa comune. Ascolta GLOBAL_MUTE (c9).

**Rail locali e correnti** [PROVVISORIO]:

| Modulo | ±18 V audio (da raw ±27) | ±15 V LN (da raw ±22) | +5 V |
|---|---|---|---|
| MIC | ~22 mA tip / 40 max | ~20 mA tip / 30 max | ~15 mA |
| MONO | ~30 mA tip / 45 max | ~5 mA (detector) | ~15 mA |

Alimentatore riverificato il 2026-10-13 con 4 moduli: il ramo audio
reale è ~1,2 A (contando anche FX-SEND e cuffie) e il trasformatore è
stato ridimensionato a 200 VA (decisione 98, `sistema-psu.md` REV).

**Grounding**: XLR pin 1 a CHASSIS al connettore; jack con sleeve a
AGND del modulo, come i jack pedali (sistema-grounding §4).

## 8. Silicio per modulo [PROVVISORIO — regola 3]

| Voce | MIC | MONO |
|---|---|---|
| OPA1612 dual | 3 (coppia INA; differenziale; driver L/R) | 1 (driver L/R) |
| OPA1654 quad | 3 (passa-alto + stadio 2; EQ2; iniezione) | 3 (buffer + make-up; EQ2; iniezione) |
| ADG1434 quad SPDT | 1 (solo mute globale delle mandate) | 1 |
| LM339 + detector + LED multicolore | 1 | 1 |
| Regolatori locali | LM317/337 ±18, LT3045/94 ±15 LN, 78L15/79L15 switch | LM317/337 ±18, 78L15/79L15 switch |
| Pannello | 7 pot, 1 LED, XLR | 7 pot, 1 LED, jack |

Nessun VCA 218x: il lotto della voce 37 non cambia.

## 9. Simulazioni (`sim/mic/`, 2026-10-13)

`mic-pre.inc` (preamp) · `backend.inc` (EQ2 + driver, blocco di
simulazione) · `mic-pre-ac.cir` · `mic-pre-noise.cir` + varianti
300/600 Ω · `mic-pre-cmrr.cir` · `mic-module-noise.cir` · `gen-ac.cir` ·
`gen-module-noise.cir` · `send-bus-noise.cir` · `noise_total.py` ·
`RISULTATI-mic-mono.md`.

NON simulati in questa v0.1: THD e clip reali (macro lineare: banco),
clamp d'ingresso, mute globale delle mandate. Già validati altrove e
riusati: cella HIGH a 5 kHz (è quella del canale, eq-serie §9), detector
del LED (sistema-metering §2).

## 10. Risposte di Filippo (2026-10-13) — nessuna domanda aperta

1. LED: verde = segnale ok, giallo = vicino al clip, rosso = clip.
2. Massimo 4 moduli in qualunque combinazione; primo prototipo =
   1 MIC + 3 MONO.

Voce 40 (sessione hardware): taper dei pot GAIN e SEND.

## 11. Prossimi passi

1. Taratura delle tre soglie del LED sul prototipo.
2. Suite di simulazione completa (elenco in §9).
3. Schema e BOM dei due moduli.
4. Riverifica PSU con 4 moduli (S1) e nota di revisione a master-out §A2.
5. Banco: EIN con sorgente reale, CMRR con cavo lungo, RFI.
