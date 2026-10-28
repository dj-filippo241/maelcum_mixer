# FX-SEND, schede v0.2-bozza (2026-10-27)

Prima PCB di maelcum, rifatta con i pot a bordo (dec. 133, 135, 136). Due schede:

- **scheda principale** (`fx-send.py`): catena audio, assign, alimentazione, C96. Sta in piedi,
  perpendicolare al pannello.
- **scheda comandi** (`fx-send-comandi.py`, file in `comandi/`): i 3 pot doppi, parallela al
  pannello, tenuta dai dadi dei pot. Gli alberi cadono sui fori del render: le posizioni
  arrivano da `docs/pannelli/coordinate.json`.

Un cavo piatto 2x12 collega J1 (comandi) a J2 (principale): masse fra i gruppi di segnale. I 4
bottoni assign arrivano dal pannello del canale su J3 (1x6, logica +5 V). È una **bozza da
rivedere**: non è pronta per l'ordine.

## Cosa c'è

| File | Cosa |
|---|---|
| `fx-send.py`, `fx-send-comandi.py` | i netlist in Python: unica fonte. Schema e PCB si rigenerano da qui |
| `fx-send.kicad_sch/.kicad_pcb` | principale: 100 × 165 mm, 4 strati (In1 e In2 = piano AGND), 120 componenti |
| `comandi/fx-send-comandi.kicad_sch/.kicad_pcb` | comandi: 34 × 83 mm (pannello 36 × 87 meno i margini), 4 componenti |
| `bom.csv`, `comandi/bom.csv` | distinte |
| `out/`, `comandi/out/` | riepilogo, ERC e DRC |
| `fx-send.png`, `comandi/fx-send-comandi.png` | viste delle schede |

Rigenerare (principale circa 4 minuti, comandi meno di 1):

```bash
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 pcb/fx-send/fx-send-comandi.py
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 pcb/fx-send/fx-send.py
```

Lo schema e la PCB non vanno modificati a mano: una rigenerazione li sovrascrive. Un pannello
cambiato si rigenera con `docs/pannelli/genera_pannelli.py`, poi la scheda comandi.

## Esito dei controlli (v0.2)

