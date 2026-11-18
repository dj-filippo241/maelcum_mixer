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
					"numoutlets": 3,
					"outlettype": [
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
									"code": "// MC-LICKSHOT - lickshot in rack (dec. 179-189), modello lickshot.py.\n// GENERATO da proto-max/coefficienti/genera_lickshot.py: non modificare.\n// LFO CD4069 a dente di sega -> VCO CD4046 -> passa-alto 14,5 Hz -> FIRE\n// -> VOLUME -> eco a due BBD senza filtri (nel giro passa-alto\n// e saturazione). in1, in2 ignorati.\n// out1 = out2 = uscita (1,0 = 4.3609 V); out3 = LED dell'LFO.\n\nParam alt(71, min=0, max=100);\nParam vel(50, min=0, max=100);\nParam prof(67, min=0, max=100);\nParam vol(100, min=0, max=100);\nParam trig(0, min=0, max=1);\nParam tempo(33, min=0, max=100);\nParam rip(40, min=0, max=100);\nParam eco(40, min=0, max=100);\nHistory vi(4.3);\nHistory su(0);\nHistory fase(0);\nHistory hpx(0);\nHistory hpy(0);\nHistory gx(0);\nHistory gy(0);\nHistory ck(0);\nHistory hin(0);\nHistory hout(0);\nHistory td(7805.337600000001);\nDelay dl(48000);\nHistory s_alt(71.0);\nHistory s_vel(50.0);\nHistory s_prof(67.0);\nHistory s_vol(100.0);\nHistory s_tempo(33.0);\nHistory s_rip(40.0);\nHistory s_eco(40.0);\nt10 = exp(-1 / (0.010 * samplerate));\ns_alt = alt + t10 * (s_alt - alt);\ns_vel = vel + t10 * (s_vel - vel);\ns_prof = prof + t10 * (s_prof - prof);\ns_vol = vol + t10 * (s_vol - vol);\ns_tempo = tempo + t10 * (s_tempo - tempo);\ns_rip = rip + t10 * (s_rip - rip);\ns_eco = eco + t10 * (s_eco - eco);\n// LFO: integratore fra le soglie del Schmitt, discesa lenta, risalita dal diodo\nrl = 22000.0 + (1 - s_vel / 100) * 500000.0;\ngiu = 4.3 / (rl * 1e-06) / samplerate;\nsup = 7818.181818181819 / samplerate;\nvin = vi + su * sup - (1 - su) * giu;\nhhi = su * (vin >= 6.254545454545455);\nhlo = (1 - su) * (vin <= 2.3454545454545452);\nvi = min(max(vin, 2.3454545454545452), 6.254545454545455);\nsu = su * (1 - hhi) + hlo;\n// PROFONDITA (dec. 190): pot fra la rampa e VDD/2, buffer verso il VCOin\nvco = 4.3 + s_prof / 100 * 2.911764705882353 * (vi - 4.3) / 1.9545454545454548;\n// VCO: frequenza lineare col VCOin, f0 al centro (datasheet TI, Fig. 4)\nr1 = 10000.0 * pow(11.0, 1 - s_alt / 100);\nfz = 0.7 / (r1 * 1e-07);\nfq = fz * max(0, vco - 1.0) / 3.3;\ndt = max(fq / samplerate, 1e-9);\n// onda quadra con PolyBLEP\nta = fase / dt;\ntc = (fase - 1) / dt;\nxq = (fase < 0.5) * 2 - 1 + (fase < dt) * (ta + ta - ta * ta - 1) + (fase > 1 - dt) * (tc * tc + tc + tc + 1);\nt2 = fase + 0.5 - (fase + 0.5 >= 1);\ntb = t2 / dt;\nte = (t2 - 1) / dt;\nxq = xq - (t2 < dt) * (tb + tb - tb * tb - 1) - (t2 > 1 - dt) * (te * te + te + te + 1);\nfase = fase + fq / samplerate;\nfase = fase - (fase >= 1);\nkhp = 1 / (1 + 91.106186954104 / samplerate);\nhpy = khp * (hpy + xq - hpx);\nhpx = xq;\nvv = s_vol / 100;\ndry = hpy * (trig > 0.5) * 0.775 * vv * vv;\n// eco: due BBD in fila senza filtri (dec. 191), tempo lisciato (fionda);\n// i BBD campionano e tengono al ritmo del clock\ntm = 0.04096 + 0.36864 * s_tempo / 100;\ntd = td + (tm * samplerate - td) * (1 - exp(-1 / (0.05 * samplerate)));\nck = ck + 4096.0 / (td / samplerate) / samplerate;\ntick = ck >= 1;\nck = ck - tick;\nrd = dl.read(td, interp=\"linear\");\nhout = tick * rd + (1 - tick) * hout;\n// giro: passa-alto e saturazione\nkg = 1 / (1 + 942.4777960769379 / samplerate);\ngy = kg * (gy + hout - gx);\ngx = hout;\nfb = 1.5 * tanh(1.1 * s_rip / 100 * gy / 1.5);\nhin = tick * (dry + fb) + (1 - tick) * hin;\ndl.write(hin);\nve = s_eco / 100;\nout1 = (dry + ve * ve * hout) / 4.360865946243008;\nout2 = out1;\nout3 = min(max((vi - 2.4) / 3.854545454545455, 0), 1);\n",
									"numinlets": 2,
									"numoutlets": 3,
									"outlettype": [
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
							}
						]
					}
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
							"parameter_longname": "ALTEZZA",
							"parameter_shortname": "ALTEZZA",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								71.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "ALTEZZA",
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
					"text": "prepend alt",
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
							"parameter_longname": "VELOCITA",
							"parameter_shortname": "VELOCITA",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								50.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "VELOCITA",
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
					"text": "prepend vel",
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
							"parameter_longname": "PROFONDITA",
							"parameter_shortname": "PROFONDITA",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								67.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "PROFONDITA",
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
					"text": "prepend prof",
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
						188,
						8,
						54,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "VOLUME",
							"parameter_shortname": "VOLUME",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								100.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "VOLUME",
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
					"text": "prepend vol",
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
						8,
						70,
						54,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "TEMPO",
							"parameter_shortname": "TEMPO",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								33.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "TEMPO",
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
					"text": "prepend tempo",
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
						68,
						70,
						54,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "RIPETIZIONI",
							"parameter_shortname": "RIPETIZIONI",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								40.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "RIPETIZIONI",
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
					"text": "prepend rip",
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
						128,
						70,
						54,
						48
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "LIVELLO ECO",
							"parameter_shortname": "LIVELLO ECO",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								40.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "LIVELLO ECO",
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
					"text": "prepend eco",
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
						78,
						50,
						36
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "FIRE",
							"parameter_shortname": "FIRE",
							"parameter_initial_enable": 1,
							"parameter_type": 2,
							"parameter_enum": [
								"-",
								"FIRE"
							],
							"parameter_mmax": 1.0,
							"parameter_initial": [
								0
							],
							"parameter_unitstyle": 0
						}
					},
					"varname": "FIRE",
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
					"text": "prepend trig",
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
					"id": "obj-led",
					"maxclass": "live.meter~",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"list",
						"list"
					],
					"presentation": 1,
					"presentation_rect": [
						246,
						8,
						8,
						56
					],
					"patching_rect": [
						970,
						480,
						20,
						100
					],
					"display_range": [
						-60.0,
						0.0
					],
					"varname": "LED"
				}
			},
			{
				"box": {
					"id": "obj-nota20",
					"maxclass": "live.comment",
					"numinlets": 1,
					"numoutlets": 0,
					"presentation": 1,
					"presentation_rect": [
						8,
						124,
						250,
						40
					],
					"patching_rect": [
						20,
						760,
						250,
						18
					],
					"text": "FIRE: clic = acceso, clic = spento; da un controller mappalo su un CC. Uscita a livello del jack: mettila in MC-MONO."
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
						"obj-led",
						0
					],
					"source": [
						"obj-gen",
						2
					]
				}
			}
		],
		"parameters": {
			"obj-c0": [
				"ALTEZZA",
				"ALTEZZA",
				0
			],
			"obj-c1": [
				"VELOCITA",
				"VELOCITA",
				0
			],
			"obj-c2": [
				"PROFONDITA",
				"PROFONDITA",
				0
			],
			"obj-c3": [
				"VOLUME",
				"VOLUME",
				0
			],
			"obj-c4": [
				"TEMPO",
				"TEMPO",
				0
			],
			"obj-c5": [
				"RIPETIZIONI",
				"RIPETIZIONI",
				0
			],
			"obj-c6": [
				"LIVELLO ECO",
				"LIVELLO ECO",
				0
			],
			"obj-c7": [
				"FIRE",
				"FIRE",
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