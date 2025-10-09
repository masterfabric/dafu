# 🚀 DAFU CLI Tool - Usage Guide

DAFU (Data Analytics Functional Utilities) CLI Tool allows you to easily use fraud detection models.

## 📦 Installation

### 1. Docker Usage (Recommended)

```bash
# Start CLI Tool
docker-compose --profile cli up -d

# Connect to CLI
docker exec -it dafu-cli dafu fraud-detection
```

### 2. Local Installation

```bash
# Clone project
git clone https://github.com/MasterFabric/dafu.git
cd dafu

# Install CLI Tool
pip install -e .

# Install fraud detection requirements
pip install -r fraud_detection/requirements.txt

# Start CLI
dafu fraud-detection
```

## 🎯 Available Commands

### `dafu` - Main Command

```bash
dafu --help          # Help menu
dafu --version       # Version information
```

### `dafu info` - Platform Information

```bash
dafu info           # Platform status and information
```

### `dafu fraud-detection` - Interactive Fraud Detection

Access the interactive model selection menu with this command:

```bash
dafu fraud-detection
```

**Features:**
- ✅ Isolation Forest & Risk Score model
- ✅ LSTM & GRU Sequence models
- ✅ Model comparison
- ✅ Detailed help and information

### `dafu models` - List Available Models

```bash
dafu models         # List all fraud detection models
```

### `dafu analyze` - Batch Analysis

```bash
# Analyze with Isolation Forest
dafu analyze --model isolation-forest --input-file data.csv

# Analyze with LSTM
dafu analyze --model lstm --contamination 0.05 --input-file transactions.csv

# Analyze with all models
dafu analyze --model all --input-file data.csv
```

**Parameters:**
- `--model`: Model selection (isolation-forest, lstm, gru, all)
- `--contamination`: Expected fraud rate (0.01-0.5)
- `--input-file`: Input file (CSV format)

### `dafu api` - Start FastAPI Server

```bash
dafu api            # Start API server (http://0.0.0.0:8000)
```

API Documentation: `http://localhost:8000/docs`

### `dafu health` - Service Health Check

```bash
dafu health                    # Check all services
dafu health --service postgres # Check PostgreSQL only
dafu health --service redis    # Check Redis only
```

### `dafu shell` - Interactive Python Shell

```bash
dafu shell          # Start IPython shell (all modules loaded)
```

## 🐳 Docker Compose Usage

### Profiles

DAFU CLI Tool can run with different profiles:

#### 1. **CLI Mode** - Interactive Fraud Detection

```bash
# Start services
docker-compose --profile cli up -d

# Connect to CLI
docker exec -it dafu-cli dafu fraud-detection

# Watch logs
docker-compose logs -f dafu-cli
```

#### 2. **API Mode** - REST API Server

```bash
# Start API server
docker-compose --profile api up -d

# Access API documentation
open http://localhost:8000/docs

# Watch logs
docker-compose logs -f fraud-detection-api
```

#### 3. **Workers Mode** - Celery Workers

```bash
# Start Celery workers
docker-compose --profile workers up -d

# Watch logs
docker-compose logs -f celery-worker
```

#### 4. **Monitoring Mode** - Prometheus & Grafana

```bash
# Start monitoring stack
docker-compose --profile monitoring up -d

# Access Grafana
open http://localhost:3000  # admin/admin

# Access Prometheus
open http://localhost:9090
```

#### 5. **Tools Mode** - Management Tools

```bash
# Start management tools
docker-compose --profile tools up -d

# Access PgAdmin
open http://localhost:5050  # admin@dafu.local/admin

# Access Redis Commander
open http://localhost:8081
```

### Multiple Profiles

```bash
# CLI + API
docker-compose --profile cli --profile api up -d

# Full stack (CLI, API, Workers, Monitoring)
docker-compose \
  --profile cli \
  --profile api \
  --profile workers \
  --profile monitoring \
  up -d

# Stop everything
docker-compose down
```

## 📊 Example Usage Scenarios

### Scenario 1: Quick Fraud Analysis

```bash
# Start Docker
docker-compose --profile cli up -d

# Enter CLI
docker exec -it dafu-cli bash

# Run fraud detection
dafu fraud-detection

# Select from menu:
# 1 -> Isolation Forest
# Follow interactive menu
```

### Scenario 2: API Integration

```bash
# Start API
docker-compose --profile api up -d

# Test API
curl http://localhost:8000/health

# View documentation
open http://localhost:8000/docs
```

### Scenario 3: Batch Processing

```bash
# Copy file to container
docker cp my_data.csv dafu-cli:/app/fraud_detection/

# Run analysis
docker exec -it dafu-cli dafu analyze \
  --model isolation-forest \
  --input-file my_data.csv \
  --contamination 0.1
```

### Scenario 4: Development Environment

```bash
# Full development stack
docker-compose \
  --profile cli \
  --profile api \
  --profile tools \
  up -d

# Work interactively in CLI
docker exec -it dafu-cli dafu shell

# Test API
curl http://localhost:8000/api/v1/models

# Manage database
open http://localhost:5050
```

## 🔧 Troubleshooting

### Container startup issues

```bash
# Check logs
docker-compose logs dafu-cli

# Restart container
docker-compose restart dafu-cli

# Enter container
docker exec -it dafu-cli bash
```

### Dependency issues

```bash
# Reinstall requirements
docker exec -it dafu-cli pip install -r /app/fraud_detection/requirements.txt

# Reinstall CLI
docker exec -it dafu-cli pip install -e /app/
```

### Database connection issues

```bash
# Check PostgreSQL status
docker exec -it dafu-postgres pg_isready

# Check Redis status
docker exec -it dafu-redis redis-cli ping

# Check RabbitMQ status
docker exec -it dafu-rabbitmq rabbitmq-diagnostics ping
```

## 📝 Environment Variables

Create `.env` file:

```bash
cp .env.example .env
```

Important variables:

```bash
FRAUD_DETECTION_ENV=development    # development, staging, production
LOG_LEVEL=INFO                     # DEBUG, INFO, WARNING, ERROR
API_PORT=8000                      # API port
POSTGRES_PASSWORD=***              # Secure password
SECRET_KEY=***                     # Change in production
```

## 🎓 Advanced Usage

### Custom Model Training

```python
# Enter Python shell with dafu shell
dafu shell

# Train model
from models.anomaly_detection import IsolationForestFraudDetector

detector = IsolationForestFraudDetector(contamination=0.1)
detector.train(X_train)
detector.save_model("my_model.joblib")
```

### API Integration

```python
import requests

# Get fraud score
response = requests.post(
    "http://localhost:8000/api/v1/score",
    json={
        "transaction_id": "txn_123",
        "amount": 500.0,
        "user_id": "user_456",
        "merchant_id": "merchant_789",
        "timestamp": "2024-01-15T10:30:00Z"
    }
)

print(response.json())
```

## 📚 More Information

- **General README**: `README.md`
- **Docker Setup**: `DOCKER_SETUP.md`
- **Quick Start**: `CLI_QUICK_START.md`
- **API Documentation**: `http://localhost:8000/docs` (when API is running)

## 🆘 Help

```bash
# Help for each command
dafu --help
dafu fraud-detection --help
dafu analyze --help

# Platform information
dafu info

# Model list
dafu models
```

---

**MasterFabric** | DAFU v1.0.0 | AGPL-3.0 License
