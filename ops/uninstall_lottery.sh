#!/bin/bash
# Retire l'agent launchd du suivi EuroMillions. Le carnet et les données restent.
set -euo pipefail
LABEL="fr.predictionlab.lottery"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
if [ -f "$PLIST" ]; then
  mv -n "$PLIST" "$PLIST.retire"
  echo "Agent arrêté ; fichier renommé en $PLIST.retire (rien n'est effacé)."
else
  echo "Aucun agent installé."
fi
