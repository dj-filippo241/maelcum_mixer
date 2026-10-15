# RISULTATI P0 — MC-CHANNEL (2026-10-14)

Piano: `docs/proto-max/piano.md` §2 P0 e §3. Generatore:
`proto-max/coefficienti/genera.py` (numeri in `canale.py`).

## Cosa contiene

- GAIN −∞ … 0 … +10 dB, law del VCA di canale (`sim/cdj/vca-law.cir`):
  metà CCW lineare in dB da −100 a 0, metà CW da 0 a +10.
- Isolator v0.4 (`eq-isolator-v0.4.md` §3, §9): banca LR4, allpass del
  2° ordine, pot lineare ×2, silenzio a fondo corsa (contatto).
  Selettore A 150/500/2500 Hz, C 150 dolce/350/3150, D 150 dolce/700/3150
  Hz (B7; fino al
  2026-10-14 sera B 100/630/4000, scartata con A, dec. 114), dissolvenza
  20 ms tra due banche che girano entrambe.
- Fader −∞ … 0, law [PROVVISORIA]: θ², −12 dB a metà corsa.
- Manopole lisciate a 10 ms.
- Non modellati: blocco della continua d'ingresso (0,72 Hz) e servo DC
  (Live non porta continua); clip e rumore (non si validano a orecchio,
  piano §1).

## FINDING: serve l'oversampling 4×

La banca convertita in digitale (bilineare con prewarp) stringe le
pendenze vicino a fs/2. Scarti contro LTspice senza oversampling:

| Incroci | 44,1 kHz | 48 kHz | 96 kHz |
|---|---|---|---|
| A 150/500/2500 | 1,09 dB (HIGH chiusa, 5 kHz) | 0,91 | 0,23 |
| B 100/630/4000 | 3,24 dB (HIGH chiusa, 8 kHz) | 2,73 | 0,85 |

Rimedio: la banca gira a 4× la frequenza di Live. Due stadi 2×
halfband polifase (schema hiir, de Soras): 12 coefficienti per
fs → 2fs, 4 per 2fs → 4fs. A 20 kHz passano con perdita < 0,000001 dB;
le immagini restano sotto −116 dB. L'infrastruttura serve anche a P1 e
P2: i saturatori la chiedono comunque.

## Verifica 1 — modello contro LTspice (`verifica.py`)

Criterio: scarto ≤ 0,5 dB dove LTspice sta sopra −40 dB; sotto, anche
il modello sotto −40 dB. Casi: le 9 righe di `eq-isolator` §4 e §9
(`iso-c-ac.log`) e le 6 della variante B (`iso-ac-b.log`), 12
frequenze, a 44,1 / 48 / 96 kHz.

| Incroci | 44,1 kHz | 48 kHz | 96 kHz |
|---|---|---|---|
| A (netlist col contatto) | 0,070 dB | 0,060 | 0,018 |
| B (netlist senza contatto) | 0,443 | 0,416 | 0,347 |

**PASS.** Lo scarto di B viene dal netlist, non dal modello: senza
contatto il pot chiuso lascia passare −54 dB (10 Ω su 10 kΩ). Con il
residuo del pot nel modello lo scarto scende a 0,01-0,03 dB. Il circuito
di progetto ha il contatto (eq-isolator §8): il modello segue quello.

## Verifica 2 — codice gen~ contro modello (`prova_gen.py`)

Il testo di `MC-CHANNEL.genexpr` tradotto in Python e suonato campione
per campione a 48 kHz (sinusoidi, ampiezza con fit ai minimi quadrati).
20 punti dell'isolator (A e B), 5 di GAIN, 3 di FADER, separazione dei
lati: **PASS, scarti ≤ 0,002 dB.**

Due errori trovati e corretti in questa verifica (il modello in
frequenza non li vedeva):

1. Ogni sotto-campione a 4× aveva filtri suoi: ogni filtro vedeva un
   campione su quattro e gli incroci scendevano di 4 volte (LOW chiusa:
   −0,4 dB a 80 Hz invece di −22,5).
2. Lo stesso errore sul secondo stadio dell'halfband: calo di −0,09 dB
   a 8 kHz con le manopole al centro.

## Verifica 3 — in Live (Filippo, 2026-10-14, `montaggio.md` §4)

- `MC-CHANNEL.amxd` si apre trascinato su una traccia; gen~ compila.
- Tutto al 50 %: suono invariato. Quattro bande a 0 %: silenzio.
- CPU con 4 dispositivi: **4 %** (240 biquad e 64 sezioni allpass per
  campione, per dispositivo). Margine ampio per P1-P4.

