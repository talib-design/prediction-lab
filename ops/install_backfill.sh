#!/bin/bash
# Installe la passe de nuit, chaque nuit à 1 h 30, sans intervention :
#   1. rattrapage de l'historique (2024, puis 2020-2023 ; jusqu'à avant-hier), 5 h maximum,
#      reprise automatique ;
#   2. reconstruction de la base ;
#   3. backtest et paris fictifs pour chaque discipline assez fournie ;
#   4. commit + push de data/carnet.jsonl et data/runs (nos décisions et rapports,
#      jamais de données PMU) : la date GitHub prouve que le carnet précède les courses.
# Un premier passage démarre tout de suite.
#
# Usage : bash ops/install_backfill.sh      Désinstaller : bash ops/uninstall_backfill.sh
#
# Mac en veille à 1 h 30 : launchd lance le passage manqué au réveil. Pendant le passage,
# caffeinate empêche la mise en veille (secteur branché ; un portable capot fermé sans écran
# externe s'endort quand même).
# Une fois tout l'historique récupéré, chaque passage ne fait plus que
# reconstruire la base (quelques minutes).
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
LABEL="fr.predictionlab.backfill"
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
    <string>/usr/bin/caffeinate</string><string>-i</string><string>-s</string>
    <string>$UV</string><string>run</string><string>--project</string><string>$REPO</string>
    <string>predlab</string><string>racing</string><string>nightly</string>
    <string>--hours</string><string>5</string>
  </array>
  <key>WorkingDirectory</key><string>$REPO</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key><string>$(dirname "$UV"):/usr/bin:/bin:/usr/sbin:/sbin</string>
    <key>PREDLAB_DATA_DIR</key><string>$REPO/data</string>
  </dict>
  <key>StartCalendarInterval</key>
  <dict><key>Hour</key><integer>1</integer><key>Minute</key><integer>30</integer></dict>
  <key>RunAtLoad</key><true/>
  <key>LowPriorityIO</key><true/>
  <key>Nice</key><integer>10</integer>
  <key>StandardOutPath</key><string>$LOGS/backfill.out.log</string>
  <key>StandardErrorPath</key><string>$LOGS/backfill.err.log</string>
</dict>
</plist>
PLIST

launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "Passe de nuit installée : premier passage en cours (5 h maximum + analyses), puis chaque nuit à 1 h 30."
echo "Suivi : tail -f \"$LOGS/backfill.out.log\""
