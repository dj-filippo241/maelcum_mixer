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
			1200.0,
			800.0
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
						700,
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
					"numoutlets": 11,
					"outlettype": [
						"signal",
						"signal",
						"signal",
						"signal",
						"signal",
						"signal",
						"signal",
						"signal",
						"signal",
						"signal",
						"signal"
					],
					"patching_rect": [
						20,
						400,
						600,
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
							760.0,
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
									"id": "obj-i0",
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
									"id": "obj-i1",
									"maxclass": "newobj",
									"text": "in 2",
									"numinlets": 0,
									"numoutlets": 1,
									"outlettype": [
										""
									],
									"patching_rect": [
										80,
										20,
										30,
										22
									]
								}
							},
							{
								"box": {
									"id": "obj-cb",
									"maxclass": "codebox",
									"code": "// MC-MIC - prototipo Max P4 (mic-mono-moduli \u00a72-\u00a75, REV dec. 111).\n// GENERATO da proto-max/coefficienti/genera_mic.py: non modificare.\n// in1 = microfono (scheda audio col preamp al minimo); in2 ignorato.\n// INA +30 dB (rail) -> passa-alto 60 Hz -> GAIN 0...+30 dB (rail) ->\n// PRE (LED) -> EQ2 (rail) -> MUTE (1 ms) -> out1 = out2 (mono\n// centrato); out3..out10 = SEND ai bus 1-4 (L, R); out11 = LED\n// (0 spento, 1 verde, 2 giallo, 3 rosso).\n\n// allpass del 1o ordine del halfband; stato in m[i] (x), m[i+1] (y)\nap(m, i, x, c) {\n\ty = c * (x - peek(m, i + 1)) + peek(m, i);\n\tpoke(m, x, i);\n\tpoke(m, y, i + 1);\n\treturn y;\n}\n\n// polo singolo TPT, uscita passa-basso; stato in m[i]\nop1(m, i, x, g) {\n\ts = peek(m, i);\n\tv = (x - s) * g / (1 + g);\n\tlo = v + s;\n\tpoke(m, lo + v, i);\n\treturn lo;\n}\n\n// SVF 2 poli TPT, uscita passa-alto; stato in m[i], m[i+1]; k = 1/Q\nsvhp(m, i, x, g, k) {\n\ts1 = peek(m, i);\n\ts2 = peek(m, i + 1);\n\tfh = (x - (k + g) * s1 - s2) / (1 + g * (k + g));\n\tfb = g * fh + s1;\n\tfl = g * fb + s2;\n\tpoke(m, g * fh + fb, i);\n\tpoke(m, g * fb + fl, i + 1);\n\treturn fh;\n}\n\nParam gain(0, min=0, max=100);\nParam low(50, min=0, max=100);\nParam high(50, min=0, max=100);\nParam snd1(0, min=0, max=100);\nParam snd2(0, min=0, max=100);\nParam snd3(0, min=0, max=100);\nParam snd4(0, min=0, max=100);\nParam mute(0, min=0, max=1);\nHistory mrm(0);\nHistory lenv(0);\nHistory llat(0);\nData sv(4);\nData sa(2);\nData hb(64);\nHistory s_gain(0.0);\nHistory s_low(50.0);\nHistory s_high(50.0);\nHistory s_snd1(0.0);\nHistory s_snd2(0.0);\nHistory s_snd3(0.0);\nHistory s_snd4(0.0);\nt10 = exp(-1 / (0.010 * samplerate));\ns_gain = gain + t10 * (s_gain - gain);\ns_low = low + t10 * (s_low - low);\ns_high = high + t10 * (s_high - high);\ns_snd1 = snd1 + t10 * (s_snd1 - snd1);\ns_snd2 = snd2 + t10 * (s_snd2 - snd2);\ns_snd3 = snd3 + t10 * (s_snd3 - snd3);\ns_snd4 = snd4 + t10 * (s_snd4 - snd4);\nsr4 = samplerate * 4;\n// GAIN: stadio 2 col pot lineare (mic.g2)\ntgn = s_gain / 100;\ngst = (5360.0 + tgn * 5000.0) / (332.0 + (1 - tgn) * 5000.0);\n// passa-alto Sallen-Key 60 Hz (mic.hpf_w0_q)\ngpa = tan(190.18471790923815 / sr4);\nkpa = 1.414213562373095;\n// EQ2 LOW: dB voluti -> posizione x del pot (fx.low_x)\nldb = (s_low / 100 >= 0.5) * 12.0 * (s_low / 100 - 0.5) + (s_low / 100 < 0.5) * ((s_low / 100 < 0.2) * (-30.0 + 120.0 * (s_low / 100 - 0.0)) + (s_low / 100 >= 0.2) * (-6.0 + 20.0 * (s_low / 100 - 0.2)));\nlgl = pow(10, ldb / 20);\nlx = (32.0 - lgl) / (31.0 * (lgl + 1));\n// EQ2 HIGH: posizione thh del pot (fx.high_thh)\nhth = (s_high / 100 >= 0.5) * 0.5 * pow(10, 0.6 * (s_high / 100 - 0.5)) + (s_high / 100 < 0.5) * (s_high / 100 >= 0.3) * 0.5 * pow(10, -3.75 * (0.5 - s_high / 100)) + (s_high / 100 < 0.3) * 0.2963799016731538 * s_high / 100;\nlra = 31000.0 * lx + 0.001;\nlrb = 31000.0 * (1 - lx) + 0.001;\nala = 1000.0 / (1000.0 + lrb);\ngla = 1 / (2 * sr4 * lrb * 5.6e-08);\nalb = (1000.0 + lra) / 1000.0;\nglb = (1000.0 + lra) / (2 * sr4 * 1000.0 * lra * 5.6e-08);\nlgk = (1000.0 + lrb) / (1000.0 + lra);\nhr1 = 10000.0 * hth + 0.001;\nhr2 = 10000.0 * (1 - hth) + 0.001;\nhk = (1 / hr2 - 1 / hr1) / (1 / hr1 + 1 / hr2 + 2.004008016032064e-05);\nghp = tan(13827.674747047453 / sr4);\nkhp = 2.892749557082327;\n// MUTE: rampa 1 ms, lineare in dB fino a -100 dB, poi zero\npmu = 1 / (0.001 * samplerate);\nmrm = mrm + min(max(mute - mrm, -pmu), pmu);\ngmu = pow(10, -5 * mrm) * (mrm < 1);\n// SEND: pot curva A (fx.level_send)\nts1 = s_snd1 / 100;\nls1 = (ts1 <= 0.5) * 0.2 * ts1 + (ts1 > 0.5) * (0.1 + 1.8 * (ts1 - 0.5));\nts2 = s_snd2 / 100;\nls2 = (ts2 <= 0.5) * 0.2 * ts2 + (ts2 > 0.5) * (0.1 + 1.8 * (ts2 - 0.5));\nts3 = s_snd3 / 100;\nls3 = (ts3 <= 0.5) * 0.2 * ts3 + (ts3 > 0.5) * (0.1 + 1.8 * (ts3 - 0.5));\nts4 = s_snd4 / 100;\nls4 = (ts4 <= 0.5) * 0.2 * ts4 + (ts4 > 0.5) * (0.1 + 1.8 * (ts4 - 0.5));\n// ingresso: 1,0 = 3.0873 V al microfono; uscita: 1,0 = 4.3609 V\nM_e = in1;\nM_o = in1;\nM_e = ap(hb, 0, M_e, 0.019059005558478156);\nM_e = ap(hb, 4, M_e, 0.1559582483500435);\nM_e = ap(hb, 8, M_e, 0.3650536901969154);\nM_e = ap(hb, 12, M_e, 0.5755010797915323);\nM_e = ap(hb, 16, M_e, 0.7526447471286863);\nM_e = ap(hb, 20, M_e, 0.8980636464339091);\nM_o = ap(hb, 2, M_o, 0.07350243453590219);\nM_o = ap(hb, 6, M_o, 0.25649919975582064);\nM_o = ap(hb, 10, M_o, 0.47327898479453656);\nM_o = ap(hb, 14, M_o, 0.6688095014357188);\nM_o = ap(hb, 18, M_o, 0.8282265929955738);\nM_o = ap(hb, 22, M_o, 0.9656701590349398);\nM_u0 = M_e;\nM_u1 = M_e;\nM_u0 = ap(hb, 24, M_u0, 0.04245470986526787);\nM_u0 = ap(hb, 28, M_u0, 0.39331989319033134);\nM_u1 = ap(hb, 26, M_u1, 0.17073985049750015);\nM_u1 = ap(hb, 30, M_u1, 0.7457135887202412);\nM_u2 = M_o;\nM_u3 = M_o;\nM_u2 = ap(hb, 24, M_u2, 0.04245470986526787);\nM_u2 = ap(hb, 28, M_u2, 0.39331989319033134);\nM_u3 = ap(hb, 26, M_u3, 0.17073985049750015);\nM_u3 = ap(hb, 30, M_u3, 0.7457135887202412);\nppk = 0;\npv = min(max(91.32528313955623 * M_u0, -13.5), 13.5);\npv = svhp(sv, 2, pv, gpa, kpa);\npv = min(max(gst * pv, -13.5), 13.5);\nppk = max(ppk, abs(pv));\neq = pv / 4.360865946243008;\neq = ala * eq + (1 - ala) * op1(sa, 0, eq, gla);\neq = alb * eq + (1 - alb) * op1(sa, 1, eq, glb);\neq = lgk * eq;\neq = eq + hk * svhp(sv, 0, eq, ghp, khp);\nM_y0 = min(max(eq, -3.7836521927978892), 3.7836521927978892);\npv = min(max(91.32528313955623 * M_u1, -13.5), 13.5);\npv = svhp(sv, 2, pv, gpa, kpa);\npv = min(max(gst * pv, -13.5), 13.5);\nppk = max(ppk, abs(pv));\neq = pv / 4.360865946243008;\neq = ala * eq + (1 - ala) * op1(sa, 0, eq, gla);\neq = alb * eq + (1 - alb) * op1(sa, 1, eq, glb);\neq = lgk * eq;\neq = eq + hk * svhp(sv, 0, eq, ghp, khp);\nM_y1 = min(max(eq, -3.7836521927978892), 3.7836521927978892);\npv = min(max(91.32528313955623 * M_u2, -13.5), 13.5);\npv = svhp(sv, 2, pv, gpa, kpa);\npv = min(max(gst * pv, -13.5), 13.5);\nppk = max(ppk, abs(pv));\neq = pv / 4.360865946243008;\neq = ala * eq + (1 - ala) * op1(sa, 0, eq, gla);\neq = alb * eq + (1 - alb) * op1(sa, 1, eq, glb);\neq = lgk * eq;\neq = eq + hk * svhp(sv, 0, eq, ghp, khp);\nM_y2 = min(max(eq, -3.7836521927978892), 3.7836521927978892);\npv = min(max(91.32528313955623 * M_u3, -13.5), 13.5);\npv = svhp(sv, 2, pv, gpa, kpa);\npv = min(max(gst * pv, -13.5), 13.5);\nppk = max(ppk, abs(pv));\neq = pv / 4.360865946243008;\neq = ala * eq + (1 - ala) * op1(sa, 0, eq, gla);\neq = alb * eq + (1 - alb) * op1(sa, 1, eq, glb);\neq = lgk * eq;\neq = eq + hk * svhp(sv, 0, eq, ghp, khp);\nM_y3 = min(max(eq, -3.7836521927978892), 3.7836521927978892);\nd0 = M_y1;\nd1 = M_y0;\nd0 = ap(hb, 32, d0, 0.04245470986526787);\nd0 = ap(hb, 36, d0, 0.39331989319033134);\nd1 = ap(hb, 34, d1, 0.17073985049750015);\nd1 = ap(hb, 38, d1, 0.7457135887202412);\nM_v0 = 0.5 * (d0 + d1);\nd0 = M_y3;\nd1 = M_y2;\nd0 = ap(hb, 32, d0, 0.04245470986526787);\nd0 = ap(hb, 36, d0, 0.39331989319033134);\nd1 = ap(hb, 34, d1, 0.17073985049750015);\nd1 = ap(hb, 38, d1, 0.7457135887202412);\nM_v1 = 0.5 * (d0 + d1);\nd0 = M_v1;\nd1 = M_v0;\nd0 = ap(hb, 40, d0, 0.019059005558478156);\nd0 = ap(hb, 44, d0, 0.1559582483500435);\nd0 = ap(hb, 48, d0, 0.3650536901969154);\nd0 = ap(hb, 52, d0, 0.5755010797915323);\nd0 = ap(hb, 56, d0, 0.7526447471286863);\nd0 = ap(hb, 60, d0, 0.8980636464339091);\nd1 = ap(hb, 42, d1, 0.07350243453590219);\nd1 = ap(hb, 46, d1, 0.25649919975582064);\nd1 = ap(hb, 50, d1, 0.47327898479453656);\nd1 = ap(hb, 54, d1, 0.6688095014357188);\nd1 = ap(hb, 58, d1, 0.8282265929955738);\nd1 = ap(hb, 62, d1, 0.9656701590349398);\nM_w = 0.5 * (d0 + d1);\nmo = gmu * M_w;\n// LED al nodo PRE: picco dei 4 campioni, rilascio 0,3 s,\n// rosso con latch 0,5 s (mic.Led)\nlcr = exp(-1 / (0.3 * samplerate));\nlenv = max(ppk, lcr * lenv);\nllat = (ppk >= 7.754838122143846) * 0.5 + (ppk < 7.754838122143846) * max(llat - 1 / samplerate, 0);\nlst = (llat > 0) * 3 + (llat <= 0) * ((lenv >= 0.549000495715314) + (lenv >= 3.886625865664586));\nout1 = mo;\nout2 = mo;\nout3 = ls1 * mo;\nout4 = ls1 * mo;\nout5 = ls2 * mo;\nout6 = ls2 * mo;\nout7 = ls3 * mo;\nout8 = ls3 * mo;\nout9 = ls4 * mo;\nout10 = ls4 * mo;\nout11 = lst;\n",
									"numinlets": 2,
									"numoutlets": 11,
									"outlettype": [
										"",
										"",
										"",
										"",
										"",
										"",
										"",
										"",
										"",
										"",
										""
									],
									"fontface": 0,
									"fontname": "<Monospaced>",
									"fontsize": 12.0,
									"patching_rect": [
										20,
										60,
										700,
										500
									]
								}
							},
							{
								"box": {
									"id": "obj-o0",
									"maxclass": "newobj",
									"text": "out 1",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										20,
										580,
										40,
										22
									]
								}
							},
							{
								"box": {
									"id": "obj-o1",
									"maxclass": "newobj",
									"text": "out 2",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										75,
										580,
										40,
										22
									]
								}
							},
							{
								"box": {
									"id": "obj-o2",
									"maxclass": "newobj",
									"text": "out 3",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										130,
										580,
										40,
										22
									]
								}
							},
							{
								"box": {
									"id": "obj-o3",
									"maxclass": "newobj",
									"text": "out 4",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										185,
										580,
										40,
										22
									]
								}
							},
							{
								"box": {
									"id": "obj-o4",
									"maxclass": "newobj",
									"text": "out 5",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										240,
										580,
										40,
										22
									]
								}
							},
							{
								"box": {
									"id": "obj-o5",
									"maxclass": "newobj",
									"text": "out 6",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										295,
										580,
										40,
										22
									]
								}
							},
							{
								"box": {
									"id": "obj-o6",
									"maxclass": "newobj",
									"text": "out 7",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										350,
										580,
										40,
										22
									]
								}
							},
							{
								"box": {
									"id": "obj-o7",
									"maxclass": "newobj",
									"text": "out 8",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										405,
										580,
										40,
										22
									]
								}
							},
							{
								"box": {
									"id": "obj-o8",
									"maxclass": "newobj",
									"text": "out 9",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										460,
										580,
										40,
										22
									]
								}
							},
							{
								"box": {
									"id": "obj-o9",
									"maxclass": "newobj",
									"text": "out 10",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										515,
										580,
										40,
										22
									]
								}
							},
							{
								"box": {
									"id": "obj-o10",
									"maxclass": "newobj",
									"text": "out 11",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										570,
										580,
										40,
										22
									]
								}
							}
						],
						"lines": [
							{
								"patchline": {
									"destination": [
										"obj-cb",
										0
									],
									"source": [
										"obj-i0",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-cb",
										1
									],
									"source": [
										"obj-i1",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-o0",
										0
									],
									"source": [
										"obj-cb",
										0
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-o1",
										0
									],
									"source": [
										"obj-cb",
										1
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-o2",
										0
									],
									"source": [
										"obj-cb",
										2
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-o3",
										0
									],
									"source": [
										"obj-cb",
										3
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-o4",
										0
									],
									"source": [
										"obj-cb",
										4
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-o5",
										0
									],
									"source": [
										"obj-cb",
										5
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-o6",
										0
									],
									"source": [
										"obj-cb",
										6
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-o7",
										0
									],
									"source": [
										"obj-cb",
										7
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-o8",
										0
									],
									"source": [
										"obj-cb",
										8
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-o9",
										0
									],
									"source": [
										"obj-cb",
										9
									]
								}
							},
							{
								"patchline": {
									"destination": [
										"obj-o10",
										0
									],
									"source": [
										"obj-cb",
										10
									]
								}
							}
						]
					}
				}
			},
			{
				"box": {
					"id": "obj-s0L",
					"maxclass": "newobj",
					"text": "send~ mcfx_b1L",
					"numinlets": 1,
					"numoutlets": 0,
					"outlettype": [],
					"patching_rect": [
						20,
						460,
						100,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-s0R",
					"maxclass": "newobj",
					"text": "send~ mcfx_b1R",
					"numinlets": 1,
					"numoutlets": 0,
					"outlettype": [],
					"patching_rect": [
						130,
						460,
						100,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-s1L",
					"maxclass": "newobj",
					"text": "send~ mcfx_b2L",
					"numinlets": 1,
					"numoutlets": 0,
					"outlettype": [],
					"patching_rect": [
						240,
						460,
						100,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-s1R",
					"maxclass": "newobj",
					"text": "send~ mcfx_b2R",
					"numinlets": 1,
					"numoutlets": 0,
					"outlettype": [],
					"patching_rect": [
						350,
						460,
						100,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-s2L",
					"maxclass": "newobj",
					"text": "send~ mcfx_b3L",
					"numinlets": 1,
					"numoutlets": 0,
					"outlettype": [],
					"patching_rect": [
						460,
						460,
						100,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-s2R",
					"maxclass": "newobj",
					"text": "send~ mcfx_b3R",
					"numinlets": 1,
					"numoutlets": 0,
					"outlettype": [],
					"patching_rect": [
						570,
						460,
						100,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-s3L",
					"maxclass": "newobj",
					"text": "send~ mcfx_b4L",
					"numinlets": 1,
					"numoutlets": 0,
					"outlettype": [],
					"patching_rect": [
						680,
						460,
						100,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-s3R",
					"maxclass": "newobj",
					"text": "send~ mcfx_b4R",
					"numinlets": 1,
					"numoutlets": 0,
					"outlettype": [],
					"patching_rect": [
						790,
						460,
						100,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-c0",
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
						54,
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
								0.0
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
					"id": "obj-c0-pre",
					"maxclass": "newobj",
					"text": "prepend gain",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						100,
						140,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-c1",
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
						68,
						8,
						54,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "EQ LOW",
							"parameter_shortname": "EQ LOW",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								50.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "EQ LOW",
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
					"id": "obj-c1-pre",
					"maxclass": "newobj",
					"text": "prepend low",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						190,
						140,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-c2",
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
						128,
						8,
						54,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "EQ HIGH",
							"parameter_shortname": "EQ HIGH",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								50.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "EQ HIGH",
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
					"id": "obj-c2-pre",
					"maxclass": "newobj",
					"text": "prepend high",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						280,
						140,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-c3",
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
						8,
						70,
						54,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "FX1",
							"parameter_shortname": "FX1",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								0.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "FX1",
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
					"id": "obj-c3-pre",
					"maxclass": "newobj",
					"text": "prepend snd1",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						370,
						140,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-c4",
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
						68,
						70,
						54,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "FX2",
							"parameter_shortname": "FX2",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								0.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "FX2",
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
					"id": "obj-c4-pre",
					"maxclass": "newobj",
					"text": "prepend snd2",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						460,
						140,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-c5",
					"maxclass": "live.dial",
					"parameter_enable": 1,
					"patching_rect": [
						550,
						80,
						44,
						48
					],
					"presentation": 1,
					"presentation_rect": [
						128,
						70,
						54,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "FX3",
							"parameter_shortname": "FX3",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								0.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "FX3",
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
					"id": "obj-c5-pre",
					"maxclass": "newobj",
					"text": "prepend snd3",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						550,
						140,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-c6",
					"maxclass": "live.dial",
					"parameter_enable": 1,
					"patching_rect": [
						640,
						80,
						44,
						48
					],
					"presentation": 1,
					"presentation_rect": [
						188,
						70,
						54,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "FX4",
							"parameter_shortname": "FX4",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								0.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "FX4",
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
					"id": "obj-c6-pre",
					"maxclass": "newobj",
					"text": "prepend snd4",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						640,
						140,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-c7",
					"maxclass": "live.tab",
					"parameter_enable": 1,
					"patching_rect": [
						730,
						80,
						44,
						48
					],
					"presentation": 1,
					"presentation_rect": [
						190,
						30,
						50,
						22
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "MUTE",
							"parameter_shortname": "MUTE",
							"parameter_initial_enable": 1,
							"parameter_type": 2,
							"parameter_enum": [
								"-",
								"MUTE"
							],
							"parameter_mmax": 1.0,
							"parameter_initial": [
								0
							],
							"parameter_unitstyle": 0
						}
					},
					"varname": "MUTE",
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
					"id": "obj-c7-pre",
					"maxclass": "newobj",
					"text": "prepend mute",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						730,
						140,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-snap",
					"maxclass": "newobj",
					"text": "snapshot~ 30",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"float"
					],
					"patching_rect": [
						900,
						480,
						80,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-int",
					"maxclass": "newobj",
					"text": "i",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"int"
					],
					"patching_rect": [
						900,
						510,
						30,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-chg",
					"maxclass": "newobj",
					"text": "change",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": [
						"",
						"int",
						"int"
					],
					"patching_rect": [
						900,
						540,
						50,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-sel",
					"maxclass": "newobj",
					"text": "sel 0 1 2 3",
					"numinlets": 5,
					"numoutlets": 5,
					"outlettype": [
						"bang",
						"bang",
						"bang",
						"bang",
						""
					],
					"patching_rect": [
						900,
						570,
						100,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-led",
					"maxclass": "panel",
					"numinlets": 1,
					"numoutlets": 0,
					"mode": 0,
					"rounded": 20,
					"bgfillcolor": [
						0.18,
						0.18,
						0.18,
						1.0
					],
					"presentation": 1,
					"presentation_rect": [
						204,
						8,
						18,
						18
					],
					"patching_rect": [
						900,
						680,
						20,
						20
					],
					"varname": "LED"
				}
			},
			{
				"box": {
					"id": "obj-col0",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"text": "bgfillcolor 0.18 0.18 0.18 1.",
					"patching_rect": [
						900,
						620,
						130,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-col1",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"text": "bgfillcolor 0.1 0.85 0.25 1.",
					"patching_rect": [
						1040,
						620,
						130,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-col2",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"text": "bgfillcolor 1. 0.82 0. 1.",
					"patching_rect": [
						1180,
						620,
						130,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-col3",
					"maxclass": "message",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"text": "bgfillcolor 1. 0.1 0.1 1.",
					"patching_rect": [
						1320,
						620,
						130,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-nota36",
					"maxclass": "live.comment",
					"numinlets": 1,
					"numoutlets": 0,
					"presentation": 1,
					"presentation_rect": [
						8,
						124,
						240,
						40
					],
					"patching_rect": [
						20,
						760,
						240,
						18
					],
					"text": "Mic sulla sua traccia, uscita al Master. Preamp della scheda al minimo. LED pre-EQ, prima del MUTE."
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
						"obj-s0L",
						0
					],
					"source": [
						"obj-gen",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-s0R",
						0
					],
					"source": [
						"obj-gen",
						3
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-s1L",
						0
					],
					"source": [
						"obj-gen",
						4
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-s1R",
						0
					],
					"source": [
						"obj-gen",
						5
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-s2L",
						0
					],
					"source": [
						"obj-gen",
						6
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-s2R",
						0
					],
					"source": [
						"obj-gen",
						7
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-s3L",
						0
					],
					"source": [
						"obj-gen",
						8
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-s3R",
						0
					],
					"source": [
						"obj-gen",
						9
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-c0-pre",
						0
					],
					"source": [
						"obj-c0",
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
						"obj-c0-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-c1-pre",
						0
					],
					"source": [
						"obj-c1",
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
						"obj-c1-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-c2-pre",
						0
					],
					"source": [
						"obj-c2",
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
						"obj-c2-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-c3-pre",
						0
					],
					"source": [
						"obj-c3",
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
						"obj-c3-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-c4-pre",
						0
					],
					"source": [
						"obj-c4",
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
						"obj-c4-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-c5-pre",
						0
					],
					"source": [
						"obj-c5",
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
						"obj-c5-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-c6-pre",
						0
					],
					"source": [
						"obj-c6",
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
						"obj-c6-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-c7-pre",
						0
					],
					"source": [
						"obj-c7",
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
						"obj-c7-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-snap",
						0
					],
					"source": [
						"obj-gen",
						10
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-int",
						0
					],
					"source": [
						"obj-snap",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-chg",
						0
					],
					"source": [
						"obj-int",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-sel",
						0
					],
					"source": [
						"obj-chg",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-col0",
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
						"obj-led",
						0
					],
					"source": [
						"obj-col0",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-col1",
						0
					],
					"source": [
						"obj-sel",
						1
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-led",
						0
					],
					"source": [
						"obj-col1",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-col2",
						0
					],
					"source": [
						"obj-sel",
						2
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-led",
						0
					],
					"source": [
						"obj-col2",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-col3",
						0
					],
					"source": [
						"obj-sel",
						3
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-led",
						0
					],
					"source": [
						"obj-col3",
						0
					]
				}
			}
		],
		"parameters": {
			"obj-c0": [
				"GAIN",
				"GAIN",
				0
			],
			"obj-c1": [
				"EQ LOW",
				"EQ LOW",
				0
			],
			"obj-c2": [
				"EQ HIGH",
				"EQ HIGH",
				0
			],
			"obj-c3": [
				"FX1",
				"FX1",
				0
			],
			"obj-c4": [
				"FX2",
				"FX2",
				0
			],
			"obj-c5": [
				"FX3",
				"FX3",
				0
			],
			"obj-c6": [
				"FX4",
				"FX4",
				0
			],
			"obj-c7": [
				"MUTE",
				"MUTE",
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