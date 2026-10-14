# BENCHMARK ESTESO — preamp dub, mixer DJ, mixer live (ricerca 2026-10-14)

> Estende `docs/05-benchmark-preamp-scena-2026-09-30.md` (9 preamp dub, che
> resta valido e non si ripete qui). Lista approvata da Filippo il
> 2026-10-14 («tutti»; nessun modello è principale: tutti a fondo).
> Ricerca web dello stesso giorno. Numeri tra virgolette = dati pubblicati
> dal costruttore o dal manuale; [R] = dato da rivenditore o forum, da
> confermare; n.p. = non pubblicato.
>
> Regola di lettura dei numeri di rumore: quasi tutti i costruttori misurano
> NON pesato, 22 Hz-22 kHz (o 20-20k), e a nominale +4 dBu. I nostri numeri
> sono A-pesati e a nominale 0 dBu. Per confrontare: il nostro A-pesato vale
> circa 2-4 dB in meno del non pesato; e il nostro rapporto segnale/rumore
> parte da 4 dB più in basso a parità di fondo, perché il nominale è 0 dBu.

## 1. Preamp dub (9 in docs/05 → 18)

| # | Modello | Paese | Tipo | Cosa ha | Numeri |
|---|---|---|---|---|---|
| 10 | Moses Audio 6U (ex Built By Moses) | UK | analogico, **stereo**, 5 vie | filtri variabili 24 dB/ott. che sostituiscono il DSP esterno; EQ a 16 bande **solo boost** (parte piatto, la manopola aggiunge); 5 parametrici. Uscito nel 2026 | n.p. |
| 11 | Ras EFX RAS-5500 (dub-siren.com) | n.p. | analogico, 5 vie | phono + line, **2 ingressi sirena, 2 mic con EQ**, 2-3 loop send/return assegnabili, EQ grafico 10 bande, semiparametrico per via, kill per via, **schede di crossover intercambiabili** | n.p. |
| 12 | Leviel Audio Standar 5W4U | FR | analogico mono 5 vie (stereo su misura) | **EQ parametrico 4 bande con Q regolabile**, uscite bilanciate | n.p. |
| 13 | Jo Red (Ginevra, chiuso ~2016-17) | CH | analogico, 3-4 vie | 5 canali, EQ **3 bande su mic e ritorni FX** (JTS e Mostec ne hanno 2), kill, send/return; somma tutto a mono [R] | n.p. |
| 14 | Jah Tubby's Enforcer EN4 / Annihilator AN4 | UK | analogico, 3-4 vie | rack 19" acciaio; cut-out switch per via; livello per via; grafico 10-12 bande; parametrico su bassi e medi; 2 phono con crossfade; LED per uscita; **2 coppie send/return eco**; 4 (EN4) o 3 (AN4) ingressi mic; **mono** (si sceglie L o R del disco) [R]; incroci di un esemplare 100 / 75-300 / 300-4k / 3,5k+ Hz [R] | usato ~£1.000 |
| 15 | Valv-a-tron (Paul Axis, Huddersfield) | UK | **tutto a valvole**, 2-3 vie, su commissione | pre, phono, finali KT88, delay analogico; sistema giocato solo in vinile | n.p. |
| 16 | BADDRIDDIM Workshop (Limoges) | FR | analogico su misura | preamp e FX dub (spring reverb, eco, **filtro a sweep ottico**); trattamento **tropicalizzato** (caldo e umidità) | n.p. |
| 17 | JBK Audio (software) | FR | **preamp in software** (PC + scheda ASIO, MIDI) + emulazione web | 2 ingressi musica, aux con gain + EQ2 + send, n vie, grafico 10 bande, 2 semiparametrici; sirena digitale DSG | — |
| 18 | «Niente preamp»: mixer + crossover + EQ esterni (sound-system.fr) | — | architettura alternativa | tesi: un preamp ha ~2 mandate, incroci fissi, è mono, colora sempre, usa solo jack; un mixer + crossover DSP è più versatile e spesso costa meno | — |

