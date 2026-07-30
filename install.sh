#!/bin/bash
# =====================================================================
#  Bale Bot + Web Management Panel — Install Script
#  GitHub: https://github.com/AH-Foud/asdfhsdaf7
# =====================================================================
set -e

# ── Colors ──
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'
BOLD='\033[1m'

# ── Banner ──
clear
echo -e "${BLUE}  ╔══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}  ║${NC}     ${CYAN}Bale Bot + Web Management Panel${NC}         ${BLUE}║${NC}"
echo -e "${BLUE}  ║${NC}     ${GREEN}Automated Installation Script${NC}            ${BLUE}║${NC}"
echo -e "${BLUE}  ╚══════════════════════════════════════════════╝${NC}"
echo ""

# ── Root check ──
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[ERROR]${NC} Please run as root: ${YELLOW}sudo bash install.sh${NC}"
    exit 1
fi

# ── Project directory ──
APP_DIR="/opt/employer-panel"
APP_USER="www-data"
SERVICE_NAME="employer-panel"

echo -e "${GREEN}[1/6]${NC} Installing system dependencies..."
apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv nginx ufw 2>/dev/null

echo -e "${GREEN}[2/6]${NC} Setting up project directory: ${APP_DIR}"
mkdir -p "$APP_DIR/data/voices"
# Copy all project files to APP_DIR
cp -r "$(dirname "$0")"/*.py "$APP_DIR/" 2>/dev/null || true
cp -r "$(dirname "$0")"/requirements.txt "$APP_DIR/" 2>/dev/null || true
cp -r "$(dirname "$0")/data" "$APP_DIR/" 2>/dev/null || true

# Set ownership
chown -R "$APP_USER":"$APP_USER" "$APP_DIR"

echo -e "${GREEN}[3/6]${NC} Installing Python requirements..."
cd "$APP_DIR"
pip3 install --break-system-packages -q -r requirements.txt 2>/dev/null || \
pip3 install -q -r requirements.txt

echo -e "${GREEN}[4/6]${NC} Creating systemd service: ${SERVICE_NAME}"
cat > "/etc/systemd/system/${SERVICE_NAME}.service" << SERVICE_EOF
[Unit]
Description=Bale Bot + Web Management Panel
After=network.target

[Service]
Type=simple
User=${APP_USER}
WorkingDirectory=${APP_DIR}
ExecStart=/usr/bin/python3 ${APP_DIR}/web_server.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE_EOF

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"

echo -e "${GREEN}[5/6]${NC} Configuring firewall..."
# Open port 5000 for direct access
ufw allow 5000/tcp 2>/dev/null || true
ufw allow 80/tcp 2>/dev/null || true
ufw allow 443/tcp 2>/dev/null || true
ufw --force enable 2>/dev/null || true

echo -e "${GREEN}[6/6]${NC} Starting service..."
systemctl restart "$SERVICE_NAME"

# ── Get server IP ──
SERVER_IP=$(curl -s -4 ifconfig.me 2>/dev/null || curl -s -4 ipinfo.io/ip 2>/dev/null || hostname -I | awk '{print $1}')

# ── Final message ──
echo ""
echo -e "${BLUE}  ╔══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}  ║${NC}  ${GREEN}✅ Installation Complete!${NC}                    ${BLUE}║${NC}"
echo -e "${BLUE}  ╚══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${BOLD}🌐 Panel URLs:${NC}"
echo -e "     • ${CYAN}http://${SERVER_IP}:5000${NC}  (direct IP)"
if [ -n "$SERVER_IP" ]; then
    echo -e "     • ${CYAN}http://${SERVER_IP}:5000${NC}  (VPS IP access)"
fi
echo ""
echo -e "  ${BOLD}⚙️  Next Steps:${NC}"
echo -e "     1. Open panel in browser: ${YELLOW}http://${SERVER_IP}:5000${NC}"
echo -e "     2. Go to: ${YELLOW}Settings${NC} page (تنظیمات)"
echo -e "     3. Enter your ${YELLOW}BOT_TOKEN${NC} and ${YELLOW}ADMIN_ID${NC}"
echo -e "     4. Restart: ${YELLOW}sudo systemctl restart ${SERVICE_NAME}${NC}"
echo ""
echo -e "  ${BOLD}📋 Useful Commands:${NC}"
echo -e "     Status:  ${YELLOW}sudo systemctl status ${SERVICE_NAME}${NC}"
echo -e "     Restart: ${YELLOW}sudo systemctl restart ${SERVICE_NAME}${NC}"
echo -e "     Logs:    ${YELLOW}sudo journalctl -u ${SERVICE_NAME} -f${NC}"
echo -e "     Stop:    ${YELLOW}sudo systemctl stop ${SERVICE_NAME}${NC}"
echo ""
echo -e "  ${BOLD}🔗 Domain Setup (Cloudflare):${NC}"
echo -e "     If you have a domain pointed to this server:"
echo -e "     Cloudflare → DNS → A record → ${SERVER_IP}"
echo -e "     Then access: ${CYAN}http://your-domain.com:5000${NC}"
echo ""
echo -e "  ${BOLD}📁 Install location:${NC} ${APP_DIR}"
echo -e "  ${BOLD}📁 Settings file:${NC}    ${APP_DIR}/settings.json"
echo ""
