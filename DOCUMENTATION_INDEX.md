# DAFU - Complete Documentation Index

## 🎯 Overview

This is the master index for all DAFU platform documentation. Use this guide to navigate to the right documentation for your needs.

---

## ⭐ Start Here

### **[Complete Usage Guide](./docs/USAGE_GUIDE.md)** 

The single most important document - covers all DAFU features in one place:
- Quick start (3 steps)
- All CLI commands
- Complete workflow examples
- Troubleshooting
- Configuration

**Start here if you're new to DAFU!**

---

## 📚 Documentation by Category

### 🔐 API & Backend

**Location**: `docs/api/`

| Document | Purpose | Audience |
|----------|---------|----------|
| **[API Usage Guide](./docs/api/API_USAGE_GUIDE.md)** | Complete REST API reference | Developers |
| **[API Quick Start](./docs/api/QUICK_START_API.md)** | 5-minute API setup | Everyone |
| **[API README](./docs/api/README.md)** | API documentation index | Everyone |

**Covers**: Authentication, Logs, Reports, Products endpoints

---

### 💻 CLI & Interface

**Location**: `docs/cli/`

| Document | Purpose | Audience |
|----------|---------|----------|
| **[DAFU CLI Guide](./docs/cli/DAFU_CLI_GUIDE.md)** | Original CLI reference | CLI users |
| **[CLI Demo](./docs/cli/DAFU_CLI_DEMO.md)** | Usage examples | Everyone |
| **[CLI Integration](./docs/cli/DAFU_CLI_INTEGRATED.md)** | API integration details | Developers |
| **[CLI Step-by-Step](./docs/cli/CLI_STEP_BY_STEP.md)** | Authentication flow | New users |
| **[CLI Usage Complete](./docs/cli/CLI_USAGE_COMPLETE.md)** | Complete CLI reference | Power users |
| **[CLI README](./docs/cli/README.md)** | CLI documentation index | Everyone |

**Covers**: Unified CLI with auth, logs, reports, products, ML models

---

### 📘 Getting Started Guides

**Location**: `docs/guides/`

| Document | Purpose | Audience |
|----------|---------|----------|
| **[Quick Start](./docs/guides/QUICK_START.md)** | ML models quick start | Data scientists |
| **[Implementation Complete](./docs/guides/IMPLEMENTATION_COMPLETE.md)** | Implementation status | Everyone |

**Covers**: ML model training and usage

---

### 🐳 Deployment & Infrastructure

**Location**: `docs/docker/`

| Document | Purpose | Audience |
|----------|---------|----------|
| **[Docker Status](./docs/docker/DOCKER_STATUS.md)** | Current deployment status | DevOps |
| **[Docker Setup](./docs/docker/DOCKER_SETUP.md)** | Docker configuration | DevOps |
| **[Docker README](./docs/docker/DOCKER_README.md)** | Docker overview | Everyone |
| **[Docker Implementation](./docs/docker/DOCKER_IMPLEMENTATION_SUMMARY.md)** | Implementation details | Developers |

**Covers**: Docker Compose, containerization, deployment

---

### 📖 Root Documentation

**Location**: `/` (project root)

| Document | Purpose |
|----------|---------|
| **[README.md](./README.md)** | Main project README |
| **[USAGE_GUIDE](./docs/USAGE_GUIDE.md)** | Complete usage guide |
| **[HOW_TO_USE_CLI](./HOW_TO_USE_CLI.md)** | Quick CLI instructions |
| **[API_SETUP_COMPLETE](./API_SETUP_COMPLETE.md)** | API setup summary |
| **[TESTED_QUICK_START](./TESTED_QUICK_START.md)** | Tested installation steps |
| **[DOCUMENTATION_STRUCTURE](./DOCUMENTATION_STRUCTURE.md)** | Old structure reference |

---

## 🎯 Quick Navigation by Task

### I want to...

