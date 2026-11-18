# FASE 4 — Lickshot in rack 1U: architettura v0.3 (2026-11-18)

> **Stato: v0.2 — requisiti e catena chiusi, topologia per blocchi
> scelta, componenti [PROVVISORIO — regola 3]. v0.2: datasheet del clock
> (MN3102), op-amp TLC2272, un V3102 per BBD, rail dei BBD a 5 V,
> attenuatore −14 dB; PROFONDITÀ e giro simulati in LTspice
> (`sim/lickshot/RISULTATI-lickshot-v02.md`). Legge di TEMPO: pot
> lineare (dec. 193). v0.3: mix e uscita simulati, alimentazione
> calcolata (§5-§6 del RISULTATI); bozza del pannello (§5).** Metodo (regola 4): requisito → funzione di
> trasferimento → topologia → componenti → simulazione → PCB. Questo
> documento arriva alla topologia e alla prima scelta dei componenti.
> Il modello che suona (banco web e MC-LICKSHOT) sta in
> `proto-max/coefficienti/lickshot.py`: è la funzione di trasferimento
> di riferimento, ascoltata da Filippo il 2026-11-18 («mi sembra top»).

## 1. Requisiti (dec. 179-190)

| Voce | Valore | Origine |
|---|---|---|
| Famiglia | analogica dedicata: LFO che piega un oscillatore | dec. 179 [F] |
| Voci | una | dec. 180 [F] |
| Eco | dentro la macchina, BBD, due chip in fila (~400 ms) | dec. 181-182 [F] |
| Trigger | solo il tasto FIRE sul pannello: suona finché è premuto | dec. 183 [F] |
| Comandi | ALTEZZA (64-700 Hz), VELOCITÀ, PROFONDITÀ, VOLUME, TEMPO, RIPETIZIONI, LIVELLO ECO; LED dell'LFO; FIRE | dec. 184, 185, 190, 194 [F] |
| Giro dell'eco | passa-alto e saturazione fissi, senza comandi | dec. 186 [F] |
| Filtri dei BBD | nessuno: niente anti-alias né ricostruzione | dec. 191 [F] |
| Uscita | jack mono sbilanciato, 0 dBu nominale, verso un modulo MONO | dec. 187 [F] |
| Formato | rack 1U | dec. 188 [F] |
| Alimentazione | alimentatore esterno a spina, DC, connettore con blocco | dec. 189 [F] |

## 2. Catena

```
FIRE ─┐
LFO CD4069 ─► PROFONDITÀ ─► VCO CD4046 ─► passa-alto 14,5 Hz ─► FIRE ─► VOLUME ─┬─────────────► MIX ─► USCITA 0 dBu
(VELOCITÀ)    (pot + buffer)  (ALTEZZA)                                          │                ▲ (LIVELLO ECO)
   └─► LED                                                                       ▼                │
                                    SOMMA ─► attenuatore ─► BBD 1 ─► BBD 2 ─► make-up (niente filtri) ─┤
                                      ▲                    clock V3102 (TEMPO)                     │
                                      └── RIPETIZIONI ◄── saturazione ◄── passa-alto 150 Hz ◄──────┘
```

