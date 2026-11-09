# MONO, scheda principale v0.1-bozza (2026-11-04, todo 30)

Schema e distinta del modulo MONO (dec. 97), scritti col generatore. Fonte unica: `mono.py`;
le celle comuni col MIC stanno in `pcb/tools/celle_micmono.py` (EQ2, detector e LED, driver
MSUM, mandate, alimentazione).

Rigenerare (pochi secondi; senza `--solo-schema` anche il PCB, ~4 minuti):

```bash
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 pcb/mono/mono.py --solo-schema
```

## Stato

- **SCHEMA PASSA**: 87 reti, nessuna con un pin solo; schema = netlist nei due sensi; ERC 0
  errori, 1 avviso voluto («VSS non a massa» sull'ADG1434).
- **PCB: PASSA** (giro del 2026-11-04, todo 237). Scheda comandi: PASSA (vedi sotto).
- 125 pezzi in distinta (127 impronte coi fori). Silicio: OPA1612 ×1, OPA1654 ×3, ADG1434 ×1,
  LM339 ×1, LM317 + LM337, 78L15 + 79L15, 1N4148W ×6. Coincide con la §8 del design doc.

## Giro del PCB (2026-11-04, todo 237): PASSA

Scheda principale 100 × 220, un lato, 127 impronte. Il primo giro (todo 30) dava 31 errori di
distanza sulle classi sottili: il `.kicad_pro` diceva 0,25 mm, la scheda 0,2. Il generatore ora
prende le regole da una fonte sola (`Design._classrules`, todo 205, 0240fe8): nessuna modifica qui.

- ERC 0 errori (1 avviso voluto, VSS dell'ADG1434). DRC 0 violazioni; avvisi: 5 silk_overlap,
  14 silk_over_copper, 50 net_conflict attesi. Freerouting: nessuna rete di segnale aperta (la
  massa la chiudono le colate).
- Controllo audio: A1 9, A2 21, A3 10, A4 3, A5 0 (primo giro: A3 10, A4 3, A5 7).

Scheda comandi (`mono-comandi.py`, file in `comandi/`): 34 × 186,5 mm (pannello 36 × 190,5 meno
i margini), 9 componenti: 7 pot singoli Alps RK09L verticali alle posizioni di
`coordinate.json` («mono»), LED bicolore, J1 2x11 in alto. PASSA: ERC 0, DRC 0 violazioni,
0 aperti; 15 avvisi net_conflict attesi (staffe dei pot e filo CTRL_GND libero sul lato comandi).
Ordine dei fili: `cavo.py`, letto da `mono.py` e da `mono-comandi.py`. Celle della scheda comandi
in `celle_micmono.scheda_comandi`.

NOTA della scheda comandi (da decidere o verificare):

- Pot di classe 14 mm (GAIN, SEND) disegnati come RK09L 9 mm: KiCad non ha l'RK14 (come il FX-SEND).
- LED: un bicolore 3 mm ad anodo comune al centro; il render del pannello mostra tre punti a
  passo 4 mm. Il pezzo non è scelto: il pinout (1 = catodo verde, 2 = anodo, 3 = catodo rosso)
  va verificato sul suo datasheet.
- Curve: GAIN 10k A (todo 131); EQ e SEND 10k, curva non scritta (dec. 129).

## Catena e polarità

Jack TS (J3) → TVS → 1k + clamp ai ±18 → 100n + 1M → buffer 1 MΩ (U3) → pot GAIN 10k A sul cavo
→ make-up +9,97 dB (2,15k / 1k) → PRE → EQ2 (U4) → POST → driver MSUM7 (U8) e 4 mandate (U9, U10).
Polarità: POST +1, driver MSUM −1, [A2] −1 → +1 (todo 227, F2).

## Scelte NOTA (non scritte nei documenti)

1. **Clamp con 1N4148W** al posto della classe BAV199 (pinout non verificabile da qui); TVS
   bidirezionale low-cap 24 V in SOD-323, valore da scegliere.
2. **Jack su un cavo (J3, 2 poli)**: posizione sul pannello non decisa.
3. **Mandate: 2k2 in serie fra cursore e ADG1434.** Il POST del MONO arriva a +23 dBu (PRE +17 più
   EQ +6), oltre i ±15 V dello switch (+22,5 dBu, trappola ADG1434 del CLAUDE.md). La 2k2 limita
   a ~1 mA la corrente nei diodi di protezione; il mute (SxB a massa) vale −53 dB col pot tutto
   aperto. Rumore della 2k2: ~−119 dBu, sotto i −111 dBu della mandata chiusa. Lo stesso
   problema c'è nel FX-SEND (LVL_W su ±15 SW): da guardare là.
4. **Detector e LM339** sul ±18 (il design doc §7 dà ~5 mA sul ±15 LN, ma il MONO non ha LT3045):
   soglie da partitore sul +18 V, 165k / 7,68k / 6,65k / 1,1k → −6,0 / +11,0 / +17,0 dBu.
   La tolleranza del ±18 (cap-moltiplicatore, ±3 %) sposta le soglie di ±0,25 dB.
5. EQ2, LED, driver: come `pcb/mic/NOTE.md` punti 4, 5, 9, 11.

## Cosa resta

1. Scheda comandi: fatta (sopra). Restano la scelta del LED e del pot 14 mm.
2. Simulare la logica del LED coi componenti; banco per le soglie.

## 2026-11-09: scheda comandi sulla disposizione F (dec. 172)

Rigenerata da `coordinate.json` nuovo: 59.0 × 175.8 mm (pannello 61 × 179.8 meno i margini). PASSA in due giri. La scheda principale non cambia: stesso cavo, stessi fili.
