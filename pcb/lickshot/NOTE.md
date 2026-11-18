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

- **PASSA** a un BBD (2026-11-19, dec. 198): Freerouting chiuso al 4o tentativo su 6. Margine
  stretto: se un giro nuovo dà NON PASSA, alzare `d.route_tries`.
- PASSA a due BBD (2026-11-19, v0.1 corretta: RISULTATI-scheda §2-§3). Scheda allungata da 80 a 95 mm
  di profondità: col trimmer di taratura della make-up il blocco dell'eco non trovava più posto
  (due giri NON PASSA). Freerouting chiuso al 1o tentativo su 6 (`d.route_tries = 6`,
  `d.link_pairs = True` per i trimmer a reostato). Controllo audio A1 da 2 a 3.
- Giro del 2026-11-18 (280 x 80, prima delle correzioni): PASSA al 4o tentativo su 4.
- Silicio (dec. 198: un BBD e un clock): TLC2272 x5, CD4069UB, CD4046B, V3205D, V3102, 78L09, 78L05, 2N3904, 1N5819,
  1N4148 + 1N4148W x2. Trimmer: 2 polarizzazioni, 2 cancellazioni del clock, fondo scala di TEMPO
  (3266W), taratura del giro (3224W SMD 500k). Dopo la dec. 198: una polarizzazione e una
  cancellazione.
- Preventivi per 5 schede: `PREVENTIVI.md` (calcolati su 280 x 80).

## Forma della scheda

- 280 x 95 mm, 4 strati, orizzontale nel rack. Bordo davanti (y = 0) contro il pannello; la
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
   dentro il partitore (12,7k/10k = 0,44) e l'x2,5 resta dopo i diodi: un op-amp in meno.
   **Confermata** (RISULTATI-scheda §2): fondo corsa esatto (+0,83 dB), -0,7 dB a 1/4 e 3/4,
   -0,9 dB a metà. A RIPETIZIONI tutto il giro si tiene a 0,90 V, come la v0.2.
5. Uscite dei BBD: **corretta** il 2026-11-18. Lo schema d'applicazione del V3205D mette 100k
   per uscita (anche RL delle caratteristiche) e 5,6k + 5,6k per sommarle: qui 100k e il trimmer
   10k. Il cursore del trimmer (~3k) davanti ai 10k della make-up toglieva fino a 2,1 dB al giro:
   make-up ora con ingresso 47k e reazione 100k + trimmer 500k (taratura del giro, copre la
   dispersione di -4...+4 dB per chip del datasheet). RISULTATI-scheda §2.
6. Polarizzazione dei BBD: trimmer 10k fra +5 V e massa, 100k verso l'ingresso, 1 uF sul cursore.
   Ingresso dal dominio a 9 V con 1 uF, senza buffer (sorgente 8k del partitore -14 dB): costa
   0,7 dB, recuperati dal trimmer della make-up. Confermata. Lo schema d'applicazione tara lo
   stesso punto con un trimmer da 100k «per la minima distorsione»: si tara sul pezzo.
7. Clock (dec. 198): un solo V3102, R fra OX2 e OX1, C **220 pF** C0G fra OX3 e OX1 (MN3102
   p. 107, letto dall'immagine): 50-5 kHz, 41-405 ms. TEMPO = 250k + 22k + trimmer 10k.
8. Condensatori grandi in ceramica X7R 1206 (1 uF dei BBD e della make-up): film se all'ascolto
   si sente. Il 10 uF del colpo non c'è più: il colpo entra con 100 nF film e 110k (sotto).
9. FIRE: tasto normalmente aperto in serie fra il guadagno del colpo e VOLUME, 100k verso VDD/2 a
   tasto aperto.
10. Pinout di V3102 e V3205D dai datasheet citati nella `desc` dei simboli. Il V3102 viene dal
    gemello MN3102: da confermare sul foglio CoolAudio o sul pezzo (lickshot.md §4).
11. **Corretta** il 2026-11-18: il colpo entrava con 10 uF -> partitore 1k/100 verso VMID. Il VCO
    gira sempre: a ogni fronte +-4 mA nel buffer di VDD/2, VMID scosso di +-0,2 V e disturbo nel
    giro anche a FIRE aperto. Ora 100 nF film -> 110k nell'invertente (19,1k): stesso plateau
    0,78 V, stesso passa-alto 14,5 Hz, VMID entro +-10 mV (RISULTATI-scheda §3).

Verificato in: Python no / LTspice sì (stadi audio della scheda col TLC2272 tarato sul modello TI,
BBD ideali: `sim/lickshot/scheda.inc`, RISULTATI-scheda.md) / Live no.
