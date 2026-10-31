# MASTER: note delle schede (bozza, 2026-10-28)

Stato: `master-segnale.py` scritto, 100 × 220 coi due lati (dec. 142): **NON PASSA** (sotto). Non committato
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

## Giri a 100 × 220 coi due lati (dec. 142, 2026-10-28)

I 282 componenti ci stanno: MONO, LEVEL e meter sul retro, In2 come strato di piste.
Tre giri, tutti NON PASSA per le stesse reti: le alimentazioni che attraversano la scheda
dal C96 (in basso) ai connettori verso le altre schede.

| Giro | J2 (uscita) | Aperte |
|---|---|---|
| 1 | bordo destro, a metà | SETP; piste a 0,28 mm dal bordo (corretto: fascia di 0,8 mm) |
| 2 | bordo destro, a metà | SETP, +5V, CTRL_GND (0,8 mm, ~200 mm di corsa) |
| 3 | in alto accanto a J3 | SETP, +5V, CTRL_GND (0,5 mm), RAW±26 |

Freerouting: 13 minuti di CPU per giro, fino a 3 ore di orologio a macchina carica.
Giri del 2026-10-29, dopo la dec. 143 (alimentazioni delle uscite dal loro C96, J2 2x7 solo audio e CLIP):

| Giro | Modifica | Aperte |
|---|---|---|
| 4 | J2 senza alimentazioni, SETP 0,3 mm | SETP, +5V, CTRL_GND (12 collegamenti) |
| 5 | reti sottili con via 0,8/0,4 e distanza 0,2 | SETP 2, +5V 2, CTRL_GND 3; 3 errori nuovi di distanza |

Restano aperti anche collegamenti fra pin vicini del C96 (a21-a22, a23-a24) e fra R7, C11 e U42:
non è spazio. Da capire prima di un altro giro (ripartire da una sessione pulita). Il cambio
delle vie sottili in `pcbgen.py` non è ancora provato sul FX-SEND.

Strade scritte il 2026-10-28 (la 1 è diventata la dec. 143):

1. **Le schede d'uscita prendono l'alimentazione dal backplane** con un connettore loro
   (RAW±26, RAW±27, +5V, CTRL_GND). Sulla scheda di segnale resta solo l'audio verso J2.
   Tocca il backplane (slot del master): da proporre a Filippo.
2. Altrimenti J2 in basso accanto al C96 (alimentazioni corte) e solo +5V/CTRL_GND fino a J3.
3. SETP (LT3045, MSOP passo 0,65): pista ≤ 0,3 mm come le reti TSSOP.

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
10. **LT3045 / LT3094**: pinout verificato il 2026-10-31 sui datasheet Rev. B (LT3045 p. 12-13,
    LT3094 p. 15; copie da rlocman.ru). Il simbolo KiCad era giusto. Errore trovato: PGFB era a
    massa. Con PGFB sotto la soglia il fast start-up resta acceso (2 mA nel SET invece di 100 uA) e
    l'uscita va in dropout: niente ±15 LN. Ora PGFB va a IN (+18 / −18), come vuole il datasheet
    senza PG. PG libero, ILIM a massa, EN/UV a IN, VIOC libero: confermati. Pad esposto: GND nel
    LT3045, IN nel LT3094.

## Errori del primo giro

- Corretti nel file, non ancora rigenerati: pin V− del VCA come `passive` (ERC
  power_pin_not_driven ×5); `RECB_` rinominata `RECD_`, poi `DRVREC_` (il controllo dei refusi la confondeva con `REC_`).
- [CHIUSO 2026-10-28] `footprint_symbol_mismatch` sui 6 ponticelli JP: l'impronta del ponticello a stagno è fuori distinta, il simbolo no. Ora il generatore li tiene fuori da tutte e due.
- Aperti: pin liberi di D5
  (LM4040 NC), U42 (PG) e U43 (PG, VIOC) contati come net_conflict.
