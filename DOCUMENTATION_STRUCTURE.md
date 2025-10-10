# 📚 DAFU Documentation Structure

This document provides an overview of the DAFU documentation organization.

## 📂 Directory Structure

```
dafu/
├── README.md                          # Main project README
├── CODE_OF_CONDUCT.md                # Community guidelines
├── LICENSE                           # AGPL-3.0 license
├── commits.md                        # Commit history
├── dafu                              # Interactive CLI script
├── start.sh                          # Docker management script
│
├── docs/                             # Documentation root
│   ├── README.md                     # Documentation index
│   │
│   ├── cli/                          # CLI Documentation
│   │   ├── DAFU_CLI_GUIDE.md        # Complete CLI reference
│   │   └── DAFU_CLI_DEMO.md         # Interactive demos & examples
│   │
│   ├── docker/                       # Docker Documentation
│   │   ├── DOCKER_STATUS.md         # Implementation status
│   │   ├── DOCKER_SETUP.md          # Setup instructions
│   │   ├── DOCKER_README.md         # Docker overview
│   │   └── DOCKER_IMPLEMENTATION_SUMMARY.md
│   │
│   ├── guides/                       # General Guides
│   │   ├── QUICK_START.md           # Quick start guide
│   │   └── IMPLEMENTATION_COMPLETE.md # Implementation roadmap
│   │
│   └── assets/                       # Visual Resources
│       └── High-level-architecture.drawio.png
│
└── fraud_detection/                  # ML module documentation
    └── MODEL_PERSISTENCE_README.md  # Model persistence guide
```

## 📖 Documentation Categories

### 🚀 CLI Documentation (`docs/cli/`)

**Purpose:** Interactive command-line interface documentation

| Document | Description | Audience |
|----------|-------------|----------|
| [DAFU_CLI_GUIDE.md](./docs/cli/DAFU_CLI_GUIDE.md) | Complete CLI reference with all commands | All users |
| [DAFU_CLI_DEMO.md](./docs/cli/DAFU_CLI_DEMO.md) | Interactive demos and usage examples | New users |

**Key Topics:**
- Available commands
- Interactive vs single command mode
- Error handling and troubleshooting
- Workflow examples

### 🐳 Docker Documentation (`docs/docker/`)

**Purpose:** Docker deployment and infrastructure documentation

| Document | Description | Audience |
|----------|-------------|----------|
| [DOCKER_STATUS.md](./docs/docker/DOCKER_STATUS.md) | Current implementation status | Developers, DevOps |
| [DOCKER_SETUP.md](./docs/docker/DOCKER_SETUP.md) | Setup and configuration guide | DevOps |
| [DOCKER_README.md](./docs/docker/DOCKER_README.md) | Docker overview | All users |
| [DOCKER_IMPLEMENTATION_SUMMARY.md](./docs/docker/DOCKER_IMPLEMENTATION_SUMMARY.md) | Technical implementation details | Developers |

**Key Topics:**
- Infrastructure status
- Service configuration
- Deployment instructions
- Integration roadmap

### 📘 General Guides (`docs/guides/`)

**Purpose:** Getting started and implementation guides

| Document | Description | Audience |
|----------|-------------|----------|
| [QUICK_START.md](./docs/guides/QUICK_START.md) | Quick start guide | New users |
| [IMPLEMENTATION_COMPLETE.md](./docs/guides/IMPLEMENTATION_COMPLETE.md) | Implementation status and roadmap | Developers, PMs |

**Key Topics:**
- Getting started quickly
- Feature implementation status
- Development roadmap

### 🖼️ Assets (`docs/assets/`)

**Purpose:** Visual resources and diagrams

- Architecture diagrams
- Screenshots
- Flow charts
- Visual guides

## 🔗 Quick Links

### For New Users
1. **Start Here:** [Main README](./README.md)
2. **Quick Setup:** [Quick Start Guide](./docs/guides/QUICK_START.md)
3. **Try CLI:** [CLI Demo](./docs/cli/DAFU_CLI_DEMO.md)

### For Developers
1. **CLI Reference:** [CLI Guide](./docs/cli/DAFU_CLI_GUIDE.md)
2. **Implementation Status:** [Implementation Complete](./docs/guides/IMPLEMENTATION_COMPLETE.md)
3. **Docker Status:** [Docker Status](./docs/docker/DOCKER_STATUS.md)

### For DevOps
1. **Docker Setup:** [Docker Setup](./docs/docker/DOCKER_SETUP.md)
2. **Infrastructure:** [Docker Implementation](./docs/docker/DOCKER_IMPLEMENTATION_SUMMARY.md)
3. **Deployment:** Main README deployment sections

## 📋 Document Maintenance

### Adding New Documentation

1. **Determine Category:** Choose appropriate subfolder (cli, docker, guides)
2. **Create Document:** Follow naming convention (UPPERCASE_WITH_UNDERSCORES.md)
3. **Update Index:** Add link to `docs/README.md`
4. **Update Main README:** Add reference in main `README.md` if needed

### Documentation Standards

- **File Names:** UPPERCASE_WITH_UNDERSCORES.md
- **Headings:** Use emoji for visual hierarchy
- **Links:** Use relative paths
- **Code Blocks:** Include language specification
- **Tables:** Use for structured information

## 🔄 Recent Changes

### October 2024
- ✨ Created organized documentation structure
- 📁 Moved CLI docs to `docs/cli/`
- 🐳 Moved Docker docs to `docs/docker/`
- 📚 Moved general guides to `docs/guides/`
- 📖 Created documentation index (`docs/README.md`)
- 🔗 Updated all references in main README

## 📞 Support

For documentation issues or suggestions:
- Open an issue on GitHub
- Email: dafu@masterfabric.co
- Check [Main README](./README.md) for more support options

---

**Last Updated:** October 10, 2024
**Maintained By:** DAFU Development Team

