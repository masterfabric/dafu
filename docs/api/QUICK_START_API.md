# DAFU API Quick Start Guide

## 🚀 5-Minute Quick Start

This guide provides step-by-step instructions to quickly get DAFU API running.

### 1. Install Dependencies (2 minutes)

```bash
cd fraud_detection
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Start Database (1 minute)

#### With Docker (Recommended):

```bash
docker run -d \
  --name dafu-postgres \
  -e POSTGRES_USER=dafu \
  -e POSTGRES_PASSWORD=dafu_secure_password \
  -e POSTGRES_DB=dafu \
  -p 5432:5432 \
  postgres:15-alpine

# Create database tables
python -c "from src.api.database import init_db; init_db()"
```

#### With Local PostgreSQL:

```bash
createdb dafu
python -c "from src.api.database import init_db; init_db()"
```

### 3. Start the API (30 seconds)

```bash
# Method 1: With Uvicorn (recommended)
PYTHONPATH=/Users/furkancankaya/Documents/GitHub/dafu/fraud_detection/src uvicorn api.main:app --host 0.0.0.0 --port 8000

# or Method 2: With start script
cd /Users/furkancankaya/Documents/GitHub/dafu/fraud_detection
./start_api.sh
```

API will be available at: http://localhost:8000

### 4. Access API Documentation

Open in your browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## ⚡ Quick Test

### Test from Terminal:

```bash
# Health check
curl http://localhost:8000/health

# User registration
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "email": "test@example.com",
    "password": "Test123456"
  }'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "password": "Test123456"
  }'
```

### Test with CLI:

```bash
# User registration
python -m src.api.cli auth register

# Login
python -m src.api.cli auth login

# View your info
python -m src.api.cli auth whoami
```

---

## 📋 Basic CLI Commands

```bash
# Authentication
python -m src.api.cli auth login
python -m src.api.cli auth logout
python -m src.api.cli auth whoami

# Logs
python -m src.api.cli logs list
python -m src.api.cli logs stats

# Reports
python -m src.api.cli reports list
python -m src.api.cli reports create
python -m src.api.cli reports stats

# Products
python -m src.api.cli products list
python -m src.api.cli products high-risk
python -m src.api.cli products stats
```

---

## 🎯 Create Your First Report

### With CLI:

```bash
python -m src.api.cli reports create
# Name: My First Report
# Type: fraud_detection
# Description: Test report
```

### With API:

```bash
# First login and get token
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "test_user", "password": "Test123456"}' \
  | jq -r '.access_token')

# Create report
curl -X POST "http://localhost:8000/api/v1/reports/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Report",
    "report_type": "fraud_detection",
    "description": "Test report"
  }'
```

---

## 🐍 Using Python Client

```python
from src.api.cli_client import DAFUClient

# Create client
client = DAFUClient(base_url="http://localhost:8000")

# Register user
client.register(
    username="python_user",
    email="python@example.com",
    password="Python123"
)

# Login
result = client.login("python_user", "Python123")
print(f"Token: {result['access_token']}")

# Get user info
user = client.get_current_user()
print(f"Logged in as: {user['username']}")

# Create report
report = client.create_report(
    name="Python API Report",
    report_type="fraud_detection"
)
print(f"Report ID: {report['id']}")

# List products
products = client.get_products(limit=10)
for product in products:
    print(f"Product: {product['name']}")
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```bash
# API
API_PORT=8000
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://dafu:dafu_secure_password@localhost:5432/dafu

# Features
ENABLE_MONITORING=true
ENABLE_RATE_LIMITING=true
```

---

## 📊 Next Steps

1. ✅ Explore the API documentation: http://localhost:8000/docs
2. ✅ Try all CLI commands
3. ✅ Integrate your fraud detection models
4. ✅ Configure security settings for production
5. ✅ Setup monitoring and logging

---

## 🆘 Troubleshooting

### API won't start:

```bash
# Check port
lsof -i :8000

# Check dependencies
pip install -r requirements.txt --upgrade
```

### Database connection error:

```bash
# Is PostgreSQL running?
pg_isready -U dafu -d dafu

# Is Docker container running?
docker ps | grep dafu-postgres
```

### Detailed documentation:

📖 For detailed usage guide: [API_USAGE_GUIDE.md](./API_USAGE_GUIDE.md)

---

## 🎉 Successfully Installed!

Your API is ready! Now you can:
- ✅ Register and login users
- ✅ Create log records
- ✅ Generate reports
- ✅ Manage products
- ✅ Interact with CLI and API

**Happy coding!** 🚀

