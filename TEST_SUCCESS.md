# ✅ DAFU CLI Tool - Test Successful!

## 🎉 All Tests Passed

Build and deployment completed successfully. All services are running!

## 📊 Running Services

```bash
✅ dafu-cli        - DAFU CLI Tool (port: 8000)
✅ dafu-postgres   - PostgreSQL Database (port: 5432)
✅ dafu-redis      - Redis Cache (port: 6379)
✅ dafu-rabbitmq   - RabbitMQ (port: 5672, management: 15672)
```

## 🚀 Usage Guide

### 1. Start Containers

```bash
# Method 1: with docker-compose
docker-compose --profile cli up -d

# Method 2: with Makefile
make start-cli
```

### 2. Use CLI Commands

#### Platform Info
```bash
docker exec dafu-cli dafu info
```

#### Available Models
```bash
docker exec dafu-cli dafu models
```

#### Version
```bash
docker exec dafu-cli dafu --version
```

### 3. Interactive Fraud Detection (Main Usage)

#### Method 1: Direct Execution
```bash
docker exec -it dafu-cli dafu fraud-detection
```

#### Method 2: With Makefile (Recommended)
```bash
make shell-cli
```

This command opens the interactive menu:
```
============================================================
🔍 ENTERPRISE FRAUD DETECTION PLATFORM
============================================================

1. 🔍 ISOLATION FOREST & RISK SCORE
2. 🧠 SEQUENCE MODELS (LSTM & GRU)
3. ℹ️  MODEL COMPARISON
4. ❓ HELP & INFORMATION
5. 🚪 EXIT

Enter your choice (1-5):
```

### 4. Connect to Container with Bash

```bash
# Enter container
docker exec -it dafu-cli bash

# Run commands inside
dafu fraud-detection
dafu models
dafu info

# Exit
exit
```

### 5. Use Your Own Data

```bash
# Copy data to container
docker cp my_data.csv dafu-cli:/app/fraud_detection/

# Enter container and run fraud detection
docker exec -it dafu-cli bash
cd /app/fraud_detection
dafu fraud-detection

# Get results
docker cp dafu-cli:/app/fraud_detection/results ./my_results
```

## 📝 Makefile Commands

```bash
make start-cli      # Start CLI tool
make shell-cli      # Run fraud detection (interactive)
make cli-connect    # Connect to container with bash
make stop           # Stop services
make logs           # Show logs
```

## 🔧 Other Useful Commands

### Watch Logs
```bash
# All logs
docker-compose logs -f

# CLI logs only
docker-compose logs -f dafu-cli

# Last 50 lines only
docker-compose logs --tail=50 dafu-cli
```

### Check Container Status
```bash
docker-compose ps
```

### Restart Services
```bash
docker-compose restart dafu-cli
```

### Stop and Clean Services
```bash
# Stop only (data remains)
docker-compose down

# Delete all data (WARNING!)
docker-compose down -v
```

## 🎯 Example Usage Scenario

### Scenario: Quick Fraud Analysis

```bash
# 1. Start services
make start-cli

# 2. Wait for containers to be ready (30 seconds)
sleep 30

# 3. Run fraud detection
make shell-cli

# 4. Make selections in menu:
#    1 -> Select Isolation Forest
#    2 -> Select Unsupervised mode
#    3 -> Enter Contamination 0.1
#    4 -> Press Enter, analysis starts!

# 5. Check results
docker exec dafu-cli ls -la /app/fraud_detection/results

# 6. Copy results to local
docker cp dafu-cli:/app/fraud_detection/results ./fraud_results

# 7. Stop when done
make stop
```

## 🌐 API Mode Usage (Optional)

If you want to use API instead of CLI:

```bash
# Start API
docker-compose --profile api up -d

# Or CLI + API together
docker-compose --profile cli --profile api up -d

# Access API documentation
open http://localhost:8000/docs

# Health check
curl http://localhost:8000/health
```

## 🔍 Troubleshooting

### Container not starting
```bash
# Check logs
docker-compose logs dafu-cli

# Rebuild
docker-compose --profile cli build --no-cache
docker-compose --profile cli up -d
```

### "Module not found" error
```bash
# Enter container
docker exec -it dafu-cli bash

# Check requirements
pip list | grep -E "click|rich|pandas"

# Reinstall if missing
pip install -r /app/fraud_detection/requirements.txt
```

### Database connection error
```bash
# Check PostgreSQL status
docker exec dafu-postgres pg_isready

# Check Redis status
docker exec dafu-redis redis-cli ping

# Check RabbitMQ status
docker exec dafu-rabbitmq rabbitmq-diagnostics ping
```

## 📚 More Information

- **Detailed CLI Usage**: `CLI_USAGE.md`
- **Quick Start**: `CLI_QUICK_START.md`
- **Implementation Details**: `CLI_IMPLEMENTATION.md`
- **Docker Setup**: `DOCKER_SETUP.md`

## ✅ Test Results

All tests successful:

- ✅ Docker build successful
- ✅ Containers started successfully
- ✅ CLI commands working (`dafu --version`, `dafu info`, `dafu models`)
- ✅ Services healthy (PostgreSQL, Redis, RabbitMQ)
- ✅ Interactive fraud detection menu working
- ✅ PYTHONPATH configured correctly
- ✅ Requirements installed

---

**MasterFabric** | DAFU CLI v1.0.0 | Test Date: 2025-10-09