Note: Sage Sound (già #2 in docs/05) ha riaperto a fine 2024. **3u**
(analogico mono, £1.275): line + phono, grafico 11 bande, 1 semiparametrico
mids/tops, sweep sub, sweep LPF, 2 mandate, insert; 2 mic con insert, 4 aux
(2 con bassi/acuti, 2 con mandate), uscite collegabili a 2-3-4 vie, tutto
bilanciato salvo phono e insert. **5u** (DSP stereo, £1.675): 2 line + 1
phono stereo, **filtri HPF e LPF risonanti con pendenza regolabile**,
grafico 11, 3 semiparametrici, 2 mandate con medi e acuti separabili, 5 aux,
per uscita: crossover con pendenza, polarità, delay, limiter, **noise gate**;
SPDIF/AES. Abzu Crossfire (già #1): 5u e 8u (da £2.000), DSP; music con 2
mandate (full / medi / acuti / medi+acuti), aux con EQ3 + HPF 150/300 Hz,
**mic con limiter a una manopola**, 2 ritorni FX con EQ2 + HPF, **larghezza
stereo**, grafico 12 bande pre o post crossover, **HPF/LPF risonanti**,
**GROWL** (Amount + Dry/Wet + Hard/Soft) sul sub; per via: limiter, EQ3,
polarità, delay, incrocio, gain. RDH Electronics = marchio da cui nasce
Klementz (già #4): non è un costruttore in più.

## 2. Mixer DJ (6 citati nei documenti → 16)

Già citati nei documenti, ora schedati:

| Modello | Architettura | Filtro | EQ / isolator | Mandate | Headroom / uscita max | Rumore (non pesato salvo nota) |
|---|---|---|---|---|---|---|
| A&H Xone:92 (orig.) | analogico | 2 VCF stereo HPF/BPF/LPF, RES, 2 LFO | 4 bande +6 / −30 medi / −∞ LF-HF 12 dB/ott. | aux | canali +22 dB; MIX1 +22 dBu | residuo −99 dBu; mix −88 dBu |
| A&H Xone:92 Mk2 | analogico | 2 VCF, commutazione silenziosa | idem | aux | MIX1 +25 dBu | residuo −85; mix −81 dBu |
| A&H Xone:96 | analogico + scheda audio | 2 VCF HPF/BPF/LPF + RES + **CRUNCH** (distorsione prima del filtro), assegnabili | HI 3k +6/−∞, medi +10/−27, LO 180 +6/−∞ | aux | canali +20 dB; M1 +24 dBu | residuo −98; mix −90 dBu; THD 0,03 % |
| Pioneer DJM-900NXS2 | **digitale** (ADC 24 bit, mix 64 bit) | filtro per canale (DSP) | EQ −26/+6 o isolator −∞/+6 | send/return | n.p. | S/N line 105 dB (A, al nominale) |
| Pioneer DJM-V10 | **digitale** | HPF/LPF con RES per canale (DSP); **compressore per canale** | isolator master 3 bande; EQ 4 bande | 2 send/return esterni + Multi I/O | n.p. | S/N line 105 dB |
| Rane MP2015 | rotary **ibrido** (analogico + DSP 32 bit float, AKM) | **24 dB/ott. per canale HP/LP/HP+LP**, una RES | canale LR2 kill 150/6k o 300/3k; **isolator master LR4 24 dB/ott. a incroci variabili** | — | 8 Vrms XLR | gamma dinamica 113 dB A; THD+N 0,0009 % |
| E&S DJR400 | analogico cablato punto-punto, Parigi | — | isolator 10-300 / 300-3k / 3k-25k | loop su master e booth; send per canale (opzione) | XLR +22 dBm | n.p. |

Nuovi:

| # | Modello | Architettura | Cosa ha | Numeri |
|---|---|---|---|---|
| 1 | **A&H Xone:464** (fuori produzione) | analogico, **ibrido DJ + live**, **interno modulare (una scheda verticale per canale)** | 4 mono mic/line (phantom, HPF 100 Hz, pad −30, mute, pan, fader 100 mm) + 6 stereo (4 phono), 2 bus Mix1/Mix2 (i mono su entrambi, gli stereo solo Mix1); **6 aux da ogni canale**; 2 VCF stereo indipendenti FREQ + RES + comandi globali; EQ 4 bande +6 / −26; crossfader VCA; 2 cuffie; split cue; booth | headroom canali +21 dB, mix +23 dB; XLR max **+26 dBu**; LED di picco 9 dB prima del clip; residuo XLR **−90 dBu**; mix con un canale **−86 dBu** (S/N 90); EIN mic **−128 dB**; THD < 0,006 % a +14 dBu; 20 Hz-40 kHz +0/−1 |
| 2 | **PLAYdifferently Model 1** (Richie Hawtin / A&H) | analogico, 6 canali | **filtri passivi** (niente VCF: niente deriva termica né continua) HPF/LPF per canale a Q basso; **filtri risonanti solo sul master; la RES dell'HPF cala da sola quando la frequenza scende**; EQ «Sculpt» +8 / −20; mandate al centro del gesto; DRIVE in ingresso | **+28 dBu** bilanciato (rail ~±20 V da switching a 24 V); line-line −90 dBu, residuo **−100 dBu** non pesati; ingresso pulito > +20 dBu |
| 3 | Condesa Carmen V (Australia) | **tutto discreto**, rail **48 V** [R], derivato Bozak | 4 canali rotary; EQ 3 bande per canale; isolator master 4 bande **discreto 24 dB/ott., +12 / −∞**, true bypass; send/return; niente gain di canale | n.p. |
| 4 | Bozak CMA-10-2DL (1971-82) | discreto, **schede a innesto** (phono/line/mic si cambiano con la scheda) | 4 stereo + 2 mono, bassi/acuti ±10, insert FX (chiesto da Richard Long); alimentatore 36 V CT con soft start (~7 s) | out +18 dBm; rumore −125 dBm (pubblicità 1976); restauratore: 30 Vpp senza problemi; THD < 0,2 % |
| 5 | UREI 1620 (Sun Valley, CA) / 1620LE | discreto, **tutto su moduli a innesto** | clone Bozak con 2 aux in più + mic; bilanciamento per canale; bassi/acuti ±10; loop FX; cuffia da qualunque canale o dal master; **alimentatore interno «parte del suono»** (Soundcraft) | n.p. |
| 6 | MasterSounds Radius 4 / 4V / 4 MK2 (design A. Rigby-Jones, ex capo Xone) | analogico; 4V con **4 doppi triodi come buffer d'ingresso ai VCA** | isolator 12 dB/ott. 350 / 3,5k, OFF … +12; HPF per canale; 4V: EQ 3 bande −20/+6 | max **±27 dBu**; residuo < −97; mix < −89 dBu; gamma dinamica > 116 dB; THD+N 0,0022 % (4V < 0,01 %). MK2: residuo −105, mix −81, isolator +7 con 4 bande SUB 110 / LOW 210 / MID 1,5k / HIGH 3k |
| 7 | Isonoe ISO420 (UK, J. Greenslade) | analogico, a ordinazione, 12"×12" | 2 isolator master assegnabili **> 95 dB di taglio**, **inseriti con relè a gas inerte (true bypass)**; EQ shelving per canale; loop master + send/return con **EQ sui ritorni**; trasformatori d'uscita Lundahl; circuito **a transistor (THD 0,00033 %) o JFET (più seconda armonica) a scelta**; alimentatore lineare esterno | fader −120 dB; diafonia > 90 dB; ±0,2 dB 20-20k; canali appaiati < 0,3 dB (pot selezionati) |
| 8 | AlphaTheta Euphonia (2024) | **ibrido: mix digitale 64 bit + trasformatore Rupert Neve analogico in uscita, colore regolabile** | isolator 3 bande con **Boost Send per banda** (l'effetto su una banda sola); FX interni + send/return | n.p.; €3.799 |
| 9 | Formula Sound FF6000 (con Funktion-One) | analogico 19" | 6 canali, EQ +6 / −25 (100 / 1k / 10k), **2 loop FX con wet/dry e tasti a impulso o fissi**, uscita Zone, gain di canale sul retro | S/N 98 dB; headroom +22 dBu [R]; THD 0,005 % |
| 10 | Union Audio elara.4 MK2 (UK, a mano) | analogico | isolator 3 bande con **incrocio basso variabile sul pannello** (gli utenti lo usavano come gesto); HPF per canale con Q che sale col taglio; aux pre/post; insert master; mic su canale 1 | n.p.; ~€1.720 |

## 3. Mixer live e banchi (0 → 8)

| # | Modello | Perché nel benchmark | Cosa ha | Numeri |
|---|---|---|---|---|
| 1 | MCI di King Tubby (Dynamic Sounds, ~1965, design J. Harned) | dove nasce il dub | 12 ingressi, 4 uscite, 2 ritorni riverbero; **«Big Knob» = filtro passa-alto passivo Altec 9069B, 18 dB/ott., 10-11 scatti da 70 Hz a 7,5 kHz** | — |
| 2 | API 1608 / 1608-II (USA) | banco analogico discreto moderno | op-amp discreti 2520 ovunque, trasformatori, **bus di somma bilanciati** (i vecchi API non lo erano: più rumorosi); 8 aux pre/post in 4 coppie concentriche; 8 ritorni come canali completi; moduli 500 | clip **+28 dBu**; rumore n.p. |
| 3 | Soundcraft Ghost (UK) | banco inglese da studio | in-line con percorso Mix B; EQ 2 medi parametrici + shelving 12k / 60 Hz ±15; **HPF 100 Hz 18 dB/ott.**; 6 aux mono + 2 stereo, 4 ritorni stereo; difetto noto: **alimentatore rumoroso** | uscita diretta −95 dBu (EQ out) / −93 (EQ in) [R] |
| 4 | A&H GL2400 (UK) | live analogico di riferimento | 6 aux pre/post, ponticelli interni pre/post EQ, modo monitor; matrice 7×4; mute e AFL su tutti i master | ingresso mic fino a +34 dBu; uscite **+26 dBu**; EIN −128 |
| 5 | Midas Venice F | preamp mic da live | 6 aux (2 monitor), 2 ritorni stereo, HPF 80 Hz; preamp discreto «long-tailed pair» (eredità XL3) che **satura morbido** se spinto | CMRR 90 dB a 40 dB di gain; Venice originale: ingresso +22 dBu, LED di picco a +16 |
| 6 | Mackie 1604-VLZ4 | il pavimento economico | 4 aux per canale, 16 insert, low-cut 75 Hz 18 dB/ott., EQ 3 bande, **mute −84 dB**, solo pre/post; **bus di somma a terra virtuale** | mix −88,5 dBu (canali giù) / **−82,5 dBu (canali a unità)**; uscita +28 dBu; EIN −128,5 |
| 7 | Black Ark di Lee Perry | dub fatto con poco | prima un mixer «Alice» («giocattoli»), poi un Soundcraft; TEAC 4 piste; Mu-Tron phaser, Echoplex, Space Echo RE201, spring Grantham; **bounce di più piste su una per lo «swirl»** | — |
| 8 | A&H GS-R24 | ibrido analogico studio/live | 6 aux (1-2 pre, 3-4 pre/post, 5-6 post con ponticelli; pre-mute o post-mute a scelta), 4 gruppi, 2 canali valvolari | headroom 21 dB dal nominale, 23 dB al sommatore; mix −93 / −86 / −85 dBu con 0 / 12 / 24 canali; aux −84 dBu; EIN −128,5 |

## 4. Fonti

Preamp: sound-system.fr (lista costruttori; «5 reasons why you should not use
a preamp»; pagina Moses Audio) · mosesaudio.co.uk · dub-siren.com
(RAS-5500) · forum.speakerplans.com (topic 48551, 82844, 97871, 102550) ·
jahtubbys.co.uk/equipment.html · YouTube Axissound (Valv-a-tron) ·
LinkedIn/Facebook BADDRIDDIM · jbkaudio.fr · rdh-hifi.fr ·
sagesound.co.uk (3u, 5u) · abzuelectronics.com (preamps, 5u).

Mixer DJ: brochure Xone:464 (fullcompass.com), B&H, proacousticsusa,
manualslib (Xone:464, Model 1) · playdifferently.org (User Guide 1.4) ·
condesaelectronics.com/products/carmen + rivenditori · bozakusa.com,
Billboard 1976, fabricastronaut blog, Isonoe DLC · Soundcraft 1620LE manual,
gearnews · MasterSounds manuali (Radius 4, 4V), musictech (MK2) ·
isonoe.com/iso420 · djmag, recordcase (Euphonia) · formulasounddirect,
djresource · unionaudio.co.uk, sweetwater · allen-heath.com (Xone:92 Mk2
spec PDF), rivenditori Xone:92/96 · pioneerdj.com, manualslib (DJM-900NXS2),
B&H (V10) · cdn.inmusicbrands.com (manuale MP2015) · musictech, mixdown
(DJR400).

Mixer live: MoPOP (console MCI di Tubby), Red Bull Music Academy, The
Quietus, gearnews (AudioThing Dub Filter) · apiaudio.com (manuale 1608),
Tape Op, Vintage King · Sound On Sound (Ghost, Venice F32, GSR24), brochure
Ghost · B&H (GL2400, GS-R24) · mackie.com (1604VLZ4) · MusicRadar, Tape Op
board, Wikipedia (Black Ark) · allen-heath.com (manuale GS-R24).
