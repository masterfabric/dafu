# ============================================================================
# DAFU - Data Analytics Functional Utilities
# Makefile for Common Operations
# ============================================================================

.PHONY: help start stop restart logs status clean rebuild test

# Default target
.DEFAULT_GOAL := help

# Colors
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

##@ General

help: ## Display this help message
	@echo "$(BLUE)"
	@echo "============================================================"
	@echo "  DAFU - Data Analytics Functional Utilities"
	@echo "  Available Commands"
	@echo "============================================================"
	@echo "$(NC)"
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make $(GREEN)<target>$(NC)\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BLUE)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Docker Operations

start: ## Start all services with docker-compose
	@echo "$(BLUE)Starting DAFU platform...$(NC)"
	@chmod +x start.sh
	@./start.sh up

start-cli: ## Start CLI tool interactively
	@echo "$(BLUE)Starting DAFU CLI Tool...$(NC)"
	@docker-compose --profile cli up -d
	@echo "$(GREEN)✓ CLI started. Connect with: docker exec -it dafu-cli dafu fraud-detection$(NC)"

start-api: ## Start API server
	@echo "$(BLUE)Starting DAFU API Server...$(NC)"
	@docker-compose --profile api up -d
	@echo "$(GREEN)✓ API started at http://localhost:8000$(NC)"

start-all: ## Start all services (CLI, API, Monitoring)
	@echo "$(BLUE)Starting full DAFU stack...$(NC)"
	@docker-compose --profile cli --profile api --profile monitoring up -d
	@echo "$(GREEN)✓ All services started$(NC)"

start-tools: ## Start all services including management tools
	@echo "$(BLUE)Starting DAFU platform with tools...$(NC)"
	@chmod +x start.sh
	@./start.sh up tools

stop: ## Stop all services
	@echo "$(YELLOW)Stopping all services...$(NC)"
	@docker-compose down
	@echo "$(GREEN)✓ Services stopped$(NC)"

restart: ## Restart all services
	@echo "$(BLUE)Restarting all services...$(NC)"
	@docker-compose restart
	@echo "$(GREEN)✓ Services restarted$(NC)"

rebuild: ## Rebuild and restart all services
	@echo "$(BLUE)Rebuilding services...$(NC)"
	@docker-compose down
	@docker-compose up -d --build
	@echo "$(GREEN)✓ Services rebuilt$(NC)"

clean: ## Remove all containers and volumes (DESTRUCTIVE)
	@echo "$(YELLOW)Warning: This will remove all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		echo "$(GREEN)✓ Cleaned$(NC)"; \
	fi

##@ Monitoring & Logs

logs: ## View logs from all services
	@docker-compose logs -f

logs-api: ## View API logs only
	@docker-compose logs -f fraud-detection-api

logs-db: ## View database logs only
	@docker-compose logs -f postgres

logs-celery: ## View Celery worker logs only
	@docker-compose logs -f celery-worker

status: ## Show status of all services
	@docker-compose ps

health: ## Check health of all services
	@echo "$(BLUE)Checking service health...$(NC)"
	@curl -s http://localhost:8000/health | python3 -m json.tool || echo "$(YELLOW)API not responding$(NC)"

##@ Development

shell-cli: ## Open interactive DAFU CLI
	@docker exec -it dafu-cli dafu fraud-detection

shell-api: ## Open shell in API container
	@docker-compose exec fraud-detection-api bash

shell-db: ## Open PostgreSQL shell
	@docker-compose exec postgres psql -U dafu -d dafu

shell-redis: ## Open Redis CLI
	@docker-compose exec redis redis-cli

cli-connect: ## Connect to running CLI container
	@docker exec -it dafu-cli bash

dafu: ## Run DAFU CLI command (usage: make dafu CMD="fraud-detection")
	@docker exec -it dafu-cli dafu $(CMD)

test: ## Run tests in API container
	@docker-compose exec fraud-detection-api pytest tests/ -v

