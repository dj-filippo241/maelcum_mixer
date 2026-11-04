# MIC, scheda principale v0.1-bozza (2026-11-04, todo 30)

Schema e distinta del modulo MIC (dec. 97, 111, 145), scritti col generatore. Fonte unica:
`mic.py`; le celle comuni col MONO stanno in `pcb/tools/celle_micmono.py`.

Rigenerare (pochi secondi; senza `--solo-schema` anche il PCB, ~4 minuti):

```bash
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 pcb/mic/mic.py --solo-schema
```

## Stato

- **SCHEMA PASSA**: 131 reti, nessuna con un pin solo; schema = netlist nei due sensi; ERC 0
  errori, 1 avviso voluto («VSS non a massa» sull'ADG1434, come il FX-SEND).
- **PCB: non generato.** 204 pezzi in distinta (206 impronte coi fori). Una 100 × 220 ne porta
  ~160 su un lato: servono i due lati (`d.side = "B"` sui blocchi SMD, dec. 142) prima del giro
  con Freerouting.
- Distinta: `bom.csv`. Silicio: OPA1612 ×3, OPA1654 ×5, V2181L ×1, ADG1434 ×1, LM339 ×1,
  LT3045 + LT3094, LM317 + LM337, 78L15 + 79L15, 1N4148W ×13. Coincide con la §8 del design
  doc più la REV della dec. 145.

## Catena e polarità

XLR (J3) → ferrite + 100 pF verso CHASSIS → 10 Ω + clamp → INA +30,05 dB (U1) → differenziale
(U2, caldo sull'ingresso −) → passa-alto 60 Hz → stadio 2 (pot GAIN 5k sul cavo) → PRE →
EQ2 (U4) → POSTEQ → VCA del MUTE e del limiter (U5 + U6/U7) → POST → driver MSUM6 (U8) e
4 mandate (U9 ADG1434, U10 iniezione).

Polarità contata da capo a capo (todo 227, `sistema-polarita.md` F2): differenziale −1, stadio
2 −1, EQ2 +1, VCA + I/V +1 → POST +1; driver MSUM −1, [A2] −1 → +1. **Lo scambio degli ingressi
del differenziale (REV dec. 145) non c'è**: il differenziale resta quello di `sim/mic/mic-pre.inc`.

## Scelte NOTA (non scritte nei documenti)

1. **±15 LN dal ±18, non dal raw ±22.** LT3045 e LT3094 reggono 20 V in ingresso: come il master.
   Il design doc §7 dice «da raw ±22»: da correggere lì.
2. **Clamp d'ingresso con 1N4148W** al posto della classe BAV199: il datasheet del BAV199
   (Nexperia) non si scarica da qui, e il pinout non si scrive a memoria. Da rivedere: la perdita
   del 1N4148W (~25 nA) sui 47k dà ~1 mV, tolto dal passa-alto.
3. **XLR su un cavo (J3, 3 poli)** con ferrite, 100 pF e clamp sulla scheda. La posizione dell'XLR
   (pannello frontale o retro) non è decisa: il pannello di `coordinate.json` non lo mostra.
4. **HIGH dell'EQ2 a 4,75k / 2,26k** (E96 di 4,7k / 2,25k del design doc §5.1, ~5 kHz). Il FX-SEND
   e `sim/mic/backend.inc` usano 5,23k / 2,49k (~4,5 kHz). Discordanza da chiudere.
5. **EQ2 = cella del FX-SEND** con la LOW Baxandall a pot 10k singolo (`fx-eq2-pot10k.cir`), non la
   cella LOW a due reostati della §5.1 (servirebbe un pot doppio anche in mono).
6. **VCA**: pin V− con 5,1k verso −15 LN (valore del datasheet a −15 V); I/V 20k // 47p (REV dec. 145).
7. **Limiter: inseguitore su SM** (sezione libera del secondo quad). Senza, la 16k del sottrattore
   carica Ch: a riposo PK salirebbe a ~0,8 V e il rilascio scenderebbe da 1 s a ~16 ms.
   Sottrattore: 16k / 10k (G = 0,625), VTH 2,179 V da 169k / 10k sul +15 LN (SUBP 0,838 V).
   Mezza onda a due diodi (5 diodi nel limiter, il design doc ne conta 4).
8. **MUTE**: tasto a ritenuta fra +5VF e MUTE_SW (come il MONO del master), partitore 10k/10k,
   220n (1,1 ms), inseguitore → 2,5 V → Rb 2k. Il tipo di tasto (ritenuta o momentaneo) è di
   Filippo (voce 40): con un tasto momentaneo serve un flip-flop.
9. **LED tricolore** (logica in `celle_micmono.led3`): LED bicolore ad anodo comune, giallo = verde
   + rosso. LM339 a +5VF / CTRL_GND; detector g = 0,199 (10k / 2k49), MET ≤ 3,3 V. Soglie da
   partitore sul +15 LN: 133k / 7,68k / 6,65k / 1,1k → −5,9 / +11,1 / +17,1 dBu. Latch del rosso
   750k × 1 µF fino a 2,5 V = 0,52 s; un 2N7002 spegne il verde durante il latch. Chatter dei
   comparatori senza isteresi: da vedere a banco.
10. **Mandate**: 2k2 fra il cursore del pot SEND e l'ADG1434 (vedi `pcb/mono/NOTE.md` punto 3: nel
    MIC il POST resta sotto +13 dBu col limiter, la 2k2 serve al MONO; cella comune).
11. **Driver MSUM**: 10 pF sulla retroazione (20k / 20k), poi 20k di somma lato sorgente.

## Cosa resta

1. Scheda comandi (`mic-comandi.py`): pot GAIN 5k (curva C, todo 131), EQ LOW e HIGH 10k, SEND
   1-4 10k, LED bicolore, tasto MUTE, alle posizioni di `docs/pannelli/coordinate.json` («mic»).
   Il cavo J2 (2x12) ha già l'ordine dei fili in `mic.py` (FILI): va spostato in un `cavo.py`
   come nel FX-SEND quando nasce la scheda comandi.
2. PCB a due lati e giro completo (PASSA prima del commit della scheda).
3. Simulare coi componenti veri: limiter (raddrizzatore, superdiodo, sottrattore, mezza onda),
   logica del LED, offset del rilevatore (1 mV al pin = 0,16 dB).
4. Correnti dei rail col silicio contato qui (§7 del design doc: ±15 LN ~20 mA è basso: con INA,
   VCA e limiter si stimano ~45 mA).
