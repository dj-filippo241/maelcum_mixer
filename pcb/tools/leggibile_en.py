"""English text for the readable schematics (pcb/tools/leggibile.py --en).

The board files (pcb/<board>/<board>.py) stay in Italian. Only what a reader sees changes:
block titles, sheet titles, descriptive values. Net names stay as they are: they are the
same identifiers as on the PCB. A block or value missing here stops the run (leggibile.py
lists it), so a new block cannot slip through in Italian.
"""
import re

BLOCKS = {
    # canale
    "BACKPLANE C96 (classe CDJ, REV dec. 159)": "BACKPLANE C96 (CDJ class, rev. dec. 159)",
    "ALIMENTAZIONE +-18 audio, +-15 switch, +5, +-15 LN, +-5 riferimento":
        "POWER +-18 audio, +-15 switch, +5, +-15 LN, +-5 reference",
    "INGRESSO LINE [A] e GAIN T1 [B] (dec. 162)": "LINE INPUT [A] and GAIN T1 [B] (dec. 162)",
    "PONTE verso la scheda ISOLATOR (J4)": "BRIDGE to the ISOLATOR board (J4)",
    "CUE [D], SEND TAP [E] e METER [G] (pre-fader)": "CUE [D], SEND TAP [E] and METER [G] (pre-fader)",
    "FADER [H] (2 VCA, shaper del fader, dec. 126) e DIP (dec. 163)":
        "FADER [H] (2 VCAs, fader shaper, dec. 126) and DIP (dec. 163)",
    "LEVETTA HPF/OFF/LPF: logica autotemporizzata (74HC14, 74HC86, 74HC74) e ADG1434":
        "HPF/OFF/LPF TOGGLE: self-timed logic (74HC14, 74HC86, 74HC74) and ADG1434",
    "CAVO SCHEDA COMANDI (J2) e INGRESSI RCA (J3)": "CONTROL BOARD CABLE (J2) and RCA INPUTS (J3)",
    # canale isolator
    "PONTE dalla scheda segnale (J1) e bulk locali": "BRIDGE from the signal board (J1) and local bulk caps",
    "ISOLATOR lato L (incroci C, dec. 152; iso-incc-banca.inc)":
        "ISOLATOR left side (crossovers C, dec. 152; iso-incc-banca.inc)",
    "ISOLATOR lato R (incroci C, dec. 152; iso-incc-banca.inc)":
        "ISOLATOR right side (crossovers C, dec. 152; iso-incc-banca.inc)",
    "SOMMA DELL'ISOLATOR (non invertente) e SERVO DC": "ISOLATOR SUM (non-inverting) and DC SERVO",
    # fx-ret
    "BACKPLANE C96 (classe FX-RET, dec. 130)": "BACKPLANE C96 (FX-RET class, dec. 130)",
    "ALIMENTAZIONE +-18 audio, +5, +-15 LN, +-5 riferimento": "POWER +-18 audio, +5, +-15 LN, +-5 reference",
    "SOMMA DEL BUS (slot 1, Rf 10k, Cf 10p) e DRIVER DEL PEDALE":
        "BUS SUM (slot 1, Rf 10k, Cf 10p) and PEDAL DRIVER",
    "RITORNO: protezione, buffer JFET g=1, servo DC (ritorno-buffer-g1.cir)":
        "RETURN: protection, JFET buffer g=1, DC servo (ritorno-buffer-g1.cir)",
    "GAIN T2 (pot doppio 10k lin sul cavo, dec. 162; x1,24 todo 220) e EQ2":
        "GAIN T2 (dual 10k lin pot on the cable, dec. 162; x1.24 todo 220) and EQ2",
    "METER del ritorno (mono centrato, g = 0,288; detector meter-det-03s.cir)":
        "RETURN METER (centred mono, g = 0.288; detector meter-det-03s.cir)",
    "PONTE verso la scheda REROUTE (J4) e 10k verso i bus S1-S4":
        "BRIDGE to the REROUTE board (J4) and 10k to buses S1-S4",
    "FADER (2 VCA, shaper del fader, dec. 126) e USCITA verso MSUM (slot 6)":
        "FADER (2 VCAs, fader shaper, dec. 126) and OUTPUT to MSUM (slot 6)",
    "CAVO SCHEDA COMANDI (J2) e JACK DEL PEDALE (J3)": "CONTROL BOARD CABLE (J2) and PEDAL JACK (J3)",
    # fx-ret reroute
    "REROUTE verso S1 (2 VCA, I/V, driver invertente, shaper reroute, trim)":
        "REROUTE to S1 (2 VCAs, I/V, inverting driver, reroute shaper, trim)",
    "REROUTE verso S2 (2 VCA, I/V, driver invertente, shaper reroute, trim)":
        "REROUTE to S2 (2 VCAs, I/V, inverting driver, reroute shaper, trim)",
    "REROUTE verso S3 (2 VCA, I/V, driver invertente, shaper reroute, trim)":
        "REROUTE to S3 (2 VCAs, I/V, inverting driver, reroute shaper, trim)",
    "REROUTE verso S4 (2 VCA, I/V, driver invertente, shaper reroute, trim)":
        "REROUTE to S4 (2 VCAs, I/V, inverting driver, reroute shaper, trim)",
    "DRIVER D'INIEZIONE dei reroute (2 OPA1654, invertenti unity)":
        "REROUTE INJECTION DRIVERS (2 OPA1654, inverting unity)",
    # fx-send
    "BACKPLANE C96 (classe FX-SEND)": "BACKPLANE C96 (FX-SEND class)",
    "ALIMENTAZIONE +-18 audio, +-15 switch, +5": "POWER +-18 audio, +-15 switch, +5",
    "BUFFER IN (OPA1612)": "INPUT BUFFER (OPA1612)",
    "EQ2 lato L (LOW 120 Hz + HIGH 4,5 kHz, fx-eq2-pot10k.cir)":
        "EQ2 left side (LOW 120 Hz + HIGH 4.5 kHz, fx-eq2-pot10k.cir)",
    "INIEZIONE lato L (OPA1654 + 10k verso i bus)": "INJECTION left side (OPA1654 + 10k to the buses)",
    "EQ2 lato R (LOW 120 Hz + HIGH 4,5 kHz, fx-eq2-pot10k.cir)":
        "EQ2 right side (LOW 120 Hz + HIGH 4.5 kHz, fx-eq2-pot10k.cir)",
    "INIEZIONE lato R (OPA1654 + 10k verso i bus)": "INJECTION right side (OPA1654 + 10k to the buses)",
    "ASSIGN S1-S4 (ADG1434 pi SPDT, soft-switch 1 ms, mute globale)":
        "ASSIGN S1-S4 (ADG1434 pi SPDT, 1 ms soft switch, global mute)",
    "CAVO SCHEDA COMANDI (J2) e BOTTONI ASSIGN (J3)": "CONTROL BOARD CABLE (J2) and ASSIGN BUTTONS (J3)",
    # fx-send comandi
    "POT (posizioni dal render del pannello)": "POTS (positions from the panel render)",
    "CAVO VERSO LA SCHEDA PRINCIPALE": "CABLE TO THE MAIN BOARD",
    # master segnale
    "BACKPLANE C96 (classe MASTER)": "BACKPLANE C96 (MASTER class)",
    "ALIMENTAZIONE +-18 (LM317/337 + cap-moltiplicatore), +-15 LN (LT3045/LT3094)":
        "POWER +-18 (LM317/337 + capacitance multiplier), +-15 LN (LT3045/LT3094)",
    "MASTER SUMMING [A2] (invertente, 20k/20k/10p, sum-noise-71A.cir)":
        "MASTER SUMMING [A2] (inverting, 20k/20k/10p, sum-noise-71A.cir)",
    "MONO [A3] (matrice M/S + VCA su S, mono-ms.cir; resistenze NOTA)":
        "MONO [A3] (M/S matrix + VCA on S, mono-ms.cir; resistors NOTE)",
    "INS_SEND driver + INS_RET buffer (slot 9-10, ponticello JMS sul backplane)":
        "INS_SEND driver + INS_RET buffer (slots 9-10, JMS jumper on the backplane)",
    "BUFFER [A] [B] [C] [N] (un buffer per uscita, voce 11)": "BUFFERS [A] [B] [C] [N] (one buffer per output, item 11)",
    "MASTER LEVEL [D]: 2 VCA, shaper (shaper-master.cir), trim di law (vca-trim §3.2)":
        "MASTER LEVEL [D]: 2 VCAs, shaper (shaper-master.cir), law trim (vca-trim §3.2)",
    "BOOTH LEVEL [B2]: 2 VCA, shaper del fader (shaper-fader.cir), trim di law":
        "BOOTH LEVEL [B2]: 2 VCAs, fader shaper (shaper-fader.cir), law trim",
    "VIE_TAP [V]: driver dopo MASTER LEVEL verso b31-b32": "VIE_TAP [V]: driver after MASTER LEVEL to b31-b32",
    "METER [E]: detector di picco L/R (meter-det-03s.cir) e albero dei riferimenti (metering §5)":
        "METER [E]: L/R peak detector (meter-det-03s.cir) and reference tree (metering §5)",
    "CONNETTORI: J2 verso la scheda di USCITA, J3 verso la scheda COMANDI":
        "CONNECTORS: J2 to the OUTPUT board, J3 to the CONTROL board",
    # master uscita
    "BACKPLANE C96 (classe MASTER-OUT, dec. 143): solo alimentazioni":
        "BACKPLANE C96 (MASTER-OUT class, dec. 143): power only",
    "ALIMENTAZIONE [M]: statici +-26 filtrati, +-18 locali (LM317/337)":
        "POWER [M]: filtered +-26 static rails, local +-18 (LM317/337)",
    "RICEVITORE del MASTER e DRIVER del BOOTH [B3] (OPA1612 diretto, §3.4)":
        "MASTER RECEIVER and BOOTH DRIVER [B3] (direct OPA1612, §3.4)",
    "STADIO D'USCITA caldo [F]+[G] (bootstrap, dec. 86)": "OUTPUT STAGE hot [F]+[G] (bootstrap, dec. 86)",
    "STADIO D'USCITA freddo [F]+[G] (bootstrap, invertente)": "OUTPUT STAGE cold [F]+[G] (bootstrap, inverting)",
    "CLIP detector: finestra sul caldo, soglia 0,86 x statico, tenuta ~0,5 s (NOTA, da simulare)":
        "CLIP detector: window on the hot leg, threshold 0.86 x static rail, hold ~0.5 s (NOTE, to simulate)",
    "RELE' di MASTER e BOOTH (G6K-2F, 5 V, 237 ohm; eccitati = suono, failsafe)":
        "MASTER and BOOTH RELAYS (G6K-2F, 5 V, 237 ohm; energised = sound, failsafe)",
    "MUTE CONTROLLER [L] (mute-ctrl.cir, RISULTATI-mute-ctrl.md)":
        "MUTE CONTROLLER [L] (mute-ctrl.cir, RISULTATI-mute-ctrl.md)",
    "CONNETTORI: J2 dalla scheda di segnale, J3 verso la schedina dei connettori sul retro":
        "CONNECTORS: J2 from the signal board, J3 to the rear connector board",
    "COMANDO DEI RELE' dalla GLOBAL_MUTE (c9): basso = suona":
        "RELAY DRIVE from GLOBAL_MUTE (c9): low = sound",
    # mic
    "BACKPLANE C96 (classe MIC/GEN, MSUM6)": "BACKPLANE C96 (MIC/GEN class, MSUM6)",
    "ALIM: +18V (LM317 + BD139)": "POWER: +18V (LM317 + BD139)",
    "ALIM: -18V (LM337 + BD140)": "POWER: -18V (LM337 + BD140)",
    "ALIM: +15SW (78L15)": "POWER: +15SW (78L15)",
    "ALIM: -15SW (79L15)": "POWER: -15SW (79L15)",
    "ALIM: +5VF": "POWER: +5VF",
    "ALIM: +15LN (LT3045)": "POWER: +15LN (LT3045)",
    "ALIM: -15LN (LT3094)": "POWER: -15LN (LT3094)",
    "INGRESSO XLR: RFI, clamp, carico 2,32k, bias 2x47k (mic-pre.inc)":
        "XLR INPUT: RFI, clamp, 2.32k load, 2x47k bias (mic-pre.inc)",
    "INA +30,05 dB e differenziale unity (OPA1612)": "INA +30.05 dB and unity differential (OPA1612)",
    "PASSA-ALTO 60 Hz, STADIO 2 (0...+30 dB), DETECTOR del LED (OPA1654)":
        "HIGH-PASS 60 Hz, STAGE 2 (0...+30 dB), LED DETECTOR (OPA1654)",
    "LED tricolore (LM339)": "Three-colour LED (LM339)",
    "EQ2 (+-18)": "EQ2 (+-18)",
    "VCA del MUTE e del limiter (dec. 111, 145; sim/mic/mic-limiter.cir)":
        "MUTE and limiter VCA (dec. 111, 145; sim/mic/mic-limiter.cir)",
    "DRIVER MSUM6 L/R (invertenti, todo 227)": "MSUM6 L/R DRIVERS (inverting, todo 227)",
    "MANDATE S1-S4 (pot sul cavo, mute globale, iniezione)": "SENDS S1-S4 (pots on the cable, global mute, injection)",
    "CAVO SCHEDA COMANDI (J2)": "CONTROL BOARD CABLE (J2)",
    # mic comandi
    "COMANDI (posizioni dal render del pannello)": "CONTROLS (positions from the panel render)",
    # mono
    "BACKPLANE C96 (classe MIC/GEN, MSUM7)": "BACKPLANE C96 (MIC/GEN class, MSUM7)",
    "INGRESSO JACK TS: R serie, clamp, TVS, C film, bias 1M":
        "TS JACK INPUT: series R, clamp, TVS, film C, 1M bias",
    "BUFFER, MAKE-UP +10 dB, DETECTOR del LED (OPA1654)": "BUFFER, MAKE-UP +10 dB, LED DETECTOR (OPA1654)",
    "DRIVER MSUM7 L/R (invertenti, todo 227)": "MSUM7 L/R DRIVERS (inverting, todo 227)",
    # psu-in
    "BACKPLANE C96 (slot PSU-IN): riga a intera, AC_OK su c17": "BACKPLANE C96 (PSU-IN slot): whole row a, AC_OK on c17",
    "CAVO DAL BOX (20 conduttori, §3)": "CABLE FROM THE BOX (20 conductors, §3)",
    "RAIL AUDIO +-22,0 V (pin raw +-27): T4 A, TVS 26 V, 2,2 mF":
        "AUDIO RAIL +-22.0 V (raw +-27 pins): T4 A, TVS 26 V, 2.2 mF",
    "RAIL LN +-19 V (pin raw +-22): T1 A, TVS 22 V, 1 mF": "LN RAIL +-19 V (raw +-22 pins): T1 A, TVS 22 V, 1 mF",
    "RAIL [M] raw +-27 V (pin raw +-26): T500 mA, TVS 33 V, 1 mF":
        "RAIL [M] raw +-27 V (raw +-26 pins): T500 mA, TVS 33 V, 1 mF",
    "RAIL +5 V: T2 A, TVS 5,0 V, 1 mF": "RAIL +5 V: T2 A, TVS 5.0 V, 1 mF",
    "V_FAN (T500 mA) e AC_OK": "V_FAN (T500 mA) and AC_OK",
    "STELLA analogue-0V (§4.2, grounding §2)": "analogue-0V STAR (§4.2, grounding §2)",
    # master, scheda comandi
    "POT e TASTO MONO (posizioni dal render del pannello)": "POTS and MONO BUTTON (positions from the panel render)",
    "METER L e R: 2 LM3915 in cascata per lato, 20 LED": "METERS L and R: 2 cascaded LM3915 per side, 20 LEDs",
    "CAVI: J1 verso la scheda di segnale (J3), J2 verso la scheda d'uscita L (J4)":
        "CABLES: J1 to the signal board (J3), J2 to the L output board (J4)",
    # canale, scheda comandi
    "POT: GAIN e ISOLATOR (pot doppi, sezione A = L, B = R)": "POTS: GAIN and ISOLATOR (dual pots, section A = L, B = R)",
    "LEVETTE: FILTRO (HPF/OFF/LPF) e LINE/PHONO": "TOGGLES: FILTER (HPF/OFF/LPF) and LINE/PHONO",
    "BOTTONI: FX1-4 (assign verso il FX-SEND) e CUE": "BUTTONS: FX1-4 (assign to the FX-SEND) and CUE",
    "METER: un LM3915, 10 LED (+24...-3 dBu)": "METER: one LM3915, 10 LEDs (+24...-3 dBu)",
    "FADER (PTA6043, corsa 60 mm, dec. 169)": "FADER (PTA6043, 60 mm travel, dec. 169)",
    "CAVI: J2 verso canale.py (J2), J3 verso fx-send.py (J3)": "CABLES: J2 to canale.py (J2), J3 to fx-send.py (J3)",
    "POT: GAIN (doppio), EQ2 (doppi), REROUTE (singoli con scatto)": "POTS: GAIN (dual), EQ2 (dual), REROUTE (single, centre detent)",
    "FADER (PTA4543, corsa 45 mm, dec. 169)": "FADER (PTA4543, 45 mm travel, dec. 169)",
    "CAVO: J2 verso fx-ret.py (J2)": "CABLE: J2 to fx-ret.py (J2)",
    # cue
    "BACKPLANE C96 (classe CUE: slot 1-4 = CUE1-4 in, slot 5 = MON in)":
        "BACKPLANE C96 (CUE class: slots 1-4 = CUE1-4 in, slot 5 = MON in)",
    "ALIMENTAZIONE +18 audio (LM317 dal raw +27, bulk 1000 uF)": "POWER +18 audio (LM317 from raw +27, 1000 uF bulk)",
    "ALIMENTAZIONE -18 audio (LM337 dal raw -27, bulk 1000 uF)": "POWER -18 audio (LM337 from raw -27, 1000 uF bulk)",
    "ALIMENTAZIONE +15 LN (LM317 a +16,5 dal raw +22, poi LT3045)":
        "POWER +15 LN (LM317 to +16.5 from raw +22, then LT3045)",
    "ALIMENTAZIONE -15 LN (LM337 a -16,5 dal raw -22, poi LT3094)":
        "POWER -15 LN (LM337 to -16.5 from raw -22, then LT3094)",
    "[A] CUE SUMMING L/R (massa virtuale, Rf 10k, -1) e [B] MON (invertente 20k/20k, F4)":
        "[A] CUE SUMMING L/R (virtual earth, Rf 10k, -1) and [B] MON (inverting 20k/20k, F4)",
    "[C2] buffer fra BLEND e LEVEL (NOTA: tiene la law del blend esatta)":
        "[C2] buffer between BLEND and LEVEL (keeps the blend law exact)",
    "[E] AMPLI CUFFIA L (OPA1612 + diamond MJE340/350, v0.2)": "[E] HEADPHONE AMP L (OPA1612 + MJE340/350 diamond, v0.2)",
    "[E] AMPLI CUFFIA R (OPA1612 + diamond MJE340/350, v0.2)": "[E] HEADPHONE AMP R (OPA1612 + MJE340/350 diamond, v0.2)",
    "[F] RELE' delle cuffie (G6K-2F, 5 V, 237 ohm; eccitati = suono; failsafe)":
        "[F] HEADPHONE RELAYS (G6K-2F, 5 V, 237 ohm; energised = sound; failsafe)",
    "[G] PROTEZIONE: finestre sui raw +-22 e +-27, timer 1,8 s (il CUE non ascolta c9)":
        "[G] PROTECTION: windows on raw +-22 and +-27, 1.8 s timer (the CUE ignores c9)",
    "[F] RSERIE L (10 ohm 2 W, una per jack)": "[F] SERIES R L (10 ohm 2 W, one per jack)",
    "[F] RSERIE R (10 ohm 2 W, una per jack)": "[F] SERIES R R (10 ohm 2 W, one per jack)",
    "CAVI verso la scheda comandi: J2 pot, J3 cuffie": "CABLES to the control board: J2 pots, J3 headphones",
    # cue, scheda comandi
    "POT BLEND e LEVEL, JACK delle cuffie (posizioni dal render del pannello)":
        "BLEND and LEVEL POTS, HEADPHONE JACKS (positions from the panel render)",
    "CAVI: J3 pot (J2 di cue.py), J4 cuffie (J3 di cue.py)": "CABLES: J3 pots (J2 of cue.py), J4 headphones (J3 of cue.py)",
}

