# DAFU CLI Documentation

This directory contains comprehensive CLI documentation for the DAFU platform.

---

## 📚 Available Documentation

### **[DAFU CLI Guide](./DAFU_CLI_GUIDE.md)** 📘 Main Reference

Original comprehensive CLI guide covering:
- Interactive mode usage
- All CLI commands
- Docker integration
- System information commands

### **[CLI Demo](./DAFU_CLI_DEMO.md)** 🎬 Examples & Demos

Demonstrations and examples:
- Real usage scenarios
- Screenshot-equivalent text outputs
- Step-by-step walkthroughs

### **[CLI with API Integration](./DAFU_CLI_INTEGRATED.md)** 🔌 API Features ![NEW](https://img.shields.io/badge/NEW!-brightgreen)

Complete guide for using API features through CLI:
- Authentication commands
- Logs management
- Reports management
- Products management
- Integration architecture

### **[CLI Step-by-Step](./CLI_STEP_BY_STEP.md)** 📋 Detailed Guide ![NEW](https://img.shields.io/badge/NEW!-brightgreen)

Step-by-step authentication and session management:
- Login process
- Session file management
- Token handling
- Complete workflows

### **[CLI Usage Complete](./CLI_USAGE_COMPLETE.md)** 📖 Complete Reference ![NEW](https://img.shields.io/badge/NEW!-brightgreen)

Comprehensive CLI usage guide:
- All commands explained
- Usage modes
- Examples for every feature
- Troubleshooting

---

## 🎯 Quick Start

### Basic Usage

```bash
# Start DAFU CLI
./dafu

# Interactive mode
dafu> help
dafu> auth login
dafu> logs list
dafu> reports list
dafu> fraud-detection
dafu> exit
```

### Single Command Mode

```bash
./dafu help
./dafu auth whoami
./dafu logs stats
./dafu reports list
```

---

## 📋 CLI Command Categories

### 🔐 Authentication & Users ![NEW](https://img.shields.io/badge/NEW!-brightgreen)
- `auth login` - Login to API
- `auth logout` - Logout
- `auth whoami` - Show current user
- `auth register` - Register new user

### 📋 Logs Management ![NEW](https://img.shields.io/badge/NEW!-brightgreen)
- `logs list [limit]` - List recent logs
- `logs stats [hours]` - Log statistics

### 📊 Reports Management ![NEW](https://img.shields.io/badge/NEW!-brightgreen)
- `reports list [limit]` - List reports
- `reports create` - Create new report
- `reports view <id>` - View report details
- `reports stats` - Report statistics

### 🛍️ Products Management ![NEW](https://img.shields.io/badge/NEW!-brightgreen)
- `products list [limit]` - List products
- `products high-risk` - High-risk products
- `products stats` - Product statistics

### 🤖 ML Models
- `fraud-detection` - Run ML models interactively
- `models` - Alias for fraud-detection
- `ml` - Alias for fraud-detection

### 🐳 Docker Services
- `docker up/down/restart` - Manage services
- `docker status` - Service status
- `docker logs` - View logs

### 📊 System Information
- `status` - Platform status
- `version` - Version information
- `info` - System details

---

## 🔑 Prerequisites for API Features

### Required Services

1. **PostgreSQL**:
   ```bash
   docker run -d --name dafu-postgres \
     -e POSTGRES_USER=dafu \
     -e POSTGRES_PASSWORD=dafu_secure_password \
     -e POSTGRES_DB=dafu \
     -p 5432:5432 \
     postgres:15-alpine
   ```

2. **API Server**:
   ```bash
   cd fraud_detection
   ./start_api.sh
   ```

---

## 💡 Which Document Should I Read?

| Your Goal | Recommended Document |
|-----------|---------------------|
| **Just getting started** | [DAFU CLI Guide](./DAFU_CLI_GUIDE.md) |
| **Want to see examples** | [CLI Demo](./DAFU_CLI_DEMO.md) |
| **Use API features** | [CLI with API Integration](./DAFU_CLI_INTEGRATED.md) |
| **Need step-by-step for auth** | [CLI Step-by-Step](./CLI_STEP_BY_STEP.md) |
| **Want complete reference** | [CLI Usage Complete](./CLI_USAGE_COMPLETE.md) |
| **General platform usage** | [Usage Guide](../USAGE_GUIDE.md) |

---

## 🎓 Learning Path

### Beginner
1. **[DAFU CLI Guide](./DAFU_CLI_GUIDE.md)** - Learn basic commands
2. **[CLI Demo](./DAFU_CLI_DEMO.md)** - See examples
3. Start using: `./dafu help`

### Intermediate
1. **[CLI with API Integration](./DAFU_CLI_INTEGRATED.md)** - API features
2. **[CLI Step-by-Step](./CLI_STEP_BY_STEP.md)** - Authentication flow
3. Try API commands: `./dafu auth login`

### Advanced
1. **[CLI Usage Complete](./CLI_USAGE_COMPLETE.md)** - Full reference
2. **[API Usage Guide](../api/API_USAGE_GUIDE.md)** - Direct API calls
3. Write automation scripts

---

## 🆘 Troubleshooting

Common issues and their documentation:

| Issue | Solution Location |
|-------|------------------|
| How to login? | [CLI Step-by-Step](./CLI_STEP_BY_STEP.md) |
| API not responding | [CLI with API Integration](./DAFU_CLI_INTEGRATED.md#prerequisites) |
| Command not found | [CLI Usage Complete](./CLI_USAGE_COMPLETE.md) |
| Session expired | [CLI Step-by-Step](./CLI_STEP_BY_STEP.md#step-4-cli-for-session-file) |

---

## 📞 Support

- **Interactive Help**: `./dafu help`
- **API Docs**: http://localhost:8000/docs (when running)
- **GitHub Issues**: https://github.com/MasterFabric/dafu/issues

---

**DAFU CLI - One Command for Everything** 🚀

