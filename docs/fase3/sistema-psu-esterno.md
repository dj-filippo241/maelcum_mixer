# Alimentatore esterno e modulo PSU-IN (dec. 113) — v0.1 [PROVVISORIO — regola 3]

Data: 2026-10-14. Todo 51. Base: decisione 113 (alimentatore esterno,
scelta di Filippo), dec. 90(c) (lineare, niente switching), dec. 93
(regolazione finale locale per modulo), dec. 111 (moduli opzionali, 40 °C,
all'aperto), dec. 112 (ventole a termostato). Architettura di partenza:
`sistema-psu.md` REV dec. 113. Simulazioni: `sim/system/psu-box-*.cir`,
risultati in `sim/system/RISULTATI-psu-box.md`.

Questo documento contiene solo ingegneria. Nessuna voce tocca il suono o il
pannello del mixer. Le scelte fisiche (connettore, forma del box, dove sta
sul palco) restano alla sessione hardware (voce 40).

## 0. Cosa cambia rispetto alla REV dec. 113 di `sistema-psu.md`

1. **Pre-regolatore audio a ±22,0 V, non ±22,5.** A 22,5 V e rete −10 %
   l'LDO esce di regolazione nella valle del ripple (simulato, §2.3).
2. **LDO discreto a MOSFET**, non integrato. Un LT1083/1085 chiede
   1,2-1,3 V di dropout a 1,7 A; nella valle restano 1,0 V scarsi.
3. **Bulk del W1 da 15 mF per ramo** (era 10). Allunga la tenuta allo
   spegnimento da 18 a 26 ms a rete −10 % (§2.6).
4. **Linea AC_OK nel cavo.** Il box sente la mancanza di rete e il
   supervisor muta prima che i moduli perdano l'alimentazione.
5. **Conduttore di terra dedicato nel cavo**, non solo lo schermo (§3).
6. **Fusibili a due livelli**: fusibili di gruppo sul PSU-IN e PTC
   (fusibili autoripristinanti) per modulo sul backplane (§4.3).
7. **Calore nel box rifatto**: ~48 W nominali, ~63 W a rete +10 % (erano
   stimati ~30 / ~45). Nel mixer: ~83 W base, ~97 W coi moduli opzionali.

## 1. Schema a blocchi

```
BOX ESTERNO                                         CAVO ≤ 2 m       MIXER — modulo PSU-IN
rete IEC + filtro + interruttore + T2 A + NTC/relè                    connettore
toroidale ~250 VA, schermo elettrostatico                              │
 W1 2×21 V 3,5 A → T4 A → ponte → 15 mF ×2 → LDO MOSFET ±22,0 V ═══════ TVS → F gruppo → 2,2 mF → backplane «audio»
 W2 2×18 V 1,0 A → T1,25 A → ponte → 10 mF ×2 → LDO MOSFET ±19,0 V ══ TVS → F gruppo → 1 mF   → backplane «LN»
 W3 2×20 V 0,4 A → T630 mA → ponte → 4,7 mF ×2 → [M] raw ±27 ════════ TVS → F gruppo → 1 mF   → backplane [M]
 W4 9 V 2,5 A → T3,15 A → ponte → 10 mF → regolatore +5 V ═══════════ TVS → F gruppo → 1 mF   → backplane +5
                                     └→ V_FAN (raw W4) ═══════════════ F → driver ventole (termostato)
 rivelatore AC_OK (dal W1) ═══════════════════════════════════════════ → supervisor (mute)
 terra di rete → telaio del box ═══ conduttore PE + schermo ══════════ → telaio del mixer
                                                                       stella analogue-0V: tutti gli 0 V qui
```

## 2. Box esterno

### 2.1 Trasformatore e raddrizzatori

Toroidale ~250 VA, avvolgimenti invariati (dec. 111/112): W1 2×21 V 3,5 A,
W2 2×18 V 1,0 A, W3 2×20 V 0,4 A, W4 9 V 2,5 A. Schermo elettrostatico tra
primario e secondari, termofusibile integrato. Ponti da 8-10 A per W1, da
3 A per gli altri, sulla stessa aletta degli LDO.

Bulk: **W1 15 mF per ramo** (35 V, 105 °C), W2 10 mF, W3 4,7 mF, W4 10 mF.

### 2.2 LDO discreto (W1 e W2, stessa topologia)

Ramo positivo (il negativo è lo specchio, con N-MOSFET):

```
raw+ ──Rsense──┬── S ┐
               │     P-MOSFET ── uscita ±22,0 ── partitore ── amp. d'errore (−)
  PNP limite ──┘     G ── Rgs 10 k a S, zener 12 V G-S
                     └── NPN (emettitore su 4,7 k) ← amp. d'errore
riferimento 2,5 V (shunt) → RC di soft-start (τ ~0,1 s) → amp. d'errore (+)
```

- **Passo**: P-MOSFET di potenza (classe IRF9540 / SUP, Rds ≤ 0,1 Ω),
  TO-220 o TO-247 sull'aletta. Il ramo negativo usa l'N-MOSFET
  complementare.
- **Amplificatore d'errore**: op-amp alimentato dal raw (fino a 32 V a rete
  +10 % e carico leggero): classe 36-40 V di alimentazione massima.
  Pilota il gate attraverso un NPN con resistenza d'emettitore: così
  l'op-amp lavora vicino a massa e la compensazione è un integratore
  (10 nF + 10 k) sul suo ingresso invertente.
