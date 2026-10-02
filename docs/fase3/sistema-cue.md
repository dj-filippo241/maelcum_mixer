# Sistema CUE / cuffie — S5 (voce q18)

**v0.1 — 2026-10-02.** Ultimo workstream del piano fase 3
(`00-piano-sistema.md`). Chiude il design di sistema: dopo questo doc il
design elettrico del mixer è COMPLETO e si può proporre la ripresa del
prototipo M4L (dec. 78). Simulazioni: `sim/system/cue-*.cir`, risultati
in `sim/system/RISULTATI-cue.md`. Requisiti: SPECIFICA §10 [BLOCCATO],
decisioni 90(b), 93, 94(b); interfacce backplane: `sistema-backplane.md`
v0.2 §3-§5.

## 1. Requisiti e vincoli ereditati (non ridiscussi)

- CUE solo sui 4 canali DJ, punto locked post-EQ / pre-filter / pre-fader
  (cdj §3.4: buffer dedicato → switch di canale → CUE bus). Più cue
  attivi sommati; niente cue su FX/mic/generic; niente meter cuffia.
- Blend CUE↔Master: CCW = cue, centro = 50/50, CW = master; stesso mix su
  entrambe le uscite; level condiviso; 2 uscite cuffia in parallelo;
  split cue NON incluso (voce 40).
- Ampli cuffia dedicato high-current, ~1 Vrms su 32-250 Ω, alimentazione
  e ground isolati (regolazione LOCALE nel modulo, come tutti i moduli).
- Rumore di sistema ≤ −78 dBu A-wtd (dec. 89) da non erodere: il percorso
  cue non alimenta il master (isolato by construction); target proprio
  del percorso cuffia ≤ −90 dBu A-wtd al jack.
- Standard elettrico I/O: single-ended 0 dBu tra moduli (dec. 94a);
  ricevitore cue sum = iniezione 10k su massa virtuale, ricevitore MON =
  buffer ≥ 100k (S3 §4); driver di modulo ≤ 50 Ω.
- GLOBAL_MUTE (linea c9): **il CUE NON lo ascolta** (scelta di Filippo
  2026-10-02, chiude la materia aperta da dec. 94b): la cuffia resta viva
  durante power-on/off e guasti rail del master. La protezione dai
  transienti PROPRI del modulo cue è locale (§6).

## 2. Diagramma a blocchi del modulo

```
(dal backplane, slot CUE: 4× cue in L/R + MON in L/R + riga a/c)
  CUE1-4 L/R ──► [A] CUE SUMMING L/R (massa virtuale, Rf 10k, −1)
                        │
  MON in L/R ──► [B] MON BUFFER L/R (follower direct, +1)
                        │
            [C] BLEND CUE↔MASTER (pot doppio 10k lin, centro = 50/50)
                        │
            [D] LEVEL (pot doppio 10k log, CCW = silenzio)
                        │
            [E] AMPLI CUFFIA L/R (OP1612 + diamond, gain +1, ±18 locali)
                        │
            [F] USCITE: Rser 10 Ω ×4 → relay DPDT ×2 → 2 jack stereo
                        │
  raw ±22 → ±16,5 → LT3045/94 → ±15,0 LN  ([A][B][C][D] + riferimenti)
  raw ±27 → LM317/337 → ±18 audio locali  ([E])
  +5 V → [G] CONTROLLO LOCALE (timer + supervisore ±22 → relay [F])
```

Ogni blocco stereo con sezioni separate L/R; nessun buffer condiviso tra
destinazioni (regola della casa, master-out §2).

## 3. [A] CUE SUMMING

Summer invertente a massa virtuale: 4 ingressi × 10k (resistenze di
iniezione lato sorgente, nel modulo CDJ, convenzione multidrop S3 §4) +
Rf 10k → guadagno −1 per cue attivo, nominale 0 dBu ciascuno. Somma di 4
cue a nominale = +12 dBu (3,1 V): dentro i ±15 V LN (capability ~+20 dBu,
sheet §1); picchi oltre = disciplina operatore, come il summing master.
L'ingresso a massa virtuale isola i contributori: uno switch aperto
(lato CDJ, π SPDT classe ADG1434, off-isolation −95 dB @20 kHz) rimuove
il canale dal net senza interagire con gli altri. OP1612 dual (1 chip
L/R), rail ±15 LN. Polarità: −1 (vedi §7).

## 4. [B] MON BUFFER — presa dal master (DECISIONE di Filippo 2026-10-02)

