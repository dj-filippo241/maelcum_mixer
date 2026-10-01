# RISULTATI — Self-feedback (dec. 91b, 2026-10-01)

Netlist: `fx-loop-self.cir` (loop con pedale), `fx-loop-self-dry.cir`
(dry loop senza pedale), `fx-self-cvsmooth.cir` (smoothing CV ramo self).
Catena comportamentale come `fx-loop.cir` (§8.1): i numeri del self sono
direttamente confrontabili col cross perché la dinamica d'anello è la
stessa (bus → pedale → ritorno → VCA → bus).

## 1. Self con pedale — bounded-by-design CONFERMATO

| g_loop (self al max) | Ampiezza a regime | Interpretazione |
|---|---|---|
| 0,8 | decade a ~0 | eco che si spegne — uso normale |
| 1,0 | sostiene 10 mV iniziali | unity critico autosostenuto |
| 1,2 | **±7,90 V = +20,2 dBu** | cresce e si stabilizza sul tanh del pedale |
| 2,0 | **±11,49 V = +23,4 dBu** | stabilizzato, MAI ai rail (clamp ±16,5 V) |

Identico a §8.1 (cross): il bounding viene dalla saturazione del pedale,
non dai rail — "niente limiter" (SPEC §7) rispettato anche sul self.
Limite del modello (onestà, già documentato in §8.1): zero ritardo e
catena non invertente → l'ampiezza si latcha su una polarità
(ret_pk = ret_min); nel loop reale il ritardo del pedale rigenera l'eco
a tempo, meccanismo di bounding identico. Il carattere si ascolta al
prototipo (pedale vero).

## 2. Dry loop (pedale assente, cavo patch send→return) — caso K4

| g_loop secco | Esito |
|---|---|
| 1,0 | sostiene dalla condizione iniziale (in realtà: il rumore d'ingresso cresce lentamente — unity secco senza elemento saturante) |
| 3,0 | **runaway → clamp ±16,5 V** |
| 10,0 (GAIN ritorno ~+20 dB, self 0 dB) | **runaway → clamp ±16,5 V** |

Senza il tanh del pedale il bounding resta SOLO nei clamp degli stadi
(±16,5 V): oscillazione ai rail, non musicale, **recuperabile chiudendo
il pot self o il GAIN del ritorno** = disciplina operatore K4 (dec. 84),
già accettata da dec. 91 ("senza pedale e pot al max può fischiare").
Nota d'uso per il manuale: il dry loop (patch diretto) è una scelta
estetica legittima SOLO con self sotto unity. Anche qui latch di polarità
= artefatto del modello a zero ritardo.

## 3. Smoothing 1 ms sul ramo self (dec. 80 famiglia)

VCA THAT2181 (macro `sim/lib/that2181.inc`, law 6,1 mV/dB), CV step
0 → −61 mV (0 → −10 dB) a t = 5 ms, audio 1 kHz 2,19 Vp:

| Ramo | Transizione inviluppo | Steady state |
|---|---|---|
| HARD (CV diretta) | 2,19 → 0,69 V in ~10 µs (step = splat larga banda) | −10 dB esatto (0,6925 V, law verificata 1e-4) |
| SOFT (RC 1k/1µ, τ 1 ms) | 2,19 → 0,69 V in ~5 ms (valori intermedi 1,72/−1,20) | identico |

Il ramo self usa lo STESSO shaper a tratti (§8.3, law verificata 13 punti)
e lo stesso smoothing dei 3 pot cross: click −9,6 dB class (dati
`reroute-ramp.cir`). Nessuna verifica aggiuntiva richiesta: la famiglia
è già validata end-to-end.

## 4. Conclusioni per il design

1. Self-feedback = quarto VCA per ritorno (matrice 16×): topologia
   identica ai cross, stesso nodo REROUTE, stessa law/shaper/smoothing.
2. Bounded-by-design confermato col pedale; dry loop = K4 documentato.
3. Accumulo rumore nel self: stesso fattore 1/√(1−g²) di §7 fx-module
   (sotto unity è trascurabile, vicino a unity è mascherato).
