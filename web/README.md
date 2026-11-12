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
| `dsp/*.js` | dispositivi gen~ tradotti in JavaScript | `tools/gen2js.mjs` (da `proto-max/*.genexpr`) |
| `motore.js` | AudioWorklet: canali, mandate, levetta HPF/OFF/LPF, filtri sui bus, MIC, pedali, ritorni, master | a mano |
| `five.worker.js` | il 5-way in un filo di calcolo a parte (16 ms di ritardo, ritorni e mic allineati) | a mano |
| `coi.js` | service worker: dà la memoria condivisa su GitHub Pages, che non manda le intestazioni | a mano |
| `ledvie.js` | LED di livello delle 5 vie (dec. 177) | a mano |
| `costanti.js` | blocco, ritardo e anello, comuni a pagina, motore e Worker | a mano |
| `pedali.js` | eco a nastro, eco ping-pong, molla, riverbero | dai pedali di Federico |
| `tools/prova.mjs` | prova a banco in node: suono, numeri validi, peso | a mano |

Dopo un cambio in `proto-max` o nei pannelli:

```bash
node web/tools/gen2js.mjs && python3 web/tools/pannello.py && node web/tools/prova.mjs
```

## Limiti

- Muti, perché il prototipo non ha il loro dispositivo: MONO 1-3, CUE e cuffie, BOOTH,
  LINE/PHONO.
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
