# Questioni aperte

> Tutto ciò che NON è ancora deciso. Quando una voce si chiude, si sposta in
> `01-decisioni-bloccate.md` con data e origine. Le voci marcate **[EXPORT]** richiedono
> prima la lettura dell'export completo di ChatGPT.

## Da risolvere con la revisione dell'export [EXPORT]

1. **[EXPORT]** Verificare ogni decisione [R] di `01-decisioni-bloccate.md` contro l'export completo: il resoconto parziale potrebbe contenere versioni superate di decisioni poi cambiate.
2. **[EXPORT]** Cercare contraddizioni tra risposte date a distanza di giorni (nelle chat lunghe le decisioni cambiano senza annuncio).
3. **[EXPORT]** Recuperare i dettagli che il resoconto cita ma non riporta: diagramma completo del segnale DJ, spec table EQ, diagramma master, posizioni dei meter, tipi di modulo previsti, architettura rail completa.
4. **[EXPORT]** Ricostruire la storia delle correzioni: quali versioni sono state sostituite da quali (il resoconto dice di preservarle come "superseded").

## Progettazione circuitale (tutta la fase 2 del metodo)

5. Topologia e frequenze esatte EQ di canale 4 bande (riferimento Xone dichiarato; centri, Q, gain range da derivare). **[detto "ne riparleremo" da Filippo]**
6. Topologia RIAA reale (funzione di trasferimento composita, gain distribution, overload, rumore).
7. Popolazione di testine previste → loading e capacità d'ingresso phono (il range 100–300 pF NON è congelato).
8. Filter bank 5-way: matematica complementare delle 5 bande, frequenze di crossover, relazione con le 5 vie dell'impianto (Filippo deve fornire le frequenze di taglio del suo sistema).
9. EQ creativo 5-way: implementazione position/width, range, relazione position↔width, legge del gain (+15 dB), interazione tra bande.
10. Drive 5-way: taper esatto del pot (la curva "50% = punto ottimale, +7 dB pulito" va tradotta in legge), stadio JFET vs BJT asimmetrico, interazione con gain di banda.
11. SVF globale: topologia concreta attorno al dispositivo reale (OTA/ladder), controllo logaritmico o a range multipli per il 1000:1, architettura risonanza→auto-oscillazione con limiting prevedibile e musicale (riferimento Sherman → carattere da definire).
12. Overdrive filtro: topologia, gain range, headroom, compensazione/gain staging.
13. Interfaccia pedali: valori selezionabili del pad di mandata, driver, protezione ritorno, impedenze, EQ di mandata (2 bande: topologia e frequenze).
14. Matrice feedback FX: legge di attenuazione, summing, isolamento tra destinazioni, stabilità di loop, accumulo di rumore, implementazione switch/controlli.
15. Mic preamp: topologia e gain range per dinamici (niente phantom), EQ 2 bande, clip warning.
16. Moduli mono generici: quante varianti, impedenze, gain, mono→stereo.
17. Master: valori summing, stadio +6 dB, driver bilanciato concreto (capacità +24 dBu reale), stadio booth, buffer REC con livello adatto allo Zoom.
18. CUE/cuffie: summing CUE, crossfade CUE/master, ampli cuffia, impedenza d'uscita, isolamento di potenza, due uscite.
19. Metering: tipo di meter, numero di LED, costanti di tempo del peak detector, tarature per ogni posizione (DJ, FX return, 5-way, master), soglia red, clip detector purple, architettura driver.
20. PSU: architettura rail finale, correnti per ramo, regolatori locali, sequencing, budget termico, mute on/off.
21. Grounding/EMC: topologia analogue-0V, punto di bonding chassis, trattamento schermi XLR/RCA, strategia masse pedali e giradischi, filtraggio EMC/RF.
22. Backplane: connettore e pinout, famiglia di connettori, correnti/tracce, contatti di massa modulo, requisiti di schermatura.

## Decisioni di Filippo rimandate ("ne parliamo dopo")

23. Chi esegue la costruzione fisica (Filippo, tecnico, PCB assemblati).
24. Formato e layout dei comandi del 5-way (slider vs rotativi per banda; il principio generale "fader=slider, resto=pot" è bloccato, il layout no).
25. Che pedali userà davvero (chitarra e/o rack studio: il principio "pad selezionabile" è bloccato, i valori no).
26. Quale DSP/processore e quali finali ha l'impianto a valle (determina livello nominale d'uscita e calibrazione meter).
27. Modello esatto dello Zoom per l'uscita REC.
28. Frequenze di taglio/zone delle 5 vie del suo soundsystem (serve per il filter bank del 5-way — voce 8).
29. Nome/cognome del progetto per il telaio, vincoli meccanici di ingombro (il design del pannello è suo).

## Verifiche strumentazione

30. Strumentazione di misura disponibile: oscilloscopio? generatore di funzioni? (per le misure audio: scheda audio + REW/ARTA bastano; lo Zoom c'è già). Da comprare solo il necessario, in fase 1.

## Roadmap (unica, sostituisce i "next step" sparsi)

- **ORA**: attendere export ChatGPT → revisione critica completa → specifica consolidata unica (`SPECIFICA.md`).
- **POI — Fase 1 di costruzione**: modulo canale (phono o CDJ) + modulo FX + master out + PSU di base → valida il backplane.
- **POI — Fase 2**: 5-way preamp e filtro globale (i due blocchi difficili).
- **INFINE**: mic, moduli generici, CUE, metering completo, telaio definitivo, integrazione, taratura sul soundsystem.
