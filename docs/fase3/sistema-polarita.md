# Sistema — registro delle polarità (todo 227, 2026-11-03)

Stato: [PROVVISORIO]. Conto dei segni su carta, dai design doc e dai netlist
citati. Si conferma a banco con un impulso su ogni percorso (§6).

## 1. Perché esiste

Il todo 227 nasce dal datasheet THAT 2181 Rev 03 p. 7: VCA + I/V NON
inverte. Il controllo dei VCA ha trovato un problema più largo. Nessun
documento contava i segni da un capo all'altro del mixer. Ogni modulo
dichiara la sua polarità, ma i ricevitori dei net multidrop (DJ bus, bus
HPF/LPF, bus FX S1-S4, MASTER SUM, CUE sum) sono somme a massa virtuale:
ognuno inverte. Un percorso che attraversa due ricevitori torna diritto,
uno che ne attraversa uno o tre esce rovesciato.

Quando due percorsi dello stesso segnale si risommano con segni opposti,
il suono si svuota: il dry di un canale contro il suo ritorno dal pedale,
il CUE contro il master in cuffia.

## 2. Regola

1. Ogni percorso da una sorgente all'XLR master esce **non invertente**
   (polarità assoluta diritta: pin 2 dell'XLR = fase dell'ingresso).
2. Ogni anello di feedback FX (reroute cross e SELF) è **non invertente**,
   come lo modellano fx-module §8.1 e §8.5.
3. Ogni ricevitore a massa virtuale conta −1. Un percorso nuovo si
   progetta contando i ricevitori, non solo gli stadi del modulo.

## 3. Segni per blocco

| Blocco | Segno | Fonte |
|---|---|---|
| Canale: ingresso, GAIN (pot T + non invertente), isolator, send tap, CUE out | +1 | cdj §3.2-3.3 (isolator «polarità diritta»; REV 2026-11-04, incroci C: +1 a DC, poi la fase gira verso −180° sopra 150 Hz, allpass del 1o ordine come nel prototipo; tutte le prese stanno dopo l'EQ, eq-isolator §10.2) |
| Fader del canale e del ritorno: VCA + I/V | +1 | datasheet THAT 2181 p. 7; sostituisce un buffer non invertente |
| Ricevitore DJ bus (massa virtuale, nel 5-way, non disegnato in five-way §2) | −1 | backplane §4, `sim/cdj/djbus-level.cir` |
| 5-way da tensione d'ingresso a MSUM out (pad, banca, gate, celle, drive, make-up) | +1 | **misurato oggi**: `pol-5way-ac.cir`, fase −22° a 10 Hz e −11° a 100 kHz (resto = allpass della banca) |
| MASTER SUM [A2] + MONO [A3] | −1 | master-out §2, `master-segnale.py` |
| [A] [B] [C] [N] buffer, MASTER LEVEL e BOOTH LEVEL (VCA + I/V), [F] [G] hot | +1 | master-out §2-3, datasheet p. 7 |
| FX-SEND: buffer, EQ2, LEVEL, assign, iniezione | +1 | fx-send §2; EQ2 = due celle invertenti (`sim/fx/fx-eq2.cir`) |
| Ricevitore del bus FX S1-S4 | −1 | fx-module §3 |
| Driver del pedale | +1 | fx-module §4 |
| Ritorno: buffer, GAIN T2 (due invertenti), EQ2, fader VCA, out | +1 | fx-module §5 REV dec. 162 / todo 220 |
| Reroute: VCA + I/V, driver d'iniezione | +1 | fx-module §2bis.1, datasheet p. 7 |
| Ricevitore bus HPF / LPF del filtro | −1 | filter §2bis |
| Core filtro (2 sezioni SVF, HP e LP = −Vin ciascuna) | +1 | filter §3 |
| Overdrive col VCA vero e il ramo pulito da x (rimedio F1) | −1 | filter §5ter, `od2-pol-c.cir` |
| MIC e MONO, ingresso → POST, buffer d'iniezione | +1 | mic-mono §2, §3.1; schema `pcb/mic/mic.py` senza scambio dell'INA (todo 30) |
| MIC e MONO, driver MSUM (F2) | −1 | `pcb/tools/celle_micmono.py`, 20k/20k (todo 30) |
| CUE summer | −1 | sistema-cue §7 |
| Buffer MON nel modulo CUE | +1 | sistema-cue §7 |

## 4. Percorsi

Segno all'uscita di [A2] (dopo, fino all'XLR, tutto +1).