## Non verificato
- Confronto con LTspice dentro Max (rumore rosa, piano §3): sostituito
  dalle due verifiche sopra, che coprono la stessa catena in modo
  ripetibile.

## Variante C (2026-10-14 sera, dopo l'ascolto, dec. 114)

Richiesta di Filippo: HI a metà tra A e B; MID-HIGH che scende più in
basso; LOW e LOW-MID più accavallate. Proposta approvata: **C = 150 Hz
dolce / 350 / 3150 Hz**. Il primo incrocio è LR2 (12 dB/ott, Q 0,5):
LP2 − HP2 = allpass del 1° ordine, quindi i rami alti girano di polarità
e la somma resta piatta senza allpass in più (`canale.PENDENZE`). In
hardware è lo stesso schema con meno componenti su quell'incrocio; il
netlist LTspice di C si fa solo se C (o una sua figlia) passa l'ascolto.

Modello (`canale.isolator`, analogico), dB:

| Banda chiusa, punto | A | B | C |
|---|---|---|---|
| LOW, 50 Hz | −38,3 | −24,6 | −20,0 |
| LOW, 80 Hz | −22,5 | −10,7 | −13,1 |
| LOW, 250 Hz | −1,1 | −0,2 | −2,7 |
| LOW-MID, buco più profondo | −16,0 (275 Hz) | −26,3 (251) | **−7,8 (229)** |
| MID-HIGH, buco più profondo | −22,4 (1122) | −26,4 (1585) | −27,5 (1148) |
| HIGH, 5 kHz | −24,6 | −10,7 | −17,3 |
| HIGH, 8 kHz | −40,5 | −24,6 | −32,5 |

FINDING: con C la LOW-MID chiusa da sola scava solo −7,8 dB (stima a
voce prima del calcolo: ~−15). Banda stretta (1,2 ottave) e fianco basso
dolce: LOW e MID-HIGH la riempiono. È il prezzo dell'accavallamento.

Verifiche: `verifica.py` PASS invariato (A e B contro LTspice, il
modello LR4 non cambia); `prova_gen.py` PASS con 16 punti di C, scarti
≤ 0,001 dB. Il selettore ora porta A e C.

## Variante D (2026-10-14 sera)

Richiesta di Filippo: HI-MID «abbastanza ampio ma senza il kick», «più
simile ai mixer DJ del benchmark» (`docs/09`: confine implicito tra i
centri LO-MID e HI-MID = 620-760 Hz). **D = 150 Hz dolce / 700 / 3150 Hz**,
scelta di Filippo tra D, 500 Hz e entrambe. Nota a Filippo: contraddice in
parte la richiesta di prima (HI-MID sotto 500/630); nei mixer DJ i medi
sono campane larghe e il taglio di HI-MID si sente anche verso 400 Hz.

| Modello, dB | C (350) | D (700) |
|---|---|---|
| HI-MID aperta da sola, 250 Hz (colpo del kick) | −16,4 | −38,6 |
| HI-MID aperta da sola, 150 Hz | −35,7 | −59,6 |
| HI-MID chiusa, buco più profondo | −27,5 (1148 Hz) | −19,9 (1514 Hz) |
| LOW-MID chiusa, buco più profondo | −7,8 (226 Hz) | −13,8 (367 Hz) |

Selettore a tre posizioni (A, C, D), dissolvenza 20 ms tra varianti
vicine. `prova_gen.py` PASS con 9 punti di D in più.


## Selettore CURVA (2026-10-14, 23:55)

Filippo vuole la curva dei DJM Pioneer. I dati (docs/09 §7) dicono
−12 dB a ore 9 (DJM-600/850) e taglio rapido a fine corsa; col pot
lineare di serie nessuna rete passiva ci arriva. Per sentire se la
differenza conta: selettore **CURVA = LINEARE / PIONEER** (ideale, solo
ascolto). PIONEER: lato taglio (2θ)^1,5, lato boost uguale al lineare.

| Manopola | 5 % | 10 % | 20 % (ore 9) | 30 % | 40 % | 50 % | 75 % | 100 % |
|---|---|---|---|---|---|---|---|---|
| LINEARE, dB | −20,0 | −14,0 | −8,0 | −4,4 | −1,9 | 0 | +3,5 | +6,0 |
| PIONEER, dB | −30,0 | −21,0 | −11,9 | −6,7 | −2,9 | 0 | +3,5 | +6,0 |

