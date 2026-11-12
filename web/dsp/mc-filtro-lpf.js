// GENERATO da web/tools/gen2js.mjs a partire da proto-max/MC-FILTRO-LPF.genexpr: non modificare.
// Il codice DSP è quello del prototipo, riga per riga; cambiano solo dichiarazioni e ingressi/uscite.
const pi = Math.PI, twopi = 2 * Math.PI, e = Math.E;
const min = Math.min, max = Math.max, abs = Math.abs, pow = Math.pow, exp = Math.exp;
const log = Math.log, tan = Math.tan, tanh = Math.tanh, sqrt = Math.sqrt;
const samplerate = globalThis.sampleRate;
if (!(samplerate > 0)) throw new Error("sampleRate non definito prima dell'import");
function noise() { return Math.random() * 2 - 1; }
function isnan(x) { return x !== x ? 1 : 0; }
function isinf(x) { return x === Infinity || x === -Infinity ? 1 : 0; }
function peek(m, i) { return m[i]; }
function poke(m, v, i) { m[i] = v; }
function ap(m, i, x, c) {
	let y = 0;
	y = c * (x - peek(m, i + 1)) + peek(m, i);
	poke(m, x, i);
	poke(m, y, i + 1);
	return y;
}
function aota(u) {
	let m = 0;
	m = max(abs(u), 0.000001);
	return 1.55112 * tanh(m / 1.55112) / m;
}
function spl(z) {
	return log(1 + exp(min(z, 30))) + max(z - 30, 0);
}
function alim(v, lg, lk, lw) {
	let m = 0;
	m = max(abs(v), 0.000001);
	return lg * lw * (spl((m - lk) / lw) - spl(-lk / lw)) / m;
}
function ares(u) {
	let m = 0;
	m = max(abs(u), 0.000001);
	return 0.77556 * tanh(m / 0.77556) / m;
}
function clipd(v) {
	let a = 0, t = 0, w = 0, ex = 0, f = 0, df = 0;
	a = abs(v);
	t = a / 1.1088e-05;
	w = min(a, 0.09063096 * log(t + sqrt(t * t + 1)));
	ex = exp(w / 0.09063096);
	f = (a - w) / 2200.0 - 2.52e-09 * (ex - 1 / ex);
	df = -1 / 2200.0 - 2.52e-09 * (ex + 1 / ex) / 0.09063096;
	w = w - f / df;
	ex = exp(w / 0.09063096);
	f = (a - w) / 2200.0 - 2.52e-09 * (ex - 1 / ex);
	df = -1 / 2200.0 - 2.52e-09 * (ex + 1 / ex) / 0.09063096;
	w = w - f / df;
	ex = exp(w / 0.09063096);
	f = (a - w) / 2200.0 - 2.52e-09 * (ex - 1 / ex);
	df = -1 / 2200.0 - 2.52e-09 * (ex + 1 / ex) / 0.09063096;
	w = w - f / df;
	return w * ((v >= 0) * 2 - 1);
}
function sez_a0_hp(m, i, x, g, d) {
	let s1 = 0, s2 = 0, bpv = 0, ab = 0, g1 = 0, g2 = 0, rr = 0, bp = 0, hp = 0, lp = 0;
	s1 = peek(m, i);
	s2 = peek(m, i + 1);
	bpv = peek(m, i + 3);
	ab = aota(bpv);
	g1 = g * aota(peek(m, i + 2));
	g2 = g * ab;
	rr = d * ab;
	bp = (g1 * (x - s2) + s1) / (1 + g1 * g2 + g1 * rr);
	hp = x - s2 - (g2 + rr) * bp;
	lp = g2 * bp + s2;
	poke(m, bp + g1 * hp, i);
	poke(m, lp + g2 * bp, i + 1);
	poke(m, hp, i + 2);
	poke(m, bp, i + 3);
	return hp;
}
function sez_a0_lp(m, i, x, g, d) {
	let s1 = 0, s2 = 0, bpv = 0, ab = 0, g1 = 0, g2 = 0, rr = 0, bp = 0, hp = 0, lp = 0;
	s1 = peek(m, i);
	s2 = peek(m, i + 1);
	bpv = peek(m, i + 3);
	ab = aota(bpv);
	g1 = g * aota(peek(m, i + 2));
	g2 = g * ab;
	rr = d * ab;
	bp = (g1 * (x - s2) + s1) / (1 + g1 * g2 + g1 * rr);
	hp = x - s2 - (g2 + rr) * bp;
	lp = g2 * bp + s2;
	poke(m, bp + g1 * hp, i);
	poke(m, lp + g2 * bp, i + 1);
	poke(m, hp, i + 2);
	poke(m, bp, i + 3);
	return lp;
}
function sez_a1_hp(m, i, x, g, d) {
	let s1 = 0, s2 = 0, bpv = 0, ab = 0, g1 = 0, g2 = 0, rr = 0, bp = 0, hp = 0, lp = 0;
	s1 = peek(m, i);
	s2 = peek(m, i + 1);
	bpv = peek(m, i + 3);
	ab = aota(bpv);
	g1 = g * aota(peek(m, i + 2));
	g2 = g * ab;
	rr = d * ab + alim(bpv, 1.7, 0.82, 0.06);
	bp = (g1 * (x - s2) + s1) / (1 + g1 * g2 + g1 * rr);
	hp = x - s2 - (g2 + rr) * bp;
	lp = g2 * bp + s2;
	poke(m, bp + g1 * hp, i);
	poke(m, lp + g2 * bp, i + 1);
	poke(m, hp, i + 2);
	poke(m, bp, i + 3);
	return hp;
}
function sez_a1_lp(m, i, x, g, d) {
	let s1 = 0, s2 = 0, bpv = 0, ab = 0, g1 = 0, g2 = 0, rr = 0, bp = 0, hp = 0, lp = 0;
	s1 = peek(m, i);
	s2 = peek(m, i + 1);
	bpv = peek(m, i + 3);
	ab = aota(bpv);
	g1 = g * aota(peek(m, i + 2));
	g2 = g * ab;
	rr = d * ab + alim(bpv, 1.7, 0.82, 0.06);
	bp = (g1 * (x - s2) + s1) / (1 + g1 * g2 + g1 * rr);
	hp = x - s2 - (g2 + rr) * bp;
	lp = g2 * bp + s2;
	poke(m, bp + g1 * hp, i);
	poke(m, lp + g2 * bp, i + 1);
	poke(m, hp, i + 2);
	poke(m, bp, i + 3);
	return lp;
}
export const PARAMS = {"freq_lp":{"def":100,"min":0,"max":100},"res_lp":{"def":0,"min":0,"max":100},"drive_lp":{"def":0,"min":0,"max":100}};
const HISTORY = {"s_freq_lp":100,"s_res_lp":0,"s_drive_lp":0};
export class Dispositivo {
	constructor() {
		this.P = {};
		for (const k in PARAMS) this.P[k] = PARAMS[k].def;
		this.H = Object.assign({}, HISTORY);
		this.D = { st: new Float64Array(16), hb: new Float64Array(128) };
		this.meter = new Float64Array(0);
	}
	set(n, v) { const q = PARAMS[n]; v = +v; if (q && v === v) this.P[n] = Math.min(q.max, Math.max(q.min, v)); }
	// ingresso: [L, R]; uscite: un [L, R] per coppia stereo. Il meter tiene il picco del blocco.
	process(iL, iR, uscite, n) {
		const o1 = uscite[0][0], o2 = uscite[0][1];
		const { freq_lp, res_lp, drive_lp } = this.P;
		let { s_freq_lp, s_res_lp, s_drive_lp } = this.H;
		const { st, hb } = this.D;
		const M = this.meter;
		M.fill(0);
		for (let __k = 0; __k < n; __k++) {
			const in1 = iL[__k], in2 = iR[__k];
			let out1 = 0, out2 = 0, t1 = 0, t10 = 0, t20 = 0, sr4 = 0, q1i = 0, m1 = 0, q2i = 0, m2 = 0, dq1 = 0, th = 0, f_lp = 0, g_lp1 = 0, g_lp2 = 0, od_lp = 0, tr = 0, gr = 0, d_lp = 0, L_e = 0, L_o = 0, L_u0 = 0, L_u1 = 0, L_u2 = 0, L_u3 = 0, xin = 0, alpl = 0, olp = 0, L_y0 = 0, L_y1 = 0, L_y2 = 0, L_y3 = 0, d0 = 0, d1 = 0, L_v0 = 0, L_v1 = 0, L_w = 0, R_e = 0, R_o = 0, R_u0 = 0, R_u1 = 0, R_u2 = 0, R_u3 = 0, R_y0 = 0, R_y1 = 0, R_y2 = 0, R_y3 = 0, R_v0 = 0, R_v1 = 0, R_w = 0;
			t1 = exp(-1 / (0.001 * samplerate));
			t10 = exp(-1 / (0.010 * samplerate));
			t20 = exp(-1 / (0.020 * samplerate));
			s_freq_lp = freq_lp + t10 * (s_freq_lp - freq_lp);
			s_res_lp = res_lp + t10 * (s_res_lp - res_lp);
			s_drive_lp = drive_lp + t10 * (s_drive_lp - drive_lp);
			sr4 = samplerate * 4;
			q1i = 1.8477457501847745;
			m1 = 1.0;
			q2i = 0.765345170671973;
			m2 = 1.0;
			dq1 = q1i;
			th = s_freq_lp / 100;
			f_lp = (th < 0.05) * 10 * pow(2, th / 0.05) + (th >= 0.05) * (th <= 0.95) * 20 * pow(1000, (th - 0.05) / 0.9) + (th > 0.95) * 20000 * pow(1.75, (th - 0.95) / 0.05);
			g_lp1 = tan(pi * f_lp * m1 / sr4);
			g_lp2 = tan(pi * f_lp * m2 / sr4);
			od_lp = pow(s_drive_lp / 100, 1.0);
			tr = s_res_lp / 100;
			gr = (tr <= 0.9) * pow(0.125, tr / 0.9) + (tr > 0.9) * (0.125 + -0.375 * (tr - 0.9) / 0.1);
			d_lp = (gr > 0) * gr * q2i + (gr <= 0) * 1.4142135623730951 * gr;
			L_e = in1;
			L_o = in1;
			L_e = ap(hb, 0, L_e, 0.019059005558478156);
			L_e = ap(hb, 4, L_e, 0.1559582483500435);
			L_e = ap(hb, 8, L_e, 0.3650536901969154);
			L_e = ap(hb, 12, L_e, 0.5755010797915323);
			L_e = ap(hb, 16, L_e, 0.7526447471286863);
			L_e = ap(hb, 20, L_e, 0.8980636464339091);
			L_o = ap(hb, 2, L_o, 0.07350243453590219);
			L_o = ap(hb, 6, L_o, 0.25649919975582064);
			L_o = ap(hb, 10, L_o, 0.47327898479453656);
			L_o = ap(hb, 14, L_o, 0.6688095014357188);
			L_o = ap(hb, 18, L_o, 0.8282265929955738);
			L_o = ap(hb, 22, L_o, 0.9656701590349398);
			L_u0 = L_e;
			L_u1 = L_e;
			L_u0 = ap(hb, 24, L_u0, 0.04245470986526787);
			L_u0 = ap(hb, 28, L_u0, 0.39331989319033134);
			L_u1 = ap(hb, 26, L_u1, 0.17073985049750015);
			L_u1 = ap(hb, 30, L_u1, 0.7457135887202412);
			L_u2 = L_o;
			L_u3 = L_o;
			L_u2 = ap(hb, 24, L_u2, 0.04245470986526787);
			L_u2 = ap(hb, 28, L_u2, 0.39331989319033134);
			L_u3 = ap(hb, 26, L_u3, 0.17073985049750015);
			L_u3 = ap(hb, 30, L_u3, 0.7457135887202412);
			xin = L_u0 * 4.360865946243008 + noise() * 0.00001;
			alpl = sez_a0_lp(st, 0, xin, g_lp1, dq1);
			alpl = sez_a1_lp(st, 4, alpl, g_lp2, d_lp);
			olp = alpl;
			if (od_lp > 1e-09) {
			olp = olp + od_lp * (1.171 * clipd(2 * olp) - olp);
			}
			L_y0 = olp / 4.360865946243008;
			xin = L_u1 * 4.360865946243008 + noise() * 0.00001;
			alpl = sez_a0_lp(st, 0, xin, g_lp1, dq1);
			alpl = sez_a1_lp(st, 4, alpl, g_lp2, d_lp);
			olp = alpl;
			if (od_lp > 1e-09) {
			olp = olp + od_lp * (1.171 * clipd(2 * olp) - olp);
			}
			L_y1 = olp / 4.360865946243008;
			xin = L_u2 * 4.360865946243008 + noise() * 0.00001;
			alpl = sez_a0_lp(st, 0, xin, g_lp1, dq1);
			alpl = sez_a1_lp(st, 4, alpl, g_lp2, d_lp);
			olp = alpl;
			if (od_lp > 1e-09) {
			olp = olp + od_lp * (1.171 * clipd(2 * olp) - olp);
			}
			L_y2 = olp / 4.360865946243008;
			xin = L_u3 * 4.360865946243008 + noise() * 0.00001;
			alpl = sez_a0_lp(st, 0, xin, g_lp1, dq1);
			alpl = sez_a1_lp(st, 4, alpl, g_lp2, d_lp);
			olp = alpl;
			if (od_lp > 1e-09) {
			olp = olp + od_lp * (1.171 * clipd(2 * olp) - olp);
			}
			L_y3 = olp / 4.360865946243008;
			d0 = L_y1;
			d1 = L_y0;
			d0 = ap(hb, 32, d0, 0.04245470986526787);
			d0 = ap(hb, 36, d0, 0.39331989319033134);
			d1 = ap(hb, 34, d1, 0.17073985049750015);
			d1 = ap(hb, 38, d1, 0.7457135887202412);
			L_v0 = 0.5 * (d0 + d1);
			d0 = L_y3;
			d1 = L_y2;
			d0 = ap(hb, 32, d0, 0.04245470986526787);
			d0 = ap(hb, 36, d0, 0.39331989319033134);
			d1 = ap(hb, 34, d1, 0.17073985049750015);
			d1 = ap(hb, 38, d1, 0.7457135887202412);
			L_v1 = 0.5 * (d0 + d1);
			d0 = L_v1;
			d1 = L_v0;
			d0 = ap(hb, 40, d0, 0.019059005558478156);
			d0 = ap(hb, 44, d0, 0.1559582483500435);
			d0 = ap(hb, 48, d0, 0.3650536901969154);
			d0 = ap(hb, 52, d0, 0.5755010797915323);
			d0 = ap(hb, 56, d0, 0.7526447471286863);
			d0 = ap(hb, 60, d0, 0.8980636464339091);
			d1 = ap(hb, 42, d1, 0.07350243453590219);
			d1 = ap(hb, 46, d1, 0.25649919975582064);
			d1 = ap(hb, 50, d1, 0.47327898479453656);
			d1 = ap(hb, 54, d1, 0.6688095014357188);
			d1 = ap(hb, 58, d1, 0.8282265929955738);
			d1 = ap(hb, 62, d1, 0.9656701590349398);
			L_w = 0.5 * (d0 + d1);
			out1 = L_w;
			R_e = in2;
			R_o = in2;
			R_e = ap(hb, 64, R_e, 0.019059005558478156);
			R_e = ap(hb, 68, R_e, 0.1559582483500435);
			R_e = ap(hb, 72, R_e, 0.3650536901969154);
			R_e = ap(hb, 76, R_e, 0.5755010797915323);
			R_e = ap(hb, 80, R_e, 0.7526447471286863);
			R_e = ap(hb, 84, R_e, 0.8980636464339091);
			R_o = ap(hb, 66, R_o, 0.07350243453590219);
			R_o = ap(hb, 70, R_o, 0.25649919975582064);
			R_o = ap(hb, 74, R_o, 0.47327898479453656);
			R_o = ap(hb, 78, R_o, 0.6688095014357188);
			R_o = ap(hb, 82, R_o, 0.8282265929955738);
			R_o = ap(hb, 86, R_o, 0.9656701590349398);
			R_u0 = R_e;
			R_u1 = R_e;
			R_u0 = ap(hb, 88, R_u0, 0.04245470986526787);
			R_u0 = ap(hb, 92, R_u0, 0.39331989319033134);
			R_u1 = ap(hb, 90, R_u1, 0.17073985049750015);
			R_u1 = ap(hb, 94, R_u1, 0.7457135887202412);
			R_u2 = R_o;
			R_u3 = R_o;
			R_u2 = ap(hb, 88, R_u2, 0.04245470986526787);
			R_u2 = ap(hb, 92, R_u2, 0.39331989319033134);
			R_u3 = ap(hb, 90, R_u3, 0.17073985049750015);
			R_u3 = ap(hb, 94, R_u3, 0.7457135887202412);
			xin = R_u0 * 4.360865946243008 + noise() * 0.00001;
			alpl = sez_a0_lp(st, 8, xin, g_lp1, dq1);
			alpl = sez_a1_lp(st, 12, alpl, g_lp2, d_lp);
			olp = alpl;
			if (od_lp > 1e-09) {
			olp = olp + od_lp * (1.171 * clipd(2 * olp) - olp);
			}
			R_y0 = olp / 4.360865946243008;
			xin = R_u1 * 4.360865946243008 + noise() * 0.00001;
			alpl = sez_a0_lp(st, 8, xin, g_lp1, dq1);
			alpl = sez_a1_lp(st, 12, alpl, g_lp2, d_lp);
			olp = alpl;
			if (od_lp > 1e-09) {
			olp = olp + od_lp * (1.171 * clipd(2 * olp) - olp);
			}
			R_y1 = olp / 4.360865946243008;
			xin = R_u2 * 4.360865946243008 + noise() * 0.00001;
			alpl = sez_a0_lp(st, 8, xin, g_lp1, dq1);
			alpl = sez_a1_lp(st, 12, alpl, g_lp2, d_lp);
			olp = alpl;
			if (od_lp > 1e-09) {
			olp = olp + od_lp * (1.171 * clipd(2 * olp) - olp);
			}
			R_y2 = olp / 4.360865946243008;
			xin = R_u3 * 4.360865946243008 + noise() * 0.00001;
			alpl = sez_a0_lp(st, 8, xin, g_lp1, dq1);
			alpl = sez_a1_lp(st, 12, alpl, g_lp2, d_lp);
			olp = alpl;
			if (od_lp > 1e-09) {
			olp = olp + od_lp * (1.171 * clipd(2 * olp) - olp);
			}
			R_y3 = olp / 4.360865946243008;
			d0 = R_y1;
			d1 = R_y0;
			d0 = ap(hb, 96, d0, 0.04245470986526787);
			d0 = ap(hb, 100, d0, 0.39331989319033134);
			d1 = ap(hb, 98, d1, 0.17073985049750015);
			d1 = ap(hb, 102, d1, 0.7457135887202412);
			R_v0 = 0.5 * (d0 + d1);
			d0 = R_y3;
			d1 = R_y2;
			d0 = ap(hb, 96, d0, 0.04245470986526787);
			d0 = ap(hb, 100, d0, 0.39331989319033134);
			d1 = ap(hb, 98, d1, 0.17073985049750015);
			d1 = ap(hb, 102, d1, 0.7457135887202412);
			R_v1 = 0.5 * (d0 + d1);
			d0 = R_v1;
			d1 = R_v0;
			d0 = ap(hb, 104, d0, 0.019059005558478156);
			d0 = ap(hb, 108, d0, 0.1559582483500435);
			d0 = ap(hb, 112, d0, 0.3650536901969154);
			d0 = ap(hb, 116, d0, 0.5755010797915323);
			d0 = ap(hb, 120, d0, 0.7526447471286863);
			d0 = ap(hb, 124, d0, 0.8980636464339091);
			d1 = ap(hb, 106, d1, 0.07350243453590219);
			d1 = ap(hb, 110, d1, 0.25649919975582064);
			d1 = ap(hb, 114, d1, 0.47327898479453656);
			d1 = ap(hb, 118, d1, 0.6688095014357188);
			d1 = ap(hb, 122, d1, 0.8282265929955738);
			d1 = ap(hb, 126, d1, 0.9656701590349398);
			R_w = 0.5 * (d0 + d1);
			out2 = R_w;
			o1[__k] = out1;
			o2[__k] = out2;
		}
		Object.assign(this.H, { s_freq_lp, s_res_lp, s_drive_lp });
		const fine = o1[n - 1] + o2[n - 1];
		if (!(fine - fine === 0)) {
			this.H = Object.assign({}, HISTORY);
			for (const k in this.D) this.D[k].fill(0);
			for (const u of uscite) { u[0].fill(0); u[1].fill(0); }
		}
	}
}
