# RISULTATI — isolator di canale riallineato a incroci C e curva PIONEER (todo 211, 2026-11-04)

Decisioni: 152 (incroci C, 150 Hz LR2 / 350 / 3150 Hz), 146 (curva PIONEER).
Riferimento: prototipo `proto-max/coefficienti/canale.py` (`bande()`, `INCROCI["C"]`,
`PENDENZE["C"]`, `banda_pioneer`), valutato a fs = 192 kHz.

Netlist (op-amp reali OP1654 / OP1612 di `sim/lib/opamp-audio.inc`):

- `iso-incc-banca.inc`: circuito comune (banca, manopole, somma, servo).
- `iso-incc-ac.cir`: risposta, 20 casi di manopole × 2 leggi del pot.
- `iso-incc-noise.cir`: rumore, densità a 16 punti (`sim/mic/noise_total.py`).
- `iso-incc-dc.cir`: continua e servo.
- `confronto_incc.py <log>`: tabella hardware contro prototipo.
- `legge_pot_ricerca.py`, `legge_pot_4sezioni.py`: fattibilità della curva PIONEER.

Legge del pot nei netlist: `law=0` pot lineare B (RK14K doppio 10k con scatto,
residuo 20 Ω, il pezzo a catalogo); `law=1` taper «PIONEER ideale» (partitore
0,5·(2θ)^1,5 sotto il centro, θ sopra). Il secondo NON esiste a catalogo: serve
solo a separare l'errore della banca da quello della manopola.

## 1. Topologia nuova (ingegneria)

Stessa struttura del prototipo, banda per banda:

| Banda | Prototipo | Hardware | Segno |
|---|---|---|---|
| LOW | LP2(f1) · AP(f2) · AP(f3) | SK LP Q 0,5 + AP2 + AP2 | + · − · − = + |
| LOW-MID | −HP2(f1) · LP4(f2) · AP(f3) | (spina) SK HP Q 0,5 → SK + SK → AP2 | + · + · − = − |
| MID-HIGH | −HP2(f1) · HP4(f2) · LP4(f3) | (spina) SK HP Q 0,5 → SK SK → **MFB LP** + SK | − |
| HIGH | −HP2(f1) · HP4(f2) · HP4(f3) | (spina) SK HP Q 0,5 → SK SK → **MFB HP** + SK | − |

LP2 − HP2 con Q 0,5 è un allpass del 1o ordine: la somma al centro resta piatta.
Il segno «−» dei tre rami alti si ottiene senza invertitori: una delle due sezioni
LR4 a 3150 Hz è un MFB (invertente, guadagno −1) invece di un Sallen-Key. Sparisce
anche l'invertitore del LOW-MID della v0.4.

Valori [PROVVISORI — regola 3], R calcolate (in E96 0,1 % a banco), C 1 % C0G/film:

| Cella | C | R |
|---|---|---|
| f1 150 Hz, SK LP e HP Q 0,5 (R uguali, C uguali) | 220 n | 4,82 k |
| f2 350 Hz, SK LP (C a massa 100 n, C fb 200 n) e SK HP (100 n) | 100 n / 200 n | 3,22 k (HP: 3,22 k / 6,43 k) |
| f2 allpass AP2 | 47 n / 94 n | 6,84 k / 13,7 k / 10,3 k |
| f3 3150 Hz, SK LP e HP | 10 n / 20 n | 3,57 k (HP: 3,57 k / 7,15 k) |
| f3 MFB HP (tre C uguali, R2 = 4,5 R1) | 10 n | 2,38 k / 10,7 k |
| f3 MFB LP (tre R uguali, C a massa = 4,5 C fb) | 4,7 n / 21,15 n | 5,07 k |
| f3 allpass AP2 | 4,7 n / 9,4 n | 7,60 k / 15,2 k / 11,4 k |

Le C sono state alzate dopo il primo giro (`iso-incc-banca.inc` con C più piccole:
centro −96,2 dBu A-wtd): impedenze più basse, rumore tornato al livello della v0.4.
Le C da 200 n, 94 n, 20 n, 9,4 n e 21,15 n sono coppie in parallelo o si
riscalano le R su un valore E6: da fissare col layout.

