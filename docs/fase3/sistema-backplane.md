# Sistema backplane (questione 22 + parte 38) — v0.2 [PROVVISORIO — regola 3; potenza REV dec. 93]

Data: 2026-10-01 (workstream S3, piano `00-piano-sistema.md`, dec. 90;
v0.2 stessa data: TASK 0 riconciliazione rail, dec. 93).
Vincoli [BLOCCATI] da SPECIFICA §3 [REV decisione 93]: bus potenza sul
backplane = **raw ±27 V audio, raw ±22 V LN/OTA, raw ±26 V [M] HV (solo
master), +5 V control (regolato nella PSU), analogue 0 V, control ground,
chassis/shield** (il «±24 V unico» del consolidamento 2026-09-18 è
SUPERATO: attuazione dec. 90(c) — secondari dedicati + regolazione
locale); i rail ±18 V audio e ±15 V LN si generano LOCALMENTE in ogni
modulo, ciascuno dal suo raw (dec. 45 + miglioria §3 + dec. 93);
separazione fisica audio/controllo/potenza/ground; connettori robusti
card-edge/board-to-board con keying; nessun bus floating; no hot-swap;
test point per modulo; CV 0-5 V = convenzione d'interfaccia. Masse:
topologia in `sistema-grounding.md` (stella unica alla PSU; qui viaggiano
i ritorni dedicati).

## 1. Famiglia connettori — scelta

| Candidato | Pro | Contro | Esito |
|---|---|---|---|
| **DIN 41612 tipo C (3×32 = 96 pos, passo 2,54 mm)** | 3 file FISICHE separate = la separazione potenza/audio/controllo [BLOCCATA] viene gratis (riga a/b/c); 2,2-3 A/pin; keying/codifica meccanica nativa; storico pro-audio/broadcast; ancora prodotto (TE/HARTING/ept + clone economici); versione angolo retto per moduli verticali | costo medio (~4-8 €/coppia); serve PCB o telaio forato | **SCELTA [PROVVISORIO — q29 meccanica]** |
| Card-edge 2×50 (gold fingers) | economico, meccanica semplice | solo 2 file (separazione per posizione, non fisica); usura delle dita a inserzioni ripetute; keying solo per intaglio; corrente/pin ~1 A | fallback se il budget meccanico (q29) lo impone |
| D-sub HD 44 | reperibile, robusto | non è un backplane (point-to-point per modulo); densità bassa per 40+ segnali | scartato |
| Molex Mini-Fit Jr | 9 A/pin, keying per housing | densità bassa sui segnali, ingombro; soluzione ibrida = due famiglie da gestire | scartato (ibrido possibile solo per la PSU) |

Corrente per pin: 2,2 A nominale IEC 60603-2 (derating ~30% con pin
adiacenti carichi) → i 2 pin per rail raw del §3 (REV dec. 93) danno
capacità ≥3 A contro un assorbimento max per raw di 1,1 A (§6):
margine ≥2,7× (≥4× sul tipico 0,9 A).

## 2. Classi di modulo e connettori

| Classe | Qtà moduli | Connettori | Note |
|---|---|---|---|
| CDJ CH1-4 | 4 | 1×C96 | out DJ bus, cue, send tap (→FX-SEND, dec. 91), filter I/F + mode bit |
| FX-SEND | 4 | 1×C96 | micro-modulo send (dec. 91a): EQ2+level+assign di UN canale; bottoni via harness dal pannello canale |
| FILTRO | 1 | 1×C96 | 4 canali × (send in + return out) = 8 slot stereo, 8 mode bit in |
| 5-WAY | 1 | 1×C96 | DJ bus in → out MASTER SUM |
| FX | 1 | 1×C96 | 4 bus-net in (multidrop, dec. 91) + 4 return out = 8 slot stereo |
| MASTER | 1 | 1×C96 | 7 contributori MASTER SUM + MON out verso CUE |
| CUE | 1 | 1×C96 | 4 cue in + MON in; ampli cuffia locale |
| MIC | 1 | 1×C96 | send FX + out MASTER SUM |
| GENERIC MONO | 1..n | 1×C96 | come MIC |
| PSU | 1 | 1×C96 (lato distribuzione) + morsetti/viti per ingresso rete e secondari | la PSU È la stella (§grounding): i radiali AGND partono dal suo connettore |
| UTILITY/spare | 2 | 2×C96 | future/prototipi (SPECIFICA §3 "utility/future") |

