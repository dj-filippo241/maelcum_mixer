# RISULTATI P2 — MC-5WAY (2026-10-15)

Piano: `docs/proto-max/piano.md` §2 P2. Modello: `coefficienti/fiveway.py`.
Generatore: `genera_5way.py`. Verifiche: `taratura_sat.py` (saturatori
contro LTspice), `prova_5way.py` (codice gen~ contro modello).

## Cosa contiene

- **KILL** SUB / KICK / MID / HIGH / SUPER: banca LR4 allineata in fase
  (five-way §3.1), taglio netto come lo switch vero (dec. 88).
- **EQ creativo**, 5 campane in serie dopo la banca (§4): GAIN fino a
  +15 / +15 / +15 / +12 / +9 dB, notch a fine corsa CCW; POSITION
  20-120 / 80-400 / 250-1500 / 800-5000 / 3000-20000 Hz, law
  esponenziale; WIDTH Q3 / Q1 / Q0,5.
- **GROWL** (sotto 350 Hz) e **NASTRO** in parallelo al pulito (§5bis,
  dec. 99). Stato dopo gli ascolti (§6-9): GROWL lineare, Rf 47k; NASTRO
  taper A × 0,85; selettori GROWL VER (DEC.99 / LIBERO / BANDE) e NASTRO
  VER (OGGI / COMPLETO / EXCITER / CLASSE A / LIBERO / COMPL. MEDI /
  BANDE; §11-13).
- **CROSSOVER** A-H, solo prototipo, per B3 (§1; E aggiunta in §6, F e H in §20).
- Riferimento interno −6 dB (dec. 73): conta solo per i saturatori.
- Livelli: 0 dBu = −12 dBFS di picco [PROVVISORIO, come P1]. Tutto a 4×.
- Non modellati: rumore, clipping dei rail (+21 dBu circa nel dominio
  interno), servo DC del make-up (in digitale non c'è continua da
  togliere), deriva termica delle celle.

## 1. Varianti di CROSSOVER (B3, scelte da Filippo sul benchmark)

| Variante | SUB/KICK | KICK/MID | MID/HIGH | HIGH/SUPER | Fonte |
|---|---|---|---|---|---|
| A | 90 | 350 | 1200 | 3500 | design attuale (dec. 66, resoconto ChatGPT) |
| B | 80 | 200 | 1200 | 6000 | Jah Tubbys Devastator ordinato su misura (forum Dubsounds) |
| C | 75 | 190 | 2200 | 8000 | JB Audio Units, preamp 5 vie di serie |
| D | 80 | 220 | 1500 | 7000 | Speakerplans, punti di partenza di un moderatore |

Benchmark: tutti tagliano KICK/MID a 180-220 Hz (noi 350) e HIGH/SUPER a
5-8 kHz (noi 3500). Mostec 4 vie: 90 / 200 / 4500. Fonti: jbaudiounits.com
(5 Ways Pre-Amp), mostec.co.uk (Preamps), forum.dubsounds.fr (Jah Tubbys,
quali frequenze), forum.speakerplans.com (5 Way Horn system; Small
Reggae/Dub sound system). Sono specifiche e scelte di chi costruisce, non
misure.

**Profondità del KILL al centro della via** (dB del resto della banca,
formule analogiche; SUB a 40 Hz, SUPER a due volte l'ultimo crossover):

| Variante | SUB | KICK | MID | HIGH | SUPER |
|---|---|---|---|---|---|
| A | −28,5 | −18,4 (177 Hz) | −16,4 (648 Hz) | −14,0 (2,0 kHz) | −24,5 |
| B | −24,6 | −11,8 (126 Hz) | −25,4 (490 Hz) | −22,4 (2,7 kHz) | −24,6 |
| C | −22,5 | −12,0 (119 Hz) | −36,5 (647 Hz) | −17,3 (4,2 kHz) | −24,6 |
| D | −24,6 | −13,2 (133 Hz) | −27,5 (574 Hz) | −21,3 (3,2 kHz) | −24,6 |
| E | −20,8 (45 Hz) | −9,6 (117 Hz) | −28,0 (452 Hz) | −22,4 (2,7 kHz) | −24,6 |

Lettura: con 24 dB/ottava una via stretta non si spegne mai del tutto.
La KICK del benchmark (80-200 Hz, 1,3 ottave) scava ~12 dB; la nostra
(90-350, 2 ottave) ~18. In cambio la MID larga del benchmark scava
25-36 dB. Esempio: KILL SUB su un tono a 60 Hz con la variante A lascia
−15,6 dB (la KICK parte a 90 Hz e 60 Hz è a mezza ottava).

## 2. Modello contro le formule (`fiveway.py`)

- Somma della banca, digitale a 4× contro analogico, 10 Hz-16 kHz:
  0,0000 dB. La bilineare conserva LP4 + HP4 = A2: la somma resta
  piatta esatta anche nel digitale.
- Celle: +15,00 dB al centro con le tre WIDTH; notch profondo
  (−318 dB numerico). La cella vera di LTspice fa −46…−47 dB (§4.2):
  differenza non udibile, il notch del modello è più profondo.

## 3. GROWL e NASTRO contro LTspice (`taratura_sat.py`)

Riferimento: `sim/five-way/drive2-chain.cir` (50 Hz) e
`drive2-chain-1k.cir`, 6 posizioni × 4 livelli, stesse condizioni del
netlist (Vs2 da 2,1 V, 3 s, ultime 10 periodi, 8 armoniche).

- GROWL 50 Hz e 1 kHz: livello entro 0,01 dB; THD entro 0,02 punti,
  salvo +10 dBu a fine corsa: 18,8 % contro 19,5 % (0,65 punti).
- NASTRO: livello entro 0,01 dB; THD entro 0,12 punti.

**FINDING** (il primo modello del NASTRO sbagliava di +0,26 dB a basso
livello e di 8 punti di THD sui picchi): servono due cose del circuito
che il design non mette in evidenza.
1. Il sommatore carica il drain attraverso il condensatore d'uscita
   (Rts = 10k/kt = 48,5 k in parallelo a Rd 1,5 k): −3 % di guadagno.
2. Sui picchi a +10 dBu il JFET esce dalla saturazione ed entra in
   triodo: Shichman-Hodges completo, Newton sulla corrente.
Il punto di lavoro a riposo si trova solo smorzando l'iterazione
(Vs2 = 900 Id diretto oscilla): Vs2 2,018 V, Id 2,24 mA, Vd 14,6 V.

## 4. Codice gen~ contro modello (`prova_5way.py`)

Testo di `MC-5WAY.genexpr` tradotto in Python e suonato a 48 kHz sui
due canali, contro `fiveway.Completo` a 192 kHz senza halfband.

**PASS, 155 punti su 155**, ogni punto sui due canali:
- tutto al centro: trasparente, 0,00 dB a 30 / 200 / 1000 / 8000 Hz;
- KILL di ogni via a 60 / 200 / 700 / 2000 / 6000 Hz, variante A:
  scarto ≤ 0,05 dB (es. KILL KICK a 200 Hz −17,59 dB);
- varianti B, C, D: KILL KICK e KILL SUPER a 120 Hz e 5 kHz;
- EQ1-EQ5 al centro della campana: GAIN 100 / 75 / 25 / 3 / 0 %, WIDTH
  Q3 / Q1 / Q0,5: scarto ≤ 0,05 dB; il notch (0 %) sotto −120 dB in
  entrambi (la prima versione della prova confrontava residui numerici
  a −230…−320 dB e segnava 10 punti FUORI: corretto il confronto, non
  il dispositivo);
- GROWL e NASTRO a 50 Hz, 0 e +10 dBu, da soli e insieme: ≤ 0,01 dB;
- canali indipendenti: con R a zero e L a 0 dBu (GROWL e NASTRO al
  50 %), l'uscita R resta 0,0.

Altri controlli:
- Nessuna variabile passa dal lato L al lato R (controllo automatico
  delle letture, lo stesso che ha trovato l'errore di P1).
- Patch: 23 comandi, ognuno sul suo `Param`; codice nella patch uguale
  al `.genexpr`; comandi del pannello senza sovrapposizioni (426 × 166
  px).
- Stress: comandi mossi a salti ogni 30 ms (KILL, GAIN agli estremi,
  WIDTH, CROSSOVER, GROWL, NASTRO), quadra a 0 dBFS, a 44,1 e 96 kHz:
  nessun valore non finito. Picco fino a 4,6 (+13 dBFS) con boost
  +15 dB: la scheda audio satura; il circuito vero arriva al rail.

## Non verificato

- Sintassi gen~ e CPU: si vedono all'apertura in Live.
- Law del GAIN: il tratto CCW (−27 dB al 5 %, poi notch) è preso dalle
  shelf di eq-serie §10 [PROVVISORIO]; per le campane il design dice solo
  «accelerazione negli ultimi 5 %». Da sentire.

## 5. Errore trovato in Live: passava solo il SUB (2026-10-15)

Segnalato da Filippo al primo ascolto. Il SUB è l'unica via che non usa
l'uscita HP della funzione SVF; la spina delle altre quattro sì. La
prima versione aveva `svf()` con **tre** valori di ritorno (lp, bp, hp,
la spina usava il terzo) e le variabili esterne con gli stessi nomi dei
locali della funzione. La traduzione Python gestisce entrambe le cose,
gen~ no: la prova passava, Live suonava solo il SUB.

Correzione (senza conferma da Max sulla causa esatta, una delle due o
entrambe): tre funzioni a uscita singola `svlp` / `svbp` / `svhp`;
nessun nome esterno uguale a un parametro o locale di funzione
(controllo automatico: nessuno). Regola per i prossimi dispositivi:
funzioni con un solo valore di ritorno, nomi esterni distinti dai
locali. Prova di nuovo PASS 155/155. Conferma finale: ascolto.

## 6. Primo ascolto di Filippo e modifiche (2026-10-15)

Parole di Filippo: «il nastro è troppo aggressivo, mentre growl non
abbastanza e mi pare funzioni solo con le medie e le alte killate».
Impianto di Filippo (DSP): 37 / 80 / 170 / 1200 Hz / 20 kHz.

Lettura (mostrata a Filippo prima delle scelte):
- il materiale masterizzato suona in Live ~6 dB sopra il nominale del
  prototipo (0 dBu = −12 dBFS di picco): NASTRO al 100 % passa da 5,5 % a
  19 % di THD; GROWL comprime il basso invece di sporcarlo;
- le armoniche del GROWL (100-300 Hz) cadono nella zona cassa e medie
  basse: con il mix pieno si confondono, con MID e HIGH killate si
  sentono.

Scelte di Filippo [PROVVISORIE, in ascolto]: variante E del CROSSOVER;
NASTRO pot logaritmico con fine corsa al 30 %; GROWL con più spinta.
Proposta scartata: manopola LIVELLO di taratura (opzione 1).

- **E 80/170/1,2k/6k** nel selettore (gli incroci dell'impianto +
  HIGH/SUPER a 6 kHz). KILL KICK al centro −9,6 dB: la via 80-170 Hz è
  poco più di un'ottava.
- **NASTRO**: taper A (10 % a metà corsa) × 0,3. Hardware: pot log 10k
  con 23,3k in serie sopra. Fine corsa al nominale ≈ 1,6 % THD.
- **GROWL**: Rf 47k, kg 0,4634. LTspice (`sim/five-way/drive2-chain-g47.cir`,
  `-g47-1k.cir`) contro modello: livello entro 0,00 dB, THD entro
  1,3 punti (picchi +10 dBu a fine corsa: 18,4 % contro 19,7 %).

| GROWL 100 % | 22k (prima) | 47k (ora) |
|---|---|---|
| programma piano −16 dBu (interno) | 4,9 %, +2,1 dB | 18 %, +4,5 dB |
| nominale −6 dBu | 20 %, −0,3 dB | 25 %, −0,5 dB |
| spinto 0 dBu | 22 %, −3,2 dB | 26 %, −4,5 dB |
| medi 1 kHz al nominale | 0,04 %, −0,3 dB | 1,2 %, −1,0 dB |

Prova gen~ contro modello: **PASS 163/163** (con la variante E). Stress:
nessun valore non finito; i picchi alti (fino a +20 dBFS) nascono dai
salti istantanei dei comandi su boost Q3: con i comandi fermi lo stesso
caso fa 2,7.

Da fare prima di congelare: rumore del ramo GROWL a 47k
(`drive2-noise.cir`).

## 7. Secondo ascolto: NASTRO al 70 %, GROWL LIBERO (2026-10-15)

Parole di Filippo: «il nastro è troppo cappato, cappamelo al 70 %»;
«il growl mi sembra funzioni un po' al opposto di quello che mi
immaginavo: al posto che ingigantire i bassi distorcendoli e "collandoli"
mi pare che li indebolisca»; «fammi una versione in cui ti dimentichi
temporaneamente di dec. 99».

- **NASTRO**: fine corsa al 70 % dell'originale [SUPERATO da §8: 85 %] (pot log 10k + 4,3k in
  serie sopra).
- **Perché il GROWL dec. 99 indebolisce**: è tarato a pari volume sul
  nominale; sul materiale di Filippo (~0 dBu interni) comprime: basso
  −4,5 dB a fine corsa, −9,7 sui picchi caldi.
- **GROWL LIBERO** (solo prototipo, selettore GROWL VER DEC.99 /
  LIBERO): pot doppio, un tratto è la R d'ingresso del clipper (10k →
  1,26k = spinta 0 → +18 dB, lineare in dB), l'altro la miscela che
  sostituisce il basso pulito; kl 0,6783 = +6 dB di basso a fine corsa
  su 0 dBu interni [SUPERATO da §8: 0,6043 = +5 dB]. Nessuno stadio di guadagno davanti ai diodi: con uno
  stadio a +18 dB i picchi caldi andavano al rail (±16 V) e tosavano duro.

