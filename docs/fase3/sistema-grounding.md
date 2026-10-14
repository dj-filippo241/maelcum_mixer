# Sistema grounding/EMC (questione 21) — v0.1 [PROVVISORIO — regola 3]

Data: 2026-10-01 (workstream S2, piano `00-piano-sistema.md`, dec. 90).
Scope: topologia analogue-0V, bonding chassis, schermi, masse speciali
(phono/pedali/CUE), EMC/RF, regole layout millefori. Interfacce:
`SPECIFICA.md` §3 (righe [BLOCCATE] 70-71), sheet §1 (domini),
`phono-stage.md` (GND giradischi → stella), `sistema-backplane.md` (i
ritorni di massa viaggiano sul backplane — pinout lì).

> **[REV 2026-10-14, dec. 113 — alimentatore esterno]** La stella
> analogue-0V resta DENTRO il mixer, nel modulo PSU-IN che riceve il cavo
> dal box esterno (`sistema-psu.md` REV dec. 113). Il box non collega i
> suoi zeri alla terra: gli 0 V dei secondari viaggiano nel cavo e si
> uniscono solo alla stella. La terra di rete arriva al telaio del mixer
> dallo schermo del cavo; il bond CHASSIS↔AGND unico (§2) resta alla
> stella. Dove sotto si legge «modulo PSU», vale «modulo PSU-IN».

## 1. Principio

Un solo punto di riferimento: la **stella analogue-0V** nel modulo PSU
(ritorno center-tap del secondario audio del toroidale, morchetto unico).
Tutte le masse di segnale convergono lì e da nessun'altra parte. Chassis,
control ground e schermi hanno percorsi propri che incontrano la stella
UNA volta sola. Nessuna corrente di potenza, commutazione o segnale
condivide un conduttore con un'altra: il backplane distribuisce ritorni
dedicati per classe (riga a di ogni connettore: 8 pin AGND per modulo).

Regola aurea del progetto: le correnti tornano alla stella senza mai
attraversare il percorso di un altro modulo. Un modulo che assorbe 300 mA
non deve produrre 300 mA × Z_comune su un nodo che un preamp phono usa
come riferimento (Z_comune obiettivo < 1 mΩ → < 0,3 µV = −128 dBu: sotto ogni
target del progetto, dec. 89).

## 2. Topologia a tre piani di massa

| Piano | Cosa porta | Dove nasce | Dove incontra gli altri |
|---|---|---|---|
| AGND (analogue 0V) | ritorni segnale + ritorni potenza dei rail locali | stella PSU (center-tap secondario audio) | — (è il riferimento) |
| CTRL_GND (control ground) | ritorni logici: mode bit, mute, CV, LED | secondario +5 V (raddrizzatore dedicato) | UNICO bond AGND↔CTRL_GND alla stella PSU |
| CHASSIS/SHIELD | schermi connettori esterni, telaio, alette | — | UNICO bond CHASSIS↔AGND alla stella PSU (morsetto dedicato, removibile per diagnosi hum) |

Motivazione del bond chassis singolo alla stella (e non distribuito):
le correnti di schermo dei cavi esterni (RCA giradischi, XLR, jack
pedali) rientrano tutte al punto stella; il telaio resta a potenziale di
riferimento senza anelli. Alternativa classica "chassis a 1 nF/1 MΩ
ibrido" NON adottata: con un solo giradischi + rack FX la via bassa
impedenza unica è più predicibile; il morsetto removibile permette di
sperimentare l'isolamento a banco (voce: verifica hum in sessione
hardware).

## 3. Percorsi per modulo

1. Ogni modulo riceve AGND sui pin dedicati della riga potenza del suo
   connettore (8 pin paralleli = <1 mΩ di contatto, `sistema-backplane.md`).
2. Dentro il modulo: piano/maglia di massa locale (millefori: rete a
   intreccio di filo rigido 0,8-1 mm stagnato, o PCB con copper pour);
   la massa locale fa capo a UN punto del modulo (il pin AGND del
   connettore) — niente ritorni a catena (daisy-chain) tra sezioni.
3. Sezioni interne con correnti diverse (es. nel canale: phono
   pre → EQ → driver) hanno ritorni stellati interni: il punto di stella
   di modulo sta fisicamente vicino al connettore, e le sezioni sensibili
   (phono, primo stadio) tornano per prime.
