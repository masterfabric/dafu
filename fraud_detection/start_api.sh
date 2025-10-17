#!/bin/bash

# ============================================================================
# DAFU API - Startup Script
# ============================================================================
# Quick startup script for DAFU API with database initialization
# ============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Banner
echo -e "${BLUE}${BOLD}"
cat << "EOF"
╔════════════════════════════════════════════════════════════╗
║  ____    _    _____ _   _      _    ____ ___              ║
║ |  _ \  / \  |  ___| | | |    / \  |  _ \_ _|             ║
║ | | | |/ _ \ | |_  | | | |   / _ \ | |_) | |              ║
║ | |_| / ___ \|  _| | |_| |  / ___ \|  __/| |              ║
║ |____/_/   \_\_|    \___/  /_/   \_\_|  |___|             ║
║                                                            ║
║ Data Analytics Functional Utilities - API Server          ║
╚════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${CYAN}Starting DAFU API...${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating one...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
    echo ""
fi

# Activate virtual environment
echo -e "${CYAN}Activating virtual environment...${NC}"
source venv/bin/activate

# Install/upgrade dependencies
echo -e "${CYAN}Checking dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Check if PostgreSQL is running
echo -e "${CYAN}Checking database connection...${NC}"
if command -v pg_isready &> /dev/null; then
    if pg_isready -h localhost -U dafu &> /dev/null; then
        echo -e "${GREEN}✓ PostgreSQL is running${NC}"
    else
        echo -e "${YELLOW}⚠ PostgreSQL connection failed${NC}"
        echo -e "${CYAN}Starting PostgreSQL with Docker...${NC}"
        docker run -d \
            --name dafu-postgres \
            -e POSTGRES_USER=dafu \
            -e POSTGRES_PASSWORD=dafu_secure_password \
            -e POSTGRES_DB=dafu \
            -p 5432:5432 \
            postgres:15-alpine
        
        # Wait for PostgreSQL to be ready
        echo -e "${CYAN}Waiting for PostgreSQL to be ready...${NC}"
        sleep 5
        echo -e "${GREEN}✓ PostgreSQL started${NC}"
    fi
else
    echo -e "${YELLOW}⚠ pg_isready not found, skipping PostgreSQL check${NC}"
fi
echo ""

# Initialize database
echo -e "${CYAN}Initializing database...${NC}"
cd "$SCRIPT_DIR"
python -c "from src.api.database import init_db; init_db()" 2>/dev/null || echo -e "${YELLOW}Database already initialized${NC}"
echo -e "${GREEN}✓ Database ready${NC}"
echo ""

# Start API
echo -e "${BLUE}${BOLD}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}Starting DAFU API Server...${NC}"
echo -e "${BLUE}${BOLD}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}API will be available at:${NC}"
echo -e "  ${GREEN}• http://localhost:8000${NC}"
echo -e "  ${GREEN}• http://localhost:8000/docs${NC}    ${YELLOW}(Swagger UI)${NC}"
echo -e "  ${GREEN}• http://localhost:8000/redoc${NC}   ${YELLOW}(ReDoc)${NC}"
echo ""
echo -e "${CYAN}Press ${BOLD}Ctrl+C${NC}${CYAN} to stop the server${NC}"
echo ""
echo -e "${BLUE}${BOLD}════════════════════════════════════════════════════════════${NC}"
echo ""

# Start uvicorn
cd "$SCRIPT_DIR"
export PYTHONPATH="$SCRIPT_DIR/src"
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Cleanup on exit
echo ""
echo -e "${GREEN}API server stopped${NC}"
deactivate 2>/dev/null || true

