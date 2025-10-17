# DAFU CLI - Integrated API Commands

## 🎉 Overview

The main `./dafu` CLI now includes **full API integration**! You can manage authentication, logs, reports, and products directly from the DAFU CLI.

---

## 🚀 Quick Start

### Start in Interactive Mode

```bash
./dafu
```

This will open the interactive DAFU CLI where you can type commands.

### Run Single Commands

```bash
./dafu <command> <subcommand> [args]
```

---

## 📋 Available Commands

### 🔐 Authentication & User Management

```bash
# Interactive mode
dafu> auth login
dafu> auth logout
dafu> auth whoami
dafu> auth register

# Single command mode
./dafu auth login
./dafu auth logout
./dafu auth whoami
./dafu auth register
```

**What they do**:
- `auth login` - Login to DAFU API (interactive: asks username/password)
- `auth logout` - Logout and clear session
- `auth whoami` - Show current logged-in user information
- `auth register` - Register new user (uses API endpoint)

---

### 📋 Logs Management

```bash
# Interactive mode
dafu> logs list
dafu> logs list 20
dafu> logs stats
dafu> logs stats 48

# Single command mode
./dafu logs list
./dafu logs list 20
./dafu logs stats 24
```

**What they do**:
- `logs list [limit]` - List recent logs (default: 20)
- `logs stats [hours]` - Show log statistics (default: 24 hours)

---

### 📊 Reports Management

```bash
# Interactive mode
dafu> reports list
dafu> reports list 10
dafu> reports create
dafu> reports view 1
dafu> reports stats

# Single command mode
./dafu reports list
./dafu reports create
./dafu reports view 1
./dafu reports stats
```

**What they do**:
- `reports list [limit]` - List your reports
- `reports create` - Create new fraud detection report (interactive)
- `reports view <id>` - View detailed report information
- `reports stats` - Show report statistics

---

### 🛍️ Products Management

```bash
# Interactive mode
dafu> products list
dafu> products list 50
dafu> products high-risk
dafu> products stats

# Single command mode
./dafu products list
./dafu products high-risk
./dafu products stats
```

**What they do**:
- `products list [limit]` - List products
- `products high-risk [limit]` - List high-risk products
- `products stats` - Show product statistics

---

### 🤖 ML Models (Existing)

```bash
dafu> fraud-detection
dafu> models
dafu> ml
```

**What they do**:
- Run interactive fraud detection models (existing functionality)

---

### 🐳 Docker Services (Existing)

```bash
dafu> docker up
dafu> docker down
dafu> docker status
dafu> docker logs
```

**What they do**:
- Manage Docker services (existing functionality)

---

## 🎯 Complete Workflow Example

### Interactive Mode Session

```bash
$ ./dafu

╔════════════════════════════════════════════════════════════╗
║  ____    _    _____ _   _                                  ║
║ |  _ \  / \  |  ___| | | |                                 ║
║ | | | |/ _ \ | |_  | | | |                                 ║
║ | |_| / ___ \|  _| | |_| |                                 ║
║ |____/_/   \_\_|    \___/                                  ║
║                                                            ║
║ Data Analytics Functional Utilities - Interactive CLI     ║
║ Enterprise Fraud Detection & Analytics Platform           ║
╚════════════════════════════════════════════════════════════╝

Welcome to DAFU Interactive CLI!
Type 'help' for available commands or 'exit' to quit

dafu> help
... shows all commands ...

dafu> auth login
Username: myuser
Password: ********
✓ Logged in as 'myuser'
ℹ Token expires in: 24 hours

dafu> auth whoami
============================================================
              Current User Information                  
============================================================
  ID:         1
  Username:   myuser
  Email:      user@example.com
  Role:       user
  Status:     active

dafu> logs list 5
============================================================
                Recent Logs (Last 5)                    
============================================================
ID | Level | Message                    | Time           
----------------------------------------------------------
5  | INFO  | User logged in              | 2025-10-17 12:00
...

dafu> reports list
============================================================
                Your Reports (Last 5)                   
============================================================
ID | Name              | Type            | Status    | Progress
----------------------------------------------------------------
1  | My Fraud Report   | fraud_detection | completed | 100%
...

dafu> products stats
============================================================
                Product Statistics                     
============================================================
  Total Products:   150
  High Risk:        12
  Low Stock:        8
  ...

dafu> exit
👋 Thank you for using DAFU Platform!
Goodbye!
```

