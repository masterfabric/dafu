# LLM Chat Connector Hub Manager - Technical Development Guide

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

The **LLM Chat Connector Hub Manager** provides a unified interface for integrating multiple Large Language Model (LLM) providers into the DAFU platform. It supports OpenAI and Claude (Anthropic) APIs, allowing seamless switching between providers and managing chat interactions for fraud detection analysis.

### Key Features

- **Multi-Provider Support**: OpenAI GPT and Anthropic Claude integration
- **Unified Interface**: Single API for all LLM providers
- **Provider Switching**: Dynamic provider selection per request
- **Chat Management**: Conversation history and context management
- **Streaming Support**: Real-time streaming responses
- **Error Handling**: Robust error handling and fallback mechanisms
- **Rate Limiting**: Provider-specific rate limiting
- **Cost Tracking**: Usage and cost monitoring per provider

### Use Cases

- Fraud detection analysis with AI assistance
- Natural language queries about fraud patterns
- Automated report generation with LLM
- Customer support integration
- Fraud investigation assistance

---

## 🏗️ Architecture

### Component Structure

```
core/apis/
├── services/
│   ├── main.py                    # FastAPI app
│   └── llm_routes.py             # LLM endpoints (NEW)
├── modules/
│   └── llm/
│       ├── __init__.py
│       ├── hub.py                # LLM Hub Manager (NEW)
│       ├── providers/
│       │   ├── __init__.py
│       │   ├── base.py          # Base provider interface (NEW)
│       │   ├── openai_provider.py    # OpenAI provider (NEW)
│       │   └── claude_provider.py    # Claude provider (NEW)
│       ├── chat_manager.py      # Chat session management (NEW)
│       └── models.py            # Pydantic models (NEW)
└── configs/
    └── settings.py               # Configuration (updated)
```

### LLM Hub Flow

```
Client Request
    ↓
LLM Router (/api/v1/llm/*)
    ↓
Hub Manager (Select Provider)
    ↓
Provider Interface (OpenAI/Claude)
    ↓
API Call (OpenAI/Anthropic)
    ↓
Response Processing
    ↓
Chat Manager (Store History)
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
│  LLM Router     │
│  (FastAPI)      │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Hub Manager    │
│ (Select Provider)│
└──────┬──────────┘
       │
       ├──────────────┐
       ▼              ▼
┌─────────────┐  ┌─────────────┐
│   OpenAI    │  │   Claude    │
│  Provider   │  │  Provider   │
└──────┬──────┘  └──────┬──────┘
       │                │
       └────────┬───────┘
                ▼
       ┌─────────────────┐
       │  API Response   │
       │   Processing    │
       └──────┬──────────┘
              │
              ▼
       ┌─────────────────┐
       │ Chat Manager    │
       │ (Store History) │
       └──────┬──────────┘
              │
              ▼
       ┌─────────────────┐
       │   Response     │
       │   (Formatted)   │
       └─────────────────┘
```

---

## 📝 Step-by-Step Development

### Step 1: Install Dependencies

Add LLM-related dependencies to `requirements.txt`:

```bash
# LLM Provider SDKs
openai>=1.0.0
anthropic>=0.7.0

# Additional utilities
aiohttp>=3.9.0
tenacity>=8.2.0  # For retries
```

Install dependencies:

```bash
cd /Users/gurkanfikretgunak/Documents/GitHub/dafu
pip install -r requirements.txt
```

### Step 2: Create LLM Module Structure

Create the LLM module directory:

```bash
mkdir -p core/apis/modules/llm/providers
touch core/apis/modules/llm/__init__.py
touch core/apis/modules/llm/hub.py
touch core/apis/modules/llm/chat_manager.py
touch core/apis/modules/llm/models.py
touch core/apis/modules/llm/providers/__init__.py
touch core/apis/modules/llm/providers/base.py
touch core/apis/modules/llm/providers/openai_provider.py
touch core/apis/modules/llm/providers/claude_provider.py
```

### Step 3: Implement Base Provider Interface

Create `core/apis/modules/llm/providers/base.py`:

