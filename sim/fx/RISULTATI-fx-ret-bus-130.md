# RISULTATI — bus FX-RET con le 4 iniezioni dei reroute (dec. 130, todo 133)

Data: 2026-10-26. Topologia: `docs/fase1/fx-module.md` §2bis. Il net Sn
è multidrop sul backplane (~70 cm) e fa da massa virtuale del summing nello
slot 1 del FX-RET n. Ogni reroute (3 cross + SELF) arriva così: uscita del
VCA → I/V OPA1612 20k → driver OPA1612 → 10k lato sorgente sul net.

Netlist:

| File | Cosa misura |
|---|---|
| `fx-ret-bus-noise-130.cir` | rumore al jack SEND, 12 contributori, 4 iniezioni |
| `fx-ret-bus-ac-130.cir` | stabilità del summing con la capacità del net (Cf 10 pF); catena del SELF |
| `fx-ret-bus-ac-cf0-130.cir` | stessa cosa senza Cf |
| `fx-ret-bus-xtalk-130.cir` | crosstalk da una pista vicina pilotata, accoppiata al net |

Per la stabilità la macro OPA1612 ha un secondo polo (115 MHz, margine
~55° a guadagno 1): la macro condivisa ha un polo solo ed è sempre stabile.
Capacità del net verso massa 50 pF [ASSUNZIONE: 70 cm su piano di massa].

## 1. Rumore al jack SEND (pad 0 dB, carico 10k)

| Caso | Densità | Piatto 20-20k | A-wtd | Target ≤ −88 |
|---|---|---|---|---|
| VCA dei 4 reroute al floor datasheet −98 dBV, sempre (convenzione 71A) | 185 nV/√Hz | −89,4 dBu | **−91,5 dBu** | PASS 3,5 dB |
| Core dei VCA muto (reroute chiusi): restano I/V e driver | 60 nV/√Hz | −99,2 dBu | **−101,3 dBu** | PASS 13,3 dB |
| Rev. 71A (3 VCA a peso 1/3, interfaccia allora non definita) | 62 nV/√Hz | −98,9 dBu | −100,8 dBu | |

**FINDING.** La stima di fx-module §2bis (~−110 dBu per iniezione, +0,5 dB
sul bus) contava solo i buffer. Con la dec. 130 il reroute arriva al bus a
**peso 1** (come ogni sorgente da 10k), non a 1/3 come nella rev. 71A. Se il
VCA tiene il floor di −98 dBV anche a reroute chiuso, i 4 VCA dominano e il
bus sale di ~10 dB: −91,5 dBu, ancora dentro il target. Il valore vero sta
fra −91,5 e −101,3: dipende dal rumore del clone V2181L ad alta
attenuazione, che il datasheet non dà (si misura sul lotto, a banco).

Cosa vuol dire all'orecchio: il bus FX va al pedale, non al master. Il
fruscio in più si sente solo nella coda di un'eco o di un riverbero con
GAIN del ritorno alto, ed è comunque 3,5 dB sotto il limite fissato. Coi
reroute aperti il segnale del reroute copre il proprio rumore.

Leve se il banco dà il caso peggiore e serve margine:
1. Iniezione a peso 1/2 (20k invece di 10k): −4…−5 dB di rumore, ma il
   reroute a fondo corsa arriva al bus a −6 dB (cambia la musica: va
   chiesto a Filippo).
2. Mute dei VCA chiusi con la stessa linea del kill (CV oltre il fondo):
   non cambia il rumore del core, quindi serve solo se il banco dice che il
   floor non scende con l'attenuazione.

## 2. Stabilità del summing col net lungo

Picco della risposta da una sorgente al bus, sopra 100 kHz:

| Capacità del net | Cf 10 pF su Rf | Senza Cf |
|---|---|---|
| 0 pF | 0 dB (nessun picco) | 0 dB |
| 50 pF | 0 dB | **+3,0 dB** |
| 100 pF | 0 dB | **+5,6 dB** |

Cf 10 pF su Rf 10k (polo a 1,6 MHz) è **obbligatorio** in ogni FX-RET: il
net lungo carica la massa virtuale e senza Cf il summing va verso
l'oscillazione. A 1 kHz il guadagno resta 0,000 dB in tutti i casi.

## 3. Crosstalk sul net da una pista pilotata vicina

Sorgente a bassa impedenza (driver, RET out, MSUM) accoppiata al net con
una capacità Cc. La corrente entra nella massa virtuale e Rf la converte:
il crosstalk sale di 6 dB per ottava.

| Cc | 1 kHz | 10 kHz | 20 kHz |
|---|---|---|---|
| 1 pF | −84 dB | −64 dB | −58 dB |
| 2 pF | −78 dB | −58 dB | −52 dB |
| 10 pF | −64 dB | −44 dB | −38 dB |

**FINDING.** `sistema-backplane.md` §4 stima «< −100 dB a 20 kHz» con
0,5-1 pF fra pin. Vale fra due nodi ad alta impedenza; non vale verso un
net a massa virtuale: con 1 pF il crosstalk è −58 dB a 20 kHz. I pin
dello stesso slot (L e R dello stesso net) sono entrambi a massa virtuale e
non si disturbano; il rischio sono le piste lunghe parallele a linee
pilotate. Per stare al livello del DJ bus (−72 dB a 20 kHz, dec. 94)
l'accoppiamento verso ogni linea pilotata deve restare **≤ 0,2 pF**.

**Vincoli PCB del backplane** (dalla simulazione):
- net S1-S4 su strato interno fra due piani di massa (stripline), con
  pista di guardia a massa ai lati per tutta la lunghezza;
- nessuna linea pilotata in parallelo ai net per più di pochi cm; gli
  incroci a 90°;
- ai pin, l'AGND fra gli slot resta (già nel pinout).

## 4. Catena del SELF attraverso il backplane

Risposta dalla corrente del VCA al bus (I/V con 33 pF, driver, 10k, net,
summing con Cf 10 pF): 20 Hz −0,00001 dB; 20 kHz **−0,03 dB e −5,5°**
(−4,8° senza Cf). Il ritardo della pista (ns) non conta. L'anello del SELF
vede lo stesso guadagno di prima: il «bounded-by-design» di §8.5 resta
valido. Uguale con 0, 50 e 100 pF sul net.

## 5. Stato

- Rumore, stabilità, crosstalk e SELF: simulati. Il numero vero del rumore
  aspetta il banco (floor del V2181L ad alta attenuazione).
- Corrente delle iniezioni sul W1 (+64 mA): `sim/system/RISULTATI-psu-box.md` §6.
