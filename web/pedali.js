// I quattro pedali dei bus FX. Non fanno parte del mixer: in Live erano effetti di Live
// (montaggio.md, P3). Vengono dai pedali di Federico (maelcum-soundsystem, src/engine/pedali.ts,
// 12/11/2026), tradotti in JavaScript senza cambiare il suono. Stereo, 100 % wet.
// Due manopole per pedale: a e b, da 0 a 100.

const BPM_PARTENZA = 120;
const RITARDO_MAX = 3; // secondi
const sat = (x) => Math.tanh(x * 0.9) / 0.9;

class Linea {
  constructor(max) {
    this.buf = new Float32Array(max);
    this.w = 0;
  }
  leggi(ritardo) {
    const n = this.buf.length;
    const p = this.w - ritardo;
    const i = Math.floor(p);
    const f = p - i;
    const a = this.buf[((i % n) + n) % n];
    const b = this.buf[(((i + 1) % n) + n) % n];
    return a + (b - a) * f;
  }
  scrivi(x) {
    this.buf[this.w] = x;
    this.w = (this.w + 1) % this.buf.length;
  }
}

// Eco a nastro: ritardo che scivola verso il TEMPO, passa-banda nell'anello, saturazione.
class Eco {
  constructor(nome, fs, pingpong, battiti) {
    this.nome = nome;
    this.manopole = ["TEMPO", "RIPETIZIONI"];
    this.a = 50;
    this.b = 45;
    this.fs = fs;
    this.pingpong = pingpong;
    this.battiti = battiti;
    this.lL = new Linea(Math.ceil(fs * RITARDO_MAX) + 2);
    this.lR = new Linea(Math.ceil(fs * RITARDO_MAX) + 2);
    this.tempoBase = (battiti * 60) / BPM_PARTENZA;
    this.rit = this.tempoSecondi() * fs;
    this.lpL = this.lpR = this.hpL = this.hpR = 0;
  }
  bpm(v) {
    this.tempoBase = (this.battiti * 60) / v;
  }
  tempoSecondi() {
    return Math.min(RITARDO_MAX, this.tempoBase * Math.pow(2, (this.a - 50) / 50));
  }
  elabora(inL, inR, outL, outR, n) {
    const meta = this.tempoSecondi() * this.fs;
    const fb = Math.min(1.08, (this.b / 100) * 1.1);
    const clp = 1 - Math.exp((-2 * Math.PI * 2600) / this.fs);
    const chp = 1 - Math.exp((-2 * Math.PI * 140) / this.fs);
    for (let k = 0; k < n; k++) {
      this.rit += (meta - this.rit) * 0.00012;
      const yL = this.lL.leggi(this.rit);
      const yR = this.lR.leggi(this.rit);
      this.lpL += (yL - this.lpL) * clp;
      this.lpR += (yR - this.lpR) * clp;
      this.hpL += (this.lpL - this.hpL) * chp;
      this.hpR += (this.lpR - this.hpR) * chp;
      const rL = sat((this.lpL - this.hpL) * fb);
      const rR = sat((this.lpR - this.hpR) * fb);
      if (this.pingpong) {
        this.lL.scrivi(0.5 * (inL[k] + inR[k]) + rR);
        this.lR.scrivi(rL);
      } else {
        this.lL.scrivi(inL[k] + rL);
        this.lR.scrivi(inR[k] + rR);
      }
      outL[k] = yL;
      outR[k] = yR;
    }
  }
}

// Molla: catena di allpass (il "boing") e anello di ritardo corto con perdite.
class Molla {
  constructor(nome, fs) {
    this.nome = nome;
    this.manopole = ["CODA", "TONO"];
    this.a = 55;
    this.b = 50;
    this.fs = fs;
    this.ap = [new Float32Array(48), new Float32Array(48)];
    this.lin = [new Linea(Math.ceil(fs * 0.2)), new Linea(Math.ceil(fs * 0.2))];
    this.lp = [0, 0];
  }
  elabora(inL, inR, outL, outR, n) {
    const coda = 0.55 + 0.42 * (this.a / 100);
    const c = 1 - Math.exp((-2 * Math.PI * (900 + 5000 * (this.b / 100))) / this.fs);
    const g = 0.62;
    const ritardi = [0.0337 * this.fs, 0.0411 * this.fs];
    for (let ch = 0; ch < 2; ch++) {
      const inp = ch === 0 ? inL : inR;
      const out = ch === 0 ? outL : outR;
      const s = this.ap[ch];
      const lin = this.lin[ch];
      for (let k = 0; k < n; k++) {
        let x = inp[k] + lin.leggi(ritardi[ch]) * coda;
        for (let j = 0; j < 24; j++) {
          const y = -g * x + s[2 * j] + g * s[2 * j + 1];
          s[2 * j] = x;
          s[2 * j + 1] = y;
          x = y;
        }
        this.lp[ch] += (x - this.lp[ch]) * c;
        lin.scrivi(sat(this.lp[ch]));
        out[k] = this.lp[ch];
      }
    }
  }
}

// Riverbero lungo: Freeverb (8 comb con passa-basso + 4 allpass per lato).
class Riverbero {
  constructor(nome, fs) {
    this.nome = nome;
    this.manopole = ["CODA", "TONO"];
    this.a = 60;
    this.b = 45;
    const k = fs / 44100;
    const cl = [1116, 1188, 1277, 1356, 1422, 1491, 1557, 1617];
    const al = [556, 441, 341, 225];
    this.comb = [0, 23].map((sp) => cl.map((l) => ({ buf: new Float32Array(Math.round((l + sp) * k)), i: 0, f: 0 })));
    this.all = [0, 23].map((sp) => al.map((l) => ({ buf: new Float32Array(Math.round((l + sp) * k)), i: 0 })));
  }
  elabora(inL, inR, outL, outR, n) {
    const room = 0.7 + 0.28 * (this.a / 100);
    const damp = 0.15 + 0.6 * (1 - this.b / 100);
    for (let ch = 0; ch < 2; ch++) {
      const out = ch === 0 ? outL : outR;
      const cs = this.comb[ch];
      const as = this.all[ch];
      for (let k = 0; k < n; k++) {
        const x = (inL[k] + inR[k]) * 0.015;
        let y = 0;
        for (const c of cs) {
          const o = c.buf[c.i];
          c.f = o * (1 - damp) + c.f * damp;
          c.buf[c.i] = x + c.f * room;
          c.i = (c.i + 1) % c.buf.length;
          y += o;
        }
        for (const a of as) {
          const b = a.buf[a.i];
          a.buf[a.i] = y + b * 0.5;
          a.i = (a.i + 1) % a.buf.length;
          y = b - y;
        }
        out[k] = y;
      }
    }
  }
}

export const NOMI_PEDALI = [
  ["ECO A NASTRO", "TEMPO", "RIPETIZIONI", 50, 45],
  ["ECO PING-PONG", "TEMPO", "RIPETIZIONI", 50, 45],
  ["MOLLA", "CODA", "TONO", 55, 50],
  ["RIVERBERO", "CODA", "TONO", 60, 45],
];

export function creaPedali(fs) {
  return [
    new Eco("ECO A NASTRO", fs, false, 1.5),
    new Eco("ECO PING-PONG", fs, true, 1),
    new Molla("MOLLA", fs),
    new Riverbero("RIVERBERO", fs),
  ];
}
