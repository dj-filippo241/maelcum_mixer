# RISULTATI — D5: risonanza del filtro e overdrive col chip reale

Data: 2026-10-14. Todo #10. Punto di partenza: core (a), OTA nudo («a per ora»
di Filippo; la scelta B1 resta aperta). Il passo 1 ha mostrato che il core (a)
della v0.2 non funziona ai livelli di progetto. Filippo ha scelto di
proseguire col core (a) dotato di partitore, come nei filtri OTA reali. In
questo file lo chiamo (a′).

Netlist (tutti in `sim/filtro/`):

| passo | netlist | cosa misura |
|---|---|---|
| 1 | `d5-core.cir`, `d5-osc.cir` | core (a) nudo: risonanza sul programma, auto-oscillazione |
| 2 | `d5a-core.cir`, `d5a-dbg.cir` | core (a′), partitore k = 1/10, 1/20, 1/40, limitatore v0.2 |
| 2 | `d5a-osc.cir`, `d5a-lim.cir` | auto-oscillazione di (a′) e due limitatori scartati |
| 2 | `d5a-nl-k20/30/40.cir` | limitatore nuovo (perdita non lineare), oscillazione |
| 2 | `d5a-core2.cir` | griglia RES col limitatore nuovo, k = 1/20, 1/30, 1/40 |
| 2 | `d5a-noise-k{1,20,30,40}-{10.8u,397u}.cir` | rumore del core (a′) |
| 3 | `d5-chain.cir` | core (a′) + overdrive v0.2: il D5 vero e proprio |

Metodo comune: `.tran ... uic`. Il punto di lavoro del loop con gli OTA RES
a Iabc quasi zero non converge: 9 minuti senza esito. Misura su 20 ms a
regime dopo 60 ms; ampiezze picco-picco, per separare la continua.

## 0. Correzione del modello LM13700 (`sim/lib/lm13700.inc`)

Nel modello condiviso l'uscita dell'OTA era il collettore del transistor
d'ingresso Q5. Sotto ~−0,4 V d'uscita Q5 saturava, e comparivano una
continua che dipende dal segnale (fino a 0,6 V) e una seconda armonica
spuria (10-17 %). Il die reale porta Ic5 all'uscita con un mirror PNP e un
mirror NPN, e l'uscita arriva quasi alle alimentazioni. Il modello ora ha i
due mirror (Q8-Q11).

Self-test rilanciati (`ota-selftest-{ac,tran,noise}.cir`), vecchio → nuovo:

- gm: +0,06 dB. Trascurabile.
- limite di corrente e THD della tanh: invariati (H2 0,4 % → 0,27 % a 104 mV).
- rumore: +3,0 dB (×1,41) a ogni Iabc, per esempio 2,6 → 3,7 nV/√Hz a
  500 uA e 15,2 → 21,4 a 7,56 uA. I due mirror in più sono transistor
  veri: il nuovo valore è più vicino al die. L'intestazione del modello
  riporta i valori nuovi.

Chi ha usato il modello prima: 21 netlist del filtro e 4 del 5-way. Le celle
del 5-way non usano più l'LM13700 (v0.2.1). I risultati del core nudo hanno
stati d'uscita sotto 0,15 V, quindi il difetto non li tocca; il rumore sì
(+3 dB sulla parte OTA).

**Rumore del core (a) di settembre (−89,9 / −90,3 dBu A-wtd a fc max) NON
riproducibile.** Rilanciato col modello nuovo, `svf-noise-71A-397u.cir` dà
38 µV/√Hz a 20 Hz: il `.noise` cade nel ramo DC falso del loop
(`RISULTATI-ota-real.md` §7, lezione 2). Il netlist pulito di questo lavoro
(`d5a-noise-k1-397u.cir`, punto di lavoro trovato al primo colpo) dà
−104,4 dBu A-wtd per lo stesso core nudo. Il −89,9 di `docs/06` era
quindi pessimista; resta comunque superato, perché il core nudo non si usa.

## 1. Core (a) nudo: la risonanza non esiste ai livelli di progetto

Core = SVF 2 poli di `svf-real-thd.cir` istanza A (C 33 nF, Iabc 10,8 uA,
fc ~1 kHz), RES con OTA reali al posto della sorgente ideale di
`res-osc.cir`, soft limiter 1k + 3+3 1N4148 sul nodo BP (v0.2). Law dec.
102: gres = 1 − θ/0,9. Tono a 1 kHz (sul taglio), uscita LP, valori col
modello corretto. «Ideale» = Q × ingresso.

