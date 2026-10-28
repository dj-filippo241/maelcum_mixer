# Sistema — SHAPER a tratti: la rete che dà la curva alle manopole (2026-10-13)

> **Stato: v0.1 — circuito definito e VERIFICATO in simulazione.** Chiude
> il punto «implementazione a componenti discreti dello shaper» rimasto
> aperto in FX (§7), filtro (§4), drive 5-way e position 5-way. Finora lo
> shaper era solo una curva matematica dentro le simulazioni. Valori
> [PROVVISORIO — regola 3], taratura a banco come da decisione 70.
> Simulazioni: `sim/shaper/` (`shaper_fit.py` + tre netlist).

## 1. A cosa serve

Una manopola dà una tensione che sale in modo uniforme, 0-5 V. Molti
comandi del mixer vogliono invece una curva: tanta corsa dove serve
precisione, poca dove non serve. Lo shaper trasforma la tensione della
manopola nella curva voluta, prima che arrivi al VCA o al filtro.

Dove sta nel mixer:

| Comando | Quanti | Curva |
|---|---|---|
| Reroute e self-feedback FX | 16 | 0 → −100 dB, finissima negli ultimi dB (SPEC §7) |
| Drive 5-way | 1 | 0 / +7 / +9,5 / +12 / +14 / +16 dB (dec. 82/87) |
| Drive filtro (HPF, LPF) | 2 | come il drive 5-way (filter-module §5bis) |
| Position 5-way | 5 | frequenza esponenziale su 2,6 ottave |
| MASTER e BOOTH | 2 | MASTER: silenzio → 0 dB allo scatto al centro → +6 dB (dec. 139); BOOTH: curva del fader |
| Frequenza filtro (HPF, LPF) | 2 | LPF: curva Xone:96 nel 90 % centrale, più ripida negli ultimi 5 % (dec. 70/102); HPF: 20 Hz a 0 %, senza ramo basso (dec. 137) |

## 2. Circuito: un op-amp, pochi diodi

```
 Vx (dalla manopola, bufferizzata) ──┬── Rm ───────────────────┐
                                     ├── Ra1 ──●── D1 ─────────┤
                                     │         └── Rb1 ── −5 V │
                                     ├── Ra2 ──●── D2 ─────────┤   Rf 10k
                                     │         └── Rb2 ── −5 V ├──/\/\──┐
                                     └── Ra3 ──●── D3 ─────────┤        │
                                               └── Rb3 ── −5 V │        │
                                                     massa ────┤−\      │
                                                     virtuale  │  >─────┴── Vout
                                                         0 V ──┤+/
```

- Sommatore invertente. Il ramo Rm dà la pendenza di base.
- Ogni ramo a diodo resta spento finché Vx è sotto la sua soglia; sopra,
  aggiunge pendenza. Soglia = rapporto Ra/Rb; pendenza aggiunta = 1/Ra.
- Più rami = più tratti. Le curve che «accelerano» in un solo verso si
  fanno così. Per un tratto che deve accelerare verso il BASSO della
  corsa si aggiunge un ramo col diodo rovesciato e Rb verso +5 V:
  stesso circuito, nessun op-amp in più (serve alla law del filtro).
- Dove serve la zona di precisione a fine corsa, la manopola si cabla
  rovescia: in quella zona tutti i diodi sono spenti e la curva dipende
  solo da resistenze.
- La curva si disegna a livello di volt (uscita fino a ~6 V) e si divide
  per 10 solo all'ingresso del VCA: così pochi mV di deriva dei diodi
  pesano centesimi di dB.
- Costo per manopola: 1 sezione di op-amp, 2-3 diodi 1N4148, 6-8
  resistenze all'1 %. Totale mixer: ~26 shaper ≈ 7 quad op-amp.

## 3. Risultati (LTspice, valori E96, diodo 1N4148, 20 / 35 / 50 °C)

La temperatura è quella interna del telaio fanless, da freddo a caldo.

**Reroute FX** (`shaper-reroute.cir`, 3 rami, manopola rovescia):

| Target | 0 | −0,5 | −1 | −2,5 | −4 | −7 | −10 | −15 | −20 | −30 | −40 | −70 | −100 dB |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| errore 20 °C | 0,00 | −0,05 | −0,10 | +0,24 | +0,08 | +0,20 | +0,23 | +0,21 | +0,04 | +1,4 | +0,8 | +6,9 | +1,8 |
| errore 35 °C | 0,00 | −0,05 | −0,10 | +0,17 | −0,05 | +0,06 | +0,08 | +0,07 | −0,24 | +0,9 | −0,5 | +3,4 | −2,0 |
| errore 50 °C | +0,01 | −0,04 | −0,10 | +0,09 | −0,19 | −0,09 | −0,06 | −0,07 | −0,60 | +0,3 | −2,2 | −0,2 | −5,7 |

