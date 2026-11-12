// Banco del mixer: il pannello della disposizione F visto dall'alto (pannello.json), i quattro
// pedali accanto, e il motore audio (motore.js + five.worker.js) col codice di proto-max.
// Grafica minima: cerchi, rettangoli e scritte. Misure in millimetri (1 unità SVG = 1 mm).

import { NOMI_PEDALI } from "./pedali.js";
import { STRUMENTI } from "./strumenti.js";

const NS = "http://www.w3.org/2000/svg";
const svg = document.getElementById("banco");
const stato = document.getElementById("stato");
const avvisa = (t) => (document.getElementById("avviso").textContent = t);
const lettura = document.getElementById("lettura");
const leggiFile = async (u) => {
  const r = await fetch(u);
  if (!r.ok) throw new Error(`${u}: ${r.status}`);
  return r.json();
};
let pannello, indice;
try {
  [pannello, indice] = await Promise.all([leggiFile("pannello.json"), leggiFile("dsp/indice.json")]);
} catch (e) {
  avvisa("La pagina non ha letto i suoi file. Ricaricala; aprila dal link, non dal disco.");
  throw e;
}

// ---------------------------------------------------------------- collegamenti dei comandi
const BANDE = { HIGH: "high", "MID-HIGH": "midhigh", "LOW-MID": "lowmid", LOW: "low" };
const VIE = ["SUB", "KICK", "MID", "HIGH", "SUPER"];
const KILL = ["k_sub", "k_kick", "k_mid", "k_high", "k_super"];
const def = (dev, p) => {
  const tab = { ch: "MC-CHANNEL-S", send: "MC-SEND", hpf: "MC-FILTRO-HPF", lpf: "MC-FILTRO-LPF",
    five: "MC-5WAY-S", ret: "MC-RET", mic: "MC-MIC", mono: "MC-MONO", master: "MC-MASTER" }[dev];
  return indice[tab][p][0];
};
const par = (dev, p, i, d) => ({ tipo: "param", dev, p, i, def: d ?? def(dev, p) });

function collega(mod, c, k) {
  const n = c.nome;
  const i = mod.i;
  switch (mod.tipo) {
    case "canale":
      if (n === "GAIN") return par("ch", "gain", i);
      if (BANDE[n]) return par("ch", BANDE[n], i);
      if (n === "FADER") return par("ch", "fader", i, 75);
      if (n === "FILTRO") return { tipo: "modo", i, def: 1 };
      if (/^FX\d$/.test(n)) return par("send", "as" + n[2], i);
      if (n === "LEVEL") return par("send", "level", i);
      if (n === "EQ HIGH") return par("send", "high", i);
      if (n === "EQ LOW") return par("send", "low", i);
      if (n === "METER") return { tipo: "meter", src: ["deck", i] };
      return null; // LINE/PHONO, CUE
    case "mic":
      if (n === "GAIN") return par("mic", "gain");
      if (n === "EQ HIGH") return par("mic", "high");
      if (n === "EQ LOW") return par("mic", "low");
      if (n === "MUTE") return par("mic", "mute");
      if (n.startsWith("SEND")) return par("mic", "snd" + n.slice(-1));
      if (n === "LED") return { tipo: "led", src: ["mic"] };
      return null;
    case "ret":
      if (n === "GAIN") return par("ret", "gain", i);
      if (n === "EQ HIGH") return par("ret", "high", i);
      if (n === "EQ LOW") return par("ret", "low", i);
      if (n === "SELF") return par("ret", "rr" + (i + 1), i);
      if (n.startsWith("> FX")) return par("ret", "rr" + n.slice(-1), i);
      if (n === "FADER") return { tipo: "faderRet", i, def: 70 };
      if (n === "METER") return { tipo: "meter", src: ["ret", i] };
      return null;
    case "filtro": {
      const sez = k < 3 ? "hp" : "lp";
      const p = { RES: "res", FREQ: "freq", DRIVE: "drive" }[n] + "_" + sez;
      return par(sez === "hp" ? "hpf" : "lpf", p, 0, p === "freq_lp" ? 100 : undefined);
    }
    case "five": {
      const via = VIE.findIndex((v) => n.endsWith(" " + v));
      if (n.startsWith("GAIN ")) return par("five", "g_" + (via + 1));
      if (n.startsWith("POSITION ")) return par("five", "p_" + (via + 1));
      if (n.startsWith("WIDTH ")) return par("five", "w_" + (via + 1));
      if (n === "GROWL") return par("five", "growl");
      if (n === "NASTRO") return par("five", "nastro");
      if (n === "FISSO/MOLLA") {
        const v = mod.comandi.filter((x) => x.nome === "FISSO/MOLLA").indexOf(c);
        return { tipo: "kill", p: KILL[v] };
      }
      if (n === "METER") return { tipo: "meter", src: ["five"] };
      if (n === "LED") {
        // un LED per via, da sinistra: SUB, KICK, MID, HIGH, SUPER (ledvie.js nel motore)
        const v = mod.comandi.filter((x) => x.nome === "LED").indexOf(c);
        return { tipo: "led", src: ["five", v] };
      }
      return null;
    }
    case "master":
      if (n === "MASTER") return par("master", "level");
      if (n === "MONO") return par("master", "mono");
      if (n === "L") return { tipo: "meter", src: ["master", 0] };
      if (n === "R") return { tipo: "meter", src: ["master", 1] };
      return null; // BOOTH
    case "mono": {
      // MONO 1 = NJD, MONO 2 = LICKSHOT (strumenti.js), MONO 3 senza sorgente
      const j = i - 1;
      if (n === "GAIN") return par("mono", "gain", j, [90, 75, 62][j]);
      if (n === "EQ HIGH") return par("mono", "high", j);
      if (n === "EQ LOW") return par("mono", "low", j);
      if (n.startsWith("SEND")) return par("mono", "snd" + n.slice(-1), j);
      if (n === "LED") return { tipo: "led", src: ["mono", j] };
      return null;
    }
    default:
      return null; // CUE
  }
}

