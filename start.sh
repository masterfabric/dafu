#!/bin/bash

# ============================================================================
# DAFU - Data Analytics Functional Utilities
# Docker Compose Startup Script
# ============================================================================
# 
# ⚠️  WARNING: Docker services are currently commented out
# 
# All services in docker-compose.yml are commented out until API-ML
# integration is complete. Use direct Python execution for ML models.
# 
# For current usage: cd fraud_detection && python src/models/main.py
# 
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
cat << "EOF"
============================================================
  ____    _    _____ _   _ 
 |  _ \  / \  |  ___| | | |
 | | | |/ _ \ | |_  | | | |
 | |_| / ___ \|  _| | |_| |
 |____/_/   \_\_|    \___/ 
                            
 Data Analytics Functional Utilities
 Docker Compose Setup
============================================================
EOF
echo -e "${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found${NC}"
    echo "Creating .env from .env.example..."
    
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env file${NC}"
        echo -e "${YELLOW}Please review and update .env with your configuration${NC}"
    else
        echo -e "${RED}Error: .env.example not found${NC}"
        echo "Creating minimal .env file..."
        cat > .env << 'ENVEOF'
FRAUD_DETECTION_ENV=development
LOG_LEVEL=INFO
POSTGRES_USER=dafu
POSTGRES_PASSWORD=dafu_secure_password
POSTGRES_DB=dafu
RABBITMQ_USER=dafu
RABBITMQ_PASSWORD=dafu_rabbitmq_password
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin
ENVEOF
        echo -e "${GREEN}✓ Created minimal .env file${NC}"
    fi
fi

# Parse command line arguments
ACTION="${1:-up}"
PROFILE="${2:-}"

echo -e "${BLUE}Starting DAFU Platform...${NC}"
echo ""

# Function to wait for service
wait_for_service() {
    local service=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    echo -ne "${YELLOW}Waiting for $service to be ready${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            echo -e "\n${GREEN}✓ $service is ready${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo -e "\n${RED}✗ $service failed to start${NC}"
    return 1
}

# Execute action
case $ACTION in
    up)
        echo "Starting all services..."
        if [ -n "$PROFILE" ]; then
            docker-compose --profile "$PROFILE" up -d
        else
            docker-compose up -d
        fi
        
        echo ""
        echo -e "${BLUE}Waiting for services to be ready...${NC}"
        echo ""
        
        # Wait for API
        wait_for_service "Fraud Detection API" "http://localhost:8000/health" || true
        
        echo ""
        echo -e "${YELLOW}============================================================${NC}"
        echo -e "${YELLOW}  ⚠️  Docker Services Are Currently Commented Out${NC}"
        echo -e "${YELLOW}============================================================${NC}"
        echo ""
        echo -e "${RED}All services in docker-compose.yml are commented out.${NC}"
        echo ""
        echo -e "${GREEN}To use DAFU ML models NOW:${NC}"
        echo ""
        echo "  cd fraud_detection"
        echo "  python3 -m venv venv"
        echo "  source venv/bin/activate"
        echo "  pip install -r requirements.txt"
        echo "  cd src/models"
        echo "  python main.py"
        echo ""
        echo -e "${YELLOW}To activate Docker services:${NC}"
        echo "  1. Uncomment services in docker-compose.yml"
        echo "  2. Complete API-ML integration"
        echo "  3. Run: ./start.sh up"
        echo ""
        echo "See DOCKER_STATUS.md for details."
        echo ""
        ;;
        
    down)
        echo "Stopping all services..."
        docker-compose down
        echo -e "${GREEN}✓ All services stopped${NC}"
        ;;
        
    restart)
        echo "Restarting all services..."
        docker-compose restart
        echo -e "${GREEN}✓ All services restarted${NC}"
        ;;
        
    logs)
        docker-compose logs -f
        ;;
        
    status)
        echo "Service Status:"
        docker-compose ps
        ;;
        
    clean)
        echo -e "${YELLOW}Warning: This will remove all containers and volumes${NC}"
        read -p "Are you sure? (yes/no): " -r
        if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            docker-compose down -v
            echo -e "${GREEN}✓ Cleaned all containers and volumes${NC}"
        else
            echo "Cancelled"
        fi
        ;;
        
    rebuild)
        echo "Rebuilding and restarting services..."
        docker-compose down
        docker-compose up -d --build
        echo -e "${GREEN}✓ Services rebuilt and started${NC}"
        ;;
        
    *)
        echo "Usage: $0 {up|down|restart|logs|status|clean|rebuild} [profile]"
        echo ""
        echo "Commands:"
        echo "  up       - Start all services"
        echo "  down     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  logs     - View logs (follow mode)"
        echo "  status   - Show service status"
        echo "  clean    - Remove all containers and volumes"
        echo "  rebuild  - Rebuild and restart services"
        echo ""
        echo "Profiles:"
        echo "  tools    - Start with management tools (PgAdmin, Redis Commander)"
        echo ""
        echo "Examples:"
        echo "  $0 up              # Start all services"
        echo "  $0 up tools        # Start with management tools"
        echo "  $0 logs            # View logs"
        echo "  $0 down            # Stop services"
        exit 1
        ;;
esac