Da 0 a −15 dB, la zona dove si gioca il feedback dub, l'errore sta entro
±0,25 dB e non si muove con la temperatura. Sotto −30 dB l'errore sale
a qualche dB: lì il ritorno è quasi chiuso e non si sente.

**Drive** (`shaper-drive.cir`, 2 rami): errore entro **±0,2 dB** su tutta
la corsa e a tutte le temperature.

**Position 5-way** (`shaper-position.cir`, 3 rami): frequenza entro ±1 %
col fit ideale; con valori E96 fino a +2,2 % a 35 °C e +3,6 % a 50 °C
(circa mezzo semitono a fine corsa, a caldo). Un trimmer sul ramo
principale lo riporta dentro. Il «±1,8 %» scritto in five-way §4.2 era
la sola matematica della curva.

**Frequenza del filtro** (`shaper-filtro-freq.cir` + `shaper_filtro_tab.py`,
2026-10-13, law della decisione 102: curva Xone:96 nel 90 % centrale).
Uscita lineare in ottave, 0,5 V/ottava. Ramo principale Rm 9,09k; ramo
alto (diodo diretto, sopra il 95 %) Ra 20k / Rb 24,3k verso −5 V; ramo
basso (diodo rovesciato, sotto il 5 %) Ra 11,3k / Rb 80,6k verso −5 V
(nota: per avere la soglia a tensione positiva la Rb del ramo rovesciato
va a −5 V, non a +5 V). Zero e fondo scala tarati al 25 % e al 75 %.

| Manopola | Target | 20 °C | 35 °C | 50 °C |
|---|---|---|---|---|
| 0 % | 10 Hz | +4,1 % | −0,5 % | −4,9 % |
| 2,5 % | 14,1 Hz | +0,4 % | −3,7 % | −7,7 % |
| 5 % | 20 Hz | −5,6 % | −8,5 % | −11,7 % |
| 10 % | 29,4 Hz | −0,1 % | −0,3 % | −0,8 % |
| 25-75 % | 93 Hz-4,3 kHz | 0,0 % | 0,0 % | 0,0 % |
| 90 % | 13,6 kHz | +0,2 % | +0,6 % | +1,4 % |
| 95 % | 20 kHz | +3,0 % | +5,3 % | +8,3 % |
| 97,5 % | 26,5 kHz | −1,9 % | +1,2 % | +4,8 % |
| 100 % | 35 kHz | −5,2 % | −1,6 % | +2,2 % |

Dal 10 al 90 % della corsa la curva è esatta e non si muove con la
temperatura (sole resistenze). Ai due ginocchi (5 % e 95 %) il diodo
arrotonda lo spigolo: errore fino a −12 % a caldo, cioè 17,7 Hz al posto
di 20 Hz. Tolleranza di progetto ±5-10 % (dec. 74): fuori solo in quel
punto, a 50 °C, in zona infrasonica. Accettato come partenza.

La tabella sopra vale per la sezione **LPF**. **Sezione HPF, dec. 137
(2026-10-27)** (`shaper-filtro-freq-hpf.cir`, `-hpf-hot.cir`; tabella con
`shaper_filtro_tab.py <log> --hp`): legge 20 Hz · 1000^(θ/0,95) fino al
95 %, poi 20 → 35 kHz. Il ramo basso sparisce; Rm 9,09k → **9,53k**, ramo
alto Ra 20k / Rb 24,3k → **17,8k / 21,5k**. Il ginocchio basso non c'è più:
0-75 % esatto a tutte le temperature (errore 0,0 %, 37 Hz al 8,5 %).

| Manopola | Target | 20 °C | 35 °C | 50 °C | 65 °C | 75 °C |
|---|---|---|---|---|---|---|
| 0 % | 20 Hz | 0,0 % | 0,0 % | 0,0 % | 0,0 % | −0,1 % |
| 8,5 % | 37,1 Hz | 0,0 % | 0,0 % | 0,0 % | 0,0 % | −0,1 % |
| 10-75 % | 41 Hz-4,7 kHz | 0,0 % | 0,0 % | 0,0 % | 0,0 % | −0,1 % |
| 90 % | 13,9 kHz | +0,2 % | +0,4 % | +1,1 % | +2,4 % | +3,5 % |
| 95 % | 20 kHz | +2,4 % | +4,7 % | +7,6 % | +11,3 % | +14,0 % |
| 97,5 % | 26,5 kHz | −3,5 % | −0,4 % | +3,4 % | +7,6 % | +10,5 % |
| 100 % | 35 kHz | −7,5 % | −3,7 % | +0,3 % | +4,8 % | +7,9 % |