## 2. Risposta: hardware contro prototipo (`iso-incc-ac.cir`)

Guadagno in dB. «HW» = hardware con taper PIONEER ideale (law 1); con pot lineare
(law 0) le righe a manopola 0, 0,5 e 1 sono identiche (la legge conta solo fra
gli estremi e il centro).

| Manopole | 20 | 50 | 150 | 229 | 350 | 1050 | 3150 | 5000 | 8000 | 20k |
|---|---|---|---|---|---|---|---|---|---|---|
| tutte al centro, HW | +0,004 | +0,004 | +0,004 | +0,003 | +0,002 | +0,004 | +0,002 | +0,002 | +0,002 | +0,001 |
| LOW a zero, HW | −33,4 | −19,7 | −6,0 | −3,1 | −1,5 | −0,2 | 0,0 | 0,0 | 0,0 | 0,0 |
| LOW a zero, prototipo | −35,2 | −20,0 | −6,0 | −3,1 | −1,5 | −0,2 | 0,0 | 0,0 | 0,0 | 0,0 |
| LOW-MID a zero, HW | −0,2 | −0,9 | −5,7 | **−7,7** | −4,7 | −0,1 | 0,0 | 0,0 | 0,0 | 0,0 |
| LOW-MID a zero, prototipo | −0,2 | −0,9 | −5,7 | −7,8 | −4,8 | −0,1 | 0,0 | 0,0 | 0,0 | 0,0 |
| MID-HIGH a zero, HW | 0,0 | 0,0 | −0,1 | −1,0 | −4,7 | **−26,5** | −6,0 | −1,3 | −0,2 | 0,0 |
| MID-HIGH a zero, prototipo | 0,0 | 0,0 | −0,1 | −1,0 | −4,8 | −27,2 | −6,0 | −1,3 | −0,2 | 0,0 |
| HIGH a zero, HW | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 | −0,1 | −6,0 | −17,1 | −31,2 | −46,7 |
| HIGH a zero, prototipo | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 | −0,1 | −6,0 | −17,3 | −32,6 | −64,7 |
| LOW + LOW-MID a zero, HW | −48,0 | −47,9 | −33,9 | −19,0 | −7,4 | −0,3 | 0,0 | 0,0 | 0,0 | 0,0 |
| MID-HIGH + HIGH a zero, HW | 0,0 | 0,0 | −0,1 | −1,0 | −4,7 | −28,9 | −43,9 | −46,2 | −47,3 | −47,9 |
| tutte a zero, HW | −48,0 piatto | | | | | | | | | |
| una banda al massimo | +6,0 nella banda, +3,5 all'incrocio, 0 fuori (scarto dal prototipo ≤ 0,02 dB) | | | | | | | | | |
| tutte al massimo | +6,01 piatto (prototipo +6,02) | | | | | | | | | |

Esiti:

- **La banca segue il prototipo entro 0,05 dB** dovunque il prototipo sta sopra
  −10 dB: centro, bande al massimo, incroci, punti della curva. Fase: entro
  0,5° da 20 Hz a 20 kHz (al centro).
- **Gli scarti più grandi stanno solo nel fondo dei tagli** e vengono dal
  residuo del pot (20 Ω su 10 kΩ), non dalla banca: il prototipo scende a
  −64 dB (HIGH a zero, 20 kHz), l'hardware si ferma a −47…−48 dB. Lo scarto
  massimo dove il prototipo sta sopra −40 dB: 1,9 dB (LOW + LOW-MID a zero a
  150 Hz: −33,9 contro −35,8).
- **FINDING (residuo del pot).** La dec. 127 scrive «banda chiusa a circa
  −54 dB» con residuo ≤ 20 Ω. Il −54 era calcolato con 10 Ω (eq-isolator §5).
  Con 20 Ω, il caso peggiore garantito, una banda chiusa sta a **−48 dB**
  (20 Ω/10 kΩ = −54 dB, più i 6 dB della somma ×2). Con 10 Ω torna −54. Non è
  un effetto degli incroci C: vale anche per la v0.4. Il muto del canale resta
  il fader (−100 dB).
