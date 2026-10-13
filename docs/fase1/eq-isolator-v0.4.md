# EQ DI CANALE v0.4 — isolator a 4 bande (2026-10-13)

> **Stato: v0.4-beta2, SIMULATO e INTEGRATO NEL CANALE (alpha + completamento §8 + integrazione §9, 2026-10-13).** Decisione 105 [F]: «rifai il 4 band EQ
> in modo che sia un isolator». Sostituisce l'EQ in serie v0.3 beta-3
> (`eq-serie-v0.3.md`), che resta ARCHIVIATO come alternativa. Topologia
> scelta e simulata; valori [PROVVISORI — regola 3]. Tre numeri musicali
> aspettano la conferma di Filippo (§6).

## 1. Requisito (decisione 105)

- Ogni manopola porta la SUA banda dal silenzio (fondo corsa) a 0 dB
  (centro, detent) a +6 dB (fine corsa).
- Tutte e quattro a fondo corsa = canale muto, senza contare sul fader.
- Centro piatto: tutte le manopole al detent = segnale invariato.
- Restano 4 manopole per canale: nessun comando nuovo.

## 2. Perché bande in parallelo

Nell'EQ in serie il segnale attraversa le quattro celle una dopo
l'altra: una cella non «contiene» la sua banda, la scolpisce su tutto il
segnale, e il silenzio non esiste. Nell'isolator il segnale viene diviso
in quattro strade, una per banda. Ogni manopola è il rubinetto della sua
strada. Chiuso il rubinetto, quella banda non arriva alla somma.

## 3. Topologia

Banca a crossover Linkwitz-Riley 24 dB/ottava allineata in fase: la
stessa matematica della kill bank del 5-way (five-way §3.1, somma piatta
esatta), ridotta a 3 incroci f1 / f2 / f3.

```
ingresso ─┬─ LP4(f1) ─ A2(f2) ─ A2(f3) ──────────── pot LOW ──┐
          └─ HP4(f1) ─┬─ LP4(f2) ─ A2(f3) ─ invert. ─ pot LM ──┤
                      └─ HP4(f2) ─┬─ LP4(f3) ──────── pot MH ──┼─ somma ×2 ─ uscita
                                  └─ HP4(f3) ──────── pot HIGH ┘
```

- LP4 / HP4 = due sezioni Sallen-Key Butterworth in cascata (Q 0,707;
  HP con R_fb = R_gnd/2).
- A2 = allpass del 2° ordine (MFB bandpass + sommatore, 2 op-amp): porta
  ogni banda alla stessa fase di riferimento. Senza gli allpass la somma
  ha buchi di 3-5 dB (lezione 5-way v0.1).
- La banda LOW-MID attraversa un solo allpass ed esce invertita: un
  invertitore unity la raddrizza.
- **Manopola di banda**: pot LINEARE 10 kΩ usato come partitore + buffer;
  la somma finale guadagna 2. A metà corsa il partitore dà 0,5: 0,5 × 2
  = 0 dB esatti. A fine corsa 1 × 2 = +6 dB. A fondo corsa il cursore è
  a massa: silenzio.
- La somma è invertente: l'uscita dell'EQ è INVERTITA. Da chiudere nella
  polarità del canale (`cdj-line-channel.md` §3.3).
  **[SUPERATO 2026-10-13 → §9: la somma è diventata NON invertente,
  l'uscita dell'EQ è a polarità diritta. Lo schema qui sopra resta
  valido fino ai pot; cambia solo lo stadio di somma.]**

Law della manopola (pot lineare, per costruzione): fondo corsa silenzio ·
5 % −20 dB · 12 % −12 dB · 25 % −6 dB · 50 % 0 dB · 75 % +3,5 dB · 100 %
+6 dB. Lenta attorno al centro, rapida verso il fondo.

## 4. Misure (`sim/eq-iso/iso-ac.cir`, op-amp reali OP1654 / OP1612)

Incroci di partenza 150 / 500 / 2500 Hz. Guadagno in dB:

