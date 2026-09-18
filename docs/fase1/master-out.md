# FASE 1 — Modulo MASTER OUT: design circuitale v0.2

> **v0.2 (2026-09-18)**: integrate le risposte di Filippo alle 7 voci (§8): uscite
> universali per DSP/registratori standard, booth XLR, detent a unity, meter di
> precisione, rail low-noise confermati. La logica colori/zone del meter resta
> [EXPORT] (backlog ChatGPT) — la scala elettrica è già progettata indipendentemente.

> **Stato**: bozza di ingegneria. Le topologie sono candidate [PROVVISORIO]; nessun valore
> è congelato (regola 3 del progetto). Le scelte marcate [APERTO-F] aspettano Filippo.
> Deroga registrata: Filippo ha autorizzato l'avvio del design il 2026-09-18 in attesa
> dell'export ChatGPT; questa sezione (punto 21 della review) era già giudicata "solida".

## 1. Requisiti funzionali (richiami da 01-decisioni-bloccate)

- [BLOCCATO] MASTER LEVEL attivo −∞ → 0 dB (unity) → +6 dB, stereo-linked, tracking ≤ 0,25 dB, full CCW = mute pratico (voci 12, 38)
- [BLOCCATO] Meter DOPO il level: mostra il livello reale in uscita (voce 38)
- [BLOCCATO] 6 zone: blue → green → yellow → amber → red → purple; purple = clip detector vero (voce 43)
- [BLOCCATO] Uscita XLR L/R bilanciata attiva, Z out < 50 Ω ideale, capacità pulita ≥ +24 dBu, niente trasformatore, nessuna colorazione, protezione corto (voce 42)
- [BLOCCATO] BOOTH: presa da MASTER SUM prima del level, −∞ → 0 dB, linked, il master non lo influenza (voce 39)
- [BLOCCATO] REC: presa prima di tutto, nessun controllo, ≈ 0 dBu al nominale → nel nostro caso con attenuazione fissa adatta allo Zoom (voci 40, 41)
- [BLOCCATO] Buffer dedicato per ogni uscita, mai splittati (voce 11)
- [BLOCCATO] Mute power-on/power-off obbligatorio; protezioni DC/corto/RF; protezioni ≠ dinamica (voci 10, 46)
- [BLOCCATO] Banda 8 Hz–35 kHz con filtro OFF; nessun filtraggio aggressivo in uscita (voce 44)
- [BLOCCATO] Livelli: nominale 0 dBu (0,775 Vrms); +24 dBu = 12,28 Vrms = 17,4 Vpicco = 34,7 Vpp come requisito DI SISTEMA sull'uscita (voci 7, correzione review 2)

## 2. Diagramma a blocchi del modulo

```
(dal backplane: MASTER SUM bus, stereo)
        │
        ├────────────────────────────┬──────────────────────────┐
        │                            │                          │
  [A] IN BUFFER x2            [B] BOOTH BUFFER x2         [C] REC BUFFER x2
        │                            │                          │
        │                     [B2] BOOTH LEVEL            [C2] ATTENUATORE
        │                        (VCA, −∞→0 dB)             FISSO (per Zoom)
        │                            │                          │
  [A2] MASTER SUMMING x2             │                   [C3] REC MUTE
   (opzionale, vedi §3.1)            │                          │
        │                            │                          │
  [D] MASTER LEVEL x1 stereo         │                          │
   (VCA doppio, −∞→+6 dB,            │                          │
    un solo controllo CV)            │                          │
        │                            │                          │
        ├──► [E] METER PICKUP        │                          │
        │     (peak L/R + clip det.) │                          │
        │                            │                          │
  [F] OUT FRONT x2            [B3] BOOTH DRIVER x2              │
   (OPA1612, ±18 V)              (±18 V)                        │
        │                            │                          │
  [G] STADIO USCITA HV x2     [B4] BOOTH MUTE            [C4] USCITA REC
   (discreto, ±24 V,                 │                          │
    composite con [F])         [B5] USCITA BOOTH           (TRS/mini-jack
        │                            │                    [APERTO-F])
  [H] MUTE + PROTEZIONE        (XLR o TRS [APERTO-F])            │
        │                                                        │
  [I] XLR MASTER OUT L/R                                         │
                                                                 │
  [L] MUTE CONTROLLER (analogico: supervisore rail + timer) ─────┘
      comanda [H], [B4], [C3]

  [M] PSU LOCALE: ±24 V main in → ±24 V filtrato (stadio HV),
      ±18 V LDO (front/VCA/booth), ±15 V ultra-low-noise
      (summing/meter/sum), +5 V control (LED/logica mute)
```

