* ============================================================
* OPAMAC-ISUP-T — variante TRAN (swing/THD/corto/servo)
* Identica alla v0.3b (opamac-isup.inc) nella TOPOLOGIA degli
* assorbimenti — Bq vp→vm (Iq 40 mA), Bp vp→0 (source), Bm 0→vm
* (sink), KCL del nodo out affidato alla sola E3 (nessuna doppia
* iniezione della v0.3a) — ma usa max(±I(E3),0) invece dello
* specchio lineare: in .tran il kink a I(E3)=0 e' gestito a tratti
* dal simulatore (nessuna linearizzazione) e riproduce il taglio
* reale del ramo in controfase (classe AB: il ramo freddo smette
* di assorbire oltre Iq, non va in negativo come nel lineare).
* COSTO DICHIARATO: il riferimento I(E3) dentro il subckt rallenta
* il Newton a ogni passo (misurato: run >4× piu' lento della v0.3a)
* → questa variante si usa SOLO dove il kink non tocca l'uscita:
* i rail alimentano la macro solo via clamp limit() (inattivi in
* regime lineare) → nessuna iniezione su OUT.
* Per .ac/.noise usare opamac-isup.inc (specchio lineare: kink
* indefinito = picchi spuri misurati nella v0.3a, documentati).
* STATO MODELLI [PROVVISORIO — regola 3].
* ============================================================
.subckt OPAMAC inp inn out vp vm
E1 x 0 value={1000*(V(inp)-V(inn))}
R1 x p1 1k
C1 p1 0 1.99u
E2 y 0 p1 0 1000
R2 y p2 1k
C2 p2 0 3.98p
E3 out 0 value={limit(V(p2),V(vm)+1.5,V(vp)-1.5)}
* --- assorbimenti alimentazione (variante tran, max) ---
Bq vp vm I={40m}
Bp vp 0 I={(-I(E3)+abs(I(E3)))/2}
Bm 0 vm I={(I(E3)+abs(I(E3)))/2}
.ends OPAMAC
