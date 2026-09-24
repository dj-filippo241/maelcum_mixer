# EQ SERIE v0.3-alpha — celle Baxandall a law asimmetrica (2026-09-24)

> **Stato: ALPHA.** Cella LOW derivata e dimostrata in LTspice (`sim/eq-serie/`).
> Celle MID/HIGH, cascata completa, rumore e livelli = v0.3-beta. Origine:
> decisione 76 (EQ in serie, famiglia Baxandall) dopo il finding critico delle
> celle a contribuzione (`sim/cdj-eq/RISULTATI-eq.md`). Sostituisce CDJ v0.2 §3.3.

## 1. Il vincolo che decide tutto: boost e cut simmetrici non bastano

Cella invertente classica con pot complementare nei due bracci:

    G(s) = −Zf/Zin;  Zin = R + Za(x);  Zf = R + Zb(x)
    Za = (x·Rp) || (1/sC);  Zb = ((1−x)·Rp) || (1/sC)

Proprietà (dimostrate in simulazione):
- **x = 0,5 → G = −1 esatto a ogni frequenza** (Za = Zb per costruzione:
  il detent "piatto assoluto" della v0.2 sopravvive, ±0,02 dB misurati);
- boost e cut elettricamente **simmetrici**: ±20·log(1+Rp/R).

Il requisito è asimmetrico (−∞ → 0 → +6, SPECIFICA §4): con Rp/R = 1 il kill
sarebbe −6 dB. La soluzione NON è nella rete (la simmetria è dimostrabile per
ogni cella complementare a singolo pot) ma nella **legge del pot**: rete
elettrica simmetrica ±X dB, taper meccanico custom che mappa:

    θ ∈ [0,5 → 0]  (cut):   x → 0,5 … ~1,0  (tutta la profondità, −X dB al fondo)
    θ ∈ [0,5 → 1]  (boost): x → 0,5 … x₆    (solo il tratto che serve per +6 dB)

Coerente con la filosofia già bloccata per il filtro (dec. 70: law musicale
al centro, accelerazione agli estremi) e con la sessione hardware pot (voce 40).
In elettronica: la stessa asimmetria si ottiene col pot lineare + le due metà
corsa usate in tratti diversi; il taper custom serve per il feel musicale.

## 2. Cella LOW — proof-of-concept misurato (2026-09-24)

Valori [PROVVISORIO — regola 3]: R = 1 kΩ, Rp = 31 kΩ, C = 100 nF,
op-amp macro ideale. Griglia misurata (`sim/eq-serie/low-cell.cir`):

| x (elettrica) | gesto | 20 Hz | 70 Hz | 150 Hz | 1 kHz | 10 kHz | min banda |
|---|---|---|---|---|---|---|---|
| 0,323 | boost +6 | +5,76 | +4,08 | +1,84 | −0,25 | −0,03 | −0,25 |
| 0,400 | boost medio | +3,16 | +2,19 | +0,93 | −0,14 | −0,02 | −0,14 |
| 0,500 | **DETENT** | −0,02 | −0,02 | −0,02 | −0,02 | −0,02 | −0,02 |
| 0,600 | cut lieve | −3,19 | −2,22 | −0,96 | +0,11 | −0,01 | −3,32 |
| 0,750 | cut medio | −8,55 | −6,24 | −3,09 | +0,34 | +0,00 | −8,87 |
| 0,900 | cut forte | −16,48 | −13,07 | −8,36 | +0,63 | +0,04 | −16,97 |
| 0,970 | cut profondo | −23,57 | −19,77 | −14,65 | −0,87 | +0,19 | −24,14 |
| 0,999 | KILL | −29,23 | −25,29 | −20,09 | −5,42 | +0,12 | −29,84 |

Lettura musicale (cosa si sente):
- **Kill vero**: a fine corsa il basso a 20 Hz è giù di ~30 dB — la cassa
  sparisce, non "si affloscia" come nella v0.2 (−8 dB con gobba). Nessun bump
  a nessuna posizione: il minimo in banda resta sulle basse a ogni x
  (colonna gmin ≈ g20 sempre) → la sottrazione qui è tra impedenze reali
  (partitore), non tra segnali sfasati: il difetto fatale della v0.2 è assente
  per costruzione.
- **Le medie restano vive**: con il kill inserito, 1 kHz sta a −5 dB e 10 kHz
  a 0 — il gesto dub classico (via il basso, hi-hat e voce restano) funziona.
- **Boost shelf liscio**: +5,8 dB a 20 Hz che sfuma con pendenza di shelf,
  niente buchi a 150 Hz (la v0.2 scavava −1,7 dB).
- **Detent assoluto**: −0,02 dB piatti su tutta la banda: la traccia passa
  come registrata (valore centrale della v0.2 preservato).
- Effetto cosmetico noto: cut profondi portano +0,3…+0,6 dB intorno a 1 kHz
  (interazione di fase degli zeri/poli della cella) — sotto la soglia di
  udibilità dentro il gesto del kill; la cascata a 4 bande lo riduce ancora
  (verifica in v0.3-beta).

## 3. Tracking stereo — numeri per la questione 53

`low-cell-track.cir`, mismatch tra sezioni del pot doppio (err = ±0,5/1% per lato):