4. Regolazione locale (dec. 45/90): LM317/337 ±18 V, LT3045/94 ±15 V LN,
   LDO ±15 V switch — i loro ritorni vanno al punto di stella di modulo,
   NON al carico (il carico torna separatamente: la corrente di uscita
   non attraversa il riferimento del regolatore).
5. Test point AGND su ogni modulo (SPECIFICA §2 [BLOCCATO]).

## 4. Schermi e connettori esterni

| Interfaccia | Trattamento | Motivo |
|---|---|---|
| XLR in/out (master, mic) | pin 1 → CHASSIS al connettore (corto, diretto); segnale riferimento AGND del modulo | standard AES: lo schermo scarica RF sul telaio senza entrare nel riferimento audio |
| RCA line/CDJ | shell → CHASSIS diretto al pannello | idem; guscio metallico del pannello = continuazione del telaio |
| RCA phono | shell → CHASSIS; **in più** il terminale GND del giradischi è ISOLATO dal pannello e scende con filo dedicato alla stella AGND (posticino nel modulo phono/canale) | la corrente del filo di massa giradischi (che raccoglie il loop telaio-motore) non deve passare nello schermo del segnale né nel telaio: `phono-stage.md` riga 31/125 |
| Jack pedali FX (send/return) | sleeve → AGND del modulo FX nel punto stella di modulo; nessun ground-lift di default | ritorno del pedale definito; see §5 |
| Jack GENERIC MONO (in) | sleeve → AGND del modulo nel punto stella di modulo, come i jack pedali | sorgente esterna single-ended: il suo ritorno è il riferimento del buffer d'ingresso (`docs/fase4/mic-mono-moduli.md` §7) |
| Jack CUE/booth/utility | sleeve → AGND locale del modulo | ritorno cuffia = riferimento dell'ampli, non del telaio |
| Cavi interni schermati (dove servono: phono in→stadio, cue bus se lungo) | schermo mono-lato: lato sorgente a AGND, lato destino floating (nastro) | evita anelli di massa interni; la RF resta scaricata dal lato sorgente + chassis ai connettori |

## 5. Masse speciali

**Phono (critica)**: catena del giradischi = loop d'antenna grande.
Regole: (1) filo GND giradischi → stella AGND con percorso proprio, mai
avvitato al telaio; (2) RCA phono il più vicino possibile al front-end
(modulo canale, sezione A0): il tratto RCA→JFET è <10 cm schermato;
(3) nessun altro ritorno di potenza passa nel raggio della sezione phono
(layout: sezione phono al bordo del modulo, lontano dal connettore di
potenza); (4) il guscio RCA phono tocca il pannello (= chassis) solo al
connettore. Se a banco compare hum a 50/100 Hz: diagnosi col morsetto
chassis-stella aperto (§2) e, se serve, isolamento del sleeve phono dal
chassis (round RC 1 MΩ//10 nF documentato come opzione, non di serie).

**Pedali FX**: ogni pedale chiude un loop col mixer. Strategia di base:
sleeve di send E return allo stesso AGND di modulo (loop piccolo dentro
il mixer, loop grande pedale-mixer inevitabile e gestito dai driver:
send low-Z, return hi-Z ≥1 MΩ con protezione — `fx-module.md` §4).
Il "controlled mono sum" (2×10k, mai hard-short) resta. Se un pedale
specifico frigge (ground loop proprio): rimedio a banco = transformer
isolation sul return O ground-lift sul send del canale interessato —
predisposizione: footprint per 1 MΩ//10 nF sleeve→chassis su ogni jack
pedale [PROVVISORIO — decisione a banco, sessione hardware].

**CUE/cuffie**: ritorno cuffia = AGND del modulo CUE (stella di modulo);
le 2 uscite in parallelo (dec. 90) condividono lo sleeve: nessun anello
verso altri moduli. Il livello cuffia (fino a ~1 Vrms su 32 Ω = 30 mA)
resta confinato nel modulo.

**CV e controllo**: i CV 0-5 V (convenzione SPECIFICA §2) tornano su
CTRL_GND (riga c del connettore, pin dedicati adiacenti), mai su AGND.
Il bond unico alla stella evita che le correnti di commutazione degli
switch/logiche (kill, mode bit, LED) moduli i riferimenti audio.

## 6. EMC/RF

1. **Filtro di rete nel modulo PSU** (interfaccia con S1): ingresso IEC
   con filtro X2/Y2 + common-mode choke integrato; Y-cap verso chassis
   nel punto di entrata; il secondario del toroidale NON ha Y-cap verso
   AGND (isolamento pulito); il bond AGND-chassis resta unico (§2).
2. Ferrite + bulk locale all'ingresso rail di ogni modulo (già a sheet
   §1 REV dec. 93): bead sui raw in ingresso (±27 audio / ±22 LN /
   ±26 [M] master) + 100-470 µ bulk + 100 n per op-amp.