**LIBERO, modello contro LTspice** (`sim/five-way/drive2-libero.cir`,
50 Hz, THD % e variazione del fondamentale):

| GROWL | piano −16 | nominale −6 | 0 dBu (mix di Filippo) | +10 |
|---|---|---|---|---|
| 25 % | 11,8 · +3,9 dB | 9,1 · +1,1 | 6,2 · −0,1 | 2,6 · −0,6 |
| 50 % | 20,2 · +8,0 | 16,9 · +2,9 | 12,4 · +0,7 | 5,8 · −1,5 |
| 100 % | 26,5 · +14,9 | 20,8 · +8,6 | 15,5 · +5,9 | 7,5 · +3,1 |

LTspice e modello coincidono in tutte le 12 caselle: THD entro 0,1
punti, livello entro 0,1 dB. Prova gen~ contro modello: **PASS 175/175**.

Conflitto aperto: LIBERO alza il volume del basso (fino a +15 dB sul
basso piano), contro la dec. 99 (c). Se Filippo sceglie LIBERO, la
dec. 99 (c) va rivista. Rumore del ramo da misurare prima di congelare.

## 8. Terzo ascolto: GROWL LIBERO +5 dB, NASTRO 85 % (2026-10-15)

Parole di Filippo: «al momento mi sembra quasi giusto: farei il growl un
po' più sciallo (ma ci siamo quasi) e il nastro un po' più aggressivo».

- GROWL LIBERO: spinta invariata (+18 dB), kl 0,6783 → **0,6043** = +5 dB
  di basso a fine corsa sul mix di Filippo (era +6). Provata anche la
  spinta a +15 dB: sul mix la THD SALE (15,5 → 18 %) perché serve più
  miscela per lo stesso volume; scartata. La THD la decide la spinta,
  il volume la miscela.
- NASTRO: fine corsa all'**85 %** (pot log 10k + 1,8k in serie sopra).
- LTspice `drive2-libero.cir` con kl 0,6043, contro modello: tutte le 12
  caselle entro 0,1 punti di THD e 0,1 dB (fine corsa sul mix: 15,4 %,
  +4,9 dB di fondamentale). Prova gen~: **PASS 175/175**.

Domanda aperta a Filippo: alternative al NASTRO da mettere nel
prototipo (nastro completo con enfasi e head bump, trasformatore,
exciter, classe A, valvola).

## 9. Alternative al NASTRO: COMPLETO, EXCITER, CLASSE A (2026-10-15)

Domanda di Filippo: «mi chiedevo se ci fossero altre opzioni al posto che
la distorsione nastro da valutare». Proposte (nastro completo,
trasformatore, exciter, classe A, valvola; esclusi i compressori =
dinamica automatica). Scelta di Filippo: «nastro, exciter e transistor».
Selettore NASTRO VER (solo prototipo): OGGI / COMPLETO / EXCITER /
CLASSE A, stessa manopola NASTRO (taper A × 0,85). Modello:
`coefficienti/alternative.py`; taratura `taratura_alt.py`; confronto
`confronto_alt.py`.

| Versione | Circuito | Taratura |
|---|---|---|
| COMPLETO | JFET del NASTRO tra enfasi (non invertente 23,33k / 10k + 3,183n: zero 1,5 kHz, polo 5 kHz, +10,5 dB) e de-enfasi passiva inversa; head bump +3 dB a 80 Hz, Q 1, nel ramo saturato | kt del NASTRO |
| EXCITER | passa-alto SK 2 poli 3 kHz → clipper Rin 10k, Rf 100k, 1 diodo + 1k / 2 diodi + 1k → passa-alto CR 3 kHz → si somma | ke 0,30509 = +3 dB su 5 kHz a −16 dBu, fine corsa |
| CLASSE A | NPN 2N3904 a emettitore comune, Rc 3,3k, Re 100 + 900 bypassata, base 2,65 V + 0,4 × ingresso, collettore AC nel sommatore | kc 0,0895 a pari livello al nominale; attenuazione 0,4 = THD del NASTRO OGGI sul mix |

**Modello contro LTspice** (`sim/five-way/alt-completo.cir`,
`alt-completo-80.cir`, `alt-completo-8000.cir`, `alt-exciter.cir`,
`alt-classe-a.cir`; 4 livelli × 4 posizioni):

