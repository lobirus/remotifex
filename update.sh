#!/bin/bash
set -e

# Remotifex Update Script
# Usage: curl -fsSL https://update.remotifex.com | bash

REMOTIFEX_DIR="${REMOTIFEX_DIR:-/opt/remotifex}"
AUTO_YES=false
SIGNAL_MODE=false
USE_MAIN=false
UPDATE_DIR=""
ROLLBACK_COMMIT=""

show_help() {
    echo "Remotifex Updater"
    echo ""
    echo "Usage: curl -fsSL https://update.remotifex.com | bash [-s -- OPTIONS]"
    echo "       ./update.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -y, --yes     Auto-accept all prompts (non-interactive mode)"
    echo "  --main        Update to the latest main branch instead of the latest release"
    echo "  --signal      Signal mode for UI-triggered updates (writes status to .update/)"
    echo "  -h, --help    Show this help message"
    echo ""
    echo "Environment variables:"
    echo "  REMOTIFEX_DIR  Installation directory (default: /opt/remotifex)"
    echo ""
    echo "Examples:"
    echo "  curl -fsSL https://update.remotifex.com | bash"
    echo "  curl -fsSL https://update.remotifex.com | bash -s -- -y"
    echo "  curl -fsSL https://update.remotifex.com | bash -s -- --main"
    echo "  ./update.sh --main -y"
    exit 0
}

# Parse flags
for arg in "$@"; do
    case "$arg" in
        -y|--yes) AUTO_YES=true ;;
        --signal) SIGNAL_MODE=true; AUTO_YES=true ;;
        --main) USE_MAIN=true ;;
        -h|--help) show_help ;;
    esac
done

if [ "$SIGNAL_MODE" = true ]; then
    UPDATE_DIR="$REMOTIFEX_DIR/.update"
    mkdir -p "$UPDATE_DIR"
fi

# Prompt user for confirmation. Auto-accepts if -y flag is set.
confirm() {
    local prompt="$1"
    if [ "$AUTO_YES" = true ]; then
        log "$prompt [y/N] y (auto-accepted)"
        return 0
    fi
    read -r -p "$prompt [y/N] " response
    case "$response" in
        [yY][eE][sS]|[yY]) return 0 ;;
        *) return 1 ;;
    esac
}

# Log output — also writes to .update/output.log in signal mode
log() {
    echo "$@"
    if [ "$SIGNAL_MODE" = true ]; then
        echo "$@" >> "$UPDATE_DIR/output.log"
    fi
}