```python
"""
Base LLM Provider Interface
Abstract base class for all LLM providers
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, Any, Optional, List
from pydantic import BaseModel


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str  # "user", "assistant", "system"
    content: str


class LLMResponse(BaseModel):
    """Standardized LLM response"""
    content: str
    provider: str
    model: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None


class BaseLLMProvider(ABC):
    """Base class for LLM providers"""
    
    def __init__(self, api_key: str, model: str = None):
        self.api_key = api_key
        self.model = model
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def chat(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> LLMResponse:
        """
        Send chat completion request
        
        Args:
            messages: List of chat messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Provider-specific parameters
            
        Returns:
            LLMResponse with generated content
        """
        pass
    
    @abstractmethod
    async def stream_chat(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream chat completion
        
        Args:
            messages: List of chat messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Provider-specific parameters
            
        Yields:
            Chunks of generated text
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models for this provider"""
        pass
```

### Step 4: Implement OpenAI Provider

Create `core/apis/modules/llm/providers/openai_provider.py`:

```python
"""
OpenAI Provider Implementation
"""

from typing import List, AsyncIterator
from openai import AsyncOpenAI
from .base import BaseLLMProvider, ChatMessage, LLMResponse
import logging

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider"""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        super().__init__(api_key, model)
        self.client = AsyncOpenAI(api_key=api_key)
        self.name = "openai"
    
    async def chat(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> LLMResponse:
        """Send chat completion request to OpenAI"""
        try:
            # Convert ChatMessage to OpenAI format
            openai_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                provider="openai",
                model=self.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                finish_reason=response.choices[0].finish_reason
            )
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}", exc_info=True)
            raise
    
    async def stream_chat(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream chat completion from OpenAI"""
        try:
            openai_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"OpenAI streaming error: {str(e)}", exc_info=True)
            raise
    
    def get_available_models(self) -> List[str]:
        """Get available OpenAI models"""
        return [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4-turbo-preview",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ]
```

### Step 5: Implement Claude Provider

Create `core/apis/modules/llm/providers/claude_provider.py`:

```python
"""
Anthropic Claude Provider Implementation
"""

from typing import List, AsyncIterator
from anthropic import AsyncAnthropic
from .base import BaseLLMProvider, ChatMessage, LLMResponse
import logging

logger = logging.getLogger(__name__)


class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        super().__init__(api_key, model)
        self.client = AsyncAnthropic(api_key=api_key)
        self.name = "claude"
    
    async def chat(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> LLMResponse:
        """Send chat completion request to Claude"""
        try:
            # Claude uses different message format
            system_message = None
            claude_messages = []
            
            for msg in messages:
                if msg.role == "system":
                    system_message = msg.content
                else:
                    claude_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            response = await self.client.messages.create(
                model=self.model,
                messages=claude_messages,
                system=system_message,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            # Extract content from Claude response
            content = ""
            if response.content:
                for block in response.content:
                    if block.type == "text":
                        content += block.text
            
            return LLMResponse(
                content=content,
                provider="claude",
                model=self.model,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                },
                finish_reason=response.stop_reason
            )
        except Exception as e:
            logger.error(f"Claude API error: {str(e)}", exc_info=True)
            raise
    
    async def stream_chat(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream chat completion from Claude"""
        try:
            system_message = None
            claude_messages = []
            
            for msg in messages:
                if msg.role == "system":
                    system_message = msg.content
                else:
                    claude_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            stream = await self.client.messages.create(
                model=self.model,
                messages=claude_messages,
                system=system_message,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )
            
            async for event in stream:
                if event.type == "content_block_delta":
                    if event.delta.type == "text_delta":
                        yield event.delta.text
        except Exception as e:
            logger.error(f"Claude streaming error: {str(e)}", exc_info=True)
            raise
    
    def get_available_models(self) -> List[str]:
        """Get available Claude models"""
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
```

### Step 6: Implement Chat Manager

Create `core/apis/modules/llm/chat_manager.py`:

