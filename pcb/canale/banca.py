"""Isolator incroci C del CANALE (dec. 152, iso-incc-banca.inc, RISULTATI-incroci-C §1) e ponte
fra le due schede del canale (todo 167, divisione PROVVISORIA, pcb/canale/NOTE.md).

Le funzioni sono quelle di canale.py v0.1, spostate qui senza cambiare valori né reti: la
banca dei due lati, la somma non invertente x10 e il servo DC stanno sulla scheda isolator
(canale-isolator.py), che non ha C96.

Ponte: cavo piatto 2x18, stesso ordine dei pin sulle due schede (J4 di canale.py, J1 di
canale-isolator.py). Viaggiano ±18, GO (uscita del GAIN), EQ (uscita della somma) e le 16 reti
dei pot B dell'isolator, che proseguono sul cavo dei pot J2 della scheda segnale.
"""
from celle_vca import opa2, opa4, C12

C10 = "Capacitor_SMD:C_1210_3225Metric"
POT_L = ["LOO_L", "K1W_L", "LMO_L", "K2W_L", "MHO_L", "K3W_L", "HIO_L", "K4W_L"]
POT_R = [n.replace("_L", "_R") for n in POT_L]
PONTE = ["+18V", "+18V", "AGND", "AGND", "-18V", "-18V", "AGND", "AGND",
         "GO_L", "GO_R", "AGND", "AGND", "EQ_L", "EQ_R", "AGND", "AGND"] + POT_L + ["AGND", "AGND"] + POT_R + ["AGND", "AGND"]


def ponte(d, ref, place, note):
    d.part("J", "Connector_Generic:Conn_02x18_Odd_Even", "2x18 ponte isolator",
           "Connector_PinHeader_2.54mm:PinHeader_2x18_P2.54mm_Vertical",
           {i + 1: n for i, n in enumerate(PONTE)}, ref=ref, place=place, note=note)


