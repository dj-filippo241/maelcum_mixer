  <!-- CELL ZOOM v0.2.1 + continuous WIDTH v0.2.2 (dec. 117), English copy of cella-v021.frag, 2026-11-04 -->
  <rect x="420" y="110" width="1100" height="560" rx="10" fill="#fff" stroke="#1F7A4D" stroke-width="1.5"/>
  <text x="450" y="146" font-size="16" font-weight="700" fill="#1F7A4D">ZOOM — PARAMETRIC CELL v0.2.1 + continuous WIDTH v0.2.2 (JFET VCR, dec. 117)</text>
  <text x="450" y="168" font-size="11.5" fill="#666">1 matched dual JFET per cell · core at −12 dBu local (Rvin 40.2k) · ×4 make-up absorbed in the injection · verified: THD 0.005% nom / 0.125% worst, law ±0.03%</text>

  <!-- summer -->
  <rect x="450" y="230" width="150" height="86" rx="6" fill="#fff" stroke="#1A1A1A" stroke-width="1.5"/>
  <text x="525" y="256" font-size="12" font-weight="700" text-anchor="middle">SUMMER</text>
  <text x="525" y="274" font-size="10" fill="#444" text-anchor="middle">in: vin (40.2k = −12 dB pad)</text>
  <text x="525" y="290" font-size="10" fill="#444" text-anchor="middle">+ lp (10k) + damping from −dq</text>
  <text x="525" y="306" font-size="10" fill="#444" text-anchor="middle">(R0 30k: Q = 0.3/alpha)</text>

  <!-- VCR int 1 -->
  <rect x="650" y="200" width="200" height="116" rx="6" fill="#F2F8F4" stroke="#1F7A4D" stroke-width="1.5"/>
  <text x="750" y="224" font-size="12" font-weight="700" fill="#1F7A4D" text-anchor="middle">INTEGRATOR 1</text>
  <text x="750" y="242" font-size="10" fill="#444" text-anchor="middle">JFET in triode = VCR: rds = f(Vcm)</text>
  <text x="750" y="258" font-size="10" fill="#444" text-anchor="middle">bootstrapped gate: Vcm + vds/2</text>
  <text x="750" y="274" font-size="10" fill="#444" text-anchor="middle">(2×100k: square-law term cancelled)</text>
  <text x="750" y="290" font-size="10" fill="#444" text-anchor="middle">→ Cint 56n → inverting op-amp</text>
  <text x="750" y="306" font-size="10" fill="#444" text-anchor="middle">window: vds ≤ 2(Vcm−Vt)</text>

  <!-- stato bp -->
  <rect x="900" y="200" width="140" height="116" rx="6" fill="#fff" stroke="#1A1A1A" stroke-width="1.5"/>
  <text x="970" y="226" font-size="12" font-weight="700" text-anchor="middle">bp STATE</text>
  <text x="970" y="244" font-size="10" fill="#444" text-anchor="middle">buffer → bp_b</text>
  <text x="970" y="260" font-size="10" fill="#444" text-anchor="middle">peak = Q × Vin_core</text>
  <text x="970" y="276" font-size="10" fill="#444" text-anchor="middle">(291 mV nom. at Q3 —</text>
  <text x="970" y="292" font-size="10" fill="#444" text-anchor="middle">inside the window</text>
  <text x="970" y="308" font-size="10" fill="#444" text-anchor="middle">≥ 494 mV)</text>

  <!-- VCR int 2 -->
  <rect x="650" y="360" width="200" height="96" rx="6" fill="#F2F8F4" stroke="#1F7A4D" stroke-width="1.5"/>
  <text x="750" y="384" font-size="12" font-weight="700" fill="#1F7A4D" text-anchor="middle">INTEGRATOR 2</text>
  <text x="750" y="402" font-size="10" fill="#444" text-anchor="middle">same structure, from bp_b</text>
  <text x="750" y="418" font-size="10" fill="#444" text-anchor="middle">→ lp state → buffer lp_b</text>
  <text x="750" y="434" font-size="10" fill="#444" text-anchor="middle">lp_b → summer (feedback)</text>

  <!-- invertitore -->
  <rect x="900" y="360" width="140" height="96" rx="6" fill="#fff" stroke="#1A1A1A" stroke-width="1.5"/>
  <text x="970" y="386" font-size="12" font-weight="700" text-anchor="middle">WIDTH → ±dq</text>
  <text x="970" y="404" font-size="10" fill="#444" text-anchor="middle">1k pot: alpha 0.1…1</text>
  <text x="970" y="420" font-size="10" fill="#444" text-anchor="middle">→ ×10 buffer (OPA1612)</text>
  <text x="970" y="436" font-size="10" fill="#444" text-anchor="middle">dq = 10·alpha·bp_b</text>
  <text x="970" y="452" font-size="10" fill="#444" text-anchor="middle">→ inverter: −dq</text>

  <!-- pot gain -->
  <rect x="1100" y="260" width="170" height="120" rx="6" fill="#FFF7ED" stroke="#C05A1B" stroke-width="1.5"/>
  <text x="1185" y="286" font-size="12" font-weight="700" fill="#C05A1B" text-anchor="middle">POT GAIN (b)</text>
  <text x="1185" y="304" font-size="10" fill="#444" text-anchor="middle">between +dq and −dq — IN</text>
  <text x="1185" y="320" font-size="10" fill="#444" text-anchor="middle">the signal domain (no CV)</text>
  <text x="1185" y="336" font-size="10" fill="#444" text-anchor="middle">v0.2.1: wired to the opposite</text>
  <text x="1185" y="352" font-size="10" fill="#444" text-anchor="middle">end (H = |1+b|, notch at b=−1)</text>
  <text x="1185" y="368" font-size="10" fill="#444" text-anchor="middle">physical detent = flat ±0.0001 dB</text>

  <!-- out summer -->
  <rect x="1330" y="260" width="160" height="120" rx="6" fill="#fff" stroke="#1A1A1A" stroke-width="1.5"/>
  <text x="1410" y="286" font-size="12" font-weight="700" text-anchor="middle">SUMMER OUT</text>
  <text x="1410" y="304" font-size="10" fill="#444" text-anchor="middle">dry: 10k/10k (unity)</text>
  <text x="1410" y="320" font-size="10" fill="#444" text-anchor="middle">injection: fixed Rbw 1.62k</text>
  <text x="1410" y="336" font-size="10" fill="#444" text-anchor="middle">same boost at every Q</text>
  <text x="1410" y="352" font-size="10" fill="#444" text-anchor="middle">H = −(1 − b·BP_norm)</text>
  <text x="1410" y="368" font-size="10" fill="#444" text-anchor="middle">→ next cell</text>

  <!-- position CV -->
  <rect x="450" y="520" width="620" height="110" rx="6" fill="#EEF3F6" stroke="#2F6D8E" stroke-width="1.2"/>
  <text x="470" y="546" font-size="12" font-weight="700" fill="#2F6D8E">POSITION (per band, L/R ganged)</text>
  <text x="470" y="566" font-size="10.5" fill="#444">pot θ → law shaper (dec. 70 family: exponential) → Vcm (−1.75…−0.29 V, never positive)</text>
  <text x="470" y="584" font-size="10.5" fill="#444">→ gain-2 buffer → Vcm2 bus → 2×100k network per JFET (gate = Vcm + vds/2)</text>
  <text x="470" y="602" font-size="10.5" fill="#444">f0 = 2β(Vcm−Vt)/(2πC) → C per band: 680n / 180n / 56n / 18n / 4.7n (EQ1-5, table §4.2)</text>
  <text x="470" y="620" font-size="10.5" fill="#444">10-turn trim per side/band · L/R tracking: matched pair on one die (≤17 cents over ±10 °C)</text>

  <!-- width switch -->
  <rect x="1110" y="520" width="380" height="110" rx="6" fill="#EEF3F6" stroke="#2F6D8E" stroke-width="1.2"/>
  <text x="1130" y="546" font-size="12" font-weight="700" fill="#2F6D8E">WIDTH + GAIN (panel)</text>
  <text x="1130" y="566" font-size="10.5" fill="#444">WIDTH: continuous knob Q3…Q0.3, dual 1k pot</text>
  <text x="1130" y="584" font-size="10.5" fill="#444">~20 % log taper (dec. 129 C2) [PROV]</text>
  <text x="1130" y="602" font-size="10.5" fill="#444">GAIN: linear pot + law resistors (dec. 129 B2): boost</text>
  <text x="1130" y="620" font-size="10.5" fill="#444">uniform up to +15, full notch in the last degrees</text>

  <!-- frecce zoom -->
  <g stroke="#C05A1B" stroke-width="2.5" fill="none">
    <path d="M 600 273 L 645 273" marker-end="url(#ar)"/>
    <path d="M 850 258 L 895 258" marker-end="url(#ar)"/>
    <path d="M 970 316 L 970 355" marker-end="url(#ar)"/>
    <path d="M 900 420 L 855 420" marker-end="url(#ar)"/>
    <path d="M 750 355 L 750 316" marker-end="url(#ar)" opacity="0"/>
    <path d="M 645 408 L 620 408 L 620 320 L 595 320" marker-end="url(#ar)"/>
    <path d="M 1040 320 L 1095 320" marker-end="url(#ar)"/>
    <path d="M 1270 320 L 1325 320" marker-end="url(#ar)"/>
    <path d="M 970 316 L 970 340 L 1185 340 L 1185 385" marker-end="url(#ar)" opacity="0"/>
  </g>
  <!-- pot dai due stati -->
  <g stroke="#C05A1B" stroke-width="2" fill="none">
    <path d="M 1040 240 L 1185 240 L 1185 255" marker-end="url(#ar)"/>
    <path d="M 1040 408 L 1075 408 L 1075 470 L 1185 470 L 1185 386" marker-end="url(#ar)"/>
  </g>
  <text x="1080" y="232" font-size="10" fill="#666">+dq</text>
  <text x="1082" y="464" font-size="10" fill="#666">−dq (from the inverter)</text>
  <!-- damping -->
  <path d="M 970 456 L 970 480 L 525 480 L 525 320" stroke="#C05A1B" stroke-width="2" fill="none" marker-end="url(#ar)"/>
  <text x="700" y="474" font-size="10" fill="#666">−dq → damping (R0 30k)</text>
  <!-- CV -->
  <g stroke="#2F6D8E" stroke-width="1.5" stroke-dasharray="6 3" fill="none">
    <path d="M 700 515 L 700 320 L 695 320" marker-end="url(#arw)" opacity="0"/>
    <path d="M 668 515 L 668 320" marker-end="url(#arw)"/>
    <path d="M 780 515 L 780 460" marker-end="url(#arw)"/>
  </g>
  <text x="800" y="512" font-size="10" fill="#2F6D8E">Vcm2 (bootstrap) to the gates</text>

