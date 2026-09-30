# RISULTATI — Module-noise 5-way v0.2.1 + D6 rumore drive (2026-09-30)

Task 3 handoff 2026-09-29: «module-noise catena v0.2.1 completa INCL. D6
rumore drive (stima −98 dBu, Rg 10k dominante) vs target −90 dBu».
Netlist: `drive-noise.cir` (D6), `module-noise-v021.cir` (catena completa).
Esito in una riga: **la stima era sbagliata due volte — il drive reale fa
−85,7 dBu (domina il VCA, non Rg) e il modulo completo fa −77,3…−73,0 dBu:
il target −90 dBu NON è raggiungibile con 6 THAT 218x nel percorso.**
Più un finding sistemico: tutti i numeri di rumore integrato del repo sono
~21 dB ottimisti (quirk LTspice `.meas INTEG`). Dettaglio sotto.

## 1. Due quirk di LTspice 26.0.2 (verificati con test minimi)

**QUIRK 1 — `.meas noise INTEG V(onoise)*V(onoise)` integra en²·√Δf, non
en²·Δf.** Test risolutivo: R 10 Ω nota (densità 0,407 nV/√Hz, integrale vero
20-20k = 3,31e-15): il log dà 2,34e-17, rapporto esatto 141,4 = √19980.
Conseguenza: ogni totale di rumore ricavato come √INTEG (metodologia usata
fin qui nel repo) è basso di (Δf)^¼ ≈ 11,9× = **21,5 dB** (spettro piatto).
Metodo corretto adottato qui: densità misurate a 10-12 punti (`.meas FIND
V(onoise) AT f`), integrazione trapezoidale di en² in python.

**QUIRK 2 — le E source `value={...}` con uscita riferita a nodo NON gnd
non propagano il rumore in .noise** (test minimi: `E out 0 value={V(n)}`
propaga; `E out ref value={V(n)}` propaga solo ref; il rumore iniettato va
messo con **E lineare 4 nodi**: `Ex out+ out− in+ in− 1`, forma classica
SPICE che fa parte della matrice piccolo-segnale). Attenzione: le macro del
repo (OP1654/OP1612/OPAMP) usano E value gnd-riferite e propagano ✓ —
il caso3 (Rg) lo conferma; ma ogni iniezione futura deve usare la forma
lineare. Bonus bug: `.subckt VCAM` (that2181-style) istanziato in un netlist
che contiene anche la banca SK/AP2 → parse «Instance with that name already
defined» (bisect: F3/F5/F7 in questa cartella... file tmp rimossi); fix =
inline del VCAM con nomi unici (fatto in `module-noise-v021.cir`).

Lezione candidata per il metodo di simulazione: mai più totali di rumore da
√INTEG; iniezioni di rumore solo con E/F/G/H lineari; verificare sempre con
una R nota (densità e integrale hanno valori attesi esatti).

## 2. D6 — rumore catena drive (`drive-noise.cir`, ablations .step case)

Uscita drive (pre make-up), 20 Hz-20 kHz non A-pesata, θ-invariante
(nessuna sorgente a monte del VCA; V1 noiseless):

| caso | µV | dBu | nV/√Hz @1k |
|---|---|---|---|
| completa (VCA −98 dBV + servo TL062) | 40,25 | **−85,7** | 284,7 |
| VCA silente | 14,40 | −94,6 | 101,9 |
| servo silente | 38,97 | −86,0 | 275,7 |
| Rg 100 Ω | 39,89 | −85,8 | 282,2 |
| VCA −104 dBV (I/V 10k) | 30,20 | −88,2 | 213,7 |

Contributi (potenza): **VCA 218x 37,6 µV (−86,3 dBu) = DOMINANTE (87%)**;
servo TL062 via Rinj 10,1 µV (−97,7) — l'iniezione sospettata a desk è reale:
35 nV/√Hz ×2 (noise gain X5) ×0,9 (Rinj/Rf) ≈ 64 nV a reco; Rg 10k 5,4 µV
(−103,2); discreti+recovery il resto. **La stima handoff «−98 dBu, Rg
dominante» era doppia errata**: Rg è il terzo contributo, e il totale è
−85,7 dBu pre-makeup = **−79,7 dBu al master sum** (make-up +6 dB).

Fix ingegneristiche disponibili (nessuna tocca la musica): servo con op-amp
silenzioso (TL072 18n / OPA2134 8n al posto del TL062 35n) o scala
Rinj 2,2k→22k + R1s 1M→10M + C1s 470n→47n (fc invariata): −6…−9 dB sul
drive; I/V del VCA a 10k (regola datasheet): −2,5 dB.

## 3. Rumore 218x — fonte e interpretazione

Product page THAT (2181 Series): **Output Noise −98 dBV a 0 dB gain**
(= 12,6 µV = 89 nV/√Hz su 20 kHz), Dynamic Range >120 dB; nota datasheet
(via ricerca): con resistenze I/V a 10 kΩ il floor scende a −104 dBV typ
(= 47 nV/√Hz). Condizioni esatte (banda/pesatura) NON verificate sul PDF
(serve poppler): interpretazione usata = bianchi 20-20k non pesati
(conservativa). Modello: R 481k (−98 dBV) o 240k (−104 dBV) + E lineare
in serie all'uscita VCA. Il clone CoolAudio V2181L dichiara DR >115 dB
(peggio: floor ~−97 dBu classe).