def banca(d):
    """Le due banche, la somma e il servo: come canale.py v0.1 (riferimenti U3-U14 invariati)."""
    def ap2(s, tag, vin, vout, c, c2x, r1, r2, rf):
        """Allpass del 2o ordine (MFB passa-banda + sommatore), uscita = -AP (iso-incc-banca.inc)."""
        n, m, bp, sm = [x + tag + s for x in ("APN", "APM", "APB", "APS")]
        d.R(vin, n, r1 + " 0.1%")
        d.R(n, "AGND", r2 + " 0.1%")
        d.C(n, m, c2x, C10 if "n" not in c2x or float(c2x.split("n")[0]) > 50 else C12,
            note="NOTA: 2C, coppia in parallelo da fissare col layout (RISULTATI-incroci-C §1)")
        d.R(m, bp, rf + " 0.1%")
        d.C(n, bp, c, C10 if c.startswith("47n") else C12)
        d.R(vin, sm, "10k 0.1%")
        d.R(bp, sm, "4k99 0.1%", note="sim 5k: E96 4,99k")
        d.R(sm, vout, "10k 0.1%")
        return [("AGND", m, bp), ("AGND", sm, vout)]


    def sk(s, tag, vin, vout, hp, r, rg, cfb, cg, cval):
        """Sallen-Key unity. hp: C in serie (cval), R verso l'uscita (r) e verso massa (rg).
        lp: R in serie (r), C verso l'uscita (cfb) e verso massa (cg)."""
        a, bq = "SKA" + tag + s, "SKB" + tag + s
        fp = lambda v: C10 if v.endswith("n") and float(v[:-1].replace("n", "")) >= 47 else C12
        if hp:
            d.C(vin, a, cval + " C0G", fp(cval))
            d.C(a, bq, cval + " C0G", fp(cval))
            d.R(a, vout, r + " 0.1%")
            d.R(bq, "AGND", rg + " 0.1%")
        else:
            d.R(vin, a, r + " 0.1%")
            d.R(a, bq, r + " 0.1%")
            d.C(a, vout, cfb + " C0G", fp(cfb),
                note="NOTA: coppia in parallelo da fissare col layout" if cfb in ("200n", "20n") else "")
            d.C(bq, "AGND", cg + " C0G", fp(cg))
        return [(bq, vout, vout)]


    def isolator(s, vin, vout, uq, usum):
        secs = []
        # spina HP: HP2(150, Q 0,5) SK | HP4(350) SK SK | HP4(3150) MFB + SK
        secs += sk(s, "H1", vin, "R1" + s, True, "4k81", "4k81", None, None, "220n")
        secs += sk(s, "H2", "R1" + s, "R2A" + s, True, "3k20", "6k42", None, None, "100n")
        secs += sk(s, "G2", "R2A" + s, "R2" + s, True, "3k20", "6k42", None, None, "100n")
        x, nn = "MHX" + s, "MHN" + s
        d.C("R2" + s, x, "10n C0G", C12)
        d.C(x, "R3A" + s, "10n C0G", C12)
        d.C(x, nn, "10n C0G", C12)
        d.R(x, "AGND", "2k37 0.1%", note="calcolo 2,38k")
        d.R(nn, "R3A" + s, "10k7 0.1%")
        secs += [("AGND", nn, "R3A" + s)]
        secs += sk(s, "H3B", "R3A" + s, "HIO" + s, True, "3k57", "7k15", None, None, "10n")
        # LOW: LP2(150) SK Q 0,5 + AP2(350) + AP2(3150)
        secs += sk(s, "A1", vin, "LA" + s, False, "4k81", None, "220n", "220n", None)
        secs += ap2(s, "P1", "LA" + s, "LB" + s, "47n C0G", "94n C0G", "6k81", "13k7", "10k2")
        secs += ap2(s, "P2", "LB" + s, "LOO" + s, "4n7 C0G", "9n4 C0G", "7k59", "15k2", "11k4")
        # LOW-MID: LP4(350) SK SK + AP2(3150)
        secs += sk(s, "B1", "R1" + s, "MA" + s, False, "3k20", None, "200n", "100n", None)
        secs += sk(s, "B2", "MA" + s, "MB" + s, False, "3k20", None, "200n", "100n", None)
        secs += ap2(s, "P3", "MB" + s, "LMO" + s, "4n7 C0G", "9n4 C0G", "7k59", "15k2", "11k4")
        # MID-HIGH: LP4(3150) MFB (tre R uguali, C a massa 4,5 C) + SK
        x, nn = "MCX" + s, "MCN" + s
        d.R("R2" + s, x, "5k05 0.1%", note="calcolo 5,07k")
        d.R(x, "HA" + s, "5k05 0.1%")
        d.R(x, nn, "5k05 0.1%")
        d.C(x, "AGND", "21n15 C0G", C12, note="NOTA: 4,5 x 4,7n, coppia in parallelo da fissare col layout")
        d.C(nn, "HA" + s, "4n7 C0G", C12)
        secs += [("AGND", nn, "HA" + s)]
        secs += sk(s, "C2", "HA" + s, "MHO" + s, False, "3k57", None, "20n", "10n", None)
        # 4 manopole: pot lineare B 10k sul cavo (banda -> cursore KnW -> massa), buffer
        for k in range(1, 5):
            secs += [("K%dW%s" % (k, s), "K%d%s" % (k, s), "K%d%s" % (k, s))]
            d.R("K%d%s" % (k, s), "SP" + s, "2k49 0.1%")
        assert len(secs) == 20, len(secs)
        for q in range(5):
            opa4(d, "U%d" % (uq + q), *secs[4 * q:4 * q + 4], note="isolator lato %s, sezioni %d-%d" % (s[1], 4 * q + 1, 4 * q + 4))
        # somma non invertente x10 e servo DC (eq-isolator §9)
        d.R("SV" + s, "SP" + s, "2k 0.1%", note="ramo del servo")
        d.R("NGS" + s, vout, "1k8 0.1%")
        d.R("NGS" + s, "AGND", "200 0.1%")
        d.R(vout, "SVI" + s, "1M")
        d.C("SVI" + s, "SVO" + s, "27n C0G", C12, note="integratore 1M/27n")
        d.R("SVO" + s, "SV" + s, "100k")
        d.R("SV" + s, "AGND", "499 0.1%", note="polo 0,058 Hz, corsa +-129 mV")

    for s, uq in (("_L", 3), ("_R", 8)):
        d.block = "ISOLATOR lato %s (incroci C, dec. 152; iso-incc-banca.inc)" % s[1]
        isolator(s, "GO" + s, "EQ" + s, uq, None)
    d.block = "SOMMA DELL'ISOLATOR (non invertente) e SERVO DC"
    opa2(d, "U13", ("SP_L", "NGS_L", "EQ_L"), ("SP_R", "NGS_R", "EQ_R"), note="somma x10 (2 per banda)")
    opa2(d, "U14", ("AGND", "SVI_L", "SVO_L"), ("AGND", "SVI_R", "SVO_R"), value="OPA1642AIDR",
         note="servo DC (classe OPA2134 nel doc; OPA1642, SBOS484D)")
