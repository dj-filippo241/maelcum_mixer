# CUE: note della scheda (todo 294)

Due schede, generate da `cue.py` (segnale, col C96) e `cue-comandi.py` (comandi dietro il
pannello). Fonte: `docs/fase3/sistema-cue.md` v0.2. Valori [PROVVISORIO].

## Scheda di segnale (`cue.py`)

196 × 124 mm (prima 177: giro 1), sinistra-destra sotto il pannello del CUE (`pcb/PIANO-SCHEDE-F.md`), C96 in basso.

| Blocco | Pezzi |
|---|---|
| [A] somma dei cue, [B] MON invertente, [C2] buffer del blend | OPA1612 ×3 su ±15 LN |
| [E] ampli cuffia L e R | OPA1612 ×2 su ±18 (uno per lato), MJE340/350 ×2+2, BC847/BC857, BF245B ×4, trimmer 500 Ω ×2 |
| [F] uscite | Rserie 10 Ω 2 W ×4, relè G6K-2F ×2, AO3400A |
| [G] protezione | TL431, LM339 ×2 |
| Alimentazione | LM317/337 TO-220 (±18 dal raw ±27), LM317/337 SOT-223 (±16,5 dal raw ±22), LT3045/LT3094 (±15 LN) |

### Scelte non scritte nel design doc (NOTA)

1. **Iniezione 10k sulla scheda del CUE.** Il design doc mette le 10k «lato sorgente, nel
   modulo CDJ»; `canale.py` esce invece con 47 Ω dopo lo switch (slot 2). Ogni cue ha il suo
   slot, quindi le 10k stanno qui senza cambiare niente: guadagno −0,04 dB.
2. **Buffer [C2] fra BLEND e LEVEL** (un OPA1612 in più). Senza, il LEVEL da 10k carica il
   cursore del BLEND, che ha fino a 2,5 kΩ al centro: il centro scenderebbe a −8 dB per parte
   (−1,9 dB in tutto) invece dei −6 bloccati in §5. Il Test 2 di `RISULTATI-cue.md` non aveva
   il LEVEL sul cursore. Calcolo: carico 10k, sorgente X(1−X)·10k → 1/(1 + X(1−X)).
   Annotato in `sistema-cue.md` §5 (REV 2026-11-11).
3. **Rserie: 4, non 8.** Il diagramma di §2 dice «Rser 10 Ω ×4» (una per ramo-jack: L e R per
   due jack); la BOM di §10 dice 8. Qui 4, a foro passante da 2 W.
4. **Jack sulla scheda comandi, con un cavo loro (J3 ↔ J4) e un ritorno loro (HPG).** La
   corrente delle cuffie (fino a ~140 mA) non passa sul filo di massa dei pot: sul cavo dei pot
   farebbe 1-4 mV di segnale d'uscita sulla massa del LEVEL. HPG si unisce ad AGND con uno 0 Ω
   vicino all'ampli.
5. **1 MΩ a massa** sull'ingresso di [C2] e sull'ingresso dell'ampli: a cavo staccato gli
   ingressi non restano liberi. In uso pesano meno di 0,01 dB.
6. **Finestre dei raw negativi**: un LM339 su +5 V non legge tensioni negative. Partitore fra
   VREF (2,495 V) e il raw: il nodo sale quando il raw cala. Soglia 1,00 V; −22 scatta a
   −17,0 V (10k/120k), −27 a −20,0 V (10k/140k). BAT54 a CTRL_GND sui due nodi: a +5 V spento
   il nodo non scende sotto −0,3 V. Calcolo, da simulare insieme al timer.
7. **Timer**: 1,2 MΩ × 2,2 µF, soglia VREF: ~1,8 s (requisito 1,5-2 s). Scarica di CT con un
   BAT54 verso ROK: al calo di un raw i relè aprono in ~1 ms più il rilascio del relè.
8. **Pre-regolatori ±16,5 in SOT-223** (25 mA, 0,14 W): il design doc non dice il contenitore.
9. **Finali**: rame ≥ 4 cm² (§5) e moltiplicatore di Vbe vicino ai finali: il generatore non
   li garantisce. Da controllare nel layout vero.
10. **Un OPA1612 per lato nell'ampli** (il design doc ne mette uno per L e R). Con un chip
    solo il grappolo legava al chip i passivi dei due ampli e il blocco usciva dalla scheda.
    La seconda sezione di ogni chip resta libera, a inseguitore a massa. Le Rserie da 2 W
    stanno in un blocco loro: dentro il blocco dell'ampli lo allargavano a 193 mm.

## Scheda comandi (`cue-comandi.py`)

198 × 48 mm, tutto il pannello meno i bordi. BLEND (10k lin, scatto) e LEVEL (10k log) doppi;
due jack Neutrik NJ3FD-V verticali; J3 (2x7, pot) e J4 (2x3, cuffie) verso J2 e J3 di `cue.py`.

## Esiti

- Scheda comandi: PASSA al primo tentativo, controllo audio 0 (2026-11-11).
- Scheda di segnale: NON PASSA ai giri 1 (177 mm, 113 aperti) e 2 (196 mm, strato interno,
  CTRL_GND gemelli, protezione sul retro: 97 aperti). Causa trovata il 2026-11-11 alle 19:40:
  il grappolo lega a U4 (op-amp dell'ampli, blocco a sé) 28 passivi di tutti e due gli ampli;
  il blocco non trova posto («servono 117 mm in più di larghezza») e finisce fuori scheda. Non è
  lo spazio: la scheda è mezza vuota. Rimedio (giro 3, punto 10): un OPA1612 per lato dentro il blocco del
  suo ampli e Rserie in un blocco loro; tutti i blocchi entrano nella scheda.
