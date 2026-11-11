* =====================================================================
* Todo 289 (2026-11-11): levetta HPF/OFF/LPF del canale con la LOGICA
* VERA e la catena del fader com'e' sulla scheda (pcb/canale/canale.py,
* pcb/tools/celle_vca.py dopo il todo 281). Circuito condiviso da
*   filtsel-dip-logica.cir  (click e tempi del dip)
*   filtsel-dip-flick.cir   (levetta che torna indietro: blocco)
* Catena: levetta -> XOR (74HC86) -> OR a diodi = DIFF (100k a massa)
*   -> due RC 10k/50n bufferizzati (OPA1612) -> DIPCV -> 4,99k nel nodo
*   di somma dello shaper del fader -> stadio del partitore x(-1,916)
*   -> partitore 18,2k/1k -> pin EC- dei VCA.
*   Ritardo: R/47n + due Schmitt (74HC14) = CLK -> 74HC74 copia la
*   levetta su Q -> ADG1434 (BBM) commuta; Q = levetta, DIFF si rilascia.
* logic=0  com'e' disegnato: RC del dip e ritardo 33k appesi al nodo DIFF
*          dei diodi. In rilascio il diodo si apre: DIFF scende solo
*          attraverso il 100k, con 50n + 47n appesi.
* logic=1  DIFF ripreso da due porte libere (74HC14 sez. 6 + 74HC86
*          sez. 4 con B a +5 V): RC e ritardo 33k pilotati da un'uscita.
* logic=2  come 1, ritardo rd2/47n (rd2 nel .cir: 47k, 56k, 68k) e diodo
*          di scarica (anodo DLY, catodo DIFF ripreso) in parallelo a rd2.
* corner: soglie del 74HC14 nel ritardo, a 5 V (TI SCLS085L, interpolate
*   fra 4,5 e 6 V): 0 tipiche VT+ 2,77 / VT- 1,73; 1 minime 1,73 / 1,00;
*   2 massime 3,49 / 2,70 V.
* 74HC74: master-slave (fronte di salita vero), non un latch trasparente.
* Op-amp: OPS (stato del polo fermato ai rail - 0,2 V, GBW 20 MHz,
* slew ~12 V/us), regola NASTRO B9 / led-livello.inc.
* Uscite logiche 50 ohm; levetta gia' pulita dall'antirimbalzo.
* =====================================================================
.include ../lib/that2181.inc
.model DID D(Ron=1m Roff=1G Vfwd=0)
.model D1N4148 D(Is=2.52n Rs=0.568 N=1.752 Cjo=4p Tt=4n)
.subckt OPS inp inn out vp vm
E1 xx 0 value={limit(1e6*(V(inp)-V(inn)),-1e5,1e5)}
R1 xx p1 5005
C1 p1 0 1.59u
Ehi hi 0 value={V(vp)-0.2}
Elo lo 0 value={V(vm)+0.2}
Dh p1 hi DID
Dl lo p1 DID
E2 out 0 p1 0 1
.ends OPS
.param vth={if(corner==1,1.73,if(corner==2,3.49,2.77))}
.param vtl={if(corner==1,1.00,if(corner==2,2.70,1.73))}
.param rdl={if(logic==2,rd2,33k)}
.model SWUP SW(Ron=50 Roff=1G Vt=2.2 Vh=0.5)
.model SWDN SW(Ron=50 Roff=1G Vt=-2.2 Vh=0.5)
.model SKUP SW(Ron=50 Roff=1G Vt={(vth+vtl)/2} Vh={(vth-vtl)/2})
.model SKDN SW(Ron=50 Roff=1G Vt={-(vth+vtl)/2} Vh={(vth-vtl)/2})
.model SWH SW(Ron=100 Roff=1G Vt=2.5 Vh=0)
.model SWLO SW(Ron=100 Roff=1G Vt=-2.5 Vh=0)
.model SWADG SW(Ron=5 Roff=1G Vt=2.5 Vh=0)
.model SWADGN SW(Ron=5 Roff=1G Vt=-2.5 Vh=0)
.options cshunt=1e-15
Vcc vcc 0 DC 15
Vee vee 0 DC -15
V5 v5 0 DC 5
Vref nref 0 DC -5
V1 in 0 SINE(0 {vp} 1k)
*
* ---------------- logica (un bit: la levetta da OFF a HPF) ----------------
* d0 = uscita dell'antirimbalzo (PWL nel .cir)
* 74HC74 master-slave: il master segue D0 con CLK basso, lo slave copia il
* master con CLK alto -> Q0 cambia solo sul fronte di salita
Sm d0 mst 0 clk SWLO
Cm mst 0 100p
Rm0 mst 0 1G
Em mstb 0 mst 0 1
Ss mstb q0 clk 0 SWH
Cq q0 0 100p
Rq q0 0 1G
* XOR levetta / stato, uscita 50 ohm
Bx xo 0 V={5*abs(u(V(d0)-2.5)-u(V(q0)-2.5))}
Rxo xo x0 50
Dor x0 diffr D1N4148
Rpd diffr 0 100k
* DIFF ripreso: Schmitt (sez. 6) + XOR con +5 V (sez. 4), 50 ohm
Sbu v5 diffb diffr 0 SWUP
Sbd diffb 0 0 diffr SWDN
Cbb diffb 0 10p
* RC del dip e ritardo: dal nodo dei diodi (logic=0) o dall'uscita ripresa
Rda diffr dp1 {if(logic==0,10k,1e12)}
Rdb diffb dp1 {if(logic==0,1e12,10k)}
Cd1 dp1 0 50n
Xb1 dp1 dpb1 dpb1 vcc vee OPS
Rd2 dpb1 dp2 10k
Cd2 dp2 0 50n
Xb2 dp2 dipcv dipcv vcc vee OPS
Rla diffr dly {if(logic==0,rdl,1e12)}
Rlb diffb dly {if(logic==0,1e12,rdl)}
Cly dly 0 47n
* logic=2: diodo di scarica del ritardo verso il DIFF ripreso
Dsc dly dsk D1N4148
Rsk dsk diffb {if(logic==2,1m,1e12)}
* due Schmitt in fila = CLK non invertito
Scu v5 clk dly 0 SKUP
Scd clk 0 0 dly SKDN
Ccl clk 0 10p
*
* ---------------- shaper del fader (FADER di celle_vca.py) ----------------
Vx x 0 DC {xp}
Rmx x sj 43.2k
Ra1 x n1 68.1k
Rb1 n1 nref 357k
D1 n1 sj D1N4148
Ra2 x n2 20.0k
Rb2 n2 nref 38.3k
D2 n2 sj D1N4148
Ra3 x n3 976
Rb3 n3 nref 1.33k
D3 n3 sj D1N4148
Rx0 x 0 100k
Rf sj sh 10k
Rdip dipcv sj 4.99k
Xsh 0 sj sh vcc vee OPS
* stadio del partitore x(-1,916) e partitore 18,2k / 1k (lato L)
Rin sh np 9.76k
Rfs np cvp 18.7k
Xst 0 np cvp vcc vee OPS
Rt cvp ecm 18.2k
Rb ecm 0 1k
*
* ---------------- VCA del fader, ADG con BBM, bus ----------------
Xvca in vout 0 ecm vcc vee THAT2181
* ADG: il DJ bus apre quando Q0 passa 2,5 V, il bus HPF chiude ~0,7 us dopo
Rqd q0 q0d 1k
Cqd q0d 0 1n
Sold vout bdj 0 q0 SWADGN
Snew vout bhp q0d 0 SWADG
Rdj bdj 0 10k
Rhp bhp 0 10k
* sonde click HP 2 poli ~1,6 kHz (come filtsel-dip.cir)
C1a bdj h1a 10n
R1a h1a 0 10k
C2a h1a hdj 10n
R2a hdj 0 10k
C1b bhp h1b 10n
R1b h1b 0 10k
C2b h1b hhp 10n
R2b hhp 0 10k
