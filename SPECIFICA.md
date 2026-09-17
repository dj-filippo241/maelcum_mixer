# SPECIFICA — MAELCUM MIXER (mixer dub modulare analogico, esemplare unico)

> **STATO: SCHELETRO.** Questo documento diventerà la specifica unica e autorevole.
> Si compila DOPO la revisione critica dell'export completo di ChatGPT (vedi
> `docs/02-questioni-aperte.md`, voci [EXPORT]). Fino ad allora fa fede la coppia
> `docs/01-decisioni-bloccate.md` + `docs/02-questioni-aperte.md`.
>
> **Convenzione di stato** per ogni voce:
> `[BLOCCATO]` deciso, non si ridiscute · `[PROVVISORIO]` target di lavoro, misurabile/correggibile ·
> `[APERTO]` da decidere · `[SUPERATO]` versione vecchia, tenuta solo per storia (con data e motivo).
>
> **Metodo della fase circuitale**: requisito funzionale → funzione di trasferimento →
> topologia → selezione componenti → simulazione → vincoli PCB → prototipo → misura → revisione.

## 1. Vincoli globali di progetto

[DA COMPILARE — una sola volta: analogue-only/no DSP, filosofia livelli (0 dBu nom, +24 dBu di sistema), rail ±24 V con domini locali, no dinamica automatica, nonlinearità solo dove voluto, buffering low-Z, regole stereo, regola protezioni ≠ limiting]

## 2. Architettura del segnale — diagramma autorevole unico

[DA COMPILARE — un solo diagramma completo: sorgenti → canali → bus → 5-way → master sum → uscite; diramazioni FX, CUE, meter]

## 3. Moduli e backplane

[DA COMPILARE — tipi di modulo previsti, standard elettrico I/O tra moduli, connettore e pinout, separazione audio/controllo/potenza/ground, CV 0–5 V come convenzione d'interfaccia]

## 4. Canale DJ (modulo)

[DA COMPILARE — catena input → gain → EQ → CUE/FX split → filtro → fader → bus; phono/RIAA; line; EQ 4 bande stile Xone; gain range]

## 5. Filtro globale (modulo condiviso)

[DA COMPILARE — SVF 4 poli, range HPF/LPF, 4 controlli condivisi + selettore locale, risonanza/auto-oscillazione musicale in stile Sherman, overdrive post-filtro]

## 6. 5-way performance EQ / dub preamp (modulo)

[DA COMPILARE — filter bank complementare sulle 5 vie dell'impianto, kill switch per via, EQ creativo position/width/gain, curva drive (CCW pulito, 50% ottimale, >50% saturazione progressiva), meter di sezione]

## 7. Sistema FX

[DA COMPILARE — 4 bus, send con EQ 2 bande, interfaccia pedali con pad selezionabile (chitarra + rack studio), ritorni, matrice feedback 12 percorsi con reroute pre-fader, VCA, controlli pensati per l'uso live]

## 8. Mic e ingressi mono generici (moduli)

[DA COMPILARE — mic dinamici senza phantom, gain ~40-50 dB, EQ 2 bande, clip warning; modulo sorgente generico mono→stereo]

## 9. Master, Booth, Rec

[DA COMPILARE — summing, MASTER LEVEL attivo −∞→0→+6 dB linked, uscita XLR bilanciata attiva, BOOTH pre-master-level, REC fisso verso Zoom, buffer dedicati, protezioni e mute]

## 10. CUE / cuffie

[DA COMPILARE — summing CUE, crossfade CUE/master, ampli cuffia, due uscite, isolamento]

## 11. Metering

[DA COMPILARE — 6 zone blue→purple, clip detector vero per il purple, posizioni dei meter, costanti di tempo, tarature, soglie]

## 12. Alimentazione

[DA COMPILARE — toroidale lineare + regolazione locale, rail e domini, budget correnti, protezioni per ramo, sequencing, mute on/off, termica]

## 13. Grounding ed EMC

[DA COMPILARE — strategia di massa come sistema unico: analogue 0V, chassis/PE, schermi XLR/RCA, masse pedali e giradischi, filtraggio]

## 14. Budget di rumore

[DA COMPILARE — target per stadio + calcolo del budget complessivo (sostituisce il −90 dBu "globale" non verificato)]

## 15. Interfaccia meccanica/elettrica

[DA COMPILARE — requisiti elettrici per il design del pannello di Filippo: consumi modulo, pin, correnti backplane, contatti massa, schermature, accessi di servizio]

## 16. Roadmap di costruzione

[DA COMPILARE dalla roadmap in docs/02 — fase 1: canale + FX + master + PSU; fase 2: 5-way + filtro; poi integrazioni]

## Appendice A — Storia delle correzioni

[DA COMPILARE dall'export — versioni superate con data e motivo, per non ripetere gli errori]

## Appendice B — BOM e costi

[DA COMPILARE modulo per modulo, quando i circuiti sono scelti; stima spannometrica attuale: 3.000–4.000 € materiali per la macchina completa, fase 1 ~700–1.300 €]