Tap nel modulo master: **post-summing [A2], pre-master-level [D]** —
stesso nodo di programma di REC e BOOTH, buffer dedicato nuovo **[N]**
(adderendum in `master-out.md`). Comportamento stile DJM-900NXS2
(verificato sui manuali: il master cue Pioneer è pre master level; lo
Xone:92 invece monitora il bus LR MIX post-master): il blend non segue
la manopola master, che nel dub è un gesto performativo; il programma
vero si ascolta dal booth. Conseguenza accettata: master a zero ≠
silenzio in cuffia sul lato master del blend.

Buffer [N] nel master: OP1612 unity NON invertente, uscita ≤ 50 Ω verso
lo slot 8 del backplane. Nel modulo cue il ricevitore MON è un **follower
direct** (senza resistenza serie): una 100k in serie inietterebbe
40,7 nV/√Hz; il requisito S3 «≥ 100k sul net» è soddisfatto
dall'impedenza d'ingresso del follower (correnti di bias in pA), e il
ritorno DC è garantito dal driver d'uscita [N] del master. Polarità: +1
(vedi §7). Rail ±15 LN.

## 5. [C][D][E][F] Blend, level, ampli cuffia, uscite

**Blend [C]**: pot doppio gang 10k LINEARE, estremi pilotati da sorgenti
a bassa Z (uscite di [A] e [B]): law lineare in tensione ESATTA
(RISULTATI-cue Test 2). Isolamento agli estremi CHIUSO ANALITICO
2026-10-02 (banco = conferma): Zo closed-loop OP1612 a 20 kHz =
Zo_ol/(1+T) ≈ 60 Ω/4000 ≈ 15 mΩ (Zo_ol ≈ 60 Ω assunto per la famiglia
bipolare TI, T = GBW/f = 4000) → leak = 15 mΩ/10 k = **−116 dB**; il
−138 dB della sim (macro Zo = 0) è il limite inferiore. Centro =
50/50 con −6 dB per parte [BLOCCATO confermato in sim]; detent centrale
sul pot = hardware, voce 40. A centro, carico visto da ciascuna sorgente ≈ 10k:
trascurabile per OP1612.

**Level [D]**: pot doppio gang 10k LOGARITMICO, CCW = wiper a massa =
silenzio vero (−∞). Wiper → ingresso non invertente di [E]; ritorno DC
del bias (2 pA) attraverso la pista: nessun pop.

**Ampli cuffia [E]**: gain **+1 CHIUSO PER CALCOLO** 2026-10-02 (banco =
sanity): a level max il jack arriva al limitatore (4,5 Vp su 32 Ω =
3,4 Vrms = 361 mW = +25,6 dBm; su 250 Ω 5,45 Vrms = +20,7 dBm): anche
con cuffia poco sensibile (84 dB SPL/mW) sono 110/105 dB SPL, abbondanti
per la scena; +2 dB sarebbe solo headroom di manopola. OP1612 in guadagno +1 (feedback preso su OUTA,
pre-Rserie) + diamond class-AB MJE340/350; bias = Vbe-multiplier con
trimmer [PROVV] (idle ~20 mA) e stringa pilotata da CCS JFET Idss ~8 mA
(lezione sim: col resistore al rail la stringa muore a uscita alta);
Re 4,7 Ω doppi per ramo (stabilità termica E senso corrente); limitatori
Vbe sui Re a ~140 mA (corto franco al jack = clamp, dissipazione MJE a
corto sostenuto 2,1 W → TO-126 su rame ≥ 4 cm², abuso prolungato =
dominio termico come master-out v0.3). Rail **±18 V audio locali**
(LM317/337 dal raw ±27 + bulk 1000 µF/100 nF): lo stadio di potenza
cuffia NON sta sul rail LN — i picchi di corrente del carico (fino a
170 mA per ramo in programma, 340 mA in doppio corto) non devono
modulare il rail ultra-low-noise; i blocchi di segnale [A]-[D] restano
su ±15,0 LN. «Alimentazione isolata» [BLOCCATO SPEC §10] = regolazione
locale dedicata, soddisfatta. **STATO BIAS/LIMITATORI: APERTO**
(REV 2026-10-02 sera): col pinout BJT corretto (C-B-E — la prima
stesura dei netlist aveva il multiplier C-E-B = spento, idle parassita
~150 mA che mascherava il crossover) il Test 1 rigenerato dà THD
4,8-13,5 % @1 Vrms, guadagno anomalo 1,53 su 250 Ω a basso livello e
limitatori che non limitano (462 mA a 16 Ω): la rete bias+limitatori va
ridisegnata e riverificata (task sistema-cue-banco, prossima sessione;
dettagli e dati in `sim/system/RISULTATI-cue.md` Test 1 REV). Livello,
partitore Rserie e rumore (Test 4) NON dipendono dal bias e restano
validi.