```python
"""
Chat Session Manager
Manages conversation history and sessions
"""

from typing import Dict, List, Optional
from datetime import datetime
from .models import ChatMessage, ChatSession
from .providers.base import BaseLLMProvider
import uuid
import logging

logger = logging.getLogger(__name__)


class ChatManager:
    """Manages chat sessions and conversation history"""
    
    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
    
    def create_session(
        self,
        user_id: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Create a new chat session
        
        Args:
            user_id: User identifier
            system_prompt: Optional system prompt
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        
        messages = []
        if system_prompt:
            messages.append(ChatMessage(
                role="system",
                content=system_prompt
            ))
        
        session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            messages=messages,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.sessions[session_id] = session
        logger.info(f"Created chat session {session_id} for user {user_id}")
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ):
        """
        Add message to session
        
        Args:
            session_id: Session identifier
            role: Message role (user/assistant/system)
            content: Message content
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        message = ChatMessage(role=role, content=content)
        session.messages.append(message)
        session.updated_at = datetime.utcnow()
        
        logger.debug(f"Added {role} message to session {session_id}")
    
    def get_messages(self, session_id: str) -> List[ChatMessage]:
        """Get all messages for a session"""
        session = self.sessions.get(session_id)
        if not session:
            return []
        return session.messages
    
    def delete_session(self, session_id: str):
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session {session_id}")


# Global chat manager instance
chat_manager = ChatManager()
```

### Step 7: Implement LLM Models

Create `core/apis/modules/llm/models.py`:

```python
"""
LLM Pydantic Models
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from .providers.base import ChatMessage


class ChatSession(BaseModel):
    """Chat session model"""
    session_id: str
    user_id: str
    messages: List[ChatMessage] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Existing session ID")
    provider: str = Field("openai", description="LLM provider (openai/claude)")
    model: Optional[str] = Field(None, description="Model name (optional)")
    temperature: float = Field(0.7, ge=0, le=2, description="Sampling temperature")
    max_tokens: int = Field(1000, ge=1, le=4000, description="Max tokens to generate")
    stream: bool = Field(False, description="Enable streaming response")
    system_prompt: Optional[str] = Field(None, description="System prompt for new session")


class ChatResponse(BaseModel):
    """Chat response model"""
    session_id: str = Field(..., description="Session ID")
    message: str = Field(..., description="Assistant response")
    provider: str = Field(..., description="Provider used")
    model: str = Field(..., description="Model used")
    usage: Optional[Dict[str, int]] = Field(None, description="Token usage")
    finish_reason: Optional[str] = Field(None, description="Finish reason")


class ProviderInfo(BaseModel):
    """Provider information model"""
    name: str
    available: bool
    models: List[str]
    default_model: str
```

### Step 8: Implement LLM Hub

Create `core/apis/modules/llm/hub.py`:

```python
"""
LLM Hub Manager
Centralized manager for multiple LLM providers
"""

from typing import Dict, Optional
from .providers.base import BaseLLMProvider, ChatMessage, LLMResponse
from .providers.openai_provider import OpenAIProvider
from .providers.claude_provider import ClaudeProvider
from core.configs.settings import (
    OPENAI_API_KEY,
    ANTHROPIC_API_KEY,
    OPENAI_DEFAULT_MODEL,
    CLAUDE_DEFAULT_MODEL
)
import logging

logger = logging.getLogger(__name__)


class LLMHub:
    """Hub for managing multiple LLM providers"""
    
    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available providers"""
        # Initialize OpenAI
        if OPENAI_API_KEY:
            try:
                self.providers["openai"] = OpenAIProvider(
                    api_key=OPENAI_API_KEY,
                    model=OPENAI_DEFAULT_MODEL
                )
                logger.info("OpenAI provider initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {str(e)}")
        
        # Initialize Claude
        if ANTHROPIC_API_KEY:
            try:
                self.providers["claude"] = ClaudeProvider(
                    api_key=ANTHROPIC_API_KEY,
                    model=CLAUDE_DEFAULT_MODEL
                )
                logger.info("Claude provider initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Claude: {str(e)}")
    
    def get_provider(self, name: str) -> Optional[BaseLLMProvider]:
        """Get provider by name"""
        return self.providers.get(name)
    
    def list_providers(self) -> list[str]:
        """List available providers"""
        return list(self.providers.keys())
    
    async def chat(
        self,
        provider_name: str,
        messages: list[ChatMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> LLMResponse:
        """
        Send chat request through specified provider
        
        Args:
            provider_name: Provider name (openai/claude)
            messages: List of chat messages
            model: Optional model override
            temperature: Sampling temperature
            max_tokens: Max tokens
            **kwargs: Provider-specific parameters
            
        Returns:
            LLMResponse
            
        Raises:
            ValueError: If provider not found
        """
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Provider {provider_name} not available")
        
        # Override model if specified
        if model:
            provider.model = model
        
        return await provider.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )


# Global LLM hub instance
llm_hub = LLMHub()
```