// ---------------------------------------------------------------- disegno
const el = (tag, attr = {}, padre = svg) => {
  const e = document.createElementNS(NS, tag);
  for (const k in attr) e.setAttribute(k, attr[k]);
  padre.appendChild(e);
  return e;
};
const testo = (x, y, t, cls, padre) => {
  const e = el("text", { x, y, class: cls }, padre);
  e.textContent = t;
  return e;
};

const W = pannello.larghezza, H = pannello.altezza;
const XP = W + 8; // colonna dei pedali
const WP = 64, HP = 92;
svg.setAttribute("viewBox", `-4 -4 ${XP + 2 * WP + 12} ${H + 8}`);

const comandi = []; // { b, val, aggiorna(), ... }
const tastiStrum = {}; // tasto della tastiera -> pulsante di uno strumento

function disegnaManopola(g, c, ctl) {
  const r = (c.cappuccio || 10) / 2;
  if (ctl.b && r < 5) el("circle", { cx: c.x, cy: c.y, r: 5, class: "bersaglio" }, g);
  el("circle", { cx: c.x, cy: c.y, r }, g);
  if (c.scatto) el("line", { x1: c.x, y1: c.y - r - 1.4, x2: c.x, y2: c.y - r - 0.4, class: "tacca", stroke: "#8a8a84", "stroke-width": 0.4 }, g);
  const ind = el("line", { x1: c.x, y1: c.y, x2: c.x, y2: c.y - r * 0.85 }, g);
  testo(c.x, c.y + r + 2.8, c.etichetta || c.nome, "eti", g);
  const val = testo(c.x, c.y + r + 5.2, "", "val", g);
  ctl.aggiorna = () => {
    const a = (-135 + 2.7 * ctl.val) * (Math.PI / 180);
    ind.setAttribute("x2", c.x + Math.sin(a) * r * 0.85);
    ind.setAttribute("y2", c.y - Math.cos(a) * r * 0.85);
    val.textContent = ctl.trascino ? Math.round(ctl.val) : "";
  };
}

function disegnaFader(g, c, ctl) {
  const h = c.corsa;
  el("line", { x1: c.x, y1: c.y - h / 2, x2: c.x, y2: c.y + h / 2, class: "binario" }, g);
  const cur = el("rect", { x: c.x - 4, y: 0, width: 8, height: 3.5, rx: 0.6, class: "cursore" }, g);
  el("rect", { x: c.x - 6, y: c.y - h / 2 - 3, width: 12, height: h + 6, class: "bersaglio" }, g);
  testo(c.x, c.y + h / 2 + 5, c.nome, "eti", g);
  ctl.aggiorna = () => cur.setAttribute("y", c.y + h / 2 - (ctl.val / 100) * h - 1.75);
  ctl.fader = { y0: c.y + h / 2, h };
}

function disegnaBottone(g, c, ctl) {
  el("rect", { x: c.x - c.larghezza / 2, y: c.y - c.altezza / 2, width: c.larghezza, height: c.altezza, rx: 1 }, g);
  testo(c.x, c.y + 0.8, c.nome, "eti", g);
  ctl.aggiorna = () => g.classList.toggle("on", ctl.val > 0);
}

function disegnaLevetta(g, c, ctl) {
  el("rect", { x: c.x - 4, y: c.y - 6, width: 8, height: 12, rx: 1 }, g);
  const pos = c.posizioni.length === 2 && ctl.b?.tipo !== "kill" ? c.posizioni : c.posizioni;
  const t = testo(c.x, c.y + 0.8, "", "eti", g);
  if (ctl.b?.tipo === "kill") {
    testo(c.x, c.y - 7.2, "FISSO", "eti", g);
    testo(c.x, c.y + 9.6, "MOLLA", "eti", g);
  } else testo(c.x, c.y + 9.6, c.nome, "eti", g);
  ctl.aggiorna = () => {
    if (ctl.b?.tipo === "modo") t.textContent = ["HPF", "OFF", "LPF"][ctl.val];
    else if (ctl.b?.tipo === "kill") t.textContent = ctl.fisso ? "KILL" : ctl.molla ? "kill" : "ON";
    else t.textContent = pos[0];
    g.classList.toggle("on", ctl.b?.tipo === "kill" && (ctl.fisso || ctl.molla));
  };
}

