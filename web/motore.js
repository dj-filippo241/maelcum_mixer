// Il motore audio: un solo AudioWorklet che chiama in fila i dispositivi del prototipo
// (proto-max, tradotti da tools/gen2js.mjs) col cablaggio del mixer di oggi:
//
//   deck i -> MC-CHANNEL-S -> MC-SEND -> levetta HPF / OFF / LPF (dip di 3 ms, dec. 163)
//        OFF -> DJ BUS ; HPF -> bus HPF -> MC-FILTRO-HPF -> DJ BUS ; LPF -> bus LPF -> MC-FILTRO-LPF -> DJ BUS
//   DJ BUS -> MC-5WAY-S (scelte della dec. 175) -> somma master. Il 5-way gira in due Worker,
//   uno per lato (five.worker.js), quando la pagina ha la memoria condivisa: arriva LAT blocchi dopo, e
//   ritorni e mic si ritardano dello stesso tempo.
//   mandate (MC-SEND, MC-MIC) + reroute dei ritorni -> bus FX 1-4 -> pedale -> MC-RET -> fader -> somma master
//   MC-MIC -> somma master
//   somma master -> MC-MASTER -> protezione per le orecchie (-1 dBFS, fuori dal design) -> uscita
//
// LED delle 5 vie: banco d'analisi sull'uscita del 5-way (ledvie.js, dec. 177).
//   strumenti (strumenti.js: NJD, LICKSHOT) -> MC-MONO 1 e 2 (MONO 3 senza sorgente) -> somma master + bus FX
// Il CUE, BOOTH e LINE/PHONO non hanno un dispositivo nel prototipo: restano muti.

import { Dispositivo as Canale } from "./dsp/mc-channel-s.js";
import { Dispositivo as Send } from "./dsp/mc-send.js";
import { Dispositivo as FiltroHPF } from "./dsp/mc-filtro-hpf.js";
import { Dispositivo as FiltroLPF } from "./dsp/mc-filtro-lpf.js";
import { Dispositivo as FiveS } from "./dsp/mc-5way-s.js";
import { Dispositivo as Ret } from "./dsp/mc-ret.js";
import { Dispositivo as Mic } from "./dsp/mc-mic.js";
import { Dispositivo as Mono } from "./dsp/mc-mono.js";
import { Njd, Lickshot } from "./strumenti.js";
import { Dispositivo as Master } from "./dsp/mc-master.js";
import { creaPedali } from "./pedali.js";
import { LedVie } from "./ledvie.js";

import { B, LAT, ANELLO, viste } from "./costanti.js";
export { LAT, ANELLO };
const st = () => [new Float32Array(B), new Float32Array(B)];
const cinque = () => [st(), st(), st(), st(), st()];
const ZERO = new Float32Array(B);

function picco(a, b) {
  let m = 0;
  for (let k = 0; k < B; k++) {
    const v = Math.max(Math.abs(a[k]), Math.abs(b[k]));
    if (v > m) m = v;
  }
  return m;
}

export class Mixer {
  // sab: memoria condivisa coi due Worker del 5-way, lato L e lato R (null = 5-way qui dentro)
  constructor(fs, sab = null) {
    this.fs = fs;
    this.esterno = !!sab;
    if (sab) {
      Object.assign(this, viste(sab)); // ctl, par, ringIn, ringOut (costanti.js)
      this.n = 0;
      this.ritardo = Array.from({ length: LAT }, () => st());
      this.persi = 0;
    }
    this.deck = [0, 1, 2, 3].map(() => ({
      ch: new Canale(), send: new Send(), L: null, R: null, pos: 0,
      inp: st(), oCh: st(), oSn: cinque(),
      modo: 1, modoVoluto: 1, gModo: 1, pk: 0,
    }));
    for (const d of this.deck) d.ch.set("fader", 0); // fader giù all'accensione
    this.hpf = new FiltroHPF();
    this.lpf = new FiltroLPF();
    this.lpf.set("freq_lp", 100); // LPF aperto
    this.fiveS = this.esterno ? null : new FiveS();
    this.mic = new Mic();
    this.monos = [0, 1, 2].map(() => new Mono());
    this.strum = [new Njd(fs), new Lickshot(fs)];
    this.inMono = [new Float32Array(B), new Float32Array(B), new Float32Array(B)];
    this.oMono = this.monos.map(() => cinque());
    this.ledMono = [0, 0, 0];
    this.rets = [0, 1, 2, 3].map(() => new Ret());
    this.master = new Master();
    this.pedali = creaPedali(fs);
    this.faderRet = [0, 0, 0, 0];
    this.gRet = [0, 0, 0, 0];
    this.suona = false;
    this.prot = 1;

    this.busHPF = st();
    this.busLPF = st();
    this.dj = st();
    this.daPulire = [this.busHPF, this.busLPF, this.dj];
    this.oHPF = st();
    this.oLPF = st();
    this.oFive = st();
    this.oMic = cinque();
    this.bus = [st(), st(), st(), st()];
    this.ped = [st(), st(), st(), st()];
    this.oRet = this.rets.map(() => cinque());
    this.rerPrec = [st(), st(), st(), st()];
    this.somma = st();
    this.oMs = st();
    this.pkFive = 0;
    this.pkRet = [0, 0, 0, 0];
    this.clipRet = [0, 0, 0, 0];
    this.pkMaster = [0, 0];
    this.clipMaster = [0, 0];
    this.led = 0;
    this.ledVie = new LedVie(fs);
  }

