#!/bin/bash
# Arrête et supprime l'agent de collecte. Les données déjà collectées sont conservées.
set -euo pipefail
LABEL="fr.predictionlab.collect"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
rm -f "$PLIST"
echo "Collecte automatique désinstallée."