lint: ## Run linting in API container
	@docker-compose exec fraud-detection-api black src/ tests/
	@docker-compose exec fraud-detection-api flake8 src/ tests/

##@ Database

db-migrate: ## Run database migrations
	@docker-compose exec fraud-detection-api alembic upgrade head

db-backup: ## Backup PostgreSQL database
	@echo "$(BLUE)Backing up database...$(NC)"
	@mkdir -p backups
	@docker-compose exec -T postgres pg_dump -U dafu dafu > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✓ Database backed up to backups/$(NC)"

db-restore: ## Restore PostgreSQL database (provide BACKUP=filename)
	@echo "$(YELLOW)Restoring database from $(BACKUP)...$(NC)"
	@docker-compose exec -T postgres psql -U dafu dafu < $(BACKUP)
	@echo "$(GREEN)✓ Database restored$(NC)"

##@ Setup

setup: ## Initial setup - create .env (Docker services commented out)
	@echo "$(YELLOW)============================================================$(NC)"
	@echo "$(YELLOW)  ⚠️  Docker Services Are Currently Commented Out$(NC)"
	@echo "$(YELLOW)============================================================$(NC)"
	@echo ""
	@echo "$(RED)All services in docker-compose.yml are commented out.$(NC)"
	@echo ""
	@echo "$(GREEN)To use DAFU ML models NOW:$(NC)"
	@echo "  cd fraud_detection"
	@echo "  python3 -m venv venv"
	@echo "  source venv/bin/activate"
	@echo "  pip install -r requirements.txt"
	@echo "  cd src/models"
	@echo "  python main.py"
	@echo ""
	@echo "$(YELLOW)Docker services will be activated after API-ML integration.$(NC)"
	@echo "See DOCKER_STATUS.md for details."
	@echo ""

##@ Monitoring

open-api: ## Open API documentation in browser
	@open http://localhost:8000/docs || xdg-open http://localhost:8000/docs || echo "Open http://localhost:8000/docs"

open-grafana: ## Open Grafana in browser
	@open http://localhost:3000 || xdg-open http://localhost:3000 || echo "Open http://localhost:3000"

open-prometheus: ## Open Prometheus in browser
	@open http://localhost:9090 || xdg-open http://localhost:9090 || echo "Open http://localhost:9090"

open-rabbitmq: ## Open RabbitMQ management in browser
	@open http://localhost:15672 || xdg-open http://localhost:15672 || echo "Open http://localhost:15672"

##@ Documentation

docs: ## Display quick reference
	@echo "$(BLUE)"
	@echo "============================================================"
	@echo "  DAFU Quick Reference"
	@echo "============================================================"
	@echo "$(NC)"
	@echo "$(GREEN)🚀 Quick Start with CLI:$(NC)"
	@echo "  make start-cli              # Start CLI tool"
	@echo "  make shell-cli              # Run fraud detection"
	@echo "  make start-api              # Start API server"
	@echo "  make start-all              # Start everything"
	@echo ""
	@echo "$(GREEN)📊 Available Commands:$(NC)"
	@echo "  dafu fraud-detection        # Interactive fraud detection"
	@echo "  dafu models                 # List available models"
	@echo "  dafu api                    # Start API server"
	@echo "  dafu info                   # Platform information"
	@echo ""
	@echo "$(BLUE)🌐 Service URLs:$(NC)"
	@echo "  API Documentation:    http://localhost:8000/docs"
	@echo "  Grafana:              http://localhost:3000"
	@echo "  Prometheus:           http://localhost:9090"
	@echo "  RabbitMQ:             http://localhost:15672"
	@echo ""
	@echo "For full CLI help: cat CLI_USAGE.md"
	@echo "For Docker setup: cat DOCKER_SETUP.md"

version: ## Display version information
	@echo "DAFU Platform v1.0.0"
	@echo "Docker version:"
	@docker --version
	@echo "Docker Compose version:"
	@docker-compose --version