| RES θ (Q) | −30 dBu: misurato / ideale (mVp) | −10 dBu | 0 dBu |
|---|---|---|---|
| 0 % (0,71) | 25 / 24 | 52 / 245 | 116 / 775 |
| 50 % (1,6) | 41 / 55 | 66 / 554 | 199 / 1750 |
| 70 % (3,2) | 43 / 110 | 101 / 1100 | 251 / 3500 |
| 80 % (6,4) | 44 / 220 | 137 / 2200 | 315 / 7000 |
| 85 % (12,7) | 44 / 440 | 171 / 4400 | 338 / 13900 |

- Lo stato BP non supera ~55 mV sul taglio: è il tetto dei 52 mV
  (`RISULTATI-ota-real.md` §6). Il picco di risonanza resta sotto il tetto
  a qualunque livello d'ingresso.
- Programma a 0 dBu, RES al minimo: il tono sul taglio perde 23 dB
  invece dei 3 di un filtro ideale. Sotto il taglio (250 Hz) un programma
  di 0 dBu esce a −4 dBu rms e distorto.
- Auto-oscillazione (`d5-osc.cir`, senza ingresso): con fc 1 kHz suona a
  81-112 Hz, con fc 10 kHz a 609-782 Hz. È circa 3,5 ottave sotto il taglio.
  Ampiezza −10…0 dBu rms, e varia col taglio.

La riga «compressione morbida ~1 % a 0 dBu» di `RISULTATI-ota-real.md` §3 è
vera per il THD, ma la stessa tabella dice «gain −3,5×»: il core distorce
poco perché schiaccia il livello.

## 2. Core (a′): OTA con partitore

### Circuito

```
summer ─hp─► Ra ─┬─► OTA1 (+) ─► C = 33 nF·k ─► buffer ─bp_b─► Ra ─┬─► OTA2 (+) ─► C = 33 nF·k ─► buffer ─► LP
                 Rd 100 Ω                                           Rd 100 Ω
                                                                   └─► OTA RES ± (Iabc = 7,365 uA·|gres|/k) ─► summer
bp_b ─► 4,7k ─► 2+2 1N4148 antiparallele ─► summer   (limitatore nuovo)
```

- Partitore k = Rd/(Ra + Rd), Rd 100 Ω (Ra 1,9k / 2,9k / 3,9k per 1/20,
  1/30, 1/40). Il tetto di stato sul taglio sale a 52 mV/k: 1,04 / 1,56 /
  2,08 V.
- C = 33 nF · k (1,65 / 1,1 / 0,825 nF): la mappa Iabc → fc resta quella
  della v0.2, quindi converter, mirror e shaper (dec. 102) sono invariati.
  Verificato: risposta a piccolo segnale 1,00 / 0,70 / 0,24 / 0,063 a
  0,25 / 1 / 2 / 4 kHz (`d5a-dbg.cir`), quella di un 2 poli Q 0,707.
- **Offset in continua ×1/k**: l'offset dell'OTA si legge sugli stati
  moltiplicato per 1/k. Misurato 2,6-5,3 mV all'uscita LP con Vos tipico
  (0,4 mV); con Vos massimo (4 mV) ~26-53 mV (×10, stima). Il servo DC
  dell'overdrive (§5ter) corregge fino a 83 mV in ingresso a m = 1:
  basta, ma col margine ridotto da ≥ 16× a ~1,6×. Da vedere a banco.

### Limitatore dell'oscillazione: tre posizioni provate

1. **v0.2, 1k + 3+3 diodi sul nodo BP** (`d5a-osc.cir`): il nodo BP è
   l'uscita dell'OTA e la corrente nei diodi la dà l'OTA, che ne ha
   quanto la sua Iabc. L'ampiezza dipende dal taglio: circa +3,5 dB per
   decade. Scartato.
2. **nessun limitatore, o 2+2 diodi su Rf del summer** (`d5a-lim.cir`):
   l'oscillazione arriva alle alimentazioni (±13,5 V). Scartati.
3. **perdita non lineare dal buffer BP al summer** (`d5a-nl-k*.cir`):
   4,7k + 2+2 1N4148. Sotto ~1,1 V non conduce; sopra smorza l'anello con
   corrente presa da un nodo a bassa impedenza. **Adottato.**

