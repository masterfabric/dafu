# DAFU - Complete Usage Guide

## 🎯 Overview

DAFU (Data Analytics Functional Utilities) is an enterprise fraud detection platform with an integrated CLI that provides:
- 🔐 **Authentication & User Management** (JWT-based)
- 📋 **System Logging & Analytics**
- 📊 **Fraud Detection Reports**
- 🛍️ **Product Risk Management**
- 🤖 **ML Model Execution**
- 🐳 **Docker Service Orchestration**

**All from one unified CLI: `./dafu`**

---

## 🚀 Quick Start (3 Steps)

### Step 1: Start PostgreSQL

```bash
docker run -d --name dafu-postgres \
  -e POSTGRES_USER=dafu \
  -e POSTGRES_PASSWORD=dafu_secure_password \
  -e POSTGRES_DB=dafu \
  -p 5432:5432 \
  postgres:15-alpine
```

### Step 2: Start API (in separate terminal)

```bash
cd fraud_detection
./start_api.sh
```

Keep this running! Wait for:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Step 3: Use DAFU CLI

```bash
./dafu

dafu> help              # See all commands
dafu> auth register     # Register first time
dafu> auth login        # Login
dafu> auth whoami       # Check user info
dafu> logs list         # View logs
dafu> reports list      # View reports
dafu> products stats    # Product statistics
```

---

## 📋 Complete Command Reference

### 🔐 Authentication & User Management

| Command | Description | Example |
|---------|-------------|---------|
| `auth login` | Login to API (interactive) | `./dafu auth login` |
| `auth logout` | Logout and clear session | `./dafu auth logout` |
| `auth whoami` | Show current user info | `./dafu auth whoami` |
| `auth register` | Register new user | `./dafu auth register` |

**Example**:
```bash
./dafu auth login
# Username: admin
# Password: ********
# ✓ Logged in as 'admin'
```

---

### 📋 Logs Management

| Command | Description | Example |
|---------|-------------|---------|
| `logs list [limit]` | List recent logs | `./dafu logs list 20` |
| `logs stats [hours]` | Show log statistics | `./dafu logs stats 24` |

**Example**:
```bash
./dafu logs list 10

# Output:
# ID | Level | Message              | Time
# 10 | INFO  | User logged in       | 2025-10-17 12:00
# 9  | INFO  | Report completed     | 2025-10-17 11:55
# ...
```

---

### 📊 Reports Management

| Command | Description | Example |
|---------|-------------|---------|
| `reports list [limit]` | List your reports | `./dafu reports list` |
| `reports create` | Create new report (interactive) | `./dafu reports create` |
| `reports view <id>` | View report details | `./dafu reports view 1` |
| `reports stats` | Show report statistics | `./dafu reports stats` |

**Example**:
```bash
./dafu reports create
# Report Name: Monthly Fraud Analysis
# Report Type: fraud_detection
# Description: October 2025 analysis
# ✓ Report created with ID: 5

./dafu reports view 5
# Report Details:
# ID: 5
# Name: Monthly Fraud Analysis
# Status: completed
# Progress: 100%
# ...
```

---

### 🛍️ Products Management

| Command | Description | Example |
|---------|-------------|---------|
| `products list [limit]` | List products | `./dafu products list 50` |
| `products high-risk [limit]` | List high-risk products | `./dafu products high-risk` |
| `products stats` | Show product statistics | `./dafu products stats` |

**Example**:
```bash
./dafu products high-risk 5

# Output:
# ID  | SKU       | Name          | Risk Score | Incidents
# 15  | PHONE-X   | Phone Model X | 0.85       | 12
# 23  | WATCH-L   | Luxury Watch  | 0.78       | 8
# ...
```

---

### 🤖 ML Models (Fraud Detection)

| Command | Description | Example |
|---------|-------------|---------|
| `fraud-detection` | Run ML models (interactive) | `./dafu fraud-detection` |
| `models` | Alias for fraud-detection | `./dafu models` |
| `ml` | Alias for fraud-detection | `./dafu ml` |

**Example**:
```bash
./dafu fraud-detection

# Interactive menu appears:
# 1. 🔍 ISOLATION FOREST & RISK SCORE
# 2. 🧠 SEQUENCE MODELS (LSTM & GRU)
# 3. ℹ️  MODEL COMPARISON
# 4. ❓ HELP & INFORMATION
# 5. 🚪 EXIT
```

---

### 🐳 Docker Services

| Command | Description | Example |
|---------|-------------|---------|
| `docker up` | Start Docker services | `./dafu docker up` |
| `docker down` | Stop Docker services | `./dafu docker down` |
| `docker restart` | Restart Docker services | `./dafu docker restart` |
| `docker status` | Show service status | `./dafu docker status` |
| `docker logs` | View Docker logs | `./dafu docker logs` |
| `docker rebuild` | Rebuild services | `./dafu docker rebuild` |