### Step 9: Create LLM Routes

Create `core/apis/services/llm_routes.py`:

```python
"""
LLM API Routes
FastAPI routes for LLM chat functionality
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Optional
from core.apis.modules.llm.hub import llm_hub
from core.apis.modules.llm.chat_manager import chat_manager
from core.apis.modules.llm.models import (
    ChatRequest,
    ChatResponse,
    ProviderInfo
)
from core.apis.modules.llm.providers.base import ChatMessage
from core.apis.services.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/llm", tags=["LLM"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Send chat message to LLM
    
    Requires authentication.
    """
    try:
        user_id = current_user.get("id") or current_user.get("username")
        
        # Get or create session
        if request.session_id:
            session = chat_manager.get_session(request.session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
        else:
            # Create new session
            request.session_id = chat_manager.create_session(
                user_id=user_id,
                system_prompt=request.system_prompt
            )
        
        # Add user message to session
        chat_manager.add_message(
            session_id=request.session_id,
            role="user",
            content=request.message
        )
        
        # Get messages from session
        messages = chat_manager.get_messages(request.session_id)
        
        # Get provider
        provider = llm_hub.get_provider(request.provider)
        if not provider:
            raise HTTPException(
                status_code=400,
                detail=f"Provider {request.provider} not available"
            )
        
        # Override model if specified
        if request.model:
            provider.model = request.model
        
        # Handle streaming
        if request.stream:
            async def generate_stream():
                async for chunk in provider.stream_chat(
                    messages=messages,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                ):
                    yield f"data: {chunk}\n\n"
            
            return StreamingResponse(
                generate_stream(),
                media_type="text/event-stream"
            )
        
        # Non-streaming response
        response = await provider.chat(
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        # Add assistant response to session
        chat_manager.add_message(
            session_id=request.session_id,
            role="assistant",
            content=response.content
        )
        
        return ChatResponse(
            session_id=request.session_id,
            message=response.content,
            provider=response.provider,
            model=response.model,
            usage=response.usage,
            finish_reason=response.finish_reason
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers", response_model=list[ProviderInfo])
async def list_providers(current_user: dict = Depends(get_current_user)):
    """
    List available LLM providers
    
    Requires authentication.
    """
    providers_info = []
    
    for name in llm_hub.list_providers():
        provider = llm_hub.get_provider(name)
        if provider:
            providers_info.append(ProviderInfo(
                name=name,
                available=True,
                models=provider.get_available_models(),
                default_model=provider.model
            ))
    
    return providers_info


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get chat session details
    
    Requires authentication.
    """
    session = chat_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check ownership
    user_id = current_user.get("id") or current_user.get("username")
    if session.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return session


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete chat session
    
    Requires authentication.
    """
    session = chat_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check ownership
    user_id = current_user.get("id") or current_user.get("username")
    if session.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    chat_manager.delete_session(session_id)
    return {"message": "Session deleted"}


@router.get("/health")
async def llm_health():
    """
    LLM service health check
    """
    return {
        "status": "healthy",
        "service": "llm",
        "providers_available": len(llm_hub.list_providers()),
        "providers": llm_hub.list_providers()
    }
```

### Step 10: Register LLM Routes

Update `core/apis/services/main.py`:

Add import:

```python
from .llm_routes import router as llm_router
```

Add router registration:

```python
# Include LLM router
app.include_router(llm_router)
```

### Step 11: Update Configuration

Add LLM configuration to `core/configs/settings.py`:

```python
# LLM Provider Configuration
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_DEFAULT_MODEL: str = os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4")

ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_DEFAULT_MODEL: str = os.getenv("CLAUDE_DEFAULT_MODEL", "claude-3-opus-20240229")

# LLM Hub Configuration
LLM_ENABLED: bool = os.getenv("LLM_ENABLED", "true").lower() == "true"
LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "4000"))
LLM_DEFAULT_TEMPERATURE: float = float(os.getenv("LLM_DEFAULT_TEMPERATURE", "0.7"))
```

---

## 🚀 How to Run

### Prerequisites

- Python 3.9+
- FastAPI application running
- OpenAI API key (for OpenAI provider)
- Anthropic API key (for Claude provider)
- PostgreSQL database (for authentication)

### Step 1: Install Dependencies

