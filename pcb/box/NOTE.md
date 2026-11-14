# BOX: note della bozza v0.1 (2026-11-14)

Scheda del box dell'alimentatore esterno, da `box.py` (sistema-psu-esterno.md §1-§3,
RISULTATI-psu-box.md §7, dec. 131). 260 x 200 mm, 4 strati, 141 componenti, 93 reti.
Esito: **PASSA** (ERC 0 errori, DRC 0 errori e 0 aperti a tutti e 4 i tentativi di Freerouting;
27 avvisi attesi di parità, pin liberi del J1).

## Cosa c'è

- Morsetti dei secondari (W1 2x21 V 7,0 A, W2 2x18 V 1,5 A, W3 2x20 V, W4 9 V) e fusibili lenti
  prima dei ponti: W1 T8 A, W2 T2 A, W3 T630 mA, W4 T3,15 A.
- Ponti: W1 KBPC2502 (25 A), gli altri GBU4D. Bulk: W1 22 mF, W2 10 mF, W3 4,7 mF, W4 10 mF.
- Quattro LDO discreti a MOSFET (§2.2, valori di psu-box-w1-142-7a.cir): W1 +-22,0 V con Rsense
  0,15 ohm (IRFP9140N / IRFP140N, TO-247), W2 +-19 V con 0,56 ohm (IRF9540N / IRF540N, TO-220).
- +5 V col LM1084-5.0; V_FAN = raw W4 sul pin 17 del cavo, ritorno sul 18.
- AC_OK (§2.5): doppia semionda dal W1, 47k / 4,7k / 10 uF, soglia 1,384 V (LM4040 + 8,06k/10k),
  LM393: sezione A con isteresi, sezione B open collector verso il cavo (pull-up nel PSU-IN).
- J1 Mini-Fit Jr 2x12 con lo stesso ordine del J2 di PSU-IN.
- Pezzi sull'aletta (MOSFET, ponti, LM1084) sul bordo basso, y = 12.

Fuori dalla scheda (cablaggio del box): presa IEC col filtro, interruttore, fusibile del primario
T3,15 A, NTC col relè di bypass, toroidale, PE sul telaio. Fori di fissaggio senza pad: gli 0 V del
box non toccano la terra (§3).

## Scelte segnate NOTA

1. Bulk del W1 a 50 V (il documento dice 35): a vuoto e rete +10 % il picco vale ~34 V
   (21 x 1,07 x 1,1 x 1,414 - 0,7).
2. OPA197 come amplificatore d'errore: 36 V di lavoro (40 assoluti) contro ~34 V di raw nel caso peggiore.
3. Pinout G-D-S dei MOSFET: da confermare sul datasheet prima dell'ordine.
4. Portafusibile da 10 A per il T8 A del W1 (Schurter 0031.8201): da verificare a catalogo.
5. AC_OK: rivelatore sullo 0 V audio, comparatore sul CTRL_GND; si uniscono alla stella del mixer
   (differenza <= ~0,1 V, ~3 % della soglia). Isteresi 10k / 1M (~50 mV).
6. Collegamenti Kelvin (0 ohm) fra le reti larghe di potenza e le reti sottili del controllo
   (RK_, SK_, OK_, ZK_, 5V_L, GND_L): le piste larghe non entrano nei pin SOT-23 e SOIC, e il
   partitore legge la tensione al condensatore d'uscita.
7. Masse senza colata (0V_LN, 0V_M, 0V_FAN) a 0,6 mm; CTRL_GND come piano pieno su In2.
   Piste di potenza del W1 a 2,0 mm: per 2,7 A per ramo servono colate di potenza o piste sui due
   strati (come PSU-IN NOTA 5).
8. Bulk 25 V sul W4: picco ~15 V a vuoto.

## Giri della PCB

1. 240 x 170: 41 aperti, 2 courtyard (ponti GBU a 20 mm di passo).
2. 260 x 200, ponti a 26 mm: 31 aperti (CTRL_GND 13, C+5 6, W1 3-3-3).
3. link_pairs: 50 aperti. I gemelli del J1 (passo 4,2 mm) stavano oltre dmax 4,0.
4. Causa principale: reti larghe (0,8-2 mm) nei pin SOT-23 e SOIC. Tie Kelvin: 24 aperti.
5. `d.link_pairs_dmax = 4.5` (nuovo nel generatore) e DesignRiprova: 13 aperti, tutti sulle masse.
6. Masse a 0,6 mm: 9. Bulk di W3 e W4 accanto ai ponti: 8, tutti CTRL_GND.
7. `d.piano_in2 = "CTRL_GND"` (nuovo nel generatore: In2 piano pieno di una seconda massa): **PASSA**.

## Resta

- Colate di potenza del W1 (NOTA 7).
- Schema leggibile in inglese: il box non è ancora in `pcb/schematics-readable.pdf` (leggibile.py).
- Pinout dei MOSFET e portafusibile del W1 (NOTA 3, 4).

Verificato in: KiCad (ERC, DRC). Python: no. LTspice: no (valori dai netlist psu-box-*). Live: no.
