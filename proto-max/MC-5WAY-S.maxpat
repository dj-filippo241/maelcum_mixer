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
									"code": "// MC-5WAY-S - prototipo Max P2 del 5-way maelcum_mixer.\n// GENERATO da proto-max/coefficienti/genera_5way.py: non modificare.\n// Banca LR4 allineata in fase (5 vie, kill netti), 5 celle a campana,\n// GROWL e NASTRO in parallelo al pulito. Tutto a 4x.\n\n// allpass del 1o ordine del halfband; stato in m[i] (x), m[i+1] (y)\nap(m, i, x, c) {\n\ty = c * (x - peek(m, i + 1)) + peek(m, i);\n\tpoke(m, x, i);\n\tpoke(m, y, i + 1);\n\treturn y;\n}\n\n// SVF 2 poli TPT lineare, uscita LP; stato in m[i], m[i+1]; k = 1/Q\nsvlp(m, i, x, g, k) {\n\ts1 = peek(m, i);\n\ts2 = peek(m, i + 1);\n\tfh = (x - (k + g) * s1 - s2) / (1 + g * (k + g));\n\tfb = g * fh + s1;\n\tfl = g * fb + s2;\n\tpoke(m, g * fh + fb, i);\n\tpoke(m, g * fb + fl, i + 1);\n\treturn fl;\n}\n\n// SVF 2 poli TPT lineare, uscita BP; stato in m[i], m[i+1]; k = 1/Q\nsvbp(m, i, x, g, k) {\n\ts1 = peek(m, i);\n\ts2 = peek(m, i + 1);\n\tfh = (x - (k + g) * s1 - s2) / (1 + g * (k + g));\n\tfb = g * fh + s1;\n\tfl = g * fb + s2;\n\tpoke(m, g * fh + fb, i);\n\tpoke(m, g * fb + fl, i + 1);\n\treturn fb;\n}\n\n// SVF 2 poli TPT lineare, uscita HP; stato in m[i], m[i+1]; k = 1/Q\nsvhp(m, i, x, g, k) {\n\ts1 = peek(m, i);\n\ts2 = peek(m, i + 1);\n\tfh = (x - (k + g) * s1 - s2) / (1 + g * (k + g));\n\tfb = g * fh + s1;\n\tfl = g * fb + s2;\n\tpoke(m, g * fh + fb, i);\n\tpoke(m, g * fb + fl, i + 1);\n\treturn fh;\n}\n\n// passa-alto del 1o ordine TPT (condensatore di accoppiamento)\nhp1(m, i, x, g) {\n\ts = peek(m, i);\n\tv = (x - s) * g / (1 + g);\n\tlo = v + s;\n\tpoke(m, lo + v, i);\n\treturn x - lo;\n}\n\n// clipper del GROWL: 10k in, 22k || (1 diodo + 2,2k) || (3 diodi +\n// 2,2k); Newton sulla tensione dei diodi del ramo che conduce\nclipg(low) {\n\tii = low / 10000.0;\n\tpos = ii >= 0;\n\ta = abs(ii);\n\trr = pos * 2200.568 + (1 - pos) * 2201.704;\n\tnv = pos * 0.04531548 + (1 - pos) * 0.13594644;\n\tvd = nv * log(1 + a / 2.52e-09);\n\tex = exp(vd / nv);\n\tf = 2.52e-09 * (ex - 1) * (1 + rr / 47000.0) + vd / 47000.0 - a;\n\tdf = 2.52e-09 * ex / nv * (1 + rr / 47000.0) + 1 / 47000.0;\n\tvd = vd - f / df;\n\tex = exp(vd / nv);\n\tf = 2.52e-09 * (ex - 1) * (1 + rr / 47000.0) + vd / 47000.0 - a;\n\tdf = 2.52e-09 * ex / nv * (1 + rr / 47000.0) + 1 / 47000.0;\n\tvd = vd - f / df;\n\tex = exp(vd / nv);\n\tf = 2.52e-09 * (ex - 1) * (1 + rr / 47000.0) + vd / 47000.0 - a;\n\tdf = 2.52e-09 * ex / nv * (1 + rr / 47000.0) + 1 / 47000.0;\n\tvd = vd - f / df;\n\tex = exp(vd / nv);\n\tf = 2.52e-09 * (ex - 1) * (1 + rr / 47000.0) + vd / 47000.0 - a;\n\tdf = 2.52e-09 * ex / nv * (1 + rr / 47000.0) + 1 / 47000.0;\n\tvd = vd - f / df;\n\tid = 2.52e-09 * (exp(vd / nv) - 1);\n\treturn 47000.0 * (a - id) * (pos * 2 - 1);\n}\n\n// GROWL A BANDE, clipper del basso: Rin variabile (spinta), Rf 47000, 1 / 3 diodi con 470\nclipbl(cbx, cbrin) {\n\tcbi = cbx / cbrin;\n\tcbp = cbi >= 0;\n\tcba = abs(cbi);\n\tcbr = cbp * 470.568 + (1 - cbp) * 471.704;\n\tcbn = cbp * 0.04531548 + (1 - cbp) * 0.13594644;\n\tcbd = cbn * log(1 + cba / 2.52e-09);\n\tcbe = exp(cbd / cbn);\n\tcbf = 2.52e-09 * (cbe - 1) * (1 + cbr / 47000.0) + cbd / 47000.0 - cba;\n\tcbg = 2.52e-09 * cbe / cbn * (1 + cbr / 47000.0) + 1 / 47000.0;\n\tcbd = cbd - cbf / cbg;\n\tcbe = exp(cbd / cbn);\n\tcbf = 2.52e-09 * (cbe - 1) * (1 + cbr / 47000.0) + cbd / 47000.0 - cba;\n\tcbg = 2.52e-09 * cbe / cbn * (1 + cbr / 47000.0) + 1 / 47000.0;\n\tcbd = cbd - cbf / cbg;\n\tcbe = exp(cbd / cbn);\n\tcbf = 2.52e-09 * (cbe - 1) * (1 + cbr / 47000.0) + cbd / 47000.0 - cba;\n\tcbg = 2.52e-09 * cbe / cbn * (1 + cbr / 47000.0) + 1 / 47000.0;\n\tcbd = cbd - cbf / cbg;\n\tcbe = exp(cbd / cbn);\n\tcbf = 2.52e-09 * (cbe - 1) * (1 + cbr / 47000.0) + cbd / 47000.0 - cba;\n\tcbg = 2.52e-09 * cbe / cbn * (1 + cbr / 47000.0) + 1 / 47000.0;\n\tcbd = cbd - cbf / cbg;\n\tcbe = exp(cbd / cbn);\n\tcbf = 2.52e-09 * (cbe - 1) * (1 + cbr / 47000.0) + cbd / 47000.0 - cba;\n\tcbg = 2.52e-09 * cbe / cbn * (1 + cbr / 47000.0) + 1 / 47000.0;\n\tcbd = cbd - cbf / cbg;\n\tcbe = exp(cbd / cbn);\n\tcbf = 2.52e-09 * (cbe - 1) * (1 + cbr / 47000.0) + cbd / 47000.0 - cba;\n\tcbg = 2.52e-09 * cbe / cbn * (1 + cbr / 47000.0) + 1 / 47000.0;\n\tcbd = cbd - cbf / cbg;\n\tcbq = 2.52e-09 * (exp(cbd / cbn) - 1);\n\treturn 47000.0 * (cba - cbq) * (cbp * 2 - 1);\n}\n\n// GROWL A BANDE, clipper del medio: Rin variabile (spinta), Rf 10000, 3 / 3 diodi con 4700\nclipbm(cbx, cbrin) {\n\tcbi = cbx / cbrin;\n\tcbp = cbi >= 0;\n\tcba = abs(cbi);\n\tcbr = cbp * 4701.704 + (1 - cbp) * 4701.704;\n\tcbn = cbp * 0.13594644 + (1 - cbp) * 0.13594644;\n\tcbd = cbn * log(1 + cba / 2.52e-09);\n\tcbe = exp(cbd / cbn);\n\tcbf = 2.52e-09 * (cbe - 1) * (1 + cbr / 10000.0) + cbd / 10000.0 - cba;\n\tcbg = 2.52e-09 * cbe / cbn * (1 + cbr / 10000.0) + 1 / 10000.0;\n\tcbd = cbd - cbf / cbg;\n\tcbe = exp(cbd / cbn);\n\tcbf = 2.52e-09 * (cbe - 1) * (1 + cbr / 10000.0) + cbd / 10000.0 - cba;\n\tcbg = 2.52e-09 * cbe / cbn * (1 + cbr / 10000.0) + 1 / 10000.0;\n\tcbd = cbd - cbf / cbg;\n\tcbe = exp(cbd / cbn);\n\tcbf = 2.52e-09 * (cbe - 1) * (1 + cbr / 10000.0) + cbd / 10000.0 - cba;\n\tcbg = 2.52e-09 * cbe / cbn * (1 + cbr / 10000.0) + 1 / 10000.0;\n\tcbd = cbd - cbf / cbg;\n\tcbe = exp(cbd / cbn);\n\tcbf = 2.52e-09 * (cbe - 1) * (1 + cbr / 10000.0) + cbd / 10000.0 - cba;\n\tcbg = 2.52e-09 * cbe / cbn * (1 + cbr / 10000.0) + 1 / 10000.0;\n\tcbd = cbd - cbf / cbg;\n\tcbe = exp(cbd / cbn);\n\tcbf = 2.52e-09 * (cbe - 1) * (1 + cbr / 10000.0) + cbd / 10000.0 - cba;\n\tcbg = 2.52e-09 * cbe / cbn * (1 + cbr / 10000.0) + 1 / 10000.0;\n\tcbd = cbd - cbf / cbg;\n\tcbe = exp(cbd / cbn);\n\tcbf = 2.52e-09 * (cbe - 1) * (1 + cbr / 10000.0) + cbd / 10000.0 - cba;\n\tcbg = 2.52e-09 * cbe / cbn * (1 + cbr / 10000.0) + 1 / 10000.0;\n\tcbd = cbd - cbf / cbg;\n\tcbq = 2.52e-09 * (exp(cbd / cbn) - 1);\n\treturn 10000.0 * (cba - cbq) * (cbp * 2 - 1);\n}\n\n// polo singolo TPT, uscita passa-basso; stato in m[i]\nop1(m, i, x, g) {\n\ts = peek(m, i);\n\tv = (x - s) * g / (1 + g);\n\tlo = v + s;\n\tpoke(m, lo + v, i);\n\treturn lo;\n}\n\n// clipper dell'EXCITER: 10k in, 100k || (1 diodo + 1k) || (2 diodi + 1k)\nclipe(h) {\n\tii = h / 10000.0;\n\tpos = ii >= 0;\n\ta = abs(ii);\n\trr = pos * 1000.568 + (1 - pos) * 1001.136;\n\tnv = pos * 0.04531548 + (1 - pos) * 0.09063096;\n\tvd = nv * log(1 + a / 2.52e-09);\n\tex = exp(vd / nv);\n\tf = 2.52e-09 * (ex - 1) * (1 + rr / 100000.0) + vd / 100000.0 - a;\n\tdf = 2.52e-09 * ex / nv * (1 + rr / 100000.0) + 1 / 100000.0;\n\tvd = vd - f / df;\n\tex = exp(vd / nv);\n\tf = 2.52e-09 * (ex - 1) * (1 + rr / 100000.0) + vd / 100000.0 - a;\n\tdf = 2.52e-09 * ex / nv * (1 + rr / 100000.0) + 1 / 100000.0;\n\tvd = vd - f / df;\n\tex = exp(vd / nv);\n\tf = 2.52e-09 * (ex - 1) * (1 + rr / 100000.0) + vd / 100000.0 - a;\n\tdf = 2.52e-09 * ex / nv * (1 + rr / 100000.0) + 1 / 100000.0;\n\tvd = vd - f / df;\n\tex = exp(vd / nv);\n\tf = 2.52e-09 * (ex - 1) * (1 + rr / 100000.0) + vd / 100000.0 - a;\n\tdf = 2.52e-09 * ex / nv * (1 + rr / 100000.0) + 1 / 100000.0;\n\tvd = vd - f / df;\n\tid = 2.52e-09 * (exp(vd / nv) - 1);\n\treturn 100000.0 * (a - id) * (pos * 2 - 1);\n}\n\n// CLASSE A: un passo di Newton su Vbe (Gummel-Poon ridotto, 2N3904);\n// m[i] = Vc stimata, m[i+1] = Ic\nbstep(m, i, vbe, vb, ve2, vth, rp) {\n\tex = exp(vbe / 0.025865);\n\tq1 = 1 / (1 - (vb - peek(m, i)) / 74.03);\n\tq2 = 6.734e-15 * (ex - 1) / 0.06678;\n\tsq = sqrt(1 + 4 * q2);\n\tqb = 0.5 * q1 * (1 + sq);\n\tic = 6.734e-15 * (ex - 1) / qb;\n\tie = ic * 1.0024015369836696;\n\tf = vbe + 100.0 * ie + ve2 - vb;\n\tdf = 1 + 100.0 * ie / 0.025865 / sq;\n\tpoke(m, max(vth - rp * ic, ve2 + 100.0 * ie + 0.15), i);\n\tpoke(m, ic, i + 1);\n\treturn min(max(vbe - f / df, 0.3), 0.9);\n}\n\n// NASTRO LIBERO: gate dietro 10k, diodo gate-source verso gvs;\n// Newton dall'alto\ngatev(gin, gvs) {\n\tgvg = gvs + 0.025865 * log(1 + max(gin - gvs, 0) / 1e-10);\n\tgax = exp((gvg - gvs) / 0.025865);\n\tgf = gvg + 1e-10 * (gax - 1) - gin;\n\tgdf = 1 + 3.866228494104002e-09 * gax;\n\tgvg = gvg - gf / gdf;\n\tgax = exp((gvg - gvs) / 0.025865);\n\tgf = gvg + 1e-10 * (gax - 1) - gin;\n\tgdf = 1 + 3.866228494104002e-09 * gax;\n\tgvg = gvg - gf / gdf;\n\tgax = exp((gvg - gvs) / 0.025865);\n\tgf = gvg + 1e-10 * (gax - 1) - gin;\n\tgdf = 1 + 3.866228494104002e-09 * gax;\n\tgvg = gvg - gf / gdf;\n\tgax = exp((gvg - gvs) / 0.025865);\n\tgf = gvg + 1e-10 * (gax - 1) - gin;\n\tgdf = 1 + 3.866228494104002e-09 * gax;\n\tgvg = gvg - gf / gdf;\n\treturn gvg;\n}\n\n// un passo di Newton sulla corrente del JFET (Shichman-Hodges,\n// saturazione o triodo); drain su Rd e sul sommatore (vc)\njstep(vg, vs2, vc, idd) {\n\tvd = 1455.0392860607237 * (0.012 + vc / 48543.68932038835 - idd);\n\tvs = vs2 + 150.0 * idd;\n\tvov = max(vg - vs - (-3.0), 0);\n\tvds = vd - vs;\n\tsat = vds >= vov;\n\tcl = 1 + 0.006 * vds;\n\tq = vds * (2 * vov - vds);\n\ti = sat * 0.005 * vov * vov * cl + (1 - sat) * 0.005 * q * cl;\n\tdgs = sat * 0.01 * vov * cl + (1 - sat) * 0.01 * vds * cl;\n\tdds = sat * 3e-05 * vov * vov + (1 - sat) * 0.005 * ((2 * vov - 2 * vds) * cl + q * 0.006);\n\tdf = 1 + dgs * 150.0 + dds * (1605.0392860607237);\n\treturn max(idd - (idd - i) / df, 0);\n}\n\nParam k_sub(0, min=0, max=1);\nParam k_kick(0, min=0, max=1);\nParam k_mid(0, min=0, max=1);\nParam k_high(0, min=0, max=1);\nParam k_super(0, min=0, max=1);\nParam g_1(50, min=0, max=100);\nParam g_2(50, min=0, max=100);\nParam g_3(50, min=0, max=100);\nParam g_4(50, min=0, max=100);\nParam g_5(50, min=0, max=100);\nParam p_1(50, min=0, max=100);\nParam p_2(50, min=0, max=100);\nParam p_3(50, min=0, max=100);\nParam p_4(50, min=0, max=100);\nParam p_5(50, min=0, max=100);\nParam w_1(50, min=0, max=100);\nParam w_2(50, min=0, max=100);\nParam w_3(50, min=0, max=100);\nParam w_4(50, min=0, max=100);\nParam w_5(50, min=0, max=100);\nParam growl(0, min=0, max=100);\nParam nastro(0, min=0, max=100);\nData sv(128);\nData sa(80);\nData zk(30);  // kill allo zero: per lato e via stato, campione prima, conteggio\nData hb(128);\nHistory s_g_1(50);\nHistory s_g_2(50);\nHistory s_g_3(50);\nHistory s_g_4(50);\nHistory s_g_5(50);\nHistory s_p_1(50);\nHistory s_p_2(50);\nHistory s_p_3(50);\nHistory s_p_4(50);\nHistory s_p_5(50);\nHistory s_w_1(50);\nHistory s_w_2(50);\nHistory s_w_3(50);\nHistory s_w_4(50);\nHistory s_w_5(50);\nHistory s_growl(50);\nHistory s_nastro(0);\n\n// manopole lisciate 10 ms (WIDTH compreso); CROSSOVER 20 ms; KILL netti\nt1 = exp(-1 / (0.001 * samplerate));\nt10 = exp(-1 / (0.010 * samplerate));\nt20 = exp(-1 / (0.020 * samplerate));\ns_g_1 = g_1 + t10 * (s_g_1 - g_1);\ns_g_2 = g_2 + t10 * (s_g_2 - g_2);\ns_g_3 = g_3 + t10 * (s_g_3 - g_3);\ns_g_4 = g_4 + t10 * (s_g_4 - g_4);\ns_g_5 = g_5 + t10 * (s_g_5 - g_5);\ns_p_1 = p_1 + t10 * (s_p_1 - p_1);\ns_p_2 = p_2 + t10 * (s_p_2 - p_2);\ns_p_3 = p_3 + t10 * (s_p_3 - p_3);\ns_p_4 = p_4 + t10 * (s_p_4 - p_4);\ns_p_5 = p_5 + t10 * (s_p_5 - p_5);\ns_w_1 = w_1 + t1 * (s_w_1 - w_1);\ns_w_2 = w_2 + t1 * (s_w_2 - w_2);\ns_w_3 = w_3 + t1 * (s_w_3 - w_3);\ns_w_4 = w_4 + t1 * (s_w_4 - w_4);\ns_w_5 = w_5 + t1 * (s_w_5 - w_5);\ns_growl = growl + t10 * (s_growl - growl);\ns_nastro = nastro + t10 * (s_nastro - nastro);\nsr4 = samplerate * 4;\n\n// CROSSOVER H 60/250/1.2k/8k\ngx0 = tan(pi * 60.0 / sr4);\ngx1 = tan(pi * 250.0 / sr4);\ngx2 = tan(pi * 1200.0 / sr4);\ngx3 = tan(pi * 8000.0 / sr4);\n\n// KILL: 1 = via aperta (interruttore, dec. 88). La levetta scatta al\n// primo passaggio per lo zero della via, o dopo 20 ms (dec. 164)\na0 = 1 - k_sub;\na1 = 1 - k_kick;\na2 = 1 - k_mid;\na3 = 1 - k_high;\na4 = 1 - k_super;\nztm = 0.02 * sr4;\n\n// celle EQ: GAIN (famiglia eq-serie \u00a710), POSITION esponenziale,\n// WIDTH continuo Q3...Q0,3, taper log 20 % (fw.q_width; dec. 117, 129)\nth = s_g_1 / 100;\ngl = (th >= 0.5) * pow(10, 0.75 * (th - 0.5) / 0.5) + (th < 0.5) * (th >= 0.05) * pow(10, -1.35 * (0.5 - th) / 0.45) + (th < 0.05) * 0.0446683592150963 * th / 0.05;\nb1 = gl - 1;\nge1 = tan(pi * 20.0 * pow(6.0, s_p_1 / 100) / sr4);\ntw = s_w_1 / 100;\naw = (tw <= 0.5) * 0.4 * tw + (tw > 0.5) * (0.2 + 1.6 * (tw - 0.5));\nke1 = (0.1 + 0.9 * aw) / 0.3;\nth = s_g_2 / 100;\ngl = (th >= 0.5) * pow(10, 0.75 * (th - 0.5) / 0.5) + (th < 0.5) * (th >= 0.05) * pow(10, -1.35 * (0.5 - th) / 0.45) + (th < 0.05) * 0.0446683592150963 * th / 0.05;\nb2 = gl - 1;\nge2 = tan(pi * 80.0 * pow(5.0, s_p_2 / 100) / sr4);\ntw = s_w_2 / 100;\naw = (tw <= 0.5) * 0.4 * tw + (tw > 0.5) * (0.2 + 1.6 * (tw - 0.5));\nke2 = (0.1 + 0.9 * aw) / 0.3;\nth = s_g_3 / 100;\ngl = (th >= 0.5) * pow(10, 0.75 * (th - 0.5) / 0.5) + (th < 0.5) * (th >= 0.05) * pow(10, -1.35 * (0.5 - th) / 0.45) + (th < 0.05) * 0.0446683592150963 * th / 0.05;\nb3 = gl - 1;\nge3 = tan(pi * 250.0 * pow(6.0, s_p_3 / 100) / sr4);\ntw = s_w_3 / 100;\naw = (tw <= 0.5) * 0.4 * tw + (tw > 0.5) * (0.2 + 1.6 * (tw - 0.5));\nke3 = (0.1 + 0.9 * aw) / 0.3;\nth = s_g_4 / 100;\ngl = (th >= 0.5) * pow(10, 0.6 * (th - 0.5) / 0.5) + (th < 0.5) * (th >= 0.05) * pow(10, -1.35 * (0.5 - th) / 0.45) + (th < 0.05) * 0.0446683592150963 * th / 0.05;\nb4 = gl - 1;\nge4 = tan(pi * 800.0 * pow(6.25, s_p_4 / 100) / sr4);\ntw = s_w_4 / 100;\naw = (tw <= 0.5) * 0.4 * tw + (tw > 0.5) * (0.2 + 1.6 * (tw - 0.5));\nke4 = (0.1 + 0.9 * aw) / 0.3;\nth = s_g_5 / 100;\ngl = (th >= 0.5) * pow(10, 0.45 * (th - 0.5) / 0.5) + (th < 0.5) * (th >= 0.05) * pow(10, -1.35 * (0.5 - th) / 0.45) + (th < 0.05) * 0.0446683592150963 * th / 0.05;\nb5 = gl - 1;\nge5 = tan(pi * 3000.0 * pow(6.666666666666667, s_p_5 / 100) / sr4);\ntw = s_w_5 / 100;\naw = (tw <= 0.5) * 0.4 * tw + (tw > 0.5) * (0.2 + 1.6 * (tw - 0.5));\nke5 = (0.1 + 0.9 * aw) / 0.3;\n// GROWL: curva lenta, mg = t^1.74\nmg = pow(s_growl / 100, 1.74);\ntn = s_nastro / 100;\nmt = 0.85 * ((tn <= 0.5) * 0.5 * tn / 0.5 + (tn > 0.5) * (0.5 + 0.5 * (tn - 0.5) / 0.5));\n// NASTRO LIBERO: spinta 0 -> +12 dB con la manopola\ngnl = pow(10, 0.6 * tn);\n// NASTRO A BANDE: manopola a curva inversa, tb = 1 - (1 - tn)^2.5\ntb = 1 - pow(1 - tn, 2.5);\nmtb = 0.85 * ((tb <= 0.5) * 0.5 * tb / 0.5 + (tb > 0.5) * (0.5 + 0.5 * (tb - 0.5) / 0.5));\ngnb = pow(10, 0.6 * tb);\n// GROWL A BANDE (dec. 165, 175): solo questo, il LIBERO non si calcola;\n// con la manopola a zero il blocco non si calcola e i suoi stati vanno a zero\nwgb = s_growl > 0.001;\n// GROWL A BANDE: LP4 250 Hz al basso, LP1 2500 Hz ai medi; spinta 0 -> +20 / +6 dB col pot\nrbl = 10000 / pow(10, 1.0 * mg);\nrbm = 10000 / pow(10, 0.3 * mg);\ngbf = tan(pi * 250.0 / sr4);\ngbfm = tan(pi * 2500.0 / sr4);\ngbh = tan(pi * 1.0 / sr4);\nglp = tan(pi * 350.0 / sr4);\nghg = tan(pi * 0.7375240062878429 / sr4);\nkcb = 1 / (sr4 * 0.0022);\nkc = 1 / (sr4 * 0.48543689320388356);\n// NASTRO A BANDE B9 (dec. 166, 175): solo questo; a manopola zero non si calcola\nwn6 = s_nastro > 0.001;\n// NASTRO A BANDE: enfasi (bassi 30/140 Hz e super 9000/10800 Hz tagliati) davanti al LIBERO, de-enfasi dopo\n// inclinazione dei medi: polo 1000 Hz / zero 3000 Hz prima del JFET, inversa dopo\ngnp = tan(pi * 140.0 / sr4);\ngna = tan(pi * 9000.0 / sr4);\ngnh = tan(pi * 6073.28631205577 / sr4);\ngnq = tan(pi * 47.5467957738334 / sr4);\ngnt = tan(pi * 1000.0 / sr4);\ngnu = tan(pi * 3000.0 / sr4);\ngcp = tan(pi * 5000.0 / sr4);\ngcz = tan(pi * 1500.0 / sr4);\ngmp = tan(pi * 600.0 / sr4);\ngmz = tan(pi * 300.0 / sr4);\nghb = tan(pi * 80.0 / sr4);\ngex = tan(pi * 3000.0 / sr4);\nkce = 1 / (sr4 * 0.0022);\nkcc = 1 / (sr4 * 1.11731843575419);\n\n// livelli: 1,0 digitale = 4.361 V; dominio interno -6 dB\n// ===== lato L =====\nL_e = in1;\nL_o = in1;\nL_e = ap(hb, 0, L_e, 0.019059005558478156);\nL_e = ap(hb, 4, L_e, 0.1559582483500435);\nL_e = ap(hb, 8, L_e, 0.3650536901969154);\nL_e = ap(hb, 12, L_e, 0.5755010797915323);\nL_e = ap(hb, 16, L_e, 0.7526447471286863);\nL_e = ap(hb, 20, L_e, 0.8980636464339091);\nL_o = ap(hb, 2, L_o, 0.07350243453590219);\nL_o = ap(hb, 6, L_o, 0.25649919975582064);\nL_o = ap(hb, 10, L_o, 0.47327898479453656);\nL_o = ap(hb, 14, L_o, 0.6688095014357188);\nL_o = ap(hb, 18, L_o, 0.8282265929955738);\nL_o = ap(hb, 22, L_o, 0.9656701590349398);\nL_u0 = L_e;\nL_u1 = L_e;\nL_u0 = ap(hb, 24, L_u0, 0.04245470986526787);\nL_u0 = ap(hb, 28, L_u0, 0.39331989319033134);\nL_u1 = ap(hb, 26, L_u1, 0.17073985049750015);\nL_u1 = ap(hb, 30, L_u1, 0.7457135887202412);\nL_u2 = L_o;\nL_u3 = L_o;\nL_u2 = ap(hb, 24, L_u2, 0.04245470986526787);\nL_u2 = ap(hb, 28, L_u2, 0.39331989319033134);\nL_u3 = ap(hb, 26, L_u3, 0.17073985049750015);\nL_u3 = ap(hb, 30, L_u3, 0.7457135887202412);\nxa = L_u0;\n// banca: spina HP4 ai 4 crossover\np0 = xa;\np1 = svhp(sv, 0, p0, gx0, 1.4142135623730951);\np1 = svhp(sv, 2, p1, gx0, 1.4142135623730951);\np2 = svhp(sv, 4, p1, gx1, 1.4142135623730951);\np2 = svhp(sv, 6, p2, gx1, 1.4142135623730951);\np3 = svhp(sv, 8, p2, gx2, 1.4142135623730951);\np3 = svhp(sv, 10, p3, gx2, 1.4142135623730951);\np4 = svhp(sv, 12, p3, gx3, 1.4142135623730951);\np4 = svhp(sv, 14, p4, gx3, 1.4142135623730951);\n// vie: LP4 dalla presa e allpass dei crossover sopra\nya = p0;\nya = svlp(sv, 16, ya, gx0, 1.4142135623730951);\nya = svlp(sv, 18, ya, gx0, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 20, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 22, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 24, ya, gx3, 1.4142135623730951);\nv0 = ya;\nya = p1;\nya = svlp(sv, 26, ya, gx1, 1.4142135623730951);\nya = svlp(sv, 28, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 30, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 32, ya, gx3, 1.4142135623730951);\nv1 = ya;\nya = p2;\nya = svlp(sv, 34, ya, gx2, 1.4142135623730951);\nya = svlp(sv, 36, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 38, ya, gx3, 1.4142135623730951);\nv2 = ya;\nya = p3;\nya = svlp(sv, 40, ya, gx3, 1.4142135623730951);\nya = svlp(sv, 42, ya, gx3, 1.4142135623730951);\nv3 = ya;\nzv = v0;\nzs = peek(zk, 0);\nzn = peek(zk, 2);\nzt = 1 - a0;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 1) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 0);\npoke(zk, zv, 1);\npoke(zk, zn, 2);\nz0 = 1 - zs;\nzv = v1;\nzs = peek(zk, 3);\nzn = peek(zk, 5);\nzt = 1 - a1;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 4) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 3);\npoke(zk, zv, 4);\npoke(zk, zn, 5);\nz1 = 1 - zs;\nzv = v2;\nzs = peek(zk, 6);\nzn = peek(zk, 8);\nzt = 1 - a2;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 7) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 6);\npoke(zk, zv, 7);\npoke(zk, zn, 8);\nz2 = 1 - zs;\nzv = v3;\nzs = peek(zk, 9);\nzn = peek(zk, 11);\nzt = 1 - a3;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 10) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 9);\npoke(zk, zv, 10);\npoke(zk, zn, 11);\nz3 = 1 - zs;\nzv = p4;\nzs = peek(zk, 12);\nzn = peek(zk, 14);\nzt = 1 - a4;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 13) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 12);\npoke(zk, zv, 13);\npoke(zk, zn, 14);\nz4 = 1 - zs;\nya = z0 * v0 + z1 * v1 + z2 * v2 + z3 * v3 + z4 * p4;\n// EQ creativo: 5 campane in serie\nya = ya + b1 * ke1 * svbp(sv, 44, ya, ge1, ke1);\nya = ya + b2 * ke2 * svbp(sv, 46, ya, ge2, ke2);\nya = ya + b3 * ke3 * svbp(sv, 48, ya, ge3, ke3);\nya = ya + b4 * ke4 * svbp(sv, 50, ya, ge4, ke4);\nya = ya + b5 * ke5 * svbp(sv, 52, ya, ge5, ke5);\n// GROWL (sotto 350 Hz) e NASTRO, volt del dominio interno\nxa = ya * 2.180432973121504;\ndg = 0;\n// GROWL A BANDE (dec. 165)\ndgb = 0;\nif (wgb > 0) {\ngbl = svlp(sv, 60, xa, gbf, 1.4142135623730951);\ngbl = svlp(sv, 62, gbl, gbf, 1.4142135623730951);\ngbm = op1(sa, 23, xa - gbl, gbfm);\ndgb = 0.9 * hp1(sa, 24, clipbl(gbl, rbl), gbh) - gbl + 0.5011872336272724 * hp1(sa, 25, clipbm(gbm, rbm), gbh) - gbm;\n}\ndg = dg + wgb * (dgb - dg);\ny1 = xa + mg * dg;\n// NASTRO A BANDE (dec. 166)\ndnb = 0;\nif (wn6 > 0) {\nnbu = y1;\nnbp = op1(sa, 26, nbu, gnp);\nnbu = 0.21428571428571427 * nbp + nbu - nbp;\nnbp = op1(sa, 27, nbu, gnp);\nnbu = 0.21428571428571427 * nbp + nbu - nbp;\nnbp = op1(sa, 28, nbu, gnp);\nnbu = 0.21428571428571427 * nbp + nbu - nbp;\nnbp = op1(sa, 29, nbu, gna);\nnbu = nbp + 0.8333333333333334 * (nbu - nbp);\nnbp = op1(sa, 30, nbu, gnt);\nnbu = nbp + 0.3333333333333333 * (nbu - nbp);\nqvin = min(max(gnb * nbu, -16.0), 16.0);\nqvs2 = 2.017546946859815 + peek(sa, 31);\nqid = 0.002241718829844239 + peek(sa, 32);\nqvc = 14.637421755233643 + peek(sa, 33);\nqig = peek(sa, 34);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvd = 1455.0392860607237 * (0.012 + qvc / 48543.68932038835 - qid);\nqtac = qvd - qvc;\npoke(sa, qvs2 + kcb * (qid + qig - qvs2 / 900.0) - 2.017546946859815, 31);\npoke(sa, qid - 0.002241718829844239, 32);\npoke(sa, qvc + kc * qtac - 14.637421755233643, 33);\npoke(sa, qig, 34);\nnbw = -0.1977 * qtac;\nnbp = op1(sa, 35, nbw, gnh);\nnbw = nbp + 0.6748095902284189 * (nbw - nbp);\nnbp = op1(sa, 36, nbw, gnu);\nnbw = nbp + 3.0 * (nbw - nbp);\nnbp = op1(sa, 37, nbw, gnq);\nnbw = 2.9444676075742353 * nbp + nbw - nbp;\nnbp = op1(sa, 38, nbw, gnq);\nnbw = 2.9444676075742353 * nbp + nbw - nbp;\nnbp = op1(sa, 39, nbw, gnq);\nnbw = 2.9444676075742353 * nbp + nbw - nbp;\ndnb = 0.6683439175686147 * nbw - y1;\n}\nL_y0 = (y1 + mtb * dnb) / 2.180432973121504;\nxa = L_u1;\n// banca: spina HP4 ai 4 crossover\np0 = xa;\np1 = svhp(sv, 0, p0, gx0, 1.4142135623730951);\np1 = svhp(sv, 2, p1, gx0, 1.4142135623730951);\np2 = svhp(sv, 4, p1, gx1, 1.4142135623730951);\np2 = svhp(sv, 6, p2, gx1, 1.4142135623730951);\np3 = svhp(sv, 8, p2, gx2, 1.4142135623730951);\np3 = svhp(sv, 10, p3, gx2, 1.4142135623730951);\np4 = svhp(sv, 12, p3, gx3, 1.4142135623730951);\np4 = svhp(sv, 14, p4, gx3, 1.4142135623730951);\n// vie: LP4 dalla presa e allpass dei crossover sopra\nya = p0;\nya = svlp(sv, 16, ya, gx0, 1.4142135623730951);\nya = svlp(sv, 18, ya, gx0, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 20, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 22, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 24, ya, gx3, 1.4142135623730951);\nv0 = ya;\nya = p1;\nya = svlp(sv, 26, ya, gx1, 1.4142135623730951);\nya = svlp(sv, 28, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 30, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 32, ya, gx3, 1.4142135623730951);\nv1 = ya;\nya = p2;\nya = svlp(sv, 34, ya, gx2, 1.4142135623730951);\nya = svlp(sv, 36, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 38, ya, gx3, 1.4142135623730951);\nv2 = ya;\nya = p3;\nya = svlp(sv, 40, ya, gx3, 1.4142135623730951);\nya = svlp(sv, 42, ya, gx3, 1.4142135623730951);\nv3 = ya;\nzv = v0;\nzs = peek(zk, 0);\nzn = peek(zk, 2);\nzt = 1 - a0;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 1) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 0);\npoke(zk, zv, 1);\npoke(zk, zn, 2);\nz0 = 1 - zs;\nzv = v1;\nzs = peek(zk, 3);\nzn = peek(zk, 5);\nzt = 1 - a1;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 4) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 3);\npoke(zk, zv, 4);\npoke(zk, zn, 5);\nz1 = 1 - zs;\nzv = v2;\nzs = peek(zk, 6);\nzn = peek(zk, 8);\nzt = 1 - a2;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 7) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 6);\npoke(zk, zv, 7);\npoke(zk, zn, 8);\nz2 = 1 - zs;\nzv = v3;\nzs = peek(zk, 9);\nzn = peek(zk, 11);\nzt = 1 - a3;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 10) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 9);\npoke(zk, zv, 10);\npoke(zk, zn, 11);\nz3 = 1 - zs;\nzv = p4;\nzs = peek(zk, 12);\nzn = peek(zk, 14);\nzt = 1 - a4;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 13) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 12);\npoke(zk, zv, 13);\npoke(zk, zn, 14);\nz4 = 1 - zs;\nya = z0 * v0 + z1 * v1 + z2 * v2 + z3 * v3 + z4 * p4;\n// EQ creativo: 5 campane in serie\nya = ya + b1 * ke1 * svbp(sv, 44, ya, ge1, ke1);\nya = ya + b2 * ke2 * svbp(sv, 46, ya, ge2, ke2);\nya = ya + b3 * ke3 * svbp(sv, 48, ya, ge3, ke3);\nya = ya + b4 * ke4 * svbp(sv, 50, ya, ge4, ke4);\nya = ya + b5 * ke5 * svbp(sv, 52, ya, ge5, ke5);\n// GROWL (sotto 350 Hz) e NASTRO, volt del dominio interno\nxa = ya * 2.180432973121504;\ndg = 0;\n// GROWL A BANDE (dec. 165)\ndgb = 0;\nif (wgb > 0) {\ngbl = svlp(sv, 60, xa, gbf, 1.4142135623730951);\ngbl = svlp(sv, 62, gbl, gbf, 1.4142135623730951);\ngbm = op1(sa, 23, xa - gbl, gbfm);\ndgb = 0.9 * hp1(sa, 24, clipbl(gbl, rbl), gbh) - gbl + 0.5011872336272724 * hp1(sa, 25, clipbm(gbm, rbm), gbh) - gbm;\n}\ndg = dg + wgb * (dgb - dg);\ny1 = xa + mg * dg;\n// NASTRO A BANDE (dec. 166)\ndnb = 0;\nif (wn6 > 0) {\nnbu = y1;\nnbp = op1(sa, 26, nbu, gnp);\nnbu = 0.21428571428571427 * nbp + nbu - nbp;\nnbp = op1(sa, 27, nbu, gnp);\nnbu = 0.21428571428571427 * nbp + nbu - nbp;\nnbp = op1(sa, 28, nbu, gnp);\nnbu = 0.21428571428571427 * nbp + nbu - nbp;\nnbp = op1(sa, 29, nbu, gna);\nnbu = nbp + 0.8333333333333334 * (nbu - nbp);\nnbp = op1(sa, 30, nbu, gnt);\nnbu = nbp + 0.3333333333333333 * (nbu - nbp);\nqvin = min(max(gnb * nbu, -16.0), 16.0);\nqvs2 = 2.017546946859815 + peek(sa, 31);\nqid = 0.002241718829844239 + peek(sa, 32);\nqvc = 14.637421755233643 + peek(sa, 33);\nqig = peek(sa, 34);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvd = 1455.0392860607237 * (0.012 + qvc / 48543.68932038835 - qid);\nqtac = qvd - qvc;\npoke(sa, qvs2 + kcb * (qid + qig - qvs2 / 900.0) - 2.017546946859815, 31);\npoke(sa, qid - 0.002241718829844239, 32);\npoke(sa, qvc + kc * qtac - 14.637421755233643, 33);\npoke(sa, qig, 34);\nnbw = -0.1977 * qtac;\nnbp = op1(sa, 35, nbw, gnh);\nnbw = nbp + 0.6748095902284189 * (nbw - nbp);\nnbp = op1(sa, 36, nbw, gnu);\nnbw = nbp + 3.0 * (nbw - nbp);\nnbp = op1(sa, 37, nbw, gnq);\nnbw = 2.9444676075742353 * nbp + nbw - nbp;\nnbp = op1(sa, 38, nbw, gnq);\nnbw = 2.9444676075742353 * nbp + nbw - nbp;\nnbp = op1(sa, 39, nbw, gnq);\nnbw = 2.9444676075742353 * nbp + nbw - nbp;\ndnb = 0.6683439175686147 * nbw - y1;\n}\nL_y1 = (y1 + mtb * dnb) / 2.180432973121504;\nxa = L_u2;\n// banca: spina HP4 ai 4 crossover\np0 = xa;\np1 = svhp(sv, 0, p0, gx0, 1.4142135623730951);\np1 = svhp(sv, 2, p1, gx0, 1.4142135623730951);\np2 = svhp(sv, 4, p1, gx1, 1.4142135623730951);\np2 = svhp(sv, 6, p2, gx1, 1.4142135623730951);\np3 = svhp(sv, 8, p2, gx2, 1.4142135623730951);\np3 = svhp(sv, 10, p3, gx2, 1.4142135623730951);\np4 = svhp(sv, 12, p3, gx3, 1.4142135623730951);\np4 = svhp(sv, 14, p4, gx3, 1.4142135623730951);\n// vie: LP4 dalla presa e allpass dei crossover sopra\nya = p0;\nya = svlp(sv, 16, ya, gx0, 1.4142135623730951);\nya = svlp(sv, 18, ya, gx0, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 20, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 22, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 24, ya, gx3, 1.4142135623730951);\nv0 = ya;\nya = p1;\nya = svlp(sv, 26, ya, gx1, 1.4142135623730951);\nya = svlp(sv, 28, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 30, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 32, ya, gx3, 1.4142135623730951);\nv1 = ya;\nya = p2;\nya = svlp(sv, 34, ya, gx2, 1.4142135623730951);\nya = svlp(sv, 36, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 38, ya, gx3, 1.4142135623730951);\nv2 = ya;\nya = p3;\nya = svlp(sv, 40, ya, gx3, 1.4142135623730951);\nya = svlp(sv, 42, ya, gx3, 1.4142135623730951);\nv3 = ya;\nzv = v0;\nzs = peek(zk, 0);\nzn = peek(zk, 2);\nzt = 1 - a0;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 1) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 0);\npoke(zk, zv, 1);\npoke(zk, zn, 2);\nz0 = 1 - zs;\nzv = v1;\nzs = peek(zk, 3);\nzn = peek(zk, 5);\nzt = 1 - a1;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 4) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 3);\npoke(zk, zv, 4);\npoke(zk, zn, 5);\nz1 = 1 - zs;\nzv = v2;\nzs = peek(zk, 6);\nzn = peek(zk, 8);\nzt = 1 - a2;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 7) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 6);\npoke(zk, zv, 7);\npoke(zk, zn, 8);\nz2 = 1 - zs;\nzv = v3;\nzs = peek(zk, 9);\nzn = peek(zk, 11);\nzt = 1 - a3;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 10) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 9);\npoke(zk, zv, 10);\npoke(zk, zn, 11);\nz3 = 1 - zs;\nzv = p4;\nzs = peek(zk, 12);\nzn = peek(zk, 14);\nzt = 1 - a4;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 13) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 12);\npoke(zk, zv, 13);\npoke(zk, zn, 14);\nz4 = 1 - zs;\nya = z0 * v0 + z1 * v1 + z2 * v2 + z3 * v3 + z4 * p4;\n// EQ creativo: 5 campane in serie\nya = ya + b1 * ke1 * svbp(sv, 44, ya, ge1, ke1);\nya = ya + b2 * ke2 * svbp(sv, 46, ya, ge2, ke2);\nya = ya + b3 * ke3 * svbp(sv, 48, ya, ge3, ke3);\nya = ya + b4 * ke4 * svbp(sv, 50, ya, ge4, ke4);\nya = ya + b5 * ke5 * svbp(sv, 52, ya, ge5, ke5);\n// GROWL (sotto 350 Hz) e NASTRO, volt del dominio interno\nxa = ya * 2.180432973121504;\ndg = 0;\n// GROWL A BANDE (dec. 165)\ndgb = 0;\nif (wgb > 0) {\ngbl = svlp(sv, 60, xa, gbf, 1.4142135623730951);\ngbl = svlp(sv, 62, gbl, gbf, 1.4142135623730951);\ngbm = op1(sa, 23, xa - gbl, gbfm);\ndgb = 0.9 * hp1(sa, 24, clipbl(gbl, rbl), gbh) - gbl + 0.5011872336272724 * hp1(sa, 25, clipbm(gbm, rbm), gbh) - gbm;\n}\ndg = dg + wgb * (dgb - dg);\ny1 = xa + mg * dg;\n// NASTRO A BANDE (dec. 166)\ndnb = 0;\nif (wn6 > 0) {\nnbu = y1;\nnbp = op1(sa, 26, nbu, gnp);\nnbu = 0.21428571428571427 * nbp + nbu - nbp;\nnbp = op1(sa, 27, nbu, gnp);\nnbu = 0.21428571428571427 * nbp + nbu - nbp;\nnbp = op1(sa, 28, nbu, gnp);\nnbu = 0.21428571428571427 * nbp + nbu - nbp;\nnbp = op1(sa, 29, nbu, gna);\nnbu = nbp + 0.8333333333333334 * (nbu - nbp);\nnbp = op1(sa, 30, nbu, gnt);\nnbu = nbp + 0.3333333333333333 * (nbu - nbp);\nqvin = min(max(gnb * nbu, -16.0), 16.0);\nqvs2 = 2.017546946859815 + peek(sa, 31);\nqid = 0.002241718829844239 + peek(sa, 32);\nqvc = 14.637421755233643 + peek(sa, 33);\nqig = peek(sa, 34);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvd = 1455.0392860607237 * (0.012 + qvc / 48543.68932038835 - qid);\nqtac = qvd - qvc;\npoke(sa, qvs2 + kcb * (qid + qig - qvs2 / 900.0) - 2.017546946859815, 31);\npoke(sa, qid - 0.002241718829844239, 32);\npoke(sa, qvc + kc * qtac - 14.637421755233643, 33);\npoke(sa, qig, 34);\nnbw = -0.1977 * qtac;\nnbp = op1(sa, 35, nbw, gnh);\nnbw = nbp + 0.6748095902284189 * (nbw - nbp);\nnbp = op1(sa, 36, nbw, gnu);\nnbw = nbp + 3.0 * (nbw - nbp);\nnbp = op1(sa, 37, nbw, gnq);\nnbw = 2.9444676075742353 * nbp + nbw - nbp;\nnbp = op1(sa, 38, nbw, gnq);\nnbw = 2.9444676075742353 * nbp + nbw - nbp;\nnbp = op1(sa, 39, nbw, gnq);\nnbw = 2.9444676075742353 * nbp + nbw - nbp;\ndnb = 0.6683439175686147 * nbw - y1;\n}\nL_y2 = (y1 + mtb * dnb) / 2.180432973121504;\nxa = L_u3;\n// banca: spina HP4 ai 4 crossover\np0 = xa;\np1 = svhp(sv, 0, p0, gx0, 1.4142135623730951);\np1 = svhp(sv, 2, p1, gx0, 1.4142135623730951);\np2 = svhp(sv, 4, p1, gx1, 1.4142135623730951);\np2 = svhp(sv, 6, p2, gx1, 1.4142135623730951);\np3 = svhp(sv, 8, p2, gx2, 1.4142135623730951);\np3 = svhp(sv, 10, p3, gx2, 1.4142135623730951);\np4 = svhp(sv, 12, p3, gx3, 1.4142135623730951);\np4 = svhp(sv, 14, p4, gx3, 1.4142135623730951);\n// vie: LP4 dalla presa e allpass dei crossover sopra\nya = p0;\nya = svlp(sv, 16, ya, gx0, 1.4142135623730951);\nya = svlp(sv, 18, ya, gx0, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 20, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 22, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 24, ya, gx3, 1.4142135623730951);\nv0 = ya;\nya = p1;\nya = svlp(sv, 26, ya, gx1, 1.4142135623730951);\nya = svlp(sv, 28, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 30, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 32, ya, gx3, 1.4142135623730951);\nv1 = ya;\nya = p2;\nya = svlp(sv, 34, ya, gx2, 1.4142135623730951);\nya = svlp(sv, 36, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 38, ya, gx3, 1.4142135623730951);\nv2 = ya;\nya = p3;\nya = svlp(sv, 40, ya, gx3, 1.4142135623730951);\nya = svlp(sv, 42, ya, gx3, 1.4142135623730951);\nv3 = ya;\nzv = v0;\nzs = peek(zk, 0);\nzn = peek(zk, 2);\nzt = 1 - a0;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 1) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 0);\npoke(zk, zv, 1);\npoke(zk, zn, 2);\nz0 = 1 - zs;\nzv = v1;\nzs = peek(zk, 3);\nzn = peek(zk, 5);\nzt = 1 - a1;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 4) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 3);\npoke(zk, zv, 4);\npoke(zk, zn, 5);\nz1 = 1 - zs;\nzv = v2;\nzs = peek(zk, 6);\nzn = peek(zk, 8);\nzt = 1 - a2;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 7) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 6);\npoke(zk, zv, 7);\npoke(zk, zn, 8);\nz2 = 1 - zs;\nzv = v3;\nzs = peek(zk, 9);\nzn = peek(zk, 11);\nzt = 1 - a3;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 10) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 9);\npoke(zk, zv, 10);\npoke(zk, zn, 11);\nz3 = 1 - zs;\nzv = p4;\nzs = peek(zk, 12);\nzn = peek(zk, 14);\nzt = 1 - a4;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 13) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 12);\npoke(zk, zv, 13);\npoke(zk, zn, 14);\nz4 = 1 - zs;\nya = z0 * v0 + z1 * v1 + z2 * v2 + z3 * v3 + z4 * p4;\n// EQ creativo: 5 campane in serie\nya = ya + b1 * ke1 * svbp(sv, 44, ya, ge1, ke1);\nya = ya + b2 * ke2 * svbp(sv, 46, ya, ge2, ke2);\nya = ya + b3 * ke3 * svbp(sv, 48, ya, ge3, ke3);\nya = ya + b4 * ke4 * svbp(sv, 50, ya, ge4, ke4);\nya = ya + b5 * ke5 * svbp(sv, 52, ya, ge5, ke5);\n// GROWL (sotto 350 Hz) e NASTRO, volt del dominio interno\nxa = ya * 2.180432973121504;\ndg = 0;\n// GROWL A BANDE (dec. 165)\ndgb = 0;\nif (wgb > 0) {\ngbl = svlp(sv, 60, xa, gbf, 1.4142135623730951);\ngbl = svlp(sv, 62, gbl, gbf, 1.4142135623730951);\ngbm = op1(sa, 23, xa - gbl, gbfm);\ndgb = 0.9 * hp1(sa, 24, clipbl(gbl, rbl), gbh) - gbl + 0.5011872336272724 * hp1(sa, 25, clipbm(gbm, rbm), gbh) - gbm;\n}\ndg = dg + wgb * (dgb - dg);\ny1 = xa + mg * dg;\n// NASTRO A BANDE (dec. 166)\ndnb = 0;\nif (wn6 > 0) {\nnbu = y1;\nnbp = op1(sa, 26, nbu, gnp);\nnbu = 0.21428571428571427 * nbp + nbu - nbp;\nnbp = op1(sa, 27, nbu, gnp);\nnbu = 0.21428571428571427 * nbp + nbu - nbp;\nnbp = op1(sa, 28, nbu, gnp);\nnbu = 0.21428571428571427 * nbp + nbu - nbp;\nnbp = op1(sa, 29, nbu, gna);\nnbu = nbp + 0.8333333333333334 * (nbu - nbp);\nnbp = op1(sa, 30, nbu, gnt);\nnbu = nbp + 0.3333333333333333 * (nbu - nbp);\nqvin = min(max(gnb * nbu, -16.0), 16.0);\nqvs2 = 2.017546946859815 + peek(sa, 31);\nqid = 0.002241718829844239 + peek(sa, 32);\nqvc = 14.637421755233643 + peek(sa, 33);\nqig = peek(sa, 34);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvd = 1455.0392860607237 * (0.012 + qvc / 48543.68932038835 - qid);\nqtac = qvd - qvc;\npoke(sa, qvs2 + kcb * (qid + qig - qvs2 / 900.0) - 2.017546946859815, 31);\npoke(sa, qid - 0.002241718829844239, 32);\npoke(sa, qvc + kc * qtac - 14.637421755233643, 33);\npoke(sa, qig, 34);\nnbw = -0.1977 * qtac;\nnbp = op1(sa, 35, nbw, gnh);\nnbw = nbp + 0.6748095902284189 * (nbw - nbp);\nnbp = op1(sa, 36, nbw, gnu);\nnbw = nbp + 3.0 * (nbw - nbp);\nnbp = op1(sa, 37, nbw, gnq);\nnbw = 2.9444676075742353 * nbp + nbw - nbp;\nnbp = op1(sa, 38, nbw, gnq);\nnbw = 2.9444676075742353 * nbp + nbw - nbp;\nnbp = op1(sa, 39, nbw, gnq);\nnbw = 2.9444676075742353 * nbp + nbw - nbp;\ndnb = 0.6683439175686147 * nbw - y1;\n}\nL_y3 = (y1 + mtb * dnb) / 2.180432973121504;\nif (wgb == 0) {\npoke(sv, 0, 60);\npoke(sv, 0, 61);\npoke(sv, 0, 62);\npoke(sv, 0, 63);\npoke(sa, 0, 23);\npoke(sa, 0, 24);\npoke(sa, 0, 25);\n}\nif (wn6 == 0) {\npoke(sa, 0, 26);\npoke(sa, 0, 27);\npoke(sa, 0, 28);\npoke(sa, 0, 29);\npoke(sa, 0, 30);\npoke(sa, 0, 31);\npoke(sa, 0, 32);\npoke(sa, 0, 33);\npoke(sa, 0, 34);\npoke(sa, 0, 35);\npoke(sa, 0, 36);\npoke(sa, 0, 37);\npoke(sa, 0, 38);\npoke(sa, 0, 39);\n}\nd0 = L_y1;\nd1 = L_y0;\nd0 = ap(hb, 32, d0, 0.04245470986526787);\nd0 = ap(hb, 36, d0, 0.39331989319033134);\nd1 = ap(hb, 34, d1, 0.17073985049750015);\nd1 = ap(hb, 38, d1, 0.7457135887202412);\nL_v0 = 0.5 * (d0 + d1);\nd0 = L_y3;\nd1 = L_y2;\nd0 = ap(hb, 32, d0, 0.04245470986526787);\nd0 = ap(hb, 36, d0, 0.39331989319033134);\nd1 = ap(hb, 34, d1, 0.17073985049750015);\nd1 = ap(hb, 38, d1, 0.7457135887202412);\nL_v1 = 0.5 * (d0 + d1);\nd0 = L_v1;\nd1 = L_v0;\nd0 = ap(hb, 40, d0, 0.019059005558478156);\nd0 = ap(hb, 44, d0, 0.1559582483500435);\nd0 = ap(hb, 48, d0, 0.3650536901969154);\nd0 = ap(hb, 52, d0, 0.5755010797915323);\nd0 = ap(hb, 56, d0, 0.7526447471286863);\nd0 = ap(hb, 60, d0, 0.8980636464339091);\nd1 = ap(hb, 42, d1, 0.07350243453590219);\nd1 = ap(hb, 46, d1, 0.25649919975582064);\nd1 = ap(hb, 50, d1, 0.47327898479453656);\nd1 = ap(hb, 54, d1, 0.6688095014357188);\nd1 = ap(hb, 58, d1, 0.8282265929955738);\nd1 = ap(hb, 62, d1, 0.9656701590349398);\nL_w = 0.5 * (d0 + d1);\nout1 = L_w;\n\n// ===== lato R =====\nR_e = in2;\nR_o = in2;\nR_e = ap(hb, 64, R_e, 0.019059005558478156);\nR_e = ap(hb, 68, R_e, 0.1559582483500435);\nR_e = ap(hb, 72, R_e, 0.3650536901969154);\nR_e = ap(hb, 76, R_e, 0.5755010797915323);\nR_e = ap(hb, 80, R_e, 0.7526447471286863);\nR_e = ap(hb, 84, R_e, 0.8980636464339091);\nR_o = ap(hb, 66, R_o, 0.07350243453590219);\nR_o = ap(hb, 70, R_o, 0.25649919975582064);\nR_o = ap(hb, 74, R_o, 0.47327898479453656);\nR_o = ap(hb, 78, R_o, 0.6688095014357188);\nR_o = ap(hb, 82, R_o, 0.8282265929955738);\nR_o = ap(hb, 86, R_o, 0.9656701590349398);\nR_u0 = R_e;\nR_u1 = R_e;\nR_u0 = ap(hb, 88, R_u0, 0.04245470986526787);\nR_u0 = ap(hb, 92, R_u0, 0.39331989319033134);\nR_u1 = ap(hb, 90, R_u1, 0.17073985049750015);\nR_u1 = ap(hb, 94, R_u1, 0.7457135887202412);\nR_u2 = R_o;\nR_u3 = R_o;\nR_u2 = ap(hb, 88, R_u2, 0.04245470986526787);\nR_u2 = ap(hb, 92, R_u2, 0.39331989319033134);\nR_u3 = ap(hb, 90, R_u3, 0.17073985049750015);\nR_u3 = ap(hb, 94, R_u3, 0.7457135887202412);\nxa = R_u0;\n// banca: spina HP4 ai 4 crossover\np0 = xa;\np1 = svhp(sv, 64, p0, gx0, 1.4142135623730951);\np1 = svhp(sv, 66, p1, gx0, 1.4142135623730951);\np2 = svhp(sv, 68, p1, gx1, 1.4142135623730951);\np2 = svhp(sv, 70, p2, gx1, 1.4142135623730951);\np3 = svhp(sv, 72, p2, gx2, 1.4142135623730951);\np3 = svhp(sv, 74, p3, gx2, 1.4142135623730951);\np4 = svhp(sv, 76, p3, gx3, 1.4142135623730951);\np4 = svhp(sv, 78, p4, gx3, 1.4142135623730951);\n// vie: LP4 dalla presa e allpass dei crossover sopra\nya = p0;\nya = svlp(sv, 80, ya, gx0, 1.4142135623730951);\nya = svlp(sv, 82, ya, gx0, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 84, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 86, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 88, ya, gx3, 1.4142135623730951);\nv0 = ya;\nya = p1;\nya = svlp(sv, 90, ya, gx1, 1.4142135623730951);\nya = svlp(sv, 92, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 94, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 96, ya, gx3, 1.4142135623730951);\nv1 = ya;\nya = p2;\nya = svlp(sv, 98, ya, gx2, 1.4142135623730951);\nya = svlp(sv, 100, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 102, ya, gx3, 1.4142135623730951);\nv2 = ya;\nya = p3;\nya = svlp(sv, 104, ya, gx3, 1.4142135623730951);\nya = svlp(sv, 106, ya, gx3, 1.4142135623730951);\nv3 = ya;\nzv = v0;\nzs = peek(zk, 15);\nzn = peek(zk, 17);\nzt = 1 - a0;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 16) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 15);\npoke(zk, zv, 16);\npoke(zk, zn, 17);\nz0 = 1 - zs;\nzv = v1;\nzs = peek(zk, 18);\nzn = peek(zk, 20);\nzt = 1 - a1;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 19) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 18);\npoke(zk, zv, 19);\npoke(zk, zn, 20);\nz1 = 1 - zs;\nzv = v2;\nzs = peek(zk, 21);\nzn = peek(zk, 23);\nzt = 1 - a2;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 22) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 21);\npoke(zk, zv, 22);\npoke(zk, zn, 23);\nz2 = 1 - zs;\nzv = v3;\nzs = peek(zk, 24);\nzn = peek(zk, 26);\nzt = 1 - a3;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 25) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 24);\npoke(zk, zv, 25);\npoke(zk, zn, 26);\nz3 = 1 - zs;\nzv = p4;\nzs = peek(zk, 27);\nzn = peek(zk, 29);\nzt = 1 - a4;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 28) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 27);\npoke(zk, zv, 28);\npoke(zk, zn, 29);\nz4 = 1 - zs;\nya = z0 * v0 + z1 * v1 + z2 * v2 + z3 * v3 + z4 * p4;\n// EQ creativo: 5 campane in serie\nya = ya + b1 * ke1 * svbp(sv, 108, ya, ge1, ke1);\nya = ya + b2 * ke2 * svbp(sv, 110, ya, ge2, ke2);\nya = ya + b3 * ke3 * svbp(sv, 112, ya, ge3, ke3);\nya = ya + b4 * ke4 * svbp(sv, 114, ya, ge4, ke4);\nya = ya + b5 * ke5 * svbp(sv, 116, ya, ge5, ke5);\n// GROWL (sotto 350 Hz) e NASTRO, volt del dominio interno\nxa = ya * 2.180432973121504;\ndg = 0;\n// GROWL A BANDE (dec. 165)\ndgb = 0;\nif (wgb > 0) {\ngbl = svlp(sv, 124, xa, gbf, 1.4142135623730951);\ngbl = svlp(sv, 126, gbl, gbf, 1.4142135623730951);\ngbm = op1(sa, 63, xa - gbl, gbfm);\ndgb = 0.9 * hp1(sa, 64, clipbl(gbl, rbl), gbh) - gbl + 0.5011872336272724 * hp1(sa, 65, clipbm(gbm, rbm), gbh) - gbm;\n}\ndg = dg + wgb * (dgb - dg);\ny1 = xa + mg * dg;\n// NASTRO A BANDE (dec. 166)\ndnb = 0;\nif (wn6 > 0) {\nnbu = y1;\nnbp = op1(sa, 66, nbu, gnp);\nnbu = 0.21428571428571427 * nbp + nbu - nbp;\nnbp = op1(sa, 67, nbu, gnp);\nnbu = 0.21428571428571427 * nbp + nbu - nbp;\nnbp = op1(sa, 68, nbu, gnp);\nnbu = 0.21428571428571427 * nbp + nbu - nbp;\nnbp = op1(sa, 69, nbu, gna);\nnbu = nbp + 0.8333333333333334 * (nbu - nbp);\nnbp = op1(sa, 70, nbu, gnt);\nnbu = nbp + 0.3333333333333333 * (nbu - nbp);\nqvin = min(max(gnb * nbu, -16.0), 16.0);\nqvs2 = 2.017546946859815 + peek(sa, 71);\nqid = 0.002241718829844239 + peek(sa, 72);\nqvc = 14.637421755233643 + peek(sa, 73);\nqig = peek(sa, 74);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvd = 1455.0392860607237 * (0.012 + qvc / 48543.68932038835 - qid);\nqtac = qvd - qvc;\npoke(sa, qvs2 + kcb * (qid + qig - qvs2 / 900.0) - 2.017546946859815, 71);\npoke(sa, qid - 0.002241718829844239, 72);\npoke(sa, qvc + kc * qtac - 14.637421755233643, 73);\npoke(sa, qig, 74);\nnbw = -0.1977 * qtac;\nnbp = op1(sa, 75, nbw, gnh);\nnbw = nbp + 0.6748095902284189 * (nbw - nbp);\nnbp = op1(sa, 76, nbw, gnu);\nnbw = nbp + 3.0 * (nbw - nbp);\nnbp = op1(sa, 77, nbw, gnq);\nnbw = 2.9444676075742353 * nbp + nbw - nbp;\nnbp = op1(sa, 78, nbw, gnq);\nnbw = 2.9444676075742353 * nbp + nbw - nbp;\nnbp = op1(sa, 79, nbw, gnq);\nnbw = 2.9444676075742353 * nbp + nbw - nbp;\ndnb = 0.6683439175686147 * nbw - y1;\n}\nR_y0 = (y1 + mtb * dnb) / 2.180432973121504;\nxa = R_u1;\n// banca: spina HP4 ai 4 crossover\np0 = xa;\np1 = svhp(sv, 64, p0, gx0, 1.4142135623730951);\np1 = svhp(sv, 66, p1, gx0, 1.4142135623730951);\np2 = svhp(sv, 68, p1, gx1, 1.4142135623730951);\np2 = svhp(sv, 70, p2, gx1, 1.4142135623730951);\np3 = svhp(sv, 72, p2, gx2, 1.4142135623730951);\np3 = svhp(sv, 74, p3, gx2, 1.4142135623730951);\np4 = svhp(sv, 76, p3, gx3, 1.4142135623730951);\np4 = svhp(sv, 78, p4, gx3, 1.4142135623730951);\n// vie: LP4 dalla presa e allpass dei crossover sopra\nya = p0;\nya = svlp(sv, 80, ya, gx0, 1.4142135623730951);\nya = svlp(sv, 82, ya, gx0, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 84, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 86, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 88, ya, gx3, 1.4142135623730951);\nv0 = ya;\nya = p1;\nya = svlp(sv, 90, ya, gx1, 1.4142135623730951);\nya = svlp(sv, 92, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 94, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 96, ya, gx3, 1.4142135623730951);\nv1 = ya;\nya = p2;\nya = svlp(sv, 98, ya, gx2, 1.4142135623730951);\nya = svlp(sv, 100, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 102, ya, gx3, 1.4142135623730951);\nv2 = ya;\nya = p3;\nya = svlp(sv, 104, ya, gx3, 1.4142135623730951);\nya = svlp(sv, 106, ya, gx3, 1.4142135623730951);\nv3 = ya;\nzv = v0;\nzs = peek(zk, 15);\nzn = peek(zk, 17);\nzt = 1 - a0;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 16) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 15);\npoke(zk, zv, 16);\npoke(zk, zn, 17);\nz0 = 1 - zs;\nzv = v1;\nzs = peek(zk, 18);\nzn = peek(zk, 20);\nzt = 1 - a1;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 19) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 18);\npoke(zk, zv, 19);\npoke(zk, zn, 20);\nz1 = 1 - zs;\nzv = v2;\nzs = peek(zk, 21);\nzn = peek(zk, 23);\nzt = 1 - a2;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 22) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 21);\npoke(zk, zv, 22);\npoke(zk, zn, 23);\nz2 = 1 - zs;\nzv = v3;\nzs = peek(zk, 24);\nzn = peek(zk, 26);\nzt = 1 - a3;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 25) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 24);\npoke(zk, zv, 25);\npoke(zk, zn, 26);\nz3 = 1 - zs;\nzv = p4;\nzs = peek(zk, 27);\nzn = peek(zk, 29);\nzt = 1 - a4;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 28) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 27);\npoke(zk, zv, 28);\npoke(zk, zn, 29);\nz4 = 1 - zs;\nya = z0 * v0 + z1 * v1 + z2 * v2 + z3 * v3 + z4 * p4;\n// EQ creativo: 5 campane in serie\nya = ya + b1 * ke1 * svbp(sv, 108, ya, ge1, ke1);\nya = ya + b2 * ke2 * svbp(sv, 110, ya, ge2, ke2);\nya = ya + b3 * ke3 * svbp(sv, 112, ya, ge3, ke3);\nya = ya + b4 * ke4 * svbp(sv, 114, ya, ge4, ke4);\nya = ya + b5 * ke5 * svbp(sv, 116, ya, ge5, ke5);\n// GROWL (sotto 350 Hz) e NASTRO, volt del dominio interno\nxa = ya * 2.180432973121504;\ndg = 0;\n// GROWL A BANDE (dec. 165)\ndgb = 0;\nif (wgb > 0) {\ngbl = svlp(sv, 124, xa, gbf, 1.4142135623730951);\ngbl = svlp(sv, 126, gbl, gbf, 1.4142135623730951);\ngbm = op1(sa, 63, xa - gbl, gbfm);\ndgb = 0.9 * hp1(sa, 64, clipbl(gbl, rbl), gbh) - gbl + 0.5011872336272724 * hp1(sa, 65, clipbm(gbm, rbm), gbh) - gbm;\n}\ndg = dg + wgb * (dgb - dg);\ny1 = xa + mg * dg;\n// NASTRO A BANDE (dec. 166)\ndnb = 0;\nif (wn6 > 0) {\nnbu = y1;\nnbp = op1(sa, 66, nbu, gnp);\nnbu = 0.21428571428571427 * nbp + nbu - nbp;\nnbp = op1(sa, 67, nbu, gnp);\nnbu = 0.21428571428571427 * nbp + nbu - nbp;\nnbp = op1(sa, 68, nbu, gnp);\nnbu = 0.21428571428571427 * nbp + nbu - nbp;\nnbp = op1(sa, 69, nbu, gna);\nnbu = nbp + 0.8333333333333334 * (nbu - nbp);\nnbp = op1(sa, 70, nbu, gnt);\nnbu = nbp + 0.3333333333333333 * (nbu - nbp);\nqvin = min(max(gnb * nbu, -16.0), 16.0);\nqvs2 = 2.017546946859815 + peek(sa, 71);\nqid = 0.002241718829844239 + peek(sa, 72);\nqvc = 14.637421755233643 + peek(sa, 73);\nqig = peek(sa, 74);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvd = 1455.0392860607237 * (0.012 + qvc / 48543.68932038835 - qid);\nqtac = qvd - qvc;\npoke(sa, qvs2 + kcb * (qid + qig - qvs2 / 900.0) - 2.017546946859815, 71);\npoke(sa, qid - 0.002241718829844239, 72);\npoke(sa, qvc + kc * qtac - 14.637421755233643, 73);\npoke(sa, qig, 74);\nnbw = -0.1977 * qtac;\nnbp = op1(sa, 75, nbw, gnh);\nnbw = nbp + 0.6748095902284189 * (nbw - nbp);\nnbp = op1(sa, 76, nbw, gnu);\nnbw = nbp + 3.0 * (nbw - nbp);\nnbp = op1(sa, 77, nbw, gnq);\nnbw = 2.9444676075742353 * nbp + nbw - nbp;\nnbp = op1(sa, 78, nbw, gnq);\nnbw = 2.9444676075742353 * nbp + nbw - nbp;\nnbp = op1(sa, 79, nbw, gnq);\nnbw = 2.9444676075742353 * nbp + nbw - nbp;\ndnb = 0.6683439175686147 * nbw - y1;\n}\nR_y1 = (y1 + mtb * dnb) / 2.180432973121504;\nxa = R_u2;\n// banca: spina HP4 ai 4 crossover\np0 = xa;\np1 = svhp(sv, 64, p0, gx0, 1.4142135623730951);\np1 = svhp(sv, 66, p1, gx0, 1.4142135623730951);\np2 = svhp(sv, 68, p1, gx1, 1.4142135623730951);\np2 = svhp(sv, 70, p2, gx1, 1.4142135623730951);\np3 = svhp(sv, 72, p2, gx2, 1.4142135623730951);\np3 = svhp(sv, 74, p3, gx2, 1.4142135623730951);\np4 = svhp(sv, 76, p3, gx3, 1.4142135623730951);\np4 = svhp(sv, 78, p4, gx3, 1.4142135623730951);\n// vie: LP4 dalla presa e allpass dei crossover sopra\nya = p0;\nya = svlp(sv, 80, ya, gx0, 1.4142135623730951);\nya = svlp(sv, 82, ya, gx0, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 84, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 86, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 88, ya, gx3, 1.4142135623730951);\nv0 = ya;\nya = p1;\nya = svlp(sv, 90, ya, gx1, 1.4142135623730951);\nya = svlp(sv, 92, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 94, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 96, ya, gx3, 1.4142135623730951);\nv1 = ya;\nya = p2;\nya = svlp(sv, 98, ya, gx2, 1.4142135623730951);\nya = svlp(sv, 100, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 102, ya, gx3, 1.4142135623730951);\nv2 = ya;\nya = p3;\nya = svlp(sv, 104, ya, gx3, 1.4142135623730951);\nya = svlp(sv, 106, ya, gx3, 1.4142135623730951);\nv3 = ya;\nzv = v0;\nzs = peek(zk, 15);\nzn = peek(zk, 17);\nzt = 1 - a0;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 16) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 15);\npoke(zk, zv, 16);\npoke(zk, zn, 17);\nz0 = 1 - zs;\nzv = v1;\nzs = peek(zk, 18);\nzn = peek(zk, 20);\nzt = 1 - a1;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 19) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 18);\npoke(zk, zv, 19);\npoke(zk, zn, 20);\nz1 = 1 - zs;\nzv = v2;\nzs = peek(zk, 21);\nzn = peek(zk, 23);\nzt = 1 - a2;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 22) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 21);\npoke(zk, zv, 22);\npoke(zk, zn, 23);\nz2 = 1 - zs;\nzv = v3;\nzs = peek(zk, 24);\nzn = peek(zk, 26);\nzt = 1 - a3;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 25) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 24);\npoke(zk, zv, 25);\npoke(zk, zn, 26);\nz3 = 1 - zs;\nzv = p4;\nzs = peek(zk, 27);\nzn = peek(zk, 29);\nzt = 1 - a4;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 28) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 27);\npoke(zk, zv, 28);\npoke(zk, zn, 29);\nz4 = 1 - zs;\nya = z0 * v0 + z1 * v1 + z2 * v2 + z3 * v3 + z4 * p4;\n// EQ creativo: 5 campane in serie\nya = ya + b1 * ke1 * svbp(sv, 108, ya, ge1, ke1);\nya = ya + b2 * ke2 * svbp(sv, 110, ya, ge2, ke2);\nya = ya + b3 * ke3 * svbp(sv, 112, ya, ge3, ke3);\nya = ya + b4 * ke4 * svbp(sv, 114, ya, ge4, ke4);\nya = ya + b5 * ke5 * svbp(sv, 116, ya, ge5, ke5);\n// GROWL (sotto 350 Hz) e NASTRO, volt del dominio interno\nxa = ya * 2.180432973121504;\ndg = 0;\n// GROWL A BANDE (dec. 165)\ndgb = 0;\nif (wgb > 0) {\ngbl = svlp(sv, 124, xa, gbf, 1.4142135623730951);\ngbl = svlp(sv, 126, gbl, gbf, 1.4142135623730951);\ngbm = op1(sa, 63, xa - gbl, gbfm);\ndgb = 0.9 * hp1(sa, 64, clipbl(gbl, rbl), gbh) - gbl + 0.5011872336272724 * hp1(sa, 65, clipbm(gbm, rbm), gbh) - gbm;\n}\ndg = dg + wgb * (dgb - dg);\ny1 = xa + mg * dg;\n// NASTRO A BANDE (dec. 166)\ndnb = 0;\nif (wn6 > 0) {\nnbu = y1;\nnbp = op1(sa, 66, nbu, gnp);\nnbu = 0.21428571428571427 * nbp + nbu - nbp;\nnbp = op1(sa, 67, nbu, gnp);\nnbu = 0.21428571428571427 * nbp + nbu - nbp;\nnbp = op1(sa, 68, nbu, gnp);\nnbu = 0.21428571428571427 * nbp + nbu - nbp;\nnbp = op1(sa, 69, nbu, gna);\nnbu = nbp + 0.8333333333333334 * (nbu - nbp);\nnbp = op1(sa, 70, nbu, gnt);\nnbu = nbp + 0.3333333333333333 * (nbu - nbp);\nqvin = min(max(gnb * nbu, -16.0), 16.0);\nqvs2 = 2.017546946859815 + peek(sa, 71);\nqid = 0.002241718829844239 + peek(sa, 72);\nqvc = 14.637421755233643 + peek(sa, 73);\nqig = peek(sa, 74);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvd = 1455.0392860607237 * (0.012 + qvc / 48543.68932038835 - qid);\nqtac = qvd - qvc;\npoke(sa, qvs2 + kcb * (qid + qig - qvs2 / 900.0) - 2.017546946859815, 71);\npoke(sa, qid - 0.002241718829844239, 72);\npoke(sa, qvc + kc * qtac - 14.637421755233643, 73);\npoke(sa, qig, 74);\nnbw = -0.1977 * qtac;\nnbp = op1(sa, 75, nbw, gnh);\nnbw = nbp + 0.6748095902284189 * (nbw - nbp);\nnbp = op1(sa, 76, nbw, gnu);\nnbw = nbp + 3.0 * (nbw - nbp);\nnbp = op1(sa, 77, nbw, gnq);\nnbw = 2.9444676075742353 * nbp + nbw - nbp;\nnbp = op1(sa, 78, nbw, gnq);\nnbw = 2.9444676075742353 * nbp + nbw - nbp;\nnbp = op1(sa, 79, nbw, gnq);\nnbw = 2.9444676075742353 * nbp + nbw - nbp;\ndnb = 0.6683439175686147 * nbw - y1;\n}\nR_y2 = (y1 + mtb * dnb) / 2.180432973121504;\nxa = R_u3;\n// banca: spina HP4 ai 4 crossover\np0 = xa;\np1 = svhp(sv, 64, p0, gx0, 1.4142135623730951);\np1 = svhp(sv, 66, p1, gx0, 1.4142135623730951);\np2 = svhp(sv, 68, p1, gx1, 1.4142135623730951);\np2 = svhp(sv, 70, p2, gx1, 1.4142135623730951);\np3 = svhp(sv, 72, p2, gx2, 1.4142135623730951);\np3 = svhp(sv, 74, p3, gx2, 1.4142135623730951);\np4 = svhp(sv, 76, p3, gx3, 1.4142135623730951);\np4 = svhp(sv, 78, p4, gx3, 1.4142135623730951);\n// vie: LP4 dalla presa e allpass dei crossover sopra\nya = p0;\nya = svlp(sv, 80, ya, gx0, 1.4142135623730951);\nya = svlp(sv, 82, ya, gx0, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 84, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 86, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 88, ya, gx3, 1.4142135623730951);\nv0 = ya;\nya = p1;\nya = svlp(sv, 90, ya, gx1, 1.4142135623730951);\nya = svlp(sv, 92, ya, gx1, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 94, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 96, ya, gx3, 1.4142135623730951);\nv1 = ya;\nya = p2;\nya = svlp(sv, 98, ya, gx2, 1.4142135623730951);\nya = svlp(sv, 100, ya, gx2, 1.4142135623730951);\nya = ya - 2.8284271247461903 * svbp(sv, 102, ya, gx3, 1.4142135623730951);\nv2 = ya;\nya = p3;\nya = svlp(sv, 104, ya, gx3, 1.4142135623730951);\nya = svlp(sv, 106, ya, gx3, 1.4142135623730951);\nv3 = ya;\nzv = v0;\nzs = peek(zk, 15);\nzn = peek(zk, 17);\nzt = 1 - a0;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 16) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 15);\npoke(zk, zv, 16);\npoke(zk, zn, 17);\nz0 = 1 - zs;\nzv = v1;\nzs = peek(zk, 18);\nzn = peek(zk, 20);\nzt = 1 - a1;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 19) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 18);\npoke(zk, zv, 19);\npoke(zk, zn, 20);\nz1 = 1 - zs;\nzv = v2;\nzs = peek(zk, 21);\nzn = peek(zk, 23);\nzt = 1 - a2;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 22) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 21);\npoke(zk, zv, 22);\npoke(zk, zn, 23);\nz2 = 1 - zs;\nzv = v3;\nzs = peek(zk, 24);\nzn = peek(zk, 26);\nzt = 1 - a3;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 25) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 24);\npoke(zk, zv, 25);\npoke(zk, zn, 26);\nz3 = 1 - zs;\nzv = p4;\nzs = peek(zk, 27);\nzn = peek(zk, 29);\nzt = 1 - a4;\nzc = abs(zt - zs) > 0.5;\nzn = zc * (zn + 1);\nzw = zc * max(peek(zk, 28) * zv <= 0, zn >= ztm);\nzs = zs + zw * (zt - zs);\npoke(zk, zs, 27);\npoke(zk, zv, 28);\npoke(zk, zn, 29);\nz4 = 1 - zs;\nya = z0 * v0 + z1 * v1 + z2 * v2 + z3 * v3 + z4 * p4;\n// EQ creativo: 5 campane in serie\nya = ya + b1 * ke1 * svbp(sv, 108, ya, ge1, ke1);\nya = ya + b2 * ke2 * svbp(sv, 110, ya, ge2, ke2);\nya = ya + b3 * ke3 * svbp(sv, 112, ya, ge3, ke3);\nya = ya + b4 * ke4 * svbp(sv, 114, ya, ge4, ke4);\nya = ya + b5 * ke5 * svbp(sv, 116, ya, ge5, ke5);\n// GROWL (sotto 350 Hz) e NASTRO, volt del dominio interno\nxa = ya * 2.180432973121504;\ndg = 0;\n// GROWL A BANDE (dec. 165)\ndgb = 0;\nif (wgb > 0) {\ngbl = svlp(sv, 124, xa, gbf, 1.4142135623730951);\ngbl = svlp(sv, 126, gbl, gbf, 1.4142135623730951);\ngbm = op1(sa, 63, xa - gbl, gbfm);\ndgb = 0.9 * hp1(sa, 64, clipbl(gbl, rbl), gbh) - gbl + 0.5011872336272724 * hp1(sa, 65, clipbm(gbm, rbm), gbh) - gbm;\n}\ndg = dg + wgb * (dgb - dg);\ny1 = xa + mg * dg;\n// NASTRO A BANDE (dec. 166)\ndnb = 0;\nif (wn6 > 0) {\nnbu = y1;\nnbp = op1(sa, 66, nbu, gnp);\nnbu = 0.21428571428571427 * nbp + nbu - nbp;\nnbp = op1(sa, 67, nbu, gnp);\nnbu = 0.21428571428571427 * nbp + nbu - nbp;\nnbp = op1(sa, 68, nbu, gnp);\nnbu = 0.21428571428571427 * nbp + nbu - nbp;\nnbp = op1(sa, 69, nbu, gna);\nnbu = nbp + 0.8333333333333334 * (nbu - nbp);\nnbp = op1(sa, 70, nbu, gnt);\nnbu = nbp + 0.3333333333333333 * (nbu - nbp);\nqvin = min(max(gnb * nbu, -16.0), 16.0);\nqvs2 = 2.017546946859815 + peek(sa, 71);\nqid = 0.002241718829844239 + peek(sa, 72);\nqvc = 14.637421755233643 + peek(sa, 73);\nqig = peek(sa, 74);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvg = gatev(qvin, qvs2 + 150.0 * (qid + qig));\nqig = (qvin - qvg) / 10000.0;\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqid = jstep(qvg, qvs2 + 150.0 * qig, qvc, qid);\nqvd = 1455.0392860607237 * (0.012 + qvc / 48543.68932038835 - qid);\nqtac = qvd - qvc;\npoke(sa, qvs2 + kcb * (qid + qig - qvs2 / 900.0) - 2.017546946859815, 71);\npoke(sa, qid - 0.002241718829844239, 72);\npoke(sa, qvc + kc * qtac - 14.637421755233643, 73);\npoke(sa, qig, 74);\nnbw = -0.1977 * qtac;\nnbp = op1(sa, 75, nbw, gnh);\nnbw = nbp + 0.6748095902284189 * (nbw - nbp);\nnbp = op1(sa, 76, nbw, gnu);\nnbw = nbp + 3.0 * (nbw - nbp);\nnbp = op1(sa, 77, nbw, gnq);\nnbw = 2.9444676075742353 * nbp + nbw - nbp;\nnbp = op1(sa, 78, nbw, gnq);\nnbw = 2.9444676075742353 * nbp + nbw - nbp;\nnbp = op1(sa, 79, nbw, gnq);\nnbw = 2.9444676075742353 * nbp + nbw - nbp;\ndnb = 0.6683439175686147 * nbw - y1;\n}\nR_y3 = (y1 + mtb * dnb) / 2.180432973121504;\nif (wgb == 0) {\npoke(sv, 0, 124);\npoke(sv, 0, 125);\npoke(sv, 0, 126);\npoke(sv, 0, 127);\npoke(sa, 0, 63);\npoke(sa, 0, 64);\npoke(sa, 0, 65);\n}\nif (wn6 == 0) {\npoke(sa, 0, 66);\npoke(sa, 0, 67);\npoke(sa, 0, 68);\npoke(sa, 0, 69);\npoke(sa, 0, 70);\npoke(sa, 0, 71);\npoke(sa, 0, 72);\npoke(sa, 0, 73);\npoke(sa, 0, 74);\npoke(sa, 0, 75);\npoke(sa, 0, 76);\npoke(sa, 0, 77);\npoke(sa, 0, 78);\npoke(sa, 0, 79);\n}\nd0 = R_y1;\nd1 = R_y0;\nd0 = ap(hb, 96, d0, 0.04245470986526787);\nd0 = ap(hb, 100, d0, 0.39331989319033134);\nd1 = ap(hb, 98, d1, 0.17073985049750015);\nd1 = ap(hb, 102, d1, 0.7457135887202412);\nR_v0 = 0.5 * (d0 + d1);\nd0 = R_y3;\nd1 = R_y2;\nd0 = ap(hb, 96, d0, 0.04245470986526787);\nd0 = ap(hb, 100, d0, 0.39331989319033134);\nd1 = ap(hb, 98, d1, 0.17073985049750015);\nd1 = ap(hb, 102, d1, 0.7457135887202412);\nR_v1 = 0.5 * (d0 + d1);\nd0 = R_v1;\nd1 = R_v0;\nd0 = ap(hb, 104, d0, 0.019059005558478156);\nd0 = ap(hb, 108, d0, 0.1559582483500435);\nd0 = ap(hb, 112, d0, 0.3650536901969154);\nd0 = ap(hb, 116, d0, 0.5755010797915323);\nd0 = ap(hb, 120, d0, 0.7526447471286863);\nd0 = ap(hb, 124, d0, 0.8980636464339091);\nd1 = ap(hb, 106, d1, 0.07350243453590219);\nd1 = ap(hb, 110, d1, 0.25649919975582064);\nd1 = ap(hb, 114, d1, 0.47327898479453656);\nd1 = ap(hb, 118, d1, 0.6688095014357188);\nd1 = ap(hb, 122, d1, 0.8282265929955738);\nd1 = ap(hb, 126, d1, 0.9656701590349398);\nR_w = 0.5 * (d0 + d1);\nout2 = R_w;\n\n",
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
						40
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
						66,
						54,
						40
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
					"maxclass": "live.dial",
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
						108,
						54,
						40
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "EQ1 WIDTH",
							"parameter_shortname": "EQ1 WIDTH",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								50.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "EQ1 WIDTH",
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
						40
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
						66,
						54,
						40
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
					"maxclass": "live.dial",
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
						108,
						54,
						40
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "EQ2 WIDTH",
							"parameter_shortname": "EQ2 WIDTH",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								50.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "EQ2 WIDTH",
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
						40
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
						66,
						54,
						40
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
					"maxclass": "live.dial",
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
						108,
						54,
						40
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "EQ3 WIDTH",
							"parameter_shortname": "EQ3 WIDTH",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								50.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "EQ3 WIDTH",
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
						40
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
						66,
						54,
						40
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
					"maxclass": "live.dial",
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
						108,
						54,
						40
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "EQ4 WIDTH",
							"parameter_shortname": "EQ4 WIDTH",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								50.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "EQ4 WIDTH",
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
						40
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
						66,
						54,
						40
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
					"maxclass": "live.dial",
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
						108,
						54,
						40
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "EQ5 WIDTH",
							"parameter_shortname": "EQ5 WIDTH",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								50.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "EQ5 WIDTH",
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
					"id": "obj-nota",
					"maxclass": "live.comment",
					"numinlets": 1,
					"numoutlets": 0,
					"presentation": 1,
					"presentation_rect": [
						8,
						150,
						490,
						18
					],
					"patching_rect": [
						20,
						520,
						490,
						18
					],
					"text": "Semplice (dec. 175): CROSSOVER H 60/250/1,2k/8k, GROWL BANDE, NASTRO BANDE B9. 0 dBu = -12 dBFS."
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