| Manopole | 20 | 50 | 80 | 150 | 274 | 500 | 1,1k | 2,5k | 5k | 8k | 20k | 35k |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tutte al centro | 0,00 | 0,00 | 0,00 | −0,01 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 |
| LOW a zero | −52,7 | −37,0 | −22,3 | −6,0 | −0,8 | −0,1 | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 |
| LOW-MID a zero | 0,0 | −0,1 | −0,7 | −5,9 | **−15,9** | −5,9 | −0,3 | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 |
| MID-HIGH a zero | 0,0 | 0,0 | 0,0 | 0,0 | −0,7 | −5,9 | **−22,2** | −6,0 | −0,5 | −0,1 | 0,0 | 0,0 |
| HIGH a zero | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 | −0,3 | −6,0 | −24,3 | −38,8 | −53,0 | −53,9 |
| LOW + LOW-MID a zero | −54,0 | −54,0 | −53,8 | −44,4 | −22,2 | −6,1 | −0,3 | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 |
| MID-HIGH + HIGH a zero | 0,0 | 0,0 | 0,0 | 0,0 | −0,7 | −5,9 | −27,8 | −48,9 | −53,6 | −53,9 | −54,0 | −54,0 |
| tutte a zero | −54,0 piatto (limite: residuo del pot, vedi §5) |
| una banda al massimo | +6,0 nella banda, +3,5 all'incrocio, 0 fuori |
| tutte al massimo | +6,01 piatto |
| tutte a 1/4 di corsa | −6,0 piatto |

Esiti:

- **Centro piatto entro 0,01 dB** da 20 Hz a 35 kHz. Con tutte le
  manopole alla stessa posizione l'EQ è sempre piatto: è un volume.
- **LOW e HIGH spariscono davvero**: il basso a 50 Hz scende di 37 dB,
  gli alti a 8 kHz di 39 dB. La voce 68 (HIGH che «scurisce», −9 dB)
  cade.
- **FINDING — le due bande medie da sole non arrivano al silenzio.**
  Chiusa la sola LOW-MID, al suo centro restano −16 dB; chiusa la sola
  MID-HIGH, −22 dB. Non è un difetto del circuito: una banda stretta sta
  tra due vicine, e le code dei vicini (24 dB/ottava) la riempiono. Il
  silenzio arriva quando si chiudono anche i vicini (righe «due bande a
  zero»). All'orecchio: chiudendo solo i medio-bassi il corpo della
  musica si svuota molto ma non scompare.
- La profondità delle medie dipende dalla LARGHEZZA delle bande, cioè
  dagli incroci. Variante B, incroci 100 / 630 / 4000 Hz
  (`iso-ac-b.cir`): LOW-MID −25,9 dB e MID-HIGH −26,1 dB al centro; in
  cambio LOW e HIGH diventano più strette (LOW a zero: −24 dB a 50 Hz,
  −11 a 80 Hz; HIGH a zero: −11 dB a 5 kHz, −24 a 8 kHz).

Rumore (`iso-noise.cir`, densità a 16 punti):

| Manopole | Uscita |
|---|---|
| tutte al centro | **−97,1 dBu A-wtd** (−95,7 piatto) |
| tutte al massimo | −92,3 dBu A-wtd |
| tutte a zero | −103,9 dBu A-wtd |

L'EQ in serie faceva −89,2 dBu ed era l'82 % del rumore del canale: con
l'isolator il canale migliora (totale di canale e di sistema da
ricalcolare, todo 38).

## 5. Costi e limiti (da sapere prima di confermare)

- **Silenzio a fondo corsa = quanto è buono il pot.** Un pot rotativo a
  fondo corsa non va a zero ohm: restano alcuni ohm. Con 10 Ω su 10 kΩ
  (modello) il residuo è −54 dB: quasi inudibile, non silenzio assoluto.
  Due rimedi d'ingegneria, nessun comando nuovo: (a) pot con residuo
  basso garantito (voce 40); (b) il contatto di fine corsa già previsto
  dalla dec. 104, qui usato banda per banda per mettere a massa
  l'ingresso del buffer: silenzio vero. Raccomandazione: (b).
