# 10 — L'impianto a valle: Horns & Bricks

Fonte: scheda tecnica di Filippo aggiornata al 21/10/2026, incollata in sessione il 27/10/2026.
È il riferimento per tutto ciò che il mixer dà per scontato sull'impianto (vie, incroci, DSP, mono,
effetti esterni). Il testo sotto è la scheda così com'è. Le differenze con le decisioni del progetto
stanno in `02-questioni-aperte.md` solo dopo che Filippo le ha discusse: questo documento non decide niente.

Risposte di Filippo del 27/10: la quinta via arriva a breve, prima del mixer (dec. 132 b); maelcum sostituisce mixer DJ, EPM6 e Ligwa (dec. 132 a); incroci da valutare (B3); infrasub 10 Hz da rivedere (A20); gli effetti esterni citati qui non vincolano il progetto.

---

# HORNS & BRICKS — Scheda tecnica completa del sound system

*Aggiornamento: 21 ottobre 2026*

## 1. Identità e filosofia del sistema

Horns & Bricks è un sound system artigianale dedicato principalmente a reggae, roots e dub, ispirato alla tradizione dei sound system giamaicani.

Il nome richiama le mura di Gerico, abbattute dal suono dei corni.

Il sistema è un *muro mono, attualmente a quattro vie*, con una quinta via dedicata ai supertweeter in fase di progettazione.

### Obiettivi sonori

- Elevata pressione sonora e forte impatto fisico delle basse frequenze.
- Basso profondo e potente, con il caratteristico suono dei cabinet scoop.
- Kick definito e incisivo.
- Riproduzione chiara e intelligibile delle frequenze medie.
- Alte frequenze brillanti ma non aggressive.
- Conservazione del carattere tradizionale dei dub sound system, privilegiando però una taratura tecnicamente corretta.

Il sound system è autocostruito e utilizza cabinet derivati da progetti esistenti, con altoparlanti selezionati separatamente.

Per questo motivo, non deve essere considerato un sistema commerciale già ottimizzato dal produttore: necessita di un lavoro specifico di misurazione, allineamento, filtraggio ed equalizzazione.

---

## 2. Sistema di diffusione

### SUB — Prima via

*Configurazione attuale*

- Cabinet: 2 × Super Scooper, progetto di Rog Mogale
- Altoparlanti: 2 × 18Sound 18LW2400
- Diametro: 18"
- Impedenza nominale: 8 Ω ciascuno
- Potenza nominale: 1200 W AES per altoparlante
- Caricamento: scoop, tromba ripiegata con camera posteriore di compressione
- Amplificatore: CVR DSP-3002

Gli scoop costituiscono un elemento fondamentale dell'identità sonora del sistema.

L'utente desidera conservarli e ottimizzarne le prestazioni, anziché sostituirli con altri progetti come bass reflex, hog scoop o paraflex.

Sono emerse problematiche relative al controllo delle frequenze più basse, alla definizione del basso e alla possibile perdita di rendimento quando il sistema viene spinto a livelli elevati.

Il progetto originale di Rog Mogale suggerisce un taglio subsonico intorno a 38 Hz quando vengono utilizzati due scoop.

In precedenza è stato utilizzato anche un taglio inferiore di 32 Hz, ritenuto potenzialmente troppo basso per il caricamento.

### KICK / UPPER BASS — Seconda via

*Configurazione attuale*

- Cabinet: 2 × cabinet kick con caricamento a tromba
- Altoparlanti: 2 × 18Sound 15MB1000
- Diametro: 15"
- Amplificatore: CVR D-2002
- Banda di lavoro indicativa: 80–170 Hz

Questa via è responsabile di gran parte dell'impatto fisico dei colpi di cassa e delle percussioni.

Durante gli ultimi utilizzi sono emerse alcune criticità, soprattutto un suono percepito come gonfio e rimbombante.

Le cause devono ancora essere identificate attraverso misurazioni.

### MID — Terza via

*Configurazione attuale*

- Cabinet: 2 × sezioni medio-basse del progetto MT121 di Rog Mogale
- Altoparlanti: 2 × 18Sound 12MB700
- Diametro: 12"
- Amplificatore: CVR D-1002
- Banda di lavoro indicativa: 170–1100 Hz

I cabinet sono attualmente privi di materiale fonoassorbente interno significativo.

È in corso una valutazione sull'opportunità di installare materiale assorbente nelle camere posteriori dei woofer.

Durante alcune prove di ascolto, la colorazione scatolosa del sistema sembrava provenire almeno in parte dalla sezione MID.

È stata inoltre considerata la possibilità di aggiungere un terzo cabinet medio, ma questa modifica non è ancora stata realizzata.

### HIGH — Quarta via

