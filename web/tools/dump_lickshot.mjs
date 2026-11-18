// Fa suonare la LICKSHOT del banco web col copione di prova_lickshot.py e scrive i campioni.
// Uso: node web/tools/dump_lickshot.mjs <file.json>  poi  python3 proto-max/coefficienti/prova_lickshot.py --web <file.json>
import { writeFileSync } from "node:fs";
import { Lickshot } from "../strumenti.js";
const FS = 48000;
const passi = [[0.0, { trig: 1 }], [0.6, { alt: 30, vel: 90 }], [0.9, { tempo: 20, rip: 80, eco: 90 }],
  [1.3, { trig: 0 }], [1.5, { lfo: 0, trig: 1 }], [1.7, { trig: 0, lfo: 1 }], [1.9, { vol: 40, trig: 1 }]];
const l = new Lickshot(FS), out = [], uno = new Float64Array(1);
let j = 0;
for (let i = 0; i < Math.floor(2.2 * FS); i++) {
  while (j < passi.length && i >= passi[j][0] * FS) { for (const [k, v] of Object.entries(passi[j][1])) l.set(k, v); j++; }
  l.process(uno, 1);
  out.push(uno[0]);
}
writeFileSync(process.argv[2], JSON.stringify(out));