`prova_gen.py` PASS (6 punti della curva PIONEER su D). Se PIONEER vince
all'ascolto, il circuito per costruirla resta da studiare (pot a taper
con trim, oppure stadio attivo).

## Selettore EQ TIPO (2026-10-15, voce B5)

Filippo tiene B5 aperta come opzione d'ascolto: **EQ TIPO = ISOLATOR /
SERIE**. SERIE è l'EQ in serie archiviato (v0.3 beta-3,
`docs/fase1/eq-serie-v0.3.md`): LOW Baxandall a shelf (70 Hz), LOW-MID e
MID-HIGH a campana sottrattiva (250 Hz Q 0,8 e 1 kHz Q 0,9), HIGH
sottrattiva con HP2 (~4,9 kHz). L'EQ di progetto resta l'isolator
(dec. 105). Modello: `coefficienti/serie.py`, ricavato dai componenti di
`sim/eq-serie/cascade-b3.cir` con op-amp ideali. Gira a 4× come
l'isolator; dissolvenza di 20 ms tra i due EQ. INCROCI e CURVA agiscono
solo su ISOLATOR.

Law delle manopole (eq-serie §10): LOW e HIGH a tratti, con il kill
negli ultimi 5 % di corsa; LOW-MID e MID-HIGH pot lineare col cursore
caricato dal summer (10k su 49,9k). Per la HIGH il netlist dà solo gli
estremi: la law intermedia segue quella della LOW in dB, normalizzata
agli estremi del netlist [PROVVISORIO, solo ascolto].

| Manopola | 0 % | 5 % | 10 % | 20 % | 30 % | 40 % | 50 % | 75 % | 100 % |
|---|---|---|---|---|---|---|---|---|---|
| LOW, 20 Hz | −29,2 | −23,6 | −17,9 | −11,3 | −6,9 | −3,3 | 0 | +2,8 | +5,8 |
| LOW-MID, 250 Hz | −48,3 | −19,2 | −13,3 | −7,5 | −4,2 | −1,8 | 0 | +3,4 | +6,0 |
| MID-HIGH, 1 kHz | −44,0 | −19,4 | −13,5 | −7,6 | −4,2 | −1,8 | 0 | +3,4 | +6,0 |
| HIGH, 20 kHz | −9,1 | −9,2 | −9,2 | −8,3 | −6,1 | −3,2 | 0 | +2,8 | +5,9 |

Cosa si sente rispetto all'isolator: nessuna banda spegne. LOW a zero
lascia la coda del basso (−16 dB a 250 Hz, −5 a 1 kHz); i medi a zero
scavano una buca stretta (−2 dB a un'ottava dal centro); HIGH a zero
scurisce invece di togliere (+1,7 dB a 5 kHz, −3 a 10 kHz: il finding
della questione 68). Tutte a zero: ~−26 dB sotto, ma 2,5-5 kHz restano
aperti.

Verifiche:
- `verifica_serie.py`: modello contro `cascade-b3.log`, 10 modi × 12
  frequenze. **PASS**, scarto massimo 0,24 dB analogico, 0,25 a 48 kHz,
  0,07 a 44,1, 0,01 a 96 (sotto −40 dB i notch del modello sono più
  profondi: op-amp ideali).
- `prova_gen.py`: 37 punti di SERIE in più, gen~ contro modello.
  **PASS**, scarti ≤ 0,001 dB; i punti di prima restano invariati.
- Non verificato: apertura in Max (sintassi gen~) e CPU con il ramo in
  più (4 biquad × 4 sotto-campioni × 2 lati).

## CPU: solo i blocchi che si sentono (2026-10-15 sera)

Finding in Live (Filippo): con canale, filtro e 5-way sulla stessa traccia,
muovendo le manopole l'audio «cambia velocità». Causa: Live calcola i
dispositivi di una traccia in fila su un solo core; il processo Live stava
a ~80 % di un core (l'indicatore CPU di Live, ~45 %, è la media dei core).
Il MC-CHANNEL con EQ TIPO non partiva più (Edit compreso). Con i
dispositivi MC spenti il problema spariva.

Rimedio: MC-CHANNEL calcola solo le varianti con peso > 1e-5 (−100 dB):
in uso normale una banca su quattro (A, C, D, SERIE), due durante i 20 ms
di dissolvenza. Gli stati di un blocco spento vanno a zero, così riparte
pulito. `prova_gen.py` PASS, più una prova nuova dei cambi di selettore
(A → D → SERIE → C: valore giusto dopo l'assestamento, nessun picco).
