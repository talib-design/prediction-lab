#!/bin/bash
# Arrête le rattrapage historique. Les données déjà récupérées sont conservées.
set -euo pipefail
PLIST="$HOME/Library/LaunchAgents/fr.predictionlab.backfill.plist"
launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
rm -f "$PLIST"
echo "Rattrapage désinstallé."
