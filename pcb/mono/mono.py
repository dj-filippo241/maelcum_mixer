"""MONO: modulo mono generico (dec. 97), scheda principale col C96. Bozza v0.1.

Catena (docs/fase4/mic-mono-moduli.md §2, §4, §5):
 JACK -> R serie 1k + clamp + TVS -> C 100n + bias 1M -> buffer FET 1 MOhm -> pot GAIN 10k A
      -> make-up +10 dB -> PRE (detector del LED) -> EQ2 -> POST
      -> driver MSUM7 L/R (invertenti, todo 227) + 4 mandate.

Polarità (sistema-polarita.md): buffer, make-up ed EQ2 non invertono -> POST +1; driver MSUM -1,
[A2] -1 -> +1 all'XLR del master. Niente VCA, niente MUTE (dec. 111: solo il MIC).

Pot e LED stanno sulla scheda comandi dietro il pannello (cavo J2, da disegnare: pcb/mono/NOTE.md).
Jack su un cavo a J3: la sua posizione sul pannello non è decisa.
Fonti: sim/mic/gen-ac.cir, sim/fx/fx-eq2-pot10k.cir, master-segnale.py.
Valori [PROVVISORIO]. Le scelte non scritte nei documenti sono segnate NOTA (pcb/mono/NOTE.md).
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from pcbgen import Design
import celle_micmono as cm
from celle_micmono import opa2, opa4, diode, C12

d = Design("mono", HERE, "maelcum MONO (dec. 97) - bozza v0.1", board=(100, 220), rev="0.1-bozza")
d.gnd = "AGND"

from cavo import CAVO as FILI     # ordine dei fili: cavo.py, letto anche dalla scheda comandi

d.block = "BACKPLANE C96 (classe MIC/GEN, MSUM7)"
cm.backplane(d, "MSUM7")

d.block = "ALIMENTAZIONE +-18 audio, +-15 switch, +5"
cm.power_18_sw(d)

d.block = "INGRESSO JACK TS: R serie, clamp, TVS, C film, bias 1M"
d.part("J", "Connector_Generic:Conn_01x02", "jack TS (cavo)", "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
       {1: "JTIP", 2: "AGND"}, ref="J3", place=(85, 5, 90),
       note="NOTA: cavo verso il jack TS; sleeve ad AGND del modulo (grounding §4)")
d.part("D", "Device:D_TVS", "TVS bidir. low-cap 24 V", "Diode_SMD:D_SOD-323", {1: "JTIP", 2: "AGND"},
       note="NOTA: tensione di lavoro sopra gli 8,7 Vp di +18 dBu")
d.R("JTIP", "MIN1", "1k 1%")
diode(d, "MIN1", "+18V", note="NOTA: clamp 1N4148W al posto del BAV199 (pinout non verificato)")
diode(d, "-18V", "MIN1")
d.C("MIN1", "MINC", "100n C0G", C12, note="film o C0G: polo 1,6 Hz col bias 1M")
d.R("MINC", "AGND", "1M 1%", note="Zin 1 MOhm")

d.block = "BUFFER, MAKE-UP +10 dB, DETECTOR del LED (OPA1654)"
d.R("PRE", "MKN", "2k15 0.1%")
d.R("MKN", "AGND", "1k 0.1%", note="G = 3,15 = +9,97 dB")
sd, sb = cm.detector(d, "PRE")
opa4(d, "U3", ("MINC", "BUF", "BUF"), ("GW", "MKN", "PRE"), sd, sb, "+18V", "-18V",
     note="buffer 1 MOhm, make-up (pot GAIN 10k A sul cavo: AGND-GW-BUF), superdiodo e buffer del LED")

d.block = "LED tricolore (LM339)"
cm.led3(d, "+18V", "165k")

d.block = "EQ2 (+-18)"
cm.eq2(d, "U4", "PRE", "POST")

d.block = "DRIVER MSUM7 L/R (invertenti, todo 227)"
cm.msum_drivers(d, "U8", "POST", "MSUM7")
d.block = "MANDATE S1-S4 (pot sul cavo, mute globale, iniezione)"
cm.sends(d, "U9", "U10")

d.block = "CAVO SCHEDA COMANDI (J2)"
cm.cavo(d, FILI)

d.audio_rules = {
    "sensibili": r"^(NB|NSH|NVH|NHB|MINC|MKN|GW|NDR_[LR]|INJ\d|S\d_OUT_[LR]|MSUM7_[LR])$",
    "cavo": r"^(NA|NB|NC|BUF|GW|VHN|WPH|VHP|SW\d)$",
    "rumorose": r"^(\+15SW|-15SW|SMUTE_N|MUTE_G|GLOBAL_MUTE|\+5VF?|LT|LQ|KR|KG|GFD|LK[RG]|V27F[+-]|VREG[+-]|BASE[+-]|RAW.*|CTRL_GND)$",
    "regolatori": ["U40", "U41", "U42", "U43", "Q40", "Q41"],
}

if __name__ == "__main__":
    d.build(route="--no-route" not in sys.argv)
