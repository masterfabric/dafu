#!/bin/bash
# ============================================================================
# DAFU - Data Analytics Functional Utilities
# Docker Entrypoint Script
# ============================================================================
# This script handles container initialization and service startup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print banner
print_banner() {
    echo -e "${BLUE}"
    echo "============================================================"
    echo "  DAFU - Data Analytics Functional Utilities"
    echo "  Fraud Detection & E-commerce Analytics Platform"
    echo "============================================================"
    echo -e "${NC}"
}

# Wait for service to be ready
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local max_attempts=30
    local attempt=0

    echo -e "${YELLOW}⏳ Waiting for ${service_name} at ${host}:${port}...${NC}"
    
    while [ $attempt -lt $max_attempts ]; do
        if nc -z "$host" "$port" 2>/dev/null; then
            echo -e "${GREEN}✓ ${service_name} is ready!${NC}"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    
    echo -e "${RED}✗ ${service_name} failed to start${NC}"
    return 1
}

# Initialize database
init_database() {
    if [ "$DATABASE_URL" ]; then
        echo -e "${YELLOW}📊 Checking database connection...${NC}"
        # Extract host and port from DATABASE_URL
        DB_HOST=$(echo "$DATABASE_URL" | sed -n 's/.*@\([^:]*\):.*/\1/p')
        DB_PORT=$(echo "$DATABASE_URL" | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
        
        if [ "$DB_HOST" ] && [ "$DB_PORT" ]; then
            wait_for_service "$DB_HOST" "$DB_PORT" "PostgreSQL"
        fi
    fi
}

# Initialize Redis
init_redis() {
    if [ "$REDIS_URL" ]; then
        echo -e "${YELLOW}🔴 Checking Redis connection...${NC}"
        REDIS_HOST=$(echo "$REDIS_URL" | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
        REDIS_PORT=$(echo "$REDIS_URL" | sed -n 's/.*:\([0-9]*\).*/\1/p')
        
        if [ "$REDIS_HOST" ] && [ "$REDIS_PORT" ]; then
            wait_for_service "$REDIS_HOST" "$REDIS_PORT" "Redis"
        fi
    fi
}

# Initialize RabbitMQ
init_rabbitmq() {
    if [ "$RABBITMQ_URL" ]; then
        echo -e "${YELLOW}🐰 Checking RabbitMQ connection...${NC}"
        RABBIT_HOST=$(echo "$RABBITMQ_URL" | sed -n 's/.*@\([^:]*\):.*/\1/p')
        RABBIT_PORT=$(echo "$RABBITMQ_URL" | sed -n 's/.*:\([0-9]*\).*/\1/p')
        
        if [ "$RABBIT_HOST" ] && [ "$RABBIT_PORT" ]; then
            wait_for_service "$RABBIT_HOST" "$RABBIT_PORT" "RabbitMQ"
        fi
    fi
}

# Initialize application
init_app() {
    echo -e "${YELLOW}🔧 Initializing application...${NC}"
    
    # Create necessary directories
    mkdir -p "$MODEL_STORAGE_PATH" "$RESULTS_PATH" /app/logs
    
    # Set permissions
    chmod -R 755 /app/fraud_detection/models
    chmod -R 755 /app/fraud_detection/results
    chmod -R 755 /app/fraud_detection/logs
    
    echo -e "${GREEN}✓ Application initialized${NC}"
}

# Main execution
main() {
    print_banner
    
    # Check environment
    echo -e "${BLUE}Environment: ${FRAUD_DETECTION_ENV:-development}${NC}"
    echo -e "${BLUE}Log Level: ${LOG_LEVEL:-INFO}${NC}"
    echo ""
    
    # Initialize services if URLs are provided
    init_database
    init_redis
    init_rabbitmq
    
    # Initialize application
    init_app
    
    echo ""
    echo -e "${GREEN}✓ All services ready!${NC}"
    echo -e "${BLUE}Starting application...${NC}"
    echo ""
    
    # Execute the provided command
    exec "$@"
}

# Run main function
main "$@"

