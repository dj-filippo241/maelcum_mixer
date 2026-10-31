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
									"code": "// MC-CHANNEL - prototipo Max P0 del canale maelcum_mixer.\n// GENERATO da proto-max/coefficienti/genera.py: non modificare a mano.\n// GAIN -inf..0..+10 dB, isolator a 4 bande (0..+6 dB, silenzio a\n// fondo corsa), fader. Banca a 4x della frequenza di campionamento.\n\n// biquad in forma trasposta II; stato in m[i], m[i+1]\nbq(m, i, x, b0, b1, b2, a1, a2) {\n\ty = b0 * x + peek(m, i);\n\tpoke(m, b1 * x - a1 * y + peek(m, i + 1), i);\n\tpoke(m, b2 * x - a2 * y, i + 1);\n\treturn y;\n}\n\n// allpass del 1o ordine del halfband; stato in m[i] (x), m[i+1] (y)\nap(m, i, x, c) {\n\ty = c * (x - peek(m, i + 1)) + peek(m, i);\n\tpoke(m, x, i);\n\tpoke(m, y, i + 1);\n\treturn y;\n}\n\nParam gain(50.0, min=0, max=100);\nParam low(50.0, min=0, max=100);\nParam lowmid(50.0, min=0, max=100);\nParam midhigh(50.0, min=0, max=100);\nParam high(50.0, min=0, max=100);\nParam fader(100.0, min=0, max=100);\nParam incroci(0, min=0, max=4);\nParam curva(0, min=0, max=1);\nParam eqtipo(0, min=0, max=2);\nData st(316);\nData hb(128);\nHistory s_gain(50.0);\nHistory s_low(50.0);\nHistory s_lowmid(50.0);\nHistory s_midhigh(50.0);\nHistory s_high(50.0);\nHistory s_fader(100.0);\nHistory s_x(0);\nHistory s_c(0);\nHistory s_t(0);\n\n// manopole lisciate: 10 ms (selettore 20 ms, dissolvenza A/B)\nt10 = exp(-1 / (0.010 * samplerate));\nt20 = exp(-1 / (0.020 * samplerate));\ns_gain = gain + t10 * (s_gain - gain);\ns_low = low + t10 * (s_low - low);\ns_lowmid = lowmid + t10 * (s_lowmid - lowmid);\ns_midhigh = midhigh + t10 * (s_midhigh - midhigh);\ns_high = high + t10 * (s_high - high);\ns_fader = fader + t10 * (s_fader - fader);\ns_x = incroci + t20 * (s_x - incroci);\ns_c = curva + t20 * (s_c - curva);\ns_t = eqtipo + t20 * (s_t - eqtipo);\n\n// GAIN: fondo corsa muto, meta CCW -100..0 dB, meta CW 0..+10 dB\ntg = s_gain / 100;\ng_gain = pow(10, min(200 * tg - 100, 20 * tg - 10) / 20) * (tg > 0);\n// bande: pot lineare x2, oppure curva Pioneer ideale (docs/09 \u00a77):\n// taglio (2 theta)^1,5, boost uguale; a fondo corsa il contatto da silenzio\nx_low = 2 * s_low / 100;\ng_low = ((1 - s_c) * x_low + s_c * (pow(min(x_low, 1), 1.5) + max(x_low - 1, 0))) * max(low > 0, s_low > 0.001);\nx_lowmid = 2 * s_lowmid / 100;\ng_lowmid = ((1 - s_c) * x_lowmid + s_c * (pow(min(x_lowmid, 1), 1.5) + max(x_lowmid - 1, 0))) * max(lowmid > 0, s_lowmid > 0.001);\nx_midhigh = 2 * s_midhigh / 100;\ng_midhigh = ((1 - s_c) * x_midhigh + s_c * (pow(min(x_midhigh, 1), 1.5) + max(x_midhigh - 1, 0))) * max(midhigh > 0, s_midhigh > 0.001);\nx_high = 2 * s_high / 100;\ng_high = ((1 - s_c) * x_high + s_c * (pow(min(x_high, 1), 1.5) + max(x_high - 1, 0))) * max(high > 0, s_high > 0.001);\n// fader [PROVVISORIO]: curva quadratica, -12 dB a meta corsa\ntf = s_fader / 100;\ng_fader = tf * tf;\n\n// coefficienti degli incroci (bilineare con prewarp)\n// LR4: Q 0,7071 due volte; LR2: Q 0,5 una volta\nsr4 = samplerate * 4;\nA1_k = tan(pi * 150.0 / sr4);\nA1_kk = A1_k * A1_k;\nA1_n = 1 / (1 + A1_k * 1.4142135623730951 + A1_kk);\nA1_a1 = 2 * (A1_kk - 1) * A1_n;\nA1_a2 = (1 - A1_k * 1.4142135623730951 + A1_kk) * A1_n;\nA1_lb = A1_kk * A1_n;\nA2_k = tan(pi * 500.0 / sr4);\nA2_kk = A2_k * A2_k;\nA2_n = 1 / (1 + A2_k * 1.4142135623730951 + A2_kk);\nA2_a1 = 2 * (A2_kk - 1) * A2_n;\nA2_a2 = (1 - A2_k * 1.4142135623730951 + A2_kk) * A2_n;\nA2_lb = A2_kk * A2_n;\nA3_k = tan(pi * 2500.0 / sr4);\nA3_kk = A3_k * A3_k;\nA3_n = 1 / (1 + A3_k * 1.4142135623730951 + A3_kk);\nA3_a1 = 2 * (A3_kk - 1) * A3_n;\nA3_a2 = (1 - A3_k * 1.4142135623730951 + A3_kk) * A3_n;\nA3_lb = A3_kk * A3_n;\nC1_k = tan(pi * 150.0 / sr4);\nC1_kk = C1_k * C1_k;\nC1_n = 1 / (1 + C1_k * 2.0 + C1_kk);\nC1_a1 = 2 * (C1_kk - 1) * C1_n;\nC1_a2 = (1 - C1_k * 2.0 + C1_kk) * C1_n;\nC1_lb = C1_kk * C1_n;\nC2_k = tan(pi * 350.0 / sr4);\nC2_kk = C2_k * C2_k;\nC2_n = 1 / (1 + C2_k * 1.4142135623730951 + C2_kk);\nC2_a1 = 2 * (C2_kk - 1) * C2_n;\nC2_a2 = (1 - C2_k * 1.4142135623730951 + C2_kk) * C2_n;\nC2_lb = C2_kk * C2_n;\nC3_k = tan(pi * 3150.0 / sr4);\nC3_kk = C3_k * C3_k;\nC3_n = 1 / (1 + C3_k * 1.4142135623730951 + C3_kk);\nC3_a1 = 2 * (C3_kk - 1) * C3_n;\nC3_a2 = (1 - C3_k * 1.4142135623730951 + C3_kk) * C3_n;\nC3_lb = C3_kk * C3_n;\nD1_k = tan(pi * 150.0 / sr4);\nD1_kk = D1_k * D1_k;\nD1_n = 1 / (1 + D1_k * 2.0 + D1_kk);\nD1_a1 = 2 * (D1_kk - 1) * D1_n;\nD1_a2 = (1 - D1_k * 2.0 + D1_kk) * D1_n;\nD1_lb = D1_kk * D1_n;\nD2_k = tan(pi * 700.0 / sr4);\nD2_kk = D2_k * D2_k;\nD2_n = 1 / (1 + D2_k * 1.4142135623730951 + D2_kk);\nD2_a1 = 2 * (D2_kk - 1) * D2_n;\nD2_a2 = (1 - D2_k * 1.4142135623730951 + D2_kk) * D2_n;\nD2_lb = D2_kk * D2_n;\nD3_k = tan(pi * 3150.0 / sr4);\nD3_kk = D3_k * D3_k;\nD3_n = 1 / (1 + D3_k * 1.4142135623730951 + D3_kk);\nD3_a1 = 2 * (D3_kk - 1) * D3_n;\nD3_a2 = (1 - D3_k * 1.4142135623730951 + D3_kk) * D3_n;\nD3_lb = D3_kk * D3_n;\nE1_k = tan(pi * 150.0 / sr4);\nE1_kk = E1_k * E1_k;\nE1_n = 1 / (1 + E1_k * 1.4142135623730951 + E1_kk);\nE1_a1 = 2 * (E1_kk - 1) * E1_n;\nE1_a2 = (1 - E1_k * 1.4142135623730951 + E1_kk) * E1_n;\nE1_lb = E1_kk * E1_n;\nE2_k = tan(pi * 400.0 / sr4);\nE2_kk = E2_k * E2_k;\nE2_n = 1 / (1 + E2_k * 1.4142135623730951 + E2_kk);\nE2_a1 = 2 * (E2_kk - 1) * E2_n;\nE2_a2 = (1 - E2_k * 1.4142135623730951 + E2_kk) * E2_n;\nE2_lb = E2_kk * E2_n;\nE3_k = tan(pi * 2500.0 / sr4);\nE3_kk = E3_k * E3_k;\nE3_n = 1 / (1 + E3_k * 1.4142135623730951 + E3_kk);\nE3_a1 = 2 * (E3_kk - 1) * E3_n;\nE3_a2 = (1 - E3_k * 1.4142135623730951 + E3_kk) * E3_n;\nE3_lb = E3_kk * E3_n;\nG1_k = tan(pi * 150.0 / sr4);\nG1_kk = G1_k * G1_k;\nG1_n = 1 / (1 + G1_k * 1.4142135623730951 + G1_kk);\nG1_a1 = 2 * (G1_kk - 1) * G1_n;\nG1_a2 = (1 - G1_k * 1.4142135623730951 + G1_kk) * G1_n;\nG1_lb = G1_kk * G1_n;\nG2_k = tan(pi * 450.0 / sr4);\nG2_kk = G2_k * G2_k;\nG2_n = 1 / (1 + G2_k * 1.4142135623730951 + G2_kk);\nG2_a1 = 2 * (G2_kk - 1) * G2_n;\nG2_a2 = (1 - G2_k * 1.4142135623730951 + G2_kk) * G2_n;\nG2_lb = G2_kk * G2_n;\nG3_k = tan(pi * 2500.0 / sr4);\nG3_kk = G3_k * G3_k;\nG3_n = 1 / (1 + G3_k * 1.4142135623730951 + G3_kk);\nG3_a1 = 2 * (G3_kk - 1) * G3_n;\nG3_a2 = (1 - G3_k * 1.4142135623730951 + G3_kk) * G3_n;\nG3_lb = G3_kk * G3_n;\n\n// EQ DJM (B5, 2026-10-31, djm.py): sul modello del DJM-900NXS\n// (LOW 70 Hz, MID 1 kHz, HI 13 kHz; -26..+6 dB). LOW = scaffale basso,\n// LOW-MID = campana 1 kHz, HIGH = scaffale alto; MID-HIGH non agisce.\n// F = fondo -26 dB, uno scaffale per lato; P = fondo -40 dB, due in fila.\njFl_A = pow(10, 20 * log10(max(g_low, 0.05011872336272722)) / 1 / 40);\njFl_c = cos(2 * pi * 300.0 / sr4);\njFl_ra = 2 * sqrt(jFl_A) * sin(2 * pi * 300.0 / sr4) * 0.7071067811865476;\njFl_ap = jFl_A + 1;\njFl_am = (1) * (jFl_A - 1);\njFl_ai = 1 / (jFl_ap + jFl_am * jFl_c + jFl_ra);\njFl_b0 = jFl_A * (jFl_ap - jFl_am * jFl_c + jFl_ra) * jFl_ai;\njFl_b1 = 2 * jFl_A * (jFl_am - jFl_ap * jFl_c) * jFl_ai;\njFl_b2 = jFl_A * (jFl_ap - jFl_am * jFl_c - jFl_ra) * jFl_ai;\njFl_a1 = -2 * (jFl_am + jFl_ap * jFl_c) * jFl_ai;\njFl_a2 = (jFl_ap + jFl_am * jFl_c - jFl_ra) * jFl_ai;\njFh_A = pow(10, 20 * log10(max(g_high, 0.05011872336272722)) / 1 / 40);\njFh_c = cos(2 * pi * 3600.0 / sr4);\njFh_ra = 2 * sqrt(jFh_A) * sin(2 * pi * 3600.0 / sr4) * 0.7071067811865476;\njFh_ap = jFh_A + 1;\njFh_am = (-1) * (jFh_A - 1);\njFh_ai = 1 / (jFh_ap + jFh_am * jFh_c + jFh_ra);\njFh_b0 = jFh_A * (jFh_ap - jFh_am * jFh_c + jFh_ra) * jFh_ai;\njFh_b1 = 2 * jFh_A * (jFh_am - jFh_ap * jFh_c) * jFh_ai;\njFh_b2 = jFh_A * (jFh_ap - jFh_am * jFh_c - jFh_ra) * jFh_ai;\njFh_a1 = -2 * (jFh_am + jFh_ap * jFh_c) * jFh_ai;\njFh_a2 = (jFh_ap + jFh_am * jFh_c - jFh_ra) * jFh_ai;\njFm_A = pow(10, 20 * log10(max(g_lowmid, 0.05011872336272722)) / 40);\njFm_al = sin(2 * pi * 1000.0 / sr4) / 1.4;\njFm_ai = 1 / (1 + jFm_al / jFm_A);\njFm_b0 = (1 + jFm_al * jFm_A) * jFm_ai;\njFm_a1 = -2 * cos(2 * pi * 1000.0 / sr4) * jFm_ai;\njFm_b2 = (1 - jFm_al * jFm_A) * jFm_ai;\njFm_a2 = (1 - jFm_al / jFm_A) * jFm_ai;\njPl_A = pow(10, 20 * log10(max(g_low, 0.01)) / 2 / 40);\njPl_c = cos(2 * pi * 320.0 / sr4);\njPl_ra = 2 * sqrt(jPl_A) * sin(2 * pi * 320.0 / sr4) * 0.7071067811865476;\njPl_ap = jPl_A + 1;\njPl_am = (1) * (jPl_A - 1);\njPl_ai = 1 / (jPl_ap + jPl_am * jPl_c + jPl_ra);\njPl_b0 = jPl_A * (jPl_ap - jPl_am * jPl_c + jPl_ra) * jPl_ai;\njPl_b1 = 2 * jPl_A * (jPl_am - jPl_ap * jPl_c) * jPl_ai;\njPl_b2 = jPl_A * (jPl_ap - jPl_am * jPl_c - jPl_ra) * jPl_ai;\njPl_a1 = -2 * (jPl_am + jPl_ap * jPl_c) * jPl_ai;\njPl_a2 = (jPl_ap + jPl_am * jPl_c - jPl_ra) * jPl_ai;\njPh_A = pow(10, 20 * log10(max(g_high, 0.01)) / 2 / 40);\njPh_c = cos(2 * pi * 3000.0 / sr4);\njPh_ra = 2 * sqrt(jPh_A) * sin(2 * pi * 3000.0 / sr4) * 0.7071067811865476;\njPh_ap = jPh_A + 1;\njPh_am = (-1) * (jPh_A - 1);\njPh_ai = 1 / (jPh_ap + jPh_am * jPh_c + jPh_ra);\njPh_b0 = jPh_A * (jPh_ap - jPh_am * jPh_c + jPh_ra) * jPh_ai;\njPh_b1 = 2 * jPh_A * (jPh_am - jPh_ap * jPh_c) * jPh_ai;\njPh_b2 = jPh_A * (jPh_ap - jPh_am * jPh_c - jPh_ra) * jPh_ai;\njPh_a1 = -2 * (jPh_am + jPh_ap * jPh_c) * jPh_ai;\njPh_a2 = (jPh_ap + jPh_am * jPh_c - jPh_ra) * jPh_ai;\njPm_A = pow(10, 20 * log10(max(g_lowmid, 0.01)) / 40);\njPm_al = sin(2 * pi * 1000.0 / sr4) / 1.0;\njPm_ai = 1 / (1 + jPm_al / jPm_A);\njPm_b0 = (1 + jPm_al * jPm_A) * jPm_ai;\njPm_a1 = -2 * cos(2 * pi * 1000.0 / sr4) * jPm_ai;\njPm_b2 = (1 - jPm_al * jPm_A) * jPm_ai;\njPm_a2 = (1 - jPm_al / jPm_A) * jPm_ai;\n\n// pesi: dissolvenza fra varianti vicine (1 - |s_x - i|) e fra i tipi di EQ\nw_A = max(0, 1 - abs(s_x - 0)) * max(0, 1 - s_t);\non_A = w_A > 1e-05;\nw_C = max(0, 1 - abs(s_x - 1)) * max(0, 1 - s_t);\non_C = w_C > 1e-05;\nw_D = max(0, 1 - abs(s_x - 2)) * max(0, 1 - s_t);\non_D = w_D > 1e-05;\nw_E = max(0, 1 - abs(s_x - 3)) * max(0, 1 - s_t);\non_E = w_E > 1e-05;\nw_G = max(0, 1 - abs(s_x - 4)) * max(0, 1 - s_t);\non_G = w_G > 1e-05;\nw_F = max(0, 1 - abs(s_t - 1));\non_F = w_F > 1e-05;\nw_P = max(0, 1 - abs(s_t - 2));\non_P = w_P > 1e-05;\n\n// ===== lato L =====\nL_e = in1;\nL_o = in1;\nL_e = ap(hb, 0, L_e, 0.019059005558478156);\nL_e = ap(hb, 4, L_e, 0.1559582483500435);\nL_e = ap(hb, 8, L_e, 0.3650536901969154);\nL_e = ap(hb, 12, L_e, 0.5755010797915323);\nL_e = ap(hb, 16, L_e, 0.7526447471286863);\nL_e = ap(hb, 20, L_e, 0.8980636464339091);\nL_o = ap(hb, 2, L_o, 0.07350243453590219);\nL_o = ap(hb, 6, L_o, 0.25649919975582064);\nL_o = ap(hb, 10, L_o, 0.47327898479453656);\nL_o = ap(hb, 14, L_o, 0.6688095014357188);\nL_o = ap(hb, 18, L_o, 0.8282265929955738);\nL_o = ap(hb, 22, L_o, 0.9656701590349398);\nL_u0 = L_e;\nL_u1 = L_e;\nL_u0 = ap(hb, 24, L_u0, 0.04245470986526787);\nL_u0 = ap(hb, 28, L_u0, 0.39331989319033134);\nL_u1 = ap(hb, 26, L_u1, 0.17073985049750015);\nL_u1 = ap(hb, 30, L_u1, 0.7457135887202412);\nL_u2 = L_o;\nL_u3 = L_o;\nL_u2 = ap(hb, 24, L_u2, 0.04245470986526787);\nL_u2 = ap(hb, 28, L_u2, 0.39331989319033134);\nL_u3 = ap(hb, 26, L_u3, 0.17073985049750015);\nL_u3 = ap(hb, 30, L_u3, 0.7457135887202412);\nL0A = 0;\nif (on_A) {\nL0Al = bq(st, 0, L_u0, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL0Al = bq(st, 2, L0Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL0Al = bq(st, 4, L0Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nL0Al = bq(st, 6, L0Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL0Ah1 = bq(st, 8, L_u0, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL0Ah1 = bq(st, 10, L0Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL0Alm = bq(st, 12, L0Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL0Alm = bq(st, 14, L0Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL0Alm = bq(st, 16, L0Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL0Ah2 = bq(st, 18, L0Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL0Ah2 = bq(st, 20, L0Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL0Amh = bq(st, 22, L0Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL0Amh = bq(st, 24, L0Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL0Ahi = bq(st, 26, L0Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL0Ahi = bq(st, 28, L0Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL0A = g_low * L0Al + g_lowmid * L0Alm + g_midhigh * L0Amh + g_high * L0Ahi;\n}\nL0C = 0;\nif (on_C) {\nL0Cl = bq(st, 30, L_u0, C1_lb, 2 * C1_lb, C1_lb, C1_a1, C1_a2);\nL0Cl = bq(st, 32, L0Cl, C2_a2, C2_a1, 1, C2_a1, C2_a2);\nL0Cl = bq(st, 34, L0Cl, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nL0Ch1 = bq(st, 36, L_u0, C1_n, -2 * C1_n, C1_n, C1_a1, C1_a2);\nL0Ch1 = -L0Ch1;\nL0Clm = bq(st, 38, L0Ch1, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nL0Clm = bq(st, 40, L0Clm, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nL0Clm = bq(st, 42, L0Clm, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nL0Ch2 = bq(st, 44, L0Ch1, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nL0Ch2 = bq(st, 46, L0Ch2, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nL0Cmh = bq(st, 48, L0Ch2, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nL0Cmh = bq(st, 50, L0Cmh, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nL0Chi = bq(st, 52, L0Ch2, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nL0Chi = bq(st, 54, L0Chi, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nL0C = g_low * L0Cl + g_lowmid * L0Clm + g_midhigh * L0Cmh + g_high * L0Chi;\n}\nL0D = 0;\nif (on_D) {\nL0Dl = bq(st, 56, L_u0, D1_lb, 2 * D1_lb, D1_lb, D1_a1, D1_a2);\nL0Dl = bq(st, 58, L0Dl, D2_a2, D2_a1, 1, D2_a1, D2_a2);\nL0Dl = bq(st, 60, L0Dl, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nL0Dh1 = bq(st, 62, L_u0, D1_n, -2 * D1_n, D1_n, D1_a1, D1_a2);\nL0Dh1 = -L0Dh1;\nL0Dlm = bq(st, 64, L0Dh1, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nL0Dlm = bq(st, 66, L0Dlm, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nL0Dlm = bq(st, 68, L0Dlm, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nL0Dh2 = bq(st, 70, L0Dh1, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nL0Dh2 = bq(st, 72, L0Dh2, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nL0Dmh = bq(st, 74, L0Dh2, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nL0Dmh = bq(st, 76, L0Dmh, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nL0Dhi = bq(st, 78, L0Dh2, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nL0Dhi = bq(st, 80, L0Dhi, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nL0D = g_low * L0Dl + g_lowmid * L0Dlm + g_midhigh * L0Dmh + g_high * L0Dhi;\n}\nL0E = 0;\nif (on_E) {\nL0El = bq(st, 82, L_u0, E1_lb, 2 * E1_lb, E1_lb, E1_a1, E1_a2);\nL0El = bq(st, 84, L0El, E1_lb, 2 * E1_lb, E1_lb, E1_a1, E1_a2);\nL0El = bq(st, 86, L0El, E2_a2, E2_a1, 1, E2_a1, E2_a2);\nL0El = bq(st, 88, L0El, E3_a2, E3_a1, 1, E3_a1, E3_a2);\nL0Eh1 = bq(st, 90, L_u0, E1_n, -2 * E1_n, E1_n, E1_a1, E1_a2);\nL0Eh1 = bq(st, 92, L0Eh1, E1_n, -2 * E1_n, E1_n, E1_a1, E1_a2);\nL0Elm = bq(st, 94, L0Eh1, E2_lb, 2 * E2_lb, E2_lb, E2_a1, E2_a2);\nL0Elm = bq(st, 96, L0Elm, E2_lb, 2 * E2_lb, E2_lb, E2_a1, E2_a2);\nL0Elm = bq(st, 98, L0Elm, E3_a2, E3_a1, 1, E3_a1, E3_a2);\nL0Eh2 = bq(st, 100, L0Eh1, E2_n, -2 * E2_n, E2_n, E2_a1, E2_a2);\nL0Eh2 = bq(st, 102, L0Eh2, E2_n, -2 * E2_n, E2_n, E2_a1, E2_a2);\nL0Emh = bq(st, 104, L0Eh2, E3_lb, 2 * E3_lb, E3_lb, E3_a1, E3_a2);\nL0Emh = bq(st, 106, L0Emh, E3_lb, 2 * E3_lb, E3_lb, E3_a1, E3_a2);\nL0Ehi = bq(st, 108, L0Eh2, E3_n, -2 * E3_n, E3_n, E3_a1, E3_a2);\nL0Ehi = bq(st, 110, L0Ehi, E3_n, -2 * E3_n, E3_n, E3_a1, E3_a2);\nL0E = g_low * L0El + g_lowmid * L0Elm + g_midhigh * L0Emh + g_high * L0Ehi;\n}\nL0G = 0;\nif (on_G) {\nL0Gl = bq(st, 112, L_u0, G1_lb, 2 * G1_lb, G1_lb, G1_a1, G1_a2);\nL0Gl = bq(st, 114, L0Gl, G1_lb, 2 * G1_lb, G1_lb, G1_a1, G1_a2);\nL0Gl = bq(st, 116, L0Gl, G2_a2, G2_a1, 1, G2_a1, G2_a2);\nL0Gl = bq(st, 118, L0Gl, G3_a2, G3_a1, 1, G3_a1, G3_a2);\nL0Gh1 = bq(st, 120, L_u0, G1_n, -2 * G1_n, G1_n, G1_a1, G1_a2);\nL0Gh1 = bq(st, 122, L0Gh1, G1_n, -2 * G1_n, G1_n, G1_a1, G1_a2);\nL0Glm = bq(st, 124, L0Gh1, G2_lb, 2 * G2_lb, G2_lb, G2_a1, G2_a2);\nL0Glm = bq(st, 126, L0Glm, G2_lb, 2 * G2_lb, G2_lb, G2_a1, G2_a2);\nL0Glm = bq(st, 128, L0Glm, G3_a2, G3_a1, 1, G3_a1, G3_a2);\nL0Gh2 = bq(st, 130, L0Gh1, G2_n, -2 * G2_n, G2_n, G2_a1, G2_a2);\nL0Gh2 = bq(st, 132, L0Gh2, G2_n, -2 * G2_n, G2_n, G2_a1, G2_a2);\nL0Gmh = bq(st, 134, L0Gh2, G3_lb, 2 * G3_lb, G3_lb, G3_a1, G3_a2);\nL0Gmh = bq(st, 136, L0Gmh, G3_lb, 2 * G3_lb, G3_lb, G3_a1, G3_a2);\nL0Ghi = bq(st, 138, L0Gh2, G3_n, -2 * G3_n, G3_n, G3_a1, G3_a2);\nL0Ghi = bq(st, 140, L0Ghi, G3_n, -2 * G3_n, G3_n, G3_a1, G3_a2);\nL0G = g_low * L0Gl + g_lowmid * L0Glm + g_midhigh * L0Gmh + g_high * L0Ghi;\n}\nL0jF = 0;\nif (on_F) {\nL0jF = L_u0;\nL0jF = bq(st, 142, L0jF, jFl_b0, jFl_b1, jFl_b2, jFl_a1, jFl_a2);\nL0jF = bq(st, 144, L0jF, jFm_b0, jFm_a1, jFm_b2, jFm_a1, jFm_a2);\nL0jF = bq(st, 146, L0jF, jFh_b0, jFh_b1, jFh_b2, jFh_a1, jFh_a2);\n}\nL0jP = 0;\nif (on_P) {\nL0jP = L_u0;\nL0jP = bq(st, 148, L0jP, jPl_b0, jPl_b1, jPl_b2, jPl_a1, jPl_a2);\nL0jP = bq(st, 150, L0jP, jPl_b0, jPl_b1, jPl_b2, jPl_a1, jPl_a2);\nL0jP = bq(st, 152, L0jP, jPm_b0, jPm_a1, jPm_b2, jPm_a1, jPm_a2);\nL0jP = bq(st, 154, L0jP, jPh_b0, jPh_b1, jPh_b2, jPh_a1, jPh_a2);\nL0jP = bq(st, 156, L0jP, jPh_b0, jPh_b1, jPh_b2, jPh_a1, jPh_a2);\n}\nL_y0 = w_A * L0A + w_C * L0C + w_D * L0D + w_E * L0E + w_G * L0G + w_F * L0jF + w_P * L0jP;\nL1A = 0;\nif (on_A) {\nL1Al = bq(st, 0, L_u1, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL1Al = bq(st, 2, L1Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL1Al = bq(st, 4, L1Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nL1Al = bq(st, 6, L1Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL1Ah1 = bq(st, 8, L_u1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL1Ah1 = bq(st, 10, L1Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL1Alm = bq(st, 12, L1Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL1Alm = bq(st, 14, L1Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL1Alm = bq(st, 16, L1Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL1Ah2 = bq(st, 18, L1Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL1Ah2 = bq(st, 20, L1Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL1Amh = bq(st, 22, L1Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL1Amh = bq(st, 24, L1Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL1Ahi = bq(st, 26, L1Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL1Ahi = bq(st, 28, L1Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL1A = g_low * L1Al + g_lowmid * L1Alm + g_midhigh * L1Amh + g_high * L1Ahi;\n}\nL1C = 0;\nif (on_C) {\nL1Cl = bq(st, 30, L_u1, C1_lb, 2 * C1_lb, C1_lb, C1_a1, C1_a2);\nL1Cl = bq(st, 32, L1Cl, C2_a2, C2_a1, 1, C2_a1, C2_a2);\nL1Cl = bq(st, 34, L1Cl, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nL1Ch1 = bq(st, 36, L_u1, C1_n, -2 * C1_n, C1_n, C1_a1, C1_a2);\nL1Ch1 = -L1Ch1;\nL1Clm = bq(st, 38, L1Ch1, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nL1Clm = bq(st, 40, L1Clm, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nL1Clm = bq(st, 42, L1Clm, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nL1Ch2 = bq(st, 44, L1Ch1, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nL1Ch2 = bq(st, 46, L1Ch2, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nL1Cmh = bq(st, 48, L1Ch2, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nL1Cmh = bq(st, 50, L1Cmh, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nL1Chi = bq(st, 52, L1Ch2, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nL1Chi = bq(st, 54, L1Chi, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nL1C = g_low * L1Cl + g_lowmid * L1Clm + g_midhigh * L1Cmh + g_high * L1Chi;\n}\nL1D = 0;\nif (on_D) {\nL1Dl = bq(st, 56, L_u1, D1_lb, 2 * D1_lb, D1_lb, D1_a1, D1_a2);\nL1Dl = bq(st, 58, L1Dl, D2_a2, D2_a1, 1, D2_a1, D2_a2);\nL1Dl = bq(st, 60, L1Dl, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nL1Dh1 = bq(st, 62, L_u1, D1_n, -2 * D1_n, D1_n, D1_a1, D1_a2);\nL1Dh1 = -L1Dh1;\nL1Dlm = bq(st, 64, L1Dh1, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nL1Dlm = bq(st, 66, L1Dlm, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nL1Dlm = bq(st, 68, L1Dlm, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nL1Dh2 = bq(st, 70, L1Dh1, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nL1Dh2 = bq(st, 72, L1Dh2, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nL1Dmh = bq(st, 74, L1Dh2, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nL1Dmh = bq(st, 76, L1Dmh, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nL1Dhi = bq(st, 78, L1Dh2, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nL1Dhi = bq(st, 80, L1Dhi, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nL1D = g_low * L1Dl + g_lowmid * L1Dlm + g_midhigh * L1Dmh + g_high * L1Dhi;\n}\nL1E = 0;\nif (on_E) {\nL1El = bq(st, 82, L_u1, E1_lb, 2 * E1_lb, E1_lb, E1_a1, E1_a2);\nL1El = bq(st, 84, L1El, E1_lb, 2 * E1_lb, E1_lb, E1_a1, E1_a2);\nL1El = bq(st, 86, L1El, E2_a2, E2_a1, 1, E2_a1, E2_a2);\nL1El = bq(st, 88, L1El, E3_a2, E3_a1, 1, E3_a1, E3_a2);\nL1Eh1 = bq(st, 90, L_u1, E1_n, -2 * E1_n, E1_n, E1_a1, E1_a2);\nL1Eh1 = bq(st, 92, L1Eh1, E1_n, -2 * E1_n, E1_n, E1_a1, E1_a2);\nL1Elm = bq(st, 94, L1Eh1, E2_lb, 2 * E2_lb, E2_lb, E2_a1, E2_a2);\nL1Elm = bq(st, 96, L1Elm, E2_lb, 2 * E2_lb, E2_lb, E2_a1, E2_a2);\nL1Elm = bq(st, 98, L1Elm, E3_a2, E3_a1, 1, E3_a1, E3_a2);\nL1Eh2 = bq(st, 100, L1Eh1, E2_n, -2 * E2_n, E2_n, E2_a1, E2_a2);\nL1Eh2 = bq(st, 102, L1Eh2, E2_n, -2 * E2_n, E2_n, E2_a1, E2_a2);\nL1Emh = bq(st, 104, L1Eh2, E3_lb, 2 * E3_lb, E3_lb, E3_a1, E3_a2);\nL1Emh = bq(st, 106, L1Emh, E3_lb, 2 * E3_lb, E3_lb, E3_a1, E3_a2);\nL1Ehi = bq(st, 108, L1Eh2, E3_n, -2 * E3_n, E3_n, E3_a1, E3_a2);\nL1Ehi = bq(st, 110, L1Ehi, E3_n, -2 * E3_n, E3_n, E3_a1, E3_a2);\nL1E = g_low * L1El + g_lowmid * L1Elm + g_midhigh * L1Emh + g_high * L1Ehi;\n}\nL1G = 0;\nif (on_G) {\nL1Gl = bq(st, 112, L_u1, G1_lb, 2 * G1_lb, G1_lb, G1_a1, G1_a2);\nL1Gl = bq(st, 114, L1Gl, G1_lb, 2 * G1_lb, G1_lb, G1_a1, G1_a2);\nL1Gl = bq(st, 116, L1Gl, G2_a2, G2_a1, 1, G2_a1, G2_a2);\nL1Gl = bq(st, 118, L1Gl, G3_a2, G3_a1, 1, G3_a1, G3_a2);\nL1Gh1 = bq(st, 120, L_u1, G1_n, -2 * G1_n, G1_n, G1_a1, G1_a2);\nL1Gh1 = bq(st, 122, L1Gh1, G1_n, -2 * G1_n, G1_n, G1_a1, G1_a2);\nL1Glm = bq(st, 124, L1Gh1, G2_lb, 2 * G2_lb, G2_lb, G2_a1, G2_a2);\nL1Glm = bq(st, 126, L1Glm, G2_lb, 2 * G2_lb, G2_lb, G2_a1, G2_a2);\nL1Glm = bq(st, 128, L1Glm, G3_a2, G3_a1, 1, G3_a1, G3_a2);\nL1Gh2 = bq(st, 130, L1Gh1, G2_n, -2 * G2_n, G2_n, G2_a1, G2_a2);\nL1Gh2 = bq(st, 132, L1Gh2, G2_n, -2 * G2_n, G2_n, G2_a1, G2_a2);\nL1Gmh = bq(st, 134, L1Gh2, G3_lb, 2 * G3_lb, G3_lb, G3_a1, G3_a2);\nL1Gmh = bq(st, 136, L1Gmh, G3_lb, 2 * G3_lb, G3_lb, G3_a1, G3_a2);\nL1Ghi = bq(st, 138, L1Gh2, G3_n, -2 * G3_n, G3_n, G3_a1, G3_a2);\nL1Ghi = bq(st, 140, L1Ghi, G3_n, -2 * G3_n, G3_n, G3_a1, G3_a2);\nL1G = g_low * L1Gl + g_lowmid * L1Glm + g_midhigh * L1Gmh + g_high * L1Ghi;\n}\nL1jF = 0;\nif (on_F) {\nL1jF = L_u1;\nL1jF = bq(st, 142, L1jF, jFl_b0, jFl_b1, jFl_b2, jFl_a1, jFl_a2);\nL1jF = bq(st, 144, L1jF, jFm_b0, jFm_a1, jFm_b2, jFm_a1, jFm_a2);\nL1jF = bq(st, 146, L1jF, jFh_b0, jFh_b1, jFh_b2, jFh_a1, jFh_a2);\n}\nL1jP = 0;\nif (on_P) {\nL1jP = L_u1;\nL1jP = bq(st, 148, L1jP, jPl_b0, jPl_b1, jPl_b2, jPl_a1, jPl_a2);\nL1jP = bq(st, 150, L1jP, jPl_b0, jPl_b1, jPl_b2, jPl_a1, jPl_a2);\nL1jP = bq(st, 152, L1jP, jPm_b0, jPm_a1, jPm_b2, jPm_a1, jPm_a2);\nL1jP = bq(st, 154, L1jP, jPh_b0, jPh_b1, jPh_b2, jPh_a1, jPh_a2);\nL1jP = bq(st, 156, L1jP, jPh_b0, jPh_b1, jPh_b2, jPh_a1, jPh_a2);\n}\nL_y1 = w_A * L1A + w_C * L1C + w_D * L1D + w_E * L1E + w_G * L1G + w_F * L1jF + w_P * L1jP;\nL2A = 0;\nif (on_A) {\nL2Al = bq(st, 0, L_u2, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL2Al = bq(st, 2, L2Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL2Al = bq(st, 4, L2Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nL2Al = bq(st, 6, L2Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL2Ah1 = bq(st, 8, L_u2, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL2Ah1 = bq(st, 10, L2Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL2Alm = bq(st, 12, L2Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL2Alm = bq(st, 14, L2Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL2Alm = bq(st, 16, L2Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL2Ah2 = bq(st, 18, L2Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL2Ah2 = bq(st, 20, L2Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL2Amh = bq(st, 22, L2Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL2Amh = bq(st, 24, L2Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL2Ahi = bq(st, 26, L2Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL2Ahi = bq(st, 28, L2Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL2A = g_low * L2Al + g_lowmid * L2Alm + g_midhigh * L2Amh + g_high * L2Ahi;\n}\nL2C = 0;\nif (on_C) {\nL2Cl = bq(st, 30, L_u2, C1_lb, 2 * C1_lb, C1_lb, C1_a1, C1_a2);\nL2Cl = bq(st, 32, L2Cl, C2_a2, C2_a1, 1, C2_a1, C2_a2);\nL2Cl = bq(st, 34, L2Cl, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nL2Ch1 = bq(st, 36, L_u2, C1_n, -2 * C1_n, C1_n, C1_a1, C1_a2);\nL2Ch1 = -L2Ch1;\nL2Clm = bq(st, 38, L2Ch1, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nL2Clm = bq(st, 40, L2Clm, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nL2Clm = bq(st, 42, L2Clm, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nL2Ch2 = bq(st, 44, L2Ch1, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nL2Ch2 = bq(st, 46, L2Ch2, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nL2Cmh = bq(st, 48, L2Ch2, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nL2Cmh = bq(st, 50, L2Cmh, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nL2Chi = bq(st, 52, L2Ch2, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nL2Chi = bq(st, 54, L2Chi, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nL2C = g_low * L2Cl + g_lowmid * L2Clm + g_midhigh * L2Cmh + g_high * L2Chi;\n}\nL2D = 0;\nif (on_D) {\nL2Dl = bq(st, 56, L_u2, D1_lb, 2 * D1_lb, D1_lb, D1_a1, D1_a2);\nL2Dl = bq(st, 58, L2Dl, D2_a2, D2_a1, 1, D2_a1, D2_a2);\nL2Dl = bq(st, 60, L2Dl, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nL2Dh1 = bq(st, 62, L_u2, D1_n, -2 * D1_n, D1_n, D1_a1, D1_a2);\nL2Dh1 = -L2Dh1;\nL2Dlm = bq(st, 64, L2Dh1, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nL2Dlm = bq(st, 66, L2Dlm, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nL2Dlm = bq(st, 68, L2Dlm, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nL2Dh2 = bq(st, 70, L2Dh1, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nL2Dh2 = bq(st, 72, L2Dh2, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nL2Dmh = bq(st, 74, L2Dh2, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nL2Dmh = bq(st, 76, L2Dmh, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nL2Dhi = bq(st, 78, L2Dh2, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nL2Dhi = bq(st, 80, L2Dhi, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nL2D = g_low * L2Dl + g_lowmid * L2Dlm + g_midhigh * L2Dmh + g_high * L2Dhi;\n}\nL2E = 0;\nif (on_E) {\nL2El = bq(st, 82, L_u2, E1_lb, 2 * E1_lb, E1_lb, E1_a1, E1_a2);\nL2El = bq(st, 84, L2El, E1_lb, 2 * E1_lb, E1_lb, E1_a1, E1_a2);\nL2El = bq(st, 86, L2El, E2_a2, E2_a1, 1, E2_a1, E2_a2);\nL2El = bq(st, 88, L2El, E3_a2, E3_a1, 1, E3_a1, E3_a2);\nL2Eh1 = bq(st, 90, L_u2, E1_n, -2 * E1_n, E1_n, E1_a1, E1_a2);\nL2Eh1 = bq(st, 92, L2Eh1, E1_n, -2 * E1_n, E1_n, E1_a1, E1_a2);\nL2Elm = bq(st, 94, L2Eh1, E2_lb, 2 * E2_lb, E2_lb, E2_a1, E2_a2);\nL2Elm = bq(st, 96, L2Elm, E2_lb, 2 * E2_lb, E2_lb, E2_a1, E2_a2);\nL2Elm = bq(st, 98, L2Elm, E3_a2, E3_a1, 1, E3_a1, E3_a2);\nL2Eh2 = bq(st, 100, L2Eh1, E2_n, -2 * E2_n, E2_n, E2_a1, E2_a2);\nL2Eh2 = bq(st, 102, L2Eh2, E2_n, -2 * E2_n, E2_n, E2_a1, E2_a2);\nL2Emh = bq(st, 104, L2Eh2, E3_lb, 2 * E3_lb, E3_lb, E3_a1, E3_a2);\nL2Emh = bq(st, 106, L2Emh, E3_lb, 2 * E3_lb, E3_lb, E3_a1, E3_a2);\nL2Ehi = bq(st, 108, L2Eh2, E3_n, -2 * E3_n, E3_n, E3_a1, E3_a2);\nL2Ehi = bq(st, 110, L2Ehi, E3_n, -2 * E3_n, E3_n, E3_a1, E3_a2);\nL2E = g_low * L2El + g_lowmid * L2Elm + g_midhigh * L2Emh + g_high * L2Ehi;\n}\nL2G = 0;\nif (on_G) {\nL2Gl = bq(st, 112, L_u2, G1_lb, 2 * G1_lb, G1_lb, G1_a1, G1_a2);\nL2Gl = bq(st, 114, L2Gl, G1_lb, 2 * G1_lb, G1_lb, G1_a1, G1_a2);\nL2Gl = bq(st, 116, L2Gl, G2_a2, G2_a1, 1, G2_a1, G2_a2);\nL2Gl = bq(st, 118, L2Gl, G3_a2, G3_a1, 1, G3_a1, G3_a2);\nL2Gh1 = bq(st, 120, L_u2, G1_n, -2 * G1_n, G1_n, G1_a1, G1_a2);\nL2Gh1 = bq(st, 122, L2Gh1, G1_n, -2 * G1_n, G1_n, G1_a1, G1_a2);\nL2Glm = bq(st, 124, L2Gh1, G2_lb, 2 * G2_lb, G2_lb, G2_a1, G2_a2);\nL2Glm = bq(st, 126, L2Glm, G2_lb, 2 * G2_lb, G2_lb, G2_a1, G2_a2);\nL2Glm = bq(st, 128, L2Glm, G3_a2, G3_a1, 1, G3_a1, G3_a2);\nL2Gh2 = bq(st, 130, L2Gh1, G2_n, -2 * G2_n, G2_n, G2_a1, G2_a2);\nL2Gh2 = bq(st, 132, L2Gh2, G2_n, -2 * G2_n, G2_n, G2_a1, G2_a2);\nL2Gmh = bq(st, 134, L2Gh2, G3_lb, 2 * G3_lb, G3_lb, G3_a1, G3_a2);\nL2Gmh = bq(st, 136, L2Gmh, G3_lb, 2 * G3_lb, G3_lb, G3_a1, G3_a2);\nL2Ghi = bq(st, 138, L2Gh2, G3_n, -2 * G3_n, G3_n, G3_a1, G3_a2);\nL2Ghi = bq(st, 140, L2Ghi, G3_n, -2 * G3_n, G3_n, G3_a1, G3_a2);\nL2G = g_low * L2Gl + g_lowmid * L2Glm + g_midhigh * L2Gmh + g_high * L2Ghi;\n}\nL2jF = 0;\nif (on_F) {\nL2jF = L_u2;\nL2jF = bq(st, 142, L2jF, jFl_b0, jFl_b1, jFl_b2, jFl_a1, jFl_a2);\nL2jF = bq(st, 144, L2jF, jFm_b0, jFm_a1, jFm_b2, jFm_a1, jFm_a2);\nL2jF = bq(st, 146, L2jF, jFh_b0, jFh_b1, jFh_b2, jFh_a1, jFh_a2);\n}\nL2jP = 0;\nif (on_P) {\nL2jP = L_u2;\nL2jP = bq(st, 148, L2jP, jPl_b0, jPl_b1, jPl_b2, jPl_a1, jPl_a2);\nL2jP = bq(st, 150, L2jP, jPl_b0, jPl_b1, jPl_b2, jPl_a1, jPl_a2);\nL2jP = bq(st, 152, L2jP, jPm_b0, jPm_a1, jPm_b2, jPm_a1, jPm_a2);\nL2jP = bq(st, 154, L2jP, jPh_b0, jPh_b1, jPh_b2, jPh_a1, jPh_a2);\nL2jP = bq(st, 156, L2jP, jPh_b0, jPh_b1, jPh_b2, jPh_a1, jPh_a2);\n}\nL_y2 = w_A * L2A + w_C * L2C + w_D * L2D + w_E * L2E + w_G * L2G + w_F * L2jF + w_P * L2jP;\nL3A = 0;\nif (on_A) {\nL3Al = bq(st, 0, L_u3, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL3Al = bq(st, 2, L3Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nL3Al = bq(st, 4, L3Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nL3Al = bq(st, 6, L3Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL3Ah1 = bq(st, 8, L_u3, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL3Ah1 = bq(st, 10, L3Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nL3Alm = bq(st, 12, L3Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL3Alm = bq(st, 14, L3Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nL3Alm = bq(st, 16, L3Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nL3Ah2 = bq(st, 18, L3Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL3Ah2 = bq(st, 20, L3Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nL3Amh = bq(st, 22, L3Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL3Amh = bq(st, 24, L3Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nL3Ahi = bq(st, 26, L3Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL3Ahi = bq(st, 28, L3Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nL3A = g_low * L3Al + g_lowmid * L3Alm + g_midhigh * L3Amh + g_high * L3Ahi;\n}\nL3C = 0;\nif (on_C) {\nL3Cl = bq(st, 30, L_u3, C1_lb, 2 * C1_lb, C1_lb, C1_a1, C1_a2);\nL3Cl = bq(st, 32, L3Cl, C2_a2, C2_a1, 1, C2_a1, C2_a2);\nL3Cl = bq(st, 34, L3Cl, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nL3Ch1 = bq(st, 36, L_u3, C1_n, -2 * C1_n, C1_n, C1_a1, C1_a2);\nL3Ch1 = -L3Ch1;\nL3Clm = bq(st, 38, L3Ch1, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nL3Clm = bq(st, 40, L3Clm, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nL3Clm = bq(st, 42, L3Clm, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nL3Ch2 = bq(st, 44, L3Ch1, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nL3Ch2 = bq(st, 46, L3Ch2, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nL3Cmh = bq(st, 48, L3Ch2, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nL3Cmh = bq(st, 50, L3Cmh, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nL3Chi = bq(st, 52, L3Ch2, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nL3Chi = bq(st, 54, L3Chi, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nL3C = g_low * L3Cl + g_lowmid * L3Clm + g_midhigh * L3Cmh + g_high * L3Chi;\n}\nL3D = 0;\nif (on_D) {\nL3Dl = bq(st, 56, L_u3, D1_lb, 2 * D1_lb, D1_lb, D1_a1, D1_a2);\nL3Dl = bq(st, 58, L3Dl, D2_a2, D2_a1, 1, D2_a1, D2_a2);\nL3Dl = bq(st, 60, L3Dl, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nL3Dh1 = bq(st, 62, L_u3, D1_n, -2 * D1_n, D1_n, D1_a1, D1_a2);\nL3Dh1 = -L3Dh1;\nL3Dlm = bq(st, 64, L3Dh1, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nL3Dlm = bq(st, 66, L3Dlm, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nL3Dlm = bq(st, 68, L3Dlm, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nL3Dh2 = bq(st, 70, L3Dh1, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nL3Dh2 = bq(st, 72, L3Dh2, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nL3Dmh = bq(st, 74, L3Dh2, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nL3Dmh = bq(st, 76, L3Dmh, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nL3Dhi = bq(st, 78, L3Dh2, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nL3Dhi = bq(st, 80, L3Dhi, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nL3D = g_low * L3Dl + g_lowmid * L3Dlm + g_midhigh * L3Dmh + g_high * L3Dhi;\n}\nL3E = 0;\nif (on_E) {\nL3El = bq(st, 82, L_u3, E1_lb, 2 * E1_lb, E1_lb, E1_a1, E1_a2);\nL3El = bq(st, 84, L3El, E1_lb, 2 * E1_lb, E1_lb, E1_a1, E1_a2);\nL3El = bq(st, 86, L3El, E2_a2, E2_a1, 1, E2_a1, E2_a2);\nL3El = bq(st, 88, L3El, E3_a2, E3_a1, 1, E3_a1, E3_a2);\nL3Eh1 = bq(st, 90, L_u3, E1_n, -2 * E1_n, E1_n, E1_a1, E1_a2);\nL3Eh1 = bq(st, 92, L3Eh1, E1_n, -2 * E1_n, E1_n, E1_a1, E1_a2);\nL3Elm = bq(st, 94, L3Eh1, E2_lb, 2 * E2_lb, E2_lb, E2_a1, E2_a2);\nL3Elm = bq(st, 96, L3Elm, E2_lb, 2 * E2_lb, E2_lb, E2_a1, E2_a2);\nL3Elm = bq(st, 98, L3Elm, E3_a2, E3_a1, 1, E3_a1, E3_a2);\nL3Eh2 = bq(st, 100, L3Eh1, E2_n, -2 * E2_n, E2_n, E2_a1, E2_a2);\nL3Eh2 = bq(st, 102, L3Eh2, E2_n, -2 * E2_n, E2_n, E2_a1, E2_a2);\nL3Emh = bq(st, 104, L3Eh2, E3_lb, 2 * E3_lb, E3_lb, E3_a1, E3_a2);\nL3Emh = bq(st, 106, L3Emh, E3_lb, 2 * E3_lb, E3_lb, E3_a1, E3_a2);\nL3Ehi = bq(st, 108, L3Eh2, E3_n, -2 * E3_n, E3_n, E3_a1, E3_a2);\nL3Ehi = bq(st, 110, L3Ehi, E3_n, -2 * E3_n, E3_n, E3_a1, E3_a2);\nL3E = g_low * L3El + g_lowmid * L3Elm + g_midhigh * L3Emh + g_high * L3Ehi;\n}\nL3G = 0;\nif (on_G) {\nL3Gl = bq(st, 112, L_u3, G1_lb, 2 * G1_lb, G1_lb, G1_a1, G1_a2);\nL3Gl = bq(st, 114, L3Gl, G1_lb, 2 * G1_lb, G1_lb, G1_a1, G1_a2);\nL3Gl = bq(st, 116, L3Gl, G2_a2, G2_a1, 1, G2_a1, G2_a2);\nL3Gl = bq(st, 118, L3Gl, G3_a2, G3_a1, 1, G3_a1, G3_a2);\nL3Gh1 = bq(st, 120, L_u3, G1_n, -2 * G1_n, G1_n, G1_a1, G1_a2);\nL3Gh1 = bq(st, 122, L3Gh1, G1_n, -2 * G1_n, G1_n, G1_a1, G1_a2);\nL3Glm = bq(st, 124, L3Gh1, G2_lb, 2 * G2_lb, G2_lb, G2_a1, G2_a2);\nL3Glm = bq(st, 126, L3Glm, G2_lb, 2 * G2_lb, G2_lb, G2_a1, G2_a2);\nL3Glm = bq(st, 128, L3Glm, G3_a2, G3_a1, 1, G3_a1, G3_a2);\nL3Gh2 = bq(st, 130, L3Gh1, G2_n, -2 * G2_n, G2_n, G2_a1, G2_a2);\nL3Gh2 = bq(st, 132, L3Gh2, G2_n, -2 * G2_n, G2_n, G2_a1, G2_a2);\nL3Gmh = bq(st, 134, L3Gh2, G3_lb, 2 * G3_lb, G3_lb, G3_a1, G3_a2);\nL3Gmh = bq(st, 136, L3Gmh, G3_lb, 2 * G3_lb, G3_lb, G3_a1, G3_a2);\nL3Ghi = bq(st, 138, L3Gh2, G3_n, -2 * G3_n, G3_n, G3_a1, G3_a2);\nL3Ghi = bq(st, 140, L3Ghi, G3_n, -2 * G3_n, G3_n, G3_a1, G3_a2);\nL3G = g_low * L3Gl + g_lowmid * L3Glm + g_midhigh * L3Gmh + g_high * L3Ghi;\n}\nL3jF = 0;\nif (on_F) {\nL3jF = L_u3;\nL3jF = bq(st, 142, L3jF, jFl_b0, jFl_b1, jFl_b2, jFl_a1, jFl_a2);\nL3jF = bq(st, 144, L3jF, jFm_b0, jFm_a1, jFm_b2, jFm_a1, jFm_a2);\nL3jF = bq(st, 146, L3jF, jFh_b0, jFh_b1, jFh_b2, jFh_a1, jFh_a2);\n}\nL3jP = 0;\nif (on_P) {\nL3jP = L_u3;\nL3jP = bq(st, 148, L3jP, jPl_b0, jPl_b1, jPl_b2, jPl_a1, jPl_a2);\nL3jP = bq(st, 150, L3jP, jPl_b0, jPl_b1, jPl_b2, jPl_a1, jPl_a2);\nL3jP = bq(st, 152, L3jP, jPm_b0, jPm_a1, jPm_b2, jPm_a1, jPm_a2);\nL3jP = bq(st, 154, L3jP, jPh_b0, jPh_b1, jPh_b2, jPh_a1, jPh_a2);\nL3jP = bq(st, 156, L3jP, jPh_b0, jPh_b1, jPh_b2, jPh_a1, jPh_a2);\n}\nL_y3 = w_A * L3A + w_C * L3C + w_D * L3D + w_E * L3E + w_G * L3G + w_F * L3jF + w_P * L3jP;\nif (on_A == 0) {\npoke(st, 0, 0);\npoke(st, 0, 1);\npoke(st, 0, 2);\npoke(st, 0, 3);\npoke(st, 0, 4);\npoke(st, 0, 5);\npoke(st, 0, 6);\npoke(st, 0, 7);\npoke(st, 0, 8);\npoke(st, 0, 9);\npoke(st, 0, 10);\npoke(st, 0, 11);\npoke(st, 0, 12);\npoke(st, 0, 13);\npoke(st, 0, 14);\npoke(st, 0, 15);\npoke(st, 0, 16);\npoke(st, 0, 17);\npoke(st, 0, 18);\npoke(st, 0, 19);\npoke(st, 0, 20);\npoke(st, 0, 21);\npoke(st, 0, 22);\npoke(st, 0, 23);\npoke(st, 0, 24);\npoke(st, 0, 25);\npoke(st, 0, 26);\npoke(st, 0, 27);\npoke(st, 0, 28);\npoke(st, 0, 29);\n}\nif (on_C == 0) {\npoke(st, 0, 30);\npoke(st, 0, 31);\npoke(st, 0, 32);\npoke(st, 0, 33);\npoke(st, 0, 34);\npoke(st, 0, 35);\npoke(st, 0, 36);\npoke(st, 0, 37);\npoke(st, 0, 38);\npoke(st, 0, 39);\npoke(st, 0, 40);\npoke(st, 0, 41);\npoke(st, 0, 42);\npoke(st, 0, 43);\npoke(st, 0, 44);\npoke(st, 0, 45);\npoke(st, 0, 46);\npoke(st, 0, 47);\npoke(st, 0, 48);\npoke(st, 0, 49);\npoke(st, 0, 50);\npoke(st, 0, 51);\npoke(st, 0, 52);\npoke(st, 0, 53);\npoke(st, 0, 54);\npoke(st, 0, 55);\n}\nif (on_D == 0) {\npoke(st, 0, 56);\npoke(st, 0, 57);\npoke(st, 0, 58);\npoke(st, 0, 59);\npoke(st, 0, 60);\npoke(st, 0, 61);\npoke(st, 0, 62);\npoke(st, 0, 63);\npoke(st, 0, 64);\npoke(st, 0, 65);\npoke(st, 0, 66);\npoke(st, 0, 67);\npoke(st, 0, 68);\npoke(st, 0, 69);\npoke(st, 0, 70);\npoke(st, 0, 71);\npoke(st, 0, 72);\npoke(st, 0, 73);\npoke(st, 0, 74);\npoke(st, 0, 75);\npoke(st, 0, 76);\npoke(st, 0, 77);\npoke(st, 0, 78);\npoke(st, 0, 79);\npoke(st, 0, 80);\npoke(st, 0, 81);\n}\nif (on_E == 0) {\npoke(st, 0, 82);\npoke(st, 0, 83);\npoke(st, 0, 84);\npoke(st, 0, 85);\npoke(st, 0, 86);\npoke(st, 0, 87);\npoke(st, 0, 88);\npoke(st, 0, 89);\npoke(st, 0, 90);\npoke(st, 0, 91);\npoke(st, 0, 92);\npoke(st, 0, 93);\npoke(st, 0, 94);\npoke(st, 0, 95);\npoke(st, 0, 96);\npoke(st, 0, 97);\npoke(st, 0, 98);\npoke(st, 0, 99);\npoke(st, 0, 100);\npoke(st, 0, 101);\npoke(st, 0, 102);\npoke(st, 0, 103);\npoke(st, 0, 104);\npoke(st, 0, 105);\npoke(st, 0, 106);\npoke(st, 0, 107);\npoke(st, 0, 108);\npoke(st, 0, 109);\npoke(st, 0, 110);\npoke(st, 0, 111);\n}\nif (on_G == 0) {\npoke(st, 0, 112);\npoke(st, 0, 113);\npoke(st, 0, 114);\npoke(st, 0, 115);\npoke(st, 0, 116);\npoke(st, 0, 117);\npoke(st, 0, 118);\npoke(st, 0, 119);\npoke(st, 0, 120);\npoke(st, 0, 121);\npoke(st, 0, 122);\npoke(st, 0, 123);\npoke(st, 0, 124);\npoke(st, 0, 125);\npoke(st, 0, 126);\npoke(st, 0, 127);\npoke(st, 0, 128);\npoke(st, 0, 129);\npoke(st, 0, 130);\npoke(st, 0, 131);\npoke(st, 0, 132);\npoke(st, 0, 133);\npoke(st, 0, 134);\npoke(st, 0, 135);\npoke(st, 0, 136);\npoke(st, 0, 137);\npoke(st, 0, 138);\npoke(st, 0, 139);\npoke(st, 0, 140);\npoke(st, 0, 141);\n}\nif (on_F == 0) {\npoke(st, 0, 142);\npoke(st, 0, 143);\npoke(st, 0, 144);\npoke(st, 0, 145);\npoke(st, 0, 146);\npoke(st, 0, 147);\n}\nif (on_P == 0) {\npoke(st, 0, 148);\npoke(st, 0, 149);\npoke(st, 0, 150);\npoke(st, 0, 151);\npoke(st, 0, 152);\npoke(st, 0, 153);\npoke(st, 0, 154);\npoke(st, 0, 155);\npoke(st, 0, 156);\npoke(st, 0, 157);\n}\nd0 = L_y1;\nd1 = L_y0;\nd0 = ap(hb, 32, d0, 0.04245470986526787);\nd0 = ap(hb, 36, d0, 0.39331989319033134);\nd1 = ap(hb, 34, d1, 0.17073985049750015);\nd1 = ap(hb, 38, d1, 0.7457135887202412);\nL_v0 = 0.5 * (d0 + d1);\nd0 = L_y3;\nd1 = L_y2;\nd0 = ap(hb, 32, d0, 0.04245470986526787);\nd0 = ap(hb, 36, d0, 0.39331989319033134);\nd1 = ap(hb, 34, d1, 0.17073985049750015);\nd1 = ap(hb, 38, d1, 0.7457135887202412);\nL_v1 = 0.5 * (d0 + d1);\nd0 = L_v1;\nd1 = L_v0;\nd0 = ap(hb, 40, d0, 0.019059005558478156);\nd0 = ap(hb, 44, d0, 0.1559582483500435);\nd0 = ap(hb, 48, d0, 0.3650536901969154);\nd0 = ap(hb, 52, d0, 0.5755010797915323);\nd0 = ap(hb, 56, d0, 0.7526447471286863);\nd0 = ap(hb, 60, d0, 0.8980636464339091);\nd1 = ap(hb, 42, d1, 0.07350243453590219);\nd1 = ap(hb, 46, d1, 0.25649919975582064);\nd1 = ap(hb, 50, d1, 0.47327898479453656);\nd1 = ap(hb, 54, d1, 0.6688095014357188);\nd1 = ap(hb, 58, d1, 0.8282265929955738);\nd1 = ap(hb, 62, d1, 0.9656701590349398);\nL_w = 0.5 * (d0 + d1);\nL_out = g_gain * g_fader * L_w;\n\n// ===== lato R =====\nR_e = in2;\nR_o = in2;\nR_e = ap(hb, 64, R_e, 0.019059005558478156);\nR_e = ap(hb, 68, R_e, 0.1559582483500435);\nR_e = ap(hb, 72, R_e, 0.3650536901969154);\nR_e = ap(hb, 76, R_e, 0.5755010797915323);\nR_e = ap(hb, 80, R_e, 0.7526447471286863);\nR_e = ap(hb, 84, R_e, 0.8980636464339091);\nR_o = ap(hb, 66, R_o, 0.07350243453590219);\nR_o = ap(hb, 70, R_o, 0.25649919975582064);\nR_o = ap(hb, 74, R_o, 0.47327898479453656);\nR_o = ap(hb, 78, R_o, 0.6688095014357188);\nR_o = ap(hb, 82, R_o, 0.8282265929955738);\nR_o = ap(hb, 86, R_o, 0.9656701590349398);\nR_u0 = R_e;\nR_u1 = R_e;\nR_u0 = ap(hb, 88, R_u0, 0.04245470986526787);\nR_u0 = ap(hb, 92, R_u0, 0.39331989319033134);\nR_u1 = ap(hb, 90, R_u1, 0.17073985049750015);\nR_u1 = ap(hb, 94, R_u1, 0.7457135887202412);\nR_u2 = R_o;\nR_u3 = R_o;\nR_u2 = ap(hb, 88, R_u2, 0.04245470986526787);\nR_u2 = ap(hb, 92, R_u2, 0.39331989319033134);\nR_u3 = ap(hb, 90, R_u3, 0.17073985049750015);\nR_u3 = ap(hb, 94, R_u3, 0.7457135887202412);\nR0A = 0;\nif (on_A) {\nR0Al = bq(st, 158, R_u0, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR0Al = bq(st, 160, R0Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR0Al = bq(st, 162, R0Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nR0Al = bq(st, 164, R0Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR0Ah1 = bq(st, 166, R_u0, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR0Ah1 = bq(st, 168, R0Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR0Alm = bq(st, 170, R0Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR0Alm = bq(st, 172, R0Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR0Alm = bq(st, 174, R0Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR0Ah2 = bq(st, 176, R0Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR0Ah2 = bq(st, 178, R0Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR0Amh = bq(st, 180, R0Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR0Amh = bq(st, 182, R0Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR0Ahi = bq(st, 184, R0Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR0Ahi = bq(st, 186, R0Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR0A = g_low * R0Al + g_lowmid * R0Alm + g_midhigh * R0Amh + g_high * R0Ahi;\n}\nR0C = 0;\nif (on_C) {\nR0Cl = bq(st, 188, R_u0, C1_lb, 2 * C1_lb, C1_lb, C1_a1, C1_a2);\nR0Cl = bq(st, 190, R0Cl, C2_a2, C2_a1, 1, C2_a1, C2_a2);\nR0Cl = bq(st, 192, R0Cl, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nR0Ch1 = bq(st, 194, R_u0, C1_n, -2 * C1_n, C1_n, C1_a1, C1_a2);\nR0Ch1 = -R0Ch1;\nR0Clm = bq(st, 196, R0Ch1, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nR0Clm = bq(st, 198, R0Clm, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nR0Clm = bq(st, 200, R0Clm, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nR0Ch2 = bq(st, 202, R0Ch1, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nR0Ch2 = bq(st, 204, R0Ch2, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nR0Cmh = bq(st, 206, R0Ch2, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nR0Cmh = bq(st, 208, R0Cmh, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nR0Chi = bq(st, 210, R0Ch2, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nR0Chi = bq(st, 212, R0Chi, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nR0C = g_low * R0Cl + g_lowmid * R0Clm + g_midhigh * R0Cmh + g_high * R0Chi;\n}\nR0D = 0;\nif (on_D) {\nR0Dl = bq(st, 214, R_u0, D1_lb, 2 * D1_lb, D1_lb, D1_a1, D1_a2);\nR0Dl = bq(st, 216, R0Dl, D2_a2, D2_a1, 1, D2_a1, D2_a2);\nR0Dl = bq(st, 218, R0Dl, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nR0Dh1 = bq(st, 220, R_u0, D1_n, -2 * D1_n, D1_n, D1_a1, D1_a2);\nR0Dh1 = -R0Dh1;\nR0Dlm = bq(st, 222, R0Dh1, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nR0Dlm = bq(st, 224, R0Dlm, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nR0Dlm = bq(st, 226, R0Dlm, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nR0Dh2 = bq(st, 228, R0Dh1, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nR0Dh2 = bq(st, 230, R0Dh2, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nR0Dmh = bq(st, 232, R0Dh2, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nR0Dmh = bq(st, 234, R0Dmh, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nR0Dhi = bq(st, 236, R0Dh2, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nR0Dhi = bq(st, 238, R0Dhi, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nR0D = g_low * R0Dl + g_lowmid * R0Dlm + g_midhigh * R0Dmh + g_high * R0Dhi;\n}\nR0E = 0;\nif (on_E) {\nR0El = bq(st, 240, R_u0, E1_lb, 2 * E1_lb, E1_lb, E1_a1, E1_a2);\nR0El = bq(st, 242, R0El, E1_lb, 2 * E1_lb, E1_lb, E1_a1, E1_a2);\nR0El = bq(st, 244, R0El, E2_a2, E2_a1, 1, E2_a1, E2_a2);\nR0El = bq(st, 246, R0El, E3_a2, E3_a1, 1, E3_a1, E3_a2);\nR0Eh1 = bq(st, 248, R_u0, E1_n, -2 * E1_n, E1_n, E1_a1, E1_a2);\nR0Eh1 = bq(st, 250, R0Eh1, E1_n, -2 * E1_n, E1_n, E1_a1, E1_a2);\nR0Elm = bq(st, 252, R0Eh1, E2_lb, 2 * E2_lb, E2_lb, E2_a1, E2_a2);\nR0Elm = bq(st, 254, R0Elm, E2_lb, 2 * E2_lb, E2_lb, E2_a1, E2_a2);\nR0Elm = bq(st, 256, R0Elm, E3_a2, E3_a1, 1, E3_a1, E3_a2);\nR0Eh2 = bq(st, 258, R0Eh1, E2_n, -2 * E2_n, E2_n, E2_a1, E2_a2);\nR0Eh2 = bq(st, 260, R0Eh2, E2_n, -2 * E2_n, E2_n, E2_a1, E2_a2);\nR0Emh = bq(st, 262, R0Eh2, E3_lb, 2 * E3_lb, E3_lb, E3_a1, E3_a2);\nR0Emh = bq(st, 264, R0Emh, E3_lb, 2 * E3_lb, E3_lb, E3_a1, E3_a2);\nR0Ehi = bq(st, 266, R0Eh2, E3_n, -2 * E3_n, E3_n, E3_a1, E3_a2);\nR0Ehi = bq(st, 268, R0Ehi, E3_n, -2 * E3_n, E3_n, E3_a1, E3_a2);\nR0E = g_low * R0El + g_lowmid * R0Elm + g_midhigh * R0Emh + g_high * R0Ehi;\n}\nR0G = 0;\nif (on_G) {\nR0Gl = bq(st, 270, R_u0, G1_lb, 2 * G1_lb, G1_lb, G1_a1, G1_a2);\nR0Gl = bq(st, 272, R0Gl, G1_lb, 2 * G1_lb, G1_lb, G1_a1, G1_a2);\nR0Gl = bq(st, 274, R0Gl, G2_a2, G2_a1, 1, G2_a1, G2_a2);\nR0Gl = bq(st, 276, R0Gl, G3_a2, G3_a1, 1, G3_a1, G3_a2);\nR0Gh1 = bq(st, 278, R_u0, G1_n, -2 * G1_n, G1_n, G1_a1, G1_a2);\nR0Gh1 = bq(st, 280, R0Gh1, G1_n, -2 * G1_n, G1_n, G1_a1, G1_a2);\nR0Glm = bq(st, 282, R0Gh1, G2_lb, 2 * G2_lb, G2_lb, G2_a1, G2_a2);\nR0Glm = bq(st, 284, R0Glm, G2_lb, 2 * G2_lb, G2_lb, G2_a1, G2_a2);\nR0Glm = bq(st, 286, R0Glm, G3_a2, G3_a1, 1, G3_a1, G3_a2);\nR0Gh2 = bq(st, 288, R0Gh1, G2_n, -2 * G2_n, G2_n, G2_a1, G2_a2);\nR0Gh2 = bq(st, 290, R0Gh2, G2_n, -2 * G2_n, G2_n, G2_a1, G2_a2);\nR0Gmh = bq(st, 292, R0Gh2, G3_lb, 2 * G3_lb, G3_lb, G3_a1, G3_a2);\nR0Gmh = bq(st, 294, R0Gmh, G3_lb, 2 * G3_lb, G3_lb, G3_a1, G3_a2);\nR0Ghi = bq(st, 296, R0Gh2, G3_n, -2 * G3_n, G3_n, G3_a1, G3_a2);\nR0Ghi = bq(st, 298, R0Ghi, G3_n, -2 * G3_n, G3_n, G3_a1, G3_a2);\nR0G = g_low * R0Gl + g_lowmid * R0Glm + g_midhigh * R0Gmh + g_high * R0Ghi;\n}\nR0jF = 0;\nif (on_F) {\nR0jF = R_u0;\nR0jF = bq(st, 300, R0jF, jFl_b0, jFl_b1, jFl_b2, jFl_a1, jFl_a2);\nR0jF = bq(st, 302, R0jF, jFm_b0, jFm_a1, jFm_b2, jFm_a1, jFm_a2);\nR0jF = bq(st, 304, R0jF, jFh_b0, jFh_b1, jFh_b2, jFh_a1, jFh_a2);\n}\nR0jP = 0;\nif (on_P) {\nR0jP = R_u0;\nR0jP = bq(st, 306, R0jP, jPl_b0, jPl_b1, jPl_b2, jPl_a1, jPl_a2);\nR0jP = bq(st, 308, R0jP, jPl_b0, jPl_b1, jPl_b2, jPl_a1, jPl_a2);\nR0jP = bq(st, 310, R0jP, jPm_b0, jPm_a1, jPm_b2, jPm_a1, jPm_a2);\nR0jP = bq(st, 312, R0jP, jPh_b0, jPh_b1, jPh_b2, jPh_a1, jPh_a2);\nR0jP = bq(st, 314, R0jP, jPh_b0, jPh_b1, jPh_b2, jPh_a1, jPh_a2);\n}\nR_y0 = w_A * R0A + w_C * R0C + w_D * R0D + w_E * R0E + w_G * R0G + w_F * R0jF + w_P * R0jP;\nR1A = 0;\nif (on_A) {\nR1Al = bq(st, 158, R_u1, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR1Al = bq(st, 160, R1Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR1Al = bq(st, 162, R1Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nR1Al = bq(st, 164, R1Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR1Ah1 = bq(st, 166, R_u1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR1Ah1 = bq(st, 168, R1Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR1Alm = bq(st, 170, R1Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR1Alm = bq(st, 172, R1Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR1Alm = bq(st, 174, R1Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR1Ah2 = bq(st, 176, R1Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR1Ah2 = bq(st, 178, R1Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR1Amh = bq(st, 180, R1Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR1Amh = bq(st, 182, R1Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR1Ahi = bq(st, 184, R1Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR1Ahi = bq(st, 186, R1Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR1A = g_low * R1Al + g_lowmid * R1Alm + g_midhigh * R1Amh + g_high * R1Ahi;\n}\nR1C = 0;\nif (on_C) {\nR1Cl = bq(st, 188, R_u1, C1_lb, 2 * C1_lb, C1_lb, C1_a1, C1_a2);\nR1Cl = bq(st, 190, R1Cl, C2_a2, C2_a1, 1, C2_a1, C2_a2);\nR1Cl = bq(st, 192, R1Cl, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nR1Ch1 = bq(st, 194, R_u1, C1_n, -2 * C1_n, C1_n, C1_a1, C1_a2);\nR1Ch1 = -R1Ch1;\nR1Clm = bq(st, 196, R1Ch1, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nR1Clm = bq(st, 198, R1Clm, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nR1Clm = bq(st, 200, R1Clm, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nR1Ch2 = bq(st, 202, R1Ch1, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nR1Ch2 = bq(st, 204, R1Ch2, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nR1Cmh = bq(st, 206, R1Ch2, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nR1Cmh = bq(st, 208, R1Cmh, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nR1Chi = bq(st, 210, R1Ch2, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nR1Chi = bq(st, 212, R1Chi, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nR1C = g_low * R1Cl + g_lowmid * R1Clm + g_midhigh * R1Cmh + g_high * R1Chi;\n}\nR1D = 0;\nif (on_D) {\nR1Dl = bq(st, 214, R_u1, D1_lb, 2 * D1_lb, D1_lb, D1_a1, D1_a2);\nR1Dl = bq(st, 216, R1Dl, D2_a2, D2_a1, 1, D2_a1, D2_a2);\nR1Dl = bq(st, 218, R1Dl, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nR1Dh1 = bq(st, 220, R_u1, D1_n, -2 * D1_n, D1_n, D1_a1, D1_a2);\nR1Dh1 = -R1Dh1;\nR1Dlm = bq(st, 222, R1Dh1, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nR1Dlm = bq(st, 224, R1Dlm, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nR1Dlm = bq(st, 226, R1Dlm, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nR1Dh2 = bq(st, 228, R1Dh1, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nR1Dh2 = bq(st, 230, R1Dh2, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nR1Dmh = bq(st, 232, R1Dh2, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nR1Dmh = bq(st, 234, R1Dmh, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nR1Dhi = bq(st, 236, R1Dh2, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nR1Dhi = bq(st, 238, R1Dhi, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nR1D = g_low * R1Dl + g_lowmid * R1Dlm + g_midhigh * R1Dmh + g_high * R1Dhi;\n}\nR1E = 0;\nif (on_E) {\nR1El = bq(st, 240, R_u1, E1_lb, 2 * E1_lb, E1_lb, E1_a1, E1_a2);\nR1El = bq(st, 242, R1El, E1_lb, 2 * E1_lb, E1_lb, E1_a1, E1_a2);\nR1El = bq(st, 244, R1El, E2_a2, E2_a1, 1, E2_a1, E2_a2);\nR1El = bq(st, 246, R1El, E3_a2, E3_a1, 1, E3_a1, E3_a2);\nR1Eh1 = bq(st, 248, R_u1, E1_n, -2 * E1_n, E1_n, E1_a1, E1_a2);\nR1Eh1 = bq(st, 250, R1Eh1, E1_n, -2 * E1_n, E1_n, E1_a1, E1_a2);\nR1Elm = bq(st, 252, R1Eh1, E2_lb, 2 * E2_lb, E2_lb, E2_a1, E2_a2);\nR1Elm = bq(st, 254, R1Elm, E2_lb, 2 * E2_lb, E2_lb, E2_a1, E2_a2);\nR1Elm = bq(st, 256, R1Elm, E3_a2, E3_a1, 1, E3_a1, E3_a2);\nR1Eh2 = bq(st, 258, R1Eh1, E2_n, -2 * E2_n, E2_n, E2_a1, E2_a2);\nR1Eh2 = bq(st, 260, R1Eh2, E2_n, -2 * E2_n, E2_n, E2_a1, E2_a2);\nR1Emh = bq(st, 262, R1Eh2, E3_lb, 2 * E3_lb, E3_lb, E3_a1, E3_a2);\nR1Emh = bq(st, 264, R1Emh, E3_lb, 2 * E3_lb, E3_lb, E3_a1, E3_a2);\nR1Ehi = bq(st, 266, R1Eh2, E3_n, -2 * E3_n, E3_n, E3_a1, E3_a2);\nR1Ehi = bq(st, 268, R1Ehi, E3_n, -2 * E3_n, E3_n, E3_a1, E3_a2);\nR1E = g_low * R1El + g_lowmid * R1Elm + g_midhigh * R1Emh + g_high * R1Ehi;\n}\nR1G = 0;\nif (on_G) {\nR1Gl = bq(st, 270, R_u1, G1_lb, 2 * G1_lb, G1_lb, G1_a1, G1_a2);\nR1Gl = bq(st, 272, R1Gl, G1_lb, 2 * G1_lb, G1_lb, G1_a1, G1_a2);\nR1Gl = bq(st, 274, R1Gl, G2_a2, G2_a1, 1, G2_a1, G2_a2);\nR1Gl = bq(st, 276, R1Gl, G3_a2, G3_a1, 1, G3_a1, G3_a2);\nR1Gh1 = bq(st, 278, R_u1, G1_n, -2 * G1_n, G1_n, G1_a1, G1_a2);\nR1Gh1 = bq(st, 280, R1Gh1, G1_n, -2 * G1_n, G1_n, G1_a1, G1_a2);\nR1Glm = bq(st, 282, R1Gh1, G2_lb, 2 * G2_lb, G2_lb, G2_a1, G2_a2);\nR1Glm = bq(st, 284, R1Glm, G2_lb, 2 * G2_lb, G2_lb, G2_a1, G2_a2);\nR1Glm = bq(st, 286, R1Glm, G3_a2, G3_a1, 1, G3_a1, G3_a2);\nR1Gh2 = bq(st, 288, R1Gh1, G2_n, -2 * G2_n, G2_n, G2_a1, G2_a2);\nR1Gh2 = bq(st, 290, R1Gh2, G2_n, -2 * G2_n, G2_n, G2_a1, G2_a2);\nR1Gmh = bq(st, 292, R1Gh2, G3_lb, 2 * G3_lb, G3_lb, G3_a1, G3_a2);\nR1Gmh = bq(st, 294, R1Gmh, G3_lb, 2 * G3_lb, G3_lb, G3_a1, G3_a2);\nR1Ghi = bq(st, 296, R1Gh2, G3_n, -2 * G3_n, G3_n, G3_a1, G3_a2);\nR1Ghi = bq(st, 298, R1Ghi, G3_n, -2 * G3_n, G3_n, G3_a1, G3_a2);\nR1G = g_low * R1Gl + g_lowmid * R1Glm + g_midhigh * R1Gmh + g_high * R1Ghi;\n}\nR1jF = 0;\nif (on_F) {\nR1jF = R_u1;\nR1jF = bq(st, 300, R1jF, jFl_b0, jFl_b1, jFl_b2, jFl_a1, jFl_a2);\nR1jF = bq(st, 302, R1jF, jFm_b0, jFm_a1, jFm_b2, jFm_a1, jFm_a2);\nR1jF = bq(st, 304, R1jF, jFh_b0, jFh_b1, jFh_b2, jFh_a1, jFh_a2);\n}\nR1jP = 0;\nif (on_P) {\nR1jP = R_u1;\nR1jP = bq(st, 306, R1jP, jPl_b0, jPl_b1, jPl_b2, jPl_a1, jPl_a2);\nR1jP = bq(st, 308, R1jP, jPl_b0, jPl_b1, jPl_b2, jPl_a1, jPl_a2);\nR1jP = bq(st, 310, R1jP, jPm_b0, jPm_a1, jPm_b2, jPm_a1, jPm_a2);\nR1jP = bq(st, 312, R1jP, jPh_b0, jPh_b1, jPh_b2, jPh_a1, jPh_a2);\nR1jP = bq(st, 314, R1jP, jPh_b0, jPh_b1, jPh_b2, jPh_a1, jPh_a2);\n}\nR_y1 = w_A * R1A + w_C * R1C + w_D * R1D + w_E * R1E + w_G * R1G + w_F * R1jF + w_P * R1jP;\nR2A = 0;\nif (on_A) {\nR2Al = bq(st, 158, R_u2, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR2Al = bq(st, 160, R2Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR2Al = bq(st, 162, R2Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nR2Al = bq(st, 164, R2Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR2Ah1 = bq(st, 166, R_u2, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR2Ah1 = bq(st, 168, R2Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR2Alm = bq(st, 170, R2Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR2Alm = bq(st, 172, R2Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR2Alm = bq(st, 174, R2Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR2Ah2 = bq(st, 176, R2Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR2Ah2 = bq(st, 178, R2Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR2Amh = bq(st, 180, R2Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR2Amh = bq(st, 182, R2Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR2Ahi = bq(st, 184, R2Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR2Ahi = bq(st, 186, R2Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR2A = g_low * R2Al + g_lowmid * R2Alm + g_midhigh * R2Amh + g_high * R2Ahi;\n}\nR2C = 0;\nif (on_C) {\nR2Cl = bq(st, 188, R_u2, C1_lb, 2 * C1_lb, C1_lb, C1_a1, C1_a2);\nR2Cl = bq(st, 190, R2Cl, C2_a2, C2_a1, 1, C2_a1, C2_a2);\nR2Cl = bq(st, 192, R2Cl, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nR2Ch1 = bq(st, 194, R_u2, C1_n, -2 * C1_n, C1_n, C1_a1, C1_a2);\nR2Ch1 = -R2Ch1;\nR2Clm = bq(st, 196, R2Ch1, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nR2Clm = bq(st, 198, R2Clm, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nR2Clm = bq(st, 200, R2Clm, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nR2Ch2 = bq(st, 202, R2Ch1, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nR2Ch2 = bq(st, 204, R2Ch2, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nR2Cmh = bq(st, 206, R2Ch2, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nR2Cmh = bq(st, 208, R2Cmh, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nR2Chi = bq(st, 210, R2Ch2, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nR2Chi = bq(st, 212, R2Chi, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nR2C = g_low * R2Cl + g_lowmid * R2Clm + g_midhigh * R2Cmh + g_high * R2Chi;\n}\nR2D = 0;\nif (on_D) {\nR2Dl = bq(st, 214, R_u2, D1_lb, 2 * D1_lb, D1_lb, D1_a1, D1_a2);\nR2Dl = bq(st, 216, R2Dl, D2_a2, D2_a1, 1, D2_a1, D2_a2);\nR2Dl = bq(st, 218, R2Dl, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nR2Dh1 = bq(st, 220, R_u2, D1_n, -2 * D1_n, D1_n, D1_a1, D1_a2);\nR2Dh1 = -R2Dh1;\nR2Dlm = bq(st, 222, R2Dh1, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nR2Dlm = bq(st, 224, R2Dlm, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nR2Dlm = bq(st, 226, R2Dlm, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nR2Dh2 = bq(st, 228, R2Dh1, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nR2Dh2 = bq(st, 230, R2Dh2, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nR2Dmh = bq(st, 232, R2Dh2, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nR2Dmh = bq(st, 234, R2Dmh, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nR2Dhi = bq(st, 236, R2Dh2, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nR2Dhi = bq(st, 238, R2Dhi, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nR2D = g_low * R2Dl + g_lowmid * R2Dlm + g_midhigh * R2Dmh + g_high * R2Dhi;\n}\nR2E = 0;\nif (on_E) {\nR2El = bq(st, 240, R_u2, E1_lb, 2 * E1_lb, E1_lb, E1_a1, E1_a2);\nR2El = bq(st, 242, R2El, E1_lb, 2 * E1_lb, E1_lb, E1_a1, E1_a2);\nR2El = bq(st, 244, R2El, E2_a2, E2_a1, 1, E2_a1, E2_a2);\nR2El = bq(st, 246, R2El, E3_a2, E3_a1, 1, E3_a1, E3_a2);\nR2Eh1 = bq(st, 248, R_u2, E1_n, -2 * E1_n, E1_n, E1_a1, E1_a2);\nR2Eh1 = bq(st, 250, R2Eh1, E1_n, -2 * E1_n, E1_n, E1_a1, E1_a2);\nR2Elm = bq(st, 252, R2Eh1, E2_lb, 2 * E2_lb, E2_lb, E2_a1, E2_a2);\nR2Elm = bq(st, 254, R2Elm, E2_lb, 2 * E2_lb, E2_lb, E2_a1, E2_a2);\nR2Elm = bq(st, 256, R2Elm, E3_a2, E3_a1, 1, E3_a1, E3_a2);\nR2Eh2 = bq(st, 258, R2Eh1, E2_n, -2 * E2_n, E2_n, E2_a1, E2_a2);\nR2Eh2 = bq(st, 260, R2Eh2, E2_n, -2 * E2_n, E2_n, E2_a1, E2_a2);\nR2Emh = bq(st, 262, R2Eh2, E3_lb, 2 * E3_lb, E3_lb, E3_a1, E3_a2);\nR2Emh = bq(st, 264, R2Emh, E3_lb, 2 * E3_lb, E3_lb, E3_a1, E3_a2);\nR2Ehi = bq(st, 266, R2Eh2, E3_n, -2 * E3_n, E3_n, E3_a1, E3_a2);\nR2Ehi = bq(st, 268, R2Ehi, E3_n, -2 * E3_n, E3_n, E3_a1, E3_a2);\nR2E = g_low * R2El + g_lowmid * R2Elm + g_midhigh * R2Emh + g_high * R2Ehi;\n}\nR2G = 0;\nif (on_G) {\nR2Gl = bq(st, 270, R_u2, G1_lb, 2 * G1_lb, G1_lb, G1_a1, G1_a2);\nR2Gl = bq(st, 272, R2Gl, G1_lb, 2 * G1_lb, G1_lb, G1_a1, G1_a2);\nR2Gl = bq(st, 274, R2Gl, G2_a2, G2_a1, 1, G2_a1, G2_a2);\nR2Gl = bq(st, 276, R2Gl, G3_a2, G3_a1, 1, G3_a1, G3_a2);\nR2Gh1 = bq(st, 278, R_u2, G1_n, -2 * G1_n, G1_n, G1_a1, G1_a2);\nR2Gh1 = bq(st, 280, R2Gh1, G1_n, -2 * G1_n, G1_n, G1_a1, G1_a2);\nR2Glm = bq(st, 282, R2Gh1, G2_lb, 2 * G2_lb, G2_lb, G2_a1, G2_a2);\nR2Glm = bq(st, 284, R2Glm, G2_lb, 2 * G2_lb, G2_lb, G2_a1, G2_a2);\nR2Glm = bq(st, 286, R2Glm, G3_a2, G3_a1, 1, G3_a1, G3_a2);\nR2Gh2 = bq(st, 288, R2Gh1, G2_n, -2 * G2_n, G2_n, G2_a1, G2_a2);\nR2Gh2 = bq(st, 290, R2Gh2, G2_n, -2 * G2_n, G2_n, G2_a1, G2_a2);\nR2Gmh = bq(st, 292, R2Gh2, G3_lb, 2 * G3_lb, G3_lb, G3_a1, G3_a2);\nR2Gmh = bq(st, 294, R2Gmh, G3_lb, 2 * G3_lb, G3_lb, G3_a1, G3_a2);\nR2Ghi = bq(st, 296, R2Gh2, G3_n, -2 * G3_n, G3_n, G3_a1, G3_a2);\nR2Ghi = bq(st, 298, R2Ghi, G3_n, -2 * G3_n, G3_n, G3_a1, G3_a2);\nR2G = g_low * R2Gl + g_lowmid * R2Glm + g_midhigh * R2Gmh + g_high * R2Ghi;\n}\nR2jF = 0;\nif (on_F) {\nR2jF = R_u2;\nR2jF = bq(st, 300, R2jF, jFl_b0, jFl_b1, jFl_b2, jFl_a1, jFl_a2);\nR2jF = bq(st, 302, R2jF, jFm_b0, jFm_a1, jFm_b2, jFm_a1, jFm_a2);\nR2jF = bq(st, 304, R2jF, jFh_b0, jFh_b1, jFh_b2, jFh_a1, jFh_a2);\n}\nR2jP = 0;\nif (on_P) {\nR2jP = R_u2;\nR2jP = bq(st, 306, R2jP, jPl_b0, jPl_b1, jPl_b2, jPl_a1, jPl_a2);\nR2jP = bq(st, 308, R2jP, jPl_b0, jPl_b1, jPl_b2, jPl_a1, jPl_a2);\nR2jP = bq(st, 310, R2jP, jPm_b0, jPm_a1, jPm_b2, jPm_a1, jPm_a2);\nR2jP = bq(st, 312, R2jP, jPh_b0, jPh_b1, jPh_b2, jPh_a1, jPh_a2);\nR2jP = bq(st, 314, R2jP, jPh_b0, jPh_b1, jPh_b2, jPh_a1, jPh_a2);\n}\nR_y2 = w_A * R2A + w_C * R2C + w_D * R2D + w_E * R2E + w_G * R2G + w_F * R2jF + w_P * R2jP;\nR3A = 0;\nif (on_A) {\nR3Al = bq(st, 158, R_u3, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR3Al = bq(st, 160, R3Al, A1_lb, 2 * A1_lb, A1_lb, A1_a1, A1_a2);\nR3Al = bq(st, 162, R3Al, A2_a2, A2_a1, 1, A2_a1, A2_a2);\nR3Al = bq(st, 164, R3Al, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR3Ah1 = bq(st, 166, R_u3, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR3Ah1 = bq(st, 168, R3Ah1, A1_n, -2 * A1_n, A1_n, A1_a1, A1_a2);\nR3Alm = bq(st, 170, R3Ah1, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR3Alm = bq(st, 172, R3Alm, A2_lb, 2 * A2_lb, A2_lb, A2_a1, A2_a2);\nR3Alm = bq(st, 174, R3Alm, A3_a2, A3_a1, 1, A3_a1, A3_a2);\nR3Ah2 = bq(st, 176, R3Ah1, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR3Ah2 = bq(st, 178, R3Ah2, A2_n, -2 * A2_n, A2_n, A2_a1, A2_a2);\nR3Amh = bq(st, 180, R3Ah2, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR3Amh = bq(st, 182, R3Amh, A3_lb, 2 * A3_lb, A3_lb, A3_a1, A3_a2);\nR3Ahi = bq(st, 184, R3Ah2, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR3Ahi = bq(st, 186, R3Ahi, A3_n, -2 * A3_n, A3_n, A3_a1, A3_a2);\nR3A = g_low * R3Al + g_lowmid * R3Alm + g_midhigh * R3Amh + g_high * R3Ahi;\n}\nR3C = 0;\nif (on_C) {\nR3Cl = bq(st, 188, R_u3, C1_lb, 2 * C1_lb, C1_lb, C1_a1, C1_a2);\nR3Cl = bq(st, 190, R3Cl, C2_a2, C2_a1, 1, C2_a1, C2_a2);\nR3Cl = bq(st, 192, R3Cl, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nR3Ch1 = bq(st, 194, R_u3, C1_n, -2 * C1_n, C1_n, C1_a1, C1_a2);\nR3Ch1 = -R3Ch1;\nR3Clm = bq(st, 196, R3Ch1, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nR3Clm = bq(st, 198, R3Clm, C2_lb, 2 * C2_lb, C2_lb, C2_a1, C2_a2);\nR3Clm = bq(st, 200, R3Clm, C3_a2, C3_a1, 1, C3_a1, C3_a2);\nR3Ch2 = bq(st, 202, R3Ch1, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nR3Ch2 = bq(st, 204, R3Ch2, C2_n, -2 * C2_n, C2_n, C2_a1, C2_a2);\nR3Cmh = bq(st, 206, R3Ch2, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nR3Cmh = bq(st, 208, R3Cmh, C3_lb, 2 * C3_lb, C3_lb, C3_a1, C3_a2);\nR3Chi = bq(st, 210, R3Ch2, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nR3Chi = bq(st, 212, R3Chi, C3_n, -2 * C3_n, C3_n, C3_a1, C3_a2);\nR3C = g_low * R3Cl + g_lowmid * R3Clm + g_midhigh * R3Cmh + g_high * R3Chi;\n}\nR3D = 0;\nif (on_D) {\nR3Dl = bq(st, 214, R_u3, D1_lb, 2 * D1_lb, D1_lb, D1_a1, D1_a2);\nR3Dl = bq(st, 216, R3Dl, D2_a2, D2_a1, 1, D2_a1, D2_a2);\nR3Dl = bq(st, 218, R3Dl, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nR3Dh1 = bq(st, 220, R_u3, D1_n, -2 * D1_n, D1_n, D1_a1, D1_a2);\nR3Dh1 = -R3Dh1;\nR3Dlm = bq(st, 222, R3Dh1, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nR3Dlm = bq(st, 224, R3Dlm, D2_lb, 2 * D2_lb, D2_lb, D2_a1, D2_a2);\nR3Dlm = bq(st, 226, R3Dlm, D3_a2, D3_a1, 1, D3_a1, D3_a2);\nR3Dh2 = bq(st, 228, R3Dh1, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nR3Dh2 = bq(st, 230, R3Dh2, D2_n, -2 * D2_n, D2_n, D2_a1, D2_a2);\nR3Dmh = bq(st, 232, R3Dh2, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nR3Dmh = bq(st, 234, R3Dmh, D3_lb, 2 * D3_lb, D3_lb, D3_a1, D3_a2);\nR3Dhi = bq(st, 236, R3Dh2, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nR3Dhi = bq(st, 238, R3Dhi, D3_n, -2 * D3_n, D3_n, D3_a1, D3_a2);\nR3D = g_low * R3Dl + g_lowmid * R3Dlm + g_midhigh * R3Dmh + g_high * R3Dhi;\n}\nR3E = 0;\nif (on_E) {\nR3El = bq(st, 240, R_u3, E1_lb, 2 * E1_lb, E1_lb, E1_a1, E1_a2);\nR3El = bq(st, 242, R3El, E1_lb, 2 * E1_lb, E1_lb, E1_a1, E1_a2);\nR3El = bq(st, 244, R3El, E2_a2, E2_a1, 1, E2_a1, E2_a2);\nR3El = bq(st, 246, R3El, E3_a2, E3_a1, 1, E3_a1, E3_a2);\nR3Eh1 = bq(st, 248, R_u3, E1_n, -2 * E1_n, E1_n, E1_a1, E1_a2);\nR3Eh1 = bq(st, 250, R3Eh1, E1_n, -2 * E1_n, E1_n, E1_a1, E1_a2);\nR3Elm = bq(st, 252, R3Eh1, E2_lb, 2 * E2_lb, E2_lb, E2_a1, E2_a2);\nR3Elm = bq(st, 254, R3Elm, E2_lb, 2 * E2_lb, E2_lb, E2_a1, E2_a2);\nR3Elm = bq(st, 256, R3Elm, E3_a2, E3_a1, 1, E3_a1, E3_a2);\nR3Eh2 = bq(st, 258, R3Eh1, E2_n, -2 * E2_n, E2_n, E2_a1, E2_a2);\nR3Eh2 = bq(st, 260, R3Eh2, E2_n, -2 * E2_n, E2_n, E2_a1, E2_a2);\nR3Emh = bq(st, 262, R3Eh2, E3_lb, 2 * E3_lb, E3_lb, E3_a1, E3_a2);\nR3Emh = bq(st, 264, R3Emh, E3_lb, 2 * E3_lb, E3_lb, E3_a1, E3_a2);\nR3Ehi = bq(st, 266, R3Eh2, E3_n, -2 * E3_n, E3_n, E3_a1, E3_a2);\nR3Ehi = bq(st, 268, R3Ehi, E3_n, -2 * E3_n, E3_n, E3_a1, E3_a2);\nR3E = g_low * R3El + g_lowmid * R3Elm + g_midhigh * R3Emh + g_high * R3Ehi;\n}\nR3G = 0;\nif (on_G) {\nR3Gl = bq(st, 270, R_u3, G1_lb, 2 * G1_lb, G1_lb, G1_a1, G1_a2);\nR3Gl = bq(st, 272, R3Gl, G1_lb, 2 * G1_lb, G1_lb, G1_a1, G1_a2);\nR3Gl = bq(st, 274, R3Gl, G2_a2, G2_a1, 1, G2_a1, G2_a2);\nR3Gl = bq(st, 276, R3Gl, G3_a2, G3_a1, 1, G3_a1, G3_a2);\nR3Gh1 = bq(st, 278, R_u3, G1_n, -2 * G1_n, G1_n, G1_a1, G1_a2);\nR3Gh1 = bq(st, 280, R3Gh1, G1_n, -2 * G1_n, G1_n, G1_a1, G1_a2);\nR3Glm = bq(st, 282, R3Gh1, G2_lb, 2 * G2_lb, G2_lb, G2_a1, G2_a2);\nR3Glm = bq(st, 284, R3Glm, G2_lb, 2 * G2_lb, G2_lb, G2_a1, G2_a2);\nR3Glm = bq(st, 286, R3Glm, G3_a2, G3_a1, 1, G3_a1, G3_a2);\nR3Gh2 = bq(st, 288, R3Gh1, G2_n, -2 * G2_n, G2_n, G2_a1, G2_a2);\nR3Gh2 = bq(st, 290, R3Gh2, G2_n, -2 * G2_n, G2_n, G2_a1, G2_a2);\nR3Gmh = bq(st, 292, R3Gh2, G3_lb, 2 * G3_lb, G3_lb, G3_a1, G3_a2);\nR3Gmh = bq(st, 294, R3Gmh, G3_lb, 2 * G3_lb, G3_lb, G3_a1, G3_a2);\nR3Ghi = bq(st, 296, R3Gh2, G3_n, -2 * G3_n, G3_n, G3_a1, G3_a2);\nR3Ghi = bq(st, 298, R3Ghi, G3_n, -2 * G3_n, G3_n, G3_a1, G3_a2);\nR3G = g_low * R3Gl + g_lowmid * R3Glm + g_midhigh * R3Gmh + g_high * R3Ghi;\n}\nR3jF = 0;\nif (on_F) {\nR3jF = R_u3;\nR3jF = bq(st, 300, R3jF, jFl_b0, jFl_b1, jFl_b2, jFl_a1, jFl_a2);\nR3jF = bq(st, 302, R3jF, jFm_b0, jFm_a1, jFm_b2, jFm_a1, jFm_a2);\nR3jF = bq(st, 304, R3jF, jFh_b0, jFh_b1, jFh_b2, jFh_a1, jFh_a2);\n}\nR3jP = 0;\nif (on_P) {\nR3jP = R_u3;\nR3jP = bq(st, 306, R3jP, jPl_b0, jPl_b1, jPl_b2, jPl_a1, jPl_a2);\nR3jP = bq(st, 308, R3jP, jPl_b0, jPl_b1, jPl_b2, jPl_a1, jPl_a2);\nR3jP = bq(st, 310, R3jP, jPm_b0, jPm_a1, jPm_b2, jPm_a1, jPm_a2);\nR3jP = bq(st, 312, R3jP, jPh_b0, jPh_b1, jPh_b2, jPh_a1, jPh_a2);\nR3jP = bq(st, 314, R3jP, jPh_b0, jPh_b1, jPh_b2, jPh_a1, jPh_a2);\n}\nR_y3 = w_A * R3A + w_C * R3C + w_D * R3D + w_E * R3E + w_G * R3G + w_F * R3jF + w_P * R3jP;\nif (on_A == 0) {\npoke(st, 0, 158);\npoke(st, 0, 159);\npoke(st, 0, 160);\npoke(st, 0, 161);\npoke(st, 0, 162);\npoke(st, 0, 163);\npoke(st, 0, 164);\npoke(st, 0, 165);\npoke(st, 0, 166);\npoke(st, 0, 167);\npoke(st, 0, 168);\npoke(st, 0, 169);\npoke(st, 0, 170);\npoke(st, 0, 171);\npoke(st, 0, 172);\npoke(st, 0, 173);\npoke(st, 0, 174);\npoke(st, 0, 175);\npoke(st, 0, 176);\npoke(st, 0, 177);\npoke(st, 0, 178);\npoke(st, 0, 179);\npoke(st, 0, 180);\npoke(st, 0, 181);\npoke(st, 0, 182);\npoke(st, 0, 183);\npoke(st, 0, 184);\npoke(st, 0, 185);\npoke(st, 0, 186);\npoke(st, 0, 187);\n}\nif (on_C == 0) {\npoke(st, 0, 188);\npoke(st, 0, 189);\npoke(st, 0, 190);\npoke(st, 0, 191);\npoke(st, 0, 192);\npoke(st, 0, 193);\npoke(st, 0, 194);\npoke(st, 0, 195);\npoke(st, 0, 196);\npoke(st, 0, 197);\npoke(st, 0, 198);\npoke(st, 0, 199);\npoke(st, 0, 200);\npoke(st, 0, 201);\npoke(st, 0, 202);\npoke(st, 0, 203);\npoke(st, 0, 204);\npoke(st, 0, 205);\npoke(st, 0, 206);\npoke(st, 0, 207);\npoke(st, 0, 208);\npoke(st, 0, 209);\npoke(st, 0, 210);\npoke(st, 0, 211);\npoke(st, 0, 212);\npoke(st, 0, 213);\n}\nif (on_D == 0) {\npoke(st, 0, 214);\npoke(st, 0, 215);\npoke(st, 0, 216);\npoke(st, 0, 217);\npoke(st, 0, 218);\npoke(st, 0, 219);\npoke(st, 0, 220);\npoke(st, 0, 221);\npoke(st, 0, 222);\npoke(st, 0, 223);\npoke(st, 0, 224);\npoke(st, 0, 225);\npoke(st, 0, 226);\npoke(st, 0, 227);\npoke(st, 0, 228);\npoke(st, 0, 229);\npoke(st, 0, 230);\npoke(st, 0, 231);\npoke(st, 0, 232);\npoke(st, 0, 233);\npoke(st, 0, 234);\npoke(st, 0, 235);\npoke(st, 0, 236);\npoke(st, 0, 237);\npoke(st, 0, 238);\npoke(st, 0, 239);\n}\nif (on_E == 0) {\npoke(st, 0, 240);\npoke(st, 0, 241);\npoke(st, 0, 242);\npoke(st, 0, 243);\npoke(st, 0, 244);\npoke(st, 0, 245);\npoke(st, 0, 246);\npoke(st, 0, 247);\npoke(st, 0, 248);\npoke(st, 0, 249);\npoke(st, 0, 250);\npoke(st, 0, 251);\npoke(st, 0, 252);\npoke(st, 0, 253);\npoke(st, 0, 254);\npoke(st, 0, 255);\npoke(st, 0, 256);\npoke(st, 0, 257);\npoke(st, 0, 258);\npoke(st, 0, 259);\npoke(st, 0, 260);\npoke(st, 0, 261);\npoke(st, 0, 262);\npoke(st, 0, 263);\npoke(st, 0, 264);\npoke(st, 0, 265);\npoke(st, 0, 266);\npoke(st, 0, 267);\npoke(st, 0, 268);\npoke(st, 0, 269);\n}\nif (on_G == 0) {\npoke(st, 0, 270);\npoke(st, 0, 271);\npoke(st, 0, 272);\npoke(st, 0, 273);\npoke(st, 0, 274);\npoke(st, 0, 275);\npoke(st, 0, 276);\npoke(st, 0, 277);\npoke(st, 0, 278);\npoke(st, 0, 279);\npoke(st, 0, 280);\npoke(st, 0, 281);\npoke(st, 0, 282);\npoke(st, 0, 283);\npoke(st, 0, 284);\npoke(st, 0, 285);\npoke(st, 0, 286);\npoke(st, 0, 287);\npoke(st, 0, 288);\npoke(st, 0, 289);\npoke(st, 0, 290);\npoke(st, 0, 291);\npoke(st, 0, 292);\npoke(st, 0, 293);\npoke(st, 0, 294);\npoke(st, 0, 295);\npoke(st, 0, 296);\npoke(st, 0, 297);\npoke(st, 0, 298);\npoke(st, 0, 299);\n}\nif (on_F == 0) {\npoke(st, 0, 300);\npoke(st, 0, 301);\npoke(st, 0, 302);\npoke(st, 0, 303);\npoke(st, 0, 304);\npoke(st, 0, 305);\n}\nif (on_P == 0) {\npoke(st, 0, 306);\npoke(st, 0, 307);\npoke(st, 0, 308);\npoke(st, 0, 309);\npoke(st, 0, 310);\npoke(st, 0, 311);\npoke(st, 0, 312);\npoke(st, 0, 313);\npoke(st, 0, 314);\npoke(st, 0, 315);\n}\nd0 = R_y1;\nd1 = R_y0;\nd0 = ap(hb, 96, d0, 0.04245470986526787);\nd0 = ap(hb, 100, d0, 0.39331989319033134);\nd1 = ap(hb, 98, d1, 0.17073985049750015);\nd1 = ap(hb, 102, d1, 0.7457135887202412);\nR_v0 = 0.5 * (d0 + d1);\nd0 = R_y3;\nd1 = R_y2;\nd0 = ap(hb, 96, d0, 0.04245470986526787);\nd0 = ap(hb, 100, d0, 0.39331989319033134);\nd1 = ap(hb, 98, d1, 0.17073985049750015);\nd1 = ap(hb, 102, d1, 0.7457135887202412);\nR_v1 = 0.5 * (d0 + d1);\nd0 = R_v1;\nd1 = R_v0;\nd0 = ap(hb, 104, d0, 0.019059005558478156);\nd0 = ap(hb, 108, d0, 0.1559582483500435);\nd0 = ap(hb, 112, d0, 0.3650536901969154);\nd0 = ap(hb, 116, d0, 0.5755010797915323);\nd0 = ap(hb, 120, d0, 0.7526447471286863);\nd0 = ap(hb, 124, d0, 0.8980636464339091);\nd1 = ap(hb, 106, d1, 0.07350243453590219);\nd1 = ap(hb, 110, d1, 0.25649919975582064);\nd1 = ap(hb, 114, d1, 0.47327898479453656);\nd1 = ap(hb, 118, d1, 0.6688095014357188);\nd1 = ap(hb, 122, d1, 0.8282265929955738);\nd1 = ap(hb, 126, d1, 0.9656701590349398);\nR_w = 0.5 * (d0 + d1);\nR_out = g_gain * g_fader * R_w;\n\n// protezione del prototipo: campione non valido -> stati a zero, silenzio\nbad = isnan(L_out) + isnan(R_out) + (abs(L_out) > 64) + (abs(R_out) > 64);\nif (bad > 0) {\npoke(st, 0, 0);\npoke(st, 0, 1);\npoke(st, 0, 2);\npoke(st, 0, 3);\npoke(st, 0, 4);\npoke(st, 0, 5);\npoke(st, 0, 6);\npoke(st, 0, 7);\npoke(st, 0, 8);\npoke(st, 0, 9);\npoke(st, 0, 10);\npoke(st, 0, 11);\npoke(st, 0, 12);\npoke(st, 0, 13);\npoke(st, 0, 14);\npoke(st, 0, 15);\npoke(st, 0, 16);\npoke(st, 0, 17);\npoke(st, 0, 18);\npoke(st, 0, 19);\npoke(st, 0, 20);\npoke(st, 0, 21);\npoke(st, 0, 22);\npoke(st, 0, 23);\npoke(st, 0, 24);\npoke(st, 0, 25);\npoke(st, 0, 26);\npoke(st, 0, 27);\npoke(st, 0, 28);\npoke(st, 0, 29);\npoke(st, 0, 30);\npoke(st, 0, 31);\npoke(st, 0, 32);\npoke(st, 0, 33);\npoke(st, 0, 34);\npoke(st, 0, 35);\npoke(st, 0, 36);\npoke(st, 0, 37);\npoke(st, 0, 38);\npoke(st, 0, 39);\npoke(st, 0, 40);\npoke(st, 0, 41);\npoke(st, 0, 42);\npoke(st, 0, 43);\npoke(st, 0, 44);\npoke(st, 0, 45);\npoke(st, 0, 46);\npoke(st, 0, 47);\npoke(st, 0, 48);\npoke(st, 0, 49);\npoke(st, 0, 50);\npoke(st, 0, 51);\npoke(st, 0, 52);\npoke(st, 0, 53);\npoke(st, 0, 54);\npoke(st, 0, 55);\npoke(st, 0, 56);\npoke(st, 0, 57);\npoke(st, 0, 58);\npoke(st, 0, 59);\npoke(st, 0, 60);\npoke(st, 0, 61);\npoke(st, 0, 62);\npoke(st, 0, 63);\npoke(st, 0, 64);\npoke(st, 0, 65);\npoke(st, 0, 66);\npoke(st, 0, 67);\npoke(st, 0, 68);\npoke(st, 0, 69);\npoke(st, 0, 70);\npoke(st, 0, 71);\npoke(st, 0, 72);\npoke(st, 0, 73);\npoke(st, 0, 74);\npoke(st, 0, 75);\npoke(st, 0, 76);\npoke(st, 0, 77);\npoke(st, 0, 78);\npoke(st, 0, 79);\npoke(st, 0, 80);\npoke(st, 0, 81);\npoke(st, 0, 82);\npoke(st, 0, 83);\npoke(st, 0, 84);\npoke(st, 0, 85);\npoke(st, 0, 86);\npoke(st, 0, 87);\npoke(st, 0, 88);\npoke(st, 0, 89);\npoke(st, 0, 90);\npoke(st, 0, 91);\npoke(st, 0, 92);\npoke(st, 0, 93);\npoke(st, 0, 94);\npoke(st, 0, 95);\npoke(st, 0, 96);\npoke(st, 0, 97);\npoke(st, 0, 98);\npoke(st, 0, 99);\npoke(st, 0, 100);\npoke(st, 0, 101);\npoke(st, 0, 102);\npoke(st, 0, 103);\npoke(st, 0, 104);\npoke(st, 0, 105);\npoke(st, 0, 106);\npoke(st, 0, 107);\npoke(st, 0, 108);\npoke(st, 0, 109);\npoke(st, 0, 110);\npoke(st, 0, 111);\npoke(st, 0, 112);\npoke(st, 0, 113);\npoke(st, 0, 114);\npoke(st, 0, 115);\npoke(st, 0, 116);\npoke(st, 0, 117);\npoke(st, 0, 118);\npoke(st, 0, 119);\npoke(st, 0, 120);\npoke(st, 0, 121);\npoke(st, 0, 122);\npoke(st, 0, 123);\npoke(st, 0, 124);\npoke(st, 0, 125);\npoke(st, 0, 126);\npoke(st, 0, 127);\npoke(st, 0, 128);\npoke(st, 0, 129);\npoke(st, 0, 130);\npoke(st, 0, 131);\npoke(st, 0, 132);\npoke(st, 0, 133);\npoke(st, 0, 134);\npoke(st, 0, 135);\npoke(st, 0, 136);\npoke(st, 0, 137);\npoke(st, 0, 138);\npoke(st, 0, 139);\npoke(st, 0, 140);\npoke(st, 0, 141);\npoke(st, 0, 142);\npoke(st, 0, 143);\npoke(st, 0, 144);\npoke(st, 0, 145);\npoke(st, 0, 146);\npoke(st, 0, 147);\npoke(st, 0, 148);\npoke(st, 0, 149);\npoke(st, 0, 150);\npoke(st, 0, 151);\npoke(st, 0, 152);\npoke(st, 0, 153);\npoke(st, 0, 154);\npoke(st, 0, 155);\npoke(st, 0, 156);\npoke(st, 0, 157);\npoke(st, 0, 158);\npoke(st, 0, 159);\npoke(st, 0, 160);\npoke(st, 0, 161);\npoke(st, 0, 162);\npoke(st, 0, 163);\npoke(st, 0, 164);\npoke(st, 0, 165);\npoke(st, 0, 166);\npoke(st, 0, 167);\npoke(st, 0, 168);\npoke(st, 0, 169);\npoke(st, 0, 170);\npoke(st, 0, 171);\npoke(st, 0, 172);\npoke(st, 0, 173);\npoke(st, 0, 174);\npoke(st, 0, 175);\npoke(st, 0, 176);\npoke(st, 0, 177);\npoke(st, 0, 178);\npoke(st, 0, 179);\npoke(st, 0, 180);\npoke(st, 0, 181);\npoke(st, 0, 182);\npoke(st, 0, 183);\npoke(st, 0, 184);\npoke(st, 0, 185);\npoke(st, 0, 186);\npoke(st, 0, 187);\npoke(st, 0, 188);\npoke(st, 0, 189);\npoke(st, 0, 190);\npoke(st, 0, 191);\npoke(st, 0, 192);\npoke(st, 0, 193);\npoke(st, 0, 194);\npoke(st, 0, 195);\npoke(st, 0, 196);\npoke(st, 0, 197);\npoke(st, 0, 198);\npoke(st, 0, 199);\npoke(st, 0, 200);\npoke(st, 0, 201);\npoke(st, 0, 202);\npoke(st, 0, 203);\npoke(st, 0, 204);\npoke(st, 0, 205);\npoke(st, 0, 206);\npoke(st, 0, 207);\npoke(st, 0, 208);\npoke(st, 0, 209);\npoke(st, 0, 210);\npoke(st, 0, 211);\npoke(st, 0, 212);\npoke(st, 0, 213);\npoke(st, 0, 214);\npoke(st, 0, 215);\npoke(st, 0, 216);\npoke(st, 0, 217);\npoke(st, 0, 218);\npoke(st, 0, 219);\npoke(st, 0, 220);\npoke(st, 0, 221);\npoke(st, 0, 222);\npoke(st, 0, 223);\npoke(st, 0, 224);\npoke(st, 0, 225);\npoke(st, 0, 226);\npoke(st, 0, 227);\npoke(st, 0, 228);\npoke(st, 0, 229);\npoke(st, 0, 230);\npoke(st, 0, 231);\npoke(st, 0, 232);\npoke(st, 0, 233);\npoke(st, 0, 234);\npoke(st, 0, 235);\npoke(st, 0, 236);\npoke(st, 0, 237);\npoke(st, 0, 238);\npoke(st, 0, 239);\npoke(st, 0, 240);\npoke(st, 0, 241);\npoke(st, 0, 242);\npoke(st, 0, 243);\npoke(st, 0, 244);\npoke(st, 0, 245);\npoke(st, 0, 246);\npoke(st, 0, 247);\npoke(st, 0, 248);\npoke(st, 0, 249);\npoke(st, 0, 250);\npoke(st, 0, 251);\npoke(st, 0, 252);\npoke(st, 0, 253);\npoke(st, 0, 254);\npoke(st, 0, 255);\npoke(st, 0, 256);\npoke(st, 0, 257);\npoke(st, 0, 258);\npoke(st, 0, 259);\npoke(st, 0, 260);\npoke(st, 0, 261);\npoke(st, 0, 262);\npoke(st, 0, 263);\npoke(st, 0, 264);\npoke(st, 0, 265);\npoke(st, 0, 266);\npoke(st, 0, 267);\npoke(st, 0, 268);\npoke(st, 0, 269);\npoke(st, 0, 270);\npoke(st, 0, 271);\npoke(st, 0, 272);\npoke(st, 0, 273);\npoke(st, 0, 274);\npoke(st, 0, 275);\npoke(st, 0, 276);\npoke(st, 0, 277);\npoke(st, 0, 278);\npoke(st, 0, 279);\npoke(st, 0, 280);\npoke(st, 0, 281);\npoke(st, 0, 282);\npoke(st, 0, 283);\npoke(st, 0, 284);\npoke(st, 0, 285);\npoke(st, 0, 286);\npoke(st, 0, 287);\npoke(st, 0, 288);\npoke(st, 0, 289);\npoke(st, 0, 290);\npoke(st, 0, 291);\npoke(st, 0, 292);\npoke(st, 0, 293);\npoke(st, 0, 294);\npoke(st, 0, 295);\npoke(st, 0, 296);\npoke(st, 0, 297);\npoke(st, 0, 298);\npoke(st, 0, 299);\npoke(st, 0, 300);\npoke(st, 0, 301);\npoke(st, 0, 302);\npoke(st, 0, 303);\npoke(st, 0, 304);\npoke(st, 0, 305);\npoke(st, 0, 306);\npoke(st, 0, 307);\npoke(st, 0, 308);\npoke(st, 0, 309);\npoke(st, 0, 310);\npoke(st, 0, 311);\npoke(st, 0, 312);\npoke(st, 0, 313);\npoke(st, 0, 314);\npoke(st, 0, 315);\npoke(hb, 0, 0);\npoke(hb, 0, 1);\npoke(hb, 0, 2);\npoke(hb, 0, 3);\npoke(hb, 0, 4);\npoke(hb, 0, 5);\npoke(hb, 0, 6);\npoke(hb, 0, 7);\npoke(hb, 0, 8);\npoke(hb, 0, 9);\npoke(hb, 0, 10);\npoke(hb, 0, 11);\npoke(hb, 0, 12);\npoke(hb, 0, 13);\npoke(hb, 0, 14);\npoke(hb, 0, 15);\npoke(hb, 0, 16);\npoke(hb, 0, 17);\npoke(hb, 0, 18);\npoke(hb, 0, 19);\npoke(hb, 0, 20);\npoke(hb, 0, 21);\npoke(hb, 0, 22);\npoke(hb, 0, 23);\npoke(hb, 0, 24);\npoke(hb, 0, 25);\npoke(hb, 0, 26);\npoke(hb, 0, 27);\npoke(hb, 0, 28);\npoke(hb, 0, 29);\npoke(hb, 0, 30);\npoke(hb, 0, 31);\npoke(hb, 0, 32);\npoke(hb, 0, 33);\npoke(hb, 0, 34);\npoke(hb, 0, 35);\npoke(hb, 0, 36);\npoke(hb, 0, 37);\npoke(hb, 0, 38);\npoke(hb, 0, 39);\npoke(hb, 0, 40);\npoke(hb, 0, 41);\npoke(hb, 0, 42);\npoke(hb, 0, 43);\npoke(hb, 0, 44);\npoke(hb, 0, 45);\npoke(hb, 0, 46);\npoke(hb, 0, 47);\npoke(hb, 0, 48);\npoke(hb, 0, 49);\npoke(hb, 0, 50);\npoke(hb, 0, 51);\npoke(hb, 0, 52);\npoke(hb, 0, 53);\npoke(hb, 0, 54);\npoke(hb, 0, 55);\npoke(hb, 0, 56);\npoke(hb, 0, 57);\npoke(hb, 0, 58);\npoke(hb, 0, 59);\npoke(hb, 0, 60);\npoke(hb, 0, 61);\npoke(hb, 0, 62);\npoke(hb, 0, 63);\npoke(hb, 0, 64);\npoke(hb, 0, 65);\npoke(hb, 0, 66);\npoke(hb, 0, 67);\npoke(hb, 0, 68);\npoke(hb, 0, 69);\npoke(hb, 0, 70);\npoke(hb, 0, 71);\npoke(hb, 0, 72);\npoke(hb, 0, 73);\npoke(hb, 0, 74);\npoke(hb, 0, 75);\npoke(hb, 0, 76);\npoke(hb, 0, 77);\npoke(hb, 0, 78);\npoke(hb, 0, 79);\npoke(hb, 0, 80);\npoke(hb, 0, 81);\npoke(hb, 0, 82);\npoke(hb, 0, 83);\npoke(hb, 0, 84);\npoke(hb, 0, 85);\npoke(hb, 0, 86);\npoke(hb, 0, 87);\npoke(hb, 0, 88);\npoke(hb, 0, 89);\npoke(hb, 0, 90);\npoke(hb, 0, 91);\npoke(hb, 0, 92);\npoke(hb, 0, 93);\npoke(hb, 0, 94);\npoke(hb, 0, 95);\npoke(hb, 0, 96);\npoke(hb, 0, 97);\npoke(hb, 0, 98);\npoke(hb, 0, 99);\npoke(hb, 0, 100);\npoke(hb, 0, 101);\npoke(hb, 0, 102);\npoke(hb, 0, 103);\npoke(hb, 0, 104);\npoke(hb, 0, 105);\npoke(hb, 0, 106);\npoke(hb, 0, 107);\npoke(hb, 0, 108);\npoke(hb, 0, 109);\npoke(hb, 0, 110);\npoke(hb, 0, 111);\npoke(hb, 0, 112);\npoke(hb, 0, 113);\npoke(hb, 0, 114);\npoke(hb, 0, 115);\npoke(hb, 0, 116);\npoke(hb, 0, 117);\npoke(hb, 0, 118);\npoke(hb, 0, 119);\npoke(hb, 0, 120);\npoke(hb, 0, 121);\npoke(hb, 0, 122);\npoke(hb, 0, 123);\npoke(hb, 0, 124);\npoke(hb, 0, 125);\npoke(hb, 0, 126);\npoke(hb, 0, 127);\nL_out = 0;\nR_out = 0;\n}\nout1 = L_out;\nout2 = R_out;\n",
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
								"A 500",
								"C 350",
								"D 700",
								"A 400",
								"A 450"
							],
							"parameter_mmax": 4.0,
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
								"DJM -26",
								"DJM SPINTO -40"
							],
							"parameter_mmax": 2.0,
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
					"num_lines_patching": 2,
					"num_lines_presentation": 2
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
					"text": "50% = 0 dB. DJM: LOW, LOW-MID = MID 1k, HIGH; MID-HIGH e INCROCI solo per ISOLATOR."
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