function disegnaMeter(g, c, ctl) {
  const segs = [];
  const n = c.segmenti;
  for (let k = 0; k < n; k++) {
    const s = c.orizzontale
      ? el("rect", { x: c.x + k * c.passo, y: c.y, width: c.passo - 0.8, height: 3, class: "seg" }, g)
      : el("rect", { x: c.x - 2, y: c.y + (n - 1 - k) * c.passo, width: 4, height: c.passo - 1, class: "seg" }, g);
    segs.push(s);
  }
  testo(c.orizzontale ? c.x - 3 : c.x, c.orizzontale ? c.y + 2.6 : c.y + n * c.passo + 2.4, c.nome === "METER" ? "" : c.nome, "eti", g);
  ctl.segs = segs;
  ctl.dbu = -99;
}

function disegnaLed(g, c, ctl) {
  ctl.led = [-1, 0, 1].map((d) => el("circle", { cx: c.x + d * (c.passo || 4), cy: c.y, r: 1.2, class: "seg" }, g));
  ctl.dbu = 0;
}

for (const mod of pannello.moduli) {
  const g = el("g", { "data-modulo": mod.tipo + mod.i });
  el("rect", { x: mod.x, y: mod.y, width: mod.w, height: mod.h, class: "modulo" }, g);
  testo(mod.x + 3, mod.y + 6, mod.titolo, "titolo", g);
  mod.g = g;
  if (mod.tipo === "canale") {
    mod.etiFile = testo(mod.x + mod.w / 2, mod.y + 10.5, "riddim di prova", "deck-file", g);
    preparaDeck(mod);
  }
  mod.comandi.forEach((c, k) => {
    const b = collega(mod, c, k);
    const gc = el("g", {}, g);
    const ctl = { c, b, val: 0, dove: mod.titolo };
    const inerte = !b && c.tipo !== "jack";
    if (inerte || c.tipo === "jack") gc.classList.add("inerte");
    if (c.tipo === "manopola") {
      gc.classList.add("manopola");
      if (b) gc.classList.add("comando");
      disegnaManopola(gc, c, ctl);
    } else if (c.tipo === "fader") {
      gc.classList.add("comando");
      disegnaFader(gc, c, ctl);
    } else if (c.tipo === "bottone") {
      gc.classList.add("bottone");
      if (b) gc.classList.add("click");
      disegnaBottone(gc, c, ctl);
    } else if (c.tipo === "levetta") {
      gc.classList.add("levetta");
      if (b) gc.classList.add("click");
      disegnaLevetta(gc, c, ctl);
    } else if (c.tipo === "meter") disegnaMeter(gc, c, ctl);
    else if (c.tipo === "led3") disegnaLed(gc, c, ctl);
    else if (c.tipo === "jack") {
      el("circle", { cx: c.x, cy: c.y, r: 3.5 }, gc);
      testo(c.x, c.y + 6.5, c.nome, "eti", gc);
    }
    if (inerte) {
      const t = el("title", {}, gc);
      t.textContent = `${c.nome}: comando finto, qui non fa niente`;
    }
    ctl.g = gc;
    if (b && b.def !== undefined) ctl.val = b.def;
    if (b?.tipo === "kill") ctl.fisso = ctl.molla = false;
    comandi.push(ctl);
    ctl.aggiorna?.();
    if (b) attiva(ctl);
  });
}

// pedali, accanto al mixer: 2 x 2, uno per bus FX
NOMI_PEDALI.forEach(([nome, a, b, da, db], i) => {
  const x = XP + (i % 2) * (WP + 4), y = 40 + Math.floor(i / 2) * (HP + 6);
  const g = el("g", {});
  el("rect", { x, y, width: WP, height: HP, rx: 3, class: "modulo" }, g);
  testo(x + 3, y + 6, `FX ${i + 1} · ${nome}`, "titolo", g);
  testo(x + 3, y + 10.5, "pedale fuori dal mixer", "deck-file", g).style.textAnchor = "start"; // la classe CSS vince sull'attributo
  [[a, "a", da], [b, "b", db]].forEach(([eti, k, d], j) => {
    const c = { tipo: "manopola", nome: eti, x: x + 18 + j * 28, y: y + 35, cappuccio: 18 };
    const gc = el("g", { class: "manopola comando" }, g);
    const ctl = { c, b: { tipo: "pedale", i, k, def: d }, val: d, g: gc };
    disegnaManopola(gc, c, ctl);
    ctl.aggiorna();
    comandi.push(ctl);
    attiva(ctl);
  });
  el("rect", { x: x + 22, y: y + 62, width: 20, height: 12, rx: 2, fill: "none", stroke: "#b9b9b2", "stroke-width": 0.4 }, g);
  testo(x + WP / 2, y + 69.5, "100 % wet", "eti", g);
});
testo(XP, 34, "PEDALI FX (mandata dai bus, ritorno nei FX RET)", "eti", svg).style.textAnchor = "start"; // la classe CSS vince sull'attributo