Auto-oscillazione col limitatore 3, senza ingresso (fc impostato ≈ 101 /
1010 / 10100 Hz):

| k | RES poco oltre 90 % (gres −0,1): nota · livello | RES 100 % (gres −0,75): nota · livello |
|---|---|---|
| 1/20 | −2,7 semitoni · −2,0 dBu | −8,2 semitoni · +3,8 dBu |
| 1/30 | −1,3 · −1,8 | −5,7 · +4,9 |
| 1/40 | −0,8 · −1,7 | −4,2 · +5,6 |

Valori a fc 1 kHz (riferimento 1010 Hz misurato in `RISULTATI-ota-real.md`
§3); livello LP in dBu rms.

- Livello e nota sono **gli stessi su tre decadi** di taglio (scarto
  ≤ 0,6 dB e ≤ 0,3 semitoni): la nota segue la manopola FREQ.
- La nota cala quando la RES sale dentro la zona di oscillazione: a fine
  corsa suona 4-8 semitoni sotto il taglio. Gli OTA vicino al tetto
  rallentano il giro. Più piccolo è k, meno cala.
- Livello a fine corsa +3,8…+5,6 dBu: sotto il requisito +6…+10 dBu
  (SPECIFICA §5) di 0,4-2,2 dB. Con 1k al posto di 4,7k il livello scende
  di ~2,5 dB e la nota cala di 0,1-1,2 semitoni in meno.

### Risonanza sul programma (`d5a-core2.cir`, limitatore 3)

Tono a 1 kHz sul taglio, uscita LP. Rapporto tra uscita e ingresso
(componente fondamentale):

| RES θ | ideale | k 1/20: −30 / −10 / 0 dBu | k 1/30 | k 1/40 |
|---|---|---|---|---|
| 0 % | −3,0 dB | −3,0 / −3,0 / −3,8 | −3,0 / −3,0 / −3,5 | −3,1 / −3,1 / −3,4 |
| 50 % | +4,0 | +4,0 / +3,7 / −2,1 | +4,0 / +3,8 / −0,5 | +3,9 / +3,8 / 0,0 |
| 70 % | +10,1 | +10,0 / +6,0 / −1,9 | +9,9 / +7,2 / +0,3 | +9,9 / +7,5 / +1,1 |
| 85 % | +22,1 | +20,7 / +6,7 / −1,8 | +21,3 / +8,5 / +0,7 | +21,1 / +9,2 / +1,8 |

- Con un programma a −30 dBu la risonanza è quella ideale (+21 dB).
- Con un programma a −10 dBu la risonanza c'è e si sente fino a ~70 %;
  oltre si ferma contro il tetto (+6,7…+9,2 dB invece di +22).
- Con un programma a 0 dBu il picco non supera il programma di più di
  ~2 dB: il core comprime il fischio. THD del core 1,5-2 % (terza e
  seconda armonica): è il carattere OTA.
- Sotto il taglio il core (a′) passa il programma intero a 0 dBu.

### Rumore del core (a′) (`d5a-noise-*`, metodo `docs/06`)

| core | fc 1 kHz | fc massimo (37 kHz) |
|---|---|---|
| (a) nudo, riferimento | −113,8 | −104,4 |
| (a′) k 1/20 | −91,4 | −90,3 |
| (a′) k 1/30 | −87,9 | −87,4 |
| (a′) k 1/40 | −85,5 | −85,3 |

dBu A-wtd, uscita LP, RES al minimo. Il rumore sale come 1/k: la fonte
principale è l'OTA RES, che col partitore lavora a 7,365 uA/k (147-295 uA)
e inietta la sua corrente di rumore nel summer.

Sistema con 4 filtri inseriti, overdrive chiuso (base −82,9 a filtri OFF,
`docs/06` §10; overdrive chiuso −102,6): k 1/20 → **−80,4** (PASS 2,4 sul
−78); k 1/30 → **−79,0** (PASS 1,0); k 1/40 → **−77,7** (FAIL 0,3).

## 3. D5: core (a′) + overdrive v0.2 (`d5-chain.cir`)

Overdrive = blocco di `od2-chain.cir` sull'uscita LP. Tono a 1 kHz sul
taglio. THD % · livello d'uscita in dBu rms, manopola DRIVE
0 / 25 / 50 / 65 / 80 / 90 / 100 %.