  comando(m) {
    if (m.t === "p") {
      if (m.dev === "ch") this.deck[m.i].ch.set(m.p, m.v);
      else if (m.dev === "send") this.deck[m.i].send.set(m.p, m.v);
      else if (m.dev === "hpf") this.hpf.set(m.p, m.v);
      else if (m.dev === "lpf") this.lpf.set(m.p, m.v);
      else if (m.dev === "five") {
        if (this.fiveS) this.fiveS.set(m.p, m.v);
      } else if (m.dev === "ret") this.rets[m.i].set(m.p, m.v);
      else if (m.dev === "mic") this.mic.set(m.p, m.v);
      else if (m.dev === "mono") this.monos[m.i].set(m.p, m.v);
      else if (m.dev === "master") this.master.set(m.p, m.v);
    } else if (m.t === "modo") this.deck[m.i].modoVoluto = m.v;
    else if (m.t === "faderRet") this.faderRet[m.i] = m.v;
    else if (m.t === "pedale") this.pedali[m.i][m.k] = m.v;
    else if (m.t === "strum") this.strum[m.i].set(m.k, m.v);
    else if (m.t === "bpm") for (const p of this.pedali) p.bpm?.(m.v);
    else if (m.t === "interno") {
      // il Worker del 5-way non è partito: il 5-way torna qui dentro
      if (this.esterno) {
        this.esterno = false;
        this.fiveS = new FiveS();
      }
    } else if (m.t === "traccia") {
      if (!m.L || !m.L.length) return;
      const d = this.deck[m.i];
      d.L = m.L;
      d.R = m.R;
      d.pos = 0;
    } else if (m.t === "play") {
      this.suona = m.on;
      if (m.riavvolgi) for (const d of this.deck) d.pos = 0;
    }
  }

