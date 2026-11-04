# PSU-IN: note della bozza v0.1 (todo 167, 2026-11-04)

Schema da `psu-in.py` (sistema-psu-esterno.md §4, sistema-backplane.md REV dec. 113).
Esito: **SCHEMA PASSA** (ERC 0 errori), 41 componenti. **PCB: PASSA** (2026-11-04, 4o giro).

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
   Portafusibile: Stelvio-Kontek PTF78 (5x20 aperto, 2 pin). Le clip 5x20 della libreria hanno due
   pad con lo stesso numero: Freerouting ne collega uno solo e il DRC conta l'altro aperto. Il
   Schurter FAB (chiuso) è più grande: con 9 fusibili la scheda non bastava (12 mm in più).
3. Cavo interno dal connettore circolare: Mini-Fit Jr 2x12 (J2).
4. Driver delle ventole (§4.5): nessun circuito nel documento; qui solo fusibile e J3.
5. Piste di potenza a 0,8 mm (con 1,5 mm Freerouting non passa fra i pin del C96): per
   1,7 A servono colate di potenza o piste sui due strati, da fare nel generatore.

## Esito della PCB

Giri 1-3 (clip Littelfuse 111): piste 1,5 mm = 24 aperti; 0,8 mm = 15 aperti; 0,8 mm con In2 di
piste = 4 aperti. I 4 aperti non erano CTRL_GND: erano +5V attorno al secondo pad «2» della clip
F7 (J1 a21/a22 e R1 senza piste). Giro 4 con Schurter FAB: piazzamento a colonne, 12 mm fuori,
24 aperti. Giro 5 con PTF78: **PASSA** (DRC 0 errori, 0 aperti; 70 avvisi attesi di parità).

Resta (non ferma la bozza): piste di potenza a 0,8 mm, per 1,7 A servono colate di potenza
(NOTA 5); circuito del driver delle ventole (NOTA 4).
