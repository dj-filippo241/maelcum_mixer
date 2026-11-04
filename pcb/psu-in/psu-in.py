"""PSU-IN: modulo d'ingresso dell'alimentatore esterno (dec. 113), slot PSU del backplane. Bozza v0.1.

Fonte: docs/fase3/sistema-psu-esterno.md §1, §3, §4 (ingresso, stella, fusibili, supervisor,
termostato), sistema-backplane.md REV dec. 113 (i pin «raw ±27 AUDIO» portano ±22,0 V
pre-regolati, i «raw ±22 LN» ±19 V, [M] resta raw ±27 su a9-a12, +5 invariato) e §3,
sistema-grounding.md §2 (stella, bond unici AGND-CTRL_GND e CHASSIS-AGND).

Per ogni rail: fusibile di gruppo 5x20, TVS verso il suo 0 V, Schottky inverso, bulk locale.
Ogni 0 V del cavo resta una rete sua fino alla stella (0 ohm verso AGND, un punto solo).
Il driver delle ventole (§4.5) non ha ancora un circuito: qui solo il fusibile e il connettore.
Valori [PROVVISORIO]. Le scelte non scritte nei documenti sono segnate NOTA (pcb/psu-in/NOTE.md).
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from pcbgen import Design
from backplane import c96, SYM_C96, FP_C96, RIGA_A

d = Design("psu-in", HERE, "maelcum PSU-IN (dec. 113) - bozza v0.1", board=(100, 220), rev="0.1-bozza")
d.gnd = "AGND"
d.inner_signal = True     # In2 strato di piste: le reti di potenza larghe passano sotto il C96
FUSE = "Fuse:Fuseholder_Clip-5x20mm_Littelfuse_111_Inline_P20.00x5.00mm_D1.05mm_Horizontal"
SMB = "Diode_SMD:D_SMB"
SMC = "Diode_SMD:D_SMC"

# ------------------------------------------------------------ backplane
d.block = "BACKPLANE C96 (slot PSU-IN): riga a intera, AC_OK su c17"
d.power_nets("RAW+27", "RAW-27", "RAW+22", "RAW-22", "RAW+26", "RAW-26", "+5V", "AGND", "CTRL_GND", "CHASSIS",
             "C+22", "C-22", "C+19", "C-19", "C+27", "C-27", "C+5", "VFAN", "VFAN_F",
             "0V_A", "0V_LN", "0V_M", "0V_FAN", width=0.8)
d.part("J", SYM_C96, "C96 maschio", FP_C96, c96({}, a=list(RIGA_A), c=["c17"]), ref="J1", place=(50, 213.5, 180),
       note="DIN 41612 C 3x32, angolo retto; riga a intera, compresi i [M] a9-a12")
for ref, x in (("H1", 5), ("H2", 95)):
    d.part("H", "Mechanical:MountingHole_Pad", "CHASSIS", "MountingHole:MountingHole_3.2mm_M3_Pad",
           {1: "CHASSIS"}, ref=ref, place=(x, 5, 0), note="foro di fissaggio, a CHASSIS")

# ------------------------------------------------------------ cavo dal box
d.block = "CAVO DAL BOX (20 conduttori, §3)"
CAVO = ["C+22", "C+22", "C-22", "C-22", "0V_A", "0V_A", "C+19", "C-19", "0V_LN", "C+27", "C-27", "0V_M",
        "C+5", "C+5", "CTRL_GND", "CTRL_GND", "VFAN", "0V_FAN", "AC_OK", None, None, None, None, None]
d.part("J", "Connector_Generic:Conn_02x12_Odd_Even", "Mini-Fit Jr 2x12", "Connector_Molex:Molex_Mini-Fit_Jr_5566-24A2_2x12_P4.20mm_Vertical",
       {i + 1: n for i, n in enumerate(CAVO) if n}, ref="J2", place=(50, 12, 0),
       note="NOTA: cavo interno dal connettore circolare del pannello posteriore (>= 5 A per contatto, §3)")


# ------------------------------------------------------------ rail
def rail(cin, out, zero, fuse, tvs, schottky, bulk, bulk_fp, neg=False, nota=""):
    """Fusibile di gruppo, poi TVS e Schottky inverso verso il proprio 0 V, poi bulk (§4.1).
    NOTA: il fusibile sta PRIMA del TVS: così la corrente del TVS (LDO del box in corto) lo apre."""
    d.part("F", "Device:Fuse", fuse, FUSE, {1: cin, 2: out}, note="fusibile di gruppo 5x20 (§4.3)" + nota)
    if neg:
        d.part("D", "Device:D_TVS", tvs, SMB, {1: zero, 2: out}, note="TVS verso il suo 0 V (§4.1)")
        d.part("D", "Device:D", schottky, SMC, {"K": zero, "A": out}, note="Schottky inverso")
        d.CP(zero, out, bulk, bulk_fp)
    else:
        d.part("D", "Device:D_TVS", tvs, SMB, {1: out, 2: zero}, note="TVS verso il suo 0 V (§4.1)")
        d.part("D", "Device:D", schottky, SMC, {"K": out, "A": zero}, note="Schottky inverso")
        d.CP(out, zero, bulk, bulk_fp)


D18 = "Capacitor_THT:CP_Radial_D18.0mm_P7.50mm"
D12 = "Capacitor_THT:CP_Radial_D12.5mm_P5.00mm"
d.block = "RAIL AUDIO +-22,0 V (pin raw +-27): T2,5 A, TVS 26 V, 2,2 mF"
rail("C+22", "RAW+27", "0V_A", "T2.5A", "SMBJ26A", "SS54", "2200u 35V", D18)
rail("C-22", "RAW-27", "0V_A", "T2.5A", "SMBJ26A", "SS54", "2200u 35V", D18, neg=True)
d.block = "RAIL LN +-19 V (pin raw +-22): T1 A, TVS 22 V, 1 mF"
rail("C+19", "RAW+22", "0V_LN", "T1A", "SMBJ22A", "SS54", "1000u 35V", D12)
rail("C-19", "RAW-22", "0V_LN", "T1A", "SMBJ22A", "SS54", "1000u 35V", D12, neg=True)
d.block = "RAIL [M] raw +-27 V (pin raw +-26): T500 mA, TVS 33 V, 1 mF"
rail("C+27", "RAW+26", "0V_M", "T500mA", "SMBJ33A", "SS54", "1000u 63V", D12,
     nota="; NOTA: 63 V per il clamp del TVS a 33 V di standoff")
rail("C-27", "RAW-26", "0V_M", "T500mA", "SMBJ33A", "SS54", "1000u 63V", D12, neg=True)
d.block = "RAIL +5 V: T2 A, TVS 5,0 V, 1 mF"
rail("C+5", "+5V", "CTRL_GND", "T2A", "SMBJ5.0A", "SS54", "1000u 10V", D12)
d.block = "V_FAN (T500 mA) e AC_OK"
d.part("F", "Device:Fuse", "T500mA", FUSE, {1: "VFAN", 2: "VFAN_F"}, note="fusibile delle ventole (§4.3)")
d.part("J", "Connector_Generic:Conn_01x03", "1x3 driver ventole", "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical",
       {1: "VFAN_F", 2: "0V_FAN", 3: "AGND"}, ref="J3", place=(88, 60, 90),
       note="NOTA: verso il driver lineare delle ventole (§4.5), circuito da progettare")
d.R("+5V", "AC_OK", "10k", note="NOTA: pull-up dell'open collector AC_OK (§2.5)")

# ------------------------------------------------------------ stella
d.block = "STELLA analogue-0V (§4.2, grounding §2)"
for z in ("0V_A", "0V_LN", "0V_M", "0V_FAN"):
    d.R(z, "AGND", "0", "Resistor_SMD:R_2512_6332Metric", note="NOTA: ponte di stella (0 ohm 2512): un 0 V per conduttore")
d.R("CTRL_GND", "AGND", "0", "Resistor_SMD:R_2512_6332Metric", note="UNICO bond AGND-CTRL_GND (grounding §2)")
d.part("J", "Connector_Generic:Conn_01x02", "bond CHASSIS-AGND", "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
       {1: "CHASSIS", 2: "AGND"}, ref="JB1", note="UNICO bond CHASSIS-AGND, removibile per la diagnosi del ronzio (grounding §2)")

d.audio_rules = {"sensibili": r"^$", "cavo": r"^$", "rumorose": r"^$", "regolatori": []}

if __name__ == "__main__":
    d.build(route="--no-route" not in sys.argv)