  // un blocco da 128 campioni: micL/micR = ingresso del microfono, out = [L, R]
  blocco(micL, micR, out) {
    for (const a of this.daPulire) {
      a[0].fill(0);
      a[1].fill(0);
    }
    // bus FX: partono dal reroute del blocco prima (un blocco di ritardo nell'anello)
    for (let b = 0; b < 4; b++) {
      this.bus[b][0].set(this.rerPrec[b][0]);
      this.bus[b][1].set(this.rerPrec[b][1]);
    }

    const passoDip = 1 / (0.0015 * this.fs); // 1,5 ms giù, 1,5 ms su
    for (const d of this.deck) {
      if (this.suona && d.L) {
        const n = d.L.length;
        for (let k = 0; k < B; k++) {
          d.inp[0][k] = d.L[d.pos];
          d.inp[1][k] = d.R[d.pos];
          if (++d.pos >= n) d.pos = 0;
        }
      } else {
        d.inp[0].fill(0);
        d.inp[1].fill(0);
      }
      d.ch.process(d.inp[0], d.inp[1], [d.oCh], B);
      d.send.process(d.oCh[0], d.oCh[1], d.oSn, B);
      d.pk = Math.max(d.pk, picco(d.oCh[0], d.oCh[1]));
      for (let b = 0; b < 4; b++) {
        const s = d.oSn[b + 1];
        const bb = this.bus[b];
        for (let k = 0; k < B; k++) {
          bb[0][k] += s[0][k];
          bb[1][k] += s[1][k];
        }
      }
      for (let k = 0; k < B; k++) {
        if (d.modo !== d.modoVoluto) {
          d.gModo -= passoDip;
          if (d.gModo <= 0) {
            d.gModo = 0;
            d.modo = d.modoVoluto;
          }
        } else if (d.gModo < 1) d.gModo = Math.min(1, d.gModo + passoDip);
        const dst = d.modo === 0 ? this.busHPF : d.modo === 2 ? this.busLPF : this.dj;
        dst[0][k] += d.oSn[0][0][k] * d.gModo;
        dst[1][k] += d.oSn[0][1][k] * d.gModo;
      }
    }

    this.hpf.process(this.busHPF[0], this.busHPF[1], [this.oHPF], B);
    this.lpf.process(this.busLPF[0], this.busLPF[1], [this.oLPF], B);
    for (let k = 0; k < B; k++) {
      this.dj[0][k] += this.oHPF[0][k] + this.oLPF[0][k];
      this.dj[1][k] += this.oHPF[1][k] + this.oLPF[1][k];
    }
    if (this.esterno) this.fiveFuori();
    else this.fiveS.process(this.dj[0], this.dj[1], [this.oFive], B);
    this.pkFive = Math.max(this.pkFive, picco(this.oFive[0], this.oFive[1]));
    this.ledVie.process(this.oFive[0], this.oFive[1], B);

    this.mic.process(micL || ZERO, micR || micL || ZERO, this.oMic, B);
    this.led = Math.max(this.led, this.mic.meter[0]);
    // strumenti nei MONO: volt al jack -> scala di MC-MONO (1,0 = 4,36 V, fx.LIV)
    for (let j = 0; j < 2; j++) {
      this.strum[j].process(this.inMono[j], B);
      for (let k = 0; k < B; k++) this.inMono[j][k] /= 4.3609; // fx.LIV
    }
    for (let j = 0; j < 3; j++) {
      this.monos[j].process(this.inMono[j], this.inMono[j], this.oMono[j], B);
      this.ledMono[j] = Math.max(this.ledMono[j], this.monos[j].meter[0]);
    }
    for (let b = 0; b < 4; b++) {
      const s = this.oMic[b + 1];
      for (let k = 0; k < B; k++) {
        this.bus[b][0][k] += s[0][k];
        this.bus[b][1][k] += s[1][k];
      }
      for (const om of this.oMono) {
        const sm = om[b + 1];
        for (let k = 0; k < B; k++) {
          this.bus[b][0][k] += sm[0][k];
          this.bus[b][1][k] += sm[1][k];
        }
      }
      this.rerPrec[b][0].fill(0);
      this.rerPrec[b][1].fill(0);
    }

    const S = this.somma; // qui: mic e ritorni; il 5-way si aggiunge dopo, allineato
    S[0].set(this.oMic[0][0]);
    S[1].set(this.oMic[0][1]);
    for (const om of this.oMono) {
      for (let k = 0; k < B; k++) {
        S[0][k] += om[0][0][k];
        S[1][k] += om[0][1][k];
      }
    }
    for (let r = 0; r < 4; r++) {
      this.pedali[r].elabora(this.bus[r][0], this.bus[r][1], this.ped[r][0], this.ped[r][1], B);
      const o = this.oRet[r];
      this.rets[r].process(this.ped[r][0], this.ped[r][1], o, B);
      this.pkRet[r] = Math.max(this.pkRet[r], this.rets[r].meter[0]);
      this.clipRet[r] = Math.max(this.clipRet[r], this.rets[r].meter[1]);
      for (let b = 0; b < 4; b++) {
        const src = o[b + 1];
        for (let k = 0; k < B; k++) {
          this.rerPrec[b][0][k] += src[0][k];
          this.rerPrec[b][1][k] += src[1][k];
        }
      }
      // fader del ritorno: -12 dB a metà corsa (legge del fader di Federico), lisciato
      const tf = this.faderRet[r] / 100;
      const g = tf * tf;
      for (let k = 0; k < B; k++) {
        this.gRet[r] += (g - this.gRet[r]) * 0.002;
        S[0][k] += o[0][0][k] * this.gRet[r];
        S[1][k] += o[0][1][k] * this.gRet[r];
      }
    }

    if (this.esterno) {
      // mic e ritorni aspettano il 5-way: LAT blocchi
      const d = this.ritardo[this.n % LAT];
      for (let c = 0; c < 2; c++) {
        for (let k = 0; k < B; k++) {
          const v = d[c][k];
          d[c][k] = S[c][k];
          S[c][k] = v;
        }
      }
      this.n++;
    }
    for (let k = 0; k < B; k++) {
      S[0][k] += this.oFive[0][k];
      S[1][k] += this.oFive[1][k];
    }
    this.master.process(S[0], S[1], [this.oMs], B);
    const M = this.master.meter;
    this.pkMaster[0] = Math.max(this.pkMaster[0], M[0]);
    this.pkMaster[1] = Math.max(this.pkMaster[1], M[1]);
    this.clipMaster[0] = Math.max(this.clipMaster[0], M[2]);
    this.clipMaster[1] = Math.max(this.clipMaster[1], M[3]);
    for (let k = 0; k < B; k++) {
      let p = Math.max(Math.abs(this.oMs[0][k]), Math.abs(this.oMs[1][k]));
      if (!(p < 1e6)) p = 1e6;
      const voluto = p * this.prot > 0.89 ? 0.89 / p : 1;
      this.prot = voluto < this.prot ? voluto : this.prot + (1 - this.prot) * 0.00005;
      out[0][k] = this.oMs[0][k] * this.prot;
      out[1][k] = this.oMs[1][k] * this.prot;
      // un valore rotto (NaN, infinito) non arriva alle casse
      if (!(Math.abs(out[0][k]) < 4)) out[0][k] = 0;
      if (!(Math.abs(out[1][k]) < 4)) out[1][k] = 0;
    }
  }

