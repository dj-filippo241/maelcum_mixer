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
- **PCB: PASSA, stabile** (todo 248, 2026-11-05): 5 generazioni di fila, 5 PASSA. Vedi «Routing
  stabile». Scheda comandi: PASSA.
- Distinta: `bom.csv`. Silicio: OPA1612 ×3, OPA1654 ×5, V2181L ×1, ADG1434 ×1, LM339 ×1,
  LT3045 + LT3094, LM317 + LM337, 78L15 + 79L15, 1N4148W ×13. Coincide con la §8 del design
  doc più la REV della dec. 145.

## Giro del PCB (2026-11-04, todo 237)

Scheda principale 100 × 220, 206 impronte, SMD sui due lati (dec. 142): in `mic.py` vanno sul
retro i blocchi LED (LM339) e VCA del MUTE e del limiter (`d.side = "B"`); l'EQ2 resta davanti.
Le piste ±18 V scendono da 0,6 a 0,4 mm, solo nel MIC (NOTA: 0,4 mm porta ~1 A, il ramo ne usa
qualche decina di mA). Il generatore non cambia.

Giro committato: PASSA. ERC 0 errori (1 avviso voluto). DRC 0 violazioni; avvisi: 13 via_dangling
(fanout di massa, 5 via senza posto libero), 10 silk_overlap, 20 silk_over_copper, 53 net_conflict
attesi. Controllo audio: **A1 26, A2 32, A3 17, A4 2, A5 0**. A1 alto: i 100n e i condensatori dei
regolatori lontani dal pin (retro e alimentazione lunga 90 mm); da guardare col punto 5 di
`pcb/NOTE-generatore.md`.

**[SUPERATO 2026-11-05: vedi «Routing stabile e A1»] Esito instabile.** Freerouting non dà lo stesso risultato a ogni giro. Prove, stesso file salvo
dove scritto:

| Variante | Esito |
|---|---|
| LED, EQ2 e VCA sul retro, ±18 a 0,6 mm | NON PASSA: -18V aperta (11) |
| EQ2 davanti, ±18 a 0,6 | NON PASSA: -18V aperta (11) |
| EQ2, LED e VCA sul retro, ±18 a 0,4 | NON PASSA: 1 aperto |
| **EQ2 davanti, ±18 a 0,4 (adesso)**, 4 giri | 2 PASSA; 1 aperto (GLOBAL_MUTE); +15LN aperta (9); 2 errori di distanza |

Un PASSA su due non è una prova (NOTE-generatore, blocchi vicino ai connettori). Strade: più
blocchi sul retro per svuotare il davanti (oggi il retro si piazza nel primo posto libero, punto 1
di NOTE-generatore), oppure la scheda MIC su due schede (dec. 144).

## Routing stabile e A1 (2026-11-05, todo 248)

**Cos'è A1.** La regola A1 del controllo audio (`audiocheck.py`) misura la distanza fra ogni pin
di alimentazione di un chip e il condensatore più vicino sulla stessa rete: ≤ 3 mm per gli
op-amp, ≤ 10 mm per i regolatori. Un condensatore lontano lascia una pista lunga che fa da
induttanza: il regolatore oscilla o il chip vede i disturbi dell'alimentazione.

**A1: 26 → 9.** Prima 25 voci su 26 erano regolatori: tutta l'alimentazione stava in un blocco
solo, impacchettato a file, e i condensatori finivano a 13-38 mm dal loro pin. Cosa cambia:

1. `celle_micmono.power_18_sw` e `power_ln` hanno l'opzione `blocco=`: ogni regolatore fa un
   blocco suo coi suoi condensatori e la sua ferrite (la ferrite tocca il C96, così il blocco si
   piazza vicino al connettore). Default `None`: MONO, canale e FX-RET non cambiano (schema del
   MONO rigenerato, identico).
2. In `mic.py` (classe `MicDesign`) i C SMD di un'alimentazione di un regolatore U (LT3045,
   LT3094, 78L15, 79L15) si legano al pin come i 100n degli op-amp, sul pin d'angolo.

Restano 9: LM317, LM337, BD139 e BD140 (foro passante, elettrolitici radiali, 12-16 mm dal pin
contro 10) e U5.5 (VEE del VCA): quel pin va a −15 LN con la 5,1k, non vuole un condensatore.
È un falso positivo della regola, non un difetto.

**Perché il routing cambiava da un giro all'altro.** Il piazzamento è identico a ogni giro
(verificato). Cambia l'ordine in cui KiCad scrive pezzi e pin nel `.dsn`, e Freerouting dà un
risultato diverso per ogni ordine. Più o meno un tentativo su due lascia un collegamento aperto,
quasi sempre su una rete larga del C96 (+5V, CTRL_GND, RAW±22, RAW-27, +15SW): Freerouting tira
la pista dalla ferrite a una via, si ferma lì e dichiara la rete chiusa. Rileggere lo stesso
file dà lo stesso ordine e lo stesso aperto.

Cosa cambia in `mic.py` (il generatore non cambia):

