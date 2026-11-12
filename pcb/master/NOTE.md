# MASTER: note delle schede (bozza, 2026-10-28; giri del 2026-11-04 in fondo)

Stato al 2026-11-04 (todo 204 e 206): tre schede da 100 × 220, generate dal loro file.

| Scheda | File | Impronte | Esito | Audio A1/A2/A3/A4/A5 |
|---|---|---|---|---|
| segnale | `master-segnale.py` | 283 | **PASSA** (giro 13) | 28/33/28/1/0 |
| uscita L | `master-uscita.py L` | 155 | **PASSA** (giro 4) | 2/9/9/0/0 |
| uscita R | `master-uscita.py R` | 144 | **PASSA** (giro 2) | 2/9/9/0/0 |

Freerouting non dà lo stesso risultato a ogni giro: segnale 2 PASSA su 8 giri del 4/11 (i primi
col generatore senza le due opzioni nuove), uscita L 1 su 2 dopo la correzione di J4, R 2 su 2.
Valori dei componenti [PROVVISORIO]. A1 della segnale (28) sono i regolatori e i loro C: punto 5
di `pcb/NOTE-generatore.md`.

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
   ha solo blocchi ideali. **Simulata coi componenti il 2026-11-03** (todo 200,
   `sim/master-out/RISULTATI-mono-ms-comp.md`): il VCA + I/V NON inverte (datasheet THAT
   2181 Rev 03 p. 7), quindi Sv = +S e le uscite erano scambiate: ora U3B esce su LO_R e
   U4A su LO_L. Aggiunto 47p C0G sul 10k di M (separazione piatta fino a 20 kHz).
   Separazione −38 dB nel caso peggiore (errore di guadagno del VCA), rumore −96,4 dBu A.
5. **Tasto MONO**: a ritenuta verso +5 REF, aperto = stereo; RC 10k/100n (1 ms in salita,
   2 ms in discesa), stadio x2,36 (10,2k / 7,5k) e partitore 18,2k/1k = 0,615 V su EC− = −100 dB.
   Todo 288: prima inseguitore + 7,15k/1k, con l'op-amp al rail 1,88 V al pin (limite ±1 V); ora
   0,80 V (`sim/system/RISULTATI-ec-pin.md` §4).
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

## Giri del 2026-11-04 (todo 204 e 206)

### Scheda di segnale

Modifiche nel file, senza toccare il circuito:

1. **+5V e CTRL_GND fuori dal C96 della segnale** (a21-a24): nessun pezzo li usa. La scheda comandi
   li prende dalla J4 della scheda d'uscita L. CTRL_GND resta sui ritorni c16-c28.
2. **RAW±22 fuori** (a5-a8): nessun pezzo li usa; li univa solo un ponticello pin-pin del C96
   (giro 8: RAW+22 aperta).
3. **MASTER LEVEL e BOOTH LEVEL sul lato componenti.** Sul retro i trimmer a foro passante restavano
   in alto col blocco e i VCA e i partitori finivano 70-110 mm più in basso: LT_M e ECM_MR lunghe
   oltre 100 mm (rete di CV sensibile), ECM_MR aperta al giro 7. Per far posto: BUFFER [A][B][C][N]
   e VIE_TAP sul retro.
4. Piste di potenza: +-18 e +-15 LN a 0,4 mm (<= 0,15 A; 0,6 lasciava aperta -18V), CTRL_GND 0,4.
5. `d.link_pairs` e `d.fanout_more` (opzioni nuove del generatore, sotto).

| Giro | Modifica | Esito |
|---|---|---|
| 6 (agente prima) | +5V e CTRL_GND dalla J4 della L | PASSA alle 13:19 |
| 7 | stesso file, di nuovo | NON PASSA: ECM_MR (RV4-2/RV4-3) |
| 8 | LEVEL sul davanti, BUFFER e VIE_TAP sul retro | NON PASSA: RAW+22 (a5-a6) |
| 9 | senza RAW±22 | NON PASSA: isola di massa su C78 (pad senza via) |
| 10 | stesso file | NON PASSA: ECM_MR, ECM_BR (RV-2/RV-3), RAW-27 (a3-a4) |
| 11 | `link_pairs` su tutti i pad | NON PASSA: isola su C53; 11 falsi aperti fra pin SMD gemelli |
| 12 | `link_pairs` solo foro passante, `fanout_more` | DRC 0 aperti; Freerouting conta RV8-2/3 aperta (falso) |
| 13 | il conto ignora le piste gemelle | **PASSA** |

**Finding: Freerouting non unisce due pad vicini della stessa impronta e della stessa rete.**
Cursore e capo di un trimmer (RV4-2/3, RV8-2/3), pin doppi del C96 (a3/a4, a5/a6, a21/a22,
a23/a24 dei giri 1-5), J4 della L. Ogni giro ne lascia aperti alcuni a caso; sulla J4 sempre.
Rimedio nel generatore: una pista dritta prima di Freerouting (`d.link_pairs`).

**Isole di massa.** Un pad SMD di massa senza via di fanout («senza posto libero») si collega
solo con la colata del suo strato; se il routing la spezza resta un'isola (C78, C53). Con
`d.fanout_more` i pad senza via scendono da 15 a 5. I 5 restano un rischio a ogni giro.

