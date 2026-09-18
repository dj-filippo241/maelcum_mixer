# FASE 1 — Modulo CANALE CDJ/LINE: design circuitale v0.1

> **Stato**: bozza di ingegneria. Topologie candidate [PROVVISORIO], nessun valore congelato
> (regola 3). **Scope deciso da Filippo 2026-09-18: SOLO ingresso line (CDJ/line); la sezione
> phono/RIAA NON si progetta ora** — il modulo lascia il posto per una variante phono futura.
>
> Dipendenze da verificare sull'export ChatGPT [EXPORT]: canale stereo vs mono, logica
> esatta dell'assignment switch FX, punto di prelievo CUE, interazione elettrica col
> modulo filtro globale, standard I/O del backplane (questione aperta 38).

## 1. Requisiti funzionali (richiami)

- [BLOCCATO 15/17] Catena canale: input → gain → EQ 4 bande → split CUE/FX → filtro (selettore locale) → fader → bus DJ
- [BLOCCATO 17] EQ 4 bande stile Xone: bassi, medio-bassi, medi, alti; ogni knob fino a −∞ a full CCW; il comportamento "reference + contribution" è quello consolidato nel resoconto [R]
- [BLOCCATO 16] Il canale esiste come modulo a sé sul backplane
- [BLOCCATO 12] Stereo: controlli linked, no pan, matched L/R, mono-compatibile — assumiamo percorso audio stereo con controlli singoli (verifica [EXPORT])
- [BLOCCATO 7] Nominale 0 dBu, picchi interni attesi ≤ +16 dBu, dominio ±15 V (sine capability ~+19 dBu)
- [R derivato] Split CUE e FX **pre-fader**: la catena bloccata li colloca prima del fader — il canale chiuso non zittisce né il CUE né l'FX send (comportamento classico da dub/club)
- [BLOCCATO 47] Fader = slider; il resto pot rotativi
- [BLOCCATO 14] CV 0–5 V come convenzione d'interfaccia sul backplane (il selettore filtro del canale comunica in digitale semplice o CV: da definire col modulo filtro)

## 2. Diagramma a blocchi (per metà canale — L; R identico)

```
[RCA LINE IN] ─► [A] PROTEZIONE + IN BUFFER ─► [A2] TRIM/GAIN ─► [B] EQ 4 BANDE
                                                                     │
                                            ┌────────────────────────┼───────────────────┐
                                            │                        │                   │
                                     [C] CUE SEND              [D] FX SEND          [E] FILTER I/F
                                      (pre-fader,               (pre-fader,           (selettore locale
                                       switch verso              EQ 2 bande,           HPF/OFF/LPF;
                                       CUE bus)                  assign 1-of-4,        audio al modulo
                                                                 level pot)          filtro via backplane)
                                            │                        │                   │
                                            │                        │            ritorno filtro
                                            │                        │                   │
                                            ▼                        ▼                   ▼
                                         (al modulo CUE)      (al modulo FX)      [F] FADER (slider)
                                                                                           │
                                                                                    [G] OUT DRIVER
                                                                                           │
                                                                          [H] clip warn LED (pickup)
                                                                                           │
                                                                                    ► DJ BUS (backplane)

[M] PSU LOCALE: ±24 V main in → ±15 V low-noise (audio), +5 V control (LED, logica)
```

## 3. Design per stadio

### 3.1 [A] Ingresso line + protezione

- RCA pannello (dorato, isolato da chassis con rondella dedicata — la strategia di massa RCA è questione aperta 21)
- Protezione: R serie 100 Ω + TVS low-capacitance + bead ferrite; rete RC d'ingresso con polo > 100 kHz (invisibile sotto i 35 kHz)
- Buffer: OPA1612 unity non-inverting, Z_in ≥ 47 kΩ (compatibile con qualunque uscita line CDJ/preamp), dominio ±15 V
- Assunzioni sorgenti [PROVVISORIO]: uscite CDJ/line tipiche −10 dBV…+8 dBu; nessun carico difficile

### 3.2 [A2] Trim/gain variabile

- Range proposto [PROVVISORIO]: **−10…+10 dB** con detent a unity — copre sorgenti consumer calde e fredde senza spreco di corsa
- Implementazione: pot lineare 10 kΩ in partitore seguito da stadio gain variabile inverting (R_f commutata dal wiper) OPPURE attenuatore passivo + buffer. Raccomandato: **inverting con pot nel feedback** (un solo attivo, legge pulita, Z bassa subito dopo il trim)
- Il trim è il PUNTO di guadagno del canale: a unity, 0 dBu in ingresso → 0 dBu in uscita

