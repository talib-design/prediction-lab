#!/bin/bash
# Installe la collecte automatique des courses (toutes les 5 minutes) avec launchd.
#
# Usage, depuis le Terminal :   bash ops/install_collector.sh
# Désinstaller :                bash ops/uninstall_collector.sh
#
# Ce que ça fait : enregistre un agent launchd qui lance `predlab racing collect`
# toutes les 5 minutes tant que le Mac est allumé et éveillé. Un Mac en veille ne
# collecte rien : les instantanés manqués sont perdus pour de bon.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
LABEL="fr.predictionlab.collect"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
LOGS="$REPO/data/logs"
UV="$(command -v uv || true)"

if [ -z "$UV" ]; then
  echo "uv est introuvable. Installez-le (https://docs.astral.sh/uv/) puis relancez ce script."
  exit 1
fi

mkdir -p "$LOGS" "$HOME/Library/LaunchAgents"

echo "Test d'une passe de collecte avant installation…"
if ! (cd "$REPO" && "$UV" run predlab racing collect); then
  echo "La passe de test a échoué : voir le message ci-dessus. Rien n'a été installé."
  exit 1
fi

cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>$UV</string>
    <string>run</string>
    <string>--project</string>
    <string>$REPO</string>
    <string>predlab</string>
    <string>racing</string>
    <string>collect</string>
  </array>
  <key>WorkingDirectory</key><string>$REPO</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key><string>$(dirname "$UV"):/usr/bin:/bin:/usr/sbin:/sbin</string>
    <key>PREDLAB_DATA_DIR</key><string>$REPO/data</string>
  </dict>
  <key>StartInterval</key><integer>300</integer>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>$LOGS/launchd.out.log</string>
  <key>StandardErrorPath</key><string>$LOGS/launchd.err.log</string>
</dict>
</plist>
PLIST

launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "Agent installé : $PLIST"
echo "Première exécution en cours, vérification dans 30 secondes…"
sleep 30

if grep -qs "Operation not permitted" "$LOGS/launchd.err.log"; then
  cat <<'MSG'

macOS bloque l'accès au dossier Documents pour les tâches en arrière-plan.
Correctif : Réglages Système → Confidentialité et sécurité → Accès complet au disque,
ajoutez le programme uv (chemin affiché par `which uv`), puis relancez ce script.
MSG
  exit 1
fi

tail -n 5 "$LOGS/collect.log" 2>/dev/null || echo "Pas encore de ligne dans collect.log : regardez $LOGS/launchd.err.log"
echo "OK. Suivi : uv run predlab racing today"
