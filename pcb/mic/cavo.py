"""Ordine dei fili del cavo piatto 2x12 fra scheda comandi (J1) e scheda principale (J2) del MIC.

Una lista sola, letta da mic.py e da mic-comandi.py: i due connettori non possono divergere.
Masse fra i gruppi; GINV (massa virtuale dello stadio 2) e NB (cursore del LOW) stanno fra
fili di segnale del loro pot, con una massa ai lati del gruppo.
"""
CAVO = ["AGND", "GP1", "GINV", "GP2", "AGND", "NA", "NB", "NC", "AGND", "VHN", "WPH", "VHP",
        "AGND", "POST", "SW1", "SW2", "SW3", "SW4", "AGND", "+5VF", "LKG", "LKR", "MUTE_SW", "CTRL_GND"]
