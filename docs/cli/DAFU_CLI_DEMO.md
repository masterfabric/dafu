# 🎬 DAFU Interactive CLI Demo

## Quick Demo Session

Here's a complete demo session showing how to use the DAFU CLI:

### Starting the CLI

```bash
$ ./dafu
```

```
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

dafu>
```

### Exploring Commands

```bash
dafu> help
```

```
Available Commands:
══════════════════════════════════════════════════════════

Fraud Detection & ML Models:
  fraud-detection     - Run fraud detection models (interactive)
  models              - Alias for fraud-detection
  ml                  - Alias for fraud-detection

Docker Services:
  docker up           - Start Docker services
  docker down         - Stop Docker services
  docker restart      - Restart Docker services
  docker status       - Show Docker service status
  docker logs         - View Docker logs
  docker rebuild      - Rebuild and restart services

System Information:
  status              - Show platform status
  version             - Show version information
  info                - Show system information

Utilities:
  help                - Show this help message
  clear               - Clear the screen
  exit                - Exit DAFU CLI
  quit                - Alias for exit

══════════════════════════════════════════════════════════
```

### Checking System Status

```bash
dafu> status
```

```
DAFU Platform Status
══════════════════════════════════════════════════════════
Python 3:          ✓ Available (Python 3.9.6)
Docker:            ✓ Available (Docker version 24.0.5)
Docker Daemon:     ✓ Running
Docker Services:   ○ No containers running
Fraud Detection:   ✓ Available
Trained Models:    ✓ 2 model(s) found
```

### Viewing System Information

```bash
dafu> info
```

```
DAFU System Information
══════════════════════════════════════════════════════════
Installation Path: /Users/user/Documents/GitHub/dafu
Fraud Detection:   /Users/user/Documents/GitHub/dafu/fraud_detection

Python Virtual Env: ✓ Configured
Docker Compose:     ✓ Available

Available Components:
  • Isolation Forest Fraud Detection
  • LSTM/GRU Sequence Models
  • Risk Score Analysis
  • Real-time Stream Processing
  • Batch Processing
```

### Checking Version

```bash
dafu> version
```

```
DAFU Platform Version Information
──────────────────────────────────────────────
Version:     1.0.0
Build:       Production
Platform:    Fraud Detection & Analytics
Python:      Python 3.9.6
Docker:      Docker version 24.0.5
```

### Running Fraud Detection

```bash
dafu> fraud-detection
```

```
🔍 Starting Fraud Detection Models...

Virtual environment found. Activating...
════════════════════════════════════════════════════════════

============================================================
🔍 ENTERPRISE FRAUD DETECTION PLATFORM
============================================================
Advanced Machine Learning Models for Fraud Detection
Version: 1.0.0
============================================================

This platform offers multiple fraud detection approaches:
• Traditional ML: Isolation Forest with Risk Score analysis
• Deep Learning: LSTM and GRU sequence-based models
• Both supervised and unsupervised learning modes
• Real-time streaming and batch processing capabilities
============================================================

⚡ Fast startup - models load only when selected!

============================================================
🎯 SELECT FRAUD DETECTION MODEL
============================================================
Choose the type of fraud detection model you want to use:

1. 🔍 ISOLATION FOREST & RISK SCORE
   • Traditional machine learning approach
   • Excellent for tabular data with numerical features
   • Supports both supervised and unsupervised learning
   • Risk score based anomaly detection
   • Fast training and prediction

2. 🧠 SEQUENCE MODELS (LSTM & GRU)
   • Deep learning approach for sequential data
   • Captures temporal patterns and dependencies
   • Autoencoder architecture for anomaly detection
   • Best for time-series and transaction sequences
   • More complex but potentially more accurate

3. ℹ️  MODEL COMPARISON
   • Compare different models on the same dataset
   • Get recommendations based on your data

4. ❓ HELP & INFORMATION
   • Detailed information about each model
   • Data requirements and recommendations

5. 🚪 EXIT
   • Exit the application
============================================================

Enter your choice (1-5): 1

📦 Loading Isolation Forest model...

✅ Initialized Isolation Forest & Risk Score

🚀 Starting Isolation Forest & Risk Score...
============================================================
[... model runs and completes ...]

════════════════════════════════════════════════════════════
✓ Fraud detection session completed

dafu>
```

### Docker Operations

