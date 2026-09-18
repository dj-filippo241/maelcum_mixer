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
26. Quale DSP/processore e quali finali ha l'impianto a valle. **CHIUSA come requisito 2026-09-18**: uscita universale per DSP standard (decisione 49). Il modello specifico resta utile solo per la calibrazione finale al banco, non blocca nulla.
27. Modello esatto dello Zoom per l'uscita REC. **CHIUSA come requisito 2026-09-18**: REC universale per registratori standard (decisione 50).
28. Frequenze di taglio/zone delle 5 vie del suo soundsystem (serve per il filter bank del 5-way — voce 8).
29. Nome/cognome del progetto per il telaio, vincoli meccanici di ingombro (il design del pannello è suo).

## Nati dal design fase 1 — modulo MASTER OUT (2026-09-18, docs/fase1/master-out.md)

31. Margine VCA a +6 dB di trim con picchi programma +16 dBu: il dominio ±18 V è al limite (level plan §4). La simulazione deve dire dove inizia il clipping del VCA e quanto è morbido. Alternative se è brutto: summing a −6 dB interni, rail VCA più alto, o accettare documentando.
32. **[CHIUSA 2026-09-18]** Connettore BOOTH: XLR (decisione 51).
33. **[CHIUSA 2026-09-18]** Detent a unity: sì (decisione 52); hardware manopole rimandato → nuova voce 40.
34. **[CHIUSA 2026-09-18]** Metering: precisione massima, 20 segmenti/canale 3 dB (decisione 53).
35. **[CHIUSA 2026-09-18]** Rail low-noise LT3045/LT3094: sì (decisione 54).
36. **[RINVIATA ALL'EXPORT]** Soglie/colori zone meter: la logica è nel backlog ChatGPT (decisione 55) → voce 39.
37. Verificare esistenza/reperibilità THAT 2181 (doppio VCA); in subordine 2× THAT 2180 su stessa CV o equivalenti ADI (SSM2164/2122, legacy).
38. **[EXPORT]** Confermare da export: chi esegue il summing finale (modulo master o modulo 5-way), standard elettrico I/O del backplane (proposta provvisoria: single-ended 0 dBu tra moduli, bilanciato solo verso l'esterno), numero esatto di ingressi del master summing.
39. **[EXPORT]** Logica colori/zone del meter sulla scala a 20 segmenti: recuperare la definizione dal backlog ChatGPT e mapparla sui segmenti (decisione 55).
40. **[APERTO-F]** Hardware di tutte le manopole del mixer (marca/modello potenziometri, slider, cap, detent): sessione dedicata quando il design elettrico dei controlli è stabile — serve sapere quanti pot servono, di che legge e con quale albero.

## Nati dal design fase 1 — modulo CANALE CDJ/LINE (2026-09-18, docs/fase1/cdj-line-channel.md)

41. **[EXPORT]** Canale stereo vs mono: il design assume stereo con controlli singoli (coerente con decisione 12), ma il resoconto non lo dichiara esplicitamente.
42. **[EXPORT]** Interfaccia filtro: send/return per canale via backplane (ipotesi di lavoro) oppure filtro sul bus DJ a valle dei canali? Critico: decide le connessioni audio del modulo canale.
43. **[EXPORT]** Logica assignment switch FX: 1-of-4 esclusivo o destinazioni multiple? E metodo di soppressione transiente di commutazione (FET-switch vs mini-relay make-before-break).
44. **[EXPORT]** Punto esatto del pickup CUE (il design assume post-EQ pre-split).
45. **[APERTO-F]** Boost EQ per banda: ok +9 dB proposto o più cattivo (+12/+15)?
46. **[APERTO-F]** Trim ingresso: ok −10…+10 dB proposto, o ±6 basta conoscendo i livelli dei suoi CDJ?
47. Margine headroom canale: trim +10 dB + boost multipli possono saturare il dominio ±15 V — la simulazione deve mostrare dove e quanto è morbido il clipping; alternativa: trim max +6 dB.
48. Rumore dei potenziometri come dominante nel canale: la simulazione §6.3 decide il valore ohmico dei pot (47 k vs 10 k) prima della sessione hardware (questione 40).

## Verifiche strumentazione

30. Strumentazione di misura disponibile: oscilloscopio? generatore di funzioni? (per le misure audio: scheda audio + REW/ARTA bastano; lo Zoom c'è già). Da comprare solo il necessario, in fase 1.

## Roadmap (unica, sostituisce i "next step" sparsi)

- **ORA (in parallelo)**: attendere export ChatGPT → revisione critica completa → specifica consolidata unica (`SPECIFICA.md`). Deroga Filippo 2026-09-18: il design di fase 1 parte prima dell'export, sulle sezioni già solide.
- **IN CORSO — design fase 1**: MASTER OUT v0.2 fatto; CANALE CDJ/LINE v0.1 fatto (phono escluso per ora, decisione 56). Prossimi: risposte di Filippo a §7 del canale (boost EQ, trim), poi simulazioni LTspice di entrambi i moduli (primi candidati: composite amplifier del master, EQ a contribuzione del canale).
- **POI — Fase 1 di costruzione**: modulo canale (phono o CDJ) + modulo FX + master out + PSU di base → valida il backplane.
- **POI — Fase 2**: 5-way preamp e filtro globale (i due blocchi difficili).
- **INFINE**: mic, moduli generici, CUE, metering completo, telaio definitivo, integrazione, taratura sul soundsystem.
