# FastAPI MCP Feature - Technical Development Guide

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Step-by-Step Development](#step-by-step-development)
4. [How to Run](#how-to-run)
5. [How to Test](#how-to-test)
6. [API Endpoints](#api-endpoints)
7. [Configuration](#configuration)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The **Model Context Protocol (MCP)** feature enables FastAPI to act as an MCP server, allowing external clients (like AI assistants, IDEs, or other services) to interact with DAFU's fraud detection capabilities through a standardized protocol.

### Key Features

- **MCP Server Implementation**: FastAPI-based MCP server for tool exposure
- **Tool Registration**: Dynamic tool registration and discovery
- **Request Handling**: Async request processing with validation
- **Error Handling**: Comprehensive error responses
- **Authentication**: Secure access control for MCP endpoints
- **Tool Execution**: Safe execution of fraud detection tools

### Use Cases

- AI assistants querying fraud detection models
- IDE integrations for fraud analysis
- External services accessing DAFU capabilities
- Automated fraud detection workflows

---

## 🏗️ Architecture

### Component Structure

```
core/apis/
├── services/
│   ├── main.py                 # FastAPI app
│   └── mcp_routes.py          # MCP endpoints (NEW)
├── modules/
│   └── mcp/
│       ├── __init__.py
│       ├── server.py          # MCP server implementation (NEW)
│       ├── tools.py           # Tool registry (NEW)
│       ├── handlers.py        # Request handlers (NEW)
│       └── models.py          # Pydantic models (NEW)
└── plugins/
    └── mcp_tools/
        ├── __init__.py
        ├── fraud_detection_tool.py    # Fraud detection tool (NEW)
        ├── model_management_tool.py   # Model management tool (NEW)
        └── analytics_tool.py          # Analytics tool (NEW)
```

### MCP Protocol Flow

```
Client Request
    ↓
MCP Router (/api/v1/mcp/*)
    ↓
MCP Server Handler
    ↓
Tool Registry (Find Tool)
    ↓
Tool Execution
    ↓
Response Formatter
    ↓
Client Response
```

### Data Flow Diagram

```
┌─────────────┐
│   Client    │
│  (Request)  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  MCP Router     │
│  (FastAPI)      │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  MCP Server     │
│  (Handler)      │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Tool Registry   │
│ (Find Tool)     │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Tool Execution  │
│ (Handler)       │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│   Response      │
│  (Formatted)    │
└─────────────────┘
```

---

## 📝 Step-by-Step Development

### Step 1: Install Dependencies

Add MCP-related dependencies to `requirements.txt`:

```bash
# MCP Protocol Support
mcp>=0.1.0
pydantic>=2.0.0
```

Install dependencies:

```bash
cd /Users/gurkanfikretgunak/Documents/GitHub/dafu
pip install -r requirements.txt
```

### Step 2: Create MCP Module Structure

Create the MCP module directory:

```bash
mkdir -p core/apis/modules/mcp
mkdir -p core/apis/plugins/mcp_tools
touch core/apis/modules/mcp/__init__.py
touch core/apis/modules/mcp/server.py
touch core/apis/modules/mcp/tools.py
touch core/apis/modules/mcp/handlers.py
touch core/apis/modules/mcp/models.py
touch core/apis/plugins/mcp_tools/__init__.py
```

### Step 3: Implement MCP Models

Create `core/apis/modules/mcp/models.py`:

```python
"""
MCP Protocol Models
Pydantic models for MCP request/response handling
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class MCPTool(BaseModel):
    """MCP Tool definition"""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    inputSchema: Dict[str, Any] = Field(..., description="JSON schema for tool inputs")


class MCPListToolsResponse(BaseModel):
    """Response for list_tools request"""
    tools: List[MCPTool] = Field(..., description="List of available tools")


class MCPCallToolRequest(BaseModel):
    """Request for call_tool"""
    name: str = Field(..., description="Tool name to call")
    arguments: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Tool arguments")


class MCPCallToolResponse(BaseModel):
    """Response for call_tool"""
    content: List[Dict[str, Any]] = Field(..., description="Tool execution results")
    isError: bool = Field(default=False, description="Whether execution resulted in error")


class MCPError(BaseModel):
    """MCP Error response"""
    code: int = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional error data")
```

### Step 4: Implement Tool Registry

Create `core/apis/modules/mcp/tools.py`:

```python
"""
MCP Tool Registry
Manages registration and discovery of MCP tools
"""

from typing import Dict, Callable, Any, Optional
from .models import MCPTool
import logging

logger = logging.getLogger(__name__)


class MCPToolRegistry:
    """Registry for MCP tools"""
    
    def __init__(self):
        self._tools: Dict[str, MCPTool] = {}
        self._handlers: Dict[str, Callable] = {}
    
    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        handler: Callable
    ):
        """
        Register a new MCP tool
        
        Args:
            name: Tool name (must be unique)
            description: Tool description
            input_schema: JSON schema for tool inputs
            handler: Async function to handle tool execution
        """
        if name in self._tools:
            logger.warning(f"Tool {name} already registered, overwriting")
        
        tool = MCPTool(
            name=name,
            description=description,
            inputSchema=input_schema
        )
        
        self._tools[name] = tool
        self._handlers[name] = handler
        logger.info(f"Registered MCP tool: {name}")
    
    def get_tool(self, name: str) -> Optional[MCPTool]:
        """Get tool by name"""
        return self._tools.get(name)
    
    def list_tools(self) -> list[MCPTool]:
        """List all registered tools"""
        return list(self._tools.values())
    
    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            Tool execution result
            
        Raises:
            ValueError: If tool not found
            Exception: If tool execution fails
        """
        if name not in self._handlers:
            raise ValueError(f"Tool {name} not found")
        
        handler = self._handlers[name]
        try:
            result = await handler(**arguments)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": str(result)
                    }
                ],
                "isError": False
            }
        except Exception as e:
            logger.error(f"Tool {name} execution failed: {str(e)}", exc_info=True)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: {str(e)}"
                    }
                ],
                "isError": True
            }


# Global tool registry instance
tool_registry = MCPToolRegistry()
```

### Step 5: Implement MCP Server

Create `core/apis/modules/mcp/server.py`:

```python
"""
MCP Server Implementation
Core MCP protocol handling
"""

from typing import Dict, Any
from .tools import tool_registry
from .models import MCPListToolsResponse, MCPCallToolResponse
import logging

logger = logging.getLogger(__name__)


class MCPServer:
    """MCP Server for handling protocol requests"""
    
    def __init__(self):
        self.tool_registry = tool_registry
    
    async def list_tools(self) -> MCPListToolsResponse:
        """
        List all available tools
        
        Returns:
            MCPListToolsResponse with all registered tools
        """
        tools = self.tool_registry.list_tools()
        logger.info(f"Listing {len(tools)} MCP tools")
        return MCPListToolsResponse(tools=tools)
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> MCPCallToolResponse:
        """
        Call a tool by name
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            MCPCallToolResponse with execution results
        """
        logger.info(f"Calling MCP tool: {name} with arguments: {arguments}")
        
        result = await self.tool_registry.execute_tool(name, arguments)
        
        return MCPCallToolResponse(
            content=result["content"],
            isError=result["isError"]
        )


# Global MCP server instance
mcp_server = MCPServer()
```

### Step 6: Create MCP Tools

Create `core/apis/plugins/mcp_tools/fraud_detection_tool.py`:

```python
"""
Fraud Detection MCP Tool
Tool for performing fraud detection via MCP
"""

from typing import Dict, Any
from core.apis.modules.mcp.tools import tool_registry
import logging

logger = logging.getLogger(__name__)


async def fraud_detection_handler(
    transaction_id: str,
    amount: float,
    user_id: str,
    merchant_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Handle fraud detection tool execution
    
    Args:
        transaction_id: Transaction identifier
        amount: Transaction amount
        user_id: User identifier
        merchant_id: Merchant identifier
        **kwargs: Additional parameters
        
    Returns:
        Fraud detection result
    """
    logger.info(f"Executing fraud detection for transaction: {transaction_id}")
    
    # TODO: Integrate with actual fraud detection models
    # For now, return mock result
    result = {
        "transaction_id": transaction_id,
        "risk_score": 0.15,
        "is_fraud": False,
        "confidence": 0.92,
        "model_used": "isolation_forest"
    }
    
    return result


def register_fraud_detection_tool():
    """Register fraud detection tool with MCP registry"""
    tool_registry.register_tool(
        name="fraud_detection",
        description="Perform real-time fraud detection on a transaction",
        input_schema={
            "type": "object",
            "properties": {
                "transaction_id": {
                    "type": "string",
                    "description": "Unique transaction identifier"
                },
                "amount": {
                    "type": "number",
                    "description": "Transaction amount"
                },
                "user_id": {
                    "type": "string",
                    "description": "User identifier"
                },
                "merchant_id": {
                    "type": "string",
                    "description": "Merchant identifier"
                }
            },
            "required": ["transaction_id", "amount", "user_id", "merchant_id"]
        },
        handler=fraud_detection_handler
    )
    logger.info("Fraud detection tool registered")


# Auto-register on import
register_fraud_detection_tool()
```

Create `core/apis/plugins/mcp_tools/model_management_tool.py`:

```python
"""
Model Management MCP Tool
Tool for managing fraud detection models via MCP
"""

from typing import Dict, Any, List
from core.apis.modules.mcp.tools import tool_registry
import logging

logger = logging.getLogger(__name__)


async def list_models_handler() -> List[Dict[str, Any]]:
    """
    Handle list models tool execution
    
    Returns:
        List of available models
    """
    logger.info("Listing available fraud detection models")
    
    # TODO: Integrate with actual model registry
    models = [
        {
            "id": "isolation_forest_v1",
            "name": "Isolation Forest",
            "type": "anomaly_detection",
            "status": "active",
            "accuracy": 0.95
        },
        {
            "id": "lstm_v1",
            "name": "LSTM Sequence Model",
            "type": "sequence_detection",
            "status": "active",
            "accuracy": 0.93
        }
    ]
    
    return models


def register_model_management_tool():
    """Register model management tool with MCP registry"""
    tool_registry.register_tool(
        name="list_models",
        description="List all available fraud detection models",
        input_schema={
            "type": "object",
            "properties": {},
            "required": []
        },
        handler=list_models_handler
    )
    logger.info("Model management tool registered")


# Auto-register on import
register_model_management_tool()
```

### Step 7: Create MCP Routes

Create `core/apis/services/mcp_routes.py`:

```python
"""
MCP API Routes
FastAPI routes for MCP protocol endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from core.apis.modules.mcp.server import mcp_server
from core.apis.modules.mcp.models import (
    MCPListToolsResponse,
    MCPCallToolRequest,
    MCPCallToolResponse
)
from core.apis.services.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/mcp", tags=["MCP"])


@router.get("/tools", response_model=MCPListToolsResponse)
async def list_tools(current_user: dict = Depends(get_current_user)):
    """
    List all available MCP tools
    
    Requires authentication.
    """
    try:
        response = await mcp_server.list_tools()
        return response
    except Exception as e:
        logger.error(f"Error listing MCP tools: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tools/call", response_model=MCPCallToolResponse)
async def call_tool(
    request: MCPCallToolRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Call an MCP tool
    
    Requires authentication.
    """
    try:
        response = await mcp_server.call_tool(
            name=request.name,
            arguments=request.arguments or {}
        )
        return response
    except ValueError as e:
        logger.error(f"Tool not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error calling MCP tool: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def mcp_health():
    """
    MCP service health check
    """
    return {
        "status": "healthy",
        "service": "mcp",
        "tools_registered": len(mcp_server.tool_registry.list_tools())
    }
```

### Step 8: Register MCP Routes and Tools

Update `core/apis/services/main.py`:

Add imports at the top:

```python
# MCP Routes
from .mcp_routes import router as mcp_router

# Import MCP tools to register them
from core.apis.plugins.mcp_tools import fraud_detection_tool
from core.apis.plugins.mcp_tools import model_management_tool
```

Add router registration:

```python
# Include MCP router
app.include_router(mcp_router)
```

### Step 9: Update Configuration

Add MCP configuration to `core/configs/settings.py`:

```python
# MCP Configuration
MCP_ENABLED: bool = os.getenv("MCP_ENABLED", "true").lower() == "true"
MCP_PORT: int = int(os.getenv("MCP_PORT", "8001"))
MCP_AUTH_REQUIRED: bool = os.getenv("MCP_AUTH_REQUIRED", "true").lower() == "true"
```

### Step 10: Create Module Init Files

Create `core/apis/modules/mcp/__init__.py`:

```python
"""
MCP Module
Model Context Protocol implementation
"""

from .server import mcp_server
from .tools import tool_registry
from .models import (
    MCPTool,
    MCPListToolsResponse,
    MCPCallToolRequest,
    MCPCallToolResponse
)

__all__ = [
    "mcp_server",
    "tool_registry",
    "MCPTool",
    "MCPListToolsResponse",
    "MCPCallToolRequest",
    "MCPCallToolResponse"
]
```

Create `core/apis/plugins/mcp_tools/__init__.py`:

```python
"""
MCP Tools Plugin Module
"""

# Import tools to trigger registration
from . import fraud_detection_tool
from . import model_management_tool

__all__ = [
    "fraud_detection_tool",
    "model_management_tool"
]
```

---

## 🚀 How to Run

### Prerequisites

- Python 3.9+
- FastAPI application running
- PostgreSQL database (for authentication)
- Dependencies installed

### Step 1: Install Dependencies

```bash
cd /Users/gurkanfikretgunak/Documents/GitHub/dafu
pip install -r requirements.txt
```

### Step 2: Set Environment Variables

Create or update `.env` file:

```bash
# MCP Configuration
MCP_ENABLED=true
MCP_PORT=8001
MCP_AUTH_REQUIRED=true

# Database (for authentication)
DATABASE_URL=postgresql://dafu:dafu_secure_password@localhost:5432/dafu

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### Step 3: Start PostgreSQL (if not running)

```bash
docker run -d --name dafu-postgres \
  -e POSTGRES_USER=dafu \
  -e POSTGRES_PASSWORD=dafu_secure_password \
  -e POSTGRES_DB=dafu \
  -p 5432:5432 \
  postgres:15-alpine
```

### Step 4: Initialize Database

```bash
cd core/apis/services
python -c "from database import init_db; init_db()"
```

### Step 5: Start FastAPI Server

```bash
cd core/apis/services
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 6: Verify MCP Endpoints

Check health endpoint:

```bash
curl http://localhost:8000/api/v1/mcp/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "mcp",
  "tools_registered": 2
}
```

### Step 7: Access API Documentation

Open browser to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Navigate to **MCP** section to see available endpoints.

---

## 🧪 How to Test

### Test 1: Health Check (No Auth Required)

```bash
curl -X GET "http://localhost:8000/api/v1/mcp/health"
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "mcp",
  "tools_registered": 2
}
```

### Test 2: List Tools (Auth Required)

First, get authentication token:

```bash
# Login
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
```

List tools:

```bash
curl -X GET "http://localhost:8000/api/v1/mcp/tools" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "tools": [
    {
      "name": "fraud_detection",
      "description": "Perform real-time fraud detection on a transaction",
      "inputSchema": {
        "type": "object",
        "properties": {
          "transaction_id": {"type": "string"},
          "amount": {"type": "number"},
          "user_id": {"type": "string"},
          "merchant_id": {"type": "string"}
        },
        "required": ["transaction_id", "amount", "user_id", "merchant_id"]
      }
    },
    {
      "name": "list_models",
      "description": "List all available fraud detection models",
      "inputSchema": {
        "type": "object",
        "properties": {},
        "required": []
      }
    }
  ]
}
```

### Test 3: Call Fraud Detection Tool

```bash
curl -X POST "http://localhost:8000/api/v1/mcp/tools/call" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "fraud_detection",
    "arguments": {
      "transaction_id": "txn_12345",
      "amount": 99.99,
      "user_id": "user_123",
      "merchant_id": "merchant_456"
    }
  }'
```

**Expected Response:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"transaction_id\": \"txn_12345\", \"risk_score\": 0.15, \"is_fraud\": false, \"confidence\": 0.92, \"model_used\": \"isolation_forest\"}"
    }
  ],
  "isError": false
}
```

### Test 4: Call List Models Tool

```bash
curl -X POST "http://localhost:8000/api/v1/mcp/tools/call" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "list_models",
    "arguments": {}
  }'
```

**Expected Response:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "[{\"id\": \"isolation_forest_v1\", \"name\": \"Isolation Forest\", \"type\": \"anomaly_detection\", \"status\": \"active\", \"accuracy\": 0.95}, {\"id\": \"lstm_v1\", \"name\": \"LSTM Sequence Model\", \"type\": \"sequence_detection\", \"status\": \"active\", \"accuracy\": 0.93}]"
    }
  ],
  "isError": false
}
```

### Test 5: Error Handling - Invalid Tool

```bash
curl -X POST "http://localhost:8000/api/v1/mcp/tools/call" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "non_existent_tool",
    "arguments": {}
  }'
```

**Expected Response:**
```json
{
  "detail": "Tool non_existent_tool not found"
}
```

### Test 6: Error Handling - Missing Authentication

```bash
curl -X GET "http://localhost:8000/api/v1/mcp/tools"
```

**Expected Response:**
```json
{
  "detail": "Not authenticated"
}
```

### Automated Testing with pytest

Create `tests/test_mcp.py`:

```python
import pytest
from httpx import AsyncClient
from core.apis.services.main import app


@pytest.mark.asyncio
async def test_mcp_health():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/mcp/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "tools_registered" in data


@pytest.mark.asyncio
async def test_list_tools_authenticated(authenticated_client):
    response = await authenticated_client.get("/api/v1/mcp/tools")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert len(data["tools"]) > 0


@pytest.mark.asyncio
async def test_call_fraud_detection_tool(authenticated_client):
    response = await authenticated_client.post(
        "/api/v1/mcp/tools/call",
        json={
            "name": "fraud_detection",
            "arguments": {
                "transaction_id": "test_txn",
                "amount": 100.0,
                "user_id": "test_user",
                "merchant_id": "test_merchant"
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "content" in data
    assert data["isError"] == False


@pytest.mark.asyncio
async def test_call_invalid_tool(authenticated_client):
    response = await authenticated_client.post(
        "/api/v1/mcp/tools/call",
        json={
            "name": "invalid_tool",
            "arguments": {}
        }
    )
    assert response.status_code == 404
```

Run tests:

```bash
pytest tests/test_mcp.py -v
```

---

## 📡 API Endpoints

### GET `/api/v1/mcp/health`

Health check endpoint (no authentication required).

**Response:**
```json
{
  "status": "healthy",
  "service": "mcp",
  "tools_registered": 2
}
```

### GET `/api/v1/mcp/tools`

List all available MCP tools (authentication required).

**Response:**
```json
{
  "tools": [
    {
      "name": "fraud_detection",
      "description": "Perform real-time fraud detection",
      "inputSchema": {...}
    }
  ]
}
```

### POST `/api/v1/mcp/tools/call`

Call an MCP tool (authentication required).

**Request Body:**
```json
{
  "name": "fraud_detection",
  "arguments": {
    "transaction_id": "txn_123",
    "amount": 99.99,
    "user_id": "user_123",
    "merchant_id": "merchant_456"
  }
}
```

**Response:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "..."
    }
  ],
  "isError": false
}
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_ENABLED` | `true` | Enable/disable MCP feature |
| `MCP_PORT` | `8001` | MCP server port (if separate) |
| `MCP_AUTH_REQUIRED` | `true` | Require authentication for MCP endpoints |

### Tool Registration

Tools are automatically registered when imported. To add a new tool:

1. Create tool file in `core/apis/plugins/mcp_tools/`
2. Implement handler function
3. Call `register_tool()` in the file
4. Import the module in `main.py`

---

## 🐛 Troubleshooting

### Issue: Tools Not Registered

**Symptoms:** `/api/v1/mcp/tools` returns empty list

**Solution:**
1. Check that tool modules are imported in `main.py`
2. Verify tool registration functions are called
3. Check logs for registration errors

### Issue: Authentication Errors

**Symptoms:** 401 Unauthorized responses

**Solution:**
1. Verify JWT token is valid
2. Check token expiration
3. Ensure `MCP_AUTH_REQUIRED=true` matches your setup

### Issue: Tool Execution Fails

**Symptoms:** `isError: true` in response

**Solution:**
1. Check tool handler implementation
2. Verify input arguments match schema
3. Review server logs for detailed errors

### Issue: Import Errors

**Symptoms:** ModuleNotFoundError when starting server

**Solution:**
1. Verify all dependencies are installed
2. Check Python path configuration
3. Ensure all `__init__.py` files exist

---

## 📚 Additional Resources

- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [DAFU API Documentation](./API_USAGE_GUIDE.md)

---

## 🔄 Next Steps

1. ✅ Implement core MCP server
2. ✅ Create tool registry
3. ✅ Add fraud detection tool
4. ✅ Add model management tool
5. 🔄 Integrate with actual ML models
6. 🔄 Add more specialized tools
7. 🔄 Implement tool caching
8. 🔄 Add rate limiting for tools
9. 🔄 Create MCP client SDK

---

**DAFU MCP Feature** - Model Context Protocol Integration 🚀

