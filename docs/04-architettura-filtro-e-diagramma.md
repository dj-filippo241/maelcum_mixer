# 04 — Diagramma completo del mixer + architettura del filtro (A vs B)

> Nato dalla domanda di Filippo (2026-09-18): «voglio capire meglio il filtro: pensavo
> fossero solo 2 — come funziona il filtro dello Xone:92? Prima di passare alle PCB voglio
> essere sicuro che tutto il resto abbia senso; voglio un diagramma completo».
> Le informazioni sullo Xone:92 sono verificate su manuali/fonti Allen & Heath (link in §4).

## 1. Diagramma completo del mixer (tutti i moduli)

```
 SORGENTI            MODULI CANALE (×4, stereo)                 MODULO FILTRO            MODULO 5-WAY
═══════════        ═══════════════════════════════            ═══════════════          ═══════════════

 CDJ/LINE ──► PROTEZ → BUFFER → GAIN → EQ 4 BANDE ──┬── (1) CUE ──► CUE BUS ═══╗
 (phono Rev B                                       │                           ║
  futura)                                           ├── (2) FX SEND ──► ═══╗    ║
                                                    │       (EQ2+assign      ║    ║
                                                    │        +level)         ║    ║
                                                    └── (3) FILTER SEND ════►║────╫──► CORE FILTRO
                                                            ▲              ║    ║    (see §5-6: A o B)
                                                            ║ ritorno      ║    ║    + risonanza
                                                        FILTER RETURN ◄════╝    ║    + overdrive
                                                            │                   ║
                                                     METER DJ → FADER → OUT DRV ║
                                                            │                   ║
                                                            ▼                   ║
                                                        DJ BUS L/R ═════════════╬══► KILL bank 5 vie
                                                                                ║    + EQ creativo 5 bande
 MIC ──► MODULO MIC (preamp 30-60dB, no phantom, EQ2) ══════════════════════════╬══► + DRIVE + meter
                                                                                ║         │
 GENERIC MONO ──► MODULO SORGENTE (buffer hi-Z, gain, EQ2, mono→stereo) ════════╬══►      │
                                                                                ║         │
                          MODULO FX  ◄══════════════════════════════════════════╝         │
                          ┌───────────────────────────────────────────────┐               │
                          │ BUS 1..4 (summing virtuale) → pad → PEDALI OUT│               │
                          │ PEDALI IN (hi-Z ≥1MΩ) → gain → EQ2 → meter    │               │
                          │  → FADER ritorno → MASTER SUM                 │               │
                          │ MATRICE FEEDBACK: 3 reroute per ritorno       │               │
                          │  (pre-fader, VCA, no self-route) → BUS 1..4   │               │
                          └───────────────────────────────────────────────┘               │
                                                    │                                     │
                                                    ▼                                     ▼
                          MODULO MASTER       MASTER SUM ◄────────────────────────────────┘
                          ┌──────────────────────────────────────────────┐
                          │ SUMMING → [MASTER LEVEL VCA −∞..0..+6]       │
                          │    ├─► meter 20 segm + clip purple           │
                          │    └─► front ±18V → HV ±24V → XLR MASTER     │
                          │ BOOTH (pre-level) → level −∞..0 → XLR BOOTH  │
                          │ REC (pre-tutto) → buffer 0 dBu → REC OUT     │
                          │ MUTE controller + protezioni                 │
                          └──────────────────────────────────────────────┘

 CUE BUS ══► MODULO CUE/CUFFIE: somma CUE attivi → mix CUE/MASTER → amp cuffia → 2 uscite

 BACKPLANE: bus audio (DJ L/R, FX1-4 L/R, 5-WAY L/R, MASTER L/R, CUE L/R, filter send/return
 per canale) + bus controllo (CV 0-5V, logiche selettori) + potenza (±24, ±15, +5) + ground
 (analogue 0V, control GND, chassis) — separati fisicamente.
```

Nota: FX returns, mic e generic mono NON passano dal 5-way (locked, doc §3). Il 5-way
processa solo il DJ BUS.

## 2. Catena di un canale (zoom)

```
RCA L/R → protezione → buffer → GAIN (−∞..0..+10, detent) → EQ 4 bande (+6/−∞ cad.)
   → nodo di split (post-EQ):
       ├─► CUE (pre-fader) → switch → CUE bus
       ├─► FX SEND (pre-fader, pre-filter): EQ 2 bande → level −∞..0 → assign multipli S1-S4
       └─► dry → FILTER SEND → [modulo filtro] → FILTER RETURN
              → METER DJ (post-filter, pre-fader) → FADER (slider, linked ≤0,5 dB)
              → out driver ≤50Ω → DJ BUS
```