Ogni ramo ha il suo buffer: il vincolo [BLOCCATO] "mai un buffer unico splittato" è rispettato alla lettera — [A], [B], [C] sono tre ingressi distinti dello stesso bus.

## 3. Design per stadio

### 3.1 [A] In buffer + [A2] Master summing

**Dubbio architetturale da risolvere con l'export**: la review elenca "master summing resistor/gain values" tra gli aperti della sezione master, quindi la somma finale vive qui. Ma quante sorgenti arrivano al modulo master via backplane?

Ipotesi di lavoro [PROVVISORIO], coerente con le voci bloccate (DJ bus → 5-way → master; FX/mic/generic → master):
- 8 ingressi di summing per canale (5-way L/R, fino a 4 ritorni FX stereo o 2 + spare, mic, generic, 2 spare)
- **Summing inverting** su OPA1612: R_in = 20 kΩ ciascuno, R_f = 20 kΩ (unity), C_f = 10 pF (stabilità/RF)
- Nodo summing in massa virtuale: crosstalk tra sorgenti trascurabile — è il motivo per preferire l'inverting al passivo su un backplane
- Ingressi non usati: terminati a massa con 20 kΩ (il resistore di summing resta, ingresso a 0 V)
- I gain di contribuzione stanno a monte (fader di canale, level ritorni FX): il summing è unity, così "MASTER SUM ≈ 0 dBu con programma a fader unity" resta vero

Alternativa da valutare se l'export dice che la somma è già fatta nel modulo 5-way: [A2] diventa un buffer di ingresso puro (unity, OPA1612 non-inverting, Z_in ≥ 20 kΩ, Z_out < 50 Ω).

**Livelli nel nodo**: nominale 0 dBu; picchi programma attesi fino a +16 dBu (4,9 Vrms); dominio ±15 V (capability sine ≈ +19 dBu con OPA1612 su ±15 V e carico leggero — margine ~3 dB, da verificare in simulazione).

### 3.2 [D] MASTER LEVEL — il cuore del modulo

**Topologia raccomandata [PROVVISORIO]: VCA elettronico stereo pilotato da UN SOLO controllo.**

Motivazione sul requisito bloccato tracking ≤ 0,25 dB:
- pot doppio gang meccanico: il tracking dipende dall'accoppiamento delle piste — ALPS RK27 dichiara tipicamente ±1-2 dB tra sezioni; NON rispetta il requisito
- VCA doppio con singola tensione di controllo (CV): i due canali seguono la stessa legge elettrica — tracking determinato dal matching dei die, tipicamente ≤ 0,1 dB nella famiglia THAT 218x. È l'unica via realistica per ≤ 0,25 dB con controllo manuale

