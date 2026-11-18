"""Genera MC-LICKSHOT (dec. 179-189): la lickshot in Live.

Uso:  python3 proto-max/coefficienti/genera_lickshot.py
Scrive in proto-max/: MC-LICKSHOT (.genexpr, .maxpat, .amxd).

Numeri e deduzioni in lickshot.py (modello di riferimento). La prova
prova_lickshot.py fa suonare il .genexpr tradotto in Python e lo confronta
campione per campione col modello.

Dispositivo audio: va su una traccia audio vuota, l'ingresso non si usa.
L'uscita (1,0 = fx.LIV volt, come il jack dei MONO) va a MC-MONO sulla
stessa traccia, oppure dritta al master. FIRE e un interruttore: un clic
accende, un clic spegne; da un controller si mappa su un CC (premi = 127,
lasci = 0). Una nota MIDI in Live fa da interruttore, non da tasto.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import fx  # noqa: E402
import lickshot as L  # noqa: E402
from genera import Codice  # noqa: E402
from genera_fx import Patch, lisci, scrivi  # noqa: E402

DIAL = [("alt", "ALTEZZA"), ("vel", "VELOCITA"), ("prof", "PROFONDITA"),
        ("vol", "VOLUME"), ("tempo", "TEMPO"), ("rip", "RIPETIZIONI"),
        ("eco", "LIVELLO ECO")]


def genexpr():
    g = Codice()
    r = g.r
    r("// MC-LICKSHOT - lickshot in rack (dec. 179-189), modello lickshot.py.")
    r("// GENERATO da proto-max/coefficienti/genera_lickshot.py: non modificare.")
    r("// LFO CD4069 a dente di sega -> VCO CD4046 -> passa-alto 145 Hz -> FIRE")
    r("// -> VOLUME -> eco a due BBD (anti-alias prima e dopo, nel giro passa-alto")
    r("// e saturazione). in1, in2 ignorati.")
    r(f"// out1 = out2 = uscita (1,0 = {fx.LIV:.4f} V); out3 = LED dell'LFO.")
    r()
    for nome, ini in L.INIZIALI.items():
        mx = 1 if nome == "trig" else 100
        r(f"Param {nome}({ini:g}, min=0, max={mx});")
    for nome in ("vi", "su", "fase", "hpx", "hpy", "gx", "gy",
                 "pi1", "pi2", "qi1", "qi2"):
        ini = L.VDD / 2 if nome == "vi" else 0
        r(f"History {nome}({ini!r});")
    r(f"History td({L.tempo_eco(L.INIZIALI['tempo']) * 48000!r});")
    r("Delay dl(48000);")
    lisci(r, ["alt", "vel", "prof", "vol", "tempo", "rip", "eco"], L.INIZIALI)
    r("// LFO: integratore fra le soglie del Schmitt, discesa lenta, risalita dal diodo")
    r(f"rl = {L.R_LFO!r} + (1 - s_vel / 100) * {L.P_LFO!r};")
    r(f"giu = {L.VDD / 2!r} / (rl * {L.C_LFO!r}) / samplerate;")
    r(f"sup = {(L.HI - L.LO) / L.T_SU!r} / samplerate;")
    r("vin = vi + su * sup - (1 - su) * giu;")
    r(f"hhi = su * (vin >= {L.HI!r});")
    r(f"hlo = (1 - su) * (vin <= {L.LO!r});")
    r(f"vi = min(max(vin, {L.LO!r}), {L.HI!r});")
    r("su = su * (1 - hhi) + hlo;")
    r("// PROFONDITA (dec. 190): pot fra la rampa e VDD/2, buffer verso il VCOin")
    r(f"vco = {L.VDD / 2!r} + s_prof / 100 * {L.A_MAX!r} * (vi - {L.VDD / 2!r}) / {(L.HI - L.LO) / 2!r};")
    r("// VCO: frequenza lineare col VCOin, f0 al centro (datasheet TI, Fig. 4)")
    r(f"r1 = {L.R_VCO!r} + (1 - s_alt / 100) * {L.P_VCO!r};")
    r(f"fz = {L.K_F0!r} / (r1 * {L.C_VCO!r});")
    r(f"fq = fz * max(0, vco - {L.VOFF!r}) / {L.VDD / 2 - L.VOFF!r};")
    r("dt = max(fq / samplerate, 1e-9);")
    r("// onda quadra con PolyBLEP")
    r("ta = fase / dt;")
    r("tc = (fase - 1) / dt;")
    r("xq = (fase < 0.5) * 2 - 1 + (fase < dt) * (ta + ta - ta * ta - 1)"
      " + (fase > 1 - dt) * (tc * tc + tc + tc + 1);")
    r("t2 = fase + 0.5 - (fase + 0.5 >= 1);")
    r("tb = t2 / dt;")
    r("te = (t2 - 1) / dt;")
    r("xq = xq - (t2 < dt) * (tb + tb - tb * tb - 1)"
      " - (t2 > 1 - dt) * (te * te + te + te + 1);")
    r("fase = fase + fq / samplerate;")
    r("fase = fase - (fase >= 1);")
    r(f"khp = 1 / (1 + {2 * 3.141592653589793 * L.F_HP_OUT!r} / samplerate);")
    r("hpy = khp * (hpy + xq - hpx);")
    r("hpx = xq;")
    r("vv = s_vol / 100;")
    r(f"dry = hpy * (trig > 0.5) * {L.V_NOM!r} * vv * vv;")
    r("// eco: due BBD in fila, tempo lisciato (fionda), anti-alias fclk/4")
    r(f"tm = {L.T_MIN!r} * pow({L.T_MAX / L.T_MIN!r}, s_tempo / 100);")
    r(f"td = td + (tm * samplerate - td) * (1 - exp(-1 / ({L.T_LISCIO!r} * samplerate)));")
    r(f"fcb = min({L.K_FC * L.N_BBD / 2!r} / (td / samplerate), {L.FC_MAX!r});")
    r("gb = tan(3.141592653589793 * fcb / samplerate);")
    r("a1 = 1 / (1 + gb * (gb + 1.4142135623730951));")
    r("a2 = gb * a1;")
    r("a3 = gb * a2;")
    r('rd = dl.read(td, interp="linear");')
    r("// anti-alias dopo i BBD")
    r("v3 = rd - qi2;")
    r("v1 = a1 * qi1 + a2 * v3;")
    r("post = qi2 + a2 * qi1 + a3 * v3;")
    r("qi1 = 2 * v1 - qi1;")
    r("qi2 = 2 * post - qi2;")
    r("// giro: passa-alto e saturazione")
    r(f"kg = 1 / (1 + {2 * 3.141592653589793 * L.F_HP_GIRO!r} / samplerate);")
    r("gy = kg * (gy + post - gx);")
    r("gx = post;")
    r(f"fb = {L.V_SAT!r} * tanh({L.G_MAX!r} * s_rip / 100 * gy / {L.V_SAT!r});")
    r("// anti-alias prima dei BBD")
    r("w3 = dry + fb - pi2;")
    r("w1 = a1 * pi1 + a2 * w3;")
    r("pre = pi2 + a2 * pi1 + a3 * w3;")
    r("pi1 = 2 * w1 - pi1;")
    r("pi2 = 2 * pre - pi2;")
    r("dl.write(pre);")
    r("ve = s_eco / 100;")
    r(f"out1 = (dry + ve * ve * post) / {fx.LIV!r};")
    r("out2 = out1;")
    r(f"out3 = min(max((vi - {L.V_LED!r}) / {L.HI - L.V_LED!r}, 0), 1);")
    return "\n".join(g.righe) + "\n"


def patch(codice):
    p = Patch()
    p.gen(codice, 3)
    for j, (ng, nl) in enumerate(DIAL[:4]):
        p.dial(ng, nl, L.INIZIALI[ng], [8 + 60 * j, 8, 54, 48])
    for j, (ng, nl) in enumerate(DIAL[4:]):
        p.dial(ng, nl, L.INIZIALI[ng], [8 + 60 * j, 70, 54, 48])
    p.tab("trig", "FIRE", ["-", "FIRE"], 0, [190, 78, 50, 36])
    p.meter("obj-led", 2, [246, 8, 8, 56], "LED")
    p.nota("FIRE: clic = acceso, clic = spento; da un controller mappalo su un "
           "CC. Uscita a livello del jack: mettila in MC-MONO.", [8, 124, 250, 40])
    return p.json()


def main():
    c = genexpr()
    scrivi("MC-LICKSHOT", patch(c), c)


if __name__ == "__main__":
    main()