*Configurazione attuale*

- Trombe: 2 × 18Sound XT1464
- Driver a compressione: 2 × 18Sound ND1460
- Impedenza nominale driver: 8 Ω
- Amplificatore: Yamaha P2500S
- Banda di lavoro indicativa: 1100–20000 Hz

L'amplificatore Yamaha è utilizzato per la via HIGH, non il Crown XLi800.

I driver a compressione mostrano una naturale riduzione dell'emissione nella parte più alta dello spettro, motivando il progetto di una quinta via.

### SUPER HIGH — Quinta via in progettazione

*Componenti previsti*

- Supertweeter: 4 × Monacor MPT-177
- Tipologia: piezoelettrici
- Amplificatore destinato alla via: Crown XLi800
- Cabinet: nuovi moduli rettangolari autocostruiti

La disposizione estetica prevede coppie di tweeter sfalsati, richiamando i mattoni del nome Horns & Bricks.

È stata discussa una configurazione con due tweeter in serie per coppia e due coppie in parallelo.

Sono state acquistate due resistenze Ciare da 18 Ω / 20 W, ma il loro impiego definitivo non è ancora stato stabilito.

*Nota tecnica:* essendo dispositivi piezoelettrici, i Monacor MPT-177 non possono essere trattati come normali altoparlanti dinamici da 8 Ω. Il cablaggio, il comportamento dell'impedenza e l'eventuale rete di protezione devono essere verificati separatamente.

Il crossover della quinta via non è ancora stato definito. Si sta valutando un intervento indicativamente nella regione superiore agli 8–12 kHz.

---

## 3. Amplificazione — Configurazione aggiornata

Il sistema utilizza amplificatori di potenza separati per ciascuna banda di frequenze.

| Via | Amplificatore | Diffusori |
|---|---|---|
| SUB | *CVR DSP-3002* | 2 × 18Sound 18LW2400 |
| KICK | *CVR D-2002* | 2 × 18Sound 15MB1000 |
| MID | *CVR D-1002* | 2 × 18Sound 12MB700 |
| HIGH | *Yamaha P2500S* | 2 × 18Sound ND1460 |
| SUPER HIGH (futura) | *Crown XLi800* | 4 × Monacor MPT-177 |

### Organizzazione dei canali

La configurazione attuale prevede un altoparlante per canale di amplificazione sulle quattro vie.

Il sistema è monofonico dal punto di vista del programma musicale, ma utilizza più canali di amplificazione per distribuire la potenza tra i cabinet.

Il fatto che il sistema sia mono non implica che gli amplificatori debbano necessariamente lavorare in modalità bridge.

### Impostazioni

- Amplificatori CVR: guadagno nominale di riferimento di 32 dB.
- Yamaha P2500S: guadagno di circa 32 dB.
- Yamaha: filtri interni e YS Processing disattivati.

Le impostazioni effettive dei guadagni e dei livelli devono essere verificate durante la taratura generale.

### Possibili ampliamenti

È stata valutata l'aggiunta di un terzo cabinet medio, da collegare eventualmente al CVR D-1002.

Sono state discusse diverse distribuzioni dei carichi, con impedenze di 2, 4 e 8 Ω.

La scelta non è stata ancora effettuata.

Un'eventuale configurazione asimmetrica dei canali richiederebbe particolare attenzione ai livelli di uscita, ai carichi e all'organizzazione del processamento DSP.

---

## 4. Processamento digitale e crossover

*DSP principale: dbx DriveRack VENU360*

Il VENU360 viene utilizzato per:

- Separazione delle bande di frequenza.
- Filtri passa-alto e passa-basso.
- Equalizzazione parametrica.
- Delay e allineamento temporale.
- Regolazione dei livelli.
- Gestione del segnale destinato agli amplificatori.
- Funzioni di protezione e limitazione disponibili.

### Configurazione crossover di riferimento

| Via | Banda di frequenza | Delay di riferimento |
|---|---|---|
| SUB | 37–80 Hz | 0 ms |
| KICK | 80–170 Hz | 6,50 ms |
| MID | 170–1100 Hz | 7,06 ms |
| HIGH | 1100–20000 Hz | 9,83 ms |

Questi valori rappresentano impostazioni di riferimento discusse in precedenza, non un allineamento definitivamente validato attraverso misurazioni.

Per i crossover sono stati considerati prevalentemente filtri Linkwitz-Riley a 24 dB/ottava.

Per la protezione inferiore degli scoop è stato considerato anche un filtro Butterworth a 24 dB/ottava.

Non sono ancora disponibili curve acustiche misurate che permettano di confermare la correttezza dei tagli e dei delay.

### Stato della taratura

Il sistema è stato regolato prevalentemente a orecchio.