| Caso | scarto THD | scarto livello |
|---|---|---|
| COMPLETO 1 kHz | 0,02 punti | 0,00 dB |
| COMPLETO 8 kHz | 0,80 punti (picchi +10) | 0,02 dB |
| COMPLETO 80 Hz | 0,11 punti | 0,00 dB |
| EXCITER 5 kHz | 0,12 punti | 0,04 dB |
| CLASSE A 1 kHz | ≤ 0,4 punti fino a 0 dBu; 4,2 punti sui picchi +10 a fine corsa (32 % contro 28 %) | 0,46 dB |

Cosa fanno (fine corsa):
- COMPLETO: al nominale gli acuti a 8 kHz saturano cinque volte i medi
  (22 % contro 4,4 %); basso a 80 Hz +2,5 dB.
- EXCITER: +3 dB e 17,5 % sugli acuti piani, quasi niente su quelli forti
  (2,5 % a +10 dBu): tira fuori il dettaglio, non ingrossa.
- CLASSE A: pulito al nominale (3,9 %), 19 % sul mix di Filippo, 28 % sui
  picchi: pulito finché non spingi.

**FINDING del transistor** (tre modelli prima di coincidere): (1) senza
alta iniezione (IKF) ed Early dentro la giunzione il modello sporca meno
(fino a 5,5 punti); (2) l'Early va limitato alla zona attiva, se no
esplode in saturazione; (3) in saturazione la base impone ancora la
corrente di emettitore: il collettore segue l'emettitore e il
condensatore di emettitore integra tutta la corrente. Il tetto «a
corrente» (minimo liscio su Ic) sbagliava in modo insensibile ai
parametri.

Nel codice gen~: funzioni a un ritorno (`op1`, `clipe`, `bstep` con
stato in Data); il parametro del selettore si chiama `nver` perché `nv`
è un locale dei clipper (controllo nomi esteso a Param/History/Data:
nessuno in comune).

Prova gen~ contro modello: **PASS 191/191** (con le tre alternative su
entrambi i canali).

## 10. NASTRO LIBERO (2026-10-15)

Richiesta di Filippo: «metti anche nastro con scelta libero in
mc-5way». Lettura: come il GROWL LIBERO, un NASTRO che si dimentica della
dec. 99 (può alzare il volume, spinge di più). Quinta voce del selettore
NASTRO VER, stessa manopola NASTRO (taper A × 0,85). Numeri scelti da
Claude, da correggere a orecchio: spinta massima +12 dB, +3 dB sul mix a
fine corsa.

Circuito: il JFET del NASTRO di oggi (Rd 1,5k, Rs 150 + 900 bypassata,
drain caricato come oggi) con uno stadio di spinta davanti alla 10k del
gate: op-amp non invertente, un tratto del pot doppio, 0 → +12 dB
lineare in dB. Con +12 dB i picchi +10 dBu interni arrivano a 13,9 V,
sotto il rail di 16 V (oltre +12 dB andrebbero al rail). Il gate entra in
conduzione (diodo gate-source di NJ310, Is 10f) e si appoggia sulla
source; sul lato negativo il JFET va in interdizione. Sommatore con
Rto = Rtl = 10k · kl / kt: dl = −kl · vtac − y1, kl = **0,1977** (+3 dB a
regime sul mix di Filippo, 1 kHz, fine corsa; `taratura_alt.tara_libero`).
Modello: `alternative.Libero`.

**A regime** (la polarizzazione del JFET, Cb 2200 µF su 900 Ω, si
assesta in ~4,5 s), 1 kHz, THD % e livello RMS; a 50 Hz identico:

| NASTRO | piano −16 | nominale −6 | 0 dBu (mix di Filippo) | +10 |
|---|---|---|---|---|
| 25 % | 0,12 · +0,1 dB | 0,49 · +0,1 | 1,3 · 0,0 | 0,84 · −0,2 |
| 50 % | 0,48 · +0,7 | 2,5 · +0,5 | 4,0 · +0,1 | 1,8 · −0,4 |
| 75 % | 3,3 · +5,0 | 19 · +3,3 | 24 · +1,3 | 12 · −2,5 |
| 100 % | 7,1 · +10,3 | 38 · +7,0 | 39 · +3,0 | 31 · −5,0 |

Cosa fa, a fine corsa contro il NASTRO OGGI (stesso modello, 1 kHz): sul
tuo mix sporca 2,5 volte tanto (39 % contro 15,5 %) e alza di 3 dB
invece di abbassare di 1; al nominale 38 % contro 4,6 %; sui picchi forti
fa come OGGI (31 % contro 30 %, −5 dB tutti e due). Il programma piano
cresce di 10 dB: le parti deboli salgono, quelle forti si appiattiscono. Fino a metà corsa quasi non si sente
(taper A: miscela al 10 %), il carattere arriva nell'ultimo terzo.

**Modello contro LTspice** (`sim/five-way/nastro-libero.cir`, 1,5 s dal
punto di lavoro, 16 caselle, `confronto_alt.py`): THD entro 0,02 punti,
livello entro 0,00 dB.

Nel codice gen~: funzione `gatev` (un ritorno; locali `gvg`, `gax`,
`gf`, `gdf`: la prima stesura usava `gex`, che è il passa-alto
dell'EXCITER, trovato col controllo dei nomi); stato in `sa` (4 per
lato). Prova gen~ contro modello: **PASS 203/203**.

Conflitto aperto, come per il GROWL LIBERO: alza il volume, contro la
dec. 99 (c) (todo 61). Rumore dello stadio di spinta da misurare prima di
congelare (todo 62).

## 11. Rumore delle versioni in prova (2026-10-15, todo 62)

`sim/five-way/module-noise-p2.cir`: il modulo 5-way intero
(`module-noise-v04.cir`: banca, celle, make-up) col drive del prototipo,
circuiti reali (op-amp con rumore, pot veri, buffer, sommatori; il
selettore NASTRO VER come interruttori). Metodo a 16 punti,
`sim/mic/noise_total.py`. Uscita del modulo, manopola a fine corsa
salvo dove scritto; target del modulo −80 dBu A-wtd (dec. 89):

| Caso | dBu flat | dBu A-wtd | guadagno a 50 Hz / 1 kHz / 8 kHz (silenzio) |
|---|---|---|---|
| Manopole chiuse | −84,4 | **−85,9** | 0 / 0 / 0 dB |
| GROWL DEC.99 (47k) | −84,0 | −85,8 | +6,7 / −1,2 / −0,1 |
| GROWL LIBERO 100 % | −73,2 | **−79,6** | **+27,0** / +5,1 / −0,4 |
| GROWL LIBERO 50 % | −83,1 | −85,9 | +13,0 / −3,6 / −0,1 |
| NASTRO OGGI | −84,3 | −85,8 | 0 / 0 / 0 |
| COMPLETO | −84,1 | −85,7 | +1,6 / +0,1 / 0 |
| EXCITER | −75,6 | **−78,6** | 0 / −0,6 / **+9,8** |
| CLASSE A | −85,2 | −86,7 | −0,9 / −0,9 / −0,9 |
| NASTRO LIBERO 100 % | −73,8 | **−75,3** | **+10,6** / +10,6 / +10,6 |
| NASTRO LIBERO 50 % | −83,8 | −85,3 | +0,6 / +0,6 / +0,6 |
| GROWL LIBERO + NASTRO LIBERO | −62,5 | **−69,0** | +37,7 / +15,8 / +10,3 |

Lettura:
- I circuiti dei saturatori sono silenziosi. Quello che sale è il
  **guadagno a segnale minimo**: nel silenzio i diodi e il JFET non
  lavorano, e le versioni LIBERO e l'EXCITER amplificano il fruscio che
  arriva dalla banca e dalle celle. Il rumore riportato all'ingresso
  (EIN) resta −84 dBu per i LIBERO; sale solo con l'EXCITER (−75 dBu),
  perché il suo clipper guadagna +20 dB sugli acuti.
- **GROWL LIBERO a fine corsa**: +27 dB a 50 Hz nel silenzio (sul basso
  piano era +15: con la musica i diodi conducono e il guadagno scende).
  Si sente come un rombo basso tra un pezzo e l'altro; la pesatura A lo
  nasconde (−79,6 A-wtd contro −73,2 piatto).
- **NASTRO LIBERO a fine corsa**: +10,6 dB su tutta la banda, cioè il
  fruscio di fondo sale di 10 dB nelle pause. È lo stesso meccanismo del
  «+10 dB sul programma piano».
- **EXCITER**: +10 dB di fruscio sugli acuti.
- A metà corsa tutte le versioni restano entro 0,6 dB dal modulo chiuso.
- DEC.99 (47k), OGGI, COMPLETO e CLASSE A non cambiano il rumore del
  modulo (entro ±0,8 dB).

