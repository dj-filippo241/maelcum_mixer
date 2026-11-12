#!/usr/bin/env node
// Prova a banco del motore, senza browser: 10 s di rumore rosa e un'onda sui quattro deck,
// fader su, mandate e ritorni aperti, filtro e 5-way in uso. Controlla che l'uscita sia un numero,
// che il suono passi e quanto tempo di calcolo serve (carico = tempo di calcolo / tempo reale).
// Uso: node web/tools/prova.mjs

globalThis.sampleRate = 48000;
const { Mixer } = await import("../motore.js");

const fs = 48000;
const secondi = 10;
const n = fs * 2;
const tracce = [0, 1, 2, 3].map((i) => {
  const L = new Float32Array(n), R = new Float32Array(n);
  let b0 = 0, b1 = 0, b2 = 0;
  for (let k = 0; k < n; k++) {
    const w = Math.random() * 2 - 1;
    b0 = 0.99765 * b0 + w * 0.099; b1 = 0.963 * b1 + w * 0.2965; b2 = 0.57 * b2 + w * 1.0527;
    const rosa = (b0 + b1 + b2 + w * 0.1848) * 0.05;
    const tono = 0.2 * Math.sin((2 * Math.PI * 55 * (i + 1) * k) / fs);
    L[k] = rosa + tono;
    R[k] = rosa * 0.9 + tono;
  }
  return { L, R };
});

const mx = new Mixer(fs);
const c = (m) => mx.comando(m);
tracce.forEach((t, i) => c({ t: "traccia", i, L: t.L, R: t.R }));
for (let i = 0; i < 4; i++) {
  c({ t: "p", dev: "ch", i, p: "fader", v: 80 });
  c({ t: "p", dev: "send", i, p: "level", v: 60 });
  c({ t: "p", dev: "send", i, p: `as${i + 1}`, v: 1 });
  c({ t: "faderRet", i, v: 70 });
  c({ t: "p", dev: "ret", i, p: "rr" + (i + 1), v: 30 });
}
c({ t: "modo", i: 1, v: 0 });
c({ t: "modo", i: 2, v: 2 });
c({ t: "p", dev: "hpf", p: "freq_hp", v: 40 });
c({ t: "p", dev: "lpf", p: "freq_lp", v: 60 });
c({ t: "p", dev: "lpf", p: "res_lp", v: 50 });
c({ t: "p", dev: "five", p: "growl", v: 30 });
c({ t: "play", on: true });

const out = [new Float32Array(128), new Float32Array(128)];
const blocchi = Math.ceil((secondi * fs) / 128);
let rms = 0, maxAbs = 0, nan = 0;
const t0 = performance.now();
for (let b = 0; b < blocchi; b++) {
  mx.blocco(null, null, out);
  for (let k = 0; k < 128; k++) {
    const v = out[0][k];
    if (!Number.isFinite(v)) nan++;
    rms += v * v;
    maxAbs = Math.max(maxAbs, Math.abs(v));
  }
  if (b === blocchi - 1) var m = mx.meter();
}
const ms = performance.now() - t0;
rms = Math.sqrt(rms / (blocchi * 128));

// Nel browser il 5-way gira in un Worker: si misurano a parte il motore senza 5-way e il 5-way
// con GROWL e NASTRO a metà (il caso più pesante che si usa).
const { ANELLO } = await import("../motore.js");
const mx2 = new Mixer(fs, new SharedArrayBuffer(16 + 2 * ANELLO * 2 * 128 * 4));
for (const [i, t] of tracce.entries()) mx2.comando({ t: "traccia", i, L: t.L, R: t.R });
mx2.comando({ t: "play", on: true });
let t1 = performance.now();
for (let b = 0; b < blocchi; b++) mx2.blocco(null, null, out);
const caricoMotore = (performance.now() - t1) / 1000 / secondi;
const { Dispositivo: Five } = await import("../dsp/mc-5way-s.js");
const f5 = new Five();
f5.set("growl", 50);
f5.set("nastro", 50);
const iL = tracce[0].L.subarray(0, 128), iR = tracce[0].R.subarray(0, 128);
t1 = performance.now();
for (let b = 0; b < blocchi; b++) f5.process(iL, iR, [out], 128);
const caricoFive = (performance.now() - t1) / 1000 / secondi;
const dB = (x) => (20 * Math.log10(x + 1e-12)).toFixed(1);
console.log(`tutto in un filo: ${secondi} s di audio in ${(ms / 1000).toFixed(2)} s -> carico ${((ms / 1000 / secondi) * 100).toFixed(0)} %`);
console.log(`nel browser: motore senza 5-way ${(caricoMotore * 100).toFixed(0)} %, 5-way-S nel Worker (GROWL e NASTRO a metà) ${(caricoFive * 100).toFixed(0)} %`);
console.log(`uscita: rms ${dB(rms)} dBFS, picco ${dB(maxAbs)} dBFS, campioni non numerici ${nan}`);
console.log(`meter: deck ${m.deck.map((x) => dB(x)).join(" / ")} dBFS · 5-way ${dB(m.five)} · ritorni ${m.ret.map((x) => x.toFixed(2)).join(" / ")} · master ${m.master.map((x) => x.toFixed(2)).join(" / ")} · protezione ${m.prot.toFixed(2)}`);
const ok = nan === 0 && rms > 1e-4 && caricoMotore < 0.6 && caricoFive < 0.85;
console.log(ok ? "PROVA PASSA" : "PROVA NON PASSA");
process.exit(ok ? 0 : 1);
