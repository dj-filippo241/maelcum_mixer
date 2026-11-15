# Piano delle schede sulla disposizione F (dec. 172)

Generato da `pcb/tools/piano_schede.py --f` il 2026-11-09: non modificare a mano. Misure da
`docs/pannelli/proposta_f.py`. Telaio inclinato: schede alte 185 mm dietro e 120 davanti (dec. 158);
tetto 70 % (dec. 156); passo 25 mm; pannello 13U, profondità utile 570 mm.

Regola nuova: il C96 è lungo 95 mm (impronta KiCad), quindi il lato della scheda col connettore
è lungo almeno 100 mm. Sotto i moduli bassi e larghi (MASTER, 5-WAY, FILTRO, CUE) le schede vanno
da sinistra a destra; sotto le strisce (canali, MIC, MONO, ritorni) da dietro a davanti. [C, PROVVISORIO]

| Modulo | Copie | Scheda | Comp. | Fonte | Verso | Lunga (mm) | Alta (mm) | Dove | Pieno |
|---|---|---|---|---|---|---|---|---|---|
| MASTER | 1 | master-segnale.py | 283 | vero | sinistra-destra | 171 | 182 | fila 1 di 1, y 24 | 70 % |
| MASTER | 1 | master-uscita.py L | 155 | vero | sinistra-destra | 100 | 182 | fila 1 di 1, y 24 | 65 % |
| MASTER | 1 | master-uscita.py R | 144 | vero | sinistra-destra | 100 | 182 | fila 1 di 1, y 24 | 61 % |
| 5-WAY + REROUTE | 1 | five-way.py LB (celle, GROWL, NASTRO) | 440 | vero | sinistra-destra | 300 | 178 | fila 1 di 4, y 61 | 63 % |
| 5-WAY + REROUTE | 1 | five-way.py RB | 440 | vero | sinistra-destra | 300 | 175 | fila 2 di 4, y 86 | 64 % |
| 5-WAY + REROUTE | 1 | five-way.py LA (ricevitore, banca, kill) | 322 | vero | sinistra-destra | 206 | 172 | fila 3 di 4, y 112 | 70 % |
| 5-WAY + REROUTE | 1 | five-way.py RA | 322 | vero | sinistra-destra | 206 | 172 | fila 3 di 4, y 112 | 70 % |
| 5-WAY + REROUTE | 1 | fx-ret-reroute.py | 225 | vero | sinistra-destra | 139 | 178 | fila 1 di 4, y 61 | 70 % |
| 5-WAY + REROUTE | 1 | fx-ret-reroute.py | 225 | vero | sinistra-destra | 141 | 175 | fila 2 di 4, y 86 | 70 % |
| 5-WAY + REROUTE | 1 | fx-ret-reroute.py | 225 | vero | sinistra-destra | 146 | 169 | fila 4 di 4, y 137 | 70 % |
| 5-WAY + REROUTE | 1 | fx-ret-reroute.py | 225 | vero | sinistra-destra | 146 | 169 | fila 4 di 4, y 137 | 70 % |
| FILTRO | 1 | filtro, parte 1 (da scrivere) | 225 | stima +-30 % | sinistra-destra | 149 | 166 | fila 1 di 2, y 163 | 70 % |
| FILTRO | 1 | filtro, parte 2 (da scrivere) | 225 | stima +-30 % | sinistra-destra | 151 | 164 | fila 2 di 2, y 188 | 70 % |
| CANALE + FX SEND | 4 | canale.py (una scheda, C96, dec. 173) | 380 | vero | dietro-davanti | 287 | 162-129 | posto 1 di 2, y 201-488 | 70 % |
| CANALE + FX SEND | 4 | fx-send.py | 120 | vero | dietro-davanti | 100 | 162-151 | posto 2 di 2, y 201-301 | 59 % |
| CUE | 1 | cue.py | 157 | vero | sinistra-destra | 196 | 124 | fila 1 di 2, y 531 | 50 % |
| MIC | 1 | mic.py | 206 | vero | dietro-davanti | 142 | 168-152 | posto 1 di 2, y 150-292 | 70 % |
| MONO | 3 | mono.py | 127 | vero | dietro-davanti | 100 | 168-156 | posto 1 di 2, y 150-250 | 60 % |
| FX-RET | 4 | fx-ret.py (segnale, C96) | 199 | vero | dietro-davanti | 160 | 146-128 | posto 1 di 2, y 340-500 | 70 % |

Schede in tutto: 30.

## Avvisi

- Nessuno: ogni scheda ha il suo posto entro il 70 %.

## Aperto

- Backplane: quattro tratti, uno per zona (pcb/backplane/PIANO.md, todo 269). PSU-IN nella fila 4 sotto il 5-way.
- 5-way: quattro schede vere (A 322, B 440 per lato, 2026-11-15); filtro: stima +-30 %. Fila 4: due reroute e il PSU-IN a x 350-450.
- Schede comandi da disegnare: 5-way (coi LED di livello delle 5 vie), filtro.
