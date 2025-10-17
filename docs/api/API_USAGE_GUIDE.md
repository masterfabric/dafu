# DAFU API & CLI Usage Guide

## 📋 Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Starting the API](#starting-the-api)
3. [CLI Usage](#cli-usage)
4. [API Endpoints](#api-endpoints)
5. [Authentication](#authentication)
6. [Examples](#examples)

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.9+
- PostgreSQL 15+ (or use Docker)
- Redis 7+ (optional, or use Docker)

### 1. Install Dependencies

```bash
cd fraud_detection
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 3. Initialize Database

#### Option A: Using Docker (Recommended)

```bash
# Start PostgreSQL with Docker
docker run -d \
  --name dafu-postgres \
  -e POSTGRES_USER=dafu \
  -e POSTGRES_PASSWORD=dafu_secure_password \
  -e POSTGRES_DB=dafu \
  -p 5432:5432 \
  postgres:15-alpine
```

#### Option B: Local PostgreSQL

```bash
# Create database
createdb dafu

# Initialize tables
cd fraud_detection
python -c "from src.api.database import init_db; init_db()"
```

---

## 🌐 Starting the API

### Development Mode

```bash
cd fraud_detection/src/api
python main.py
```

The API will be available at: http://localhost:8000

### Production Mode with Uvicorn

```bash
cd fraud_detection
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Documentation

Once running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

---

## 💻 CLI Usage

### Setup CLI

The CLI is available as a Python module:

```bash
# From the fraud_detection directory
python -m src.api.cli <command>

# Or create an alias for convenience
alias dafu-api='python -m src.api.cli'
```

### CLI Commands Overview

#### Authentication

```bash
# Register a new user
python -m src.api.cli auth register

# Login
python -m src.api.cli auth login

# Show current user
python -m src.api.cli auth whoami

# Logout
python -m src.api.cli auth logout
```

#### Logs Management

```bash
# List recent logs
python -m src.api.cli logs list [limit]

# Show log statistics
python -m src.api.cli logs stats [hours]
```

#### Reports Management

```bash
# List reports
python -m src.api.cli reports list [limit]

# Create a new report
python -m src.api.cli reports create

# View report details
python -m src.api.cli reports view <report_id>

# Show report statistics
python -m src.api.cli reports stats
```

#### Products Management

```bash
# List products
python -m src.api.cli products list [limit]

# List high-risk products
python -m src.api.cli products high-risk [limit]

# Show product statistics
python -m src.api.cli products stats
```

---

## 🔐 Authentication

### 1. Register a New User

**CLI:**
```bash
python -m src.api.cli auth register
```

**API:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePassword123",
    "full_name": "John Doe",
    "company": "ACME Corp"
  }'
```

### 2. Login

**CLI:**
```bash
python -m src.api.cli auth login
# Enter username and password when prompted
```

**API:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "SecurePassword123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### 3. Use Token in Requests

```bash
# Set token in environment
export DAFU_TOKEN="your-access-token-here"

# Use in requests
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer $DAFU_TOKEN"
```

### 4. Generate API Key

**CLI:**
```bash
python -m src.api.cli auth generate-api-key
```

**API:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/api-key" \
  -H "Authorization: Bearer $DAFU_TOKEN"
```

---

## 📚 API Endpoints

### Health Check

```bash
# Check API health
curl http://localhost:8000/health

# Root endpoint
curl http://localhost:8000/
```

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | User login |
| POST | `/api/v1/auth/logout` | User logout |
| GET | `/api/v1/auth/me` | Get current user |
| POST | `/api/v1/auth/change-password` | Change password |
| POST | `/api/v1/auth/api-key` | Generate API key |
| GET | `/api/v1/auth/users` | List all users (Admin) |
| GET | `/api/v1/auth/users/{id}` | Get user by ID (Admin) |
| DELETE | `/api/v1/auth/users/{id}` | Delete user (Admin) |

### Log Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/logs/` | Create log entry |
| GET | `/api/v1/logs/` | Get logs (Analyst+) |
| GET | `/api/v1/logs/my-logs` | Get user's logs |
| GET | `/api/v1/logs/stats` | Get log statistics (Analyst+) |
| GET | `/api/v1/logs/{id}` | Get log by ID (Analyst+) |
| DELETE | `/api/v1/logs/cleanup` | Cleanup old logs (Admin) |

### Report Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/reports/` | Create report |
| GET | `/api/v1/reports/` | Get user's reports |
| GET | `/api/v1/reports/all` | Get all reports (Analyst+) |
| GET | `/api/v1/reports/stats` | Get report statistics |
| GET | `/api/v1/reports/{id}` | Get report by ID |
| PUT | `/api/v1/reports/{id}` | Update report |
| DELETE | `/api/v1/reports/{id}` | Delete report |
| POST | `/api/v1/reports/{id}/retry` | Retry failed report |

### Product Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/products/` | Create product (Analyst+) |
| GET | `/api/v1/products/` | Get products |
| GET | `/api/v1/products/high-risk` | Get high-risk products (Analyst+) |
| GET | `/api/v1/products/low-stock` | Get low-stock products |
| GET | `/api/v1/products/stats` | Get product statistics |
| GET | `/api/v1/products/{id}` | Get product by ID |
| GET | `/api/v1/products/sku/{sku}` | Get product by SKU |
| PUT | `/api/v1/products/{id}` | Update product (Analyst+) |
| DELETE | `/api/v1/products/{id}` | Delete product (Analyst+) |
| PUT | `/api/v1/products/{id}/fraud-risk` | Update fraud risk (Analyst+) |
| POST | `/api/v1/products/{id}/stock` | Update stock (Analyst+) |

---

## 🎯 Examples

### Example 1: Complete Authentication Flow

```bash
# 1. Register
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "analyst1",
    "email": "analyst@company.com",
    "password": "SecurePass123",
    "full_name": "Senior Analyst"
  }'

# 2. Login
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "analyst1", "password": "SecurePass123"}' \
  | jq -r '.access_token')

# 3. Get user info
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN"
```

### Example 2: Working with Logs

```bash
# Create a log entry
curl -X POST "http://localhost:8000/api/v1/logs/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "level": "info",
    "message": "User logged in successfully",
    "module": "authentication",
    "endpoint": "/api/v1/auth/login",
    "method": "POST",
    "status_code": 200,
    "response_time_ms": 45.2
  }'

# Get recent logs
curl -X GET "http://localhost:8000/api/v1/logs/my-logs?limit=10" \
  -H "Authorization: Bearer $TOKEN"

# Get log statistics
curl -X GET "http://localhost:8000/api/v1/logs/stats?hours=24" \
  -H "Authorization: Bearer $TOKEN"
```

### Example 3: Creating and Managing Reports

```bash
# Create a fraud detection report
curl -X POST "http://localhost:8000/api/v1/reports/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Monthly Fraud Analysis",
    "report_type": "fraud_detection",
    "description": "Comprehensive fraud detection analysis for October 2025",
    "config": {
      "contamination": 0.1,
      "models": ["isolation_forest", "lstm"]
    },
    "filters": {
      "start_date": "2025-10-01",
      "end_date": "2025-10-31"
    }
  }'

# List reports
curl -X GET "http://localhost:8000/api/v1/reports/?limit=20" \
  -H "Authorization: Bearer $TOKEN"

# Get report details
curl -X GET "http://localhost:8000/api/v1/reports/1" \
  -H "Authorization: Bearer $TOKEN"

# Get report statistics
curl -X GET "http://localhost:8000/api/v1/reports/stats" \
  -H "Authorization: Bearer $TOKEN"
```

### Example 4: Product Management

```bash
# Create a product
curl -X POST "http://localhost:8000/api/v1/products/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "PROD-12345",
    "name": "Premium Widget",
    "description": "High-quality widget with advanced features",
    "price": 99.99,
    "currency": "USD",
    "category": "Electronics",
    "brand": "TechBrand",
    "stock_quantity": 100
  }'

# List products
curl -X GET "http://localhost:8000/api/v1/products/?limit=20" \
  -H "Authorization: Bearer $TOKEN"

# Get high-risk products
curl -X GET "http://localhost:8000/api/v1/products/high-risk" \
  -H "Authorization: Bearer $TOKEN"

# Update product fraud risk
curl -X PUT "http://localhost:8000/api/v1/products/1/fraud-risk" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fraud_risk_score": 0.75,
    "high_risk": true,
    "fraud_incidents": 5,
    "chargeback_rate": 0.12
  }'

# Update stock
curl -X POST "http://localhost:8000/api/v1/products/1/stock?quantity=150" \
  -H "Authorization: Bearer $TOKEN"
```

### Example 5: Using Python Client Library

```python
from fraud_detection.src.api.cli_client import DAFUClient, SessionManager

# Initialize client
client = DAFUClient(base_url="http://localhost:8000")

# Register and login
client.register(
    username="analyst1",
    email="analyst@company.com",
    password="SecurePass123",
    full_name="Senior Analyst"
)

# Login
result = client.login("analyst1", "SecurePass123")
print(f"Access Token: {result['access_token']}")

# Get current user
user = client.get_current_user()
print(f"Logged in as: {user['username']} ({user['role']})")

# Create a log
log = client.create_log(
    level="info",
    message="API test completed successfully",
    module="testing"
)

# Get logs
logs = client.get_my_logs(limit=10)
for log in logs:
    print(f"[{log['level'].upper()}] {log['message']}")

# Create a report
report = client.create_report(
    name="Test Report",
    report_type="fraud_detection",
    description="Test fraud detection report"
)
print(f"Report ID: {report['id']}, Status: {report['status']}")

# Get products
products = client.get_products(limit=10)
for product in products:
    print(f"SKU: {product['sku']}, Name: {product['name']}, Risk: {product['fraud_risk_score']}")
```

---

## 🔒 User Roles and Permissions

| Role | Permissions |
|------|-------------|
| **viewer** | Read-only access to own data |
| **user** | Create and manage own resources |
| **analyst** | Access all data, create reports, manage products |
| **admin** | Full access, user management, system configuration |

---

## 🛠️ Troubleshooting

### API Won't Start

```bash
# Check if port 8000 is already in use
lsof -i :8000

# Check database connection
psql -U dafu -d dafu -h localhost

# Check logs
tail -f fraud_detection/logs/api.log
```

### Authentication Issues

```bash
# Verify JWT token
python -c "from jose import jwt; print(jwt.decode('YOUR_TOKEN', 'SECRET_KEY', algorithms=['HS256']))"

# Check session file
cat ~/.dafu_session
```

### Database Issues

```bash
# Reinitialize database
python -c "from src.api.database import drop_db, init_db; drop_db(); init_db()"

# Check database tables
psql -U dafu -d dafu -c "\dt"
```

---

## 📝 Best Practices

1. **Always use HTTPS in production**
2. **Change default passwords and secret keys**
3. **Use environment variables for sensitive data**
4. **Implement rate limiting for API endpoints**
5. **Regularly backup your database**
6. **Monitor API performance and errors**
7. **Keep dependencies up to date**
8. **Use strong passwords (minimum 12 characters)**
9. **Enable 2FA for admin accounts** (if implemented)
10. **Regularly review access logs**

---

## 🔄 Next Steps

1. ✅ Setup and start the API
2. ✅ Register your first user
3. ✅ Explore the API documentation at `/docs`
4. ✅ Try CLI commands
5. ✅ Create your first report
6. ✅ Integrate with your fraud detection models
7. ✅ Set up monitoring and alerts
8. ✅ Deploy to production

---

## 📞 Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/MasterFabric/dafu/issues
- Documentation: `/docs` directory
- API Docs: http://localhost:8000/docs

---

## 📄 License

AGPL-3.0 - See LICENSE file for details

