#!/bin/bash
# Garde le Mac éveillé pendant les heures de courses, pour que le collecteur passe dans la
# fenêtre de chaque course. Une course non figée avant son départ n'est jamais rattrapée
# (docs/METHODOLOGY.md) : un Mac en veille, c'est des courses perdues pour le bilan.
#
# Usage : bash ops/install_keepawake.sh [DÉBUT FIN SEUIL]      (défaut : 6 23 30)
# Désinstaller : bash ops/uninstall_keepawake.sh
#
# Ce que ça fait : un agent launchd tient `caffeinate -i` entre DÉBUT h et FIN h (heure du
# Mac). Seule la veille d'inactivité est bloquée : l'écran s'éteint normalement.
#   - Sur secteur : toujours actif dans la plage.
#   - Sur batterie : relâché sous SEUIL % de charge, pour ne pas vider le Mac. Il se
#     ré-active tout seul dès qu'il est rebranché ou rechargé.
#   - Hors plage : rien n'est tenu, le Mac se met en veille comme d'habitude (la passe de
#     1 h 30 a son propre caffeinate).
# Limites : un capot fermé met le Mac en veille quoi qu'on fasse, et sur batterie un Mac
# éveillé toute la journée se vide : brancher le Mac pendant les courses reste le mieux.
# DÉBUT est tôt (6 h) exprès : l'agent doit prendre la main pendant que le Mac est encore
# utilisé, sinon il s'endort avant la première course sans que rien ne puisse le réveiller.
set -euo pipefail

FROM="${1:-6}"; TO="${2:-23}"; MIN="${3:-30}"
for v in "$FROM" "$TO" "$MIN"; do
  case "$v" in ''|*[!0-9]*) echo "Arguments : trois entiers (début fin seuil), ex. 6 23 30."; exit 1;; esac
done
if [ "$FROM" -gt 23 ] || [ "$TO" -gt 24 ] || [ "$FROM" -ge "$TO" ] || [ "$MIN" -lt 5 ] || [ "$MIN" -gt 90 ]; then
  echo "Valeurs hors limites : début 0-23, fin 1-24 (après le début), seuil 5-90."
  exit 1
fi

REPO="$(cd "$(dirname "$0")/.." && pwd)"
LABEL="fr.predictionlab.keepawake"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
SUPPORT="$HOME/Library/Application Support/PredictionLab"
HELPER="$SUPPORT/keepawake.sh"
LOGS="$REPO/data/logs"
mkdir -p "$LOGS" "$HOME/Library/LaunchAgents" "$SUPPORT"

# Le script est copié hors de Documents : macOS bloque la lecture de ce dossier pour les
# tâches de fond (voir install_collector.sh).
cat > "$HELPER" <<'HELPER'
#!/bin/bash
FROM="${KEEPAWAKE_FROM:-6}"; TO="${KEEPAWAKE_TO:-23}"; MIN="${KEEPAWAKE_MIN_BATT:-30}"
TICK="${KEEPAWAKE_TICK:-60}"
CAFFEINATE="${KEEPAWAKE_CAFFEINATE:-/usr/bin/caffeinate}"
CAF=""

say() { printf '%s | %s\n' "$(date +%Y-%m-%dT%H:%M:%S%z)" "$*"; }
release() { if [ -n "$CAF" ]; then kill "$CAF" 2>/dev/null || true; fi; CAF=""; }
trap 'release; exit 0' TERM INT

say "agent démarré : plage ${FROM}h-${TO}h, seuil batterie ${MIN} %"
while true; do
  hour=$((10#$(date +%H)))
  batt="$(pmset -g batt 2>/dev/null || true)"
  pct="$(printf '%s' "$batt" | grep -Eo '[0-9]+%' | head -1 | tr -d '%' || true)"
  ac=0
  if printf '%s' "$batt" | grep -q "AC Power"; then ac=1; fi
  if [ "$ac" -eq 1 ]; then source_txt="secteur"; else source_txt="batterie ${pct:-?} %"; fi

  want=1; why="dans la plage"
  if [ "$hour" -lt "$FROM" ] || [ "$hour" -ge "$TO" ]; then
    want=0; why="hors plage"
  elif [ "$ac" -eq 0 ] && [ -n "$pct" ] && [ "$pct" -lt "$MIN" ]; then
    want=0; why="batterie sous ${MIN} %"
  fi

  alive=0
  if [ -n "$CAF" ] && kill -0 "$CAF" 2>/dev/null; then alive=1; fi
  if [ "$want" -eq 1 ] && [ "$alive" -eq 0 ]; then
    "$CAFFEINATE" -i &
    CAF=$!
    say "éveillé : ${why} (${source_txt})"
  elif [ "$want" -eq 0 ] && [ "$alive" -eq 1 ]; then
    release
    say "relâché : ${why} (${source_txt})"
  fi
  sleep "$TICK"
done
HELPER
chmod +x "$HELPER"

cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>$HELPER</string>
  </array>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key><string>/usr/bin:/bin:/usr/sbin:/sbin</string>
    <key>KEEPAWAKE_FROM</key><string>$FROM</string>
    <key>KEEPAWAKE_TO</key><string>$TO</string>
    <key>KEEPAWAKE_MIN_BATT</key><string>$MIN</string>
  </dict>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>$LOGS/keepawake.log</string>
  <key>StandardErrorPath</key><string>$LOGS/keepawake.err.log</string>
</dict>
</plist>
PLIST

launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "Agent installé : plage ${FROM}h-${TO}h, relâché sous ${MIN} % sur batterie."
sleep 3
echo "--- journal ($LOGS/keepawake.log)"
tail -n 3 "$LOGS/keepawake.log" 2>/dev/null || echo "(vide : voir $LOGS/keepawake.err.log)"
echo "--- vérification macOS (doit lister caffeinate dans la plage horaire)"
pmset -g assertions | grep -E "PreventUserIdleSystemSleep|caffeinate" || true
