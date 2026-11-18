* Lickshot - stadi audio della scheda vera (pcb/lickshot/lickshot.py, bozza v0.1).
* Stessi nodi e valori del generatore: VDD 9 V singolo, TLC2272 del modello TI
* come macro TLC2272S (sim/lib/tlc2272s.inc, tarata sul modello TI SLOJ080B: il
* modello TI con 8 istanze non converge), VDD/2 da partitore + buffer.
* Comandi come parametri (posizione elettrica 0...1):
*   vol = VOLUME, rip = RIPETIZIONI, eco = LIVELLO ECO, tc = cursore del trimmer
*   di cancellazione del clock (0,5 = centro), ilg = guadagno d'inserzione di
*   un V3205D (datasheet: 0 dB tip., -4...+4 dB), td = ritardo di un BBD.
* BBD (non esiste un modello SPICE): ingresso ad alta impedenza, ritardo ideale,
* due uscite a source follower uguali (OUT1 e OUT2 ritardate di 4096 e 4097
* stadi: stesso segnale qui) con resistenza d'uscita {rbo}, deduzione mia.
* Il clock non e' modellato: niente residuo da cancellare.
* Il nodo fbx e' il capo della reazione verso la somma: nei .tran va unito a fb
* con Rlink, nei .ac si apre l'anello e si inietta li'.
.include ../lib/tlc2272s.inc

.subckt bbd in o1 o2 params: g=1 td=50m rbo=1k
Ei a 0 in 0 1
Rt1 a l1 50
T1 l1 0 l2 0 Z0=50 Td={td}
Rt2 l2 0 50
* uscita = ingresso ritardato x g, spostata di -1 V (source follower)
Eo b 0 value={2*g*V(l2) - 1}
Ro1 b o1 {rbo}
Ro2 b o2 {rbo}
.ends

* alimentazione e VDD/2 (U3A)
Vdd vdd 0 9
Rm1 vdd vmidr 10k
Rm2 vmidr 0 10k
Cm1 vmidr 0 10u
Xu3a vmidr vmid vdd 0 vmid TLC2272S

* colpo: uscita del VCO 0/9 V -> 100 nF film -> 110k -> invertente x0,173 (U4B):
* 0,78 V di plateau e passa-alto 14,5 Hz come prima. La scheda v0.1 aveva
* 10 uF -> partitore 1k/100 verso VMID -> 10k, x1,91: a ogni fronte del VCO
* (che gira sempre) +-4 mA nel buffer di VMID, VMID sobbalza di +-0,2 V e il
* disturbo entra nel giro anche a FIRE aperto (RISULTATI-scheda.md §3).
Chpa vcoout hpa 100n
Rgi hpa gn 110k
Rgf gn colpo 19.1k
Xu4b vmid gn vdd 0 colpo TLC2272S
* FIRE: tasto in serie, 100k verso VDD/2 a tasto aperto
* (resistenza comandata dal tempo: 0,05 ohm premuto, 1 Gohm aperto)
Rfs colpo fireout R=if(time<hold,0.05,1e9)
Rfire fireout vmid 100k
* VOLUME 10k fra VMID e FIREOUT, buffer U5A
Rvol1 fireout volw {10k*(1-vol)+1m}
Rvol2 volw vmid {10k*vol+1m}
Xu5a volw dry vdd 0 dry TLC2272S

* somma del giro (U5B) e attenuatore -14 dB
Rs1 dry sumn 10k
Rs2 fbx sumn 10k
Rs3 sumn sum 10k
Xu5b vmid sumn vdd 0 sum TLC2272S
Ra1 sum att 40.2k
Ra2 att vmid 10k

* BBD 1: 1 uF, polarizzazione da trimmer 10k su +5 V (cursore a 2,5 V: 2,5k), 100k
Cb1 att bbd1in 1u
Vb5 v5 0 5
Rbt1 v5 bias1 5k
Rbt2 bias1 0 5k
Cbs1 bias1 0 1u
Rbi1 bias1 bbd1in 100k
Xbbd1 bbd1in b1o1 b1o2 bbd g={ilg} td={td} rbo={rbo}
Rl11 b1o1 0 {rlb}
Rl12 b1o2 0 {rlb}
Rtc11 b1o1 bbd1out {10k*tc+1m}
Rtc12 bbd1out b1o2 {10k*(1-tc)+1m}
* BBD 2
Cb2 bbd1out bbd2in 1u
Rbt3 v5 bias2 5k
Rbt4 bias2 0 5k
Cbs2 bias2 0 1u
Rbi2 bias2 bbd2in 100k
Xbbd2 bbd2in b2o1 b2o2 bbd g={ilg} td={td} rbo={rbo}
Rl21 b2o1 0 {rlb}
Rl22 b2o2 0 {rlb}
Rtc21 b2o1 bbd2out {10k*tc+1m}
Rtc22 bbd2out b2o2 {10k*(1-tc)+1m}

* make-up invertente (U6A): scheda v0.1 rmk 10k, rmkf 49,9k; corretta rmk 47k,
* rmkf 100k + trimmer 500k (tarata a ~280k). Passa-alto 150 Hz e buffer (U6B)
Cmk bbd2out mkc 2.2u
Rmk1 mkc mkn {rmk}
Rmk2 mkn post {rmkf}
Xu6a vmid mkn vdd 0 post TLC2272S
Chp post hpn 100n
Rhp hpn vmid 10.7k
Xu6b hpn gy vdd 0 gy TLC2272S

* RIPETIZIONI 10k fra VMID e GY, 12,7k/10k, diodi, x2,5 (U7A)
Rrp1 gy ripw {10k*(1-rip)+1m}
Rrp2 ripw vmid {10k*rip+1m}
Rsat1 ripw satd 12.7k
Rsat2 satd vmid 10k
D1 satd vmid D1N4148
D2 vmid satd D1N4148
Rsg1 satn vmid 10k
Rsg2 satn fb 15k
Xu7a satd satn vdd 0 fb TLC2272S

* LIVELLO ECO 10k fra VMID e POST, mix invertente (U7B), uscita
Reco1 post ecow {10k*(1-eco)+1m}
Reco2 ecow vmid {10k*eco+1m}
Rx1 dry mxn 10k
Rx2 ecow mxn 10k
Rx3 mxn mix 10k
Xu7b vmid mxn vdd 0 mix TLC2272S
Ro mix outr 100
Co outr jout 10u
Rpd jout 0 100k
Rmono jout 0 1Meg

.model D1N4148 D(Is=2.52n Rs=0.568 N=1.752 Cjo=4p M=0.4 tt=20n)
* punto di lavoro: tutti gli stadi a VDD/2 (senza, il .op non converge)
.nodeset V(vmid)=4.5 V(vmidr)=4.5 V(dry)=4.5 V(volw)=4.5 V(sumn)=4.5 V(sum)=4.5 V(att)=4.5
+ V(mkn)=4.5 V(post)=4.5 V(hpn)=4.5 V(gy)=4.5 V(ripw)=4.5 V(satd)=4.5 V(satn)=4.5 V(fb)=4.5
+ V(mxn)=4.5 V(mix)=4.5 V(gn)=4.5 V(colpo)=4.5 V(bbd1in)=2.5 V(bbd2in)=2.5
