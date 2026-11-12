"""Pinout del backplane C96 (DIN 41612 C 3x32): una tabella sola per tutti i moduli.

Fonte: docs/fase3/sistema-backplane.md §3 (riga a, potenza), §4 (riga b, audio, per classe),
§5 (riga c, controllo). Righe a e c hanno la stessa mappa in tutte le classi: un modulo
sceglie solo quali pin usa. La riga b la scrive il modulo, perché cambia per classe.

Uso nel netlist di un modulo:
    from backplane import c96, FP_C96, SYM_C96
    pins = c96(b={"b1": "SEND_IN_L", ...}, c=["c9"])
I pin non elencati restano senza rete (pin liberi del connettore).
"""

SYM_C96 = "Connector:DIN41612_03x32_C_Split"
FP_C96 = "Connector_DIN:DIN41612_C_3x32_Male_Horizontal_THT"

# Distanza fra il bordo della scheda di modulo e il centro dei pad del C96 (place = centro dei
# pad = fila b). Harting 09 03 196 6921 (catalogo DIN Signal p. 01.21) e la riga "Board edge"
# dell'impronta KiCad: fori della fila a a 5,3 mm dal bordo; fila b 2,54 mm più dentro. Prima
# era 6,5 (fila a a 3,96: la scheda andava sotto il labbro del corpo, todo 303).
C96_DAL_BORDO = 5.3 + 2.54        # 7,84 mm: place=(x, H - C96_DAL_BORDO, 180)

# §3: riga a, identica per tutte le classi
RIGA_A = {}
for _i in (1, 2): RIGA_A["a%d" % _i] = "RAW+27"
for _i in (3, 4): RIGA_A["a%d" % _i] = "RAW-27"
for _i in (5, 6): RIGA_A["a%d" % _i] = "RAW+22"
for _i in (7, 8): RIGA_A["a%d" % _i] = "RAW-22"
for _i in (9, 10): RIGA_A["a%d" % _i] = "RAW+26"      # solo il master li popola
for _i in (11, 12): RIGA_A["a%d" % _i] = "RAW-26"
for _i in range(13, 21): RIGA_A["a%d" % _i] = "AGND"
for _i in (21, 22): RIGA_A["a%d" % _i] = "+5V"
for _i in (23, 24): RIGA_A["a%d" % _i] = "CTRL_GND"
for _i in (25, 26): RIGA_A["a%d" % _i] = "CHASSIS"

# §5: riga c, identica per tutte le classi
RIGA_C = {}
for _i in range(1, 5):
    RIGA_C["c%d" % (2 * _i - 1)] = "FILT_MODE%d_0" % _i
    RIGA_C["c%d" % (2 * _i)] = "FILT_MODE%d_1" % _i
RIGA_C["c9"] = "GLOBAL_MUTE"
for _i in range(10, 14): RIGA_C["c%d" % _i] = "CV%d" % (_i - 9)
RIGA_C["c14"] = "LED_DIM"
RIGA_C["c15"] = "SVC"
# AC_OK (open collector dal box, alto = rete presente; psu-esterno §2.5) va dal PSU-IN al
# mute controller del master. Pin libero scelto il 2026-10-28 (pcb/master/NOTE.md): c17.
RIGA_C["c17"] = "AC_OK"
for _i in (16, 20, 24, 28): RIGA_C["c%d" % _i] = "CTRL_GND"

# pin di riga a che ogni modulo collega (il master aggiunge a9-a12)
A_STANDARD = [k for k in RIGA_A if k not in ("a9", "a10", "a11", "a12")]
C_RITORNI = ["c16", "c20", "c24", "c28"]


def c96(b, a=None, c=()):
    """Mappa pin -> rete del C96 per un modulo.

    b: dict della riga b (classe del modulo, §4).
    a: pin di riga a usati (default: tutti tranne i ±26 V del master).
    c: pin di riga c usati oltre ai ritorni CTRL_GND (es. ["c9"]).
    """
    pins = {k: RIGA_A[k] for k in (a if a is not None else A_STANDARD)}
    for k in b:
        if not k.startswith("b"):
            raise ValueError("c96: %s non è un pin di riga b" % k)
    pins.update(b)
    for k in list(c) + C_RITORNI:
        pins[k] = RIGA_C[k]
    return pins