// strumenti, sotto i pedali: NJD nel MONO 1, LICKSHOT nel MONO 2 (strumenti.js)
const YS = 40 + 2 * (HP + 6) + 12;
testo(XP, YS - 4, "STRUMENTI (nel jack dei MONO 1 e 2) · tasti 1, 2, 3", "eti", svg).style.textAnchor = "start"; // la classe CSS vince sull'attributo
STRUMENTI.forEach((st, i) => {
  const x = XP + i * (WP + 4), y = YS;
  const g = el("g", {});
  el("rect", { x, y, width: WP, height: HP + 14, rx: 3, class: "modulo" }, g);
  testo(x + 3, y + 6, st.nome, "titolo", g);
  testo(x + 3, y + 10.5, `strumento fuori dal mixer · MONO ${st.mono}`, "deck-file", g).style.textAnchor = "start"; // la classe CSS vince sull'attributo
  const lamp = el("circle", { cx: x + WP - 6, cy: y + 5, r: 1.8, class: "seg r", style: "opacity:0.15" }, g);
  comandi.push({ c: { tipo: "led", nome: "LED" }, b: { tipo: "ledStrum", i }, lampada: lamp });
  st.comandi.forEach(([eti, k, d, scatti], j) => {
    const c = { tipo: "manopola", nome: eti, x: x + 14 + (j % 2) * 36, y: y + 24 + Math.floor(j / 2) * 26, cappuccio: 13, scatti };
    const gc = el("g", { class: "manopola comando" }, g);
    const v0 = scatti ? (Math.round((d / 100) * (scatti - 1)) * 100) / (scatti - 1) : d;
    const ctl = { c, b: { tipo: "strum", i, k, def: v0, scatti }, val: v0, g: gc, dove: st.nome };
    disegnaManopola(gc, c, ctl);
    ctl.aggiorna();
    comandi.push(ctl);
    attiva(ctl);
  });
  const [eL, kL, voci, dL = 0] = st.levetta;
  {
    const c = { tipo: "bottone", nome: eL, x: x + WP / 2, y: y + 78 };
    const gc = el("g", { class: "bottone click" }, g);
    const ctl = { c, b: { tipo: "strum", i, k: kL, def: dL }, val: dL, g: gc, dove: st.nome };
    el("rect", { x: c.x - 11, y: c.y - 4, width: 22, height: 8, rx: 1 }, gc);
    const t = testo(c.x, c.y + 0.8, "", "eti", gc);
    ctl.aggiorna = () => {
      t.textContent = `${eL} ${voci[ctl.val]}`;
      gc.classList.toggle("on", ctl.val > 0);
    };
    ctl.aggiorna();
    gc.addEventListener("pointerenter", () => mostra(ctl));
    gc.addEventListener("click", () => imposta(ctl, ctl.val > 0 ? 0 : 1));
    comandi.push(ctl);
  }
  st.tasti.forEach(([eti, k, tasto], j) => {
    const n = st.tasti.length;
    const c = { tipo: "bottone", nome: eti, x: x + WP / 2 + (j - (n - 1) / 2) * 24, y: y + 94 };
    const gc = el("g", { class: "bottone click" }, g);
    const ctl = { c, b: { tipo: "strum", i, k, def: 0 }, val: 0, g: gc, dove: st.nome };
    el("rect", { x: c.x - 10, y: c.y - 6, width: 20, height: 12, rx: 2 }, gc);
    testo(c.x, c.y + 0.8, `${eti} (${tasto})`, "eti", gc);
    ctl.aggiorna = () => gc.classList.toggle("on", ctl.val > 0);
    gc.addEventListener("pointerenter", () => mostra(ctl));
    gc.addEventListener("touchstart", (e) => e.preventDefault(), { passive: false });
    gc.addEventListener("pointerdown", (e) => {
      if (e.button !== 0) return;
      e.preventDefault();
      gc.setPointerCapture(e.pointerId);
      imposta(ctl, 1);
      gc.addEventListener("lostpointercapture", () => imposta(ctl, 0), { once: true });
    });
    tastiStrum[tasto] = ctl;
    comandi.push(ctl);
  });
});

// ---------------------------------------------------------------- interazione
const mostra = (ctl) =>
  (lettura.textContent = `${ctl.dove ?? "PEDALE"} · ${ctl.c.etichetta || ctl.c.nome}` +
    (ctl.b?.scatti ? `: posizione ${Math.round((ctl.val / 100) * (ctl.b.scatti - 1)) + 1}`
      : ["manopola", "fader"].includes(ctl.c.tipo) ? `: ${Math.round(ctl.val)}` : ""));