VALUES = {
    "1x5 ingressi": "1x5 inputs",
    "2u2 film": "2u2 film",
    "2x18 cavo piatto": "2x18 ribbon cable",
    "2x2 cavo piatto": "2x2 ribbon cable",
    "2x18 ponte isolator": "2x18 isolator bridge",
    "C96 maschio": "C96 male",
    "TVS bidir <=5 pF": "TVS bidir. <=5 pF",
    "ferrite 600R": "ferrite 600R",
    "1x7 jack pedale": "1x7 pedal jack",
    "2x16 ponte reroute": "2x16 reroute bridge",
    "1x6 bottoni": "1x6 buttons",
    "2x12 cavo piatto": "2x12 ribbon cable",
    "10k doppio": "10k dual",
    "10k lin doppio selezionato": "10k lin dual, matched",
    "10k lin B doppio": "10k lin B dual",
    "2x10 cavo piatto": "2x10 ribbon cable",
    "2x7 cavo piatto": "2x7 ribbon cable",
    "2x2 cavo": "2x2 cable",
    "2x5 cavo": "2x5 cable",
    "ferrite 600R 2A": "ferrite 600R 2A",
    "XLR (cavo)": "XLR (cable)",
    "LED bicolore VR 3 mm": "two-colour LED VR 3 mm",
    "tasto MUTE": "MUTE button",
    "2x11 cavo piatto": "2x11 ribbon cable",
    "TVS bidir. low-cap 24 V": "TVS bidir. low-cap 24 V",
    "jack TS (cavo)": "TS jack (cable)",
    "1x3 driver ventole": "1x3 fan driver",
    "Mini-Fit Jr 2x12": "Mini-Fit Jr 2x12",
    "bond CHASSIS-AGND": "CHASSIS-AGND bond",
    "jack TS (cavo)": "TS jack (cable)",
    "2x3 cavo": "2x3 cable",
    "2x3 cavo piatto": "2x3 ribbon cable",
    "10k lin, scatto al centro": "10k lin, centre detent",
    "jack stereo 6,3": "6.3 mm stereo jack",
}

