// Il 5-way in un filo di calcolo a parte: legge il DJ BUS dall'anello condiviso col motore,
// passa MC-5WAY-S (scelte della dec. 175) e riscrive l'uscita. Il motore la legge LAT blocchi dopo.
let five = null;
let ctl, ringIn, ringOut;
const B = 128;
let pk = 0, blocchi = 0;

onmessage = async (ev) => {
  const m = ev.data;
  if (m.t === "avvia") {
    globalThis.sampleRate = m.fs;
    const { Dispositivo } = await import("./dsp/mc-5way-s.js");
    const { ANELLO } = await import("./motore.js");
    five = new Dispositivo();
    for (const k in m.param) five.set(k, m.param[k]);
    ctl = new Int32Array(m.sab, 0, 4);
    ringIn = new Float32Array(m.sab, 16, ANELLO * 2 * B);
    ringOut = new Float32Array(m.sab, 16 + ANELLO * 2 * B * 4, ANELLO * 2 * B);
    giro(ANELLO);
  } else if (m.t === "p" && five) five.set(m.p, m.v);
};

const L = new Float32Array(B), R = new Float32Array(B);
const out = [[new Float32Array(B), new Float32Array(B)]];

async function giro(ANELLO) {
  for (;;) {
    const scritti = Atomics.load(ctl, 0);
    let fatti = Atomics.load(ctl, 1);
    if (scritti - fatti > ANELLO) fatti = scritti - 1; // rimasto indietro: salta avanti

    while (fatti < scritti) {
      const o = (fatti % ANELLO) * 2 * B;
      L.set(ringIn.subarray(o, o + B));
      R.set(ringIn.subarray(o + B, o + 2 * B));
      five.process(L, R, out, B);
      ringOut.set(out[0][0], o);
      ringOut.set(out[0][1], o + B);
      for (let k = 0; k < B; k++) pk = Math.max(pk, Math.abs(out[0][0][k]), Math.abs(out[0][1][k]));
      fatti++;
      Atomics.store(ctl, 1, fatti);

      if (++blocchi >= 12) {
        postMessage({ five: pk });
        pk = 0;
        blocchi = 0;
      }
    }
    // aspetta il blocco dopo senza bloccare i messaggi (i comandi delle manopole)
    const r = Atomics.waitAsync(ctl, 0, scritti, 50);
    if (r.async) await r.value;
  }
}
