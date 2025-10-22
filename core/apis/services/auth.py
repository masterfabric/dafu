"""
DAFU - Data Analytics Functional Utilities
Authentication and Authorization System
========================================
JWT-based authentication with role-based access control (RBAC)

Author: MasterFabric
License: AGPL-3.0
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Union

from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from .database import get_db, User, UserRole, UserStatus

# ============================================================================
# Configuration
# ============================================================================

# Secret key for JWT - CHANGE IN PRODUCTION!
SECRET_KEY = os.getenv("SECRET_KEY", "dafu-secret-key-change-in-production-123456")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 30

# Password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__truncate_error=False
)

# Security schemes
security = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


# ============================================================================
# Pydantic Models
# ============================================================================

class UserRegister(BaseModel):
    """User registration model"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)
    full_name: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None


class UserLogin(BaseModel):
    """User login model"""
    username: str
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token payload data"""
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None


class UserResponse(BaseModel):
    """User response model"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: str
    status: str
    created_at: datetime
    last_login: Optional[datetime]
    company: Optional[str]
    phone: Optional[str]

    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    """Password change model"""
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=72)


# ============================================================================
# Password Utilities
# ============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against hashed password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


# ============================================================================
# JWT Token Utilities
# ============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Data to encode in token
        expires_delta: Token expiration time
    
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> TokenData:
    """
    Decode and verify JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        TokenData with user information
    
    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        role: str = payload.get("role")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return TokenData(username=username, user_id=user_id, role=role)
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ============================================================================
# User Authentication
# ============================================================================

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Authenticate user with username and password
    
    Args:
        db: Database session
        username: Username or email
        password: Plain password
    
    Returns:
        User object if authenticated, None otherwise
    """
    # Try username first
    user = db.query(User).filter(User.username == username).first()
    
    # If not found, try email
    if not user:
        user = db.query(User).filter(User.email == username).first()
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    # Check if user is active
    if user.status != UserStatus.ACTIVE:
        return None
    
    return user


def get_user_by_api_key(db: Session, api_key: str) -> Optional[User]:
    """Get user by API key"""
    user = db.query(User).filter(User.api_key == api_key).first()
    
    if not user or user.status != UserStatus.ACTIVE:
        return None
    
    return user


# ============================================================================
# Dependencies for Protected Routes
# ============================================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    api_key: Optional[str] = Security(api_key_header),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token or API key
    
    Usage:
        @app.get("/protected")
        def protected_route(current_user: User = Depends(get_current_user)):
            return {"user": current_user.username}
    """
    # Try API key first
    if api_key:
        user = get_user_by_api_key(db, api_key)
        if user:
            return user
    
    # Try JWT token
    if credentials:
        token = credentials.credentials
        token_data = decode_token(token)
        
        user = db.query(User).filter(User.username == token_data.username).first()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if user.status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is not active",
            )
        
        return user
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


# ============================================================================
# Role-Based Access Control (RBAC)
# ============================================================================

class RoleChecker:
    """
    Role-based access control dependency
    
    Usage:
        @app.get("/admin")
        def admin_route(current_user: User = Depends(RoleChecker(["admin"]))):
            return {"message": "Admin access"}
    """
    
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.value not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required roles: {', '.join(self.allowed_roles)}"
            )
        return current_user


# Predefined role checkers
require_admin = RoleChecker(["admin"])
require_analyst = RoleChecker(["admin", "analyst"])
require_user = RoleChecker(["admin", "analyst", "user"])


# ============================================================================
# User Management Functions
# ============================================================================

def create_user(db: Session, user_data: UserRegister, role: UserRole = UserRole.USER) -> User:
    """
    Create a new user
    
    Args:
        db: Database session
        user_data: User registration data
        role: User role (default: USER)
    
    Returns:
        Created user object
    
    Raises:
        HTTPException: If username or email already exists
    """
    # Check if username exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        company=user_data.company,
        phone=user_data.phone,
        role=role,
        status=UserStatus.ACTIVE
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


def generate_api_key(db: Session, user: User) -> str:
    """Generate API key for user"""
    import secrets
    api_key = f"dafu_{secrets.token_urlsafe(32)}"
    
    user.api_key = api_key
    db.commit()
    db.refresh(user)
    
    return api_key

