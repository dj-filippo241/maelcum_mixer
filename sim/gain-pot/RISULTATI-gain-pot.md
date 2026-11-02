# RISULTATI — GAIN con pot doppio al posto dei VCA (questione A22, todo 219, 2026-11-02)

Domanda: il GAIN dei canali (−∞…0…+10 dB) e dei ritorni FX (−∞…0…+20 dB)
può usare un pot doppio lineare selezionato invece di 2 VCA per lato,
come l'EQ (dec. 107)? Requisiti: tracking L/R ≤ 0,5 dB (SPECIFICA, GAIN
del canale; per il ritorno si assume lo stesso), detent a 0 dB, rumore non
peggiore.

## Due circuiti candidati

```
T1  PARTITORE CARICATO + AMPLI (1 op-amp per lato)
    in ── pot 10k lin ──┬── massa         Rl dal cursore a massa: la "resistenza di legge"
              cursore ──┴── Rl ── massa
              cursore ──► non invertente xA ──► out
    canale:  Rl 4,30k, A = 3,15 (2,15k/1k)
    ritorno: Rl 625 Ω, A = 5 (4,02k/1k; il buffer d'ingresso vale già 2)

T2  POT IN RETROAZIONE + STADIO K (2 op-amp per lato, polarità diritta)
    in ── Ra ── pista lato ingresso ── cursore (massa virtuale) ── pista lato uscita ── out1
    out1 ──► invertente xK ──► out
    canale:  Ra 8,66k, K = 2,72 (2k/5,44k)
    ritorno: Ra 1,24k, K = 0,625 (3,24k/2k)
```

Il guadagno di T2 dipende dal rapporto fra le due parti della pista, quasi
non dalla resistenza totale. Quello di T1 dipende anche da R/Rl.

Calcolo: `sim/gain-pot/gain_pot.py`. Rumore: `gain-pot-noise-canale.cir`
(copia di `sim/cdj/channel-noise-v04-fader.cir`, integrato con
`sim/mic/noise_total.py`) e `gain-pot-noise-ritorno.cir` (copia di
`sim/fx/fx-return-noise-fader.cir`, integrato con `noise10.py`). In
entrambi `top 0` = VCA di riferimento, `1` = T1, `2` = T2.

## 1. Curva della manopola: qui il pot CAMBIA il gesto

| Posizione | VCA oggi (canale) | T1 canale | T2 canale | VCA oggi (ritorno) | T1 ritorno | T2 ritorno |
|---|---|---|---|---|---|---|
| 5 % | −90 | −16,9 | −22,5 | −40 | −10,9 | −24,7 |
| 10 % | −80 | −11,7 | −16,2 | −35,6 | −7,7 | −18,3 |
| 20 % | −60 | −6,7 | −9,7 | −26,7 | −5,0 | −11,4 |
| 30 % | −40 | −3,9 | −5,6 | −17,8 | −3,2 | −6,8 |
| 40 % | −20 | −1,8 | −2,6 | −8,9 | −1,7 | −3,2 |
| 50 % (detent) | 0 | 0 | 0 | 0 | 0 | 0 |
| 60 % | +2 | +1,7 | +2,2 | +4 | +1,9 | +3,1 |
| 70 % | +4 | +3,4 | +4,3 | +8 | +4,1 | +6,3 |
| 80 % | +6 | +5,3 | +6,2 | +12 | +7,0 | +9,8 |
| 90 % | +8 | +7,4 | +8,1 | +16 | +11,3 | +14,0 |
| 100 % | +10 | +10 | +10 | +20 | +20 | +20 |

(dB; colonne «VCA oggi» = curva del prototipo, `proto-max/coefficienti/canale.py` e `fx.py`.)

