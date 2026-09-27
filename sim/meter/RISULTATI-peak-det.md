# PEAK DETECTOR CONDIVISO — risultati simulazioni (2026-09-27)

Riferimenti: CDJ §7.3 (`docs/fase1/cdj-line-channel.md`), FX §11.2
(`docs/fase1/fx-module.md`), 5-way §5 (`docs/fase2/five-way-module.md`),
questione 19 (costanti/zona display), decisione 65 (ballistica 10 Hz),
SPEC §7 (clip latch 300-500 ms). Netlist: `peak-det-lf.cir` (droop),
`peak-det-hfclip.cir` (cattura + latch), `peak-det-latch.cir` (timing latch
con finestra lunga). Macro op-amp: `sim/lib/opamp-audio.inc` (OP1612 +
variante OPDET con clamp anti-saturazione −1,5 V = diodo anti-windup reale).

## Circuito candidato [PROVVISORIO — regola 3]

Buffer in → superdiodo (op-amp + 1N4148 in loop: la precisione viene dal
guadagno d'anello, non dal Vf) → C hold 100 nF → R release → buffer out →
comparatore di soglia + one-shot RC (latch clip). Anti-windup: clamp
dell'uscita op-amp a ~−1,5 V (nel reale: diodo dal pin out a riferimento;
SENZA clamp l'op-amp satura a −rail e la R di re-chiusura d'anello scarica
il hold — verificato: droop falsato fino a 4×).

## 1. Droop a 10 Hz (dec. 65 "no sagging") — dati per questione 19

Decay puro misurato (hold caricato a 1,0952 V = picco 0 dBu, poi ingresso
a zero): il droop tra due picchi consecutivi a 10 Hz (Δt = 100 ms):

| τ release | Hold dopo 50 ms | Dopo 100 ms | Droop per ciclo |
|---|---|---|---|
| 0,3 s | 0,927 V | 0,783 V | **−2,9 dB** (pulsazione visibile) |
| 1 s | 1,041 V | 0,989 V | **−0,88 dB** (lieve) |
| 3 s | 1,077 V | 1,057 V | **−0,31 dB** (non percepibile) |

Conformità teoria esponenziale entro 0,5% (leakage 1N4148). Lettura per la
questione 19: "senza sagging" a 10 Hz ⇒ τ release del meter ≥ 1 s (meglio
3 s), oppure peak-hold con reset (automatico lento o manuale). La costante
300-500 ms della SPEC vale per il LATCH CLIP (nodo separato), non per la
ballistica di rilascio del meter: le due costanti convivono.

## 2. Accuratezza di cattura

- 1 kHz, 0 dBu: hold = 1,09607 V contro picco 1,096 V → errore +0,006 %
  (il superdiodo rimuove il Vf: precisione da guadagno d'anello) ✓
- Burst +18 dBu (8,7 Vp): hold = 8,7002 V → cattura esatta ✓
- 35 kHz: hold = 1,60 V (+45 %): **artefatto del macromodello** — l'anello
  di carica ha due poli a β = 1 col macro a singolo polo e ringa sul fronte.
  Il progetto reale (op-amp veri, C hold più piccolo, rete compensata o IC
  di metering) va verificato a banco in beta-3. Limite macro documentato,
  non è un finding sul circuito.

## 3. Clip latch (SPEC 300-500 ms) — meccanismo dimostrato

Comparatore (soglia d'esempio 8 V ≈ +18,3 dBu) + one-shot RC (τ = 0,7 s →
tempo sopra soglia 2,5 V = τ·ln(4,75/2,5) ≈ 450 ms): il flag resta alto
**442 ms** dopo che l'hold scende sotto soglia (misura `peak-det-latch.cir`,
burst +18 dBu 2 ms), retriggerabile se il clip si ripresenta. Soglie/zona
red e purple = questione 19/54 (display: design di sistema).

## Lezioni (si aggiungono alla lista LTspice di progetto)

- Nodo hold di un peak detector: ogni percorso verso uscite saturate è una
  via di scarica (R anti-windup verso op-amp a −rail = droop 4× falsato).
  Clamp a −1,5 V e niente R sul nodo hold.
- PWL: `10m` = 10 millisecondi (non 10 minuti) — punti non monotoni = run
  rifiutato.
- La dinamica di cattura del superdiodo non è simulabile credibilmente col
  macromodello a polo singolo: droop/latch sì (lenti), fronti HF no.
