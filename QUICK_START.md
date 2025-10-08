# 🚀 DAFU - Quick Start Guide

Get DAFU - Data Analytics Functional Utilities running in **5 minutes**!

## Prerequisites

- Docker 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Compose 2.0+ ([Install Compose](https://docs.docker.com/compose/install/))
- 8GB RAM (minimum)
- 10GB free disk space

## Quick Start

### Option 1: Using Make (Recommended)

```bash
# Clone and setup
git clone https://github.com/MasterFabric/dafu.git
cd dafu

# Start everything
make setup

# That's it! 🎉
```

### Option 2: Using Start Script

```bash
# Clone repository
git clone https://github.com/MasterFabric/dafu.git
cd dafu

# Create environment file
cp .env.example .env

# Start services
./start.sh up

# Done! 🎉
```

### Option 3: Using Docker Compose Directly

```bash
# Clone repository
git clone https://github.com/MasterFabric/dafu.git
cd dafu

# Create environment file
cp .env.example .env

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

## Verify Installation

Once started, access these URLs:

- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **RabbitMQ**: http://localhost:15672 (dafu/dafu_rabbitmq_password)

### Test the API

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "version": "1.0.0",
#   ...
# }
```

### Test Fraud Detection

```bash
# Score a transaction
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

## Common Commands

```bash
# View logs
make logs
# or
./start.sh logs
# or
docker-compose logs -f

# Stop services
make stop
# or
./start.sh down

# Restart services
make restart
# or
./start.sh restart

# Check status
make status
# or
docker-compose ps
```

## Next Steps

1. **Explore API**: http://localhost:8000/docs
2. **View Dashboards**: http://localhost:3000
3. **Read Documentation**: [DOCKER_SETUP.md](DOCKER_SETUP.md)
4. **Customize Configuration**: Edit `.env` file
5. **Train Models**: See [fraud_detection/README.md](fraud_detection/README.md)

## Troubleshooting

### Port Already in Use

```bash
# Change ports in .env
echo "API_PORT=8001" >> .env
docker-compose up -d
```

### Services Won't Start

```bash
# Check logs
docker-compose logs

# Clean restart
docker-compose down -v
docker-compose up -d
```

### Out of Memory

```bash
# Reduce workers
echo "API_WORKERS=2" >> .env
docker-compose restart
```

## Getting Help

- **Full Documentation**: [DOCKER_SETUP.md](DOCKER_SETUP.md)
- **Project README**: [README.md](README.md)
- **Issues**: https://github.com/MasterFabric/dafu/issues
- **Email**: dafu@masterfabric.co

## Success! 🎉

Your DAFU - Data Analytics Functional Utilities platform is now running!

**What's Running:**
- ✅ Fraud Detection API (FastAPI)
- ✅ PostgreSQL Database
- ✅ Redis Cache
- ✅ RabbitMQ Message Broker
- ✅ Celery Workers
- ✅ Prometheus Monitoring
- ✅ Grafana Dashboards

**Ready for:**
- Real-time fraud detection
- Batch processing
- Model training
- Analytics and monitoring

---

*Built with ❤️ by MasterFabric*