### Schede d'uscita (todo 206)

`master-uscita.py L|R` (bozza dell'agente prima, controllata contro master-out §3.3-3.8 e
`RISULTATI-mute-ctrl.md`): una per lato, ognuna col suo C96 (a9-a26, c9; la L anche a5-a6
RAW+22 e c17 AC_OK, dec. 143). Uguali salvo il mute controller [L] e il relè del REC, solo sulla L;
la R comanda i suoi relè dalla GLOBAL_MUTE (c9).

**J4 della L** (+5V e CTRL_GND verso la scheda comandi): con i pin 1-2 a +5V e 3-4 a CTRL_GND
Freerouting lasciava aperte TUTTA +5V e TUTTA CTRL_GND (giri 1-2, anche con J4 spostata).
Prova sul `.dsn`: senza J4, o coi pin alternati (+5V, CTRL_GND, +5V, CTRL_GND), 0 aperti.
Ora i pin sono alternati. La scheda comandi va disegnata con la stessa piedinatura.

| Scheda | Giro | Esito |
|---|---|---|
| L | 1 (agente prima), 2 (J4 spostata a x 50) | NON PASSA: +5V, CTRL_GND |
| L | 3 (pin di J4 alternati) | NON PASSA: -18V (12 collegamenti) |
| L | 4 (stesso file) | **PASSA** |
| R | 1 (agente prima, file vecchio), 2 | **PASSA** |

Sulle uscite restano 4 «violazioni preesistenti» che Freerouting segnala: via di fanout di massa
troppo vicine ai pad -18V dei 100n (C10, C12, C14, C17 sulla L). Il DRC di KiCad non le conta.
Probabile causa del giro 3 della L. Da guardare nel fanout del generatore.

### Cosa resta

1. Clip detector delle uscite: soglia e tenuta scritte a mano (NOTA, «da simulare»): simulare.
2. Scheda comandi: fatta (sezione sotto). Schedina dei connettori: da scrivere.
3. Pinout di MJE340/MJE350 sull'impronta BD139/BD140 («da verificare» nel file): dal datasheet.
4. A1 della segnale: regolatori coi C a più di 10 mm.
5. Nessuna domanda di design per Filippo da questi giri: nessuna modifica al backplane né al pannello.

## Scheda comandi (todo 270, 2026-11-10/11)

`master-comandi.py`, file in `comandi/`, celle in `pcb/tools/comandi.py` (nuovo: pot, fader,
levette, bottoni con luce, barre LED con LM3915, jack; serve anche alle schede comandi che mancano).
242 × 44 mm, parallela al pannello (450 × 48) da x 104 a x 346 mm, retta dai dadi dei due pot.
Posizioni da `docs/pannelli/coordinate.json`, modulo «master» (dec. 176 f).

- Pezzi: BOOTH e MASTER (pot singoli lineari 10k, manopola rovescia per lo shaper; MASTER con
  scatto al centro, dec. 139), tasto MONO con luce, due barre da 20 LED con 2 LM3915 per lato
  (VREFA 5,000 V e VREFB 1,581 V, da +24 a −33 dBu, sistema-metering.md §3 e §5).
- Cavi: J1 2×10 verso J3 della segnale (ordine letto da `master-segnale.py`); J2 2×2 con +5V e
  CTRL_GND dalla J4 dell'uscita L, pin alternati.
- **PASSA** al 1o giro (2026-11-11): 60 componenti, 57 reti, 0 aperti, ERC pulito, DRC 0 errori
  (38 silk_overlap, 76 silk_over_copper, 10 net_conflict attesi).

NOTA della scheda comandi (da verificare):

1. ~~A1: i 100n dei quattro LM3915 fino a 77 mm dal chip~~ **Corretto il 2026-11-11**: la cella
   `meter` mette il 100n accanto ai pin 2-3 del chip fissato. V+ (pin 3) a 3,2 mm dal 100n; restano
   in A1 i pin 9 (MODE, a +5V: non è un'alimentazione) a ~15 mm. Rigenerata: **PASSA**.
2. CLIP_L e CLIP_R arrivano sul cavo ma il pannello non ha un LED di clip: restano liberi.
3. Pinout dell'LM3915 dal simbolo KiCad LM3914N (stesso DIP-18): da verificare sul datasheet TI.
4. Corrente dei LED con 6,2k: formula del datasheet da verificare (~2 mA, metering §1).
5. Bottone del MONO: impronta NKK GW12LJP segnaposto, pinout da rifare col pezzo scelto.

Scheda di segnale rigenerata il 2026-11-11 (todo 288: stadio x2,36 del MONO, 2 resistenze in più):
**PASSA**, 285 componenti; via_dangling 7 → 8, A2 35 → 36.

## C96 a 5,3 mm dal bordo (2026-11-12, todo 303)

Il C96 maschio sta a y = H - `backplane.C96_DAL_BORDO` (7,84: fila b; fila a a 5,3 mm dal bordo,
disegno Harting e riga «Board edge» dell'impronta). Prima y = H - 6,5 metteva la fila a a 3,96 mm.
Esito: segnale, uscita L e uscita R PASSA al primo giro (A2 uscita L 9 -> 10, uscita R 9 -> 11).

Verificato in: KiCad (ERC, DRC). Live: no.
