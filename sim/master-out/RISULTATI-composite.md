# MASTER OUT — risultati simulazioni stadio composito (2026-09-18)

Riferimento design: `docs/fase1/master-out.md` §3.3, coda simulazioni §6.2.
Strumento: LTspice 26.0.2 via `sim/run_ltspice.sh` (batch CLI).

## Stato dei modelli — tutto [PROVVISORIO] (regola 3)

- **OPA1612**: macromodello a 2 poli tarato su datasheet (GBW 80 MHz, A0 120 dB,
  secondo polo 40 MHz, clamp uscita ±16,5 V = swing reale su rail ±18 V).
  Rumore e distorsione interna NON modellati. Da sostituire col modello ufficiale TI.
- **MJE340/MJE350**: modelli rappresentativi TO-126 (parametri tipici, non produttore).
- Stadio: push-pull class AB, moltiplicatore Vbe (Ra 2,2k / Rb 1k), Re 33 Ω,
  idle ~12 mA, feedback globale unity dall'uscita.
- Escluse da questo primo passaggio: servo DC, protezioni, reti di connettore.

## Test 1 — Swing massimo (comp-swing.cir, carico 10 kΩ, 1 kHz)

| Ampiezza in (Vp) | Uscita picco + | Uscita picco − |
|---|---|---|
| 10 → 14 | segue 1:1 | segue 1:1 |
| 16 → 22 | **saturo a +15,85 V** | **saturo a −15,81 V** |

**Risultato chiave: uscita massima ≈ ±15,85 V = 11,2 Vrms = +23,2 dBu.**

Il requisito locked è ≥ +24 dBu capability (voci 7/42); il doc §3.3 assumeva
±21 V = +25 dBu. **La simulazione smentisce l'assunzione**: l'OPA1612 su ±18 V
si ferma a ±16,5 V e lo stadio finale in configurazione follower perde altri
~0,65 V (Vbe + caduta su Re). Non esistono ±21 V con questa topologia.

Opzioni (decisione di Filippo → questione 60 in `docs/02-questioni-aperte.md`):
- (a) stadio finale a guadagno (emettitore comune dentro il feedback) invece del
  follower: recupera i ~6 dB mancanti, più delicato su stabilità;
- (b) bootstrap dell'alimentazione OPA1612 (rail che segue l'uscita): funziona,
  aggiunge componenti;
- (c) op-amp d'ingresso con rail più alti (es. famiglia ±24 V): cambia rumore/THD;
- (d) rivedere il requisito a +23 dBu: il level plan del modulo arriva a +22 dBu
  worst case, quindi +23,2 dBu basterebbe alla catena — ma il requisito di
  sistema DI +24 dBu è locked e va formalmente modificato.

## Test 2 — Banda e stabilità (comp-ac.cir, piccolo segnale)

| Carico | 8 Hz | 1 kHz | 35 kHz | Picco fuori banda | −3 dB |
|---|---|---|---|---|---|
| 10 kΩ, 0 nF | −0,08 dB | −0,06 dB | −0,06 dB | +3,3 dB @ ~50 MHz | 78 MHz |
| 10 kΩ ‖ 10 nF (cavo 100 m) | −0,08 dB | −0,06 dB | −0,14 dB | nessuno | 248 kHz |
| 10 kΩ ‖ 33 nF (ostile) | −0,09 dB | −0,07 dB | **−0,94 dB** | nessuno | 73 kHz |

- Requisito banda 8 Hz–35 kHz ±0,5 dB: **PASSA con cavo 10 nF** (peggio −0,14 dB).
- Con 33 nF il limite alto cede ~1 dB: se si vogliono cavi lunghissimi serve
  un piccolo isolamento (R serie 47-100 Ω prima del carico, da provare).
- Il picco +3,3 dB a ~50 MHz senza carico è fuori banda audio, innocuo ma
  segnalato: con carico capacitivo sparisce (smorzato).

## Test 3 — THD (comp-thd.cir, 14 Vp ≈ +21,2 dBu, massimo pulito)

| Frequenza | 600 Ω | 10 kΩ |
|---|---|---|
| 1 kHz | 0,00014 % | 0,00012 % |
| 35 kHz | 0,0050 % | 0,0043 % |