Totale: ~19 connettori femmina sul backplane (maschi sui moduli, angolo
retto, montaggio a pannello) [REV dec. 91: +4 FX-SEND].

## 3. Riga a — POTENZA (mappa IDENTICA per tutte le classi — REV decisione 93)

| Pos | Segnale | Note |
|---|---|---|
| a1-a2 | +27 V raw AUDIO | 2 pin paralleli (≥3 A vs 1,1 A max); ferrite + bulk locale nel modulo (sheet §1) |
| a3-a4 | −27 V raw AUDIO | idem |
| a5-a6 | +22 V raw LN/OTA | 2 pin (≥3 A vs 0,5 A max) |
| a7-a8 | −22 V raw LN/OTA | idem |
| a9-a10 | +26 V raw [M] HV | solo master: la mappa è identica ma SOLO il modulo MASTER popola ferrite+bulk su questi pin |
| a11-a12 | −26 V raw [M] HV | idem |
| a13-a20 | AGND (analogue 0 V, ritorni) | 8 pin = <1 mΩ di percorso; è il radiale di stella del modulo |
| a21-a22 | +5 V control | REGOLATO nella PSU (dec. 93); LED/logiche; 2 pin ≈ 4 A capacità vs 1,25 A di dimensionamento |
| a23-a24 | CTRL_GND | ritorno logico/CV; bond ad AGND solo alla stella PSU |
| a25-a26 | CHASSIS/SHIELD | alla piastra di montaggio del modulo (bond chassis unico alla stella) |
| a27-a32 | SPARE | riserva (es. −5 V futuro, +48 V phantom se il mic cambiasse — oggi NO phantom [BLOCCATO V1]) |

I rail audio ±18 V e ±15 V LN NON viaggiano sul backplane [BLOCCATO]:
ogni modulo li genera dal SUO raw dedicato (dec. 93): ±18,0 V =
LM317/337 a 19,2 V + cap-moltiplicatore dal ±27; ±15,0 V LN = pre-reg
±16,5 (LM317/337) → LT3045/94 dal ±22 (dec. 54 — LT3045 Vin max 20 V,
Vout max 15 V); ±15 V switch (ADG14xx-class, dec. 88/90) = 78L15/79L15
diretti dal ±22. Il modulo MASTER genera tutto dal ±26 [M] (LDO locali
±18/±15, master-out [M] REV). Eccezione sense: il MASTER sente i raw
±27/±22 sui propri pin di riga a per il supervisor mute (finestre per
avvolgimento, S1 §4 v0.2) — solo lettura di tensione, nessun assorbimento.

## 4. Riga b — AUDIO (single-ended 0 dBu, convenzione q38 confermata qui [PROVVISORIO])

Struttura: **10 slot stereo** (L, R, AGND) = 30 posizioni + 2 spare
(b31-b32). L'AGND ogni 3 pin isola gli slot adiacenti (capacità pin-pin
~0,5-1 pF: crosstalk stimato < −100 dB a 20 kHz su impedenze 10k —
coerente col misurato DJ bus −98 dB @1 kHz / −72 @20 kHz, `sim/cdj/`).

Semantica degli slot PER CLASSE (slot 1 = b1-b3, slot 2 = b4-b6, …):

