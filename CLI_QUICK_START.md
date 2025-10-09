# ⚡ DAFU CLI - Quick Start

## 🚀 Get Started in 5 Minutes

### 1️⃣ Start the CLI Tool

```bash
# First start the services
make start-cli

# or directly with docker-compose
docker-compose --profile cli up -d
```

### 2️⃣ Run Fraud Detection

```bash
# Enter interactive menu
make shell-cli

# or directly
docker exec -it dafu-cli dafu fraud-detection
```

### 3️⃣ Select and Use a Model

You will see these options in the interactive menu:

```
1. 🔍 ISOLATION FOREST & RISK SCORE
   - Fast and reliable anomaly detection
   - Optimized for tabular data
   
2. 🧠 SEQUENCE MODELS (LSTM & GRU)
   - Time series and sequence pattern detection
   - Captures temporal dependencies
   
3. ℹ️  MODEL COMPARISON
   - Compare models
   - Select the most suitable model
   
4. ❓ HELP & INFORMATION
   - Detailed information and help
   
5. 🚪 EXIT
```

## 📊 Example Usage

### Simple Fraud Detection

```bash
# Start CLI
docker exec -it dafu-cli dafu fraud-detection

# Select 1 in the menu (Isolation Forest)
# Then follow the interactive steps:
# - Choose Supervised or Unsupervised mode
# - Set contamination rate (e.g., 0.1 = 10% fraud)
# - Run analysis
```

### View Results

After analysis completes:

```bash
# Examine results folder in container
docker exec -it dafu-cli ls -la /app/fraud_detection/results

# Copy results to local
docker cp dafu-cli:/app/fraud_detection/results ./results
```

## 🎯 Other Commands

### Platform Information

```bash
docker exec -it dafu-cli dafu info
```

### Available Models

```bash
docker exec -it dafu-cli dafu models
```

### Interactive Python Shell

```bash
docker exec -it dafu-cli dafu shell
```

### Container Bash Shell

```bash
docker exec -it dafu-cli bash
```

## 🛠️ Makefile Shortcuts

```bash
make start-cli      # Start CLI
make shell-cli      # Open fraud detection
make cli-connect    # Connect to container with bash
make stop           # Stop all services
make logs           # View logs
```

## 📦 Use Your Own Data

### 1. Copy Data to Container

```bash
docker cp my_fraud_data.csv dafu-cli:/app/fraud_detection/
```

### 2. Enter Container and Analyze

```bash
# Enter container
docker exec -it dafu-cli bash

# Start fraud detection with DAFU CLI
dafu fraud-detection

# Select "1" in menu, continue with interactive mode
```

### 3. Get Results

```bash
# Copy results to local
docker cp dafu-cli:/app/fraud_detection/results ./my_results
```

## 🌐 API Mode

If you want to use API instead of CLI:

```bash
# Start API
make start-api

# Go to Swagger UI
open http://localhost:8000/docs

# Or test with cURL
curl http://localhost:8000/health
```

## 🎓 Advanced

### Start Full Stack

```bash
# CLI + API + Monitoring
make start-all

# Everything running:
# - CLI Tool: docker exec -it dafu-cli dafu fraud-detection
# - API: http://localhost:8000/docs
# - Grafana: http://localhost:3000
# - Prometheus: http://localhost:9090
```

### Run Custom Python Script

```bash
# Enter container
docker exec -it dafu-cli bash

# Run Python script
cd /app/fraud_detection
python my_custom_script.py
```

## ❓ Troubleshooting

### "Container not starting"

```bash
# Check logs
docker-compose logs dafu-cli

# Restart container
docker-compose restart dafu-cli
```

### "Getting import error"

```bash
# Check requirements
docker exec -it dafu-cli pip list

# Install missing package
docker exec -it dafu-cli pip install <package_name>
```

### "Can't connect to database"

```bash
# Is PostgreSQL running?
docker exec -it dafu-postgres pg_isready

# Is Redis running?
docker exec -it dafu-redis redis-cli ping
```

## 📚 More Information

- Detailed CLI usage: `CLI_USAGE.md`
- Docker setup: `DOCKER_SETUP.md`
- General README: `README.md`

## 💡 Pro Tips

1. **Use Makefile**: `make shell-cli` is the fastest way
2. **Save results**: Each analysis is saved to results/ folder
3. **Use sample data**: `/app/fraud_detection/sample_fraud_data.csv` is ready
4. **Use shell mode**: `dafu shell` has all modules ready
5. **API documentation**: `/docs` endpoint is always up-to-date

---

**Get Started Now**: `make start-cli && make shell-cli` 🚀