Per il sistema (dec. 89: −78 dBu A-wtd, con FX e overdrive aperti già
accettati come condizione d'uso, dec. 95/100): NASTRO LIBERO e le due
LIBERO insieme a fine corsa stanno sopra; GROWL LIBERO ed EXCITER al
limite. Non decide niente da solo: è un costo da mettere accanto a
quello che senti. Leve d'ingegneria, se una LIBERO vince: limitare il
guadagno a segnale minimo (per il GROWL, Rf più bassa; per il NASTRO,
meno spinta), al prezzo di un po' di carattere sul programma piano.

Modelli: la bobina del head bump del COMPLETO è ideale (in hardware un
giratore, qualche op-amp in più); il partitore della CLASSE A è
dimensionato col carico della base (52,8k / 9,11k, 10k in serie).

## WIDTH continuo (2026-10-22, dec. 117 e 129 C2, todo 127)

Il selettore WIDTH Q3 / Q1 / Q0,5 diventa una manopola continua come nel
circuito (five-way §4.3): alpha = 0,1…1 con pot log 20 %, Q = 0,3/alpha →
Q 3,00 / 1,58 / 1,07 / 0,47 / 0,30 a 0 / 25 / 50 / 75 / 100 %
(`fiveway.q_width`). Nel pannello le tre manopole per via sono più basse
(40 px) per stare nei 169 px di Live. Lisciatura 10 ms come le altre
manopole (prima 1 ms, era un selettore). MC-5WAY-S uguale.
Prove: prova_5way (WIDTH 0 / 30 / 50 / 100 %, gen~ contro modello) e
prova_semplice.


## 11. COMPLETO MEDI e NASTRO lineare (2026-10-31)

Libretto 9.3, Filippo: «nastro forse deve essere più udibile prima nella
curva»; poi «non sono sicuro sia ancora abbastanza». La manopola NASTRO
passa da taper A 10 % a log 20 % e poi a **lineare** (`fiveway.TAPER_A_MID`
0,5; a metà corsa 0,425 del fondo corsa 0,85) [PROVVISORIO], per tutte le
versioni di NASTRO VER.

Sesta voce di NASTRO VER, **COMPL. MEDI** (Filippo: «un completo che
sporca un po' più i medi e un po' meno gli acuti», «senza gobba»): il
COMPLETO con l'enfasi spostata in basso e ridotta, zero 300 Hz / polo
600 Hz (+6 dB da ~1 kHz in su; COMPLETO +10,5 dB da ~5 kHz), niente head
bump. Hardware: non invertente Rf 10k / (Rg 10k + 26,53n), de-enfasi
passiva 10k serie, 10k + 26,53n a massa. Modello `alternative.medi`.

Al nominale (-6 dBu, miscela 0,85), THD:

| | 300 Hz | 1 kHz | 3 kHz | 8 kHz |
|---|---|---|---|---|
| COMPLETO | 4,4 % | 4,4 % | 10,4 % | 22,2 % |
| COMPL. MEDI | 5,1 % | 11,5 % | 15,0 % | 15,5 % |

Scartata 500 / 1250 Hz (+8 dB): 8 kHz 21 %, acuti quasi come il COMPLETO.

Modello contro LTspice (`sim/five-way/alt-completo-medi.cir`,
`alt-completo-medi-8000.cir`, `confronto_alt.py`): 1 kHz scarto 0,05
punti e 0,02 dB; 8 kHz 0,11 punti e 0,02 dB. `confronto_alt.py` usa ora
miscele fisse (i B25-B99 dei netlist), non la law della manopola.

## 12. GROWL e NASTRO a bande (2026-11-03, dec. 165 e 166)

Revisione delle tabelle di distorsione con Filippo. Modello del prototipo
(`fiveway.py`, `alternative.py`), 192 kHz, THD da 8 armoniche, volume RMS
rispetto all'ingresso. Livelli interni: −16 piano, −6 nominale, 0 dBu =
mix di Filippo, +10 picchi. Vie del crossover E: SUB 50 Hz, KICK 120 Hz,
MID 500 Hz, HIGH 3 kHz, SUPER 12 kHz. Il modello di oggi riproduce le
tabelle LTspice già scritte (GROWL LIBERO fine corsa sul mix: 15 %, +5,0 dB,
come §8; NASTRO LIBERO come §10). Le versioni nuove NON hanno ancora una
netlist LTspice [PROVVISORIO].

Prima lettura (stato di oggi, tutte le voci con la manopola NASTRO lineare):
il GROWL LIBERO sui picchi a +10 dBu scende al 7,5 % (le 2,2k in serie ai
diodi lo riportano lineare) e a 1 kHz al nominale sporca al 57 % perdendo
4,4 dB (il passa-basso a 2 poli lascia entrare i medi, la spinta +18 dB li
porta ai diodi); il NASTRO LIBERO distorce uguale su tutte le vie (39 % sul
mix a fine corsa).

### GROWL a bande, variante D (`coefficienti/growl_bande.py`)

Circuito in five-way §5bis REV 2026-11-03. Varianti provate: B (LP 2 poli
350 Hz: 500 Hz al 56 %, 1 kHz al 100 %), C (4 poli 350 Hz: 500 Hz al 45 %),
D (4 poli 250 Hz, scelta di Filippo), E (4 poli 200 Hz: kick 51 % e −5,9 dB
sul colpo).

| Via, fine corsa | piano −16 | nominale −6 | mix 0 | picchi +10 |
|---|---|---|---|---|
| SUB 50 Hz | 32 % · +16,8 dB | 31 % · +8,6 | 28 % · +4,2 | 22 % · −1,7 |
| KICK 120 Hz | 36 % · +16,0 | 40 % · +7,0 | 42 % · +2,4 | 33 % · −4,0 |
| MID 500 Hz | 9,6 % · +7,6 | 20 % · +4,9 | 23 % · +2,0 | 20 % · −3,0 |
| 1 kHz | 0,01 % · +1,0 | 0,82 % · +0,9 | 6,0 % · −0,1 | 7,2 % · −2,6 |
| HIGH 3 kHz | 0 % · 0,0 | 0,11 % · 0,0 | 2,3 % · −0,2 | 5,3 % · −1,3 |
| SUPER 12 kHz | 0 % | 0 % | 0 % | 0,68 % |

A metà corsa, sul mix: SUB 18 % +0,7 dB, KICK 24 % −0,8, 500 Hz 7,1 %,
1 kHz 1,4 %, 3 kHz 0,2 %. Al 10 %: SUB 3,2 %, 500 Hz 0,25 %.

### NASTRO a bande, variante B8 (`coefficienti/nastro_bande.py`)

Varianti provate: B1-B3 (taglio dei bassi a una cella, super a una cella:
super 43-53 %, sub e kick +10 dB di volume), B4-B5 (super a due celle,
de-enfasi parziale: sub 31 % sui picchi), B6-B7 (bassi a due celle), B8
(B7 col volume dei bassi corretto, scelta).

| Via | mix, 50 % | mix, 100 % | nominale, 100 % | picchi, 100 % |
|---|---|---|---|---|
| SUB 50 Hz | 0,28 % · −1,8 dB | 1,6 % · +1,4 | 0,77 % · +1,4 | 6,3 % · +1,0 |
| KICK 120 Hz | 0,63 % · −0,5 | 2,8 % · +5,1 | 1,3 % · +5,2 | 18 % · +2,4 |
| MID 500 Hz | 10 % · +1,2 | 30 % · +5,1 | 19 % · +7,9 | 24 % · −2,6 |
| HIGH 3 kHz | 14 % · −0,4 | 36 % · +2,1 | 29 % · +5,3 | 28 % · −5,7 |
| SUPER 12 kHz | 2,7 % · −2,3 | 26 % · −1,6 | 8,0 % · +0,3 | 31 % · −6,8 |

La tabella mette ogni via allo stesso livello; nella musica sub e kick sono
più forti e i super più deboli. Volume a fine corsa disomogeneo fra le vie
(−1,6…+5,1 dB sul mix): da rifinire dopo l'ascolto.

### Insieme (`coefficienti/combo_bande.py`, GROWL D + NASTRO B8)

| Sul mix 0 dBu | SUB | KICK | MID | HIGH | SUPER |
|---|---|---|---|---|---|
| GROWL 100 % | 28 % · +4,2 | 42 % · +2,4 | 23 % · +2,0 | 2,3 % · −0,2 | 0 % |
| NASTRO 100 % | 1,6 % · +1,4 | 2,8 % · +5,1 | 30 % · +5,1 | 36 % · +2,1 | 26 % · −1,6 |
| tutte e due 100 % | 52 % · +3,7 | 77 % · +4,5 | 29 % · +5,2 | 36 % · +2,0 | 26 % · −1,6 |
| tutte e due 50 % | 23 % · −1,0 | 32 % · −1,1 | 9,3 % · +0,4 | 13 % · −0,8 | 2,7 % · −2,3 |

Sui picchi +10, tutte e due 100 %: SUB 34 %, KICK 48 %. Le armoniche del
GROWL (100-500 Hz) cadono dove il NASTRO sporca: a fine corsa il basso
diventa un ringhio fitto. Filippo: va bene, è il gesto estremo (dec. 166 e).

Da fare: netlist LTspice dei due circuiti; rumore dei rami nuovi (todo 234).

## 13. GROWL e NASTRO a bande in MC-5WAY (2026-11-04, todo 233)

Voce **BANDE** in GROWL VER (terza) e in NASTRO VER (settima), stessa
manopola GROWL o NASTRO. Generatore `coefficienti/genera_5way.py`, numeri
da `growl_bande.py` (variante D, `SCELTA`) e `nastro_bande.py` (B8).

- GROWL BANDE: LP4 a 250 Hz (due SVF Butterworth) verso il clipper del
  basso (Rf 47k, 1/3 diodi con 470 ohm, spinta 0 → +20 dB, K 0,9); il
  resto passa da un polo a 2,5 kHz verso il clipper dei medi (Rf 10k,
  3+3 diodi con 4,7k, spinta 0 → +6 dB); un passa-alto a 1 Hz per banda.
  Il selettore dissolve dal LIBERO alle BANDE in 20 ms.
- NASTRO BANDE: 2 poli di enfasi sui bassi (400 Hz, piano 0,2) e 2 sui
  super (5 kHz, 0,5), il NASTRO LIBERO, poi la de-enfasi inversa con
  12 dB in meno sui bassi e 7 sui super.
- I due blocchi si calcolano solo quando il selettore li pesa; spenti,
  i loro stati tornano a zero. Con le altre voci il carico di CPU resta
  quello di prima.
- MC-5WAY-S non cambia (GROWL LIBERO e NASTRO EXCITER fissi): il file
  rigenerato è identico al precedente.

Prova `prova_5way.py`: il codice gen~ tradotto in Python contro il modello
(`fiveway.Saturatori`, che ora ha le due voci): GROWL BANDE a 50, 120, 500
e 1000 Hz, NASTRO BANDE a 50, 500, 3000 e 12 000 Hz, insieme a 50, 120 e
500 Hz, a 0 e +10 dBu, sui due canali: tutti entro 0,05 dB. PASS sull'intera
prova. Le tabelle di §12 restano quelle da riconoscere all'ascolto (todo 235).

## 14. GROWL e NASTRO a bande in LTspice (todo 234)

Domanda di Filippo: «ho paura che la versione analogica distorcerà molto
di più di quella digitale». Risposta: **no**. Lo stesso circuito, scritto
con componenti (diodi 1N4148, JFET NJ310, op-amp), distorce come il
modello che suona in MC-5WAY: scarto massimo 0,03 punti di THD sul GROWL
e 0,9 punti sul NASTRO, livello entro 0,03 dB.

Netlist (2026-11-04, tutti i valori in `.param`: spinte, Rf, R serie,
frequenze; se Filippo cambia le bande, si cambiano lì). Valori verificati:
quelli del 2026-11-04 mattina, GROWL `D` e NASTRO `B8`. Il ritocco chiesto
da Filippo lo stesso giorno (GROWL più sporco su KICK e MID; NASTRO a fine
corsa SUB 0 %, KICK 11 %, MID 45 %, HIGH 34 %, SUPER 22 %) non è in questi
numeri: coi valori nuovi si riscrivono i `.param` e si rilancia lo script.

- `sim/five-way/growl-bande.cir` (dec. 165, variante D): LP4 a 250 Hz
  (due Sallen-Key a guadagno 1, Q 0,707 ciascuna, come le due SVF del
  modello), rest = x − low con un differenziale a 4 R, medi = RC a
  2,5 kHz + buffer, clipper del basso invertente (Rin = 10k/g, Rf 47k,
  1/3 diodi con 470 Ω), clipper dei medi invertente (Rf 10k, 3+3 diodi
  con 4,7k), condensatori d'accoppiamento a 1 Hz davanti a un sommatore
  invertente: d = 0,9·clip_basso − low + 0,50·clip_medi − mid. Polarità
  controllata: i clipper invertono, il sommatore inverte di nuovo, quindi
  d ha il segno del modello (1 diodo sulla semionda positiva d'ingresso).
- `sim/five-way/nastro-bande.cir` (dec. 166, variante B8): enfasi con
  celle passive + buffer (bassi: 40k ∥ 49,7 nF in serie, 10k a massa;
  super: 10k in serie, 10k + 1,59 nF a massa), spinta + JFET del NASTRO
  LIBERO, de-enfasi dei super passiva (1,19k in serie, 10k + 3,18 nF a
  massa), de-enfasi dei bassi non invertente (Rg 10k, Rf 15,1k ∥ 66 nF).
- Copie per frequenza `growl-bande-<f>.cir` e `nastro-bande-<f>.cir`
  (cambia solo `.param f`); varianti con op-amp di libreria
  `*-bande-op-<f>.cir`.
- Confronto: `proto-max/coefficienti/confronto_bande.py` (legge i log,
  fa girare il modello alle stesse condizioni: partenza dal punto di
  lavoro, stessa durata, stessa finestra, 8 armoniche, THD Partial).
  Durate: GROWL 3 s sotto 200 Hz e 0,5 s sopra; NASTRO 1,5 s sotto 1 kHz
  e 0,5 s sopra (le tabelle di §12 per il NASTRO usano 6 s: il
  condensatore di source del JFET, 2200 µF, assesta ancora qualche
  decimo; qui le due parti usano la stessa durata).

### 14.1 Modello contro LTspice (op-amp ideale, rail 16 V)

THD % e livello dB, manopola 50 e 100 %, ingresso −6 / 0 / +10 dBu interni.

GROWL A BANDE (modello | LTspice):

| Via | Manopola | −6 dBu | 0 dBu | +10 dBu |
|---|---|---|---|---|
| SUB 50 Hz | 50 % | 22,5 % +3,7 \| 22,5 % +3,7 | 17,7 % +0,7 \| 17,7 % +0,7 | 10,1 % −2,4 \| 10,1 % −2,4 |
| SUB 50 Hz | 100 % | 31,3 % +8,6 \| 31,3 % +8,6 | 28,4 % +4,2 \| 28,4 % +4,2 | 21,6 % −1,7 \| 21,6 % −1,7 |
| KICK 120 Hz | 50 % | 28,7 % +1,7 \| 28,7 % +1,7 | 23,9 % −0,8 \| 23,9 % −0,8 | 12,8 % −3,2 \| 12,8 % −3,2 |
| KICK 120 Hz | 100 % | 40,1 % +7,0 \| 40,1 % +7,0 | 42,1 % +2,4 \| 42,1 % +2,4 | 32,6 % −4,0 \| 32,6 % −4,0 |
| MID 500 Hz | 50 % | 3,9 % −0,5 \| 3,9 % −0,5 | 7,1 % −0,9 \| 7,1 % −0,9 | 7,0 % −2,5 \| 7,0 % −2,5 |
| MID 500 Hz | 100 % | 20,4 % +4,9 \| 20,4 % +4,9 | 23,2 % +2,0 \| 23,2 % +2,0 | 20,0 % −3,0 \| 20,0 % −3,0 |
| 1 kHz | 100 % | 0,8 % +0,9 \| 0,8 % +0,9 | 6,0 % −0,1 \| 6,0 % −0,1 | 7,2 % −2,7 \| 7,2 % −2,7 |
| HIGH 3 kHz | 100 % | 0,1 % 0,0 \| 0,1 % 0,0 | 2,3 % −0,2 \| 2,3 % −0,2 | 5,4 % −1,3 \| 5,4 % −1,3 |
| SUPER 12 kHz | 100 % | 0 % \| 0 % | 0 % \| 0 % | 0,7 % \| 0,7 % |

Scarto massimo: **0,03 punti di THD, 0,00 dB** (a 12 kHz, +10 dBu).

NASTRO A BANDE (modello | LTspice):

| Via | Manopola | −6 dBu | 0 dBu | +10 dBu |
|---|---|---|---|---|
| SUB 50 Hz | 100 % | 0,8 % +1,4 \| 0,8 % +1,4 | 1,6 % +1,4 \| 1,6 % +1,4 | 6,2 % +1,0 \| 6,2 % +1,0 |
| KICK 120 Hz | 100 % | 1,3 % +5,2 \| 1,3 % +5,2 | 2,8 % +5,1 \| 2,8 % +5,1 | 17,2 % +2,5 \| 17,2 % +2,5 |
| MID 500 Hz | 50 % | 3,1 % +2,3 \| 3,1 % +2,3 | 9,9 % +1,3 \| 9,9 % +1,3 | 9,9 % −1,3 \| 9,9 % −1,3 |
| MID 500 Hz | 100 % | 18,4 % +8,0 \| 18,4 % +8,0 | 28,0 % +5,4 \| 28,0 % +5,4 | 23,3 % −2,4 \| 23,3 % −2,4 |
| HIGH 3 kHz | 100 % | 25,8 % +6,6 \| 25,9 % +6,6 | 29,2 % +4,5 \| 29,2 % +4,5 | 26,9 % −2,9 \| 26,9 % −2,9 |
| SUPER 12 kHz | 50 % | 1,1 % −2,2 \| 1,1 % −2,2 | 2,6 % −2,3 \| 2,6 % −2,3 | 7,4 % −3,0 \| 7,3 % −3,0 |
| SUPER 12 kHz | 100 % | 7,7 % +0,4 \| 7,8 % +0,4 | 23,2 % −0,6 \| 23,4 % −0,6 | 26,0 % −4,3 \| 26,9 % −4,3 |

Scarto massimo: **0,88 punti di THD** (SUPER 12 kHz, 100 %, +10 dBu:
26,0 % contro 26,9 %), **0,03 dB**. Sotto i 3 kHz lo scarto resta entro
0,08 punti. A 12 kHz il JFET vero ha le capacità Cgs e Cgd, che il
modello non ha, e il modello a 192 kHz vede 16 campioni per periodo:
lo scarto è piccolo e va nei due versi.

Tutte le righe a 50 % sono nella stampa dello script; i valori di fine
corsa a 0 dBu coincidono con §12 (GROWL SUB 28 %, KICK 42 %, 1 kHz 6 %;
NASTRO SUB 1,6 %, KICK 2,8 %).

NASTRO con la durata di §12 (6 s, `nastro-bande-500-6s.cir` e
`nastro-bande-3000-6s.cir`, modo `6s` dello script): a fine corsa e
0 dBu MID 30,0 % e HIGH 35,9 % nel modello, 30,0 % e 35,9 % in LTspice
(le tabelle di §12: 30 % e 36 %). Scarto massimo 0,02 punti. Con 0,5-1,5 s
i valori sono più bassi (28 %, 29 %) nelle due parti allo stesso modo:
il condensatore di source del JFET si assesta in qualche secondo.

### 14.2 Op-amp reale (OP1654 di libreria) al posto dell'ideale

`growl-bande-op-120.cir`, `-op-1000.cir`, `-op-12000.cir` (A0 120 dB,
GBW 20 MHz, rail ±16,5 V con alimentazione ±18 V): scarto massimo
0,01 punti di THD e 0,00 dB contro l'op-amp ideale. Il guadagno d'anello
non conta: la distorsione la fanno i diodi, non gli op-amp.
Il NASTRO con OP1654 non termina in LTspice (passo che collassa a
2e-10 s dopo un punto di lavoro trovato con Gmin stepping, a 120, 3000 e
12 000 Hz; fermato a mano): non verificato. I netlist sono in sospeso,
non nel repository. Nel NASTRO gli op-amp lavorano lineari (buffer,
celle RC, sommatore): ci si aspetta lo stesso esito del GROWL, ma è una
deduzione, non una misura.

### 14.3 Rumore del modulo coi rami a bande

`sim/five-way/module-noise-bande.cir`: `module-noise-p2.cir` (banca,
celle, make-up, op-amp con rumore) col drive a bande al posto dei drive
del prototipo: GROWL A BANDE e NASTRO A BANDE come i due netlist sopra,
op-amp OP1654, pot come resistenze, d = w − y1 del NASTRO con un
differenziale a 4 R. Metodo a 16 punti, `sim/mic/noise_total.py`. Uscita
del modulo; target −80 dBu A-wtd (dec. 89):

| Caso | dBu flat | dBu A-wtd | guadagno a 50 Hz / 1 kHz / 8 kHz (silenzio) |
|---|---|---|---|
| Manopole chiuse | −84,4 | **−85,9** | 0 / 0 / 0 dB |
| GROWL BANDE 100 % | −70,3 | **−78,2** | **+32,4** / +1,0 / 0 |
| GROWL BANDE 50 % | −82,4 | −85,5 | +16,9 / −1,0 / −0,1 |
| NASTRO BANDE 100 % | −78,9 | **−79,1** | +1,4 / **+10,2** / +2,8 |
| NASTRO BANDE 50 % | −84,8 | −85,6 | −1,8 / +2,6 / −1,6 |
| GROWL + NASTRO BANDE 100 % | −64,8 | **−71,1** | +33,8 / +11,2 / +2,8 |

Lettura (stesso meccanismo di §11: guadagno a segnale minimo, non rumore
proprio dei rami):
- **GROWL BANDE a fine corsa**: nel silenzio il ramo del basso guadagna
  0,9 × 47k/1k − 1 ≈ 42 volte, +32 dB a 50 Hz (il GROWL LIBERO faceva
  +27). Il rombo basso fra un pezzo e l'altro sale di 5 dB rispetto al
  LIBERO; A-wtd −78,2 contro −79,6, 1,8 dB sopra il target del modulo.
  Il ramo dei medi è a pari livello: a 1 kHz +1 dB.
- **NASTRO BANDE a fine corsa**: +10 dB sui medi come il LIBERO, ma i
  tagli dell'enfasi lo tolgono dai bassi e dai super: −79,1 A-wtd contro
  −75,3 del LIBERO, 0,9 dB sopra il target.
- A metà corsa tutti e due restano entro 0,4 dB dal modulo chiuso.
- Insieme a fine corsa: −71,1 A-wtd (le due LIBERO facevano −69,0).
Per il sistema (target −78, dec. 89; overdrive aperti già accettati come
condizione d'uso, dec. 100) il GROWL BANDE da solo sta al limite. Leva,
se serve: meno spinta massima del basso (+20 dB → +16 dB toglie 4 dB di
rombo) o Rf più bassa, a prezzo di carattere. Decisione di Filippo.

### 14.4 Conto dei pezzi (per lato; il modulo è stereo: ×2)

GROWL A BANDE (sostituisce il GROWL LIBERO: SK, clipper, sommatore):

| Voce | Pezzi |
|---|---|
| Op-amp (sezioni) | 7: 2 Sallen-Key, 1 differenziale, 1 buffer dei medi, 2 clipper, 1 sommatore (+2 già esistenti: buffer del cursore e sommatore di miscela) |
| Diodi 1N4148 | 10 (basso 1 + 3, medi 3 + 3) |
| Resistenze | 22 (SK 4, differenziale 4, RC 1, clipper 4 + 4, sommatore 5) |
| Condensatori | 7: SK 90 n, 45 n, 90 n, 45 n; 6,37 n; accoppiamento 14,3 µF e 8 µF (bipolari o film) |
| Pot | la manopola GROWL comanda 3 tratti per lato: miscela, Rin del basso (10k → 1k, legge esponenziale: +20 dB lineari in dB), Rin dei medi (10k → 5k, +6 dB). Un pot doppio non basta: serve un pot a 3 tratti per lato (6 sul pannello stereo), oppure una legge comune ai due Rin. Da decidere in fase di pannello |

Rispetto al GROWL LIBERO: +4 sezioni di op-amp, +6 diodi, +13 R, +4 C,
+1 tratto di pot per lato.

NASTRO A BANDE (contiene il NASTRO LIBERO):

| Voce | Pezzi |
|---|---|
| Op-amp (sezioni) | 11: 4 buffer dell'enfasi, 2 buffer della de-enfasi alta, 2 non invertenti della de-enfasi bassa, spinta, sommatore del JFET, differenziale d = w − y1 (+2 già esistenti) |
| JFET | 1 (classe NJ310, come il NASTRO LIBERO) |
| Resistenze | 28 (enfasi 8, de-enfasi 8, spinta 2, JFET 4, sommatore 2, differenziale 4) |
| Condensatori | 10: enfasi 49,7 n ×2 e 1,59 n ×2, de-enfasi 3,18 n ×2 e 66 n ×2, 2200 µF di source, 10 µF di drain |
| Pot | come il LIBERO: pot doppio per lato (miscela + spinta) |

Rispetto al NASTRO LIBERO: +9 sezioni di op-amp, +19 R, +8 C. I buffer
dell'enfasi si possono ridurre (celle attive a due a due) se lo spazio
lo chiede: non cambia il suono.

Totale dei due rami: 18 sezioni di op-amp per lato (5 quad), 10 diodi,
1 JFET, 50 R, 17 C; 36 sezioni, 20 diodi, 2 JFET sul modulo stereo.

### 14.5 Da sapere

- **Super del NASTRO BANDE: −14 dB, non −7.** In `Bande.__init__` la
  riduzione dei bassi (12 dB) si divide fra le due celle, quella dei
  super (7 dB) no: ogni cella alta toglie 7 dB. Risposta netta del ramo
  saturato a piccolo segnale: −11,6 dB a 20 Hz, −0,5 dB a 1 kHz,
  −10,6 dB a 12 kHz, −12,5 dB a 20 kHz, −14 dB in fondo. MC-5WAY suona
  questa versione e i netlist la copiano; il testo della dec. 166 dice
  «7 dB in meno sui super». Da chiarire con Filippo quale delle due
  intende (non cambia il confronto).
- Il confronto prova che il netlist è il modello. Le differenze vere fra
  analogico e digitale stanno altrove: dispersione del JFET (Idss, Vto:
  trim o selezione a banco, §5bis.6) e dei diodi, temperatura. Il
  modello usa gli stessi parametri del datasheet: un pezzo diverso
  sposta tutte e due le cose insieme, e si misura sul prototipo.

## 15. Ritocco chiesto da Filippo dopo l'ascolto (2026-11-04, PROPOSTA, non applicata)

Ascolto delle voci BANDE in MC-5WAY. Filippo: GROWL «ok, un poco in più di
distorsione» su KICK e MID (risposta 2: vie del 5-way, sub com'è); NASTRO
«non abbastanza, lo sento bene solo oltre il 50 %»; a fine corsa vuole SUB 0 %,
KICK 11 %, MID 45 %, HIGH 34 %, SUPER 22 % di distorsione, con curva inversa
della manopola. Script di ricerca in `coefficienti/ricerche/` (modello, mix a
0 dBu interni, fine corsa, 192 kHz, 1,5-2 s: numeri indicativi, da rifare a 6 s).

**Curva inversa** (`nastro_curva.py`): u = 1 − (1 − t)², stessa legge per
miscela e spinta. A metà corsa dà quello che oggi dà a ore 2 (MID 21 %, HIGH
27 %); al 25 % MID 7,7 %. Fine corsa invariato. Hardware: pot doppio a curva
inversa (o lineare caricato).

**NASTRO, tetto del JFET** (`nastro_cerca2.py`): la spinta oltre +12 dB non
sporca di più i medi (28 % fra +12 e +20 dB), e anche col ramo tutto sporco
(miscela 1,0) i medi si fermano a ~38 %. Leva che funziona: rinforzare le
armoniche DOPO il JFET con una de-enfasi che sale, tolta prima.

**NASTRO, candidato** (`nastro_tilt.py`): taglio dei bassi 3 celle zero 30 /
polo 140 Hz; inclinazione dei medi polo 1 kHz / zero 3 kHz prima del JFET e
inversa dopo (nuova); taglio dei super 1 cella polo 9 kHz / zero 10,8 kHz.
Fine corsa: SUB 0,8 %, KICK ~12 %, MID 45,4 %, HIGH 34,3 %, SUPER 21,3 %.
Da sistemare: il volume sale di +4…+7 dB a fine corsa (va ritarata la
de-enfasi: rl, rh, guadagno del ramo); SUB 0,8 % invece di 0 (zero più basso).

**GROWL** (`growl_cerca.py`, variante D di partenza: SUB 28, KICK 42, MID 23):
- spinta dei medi +6 → +12 dB: MID 25 % appena (la 4,7k in serie li tiene morbidi);
- 4,7k → 1k in serie ai diodi dei medi: KICK 44, MID 25 (+2 / +2);
- 470 → 150 ohm in serie ai diodi del basso: KICK 54-55 %, ma SUB 34-35 %
  (sale anche il sub) e il kick sui picchi +10 a 57 %, −7 dB;
- spinta del basso +23 dB con 470 ohm: SUB 26, KICK 40, MID 26-27;
- Rf dei medi 22k-47k: MID 26-28 %, KICK scende a 33-39 %.
Nessuna leva semplice alza KICK e MID lasciando il SUB fermo: KICK e SUB
passano dallo stesso clipper. Strada da provare: un'enfasi 50 → 120 Hz nel
ramo del basso (come per il NASTRO), oppure il kick in parte nel ramo dei medi.

Da fare (sessione dopo): scegliere il GROWL; ritarare il volume del NASTRO;
portare i due in growl_bande/nastro_bande come varianti nuove, poi in MC-5WAY
(con la curva inversa), prova_5way, netlist LTspice di §14 coi .param nuovi.

## 16. NASTRO a bande B9 in MC-5WAY (2026-11-04, todo 245)

Il candidato del par. 15 diventa la variante **B9** di `coefficienti/nastro_bande.py`
(`SCELTA = "B9"`) e la voce BANDE di NASTRO VER in MC-5WAY. B8 resta nel modello come
riferimento. Ricerca del volume: `coefficienti/ricerche/nastro_b9.py`.

Circuito (modello): taglio dei bassi 3 celle zero 30 / polo 140 Hz; taglio dei super
1 cella polo 9 kHz / zero 10,8 kHz; **inclinazione dei medi** polo 1 kHz / zero 3 kHz
prima del JFET e inversa esatta dopo; de-enfasi ridotta di 12 dB sui bassi e 5 dB sui
super; **guadagno del ramo −3,5 dB** dopo la de-enfasi (in hardware: la resistenza del
sommatore). Manopola a **curva inversa**: rotazione u = 1 − (1 − t)², spinta 0 → +12 dB
e miscela con la legge di oggi calcolate su u. A metà corsa la manopola vale u = 0,75.
Le altre voci di NASTRO VER restano a curva lineare.

Volume. Ridurre la de-enfasi abbassa anche la distorsione (MID 45 → 39 %, HIGH 34 → 27 %
con 5 dB in meno sull'inclinazione): scartato. Il guadagno del ramo abbassa il volume e
lascia la distorsione del ramo com'è. Senza: +4,2…+7,7 dB a fine corsa; con −3,5 dB e
rh 5: +1,4…+4,3 dB.

Tabella (modello, 192 kHz, 6 s; numeri di Filippo a fine corsa: SUB 0, KICK 11, MID 45,
HIGH 34, SUPER 22 %):

| Mix 0 dBu, manopola | SUB 50 Hz | KICK 120 Hz | MID 500 Hz | HIGH 3 kHz | SUPER 12 kHz |
|---|---|---|---|---|---|
| 25 % | 0,12 % · −1,4 | 1,2 % · −0,1 | 12 % · −0,6 | 4,8 % · 0,0 | 1,9 % · −0,8 |
| 50 % | 0,43 % · +0,1 | 4,9 % · +2,0 | 32 % · +0,3 | 20 % · +1,6 | 8,7 % · +0,5 |
| 75 % | 0,71 % · +2,3 | 9,9 % · +3,7 | 43 % · +1,1 | 33 % · +3,1 | 18 % · +1,8 |
| 100 % | 0,81 % · +3,1 | 12 % · +4,3 | 46 % · +1,4 | 37 % · +3,7 | 22 % · +2,3 |

| Fine corsa | SUB | KICK | MID | HIGH | SUPER |
|---|---|---|---|---|---|
| nominale −6 | 0,40 % · +3,2 | 3,3 % · +6,0 | 36 % · +4,5 | 15 % · +5,9 | 6,2 % · +3,9 |
| picchi +10 | 3,5 % · +2,6 | 18 % · −1,2 | 42 % · −5,9 | 37 % · −2,7 | 32 % · −2,9 |

Lettura: a metà corsa i medi sono già al 32 % (B8 lineare: 10 %): «lo sento solo oltre
il 50 %» è risolto. SUB 0,8 % invece di 0: sotto l'1 %, non udibile come sporco. Sui picchi
+10 i medi si schiacciano di 5,9 dB (B8: −2,6): è il prezzo del 45 % sui medi.

Da fare: LTspice della B9 (netlist nuova, `sim/five-way/`), rumore del ramo, ascolto di
Filippo. `sim/five-way/confronto_bande.py` legge `SCELTA`: con B9 non confronta più le
netlist della B8.

Stato LTspice della B9 (2026-11-04 sera, fermato per la quota): `nastro-b9-500.cir`
non termina. Prove `t9a-d.cir` (dur 0,05 s): con la spinta a op-amp (`OPAMP0` con
`limit`, Rg 1k) il passo collassa a ~5e-11 s (t9a, 18 min); con la spinta come sorgente
`B` limitata (t9b-d) finisce in 1 min. Causa: lo stadio di spinta, non l'inclinazione
(t9d) né il differenziale (t9c). Prossimo passo: spinta come `B` (o macro lineare con
secondo polo) in tutte le `nastro-b9-*.cir`, poi `confronto_b9.py`, rumore
(`module-noise-b9.cir`), ascolto di Filippo. Verificato in: Python sì / LTspice no / Live no.

LTspice della B9 (2026-11-04 notte). Spinta come sorgente `B` con clip ai rail (come B8):
lo stadio a op-amp senza polo faceva collassare il passo (t9a-d, ora tolte). Macro
`OPAMP0` delle netlist B9: A0 1e5, polo a 100 Hz (GBW 10 MHz), clip anche sul nodo
interno. Attenzione: con il condensatore della macro sbagliato di 1000 volte (GBW 10 kHz)
le celle di enfasi perdevano 1,2 dB a 3 kHz e la THD a 3 kHz scendeva da 32 a 7 % (falso).

| Mix, manopola | modello THD · dB | LTspice Partial · dB |
|---|---|---|
| 50 Hz 0 dBu 100 % | 0,81 % · +3,14 | 0,81 % · +3,14 |
| 120 Hz 0 dBu 100 % | 11,52 % · +4,45 | 11,53 % · +4,45 |
| 500 Hz 0 dBu 50 % | 30,18 % · +0,97 | 30,20 % · +0,97 |
| 500 Hz 0 dBu 100 % | 43,95 % · +2,04 | 43,97 % · +2,04 |
| 500 Hz +10 dBu 100 % | 41,78 % · −5,69 | 41,77 % · −5,69 |

Scarto massimo a 50, 120 e 500 Hz: 0,05 punti, 0,00 dB (`confronto_b9.py`, durata 1,5 s).
A 3 e 12 kHz LTspice non termina (oltre 40 min per passo, anche con GBW 1 MHz e 0,1 s):
causa aperta, non è lo stadio di spinta.

Rumore (`module-noise-b9.cir`, `noise_total.py`): NASTRO B9 a fine corsa −79,8 dBu A
(B8: −79,1; target −80), a metà manopola −83,3, tutto chiuso −85,9.

Verificato in: Python sì / LTspice sì sotto 1 kHz, no a 3 e 12 kHz / Live no (da sentire).

## 17. Curve delle manopole GROWL e NASTRO (2026-11-05, richiesta di Filippo)

Filippo: «sulla curva del growl vorrei che salisse un po più lenta, quella del nastro un po più
veloce». Fine corsa invariati: cambia solo come si arriva al 100 %.

| Manopola | 25 % | 50 % | 75 % | Formula |
|---|---|---|---|---|
| GROWL prima (lineare) | 25 % | 50 % | 75 % | mg = t |
| GROWL ora | 12,5 % | 35 % | 65 % | mg = t^1,5 (`fiveway.GROWL_ESP`) |
| NASTRO B9 prima | 44 % | 75 % | 94 % | 1 − (1 − t)^2 |
| NASTRO B9 ora | 51 % | 82 % | 97 % | 1 − (1 − t)^2,5 (`nastro_bande.INV_ESP`) |

La curva del GROWL vale per le tre voci di GROWL VER (DEC.99, LIBERO, BANDE) e per MC-5WAY-S.
Hardware: GROWL = pot doppio a curva logaritmica, NASTRO = pot a curva logaritmica inversa
(taper C). La riga «500 Hz 0 dBu 50 %» del par. 16 ora corrisponde alla manopola al 42 %.

Le tabelle del par. 16 a 25 / 50 / 75 % sono calcolate con la curva vecchia (^2).

## 18. NASTRO B9 in LTspice a tutte le frequenze (2026-11-05, todo 256)

Causa del blocco a 3 e 12 kHz: il passo di LTspice collassava a t ~1,6 ns, subito dopo il
punto di lavoro (migliaia di «tolerance relaxed»), poi ogni giro durava ~40 min. Rimedio:
`.options cshunt=1e-15` (1 fF da ogni nodo a massa) in tutti i `nastro-b9*.cir`. Provati
anche `method=gear` e la macro senza anti-windup: non bastano. 1 fF accanto ai 0,159 pF della
macro OPAMP0 non sposta il polo. Tempi: 15-67 s per frequenza, 287 s il 3 kHz da 6 s.
I netlist usano ora la curva nuova u = 1 − (1 − th)^2,5 (par. 17): le righe a 50 % sono a u = 0,82.

`confronto_b9.py` (modello contro LTspice, THD Partial e livello, 0 / +10 dBu):

| Frequenza | 50 %, 0 dBu | 100 %, 0 dBu | 100 %, +10 dBu |
|---|---|---|---|
| 50 Hz | 0,53 % · +0,84 / 0,53 % | 0,81 % · +3,14 / 0,81 % | 3,46 / 3,47 % |
| 120 Hz | 6,58 / 6,58 % | 11,52 / 11,53 % | 16,50 / 16,55 % |
| 500 Hz | 34,20 / 34,22 % | 43,95 / 43,98 % | 41,78 / 41,77 % |
| 3 kHz | 22,58 / 22,62 % | 32,49 % · +6,54 / 32,56 % · +6,54 | 32,95 / 33,03 % |
| 12 kHz | 11,11 / 11,21 % | 19,73 / 19,80 % | 27,91 % · +2,07 / 27,97 % · +1,87 |

Scarto massimo: 0,09 punti di THD e 0,20 dB di livello (12 kHz). Durata 6 s (500 e 3000 Hz):
0,02 punti, 0,00 dB.

Verificato in: Python sì / LTspice sì a 50, 120, 500, 3k, 12k Hz / Live no (da sentire, todo 255).

## 19. Kill tagliato allo zero della via in MC-5WAY (2026-11-05, todo 226, dec. 164)

Come l'hardware (five-way §8.11): per via e per lato la levetta passa all'interruttore al
primo passaggio per lo zero della via (cambio di segno fra due sotto-campioni a 4×), o dopo
20 ms (`fw.KILL_ZC_TMAX`). L e R tagliano ciascuno al proprio zero. Vale anche per MC-5WAY-S.
Stato in `Data zk` (gen~) e in `fw.Banca` (modello).

Prova nuova in `prova_5way.py` (seno 0 dBu, kill a 102,1 ms): il salto più grande dopo il gesto
diviso il passo normale del seno. Modello, stesso gesto, allo zero contro secco:

| Via | Allo zero | Secco | Ritardo del gesto |
|---|---|---|---|
| SUB 40 Hz | 1,00 | 699 | 5,0 ms |
| KICK 120 Hz | 1,00 | 106 | 0,8 ms |
| MID 500 Hz | 1,00 | 47 | 0,6 ms |

Il ritardo dipende dalla fase al momento del gesto: al massimo mezzo periodo della via.

Verificato in: Python sì (prova_5way PASS, prova_semplice PASS) / LTspice sì per il circuito
(`kill-zc.cir`, §8.11) / Live no (da sentire sul KICK con musica vera).

## 20. Varianti F e H del CROSSOVER (2026-11-06, B3, richiesta di Filippo)

Filippo vuole una via KICK più larga, per un kill KICK più profondo. Il
pannello del 5-way non cambia: kill a levetta per via, 5 GAIN sulle celle EQ.
Nel selettore CROSSOVER di MC-5WAY, dopo E:

| Variante | SUB/KICK | KICK/MID | MID/HIGH | HIGH/SUPER | Via KICK |
|---|---|---|---|---|---|
| E | 80 | 170 | 1200 | 6000 | 1,1 ottave |
| F | 70 | 220 | 1200 | 8000 | 1,7 ottave |
| H | 60 | 250 | 1200 | 8000 | 2,1 ottave |

SUPER a 8 kHz in F e H: verso la quinta via dell'impianto (8-12 kHz, docs/10).
MC-5WAY-S resta su E.

**Kill a confronto** (`sim/five-way/kill_casse.py` e `kill_larghezza.py`, Python puro, LR4, banca risommata; cassa
= VENU360 LR4 37/80/170/1100, rumore rosa; non LTspice, non ascoltato):

| Variante | KICK al centro (mix) | cassa SUB (kill SUB) | cassa KICK (kill KICK) | cassa MID (kill MID) | cassa HIGH (kill HIGH) |
|---|---|---|---|---|---|
| E | −9,6 dB | −10,2 | −6,4 | −12,6 | −4,2 |
| F | −15,1 | −8,1 | −9,9 | −10,0 | −5,6 |
| H | −19,5 | −6,1 | −12,9 | −8,7 | −5,5 |

Lettura: allargare la via KICK scava il kill KICK e indebolisce i kill di SUB
e MID. Con la banca risommata nessuna larghezza dà −∞ (40-400 Hz: −34 al
centro, −23 sulla cassa). Il −∞ sulla cassa viene solo da un'uscita per via
(Deep Field, docs/07 §6; dec. 111). La cassa HIGH riceve HIGH e SUPER: il kill
HIGH da solo la abbassa di 4-6 dB.

Da sentire in Live: kill KICK, SUB e MID con musica vera in E, F e H.

## 21. Ascolto con la guida (2026-11-10, dec. 175)

Guida: `proto-max/ascolti-5way.pdf`. Risposte di Filippo: incroci **H**; kill allo zero
pulito; GROWL **BANDE** senza ritocchi, curva più lenta con metà corsa al 30 %
(`fiveway.GROWL_ESP` 1,5 → 1,74, vale per tutte le voci di GROWL VER e per MC-5WAY-S);
NASTRO **BANDE** B9 con la curva di oggi; medi schiacciati sui picchi: ok.

MC-5WAY e MC-5WAY-S rigenerati col nuovo esponente. MC-5WAY-S resta su E, LIBERO, EXCITER. [Superato il 2026-11-12: §22.]

## 22. MC-5WAY-S con le scelte della dec. 175; GROWL VER fino a BANDE (2026-11-12)

Richiesta di Filippo (banco nel browser, `web/`): le versioni -S con le ultime scelte.

**MC-5WAY-S** ora fissa CROSSOVER H 60/250/1,2k/8k, GROWL BANDE e NASTRO BANDE B9
(`genera_5way.py`, `SCELTA_XO` 6, `SCELTA_GV` 2, `SCELTA_NV` 6). Calcola solo quei blocchi:
il clipper del GROWL LIBERO e i sei NASTRO vecchi non si scrivono. Con la manopola a zero
(sotto 0,001) GROWL BANDE e NASTRO BANDE non si calcolano e i loro stati vanno a zero, come
già fa MC-5WAY con le voci non scelte. `prova_semplice.py`: MC-5WAY-S contro MC-5WAY con
xo 6, gv 2, nver 6, scarto massimo 3e-15, PASS. Peso nel modello JavaScript del banco
(`web/tools/prova.mjs`, un core M3 Max): 13 % del tempo reale con GROWL e NASTRO a zero,
31 % col solo GROWL a metà, 52 % col solo NASTRO, 70 % con tutti e due (il completo con le
stesse scelte: 130 %).

**GROWL VER fino a BANDE.** In MC-5WAY il `Param gv` aveva `max=1`, ma il selettore GROWL VER
di Max manda 0, 1 o 2 (BANDE). Se gen~ taglia un `Param` al suo massimo, in Live BANDE suonava
come LIBERO: la scelta GROWL BANDE della dec. 175 (c) sarebbe stata fatta sentendo il LIBERO.
Non ho trovato nella documentazione di Cycling '74 se il `Param` di un codebox taglia o no:
**deduzione, da verificare in Live** (selettore su BANDE, GROWL al massimo: se il suono non
cambia fra LIBERO e BANDE, il taglio c'era). Le prove in Python non se ne accorgevano: il
traduttore non applica i massimi (regola 11 del CLAUDE.md). Correzione: `max` = numero di voci
meno 1 (`genera_5way.py`); MC-5WAY rigenerato.

Verificato in: Python sì / LTspice no / Live no.