# Words that mean the value is Italian prose, not a part number: a value with one of them and
# no entry in VALUES stops the run.
ITALIAN = re.compile(r"\b(cavo|piatto|maschio|femmina|ponte|ponticello|presa|potenza|pilotato|ingress\w*|"
                     r"bottoni|doppio|tasto|bicolore|ventole|pedale|lato|verso|scheda|della|del|dei|con|senza)\b",
                     re.I)

# backplane (pcb/backplane/tratto.py): one block per slot, cable and power connector, named by
# pattern, so the rules below cover every slot of the four sections
SLOT_CLASS = {"master": "MASTER", "uscita": "MASTER-OUT", "5way": "5-WAY", "psu-in": "PSU-IN",
              "canale": "CHANNEL", "fx-send": "FX-SEND", "filtro": "FILTER", "cue": "CUE",
              "mic": "MIC", "mono": "MONO", "fx-ret": "FX-RET"}


def _slot(m):
    c = SLOT_CLASS.get(m.group(2))
    return None if c is None else "SLOT %s (%s class)" % (m.group(1), c)


BLOCK_RULES = [
    (r"SLOT (\S+) \(([\w-]+)\)", _slot),
    (r"CAVO (C\d+)", lambda m: "CABLE " + m.group(1)),
    (r"POTENZA (P\d+)", lambda m: "POWER " + m.group(1)),
    (r"PONTICELLI", lambda m: "JUMPERS AND HEADERS (dec. 111)"),
]

