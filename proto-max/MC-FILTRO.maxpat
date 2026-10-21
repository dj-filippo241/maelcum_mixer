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
									"code": "// MC-FILTRO - prototipo Max P1 (parte 1) del filtro maelcum_mixer.\n// GENERATO da proto-max/coefficienti/genera_filtro.py: non modificare.\n// SVF 4 poli (Q 0,541 fissa + Q 1,307 con RES), core OTA (a') col\n// tetto di 1,55 V o pulito (c-B), limitatore a diodi. Banca a 4x.\n\n// allpass del 1o ordine del halfband; stato in m[i] (x), m[i+1] (y)\nap(m, i, x, c) {\n\ty = c * (x - peek(m, i + 1)) + peek(m, i);\n\tpoke(m, x, i);\n\tpoke(m, y, i + 1);\n\treturn y;\n}\n\n// guadagno a secante dell'OTA: Vs tanh(u/Vs)/u\naota(u) {\n\tm = max(abs(u), 0.000001);\n\treturn 1.55112 * tanh(m / 1.55112) / m;\n}\n\n// softplus limitato (niente overflow)\nspl(z) {\n\treturn log(1 + exp(min(z, 30))) + max(z - 30, 0);\n}\n\n// conduttanza a secante del limitatore a diodi (4,7k + 2+2 1N4148)\nalim(v) {\n\tm = max(abs(v), 0.000001);\n\treturn 1.7 * 0.06 * (spl((m - 0.82) / 0.06) - spl(-13.666666666666666)) / m;\n}\n\n// tosatore dell'overdrive: 2,2k + 2+2 1N4148, tre passi di Newton\nclipd(v) {\n\ta = abs(v);\n\tt = a / 1.1088e-05;\n\tw = min(a, 0.09063096 * log(t + sqrt(t * t + 1)));\n\tex = exp(w / 0.09063096);\n\tf = (a - w) / 2200.0 - 2.52e-09 * (ex - 1 / ex);\n\tdf = -1 / 2200.0 - 2.52e-09 * (ex + 1 / ex) / 0.09063096;\n\tw = w - f / df;\n\tex = exp(w / 0.09063096);\n\tf = (a - w) / 2200.0 - 2.52e-09 * (ex - 1 / ex);\n\tdf = -1 / 2200.0 - 2.52e-09 * (ex + 1 / ex) / 0.09063096;\n\tw = w - f / df;\n\tex = exp(w / 0.09063096);\n\tf = (a - w) / 2200.0 - 2.52e-09 * (ex - 1 / ex);\n\tdf = -1 / 2200.0 - 2.52e-09 * (ex + 1 / ex) / 0.09063096;\n\tw = w - f / df;\n\treturn w * ((v >= 0) * 2 - 1);\n}\n\n// sezione SVF 2 poli TPT; stato in m[i..i+3] = s1, s2, hp, bp\n// d = 1/Q. Varianti senza rami morti (CPU): a = core OTA\n// (guadagno a secante), c = integratori lineari; 1 = col limitatore.\n// Un solo valore di ritorno per funzione (regola gen~): _hp o _lp\nsez_a0_hp(m, i, x, g, d) {\n\ts1 = peek(m, i);\n\ts2 = peek(m, i + 1);\n\tbpv = peek(m, i + 3);\n\tab = aota(bpv);\n\tg1 = g * aota(peek(m, i + 2));\n\tg2 = g * ab;\n\trr = d * ab;\n\tbp = (g1 * (x - s2) + s1) / (1 + g1 * g2 + g1 * rr);\n\thp = x - s2 - (g2 + rr) * bp;\n\tlp = g2 * bp + s2;\n\tpoke(m, bp + g1 * hp, i);\n\tpoke(m, lp + g2 * bp, i + 1);\n\tpoke(m, hp, i + 2);\n\tpoke(m, bp, i + 3);\n\treturn hp;\n}\n\nsez_a0_lp(m, i, x, g, d) {\n\ts1 = peek(m, i);\n\ts2 = peek(m, i + 1);\n\tbpv = peek(m, i + 3);\n\tab = aota(bpv);\n\tg1 = g * aota(peek(m, i + 2));\n\tg2 = g * ab;\n\trr = d * ab;\n\tbp = (g1 * (x - s2) + s1) / (1 + g1 * g2 + g1 * rr);\n\thp = x - s2 - (g2 + rr) * bp;\n\tlp = g2 * bp + s2;\n\tpoke(m, bp + g1 * hp, i);\n\tpoke(m, lp + g2 * bp, i + 1);\n\tpoke(m, hp, i + 2);\n\tpoke(m, bp, i + 3);\n\treturn lp;\n}\n\nsez_a1_hp(m, i, x, g, d) {\n\ts1 = peek(m, i);\n\ts2 = peek(m, i + 1);\n\tbpv = peek(m, i + 3);\n\tab = aota(bpv);\n\tg1 = g * aota(peek(m, i + 2));\n\tg2 = g * ab;\n\trr = d * ab + alim(bpv);\n\tbp = (g1 * (x - s2) + s1) / (1 + g1 * g2 + g1 * rr);\n\thp = x - s2 - (g2 + rr) * bp;\n\tlp = g2 * bp + s2;\n\tpoke(m, bp + g1 * hp, i);\n\tpoke(m, lp + g2 * bp, i + 1);\n\tpoke(m, hp, i + 2);\n\tpoke(m, bp, i + 3);\n\treturn hp;\n}\n\nsez_a1_lp(m, i, x, g, d) {\n\ts1 = peek(m, i);\n\ts2 = peek(m, i + 1);\n\tbpv = peek(m, i + 3);\n\tab = aota(bpv);\n\tg1 = g * aota(peek(m, i + 2));\n\tg2 = g * ab;\n\trr = d * ab + alim(bpv);\n\tbp = (g1 * (x - s2) + s1) / (1 + g1 * g2 + g1 * rr);\n\thp = x - s2 - (g2 + rr) * bp;\n\tlp = g2 * bp + s2;\n\tpoke(m, bp + g1 * hp, i);\n\tpoke(m, lp + g2 * bp, i + 1);\n\tpoke(m, hp, i + 2);\n\tpoke(m, bp, i + 3);\n\treturn lp;\n}\n\nsez_c0_hp(m, i, x, g, d) {\n\ts1 = peek(m, i);\n\ts2 = peek(m, i + 1);\n\tbpv = peek(m, i + 3);\n\tg1 = g;\n\tg2 = g;\n\trr = d;\n\tbp = (g1 * (x - s2) + s1) / (1 + g1 * g2 + g1 * rr);\n\thp = x - s2 - (g2 + rr) * bp;\n\tlp = g2 * bp + s2;\n\tpoke(m, bp + g1 * hp, i);\n\tpoke(m, lp + g2 * bp, i + 1);\n\tpoke(m, hp, i + 2);\n\tpoke(m, bp, i + 3);\n\treturn hp;\n}\n\nsez_c0_lp(m, i, x, g, d) {\n\ts1 = peek(m, i);\n\ts2 = peek(m, i + 1);\n\tbpv = peek(m, i + 3);\n\tg1 = g;\n\tg2 = g;\n\trr = d;\n\tbp = (g1 * (x - s2) + s1) / (1 + g1 * g2 + g1 * rr);\n\thp = x - s2 - (g2 + rr) * bp;\n\tlp = g2 * bp + s2;\n\tpoke(m, bp + g1 * hp, i);\n\tpoke(m, lp + g2 * bp, i + 1);\n\tpoke(m, hp, i + 2);\n\tpoke(m, bp, i + 3);\n\treturn lp;\n}\n\nsez_c1_hp(m, i, x, g, d) {\n\ts1 = peek(m, i);\n\ts2 = peek(m, i + 1);\n\tbpv = peek(m, i + 3);\n\tg1 = g;\n\tg2 = g;\n\trr = d + alim(bpv);\n\tbp = (g1 * (x - s2) + s1) / (1 + g1 * g2 + g1 * rr);\n\thp = x - s2 - (g2 + rr) * bp;\n\tlp = g2 * bp + s2;\n\tpoke(m, bp + g1 * hp, i);\n\tpoke(m, lp + g2 * bp, i + 1);\n\tpoke(m, hp, i + 2);\n\tpoke(m, bp, i + 3);\n\treturn hp;\n}\n\nsez_c1_lp(m, i, x, g, d) {\n\ts1 = peek(m, i);\n\ts2 = peek(m, i + 1);\n\tbpv = peek(m, i + 3);\n\tg1 = g;\n\tg2 = g;\n\trr = d + alim(bpv);\n\tbp = (g1 * (x - s2) + s1) / (1 + g1 * g2 + g1 * rr);\n\thp = x - s2 - (g2 + rr) * bp;\n\tlp = g2 * bp + s2;\n\tpoke(m, bp + g1 * hp, i);\n\tpoke(m, lp + g2 * bp, i + 1);\n\tpoke(m, hp, i + 2);\n\tpoke(m, bp, i + 3);\n\treturn lp;\n}\n\nParam freq_hp(0.0, min=0, max=100);\nParam res_hp(0.0, min=0, max=100);\nParam drive_hp(0.0, min=0, max=100);\nParam freq_lp(100.0, min=0, max=100);\nParam res_lp(0.0, min=0, max=100);\nParam drive_lp(0.0, min=0, max=100);\nParam modo(1, min=0, max=2);\nParam core(0, min=0, max=1);\nParam pend(0, min=0, max=2);\nData st(64);\nData hb(128);\nHistory s_freq_hp(0.0);\nHistory s_res_hp(0.0);\nHistory s_drive_hp(0.0);\nHistory s_freq_lp(100.0);\nHistory s_res_lp(0.0);\nHistory s_drive_lp(0.0);\nHistory s_modo(1);\nHistory s_core(0);\nHistory s_pend(0);\n\n// manopole lisciate 10 ms; MODO 1 ms (rampa, dec. 80); CORE 20 ms\nt1 = exp(-1 / (0.001 * samplerate));\nt10 = exp(-1 / (0.010 * samplerate));\nt20 = exp(-1 / (0.020 * samplerate));\ns_freq_hp = freq_hp + t10 * (s_freq_hp - freq_hp);\ns_res_hp = res_hp + t10 * (s_res_hp - res_hp);\ns_drive_hp = drive_hp + t10 * (s_drive_hp - drive_hp);\ns_freq_lp = freq_lp + t10 * (s_freq_lp - freq_lp);\ns_res_lp = res_lp + t10 * (s_res_lp - res_lp);\ns_drive_lp = drive_lp + t10 * (s_drive_lp - drive_lp);\ns_modo = modo + t1 * (s_modo - modo);\ns_core = core + t20 * (s_core - core);\ns_pend = pend + t20 * (s_pend - pend);\nw_hp = max(0, 1 - abs(s_modo));\nw_off = max(0, 1 - abs(s_modo - 1));\nw_lp = max(0, 1 - abs(s_modo - 2));\n// si calcola solo il core che si sente (CPU: traccia su un core)\non_a = 1 - s_core > 1e-05;\non_c = s_core > 1e-05;\n\nsr4 = samplerate * 4;\n// PENDENZA: Q e frequenze delle due sezioni, scivolano in 20 ms\nwp0 = max(0, 1 - abs(s_pend - 0));\nwp1 = max(0, 1 - abs(s_pend - 1));\nwp2 = max(0, 1 - abs(s_pend - 2));\nq1i = wp0 * 1.8477457501847745 + wp1 * 1.4142271248762552 + wp2 * 1.9160758766047135;\nm1 = wp0 * 1.0 + wp1 * 1.0 + wp2 * 1.4192;\nq2i = wp0 * 0.765345170671973 + wp1 * 1.4142271248762552 + wp2 * 1.2414649286157666;\nm2 = wp0 * 1.0 + wp1 * 1.0 + wp2 * 1.5912;\ndq1 = q1i;\n// sezione HP: FREQ dec. 102 (a), RES dec. 102 (b)\nth = s_freq_hp / 100;\nf_hp = (th < 0.05) * 10 * pow(2, th / 0.05) + (th >= 0.05) * (th <= 0.95) * 20 * pow(1000, (th - 0.05) / 0.9) + (th > 0.95) * 20000 * pow(1.75, (th - 0.95) / 0.05);\ng_hp1 = tan(pi * f_hp / m1 / sr4);\ng_hp2 = tan(pi * f_hp / m2 / sr4);\nod_hp = pow(s_drive_hp / 100, 2.5);\ntr = s_res_hp / 100;\ngr = (tr <= 0.9) * (1 - tr / 0.9) + (tr > 0.9) * (-0.75 * (tr - 0.9) / 0.1);\nd_hp = (gr > 0) * gr * q2i + (gr <= 0) * 1.4142135623730951 * gr;\n// sezione LP: FREQ dec. 102 (a), RES dec. 102 (b)\nth = s_freq_lp / 100;\nf_lp = (th < 0.05) * 10 * pow(2, th / 0.05) + (th >= 0.05) * (th <= 0.95) * 20 * pow(1000, (th - 0.05) / 0.9) + (th > 0.95) * 20000 * pow(1.75, (th - 0.95) / 0.05);\ng_lp1 = tan(pi * f_lp * m1 / sr4);\ng_lp2 = tan(pi * f_lp * m2 / sr4);\nod_lp = pow(s_drive_lp / 100, 2.5);\ntr = s_res_lp / 100;\ngr = (tr <= 0.9) * (1 - tr / 0.9) + (tr > 0.9) * (-0.75 * (tr - 0.9) / 0.1);\nd_lp = (gr > 0) * gr * q2i + (gr <= 0) * 1.4142135623730951 * gr;\n\n// livelli: 1,0 digitale = 4.361 V (0 dBu = -12 dBFS)\n// ===== lato L =====\nL_e = in1;\nL_o = in1;\nL_e = ap(hb, 0, L_e, 0.019059005558478156);\nL_e = ap(hb, 4, L_e, 0.1559582483500435);\nL_e = ap(hb, 8, L_e, 0.3650536901969154);\nL_e = ap(hb, 12, L_e, 0.5755010797915323);\nL_e = ap(hb, 16, L_e, 0.7526447471286863);\nL_e = ap(hb, 20, L_e, 0.8980636464339091);\nL_o = ap(hb, 2, L_o, 0.07350243453590219);\nL_o = ap(hb, 6, L_o, 0.25649919975582064);\nL_o = ap(hb, 10, L_o, 0.47327898479453656);\nL_o = ap(hb, 14, L_o, 0.6688095014357188);\nL_o = ap(hb, 18, L_o, 0.8282265929955738);\nL_o = ap(hb, 22, L_o, 0.9656701590349398);\nL_u0 = L_e;\nL_u1 = L_e;\nL_u0 = ap(hb, 24, L_u0, 0.04245470986526787);\nL_u0 = ap(hb, 28, L_u0, 0.39331989319033134);\nL_u1 = ap(hb, 26, L_u1, 0.17073985049750015);\nL_u1 = ap(hb, 30, L_u1, 0.7457135887202412);\nL_u2 = L_o;\nL_u3 = L_o;\nL_u2 = ap(hb, 24, L_u2, 0.04245470986526787);\nL_u2 = ap(hb, 28, L_u2, 0.39331989319033134);\nL_u3 = ap(hb, 26, L_u3, 0.17073985049750015);\nL_u3 = ap(hb, 30, L_u3, 0.7457135887202412);\nxin = L_u0 * 4.360865946243008 + noise() * 0.00001;\nahph = 0;\nalpl = 0;\nif (on_a) {\nahph = sez_a0_hp(st, 0, xin, g_hp1, dq1);\nahph = sez_a1_hp(st, 4, ahph, g_hp2, d_hp);\nalpl = sez_a0_lp(st, 8, xin, g_lp1, dq1);\nalpl = sez_a1_lp(st, 12, alpl, g_lp2, d_lp);\n}\nchph = 0;\nclpl = 0;\nif (on_c) {\nchph = sez_c0_hp(st, 16, xin, g_hp1, dq1);\nchph = sez_c1_hp(st, 20, chph, g_hp2, d_hp);\nclpl = sez_c0_lp(st, 24, xin, g_lp1, dq1);\nclpl = sez_c1_lp(st, 28, clpl, g_lp2, d_lp);\n}\nohp = (1 - s_core) * ahph + s_core * chph;\nif (od_hp > 1e-09) {\nohp = ohp + od_hp * (1.171 * clipd(2 * ohp) - ohp);\n}\nolp = (1 - s_core) * alpl + s_core * clpl;\nif (od_lp > 1e-09) {\nolp = olp + od_lp * (1.171 * clipd(2 * olp) - olp);\n}\nL_y0 = (w_off * xin + w_hp * ohp + w_lp * olp) / 4.360865946243008;\nxin = L_u1 * 4.360865946243008 + noise() * 0.00001;\nahph = 0;\nalpl = 0;\nif (on_a) {\nahph = sez_a0_hp(st, 0, xin, g_hp1, dq1);\nahph = sez_a1_hp(st, 4, ahph, g_hp2, d_hp);\nalpl = sez_a0_lp(st, 8, xin, g_lp1, dq1);\nalpl = sez_a1_lp(st, 12, alpl, g_lp2, d_lp);\n}\nchph = 0;\nclpl = 0;\nif (on_c) {\nchph = sez_c0_hp(st, 16, xin, g_hp1, dq1);\nchph = sez_c1_hp(st, 20, chph, g_hp2, d_hp);\nclpl = sez_c0_lp(st, 24, xin, g_lp1, dq1);\nclpl = sez_c1_lp(st, 28, clpl, g_lp2, d_lp);\n}\nohp = (1 - s_core) * ahph + s_core * chph;\nif (od_hp > 1e-09) {\nohp = ohp + od_hp * (1.171 * clipd(2 * ohp) - ohp);\n}\nolp = (1 - s_core) * alpl + s_core * clpl;\nif (od_lp > 1e-09) {\nolp = olp + od_lp * (1.171 * clipd(2 * olp) - olp);\n}\nL_y1 = (w_off * xin + w_hp * ohp + w_lp * olp) / 4.360865946243008;\nxin = L_u2 * 4.360865946243008 + noise() * 0.00001;\nahph = 0;\nalpl = 0;\nif (on_a) {\nahph = sez_a0_hp(st, 0, xin, g_hp1, dq1);\nahph = sez_a1_hp(st, 4, ahph, g_hp2, d_hp);\nalpl = sez_a0_lp(st, 8, xin, g_lp1, dq1);\nalpl = sez_a1_lp(st, 12, alpl, g_lp2, d_lp);\n}\nchph = 0;\nclpl = 0;\nif (on_c) {\nchph = sez_c0_hp(st, 16, xin, g_hp1, dq1);\nchph = sez_c1_hp(st, 20, chph, g_hp2, d_hp);\nclpl = sez_c0_lp(st, 24, xin, g_lp1, dq1);\nclpl = sez_c1_lp(st, 28, clpl, g_lp2, d_lp);\n}\nohp = (1 - s_core) * ahph + s_core * chph;\nif (od_hp > 1e-09) {\nohp = ohp + od_hp * (1.171 * clipd(2 * ohp) - ohp);\n}\nolp = (1 - s_core) * alpl + s_core * clpl;\nif (od_lp > 1e-09) {\nolp = olp + od_lp * (1.171 * clipd(2 * olp) - olp);\n}\nL_y2 = (w_off * xin + w_hp * ohp + w_lp * olp) / 4.360865946243008;\nxin = L_u3 * 4.360865946243008 + noise() * 0.00001;\nahph = 0;\nalpl = 0;\nif (on_a) {\nahph = sez_a0_hp(st, 0, xin, g_hp1, dq1);\nahph = sez_a1_hp(st, 4, ahph, g_hp2, d_hp);\nalpl = sez_a0_lp(st, 8, xin, g_lp1, dq1);\nalpl = sez_a1_lp(st, 12, alpl, g_lp2, d_lp);\n}\nchph = 0;\nclpl = 0;\nif (on_c) {\nchph = sez_c0_hp(st, 16, xin, g_hp1, dq1);\nchph = sez_c1_hp(st, 20, chph, g_hp2, d_hp);\nclpl = sez_c0_lp(st, 24, xin, g_lp1, dq1);\nclpl = sez_c1_lp(st, 28, clpl, g_lp2, d_lp);\n}\nohp = (1 - s_core) * ahph + s_core * chph;\nif (od_hp > 1e-09) {\nohp = ohp + od_hp * (1.171 * clipd(2 * ohp) - ohp);\n}\nolp = (1 - s_core) * alpl + s_core * clpl;\nif (od_lp > 1e-09) {\nolp = olp + od_lp * (1.171 * clipd(2 * olp) - olp);\n}\nL_y3 = (w_off * xin + w_hp * ohp + w_lp * olp) / 4.360865946243008;\nif (on_a == 0) {\npoke(st, 0, 0);\npoke(st, 0, 1);\npoke(st, 0, 2);\npoke(st, 0, 3);\npoke(st, 0, 4);\npoke(st, 0, 5);\npoke(st, 0, 6);\npoke(st, 0, 7);\npoke(st, 0, 8);\npoke(st, 0, 9);\npoke(st, 0, 10);\npoke(st, 0, 11);\npoke(st, 0, 12);\npoke(st, 0, 13);\npoke(st, 0, 14);\npoke(st, 0, 15);\n}\nif (on_c == 0) {\npoke(st, 0, 16);\npoke(st, 0, 17);\npoke(st, 0, 18);\npoke(st, 0, 19);\npoke(st, 0, 20);\npoke(st, 0, 21);\npoke(st, 0, 22);\npoke(st, 0, 23);\npoke(st, 0, 24);\npoke(st, 0, 25);\npoke(st, 0, 26);\npoke(st, 0, 27);\npoke(st, 0, 28);\npoke(st, 0, 29);\npoke(st, 0, 30);\npoke(st, 0, 31);\n}\nd0 = L_y1;\nd1 = L_y0;\nd0 = ap(hb, 32, d0, 0.04245470986526787);\nd0 = ap(hb, 36, d0, 0.39331989319033134);\nd1 = ap(hb, 34, d1, 0.17073985049750015);\nd1 = ap(hb, 38, d1, 0.7457135887202412);\nL_v0 = 0.5 * (d0 + d1);\nd0 = L_y3;\nd1 = L_y2;\nd0 = ap(hb, 32, d0, 0.04245470986526787);\nd0 = ap(hb, 36, d0, 0.39331989319033134);\nd1 = ap(hb, 34, d1, 0.17073985049750015);\nd1 = ap(hb, 38, d1, 0.7457135887202412);\nL_v1 = 0.5 * (d0 + d1);\nd0 = L_v1;\nd1 = L_v0;\nd0 = ap(hb, 40, d0, 0.019059005558478156);\nd0 = ap(hb, 44, d0, 0.1559582483500435);\nd0 = ap(hb, 48, d0, 0.3650536901969154);\nd0 = ap(hb, 52, d0, 0.5755010797915323);\nd0 = ap(hb, 56, d0, 0.7526447471286863);\nd0 = ap(hb, 60, d0, 0.8980636464339091);\nd1 = ap(hb, 42, d1, 0.07350243453590219);\nd1 = ap(hb, 46, d1, 0.25649919975582064);\nd1 = ap(hb, 50, d1, 0.47327898479453656);\nd1 = ap(hb, 54, d1, 0.6688095014357188);\nd1 = ap(hb, 58, d1, 0.8282265929955738);\nd1 = ap(hb, 62, d1, 0.9656701590349398);\nL_w = 0.5 * (d0 + d1);\nout1 = L_w;\n\n// ===== lato R =====\nR_e = in2;\nR_o = in2;\nR_e = ap(hb, 64, R_e, 0.019059005558478156);\nR_e = ap(hb, 68, R_e, 0.1559582483500435);\nR_e = ap(hb, 72, R_e, 0.3650536901969154);\nR_e = ap(hb, 76, R_e, 0.5755010797915323);\nR_e = ap(hb, 80, R_e, 0.7526447471286863);\nR_e = ap(hb, 84, R_e, 0.8980636464339091);\nR_o = ap(hb, 66, R_o, 0.07350243453590219);\nR_o = ap(hb, 70, R_o, 0.25649919975582064);\nR_o = ap(hb, 74, R_o, 0.47327898479453656);\nR_o = ap(hb, 78, R_o, 0.6688095014357188);\nR_o = ap(hb, 82, R_o, 0.8282265929955738);\nR_o = ap(hb, 86, R_o, 0.9656701590349398);\nR_u0 = R_e;\nR_u1 = R_e;\nR_u0 = ap(hb, 88, R_u0, 0.04245470986526787);\nR_u0 = ap(hb, 92, R_u0, 0.39331989319033134);\nR_u1 = ap(hb, 90, R_u1, 0.17073985049750015);\nR_u1 = ap(hb, 94, R_u1, 0.7457135887202412);\nR_u2 = R_o;\nR_u3 = R_o;\nR_u2 = ap(hb, 88, R_u2, 0.04245470986526787);\nR_u2 = ap(hb, 92, R_u2, 0.39331989319033134);\nR_u3 = ap(hb, 90, R_u3, 0.17073985049750015);\nR_u3 = ap(hb, 94, R_u3, 0.7457135887202412);\nxin = R_u0 * 4.360865946243008 + noise() * 0.00001;\nahph = 0;\nalpl = 0;\nif (on_a) {\nahph = sez_a0_hp(st, 32, xin, g_hp1, dq1);\nahph = sez_a1_hp(st, 36, ahph, g_hp2, d_hp);\nalpl = sez_a0_lp(st, 40, xin, g_lp1, dq1);\nalpl = sez_a1_lp(st, 44, alpl, g_lp2, d_lp);\n}\nchph = 0;\nclpl = 0;\nif (on_c) {\nchph = sez_c0_hp(st, 48, xin, g_hp1, dq1);\nchph = sez_c1_hp(st, 52, chph, g_hp2, d_hp);\nclpl = sez_c0_lp(st, 56, xin, g_lp1, dq1);\nclpl = sez_c1_lp(st, 60, clpl, g_lp2, d_lp);\n}\nohp = (1 - s_core) * ahph + s_core * chph;\nif (od_hp > 1e-09) {\nohp = ohp + od_hp * (1.171 * clipd(2 * ohp) - ohp);\n}\nolp = (1 - s_core) * alpl + s_core * clpl;\nif (od_lp > 1e-09) {\nolp = olp + od_lp * (1.171 * clipd(2 * olp) - olp);\n}\nR_y0 = (w_off * xin + w_hp * ohp + w_lp * olp) / 4.360865946243008;\nxin = R_u1 * 4.360865946243008 + noise() * 0.00001;\nahph = 0;\nalpl = 0;\nif (on_a) {\nahph = sez_a0_hp(st, 32, xin, g_hp1, dq1);\nahph = sez_a1_hp(st, 36, ahph, g_hp2, d_hp);\nalpl = sez_a0_lp(st, 40, xin, g_lp1, dq1);\nalpl = sez_a1_lp(st, 44, alpl, g_lp2, d_lp);\n}\nchph = 0;\nclpl = 0;\nif (on_c) {\nchph = sez_c0_hp(st, 48, xin, g_hp1, dq1);\nchph = sez_c1_hp(st, 52, chph, g_hp2, d_hp);\nclpl = sez_c0_lp(st, 56, xin, g_lp1, dq1);\nclpl = sez_c1_lp(st, 60, clpl, g_lp2, d_lp);\n}\nohp = (1 - s_core) * ahph + s_core * chph;\nif (od_hp > 1e-09) {\nohp = ohp + od_hp * (1.171 * clipd(2 * ohp) - ohp);\n}\nolp = (1 - s_core) * alpl + s_core * clpl;\nif (od_lp > 1e-09) {\nolp = olp + od_lp * (1.171 * clipd(2 * olp) - olp);\n}\nR_y1 = (w_off * xin + w_hp * ohp + w_lp * olp) / 4.360865946243008;\nxin = R_u2 * 4.360865946243008 + noise() * 0.00001;\nahph = 0;\nalpl = 0;\nif (on_a) {\nahph = sez_a0_hp(st, 32, xin, g_hp1, dq1);\nahph = sez_a1_hp(st, 36, ahph, g_hp2, d_hp);\nalpl = sez_a0_lp(st, 40, xin, g_lp1, dq1);\nalpl = sez_a1_lp(st, 44, alpl, g_lp2, d_lp);\n}\nchph = 0;\nclpl = 0;\nif (on_c) {\nchph = sez_c0_hp(st, 48, xin, g_hp1, dq1);\nchph = sez_c1_hp(st, 52, chph, g_hp2, d_hp);\nclpl = sez_c0_lp(st, 56, xin, g_lp1, dq1);\nclpl = sez_c1_lp(st, 60, clpl, g_lp2, d_lp);\n}\nohp = (1 - s_core) * ahph + s_core * chph;\nif (od_hp > 1e-09) {\nohp = ohp + od_hp * (1.171 * clipd(2 * ohp) - ohp);\n}\nolp = (1 - s_core) * alpl + s_core * clpl;\nif (od_lp > 1e-09) {\nolp = olp + od_lp * (1.171 * clipd(2 * olp) - olp);\n}\nR_y2 = (w_off * xin + w_hp * ohp + w_lp * olp) / 4.360865946243008;\nxin = R_u3 * 4.360865946243008 + noise() * 0.00001;\nahph = 0;\nalpl = 0;\nif (on_a) {\nahph = sez_a0_hp(st, 32, xin, g_hp1, dq1);\nahph = sez_a1_hp(st, 36, ahph, g_hp2, d_hp);\nalpl = sez_a0_lp(st, 40, xin, g_lp1, dq1);\nalpl = sez_a1_lp(st, 44, alpl, g_lp2, d_lp);\n}\nchph = 0;\nclpl = 0;\nif (on_c) {\nchph = sez_c0_hp(st, 48, xin, g_hp1, dq1);\nchph = sez_c1_hp(st, 52, chph, g_hp2, d_hp);\nclpl = sez_c0_lp(st, 56, xin, g_lp1, dq1);\nclpl = sez_c1_lp(st, 60, clpl, g_lp2, d_lp);\n}\nohp = (1 - s_core) * ahph + s_core * chph;\nif (od_hp > 1e-09) {\nohp = ohp + od_hp * (1.171 * clipd(2 * ohp) - ohp);\n}\nolp = (1 - s_core) * alpl + s_core * clpl;\nif (od_lp > 1e-09) {\nolp = olp + od_lp * (1.171 * clipd(2 * olp) - olp);\n}\nR_y3 = (w_off * xin + w_hp * ohp + w_lp * olp) / 4.360865946243008;\nif (on_a == 0) {\npoke(st, 0, 32);\npoke(st, 0, 33);\npoke(st, 0, 34);\npoke(st, 0, 35);\npoke(st, 0, 36);\npoke(st, 0, 37);\npoke(st, 0, 38);\npoke(st, 0, 39);\npoke(st, 0, 40);\npoke(st, 0, 41);\npoke(st, 0, 42);\npoke(st, 0, 43);\npoke(st, 0, 44);\npoke(st, 0, 45);\npoke(st, 0, 46);\npoke(st, 0, 47);\n}\nif (on_c == 0) {\npoke(st, 0, 48);\npoke(st, 0, 49);\npoke(st, 0, 50);\npoke(st, 0, 51);\npoke(st, 0, 52);\npoke(st, 0, 53);\npoke(st, 0, 54);\npoke(st, 0, 55);\npoke(st, 0, 56);\npoke(st, 0, 57);\npoke(st, 0, 58);\npoke(st, 0, 59);\npoke(st, 0, 60);\npoke(st, 0, 61);\npoke(st, 0, 62);\npoke(st, 0, 63);\n}\nd0 = R_y1;\nd1 = R_y0;\nd0 = ap(hb, 96, d0, 0.04245470986526787);\nd0 = ap(hb, 100, d0, 0.39331989319033134);\nd1 = ap(hb, 98, d1, 0.17073985049750015);\nd1 = ap(hb, 102, d1, 0.7457135887202412);\nR_v0 = 0.5 * (d0 + d1);\nd0 = R_y3;\nd1 = R_y2;\nd0 = ap(hb, 96, d0, 0.04245470986526787);\nd0 = ap(hb, 100, d0, 0.39331989319033134);\nd1 = ap(hb, 98, d1, 0.17073985049750015);\nd1 = ap(hb, 102, d1, 0.7457135887202412);\nR_v1 = 0.5 * (d0 + d1);\nd0 = R_v1;\nd1 = R_v0;\nd0 = ap(hb, 104, d0, 0.019059005558478156);\nd0 = ap(hb, 108, d0, 0.1559582483500435);\nd0 = ap(hb, 112, d0, 0.3650536901969154);\nd0 = ap(hb, 116, d0, 0.5755010797915323);\nd0 = ap(hb, 120, d0, 0.7526447471286863);\nd0 = ap(hb, 124, d0, 0.8980636464339091);\nd1 = ap(hb, 106, d1, 0.07350243453590219);\nd1 = ap(hb, 110, d1, 0.25649919975582064);\nd1 = ap(hb, 114, d1, 0.47327898479453656);\nd1 = ap(hb, 118, d1, 0.6688095014357188);\nd1 = ap(hb, 122, d1, 0.8282265929955738);\nd1 = ap(hb, 126, d1, 0.9656701590349398);\nR_w = 0.5 * (d0 + d1);\nout2 = R_w;\n\n",
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
						50,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "HPF FREQ",
							"parameter_shortname": "HPF FREQ",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								0.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "HPF FREQ",
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
					"text": "prepend freq_hp",
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
						64,
						8,
						50,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "HPF RES",
							"parameter_shortname": "HPF RES",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								0.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "HPF RES",
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
					"text": "prepend res_hp",
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
						120,
						8,
						50,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "HPF DRIVE",
							"parameter_shortname": "HPF DRIVE",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								0.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "HPF DRIVE",
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
					"text": "prepend drive_hp",
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
						176,
						8,
						50,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "LPF FREQ",
							"parameter_shortname": "LPF FREQ",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								100.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "LPF FREQ",
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
					"text": "prepend freq_lp",
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
						232,
						8,
						50,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "LPF RES",
							"parameter_shortname": "LPF RES",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								0.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "LPF RES",
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
					"text": "prepend res_lp",
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
					"id": "obj-d5",
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
						288,
						8,
						50,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "LPF DRIVE",
							"parameter_shortname": "LPF DRIVE",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								0.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "LPF DRIVE",
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
					"id": "obj-d5-pre",
					"maxclass": "newobj",
					"text": "prepend drive_lp",
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
					"id": "obj-t0",
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
						8,
						60,
						330,
						20
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "MODO",
							"parameter_shortname": "MODO",
							"parameter_initial_enable": 1,
							"parameter_type": 2,
							"parameter_enum": [
								"HPF",
								"OFF",
								"LPF"
							],
							"parameter_mmax": 2.0,
							"parameter_initial": [
								1
							],
							"parameter_unitstyle": 0
						}
					},
					"varname": "MODO",
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
					"id": "obj-t0-pre",
					"maxclass": "newobj",
					"text": "prepend modo",
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
					"id": "obj-t1",
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
						84,
						330,
						20
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "CORE",
							"parameter_shortname": "CORE",
							"parameter_initial_enable": 1,
							"parameter_type": 2,
							"parameter_enum": [
								"OTA (a')",
								"PULITO (c-B)"
							],
							"parameter_mmax": 1.0,
							"parameter_initial": [
								0
							],
							"parameter_unitstyle": 0
						}
					},
					"varname": "CORE",
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
					"id": "obj-t1-pre",
					"maxclass": "newobj",
					"text": "prepend core",
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
					"id": "obj-t2",
					"maxclass": "live.tab",
					"parameter_enable": 1,
					"patching_rect": [
						820,
						80,
						44,
						48
					],
					"presentation": 1,
					"presentation_rect": [
						8,
						108,
						330,
						20
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "PENDENZA",
							"parameter_shortname": "PENDENZA",
							"parameter_initial_enable": 1,
							"parameter_type": 2,
							"parameter_enum": [
								"BUTTERWORTH",
								"LINKWITZ-RILEY",
								"BESSEL"
							],
							"parameter_mmax": 2.0,
							"parameter_initial": [
								0
							],
							"parameter_unitstyle": 0
						}
					},
					"varname": "PENDENZA",
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
					"id": "obj-t2-pre",
					"maxclass": "newobj",
					"text": "prepend pend",
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
						134,
						330,
						30
					],
					"patching_rect": [
						20,
						440,
						330,
						30
					],
					"linecount": 2,
					"text": "FREQ 0-100 % = 10 Hz-35 kHz (Xone:96). RES oltre 90 % = fischio. 0 dBu = -12 dBFS."
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
						"obj-d5-pre",
						0
					],
					"source": [
						"obj-d5",
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
						"obj-d5-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-t0-pre",
						0
					],
					"source": [
						"obj-t0",
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
						"obj-t0-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-t1-pre",
						0
					],
					"source": [
						"obj-t1",
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
						"obj-t1-pre",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-t2-pre",
						0
					],
					"source": [
						"obj-t2",
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
						"obj-t2-pre",
						0
					]
				}
			}
		],
		"parameters": {
			"obj-d0": [
				"HPF FREQ",
				"HPF FREQ",
				0
			],
			"obj-d1": [
				"HPF RES",
				"HPF RES",
				0
			],
			"obj-d2": [
				"HPF DRIVE",
				"HPF DRIVE",
				0
			],
			"obj-d3": [
				"LPF FREQ",
				"LPF FREQ",
				0
			],
			"obj-d4": [
				"LPF RES",
				"LPF RES",
				0
			],
			"obj-d5": [
				"LPF DRIVE",
				"LPF DRIVE",
				0
			],
			"obj-t0": [
				"MODO",
				"MODO",
				0
			],
			"obj-t1": [
				"CORE",
				"CORE",
				0
			],
			"obj-t2": [
				"PENDENZA",
				"PENDENZA",
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