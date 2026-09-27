* =====================================================================
* MACROMODELLE OP-AMP AUDIO REALI — libreria condivisa (beta-3, 2026-09-27)
* Uso: .include ../lib/opamp-audio.inc  (path relativo al netlist)
*   X<name> <inp> <inn> <out> <vp> <vm> OP1654 | OP1612
*
* OP1654 (classe TI OPA1654, quad FET-input, celle EQ):
*   en = 4,5 nV/√Hz @1 kHz (datasheet TI) → Rn = en²/4kT = 1223 Ω
*   A0 = 120 dB (1e6), GBW = 20 MHz (datasheet 18; convenzione di progetto
*   già usata in cdj-eq) → polo dominante fp = 20 Hz
*   FET-input: corrente di rumore ~fA/√Hz → assente giustificata
*   Alimentazione progetto ±18 V = limite datasheet (±2,25…±18 V)
*
* OP1612 (classe TI OPA1612, dual bipolare, buffer/summer/make-up):
*   en = 1,1 nV/√Hz → Rn = 73 Ω
*   A0 = 130 dB (3,16e6), GBW = 80 MHz → fp = 25,3 Hz
*   bipolare: in ≈ 2 pA/√Hz — irrilevante SOLO perché qui lavora su nodi
*   a bassa Z (virtual ground di buffer/summer/make-up, <100 Ω):
*   REGOLA D'USO: OP1612 solo su sorgenti <100 Ω; sopra ~500 Ω usare
*   OP1654 (FET). (2 pA × 2,5 kΩ = 5 nV, 4,5× la sua en.)
*
* Polo dominante realizzato con R piccola + C grande (R1·C1 = 1/2π·fp):
* la termica di R1 resta ≥40 dB sotto la en del chip in tutta la banda
* audio (con R = 50 MΩ del primo tentativo il polo da solo metteva
* ~18-150 nV/√Hz in uscita — artefatto, non fisica del chip).
*
* ASSENTI (limite del macromodello, verifica a banco/prototipo):
*   - THD (macro lineare; datasheet: 1654 0,00005%, 1612 0,00008% a 1 kHz
*     G=1 — il guadagno d'anello alto in banda audio rende credibile la
*     stima "THD closed-loop ≈ THD open-loop × (1+A_loop)/A_loop")
*   - corrente di rumore (vedi regola d'uso sopra), 1/f sotto ~10 Hz
*   - slew/limit reali: clamp duro ±(rail−1,5 V) invece della saturazione
*     morbida (i test di livello vanno letti come "tocca il rail")
* =====================================================================
.subckt OP1654 inp inn out vp vm
Rn inp inx 1223
E1 xx 0 value={1e6*(V(inx)-V(inn))}
R1 xx p1 5005
C1 p1 0 1.59u
E2 out 0 value={limit(V(p1),V(vm)+1.5,V(vp)-1.5)}
.ends OP1654
.subckt OP1612 inp inn out vp vm
Rn inp inx 73
E1 xx 0 value={3.16e6*(V(inx)-V(inn))}
R1 xx p1 3955
C1 p1 0 1.59u
E2 out 0 value={limit(V(p1),V(vm)+1.5,V(vp)-1.5)}
.ends OP1612
