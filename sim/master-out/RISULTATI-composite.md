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