Numeri della catena dal modello (`lickshot.py`, `prova_lickshot.py`):
colpo da 0 a ~4 ottave secondo PROFONDITÀ (2 ottave a ~2/3), da 2 a
33 colpi al secondo (dec. 195), eco 41-410 ms, giro con guadagno fino a 1,1 (oltre
1 l'eco si autoalimenta e la saturazione la tiene).

## 3. Topologia per blocco

### 3.1 Alimentazione [PROVVISORIO]

- Ingresso: jack DC con blocco, **12 V** dall'alimentatore a spina
  (la dec. 189 lascia la tensione all'ingegneria). Diodo Schottky in
  serie (protezione contro l'inversione) e condensatore di ingresso.
- **+9 V** (regolatore lineare 78L09) per CD4069UB, CD4046B e la parte
  audio a bassa tensione. Il nucleo di Nold gira a ~8,6 V (9 V di
  batteria meno il diodo): a 9 V regolati le frequenze salgono di ~5 %;
  `lickshot.py` va riallineato (VDD) quando la tensione è fissata.
- Consumo (v0.3, `RISULTATI-lickshot-v02.md` §6): 9 V ≤ 23 mA, 5 V
  ≤ 27 mA, ~60 mA dall'ingresso. Alimentatore 12 V stabilizzato da
  almeno 200 mA. Il 78L09 prende l'ingresso dopo il 1N5819 (61 mW).
- **+5 V** (78L05) per i due V3205D e i due V3102 (v0.2; prima 7,5 V).
  v0.3: il 78L05 prende l'ingresso attraverso 47 Ω + 100 µF, non i 9 V:
  i picchi del clock restano fuori dal ramo audio (0,15 W nel 78L05).
  IDD del V3205D da rileggere sul datasheet (stimato 10 mA per chip).
  Tutte le caratteristiche del V3205D sono date a 5 V (datasheet,
  «Electrical Characteristics»); il MN3102 garantisce i 200 mW solo
  sotto 7 V (datasheet p. 108). Il V3205D lavora fra 4 e 8 V.
- Riferimenti a metà alimentazione (partitore + buffer) per gli op-amp
  e per la polarizzazione degli ingressi dei BBD.
- **Op-amp: TLC2272** (doppio; TI SLOS190H, rev. marzo 2016) sui 9 V.
  Alimentazione fino a 16 V, uscita fino ai rail, 9 nV/√Hz, 2,2 MHz.
  Limite da rispettare: modo comune d'ingresso fra VDD− e VDD+ − 1,5 V
  (7,5 V a 9 V). Gli stadi audio sono quindi **invertenti** (ingressi
  fermi su VDD/2); i non invertenti solo dove l'ingresso resta sotto
  7,5 V (buffer della rampa e PROFONDITÀ: massimo 6,55 V, simulato).
  Piedini: 1 1OUT, 2 1IN−, 3 1IN+, 4 VDD−/GND, 5 2IN+, 6 2IN−, 7 2OUT,
  8 VDD+ (SLOS190H, «Pin Configuration and Functions»).
- Margine audio a 9 V: ±4,4 V attorno a VDD/2 = +12 dBu sopra lo
  0 dBu nominale. Il picco più alto del giro dell'eco (2,09 V) lascia
  6,5 dB.

### 3.2 LFO (Nold, sigle di Orald-0)

CD4069UB: U1A + U1B trigger di Schmitt (R1 22k in reazione, R4 10k
dall'integratore), U1C integratore di Miller con C1 1 µF film; corrente
da R6 33k (dec. 195; Nold: 22k) + VELOCITÀ 500k. Diodo D3 1N4148 fisso in parallelo alla
resistenza di carica: risalita veloce, discesa lenta, il tono cade a
ogni colpo. Soglie a 6/22 e 16/22 di VDD. LED: inseguitore 2N3904
sull'uscita dell'integratore, LED e 10k. Le porte libere del CD4069UB
(U1D-F) hanno l'ingresso a massa.

### 3.3 PROFONDITÀ (dec. 190) [PROVVISORIO]

L'integratore del 4069 ha un'uscita debole: un buffer la separa dal
pot. Pot lineare fra la rampa bufferizzata e VDD/2; il cursore entra in
un non invertente riferito a VDD/2 con guadagno ~1,49 (escursione
±2,9 V attorno a VDD/2 = 4 ottave col VCO lineare, `A_MAX` del
modello), poi una R in serie al pin 9 del CD4046B. Servono op-amp con
uscita vicina ai rail: a fondo corsa il VCOin va da ~1,4 a ~7,2 V con
VDD 8,6 V.

### 3.4 VCO

CD4046B usato solo come VCO: C1 100 nF film fra i pin 6 e 7, R1 = 10k
+ ALTEZZA 100k logaritmico (reostato, dec. 194) al pin 11, R2 (pin 12)
aperta: fmin = 0. ALTEZZA va da ~64 a 700 Hz (prima 117-700 Hz con
50k lineare), ottave uguali sulla corsa.
Inhibit (pin 5) a massa. Ingressi dei comparatori a massa. f0 ≈ 0,7 /
(R1 C1) dalla Fig. 4 del datasheet; ±30 % fra un chip e l'altro: ALTEZZA
copre la differenza.

### 3.5 Uscita del colpo e FIRE

Onda quadra dal pin 4 → 10 µF → 1k su 100 Ω (passa-alto a 14,5 Hz,
dec. 194; Nold: 1 µF, 145 Hz) → op-amp di guadagno fino a 0,775 V di plateau → FIRE → VOLUME
(pot log) → buffer. FIRE è un pulsante normalmente aperto a pannello:
taglia il segnale, l'LFO gira sempre (ascoltato e accettato, dec. 190).

### 3.6 Eco a due BBD [PROVVISORIO]

- **BBD**: 2 × CoolAudio V3205D (4096 stadi, DIP-8), in fila: 8192
  stadi, ritardo = 8192 / (2 fclk). Clock 10-100 kHz → 41-410 ms.
  VGG = 14/15 VDD da partitore. Uscite OUT1 e OUT2 sommate con trimmer
  (cancellazione del clock, schema d'applicazione del BL3102).
  Livello all'ingresso: il datasheet dà 0,36 V efficaci a THD 2,5 %;
  il segnale di linea si attenua di **14 dB** prima dei BBD e si
  recupera dopo (v0.2: con −12 dB il giro a RIPETIZIONI tutto arriva a
  0,52 V di picco, proprio al 2,5 %; con −14 dB a 0,42 V, simulato).
- **Clock** (v0.2): **due V3102, uno per BBD**. Il MN3102 (gemello)
  pilota direttamente fino a 4096 stadi (datasheet p. 105): due V3205D
  sono 8192. Il primo V3102 oscilla con R e C fra OX1, OX2, OX3
  (datasheet p. 107, «Example of Oscillation Circuit»); il secondo ha OX1
  dall'OX3 del primo e OX2, OX3 aperti («separate excitation»). Ognuno
  dà CP1, CP2 e VGG = 14/15 VDD al suo BBD. Scartato un V3102 + driver
  TC4427: fronti uguali e lenti si incrociano a metà, il V3205D vuole
  l'incrocio sotto 0,3 VCPH (`RISULTATI-lickshot-v02.md` §3). Da
  verificare al prototipo: la fase del secondo divisore (deduzione mia:
  innocua).
- **TEMPO**: reostato nell'RC del primo V3102, C 100 pF. Fit sulla
  Fig. 1 del MN3102: fcp ≈ 3,22e9 / (R + 7,4k), ritardo ∝ R + 7,4k.
  Pot 250k + 22k fisso + trimmer 10k. La legge sulla corsa dipende dalla
  curva del pot: lineare, logaritmica A, o un VCO esponenziale (più
  parti). Tabella in `RISULTATI-lickshot-v02.md` §4. **Dec. 193: pot
  lineare** (la 192, pot A, è superata): 226 ms a metà corsa, il
  ribattuto stretto nel primo quarto. Modello, banco web e MC-LICKSHOT
  hanno la stessa legge dal 2026-11-18.
- **Filtri**: nessuno (dec. 191). Restano il trimmer di cancellazione
  del clock fra OUT1 e OUT2 e i condensatori di accoppiamento. Con
  TEMPO lungo (clock sotto ~18 kHz) il fischio del clock è udibile: il
  livello lo dirà la misura, il datasheet non lo dà. Il fischio passa
  anche nel giro; il passa-alto del giro non lo ferma (è un passa-alto).
  Da guardare in simulazione: che il fischio, ripetuto dal giro, non
  saturi la saturazione e non tolga spazio all'eco con RIPETIZIONI alto.
- **Giro**: passa-alto RC 150 Hz, saturazione a diodi antiparallelo con
  R in serie (ginocchio ~0,5 V al livello dei BBD, ≈ V_SAT 1,5 V del
  modello al livello di linea), RIPETIZIONI pot lineare, somma invertente
  con l'ingresso.
- **Mix** (v0.3, simulato in `mix-uscita.cir`): somma invertente
  riferita a VDD/2, asciutto e eco da 10k, reazione 10k: eco a guadagno 1
  con LIVELLO ECO tutto, come il modello. Uscita: 100 Ω + 10 µF verso il
  jack, 100k di scarica (passa-alto 0,17 Hz sul MONO da 1 MΩ). Il colpo
  esce a 0 dBu; nel caso peggiore (FIRE tenuto, RIPETIZIONI, LIVELLO ECO
  e VOLUME tutti) il mix arriva a 3,31 V di picco: 2,5 dB sotto il rail
  del TLC2272.

## 4. Piedinature (solo dai datasheet)

| Parte | Piedini | Fonte |
|---|---|---|
| CD4069UB | ingressi 1, 3, 5, 9, 11, 13; uscite 2, 4, 6, 8, 10, 12; VSS 7, VDD 14 | TI CD4069UB, «Pin Configuration and Functions» |
| CD4046B | 1 phase pulses, 2 PC1 out, 3 comparator in, 4 VCO out, 5 inhibit, 6-7 C1, 8 VSS, 9 VCO in, 10 demod out, 11 R1, 12 R2, 13 PC2 out, 14 signal in, 15 zener, 16 VDD | TI SCHS043B (rev. luglio 2003), p. 1 «Terminal assignment» |
| V3205D | 1 GND, 2 CP2, 3 OUT1, 4 OUT2, 5 VDD, 6 CP1, 7 IN, 8 VGG | CoolAudio V3205D/SD datasheet, «Pin Configuration» (copia cricklewoodelectronics.com) |
| V3102 | 1 VDD, 2 CP1, 3 GND, 4 CP2, 5 OX3, 6 OX2, 7 OX1, 8 VGG(out) | datasheet Panasonic MN3102 (gemello), p. 107 «Terminal Assignments» (copia experimentalistsanonymous.com/diy/Datasheets/MN3102.pdf, scansione 1998); coincide col foglio Belling BL3102 |
| TLC2272 | 1 1OUT, 2 1IN−, 3 1IN+, 4 VDD−/GND, 5 2IN+, 6 2IN−, 7 2OUT, 8 VDD+ | TI SLOS190H, «Pin Configuration and Functions» |

Il datasheet CoolAudio del V3102 resta irraggiungibile (cdn.mediavalet.com:
errore 500 anche il 18/11 sera). Il V3102 è venduto come equivalente del
MN3102: prima del simbolo definitivo, controllare la piedinatura sul
foglio CoolAudio o sul pezzo comprato (lezione del LSK389, todo 339).

## 5. Pannello e scheda [PROVVISORIO]

Rack 1U (44,45 mm), largo 19". Sul pannello: 7 pot, LED, FIRE.
Disposizione approvata (dec. 196, «simile a quella Klementz»):
`docs/pannelli/lickshot-1u.svg` e coordinate `lickshot-1u.json`, da
`docs/pannelli/lickshot_1u.py`.
Dietro: jack d'uscita e ingresso DC. Una scheda orizzontale dietro il
pannello coi pot a 90°, oppure pot a filo su una scheda verticale: lo
decide la disposizione di Filippo (regola del pannello). Stima: ~5
op-amp doppi TLC2272, 1 CD4069UB, 1 CD4046B, 2 V3205D, 2 V3102, 2
regolatori (78L09, 78L05), 5 trimmer (polarizzazione e cancellazione del
clock dei due BBD, fondo scala di TEMPO).

## 6. Scarti fra modello e hardware

1. VDD 8,6 V nel modello, 9 V regolati qui (§3.1). A 9 V PROFONDITÀ
   vuole G 1,51 (5,1k / 10k) per le stesse 4 ottave (simulato).
2. Filtri dei BBD: nessuno, nel modello e qui (dec. 191). Il modello
   campiona e tiene al ritmo del clock (aliasing sì), ma non ha il fischio
   del clock.
3. Il modello non ha il fruscio dei BBD (S/N 60 dB A per chip, datasheet).
4. ~~Legge di TEMPO~~: lineare nel modello e nell'hardware (dec. 193).
5. Saturazione del giro: tanh a 1,5 V nel modello, diodi 1N4148 qui. A
   RIPETIZIONI tutto il giro si tiene a 0,90 V di picco contro ~0,8 V del
   modello (simulato): ginocchio un po' più duro.

## 7. Prossimi passi

1. ~~Datasheet del clock~~: MN3102 (v0.2). Manca ancora il foglio
   CoolAudio del V3102 per la conferma.
2. ~~Op-amp~~: TLC2272 (v0.2).
3. ~~Legge di TEMPO~~: pot lineare (dec. 193), modelli riallineati.
4. ~~Simulazione di PROFONDITÀ e del giro~~ (v0.2). ~~Stadio d'uscita,
   mix, alimentazione~~ (v0.3). Resta: IDD del V3205D dal datasheet.
5. ~~Scheda~~: `pcb/lickshot/lickshot.py` a PASSA (2026-11-18): una
   scheda orizzontale 280 x 80 mm coi pot RK09L a 90 gradi alle x della
   dec. 196; FIRE, jack e DC coi fili. Scelte da confermare in
   `pcb/lickshot/NOTE.md` (scheda orizzontale, pot C di ALTEZZA,
   saturazione con un op-amp in meno, valori attorno ai BBD).
6. Simulare gli stadi veri della scheda (op-amp TLC2272, partitore
   12,7k/10k della saturazione, uscite dei BBD).

Verificato in: Python (modello) sì / LTspice sì (PROFONDITÀ, giro, mix) / Live no.
