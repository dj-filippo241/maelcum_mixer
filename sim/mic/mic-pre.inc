* MIC preamp v0.1 (mic-mono-moduli §3) — blocco comune ai test.
* Nodi: hot cold (dopo la sorgente) -> pre (uscita preamp, post stadio 2)
* Rail LN ±15 (vcl/vel). Valori [PROVVISORIO — regola 3].
* Rete d'ingresso: R serie 10 (limitazione clamp/RFI), carico differenziale
* 2,32k + bias 2x47k = Zin diff 2,26k, Z modo comune 47k per gamba.
Rsh hot ih 10
Rsc cold ic 10
Rld ih ic 2.32k
Rbsh ih 0 47k
Rbsc ic 0 {47k*(1+bal)}
* INA: coppia OP1612, Rf 499, Rg 32,4 -> G1 = 1+998/32,4 = 31,8 (30,05 dB) FISSO
X1 ih f1 o1 vcl vel OP1612
X2 ic f2 o2 vcl vel OP1612
Rf1 o1 f1 499
Rf2 o2 f2 499
Rg f1 f2 32.4
* differenziale unity 4x1k 0,1% (mis = sbilanciamento worst di UNA R)
Rd1 o1 dn 1k
Rd2 dn s1 {1k*(1+mis)}
Rd3 o2 dp 1k
Rd4 dp 0 1k
X3 dp dn s1 vcl vel OP1612
* HPF Sallen-Key 2 ordine ~60 Hz Butterworth (RATIFICATO dec. 97;
* R_fb = R_gnd/2: fix 2026-09-25). Toglie anche l'offset dell'INA.
Ck1 s1 k1 220n
Ck2 k1 k2 220n
Rk1 k1 hp 8.45k
Rk2 k2 0 16.9k
X4 k2 hp hp vcl vel OP1654
* stadio 2: guadagno variabile 0...+30 dB, pot lineare 5k col cursore al
* nodo invertente: G = -(R2 + x*P)/(R1 + (1-x)*P)
R1a hp p1 332
Rpa p1 inv {5k*(1-gp)+1m}
Rpb inv p2 {5k*gp+1m}
R2a p2 pre 5.36k
Cf2 inv pre 22p
X5 0 inv pre vcl vel OP1654
