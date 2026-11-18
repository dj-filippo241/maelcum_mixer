# FASE 4 — Lickshot in rack 1U: architettura v0.1 (2026-11-18)

> **Stato: v0.1 — requisiti e catena chiusi, topologia per blocchi
> scelta, componenti [PROVVISORIO — regola 3], nessuna simulazione
> LTspice ancora.** Metodo (regola 4): requisito → funzione di
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
| Comandi | ALTEZZA, VELOCITÀ, PROFONDITÀ, VOLUME, TEMPO, RIPETIZIONI, LIVELLO ECO; LED dell'LFO; FIRE | dec. 184, 185, 190 [F] |
| Giro dell'eco | passa-alto e saturazione fissi, senza comandi | dec. 186 [F] |
| Uscita | jack mono sbilanciato, 0 dBu nominale, verso un modulo MONO | dec. 187 [F] |
| Formato | rack 1U | dec. 188 [F] |
| Alimentazione | alimentatore esterno a spina, DC, connettore con blocco | dec. 189 [F] |

## 2. Catena

```
FIRE ─┐
LFO CD4069 ─► PROFONDITÀ ─► VCO CD4046 ─► passa-alto 145 Hz ─► FIRE ─► VOLUME ─┬─────────────► MIX ─► USCITA 0 dBu
(VELOCITÀ)    (pot + buffer)  (ALTEZZA)                                          │                ▲ (LIVELLO ECO)
   └─► LED                                                                       ▼                │
                                    SOMMA ─► anti-alias ─► BBD 1 ─► BBD 2 ─► anti-alias + make-up ─┤
                                      ▲                    clock V3102 (TEMPO)                     │
                                      └── RIPETIZIONI ◄── saturazione ◄── passa-alto 150 Hz ◄──────┘
```

