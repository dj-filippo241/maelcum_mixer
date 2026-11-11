# Backplane a tratti, disposizione F (todo 269)

Generato da `pcb/backplane/piano_f.py`: non modificare a mano. Coordinate sul fondo del telaio,
x da sinistra, y da dietro (mm). [C, PROVVISORIO]

## Tratti

| Tratto | Cosa | x | y | Misura (mm) | Slot |
|---|---|---|---|---|---|
| T1 | fondo: MASTER, 5-WAY, PSU-IN | 0-450 | 10-148 | 450 x 138 | MAS OUT_L OUT_R 5W1 5W2 PSU |
| T2 | canali: FILTRO, 4 CANALI, 4 FX-SEND | 0-200 | 152-318 | 200 x 166 | CH1 SEND1 CH2 SEND2 CH3 SEND3 CH4 SEND4 FIL1 FIL2 |
| T3 | cuffie: CUE | 0-200 | 515-555 | 200 x 40 | CUE |
| T4 | destra: MIC, 3 MONO, 4 FX-RET | 206-450 | 150-446 | 244 x 296 | MIC RET1 MONO1 RET2 MONO2 RET3 MONO3 RET4 |

## Slot

| Slot | Tratto | Classe | Pin a1 (x, y) | Verso | Rail con PTC (A) | Reti di segnale | Fonte |
|---|---|---|---|---|---|---|---|
| CH1 | T2 | canale | 12.5, 290.4 | lungo y | +5V 0.2, RAW+22 0.1, RAW+27 0.3, RAW-22 0.1, RAW-27 0.3 | BUS_HPF_L BUS_HPF_R BUS_LPF_L BUS_LPF_R CUE1_L CUE1_R DJBUS_L DJBUS_R FILT_MODE1_0 FILT_MODE1_1 SEND_TAP1_L SEND_TAP1_R | pcb/canale (netlist) |
| SEND1 | T2 | fx-send | 37.5, 290.4 | lungo y | +5V 0.05, RAW+22 0.05, RAW+27 0.1, RAW-22 0.05, RAW-27 0.1 | GLOBAL_MUTE S1_L S1_R S2_L S2_R S3_L S3_R S4_L S4_R SEND_TAP1_L SEND_TAP1_R | pcb/fx-send (netlist) |
| CH2 | T2 | canale | 62.5, 290.4 | lungo y | +5V 0.2, RAW+22 0.1, RAW+27 0.3, RAW-22 0.1, RAW-27 0.3 | BUS_HPF_L BUS_HPF_R BUS_LPF_L BUS_LPF_R CUE2_L CUE2_R DJBUS_L DJBUS_R FILT_MODE2_0 FILT_MODE2_1 SEND_TAP2_L SEND_TAP2_R | pcb/canale (netlist) |
| SEND2 | T2 | fx-send | 87.5, 290.4 | lungo y | +5V 0.05, RAW+22 0.05, RAW+27 0.1, RAW-22 0.05, RAW-27 0.1 | GLOBAL_MUTE S1_L S1_R S2_L S2_R S3_L S3_R S4_L S4_R SEND_TAP2_L SEND_TAP2_R | pcb/fx-send (netlist) |
| CH3 | T2 | canale | 112.5, 290.4 | lungo y | +5V 0.2, RAW+22 0.1, RAW+27 0.3, RAW-22 0.1, RAW-27 0.3 | BUS_HPF_L BUS_HPF_R BUS_LPF_L BUS_LPF_R CUE3_L CUE3_R DJBUS_L DJBUS_R FILT_MODE3_0 FILT_MODE3_1 SEND_TAP3_L SEND_TAP3_R | pcb/canale (netlist) |
| SEND3 | T2 | fx-send | 137.5, 290.4 | lungo y | +5V 0.05, RAW+22 0.05, RAW+27 0.1, RAW-22 0.05, RAW-27 0.1 | GLOBAL_MUTE S1_L S1_R S2_L S2_R S3_L S3_R S4_L S4_R SEND_TAP3_L SEND_TAP3_R | pcb/fx-send (netlist) |
| CH4 | T2 | canale | 162.5, 290.4 | lungo y | +5V 0.2, RAW+22 0.1, RAW+27 0.3, RAW-22 0.1, RAW-27 0.3 | BUS_HPF_L BUS_HPF_R BUS_LPF_L BUS_LPF_R CUE4_L CUE4_R DJBUS_L DJBUS_R FILT_MODE4_0 FILT_MODE4_1 SEND_TAP4_L SEND_TAP4_R | pcb/canale (netlist) |
| SEND4 | T2 | fx-send | 187.5, 290.4 | lungo y | +5V 0.05, RAW+22 0.05, RAW+27 0.1, RAW-22 0.05, RAW-27 0.1 | GLOBAL_MUTE S1_L S1_R S2_L S2_R S3_L S3_R S4_L S4_R SEND_TAP4_L SEND_TAP4_R | pcb/fx-send (netlist) |
| FIL1 | T2 | filtro | 89.4, 162.8 | lungo x | +5V 0.1, RAW+22 0.3, RAW+27 0.3, RAW-22 0.3, RAW-27 0.3 | BUS_HPF_L BUS_HPF_R BUS_LPF_L BUS_LPF_R DJBUS_L DJBUS_R FILT_MODE1_0 FILT_MODE1_1 FILT_MODE2_0 FILT_MODE2_1 FILT_MODE3_0 FILT_MODE3_1 FILT_MODE4_0 FILT_MODE4_1 | SINTETICO (backplane §4, dec. 159) |
| FIL2 | T2 | filtro | 89.4, 188.2 | lungo x | +5V 0.1, RAW+22 0.3, RAW+27 0.3, RAW-22 0.3, RAW-27 0.3 | - | SINTETICO (backplane §4, dec. 159) |
| CUE | T3 | cue | 139.4, 530.9 | lungo x | +5V 0.1, RAW+22 0.1, RAW+27 0.5, RAW-22 0.1, RAW-27 0.5 | CUE1_L CUE1_R CUE2_L CUE2_R CUE3_L CUE3_R CUE4_L CUE4_R MON_L MON_R | pcb/cue (netlist) |
| MIC | T4 | mic | 221.2, 239.4 | lungo y | +5V 0.1, RAW+22 0.1, RAW+27 0.1, RAW-22 0.1, RAW-27 0.1 | GLOBAL_MUTE MSUM6_L MSUM6_R S1_L S1_R S2_L S2_R S3_L S3_R S4_L S4_R | pcb/mic (netlist) |
| RET1 | T4 | fx-ret | 221.2, 429.4 | lungo y | +5V 0.2, RAW+22 0.1, RAW+27 0.2, RAW-22 0.1, RAW-27 0.2 | MSUM2_L MSUM2_R S1_L S1_R S2_L S2_R S3_L S3_R S4_L S4_R | pcb/fx-ret (netlist) |
| MONO1 | T4 | mono | 282.2, 239.4 | lungo y | +5V 0.1, RAW+22 0.05, RAW+27 0.1, RAW-22 0.05, RAW-27 0.1 | GLOBAL_MUTE MSUM7_L MSUM7_R S1_L S1_R S2_L S2_R S3_L S3_R S4_L S4_R | pcb/mono (netlist) |
| RET2 | T4 | fx-ret | 282.2, 429.4 | lungo y | +5V 0.2, RAW+22 0.1, RAW+27 0.2, RAW-22 0.1, RAW-27 0.2 | MSUM3_L MSUM3_R S1_L S1_R S2_L S2_R S3_L S3_R S4_L S4_R | pcb/fx-ret (netlist) |
| MONO2 | T4 | mono | 343.2, 239.4 | lungo y | +5V 0.1, RAW+22 0.05, RAW+27 0.1, RAW-22 0.05, RAW-27 0.1 | GLOBAL_MUTE MSUM7_L MSUM7_R S1_L S1_R S2_L S2_R S3_L S3_R S4_L S4_R | pcb/mono (netlist) |
| RET3 | T4 | fx-ret | 343.2, 429.4 | lungo y | +5V 0.2, RAW+22 0.1, RAW+27 0.2, RAW-22 0.1, RAW-27 0.2 | MSUM4_L MSUM4_R S1_L S1_R S2_L S2_R S3_L S3_R S4_L S4_R | pcb/fx-ret (netlist) |
| MONO3 | T4 | mono | 404.2, 239.4 | lungo y | +5V 0.1, RAW+22 0.05, RAW+27 0.1, RAW-22 0.05, RAW-27 0.1 | GLOBAL_MUTE MSUM7_L MSUM7_R S1_L S1_R S2_L S2_R S3_L S3_R S4_L S4_R | pcb/mono (netlist) |
| RET4 | T4 | fx-ret | 404.2, 429.4 | lungo y | +5V 0.2, RAW+22 0.1, RAW+27 0.2, RAW-22 0.1, RAW-27 0.2 | MSUM5_L MSUM5_R S1_L S1_R S2_L S2_R S3_L S3_R S4_L S4_R | pcb/fx-ret (netlist) |
| MAS | T1 | master | 89.4, 24.0 | lungo x | RAW+27 0.3, RAW-27 0.3 | INS_RET_L INS_RET_R INS_SEND_L INS_SEND_R MON_L MON_R MSUM1_L MSUM1_R MSUM2_L MSUM2_R MSUM3_L MSUM3_R MSUM4_L MSUM4_R MSUM5_L MSUM5_R MSUM6_L MSUM6_R MSUM7_L MSUM7_R VIE_TAP_L VIE_TAP_R | pcb/master/segnale (netlist) |
| OUT_L | T1 | uscita | 260.4, 24.0 | lungo x | +5V 0.2, RAW+26 0.2, RAW-26 0.2 | AC_OK GLOBAL_MUTE | pcb/master/uscita-L (netlist) |
| OUT_R | T1 | uscita | 360.4, 24.0 | lungo x | +5V 0.2, RAW+26 0.2, RAW-26 0.2 | GLOBAL_MUTE | pcb/master/uscita-R (netlist) |
| 5W1 | T1 | 5way | 89.4, 60.8 | lungo x | +5V 0.1, RAW+22 0.05, RAW+27 0.5, RAW-22 0.05, RAW-27 0.5 | 5W_OUT_L 5W_OUT_R DJBUS_L DJBUS_R | SINTETICO (backplane §4) |
| 5W2 | T1 | 5way | 89.4, 86.2 | lungo x | +5V 0.1, RAW+22 0.05, RAW+27 0.5, RAW-22 0.05, RAW-27 0.5 | - | SINTETICO (backplane §4) |
| PSU | T1 | psu-in | 439.4, 137.2 | lungo x | - | AC_OK | pcb/psu-in (netlist) |

