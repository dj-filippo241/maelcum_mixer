// Il 5-way in un filo di calcolo a parte: legge il DJ BUS dall'anello condiviso col motore,
// passa MC-5WAY-S (scelte della dec. 175) e riscrive l'uscita. Il motore la legge LAT blocchi dopo.
let five = null;
let ctl, ringIn, ringOut;
const B = 128;
const coda = []; // manopole mosse mentre il Worker si carica

onmessage = async (ev) => {
  const m = ev.data;
  if (m.t === "avvia") {
    globalThis.sampleRate = m.fs;
    const { Dispositivo } = await import("./dsp/mc-5way-s.js");
    const { ANELLO, LAT } = await import("./costanti.js");
    five = new Dispositivo();
    for (const k in m.param) five.set(k, m.param[k]);
    for (const q of coda) five.set(q.p, q.v);
    ctl = new Int32Array(m.sab, 0, 4);
    ringIn = new Float32Array(m.sab, 16, ANELLO * 2 * B);
    ringOut = new Float32Array(m.sab, 16 + ANELLO * 2 * B * 4, ANELLO * 2 * B);
    giro(ANELLO, LAT).catch((e) => postMessage({ errore: String(e) }));
  } else if (m.t === "p") five ? five.set(m.p, m.v) : coda.push(m);
};

const L = new Float32Array(B), R = new Float32Array(B);
const out = [[new Float32Array(B), new Float32Array(B)]];

async function giro(ANELLO, LAT) {
  for (;;) {
    const scritti = Atomics.load(ctl, 0);
    let fatti = Atomics.load(ctl, 1);
    // Rimasto indietro: salta i blocchi che il motore ha già dato per persi (legge scritti - LAT).
    // Non li dichiara fatti: il motore non legge mai una casella saltata.
    if (fatti < scritti - LAT) fatti = scritti - LAT;

    while (fatti < scritti) {
      const o = (fatti % ANELLO) * 2 * B;
      L.set(ringIn.subarray(o, o + B));
      R.set(ringIn.subarray(o + B, o + 2 * B));
      five.process(L, R, out, B);
      ringOut.set(out[0][0], o);
      ringOut.set(out[0][1], o + B);
      fatti++;
      Atomics.store(ctl, 1, fatti);

    }
    // aspetta il blocco dopo senza bloccare i messaggi (i comandi delle manopole)
    const r = Atomics.waitAsync(ctl, 0, scritti, 50);
    if (r.async) await r.value;
  }
}
