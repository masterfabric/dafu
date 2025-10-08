# 🐳 Docker Deployment Overview

DAFU - Data Analytics Functional Utilities - Docker & Docker Compose Setup

## 📚 Documentation Index

1. **[QUICK_START.md](QUICK_START.md)** - Get started in 5 minutes
2. **[DOCKER_SETUP.md](DOCKER_SETUP.md)** - Complete Docker documentation
3. **[README.md](README.md)** - Main project documentation

## 🚀 Quick Start (30 seconds)

```bash
git clone https://github.com/MasterFabric/dafu.git
cd dafu
make setup
```

**That's it!** Access at http://localhost:8000/docs

## 📦 What's Included

### Services
- **Fraud Detection API** (Port 8000) - FastAPI application
- **PostgreSQL** (Port 5432) - Database with schema
- **Redis** (Port 6379) - Cache and session storage
- **RabbitMQ** (Ports 5672, 15672) - Message broker
- **Celery Workers** - Background task processing
- **Prometheus** (Port 9090) - Metrics and monitoring
- **Grafana** (Port 3000) - Dashboards and visualization

### Features
- ✅ Complete microservices architecture
- ✅ Auto-scaling ready
- ✅ Health checks for all services
- ✅ Persistent data volumes
- ✅ Production-ready configuration
- ✅ Monitoring and logging
- ✅ Network isolation
- ✅ Security best practices

## 📋 Files Created

### Core Files
- `docker-compose.yml` - Main orchestration file
- `.env` - Environment configuration
- `.env.example` - Template for environment variables
- `.dockerignore` - Docker build exclusions
- `.gitignore` - Updated with Docker artifacts

### Docker Assets
- `fraud_detection/deployment/Dockerfile` - Multi-stage build
- `fraud_detection/deployment/init-db.sql` - Database schema
- `fraud_detection/deployment/prometheus.yml` - Metrics config
- `fraud_detection/deployment/grafana-datasources.yml` - Grafana config

### API Application
- `fraud_detection/src/api/main.py` - FastAPI application

### Helper Scripts
- `start.sh` - Service management script
- `Makefile` - Common operations

### Documentation
- `QUICK_START.md` - 5-minute guide
- `DOCKER_SETUP.md` - Complete documentation
- `DOCKER_README.md` - This file

## 🎯 Common Commands

### Using Make (Recommended)
```bash
make setup      # Initial setup and start
make start      # Start all services
make stop       # Stop all services
make restart    # Restart services
make logs       # View logs
make status     # Check status
make clean      # Remove all data
```

### Using Start Script
```bash
./start.sh up       # Start services
./start.sh down     # Stop services
./start.sh logs     # View logs
./start.sh status   # Check status
./start.sh rebuild  # Rebuild and restart
```

### Using Docker Compose
```bash
docker-compose up -d           # Start
docker-compose down            # Stop
docker-compose logs -f         # Logs
docker-compose ps              # Status
docker-compose restart         # Restart
docker-compose up -d --build   # Rebuild
```

## 🔍 Service URLs

After starting services:

| Service | URL | Credentials |
|---------|-----|-------------|
| **API Docs** | http://localhost:8000/docs | - |
| **API Health** | http://localhost:8000/health | - |
| **Grafana** | http://localhost:3000 | admin/admin |
| **Prometheus** | http://localhost:9090 | - |
| **RabbitMQ** | http://localhost:15672 | dafu/dafu_rabbitmq_password |

## 🧪 Testing the Setup

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. API Documentation
```bash
open http://localhost:8000/docs
```

### 3. Fraud Detection Test
```bash
curl -X POST http://localhost:8000/api/v1/score \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "tx_123",
    "amount": 150.00,
    "user_id": "user_456",
    "merchant_id": "merchant_789",
    "timestamp": "2024-01-15T10:30:00Z"
  }'
```

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Fraud API    │  │ Celery       │  │ Prometheus   │ │
│  │ (FastAPI)    │  │ Workers      │  │              │ │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘ │
│         │                  │                             │
│  ┌──────┴───────┬──────────┴─────────┬──────────────┐ │
│  │              │                     │              │ │
│  │ PostgreSQL   │    Redis           │  RabbitMQ    │ │
│  │              │                     │              │ │
│  └──────────────┘    └──────────────┘  └────────────┘ │
│                                                          │
│  ┌──────────────┐                                       │
│  │  Grafana     │                                       │
│  │              │                                       │
│  └──────────────┘                                       │
└─────────────────────────────────────────────────────────┘
```

## 🔧 Configuration

### Environment Variables

Edit `.env` file to customize:

```bash
# Application
FRAUD_DETECTION_ENV=development
LOG_LEVEL=INFO
API_WORKERS=4

# Ports
API_PORT=8000
POSTGRES_PORT=5432
REDIS_PORT=6379

# Passwords (CHANGE IN PRODUCTION!)
POSTGRES_PASSWORD=dafu_secure_password
RABBITMQ_PASSWORD=dafu_rabbitmq_password
GRAFANA_PASSWORD=admin
```

### Scaling Services

```bash
# Scale API to 3 instances
docker-compose up -d --scale fraud-detection-api=3

# Scale Celery workers to 5 instances
docker-compose up -d --scale celery-worker=5
```

## 🐛 Troubleshooting

### Port Conflicts
```bash
# Change port in .env
echo "API_PORT=8001" >> .env
docker-compose up -d
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f fraud-detection-api
```

### Clean Restart
```bash
docker-compose down -v
docker-compose up -d
```

### Check Service Health
```bash
docker-compose ps
docker stats
```

## 🔐 Security Notes

### Development vs Production

**Development (Default):**
- Default passwords
- All ports exposed
- Debug logging enabled
- No SSL/TLS

**Production:**
1. Change all passwords in `.env`
2. Set `FRAUD_DETECTION_ENV=production`
3. Enable `API_KEY_ENABLED=true`
4. Use reverse proxy with SSL
5. Restrict network access
6. Enable rate limiting
7. Configure monitoring alerts

### Production Checklist

- [ ] Update all passwords
- [ ] Enable API key authentication
- [ ] Configure SSL/TLS
- [ ] Set up firewall rules
- [ ] Configure backup strategy
- [ ] Enable monitoring alerts
- [ ] Review security settings
- [ ] Document runbooks

## 📖 Further Reading

- **[QUICK_START.md](QUICK_START.md)** - 5-minute quick start
- **[DOCKER_SETUP.md](DOCKER_SETUP.md)** - Complete documentation
- **[README.md](README.md)** - Project overview
- **Docker Docs**: https://docs.docker.com
- **FastAPI Docs**: https://fastapi.tiangolo.com

## 🆘 Getting Help

- **Documentation**: [DOCKER_SETUP.md](DOCKER_SETUP.md)
- **Issues**: https://github.com/MasterFabric/dafu/issues
- **Email**: dafu@masterfabric.co

## 📝 Summary

### What You Get

✅ **Complete Platform** - All services in one command
✅ **Production Ready** - Best practices included
✅ **Easy to Use** - Multiple deployment options
✅ **Well Documented** - Comprehensive guides
✅ **Monitoring** - Prometheus & Grafana included
✅ **Scalable** - Ready for horizontal scaling

### Next Steps

1. **Start**: `make setup`
2. **Explore**: http://localhost:8000/docs
3. **Monitor**: http://localhost:3000
4. **Customize**: Edit `.env`
5. **Deploy**: Follow production checklist

---

**Built with ❤️ by MasterFabric**

*DAFU - Data Analytics Functional Utilities - Enterprise Fraud Detection & E-commerce Analytics Platform*