| Leva | Perché |
|---|---|
| `d.inner_signal = True` | In2 strato di piste, come master e canale (SMD sui due lati) |
| `d.link_pairs = True` | pin gemelli del C96 uniti da una pista dritta |
| `d.cluster_gap = 0.8` | con 0,5 mm SMB e MUTE_CV (U7, retro) restavano aperte |
| seconda ricerca del fanout di massa | via nel pad esposto dell'LT3045 e attorno ai pad rimasti senza (U45.9, C56, C61): un pad di massa senza via lasciava un'isola di colata, «unconnected» nel DRC |
| C dei regolatori sul pin d'angolo | sul pin di mezzo coprivano il pin 9 di massa dell'LT3094 |
| fino a 4 tentativi di Freerouting | ogni tentativo ricostruisce la scheda (ordine nuovo) e cambia `-mp` (40, 20, 30, 15); controllo col DRC di kicad-cli, colate e classi come nel giro vero; resta il primo che passa. Esportare il `.dsn` in un processo nuovo non basta: l'ordine viene dal file |

Prove (generazioni di fila):

| Variante | Esito |
|---|---|
| solo i blocchi per regolatore | 1 PASSA su 5 |
| + fanout, pin d'angolo, In2, cluster 0,8, 3 tentativi sulla stessa scheda | 2 su 5: lo stesso aperto tre volte |
| + `.dsn` esportato in un processo nuovo | 4 su 5: l'ultimo fallisce 4 volte uguale |
| + piste del C96 a 0,5 mm | 2 su 5: provato e tolto |
| tentativi con la scheda ricostruita, controllo solo sugli aperti | 4 su 5 (un errore di distanza non visto) |
| + controllo col DRC completo | 3 su 5 |
| **+ `-mp` diverso a ogni tentativo (adesso)** | **5 PASSA su 5** (tentativi usati: 4, 1, 2, 3, 1) |

Ultimo giro: ERC 0 errori; DRC 0 violazioni, 0 aperti; controllo audio **A1 9, A2 34, A3 21,
A4 2, A5 3** (prima A1 26, A2 32, A3 17, A4 2, A5 0). A3 sale col grappolo a 0,8 mm; A5 sale
perché i blocchi dei regolatori ora stanno in mezzo alla scheda (piste del cavo SW1-4 a 0-3 mm
dall'LM337). Su 11 tentativi ne sono passati 5: con 4 tentativi una generazione resta senza PASSA
circa una volta su dieci (deduzione mia, dal conteggio). Una generazione dura 4-15 minuti.

Scheda comandi (`mic-comandi.py`, file in `comandi/`): 34 × 186,5 mm, 10 componenti: 7 pot singoli
Alps RK09L verticali alle posizioni di `coordinate.json` («mic»), LED bicolore, tasto MUTE, J1 2x12
in alto. PASSA: ERC 0, DRC 0 violazioni, 0 aperti, 15 net_conflict attesi (staffe dei pot, filo
CTRL_GND libero sul lato comandi). Ordine dei fili: `cavo.py`, letto da `mic.py` e da `mic-comandi.py`.
GAIN 5k C: antiorario = GP2 (0 dB), orario = GP1 (+29,9 dB).

NOTA della scheda comandi (da decidere o verificare):

- Pot di classe 14 mm (GAIN, SEND) disegnati come RK09L 9 mm: KiCad non ha l'RK14 (come il FX-SEND).
- LED: un bicolore 3 mm ad anodo comune al centro; il render mostra tre punti a passo 4 mm. Pezzo
  non scelto: pinout (1 = catodo verde, 2 = anodo, 3 = catodo rosso) da verificare sul datasheet.
- Tasto MUTE: impronta di un tasto 6 mm; ritenuta o momentaneo resta di Filippo (voce 40).

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

1. [FATTO 2026-11-04] Scheda comandi (`mic-comandi.py`): pot GAIN 5k (curva C, todo 131), EQ LOW e HIGH 10k, SEND
   1-4 10k, LED bicolore, tasto MUTE, alle posizioni di `docs/pannelli/coordinate.json` («mic»).
   Il cavo J2 (2x12) ha già l'ordine dei fili in `mic.py` (FILI): va spostato in un `cavo.py`
   come nel FX-SEND quando nasce la scheda comandi.
2. [FATTO 2026-11-05, todo 248] PCB a due lati: 5 PASSA su 5 (sopra). Restano: A5 (cavo SW1-4
   accanto all'LM337), i 4 regolatori a foro passante oltre i 10 mm di A1, e la causa vera
   degli aperti nascosti di Freerouting sulle reti larghe del C96. I tentativi multipli
   possono salire nel generatore se servono anche ad altre schede.
3. Simulare coi componenti veri: limiter (raddrizzatore, superdiodo, sottrattore, mezza onda),
   logica del LED, offset del rilevatore (1 mV al pin = 0,16 dB).
4. Correnti dei rail col silicio contato qui (§7 del design doc: ±15 LN ~20 mA è basso: con INA,
   VCA e limiter si stimano ~45 mA).

## 2026-11-09: scheda comandi sulla disposizione F (dec. 172)

Rigenerata da `coordinate.json` nuovo: 59.0 × 185.8 mm (pannello 61 × 189.8 meno i margini). PASSA in due giri. La scheda principale non cambia: stesso cavo, stessi fili.