- **Limite di corrente**: PNP con base-emettitore su Rsense; quando conduce
  riporta il gate verso il source. W1: 0,22 Ω → ~2,7 A a freddo,
  ~2,3 A a caldo. W2: 0,56 Ω → ~1,1 A.
- **Soft-start**: il riferimento sale con τ ~0,1 s. All'accensione le
  uscite crescono in ~0,3 s e la corrente di carica dei condensatori del
  mixer resta sotto il limite.
- **Valori**: W1 partitore 38,3 k / 4,99 k (21,9-22,0 V); W2 32,4 k /
  4,99 k (18,9 V). Taratura fine a banco.

### 2.3 Risultati (dettagli in `RISULTATI-psu-box.md`)

| | W1 ±22,0 V | W2 ±19 V |
|---|---|---|
| Al mixer, rete −10 … +10 % | 21,83-21,94 V | 18,84-18,92 V |
| Ripple al mixer | ≤ 3 mV pp | ≤ 1 mV pp |
| Margine minimo del MOSFET (rete −10 %, carico pieno) | 1,26 V | 1,32 V |
| Gradino di carico 1,0 → 1,7 A | −87 mV, nessuna oscillazione | — |
| Calore per MOSFET, nominale / peggiore (+10 %) | 8,3 / 13,4 W | 2,0 / 3,2 W |
| Avvolgimento nel caso peggiore | 97 % | 92 % |

A valle i regolatori locali hanno margine: LM317 → 19,2 V chiede ~20,9 V,
ne arrivano 21,8-21,9 (margine ~0,9 V). Il pre-regolatore LN locale ±16,5
chiede ~18,2 V, ne arrivano 18,8-18,9 (margine ~0,6 V). Ora i locali
lavorano su una caduta fissa, a qualunque tensione di rete.

### 2.4 +5 V e V_FAN

- **+5 V**: regolatore classe LM1084/LM2940 dal raw W4 (8,5-12,7 V), 1,25 A
  di dimensionamento, sull'aletta. Il cavo porta il +5 su due conduttori
  per polo: caduta ~0,1 V a 1,3 A, al mixer ~4,9 V. Va bene per LED,
  logiche e relè.
- **V_FAN**: raw W4 non regolato, su un conduttore dedicato con il suo
  ritorno dedicato. Il termostato sta nel mixer (§4.5).

### 2.5 Rivelatore AC_OK

