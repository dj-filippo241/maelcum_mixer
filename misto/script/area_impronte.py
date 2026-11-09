import sys, re, pcbnew
PREF = ("SN", "SJ_", "SH_", "NP_", "LT_", "OF_", "POT_")
for path in sys.argv[1:]:
    b = pcbnew.LoadBoard(path)
    bb = b.GetBoardEdgesBoundingBox()
    W, H = bb.GetWidth()/1e6, bb.GetHeight()/1e6
    tot = 0; sh = 0; n = 0; nsh = 0; kinds = {}
    for fp in b.GetFootprints():
        r = fp.GetBoundingBox(False, False)
        a = r.GetWidth()/1e6 * r.GetHeight()/1e6
        nets = [p.GetNetname() for p in fp.Pads()]
        tot += a; n += 1
        ref = fp.GetReference()
        # parti di sola rete di shaper/trim (resistenze, diodi, trimmer, C): non gli IC
        if ref[0] in "RDC" or ref.startswith("RV"):
            if any(any(x.startswith(p) for p in PREF) for x in nets):
                sh += a; nsh += 1
                k = re.sub(r"\d+", "", ref); kinds[k] = kinds.get(k, 0) + 1
    print("%s: scheda %.0fx%.0f mm = %.0f cm2; impronte %d = %.0f cm2; shaper/trim %d impronte = %.1f cm2 %s"
          % (path.split("/")[-1], W, H, W*H/100, n, tot/100, nsh, sh/100, kinds))
