#!/bin/bash
set -e

# Remotifex Uninstall Script
# Usage: ./uninstall.sh

REMOTIFEX_DIR="${REMOTIFEX_DIR:-/opt/remotifex}"
AUTO_YES=false
KEEP_DATA=false

show_help() {
    echo "Remotifex Uninstaller"
    echo ""
    echo "Usage: ./uninstall.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -y, --yes         Auto-accept all prompts (non-interactive mode)"
    echo "  --keep-data       Keep project data and database volumes"
    echo "  -h, --help        Show this help message"
    echo ""
    echo "Environment variables:"
    echo "  REMOTIFEX_DIR  Installation directory (default: /opt/remotifex)"
    echo ""
    echo "What gets removed:"
    echo "  - Docker containers, images, and networks"
    echo "  - Docker volumes (unless --keep-data is used)"
    echo "  - The remotifex-updater systemd service"
    echo "  - The installation directory ($REMOTIFEX_DIR)"
    echo ""
    echo "What is NOT removed:"
    echo "  - Docker itself"
    echo "  - Firewall rules added during install"
    exit 0
}

# Parse flags
for arg in "$@"; do
    case "$arg" in
        -y|--yes) AUTO_YES=true ;;
        --keep-data) KEEP_DATA=true ;;
        -h|--help) show_help ;;
    esac
done

confirm() {
    local prompt="$1"
    if [ "$AUTO_YES" = true ]; then
        echo "$prompt [y/N] y (auto-accepted)"
        return 0
    fi
    read -r -p "$prompt [y/N] " response
    case "$response" in
        [yY][eE][sS]|[yY]) return 0 ;;
        *) return 1 ;;
    esac
}

# Compose command helper
compose_cmd() {
    if command -v docker compose &> /dev/null; then
        docker compose "$@"
    else
        docker-compose "$@"
    fi
}

echo ""
echo "  ╔═══════════════════════════════════════╗"
echo "  ║        Remotifex Uninstaller          ║"
echo "  ║   Comfortable Remote AI Development   ║"
echo "  ╚═══════════════════════════════════════╝"
echo ""

if [ ! -d "$REMOTIFEX_DIR" ]; then
    echo "[!!] Remotifex not found at $REMOTIFEX_DIR"
    echo "     Set REMOTIFEX_DIR if installed elsewhere."
    exit 1
fi

echo "[!!] This will permanently remove Remotifex from this system."
if [ "$KEEP_DATA" = true ]; then
    echo "     Docker volumes (database, project data) will be kept."
else
    echo "     All data including projects and database will be deleted."
fi
echo ""

if ! confirm "    Are you sure you want to uninstall Remotifex?"; then
    echo "[..] Uninstall cancelled"
    exit 0
fi

echo ""

# --- Step 1: Stop and remove containers ---
echo "[..] Step 1/3: Stopping services..."

cd "$REMOTIFEX_DIR"

if [ -f "docker-compose.yml" ]; then
    if [ "$KEEP_DATA" = true ]; then
        compose_cmd down --rmi all 2>/dev/null || true
    else
        compose_cmd down --rmi all --volumes 2>/dev/null || true
    fi
    echo "[OK] Containers, images, and networks removed"
else
    echo "[OK] No docker-compose.yml found, skipping"
fi

# --- Step 2: Remove systemd service ---
echo ""
echo "[..] Step 2/3: Removing updater service..."

if command -v systemctl &> /dev/null && [ -f /etc/systemd/system/remotifex-updater.service ]; then
    systemctl stop remotifex-updater 2>/dev/null || true
    systemctl disable remotifex-updater 2>/dev/null || true
    rm -f /etc/systemd/system/remotifex-updater.service
    systemctl daemon-reload 2>/dev/null || true
    echo "[OK] Updater service removed"
else
    echo "[OK] No updater service found, skipping"
fi

# --- Step 3: Remove installation directory ---
echo ""
echo "[..] Step 3/3: Removing installation directory..."

cd /
rm -rf "$REMOTIFEX_DIR"
echo "[OK] Removed $REMOTIFEX_DIR"

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║     Remotifex has been removed.      ║"
echo "  ╚══════════════════════════════════════╝"
echo ""
if [ "$KEEP_DATA" = true ]; then
    echo "  Docker volumes were kept. To remove them manually:"
    echo "    docker volume ls | grep remotifex"
    echo "    docker volume rm <volume_name>"
    echo ""
fi
echo "  To reinstall: curl -fsSL https://get.remotifex.com | bash"
echo ""
