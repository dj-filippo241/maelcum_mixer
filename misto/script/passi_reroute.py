"""Passi della catena del misto sulla law del reroute (fx-module §8.3).
Uso: python3 misto/script/passi_reroute.py
Calcola, per ADC e DAC di N bit, il passo in dB nel punto peggiore e nella zona del
feedback (0..-15 dB). Law: lineare in dB fra i 13 punti della griglia; VCA 6,1 mV/dB al pin EC-.
"""
TH = [0, .10, .20, .325, .45, .575, .70, .775, .85, .90, .95, .975, 1]
DB = [-100, -70, -40, -30, -20, -15, -10, -7, -4, -2.5, -1, -.5, 0]
K = 6.1e-3  # V/dB al pin
SPAN = 0.85  # campo al pin, V: -0,05..+0,80 (law + correzioni di chip e temperatura, 03 §4.3)


def law(t):
    for i in range(len(TH) - 1):
        if TH[i] <= t <= TH[i + 1]:
            f = (t - TH[i]) / (TH[i + 1] - TH[i])
            return DB[i] + f * (DB[i + 1] - DB[i])
    return 0.0


def passi_adc(bit):
    n = 2 ** bit
    peggio = zona = 0.0
    for i in range(n):
        d = abs(law((i + 1) / n) - law(i / n))
        peggio = max(peggio, d)
        if law(i / n) >= -15:
            zona = max(zona, d)
    return peggio, zona


if __name__ == "__main__":
    print("ADC sulla manopola: passo in dB per un passo di lettura (bit effettivi)")
    for b in (9, 10, 12, 16):
        p, z = passi_adc(b)
        print("  %2d bit: peggiore %.3f dB   zona 0..-15 dB %.4f dB" % (b, p, z))
    print("DAC: passo al pin (campo %.2f V)" % SPAN)
    for b in (12, 14, 16):
        lsb = SPAN / 2 ** b
        print("  %2d bit: %.3f mV = %.4f dB" % (b, lsb * 1e3, lsb / K))
    print("Errore senza compensazione termica (costante del VCA +0,33 %/C, taratura a 25 C)")
    for t in (40, 55, 65):
        f = 1 + 0.0033 * (t - 25)
        print("  %d C: a -15 dB %+.2f dB, a -40 dB %+.2f dB, a -100 dB %+.1f dB"
              % (t, -15 / f + 15, -40 / f + 40, -100 / f + 100))
