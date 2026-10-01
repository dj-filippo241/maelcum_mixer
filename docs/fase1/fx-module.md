# FASE 1 — Modulo FX: design v0.3-WIP (2026-10-01)

> **v0.3-WIP (2026-10-01, decisione 91)**: (a) la sezione send di canale
> (EQ2 + level + assign) ESCE dal canale CDJ e vive nel micro-modulo
> FX-SEND ×4 (`docs/fase1/fx-send-module.md`): questo modulo riceve le
> iniezioni dai micro-moduli (net multidrop per bus, come il DJ bus);
> (b) SELF-FEEDBACK = quarto pot per ritorno: matrice 12× → **16× THAT
> 218x** (3 cross + 1 self per bus); il divieto v0.2 "self-route escluso
> fisicamente" è REVOCATO da dec. 91 (scelta di Filippo). Bounded-by-design
> CONFERMATO sul ramo self (§8.5, `sim/fx/fx-loop-self.cir`); dry loop senza
> pedale = clamp ±16,5 V, disciplina K4 (dec. 84). Chip modulo: 16 → 20;
> mixer: ~28-30 (lotto clone voce 37 → ~44-52 pz [PROVVISORIO]).
>
> **v0.2 (2026-09-27/28)**: law a tratti del reroute VERIFICATA end-to-end
> col macro THAT 218x condiviso (§8.3); DC servo dei ritorni VALIDATO, EQ2
> valori scalati VALIDATA, TVS/banda 40 kHz verificata con correzione del
> claim v0.1 (§8.4); peak detector condiviso in `sim/meter/`. CORREZIONE
> trasversale: THAT 2180/2181 = SINGLE channel (16 chip per questo modulo,
> voce 37). Design completo salvo implementazione discreta dello shaper
> (prototipo) e ratifiche di Filippo (69/55/68).
>
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
| Reroute/feedback | ogni ritorno → 3 destinazioni (gli altri bus), no self; level −∞→0 dB con law a tratti: 0-20%: −∞…−40; 20-45%: −40…−20; 45-70%: −20…−10; 70-85%: −10…−4; 85-95%: −4…−1; 95-100%: −1…0 dB; tecnologia VCA/attenuatore (solo attenuazione); catena controllo: pot → CV buffer → mappa non lineare → smoothing 1 ms (decisione 80) → VCA; **niente limiter** | SPEC §7 |
| Comportamento live | fader del ritorno = udibilità verso MASTER, NON tocca il loop interno (reroute pre-fader): fader giù, il feedback continua; loop unity = oscillazione autosostenuta **bounded by design** | SPEC §7 |
| Transienti | assign e switching: break-before-make + ramp 1 ms (decisione 80, famiglia unica per tutte le commutazioni CV) | CDJ §3.5 |

## 2. Architettura del modulo

