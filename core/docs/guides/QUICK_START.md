# 🚀 DAFU - Quick Start Guide

⚠️ **IMPORTANT: Docker services are not active yet**

Get DAFU - Data Analytics Functional Utilities ML models running in **5 minutes**!

## Prerequisites

**For ML Models (Current Method):**
- Python 3.8+ ([Install Python](https://www.python.org/downloads/))
- 4GB RAM (minimum)
- 2GB free disk space

**For Future Docker Setup:**
- Docker 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Compose 2.0+ (Docker services commented out until ready)

## Quick Start

### ✅ Current Method: Direct Python Execution

```bash
# 1. Clone and setup
git clone https://github.com/MasterFabric/dafu.git
cd dafu/core/features/fraud_detection

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run ML models
cd src/models
python main.py  # Interactive model selection

# That's it! 🎉 All ML features work!
```

### ⚠️ Docker Method (Not Active Yet)

Docker infrastructure is prepared but services are commented out until API-ML integration is complete.

```bash
# Future usage (when ready):
# 1. Uncomment services in docker-compose.yml
# 2. Run: docker-compose up -d
```

## Verify Installation

### Test ML Models (Current Method)

```bash
# After running python main.py, you'll see:
# 🔍 ENTERPRISE FRAUD DETECTION PLATFORM
# ========================================
# 
# 1. 🔍 ISOLATION FOREST & RISK SCORE
# 2. 🧠 SEQUENCE MODELS (LSTM & GRU)
# 3. ℹ️  MODEL COMPARISON
# 4. ❓ HELP & INFORMATION
# 5. 🚪 EXIT
#
# Choose an option and follow the interactive prompts!
```

### Test Individual Models

```bash
# From fraud_detection directory
python test_anomaly_detection.py  # Isolation Forest
python test_sequence_models_interactive.py  # LSTM/GRU
```

### Future API Testing (When Docker is Active)

```bash
# These will work once services are uncommented:
# curl http://localhost:8000/health
# curl http://localhost:8000/docs
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
3. **Read Documentation**: [../docker/DOCKER_SETUP.md](../docker/DOCKER_SETUP.md)
4. **Customize Configuration**: Edit `.env` file
5. **Train Models**: See [../../features/fraud_detection/API_README.md](../../features/fraud_detection/API_README.md)

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

- **Full Documentation**: [../docker/DOCKER_SETUP.md](../docker/DOCKER_SETUP.md)
- **Project README**: [../README.md](../README.md)
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