Target doc §6.1-6.2: < 0,005 % — **rispettato a 1 kHz con 40× di margine**;
a 35 kHz su 600 Ω è esattamente al limite. Nota onestà: il macromodello di
op-amp è lineare, quindi queste cifre descrivono lo stadio d'uscita + anello;
con l'OPA1612 reale la THD potrà solo peggiorare (di poco: l'anello la domina).
Valore letto: "Partial Harmonic Distortion" (somma armoniche 2-9); il campo
"Total" di LTspice su finestre multi-periodo dà artefatti (0,000000% a 35 kHz).

## Test 4 — Corto verso massa (comp-short.cir, ingresso 10 Vp)

- Corrente di picco ramo NPN: **460 mA** (PNP: 380 mA) — senza protezione.
- Dissipazione Q1: picco 4,3 W, media 1,9 W durante il corto.
- Tensione residua in uscita: 0,59 Vp.
- Il target del doc è < 60 mA per ramo con protezione: **la protezione
  (limitazione + clamp Vbe, già prevista §3.3) è indispensabile e va
  dimensionata su questi numeri**. Il transistor nudo sopravvive a un corto
  breve (460 mA < 500 mA assoluti) ma scalda: nessun corto sostenuto senza limitazione.

## Cosa manca per chiudere §6.2

1. Modello OPA1612 ufficiale TI (rumore, THD propria, comportamento ai rail)
2. Rumore residuo d'uscita (target < −100 dBu contributo PSU: test PSRR)
3. Stadio con protezione di corrente → ripetere test corto
4. Verifica termica SOA su corto sostenuto
5. Decisione Filippo sulla topologia per lo swing (questione 60) → risimulare

## Riproduzione

```bash
sim/run_ltspice.sh sim/master-out/comp-swing.cir   # poi comp-ac / comp-thd / comp-short
# risultati nei .log accanto ai netlist (~1 min di avvio Wine per run)
```

---

## v0.3 Test 5 — VAS discreto a guadagno (decisione 83, opzione a) — BOCCIATO (2026-09-29)

Tentativo: OPA1612 → CE NPN (MJE340, Re 2,2-4,7 kΩ → −24 V, carico CCS PNP 6-12 mA) →
diamond invariato; feedback globale a +in (due inversioni nell'avanti → il loop negativo
richiede feedback sul non-invertente; con −in il .op non converge: verificato).
Netlist: `compG-swing.cir` / `compG-ac.cir` / `compG-op.cir` (diagnostica .dc + .meas).

**Finding 1 — latch d'accensione (bistabilità).** Prima iterazione (CCS 6 mA, Re4 4,7 k,
Rb 1k): uscita bloccata a +11,3 V fissi, sorda all'ingresso. Meccanismo misurato
(compG-op): il CE satura (Vce = 0,03 V) perché la corrente di base sommata a Ic su Re4
alza l'emettitore fino al nodo drv; in saturazione il segno dell'anello si inverte e lo
stato si autoconserva (op-amp a +16,5 V, catena bias del diamond morta: v_mid = v_b2 =
v_drv). Mitigazioni trovate: CCS 12 mA + Rb 10 k + diodo Baker (b4→drv) — ma la fragilità
resta strutturale (nodo drv ad alta Z senza padrone DC).

**Finding 2 — muro di stabilità (il killer).** Con .nodeset sul punto buono, risposta in
frequenza (carico 10 k ‖ 10 nF):

| Cc (Miller) | Cf (feedforward) | Rz | Picco closed-loop | f picco |
|---|---|---|---|---|
| 22 p | 22 p | 1 k | +13,0 dB | 64 kHz |
| 100 p | 22 p | 1 k | +8,1 dB | 148 kHz |
| 330 p | 22 p | 1 k | +4,9 dB | 99 kHz |
| 330 p | 100 p | 1 k | **+4,7 dB (migliore)** | 79 kHz |
| 330 p | 22-330 p | 2,2-4,7 k | +9,9…+29,1 dB | 54-69 kHz |