È previsto l'utilizzo di:

- Microfono di misura.
- Scheda audio esterna.
- Computer.
- Software Open Sound Meter e/o REW.

Le misurazioni serviranno a verificare:

- Risposta in frequenza delle singole vie.
- Risposta complessiva.
- Allineamento temporale.
- Risposta di fase alle frequenze di crossover.
- Eventuali cancellazioni e sovrapposizioni.
- Risonanze dei cabinet.
- Correttezza dell'equalizzazione.
- Comportamento del sistema a differenti livelli sonori.

L'obiettivo è ottenere una configurazione di riferimento ripetibile nei diversi eventi, effettuando poi soltanto le correzioni necessarie in funzione dell'ambiente.

---

## 5. Mixer live e preamplificazione

### Mixer live

*Soundcraft EPM6*

Mixer analogico utilizzato nell'organizzazione della catena del segnale.

Caratteristiche rilevanti:

- 6 ingressi mono.
- 2 ingressi stereo.
- 2 mandate AUX.
- Equalizzazione analogica sui canali.
- Uscita stereo principale.

Il mixer può ricevere il segnale delle sorgenti DJ, di altri dispositivi e di processori esterni.

Sono state discusse le differenze tra l'utilizzo degli ingressi stereo e di due canali mono per collegare una consolle.

Le mandate AUX possono essere impiegate per inviare il segnale a processori esterni di delay e riverbero, con i limiti tipici della configurazione del mixer.

### Preamplificatore

*Ligwa Preamp — formato rack 1U*

È presente un preamplificatore Ligwa da 1U.

L'inserimento del preamp ha prodotto un miglioramento soggettivo dell'apertura e della brillantezza complessiva del sound.

Il modello esatto e il routing effettivo rispetto al Soundcraft EPM6 devono ancora essere documentati completamente.

---

## 6. Sorgenti musicali e apparecchiature DJ

Il sound system viene utilizzato con consolle DJ e sorgenti musicali, inclusi giradischi.

La configurazione definitiva delle sorgenti non è ancora documentata.

Sono stati valutati diversi mixer DJ, in particolare:

- Rane MP44.
- Allen & Heath Xone:92.
- Allen & Heath Xone:96.
- Allen & Heath Xone:S2.

Il Rane MP44 è stato considerato soprattutto per il formato rack e le possibilità di utilizzo con effetti dub esterni.

L'Xone:96 è stato esaminato anche per le interfacce audio USB integrate e la possibilità di utilizzare un computer come sorgente multicanale.

Questi mixer sono apparecchiature valutate come possibili acquisti, non componenti confermati del sistema.

### Giradischi

È stata discussa la necessità di isolare meccanicamente i giradischi dalle vibrazioni prodotte dal sound system, in particolare dalle frequenze sub.

Le soluzioni valutate includono:

- Basi pesanti.
- Materiali elastici antivibranti.
- Supporti disaccoppiati.
- Combinazioni di massa e materiali resilienti.

L'obiettivo è prevenire il feedback meccanico attraverso la puntina, particolarmente problematico nei sound system con elevata pressione sulle basse frequenze.

---

## 7. Effetti dub esterni

Si sta progettando una sezione dedicata agli effetti esterni, soprattutto echo/delay e riverbero.

### Riverbero

È stato individuato come possibile soluzione il *JB Audio Unit Reverb*.

Non risulta ancora acquistato o inserito stabilmente nel sistema.

### Echo / Delay

Sono stati considerati diversi dispositivi, tra cui alcuni prodotti Benidub.

La preferenza va ad apparecchiature rack, anche se non vengono escluse completamente le unità desktop.

L'obiettivo è sperimentare più tipi di echo prima di investire in una soluzione definitiva.

### Utilizzo previsto

Gli effetti dovranno integrarsi nella catena analogica di controllo del sound system.

Si vuole poter inviare selettivamente il segnale ai processori esterni e controllare i ritorni.

È importante valutare:

- Numero e tipologia delle mandate disponibili.
- Mandate pre-fader e post-fader.
- Possibilità di trattare separatamente delay e riverbero.
- Ritorno dei processori su canali dedicati.
- Possibilità di realizzare feedback controllati per gli effetti dub.
- Gestione del livello del segnale.
- Rumore, headroom e rischio di saturazione.

La configurazione definitiva non è ancora stata scelta.

---

## 8. Catena del segnale

### Struttura generale

La struttura funzionale del sistema può essere rappresentata così:

*Sorgenti audio → controllo e mixaggio analogico → DSP dbx VENU360 → amplificatori → diffusori*

Le apparecchiature note comprendono il Ligwa Preamp 1U e il Soundcraft EPM6.