3. Il toroidale è l'unica sorgente magnetica grossa: orientato lontano
   dalla sezione phono e dal modulo canale 1, montato su gomma, con
   schermo a campana metallico collegato al chassis [PROVVISORIO —
   verifica a banco del ronzio residuo; alternativa: toroidale incapsato].
4. RF dai cavi di pannello (pot CV lunghi): RC snubber ai pin di
   ingresso CV del modulo (100 Ω + 10 n a CTRL_GND) — stesso trattamento
   delle linee mode bit (serie 10k già previsto, §8.10 five-way, + 10 n
   lato modulo).
5. Nessun bus floating (SPECIFICA §3): ogni linea di backplane ha un
   destinatario definito e, dove bidirezionale non serve, un driver.

## 7. Anelli di massa tra moduli

L'architettura li elimina alla radice: nessun segnale audio ha un
"ritorno via chassis" — tutti i ritorni sono AGND di backplane verso la
stella unica. Gli unici anelli possibili sono esterni (cavi tra mixer e
pedali/giradischi/PA): gestiti alle interfacce (§4-5) e, a livello
sistema, dal fatto che il mixer ha UN punto di terra (la stella) e il
suo chassis tocca AGND una volta sola — nessuna corrente di terra
esterna attraversa il telaio se non via schermo dei connettori.

## 8. Regole pratiche millefori/PCB (prototipo e moduli finali)

1. La stella fisica sul backplane è realizzabile: piano AGND continuo
   (backplane = PCB a 2 strati minimo, lato solder = AGND pour quasi
   intero; ritorni dei moduli su pin multipli). Se il backplane finale è
   millefori (fase 1): barra di rame 4×20 mm imbullonata come spina
   dorsale AGND + fili radiali 1,5 mm² per modulo → stessa topologia,
   impedenza più alta ma accettabile in fase 1 (solo 4 moduli attivi).
2. Nei moduli millefori: maglie di massa a filo rigido stagnato,
   sezioni stellate, phono primo e più lontano dal connettore di
   potenza; mai un filo di ritorno condiviso tra due sezioni.
3. Disaccoppiamento: 100 n ceramico per op-amp (entrambi i rail,
   cortissimo), 10-47 µ tantalum/MLCC per gruppo di 4-8 op-amp, bulk
   100-470 µ all'ingresso rail del modulo.
4. Segnali sensibili (phono, cue, CV) instradati lontani ≥5 mm dai fili
   di potenza e dal trasformatore; incroci a 90°.
5. Ogni modulo: test point AGND + rail + 1 nodo segnale chiave
   (SPECIFICA §2 [BLOCCATO]).

## 9. Assunzioni dichiarate

- Telaio metallico conduttivo unico (alluminio/acciaio), pannello
  frontale = parte del chassis (viti + rondelle dentate per continuità).
- Un solo ingresso rete (IEC) nel modulo PSU; nessun altro modulo tocca
  la rete.
- Moduli inseriti/rimossi SOLO a sistema spento (SPECIFICA §2: no
  hot-swap [BLOCCATO]) → nessuna protezione contro correnti di
  inserimento a caldo.
- Il numero e la posizione fisica dei moduli (questione 29 ingombri) non
  cambia la topologia a stella: cambia solo la lunghezza dei radiali.

## 10. Da verificare a banco (fase 1)

1. Ronzio residuo con phono a gain max, giradischi collegato: target
   udibile solo a orecchio sul cono (< −60 dBu indotto).
2. Efficacia del bond chassis unico vs opzione RC (morsetto aperto).
3. Ground loop pedali: con il rack FX reale di Filippo, eventuali
   ground-lift da abilitare (footprint predisposto §5).
4. Crosstalk di massa: modulo che commuta (kill switch) con phono
   aperto — nessun tick sul riferimento (il click del kill è nel
   segnale, accettato dec. 88; qui si cerca accoppiamento di massa).
