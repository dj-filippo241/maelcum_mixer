# RISULTATI — Gate kill a switch analogici (redesign decisione 88)

Data: 2026-09-30. Netlist: `gate-sw-iso.cir` (off-isolation, .ac),
`gate-sw-click.cir` (click hard-cut, .tran), `bank-sw-polarity.cir`
(banca allineata completa + gate reali, 7 casi kill × 12 freq).
Metodo: solo FIND/MAX (nessun INTEG — quirk LTspice 26.0.2, §8.9).
Macro op-amp A0=120 dB come `bank-aligned.cir` (la macro v0.1 A0=60 dB
dà ~0,15 dB di errore di loop = artefatto, già documentato in quel file).

## 1. Scelta topologia: PI-SPDT, non serie semplice

Switch classe **ADG1434** (quad SPDT iCMOS ADI): Ron ≤ 4,7-5 Ω, dual
supply ±4,5…±16,5 V, break-before-make, logica IN 3 V compatibile senza
VL, segnali rail-to-rail. Dati da pagina prodotto ADI/Mouser 2026-09-30 —
**DA VERIFICARE su datasheet ufficiale (Rev. E) prima del PCB** (thread
EngineerZone segnalano casi ESD/over-voltage: protezioni ingressi da
valutare in layout). Famiglia unica per kill 5-way + assign FX +
LINE/PHONO (come prescrive dec. 88): SPDT copre tutti e tre gli usi.

Configurazione per banda = **π SPDT**: polo sul nodo d'ingresso summer;
serie verso l'uscita di banda; shunt a GND da off. Kill = serie aperta
+ nodo ancorato a GND via Ron (4,7 Ω).

Off-isolation misurata (carico reale: 10k ingresso summer invertente;
Coff incerta → sweep parametrico 2p/10p/30p/60p):

| Config | 20 Hz | 350 Hz | 1 kHz | 3,5 kHz | 20 kHz | 50 kHz |
|---|---|---|---|---|---|---|
| Serie SPST, Coff 30p | −88 | −64 | −55 | −44 | −28,5 | −20,6 |
| Serie SPST, Coff 60p | −82 | −58 | −48,5 | −37,6 | −22,5 | −14,7 |
| **π SPDT, Coff 30p** | −155 | −130 | −121 | −110 | **−95** | −87 |
| **π SPDT, Coff 60p** | −149 | −124 | −115 | −104 | **−89** | −81 |

(dB rispetto a 1 V in ingresso; π con Coff 2p/10p: ancora meglio).

**Serie semplice BOCCIATA**: −22…−52 dB a 20 kHz = la stima del doc
(−60…−70) non è raggiungibile senza shunt. Il π SPDT supera il VCA
(−90…−100 dopo trim) e rende il residuo off-state **sotto il floor di
rumore del modulo**: banda killata a +6 dBu → residuo −89 dBu @20 kHz
vs floor −83,2 dBu = il silenzio resta silenzio.

Perdita d'inserzione on-state: **−0,039 dB** (Ron 4,7+4,7/2 su 10k),
uniforme 1 kHz-60 kHz → assorbita dal make-up (dec. 73). Piatta su
tutto lo sweep koff.

## 2. Polarità: 2 invertitori unity per lato su SUB e MID

La somma telescopica LR4 richiede segni uniformi al summer; polarità
naturali della banca allineata (AP2 invertenti): SUB −(3), KICK +(2),
MID −(1), HIGH +(0), SUPER +(0). Il gate VCA (invertente) correggeva il
segno; lo switch in serie NO → **2 invertitori unity per lato su SUB e
MID** (le bande DISPARI di AP2, regola §3.1), R 2k 0,1% matched (stessa
disciplina delle coppie APSUM). Banca allineata INTATTA (l'alternativa
"scambio SK→MFB sulle sezioni finali KICK/HIGH" è a costo silicon zero
ma tocca il cuore di precisione validato §8.2: scartata).
Costo: +2 sezioni op-amp per lato (28→30), +1 quad per modulo.
Impatto rumore stimato +~0,3 dB sul contributo banca → **da riverificare
nella campagna voce 71A** (module-noise-v03.cir va integrato con i 2
invertitori).

