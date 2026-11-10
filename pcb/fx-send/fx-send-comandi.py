"""FX-SEND, scheda comandi: i 3 pot doppi dietro il pannello (dec. 133, 135).

La scheda sta parallela al pannello e si regge sui dadi dei pot. Ogni albero cade sul foro
del render: la posizione viene da docs/pannelli/coordinate.json, modulo "fx-send". Un cavo
piatto corto (J1) la collega a J2 della scheda principale (fx-send.py, stesso ordine dei pin).

Pot: Alps RK09L doppio ad albero verticale, 10k (fx-send-module.md). Il LEVEL era di classe
14 mm (dec. 118): qui è un 9 mm, perché KiCad non ha l'impronta dell'RK14 e Filippo ha
lasciato libero il tipo di pot (2026-10-27). Il cappuccio del pannello non cambia.
Estremi: pin 1 = fine corsa antiorario, pin 3 = orario, pin 2 = cursore (verificato sul catalogo
Alps RK09L rev. 2510, disegni n. 7-8: NOTE.md punto 10). Sezione A (1-3) = lato L, sezione B (4-6) = lato R. Le staffe (MP) non hanno
rete: il corpo del pot va a massa telaio attraverso il dado sul pannello metallico.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from pcbgen import Design, boxsym
from cavo import CAVO

ROOT = os.path.join(HERE, "..", "..")
PANNELLO = json.load(open(os.path.join(ROOT, "docs", "pannelli", "coordinate.json")))["moduli"]["fx-send"]
MARGINE = (1.0, 2.0)            # la scheda è più piccola del pannello: 1 mm per lato, 2 sopra e sotto
W = PANNELLO["larghezza"] - 2 * MARGINE[0]
H = PANNELLO["altezza"] - 2 * MARGINE[1]

d = Design("fx-send-comandi", os.path.join(HERE, "comandi"), "maelcum FX-SEND scheda comandi - bozza v0.2",
           board=(W, H), rev="0.2-bozza")
d.gnd = "AGND"
d.power_nets("AGND", width=0.5)

POT = boxsym("POT_DUAL", [
    ("1", "A_CCW", "passive"), ("2", "A_W", "passive"), ("3", "A_CW", "passive"), ("MP", "MP", "passive")], [
    ("4", "B_CCW", "passive"), ("5", "B_W", "passive"), ("6", "B_CW", "passive")],
    ref="RV", fp="Potentiometer_THT:Potentiometer_Alps_RK09L_Double_Vertical",
    desc="Pot doppio, Alps RK09L verticale; MP = staffe, a massa telaio attraverso il pannello")
FP = "Potentiometer_THT:Potentiometer_Alps_RK09L_Double_Vertical"
ALBERO = (10.0, 2.5)            # albero dell'RK09L doppio, rispetto al pin 1 dell'impronta

# rete per sezione: (antiorario, cursore, orario)
RETI = {
    "EQ HIGH": (("VHN_L", "WPH_L", "VHP_L"), ("VHN_R", "WPH_R", "VHP_R"),
                "HIGH: tutto antiorario = kill (Rp1h = 0, fx-eq2.cir)"),
    "EQ LOW": (("NC_L", "NB_L", "NA_L"), ("NC_R", "NB_R", "NA_R"),
               "LOW Baxandall: tutto antiorario = kill (Za max), cursore = massa virtuale"),
    "LEVEL": (("AGND", "LVL_W_L", "VHI_L"), ("AGND", "LVL_W_R", "VHI_R"),
              "LEVEL: tutto antiorario = silenzio"),
}

d.block = "POT (posizioni dal render del pannello)"
for c in PANNELLO["comandi"]:
    if c["tipo"] != "manopola":
        continue
    a, b, nota = RETI[c["nome"]]
    pins = {"1": a[0], "2": a[1], "3": a[2], "4": b[0], "5": b[1], "6": b[2]}
    x, y = c["x"] - MARGINE[0], c["y"] - MARGINE[1]
    # i pin stanno 10 mm a sinistra dell'albero: nella colonna di sinistra il pot si gira,
    # così i pin vanno verso il centro e non sul bordo. Due pot sulla stessa riga (HIGH e LOW
    # affiancati, dec. 176): pin verso l'alto, nello spazio sotto il LEVEL.
    affiancato = any(o is not c and o["tipo"] == "manopola" and abs(o["y"] - c["y"]) < 1
                     for o in PANNELLO["comandi"])
    rot = 270 if affiancato else (180 if x < W / 2 else 0)
    d.part("RV", POT, "10k doppio", FP, pins, anchor=ALBERO, place=(x, y, rot),
           note="%s; manopola %s, cappuccio %s mm" % (nota, c["nome"], c["cappuccio"]))

d.block = "CAVO VERSO LA SCHEDA PRINCIPALE"
d.part("J", "Connector_Generic:Conn_02x12_Odd_Even", "2x12 cavo piatto",
       "Connector_PinHeader_2.54mm:PinHeader_2x12_P2.54mm_Vertical",
       {i + 1: n for i, n in enumerate(CAVO)}, ref="J1", place=(W / 2, H - 4.5, 90),
       note="stesso ordine di J2 su fx-send.py")

if __name__ == "__main__":
    d.build(route="--no-route" not in sys.argv)
