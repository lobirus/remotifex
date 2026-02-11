#!/bin/bash
set -e

# Remotifex Install Script
# Usage: curl -fsSL https://get.remotifex.com | sh
# Flags: -y / --yes  Auto-accept all prompts

REMOTIFEX_DIR="${REMOTIFEX_DIR:-/opt/remotifex}"
REPO_URL="https://github.com/remotifex/remotifex.git"
AUTO_YES=false

# Parse flags
for arg in "$@"; do
    case "$arg" in
        -y|--yes) AUTO_YES=true ;;
    esac
done

# Prompt user for confirmation. Auto-accepts if -y flag is set.
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

echo ""
echo "  ╔═══════════════════════════════════════╗"
echo "  ║         Remotifex Installer           ║"
echo "  ║   Comfortable Remote AI Development   ║"
echo "  ╚═══════════════════════════════════════╝"
echo ""

# Detect package manager
detect_pkg_manager() {
    if command -v apt-get &> /dev/null; then
        echo "apt"
    elif command -v dnf &> /dev/null; then
        echo "dnf"
    elif command -v yum &> /dev/null; then
        echo "yum"
    else
        echo ""
    fi
}

# Install Docker via official convenience script
install_docker() {
    echo "[..] Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable --now docker 2>/dev/null || true
    echo "[OK] Docker installed"
}

# Install Git
install_git() {
    local pkg_mgr
    pkg_mgr=$(detect_pkg_manager)
    echo "[..] Installing Git..."
    case "$pkg_mgr" in
        apt) apt-get update -qq && apt-get install -y -qq git ;;
        dnf) dnf install -y -q git ;;
        yum) yum install -y -q git ;;
        *) echo "[!!] Cannot auto-install git — no supported package manager found"; return 1 ;;
    esac
    echo "[OK] Git installed"
}

# Check for required tools and offer to install missing ones
check_requirements() {
    local missing=()

    if ! command -v docker &> /dev/null; then
        missing+=("docker")
    fi

    if ! command -v docker compose &> /dev/null && ! command -v docker-compose &> /dev/null; then
        # Docker Compose v2 is bundled with Docker — only flag if docker itself is missing
        if command -v docker &> /dev/null; then
            missing+=("docker-compose")
        fi
    fi

    if ! command -v git &> /dev/null; then
        missing+=("git")
    fi

    if [ ${#missing[@]} -eq 0 ]; then
        echo "[OK] All requirements met"
        return
    fi

    echo "[!!] Missing required tools: ${missing[*]}"
    echo ""

    for tool in "${missing[@]}"; do
        case "$tool" in
            docker|docker-compose)
                if confirm "    Install Docker (includes Compose)?"; then
                    install_docker
                else
                    echo "[!!] Docker is required. Install it manually:"
                    echo "      https://docs.docker.com/engine/install/"
                    exit 1
                fi
                ;;
            git)
                if confirm "    Install Git?"; then
                    install_git
                else
                    echo "[!!] Git is required. Install it manually:"
                    echo "      sudo apt-get install git"
                    exit 1
                fi
                ;;
        esac
    done

    echo "[OK] All requirements met"
}

# Generate random secret
generate_secret() {
    openssl rand -base64 32 2>/dev/null || head -c 32 /dev/urandom | base64
}