TRAPPOLA documentata: la prima stesura metteva gli invertitori su
KICK/HIGH seguendo le B-source di `bank-lr4.cir` (v0.1, banca NON
allineata) → nulla di −38 dB a 3,5 kHz (cancellazione HIGH/SUPER).
Nella banca allineata la convenzione è SUB/MID (`bank-aligned.cir`
Bg1/Bg3 con segno −, e §3.1 del doc).

## 3. Piattezza con gate reali (bank-sw-polarity.cir)

Nessun kill: **−0,004…−0,011 dB su 5 Hz-60 kHz** (gmax −0,0043; il
−0,004 = Ron serie, il −0,007 HF = poli Coff su 10k, comuni a tutte le
bande). Requisito ±0,1 dB: margine 15×. La flatness §8.2 è preservata.

Residui kill (banda killata, in banda): invariati rispetto a
`bank-aligned.cir` (dominano le code di overlap LR4, non lo switch):
SUB −76,3 @10 Hz; KICK −38,3 @30 / −17,6 @200; MID −16,1 @700;
HIGH −12,2 @2,5k; SUPER −50,5 @15k / −68,2 @25k. ALL-KILL: gmax
**−85,5 dB** su 5 Hz-60 kHz (era −inf col VCA ideale): limitato dalla
somma di potenza delle 5 off-isolation; sotto il floor del modulo.

## 4. Click hard-cut (gate-sw-click.cir, .tran)

Kill al PICCO (worst §8.5), ingresso +6 dBu (max sheet, 2,19 Vp),
1 kHz, BBM 150 ns serie→shunt:

| Caso | Livello pre-kill | Passo/transiente | Nota |
|---|---|---|---|
| π SPDT, kill al picco | −2,178 V (summer) | **2,18 V** (×2 make-up = ~4,4 V out) | nessun overshoot: max post = 1,6 µV |
| π SPDT, kill allo zero | ~0 | **±0,35 mV** | taglio a zero-crossing = click trascurabile |
| serie SPST, kill al picco | −2,178 V | 2,18 V + coda 3,3 mV (τ 0,3 µs su 10k) | π più pulito: shunt azzera il nodo |

Il meccanismo è identico all'hard-cut VCA §8.5 (3,64 V con ingresso
+10 dBu: scalato a +6 dBu ≈ 3,4 V, coerente): il click = il gradino
del segnale istantaneo, non dipende dalla tecnologia di switch.
**Già accettato da dec. 88** (standard di scena: Jah Tubbys/JB cut-out,
Mostec relè). Charge injection reale (−20…−50 pC, famiglia ADG14xx):
spike mV su nodo ~10k = sub-dominante rispetto al gradino (non modellato
in sim: il modello SW non ha Q_inj → verifica a banco).
Dato musicale non bloccante: il click è massimo al picco del programma
e quasi nullo al passaggio per lo zero — il gesto chop sul battere
"suona" più del taglio a segnale basso.

## 5. Pilotaggio pannello e alimentazione

- IN logico 3 V compatibile, nessun VL: switch di pannello esistente →
  +5 V logici via 10k al pin IN, pull-down 100k lato modulo. Audio MAI
  dai contatti pannello (dec. 88 ✓). Kill = IN basso (serie apre,
  shunt chiude).
- **Alimentazione: rail ±15 V dedicato** (modulo op-amp a ±18 V >
  max ±16,5 V dell'IC). Assorbimento switch trascurabile (<100 µA in
  3 IC) → LDO/coppia 78L15-79L15 locale o rail di sistema: decisione
  rimandata al design PSU (q20, task sistema). Rail condivisibile con
  assign FX / LINE-PHONO (stessa famiglia).
- Conteggio: 10 SPDT per modulo (5 bande × 2 lati) = **3× ADG1434**
  (12 canali, 2 spare) [PROVVISORIO — regola 3: valori non congelati,
  reperibilità e second source nel task reperibilita; candidati
  equivalenti: ADG1634L 4,7 Ω, ADG1334 low-QinJ].

## 6. Stato

Ingegneria del gate switch CHIUSA (topologia π SPDT + invertitori
SUB/MID + pilotaggio + numeri off-isolation/click/piattezza). Restano:
verifica datasheet ufficiale ADG1434, protezioni ESD/over-voltage in
layout, misura click/charge injection a banco, riverifica rumore con
invertitori (voce 71A). BOM §7 aggiornata [PROVVISORIO].
