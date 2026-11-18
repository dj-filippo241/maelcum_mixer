# FLETCHER (lickshot, dec. 197): due preventivi per 5 schede (2026-11-19)

**Dopo la dec. 198 (un BBD e un clock):** BBD e clock scendono da ~190 a ~100 € per 5 schede
(5 V3205SD + 5 V3102D, 76 $ + spedizione e IVA d'importazione [S]), e spariscono un trimmer
3266W, un V3205 e un V3102 per scheda. Totali aggiornati: **A ~455 €** (~91 € a scheda),
**B ~335 €** (~67 € a scheda). Le tabelle sotto sono quelle a due BBD.

Prezzi letti il 2026-11-19 sui siti dei venditori, senza account e senza caricare file del
progetto. Distinta: `bom.csv` della scheda v0.1 corretta (103 pezzi per scheda). Cambio 1 $ =
0,90 € (stima). TME dà prezzi IVA esclusa: +22 %. Gli acquisti restano sospesi fino al prototipo
(decisione di Filippo, 14/10, confermata il 12/11): questo è solo un conto.

Segni: **[V]** prezzo letto dal venditore, **[S]** stima mia (prezzo non trovato o variante non
controllata).

## A. Tutto a foro passante, saldata a mano

La scheda va ridisegnata a foro passante (chip DIP, resistenze in piedi): il generatore la rifà,
la PCB attuale è SMD.

| Voce (5 schede) | Venditore | Prezzo | Totale |
|---|---|---|---|
| Circuito stampato 280 x 80, 4 strati, 5 pz | JLCPCB, calcolatore online [V] | 38,90 $ + 31,07 $ UPS (DDP) | 63 € |
| TLC2272CP (DIP) x 25 | TME [V] | 3,89 €/pz (15+) | 97,25 € |
| CD4069UBE x 5 | TME [V] | ~0,56 € | 2,80 € |
| CD4046BE x 5 | TME [V] | ~0,65 € | 3,27 € |
| L78L09ABZ, L78L05ABZ x 5 + 5 | TME [V] | 0,26 / 0,32 € | 2,50 € |
| 2N3904, 1N5819, 1N4148 x 3, LED | TME [V] (LED [S]) | | 2,80 € |
| Resistenze a strato metallico x 190 | TME [S] (carbone 0,0075 € [V]) | ~0,03 € | 5,70 € |
| Ceramici 100n, 330n, 100p x 75 | TME [S] | ~0,05 € | 3,75 € |
| Film 100 nF WIMA MKS2 x 15 | TME [V] | 0,247 € (10+) | 3,71 € |
| Film 1 uF x 30 | TME [S] | ~0,45 € | 13,50 € |
| Elettrolitici x 30 (Panasonic FR) | TME [V] | ~0,20 € | 6,00 € |
| Trimmer Bourns 3266W x 25 (anche il 500k) | TME [V] | 1,74 € (25+) | 43,50 € |
| Pot Alps RK09L x 35 | TME [V] (modello verticale da 10k) | 1,41 € (25+) | 49,35 € |
| Zoccoli DIP-8 / 14 / 16 x 55, pin header | TME [V] / [S] | | 4,30 € |
| **TME, IVA esclusa** | | | **238,43 €** |
| TME con IVA + spedizione | [S] spedizione ~10 € | | **~301 €** |
| V3205SD x 10 | StompBoxParts (USA) [V] | 11,00 $ | 99 € |
| V3102D x 10 | StompBoxParts (USA) [V] | 4,20 $ | 38 € |
| BBD e clock con spedizione e IVA d'importazione | [S] spedizione ~20 $ | | **~190 €** |
| **Totale A** | | | **~554 €, ~111 € a scheda** |

## B. SMD montata da JLCPCB, il foro passante lo saldi tu

La PCB di oggi. JLCPCB monta i pezzi SMD coi componenti LCSC; pot, trimmer 3266, elettrolitici,
film, regolatori, BBD e clock li compri e li saldi tu.

| Voce (5 schede) | Venditore | Prezzo | Totale |
|---|---|---|---|
| Circuito stampato (come sopra) | JLCPCB [V] | 38,90 $ + 31,07 $ | 63 € |
| Montaggio Economic: setup 8,18 $, stencil 1,53 $, 975 punti a 0,0016 $ | JLCPCB, listino [V] | | 11,27 $ |
| Pezzi «Extended» (TLC2272, CD4069, CD4046, trimmer 3224W, ~1 passivo) x 3,07 $ | JLCPCB, listino [V]; quali sono Extended [S] | | 15,35 $ |
| TLC2272CDR x 25 | LCSC [V] | 0,316 $ (10+) | 7,90 $ |
| CD4069UBM96 x 5, CD4046BM96 x 5 | LCSC [V] | 0,207 / 0,686 $ | 4,47 $ |
| Trimmer 3224W 500k x 5 | LCSC [V] | 1,41 $ | 7,05 $ |
| Resistenze e condensatori SMD «Basic» x ~300 | LCSC [S] | | ~1 $ |
| **JLCPCB montaggio e pezzi SMD** | | ~47 $ | **~42 €** |
| Foro passante da TME (pot, 20 trimmer 3266, film, elettrolitici, regolatori, diodi, LED, zoccoli) | TME [V] / [S] | 103,68 € + IVA | **~137 €** con spedizione |
| BBD e clock (come sopra) | StompBoxParts [V] | | **~190 €** |
| **Totale B** | | | **~432 €, ~86 € a scheda** |

- Una tassa «Large Size» del montaggio JLCPCB esiste, ma l'importo non l'ho trovato: la scheda è
  lunga 280 mm [S].
- JLCPCB può saldare anche il foro passante: 0,0164 $ a punto, ~600 punti = ~10 $ [V], se i pezzi
  li ha o glieli mandi tu.

## Perché B costa meno

Il TLC2272 in DIP costa 3,89 € da TME, in SMD 0,32 $ da LCSC: 25 pezzi fanno ~90 € di differenza.
Il resto si compensa. Per A il vantaggio vero è un altro: niente fabbrica, niente stencil, e i
chip negli zoccoli si cambiano a mano.

## Verifica da terzi: funziona davvero?

| Servizio | Cosa controlla | Venditore | Prezzo |
|---|---|---|---|
| Revisione di schema e PCB da un ingegnere freelance | se il circuito sta in piedi: errori, datasheet, rischi | Fiverr, offerte «schematic and PCB review» [V] | 50-400 $; per audio analogico coi BBD la fascia alta, ~200-400 $ (180-360 €) [S] |
| Collaudo funzionale delle schede montate (FCT) | le prove che scriviamo noi: tensioni, tono all'uscita, FIRE | JLCPCB, «Functional Test Service» [V] | ~16 $ di ingegneria + ~8 $/ora; ~30 € per 5 schede [S] |
| Controllo di fabbricabilità (DFM) | solo se la scheda si può costruire, non se suona | JLCDFM, gratuito | 0 € |

- Fiverr: la qualità varia molto. Un'offerta da 50 $ ha una recensione che parla di un rapporto
  pieno di errori. Va scelto chi dichiara audio analogico.
- Il collaudo JLCPCB controlla solo quello che scriviamo nel piano di prova: dice se la scheda è
  montata bene, non se il colpo e l'eco suonano come nel banco web. Il piano lo scrivo io.
- Per tutti e tre i servizi schema e PCB escono dal progetto e vanno a terzi: lo decide Filippo.

## Fonti

- JLCPCB, calcolatore: https://cart.jlcpcb.com/quote (280 x 80, 4 strati, 5 pz, 2026-11-19).
- JLCPCB, listino del montaggio: https://jlcpcb.com/help/article/pcb-assembly-price
- JLCPCB, collaudo: https://jlcpcb.com/help/article/functional-test-service
- TME Italia: https://www.tme.eu/it/ (ricerche per codice, 2026-11-19).
- LCSC: https://www.lcsc.com (ricerche per codice, 2026-11-19).
- StompBoxParts: https://stompboxparts.com/integrated-circuits-ics-/v3102d---bbd-clock-ic e la
  pagina del V3205SD.
- Fiverr, revisioni: es. https://fiverr.com/beuinnovations/do-your-schematic-and-pcb-design-reveiw
- PCBWay, collaudo (prezzo solo su richiesta): https://www.pcbway.com/pcb_prototype/PCB_Assembly_Functional_Testing.html

Da verificare prima di comprare: il codice Alps orizzontale con le curve giuste (C 100k, B 250k e
500k potrebbero non esserci nella serie RK09L); il V3205SD è il V3205D del progetto o un altro
contenitore; un venditore europeo dei CoolAudio.

## Dove si risparmia (base: B, ~432 € per 5)

In ordine di risparmio. «Suono» dice se la scelta tocca la macchina: quelle le decide Filippo.

| # | Voce | Risparmio su 5 | Suono | Fonte |
|---|---|---|---|---|
| 1 | Una sola coppia BBD + clock per scheda: eco massimo ~205 ms invece di 410 | ~95 € | sì: TEMPO dimezzato (dec. 185, 193) | prezzi StompBoxParts [V], ritardo dal datasheet V3205D [V] |
| 2 | BBD e clock da un venditore europeo (niente spedizione dagli USA e IVA d'importazione) | ~20-40 € | no | [S]: venditore non ancora trovato |
| 3 | Trimmer 3266W (1,74 €) -> trimmer economici (Piher, o SMD montati da JLCPCB) | ~30 € | no: si tarano una volta | 3266W TME [V]; alternativi [S] |
| 4 | Pot Alps RK09L (1,41 €) -> Alpha da 9 mm | ~20-30 € | no; la sensazione della manopola un po' sì | Alps TME [V]; Alpha [S] |
| 5 | Tutto da un solo ordine (pot, elettrolitici, regolatori da LCSC; JLCPCB salda anche il foro passante a ~10 $) | ~15-25 € | no | saldatura JLCPCB [V]; prezzi LCSC del foro passante [S] |
| 6 | Spedizione JLCPCB lenta invece di UPS (31 $) | ~10-20 € | no | UPS [V]; spedizione lenta [S] |
| 7 | Buoni JLCPCB per i nuovi clienti (il calcolatore mostra «Save $30 / $20») | fino a ~25 € | no | calcolatore JLCPCB [V]; condizioni [S] |
| 8 | Revisione del progetto: niente Fiverr, prova e misura del primo esemplare noi | 180-360 € (se era in conto) | no; il rischio resta nostro | Fiverr [V] |
| 9 | Elettrolitici generici al posto dei Panasonic FR | ~3 € | no | [S] |
| 10 | Senza zoccoli DIP | ~1 € | no; un chip rotto non si cambia più a mano | TME [V] |

Senza toccare il suono (2-7, 9): ~100-170 € in meno, cioè ~265-330 € per 5 (~55-65 € a
scheda). Con la 1 si scende ancora di ~95 €, ma la macchina perde metà dell'eco.

Non conviene risparmiare: il circuito stampato a 2 strati (costa pochi dollari in meno e il
routing, oggi al limite, diventa più difficile) e gli op-amp diversi dal TLC2272 (le prove di
oggi valgono per lui).

## Eco più economico (BBD e clock: oggi 30,40 $ a scheda)

| # | Opzione | A scheda | Su 5 | Suono |
|---|---|---|---|---|
| 1 | Stessi chip da un venditore europeo | ~30 $ | -20-40 € [S] | niente |
| 2 | 4 V3208 (2048 stadi) + 2 V3102 | 22,40 $ [V] | ~-35 € | quasi niente; scheda da rifare, datasheet V3208 da leggere |
| 3 | 1 V3205 + 1 V3102, eco fino a ~205 ms | 15,20 $ [V] | ~-70 € | TEMPO dimezzato |
| 4 | 1 V3205 + 1 V3102, clock fino a 5 kHz | 15,20 $ [V] | ~-70 € | eco lunghi scuri, clock sotto il minimo del datasheet |
| 5 | PT2399, eco digitale | 0,89 $ (LCSC) [V] | ~-130 € | non è più un BBD (dec. 182) |
| 6 | Cloni MN3205 da AliExpress | ~2-4 $ [S] | ~-100 € | rischio di chip rimarcati |

Esclusa: un V3102 per due V3205 (il datasheet ne regge uno da 4096 stadi).
