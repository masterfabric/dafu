# DAFU CLI - Step-by-Step Usage Guide

## 🎯 Prerequisites

Before using CLI, you need:
1. ✅ API running (http://localhost:8000)
2. ✅ PostgreSQL running (Docker or local)
3. ✅ Virtual environment activated

---

## 🚀 Step-by-Step CLI Usage

### Step 1: Start API and Database

```bash
# Navigate to project directory
cd /Users/furkancankaya/Documents/GitHub/dafu/fraud_detection

# Activate virtual environment
source venv/bin/activate

# Start PostgreSQL with Docker (if not running)
docker run -d --name dafu-postgres \
  -e POSTGRES_USER=dafu \
  -e POSTGRES_PASSWORD=dafu_secure_password \
  -e POSTGRES_DB=dafu \
  -p 5432:5432 \
  postgres:15-alpine

# Wait for PostgreSQL to be ready
sleep 5

# Initialize database
python -c "from src.api.database import init_db; init_db()"

# Start API
PYTHONPATH=$(pwd)/src uvicorn api.main:app --host 0.0.0.0 --port 8000 &

# Wait for API to start
sleep 4
```

---

### Step 2: Register User (First Time)

Since `auth register` is interactive, use API:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "myusername",
    "email": "myemail@example.com",
    "password": "mypassword123",
    "full_name": "My Full Name"
  }'
```

**Expected Output**:
```json
{
  "id": 1,
  "username": "myusername",
  "email": "myemail@example.com",
  "full_name": "My Full Name",
  "role": "user",
  "status": "active",
  ...
}
```

---

### Step 3: Login and Get Token

```bash
# Login via API and get token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "myusername",
    "password": "mypassword123"
  }' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Verify token was received
echo "Token received: ${TOKEN:0:50}..."
```

---

### Step 4: Create CLI Session File

```bash
# Create session file for CLI
echo "{
  \"token\": \"$TOKEN\",
  \"username\": \"myusername\",
  \"expires_at\": 9999999999,
  \"saved_at\": \"$(date -u +%Y-%m-%dT%H:%M:%S)\"
}" > ~/.dafu_session

# Verify session file
cat ~/.dafu_session | python3 -m json.tool
```

**Expected Output**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "username": "myusername",
  "expires_at": 9999999999,
  "saved_at": "2025-10-17T12:00:00"
}
```

---

### Step 5: Use CLI Commands

Now you can use all CLI commands!

#### View Current User
```bash
python -m src.api.cli auth whoami
```

**Output**:
```
============================================================
              Current User Information                  
============================================================

  ID:         1
  Username:   myusername
  Email:      myemail@example.com
  Full Name:  My Full Name
  Role:       user
  Status:     active
```

#### List Logs
```bash
python -m src.api.cli logs list 10
```

#### View Reports
```bash
python -m src.api.cli reports list
```

#### Check Statistics
```bash
python -m src.api.cli reports stats
python -m src.api.cli products stats
```

---

## 📝 All Available CLI Commands

### Authentication Commands
```bash
python -m src.api.cli auth whoami           # Show current user
python -m src.api.cli auth logout           # Logout (clears session)
```

### Log Commands
```bash
python -m src.api.cli logs list [limit]     # List logs (default: 20)
python -m src.api.cli logs stats [hours]    # Log statistics (default: 24h)
```

### Report Commands
```bash
python -m src.api.cli reports list [limit]  # List reports
python -m src.api.cli reports view <id>     # View report details
python -m src.api.cli reports stats         # Report statistics
```

### Product Commands
```bash
python -m src.api.cli products list [limit]         # List products
python -m src.api.cli products high-risk [limit]    # High-risk products
python -m src.api.cli products stats                # Product statistics
```

### Help
```bash
python -m src.api.cli help                  # Show help menu
```

---

## 🔄 Quick Login Script

Save this as `cli_login.sh`:

```bash
#!/bin/bash

cd /Users/furkancankaya/Documents/GitHub/dafu/fraud_detection
source venv/bin/activate

# Get credentials
read -p "Username: " USERNAME
read -sp "Password: " PASSWORD
echo ""

# Login and get token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\"}" | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

# Check if login successful
if [ -z "$TOKEN" ]; then
    echo "❌ Login failed! Incorrect username or password."
    exit 1
fi

# Create session file
echo "{\"token\": \"$TOKEN\", \"username\": \"$USERNAME\", \"expires_at\": 9999999999, \"saved_at\": \"$(date -u +%Y-%m-%dT%H:%M:%S)\"}" > ~/.dafu_session

echo "✅ Login successful!"
echo "You can now use CLI commands:"
echo "  python -m src.api.cli auth whoami"
echo "  python -m src.api.cli logs list"
echo "  python -m src.api.cli reports list"
```

**Usage**:
```bash
chmod +x cli_login.sh
./cli_login.sh
```

---

## 💡 Important Notes

1. **Session File**: Located at `~/.dafu_session`
2. **Token Expiry**: Valid for 24 hours
3. **Permissions**: Some commands require analyst/admin role
4. **API Dependency**: API must be running for CLI to work
5. **Base URL**: Default is `http://localhost:8000`

---

## 🐛 Troubleshooting

### Error: "You must be logged in to use this command"

**Solution**: Create session file using Step 3 above.

### Error: "Failed to connect to localhost port 8000"

**Solution**: Start the API first:
```bash
PYTHONPATH=/Users/furkancankaya/Documents/GitHub/dafu/fraud_detection/src \
  uvicorn api.main:app --host 0.0.0.0 --port 8000 &
```

### Error: "Operation not permitted. Required roles: admin, analyst"

**Solution**: This command requires elevated permissions. Your user role is "user", but the command needs "analyst" or "admin" role.

---

## 📋 Complete Workflow Example

```bash
# 1. Setup environment
cd /Users/furkancankaya/Documents/GitHub/dafu/fraud_detection
source venv/bin/activate

# 2. Start services (if not running)
docker start dafu-postgres || docker run -d --name dafu-postgres \
  -e POSTGRES_USER=dafu -e POSTGRES_PASSWORD=dafu_secure_password \
  -e POSTGRES_DB=dafu -p 5432:5432 postgres:15-alpine
  
PYTHONPATH=$(pwd)/src uvicorn api.main:app --host 0.0.0.0 --port 8000 &
sleep 4

# 3. Register user (first time only)
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "email": "user@example.com", "password": "pass123"}'

# 4. Login and create session
./cli_login.sh
# Enter: user1 / pass123

# 5. Use CLI commands
python -m src.api.cli auth whoami
python -m src.api.cli logs list
python -m src.api.cli reports list
python -m src.api.cli products stats

# 6. Logout when done
python -m src.api.cli auth logout
```

---

## 🎉 You're Ready!

Your CLI is now configured and ready to use!

**Most Common Commands**:
- `python -m src.api.cli auth whoami` - Check current user
- `python -m src.api.cli logs list` - View logs
- `python -m src.api.cli reports list` - View reports
- `python -m src.api.cli help` - Show all commands

**Happy coding!** 🚀

