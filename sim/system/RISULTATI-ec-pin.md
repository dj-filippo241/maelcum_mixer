# Pin EC− del VCA: tensione massima (todo 281, 2026-11-10)

Netlist: `sim/system/ec-pin-limite.cir` (.dc, op-amp con clamp a rail − 0,2 V, rail ±15,5 V).

**Limite.** THAT 2181 datasheet Rev 02, Absolute Maximum Ratings: «Maximum ΔEc, EC+ − (EC−): ±1 V»
(letto sul PDF di thatcorp.com il 2026-11-10). Il pin EC+ sta a massa: il pin EC− non deve uscire
da ±1 V. Oltre: «may cause permanent damage».

## 1. Oggi (celle_vca.py fino al 2026-11-09)

Shaper → stadio del partitore x(−1/5) (10k/2k) → partitore 1k/1k (canale: 1k/1,5k con 3,01k dal dip).

| Caso | Pin EC− |
|---|---|
| Uso normale, fader da aperto a chiuso | 0…0,65 V |
| **Canale: fader chiuso e dip della levetta (dec. 163)** | **1,38 V: oltre il limite in uso normale** |
| Guasto del +REF5 (LM4040 aperto), fader chiuso | 1,53 V (2,26 V col dip) |
| Stadio del partitore al rail (Rf aperta, accensione) | ±7,7 V (8,4 V col dip) |

Il caso del dip non è un guasto: ogni scatto della levetta HPF/OFF/LPF col fader giù porta il
pin a 1,38 V per qualche millisecondo.

## 2. Correzione [PROVVISORIO fino al prototipo]

- Stadio del partitore x(−1,916): 9,76k / 18,7k.
- Partitore 18,2k / 1,00k (D = 19,2). Lato R: 17,4k + trimmer 2k / 1,00k (scala −6…+4 %).
  Offset di coppia: 2,7 MΩ (±5,3 mV, come prima).
- Dip del canale: 4,99k dal DIPCV al nodo di somma dello shaper del fader (prima 3,01k su ogni pin).
  Il dip satura lo stadio del partitore: la saturazione fa da limite.
- Smoothing del FX-RET: 56n sulla Rf da 18,7k (1,05 ms; prima 470n sul 2k, 0,94 ms).

| Caso | Pin EC− |
|---|---|
| Legge, pot a 1 / 2,5 / 4 / 5 V | 0,0231 / 0,0649 / 0,1660 / 0,6488 V (oggi 0,0232 / 0,0650 / 0,1664 / 0,6505: −0,26 %) |
| Fader chiuso e dip | 0,797 V |
| Dip a fader aperto | 0,797 V (con rail −3 % e swing −1 V: 0,71 V; serve ≥ 0,61) |
| Guasto del +REF5 | 0,797 V |
| Stadio al rail | ±0,797 V |

−0,26 % sulla legge: 0,26 dB a −100 dB, 0,04 dB a −15 dB, dentro il trim di law.
Con lo stadio al rail negativo il VCA si apre al massimo (+130 dB nominali): l'uscita satura, ma il
chip non si rompe. È un guasto, come oggi.

Il dip ora arriva a −100 dB un po' prima (la rampa satura verso l'85 %) e riparte un po' dopo.
**Da risimulare** con la logica vera (`filtsel-dip.cir`, pcb/canale/NOTE.md punto 2).

## 3. Altri pin EC− da guardare (non corretti qui)

- MONO del master (`master-segnale.py`): follower → 7,15k / 1k. Follower al rail: 1,8 V al pin.
  Solo guasto.
- MUTE del MIC (`mic.py`): LIM 1k, MUTE_CV 2k, 1k a massa. Inseguitore del MUTE al rail: ~3 V.
  MUTE a 2,5 V col limiter che lavora: il pin si somma (stima mia: fino a ~0,9-1 V con 20-30 dB
  di limitazione). Da simulare.
- Misto: la cella CV usa già il partitore 15k/1k (misto/sim/RISULTATI-cella-cv.md §2).

File cambiati: `pcb/tools/celle_vca.py` (shaper, law_trim), `pcb/canale/canale.py` (dip),
`pcb/master/master-segnale.py`, `pcb/fx-ret/fx-ret.py`, `pcb/fx-ret/fx-ret-reroute.py`.

Verificato in: Python no / LTspice sì (.dc) / Live no (non serve: nessun effetto sonoro).
