#!/bin/bash

# ============================================================================
# DAFU CLI - Easy Login Script
# ============================================================================
# This script helps you login to DAFU CLI quickly
# ============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'
BOLD='\033[1m'

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Banner
echo -e "${BLUE}${BOLD}"
cat << "EOF"
╔════════════════════════════════════════════════════════════╗
║  ____    _    _____ _   _      ____ _     ___              ║
║ |  _ \  / \  |  ___| | | |    / ___| |   |_ _|             ║
║ | | | |/ _ \ | |_  | | | |   | |   | |    | |              ║
║ | |_| / ___ \|  _| | |_| |   | |___| |___ | |              ║
║ |____/_/   \_\_|    \___/     \____|_____|___|             ║
║                                                            ║
║ DAFU CLI Login                                             ║
╚════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Check if API is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${RED}✗ Error: API is not running!${NC}"
    echo -e "${YELLOW}Please start the API first:${NC}"
    echo -e "  ${CYAN}PYTHONPATH=\$(pwd)/src uvicorn api.main:app --host 0.0.0.0 --port 8000 &${NC}"
    exit 1
fi

echo -e "${GREEN}✓ API is running${NC}"
echo ""

# Get credentials
echo -e "${CYAN}Please enter your credentials:${NC}"
read -p "Username: " USERNAME
read -sp "Password: " PASSWORD
echo ""
echo ""

# Login and get token
echo -e "${CYAN}Logging in...${NC}"
RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\"}")

# Extract token
TOKEN=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access_token', ''))" 2>/dev/null)

# Check if login successful
if [ -z "$TOKEN" ]; then
    echo -e "${RED}✗ Login failed!${NC}"
    ERROR=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('detail', 'Unknown error'))" 2>/dev/null)
    echo -e "${YELLOW}Error: $ERROR${NC}"
    echo ""
    echo -e "${CYAN}If you don't have an account, register first:${NC}"
    echo -e "  ${GREEN}curl -X POST \"http://localhost:8000/api/v1/auth/register\" \\${NC}"
    echo -e "  ${GREEN}  -H \"Content-Type: application/json\" \\${NC}"
    echo -e "  ${GREEN}  -d '{${NC}"
    echo -e "  ${GREEN}    \"username\": \"$USERNAME\",${NC}"
    echo -e "  ${GREEN}    \"email\": \"your@email.com\",${NC}"
    echo -e "  ${GREEN}    \"password\": \"yourpassword\"${NC}"
    echo -e "  ${GREEN}  }'${NC}"
    exit 1
fi

# Get token expiry
EXPIRES_IN=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('expires_in', 86400))" 2>/dev/null)
EXPIRES_HOURS=$((EXPIRES_IN / 3600))

# Create session file
SESSION_FILE="$HOME/.dafu_session"
echo "{
  \"token\": \"$TOKEN\",
  \"username\": \"$USERNAME\",
  \"expires_at\": 9999999999,
  \"saved_at\": \"$(date -u +%Y-%m-%dT%H:%M:%S)\"
}" > "$SESSION_FILE"

# Set proper permissions
chmod 600 "$SESSION_FILE"

echo -e "${GREEN}${BOLD}✓ Login successful!${NC}"
echo ""
echo -e "${CYAN}User:${NC}        ${GREEN}$USERNAME${NC}"
echo -e "${CYAN}Token expires:${NC} ${YELLOW}$EXPIRES_HOURS hours${NC}"
echo -e "${CYAN}Session file:${NC}  ${GREEN}$SESSION_FILE${NC}"
echo ""
echo -e "${BLUE}${BOLD}You can now use CLI commands:${NC}"
echo -e "  ${GREEN}python -m src.api.cli auth whoami${NC}"
echo -e "  ${GREEN}python -m src.api.cli logs list${NC}"
echo -e "  ${GREEN}python -m src.api.cli reports list${NC}"
echo -e "  ${GREEN}python -m src.api.cli products list${NC}"
echo ""
echo -e "${CYAN}To logout:${NC}"
echo -e "  ${GREEN}python -m src.api.cli auth logout${NC}"
echo ""
echo -e "${GREEN}${BOLD}Happy coding! 🚀${NC}"

