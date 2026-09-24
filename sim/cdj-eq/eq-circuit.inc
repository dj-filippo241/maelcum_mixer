* ============================================================
* CANALE CDJ — EQ 4 bande a celle di contribuzione bipolare
* Circuito condiviso dai test eq-ac / eq-noise / eq-levels
* Riferimento: docs/fase1/cdj-line-channel.md §3.3,
*              matematica validata in sim/eq_analysis.py
* ============================================================
* TOPOLOGIA PER BANDA (come §3.3, 10 sezioni op-amp totali):
*   filtro di banda -> due polarita' (+H e -H) -> pot 10k con
*   wiper al nodo di summing. Riferimento: V_in invertito (-1).
*   V(eq_out) = V_in * (1 - somma k'_i*H_i), k' = posizione wiper.
*   Convenzione del parametro a_i: a=0 -> KILL, a=0.5 -> detent,
*   a=1 -> BOOST +6,02 dB. (Nel cablaggio reale il pot si inverte
*   in modo che CW = boost, come da law bloccata.)
* FILTRI [PROVVISORIO — regola 3; centri EQ comunque PROVVISORI]:
*   LOW  70 Hz  Butterworth (Q 0,707): Sallen-Key LPF unity
*   LM   250 Hz Q 0,8: MFB bandpass (Elliott P63, C1=C2)
*   MH   1 kHz  Q 0,9: MFB bandpass
*   HIGH 5 kHz  Butterworth: Sallen-Key HPF unity
* OP-AMP: macromodelli lineari GBW-dominati con resistenza di
*   rumore equivalente (en^2 = 4kTR):
*   OPCELL = classe OPA1654 (GBW 20 MHz, ~6 nV/rtHz -> 2,2k)
*            [rumore DA VERIFICARE su datasheet]
*   OPSUM  = classe OPA1612 (GBW 80 MHz, 1,1 nV/rtHz -> 73R)
*   Rumore in corrente non modellato; THD non misurabile con
*   macromodello lineare (servono modelli TI reali).
* err = errore di matching dei percorsi +/-H (guadagno invertitore
*   di polarita' = 1+err): 0,002 = resistori 0,1%, 0,02 = 1%.

* ---------- Macromodelli op-amp ----------
.subckt OPCELL inp inn out vp vm Rn=2174
Rn1 inp inpi {Rn}
E1 x 0 value={1000*(V(inpi)-V(inn))}
R1 x p1 1k
C1 p1 0 7.96u
E2 y 0 p1 0 1000
R2 y p2 1k
C2 p2 0 31.8p
E3 out 0 value={limit(V(p2),V(vm)+1.5,V(vp)-1.5)}
.ends OPCELL

.subckt OPSUM inp inn out vp vm Rn=73
Rn1 inp inpi {Rn}
E1 x 0 value={1000*(V(inpi)-V(inn))}
R1 x p1 1k
C1 p1 0 1.99u
E2 y 0 p1 0 1000
R2 y p2 1k
C2 p2 0 3.98p
E3 out 0 value={limit(V(p2),V(vm)+1.5,V(vp)-1.5)}
.ends OPSUM

* ---------- Rail ----------
Vp18 vp18 0 DC 18
Vm18 vm18 0 DC -18

* ---------- Banda LOW: SK LPF 70 Hz (+H = lo_p) ----------
Rlo1 in nla 16k
Rlo2 nla nlb 16k
Clo1 nla lo_p 200n
Clo2 nlb 0 100n
Xlo nlb lo_p lo_p vp18 vm18 OPCELL
* invertitore di polarita' -> lo_n = -H (matching: err)
Rloi1 lo_p nloi {10k*(1-err/2)}
Rloi2 nloi lo_n {10k*(1+err/2)}
Xloi 0 nloi lo_n vp18 vm18 OPCELL

* ---------- Banda LOW-MID: MFB BPF 250 Hz Q0,8 (-H = lm_n) ----------
Rlm1 in nlma 5.11k
Rlm2 nlma 0 18.2k
Clm1 nlma nlmb 100n
Clm2 nlma lm_n 100n
Rlm3 lm_n nlmb 10.2k
Xlm 0 nlmb lm_n vp18 vm18 OPCELL
* invertitore -> lm_p = +H
Rlmi1 lm_n nlmi {10k*(1-err/2)}
Rlmi2 nlmi lm_p {10k*(1+err/2)}
Xlmi 0 nlmi lm_p vp18 vm18 OPCELL

* ---------- Banda MID-HIGH: MFB BPF 1 kHz Q0,9 (-H = mh_n) ----------
Rmh1 in nmha 4.32k
Rmh2 nmha 0 6.98k
Cmh1 nmha nmhb 33n
Cmh2 nmha mh_n 33n
Rmh3 mh_n nmhb 8.66k
Xmh 0 nmhb mh_n vp18 vm18 OPCELL
* invertitore -> mh_p = +H
Rmhi1 mh_n nmhi {10k*(1-err/2)}
Rmhi2 nmhi mh_p {10k*(1+err/2)}
Xmhi 0 nmhi mh_p vp18 vm18 OPCELL

* ---------- Banda HIGH: SK HPF 5 kHz (+H = hi_p) ----------
Chi1 in nha 10n
Chi2 nha nhb 10n
Rhi1 nha hi_p 4.7k
Rhi2 nhb 0 2.25k
Xhi nhb hi_p hi_p vp18 vm18 OPCELL
* invertitore -> hi_n = -H
Rhin1 hi_p nhi {10k*(1-err/2)}
Rhin2 nhi hi_n {10k*(1+err/2)}
Xhin 0 nhi hi_n vp18 vm18 OPCELL

* ---------- Riferimento: vref = -V_in (OPA1612) ----------
Rref1 in nref {10k*(1-err/2)}
Rref2 nref vref {10k*(1+err/2)}
Xref 0 nref vref vp18 vm18 OPSUM

* ---------- Pot di banda (10k) -> wiper -> summing ----------
* LOW: tra lo_p (+H) e lo_n (-H)
RpotL1 lo_p wl {aL*10k+1m}
RpotL2 lo_n wl {(1-aL)*10k+1m}
* LM: tra lm_p (+H) e lm_n (-H)
RpotLM1 lm_p wlm {aLM*10k+1m}
RpotLM2 lm_n wlm {(1-aLM)*10k+1m}
* MH: tra mh_p (+H) e mh_n (-H)
RpotMH1 mh_p wmh {aMH*10k+1m}
RpotMH2 mh_n wmh {(1-aMH)*10k+1m}
* HIGH: tra hi_p (+H) e hi_n (-H)
RpotH1 hi_p wh {aH*10k+1m}
RpotH2 hi_n wh {(1-aH)*10k+1m}

* ---------- Summing (OPA1612, Rf 10k) ----------
Rs1 wl ns 10k
Rs2 wlm ns 10k
Rs3 wmh ns 10k
Rs4 wh ns 10k
Rs5 vref ns 10k
Rsf ns eq_out 10k
Xsum 0 ns eq_out vp18 vm18 OPSUM
