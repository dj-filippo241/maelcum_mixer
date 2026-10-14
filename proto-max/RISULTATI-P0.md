# RISULTATI P0 — MC-CHANNEL (2026-10-14)

Piano: `docs/proto-max/piano.md` §2 P0 e §3. Generatore:
`proto-max/coefficienti/genera.py` (numeri in `canale.py`).

## Cosa contiene

- GAIN −∞ … 0 … +10 dB, law del VCA di canale (`sim/cdj/vca-law.cir`):
  metà CCW lineare in dB da −100 a 0, metà CW da 0 a +10.
- Isolator v0.4 (`eq-isolator-v0.4.md` §3, §9): banca LR4, allpass del
  2° ordine, pot lineare ×2, silenzio a fondo corsa (contatto).
  Selettore A 150/500/2500 Hz, C 150 dolce/350/3150 Hz (B7; fino al
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

