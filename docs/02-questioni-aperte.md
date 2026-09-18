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

31. **CHIUSA dal gain-staging sheet §2/§4**: VCA su ±18 V, uso normale con ≥5 dB di margine; estremo (+6 su programma +18) = saturazione morbida intenzionale. Resta solo la verifica in simulazione del carattere del clipping THAT 218x.
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
47. **CHIUSA dal gain-staging sheet**: dominio audio del canale portato a ±18 V (capability +23 dBu); worst user error +18 con 5 dB di margine.
48. Rumore dei potenziometri come dominante nel canale: la simulazione §6.3 decide il valore ohmico dei pot (47 k vs 10 k) prima della sessione hardware (questione 40).

## Verifiche strumentazione

30. Strumentazione di misura disponibile: oscilloscopio? generatore di funzioni? (per le misure audio: scheda audio + REW/ARTA bastano; lo Zoom c'è già). Da comprare solo il necessario, in fase 1.

## Roadmap (unica, sostituisce i "next step" sparsi)

- **ORA (in parallelo)**: attendere export ChatGPT → revisione critica completa → specifica consolidata unica (`SPECIFICA.md`). Deroga Filippo 2026-09-18: il design di fase 1 parte prima dell'export, sulle sezioni già solide.
- **IN CORSO — riallineamento post-documenti (decisioni 58-66)**: MASTER OUT v0.2 valido (correzione REC: 0 dBu fissi + pad solder, decisione 63); CANALE CDJ v0.1 da revisionare a v0.2 (filtro esterno confermato = §3.6 ipotesi valida; gain/EQ/meter/assignment da allineare — addendum in coda al documento). Prossimi in ordine: (1) gain-staging sheet globale (voce 50), (2) compilazione SPECIFICA.md (voce 56), (3) revisione CDJ v0.2, (4) simulazioni LTspice (composite amplifier master, celle EQ, poi SVF del modulo filtro).
- **POI — Fase 1 di costruzione**: modulo canale (phono o CDJ) + modulo FX + master out + PSU di base → valida il backplane.
- **POI — Fase 2**: 5-way preamp e filtro globale (i due blocchi difficili).
- **INFINE**: mic, moduli generici, CUE, metering completo, telaio definitivo, integrazione, taratura sul soundsystem.

## Chiusure e nuovi aperti — 2026-09-18 pomeriggio (risposte di Filippo + status document, decisioni 58-66)

**Corpus CHIUSO**: nessun export migliore ottenibile, nessuna specifica separata lato ChatGPT (decisione 58). Le voci [EXPORT] si risolvono contro gli status doc o restano definitivamente aperte.

Chiusure:
- Voci 1-4 [EXPORT]: CHIUSE — verifica fatta in `docs/03-revisione-critica.md` (contraddizioni phono registrate; versioni superate già marcate nei documenti §38/§18).
- Voce 5 (freq EQ): baseline dai documenti 70/250/1k/5k Hz PROPOSED, boost +6 dB LOCKED (decisioni 59/64); la review con Filippo resta aperta ma c'è una baseline solida.
- Voce 7 (testine/capacità): CHIUSA (decisione 62: MM DJ + MM alta qualità; 100 pF default, selezionabile interno, solo tecnico).
- Voce 11 (SVF): si sposta nel design del MODULO FILTRO esterno (decisione 60).
- Voce 19/39 (metering): semantica colori LOCKED dai documenti; soglie numeriche = proposta master-out §3.6, da validare al banco. Nessun backlog recuperabile.
- Voci 26/27 (DSP/Zoom): CHIUSE — uscite universali (decisioni 49/50/63); i modelli specifici non rilevano per il design.
- Voce 28 (vie impianto): CHIUSA (decisione 66: typologia 5-way dub soundsystem, crossover ~90/350/1,2k/3,5k PROVVISORI).
- Voce 38: summing nel modulo MASTER CONFERMATO dai documenti §3; pinout backplane resta aperto.
- Voci 41/44/45/46: CHIUSE dai documenti (stereo locked; CUE point locked; +6 dB locked; gain −∞→0→+10 locked).
- Voce 42: CHIUSA dalla decisione 60 — modulo filtro ESTERNO, send/return via backplane (l'ipotesi CDJ v0.1 §3.6 era quella giusta).
- Voce 43: CHIUSA in parte — assignment multiple locked; resta aperto il metodo di soppressione transiente (voce 55).

Nuovi aperti:
49. **[APERTO-F]** HPF min: estendere a ~10 Hz (filtro utilizzabile anche con programma infrasub; range 10 Hz–1,5 kHz = 150:1) oppure tenere 20 Hz e usare la posizione OFF per l'infrasub? Raccomandazione di Claude: estendere a 10 Hz se la simulazione SVF conferma la fattibilità del converter log.
50. **ACTION PRIORITARIA** — Gain-staging sheet globale: tabella unica di tutti i nodi (da testina/line in fino a XLR) con nominale/max/dominio — richiesta esplicita di Filippo ("tutti i gain vanno bilanciati col resto del progetto"). Risolve insieme: phono 40 vs 42 dB, margine VCA master (voce 31), headroom bus FX (voce 31/K3), dominio overdrive (K5).
51. Tracking tra i core filtro: 8 core mono (decisione 67, architettura B′) sullo stesso PCB + 6 CV condivisi (HPF freq/res/drive, LPF freq/res/drive). Specificare tolleranza (es. ≤2% in frequenza a pari CV), trim per core, distribuzione CV a stella bufferizzata, e il mux del drive (il CV di overdrive segue la sezione selezionata dallo switch di canale).
52. Calcolo headroom bus FX con ~12 contributori (K3) e regola di gain-staging dei ritorni: livello_in × gain ≤ max dominio (K4) → design modulo FX.
53. Metodo per tracking EQ stereo ≤0,25 dB (K6): pot doppi selezionati + trim vs celle a contribuzione con CV — da decidere nel design EQ v0.2.
54. Procedura di calibrazione identica dei meter DJ tra canali (K7): trimmer o componenti matched — da definire col modulo meter.
55. Soppressione transiente assign FX: usare break-before-make + ramp 1-5 ms come per il filtro (i documenti lo prescrivono solo per il selettore filtro)?
56. Compilazione SPECIFICA.md: il corpus è chiuso, non c'è più motivo di attendere — capitolo per capitolo, dai documenti + decisioni.
57. **CHIUSA (decisione 69)**: interpretazione confermata; capacità selezionabile resta opzione interna economica (veto possibile).
58. Requisito infrasub 10 Hz (decisione 65) — implicazioni da sviluppare nel design: SUB filter bank 10-90 Hz, corner AC ≤5 Hz su tutto il percorso, ballistica meter a 10 Hz, escursione/protzioni altoparlanti restano responsabilità del DSP esterno.
