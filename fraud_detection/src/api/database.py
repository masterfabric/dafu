"""
DAFU - Data Analytics Functional Utilities
Database Models and Configuration
===================================
SQLAlchemy models for User, Log, Report, Product management

Author: MasterFabric
License: AGPL-3.0
"""

import os
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    Text,
    JSON,
    ForeignKey,
    Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.pool import QueuePool
import enum

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://dafu:dafu_secure_password@localhost:5432/dafu"
)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# ============================================================================
# Enums
# ============================================================================

class UserRole(str, enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    USER = "user"
    ANALYST = "analyst"
    VIEWER = "viewer"


class UserStatus(str, enum.Enum):
    """User status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class LogLevel(str, enum.Enum):
    """Log level enumeration"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ReportStatus(str, enum.Enum):
    """Report status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProductStatus(str, enum.Enum):
    """Product status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


# ============================================================================
# Database Models
# ============================================================================

class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    
    # Role and permissions
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Additional info
    api_key = Column(String(255), unique=True, index=True, nullable=True)
    phone = Column(String(20), nullable=True)
    company = Column(String(100), nullable=True)
    extra_data = Column(JSON, default={}, nullable=True)
    
    # Relationships
    logs = relationship("Log", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


class Log(Base):
    """Log model for system and user activity logging"""
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Log details
    level = Column(SQLEnum(LogLevel), default=LogLevel.INFO, nullable=False, index=True)
    message = Column(Text, nullable=False)
    module = Column(String(100), nullable=True, index=True)
    function = Column(String(100), nullable=True)
    
    # Request information
    endpoint = Column(String(255), nullable=True)
    method = Column(String(10), nullable=True)
    status_code = Column(Integer, nullable=True)
    response_time_ms = Column(Float, nullable=True)
    
    # Client information
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    
    # Additional data
    extra_data = Column(JSON, default={}, nullable=True)
    stack_trace = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="logs")
    
    def __repr__(self):
        return f"<Log(id={self.id}, level='{self.level}', message='{self.message[:50]}...')>"


class Report(Base):
    """Report model for fraud detection and analytics reports"""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Report details
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    report_type = Column(String(50), nullable=False, index=True)  # fraud_detection, analytics, etc.
    
    # Status and results
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.PENDING, nullable=False, index=True)
    progress = Column(Float, default=0.0, nullable=False)  # 0-100%
    
    # Configuration
    config = Column(JSON, default={}, nullable=True)  # Report parameters
    filters = Column(JSON, default={}, nullable=True)  # Data filters
    
    # Results
    results = Column(JSON, default={}, nullable=True)  # Report results
    metrics = Column(JSON, default={}, nullable=True)  # Key metrics
    file_path = Column(String(500), nullable=True)  # Path to result file
    file_size_bytes = Column(Integer, nullable=True)
    
    # Processing information
    total_records = Column(Integer, nullable=True)
    processed_records = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    processing_time_seconds = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="reports")
    
    def __repr__(self):
        return f"<Report(id={self.id}, name='{self.name}', status='{self.status}')>"


class Product(Base):
    """Product model for e-commerce and fraud monitoring"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    
    # Product identification
    sku = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Pricing
    price = Column(Float, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    cost = Column(Float, nullable=True)
    
    # Categorization
    category = Column(String(100), nullable=True, index=True)
    subcategory = Column(String(100), nullable=True)
    brand = Column(String(100), nullable=True, index=True)
    tags = Column(JSON, default=[], nullable=True)
    
    # Inventory
    stock_quantity = Column(Integer, default=0, nullable=False)
    low_stock_threshold = Column(Integer, default=10, nullable=False)
    
    # Fraud risk indicators
    fraud_risk_score = Column(Float, default=0.0, nullable=False)  # 0-1
    high_risk = Column(Boolean, default=False, nullable=False, index=True)
    fraud_incidents = Column(Integer, default=0, nullable=False)
    chargeback_rate = Column(Float, default=0.0, nullable=False)
    
    # Status
    status = Column(SQLEnum(ProductStatus), default=ProductStatus.ACTIVE, nullable=False, index=True)
    
    # Additional information
    extra_data = Column(JSON, default={}, nullable=True)
    images = Column(JSON, default=[], nullable=True)  # List of image URLs
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Product(id={self.id}, sku='{self.sku}', name='{self.name}')>"


# ============================================================================
# Database Utilities
# ============================================================================

def get_db():
    """
    Dependency function to get database session
    
    Usage in FastAPI:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully!")


def drop_db():
    """Drop all tables - USE WITH CAUTION!"""
    Base.metadata.drop_all(bind=engine)
    print("⚠️  All tables dropped!")


if __name__ == "__main__":
    # Initialize database when run directly
    print("Initializing DAFU database...")
    init_db()

