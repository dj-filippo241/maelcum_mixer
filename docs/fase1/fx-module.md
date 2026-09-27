# FASE 1 — Modulo FX: design v0.1 (2026-09-25)

> **v0.1 (2026-09-25)**: primo design del modulo FX (bus/pedali/ritorni/matrice
> di feedback). Livello: architettura + funzioni di trasferimento + verifica
> simulata dei punti a rischio (loop di feedback, summing worst-case). NON
> congela valori (regola 3): tutto [PROVVISORIO] salvo i requisiti [BLOCCATO].
> Fonti: SPECIFICA §7, gain-staging sheet §2 (K3/K4), questioni 13/14/37/55/65,
> CDJ v0.3 §3.5 (FX send). Il modulo FX è il quarto pezzo della fase 1
> (canale + FX + master + PSU base → valida il backplane).

## 1. Requisiti (stato: BLOCCATO salvo dove indicato)

| Requisito | Valore | Fonte |
|---|---|---|
| Bus | 4 (FX1-4); sorgenti: canali DJ, mic, generic mono, ritorni FX; cross-routing permesso; self-route FXn→FXn **proibito fisicamente** | SPEC §7 |
| Summing bus | attivo virtual-earth, ~0 dBu nom, dominio ±18 V; 10k/10k [PROVVISORIO]; ~12 contributori stereo; worst correlato +21,6 dBu entro capability con saturazione morbida | SPEC §7, sheet §2 |
| Interfaccia pedali | bus → driver high-headroom → pad selezionabile (prototipo −20 dB) → protezione → pedale → protezione/DC-control → ritorno hi-Z ≥1 MΩ; tolleranza ritorno −20…+18 dBu; banda ~5 Hz–40 kHz; mono pedal = controlled mono sum (mai hard-short L/R); stereo = L/R indipendenti | SPEC §7 |
| Ritorni | stereo-capable (mono centrato); gain −∞→0→+20 dB; EQ2 (LOW ~100-150, HIGH ~4-6 kHz, −∞→0→+6, broad, no risonanza/saturazione); meter dopo gain+EQ prima del fader (detector rapido, clip latch 300-500 ms); fader stereo linked | SPEC §7 |
| Regola livelli | livello_in × gain ≤ +23 dBu (K4) | sheet §2 |
| Reroute/feedback | ogni ritorno → 3 destinazioni (gli altri bus), no self; level −∞→0 dB con law a tratti: 0-20%: −∞…−40; 20-45%: −40…−20; 45-70%: −20…−10; 70-85%: −10…−4; 85-95%: −4…−1; 95-100%: −1…0 dB; tecnologia VCA/attenuatore (solo attenuazione); catena controllo: pot → CV buffer → mappa non lineare → smoothing 1-5 ms → VCA; **niente limiter** | SPEC §7 |
| Comportamento live | fader del ritorno = udibilità verso MASTER, NON tocca il loop interno (reroute pre-fader): fader giù, il feedback continua; loop unity = oscillazione autosostenuta **bounded by design** | SPEC §7 |
| Transienti | assign e switching: break-before-make + ramp 1-5 ms (voce 55, proposta uniformata al filtro) | CDJ §3.5 |

## 2. Architettura del modulo

```
                        MODULO FX (v0.1)
 dai canali/mic/generic (backplane): send L/R per sorgente, gia' con
 EQ2+level+assign (lato canale, CDJ §3.5) — il modulo riceve gli assign
 gia' commutati sui 4 bus.

 BUS 1..4 (×4 sezioni identiche):
   ingressi multipli → SUMMING virtual-earth → pad driver → DRIVER pedale
     (high-headroom, low-Z) → pad selezionabile −20/−10/0 dB → protezione
     (R serie + TVS) → JACK SEND L/R
   ritorno: JACK RETURN L/R → protezione + DC-control → BUFFER hi-Z ≥1 MΩ
     (JFET) → GAIN VCA (−∞..0..+20) → EQ2 (celle serie, §6) → nodo METER
     (pickup) → nodo REROUTE (pre-fader!) → FADER (linked) → buffer →
     backplane MASTER SUM

 MATRICE FEEDBACK (per ritorno, stereo):
   nodo REROUTE → 3 × VCA di reroute (law a tratti SPEC) → bus 1..4 MENO
   il proprio (self-route ESCLUSO FISICAMENTE dal PCB/connessioni)

 CONTROLLO:
   pot reroute → CV buffer → mappa a tratti (shaper, stessa famiglia del
   filtro §4) → smoothing 1-5 ms → CV ai VCA (stereo linked: 1 CV per
   coppia L/R)
```

