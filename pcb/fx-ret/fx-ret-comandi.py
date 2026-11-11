"""FX-RET, scheda comandi (todo 270): tutti i comandi della striscia di un ritorno FX.

La scheda sta parallela al pannello (61 x 229,85 mm) e lo copre tutto, meno 1 mm ai lati e 2
sopra e sotto: 59 x 225,85 mm. Si regge sui dadi dei pot. Posizioni da docs/pannelli/
coordinate.json, modulo "fx-ret" (dec. 176). Quattro moduli uguali (dec. 130): una scheda sola.

Un cavo, J2 2x18, verso J2 di fx-ret.py, stesso ordine (letto dal file: una fonte sola).

Reti dei comandi (da fx-ret.py, fx-ret-reroute.py e celle_vca.py):
- GAIN, pot doppio 10k lin selezionato, circuito T2 (dec. 162, fx-module §5): pot in
  retroazione, cursore GW a massa virtuale. Antiorario = O2A (retroazione zero = silenzio),
  orario = GA (dopo Ra 1,24k). Verso da sim/gain-pot/ritorno-buffer-g1.cir: xg = 0 -> Rt2b = 0.
- EQ HIGH, EQ LOW: pot doppi 10k, stesse reti del FX-SEND (EQ2, fx-send-comandi.py).
- SELF, > FX2, > FX3, > FX4: pot singoli 10k lin con scatto al centro, manopola rovescia
  (sistema-comandi.md: «cablati rovesci»): antiorario = +REF5, cursore POT_Rj, orario = AGND.
  La scheda è la stessa nei 4 moduli: il pot in posizione j (dall'alto) va a POT_Rj, cioè al
  bus Sj. Il pannello fa lo stesso (proposta_f.py: «SELF» nella posizione del bus del modulo,
  «> FXj» nelle altre); coordinate.json riporta il ritorno FX1.
- METER, 10 LED con un LM3915: MET dal superdiodo di fx-ret.py (g = 0,287), RHI = +REF5,
  come il canale (+24...-3 dBu).
- FADER, Bourns PTA4543 (corsa 45, dec. 169): in alto +REF5, cursore POT_F, in basso AGND.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from comandi import Comandi, fili_da

s = Comandi("fx-ret-comandi", os.path.join(HERE, "comandi"), "maelcum FX-RET scheda comandi - bozza v0.1", "fx-ret",
             riprova=True)   # 1 giro su 3 lasciava 14 aperti (2026-11-11)
d = s.d
d.power_nets("+5VF", "CTRL_GND", width=0.4)

EQ = {"EQ HIGH": (("VHN_L", "WPH_L", "VHP_L"), ("VHN_R", "WPH_R", "VHP_R"),
                  "EQ HIGH: tutto antiorario = kill (come il FX-SEND)"),
      "EQ LOW": (("NC_L", "NB_L", "NA_L"), ("NC_R", "NB_R", "NA_R"),
                 "EQ LOW Baxandall: tutto antiorario = kill, cursore = massa virtuale")}
CHIP = [(8.8, 190.0, 0)]   # NOTA: a sinistra della barra, sotto i reroute
J2 = (53.0, 70.0)
REROUTE = ["SELF", "> FX2", "> FX3", "> FX4"]

d.block = "POT: GAIN (doppio), EQ2 (doppi), REROUTE (singoli con scatto)"
for c in s.comandi("manopola"):
    if c["nome"] == "GAIN":
        s.pot2(c, ("O2A_L", "GW_L", "GA_L"), ("O2A_R", "GW_R", "GA_R"), "10k lin doppio selezionato",
               "GAIN T2 (dec. 162): antiorario = silenzio; pot selezionato per il tracking L/R")
    elif c["nome"] in EQ:
        a, b, nota = EQ[c["nome"]]
        s.pot2(c, a, b, "10k doppio", nota)
    else:
        j = REROUTE.index(c["nome"]) + 1
        s.pot(c, ("+REF5", "POT_R%d" % j, "AGND"), "10k lin, scatto al centro",
              "REROUTE %d verso il bus S%d (%s sul ritorno FX1, SELF sul ritorno FX%d); manopola rovescia: antiorario = +REF5"
              % (j, j, c["nome"], j))

d.block = "METER: un LM3915, 10 LED (+24...-3 dBu)"
for c in s.comandi("meter"):
    s.meter(c, "MET", ["+REF5"], piu="+5VF", meno="CTRL_GND", tag="R", chip=CHIP)

d.block = "FADER (PTA4543, corsa 45 mm, dec. 169)"
for c in s.comandi("fader"):
    s.fader(c, "+REF5", "POT_F", "AGND", nota="FADER: in cima = 0 dB, in fondo = silenzio")

d.block = "CAVO: J2 verso fx-ret.py (J2)"
s.cavo(fili_da(os.path.join(HERE, "fx-ret.py")), "J2", *J2, rot=0, nota="stesso ordine di J2 su fx-ret.py")
s.chiudi()

if __name__ == "__main__":
    if "--occupato" in sys.argv:
        for o in s.occupato: print("%-6s %6.1f %6.1f %6.1f %6.1f" % (o[4], *o[:4]))
        sys.exit()
    d.build(route="--no-route" not in sys.argv)