---

### 📊 System Information

| Command | Description | Example |
|---------|-------------|---------|
| `status` | Show platform status | `./dafu status` |
| `version` | Show version info | `./dafu version` |
| `info` | Show system info | `./dafu info` |
| `help` | Show help menu | `./dafu help` |
| `clear` | Clear screen | `./dafu clear` |
| `exit` | Exit CLI | `./dafu exit` |

---

## 🎯 Usage Modes

### Interactive Mode (Recommended)

```bash
./dafu

# Interactive session starts
dafu> help
dafu> auth login
dafu> logs list
dafu> reports stats
dafu> exit
```

**Benefits**:
- Stay in one session
- Run multiple commands
- Faster execution
- Better UX

### Single Command Mode

```bash
./dafu auth whoami
./dafu logs list 20
./dafu reports view 1
./dafu products stats
```

**Benefits**:
- Quick one-off commands
- Scriptable
- CI/CD friendly

---

## 💡 Complete Workflow Examples

### Example 1: Daily Fraud Check Routine

```bash
# Start DAFU CLI
./dafu

# Login
dafu> auth login

# Check current user
dafu> auth whoami

# View recent logs
dafu> logs list 50

# Check latest reports
dafu> reports list 10

# View high-risk products
dafu> products high-risk 20

# Check statistics
dafu> logs stats 24
dafu> reports stats
dafu> products stats

# Logout
dafu> auth logout
```

### Example 2: Create and Monitor Report

```bash
./dafu

dafu> auth login

# Create new fraud detection report
dafu> reports create
# Name: Weekly Fraud Analysis
# Type: fraud_detection
# Description: Weekly fraud pattern analysis

# List reports to get ID
dafu> reports list

# View report details (assuming ID is 7)
dafu> reports view 7

# Check report statistics
dafu> reports stats
```

### Example 3: Product Risk Analysis

```bash
./dafu

dafu> auth login

# List all products
dafu> products list 100

# Focus on high-risk products
dafu> products high-risk 10

# Check product statistics
dafu> products stats

# View system logs related to products
dafu> logs list 20
```

### Example 4: ML Model Training + Reporting

```bash
./dafu

# Run ML models
dafu> fraud-detection
# Select model, train, analyze...
# (returns to CLI when done)

# Check if report was created
dafu> reports list

# View system logs
dafu> logs list

# Check product risk updates
dafu> products high-risk
```

---

## 🔑 Prerequisites & Setup

### Required Services

1. **PostgreSQL** (for API data storage)
   ```bash
   docker run -d --name dafu-postgres \
     -e POSTGRES_USER=dafu \
     -e POSTGRES_PASSWORD=dafu_secure_password \
     -e POSTGRES_DB=dafu \
     -p 5432:5432 \
     postgres:15-alpine
   ```

2. **DAFU API** (for auth, logs, reports, products)
   ```bash
   cd fraud_detection
   ./start_api.sh
   ```

3. **Python Environment** (auto-managed by CLI)
   - Virtual environment created automatically
   - Dependencies installed automatically

### First-Time User Setup

```bash
# 1. Clone repository
git clone https://github.com/MasterFabric/dafu.git
cd dafu

# 2. Make CLI executable
chmod +x dafu

# 3. Start PostgreSQL
docker run -d --name dafu-postgres \
  -e POSTGRES_USER=dafu \
  -e POSTGRES_PASSWORD=dafu_secure_password \
  -e POSTGRES_DB=dafu \
  -p 5432:5432 \
  postgres:15-alpine

# 4. Start API (new terminal)
cd fraud_detection
./start_api.sh

# 5. Register user (first time - use curl)
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "admin123"
  }'

# 6. Use DAFU CLI
./dafu
dafu> auth login
# Username: admin
# Password: admin123
dafu> auth whoami
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file in root:

```bash
# API Configuration
API_PORT=8000
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://dafu:dafu_secure_password@localhost:5432/dafu

# Features
ENABLE_MONITORING=true
ENABLE_RATE_LIMITING=true
```

### Session Management

- **Session File**: `~/.dafu_session`
- **Token Expiry**: 24 hours
- **Auto-login**: Session persists across CLI restarts
- **Logout**: Clears session file

---

## 🐛 Troubleshooting

### "Failed to connect to localhost port 8000"

**Problem**: API not running
**Solution**:
```bash
cd fraud_detection
./start_api.sh
```

### "API Error (500): An unexpected error occurred"

**Problem**: PostgreSQL not running
**Solution**:
```bash
# Check if running
docker ps | grep dafu-postgres

# Start if stopped
docker start dafu-postgres