E nella migliore combinazione la banda audio è già fuori specifica: **+3…+4,5 dB a 35 kHz**
(target ±0,5 dB). Analisi: la macro OPA1612 è un integratore (−90° da 25 Hz); qualunque
polo del VAS sotto il crossover aggiunge il secondo −90° → margine ~0. Un booster a
guadagno 2,2 piatto fino al crossover (188 MHz) è irrealizzabile a discreti (nodo drv
5,2 kΩ, Cob 4 pF → polo ~1 MHz). Lezioni: (1) op-amp compensato + stadio a guadagno in
anello = doppio integratore, non si compensa con Miller/lead passivi; (2) il feedback va
sul +in quando l'avanti ha due inversioni (il −in dà anello positivo); (3) .nodeset è lo
strumento per forzare Newton sul punto buono e misurare l'AC vero; (4) il latch da
saturazione del VAS è un modo di guasto da cercare SEMPRE nei compositi (test d'accensione).

**Esito → decisione 86**: via adottata = BOOTSTRAP delle alimentazioni OPA1612 (opzione b
della questione 60): composito v0.2 invariato (A_vas = 1, stabilità già verificata), rail
locali flottanti che seguono l'uscita (Δ ≈ 3-5 V), swing atteso ±21…21,5 V = +25 dBu.
Design e verifica = master-out v0.3 (prossima sessione di ingegneria).

```bash
sim/run_ltspice.sh sim/master-out/compG-ac.cir    # sweep Cc×Rz×Cf, picchi closed-loop
sim/run_ltspice.sh sim/master-out/compG-op.cir    # diagnostica DC del latch (.dc + .meas FIND)
```

---

## v0.3 Test 6 — BOOTSTRAP rail OPA1612 (decisione 86): swing PASS (2026-09-29)

Topologia: composito v0.2 invariato (OPAMAC 2 poli + diamond, feedback unity a −in);
rail op-amp locali flottanti: vplus = OUT + Δ, vminus = OUT − Δ con Δ ≈ 4,4 V
(stringa 7×1N4148 + Vbe del pass); pass serie Q7 NPN da +24 / Q8 PNP verso −24
(MJE340/350); bias stringhe R 4,7 k; handoff dolce ai rail statici ±23,7 V oltre
OUT ≈ ±19,3 V. Netlist: `compB-swing.cir` (carico 10 k, 1 kHz, amp 10→22 Vp).

| Amp in (Vp) | OUT picco + | OUT picco − | vplus max | vminus min |
|---|---|---|---|---|
| 10 → 20 | segue 1:1 | segue 1:1 | OUT+4,36 (tracking ✓) | OUT−4,36 |
| 22 | **+21,50 V** | **−21,15 V** | 24,0 (handoff statico ✓) | −24…−26,3 (transitorio) |

**Risultato chiave: capability ±21,1-21,5 V = +25,7…+25,9 dBu** (correzione 2026-09-29: la conversione dBu era sbagliata; il margine ~1,7 dB era giusto. VALORE SUPERATO dal Test 7: senza Iq reale lo swing era ottimistico) contro requisito
locked ≥ +24 dBu (17,4 Vp): PASS con ~1,7 dB di margine; target §3.3 (±21 V =
+25 dBu) raggiunto. v0.2 nuda: ±15,85 V (+23,2). Asimmetria −0,35 V sul negativo:
la stringa inferiore perde corrente di bias vicino a −24 (nb2 < vm24) e Δ si
riduce prima dell'handoff — accettata (margine intatto); se serve simmetrico:
bias inferiore con JFET CCS invece di R (da valutare in v0.3 definitiva).
Il −26,3 V di vminus al picco = artefatto capacitivo transitorio della stringa
(misura MIN su finestra 6 ms), non quasi-statico: il clamp inferiore resta
sopra il drive richiesto (−21,9 V) con margine.

Limiti della macro (onesti, da verifica a banco/prototipo): PSRR assente → il
rumore delle stringhe LED/diodi sui rail NON è attenuato in sim (nel reale
OPA1612 PSRR ~120 dB LF); Iq assente → nel reale i pass vedono 40 mA continui
(dimensionamento: Q7 worst (24−(OUT+4,4))·40 mA ≈ 1,6 W a OUT −21 → aletta/
rame PCB; Rbu/Rbl da ricontrollare con Iq: stringa 4 mA + Ib 0,3 mA ok).
Mancano alla suite v0.3: AC/stabilità (attesa = v0.2: A_vas = 1 invariato, i
rail entrano solo nei clamp), THD, rumore residuo d'uscita, corto con protezioni
(sempre pendenti dal v0.2), servo DC.

```bash
sim/run_ltspice.sh sim/master-out/compB-swing.cir   # swing bootstrap (questo test)
```

---

## v0.3 Test 7 — Swing + sizing con Iq REALE (2026-09-29) — FINDING: il Test 6 era ottimistico

Macro OPAMAC-ISUP (`opamac-isup.inc` / variante tran `opamac-isup-t.inc`): la v0.2 non
assorbe corrente; la v0.3 modella Iq 40 mA (datasheet OPA1612) + la corrente di uscita
assorbita dai rail locali (specchio di E3). Con l'assorbimento reale, la rete bootstrap
del Test 6 (bias a R 4,7 k) COLLASSA ai picchi (`compB-swing2.cir`):

| Config | OUT picco + | OUT picco − | Limite |
|---|---|---|---|
| Test 6 (Iq ASSENTE) | +21,50 V | −21,15 V | — (ottimistico) |
| Test 7 (Iq 40 mA, bias R) | +19,29 V | −17,94 V | Ib dei pass attraverso R 4,7 k |

Causa: agli estremi le stringhe si spengono e la Ib dei pass deve passare nelle R di
bias → caduta Ib·R + Vbe ≈ 1,5-2,5 V sui rail locali; il lato negativo cede prima
(Q8 PNP lavora in zona invertita/satura vicino all'handoff: β forzato basso).

## v0.3 Test 7b/7c — Bias stringhe a CCS JFET + stringa 9 diodi: swing DEFINITIVO PASS

Fix (`compB-swing3.cir`): (1) bias stringhe con JFET in modo CRD (gate-source corti,
Id = Idss ≈ 3,9 mA costanti — la R di autobias resta inerte nel netlist: Vgs = 0):
a stringa spenta tutta la corrente va nella base del pass → saturazione dura →
handoff a bassa Z; (2) stringa 9×1N4148 per lato (Δ ≈ 5,3 V) + Re 33 Ω (valore v0.2)
→ margine di clamp al livello di requisito ≥ 2 V (vedi lezione Test 9).

| Amp in (Vp) | OUT picco + | OUT picco − |
|---|---|---|
| 10 → 20 | segue 1:1 | segue 1:1 |
| 22 | **+20,91 V** | **−20,42 V** |

**Capability definitiva (Iq reale): ±20,4-20,9 V = +25,4…+25,6 dBu** (10 kΩ);
requisito ≥ +24 dBu (17,37 Vp): **PASS con 1,4-1,6 dB di margine**; su 600 Ω
capability ≈ +20,2 V (margine ≥ +1,3 dB); linearità piena fino a ±20 V.
Rail: tracking Δ ≈ 5,2-5,4, handoff statico ≈ ±23,3-23,7.

**Sizing termico pass (con Iq reale)**: P_Q7/Q8 idle ≈ 0,75 W cad.; programma medio
≈ 1,0 W cad.; picco sine worst 2,7 W (amp 22). Corrente Q7 picco ≈ 50-70 mA.
→ TO-126 (MJE340/350) su ≥ 4 cm² di rame o alettina; alternativa BD139/140.
Supply chip sempre ≥ 8,4 V (min datasheet 4,5) in ogni condizione misurata.
Δ spread da Idss ±30% → ±0,3 V: margine intatto; bin a banco se serve.
Alternativa LED (preferenza design): 3 LED rossi ≈ Δ 4,8-5,0 — meno giunzioni
(rumore e TC minori); scelta finale al prototipo (la sim valida 1N4148).

## v0.3 Test 8 — AC/stabilità col bootstrap (`compB-ac.cir`) — PASS in banda

Stessa struttura misure di comp-ac.cir (v0.2) + rete servo DC finale (sotto):

| Carico | 8 Hz | 1 kHz | 35 kHz | Picco fuori banda | −3 dB |
|---|---|---|---|---|---|
| 10 kΩ, 0 nF | −0,0002 dB | ~0 dB | ~0 dB | +12,8 dB @ >1 MHz | 98 MHz |
| 10 kΩ ‖ 10 nF | −0,0002 dB | ~0 dB | +0,002 dB | +4,7 dB @ ~2 MHz | 2,2 MHz |
| 10 kΩ ‖ 33 nF | −0,0002 dB | ~0 dB | +0,008 dB | +6,2 dB @ ~1,4 MHz | 1,4 MHz |

**Banda 8 Hz-35 kHz ±0,5 dB: PASS con ogni carico** (worst +0,008 dB) — il bootstrap
NON modula la risposta (composito invariato, come atteso da decisione 86). Il picco
closed-loop MHz è fuori banda e innocuo (v0.2 aveva +3,3 dB @ 50 MHz senza carico);
Cboot di decoupling rail↔OUT PROVATO E RIMOSSO (lezione in fondo); smorzamento
eventuale a banco (R+C di Zobel già previsti al connettore).

## v0.3 Test 9 — THD AL LIVELLO DI REQUISITO +24 dBu (`compB-thd.cir`) — PASS

Il Test 4 (v0.2) misurava a 14 Vp perché il composito nudo saturava a ±15,85.
Col bootstrap la THD si misura FINALMENTE a +24 dBu = 17,37 Vp (requisito doc §6):

| Livello | Freq | 600 Ω | 10 kΩ |
|---|---|---|---|
| 14 Vp (+21,2 dBu) | 1 kHz | 0,000142 % | 0,000128 % |
| 14 Vp | 35 kHz | 0,005034 % | 0,004501 % |
| **17,37 Vp (+24 dBu)** | 1 kHz | **0,000119 %** | **0,000106 %** |
| **17,37 Vp** | 35 kHz | **0,004217 %** | **0,003762 %** |

**Target < 0,005 %: PASS a +24 dBu con margine ≥ 18 %** (35 kHz/600 Ω = caso peggiore).
A 14 Vp i valori sono IDENTICI alla v0.2 → conferma A/B: il bootstrap non aggiunge
distorsione (composito invariato ✓ decisione 86).

**Lezione (costata 3 iterazioni): margine di clamp ≥ ~1,5 V.** A +24 dBu su 600 Ω il
drive richiede drv = OUT + Vbe + I·Re ≈ OUT+1,7 V; il clamp sta a OUT + Δ − 1,5:
se Δ si assottiglia (stringa corta, o CCS a fine headroom) il drv sfiora il limit()
a ogni picco → glitch una volta per periodo → pettine armonico piatto (H2-H9 a
~4e-3, THD 1,2-21 %). Misurato con 6 diodi (Δ 3,9) e con 7+Re22 (margine 0,9):
SPARITO con 9 diodi (Δ 5,3) + Re 33 (margine ~2 V). Regola per il banco: se la THD
alta a +24 dBu mostra comb piatto, guardare il margine drv→clamp, non il crossover.

## v0.3 Test 10 — Rumore residuo d'uscita (`compB-noise.cir`) — PASS

.noise con rete servo completa (Rsrc 1k, Rf 1k, Rg/Rinj 1M, integratore 220k/15n):
**5,76 nV/√Hz piatto 10 Hz-100 kHz** → integrato 20 Hz-22 kHz = 0,85 µV =
**−119,2 dBu** contro target < −100 dBu: PASS con 19 dB di margine.
Limiti dichiarati: (a) OPA1612 reale aggiunge 1,1 nV/√Hz (× noise gain 1,001) →
−134 dBu da solo, somma in quadratura → totale ≈ −118,9 dBu (inascoltabile);
(b) la macro non ha PSRR: rumore stringhe sui rail → analisi: shot 38 pA/√Hz ×
r_string ≈ 70 Ω ≈ 2,7 nV/√Hz per rail → via PSRR ~120 dB LF = 2,7 fV/√Hz:
trascurabile di 9 ordini; HF (PSRR ~60 dB) resta pV-level. Nessun RC di filtro
sulle stringhe necessario. (c) ripple ±24 statici → reiezione d'anello + Early:
verifica a banco con PSU reale (task sistema/PSU).

## v0.3 Test 11 — Corto verso massa (`compB-short.cir`) — bootstrap = limitatore naturale

Corto 1 Ω, ingresso 10 Vp (programma) e 22 Vp (abuso): identici (il meccanismo
è il collasso dei rail, non il drive):

| Grandezza | v0.2 (rail ±18 fissi) | v0.3 bootstrap |
|---|---|---|
| Corrente picco ramo NPN | 460 mA | **106 mA** |
| Corrente picco ramo PNP | 380 mA | **67 mA** |
| Q1 dissipazione picco / media | 4,3 W / 1,9 W | **2,15 W / 1,01 W** |
| OUT residuo | 0,59 V | **0,06 V** |
| Rail durante il corto | ±18 fissi | ±5,4 (supply chip 10,8 V ≥ 4,5 ✓) |

Meccanismo: in corto OUT ≈ 0 → i rail locali crollano a ±Δ → clamp ±3,9 V →
il drive del diamond ha escursione minima. **Il target §3.3 < 60 mA/ramo
[PROVVISORIO] è superato dai dati: 106 mA auto-limitati, e la dissipazione media
(1,0 W) = worst di programma normale → corto sostenuto sopravvive col rame
standard (stesso dimensionamento del funzionamento normale).** Revisione
registrata: niente limitatore Vbe dedicato nel design v0.3; protezione estrema
(fuso/PTC per corto prolungato + abuso termico) = dominio PSU (task sistema);
SOA: 24 V × 106 mA = dentro la curva MJE340/350 con ampio margine. Verifica a
banco: corto sostenuto con termocamera su rame reale.

## v0.3 Test 12 — Servo DC + POWER-ON (`compB-servo.cir`) — PASS entrambi

**Rete servo (nuova, definitiva)**: il feedback diretto out→inn della v0.2 non ha
nodo di somma → v0.3: Rf 1k (out→inn) + Rg 1M (inn→0) = guadagno 1,001; ingresso
via Rsrc 1k + iniezione servo via Rinj 1M = attenuazione 0,999 → **guadagno netto
1,000 ±0,001**. Integratore invertente 220k/15n (fc = 0,048 Hz, finestra libera
0,05-0,5 Hz del servo FX validato) → op-amp FET-input low-Iq (TL061-class) su
±18 STATICI (la sua Iq non grava sul bootstrap).
- Vos 3 mV (caso pessimistico; OPA1612 reale max 0,5 mV) → residuo **−29,8 µV**
  (target < 5 mV rispettato 170×); svout stabile a +2,97 V (range ±16 ok:
  autorità ±16 V ≈ ±16 mV nullabili riferiti all'ingresso — 30× il Vos reale).
- Settling: −2,2 mV @ 1 s, −1,2 mV @ 3 s, −167 µV @ 10 s, −30 µV @ 20 s
  (τ ≈ 3,3 s = fc 0,048 Hz); nessun ringing (min post-boot −2,9 mV).
- Errore sul segnale: HP quadratico ½(fc/f)² → a 8 Hz = −0,0002 dB (misurato in
  Test 8: g8hz −0,0002 dB con servo in anello ✓).

**Power-on** (uic: nodi scarichi, ±24 a gradino istantaneo = caso peggiore senza
rampa PSU né mute): OUT transita a **+8,1 / −15,2 V** nei primi 100 ms, supply chip
0 → 7 V. Il mute relay [BLOCCATO §3.7, power-on ~1,5-2 s] COPRE l'intero transiente:
confermato che il relay deve stare a valle del composito (sull'XLR, come da design)
e che il timing §3.7 è adeguato. Con rampa PSU reale il transiente si riduce
ulteriormente (verifica a banco).

## Lezioni di simulazione (macro OPAMAC-ISUP)

1. **Due varianti della macro, per analisi diverse** (entrambe in `sim/master-out/`):
   `opamac-isup.inc` (specchio LINEARE degli assorbimenti: corretto per .ac/.noise —
   il kink di abs() a I(E3)=0 rende indefinita la linearizzazione → picchi spuri
   +13 dB misurati nella prima iterazione) e `opamac-isup-t.inc` (max/abs a tratti:
   corretto per .tran — lo specchio lineare in tran accoppia I(E3)↔rail nel Newton
   a ogni passo: run abortito a 27 min contro ~1 min).
2. **Topologia degli assorbimenti**: B-source verso il nodo 0 (vp→0, 0→vm), NON
   verso out: la prima versione (vp→out, out→vm) iniettava doppio sul nodo d'uscita
   e spostava il kink nel punto sbagliato (comb THD su 600 Ω).
3. **Cboot rail↔OUT (1 µF + 100 nF): PROVATO E RIMOSSO** — con gli specchi a kink
   produce glitch 0,3-0,4 V una volta per periodo (commutazione del ramo di classe AB
   attraverso il cap) → THD 5,9-38 %. A banco: eventuale decoupling dei rail da
   provare SOLO con valori piccoli (100 n) e misura THD prima/dopo.
4. **.nodeset sul punto buono** (out 0, rail ±Δ, drv 0,7): senza, il source stepping
   resta appeso (>7 min) sull'accoppiamento bootstrap+specchio.
5. **Diodi: Vf reale al bias** (0,66 V @ 4 mA per 1N4148 in questo modello, non 0,5):
   il conto di Δ va fatto sui modelli, non a spanne (6 diodi = Δ 3,9 = THD rotta).

## Stato suite v0.3 — CHIUSA (2026-09-29)

Tutti i punti dell'ADDENDUM 2026-09-29 sono coperti: swing+sizing (7/7b/7c),
AC (8), THD a +24 dBu (9), rumore (10), corto/protezioni/SOA (11), servo DC (12),
power-on (12), finestra CM (analisi: CM = OUT sempre centrata nei rail ±Δ; supply
≥ 8,4 V ≥ min 4,5 in ogni caso misurato), nota PSRR (analisi Test 10).
Restano per il banco/prototipo: modello TI ufficiale, THD reale del chip, ripple/PSRR
con PSU vero, corto sostenuto termico su rame, scelta LED vs 1N4148, trim law 2181.

```bash
sim/run_ltspice.sh sim/master-out/compB-swing3.cir   # swing definitivo + sizing
sim/run_ltspice.sh sim/master-out/compB-ac.cir       # AC/stabilita'
sim/run_ltspice.sh sim/master-out/compB-thd.cir      # THD a +24 dBu
sim/run_ltspice.sh sim/master-out/compB-noise.cir    # rumore residuo
sim/run_ltspice.sh sim/master-out/compB-short.cir    # corto
sim/run_ltspice.sh sim/master-out/compB-servo.cir    # servo DC + power-on
```

## v0.3 + dec. 93 — Test 13: INVILUPPO STATICI [M] (2026-10-01)

File: `compB-swing3-env.cir` (swing Test 7b con `.step param vstat LIST
23.6 26.5 29.2`, amp 22 Vp) + `compB-short-env.cir` (corto Test 11 agli
estremi 23.6/29.2 V, amp 22 Vp abuso). Motivazione: la dec. 93 ha
trasformato gli statici [M] da punto fisso 23,7 V a inviluppo
**±23,6…29,2 V su rete ±10%** (W3 2×20 V); verifica che requisito
≥+24 dBu e sopravvivenza al corto valgano agli estremi.

Swing (capability):

| Statici | +picco | −picco | dBu | Esito |
|---|---|---|---|---|
| 23,6 V (rete −10%, worst) | +20,57 V | −20,05 V | +25,5 / +25,2 | **PASS ≥+24, margine 1,2-1,5 dB** |
| 26,5 V (nominale) | +22,00 | −22,00 | ≥+26,3 — limitata dall'input (amp 22 Vp): capability reale più alta | PASS |
| 29,2 V (rete +10%) | +22,00 | −22,00 | ≥+26,3 — limitata dall'input | PASS |

Coerenza: il punto 23,6 V riproduce il Test 7b verificato (±20,4-20,9 V a
statici 23,7) scalato di −0,3 V.

Dissipazioni pass (Q7/Q8) a pieno swing: medie 0,93 → 1,19 W e picchi
2,18-2,36 W lungo l'inviluppo → dentro il sizing v0.3 (0,75 W idle /
1,0 W programma / 2,7 W picco, rame ≥4 cm²); a rete alta +19% medio.

Corto verso massa (abuso 22 Vp, sostenuto):

| Statici | iQ1 pk | Q1 avg | Q1 pk | Q2 avg | Vout residuo |
|---|---|---|---|---|---|
| 23,6 V | 105,6 mA | 1,00 W | 2,11 W | 0,72 W | 0,122 V |
| 29,2 V | 106,3 mA | 1,28 W | 2,72 W | 0,92 W | 0,124 V |

Meccanismo CONFERMATO: il limite bootstrap è indipendente dagli statici
(106 mA a entrambi gli estremi); a rete alta la dissipazione scala con gli
statici (+28% Q1 avg) → 1,28 W medi resta dentro il dimensionamento
"worst di programma" (rame ≥4 cm²); rail bootstrap collassati a ±5,6…5,9 V
durante il corto, come atteso.

CONCLUSIONE: **inviluppo dec. 93 PASS in simulazione a entrambi gli
estremi** — requisito ≥+24 dBu con margine ≥1,2 dB a qualsiasi rete;
corto sostenuto sopravvive a rete alta dentro il sizing esistente.
Resta a banco: THD a +24 dBu a statici alti (il Test 9 era a 23,7 V).
