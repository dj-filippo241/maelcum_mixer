"""Kill KICK contro la larghezza della via, LR4 e LR8. RISULTATI-P2 par. 20."""
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kill_casse.py')).read().split("C=[")[0])
import math
def bw8(fc,x,h):
    b=bw(fc,x,h); return b*b   # LR8 = LR4^2
def run(order):
    global lp,hp,ap
    if order==8:
        lp=lambda fc,x: bw8(fc,x,False); hp=lambda fc,x: bw8(fc,x,True)
    else:
        lp=lambda fc,x: bw(fc,x,False); hp=lambda fc,x: bw(fc,x,True)
    ap=lambda fc,x: lp(fc,x)+hp(fc,x)
    globals().update(lp=lp,hp=hp,ap=ap)
    for xs in ([80,170,1200,8000],[70,220,1200,8000],[60,250,1200,8000],[50,300,1200,8000],[40,400,1200,8000]):
        oct_=math.log2(xs[1]/xs[0]); fc=math.sqrt(xs[0]*xs[1])
        B=allb(xs,fc); c=20*math.log10(abs(sum(B)-B[1]))
        # cassa KICK sempre LR4 (VENU)
        def cd():
            def e(kill):
                def g(x):
                    Bx=allb(xs,x); A=sum(Bx); H=A-Bx[1] if kill else A
                    k=bw(80,x,True)*bw(170,x,False)
                    return abs(H*k)**2
                return integ(g)
            return 10*math.log10(e(True)/e(False))
        print(f"LR{order*0+ (4 if order==4 else 8)}  KICK {xs[0]}-{xs[1]} ({oct_:.1f} ott.)  centro {c:6.1f} dB  cassa KICK {cd():6.1f} dB  kill SUB cassa SUB? n.c.")
run(4); run(8)
