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
CYAN='\033[0;36m'
BOLD='\033[1m'
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
echo -e "${CYAN}💡 Tip: Use ${BOLD}./dafu${NC}${CYAN} for interactive CLI mode!${NC}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed (V1 or V2)
DOCKER_COMPOSE_CMD=""
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
    echo -e "${GREEN}✓ Docker Compose V1 detected${NC}"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
    echo -e "${GREEN}✓ Docker Compose V2 detected${NC}"
else
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if curl is installed (needed for health checks)
if ! command -v curl &> /dev/null; then
    echo -e "${YELLOW}Warning: curl is not installed${NC}"
    echo -e "${YELLOW}Health checks will be skipped. Install curl for better service monitoring.${NC}"
    CURL_AVAILABLE=false
else
    CURL_AVAILABLE=true
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

# Function to check if docker-compose.yml has active services
check_active_services() {
    if [ ! -f docker-compose.yml ]; then
        echo -e "${RED}Error: docker-compose.yml not found${NC}"
        exit 1
    fi
    
    # Check if services section has actual services (not just empty {})
    # Look for service definitions under 'services:' that are not commented out
    local active_services=$(grep -E "^[[:space:]]*[a-zA-Z0-9_-]+:" docker-compose.yml | grep -v "^#" | grep -v "services:" | grep -v "networks:" | grep -v "volumes:" | wc -l | tr -d ' ')
    
    # Also check if services is empty {}
    local empty_services=$(grep -E "^services:[[:space:]]*\{\}[[:space:]]*$" docker-compose.yml)
    
    if [ "$active_services" -eq 0 ] || [ -n "$empty_services" ]; then
        echo -e "${RED}Error: No active services found in docker-compose.yml${NC}"
        echo ""
        echo -e "${YELLOW}All services appear to be commented out.${NC}"
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
        echo "See docs/docker/DOCKER_STATUS.md for details."
        exit 1
    fi
    
    echo -e "${GREEN}✓ Found $active_services active service(s)${NC}"
}

# Function to wait for service
wait_for_service() {
    local service=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    # Skip if curl is not available
    if [ "$CURL_AVAILABLE" = false ]; then
        echo -e "${YELLOW}⊘ Skipping health check for $service (curl not available)${NC}"
        return 0
    fi
    
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
    
    echo -e "\n${YELLOW}⚠ $service health check timed out${NC}"
    echo -e "${YELLOW}  Service may still be starting up. Check logs with: ./start.sh logs${NC}"
    return 0
}

# Execute action
case $ACTION in
    up)
        echo "Checking docker-compose.yml..."
        check_active_services
        
        echo ""
        echo "Starting all services..."
        if [ -n "$PROFILE" ]; then
            $DOCKER_COMPOSE_CMD --profile "$PROFILE" up -d
        else
            $DOCKER_COMPOSE_CMD up -d
        fi
        
        echo ""
        echo -e "${BLUE}Waiting for services to be ready...${NC}"
        echo ""
        
        # Wait for API
        wait_for_service "Fraud Detection API" "http://localhost:8000/health"
        
        echo ""
        echo -e "${GREEN}============================================================${NC}"
        echo -e "${GREEN}  ✓ DAFU Platform Started Successfully${NC}"
        echo -e "${GREEN}============================================================${NC}"
        echo ""
        echo -e "${BLUE}Service URLs:${NC}"
        echo "  • API:        http://localhost:8000"
        echo "  • Swagger:    http://localhost:8000/docs"
        echo "  • Grafana:    http://localhost:3000 (admin/admin)"
        echo "  • Prometheus: http://localhost:9090"
        echo ""
        echo -e "${BLUE}Useful Commands:${NC}"
        echo "  • View logs:   ./start.sh logs"
        echo "  • Check status: ./start.sh status"
        echo "  • Stop services: ./start.sh down"
        echo ""
        ;;
        
    down)
        echo "Stopping all services..."
        $DOCKER_COMPOSE_CMD down
        echo -e "${GREEN}✓ All services stopped${NC}"
        ;;
        
    restart)
        echo "Restarting all services..."
        $DOCKER_COMPOSE_CMD restart
        echo -e "${GREEN}✓ All services restarted${NC}"
        ;;
        
    logs)
        $DOCKER_COMPOSE_CMD logs -f
        ;;
        
    status)
        echo "Service Status:"
        $DOCKER_COMPOSE_CMD ps
        ;;
        
    clean)
        echo -e "${YELLOW}Warning: This will remove all containers and volumes${NC}"
        
        # Check if running in non-interactive mode
        if [ -t 0 ]; then
            read -p "Are you sure? (yes/no): " -r
            REPLY_VALUE=$REPLY
        else
            echo "Running in non-interactive mode, skipping confirmation."
            echo "Use 'clean-force' to clean without confirmation."
            exit 1
        fi
        
        if [[ $REPLY_VALUE =~ ^[Yy][Ee][Ss]$ ]]; then
            $DOCKER_COMPOSE_CMD down -v
            echo -e "${GREEN}✓ Cleaned all containers and volumes${NC}"
        else
            echo "Cancelled"
        fi
        ;;
        
    clean-force)
        echo -e "${YELLOW}Force cleaning all containers and volumes...${NC}"
        $DOCKER_COMPOSE_CMD down -v
        echo -e "${GREEN}✓ Cleaned all containers and volumes${NC}"
        ;;
        
    rebuild)
        echo "Rebuilding and restarting services..."
        check_active_services
        $DOCKER_COMPOSE_CMD down
        $DOCKER_COMPOSE_CMD up -d --build
        echo -e "${GREEN}✓ Services rebuilt and started${NC}"
        ;;
        
    *)
        echo "Usage: $0 {up|down|restart|logs|status|clean|clean-force|rebuild} [profile]"
        echo ""
        echo "Commands:"
        echo "  up          - Start all services"
        echo "  down        - Stop all services"
        echo "  restart     - Restart all services"
        echo "  logs        - View logs (follow mode)"
        echo "  status      - Show service status"
        echo "  clean       - Remove all containers and volumes (interactive)"
        echo "  clean-force - Remove all containers and volumes (no confirmation)"
        echo "  rebuild     - Rebuild and restart services"
        echo ""
        echo "Profiles:"
        echo "  tools       - Start with management tools (PgAdmin, Redis Commander)"
        echo ""
        echo "Examples:"
        echo "  $0 up              # Start all services"
        echo "  $0 up tools        # Start with management tools"
        echo "  $0 logs            # View logs"
        echo "  $0 status          # Check service status"
        echo "  $0 clean           # Clean with confirmation"
        echo "  $0 clean-force     # Clean without confirmation (CI/CD)"
        echo "  $0 down            # Stop services"
        exit 1
        ;;
esac
