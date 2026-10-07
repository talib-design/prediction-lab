#!/bin/bash
# Installe le suivi automatique EuroMillions (carnet à terme) avec launchd.
#
# Usage, depuis le Terminal :   bash ops/install_lottery.sh
# Désinstaller :                bash ops/uninstall_lottery.sh
#
# Ce que ça fait : toutes les heures, `predlab lottery forward`
#   1. télécharge l'archive FDJ du moment si un tirage publié manque (mardi, vendredi) ;
#   2. note les grilles déjà figées avec le résultat et les rapports officiels ;
#   3. fige une grille par logique (+ le témoin hasard) pour le prochain tirage,
#      avant 20 h le jour du tirage (clôture des ventes en bureau de tabac et en ligne).
# Aucune mise, aucun compte FDJ : ce sont des grilles fictives, jamais jouées.
# N'utilise ni ne modifie la collecte des courses. Ne pousse rien sur GitHub.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
LABEL="fr.predictionlab.lottery"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
LOGS="$REPO/data/logs"
UV="$(command -v uv || true)"

if [ -z "$UV" ]; then
  echo "uv est introuvable. Installez-le (https://docs.astral.sh/uv/) puis relancez ce script."
  exit 1
fi

mkdir -p "$LOGS" "$HOME/Library/LaunchAgents"

echo "Passe de test avant installation (téléchargement FDJ compris)…"
if ! (cd "$REPO" && PREDLAB_DATA_DIR="$REPO/data" "$UV" run predlab lottery forward); then
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
    <string>lottery</string>
    <string>forward</string>
  </array>
  <key>WorkingDirectory</key><string>$REPO</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key><string>$(dirname "$UV"):/usr/bin:/bin:/usr/sbin:/sbin</string>
    <key>PREDLAB_DATA_DIR</key><string>$REPO/data</string>
  </dict>
  <key>StartInterval</key><integer>3600</integer>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>$LOGS/lottery.log</string>
  <key>StandardErrorPath</key><string>$LOGS/lottery.err.log</string>
</dict>
</plist>
PLIST

launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "Agent installé : $PLIST"
sleep 20
if grep -qs "Operation not permitted" "$LOGS/lottery.err.log"; then
  cat <<'MSG'

macOS bloque l'accès au dossier Documents pour les tâches en arrière-plan.
Correctif : Réglages Système → Confidentialité et sécurité → Accès complet au disque,
ajoutez le programme uv (chemin affiché par `which uv`), puis relancez ce script.
MSG
  exit 1
fi
tail -n 5 "$LOGS/lottery.log" 2>/dev/null || true
echo "OK. Suivi : uv run predlab lottery carnet"
