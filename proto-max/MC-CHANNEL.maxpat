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
									"code": "// MC-CHANNEL - prototipo Max P0 del canale maelcum_mixer.\n// GENERATO da proto-max/coefficienti/genera.py: non modificare a mano.\n// GAIN -inf..0..+10 dB, isolator a 4 bande (0..+6 dB, silenzio a\n// fondo corsa), fader. Banca a 4x della frequenza di campionamento.\n\n// biquad in forma trasposta II; stato in m[i], m[i+1]\nbq(m, i, x, b0, b1, b2, a1, a2) {\n\ty = b0 * x + peek(m, i);\n\tpoke(m, b1 * x - a1 * y + peek(m, i + 1), i);\n\tpoke(m, b2 * x - a2 * y, i + 1);\n\treturn y;\n}\n\n// allpass del 1o ordine del halfband; stato in m[i] (x), m[i+1] (y)\nap(m, i, x, c) {\n\ty = c * (x - peek(m, i + 1)) + peek(m, i);\n\tpoke(m, x, i);\n\tpoke(m, y, i + 1);\n\treturn y;\n}\n\nParam gain(50.0, min=0, max=100);\nParam low(50.0, min=0, max=100);\nParam lowmid(50.0, min=0, max=100);\nParam midhigh(50.0, min=0, max=100);\nParam high(50.0, min=0, max=100);\nParam fader(100.0, min=0, max=100);\nParam incroci(0, min=0, max=2);\nParam curva(0, min=0, max=1);\nData st(164);\nData hb(128);\nHistory s_gain(50.0);\nHistory s_low(50.0);\nHistory s_lowmid(50.0);\nHistory s_midhigh(50.0);\nHistory s_high(50.0);\nHistory s_fader(100.0);\nHistory s_x(0);\nHistory s_c(0);\n\n// manopole lisciate: 10 ms (selettore 20 ms, dissolvenza A/B)\nt10 = exp(-1 / (0.010 * samplerate));\nt20 = exp(-1 / (0.020 * samplerate));\ns_gain = gain + t10 * (s_gain - gain);\ns_low = low + t10 * (s_low - low);\ns_lowmid = lowmid + t10 * (s_lowmid - lowmid);\ns_midhigh = midhigh + t10 * (s_midhigh - midhigh);\ns_high = high + t10 * (s_high - high);\ns_fader = fader + t10 * (s_fader - fader);\ns_x = incroci + t20 * (s_x - incroci);\ns_c = curva + t20 * (s_c - curva);\n\n// GAIN: fondo corsa muto, meta CCW -100..0 dB, meta CW 0..+10 dB\ntg = s_gain / 100;\ng_gain = pow(10, min(200 * tg - 100, 20 * tg - 10) / 20) * (tg > 0);\n// bande: pot lineare x2, oppure curva Pioneer ideale (docs/09 \u00a77):\n// taglio (2 theta)^1,5, boost uguale; a fondo corsa il contatto da silenzio\nx_low = 2 * s_low / 100;\ng_low = ((1 - s_c) * x_low + s_c * (pow(min(x_low, 1), 1.5) + max(x_low - 1, 0))) * max(low > 0, s_low > 0.001);\nx_lowmid = 2 * s_lowmid / 100;\ng_lowmid = ((1 - s_c) * x_lowmid + s_c * (pow(min(x_lowmid, 1), 1.5) + max(x_lowmid - 1, 0))) * max(lowmid > 0, s_lowmid > 0.001);\nx_midhigh = 2 * s_midhigh / 100;\ng_midhigh = ((1 - s_c) * x_midhigh + s_c * (pow(min(x_midhigh, 1), 1.5) + max(x_midhigh - 1, 0))) * max(midhigh > 0, s_midhigh > 0.001);\nx_high = 2 * s_high / 100;\ng_high = ((1 - s_c) * x_high + s_c * (pow(min(x_high, 1), 1.5) + max(x_high - 1, 0))) * max(high > 0, s_high > 0.001);\n// fader [PROVVISORIO]: curva quadratica, -12 dB a meta corsa\ntf = s_fader / 100;\ng_fader = tf * tf;\n\n// coefficienti degli incroci (bilineare con prewarp)\n// LR4: Q 0,7071 due volte; LR2: Q 0,5 una volta\nsr4 = samplerate * 4;\nA1_k = tan(pi * 150.0 / sr4);\nA1_kk = A1_k * A1_k;\nA1_n = 1 / (1 + A1_k * 1.4142135623730951 + A1_kk);\nA1_a1 = 2 * (A1_kk - 1) * A1_n;\nA1_a2 = (1 - A1_k * 1.4142135623730951 + A1_kk) * A1_n;\nA1_lb = A1_kk * A1_n;\nA2_k = tan(pi * 500.0 / sr4);\nA2_kk = A2_k * A2_k;\nA2_n = 1 / (1 + A2_k * 1.4142135623730951 + A2_kk);\nA2_a1 = 2 * (A2_kk - 1) * A2_n;\nA2_a2 = (1 - A2_k * 1.4142135623730951 + A2_kk) * A2_n;\nA2_lb = A2_kk * A2_n;\nA3_k = tan(pi * 2500.0 / sr4);\nA3_kk = A3_k * A3_k;\nA3_n = 1 / (1 + A3_k * 1.4142135623730951 + A3_kk);\nA3_a1 = 2 * (A3_kk - 1) * A3_n;\nA3_a2 = (1 - A3_k * 1.4142135623730951 + A3_kk) * A3_n;\nA3_lb = A3_kk * A3_n;\nC1_k = tan(pi * 150.0 / sr4);\nC1_kk = C1_k * C1_k;\nC1_n = 1 / (1 + C1_k * 2.0 + C1_kk);\nC1_a1 = 2 * (C1_kk - 1) * C1_n;\nC1_a2 = (1 - C1_k * 2.0 + C1_kk) * C1_n;\nC1_lb = C1_kk * C1_n;\nC2_k = tan(pi * 350.0 / sr4);\nC2_kk = C2_k * C2_k;\nC2_n = 1 / (1 + C2_k * 1.4142135623730951 + C2_kk);\nC2_a1 = 2 * (C2_kk - 1) * C2_n;\nC2_a2 = (1 - C2_k * 1.4142135623730951 + C2_kk) * C2_n;\nC2_lb = C2_kk * C2_n;\nC3_k = tan(pi * 3150.0 / sr4);\nC3_kk = C3_k * C3_k;\nC3_n = 1 / (1 + C3_k * 1.4142135623730951 + C3_kk);\nC3_a1 = 2 * (C3_kk - 1) * C3_n;\nC3_a2 = (1 - C3_k * 1.4142135623730951 + C3_kk) * C3_n;\nC3_lb = C3_kk * C3_n;\nD1_k = tan(pi * 150.0 / sr4);\nD1_kk = D1_k * D1_k;\nD1_n = 1 / (1 + D1_k * 2.0 + D1_kk);\nD1_a1 = 2 * (D1_kk - 1) * D1_n;\nD1_a2 = (1 - D1_k * 2.0 + D1_kk) * D1_n;\nD1_lb = D1_kk * D1_n;\nD2_k = tan(pi * 700.0 / sr4);\nD2_kk = D2_k * D2_k;\nD2_n = 1 / (1 + D2_k * 1.4142135623730951 + D2_kk);\nD2_a1 = 2 * (D2_kk - 1) * D2_n;\nD2_a2 = (1 - D2_k * 1.4142135623730951 + D2_kk) * D2_n;\nD2_lb = D2_kk * D2_n;\nD3_k = tan(pi * 3150.0 / sr4);\nD3_kk = D3_k * D3_k;\nD3_n = 1 / (1 + D3_k * 1.4142135623730951 + D3_kk);\nD3_a1 = 2 * (D3_kk - 1) * D3_n;\nD3_a2 = (1 - D3_k * 1.4142135623730951 + D3_kk) * D3_n;\nD3_lb = D3_kk * D3_n;\n\n// ===== lato L =====\nL_e = in1;\nL_o = in1;\nL_e = ap(hb, 0, L_e, 0.019059005558478156);\nL_e = ap(hb, 4, L_e, 0.1559582483500435);\nL_e = ap(hb, 8, L_e, 0.3650536901969154);\nL_e = ap(hb, 12, L_e, 0.5755010797915323);\nL_e = ap(hb, 16, L_e, 0.7526447471286863);\nL_e = ap(hb, 20, L_e, 0.8980636464339091);\nL_o = ap(hb, 2, L_o, 0.07350243453590219);\nL_o = ap(hb, 6, L_o, 0.25649919975582064);\nL_o = ap(hb, 10, L_o, 0.47327898479453656);\nL_o = ap(hb, 14, L_o, 0.6688095014357188);\nL_o = ap(hb, 18, L_o, 0.8282265929955738);\nL_o = ap(hb, 22, L_o, 0.9656701590349398);\nL_u0 = L_e;\nL_u1 = L_e;\nL_u0 = ap(hb, 24, L_u0, 0.04245470986526787);\nL_u0 = ap(hb, 28, L_u0, 0.39331989319033134);\nL_u1 = ap(hb, 26, L_u1, 0.17073985049750015);\nL_u1 = ap(hb, 30, L_u1, 0.7457135887202412);\nL_u2 = L_o;\nL_u3 = L_o;\nL_u2 = ap(hb, 24, L_u2, 0.04245470986526787);\nL_u2 = ap(hb, 28, L_u2, 0.39331989319033134);\nL_u3 = ap(hb, 26, L_u3, 0.17073985049750015);\nL_u3 = ap(hb, 30, L_u3, 0.7457135887202412);\nL0Al = bq(st, 0, L_u0, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL0Al = bq(st, 2, L0Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL0Al = bq(st, 4, L0Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nL0Al = bq(st, 6, L0Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL0Ah1 = bq(st, 8, L_u0, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL0Ah1 = bq(st, 10, L0Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL0Alm = bq(st, 12, L0Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL0Alm = bq(st, 14, L0Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL0Alm = bq(st, 16, L0Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL0Ah2 = bq(st, 18, L0Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL0Ah2 = bq(st, 20, L0Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL0Amh = bq(st, 22, L0Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL0Amh = bq(st, 24, L0Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL0Ahi = bq(st, 26, L0Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL0Ahi = bq(st, 28, L0Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL0A = g_low * L0Al + g_lowmid * L0Alm + g_midhigh * L0Amh + g_high * L0Ahi;\nL0Cl = bq(st, 30, L_u0, C1_lb, 2 * C1_lb, C1_lb, C1_a1, C1_a2);\nL0Cl = bq(st, 32, L0Cl, C2_a2, C2_a1, 1, C2_a1, C2_a2);\nL0Cl = bq(st, 34, L0Cl, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nL0Ch1 = bq(st, 36, L_u0, C1_n, -2 * C1_n, C1_n, C1_a1, C1_a2);\nL0Ch1 = -L0Ch1;\nL0Clm = bq(st, 38, L0Ch1, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nL0Clm = bq(st, 40, L0Clm, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nL0Clm = bq(st, 42, L0Clm, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nL0Ch2 = bq(st, 44, L0Ch1, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nL0Ch2 = bq(st, 46, L0Ch2, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nL0Cmh = bq(st, 48, L0Ch2, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nL0Cmh = bq(st, 50, L0Cmh, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nL0Chi = bq(st, 52, L0Ch2, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nL0Chi = bq(st, 54, L0Chi, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nL0C = g_low * L0Cl + g_lowmid * L0Clm + g_midhigh * L0Cmh + g_high * L0Chi;\nL0Dl = bq(st, 56, L_u0, D1_lb, 2 * D1_lb, D1_lb, D1_a1, D1_a2);\nL0Dl = bq(st, 58, L0Dl, D2_a2, D2_a1, 1, D2_a1, D2_a2);\nL0Dl = bq(st, 60, L0Dl, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nL0Dh1 = bq(st, 62, L_u0, D1_n, -2 * D1_n, D1_n, D1_a1, D1_a2);\nL0Dh1 = -L0Dh1;\nL0Dlm = bq(st, 64, L0Dh1, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nL0Dlm = bq(st, 66, L0Dlm, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nL0Dlm = bq(st, 68, L0Dlm, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nL0Dh2 = bq(st, 70, L0Dh1, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nL0Dh2 = bq(st, 72, L0Dh2, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nL0Dmh = bq(st, 74, L0Dh2, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nL0Dmh = bq(st, 76, L0Dmh, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nL0Dhi = bq(st, 78, L0Dh2, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nL0Dhi = bq(st, 80, L0Dhi, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nL0D = g_low * L0Dl + g_lowmid * L0Dlm + g_midhigh * L0Dmh + g_high * L0Dhi;\nL_y0 = max(0, 1 - abs(s_x - 0)) * L0A + max(0, 1 - abs(s_x - 1)) * L0C + max(0, 1 - abs(s_x - 2)) * L0D;\nL1Al = bq(st, 0, L_u1, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL1Al = bq(st, 2, L1Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL1Al = bq(st, 4, L1Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nL1Al = bq(st, 6, L1Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL1Ah1 = bq(st, 8, L_u1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL1Ah1 = bq(st, 10, L1Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL1Alm = bq(st, 12, L1Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL1Alm = bq(st, 14, L1Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL1Alm = bq(st, 16, L1Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL1Ah2 = bq(st, 18, L1Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL1Ah2 = bq(st, 20, L1Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL1Amh = bq(st, 22, L1Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL1Amh = bq(st, 24, L1Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL1Ahi = bq(st, 26, L1Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL1Ahi = bq(st, 28, L1Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL1A = g_low * L1Al + g_lowmid * L1Alm + g_midhigh * L1Amh + g_high * L1Ahi;\nL1Cl = bq(st, 30, L_u1, C1_lb, 2 * C1_lb, C1_lb, C1_a1, C1_a2);\nL1Cl = bq(st, 32, L1Cl, C2_a2, C2_a1, 1, C2_a1, C2_a2);\nL1Cl = bq(st, 34, L1Cl, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nL1Ch1 = bq(st, 36, L_u1, C1_n, -2 * C1_n, C1_n, C1_a1, C1_a2);\nL1Ch1 = -L1Ch1;\nL1Clm = bq(st, 38, L1Ch1, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nL1Clm = bq(st, 40, L1Clm, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nL1Clm = bq(st, 42, L1Clm, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nL1Ch2 = bq(st, 44, L1Ch1, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nL1Ch2 = bq(st, 46, L1Ch2, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nL1Cmh = bq(st, 48, L1Ch2, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nL1Cmh = bq(st, 50, L1Cmh, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nL1Chi = bq(st, 52, L1Ch2, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nL1Chi = bq(st, 54, L1Chi, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nL1C = g_low * L1Cl + g_lowmid * L1Clm + g_midhigh * L1Cmh + g_high * L1Chi;\nL1Dl = bq(st, 56, L_u1, D1_lb, 2 * D1_lb, D1_lb, D1_a1, D1_a2);\nL1Dl = bq(st, 58, L1Dl, D2_a2, D2_a1, 1, D2_a1, D2_a2);\nL1Dl = bq(st, 60, L1Dl, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nL1Dh1 = bq(st, 62, L_u1, D1_n, -2 * D1_n, D1_n, D1_a1, D1_a2);\nL1Dh1 = -L1Dh1;\nL1Dlm = bq(st, 64, L1Dh1, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nL1Dlm = bq(st, 66, L1Dlm, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nL1Dlm = bq(st, 68, L1Dlm, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nL1Dh2 = bq(st, 70, L1Dh1, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nL1Dh2 = bq(st, 72, L1Dh2, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nL1Dmh = bq(st, 74, L1Dh2, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nL1Dmh = bq(st, 76, L1Dmh, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nL1Dhi = bq(st, 78, L1Dh2, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nL1Dhi = bq(st, 80, L1Dhi, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nL1D = g_low * L1Dl + g_lowmid * L1Dlm + g_midhigh * L1Dmh + g_high * L1Dhi;\nL_y1 = max(0, 1 - abs(s_x - 0)) * L1A + max(0, 1 - abs(s_x - 1)) * L1C + max(0, 1 - abs(s_x - 2)) * L1D;\nL2Al = bq(st, 0, L_u2, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL2Al = bq(st, 2, L2Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL2Al = bq(st, 4, L2Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nL2Al = bq(st, 6, L2Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL2Ah1 = bq(st, 8, L_u2, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL2Ah1 = bq(st, 10, L2Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL2Alm = bq(st, 12, L2Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL2Alm = bq(st, 14, L2Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL2Alm = bq(st, 16, L2Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL2Ah2 = bq(st, 18, L2Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL2Ah2 = bq(st, 20, L2Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL2Amh = bq(st, 22, L2Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL2Amh = bq(st, 24, L2Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL2Ahi = bq(st, 26, L2Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL2Ahi = bq(st, 28, L2Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL2A = g_low * L2Al + g_lowmid * L2Alm + g_midhigh * L2Amh + g_high * L2Ahi;\nL2Cl = bq(st, 30, L_u2, C1_lb, 2 * C1_lb, C1_lb, C1_a1, C1_a2);\nL2Cl = bq(st, 32, L2Cl, C2_a2, C2_a1, 1, C2_a1, C2_a2);\nL2Cl = bq(st, 34, L2Cl, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nL2Ch1 = bq(st, 36, L_u2, C1_n, -2 * C1_n, C1_n, C1_a1, C1_a2);\nL2Ch1 = -L2Ch1;\nL2Clm = bq(st, 38, L2Ch1, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nL2Clm = bq(st, 40, L2Clm, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nL2Clm = bq(st, 42, L2Clm, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nL2Ch2 = bq(st, 44, L2Ch1, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nL2Ch2 = bq(st, 46, L2Ch2, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nL2Cmh = bq(st, 48, L2Ch2, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nL2Cmh = bq(st, 50, L2Cmh, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nL2Chi = bq(st, 52, L2Ch2, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nL2Chi = bq(st, 54, L2Chi, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nL2C = g_low * L2Cl + g_lowmid * L2Clm + g_midhigh * L2Cmh + g_high * L2Chi;\nL2Dl = bq(st, 56, L_u2, D1_lb, 2 * D1_lb, D1_lb, D1_a1, D1_a2);\nL2Dl = bq(st, 58, L2Dl, D2_a2, D2_a1, 1, D2_a1, D2_a2);\nL2Dl = bq(st, 60, L2Dl, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nL2Dh1 = bq(st, 62, L_u2, D1_n, -2 * D1_n, D1_n, D1_a1, D1_a2);\nL2Dh1 = -L2Dh1;\nL2Dlm = bq(st, 64, L2Dh1, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nL2Dlm = bq(st, 66, L2Dlm, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nL2Dlm = bq(st, 68, L2Dlm, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nL2Dh2 = bq(st, 70, L2Dh1, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nL2Dh2 = bq(st, 72, L2Dh2, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nL2Dmh = bq(st, 74, L2Dh2, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nL2Dmh = bq(st, 76, L2Dmh, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nL2Dhi = bq(st, 78, L2Dh2, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nL2Dhi = bq(st, 80, L2Dhi, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nL2D = g_low * L2Dl + g_lowmid * L2Dlm + g_midhigh * L2Dmh + g_high * L2Dhi;\nL_y2 = max(0, 1 - abs(s_x - 0)) * L2A + max(0, 1 - abs(s_x - 1)) * L2C + max(0, 1 - abs(s_x - 2)) * L2D;\nL3Al = bq(st, 0, L_u3, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL3Al = bq(st, 2, L3Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL3Al = bq(st, 4, L3Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nL3Al = bq(st, 6, L3Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL3Ah1 = bq(st, 8, L_u3, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL3Ah1 = bq(st, 10, L3Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL3Alm = bq(st, 12, L3Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL3Alm = bq(st, 14, L3Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL3Alm = bq(st, 16, L3Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL3Ah2 = bq(st, 18, L3Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL3Ah2 = bq(st, 20, L3Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL3Amh = bq(st, 22, L3Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL3Amh = bq(st, 24, L3Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL3Ahi = bq(st, 26, L3Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL3Ahi = bq(st, 28, L3Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL3A = g_low * L3Al + g_lowmid * L3Alm + g_midhigh * L3Amh + g_high * L3Ahi;\nL3Cl = bq(st, 30, L_u3, C1_lb, 2 * C1_lb, C1_lb, C1_a1, C1_a2);\nL3Cl = bq(st, 32, L3Cl, C2_a2, C2_a1, 1, C2_a1, C2_a2);\nL3Cl = bq(st, 34, L3Cl, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nL3Ch1 = bq(st, 36, L_u3, C1_n, -2 * C1_n, C1_n, C1_a1, C1_a2);\nL3Ch1 = -L3Ch1;\nL3Clm = bq(st, 38, L3Ch1, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nL3Clm = bq(st, 40, L3Clm, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nL3Clm = bq(st, 42, L3Clm, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nL3Ch2 = bq(st, 44, L3Ch1, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nL3Ch2 = bq(st, 46, L3Ch2, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nL3Cmh = bq(st, 48, L3Ch2, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nL3Cmh = bq(st, 50, L3Cmh, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nL3Chi = bq(st, 52, L3Ch2, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nL3Chi = bq(st, 54, L3Chi, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nL3C = g_low * L3Cl + g_lowmid * L3Clm + g_midhigh * L3Cmh + g_high * L3Chi;\nL3Dl = bq(st, 56, L_u3, D1_lb, 2 * D1_lb, D1_lb, D1_a1, D1_a2);\nL3Dl = bq(st, 58, L3Dl, D2_a2, D2_a1, 1, D2_a1, D2_a2);\nL3Dl = bq(st, 60, L3Dl, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nL3Dh1 = bq(st, 62, L_u3, D1_n, -2 * D1_n, D1_n, D1_a1, D1_a2);\nL3Dh1 = -L3Dh1;\nL3Dlm = bq(st, 64, L3Dh1, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nL3Dlm = bq(st, 66, L3Dlm, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nL3Dlm = bq(st, 68, L3Dlm, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nL3Dh2 = bq(st, 70, L3Dh1, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nL3Dh2 = bq(st, 72, L3Dh2, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nL3Dmh = bq(st, 74, L3Dh2, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nL3Dmh = bq(st, 76, L3Dmh, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nL3Dhi = bq(st, 78, L3Dh2, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nL3Dhi = bq(st, 80, L3Dhi, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nL3D = g_low * L3Dl + g_lowmid * L3Dlm + g_midhigh * L3Dmh + g_high * L3Dhi;\nL_y3 = max(0, 1 - abs(s_x - 0)) * L3A + max(0, 1 - abs(s_x - 1)) * L3C + max(0, 1 - abs(s_x - 2)) * L3D;\nd0 = L_y1;\nd1 = L_y0;\nd0 = ap(hb, 32, d0, 0.04245470986526787);\nd0 = ap(hb, 36, d0, 0.39331989319033134);\nd1 = ap(hb, 34, d1, 0.17073985049750015);\nd1 = ap(hb, 38, d1, 0.7457135887202412);\nL_v0 = 0.5 * (d0 + d1);\nd0 = L_y3;\nd1 = L_y2;\nd0 = ap(hb, 32, d0, 0.04245470986526787);\nd0 = ap(hb, 36, d0, 0.39331989319033134);\nd1 = ap(hb, 34, d1, 0.17073985049750015);\nd1 = ap(hb, 38, d1, 0.7457135887202412);\nL_v1 = 0.5 * (d0 + d1);\nd0 = L_v1;\nd1 = L_v0;\nd0 = ap(hb, 40, d0, 0.019059005558478156);\nd0 = ap(hb, 44, d0, 0.1559582483500435);\nd0 = ap(hb, 48, d0, 0.3650536901969154);\nd0 = ap(hb, 52, d0, 0.5755010797915323);\nd0 = ap(hb, 56, d0, 0.7526447471286863);\nd0 = ap(hb, 60, d0, 0.8980636464339091);\nd1 = ap(hb, 42, d1, 0.07350243453590219);\nd1 = ap(hb, 46, d1, 0.25649919975582064);\nd1 = ap(hb, 50, d1, 0.47327898479453656);\nd1 = ap(hb, 54, d1, 0.6688095014357188);\nd1 = ap(hb, 58, d1, 0.8282265929955738);\nd1 = ap(hb, 62, d1, 0.9656701590349398);\nL_w = 0.5 * (d0 + d1);\nout1 = g_gain * g_fader * L_w;\n\n// ===== lato R =====\nR_e = in2;\nR_o = in2;\nR_e = ap(hb, 64, R_e, 0.019059005558478156);\nR_e = ap(hb, 68, R_e, 0.1559582483500435);\nR_e = ap(hb, 72, R_e, 0.3650536901969154);\nR_e = ap(hb, 76, R_e, 0.5755010797915323);\nR_e = ap(hb, 80, R_e, 0.7526447471286863);\nR_e = ap(hb, 84, R_e, 0.8980636464339091);\nR_o = ap(hb, 66, R_o, 0.07350243453590219);\nR_o = ap(hb, 70, R_o, 0.25649919975582064);\nR_o = ap(hb, 74, R_o, 0.47327898479453656);\nR_o = ap(hb, 78, R_o, 0.6688095014357188);\nR_o = ap(hb, 82, R_o, 0.8282265929955738);\nR_o = ap(hb, 86, R_o, 0.9656701590349398);\nR_u0 = R_e;\nR_u1 = R_e;\nR_u0 = ap(hb, 88, R_u0, 0.04245470986526787);\nR_u0 = ap(hb, 92, R_u0, 0.39331989319033134);\nR_u1 = ap(hb, 90, R_u1, 0.17073985049750015);\nR_u1 = ap(hb, 94, R_u1, 0.7457135887202412);\nR_u2 = R_o;\nR_u3 = R_o;\nR_u2 = ap(hb, 88, R_u2, 0.04245470986526787);\nR_u2 = ap(hb, 92, R_u2, 0.39331989319033134);\nR_u3 = ap(hb, 90, R_u3, 0.17073985049750015);\nR_u3 = ap(hb, 94, R_u3, 0.7457135887202412);\nR0Al = bq(st, 82, R_u0, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR0Al = bq(st, 84, R0Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR0Al = bq(st, 86, R0Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nR0Al = bq(st, 88, R0Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR0Ah1 = bq(st, 90, R_u0, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR0Ah1 = bq(st, 92, R0Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR0Alm = bq(st, 94, R0Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR0Alm = bq(st, 96, R0Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR0Alm = bq(st, 98, R0Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR0Ah2 = bq(st, 100, R0Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR0Ah2 = bq(st, 102, R0Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR0Amh = bq(st, 104, R0Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR0Amh = bq(st, 106, R0Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR0Ahi = bq(st, 108, R0Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR0Ahi = bq(st, 110, R0Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR0A = g_low * R0Al + g_lowmid * R0Alm + g_midhigh * R0Amh + g_high * R0Ahi;\nR0Cl = bq(st, 112, R_u0, C1_lb, 2 * C1_lb, C1_lb, C1_a1, C1_a2);\nR0Cl = bq(st, 114, R0Cl, C2_a2, C2_a1, 1, C2_a1, C2_a2);\nR0Cl = bq(st, 116, R0Cl, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nR0Ch1 = bq(st, 118, R_u0, C1_n, -2 * C1_n, C1_n, C1_a1, C1_a2);\nR0Ch1 = -R0Ch1;\nR0Clm = bq(st, 120, R0Ch1, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nR0Clm = bq(st, 122, R0Clm, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nR0Clm = bq(st, 124, R0Clm, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nR0Ch2 = bq(st, 126, R0Ch1, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nR0Ch2 = bq(st, 128, R0Ch2, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nR0Cmh = bq(st, 130, R0Ch2, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nR0Cmh = bq(st, 132, R0Cmh, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nR0Chi = bq(st, 134, R0Ch2, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nR0Chi = bq(st, 136, R0Chi, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nR0C = g_low * R0Cl + g_lowmid * R0Clm + g_midhigh * R0Cmh + g_high * R0Chi;\nR0Dl = bq(st, 138, R_u0, D1_lb, 2 * D1_lb, D1_lb, D1_a1, D1_a2);\nR0Dl = bq(st, 140, R0Dl, D2_a2, D2_a1, 1, D2_a1, D2_a2);\nR0Dl = bq(st, 142, R0Dl, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nR0Dh1 = bq(st, 144, R_u0, D1_n, -2 * D1_n, D1_n, D1_a1, D1_a2);\nR0Dh1 = -R0Dh1;\nR0Dlm = bq(st, 146, R0Dh1, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nR0Dlm = bq(st, 148, R0Dlm, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nR0Dlm = bq(st, 150, R0Dlm, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nR0Dh2 = bq(st, 152, R0Dh1, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nR0Dh2 = bq(st, 154, R0Dh2, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nR0Dmh = bq(st, 156, R0Dh2, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nR0Dmh = bq(st, 158, R0Dmh, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nR0Dhi = bq(st, 160, R0Dh2, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nR0Dhi = bq(st, 162, R0Dhi, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nR0D = g_low * R0Dl + g_lowmid * R0Dlm + g_midhigh * R0Dmh + g_high * R0Dhi;\nR_y0 = max(0, 1 - abs(s_x - 0)) * R0A + max(0, 1 - abs(s_x - 1)) * R0C + max(0, 1 - abs(s_x - 2)) * R0D;\nR1Al = bq(st, 82, R_u1, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR1Al = bq(st, 84, R1Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR1Al = bq(st, 86, R1Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nR1Al = bq(st, 88, R1Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR1Ah1 = bq(st, 90, R_u1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR1Ah1 = bq(st, 92, R1Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR1Alm = bq(st, 94, R1Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR1Alm = bq(st, 96, R1Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR1Alm = bq(st, 98, R1Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR1Ah2 = bq(st, 100, R1Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR1Ah2 = bq(st, 102, R1Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR1Amh = bq(st, 104, R1Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR1Amh = bq(st, 106, R1Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR1Ahi = bq(st, 108, R1Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR1Ahi = bq(st, 110, R1Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR1A = g_low * R1Al + g_lowmid * R1Alm + g_midhigh * R1Amh + g_high * R1Ahi;\nR1Cl = bq(st, 112, R_u1, C1_lb, 2 * C1_lb, C1_lb, C1_a1, C1_a2);\nR1Cl = bq(st, 114, R1Cl, C2_a2, C2_a1, 1, C2_a1, C2_a2);\nR1Cl = bq(st, 116, R1Cl, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nR1Ch1 = bq(st, 118, R_u1, C1_n, -2 * C1_n, C1_n, C1_a1, C1_a2);\nR1Ch1 = -R1Ch1;\nR1Clm = bq(st, 120, R1Ch1, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nR1Clm = bq(st, 122, R1Clm, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nR1Clm = bq(st, 124, R1Clm, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nR1Ch2 = bq(st, 126, R1Ch1, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nR1Ch2 = bq(st, 128, R1Ch2, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nR1Cmh = bq(st, 130, R1Ch2, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nR1Cmh = bq(st, 132, R1Cmh, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nR1Chi = bq(st, 134, R1Ch2, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nR1Chi = bq(st, 136, R1Chi, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nR1C = g_low * R1Cl + g_lowmid * R1Clm + g_midhigh * R1Cmh + g_high * R1Chi;\nR1Dl = bq(st, 138, R_u1, D1_lb, 2 * D1_lb, D1_lb, D1_a1, D1_a2);\nR1Dl = bq(st, 140, R1Dl, D2_a2, D2_a1, 1, D2_a1, D2_a2);\nR1Dl = bq(st, 142, R1Dl, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nR1Dh1 = bq(st, 144, R_u1, D1_n, -2 * D1_n, D1_n, D1_a1, D1_a2);\nR1Dh1 = -R1Dh1;\nR1Dlm = bq(st, 146, R1Dh1, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nR1Dlm = bq(st, 148, R1Dlm, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nR1Dlm = bq(st, 150, R1Dlm, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nR1Dh2 = bq(st, 152, R1Dh1, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nR1Dh2 = bq(st, 154, R1Dh2, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nR1Dmh = bq(st, 156, R1Dh2, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nR1Dmh = bq(st, 158, R1Dmh, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nR1Dhi = bq(st, 160, R1Dh2, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nR1Dhi = bq(st, 162, R1Dhi, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nR1D = g_low * R1Dl + g_lowmid * R1Dlm + g_midhigh * R1Dmh + g_high * R1Dhi;\nR_y1 = max(0, 1 - abs(s_x - 0)) * R1A + max(0, 1 - abs(s_x - 1)) * R1C + max(0, 1 - abs(s_x - 2)) * R1D;\nR2Al = bq(st, 82, R_u2, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR2Al = bq(st, 84, R2Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR2Al = bq(st, 86, R2Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nR2Al = bq(st, 88, R2Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR2Ah1 = bq(st, 90, R_u2, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR2Ah1 = bq(st, 92, R2Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR2Alm = bq(st, 94, R2Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR2Alm = bq(st, 96, R2Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR2Alm = bq(st, 98, R2Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR2Ah2 = bq(st, 100, R2Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR2Ah2 = bq(st, 102, R2Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR2Amh = bq(st, 104, R2Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR2Amh = bq(st, 106, R2Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR2Ahi = bq(st, 108, R2Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR2Ahi = bq(st, 110, R2Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR2A = g_low * R2Al + g_lowmid * R2Alm + g_midhigh * R2Amh + g_high * R2Ahi;\nR2Cl = bq(st, 112, R_u2, C1_lb, 2 * C1_lb, C1_lb, C1_a1, C1_a2);\nR2Cl = bq(st, 114, R2Cl, C2_a2, C2_a1, 1, C2_a1, C2_a2);\nR2Cl = bq(st, 116, R2Cl, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nR2Ch1 = bq(st, 118, R_u2, C1_n, -2 * C1_n, C1_n, C1_a1, C1_a2);\nR2Ch1 = -R2Ch1;\nR2Clm = bq(st, 120, R2Ch1, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nR2Clm = bq(st, 122, R2Clm, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nR2Clm = bq(st, 124, R2Clm, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nR2Ch2 = bq(st, 126, R2Ch1, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nR2Ch2 = bq(st, 128, R2Ch2, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nR2Cmh = bq(st, 130, R2Ch2, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nR2Cmh = bq(st, 132, R2Cmh, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nR2Chi = bq(st, 134, R2Ch2, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nR2Chi = bq(st, 136, R2Chi, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nR2C = g_low * R2Cl + g_lowmid * R2Clm + g_midhigh * R2Cmh + g_high * R2Chi;\nR2Dl = bq(st, 138, R_u2, D1_lb, 2 * D1_lb, D1_lb, D1_a1, D1_a2);\nR2Dl = bq(st, 140, R2Dl, D2_a2, D2_a1, 1, D2_a1, D2_a2);\nR2Dl = bq(st, 142, R2Dl, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nR2Dh1 = bq(st, 144, R_u2, D1_n, -2 * D1_n, D1_n, D1_a1, D1_a2);\nR2Dh1 = -R2Dh1;\nR2Dlm = bq(st, 146, R2Dh1, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nR2Dlm = bq(st, 148, R2Dlm, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nR2Dlm = bq(st, 150, R2Dlm, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nR2Dh2 = bq(st, 152, R2Dh1, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nR2Dh2 = bq(st, 154, R2Dh2, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nR2Dmh = bq(st, 156, R2Dh2, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nR2Dmh = bq(st, 158, R2Dmh, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nR2Dhi = bq(st, 160, R2Dh2, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nR2Dhi = bq(st, 162, R2Dhi, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nR2D = g_low * R2Dl + g_lowmid * R2Dlm + g_midhigh * R2Dmh + g_high * R2Dhi;\nR_y2 = max(0, 1 - abs(s_x - 0)) * R2A + max(0, 1 - abs(s_x - 1)) * R2C + max(0, 1 - abs(s_x - 2)) * R2D;\nR3Al = bq(st, 82, R_u3, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR3Al = bq(st, 84, R3Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR3Al = bq(st, 86, R3Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nR3Al = bq(st, 88, R3Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR3Ah1 = bq(st, 90, R_u3, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR3Ah1 = bq(st, 92, R3Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR3Alm = bq(st, 94, R3Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR3Alm = bq(st, 96, R3Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR3Alm = bq(st, 98, R3Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR3Ah2 = bq(st, 100, R3Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR3Ah2 = bq(st, 102, R3Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR3Amh = bq(st, 104, R3Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR3Amh = bq(st, 106, R3Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR3Ahi = bq(st, 108, R3Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR3Ahi = bq(st, 110, R3Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR3A = g_low * R3Al + g_lowmid * R3Alm + g_midhigh * R3Amh + g_high * R3Ahi;\nR3Cl = bq(st, 112, R_u3, C1_lb, 2 * C1_lb, C1_lb, C1_a1, C1_a2);\nR3Cl = bq(st, 114, R3Cl, C2_a2, C2_a1, 1, C2_a1, C2_a2);\nR3Cl = bq(st, 116, R3Cl, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nR3Ch1 = bq(st, 118, R_u3, C1_n, -2 * C1_n, C1_n, C1_a1, C1_a2);\nR3Ch1 = -R3Ch1;\nR3Clm = bq(st, 120, R3Ch1, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nR3Clm = bq(st, 122, R3Clm, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nR3Clm = bq(st, 124, R3Clm, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nR3Ch2 = bq(st, 126, R3Ch1, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nR3Ch2 = bq(st, 128, R3Ch2, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nR3Cmh = bq(st, 130, R3Ch2, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nR3Cmh = bq(st, 132, R3Cmh, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nR3Chi = bq(st, 134, R3Ch2, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nR3Chi = bq(st, 136, R3Chi, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nR3C = g_low * R3Cl + g_lowmid * R3Clm + g_midhigh * R3Cmh + g_high * R3Chi;\nR3Dl = bq(st, 138, R_u3, D1_lb, 2 * D1_lb, D1_lb, D1_a1, D1_a2);\nR3Dl = bq(st, 140, R3Dl, D2_a2, D2_a1, 1, D2_a1, D2_a2);\nR3Dl = bq(st, 142, R3Dl, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nR3Dh1 = bq(st, 144, R_u3, D1_n, -2 * D1_n, D1_n, D1_a1, D1_a2);\nR3Dh1 = -R3Dh1;\nR3Dlm = bq(st, 146, R3Dh1, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nR3Dlm = bq(st, 148, R3Dlm, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nR3Dlm = bq(st, 150, R3Dlm, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nR3Dh2 = bq(st, 152, R3Dh1, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nR3Dh2 = bq(st, 154, R3Dh2, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nR3Dmh = bq(st, 156, R3Dh2, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nR3Dmh = bq(st, 158, R3Dmh, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nR3Dhi = bq(st, 160, R3Dh2, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nR3Dhi = bq(st, 162, R3Dhi, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nR3D = g_low * R3Dl + g_lowmid * R3Dlm + g_midhigh * R3Dmh + g_high * R3Dhi;\nR_y3 = max(0, 1 - abs(s_x - 0)) * R3A + max(0, 1 - abs(s_x - 1)) * R3C + max(0, 1 - abs(s_x - 2)) * R3D;\nd0 = R_y1;\nd1 = R_y0;\nd0 = ap(hb, 96, d0, 0.04245470986526787);\nd0 = ap(hb, 100, d0, 0.39331989319033134);\nd1 = ap(hb, 98, d1, 0.17073985049750015);\nd1 = ap(hb, 102, d1, 0.7457135887202412);\nR_v0 = 0.5 * (d0 + d1);\nd0 = R_y3;\nd1 = R_y2;\nd0 = ap(hb, 96, d0, 0.04245470986526787);\nd0 = ap(hb, 100, d0, 0.39331989319033134);\nd1 = ap(hb, 98, d1, 0.17073985049750015);\nd1 = ap(hb, 102, d1, 0.7457135887202412);\nR_v1 = 0.5 * (d0 + d1);\nd0 = R_v1;\nd1 = R_v0;\nd0 = ap(hb, 104, d0, 0.019059005558478156);\nd0 = ap(hb, 108, d0, 0.1559582483500435);\nd0 = ap(hb, 112, d0, 0.3650536901969154);\nd0 = ap(hb, 116, d0, 0.5755010797915323);\nd0 = ap(hb, 120, d0, 0.7526447471286863);\nd0 = ap(hb, 124, d0, 0.8980636464339091);\nd1 = ap(hb, 106, d1, 0.07350243453590219);\nd1 = ap(hb, 110, d1, 0.25649919975582064);\nd1 = ap(hb, 114, d1, 0.47327898479453656);\nd1 = ap(hb, 118, d1, 0.6688095014357188);\nd1 = ap(hb, 122, d1, 0.8282265929955738);\nd1 = ap(hb, 126, d1, 0.9656701590349398);\nR_w = 0.5 * (d0 + d1);\nout2 = g_gain * g_fader * R_w;\n\n",
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
						70,
						240,
						40
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
						114,
						240,
						20
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
					"num_lines_patching": 2,
					"num_lines_presentation": 2
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
					"id": "obj-nota",
					"maxclass": "live.comment",
					"numinlets": 1,
					"numoutlets": 0,
					"presentation": 1,
					"presentation_rect": [
						8,
						138,
						250,
						30
					],
					"patching_rect": [
						20,
						440,
						250,
						36
					],
					"linecount": 2,
					"text": "50% = 0 dB (detent). Bande: 0% silenzio, 100% +6 dB. GAIN 100% = +10 dB."
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