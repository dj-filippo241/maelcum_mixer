// Due strumenti da banco, fuori dal mixer, che suonano nei moduli MONO:
//   NJD (MONO 1)      sirena dub classica, rifatta sullo schema ridisegnato da Zack Nelson
//                     (Zen Instruments, «NJD Dub Siren schematic redraw and PCB», 2022)
//   LICKSHOT (MONO 2) laser / tromba alla maniera delle macchine lickshot; struttura presa dal
//                     firmware open source xioTechnologies/Dub-Siren (Synthesiser.c: l'LFO riparte
//                     a ogni pressione, il gate chiude a fine ciclo, gate lisciato a 100 Hz)
// Uscita in volt, come il jack dello strumento; il motore la porta nella scala di MC-MONO.
//
// Cosa viene dallo schema NJD (valori letti sul disegno):
//   LFO   astabile a PNP T1/T2, C3 = C4 = 10 uF, resistenze di base da S3: 47k / 22k / 10k / 10k
//         (semiperiodo 0,693 R C: 3,3 / 1,5 / 0,7 Hz ... 7 Hz); S3 cortocircuita R24 nelle
//         posizioni 1-3 (caduta veloce), non nella 4 (caduta lenta)
//   forma C5 100 uF caricato dall'onda quadra attraverso D4 e R22 1k, scaricato da R22 + R23 2,2k
//         (+ R24 47k): 0,32 s o 5 s. S1 lo carica di colpo (+9 V sulla linea, azzera l'LFO),
//         S2 piano attraverso R25 10k (1,1 s). La tensione di C5 è lo SHAPED-LFO.
//   OSC   astabile a NPN T3/T4, C1 = C2 = 10 nF, collettori 4,7k, resistenze di base da S5:
//         470k / 220k / 100k / 68k (circa 150 / 330 / 720 / 1060 Hz); modulazione dai diodi
//         D1/D2 con R8/R9 220k sulle basi
//   uscita C9 100n / R26 15k, C8 100n / R27 15k (due passa-alto a 106 Hz), R3 100k su R30 10k
// Deduzione mia, non scritta sul disegno in modo leggibile: cosa porta ogni posizione di S4
// (MODULATION). Qui: 1 = sirena (C5 sulle basi), 2 = sirena a scatti (metà oscillatore
// alimentata dall'onda quadra), 3 = nota fissa a scatti, 4 = suono che vive solo con C5
// (cade e si spegne). Anche la rampa del tasto POWER (0,1 s) è mia.

const VCC = 9;
const VBE = 0.6, VCE = 0.2;

export class Njd {
  constructor(fs) {
    this.fs = fs;
    this.os = 4; // sotto-campioni per campione
    this.dt = 1 / (fs * this.os);
    this.p = { lfo: 0, mod: 0, osc: 25, vol: 100, power: 0, s1: 0, s2: 0 };
    this.vs = 0; // alimentazione dopo S6
    // LFO
    this.lfoFase = 0; // 0..1 sul periodo; prima metà = T2 acceso (uscita alta)
    // C5
    this.vc = 0;
    // oscillatore: chi conduce, base del transistor spento, collettore che si ricarica
    this.on3 = true;
    this.vbOff = -VCC;
    this.vcRec = VCE;
    // uscita
    this.hp1 = 0; this.hp1x = 0; this.hp2 = 0; this.hp2x = 0;
    this.led = 0;
  }

  set(k, v) {
    if (k === "s1" && v && !this.p.s1) this.lfoFase = 0; // S1 azzera l'LFO (D3)
    this.p[k] = v;
  }

  scatto(v) { return Math.min(3, Math.floor(v / 25)); }

