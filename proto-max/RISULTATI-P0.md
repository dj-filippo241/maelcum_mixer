# RISULTATI P0 — MC-CHANNEL (2026-10-14)

Piano: `docs/proto-max/piano.md` §2 P0 e §3. Generatore:
`proto-max/coefficienti/genera.py` (numeri in `canale.py`).

## Cosa contiene

- GAIN −∞ … 0 … +10 dB, law del VCA di canale (`sim/cdj/vca-law.cir`):
  metà CCW lineare in dB da −100 a 0, metà CW da 0 a +10.
- Isolator v0.4 (`eq-isolator-v0.4.md` §3, §9): banca LR4, allpass del
  2° ordine, pot lineare ×2, silenzio a fondo corsa (contatto).
  Selettore A 150/500/2500 Hz, B 100/630/4000 Hz (B7), dissolvenza
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

## Non verificato

- **Sintassi gen~ e caricamento in Live**: li controlla solo Max.
  Primo controllo di Filippo, `montaggio.md` §4.
- CPU con 4 dispositivi: 240 biquad e 64 sezioni allpass per campione,
  per dispositivo. Stima: pochi punti percentuali di un core.
- Confronto con LTspice dentro Max (rumore rosa, piano §3): sostituito
  dalle due verifiche sopra, che coprono la stessa catena in modo
  ripetibile.