- **Silicio**: 24 sezioni op-amp per lato = 12 quad + 1 dual per canale
  DJ stereo, 48 quad per i 4 canali. L'EQ in serie ne usava 6 quad + 2
  dual per canale (eq-serie §7): +24 quad sul mixer. Più scheda, circa
  +190 mA per rail (stima a 2 mA per sezione): il budget PSU (dec. 98)
  va riverificato.
- **Costo** [STIMA di Claude, senza preventivi]: ~130-160 € per canale
  contro i 45-60 € dell'EQ in serie, cioè +300…400 € sui 4 canali.
  Pesano op-amp (+24 quad) e condensatori di precisione della banca
  (~60 per canale). I pot diventano lineari standard: niente taper
  custom.
- **Ritardo di gruppo**: la somma è un allpass del 6° ordine. I bassi
  escono alcuni millisecondi dopo gli alti (ordine di grandezza del
  5-way: 7,9 ms di picco con incrocio a 90 Hz; qui meno, da misurare).
  Tutti i canali DJ hanno lo stesso EQ, quindi tra loro restano in fase.
- **Centro e tracking stereo** dipendono dalla linearità del pot doppio:
  un errore del 2 % al centro vale 0,17 dB. Tocca la voce 53 (ora: pot
  doppi lineari selezionati, o trim al centro).
- **Tolleranze della banca**: la piattezza vive sull'accoppiamento di 10
  sezioni di filtro e 3 allpass per lato (5-way: ±10 % su un edge = 0,02
  dB). Monte Carlo non fatto.

## 6. Numeri musicali da confermare (regola 2)

