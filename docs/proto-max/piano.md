# Prototipo Max for Live — piano v0.1 (2026-09-24)

> **AGGIORNAMENTO 2026-10-13 (decisioni 99-104) — da recepire nella proposta
> di ripresa (todo #1); il testo sotto è ancora quello del 24/09.**
> - Drive 5-way: non più «taper dec. 24» ma due manopole, GROWL (sotto
>   350 Hz) e NASTRO, saturatori in parallelo al pulito, volume fermo
>   (five-way §5bis).
> - Overdrive filtro: tosatore simmetrico in parallelo, tetto ~+5,5 dBu,
>   law θ^2,5 (filter-module §5ter).
> - Filtro: un percorso per canale (dec. 101: la voce 63 è chiusa); law
>   FREQ e RES = Xone:96 (dec. 102, tabella in filter-module §4).
> - EQ di canale: in serie v0.3 beta-3 + muto a fine corsa con tutte e 4 le
>   manopole a zero (dec. 104: la voce 59 è chiusa).

> Decisione 78 [F]: prototipo musicale digitale del mixer completo PRIMA del
> millefori. Ambiente: Ableton Live Suite (M4L incluso), controllo a mouse.
> Questo piano è [PROVVISORIO] dove non cita decisioni bloccate.

## 1. Cosa valida e cosa NO

**Valida (a orecchio, subito):**
- Gesto e feel: law dei knob (filtro dec. 70/74, taper EQ dec. 76/77), corse, detent.
- Curve: kill −30 dB delle bande EQ, shelf/bell, sovrapposizioni, all-kill.
- Carattere musicale delle scelte pendenti: allineamento 4 poli (questione 64,
  A/B Butterworth/Bessel/LR in tempo reale), mux filtro single-path vs serie (63),
  drive/distorsione (61: il prototipo È lo strumento per scegliere le referenze),
  centri/Q delle bande EQ (review con Filippo), position/width del 5-way.
- Workflow dub: quanto "suona" la catena completa mentre mixi.

**NON valida (resta al millefori + misure):**
- Rumore, headroom reale, saturazione degli OTA veri, tracking meccanico dei pot,
  PSRR, THD dei componenti. Il drive nel prototipo è un waveshaper candidato:
  approssima il carattere, non è il circuito.

Regola (dec. 78): ciò che viene approvato a orecchio qui diventa requisito
del design circuitale corrispondente.

## 2. Architettura — famiglia di dispositivi "MC-PROTO"

Live elabora un flusso stereo per traccia: il mixer diventa una famiglia di
dispositivi M4L + il routing nativo di Live.

| Dispositivo | Tipo | Dove vive | Contenuto |
|---|---|---|---|
| `MC-CHANNEL` | audio effect ×4 | una per traccia CDJ 1-4 | GAIN (law −∞..0..+10), EQ 4 bande serie (curve v0.3: kill −30 dB, detent esatto, law asimmetrica), switch modo filtro HPF/OFF/LPF (core locale pilotato dal pannello globale), FX SEND (EQ2 + level + assign S1-S4), trim ingresso. Audio FX: `send~ mc_fx1..4`; parametri filtro: `receive` dai messaggi globali |
| `MC-FILTRO` | pannello di controllo | traccia utility (o MIDI effect su una traccia) | 6 knob (HPF/LPF: freq, res, drive), law esponenziale 10 Hz–35 kHz + shaper a tratti (dec. 70), broadcast via `send` a tutti i core canale. Contiene anche l'A/B per la questione 64 (selettore allineamento) |
| `MC-FX` | audio effect | traccia Return FX | 4 bus (`receive~ mc_fx1..4`), pad, "pedale" = segnaposto modellabile (dry/saturo/delay semplice), matrice feedback 3 reroute per ritorno con law a tratti della SPECIFICA §7, fader ritorno, somma → master. Niente vincoli di routing di Live: tutto interno al device |
| `MC-5WAY` | audio effect | gruppo "DJ BUS" | 5 bande kill + EQ creativo position/width + drive (taper dec. 24), riferimento interno −6 dB (dec. 73), meter. Le bande: ~90/350/1,2k/3,5k PROVVISORI (dec. 66) — il prototipo serve ANCHE a confermarle |
| `MC-MASTER` | audio effect | master | level (law VCA), meter 20 segmenti (soglie/colori da SPECIFICA §11), booth/rec = uscite monitor di Live |
| CUE | — | — | NON modellato: il cue/monitor nativo di Live copre il requisito nel prototipo |

DSP: dove possibile oggetti nativi (`biquad~`/`filtercoeff~` per EQ shelf/bell
coefficienti calcolati dalle curve di design); SVF del filtro in `gen~`
(Chamberlin/SMV stabile, auto-oscillazione con soft limiting — stesse equazioni
del design OTA, `docs/fase2/filter-module.md`). Coefficienti e law generati da
script Python nel repo (`proto-max/coefficienti/`) → tabelle/patcher includibili:
la matematica resta versionata e verificabile.

Comunicazione tra dispositivi: `send`/`receive` (messaggi) e `send~`/`receive~`
(audio) — globali nel runtime Max dello stesso set. Latenza: i receive~ vivono
nel device FX sulla traccia Return: verificare il ritardo di un ciclo buffer e,
se udibile, compensare (nudge clip / lookahead) — nota nel test P3.

## 3. Fasi di costruzione (ognuna = set giocabile e commit)

- **P0 — Canale**: `MC-CHANNEL` (gain + EQ 4 bande con curve v0.3 + trim) e
  `MC-PROTO-SET.als` di prova (4 tracce CDJ con loop reggae/dub liberi o tuoi).
  Valida subito: kill −30, detent, law asimmetrica, centri 70/250/1k/5k (review
  con Filippo A/B). Dipendenza: nessuna (le curve target sono già decise; la
  v0.3-beta circuitale può procedere in parallelo e CONFRONTARSI col prototipo).
- **P1 — Filtro**: `MC-FILTRO` + core SVF gen~ nei canali (freq expo 10 Hz–35 kHz,
  res fino ad auto-oscillazione limitata, drive candidato). Chiude a orecchio:
  63 (mux), 64 (allineamento, selettore A/B nel pannello), parte di 61 (drive).
- **P2 — 5-way**: `MC-5WAY` sul gruppo DJ BUS: bande kill, position/width, drive
  (taper dec. 24). Esplora il carattere fase 2 PRIMA del design circuitale
  (regola 5 rispettata: il prototipo insegna, il circuito segue).
- **P3 — FX e master**: `MC-FX` (matrice feedback con law a tratti) + `MC-MASTER`
  (level, meter). Verifica stabilità dei loop di feedback e latenza receive~.
- **P4 — Rifinitura**: mappature complete, preset di partenza (tutto a detent),
  documentazione d'uso, eventuale MIDI mapping futuro.

## 4. Consegna e montaggio (vincolo tecnico onesto)

I file `.amxd` sono binari generabili solo dentro Max. Consegna quindi:
1. Claude scrive le patch come **`.maxpat` testuali** in `proto-max/` (versionate git).
2. Filippo apre Live Suite → crea un nuovo Max Audio Effect vuoto → in Max:
   File > Open del `.maxpat` fornito → seleziona tutto, copia, incolla nel
   device → Save come `.amxd` nella cartella User Library. Procedura di ~10
   minuti la prima volta, guidata passo-passo (documento `proto-max/montaggio.md`,
   da scrivere in P0).
3. Iterazione: modifiche = riapri, re-incolla (o edit diretto in Max con guida).
4. Il set `.als` di prova: salvato da Filippo, condiviso nel repo se utile
   (binario: valutare peso; in alternativa istruzioni di routing).

## 5. Struttura file

```
proto-max/
├── piano.md                  ← questo documento (in docs/proto-max/)
├── MC-CHANNEL.maxpat         ← P0
├── MC-FILTRO.maxpat          ← P1
├── MC-5WAY.maxpat            ← P2
├── MC-FX.maxpat              ← P3
├── MC-MASTER.maxpat          ← P3
├── montaggio.md              ← procedura assemblaggio in Live
└── coefficienti/             ← script Python: law, curve EQ, coeff biquad, tabelle gen~
```

## 6. Questioni toccate

- 61 (referenze distorsione): il prototipo diventa lo strumento di scelta —
  candidati drive ascoltabili in A/B (tanh, asimmetrico, diode-fold, nastro-ish).
- 63 (mux filtro) e 64 (allineamento 4 poli): chiusura a orecchio in P1.
- Review centri/Q EQ e taper law: P0.
- 59 (residuo all-kill): ascoltabile in P0 (curva target), conferma numerica
  resta alla cascata analogica v0.3-beta.
- NUOVA [APERTO-F, P2]: confermare le 5 frequenze di banda (~90/350/1,2k/3,5k,
  dec. 66 PROVVISORI) a orecchio sul 5-way.
- Loopregola: ogni scelta musicale approvata nel prototipo → nota in docs/01
  come requisito del blocco circuitale corrispondente.

## 7. Prossimo passo concreto

P0: `MC-CHANNEL.maxpat` + script coefficienti EQ (curve dalle griglie
`sim/eq-serie/` + legge taper) + `montaggio.md` + set di prova. Stima: una
sessione dedicata.
