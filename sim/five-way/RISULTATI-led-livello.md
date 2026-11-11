# RISULTATI — LED di livello delle 5 vie (dec. 176 g, todo 291)

Data: 2026-11-11. Design: `docs/fase2/five-way-led-livello.md`.
Netlist: `led-livello-soglie.cir` + celle `led-livello.inc` (LTspice 26.0.2,
`.tran 3,1 s` a passo 2 us, 145 s).

## 1. Cosa si misura

Quattro catene complete, ognuna col suo generatore: presa L e R del meter
(-6 dBu interni) → sommatore (L+R)/2 × 0,576 → banco d'analisi Sallen-Key
agli incroci H → rivelatore di picco (cella del MIC) → LED3 (LM339 + LED
bicolore, latch del rosso). Il livello del seno sale a tratti di 5 dB/s
attorno alle tre soglie. Si legge il livello (dBu interni, seno) a cui la
corrente del LED passa 1 mA.

| Catena | Frequenza | Banco | Perdita del banco a quella frequenza (calcolo) |
|---|---|---|---|
| a SUB | 40 Hz | LP 60 Hz | -0,77 dB |
| b MID | 550 Hz | HP 250 + LP 1200 | -0,41 dB |
| c SUPER | 10 kHz | HP 8 kHz | -1,51 dB |
| d MID senza clamp | 550 Hz | come b | -0,41 dB |

## 2. Soglie misurate (dBu interni; attese -24 / +6 / +12)

| Catena | Verde acceso | Giallo (rosso col verde) | Rosso (verde spento dal latch) |
|---|---|---|---|
| a SUB 40 Hz | -23,51 | +6,61 | +12,61 |
| b MID 550 Hz | -23,78 | +6,30 | +12,29 |
| c SUPER 10 kHz | -22,14 | +7,61 | +13,59 |
| d MID, senza clamp | -23,78 | +6,27 | +12,30 |

Scarto meno la perdita del banco (errore del rivelatore e dei comparatori):
SUB -0,28 / -0,16 / -0,16 dB; MID -0,19 / -0,11 / -0,12 dB; SUPER +0,35 /
+0,10 / +0,08 dB. Tutto entro ±0,4 dB. Lo scarto che resta è la forma del
banco: un tono vicino a un incrocio accende il LED più tardi, come lo
sentirebbe la via.

Riferite all'uscita del modulo (make-up +6 dB): **verde -18, giallo +12,
rosso +18 dBu** [PROVVISORIO]. +18 dBu è il picco di progetto dell'uscita
del 5-way (gain-staging sheet, riga «5-way OUT»).

## 3. Il guasto della bozza del 10/11 era nel modello

Bozza del 10/11: MID senza giallo (verde spento dal latch a -4,4 dBu),
SUPER mai acceso, SUB acceso già all'avvio. Causa: la macro del superdiodo
(`OPDETC`, copia di `OPDET` di `sim/meter/`) fermava con `limit()` solo
l'uscita. Lo stato del polo interno correva a ~-1e4 V nella mezz'onda
negativa e tornava in millisecondi: l'hold restava a poche decine di mV
anche a +12 dBu. Correzione in `led-livello.inc`: stato fermato ai limiti
dell'uscita con due diodi ideali, ingresso limitato a ±1e5 V (slew ~12 V/us,
l'OPA1654 ne fa 10). Le misure «RISE» partono dopo 0,3 s (`TD=0.3`): il
verde dell'avvio non conta più.

Conseguenza per `sim/meter/` e `sim/system/meter-*.cir`: la macro `OPDET`
ha lo stesso difetto. I loro numeri restano validi perché sono misurati a
fondo scala (burst da 5 Vp) o con `.dc`. Una prova del meter a livello basso
(segmenti in fondo alla barra) va fatta con la macro di `led-livello.inc`.

## 4. Clamp sì o no

Catena d (cella del MIC com'è disegnata, senza clamp: l'op-amp scende al
rail negativo) e catena b (clamp a -1,5 V) danno gli stessi numeri entro
0,03 dB. La macro però non simula il recupero dalla saturazione dell'op-amp
vero: per il 5-way si tiene il clamp a -1,5 V del metering
(`docs/fase3/sistema-metering.md` §2), che costa un 1N4148 per via.

## 5. Limiti

- KICK (HP 60 + LP 250) e HIGH (HP 1,2k + LP 8k) non sono simulati: stesse
  celle, valori calcolati nel design doc §4.
- Comparatori ideali (offset zero). LM339: offset 2 mV tipico, 5 mV
  massimo (TI SLCS006). Sulla soglia del verde (39,5 mV) il caso peggiore
  sposta l'accensione di -1,2 / +1,0 dB; sulle altre meno di 0,04 dB.
- Somma (L+R)/2: un suono solo su un lato legge 6 dB più basso; un suono
  in controfase non accende niente.
