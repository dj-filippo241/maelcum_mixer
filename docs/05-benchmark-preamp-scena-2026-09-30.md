# BENCHMARK — preamp dub della scena (ricerca 2026-09-30)

> Richiesta di Filippo (voce 71B): confrontare gain staging, rumore e
> architettura dei preamp di riferimento della scena soundsystem col progetto
> maelcum, PER INTERO (non solo 5-way), per decidere la ritaratura dei target
> di rumore. Ricerca web in due fasi (9 costruttori), fonti primarie privilegiate.
> Marker: [V] = verificato su fonte primaria letta; [R] = riportato (forum/FB/
> snippet); [I] = incerto. L'assenza di dati è documentata come risultato.

## 1. Schede sintetiche

| # | Costruttore | Tipo | Rumore pubblicato | Nominale | Kill/mute | VCA | Note chiave |
|---|---|---|---|---|---|---|---|
| 1 | Abzu Crossfire (UK, £1-2k) | **DSP 32-bit** + I/O analogici | nessuno (claim "cleanest") | n.d. | DSP | no (DSP) | drive "Growl" = emulazione DIGITALE valvole; 6 vie out; 5 kill |
| 2 | Sage Sound (UK, £1,3-1,7k) | 5u DSP / 3u analogico | nessuno | n.d. | DSP (5u) | no | 5u: **noise gate digitali** per mutare il fondo; manuali PDF da leggere |
| 3 | Ligwa (A. Garnett, Londra, £400-550) | analogico mono 1-5 vie | **−80 dB (Rotary EQ, non pesato)** — unico numero della scena | **+4 dBu** (LED limit +10) | mute switch per via | n.d. | PSU lineare scelta esplicita contro il rumore SMPS; SN relativa ~84 dB = "super clean" per gli owner |
| 4 | Klementz (Nantes, ~€579) | **100% analogico** (claim "no digital conversions"), stereo | nessuno | meter CLIP/0/−6/−12/−18/−24 (unità n.d.) | isolator 3 bande con kill | [I]: forse nei 2 compressori (phono/AUX) | Dub Mixer = architettura più vicina alla nostra (canali+crossfader+isolator+crossover out+FX loop+phono RIAA) |
| 5 | SP Audio / Sounds & Pressure (UK, £1,9-2,7k) | analogico mono, Dr. P. Bush | nessuno ("Extremely low noise" [R]) | n.d. | "kills" nel master | no | **GROWL**: saturazione analogica dedicata sul sub ("valve amp driven hard") = omologo diretto del nostro drive dec. 82; balanced throughout; VU a lancetta opzionali |
| 6 | Dub Sonic (J. Rambaud, FR, Dubbox €600) | analogico, filtri 24 dB/oct | nessuno | n.d. | kill switch | no | siren+echo integrati; eredità "JTS blueprint"; Neutrik/APEM |
| 7 | JB Audio Units (FR, €1,6-1,9k) | analogico [I] 5 vie | nessuno | n.d. | **cut-out switch per via** | no | bande 28-75/75-190/190-2,2k/2,2k-8k/8k-20k; uscite dual-mono TS; manuale PDF da leggere |
| 8 | Jah Tubbys (UK, heritage 1971, usato ~£1,5k) | analogico op-amp | nessuno sul preamp (solo FINALI: SN >103-105 dB, THD+N <0,05%) | n.d. | **cut-out switch** per via | no | reverse-engineering [R]: ~10 op-amp nel percorso; valori dei condensatori graffiati via in fabbrica; nessuna schematica |
| 9 | Mostec (M. Skeete, Londra, dal 2002) | analogico ("without going digital") | nessuno ("clean sounding" [R]) | n.d. | kill switch + **relè per power-on mute** | no | crossover fissati a build time sul sistema target; 3-4 vie; echo digitale = unità separata |

## 2. Quadro di scena (sintesi)

