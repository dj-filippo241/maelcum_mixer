# 5-WAY: note della bozza v0.1 (2026-11-15)

Schede di segnale del 5-way v0.3 (dec. 175), da `five-way.py LA|LB|RA|RB`. Quattro schede, due per
lato, 4 strati. Catena e valori: five-way-module.md §2-§5bis, bank-aligned-h.cir, nastro-b9.cir,
growl-bande.cir, RISULTATI-kill-zc.md. Esito: **PASSA** su tutte e quattro (ERC 0, DRC 0 errori e 0 aperti).

| Scheda | Contenuto | Componenti | Misure | Fila (PIANO-SCHEDE-F) |
|---|---|---|---|---|
| LA, RA | ricevitore del DJ bus, pad, banca H, kill a pi greco, logica dello zero, somma delle vie | 322 | 206 x 172 | 3 |
| LB, RB | POSITION, 5 celle, GROWL a bande, NASTRO B9, make-up col servo, presa del meter | 440 | 300 x 178 (L), 300 x 175 (R) | 1 e 2 |

La fila 4 tiene due schede del reroute e il PSU-IN (x 350-450, `piano_f.py`).

## Divisione e LED di livello (2026-11-15)

- Il conto vero (864 sulla L, 725 sulla R) non stava in una scheda per lato. Scelta 3 di Filippo
  (2026-11-15): i LED di livello delle 5 vie vanno sulla scheda comandi del 5-way. Il codice resta
  in `five-way.py`, funzione `led_livello()`, non chiamata: si sposta quando nasce la scheda comandi.
- Ogni scheda B porta sul cavo la presa del meter `5W_MET_L` / `5W_MET_R` (EDRV per 100 ohm). La LB
  porta anche +15LN, -15LN, +5VF e CTRL_GND per i LED. La presa della R non passa più dal backplane.
- La somma delle vie va dalla A alla B sul backplane: `5W_SUM_L` sul b7, `5W_SUM_R` sul b8, per 47 ohm.
  NOTA: la massa fra le due schede è la stella del backplane; il carico sulla B è 40,2k.
- La A ha il suo cavo J2 per le levette di kill (KSW1-5, CTRL_GND). La B ha il cavo dei pot.

## Scelte segnate NOTA

1. Pinout del dual JFET (classe LSK389) e del J310 (simbolo MMBFJ113): da confermare sul datasheet.
2. Cf 22p del ricevitore come i ricevitori del master.
3. 22k + Schottky BAT54WS davanti al LM339: l'ingresso resta sopra -0,3 V.
4. OR a diodi del fronte e del tempo massimo; logica dello zero da simulare a porte.
5. 47 ohm verso MSUM1 e ponticello J5W sul backplane.
6. +-15 LN dal +-18 (LT3045 / LT3094 reggono 20 V in ingresso).

## Retro (dec. 142)

Sulla B le celle 3-5 (solo SMD) stanno sul retro: davanti non trovano posto (giro 1, «servono 78 mm
in più»). POSITION resta davanti: sul retro con le celle lasciava aperti negli shaper (giro 3).

## Giri della PCB

1. Quattro schede, tutto davanti: LA e RA PASSA; LB e RB NON PASSA (servono 78 / 74 mm, 13 courtyard,
   Freerouting non finisce in un'ora).
2. POSITION e celle 3-5 sul retro: il piazzamento entra. Restano 13 courtyard: 8 resistenze impilate
   nello stesso punto, senza posto attorno al loro op-amp (U1 e U146). Nuovo nel generatore:
   `d.cluster_fuori = True` le rimanda al piazzamento a blocchi (spento di default).
3. Giro completo: LA e RA PASSA al primo tentativo. LB e RB 14 e 17 aperti, quasi tutti in POSITION sul retro.
4. B a 300 mm (le file 1 e 2 arrivano a 439 e 441 mm su 450): LB 3, RB 6 aperti nel tentativo migliore.
5. POSITION davanti: RB PASSA; LB 1 aperto (isola della colata AGND), anche con 6 tentativi (`d.route_tries`).
6. LB: 12 pad di massa senza posto per la via. `d.fanout_more = True` (nato sul master) le cerca anche di
   traverso: restano 2. LB PASSA al terzo tentativo, RB al primo.

## Resta

- Scheda comandi del 5-way, coi LED di livello: l'ordine del cavo viene da queste schede.
- Slot 5W1-5W4 del backplane dai netlist (oggi SINTETICO in `piano_f.py`).
- Schema leggibile in inglese (`leggibile.py`).

Verificato in: KiCad (ERC, DRC). Python: no. LTspice: no (valori dai netlist del 5-way). Live: no.
