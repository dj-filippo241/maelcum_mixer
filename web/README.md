# web/ — banco del mixer nel browser

Versione leggera, da prova, del progetto di Federico (`stellakamikaze/maelcum-soundsystem`,
12/11/2026): solo la vista dall'alto, il pannello della disposizione F e i quattro pedali FX
accanto. Grafica minima, nessun pacchetto da installare. Il suono è il codice gen~ di
`proto-max`, versioni `-S` con le ultime scelte (canale: dec. 152, 162, 168; filtro sui bus:
dec. 148, 153, 159; 5-way: dec. 175).

## Aprirlo

Online, senza installare niente: https://dj-filippo241.github.io/maelcum_mixer/web/

In locale:

```bash
python3 web/servi.py
```

Si apre `http://localhost:8765`. Poi **Accendi** e **Play**. Il server manda le intestazioni
che danno alla pagina la memoria condivisa: senza, il 5-way gira nello stesso filo del resto e
con GROWL e NASTRO alzati il suono si interrompe.

## Cosa c'è

| File | Cosa fa | Nasce da |
|---|---|---|
| `index.html`, `app.js` | pannello SVG, comandi, tracce, meter | a mano |
| `pannello.json` | posizione di ogni comando in mm | `tools/pannello.py` (da `docs/pannelli/proposta_f.py`) |
| `dsp/*.js` | dispositivi gen~ tradotti in JavaScript; il 5-way anche un lato per file (`-l`, `-r`) | `tools/gen2js.mjs` (da `proto-max/*.genexpr`) |
| `motore.js` | AudioWorklet: canali, mandate, levetta HPF/OFF/LPF, filtri sui bus, MIC, pedali, ritorni, master | a mano |
| `five.worker.js` | il 5-way in due fili di calcolo a parte, uno per lato L e R (16 ms di ritardo, ritorni e mic allineati) | a mano |
| `coi.js` | service worker: dà la memoria condivisa su GitHub Pages, che non manda le intestazioni | a mano |
| `strumenti.js` | sirena NJD (dallo schema ridisegnato da Zen Instruments) e LICKSHOT (struttura del firmware open source xioTechnologies/Dub-Siren) | a mano |
| `ledvie.js` | LED di livello delle 5 vie (dec. 177) | a mano |
| `costanti.js` | blocco, ritardo, anello e mappa della memoria condivisa, comuni a pagina, motore e Worker | a mano |
| `pedali.js` | eco a nastro, eco ping-pong, molla, riverbero | dai pedali di Federico |
| `tools/prova.mjs` | prova a banco in node: suono, numeri validi, peso | a mano |

Dopo un cambio in `proto-max` o nei pannelli:

```bash
node web/tools/gen2js.mjs && python3 web/tools/pannello.py && node web/tools/prova.mjs
```

## Peso (2026-11-13)

Misurato in node su un M3 Max, in % di un core, con GROWL e NASTRO a metà:

| | prima | ora |
|---|---|---|
| 5-way, filo più carico | 66-71 % (un Worker) | 27 % (due Worker, uno per lato) |
| motore senza 5-way | 37 % | 34 % |

Cosa è cambiato, senza togliere funzioni:
- il banco gira sempre a 48 kHz (il browser converte verso la scheda audio): a 96 kHz il 5-way
  costava il doppio;
- i due lati di MC-5WAY-S non hanno niente in comune: due Worker, uno per lato. Somma dei lati
  uguale al dispositivo intero campione per campione;
- i Worker aspettano con `Atomics.wait` e leggono le manopole dalla memoria condivisa: niente
  `Atomics.waitAsync`, che Firefox non ha;
- il Newton del JFET del NASTRO si ferma quando il passo è sotto 1e-9 relativo: uscita uguale a
  32 bit su tutti i 9 dispositivi (confronto con manopole in movimento);
- meter e LED toccano la grafica solo quando cambiano.

## Limiti

- Muti, perché il prototipo non ha il loro dispositivo: CUE e cuffie, BOOTH, LINE/PHONO.
- MONO 1-3 suonano con MC-MONO (generato da `genera_mic.py`, mic-mono-moduli §4-§5). Nel jack
  del MONO 1 c'è la sirena NJD, nel MONO 2 la LICKSHOT (`strumenti.js`, riquadri sotto i
  pedali, tasti 1, 2, 3). Il MONO 3 non ha sorgente.
- LED delle cinque vie: non vengono dal prototipo ma da `ledvie.js`, che rifà il circuito della
  dec. 177 (banco d'analisi agli incroci H sull'uscita del 5-way, somma L+R, soglie −18 / +12 /
  +18 dBu, rilascio 0,3 s, rosso tenuto 0,52 s). Aggiunti il 2026-11-12.
- Il meter del canale legge dopo il fader (nell'hardware è prima, dec. 161).
- Fader dei ritorni con la legge di Federico (−12 dB a metà corsa).
- Il riddim di prova è sintetico (75 BPM, una battuta per deck); una traccia vera si trascina
  su una striscia CDJ.

Revisione del 2026-11-12 (quattro agenti): collegamenti dei 185 comandi controllati uno per uno;
JavaScript contro modello Python sugli 8 dispositivi, scarto ≤ 3e-13; pedali uguali bit per bit a
quelli di Federico. Non provato: Safari, Firefox, telefono e tablet.

Verificato in: node (prova a banco) sì / browser (Yab, la pagina suona, nessun blocco perso con
GROWL e NASTRO a metà) sì / ascolto di Filippo no.