  process(out, n) {
    const p = this.p, dt = this.dt;
    const rLfo = [47e3, 22e3, 10e3, 10e3][this.scatto(p.lfo)];
    const rd = this.scatto(p.lfo) === 3 ? 1e3 + 2.2e3 + 47e3 : 1e3 + 2.2e3;
    const rOsc = [470e3, 220e3, 100e3, 68e3][this.scatto(p.osc)];
    const mod = this.scatto(p.mod);
    const fLfo = 1 / (2 * 0.693 * rLfo * 10e-6);
    const C5 = 100e-6, COSC = 10e-9, RC = 4.7e3;
    const kRec = 1 - Math.exp(-dt / (RC * COSC));
    const kHp = 1 / (1 + 2 * Math.PI * 106 * dt); // passa-alto 1o ordine, 15k / 100n
    const vol = p.vol / 100;
    const gOut = (10e3 / 110e3) * vol * vol; // R3 100k su R30 10k, pot logaritmico
    let ledMax = 0;
    for (let k = 0; k < n; k++) {
      let acc = 0;
      for (let s = 0; s < this.os; s++) {
        // alimentazione: S6 con una rampa breve
        this.vs += ((p.power ? VCC : 0) - this.vs) * (dt / 0.1);
        const vs = this.vs;
        // LFO a onda quadra; S1 tiene la linea a +9 V
        if (!p.s1) {
          this.lfoFase += fLfo * dt;
          if (this.lfoFase >= 1) this.lfoFase -= 1;
        }
        const vq = p.s1 ? vs : this.lfoFase < 0.5 ? vs - VCE : 0;
        // nodo dopo D4: libero (scarica verso R23/R24, carica lenta da S2) o tenuto dal diodo
        const g2 = p.s2 ? 1 / 10e3 : 0;
        let a = (this.vc / 1e3 + g2 * vs) / (1 / 1e3 + g2 + 1 / (rd - 1e3));
        if (vq - VBE > a) a = vq - VBE;
        this.vc += ((a - this.vc) / (1e3 * C5)) * dt;
        const vsh = this.vc; // SHAPED-LFO
        // MODULATION (S4, mappa dedotta): alimentazione della metà B, tensione sui diodi
        const vb = mod === 0 ? vs : mod === 3 ? vsh : vq;
        const vm = mod === 2 ? vs : mod === 3 ? 0 : vsh;
        // base del transistor spento: carica verso Veff con tau = Req C
        const vSup = this.on3 ? vb : vs; // T3 acceso: si carica la base di T4 (metà B)
        const gm = vm - VBE > this.vbOff ? 1 / 220e3 : 0;
        const req = 1 / (1 / rOsc + gm);
        const veff = req * (vSup / rOsc + (vm - VBE) * gm);
        this.vbOff += (veff - this.vbOff) * (dt / (req * COSC));
        this.vcRec += (vs - this.vcRec) * kRec;
        if (this.vbOff >= VBE) {
          // scatta: il nuovo acceso tira giù il suo collettore e spinge in negativo l'altra base
          const salto = this.vcRec - VCE;
          this.on3 = !this.on3;
          this.vbOff = VBE - salto;
          this.vcRec = VCE;
        }
        // uscita: collettore di T4 (basso quando T4 conduce, cioè quando T3 è spento)
        acc += this.on3 ? this.vcRec : VCE;
      }
      const x = acc / this.os;
      // C9/R26 e C8/R27
      this.hp1 = kHp * (this.hp1 + x - this.hp1x);
      this.hp1x = x;
      this.hp2 = kHp * (this.hp2 + this.hp1 - this.hp2x);
      this.hp2x = this.hp1;
      const y = this.hp2 * gOut;
      out[k] = y < 20 && y > -20 ? y : 0;
      if (this.vc > ledMax) ledMax = this.vc;
    }
    this.led = Math.max(this.led, ledMax / VCC);
  }
}