function attiva(ctl) {
  const { c, b, g } = ctl;
  g.addEventListener("pointerenter", () => mostra(ctl));
  if (c.tipo === "manopola" || c.tipo === "fader") {
    // il dito sul comando non fa scorrere la pagina (Safari su iOS)
    g.addEventListener("touchstart", (e) => e.preventDefault(), { passive: false });
  }
  // doppio tocco = posizione di partenza (su touch il dblclick non arriva)
  const doppio = (e) => {
    const d = e.timeStamp - (ctl.tUltimo || 0) < 300;
    ctl.tUltimo = e.timeStamp;
    if (d) imposta(ctl, b.def ?? 50);
    return d;
  };
  if (c.tipo === "manopola") {
    g.addEventListener("pointerdown", (e) => {
      if (e.button !== 0) return;
      e.preventDefault();
      if (doppio(e)) return;
      g.setPointerCapture(e.pointerId);
      const y0 = e.clientY, v0 = ctl.val;
      ctl.trascino = true;
      const muovi = (ev) => {
        const passo = ev.shiftKey ? 600 : 180; // pixel per tutta la corsa
        imposta(ctl, Math.min(100, Math.max(0, v0 + ((y0 - ev.clientY) * 100) / passo)));
      };
      const fine = () => {
        ctl.trascino = false;
        ctl.aggiorna();
        g.removeEventListener("pointermove", muovi);
      };
      g.addEventListener("pointermove", muovi);
      g.addEventListener("lostpointercapture", fine, { once: true }); // dopo pointerup e pointercancel
    });
  } else if (c.tipo === "fader") {
    const yDi = (ev) => {
      const p = svg.createSVGPoint();
      p.x = ev.clientX;
      p.y = ev.clientY;
      return p.matrixTransform(svg.getScreenCTM().inverse()).y;
    };
    g.addEventListener("pointerdown", (e) => {
      if (e.button !== 0) return;
      e.preventDefault();
      if (doppio(e)) return;
      g.setPointerCapture(e.pointerId);
      // sul cursore: trascina da dov'è; fuori dal cursore: salta al punto toccato
      const y0 = yDi(e);
      const yCur = ctl.fader.y0 - (ctl.val / 100) * ctl.fader.h;
      const v0 = Math.abs(y0 - yCur) <= 3 ? ctl.val : ((ctl.fader.y0 - y0) / ctl.fader.h) * 100;
      const muovi = (ev) => imposta(ctl, Math.min(100, Math.max(0, v0 + ((y0 - yDi(ev)) / ctl.fader.h) * 100)));
      muovi(e);
      g.addEventListener("pointermove", muovi);
      g.addEventListener("lostpointercapture", () => g.removeEventListener("pointermove", muovi), { once: true });
    });
  } else if (c.tipo === "bottone") {
    g.addEventListener("click", () => imposta(ctl, ctl.val > 0 ? 0 : 1));
  } else if (c.tipo === "levetta") {
    if (b.tipo === "modo") {
      // clic sopra = HPF, in mezzo = OFF, sotto = LPF
      g.addEventListener("click", (e) => {
        const r = g.querySelector("rect").getBoundingClientRect(); // la levetta, non le scritte
        const t = (e.clientY - r.top) / r.height;
        imposta(ctl, t < 1 / 3 ? 0 : t > 2 / 3 ? 2 : 1);
      });
    } else if (b.tipo === "kill") {
      g.addEventListener("pointerdown", (e) => {
        if (e.button !== 0) return;
        const r = g.querySelector("rect").getBoundingClientRect();
        if ((e.clientY - r.top) / r.height < 0.5) {
          ctl.fisso = !ctl.fisso;
        } else {
          ctl.molla = true;
          g.setPointerCapture(e.pointerId);
          const lascia = () => {
            ctl.molla = false;
            imposta(ctl, ctl.fisso ? 1 : 0);
          };
          g.addEventListener("lostpointercapture", lascia, { once: true });
        }
        imposta(ctl, ctl.fisso || ctl.molla ? 1 : 0);
      });
    }
  }
}

function imposta(ctl, v) {
  if (ctl.b?.scatti) v = (Math.round((v / 100) * (ctl.b.scatti - 1)) * 100) / (ctl.b.scatti - 1); // commutatore a scatti
  ctl.val = v;
  ctl.aggiorna?.();
  mostra(ctl);
  invia(ctl);
}

function invia(ctl) {
  const b = ctl.b;
  if (!motore) return;
  const v = ctl.val;
  if (b.tipo === "param" || b.tipo === "kill") {
    const dev = b.tipo === "kill" ? "five" : b.dev;
    const msg = { t: "p", dev, i: b.i ?? 0, p: b.p, v };
    if (dev === "five" && worker) worker.postMessage(msg);
    else motore.port.postMessage(msg);
  } else if (b.tipo === "modo") motore.port.postMessage({ t: "modo", i: b.i, v });
  else if (b.tipo === "faderRet") motore.port.postMessage({ t: "faderRet", i: b.i, v });
  else if (b.tipo === "pedale") motore.port.postMessage({ t: "pedale", i: b.i, k: b.k, v });
  else if (b.tipo === "strum") motore.port.postMessage({ t: "strum", i: b.i, k: b.k, v: b.scatti ? Math.round((v / 100) * 3) * 25 + 12.5 : v });
}