**k 1/30**, il valore intermedio:

| RES · ingresso | 0 % | 25 % | 50 % | 65 % | 80 % | 90 % | 100 % |
|---|---|---|---|---|---|---|---|
| 0 % · −10 dBu | 0,1 · −13,1 | 0,0 · −12,7 | 0,0 · −11,2 | 0,0 · −9,8 | 0,0 · −8,1 | 0,0 · −6,9 | 0,0 · −5,7 |
| 70 % · −10 dBu | 0,8 · −2,8 | 0,5 · −2,6 | 3,1 · −1,8 | 5,7 · −0,9 | 8,8 · +0,3 | 10,8 · +1,1 | 12,8 · +2,1 |
| 85 % · −10 dBu | 1,3 · −1,5 | 0,9 · −1,4 | 3,4 · −0,7 | 6,6 · +0,1 | 10,3 · +1,0 | 13,0 · +1,7 | 15,7 · +2,5 |
| 0 % · 0 dBu | 0,6 · −3,5 | 0,2 · −3,2 | 2,8 · −2,3 | 5,2 · −1,3 | 7,9 · −0,1 | 9,7 · +0,8 | 11,3 · +1,8 |
| 85 % · 0 dBu | 1,8 · +0,7 | 1,2 · +0,7 | 3,5 · +1,1 | 7,3 · +1,5 | 12,2 · +2,1 | 16,0 · +2,6 | 20,0 · +3,1 |
| 100 % (osc.) · −10 dBu | 43 · +4,8 | 43 · +4,8 | 41 · +4,6 | 39 · +4,5 | 37 · +4,3 | 37 · +4,1 | 37 · +4,0 |

Gli altri due partitori stanno nello stesso disegno, spostati di 1-2 dB
(k 1/20 più basso e più pulito sul fischio, k 1/40 più alto). Tabelle
complete nel log, leggibili con `python3 sim/fourier_tab.py`.

### Lettura

1. **Il fischio arriva all'overdrive a −1,5…+3 dBu, non a +8.** La griglia
   di `od2-chain.cir` (confermata il 13/10, dec. 99 i) supponeva un picco
   di risonanza a +8 dBu. Col core (a′) l'overdrive lavora sul fischio
   come su un programma nominale: a fine corsa 11-22 % invece di 31 %.
2. **L'overdrive non frena più il fischio: lo alza.** Nella griglia
   dec. 99 il picco a +8 usciva a +4,6 a fine corsa. Qui entra più basso
   e il tosatore lo porta su: +1,9…+3,4 dBu a fine corsa. Il tetto di
   +5,5 dBu regge: uscita massima misurata +5,4 dBu.
3. **Il primo sporco sul fischio lo fa il core**, non l'overdrive: 1,3-2 %
   a manopola chiusa. Il «raschio che cresce con la risonanza» della
   referenza Sherman (dec. 82) nasce già nel core (a′); l'overdrive lo
   allarga.
4. **Programma e fischio si sporcano quasi insieme.** Con RES all'85 % e
   programma a 0 dBu: 3,5 % a metà manopola, 20 % a fine corsa. La
   risonanza non ha più un «vantaggio» di livello di 8 dB sul programma.
5. **A 25 % il THD scende** sotto quello del core da solo (1,8 → 1,2 %):
   la prima dose di tosatore compensa in parte la compressione del core.
   Curiosità, non un difetto.
6. **Auto-oscillazione e overdrive**: l'overdrive aperto pulisce un po'
   l'oscillazione mescolata al programma (43 → 37 %) e la abbassa di
   0,8 dB. Nessuna instabilità.

## 4. Numeri musicali da confermare (regola 2)

**ESITO 2026-10-14: DECISIONE 110.** Filippo accetta i quattro punti come
punto di partenza (k 1/30 già deciso nella 109).

- **Partitore k**: rumore contro forza della risonanza e accordatura
  dell'oscillazione (tabelle §2). Proposta di Claude: **1/30**. Rumore
  di sistema PASS 1,0 dB; oscillazione −1,3…−5,7 semitoni,
  −1,8…+4,9 dBu.
- **Livello dell'auto-oscillazione** sotto il requisito +6…+10 dBu
  (SPECIFICA §5) di 1-2 dB a fine corsa.