---

## 🔑 Prerequisites

### 1. API Must Be Running

Before using API commands, start the API:

```bash
cd fraud_detection
./start_api.sh
```

Or in another terminal:
```bash
cd fraud_detection
source venv/bin/activate
PYTHONPATH=$(pwd)/src uvicorn api.main:app --host 0.0.0.0 --port 8000 &
```

### 2. User Account

You need a registered user. First time:

```bash
# Method 1: Via DAFU CLI
./dafu auth register

# Method 2: Via curl
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "myuser",
    "email": "user@example.com",
    "password": "mypassword"
  }'
```

---

## 💻 Usage Examples

### Single Command Mode (Non-Interactive)

```bash
# Login
./dafu auth login

# Check who is logged in
./dafu auth whoami

# List logs
./dafu logs list 10

# List reports
./dafu reports list

# View specific report
./dafu reports view 1

# List products
./dafu products list 20

# Show statistics
./dafu products stats
./dafu reports stats

# Logout
./dafu auth logout
```

### Combined with Other Commands

```bash
# Start Docker services, then check logs
./dafu docker up
./dafu logs list

# Run ML models, then view reports
./dafu fraud-detection
./dafu reports list

# Check system status, then products
./dafu status
./dafu products stats
```

---

## 🔧 How It Works

1. **Command Routing**: `./dafu` script routes commands to appropriate handlers
2. **API Commands**: `auth`, `logs`, `reports`, `products` → Python CLI (`src.api.cli`)
3. **ML Commands**: `fraud-detection`, `models`, `ml` → ML models
4. **Docker Commands**: `docker <cmd>` → `start.sh` script
5. **System Commands**: `status`, `version`, `info` → System info functions

---

## 📚 Architecture

```
┌─────────────────────────────────────────────┐
│           ./dafu (Main CLI)                 │
│  Interactive & Single Command Mode          │
└──────────────┬──────────────────────────────┘
               │
      ┌────────┴────────┬─────────┬───────────┐
      │                 │         │           │
┌─────▼─────┐  ┌────────▼─────┐  │  ┌────────▼────────┐
│API Commands│  │ ML Commands  │  │  │Docker Commands  │
│(Python CLI)│  │(Python ML)   │  │  │  (start.sh)     │
└────────────┘  └──────────────┘  │  └─────────────────┘
     │                             │
     ▼                    ┌────────▼────────┐
┌────────────┐            │System Commands  │
│ FastAPI    │            │(status/version) │
│  Backend   │            └─────────────────┘
└────────────┘
```

---

## 🎯 Key Features

✅ **Unified CLI**: All DAFU features in one command
✅ **Interactive Mode**: Type commands interactively
✅ **Single Command Mode**: Run one-off commands
✅ **Auto VirtualEnv**: Automatically activates Python environment
✅ **Color Output**: Beautiful, readable output
✅ **Session Management**: Login once, use everywhere
✅ **Error Handling**: Graceful error messages

---

## 📝 Notes

1. **API Dependency**: API commands require the API to be running
2. **Session File**: Login creates `~/.dafu_session` for authentication
3. **Virtual Environment**: Automatically managed by the script
4. **Python CLI**: Uses `src.api.cli` module in fraud_detection
5. **Non-blocking**: API commands don't block other CLI features

---

## 🆘 Troubleshooting

### "Failed to connect to localhost port 8000"

**Solution**: Start the API first:
```bash
cd fraud_detection
./start_api.sh
```

### "Virtual environment not found"

**Solution**: The script will create it automatically on first API command use.

### "You must be logged in"

**Solution**: Login first:
```bash
./dafu auth login
```

---

## 🎉 Summary

Now you can use **one unified CLI** for:
- ✅ Authentication and user management
- ✅ System logs viewing and analytics
- ✅ Fraud detection reports
- ✅ Product risk management
- ✅ ML model execution
- ✅ Docker service management
- ✅ System information

**Everything from the `./dafu` command!** 🚀

---

**Version**: 2.0.0 (with API integration)
**Updated**: 2025-10-17
**Status**: ✅ Production Ready

