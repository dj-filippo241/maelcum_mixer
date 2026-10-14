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
									"code": "// MC-CHANNEL - prototipo Max P0 del canale maelcum_mixer.\n// GENERATO da proto-max/coefficienti/genera.py: non modificare a mano.\n// GAIN -inf..0..+10 dB, isolator LR4 a 4 bande (0..+6 dB, silenzio a\n// fondo corsa), fader. Banca a 4x della frequenza di campionamento.\n\n// biquad in forma trasposta II; stato in m[i], m[i+1]\nbq(m, i, x, b0, b1, b2, a1, a2) {\n\ty = b0 * x + peek(m, i);\n\tpoke(m, b1 * x - a1 * y + peek(m, i + 1), i);\n\tpoke(m, b2 * x - a2 * y, i + 1);\n\treturn y;\n}\n\n// allpass del 1o ordine del halfband; stato in m[i] (x), m[i+1] (y)\nap(m, i, x, c) {\n\ty = c * (x - peek(m, i + 1)) + peek(m, i);\n\tpoke(m, x, i);\n\tpoke(m, y, i + 1);\n\treturn y;\n}\n\nParam gain(50.0, min=0, max=100);\nParam low(50.0, min=0, max=100);\nParam lowmid(50.0, min=0, max=100);\nParam midhigh(50.0, min=0, max=100);\nParam high(50.0, min=0, max=100);\nParam fader(100.0, min=0, max=100);\nParam incroci(0, min=0, max=1);\nData st(120);\nData hb(128);\nHistory s_gain(50.0);\nHistory s_low(50.0);\nHistory s_lowmid(50.0);\nHistory s_midhigh(50.0);\nHistory s_high(50.0);\nHistory s_fader(100.0);\nHistory s_x(0);\n\n// manopole lisciate: 10 ms (selettore 20 ms, dissolvenza A/B)\nt10 = exp(-1 / (0.010 * samplerate));\nt20 = exp(-1 / (0.020 * samplerate));\ns_gain = gain + t10 * (s_gain - gain);\ns_low = low + t10 * (s_low - low);\ns_lowmid = lowmid + t10 * (s_lowmid - lowmid);\ns_midhigh = midhigh + t10 * (s_midhigh - midhigh);\ns_high = high + t10 * (s_high - high);\ns_fader = fader + t10 * (s_fader - fader);\ns_x = incroci + t20 * (s_x - incroci);\n\n// GAIN: fondo corsa muto, meta CCW -100..0 dB, meta CW 0..+10 dB\ntg = s_gain / 100;\ng_gain = pow(10, min(200 * tg - 100, 20 * tg - 10) / 20) * (tg > 0);\n// bande: pot lineare x2; a fondo corsa il contatto da silenzio\ng_low = 2 * s_low / 100 * max(low > 0, s_low > 0.001);\ng_lowmid = 2 * s_lowmid / 100 * max(lowmid > 0, s_lowmid > 0.001);\ng_midhigh = 2 * s_midhigh / 100 * max(midhigh > 0, s_midhigh > 0.001);\ng_high = 2 * s_high / 100 * max(high > 0, s_high > 0.001);\n// fader [PROVVISORIO]: curva quadratica, -12 dB a meta corsa\ntf = s_fader / 100;\ng_fader = tf * tf;\n\n// coefficienti degli incroci (bilineare con prewarp, Q 0,7071)\nsr4 = samplerate * 4;\nA1_k = tan(pi * 150.0 / sr4);\nA1_kk = A1_k * A1_k;\nA1_n = 1 / (1 + A1_k * 1.4142135623730951 + A1_kk);\nA1_a1 = 2 * (A1_kk - 1) * A1_n;\nA1_a2 = (1 - A1_k * 1.4142135623730951 + A1_kk) * A1_n;\nA1_lb = A1_kk * A1_n;\nA2_k = tan(pi * 500.0 / sr4);\nA2_kk = A2_k * A2_k;\nA2_n = 1 / (1 + A2_k * 1.4142135623730951 + A2_kk);\nA2_a1 = 2 * (A2_kk - 1) * A2_n;\nA2_a2 = (1 - A2_k * 1.4142135623730951 + A2_kk) * A2_n;\nA2_lb = A2_kk * A2_n;\nA3_k = tan(pi * 2500.0 / sr4);\nA3_kk = A3_k * A3_k;\nA3_n = 1 / (1 + A3_k * 1.4142135623730951 + A3_kk);\nA3_a1 = 2 * (A3_kk - 1) * A3_n;\nA3_a2 = (1 - A3_k * 1.4142135623730951 + A3_kk) * A3_n;\nA3_lb = A3_kk * A3_n;\nB1_k = tan(pi * 100.0 / sr4);\nB1_kk = B1_k * B1_k;\nB1_n = 1 / (1 + B1_k * 1.4142135623730951 + B1_kk);\nB1_a1 = 2 * (B1_kk - 1) * B1_n;\nB1_a2 = (1 - B1_k * 1.4142135623730951 + B1_kk) * B1_n;\nB1_lb = B1_kk * B1_n;\nB2_k = tan(pi * 630.0 / sr4);\nB2_kk = B2_k * B2_k;\nB2_n = 1 / (1 + B2_k * 1.4142135623730951 + B2_kk);\nB2_a1 = 2 * (B2_kk - 1) * B2_n;\nB2_a2 = (1 - B2_k * 1.4142135623730951 + B2_kk) * B2_n;\nB2_lb = B2_kk * B2_n;\nB3_k = tan(pi * 4000.0 / sr4);\nB3_kk = B3_k * B3_k;\nB3_n = 1 / (1 + B3_k * 1.4142135623730951 + B3_kk);\nB3_a1 = 2 * (B3_kk - 1) * B3_n;\nB3_a2 = (1 - B3_k * 1.4142135623730951 + B3_kk) * B3_n;\nB3_lb = B3_kk * B3_n;\n\n// ===== lato L =====\nL_e = in1;\nL_o = in1;\nL_e = ap(hb, 0, L_e, 0.019059005558478156);\nL_e = ap(hb, 4, L_e, 0.1559582483500435);\nL_e = ap(hb, 8, L_e, 0.3650536901969154);\nL_e = ap(hb, 12, L_e, 0.5755010797915323);\nL_e = ap(hb, 16, L_e, 0.7526447471286863);\nL_e = ap(hb, 20, L_e, 0.8980636464339091);\nL_o = ap(hb, 2, L_o, 0.07350243453590219);\nL_o = ap(hb, 6, L_o, 0.25649919975582064);\nL_o = ap(hb, 10, L_o, 0.47327898479453656);\nL_o = ap(hb, 14, L_o, 0.6688095014357188);\nL_o = ap(hb, 18, L_o, 0.8282265929955738);\nL_o = ap(hb, 22, L_o, 0.9656701590349398);\nL_u0 = L_e;\nL_u1 = L_e;\nL_u0 = ap(hb, 24, L_u0, 0.04245470986526787);\nL_u0 = ap(hb, 28, L_u0, 0.39331989319033134);\nL_u1 = ap(hb, 26, L_u1, 0.17073985049750015);\nL_u1 = ap(hb, 30, L_u1, 0.7457135887202412);\nL_u2 = L_o;\nL_u3 = L_o;\nL_u2 = ap(hb, 24, L_u2, 0.04245470986526787);\nL_u2 = ap(hb, 28, L_u2, 0.39331989319033134);\nL_u3 = ap(hb, 26, L_u3, 0.17073985049750015);\nL_u3 = ap(hb, 30, L_u3, 0.7457135887202412);\nL0Al = bq(st, 0, L_u0, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL0Al = bq(st, 2, L0Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL0Al = bq(st, 4, L0Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nL0Al = bq(st, 6, L0Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL0Ah1 = bq(st, 8, L_u0, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL0Ah1 = bq(st, 10, L0Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL0Alm = bq(st, 12, L0Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL0Alm = bq(st, 14, L0Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL0Alm = bq(st, 16, L0Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL0Ah2 = bq(st, 18, L0Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL0Ah2 = bq(st, 20, L0Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL0Amh = bq(st, 22, L0Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL0Amh = bq(st, 24, L0Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL0Ahi = bq(st, 26, L0Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL0Ahi = bq(st, 28, L0Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL0A = g_low * L0Al + g_lowmid * L0Alm + g_midhigh * L0Amh + g_high * L0Ahi;\nL0Bl = bq(st, 30, L_u0, B1_lb, 2 * B1_lb, B1_lb, B1_a1, B1_a2);\nL0Bl = bq(st, 32, L0Bl, B1_lb, 2 * B1_lb, B1_lb, B1_a1, B1_a2);\nL0Bl = bq(st, 34, L0Bl, B2_a2, B2_a1, 1, B2_a1, B2_a2);\nL0Bl = bq(st, 36, L0Bl, B3_a2, B3_a1, 1, B3_a1, B3_a2);\nL0Bh1 = bq(st, 38, L_u0, B1_n, -2 * B1_n, B1_n, B1_a1, B1_a2);\nL0Bh1 = bq(st, 40, L0Bh1, B1_n, -2 * B1_n, B1_n, B1_a1, B1_a2);\nL0Blm = bq(st, 42, L0Bh1, B2_lb, 2 * B2_lb, B2_lb, B2_a1, B2_a2);\nL0Blm = bq(st, 44, L0Blm, B2_lb, 2 * B2_lb, B2_lb, B2_a1, B2_a2);\nL0Blm = bq(st, 46, L0Blm, B3_a2, B3_a1, 1, B3_a1, B3_a2);\nL0Bh2 = bq(st, 48, L0Bh1, B2_n, -2 * B2_n, B2_n, B2_a1, B2_a2);\nL0Bh2 = bq(st, 50, L0Bh2, B2_n, -2 * B2_n, B2_n, B2_a1, B2_a2);\nL0Bmh = bq(st, 52, L0Bh2, B3_lb, 2 * B3_lb, B3_lb, B3_a1, B3_a2);\nL0Bmh = bq(st, 54, L0Bmh, B3_lb, 2 * B3_lb, B3_lb, B3_a1, B3_a2);\nL0Bhi = bq(st, 56, L0Bh2, B3_n, -2 * B3_n, B3_n, B3_a1, B3_a2);\nL0Bhi = bq(st, 58, L0Bhi, B3_n, -2 * B3_n, B3_n, B3_a1, B3_a2);\nL0B = g_low * L0Bl + g_lowmid * L0Blm + g_midhigh * L0Bmh + g_high * L0Bhi;\nL_y0 = (1 - s_x) * L0A + s_x * L0B;\nL1Al = bq(st, 0, L_u1, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL1Al = bq(st, 2, L1Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL1Al = bq(st, 4, L1Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nL1Al = bq(st, 6, L1Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL1Ah1 = bq(st, 8, L_u1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL1Ah1 = bq(st, 10, L1Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL1Alm = bq(st, 12, L1Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL1Alm = bq(st, 14, L1Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL1Alm = bq(st, 16, L1Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL1Ah2 = bq(st, 18, L1Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL1Ah2 = bq(st, 20, L1Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL1Amh = bq(st, 22, L1Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL1Amh = bq(st, 24, L1Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL1Ahi = bq(st, 26, L1Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL1Ahi = bq(st, 28, L1Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL1A = g_low * L1Al + g_lowmid * L1Alm + g_midhigh * L1Amh + g_high * L1Ahi;\nL1Bl = bq(st, 30, L_u1, B1_lb, 2 * B1_lb, B1_lb, B1_a1, B1_a2);\nL1Bl = bq(st, 32, L1Bl, B1_lb, 2 * B1_lb, B1_lb, B1_a1, B1_a2);\nL1Bl = bq(st, 34, L1Bl, B2_a2, B2_a1, 1, B2_a1, B2_a2);\nL1Bl = bq(st, 36, L1Bl, B3_a2, B3_a1, 1, B3_a1, B3_a2);\nL1Bh1 = bq(st, 38, L_u1, B1_n, -2 * B1_n, B1_n, B1_a1, B1_a2);\nL1Bh1 = bq(st, 40, L1Bh1, B1_n, -2 * B1_n, B1_n, B1_a1, B1_a2);\nL1Blm = bq(st, 42, L1Bh1, B2_lb, 2 * B2_lb, B2_lb, B2_a1, B2_a2);\nL1Blm = bq(st, 44, L1Blm, B2_lb, 2 * B2_lb, B2_lb, B2_a1, B2_a2);\nL1Blm = bq(st, 46, L1Blm, B3_a2, B3_a1, 1, B3_a1, B3_a2);\nL1Bh2 = bq(st, 48, L1Bh1, B2_n, -2 * B2_n, B2_n, B2_a1, B2_a2);\nL1Bh2 = bq(st, 50, L1Bh2, B2_n, -2 * B2_n, B2_n, B2_a1, B2_a2);\nL1Bmh = bq(st, 52, L1Bh2, B3_lb, 2 * B3_lb, B3_lb, B3_a1, B3_a2);\nL1Bmh = bq(st, 54, L1Bmh, B3_lb, 2 * B3_lb, B3_lb, B3_a1, B3_a2);\nL1Bhi = bq(st, 56, L1Bh2, B3_n, -2 * B3_n, B3_n, B3_a1, B3_a2);\nL1Bhi = bq(st, 58, L1Bhi, B3_n, -2 * B3_n, B3_n, B3_a1, B3_a2);\nL1B = g_low * L1Bl + g_lowmid * L1Blm + g_midhigh * L1Bmh + g_high * L1Bhi;\nL_y1 = (1 - s_x) * L1A + s_x * L1B;\nL2Al = bq(st, 0, L_u2, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL2Al = bq(st, 2, L2Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL2Al = bq(st, 4, L2Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nL2Al = bq(st, 6, L2Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL2Ah1 = bq(st, 8, L_u2, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL2Ah1 = bq(st, 10, L2Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL2Alm = bq(st, 12, L2Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL2Alm = bq(st, 14, L2Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL2Alm = bq(st, 16, L2Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL2Ah2 = bq(st, 18, L2Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL2Ah2 = bq(st, 20, L2Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL2Amh = bq(st, 22, L2Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL2Amh = bq(st, 24, L2Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL2Ahi = bq(st, 26, L2Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL2Ahi = bq(st, 28, L2Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL2A = g_low * L2Al + g_lowmid * L2Alm + g_midhigh * L2Amh + g_high * L2Ahi;\nL2Bl = bq(st, 30, L_u2, B1_lb, 2 * B1_lb, B1_lb, B1_a1, B1_a2);\nL2Bl = bq(st, 32, L2Bl, B1_lb, 2 * B1_lb, B1_lb, B1_a1, B1_a2);\nL2Bl = bq(st, 34, L2Bl, B2_a2, B2_a1, 1, B2_a1, B2_a2);\nL2Bl = bq(st, 36, L2Bl, B3_a2, B3_a1, 1, B3_a1, B3_a2);\nL2Bh1 = bq(st, 38, L_u2, B1_n, -2 * B1_n, B1_n, B1_a1, B1_a2);\nL2Bh1 = bq(st, 40, L2Bh1, B1_n, -2 * B1_n, B1_n, B1_a1, B1_a2);\nL2Blm = bq(st, 42, L2Bh1, B2_lb, 2 * B2_lb, B2_lb, B2_a1, B2_a2);\nL2Blm = bq(st, 44, L2Blm, B2_lb, 2 * B2_lb, B2_lb, B2_a1, B2_a2);\nL2Blm = bq(st, 46, L2Blm, B3_a2, B3_a1, 1, B3_a1, B3_a2);\nL2Bh2 = bq(st, 48, L2Bh1, B2_n, -2 * B2_n, B2_n, B2_a1, B2_a2);\nL2Bh2 = bq(st, 50, L2Bh2, B2_n, -2 * B2_n, B2_n, B2_a1, B2_a2);\nL2Bmh = bq(st, 52, L2Bh2, B3_lb, 2 * B3_lb, B3_lb, B3_a1, B3_a2);\nL2Bmh = bq(st, 54, L2Bmh, B3_lb, 2 * B3_lb, B3_lb, B3_a1, B3_a2);\nL2Bhi = bq(st, 56, L2Bh2, B3_n, -2 * B3_n, B3_n, B3_a1, B3_a2);\nL2Bhi = bq(st, 58, L2Bhi, B3_n, -2 * B3_n, B3_n, B3_a1, B3_a2);\nL2B = g_low * L2Bl + g_lowmid * L2Blm + g_midhigh * L2Bmh + g_high * L2Bhi;\nL_y2 = (1 - s_x) * L2A + s_x * L2B;\nL3Al = bq(st, 0, L_u3, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL3Al = bq(st, 2, L3Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL3Al = bq(st, 4, L3Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nL3Al = bq(st, 6, L3Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL3Ah1 = bq(st, 8, L_u3, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL3Ah1 = bq(st, 10, L3Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL3Alm = bq(st, 12, L3Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL3Alm = bq(st, 14, L3Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL3Alm = bq(st, 16, L3Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL3Ah2 = bq(st, 18, L3Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL3Ah2 = bq(st, 20, L3Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL3Amh = bq(st, 22, L3Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL3Amh = bq(st, 24, L3Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL3Ahi = bq(st, 26, L3Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL3Ahi = bq(st, 28, L3Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL3A = g_low * L3Al + g_lowmid * L3Alm + g_midhigh * L3Amh + g_high * L3Ahi;\nL3Bl = bq(st, 30, L_u3, B1_lb, 2 * B1_lb, B1_lb, B1_a1, B1_a2);\nL3Bl = bq(st, 32, L3Bl, B1_lb, 2 * B1_lb, B1_lb, B1_a1, B1_a2);\nL3Bl = bq(st, 34, L3Bl, B2_a2, B2_a1, 1, B2_a1, B2_a2);\nL3Bl = bq(st, 36, L3Bl, B3_a2, B3_a1, 1, B3_a1, B3_a2);\nL3Bh1 = bq(st, 38, L_u3, B1_n, -2 * B1_n, B1_n, B1_a1, B1_a2);\nL3Bh1 = bq(st, 40, L3Bh1, B1_n, -2 * B1_n, B1_n, B1_a1, B1_a2);\nL3Blm = bq(st, 42, L3Bh1, B2_lb, 2 * B2_lb, B2_lb, B2_a1, B2_a2);\nL3Blm = bq(st, 44, L3Blm, B2_lb, 2 * B2_lb, B2_lb, B2_a1, B2_a2);\nL3Blm = bq(st, 46, L3Blm, B3_a2, B3_a1, 1, B3_a1, B3_a2);\nL3Bh2 = bq(st, 48, L3Bh1, B2_n, -2 * B2_n, B2_n, B2_a1, B2_a2);\nL3Bh2 = bq(st, 50, L3Bh2, B2_n, -2 * B2_n, B2_n, B2_a1, B2_a2);\nL3Bmh = bq(st, 52, L3Bh2, B3_lb, 2 * B3_lb, B3_lb, B3_a1, B3_a2);\nL3Bmh = bq(st, 54, L3Bmh, B3_lb, 2 * B3_lb, B3_lb, B3_a1, B3_a2);\nL3Bhi = bq(st, 56, L3Bh2, B3_n, -2 * B3_n, B3_n, B3_a1, B3_a2);\nL3Bhi = bq(st, 58, L3Bhi, B3_n, -2 * B3_n, B3_n, B3_a1, B3_a2);\nL3B = g_low * L3Bl + g_lowmid * L3Blm + g_midhigh * L3Bmh + g_high * L3Bhi;\nL_y3 = (1 - s_x) * L3A + s_x * L3B;\nd0 = L_y1;\nd1 = L_y0;\nd0 = ap(hb, 32, d0, 0.04245470986526787);\nd0 = ap(hb, 36, d0, 0.39331989319033134);\nd1 = ap(hb, 34, d1, 0.17073985049750015);\nd1 = ap(hb, 38, d1, 0.7457135887202412);\nL_v0 = 0.5 * (d0 + d1);\nd0 = L_y3;\nd1 = L_y2;\nd0 = ap(hb, 32, d0, 0.04245470986526787);\nd0 = ap(hb, 36, d0, 0.39331989319033134);\nd1 = ap(hb, 34, d1, 0.17073985049750015);\nd1 = ap(hb, 38, d1, 0.7457135887202412);\nL_v1 = 0.5 * (d0 + d1);\nd0 = L_v1;\nd1 = L_v0;\nd0 = ap(hb, 40, d0, 0.019059005558478156);\nd0 = ap(hb, 44, d0, 0.1559582483500435);\nd0 = ap(hb, 48, d0, 0.3650536901969154);\nd0 = ap(hb, 52, d0, 0.5755010797915323);\nd0 = ap(hb, 56, d0, 0.7526447471286863);\nd0 = ap(hb, 60, d0, 0.8980636464339091);\nd1 = ap(hb, 42, d1, 0.07350243453590219);\nd1 = ap(hb, 46, d1, 0.25649919975582064);\nd1 = ap(hb, 50, d1, 0.47327898479453656);\nd1 = ap(hb, 54, d1, 0.6688095014357188);\nd1 = ap(hb, 58, d1, 0.8282265929955738);\nd1 = ap(hb, 62, d1, 0.9656701590349398);\nL_w = 0.5 * (d0 + d1);\nout1 = g_gain * g_fader * L_w;\n\n// ===== lato R =====\nR_e = in2;\nR_o = in2;\nR_e = ap(hb, 64, R_e, 0.019059005558478156);\nR_e = ap(hb, 68, R_e, 0.1559582483500435);\nR_e = ap(hb, 72, R_e, 0.3650536901969154);\nR_e = ap(hb, 76, R_e, 0.5755010797915323);\nR_e = ap(hb, 80, R_e, 0.7526447471286863);\nR_e = ap(hb, 84, R_e, 0.8980636464339091);\nR_o = ap(hb, 66, R_o, 0.07350243453590219);\nR_o = ap(hb, 70, R_o, 0.25649919975582064);\nR_o = ap(hb, 74, R_o, 0.47327898479453656);\nR_o = ap(hb, 78, R_o, 0.6688095014357188);\nR_o = ap(hb, 82, R_o, 0.8282265929955738);\nR_o = ap(hb, 86, R_o, 0.9656701590349398);\nR_u0 = R_e;\nR_u1 = R_e;\nR_u0 = ap(hb, 88, R_u0, 0.04245470986526787);\nR_u0 = ap(hb, 92, R_u0, 0.39331989319033134);\nR_u1 = ap(hb, 90, R_u1, 0.17073985049750015);\nR_u1 = ap(hb, 94, R_u1, 0.7457135887202412);\nR_u2 = R_o;\nR_u3 = R_o;\nR_u2 = ap(hb, 88, R_u2, 0.04245470986526787);\nR_u2 = ap(hb, 92, R_u2, 0.39331989319033134);\nR_u3 = ap(hb, 90, R_u3, 0.17073985049750015);\nR_u3 = ap(hb, 94, R_u3, 0.7457135887202412);\nR0Al = bq(st, 60, R_u0, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR0Al = bq(st, 62, R0Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR0Al = bq(st, 64, R0Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nR0Al = bq(st, 66, R0Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR0Ah1 = bq(st, 68, R_u0, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR0Ah1 = bq(st, 70, R0Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR0Alm = bq(st, 72, R0Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR0Alm = bq(st, 74, R0Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR0Alm = bq(st, 76, R0Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR0Ah2 = bq(st, 78, R0Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR0Ah2 = bq(st, 80, R0Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR0Amh = bq(st, 82, R0Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR0Amh = bq(st, 84, R0Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR0Ahi = bq(st, 86, R0Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR0Ahi = bq(st, 88, R0Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR0A = g_low * R0Al + g_lowmid * R0Alm + g_midhigh * R0Amh + g_high * R0Ahi;\nR0Bl = bq(st, 90, R_u0, B1_lb, 2 * B1_lb, B1_lb, B1_a1, B1_a2);\nR0Bl = bq(st, 92, R0Bl, B1_lb, 2 * B1_lb, B1_lb, B1_a1, B1_a2);\nR0Bl = bq(st, 94, R0Bl, B2_a2, B2_a1, 1, B2_a1, B2_a2);\nR0Bl = bq(st, 96, R0Bl, B3_a2, B3_a1, 1, B3_a1, B3_a2);\nR0Bh1 = bq(st, 98, R_u0, B1_n, -2 * B1_n, B1_n, B1_a1, B1_a2);\nR0Bh1 = bq(st, 100, R0Bh1, B1_n, -2 * B1_n, B1_n, B1_a1, B1_a2);\nR0Blm = bq(st, 102, R0Bh1, B2_lb, 2 * B2_lb, B2_lb, B2_a1, B2_a2);\nR0Blm = bq(st, 104, R0Blm, B2_lb, 2 * B2_lb, B2_lb, B2_a1, B2_a2);\nR0Blm = bq(st, 106, R0Blm, B3_a2, B3_a1, 1, B3_a1, B3_a2);\nR0Bh2 = bq(st, 108, R0Bh1, B2_n, -2 * B2_n, B2_n, B2_a1, B2_a2);\nR0Bh2 = bq(st, 110, R0Bh2, B2_n, -2 * B2_n, B2_n, B2_a1, B2_a2);\nR0Bmh = bq(st, 112, R0Bh2, B3_lb, 2 * B3_lb, B3_lb, B3_a1, B3_a2);\nR0Bmh = bq(st, 114, R0Bmh, B3_lb, 2 * B3_lb, B3_lb, B3_a1, B3_a2);\nR0Bhi = bq(st, 116, R0Bh2, B3_n, -2 * B3_n, B3_n, B3_a1, B3_a2);\nR0Bhi = bq(st, 118, R0Bhi, B3_n, -2 * B3_n, B3_n, B3_a1, B3_a2);\nR0B = g_low * R0Bl + g_lowmid * R0Blm + g_midhigh * R0Bmh + g_high * R0Bhi;\nR_y0 = (1 - s_x) * R0A + s_x * R0B;\nR1Al = bq(st, 60, R_u1, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR1Al = bq(st, 62, R1Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR1Al = bq(st, 64, R1Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nR1Al = bq(st, 66, R1Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR1Ah1 = bq(st, 68, R_u1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR1Ah1 = bq(st, 70, R1Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR1Alm = bq(st, 72, R1Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR1Alm = bq(st, 74, R1Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR1Alm = bq(st, 76, R1Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR1Ah2 = bq(st, 78, R1Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR1Ah2 = bq(st, 80, R1Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR1Amh = bq(st, 82, R1Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR1Amh = bq(st, 84, R1Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR1Ahi = bq(st, 86, R1Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR1Ahi = bq(st, 88, R1Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR1A = g_low * R1Al + g_lowmid * R1Alm + g_midhigh * R1Amh + g_high * R1Ahi;\nR1Bl = bq(st, 90, R_u1, B1_lb, 2 * B1_lb, B1_lb, B1_a1, B1_a2);\nR1Bl = bq(st, 92, R1Bl, B1_lb, 2 * B1_lb, B1_lb, B1_a1, B1_a2);\nR1Bl = bq(st, 94, R1Bl, B2_a2, B2_a1, 1, B2_a1, B2_a2);\nR1Bl = bq(st, 96, R1Bl, B3_a2, B3_a1, 1, B3_a1, B3_a2);\nR1Bh1 = bq(st, 98, R_u1, B1_n, -2 * B1_n, B1_n, B1_a1, B1_a2);\nR1Bh1 = bq(st, 100, R1Bh1, B1_n, -2 * B1_n, B1_n, B1_a1, B1_a2);\nR1Blm = bq(st, 102, R1Bh1, B2_lb, 2 * B2_lb, B2_lb, B2_a1, B2_a2);\nR1Blm = bq(st, 104, R1Blm, B2_lb, 2 * B2_lb, B2_lb, B2_a1, B2_a2);\nR1Blm = bq(st, 106, R1Blm, B3_a2, B3_a1, 1, B3_a1, B3_a2);\nR1Bh2 = bq(st, 108, R1Bh1, B2_n, -2 * B2_n, B2_n, B2_a1, B2_a2);\nR1Bh2 = bq(st, 110, R1Bh2, B2_n, -2 * B2_n, B2_n, B2_a1, B2_a2);\nR1Bmh = bq(st, 112, R1Bh2, B3_lb, 2 * B3_lb, B3_lb, B3_a1, B3_a2);\nR1Bmh = bq(st, 114, R1Bmh, B3_lb, 2 * B3_lb, B3_lb, B3_a1, B3_a2);\nR1Bhi = bq(st, 116, R1Bh2, B3_n, -2 * B3_n, B3_n, B3_a1, B3_a2);\nR1Bhi = bq(st, 118, R1Bhi, B3_n, -2 * B3_n, B3_n, B3_a1, B3_a2);\nR1B = g_low * R1Bl + g_lowmid * R1Blm + g_midhigh * R1Bmh + g_high * R1Bhi;\nR_y1 = (1 - s_x) * R1A + s_x * R1B;\nR2Al = bq(st, 60, R_u2, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR2Al = bq(st, 62, R2Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR2Al = bq(st, 64, R2Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nR2Al = bq(st, 66, R2Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR2Ah1 = bq(st, 68, R_u2, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR2Ah1 = bq(st, 70, R2Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR2Alm = bq(st, 72, R2Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR2Alm = bq(st, 74, R2Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR2Alm = bq(st, 76, R2Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR2Ah2 = bq(st, 78, R2Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR2Ah2 = bq(st, 80, R2Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR2Amh = bq(st, 82, R2Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR2Amh = bq(st, 84, R2Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR2Ahi = bq(st, 86, R2Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR2Ahi = bq(st, 88, R2Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR2A = g_low * R2Al + g_lowmid * R2Alm + g_midhigh * R2Amh + g_high * R2Ahi;\nR2Bl = bq(st, 90, R_u2, B1_lb, 2 * B1_lb, B1_lb, B1_a1, B1_a2);\nR2Bl = bq(st, 92, R2Bl, B1_lb, 2 * B1_lb, B1_lb, B1_a1, B1_a2);\nR2Bl = bq(st, 94, R2Bl, B2_a2, B2_a1, 1, B2_a1, B2_a2);\nR2Bl = bq(st, 96, R2Bl, B3_a2, B3_a1, 1, B3_a1, B3_a2);\nR2Bh1 = bq(st, 98, R_u2, B1_n, -2 * B1_n, B1_n, B1_a1, B1_a2);\nR2Bh1 = bq(st, 100, R2Bh1, B1_n, -2 * B1_n, B1_n, B1_a1, B1_a2);\nR2Blm = bq(st, 102, R2Bh1, B2_lb, 2 * B2_lb, B2_lb, B2_a1, B2_a2);\nR2Blm = bq(st, 104, R2Blm, B2_lb, 2 * B2_lb, B2_lb, B2_a1, B2_a2);\nR2Blm = bq(st, 106, R2Blm, B3_a2, B3_a1, 1, B3_a1, B3_a2);\nR2Bh2 = bq(st, 108, R2Bh1, B2_n, -2 * B2_n, B2_n, B2_a1, B2_a2);\nR2Bh2 = bq(st, 110, R2Bh2, B2_n, -2 * B2_n, B2_n, B2_a1, B2_a2);\nR2Bmh = bq(st, 112, R2Bh2, B3_lb, 2 * B3_lb, B3_lb, B3_a1, B3_a2);\nR2Bmh = bq(st, 114, R2Bmh, B3_lb, 2 * B3_lb, B3_lb, B3_a1, B3_a2);\nR2Bhi = bq(st, 116, R2Bh2, B3_n, -2 * B3_n, B3_n, B3_a1, B3_a2);\nR2Bhi = bq(st, 118, R2Bhi, B3_n, -2 * B3_n, B3_n, B3_a1, B3_a2);\nR2B = g_low * R2Bl + g_lowmid * R2Blm + g_midhigh * R2Bmh + g_high * R2Bhi;\nR_y2 = (1 - s_x) * R2A + s_x * R2B;\nR3Al = bq(st, 60, R_u3, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR3Al = bq(st, 62, R3Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR3Al = bq(st, 64, R3Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nR3Al = bq(st, 66, R3Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR3Ah1 = bq(st, 68, R_u3, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR3Ah1 = bq(st, 70, R3Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR3Alm = bq(st, 72, R3Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR3Alm = bq(st, 74, R3Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR3Alm = bq(st, 76, R3Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR3Ah2 = bq(st, 78, R3Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR3Ah2 = bq(st, 80, R3Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR3Amh = bq(st, 82, R3Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR3Amh = bq(st, 84, R3Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR3Ahi = bq(st, 86, R3Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR3Ahi = bq(st, 88, R3Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR3A = g_low * R3Al + g_lowmid * R3Alm + g_midhigh * R3Amh + g_high * R3Ahi;\nR3Bl = bq(st, 90, R_u3, B1_lb, 2 * B1_lb, B1_lb, B1_a1, B1_a2);\nR3Bl = bq(st, 92, R3Bl, B1_lb, 2 * B1_lb, B1_lb, B1_a1, B1_a2);\nR3Bl = bq(st, 94, R3Bl, B2_a2, B2_a1, 1, B2_a1, B2_a2);\nR3Bl = bq(st, 96, R3Bl, B3_a2, B3_a1, 1, B3_a1, B3_a2);\nR3Bh1 = bq(st, 98, R_u3, B1_n, -2 * B1_n, B1_n, B1_a1, B1_a2);\nR3Bh1 = bq(st, 100, R3Bh1, B1_n, -2 * B1_n, B1_n, B1_a1, B1_a2);\nR3Blm = bq(st, 102, R3Bh1, B2_lb, 2 * B2_lb, B2_lb, B2_a1, B2_a2);\nR3Blm = bq(st, 104, R3Blm, B2_lb, 2 * B2_lb, B2_lb, B2_a1, B2_a2);\nR3Blm = bq(st, 106, R3Blm, B3_a2, B3_a1, 1, B3_a1, B3_a2);\nR3Bh2 = bq(st, 108, R3Bh1, B2_n, -2 * B2_n, B2_n, B2_a1, B2_a2);\nR3Bh2 = bq(st, 110, R3Bh2, B2_n, -2 * B2_n, B2_n, B2_a1, B2_a2);\nR3Bmh = bq(st, 112, R3Bh2, B3_lb, 2 * B3_lb, B3_lb, B3_a1, B3_a2);\nR3Bmh = bq(st, 114, R3Bmh, B3_lb, 2 * B3_lb, B3_lb, B3_a1, B3_a2);\nR3Bhi = bq(st, 116, R3Bh2, B3_n, -2 * B3_n, B3_n, B3_a1, B3_a2);\nR3Bhi = bq(st, 118, R3Bhi, B3_n, -2 * B3_n, B3_n, B3_a1, B3_a2);\nR3B = g_low * R3Bl + g_lowmid * R3Blm + g_midhigh * R3Bmh + g_high * R3Bhi;\nR_y3 = (1 - s_x) * R3A + s_x * R3B;\nd0 = R_y1;\nd1 = R_y0;\nd0 = ap(hb, 96, d0, 0.04245470986526787);\nd0 = ap(hb, 100, d0, 0.39331989319033134);\nd1 = ap(hb, 98, d1, 0.17073985049750015);\nd1 = ap(hb, 102, d1, 0.7457135887202412);\nR_v0 = 0.5 * (d0 + d1);\nd0 = R_y3;\nd1 = R_y2;\nd0 = ap(hb, 96, d0, 0.04245470986526787);\nd0 = ap(hb, 100, d0, 0.39331989319033134);\nd1 = ap(hb, 98, d1, 0.17073985049750015);\nd1 = ap(hb, 102, d1, 0.7457135887202412);\nR_v1 = 0.5 * (d0 + d1);\nd0 = R_v1;\nd1 = R_v0;\nd0 = ap(hb, 104, d0, 0.019059005558478156);\nd0 = ap(hb, 108, d0, 0.1559582483500435);\nd0 = ap(hb, 112, d0, 0.3650536901969154);\nd0 = ap(hb, 116, d0, 0.5755010797915323);\nd0 = ap(hb, 120, d0, 0.7526447471286863);\nd0 = ap(hb, 124, d0, 0.8980636464339091);\nd1 = ap(hb, 106, d1, 0.07350243453590219);\nd1 = ap(hb, 110, d1, 0.25649919975582064);\nd1 = ap(hb, 114, d1, 0.47327898479453656);\nd1 = ap(hb, 118, d1, 0.6688095014357188);\nd1 = ap(hb, 122, d1, 0.8282265929955738);\nd1 = ap(hb, 126, d1, 0.9656701590349398);\nR_w = 0.5 * (d0 + d1);\nout2 = g_gain * g_fader * R_w;\n\n",
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
								"B 100/630/4000"
							],
							"parameter_mmax": 1.0,
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
					"id": "obj-nota",
					"maxclass": "live.comment",
					"numinlets": 1,
					"numoutlets": 0,
					"presentation": 1,
					"presentation_rect": [
						8,
						120,
						250,
						36
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