**Uscite [F]**: per canale, l'uscita ampli si sdoppia su 2 jack stereo
con Rserie 10 Ω 2 W per ramo-jack (8 resistenze nel modulo): la Rserie
isola i due jack (un carico non modula l'altro), garantisce stabilità su
carico capacitivo (feedback pre-Rserie) e limita il corto insieme al
limitatore. Zout al jack = 10 Ω: damping factor 3,2 su 32 Ω — colore
della cuffia legato alla sua curva d'impedenza, accettato e documentato
(standard degli ampli cuffia con protezione serie); su 250 Ω l'effetto
è −0,34 dB. Level/max: 0,762 Vrms su 32 Ω con sorgente a nominale =
requisito «~1 Vrms» raggiunto con level ~90 % [PROVV: gain +2 dB se a
banco risulta corto]. Relay DPDT ×2 (uno per jack, contatti L+R) tra
Rserie e connettore, comandati da [G]; normalmente diseccitati = cuffia
muta = stato sicuro.

## 6. [G] Protezione locale (il CUE non ascolta c9)

Scelta di Filippo: durante GLOBAL_MUTE la cuffia RESTA viva (il mute
globale scatta solo a power-on/off e su guasto rail del master; tenere
la cuffia indipendente permette di continuare a cueare durante un
guasto master). Restano da togliere i transienti PROPRI del modulo cue:

- Power-on: supervisore a finestre sui raw locali (±22 < 17 V e ±27 < 20 V,
  stesso stile S1 §4/master §3.7) + timer RC 1,5-2 s → relay [F] si
  eccitano solo a rail stabili: il bang d'accensione non arriva mai ai
  jack.
- Power-off: hold-up sui bulk locali (~50-100 ms) + comparatore: al calo
  dei raw i relay aprono in < 10 ms, il pop di spegnimento resta dentro.
- Guasto rail cue: stessa finestra → relay aperti: cuffia muta (il suo
  amplificatore non ha più rail puliti), master indipendente.

Tutto analogico, niente MCU (coerenza col progetto). Consumo +5 V: 2
relay DPDT eccitati in normale esercizio ≈ 56 mA + controller ~2 mA
(budget +5 V dec. 93: worst 1,0 A → 1,06 A, dentro il dimensionamento
1,25 A). **Spec relay per classe** (parte concreta alla reperibilità
post-M4L, congelata): bobina 5 V, DPDT, contatti ≥ 2 A, bobina ≤ 30 mA,
contatti dorati; famiglia esempi Omron G6K-2 / Panasonic TQ2 / Fujitsu
JS2. **Click relay CHIUSO ANALITICO**: a power-on i relay chiudono a
timer scaduto con ampli stabile — alla chiusura il solo gradino è l'offset
DC (Vos × gain ≈ 1 mV in cuffia = 31 µW su 32 Ω: inudibile); a power-off
aprono in <10 ms con programma forse presente: bounce sotto segnale =
tick udibile allo spegnimento, stesso carattere di master-out §3.7
(pattern casa accettato); se a banco desse fastidio: sequenza locale
«muta il blend 10 ms prima dei relay» (una cella RC in più sul
controller).

## 7. Polarità e fase tra i due percorsi del blend

Polarità relativa VERIFICATA in sim (RISULTATI-cue Test 3): cue summer
−1 e MON buffer +1 (con [A2] del master che inverte a monte) fanno
SOMMARE le due componenti al centro del blend quando lo stesso programma
è presente su entrambi i lati (0 dB, nessuna cancellazione); un anello
invertito per errore cancellerebbe a −104 dB.

Fase: l'idea allpass phase-matching (handoff 02/10, identità A2 di
five-way §8.2) è valutata e CHIUSA NEGATIVA: il percorso master
attraversa la banca 5-way (prodotto di 4 allpass A2: ritardi di gruppo
~64 µs a 3,5 kHz fino a ~2,5 ms a 90 Hz), il percorso cue no.
Compensare significherebbe replicare 4 sezioni A2 × 2 op-amp × 2 canali =
16 op-amp nel modulo cue per il solo caso «cue di un canale già in
programma al centro del blend» — costo sproporzionato a un caso d'uso
marginale (il cue serve per materiale NON in programma; al centro si
staziona poco). Resta documentato: al centro, cue di un canale vivo =
comb filtering udibile sulle bande dove il ritardo 5-way dà sfasamento
180°; comportamento inherente ai crossfade cue/master di tutti i mixer
(confronto DJM/Xone: stesso carattere).