Il ginocchio alto si comporta come nella LPF (a caldo LPF: +14,5 % al
95 % a 75 °C). Due shaper diversi per HPF e LPF: stessa famiglia, un ramo
in meno nell'HPF.

**Fader** (`shaper-fader.cir`, 3 rami, fader rovescio; dec. 126,
2026-10-22): curva [PROVVISORIO] −12 dB a metà corsa; dal 45 % in su
errore entro ±0,35 dB a 20-50 °C, fino al 20 % entro ±1 dB; fader chiuso
≥ 102 dB. Tabella: `sim/cdj/RISULTATI-fader-vca.md`.

**MASTER** (`shaper-master.cir` + `master_fit.py`, 4 rami, pot rovescio;
dec. 139, 2026-10-28, todo 181). Curva [PROVVISORIO, dec. 129]: 0 dB allo
scatto al centro, sopra lineare in dB fino a +6, sotto 40 log10(2θ)
(−12 dB al 25 %), fondo corsa chiesto a −140 dB. Il +6 dB viene da un ramo
d'offset Roff 137k verso −5 V (uscita +0,366 V a fine corsa; convenzione
della famiglia: uscita negativa = taglio; il verso sul pin EC− lo dà lo
stadio del partitore, `sistema-vca-trim.md` §3.2). Valori E96: Rm 68,1k ·
rami (Ra/Rb) 1,91k/2,43k · 16,9k/38,3k · 1,82k/2,43k · 1,96k/2,61k.
Errore in dB:

| Manopola | Target | 20 °C | 35 °C | 50 °C |
|---|---|---|---|---|
| 100 % | +6.0 dB | -0.02 | -0.01 | -0.01 |
| 90 % | +4.8 dB | -0.02 | -0.02 | -0.01 |
| 80 % | +3.6 dB | -0.02 | -0.02 | -0.01 |
| 70 % | +2.4 dB | -0.03 | -0.02 | -0.02 |
| 60 % | +1.2 dB | -0.03 | -0.03 | -0.02 |
| 55 % | +0.6 dB | -0.03 | -0.03 | -0.03 |
| 50 % | +0.0 dB | -0.06 | -0.09 | -0.17 |
| 47 % | -1.1 dB | +0.50 | +0.33 | +0.08 |
| 45 % | -1.8 dB | +0.70 | +0.40 | +0.06 |
| 40 % | -3.9 dB | +0.59 | +0.16 | -0.28 |
| 35 % | -6.2 dB | +0.31 | -0.16 | -0.62 |
| 30 % | -8.9 dB | +0.22 | -0.25 | -0.73 |
| 25 % | -12.0 dB | +0.55 | +0.07 | -0.41 |
| 20 % | -15.9 dB | +1.54 | +1.03 | +0.49 |
| 15 % | -20.9 dB | +3.35 | +2.40 | +0.91 |
| 10 % | -28.0 dB | +2.53 | -2.23 | -8.54 |
| 5 % | -40.0 dB | -13.09 | -23.40 | -34.53 |
| 0 % | silenzio | -101 dB | -113 dB | -126 dB |

Sopra il centro la curva è fatta di sole resistenze: esatta e ferma con la
temperatura. Allo scatto il primo diodo comincia appena a condurre: −0,17 dB
a 50 °C, uguale sui due lati (una CV sola), si azzera a banco col trimmer
d'offset. Da −16 a −28 dB l'errore arriva a +3 dB a freddo; sotto il 10 %
la curva cade più in fretta del bersaglio (−52…−75 dB al 5 %): lì il master
è già quasi muto. Pot chiuso: −101 dB a 20 °C, requisito ≤ −90 dB.

**BOOTH** (−∞ → 0 dB, senza scatto, dec. 125): stessa curva e stesso shaper
del fader (`shaper-fader.cir`, −12 dB a metà corsa). [PROVVISORIO, dec. 129]

## 4. Cosa resta

- Frequenza del filtro: manca la pre-distorsione dell'errore del
  converter (filter-module §4, correzione ≤ 40 mV agli estremi): si
  somma a banco coi due trimmer.
- Trimmer: uno di zero e uno di fondo scala per shaper dove la law è
  critica (reroute, drive); gli altri a resistenze fisse.
- Verifica con diodi veri e op-amp vero (offset): banco.
