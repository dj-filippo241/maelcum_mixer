# FX-SEND — micro-modulo send FX (decisione 91)

> **Stato: v0.1-WIP (2026-10-01)** — design nuovo da decisione 91 (a):
> EQ2 + level + switch assign ESCONO dal canale CDJ e vivono in un
> micro-modulo separato, **uno identico per canale (4× stesso PCB)**.
> I 4 bottoni assign RESTANO sul pannello del canale e pilotano gli
> switch via linee logiche +5 V (l'audio non passa dai contatti pannello:
> schema del kill 5-way, five-way §8.10 / dec. 88).
> Comportamenti LOCKED di SPECIFICA §2 riga FX SEND **INVARIATI**:
> punto di presa post-EQ/pre-filter/pre-fader · EQ2 LOW ~120 Hz /
> HIGH ~4,5 kHz −∞→0→+6 con law dedicate · level −∞…0 (niente gain
> positivo) · assign S1-S4 multipli e simultanei · BBM + ramp 1 ms
> (dec. 80) · iniezione bufferizzata sui bus (mai passiva diretta).
> Valori [PROVVISORIO — regola 3]. Rail: ±18 V audio locale, ±15 V
> switch locale, +5 V control dal backplane (riga a).

## 1. Perché un micro-modulo

Il canale CDJ v0.4 portava a bordo la sezione send (EQ2 + level + 4
switch): dec. 91 la sposta in un modulo dedicato per tre motivi:
1. pannello: la striscia canale resta pulita (solo bottoni assign), i
   controlli di colore/mandata vivono nella sezione FX (ergonomia =
   voce 40);
2. manutenzione/upgrade: la sezione send è identica ×4 (un solo PCB,
   4 copie) ed è servibile senza aprire il canale;
3. coerenza: gli switch assign stanno vicino alla logica di pilotaggio
   e ai rail ±15 V switch (stessa famiglia π SPDT del kill, dec. 88/90).

Costo: un attraversamento backplane in più sul send (tap canale →
micro-modulo), elettricamente ininfluente (linea corta ≤0,5 m, driver
≤50 Ω, banda 40 kHz — convenzione backplane §4).

## 2. Catena per canale (il modulo ospita UN canale, L e R)

```
IN L/R (send tap dal canale CDJ, post-EQ/pre-filter/pre-fader,
        bufferizzato ≤50 Ω lato canale — cdj §3.5 REV)
  │
  ▼ BUFFER IN unity (OPA1612 ×2: isola il driver di canale, definisce
  │  il carico; la sezione era già bufferizzata: doppio buffer =
  │  ridondanza innocua, tiene il modulo autonomo)
  ▼ EQ2 — celle serie scalate (stessa famiglia EQ v0.3/dec. 76-77,
  │  valori da fx-module §6 / sim fx-eq2.cir):
  │  LOW shelf ~120 Hz (1 op-amp/lato): law "tiene i bassi per quasi
  │    tutta la corsa, toglie rapido solo al taglio estremo" [BLOCCATO]
  │  HIGH sottrattiva ~4,5 kHz (3 op-amp/lato): "taglia subito in
  │    partenza, poi graduale" [BLOCCATO]; il kill HIGH dà bump +2,1 dB
  │    al corner (questione 68 si applica, come sul canale)
  │  pot doppi 10k custom taper (voce 40/85 famiglia), −∞→0→+6
  ▼ LEVEL pot doppio 10k log [PROVVISORIO — taper custom candidato
  │  voce 40]: divisore passivo −∞…0 dB, nessun gain positivo [BLOCCATO]
  ▼ ASSIGN ×4 destinazioni (S1-S4): π SPDT famiglia ADG1434-class
  │  (serie + shunt a GND da off, Ron ≤4,7 Ω — stessa topologia e
  │  famiglia del kill 5-way, five-way §8.10): 8 switch stereo =
  │  2× quad SPDT per modulo. Multipli e simultanei [BLOCCATO]:
  │  ogni destinazione è indipendente, nessuna esclusività.
  │  SOFT-SWITCH: la ramp 1 ms [BLOCCATO dec. 80] si ottiene rallentando
  │  il fronte sul pin IN (R 10k serie + C 100 nF + pull-down 10k =
  │  τ ≈ 0,5-1 ms): durante la transizione il Ron attraversa la regione
  │  resistiva → apertura/chiusura graduale, click −9 dB class (famiglia
  │  dati §8.5 five-way: ramp 1 ms vs brusco). BBM intrinseco dello SPDT.
  ▼ BUFFER DI INIEZIONE unity (OPA1654 quad ×2: 8 sezioni) + R 10k di
    iniezione per linea → OUT S1-S4 L/R (8 linee) → backplane →
    summing virtual-earth dei bus FX (fx-module §3: multidrop come
    il DJ bus, ogni sorgente col proprio 10k lato sorgente)
```

