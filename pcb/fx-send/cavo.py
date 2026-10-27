"""Ordine dei fili del cavo piatto 2x12 fra scheda comandi (J1) e scheda principale (J2).

Una lista sola, letta da fx-send.py e da fx-send-comandi.py: i due connettori non possono
divergere. Masse fra i gruppi; NB (cursore del LOW, massa virtuale) sta fra due masse.
"""
CAVO = ["AGND", "NA_L", "NB_L", "NC_L", "AGND", "NA_R", "NB_R", "NC_R",
        "AGND", "VHN_L", "WPH_L", "VHP_L", "AGND", "VHN_R", "WPH_R", "VHP_R",
        "AGND", "VHI_L", "LVL_W_L", "AGND", "VHI_R", "LVL_W_R", "AGND", "AGND"]