| mismatch sezioni | deviazione dal nominale | L−R worst (stima ×2) | requisito ≤0,25 dB |
|---|---|---|---|
| 1 % | ≤0,08 dB (detent/boost LF) | ~0,16 dB | PASSA |
| 2 % | ≤0,17 dB (detent LF) | ~0,34 dB | al limite |

Conclusioni: pot doppi con tracking ≤1% (conduttivo-plastica di precisione,
selezione) bastano; a 2% serve trim. La zona sensibile è il detent sulle basse
(dove Za/Zb sono massime). Alternativa elettronica (VCA per banda + CV unica:
tracking perfetto by design) resta la via di fuga se la meccanica delude —
decisione dentro la voce 53, costo +4 VCA/canale.

## 4. Estensione alle altre bande (v0.3-beta, principio fissato)

- **HIGH**: duale della LOW (scambio R↔C nelle reti Za/Zb): shelf alta,
  kill −X sulle alte, identica struttura.
- **MID (250, 1k)**: celle a campana — reti Za/Zb con rami serie C-R-C
  (o twin-T) che portano Zb a un minimo reale alla frequenza centrale:
  il cut ha uno ZERO sull'asse jω → −X dB profondo e stretto al centro,
  gonne controllate; il boost è la campana duale (+6). Stessa law asimmetrica.
  Derivazione esatta e simulazione = v0.3-beta (la famiglia Baxandall "mid"
  classica copre esattamente questo caso).
- **Cascata**: 4 celle in serie, 1 sezione op-amp ciascuna = 1 quad per canale
  (vs 10 sezioni della v0.2). Quattro stadi invertenti → polarità assoluta
  preservata. Interazione tra bande adiacenti: è il carattere classico degli
  EQ in serie (le curve si sommano in dB con mutua influenza sulle gonne) —
  va mostrato a Filippo sulle curve complete (v0.3-beta).
- **All-kill (questione 59)**: il residuo non è più un leak di cancellazione
  (−0,67 dB!) ma il prodotto dei cut: nelle zone di sovrapposizione tra bande
  il residuo stimato è −15…−25 dB. Misura esatta sulla cascata in v0.3-beta;
  l'auto-mute probabilmente non serve più (il fader resta il silenzio totale).

## 5. Scelte aperte (a Filippo — regola 2)

1. **Profondità di kill — DECISA 2026-09-24 (decisione 77 [F])**: **−30 dB**
   (Rp/R ≈ 31). Il silenzio assoluto resta lavoro del fader. Reti della
   v0.3-beta dimensionate su questa profondità per tutte e 4 le bande.
2. **Taper custom**: conferma la law asimmetrica (cut: tutta la corsa;
   boost: +6 in ~metà corsa elettrica) — dettaglio feel nella sessione
   hardware (voce 40).
3. **Tracking**: pot meccanici di precisione (raccomandato, con selezione)
   vs VCA per banda (perfetto, +costo) — questione 53.
4. **EQ2 di FX send/return (questione 65)**: stessa famiglia di celle
   (2 bande, reti shelf) — conferma in v0.3-beta.

## 6. Rumore e livelli (stime, verifica in v0.3-beta)

- Rumore: 4 celle cascata, resistori ≤31 kΩ nei bracci (domina la termica
  di Za alla massima profondità): stima densità equivalente ~5-10 nV/√Hz
  per cella → integrato ben sotto il target −92 dBu (la v0.2 misurava
  −124,8 dBu con 10 op-amp: qui 4 sezioni ma resistori più grandi — la
  simulazione formale chiude il conto).
- Livelli: boost max ×2 (+6 dB) sulla banda bassa: +16 dBu in → +22 dBu out
  di cella = 13,7 Vp < 16,5 V (clamp del dominio ±18 V) — stesso margine
  della v0.2; il cut non crea headroom issues (≤1).
- Pilotaggio: il finding 2 della v0.2 (carico di sorgente) qui pesa meno
  (Zin ≥ 1 kΩ + Za ≥ ~1 kΩ in serie), ma resta la regola: pilotare da
  bassa impedenza (≤10 Ω) — il buffer/VCA di GAIN lo garantisce.

## 7. BOM di massima (coppia di canali, [PROVVISORIO])

| Voce | Qtà | Note |
|---|---|---|
| Op-amp quad low-noise (classe OPA1654) | 2 | 1 per canale (4 celle) |
| Pot doppi conduttivo-plastica, taper custom | 4 | 1 per banda (sessione voce 40) |
| R/C reti (0,1% dove il detent dipende) | ~48 | Za/Zb matched per banda |
| Stima costo | ~30-45 € | vs 70-95 € della v0.2 |

## 8. Prossimi passi (v0.3-beta)

1. Derivazione + simulazione celle MID (campana) e HIGH (duale).
2. Cascata 4 bande: curve complete per banda e combinazioni, residuo
   all-kill esatto (chiude/riformula 59), interazione bande.
3. Simulazione rumore e livelli formale; mismatch a cascata (tracking).
4. Scelte di Filippo: 53 (tracking: pot precision vs VCA) e taper (voce 40).
   Profondità kill DECISA: −30 dB (decisione 77, questione 66 chiusa).
5. Integrazione in `cdj-line-channel.md` v0.3 (sostituisce §3.3, aggiorna
   §6 BOM e §4 level plan); allineamento EQ2 FX (questione 65).
