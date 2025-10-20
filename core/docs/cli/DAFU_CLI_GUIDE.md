# 🚀 DAFU Interactive CLI Guide

## Overview

DAFU CLI is an interactive command-line interface for managing the DAFU (Data Analytics Functional Utilities) platform, including fraud detection models and Docker services.

## Quick Start

### Option 1: Interactive Mode (Recommended)

Start the interactive CLI:

```bash
./dafu
```

You'll see a welcome screen and an interactive prompt:

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

### Option 2: Single Command Mode

Execute a single command without entering interactive mode:

```bash
./dafu fraud-detection    # Run fraud detection
./dafu status             # Show platform status
./dafu help               # Show help
```

## Available Commands

### 🤖 Fraud Detection & ML Models

| Command | Description |
|---------|-------------|
| `fraud-detection` | Run fraud detection models (interactive) |
| `models` | Alias for fraud-detection |
| `ml` | Alias for fraud-detection |

**Example:**
```
dafu> fraud-detection
```

This will:
1. Check for virtual environment (create if needed)
2. Install dependencies (if needed)
3. Launch the fraud detection model selector
4. Return to CLI after completion

### 🐳 Docker Services

| Command | Description |
|---------|-------------|
| `docker up` | Start Docker services |
| `docker down` | Stop Docker services |
| `docker restart` | Restart Docker services |
| `docker status` | Show Docker service status |
| `docker logs` | View Docker logs (Ctrl+C to exit) |
| `docker rebuild` | Rebuild and restart services |

**Examples:**
```
dafu> docker up
dafu> docker status
dafu> docker logs
```

**⚠️ Error Handling:**

The CLI is designed to **stay active even when Docker commands fail**. If a Docker operation encounters an error:

- ✅ The CLI will **not exit**
- ✅ You'll see an informative error message
- ✅ You can continue using other commands
- ✅ Exit code is displayed for debugging

**Example:**
```
dafu> docker up

Starting Docker services...
[... error messages ...]

⚠️  Docker service start returned exit code: 1
💡 You can still use other CLI commands

dafu> status
[... continues normally ...]
```

This design ensures a smooth user experience even when some operations fail.

### 📊 System Information

| Command | Description |
|---------|-------------|
| `status` | Show platform status |
| `version` | Show version information |
| `info` | Show detailed system information |

**Examples:**
```
dafu> status
```

Output:
```
DAFU Platform Status
══════════════════════════════════════════════════════════
Python 3:          ✓ Available (Python 3.9.7)
Docker:            ✓ Available (Docker version 24.0.5)
Docker Daemon:     ✓ Running
Docker Services:   ○ No containers running
Fraud Detection:   ✓ Available
Trained Models:    ✓ 3 model(s) found
```

### 🛠️ Utilities

| Command | Description |
|---------|-------------|
| `help` | Show available commands |
| `clear` | Clear the screen |
| `exit` | Exit DAFU CLI |
| `quit` | Alias for exit |

## Usage Examples

### Example 1: Quick Fraud Detection

```bash
# Start CLI
./dafu

# Run fraud detection
dafu> fraud-detection

# [Interactive model selection appears]
# Choose model, process data, view results

# Returns to CLI when done
dafu> exit
```

### Example 2: Docker Management

```bash
# Start Docker services
./dafu

dafu> docker up
# Services starting...

dafu> docker status
# Check if services are running

dafu> docker logs
# View service logs (Ctrl+C to exit logs)

dafu> exit
```

### Example 3: System Check

```bash
./dafu

dafu> status
# Shows platform status

dafu> info
# Shows detailed information

dafu> version
# Shows version

dafu> exit
```

### Example 4: Single Command Execution

```bash
# No interactive mode - just run and exit
./dafu fraud-detection

# Or check status
./dafu status

# Or show help
./dafu help
```

## Workflow Examples

### Complete Fraud Detection Workflow

```bash
# 1. Start DAFU CLI
./dafu

# 2. Check system status
dafu> status

# 3. Run fraud detection
dafu> fraud-detection

# [Model selection interface appears]
# Select: 1 (Isolation Forest & Risk Score)
# [Model runs and completes]

# 4. Check results
dafu> info

# 5. Exit
dafu> exit
```

### Docker Service Workflow

```bash
# 1. Start DAFU CLI
./dafu

# 2. Start Docker services
dafu> docker up

# 3. Check status
dafu> docker status

# 4. View logs
dafu> docker logs

# 5. Stop services when done
dafu> docker down

# 6. Exit CLI
dafu> exit
```

## Features

### ✅ Auto-Setup
- Automatically creates Python virtual environment if not present
- Installs dependencies when needed
- No manual setup required

### ✅ Interactive and Scriptable
- Use interactively with a persistent session
- Or run single commands for scripting/automation

### ✅ User-Friendly
- Clear command structure
- Helpful error messages
- Color-coded output
- Tab-friendly command names

### ✅ Integrated
- Seamlessly integrates with fraud detection models
- Manages Docker services via start.sh
- Real-time status monitoring

## Tips

1. **Use Tab Completion**: Many terminals support command history with arrow keys
2. **Ctrl+C**: Interrupts current operation but doesn't exit CLI
3. **Multiple Sessions**: You can run multiple fraud detection sessions without restarting CLI
4. **Command Aliases**: Use shorter commands like `ml` instead of `fraud-detection`

## Troubleshooting

### Command Not Found

```bash
# Make sure the script is executable
chmod +x dafu
```

### Python Virtual Environment Issues

The CLI will automatically create and manage the virtual environment. If you encounter issues:

```bash
# Remove the old environment
rm -rf core/features/fraud_detection/venv

# Run fraud-detection again, it will recreate
./dafu fraud-detection
```

### Docker Commands Not Working

Make sure Docker is installed and running:

```bash
dafu> docker status
```

If Docker daemon is not running, start Docker Desktop or the Docker service.

### Permission Denied

```bash
# Make the script executable
chmod +x dafu

# If still issues, run with bash
bash dafu
```

## Integration with Start.sh

The DAFU CLI complements `start.sh`:

- **`./dafu`**: Interactive CLI for all operations
- **`./start.sh`**: Direct Docker service management

Both tools work together seamlessly!

## Next Steps

1. **Try it out**: `./dafu`
2. **Run fraud detection**: `dafu> fraud-detection`
3. **Explore commands**: `dafu> help`
4. **Check status**: `dafu> status`

Enjoy using DAFU! 🎉

