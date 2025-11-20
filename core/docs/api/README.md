# DAFU API Documentation

This directory contains comprehensive API documentation for the DAFU platform.

---

## 📚 Available Documentation

### **[API Usage Guide](./API_USAGE_GUIDE.md)** ⭐ Main Reference

Complete API documentation covering:
- All endpoints (Authentication, Logs, Reports, Products)
- Request/response examples
- Authentication flow
- Error handling
- Best practices

### **[API Quick Start](./QUICK_START_API.md)** 🚀 5-Minute Setup

Quick setup guide to get the API running:
- Installation steps
- Database setup
- First API calls
- Testing procedures

### **[MCP Feature Development](./MCP_FEATURE_DEVELOPMENT.md)** 🔧 Technical Guide

Complete technical documentation for implementing Model Context Protocol (MCP) feature:
- Architecture and component structure
- Step-by-step development guide (10+ steps)
- Detailed code examples for each component
- How to run and test instructions
- API endpoints documentation
- Configuration and troubleshooting

### **[LLM Chat Connector Hub](./LLM_CHAT_CONNECTOR_HUB.md)** 🤖 Technical Guide

Complete technical documentation for LLM Chat Connector Hub Manager:
- Multi-provider architecture (OpenAI + Claude)
- Step-by-step development guide (11+ steps)
- Provider implementation details
- Chat session management
- How to run and test instructions
- API endpoints documentation
- Configuration for both providers

---

## 🔌 API Features

### Authentication & Authorization
- JWT token-based authentication
- Role-based access control (RBAC)
- API key generation
- Session management
- Password management

### Logs Management
- Create log entries
- Query logs with filters
- Log statistics and analytics
- Cleanup operations (admin only)

### Reports Management
- Create fraud detection reports
- List and filter reports
- View report details
- Track report progress
- Retry failed reports

### Products Management
- CRUD operations for products
- Fraud risk tracking
- Stock management
- High-risk product detection
- Product analytics

### MCP (Model Context Protocol)
- Tool registration and discovery
- Fraud detection tool integration
- Model management via MCP
- External client integration

### LLM Chat Connector Hub
- Multi-provider LLM support (OpenAI + Claude)
- Chat session management
- Streaming responses
- Provider switching
- Conversation history

---

## 🚀 Quick Start

### 1. Start PostgreSQL

```bash
docker run -d --name dafu-postgres \
  -e POSTGRES_USER=dafu \
  -e POSTGRES_PASSWORD=dafu_secure_password \
  -e POSTGRES_DB=dafu \
  -p 5432:5432 \
  postgres:15-alpine
```

### 2. Start API

```bash
cd fraud_detection
./start_api.sh
```

### 3. Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📋 API Endpoints Overview

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/logout` - User logout

### Logs
- `POST /api/v1/logs/` - Create log entry
- `GET /api/v1/logs/` - List logs
- `GET /api/v1/logs/stats` - Log statistics

### Reports
- `POST /api/v1/reports/` - Create report
- `GET /api/v1/reports/` - List reports
- `GET /api/v1/reports/{id}` - Get report details
- `GET /api/v1/reports/stats` - Report statistics

### Products
- `POST /api/v1/products/` - Create product
- `GET /api/v1/products/` - List products
- `GET /api/v1/products/high-risk` - High-risk products
- `GET /api/v1/products/stats` - Product statistics

### MCP
- `GET /api/v1/mcp/health` - MCP health check
- `GET /api/v1/mcp/tools` - List available tools
- `POST /api/v1/mcp/tools/call` - Call an MCP tool

### LLM
- `GET /api/v1/llm/health` - LLM service health check
- `GET /api/v1/llm/providers` - List available providers
- `POST /api/v1/llm/chat` - Send chat message
- `GET /api/v1/llm/sessions/{session_id}` - Get session details
- `DELETE /api/v1/llm/sessions/{session_id}` - Delete session

**See [API Usage Guide](./API_USAGE_GUIDE.md) for complete endpoint reference**

---

## 🔑 Authentication

All endpoints (except register/login) require authentication via:
- **JWT Token**: `Authorization: Bearer <token>`
- **API Key**: `X-API-Key: <api-key>`

Get token by calling `/api/v1/auth/login`

---

## 📞 Support

- **Live API Docs**: http://localhost:8000/docs
- **GitHub**: https://github.com/MasterFabric/dafu
- **Email**: dafu@masterfabric.co

---

**DAFU API - Enterprise Fraud Detection Platform** 🚀

