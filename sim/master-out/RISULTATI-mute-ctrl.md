# Mute controller del master [L]: tempi (todo 182, 2026-10-28)

Netlist: `sim/master-out/mute-ctrl.cir`. Design: master-out §3.7; soglie e
tempi del supervisore: `docs/fase3/sistema-psu-esterno.md` §2.5, §2.6, §4.4.

## Circuito simulato

- **Supervisore.** AC_OK (open collector dal box, alto = rete presente) e la
  finestra del +22 (< 21,2 V) tirano giù RAILS_OK. Sono comparatori open
  collector in wired-OR (LM393/LM339). Le altre finestre (±19, [M], +5) si
  aggiungono sullo stesso nodo, uguali.
- **Timer.** RAILS_OK carica CT 2,2 µF attraverso RT 1,2 MΩ. Un comparatore
  confronta CT con VREF 2,495 V (TL431) e dà OKD (open collector, pull-up 10k).
  Il diodo DT scarica CT subito quando RAILS_OK cade: mute subito, riarmo lento.
- **Relè.** Master, booth, rec: Omron G6K-2 5 V (178 Ω, 28,1 mA), eccitati =
  suono, diseccitati = muto (failsafe). Driver NMOS logic level (AO3400)
  pilotato da OKD.
- **GLOBAL_MUTE (c9).** NMOS open drain (2N7002) pilotato da OKD: **basso =
  suona, alto = muto**. Le pull-up stanno nei moduli che ascoltano (100k su ogni
  FX-SEND). Master assente o spento: la linea resta alta, i moduli restano muti.

Sequenza: +5 sale in 50 ms; AC_OK alto a 0,10 s; +22 in finestra a 0,15 s.
Buco di rete di 20 ms a 3,000 s. Spegnimento a 7,000 s con il caso peggiore del
box (rete −10 %: i regolatori escono dopo 25,9 ms). Tolleranza di CT ±10 %.

## Risultati

| Misura | CT −10 % | nominale | CT +10 % | Requisito |
|---|---|---|---|---|
| Accensione: suono dopo l'ultima condizione in finestra | 1,61 s | 1,79 s | 1,97 s | 1,5-2 s (§3.7) |
| Riarmo dopo un buco di rete di 20 ms | 1,57 s | 1,74 s | 1,91 s | 1,5-2 s (psu-esterno §4.4) |
| GLOBAL_MUTE alta dopo la caduta di AC_OK | 0,048 ms | 0,047 ms | 0,044 ms | subito |
| Idem allo spegnimento | 0,067 ms | 0,069 ms | 0,069 ms | subito |
| Bobine scariche (10 % della corrente), diodo solo | 1,35 ms | 1,35 ms | 1,35 ms | |
| Idem, diodo + zener 12 V | 0,30 ms | 0,30 ms | 0,30 ms | |
| Corrente nelle bobine durante l'accensione (prima del timer) | 0,8 µA | 0,8 µA | 0,8 µA | nessun impulso |

- **Spegnimento: margine ampio.** Bobina scarica in 1,35 ms, più il rilascio
  meccanico del G6K (3 ms max: dato di catalogo, da verificare sul PDF Omron):
  contatti aperti entro ~4,4 ms dalla caduta di AC_OK. I regolatori del box
  escono dopo 25,9 ms nel caso peggiore. Basta il diodo solo; lo zener non serve.
- **FX-SEND.** GLOBAL_MUTE sale in meno di 0,07 ms; poi gli assign si aprono
  con la rampa di 0,09 ms (pcb/fx-send/NOTE.md punto 12). La matrice del
  self-feedback è muta prima che i rail si muovano.
- **Tensione sul driver** con lo zener: 18,4 V (AO3400 regge 30 V). Col diodo solo 5,8 V.

## Errori trovati e corretti in questa simulazione

1. **Pull-up di OKD caricata dai transistor.** Primo giro con due NPN da 2,2k
   di base: OKD restava a 1,4 V, le bobine prendevano 29 mA invece di 84 e il
   NMOS di c9 non si accendeva. Correzione: driver NMOS pilotati in tensione.
2. **Diodo di scarica 1N4148.** Lasciava ~0,6 V su CT dopo un buco: riarmo a
   1,38 s. Con lo Schottky BAT54 e RT 1,2 MΩ (era 1,0 MΩ) il riarmo sta in 1,5-2 s.

## Valori [PROVVISORIO] per la PCB del master

RT 1,2 MΩ 1 % · CT 2,2 µF film o X7R ≥ 16 V · DT BAT54 · VREF TL431 · pull-up
RAILS_OK e OKD 10k · driver relè AO3400 (o 2N7002 per relè singolo) con 100 Ω
di gate · diodo 1N4148 su ogni bobina · c9: 2N7002 open drain.

## Limiti

- Comparatori ideali con isteresi; il comportamento di LM393 sotto ~2 V di
  alimentazione non è modellato. Non conta: sotto 3,75 V la bobina non chiude.
  Il gate di c9 a 1,5 V sta sotto la soglia del 2N7002.
- Induttanza della bobina non dichiarata da Omron: stimata 150 mH per bobina
  (anche 50 mH: rilascio più veloce).
