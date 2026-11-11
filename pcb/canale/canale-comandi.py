"""CANALE CDJ/LINE, scheda comandi (todo 270): tutti i comandi della striscia del canale.

La scheda sta parallela al pannello (50 x 266,4 mm) e lo copre tutto, meno 1 mm ai lati e 2
sopra e sotto: 48 x 262,4 mm. Si regge sui dadi dei pot. Posizioni da docs/pannelli/
coordinate.json, modulo "canale" (dec. 176). Il FX-SEND sopra ha la sua scheda comandi.

Due cavi:
- J2, 2x18: verso J2 di canale.py, stesso ordine (letto dal file: una fonte sola).
- J3, 1x6: i bottoni FX1-4 verso J3 di fx-send.py (+5VF, BTN1-4, CTRL_GND), stesso ordine.
  NOTA: alimentazione e massa dei bottoni FX hanno reti proprie (+5VF_FXS, GND_FXS): il +5VF
  del canale e quello del FX-SEND non si toccano, e il cavo non chiude un anello di masse.

Reti dei comandi (da canale.py e banca.py):
- GAIN, pot doppio 10k lin (T1, dec. 162): antiorario = AGND, cursore = GW, orario = BUF.
  Sezione A = L, B = R. Scatto al centro sul pannello (coordinate.json).
- HIGH, MID-HIGH, LOW-MID, LOW: pot doppi lineari B 10k (dec. 168): banda -> cursore KnW ->
  massa. Antiorario = AGND (kill), orario = uscita della banda. K1 = LOW (LOO), K2 = LOW-MID
  (LMO), K3 = MID-HIGH (MHO), K4 = HIGH (HIO). Niente contatto di fondo corsa (dec. 127).
- FILTRO, levetta HPF/OFF/LPF: comune a CTRL_GND; HPF tira FSW0 giù, LPF tira FSW1 giù, OFF
  nessuno (canale.py: pull-up 10k, 74HC14 inverte, Q0 = HPF, Q1 = LPF).
- CUE, bottone a ritenuta: +5VF su BTNC (canale.py: «tasto CUE a ritenuta verso +5VF»).
- FX1-4, bottoni a ritenuta: +5VF_FXS su BTN1-4 (fx-send.py, assign).
- METER, 10 LED con un LM3915: MET dal superdiodo di canale.py (g = 0,287), RHI = +REF5
  (5,000 V): +24...-3 dBu, come le zone di sistema-metering.md §3. NOTA: il partitore interno
  dell'LM3915 carica il +REF5 dei pot; il master usa un follower dedicato (VREFA).
- FADER, Bourns PTA6043: in alto +REF5, cursore POT_F, in basso AGND (shaper-fader.cir: Vx
  da 0 a 5 V, fader in cima = 0 dB).
- LINE/PHONO: levetta senza reti. Il front-end PHONO è una variante di Rev B e non sta su
  canale.py (NOTE.md punto 8): la levetta si monta, i fili arriveranno con la Rev B.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from comandi import Comandi, fili_da

s = Comandi("canale-comandi", os.path.join(HERE, "comandi"), "maelcum CANALE scheda comandi - bozza v0.1", "canale")
d = s.d
d.power_nets("+5VF", "CTRL_GND", width=0.4)

ISO = {"LOW": ("LOO", "K1W"), "LOW-MID": ("LMO", "K2W"), "MID-HIGH": ("MHO", "K3W"), "HIGH": ("HIO", "K4W")}

d.block = "POT: GAIN e ISOLATOR (pot doppi, sezione A = L, B = R)"
for c in s.comandi("manopola"):
    if c["nome"] == "GAIN":
        s.pot2(c, ("AGND", "GW_L", "BUF_L"), ("AGND", "GW_R", "BUF_R"), "10k lin doppio selezionato",
               "GAIN T1 (dec. 162): antiorario = silenzio; pot selezionato per il tracking L/R")
    else:
        banda, w = ISO[c["nome"]]
        s.pot2(c, ("AGND", w + "_L", banda + "_L"), ("AGND", w + "_R", banda + "_R"), "10k lin B doppio",
               "ISOLATOR %s (dec. 168): antiorario = kill, orario = banda piena" % c["nome"])

d.block = "LEVETTE: FILTRO (HPF/OFF/LPF) e LINE/PHONO"
for c in s.comandi("levetta"):
    if c["nome"] == "FILTRO":
        s.levetta(c, "FSW0", "CTRL_GND", "FSW1", nota="HPF = FSW0 a massa, OFF = nessuno, LPF = FSW1 a massa (dec. 163)")
    else:
        s.levetta(c, None, None, None, nota="LINE/PHONO senza reti: il PHONO arriva con la Rev B (NOTE.md punto 8)")

d.block = "BOTTONI: FX1-4 (assign verso il FX-SEND) e CUE"
for c in s.comandi("bottone"):
    if c["nome"] == "CUE":
        s.bottone(c, "+5VF", "BTNC", luce=(None, "CTRL_GND", "+5VF"), rluce="1k5",
                  nota="CUE: chiuso = +5VF su BTNC; luce ~2 mA dal secondo contatto")
    else:
        k = int(c["nome"][2:])
        s.bottone(c, "+5VF_FXS", "BTN%d" % k, luce=(None, "GND_FXS", "+5VF_FXS"), rluce="1k5",
                  nota="%s: chiuso = +5VF del FX-SEND su BTN%d; luce dal secondo contatto" % (c["nome"], k))

d.block = "METER: un LM3915, 10 LED (+24...-3 dBu)"
for c in s.comandi("meter"):
    s.meter(c, "MET", ["+REF5"], piu="+5VF", meno="CTRL_GND", tag="C",
            chip=[(42.0, 243.0, 0)])   # NOTA: chip a destra del fader, sotto il cavo J2

d.block = "FADER (PTA6043, corsa 60 mm, dec. 169)"
for c in s.comandi("fader"):
    s.fader(c, "+REF5", "POT_F", "AGND", nota="FADER: in cima = 0 dB (Vx = 5 V), in fondo = silenzio")

d.block = "CAVI: J2 verso canale.py (J2), J3 verso fx-send.py (J3)"
s.cavo(fili_da(os.path.join(HERE, "canale.py")), "J2", 42.5, 203.0, rot=0,
       nota="stesso ordine di J2 su canale.py")
s.fila(["+5VF_FXS", "BTN1", "BTN2", "BTN3", "BTN4", "GND_FXS"], "J3", 44.0, 165.0, rot=0,
       nota="stesso ordine di J3 su fx-send.py: +5VF, BTN1-4, CTRL_GND (bottoni assign, dec. 133)")
s.chiudi()

if __name__ == "__main__":
    d.build(route="--no-route" not in sys.argv)
