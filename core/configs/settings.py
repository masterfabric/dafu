"""
DAFU Configuration Settings
Centralized configuration management
"""

import os
from pathlib import Path
from typing import Optional

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
CORE_ROOT = Path(__file__).parent.parent

# Database Configuration
DATABASE_URL: str = os.getenv(
    "DATABASE_URL", 
    "postgresql://dafu:dafu_secure_password@localhost:5432/dafu"
)

# Redis Configuration
REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# API Configuration
API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
API_PORT: int = int(os.getenv("API_PORT", "8000"))
API_WORKERS: int = int(os.getenv("API_WORKERS", "1"))

# Security Configuration
SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

# Model Configuration
MODEL_STORAGE_PATH: str = os.getenv(
    "MODEL_STORAGE_PATH", 
    str(CORE_ROOT / "features" / "fraud_detection" / "models")
)

# Logging Configuration
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Feature Flags
ENABLE_CACHING: bool = os.getenv("ENABLE_CACHING", "true").lower() == "true"
ENABLE_QUEUE: bool = os.getenv("ENABLE_QUEUE", "true").lower() == "true"
ENABLE_MONITORING: bool = os.getenv("ENABLE_MONITORING", "true").lower() == "true"

# Fraud Detection Configuration
FRAUD_THRESHOLD: float = float(os.getenv("FRAUD_THRESHOLD", "0.7"))
DEFAULT_CONTAMINATION: float = float(os.getenv("DEFAULT_CONTAMINATION", "0.1"))

# API Rate Limiting
API_RATE_LIMIT: int = int(os.getenv("API_RATE_LIMIT", "1000"))

# CORS Configuration
CORS_ORIGINS: list = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://dafu.masterfabric.co"
]

# Monitoring Configuration
PROMETHEUS_PORT: int = int(os.getenv("PROMETHEUS_PORT", "9090"))
GRAFANA_PORT: int = int(os.getenv("GRAFANA_PORT", "3001"))
