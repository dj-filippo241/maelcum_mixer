# 5-WAY — LED di livello delle 5 vie (dec. 176 g, todo 291)

Versione v0.1, 2026-11-11. Stato: topologia [PROPOSTA di Claude, simulata];
soglie e somma L+R [PROVVISORIO, da confermare con Filippo: A24 in
`docs/02-questioni-aperte.md`]. Simulazione: `sim/five-way/led-livello-soglie.cir`,
risultati `sim/five-way/RISULTATI-led-livello.md`.

## 1. Requisito (dec. 176 g)

Un LED tricolore per ognuna delle 5 vie, SUPER compresa: verde = c'è segnale,
giallo = vicino al limite, rosso = satura. Sul pannello: un LED sotto il nome
della via, sopra il GAIN.

## 2. Punto di lettura

Le 5 vie esistono come segnali separati solo dentro la banca dei kill (§3 del
design doc del modulo). Il GAIN di ogni via è una cella parametrica in serie
sulla somma (§4), e GROWL e NASTRO lavorano sulla somma (§5bis). Un LED letto
nella banca non vedrebbe né il GAIN né il drive: col GAIN della via a +10 dB
il LED resterebbe verde mentre il modulo satura.

Quindi il LED legge **dopo il drive, alla presa del meter del modulo** (§5.6),
dove si sente il risultato. Una seconda banca, solo d'analisi, divide quel
segnale nelle 5 vie. È una banca da lettura: non torna nel segnale, non
aggiunge rumore all'uscita.

```
presa del meter L, R (dopo il drive, -6 dBu nominali interni)
  → sommatore invertente (L+R)/2 × 0,576 (20k + 20k, Rf 5,76k, 100p)
  → banco d'analisi Sallen-Key Butterworth agli incroci H (dec. 175)
       SUB   LP 60
       KICK  HP 60   + LP 250
       MID   HP 250  + LP 1200
       HIGH  HP 1200 + LP 8000
       SUPER HP 8000
  → rivelatore di picco per via (cella del metering: superdiodo, clamp
    anti-windup -1,5 V, hold 100n, release 3M = 0,3 s, buffer)
  → LED3 per via (cella del MIC, celle_micmono.led3: 4 comparatori LM339,
    latch del rosso 0,52 s, LED bicolore ad anodo comune, giallo = verde + rosso)
```

Il sommatore inverte: per un LED la polarità non conta (il rivelatore legge
il picco positivo; su musica i picchi sono simmetrici entro pochi dB).

## 3. Soglie [PROVVISORIO]

Un partitore solo sul +15 LN, comune alle 5 vie (E96, 0,1 %):

| Rete | Valore | Tensione | dBu interni | dBu all'uscita del modulo |
|---|---|---|---|---|
| +15 → VR | 127k | | | |
| VR → VY | 12,7k | 2,508 V (rosso) | +12 | **+18** |
| VY → VG | 12,4k | 1,259 V (giallo) | +6 | **+12** |
| VG → massa | 402 | 39,5 mV (verde) | -24 | **-18** |

VR, VY e VG con 100n verso massa. Latch: VTL = 2,5 V da 10k/10k sul +5 V.
+18 dBu è il picco di progetto dell'uscita del 5-way (gain-staging sheet):
rosso = il modulo è al suo tetto, oltre c'è il clip degli op-amp a ~+22 dBu.
Giallo 6 dB prima. Verde da -18 dBu: musica presente sulla via.
Ogni soglia si sposta cambiando una resistenza.

Simulato (RISULTATI §2): soglie entro ±0,4 dB al centro della via. Vicino a
un incrocio il LED si accende più tardi, quanto il banco abbassa quella
frequenza (SUPER a 10 kHz: 1,5 dB).

## 4. Valori del banco d'analisi (E96 e E12)

Passa-basso, guadagno 1: C1 = 2·C2 circa, f0 = 1 / (2π R √(C1 C2)).
Passa-alto, guadagno 1: Rgnd = 2·Rfb, f0 = 1 / (2π C √(Rfb Rgnd)).

| Cella | Valori | f0 calcolata | Simulata |
|---|---|---|---|
| SUB LP 60 | R 17,8k, C1 220n, C2 100n | 60,3 Hz | sì |
| KICK HP 60 | C 100n, Rfb 18,7k, Rgnd 37,4k | 60,2 Hz | no |
| KICK LP 250 | R 19,6k, C1 47n, C2 22n | 252 Hz | no |
| MID HP 250 | C 22n, Rfb 20,5k, Rgnd 41,2k | 249 Hz | sì |
| MID LP 1200 | R 19,6k, C1 10n, C2 4,7n | 1184 Hz | sì |
| HIGH HP 1200 | C 4,7n, Rfb 20k, Rgnd 40,2k | 1194 Hz | no |
| HIGH LP 8000 | R 13,3k, C1 2,2n, C2 1n | 8065 Hz | no |
| SUPER HP 8000 | C 1n, Rfb 14k, Rgnd 28k | 8038 Hz | sì |

Condensatori C0G/film. Le vie KICK e HIGH usano le stesse celle: non
simulate, numeri calcolati.

## 5. Conteggio per la scheda

| Blocco | Op-amp (sezioni) | Altri chip | Passivi e piccoli |
|---|---|---|---|
| Sommatore L+R | 1 | | 4 |
| Banco d'analisi | 8 | | 32 |
| Rivelatori ×5 | 10 | | 30 (Rcomp, 1N4148, 47p, 100n hold, 3M, clamp) |
| LED3 ×5 | | 5 × LM339 | 40 (750k, 1u, 10k, 1N4148, 2N7002, 2 × 1k, 100n) |
| Soglie e latch comuni | | | 10 |
| Disaccoppiamento | 5 × OPA1654 (20 sezioni, 1 libera) | | 10 |

Totale ~10 chip e ~126 passivi: **~136 impronte**, più 5 LED bicolori sulla
scheda comandi. È quasi una facciata intera di una 100 × 220. Va contato col
resto del 5-way quando si disegna la sua scheda (todo 270 per la scheda
comandi). Corrente: 5 × 2 × 2,8 mA = 28 mA sul +5 V nel caso peggiore, ~40 mA
sul ±15 LN per i 5 quad (~2 mA per sezione).

## 6. Limiti e scelte da confermare (A24)

- **Somma L+R.** Un suono solo su un lato legge 6 dB più basso; un suono
  in controfase non accende niente. Alternativa: banco e rivelatore per lato,
  coi due superdiodi sullo stesso hold (legge il più forte dei due): il banco
  e i superdiodi raddoppiano, ~+80 impronte.
- **Comparatori.** Offset del LM339 fino a 5 mV: la soglia del verde
  (39,5 mV) può spostarsi di circa ±1 dB fra una via e l'altra. Per un «c'è
  segnale» non conta.
- **Ballistica.** La stessa del metering (dec. 81): attacco < 1 ms, release
  0,3 s, rosso tenuto 0,52 s. Sul SUB a 40 Hz l'hold cala 0,7 dB fra due picchi:
  il LED non sfarfalla.
- **Banco.** Lo scarto vicino agli incroci è voluto: il LED dice quanto c'è
  in quella via, come il kill la taglierebbe.
