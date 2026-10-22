# RISULTATI — fader mono che comanda un VCA (dec. 126, todo 129, 2026-10-22)

## Circuito (per canale CDJ e per ritorno FX, stereo)

```
fader MONO 100 mm, 10k lineare (qualunque modello, anche a carbone)
  ▼ cablato rovescio, 0…5 V dal riferimento LN (come il GAIN, cdj §3.2)
  ▼ SHAPER a diodi (famiglia sistema-shaper, 1 op-amp + 3 rami 1N4148)
  ▼ /10 → CV bipolare su EC− dei due VCA (sistema-vca-trim: partitore 1k/1k)
  ▼ VCA 2181 / V2181L lato L      VCA lato R   (trim di simmetria + coppia)
  ▼ I/V OPA1612 (sostituisce il buffer del fader) → anello XF → out driver
```

Il fader non porta l'audio: il tracking L/R ≤ 0,5 dB (dec. 59) lo danno i
due VCA trimmati in coppia (`docs/fase3/sistema-vca-trim.md`). Topologia
del canale invariata: CUE, send e filtro restano pre-fader; nei ritorni il
reroute resta pre-fader (fx-module §5).

## Curva del fader (`sim/shaper/shaper-fader.cir`, fit `sim/shaper/fader_fit.py`)

Law [PROVVISORIO, dec. 129: «come Pioneer DJM», la curva graduale; da sentire]: quadratica in ampiezza,
G = 40·log10(t), −12 dB a metà corsa. Valori E96: Rm 43,2k · ramo 1
68,1k / 357k · ramo 2 20,0k / 38,3k · ramo 3 976 / 1,33k (verso −5 V),
Rf 10k, OP1654. Il fit a 4 rami dava due rami uguali, qui fusi in uno.
Fondo corsa chiesto a −115 dB: il VCA si ferma al suo floor.

| Fader | Target | 20 °C | 35 °C | 50 °C |
|---|---|---|---|---|
| 97,5 % | −0,4 | −0,03 | −0,03 | −0,03 |
| 90 % | −1,8 | −0,07 | −0,07 | −0,07 |
| 77,5 % | −4,4 | +0,15 | +0,14 | +0,12 |
| 57,5 % | −9,6 | −0,14 | −0,24 | −0,35 |
| 45 % | −13,9 | +0,32 | +0,21 | +0,09 |
| 32,5 % | −19,5 | +0,73 | +0,25 | −0,25 |
| 20 % | −28,0 | +0,96 | +0,39 | −0,24 |
| 10 % | −40,0 | −0,5 | −5,3 | −11,0 |
| 0 % | muto | −102,7 dB | −111,0 dB | −119,5 dB |

(colonne di temperatura: errore in dB; ultima riga: attenuazione).
Dal 45 % in su l'errore resta entro ±0,35 dB a ogni temperatura; fino al
20 % entro ±1 dB. Sotto il 10 % il fader è quasi chiuso: errore di
qualche dB, inudibile. Fader chiuso: ≥ 102 dB di attenuazione.
Un'altra curva (−6 o −20 dB a metà corsa) = altri valori, stesso circuito.

## Rumore (fader aperto, VCA a 0 dB, −98 dBV da datasheet)

| Blocco | Prima (fader passivo) | Col VCA | Netlist |
|---|---|---|---|
| Canale CDJ, EQ al centro | −94,6 dBu A | **−92,9** | `sim/cdj/channel-noise-v04-fader.cir` |
| Canale, EQ tutte a zero | −104,8 | −97,0 | idem |
| Canale, EQ al massimo | −89,1 | −88,5 | idem |
| Un ritorno FX | −96,6 | **−94,1** | `sim/fx/fx-return-noise-fader.cir` (integrazione a 10 punti, ricalcolata anche sul vecchio log: −96,6 contro −96,4 del documento) |

Sistema a filtri OFF (docs/06 §10 con i due blocchi nuovi): 4 canali
−86,9 ⊕ 5-way −85,9 ⊕ 4 ritorni −87,8 ⊕ summing/master ≈ **−81,9 dBu
A-wtd, PASS 3,9 dB sul −78** (era −82,9 / 4,9). Con 4 filtri inseriti e
overdrive aperto circa −75,3 (era −75,5; condizione accettata, dec. 100).

## Alimentazione (`sim/system/psu-w1-fader.cir`)

+16 VCA e 8 shaper, meno i 16 buffer del fader tolti: caso peggiore
+100 mA per ramo (5,5 mA per VCA con I/V, tabella sistema-psu §1) →
1,91 A. W1 2×21 V 4,0 A a rete −10 %: corrente efficace 3,67 A (**92 %**,
era 88 %), raw minimo 23,7 V (era 23,9). L'LDO del box (±22,0 V) perde
~0,2 V di margine: resta in regolazione (margine MOSFET da ricontrollare
col box, era 1,56 V).

## VCA nel mixer

62 + 16 = **~78 chip** (+8 col crossfader); lotto d'acquisto ~95-105
pezzi con gli scarti dell'abbinamento. Trimmer: uno di simmetria per chip
come gli altri.

## Non fatto

- THD del VCA a fader aperto (modello lineare; datasheet 2181 grado C
  0,005 %, clone V2181L < 0,035 %): ora il segnale di canale passa da due
  VCA (GAIN e fader). Da misurare a banco.
- Box esterno con 1,91 A (margine MOSFET, calore): rifare `psu-box-w1-115`.
- Curva del fader: scelta di Filippo all'ascolto (G1-G3).
