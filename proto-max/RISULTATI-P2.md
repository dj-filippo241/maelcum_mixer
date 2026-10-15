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
  taper A × 0,85; selettori GROWL VER (DEC.99 / LIBERO) e NASTRO VER
  (OGGI / COMPLETO / EXCITER / CLASSE A).
- **CROSSOVER** A-E, solo prototipo, per B3 (§1; E aggiunta in §6).
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