1. **Rumore**: su 9 costruttori, UN numero pubblicato (Ligwa EQ −80 dB non
   pesati ≈ −83…−85 dBuA equivalenti; Jah Tubbys pubblica >103 dB ma solo sui
   finali di potenza). Tutto il resto: aggettivi ("extremely low noise",
   "super clean", "exceptionally clear"). Il DSP gestisce il fondo coi noise
   gate (Sage 5u). **Il target −90 dBuA del nostro sheet §3 è più severo di
   qualsiasi numero mai pubblicato nella categoria**: è una spec da studio di
   mastering, non da soundsystem.
2. **VCA: 0 su 9 nel percorso segnale.** I kill della scena = hard-cut a
   switch (Jah Tubbys, JB), relè (Mostec power-mute), isolator a pot
   (Klementz), o DSP. La catena a 6 THAT 218x del nostro 5-way non ha
   equivalenti pubblicati: paghiamo il floor dei VCA per avere fade da 1 ms
   (dec. 80) e law esatta del drive (dec. 82) — funzionalità che nessuno dei 9
   offre nella forma nostra.
3. **Nominale**: unico documentato = Ligwa +4 dBu (pro standard). Il nostro
   0 dBu mostra 4 dB di SNR relativa in meno a parità di floor assoluto;
   con floor −83…−86 dBuA la nostra DR relativa (83-86 dB) eguaglia/supera
   comunque Ligwa (~84 dB).
4. **Nonlinearità voluta = feature identitaria della scena**: SP Growl
   (analogico, dosabile, sul sub) è il riferimento analogico più rispettato;
   Abzu lo imita in DSP. Il nostro nastro→fuzz (dec. 82, referenza Sherman)
   è allineato alla filosofia S&P.
5. **Analogico vs DSP**: high-end nuovo vira DSP (Abzu, Sage 5u); l'analogico
   resta standard di mid-range e puristi (gli altri 7). Il nostro progetto sta
   nella categoria con MENO dati pubblici: opportunità di documentare meglio
   di tutti (pesatura e punto di misura dichiarati).

## 3. Similitudini e differenze col progetto maelcum

**Similitudini**: PSU pulita come scelta di rumore (Ligwa lineare = nostro
dominio ±15 V LN LT3045/94); parametrici sul sub (Ligwa 30-125 Hz ≈ nostre
celle EQ1/2); kill/mute per via (tutti ≈ nostra kill bank); drive come colore
(SP Growl ≈ nostro drive); formato 5 vie soundsystem; phono RIAA integrato
(Klementz, SP, Dub Sonic, Mostec, JB); FX send/return con loop (Klementz, SP,
Mostec, Dub Sonic); metering LED per via (Mostec/JB 10 segm ≈ nostro metering
a zone); power-mute (Mostec relè ≈ nostro mute §3.7).

