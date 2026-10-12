  <!-- ZOOM CELLA v0.2.1 -->
  <rect x="420" y="110" width="1100" height="560" rx="10" fill="#fff" stroke="#1F7A4D" stroke-width="1.5"/>
  <text x="450" y="146" font-size="16" font-weight="700" fill="#1F7A4D">ZOOM — CELLA PARAMETRICA v0.2.1 (JFET VCR, questione 70)</text>
  <text x="450" y="168" font-size="11.5" fill="#666">7 sezioni op-amp + 1 dual JFET matched · core a −12 dBu locale (Rvin 40,2k) · make-up ×4 assorbito nell'iniezione · verificata: THD 0,005% nom / 0,125% worst, law ±0,03%</text>

  <!-- summer -->
  <rect x="450" y="230" width="150" height="86" rx="6" fill="#fff" stroke="#1A1A1A" stroke-width="1.5"/>
  <text x="525" y="256" font-size="12" font-weight="700" text-anchor="middle">SUMMER</text>
  <text x="525" y="274" font-size="10" fill="#444" text-anchor="middle">in: vin (40,2k = pad −12 dB)</text>
  <text x="525" y="290" font-size="10" fill="#444" text-anchor="middle">+ lp (10k) + damping da −bp_b</text>
  <text x="525" y="306" font-size="10" fill="#444" text-anchor="middle">(Rq = Q·10k, switch width)</text>

  <!-- VCR int 1 -->
  <rect x="650" y="200" width="200" height="116" rx="6" fill="#F2F8F4" stroke="#1F7A4D" stroke-width="1.5"/>
  <text x="750" y="224" font-size="12" font-weight="700" fill="#1F7A4D" text-anchor="middle">INTEGRATORE 1</text>
  <text x="750" y="242" font-size="10" fill="#444" text-anchor="middle">JFET in triode = VCR: rds = f(Vcm)</text>
  <text x="750" y="258" font-size="10" fill="#444" text-anchor="middle">gate bootstrappato: Vcm + vds/2</text>
  <text x="750" y="274" font-size="10" fill="#444" text-anchor="middle">(2×100k: quadraticità cancellata)</text>
  <text x="750" y="290" font-size="10" fill="#444" text-anchor="middle">→ Cint 56n → op-amp invertente</text>
  <text x="750" y="306" font-size="10" fill="#444" text-anchor="middle">finestra: vds ≤ 2(Vcm−Vt)</text>

  <!-- stato bp -->
  <rect x="900" y="200" width="140" height="116" rx="6" fill="#fff" stroke="#1A1A1A" stroke-width="1.5"/>
  <text x="970" y="226" font-size="12" font-weight="700" text-anchor="middle">STATO bp</text>
  <text x="970" y="244" font-size="10" fill="#444" text-anchor="middle">buffer → bp_b</text>
  <text x="970" y="260" font-size="10" fill="#444" text-anchor="middle">picco = Q × Vin_core</text>
  <text x="970" y="276" font-size="10" fill="#444" text-anchor="middle">(291 mV nom. Q3 —</text>
  <text x="970" y="292" font-size="10" fill="#444" text-anchor="middle">dentro la finestra</text>
  <text x="970" y="308" font-size="10" fill="#444" text-anchor="middle">≥ 494 mV)</text>

  <!-- VCR int 2 -->
  <rect x="650" y="360" width="200" height="96" rx="6" fill="#F2F8F4" stroke="#1F7A4D" stroke-width="1.5"/>
  <text x="750" y="384" font-size="12" font-weight="700" fill="#1F7A4D" text-anchor="middle">INTEGRATORE 2</text>
  <text x="750" y="402" font-size="10" fill="#444" text-anchor="middle">stessa struttura, da bp_b</text>
  <text x="750" y="418" font-size="10" fill="#444" text-anchor="middle">→ stato lp → buffer lp_b</text>
  <text x="750" y="434" font-size="10" fill="#444" text-anchor="middle">lp_b → summer (feedback)</text>

  <!-- invertitore -->
  <rect x="900" y="360" width="140" height="96" rx="6" fill="#fff" stroke="#1A1A1A" stroke-width="1.5"/>
  <text x="970" y="386" font-size="12" font-weight="700" text-anchor="middle">INVERTITORE</text>
  <text x="970" y="404" font-size="10" fill="#444" text-anchor="middle">−bp_b (già a BOM v0.2</text>
  <text x="970" y="420" font-size="10" fill="#444" text-anchor="middle">per il pot ±bp_b):</text>
  <text x="970" y="436" font-size="10" fill="#444" text-anchor="middle">ora serve ANCHE al</text>
  <text x="970" y="452" font-size="10" fill="#444" text-anchor="middle">damping (segno loop)</text>

  <!-- pot gain -->
  <rect x="1100" y="260" width="170" height="120" rx="6" fill="#FFF7ED" stroke="#C05A1B" stroke-width="1.5"/>
  <text x="1185" y="286" font-size="12" font-weight="700" fill="#C05A1B" text-anchor="middle">POT GAIN (b)</text>
  <text x="1185" y="304" font-size="10" fill="#444" text-anchor="middle">tra +bp_b e −bp_b — NEL</text>
  <text x="1185" y="320" font-size="10" fill="#444" text-anchor="middle">dominio segnale (niente CV)</text>
  <text x="1185" y="336" font-size="10" fill="#444" text-anchor="middle">v0.2.1: cablato sul terminale</text>
  <text x="1185" y="352" font-size="10" fill="#444" text-anchor="middle">opposto (H = |1+b|, notch a b=−1)</text>
  <text x="1185" y="368" font-size="10" fill="#444" text-anchor="middle">detent fisico = piatto ±0,0001 dB</text>

  <!-- out summer -->
  <rect x="1330" y="260" width="160" height="120" rx="6" fill="#fff" stroke="#1A1A1A" stroke-width="1.5"/>
  <text x="1410" y="286" font-size="12" font-weight="700" text-anchor="middle">SUMMER OUT</text>
  <text x="1410" y="304" font-size="10" fill="#444" text-anchor="middle">dry: 10k/10k (unity)</text>
  <text x="1410" y="320" font-size="10" fill="#444" text-anchor="middle">iniezione: Rbw 2,5k·Q/4,62</text>
  <text x="1410" y="336" font-size="10" fill="#444" text-anchor="middle">(= make-up ×4 del core)</text>
  <text x="1410" y="352" font-size="10" fill="#444" text-anchor="middle">H = −(1 − b·BP_norm)</text>
  <text x="1410" y="368" font-size="10" fill="#444" text-anchor="middle">→ cella successiva</text>

  <!-- position CV -->
  <rect x="450" y="520" width="620" height="110" rx="6" fill="#EEF3F6" stroke="#2F6D8E" stroke-width="1.2"/>
  <text x="470" y="546" font-size="12" font-weight="700" fill="#2F6D8E">POSITION (per banda, L/R ganged)</text>
  <text x="470" y="566" font-size="10.5" fill="#444">pot θ → shaper law (famiglia dec. 70: esponenziale) → Vcm (−1,75…−0,29 V, mai positivo)</text>
  <text x="470" y="584" font-size="10.5" fill="#444">→ buffer gain-2 → bus Vcm2 → rete 2×100k per JFET (gate = Vcm + vds/2)</text>
  <text x="470" y="602" font-size="10.5" fill="#444">f0 = 2β(Vcm−Vt)/(2πC) → C per banda: 680n / 180n / 56n / 18n / 4,7n (EQ1-5, tabella §4.2)</text>
  <text x="470" y="620" font-size="10.5" fill="#444">trim 10 giri lato/banda · tracking L/R: coppia matched stesso die (≤17 cent su ±10 °C)</text>

  <!-- width switch -->
  <rect x="1110" y="520" width="380" height="110" rx="6" fill="#EEF3F6" stroke="#2F6D8E" stroke-width="1.2"/>
  <text x="1130" y="546" font-size="12" font-weight="700" fill="#2F6D8E">WIDTH + GAIN (pannello)</text>
  <text x="1130" y="566" font-size="10.5" fill="#444">switch 3 vie (deck doppio gangato): Q 3 / 1 / 0,5</text>
  <text x="1130" y="584" font-size="10.5" fill="#444">commuta Rq (damping) E Rbw (iniezione) — 0,1%</text>
  <text x="1130" y="602" font-size="10.5" fill="#444">pot gain: taper custom (eq-serie §10) — boost lineare</text>
  <text x="1130" y="620" font-size="10.5" fill="#444">in dB su mezza corsa, cut accelerato, notch a fine corsa</text>

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
  <text x="1080" y="232" font-size="10" fill="#666">+bp_b</text>
  <text x="1082" y="464" font-size="10" fill="#666">−bp_b (dall'invertitore)</text>
  <!-- damping -->
  <path d="M 970 456 L 970 480 L 525 480 L 525 320" stroke="#C05A1B" stroke-width="2" fill="none" marker-end="url(#ar)"/>
  <text x="560" y="474" font-size="10" fill="#666">−bp_b → damping (Rq)</text>
  <!-- CV -->
  <g stroke="#2F6D8E" stroke-width="1.5" stroke-dasharray="6 3" fill="none">
    <path d="M 700 515 L 700 320 L 695 320" marker-end="url(#arw)" opacity="0"/>
    <path d="M 720 515 L 720 320" marker-end="url(#arw)"/>
    <path d="M 780 515 L 780 460" marker-end="url(#arw)"/>
  </g>
  <text x="800" y="512" font-size="10" fill="#2F6D8E">Vcm2 (bootstrap) ai gate</text>