Tuttavia, non è ancora completamente documentato il cablaggio effettivo tra sorgenti, preamplificatore e mixer live.

Questo punto deve essere chiarito prima di progettare modifiche al routing.

### Distinzione tra le sezioni

*Sezione sorgenti*

Comprende giradischi, lettori, computer, consolle ed eventuali interfacce audio.

*Sezione di mixaggio e controllo*

Comprende mixer DJ, mixer live, preamplificatori, equalizzatori ed eventuali effetti esterni.

*Sezione di processamento*

Comprende il dbx VENU360, che gestisce crossover, delay, equalizzazione e controllo delle vie.

*Sezione di potenza*

Comprende gli amplificatori CVR, Yamaha e, in futuro, Crown.

*Sezione di diffusione*

Comprende scoop, kick, mid, high e futura via super high.

Il routing degli effetti e delle sorgenti deve essere progettato distinguendolo dal processamento DSP dedicato agli altoparlanti.

---

## 9. Criticità acustiche osservate

Durante gli ultimi utilizzi live è stata riscontrata una buona capacità del sistema di generare pressione sonora.

La criticità principale è una colorazione descritta come *gonfia, scatolosa e rimbombante*, percepita soprattutto sui colpi di cassa e sulle percussioni.

In particolare:

- Il sistema produce molta pressione, ma il kick può risultare poco definito.
- Le frequenze medio-basse sembrano contribuire alla sensazione di rimbombo.
- Durante prove di esclusione delle singole vie, parte della colorazione sembrava provenire dalla sezione MID.
- Non è ancora chiaro quanto contribuiscano il caricamento dei cabinet, l'equalizzazione o le sovrapposizioni dei crossover.
- I cabinet MID non hanno un trattamento fonoassorbente interno significativo.
- Gli scoop devono ancora essere misurati e ottimizzati.

La priorità è identificare le cause attraverso misurazioni, evitando modifiche casuali ai cabinet o ai componenti.

---

## 10. Progetti e sviluppi futuri

### Ottimizzazione acustica

- Misurazione delle singole vie.
- Verifica dei crossover.
- Verifica dei delay.
- Ottimizzazione dell'equalizzazione.
- Analisi del comportamento dei sub a volume elevato.
- Valutazione dei materiali fonoassorbenti.
- Definizione di un setup di riferimento.

### Quinta via

- Costruzione dei moduli per i supertweeter.
- Definizione del cablaggio dei Monacor MPT-177.
- Verifica dell'interfacciamento con il Crown XLi800.
- Scelta del crossover e delle eventuali protezioni.
- Integrazione con la via HIGH.

### Espansione del sistema

È stata valutata l'aggiunta di un ulteriore cabinet MID.

Sono stati inoltre discussi diversi progetti alternativi di cabinet kick e sub, senza che sia stata decisa una sostituzione dell'attuale sistema.

### Controllo e apparecchiature

- Evoluzione della sezione DJ.
- Valutazione di mixer rack.
- Integrazione di echo e riverbero esterni.
- Studio del routing di sorgenti, preamplificatori ed effetti.
- Realizzazione di rack autocostruiti per le apparecchiature.

---

## 11. Indicazioni per l'analisi tecnica da parte di un'altra AI

Questa scheda descrive un sound system artigianale realmente utilizzato, non un progetto puramente teorico.

È importante distinguere:

1. *Hardware installato:* diffusori, altoparlanti, amplificatori, DSP, Soundcraft EPM6 e Ligwa Preamp.
2. *Componenti futuri:* supertweeter Monacor e Crown XLi800 destinato alla quinta via.
3. *Apparecchiature valutate:* mixer DJ alternativi, echo, riverbero e altri dispositivi.
4. *Impostazioni provvisorie:* crossover, delay, equalizzazioni e livelli da verificare attraverso misurazioni.
5. *Informazioni mancanti:* routing dettagliato prima del mixer live, modelli delle sorgenti ed eventuali altre apparecchiature analogiche.

### Priorità nella progettazione del sistema

Il proprietario vuole mantenere la filosofia di un sound system dub tradizionale, con un controllo musicale ed espressivo diretto.

Non cerca necessariamente una soluzione digitale integrata che sostituisca tutta l'elettronica analogica.

Privilegia l'utilizzo di apparecchiature hardware, soprattutto quando consentono un controllo immediato e intuitivo di sorgenti, effetti, livelli e timbro.

Il sound deve però essere progettato con attenzione alla qualità del segnale, alla corretta struttura dei guadagni, al rumore di fondo, alla compatibilità elettrica e alla semplicità operativa durante gli eventi.

L'obiettivo finale è un sistema potente, musicalmente espressivo, tecnicamente affidabile e progressivamente più raffinato nella qualità della riproduzione.
