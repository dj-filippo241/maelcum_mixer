* ============================================================
* EQ DI CANALE v0.5 — ISOLATOR 4 BANDE, INCROCI C (dec. 152) — banca comune
* (todo 211, 2026-11-04). Incluso da iso-incc-ac.cir, iso-incc-noise.cir,
* iso-incc-dc.cir. Valori [PROVVISORI — regola 3].
*
* Incroci C: f1 = 150 Hz LR2 (12 dB/ott, Q 0,5), f2 = 350 Hz LR4, f3 = 3150 Hz LR4.
* Struttura identica al prototipo (proto-max/coefficienti/canale.py, bande()):
*   LOW     = LP2(f1)          · AP(f2) · AP(f3)
*   LOW-MID = -HP2(f1) · LP4(f2) · AP(f3)
*   MID-HIGH= -HP2(f1) · HP4(f2) · LP4(f3)
*   HIGH    = -HP2(f1) · HP4(f2) · HP4(f3)
* LP2 - HP2 (Q 0,5) = allpass del 1o ordine: la somma al centro e' piatta.
* Segni in hardware: Sallen-Key = +, MFB = -, allpass AP2 (MFB + sommatore) = -.
*   LOW: SK(+) AP2(-) AP2(-) = +                  -> nessun invertitore
*   LM : SK HP2(+) SK SK(+) AP2(-) = -            -> nessun invertitore
*   MH : SK HP2(+) HP4 SK(+) LP: MFB(-) SK(+) = - -> nessun invertitore
*   HIGH: SK HP2(+) HP4(+) HP: MFB(-) SK(+) = -   -> nessun invertitore
* (v0.4 a incroci A: LR4 ovunque e un invertitore sul LOW-MID.)
*
* Manopole: law=0 pot lineare B (quello che esiste a catalogo, RK14K doppio
* 10k B con scatto, residuo 20 ohm, dec. 127, senza contatto di fondo corsa);
* law=1 pot «PIONEER ideale» (taper su misura: partitore = 0,5 (2 th)^1,5 sotto
* il centro, th sopra). Il secondo NON esiste a catalogo: serve per confrontare.
* ============================================================
.param Rp=10k Rend=20
* Sallen-Key LP Butterworth (Q 0,707), unity: R uguali, C fb = 2 Cc
.subckt SKLP in out vcc vee PARAMS: fc=350 Cc=47n
R1 in n1 {1/(2*pi*fc*sqrt(2)*Cc)}
R2 n1 n2 {1/(2*pi*fc*sqrt(2)*Cc)}
C1 n1 out {2*Cc}
C2 n2 0 {Cc}
Xop n2 out out vcc vee OP1654
.ends SKLP
* Sallen-Key HP Butterworth (Q 0,707), unity: C uguali, R_fb = R_gnd/2
.subckt SKHP in out vcc vee PARAMS: fc=350 Cc=47n
C1 in n1 {Cc}
C2 n1 n2 {Cc}
R1 n1 out {1/(2*pi*fc*sqrt(2)*Cc)}
R2 n2 0 {2/(2*pi*fc*sqrt(2)*Cc)}
Xop n2 out out vcc vee OP1654
.ends SKHP
* Sallen-Key LP con Q 0,5 (meta' di un LR2): R uguali, C uguali
.subckt SKLP5 in out vcc vee PARAMS: fc=150 Cc=100n
R1 in n1 {1/(2*pi*fc*Cc)}
R2 n1 n2 {1/(2*pi*fc*Cc)}
C1 n1 out {Cc}
C2 n2 0 {Cc}
Xop n2 out out vcc vee OP1654
.ends SKLP5
* Sallen-Key HP con Q 0,5: C uguali, R uguali
.subckt SKHP5 in out vcc vee PARAMS: fc=150 Cc=100n
C1 in n1 {Cc}
C2 n1 n2 {Cc}
R1 n1 out {1/(2*pi*fc*Cc)}
R2 n2 0 {1/(2*pi*fc*Cc)}
Xop n2 out out vcc vee OP1654
.ends SKHP5
* MFB HP Butterworth, guadagno -1: tre C uguali, R2/R1 = 4,5
.subckt MFBHP in out vcc vee PARAMS: fc=3150 Cc=4.7n
C1 in x {Cc}
C3 x out {Cc}
C2 x nn {Cc}
R1 x 0 {1/(2*pi*fc*Cc*sqrt(4.5))}
R2 nn out {sqrt(4.5)/(2*pi*fc*Cc)}
Xop 0 nn out vcc vee OP1654
.ends MFBHP
* MFB LP Butterworth, guadagno -1: tre R uguali, C a massa = 4,5 C di retroazione
.subckt MFBLP in out vcc vee PARAMS: fc=3150 Cc=2.2n
R1 in x {1/(2*pi*fc*sqrt(4.5)*Cc)}
R3 x out {1/(2*pi*fc*sqrt(4.5)*Cc)}
R2 x nn {1/(2*pi*fc*sqrt(4.5)*Cc)}
C1 x 0 {4.5*Cc}
C2 nn out {Cc}
Xop 0 nn out vcc vee OP1654
.ends MFBLP
* Allpass del 2o ordine (MFB bandpass + sommatore), uscita = -AP
.subckt AP2 in out vcc vee PARAMS: f0=1200 C=10n
R1 in n1 {1/(sqrt(2)*2*pi*f0*C)}
R2 n1 0 {2/(sqrt(2)*2*pi*f0*C)}
C1 n1 nm {2*C}
Rf nm bp {1.5/(sqrt(2)*2*pi*f0*C)}
C2 n1 bp {C}
Xbp 0 nm bp vcc vee OP1654
Ra in n 10k
Rb bp n 5k
Rg n out 10k
Xsm 0 n out vcc vee OP1654
.ends AP2
* Manopola di banda: pot + buffer. th = posizione 0...1; k = partitore
.subckt BPOT in out vcc vee PARAMS: th=0.5 law=0
Rt in w {Rp*(1-if(law>0.5,if(th<0.5,0.5*pwr(2*th,1.5),th),th))+Rend}
Rb w 0 {Rp*if(law>0.5,if(th<0.5,0.5*pwr(2*th,1.5),th),th)+Rend}
Xb w out out vcc vee OP1654
.ends BPOT
Vcc vcc 0 DC 18
Vee vee 0 DC -18
* --- Spina HP condivisa: HP2(f1) SK Q 0,5 | HP4(f2) SK SK | HP4(f3) MFB SK ---
XH1 vin r1 vcc vee SKHP5 fc={f1} Cc=220n
XH2 r1 r2 vcc vee SKHP fc={f2} Cc=100n
XH2b r2 r2b vcc vee SKHP fc={f2} Cc=100n
XH3 r2b r3 vcc vee MFBHP fc={f3} Cc=10n
XH3b r3 r3b vcc vee SKHP fc={f3} Cc=10n
* --- LOW: LP2(f1) SK Q 0,5 + AP2(f2) + AP2(f3) ---
XA1 vin la vcc vee SKLP5 fc={f1} Cc=220n
XP1 la lb vcc vee AP2 f0={f2} C=47n
XP2 lb low_o vcc vee AP2 f0={f3} C=4.7n
* --- LOW-MID: presa r1 -> LP4(f2) + AP2(f3) ---
XB1 r1 ma vcc vee SKLP fc={f2} Cc=100n
XB2 ma mb vcc vee SKLP fc={f2} Cc=100n
XP3 mb lm_o vcc vee AP2 f0={f3} C=4.7n
* --- MID-HIGH: presa r2b -> LP4(f3): MFB + SK ---
XC1 r2b ha vcc vee MFBLP fc={f3} Cc=4.7n
XC2 ha mh_o vcc vee SKLP fc={f3} Cc=10n
* --- HIGH: presa r3b diretta ---
* --- 4 manopole + somma NON invertente (come v0.4 §9): 4x2,49k + ramo servo, guadagno 10 ---
XK1 low_o k1 vcc vee BPOT th={t1} law={law}
XK2 lm_o k2 vcc vee BPOT th={t2} law={law}
XK3 mh_o k3 vcc vee BPOT th={t3} law={law}
XK4 r3b k4 vcc vee BPOT th={t4} law={law}
Rs1 k1 sp 2.49k
Rs2 k2 sp 2.49k
Rs3 k3 sp 2.49k
Rs4 k4 sp 2.49k
Rs5 sv sp 2k
Rsf ng out 1.8k
Rsg ng 0 200
Xsum sp ng out vcc vee OP1612
* --- servo DC: integratore 1M/27n su out -> partitore 100k/499 -> 2k nel nodo di mix
Rsvi out svi 1Meg
Csvi svi svo 27n
Rnsv svp svx 3863
Esv svo 0 svx svi 1e6
Vosv svp 0 DC {vosv}
Rsva svo sv 100k
Rsvb sv 0 499
