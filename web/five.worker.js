// Un lato del 5-way (L o R) in un filo di calcolo a parte. I due lati di MC-5WAY-S non hanno
// niente in comune (dsp/mc-5way-s-l.js e -r.js, dallo stesso genexpr): due Worker dimezzano il
// peso per filo. Legge il DJ BUS dall'anello condiviso col motore, riscrive il suo canale.
// Aspetta col blocco di Atomics.wait (va in tutti i browser con la memoria condivisa, Firefox
// compreso) e legge le manopole dalla memoria condivisa: nessun messaggio durante il giro.
onmessage = async (ev) => {
  const m = ev.data;
  if (m.t !== "avvia") return;
  try {
    globalThis.sampleRate = m.fs;
    const { Dispositivo } = await import(`./dsp/mc-5way-s-${m.lato}.js`);
    const { B, ANELLO, LAT, viste } = await import("./costanti.js");
    giro(new Dispositivo(), viste(m.sab), m.lato === "l" ? 0 : 1, m.chiavi, B, ANELLO, LAT);
  } catch (e) {
    postMessage({ errore: String(e) });
  }
};

function giro(five, { ctl, par, ringIn, ringOut }, c, chiavi, B, ANELLO, LAT) {
  const L = new Float32Array(B), R = new Float32Array(B);
  const out = [[new Float32Array(B), new Float32Array(B)]];
  const mio = 1 + c;
  let versione = -1;
  for (;;) {
    const v = Atomics.load(ctl, 3);
    if (v !== versione) {
      versione = v;
      chiavi.forEach((k, i) => five.set(k, par[i]));
    }
    const scritti = Atomics.load(ctl, 0);
    let fatti = Atomics.load(ctl, mio);
    // Rimasto indietro: salta i blocchi che il motore ha già dato per persi (legge scritti - LAT).
    if (fatti < scritti - LAT) fatti = scritti - LAT;
    while (fatti < scritti) {
      const o = (fatti % ANELLO) * 2 * B;
      L.set(ringIn.subarray(o, o + B));
      R.set(ringIn.subarray(o + B, o + 2 * B));
      five.process(L, R, out, B);
      ringOut.set(out[0][c], o + c * B);
      fatti++;
      Atomics.store(ctl, mio, fatti);
    }
    Atomics.wait(ctl, 0, scritti, 50);
  }
}
