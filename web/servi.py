#!/usr/bin/env python3
"""Apre il banco del mixer nel browser: http://localhost:8765
Serve la cartella web/ con le due intestazioni che danno alla pagina la memoria condivisa
(il 5-way gira in un Worker a parte). Nessun pacchetto da installare.
Uso: python3 web/servi.py [--senza-browser]      (Ctrl+C per fermare)
"""
import http.server
import os
import socketserver
import sys
import webbrowser

PORTA = 8765
QUI = os.path.dirname(os.path.abspath(__file__))


class Gestore(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      ".js": "text/javascript", ".mjs": "text/javascript", ".json": "application/json"}

    def __init__(self, *a, **k):
        super().__init__(*a, directory=QUI, **k)

    def end_headers(self):
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *a):
        pass


socketserver.TCPServer.allow_reuse_address = True
with socketserver.ThreadingTCPServer(("127.0.0.1", PORTA), Gestore) as s:
    url = f"http://localhost:{PORTA}/"
    print(f"Banco del mixer: {url}  (Ctrl+C per fermare)")
    if "--senza-browser" not in sys.argv:
        webbrowser.open(url)
    try:
        s.serve_forever()
    except KeyboardInterrupt:
        pass