**Candidato**: THAT 2181 (doppio VCA low-distortion, max ±18 V) oppure 2× THAT 2180 (singoli) sulla stessa CV se il 2181 risultasse irreperibile. [PROVVISORIO — verificare disponibilità, prezzo e legge dB/V esatta sui datasheet prima dell'ordine]

**Catena del controllo** (mono, un pot per entrambi i canali):
```
pot lineare 10 kΩ → generatore CV (mappa rotazione → legge dB voluta)
→ CV buffer → control input THAT 2181 (canali A+B in parallelo elettrico)
```
- Legge target: −∞ (≤ −90 dB) a full CCW · 0 dB (unity) al ~75-80% della corsa · +6 dB a fine corsa
- Il tratto sotto unity occupa la maggior parte della corsa (uso normale), +6 dB è trim fine in cima — coerente con "positive gain only above unity"
- Detent meccanico a unity: **SI [BLOCCATO-F 2026-09-18]**. Nota: l'hardware di tutte le manopole (marca/modello pot) si rivede globalmente in un secondo momento — qui conta solo che il pot del master abbia il detent

**Dominio di alimentazione VCA**: ±18 V locali (massimo assoluto THAT 218x; verificare raccomandazione datasheet — se indica ±16,8 max operativi, il rail locale diventa ±16 V). Con +6 dB su picchi +16 dBu in ingresso, l'uscita VCA arriva a ~+22 dBu: il dominio ±18 V è necessario, il ±15 V non basterebbe.

### 3.3 [F]+[G] Stadio d'uscita master — dove vive il +24 dBu

Nessun integrato commerciale in catalogo comodo garantisce +24 dBu sustained (servono ≥ 17,4 Vpicco di swing, cioè rail ≥ ±20 V reali):
- THAT 1646 / 1606 (balanced line driver): max ±18 V → swing insufficiente con margine
- OPA1612 e simili: max ±18 V, swing tipico ±13-14 V su carico → ~+22 dBu max, marginale

**Topologia raccomandata [PROVVISORIO]: amplificatore composito.**
```
OPA1612 (errore/input, ±18 V)
   +
stadio diamond discreto in class AB (±24 V, dentro il feedback globale dell'OPA1612)
```
- Il diamond buffer (coppia complementare NPN/PNP, es. MJE340/MJE350 o BD139/BD140 [PROVVISORIO], bias class AB ~10-15 mA con diodi/LED + moltiplicatore Vbe, resistenze di emettitore 10-100 Ω)
- Nel feedback globale: THD dominata dall'OPA1612 (< 0,001% realistico), Z_out in anello < 1 Ω → soddisfa "< 50 Ω ideale" con due ordini di grandezza di margine
- Swing atteso su ±24 V: ~±21 V = **+25 dBu sine sustained** → requisito +24 dBu con margine ~1 dB [PROVVISORIO, da misurare]

**Bilanciamento**: driver attivo a uscita incrociata (hot = segnale, cold = −segnale):
- hot: composito non-inverting unity
- cold: composito inverting unity (resistenze matched 0,1% sul percorso)
- CMRR dell'uscita limitato dal matching delle resistenze: 0,1% → ~60 dB, adeguato per linea

**Protezioni allo stadio**:
- Limitazione di corrente: resistenze di emettitore + clamp Vbe sui drive (corrente di corto < 60 mA per ramo [PROVVISORIO])
- Safe area: i MJE340/350 reggono il corto verso massa con Re = 47 Ω e bias basso — da verificare in simulazione termica semplificata
- DC: **servo DC** (integratore lento in anello sull'OPA1612, offset d'uscita < 5 mV) invece di condensatori in serie al segnale — obbligatorio con banda 8 Hz (un cap di blocco a 8 Hz su 10 kΩ sarebbe ~2 µF: colore e ingombro)
- Relay di mute in serie all'XLR (contatti dorati, segnale < 5 V: G6K/G5V o equivalenti)

**Protezione al connettore [I]**:
- R serie 47 Ω + bead ferrite + 100 pF verso chassis (polo a ~30 MHz: invisibile sotto i 35 kHz)
- TVS bidirezionale low-capacitance sulla linea (es. serie PESD/CDSOT a bassa capacità) per ESD
- Pin 1 XLR → chassis con rete RC di lifting (1 kΩ // 4,7 nF in serie al legame diretto, punto di star grounding del modulo — coerente con la questione aperta 21 sul grounding)

**Compatibilità d'uscita [BLOCCATO-F 2026-09-18]**: nessun DSP specifico di riferimento — l'uscita deve lavorare con la maggior parte dei DSP/processor standard. Traduzione tecnica: XLR bilanciato, nominale 0 dBu, capace di pilotare senza sforzo ingressi pro +4 dBu (che hanno trim), Z out < 50 Ω, stabile con cavi lunghi. La capacità ≥ +24 dBu già progettata copre qualunque ingresso standard.

### 3.4 [B] BOOTH

- Buffer d'ingresso dedicato ([B], OPA1612 unity, ±18 V — picchi +16 dBu ok)
- BOOTH LEVEL: stesso approccio del master — VCA con singola CV, range −∞ → 0 dB (solo trim negativo, il requisito non chiede +6). Opzione economica: 1× THAT 2180 singolo stereo-linked... serve doppia sezione → un 2181 dedicato o metà di un secondo 2181 [PROVVISORIO — dipende da cosa si trova]
- Driver d'uscita: qui il +24 dBu NON è richiesto (max ~0 dBu, picchi +16-18 dBu): basta OPA1612 + diamond piccolo su ±18 V, o anche OPA1612 diretto su carico ≥ 2 kΩ con corrente di picco < 5 mA
- Connettore: **XLR bilanciato [BLOCCATO-F 2026-09-18]** — coerente col master, robusto, driver bilanciato dedicato

### 3.5 [C] REC (verso Zoom)

- Buffer dedicato unity ([C], OPA1612, ±15 V sufficienti: livello ≤ nominale)
- **Requisito aggiornato [BLOCCATO-F 2026-09-18]**: compatibile con la maggior parte dei registratori standard (Zoom o equivalente), non tarato su un modello specifico
- Connettore: **TRS jack**, cablaggio unbalanced-compatible (tip = hot, sleeve = ground, ring = cold collegato a sleeve: funziona sia con cavi TS che TRS)
- Attenuatore fisso a resistenze (precisione 0,1%): da 0 dBu a **−10 dBV** (0,245 Vrms), pad ≈ −10 dB [PROVVISORIO]: è il livello line-in tipico dei registratori portatili; gli ingressi pro con trim lo gestiscono comunque. Opzione: jumper interno a 2 posizioni (−10/−20 dB) per registratori molto sensibili — costo zero, si decide al prototipo
- Niente limiter (bloccato): se il mixer viene spinto a +18 dBu interni, il registratore prende un segnale caldo ma l'attenuatore lo riporta nel suo range; la responsabilità del gain staging resta a monte, come da filosofia

### 3.6 [E] Metering master — precisione massima [BLOCCATO-F 2026-09-18]

Requisito di Filippo: **«il più preciso possibile»**. Traduzione tecnica:

**Catena per canale**:
```
pickup post-VCA (prima del [F]) → precision peak detector (opamp + diodi in
feedback, C_hold 1 µF, attacco < 1 ms) → 2× LM3915 in cascata (bar mode)
→ 20 LED per canale, passi 3 dB → scala −42 … +18 dBu [PROVVISORIO]
```
- **Scala**: 20 segmenti per canale, 3 dB a segmento — è la risoluzione nativa dell'LM3915 (driver logaritmico classico per meter, 10 segmenti per chip, due chip in cascata per canale). È il massimo ottenibile restando 100% analogici (niente ADC/display digitali, per coerenza col progetto).
- **Accuratezza**: ±0,5-1 dB per segmento tipica dell'LM3915 + tolleranza delle referenze [PROVVISORIO — verificare a datasheet e calibrare al banco con tone a livelli noti].
- **Ballistica**: attacco < 1 ms (vero peak), decay ~ −20 dB/s con trimmer sul modulo (sperimentabile senza rifare il PCB), hold del picco.
- **Clip detector purple**: comparatore indipendente (LM339) sull'uscita del diamond con soglia = rail − 2 V (≈ ±22 V), latch ~0,5 s con autoreset. Scatta SOLO quando lo stadio d'uscita arriva davvero al limite, non "quando l'ultimo LED si accende" — implementa la correzione 20 della review.
- **Colori e zone [EXPORT]**: la logica a 6 zone (blue → purple) è nel backlog con ChatGPT. La mappatura colori sulla scala a 20 segmenti si decide con l'export. La tabella sotto resta segnaposto per le SOLE soglie elettriche provvisorie:

| Zona (provvisoria) | Intervallo | Significato |
|---|---|---|
| blue | < −20 dBu | poco segnale |
| green | −20 … −6 dBu | safe (programma normale intorno allo 0) |
| yellow | −6 … 0 dBu | loud |
| amber | 0 … +6 dBu | hard |
| red | +6 … +18 dBu | extreme |
| purple | clip detector indipendente | clipping reale allo stadio d'uscita |

- Conseguenza pratica sui LED: 20 segmenti × 2 canali + clip = ~42 LED sul pannello del modulo master. Con bar mode e LED ad alta efficienza il consumo resta < 150 mA a +5 V [PROVVISORIO]. Se il pannello diventa troppo fitto, l'alternativa è 10 segmenti per canale (1 chip, 3 dB, range −12…+18): stesso circuito, metà LED — si decide con il layout del pannello (che è di Filippo).

### 3.7 [L] Mute controller (power-on/power-off)

Tutto analogico, niente MCU (coerenza col progetto):
- Supervisore: partitore sui ±24 V → comparatore con isteresi → "rails OK"
- Power-on: timer RC (~1,5-2 s) poi eccita i relay — il bang di accensione non arriva mai ai connettori
- Power-off: l'energia immagazzinata nei bulk cap del modulo alimenta il controller ancora per ~50-100 ms tramite diodo di hold-up; al calo dei rail il relay apre in < 10 ms — il pop di spegnimento resta dentro
- Stesso segnale pilota [H], [B4], [C3] (relay indipendenti per ogni uscita: un guasto non le ammutolisce tutte... anzi sì le ammutolisce, ma è il comportamento sicuro)

### 3.8 [M] PSU locale del modulo

| Rail | Da | Per | Regolatore candidato [PROVVISORIO] | Corrente stimata |
|---|---|---|---|---|
| ±24 V filtrato | main | stadio HV uscita [G] | ferrite + bulk locale (1000 µF + 100 nF) | ~40 mA picco per canale |
| ±18 V | main | [F] front, VCA level, booth driver | LM317/LM337 o LDO equivalenti (dropout ~3 V ok) | ~60-80 mA |
| ±15 V ultra-low-noise | ±18 | summing [A2], meter [E], REC [C] | LT3045/LT3094 (0,8 µVrms) — o 78L15/79L15 nella variante economica | ~40-60 mA |
| +5 V control | main o +12 control bus | LED, logica mute, comparator | LDO locale 78L05 | ~100 mA (LED dipendenti) |

Budget termico modulo: ~8-12 W dissipati → nessun problema con le alette dei TO-220/LDO in SMD/through-hole su PCB normale. [PROVVISORIO, da ricalcolare a componenti scelti]

**Scelta di qualità [APERTO-F]**: i rail ±15 V "audio puri" con LT3045/LT3094 costano ~8-10 € in più a modulo ma sono l'assicurazione rumore più economica del progetto. Raccomandati sul summing e sul meter; LM317 basta altrove.

## 4. Tabella livelli del modulo (level plan)

| Nodo | Nominale | Max programma atteso | Capability sine | Dominio |
|---|---|---|---|---|
| Ingresso bus (backplane) | 0 dBu | +16 dBu | — | — |
| Uscita summing [A2] | 0 dBu | +16 dBu | +19 dBu | ±15 V |
| In/Out VCA master [D] a unity | 0 dBu | +16 dBu | — | ±18 V |
| Uscita VCA a +6 dB | +6 dBu | +22 dBu | ~+24 dBu | ±18 V |
| Ingresso stadio HV [G] | 0 dBu | +22 dBu | — | ±18 V |
| Uscita XLR | 0 dBu | dipende dal master level | **+25 dBu** | ±24 V |
| Booth max | 0 dBu | +16 dBu | +20 dBu | ±18 V |
| REC out | −10 dBV | ~+8 dBV (raro) | — | ±15 V |

Conseguenza onesta da registrare: a MASTER LEVEL a +6 dB con programma già a +16 dBu interni, il VCA su ±18 V è al limite. È voluto dalla filosofia (chi spinge sa di spingere), ma va misurato in simulazione dove esattamente inizia il clipping del VCA e quanto è morbido. Se è brutto, le opzioni sono: (a) summing a nominale più basso (−6 dB interni e +6 al master, invariato il rumore relativo), (b) VCA su rail dedicato più alto se il datasheet lo permette, (c) accettare e documentare. → **Voce nuova nelle questioni aperte.**

## 5. Componenti candidati (per la BOM di massima)

| Ruolo | Candidato | Note | Prezzo unitario stimato |
|---|---|---|---|
| Op-amp audio summing/buffer/meter | OPA1612AID (dual) | ±18 V max, 1,1 nV/√Hz, THD ~0,00008% — verificare Iq a datasheet | ~4-6 € |
| VCA master + booth level | THAT 2181 (dual) o 2× 2180 | verificare esistenza/disponibilità 2181; in subordine SSM2164/SSM2122 (Analog Devices, legacy) | ~5-8 € |
| Transistor diamond output | MJE340/MJE350 o BD139/BD140 | TO-126, 500 mA — abbondanti per linea | ~0,5-1 € la coppia |
| Coppia d'ingresso diamond (se serve matching) | KSC1845/KSA992 | sostituti moderni dei classici Toshiba 2SC2240/2SA970 | ~1 € la coppia |
| Comparator clip purple | LM339 ×1 | quad, open-collector | ~0,5 € |
| Scale meter | LM3915 ×4 | 10 segmenti log 3 dB cad., 2 in cascata per canale, bar mode | ~1-2 € cad |
| Relay mute | Omron G6K-2 o G5V-1 | segnale, contatti dorati | ~2-3 € ×3 |
| Regolatori low-noise | LT3045 + LT3094 | **CONFERMATI [BLOCCATO-F]** per summing, CV del VCA e meter | ~4-5 € cad |
| Regolatori standard | LM317/LM337, 78L05 | | ~1 € |
| XLR femmina pannello ×4 | Neutrik NC3FAH o equivalente | master L/R + booth L/R; pin1 → rete RC → star ground modulo | ~3-4 € cad |
| TVS/connettore | PESD5V0 low-cap | ESD | ~0,5 € |

**Stima BOM modulo master out: ~60-90 €** (esclusi PCB, connettori backplane, manopole). [PROVVISORIO]

## 6. Simulazioni da eseguire (LTspice) — prima di qualunque ordine

1. Summing 8 ingressi: THD+N vs livello (target: < 0,005% a +16 dBu), noise residuo in uscita, interazione R_in/C_f con banda 8 Hz–35 kHz (±0,5 dB)
2. Composite amplifier [F]+[G]: swing massimo su 10 kΩ e 600 Ω, THD a +24 dBu/1 kHz e a 35 kHz, margine di fase con carico capacitivo (cavo 100 m ~ 10 nF), comportamento di corto
3. VCA THAT 218x: legge dB/V reale, tracking canali, THD vs livello a +18 dBu, margine prima del clipping a +6 dB di trim
4. Peak detector: ballistica (attacco/decay) e errore di lettura a 8 Hz e 35 kHz
5. Mute controller: tempi di apertura/chiusura relay con modello di PSU (bulk cap reali)
6. PSRR di fine catena: quanto rumore/residuo dei rail ±18/±24 arriva all'XLR (target: contributo PSU < −100 dBu)

## 7. Budget di rumore — impostazione (non risultati)

Metodo corretto imposto dalla review (correzione 13): per stadio, non "−90 dBu globale".
- Catena dominante: summing (R equivalenti ~2,5 kΩ visti dall'OPA1612 → ~4-5 nV/√Hz termici + 1,1 nV dell'opamp) → VCA (218x: rumore in banda audio da verificare a datasheet, tipicamente dominante nel percorso) → front → HV (il diamond dentro il feedback aggiunge poco)
- Stima grezza [PROVVISORIO]: −92…−86 dBu A-wtd residuo all'XLR a unity, con i rail low-noise; senza LT3045/3094 aggiungere 2-4 dB
- Il verdetto arriva dalla simulazione 1+3+6, non da questa riga

## 8. Risposte di Filippo (ricevute 2026-09-18) — esito

| # | Domanda | Risposta | Conseguenza sul design |
|---|---|---|---|
| 1 | DSP a valle | Irrilevante: deve lavorare con la maggior parte dei DSP standard | XLR universale: bilanciato, 0 dBu nom, pilota ingressi pro +4 dBu, Z out < 50 Ω (§3.3) |
| 2 | Zoom per REC | Uguale: compatibile con la maggior parte dei registratori | REC su TRS unbalanced-compatible, pad −10 dBV, jumper −10/−20 opzionale (§3.5) |
| 3 | Connettore booth | XLR | Booth bilanciato su XLR (§3.4) |
| 4 | Detent unity | Sì; hardware di tutte le manopole da rivedere dopo | Pot con detent a unity; selezione hardware rimandata a sessione dedicata (§3.2) |
| 5 | Ballistica/LED | Il più preciso possibile | 20 segmenti/canale a passi 3 dB, LM3915 in cascata, attacco < 1 ms (§3.6) |
| 6 | Rail LT3045/3094 | Sì | Confermati su summing, CV VCA, meter (§3.8, §5) |
| 7 | Soglie/colori zone | La logica colori è nel backlog con ChatGPT | [EXPORT]: mappatura colori da definire sull'export; scala elettrica già fatta (§3.6) |

Restano utili ma NON bloccanti: modello del DSP e del registratore quando ci saranno, per la calibrazione finale al banco.

## 9. Prossimi passi

1. [FATTO 2026-09-18] Risposte di Filippo integrate → questo documento è v0.2
2. Simulazioni LTspice §6 (i file `.asc` versionati in `sim/master-out/`) — primo candidato: composite amplifier §3.3 (è il cuore elettrico del modulo)
3. Alla chiusura dell'export ChatGPT: verifica che questa sezione non contraddica decisioni prese là (in particolare: chi fa il summing, standard I/O del backplane, posizione esatta del meter, logica colori)
4. Solo dopo: schema elettrico definitivo e PCB del modulo

---

## ADDENDUM 2026-09-18 — correzione REC (decisione 63)

REC OUT: **0 dBu nominali fissi** («la cosa più semplice e standard»), nessun controllo utente. I pad solder-only 0/−10/−20 dB sul PCB (accesso tecnico) sostituiscono il jumper utente proposto in §3.5. Il resto della v0.2 resta valido; gli status doc confermano il master meter come "most precise meter" (compatibile con la scala 20 segmenti, decisione 53).
