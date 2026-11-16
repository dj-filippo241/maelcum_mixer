"""Pezzi comuni alle schede del 5-way (todo 342): five-way.py (segnale) e five-way-comandi.py.

Prima stavano copiati nei due file. Una sola copia, così un cambio della regola dei condensatori
o del riempimento dei quad vale per tutte e cinque le schede.

Uso:
    from comune_5w import Parti
    pz = Parti(d, primo=0)                # primo: da dove contano i riferimenti U
    uref, Cx = pz.uref, pz.Cx
    P = pz.Pack("+18V", "-18V")
"""
import celle_vca as cv
from celle_vca import C12

CF = "Capacitor_SMD:C_1812_4532Metric"          # film PPS / C0G grandi


class Parti:
    def __init__(self, d, primo=0, nu_col_ref=False):
        """nu_col_ref: nome delle reti delle sezioni libere. False = NU<n>_<k> (schede di segnale),
        True = NUU<n>_<k> (scheda comandi). Due nomi per non cambiare gli schemi già a PASSA."""
        self.d, self.n, self.nu_col_ref = d, primo, nu_col_ref

    def uref(self):
        self.n += 1
        return "U%d" % self.n

    def Cx(self, a, b, v, note=""):
        """Condensatore di segnale: C0G 1206 fino a 22n, film 1812 da 33n in su."""
        if "u" in v:
            big = True
        else:
            big = float(v.replace("n", ".") if not v.endswith("n") else v[:-1]) >= 33
        self.d.C(a, b, v + (" film" if big else " C0G"), CF if big else C12, note=note)

    def Pack(self, vp="+18V", vm="-18V"):
        return Pack(self, vp, vm)


class Pack:
    """Raccoglie sezioni op-amp (ingresso +, ingresso -, uscita) e le mette in quad OPA1654.
    Una sezione libera diventa un inseguitore a massa."""

    def __init__(self, parti, vp, vm):
        self.pz, self.secs, self.vp, self.vm = parti, [], vp, vm

    def add(self, sec):
        self.secs.append(sec)

    def flush(self, note):
        while self.secs:
            q, self.secs = self.secs[:4], self.secs[4:]
            ref = "U%d" % (self.pz.n + 1)
            k = 0
            while len(q) < 4:
                k += 1
                n = "NU%s_%d" % (ref if self.pz.nu_col_ref else ref[1:], k)
                q.append(("AGND", n, n))
            cv.opa4(self.pz.d, self.pz.uref(), *q, vp=self.vp, vm=self.vm, note=note)