Nota "controlled mono sum" (pedale mono): send mono = somma L+R via 2×10k
verso il jack mono (mai hard-short); return mono = buffer → distribuito a
L/R con due path matched (centraggio affidabile, no phase games).

## 3. Summing bus — dimensionamento e verifica

- Virtual-earth: Rf 10k, N ingressi 10k [PROVVISORIO]: ogni send di canale
  (uscita a bassa Z, level −∞..0) contribuisce con peso unity.
- Worst-case correlato (sheet §2/K3): 12 × 0 dBu in fase = 9,3 Vp =
  +21,6 dBu — **verificato in simulazione** (§8): nessun clipping
  (clamp ±16,5 V), margine 7,2 V. La saturazione oltre il worst è morbida
  (op-amp classe OPA1612 — il clamp del macro è duro, il reale satura
  graduale; carattere da verificare col modello TI, come per il master).
- Crosstalk tra contributori: virtual-earth ideale = 0; reale ≈ (1+N)/A ≈
  13/1000 = −38 dB (guadagno d'anello del macro). Nella pratica dominano
  accoppiamenti di layout/PSU: regole PCB (stellar summing point, ground
  del modulo separato — questione 21).
- Headroom interno: il nodo di summing è a massa virtuale (0 V): nessun
  problema di swing interno; l'uscita del summing è il punto caldo
  (+21,6 dBu worst) → op-amp di bus su ±18 V con clamp reale ~±16,5.

## 4. Interfaccia pedali (questione 13 — proposta v0.1 [PROVVISORIO])

- **Send**: summing → driver buffer (OPA1612 class, low-Z ≤50 Ω) →
  **pad selezionabile** solder-pad/DIP: −20 dB (prototipo, chitarra/rack
  -10 dBu sensibili) / −10 / 0 dB (rack +4 dBu) → R serie 100 Ω + TVS
  low-cap → jack. Livello al pedale con pad −20: nominale −20 dBu
  (0,775 Vrms? no: 0 dBu bus → −20 dBu = 77 mV ≈ livello chitarra ✓),
  max +16 dBu bus → −4 dBu al pedale (non si sfonda mai l'ingresso
  pedale tipico).
- **Return**: jack → R 100 Ω + TVS + polarizzazione → **buffer JFET
  hi-Z ≥1 MΩ** (candidato: OPA1642/JFET discreto 2N5457 — da verificare
  rumore e bias; alternativa: op-amp JFET-input) → **DC-control**:
  requisito banda 5 Hz–40 kHz (infrasub!) → niente cap di accoppiamento
  economici: **DC servo** (integratore che corregge l'offset del buffer,
  corner ~0,5 Hz) oppure cap film 22-47 µF (angolo ≤3 Hz con 1 MΩ:
  22 µF → 7 Hz ✗; 47 µF → 3,4 Hz ✓ [PROVVISORIO]). Raccomandazione:
  DC servo (nessun elettrolitico nel percorso, coerente col requisito
  AC ≤5 Hz del progetto, decisione 65).
- Tolleranza ritorno −20…+18 dBu: il buffer JFET + gain VCA a −∞..0
  assorbe tutto il range; +18 dBu in ingresso = 6,9 Vp: headroom dominio
  ±18 ✓ (stesso worst del canale).
- Protezione: R serie + TVS bidirezionali low-cap (<5 pF per non tagliare
  40 kHz su 1 MΩ//5pF... a 1 MΩ anche 10 pF = −1,6 dB @40 kHz: TVS
  low-cap obbligatoria, verifica in v0.2).

## 5. Canale di ritorno

Catena (SPEC §7): buffer hi-Z → GAIN VCA (THAT 2181, −∞..0..+20, CV dal
pot con law dB lineare + shaper) → EQ2 (§6) → METER pickup (detector
rapido + clip latch 300-500 ms — design condiviso col meter di canale,
simulazione peak detector = CDJ §7 punto 3) → **nodo REROUTE (pre-fader)**
→ FADER stereo linked (−∞..0, slider conduttivo-plastica come i canali,
voce 40) → buffer out ≤50 Ω → MASTER SUM (backplane).

Regola K4 (sheet §2): livello_in × gain ≤ +23 dBu: con ritorno max +18 dBu
e gain max +20 → +38 teorici: **la law del gain VCA va limitata** o il
trim di calibrazione del return deve mappare il fine corsa su ingressi
realistici; proposta v0.1 [PROVVISORIO]: gain max effettivo +20 solo con
ingresso ≤ +3 dBu (regola d'uso documentata) + hard-limit resistivo nel
path (pad commutato se ingresso > +10: selettore sensitivity −20/0/+10
come nei preamp — da ratificare con Filippo: cambia il pannello).

## 6. EQ2 (ritorni E send di canale — questione 65)

Stessa famiglia delle celle serie EQ v0.3 (decisione 76/77):
- **LOW shelf** ~120 Hz (send) / 100-150 Hz (return): cella shelf
  complementare (R/Rp 1:31 → kill −30 dB, boost +6) — identica alla LOW
  del canale, valori RC scalati sulla frequenza.
- **HIGH** ~4,5 kHz (send) / 4-6 kHz (return): cella sottrattiva
  −(1−b·HP2) — il kill HIGH dà bump +2,1 dB al corner e −9…−14 dB a 20-35 kHz (Q HP2 corretto 2026-09-25): **la questione 68
  si applica anche qui** (stessa scelta: accettare o crossfade-LP2;
  un'unica decisione copre canale, send FX e ritorni).
- Law dedicate [BLOCCATO dai doc]: bassi "tiene per quasi tutta la corsa,
  toglie rapido solo al taglio estremo" = cut concentrato negli ultimi
  ~15-20% (taper custom, tabella in v0.2); alti "taglio rapido in
  partenza, poi graduale" = inversa. Boost +6 su entrambe.
- "No risonanza/saturazione" (SPEC §7): le celle serie non hanno risonanza
  per costruzione ✓; op-amp in classe lineare.
- Silicon: 2 celle × (1-3 sezioni) per EQ2: LOW shelf 1 sezione + HIGH
  sottrattiva 3 sezioni = 4 sezioni per EQ2 mono, 8 per stereo — per i
  4 ritorni: 16 sezioni (4 quad); lato send (nei canali): 8 sezioni per
  canale stereo... il send EQ2 vive nel modulo CANALE (CDJ §3.5): +2 quad
  per canale. [PROVVISORIO]

## 7. Matrice di feedback (questione 14 — design v0.1)

- **Topologia**: per ogni ritorno (4), 3 VCA di reroute (verso gli altri
  3 bus) × 2 canali = 6 sezioni VCA per ritorno = 24 sezioni = **12× THAT
  2181** [PROVVISORIO — voce 37 per la reperibilità]. Solo attenuazione
  (gain ≤ 0 dB) come da SPEC. Self-route: escluso fisicamente (nessuna
  pista/connessione dal reroute del ritorno N al bus N) ✓ requisito.
- **Law a tratti** (SPEC, tabella in §1): shaper CV a diodi/resistori —
  stessa famiglia dello shaper del filtro (filter-module §4): 6 breakpoint,
  trimmer a banco. Il tratto 95-100% (−1…0 dB) è il controllo finissimo
  vicino all'apertura: è la zona musicale critica del dub feedback.
  **VERIFICATA end-to-end (§8.3)**: 13 punti di griglia esatti a 1e-8 dB
  attraverso shaper → smoothing → THAT 218x (macro `sim/lib/that2181.inc`).
  12 shaper identici (uno per controllo reroute): rete diodi/resistori,
  replica su PCB, costo trascurabile.
- **Smoothing 1-5 ms** (SPEC): RC + buffer sulla CV del VCA (1 ms =
  click-free senza impastare il gesto — verificato coi numeri in §8.3:
  click −9,6 dB vs catena non smorzata, chiusura ~5 ms; 5 ms = click sotto
  il programma ma chiusura ~25 ms).
- **Stabilità del loop / bounded by design** (§8, simulato): il loop
  ritorno→reroute→bus→pedale→ritorno ha guadagno d'anello g_loop =
  g_reroute · g_pedale_path. SPEC: niente limiter → il bounding è dato
  dalla **saturazione del pedale stesso** (ogni pedale reale satura) +
  dalla struttura gain: regola di design v0.1 [PROVVISORIO]: a reroute
  100% (0 dB) e pad nominale, g_loop = ~0…+3 dB (unity o poco sopra):
  sotto unity = eco che decade (uso normale); a unity/sopra = oscillazione
  autosostenuta che si stabilizza sulla saturazione del pedale = il gesto
  dub classico ("il delay che si mangia se stesso"). Simulazione (§8):
  con g_loop 1,2-2,0 l'ampiezza si ferma dove il tanh del pedale chiude
  l'anello — mai runaway ai rail.
- **Accumulo di rumore** (questione 14): il loop ricircola il rumore:
  fattore 1/√(1−g²): g=0,9 → +2,6 dB; g=0,99 → +10 dB; g≥1 → il rumore
  cresce con l'oscillazione (mascherato). Regola d'uso: il rumore cresce
  solo vicino a unity, dove è musicalmente coperto — accettabile; niente
  gating (vietate dinamiche automatiche).
- **Isolamento tra destinazioni**: ogni reroute è un VCA dedicato (uscita
  propria verso il bus di destinazione, diodo/pista separata): nessun
  accoppiamento tra destinazioni se non via bus (virtual-earth, −38 dB).

## 8. Simulazioni v0.1 (`sim/fx/`)

Modelli comportamentali (il circuito reale arriva in v0.2): lo scopo è la
dinamica del loop e il worst-case del summing, non il carattere sonoro.

### 8.1 Loop di feedback (fx-loop.cir, comportamentale)

| g_loop | Ampiezza a regime | Interpretazione |
|---|---|---|
| 0,8 | decade a ~0 | sotto unity: l'eco si spegne — uso normale |
| 1,0 | sostiene l'ampiezza iniziale | unity critico: oscillazione autosostenuta |
| 1,2 | ±7,9 V = **+20,2 dBu** | cresce e si STABILIZZA sulla saturazione del pedale |
| 2,0 | ±11,5 V = **+23,4 dBu** | stabilizzato, MAI ai rail (clamp ±16,5 V) |

- **"Bounded by design" VERIFICATO**: il limiting viene dal tanh del pedale,
  non dai rail — coerente con "niente limiter" (SPEC §7). Con il margine di
  design proposto (g_loop ≤ +3 dB a reroute 100%) il regime sta a ~+20 dBu,
  dentro la regola ≤ +23 dBu del dominio.
- Limite del modello (onestà): zero ritardo e catena non invertente →
  l'ampiezza si latcha su una polarità. Nel loop reale c'è il tempo di
  ritardo del pedale: l'eco si rigenera a tempo, il meccanismo di bounding
  è identico. Il carattere (come "suona" l'oscillazione) si ascolta al
  prototipo con pedale vero.

### 8.2 Summing bus (fx-summing.cir)

- 12 sorgenti × 0,775 Vp (0 dBu) in fase → uscita ±9,18 V = **+21,5 dBu**
  (atteso ideale 9,3 V: −1,3% da guadagno d'anello finito): **nessun
  clipping**, margine 7,3 V al clamp. Conferma il worst-case del sheet §2/K3.
- Crosstalk: −38 dB analitico (virtual-earth, A=1000); nella pratica domina
  il layout (regole §3).

### 8.3 v0.2 — Law a tratti del reroute VERIFICATA (`reroute-law.cir`, `reroute-ramp.cir`)

Catena CV (SPEC §7): pot 0-5 V → shaper a tratti (in sim: PWL via if()
annidati — LTspice non ha pwl() nei B-source; nel reale: rete
diodi/resistori a breakpoint, famiglia dello shaper del filtro,
filter-module §4, trimmer a banco) → smoothing RC 1 ms → EC− del THAT 218x
(modello condiviso `sim/lib/that2181.inc`, law 6,1 mV/dB).

**Law esatta**: griglia 13 punti (6 breakpoint SPEC + 7 punti medi), errore
≤1e-8 dB: G = 0/−0,5/−1/−2,5/−4/−7/−10/−15/−20/−30/−40/−70/−100 dB per
θ = 1/0,975/0,95/0,90/0,85/0,775/0,70/0,575/0,45/0,325/0,20/0,10/0. Il
tratto 95-100% (−1…0, zona critica del feedback dub) è lineare-in-dB come
da SPEC; "−∞" = floor −100 dB del VCA (gain range datasheet).

**Transiente di reroute** (gesto: pot chiuso in 10 µs, segnale 0 dBu 1 kHz,
sonda click HP 2 poli — metodo di `sim/five-way/gate-ramp.cir`):

| τ smoothing | Picco click | vs brusco | Tempo di chiusura |
|---|---|---|---|
| 1 µs (assente) | 1,00 V | — | istantaneo |
| 1 ms | 0,33 V | −9,6 dB | ~5 ms |
| 5 ms | 0,21 V (= baseline del programma) | −13,4 dB | ~25 ms |

Entrambi i τ della SPEC sono click-free (1 ms resta 1,5 dB sopra il
residuo di programma; 5 ms scende sotto). La differenza è il feel: 1 ms =
lo "scatto" che chiude subito (coerente col gate 5-way); 5 ms = fade più
morbido ma chiusura lenta. Raccomandazione [PROVVISORIO]: **1 ms** per il
reroute; conferma a orecchio in M4L (dati per la ratifica voce 55).

## 9. BOM di massima v0.1 [molto PROVVISORIA]

| Voce | Qtà | Note |
|---|---|---|
| THAT 2180/2181 (SINGLE VCA — datasheet 2026-09-27: "dual" = porti di controllo, non canali) | 12 reroute + 4 gain ritorno = 16 chip | voce 37 (reperibilità/prezzo: ~34-36 chip in tutto il mixer) |
| Quad op-amp (bus driver, buffer, summing, EQ2 ritorni, servo DC) | ~10-12 | classe OPA1654/1612 mista |
| JFET buffer ritorno (o op-amp JFET-input) | 8 | hi-Z ≥1 MΩ |
| Shaper law reroute (diodi/R/trimmer) | 8 canali CV | famiglia shaper filtro |
| Switch/jack/pad/DIP, TVS low-cap, R 0,1% | — | pad send selezionabile |
| Stima costo | ~150-200 € | dominato dai VCA; esemplare unico, qualità > costi (SPEC §1) |

## 10. Questioni toccate

- **13** (interfaccia pedali): proposta v0.1 completa (§4) — pad −20/−10/0,
  DC servo, TVS low-cap; DA CONFERMARE con Filippo (selettore sensitivity
  del §5 cambia il pannello: sua scelta).
- **14** (matrice feedback): stabilità e bounded-by-design SIMULATI (§8);
  rumore di loop quantificato; isolamento ok. Restano: circuito concreto
  degli shaper (v0.2) e verifica con pedali reali (prototipo).
- **55** (transienti): proposta uniformata break-before-make + ramp 1-5 ms
  anche per assign FX e reroute — DA RATIFICARE.
- **65** (EQ2): allineata alla famiglia serie v0.3; la questione 68 (kill
  HIGH) si applica anche qui — una decisione unica copre tutto.
- **37** (THAT 2181): il modulo FX ne usa 16 — la verifica di reperibilità
  diventa critica per questo modulo (in subordine: VCA discreti o SSM2164
  legacy).
- NUOVA [APERTO-F → questione 69, §5]: selettore sensitivity dei ritorni (−20/0/+10 dB)
  per rispettare K4 senza limitare il gain: cambia il pannello, decide Filippo.

## 11. Prossimi passi (v0.2)

1. [LAW + CATENA CV FATTE 2026-09-27, §8.3] Restano i circuiti concreti:
   DC servo dei ritorni, EQ2 con valori scalati + simulazione (stesso
   metodo di eq-serie beta-3, macro reali in `sim/lib/opamp-audio.inc`).
2. [FATTO 2026-09-27] Peak detector meter (condiviso con CDJ §7.3):
   `sim/meter/` + `RISULTATI-peak-det.md` — droop a 10 Hz per τ release
   (−2,9/−0,88/−0,31 dB per ciclo con τ 0,3/1/3 s → raccomandazione ≥1 s),
   clip latch 442 ms retriggerabile dimostrato, cattura HF = banco beta-3.
   Soglie e zone display = questione 19.
3. [FATTO 2026-09-27] Modello THAT 218x: `sim/lib/that2181.inc` condiviso
   (law/headroom verificati qui §8.3 e in CDJ §7 item 2). THD: non
   misurabile in macro lineare — datasheet + modello TI + banco al
   prototipo. CORREZIONE: 218x = SINGLE (voce 37 riscritta: i 16 del BOM
   §9 sono 16 CHIP, non 16 sezioni di dual).
4. Verifica TVS/capacità su banda 40 kHz a 1 MΩ.
5. Ratifiche di Filippo: sensitivity return (69), questione 55 (dati ramp
   in §8.3 e five-way §8.5), questione 68.
6. Prototipo: un bus + un ritorno + un loop con pedale reale prima del PCB.