// ---------------------------------------------------------------- tracce
const deck = [null, null, null, null];

function preparaDeck(mod) {
  const scegli = document.createElement("input");
  scegli.type = "file";
  scegli.accept = "audio/*";
  scegli.hidden = true;
  document.body.appendChild(scegli);
  const titolo = el("rect", { x: mod.x, y: mod.y, width: mod.w, height: 12, class: "bersaglio", style: "cursor:pointer" }, mod.g);
  el("title", {}, titolo).textContent = "Clic per caricare una traccia su questo deck";
  titolo.addEventListener("click", () => scegli.click());
  scegli.addEventListener("change", () => {
    const f = scegli.files[0];
    scegli.value = ""; // lo stesso file si può ricaricare
    if (f) caricaFile(mod, f);
  });
  mod.g.addEventListener("dragover", (e) => {
    e.preventDefault();
    mod.g.classList.add("drop");
  });
  mod.g.addEventListener("dragleave", () => mod.g.classList.remove("drop"));
  mod.g.addEventListener("drop", (e) => {
    e.preventDefault();
    mod.g.classList.remove("drop");
    const f = e.dataTransfer.files[0];
    if (f) caricaFile(mod, f);
  });
}

async function caricaFile(mod, file) {
  mod.etiFile.textContent = "carico…";
  try {
    await accendi();
    const buf = await ctx.decodeAudioData(await file.arrayBuffer());
    const L = buf.getChannelData(0).slice();
    const R = (buf.numberOfChannels > 1 ? buf.getChannelData(1) : buf.getChannelData(0)).slice();
    mandaTraccia(mod.i, L, R);
    mod.etiFile.textContent = file.name.length > 22 ? file.name.slice(0, 21) + "…" : file.name;
  } catch {
    mod.etiFile.textContent = "file non letto";
    avvisa(`Non leggo ${file.name}: prova un mp3 o un wav.`);
  }
}

function mandaTraccia(i, L, R) {
  motore.port.postMessage({ t: "traccia", i, L, R }, [L.buffer, R.buffer]);
  deck[i] = true;
}

// Riddim di prova a 75 BPM, 4 battute, un elemento per deck: batteria, basso, skank, melodica.
// Livello: picchi a -9 dBFS (0 dBu = -12 dBFS nel prototipo).
function riddim(fs) {
  const bpm = 75, battito = 60 / bpm, n = Math.round(fs * battito * 16);
  const st = () => [new Float32Array(n), new Float32Array(n)];
  const tr = [st(), st(), st(), st()];
  const nota = (m) => 440 * Math.pow(2, (m - 69) / 12);
  const metti = (t, i, durata, f) => {
    const a = Math.round(t * fs), b = Math.min(n, a + Math.round(durata * fs));
    for (let k = a; k < b; k++) {
      const v = f((k - a) / fs);
      tr[i][0][k] += v;
      tr[i][1][k] += v;
    }
  };
  let seme = 1;
  const rnd = () => ((seme = (seme * 16807) % 2147483647) / 2147483647) * 2 - 1;
  const accordi = [[57, 60, 64], [62, 65, 69], [64, 67, 71], [57, 60, 64]];
  const bassi = [[45, 45, 48, 45, 43], [50, 50, 53, 50, 48], [52, 52, 55, 52, 50], [45, 45, 48, 50, 52]];
  const tempiB = [0, 0.75, 1.5, 2, 3];
  const melodia = [[69, 0], [72, 1.5], [71, 2.5], [67, 3], [69, 8], [64, 10], [67, 11.5], [69, 12]];
  for (let bar = 0; bar < 4; bar++) {
    const t0 = bar * 4 * battito;
    // one drop: cassa e rullante sul terzo battito, charleston in ottavi
    metti(t0 + 2 * battito, 0, 0.5, (t) => Math.sin(2 * Math.PI * (45 * t + 40 * (1 - Math.exp(-t * 30)) / 30)) * Math.exp(-t * 7));
    metti(t0 + 2 * battito, 0, 0.18, (t) => rnd() * 0.5 * Math.exp(-t * 25) + Math.sin(2 * Math.PI * 190 * t) * 0.3 * Math.exp(-t * 30));
    for (let h = 0; h < 8; h++) {
      let prec = 0;
      metti(t0 + h * battito * 0.5, 0, 0.05, () => {
        const x = rnd();
        const y = x - prec;
        prec = x;
        return y * 0.12;
      });
    }
    bassi[bar].forEach((m, j) => {
      const f = nota(m);
      metti(t0 + tempiB[j] * battito, 1, battito * 0.7, (t) =>
        (Math.sin(2 * Math.PI * f * t) + 0.25 * Math.sin(4 * Math.PI * f * t)) * Math.min(1, t * 200) * Math.exp(-t * 2));
    });
    for (let s = 0; s < 4; s++) {
      metti(t0 + (s + 0.5) * battito, 2, 0.16, (t) => {
        let v = 0;
        for (const m of accordi[bar]) {
          const f = nota(m);
          v += Math.sin(2 * Math.PI * f * t) + 0.4 * Math.sin(4 * Math.PI * f * t) + 0.2 * Math.sin(6 * Math.PI * f * t);
        }
        return v * Math.exp(-t * 22);
      });
    }
  }
  for (const [m, b] of melodia) {
    const f = nota(m + 12);
    metti(b * battito, 3, battito * 1.2, (t) => {
      const ph = 2 * Math.PI * f * t + 0.03 * Math.sin(2 * Math.PI * 5.5 * t) * f / 5.5 * 0.05;
      return (Math.sin(ph) + 0.33 * Math.sin(3 * ph) + 0.2 * Math.sin(5 * ph)) * Math.min(1, t * 30) * Math.exp(-t * 1.5);
    });
  }
  for (const [L, R] of tr) {
    let p = 0;
    for (const v of L) p = Math.max(p, Math.abs(v));
    const g = 0.355 / (p || 1);
    for (let k = 0; k < n; k++) {
      L[k] *= g;
      R[k] *= g;
    }
  }
  return tr;
}

