# RISULTATI P3 — FX e master (2026-10-15)

Piano: `docs/proto-max/piano.md` §2 P3. Modello: `coefficienti/fx.py`.
Generatore: `genera_fx.py`. Verifiche: `verifica_fx.py` (modello contro
LTspice e SPEC), `prova_fx.py` (codice gen~ contro modello).

## Cosa contiene

Scelta di Filippo (2026-10-15): i pedali sono **effetti veri di Live**,
non segnaposto dentro MC-FX. Il piano diceva un solo `MC-FX`; con gli
effetti di Live servono quattro dispositivi:

| Dispositivo | Dove | Comandi | Fonte |
|---|---|---|---|
| MC-SEND | ogni canale, tra MC-CHANNEL e MC-FILTRO | EQ LOW, EQ HIGH, LEVEL, FX1-FX4 | fx-send-module §2, dec. 91a, 108 |
| MC-BUS | primo dispositivo di ogni traccia FX | BUS (FX1-FX4, solo montaggio) | fx-module §2-§3 |
| MC-RET | dopo l'effetto, sulla stessa traccia FX | GAIN, EQ LOW, EQ HIGH, > FX1-> FX4, meter | fx-module §5, §7 |
| MC-MASTER | traccia Master | MASTER, MONO, meter L/R | master-out §3.2, addendum dec. 111 |

Catena di una traccia FX: MC-BUS → effetto di Live (il pedale) → MC-RET
→ fader della traccia (= fader del ritorno). Il reroute sta prima del
fader: abbassi il fader e il loop continua (SPEC §7).

Collegamenti: `send~ mcfx_b<n>L/R` da MC-SEND e da MC-RET, `receive~` in
MC-BUS. La refpage di Max conferma: più `send~` con lo stesso nome si
sommano nel `receive~`. Il bus è quindi la somma di tutte le mandate e
di tutti i reroute, come il sommatore virtual-earth del circuito.

Non c'è un comando in più rispetto al design. BUS di MC-BUS serve solo a
dire alla traccia quale bus ascolta.

## 1. Law e numeri

| Comando | Law | Stato |
|---|---|---|
| LEVEL (mandata) | pot log curva A: −20 dB a metà, 0 dB a fine corsa | dec. 108 |
| ASSIGN | rampa 1 ms | dec. 80 |
| EQ LOW (mandata e ritorno) | taglio: 0 → −6 dB tra 50 e 20 %, −6 → −30 dB negli ultimi 20 %; boost 0 → +6 dB | [PROVVISORIO]: la SPEC dice solo «rapidi solo al taglio estremo» |
| EQ HIGH | taglio: asintoto 0 → −15 dB tra 50 e 30 %, poi fino al kill; boost 0 → +6 dB | [PROVVISORIO]: la SPEC dice «taglio rapido in partenza, poi graduale» |
| GAIN (ritorno) | 0 → +20 dB su metà corsa CW; −40 → 0 dB tra 5 e 50 %; silenzio a fondo corsa | [PROVVISORIO] |
| REROUTE | a tratti, SPEC §7: 0-20 % −∞…−40, 20-45 % −40…−20, 45-70 % −20…−10, 70-85 % −10…−4, 85-95 % −4…−1, 95-100 % −1…0 dB; CV lisciato 1 ms | BLOCCATO |
| MASTER | −∞ a fondo corsa, 0 dB all'80 % (detent), +6 dB a fine corsa | [PROVVISORIO]: master-out §3.2 dice unity al 75-80 % |
| MONO | M/S, S in un VCA da 0 a −100 dB in 1 ms | addendum dec. 111 |
| Rail | sommatore del bus e VCA del ritorno a ±16,5 V (+23,5 dBu) | fx-module §8.5 |
| Meter | fondo scala +24 dBu, rilascio 0,3 s, clip latch 479 ms sopra +23 dBu | sistema-metering, dec. 81/90 |

Sul meter di Live (scala −60…0): 0 = +24 dBu, −24 = 0 dBu. Il meter del
ritorno è uno solo (mono centrato, il più alto dei due lati).

**EQ2, cella HIGH**: a fondo corsa toglie solo −1,4 dB a 10 kHz e −5,1 dB
a 20 kHz. È la cella sottrattiva del design (questione 68, accettata
anche per i ritorni, fx-module §6): scurisce, non spegne gli alti.

## 2. Modello contro LTspice e SPEC (`verifica_fx.py`)

