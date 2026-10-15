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
					"numoutlets": 12,
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
									"code": "// MC-RET - prototipo Max P3 (ritorno FX, fx-module \u00a75 e \u00a77).\n// GENERATO da proto-max/coefficienti/genera_fx.py: non modificare.\n// GAIN (VCA, rail) -> EQ2 (rail) -> meter -> 4 REROUTE pre-fader.\n// out1-2 al fader; out3..out10 = reroute ai bus 1-4 (L, R);\n// out11 meter (1 = +24 dBu), out12 clip (latch 479 ms).\n\n// allpass del 1o ordine del halfband; stato in m[i] (x), m[i+1] (y)\nap(m, i, x, c) {\n\ty = c * (x - peek(m, i + 1)) + peek(m, i);\n\tpoke(m, x, i);\n\tpoke(m, y, i + 1);\n\treturn y;\n}\n\n// polo singolo TPT, uscita passa-basso; stato in m[i]\nop1(m, i, x, g) {\n\ts = peek(m, i);\n\tv = (x - s) * g / (1 + g);\n\tlo = v + s;\n\tpoke(m, lo + v, i);\n\treturn lo;\n}\n\n// SVF 2 poli TPT, uscita passa-alto; stato in m[i], m[i+1]; k = 1/Q\nsvhp(m, i, x, g, k) {\n\ts1 = peek(m, i);\n\ts2 = peek(m, i + 1);\n\tfh = (x - (k + g) * s1 - s2) / (1 + g * (k + g));\n\tfb = g * fh + s1;\n\tfl = g * fb + s2;\n\tpoke(m, g * fh + fb, i);\n\tpoke(m, g * fb + fl, i + 1);\n\treturn fh;\n}\n\nParam gain(50, min=0, max=100);\nParam low(50, min=0, max=100);\nParam high(50, min=0, max=100);\nParam rr1(0, min=0, max=100);\nHistory c_rr1(0);\nParam rr2(0, min=0, max=100);\nHistory c_rr2(0);\nParam rr3(0, min=0, max=100);\nHistory c_rr3(0);\nParam rr4(0, min=0, max=100);\nHistory c_rr4(0);\nHistory menv(0);\nHistory mlat(0);\nData sv(4);\nData sa(4);\nData hb(128);\nHistory s_gain(50);\nHistory s_low(50);\nHistory s_high(50);\nt10 = exp(-1 / (0.010 * samplerate));\ns_gain = gain + t10 * (s_gain - gain);\ns_low = low + t10 * (s_low - low);\ns_high = high + t10 * (s_high - high);\nsr4 = samplerate * 4;\ntg = s_gain / 100;\ngnl = (tg >= 0.5) * pow(10, 2.0 * (tg - 0.5)) + (tg < 0.5) * (tg >= 0.05) * pow(10, -4.444444444444445 * (0.5 - tg)) + (tg < 0.05) * 0.19999999999999998 * tg;\n// EQ2 LOW: dB voluti -> posizione x del pot (fx.low_x)\nldb = (s_low / 100 >= 0.5) * 12.0 * (s_low / 100 - 0.5) + (s_low / 100 < 0.5) * ((s_low / 100 < 0.2) * (-30.0 + 120.0 * (s_low / 100 - 0.0)) + (s_low / 100 >= 0.2) * (-6.0 + 20.0 * (s_low / 100 - 0.2)));\nlgl = pow(10, ldb / 20);\nlx = (32.0 - lgl) / (31.0 * (lgl + 1));\n// EQ2 HIGH: posizione thh del pot (fx.high_thh)\nhth = (s_high / 100 >= 0.5) * 0.5 * pow(10, 0.6 * (s_high / 100 - 0.5)) + (s_high / 100 < 0.5) * (s_high / 100 >= 0.3) * 0.5 * pow(10, -3.75 * (0.5 - s_high / 100)) + (s_high / 100 < 0.3) * 0.2963799016731538 * s_high / 100;\nlra = 31000.0 * lx + 0.001;\nlrb = 31000.0 * (1 - lx) + 0.001;\nala = 1000.0 / (1000.0 + lrb);\ngla = 1 / (2 * sr4 * lrb * 5.6e-08);\nalb = (1000.0 + lra) / 1000.0;\nglb = (1000.0 + lra) / (2 * sr4 * 1000.0 * lra * 5.6e-08);\nlgk = (1000.0 + lrb) / (1000.0 + lra);\nhr1 = 10000.0 * hth + 0.001;\nhr2 = 10000.0 * (1 - hth) + 0.001;\nhk = (1 / hr2 - 1 / hr1) / (1 / hr1 + 1 / hr2 + 2.004008016032064e-05);\nghp = tan(13827.674747047453 / sr4);\nkhp = 2.892749557082327;\n// REROUTE: law a tratti della SPEC \u00a77, CV lisciato 1 ms\nccr = exp(-1 / (0.001 * samplerate));\nq_rr1 = (rr1 / 100 < 0.2) * (-100.0 + 300.0 * (rr1 / 100 - 0.0)) + (rr1 / 100 >= 0.2) * (rr1 / 100 < 0.45) * (-40.0 + 80.0 * (rr1 / 100 - 0.2)) + (rr1 / 100 >= 0.45) * (rr1 / 100 < 0.7) * (-20.0 + 40.00000000000001 * (rr1 / 100 - 0.45)) + (rr1 / 100 >= 0.7) * (rr1 / 100 < 0.85) * (-10.0 + 39.99999999999999 * (rr1 / 100 - 0.7)) + (rr1 / 100 >= 0.85) * (rr1 / 100 < 0.95) * (-4.0 + 30.000000000000007 * (rr1 / 100 - 0.85)) + (rr1 / 100 >= 0.95) * (-1.0 + 19.999999999999982 * (rr1 / 100 - 0.95));\nl_rr1 = pow(10, q_rr1 / 20);\nc_rr1 = l_rr1 + ccr * (c_rr1 - l_rr1);\nq_rr2 = (rr2 / 100 < 0.2) * (-100.0 + 300.0 * (rr2 / 100 - 0.0)) + (rr2 / 100 >= 0.2) * (rr2 / 100 < 0.45) * (-40.0 + 80.0 * (rr2 / 100 - 0.2)) + (rr2 / 100 >= 0.45) * (rr2 / 100 < 0.7) * (-20.0 + 40.00000000000001 * (rr2 / 100 - 0.45)) + (rr2 / 100 >= 0.7) * (rr2 / 100 < 0.85) * (-10.0 + 39.99999999999999 * (rr2 / 100 - 0.7)) + (rr2 / 100 >= 0.85) * (rr2 / 100 < 0.95) * (-4.0 + 30.000000000000007 * (rr2 / 100 - 0.85)) + (rr2 / 100 >= 0.95) * (-1.0 + 19.999999999999982 * (rr2 / 100 - 0.95));\nl_rr2 = pow(10, q_rr2 / 20);\nc_rr2 = l_rr2 + ccr * (c_rr2 - l_rr2);\nq_rr3 = (rr3 / 100 < 0.2) * (-100.0 + 300.0 * (rr3 / 100 - 0.0)) + (rr3 / 100 >= 0.2) * (rr3 / 100 < 0.45) * (-40.0 + 80.0 * (rr3 / 100 - 0.2)) + (rr3 / 100 >= 0.45) * (rr3 / 100 < 0.7) * (-20.0 + 40.00000000000001 * (rr3 / 100 - 0.45)) + (rr3 / 100 >= 0.7) * (rr3 / 100 < 0.85) * (-10.0 + 39.99999999999999 * (rr3 / 100 - 0.7)) + (rr3 / 100 >= 0.85) * (rr3 / 100 < 0.95) * (-4.0 + 30.000000000000007 * (rr3 / 100 - 0.85)) + (rr3 / 100 >= 0.95) * (-1.0 + 19.999999999999982 * (rr3 / 100 - 0.95));\nl_rr3 = pow(10, q_rr3 / 20);\nc_rr3 = l_rr3 + ccr * (c_rr3 - l_rr3);\nq_rr4 = (rr4 / 100 < 0.2) * (-100.0 + 300.0 * (rr4 / 100 - 0.0)) + (rr4 / 100 >= 0.2) * (rr4 / 100 < 0.45) * (-40.0 + 80.0 * (rr4 / 100 - 0.2)) + (rr4 / 100 >= 0.45) * (rr4 / 100 < 0.7) * (-20.0 + 40.00000000000001 * (rr4 / 100 - 0.45)) + (rr4 / 100 >= 0.7) * (rr4 / 100 < 0.85) * (-10.0 + 39.99999999999999 * (rr4 / 100 - 0.7)) + (rr4 / 100 >= 0.85) * (rr4 / 100 < 0.95) * (-4.0 + 30.000000000000007 * (rr4 / 100 - 0.85)) + (rr4 / 100 >= 0.95) * (-1.0 + 19.999999999999982 * (rr4 / 100 - 0.95));\nl_rr4 = pow(10, q_rr4 / 20);\nc_rr4 = l_rr4 + ccr * (c_rr4 - l_rr4);\n// ===== lato L =====\nL_e = in1;\nL_o = in1;\nL_e = ap(hb, 0, L_e, 0.019059005558478156);\nL_e = ap(hb, 4, L_e, 0.1559582483500435);\nL_e = ap(hb, 8, L_e, 0.3650536901969154);\nL_e = ap(hb, 12, L_e, 0.5755010797915323);\nL_e = ap(hb, 16, L_e, 0.7526447471286863);\nL_e = ap(hb, 20, L_e, 0.8980636464339091);\nL_o = ap(hb, 2, L_o, 0.07350243453590219);\nL_o = ap(hb, 6, L_o, 0.25649919975582064);\nL_o = ap(hb, 10, L_o, 0.47327898479453656);\nL_o = ap(hb, 14, L_o, 0.6688095014357188);\nL_o = ap(hb, 18, L_o, 0.8282265929955738);\nL_o = ap(hb, 22, L_o, 0.9656701590349398);\nL_u0 = L_e;\nL_u1 = L_e;\nL_u0 = ap(hb, 24, L_u0, 0.04245470986526787);\nL_u0 = ap(hb, 28, L_u0, 0.39331989319033134);\nL_u1 = ap(hb, 26, L_u1, 0.17073985049750015);\nL_u1 = ap(hb, 30, L_u1, 0.7457135887202412);\nL_u2 = L_o;\nL_u3 = L_o;\nL_u2 = ap(hb, 24, L_u2, 0.04245470986526787);\nL_u2 = ap(hb, 28, L_u2, 0.39331989319033134);\nL_u3 = ap(hb, 26, L_u3, 0.17073985049750015);\nL_u3 = ap(hb, 30, L_u3, 0.7457135887202412);\neq = min(max(gnl * L_u0, -3.7836521927978892), 3.7836521927978892);\neq = ala * eq + (1 - ala) * op1(sa, 0, eq, gla);\neq = alb * eq + (1 - alb) * op1(sa, 1, eq, glb);\neq = lgk * eq;\neq = eq + hk * svhp(sv, 0, eq, ghp, khp);\nL_y0 = min(max(eq, -3.7836521927978892), 3.7836521927978892);\neq = min(max(gnl * L_u1, -3.7836521927978892), 3.7836521927978892);\neq = ala * eq + (1 - ala) * op1(sa, 0, eq, gla);\neq = alb * eq + (1 - alb) * op1(sa, 1, eq, glb);\neq = lgk * eq;\neq = eq + hk * svhp(sv, 0, eq, ghp, khp);\nL_y1 = min(max(eq, -3.7836521927978892), 3.7836521927978892);\neq = min(max(gnl * L_u2, -3.7836521927978892), 3.7836521927978892);\neq = ala * eq + (1 - ala) * op1(sa, 0, eq, gla);\neq = alb * eq + (1 - alb) * op1(sa, 1, eq, glb);\neq = lgk * eq;\neq = eq + hk * svhp(sv, 0, eq, ghp, khp);\nL_y2 = min(max(eq, -3.7836521927978892), 3.7836521927978892);\neq = min(max(gnl * L_u3, -3.7836521927978892), 3.7836521927978892);\neq = ala * eq + (1 - ala) * op1(sa, 0, eq, gla);\neq = alb * eq + (1 - alb) * op1(sa, 1, eq, glb);\neq = lgk * eq;\neq = eq + hk * svhp(sv, 0, eq, ghp, khp);\nL_y3 = min(max(eq, -3.7836521927978892), 3.7836521927978892);\nd0 = L_y1;\nd1 = L_y0;\nd0 = ap(hb, 32, d0, 0.04245470986526787);\nd0 = ap(hb, 36, d0, 0.39331989319033134);\nd1 = ap(hb, 34, d1, 0.17073985049750015);\nd1 = ap(hb, 38, d1, 0.7457135887202412);\nL_v0 = 0.5 * (d0 + d1);\nd0 = L_y3;\nd1 = L_y2;\nd0 = ap(hb, 32, d0, 0.04245470986526787);\nd0 = ap(hb, 36, d0, 0.39331989319033134);\nd1 = ap(hb, 34, d1, 0.17073985049750015);\nd1 = ap(hb, 38, d1, 0.7457135887202412);\nL_v1 = 0.5 * (d0 + d1);\nd0 = L_v1;\nd1 = L_v0;\nd0 = ap(hb, 40, d0, 0.019059005558478156);\nd0 = ap(hb, 44, d0, 0.1559582483500435);\nd0 = ap(hb, 48, d0, 0.3650536901969154);\nd0 = ap(hb, 52, d0, 0.5755010797915323);\nd0 = ap(hb, 56, d0, 0.7526447471286863);\nd0 = ap(hb, 60, d0, 0.8980636464339091);\nd1 = ap(hb, 42, d1, 0.07350243453590219);\nd1 = ap(hb, 46, d1, 0.25649919975582064);\nd1 = ap(hb, 50, d1, 0.47327898479453656);\nd1 = ap(hb, 54, d1, 0.6688095014357188);\nd1 = ap(hb, 58, d1, 0.8282265929955738);\nd1 = ap(hb, 62, d1, 0.9656701590349398);\nL_w = 0.5 * (d0 + d1);\n// ===== lato R =====\nR_e = in2;\nR_o = in2;\nR_e = ap(hb, 64, R_e, 0.019059005558478156);\nR_e = ap(hb, 68, R_e, 0.1559582483500435);\nR_e = ap(hb, 72, R_e, 0.3650536901969154);\nR_e = ap(hb, 76, R_e, 0.5755010797915323);\nR_e = ap(hb, 80, R_e, 0.7526447471286863);\nR_e = ap(hb, 84, R_e, 0.8980636464339091);\nR_o = ap(hb, 66, R_o, 0.07350243453590219);\nR_o = ap(hb, 70, R_o, 0.25649919975582064);\nR_o = ap(hb, 74, R_o, 0.47327898479453656);\nR_o = ap(hb, 78, R_o, 0.6688095014357188);\nR_o = ap(hb, 82, R_o, 0.8282265929955738);\nR_o = ap(hb, 86, R_o, 0.9656701590349398);\nR_u0 = R_e;\nR_u1 = R_e;\nR_u0 = ap(hb, 88, R_u0, 0.04245470986526787);\nR_u0 = ap(hb, 92, R_u0, 0.39331989319033134);\nR_u1 = ap(hb, 90, R_u1, 0.17073985049750015);\nR_u1 = ap(hb, 94, R_u1, 0.7457135887202412);\nR_u2 = R_o;\nR_u3 = R_o;\nR_u2 = ap(hb, 88, R_u2, 0.04245470986526787);\nR_u2 = ap(hb, 92, R_u2, 0.39331989319033134);\nR_u3 = ap(hb, 90, R_u3, 0.17073985049750015);\nR_u3 = ap(hb, 94, R_u3, 0.7457135887202412);\neq = min(max(gnl * R_u0, -3.7836521927978892), 3.7836521927978892);\neq = ala * eq + (1 - ala) * op1(sa, 2, eq, gla);\neq = alb * eq + (1 - alb) * op1(sa, 3, eq, glb);\neq = lgk * eq;\neq = eq + hk * svhp(sv, 2, eq, ghp, khp);\nR_y0 = min(max(eq, -3.7836521927978892), 3.7836521927978892);\neq = min(max(gnl * R_u1, -3.7836521927978892), 3.7836521927978892);\neq = ala * eq + (1 - ala) * op1(sa, 2, eq, gla);\neq = alb * eq + (1 - alb) * op1(sa, 3, eq, glb);\neq = lgk * eq;\neq = eq + hk * svhp(sv, 2, eq, ghp, khp);\nR_y1 = min(max(eq, -3.7836521927978892), 3.7836521927978892);\neq = min(max(gnl * R_u2, -3.7836521927978892), 3.7836521927978892);\neq = ala * eq + (1 - ala) * op1(sa, 2, eq, gla);\neq = alb * eq + (1 - alb) * op1(sa, 3, eq, glb);\neq = lgk * eq;\neq = eq + hk * svhp(sv, 2, eq, ghp, khp);\nR_y2 = min(max(eq, -3.7836521927978892), 3.7836521927978892);\neq = min(max(gnl * R_u3, -3.7836521927978892), 3.7836521927978892);\neq = ala * eq + (1 - ala) * op1(sa, 2, eq, gla);\neq = alb * eq + (1 - alb) * op1(sa, 3, eq, glb);\neq = lgk * eq;\neq = eq + hk * svhp(sv, 2, eq, ghp, khp);\nR_y3 = min(max(eq, -3.7836521927978892), 3.7836521927978892);\nd0 = R_y1;\nd1 = R_y0;\nd0 = ap(hb, 96, d0, 0.04245470986526787);\nd0 = ap(hb, 100, d0, 0.39331989319033134);\nd1 = ap(hb, 98, d1, 0.17073985049750015);\nd1 = ap(hb, 102, d1, 0.7457135887202412);\nR_v0 = 0.5 * (d0 + d1);\nd0 = R_y3;\nd1 = R_y2;\nd0 = ap(hb, 96, d0, 0.04245470986526787);\nd0 = ap(hb, 100, d0, 0.39331989319033134);\nd1 = ap(hb, 98, d1, 0.17073985049750015);\nd1 = ap(hb, 102, d1, 0.7457135887202412);\nR_v1 = 0.5 * (d0 + d1);\nd0 = R_v1;\nd1 = R_v0;\nd0 = ap(hb, 104, d0, 0.019059005558478156);\nd0 = ap(hb, 108, d0, 0.1559582483500435);\nd0 = ap(hb, 112, d0, 0.3650536901969154);\nd0 = ap(hb, 116, d0, 0.5755010797915323);\nd0 = ap(hb, 120, d0, 0.7526447471286863);\nd0 = ap(hb, 124, d0, 0.8980636464339091);\nd1 = ap(hb, 106, d1, 0.07350243453590219);\nd1 = ap(hb, 110, d1, 0.25649919975582064);\nd1 = ap(hb, 114, d1, 0.47327898479453656);\nd1 = ap(hb, 118, d1, 0.6688095014357188);\nd1 = ap(hb, 122, d1, 0.8282265929955738);\nd1 = ap(hb, 126, d1, 0.9656701590349398);\nR_w = 0.5 * (d0 + d1);\n// meter del ritorno: una barra, mono centrato (sistema-metering \u00a71)\nmcr = exp(-1 / (0.3 * samplerate));\nma = max(abs(L_w), abs(R_w)) * 4.360865946243008;\nmenv = max(ma, mcr * menv);\nmlat = (ma >= 15.472936263797646) * 0.479 + (ma < 15.472936263797646) * max(mlat - 1 / samplerate, 0);\nout1 = L_w;\nout2 = R_w;\nout3 = c_rr1 * L_w;\nout4 = c_rr1 * R_w;\nout5 = c_rr2 * L_w;\nout6 = c_rr2 * R_w;\nout7 = c_rr3 * L_w;\nout8 = c_rr3 * R_w;\nout9 = c_rr4 * L_w;\nout10 = c_rr4 * R_w;\nout11 = menv / 17.360920030219035;\nout12 = mlat > 0;\n",
									"numinlets": 2,
									"numoutlets": 12,
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
							},
							{
								"box": {
									"id": "obj-o11",
									"maxclass": "newobj",
									"text": "out 12",
									"numinlets": 1,
									"numoutlets": 0,
									"patching_rect": [
										625,
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
							},
							{
								"patchline": {
									"destination": [
										"obj-o11",
										0
									],
									"source": [
										"obj-cb",
										11
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
							"parameter_longname": "> FX1",
							"parameter_shortname": "> FX1",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								0.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "> FX1",
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
					"text": "prepend rr1",
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
							"parameter_longname": "> FX2",
							"parameter_shortname": "> FX2",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								0.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "> FX2",
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
					"text": "prepend rr2",
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
							"parameter_longname": "> FX3",
							"parameter_shortname": "> FX3",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								0.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "> FX3",
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
					"text": "prepend rr3",
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
							"parameter_longname": "> FX4",
							"parameter_shortname": "> FX4",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								0.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "> FX4",
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
					"text": "prepend rr4",
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
					"id": "obj-met",
					"maxclass": "live.meter~",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"list",
						"list"
					],
					"presentation": 1,
					"presentation_rect": [
						250,
						8,
						14,
						110
					],
					"patching_rect": [
						850,
						480,
						20,
						100
					],
					"display_range": [
						-60.0,
						0.0
					],
					"varname": "METER"
				}
			},
			{
				"box": {
					"id": "obj-clip",
					"maxclass": "live.meter~",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"list",
						"list"
					],
					"presentation": 1,
					"presentation_rect": [
						268,
						8,
						6,
						110
					],
					"patching_rect": [
						880,
						480,
						20,
						100
					],
					"display_range": [
						-60.0,
						0.0
					],
					"varname": "CLIP"
				}
			},
			{
				"box": {
					"id": "obj-nota27",
					"maxclass": "live.comment",
					"numinlets": 1,
					"numoutlets": 0,
					"presentation": 1,
					"presentation_rect": [
						8,
						124,
						280,
						30
					],
					"patching_rect": [
						20,
						760,
						280,
						18
					],
					"text": "REROUTE pre-fader (law SPEC \u00a77). Meter: 0 = +24 dBu, -24 = 0 dBu."
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
						"obj-met",
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
						"obj-clip",
						0
					],
					"source": [
						"obj-gen",
						11
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
				"> FX1",
				"> FX1",
				0
			],
			"obj-c4": [
				"> FX2",
				"> FX2",
				0
			],
			"obj-c5": [
				"> FX3",
				"> FX3",
				0
			],
			"obj-c6": [
				"> FX4",
				"> FX4",
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