## 8. Rail, correnti, backplane

| Rail locale | Da | Per | Corrente (idle / picco) |
|---|---|---|---|
| ±15,0 LN | pre-reg ±16,5 + LT3045/94 dal raw ±22 | [A][B][C][D], riferimenti | ~23 / 25 mA |
| ±18 audio | LM317/337 dal raw ±27 + bulk locale | [E] | ~15 / 170 mA programma (pavimento ~10 mA col bias corretto); corto DA RIVERIFICARE dopo il redesign bias (il clamp misurato NON interviene: 462 mA) |
| +5 V | bus backplane (regolato in PSU, dec. 93) | [G] relay + controller | ~58 / 60 mA |

La riga correnti CUE di `sistema-backplane.md` §6 ([PROVV fino a S5]:
±50/±110 su ±27, ±30/±90 su ±22) è REVISIONATA con questi numeri
(§6 REV in quel doc). Pinout slot CUE invariato (S3 §3: 4 cue in + MON in
slot 5 + riga a/c comuni); il modulo cue ascolta c9? NO (dec. Filippo):
la riga c9 resta connessa ma inascoltata per scelta — segnato sul doc
backplane §5 per chi legge.

## 9. Rumore e crosstalk

- Rumore al jack (level max, blend centro, 1 cue attivo): 8,50 nV/√Hz
  piatto → **−114,8 dBu A-wtd** vs target −90: PASS 24,8 dB; in cuffia
  32 Ω/100 dB/mW ≈ −2 dB SPL (RISULTATI-cue Test 4).
- Crosstalk cue→cue: massa virtuale + switch aperti lato CDJ (−95 dB
  @20 kHz classe ADG1434): by construction.
- Crosstalk MON→cue agli estremi del blend: −116 dB stimati (Test 2).
- L→R: ampli separati; jack→jack: stesso segnale by design (uscite
  parallele [BLOCCATO]), interazione solo via Rserie in corto franco
  (accettato: guasto, non uso).

## 10. BOM di massima [molto PROVVISORIA — regola 3]

3× OPA1612 (summer L/R, MON L/R, ampli L/R) · 4× MJE340 + 4× MJE350 ·
4× JFET CRD Idss ~8 mA (o LM334 trimmati) · 2× LT3045 + 2× LT3094 ·
2× LM317 + 2× LM337 · 2× relay DPDT 5 V · pot doppio 10k lin con detent
centrale ×1 + pot doppio 10k log ×1 (voce 40) · 8× R 10 Ω 2 W · 4× R 4,7 Ω
· 2× jack stereo (voce 40) · trimmer multiplier ×2 · bulk/bypass locali.
Nel modulo master: +1 OPA1612 per il buffer [N] MON.

## 11. Simulazioni eseguite (2026-10-02)

`sim/system/cue-hp-load.cir` (Test 1: carichi 16/25,8/32/250/corto ×
1 Vrms/12 Vp: THD, clamp, headroom) · `cue-blend.cir` (Test 2: law e
isolamento, due toni) · `cue-blend-pol.cir` (Test 3: polarità al centro)
· `cue-chain-noise.cir` (Test 4: rumore, metodo densità a 12 punti).
Risultati e lezioni di metodo in `sim/system/RISULTATI-cue.md`.

## 12. Aperti (non bloccano il design)

- **Rete bias+limitatori dell'ampli cuffia da ridisegnare** (Test 1 REV
  02/10 sera: THD 5-13 % @1 Vrms, clamp assente, guadagno anomalo su
  250 Ω): primo item della prossima sessione; trimmer, idle e corso di
  regolazione si definiscono DOPO il redesign (i vecchi numeri «idle
  ~20 mA» erano teorici, mai verificati).
- Relay: parte concreta dentro la spec per classe qui sopra, alla
  reperibilità post-M4L (congelata).
- Jack/posizione/detent/level range: sessione hardware (voce 40, Filippo).
- Conferme a banco residue (sanity, non decisioni): gain +1 con cuffie
  reali, isolamento blend a 20 kHz col chip reale (stima −116 dB),
  eventuale tick di power-off.
