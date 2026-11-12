// LED di livello delle 5 vie, come nell'hardware (dec. 176 g e 177,
// docs/fase2/five-way-led-livello.md): legge l'uscita del 5-way dopo il drive, somma (L+R)/2,
// banco d'analisi Butterworth del 2o ordine agli incroci H (60 / 250 / 1200 / 8000 Hz),
// rivelatore di picco con rilascio 0,3 s, soglie all'uscita del modulo
// verde -18 dBu, giallo +12, rosso +18, rosso tenuto 0,52 s.
// Banco da lettura: non tocca il suono.

const VP_0DBU = 1.0957; // picco di 0 dBu
const V_FS = 4.3609;    // campione 1,0 = 4,36 V di picco (come il meter del 5-way in app.js)
const soglia = (dbu) => (VP_0DBU * Math.pow(10, dbu / 20)) / V_FS;
const S_VERDE = soglia(-18), S_GIALLO = soglia(12), S_ROSSO = soglia(18);

// cella del 2o ordine, Q 0,707, bilineare con prewarp
function cella(tipo, f, fs) {
  const w = (2 * Math.PI * f) / fs;
  const cw = Math.cos(w), al = Math.sin(w) / (2 * Math.SQRT1_2);
  const a0 = 1 + al;
  const b = tipo === "lp" ? [(1 - cw) / 2, 1 - cw, (1 - cw) / 2] : [(1 + cw) / 2, -(1 + cw), (1 + cw) / 2];
  return { b0: b[0] / a0, b1: b[1] / a0, b2: b[2] / a0, a1: (-2 * cw) / a0, a2: (1 - al) / a0, z1: 0, z2: 0 };
}
function passa(c, x) {
  const y = c.b0 * x + c.z1;
  c.z1 = c.b1 * x - c.a1 * y + c.z2;
  c.z2 = c.b2 * x - c.a2 * y;
  return y;
}

export class LedVie {
  constructor(fs) {
    this.vie = [
      [cella("lp", 60, fs)],
      [cella("hp", 60, fs), cella("lp", 250, fs)],
      [cella("hp", 250, fs), cella("lp", 1200, fs)],
      [cella("hp", 1200, fs), cella("lp", 8000, fs)],
      [cella("hp", 8000, fs)],
    ];
    this.hold = new Float64Array(5);
    this.rosso = new Int32Array(5); // campioni di rosso ancora da tenere
    this.stato = new Int32Array(5); // massimo dal meter prima: 0 spento, 1 verde, 2 giallo, 3 rosso
    this.rilascio = Math.exp(-1 / (0.3 * fs));
    this.latch = Math.round(0.52 * fs);
  }

  process(L, R, n) {
    for (let v = 0; v < 5; v++) {
      const celle = this.vie[v];
      let h = this.hold[v], r = this.rosso[v], st = this.stato[v];
      for (let k = 0; k < n; k++) {
        let y = (L[k] + R[k]) * 0.5;
        for (let c = 0; c < celle.length; c++) y = passa(celle[c], y);
        y = Math.abs(y);
        h = y > h ? y : h * this.rilascio;
        if (h >= S_ROSSO) r = this.latch;
        else if (r > 0) r--;
        const s = r > 0 ? 3 : h >= S_GIALLO ? 2 : h >= S_VERDE ? 1 : 0;
        if (s > st) st = s;
      }
      // un valore rotto non blocca il LED acceso
      if (!(h < 1e6)) { h = 0; for (const c of celle) c.z1 = c.z2 = 0; }
      this.hold[v] = h;
      this.rosso[v] = r;
      this.stato[v] = st;
    }
  }

  // stato dei 5 LED dal meter prima, poi riparte da zero
  leggi() {
    const s = Array.from(this.stato);
    this.stato.fill(0);
    return s;
  }
}
