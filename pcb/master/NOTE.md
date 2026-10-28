# MASTER: note delle schede (bozza, 2026-10-28)

Stato: `master-segnale.py` scritto, primo giro senza piste: **NON PASSA**. Non committato
come scheda finché non passa (regola delle PCB).

## Finding: la scheda di segnale da sola non sta in 100 × 165 mm

Primo giro (`--no-route`, board 150 × 165): 282 impronte; il piazzamento chiede **200 mm in
più di larghezza**, cioè ~350 × 165. Il FX-SEND porta 120 impronte su 100 × 165. La stima
della dec. 140 («~350-400 componenti per tutto il master») era bassa: la sola scheda di
segnale ne ha 282, contando trim, ponticelli, disaccoppiamenti e regolatori.

Misure dei pannelli (`docs/pannelli/coordinate.json`): FX-SEND 36 × 87 mm, MASTER 96 × 93.
Le schede stanno in verticale sotto il pannello (FX-SEND: 100 × 165). Sotto 96 mm di
pannello entrano più schede verticali affiancate. Strada da proporre a Filippo: il master
come pacco di 4-5 schede verticali da ~100 × 165 (segnale divisa in 2-3, uscita in 2),
pannello invariato. Va rivista la dec. 140 (che dice «due schede»): decide Filippo.

## Scelte NOTA (non nei documenti)

1. **AC_OK su c17** del C96 (`backplane.py`, `sistema-backplane.md` §5): pin libero.
2. **VCA, resistenza del pin V−**: 6,19k verso −18 V (datasheet: 5,1k a −15 V, 2,4 mA).
3. **Stadio del partitore** dopo lo shaper: invertente ×(−1/5) (10k/2k), poi 1k/1k: CV al
   pin = uscita dello shaper / 10, come `RISULTATI-fader-vca.md`. Inverte anche il segno
   (shaper negativo = taglio, EC− positivo = taglio).
4. **Matrice MONO**: M = −(L+R)/2 (20k, 20k, 10k), S = (L−R)/2 (differenziale 20k/10k),
   VCA su S con I/V 20k, L' = −(M+Sv), R' = Sv − M (differenziale 20k). `mono-ms.cir`
   ha solo blocchi ideali: **da simulare coi componenti** (separazione, rumore, polarità).
5. **Tasto MONO**: a ritenuta verso +5 REF, aperto = stereo; RC 10k/100n (1 ms in salita,
   2 ms in discesa), partitore 7,15k/1k = 0,613 V su EC− = −100 dB.
6. **Riferimenti ±5 V**: LM4040-5,0 da +15 LN (1k5) + follower; −5 V = invertente 10k/10k.
7. **Uscite verso il backplane** (MON, INS_SEND, VIE_TAP, REC): follower + 47 Ω.
8. **Pad del REC**: 6,81k in serie, shunt 3,16k (−10 dB) o 757 Ω (−20 dB) a ponticello;
   0 dB = ponticello chiuso di serie (dec. 63).
9. **Meter**: guadagno 10k/4,02k = 0,287; vrefB con 4,64k (E96) = 1,585 V.
10. **LT3045 / LT3094**: pinout preso dal simbolo KiCad (LT3045xMSE, LT3093xMSE). **Da
    verificare sul datasheet** (analog.com non si scarica: via radiolocman). PG libero,
    PGFB a massa, VIOC libero: da verificare.

## Errori del primo giro

- Corretti nel file, non ancora rigenerati: pin V− del VCA come `passive` (ERC
  power_pin_not_driven ×5); `RECB_` rinominata `RECD_` (refuso sospetto con `REC_`).
- Aperti: `footprint_symbol_mismatch` sui 6 ponticelli JP (da capire); pin liberi di D5
  (LM4040 NC), U42 (PG) e U43 (PG, VIOC) contati come net_conflict.