**Differenze strutturali**: (1) loro sono preamp/crossover AFTER il mixer,
noi integriamo 4 canali DJ + matrice FX 12× + phono + 5-way in un corpo solo
(l'unico vicino è il Klementz Dub Mixer, stereo e senza matrice FX);
(2) nessuno ha VCA in catena: noi 34-36 pre-dec. 88 (ora ~24-26; 6 erano nel 5-way mono) per fade/law/
matrice; (3) nessuno pubblica gain staging: il nostro sheet mappa ogni nodo
(0 dBu nom, worst +16/+18, capability +24 XLR) — rigore superiore a tutto
il documentabile; (4) headroom: nessuno dichiara dBu di clip (Ligwa indica
limit a +10 sul nominale +4); noi ≥+24 con margini per nodo; (5) la scena
hard-cutta i kill e vive felice: il nostro fade 1 ms è un di più che costa
5 VCA — dato nuovo per la decisione 80 se si volesse rinegoziarla.

## 4. Implicazioni per la voce 71B (target rumore)

- Posizionamento: il 5-way simulato (−77…−73 dBu) sta già dentro/sopra
  l'unico dato di scena; con le fix ingegneristiche (−83…−86 dBuA) **supera o
  eguaglia qualsiasi riferimento pubblicato**.
- Ritaratura difendibile: **−80…−85 dBuA in uscita con pesatura e punto di
  misura dichiarati** (sheet §3 rev 2), restando i più trasparenti della
  categoria perché gli altri non dichiarano nulla.
- Alternativa architetturale emersa (coerente con la scena): kill a
  switch/relè (hard-cut come Jah Tubbys/Mostec/JB) e VCA solo sul drive →
  il floor torna quello di una catena op-amp; costa la revoca della dec. 80
  (fade 1 ms) — decisione di Filippo, tocca un gesto musicale.
- **PDF VERIFICATI IN LOCALE (2026-09-30, poppler)**: Sage 5u manual rev4.0,
  JB 5-Way manual, Mostec MiniPre guide, Klementz NanoPre + Modular Machines —
  NESSUNA tabella di rumore/SNR/headroom in nessuno dei cinque. Unici dati
  quantitativi: Sage 5u (DSP): −1 dBFS = 19 dBV (full-scale interno ≈ +21 dBu)
  e noise gate −140…−120 dBFS («−120 dB silenzia la maggior parte del rumore
  interno del preamp» → il fondo esiste, viene MASCHERATO col gate, non
  certificato); Mostec: relè di mute ~4 s a power-on/off. Conferma: la scena
  non pubblica misure di rumore, punto.
- **SWEEP PDF COMPLETO (fase 3, 2026-09-30)**: letti anche Sage **3u rev1**
  (l'analogico: nessun numero), Sage vecchi manuali (6u/4u/2u FAQ, Bass Thing,
  LCD: nessun numero); Abzu, Ligwa, Dub Sonic, SP Audio: **nessun PDF pubblico
  esiste** (siti marketing Wix, verificato con scan diretto); Jah Tubbys:
  nessuna documentazione ufficiale (valori dei componenti graffiati in
  fabbrica). ESITO: il quadro del benchmark NON CAMBIA — Ligwa −80 dB (solo
  EQ) resta l'unico numero di rumore pubblicato dall'intera scena.
- **Datasheet THAT 2181 LETTO IN LOCALE (poppler)**: condizioni esatte
  confermate — output noise **−98 dBV, 20 Hz–20 kHz NON pesati, 0 dB gain,
  Rout = 20 kΩ** (applicazione standard con OP275); −88 dBV a +15 dB gain
  (il floor segue il gain: il punto di misura del target va dichiarato col
  setting del drive); con I/V 10 kΩ: −104 dBV typ (−6 dB per dimezzamento R).
  Due note di design: (1) **noise modulation**: il floor sale ~4 dB con
  segnale 50 µA rms (shot noise del core Blackmer) — irrilevante ai nostri
  livelli di programma; (2) THAT raccomanda CV processate a 61 mV/dB (10× la
  nostra 6,1 mV/dB) per tenere il rumore del controllo lontano dall'audio →
  verificare il budget rumore CV (shaper + smoothing 1 ms dec. 80 + rail
  ±15 V LN) nel design di sistema (q. 20/21).

## 5. Esito per il progetto (2026-09-30)

Il benchmark ha informato la **decisione 88**: kill 5-way a switch analogici
hard-cut (come Jah Tubbys/JB/Mostec), 10 THAT 218x rimossi dai gate, drive
mantiene il 218x (law dec. 82), pacchetto fix ingegneristiche. Nuovo target
rumore 5-way: **≤ −80 dBu A-wtd** (misurato −83,2 con switch+fix) — a livello
Ligwa («super clean» di scena), con pesatura e punto di misura dichiarati:
nessuno dei 9 fa altrettanto.

## 6. Fonti principali

abzuelectronics.com/preamps · sagesound.co.uk (5u/3u/manuals) · ligwa.com +
forum.speakerplans.com (topic 100481, 104443, 89032) · celestion.com
intervista A. Garnett · klementz.fr (inside-the-dub-mixer, stereo-reggae-dub-
preamp) · spaudio.co.uk (about-us, growl-preamp-5-way) · dub-sonic.com ·
jbaudiounits.com/product-page/5-ways-pre-amp · jahtubbys.co.uk/equipment.html
+ speakerplans topic19980 (reverse engineering JTS) · mostec.co.uk/
electronics/preamps.htm · sound-system.fr (lista preamp dub, Mostec, SP)
