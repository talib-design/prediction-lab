#!/bin/bash
# Retire l'agent qui garde le Mac éveillé. Le journal data/logs/keepawake.log est conservé.
set -euo pipefail
LABEL="fr.predictionlab.keepawake"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
if [ -f "$PLIST" ]; then mv -n "$PLIST" "$PLIST.retire" ; fi
echo "Agent retiré (plist renommé en .retire, helper laissé dans ~/Library/Application Support/PredictionLab)."