# Or create new
docker rm -f dafu-postgres
docker run -d --name dafu-postgres \
  -e POSTGRES_USER=dafu \
  -e POSTGRES_PASSWORD=dafu_secure_password \
  -e POSTGRES_DB=dafu \
  -p 5432:5432 \
  postgres:15-alpine
```

### "You must be logged in"

**Problem**: No active session
**Solution**:
```bash
./dafu auth login
```

### "address already in use" (port 8000)

**Problem**: Old API process running
**Solution**:
```bash
pkill -9 -f uvicorn
sleep 2
# Then restart API
```

---

## 📚 Related Documentation

### Quick References
- **[API Usage Guide](./api/API_USAGE_GUIDE.md)** - Complete API documentation
- **[API Quick Start](./api/QUICK_START_API.md)** - 5-minute API setup
- **[CLI Guide](./cli/DAFU_CLI_GUIDE.md)** - Original CLI guide
- **[CLI Integration](./cli/DAFU_CLI_INTEGRATED.md)** - API integration details
- **[CLI Step-by-Step](./cli/CLI_STEP_BY_STEP.md)** - Detailed CLI usage

### Guides
- **[Quick Start](./guides/QUICK_START.md)** - ML models quick start
- **[Docker Status](./docker/DOCKER_STATUS.md)** - Docker deployment info

---

## 🎓 Advanced Usage

### Scripting with DAFU CLI

```bash
#!/bin/bash
# automated_check.sh

# Login (non-interactive - use session file)
# First create session manually: ./dafu auth login

# Run commands
./dafu logs stats 24 > daily_logs.txt
./dafu reports stats > daily_reports.txt
./dafu products high-risk > high_risk_products.txt

# Send reports via email
mail -s "Daily DAFU Report" admin@company.com < daily_logs.txt
```

### Python Integration

```python
from fraud_detection.src.api.cli_client import DAFUClient

# Create client
client = DAFUClient(base_url="http://localhost:8000")

# Login
client.login("username", "password")

# Use API programmatically
user = client.get_current_user()
logs = client.get_my_logs(limit=100)
reports = client.get_reports(limit=50)
products = client.get_high_risk_products()

# Process data
for product in products:
    if product['fraud_risk_score'] > 0.8:
        print(f"Alert: {product['name']} - Risk: {product['fraud_risk_score']}")
```

---

## 🎉 Features Summary

### ✅ Fully Working Features

- **Authentication System**: JWT-based, role-based access control
- **Logging System**: Structured logging with analytics
- **Report Management**: Fraud detection report generation
- **Product Management**: Risk tracking and inventory
- **ML Models**: Isolation Forest, LSTM, GRU models
- **Stream Processing**: Real-time data processing
- **Batch Processing**: Large-scale analysis
- **Model Persistence**: Save/load trained models
- **Unified CLI**: Single command for all features
- **Docker Support**: Service orchestration

### 🔑 Key Benefits

1. **Unified Interface**: One CLI for everything
2. **Auto-Management**: Virtual environment handled automatically
3. **Persistent Sessions**: Login once, use everywhere
4. **Interactive & Scriptable**: Works both ways
5. **Production-Ready**: Enterprise-grade security and reliability
6. **Extensible**: Easy to add new features

---

## 📊 User Roles & Permissions

| Role | Permissions |
|------|-------------|
| **viewer** | Read-only access to own data |
| **user** | Create and manage own resources |
| **analyst** | Access all data, manage products, view all logs |
| **admin** | Full system access, user management |

---

## 🛠️ Technology Stack

- **CLI**: Bash + Python
- **API**: FastAPI
- **Database**: PostgreSQL
- **Authentication**: JWT (python-jose)
- **Password Hashing**: Passlib + bcrypt
- **ORM**: SQLAlchemy
- **ML**: scikit-learn, TensorFlow
- **Containerization**: Docker
- **Documentation**: OpenAPI/Swagger

---

## 📞 Support

- **Documentation**: `/docs` directory
- **API Docs**: http://localhost:8000/docs (when running)
- **GitHub Issues**: https://github.com/MasterFabric/dafu/issues
- **Email**: dafu@masterfabric.co

---

## 🎯 What's Next?

1. ✅ Explore all CLI commands: `./dafu help`
2. ✅ Try ML models: `./dafu fraud-detection`
3. ✅ Create your first report: `./dafu reports create`
4. ✅ Monitor products: `./dafu products high-risk`
5. ✅ Check system health: `./dafu status`
6. ✅ View API docs: http://localhost:8000/docs

---

**DAFU - Your Complete Fraud Detection Platform** 🚀

**Version**: 2.0.0 (with API integration)
**Updated**: 2025-10-17
**License**: AGPL-3.0

