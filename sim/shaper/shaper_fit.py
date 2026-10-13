"""Fit dei valori di uno SHAPER a tratti (famiglia unica, docs/fase3/sistema-shaper.md).
Modello: sommatore invertente (Rf 10k) + ramo principale Rm + N rami diodo
(Ra dal segnale al nodo, Rb dal nodo a -5 V, 1N4148 verso la massa virtuale).
Python puro (niente numpy/scipy): bisezione sul nodo + Nelder-Mead sui log(R).
Taratura a 35 C; stampa l'errore a 20/35/50 C. Uso: python3 shaper_fit.py"""
import math
Is,N=2.52e-9,1.752
def idiode(v,T):
    Vt=8.617e-5*T; Tn=300.15
    IsT=Is*(T/Tn)**(3/N)*math.exp((T/Tn-1)*1.11/(N*Vt))
    return IsT*(math.exp(min(v/(N*Vt),60))-1)
def branch(vx,Ra,Rb,Vb,T):
    lo,hi=-6.0,1.0
    for _ in range(50):
        m=0.5*(lo+hi)
        if (vx-m)/Ra+(Vb-m)/Rb-idiode(m,T)>0: lo=m
        else: hi=m
    return idiode(0.5*(lo+hi),T)
Rf=10e3; TF=308.15
def nm(f,x0,it=2000,step=0.15):
    n=len(x0); S=[list(x0)]
    for i in range(n):
        y=list(x0); y[i]+=step; S.append(y)
    F=[f(s) for s in S]
    for _ in range(it):
        o=sorted(range(n+1),key=lambda i:F[i]); S=[S[i] for i in o]; F=[F[i] for i in o]
        c=[sum(S[i][j] for i in range(n))/n for j in range(n)]
        xr=[c[j]+(c[j]-S[-1][j]) for j in range(n)]; fr=f(xr)
        if fr<F[0]:
            xe=[c[j]+2*(c[j]-S[-1][j]) for j in range(n)]; fe=f(xe)
            if fe<fr: S[-1],F[-1]=xe,fe
            else: S[-1],F[-1]=xr,fr
        elif fr<F[-2]: S[-1],F[-1]=xr,fr
        else:
            xc=[c[j]+0.5*(S[-1][j]-c[j]) for j in range(n)]; fc=f(xc)
            if fc<F[-1]: S[-1],F[-1]=xc,fc
            else:
                for i in range(1,n+1):
                    S[i]=[S[0][j]+0.5*(S[i][j]-S[0][j]) for j in range(n)]; F[i]=f(S[i])
    return S[0],F[0]
def fit(name,TH,Y,W,nb,p0):
    # Y = |Vout| desiderata (V) meno il valore a x=0 ; asse x = 5*theta diretto
    def law(p,T=TF):
        out=[]
        for t in TH:
            vx=5*t; i=vx/p[0]
            for k in range(nb): i+=branch(vx,p[1+2*k],p[2+2*k],-5.0,T)
            out.append(Rf*i)
        return out
    def cost(q):
        p=[math.exp(x) for x in q]; d=law(p)
        pen=sum((max(0,math.log(2e3/x))+max(0,math.log(x/1.5e6)))**2 for x in p)*1e3
        return sum(((a-d[0]-y)*w)**2 for a,y,w in zip(d,Y,W))+pen
    q,fv=nm(cost,[math.log(x) for x in p0]); q,fv=nm(cost,q,step=0.05)
    p=[math.exp(x) for x in q]
    print(name,"valori:"," ".join("%.0f"%x for x in p))
    res={}
    for T,lab in ((293.15,"20C"),(308.15,"35C"),(323.15,"50C")):
        d=law(p,T); z=law(p,TF)[0]; res[lab]=[a-z for a in d]
    return p,res
if __name__=="__main__":
    # REROUTE FX: asse x = 5*(1-theta) (pot rovescio); |Vout| = -G*61 mV
    THr=[1,.975,.95,.90,.85,.775,.70,.575,.45,.325,.20,.10,0]
    Gr=[0,-.5,-1,-2.5,-4,-7,-10,-15,-20,-30,-40,-70,-100.]
    Wr=[10,10,10,8,8,5,5,3,3,1.5,1.5,.3,.3]
    p,r=fit("REROUTE",[1-t for t in THr],[-g*0.061 for g in Gr],[w/0.061 for w in Wr],3,[39e3,43e3,300e3,18.5e3,40e3,2.6e3,3.8e3])
    for lab in r: print(" ",lab," ".join("%+6.2f"%(-a/0.061-g) for a,g in zip(r[lab],Gr)),"(errore dB)")
    # DRIVE 5-way: delta dB su 0..16, scala 61 mV/dB
    TH=[0,.25,.5,.575,.65,.725,.8,.85,.9,.95,1]
    GD=[0,3.5,7,8.25,9.5,10.75,12,13,14,15,16]
    p,r=fit("DRIVE",TH,[g*0.061 for g in GD],[1/0.061]*len(TH),2,[82e3,300e3,300e3,150e3,60e3])
    for lab in r: print(" ",lab," ".join("%+5.2f"%(a/0.061-g) for a,g in zip(r[lab],GD)),"(errore dB)")
    # POSITION 5-way: y = 6^theta (x1 V a theta 0 → 6 V a theta 1); fit sulla parte variabile
    TH=[i/20 for i in range(21)]
    Y=[6**t-1 for t in TH]
    p,r=fit("POSITION",TH,Y,[1/(6**t) for t in TH],3,[25e3,40e3,300e3,20e3,60e3,10e3,15e3])
    for lab in r: print(" ",lab," ".join("%+4.1f"%(100*(a+1-6**t)/6**t) for a,t in zip(r[lab],TH)),"(errore % di f)")
