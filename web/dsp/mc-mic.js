// GENERATO da web/tools/gen2js.mjs a partire da proto-max/MC-MIC.genexpr: non modificare.
// Il codice DSP è quello del prototipo, riga per riga; cambiano solo dichiarazioni e ingressi/uscite.
const pi = Math.PI, twopi = 2 * Math.PI, e = Math.E;
const min = Math.min, max = Math.max, abs = Math.abs, pow = Math.pow, exp = Math.exp;
const log = Math.log, tan = Math.tan, tanh = Math.tanh, sqrt = Math.sqrt;
const samplerate = globalThis.sampleRate;
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
function op1(m, i, x, g) {
	let s = 0, v = 0, lo = 0;
	s = peek(m, i);
	v = (x - s) * g / (1 + g);
	lo = v + s;
	poke(m, lo + v, i);
	return lo;
}
function svhp(m, i, x, g, k) {
	let s1 = 0, s2 = 0, fh = 0, fb = 0, fl = 0;
	s1 = peek(m, i);
	s2 = peek(m, i + 1);
	fh = (x - (k + g) * s1 - s2) / (1 + g * (k + g));
	fb = g * fh + s1;
	fl = g * fb + s2;
	poke(m, g * fh + fb, i);
	poke(m, g * fb + fl, i + 1);
	return fh;
}
export const PARAMS = {"gain":{"def":0,"min":0,"max":100},"low":{"def":50,"min":0,"max":100},"high":{"def":50,"min":0,"max":100},"snd1":{"def":0,"min":0,"max":100},"snd2":{"def":0,"min":0,"max":100},"snd3":{"def":0,"min":0,"max":100},"snd4":{"def":0,"min":0,"max":100},"mute":{"def":0,"min":0,"max":1}};
const HISTORY = {"mrm":0,"lenv":0,"llat":0,"lpk":0,"lsm":0,"s_gain":0,"s_low":50,"s_high":50,"s_snd1":0,"s_snd2":0,"s_snd3":0,"s_snd4":0};
export class Dispositivo {
	constructor() {
		this.P = {};
		for (const k in PARAMS) this.P[k] = PARAMS[k].def;
		this.H = Object.assign({}, HISTORY);
		this.D = { sv: new Float64Array(4), sa: new Float64Array(2), hb: new Float64Array(64) };
		this.meter = new Float64Array(1);
	}
	set(n, v) { const q = PARAMS[n]; if (q) this.P[n] = Math.min(q.max, Math.max(q.min, +v)); }
	// ingresso: [L, R]; uscite: un [L, R] per coppia stereo. Il meter tiene il picco del blocco.
	process(iL, iR, uscite, n) {
		const o1 = uscite[0][0], o2 = uscite[0][1];
		const o3 = uscite[1][0], o4 = uscite[1][1];
		const o5 = uscite[2][0], o6 = uscite[2][1];
		const o7 = uscite[3][0], o8 = uscite[3][1];
		const o9 = uscite[4][0], o10 = uscite[4][1];
		const { gain, low, high, snd1, snd2, snd3, snd4, mute } = this.P;
		let { mrm, lenv, llat, lpk, lsm, s_gain, s_low, s_high, s_snd1, s_snd2, s_snd3, s_snd4 } = this.H;
		const { sv, sa, hb } = this.D;
		const M = this.meter;
		M.fill(0);
		for (let __k = 0; __k < n; __k++) {
			const in1 = iL[__k], in2 = iR[__k];
			let out1 = 0, out2 = 0, out3 = 0, out4 = 0, out5 = 0, out6 = 0, out7 = 0, out8 = 0, out9 = 0, out10 = 0, out11 = 0, t10 = 0, sr4 = 0, tgu = 0, tgn = 0, gst = 0, gpa = 0, kpa = 0, ldb = 0, lgl = 0, lx = 0, hth = 0, lra = 0, lrb = 0, ala = 0, gla = 0, alb = 0, glb = 0, lgk = 0, hr1 = 0, hr2 = 0, hk = 0, ghp = 0, khp = 0, pmu = 0, gmu = 0, ts1 = 0, ls1 = 0, ts2 = 0, ls2 = 0, ts3 = 0, ls3 = 0, ts4 = 0, ls4 = 0, M_e = 0, M_o = 0, M_u0 = 0, M_u1 = 0, M_u2 = 0, M_u3 = 0, ppk = 0, pv = 0, eq = 0, M_y0 = 0, M_y1 = 0, M_y2 = 0, M_y3 = 0, d0 = 0, d1 = 0, M_v0 = 0, M_v1 = 0, M_w = 0, lec = 0, mo = 0, lre = 0, lcr = 0, lst = 0;
			t10 = exp(-1 / (0.010 * samplerate));
			s_gain = gain + t10 * (s_gain - gain);
			s_low = low + t10 * (s_low - low);
			s_high = high + t10 * (s_high - high);
			s_snd1 = snd1 + t10 * (s_snd1 - snd1);
			s_snd2 = snd2 + t10 * (s_snd2 - snd2);
			s_snd3 = snd3 + t10 * (s_snd3 - snd3);
			s_snd4 = snd4 + t10 * (s_snd4 - snd4);
			sr4 = samplerate * 4;
			tgu = 1 - s_gain / 100;
			tgn = 1 - ((tgu <= 0.5) * 0.4 * tgu + (tgu > 0.5) * (0.2 + 1.6 * (tgu - 0.5)));
			gst = (5360.0 + tgn * 5000.0) / (332.0 + (1 - tgn) * 5000.0);
			gpa = tan(190.18471790923815 / sr4);
			kpa = 1.414213562373095;
			ldb = (s_low / 100 >= 0.5) * 12.0 * (s_low / 100 - 0.5) + (s_low / 100 < 0.5) * ((s_low / 100 < 0.2) * (-30.0 + 120.0 * (s_low / 100 - 0.0)) + (s_low / 100 >= 0.2) * (-6.0 + 20.0 * (s_low / 100 - 0.2)));
			lgl = pow(10, ldb / 20);
			lx = (32.0 - lgl) / (31.0 * (lgl + 1));
			hth = (s_high / 100 >= 0.5) * 0.5 * pow(10, 0.6 * (s_high / 100 - 0.5)) + (s_high / 100 < 0.5) * (s_high / 100 >= 0.3) * 0.5 * pow(10, -3.75 * (0.5 - s_high / 100)) + (s_high / 100 < 0.3) * 0.2963799016731538 * s_high / 100;
			lra = 31000.0 * lx + 0.001;
			lrb = 31000.0 * (1 - lx) + 0.001;
			ala = 1000.0 / (1000.0 + lrb);
			gla = 1 / (2 * sr4 * lrb * 5.6e-08);
			alb = (1000.0 + lra) / 1000.0;
			glb = (1000.0 + lra) / (2 * sr4 * 1000.0 * lra * 5.6e-08);
			lgk = (1000.0 + lrb) / (1000.0 + lra);
			hr1 = 10000.0 * hth + 0.001;
			hr2 = 10000.0 * (1 - hth) + 0.001;
			hk = (1 / hr2 - 1 / hr1) / (1 / hr1 + 1 / hr2 + 2.004008016032064e-05);
			ghp = tan(13827.674747047453 / sr4);
			khp = 2.892749557082327;
			pmu = 1 / (0.001 * samplerate);
			mrm = mrm + min(max(mute - mrm, -pmu), pmu);
			gmu = pow(10, -5 * mrm) * (mrm < 1);
			ts1 = s_snd1 / 100;
			ls1 = (ts1 <= 0.5) * 0.2 * ts1 + (ts1 > 0.5) * (0.1 + 1.8 * (ts1 - 0.5));
			ts2 = s_snd2 / 100;
			ls2 = (ts2 <= 0.5) * 0.2 * ts2 + (ts2 > 0.5) * (0.1 + 1.8 * (ts2 - 0.5));
			ts3 = s_snd3 / 100;
			ls3 = (ts3 <= 0.5) * 0.2 * ts3 + (ts3 > 0.5) * (0.1 + 1.8 * (ts3 - 0.5));
			ts4 = s_snd4 / 100;
			ls4 = (ts4 <= 0.5) * 0.2 * ts4 + (ts4 > 0.5) * (0.1 + 1.8 * (ts4 - 0.5));
			M_e = in1;
			M_o = in1;
			M_e = ap(hb, 0, M_e, 0.019059005558478156);
			M_e = ap(hb, 4, M_e, 0.1559582483500435);
			M_e = ap(hb, 8, M_e, 0.3650536901969154);
			M_e = ap(hb, 12, M_e, 0.5755010797915323);
			M_e = ap(hb, 16, M_e, 0.7526447471286863);
			M_e = ap(hb, 20, M_e, 0.8980636464339091);
			M_o = ap(hb, 2, M_o, 0.07350243453590219);
			M_o = ap(hb, 6, M_o, 0.25649919975582064);
			M_o = ap(hb, 10, M_o, 0.47327898479453656);
			M_o = ap(hb, 14, M_o, 0.6688095014357188);
			M_o = ap(hb, 18, M_o, 0.8282265929955738);
			M_o = ap(hb, 22, M_o, 0.9656701590349398);
			M_u0 = M_e;
			M_u1 = M_e;
			M_u0 = ap(hb, 24, M_u0, 0.04245470986526787);
			M_u0 = ap(hb, 28, M_u0, 0.39331989319033134);
			M_u1 = ap(hb, 26, M_u1, 0.17073985049750015);
			M_u1 = ap(hb, 30, M_u1, 0.7457135887202412);
			M_u2 = M_o;
			M_u3 = M_o;
			M_u2 = ap(hb, 24, M_u2, 0.04245470986526787);
			M_u2 = ap(hb, 28, M_u2, 0.39331989319033134);
			M_u3 = ap(hb, 26, M_u3, 0.17073985049750015);
			M_u3 = ap(hb, 30, M_u3, 0.7457135887202412);
			ppk = 0;
			pv = min(max(91.32528313955623 * M_u0, -13.5), 13.5);
			pv = svhp(sv, 2, pv, gpa, kpa);
			pv = min(max(gst * pv, -13.5), 13.5);
			ppk = max(ppk, abs(pv));
			eq = pv / 4.360865946243008;
			eq = ala * eq + (1 - ala) * op1(sa, 0, eq, gla);
			eq = alb * eq + (1 - alb) * op1(sa, 1, eq, glb);
			eq = lgk * eq;
			eq = eq + hk * svhp(sv, 0, eq, ghp, khp);
			M_y0 = min(max(eq, -3.7836521927978892), 3.7836521927978892);
			pv = min(max(91.32528313955623 * M_u1, -13.5), 13.5);
			pv = svhp(sv, 2, pv, gpa, kpa);
			pv = min(max(gst * pv, -13.5), 13.5);
			ppk = max(ppk, abs(pv));
			eq = pv / 4.360865946243008;
			eq = ala * eq + (1 - ala) * op1(sa, 0, eq, gla);
			eq = alb * eq + (1 - alb) * op1(sa, 1, eq, glb);
			eq = lgk * eq;
			eq = eq + hk * svhp(sv, 0, eq, ghp, khp);
			M_y1 = min(max(eq, -3.7836521927978892), 3.7836521927978892);
			pv = min(max(91.32528313955623 * M_u2, -13.5), 13.5);
			pv = svhp(sv, 2, pv, gpa, kpa);
			pv = min(max(gst * pv, -13.5), 13.5);
			ppk = max(ppk, abs(pv));
			eq = pv / 4.360865946243008;
			eq = ala * eq + (1 - ala) * op1(sa, 0, eq, gla);
			eq = alb * eq + (1 - alb) * op1(sa, 1, eq, glb);
			eq = lgk * eq;
			eq = eq + hk * svhp(sv, 0, eq, ghp, khp);
			M_y2 = min(max(eq, -3.7836521927978892), 3.7836521927978892);
			pv = min(max(91.32528313955623 * M_u3, -13.5), 13.5);
			pv = svhp(sv, 2, pv, gpa, kpa);
			pv = min(max(gst * pv, -13.5), 13.5);
			ppk = max(ppk, abs(pv));
			eq = pv / 4.360865946243008;
			eq = ala * eq + (1 - ala) * op1(sa, 0, eq, gla);
			eq = alb * eq + (1 - alb) * op1(sa, 1, eq, glb);
			eq = lgk * eq;
			eq = eq + hk * svhp(sv, 0, eq, ghp, khp);
			M_y3 = min(max(eq, -3.7836521927978892), 3.7836521927978892);
			d0 = M_y1;
			d1 = M_y0;
			d0 = ap(hb, 32, d0, 0.04245470986526787);
			d0 = ap(hb, 36, d0, 0.39331989319033134);
			d1 = ap(hb, 34, d1, 0.17073985049750015);
			d1 = ap(hb, 38, d1, 0.7457135887202412);
			M_v0 = 0.5 * (d0 + d1);
			d0 = M_y3;
			d1 = M_y2;
			d0 = ap(hb, 32, d0, 0.04245470986526787);
			d0 = ap(hb, 36, d0, 0.39331989319033134);
			d1 = ap(hb, 34, d1, 0.17073985049750015);
			d1 = ap(hb, 38, d1, 0.7457135887202412);
			M_v1 = 0.5 * (d0 + d1);
			d0 = M_v1;
			d1 = M_v0;
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
			M_w = 0.5 * (d0 + d1);
			lec = 0.25 * max(lsm - 2.18, 0);
			mo = gmu * pow(10, -lec / 0.12200000000000001) * M_w;
			lre = 0.5 * abs(mo) * 4.360865946243008;
			lpk = (lre > lpk) * (lre + (lpk - lre) * exp(-1 / (0.002 * samplerate))) + (lre <= lpk) * lpk;
			lpk = lpk * exp(-1 / (2.0 * samplerate));
			lsm = lpk + (lsm - lpk) * exp(-1 / (0.0001 * samplerate));
			lcr = exp(-1 / (0.3 * samplerate));
			lenv = max(ppk, lcr * lenv);
			llat = (ppk >= 7.754838122143846) * 0.5 + (ppk < 7.754838122143846) * max(llat - 1 / samplerate, 0);
			lst = (llat > 0) * 3 + (llat <= 0) * ((lenv >= 0.549000495715314) + (lenv >= 3.886625865664586));
			out1 = mo;
			out2 = mo;
			out3 = ls1 * mo;
			out4 = ls1 * mo;
			out5 = ls2 * mo;
			out6 = ls2 * mo;
			out7 = ls3 * mo;
			out8 = ls3 * mo;
			out9 = ls4 * mo;
			out10 = ls4 * mo;
			out11 = lst;
			o1[__k] = out1;
			o2[__k] = out2;
			o3[__k] = out3;
			o4[__k] = out4;
			o5[__k] = out5;
			o6[__k] = out6;
			o7[__k] = out7;
			o8[__k] = out8;
			o9[__k] = out9;
			o10[__k] = out10;
			if (out11 > M[0]) M[0] = out11;
		}
		Object.assign(this.H, { mrm, lenv, llat, lpk, lsm, s_gain, s_low, s_high, s_snd1, s_snd2, s_snd3, s_snd4 });
	}
}
