# Todo 170: C96 più lungo del pannello e altezza delle schede — proposta (2026-11-04)

Proposta di Claude, nessuna scheda cambiata. Fonti: `pcb/fx-send/NOTE.md` punti 8-9,
`pcb/PIANO-schede.md`, dec. 142, 144, 158, `pcb/tools/backplane.py`.

## Il problema, in due righe

1. **C96 contro pannello.** Il DIN 41612 C 3×32 è lungo ~95 mm. Il pannello del FX-SEND è
   profondo 87 mm: la scheda (100 mm) sporge ~13 mm sotto il modulo accanto.
2. **Altezza.** Il generatore disegna rettangoli 100 × 220 (dec. 142). La dec. 158 ha poi
   inclinato il mixer: le schede diventano **trapezi da ~185 mm (in fondo) a ~120 mm (davanti)**.
   Il FX-SEND che PASSA a 220 mm, sotto il suo pannello ha 139 → 129 mm. Tutte le schede
   disegnate finora (FX-SEND, MIC, MONO, master, canale, FX-RET, PSU-IN) sono più alte del
   loro posto vero.

## Conteggi veri di oggi (todo 167)

| Scheda | Impronte | Posto sotto il pannello (PIANO) | Esito |
|---|---|---|---|
| FX-SEND | 120 | 139 → 129 mm, capienza ~106 | non sta |
| CANALE | 380 | 173 → 139 mm, capienza ~415 su 1 scheda (stima a due lati) | al 92 %, ma una 100 × 220 ne porta ~280 |
| FX-RET | 410 | 173 → 142 mm, capienza ~379 | non sta |

La capienza del PIANO conta schede più larghe di 100 mm. Il generatore oggi fa 100 mm.

## Proposta

**P1 — Il C96 resta 3×32 per tutte le classi.** Un connettore corto (3×16) rompe la mappa
comune delle righe a e c (potenza fino ad a26, controllo fino a c28): ogni modulo dovrebbe
avere la sua. No.

**P2 — La scheda non deve stare dentro il suo pannello: deve stare dentro la sua colonna.**
Il C96 sta sul fondo, il pannello sta sopra. La scheda può essere più profonda del pannello se
sotto il pannello vicino c'è posto. Nei fogli A, B e C del PIANO il filtro lascia la colonna
dei canali: il FX-SEND si allunga fino al bordo davanti (PIANO, strada 2) e il C96 ci sta.
Serve solo scegliere il foglio.

**P3 — Il generatore impara la forma vera della scheda.** Una riga nel file del modulo:
`board=(L, H_fondo, H_davanti)` per il trapezio della dec. 158. Il generatore taglia il bordo
in diagonale e tiene i pezzi dentro (stessa logica del margine dal bordo di oggi). Ogni
modulo prende le sue altezze dal PIANO. Lavoro di Claude, nessuna decisione.

**P4 — Le schede grandi si dividono, come il master.** Canale e FX-RET non stanno in una
scheda (note in `pcb/canale/NOTE.md` e `pcb/fx-ret/NOTE.md`): due schede affiancate sotto il
pannello, una col C96 e una per il blocco più grande (isolator; reroute). Il PIANO lo
prevedeva già per il master.

## Decisioni che servono a Filippo

1. Il foglio di disposizione (A, B o C del PIANO, `docs/pannelli/pannelli.pdf` pagine 4-7):
   decide dove si allunga il FX-SEND e quanto spazio hanno canale e FX-RET.
2. Canale e FX-RET su due schede affiancate ciascuno (come il master, dec. 142): sì o no.

Dopo queste due: P3 nel generatore, poi tutte le schede rigenerate col trapezio.