- EQ2, formula analogica contro `sim/fx/fx-eq2.log` (6 modi × 7
  frequenze, 20 Hz-35 kHz): entro **0,13 dB** (lo scarto più grande è a
  35 kHz, dove conta la banda degli op-amp reali).
- EQ2 digitale a 4× contro la formula analogica: entro **0,23 dB** fino
  a 20 kHz. Sopra i 24 kHz il halfband taglia comunque.
- REROUTE contro la griglia di 13 punti di fx-module §8.3: esatto
  (2·10⁻¹⁵ dB).

## 3. Codice gen~ contro modello (`prova_fx.py`)

**PASS 139/139**, sui due canali:
- MC-SEND: l'audio del canale esce identico (errore 0); EQ2 e LEVEL su
  12 casi entro 0,05 dB; ogni ASSIGN accende solo il suo bus.
- MC-RET: GAIN su 6 posizioni, EQ2, REROUTE su 6 posizioni × 4 bus;
  rail a 16,5 V (+26 dBu chiesti); meter a 0, +20, +24 dBu entro 1 %;
  clip spento a +20, acceso a +24 dBu.
- MC-MASTER: MASTER su 6 posizioni entro 0,01 dB; MONO: un solo lato in
  ingresso esce a metà su entrambi (−6 dB), L = R resta invariato.

Nomi gen~: il generatore controlla da solo che nessun nome esterno
coincida con un parametro o un locale di funzione (`nomi_in_comune`):
nessuna collisione.

## 4. Dove parte il feedback (dec. 108)

Il giro bus → pedale → GAIN → REROUTE non contiene LEVEL. Con un pedale
che esce allo stesso livello in cui entra (eco al 100 % wet, nessun
feedback interno), il loop arriva a unity quando GAIN + REROUTE = 0 dB:

| GAIN del ritorno | REROUTE per unity (self o cross) |
|---|---|
| 50 % = 0 dB | 100 % |
| 55 % = +2 dB | 91,7 % |
| 62,5 % = +5 dB | 82,5 % |
| 75 % = +10 dB | 70 % |
| 87,5 % = +15 dB | 57,5 % |
| 100 % = +20 dB | 45 % |

Quante ripetizioni prima che l'eco scenda di 60 dB, con GAIN a 0 dB:

| REROUTE | dB per giro | ripetizioni |
|---|---|---|
| 100 % | 0 | infinite (si sostiene) |
| 97,5 % | −0,5 | 120 |
| 95 % | −1 | 60 |
| 90 % | −2,5 | 24 |
| 85 % | −4 | 15 |
| 77,5 % | −7 | 8,6 |
| 70 % | −10 | 6 |
| 45 % | −20 | 3 |

Cosa vuol dire sotto le mani: con GAIN al centro tutto il gesto del dub
(da poche ripetizioni all'eco che si mangia da sola) sta nell'ultimo
terzo della corsa del REROUTE, e il tratto finale 95-100 % è quello fine.
Se alzi il GAIN per compensare una mandata bassa, il punto di innesco
scende: a GAIN +10 dB il loop parte già al 70 %.

**Sopra unity**: nel circuito il loop si ferma dove satura il pedale.
Un effetto di Live non satura: il loop sale fino al rail del bus
(+23,5 dBu, cioè +11,5 dBFS) e tosa duro. È il caso K4 della dec. 84
(«dry loop»), non il comportamento col pedale vero. Per sentire il
gesto giusto conviene mettere un **Saturator** di Live dopo l'eco:
fa la parte della saturazione del pedale.

## 5. Limiti

- **Latenza dei collegamenti**: ogni `send~`/`receive~` tra tracce può
  aggiungere un buffer di ritardo (refpage di Max: dipende dal numero di
  oggetti e dai loop). Nel giro del feedback il ritardo si somma al tempo
  dell'eco: da sentire (piano §2 P3).
- Non modellati: rumore del loop (fx-module §7: +10 dB a g 0,99),
  saturazione morbida del sommatore (qui il rail è un taglio netto),
  DC servo dei ritorni.
- Il canale R di ogni dispositivo ha i suoi stati: la prova suona sempre
  L e R.

## 6. Da sentire (domande per l'ascolto di Filippo)

1. Law dell'EQ2 (LOW e HIGH), del GAIN e del MASTER: sono mie, scritte
   dalle frasi della SPEC.
2. Dove parte il feedback e se il loop si governa con le mani (§4).
3. Latenza del giro: allunga l'eco in modo che si sente?
4. MONO: la rampa da 1 ms suona pulita sul tasto?