| Slot | CDJ (CHn) | FILTRO | 5-WAY | FX | MASTER | CUE | MIC/GEN |
|---|---|---|---|---|---|---|---|
| 1 | DJBUS out L/R | CH1 send in | DJBUS in L/R | BUS1 net in¹ | MSUM1 in (5-way) | CUE1 in (CH1) | MSUM out |
| 2 | CUE out L/R | CH1 return out | MSUM out L/R | BUS2 net in¹ | MSUM2 in (FX1) | CUE2 in (CH2) | FXSEND out (net¹) |
| 3 | SEND TAP out (→FX-SEND) | CH2 send in | — | BUS3 net in¹ | MSUM3 in (FX2) | CUE3 in (CH3) | — |
| 4 | FILT_SEND out L/R | CH2 return out | — | BUS4 net in¹ | MSUM4 in (FX3) | CUE4 in (CH4) | — |
| 5 | FILT_RET in L/R | CH3 send in | — | RET1 out (→MSUM2) | MSUM5 in (FX4) | MON in (master) | — |
| 6 | — | CH3 return out | — | RET2 out (→MSUM3) | MSUM6 in (mic) | — | — |
| 7 | — | CH4 send in | — | RET3 out (→MSUM4) | MSUM7 in (generic) | — | — |
| 8 | — | CH4 return out | — | RET4 out (→MSUM5) | MON out L/R | — | — |
| 9-10 | spare | spare | spare | spare | spare | spare | spare |

¹ **REV dec. 91 (2026-10-01)**: i bus FX S1-S4 sono NET MULTIDROP (stessa
convenzione del DJ bus): i 4 moduli FX-SEND (out S1-S4), MIC e GEN
iniettano ciascuno con la propria R 10k lato sorgente sullo stesso net;
il modulo FX riceve il net sul pin e somma sul virtual-earth (Rf 10k
locale, fx-module §3). Il SEND TAP del canale CDJ (slot 3) va allo slot 1
del proprio FX-SEND. Classe **FX-SEND** (×4): slot 1 = SEND_IN L/R (da
CDJ n), slot 2-5 = S1_OUT…S4_OUT L/R (sui net di bus), slot 6-10 = spare;
riga a/c come mappa comune (raw ±27 → ±18 audio locale, raw ±22 → ±15
switch locale 78L15/79L15, +5 V control per i pull-up bottoni; bottoni assign = harness diretto dal
pannello canale al front connector del modulo, NON sulla riga c: la mappa
controllo resta identica per tutte le classi).

Regole elettriche: driver di modulo ≤50 Ω (out driver dedicati, come il
canale CDJ); ricevitore = iniezione 10 kΩ su summing a massa virtuale
(DJ bus, MASTER SUM, FX send, CUE sum) o buffer ≥100 k (filter send,
cue monitor); nessun doppino terminato/impedenza caratteristica: con
≤0,5 m di percorso e ≤40 kHz di banda (fx §8.4) le linee sono
elettricamente corte (λ = km). Bilanciato solo verso l'esterno
(XLR master/mic [BLOCCATO]).

## 5. Riga c — CONTROLLO/CV (mappa IDENTICA per tutte le classi)

| Pos | Segnale | Note |
|---|---|---|
| c1-c8 | FILT_MODE CH1-4 [1:0] | 8 bit: 2 per canale (HPF/OFF/LPF), dal pannello canale al modulo filtro; livelli 0/+5 V, serie 10k, pull-down 100k lato filtro (stessa disciplina del pilotaggio kill §8.10 five-way); filtro con bit assente = OFF (bypass secco) |
| c9 | GLOBAL_MUTE | dal controller mute del master (supervisore rail + timer, master-out §3.7): lo ascoltano i relay di uscita dei moduli che ne hanno uno + i buffer d'iniezione dei 4 FX-SEND (dec. 94(b): i send mutano col mute globale — nessuna eccitazione della matrice self-FB nelle transizioni) |
| c10-c13 | CV_BUS 0-5 V ×4 | convenzione d'interfaccia [BLOCCATO]: CV remoti (es. filter freq shared, utility); generazione nel dominio ±15 V LN (sheet §1) |
| c14-c15 | LED_DIM / SVC | dimming LED comune (PWM lento dal PSU) + linea di servizio spare |
| c16, c20, c24, c28 | CTRL_GND | ritorni intercalati: ogni gruppo di segnali ha il suo ritorno adiacente |
| c17-c19, c21-c23, c25-c27, c29-c32 | SPARE | riserva (future: meter link, automation, MIDI…) |

