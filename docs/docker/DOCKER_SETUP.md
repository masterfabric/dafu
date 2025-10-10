# 🐳 DAFU - Docker Setup Guide

⚠️ **STATUS: Infrastructure Prepared - Services Not Active Yet**

This guide documents the Docker infrastructure prepared for DAFU. **All services are currently commented out** in docker-compose.yml until ML model integration with the API is complete.

**What Works Now:**
- ML Models (Isolation Forest, LSTM/GRU) via direct Python execution
- Model training, prediction, and persistence
- All fraud detection capabilities work without Docker

**Docker Status:**
- ✅ Configuration files ready
- ✅ Database schemas prepared
- ✅ Service definitions complete
- ⚠️ Services commented out until API-ML integration

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Services Overview](#-services-overview)
- [Usage](#-usage)
- [Monitoring](#-monitoring)
- [Troubleshooting](#-troubleshooting)
- [Production Deployment](#-production-deployment)

---

## 🚀 Quick Start

⚠️ **Docker services are not active yet.** Use local Python execution instead:

### Current Way to Use DAFU:

```bash
# 1. Clone the repository
git clone https://github.com/MasterFabric/dafu.git
cd dafu/fraud_detection

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run ML models
cd src/models
python main.py  # Interactive model selection
```

### Future Docker Setup (When Ready):

```bash
# Uncomment services in docker-compose.yml first
docker-compose up -d
```

**Current Status:** Infrastructure ready, integration pending 🔄

---

## 📦 Prerequisites

### Required Software

- **Docker**: Version 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose**: Version 2.0+ ([Install Compose](https://docs.docker.com/compose/install/))
- **Git**: For cloning the repository

### System Requirements

**Minimum:**
- 4 GB RAM
- 2 CPU cores
- 10 GB free disk space

**Recommended:**
- 8 GB RAM
- 4 CPU cores
- 20 GB free disk space

**Production:**
- 16+ GB RAM
- 8+ CPU cores
- 50+ GB free disk space
- SSD storage for databases

### Verify Installation

```bash
# Check Docker version
docker --version
# Expected: Docker version 20.10.0 or higher

# Check Docker Compose version
docker-compose --version
# Expected: Docker Compose version 2.0.0 or higher

# Test Docker
docker run hello-world
```

---

## 📥 Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/MasterFabric/dafu.git
cd dafu
```

### Step 2: Create Environment File

```bash
# Copy example environment file
cp .env.example .env

# Edit configuration (optional)
nano .env
```

**Important:** Update the following values in `.env` for production:
- `SECRET_KEY` - Change to a secure random string
- `POSTGRES_PASSWORD` - Use a strong password
- `RABBITMQ_PASSWORD` - Use a strong password
- `GRAFANA_PASSWORD` - Change default password
- All other default passwords

### Step 3: Build and Start Services

```bash
# Build and start all services
docker-compose up -d

# Expected output:
# Creating network "dafu-network" ... done
# Creating volume "dafu-postgres-data" ... done
# Creating volume "dafu-redis-data" ... done
# Creating dafu-postgres ... done
# Creating dafu-redis ... done
# Creating dafu-rabbitmq ... done
# Creating dafu-fraud-api ... done
# Creating dafu-celery-worker ... done
# Creating dafu-prometheus ... done
# Creating dafu-grafana ... done
```

### Step 4: Verify Services

```bash
# Check service status
docker-compose ps

# Expected output:
# NAME                    STATUS              PORTS
# dafu-fraud-api          Up (healthy)        0.0.0.0:8000->8000/tcp
# dafu-postgres           Up (healthy)        0.0.0.0:5432->5432/tcp
# dafu-redis              Up (healthy)        0.0.0.0:6379->6379/tcp
# dafu-rabbitmq           Up                  0.0.0.0:5672->5672/tcp, 0.0.0.0:15672->15672/tcp
# dafu-celery-worker      Up                  
# dafu-prometheus         Up                  0.0.0.0:9090->9090/tcp
# dafu-grafana            Up                  0.0.0.0:3000->3000/tcp
```

### Step 5: Access Services

Open your browser and navigate to:

- **API Documentation**: http://localhost:8000/docs
- **Grafana Dashboards**: http://localhost:3000 (admin/admin)
- **Prometheus Metrics**: http://localhost:9090
- **RabbitMQ Management**: http://localhost:15672 (dafu/dafu_rabbitmq_password)

---

## ⚙️ Configuration

### Environment Variables

The `.env` file contains all configuration options:

#### Application Settings
```bash
FRAUD_DETECTION_ENV=development  # development | staging | production
LOG_LEVEL=INFO                   # DEBUG | INFO | WARNING | ERROR
API_WORKERS=4                    # Number of API workers
```

#### Database Configuration
```bash
POSTGRES_USER=dafu
POSTGRES_PASSWORD=dafu_secure_password  # CHANGE IN PRODUCTION!
POSTGRES_DB=dafu
POSTGRES_PORT=5432
```

#### Cache Configuration
```bash
REDIS_PORT=6379
REDIS_PASSWORD=                  # Leave empty for no password
```

#### Message Broker Configuration
```bash
RABBITMQ_USER=dafu
RABBITMQ_PASSWORD=dafu_rabbitmq_password  # CHANGE IN PRODUCTION!
RABBITMQ_PORT=5672
RABBITMQ_MANAGEMENT_PORT=15672
```

#### Monitoring Configuration
```bash
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin           # CHANGE IN PRODUCTION!
```

### Custom Configuration

To modify service configuration:

1. **API Configuration**: Edit `fraud_detection/src/api/main.py`
2. **Database Schema**: Edit `fraud_detection/deployment/init-db.sql`
3. **Prometheus**: Edit `fraud_detection/deployment/prometheus.yml`
4. **Grafana**: Edit `fraud_detection/deployment/grafana-datasources.yml`

After changes, rebuild and restart:

```bash
docker-compose down
docker-compose up -d --build
```

---

## 🏗️ Services Overview

### 1. Fraud Detection API (`fraud-detection-api`)

**Main application service providing fraud detection capabilities.**

- **Port**: 8000
- **Technology**: FastAPI, Python 3.9
- **Features**:
  - Real-time fraud scoring
  - Batch processing
  - Model management
  - RESTful API with OpenAPI documentation

**Endpoints**:
- `GET /` - Service information
- `GET /health` - Health check
- `POST /api/v1/score` - Real-time fraud scoring
- `POST /api/v1/batch/analyze` - Batch analysis
- `GET /api/v1/models` - List models
- `GET /docs` - Interactive API documentation

### 2. PostgreSQL Database (`postgres`)

**Persistent data storage.**

- **Port**: 5432
- **Version**: PostgreSQL 15 Alpine
- **Database**: dafu
- **Features**:
  - Transaction storage
  - User and merchant data
  - Model metadata
  - Fraud predictions history

### 3. Redis Cache (`redis`)

**In-memory data store and cache.**

- **Port**: 6379
- **Version**: Redis 7 Alpine
- **Features**:
  - Prediction caching
  - Session storage
  - Rate limiting
  - Real-time data

### 4. RabbitMQ Message Broker (`rabbitmq`)

**Message queue for asynchronous processing.**

- **Ports**: 5672 (AMQP), 15672 (Management UI)
- **Version**: RabbitMQ 3.12 Management Alpine
- **Features**:
  - Task queue for Celery workers
  - Event-driven architecture
  - Reliable message delivery

### 5. Celery Worker (`celery-worker`)

**Background task processor.**

- **Technology**: Celery with Python
- **Features**:
  - Batch processing jobs
  - Model training tasks
  - Scheduled jobs
  - Report generation

### 6. Prometheus (`prometheus`)

**Metrics collection and monitoring.**

- **Port**: 9090
- **Features**:
  - Application metrics
  - Service health monitoring
  - Custom metrics
  - Alerting rules

### 7. Grafana (`grafana`)

**Metrics visualization and dashboards.**

- **Port**: 3000
- **Default Login**: admin / admin
- **Features**:
  - Real-time dashboards
  - Custom visualizations
  - Alerting
  - Data source integration

---

## 💻 Usage

### Basic Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f fraud-detection-api

# Restart a service
docker-compose restart fraud-detection-api

# Rebuild and restart
docker-compose up -d --build

# Remove all containers and volumes
docker-compose down -v
```

### Service Management

#### Start/Stop Individual Services

```bash
# Start only API and dependencies
docker-compose up -d postgres redis rabbitmq fraud-detection-api

# Stop Grafana
docker-compose stop grafana

# Restart Redis
docker-compose restart redis
```

#### Scale Services

```bash
# Scale API to 3 instances
docker-compose up -d --scale fraud-detection-api=3

# Scale Celery workers to 5 instances
docker-compose up -d --scale celery-worker=5
```

### Optional Management Tools

Start additional management tools:

```bash
# Start PgAdmin and Redis Commander
docker-compose --profile tools up -d

# Access PgAdmin: http://localhost:5050
# Access Redis Commander: http://localhost:8081
```

### Making API Requests

#### Health Check

```bash
curl http://localhost:8000/health
```

#### Fraud Scoring

```bash
curl -X POST http://localhost:8000/api/v1/score \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "tx_123",
    "amount": 150.00,
    "user_id": "user_456",
    "merchant_id": "merchant_789",
    "timestamp": "2024-01-15T10:30:00Z",
    "device_fingerprint": "fp_abc123",
    "ip_address": "192.168.1.1"
  }'
```

#### List Models

```bash
curl http://localhost:8000/api/v1/models
```

---

## 📊 Monitoring

### Access Monitoring Tools

1. **Grafana Dashboards**
   ```bash
   open http://localhost:3000
   # Login: admin / admin
   ```

2. **Prometheus Metrics**
   ```bash
   open http://localhost:9090
   ```

3. **RabbitMQ Management**
   ```bash
   open http://localhost:15672
   # Login: dafu / dafu_rabbitmq_password
   ```

### View Logs

```bash
# All services
docker-compose logs -f

# API only
docker-compose logs -f fraud-detection-api

# Last 100 lines
docker-compose logs --tail=100 fraud-detection-api

# Follow logs from specific time
docker-compose logs --since="2024-01-15T10:00:00" fraud-detection-api
```

### Check Service Health

```bash
# API health
curl http://localhost:8000/health

# Database connection
docker-compose exec postgres pg_isready -U dafu

# Redis connection
docker-compose exec redis redis-cli ping
```

### Monitor Resource Usage

```bash
# View resource usage
docker stats

# Service-specific stats
docker stats dafu-fraud-api
```

---

## 🔧 Troubleshooting

### Common Issues

#### Issue 1: Port Already in Use

**Error:**
```
Error starting userland proxy: listen tcp 0.0.0.0:8000: bind: address already in use
```

**Solution:**
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in .env
echo "API_PORT=8001" >> .env
docker-compose up -d
```

#### Issue 2: Database Connection Failed

**Error:**
```
could not connect to server: Connection refused
```

**Solution:**
```bash
# Check database status
docker-compose ps postgres

# Restart database
docker-compose restart postgres

# Check logs
docker-compose logs postgres

# Verify database is initialized
docker-compose exec postgres psql -U dafu -d dafu -c "\dt"
```

#### Issue 3: Out of Memory

**Error:**
```
Cannot allocate memory
```

**Solution:**
```bash
# Increase Docker memory in Docker Desktop settings
# Or reduce workers in .env
echo "API_WORKERS=2" >> .env
echo "MAX_WORKERS=2" >> .env
docker-compose up -d --build
```

#### Issue 4: Permission Denied

**Error:**
```
Permission denied: '/app/models'
```

**Solution:**
```bash
# Fix permissions
chmod -R 755 fraud_detection/models
chmod -R 755 fraud_detection/results

# Restart services
docker-compose restart
```

#### Issue 5: Container Won't Start

**Solution:**
```bash
# View detailed logs
docker-compose logs fraud-detection-api

# Rebuild container
docker-compose build --no-cache fraud-detection-api
docker-compose up -d

# Remove and recreate
docker-compose down
docker-compose up -d
```

### Clean Reset

If all else fails, perform a clean reset:

```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: deletes all data!)
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Clean Docker system
docker system prune -a --volumes

# Rebuild from scratch
docker-compose up -d --build
```

### Getting Help

```bash
# Check service status
docker-compose ps

# View service logs
docker-compose logs

# Enter container shell
docker-compose exec fraud-detection-api bash

# Check environment variables
docker-compose exec fraud-detection-api env
```

---

## 🚀 Production Deployment

### Pre-Production Checklist

- [ ] Update all passwords in `.env`
- [ ] Set `FRAUD_DETECTION_ENV=production`
- [ ] Enable API key authentication
- [ ] Configure SSL/TLS certificates
- [ ] Set up backup strategy
- [ ] Configure monitoring alerts
- [ ] Review security settings
- [ ] Test disaster recovery
- [ ] Document runbooks

### Production Configuration

```bash
# .env production settings
FRAUD_DETECTION_ENV=production
LOG_LEVEL=WARNING
DEBUG=false
API_KEY_ENABLED=true
ENABLE_RATE_LIMITING=true

# Strong passwords
SECRET_KEY=<generate-32-char-random-string>
POSTGRES_PASSWORD=<strong-password>
RABBITMQ_PASSWORD=<strong-password>
REDIS_PASSWORD=<strong-password>
```

### Security Hardening

1. **Enable TLS/SSL**
   ```bash
   # Use reverse proxy (nginx/traefik) with SSL
   # Configure HTTPS in docker-compose.yml
   ```

2. **Restrict Network Access**
   ```bash
   # Remove port exposures for internal services
   # Use firewall rules
   ```

3. **Enable Authentication**
   ```bash
   # Set API_KEY_ENABLED=true
   # Configure OAuth2/JWT
   ```

4. **Regular Updates**
   ```bash
   # Update base images
   docker-compose pull
   docker-compose up -d
   ```

### Backup Strategy

```bash
# Backup PostgreSQL
docker-compose exec postgres pg_dump -U dafu dafu > backup.sql

# Backup Redis
docker-compose exec redis redis-cli SAVE

# Backup models
tar -czf models-backup.tar.gz fraud_detection/models/

# Restore PostgreSQL
docker-compose exec -T postgres psql -U dafu dafu < backup.sql
```

### Monitoring and Alerts

Configure alerts in Prometheus:

```yaml
# Example alert rule
groups:
  - name: fraud_detection
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        annotations:
          summary: High error rate detected
```

### Horizontal Scaling

```bash
# Scale API instances
docker-compose up -d --scale fraud-detection-api=5

# Scale Celery workers
docker-compose up -d --scale celery-worker=10

# Use load balancer (nginx, traefik)
```

---

## 📝 Additional Resources

### Documentation Links

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Docker Documentation](https://docs.docker.com)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)

### Project Links

- **GitHub Repository**: https://github.com/MasterFabric/dafu
- **Issue Tracker**: https://github.com/MasterFabric/dafu/issues
- **Main README**: [README.md](README.md)

### Support

- **Email**: dafu@masterfabric.co
- **Issues**: GitHub Issues
- **License**: AGPL-3.0

---

## 🎉 Success!

Your DAFU Enterprise Fraud Detection Platform is now running with Docker!

**Next Steps:**

1. Explore API documentation: http://localhost:8000/docs
2. View Grafana dashboards: http://localhost:3000
3. Test fraud detection with sample data
4. Customize models and configuration
5. Deploy to production

**Happy Fraud Detecting! 🚀**

---

*DAFU - Enterprise Fraud Detection & E-commerce Analytics Platform*  
*Built with ❤️ by MasterFabric*
