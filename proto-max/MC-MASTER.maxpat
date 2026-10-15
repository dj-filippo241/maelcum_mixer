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
					"numoutlets": 6,
					"outlettype": [
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
									"code": "// MC-MASTER - prototipo Max P3 (master-out \u00a73.2, addendum dec. 111).\n// GENERATO da proto-max/coefficienti/genera_fx.py: non modificare.\n// MONO (M/S, S in un VCA da 0 a -100 dB in 1 ms) -> MASTER LEVEL ->\n// meter L e R (out3-4, 1 = +24 dBu) e clip (out5-6).\n\nParam level(80, min=0, max=100);\nParam mono(0, min=0, max=1);\nHistory mrp(0);\nHistory menl(0);\nHistory menr(0);\nHistory mlal(0);\nHistory mlar(0);\nHistory s_level(80.0);\nt10 = exp(-1 / (0.010 * samplerate));\ns_level = level + t10 * (s_level - level);\npm = 1 / (0.001 * samplerate);\nmrp = mrp + min(max(mono - mrp, -pm), pm);\nmgs = pow(10, -5 * mrp) * (mrp < 1);\nmmid = 0.5 * (in1 + in2);\nmside = 0.5 * (in1 - in2) * mgs;\ntm = s_level / 100;\nmgl = (tm >= 0.8) * pow(10, 1.5000000000000004 * (tm - 0.8)) + (tm < 0.8) * (tm >= 0.05) * pow(10, -4.0 * (0.8 - tm)) + (tm < 0.05) * 0.02 * tm;\nmol = mgl * (mmid + mside);\nmor = mgl * (mmid - mside);\nmcr = exp(-1 / (0.3 * samplerate));\nma = abs(mol) * 4.360865946243008;\nmenl = max(ma, mcr * menl);\nmlal = (ma >= 15.472936263797646) * 0.479 + (ma < 15.472936263797646) * max(mlal - 1 / samplerate, 0);\nma = abs(mor) * 4.360865946243008;\nmenr = max(ma, mcr * menr);\nmlar = (ma >= 15.472936263797646) * 0.479 + (ma < 15.472936263797646) * max(mlar - 1 / samplerate, 0);\nout1 = mol;\nout2 = mor;\nout3 = menl / 17.360920030219035;\nout4 = menr / 17.360920030219035;\nout5 = mlal > 0;\nout6 = mlar > 0;\n",
									"numinlets": 2,
									"numoutlets": 6,
									"outlettype": [
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
						60,
						52
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "MASTER",
							"parameter_shortname": "MASTER",
							"parameter_initial_enable": 1,
							"parameter_type": 0,
							"parameter_mmax": 100.0,
							"parameter_initial": [
								80.0
							],
							"parameter_unitstyle": 5
						}
					},
					"varname": "MASTER",
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
					"text": "prepend level",
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
						8,
						66,
						60,
						36
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "MONO",
							"parameter_shortname": "MONO",
							"parameter_initial_enable": 1,
							"parameter_type": 2,
							"parameter_enum": [
								"STEREO",
								"MONO"
							],
							"parameter_mmax": 1.0,
							"parameter_initial": [
								0
							],
							"parameter_unitstyle": 0
						}
					},
					"varname": "MONO",
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
					"id": "obj-c1-pre",
					"maxclass": "newobj",
					"text": "prepend mono",
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
					"id": "obj-ml",
					"maxclass": "live.meter~",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"list",
						"list"
					],
					"presentation": 1,
					"presentation_rect": [
						80,
						8,
						12,
						110
					],
					"patching_rect": [
						910,
						480,
						20,
						100
					],
					"display_range": [
						-60.0,
						0.0
					],
					"varname": "METER L"
				}
			},
			{
				"box": {
					"id": "obj-mr",
					"maxclass": "live.meter~",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"list",
						"list"
					],
					"presentation": 1,
					"presentation_rect": [
						94,
						8,
						12,
						110
					],
					"patching_rect": [
						940,
						480,
						20,
						100
					],
					"display_range": [
						-60.0,
						0.0
					],
					"varname": "METER R"
				}
			},
			{
				"box": {
					"id": "obj-cl",
					"maxclass": "live.meter~",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"list",
						"list"
					],
					"presentation": 1,
					"presentation_rect": [
						108,
						8,
						5,
						110
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
					"varname": "CLIP L"
				}
			},
			{
				"box": {
					"id": "obj-cr",
					"maxclass": "live.meter~",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [
						"list",
						"list"
					],
					"presentation": 1,
					"presentation_rect": [
						115,
						8,
						5,
						110
					],
					"patching_rect": [
						700,
						480,
						20,
						100
					],
					"display_range": [
						-60.0,
						0.0
					],
					"varname": "CLIP R"
				}
			},
			{
				"box": {
					"id": "obj-nota11",
					"maxclass": "live.comment",
					"numinlets": 1,
					"numoutlets": 0,
					"presentation": 1,
					"presentation_rect": [
						8,
						124,
						200,
						30
					],
					"patching_rect": [
						20,
						760,
						200,
						18
					],
					"text": "Unity all'80 % (detent). Meter: 0 = +24 dBu, -24 = 0 dBu."
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
						"obj-ml",
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
						"obj-mr",
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
						"obj-cl",
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
						"obj-cr",
						0
					],
					"source": [
						"obj-gen",
						5
					]
				}
			}
		],
		"parameters": {
			"obj-c0": [
				"MASTER",
				"MASTER",
				0
			],
			"obj-c1": [
				"MONO",
				"MONO",
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