- Principale: 91 reti, nessuna con un pin solo; schema esportato = netlist voluto. ERC 0 errori
  (2 avvisi «VSS non a massa» sull'ADG1434, voluti). DRC 0 violazioni, 0 collegamenti mancanti;
  3 avvisi «via sospesa» del fanout di massa e avvisi di parità cosmetici (pin liberi del C96,
  campo «Nota», attributi dei fori).
- Comandi: 17 reti, ERC 0, DRC 0 violazioni e 0 collegamenti mancanti. Avvisi di parità: le
  staffe dei pot (MP) senza rete, volute.
- A 100 × 130 mm Freerouting lasciava 5 collegamenti: la scheda è salita a 165 mm e le piste
  ±15 V switch a 0,25 mm.

## Fonti dei valori

Catena audio da `sim/fx/fx-eq2-pot10k.cir` (cella LOW Baxandall, pot 10k) e `sim/fx/send-chain-noise.cir`. Pinout C96 da
`docs/fase3/sistema-backplane.md` §3-5, classe FX-SEND. Ramo ±18 V da `sim/system/psu-rail.cir`.
Tutto [PROVVISORIO].

## Incongruenze trovate disegnando (da chiudere)

1. **[CHIUSA 2026-10-27] Pot LOW a 4 sezioni.** Risolta riordinando la cella (Baxandall): un pot doppio 10k, `sim/fx/RISULTATI-fx-eq2-pot10k.md`. Testo originale: La cella shelf ha due reostati complementari per lato (Rza, Rzb): in stereo servono 4 sezioni. Il documento dice «pot doppi». Il valore simulato è 31k, che non esiste a catalogo (25k o 50k → ricalcolo).
2. **OPA1654: 4 chip, non 3** (resta da correggere nella BOM del design doc §5). 18 sezioni = 1 OPA1612 (buffer in) + 4 OPA1654 (2 EQ + 2 iniezione). La BOM del §5 ne conta 3.
3. **[CHIUSA 2026-10-27] Pinout ADG1434.** Verificato sul datasheet Rev. E (tabella 8): i pin 6-20 della bozza erano sbagliati (canale 2 a sinistra, VDD sul 16, NIC sul 15). Simbolo corretto in `fx-send.py`; tabella di verità confermata (IN alto = SxA chiuso). Dettagli: `docs/fase1/adg1434-datasheet-verify.md` §6.
4. **[SUPERATA dalla dec. 133: pot saldati sulla scheda, bozza da rifare]** Pot fuori scheda via harness (come dice il §4): i nodi NB_L/NB_R della cella LOW sono masse virtuali e viaggiano sul cavo fino al pannello. Rischio di ronzio e di instabilità. In alternativa i pot si montano sulla scheda, se la meccanica lo permette.
5. **GLOBAL_MUTE (c9): polarità confermata il 2026-10-28** (`sim/master-out/RISULTATI-mute-ctrl.md`, todo 182): basso = suona, alto = muto. Il master tira giù la linea con un NMOS open drain; qui la pull-up a +5 V tiene il send muto senza master. Il mute apre i 4 assign (rete corretta il 2026-10-28, punto 12).
6. **Cap-moltiplicatore scalato** a circa 50 mA: Rb 1k, Cb 470 µF (la sim usa 47 Ω e 10 mF per 0,85 A). Il ±18 V esce a circa 18,0 V, da riverificare in simulazione col carico vero.
7. Aggiunti e non scritti nel documento: 100k a massa sugli ingressi SEND_IN (ingresso definito senza canale), diodi di protezione degli LM317/337, ferrite e bulk su ogni raw.

## Nuovi punti della v0.2

8. **Il C96 è più lungo del pannello.** Il DIN 41612 a 32 file misura circa 95 mm; il pannello
   del FX-SEND è profondo 87 mm. La scheda principale (100 mm) sporge di circa 13 mm sotto il
   modulo vicino. Strade: spostare la scheda in profondità, oppure un connettore a 16 file per
   le classi piccole. Da chiudere con la meccanica (q29).
9. **Altezza 165 mm** della scheda principale: dipende dall'altezza interna del telaio (q29).
   Si accorcia mettendo componenti sui due lati o tornando a una scheda larga.
10. **Pot.** Estremi dell'Alps RK09L (pin 1 antiorario, 3 orario, 2 cursore) da verificare sul
    disegno Alps: il sito non si scaricava. Curva del pot provvisoria (dec. 129). LEVEL da 9 mm
    invece di 14 (dec. 118) finché non c'è l'impronta dell'RK14.
11. **Cavo piatto e masse virtuali.** NB_L e NB_R (cursore del LOW, massa virtuale) viaggiano sul
    cavo, fra due fili di massa. Il cavo va tenuto corto (≤ 10 cm). Da provare a banco: ronzio e
    stabilità della cella LOW col cavo vero.

## Revisione del 2026-10-28 (generatore, `pcb/NOTE-generatore.md`)

12. **Mute degli assign corretto.** La v0.2 aveva 10k a massa e 4k7 in serie al 2N7002: col
    mute attivo e il bottone premuto l'ingresso dell'ADG1434 stava a 1,21 V, fra VIL 0,8 V e
    VIH 2,0 V (`docs/fase1/adg1434-datasheet-verify.md`); da acceso 2,5 V. Ora 100k a massa e
    1k sul FET: acceso 4,55 V, mute 0,45 V. Rampe: accensione 0,9 ms, mute 0,09 ms.
13. **Disaccoppiamento:** ogni 100n sta a ~2 mm dal pin del suo chip (prima 8-13 mm).
14. **Esito dei controlli adesso:** principale e comandi PASSA. Principale: ERC 0 errori,
    schema = netlist nei due sensi, DRC 0 errori, 0 collegamenti mancanti; avvisi: 51 attesi
    (pin liberi del C96), 2 via sospese di Freerouting. Controllo audio A1-A5: 10/29/23/4/3.
15. Diodi di protezione D2/D4 col simbolo `Device:D` (era 1N4148W con valore S1G).
16. Discordanze trovate dall'analisi, ancora aperte: `sim/fx/send-chain-noise.cir` descrive
    la cella LOW vecchia (1k/15,5k/56n), quindi il rumore −98,5 dBu del design doc §6 non vale
    per questa scheda; 1,72k non esiste all'1 % (E96: 1,74k = 19,4 V); `coordinate.json` dice
    ancora pot da 14 mm per il LEVEL; il design doc §5 dà al LEVEL un pot «custom taper», la
    scheda un 10k senza curva indicata.

## Limiti della bozza

- Piazzamento automatico per blocchi, senza criteri audio: i componenti della stessa cella non stanno stretti attorno al loro op-amp, e le masse virtuali non hanno la guardia chiesta dal backplane §4 (≤ 0,2 pF).
- Piste di Freerouting: corrette per il DRC, non ottimizzate per rumore e diafonia. Prima dell'ordine serve un passaggio a mano sui nodi critici: NB, NSH, gli ingressi degli op-amp, i ritorni dei bulk.
- Misure della scheda principale [PROVVISORIO]: dipendono dalla meccanica (q29), vedi punti 8 e 9.
- Dissipazione di LM317/337 e BD139/140 non verificata sul rame.