Doppia semionda dal W1 (due diodi dalle estremità dell'avvolgimento),
partitore 47 k / 4,7 k, condensatore 10 µF: τ = 42,7 ms. Un comparatore
con isteresi confronta il picco con una soglia fissa al **75 % del picco
nominale**. Uscita open-collector verso il mixer, attiva alta = rete
presente, con pull-up al +5 nel PSU-IN. Cavo staccato = linea bassa =
mute.

### 2.6 Spegnimento: chi arriva prima

Simulato con distacco sul picco e carico costante (`psu-box-off*.cir`):

| Rete | AC_OK + relè | I regolatori locali escono (15 mF, 1,7 A) |
|---|---|---|
| −10 % | ≤ 12,7 ms | 25,9 ms |
| nominale | ≤ 17,3 ms | > 36 ms |
| +10 % | ≤ 21,4 ms | 79,7 ms |

Con 10 mF il caso a rete −10 % dava 18,3 ms: troppo vicino. Da qui il bulk
da 15 mF. AC_OK scatta anche se la rete scende sotto ~−21 % (brown-out):
il mixer muta invece di distorcere.

### 2.7 Protezioni del box

- Primario: interruttore bipolare, fusibile T2 A, NTC 10-20 Ω con relè di
  bypass dopo ~0,5 s (inrush del toroidale), filtro di rete a due stadi
  nella presa IEC.
- Secondari: fusibili lenti prima dei ponti (W1 T4 A per ramo, W2
  T1,25 A, W3 T630 mA, W4 T3,15 A).
- Uscite: limite di corrente degli LDO (cortocircuito nel cavo o nel
  backplane). [M] e +5 non hanno limite attivo: li proteggono i fusibili
  di gruppo nel PSU-IN.

### 2.8 Termica e meccanica del box

| Sorgente | Nominale | Rete +10 % |
|---|---|---|
| MOSFET W1 (2) | 16,6 W | 26,8 W |
| MOSFET W2 (2) | 4,0 W | 6,4 W |
| Regolatore +5 (worst LED) | 5,7 W | 7,7 W |
| Ponti | ~6,5 W | ~6,5 W |
| Rsense | ~1,5 W | ~1,5 W |
| Trasformatore (perdite proprie) | ~13 W | ~14 W |
| **Totale box** | **~48 W** | **~63 W** |

Sull'aletta: ~33 W nominali, ~48 W nel caso peggiore. Obiettivo: aletta
≤ 70 °C a 40 °C ambiente, perché la tocca chi la sposta. Serve
**Rθ ≤ 0,6 K/W**, cioè una parete alettata del box in estruso
(ordine di grandezza 300 × 150 mm con alette da 40-50 mm), senza ventola.
Giunzione del MOSFET più caldo: ~70 + 13,4 × 1,3 ≈ 88 °C (limite 150).

Ambiente all'aperto (dec. 111 e): box chiuso contro pioggia e polvere,
alette all'esterno, trasformatore e schede dentro. Le perdite interne
(~20 W) alzano l'aria interna di ~10 K. Elettrolitici da 105 °C. Il box
può stare a terra sotto il banco: va appoggiato su piedini e non coperto.

## 3. Cavo e connettore

Lunghezza ≤ 2 m. Conduttori da 0,5 mm² (0,036 Ω/m), schermo complessivo.

| Funzione | Conduttori | Corrente max | Caduta |
|---|---|---|---|
| +22,0 / −22,0 audio | 2 + 2 | 1,7 A | ~60 mV |
| 0 V audio (W1) | 2 | differenza dei rami | — |
| +19 / −19 LN | 1 + 1 | 0,48 A | ~35 mV |
| 0 V LN (W2) | 1 | — | — |
| +27 / −27 [M] raw | 1 + 1 | 0,17 A | ~12 mV |
| 0 V [M] (W3) | 1 | — | — |
| +5 V | 2 | 1,3 A | ~50 mV |
| 0 V +5 (W4) | 2 | 1,3 A | ~50 mV |
| V_FAN + ritorno ventole | 1 + 1 | 0,3 A | — |
| AC_OK | 1 | µA | — |
| PE (terra di protezione) | 1 (contatto che chiude per primo) | — | — |
| **Totale** | **20** | | |

- Ogni 0 V dei secondari viaggia separato fino alla stella nel PSU-IN
  (`sistema-grounding.md` REV dec. 113). Nel box gli 0 V non toccano la
  terra.
- **Terra**: un conduttore PE dedicato (giallo-verde, sezione ≥ 0,75 mm²)
  collega il telaio del box al telaio del mixer. Lo schermo del cavo si
  chiude sui gusci metallici dei due connettori. Così la continuità di
  terra non dipende dalla calza.
- **Connettore**: circolare metallico a vite, IP65, con codifica, **≥ 20
  contatti da ≥ 5 A più 2-4 di scorta** (classe 24 poli). Il PE deve
  chiudere prima degli altri. Marca e modello: sessione hardware (voce 40).

## 4. Modulo PSU-IN (dentro il mixer)

Sta nello slot PSU del backplane (`sistema-backplane.md` REV dec. 113).

### 4.1 Ingresso

Per ogni rail, nell'ordine:
1. **TVS** verso il suo 0 V: ±22 → 26 V di standoff (rottura ~29 V); ±19 →
   22 V; [M] → 33 V; +5 → 5,0 V. Assorbono i disturbi del cavo. Se un LDO
   del box va in corto, il TVS conduce e il fusibile di gruppo si apre:
   i moduli non vedono il raw.
2. **Diodo Schottky inverso** verso lo 0 V (protegge da un rail mancante o
   invertito).
3. **Fusibile di gruppo** (5×20 in portafusibile accessibile).
4. **Bulk locale**: 2,2 mF sui ±22, 1 mF su ±19, [M] e +5. Assorbe i picchi
   di corrente dei moduli, così il cavo vede una corrente calma.

### 4.2 Stella

Tutti gli 0 V del cavo (audio, LN, [M], +5, ritorno ventole) arrivano su
conduttori separati e si uniscono in un solo punto del PSU-IN. Da qui
partono i ritorni del backplane. Il bond telaio↔AGND unico resta qui
(`sistema-grounding.md` §2). Il ritorno delle ventole entra nella stella
con un filo suo, mai su AGND né su CTRL_GND.

### 4.3 Fusibili a due livelli

| Livello | Dove | Valori [PROVVISORIO] |
|---|---|---|
| Gruppo | PSU-IN, 5×20 accessibili | ±22: T2,5 A per ramo · ±19: T1 A · [M]: T500 mA · +5: T2 A · V_FAN: T500 mA |
| Modulo | backplane, PTC per slot e per rail | canale 0,3 A · 5-way 0,6 A · FX 0,4 A · filtro 0,3 A · FX-SEND, CUE, mic, mono 0,1-0,2 A · opzionali 0,1-0,3 A |

Motivo del cambio rispetto a `sistema-psu.md` §4 (un fusibile 5×20 per
modulo e per rail): coi moduli opzionali i fusibili diventerebbero ~40. Le
PTC si ripristinano da sole a guasto rimosso e non chiedono accesso. Il
regolatore locale di ogni modulo resta il primo limite (1,5-2,2 A con
protezione termica).

### 4.4 Supervisor: soglie e tempi

Il supervisor (master-out §3.7) vive sul +5 del box e ora sente i rail
pre-regolati. Le soglie seguono i nuovi valori:

| Ingresso | Sotto (mute) | Sopra (mute + LED guasto) | Filtro |
|---|---|---|---|
| ±22,0 audio | < 21,2 V | > 23,5 V | 1 ms |
| ±19 LN | < 18,3 V | > 20,5 V | 1 ms |
| [M] raw | < 22,0 V | — (raw, 30,3 V normali a +10 %) | 5 ms (ripple) |
| +5 | < 4,6 V | > 5,5 V | 1 ms |
| AC_OK | linea bassa | — | nessuno |

- **Mute subito, riarmo lento**: qualunque condizione fuori finestra
  rilascia i relè. Il riarmo avviene 1,5-2 s dopo che tutto è tornato in
  finestra.
- Il filtro «> 100 ms» del §4 di `sistema-psu.md` serviva a non mutare sui
  picchi di programma con i raw non regolati. Ora i rail arrivano
  regolati dal box e i picchi non li fanno scendere: basta 1 ms.
- Cavo staccato o box spento: AC_OK basso e +5 assente, quindi relè
  rilasciati (failsafe). Nessun pop.

### 4.5 Termostato delle ventole (dec. 112)

- Sensore: NTC sulla barra dei regolatori ±18 dei moduli caldi.
- Driver lineare dal V_FAN (raw W4, 8,5-12,7 V): op-amp + transistor di
  potenza sulla barra. Niente PWM.
- Legge: spente sotto 35 °C; a 35 °C partono a ~6 V (tensione di avvio
  sicura di una ventola da 12 V), isteresi 2 K; poi salgono in modo
  lineare fino al massimo a 50 °C. Il massimo è ~1 V sotto la valle del
  raw (7,5 V a rete −10 %, ~9,5 V nominali). Così il driver toglie anche
  il ripple a 100 Hz: niente ronzio meccanico dalle ventole.
- Dissipazione del driver: ≤ 2 W (6 V di uscita a rete +10 %).
- Uscita tachimetrica delle ventole verso il supervisor: ventola ferma
  oltre 45 °C → LED guasto, nessun mute.

## 5. Bilancio termico dentro il mixer (sostituisce la stima della dec. 113)

| Sorgente | Base (1,4 A) | Con moduli opzionali (1,7 A) |
|---|---|---|
| Regolatori ±18 (21,9 → 19,2 V) | 7,6 W | 9,2 W |
| Moltiplicatori di capacità ±18 | 3,4 W | 4,1 W |
| Op-amp / VCA sui ±18 | 50,4 W | 61,2 W |
| LN ±15: pre-reg locali (18,9 → 16,5 V) + LT3045/94 + carichi | 9,9 W | 10,3 W |
| +5 V: LED e logiche (il regolatore è nel box) | 2,8 W | 2,8 W |
| Master [M]: stadio HV + LDO locali | 7,0 W | 7,0 W |
| Ventole e driver | ~2 W | ~2 W |
| **Totale** | **~83 W** | **~97 W** |

Il totale non dipende più dalla rete, tranne il master [M] (raw non
regolato, ±1 W). Con le ventole (dec. 112) l'aria interna sale di ~3 K
sopra l'ambiente.

## 6. Aperti

- Connettore, marca del box e posizione sul palco: sessione hardware
  (voce 40).
- A banco: stabilità degli LDO coi MOSFET reali (la capacità di gate vera
  sposta il polo), corrente di limite a caldo, tempi di AC_OK e dei relè,
  soglie del supervisor, temperatura dell'aletta con termocamera.
- I modelli usati sono di classe (VDMOS generico, op-amp comportamentale):
  i margini di dropout (≥ 1,26 V) assorbono la differenza col componente
  vero.
