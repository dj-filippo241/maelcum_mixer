* =====================================================================
* THAT 218x (2180/2181, Blackmer SINGLE VCA) — macromodello comportamentale
* v0.1 (2026-09-27) — CONDIVISO: gate 5-way, matrice FX, VCA CDJ/master.
* Fonti: datasheet THAT 2181-Series (thatcorp.com) + product page:
*   - law: G(dB) = (V(ecp) − V(ecm)) / 6,1 mV   (±6,1 mV/dB, 164 dB/V)
*   - gain range: < −100 dB … > +40 dB (floor/ceiling nel modello: 1e-5/100)
*   - dynamic range > 120 dB; THD A/B/C: 0,0025/0,004/0,005 % typ
*   - 2181 = trimmabile (trim in-circuit obbligatorio per THD/feedthrough
*     garantiti); 2180 = pre-trimmato in wafer. SINGLE channel: il "dual"
*     del datasheet sono i due porti di controllo EC+/EC−.
* Modello: moltiplicatore ideale + polo 20 MHz (GBW datasheet) + clamp rail.
* ASSENTI (verifica a banco / beta-3): THD vs livello, rumore, feedthrough
* EC→audio (~−85…−100 dB dopo trim: è il floor reale del kill "silenzio"),
* impedenze IN/OUT reali (il chip è current-in/current-out: la applicazione
* circuitale completa di I/V sta nei design doc dei moduli).
* Uso: X<name> <in> <out> <ecp> <ecm> <vp> <vm> THAT2181
* =====================================================================
.subckt THAT2181 in out ecp ecm vp vm
Bg1 nout0 0 V={V(in)*limit(10**((V(ecp)-V(ecm))/0.122),1e-5,100)}
Rpol nout0 nout1 1k
Cpol nout1 0 8p
Eout out 0 value={limit(V(nout1),V(vm)+1.5,V(vp)-1.5)}
.ends THAT2181
