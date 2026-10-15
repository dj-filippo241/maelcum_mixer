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
					"id": "obj-rL",
					"maxclass": "newobj",
					"text": "receive~ mcfx_b1L",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						20,
						200,
						110,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-pL",
					"maxclass": "newobj",
					"text": "+~",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						20,
						260,
						40,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-kL",
					"maxclass": "newobj",
					"text": "clip~ -3.783652 3.783652",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						20,
						320,
						120,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-fL",
					"maxclass": "newobj",
					"text": "sprintf set mcfx_b%ldL",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						20,
						140,
						160,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-rR",
					"maxclass": "newobj",
					"text": "receive~ mcfx_b1R",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						220,
						200,
						110,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-pR",
					"maxclass": "newobj",
					"text": "+~",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						220,
						260,
						40,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-kR",
					"maxclass": "newobj",
					"text": "clip~ -3.783652 3.783652",
					"numinlets": 3,
					"numoutlets": 1,
					"outlettype": [
						"signal"
					],
					"patching_rect": [
						220,
						320,
						120,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-fR",
					"maxclass": "newobj",
					"text": "sprintf set mcfx_b%ldR",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [
						""
					],
					"patching_rect": [
						220,
						140,
						160,
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
						8,
						120,
						18
					],
					"saved_attribute_attributes": {
						"valueof": {
							"parameter_longname": "BUS",
							"parameter_shortname": "BUS",
							"parameter_initial_enable": 1,
							"parameter_type": 2,
							"parameter_enum": [
								"FX1",
								"FX2",
								"FX3",
								"FX4"
							],
							"parameter_mmax": 3.0,
							"parameter_initial": [
								0
							],
							"parameter_unitstyle": 0
						}
					},
					"varname": "BUS",
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
					"id": "obj-piu",
					"maxclass": "newobj",
					"text": "+ 1",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [
						"int"
					],
					"patching_rect": [
						20,
						100,
						40,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-dev",
					"maxclass": "newobj",
					"text": "live.thisdevice",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": [
						"bang",
						"int",
						"int"
					],
					"patching_rect": [
						200,
						40,
						90,
						22
					]
				}
			},
			{
				"box": {
					"id": "obj-nota13",
					"maxclass": "live.comment",
					"numinlets": 1,
					"numoutlets": 0,
					"presentation": 1,
					"presentation_rect": [
						8,
						32,
						300,
						40
					],
					"patching_rect": [
						20,
						760,
						300,
						18
					],
					"text": "Primo dispositivo della traccia FX: somma delle mandate e dei reroute del bus scelto, rail +-16,5 V. Poi il tuo effetto, poi MC-RET."
				}
			}
		],
		"lines": [
			{
				"patchline": {
					"destination": [
						"obj-pL",
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
						"obj-pL",
						1
					],
					"source": [
						"obj-rL",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-kL",
						0
					],
					"source": [
						"obj-pL",
						0
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
						"obj-kL",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-rL",
						0
					],
					"source": [
						"obj-fL",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-pR",
						0
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
						"obj-pR",
						1
					],
					"source": [
						"obj-rR",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-kR",
						0
					],
					"source": [
						"obj-pR",
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
						"obj-kR",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-rR",
						0
					],
					"source": [
						"obj-fR",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-piu",
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
						"obj-fL",
						0
					],
					"source": [
						"obj-piu",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-fR",
						0
					],
					"source": [
						"obj-piu",
						0
					]
				}
			},
			{
				"patchline": {
					"destination": [
						"obj-c0",
						0
					],
					"source": [
						"obj-dev",
						0
					]
				}
			}
		],
		"parameters": {
			"obj-c0": [
				"BUS",
				"BUS",
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