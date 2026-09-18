#!/bin/bash
# Wrapper per simulazioni LTspice in batch mode su macOS.
#
# Perche' questo script esiste (verificato il 2026-09-18, LTspice 26.0.2):
# - LTspice per Mac e' una applicazione Windows dentro Wine (CrossOver).
# - Il launcher ufficiale (/Applications/LTspice.app/Contents/MacOS/LTspice)
#   intercetta e perde i flag CLI (-b, -o): la simulazione non parte.
# - `open -a LTspice --args ...` perde gli argomenti allo stesso modo.
# - La via funzionante: chiamare direttamente il binario wine del bundle con
#   WINEPREFIX sul bottle "ltspice" e passare il netlist con percorso
#   assoluto Windows (Z:\...). Il file va subito dopo -b. Il flag -o non
#   e' supportato: il log esce come <netlist>.log accanto al netlist.
#
# Uso:
#   ./run_ltspice.sh percorso/al/netlist.cir
#
# Output: <netlist>.log (errori, .meas, punto di lavoro) e <netlist>.raw
# (forme d'onda) nella stessa cartella del netlist.
# Avvio: ~30-60 s (inizializzazione grafica Wine anche in batch).
set -e

NETLIST="$1"
if [ -z "$NETLIST" ]; then
  echo "Uso: run_ltspice.sh <percorso-netlist>"
  exit 1
fi

# Percorso assoluto (il cwd di Wine dentro il bottle non e' affidabile)
case "$NETLIST" in
  /*) ;;
  *) NETLIST="$PWD/$NETLIST" ;;
esac
if [ ! -f "$NETLIST" ]; then
  echo "File non trovato: $NETLIST"
  exit 1
fi

export WINEPREFIX="$HOME/Library/Application Support/LTspice/Bottles/ltspice"
export WINEDEBUG=-all
WINE="/Applications/LTspice.app/Contents/SharedSupport/ltspice/bin/wine"
EXE='C:\Program Files\ADI\LTspice\LTspice.exe'

# /percorso/unix -> Z:\percorso\unix
ZPATH="Z:${NETLIST//\//\\}"

"$WINE" "$EXE" -b "$ZPATH" > /dev/null 2>&1 || {
  echo "Simulazione fallita: $NETLIST"
  exit 1
}

LOG="${NETLIST%.*}.log"
if [ -f "$LOG" ]; then
  echo "--- $LOG ---"
  cat "$LOG"
else
  echo "Simulazione eseguita ma log non trovato in $LOG"
  exit 1
fi