- **Nota dell'oscillazione** che cala di 4-8 semitoni tra 90 % e 100 % di
  RES.
- **Forza della risonanza**: il picco si ferma a +7…+9 dB su un programma
  a −10 dBu e a ~+1 dB su 0 dBu. Le law RES della dec. 102 erano scritte sui
  picchi ideali (+4 / +10 / +16 / +22 dB).
- **Griglia dell'overdrive** (dec. 99 i): confermata su un picco di +8 dBu
  che col core (a′) non c'è. Va riletta con la tabella §3.

## 5. Non fatto

- ~~Rumore con l'overdrive aperto~~ e ~~core a 4 poli~~: FATTI il
  2026-10-21, §6.
- Programma vero (più toni, transitori): solo toni a 1 kHz e 250 Hz.
- Deriva termica del partitore e degli OTA; offset in continua con Vos
  massimo dentro la catena col servo.

## 6. Core a 4 poli e rumore con l'overdrive aperto (2026-10-21, todo 46)

Core (a′) k 1/30 in due sezioni, allineamento Butterworth: sezione 1 a Q
0,541 fissa (OTA di smorzamento a Iabc fissa, niente limitatore), sezione 2
a Q 1,307 con la RES (law dec. 102) e il limitatore del §2. È la struttura
del prototipo `MC-FILTRO` (sez_a0 + sez_a1). Overdrive v0.2 sull'uscita LP
come nel §3.

| netlist | cosa misura |
|---|---|
| `d5b-4p-chain.cir` | risonanza sul programma e overdrive (tono a 1 kHz sul taglio) |
| `d5b-4p-osc-g{0.1,0.75}-{1.08u,10.8u,108u}.cir` | auto-oscillazione senza ingresso, un caso per netlist |
| `d5b-4p-noise-{397u,10.8u}.cir` | rumore core + overdrive v0.2b (od2-noise-b), DRIVE 0 / 50 / 80 / 100 % |
| `d5b-4p-noise-r1-*`, `-r2-*`, `-k20-*` | varianti per il rumore (sotto) |

`d5b-4p-osc.cir` (sei casi in un netlist, 1 s ciascuno) non termina: dopo
40 minuti era al quinto caso. Spezzato nei sei netlist sopra, ognuno
finisce in 1-8 minuti.

### 6.1 Risonanza e overdrive (`d5b-4p-chain.cir`)

THD % · uscita dBu rms, manopola DRIVE 0 / 50 / 80 / 100 %:

| RES · ingresso | 0 % | 50 % | 80 % | 100 % |
|---|---|---|---|---|
| 85 % · −30 dBu | 0,1 · −9,2 | 0,2 · −7,4 | 0,5 · −4,4 | 0,8 · −2,0 |
| 85 % · −10 dBu | 0,9 · −2,5 | 3,2 · −1,5 | 9,2 · +0,5 | 13,6 · +2,2 |
| 70 % · −10 dBu | 0,6 · −3,5 | 2,8 · −2,3 | 7,8 · −0,1 | 11,2 · +1,8 |
| 0 % · −10 dBu | 0,1 · −13,1 | 0,0 · −11,3 | 0,0 · −8,2 | 0,0 · −5,8 |
| 85 % · 0 dBu | 1,6 · −0,4 | 3,5 · +0,2 | 11,4 · +1,6 | 17,9 · +2,9 |
| 0 % · 0 dBu | 0,5 · −3,7 | 2,7 · −2,5 | 7,5 · −0,2 | 10,7 · +1,7 |

Guadagno sul taglio (fondamentale), contro l'ideale −3,0 / +4,0 / +10,1 /
+22,1 dB a RES 0 / 50 / 70 / 85 %:

| ingresso | 0 % | 50 % | 70 % | 85 % |
|---|---|---|---|---|
| −30 dBu | −3,1 | +3,9 | +9,7 | +20,8 |
| −10 dBu | −3,1 | +3,6 | +6,5 | +7,5 |
| 0 dBu | −3,7 | −1,4 | −0,8 | −0,4 |

- Stesso disegno del 2 poli (§2, §3): risonanza piena a −30 dBu, tetto a
  −10 dBu, compressione a 0 dBu. Il fischio sul programma è ~1 dB più
  debole (85 % a −10 dBu: +7,5 contro +8,5 dB).