## Cavi fra tratti

| Cavo | Da | A | Tipo | Fili (in ordine) |
|---|---|---|---|---|
| C1 | T1 | T2 | VE | AGND DJBUS_L AGND DJBUS_R AGND AGND AGND AGND AGND AGND |
| C2 | T1 | T2 | pilotato | AGND MON_L AGND MON_R CTRL_GND GLOBAL_MUTE AGND AGND AGND AGND |
| C3 | T2 | T3 | pilotato | AGND CUE1_L AGND CUE1_R AGND CUE2_L AGND CUE2_R AGND CUE3_L AGND CUE3_R AGND CUE4_L AGND CUE4_R AGND MON_L AGND MON_R AGND AGND |
| C4 | T2 | T4 | VE | AGND S1_L AGND S1_R AGND S2_L AGND S2_R AGND S3_L AGND S3_R AGND S4_L AGND S4_R AGND AGND |
| C5 | T1 | T4 | VE | AGND MSUM6_L AGND MSUM6_R AGND MSUM7_L AGND MSUM7_R AGND AGND |
| C6 | T1 | T4 | pilotato | AGND MSUM2_L AGND MSUM2_R AGND MSUM3_L AGND MSUM3_R AGND MSUM4_L AGND MSUM4_R AGND MSUM5_L AGND MSUM5_R CTRL_GND GLOBAL_MUTE AGND AGND |
| P2 | T1 | T2 | potenza (Mini-Fit Jr 2x5) | RAW+27 RAW-27 RAW+22 RAW-22 +5V AGND AGND AGND CTRL_GND CHASSIS |
| P3 | T1 | T3 | potenza (Mini-Fit Jr 2x5) | RAW+27 RAW-27 RAW+22 RAW-22 +5V AGND AGND AGND CTRL_GND CHASSIS |
| P4 | T1 | T4 | potenza (Mini-Fit Jr 2x5) | RAW+27 RAW-27 RAW+22 RAW-22 +5V AGND AGND AGND CTRL_GND CHASSIS |

## Controllo

- PASSA: ogni rete ha i suoi capi, ogni rete fra tratti ha il suo cavo.