Metà destra: il pot segue bene la curva di oggi (T2 entro 0,3 dB sul
canale; sul ritorno più lento fino all'80 % e poi rapido).

Metà sinistra: tutt'altro gesto. Oggi il GAIN di canale, sotto il centro, è
quasi un fader: a ore 11 sei già a −20 dB, a ore 10 a −40. Col pot la metà
sinistra diventa un trim: a ore 11 togli 2-3 dB, a ore 9 circa 6-10 dB, e
il silenzio arriva solo negli ultimi 5-10 % della corsa. È il gesto dei
trim dei mixer DJ comuni (aggiustare un disco troppo caldo di qualche dB),
non quello di oggi.

Non si può copiare la curva di oggi col pot: il tracking peggiora in
proporzione alla pendenza (la curva di oggi scende di 2 dB per ogni 1 % di
corsa sotto il centro; col 2 % di differenza fra le piste fanno 4 dB fra L
e R). Scelta musicale: è di Filippo.

## 2. Tracking L/R

Modello: le due piste del pot doppio differiscono per posizione (dx, per
lato, segni opposti = caso peggiore) e per resistenza totale (dR fra le
piste). Tre livelli: stretti (dx 0,5 %, dR 0,5 %), «come dec. 107»
(dx 1 % per lato = 2 % fra le piste, dR 2 %), non selezionati (dx 3 %, dR 10 %).

| Caso | Al detent | Sopra il detent (max) | Fascia ≤ 0,5 dB sotto il detent |
|---|---|---|---|
| Canale T1, stretti | 0,19 | 0,29 | fino a −9,0 dB |
| Canale T1, dec. 107 | 0,41 | 0,57 (ultimo 10 %) | fino a −3,4 dB |
| Canale T2, stretti | 0,27 | 0,27 | fino a −9,5 dB |
| Canale T2, dec. 107 | 0,59 | 0,59 | nessuna |
| Ritorno T1, stretti | 0,21 | 1,37 (verso +20) | fino a −8,2 dB |
| Ritorno T2, stretti | 0,32 | 0,80 (verso +20) | fino a −10,4 dB |
| Ritorno T2, dec. 107 | 0,66 | 1,63 | nessuna |
| Qualunque, non selezionati | 1,4-2,0 | 1,7-6,3 | nessuna |

(dB, errore L−R nel caso peggiore.)

Lettura:
- Canale: il requisito ≤ 0,5 dB regge da circa −9 dB a +10 dB solo con pot
  selezionati stretti (0,5 % fra le piste). Con la selezione pensata per
  l'EQ (2 %) T1 sta a 0,41 al detent e sfora appena verso +10.
- Ritorno: +20 dB di corsa sono il doppio del canale. Verso fine corsa
  nessuna selezione realistica tiene 0,5 dB (T2 stretti: 0,8 dB al 100 %,
  0,51 al 90 %). Fra −10 e +16 dB T2 stretti regge.
- Un trimmer al centro (come dec. 107) azzera l'errore al detent, non
  quello lontano dal centro.
- Il VCA oggi tiene ≤ 0,5 dB su tutta la corsa coi trimmer
  (`docs/fase3/sistema-vca-trim.md`). Il pot no: la differenza sta tutta
  nella selezione, che va misurata a banco (quanti pot servono per
  trovare coppie al 0,5 %).

Detent assoluto (fra un canale e l'altro, tolleranza ±20 % della pista):
T1 canale −0,62 dB, T1 ritorno −1,29 dB, T2 canale +0,97 dB, T2 ritorno
+0,29 dB. Il VCA oggi è esatto al detent (trim). Col pot servono pot a
tolleranza stretta o una resistenza scelta a banco.

## 3. Rumore (GAIN al detent, stessi netlist del riferimento)

| Blocco | VCA | T1 | T2 |
|---|---|---|---|
| Canale CDJ, EQ al centro | −92,9 dBu A | **−94,5** | −94,3 |
| Un ritorno FX | −93,9 dBu A | **−96,1** | −96,3 |

Il riferimento del canale coincide col documento (−92,9). Quello del
ritorno esce −93,9 contro −94,1 di `RISULTATI-fader-vca.md`: stesso
netlist, regola di integrazione a 10 punti diversa; il confronto qui usa la
stessa regola per tutte e tre le colonne.

Sistema a filtri OFF (docs/06 §10 coi blocchi nuovi): −81,9 → **−82,9 dBu
A-wtd** (PASS 4,9 dB sul −78; 4 canali −88,5, 4 ritorni −90,0).

## 4. Altro da sapere

- **Fruscio della manopola.** Col VCA il pot porta solo la tensione di
  comando: sporco e usura non si sentono. Col pot l'audio passa dal
  cursore: un pot sporco o consumato gracchia quando lo giri. Vale già per
  l'EQ (dec. 107). Serve zero continua sulla pista (in T2 il cursore sta a
  massa virtuale: solo l'offset dell'op-amp; in T1 l'offset del buffer).
- **Headroom.** Canale: invariato (il partitore abbassa prima dell'ampli).
  Ritorno T2: il primo stadio lavora 4 dB sopra l'uscita al detent, sotto
  il buffer d'ingresso.
- **Errore trovato fuori dal GAIN (vecchio).** Il buffer d'ingresso del
  ritorno ha guadagno 2. `fx-module.md` §4 dà «+18 dBu = 6,9 Vp»: è
  l'errore del todo 125. +18 dBu = 8,70 Vp, ×2 = 17,4 Vp su ±18 V: al
  limite o oltre (macro a ±16,5 V). La tolleranza +18 dBu del ritorno va
  ricontrollata con o senza A22.
- **Componenti.** T1 = 1 op-amp per lato (prende il posto dell'I/V del
  VCA), T2 = 2. Risparmio di A22 invariato (16 VCA, ~48 trimmer, 8 shaper).

## Conclusione

Rumore: il pot vince (−1,6 dB sul canale, −2,2 sul ritorno). Tracking:
regge ≤ 0,5 dB solo con pot selezionati stretti e solo dal −10 dB in su;
sul ritorno non regge verso +20. Curva: la metà sinistra diventa un trim,
non più un quasi-fader. Se Filippo vuole la metà sinistra di oggi, il pot
non basta.

Proposta se Filippo dice sì: T1 sul canale (un op-amp, migliore al
detent), T2 sul ritorno (migliore verso +20, quasi indifferente alla
tolleranza della pista). [PROVVISORIO: dipende dalla selezione misurata a
banco.]
