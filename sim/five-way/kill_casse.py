"""Kill del 5-way sulle casse dell impianto (VENU360 LR4 37/80/170/1100), banca
LR4 risommata, rumore rosa. Python puro. RISULTATI-P2 par. 20 (2026-11-06)."""
import math
N=3000
F=[10**(math.log10(20)+(math.log10(20000)-math.log10(20))*i/(N-1)) for i in range(N)]
def bw(fc,x,hpq):
    s=1j*x/fc; d=1+math.sqrt(2)*s+s*s
    b=(s*s/d) if hpq else (1/d); return b*b
def lp(fc,x): return bw(fc,x,False)
def hp(fc,x): return bw(fc,x,True)
def ap(fc,x): return lp(fc,x)+hp(fc,x)
def band(xs,i,x):
    h=1
    for j in range(i): h*=hp(xs[j],x)
    if i<len(xs): h*=lp(xs[i],x)
    for j in range(i+1,len(xs)): h*=ap(xs[j],x)
    return h
def allb(xs,x): return [band(xs,i,x) for i in range(len(xs)+1)]
cab={'SUB':lambda x:hp(37,x)*lp(80,x),'KICK':lambda x:hp(80,x)*lp(170,x),'MID':lambda x:hp(170,x)*lp(1100,x),'HIGH':lambda x:hp(1100,x)}
def integ(fn):
    tot=0
    for k in range(N-1):
        x0,x1=F[k],F[k+1]; tot+=(fn(x0)/x0+fn(x1)/x1)/2*(x1-x0)
    return tot
def cab_drop(xs,b,c):
    def e(kill):
        def g(x):
            B=allb(xs,x); A=sum(B); H=A-B[b] if kill else A
            return abs(H*cab[c](x))**2
        return integ(g)
    return 10*math.log10(e(True)/e(False))
def centro(xs,b):
    fc=40 if b==0 else (2*xs[-1] if b==len(xs) else math.sqrt(xs[b-1]*xs[b]))
    B=allb(xs,fc); return 20*math.log10(abs(sum(B)-B[b]))
C=[('E impianto',[80,170,1200,6000]),('F',[70,220,1200,8000]),('H',[60,250,1200,8000]),
   ('A vecchia',[90,350,1200,3500]),('B Jah Tubbys',[80,200,1200,6000]),('C JB Audio',[75,190,2200,8000]),
   ('D Speakerplans',[80,220,1500,7000]),('Dubsounds DIY',[90,180,1200,5000]),('Deep Field + 1,2k',[91,239,1200,4168]),
   ('Condesa + 1,2k',[80,280,1200,4000]),('isolator 110/210',[110,210,1500,3000])]
print("variante              incroci                 centro SUB KICK MID HIGH SUP | cassa SUB KICK MID HIGH(kH) HIGH(kS)")
for k,xs in C:
    cs=[centro(xs,b) for b in range(5)]
    cd=[cab_drop(xs,0,'SUB'),cab_drop(xs,1,'KICK'),cab_drop(xs,2,'MID'),cab_drop(xs,3,'HIGH'),cab_drop(xs,4,'HIGH')]
    print(f"{k:21s} {str(xs):24s}"+" ".join(f"{v:5.1f}" for v in cs)+" | "+" ".join(f"{v:5.1f}" for v in cd))
