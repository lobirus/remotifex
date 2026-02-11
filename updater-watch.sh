#!/bin/bash
# Remotifex Update Watcher
# Polls for UI-triggered update requests and runs update.sh
# Installed as a systemd service by install.sh

REMOTIFEX_DIR="${REMOTIFEX_DIR:-/opt/remotifex}"
WATCH_DIR="$REMOTIFEX_DIR/.update"

mkdir -p "$WATCH_DIR"

echo "[remotifex-updater] Watching for update triggers at $WATCH_DIR/trigger.json"

while true; do
    if [ -f "$WATCH_DIR/trigger.json" ]; then
        echo "[remotifex-updater] Update triggered at $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
        rm -f "$WATCH_DIR/trigger.json"
        "$REMOTIFEX_DIR/update.sh" --signal --yes 2>&1 || true
        echo "[remotifex-updater] Update process finished"
    fi
    sleep 2
done
