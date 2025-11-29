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