Conteggio silicon per modulo: 2 buffer in + 8 EQ2 (1+3 per lato) +
8 iniezione = 18 sezioni ≈ 4,5 quad → **5 quad/modulo** (OPA1654 per
l'audio, OPA1612 per i buffer in [PROVVISORIO]) + 2 quad SPDT.
×4 moduli: ~20 quad + 8 SPDT.

## 3. Pilotaggio bottoni (pannello canale → micro-modulo)

- 4 bottoni per canale sul pannello del canale CDJ (gesto invariato).
- Cablaggio: **harness diretto pannello → connettore frontale del
  micro-modulo** (6 fili/canale: 4 IN + ritorno CTRL_GND; il +5 V lo
  fornisce il micro-modulo dalla riga a del backplane). Non passa dal
  modulo canale né dal backplane: la riga c ha mappa IDENTICA per tutte
  le classi (backplane §5) e non si aggiungono pin logici per classe.
- Cella per bottone: +5 V ctrl → bottone → R 10k → pin IN (con
  C 100 nF e pull-down 10k lato modulo) = ramp ~0,5-1 ms in chiusura;
  apertura scarica via pull-down (τ ≈ 1 ms simmetrico).
- Logica: IN alto = serie chiuso/shunt aperto = send attivo. Bottoni
  multipli = più IN alti simultaneamente (nessuna interdipendenza).
- Audio MAI dai contatti (usura/crackle evitati — dec. 88 schema kill).

## 4. Interfaccia backplane (classe FX-SEND, pinout nel doc backplane)

| Slot riga b | Segnale | Direzione |
|---|---|---|
| 1 | SEND_IN L/R (dal canale CDJ n, slot 3 CDJ) | in |
| 2 | S1_OUT L/R (→ net bus 1, multidrop con gli altri 3 moduli + mic/gen) | out |
| 3 | S2_OUT L/R (→ net bus 2) | out |
| 4 | S3_OUT L/R (→ net bus 3) | out |
| 5 | S4_OUT L/R (→ net bus 4) | out |
| 6-10 | spare | — |

Riga a: ±24 V raw → ±18 V audio locale (LM317/337 + cap-moltiplicatore,
sheet §1), ±15 V switch locale (LDO, dec. 88/90), +5 V control, AGND
radiale, CTRL_GND, CHASSIS. Riga c: GLOBAL_MUTE in ascolto (i buffer
d'iniezione mutano all'accensione se il supervisore lo chiede —
coerente col mastering §3.7; [PROVVISORIO: valutare se il send deve
mutare col mute globale o restare vivo per i pedali]).

Front connector (harness pannello): 3 pot doppi (LOW, HIGH, LEVEL =
9 pin + schermi) + 4 linee bottoni + CTRL_GND. Layout pannello = voce 40.

## 5. BOM per modulo [PROVVISORIO — regola 3]

| Voce | Qtà | Note |
|---|---|---|
| OPA1654 quad | 3 | EQ2 HIGH + iniezione (audio low-noise) |
| OPA1612 dual | 1 | buffer in |
| ADG1434-class quad SPDT | 2 | assign π (famiglia kill/dec. 90c) |
| LDO ±15 V switch (78L15/79L15 o LDO low-noise) | 2 | da ±24 raw locali |
| LM317/LM337 + passivi cap-moltiplicatore | 2 | ±18 V audio |
| Pot doppi 10k custom taper (LOW/HIGH/LEVEL) | 3 | voce 40/85 |
| Reti RC celle (0,1% shelf, C0G/PP), R iniezione 10k, RC soft-switch | — | |
| Connettore C96 + front connector | 2 | backplane §7 |

Costo stimato: ~25-35 €/modulo, ~100-140 € per i 4 [PROVVISORIO].
Delta vs v0.4 canale: il canale perde ~9 sezioni op-amp + 8 switch +
3 pot (scende a ~28-30 €/canale di silicon): il costo totale di sistema
sale di ~+30-50 € (4 connettori + 4 PCB + rail locali) — prezzo della
separabilità, accettato da dec. 91.

## 6. Rumore (nota per il sistema)

La sezione send NON tocca il percorso principale del canale (il budget
canale −90,3 dBu A-wtd resta valido: il tap è un'uscita bufferizzata in
parallelo). Il rumore del micro-modulo viaggia solo verso i bus FX:
EQ2+level+buffer ≈ classe EQ β3 ridotta (2 celle vs 4) ≈ −95 dBu per
canale stimato [PROVVISORIO — da misurare nella campagna di verifica:
il budget FX send −100,8 dBu (RISULTATI-fx-noise-71A) assumeva
contributori TERMINATI: a canali vivi il send chain contribuisce; la
somma di 4 send vivi + bus resta comunque ≥15 dB sotto il sistema
−80,5 dBu A-wtd → nessuna ritaratura attesa].

## 7. Simulazioni

- Soft-switch assign: click = famiglia ramp 1 ms (§8.5 five-way:
  −8,4…−9,6 dB vs brusco); la cella RC sul pin IN sposta la commutazione
  nella regione resistiva del Ron → verifica a banco (charge injection
  reale ADG1434 non nel modello).
- Iniezione multidrop: coperta da fx-summing.cir (virtual-earth, 12
  sorgenti, worst +21,5 dBu nessun clip) e djbus (crosstalk −98 dB @1k).
- Self-feedback (dec. 91b): `sim/fx/fx-loop-self.cir` +
  `RISULTATI-fx-self.md` — bounded-by-design CONFERMATO sul ramo self.

## 8. Aperti / voce 40 / reperibilità

- Taper custom dei 3 pot (famiglia dec. 85/voce 40): law EQ2 e level
  definite, la meccanica del gesto è da sessione hardware.
- GLOBAL_MUTE sui buffer d'iniezione (vedere §4: scelta da ratificare
  se tocca l'uso — pedali che ricevono segnale durante il mute master).
- ADG1434 datasheet Rev. E + protezioni ESD (task adg1434-datasheet,
  stesso finding del kill 5-way).
- Verifica rumore send chain a canali vivi (coda campagna 71A).
