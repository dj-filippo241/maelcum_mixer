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
					"numoutlets": 10,
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
									"code": "// MC-SEND - prototipo Max P3 (FX-SEND, fx-send-module \u00a72).\n// GENERATO da proto-max/coefficienti/genera_fx.py: non modificare.\n// L'audio del canale passa intatto (out1, out2). EQ2 -> LEVEL ->\n// 4 ASSIGN (rampa 1 ms) -> out3..out10 = bus 1-4, L e R.\n\n// allpass del 1o ordine del halfband; stato in m[i] (x), m[i+1] (y)\nap(m, i, x, c) {\n\ty = c * (x - peek(m, i + 1)) + peek(m, i);\n\tpoke(m, x, i);\n\tpoke(m, y, i + 1);\n\treturn y;\n}\n\n// polo singolo TPT, uscita passa-basso; stato in m[i]\nop1(m, i, x, g) {\n\ts = peek(m, i);\n\tv = (x - s) * g / (1 + g);\n\tlo = v + s;\n\tpoke(m, lo + v, i);\n\treturn lo;\n}\n\n// SVF 2 poli TPT, uscita passa-alto; stato in m[i], m[i+1]; k = 1/Q\nsvhp(m, i, x, g, k) {\n\ts1 = peek(m, i);\n\ts2 = peek(m, i + 1);\n\tfh = (x - (k + g) * s1 - s2) / (1 + g * (k + g));\n\tfb = g * fh + s1;\n\tfl = g * fb + s2;\n\tpoke(m, g * fh + fb, i);\n\tpoke(m, g * fb + fl, i + 1);\n\treturn fh;\n}\n\nParam low(50, min=0, max=100);\nParam high(50, min=0, max=100);\nParam level(0, min=0, max=100);\nParam as1(0, min=0, max=1);\nHistory r_as1(0);\nParam as2(0, min=0, max=1);\nHistory r_as2(0);\nParam as3(0, min=0, max=1);\nHistory r_as3(0);\nParam as4(0, min=0, max=1);\nHistory r_as4(0);\nData sv(4);\nData sa(4);\nData hb(128);\nHistory s_low(50);\nHistory s_high(50);\nHistory s_level(0);\nt10 = exp(-1 / (0.010 * samplerate));\ns_low = low + t10 * (s_low - low);\ns_high = high + t10 * (s_high - high);\ns_level = level + t10 * (s_level - level);\nsr4 = samplerate * 4;\n// EQ2 LOW: dB voluti -> posizione x del pot (fx.low_x)\nldb = (s_low / 100 >= 0.5) * 12.0 * (s_low / 100 - 0.5) + (s_low / 100 < 0.5) * ((s_low / 100 < 0.2) * (-30.0 + 120.0 * (s_low / 100 - 0.0)) + (s_low / 100 >= 0.2) * (-6.0 + 20.0 * (s_low / 100 - 0.2)));\nlgl = pow(10, ldb / 20);\nlx = (32.0 - lgl) / (31.0 * (lgl + 1));\n// EQ2 HIGH: posizione thh del pot (fx.high_thh)\nhth = (s_high / 100 >= 0.5) * 0.5 * pow(10, 0.6 * (s_high / 100 - 0.5)) + (s_high / 100 < 0.5) * (s_high / 100 >= 0.3) * 0.5 * pow(10, -3.75 * (0.5 - s_high / 100)) + (s_high / 100 < 0.3) * 0.2963799016731538 * s_high / 100;\nlra = 31000.0 * lx + 0.001;\nlrb = 31000.0 * (1 - lx) + 0.001;\nala = 1000.0 / (1000.0 + lrb);\ngla = 1 / (2 * sr4 * lrb * 5.6e-08);\nalb = (1000.0 + lra) / 1000.0;\nglb = (1000.0 + lra) / (2 * sr4 * 1000.0 * lra * 5.6e-08);\nlgk = (1000.0 + lrb) / (1000.0 + lra);\nhr1 = 10000.0 * hth + 0.001;\nhr2 = 10000.0 * (1 - hth) + 0.001;\nhk = (1 / hr2 - 1 / hr1) / (1 / hr1 + 1 / hr2 + 2.004008016032064e-05);\nghp = tan(13827.674747047453 / sr4);\nkhp = 2.892749557082327;\ntv = s_level / 100;\nlev = (tv <= 0.5) * 0.2 * tv + (tv > 0.5) * (0.1 + 1.8 * (tv - 0.5));\npr = 1 / (0.001 * samplerate);\nr_as1 = r_as1 + min(max(as1 - r_as1, -pr), pr);\nr_as2 = r_as2 + min(max(as2 - r_as2, -pr), pr);\nr_as3 = r_as3 + min(max(as3 - r_as3, -pr), pr);\nr_as4 = r_as4 + min(max(as4 - r_as4, -pr), pr);\n// ===== lato L =====\nL_e = in1;\nL_o = in1;\nL_e = ap(hb, 0, L_e, 0.019059005558478156);\nL_e = ap(hb, 4, L_e, 0.1559582483500435);\nL_e = ap(hb, 8, L_e, 0.3650536901969154);\nL_e = ap(hb, 12, L_e, 0.5755010797915323);\nL_e = ap(hb, 16, L_e, 0.7526447471286863);\nL_e = ap(hb, 20, L_e, 0.8980636464339091);\nL_o = ap(hb, 2, L_o, 0.07350243453590219);\nL_o = ap(hb, 6, L_o, 0.25649919975582064);\nL_o = ap(hb, 10, L_o, 0.47327898479453656);\nL_o = ap(hb, 14, L_o, 0.6688095014357188);\nL_o = ap(hb, 18, L_o, 0.8282265929955738);\nL_o = ap(hb, 22, L_o, 0.9656701590349398);\nL_u0 = L_e;\nL_u1 = L_e;\nL_u0 = ap(hb, 24, L_u0, 0.04245470986526787);\nL_u0 = ap(hb, 28, L_u0, 0.39331989319033134);\nL_u1 = ap(hb, 26, L_u1, 0.17073985049750015);\nL_u1 = ap(hb, 30, L_u1, 0.7457135887202412);\nL_u2 = L_o;\nL_u3 = L_o;\nL_u2 = ap(hb, 24, L_u2, 0.04245470986526787);\nL_u2 = ap(hb, 28, L_u2, 0.39331989319033134);\nL_u3 = ap(hb, 26, L_u3, 0.17073985049750015);\nL_u3 = ap(hb, 30, L_u3, 0.7457135887202412);\neq = L_u0;\neq = ala * eq + (1 - ala) * op1(sa, 0, eq, gla);\neq = alb * eq + (1 - alb) * op1(sa, 1, eq, glb);\neq = lgk * eq;\neq = eq + hk * svhp(sv, 0, eq, ghp, khp);\nL_y0 = eq;\neq = L_u1;\neq = ala * eq + (1 - ala) * op1(sa, 0, eq, gla);\neq = alb * eq + (1 - alb) * op1(sa, 1, eq, glb);\neq = lgk * eq;\neq = eq + hk * svhp(sv, 0, eq, ghp, khp);\nL_y1 = eq;\neq = L_u2;\neq = ala * eq + (1 - ala) * op1(sa, 0, eq, gla);\neq = alb * eq + (1 - alb) * op1(sa, 1, eq, glb);\neq = lgk * eq;\neq = eq + hk * svhp(sv, 0, eq, ghp, khp);\nL_y2 = eq;\neq = L_u3;\neq = ala * eq + (1 - ala) * op1(sa, 0, eq, gla);\neq = alb * eq + (1 - alb) * op1(sa, 1, eq, glb);\neq = lgk * eq;\neq = eq + hk * svhp(sv, 0, eq, ghp, khp);\nL_y3 = eq;\nd0 = L_y1;\nd1 = L_y0;\nd0 = ap(hb, 32, d0, 0.04245470986526787);\nd0 = ap(hb, 36, d0, 0.39331989319033134);\nd1 = ap(hb, 34, d1, 0.17073985049750015);\nd1 = ap(hb, 38, d1, 0.7457135887202412);\nL_v0 = 0.5 * (d0 + d1);\nd0 = L_y3;\nd1 = L_y2;\nd0 = ap(hb, 32, d0, 0.04245470986526787);\nd0 = ap(hb, 36, d0, 0.39331989319033134);\nd1 = ap(hb, 34, d1, 0.17073985049750015);\nd1 = ap(hb, 38, d1, 0.7457135887202412);\nL_v1 = 0.5 * (d0 + d1);\nd0 = L_v1;\nd1 = L_v0;\nd0 = ap(hb, 40, d0, 0.019059005558478156);\nd0 = ap(hb, 44, d0, 0.1559582483500435);\nd0 = ap(hb, 48, d0, 0.3650536901969154);\nd0 = ap(hb, 52, d0, 0.5755010797915323);\nd0 = ap(hb, 56, d0, 0.7526447471286863);\nd0 = ap(hb, 60, d0, 0.8980636464339091);\nd1 = ap(hb, 42, d1, 0.07350243453590219);\nd1 = ap(hb, 46, d1, 0.25649919975582064);\nd1 = ap(hb, 50, d1, 0.47327898479453656);\nd1 = ap(hb, 54, d1, 0.6688095014357188);\nd1 = ap(hb, 58, d1, 0.8282265929955738);\nd1 = ap(hb, 62, d1, 0.9656701590349398);\nL_w = 0.5 * (d0 + d1);\n// ===== lato R =====\nR_e = in2;\nR_o = in2;\nR_e = ap(hb, 64, R_e, 0.019059005558478156);\nR_e = ap(hb, 68, R_e, 0.1559582483500435);\nR_e = ap(hb, 72, R_e, 0.3650536901969154);\nR_e = ap(hb, 76, R_e, 0.5755010797915323);\nR_e = ap(hb, 80, R_e, 0.7526447471286863);\nR_e = ap(hb, 84, R_e, 0.8980636464339091);\nR_o = ap(hb, 66, R_o, 0.07350243453590219);\nR_o = ap(hb, 70, R_o, 0.25649919975582064);\nR_o = ap(hb, 74, R_o, 0.47327898479453656);\nR_o = ap(hb, 78, R_o, 0.6688095014357188);\nR_o = ap(hb, 82, R_o, 0.8282265929955738);\nR_o = ap(hb, 86, R_o, 0.9656701590349398);\nR_u0 = R_e;\nR_u1 = R_e;\nR_u0 = ap(hb, 88, R_u0, 0.04245470986526787);\nR_u0 = ap(hb, 92, R_u0, 0.39331989319033134);\nR_u1 = ap(hb, 90, R_u1, 0.17073985049750015);\nR_u1 = ap(hb, 94, R_u1, 0.7457135887202412);\nR_u2 = R_o;\nR_u3 = R_o;\nR_u2 = ap(hb, 88, R_u2, 0.04245470986526787);\nR_u2 = ap(hb, 92, R_u2, 0.39331989319033134);\nR_u3 = ap(hb, 90, R_u3, 0.17073985049750015);\nR_u3 = ap(hb, 94, R_u3, 0.7457135887202412);\neq = R_u0;\neq = ala * eq + (1 - ala) * op1(sa, 2, eq, gla);\neq = alb * eq + (1 - alb) * op1(sa, 3, eq, glb);\neq = lgk * eq;\neq = eq + hk * svhp(sv, 2, eq, ghp, khp);\nR_y0 = eq;\neq = R_u1;\neq = ala * eq + (1 - ala) * op1(sa, 2, eq, gla);\neq = alb * eq + (1 - alb) * op1(sa, 3, eq, glb);\neq = lgk * eq;\neq = eq + hk * svhp(sv, 2, eq, ghp, khp);\nR_y1 = eq;\neq = R_u2;\neq = ala * eq + (1 - ala) * op1(sa, 2, eq, gla);\neq = alb * eq + (1 - alb) * op1(sa, 3, eq, glb);\neq = lgk * eq;\neq = eq + hk * svhp(sv, 2, eq, ghp, khp);\nR_y2 = eq;\neq = R_u3;\neq = ala * eq + (1 - ala) * op1(sa, 2, eq, gla);\neq = alb * eq + (1 - alb) * op1(sa, 3, eq, glb);\neq = lgk * eq;\neq = eq + hk * svhp(sv, 2, eq, ghp, khp);\nR_y3 = eq;\nd0 = R_y1;\nd1 = R_y0;\nd0 = ap(hb, 96, d0, 0.04245470986526787);\nd0 = ap(hb, 100, d0, 0.39331989319033134);\nd1 = ap(hb, 98, d1, 0.17073985049750015);\nd1 = ap(hb, 102, d1, 0.7457135887202412);\nR_v0 = 0.5 * (d0 + d1);\nd0 = R_y3;\nd1 = R_y2;\nd0 = ap(hb, 96, d0, 0.04245470986526787);\nd0 = ap(hb, 100, d0, 0.39331989319033134);\nd1 = ap(hb, 98, d1, 0.17073985049750015);\nd1 = ap(hb, 102, d1, 0.7457135887202412);\nR_v1 = 0.5 * (d0 + d1);\nd0 = R_v1;\nd1 = R_v0;\nd0 = ap(hb, 104, d0, 0.019059005558478156);\nd0 = ap(hb, 108, d0, 0.1559582483500435);\nd0 = ap(hb, 112, d0, 0.3650536901969154);\nd0 = ap(hb, 116, d0, 0.5755010797915323);\nd0 = ap(hb, 120, d0, 0.7526447471286863);\nd0 = ap(hb, 124, d0, 0.8980636464339091);\nd1 = ap(hb, 106, d1, 0.07350243453590219);\nd1 = ap(hb, 110, d1, 0.25649919975582064);\nd1 = ap(hb, 114, d1, 0.47327898479453656);\nd1 = ap(hb, 118, d1, 0.6688095014357188);\nd1 = ap(hb, 122, d1, 0.8282265929955738);\nd1 = ap(hb, 126, d1, 0.9656701590349398);\nR_w = 0.5 * (d0 + d1);\nout1 = in1;\nout2 = in2;\nout3 = r_as1 * lev * L_w;\nout4 = r_as1 * lev * R_w;\nout5 = r_as2 * lev * L_w;\nout6 = r_as2 * lev * R_w;\nout7 = r_as3 * lev * L_w;\nout8 = r_as3 * lev * R_w;\nout9 = r_as4 * lev * L_w;\nout10 = r_as4 * lev * R_w;\n",
									"numinlets": 2,
									"numoutlets": 10,
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
					"id": "obj-c0-pre",
					"maxclass": "newobj",
					"text": "prepend low",
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
					"id": "obj-c1-pre",
					"maxclass": "newobj",
					"text": "prepend high",
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
							"parameter_longname": "LEVEL",
							"parameter_shortname": "LEVEL",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								0.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "LEVEL",
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
					"text": "prepend level",
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
					"maxclass": "live.tab",
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
						64,
						42,
						18
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "FX1",
							"parameter_shortname": "FX1",
							"parameter_initial_enable": 1,
							"parameter_type": 2,
							"parameter_enum": [
								"-",
								"ON"
							],
							"parameter_mmax": 1.0,
							"parameter_initial": [
								0
							],
							"parameter_unitstyle": 0
						}
					},
					"varname": "FX1",
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
					"id": "obj-c3-pre",
					"maxclass": "newobj",
					"text": "prepend as1",
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
					"maxclass": "live.tab",
					"parameter_enable": 1,
					"patching_rect": [
						460,
						80,
						44,
						48
					],
					"presentation": 1,
					"presentation_rect": [
						54,
						64,
						42,
						18
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "FX2",
							"parameter_shortname": "FX2",
							"parameter_initial_enable": 1,
							"parameter_type": 2,
							"parameter_enum": [
								"-",
								"ON"
							],
							"parameter_mmax": 1.0,
							"parameter_initial": [
								0
							],
							"parameter_unitstyle": 0
						}
					},
					"varname": "FX2",
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
					"id": "obj-c4-pre",
					"maxclass": "newobj",
					"text": "prepend as2",
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
					"maxclass": "live.tab",
					"parameter_enable": 1,
					"patching_rect": [
						550,
						80,
						44,
						48
					],
					"presentation": 1,
					"presentation_rect": [
						100,
						64,
						42,
						18
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "FX3",
							"parameter_shortname": "FX3",
							"parameter_initial_enable": 1,
							"parameter_type": 2,
							"parameter_enum": [
								"-",
								"ON"
							],
							"parameter_mmax": 1.0,
							"parameter_initial": [
								0
							],
							"parameter_unitstyle": 0
						}
					},
					"varname": "FX3",
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
					"id": "obj-c5-pre",
					"maxclass": "newobj",
					"text": "prepend as3",
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
					"maxclass": "live.tab",
					"parameter_enable": 1,
					"patching_rect": [
						640,
						80,
						44,
						48
					],
					"presentation": 1,
					"presentation_rect": [
						146,
						64,
						42,
						18
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "FX4",
							"parameter_shortname": "FX4",
							"parameter_initial_enable": 1,
							"parameter_type": 2,
							"parameter_enum": [
								"-",
								"ON"
							],
							"parameter_mmax": 1.0,
							"parameter_initial": [
								0
							],
							"parameter_unitstyle": 0
						}
					},
					"varname": "FX4",
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
					"id": "obj-c6-pre",
					"maxclass": "newobj",
					"text": "prepend as4",
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
					"id": "obj-nota25",
					"maxclass": "live.comment",
					"numinlets": 1,
					"numoutlets": 0,
					"presentation": 1,
					"presentation_rect": [
						8,
						90,
						200,
						40
					],
					"patching_rect": [
						20,
						760,
						200,
						18
					],
					"text": "Presa post-EQ, pre-filtro, pre-fader: tra MC-CHANNEL e MC-FILTRO. L'audio del canale passa intatto."
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
			}
		],
		"parameters": {
			"obj-c0": [
				"EQ LOW",
				"EQ LOW",
				0
			],
			"obj-c1": [
				"EQ HIGH",
				"EQ HIGH",
				0
			],
			"obj-c2": [
				"LEVEL",
				"LEVEL",
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