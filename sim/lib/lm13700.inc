* =====================================================================
* LM13700 (OTA dual, canale SINGOLO) — macromodello transistor-level
* v0.1 (2026-09-28) — CONDIVISO: filtro v0.3 + celle parametriche 5-way.
* Fonte: datasheet TI SNOSBW2F (nov 1999, rev nov 2015), tabella 6.4
* (VS = ±15 V, TA = 25 °C, IABC = 500 µA, pin 2/15 aperti):
*   - gm = 19,2·IABC (min 6,7 / typ 9,6 / max 13 mS a 500 µA;
*     tracking tra canali 0,3 dB)
*   - PICCO CORRENTE D'USCITA ≈ IABC (5 µA a IABC = 5 µA;
*     350/500/650 µA a IABC = 500 µA) → il nodo integratore NON può
*     superare Vmax(f) = IABC/(2πfC) = f0/(19,2·f) — A f = f0: 52 mV.
*     Il modello lo riproduce FISICAMENTE (coda = IABC).
*   - Iout = IABC·tanh(Vd/2VT): linearità ≤ ~26 mV differenziali senza
*     diodi (THD3 ≈ (Vd/52mV)²/4); DIODI LINEARIZZANTI: cancellation
*     ESATTA solo in drive DIFFERENZIALE (Is su entrambi i diodi,
*     Iout = IABC·Is/ID); in drive single-ended la cancellation è
*     parziale (THD2 ≈ Is/(4·ID)) — §7.3.2 datasheet.
*   - VOS: 0,4 mV typ / 4 mV max; CAMBIO di offset al variare di IABC
*     (5 µA…500 µA): 0,1 typ / 3 mV max → nel modello: param Vos_ota,
*     le sweep vanno lette come inviluppo (typ e max).
*   - Ib: 0,4 µA typ / 5 µA max a 500 µA → Bf = 500 nel modello
*     (0,5 µA per lato a 500 µA); scala ≈ con IABC (coppia d'ingresso).
*   - Swing: ±12/14,2 V (RL = ∞) — il modello non clampa l'uscita OTA
*     (nodo a alta Z: chi legge usa i buffer esterni, progetto v0.2).
*   - Assoluti: supply max 36 V / ±18 V; RACCOMANDATO ±16 V max →
*     il dominio del progetto ±18 V È AL LIMITE ASSOLUTO del chip:
*     rail dedicati ±15/±16 V per gli OTA = nota per il design PSU
*     (questione 20). Nel modello: usare ±15 V (condizione datasheet).
* RUMORE — ASSENTE dal datasheet come specifica numerica (solo Fig. 15,
* grafico "Output Noise vs Frequency"): il modello lo genera FISICAMENTE
* (shot/termica della coppia: en ≈ sqrt(4kT·2·(Rb+re)), re = 2VT/IABC):
* MISURATO nel self-test (modello col mirror d'uscita completo, 2026-10-14):
* 3,7 nV/√Hz a 500 µA · 6,4 a 100 µ · 10,8 a 31 µ · 21,4 a 7,56 µ ·
* 41,4 a 2 µ · 186 a 100 nA (piatta in frequenza nel macro). Prima del fix
* del 2026-10-14 i valori erano ×0,71 (2,6 · 4,5 · 7,7 · 15,2 · 29,4 · 133).
* [PROVVISORIO — regola 3: è il LIMITE FISICO della coppia; il die reale
* (r_bb' vera, mirror, geometria laterale) sarà verosimilmente 2-5× peggio:
* trattare i margini di rumore come OTTIMISTI e verificare a banco.]
* ASSENTI (verifica a banco/prototipo): THD del die reale oltre la tanh
* (geometrie/laterale PNP), breakdown, CMRR 80-110 dB (modello: ∞),
* crosstalk tra canali (100 dB), buffer Darlington interni (il progetto
* usa buffer op-amp esterni: non modellati), deriva termica di gm.
* Topologia del macro (comportamento, non il die): mirror di coda 1:1
* (Q1/Q2) + coppia diff NPN (Q4/Q5) + mirror PNP di uscita (Q6/Q7):
* Iout = Ic4 − Ic5 = IABC·tanh(Vd/2VT). Vce interni non fisici (il die
* reale è cascodato): macro valido entro ±15 V, CM ±13 V.
* Pin: inp inn out iabc dbp dbn vcc vee
*   - iabc: il pin ASSORBE Iabc (modello: Q1 verso vee, pin ≈ vee+0,7 V;
*     nel progetto reale il pin sta a V− + 2 Vbe — la distribuzione
*     mirror bufferizzati del filtro v0.2 gestisce il livello).
*   - dbp/dbn: bias diodi linearizzanti (ID entra nel pin, esce su
*     inp/inn); aperti = diodi inerti (R 1G di convergenza).
* Uso: X<name> inp inn out iabc dbp dbn vcc vee LM13700 [Vos=<val>]
*   + generatore di corrente sul pin iabc (es. Ix vcc iabc DC {Iabc}).
* PARAMS: Vos = offset d'ingresso (default 0,4 mV typ; 4m = max;
*   il CAMBIO con Iabc aggiunge ±0,1…3 mV: le sweep vanno lette come
*   inviluppo). Esprimibile come {param} globale per .step.
* =====================================================================
.subckt LM13700 inp inn out iabc dbp dbn vcc vee PARAMS: Vos=0.4m
* --- mirror di coda: I(Q1) = Iabc → tail = Iabc ---
Q1 iabc iabc vee QN13700
Q2 tail iabc vee QN13700
* --- offset di tensione (mismatch interno) ---
Vosrc inn innx DC {Vos}
* --- coppia d'ingresso: Q4 su inp, Q5 su innx ---
Q4 a inp tail QN13700
Q5 b innx tail QN13700
* --- mirror di uscita PNP: riporta Ic4 su out (sorgente) ---
Q6 a a vcc QP13700
Q7 out a vcc QP13700
* --- FIX 2026-10-14 (D5, sim/filtro/RISULTATI-D5.md): Ic5 arriva su out
* attraverso un mirror PNP (Q8/Q9) e un mirror NPN (Q10/Q11), come nel
* die reale. Prima Q5 aveva il collettore direttamente su out: sotto
* ~-0,4 V d'uscita Q5 saturava (continua e H2 spurie). I risultati con
* stati d'uscita sopra -0,4 V (core nudo, celle 5-way) non cambiano. ---
Q8 b b vcc QP13700
Q9 c b vcc QP13700
Q10 c c vee QN13700
Q11 out c vee QN13700
* --- diodi linearizzanti (matched alla coppia): ID da dbp/dbn ---
QDp dbp dbp inp QN13700
QDn dbn dbn inn QN13700
Rdbp dbp 0 1G
Rdbn dbn 0 1G
* Vaf = 2000: il die reale ha mirror/cascode ad alta Z (datasheet: uscita
* OTA ~8 MΩ min = ro = Vaf/Ic → 7 MΩ a 500 µA). Con Vaf = 100 il self-test
* mostrava gm +20% (Early dei mirror) e corrente d'offset d'uscita = 7% di
* Iabc (≈ 3,6 mV di Vos efficace: oltre il max datasheet) — entrambi artefatti.
.model QN13700 NPN(Is=1e-15 Bf=500 Vaf=2000 Rb=50 Cje=2p Cjc=1p Tf=1n)
.model QP13700 PNP(Is=1e-15 Bf=500 Vaf=2000 Rb=50 Cje=2p Cjc=1p Tf=1n)
.ends LM13700
