# 🎯 DAFU CLI - How to Use (Simple Guide)

## ✅ What Changed

Your `./dafu` CLI now includes **API commands**! 

Before: Only fraud-detection, docker, status commands
**Now**: + auth, logs, reports, products commands! 🎉

---

## 🚀 Quick Start (3 Steps)

### Step 1: Start the API

**Terminal 1** (keep this running):
```bash
cd fraud_detection
./start_api.sh
```

Wait for: `INFO: Uvicorn running on http://0.0.0.0:8000`

### Step 2: Start DAFU CLI

**Terminal 2**:
```bash
./dafu
```

You'll see the DAFU interactive CLI.

### Step 3: Login

```bash
dafu> auth login
```

**First time?** Register first via API:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "myuser",
    "email": "my@email.com",
    "password": "mypass123"
  }'
```

Then login with those credentials.

---

## 📋 All New Commands

### Authentication
```bash
./dafu auth login      # Login (asks username/password)
./dafu auth whoami     # Show current user
./dafu auth logout     # Logout
```

### Logs
```bash
./dafu logs list       # List recent logs
./dafu logs list 50    # List last 50 logs
./dafu logs stats      # 24h statistics
./dafu logs stats 48   # 48h statistics
```

### Reports
```bash
./dafu reports list    # Your reports
./dafu reports create  # Create new report
./dafu reports view 1  # View report #1
./dafu reports stats   # Statistics
```

### Products
```bash
./dafu products list       # All products
./dafu products high-risk  # High-risk only
./dafu products stats      # Statistics
```

---

## 🎯 Example Usage

### Interactive Mode

```bash
$ ./dafu

dafu> help                  # See all commands
dafu> auth login            # Login
dafu> auth whoami           # Check user
dafu> logs list 10          # View logs
dafu> reports list          # View reports
dafu> products stats        # Product stats
dafu> exit                  # Exit
```

### Single Command Mode

```bash
./dafu auth login
./dafu auth whoami
./dafu logs stats
./dafu products high-risk
```

---

## 🔧 How It Works

```
You type:  ./dafu auth login
           ↓
dafu script receives: "auth" "login"
           ↓
Calls: execute_api_command("auth", "login")
           ↓
Activates: fraud_detection/venv
           ↓
Runs: python -m src.api.cli auth login
           ↓
Python CLI handles login interactively
           ↓
Creates: ~/.dafu_session
           ↓
Returns to dafu prompt
```

---

## 📝 Important Notes

1. **API Must Be Running**: Start with `cd fraud_detection && ./start_api.sh`
2. **Session File**: Login creates `~/.dafu_session`
3. **Auto Setup**: Virtual environment created automatically if missing
4. **Works Both Ways**: Interactive mode AND single commands
5. **Existing Commands**: All old commands (fraud-detection, docker) still work!

---

## 🎓 Complete Workflow Example

```bash
# Terminal 1: Start API
cd fraud_detection
./start_api.sh

# Terminal 2: Use CLI
./dafu

# In DAFU CLI:
dafu> auth login
Username: admin
Password: ********
✓ Logged in

dafu> auth whoami
  ID:         1
  Username:   admin
  Role:       admin
  Status:     active

dafu> logs list 5
ID | Level | Message              | Time
--------------------------------------------
5  | INFO  | User logged in       | 2025-10-17 12:00
4  | INFO  | Report completed     | 2025-10-17 11:55
...

dafu> reports create
Report Name: Daily Fraud Scan
Report Type: fraud_detection
Description: Automated daily scan
✓ Report created with ID: 5

dafu> reports list
ID | Name              | Type            | Status    | Progress
----------------------------------------------------------------
5  | Daily Fraud Scan  | fraud_detection | pending   | 0%
...

dafu> products high-risk 5
ID  | SKU       | Name          | Risk Score | Incidents
---------------------------------------------------------
15  | PHONE-X   | Phone Model X | 0.85       | 12
...

dafu> exit
👋 Thank you for using DAFU Platform!
```

---

## 🆘 Troubleshooting

### "Failed to connect to localhost port 8000"

**Problem**: API is not running
**Solution**:
```bash
cd fraud_detection
./start_api.sh
```

### "You must be logged in"

**Problem**: No active session
**Solution**:
```bash
./dafu auth login
```

### "Virtual environment not found"

**Don't worry!** The script will create it automatically on first API command.

---

## 🎉 Summary

**What you can do now**:

```bash
./dafu                    # Everything in one CLI!

# API Commands (NEW!)
./dafu auth login         ← Login to API
./dafu auth whoami        ← Show user info
./dafu logs list          ← View system logs
./dafu reports list       ← View reports
./dafu products stats     ← Product statistics

# Existing Commands
./dafu fraud-detection    ← Run ML models
./dafu docker up          ← Start Docker
./dafu status             ← System status
```

**One CLI. All features. Simple.** 🚀

---

**For detailed documentation**: See `docs/DAFU_CLI_INTEGRATED.md`

