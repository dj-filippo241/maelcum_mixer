# LICKSHOT, scheda unica v0.1-bozza (2026-11-18, todo 376)

Schema, PCB e distinta della lickshot in rack 1U (dec. 179-196), scritti col generatore. Fonte
unica: `lickshot.py`. Circuito da `docs/fase4/lickshot.md` v0.3 e dai netlist di `sim/lickshot/`
(`profondita.cir`, `giro-att14.cir`, `mix-uscita.cir`); comandi alle x di
`docs/pannelli/lickshot-1u.json` (dec. 196).

Rigenerare (~4 minuti; con `--solo-schema` pochi secondi):

```bash
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 pcb/lickshot/lickshot.py
```

## Stato

- **PASSA** (2026-11-18). ERC 0 errori. DRC 0 violazioni; avvisi: 36 silk_edge_clearance (le
  serigrafie dei pot escono dal bordo davanti, voluto), 4 silk_overlap, 4 silk_over_copper,
  11 net_conflict attesi. Freerouting chiuso al **4o tentativo** su 4 (giri 1-3: 1-2 reti aperte
  fra +5V, RAMP, VMID): margine stretto, un giro nuovo può dare NON PASSA. Se succede, alzare
  `d.route_tries`.
- Controllo audio: A1 2 (decoupling del 5 V dei V3102, 9,65 mm), A2 4, A3 9, A4 0, A5 0.
- 108 pezzi, 73 righe di distinta. Silicio: TLC2272 x5, CD4069UB, CD4046B, V3205D x2, V3102 x2,
  78L09, 78L05, 2N3904, 1N5819, 1N4148 + 1N4148W x2. Coincide con la stima di lickshot.md §5
  (5 trimmer: 2 polarizzazioni, 2 cancellazioni del clock, fondo scala di TEMPO).

## Forma della scheda

- 280 x 80 mm, 4 strati, orizzontale nel rack. Bordo davanti (y = 0) contro il pannello; la
  scheda copre le x da 100 a 380 mm del pannello (`X0` in `lickshot.py`).
- Pot Alps RK09L **orizzontali**: l'albero esce dal bordo davanti, il fronte del corpo sta sul
  bordo. Il LED da 3 mm è a 90 gradi (impronta Z 6 mm).
- FIRE (24 mm), jack d'uscita e presa DC stanno sui pannelli e arrivano coi fili: J2 (FIRE, vicino
  al tasto a destra), J3 (uscita) e J1 (DC) sul bordo dietro.
- Quattro fori M3 senza pad: la massa arriva solo dal MONO (RISULTATI §6).

## Le scelte NOTA (da decidere o verificare)

1. Scheda orizzontale coi pot a 90 gradi: lickshot.md §5 lasciava aperta anche la scheda verticale.
   Coi comandi tutti in una riga (dec. 196) basta una scheda sola. [C] da confermare.
2. Altezza dei pot sulla scheda: l'albero sta a 17,45 mm dal fondo del pannello (y 27 su 44,45).
   Distanziali della scheda = 17,45 mm meno l'altezza dell'albero dal catalogo Alps. Il LED va
   alla stessa altezza (Z dell'impronta).
3. ALTEZZA: reostato fra cursore e capo orario di un pot **logaritmico inverso (C)**: R scende in
   modo esponenziale, ottave uguali, nota che sale in senso orario (deduzione mia dal modello:
   `r_alt`). Con un pot A la legge si rovescia. VELOCITÀ e TEMPO lineari; VOLUME e LIVELLO ECO A.
4. Saturazione del giro: i netlist hanno RIPETIZIONI x 1,1, partitore 15k/10k e x2,5. Qui il 1,1 è
   dentro il partitore (12,7k/10k = 0,44) e l'x2,5 resta dopo i diodi: un op-amp in meno. Il
   cursore di RIPETIZIONI (fino a 2,5k) si somma al 12,7k: a metà corsa il giro perde ~0,9 dB.
   Da simulare con lo stadio vero.
5. Uscite dei BBD: 47k a massa (carico dei source follower) e trimmer 10k fra OUT1 e OUT2. Valori
   da rileggere sullo schema d'applicazione del V3205D.
6. Polarizzazione dei BBD: trimmer 10k fra +5 V e massa, 100k verso l'ingresso, 1 uF sul cursore.
   Ingresso dal dominio a 9 V con 1 uF, senza buffer (sorgente 8k del partitore -14 dB).
7. Clock: R fra OX2 e OX1, C 100 pF fra OX3 e OX1 (MN3102 p. 107, letto dall'immagine). Il secondo
   V3102 ha OX1 dall'OX3 del primo, OX2 e OX3 aperti. TEMPO = 250k + 22k + trimmer 10k.
8. Condensatori grandi in ceramica X7R 1206 (10 uF del colpo, 2,2 uF del make-up, 1 uF dei BBD):
   film se all'ascolto si sente.
9. FIRE: tasto normalmente aperto in serie fra il guadagno del colpo e VOLUME, 100k verso VDD/2 a
   tasto aperto.
10. Pinout di V3102 e V3205D dai datasheet citati nella `desc` dei simboli. Il V3102 viene dal
    gemello MN3102: da confermare sul foglio CoolAudio o sul pezzo (lickshot.md §4).

Verificato in: Python no / LTspice no (gli stadi veri della scheda non sono simulati; i netlist
v0.2-v0.3 usano op-amp ideali) / Live no.
