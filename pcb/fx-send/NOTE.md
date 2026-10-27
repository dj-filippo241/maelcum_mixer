# FX-SEND, scheda v0.1-bozza (2026-10-27)

Prima PCB di maelcum. Nasce dalla richiesta di Filippo del 2026-10-27 («fai tutte le pcb che
riesci»), che riapre schemi e PCB fermi dal 2026-10-26. È una **bozza da rivedere**: non è
pronta per l'ordine.

## Cosa c'è

| File | Cosa |
|---|---|
| `fx-send.py` | il netlist in Python: unica fonte. Schema e PCB si rigenerano da qui |
| `fx-send.kicad_sch` | schema generato (etichette sui pin, un riquadro per blocco) |
| `fx-send.kicad_pcb` | PCB 160 × 100 mm, 4 strati (In1 e In2 = piano AGND), piste di Freerouting |
| `bom.csv` | distinta: 119 componenti |
| `out/riepilogo.json`, `out/erc.json`, `out/drc.json` | esito dei controlli |
| `fx-send.png` | vista della scheda |

Rigenerare (circa 4 minuti, quasi tutti di Freerouting):

```bash
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 pcb/fx-send/fx-send.py
```

Lo schema e la PCB non vanno modificati a mano: una rigenerazione li sovrascrive.

## Esito dei controlli

- Netlist: 91 reti, nessuna rete con un pin solo. Lo schema esportato da KiCad coincide col netlist voluto, rete per rete.
- ERC: 0 errori. 2 avvisi «VSS non a massa» sull'ADG1434, voluti perché VSS va a −15 V.
- DRC: 0 violazioni, 0 collegamenti mancanti.
- Parità schema/PCB: 71 avvisi cosmetici. 51 sono pin liberi del C96, che lo schema chiama «unconnected-…» e la PCB lascia senza rete. 20 riguardano il campo «Nota» e gli attributi di distinta dei fori.

## Fonti dei valori

Catena audio da `sim/fx/fx-eq2.cir` e `sim/fx/send-chain-noise.cir`. Pinout C96 da
`docs/fase3/sistema-backplane.md` §3-5, classe FX-SEND. Ramo ±18 V da `sim/system/psu-rail.cir`.
Tutto [PROVVISORIO].

## Incongruenze trovate disegnando (da chiudere)

1. **Pot LOW a 4 sezioni.** La cella shelf ha due reostati complementari per lato (Rza, Rzb): in stereo servono 4 sezioni. Il documento dice «pot doppi». Il valore simulato è 31k, che non esiste a catalogo (25k o 50k → ricalcolo).
2. **OPA1654: 4 chip, non 3.** 18 sezioni = 1 OPA1612 (buffer in) + 4 OPA1654 (2 EQ + 2 iniezione). La BOM del §5 ne conta 3.
3. **[CHIUSA 2026-10-27] Pinout ADG1434.** Verificato sul datasheet Rev. E (tabella 8): i pin 6-20 della bozza erano sbagliati (canale 2 a sinistra, VDD sul 16, NIC sul 15). Simbolo corretto in `fx-send.py`; tabella di verità confermata (IN alto = SxA chiuso). Dettagli: `docs/fase1/adg1434-datasheet-verify.md` §6.
4. **[SUPERATA dalla dec. 133: pot saldati sulla scheda, bozza da rifare]** Pot fuori scheda via harness (come dice il §4): i nodi NB_L/NB_R della cella LOW sono masse virtuali e viaggiano sul cavo fino al pannello. Rischio di ronzio e di instabilità. In alternativa i pot si montano sulla scheda, se la meccanica lo permette.
5. **GLOBAL_MUTE (c9): polarità non definita** nel master (§3.7). Qui: pull-up a +5 V, alto = muto, così senza master il send resta muto. Il mute apre i 4 assign con una rampa di circa 0,5 ms (4,7k su 100n). Da ratificare quando si disegna il controller del mute.
6. **Cap-moltiplicatore scalato** a circa 50 mA: Rb 1k, Cb 470 µF (la sim usa 47 Ω e 10 mF per 0,85 A). Il ±18 V esce a circa 18,0 V, da riverificare in simulazione col carico vero.
7. Aggiunti e non scritti nel documento: 100k a massa sugli ingressi SEND_IN (ingresso definito senza canale), diodi di protezione degli LM317/337, ferrite e bulk su ogni raw.

## Limiti della bozza

- Piazzamento automatico per blocchi, senza criteri audio: i componenti della stessa cella non stanno stretti attorno al loro op-amp, e le masse virtuali non hanno la guardia chiesta dal backplane §4 (≤ 0,2 pF).
- Piste di Freerouting: corrette per il DRC, non ottimizzate per rumore e diafonia. Prima dell'ordine serve un passaggio a mano sui nodi critici: NB, NSH, gli ingressi degli op-amp, i ritorni dei bulk.
- Misure della scheda (160 × 100) e posizione del connettore frontale [PROVVISORIO]: dipendono dalla meccanica (q29).
- Dissipazione di LM317/337 e BD139/140 non verificata sul rame.