# Write status JSON for UI consumption
write_status() {
    if [ "$SIGNAL_MODE" != true ]; then return; fi
    local status="$1"
    local step="$2"
    local error="${3:-}"
    local now
    now=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    cat > "$UPDATE_DIR/status.json" << STATUSEOF
{
    "status": "$status",
    "step": "$step",
    "current_version": "$CURRENT_VERSION",
    "new_version": "$LATEST_VERSION",
    "started_at": "$UPDATE_STARTED",
    "completed_at": "$now",
    "error": "$error"
}
STATUSEOF
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
echo "  ║          Remotifex Updater            ║"
echo "  ║   Comfortable Remote AI Development   ║"
echo "  ╚═══════════════════════════════════════╝"
echo ""

# Clear previous log in signal mode
if [ "$SIGNAL_MODE" = true ]; then
    > "$UPDATE_DIR/output.log"
fi

UPDATE_STARTED=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# --- Step 1: Verify installation ---
log "[..] Step 1/5: Checking installation..."

if [ ! -d "$REMOTIFEX_DIR" ]; then
    log "[!!] Remotifex not found at $REMOTIFEX_DIR"
    log "     Set REMOTIFEX_DIR or install first: curl -fsSL https://get.remotifex.com | bash"
    write_status "failed" "check_installation" "Remotifex not found at $REMOTIFEX_DIR"
    exit 1
fi

cd "$REMOTIFEX_DIR"

if [ ! -f "docker-compose.yml" ]; then
    log "[!!] Not a valid Remotifex installation (missing docker-compose.yml)"
    write_status "failed" "check_installation" "Invalid installation directory"
    exit 1
fi

CURRENT_VERSION="unknown"
if [ -f "VERSION" ]; then
    CURRENT_VERSION=$(cat VERSION | tr -d '[:space:]')
fi

log "[OK] Remotifex installation found at $REMOTIFEX_DIR (v$CURRENT_VERSION)"

# --- Step 2: Check for updates ---
log ""
log "[..] Step 2/5: Checking for updates..."
write_status "in_progress" "checking_updates"

git fetch --tags --quiet 2>/dev/null || {
    log "[!!] Failed to fetch from remote. Check your network connection."
    write_status "failed" "checking_updates" "Failed to fetch from remote"
    exit 1
}

if [ "$USE_MAIN" = true ]; then
    # Main branch mode: compare HEAD against origin/main
    LATEST_VERSION="main ($(git rev-parse --short origin/main 2>/dev/null))"
    LOCAL_HEAD=$(git rev-parse HEAD 2>/dev/null)
    REMOTE_HEAD=$(git rev-parse origin/main 2>/dev/null)

    if [ "$LOCAL_HEAD" = "$REMOTE_HEAD" ]; then
        log "[OK] Already running the latest main branch (v$CURRENT_VERSION)"
        write_status "completed" "up_to_date"
        exit 0
    fi

    log "[OK] Update available: v$CURRENT_VERSION → $LATEST_VERSION"
else
    # Release mode: compare against latest tag
    LATEST_TAG=$(git tag -l 'v*' --sort=-version:refname | head -n1)

    if [ -z "$LATEST_TAG" ]; then
        log "[!!] No release tags found in remote"
        write_status "failed" "checking_updates" "No release tags found"
        exit 1
    fi

    LATEST_VERSION="${LATEST_TAG#v}"

    if [ "$CURRENT_VERSION" = "$LATEST_VERSION" ]; then
        log "[OK] Already running the latest version (v$CURRENT_VERSION)"
        write_status "completed" "up_to_date"
        exit 0
    fi

    log "[OK] Update available: v$CURRENT_VERSION → v$LATEST_VERSION"
fi

# --- Step 3: Show what's new ---
log ""
write_status "in_progress" "showing_changes"

if [ "$USE_MAIN" = true ]; then
    log "[..] Step 3/5: Changes on main since current HEAD..."
    CHANGES=$(git log --oneline "HEAD..origin/main" 2>/dev/null | head -20)
    if [ -n "$CHANGES" ]; then
        log ""
        log "$CHANGES"
        CHANGE_COUNT=$(git log --oneline "HEAD..origin/main" 2>/dev/null | wc -l | tr -d '[:space:]')
        if [ "$CHANGE_COUNT" -gt 20 ]; then
            log "    ... and $((CHANGE_COUNT - 20)) more commits"
        fi
        log ""
    fi
else
    log "[..] Step 3/5: Changes in v$LATEST_VERSION..."
    CURRENT_TAG="v$CURRENT_VERSION"

    if git rev-parse "$CURRENT_TAG" &>/dev/null; then
        CHANGES=$(git log --oneline "$CURRENT_TAG..$LATEST_TAG" 2>/dev/null | head -20)
        if [ -n "$CHANGES" ]; then
            log ""
            log "$CHANGES"
            CHANGE_COUNT=$(git log --oneline "$CURRENT_TAG..$LATEST_TAG" 2>/dev/null | wc -l | tr -d '[:space:]')
            if [ "$CHANGE_COUNT" -gt 20 ]; then
                log "    ... and $((CHANGE_COUNT - 20)) more commits"
            fi
            log ""
        fi
    else
        log "    (Cannot show changes — current version tag not found)"
        log ""
    fi
fi

if ! confirm "    Proceed with update?"; then
    log "[..] Update cancelled"
    exit 0
fi

# --- Step 4: Pull latest code ---
log ""
log "[..] Step 4/5: Pulling latest code..."
write_status "in_progress" "pulling_code"

# Record rollback point
ROLLBACK_COMMIT=$(git rev-parse HEAD)

# Check for local modifications
if ! git diff --quiet 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
    log "[!!] Local modifications detected — stashing changes..."
    git stash --quiet
fi

if [ "$USE_MAIN" = true ]; then
    git checkout main --quiet 2>/dev/null || true
    if ! git pull --ff-only --quiet 2>/dev/null; then
        log "[!!] Fast-forward pull failed. Attempting reset to origin/main..."
        git reset --hard origin/main --quiet 2>/dev/null || {
            log "[!!] Failed to update code"
            write_status "failed" "pulling_code" "Git pull failed"
            exit 1
        }
    fi
else
    if ! git pull --ff-only 2>/dev/null; then
        log "[!!] Fast-forward pull failed. Attempting reset to $LATEST_TAG..."
        git checkout "$LATEST_TAG" --quiet 2>/dev/null || {
            log "[!!] Failed to update code"
            write_status "failed" "pulling_code" "Git pull failed"
            exit 1
        }
    fi
fi

NEW_VERSION="unknown"
if [ -f "VERSION" ]; then
    NEW_VERSION=$(cat VERSION | tr -d '[:space:]')
fi

log "[OK] Code updated to v$NEW_VERSION"

# --- Step 5: Rebuild and restart ---
log ""
log "[..] Step 5/5: Rebuilding and restarting services..."
write_status "in_progress" "rebuilding"

if ! compose_cmd build 2>&1 | while IFS= read -r line; do log "    $line"; done; then
    log ""
    log "[!!] Build failed — rolling back to previous version..."
    write_status "in_progress" "rolling_back"
    git checkout "$ROLLBACK_COMMIT" --quiet 2>/dev/null
    compose_cmd build --quiet 2>/dev/null
    compose_cmd up -d 2>/dev/null
    log "[!!] Rolled back to v$CURRENT_VERSION"
    write_status "failed" "rebuilding" "Build failed, rolled back to v$CURRENT_VERSION"
    exit 1
fi

compose_cmd up -d 2>&1 | while IFS= read -r line; do log "    $line"; done

log ""
log "[OK] Services restarted"

# Done
log ""
log "  ╔══════════════════════════════════════╗"
log "  ║        Update complete!              ║"
log "  ╚══════════════════════════════════════╝"
log ""
log "  Updated: v$CURRENT_VERSION → v$NEW_VERSION"
log ""

write_status "completed" "done"