// LICKSHOT: un oscillatore a onda quadra (due, leggermente scordati, in TROMBA), un LFO a dente
// di sega discendente che fa cadere il tono di 3 ottave a ogni colpo (LASER). Il tasto apre il
// gate e fa ripartire l'LFO; lasciato, il colpo in corso finisce e il gate chiude: un tocco breve
// = un colpo, tenuto = raffica. Numeri (gamme, 3 ottave, inviluppo del colpo) scelti da me.
export class Lickshot {
  constructor(fs) {
    this.fs = fs;
    this.p = { tone: 55, rate: 45, lfo: 1, vol: 100, trig: 0 };
    this.fase = 0; this.fase2 = 0; this.lfoFase = 0;
    this.gate = 0; this.gg = 0;
    this.kGate = 1 - Math.exp((-2 * Math.PI * 100) / fs);
    this.lp = 0;
    this.led = 0;
  }

  set(k, v) {
    if (k === "trig" && v && !this.p.trig) {
      this.lfoFase = 0;
      this.gate = 1;
    }
    this.p[k] = v;
  }

  process(out, n) {
    const p = this.p, fs = this.fs;
    const fTono = 120 * Math.pow(20, p.tone / 100); // 120 Hz ... 2,4 kHz
    const fLfo = 3 * Math.pow(10, p.rate / 100); // 3 ... 30 colpi al secondo
    const laser = p.lfo > 0;
    const amp = 0.9 * (p.vol / 100) * (p.vol / 100); // volt di picco
    const kLp = 1 - Math.exp((-2 * Math.PI * 6000) / fs);
    let ledMax = 0;
    for (let k = 0; k < n; k++) {
      let f = fTono, inv = 1;
      if (laser) {
        f = fTono * Math.pow(2, 3 * (1 - this.lfoFase));
        inv = Math.exp(-2.5 * this.lfoFase);
        this.lfoFase += fLfo / fs;
        if (this.lfoFase >= 1) {
          this.lfoFase -= 1;
          if (!p.trig) this.gate = 0; // il colpo è finito e il tasto è su
        }
      } else if (!p.trig) this.gate = 0;
      this.gg += (this.gate - this.gg) * this.kGate;
      let y = quadra(this.fase, f / fs);
      this.fase += f / fs;
      if (this.fase >= 1) this.fase -= 1;
      if (!laser) {
        const f2 = f * 1.012;
        y = 0.5 * (y + quadra(this.fase2, f2 / fs));
        this.fase2 += f2 / fs;
        if (this.fase2 >= 1) this.fase2 -= 1;
      }
      this.lp += (y - this.lp) * kLp;
      const v = this.lp * inv * this.gg * amp;
      out[k] = v;
      const a = Math.abs(v);
      if (a > ledMax) ledMax = a;
    }
    this.led = Math.max(this.led, this.gg);
  }
}

// onda quadra con PolyBLEP (meno ripiegamento sopra Nyquist)
function quadra(t, dt) {
  let y = t < 0.5 ? 1 : -1;
  y += blep(t, dt);
  let t2 = t + 0.5;
  if (t2 >= 1) t2 -= 1;
  y -= blep(t2, dt);
  return y;
}
function blep(t, dt) {
  if (t < dt) { t /= dt; return t + t - t * t - 1; }
  if (t > 1 - dt) { t = (t - 1) / dt; return t * t + t + t + 1; }
  return 0;
}

export const STRUMENTI = [
  { nome: "NJD", mono: 1, comandi: [
    ["LFO RATE", "lfo", 0, 4], ["MODULATION", "mod", 0, 4], ["OSC RATE", "osc", 25, 4], ["VOLUME", "vol", 100],
  ], tasti: [["S1", "s1", "1"], ["S2", "s2", "2"]], levetta: ["POWER", "power", ["OFF", "ON"]] },
  { nome: "LICKSHOT", mono: 2, comandi: [
    ["TONE", "tone", 55], ["RATE", "rate", 45], ["VOLUME", "vol", 100],
  ], tasti: [["FIRE", "trig", "3"]], levetta: ["LFO", "lfo", ["TROMBA", "LASER"], 1] },
];
