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
			600.0
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
						400,
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
									"code": "// MC-5WAY - prototipo Max P2 del 5-way maelcum_mixer.\n// GENERATO da proto-max/coefficienti/genera_5way.py: non modificare.\n// Banca LR4 allineata in fase (5 vie, kill netti), 5 celle a campana,\n// GROWL e NASTRO in parallelo al pulito. Tutto a 4x.\n\n// allpass del 1o ordine del halfband; stato in m[i] (x), m[i+1] (y)\nap(m, i, x, c) {\n\ty = c * (x - peek(m, i + 1)) + peek(m, i);\n\tpoke(m, x, i);\n\tpoke(m, y, i + 1);\n\treturn y;\n}\n\n// SVF 2 poli TPT lineare, uscita LP; stato in m[i], m[i+1]; k = 1/Q\nsvlp(m, i, x, g, k) {\n\ts1 = peek(m, i);\n\ts2 = peek(m, i + 1);\n\tfh = (x - (k + g) * s1 - s2) / (1 + g * (k + g));\n\tfb = g * fh + s1;\n\tfl = g * fb + s2;\n\tpoke(m, g * fh + fb, i);\n\tpoke(m, g * fb + fl, i + 1);\n\treturn fl;\n}\n\n// SVF 2 poli TPT lineare, uscita BP; stato in m[i], m[i+1]; k = 1/Q\nsvbp(m, i, x, g, k) {\n\ts1 = peek(m, i);\n\ts2 = peek(m, i + 1);\n\tfh = (x - (k + g) * s1 - s2) / (1 + g * (k + g));\n\tfb = g * fh + s1;\n\tfl = g * fb + s2;\n\tpoke(m, g * fh + fb, i);\n\tpoke(m, g * fb + fl, i + 1);\n\treturn fb;\n}\n\n// SVF 2 poli TPT lineare, uscita HP; stato in m[i], m[i+1]; k = 1/Q\nsvhp(m, i, x, g, k) {\n\ts1 = peek(m, i);\n\ts2 = peek(m, i + 1);\n\tfh = (x - (k + g) * s1 - s2) / (1 + g * (k + g));\n\tfb = g * fh + s1;\n\tfl = g * fb + s2;\n\tpoke(m, g * fh + fb, i);\n\tpoke(m, g * fb + fl, i + 1);\n\treturn fh;\n}\n\n// passa-alto del 1o ordine TPT (condensatore di accoppiamento)\nhp1(m, i, x, g) {\n\ts = peek(m, i);\n\tv = (x - s) * g / (1 + g);\n\tlo = v + s;\n\tpoke(m, lo + v, i);\n\treturn x - lo;\n}\n\n// clipper del GROWL: 10k in, 22k || (1 diodo + 2,2k) || (3 diodi +\n// 2,2k); Newton sulla tensione dei diodi del ramo che conduce\nclipg(low) {\n\tii = low / 10000.0;\n\tpos = ii >= 0;\n\ta = abs(ii);\n\trr = pos * 2200.568 + (1 - pos) * 2201.704;\n\tnv = pos * 0.04531548 + (1 - pos) * 0.13594644;\n\tvd = nv * log(1 + a / 2.52e-09);\n\tex = exp(vd / nv);\n\tf = 2.52e-09 * (ex - 1) * (1 + rr / 22000.0) + vd / 22000.0 - a;\n\tdf = 2.52e-09 * ex / nv * (1 + rr / 22000.0) + 1 / 22000.0;\n\tvd = vd - f / df;\n\tex = exp(vd / nv);\n\tf = 2.52e-09 * (ex - 1) * (1 + rr / 22000.0) + vd / 22000.0 - a;\n\tdf = 2.52e-09 * ex / nv * (1 + rr / 22000.0) + 1 / 22000.0;\n\tvd = vd - f / df;\n\tex = exp(vd / nv);\n\tf = 2.52e-09 * (ex - 1) * (1 + rr / 22000.0) + vd / 22000.0 - a;\n\tdf = 2.52e-09 * ex / nv * (1 + rr / 22000.0) + 1 / 22000.0;\n\tvd = vd - f / df;\n\tex = exp(vd / nv);\n\tf = 2.52e-09 * (ex - 1) * (1 + rr / 22000.0) + vd / 22000.0 - a;\n\tdf = 2.52e-09 * ex / nv * (1 + rr / 22000.0) + 1 / 22000.0;\n\tvd = vd - f / df;\n\tid = 2.52e-09 * (exp(vd / nv) - 1);\n\treturn 22000.0 * (a - id) * (pos * 2 - 1);\n}\n\n// un passo di Newton sulla corrente del JFET (Shichman-Hodges,\n// saturazione o triodo); drain su Rd e sul sommatore (vc)\njstep(vg, vs2, vc, idd) {\n\tvd = 1455.0392860607237 * (0.012 + vc / 48543.68932038835 - idd);\n\tvs = vs2 + 150.0 * idd;\n\tvov = max(vg - vs - (-3.0), 0);\n\tvds = vd - vs;\n\tsat = vds >= vov;\n\tcl = 1 + 0.006 * vds;\n\tq = vds * (2 * vov - vds);\n\ti = sat * 0.005 * vov * vov * cl + (1 - sat) * 0.005 * q * cl;\n\tdgs = sat * 0.01 * vov * cl + (1 - sat) * 0.01 * vds * cl;\n\tdds = sat * 3e-05 * vov * vov + (1 - sat) * 0.005 * ((2 * vov - 2 * vds) * cl + q * 0.006);\n\tdf = 1 + dgs * 150.0 + dds * (1605.0392860607237);\n\treturn max(idd - (idd - i) / df, 0);\n}\n\nParam k_sub(0, min=0, max=1);\nParam k_kick(0, min=0, max=1);\nParam k_mid(0, min=0, max=1);\nParam k_high(0, min=0, max=1);\nParam k_super(0, min=0, max=1);\nParam g_1(50, min=0, max=100);\nParam g_2(50, min=0, max=100);\nParam g_3(50, min=0, max=100);\nParam g_4(50, min=0, max=100);\nParam g_5(50, min=0, max=100);\nParam p_1(50, min=0, max=100);\nParam p_2(50, min=0, max=100);\nParam p_3(50, min=0, max=100);\nParam p_4(50, min=0, max=100);\nParam p_5(50, min=0, max=100);\nParam w_1(1, min=0, max=2);\nParam w_2(1, min=0, max=2);\nParam w_3(1, min=0, max=2);\nParam w_4(1, min=0, max=2);\nParam w_5(1, min=0, max=2);\nParam growl(0, min=0, max=100);\nParam nastro(0, min=0, max=100);\nParam xo(0, min=0, max=3);\nData sv(112);\nData sa(8);\nData hb(128);\nHistory s_g_1(50);\nHistory s_g_2(50);\nHistory s_g_3(50);\nHistory s_g_4(50);\nHistory s_g_5(50);\nHistory s_p_1(50);\nHistory s_p_2(50);\nHistory s_p_3(50);\nHistory s_p_4(50);\nHistory s_p_5(50);\nHistory s_w_1(1);\nHistory s_w_2(1);\nHistory s_w_3(1);\nHistory s_w_4(1);\nHistory s_w_5(1);\nHistory s_growl(50);\nHistory s_nastro(0);\nHistory s_xo(0);\n\n// manopole lisciate 10 ms; WIDTH 1 ms; CROSSOVER 20 ms; KILL netti\nt1 = exp(-1 / (0.001 * samplerate));\nt10 = exp(-1 / (0.010 * samplerate));\nt20 = exp(-1 / (0.020 * samplerate));\ns_g_1 = g_1 + t10 * (s_g_1 - g_1);\ns_g_2 = g_2 + t10 * (s_g_2 - g_2);\ns_g_3 = g_3 + t10 * (s_g_3 - g_3);\ns_g_4 = g_4 + t10 * (s_g_4 - g_4);\ns_g_5 = g_5 + t10 * (s_g_5 - g_5);\ns_p_1 = p_1 + t10 * (s_p_1 - p_1);\ns_p_2 = p_2 + t10 * (s_p_2 - p_2);\ns_p_3 = p_3 + t10 * (s_p_3 - p_3);\ns_p_4 = p_4 + t10 * (s_p_4 - p_4);\ns_p_5 = p_5 + t10 * (s_p_5 - p_5);\ns_w_1 = w_1 + t1 * (s_w_1 - w_1);\ns_w_2 = w_2 + t1 * (s_w_2 - w_2);\ns_w_3 = w_3 + t1 * (s_w_3 - w_3);\ns_w_4 = w_4 + t1 * (s_w_4 - w_4);\ns_w_5 = w_5 + t1 * (s_w_5 - w_5);\ns_growl = growl + t10 * (s_growl - growl);\ns_nastro = nastro + t10 * (s_nastro - nastro);\ns_xo = xo + t20 * (s_xo - xo);\nsr4 = samplerate * 4;\n\n// CROSSOVER: le 4 varianti di B3, frequenze che scivolano in 20 ms\nwx0 = max(0, 1 - abs(s_xo - 0));\nwx1 = max(0, 1 - abs(s_xo - 1));\nwx2 = max(0, 1 - abs(s_xo - 2));\nwx3 = max(0, 1 - abs(s_xo - 3));\ngx0 = tan(pi * (wx0 * 90.0 + wx1 * 80.0 + wx2 * 75.0 + wx3 * 80.0) / sr4);\ngx1 = tan(pi * (wx0 * 350.0 + wx1 * 200.0 + wx2 * 190.0 + wx3 * 220.0) / sr4);\ngx2 = tan(pi * (wx0 * 1200.0 + wx1 * 1200.0 + wx2 * 2200.0 + wx3 * 1500.0) / sr4);\ngx3 = tan(pi * (wx0 * 3500.0 + wx1 * 6000.0 + wx2 * 8000.0 + wx3 * 7000.0) / sr4);\n\n// KILL: 1 = via aperta (interruttore, taglio netto: dec. 88)\na0 = 1 - k_sub;\na1 = 1 - k_kick;\na2 = 1 - k_mid;\na3 = 1 - k_high;\na4 = 1 - k_super;\n\n// celle EQ: GAIN (famiglia eq-serie \u00a710), POSITION esponenziale,\n// WIDTH Q 3 / 1 / 0,5\nth = s_g_1 / 100;\ngl = (th >= 0.5) * pow(10, 0.75 * (th - 0.5) / 0.5) + (th < 0.5) * (th >= 0.05) * pow(10, -1.35 * (0.5 - th) / 0.45) + (th < 0.05) * 0.0446683592150963 * th / 0.05;\nb1 = gl - 1;\nge1 = tan(pi * 20.0 * pow(6.0, s_p_1 / 100) / sr4);\nke1 = max(0, 1 - abs(s_w_1)) * 0.3333333333333333 + max(0, 1 - abs(s_w_1 - 1)) * 1.0 + max(0, 1 - abs(s_w_1 - 2)) * 2.0;\nth = s_g_2 / 100;\ngl = (th >= 0.5) * pow(10, 0.75 * (th - 0.5) / 0.5) + (th < 0.5) * (th >= 0.05) * pow(10, -1.35 * (0.5 - th) / 0.45) + (th < 0.05) * 0.0446683592150963 * th / 0.05;\nb2 = gl - 1;\nge2 = tan(pi * 80.0 * pow(5.0, s_p_2 / 100) / sr4);\nke2 = max(0, 1 - abs(s_w_2)) * 0.3333333333333333 + max(0, 1 - abs(s_w_2 - 1)) * 1.0 + max(0, 1 - abs(s_w_2 - 2)) * 2.0;\nth = s_g_3 / 100;\ngl = (th >= 0.5) * pow(10, 0.75 * (th - 0.5) / 0.5) + (th < 0.5) * (th >= 0.05) * pow(10, -1.35 * (0.5 - th) / 0.45) + (th < 0.05) * 0.0446683592150963 * th / 0.05;\nb3 = gl - 1;\nge3 = tan(pi * 250.0 * pow(6.0, s_p_3 / 100) / sr4);\nke3 = max(0, 1 - abs(s_w_3)) * 0.3333333333333333 + max(0, 1 - abs(s_w_3 - 1)) * 1.0 + max(0, 1 - abs(s_w_3 - 2)) * 2.0;\nth = s_g_4 / 100;\ngl = (th >= 0.5) * pow(10, 0.6 * (th - 0.5) / 0.5) + (th < 0.5) * (th >= 0.05) * pow(10, -1.35 * (0.5 - th) / 0.45) + (th < 0.05) * 0.0446683592150963 * th / 0.05;\nb4 = gl - 1;\nge4 = tan(pi * 800.0 * pow(6.25, s_p_4 / 100) / sr4);\nke4 = max(0, 1 - abs(s_w_4)) * 0.3333333333333333 + max(0, 1 - abs(s_w_4 - 1)) * 1.0 + max(0, 1 - abs(s_w_4 - 2)) * 2.0;\nth = s_g_5 / 100;\ngl = (th >= 0.5) * pow(10, 0.45 * (th - 0.5) / 0.5) + (th < 0.5) * (th >= 0.05) * pow(10, -1.35 * (0.5 - th) / 0.45) + (th < 0.05) * 0.0446683592150963 * th / 0.05;\nb5 = gl - 1;\nge5 = tan(pi * 3000.0 * pow(6.666666666666667, s_p_5 / 100) / sr4);\nke5 = max(0, 1 - abs(s_w_5)) * 0.3333333333333333 + max(0, 1 - abs(s_w_5 - 1)) * 1.0 + max(0, 1 - abs(s_w_5 - 2)) * 2.0;\nmg = s_growl / 100;\nmt = s_nastro / 100;\nglp = tan(pi * 350.0 / sr4);\nghg = tan(pi * 0.9756198011533183 / sr4);\nkcb = 1 / (sr4 * 0.0022);\nkc = 1 / (sr4 * 0.48543689320388356);\n\n// livelli: 1,0 digitale = 4.361 V; dominio interno -6 dB\n// ===== lato L =====\nL_e = in1;\nL_o = in1;\nL_e = ap(hb, 0, L_e, 0.019059005558478156);\nL_e = ap(hb, 4, L_e, 0.1559582483500435);\nL_e = ap(hb, 8, L_e, 0.3650536901969154);\nL_e = ap(hb, 12, L_e, 0.5755010797915323);\nL_e = ap(hb, 16, L_e, 0.7526447471286863);\nL_e = ap(hb, 20, L_e, 0.8980636464339091);\nL_o = ap(hb, 2, L_o, 0.07350243453590219);\nL_o = ap(hb, 6, L_o, 0.25649919975582064);\nL_o = ap(hb, 10, L_o, 0.47327898479453656);\nL_o = ap(hb, 14, L_o, 0.6688095014357188);\nL_o = ap(hb, 18, L_o, 0.8282265929955738);\nL_o = ap(hb, 22, L_o, 0.9656701590349398);\nL_u0 = L_e;\nL_u1 = L_e;\nL_u0 = ap(hb, 24, L_u0, 0.04245470986526787);\nL_u0 = ap(hb, 28, L_u0, 0.39331989319033134);\nL_u1 = ap(hb, 26, L_u1, 0.17073985049750015);\nL_u1 = ap(hb, 30, L_u1, 0.7457135887202412);\nL_u2 = L_o;\nL_u3 = L_o;\nL_u2 = ap(hb, 24, L_u2, 0.04245470986526787);\nL_u2 = ap(hb, 28, L_u2, 0.39331989319033134);\nL_u3 = ap(hb, 26, L_u3, 0.17073985049750015);\nL_u3 = ap(hb, 30, L_u3, 0.7457135887202412);\nxa = L_u0;\n// banca: spina HP4 ai 4 crossover\np0 = xa;\np1 = svhp(sv, 0, p0, gx0, 1.4142135623730951);\np1 = svhp(sv, 2, p1, gx0, 1.4142135623730951);\np2 = svhp(sv, 4, p1, gx1, 1.4142135623730951);\np2 = svhp(sv, 6, p2, gx1, 1.4142135623730951);\np3 = svhp(sv, 8, p2, gx2, 1.4142135623730951);\np3 = svhp(sv, 10, p3, gx2, 1.4142135623730951);\np4 = svhp(sv, 12, p3, gx3, 1.4142135623730951);\np4 = svhp(sv, 14, p4, gx3, 1.4142135623730951);\n// vie: LP4 dalla presa e allpass dei crossover sopra\nya = p0;\nya = svlp(sv, 16, ya, gx0, 1.4142135623730951);\nya = svlp(sv, 18, ya, gx0, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 20, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 22, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 24, ya, gx3, 1.4142135623730951);\nv0 = ya;\nya = p1;\nya = svlp(sv, 26, ya, gx1, 1.4142135623730951);\nya = svlp(sv, 28, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 30, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 32, ya, gx3, 1.4142135623730951);\nv1 = ya;\nya = p2;\nya = svlp(sv, 34, ya, gx2, 1.4142135623730951);\nya = svlp(sv, 36, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 38, ya, gx3, 1.4142135623730951);\nv2 = ya;\nya = p3;\nya = svlp(sv, 40, ya, gx3, 1.4142135623730951);\nya = svlp(sv, 42, ya, gx3, 1.4142135623730951);\nv3 = ya;\nya = a0 * v0 + a1 * v1 + a2 * v2 + a3 * v3 + a4 * p4;\n// EQ creativo: 5 campane in serie\nya = ya + b1 * ke1 * svbp(sv, 44, ya, ge1, ke1);\nya = ya + b2 * ke2 * svbp(sv, 46, ya, ge2, ke2);\nya = ya + b3 * ke3 * svbp(sv, 48, ya, ge3, ke3);\nya = ya + b4 * ke4 * svbp(sv, 50, ya, ge4, ke4);\nya = ya + b5 * ke5 * svbp(sv, 52, ya, ge5, ke5);\n// GROWL (sotto 350 Hz) e NASTRO, volt del dominio interno\nxa = ya * 2.180432973121504;\nlw = svlp(sv, 54, xa, glp, 1.4142135623730951);\ndg = 0.613 * hp1(sa, 0, clipg(lw), ghg) - lw;\ny1 = xa + mg * dg;\njvs = 2.017546946859815 + peek(sa, 1);\njvc = 14.637421755233643 + peek(sa, 3);\njid = 0.002241718829844239 + peek(sa, 2);\njid = jstep(y1, jvs, jvc, jid);\njid = jstep(y1, jvs, jvc, jid);\njid = jstep(y1, jvs, jvc, jid);\njid = jstep(y1, jvs, jvc, jid);\nvdr = 1455.0392860607237 * (0.012 + jvc / 48543.68932038835 - jid);\nvtac = vdr - jvc;\npoke(sa, jvs + kcb * (jid - jvs / 900.0) - 2.017546946859815, 1);\npoke(sa, jid - 0.002241718829844239, 2);\npoke(sa, jvc + kc * vtac - 14.637421755233643, 3);\ndt = -0.206 * vtac - y1;\nL_y0 = (y1 + mt * dt) / 2.180432973121504;\nxa = L_u1;\n// banca: spina HP4 ai 4 crossover\np0 = xa;\np1 = svhp(sv, 0, p0, gx0, 1.4142135623730951);\np1 = svhp(sv, 2, p1, gx0, 1.4142135623730951);\np2 = svhp(sv, 4, p1, gx1, 1.4142135623730951);\np2 = svhp(sv, 6, p2, gx1, 1.4142135623730951);\np3 = svhp(sv, 8, p2, gx2, 1.4142135623730951);\np3 = svhp(sv, 10, p3, gx2, 1.4142135623730951);\np4 = svhp(sv, 12, p3, gx3, 1.4142135623730951);\np4 = svhp(sv, 14, p4, gx3, 1.4142135623730951);\n// vie: LP4 dalla presa e allpass dei crossover sopra\nya = p0;\nya = svlp(sv, 16, ya, gx0, 1.4142135623730951);\nya = svlp(sv, 18, ya, gx0, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 20, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 22, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 24, ya, gx3, 1.4142135623730951);\nv0 = ya;\nya = p1;\nya = svlp(sv, 26, ya, gx1, 1.4142135623730951);\nya = svlp(sv, 28, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 30, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 32, ya, gx3, 1.4142135623730951);\nv1 = ya;\nya = p2;\nya = svlp(sv, 34, ya, gx2, 1.4142135623730951);\nya = svlp(sv, 36, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 38, ya, gx3, 1.4142135623730951);\nv2 = ya;\nya = p3;\nya = svlp(sv, 40, ya, gx3, 1.4142135623730951);\nya = svlp(sv, 42, ya, gx3, 1.4142135623730951);\nv3 = ya;\nya = a0 * v0 + a1 * v1 + a2 * v2 + a3 * v3 + a4 * p4;\n// EQ creativo: 5 campane in serie\nya = ya + b1 * ke1 * svbp(sv, 44, ya, ge1, ke1);\nya = ya + b2 * ke2 * svbp(sv, 46, ya, ge2, ke2);\nya = ya + b3 * ke3 * svbp(sv, 48, ya, ge3, ke3);\nya = ya + b4 * ke4 * svbp(sv, 50, ya, ge4, ke4);\nya = ya + b5 * ke5 * svbp(sv, 52, ya, ge5, ke5);\n// GROWL (sotto 350 Hz) e NASTRO, volt del dominio interno\nxa = ya * 2.180432973121504;\nlw = svlp(sv, 54, xa, glp, 1.4142135623730951);\ndg = 0.613 * hp1(sa, 0, clipg(lw), ghg) - lw;\ny1 = xa + mg * dg;\njvs = 2.017546946859815 + peek(sa, 1);\njvc = 14.637421755233643 + peek(sa, 3);\njid = 0.002241718829844239 + peek(sa, 2);\njid = jstep(y1, jvs, jvc, jid);\njid = jstep(y1, jvs, jvc, jid);\njid = jstep(y1, jvs, jvc, jid);\njid = jstep(y1, jvs, jvc, jid);\nvdr = 1455.0392860607237 * (0.012 + jvc / 48543.68932038835 - jid);\nvtac = vdr - jvc;\npoke(sa, jvs + kcb * (jid - jvs / 900.0) - 2.017546946859815, 1);\npoke(sa, jid - 0.002241718829844239, 2);\npoke(sa, jvc + kc * vtac - 14.637421755233643, 3);\ndt = -0.206 * vtac - y1;\nL_y1 = (y1 + mt * dt) / 2.180432973121504;\nxa = L_u2;\n// banca: spina HP4 ai 4 crossover\np0 = xa;\np1 = svhp(sv, 0, p0, gx0, 1.4142135623730951);\np1 = svhp(sv, 2, p1, gx0, 1.4142135623730951);\np2 = svhp(sv, 4, p1, gx1, 1.4142135623730951);\np2 = svhp(sv, 6, p2, gx1, 1.4142135623730951);\np3 = svhp(sv, 8, p2, gx2, 1.4142135623730951);\np3 = svhp(sv, 10, p3, gx2, 1.4142135623730951);\np4 = svhp(sv, 12, p3, gx3, 1.4142135623730951);\np4 = svhp(sv, 14, p4, gx3, 1.4142135623730951);\n// vie: LP4 dalla presa e allpass dei crossover sopra\nya = p0;\nya = svlp(sv, 16, ya, gx0, 1.4142135623730951);\nya = svlp(sv, 18, ya, gx0, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 20, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 22, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 24, ya, gx3, 1.4142135623730951);\nv0 = ya;\nya = p1;\nya = svlp(sv, 26, ya, gx1, 1.4142135623730951);\nya = svlp(sv, 28, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 30, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 32, ya, gx3, 1.4142135623730951);\nv1 = ya;\nya = p2;\nya = svlp(sv, 34, ya, gx2, 1.4142135623730951);\nya = svlp(sv, 36, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 38, ya, gx3, 1.4142135623730951);\nv2 = ya;\nya = p3;\nya = svlp(sv, 40, ya, gx3, 1.4142135623730951);\nya = svlp(sv, 42, ya, gx3, 1.4142135623730951);\nv3 = ya;\nya = a0 * v0 + a1 * v1 + a2 * v2 + a3 * v3 + a4 * p4;\n// EQ creativo: 5 campane in serie\nya = ya + b1 * ke1 * svbp(sv, 44, ya, ge1, ke1);\nya = ya + b2 * ke2 * svbp(sv, 46, ya, ge2, ke2);\nya = ya + b3 * ke3 * svbp(sv, 48, ya, ge3, ke3);\nya = ya + b4 * ke4 * svbp(sv, 50, ya, ge4, ke4);\nya = ya + b5 * ke5 * svbp(sv, 52, ya, ge5, ke5);\n// GROWL (sotto 350 Hz) e NASTRO, volt del dominio interno\nxa = ya * 2.180432973121504;\nlw = svlp(sv, 54, xa, glp, 1.4142135623730951);\ndg = 0.613 * hp1(sa, 0, clipg(lw), ghg) - lw;\ny1 = xa + mg * dg;\njvs = 2.017546946859815 + peek(sa, 1);\njvc = 14.637421755233643 + peek(sa, 3);\njid = 0.002241718829844239 + peek(sa, 2);\njid = jstep(y1, jvs, jvc, jid);\njid = jstep(y1, jvs, jvc, jid);\njid = jstep(y1, jvs, jvc, jid);\njid = jstep(y1, jvs, jvc, jid);\nvdr = 1455.0392860607237 * (0.012 + jvc / 48543.68932038835 - jid);\nvtac = vdr - jvc;\npoke(sa, jvs + kcb * (jid - jvs / 900.0) - 2.017546946859815, 1);\npoke(sa, jid - 0.002241718829844239, 2);\npoke(sa, jvc + kc * vtac - 14.637421755233643, 3);\ndt = -0.206 * vtac - y1;\nL_y2 = (y1 + mt * dt) / 2.180432973121504;\nxa = L_u3;\n// banca: spina HP4 ai 4 crossover\np0 = xa;\np1 = svhp(sv, 0, p0, gx0, 1.4142135623730951);\np1 = svhp(sv, 2, p1, gx0, 1.4142135623730951);\np2 = svhp(sv, 4, p1, gx1, 1.4142135623730951);\np2 = svhp(sv, 6, p2, gx1, 1.4142135623730951);\np3 = svhp(sv, 8, p2, gx2, 1.4142135623730951);\np3 = svhp(sv, 10, p3, gx2, 1.4142135623730951);\np4 = svhp(sv, 12, p3, gx3, 1.4142135623730951);\np4 = svhp(sv, 14, p4, gx3, 1.4142135623730951);\n// vie: LP4 dalla presa e allpass dei crossover sopra\nya = p0;\nya = svlp(sv, 16, ya, gx0, 1.4142135623730951);\nya = svlp(sv, 18, ya, gx0, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 20, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 22, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 24, ya, gx3, 1.4142135623730951);\nv0 = ya;\nya = p1;\nya = svlp(sv, 26, ya, gx1, 1.4142135623730951);\nya = svlp(sv, 28, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 30, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 32, ya, gx3, 1.4142135623730951);\nv1 = ya;\nya = p2;\nya = svlp(sv, 34, ya, gx2, 1.4142135623730951);\nya = svlp(sv, 36, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 38, ya, gx3, 1.4142135623730951);\nv2 = ya;\nya = p3;\nya = svlp(sv, 40, ya, gx3, 1.4142135623730951);\nya = svlp(sv, 42, ya, gx3, 1.4142135623730951);\nv3 = ya;\nya = a0 * v0 + a1 * v1 + a2 * v2 + a3 * v3 + a4 * p4;\n// EQ creativo: 5 campane in serie\nya = ya + b1 * ke1 * svbp(sv, 44, ya, ge1, ke1);\nya = ya + b2 * ke2 * svbp(sv, 46, ya, ge2, ke2);\nya = ya + b3 * ke3 * svbp(sv, 48, ya, ge3, ke3);\nya = ya + b4 * ke4 * svbp(sv, 50, ya, ge4, ke4);\nya = ya + b5 * ke5 * svbp(sv, 52, ya, ge5, ke5);\n// GROWL (sotto 350 Hz) e NASTRO, volt del dominio interno\nxa = ya * 2.180432973121504;\nlw = svlp(sv, 54, xa, glp, 1.4142135623730951);\ndg = 0.613 * hp1(sa, 0, clipg(lw), ghg) - lw;\ny1 = xa + mg * dg;\njvs = 2.017546946859815 + peek(sa, 1);\njvc = 14.637421755233643 + peek(sa, 3);\njid = 0.002241718829844239 + peek(sa, 2);\njid = jstep(y1, jvs, jvc, jid);\njid = jstep(y1, jvs, jvc, jid);\njid = jstep(y1, jvs, jvc, jid);\njid = jstep(y1, jvs, jvc, jid);\nvdr = 1455.0392860607237 * (0.012 + jvc / 48543.68932038835 - jid);\nvtac = vdr - jvc;\npoke(sa, jvs + kcb * (jid - jvs / 900.0) - 2.017546946859815, 1);\npoke(sa, jid - 0.002241718829844239, 2);\npoke(sa, jvc + kc * vtac - 14.637421755233643, 3);\ndt = -0.206 * vtac - y1;\nL_y3 = (y1 + mt * dt) / 2.180432973121504;\nd0 = L_y1;\nd1 = L_y0;\nd0 = ap(hb, 32, d0, 0.04245470986526787);\nd0 = ap(hb, 36, d0, 0.39331989319033134);\nd1 = ap(hb, 34, d1, 0.17073985049750015);\nd1 = ap(hb, 38, d1, 0.7457135887202412);\nL_v0 = 0.5 * (d0 + d1);\nd0 = L_y3;\nd1 = L_y2;\nd0 = ap(hb, 32, d0, 0.04245470986526787);\nd0 = ap(hb, 36, d0, 0.39331989319033134);\nd1 = ap(hb, 34, d1, 0.17073985049750015);\nd1 = ap(hb, 38, d1, 0.7457135887202412);\nL_v1 = 0.5 * (d0 + d1);\nd0 = L_v1;\nd1 = L_v0;\nd0 = ap(hb, 40, d0, 0.019059005558478156);\nd0 = ap(hb, 44, d0, 0.1559582483500435);\nd0 = ap(hb, 48, d0, 0.3650536901969154);\nd0 = ap(hb, 52, d0, 0.5755010797915323);\nd0 = ap(hb, 56, d0, 0.7526447471286863);\nd0 = ap(hb, 60, d0, 0.8980636464339091);\nd1 = ap(hb, 42, d1, 0.07350243453590219);\nd1 = ap(hb, 46, d1, 0.25649919975582064);\nd1 = ap(hb, 50, d1, 0.47327898479453656);\nd1 = ap(hb, 54, d1, 0.6688095014357188);\nd1 = ap(hb, 58, d1, 0.8282265929955738);\nd1 = ap(hb, 62, d1, 0.9656701590349398);\nL_w = 0.5 * (d0 + d1);\nout1 = L_w;\n\n// ===== lato R =====\nR_e = in2;\nR_o = in2;\nR_e = ap(hb, 64, R_e, 0.019059005558478156);\nR_e = ap(hb, 68, R_e, 0.1559582483500435);\nR_e = ap(hb, 72, R_e, 0.3650536901969154);\nR_e = ap(hb, 76, R_e, 0.5755010797915323);\nR_e = ap(hb, 80, R_e, 0.7526447471286863);\nR_e = ap(hb, 84, R_e, 0.8980636464339091);\nR_o = ap(hb, 66, R_o, 0.07350243453590219);\nR_o = ap(hb, 70, R_o, 0.25649919975582064);\nR_o = ap(hb, 74, R_o, 0.47327898479453656);\nR_o = ap(hb, 78, R_o, 0.6688095014357188);\nR_o = ap(hb, 82, R_o, 0.8282265929955738);\nR_o = ap(hb, 86, R_o, 0.9656701590349398);\nR_u0 = R_e;\nR_u1 = R_e;\nR_u0 = ap(hb, 88, R_u0, 0.04245470986526787);\nR_u0 = ap(hb, 92, R_u0, 0.39331989319033134);\nR_u1 = ap(hb, 90, R_u1, 0.17073985049750015);\nR_u1 = ap(hb, 94, R_u1, 0.7457135887202412);\nR_u2 = R_o;\nR_u3 = R_o;\nR_u2 = ap(hb, 88, R_u2, 0.04245470986526787);\nR_u2 = ap(hb, 92, R_u2, 0.39331989319033134);\nR_u3 = ap(hb, 90, R_u3, 0.17073985049750015);\nR_u3 = ap(hb, 94, R_u3, 0.7457135887202412);\nxa = R_u0;\n// banca: spina HP4 ai 4 crossover\np0 = xa;\np1 = svhp(sv, 56, p0, gx0, 1.4142135623730951);\np1 = svhp(sv, 58, p1, gx0, 1.4142135623730951);\np2 = svhp(sv, 60, p1, gx1, 1.4142135623730951);\np2 = svhp(sv, 62, p2, gx1, 1.4142135623730951);\np3 = svhp(sv, 64, p2, gx2, 1.4142135623730951);\np3 = svhp(sv, 66, p3, gx2, 1.4142135623730951);\np4 = svhp(sv, 68, p3, gx3, 1.4142135623730951);\np4 = svhp(sv, 70, p4, gx3, 1.4142135623730951);\n// vie: LP4 dalla presa e allpass dei crossover sopra\nya = p0;\nya = svlp(sv, 72, ya, gx0, 1.4142135623730951);\nya = svlp(sv, 74, ya, gx0, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 76, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 78, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 80, ya, gx3, 1.4142135623730951);\nv0 = ya;\nya = p1;\nya = svlp(sv, 82, ya, gx1, 1.4142135623730951);\nya = svlp(sv, 84, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 86, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 88, ya, gx3, 1.4142135623730951);\nv1 = ya;\nya = p2;\nya = svlp(sv, 90, ya, gx2, 1.4142135623730951);\nya = svlp(sv, 92, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 94, ya, gx3, 1.4142135623730951);\nv2 = ya;\nya = p3;\nya = svlp(sv, 96, ya, gx3, 1.4142135623730951);\nya = svlp(sv, 98, ya, gx3, 1.4142135623730951);\nv3 = ya;\nya = a0 * v0 + a1 * v1 + a2 * v2 + a3 * v3 + a4 * p4;\n// EQ creativo: 5 campane in serie\nya = ya + b1 * ke1 * svbp(sv, 100, ya, ge1, ke1);\nya = ya + b2 * ke2 * svbp(sv, 102, ya, ge2, ke2);\nya = ya + b3 * ke3 * svbp(sv, 104, ya, ge3, ke3);\nya = ya + b4 * ke4 * svbp(sv, 106, ya, ge4, ke4);\nya = ya + b5 * ke5 * svbp(sv, 108, ya, ge5, ke5);\n// GROWL (sotto 350 Hz) e NASTRO, volt del dominio interno\nxa = ya * 2.180432973121504;\nlw = svlp(sv, 110, xa, glp, 1.4142135623730951);\ndg = 0.613 * hp1(sa, 4, clipg(lw), ghg) - lw;\ny1 = xa + mg * dg;\njvs = 2.017546946859815 + peek(sa, 5);\njvc = 14.637421755233643 + peek(sa, 7);\njid = 0.002241718829844239 + peek(sa, 6);\njid = jstep(y1, jvs, jvc, jid);\njid = jstep(y1, jvs, jvc, jid);\njid = jstep(y1, jvs, jvc, jid);\njid = jstep(y1, jvs, jvc, jid);\nvdr = 1455.0392860607237 * (0.012 + jvc / 48543.68932038835 - jid);\nvtac = vdr - jvc;\npoke(sa, jvs + kcb * (jid - jvs / 900.0) - 2.017546946859815, 5);\npoke(sa, jid - 0.002241718829844239, 6);\npoke(sa, jvc + kc * vtac - 14.637421755233643, 7);\ndt = -0.206 * vtac - y1;\nR_y0 = (y1 + mt * dt) / 2.180432973121504;\nxa = R_u1;\n// banca: spina HP4 ai 4 crossover\np0 = xa;\np1 = svhp(sv, 56, p0, gx0, 1.4142135623730951);\np1 = svhp(sv, 58, p1, gx0, 1.4142135623730951);\np2 = svhp(sv, 60, p1, gx1, 1.4142135623730951);\np2 = svhp(sv, 62, p2, gx1, 1.4142135623730951);\np3 = svhp(sv, 64, p2, gx2, 1.4142135623730951);\np3 = svhp(sv, 66, p3, gx2, 1.4142135623730951);\np4 = svhp(sv, 68, p3, gx3, 1.4142135623730951);\np4 = svhp(sv, 70, p4, gx3, 1.4142135623730951);\n// vie: LP4 dalla presa e allpass dei crossover sopra\nya = p0;\nya = svlp(sv, 72, ya, gx0, 1.4142135623730951);\nya = svlp(sv, 74, ya, gx0, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 76, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 78, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 80, ya, gx3, 1.4142135623730951);\nv0 = ya;\nya = p1;\nya = svlp(sv, 82, ya, gx1, 1.4142135623730951);\nya = svlp(sv, 84, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 86, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 88, ya, gx3, 1.4142135623730951);\nv1 = ya;\nya = p2;\nya = svlp(sv, 90, ya, gx2, 1.4142135623730951);\nya = svlp(sv, 92, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 94, ya, gx3, 1.4142135623730951);\nv2 = ya;\nya = p3;\nya = svlp(sv, 96, ya, gx3, 1.4142135623730951);\nya = svlp(sv, 98, ya, gx3, 1.4142135623730951);\nv3 = ya;\nya = a0 * v0 + a1 * v1 + a2 * v2 + a3 * v3 + a4 * p4;\n// EQ creativo: 5 campane in serie\nya = ya + b1 * ke1 * svbp(sv, 100, ya, ge1, ke1);\nya = ya + b2 * ke2 * svbp(sv, 102, ya, ge2, ke2);\nya = ya + b3 * ke3 * svbp(sv, 104, ya, ge3, ke3);\nya = ya + b4 * ke4 * svbp(sv, 106, ya, ge4, ke4);\nya = ya + b5 * ke5 * svbp(sv, 108, ya, ge5, ke5);\n// GROWL (sotto 350 Hz) e NASTRO, volt del dominio interno\nxa = ya * 2.180432973121504;\nlw = svlp(sv, 110, xa, glp, 1.4142135623730951);\ndg = 0.613 * hp1(sa, 4, clipg(lw), ghg) - lw;\ny1 = xa + mg * dg;\njvs = 2.017546946859815 + peek(sa, 5);\njvc = 14.637421755233643 + peek(sa, 7);\njid = 0.002241718829844239 + peek(sa, 6);\njid = jstep(y1, jvs, jvc, jid);\njid = jstep(y1, jvs, jvc, jid);\njid = jstep(y1, jvs, jvc, jid);\njid = jstep(y1, jvs, jvc, jid);\nvdr = 1455.0392860607237 * (0.012 + jvc / 48543.68932038835 - jid);\nvtac = vdr - jvc;\npoke(sa, jvs + kcb * (jid - jvs / 900.0) - 2.017546946859815, 5);\npoke(sa, jid - 0.002241718829844239, 6);\npoke(sa, jvc + kc * vtac - 14.637421755233643, 7);\ndt = -0.206 * vtac - y1;\nR_y1 = (y1 + mt * dt) / 2.180432973121504;\nxa = R_u2;\n// banca: spina HP4 ai 4 crossover\np0 = xa;\np1 = svhp(sv, 56, p0, gx0, 1.4142135623730951);\np1 = svhp(sv, 58, p1, gx0, 1.4142135623730951);\np2 = svhp(sv, 60, p1, gx1, 1.4142135623730951);\np2 = svhp(sv, 62, p2, gx1, 1.4142135623730951);\np3 = svhp(sv, 64, p2, gx2, 1.4142135623730951);\np3 = svhp(sv, 66, p3, gx2, 1.4142135623730951);\np4 = svhp(sv, 68, p3, gx3, 1.4142135623730951);\np4 = svhp(sv, 70, p4, gx3, 1.4142135623730951);\n// vie: LP4 dalla presa e allpass dei crossover sopra\nya = p0;\nya = svlp(sv, 72, ya, gx0, 1.4142135623730951);\nya = svlp(sv, 74, ya, gx0, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 76, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 78, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 80, ya, gx3, 1.4142135623730951);\nv0 = ya;\nya = p1;\nya = svlp(sv, 82, ya, gx1, 1.4142135623730951);\nya = svlp(sv, 84, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 86, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 88, ya, gx3, 1.4142135623730951);\nv1 = ya;\nya = p2;\nya = svlp(sv, 90, ya, gx2, 1.4142135623730951);\nya = svlp(sv, 92, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 94, ya, gx3, 1.4142135623730951);\nv2 = ya;\nya = p3;\nya = svlp(sv, 96, ya, gx3, 1.4142135623730951);\nya = svlp(sv, 98, ya, gx3, 1.4142135623730951);\nv3 = ya;\nya = a0 * v0 + a1 * v1 + a2 * v2 + a3 * v3 + a4 * p4;\n// EQ creativo: 5 campane in serie\nya = ya + b1 * ke1 * svbp(sv, 100, ya, ge1, ke1);\nya = ya + b2 * ke2 * svbp(sv, 102, ya, ge2, ke2);\nya = ya + b3 * ke3 * svbp(sv, 104, ya, ge3, ke3);\nya = ya + b4 * ke4 * svbp(sv, 106, ya, ge4, ke4);\nya = ya + b5 * ke5 * svbp(sv, 108, ya, ge5, ke5);\n// GROWL (sotto 350 Hz) e NASTRO, volt del dominio interno\nxa = ya * 2.180432973121504;\nlw = svlp(sv, 110, xa, glp, 1.4142135623730951);\ndg = 0.613 * hp1(sa, 4, clipg(lw), ghg) - lw;\ny1 = xa + mg * dg;\njvs = 2.017546946859815 + peek(sa, 5);\njvc = 14.637421755233643 + peek(sa, 7);\njid = 0.002241718829844239 + peek(sa, 6);\njid = jstep(y1, jvs, jvc, jid);\njid = jstep(y1, jvs, jvc, jid);\njid = jstep(y1, jvs, jvc, jid);\njid = jstep(y1, jvs, jvc, jid);\nvdr = 1455.0392860607237 * (0.012 + jvc / 48543.68932038835 - jid);\nvtac = vdr - jvc;\npoke(sa, jvs + kcb * (jid - jvs / 900.0) - 2.017546946859815, 5);\npoke(sa, jid - 0.002241718829844239, 6);\npoke(sa, jvc + kc * vtac - 14.637421755233643, 7);\ndt = -0.206 * vtac - y1;\nR_y2 = (y1 + mt * dt) / 2.180432973121504;\nxa = R_u3;\n// banca: spina HP4 ai 4 crossover\np0 = xa;\np1 = svhp(sv, 56, p0, gx0, 1.4142135623730951);\np1 = svhp(sv, 58, p1, gx0, 1.4142135623730951);\np2 = svhp(sv, 60, p1, gx1, 1.4142135623730951);\np2 = svhp(sv, 62, p2, gx1, 1.4142135623730951);\np3 = svhp(sv, 64, p2, gx2, 1.4142135623730951);\np3 = svhp(sv, 66, p3, gx2, 1.4142135623730951);\np4 = svhp(sv, 68, p3, gx3, 1.4142135623730951);\np4 = svhp(sv, 70, p4, gx3, 1.4142135623730951);\n// vie: LP4 dalla presa e allpass dei crossover sopra\nya = p0;\nya = svlp(sv, 72, ya, gx0, 1.4142135623730951);\nya = svlp(sv, 74, ya, gx0, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 76, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 78, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 80, ya, gx3, 1.4142135623730951);\nv0 = ya;\nya = p1;\nya = svlp(sv, 82, ya, gx1, 1.4142135623730951);\nya = svlp(sv, 84, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 86, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 88, ya, gx3, 1.4142135623730951);\nv1 = ya;\nya = p2;\nya = svlp(sv, 90, ya, gx2, 1.4142135623730951);\nya = svlp(sv, 92, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 94, ya, gx3, 1.4142135623730951);\nv2 = ya;\nya = p3;\nya = svlp(sv, 96, ya, gx3, 1.4142135623730951);\nya = svlp(sv, 98, ya, gx3, 1.4142135623730951);\nv3 = ya;\nya = a0 * v0 + a1 * v1 + a2 * v2 + a3 * v3 + a4 * p4;\n// EQ creativo: 5 campane in serie\nya = ya + b1 * ke1 * svbp(sv, 100, ya, ge1, ke1);\nya = ya + b2 * ke2 * svbp(sv, 102, ya, ge2, ke2);\nya = ya + b3 * ke3 * svbp(sv, 104, ya, ge3, ke3);\nya = ya + b4 * ke4 * svbp(sv, 106, ya, ge4, ke4);\nya = ya + b5 * ke5 * svbp(sv, 108, ya, ge5, ke5);\n// GROWL (sotto 350 Hz) e NASTRO, volt del dominio interno\nxa = ya * 2.180432973121504;\nlw = svlp(sv, 110, xa, glp, 1.4142135623730951);\ndg = 0.613 * hp1(sa, 4, clipg(lw), ghg) - lw;\ny1 = xa + mg * dg;\njvs = 2.017546946859815 + peek(sa, 5);\njvc = 14.637421755233643 + peek(sa, 7);\njid = 0.002241718829844239 + peek(sa, 6);\njid = jstep(y1, jvs, jvc, jid);\njid = jstep(y1, jvs, jvc, jid);\njid = jstep(y1, jvs, jvc, jid);\njid = jstep(y1, jvs, jvc, jid);\nvdr = 1455.0392860607237 * (0.012 + jvc / 48543.68932038835 - jid);\nvtac = vdr - jvc;\npoke(sa, jvs + kcb * (jid - jvs / 900.0) - 2.017546946859815, 5);\npoke(sa, jid - 0.002241718829844239, 6);\npoke(sa, jvc + kc * vtac - 14.637421755233643, 7);\ndt = -0.206 * vtac - y1;\nR_y3 = (y1 + mt * dt) / 2.180432973121504;\nd0 = R_y1;\nd1 = R_y0;\nd0 = ap(hb, 96, d0, 0.04245470986526787);\nd0 = ap(hb, 100, d0, 0.39331989319033134);\nd1 = ap(hb, 98, d1, 0.17073985049750015);\nd1 = ap(hb, 102, d1, 0.7457135887202412);\nR_v0 = 0.5 * (d0 + d1);\nd0 = R_y3;\nd1 = R_y2;\nd0 = ap(hb, 96, d0, 0.04245470986526787);\nd0 = ap(hb, 100, d0, 0.39331989319033134);\nd1 = ap(hb, 98, d1, 0.17073985049750015);\nd1 = ap(hb, 102, d1, 0.7457135887202412);\nR_v1 = 0.5 * (d0 + d1);\nd0 = R_v1;\nd1 = R_v0;\nd0 = ap(hb, 104, d0, 0.019059005558478156);\nd0 = ap(hb, 108, d0, 0.1559582483500435);\nd0 = ap(hb, 112, d0, 0.3650536901969154);\nd0 = ap(hb, 116, d0, 0.5755010797915323);\nd0 = ap(hb, 120, d0, 0.7526447471286863);\nd0 = ap(hb, 124, d0, 0.8980636464339091);\nd1 = ap(hb, 106, d1, 0.07350243453590219);\nd1 = ap(hb, 110, d1, 0.25649919975582064);\nd1 = ap(hb, 114, d1, 0.47327898479453656);\nd1 = ap(hb, 118, d1, 0.6688095014357188);\nd1 = ap(hb, 122, d1, 0.8282265929955738);\nd1 = ap(hb, 126, d1, 0.9656701590349398);\nR_w = 0.5 * (d0 + d1);\nout2 = R_w;\n\n",
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
						460,
						60,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-c0",
					"maxclass": "live.tab",
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
						4,
						54,
						18
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "KILL SUB",
							"parameter_shortname": "KILL SUB",
							"parameter_initial_enable": 1,
							"parameter_type": 2,
							"parameter_enum": [
								"ON",
								"KILL"
							],
							"parameter_mmax": 1.0,
							"parameter_initial": [
								0
							],
							"parameter_unitstyle": 0
						}
					},
					"varname": "KILL SUB",
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
					"id": "obj-c0-pre",
					"maxclass": "newobj",
					"text": "prepend k_sub",
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
					"maxclass": "live.tab",
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
						4,
						54,
						18
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "KILL KICK",
							"parameter_shortname": "KILL KICK",
							"parameter_initial_enable": 1,
							"parameter_type": 2,
							"parameter_enum": [
								"ON",
								"KILL"
							],
							"parameter_mmax": 1.0,
							"parameter_initial": [
								0
							],
							"parameter_unitstyle": 0
						}
					},
					"varname": "KILL KICK",
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
					"id": "obj-c1-pre",
					"maxclass": "newobj",
					"text": "prepend k_kick",
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
					"maxclass": "live.tab",
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
						4,
						54,
						18
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "KILL MID",
							"parameter_shortname": "KILL MID",
							"parameter_initial_enable": 1,
							"parameter_type": 2,
							"parameter_enum": [
								"ON",
								"KILL"
							],
							"parameter_mmax": 1.0,
							"parameter_initial": [
								0
							],
							"parameter_unitstyle": 0
						}
					},
					"varname": "KILL MID",
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
					"id": "obj-c2-pre",
					"maxclass": "newobj",
					"text": "prepend k_mid",
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
						188,
						4,
						54,
						18
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "KILL HIGH",
							"parameter_shortname": "KILL HIGH",
							"parameter_initial_enable": 1,
							"parameter_type": 2,
							"parameter_enum": [
								"ON",
								"KILL"
							],
							"parameter_mmax": 1.0,
							"parameter_initial": [
								0
							],
							"parameter_unitstyle": 0
						}
					},
					"varname": "KILL HIGH",
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
					"text": "prepend k_high",
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
						248,
						4,
						54,
						18
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "KILL SUPER",
							"parameter_shortname": "KILL SUPER",
							"parameter_initial_enable": 1,
							"parameter_type": 2,
							"parameter_enum": [
								"ON",
								"KILL"
							],
							"parameter_mmax": 1.0,
							"parameter_initial": [
								0
							],
							"parameter_unitstyle": 0
						}
					},
					"varname": "KILL SUPER",
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
					"text": "prepend k_super",
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
						8,
						24,
						54,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "EQ1 GAIN",
							"parameter_shortname": "EQ1 GAIN",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								50.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "EQ1 GAIN",
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
					"text": "prepend g_1",
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
						8,
						74,
						54,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "EQ1 POS",
							"parameter_shortname": "EQ1 POS",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								50.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "EQ1 POS",
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
					"text": "prepend p_1",
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
						8,
						126,
						54,
						18
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "EQ1 WIDTH",
							"parameter_shortname": "EQ1 WIDTH",
							"parameter_initial_enable": 1,
							"parameter_type": 2,
							"parameter_enum": [
								"Q3",
								"Q1",
								"Q0.5"
							],
							"parameter_mmax": 2.0,
							"parameter_initial": [
								1
							],
							"parameter_unitstyle": 0
						}
					},
					"varname": "EQ1 WIDTH",
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
					"text": "prepend w_1",
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
					"id": "obj-c8",
					"maxclass": "live.dial",
					"parameter_enable": 1,
					"patching_rect": [
						820,
						80,
						44,
						48
					],
					"presentation": 1,
					"presentation_rect": [
						68,
						24,
						54,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "EQ2 GAIN",
							"parameter_shortname": "EQ2 GAIN",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								50.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "EQ2 GAIN",
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
					"id": "obj-c8-pre",
					"maxclass": "newobj",
					"text": "prepend g_2",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						820,
						140,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-c9",
					"maxclass": "live.dial",
					"parameter_enable": 1,
					"patching_rect": [
						910,
						80,
						44,
						48
					],
					"presentation": 1,
					"presentation_rect": [
						68,
						74,
						54,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "EQ2 POS",
							"parameter_shortname": "EQ2 POS",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								50.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "EQ2 POS",
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
					"id": "obj-c9-pre",
					"maxclass": "newobj",
					"text": "prepend p_2",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						910,
						140,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-c10",
					"maxclass": "live.tab",
					"parameter_enable": 1,
					"patching_rect": [
						1000,
						80,
						44,
						48
					],
					"presentation": 1,
					"presentation_rect": [
						68,
						126,
						54,
						18
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "EQ2 WIDTH",
							"parameter_shortname": "EQ2 WIDTH",
							"parameter_initial_enable": 1,
							"parameter_type": 2,
							"parameter_enum": [
								"Q3",
								"Q1",
								"Q0.5"
							],
							"parameter_mmax": 2.0,
							"parameter_initial": [
								1
							],
							"parameter_unitstyle": 0
						}
					},
					"varname": "EQ2 WIDTH",
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
					"id": "obj-c10-pre",
					"maxclass": "newobj",
					"text": "prepend w_2",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1000,
						140,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-c11",
					"maxclass": "live.dial",
					"parameter_enable": 1,
					"patching_rect": [
						1090,
						80,
						44,
						48
					],
					"presentation": 1,
					"presentation_rect": [
						128,
						24,
						54,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "EQ3 GAIN",
							"parameter_shortname": "EQ3 GAIN",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								50.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "EQ3 GAIN",
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
					"id": "obj-c11-pre",
					"maxclass": "newobj",
					"text": "prepend g_3",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1090,
						140,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-c12",
					"maxclass": "live.dial",
					"parameter_enable": 1,
					"patching_rect": [
						100,
						220,
						44,
						48
					],
					"presentation": 1,
					"presentation_rect": [
						128,
						74,
						54,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "EQ3 POS",
							"parameter_shortname": "EQ3 POS",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								50.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "EQ3 POS",
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
					"id": "obj-c12-pre",
					"maxclass": "newobj",
					"text": "prepend p_3",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						100,
						280,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-c13",
					"maxclass": "live.tab",
					"parameter_enable": 1,
					"patching_rect": [
						190,
						220,
						44,
						48
					],
					"presentation": 1,
					"presentation_rect": [
						128,
						126,
						54,
						18
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "EQ3 WIDTH",
							"parameter_shortname": "EQ3 WIDTH",
							"parameter_initial_enable": 1,
							"parameter_type": 2,
							"parameter_enum": [
								"Q3",
								"Q1",
								"Q0.5"
							],
							"parameter_mmax": 2.0,
							"parameter_initial": [
								1
							],
							"parameter_unitstyle": 0
						}
					},
					"varname": "EQ3 WIDTH",
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
					"id": "obj-c13-pre",
					"maxclass": "newobj",
					"text": "prepend w_3",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						190,
						280,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-c14",
					"maxclass": "live.dial",
					"parameter_enable": 1,
					"patching_rect": [
						280,
						220,
						44,
						48
					],
					"presentation": 1,
					"presentation_rect": [
						188,
						24,
						54,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "EQ4 GAIN",
							"parameter_shortname": "EQ4 GAIN",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								50.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "EQ4 GAIN",
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
					"id": "obj-c14-pre",
					"maxclass": "newobj",
					"text": "prepend g_4",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						280,
						280,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-c15",
					"maxclass": "live.dial",
					"parameter_enable": 1,
					"patching_rect": [
						370,
						220,
						44,
						48
					],
					"presentation": 1,
					"presentation_rect": [
						188,
						74,
						54,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "EQ4 POS",
							"parameter_shortname": "EQ4 POS",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								50.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "EQ4 POS",
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
					"id": "obj-c15-pre",
					"maxclass": "newobj",
					"text": "prepend p_4",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						370,
						280,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-c16",
					"maxclass": "live.tab",
					"parameter_enable": 1,
					"patching_rect": [
						460,
						220,
						44,
						48
					],
					"presentation": 1,
					"presentation_rect": [
						188,
						126,
						54,
						18
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "EQ4 WIDTH",
							"parameter_shortname": "EQ4 WIDTH",
							"parameter_initial_enable": 1,
							"parameter_type": 2,
							"parameter_enum": [
								"Q3",
								"Q1",
								"Q0.5"
							],
							"parameter_mmax": 2.0,
							"parameter_initial": [
								1
							],
							"parameter_unitstyle": 0
						}
					},
					"varname": "EQ4 WIDTH",
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
					"id": "obj-c16-pre",
					"maxclass": "newobj",
					"text": "prepend w_4",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						460,
						280,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-c17",
					"maxclass": "live.dial",
					"parameter_enable": 1,
					"patching_rect": [
						550,
						220,
						44,
						48
					],
					"presentation": 1,
					"presentation_rect": [
						248,
						24,
						54,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "EQ5 GAIN",
							"parameter_shortname": "EQ5 GAIN",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								50.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "EQ5 GAIN",
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
					"id": "obj-c17-pre",
					"maxclass": "newobj",
					"text": "prepend g_5",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						550,
						280,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-c18",
					"maxclass": "live.dial",
					"parameter_enable": 1,
					"patching_rect": [
						640,
						220,
						44,
						48
					],
					"presentation": 1,
					"presentation_rect": [
						248,
						74,
						54,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "EQ5 POS",
							"parameter_shortname": "EQ5 POS",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								50.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "EQ5 POS",
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
					"id": "obj-c18-pre",
					"maxclass": "newobj",
					"text": "prepend p_5",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						640,
						280,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-c19",
					"maxclass": "live.tab",
					"parameter_enable": 1,
					"patching_rect": [
						730,
						220,
						44,
						48
					],
					"presentation": 1,
					"presentation_rect": [
						248,
						126,
						54,
						18
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "EQ5 WIDTH",
							"parameter_shortname": "EQ5 WIDTH",
							"parameter_initial_enable": 1,
							"parameter_type": 2,
							"parameter_enum": [
								"Q3",
								"Q1",
								"Q0.5"
							],
							"parameter_mmax": 2.0,
							"parameter_initial": [
								1
							],
							"parameter_unitstyle": 0
						}
					},
					"varname": "EQ5 WIDTH",
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
					"id": "obj-c19-pre",
					"maxclass": "newobj",
					"text": "prepend w_5",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						730,
						280,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-c20",
					"maxclass": "live.dial",
					"parameter_enable": 1,
					"patching_rect": [
						820,
						220,
						44,
						48
					],
					"presentation": 1,
					"presentation_rect": [
						312,
						24,
						54,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "GROWL",
							"parameter_shortname": "GROWL",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								0.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "GROWL",
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
					"id": "obj-c20-pre",
					"maxclass": "newobj",
					"text": "prepend growl",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						820,
						280,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-c21",
					"maxclass": "live.dial",
					"parameter_enable": 1,
					"patching_rect": [
						910,
						220,
						44,
						48
					],
					"presentation": 1,
					"presentation_rect": [
						372,
						24,
						54,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "NASTRO",
							"parameter_shortname": "NASTRO",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								0.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "NASTRO",
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
					"id": "obj-c21-pre",
					"maxclass": "newobj",
					"text": "prepend nastro",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						910,
						280,
						85,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-c22",
					"maxclass": "live.tab",
					"parameter_enable": 1,
					"patching_rect": [
						1000,
						220,
						44,
						48
					],
					"presentation": 1,
					"presentation_rect": [
						312,
						78,
						114,
						66
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "CROSSOVER",
							"parameter_shortname": "CROSSOVER",
							"parameter_initial_enable": 1,
							"parameter_type": 2,
							"parameter_enum": [
								"A 90/350/1.2k/3.5k",
								"B 80/200/1.2k/6k",
								"C 75/190/2.2k/8k",
								"D 80/220/1.5k/7k"
							],
							"parameter_mmax": 3.0,
							"parameter_initial": [
								0
							],
							"parameter_unitstyle": 0
						}
					},
					"varname": "CROSSOVER",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": [
						"",
						"",
						"float"
					],
					"num_lines_patching": 4,
					"num_lines_presentation": 4
				}
			},
			{
				"box": {
					"id": "obj-c22-pre",
					"maxclass": "newobj",
					"text": "prepend xo",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						1000,
						280,
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
						148,
						420,
						18
					],
					"patching_rect": [
						20,
						520,
						420,
						18
					],
					"text": "KILL per via; EQ a campana; GROWL < 350 Hz. CROSSOVER solo prototipo (B3). 0 dBu = -12 dBFS."
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
						"obj-c8-pre",
						0
					],
					"source": [
						"obj-c8",
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
						"obj-c8-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-c9-pre",
						0
					],
					"source": [
						"obj-c9",
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
						"obj-c9-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-c10-pre",
						0
					],
					"source": [
						"obj-c10",
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
						"obj-c10-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-c11-pre",
						0
					],
					"source": [
						"obj-c11",
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
						"obj-c11-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-c12-pre",
						0
					],
					"source": [
						"obj-c12",
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
						"obj-c12-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-c13-pre",
						0
					],
					"source": [
						"obj-c13",
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
						"obj-c13-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-c14-pre",
						0
					],
					"source": [
						"obj-c14",
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
						"obj-c14-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-c15-pre",
						0
					],
					"source": [
						"obj-c15",
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
						"obj-c15-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-c16-pre",
						0
					],
					"source": [
						"obj-c16",
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
						"obj-c16-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-c17-pre",
						0
					],
					"source": [
						"obj-c17",
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
						"obj-c17-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-c18-pre",
						0
					],
					"source": [
						"obj-c18",
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
						"obj-c18-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-c19-pre",
						0
					],
					"source": [
						"obj-c19",
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
						"obj-c19-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-c20-pre",
						0
					],
					"source": [
						"obj-c20",
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
						"obj-c20-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-c21-pre",
						0
					],
					"source": [
						"obj-c21",
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
						"obj-c21-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-c22-pre",
						0
					],
					"source": [
						"obj-c22",
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
						"obj-c22-pre",
						0
					]
				}
			}
		],
		"parameters": {
			"obj-c0": [
				"KILL SUB",
				"KILL SUB",
				0
			],
			"obj-c1": [
				"KILL KICK",
				"KILL KICK",
				0
			],
			"obj-c2": [
				"KILL MID",
				"KILL MID",
				0
			],
			"obj-c3": [
				"KILL HIGH",
				"KILL HIGH",
				0
			],
			"obj-c4": [
				"KILL SUPER",
				"KILL SUPER",
				0
			],
			"obj-c5": [
				"EQ1 GAIN",
				"EQ1 GAIN",
				0
			],
			"obj-c6": [
				"EQ1 POS",
				"EQ1 POS",
				0
			],
			"obj-c7": [
				"EQ1 WIDTH",
				"EQ1 WIDTH",
				0
			],
			"obj-c8": [
				"EQ2 GAIN",
				"EQ2 GAIN",
				0
			],
			"obj-c9": [
				"EQ2 POS",
				"EQ2 POS",
				0
			],
			"obj-c10": [
				"EQ2 WIDTH",
				"EQ2 WIDTH",
				0
			],
			"obj-c11": [
				"EQ3 GAIN",
				"EQ3 GAIN",
				0
			],
			"obj-c12": [
				"EQ3 POS",
				"EQ3 POS",
				0
			],
			"obj-c13": [
				"EQ3 WIDTH",
				"EQ3 WIDTH",
				0
			],
			"obj-c14": [
				"EQ4 GAIN",
				"EQ4 GAIN",
				0
			],
			"obj-c15": [
				"EQ4 POS",
				"EQ4 POS",
				0
			],
			"obj-c16": [
				"EQ4 WIDTH",
				"EQ4 WIDTH",
				0
			],
			"obj-c17": [
				"EQ5 GAIN",
				"EQ5 GAIN",
				0
			],
			"obj-c18": [
				"EQ5 POS",
				"EQ5 POS",
				0
			],
			"obj-c19": [
				"EQ5 WIDTH",
				"EQ5 WIDTH",
				0
			],
			"obj-c20": [
				"GROWL",
				"GROWL",
				0
			],
			"obj-c21": [
				"NASTRO",
				"NASTRO",
				0
			],
			"obj-c22": [
				"CROSSOVER",
				"CROSSOVER",
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