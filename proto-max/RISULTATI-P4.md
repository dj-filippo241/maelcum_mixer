# RISULTATI P4 — Mic (2026-10-15)

Piano: `docs/proto-max/piano.md` §2 P4. Design: `docs/fase4/mic-mono-moduli.md`
(dec. 97, REV dec. 111). Modello: `coefficienti/mic.py`. Generatore:
`genera_mic.py`. Verifiche: `verifica_mic.py` (modello contro LTspice),
`prova_mic.py` (codice gen~ contro modello).

## Cosa contiene

Un dispositivo, `MC-MIC`, sulla traccia del microfono. Il pannello è quello
del modulo, niente di più: GAIN, EQ LOW, EQ HIGH, FX1-FX4 (le 4 mandate),
il tasto MUTE e il LED a tre colori.

```
scheda audio (preamp al minimo) -> INA +30 dB fisso (rail) -> passa-alto
60 Hz -> GAIN 0...+30 dB (rail) -> nodo PRE -> LED
      -> EQ2 (rail) -> MUTE (1 ms) -> uscita L = R (mono centrato) al Master
                                   -> FX1-FX4 -> bus di P3 (send~ mcfx_b<n>)
```

- Le mandate arrivano agli stessi bus di MC-SEND e MC-RET: il receive~ di
  MC-BUS le somma, come il multidrop del backplane.
- Il MUTE spegne uscita e mandate insieme (il caso del larsen). Il LED sta
  prima del MUTE: col mic muto vedi ancora se l'MC parla.
- L'ingresso destro è ignorato: il mic è mono, sul canale sinistro del
  dispositivo.

## 1. Law e numeri

| Comando | Law | Stato |
|---|---|---|
| GAIN | [REV 2026-10-22, dec. 129 E2] pot a curva inversa C 20 %: 29,5 dB a 0 %, 36,3 a 25 %, 46,4 a metà, 50,9 a 75 %, 59,3 a fine corsa (prima, lineare: 38,3 a metà, ultimo 10 % = 8,4 dB) | circuito simulato; prova_mic PASS |
| Passa-alto | Sallen-Key 2° ordine, f0 60,5 Hz, Q 0,707: −3 dB a 60 Hz, −0,55 a 100 Hz | dec. 97 |
| EQ LOW / HIGH | le celle e le law di P3 | [PROVVISORIO], come B8 |
| FX1-FX4 | pot curva A: −20 dB a metà, 0 dB a fine corsa, mai sopra 0 | [PROVVISORIO], voce 40 |
| MUTE | VCA da 0 a −100 dB in 1 ms, lineare in dB, poi zero | REV dec. 111 |
| LED | picco al nodo PRE, rilascio 0,3 s: verde ≥ −6 dBu, giallo ≥ +11, rosso ≥ +17 con latch 0,5 s | [PROVVISORIO], B6 |
| Rail | front-end ±13,5 V (+21,8 dBu, l'overload simulato dell'INA); EQ2 e VCA ±16,5 V | §3.3, fx-module §8.5 |

**Ingresso**: la scheda audio fa la parte del connettore XLR. Il modello
assume che 0 dBFS al preamp minimo corrisponda a **+9 dBu** al microfono
(`mic.SCHEDA_DBU`, [PROVVISORIO]: valore tipico, da sostituire col dato
della scheda di Filippo). Se il numero è sbagliato, il guadagno vero è
spostato della differenza; la forma delle law non cambia.

**Uscita**: 0 dBu = −12 dBFS di picco, come P0-P3.

## 2. Modello contro LTspice (`verifica_mic.py`)

- Preamp, formula contro `sim/mic/mic-pre-ac.log`: 11 posizioni del GAIN
  × 6 frequenze (20 Hz-20 kHz), scarto massimo **0,057 dB** (a 60 Hz; a
  1 kHz ≤ 0,001 dB).
- Le due resistenze da 10 Ω in serie all'ingresso contano: senza, il
  guadagno esce 0,07 dB più alto.
- Preamp digitale a 4× contro la formula: scarto < 0,001 dB.

## 3. Codice gen~ contro modello (`prova_mic.py`)

**PASS 106/106**, su tutte e due le uscite:
- GAIN su 5 posizioni, passa-alto a 40/60/100 Hz, EQ2 su 4 casi: entro
  0,05 dB.
- Ingresso destro ignorato (errore 0).
- Front-end tosato (GAIN 100 %, 100 mV al mic): fondamentale entro
  0,01 dB dal modello. Il picco dell'onda tosata esce a 15,6 V invece di
  13,5: è il halfband del ritorno a 48 kHz (Gibbs), non un errore.
- MUTE: aperto = modello, chiuso = silenzio, anche sulle mandate.
- FX1-FX4: ogni manopola accende solo il suo bus, L e R, a 0 dB e a
  −20 dB (metà corsa).
- LED: spento a −10 dBu, verde a 0, giallo a +14, rosso a +18, uguale col
  MUTE acceso; il rosso resta 0,5 s dopo il colpo.

Nomi gen~: nessuna collisione (`nomi_in_comune`).

## 4. Limiti

- Niente rumore: il fruscio del microfono amplificato (mic-mono §6: sopra
  ~45 dB di GAIN il sistema supera il target) qui è il fruscio della
  scheda audio, non quello del circuito.
- Saturazione del front-end a taglio netto; il circuito vero tosa un po'
  più morbido.
- Il LED gira sul picco dei 4 campioni del sovracampionamento; il
  detector del circuito è analogico.

## 5. Da sentire (domande per l'ascolto di Filippo)

1. Serve un limiter sul mic? (idea della review, non discussa: non è nel
   dispositivo, si decide a orecchio).
2. LED: le tre soglie si accendono nel punto giusto mentre l'MC parla e
   urla (B6)?
3. GAIN: col pot lineare l'ultimo 10 % fa 8,4 dB. Si regola bene a mano
   (voce 40)?
4. MUTE: il tasto suona pulito, senza click?
5. Le mandate FX1-FX4: la voce nell'eco del dub con la law curva A.
