* TLC2272S - macro semplice del TLC2272 (TI SLOS190H), tarata sul modello TI
* SLOJ080B (sim/lib/tlc2272.lib) in sim/lickshot/tlc-taratura.cir (2026-11-18).
* Serve perche' il modello TI, con 7-8 istanze nello stesso circuito, non trova
* il punto di lavoro in LTspice 26.0.2 (lickshot, scheda.inc).
* A0 1e5, polo a 22 Hz: GBW 2,2 MHz (datasheet 2,18 MHz a 5 V).
* Slew rate 3,6 V/us (corrente dell'integratore limitata a 2,6 uA su 0,723 pF).
* Uscita fermata 30 mV dentro i rail + 200 ohm (banco: invertente x2, 10k verso
* VDD/2, 9 V): risultati in sim/lickshot/RISULTATI-scheda.md §1.
* Anti-windup: il nodo del polo non esce oltre 0,2 V dai rail.
* Non modellati: rumore, offset, limite di modo comune (TI: VDD+ - 1 V; il
* datasheet raccomanda VDD+ - 1,5 V): si controlla a parte sui nodi.
.subckt TLC2272S inp inn vp vm out
G1 0 p value={limit(1e-5*V(inp,inn),-2.6u,2.6u)}
R1 p 0 1e10
C1 p 0 0.723p
G2 p 0 value={if(V(p)>V(vp)+0.2,(V(p)-V(vp)-0.2)*1e-3,if(V(p)<V(vm)-0.2,(V(p)-V(vm)+0.2)*1e-3,0))}
E2 o 0 value={limit(V(p),V(vm)+0.03,V(vp)-0.03)}
Ro o out 200
.ends