**[2026-10-13: Filippo rinvia la conferma all'ascolto sul prototipo (docs/02 B7). I valori qui sotto sono il punto di partenza.]**

1. **Incroci**: 150 / 500 / 2500 Hz (bande estreme larghe, medie poco
   profonde da sole) oppure 100 / 630 / 4000 Hz (medie a −26 dB, estreme
   più strette), o altri. Si rivedono a orecchio sul prototipo (B5).
2. **Boost massimo +6 dB** (assunto dalla SPECIFICA §4).
3. **Law lineare** della manopola (tabella §3): il taglio si concentra
   nell'ultimo quarto di corsa.

## 7. Non fatto

THD e clip reali (macro lineari: banco); Monte Carlo con le manopole
fuori dal centro; integrazione in `cdj-line-channel.md` §3.3 (polarità:
l'uscita è invertita) e nel piano Max; ricalcolo ufficiale del rumore di
canale e di sistema (todo 38); pot doppio lineare con contatto di fondo
corsa (voce 40).

**[2026-10-13: integrazione nel canale e rumore di canale e di sistema
FATTI → §9 e `docs/06` §10. Restano: THD e clip a banco, Monte Carlo
fuori dal centro, piano Max (todo 1), pot (voce 40).]**

## 8. Completamento v0.4-beta (2026-10-13, `sim/eq-iso/iso-b-*.cir`)

**Contatto di fondo corsa per banda.** Ogni pot ha un contatto che a
fondo corsa chiude il cursore a massa (50 mΩ nel modello). Il residuo
del pot non conta più:

| Manopole | Prima (solo pot, 10 Ω) | Col contatto |
|---|---|---|
| tutte a zero | −54 dB | **−100 dB** |
| LOW a zero, a 20 Hz | −52,7 dB | −69,7 dB |
| HIGH a zero, a 20 kHz | −53,0 dB | −71,9 dB |

Con 0 dBu in ingresso, a manopole chiuse escono −100 dBu: sotto il
rumore del canale. È silenzio. Il contatto sta su un nodo già quasi a
zero: non porta segnale e non fa click udibili (da confermare a banco).

**Servo DC sulla somma.** Solo la banda LOW porta la continua (le altre
tre passano da un passa-alto). Integratore 1 MΩ / 27 nF + partitore
100 kΩ / 100 Ω sul piedino + della somma: polo 0,053 Hz, corsa ±117 mV.
Con 20 mV di continua in ingresso l'uscita resta a 2,0 mV (offset
dell'op-amp del servo al massimo di datasheet), anche con LOW a +6 dB.
Piattezza: −0,0003 dB a 10 Hz, −0,0006 dB a 5 Hz.

**Rumore col servo**: −97,1 dBu A-wtd al centro (invariato), −92,2 tutto
al massimo, −103,6 tutto chiuso. Stima del canale DJ intero: circa −94
dBu A-wtd (EQ −97,1 + VCA di gain −97,5; era −90,0). Da ufficializzare
col ricalcolo di sistema.

**Ritardo di gruppo** (manopole al centro): 4,2 ms a 30 Hz, picco 4,7 ms
a 100 Hz, 4,1 a 150, 2,1 a 300, 1,4 a 500, 0,5 a 1 kHz, 0,2 a 2,5 kHz,
0,01 a 10 kHz. I bassi escono circa 5 ms dopo gli alti: dentro la
finestra in cui l'orecchio fonde i suoni (~20 ms), e meno del 5-way
(7,9 ms). I due ritardi si sommano lungo il percorso canale → 5-way:
circa 12 ms sul sub. Da sentire sul prototipo.

**Headroom interno**: nessun nodo della banca supera il livello
d'ingresso (massimo 0,0 dB). L'uscita sale di 6 dB con tutte le bande al
massimo: il clip dell'EQ arriva con circa +17,5 dBu in ingresso, come
nell'EQ in serie (stesso boost).

**Tolleranze** (Monte Carlo, 40 estrazioni, manopole al centro esatto,
20 Hz-20 kHz):

| Componenti dei filtri | Errore peggiore dal piatto |
|---|---|
| R 1 %, C 2 % | +0,28 / −0,22 dB |
| R 0,1 %, C 1 % | +0,13 / −0,13 dB |

FINDING: con componenti normali il centro NON resta entro ±0,1 dB. Con
R 0,1 % e C 1 % ci arriva quasi. Scelta d'ingegneria: R 0,1 %, C 1 %
(C0G o film) e un trimmer per incrocio a banco. Un'ondulazione di 0,1-
0,2 dB larga un'ottava non si sente come colore, ma i due lati stereo
vanno tenuti uguali (voce 53).

**Alimentatore** (`sim/system/psu-w1-iso.cir`): il ramo audio sale da
1,2 a circa 1,4 A. FINDING: l'avvolgimento audio deciso con la dec. 98
(2×21 V 2,5 A) lavora al 105-107 % della sua corrente nominale. Con
2×21 V 3,0 A lavora al 90-92 % e la tensione minima a rete −10 % resta
23,8 V (ne servono 21,7). Il trasformatore passa da 200 a circa 225 VA
(taglia commerciale: 225 o 250). **RATIFICATO da Filippo → DECISIONE 106.**

## 9. Integrazione nel canale: polarità diritta (2026-10-13, `sim/eq-iso/iso-c-*.cir`)

**Problema.** Con la somma invertente l'EQ usciva a polarità rovesciata.
Dall'uscita dell'EQ partono CUE, send FX, filtro e fader: la polarità va
raddrizzata lì, non più a valle. Rovesciata a valle, la cuffia (CUE) e
il master dello stesso canale si cancellano nel blend.

**Soluzione: somma NON invertente.** Nessun op-amp in più.

```
buffer LOW  ── 2,49k ─┐
buffer LM   ── 2,49k ─┤
buffer MH   ── 2,49k ─┼── nodo di mix ── piedino + ─┐
buffer HIGH ── 2,49k ─┤                             OP1612 ── uscita
servo ─ 100k ─┬─ 2k ──┘        piedino − ── 1,8k ───┘ (retroazione)
             499                    └── 200 ── massa
              └─ massa
```

Il nodo di mix fa la media dei cinque rami (1/5 per ramo); l'op-amp
guadagna 10: ogni banda arriva in uscita con guadagno 2, come prima.
Pot a metà = 0 dB, pot a fine corsa = +6 dB.

Vie scartate: invertitore dopo la somma (+1 sezione per lato, +1 dual
per canale); invertire le tre bande diritte prima della somma (+2
sezioni per lato); invertire fader o out driver (lascia rovesciati CUE,
send e filtro).

**Servo DC.** Stessa cella (integratore invertente 1 MΩ / 27 nF,
ingresso dal piedino +): qui il piedino + è il nodo di mix, e il servo
è il quinto ramo. Partitore 100 kΩ / 499 Ω + 2 kΩ: polo 0,058 Hz, corsa
±129 mV.

**Misure** (`iso-c-ac.cir`, `iso-c-dc.cir`, `iso-c-noise.cir`; colonna di sinistra: `iso-b-*.cir`, col contatto di fondo corsa):

| Grandezza | Somma invertente (§8) | Somma non invertente |
|---|---|---|
| Fase a 5 Hz (0° = diritta) | +173,3° | **−6,7°** |
| Centro, 20 Hz-35 kHz | −0,004…0,000 dB | +0,000…+0,004 dB |
| Tutte a zero | −100,0 dB | −100,0 dB |
| LOW a zero, a 50 Hz | −38,3 dB | −38,3 dB |
| HIGH a zero, a 8 kHz | −40,5 dB | −40,5 dB |
| LOW-MID a zero, a 274 Hz | −16,0 dB | −16,0 dB |
| MID-HIGH a zero, a 1,1 kHz | −22,4 dB | −22,4 dB |
| Tutte al massimo | +6,01 dB | +6,01 dB |
| Continua in uscita (20 mV in ingresso, offset servo 2 mV) | 2,0 mV | 2,0 mV |
| Rumore al centro | −97,1 dBu A-wtd | **−97,3 dBu A-wtd** |
| Rumore tutte al massimo | −92,2 | −92,3 |
| Rumore tutte a zero | −103,6 | −104,8 |
| Ritardo di gruppo a 30 Hz | 4,2 ms | 4,2 ms |

Con 20 mV di continua in ingresso l'uscita del servo sta a −1,8 V
(centro) e −3,8 V (LOW al massimo): lontana dai rail.

**Costo della scelta.** L'op-amp di somma non lavora più a massa
virtuale: i due piedini seguono il segnale, a 1/10 dell'uscita (−20 dB
sull'ingresso al centro, −14 dB con tutte le bande al massimo: circa
1,1 V di picco al clip). Per un OPA1612 è un modo comune piccolo;
l'effetto sulla distorsione si verifica a banco (le macro sono lineari).

**Silicio per canale DJ stereo**: invariato. 12 quad OPA1654 (banca,
allpass, buffer dei pot) + 1 dual OPA1612 (le due somme) + 1 dual per i
due servo (classe OPA2134, come nel modello).

**Canale completo** (`sim/cdj/channel-noise-v04-iso.cir`: blocco della
continua, buffer, VCA di gain, isolator, fader, out driver):

| Manopole EQ | Out driver di canale | Target (dec. 89) |
|---|---|---|
| tutte al centro | **−94,6 dBu A-wtd** (−92,9 piatto) | ≤ −80: PASS 14,6 dB |
| tutte al massimo | −89,1 dBu A-wtd | PASS 9,1 dB |
| tutte a zero | −104,8 dBu A-wtd | — |

Il canale con l'EQ in serie faceva −90,0. La stima «circa −94» del §8 è
confermata. Sistema: `docs/06` §10.

Valori [PROVVISORI — regola 3]. Polarità assoluta dello stadio VCA di
gain (a monte dell'EQ, comune a tutte le prese): la macro è ideale e
diritta; il segno reale del 218x col suo stadio d'uscita si verifica su
datasheet e a banco. Non può creare cancellazioni dentro il canale.