## 6. Correnti stimate per classe e per raw [PROVVISORIO — il calcolo esatto è di S1/PSU; REV dec. 93: split per rail dedicato]

| Classe | ±27 audio (tip/max) | ±22 LN (tip/max) | ±26 [M] | +5 V | Nota dominante |
|---|---|---|---|---|---|
| CDJ ×4 | ±65/±110 mA cad. | ±17/±40 cad. (phono LN) | — | ~20 mA | op-amp ~24 sezioni + 1-3 VCA |
| 5-WAY | ±250/±350 mA | ~5/10 (Iq 78L15 switch) | — | ~20 mA | ~35 quad + 2 VCA + 3 switch IC (µA) |
| FILTRO | ±110/±150 mA | ±65-100/±190 (OTA + riserva c-B) | — | ~20 mA | 8 core OTA (Iabc!) + ~20 quad |
| FX | ±180/±300 mA [PROVV] | — | — | ~20 mA | 20 VCA 218x (16 matrice + 4 ritorno gain, dec. 91b) + op-amp |
| FX-SEND ×4 (dec. 91) | ±40/±60 mA cad. | ~5/10 cad. (78L15 switch) | — | ~10 mA | ~18 sezioni op-amp + 2 switch IC (µA) |
| MASTER | — (LDO ±18/±15 locali da [M]) | — | ±130/±170 | ~30 mA | HV stage Iq 40 mA×2 + summing/meter + LDO locali |
| CUE | ±50/±110 [PROVV fino a S5] | ±30/±90 (ampli cuffia LN) | — | ~20 mA | 1 Vrms/32 Ω ×2 uscite |
| MIC/GEN | ±10/±20 cad. | ±20/±30 cad. (preamp LN) | — | ~10 mA | preamp + EQ2 |
| LED/metering (tutti) | — | ±100/±125 (albero riferimenti) | — | 200/500 mA | dato S4: ~103 segmenti (master 2×20 + zone 10×~6), 2 mA typ / 5 mA worst |
| **Totale per raw** | **~±0,9-1,0 A tip** (somma dei max singoli ~1,5 A — nota sotto) | **~±0,28 A tip / ±0,45 A picco** (+switch µA-Iq) | **±0,13/±0,17 A** | **~0,55/1,0 A worst** (dimensionamento 1,25 A) | W1 1,2 A/lato · W2 0,6 A · W3 0,3 A · W4 1,2 A (S1 §2 v0.2) |

Nota sui massimi (dec. 93): i «max» per classe sono inviluppi conservativi
del PICCO DI SEGNALE (scala ms) del singolo modulo — non si presentano mai
tutti insieme (crest factor musicale). Il trasformatore è dimensionato sui
totali tipici (S1 §1: 0,9 A audio, 0,28 A LN, 130 mA [M], 0,55 A +5) e il
bulk (2×10 mF per W1/W2) fornisce i picchi; la somma dei max singoli
(~1,5 A su ±27) serve solo al dimensionamento delle piste del singolo
ramo e dei fusibili di ramo (S1 §4).

## 7. Keying, meccanica, riparabilità

1. **Codifica per classe**: i connettori DIN 41612 accettano pin di
   codifica/guide in posizioni diverse → ogni classe ha la SUA codifica
   (CDJ, FILTRO, …): l'inserimento errato è meccanicamente impossibile.
   In aggiunta: etichetta classe sul telaio + colore della maniglia
   estrattore per classe [principio RATIFICATO dec. 94(c); palette e
   hardware = voce 40 — sessione hardware].