```bash
dafu> docker status
```

```
Docker service status:
NAME      IMAGE     COMMAND   SERVICE   CREATED   STATUS    PORTS
```

```bash
dafu> docker up
```

```
Starting Docker services...

============================================================
  ____    _    _____ _   _ 
 |  _ \  / \  |  ___| | | |
 | | | |/ _ \ | |_  | | | |
 | |_| / ___ \|  _| | |_| |
 |____/_/   \_\_|    \___/ 
                            
 Data Analytics Functional Utilities
 Docker Compose Setup
============================================================

💡 Tip: Use ./dafu for interactive CLI mode!

✓ Docker Compose V1 detected
Starting DAFU Platform...

Checking docker-compose.yml...
Error: No active services found in docker-compose.yml

All services appear to be commented out.

To use DAFU ML models NOW:
  cd fraud_detection
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  cd src/models
  python main.py

See DOCKER_STATUS.md for details.

⚠️  Docker service start returned exit code: 1
💡 You can still use other CLI commands

dafu>
```

**Notice**: Even though Docker failed to start (no active services), the CLI **does not exit**. You can continue using other commands!

### Clearing the Screen

```bash
dafu> clear
```

*[Screen clears and shows banner again]*

### Exiting the CLI

```bash
dafu> exit
```

```
👋 Thank you for using DAFU Platform!
Goodbye!
```

---

## Single Command Mode

You can also use DAFU CLI in single command mode without entering interactive mode:

### Quick Status Check

```bash
$ ./dafu status
```

```
DAFU Platform Status
══════════════════════════════════════════════════════════
Python 3:          ✓ Available (Python 3.9.6)
Docker:            ✓ Available (Docker version 24.0.5)
Docker Daemon:     ✓ Running
Docker Services:   ○ No containers running
Fraud Detection:   ✓ Available
Trained Models:    ✓ 2 model(s) found
```

### Run Fraud Detection Directly

```bash
$ ./dafu fraud-detection
```

*[Launches fraud detection directly without interactive mode]*

### Show Help

```bash
$ ./dafu help
```

*[Shows help and exits]*

---

## Key Features Demonstrated

✅ **Interactive Mode**: Persistent session, no need to restart
✅ **Single Command Mode**: Quick operations without entering interactive mode
✅ **Auto-Setup**: Virtual environment and dependencies handled automatically
✅ **Multiple Aliases**: `fraud-detection`, `models`, `ml` all work the same
✅ **Docker Integration**: Manage Docker services from CLI
✅ **System Monitoring**: Real-time status of all components
✅ **User-Friendly**: Clear output, color-coded messages
✅ **Resilient Error Handling**: CLI stays active even when commands fail ![NEW](https://img.shields.io/badge/NEW!-brightgreen)
✅ **No Crashes**: Docker errors won't exit the CLI session

---

## Comparison: Old vs New Workflow

### ❌ Old Workflow (Manual)

```bash
# Terminal 1
cd fraud_detection
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd src/models
python main.py

# [Model runs]
# [Want to run again? Repeat everything]
```

### ✅ New Workflow (DAFU CLI)

```bash
./dafu
dafu> fraud-detection
# [Model runs]
dafu> fraud-detection
# [Run again! No setup needed]
dafu> status
# [Check system]
dafu> docker up
# [Manage Docker]
dafu> exit
```

**Benefits:**
- 🚀 **90% faster** - No manual setup
- 🔄 **Persistent session** - Run multiple times without restart
- 🎯 **All-in-one** - ML models + Docker + System info
- 💡 **Smart** - Auto-creates environment and installs dependencies
- 🎨 **Beautiful** - Clean, modern interface

---

## Tips & Tricks

1. **Command History**: Use arrow keys (↑↓) to navigate command history
2. **Tab Completion**: Many terminals support tab completion
3. **Ctrl+C**: Interrupts current operation but stays in CLI
4. **Multiple Operations**: Run fraud detection multiple times without exiting
5. **Single Commands**: Use `./dafu status` for quick checks in scripts

---

## Next Steps

1. **Try it yourself**: `./dafu`
2. **Read the guide**: Check `DAFU_CLI_GUIDE.md` for complete documentation
3. **Explore models**: Run `fraud-detection` and try different models
4. **Integrate**: Use in your automation scripts

Happy fraud detecting! 🎉