  // DJ BUS verso i Worker, 5-way di LAT blocchi fa dai Worker (pronto quando lo sono i due lati)
  fiveFuori() {
    const n = this.n;
    const o = (n % ANELLO) * 2 * B;
    this.ringIn.set(this.dj[0], o);
    this.ringIn.set(this.dj[1], o + B);
    Atomics.store(this.ctl, 0, n + 1);
    Atomics.notify(this.ctl, 0);
    const vecchio = n - LAT;
    const pronti = Math.min(Atomics.load(this.ctl, 1), Atomics.load(this.ctl, 2));
    if (vecchio >= 0 && pronti > vecchio) {
      const q = (vecchio % ANELLO) * 2 * B;
      this.oFive[0].set(this.ringOut.subarray(q, q + B));
      this.oFive[1].set(this.ringOut.subarray(q + B, q + 2 * B));
    } else {
      this.oFive[0].fill(0);
      this.oFive[1].fill(0);
      // il primo secondo non conta: i due Worker si scaldano (compilazione del codice)
      if (vecchio >= 0 && pronti > 0 && n * B > this.fs) this.persi++;
    }
  }

  // i meter dal blocco prima e li azzera
  meter() {
    const m = {
      deck: this.deck.map((d) => d.pk),
      pos: this.deck.map((d) => (d.L ? d.pos / d.L.length : 0)),
      five: this.pkFive,
      ret: this.pkRet.slice(),
      clipRet: this.clipRet.slice(),
      master: this.pkMaster.slice(),
      clipMaster: this.clipMaster.slice(),
      led: this.led,
      ledVie: this.ledVie.leggi(),
      ledMono: this.ledMono.slice(),
      ledStrum: this.strum.map((x) => x.led),
      prot: this.prot,
      persi: this.persi || 0,
    };
    for (const d of this.deck) d.pk = 0;
    this.pkFive = this.led = 0;
    this.ledMono.fill(0);
    for (const x of this.strum) x.led = 0;
    this.pkRet.fill(0);
    this.clipRet.fill(0);
    this.pkMaster.fill(0);
    this.clipMaster.fill(0);
    return m;
  }
}

// Dentro il browser: il processore. In node (prova a banco) la classe sopra basta.
if (typeof AudioWorkletProcessor !== "undefined") {
  class Motore extends AudioWorkletProcessor {
    constructor(opzioni) {
      super();
      this.mx = new Mixer(sampleRate, opzioni?.processorOptions?.sab || null);
      this.blocchi = 0;
      this.port.onmessage = (ev) => this.mx.comando(ev.data);
    }
    process(inputs, outputs) {
      const mic = inputs[0] || [];
      const out = outputs[0];
      this.mx.blocco(mic[0], mic[1], out);
      if (++this.blocchi >= 12) {
        this.blocchi = 0;
        this.port.postMessage(this.mx.meter());
      }
      return true;
    }
  }
  registerProcessor("maelcum", Motore);
}