2. **Meccanica proposta**: backplane orizzontale sul fondo del telaio;
   moduli verticali, appesi al pannello frontale (viti + rondelle
   dentate per continuità chassis), connettore maschio angolo retto che
   innesta verso il basso; guide laterali in lamiera per l'allineamento.
   Manutenzione: sviti il pannello, sfili il modulo — nessuna rimozione
   di cablaggio. Ingombri esatti = questione 29 (pannello di Filippo).
3. **Comportamento a modulo rimosso** (q38): sistema SPENTO (no
   hot-swap [BLOCCATO]). Ad ogni modo: le uscite dei moduli assenti non
   caricano i bus (i bus sono ingressi a massa virtuale con iniezione
   10k: un modulo assente = un'assenza, non un carico — crosstalk e
   somma già validati così, `sim/cdj/djbus-*`); un modulo PRESENTE MA
   SPENTO può essere alimentato di rimando dai pin audio (diodi ESD
   degli op-amp): la serie ≥470 Ω-10k su ogni linea limita la corrente
   <1 mA = sicuro; regola di servizio: mai alimentare segnali esterni
   col mixer spento.
4. **Backplane fase 1** (prototipo validazione: CDJ + FX + master + PSU
   base, SPECIFICA §fase): stessa famiglia connettori, 4 slot + 2 spare,
   anche millefori con barra AGND in rame (§8 grounding); il pinout è
   già quello definitivo → la fase 1 valida davvero il backplane.

## 8. Costruzione backplane

- PCB 2 strati minimo (lato componenti = segnali, lato saldature =
  pour AGND + piste potenza rinforzate); piste raw (±27/±22/±26[M])
  ≥ 2,5 mm o doppie, +5 V ≥ 1,5 mm (dec. 93);
  AGND pour continuo sotto la riga a; riga b con AGND di slot a pour
  dedicato; riga c separata da pista CTRL_GND.
- In alternativa fase 1: millefori + barra di rame AGND 4×20 mm, fili
  radiali 1,5 mm² per la potenza, cavetto schermato a coppie per l'audio
  (ogni slot stereo = 1 cavetto 3 conduttori con drain a AGND).
- Ogni connettore: condensatori di bypass 100 n tra pin potenza e AGND
  lato backplane + 10 µ bulk per slot di modulo.

## 9. Chiusure per q38 — RATIFICATE 2026-10-01 → decisione 94(a)

1. Standard elettrico I/O backplane: **single-ended 0 dBu tra moduli,
   bilanciato solo verso l'esterno** (la proposta provvisoria dell'export
   è confermata dai numeri: rumore/crosstalk validati su questa base).
2. Ingressi MASTER SUM: **7 contributori stereo** (5-way, 4 FX return,
   mic, generic) — il summing vive nel modulo master (inverting
   virtual-earth, `master-out.md` §A2).
3. Summing finale: modulo MASTER (già [BLOCCATO] SPECIFICA:127).

## 10. Assunzioni dichiarate

- Moduli = schede verticali dietro pannello (non card-cage Eurocard):
  il DIN 41612 angolo retto lo permette; se q29 sceglie il card-cage,
  stessa famiglia, montaggio diverso.
- Un backplane unico (non segmentato): ~15 slot in linea, lunghezza
  ≤70-80 cm [PROVVISORIO — q29]; a quella lunghezza le cadute sui raw
  sono <10 mV con piste §8 (loop ~6 mΩ su 2,5 mm² × 0,7 m a 1,1 A —
  dentro il margine dropout dei regolatori locali, verifica S1 §2 v0.2).
- FX = modulo unico con matrice interna (accorpamento dei 4 FX RETURN
  dei doc: da ratificare in fase di layout, SPECIFICA §3).