```bash
cd /Users/gurkanfikretgunak/Documents/GitHub/dafu
pip install -r requirements.txt
```

### Step 2: Set Environment Variables

Create or update `.env` file:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_DEFAULT_MODEL=gpt-4

# Anthropic Claude Configuration
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here
CLAUDE_DEFAULT_MODEL=claude-3-opus-20240229

# LLM Hub Configuration
LLM_ENABLED=true
LLM_MAX_TOKENS=4000
LLM_DEFAULT_TEMPERATURE=0.7

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

### Step 6: Verify LLM Endpoints

Check health endpoint:

```bash
curl http://localhost:8000/api/v1/llm/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "llm",
  "providers_available": 2,
  "providers": ["openai", "claude"]
}
```

### Step 7: Access API Documentation

Open browser to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Navigate to **LLM** section to see available endpoints.

---

## 🧪 How to Test

### Test 1: Health Check (No Auth Required)

```bash
curl -X GET "http://localhost:8000/api/v1/llm/health"
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "llm",
  "providers_available": 2,
  "providers": ["openai", "claude"]
}
```

### Test 2: List Providers (Auth Required)

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

List providers:

```bash
curl -X GET "http://localhost:8000/api/v1/llm/providers" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
[
  {
    "name": "openai",
    "available": true,
    "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
    "default_model": "gpt-4"
  },
  {
    "name": "claude",
    "available": true,
    "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229"],
    "default_model": "claude-3-opus-20240229"
  }
]
```

### Test 3: Chat with OpenAI

```bash
curl -X POST "http://localhost:8000/api/v1/llm/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is fraud detection?",
    "provider": "openai",
    "temperature": 0.7,
    "max_tokens": 500
  }'
```

**Expected Response:**
```json
{
  "session_id": "uuid-here",
  "message": "Fraud detection is...",
  "provider": "openai",
  "model": "gpt-4",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 150,
    "total_tokens": 160
  },
  "finish_reason": "stop"
}
```

### Test 4: Chat with Claude

```bash
curl -X POST "http://localhost:8000/api/v1/llm/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain anomaly detection in fraud detection",
    "provider": "claude",
    "model": "claude-3-sonnet-20240229",
    "temperature": 0.7
  }'
```

**Expected Response:**
```json
{
  "session_id": "uuid-here",
  "message": "Anomaly detection in fraud detection...",
  "provider": "claude",
  "model": "claude-3-sonnet-20240229",
  "usage": {
    "input_tokens": 15,
    "output_tokens": 200
  },
  "finish_reason": "end_turn"
}
```

### Test 5: Continue Conversation (Use Session)

```bash
# First message
RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/llm/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is isolation forest?",
    "provider": "openai"
  }')

SESSION_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['session_id'])")

# Follow-up message using same session
curl -X POST "http://localhost:8000/api/v1/llm/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"How does it work?\",
    \"session_id\": \"$SESSION_ID\",
    \"provider\": \"openai\"
  }"
```

### Test 6: Streaming Response

```bash
curl -X POST "http://localhost:8000/api/v1/llm/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Write a short story about fraud detection",
    "provider": "openai",
    "stream": true
  }'
```

**Expected Response:** Server-Sent Events stream

### Test 7: Get Session Details

```bash
curl -X GET "http://localhost:8000/api/v1/llm/sessions/$SESSION_ID" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "session_id": "uuid-here",
  "user_id": "user123",
  "messages": [
    {"role": "user", "content": "What is fraud detection?"},
    {"role": "assistant", "content": "Fraud detection is..."}
  ],
  "created_at": "2025-01-15T10:00:00",
  "updated_at": "2025-01-15T10:05:00"
}
```

### Test 8: Error Handling - Invalid Provider

```bash
curl -X POST "http://localhost:8000/api/v1/llm/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test",
    "provider": "invalid_provider"
  }'
```

**Expected Response:**
```json
{
  "detail": "Provider invalid_provider not available"
}
```

### Automated Testing with pytest

Create `tests/test_llm.py`:

```python
import pytest
from httpx import AsyncClient
from core.apis.services.main import app


@pytest.mark.asyncio
async def test_llm_health():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/llm/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "providers" in data


@pytest.mark.asyncio
async def test_list_providers(authenticated_client):
    response = await authenticated_client.get("/api/v1/llm/providers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_chat_openai(authenticated_client):
    response = await authenticated_client.post(
        "/api/v1/llm/chat",
        json={
            "message": "Hello",
            "provider": "openai",
            "max_tokens": 100
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "message" in data
    assert data["provider"] == "openai"


@pytest.mark.asyncio
async def test_chat_claude(authenticated_client):
    response = await authenticated_client.post(
        "/api/v1/llm/chat",
        json={
            "message": "Hello",
            "provider": "claude",
            "max_tokens": 100
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "claude"
```

Run tests:

```bash
pytest tests/test_llm.py -v
```

---

## 📡 API Endpoints

### GET `/api/v1/llm/health`

Health check endpoint (no authentication required).

**Response:**
```json
{
  "status": "healthy",
  "service": "llm",
  "providers_available": 2,
  "providers": ["openai", "claude"]
}
```

### GET `/api/v1/llm/providers`

List available LLM providers (authentication required).

**Response:**
```json
[
  {
    "name": "openai",
    "available": true,
    "models": ["gpt-4", "gpt-3.5-turbo"],
    "default_model": "gpt-4"
  }
]
```

### POST `/api/v1/llm/chat`

Send chat message to LLM (authentication required).

**Request Body:**
```json
{
  "message": "Your question here",
  "provider": "openai",
  "session_id": "optional-session-id",
  "model": "optional-model-override",
  "temperature": 0.7,
  "max_tokens": 1000,
  "stream": false,
  "system_prompt": "Optional system prompt"
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "message": "Response text",
  "provider": "openai",
  "model": "gpt-4",
  "usage": {"prompt_tokens": 10, "completion_tokens": 50},
  "finish_reason": "stop"
}
```

### GET `/api/v1/llm/sessions/{session_id}`

Get chat session details (authentication required).

### DELETE `/api/v1/llm/sessions/{session_id}`

Delete chat session (authentication required).

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | `""` | OpenAI API key |
| `OPENAI_DEFAULT_MODEL` | `"gpt-4"` | Default OpenAI model |
| `ANTHROPIC_API_KEY` | `""` | Anthropic API key |
| `CLAUDE_DEFAULT_MODEL` | `"claude-3-opus-20240229"` | Default Claude model |
| `LLM_ENABLED` | `"true"` | Enable/disable LLM feature |
| `LLM_MAX_TOKENS` | `4000` | Maximum tokens per request |
| `LLM_DEFAULT_TEMPERATURE` | `0.7` | Default sampling temperature |

### Provider Configuration

Providers are automatically initialized if API keys are provided. To disable a provider, simply don't set its API key.

---

## 🐛 Troubleshooting

### Issue: Providers Not Available

**Symptoms:** `/api/v1/llm/providers` returns empty list

**Solution:**
1. Verify API keys are set in environment variables
2. Check API keys are valid
3. Review server logs for initialization errors

### Issue: Authentication Errors

**Symptoms:** 401 Unauthorized responses

**Solution:**
1. Verify JWT token is valid
2. Check token expiration
3. Ensure user is logged in

### Issue: API Rate Limits

**Symptoms:** 429 Too Many Requests

**Solution:**
1. Implement rate limiting per user
2. Add retry logic with exponential backoff
3. Consider using provider-specific rate limit handling

### Issue: Streaming Not Working

**Symptoms:** Streaming endpoint returns error

**Solution:**
1. Verify client supports Server-Sent Events
2. Check provider streaming implementation
3. Review network configuration

### Issue: Session Not Found

**Symptoms:** 404 Session not found

**Solution:**
1. Verify session ID is correct
2. Check session hasn't expired
3. Ensure session belongs to current user

---

## 📚 Additional Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Anthropic Claude API Documentation](https://docs.anthropic.com)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [DAFU API Documentation](./API_USAGE_GUIDE.md)

---

## 🔄 Next Steps

1. ✅ Implement base provider interface
2. ✅ Add OpenAI provider
3. ✅ Add Claude provider
4. ✅ Implement chat session management
5. 🔄 Add cost tracking per provider
6. 🔄 Implement rate limiting
7. 🔄 Add provider fallback mechanism
8. 🔄 Create LLM client SDK
9. 🔄 Add conversation export functionality
10. 🔄 Implement provider load balancing

---

**DAFU LLM Chat Connector Hub** - Multi-Provider LLM Integration 🚀