```
                        MODULO FX (v0.2)
 dai micro-moduli FX-SEND ×4 (dec. 91a: EQ2+level+assign vivono li',
 `fx-send-module.md`) + mic/generic: un NET MULTIDROP per bus (S1-S4),
 ogni sorgente inietta col proprio 10k lato sorgente sul virtual-earth
 del bus (stessa convenzione del DJ bus; backplane §4).

 BUS 1..4 (×4 sezioni identiche):
   ingressi multipli → SUMMING virtual-earth → pad driver → DRIVER pedale
     (high-headroom, low-Z) → pad selezionabile −20/−10/0 dB → protezione
     (R serie + TVS) → JACK SEND L/R
   ritorno: JACK RETURN L/R → protezione + DC-control → BUFFER hi-Z ≥1 MΩ
     (JFET) → GAIN VCA (−∞..0..+20) → EQ2 (celle serie, §6) → nodo METER
     (pickup) → nodo REROUTE (pre-fader!) → FADER (linked) → buffer →
     backplane MASTER SUM

 MATRICE FEEDBACK (per ritorno, stereo) [REV dec. 91b]:
   nodo REROUTE → 4 × VCA di reroute (3 cross + 1 SELF; law a tratti SPEC,
   stessa famiglia) → bus 1..4 INCLUSO il proprio (il divieto v0.2
   "self-route escluso fisicamente" è REVOCATO: il self re-inietta sul
   summing del proprio bus, stesso nodo dei cross)

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

## 4. Interfaccia pedali (questione 13 — proposta v0.2 [PROVVISORIO])

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
  economici: **DC servo VALIDATO v0.2 (§8.4)** — buffer con nodo FB per
  l'iniezione (gain 2) + integratore vero (1 MΩ/15 nF) + R inj 1 MΩ:
  corner 0,053 Hz, errore sul segnale a 5 Hz = −0,001 dB (l'errore del
  servo è quadratico ½(fc/f)²: anche corner 0,5 Hz darebbe −0,04 dB),
  nulling offset ≥84 dB (3 mV → 191 nV), settling τ ≈ 3 s. Il cap film
  47 µF resta alternativa economica (angolo 3,4 Hz) ma il servo evita
  elettrolitici/film enormi nel percorso (coerente con dec. 65).
- Tolleranza ritorno −20…+18 dBu: il buffer JFET + gain VCA a −∞..0
  assorbe tutto il range; +18 dBu in ingresso = 6,9 Vp: headroom dominio
  ±18 ✓ (stesso worst del canale).
- Protezione: R serie + TVS bidirezionali low-cap. **Verifica v0.2 (§8.4) —
  CORREZIONE del claim v0.1** ("10 pF a 1 MΩ = −1,6 dB @40 kHz"): il conto
  era doppiamente sbagliato (a 1 MΩ sorgente sarebbero −8,6 dB; soprattutto
  la R di bias NON fa il polo con la C del nodo — lo fa la Z della SORGENTE).
  Numeri reali: ritorno rack (sorgente ~100 Ω): TVS irrilevante, −0,001 dB
  @40 kHz anche con 10 pF; ritorno chitarra (10 kΩ + cavo 220 pF): −1,24…
  −1,32 dB @40 kHz di cui la TVS (2→10 pF) vale 0,07 dB — domina il cavo
  (fisica del pickup, non dell'interfaccia). TVS low-cap ≤5 pF resta buona
  pratica (quota ≤0,05 dB); R bias 1 MΩ confermata (carico chitarra
  −0,087 dB). La banda 5 Hz–40 kHz dell'ELETTRONICA è verificata (servo +
  buffer piatti, §8.4).

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
- **Valori scalati VERIFICATI v0.2 (§8.4)**: LOW C = 56 nF (shelf ~120 Hz),
  HIGH Rh1/Rh2 = 5,23k/2,5k con Ch 10 nF (~4,5 kHz); griglia conforme:
  detent ±0,005 dB su 20 Hz–35 kHz, kill LOW −29,6 dB @20 Hz, boost +5,9…
  +6,0, kill HIGH −9,3 @35 kHz con bump +0,5 @4,5 kHz (classe canale:
  questione 68 confermata anche qui).
- Silicon: 2 celle × (1-3 sezioni) per EQ2: LOW shelf 1 sezione + HIGH
  sottrattiva 3 sezioni = 4 sezioni per EQ2 mono, 8 per stereo — per i
  4 ritorni: 16 sezioni (4 quad); lato send (nei canali): 8 sezioni per
  canale stereo... il send EQ2 vive nel modulo CANALE (CDJ §3.5): +2 quad
  per canale. [PROVVISORIO]

## 7. Matrice di feedback (questione 14 — design v0.1)

- **Topologia [REV dec. 91b]**: per ogni ritorno (4), **4 VCA di reroute
  (3 cross verso gli altri bus + 1 SELF verso il proprio bus)** × 2 canali
  = 8 sezioni VCA per ritorno = 32 sezioni = **16× THAT 2181**
  [PROVVISORIO — voce 37 per la reperibilità]. Solo attenuazione (gain
  ≤ 0 dB) come da SPEC. Il self si inietta sullo STESSO nodo summing del
  proprio bus (virtual-earth): punto unico d'ingresso, isolamento tra
  destinazioni invariato, nessun percorso speciale sul PCB (il divieto
  v0.2 è revocato: la pista self ORA esiste). Perché lì: il nodo REROUTE
  (pre-fader, §5) è l'unico punto che vede il ritorno prima del master —
  il self passa dal fader del ritorno come i cross (gesto coerente: chiudo
  il fader e il feedback sparisce tutto).
- **Law a tratti** (SPEC, tabella in §1): shaper CV a diodi/resistori —
  stessa famiglia dello shaper del filtro (filter-module §4): 6 breakpoint,
  trimmer a banco. Il tratto 95-100% (−1…0 dB) è il controllo finissimo
  vicino all'apertura: è la zona musicale critica del dub feedback.
  **VERIFICATA end-to-end (§8.3)**: 13 punti di griglia esatti a 1e-8 dB
  attraverso shaper → smoothing → THAT 218x (macro `sim/lib/that2181.inc`).
  **16 shaper identici** (uno per controllo reroute, 12 cross + 4 self —
  dec. 91b: il self usa la STESSA law, confermato §8.5): rete
  diodi/resistori, replica su PCB, costo trascurabile.
- **Smoothing 1-5 ms** (SPEC): RC + buffer sulla CV del VCA (1 ms =
  click-free senza impastare il gesto — verificato coi numeri in §8.3:
  click −9,6 dB vs catena non smorzata, chiusura ~5 ms; 5 ms = click sotto
  il programma ma chiusura ~25 ms).
- **Stabilità del loop / bounded by design** (§8, simulato; §8.5 per il
  self): il loop ritorno→reroute→bus→pedale→ritorno ha guadagno d'anello
  g_loop = g_reroute · g_pedale_path. SPEC: niente limiter → il bounding è dato
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

## 8. Simulazioni v0.1-v0.2 (`sim/fx/`)

§8.1-8.2 (v0.1): modelli comportamentali — scopo: dinamica del loop e
worst-case del summing, non il carattere sonoro. §8.3-8.4 (v0.2): modelli
reali (`sim/lib/that2181.inc`, `sim/lib/opamp-audio.inc`).

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
lo "scatto" che chiude subito (coerente col gate 5-way [escluso dalla famiglia con dec. 88: kill hard-cut a switch]); 5 ms = fade più
morbido ma chiusura lenta. Raccomandazione RATIFICATA (decisione 80): **1 ms**
per il reroute, famiglia unica; conferma a orecchio in M4L.

### 8.4 v0.2 — Banda/TVS, DC servo, EQ2 (`fx-tvs-bw.cir`, `fx-dc-servo.cir`, `fx-eq2.cir`)

**Banda d'ingresso e TVS** (griglia R_sorgente × C_TVS, §4): il polo HF lo
fa la Z sorgente con la C del nodo, NON la R di bias 1 MΩ. Rack (100 Ω):
−0,001 dB @40 kHz con TVS fino a 10 pF. Chitarra (10 kΩ + cavo 220 pF):
−1,24…−1,32 dB @40 kHz (il cavo domina; la TVS aggiunge ≤0,07 dB). Il claim
v0.1 (−1,6 dB da 10 pF su 1 MΩ) era sbagliato nel modello e nel conto:
corretto in §4. Scelta componenti: TVS ≤5 pF, R bias 1 MΩ (JFET-input).

**DC servo** (`fx-dc-servo.cir`, buffer OP1642-class con Vos 3 mV): catena
buffer gain 2 (nodo FB = iniezione) → I/V −0,5 (stadio d'ingresso VCA) →
servo = integratore invertente (1 MΩ/15 nF, τi 15 ms) → R inj 1 MΩ sul FB.
- Loop gain misurato (broken-loop): T(1 Hz) = −25,5 dB, pendenza 1/f →
  fc = 0,053 Hz come da progetto;
- segnale: piatto 5 Hz–100 kHz, errore a 5 Hz = −0,001 dB (l'iniezione sul
  FB forma un HP sul segnale con errore quadratico ½(fc/f)²: anche il corner
  0,5 Hz del v0.1 starebbe in ±0,05 dB — il corner è libero tra 0,05 e 0,5 Hz);
- offset: nulling da 3 mV a −191 nV (84 dB); settling τ ≈ 3,1 s (residuo
  20 µV a 15 s dall'accensione — il mute di partenza dei ritorni copre);
- offset di gain residuo +0,043 dB (R inj carica il partitore FB di 1/1000):
  si assorbe nel trim di calibrazione del ritorno (gain VCA).

**EQ2 valori scalati** (`fx-eq2.cir`, celle serie v0.3 con OP1654/OP1612 da
libreria): griglia 6 modi — detent ±0,005 dB (20 Hz–35 kHz); kill LOW
−29,6 dB @20 Hz (dec. 77); boost LOW +5,93 @20; kill HIGH: bump +0,47
@4,5k, −5,1 @20k, −9,3 @35k (questione 68 si applica identica al canale);
boost HIGH +5,1…+5,7 @20-35k; both-kill = somma dei due. Scaling confermato:
LOW C 56 nF (Rp 31k invariato), HIGH R 5,23k/2,5k (Ch 10 nF invariato).

### 8.5 v0.3 — Self-feedback (dec. 91b): bounded-by-design CONFERMATO (`fx-loop-self.cir`, `fx-loop-self-dry.cir`, `fx-self-cvsmooth.cir` + `RISULTATI-fx-self.md`, 2026-10-01)

Con pedale (tanh ±12 V): g_loop 0,8 → decade; 1,0 → sostiene; 1,2 →
±7,90 V = +20,2 dBu; 2,0 → ±11,49 V = +23,4 dBu — **identico al cross
(§8.1), mai ai rail (clamp ±16,5 V)**: il bounding viene dal pedale,
"niente limiter" rispettato anche sul self. Dry loop (patch send→return
senza pedale): g 3,0 e 10,0 → **runaway contenuto solo dai clamp ±16,5 V**
= caso K4 (dec. 84/91: disciplina operatore, recuperabile chiudendo il
pot; nota d'uso: dry loop legittimo solo con self sotto unity).
Smoothing CV ramo self: RC 1k/1µ (τ 1 ms) → transizione inviluppo ~5 ms
vs ~10 µs hard, law −10 dB esatta (0,6925 V da 2,19 V) — stessa famiglia
dei cross (§8.3/§8.5 five-way: click −9 dB class). Limite del modello
(zero ritardo → latch di polarità) documentato in §8.1: vale anche qui.

## 9. BOM di massima v0.1 [molto PROVVISORIA]

| Voce | Qtà | Note |
|---|---|---|
| THAT 2180/2181 (SINGLE VCA — datasheet 2026-09-27: "dual" = porti di controllo, non canali) | 16 reroute (12 cross + 4 self, dec. 91) + 4 gain ritorno = 20 chip | voce 37 (reperibilità/prezzo: ~28-30 chip in tutto il mixer post-dec. 91 (era ~24-26 post-dec. 88, ~34-36 pre); lotto clone → ~44-52 pz [PROVVISORIO]) |
| Quad op-amp (bus driver, buffer, summing, EQ2 ritorni, servo DC) | ~10-12 | classe OPA1654/1612 mista |
| JFET buffer ritorno (o op-amp JFET-input) | 8 | hi-Z ≥1 MΩ |
| Shaper law reroute (diodi/R/trimmer) | 16 canali CV (12 cross + 4 self) | famiglia shaper filtro |
| Micro-moduli FX-SEND (dec. 91a) | 4 | BOM propria in `fx-send-module.md` §5 (~25-35 €/cad) |
| Switch/jack/pad/DIP, TVS low-cap, R 0,1% | — | pad send selezionabile |
| Stima costo | ~150-200 € | dominato dai VCA; esemplare unico, qualità > costi (SPEC §1) |

## 10. Questioni toccate

- **13** (interfaccia pedali): proposta v0.1 completa (§4) — pad −20/−10/0,
  DC servo, TVS low-cap; DA CONFERMARE con Filippo (selettore sensitivity
  del §5 cambia il pannello: sua scelta).
- **14** (matrice feedback): stabilità e bounded-by-design SIMULATI (§8)
  e CONFERMATI sul ramo self (§8.5, dec. 91b: 16× VCA, dry loop = K4);
  rumore di loop quantificato; isolamento ok. Restano: circuito concreto
  degli shaper (ora 16) e verifica con pedali reali (prototipo).
- **55** (transienti): CHIUSA 2026-09-28 — decisione 80: BBM + ramp 1 ms,
  famiglia unica per tutte le commutazioni CV del mixer.
- **65** (EQ2): allineata alla famiglia serie v0.3; la questione 68 (kill
  HIGH) si applica anche qui — una decisione unica copre tutto.
- **37** (THAT 2181): il modulo FX ne usa 16 — la verifica di reperibilità
  diventa critica per questo modulo (in subordine: VCA discreti o SSM2164
  legacy).
- NUOVA [APERTO-F → questione 69, §5]: selettore sensitivity dei ritorni (−20/0/+10 dB)
  per rispettare K4 senza limitare il gain: cambia il pannello, decide Filippo.

## 11. Prossimi passi (v0.2)

1. [FATTO 2026-09-27/28: law + catena CV (§8.3), DC servo ed EQ2 scalata
   (§8.4)] Resta l'implementazione a componenti discreti dello shaper
   (rete diodi/resistori, famiglia filtro) e il layout del nodo d'ingresso
   (TVS/cavo) — da millefori/PCB.
2. [FATTO 2026-09-27] Peak detector meter (condiviso con CDJ §7 item 6):
   `sim/meter/` + `RISULTATI-peak-det.md` — droop a 10 Hz per τ release
   (−2,9/−0,88/−0,31 dB per ciclo con τ 0,3/1/3 s); ballistica RATIFICATA:
   release ~0,3 s stile Pioneer DJM (decisione 81),
   clip latch 442 ms retriggerabile dimostrato, cattura HF = banco beta-3.
   Soglie e zone display = questione 19 (parte restante).
3. [FATTO 2026-09-27] Modello THAT 218x: `sim/lib/that2181.inc` condiviso
   (law/headroom verificati qui §8.3 e in CDJ §7 item 4). THD: non
   misurabile in macro lineare — datasheet + modello TI + banco al
   prototipo. CORREZIONE: 218x = SINGLE (voce 37 riscritta: i 16 del BOM
   §9 sono 16 CHIP, non 16 sezioni di dual).
4. [FATTO 2026-09-27] Verifica TVS/banda 40 kHz: claim v0.1 CORRETTO (§4,
   §8.4) — il polo lo fa la Z sorgente, non la R di bias; TVS ≤5 pF buona
   pratica, 1 MΩ confermato.
5. Ratifiche di Filippo: sensitivity return (69), questione 55 (dati ramp
   in §8.3 e five-way §8.5), questione 68.
6. Prototipo: un bus + un ritorno + un loop con pedale reale prima del PCB.