// ---------------------------------------------------------------- accensione
let ctx = null, motore = null, worker = null, micNodo = null;
const bAccendi = document.getElementById("accendi");
const bPlay = document.getElementById("play");
const bCapo = document.getElementById("riavvolgi");
const bMic = document.getElementById("mic");

let accensione = null;
function accendi() {
  return (accensione ??= (async () => {
    bAccendi.disabled = true;
    stato.textContent = "accendo…";
    try {
      await accendiDavvero();
      stato.textContent = "acceso: premi Play";
    } catch (e) {
      console.error(e);
      accensione = null;
      try { ctx?.close(); } catch {}
      ctx = motore = null;
      worker?.terminate();
      worker = null;
      bAccendi.disabled = false;
      stato.textContent = "spento";
      avvisa("L'audio non parte in questo browser. Prova Chrome o Firefox aggiornati.");
      throw e;
    }
  })());
}

function fiveInterno(perche) {
  if (!worker) return;
  worker.terminate();
  worker = null;
  motore.port.postMessage({ t: "interno" });
  for (const c of comandi) if (c.b && (c.b.dev === "five" || c.b.tipo === "kill")) invia(c);
  fiveFuori = "modo leggero: con GROWL e NASTRO alti il suono può interrompersi";
  if (perche) console.warn("5-way nel filo del motore:", perche);
}

async function accendiDavvero() {
  ctx = new AudioContext({ latencyHint: "interactive" }); // buffer corti: tasti e kill rispondono subito (playback: ~90 ms)
  await ctx.audioWorklet.addModule("motore.js");
  const { LAT, ANELLO } = await import("./costanti.js");
  let sab = null;
  if (globalThis.crossOriginIsolated && typeof Atomics.waitAsync === "function") {
    sab = new SharedArrayBuffer(16 + 2 * ANELLO * 2 * 128 * 4);
    worker = new Worker("five.worker.js", { type: "module" });
    const p5 = {};
    for (const c of comandi) if (c.b && (c.b.dev === "five" || c.b.tipo === "kill")) p5[c.b.p] = c.val;
    worker.postMessage({ t: "avvia", fs: ctx.sampleRate, sab, param: p5 });
    worker.onmessage = (e) => e.data.errore && fiveInterno(e.data.errore);
    worker.onerror = (e) => fiveInterno(e.message);
    fiveFuori = `5-way in un filo a parte (+${Math.round((LAT * 128 * 1000) / ctx.sampleRate)} ms)`;
  } else fiveFuori = "modo leggero: con GROWL e NASTRO alti il suono può interrompersi";
  motore = new AudioWorkletNode(ctx, "maelcum", {
    numberOfInputs: 1, numberOfOutputs: 1, outputChannelCount: [2], processorOptions: { sab },
  });
  motore.connect(ctx.destination);
  motore.port.onmessage = (e) => meter(e.data);
  for (const c of comandi) if (c.b && !["meter", "led", "ledStrum"].includes(c.b.tipo)) invia(c);
  motore.port.postMessage({ t: "bpm", v: 75 });
  riddim(ctx.sampleRate).forEach(([L, R], i) => {
    if (!deck[i]) mandaTraccia(i, L, R);
  });
  bAccendi.textContent = "Acceso";
  bPlay.disabled = bCapo.disabled = bMic.disabled = false;
}