Numeri della catena dal modello (`lickshot.py`, `prova_lickshot.py`):
colpo da 0 a ~4 ottave secondo PROFONDITÀ (2 ottave a ~2/3), da 2 a
48 colpi al secondo, eco 41-410 ms, giro con guadagno fino a 1,1 (oltre
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
- **+7,5 V** (regolatore regolabile) per i due V3205D e il clock:
  il V3205D lavora fra 4 e 8 V (datasheet, «Operating Condition»), il
  valore assoluto massimo è 11 V.
- Riferimenti a metà alimentazione (partitore + buffer) per gli op-amp
  e per la polarizzazione degli ingressi dei BBD.
- Op-amp: da scegliere con datasheet alla mano (ingresso e uscita
  vicino ai rail a 9-12 V singoli). Candidati da verificare, non scelti.

### 3.2 LFO (Nold, sigle di Orald-0)

CD4069UB: U1A + U1B trigger di Schmitt (R1 22k in reazione, R4 10k
dall'integratore), U1C integratore di Miller con C1 1 µF film; corrente
da R6 22k + VELOCITÀ 500k. Diodo D3 1N4148 fisso in parallelo alla
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
+ ALTEZZA 50k (reostato) al pin 11, R2 (pin 12) aperta: fmin = 0.
Inhibit (pin 5) a massa. Ingressi dei comparatori a massa. f0 ≈ 0,7 /
(R1 C1) dalla Fig. 4 del datasheet; ±30 % fra un chip e l'altro: ALTEZZA
copre la differenza.

### 3.5 Uscita del colpo e FIRE

Onda quadra dal pin 4 → 1 µF → 1k su 100 Ω (passa-alto a 145 Hz, come
Nold) → op-amp di guadagno fino a 0,775 V di plateau → FIRE → VOLUME
(pot log) → buffer. FIRE è un pulsante normalmente aperto a pannello:
taglia il segnale, l'LFO gira sempre (ascoltato e accettato, dec. 190).

### 3.6 Eco a due BBD [PROVVISORIO]

- **BBD**: 2 × CoolAudio V3205D (4096 stadi, DIP-8), in fila: 8192
  stadi, ritardo = 8192 / (2 fclk). Clock 10-100 kHz → 41-410 ms.
  VGG = 14/15 VDD da partitore. Uscite OUT1 e OUT2 sommate con trimmer
  (cancellazione del clock, schema d'applicazione del BL3102).
  Livello all'ingresso: il datasheet dà 0,36 V efficaci a THD 2,5 %;
  il segnale di linea si attenua di ~12 dB prima dei BBD e si
  recupera dopo.
- **Clock**: V3102 (gemello del MN3102), 2 fasi, VGG interno. Comando
  del TEMPO: da decidere fra RC interno col pot (legge 1/R) e un
  secondo CD4046B come VCO esterno (legge esponenziale come nel modello,
  più l'effetto «fionda» lisciando la tensione). [APERTO]
- **Anti-alias**: nel modello il taglio segue il clock (fclk/4, max
  8 kHz). Un filtro che insegue il clock vuole un filtro a capacità
  commutate o una cella controllata in tensione; la via comune è un
  filtro fisso a ~3-4 kHz a 2-3 poli prima e dopo. [APERTO: se fisso,
  il modello va riallineato e ascoltato di nuovo, perché coi tempi corti
  le ripetizioni diventano più scure di oggi]
- **Giro**: passa-alto RC 150 Hz, saturazione a diodi antiparallelo con
  R in serie (ginocchio ~0,5 V al livello dei BBD, ≈ V_SAT 1,5 V del
  modello al livello di linea), RIPETIZIONI pot lineare, somma invertente
  con l'ingresso.
- **Mix**: asciutto + LIVELLO ECO (pot log) × uscita dei BBD, op-amp
  d'uscita, 100 Ω e condensatore verso il jack.

## 4. Piedinature (solo dai datasheet)

| Parte | Piedini | Fonte |
|---|---|---|
| CD4069UB | ingressi 1, 3, 5, 9, 11, 13; uscite 2, 4, 6, 8, 10, 12; VSS 7, VDD 14 | TI CD4069UB, «Pin Configuration and Functions» |
| CD4046B | 1 phase pulses, 2 PC1 out, 3 comparator in, 4 VCO out, 5 inhibit, 6-7 C1, 8 VSS, 9 VCO in, 10 demod out, 11 R1, 12 R2, 13 PC2 out, 14 signal in, 15 zener, 16 VDD | TI SCHS043B (rev. luglio 2003), p. 1 «Terminal assignment» |
| V3205D | 1 GND, 2 CP2, 3 OUT1, 4 OUT2, 5 VDD, 6 CP1, 7 IN, 8 VGG | CoolAudio V3205D/SD datasheet, «Pin Configuration» (copia cricklewoodelectronics.com) |
| V3102 | **da verificare**: il datasheet CoolAudio non si scarica (errore 500). Il gemello Belling BL3102 dà 1 VDD, 2 CP1, 3 GND, 4 CP2, 5-7 OX3-OX1, 8 VGG | foglio Belling BL3102 (1 pagina, senza formula dell'oscillatore) |

Il pinout del V3102 non entra in un simbolo finché non c'è il suo
datasheet (lezione del LSK389, todo 339).

## 5. Pannello e scheda [PROVVISORIO]

Rack 1U (44,45 mm), largo 19". Sul pannello: 7 pot, LED, FIRE.
Dietro: jack d'uscita e ingresso DC. Una scheda orizzontale dietro il
pannello coi pot a 90°, oppure pot a filo su una scheda verticale: lo
decide la disposizione di Filippo (regola del pannello). Stima: ~5
op-amp doppi, 1 CD4069UB, 1-2 CD4046B, 2 V3205D, 1 V3102, 2
regolatori, 4 trimmer (polarizzazione e cancellazione del clock dei due
BBD).

## 6. Scarti fra modello e hardware

1. VDD 8,6 V nel modello, 9 V regolati qui (§3.1).
2. Anti-alias che segue il clock nel modello, probabilmente fisso qui
   (§3.6).
3. Il modello non ha il fruscio dei BBD (S/N 60 dB A per chip, datasheet).
4. Legge di TEMPO: esponenziale nel modello, da fissare col circuito del
   clock (§3.6).

## 7. Prossimi passi

1. Datasheet del V3102 (o scelta del BL3102 col suo datasheet).
2. Op-amp scelti dal datasheet.
3. Decisioni aperte di ingegneria: clock del TEMPO e anti-alias fisso o
   inseguito. Se cambiano il suono, riallineare `lickshot.py`, il banco web
   e MC-LICKSHOT e farli riascoltare a Filippo.
4. Simulazione LTspice dei blocchi analogici (PROFONDITÀ, uscita, giro
   dell'eco col BBD come ritardo ideale, saturazione) in `sim/lickshot/`.
5. Scheda `pcb/lickshot/lickshot.py` col generatore, dopo la
   disposizione del pannello.

Verificato in: Python (modello) sì / LTspice no / Live no.