## 3. Cos'è un "core" filtro — da dove salta fuori il numero 8

- Un core SVF (state-variable filter) produce CONTEMPORANEAMENTE le uscite HP, BP e LP:
  il "selettore HPF/OFF/LPF" è solo un multiplexer che sceglie quale uscita prendere.
- La pendenza richiesta è 24 dB/ottava (4 poli) = DUE sezioni 2 poli in cascata per core.
- Ogni canale è STEREO: servono 2 core per canale (L e R, matched).
- Opzione B (documenti): 4 canali × 2 lati = **8 core mono** = 16 sezioni 2 poli.
  Ecco da dove veniva il mio "8" — non 8 filtri diversi, ma 4 filtri stereo.
- Opzione A (stile Xone/Sherman): 2 core stereo totali = **4 core mono** = 8 sezioni.

## 4. Come funziona il filtro dello Xone:92 (verificato)

Fonti: manuali ufficiali Allen & Heath e pagina prodotto (link a piè di documento).

- **DUE filtri stereo indipendenti** (VCF 1 e VCF 2), uno per lato del crossfader.
- Ogni filtro ha: selettore di tipo **HPF / BPF / LPF**, knob **FREQuency** (sweep),
  knob **RES** (risonanza/Q) grande, switch **FILTER ON**, e un **LFO** dedicato
  (depth, rate, tap-tempo, sync MIDI) che modula la frequenza ciclicamente.
- Ogni canale ha uno **switch di assegnazione a 3 vie** (sotto il knob dei bassi):
  **F1 / OFF / F2**. Più canali possono stare sullo stesso filtro.
- **VCF LINK 2-1**: il knob frequenza del Filtro 1 può pilotare anche il Filtro 2.
- Mk2 (2024): commutazione silenziosa, curva di controllo ottimizzata, risonanza estesa.
- Allen & Heath non pubblica pendenza/range esatti: il filtro va "a orecchio" (il che,
  detto di passaggio, è un buon argomento per fidarci delle nostre simulazioni più
  delle schede marketing).

In sintesi: **2 cervelli filtranti condivisibili, assegnabili per canale, ognuno con i
SUOI parametri indipendenti.**

## 5. Come funziona invece l'architettura dei tuoi documenti ("opzione B")

- **4 core dedicati** (uno per canale, stereo → 8 core mono), tutti nel modulo filtro.
- **UN solo set di controlli condivisi**: freq HPF, freq LPF, risonanza, overdrive →
  diventano CV (0-5 V) distribuiti a tutti i core.
- Ogni canale sceglie solo la MODALITÀ: HPF / OFF / LPF (selettore sul canale).
- Overdrive DOPO il filtro, prima del meter di canale.
- Conseguenza musicale: tutti i canali filtrati insieme "si muovono insieme"
  (stessa frequenza per tutti gli HPF, stessa per tutti gli LPF); risonanza e
  overdrive globali.

## 6. Confronto A vs B

| | **A — 2 core indipendenti (Xone/Sherman)** | **B — 4 core, controlli condivisi (documenti)** |
|---|---|---|
| Canali filtrabili insieme | fino a 2 gruppi (ogni gruppo può sommare più canali) | tutti e 4, sempre |
| Parametri | indipendenti per filtro: freq/modo/res/overdrive suoi | condivisi: 1 freq HPF, 1 freq LPF, 1 res, 1 overdrive per tutti |
| Workflow tipico | batteria su F1 in HPF-sweep E basso su F2 in LPF, contemporaneamente e indipendenti | sweep coerente su più canali; HPF+LPF insieme sui due knob ma uguali per tutti i canali in quel modo |
| Circuito | 4 core mono (8 sezioni 2 poli) | 8 core mono (16 sezioni) — il doppio |
| Tracking | facile: matching solo L/R dentro ogni core | difficile: 8 core sulla stessa CV → trim per core (voce 51) |
| Selettore sul canale | F1 / OFF / F2 | HPF / OFF / LPF |
| Overdrive | per filtro (come Sherman: ogni blocco ha il suo drive) | condiviso |
| Riferimenti reali | Xone:92/96, Sherman Filterbank — **i tuoi due riferimenti dichiarati** | originale della conversazione ChatGPT ("architecture correction") |
| Backplane/canali | IDENTICO in entrambe le opzioni: send/return stereo + 2 bit di selezione per canale. La scelta cambia SOLO l'interno del modulo filtro (fase 2) | idem |

## 7. Raccomandazione di Claude (non vincolante — decide Filippo)

