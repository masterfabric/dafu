# DAFU API - Authentication, Logging, Reporting & Product Management

## 🎯 Overview

DAFU API is an enterprise-grade backend system built with FastAPI. It provides JWT authentication, logging, reporting, and product management features.

## ✨ Features

### 🔐 Authentication & Authorization
- JWT token-based authentication
- Role-based access control (RBAC)
- API key generation
- User registration & login
- Password management
- Session management

### 📋 Logging System
- Structured logging
- Log levels (debug, info, warning, error, critical)
- Request/response logging
- Performance metrics
- Log statistics and analytics

### 📊 Report Management
- Fraud detection reports
- Analytics reports
- Risk analysis reports
- Asynchronous report generation
- Progress tracking
- Report statistics

### 🛍️ Product Management
- Product CRUD operations
- Fraud risk tracking
- Stock management
- High-risk product detection
- Product analytics
- Category management

## 🚀 Quick Start

### 1. Quick Start

```bash
cd fraud_detection
./start_api.sh
```

API will be available at: http://localhost:8000

### 2. Manual Start

```bash
cd fraud_detection
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Initialize database
python -c "from src.api.database import init_db; init_db()"

# Start API
cd src/api
python main.py
```

## 💻 CLI Usage

### Authentication

```bash
# Register
python -m src.api.cli auth register

# Login
python -m src.api.cli auth login

# Check current user
python -m src.api.cli auth whoami

# Logout
python -m src.api.cli auth logout
```

### Logs

```bash
# List logs
python -m src.api.cli logs list 20

# Show statistics
python -m src.api.cli logs stats 24
```

### Reports

```bash
# List reports
python -m src.api.cli reports list

# Create report
python -m src.api.cli reports create

# View report
python -m src.api.cli reports view 1

# Show statistics
python -m src.api.cli reports stats
```

### Products

```bash
# List products
python -m src.api.cli products list

# High-risk products
python -m src.api.cli products high-risk

# Show statistics
python -m src.api.cli products stats
```

## 🔌 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/change-password` - Change password
- `POST /api/v1/auth/api-key` - Generate API key

### Logs
- `POST /api/v1/logs/` - Create log entry
- `GET /api/v1/logs/` - Get logs (filtered)
- `GET /api/v1/logs/my-logs` - Get user's logs
- `GET /api/v1/logs/stats` - Get log statistics
- `GET /api/v1/logs/{id}` - Get log by ID

### Reports
- `POST /api/v1/reports/` - Create report
- `GET /api/v1/reports/` - Get user's reports
- `GET /api/v1/reports/all` - Get all reports (Analyst+)
- `GET /api/v1/reports/{id}` - Get report by ID
- `PUT /api/v1/reports/{id}` - Update report
- `DELETE /api/v1/reports/{id}` - Delete report
- `POST /api/v1/reports/{id}/retry` - Retry failed report

### Products
- `POST /api/v1/products/` - Create product (Analyst+)
- `GET /api/v1/products/` - Get products
- `GET /api/v1/products/high-risk` - Get high-risk products
- `GET /api/v1/products/{id}` - Get product by ID
- `GET /api/v1/products/sku/{sku}` - Get product by SKU
- `PUT /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Delete product
- `PUT /api/v1/products/{id}/fraud-risk` - Update fraud risk
- `POST /api/v1/products/{id}/stock` - Update stock

## 📚 Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🐍 Python Client Usage

```python
from src.api.cli_client import DAFUClient

# Initialize client
client = DAFUClient(base_url="http://localhost:8000")

# Register & login
client.register(username="user1", email="user@example.com", password="pass123")
result = client.login("user1", "pass123")

# Get current user
user = client.get_current_user()
print(f"Logged in as: {user['username']}")

# Create log
log = client.create_log(level="info", message="Test log")

# Create report
report = client.create_report(
    name="Test Report",
    report_type="fraud_detection"
)

# Get products
products = client.get_products(limit=10)
```

## 🗄️ Database Schema

### Users Table
- id, username, email, hashed_password
- role (admin, analyst, user, viewer)
- status (active, inactive, suspended, deleted)
- api_key, created_at, updated_at, last_login

### Logs Table
- id, user_id, level, message, module, function
- endpoint, method, status_code, response_time_ms
- ip_address, user_agent, metadata, created_at

### Reports Table
- id, user_id, name, description, report_type
- status (pending, processing, completed, failed)
- progress, config, filters, results, metrics
- total_records, processing_time_seconds
- created_at, started_at, completed_at

### Products Table
- id, sku, name, description, price, currency
- category, subcategory, brand, tags
- stock_quantity, low_stock_threshold
- fraud_risk_score, high_risk, fraud_incidents
- status (active, inactive, suspended, deleted)
- created_at, updated_at

## 🔒 User Roles

| Role | Permissions |
|------|-------------|
| **viewer** | Read own data |
| **user** | Manage own resources |
| **analyst** | Access all data, manage products |
| **admin** | Full system access |

## 🛠️ Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL 15+
- **Authentication**: JWT (python-jose)
- **Password Hashing**: Passlib + bcrypt
- **ORM**: SQLAlchemy
- **API Docs**: Swagger/OpenAPI 3.0
- **CLI**: Python argparse

## 📦 Dependencies

```
fastapi>=0.95.0
uvicorn[standard]>=0.20.0
pydantic>=1.10.0
sqlalchemy>=1.4.0
psycopg2-binary>=2.9.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
requests>=2.31.0
```

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

## 📊 Example Usage

### cURL Examples

```bash
# Register
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "email": "test@example.com", "password": "Test123456"}'

# Login
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "Test123456"}' \
  | jq -r '.access_token')

# Create log
curl -X POST "http://localhost:8000/api/v1/logs/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"level": "info", "message": "Test log"}'

# List reports
curl -X GET "http://localhost:8000/api/v1/reports/?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

## 🚀 Production Deployment

1. **Use strong SECRET_KEY**:
   ```bash
   openssl rand -hex 32
   ```

2. **Configure PostgreSQL properly**
3. **Enable HTTPS**
4. **Set up monitoring** (Prometheus/Grafana)
5. **Configure rate limiting**
6. **Use production WSGI server** (Gunicorn + Uvicorn workers)

```bash
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📖 Additional Documentation

- [API Usage Guide](../docs/API_USAGE_GUIDE.md) - Detailed API documentation
- [Quick Start Guide](../docs/QUICK_START_API.md) - 5-minute quick start
- [Main README](../README.md) - Project overview

## 🐛 Troubleshooting

### API won't start
```bash
lsof -i :8000  # Check if port is in use
```

### Database connection error
```bash
pg_isready -U dafu -d dafu  # Check PostgreSQL
docker ps | grep postgres   # Check Docker container
```

### Dependencies issues
```bash
pip install -r requirements.txt --upgrade
```

## 📝 License

AGPL-3.0 - See LICENSE file

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b api/fastapi/feature/your-feature/v1`
3. Commit changes: `git commit -am 'Add feature'`
4. Push branch: `git push origin api/fastapi/feature/your-feature/v1`
5. Create Pull Request

## 📞 Support

- Issues: https://github.com/MasterFabric/dafu/issues
- Documentation: `/docs` directory
- API Docs: http://localhost:8000/docs

---

**Built with ❤️ using FastAPI and Python**

