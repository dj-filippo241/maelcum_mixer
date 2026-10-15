{
	"patcher": {
		"fileversion": 1,
		"appversion": {
			"major": 9,
			"minor": 0,
			"revision": 0,
			"architecture": "x64",
			"modernui": 1
		},
		"classnamespace": "box",
		"rect": [
			100.0,
			100.0,
			900.0,
			520.0
		],
		"openrect": [
			0.0,
			0.0,
			0.0,
			169.0
		],
		"bglocked": 0,
		"openinpresentation": 1,
		"default_fontsize": 10.0,
		"default_fontface": 0,
		"default_fontname": "Arial Bold",
		"gridonopen": 1,
		"gridsize": [
			8.0,
			8.0
		],
		"gridsnaponopen": 1,
		"objectsnaponopen": 1,
		"statusbarvisible": 2,
		"toolbarvisible": 1,
		"boxanimatetime": 500,
		"enablehscroll": 1,
		"enablevscroll": 1,
		"devicewidth": 0.0,
		"description": "",
		"digest": "",
		"tags": "",
		"style": "",
		"boxes": [
			{
				"box": {
					"id": "obj-in",
					"maxclass": "newobj",
					"text": "plugin~",
					"numinlets": 2,
					"numoutlets": 2,
					"outlettype": [
						"signal",
						"signal"
					],
					"patching_rect": [
						20,
						20,
						60,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-gen",
					"maxclass": "newobj",
					"text": "gen~",
					"numinlets": 2,
					"numoutlets": 2,
					"outlettype": [
						"signal",
						"signal"
					],
					"patching_rect": [
						20,
						300,
						300,
						22
					],
					"patcher": {
						"fileversion": 1,
						"appversion": {
							"major": 9,
							"minor": 0,
							"revision": 0,
							"architecture": "x64",
							"modernui": 1
						},
						"classnamespace": "dsp.gen",
						"rect": [
							60.0,
							60.0,
							700.0,
							640.0
						],
						"bglocked": 0,
						"openinpresentation": 0,
						"default_fontsize": 12.0,
						"default_fontface": 0,
						"default_fontname": "Arial",
						"gridonopen": 1,
						"gridsize": [
							15.0,
							15.0
						],
						"gridsnaponopen": 1,
						"objectsnaponopen": 1,
						"statusbarvisible": 2,
						"toolbarvisible": 1,
						"boxanimatetime": 200,
						"enablehscroll": 1,
						"enablevscroll": 1,
						"devicewidth": 0.0,
						"description": "",
						"digest": "",
						"tags": "",
						"style": "",
						"boxes": [
							{
								"box": {
									"id": "obj-1",
									"maxclass": "newobj",
									"text": "in 1",
									"numinlets": 0,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										20,
										20,
										30,
										22
									]
								}
							},
							{
								"box": {
									"id": "obj-2",
									"maxclass": "newobj",
									"text": "in 2",
									"numinlets": 0,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										400,
										20,
										30,
										22
									]
								}
							},
							{
								"box": {
									"id": "obj-3",
									"maxclass": "codebox",
									"code": "// MC-CHANNEL - prototipo Max P0 del canale maelcum_mixer.\n// GENERATO da proto-max/coefficienti/genera.py: non modificare a mano.\n// GAIN -inf..0..+10 dB, isolator a 4 bande (0..+6 dB, silenzio a\n// fondo corsa), fader. Banca a 4x della frequenza di campionamento.\n\n// biquad in forma trasposta II; stato in m[i], m[i+1]\nbq(m, i, x, b0, b1, b2, a1, a2) {\n\ty = b0 * x + peek(m, i);\n\tpoke(m, b1 * x - a1 * y + peek(m, i + 1), i);\n\tpoke(m, b2 * x - a2 * y, i + 1);\n\treturn y;\n}\n\n// allpass del 1o ordine del halfband; stato in m[i] (x), m[i+1] (y)\nap(m, i, x, c) {\n\ty = c * (x - peek(m, i + 1)) + peek(m, i);\n\tpoke(m, x, i);\n\tpoke(m, y, i + 1);\n\treturn y;\n}\n\nParam gain(50.0, min=0, max=100);\nParam low(50.0, min=0, max=100);\nParam lowmid(50.0, min=0, max=100);\nParam midhigh(50.0, min=0, max=100);\nParam high(50.0, min=0, max=100);\nParam fader(100.0, min=0, max=100);\nParam incroci(0, min=0, max=2);\nParam curva(0, min=0, max=1);\nParam eqtipo(0, min=0, max=1);\nData st(180);\nData hb(128);\nHistory s_gain(50.0);\nHistory s_low(50.0);\nHistory s_lowmid(50.0);\nHistory s_midhigh(50.0);\nHistory s_high(50.0);\nHistory s_fader(100.0);\nHistory s_x(0);\nHistory s_c(0);\nHistory s_t(0);\n\n// manopole lisciate: 10 ms (selettore 20 ms, dissolvenza A/B)\nt10 = exp(-1 / (0.010 * samplerate));\nt20 = exp(-1 / (0.020 * samplerate));\ns_gain = gain + t10 * (s_gain - gain);\ns_low = low + t10 * (s_low - low);\ns_lowmid = lowmid + t10 * (s_lowmid - lowmid);\ns_midhigh = midhigh + t10 * (s_midhigh - midhigh);\ns_high = high + t10 * (s_high - high);\ns_fader = fader + t10 * (s_fader - fader);\ns_x = incroci + t20 * (s_x - incroci);\ns_c = curva + t20 * (s_c - curva);\ns_t = eqtipo + t20 * (s_t - eqtipo);\n\n// GAIN: fondo corsa muto, meta CCW -100..0 dB, meta CW 0..+10 dB\ntg = s_gain / 100;\ng_gain = pow(10, min(200 * tg - 100, 20 * tg - 10) / 20) * (tg > 0);\n// bande: pot lineare x2, oppure curva Pioneer ideale (docs/09 \u00a77):\n// taglio (2 theta)^1,5, boost uguale; a fondo corsa il contatto da silenzio\nx_low = 2 * s_low / 100;\ng_low = ((1 - s_c) * x_low + s_c * (pow(min(x_low, 1), 1.5) + max(x_low - 1, 0))) * max(low > 0, s_low > 0.001);\nx_lowmid = 2 * s_lowmid / 100;\ng_lowmid = ((1 - s_c) * x_lowmid + s_c * (pow(min(x_lowmid, 1), 1.5) + max(x_lowmid - 1, 0))) * max(lowmid > 0, s_lowmid > 0.001);\nx_midhigh = 2 * s_midhigh / 100;\ng_midhigh = ((1 - s_c) * x_midhigh + s_c * (pow(min(x_midhigh, 1), 1.5) + max(x_midhigh - 1, 0))) * max(midhigh > 0, s_midhigh > 0.001);\nx_high = 2 * s_high / 100;\ng_high = ((1 - s_c) * x_high + s_c * (pow(min(x_high, 1), 1.5) + max(x_high - 1, 0))) * max(high > 0, s_high > 0.001);\n// fader [PROVVISORIO]: curva quadratica, -12 dB a meta corsa\ntf = s_fader / 100;\ng_fader = tf * tf;\n\n// coefficienti degli incroci (bilineare con prewarp)\n// LR4: Q 0,7071 due volte; LR2: Q 0,5 una volta\nsr4 = samplerate * 4;\nA1_k = tan(pi * 150.0 / sr4);\nA1_kk = A1_k * A1_k;\nA1_n = 1 / (1 + A1_k * 1.4142135623730951 + A1_kk);\nA1_a1 = 2 * (A1_kk - 1) * A1_n;\nA1_a2 = (1 - A1_k * 1.4142135623730951 + A1_kk) * A1_n;\nA1_lb = A1_kk * A1_n;\nA2_k = tan(pi * 500.0 / sr4);\nA2_kk = A2_k * A2_k;\nA2_n = 1 / (1 + A2_k * 1.4142135623730951 + A2_kk);\nA2_a1 = 2 * (A2_kk - 1) * A2_n;\nA2_a2 = (1 - A2_k * 1.4142135623730951 + A2_kk) * A2_n;\nA2_lb = A2_kk * A2_n;\nA3_k = tan(pi * 2500.0 / sr4);\nA3_kk = A3_k * A3_k;\nA3_n = 1 / (1 + A3_k * 1.4142135623730951 + A3_kk);\nA3_a1 = 2 * (A3_kk - 1) * A3_n;\nA3_a2 = (1 - A3_k * 1.4142135623730951 + A3_kk) * A3_n;\nA3_lb = A3_kk * A3_n;\nC1_k = tan(pi * 150.0 / sr4);\nC1_kk = C1_k * C1_k;\nC1_n = 1 / (1 + C1_k * 2.0 + C1_kk);\nC1_a1 = 2 * (C1_kk - 1) * C1_n;\nC1_a2 = (1 - C1_k * 2.0 + C1_kk) * C1_n;\nC1_lb = C1_kk * C1_n;\nC2_k = tan(pi * 350.0 / sr4);\nC2_kk = C2_k * C2_k;\nC2_n = 1 / (1 + C2_k * 1.4142135623730951 + C2_kk);\nC2_a1 = 2 * (C2_kk - 1) * C2_n;\nC2_a2 = (1 - C2_k * 1.4142135623730951 + C2_kk) * C2_n;\nC2_lb = C2_kk * C2_n;\nC3_k = tan(pi * 3150.0 / sr4);\nC3_kk = C3_k * C3_k;\nC3_n = 1 / (1 + C3_k * 1.4142135623730951 + C3_kk);\nC3_a1 = 2 * (C3_kk - 1) * C3_n;\nC3_a2 = (1 - C3_k * 1.4142135623730951 + C3_kk) * C3_n;\nC3_lb = C3_kk * C3_n;\nD1_k = tan(pi * 150.0 / sr4);\nD1_kk = D1_k * D1_k;\nD1_n = 1 / (1 + D1_k * 2.0 + D1_kk);\nD1_a1 = 2 * (D1_kk - 1) * D1_n;\nD1_a2 = (1 - D1_k * 2.0 + D1_kk) * D1_n;\nD1_lb = D1_kk * D1_n;\nD2_k = tan(pi * 700.0 / sr4);\nD2_kk = D2_k * D2_k;\nD2_n = 1 / (1 + D2_k * 1.4142135623730951 + D2_kk);\nD2_a1 = 2 * (D2_kk - 1) * D2_n;\nD2_a2 = (1 - D2_k * 1.4142135623730951 + D2_kk) * D2_n;\nD2_lb = D2_kk * D2_n;\nD3_k = tan(pi * 3150.0 / sr4);\nD3_kk = D3_k * D3_k;\nD3_n = 1 / (1 + D3_k * 1.4142135623730951 + D3_kk);\nD3_a1 = 2 * (D3_kk - 1) * D3_n;\nD3_a2 = (1 - D3_k * 1.4142135623730951 + D3_kk) * D3_n;\nD3_lb = D3_kk * D3_n;\n\n// EQ in serie (B5, archiviato: confronto a orecchio). Law eq-serie \u00a710:\n// LOW e HIGH a tratti (kill negli ultimi 5 %), medi pot lineare caricato\nsk = 2 * sr4;\nsk2 = sk * sk;\nsr_tl = s_low / 100;\nsr_xl = 0.999 - 0.029000 * min(max(sr_tl / 0.05, 0), 1) - 0.470000 * min(max((sr_tl - 0.05) / 0.45, 0), 1) - 0.177000 * min(max((sr_tl - 0.5) / 0.5, 0), 1);\nsr_th = s_high / 100;\nsr_xh = 0.999 - 0.029000 * min(max(sr_th / 0.05, 0), 1) - 0.470000 * min(max((sr_th - 0.05) / 0.45, 0), 1) - 0.177000 * min(max((sr_th - 0.5) / 0.5, 0), 1);\nsr_gh = (1000.0 + (1 - sr_xh) * 31000.0) / (1000.0 + sr_xh * 31000.0);\nsr_chi = (sr_th <= 0.5) * (1 - sr_gh) / 0.9677500078200757 - (sr_th > 0.5) * (sr_gh - 1) / 0.9964587305911197;\nsr_tlm = s_lowmid / 100;\nsr_clm = (1 - 2 * sr_tlm) / (1 + 0.20040080160320642 * sr_tlm * (1 - sr_tlm));\nsr_tmh = s_midhigh / 100;\nsr_cmh = (1 - 2 * sr_tmh) / (1 + 0.20040080160320642 * sr_tmh * (1 - sr_tmh));\n// cella LOW: Baxandall, (R + Zb) / (R + Za)\nsr_ra = 31000.0 * sr_xl + 0.001;\nsr_rb = 31000.0 * (1 - sr_xl) + 0.001;\nsr_na0 = 1000.0 + sr_rb;\nsr_na1 = 9.999999999999999e-05 * sr_rb;\nsr_ta = sr_ra * 1e-07;\nsr_nb0 = 1000.0 + sr_ra;\nsr_nb1 = 9.999999999999999e-05 * sr_ra;\nsr_tb = sr_rb * 1e-07;\nsl_ai = 1 / (sr_nb0 + (sr_nb1 + sr_nb0 * sr_tb) * sk + (sr_nb1 * sr_tb) * sk2);\nsl_b0 = (sr_na0 + (sr_na1 + sr_na0 * sr_ta) * sk + (sr_na1 * sr_ta) * sk2) * sl_ai;\nsl_b1 = (2 * (sr_na0) - 2 * (sr_na1 * sr_ta) * sk2) * sl_ai;\nsl_b2 = (sr_na0 - (sr_na1 + sr_na0 * sr_ta) * sk + (sr_na1 * sr_ta) * sk2) * sl_ai;\nsl_a1 = (2 * (sr_nb0) - 2 * (sr_nb1 * sr_tb) * sk2) * sl_ai;\nsl_a2 = (sr_nb0 - (sr_nb1 + sr_nb0 * sr_tb) * sk + (sr_nb1 * sr_tb) * sk2) * sl_ai;\n// passa-banda MFB dei medi e passa-alto Sallen-Key della HIGH\nslm_ai = 1 / (0.0002506397711877164 + (2e-07) * sk + (1.0199999999999998e-10) * sk2);\nslm_b0 = (0.0 + (-1.9960861056751465e-07) * sk + (0.0) * sk2) * slm_ai;\nslm_b1 = (2 * (0.0) - 2 * (0.0) * sk2) * slm_ai;\nslm_b2 = (0.0 - (-1.9960861056751465e-07) * sk + (0.0) * sk2) * slm_ai;\nslm_a1 = (2 * (0.0002506397711877164) - 2 * (1.0199999999999998e-10) * sk2) * slm_ai;\nslm_a2 = (0.0002506397711877164 - (2e-07) * sk + (1.0199999999999998e-10) * sk2) * slm_ai;\nsmh_ai = 1 / (0.00037474795712618065 + (6.6e-08) * sk + (9.430739999999999e-12) * sk2);\nsmh_b0 = (0.0 + (-6.615277777777777e-08) * sk + (0.0) * sk2) * smh_ai;\nsmh_b1 = (2 * (0.0) - 2 * (0.0) * sk2) * smh_ai;\nsmh_b2 = (0.0 - (-6.615277777777777e-08) * sk + (0.0) * sk2) * smh_ai;\nsmh_a1 = (2 * (0.00037474795712618065) - 2 * (9.430739999999999e-12) * sk2) * smh_ai;\nsmh_a2 = (0.00037474795712618065 - (6.6e-08) * sk + (9.430739999999999e-12) * sk2) * smh_ai;\nshi_ai = 1 / (0.0004347826086956522 + (2e-08) * sk + (4.600000000000001e-13) * sk2);\nshi_b0 = (0.0 + (0.0) * sk + (4.600000000000001e-13) * sk2) * shi_ai;\nshi_b1 = (2 * (0.0) - 2 * (4.600000000000001e-13) * sk2) * shi_ai;\nshi_b2 = (0.0 - (0.0) * sk + (4.600000000000001e-13) * sk2) * shi_ai;\nshi_a1 = (2 * (0.0004347826086956522) - 2 * (4.600000000000001e-13) * sk2) * shi_ai;\nshi_a2 = (0.0004347826086956522 - (2e-08) * sk + (4.600000000000001e-13) * sk2) * shi_ai;\n\n// pesi: dissolvenza fra varianti vicine (1 - |s_x - i|) e fra isolator e serie\nw_A = max(0, 1 - abs(s_x - 0)) * (1 - s_t);\non_A = w_A > 1e-05;\nw_C = max(0, 1 - abs(s_x - 1)) * (1 - s_t);\non_C = w_C > 1e-05;\nw_D = max(0, 1 - abs(s_x - 2)) * (1 - s_t);\non_D = w_D > 1e-05;\nw_S = s_t;\non_S = w_S > 1e-05;\n\n// ===== lato L =====\nL_e = in1;\nL_o = in1;\nL_e = ap(hb, 0, L_e, 0.019059005558478156);\nL_e = ap(hb, 4, L_e, 0.1559582483500435);\nL_e = ap(hb, 8, L_e, 0.3650536901969154);\nL_e = ap(hb, 12, L_e, 0.5755010797915323);\nL_e = ap(hb, 16, L_e, 0.7526447471286863);\nL_e = ap(hb, 20, L_e, 0.8980636464339091);\nL_o = ap(hb, 2, L_o, 0.07350243453590219);\nL_o = ap(hb, 6, L_o, 0.25649919975582064);\nL_o = ap(hb, 10, L_o, 0.47327898479453656);\nL_o = ap(hb, 14, L_o, 0.6688095014357188);\nL_o = ap(hb, 18, L_o, 0.8282265929955738);\nL_o = ap(hb, 22, L_o, 0.9656701590349398);\nL_u0 = L_e;\nL_u1 = L_e;\nL_u0 = ap(hb, 24, L_u0, 0.04245470986526787);\nL_u0 = ap(hb, 28, L_u0, 0.39331989319033134);\nL_u1 = ap(hb, 26, L_u1, 0.17073985049750015);\nL_u1 = ap(hb, 30, L_u1, 0.7457135887202412);\nL_u2 = L_o;\nL_u3 = L_o;\nL_u2 = ap(hb, 24, L_u2, 0.04245470986526787);\nL_u2 = ap(hb, 28, L_u2, 0.39331989319033134);\nL_u3 = ap(hb, 26, L_u3, 0.17073985049750015);\nL_u3 = ap(hb, 30, L_u3, 0.7457135887202412);\nL0A = 0;\nif (on_A) {\nL0Al = bq(st, 0, L_u0, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL0Al = bq(st, 2, L0Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL0Al = bq(st, 4, L0Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nL0Al = bq(st, 6, L0Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL0Ah1 = bq(st, 8, L_u0, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL0Ah1 = bq(st, 10, L0Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL0Alm = bq(st, 12, L0Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL0Alm = bq(st, 14, L0Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL0Alm = bq(st, 16, L0Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL0Ah2 = bq(st, 18, L0Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL0Ah2 = bq(st, 20, L0Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL0Amh = bq(st, 22, L0Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL0Amh = bq(st, 24, L0Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL0Ahi = bq(st, 26, L0Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL0Ahi = bq(st, 28, L0Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL0A = g_low * L0Al + g_lowmid * L0Alm + g_midhigh * L0Amh + g_high * L0Ahi;\n}\nL0C = 0;\nif (on_C) {\nL0Cl = bq(st, 30, L_u0, C1_lb, 2 * C1_lb, C1_lb, C1_a1, C1_a2);\nL0Cl = bq(st, 32, L0Cl, C2_a2, C2_a1, 1, C2_a1, C2_a2);\nL0Cl = bq(st, 34, L0Cl, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nL0Ch1 = bq(st, 36, L_u0, C1_n, -2 * C1_n, C1_n, C1_a1, C1_a2);\nL0Ch1 = -L0Ch1;\nL0Clm = bq(st, 38, L0Ch1, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nL0Clm = bq(st, 40, L0Clm, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nL0Clm = bq(st, 42, L0Clm, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nL0Ch2 = bq(st, 44, L0Ch1, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nL0Ch2 = bq(st, 46, L0Ch2, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nL0Cmh = bq(st, 48, L0Ch2, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nL0Cmh = bq(st, 50, L0Cmh, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nL0Chi = bq(st, 52, L0Ch2, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nL0Chi = bq(st, 54, L0Chi, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nL0C = g_low * L0Cl + g_lowmid * L0Clm + g_midhigh * L0Cmh + g_high * L0Chi;\n}\nL0D = 0;\nif (on_D) {\nL0Dl = bq(st, 56, L_u0, D1_lb, 2 * D1_lb, D1_lb, D1_a1, D1_a2);\nL0Dl = bq(st, 58, L0Dl, D2_a2, D2_a1, 1, D2_a1, D2_a2);\nL0Dl = bq(st, 60, L0Dl, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nL0Dh1 = bq(st, 62, L_u0, D1_n, -2 * D1_n, D1_n, D1_a1, D1_a2);\nL0Dh1 = -L0Dh1;\nL0Dlm = bq(st, 64, L0Dh1, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nL0Dlm = bq(st, 66, L0Dlm, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nL0Dlm = bq(st, 68, L0Dlm, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nL0Dh2 = bq(st, 70, L0Dh1, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nL0Dh2 = bq(st, 72, L0Dh2, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nL0Dmh = bq(st, 74, L0Dh2, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nL0Dmh = bq(st, 76, L0Dmh, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nL0Dhi = bq(st, 78, L0Dh2, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nL0Dhi = bq(st, 80, L0Dhi, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nL0D = g_low * L0Dl + g_lowmid * L0Dlm + g_midhigh * L0Dmh + g_high * L0Dhi;\n}\nL0s4 = 0;\nif (on_S) {\nL0s1 = bq(st, 82, L_u0, sl_b0, sl_b1, sl_b2, sl_a1, sl_a2);\nL0sb = bq(st, 84, L0s1, slm_b0, slm_b1, slm_b2, slm_a1, slm_a2);\nL0s2 = L0s1 + sr_clm * L0sb;\nL0sb = bq(st, 86, L0s2, smh_b0, smh_b1, smh_b2, smh_a1, smh_a2);\nL0s3 = L0s2 + sr_cmh * L0sb;\nL0sb = bq(st, 88, L0s3, shi_b0, shi_b1, shi_b2, shi_a1, shi_a2);\nL0s4 = L0s3 - sr_chi * L0sb;\n}\nL_y0 = w_A * L0A + w_C * L0C + w_D * L0D + w_S * L0s4;\nL1A = 0;\nif (on_A) {\nL1Al = bq(st, 0, L_u1, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL1Al = bq(st, 2, L1Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL1Al = bq(st, 4, L1Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nL1Al = bq(st, 6, L1Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL1Ah1 = bq(st, 8, L_u1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL1Ah1 = bq(st, 10, L1Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL1Alm = bq(st, 12, L1Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL1Alm = bq(st, 14, L1Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL1Alm = bq(st, 16, L1Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL1Ah2 = bq(st, 18, L1Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL1Ah2 = bq(st, 20, L1Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL1Amh = bq(st, 22, L1Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL1Amh = bq(st, 24, L1Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL1Ahi = bq(st, 26, L1Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL1Ahi = bq(st, 28, L1Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL1A = g_low * L1Al + g_lowmid * L1Alm + g_midhigh * L1Amh + g_high * L1Ahi;\n}\nL1C = 0;\nif (on_C) {\nL1Cl = bq(st, 30, L_u1, C1_lb, 2 * C1_lb, C1_lb, C1_a1, C1_a2);\nL1Cl = bq(st, 32, L1Cl, C2_a2, C2_a1, 1, C2_a1, C2_a2);\nL1Cl = bq(st, 34, L1Cl, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nL1Ch1 = bq(st, 36, L_u1, C1_n, -2 * C1_n, C1_n, C1_a1, C1_a2);\nL1Ch1 = -L1Ch1;\nL1Clm = bq(st, 38, L1Ch1, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nL1Clm = bq(st, 40, L1Clm, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nL1Clm = bq(st, 42, L1Clm, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nL1Ch2 = bq(st, 44, L1Ch1, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nL1Ch2 = bq(st, 46, L1Ch2, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nL1Cmh = bq(st, 48, L1Ch2, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nL1Cmh = bq(st, 50, L1Cmh, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nL1Chi = bq(st, 52, L1Ch2, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nL1Chi = bq(st, 54, L1Chi, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nL1C = g_low * L1Cl + g_lowmid * L1Clm + g_midhigh * L1Cmh + g_high * L1Chi;\n}\nL1D = 0;\nif (on_D) {\nL1Dl = bq(st, 56, L_u1, D1_lb, 2 * D1_lb, D1_lb, D1_a1, D1_a2);\nL1Dl = bq(st, 58, L1Dl, D2_a2, D2_a1, 1, D2_a1, D2_a2);\nL1Dl = bq(st, 60, L1Dl, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nL1Dh1 = bq(st, 62, L_u1, D1_n, -2 * D1_n, D1_n, D1_a1, D1_a2);\nL1Dh1 = -L1Dh1;\nL1Dlm = bq(st, 64, L1Dh1, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nL1Dlm = bq(st, 66, L1Dlm, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nL1Dlm = bq(st, 68, L1Dlm, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nL1Dh2 = bq(st, 70, L1Dh1, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nL1Dh2 = bq(st, 72, L1Dh2, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nL1Dmh = bq(st, 74, L1Dh2, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nL1Dmh = bq(st, 76, L1Dmh, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nL1Dhi = bq(st, 78, L1Dh2, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nL1Dhi = bq(st, 80, L1Dhi, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nL1D = g_low * L1Dl + g_lowmid * L1Dlm + g_midhigh * L1Dmh + g_high * L1Dhi;\n}\nL1s4 = 0;\nif (on_S) {\nL1s1 = bq(st, 82, L_u1, sl_b0, sl_b1, sl_b2, sl_a1, sl_a2);\nL1sb = bq(st, 84, L1s1, slm_b0, slm_b1, slm_b2, slm_a1, slm_a2);\nL1s2 = L1s1 + sr_clm * L1sb;\nL1sb = bq(st, 86, L1s2, smh_b0, smh_b1, smh_b2, smh_a1, smh_a2);\nL1s3 = L1s2 + sr_cmh * L1sb;\nL1sb = bq(st, 88, L1s3, shi_b0, shi_b1, shi_b2, shi_a1, shi_a2);\nL1s4 = L1s3 - sr_chi * L1sb;\n}\nL_y1 = w_A * L1A + w_C * L1C + w_D * L1D + w_S * L1s4;\nL2A = 0;\nif (on_A) {\nL2Al = bq(st, 0, L_u2, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL2Al = bq(st, 2, L2Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL2Al = bq(st, 4, L2Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nL2Al = bq(st, 6, L2Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL2Ah1 = bq(st, 8, L_u2, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL2Ah1 = bq(st, 10, L2Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL2Alm = bq(st, 12, L2Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL2Alm = bq(st, 14, L2Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL2Alm = bq(st, 16, L2Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL2Ah2 = bq(st, 18, L2Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL2Ah2 = bq(st, 20, L2Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL2Amh = bq(st, 22, L2Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL2Amh = bq(st, 24, L2Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL2Ahi = bq(st, 26, L2Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL2Ahi = bq(st, 28, L2Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL2A = g_low * L2Al + g_lowmid * L2Alm + g_midhigh * L2Amh + g_high * L2Ahi;\n}\nL2C = 0;\nif (on_C) {\nL2Cl = bq(st, 30, L_u2, C1_lb, 2 * C1_lb, C1_lb, C1_a1, C1_a2);\nL2Cl = bq(st, 32, L2Cl, C2_a2, C2_a1, 1, C2_a1, C2_a2);\nL2Cl = bq(st, 34, L2Cl, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nL2Ch1 = bq(st, 36, L_u2, C1_n, -2 * C1_n, C1_n, C1_a1, C1_a2);\nL2Ch1 = -L2Ch1;\nL2Clm = bq(st, 38, L2Ch1, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nL2Clm = bq(st, 40, L2Clm, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nL2Clm = bq(st, 42, L2Clm, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nL2Ch2 = bq(st, 44, L2Ch1, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nL2Ch2 = bq(st, 46, L2Ch2, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nL2Cmh = bq(st, 48, L2Ch2, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nL2Cmh = bq(st, 50, L2Cmh, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nL2Chi = bq(st, 52, L2Ch2, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nL2Chi = bq(st, 54, L2Chi, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nL2C = g_low * L2Cl + g_lowmid * L2Clm + g_midhigh * L2Cmh + g_high * L2Chi;\n}\nL2D = 0;\nif (on_D) {\nL2Dl = bq(st, 56, L_u2, D1_lb, 2 * D1_lb, D1_lb, D1_a1, D1_a2);\nL2Dl = bq(st, 58, L2Dl, D2_a2, D2_a1, 1, D2_a1, D2_a2);\nL2Dl = bq(st, 60, L2Dl, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nL2Dh1 = bq(st, 62, L_u2, D1_n, -2 * D1_n, D1_n, D1_a1, D1_a2);\nL2Dh1 = -L2Dh1;\nL2Dlm = bq(st, 64, L2Dh1, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nL2Dlm = bq(st, 66, L2Dlm, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nL2Dlm = bq(st, 68, L2Dlm, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nL2Dh2 = bq(st, 70, L2Dh1, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nL2Dh2 = bq(st, 72, L2Dh2, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nL2Dmh = bq(st, 74, L2Dh2, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nL2Dmh = bq(st, 76, L2Dmh, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nL2Dhi = bq(st, 78, L2Dh2, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nL2Dhi = bq(st, 80, L2Dhi, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nL2D = g_low * L2Dl + g_lowmid * L2Dlm + g_midhigh * L2Dmh + g_high * L2Dhi;\n}\nL2s4 = 0;\nif (on_S) {\nL2s1 = bq(st, 82, L_u2, sl_b0, sl_b1, sl_b2, sl_a1, sl_a2);\nL2sb = bq(st, 84, L2s1, slm_b0, slm_b1, slm_b2, slm_a1, slm_a2);\nL2s2 = L2s1 + sr_clm * L2sb;\nL2sb = bq(st, 86, L2s2, smh_b0, smh_b1, smh_b2, smh_a1, smh_a2);\nL2s3 = L2s2 + sr_cmh * L2sb;\nL2sb = bq(st, 88, L2s3, shi_b0, shi_b1, shi_b2, shi_a1, shi_a2);\nL2s4 = L2s3 - sr_chi * L2sb;\n}\nL_y2 = w_A * L2A + w_C * L2C + w_D * L2D + w_S * L2s4;\nL3A = 0;\nif (on_A) {\nL3Al = bq(st, 0, L_u3, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL3Al = bq(st, 2, L3Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL3Al = bq(st, 4, L3Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nL3Al = bq(st, 6, L3Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL3Ah1 = bq(st, 8, L_u3, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL3Ah1 = bq(st, 10, L3Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL3Alm = bq(st, 12, L3Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL3Alm = bq(st, 14, L3Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL3Alm = bq(st, 16, L3Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL3Ah2 = bq(st, 18, L3Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL3Ah2 = bq(st, 20, L3Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL3Amh = bq(st, 22, L3Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL3Amh = bq(st, 24, L3Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL3Ahi = bq(st, 26, L3Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL3Ahi = bq(st, 28, L3Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL3A = g_low * L3Al + g_lowmid * L3Alm + g_midhigh * L3Amh + g_high * L3Ahi;\n}\nL3C = 0;\nif (on_C) {\nL3Cl = bq(st, 30, L_u3, C1_lb, 2 * C1_lb, C1_lb, C1_a1, C1_a2);\nL3Cl = bq(st, 32, L3Cl, C2_a2, C2_a1, 1, C2_a1, C2_a2);\nL3Cl = bq(st, 34, L3Cl, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nL3Ch1 = bq(st, 36, L_u3, C1_n, -2 * C1_n, C1_n, C1_a1, C1_a2);\nL3Ch1 = -L3Ch1;\nL3Clm = bq(st, 38, L3Ch1, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nL3Clm = bq(st, 40, L3Clm, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nL3Clm = bq(st, 42, L3Clm, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nL3Ch2 = bq(st, 44, L3Ch1, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nL3Ch2 = bq(st, 46, L3Ch2, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nL3Cmh = bq(st, 48, L3Ch2, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nL3Cmh = bq(st, 50, L3Cmh, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nL3Chi = bq(st, 52, L3Ch2, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nL3Chi = bq(st, 54, L3Chi, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nL3C = g_low * L3Cl + g_lowmid * L3Clm + g_midhigh * L3Cmh + g_high * L3Chi;\n}\nL3D = 0;\nif (on_D) {\nL3Dl = bq(st, 56, L_u3, D1_lb, 2 * D1_lb, D1_lb, D1_a1, D1_a2);\nL3Dl = bq(st, 58, L3Dl, D2_a2, D2_a1, 1, D2_a1, D2_a2);\nL3Dl = bq(st, 60, L3Dl, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nL3Dh1 = bq(st, 62, L_u3, D1_n, -2 * D1_n, D1_n, D1_a1, D1_a2);\nL3Dh1 = -L3Dh1;\nL3Dlm = bq(st, 64, L3Dh1, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nL3Dlm = bq(st, 66, L3Dlm, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nL3Dlm = bq(st, 68, L3Dlm, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nL3Dh2 = bq(st, 70, L3Dh1, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nL3Dh2 = bq(st, 72, L3Dh2, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nL3Dmh = bq(st, 74, L3Dh2, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nL3Dmh = bq(st, 76, L3Dmh, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nL3Dhi = bq(st, 78, L3Dh2, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nL3Dhi = bq(st, 80, L3Dhi, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nL3D = g_low * L3Dl + g_lowmid * L3Dlm + g_midhigh * L3Dmh + g_high * L3Dhi;\n}\nL3s4 = 0;\nif (on_S) {\nL3s1 = bq(st, 82, L_u3, sl_b0, sl_b1, sl_b2, sl_a1, sl_a2);\nL3sb = bq(st, 84, L3s1, slm_b0, slm_b1, slm_b2, slm_a1, slm_a2);\nL3s2 = L3s1 + sr_clm * L3sb;\nL3sb = bq(st, 86, L3s2, smh_b0, smh_b1, smh_b2, smh_a1, smh_a2);\nL3s3 = L3s2 + sr_cmh * L3sb;\nL3sb = bq(st, 88, L3s3, shi_b0, shi_b1, shi_b2, shi_a1, shi_a2);\nL3s4 = L3s3 - sr_chi * L3sb;\n}\nL_y3 = w_A * L3A + w_C * L3C + w_D * L3D + w_S * L3s4;\nif (on_A == 0) {\npoke(st, 0, 0);\npoke(st, 0, 1);\npoke(st, 0, 2);\npoke(st, 0, 3);\npoke(st, 0, 4);\npoke(st, 0, 5);\npoke(st, 0, 6);\npoke(st, 0, 7);\npoke(st, 0, 8);\npoke(st, 0, 9);\npoke(st, 0, 10);\npoke(st, 0, 11);\npoke(st, 0, 12);\npoke(st, 0, 13);\npoke(st, 0, 14);\npoke(st, 0, 15);\npoke(st, 0, 16);\npoke(st, 0, 17);\npoke(st, 0, 18);\npoke(st, 0, 19);\npoke(st, 0, 20);\npoke(st, 0, 21);\npoke(st, 0, 22);\npoke(st, 0, 23);\npoke(st, 0, 24);\npoke(st, 0, 25);\npoke(st, 0, 26);\npoke(st, 0, 27);\npoke(st, 0, 28);\npoke(st, 0, 29);\n}\nif (on_C == 0) {\npoke(st, 0, 30);\npoke(st, 0, 31);\npoke(st, 0, 32);\npoke(st, 0, 33);\npoke(st, 0, 34);\npoke(st, 0, 35);\npoke(st, 0, 36);\npoke(st, 0, 37);\npoke(st, 0, 38);\npoke(st, 0, 39);\npoke(st, 0, 40);\npoke(st, 0, 41);\npoke(st, 0, 42);\npoke(st, 0, 43);\npoke(st, 0, 44);\npoke(st, 0, 45);\npoke(st, 0, 46);\npoke(st, 0, 47);\npoke(st, 0, 48);\npoke(st, 0, 49);\npoke(st, 0, 50);\npoke(st, 0, 51);\npoke(st, 0, 52);\npoke(st, 0, 53);\npoke(st, 0, 54);\npoke(st, 0, 55);\n}\nif (on_D == 0) {\npoke(st, 0, 56);\npoke(st, 0, 57);\npoke(st, 0, 58);\npoke(st, 0, 59);\npoke(st, 0, 60);\npoke(st, 0, 61);\npoke(st, 0, 62);\npoke(st, 0, 63);\npoke(st, 0, 64);\npoke(st, 0, 65);\npoke(st, 0, 66);\npoke(st, 0, 67);\npoke(st, 0, 68);\npoke(st, 0, 69);\npoke(st, 0, 70);\npoke(st, 0, 71);\npoke(st, 0, 72);\npoke(st, 0, 73);\npoke(st, 0, 74);\npoke(st, 0, 75);\npoke(st, 0, 76);\npoke(st, 0, 77);\npoke(st, 0, 78);\npoke(st, 0, 79);\npoke(st, 0, 80);\npoke(st, 0, 81);\n}\nif (on_S == 0) {\npoke(st, 0, 82);\npoke(st, 0, 83);\npoke(st, 0, 84);\npoke(st, 0, 85);\npoke(st, 0, 86);\npoke(st, 0, 87);\npoke(st, 0, 88);\npoke(st, 0, 89);\n}\nd0 = L_y1;\nd1 = L_y0;\nd0 = ap(hb, 32, d0, 0.04245470986526787);\nd0 = ap(hb, 36, d0, 0.39331989319033134);\nd1 = ap(hb, 34, d1, 0.17073985049750015);\nd1 = ap(hb, 38, d1, 0.7457135887202412);\nL_v0 = 0.5 * (d0 + d1);\nd0 = L_y3;\nd1 = L_y2;\nd0 = ap(hb, 32, d0, 0.04245470986526787);\nd0 = ap(hb, 36, d0, 0.39331989319033134);\nd1 = ap(hb, 34, d1, 0.17073985049750015);\nd1 = ap(hb, 38, d1, 0.7457135887202412);\nL_v1 = 0.5 * (d0 + d1);\nd0 = L_v1;\nd1 = L_v0;\nd0 = ap(hb, 40, d0, 0.019059005558478156);\nd0 = ap(hb, 44, d0, 0.1559582483500435);\nd0 = ap(hb, 48, d0, 0.3650536901969154);\nd0 = ap(hb, 52, d0, 0.5755010797915323);\nd0 = ap(hb, 56, d0, 0.7526447471286863);\nd0 = ap(hb, 60, d0, 0.8980636464339091);\nd1 = ap(hb, 42, d1, 0.07350243453590219);\nd1 = ap(hb, 46, d1, 0.25649919975582064);\nd1 = ap(hb, 50, d1, 0.47327898479453656);\nd1 = ap(hb, 54, d1, 0.6688095014357188);\nd1 = ap(hb, 58, d1, 0.8282265929955738);\nd1 = ap(hb, 62, d1, 0.9656701590349398);\nL_w = 0.5 * (d0 + d1);\nout1 = g_gain * g_fader * L_w;\n\n// ===== lato R =====\nR_e = in2;\nR_o = in2;\nR_e = ap(hb, 64, R_e, 0.019059005558478156);\nR_e = ap(hb, 68, R_e, 0.1559582483500435);\nR_e = ap(hb, 72, R_e, 0.3650536901969154);\nR_e = ap(hb, 76, R_e, 0.5755010797915323);\nR_e = ap(hb, 80, R_e, 0.7526447471286863);\nR_e = ap(hb, 84, R_e, 0.8980636464339091);\nR_o = ap(hb, 66, R_o, 0.07350243453590219);\nR_o = ap(hb, 70, R_o, 0.25649919975582064);\nR_o = ap(hb, 74, R_o, 0.47327898479453656);\nR_o = ap(hb, 78, R_o, 0.6688095014357188);\nR_o = ap(hb, 82, R_o, 0.8282265929955738);\nR_o = ap(hb, 86, R_o, 0.9656701590349398);\nR_u0 = R_e;\nR_u1 = R_e;\nR_u0 = ap(hb, 88, R_u0, 0.04245470986526787);\nR_u0 = ap(hb, 92, R_u0, 0.39331989319033134);\nR_u1 = ap(hb, 90, R_u1, 0.17073985049750015);\nR_u1 = ap(hb, 94, R_u1, 0.7457135887202412);\nR_u2 = R_o;\nR_u3 = R_o;\nR_u2 = ap(hb, 88, R_u2, 0.04245470986526787);\nR_u2 = ap(hb, 92, R_u2, 0.39331989319033134);\nR_u3 = ap(hb, 90, R_u3, 0.17073985049750015);\nR_u3 = ap(hb, 94, R_u3, 0.7457135887202412);\nR0A = 0;\nif (on_A) {\nR0Al = bq(st, 90, R_u0, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR0Al = bq(st, 92, R0Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR0Al = bq(st, 94, R0Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nR0Al = bq(st, 96, R0Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR0Ah1 = bq(st, 98, R_u0, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR0Ah1 = bq(st, 100, R0Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR0Alm = bq(st, 102, R0Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR0Alm = bq(st, 104, R0Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR0Alm = bq(st, 106, R0Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR0Ah2 = bq(st, 108, R0Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR0Ah2 = bq(st, 110, R0Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR0Amh = bq(st, 112, R0Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR0Amh = bq(st, 114, R0Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR0Ahi = bq(st, 116, R0Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR0Ahi = bq(st, 118, R0Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR0A = g_low * R0Al + g_lowmid * R0Alm + g_midhigh * R0Amh + g_high * R0Ahi;\n}\nR0C = 0;\nif (on_C) {\nR0Cl = bq(st, 120, R_u0, C1_lb, 2 * C1_lb, C1_lb, C1_a1, C1_a2);\nR0Cl = bq(st, 122, R0Cl, C2_a2, C2_a1, 1, C2_a1, C2_a2);\nR0Cl = bq(st, 124, R0Cl, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nR0Ch1 = bq(st, 126, R_u0, C1_n, -2 * C1_n, C1_n, C1_a1, C1_a2);\nR0Ch1 = -R0Ch1;\nR0Clm = bq(st, 128, R0Ch1, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nR0Clm = bq(st, 130, R0Clm, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nR0Clm = bq(st, 132, R0Clm, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nR0Ch2 = bq(st, 134, R0Ch1, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nR0Ch2 = bq(st, 136, R0Ch2, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nR0Cmh = bq(st, 138, R0Ch2, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nR0Cmh = bq(st, 140, R0Cmh, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nR0Chi = bq(st, 142, R0Ch2, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nR0Chi = bq(st, 144, R0Chi, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nR0C = g_low * R0Cl + g_lowmid * R0Clm + g_midhigh * R0Cmh + g_high * R0Chi;\n}\nR0D = 0;\nif (on_D) {\nR0Dl = bq(st, 146, R_u0, D1_lb, 2 * D1_lb, D1_lb, D1_a1, D1_a2);\nR0Dl = bq(st, 148, R0Dl, D2_a2, D2_a1, 1, D2_a1, D2_a2);\nR0Dl = bq(st, 150, R0Dl, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nR0Dh1 = bq(st, 152, R_u0, D1_n, -2 * D1_n, D1_n, D1_a1, D1_a2);\nR0Dh1 = -R0Dh1;\nR0Dlm = bq(st, 154, R0Dh1, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nR0Dlm = bq(st, 156, R0Dlm, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nR0Dlm = bq(st, 158, R0Dlm, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nR0Dh2 = bq(st, 160, R0Dh1, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nR0Dh2 = bq(st, 162, R0Dh2, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nR0Dmh = bq(st, 164, R0Dh2, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nR0Dmh = bq(st, 166, R0Dmh, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nR0Dhi = bq(st, 168, R0Dh2, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nR0Dhi = bq(st, 170, R0Dhi, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nR0D = g_low * R0Dl + g_lowmid * R0Dlm + g_midhigh * R0Dmh + g_high * R0Dhi;\n}\nR0s4 = 0;\nif (on_S) {\nR0s1 = bq(st, 172, R_u0, sl_b0, sl_b1, sl_b2, sl_a1, sl_a2);\nR0sb = bq(st, 174, R0s1, slm_b0, slm_b1, slm_b2, slm_a1, slm_a2);\nR0s2 = R0s1 + sr_clm * R0sb;\nR0sb = bq(st, 176, R0s2, smh_b0, smh_b1, smh_b2, smh_a1, smh_a2);\nR0s3 = R0s2 + sr_cmh * R0sb;\nR0sb = bq(st, 178, R0s3, shi_b0, shi_b1, shi_b2, shi_a1, shi_a2);\nR0s4 = R0s3 - sr_chi * R0sb;\n}\nR_y0 = w_A * R0A + w_C * R0C + w_D * R0D + w_S * R0s4;\nR1A = 0;\nif (on_A) {\nR1Al = bq(st, 90, R_u1, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR1Al = bq(st, 92, R1Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR1Al = bq(st, 94, R1Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nR1Al = bq(st, 96, R1Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR1Ah1 = bq(st, 98, R_u1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR1Ah1 = bq(st, 100, R1Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR1Alm = bq(st, 102, R1Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR1Alm = bq(st, 104, R1Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR1Alm = bq(st, 106, R1Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR1Ah2 = bq(st, 108, R1Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR1Ah2 = bq(st, 110, R1Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR1Amh = bq(st, 112, R1Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR1Amh = bq(st, 114, R1Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR1Ahi = bq(st, 116, R1Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR1Ahi = bq(st, 118, R1Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR1A = g_low * R1Al + g_lowmid * R1Alm + g_midhigh * R1Amh + g_high * R1Ahi;\n}\nR1C = 0;\nif (on_C) {\nR1Cl = bq(st, 120, R_u1, C1_lb, 2 * C1_lb, C1_lb, C1_a1, C1_a2);\nR1Cl = bq(st, 122, R1Cl, C2_a2, C2_a1, 1, C2_a1, C2_a2);\nR1Cl = bq(st, 124, R1Cl, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nR1Ch1 = bq(st, 126, R_u1, C1_n, -2 * C1_n, C1_n, C1_a1, C1_a2);\nR1Ch1 = -R1Ch1;\nR1Clm = bq(st, 128, R1Ch1, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nR1Clm = bq(st, 130, R1Clm, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nR1Clm = bq(st, 132, R1Clm, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nR1Ch2 = bq(st, 134, R1Ch1, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nR1Ch2 = bq(st, 136, R1Ch2, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nR1Cmh = bq(st, 138, R1Ch2, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nR1Cmh = bq(st, 140, R1Cmh, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nR1Chi = bq(st, 142, R1Ch2, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nR1Chi = bq(st, 144, R1Chi, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nR1C = g_low * R1Cl + g_lowmid * R1Clm + g_midhigh * R1Cmh + g_high * R1Chi;\n}\nR1D = 0;\nif (on_D) {\nR1Dl = bq(st, 146, R_u1, D1_lb, 2 * D1_lb, D1_lb, D1_a1, D1_a2);\nR1Dl = bq(st, 148, R1Dl, D2_a2, D2_a1, 1, D2_a1, D2_a2);\nR1Dl = bq(st, 150, R1Dl, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nR1Dh1 = bq(st, 152, R_u1, D1_n, -2 * D1_n, D1_n, D1_a1, D1_a2);\nR1Dh1 = -R1Dh1;\nR1Dlm = bq(st, 154, R1Dh1, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nR1Dlm = bq(st, 156, R1Dlm, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nR1Dlm = bq(st, 158, R1Dlm, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nR1Dh2 = bq(st, 160, R1Dh1, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nR1Dh2 = bq(st, 162, R1Dh2, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nR1Dmh = bq(st, 164, R1Dh2, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nR1Dmh = bq(st, 166, R1Dmh, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nR1Dhi = bq(st, 168, R1Dh2, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nR1Dhi = bq(st, 170, R1Dhi, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nR1D = g_low * R1Dl + g_lowmid * R1Dlm + g_midhigh * R1Dmh + g_high * R1Dhi;\n}\nR1s4 = 0;\nif (on_S) {\nR1s1 = bq(st, 172, R_u1, sl_b0, sl_b1, sl_b2, sl_a1, sl_a2);\nR1sb = bq(st, 174, R1s1, slm_b0, slm_b1, slm_b2, slm_a1, slm_a2);\nR1s2 = R1s1 + sr_clm * R1sb;\nR1sb = bq(st, 176, R1s2, smh_b0, smh_b1, smh_b2, smh_a1, smh_a2);\nR1s3 = R1s2 + sr_cmh * R1sb;\nR1sb = bq(st, 178, R1s3, shi_b0, shi_b1, shi_b2, shi_a1, shi_a2);\nR1s4 = R1s3 - sr_chi * R1sb;\n}\nR_y1 = w_A * R1A + w_C * R1C + w_D * R1D + w_S * R1s4;\nR2A = 0;\nif (on_A) {\nR2Al = bq(st, 90, R_u2, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR2Al = bq(st, 92, R2Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR2Al = bq(st, 94, R2Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nR2Al = bq(st, 96, R2Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR2Ah1 = bq(st, 98, R_u2, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR2Ah1 = bq(st, 100, R2Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR2Alm = bq(st, 102, R2Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR2Alm = bq(st, 104, R2Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR2Alm = bq(st, 106, R2Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR2Ah2 = bq(st, 108, R2Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR2Ah2 = bq(st, 110, R2Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR2Amh = bq(st, 112, R2Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR2Amh = bq(st, 114, R2Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR2Ahi = bq(st, 116, R2Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR2Ahi = bq(st, 118, R2Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR2A = g_low * R2Al + g_lowmid * R2Alm + g_midhigh * R2Amh + g_high * R2Ahi;\n}\nR2C = 0;\nif (on_C) {\nR2Cl = bq(st, 120, R_u2, C1_lb, 2 * C1_lb, C1_lb, C1_a1, C1_a2);\nR2Cl = bq(st, 122, R2Cl, C2_a2, C2_a1, 1, C2_a1, C2_a2);\nR2Cl = bq(st, 124, R2Cl, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nR2Ch1 = bq(st, 126, R_u2, C1_n, -2 * C1_n, C1_n, C1_a1, C1_a2);\nR2Ch1 = -R2Ch1;\nR2Clm = bq(st, 128, R2Ch1, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nR2Clm = bq(st, 130, R2Clm, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nR2Clm = bq(st, 132, R2Clm, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nR2Ch2 = bq(st, 134, R2Ch1, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nR2Ch2 = bq(st, 136, R2Ch2, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nR2Cmh = bq(st, 138, R2Ch2, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nR2Cmh = bq(st, 140, R2Cmh, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nR2Chi = bq(st, 142, R2Ch2, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nR2Chi = bq(st, 144, R2Chi, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nR2C = g_low * R2Cl + g_lowmid * R2Clm + g_midhigh * R2Cmh + g_high * R2Chi;\n}\nR2D = 0;\nif (on_D) {\nR2Dl = bq(st, 146, R_u2, D1_lb, 2 * D1_lb, D1_lb, D1_a1, D1_a2);\nR2Dl = bq(st, 148, R2Dl, D2_a2, D2_a1, 1, D2_a1, D2_a2);\nR2Dl = bq(st, 150, R2Dl, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nR2Dh1 = bq(st, 152, R_u2, D1_n, -2 * D1_n, D1_n, D1_a1, D1_a2);\nR2Dh1 = -R2Dh1;\nR2Dlm = bq(st, 154, R2Dh1, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nR2Dlm = bq(st, 156, R2Dlm, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nR2Dlm = bq(st, 158, R2Dlm, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nR2Dh2 = bq(st, 160, R2Dh1, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nR2Dh2 = bq(st, 162, R2Dh2, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nR2Dmh = bq(st, 164, R2Dh2, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nR2Dmh = bq(st, 166, R2Dmh, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nR2Dhi = bq(st, 168, R2Dh2, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nR2Dhi = bq(st, 170, R2Dhi, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nR2D = g_low * R2Dl + g_lowmid * R2Dlm + g_midhigh * R2Dmh + g_high * R2Dhi;\n}\nR2s4 = 0;\nif (on_S) {\nR2s1 = bq(st, 172, R_u2, sl_b0, sl_b1, sl_b2, sl_a1, sl_a2);\nR2sb = bq(st, 174, R2s1, slm_b0, slm_b1, slm_b2, slm_a1, slm_a2);\nR2s2 = R2s1 + sr_clm * R2sb;\nR2sb = bq(st, 176, R2s2, smh_b0, smh_b1, smh_b2, smh_a1, smh_a2);\nR2s3 = R2s2 + sr_cmh * R2sb;\nR2sb = bq(st, 178, R2s3, shi_b0, shi_b1, shi_b2, shi_a1, shi_a2);\nR2s4 = R2s3 - sr_chi * R2sb;\n}\nR_y2 = w_A * R2A + w_C * R2C + w_D * R2D + w_S * R2s4;\nR3A = 0;\nif (on_A) {\nR3Al = bq(st, 90, R_u3, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR3Al = bq(st, 92, R3Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR3Al = bq(st, 94, R3Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nR3Al = bq(st, 96, R3Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR3Ah1 = bq(st, 98, R_u3, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR3Ah1 = bq(st, 100, R3Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR3Alm = bq(st, 102, R3Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR3Alm = bq(st, 104, R3Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR3Alm = bq(st, 106, R3Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR3Ah2 = bq(st, 108, R3Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR3Ah2 = bq(st, 110, R3Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR3Amh = bq(st, 112, R3Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR3Amh = bq(st, 114, R3Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR3Ahi = bq(st, 116, R3Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR3Ahi = bq(st, 118, R3Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR3A = g_low * R3Al + g_lowmid * R3Alm + g_midhigh * R3Amh + g_high * R3Ahi;\n}\nR3C = 0;\nif (on_C) {\nR3Cl = bq(st, 120, R_u3, C1_lb, 2 * C1_lb, C1_lb, C1_a1, C1_a2);\nR3Cl = bq(st, 122, R3Cl, C2_a2, C2_a1, 1, C2_a1, C2_a2);\nR3Cl = bq(st, 124, R3Cl, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nR3Ch1 = bq(st, 126, R_u3, C1_n, -2 * C1_n, C1_n, C1_a1, C1_a2);\nR3Ch1 = -R3Ch1;\nR3Clm = bq(st, 128, R3Ch1, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nR3Clm = bq(st, 130, R3Clm, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nR3Clm = bq(st, 132, R3Clm, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nR3Ch2 = bq(st, 134, R3Ch1, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nR3Ch2 = bq(st, 136, R3Ch2, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nR3Cmh = bq(st, 138, R3Ch2, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nR3Cmh = bq(st, 140, R3Cmh, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nR3Chi = bq(st, 142, R3Ch2, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nR3Chi = bq(st, 144, R3Chi, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nR3C = g_low * R3Cl + g_lowmid * R3Clm + g_midhigh * R3Cmh + g_high * R3Chi;\n}\nR3D = 0;\nif (on_D) {\nR3Dl = bq(st, 146, R_u3, D1_lb, 2 * D1_lb, D1_lb, D1_a1, D1_a2);\nR3Dl = bq(st, 148, R3Dl, D2_a2, D2_a1, 1, D2_a1, D2_a2);\nR3Dl = bq(st, 150, R3Dl, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nR3Dh1 = bq(st, 152, R_u3, D1_n, -2 * D1_n, D1_n, D1_a1, D1_a2);\nR3Dh1 = -R3Dh1;\nR3Dlm = bq(st, 154, R3Dh1, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nR3Dlm = bq(st, 156, R3Dlm, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nR3Dlm = bq(st, 158, R3Dlm, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nR3Dh2 = bq(st, 160, R3Dh1, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nR3Dh2 = bq(st, 162, R3Dh2, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nR3Dmh = bq(st, 164, R3Dh2, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nR3Dmh = bq(st, 166, R3Dmh, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nR3Dhi = bq(st, 168, R3Dh2, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nR3Dhi = bq(st, 170, R3Dhi, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nR3D = g_low * R3Dl + g_lowmid * R3Dlm + g_midhigh * R3Dmh + g_high * R3Dhi;\n}\nR3s4 = 0;\nif (on_S) {\nR3s1 = bq(st, 172, R_u3, sl_b0, sl_b1, sl_b2, sl_a1, sl_a2);\nR3sb = bq(st, 174, R3s1, slm_b0, slm_b1, slm_b2, slm_a1, slm_a2);\nR3s2 = R3s1 + sr_clm * R3sb;\nR3sb = bq(st, 176, R3s2, smh_b0, smh_b1, smh_b2, smh_a1, smh_a2);\nR3s3 = R3s2 + sr_cmh * R3sb;\nR3sb = bq(st, 178, R3s3, shi_b0, shi_b1, shi_b2, shi_a1, shi_a2);\nR3s4 = R3s3 - sr_chi * R3sb;\n}\nR_y3 = w_A * R3A + w_C * R3C + w_D * R3D + w_S * R3s4;\nif (on_A == 0) {\npoke(st, 0, 90);\npoke(st, 0, 91);\npoke(st, 0, 92);\npoke(st, 0, 93);\npoke(st, 0, 94);\npoke(st, 0, 95);\npoke(st, 0, 96);\npoke(st, 0, 97);\npoke(st, 0, 98);\npoke(st, 0, 99);\npoke(st, 0, 100);\npoke(st, 0, 101);\npoke(st, 0, 102);\npoke(st, 0, 103);\npoke(st, 0, 104);\npoke(st, 0, 105);\npoke(st, 0, 106);\npoke(st, 0, 107);\npoke(st, 0, 108);\npoke(st, 0, 109);\npoke(st, 0, 110);\npoke(st, 0, 111);\npoke(st, 0, 112);\npoke(st, 0, 113);\npoke(st, 0, 114);\npoke(st, 0, 115);\npoke(st, 0, 116);\npoke(st, 0, 117);\npoke(st, 0, 118);\npoke(st, 0, 119);\n}\nif (on_C == 0) {\npoke(st, 0, 120);\npoke(st, 0, 121);\npoke(st, 0, 122);\npoke(st, 0, 123);\npoke(st, 0, 124);\npoke(st, 0, 125);\npoke(st, 0, 126);\npoke(st, 0, 127);\npoke(st, 0, 128);\npoke(st, 0, 129);\npoke(st, 0, 130);\npoke(st, 0, 131);\npoke(st, 0, 132);\npoke(st, 0, 133);\npoke(st, 0, 134);\npoke(st, 0, 135);\npoke(st, 0, 136);\npoke(st, 0, 137);\npoke(st, 0, 138);\npoke(st, 0, 139);\npoke(st, 0, 140);\npoke(st, 0, 141);\npoke(st, 0, 142);\npoke(st, 0, 143);\npoke(st, 0, 144);\npoke(st, 0, 145);\n}\nif (on_D == 0) {\npoke(st, 0, 146);\npoke(st, 0, 147);\npoke(st, 0, 148);\npoke(st, 0, 149);\npoke(st, 0, 150);\npoke(st, 0, 151);\npoke(st, 0, 152);\npoke(st, 0, 153);\npoke(st, 0, 154);\npoke(st, 0, 155);\npoke(st, 0, 156);\npoke(st, 0, 157);\npoke(st, 0, 158);\npoke(st, 0, 159);\npoke(st, 0, 160);\npoke(st, 0, 161);\npoke(st, 0, 162);\npoke(st, 0, 163);\npoke(st, 0, 164);\npoke(st, 0, 165);\npoke(st, 0, 166);\npoke(st, 0, 167);\npoke(st, 0, 168);\npoke(st, 0, 169);\npoke(st, 0, 170);\npoke(st, 0, 171);\n}\nif (on_S == 0) {\npoke(st, 0, 172);\npoke(st, 0, 173);\npoke(st, 0, 174);\npoke(st, 0, 175);\npoke(st, 0, 176);\npoke(st, 0, 177);\npoke(st, 0, 178);\npoke(st, 0, 179);\n}\nd0 = R_y1;\nd1 = R_y0;\nd0 = ap(hb, 96, d0, 0.04245470986526787);\nd0 = ap(hb, 100, d0, 0.39331989319033134);\nd1 = ap(hb, 98, d1, 0.17073985049750015);\nd1 = ap(hb, 102, d1, 0.7457135887202412);\nR_v0 = 0.5 * (d0 + d1);\nd0 = R_y3;\nd1 = R_y2;\nd0 = ap(hb, 96, d0, 0.04245470986526787);\nd0 = ap(hb, 100, d0, 0.39331989319033134);\nd1 = ap(hb, 98, d1, 0.17073985049750015);\nd1 = ap(hb, 102, d1, 0.7457135887202412);\nR_v1 = 0.5 * (d0 + d1);\nd0 = R_v1;\nd1 = R_v0;\nd0 = ap(hb, 104, d0, 0.019059005558478156);\nd0 = ap(hb, 108, d0, 0.1559582483500435);\nd0 = ap(hb, 112, d0, 0.3650536901969154);\nd0 = ap(hb, 116, d0, 0.5755010797915323);\nd0 = ap(hb, 120, d0, 0.7526447471286863);\nd0 = ap(hb, 124, d0, 0.8980636464339091);\nd1 = ap(hb, 106, d1, 0.07350243453590219);\nd1 = ap(hb, 110, d1, 0.25649919975582064);\nd1 = ap(hb, 114, d1, 0.47327898479453656);\nd1 = ap(hb, 118, d1, 0.6688095014357188);\nd1 = ap(hb, 122, d1, 0.8282265929955738);\nd1 = ap(hb, 126, d1, 0.9656701590349398);\nR_w = 0.5 * (d0 + d1);\nout2 = g_gain * g_fader * R_w;\n\n",
									"numinlets": 2,
									"numoutlets": 2,
									"outlettype": [
										"",
										""
									],
									"fontface": 0,
									"fontname": "<Monospaced>",
									"fontsize": 12.0,
									"patching_rect": [
										20,
										60,
										600,
										500
									]
								}
							},
							{
								"box": {
									"id": "obj-4",
									"maxclass": "newobj",
									"text": "out 1",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										20,
										580,
										37,
										22
									]
								}
							},
							{
								"box": {
									"id": "obj-5",
									"maxclass": "newobj",
									"text": "out 2",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										400,
										580,
										37,
										22
									]
								}
							}
						],
						"lines": [
							{
								"patchline": {
									"destination": [
										"obj-3",
										0
									],
									"source": [
										"obj-1",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-3",
										1
									],
									"source": [
										"obj-2",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-4",
										0
									],
									"source": [
										"obj-3",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-5",
										0
									],
									"source": [
										"obj-3",
										1
									]
								}
							}
						]
					}
				}
			},
			{
				"box": {
					"id": "obj-out",
					"maxclass": "newobj",
					"text": "plugout~",
					"numinlets": 2,
					"numoutlets": 2,
					"outlettype": [
						"signal",
						"signal"
					],
					"patching_rect": [
						20,
						360,
						60,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-d0",
					"maxclass": "live.dial",
					"parameter_enable": 1,
					"patching_rect": [
						100,
						80,
						44,
						48
					],
					"presentation": 1,
					"presentation_rect": [
						8,
						8,
						44,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "GAIN",
							"parameter_shortname": "GAIN",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								50.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "GAIN",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"float"
					]
				}
			},
			{
				"box": {
					"id": "obj-d0-pre",
					"maxclass": "newobj",
					"text": "prepend gain",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						100,
						200,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-d1",
					"maxclass": "live.dial",
					"parameter_enable": 1,
					"patching_rect": [
						190,
						80,
						44,
						48
					],
					"presentation": 1,
					"presentation_rect": [
						58,
						8,
						44,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "LOW",
							"parameter_shortname": "LOW",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								50.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "LOW",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"float"
					]
				}
			},
			{
				"box": {
					"id": "obj-d1-pre",
					"maxclass": "newobj",
					"text": "prepend low",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						190,
						200,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-d2",
					"maxclass": "live.dial",
					"parameter_enable": 1,
					"patching_rect": [
						280,
						80,
						44,
						48
					],
					"presentation": 1,
					"presentation_rect": [
						108,
						8,
						44,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "LOW-MID",
							"parameter_shortname": "LOW-MID",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								50.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "LOW-MID",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"float"
					]
				}
			},
			{
				"box": {
					"id": "obj-d2-pre",
					"maxclass": "newobj",
					"text": "prepend lowmid",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						280,
						200,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-d3",
					"maxclass": "live.dial",
					"parameter_enable": 1,
					"patching_rect": [
						370,
						80,
						44,
						48
					],
					"presentation": 1,
					"presentation_rect": [
						158,
						8,
						44,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "MID-HIGH",
							"parameter_shortname": "MID-HIGH",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								50.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "MID-HIGH",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"float"
					]
				}
			},
			{
				"box": {
					"id": "obj-d3-pre",
					"maxclass": "newobj",
					"text": "prepend midhigh",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						370,
						200,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-d4",
					"maxclass": "live.dial",
					"parameter_enable": 1,
					"patching_rect": [
						460,
						80,
						44,
						48
					],
					"presentation": 1,
					"presentation_rect": [
						208,
						8,
						44,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "HIGH",
							"parameter_shortname": "HIGH",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								50.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "HIGH",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"float"
					]
				}
			},
			{
				"box": {
					"id": "obj-d4-pre",
					"maxclass": "newobj",
					"text": "prepend high",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						460,
						200,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-fad",
					"maxclass": "live.slider",
					"parameter_enable": 1,
					"patching_rect": [
						550,
						80,
						44,
						90
					],
					"presentation": 1,
					"presentation_rect": [
						262,
						8,
						40,
						150
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "FADER",
							"parameter_shortname": "FADER",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								100.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "FADER",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"",
						"float"
					]
				}
			},
			{
				"box": {
					"id": "obj-fad-pre",
					"maxclass": "newobj",
					"text": "prepend fader",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						550,
						200,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-sel",
					"maxclass": "live.tab",
					"parameter_enable": 1,
					"patching_rect": [
						640,
						80,
						44,
						90
					],
					"presentation": 1,
					"presentation_rect": [
						8,
						62,
						240,
						30
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "INCROCI",
							"parameter_shortname": "INCROCI",
							"parameter_initial_enable": 1,
							"parameter_type": 2,
							"parameter_enum": [
								"A 150/500/2500",
								"C 150d/350/3150",
								"D 150d/700/3150"
							],
							"parameter_mmax": 2.0,
							"parameter_initial": [
								0
							],
							"parameter_unitstyle": 0
						}
					},
					"varname": "INCROCI",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": [
						"",
						"",
						"float"
					],
					"num_lines_patching": 2,
					"num_lines_presentation": 2
				}
			},
			{
				"box": {
					"id": "obj-sel-pre",
					"maxclass": "newobj",
					"text": "prepend incroci",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						640,
						200,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-cur",
					"maxclass": "live.tab",
					"parameter_enable": 1,
					"patching_rect": [
						730,
						80,
						44,
						90
					],
					"presentation": 1,
					"presentation_rect": [
						8,
						96,
						240,
						18
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "CURVA",
							"parameter_shortname": "CURVA",
							"parameter_initial_enable": 1,
							"parameter_type": 2,
							"parameter_enum": [
								"LINEARE",
								"PIONEER"
							],
							"parameter_mmax": 1.0,
							"parameter_initial": [
								0
							],
							"parameter_unitstyle": 0
						}
					},
					"varname": "CURVA",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": [
						"",
						"",
						"float"
					],
					"num_lines_patching": 1,
					"num_lines_presentation": 1
				}
			},
			{
				"box": {
					"id": "obj-cur-pre",
					"maxclass": "newobj",
					"text": "prepend curva",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						730,
						200,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-eqt",
					"maxclass": "live.tab",
					"parameter_enable": 1,
					"patching_rect": [
						820,
						80,
						44,
						90
					],
					"presentation": 1,
					"presentation_rect": [
						8,
						118,
						240,
						18
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "EQ TIPO",
							"parameter_shortname": "EQ TIPO",
							"parameter_initial_enable": 1,
							"parameter_type": 2,
							"parameter_enum": [
								"ISOLATOR",
								"SERIE 70/250/1k/5k"
							],
							"parameter_mmax": 1.0,
							"parameter_initial": [
								0
							],
							"parameter_unitstyle": 0
						}
					},
					"varname": "EQ TIPO",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": [
						"",
						"",
						"float"
					],
					"num_lines_patching": 1,
					"num_lines_presentation": 1
				}
			},
			{
				"box": {
					"id": "obj-eqt-pre",
					"maxclass": "newobj",
					"text": "prepend eqtipo",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						820,
						200,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-nota",
					"maxclass": "live.comment",
					"numinlets": 1,
					"numoutlets": 0,
					"presentation": 1,
					"presentation_rect": [
						8,
						140,
						250,
						28
					],
					"patching_rect": [
						20,
						440,
						250,
						36
					],
					"linecount": 2,
					"text": "50% = 0 dB. SERIE: 0% taglia, non spegne; INCROCI e CURVA solo per ISOLATOR."
				}
			}
		],
		"lines": [
			{
				"patchline": {
					"destination": [
						"obj-gen",
						0
					],
					"source": [
						"obj-in",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-gen",
						1
					],
					"source": [
						"obj-in",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-out",
						0
					],
					"source": [
						"obj-gen",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-out",
						1
					],
					"source": [
						"obj-gen",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-d0-pre",
						0
					],
					"source": [
						"obj-d0",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-gen",
						0
					],
					"source": [
						"obj-d0-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-d1-pre",
						0
					],
					"source": [
						"obj-d1",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-gen",
						0
					],
					"source": [
						"obj-d1-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-d2-pre",
						0
					],
					"source": [
						"obj-d2",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-gen",
						0
					],
					"source": [
						"obj-d2-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-d3-pre",
						0
					],
					"source": [
						"obj-d3",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-gen",
						0
					],
					"source": [
						"obj-d3-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-d4-pre",
						0
					],
					"source": [
						"obj-d4",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-gen",
						0
					],
					"source": [
						"obj-d4-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-fad-pre",
						0
					],
					"source": [
						"obj-fad",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-gen",
						0
					],
					"source": [
						"obj-fad-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-sel-pre",
						0
					],
					"source": [
						"obj-sel",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-gen",
						0
					],
					"source": [
						"obj-sel-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-cur-pre",
						0
					],
					"source": [
						"obj-cur",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-gen",
						0
					],
					"source": [
						"obj-cur-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-eqt-pre",
						0
					],
					"source": [
						"obj-eqt",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-gen",
						0
					],
					"source": [
						"obj-eqt-pre",
						0
					]
				}
			}
		],
		"parameters": {
			"obj-d0": [
				"GAIN",
				"GAIN",
				0
			],
			"obj-d1": [
				"LOW",
				"LOW",
				0
			],
			"obj-d2": [
				"LOW-MID",
				"LOW-MID",
				0
			],
			"obj-d3": [
				"MID-HIGH",
				"MID-HIGH",
				0
			],
			"obj-d4": [
				"HIGH",
				"HIGH",
				0
			],
			"obj-fad": [
				"FADER",
				"FADER",
				0
			],
			"obj-sel": [
				"INCROCI",
				"INCROCI",
				0
			],
			"obj-cur": [
				"CURVA",
				"CURVA",
				0
			],
			"obj-eqt": [
				"EQ TIPO",
				"EQ TIPO",
				0
			]
		},
		"dependency_cache": [],
		"latency": 0,
		"autosave": 0,
		"project": {
			"version": 1,
			"amxdtype": 1633771873,
			"readonly": 0,
			"devpathtype": 0,
			"devpath": ".",
			"contents": {
				"patchers": {}
			},
			"layout": {},
			"searchpath": {},
			"detailsvisible": 0,
			"autoorganize": 1,
			"hideprojectwindow": 1,
			"showdependencies": 1,
			"autolocalize": 0,
			"sortmode": 0,
			"viewmode": 0
		}
	}
}