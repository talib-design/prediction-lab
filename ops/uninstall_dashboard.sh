#!/bin/bash
# Arrête le service du tableau de bord. Aucune donnée n'est touchée.
set -euo pipefail
PLIST="$HOME/Library/LaunchAgents/fr.predictionlab.dashboard.plist"
launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
rm -f "$PLIST"
echo "Tableau de bord désinstallé (relançable à la main : uv run predlab dashboard)."