### 3.3 [B] EQ 4 bande — celle a contribuzione (il cuore musicale del modulo)

**Architettura [PROVVISORIO], coerente col "contribution-cell concept" del resoconto:**

```
                     ┌────────────── R_ref (unity) ─────────────┐
IN (post-trim) ──────┤                                          ├──► SUMMING AMP (OPA1612
                     ├─ [LOW shelf]  ─ pot LOW ──── R1 ────────┤     inverting) ──► OUT EQ
                     ├─ [LOW-MID bell] pot LOW-MID ─ R2 ───────┤
                     ├─ [MID bell]   ─ pot MID ──── R3 ────────┤
                     └─ [HIGH shelf] ─ pot HIGH ─── R4 ────────┘
```

- **Come funziona**: il segnale diretto passa per il ramo di riferimento (unity); ogni banda viene estratta dal suo filtro, attenuata/variata dal pot di banda e ri-sommata al riferimento. La risposta è piatta quando ogni contribuzione è calibrata sul suo valore nominale (detent del pot).
- **Kill naturale**: pot a full CCW = wiper a massa = contribuzione zero = la banda sparisce (−∞). È il comportamento bloccato in decisione 17, e viene gratis dalla topologia.
- **Boost**: fine corsa CW = contribuzione massima. Range proposto [PROVVISORIO — APERTO-F]: **+9 dB** per banda (stile DJ console: boost musicale ma non distruttivo; il resoconto non fissa il valore).
- **Bande e frequenze [PROVVISORIO — da rivedere con Filippo, come concordato]**:

| Banda | Tipo | Frequenza proposta | Q/larghezza proposta |
|---|---|---|---|
| LOW | shelf | ~100 Hz | shelf 6 dB/ott |
| LOW-MID | bell | ~300 Hz | Q ~1,0 |
| MID | bell | ~1,2 kHz | Q ~1,2 |
| HIGH | shelf | ~8 kHz | shelf 6 dB/ott |

  Nota: l'EQ di canale NON deve sovrapporsi concettualmente al KILL del 5-way: qui le bande sono "musicali" (colorare il canale), là sono le vie fisiche dell'impianto (decisione 22).

- **Filtri**: shelf = Sallen-Key o RC + buffer; bell = multiple-feedback (MFB) con OPA1612. Condensatori C0G/NP0 e film (mai ceramici X7R nel segnale: microfonici e distortivi), resistori 1% thin-film, valori di frequenza calcolati — non a orecchio
- **Flat-at-center**: obiettivo ±0,5 dB di piattezza con tutti i pot al detent [PROVVISORIO] — si ottiene calibrando i gain di contribuzione (R1-R4) in simulazione; tolleranze dei componenti: 1% basta se le R critiche sono matched/trimmer opzionale
- **Interazione tra bande**: nella topologia a contribuzione le bande interagiscono poco ma non zero (somma vettoriale). La simulazione §6 deve mostrare le curve con 1, 2 e 4 bande attive insieme

### 3.4 [C] CUE send (pre-fader)

- Pickup subito dopo l'EQ (punto esatto: post-EQ, pre-split-FX — verificare [EXPORT] se il resoconto lo colloca altrove)
- Buffer dedicato → switch CUE del canale (on/off) → CUE bus sul backplane (somma dei CUE attivi vive nel modulo CUE, questione aperta 18)
- Nessuna elaborazione: il CUE deve far sentire esattamente il canale

### 3.5 [D] FX send (pre-fader)