# Detect public IP
detect_ip() {
    # Try external service
    local ip
    ip=$(curl -s --max-time 5 https://api.ipify.org 2>/dev/null) && echo "$ip" && return
    # Fallback: hostname -based
    ip=$(hostname -I 2>/dev/null | awk '{print $1}') && [ -n "$ip" ] && echo "$ip" && return
    echo "localhost"
}

# Check and configure firewall
check_firewall() {
    # Detect active firewall
    if command -v ufw &> /dev/null && ufw status 2>/dev/null | grep -q "active"; then
        echo "[..] Detected active UFW firewall"
        local needs_config=false

        if ! ufw status | grep -qE "80/(tcp|ALLOW)"; then
            needs_config=true
        fi
        if ! ufw status | grep -qE "443/(tcp|ALLOW)"; then
            needs_config=true
        fi

        if [ "$needs_config" = true ]; then
            echo "[!!] Ports 80 and/or 443 are not open"
            if confirm "    Open ports 80 (HTTP) and 443 (HTTPS) in UFW?"; then
                ufw allow 80/tcp
                ufw allow 443/tcp
                echo "[OK] Firewall configured"
            else
                echo "[!!] Warning: Remotifex may not be reachable without ports 80/443 open"
            fi
        else
            echo "[OK] Firewall already allows ports 80 and 443"
        fi

    elif command -v firewall-cmd &> /dev/null && systemctl is-active --quiet firewalld 2>/dev/null; then
        echo "[..] Detected active firewalld"
        local needs_config=false

        if ! firewall-cmd --list-services --quiet 2>/dev/null | grep -q "http"; then
            needs_config=true
        fi
        if ! firewall-cmd --list-services --quiet 2>/dev/null | grep -q "https"; then
            needs_config=true
        fi

        if [ "$needs_config" = true ]; then
            echo "[!!] HTTP and/or HTTPS services are not enabled"
            if confirm "    Enable HTTP and HTTPS in firewalld?"; then
                firewall-cmd --permanent --add-service=http
                firewall-cmd --permanent --add-service=https
                firewall-cmd --reload
                echo "[OK] Firewall configured"
            else
                echo "[!!] Warning: Remotifex may not be reachable without HTTP/HTTPS enabled"
            fi
        else
            echo "[OK] Firewall already allows HTTP and HTTPS"
        fi

    elif command -v iptables &> /dev/null && iptables -L INPUT -n 2>/dev/null | grep -q "DROP\|REJECT"; then
        echo "[..] Detected iptables with restrictive policy"
        echo "[!!] Ports 80 and 443 may be blocked"
        if confirm "    Add iptables rules for ports 80 (HTTP) and 443 (HTTPS)?"; then
            iptables -I INPUT -p tcp --dport 80 -j ACCEPT
            iptables -I INPUT -p tcp --dport 443 -j ACCEPT
            echo "[OK] Firewall rules added (not persisted — install iptables-persistent to keep them)"
        else
            echo "[!!] Warning: Remotifex may not be reachable without ports 80/443 open"
        fi

    else
        echo "[OK] No active firewall detected"
    fi
}

# Clone or update repository
setup_repo() {
    if [ -d "$REMOTIFEX_DIR" ]; then
        echo "[..] Updating existing installation..."
        cd "$REMOTIFEX_DIR"
        git pull --ff-only
    else
        echo "[..] Cloning Remotifex..."
        git clone "$REPO_URL" "$REMOTIFEX_DIR"
        cd "$REMOTIFEX_DIR"
    fi
    echo "[OK] Repository ready"
}

# Create .env file
setup_env() {
    if [ -f "$REMOTIFEX_DIR/.env" ]; then
        echo "[OK] .env file already exists, keeping it"
        return
    fi

    echo "[..] Creating .env configuration..."

    JWT_SECRET=$(generate_secret)
    ENCRYPTION_KEY=$(generate_secret)

    cat > "$REMOTIFEX_DIR/.env" << EOF
# Remotifex Configuration
# Generated by install script on $(date -u +"%Y-%m-%dT%H:%M:%SZ")
# All settings are managed via the web UI — no need to edit this file.

# Security (auto-generated)
JWT_SECRET=${JWT_SECRET}
ENCRYPTION_KEY=${ENCRYPTION_KEY}

# MongoDB
MONGODB_URL=mongodb://mongo:27017/remotifex

# Redis
REDIS_URL=redis://redis:6379/0

# Data directory
PROJECTS_DATA_DIR=/data/projects
EOF

    chmod 600 "$REMOTIFEX_DIR/.env"
    echo "[OK] .env created with generated secrets"
}

# Build and start services
start_services() {
    echo "[..] Building and starting Remotifex..."
    cd "$REMOTIFEX_DIR"
    docker compose build
    docker compose up -d
    echo "[OK] All services started"
}

# Set up the update watcher service (enables UI-triggered updates)
setup_updater() {
    # Create the update signal directory
    mkdir -p "$REMOTIFEX_DIR/.update"

    # Only install systemd service on systems that have systemd
    if ! command -v systemctl &> /dev/null; then
        echo "[OK] Update directory created (no systemd — UI updates not available)"
        return
    fi

    cat > /etc/systemd/system/remotifex-updater.service << EOF
[Unit]
Description=Remotifex Update Watcher
After=docker.service

[Service]
Type=simple
ExecStart=$REMOTIFEX_DIR/updater-watch.sh
Environment=REMOTIFEX_DIR=$REMOTIFEX_DIR
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable --now remotifex-updater 2>/dev/null || true
    echo "[OK] Update watcher service installed"
}

# Main
echo "Step 1/6: Checking requirements..."
check_requirements

echo ""
echo "Step 2/6: Checking firewall..."
check_firewall

echo ""
echo "Step 3/6: Setting up repository..."
setup_repo

echo ""
echo "Step 4/6: Configuring environment..."
setup_env

echo ""
echo "Step 5/6: Starting services..."
start_services

echo ""
echo "Step 6/6: Setting up update service..."
setup_updater

SERVER_IP=$(detect_ip)

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║       Remotifex is running!          ║"
echo "  ╚══════════════════════════════════════╝"
echo ""
echo "  Open http://${SERVER_IP} in your browser"
echo "  Complete the setup wizard to get started."
echo ""
echo "  Domains, AI keys, and all other settings"
echo "  are configured via the web UI."
echo ""
echo "  To update Remotifex:"
echo "    curl -fsSL https://update.remotifex.com | sh"
echo "    or use the Settings page in the web UI"
echo ""