bAccendi.addEventListener("click", () => accendi().catch(() => {}));
// tasti 1, 2, 3: i pulsanti degli strumenti, tenuti finché il tasto è giù
for (const [tipo, v] of [["keydown", 1], ["keyup", 0]]) {
  addEventListener(tipo, (e) => {
    const ctl = tastiStrum[e.key];
    if (!ctl || e.repeat || e.target.tagName === "INPUT") return;
    e.preventDefault();
    if (ctl.val !== v) imposta(ctl, v);
  });
}
addEventListener("blur", () => { for (const k in tastiStrum) if (tastiStrum[k].val) imposta(tastiStrum[k], 0); });
addEventListener("keydown", (e) => {
  if (e.code !== "Space" || e.target.tagName === "BUTTON" || bPlay.disabled) return;
  e.preventDefault();
  bPlay.click();
});
// un file lasciato fuori da una striscia non fa aprire il file al browser
for (const t of ["dragover", "drop"]) addEventListener(t, (e) => e.preventDefault());

let zoom = 1;
const scala = (d) => {
  zoom = Math.min(8, Math.max(0.4, zoom * d));
  svg.style.width = zoom * 100 + "%";
  svg.style.maxWidth = zoom > 1 ? "none" : zoom * 1400 + "px";
};
document.getElementById("piu").addEventListener("click", () => scala(1.25));
document.getElementById("meno").addEventListener("click", () => scala(0.8));
bPlay.addEventListener("click", async () => {
  await ctx.resume();
  const on = bPlay.getAttribute("aria-pressed") !== "true";
  bPlay.setAttribute("aria-pressed", on);
  bPlay.textContent = on ? "Stop" : "Play";
  motore.port.postMessage({ t: "play", on });
});
bCapo.addEventListener("click", () => motore.port.postMessage({ t: "play", on: bPlay.getAttribute("aria-pressed") === "true", riavvolgi: true }));
bMic.addEventListener("click", async () => {
  if (micNodo) {
    micNodo.disconnect();
    micNodo.mediaStream.getTracks().forEach((t) => t.stop());
    micNodo = null;
    bMic.setAttribute("aria-pressed", "false");
    return;
  }
  bMic.disabled = true;
  try {
    const s = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: false, noiseSuppression: false, autoGainControl: false } });
    micNodo = ctx.createMediaStreamSource(s);
    micNodo.connect(motore);
    bMic.setAttribute("aria-pressed", "true");
  } catch {
    avvisa("Microfono non disponibile: controlla il permesso del browser.");
  } finally {
    bMic.disabled = false;
  }
});

// ---------------------------------------------------------------- meter
let fiveFuori = "";
const dBuCampione = (x) => 20 * Math.log10((x * 4.3609) / 1.0957 + 1e-9); // 1,0 = 4,36 V di picco
const dBuMeter = (m) => 24 + 20 * Math.log10(m + 1e-9); // meter dei dispositivi: 1 = +24 dBu

function accendiSeg(ctl, dbu, basso, alto) {
  ctl.dbu = Math.max(dbu, ctl.dbu - 2);
  const n = ctl.segs.length;
  ctl.segs.forEach((s, k) => {
    const soglia = basso + ((alto - basso) * k) / (n - 1);
    const acceso = ctl.dbu >= soglia;
    const col = k >= n - Math.max(1, Math.round(n / 10)) ? "r" : k >= n - Math.max(2, Math.round(n / 4)) ? "g" : "v";
    s.setAttribute("class", "seg" + (acceso ? " " + col : ""));
  });
}

function meter(m) {
  for (const ctl of comandi) {
    const b = ctl.b;
    if (!b) continue;
    if (b.tipo === "meter") {
      const [src, i] = b.src;
      if (src === "deck") accendiSeg(ctl, dBuCampione(m.deck[i]), -24, 18);
      else if (src === "ret") accendiSeg(ctl, dBuMeter(m.ret[i]), -24, 18);
      else if (src === "five") accendiSeg(ctl, dBuCampione(m.five), -24, 18);
      else if (src === "master") accendiSeg(ctl, dBuMeter(m.master[i]), -30, 24);
    } else if (b.tipo === "ledStrum") {
      ctl.lampada.style.opacity = (0.15 + 0.85 * Math.min(1, m.ledStrum[b.i])).toFixed(2);
    } else if (b.tipo === "led") {
      // stato del LED: 0 spento, 1 verde, 2 giallo, 3 rosso (MC-MIC nel dispositivo, 5 vie in ledvie.js)
      const st = b.src[0] === "five" ? m.ledVie[b.src[1]] : b.src[0] === "mono" ? m.ledMono[b.src[1]] : m.led;
      ctl.dbu = Math.max(st, ctl.dbu - 0.2);
      ctl.led[0].setAttribute("class", "seg" + (ctl.dbu >= 1 ? " v" : ""));
      ctl.led[1].setAttribute("class", "seg" + (ctl.dbu >= 2 ? " g" : ""));
      ctl.led[2].setAttribute("class", "seg" + (ctl.dbu >= 3 ? " r" : ""));
    }
  }
  const prot = m.prot < 0.98 ? ` · volume troppo alto, abbasso di ${(-20 * Math.log10(m.prot)).toFixed(1)} dB` : "";
  stato.textContent = `${fiveFuori}${m.persi ? ` · blocchi 5-way persi ${m.persi}` : ""}${prot}`;
}
