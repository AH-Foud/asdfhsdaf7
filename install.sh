#!/bin/bash
# =====================================================================
#  Bale Bot + Web Management Panel — Install Script
#  GitHub: https://github.com/AH-Foud/asdfhsdaf7
# =====================================================================
set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'
BOLD='\033[1m'

clear
echo -e "${BLUE}  ╔══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}  ║${NC}     ${CYAN}Bale Bot + Web Management Panel${NC}         ${BLUE}║${NC}"
echo -e "${BLUE}  ║${NC}     ${GREEN}Automated Installation Script${NC}            ${BLUE}║${NC}"
echo -e "${BLUE}  ╚══════════════════════════════════════════════╝${NC}"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[ERROR]${NC} Please run as root: ${YELLOW}sudo bash install.sh${NC}"
    exit 1
fi

APP_DIR="/opt/employer-panel"
APP_USER="www-data"
SERVICE_NAME="employer-panel"

echo -e "${GREEN}[1/6]${NC} Installing system dependencies..."
apt-get update -qq
apt-get install -y -qq python3 python3-full python3-pip python3-venv nginx ufw curl 2>/dev/null

echo -e "${GREEN}[2/6]${NC} Setting up project directory: ${APP_DIR}"
mkdir -p "$APP_DIR/data/voices"
cp -r "$(dirname "$0")"/*.py "$APP_DIR/" 2>/dev/null || true
cp -r "$(dirname "$0")"/*.html "$APP_DIR/" 2>/dev/null || true
cp -r "$(dirname "$0")"/requirements.txt "$APP_DIR/" 2>/dev/null || true
cp -r "$(dirname "$0")/data" "$APP_DIR/" 2>/dev/null || true
chown -R "$APP_USER":"$APP_USER" "$APP_DIR"

echo -e "${GREEN}[3/6]${NC} Creating Python virtual environment..."
cd "$APP_DIR"
python3 -m venv venv
echo -e "       Installing Python requirements in venv..."
"$APP_DIR/venv/bin/pip" install -q -r requirements.txt

echo -e "${GREEN}[4/6]${NC} Creating systemd service: ${SERVICE_NAME}"
cat > "/etc/systemd/system/${SERVICE_NAME}.service" << SERVICE_EOF
[Unit]
Description=Bale Bot + Web Management Panel
After=network.target

[Service]
Type=simple
User=${APP_USER}
WorkingDirectory=${APP_DIR}
ExecStart=${APP_DIR}/venv/bin/python3 ${APP_DIR}/web_server.py
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
ufw allow 5000/tcp 2>/dev/null || true
ufw allow 80/tcp 2>/dev/null || true
ufw allow 443/tcp 2>/dev/null || true
ufw --force enable 2>/dev/null || true

echo -e "${GREEN}[6/6]${NC} Starting service..."
systemctl restart "$SERVICE_NAME"

SERVER_IP=$(curl -s -4 ifconfig.me 2>/dev/null || curl -s -4 ipinfo.io/ip 2>/dev/null || hostname -I | awk '{print $1}')

echo ""
echo -e "${BLUE}  ╔══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}  ║${NC}  ${GREEN}✅ Installation Complete!${NC}                    ${BLUE}║${NC}"
echo -e "${BLUE}  ╚══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${BOLD}🌐 Panel URL:${NC}  ${CYAN}http://${SERVER_IP}:5000${NC}"
echo ""
echo -e "  ${BOLD}⚙️  Setup Bot Token & Admin ID:${NC}"
echo -e "     curl -X POST http://localhost:5000/api/settings \\"
echo -e "       -H 'Content-Type: application/json' \\"
echo -e "       -d '{\"bot_token\": \"YOUR_TOKEN\", \"admin_id\": YOUR_ID}'"
echo -e "     ${YELLOW}sudo systemctl restart ${SERVICE_NAME}${NC}"
echo ""
echo -e "  ${BOLD}📋 Commands:${NC}"
echo -e "     Status:   ${YELLOW}sudo systemctl status ${SERVICE_NAME}${NC}"
echo -e "     Restart:  ${YELLOW}sudo systemctl restart ${SERVICE_NAME}${NC}"
echo -e "     Logs:     ${YELLOW}sudo journalctl -u ${SERVICE_NAME} -f${NC}"
echo ""
echo -e "  ${BOLD}📁 Install:${NC} ${APP_DIR}"
echo -e "  ${BOLD}📁 Settings:${NC} ${APP_DIR}/settings.json"
echo ""