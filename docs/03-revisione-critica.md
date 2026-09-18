# 03 — Revisione critica dei documenti di stato ChatGPT (2026-09-18)

> Oggetti analizzati: `docs/export-chatgpt/status_rev2_2026-09-18.pdf` (7 pagg, "Rev 2",
> sintesi + design phono Rev A) e `docs/export-chatgpt/documento-senza-titolo.docx`
> (39 sezioni, status completo + addendum phono). Entrambi datati 18/09/2026, origine
> ChatGPT confermata (firma C2PA "OpenAI Media Service" nel PDF).
> Verifica incrociata contro: `00-resoconto`, `01-decisioni-bloccate`, i design di fase 1.

## 1. Verdetto sintetico

**Nessuna allucinazione grave trovata. La matematica è corretta. Le citazioni sono vere.
I due documenti però si contraddicono tra loro sul phono (Rev A), e contraddicono
istruzioni recenti di Filippo sull'ordine di costruzione.** Il materiale è utilizzabile
come base autorevole, con le correzioni di questo documento.

## 2. Verifica fatti e citazioni (caccia alle allucinazioni)

| Affermazione | Esito |
|---|---|
| OPA1654: JFET, ~4,5 nV/√Hz a 1 kHz, GBW 18 MHz, unity-stable, max ±18 V | VERO — datasheet TI SBOS492 confermato (ti.com/product/OPA1654) |
| TI AN-1651 / SNAA046A "Keeping Up with the Expanding Demands of High-Performance Audio" | VERO — esiste (ti.com/lit/pdf/snaa046a, National/TI 2007, sezione RIAA/"Curcio") |
| audioXpress PhL-100: MM phono, primo stadio 21,3 dB, 75 µs passivo, 318/3180 attivi, ~42 dB totali | VERO — articolo "You Can DIY PhL-100" confermato su audioxpress.com; il chip citato (OPA1642) non è confermato negli estratti ma è plausibile (stessa famiglia TI) — rischio basso |
| Tabella livelli dBu→V (0/+4/+10/+18/+24) | MATEMATICAMENTE CORRETTA (0,775 Vrms × 1,414 ecc., verificato ogni riga) |
| RIAA RC: R=1/(2πfC), C=10 nF → 227 k/63,7 k/15,9 k/3,18 k | CORRETTO |
| SVF: C=4,7 nF → gm 0,59 µS @20 Hz / 0,59 mS @20 kHz, range 1000:1 | CORRETTO (come stima d'ordine) |
| 4 canali correlati a 0 dBu → +12 dB sul bus | CORRETTO |
| Costanti RIAA 3180/318/75 µs | CORRETTE |
| Driver PA (18 Sound 18LW2400, 12MB700, ND1460), amp Crown XLi800, CVR D-series | Marche/modelli reali; "HD15 15MB1000" e "Mogale Super Scooper" non verificabili da qui — sono hardware di Filippo, chiedere conferma a lui |

## 3. Contraddizioni trovate

### 3.1 Tra i due documenti (phono Rev A) — LA PIÙ IMPORTANTE

| Parametro | DOCX (addendum) | PDF (Rev 2, §6) | Raccomandazione |
|---|---|---|---|
| Gain primo stadio | 20× = **26,0 dB** (19,0 k/1,00 k) | **21,3 dB** (17,0 k/1,60 k) | **PDF**: cita il design PhL-100 misurato (±0,1 dB), e 21,3 dB sta nel range "20-25 dB" che lo stesso DOCX §7 indica; 26 dB è FUORI da quel range |
| Capacità selezionabili | 0/100/220/330 pF | 0/47/100/150 pF | **PDF**: con ~100-150 pF di cavo, il totale resta nella finestra classica 100-300 pF; la scala DOCX (fino a 330 + cavo) sfora |
| Gain totale 1 kHz | §7 dice 35-40 dB; addendum dice 42 dB | 40-42 dB, raccomanda ~42 | **PDF** (42 dB coerente con 5-8 mV delle testine DJ + GAIN di canale a unity) |

Nota: entrambi i set di resistori sono internamente coerenti (1+19/1 = 20 = 26,0 dB;
1+17/1,6 = 11,625 = 21,3 dB). Non è un errore di calcolo: sono due revisioni diverse.
Il PDF è etichettato "Rev 2" ed è più curato → **assumere il PDF come autorevole sul phono**,
salvo parere contrario di Filippo.

### 3.2 Tra documenti e istruzioni recenti di Filippo

- **Build sequence**: PDF §16 passo 1 = "DJ channel completo INCLUSO il blocco phono";
  Filippo il 2026-09-18 ha deciso "no phono per ora" (decisione 56). Inoltre Filippo
  vuole master-out presto (fase 1), i documenti lo mettono al passo 5.
- **REC out**: documenti = "≈ 0 dBu nominale fisso"; il nostro design master-out v0.2 =
  pad −10 dBV per compatibilità registratori. Proposta di sintesi: nominale 0 dBu
  (come da documenti) + jumper sul PCB 0/−10/−20 dB per registratori sensibili.

### 3.3 Tra documenti e nostri design di fase 1 (CDJ v0.1 — da revisionare)

| Voce | Nostro CDJ v0.1 | Documenti (più recenti) | Esito |
|---|---|---|---|
| Canale stereo/mono | assunto stereo [EXPORT] | **4 canali stereo identici** (LOCKED) | confermato stereo, dubbio chiuso |
| Gain | trim −10…+10 dB proposto | **−∞ → 0 → +10 dB, detent a 0, linked ≤0,5 dB** | vince il documento |
| EQ boost | +9 dB proposto | **−∞ → 0 → +6 dB (locked behaviour)** | vince il documento |
| EQ freq | 100/300/1,2k/8k [PROVVISORIO] | 70/250/1k/5k proposti (LOW/LOW-MID/MID-HIGH/HIGH) | baseline = documento, review con Filippo resta aperta |
| EQ tracking | non specificato | ≤0,25 dB L/R (solo PDF) | nuovo requisito — implicazione: pot doppi di qualità o celle per canale accoppiate |
| Assignment FX | ipotizzato 1-of-4 | **multiple simultanee, switch analogici di precisione (JFET scartati)** | vince il documento, nostro dubbio chiuso |
| Interfaccia filtro | ipotizzato send/return a modulo centrale | **filter core PER CANALE, solo i controlli condivisi** (CV dal modulo controlli) | CAMBIO GRANDE: il canale contiene SVF 4 poli ×2 + risonanza + overdrive + meter |
| CUE | post-EQ (assunto) | post-EQ / pre-filter / pre-fader (LOCKED) | confermato |
| Meter di canale | solo clip-warn LED | **meter DJ completo post-filter/overdrive pre-fader, peak con persistenza, calibrazione identica tra canali** | nostro design da aggiornare |
| Fader | pot + buffer | conduttivo-plastica DJ-style, stereo linked ≤0,5 dB, buffer ≤50 Ω | compatibile, specifica più precisa |

### 3.4 Artefatti e anomalie nei documenti

- L'addendum DOCX contiene testo di interfaccia ChatGPT incollato per sbaglio
  («It seems like I can't do more advanced data analysis right now...»): è rumore, non contenuto.
- L'addendum DOCX afferma «I also saved these decisions as part of the ongoing project
  specification»: esiste una "project specification" dentro ChatGPT che NON è in questi
  due file? Da chiedere a Filippo (principio di proprietà: tutto deve vivere qui).
- I documenti NON sono l'export completo della conversazione: sono sintesi consolidate.
  Molte voci [EXPORT] restano tali finché non arriva la storia completa (o finché
  questi documenti non sono dichiarati sufficienti).
- Sloppy minore: «≥ −90 dBu noise» e «≥ −100 dB isolation» usano il verso sbagliato della
  disuguaglianza (il rumore deve essere ≤ −90 dBu). Si intende il target giusto, ma nella
  specifica consolidata va scritto correttamente.

## 4. Parti critiche emerse (ingegneria, non contraddizioni)

- **K1 — Il canale DJ NON è un modulo semplice.** Con i filter core per canale, ogni
  canale contiene: front-end line (e phono in futuro), gain, EQ 4 bande stereo-linked,
  2× SVF 4 poli (L/R) con risonanza auto-oscillante, overdrive non lineare, meter,
  fader. È di fatto il modulo più denso del mixer. Conseguenze: (a) il build-order
  "parto da un canale semplice" non esiste — va spezzato in sotto-fasi; (b) il layout
  deve tenere il front-end phono lontano da OTA/overdrive/LED/meter (gli stessi
  documenti lo prescrivono per il phono); (c) costo e area PCB per canale alti.
- **K2 — Tracking dei filter core tra canali.** 8 core SVF pilotati dagli STESSI CV:
  se i core dei canali 1 e 3 differiscono del 5% a parità di CV, con due canali aperti
  sullo stesso filtro si sentono due frequenze diverse. I documenti non danno una
  specifica di tracking per i core (es. ±2% sulla frequenza a CV uguale). Va aggiunta:
  trimming per core (trimmer o resistori di calibrazione) + CV bufferizzati e distribuiti
  a stella. Voce nuova nelle questioni aperte.
- **K3 — Headroom del bus FX.** "≈12 contributori stereo per bus" a unity: somma
  correlata worst-case = +21,6 dBu → oltre la capability sine di un dominio ±15 V
  (~+19 dBu). Realistico (incorrelato) +10,8 dB, ma i loop di feedback possono
  accumulare. Il modulo FX deve fare il calcolo del worst-case e decidere: resistori di
  injection calibrati per contribuzione < unity, o dominio ±18 V per il summing bus.
- **K4 — Regola di gain staging sui ritorni FX.** Return gain fino a +20 dB con
  tolleranza d'ingresso +18 dBu → richiesta teorica di +38 dBu interni: impossibile in
  ogni dominio. Serve una regola esplicita: livello_in × gain ≤ max_dominio, con
  avviso nelle istruzioni d'uso. Non è un errore del documento (che parla di range),
  ma la regola non è scritta: va scritta.
- **K5 — Overdrive: "recovery ≥ +24 dBu where practical"** su quali rail? Se lo stadio
  di recovery vive a ±15 V non può arrivare a +24 dBu. Stesso family del nostro dubbio
  sul VCA del master (questione 31): serve la mappa dei domini di tensione per gli
  stadi nonlinear, da decidere in fase 2.
- **K6 — EQ stereo tracking ≤0,25 dB**: con pot meccanici doppi è difficile (±1-2 dB
  tipici); come per il master level, la via realistica è celle a contribuzione con
  CV unica (VCA/OTA per banda stereo-linked) oppure pot doppi selezionati + trim.
  Implicazione di costo e complessità da valutare nel design EQ.
- **K7 — Il meter DJ "identical calibration across channels"** implica una procedura di
  calibrazione al banco per canale (trimmer o matched components): va prevista nel design.

## 5. Domande che i documenti stessi lasciano a Filippo (PDF §19)

1. V1 solo MM? (o anche MC high/low output)
2. Capacità: fissa 100 pF o selezionabile internamente 0/47/100/150 pF?
3. Gain 1 kHz: congelare 40 o 42 dB? (raccomandazione documento: ~42)
4. Loading: solo tecnico (solder jumper) o selettore accessibile dal pannello posteriore?

## 6. Voci dei documenti che CHIUDONO nostre questioni aperte

- 41 (stereo/mono canale) → CHIUSA: stereo locked
- 42 (interfaccia filtro) → CHIUSA: filter core per canale, controlli condivisi via CV
- 43 (assignment FX) → CHIUSA: multiple simultanee, precision analogue switch
- 44 (punto CUE) → CHIUSA: post-EQ / pre-filter / pre-fader
- 45 (boost EQ) → CHIUSA: +6 dB (locked behaviour)
- 46 (gain canale) → CHIUSA: −∞→0→+10 dB detent (supersede il nostro trim ±10)
- 28 (vie dell'impianto) → CHIUSA: SUB 20-90, KICK 90-350, MID 350-1.2k, HIGH 1.2-3.5k, SUPER HI 3.5-20k; driver elencati in §15 del DOCX (da conferma di Filippo su KICK e SUPER HI)
- 38 (parziale) → summing finale nel modulo MASTER confermato; pinout backplane resta aperto

## 7. Azioni conseguenti (proposte, non eseguite)

1. Revisionare `docs/fase1/cdj-line-channel.md` → v0.2 allineato ai documenti (gain, EQ +6/frequenze, filter core nel modulo, meter completo, assignment multiple).
2. Decidere con Filippo: build-order unificato (sua fase 1 vs sequenza documenti) — proposta: canale spezzato in 1a (line+gain+EQ+fader+buffer bus, senza filtro) e 1b (filter core+overdrive+meter); master-out resta anticipato come da suo piano; FX come da entrambi.
3. Risolvere REC (0 dBu + jumper) e ratificare PDF-come-autorevole-sul-phono.
4. Aggiungere K1-K7 alle questioni aperte; K2 (tracking filter core) come requisito nuovo da scrivere nei documenti di specifica.
5. Quando arriva l'export completo della conversazione (se arriva): verifica residua e poi compilazione di SPECIFICA.md.

## Fonti verificate

- TI OPA1654: https://www.ti.com/product/OPA1654 (datasheet SBOS492: https://www.darisus.de/Elektonikshop/Datenblaetter/TI/opa1652.pdf)
- TI AN-1651/SNAA046A: https://www.ti.com/lit/pdf/snaa046a
- audioXpress PhL-100: https://audioxpress.com/article/you-can-diy-phl-100-high-quality-mm-phono-line-and-headphone-amplifier

## 8. CORREZIONI POST-RISPOSTE DI FILIPPO (2026-09-18 pomeriggio)

- **Filtro ESTERNO ai canali** (chiarimento del proprietario, risposta 8): la frase dei documenti "four DJ filter cores" significa 4 core stereo nel MODULO FILTRO dedicato, non dentro il modulo canale. Il canale ha solo il selettore HPF/OFF/LPF + send/return sul backplane. Conseguenze: §3.3 riga "interfaccia filtro" corretta — l'ipotesi originale del CDJ v0.1 §3.6 è quella valida; K1 ridimensionato (il canale torna costruibile in fase 1); K2 spostato nel modulo filtro (8 core sullo stesso PCB: matching e trim molto più gestibili che tra moduli). Decisione 60.
- **Recency dell'addendum DOCX**: Filippo indica l'addendum come SUCCESSIVO al PDF → la raccomandazione "PDF prevale" (§3.1) NON è ratificata: entrambe le varianti phono restano [PROVVISORIO] e si risolvono con la simulazione al momento del design phono (decisione 62).
- **Corpus chiuso**: nessun export migliore ottenibile, nessuna specifica separata lato ChatGPT (decisione 58). Le voci [EXPORT] residue vanno risolte contro gli status doc o chiuse come definitivamente aperte.
- **REC**: «la cosa più semplice e standard» → 0 dBu fissi + pad solder-only sul PCB (decisione 63); la proposta −10 dBV + jumper utente di master-out v0.2 §3.5 è SUPERATA.
- **Requisito NUOVO — infrasub ~10 Hz** (risposte 11-12): banda −3 dB ≤8 Hz, SUB kill ~10-90 Hz, niente corner AC >5 Hz nel percorso principale, meter leggibile a 10 Hz, HPF min da decidere (voce 49). I modelli PA specifici sono irrilevanti: conta la typologia «5-way dub soundsystem» (decisioni 65-66).
- **Build order**: nessuno spezzamento 1a/1b — con il filtro esterno, l'ordine originale di Filippo è pienamente valido (decisione 61).
- **Interpretazione da confermare**: la risposta «7 rca» è stata letta come "connettore RCA e loading non accessibile all'utente (solo tecnico)" — voce 57 delle questioni aperte.