- La sezione 1 resta pulita: 0,26 % di THD con 0 dBu sul taglio (tetto di
  stato 1,56 V, segnale 0,59 V di picco). Lo sporco nasce nella sezione 2.
- Uscita massima +2,9 dBu, sotto il tetto di +5,5 dBu.

### 6.2 Auto-oscillazione

| RES | fc 101 Hz | fc 1010 Hz | fc 10,1 kHz |
|---|---|---|---|
| poco oltre 90 % (gres −0,1) | −1,2 st · −2,2 dBu | −1,3 st · −1,8 dBu | −1,4 st · −1,7 dBu |
| 100 % (gres −0,75) | −5,5 st · +4,7 dBu | −5,7 st · +4,9 dBu | −5,7 st · +4,9 dBu |

Nota sotto il taglio in semitoni (st) · livello LP in dBu rms. Identici al
2 poli k 1/30 (§2): oscilla la sezione 2, la sezione 1 senza ingresso non
cambia niente. I numeri della dec. 110 valgono anche per il 4 poli.

### 6.3 Rumore (metodo `docs/06`, uscita dopo l'overdrive)

dBu A-wtd, RES al minimo:

| core | DRIVE 0 % | 50 % | 80 % | 100 % |
|---|---|---|---|---|
| 4 poli k 1/30, fc max (397 uA) | −84,4 | −82,6 | −79,5 | −77,0 |
| 4 poli k 1/30, fc 1 kHz (10,8 uA) | −84,3 | −82,5 | −79,4 | −76,9 |
| 2 poli k 1/30 (§2, riferimento) | −87,4 / −87,9 | — | — | — |

- Il 4 poli fa 3,1-3,6 dB più rumore del 2 poli: due sezioni, due OTA di
  smorzamento, quattro integratori col partitore.
- Guadagno a piccolo segnale dell'overdrive: 0 / +1,8 / +4,9 / +7,4 dB,
  come nel §5ter. Il rumore cresce di pari passo: lo domina il core, non
  il blocco dell'overdrive.

**Sistema** (metodo `docs/06` §11: −82,9 a filtri OFF ⊕ 4 canali filtro):

| condizione | 2 poli (docs/06 §11) | 4 poli |
|---|---|---|
| 4 filtri inseriti, overdrive chiuso | −79,0 | **−77,0 (FAIL 1,0 sul −78)** |
| 4 filtri, DRIVE a metà | −77,8 | −75,6 |
| 4 filtri, DRIVE a fondo, in silenzio | −73,4 | −70,6 |
| 1 filtro inserito, overdrive chiuso | −81,6 | −80,5 |

Le righe con l'overdrive aperto stanno nella condizione d'uso accettata
dalla dec. 100. La prima riga no: col 4 poli, quattro filtri inseriti a
manopole ferme superano il target della dec. 89 di 1,0 dB.

### 6.4 Varianti provate per il rumore

| variante | fc max | fc 1 kHz | sistema, 4 filtri (caso peggiore) |
|---|---|---|---|
| base k 1/30 | −84,4 | −84,3 | −77,0 |
| R1: Q fissa della sezione 1 con resistenza (R = 1/(19,2·Iq1·k) = 5,4k) al posto dell'OTA | −86,0 | −84,3 | −77,0 |
| R2: R1 + base Q 1,307 della sezione 2 con resistenza; la RES toglie smorzamento con l'OTA negativo, spento a RES minima | −86,8 | −84,3 | −77,0 |
| k 1/20 (partitore della dec. 109 cambiato) | −87,2 | −87,7 | **−78,9 (PASS 0,9)** |

- Con il taglio a 1 kHz domina il rumore degli integratori (OTA a 10,8 uA
  visti attraverso il partitore ×1/k): R1 e R2 non lo toccano. Aiutano solo
  col taglio in alto.
- Solo un partitore più grande rientra nel target. Il prezzo è musicale
  (§2, k 1/20): oscillazione a fine corsa −8,2 semitoni e +3,8 dBu
  (contro −5,7 e +4,9), fischio sul programma più debole (85 % a −10 dBu:
  +6,7 contro +8,5 dB nel 2 poli). Scelta di Filippo (docs/02, A18).

### 6.5 Rumore in modo HPF (2026-10-21, pomeriggio)

dBu A-wtd, uscita HP del core a 4 poli (sezione 2 da hp1), overdrive a
valle; DRIVE chiuso / aperto:

| fc | (a′) k 1/30 (`d5b-4p-noise-hp.cir`) | (c-B) f1 12 kHz (`cb-4p-noise-hp.cir`) |
|---|---|---|
| 37 kHz | −93,6 / −86,6 | −96,5 / −93,9 |
| 1 kHz | **−81,6** / −74,2 | −90,2 / −82,8 |
| 100 Hz | −85,6 / −78,3 | **−88,4** / −81,0 |
| 10 Hz | −87,2 / (*) | −88,6 / −81,2 |

(*) (a′) a Iabc 114 nA con DRIVE aperto: guadagno 0,39 invece di 2,34.
Nel punto di lavoro l'offset del core (×1/k) polarizza il tosatore; il
netlist non ha il servo dell'overdrive (§5ter). Riga scartata.

Sistema con 4 filtri in HPF, overdrive chiuso: **(a′) −74,8 (FAIL 3,2)**,
**(c-B) −79,6 (PASS 1,6)**. In HPF il filtro aperto lascia passare il
rumore degli integratori su tutta la banda: è il caso peggiore per
entrambi i core.

### 6.6 Non fatto

- Programma vero (più toni, transitori): solo toni a 1 kHz.
- Core (c-B) a 4 poli: rumore non misurato. Serve per confrontare B1 alla
  pari.

## 7. Somma dei canali sui bus HPF e LPF (2026-11-03, todo 215, dec. 159)

Dalla dec. 159 il core non riceve più un canale: riceve il bus della
sezione, cioè la somma dei canali assegnati dopo il fader. Il ricevitore
del bus ha guadagno 1 per canale (Rf 10k, R 10k lato sorgente). Un canale a
0 dBu dà 0 dBu al core, come prima; due canali correlati +6 dBu; quattro
canali correlati +12 dBu (il caso del DJ bus nel gain-staging sheet). Due
dischi diversi a 0 dBu sommano a ~+3 dBu efficaci, con picchi a +6 dove i
kick coincidono.

| netlist | cosa misura |
|---|---|
| `d5c-sum-chain.cir` | tono a 1 kHz sul taglio (fc ~1 kHz), uscita LP, ingresso 0 / +6 / +12 dBu |
| `d5c-sum-pass.cir` | tono a 200 Hz in banda passante, LPF a fc ~1 kHz |
| `d5c-sum-pass-hp.cir` | tono a 5 kHz in banda passante, HPF a fc ~1 kHz |
| `bus-rx-noise.cir` | rumore del ricevitore del bus con 1 / 2 / 4 / 7 sorgenti |

Core (a′) k 1/30 a 4 poli e overdrive come §6.1 (DRIVE a pot doppio:
stessa funzione di trasferimento, filter-module §5ter). Le righe a 0 dBu
rifanno quelle del §6.1 (−0,4 dBu 1,6 %, −3,7 dBu 0,5 %): netlist coerenti.

### 7.1 Sul taglio (D5 con la somma)

Uscita dBu rms · THD %, DRIVE 0 %:

| ingresso | RES 0 % | RES 50 % | RES 85 % |
|---|---|---|---|
| 0 dBu (1 canale) | −3,7 · 0,5 | −1,4 · 1,3 | −0,4 · 1,6 |
| +6 dBu (2 correlati) | −0,7 · 1,4 | +0,3 · 1,7 | +0,8 · 1,8 |
| +12 dBu (4 correlati) | 0,0 · 1,6 | +0,8 · 1,7 | +1,2 · 1,7 |

Guadagno sul taglio, contro l'ideale −3,0 / +4,0 / +22,1 dB:

| ingresso | RES 0 % | RES 50 % | RES 85 % |
|---|---|---|---|
| 0 dBu | −3,7 | −1,4 | −0,4 |
| +6 dBu | −6,7 | −5,7 | −5,2 |
| +12 dBu | −12,0 | −11,2 | −10,9 |

- Sul taglio il core ha un tetto: l'uscita resta fra −1 e +1 dBu
  (fino a +1,2) qualunque sia la somma. La sezione 2 tocca il tetto di
  stato (bp_b 2,3-3,1 V picco-picco a +6/+12 dBu).
- Con un canale nulla cambia (dec. 110). Con due canali correlati la
  risonanza sul programma sparisce del tutto, e a RES 0 la zona del taglio
  scende di 3,7 dB in più dell'ideale. Con quattro, di 9 dB.