## 4. Modulo completo v0.2.1 (`module-noise-v021.cir`)

Catena mono: pad −6 → banca allineata (macro uniforme ~6 nV, metodologia
v0.2) → 5 gate 218x CON rumore → summer → 5 celle v0.2.1 detent (OP1654
reali 4,5 nV + JFET VCR NJFX + pot 10k) → drive v0.3 reale (D6) → make-up
+6. 6 config (.step gcase × th):

| config | µV out | dBu | dBu A-wtd (~−2,2) | vs target −90 |
|---|---|---|---|---|
| θ0 VCA −98 dBV (datasheet std) | 105,2 | **−77,3** | ~−79,5 | FAIL 10,5 dB |
| θ0 VCA −104 dBV (I/V 10k) | 81,8 | −79,5 | ~−81,7 | FAIL 8,3 dB |
| θ0 VCA silenziosi (= v0.2.1 senza 218x) | 48,2 | −84,1 | ~−86,3 | FAIL 3,7 dB |
| θ50 VCA −98 dBV | 172,5 | **−73,0** | ~−75,2 | FAIL 14,8 dB |
| θ50 VCA −104 dBV | 137,8 | −75,0 | ~−77,2 | FAIL 12,8 dB |
| θ50 VCA silenziosi | 91,0 | −78,6 | ~−80,8 | FAIL 9,2 dB |

Scomposizione θ0: tutti i VCA (6×, −98 dBV) = 93,5 µV (−78,4 dBu);
banca+celle+discreti+servo = 48,2 µV (−84,1 dBu).

**Lettura**: (1) il drive DA SOLO (−79,7 dBu post-makeup) sfora il target;
(2) anche zittendo tutti i VCA il modulo resta ~4 dB sopra il target — la
banca con le R da 86,6k/174k della SK (37-53 nV/√Hz ciascuna!) e il servo
TL062 pesano; (3) il noise segue la law del drive: +4,3 dB da θ0 a θ50
(normale per uno stadio a guadagno variabile).

## 5. Verdetto sul target (sheet §3: out 5-way ≤ −90 dBu A-wtd)

Il target −90 dBu A-wtd è **irraggiungibile** con l'architettura bloccata
(gate VCA per via + drive 218x, decisioni 24/80/82). Realistico con le
fix ingegneristiche (VCA I/V 10k, servo silenzioso, R banca scalate,
op-amp reali 1,1 nV al posto della macro 6 nV): **−81…−84 dBu unweighted
≈ −83…−86 A-wtd a θ0** — servono comunque 4-7 dB di deroga sul target,
oppure una revisione architetturale (gate non-VCA = contraddice dec. 80;
drive senza 218x = ridisegno law validata). Contesto musicale: −80 dBu sta
~20 dB sotto il fruscio del vinile (−60 dBu) e 80 dB sotto il nominale —
per un percorso dub a 6 VCA è una cifra onesta; un DJ mixer moderno dichiara
~100 dB ma con 1-2 VCA al massimo.

**Decisione di Filippo richiesta** (regola 2: target BLOCCATO sheet §3):
(a) deroga/renegotiation del target a ~−82 dBu A-wtd con fix ingegneristiche;
(b) mantenere −90 e ridisegnare (costo: gate a switch = addio fade 1 ms
dec. 80, oppure drive law senza 218x = ri-validazione); (c) stato dell'arte
ibrido: fix ingegneristiche + 1-2 VCA sostituiti.

## 6. Impatto sistemico del QUIRK 1 (numeri del repo da rivedere)

Tutti i totali √INTEG (fattore −21,5 dB su spettro piatto, −20…−24 dB su
spettri reali) — GIÀ CORRETTI oggi: phono (EIN 1,79 µV 10-20k, out −79,8
dBu; doc aggiornati). TRIAGE (aggiornato 2026-09-30, stesso giorno): **master-out −119,2 dBu
VALIDO** — usava già densità×√BW manuale (PASS 19 dB; la stima «~2 dB»
scritta a caldo qui sotto era sbagliata). **EQ β3: reale −89,2 dBu**
(den 190,5 nV piatta, rerun 10 punti) — target canale −92 superato dalla
sola EQ: ritaratura di SISTEMA. Celle PoC −121,7/−124,9 invalidati ma
superati da questa campagna (celle reali nel modulo). Filtro −107,8…−134,8:
da rerun (spettro band-limited, correzione stimata 2-6 dB). Module v0.2
−108,4: invalidato, sostituito. Mancano da sempre: budget canale DJ
completo e FX bus (mai simulati). → voce 71 docs/02. Nota: le DENSITÀ (nV/√Hz) misurate con .meas FIND sono corrette
ovunque — solo i totali integrati erano sbagliati.

## 7. Riproduzione

```
sim/run_ltspice.sh sim/five-way/drive-noise.cir          # D6, 5 casi
sim/run_ltspice.sh sim/five-way/module-noise-v021.cir    # modulo, 6 config
sim/run_ltspice.sh sim/cdj/phono-noise-fix.cir           # phono corretto
```
Integrazione: densità a 10-12 punti nei log, trapezoidale su en² (python,
vedi comando di analisi nella sessione 2026-09-30). I file tmp-mtest* del
bisect sono stati rimossi.
