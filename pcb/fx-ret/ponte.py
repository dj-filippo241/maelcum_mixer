"""Ponte fra le due schede del FX-RET (todo 167, divisione PROVVISORIA, NOTE.md).

Cavo piatto 2x16, passo 2,54, stesso ordine dei pin sulle due schede: J4 della scheda
segnale (fx-ret.py, col C96) e J1 della scheda reroute (fx-ret-reroute.py, senza C96).
Il backplane non cambia: le iniezioni S1-S4 passano dal C96 della scheda segnale.

Sul cavo viaggiano solo reti a bassa impedenza: alimentazioni, RRN (uscita dell'EQ2), DIR
(uscite dei driver d'iniezione) e i cursori POT_R dal cavo dei pot (J2). Le 10k verso i net
dei bus restano sulla scheda segnale, accanto al C96: il net del bus non entra nel cavo.
"""
PONTE = ["+18V", "+18V", "AGND", "AGND", "-18V", "-18V", "+15LN", "-15LN",
         "AGND", "AGND", "+REF5", "-REF5", "AGND", "AGND", "RRN_L", "RRN_R",
         "AGND", "AGND", "DIR1_L", "DIR1_R", "DIR2_L", "DIR2_R", "DIR3_L", "DIR3_R",
         "DIR4_L", "DIR4_R", "AGND", "AGND", "POT_R1", "POT_R2", "POT_R3", "POT_R4"]


def ponte(d, ref, place, note):
    d.part("J", "Connector_Generic:Conn_02x16_Odd_Even", "2x16 ponte reroute",
           "Connector_PinHeader_2.54mm:PinHeader_2x16_P2.54mm_Vertical",
           {i + 1: n for i, n in enumerate(PONTE)}, ref=ref, place=place, note=note)
