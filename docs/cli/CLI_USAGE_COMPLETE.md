# DAFU CLI - Complete Usage Guide

## ✅ API Commands Integrated!

The main `./dafu` CLI now includes **full API integration**! All authentication, logs, reports, and product management is available directly from the DAFU CLI.

---

## 🚀 How to Use

### Method 1: Interactive Mode (Recommended)

```bash
./dafu
```

This opens an interactive session:

```
dafu> help           # Show all commands
dafu> auth login     # Login to API
dafu> logs list      # View logs
dafu> reports list   # View reports
dafu> products stats # Product statistics
dafu> exit           # Exit CLI
```

### Method 2: Single Command Mode

```bash
./dafu auth whoami
./dafu logs list 20
./dafu reports stats
./dafu products high-risk
```

---

## 📋 Complete Command Reference

### 🔐 Authentication Commands

```bash
# Login (interactive: prompts for username/password)
./dafu auth login

# Show current user info
./dafu auth whoami

# Logout
./dafu auth logout

# Register (via API endpoint)
./dafu auth register
```

### 📋 Logs Commands

```bash
# List recent logs (default: 20)
./dafu logs list
./dafu logs list 50

# Show log statistics (default: 24 hours)
./dafu logs stats
./dafu logs stats 48
```

### 📊 Reports Commands

```bash
# List your reports
./dafu reports list
./dafu reports list 10

# Create new report (interactive)
./dafu reports create

# View report details
./dafu reports view 1

# Show report statistics
./dafu reports stats
```

### 🛍️ Products Commands

```bash
# List products
./dafu products list
./dafu products list 100

# List high-risk products
./dafu products high-risk
./dafu products high-risk 20

# Show product statistics
./dafu products stats
```

### 🤖 ML Model Commands (Existing)

```bash
# Run fraud detection models
./dafu fraud-detection
./dafu models
./dafu ml
```

### 🐳 Docker Commands (Existing)

```bash
# Docker service management
./dafu docker up
./dafu docker down
./dafu docker status
./dafu docker logs
```

### 📊 System Commands (Existing)

```bash
# System information
./dafu status
./dafu version
./dafu info
```

---

## 🎯 Step-by-Step: First Time Setup

### Step 1: Start API

```bash
# In a separate terminal
cd fraud_detection
./start_api.sh
```

Keep this running in the background.

### Step 2: Start DAFU CLI

```bash
# In your main terminal
./dafu
```

### Step 3: Register User (First Time Only)

```bash
dafu> auth register
```

Or via curl:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "email": "your@email.com",
    "password": "your_password"
  }'
```

### Step 4: Login

```bash
dafu> auth login
Username: your_username
Password: ********
✓ Logged in as 'your_username'
```

This creates `~/.dafu_session` for persistent authentication.

### Step 5: Use API Commands

```bash
dafu> auth whoami
dafu> logs list
dafu> reports list
dafu> products stats
```

---

## 💡 Example Session

```bash
$ ./dafu

╔════════════════════════════════════════════════════════════╗
║  ____    _    _____ _   _                                  ║
║ Data Analytics Functional Utilities - Interactive CLI     ║
╚════════════════════════════════════════════════════════════╝

Welcome to DAFU Interactive CLI!
Type 'help' for available commands or 'exit' to quit

dafu> auth login
Username: admin
Password: ********
✓ Logged in as 'admin'

dafu> auth whoami
============================================================
              Current User Information                  
============================================================
  ID:         1
  Username:   admin
  Email:      admin@company.com
  Role:       admin
  Status:     active

dafu> logs stats 24
============================================================
          Log Statistics (Last 24 hours)                          
============================================================
  Total Logs:   245
  Error Rate:   2.1%

dafu> reports list
============================================================
                Your Reports (Last 5)                   
============================================================
ID | Name              | Type            | Status    | Progress
----------------------------------------------------------------
3  | Daily Fraud Scan  | fraud_detection | completed | 100%
2  | Weekly Analysis   | analytics       | completed | 100%
1  | Risk Assessment   | risk_analysis   | completed | 100%

dafu> products high-risk 5
============================================================
              High-Risk Products (5)                    
============================================================
ID  | SKU           | Name                | Risk Score
---------------------------------------------------------
15  | PHONE-001     | Smartphone Model X  | 0.85
23  | WATCH-LUX     | Luxury Watch        | 0.78
...

dafu> exit
👋 Thank you for using DAFU Platform!
Goodbye!
```

---

## 🔑 Authentication Flow

```
1. ./dafu auth login
   ↓
2. Enter username/password
   ↓
3. API returns JWT token
   ↓
4. Session saved to ~/.dafu_session
   ↓
5. All subsequent commands use saved token
   ↓
6. ./dafu auth logout (clears session)
```

---

## 📁 Files Structure

```
/dafu (main CLI script)
  ├── calls → fraud_detection/src/api/cli.py (for API commands)
  ├── calls → fraud_detection/src/models/main.py (for ML)
  └── calls → start.sh (for Docker)

Session file: ~/.dafu_session
```

---

## 🛠️ Technical Details

### How API Commands Work

1. User runs: `./dafu auth login`
2. `dafu` script receives command
3. Routes to `execute_api_command("auth", "login")`
4. Activates virtual environment in `fraud_detection/`
5. Runs: `python -m src.api.cli auth login`
6. Python CLI handles interactive login
7. Creates session file `~/.dafu_session`
8. Returns to `dafu` prompt

### Auto Environment Setup

The CLI automatically:
- ✅ Checks for virtual environment
- ✅ Creates venv if not exists
- ✅ Installs dependencies if needed
- ✅ Activates before running API commands
- ✅ Deactivates after command completes

---

## 🎓 Advanced Usage

### Combining Commands

```bash
# Start everything and login
./dafu docker up
sleep 10
./dafu auth login

# Run ML model and check reports
./dafu fraud-detection
./dafu reports list

# Check system status
./dafu status
./dafu products stats
```

### Scripting with DAFU CLI

```bash
#!/bin/bash
# Daily fraud check automation

# Login
./dafu auth login << EOF
admin
admin_password
EOF

# Get statistics
./dafu logs stats 24
./dafu reports stats
./dafu products high-risk 10

# Logout
./dafu auth logout
```

---

## ✅ Benefits of Integrated CLI

1. **Single Entry Point**: One command for everything
2. **Consistent Interface**: Same UX across all features
3. **Auto Management**: Virtual environment handled automatically
4. **Session Persistence**: Login once, use everywhere
5. **Interactive & Scriptable**: Works in both modes
6. **Color-Coded Output**: Easy to read
7. **Error Handling**: Graceful degradation

---

## 📞 Support

- **Help**: `./dafu help`
- **API Docs**: http://localhost:8000/docs (when API running)
- **Documentation**: `/docs` directory

---

## 🎉 You're All Set!

Your DAFU CLI now has:
- ✅ API authentication
- ✅ Log management
- ✅ Report generation
- ✅ Product management
- ✅ ML model execution
- ✅ Docker orchestration
- ✅ System information

**All from one command: `./dafu`** 🚀

---

**Happy coding!**

