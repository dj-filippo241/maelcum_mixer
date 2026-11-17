# Filtro: schede di segnale (todo 337, 2026-11-16)

Generatore: `pcb/filtro/filtro.py HPF|LPF`. Due schede, una per sezione: HPF = parte 1 (fila 1
della colonna FILTRO, 149 × 166 mm), LPF = parte 2 (fila 2, 151 × 164 mm), misure da
`pcb/PIANO-SCHEDE-F.md`. Ogni scheda porta tutto della sua sezione: core stereo, CV di frequenza,
RES, overdrive, muto, uscita. Le due schede sono uguali a meno di shaper di frequenza (dec. 102 /
137), uscita del core (HP o LP) e pin del C96.

## Divisione in due schede [C]

Il piano diceva solo «parte 1, parte 2». Una scheda per sezione è la divisione con meno fili fra
le schede: nessuna corrente Iabc e nessuna CV passa da una scheda all'altra, e le due schede
condividono solo l'alimentazione e i bit FILT_MODE (riga c, uguale per tutti gli slot).

## Pin del C96 (sistema-backplane §4, classe FILTRO)

| Scheda | Ingresso | Uscita (verso il DJ bus, R 10k sulla scheda) | Bit di modo |
|---|---|---|---|
| HPF | b1 / b2 BUS_HPF_L / R | b7 / b8 HPF_OUT_L / R | c1, c3, c5, c7 (FILT_MODEn_0) |
| LPF | b4 / b5 BUS_LPF_L / R | b10 / b11 LPF_OUT_L / R | c2, c4, c6, c8 (FILT_MODEn_1) |

Bit 0 = HPF, bit 1 = LPF: dalla logica della levetta del canale (`pcb/canale/canale.py`, Q0 e Q1).

## Scelte segnate NOTA

1. **Converter esponenziale a componenti** (`sim/filtro/RISULTATI-conv-that320.md`). Il §4 del
   design doc aveva il converter solo ideale e un mirror bufferizzato NPN, che non può alimentare
   il pin Iabc (il pin assorbe corrente). Ora: THAT 320 (4 PNP appaiati) con Q1 di riferimento e
   Q2, Q3 che spingono la corrente nei due OTA di una sezione 2 poli; LM334SM PTAT per Iref.
   Quattro converter per scheda (due per core), un trimmer di fondo scala ciascuno. Il §4 diceva
   «2 converter per sezione»: sono 4 perché il THAT 320 ha 3 uscite e un core ha 4 OTA.
2. **Q 0,541 della sezione 1 con una resistenza** (5,41k dal buffer BP al summer), non con un OTA
   a corrente fissa come nel sim: stesso smorzamento, un LM13700 in meno per core, niente deriva
   termica della gm.
3. **Partitore 2,87k / 100** (E96): k 1/29,7 invece di 1/30. Sposta la mappa di frequenza dell'1 %,
   lo stesso su tutti gli OTA: lo assorbe il trimmer di fondo scala.
4. **Sorgenti della RES**: op-amp + MMBT3906, emettitore su 41,7k verso massa. Il comando deve
   essere negativo: gpos esce già negativo dallo shaper; gneg passa da un invertitore in più.
   41,7k = 22,6k × 1,848: la RES lavora sulla sezione Q 1,307 del core a 4 poli (d5b-4p-chain.cir).
5. **Muto secco** con ADG1434 dall'OR a diodi dei quattro bit. Col filtro senza canali il segnale
   d'ingresso è zero, ma un fischio della RES tagliato di colpo può fare click. Da sentire a banco;
   rimedio pronto: il taglio allo zero del kill del 5-way (dec. 164).
6. **Alimentazioni**: core, converter, RES e CV sul ±15 LN (LT3045 / LT3094, ~100 mA); ricevitore,
   overdrive e driver sul ±18; ADG sul ±15 switch. Da contare a banco: il cap-moltiplicatore del
   ±18 (`celle_micmono.power_18_sw`, 1k sulla base del BD139) porta anche il ±15 LN, ~150 mA in
   tutto; con β 50 la caduta sulla base arriva a ~3 V.
7. **Resistenza tempco** 1k +3300 ppm/K (1206): parte da scegliere con la reperibilità (todo 13).
   Sulla scheda va in mezzo ai quattro THAT 320, incollata.
8. **Retro**: i due core e la RES stanno sul retro (solo SMD). Davanti non c'era posto: giro 1
   «servono 105 mm», giro 2 col solo core R sul retro 57 mm, giro 3 coi due core 8 mm.

## Cavo della scheda comandi (J2, 2 × 6)

`fili_cavo()` in `filtro.py`: FREQ (pot fra +REF5 e AGND, cursore FW), RES (pot cablato rovescio,
cursore RW), DRIVE (pot doppio lineare: capo PTL / PTR, cursore DWL / DWR, altro capo AGND). La
scheda comandi del filtro non esiste ancora (todo 270): leggerà l'ordine da qui.

## Taratura a banco (per scheda)

- ZERO e SCALA della frequenza (trimmer 1k e 5k), poi il fondo scala di ogni converter (100 Ω).
- RES: trimmer su Rref, «il fischio parte al 93 %».

9. **Riempimento 90-92 %** in `pcb/PIANO-SCHEDE-F.md` contro il tetto del 70 % (dec. 156): il
   conto del piano vale per un lato solo, queste schede usano i due lati (core e RES sul retro).
   Lunghezze fisse 149 e 151 mm nel piano.

## Esiti

- 2026-11-16, HPF giro 1 (4 tentativi): NON PASSA, 3 aperti (un'isola di AGND, pad 7 di U23,
  tratto BRNR). Aggiunti `d.route_tries` e `d.fanout_more` (come 5-way LB).
- 2026-11-16, 6 tentativi: HPF migliore 1 aperto, LPF migliore 2; gli aperti cambiano a ogni
  tentativo (-15LN, pin del LM13700 della RES sul retro): casuali, non di progetto.
- 2026-11-17, 10 tentativi: **HPF PASSA** al tentativo 9, **LPF PASSA** al primo. ERC pulito
  (1 avviso ground_pin_not_ground: VSS dell'ADG1434 U26 è il -15 V switch, giusto). La HPF è al limite: un giro nuovo può chiedere tutti i 10
  tentativi (~6 min l'uno).
- Conteggio: HPF 291 impronte, LPF 294.
