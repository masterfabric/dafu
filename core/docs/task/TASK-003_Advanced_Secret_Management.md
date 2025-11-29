# [TASK-003] Implement Advanced Secret & Configuration Management

**Status:** `Open`  
**Priority:** `Critical`  
**Owner:** `Project Owner`  
**Assignee:** `Data Engineer`  

---

## 1. Project Owner's Perspective

### Goal
To completely eliminate security risks arising from hardcoded or committed credentials. We must adopt a professional, secure, and flexible configuration strategy that works seamlessly across local development, testing, and containerized production environments.

### User Story
"As a DevOps Engineer, I want the application to be fully configurable via environment variables, with a clear separation between code and configuration, so that I can deploy the same application artifact to any environment without code changes and manage secrets securely using standard orchestration tools."

### Value Proposition
- **Enhanced Security:** Prevents sensitive data (passwords, API keys) from ever being stored in the codebase.
- **Improved Portability:** The application can be deployed anywhere (local, Docker, Kubernetes) without code modification.
- **Simplified Configuration:** Centralizes configuration management through a standard, well-understood mechanism (environment variables).
- **Compliance:** Adheres to industry best practices like the [12-Factor App methodology](https://12factor.net/config), which is often a requirement for enterprise-grade software.

### Acceptance Criteria
- No secrets (passwords, secret keys) are present in any code or configuration files in the repository.
- The application must read all configuration, including database URLs and secret keys, from environment variables.
- A `.env.example` file must exist in the root directory to document all required environment variables.
- The `.env` file must be included in `.gitignore`.
- The application must function correctly in both a local environment (using a `.env` file) and a containerized environment (where variables are injected by the orchestrator).

---

## 2. Technical Analysis & Implementation Plan

### Current State
The project has a `core/configs` directory, which is a good start. However, it's not clear how secrets are managed, and there's a high risk of developers hardcoding values for convenience. We need a formal, secure system.

### Proposed Solution
We will refactor the configuration logic to strictly follow the 12-Factor App methodology. The application code will be modified to read all configuration from environment variables. For developer convenience, we will integrate `python-dotenv` to load these variables from a local `.env` file during development. In production, these variables will be injected directly by the container orchestrator (e.g., Docker Compose, Kubernetes).

### Step-by-Step Implementation
1.  **Add Dependency:** Add `python-dotenv` to the `requirements.txt` file.
2.  **Update `.gitignore`:** Add `.env` to the project's `.gitignore` file to ensure local secret files are never committed.
3.  **Create `.env.example`:** In the project root, create a `.env.example` file. This file will serve as a template, listing all the environment variables the application needs, but with placeholder or empty values.
    ```env
    # .env.example
    # Application Settings
    SECRET_KEY=
    
    # Database Configuration
    DB_USER=dafu
    DB_PASSWORD=
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=dafu
    DATABASE_URL=
    ```
4.  **Refactor Configuration Files:**
    - Modify `core/configs/settings.py` and `core/configs/database.py`.
    - At the top of the main application entry point (e.g., `core/apis/services/main.py`), load the environment variables from the `.env` file:
      ```python
      from dotenv import load_dotenv
      load_dotenv() 
      ```
    - In the configuration files, use `os.getenv()` to read each variable. Provide sensible, non-secret defaults where applicable. For the database URL, construct it from its component parts if the full URL isn't provided.
      ```python
      import os
      
      # Example for settings.py
      SECRET_KEY = os.getenv("SECRET_KEY")
      
      # Example for database.py
      DB_USER = os.getenv("DB_USER", "dafu")
      DB_PASSWORD = os.getenv("DB_PASSWORD")
      # ... etc.
      DATABASE_URL = os.getenv("DATABASE_URL")
      if not DATABASE_URL:
          DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
      ```
5.  **Update Documentation:** Add a new section to `core/docs/docker/DOCKER_SETUP.md` titled "Production Configuration & Secret Management." This section must explain:
    - The role of the `.env` file for local development.
    - The production strategy: secrets are **not** read from a file but are injected as environment variables by the container orchestrator (e.g., using the `environment` key in `docker-compose.yml` or Kubernetes Secrets).

### Key Files & Directories to Modify
- `/requirements.txt` (Add `python-dotenv`)
- `/.gitignore` (Add `.env`)
- `/.env.example` (New file)
- `/core/configs/settings.py`
- `/core/configs/database.py`
- `/core/apis/services/main.py` (Or other main entry point)
- `/core/docs/docker/DOCKER_SETUP.md`

### Testing Strategy
- **Local Test:**
    1. Create a local `.env` file with valid credentials.
    2. Run the application locally and verify it connects to the database and functions correctly.
- **Container Test:**
    1. Modify the `docker-compose.yml` to pass secrets via the `environment` block.
    2. Run `docker-compose up`.
    3. Verify the containerized application starts and functions correctly, reading the configuration injected by Docker Compose.
- **Negative Test:**
    1. Run the application without a `.env` file and without injecting environment variables.
    2. Verify that the application fails to start with a clear error message (e.g., "DATABASE_URL not set" or "SECRET_KEY is missing").

---
## 2.1. Deep Dive: Engineering Perspective

### Strongly-Typed Settings with Pydantic
Using `os.getenv()` is functional but has a major drawback: all values are strings. This requires manual type casting (e.g., `int(os.getenv("DB_PORT"))`), which is error-prone. A much more robust, modern, and Pythonic approach is to use **Pydantic's `BaseSettings`**. This allows us to create a strongly-typed configuration object that automatically reads from environment variables and performs type validation.

### Configuration Source Hierarchy
The application should respect a clear hierarchy for loading configuration:
1.  Environment variables (highest priority).
2.  Secrets from a dedicated secret manager like HashiCorp Vault.
3.  Values in the `.env` file (for local development overrides).
4.  Default values defined in the Pydantic `AppSettings` class (lowest priority).

### NEW: Integration with HashiCorp Vault
For a true enterprise-grade security posture, we will integrate with **HashiCorp Vault**. This moves secrets entirely out of environment variables and into a dedicated, secure, and auditable system.

**Technical Strategy:**
1.  **Add Vault Client:** Add the official HashiCorp Vault client library to `requirements.txt`: `hvac`.
2.  **Vault Authentication:** The application needs to authenticate with Vault to get a token. For containerized environments, the best methods are **AppRole** or the **Kubernetes Auth Method**. The application would be configured with a `ROLE_ID` and `SECRET_ID` (for AppRole) or a service account token (for K8s) via environment variables.
3.  **Extend Pydantic Settings:** We will create a custom `vault_config_source` for our Pydantic `BaseSettings` model. This function will be responsible for fetching secrets from Vault and making them available to Pydantic.

**Updated Pydantic Settings Example:**
```python
# core/configs/settings.py
import os
import hvac
from pydantic import PostgresDsn, Field
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource

def get_vault_secrets() -> dict:
    """
    Fetches secrets from HashiCorp Vault.
    """
    try:
        vault_addr = os.getenv("VAULT_ADDR")
        role_id = os.getenv("VAULT_ROLE_ID")
        secret_id = os.getenv("VAULT_SECRET_ID")

        if not all([vault_addr, role_id, secret_id]):
            # Not in a Vault-enabled environment, return empty dict
            return {}

        client = hvac.Client(url=vault_addr)
        
        # Authenticate using AppRole
        client.auth.approle.login(role_id=role_id, secret_id=secret_id)
        
        if not client.is_authenticated():
            raise ConnectionError("Failed to authenticate with Vault")

        # Read secrets from a specific path, e.g., 'kv/data/dafu'
        # The actual data is in the 'data']['data'] part of the response
        secrets = client.secrets.kv.v2.read_secret_version(path='dafu')
        return secrets['data']['data']

    except Exception as e:
        # In a real app, use structured logging here
        print(f"Warning: Could not fetch secrets from Vault: {e}")
        return {}

class VaultConfigSource(PydanticBaseSettingsSource):
    """
    A Pydantic settings source that loads secrets from HashiCorp Vault.
    """
    def __call__(self) -> dict:
        return get_vault_secrets()

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # Config fields will be populated from Vault first, then .env, then defaults
    SECRET_KEY: str
    DB_PASSWORD: str
    DB_USER: str = "dafu"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "dafu"

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        # Define the hierarchy: Vault -> Env Vars -> .env file -> defaults
        return env_settings, VaultConfigSource(settings_cls), dotenv_settings, init_settings

# Create a single, importable instance
settings = AppSettings()
```
This implementation provides a sophisticated, secure, and flexible configuration system that is ready for enterprise deployment. It cleanly separates concerns and establishes a clear precedence for where configuration values should come from.

---

## 3. Docker Container-to-Container Communication & Secret Management

### 3.1. Technical Installation Steps

**Prerequisites:**
```bash
# Install Docker and Docker Compose
docker --version  # Should be 20.10+
docker-compose --version  # Should be 2.0+

# Install required Python packages
pip install python-dotenv hvac pydantic pydantic-settings
```

**Project Structure Setup:**
```bash
# Add to requirements.txt
echo "python-dotenv>=1.0.0" >> requirements.txt
echo "hvac>=1.2.1" >> requirements.txt
echo "pydantic>=2.0.0" >> requirements.txt
echo "pydantic-settings>=2.0.0" >> requirements.txt

# Create .env.example template
cat > .env.example << 'EOF'
# Application Settings
SECRET_KEY=your-secret-key-here
FRAUD_DETECTION_ENV=development

# Database Configuration
POSTGRES_USER=dafu
POSTGRES_PASSWORD=
POSTGRES_DB=dafu
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DATABASE_URL=

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_URL=redis://redis:6379/0

# RabbitMQ Configuration (if using)
RABBITMQ_USER=dafu
RABBITMQ_PASSWORD=
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_URL=

# Vault Configuration (Production)
VAULT_ADDR=http://vault:8200
VAULT_ROLE_ID=
VAULT_SECRET_ID=
VAULT_TOKEN=

# API Configuration
API_PORT=8000
LOG_LEVEL=INFO
EOF

# Update .gitignore
echo ".env" >> .gitignore
echo "*.env" >> .gitignore
echo "!.env.example" >> .gitignore
```

### 3.2. Container-to-Container Communication in Docker

**Understanding Docker Networking:**

When containers run in the same Docker network (`dafu-network`), they communicate using **service names as hostnames**. Docker's internal DNS resolves service names to container IP addresses.

**Key Principles:**
1. **Service Discovery:** Use Docker service names (e.g., `postgres`, `redis`, `rabbitmq`) instead of `localhost`
2. **Network Isolation:** Containers in the same network can communicate; external access requires port mapping
3. **Environment Variables:** Configuration is injected via environment variables, not files

**Example Connection Strings in Docker:**
```python
# ❌ WRONG: Using localhost (doesn't work in containers)
DATABASE_URL = "postgresql://dafu:password@localhost:5432/dafu"
REDIS_URL = "redis://localhost:6379/0"

# ✅ CORRECT: Using Docker service names
DATABASE_URL = "postgresql://dafu:password@postgres:5432/dafu"
REDIS_URL = "redis://redis:6379/0"
RABBITMQ_URL = "amqp://dafu:password@rabbitmq:5672/"
```

### 3.3. Docker Compose Configuration with Secrets

**Option 1: Environment Variables (Development)**

Update `docker-compose.yml`:
```yaml
services:
  fraud-detection-api:
    environment:
      # Read from host .env file
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379/0
      - RABBITMQ_URL=amqp://${RABBITMQ_USER}:${RABBITMQ_PASSWORD}@rabbitmq:5672/
      # Container-to-container communication
      - POSTGRES_HOST=postgres
      - REDIS_HOST=redis
      - RABBITMQ_HOST=rabbitmq
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - dafu-network

  postgres:
    environment:
      - POSTGRES_USER=${POSTGRES_USER:-dafu}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB:-dafu}
    networks:
      - dafu-network

  redis:
    networks:
      - dafu-network

  rabbitmq:
    environment:
      - RABBITMQ_DEFAULT_USER=${RABBITMQ_USER:-dafu}
      - RABBITMQ_DEFAULT_PASS=${RABBITMQ_PASSWORD}
    networks:
      - dafu-network

networks:
  dafu-network:
    driver: bridge
```

**Option 2: Docker Secrets (Production - Docker Swarm)**

```yaml
services:
  fraud-detection-api:
    secrets:
      - db_password
      - secret_key
      - redis_password
    environment:
      - DATABASE_URL=postgresql://dafu@postgres:5432/dafu
      - DB_PASSWORD_FILE=/run/secrets/db_password
      - SECRET_KEY_FILE=/run/secrets/secret_key
      - REDIS_URL=redis://redis:6379/0
      - REDIS_PASSWORD_FILE=/run/secrets/redis_password

secrets:
  db_password:
    external: true
  secret_key:
    external: true
  redis_password:
    external: true
```

**Create secrets in Docker Swarm:**
```bash
echo "my_secure_password" | docker secret create db_password -
echo "my_secret_key_here" | docker secret create secret_key -
echo "redis_password_here" | docker secret create redis_password -
```

**Read secrets in application code:**
```python
import os

def get_secret(secret_name: str, env_var: str) -> str:
    """
    Read secret from file (Docker Swarm) or environment variable.
    """
    secret_file = os.getenv(f"{env_var}_FILE")
    if secret_file and os.path.exists(secret_file):
        with open(secret_file) as f:
            return f.read().strip()
    return os.getenv(env_var, "")

# Usage
DB_PASSWORD = get_secret("db_password", "DB_PASSWORD")
SECRET_KEY = get_secret("secret_key", "SECRET_KEY")
```

### 3.4. HashiCorp Vault Integration in Docker

**Docker Compose with Vault:**

```yaml
services:
  vault:
    image: vault:latest
    container_name: dafu-vault
    restart: unless-stopped
    ports:
      - "8200:8200"
    environment:
      - VAULT_DEV_ROOT_TOKEN_ID=${VAULT_ROOT_TOKEN:-root}
      - VAULT_DEV_LISTEN_ADDRESS=0.0.0.0:8200
    cap_add:
      - IPC_LOCK
    networks:
      - dafu-network
    healthcheck:
      test: ["CMD", "vault", "status"]
      interval: 10s
      timeout: 5s
      retries: 5

  fraud-detection-api:
    environment:
      - VAULT_ADDR=http://vault:8200
      - VAULT_ROLE_ID=${VAULT_ROLE_ID}
      - VAULT_SECRET_ID=${VAULT_SECRET_ID}
      # Container-to-container: Use 'vault' hostname
      - DATABASE_URL=postgresql://dafu@postgres:5432/dafu
    depends_on:
      vault:
        condition: service_healthy
      postgres:
        condition: service_healthy
    networks:
      - dafu-network
```

**Initialize Vault and Store Secrets:**

```bash
# 1. Start Vault
docker-compose up -d vault

# 2. Initialize Vault (do once)
export VAULT_ADDR='http://localhost:8200'
export VAULT_TOKEN='root'

# 3. Enable KV secrets engine
docker exec dafu-vault vault secrets enable -path=kv kv-v2

# 4. Store secrets
docker exec dafu-vault vault kv put kv/dafu \
  SECRET_KEY="your-secret-key" \
  DB_PASSWORD="your-db-password" \
  REDIS_PASSWORD="your-redis-password"

# 5. Enable AppRole authentication
docker exec dafu-vault vault auth enable approle

# 6. Create policy
docker exec dafu-vault vault policy write dafu-policy - << EOF
path "kv/data/dafu" {
  capabilities = ["read"]
}
EOF

# 7. Create AppRole
docker exec dafu-vault vault write auth/approle/role/dafu \
  secret_id_ttl=24h \
  token_ttl=1h \
  token_max_ttl=4h \
  policies="dafu-policy"

# 8. Get RoleID and SecretID
ROLE_ID=$(docker exec dafu-vault vault read -field=role_id auth/approle/role/dafu/role-id)
SECRET_ID=$(docker exec dafu-vault vault write -field=secret_id -f auth/approle/role/dafu/secret-id)

echo "VAULT_ROLE_ID=$ROLE_ID" >> .env
echo "VAULT_SECRET_ID=$SECRET_ID" >> .env
```

### 3.5. Updated Application Configuration

**`core/configs/settings.py` with Docker-aware logic:**

```python
import os
import hvac
from typing import Optional
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    # Application
    SECRET_KEY: str
    FRAUD_DETECTION_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # Database - Use Docker service names in container
    POSTGRES_USER: str = "dafu"
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = Field(default="postgres")  # Docker service name
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "dafu"
    DATABASE_URL: Optional[str] = None
    
    # Redis - Docker service name
    REDIS_HOST: str = Field(default="redis")
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_URL: Optional[str] = None
    
    # RabbitMQ - Docker service name
    RABBITMQ_HOST: str = Field(default="rabbitmq")
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "dafu"
    RABBITMQ_PASSWORD: Optional[str] = None
    RABBITMQ_URL: Optional[str] = None
    
    # Vault
    VAULT_ADDR: Optional[str] = Field(default="http://vault:8200")
    VAULT_ROLE_ID: Optional[str] = None
    VAULT_SECRET_ID: Optional[str] = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Load from Vault if configured
        if self.VAULT_ADDR and self.VAULT_ROLE_ID and self.VAULT_SECRET_ID:
            self._load_from_vault()
        
        # Construct URLs if not provided
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        
        if not self.REDIS_URL:
            auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
            self.REDIS_URL = f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/0"
        
        if not self.RABBITMQ_URL:
            self.RABBITMQ_URL = (
                f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}"
                f"@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/"
            )
    
    def _load_from_vault(self):
        """Load secrets from HashiCorp Vault"""
        try:
            client = hvac.Client(url=self.VAULT_ADDR)
            client.auth.approle.login(
                role_id=self.VAULT_ROLE_ID,
                secret_id=self.VAULT_SECRET_ID
            )
            
            if client.is_authenticated():
                secrets = client.secrets.kv.v2.read_secret_version(path='dafu')
                vault_data = secrets['data']['data']
                
                # Override with Vault secrets
                for key, value in vault_data.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
                        
        except Exception as e:
            print(f"Warning: Could not load from Vault: {e}")

# Singleton instance
settings = AppSettings()
```

### 3.6. Health Checks and Service Dependencies

**Ensure proper startup order:**

```yaml
services:
  fraud-detection-api:
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      vault:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
```

### 3.7. Testing Container Communication

**Test connectivity between containers:**

```bash
# 1. Start all services
docker-compose up -d

# 2. Check network
docker network inspect dafu-network

# 3. Test from API container to database
docker exec dafu-fraud-api ping -c 2 postgres

# 4. Test database connection
docker exec dafu-fraud-api python -c "
from core.configs.settings import settings
import psycopg2
conn = psycopg2.connect(settings.DATABASE_URL)
print('Database connection successful!')
conn.close()
"

# 5. Test Redis connection
docker exec dafu-fraud-api python -c "
from core.configs.settings import settings
import redis
r = redis.from_url(settings.REDIS_URL)
r.ping()
print('Redis connection successful!')
"

# 6. View logs
docker-compose logs -f fraud-detection-api

# 7. Check environment variables
docker exec dafu-fraud-api env | grep -E '(POSTGRES|REDIS|VAULT)'
```

### 3.8. Troubleshooting Common Issues

**Issue 1: Cannot connect to database**
```bash
# Check if postgres is running
docker ps | grep postgres

# Check postgres logs
docker logs dafu-postgres

# Verify environment variables
docker exec dafu-fraud-api env | grep DATABASE_URL

# Test connection manually
docker exec dafu-postgres psql -U dafu -d dafu -c "SELECT 1;"
```

**Issue 2: Vault authentication fails**
```bash
# Check Vault status
docker exec dafu-vault vault status

# Verify secrets
docker exec dafu-vault vault kv get kv/dafu

# Test authentication
docker exec dafu-fraud-api python -c "
import hvac, os
client = hvac.Client(url=os.getenv('VAULT_ADDR'))
client.auth.approle.login(
    role_id=os.getenv('VAULT_ROLE_ID'),
    secret_id=os.getenv('VAULT_SECRET_ID')
)
print('Vault auth successful!')
"
```

**Issue 3: Container-to-container DNS not working**
```bash
# Check network configuration
docker network inspect dafu-network

# Verify all containers are in the same network
docker ps --format "table {{.Names}}\t{{.Networks}}"

# Test DNS resolution
docker exec dafu-fraud-api nslookup postgres
docker exec dafu-fraud-api nslookup redis
```

### 3.9. Production Deployment Checklist

- [ ] All secrets stored in Vault or Docker Secrets (not environment variables)
- [ ] `.env` file added to `.gitignore`
- [ ] `.env.example` template created and documented
- [ ] Container health checks configured
- [ ] Service dependencies properly defined with `depends_on`
- [ ] All connection strings use Docker service names (not `localhost`)
- [ ] Network isolation configured (`dafu-network`)
- [ ] Volume mounts configured for persistent data
- [ ] Proper error handling for missing secrets
- [ ] Logging configured for secret access attempts
- [ ] Regular secret rotation mechanism in place
- [ ] Backup strategy for Vault data

---

## 4. Summary

This comprehensive guide covers:
1. ✅ Technical installation steps for secret management
2. ✅ Container-to-container communication principles
3. ✅ Docker Compose configuration with multiple secret strategies
4. ✅ HashiCorp Vault integration with Docker
5. ✅ Health checks and service dependencies
6. ✅ Testing and troubleshooting procedures
7. ✅ Production deployment best practices

The implementation ensures secure, scalable secret management across development, testing, and production environments.
