# BENCHMARK EQ A 4 BANDE — frequenze e tagli (ricerca 2026-10-14 sera)

> Richiesta di Filippo dopo l'ascolto di P0 (dec. 114): dai benchmark
> (`docs/05`, `docs/07`) tutti i mixer con EQ o isolator a 4 bande, con i
> loro tagli; dove non sono dichiarati, misure di terzi. Serve a B7
> (incroci dell'isolator). Ricerca web dello stesso giorno.
>
> Gradi di certezza: **[U]** = documento ufficiale del costruttore
> (manuale, scheda tecnica, manuale di servizio); **[V]** = rivenditore;
> **[M]** = misura di terzi; **n.t.** = non trovato.

## 1. Attenzione: due famiglie diverse

- **Isolator** (come il nostro, dec. 105): bande divise da incroci; ogni
  manopola va a −∞. I numeri sono **confini** tra le bande.
- **EQ DJ a campana** (Xone, Pioneer in modo EQ): LO e HI a scaffale con
  kill, i medi a campana con taglio finito (−26…−30 dB). I numeri sono
  **centri** (medi) o **angoli** (LO, HI), non confini. Le bande si
  accavallano molto: LO e LO-MID distano meno di un'ottava.

## 2. Mixer DJ con 4 bande per canale

| Mixer | Tipo | LO | LO-MID | HI-MID | HI | Escursione | Pendenza | Fonte |
|---|---|---|---|---|---|---|---|---|
| Xone:92 Mk2 | EQ campana | 220 Hz | 320 Hz | 1,8 kHz | 2,4 kHz | LO/HI +6/−∞; medi +6/−30 | 12 dB/ott. su LO/HI (Xone:92 orig.) | [U] scheda tecnica Mk2 |
| Xone:92 orig. | EQ campana | 250 Hz | 350 Hz | 2 kHz | 2,5 kHz | idem | 12 dB/ott. LO/HI | [U] manuale (specifiche) |
| Xone:96 | EQ campana «asimmetrico» | 180 Hz | 350 Hz | 1,1 kHz | 3 kHz | LO/HI +6/−∞; medi +10/−27 | n.t. | [U] manuale |
| Xone:464 (stereo) | EQ campana | 100 Hz | 250 Hz | 1 kHz | 10 kHz | +6/−23 (brochure) o −26 [V] | n.t. | [U] brochure |
| Pioneer DJM-V10 | EQ campana (DSP) | 200 Hz | 400 Hz | 1,2 kHz | 2 kHz | LO/HI +6/−∞; medi +6/−26 | n.t. | [U] manuale di servizio RRV4703 |

Misura di terzi sulle Xone:92: un utente (Tarekith, forum Ableton) dice
che all'analizzatore gli angoli «sono diversi» da quelli del manuale, ma
non pubblica i numeri [M, senza valori].

## 3. Isolator a 4 bande

| Mixer | Confini | Escursione | Pendenza | Fonte |
|---|---|---|---|---|
| Condesa Carmen V (opz. 4 vie, master) | 80 Hz / 280 Hz / 4 kHz | +12 / −∞ | 24 dB/ott. (4 poli), discreto | [U] condesaelectronics.com + [V] Rubadub |
| MasterSounds Radius 4 MK2 | SUB 110 / LOW 210 / MID 1,5k / HIGH 3k Hz (non chiaro se centri o confini) | OFF … +7 | n.t. (MK1: 12 dB/ott.) | [U] manuale MK2 |

## 4. Crossover a 4 vie dei preamp dub (contesto, non EQ)

| Preamp | Confini | Fonte |
|---|---|---|
| Jah Tubby's EN4 (un esemplare) | ~100 / ~300 / ~3,5-4k Hz | [R] docs/07 |
| JB Audio Units (5 vie) | 75 / 190 / 2,2k / 8k Hz | docs/05 |
| Mostec, Leviel 5W4U | n.t. (Mostec: incroci fissati sul sistema; Leviel: parametrico) | docs/05, 07 |

## 5. Isolator a 3 bande (riferimento per i confini estremi)

| Mixer | Confini | Pendenza | Fonte |
|---|---|---|---|
| Condesa Carmen V (3 vie) | 280 Hz / 4 kHz | 24 dB/ott. | [U] |
| MasterSounds Radius 4 MK1 | 350 Hz / 3,5 kHz | 12 dB/ott. | [U] manuale |
| MasterSounds Radius MK2 (3 vie) | 650 / 1,5k / 3k (bande) | n.t. | [U] |
| E&S DJR400 | 300 Hz / 3 kHz | n.t. | docs/07 |
| Rane MP2015 (master) | variabili | LR4 | docs/07 |
| Pioneer DJM-900NXS2 / V10 (master) | n.t. (Pioneer pubblica solo −∞/+6, +9) | n.t. | [U] |

Pioneer isolator: nessun confine pubblicato né misurato. L'unica misura
trovata (wavealign.app, modello non dichiarato) descrive solo la forma
della law: in modo isolator il taglio è dolce nella prima metà della corsa
e ripido nella seconda; in modo EQ succede il contrario. Niente numeri.

## 6. Lettura per B7

- Confine LOW / LOW-MID: le Xone e il V10 mettono LO a 180-220 Hz e LO-MID
  a 320-400 Hz; gli isolator stanno a 80-110 Hz (con banda SUB) o a
  280-350 Hz (3 vie).
- Confine MID / HI: tutti tra 2 e 4 kHz (V10 2k, Xone:92 2,4k, Xone:96 3k,
  MasterSounds 3k, Condesa 4k). La nostra C (3150 Hz) sta nel mezzo.
- Confine LOW-MID / MID-HIGH: i DJ EQ hanno il centro di LO-MID a
  320-400 Hz e di HI-MID a 1,1-1,8 kHz; il confine «implicito» cade
  intorno a 600-800 Hz. La nostra C lo mette a 350 Hz, più in basso di
  tutti.
- L'accavallamento LO/LO-MID chiesto da Filippo è la regola nei DJ EQ a
  campana (220 e 320 Hz nella Xone:92: mezza ottava).

## Fonti

- Xone:92 Mk2, scheda tecnica: allen-heath.com/content/uploads/2024/10/Xone92-Mk2-Technical-Specifications.pdf
- Xone:92 orig., manuale: manualslib.com/manual/627884 (p. 34)
- Xone:96, manuale (copia): veranstaltungstechnikmueller.de/pdf/Allen_Heath_Xone96_Bedienungsanleitung.pdf
- Xone:464, brochure: fullcompass.com/common/files/48-AllenHeathXone464Brochure.pdf
- DJM-V10: manuale di servizio RRV4703 (pdfcoffee.com, manualslib.com/manual/3461698), hightech.ee
- DJM-900NXS2, manuale: novelty.fr (pioneer_djm-900nxs2_manual_EN.pdf)
- MasterSounds Radius 4 MK2: manuals.plus, theransomnote.com; MK1: manualslib.com/manual/1565567
- Condesa Carmen V: condesaelectronics.com/products/carmen-v, rubadub.co.uk
- Misure: wavealign.app/blog/pioneer-mixer-isolator-vs-eq-mode; forum.ableton.com/viewtopic.php?t=161248
