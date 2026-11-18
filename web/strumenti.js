// Due strumenti da banco, fuori dal mixer, che suonano nei moduli MONO:
//   NJD (MONO 1)      sirena dub classica, rifatta sullo schema ridisegnato da Zack Nelson
//                     (Zen Instruments, «NJD Dub Siren schematic redraw and PCB», 2022)
//   LICKSHOT (MONO 2) nucleo di Nold (LFO CD4069 -> VCO CD4046), valori dallo schema KiCad di
//                     Orald-0 e dal datasheet TI del CD4046B (dettagli sopra la classe)
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
//   S4    MODULATION, letto sul disegno (rev. 12/11): il comune di C2 alimenta le resistenze di
//         base della metà A, quello di C3 la metà B, C1 porta +9 V sui diodi D1/D2 in posizione 3.
//           pos. 1  A = +9 V         B = SHAPED-LFO   sirena che cade e si spegne con C5
//           pos. 2  A = +9 V         B = LFO quadra   beep a scatti
//           pos. 3  A = LFO quadra   B = LFO quadra   due toni (diodi a +9 V: suona anche a quadra bassa)
//           pos. 4  A = SHAPED-LFO   B = SHAPED-LFO   sirena piena, segue C5 sulle due metà
// Deduzione mia: la rampa del tasto POWER (20 ms).

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
        this.vs += ((p.power ? VCC : 0) - this.vs) * (dt / 0.02);
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
        // MODULATION (S4): alimentazione delle due metà, tensione sui diodi
        const va = mod <= 1 ? vs : mod === 2 ? vq : vsh;
        const vb = mod === 0 ? vsh : mod === 3 ? vsh : vq;
        const vm = mod === 2 ? vs : 0;
        // base del transistor spento: carica verso Veff con tau = Req C
        const vSup = this.on3 ? vb : va; // T3 acceso: si carica la base di T4 (metà B)
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

// LICKSHOT: nucleo di Nold («Lickshot-I», 2016), collegamenti letti nel KiCad di Orald-0
// (github.com/Orald-0/lickshot_dub_siren, cartella «DA SBROGLIARE», sigle di Orald-0 qui sotto).
// Comandi della dec. 184: ALTEZZA, VELOCITÀ, LFO ON/OFF, VOLUME, LED; il colpo parte dal tasto (dec. 183).
//
// Cosa viene dallo schema:
//   alimentazione  9 V attraverso D4 1N5817 e R21 33 ohm: VDD ~8,6 V (caduta del diodo: deduzione mia)
//   LFO   CD4069: U1A+U1B = trigger di Schmitt (R1 22k in reazione, R4 10k dall'integratore);
//         U1C = integratore di Miller con C1 1 uF, corrente da R6 22k + RV2 500k (VELOCITÀ).
//         Soglie del Schmitt: 6/22 e 16/22 di VDD (con la soglia della porta a VDD/2).
//         Rampa lenta: T = 0,909 (R6 + RV2) C1 = 20 ms ... 0,47 s, cioè ~48 ... 2,1 colpi al secondo.
//         I diodi D2/D3 col deviatore SW1 cortocircuitano R6+RV2 in un verso: dente di sega.
//         Qui SW1 è fisso su D3 (FORMA scartata, dec. 184): risalita veloce, discesa lenta = il tono
//         cade a ogni colpo. Risalita ~0,5 ms (resistenza d'uscita del 4069 ~500 ohm: deduzione mia).
//   VCO   CD4046: l'uscita dell'integratore entra nel VCOin (R5 10k), R1 = R2 10k + RV1 50k
//         (ALTEZZA), C1 = C2 100 nF, R2 al pin 12 aperta (fmin = 0). Frequenza al centro
//         (VCOin = VDD/2): ~0,7 / (R1 C1) dalla Fig. 4 del datasheet TI SCHS043B (10k, 0,1 uF:
//         ~700 Hz a 9-10 V; ±30 % fra un chip e l'altro). Legge lineare col VCOin, zero a ~1 V
//         (soglia: deduzione mia). La rampa va da 2,3 a 6,3 V: il colpo copre ~2 ottave,
//         da ~1,1 kHz a ~290 Hz con ALTEZZA al massimo, da ~190 a ~50 Hz al minimo.
//   uscita onda quadra dal pin 4 -> C3 1 uF -> R9 1k su R8 100 ohm (passa-alto a 145 Hz) -> SW3:
//         il tasto apre e chiude il segnale, l'LFO gira sempre (non riparte alla pressione).
//   LED   inseguitore Q1 2N3904 sull'uscita dell'integratore, LED e R3 10k: si accende con la rampa.
// Scelte mie, fuori dallo schema: LFO OFF ferma la rampa a VDD/2 (tono fisso al centro, dec. 184);
// VOLUME = pot logaritmico; livello 0 dBu (0,775 V sul plateau) a VOLUME pieno (dec. 187).
const VDD_L = 8.6;
const LO_L = (6 / 22) * VDD_L, HI_L = (16 / 22) * VDD_L;
const VOFF_L = 1.0;

export class Lickshot {
  constructor(fs) {
    this.fs = fs;
    this.p = { alt: 80, vel: 50, lfo: 1, vol: 100, trig: 0 };
    this.vi = VDD_L / 2; // uscita dell'integratore (U1C) = VCOin
    this.su = false; // true durante la risalita veloce
    this.fase = 0;
    this.hpx = 0; this.hpy = 0;
    this.led = 0;
  }

  set(k, v) { this.p[k] = v; }

  process(out, n) {
    const p = this.p, fs = this.fs;
    const r1 = 10e3 + (1 - p.alt / 100) * 50e3; // RV1 come reostato: a destra 10k
    const f0 = 0.7 / (r1 * 100e-9);
    const rl = 22e3 + (1 - p.vel / 100) * 500e3; // R6 + RV2
    const giu = VDD_L / 2 / (rl * 1e-6) / fs; // volt per campione nella discesa
    const su = (HI_L - LO_L) / 5e-4 / fs;
    const kHp = 1 / (1 + 2 * Math.PI * 145 / fs);
    const amp = 0.775 * (p.vol / 100) * (p.vol / 100);
    const gate = p.trig ? 1 : 0;
    let ledMax = 0;
    for (let k = 0; k < n; k++) {
      if (p.lfo) {
        if (this.su) {
          this.vi += su;
          if (this.vi >= HI_L) { this.vi = HI_L; this.su = false; }
        } else {
          this.vi -= giu;
          if (this.vi <= LO_L) { this.vi = LO_L; this.su = true; }
        }
      } else this.vi = VDD_L / 2;
      const f = (f0 * Math.max(0, this.vi - VOFF_L)) / (VDD_L / 2 - VOFF_L);
      const x = quadra(this.fase, f / fs);
      this.fase += f / fs;
      if (this.fase >= 1) this.fase -= 1;
      this.hpy = kHp * (this.hpy + x - this.hpx); // C3 su R9 + R8
      this.hpx = x;
      out[k] = this.hpy * gate * amp;
      const l = (this.vi - 2.4) / (HI_L - 2.4); // Q1 + LED: si accende sopra ~2,4 V
      if (l > ledMax) ledMax = l;
    }
    this.led = Math.max(this.led, Math.min(1, Math.max(0, ledMax)));
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
    ["ALTEZZA", "alt", 80], ["VELOCITÀ", "vel", 50], ["VOLUME", "vol", 100],
  ], tasti: [["FIRE", "trig", "3"]], levetta: ["LFO", "lfo", ["OFF", "ON"], 1] },
];
