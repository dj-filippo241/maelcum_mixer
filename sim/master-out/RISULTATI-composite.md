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

**Risultato chiave: capability ±21,1-21,5 V = +25,0…+25,2 dBu** contro requisito
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
