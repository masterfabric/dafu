# DAFU API - Usage Examples

## 📖 Table of Contents

1. [Quick Start](#quick-start)
2. [Authentication Examples](#authentication-examples)
3. [Log Management](#log-management)
4. [Report Generation](#report-generation)
5. [Product Management](#product-management)
6. [Python Client Examples](#python-client-examples)
7. [Real-World Scenarios](#real-world-scenarios)

---

## 🚀 Quick Start

### Start the API

```bash
cd fraud_detection
./start_api.sh
```

After API starts: http://localhost:8000

---

## 🔐 Authentication Examples

### 1. New User Registration

#### With CLI:
```bash
python -m src.api.cli auth register
```

**Screen output:**
```
====================================================================
                      User Registration                            
====================================================================

Username: johndoe
Email: john@company.com
Password: ********
Confirm Password: ********
Full Name (optional): John Doe
Company (optional): ACME Corp
Phone (optional): +1-555-0123

✓ User 'johndoe' registered successfully!
ℹ You can now login with your credentials
```

#### With API:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@company.com",
    "password": "SecurePass123!",
    "full_name": "John Doe",
    "company": "ACME Corp",
    "phone": "+1-555-0123"
  }'
```

**Response:**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@company.com",
  "full_name": "John Doe",
  "role": "user",
  "status": "active",
  "created_at": "2025-10-17T10:30:00Z",
  "last_login": null,
  "company": "ACME Corp",
  "phone": "+1-555-0123"
}
```

### 2. Login

#### With CLI:
```bash
python -m src.api.cli auth login
```

**Screen output:**
```
====================================================================
                          User Login                               
====================================================================

Username or Email: johndoe
Password: ********

✓ Logged in as 'johndoe'
ℹ Token expires in: 24 hours
```

#### With API:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "SecurePass123!"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### 3. View User Information

#### With CLI:
```bash
python -m src.api.cli auth whoami
```

**Screen output:**
```
====================================================================
                Current User Information                           
====================================================================

  ID:         1
  Username:   johndoe
  Email:      john@company.com
  Full Name:  John Doe
  Role:       user
  Status:     active
  Company:    ACME Corp
  Created:    2025-10-17T10:30:00Z
  Last Login: 2025-10-17T11:00:00Z
```

---

## 📋 Log Management

### 1. Creating Logs

#### With Python:
```python
from src.api.cli_client import get_client

client = get_client()

# Info log
log = client.create_log(
    level="info",
    message="User successfully logged in",
    module="authentication",
    endpoint="/api/v1/auth/login",
    method="POST",
    status_code=200,
    response_time_ms=45.2
)

# Error log
error_log = client.create_log(
    level="error",
    message="Database connection failed",
    module="database",
    metadata={
        "error_code": "DB001",
        "retry_count": 3
    },
    stack_trace="Traceback (most recent call last)..."
)
```

### 2. Viewing Log List

#### With CLI:
```bash
python -m src.api.cli logs list 20
```

**Screen output:**
```
====================================================================
                   Recent Logs (Last 20)                          
====================================================================

ID  | Level    | Message                              | Time           
--------------------------------------------------------------------
15  | INFO     | User logged in successfully          | 2025-10-17 11:00
14  | WARNING  | API rate limit approaching           | 2025-10-17 10:55
13  | INFO     | Report generation completed          | 2025-10-17 10:50
12  | ERROR    | Database query timeout               | 2025-10-17 10:45
11  | INFO     | New product created: SKU-12345       | 2025-10-17 10:40
```

### 3. Log Statistics

#### With CLI:
```bash
python -m src.api.cli logs stats 24
```

**Screen output:**
```
====================================================================
          Log Statistics (Last 24 hours)                          
====================================================================

  Total Logs:   1,245
  Error Rate:   2.3%
  Avg Response: 45.67ms

By Level:
    DEBUG          125
    INFO           980
    WARNING         95
    ERROR           35
    CRITICAL        10
```

---

## 📊 Report Generation

### 1. Creating Fraud Detection Report

#### With CLI:
```bash
python -m src.api.cli reports create
```

**Screen output:**
```
====================================================================
                     Create New Report                            
====================================================================

Report Name: October Fraud Analysis
Report Type (fraud_detection/analytics/risk_analysis): fraud_detection
Description (optional): Monthly fraud detection analysis for October 2025

✓ Report created with ID: 7
ℹ Status: pending
```

#### With Python:
```python
from src.api.cli_client import get_client

client = get_client()

report = client.create_report(
    name="October Fraud Analysis",
    report_type="fraud_detection",
    description="Monthly fraud detection analysis for October 2025",
    config={
        "contamination": 0.1,
        "models": ["isolation_forest", "lstm", "xgboost"],
        "threshold": 0.7
    },
    filters={
        "start_date": "2025-10-01",
        "end_date": "2025-10-31",
        "min_amount": 100,
        "categories": ["electronics", "jewelry"]
    }
)

print(f"Report ID: {report['id']}")
print(f"Status: {report['status']}")
```

### 2. Report List

#### With CLI:
```bash
python -m src.api.cli reports list
```

**Screen output:**
```
====================================================================
                   Your Reports (Last 20)                         
====================================================================

ID | Name                      | Type             | Status     | Progress | Created
--------------------------------------------------------------------------------------
7  | October Fraud Analysis    | fraud_detection  | completed  | 100%     | 2025-10-17 10:00
6  | Q3 Risk Assessment        | risk_analysis    | completed  | 100%     | 2025-10-15 14:30
5  | Weekly Analytics          | analytics        | failed     | 45%      | 2025-10-14 09:15
4  | Product Risk Scoring      | fraud_detection  | completed  | 100%     | 2025-10-13 16:20
```

### 3. Report Details

#### With CLI:
```bash
python -m src.api.cli reports view 7
```

**Screen output:**
```
====================================================================
        Report Details - October Fraud Analysis                   
====================================================================

  ID:           7
  Name:         October Fraud Analysis
  Type:         fraud_detection
  Status:       completed
  Progress:     100%
  Created:      2025-10-17T10:00:00Z
  Completed:    2025-10-17T10:15:32Z
  Processing:   932.45s
  Records:      15,420

Results:
{
  "summary": "Fraud detection completed successfully",
  "fraud_detected": 154,
  "fraud_rate": 1.0,
  "high_risk_transactions": 234,
  "total_loss_prevented": 45678.90
}
```

---

## 🛍️ Product Management

### 1. Adding Products

#### With Python:
```python
from src.api.cli_client import get_client

client = get_client()

product = client.create_product(
    sku="LAPTOP-M1-PRO-16",
    name="MacBook Pro 16-inch M1",
    description="High-performance laptop with M1 Pro chip",
    price=2499.99,
    currency="USD",
    cost=1800.00,
    category="Electronics",
    subcategory="Laptops",
    brand="Apple",
    tags=["laptop", "apple", "m1", "professional"],
    stock_quantity=50,
    low_stock_threshold=10
)

print(f"Product created: {product['name']} (ID: {product['id']})")
```

### 2. High-Risk Products

#### With CLI:
```bash
python -m src.api.cli products high-risk 10
```

**Screen output:**
```
====================================================================
                  High-Risk Products (10)                         
====================================================================

ID  | SKU            | Name                  | Risk Score | Incidents
-----------------------------------------------------------------------
15  | PHONE-XYZ-128  | Smartphone XYZ 128GB  | 0.85       | 12
23  | WATCH-LUX-001  | Luxury Watch Model 1  | 0.78       | 8
31  | JEWELRY-RING-5 | Diamond Ring 5ct      | 0.72       | 6
```

### 3. Update Product Risk

#### With Python:
```python
from src.api.cli_client import get_client

client = get_client()

# Update fraud risk
updated = client.update_product_fraud_risk(
    product_id=15,
    fraud_risk_score=0.85,
    high_risk=True,
    fraud_incidents=12,
    chargeback_rate=0.15
)

print(f"Risk score updated for: {updated['name']}")
print(f"New risk score: {updated['fraud_risk_score']}")
```

### 4. Stock Update

```python
# Update stock
result = client.update_stock(product_id=15, quantity=75)

print(f"Stock updated from {result['old_quantity']} to {result['new_quantity']}")
```

---

## 🐍 Python Client Examples

### Complete Workflow Example

```python
from src.api.cli_client import DAFUClient, SessionManager

# 1. Create client
client = DAFUClient(base_url="http://localhost:8000")

# 2. Register user
try:
    user = client.register(
        username="fraud_analyst",
        email="analyst@company.com",
        password="SecurePass123!",
        full_name="Fraud Analyst",
        company="Security Inc."
    )
    print(f"✓ Registered: {user['username']}")
except Exception as e:
    print(f"Registration failed: {e}")

# 3. Login
login_result = client.login("fraud_analyst", "SecurePass123!")
print(f"✓ Logged in, token expires in {login_result['expires_in']//3600} hours")

# 4. Get user info
current_user = client.get_current_user()
print(f"✓ Current user: {current_user['username']} ({current_user['role']})")

# 5. Create log
log = client.create_log(
    level="info",
    message="Started fraud analysis workflow",
    module="fraud_detection",
    metadata={"workflow_id": "FD-2025-10-17-001"}
)
print(f"✓ Log created: ID {log['id']}")

# 6. Create report
report = client.create_report(
    name="Daily Fraud Scan",
    report_type="fraud_detection",
    description="Automated daily fraud detection",
    config={
        "contamination": 0.05,
        "models": ["isolation_forest"]
    }
)
print(f"✓ Report created: ID {report['id']}, Status: {report['status']}")

# 7. Check products
high_risk_products = client.get_high_risk_products(limit=5)
print(f"✓ Found {len(high_risk_products)} high-risk products")

for product in high_risk_products:
    print(f"  - {product['name']}: Risk {product['fraud_risk_score']:.2f}")

# 8. Get statistics
log_stats = client.get_log_stats(hours=24)
report_stats = client.get_report_stats()
product_stats = client.get_product_stats()

print(f"\n📊 Statistics:")
print(f"  Logs (24h): {log_stats['total_logs']}")
print(f"  Reports: {report_stats['total_reports']}")
print(f"  Products: {product_stats['total_products']}")
print(f"  High Risk: {product_stats['high_risk_count']}")
```

---

## 🌍 Real-World Scenarios

### Scenario 1: E-commerce Fraud Detection Pipeline

```python
from src.api.cli_client import get_client
import time

client = get_client()

# 1. Create daily report
print("Creating daily fraud report...")
report = client.create_report(
    name=f"Daily Fraud Report - {time.strftime('%Y-%m-%d')}",
    report_type="fraud_detection",
    config={
        "contamination": 0.05,
        "models": ["isolation_forest", "lstm"],
        "threshold": 0.7
    },
    filters={
        "start_date": time.strftime('%Y-%m-%d'),
        "min_amount": 50
    }
)

# 2. Wait for report completion
report_id = report['id']
while True:
    report = client.get_report(report_id)
    print(f"Progress: {report['progress']:.0f}%")
    
    if report['status'] == 'completed':
        break
    elif report['status'] == 'failed':
        print(f"Report failed: {report['error_message']}")
        break
    
    time.sleep(5)

# 3. Analyze results
if report['status'] == 'completed':
    results = report['results']
    print(f"\n✓ Report completed!")
    print(f"  Total records: {report['total_records']}")
    print(f"  Frauds detected: {results['fraud_detected']}")
    print(f"  Fraud rate: {results['fraud_rate']:.2%}")
    
    # 4. Check high-risk products
    high_risk = client.get_high_risk_products(limit=10)
    
    # 5. Update risk scores
    for product in high_risk:
        if product['fraud_incidents'] > 5:
            client.update_product_fraud_risk(
                product_id=product['id'],
                fraud_risk_score=min(product['fraud_risk_score'] + 0.1, 1.0),
                high_risk=True
            )
    
    # 6. Save log
    client.create_log(
        level="info",
        message=f"Daily fraud detection completed: {results['fraud_detected']} frauds detected",
        module="fraud_pipeline",
        metadata={
            "report_id": report_id,
            "fraud_count": results['fraud_detected'],
            "total_records": report['total_records']
        }
    )
```

### Scenario 2: Product Risk Analysis and Alert System

```python
from src.api.cli_client import get_client

client = get_client()

# 1. Get all products
products = client.get_products(limit=1000)

# 2. Perform risk analysis
high_risk_products = []
warnings = []

for product in products:
    # Low stock + high risk combination
    if product['stock_quantity'] <= product['low_stock_threshold'] and product['high_risk']:
        warnings.append({
            'type': 'critical',
            'product': product['name'],
            'reason': 'Low stock + High fraud risk'
        })
    
    # High chargeback rate
    if product['chargeback_rate'] > 0.1:
        warnings.append({
            'type': 'warning',
            'product': product['name'],
            'reason': f'High chargeback rate: {product["chargeback_rate"]:.1%}'
        })
    
    # Many fraud incidents
    if product['fraud_incidents'] > 10:
        high_risk_products.append(product)

# 3. Reporting
print(f"⚠️  Found {len(warnings)} warnings:")
for warning in warnings:
    print(f"  [{warning['type'].upper()}] {warning['product']}: {warning['reason']}")

# 4. Create report for high-risk products
if high_risk_products:
    report = client.create_report(
        name="High-Risk Products Analysis",
        report_type="risk_analysis",
        description=f"Analysis of {len(high_risk_products)} high-risk products",
        config={
            "product_ids": [p['id'] for p in high_risk_products]
        }
    )
    print(f"\n✓ Risk analysis report created: ID {report['id']}")

# 5. Save log
client.create_log(
    level="warning" if warnings else "info",
    message=f"Product risk analysis completed: {len(warnings)} warnings, {len(high_risk_products)} high-risk products",
    module="risk_analysis",
    metadata={
        "total_products": len(products),
        "warnings": len(warnings),
        "high_risk_count": len(high_risk_products)
    }
)
```

---

## 📝 Notes

- All examples have been tested and are working
- For API documentation: http://localhost:8000/docs
- For CLI help: `python -m src.api.cli help`
- For Python client documentation: `help(DAFUClient)`

---

## 🎓 More Information

- [API Usage Guide](../docs/API_USAGE_GUIDE.md)
- [Quick Start Guide](../docs/QUICK_START_API.md)
- [API README](./API_README.md)

---

**Happy coding! 🚀**

