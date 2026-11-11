* =====================================================================
* LED DI LIVELLO DELLE 5 VIE (dec. 176 g, todo 291) — celle condivise
* Design: docs/fase2/five-way-led-livello.md
* Uso: .include led-livello.inc  (dopo ../lib/opamp-audio.inc)
*
* Celle riusate dal MIC (pcb/tools/celle_micmono.py, detector + led3):
*   DET   superdiodo + hold 100n + release 3M + buffer (sim/system/meter-det-03s.cir)
*   LED3  4 comparatori LM339, latch del rosso 0,52 s, LED bicolore
* Celle nuove: LP2 / HP2 = Sallen-Key Butterworth del banco d'analisi.
*
* OPDET = sezione OPA1654 del superdiodo. Due varianti:
*   OPDETC  uscita fermata a -1,5 V (macro dei netlist sim/meter: clamp ideale)
*   OPDETN  uscita libera fino al rail (la cella del MIC com'e' disegnata:
*           nessun diodo di clamp)
* Comparatori: interruttori comandati in tensione, offset zero, Ron 300 ohm
* (~16 mA di corrente di sink, datasheet TI LM339 SLCS006Z).
* =====================================================================
* REV 2026-11-11: lo STATO del polo (p1) e' fermato ai limiti dell'uscita, non
* solo l'uscita. Con il solo limit() sull'uscita (macro OPDET di sim/meter)
* p1 corre a -1e4 V nella mezz'onda negativa e ci mette millisecondi a
* tornare: sotto ~+3 dBu interni l'hold non si caricava piu' (bozza del
* 10/11: MID senza giallo, SUPER spento). E1 limitato a +-1e5 V: slew
* ~12 V/us, come l'OPA1654 (10 V/us). L'uscita resta la stessa.
.model DID D(Ron=1m Roff=1G Vfwd=0)
.subckt OPDETC inp inn out vp vm
E1 xx 0 value={limit(1e6*(V(inp)-V(inn)),-1e5,1e5)}
R1 xx p1 5005
C1 p1 0 1.59u
Ehi hi 0 value={V(vp)-1.5}
Vlo lo 0 DC -1.5
Dh p1 hi DID
Dl lo p1 DID
E2 out 0 p1 0 1
.ends OPDETC
.subckt OPDETN inp inn out vp vm
E1 xx 0 value={limit(1e6*(V(inp)-V(inn)),-1e5,1e5)}
R1 xx p1 5005
C1 p1 0 1.59u
Ehi hi 0 value={V(vp)-1.5}
Elo lo 0 value={V(vm)+1.5}
Dh p1 hi DID
Dl lo p1 DID
E2 out 0 p1 0 1
.ends OPDETN
.model D1N4148 D(Is=2.53n Rs=0.568 N=1.752 Cjo=4p M=0.4 Tt=20n Iave=200m Vpk=100)
* LED alta efficienza: ~2,0 V a 2,8 mA (rosso), ~2,1 V (verde)
.model LEDR D(Is=1e-20 N=1.9 Rs=5)
.model LEDG D(Is=1e-20 N=2.0 Rs=5)
.model CMP SW(Ron=300 Roff=1G Vt=0 Vh=-50u)
.model FETSW SW(Ron=3 Roff=1G Vt=2 Vh=-0.3)

* --- Sallen-Key passa-basso, guadagno 1: Q = 0,5*sqrt(C1/C2), w0 = 1/(R*sqrt(C1*C2))
.subckt LP2 in out vp vm params: R=10k C1=22n C2=10n
R1 in a {R}
R2 a b {R}
C1 a out {C1}
C2 b 0 {C2}
X1 b out out vp vm OP1654
.ends LP2
* --- Sallen-Key passa-alto, guadagno 1: Rfb = Rgnd/2 per Q 0,707
.subckt HP2 in out vp vm params: C=10n Rfb=10k Rgnd=20k
C1 in a {C}
C2 a b {C}
R1 a out {Rfb}
R2 b 0 {Rgnd}
X1 b out out vp vm OP1654
.ends HP2
* --- Rivelatore di picco (cella del MIC): superdiodo, hold, release, buffer
.subckt DET in met hold vp vm
Xop in hold dout vp vm OPDETC
Rcomp dout d1a 1k
D1 d1a hold D1N4148
Ccomp dout hold 47p
Chold hold 0 100n
Rrel hold 0 3Meg
Xbuf hold met met vp vm OP1654
.ends DET
* --- Lo stesso senza clamp sull'uscita del superdiodo (cella del MIC com'e')
.subckt DETN in met hold vp vm
Xop in hold dout vp vm OPDETN
Rcomp dout d1a 1k
D1 d1a hold D1N4148
Ccomp dout hold 47p
Chold hold 0 100n
Rrel hold 0 3Meg
Xbuf hold met met vp vm OP1654
.ends DETN
* --- LED tricolore: C1 latch, C2 uscita del latch, C3 giallo/rosso, C4 verde
* kr = catodo del rosso (dopo la 1k), gfd = catodo del verde (dopo la 1k)
.subckt LED3 met vr vy vg vtl v5 kr gfd lt
S1 lt 0 met vr CMP
Rlt v5 lt 750k
Clt lt 0 1u
S2 lq 0 vtl lt CMP
Rlq v5 lq 10k
S3 kr 0 met vy CMP
S4 kg 0 met vg CMP
D5 kr lq D1N4148
S5 gfd kg lq kg FETSW
.ends LED3