| Percorso | Ricevitori attraversati | Segno oggi | Esito |
|---|---|---|---|
| Canale → DJ bus → 5-way → MSUM1 | DJ bus, [A2] | +1 | OK |
| Canale → FX-SEND → pedale → ritorno → MSUM2-5 | S, [A2] | +1 | OK: dry e ritorno in fase |
| Canale → bus HPF/LPF → filtro → DJ bus → 5-way | HPF/LPF, DJ bus, [A2] | **−1** | **F1** |
| MIC/MONO → MSUM6/7 | [A2] | **−1** | **F2** |
| MIC/MONO → bus FX → pedale → ritorno | S, [A2] | +1 | OK, ma opposto al dry: F2 |
| Anello reroute: ritorno → VCA → bus S → pedale → ritorno | S | **−1** | **F3** |
| CUE: canale → CUE sum, contro MON (= uscita [A2]) | CUE sum | −1 contro +1 | **F4** |

## 5. Finding e rimedi [PROVVISORIO]

Rimedi scelti a costo nullo: uno stadio unity che esiste già passa da
non invertente a invertente (due resistenze uguali 0,1 %).

- **F1 — filtro sui bus (dec. 159).** Il ricevitore del bus HPF/LPF
  aggiunge un'inversione che il send/return per canale non aveva. Un
  canale con la levetta su HPF o LPF esce rovesciato rispetto agli altri e
  al suo ritorno FX (il send è pre-filtro). Rimedio [SIMULATO]: la cella di
  overdrive corretta per il segno del VCA esce già invertita,
  y = −(x + m·d) (filter §5ter, `sim/filtro/od2-pol-c.cir`); il driver
  d'uscita resta diritto.
- **F2 — MIC e MONO.** Il dry va dritto su [A2] (un ricevitore), la
  mandata FX ne passa due: con un pedale che lascia passare il diretto
  (delay con mix, riverbero) voce e ritorno si sottraggono. Rimedio:
  i due driver MSUM (L e R) invertenti; le mandate restano come sono.
  Dentro il todo 30.
- **F3 — anello del reroute.** Contato oggi è invertente; i modelli di
  fx-module §8.1/§8.5 lo davano non invertente. All'orecchio: con un
  delay l'eco cambia segno a ogni giro; quando il feedback va in
  autooscillazione la nota scende di un'ottava (periodo 2T invece di T) e
  le punte del pettine cadono a metà strada. Rimedio: driver d'iniezione
  del reroute (fx-module §2bis.1) invertente. Il ritorno verso il master
  non cambia (il reroute sta fuori dal percorso verso MSUM). Le simulazioni
  di §8 restano valide perché modellano già l'anello non invertente.
- **F4 — blend del CUE.** Il Test 3 di `sim/system/RISULTATI-cue.md`
  supponeva l'ingresso di [A2] uguale al canale; ma il canale passa dal
  ricevitore del DJ bus e arriva a [A2] rovesciato. Con la polarità di
  oggi, al centro del blend un canale già in programma si cancella in
  cuffia dove la banca 5-way non sfasa (in simulazione −104 dB) e fa
  pettine altrove (sistema-cue §7). Rimedio: buffer MON del modulo CUE invertente
  (20k/20k, il driver [N] ≤ 50 Ω regge il carico). In cuffia la polarità
  assoluta resta rovesciata: non si sente.

## 6. Cosa resta

- Fase assoluta all'XLR: +1 per i canali e i ritorni, +1 per MIC/MONO
  dopo F2. Phono (RIAA passiva + stadi, phono-stage) non ha un segno
  dichiarato: da contare col prossimo giro del canale.
- Insert del master (INS_SEND/INS_RET, dec. 111): il segno dipende dal
  processore esterno; nel mixer va tenuto +1 fra le due prese.
- Banco: un impulso positivo su ogni ingresso, oscilloscopio su XLR pin 2,
  cuffia, mandate e ritorni. Una riga per percorso della tabella §4.
- VCA (todo 227): fader, reroute, MASTER, BOOTH sono in serie e il chip
  non inverte; nessun documento li contava invertenti. Le eccezioni erano
  MONO (corretto, 7043b91), overdrive del filtro e celle c-B (todo 212),
  MIC (todo 30).