**Opzione A**, per cinque motivi:
1. I tuoi due riferimenti sonori (Sherman Filterbank, Xone) sono esattamente macchine
   a 2 filtri indipendenti: la tua intuizione "pensavo fossero solo 2" coincide con la
   tua estetica dichiarata.
2. Metà del circuito: meno OTA, meno rumore, meno aree di PCB, meno punti di guasto.
3. Il tracking (voce 51/K2) diventa un problema piccolo: matching L/R dentro 2 core,
   invece di 8 core che devono inseguire la stessa CV.
4. Due filtri indipendenti = più espressione dal vivo (due sweep diversi
   contemporaneamente), che è ciò per cui lo Sherman è leggendario.
5. La scelta è confinata nel modulo filtro (fase 2): canali e backplane non cambiano,
   quindi è anche una decisione che resta economicamente reversibile fino a quel PCB.

**Quando invece ha ragione la B**: se il gesto che vuoi è "una manopola sola che muove
tutto il mix" (4 canali che spazzano insieme in modo coerente). Esiste anche una via
di mezzo: modulo B costruito modularmente, con 2 core popolati all'inizio (canali 1-2)
ed espansione a 4 in seguito.

## 8. Sulla richiesta "essere sicuro che tutto abbia senso prima delle PCB"

Concordato al 100%, ed è già regola di progetto (metodo: requisito → funzione di
trasferimento → topologia → componenti → **simulazione** → **prototipo su millefori** →
**misura** → revisione; nessun modulo va a PCB prima di aver superato simulazione e
prototipo). Questo documento fornisce il diagramma completo (destinato a SPECIFICA §2);
mancano ancora, per chiudere il cerchio del "tutto ha senso": (1) decisione A/B qui
sotto, (2) gain-staging sheet globale (voce 50), (3) compilazione SPECIFICA.md (voce 56).

## Fonti Xone:92

- Manuale utente Xone:92 Mk2 (PDF ufficiale): https://www.allen-heath.com/content/uploads/2024/10/Xone92-Mk2-User-Guide.pdf
- Manuale Xone:92 Limited Edition (PDF ufficiale): https://www.allen-heath.com/content/uploads/2026/07/Xone92-Limited-Edition-UG-iss_2.pdf
- Pagina prodotto: https://www.allen-heath.com/hardware/xone-series/xone92/
- Manuale Xone:92 (IT, mirror): https://www.dittasistema.it/wp-content/uploads/2015/09/Manuale-Allen-Heath-XONE-92.pdf
- Xone:96 User Guide (stessa architettura VCF): https://support.allen-heath.com/hc/en-gb/articles/43053562464017-Xone-96-User-Guide
- Dettagli pratici assign/resonance (community): https://www.reddit.com/r/Beatmatch/comments/1bjdyjd/xone_92_filters/ e https://forum.djtechtools.com/t/question-about-xone-92-filters/51474
- Nota Mk2 (Sonic State): https://sonicstate.com/amped/2024-10-10/popular-dj-mixer-gets-an-update/

## 9. ESITO della decisione (2026-09-18) — architettura B′

Filippo non ha scelto né A né B pure: ha descritto il pannello che vuole, e quel pannello
corrisponde a una variante di B (decisione 67):

- Sul canale: switch 3 posizioni **HPF / OFF / LPF** (BPF escluso)
- Sul modulo filtro: **6 knob** = HPF freq + HPF res + HPF drive | LPF freq + LPF res + LPF drive
- Un core dedicato per canale (4 stereo = 8 mono, stesso PCB) con trimming

```
PANNELLO MODULO FILTRO (B′):
┌────────────────────────────────────────────────┐
│  SEZIONE HPF          │        SEZIONE LPF     │
│  [FREQ] [RES] [DRIVE] │  [FREQ] [RES] [DRIVE]  │
│  10 Hz–1,5 kHz        │  500 Hz–20 kHz         │
└────────────────────────────────────────────────┘
   Ogni canale: switch HPF/OFF/LPF → segue i knob della sua sezione
```

Perché i core devono essere per-canale (e non 2 condivisi): la catena bloccata mette il
filtro PRIMA del fader e il meter DOPO il filtro — con 2 soli core condivisi i canali
dovrebbero essere sommati prima del filtro, e i fader individuali non controllerebbero
più il proprio segnale filtrato. Nello Xone infatti il filtro lavora su un submix
(post-fader): è l'unico modo di farlo con 2 core. La B′ mantiene invece il controllo
individuale pre-fader, al costo di 4 core.

HPF min: 10 Hz (decisione 68, derivata dal requisito infrasub, verifica in simulazione).
