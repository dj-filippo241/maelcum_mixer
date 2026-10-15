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
  dec. 99), pot lineari.
- **CROSSOVER** A / B / C / D, solo prototipo, per B3 (sotto).
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