Catena: pickup post-EQ → EQ 2 bande di send [topologia e frequenze: questione aperta 13, non si duplica qui — il modulo canale espone l'interfaccia] → pot di livello send → switch di assegnazione 1-of-4 bus FX → driver verso backplane.

- **Assignment switch**: 1-of-4 rotativo; la logica (una sola destinazione alla volta? più destinazioni? esclusione reciproca?) è [EXPORT] — qui si progetta l'interfaccia elettrica: 4 uscite a livello di bus, muting delle non selezionate con FET-switch o relay a seconda di cosa dice l'export sulla soppressione dei transienti (questione aperta 13: "switch transient suppression")
- Livello send: pot −∞…0 dB (il bus FX ha la sua somma e il suo headroom nel modulo FX)
- Anti-pop: la commutazione di bus a segnale caldo è il punto delicato — candidata: la commutazione a zero-crossing non esiste in analogico puro → switch make-before-break + resistenze di isolamento; da simulare/misurare

### 3.6 [E] Interfaccia filtro globale

Dal resoconto (decisioni 26-27): i 4 controlli del filtro sono CONDIVISI (nel modulo filtro), il canale ha solo il selettore locale HPF/OFF/LPF.

- **Percorso audio**: il canale manda il segnale post-split al modulo filtro e ne riceve il ritorno? Oppure il filtro vive sul bus DJ a valle dei canali? Il resoconto dice "channel routing implementation" = aperto → **[EXPORT] critico**: questo punto decide se il modulo canale ha due connessioni audio in più sul backplane (send/return filtro) o nessuna
- **Ipotesi di lavoro [PROVVISORIO]** (la più coerente con "selettore per canale su filtro globale"): send/return dedicato per canale via backplane; il selettore locale pilota una matrice di relay NEL modulo filtro (il canale invia solo la logica: 2 bit HPF/OFF/LPF sulla sezione control del backplane, CV 0-5 V)
- Vantaggio dell'ipotesi: i controlli condivisi restano nel modulo filtro, il canale non ha circuiti audio verso il filtro se non il proprio send/return bufferizzato

### 3.7 [F] Fader di canale

- **Raccomandazione [PROVVISORIO]**: slider pot audio di qualità (la selezione hardware è rimandata — questione 40) come attenuatore passivo post-filtro, seguito da buffer unity OPA1612 → Z bassa verso il bus
- Alternativa VCA (come il master): più controllo (legge esatta, mute elettronico) ma +1 THAT 218x per canale e +CV. Non necessario se il fader è l'unico controllo di livello del canale — si tiene come opzione se l'export rivela esigenze di automazione/mute globale
- Legge del fader: audio taper standard; la corsa utile sta negli ultimi 3/4 (il primo quarto = attenuazione fine verso −∞): da verificare col pot scelto

### 3.8 [G] Out driver + clip warning [H]

- Driver: OPA1612 unity, Z_out < 100 Ω verso il DJ bus (che è summing inverting nel modulo a valle — decisione sul chi-summa: questione 38/[EXPORT])
- Clip warning: comparatore sul pickup d'uscita, soglia [PROVVISORIO] +16 dBu (≈ inizio zona "hard"), LED di canale — il metering vero di canale è nel modulo metering/5-way, qui basta l'avviso
- Il bus DJ è passivo-inverting a monte del 5-way [R]: il driver di canale deve pilotare i resistori di bus senza alzare la Z sorgente — valore esatto dopo la questione 38

### 3.9 [M] PSU locale

- ±24 V main in → **±15 V low-noise** (LT3045/LT3094, decisione 54 estesa ai moduli audio) per tutto il percorso audio del canale
- +5 V control (dal bus control del backplane) per LED e logica selettori
- Corrente stimata modulo: ~40-60 mA su ±15 V (4-5 OPA1612 dual + logica) → < 2 W dissipati [PROVVISORIO]
- Decoupling locale: 100 nF per pin di alimentazione + 10 µF per rail sul modulo

## 4. Tabella livelli del modulo (level plan)

| Nodo | Nominale | Max atteso | Capability sine | Dominio |
|---|---|---|---|---|
| Ingresso RCA | −10 dBV…0 dBu | +8 dBu (CDJ hot) | — | — |
| Post-trim | 0 dBu | +10 dBu (trim +10 su sorgente calda: raro) | +19 dBu | ±15 V |
| Post-EQ (tutte le bande a 0) | 0 dBu | +16 dBu (programma + boost) | +19 dBu | ±15 V |
| FX send out | 0 dBu | +12 dBu | +19 dBu | ±15 V |
| Post-fader/out driver | 0 dBu (fader unity) | +16 dBu | +19 dBu | ±15 V |

**Nota di margine**: con trim +10 dB e boost EQ +9 dB su più bande il canale PUÒ superare il dominio ±15 V su programma estremo. È coerente con la filosofia (si spinge sapendo di spingere), ma la simulazione deve mostrare dove e come satura (l'OPA1612 satura morbido). Se servisse margine: trim max +6 dB invece di +10. → questione aperta nuova.

## 5. Componenti candidati (BOM di massima)

| Ruolo | Candidato | Note | Prezzo stimato |
|---|---|---|---|
| Op-amp audio (4-5 dual) | OPA1612AID | buffer, trim, filtri EQ, summing, out driver | ~4-6 € cad |
| Comparator clip | TLV3201 o 1/4 LM339 | soglia +16 dBu | ~0,5 € |
| Pot EQ (4) + trim + send | hardware rimandato (questione 40) | intanto: RK097/RK27-like 10 kΩ nei calcoli | — |
| Fader | hardware rimandato (questione 40) | RSA0N-like nei calcoli | — |
| Condensatori filtri | C0G/NP0 + film (PPS/ecse) | valori da calcolo, tolleranza 2-5% | ~3-5 € |
| Resistori segnale | thin-film 1% (0,1% sulle R critiche EQ) | | ~2-3 € |
| RCA ×2 | dorati isolati da chassis | | ~3-4 € |
| Switch/relay assign FX | da decidere post-export (FET-switch vs mini-relay) | | ~2-5 € |
| Connettore backplane | famiglia da definire (questione 22/38) | | — |

**Stima BOM modulo canale (esclusi pot/fader/pannello): ~35-55 €** [PROVVISORIO]

## 6. Simulazioni da eseguire (LTspice)

1. **EQ completo**: risposta con ogni banda sola (verifica centri/Q/boost), tutte al detent (piattezza ±0,5 dB), combinazioni estreme (LOW kill + HIGH +9), interazione tra bande
2. **Trim + EQ + headroom**: THD e punto di saturazione con trim +10 e boost multipli (dove satura, quanto è morbido)
3. **Noise**: residuo all'out driver con ingresso terminato; contributo dei pot (47 k vs 10 k — il rumore dei pot è spesso dominante in un canale DJ); target [PROVVISORIO] < −88 dBu A-wtd residuo di canale
4. **Crosstalk L/R**: accoppiamento nel summing EQ e sul backplane (target < −80 dB)
5. **FX assign switch**: transiente di commutazione a segnale caldo (anti-pop)
6. Banda 8 Hz–35 kHz end-to-end a EQ piatto (±0,5 dB)

## 7. Cosa serve da Filippo (poche, il resto è [PROVVISORIO] o [EXPORT])

1. **Boost EQ per banda**: ok +9 dB proposto, o preferisci più cattivo (+12/+15)? (il kill a −∞ è già bloccato)
2. **Trim input**: ok −10…+10 dB, o i tuoi CDJ hanno livello fisso noto e basta ±6?
3. *(Non urgente, già concordato)*: frequenze e comportamenti EQ si rivedono insieme prima dello schema definitivo

## 8. Prossimi passi

1. Risposte alle 2 voci §7 → v0.2
2. Simulazioni §6 (file `.asc` in `sim/cdj-channel/`) — prima: EQ completo, è la firma sonora del canale
3. Alla chiusura dell'export: risolvere [EXPORT] (stereo/mono, send/return filtro, assignment FX, punto CUE, standard backplane)
4. Solo dopo: schema definitivo e PCB

---

## ADDENDUM 2026-09-18 (post status document + risposte di Filippo) — revisione v0.2 in coda

Voci di questo v0.1 SUPERATE o AGGIORNATE (decisioni 58-66, docs/03 §8):

- §3.2 trim −10…+10 dB → **gain −∞→0→+10 dB con detent centrale**, stereo-linked, tracking ≤0,5 dB (locked)
- §3.3 EQ: boost **+6 dB (locked**, non +9); frequenze baseline **70/250/1k/5k Hz** (proposte dai documenti, Q ~0,7-0,9); nomi bande LOW/LOW-MID/**MID-HIGH**/HIGH; law di controllo: lenta al centro, rapida agli estremi; requisito nuovo: **tracking stereo ≤0,25 dB** (metodo da decidere — voce 53)
- §3.5 FX assign: **multiple simultanee** (non 1-of-4), precision analogue switch, JFET scartati
- §3.6 interfaccia filtro: **ipotesi originale CONFERMATA dal proprietario** — send/return verso il MODULO FILTRO esterno, il canale ha solo il selettore HPF/OFF/LPF (decisione 60)
- §3.8 meter: **meter DJ completo** post-filter/overdrive pre-fader, peak con persistenza, calibrazione identica tra canali (non solo clip-warn)
- §7 domande: superate (risposte integrate nelle decisioni 58-66)
- Nota fase 1: finché il modulo filtro non esiste, il selettore resta su OFF/bypass e il canale lavora dry (decisione 61)