- Come nel prototipo, il LOW-MID chiuso da solo scava poco: −7,7 dB a 229 Hz.
  È la conseguenza dell'incrocio dolce a 150 Hz (il LOW e il LOW-MID si
  accavallano, dec. 114 e 152) e Filippo l'ha già sentito nel prototipo. Il
  MID-HIGH chiuso da solo scava −26,5 dB a 1050 Hz (con incroci A: −22).

## 3. Curva della manopola: PIONEER contro pot reale

Tutte le manopole alla stessa posizione (l'EQ diventa un volume), 1 kHz:

| Posizione θ | 0,05 | 0,1 | 0,2 (ore 9) | 0,25 | 0,3 | 0,4 | 0,5 | 0,75 | 1 |
|---|---|---|---|---|---|---|---|---|---|
| prototipo PIONEER | −30,0 | −21,0 | −11,9 | −9,0 | −6,7 | −2,9 | 0 | +3,5 | +6,0 |
| HW taper PIONEER ideale | −29,0 | −20,6 | −11,8 | −9,0 | −6,6 | −2,9 | 0 | +3,5 | +6,0 |
| HW pot lineare B (a catalogo) | −19,7 | −13,8 | −7,9 | −6,0 | −4,4 | −1,9 | 0 | +3,5 | +6,0 |
| **scarto lineare − PIONEER** | **+10,3** | **+7,1** | **+4,0** | **+3,1** | **+2,2** | **+1,0** | 0 | 0 | 0 |

Il lato boost è identico (PIONEER = lineare sopra il centro). Il lato taglio
no: **con il pot che esiste a catalogo la curva hardware NON segue PIONEER
entro 1 dB fra fondo corsa e θ 0,4.** Con il taper ideale lo scarto resta
≤ 0,35 dB fino a θ 0,1 (−1 dB a θ 0,05, per il residuo del pot).

**Fattibilità con pezzi reali** (calcolo, non simulazione LTspice):

1. **Pot lineare + resistenze di legge + il buffer della banda**
   (`legge_pot_ricerca.py`): 8 × 20000 reti a caso (1 pista, 1 op-amp, 3-6
   resistenze fra due nodi qualsiasi) con silenzio a fondo corsa, centro 0 dB,
   fine corsa +6 dB e anello stabile. Il migliore scarta 7,0 dB: è il pot
   lineare nudo. Conferma docs/09 §7: ogni resistenza aggiunta rende la curva
   più dolce, mai più ripida. Il motivo: con una pista sola la legge è un
   rapporto di polinomi del 2o grado in θ; per tenere insieme centro esatto e
   +6 dB a fine corsa il taglio non può scendere sotto la retta.
2. **Pot a 4 sezioni (due piste per lato)** (`legge_pot_4sezioni.py`): prodotto
   di due partitori caricati con un buffer in mezzo. Col fine corsa a +6 dB
   (entro 0,2 dB) lo scarto massimo è 4,7 dB; senza quel vincolo 1,8 dB, ma il
   boost sale a +7,8 dB. Un RK14 a 4 sezioni con scatto al centro non risulta
   a catalogo [DA VERIFICARE]; la ricerca del 2026-11-04 ha trovato solo doppi.
3. **Taper su misura** (pot doppio con la curva PIONEER stampata sulla pista):
   segue la curva (riga «HW taper PIONEER ideale»). Escluso dalla dec. 114(c)
   e dalla dec. 146 (solo pot a catalogo).
4. **VCA per banda** (pot lineare → CV → shaper → VCA doppio): segue la curva
   esatta, ma servono 8 VCA per canale (32 sul mixer), uno shaper per banda e
   il rumore di 4 VCA sommati ×2 sul percorso. La dec. 107 aveva scartato i
   VCA per banda (tracking). Non simulato.

**Da decidere (Filippo, non Claude)**: la dec. 146 chiede la curva PIONEER
con un pot di serie, e un pot di serie non la fa. Le strade sono le quattro
sopra. Finché non si sceglie, i netlist e il documento usano il pot lineare B
(law=0) e riportano lo scarto.

## 4. Rumore (`iso-incc-noise.cir`, densità a 16 punti, `noise_total.py`)

| Manopole | Uscita EQ | v0.4 a incroci A (`iso-c-noise.cir`) |
|---|---|---|
| tutte al centro | **−97,4 dBu A-wtd** (−96,0 piatto) | −97,3 |
| tutte al massimo | −92,4 dBu A-wtd | −92,3 |
| tutte a zero | −104,8 dBu A-wtd | −104,8 |

Uguale alla v0.4 entro 0,1 dB: il rumore del canale (−94,6 dBu A-wtd, docs/06
§10) e del sistema (−82,9, §14) non cambiano. La legge del pot non conta ai
tre punti misurati (centro, estremi). Primo giro con C più piccole (R fino a
23 k): −96,2 al centro; le C più grandi del §1 lo riportano a −97,4.

## 5. Continua, ritardo, headroom

- Servo (`iso-incc-dc.cir`, 20 mV in ingresso, offset del servo 2 mV): uscita
  2,0 mV al centro e col LOW al massimo; uscita del servo −1,8 V / −3,8 V.
  Come v0.4.
- Ritardo di gruppo al centro: 3,5 ms a 30 Hz, 3,3 a 60, 3,0 a 100, 2,7 a 150,
  2,0 a 300, 1,1 a 500, 0,4 a 1 kHz, 0,2 a 3150, 0,02 a 10 kHz (v0.4: 4,2 ms a
  30 Hz, picco 4,7 a 100 Hz). Meno ritardo sui bassi: l'incrocio LR2 è un
  allpass del 1o ordine.
- Headroom: nessun nodo interno sopra il livello d'ingresso (massimo −0,04 dB
  sul ramo LOW); piedino + della somma a −20 dB (centro) e −14 dB (tutte al
  massimo), come v0.4.