- THD sul taglio 1,4-1,8 %, quasi tutta terza armonica, come con un canale.

DRIVE aperto, sul taglio: con la somma (+6/+12 dBu) uscita +2,6…+3,1 dBu
e THD 17-21 %; con un canale +1,7…+2,7 dBu e 11-18 %. Tetto
dell'overdrive (+5,5 dBu) rispettato.

### 7.2 In banda passante

Uscita dBu rms · THD %, RES 0 % (RES 85 %: livello entro 0,2 dB, THD fra parentesi):

| ingresso | LPF, 200 Hz, DRIVE 0 | LPF, DRIVE 50 | LPF, DRIVE 100 | HPF, 5 kHz, DRIVE 0 | HPF, DRIVE 100 |
|---|---|---|---|---|---|
| 0 dBu | −0,1 · 0,04 (0,05) | +0,5 · 4,5 | +2,8 · 19 | +0,1 · 0,5 (0,4) | +2,8 · 20 |
| +6 dBu | +5,9 · 0,18 (0,30) | +5,6 · 4,3 | +3,9 · 29 | +6,1 · 1,2 (0,9) | +3,9 · 29 |
| +12 dBu | +11,9 · 2,2 (3,7) | +11,0 · 2,5 | +4,6 · 34 | +12,1 · 1,6 (1,1) | +4,6 · 34 |

- In banda il filtro passa la somma senza perdite: il livello resta
  quello d'ingresso fino a +12 dBu.
- LPF: pulito fino a due canali correlati (≤ 0,3 %); con quattro
  correlati 2-4 %, terza armonica.
- HPF: la sezione 1 (da hp1) sporca già a 0 dBu (0,4-0,5 %, come prima);
  1-1,6 % con la somma.
- DRIVE: il tosatore ha soglie fisse, quindi la somma satura di più. A
  fondo corsa l'uscita sale da +2,8 a +4,6 dBu e la THD da 19 a 34 %:
  i dischi si sporcano a vicenda, come accettato dalla dec. 159(d).
- Dopo la sezione il DJ bus riceve al massimo +12 dBu (DRIVE chiuso,
  quattro canali correlati): lo stesso massimo del DJ bus a filtri OFF.

### 7.3 Rumore del ricevitore e di sistema

Ricevitore del bus (`bus-rx-noise.cir`, OPA1612, Rf 10k), uscita dBu
A-wtd: 1 sorgente −111,5, 2 −109,7, 4 −107,4, 7 −105,3. Sta 25 dB sotto il
core: trascurabile. Anche le 2 uscite del filtro sul DJ bus (7 sorgenti
invece di 5) non cambiano il sistema.

Sistema = −82,9 (filtri OFF, docs/06 §14) ⊕ core attivi ⊕ ricevitori.
Una sezione senza canali è muta (dec. 159c): il suo core non conta. Core
dal §6.3 e §6.5 (uscita dopo l'overdrive v0.2b; il DRIVE a pot fa
−108…−102 dBu, il core domina).

| condizione | prima (4 core, §6.3/§6.5) | ora (dec. 159) |
|---|---|---|
| solo LPF in uso, DRIVE chiuso | −77,0 | **−80,6** (PASS 2,6) |
| solo HPF in uso (fc 1 kHz, caso peggiore), DRIVE chiuso | −74,8 | **−79,2** (PASS 1,2) |
| HPF e LPF in uso, DRIVE chiuso | — | **−78,0** (PASS 0,0) |
| HPF e LPF, DRIVE a metà | −75,6 | −76,8 (HPF a metà stimato −79,8: core + 1,8 dB) |
| HPF e LPF, DRIVE a fondo, in silenzio | −70,6 | −72,0 |

- Il FAIL del §6.3 (A18) sparisce: a DRIVE chiuso il sistema resta entro
  il −78 della dec. 89 in ogni caso, al limite con le due sezioni in uso e
  l'HPF a 1 kHz.
- Le righe col DRIVE aperto restano nella condizione d'uso della dec. 100.
- Il numero di canali assegnati non cambia il rumore: il core è uno per
  sezione.

### 7.4 Non fatto

- Programma vero (due dischi, kick sovrapposti): solo toni.
- Il prototipo MC-FILTRO filtra ancora per canale (todo 216): il tetto sul
  taglio con la somma va sentito lì.
