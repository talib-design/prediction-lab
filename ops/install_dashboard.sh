#!/bin/bash
# Installe le tableau de bord comme service : il démarre avec la session macOS, tourne
# en arrière-plan et redémarre s'il s'arrête. Plus besoin de Terminal.
#
#   Adresse fixe : http://127.0.0.1:8790   (à mettre en favori)
#
# Usage : bash ops/install_dashboard.sh     Désinstaller : bash ops/uninstall_dashboard.sh
# Après une mise à jour du code : relancer ce script (il redémarre le service).
#
# Lecture seule, joignable uniquement depuis ce Mac (127.0.0.1).
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
LABEL="fr.predictionlab.dashboard"
PORT=8790
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
LOGS="$REPO/data/logs"
UV="$(command -v uv || true)"
[ -z "$UV" ] && { echo "uv est introuvable."; exit 1; }
mkdir -p "$LOGS" "$HOME/Library/LaunchAgents"

cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>$UV</string><string>run</string><string>--project</string><string>$REPO</string>
    <string>predlab</string><string>dashboard</string>
    <string>--port</string><string>$PORT</string><string>--strict-port</string><string>--no-open</string>
  </array>
  <key>WorkingDirectory</key><string>$REPO</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key><string>$(dirname "$UV"):/usr/bin:/bin:/usr/sbin:/sbin</string>
    <key>PREDLAB_DATA_DIR</key><string>$REPO/data</string>
  </dict>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>ThrottleInterval</key><integer>30</integer>
  <key>StandardOutPath</key><string>$LOGS/dashboard.out.log</string>
  <key>StandardErrorPath</key><string>$LOGS/dashboard.err.log</string>
</dict>
</plist>
PLIST

launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
# Let the previous instance release the port before the new one binds it.
for _ in 1 2 3 4 5 6 7 8 9 10; do
  curl -fs "http://127.0.0.1:$PORT/api/health" >/dev/null 2>&1 || break
  sleep 1
done
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "Démarrage du tableau de bord…"
ok=""
for _ in $(seq 1 40); do
  if curl -fs "http://127.0.0.1:$PORT/api/health" >/dev/null 2>&1; then ok=1; break; fi
  sleep 1
done
if [ -n "$ok" ]; then
  echo "Tableau de bord actif : http://127.0.0.1:$PORT  (ouvert automatiquement à chaque session)"
  open "http://127.0.0.1:$PORT/" || true
else
  echo "Le service démarre encore, ou le port $PORT est pris. Journal :"
  tail -n 5 "$LOGS/dashboard.err.log" 2>/dev/null || true
fi