| Task | Documentation |
|------|---------------|
| **Get started with everything** | [Usage Guide](./docs/USAGE_GUIDE.md) |
| **Use the CLI** | [CLI Guide](./docs/cli/DAFU_CLI_GUIDE.md) |
| **Setup the API** | [API Quick Start](./docs/api/QUICK_START_API.md) |
| **Call API endpoints** | [API Usage Guide](./docs/api/API_USAGE_GUIDE.md) |
| **Run ML models** | [ML Quick Start](./docs/guides/QUICK_START.md) |
| **Deploy with Docker** | [Docker Status](./docs/docker/DOCKER_STATUS.md) |
| **Authenticate users** | [CLI Step-by-Step](./docs/cli/CLI_STEP_BY_STEP.md) |
| **View logs** | [Usage Guide - Logs](./docs/USAGE_GUIDE.md#logs-management) |
| **Create reports** | [Usage Guide - Reports](./docs/USAGE_GUIDE.md#reports-management) |
| **Manage products** | [Usage Guide - Products](./docs/USAGE_GUIDE.md#products-management) |

---

## 📊 Documentation Organization

```
dafu/
├── README.md                           # Main project README
├── docs/
│   ├── USAGE_GUIDE.md                 # ⭐ Complete usage guide (START HERE)
│   ├── README.md                       # Documentation index
│   │
│   ├── api/                            # 🔐 API Documentation
│   │   ├── README.md
│   │   ├── API_USAGE_GUIDE.md         # Complete API reference
│   │   └── QUICK_START_API.md         # 5-minute API setup
│   │
│   ├── cli/                            # 💻 CLI Documentation
│   │   ├── README.md
│   │   ├── DAFU_CLI_GUIDE.md          # Original CLI guide
│   │   ├── DAFU_CLI_DEMO.md           # Usage examples
│   │   ├── DAFU_CLI_INTEGRATED.md     # API integration
│   │   ├── CLI_STEP_BY_STEP.md        # Step-by-step auth
│   │   └── CLI_USAGE_COMPLETE.md      # Complete reference
│   │
│   ├── guides/                         # 📘 Getting Started
│   │   ├── QUICK_START.md             # ML models quick start
│   │   └── IMPLEMENTATION_COMPLETE.md # Implementation status
│   │
│   ├── docker/                         # 🐳 Docker Documentation
│   │   ├── DOCKER_STATUS.md
│   │   ├── DOCKER_SETUP.md
│   │   ├── DOCKER_README.md
│   │   └── DOCKER_IMPLEMENTATION_SUMMARY.md
│   │
│   └── assets/                         # 🖼️ Images & Diagrams
│       └── High-level-architecture.drawio.png
│
├── fraud_detection/
│   ├── API_README.md                   # API overview
│   ├── USAGE_EXAMPLES.md               # Usage examples
│   └── cli_login.sh                    # Login helper script
│
└── Other documentation files...
```

---

## 🚀 Quick Start Paths

### Path 1: Complete Platform (Recommended)
1. [Usage Guide](../USAGE_GUIDE.md) - Complete overview
2. [API Quick Start](../api/QUICK_START_API.md) - Setup API
3. [CLI Integration](./DAFU_CLI_INTEGRATED.md) - Use CLI with API

### Path 2: CLI Only
1. [DAFU CLI Guide](./DAFU_CLI_GUIDE.md) - Learn CLI basics
2. [CLI Demo](./DAFU_CLI_DEMO.md) - See examples
3. [ML Quick Start](../guides/QUICK_START.md) - Run ML models

### Path 3: API Only
1. [API Quick Start](../api/QUICK_START_API.md) - Setup in 5 minutes
2. [API Usage Guide](../api/API_USAGE_GUIDE.md) - Full API reference
3. Use Swagger UI: http://localhost:8000/docs

---

## 🎓 By Experience Level

### Beginners
- **[Usage Guide](../USAGE_GUIDE.md)** - Start here
- **[CLI Demo](./DAFU_CLI_DEMO.md)** - See examples

### Intermediate
- **[CLI Integration](./DAFU_CLI_INTEGRATED.md)** - API features
- **[API Usage Guide](../api/API_USAGE_GUIDE.md)** - API details

### Advanced
- **[CLI Usage Complete](./CLI_USAGE_COMPLETE.md)** - Full reference
- Write custom automation scripts

---

## 🔍 Find Documentation

### By Feature

| Feature | Documentation |
|---------|---------------|
| **Authentication** | [CLI Step-by-Step](./CLI_STEP_BY_STEP.md), [API Guide](../api/API_USAGE_GUIDE.md#authentication) |
| **Logging** | [Usage Guide - Logs](../USAGE_GUIDE.md#logs-management) |
| **Reports** | [Usage Guide - Reports](../USAGE_GUIDE.md#reports-management) |
| **Products** | [Usage Guide - Products](../USAGE_GUIDE.md#products-management) |
| **ML Models** | [ML Quick Start](../guides/QUICK_START.md) |
| **Docker** | [Docker Status](../docker/DOCKER_STATUS.md) |

### By User Type

| User Type | Start Here |
|-----------|-----------|
| **End User** | [Usage Guide](../USAGE_GUIDE.md) |
| **Developer** | [API Usage Guide](../api/API_USAGE_GUIDE.md) |
| **Data Scientist** | [ML Quick Start](../guides/QUICK_START.md) |
| **DevOps** | [Docker Status](../docker/DOCKER_STATUS.md) |
| **Admin** | [Usage Guide](../USAGE_GUIDE.md) + [API Guide](../api/API_USAGE_GUIDE.md) |

---

## 📞 Support

- **CLI Help**: `./dafu help`
- **API Docs**: http://localhost:8000/docs
- **GitHub**: https://github.com/MasterFabric/dafu/issues

---

**DAFU - Enterprise Fraud Detection Platform** 🚀

