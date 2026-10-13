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
| Frequenza filtro (HPF, LPF) | 2 | lineare al centro, più ripida ai due estremi (dec. 70) |

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

## 4. Cosa resta

- Frequenza del filtro: la rete è la stessa (un ramo diretto e un ramo
  rovesciato); i valori si calcolano con `shaper_fit.py` dalla tabella
  θ→f quando la law è chiusa a banco con la pre-distorsione del
  converter (dec. 70). Non simulata qui.
- Trimmer: uno di zero e uno di fondo scala per shaper dove la law è
  critica (reroute, drive); gli altri a resistenze fisse.
- Verifica con diodi veri e op-amp vero (offset): banco.