## 6. Polarità

Al centro l'EQ è un allpass del 5o ordine: diritto a DC (fase −6° a 5 Hz),
−171° a 150 Hz, poi gira fino a circa −164° a 35 kHz. Con gli incroci A (tutti
LR4) tornava a −360° in alto, cioè diritto. Oggi sopra qualche centinaio di Hz
il segnale esce con la fase vicina a −180°. È identico al prototipo (stessi
segni, scarto di fase ≤ 0,5°). Dentro il mixer non crea cancellazioni: CUE,
send, filtro e fader prendono tutti l'uscita dell'EQ. Il canale MIC/MONO non
ha l'isolator: un segnale mandato insieme a un canale DJ e a un MIC si
sommerebbe con fasi diverse sopra 150 Hz (caso d'uso non previsto). Il segno
globale si può rovesciare senza op-amp in più (LOW invertito, rami alti
diritti: DC rovesciata, alti diritti); è una scelta da fare insieme a Filippo
se interessa.

## 7. Silicio e componenti per lato

| | v0.4 (incroci A) | v0.5 (incroci C) |
|---|---|---|
| sezioni OPA1654 per lato | 23 (spina 6, LOW 6, LOW-MID 5, MID-HIGH 2, buffer 4) | **20** (spina 5, LOW 5, LOW-MID 4, MID-HIGH 2, buffer 4) |
| quad OPA1654 per canale stereo | 12 (46 sezioni) | **10** (40 sezioni, nessuna libera) |
| quad sul mixer (4 canali) | 48 | **40** |
| C di precisione per lato | ~30 (stima, eq-isolator §5) | 27 (54 per canale) |
| OPA1612 (somme) e servo | 1 dual + 1 dual | invariati |

## 8. Non fatto [PROVVISORIO, vuole il banco]

Monte Carlo delle tolleranze con la topologia nuova (v0.4: R 0,1 % e C 1 %
per stare entro ±0,13 dB); THD e clip reali (macro lineari); stabilità delle
celle MFB con l'OPA1654 vero; scelta delle C in E6 e delle coppie in parallelo;
la strada per la curva PIONEER (§3).
