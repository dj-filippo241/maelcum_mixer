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
- **PCB: NON PASSA** per un difetto del generatore (vedi «Giro del PCB» sotto).
- 125 pezzi in distinta (127 impronte coi fori). Silicio: OPA1612 ×1, OPA1654 ×3, ADG1434 ×1,
  LM339 ×1, LM317 + LM337, 78L15 + 79L15, 1N4148W ×6. Coincide con la §8 del design doc.

## Giro del PCB (2026-11-04): NON PASSA, non committato

Un giro completo su 100 × 220, un lato: piazzamento e Freerouting riusciti (nessuna rete di
segnale aperta), ma **DRC 31 errori di distanza**, tutti su reti delle classi sottili
(+15SW, −15SW, +5VF a 0,25 mm) contro vie e piste vicine. Controllo audio A1-A5: vedi
`out/riepilogo.json` del giro (A3 10, A4 3, A5 7).

Causa nel generatore, non nella scheda: `pcbgen.py` dà alle classi sottili distanza 0,2 mm e
via 0,8 mm nel PCB (`build_pcb`, revisione «vie piccole» del master, f58b4a7), ma scrive nel
`.kicad_pro` distanza 0,25 mm e via 1,0 mm per tutte le classi (`_write_project`). Freerouting
lavora a 0,2, il DRC di kicad-cli controlla a 0,25. È la stessa cosa dei «3 errori nuovi di
distanza» del giro 5 del master. Da allineare in `_write_project` (thin → 0,2 / 0,8 / 0,4),
poi rifare il giro. I file del PCB restano fuori dal commit.

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

1. Scheda comandi (`mono-comandi.py`): pot GAIN 10k A (todo 131), EQ LOW e HIGH 10k, SEND 1-4,
   LED bicolore, alle posizioni di `coordinate.json` («mono»). Cavo J2 2x11 (FILI in `mono.py`).
2. Simulare la logica del LED coi componenti; banco per le soglie.
