# Riconta dal basso della corrente del ramo audio ±18 V (W1), todo 142, 2026-10-26.
# Quantita' da docs/budget/genera_budget.py; Iq da datasheet. Uso: python3 docs/fase3/riconta_w1.py
# Riconta del ramo audio ±18 V (W1): corrente per ramo, mA.
# Iq per chip: (vecchia tabella sistema-psu §1, datasheet tipico, datasheet massimo)
IQ = {
 'opa1612': (4.0, 7.2, 9.0),    # dual: 3,6 mA/canale typ, 4,5 max (TI)
 'opa1654': (7.2, 8.0, 10.0),   # quad: 2,0 mA/canale typ, 2,5 max (TI)
 'vca':     (5.5, 5.5, 7.0),    # 2181 ~2,4 typ + quota I/V (tabella di progetto); max ~4 + I/V
 'dual':    (8.0, 8.0, 10.0),   # servo classe OPA2134: 4 mA/canale typ, 5 max
 'lm317':   (5.0, 5.0, 10.0),   # corrente del partitore di ogni regolatore (un rail)
}
# (modulo, copie, {chip: quantita' sui ±18}, extra mA typ, extra mA max, nota)
M = [
 ('Canale CDJ',   4, {'opa1654':12,'opa1612':5,'dual':1,'vca':4,'lm317':1}, 0, 0, 'phono (2 OPA1612) sul LN ±15'),
 ('FX-SEND',      4, {'opa1654':3,'opa1612':1,'lm317':1}, 0, 0, ''),
 ('FX-RET',       4, {'opa1654':5,'opa1612':1,'vca':12,'lm317':1}, 2, 4, 'JFET dei buffer'),
 ('Filtro',       1, {'opa1654':20,'vca':8,'lm317':1}, 0, 0, 'tutti gli op-amp sui ±18 (prudente); OTA sul LN'),
 ('5-way',        1, {'opa1654':36,'opa1612':11,'dual':2,'lm317':1}, 10, 20, 'GROWL/NASTRO discreti'),
 ('CUE cuffie',   1, {'lm317':1}, 61, 150, 'stadio v0.2: 61 idle; 150 = programma forte in cuffia'),
 ('MIC',          1, {'opa1654':3,'opa1612':1,'vca':1,'lm317':1}, 0, 0, 'INA (2 OPA1612) sul LN'),
 ('MONO',         3, {'opa1654':3,'opa1612':1,'lm317':1}, 0, 0, ''),
]
OPZ = [  # moduli opzionali (dec. 111), stima con Iq da datasheet
 ('Crossfader',          {'vca':8,'opa1654':2,'lm317':1}, 0),
 ('EQ grafico x2',       {'opa1654':12,'lm317':2}, 0),     # 12 bande stereo: ~6 quad per inserzione
 ('Uscite per via',      {'opa1654':8,'opa1612':5,'lm317':1}, 30),  # LR4 stereo + 10 driver
 ('Anello XF nei canali',{'opa1612':2}, 0),
]
def tot(chips, k): return sum(IQ[c][k]*n for c,n in chips.items())
for k,nome in [(0,'vecchia tabella'),(1,'datasheet tipico'),(2,'datasheet massimo')]:
    base=0
    righe=[]
    for m,cp,ch,et,em,_ in M:
        v=(tot(ch,k)+(em if k==2 else et))*cp
        base+=v; righe.append((m,cp,v))
    opz=sum(tot(ch,k)+e for _,ch,e in OPZ)
    print(f'== {nome}: base {base:.0f} mA, opzionali {opz:.0f} mA, totale {base+opz:.0f} mA')
    if k==1:
        for m,cp,v in righe: print(f'   {m:12} x{cp}: {v:5.0f} mA')
        for o,ch,e in OPZ: print(f'   opz {o:20}: {tot(ch,1)+e:5.0f} mA')
