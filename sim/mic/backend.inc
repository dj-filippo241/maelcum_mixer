* BACK-END comune MIC/GENERIC (mic-mono-moduli §5): nodo "pre" -> EQ2 al
* detent (celle serie scalate, valori fx-eq2.cir) -> driver L (R identico).
* Rail audio ±18 (vcc/vee).
RinL pre naL 1k
RzaL naL nbL 15.5k
CzaL naL nbL 56n
XopL 0 nbL v_lo vcc vee OP1654
RfL nbL ncL 1k
RzbL ncL v_lo 15.5k
CzbL ncL v_lo 56n
Ch1 v_lo nha 10n
Ch2 nha nhb 10n
Rh1 nha vhp 5.23k
Rh2 nhb 0 2.5k
X1h nhb vhp vhp vcc vee OP1654
Rh3 vhp nvh 10k
Rh4 nvh vhn 10k
X2h 0 nvh vhn vcc vee OP1654
Rp1h vhn wph 5k
Rp2h vhp wph 5k
Rah v_lo nsh 49.9k
Rbh wph nsh 49.9k
Rfh nsh v_hi 49.9k
X3h 0 nsh v_hi vcc vee OP1654
Xol v_hi ol ol vcc vee OP1612
Rol ol outl 47
Rload outl 0 20k