VALUE_RULES = [
    (r"cavo (C\d+ T\d-T\d) \(VE\)", lambda m: "ribbon cable %s (virtual earth)" % m.group(1)),
    (r"cavo (C\d+ T\d-T\d) \(pilotato\)", lambda m: "ribbon cable %s (driven lines)" % m.group(1)),
    (r"C96 femmina (\S+)", lambda m: "C96 female " + m.group(1)),
    (r"potenza (P\d+ T\d-T\d)", lambda m: "power " + m.group(1)),
    (r"ponticello (\S+)", lambda m: "jumper " + m.group(1)),
    (r"presa (\S+)", lambda m: "header " + m.group(1)),
]

TITLE = [
    (r"scheda di segnale", "signal board"),
    (r"scheda di USCITA", "OUTPUT board"),
    (r"scheda comandi", "control board"),
    (r"\bCANALE\b", "CHANNEL"),
    (r"\bCANALI\b", "CHANNELS"),
    (r"\bFILTRO\b", "FILTER"),
    (r"\(fondo:", "(rear:"),
    (r"\(canali:", "(channels:"),
    (r"\(cuffie:", "(headphones:"),
    (r"\(destra:", "(right:"),
    (r"\bbozza\b", "draft"),
]


def title(t):
    for a, b in TITLE:
        t = re.sub(a, b, t)
    return t


def rev(r):
    return r.replace("bozza", "draft")


def _rule(rules, s):
    for a, f in rules:
        m = re.fullmatch(a, s)
        if m:
            return f(m)
    return None


def block(b):
    return BLOCKS.get(b) or _rule(BLOCK_RULES, b)


def value(v):
    if v in VALUES:
        return VALUES[v]
    e = _rule(VALUE_RULES, v)
    if e is not None:
        return e
    return None if ITALIAN.search(v) else v
