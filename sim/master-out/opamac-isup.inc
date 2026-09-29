* ============================================================
* OPAMAC-ISUP — macromodello OPA1612 v0.2 + ASSORBIMENTO REALE
* Perche' esiste: la macro v0.2 (inline in comp-*.cir) ha l'uscita
* come VCVS ideale che NON assorbe corrente dai rail e Iq = 0.
* Col bootstrap (decisione 86) i rail sono generati da pass serie:
* il dimensionamento reale deve vedere Iq 40 mA (datasheet OPA1612)
* + la corrente di uscita del chip assorbita dai rail locali.
* --- VERSIONE v0.3b (2026-09-29): SPECCHIO LINEARE ---
* La v0.3a usava max(±I(E3),0) (kink a I=0): in .ac/.noise la
* linearizzazione sul kink e' indefinita → picchi spuri (+6,5 dB
* misurati con carico 33 nF) e in .tran il kink inietta un gradino
* a ogni attraversamento della corrente di carico → pettine di
* armoniche ~1,2 % su 600 Ohm (misurato, artefatto).
* La v0.3b modella la classe AB del chip con lo specchio lineare,
* esatto intorno all'idle (entrambi i rami conducono):
*   Bq: Iq 40 mA costanti da vp a vm (corrente quiescente chip)
*   Bp: vp → 0, assorbe −I(E3) da vp quando il chip eroga
*   Bm: 0 → vm, inietta I(E3) su vm quando il chip assorbe
* KCL del nodo out: solo E3 (nessuna doppia iniezione).
* Approssimazione dichiarata: il ramo non interessato al segnale
* vede Iq ∓ x invece di Iq (errore ≤ picco di carico, ≤ 30 mA,
* sul lato FREDDO del dimensionamento: il lato caldo — vp quando
* eroga, vm quando assorbe — e' esatto = Iq + x → conservativo).
* Segnale/uscita/guadagno IDENTICI alla v0.2 (E1-E3 invariati).
* STATO MODELLI [PROVVISORIO — regola 3]: GBW 80 MHz, A0 120 dB,
* 2° polo 40 MHz, clamp ±(rail−1,5 V) come v0.2.
* NOTA D'USO: questa variante lineare e' LENTA in .tran (accoppiamento
* continuo I(E3)-rail nel Newton: run abortito a 27 min contro i ~7
* della abs) → usare SOLO per .ac/.noise. Per .tran: opamac-isup-t.inc.
* ============================================================
.subckt OPAMAC inp inn out vp vm
E1 x 0 value={1000*(V(inp)-V(inn))}
R1 x p1 1k
C1 p1 0 1.99u
E2 y 0 p1 0 1000
R2 y p2 1k
C2 p2 0 3.98p
E3 out 0 value={limit(V(p2),V(vm)+1.5,V(vp)-1.5)}
* --- assorbimenti alimentazione (v0.3b, specchio lineare) ---
Bq vp vm I={40m}
Bp vp 0 I={-I(E3)}
Bm 0 vm I={I(E3)}
.ends OPAMAC
