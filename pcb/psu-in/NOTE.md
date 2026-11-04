# PSU-IN: note della bozza v0.1 (todo 167, 2026-11-04)

Schema da `psu-in.py` (sistema-psu-esterno.md §4, sistema-backplane.md REV dec. 113).
Esito: **SCHEMA PASSA** (ERC 0 errori), 41 componenti. **PCB: NON PASSA** (non committata).

## Cosa c'è

Per ogni rail: fusibile di gruppo 5x20, TVS verso il proprio 0 V, Schottky inverso, bulk.
±22,0 audio (pin raw ±27): T2,5 A, SMBJ26A, 2,2 mF. ±19 LN (pin raw ±22): T1 A, SMBJ22A, 1 mF.
[M] ±27 raw (a9-a12): T500 mA, SMBJ33A, 1 mF 63 V. +5: T2 A, SMBJ5.0A, 1 mF. V_FAN: T500 mA.
Stella: un 0 ohm 2512 per ogni 0 V del cavo verso AGND; bond unico AGND-CTRL_GND (0 ohm);
bond CHASSIS-AGND su un ponticello removibile (grounding §2). Pull-up 10k di AC_OK (c17).

## Scelte segnate NOTA

1. **Fusibile prima del TVS** (il documento elenca TVS, Schottky, fusibile): solo così la
   corrente del TVS, con un LDO del box in corto, apre il fusibile.
2. TVS SMBJ, Schottky SS54, bulk 63 V sul [M]: parti di classe, da confermare.
3. Cavo interno dal connettore circolare: Mini-Fit Jr 2x12 (J2).
4. Driver delle ventole (§4.5): nessun circuito nel documento; qui solo fusibile e J3.
5. Piste di potenza a 0,8 mm (con 1,5 mm Freerouting non passa fra i pin del C96): per
   1,7 A servono colate di potenza o piste sui due strati, da fare nel generatore.

## Esito della PCB

Tre giri: piste 1,5 mm = 24 aperti; 0,8 mm = 15 aperti (CTRL_GND 11); 0,8 mm con In2 di
piste = 4 aperti (DRC unconnected 4). Resta da dare a CTRL_GND una colata sua o una pista
dedicata sui pin c del C96.
