"""
DAFU - Data Analytics Functional Utilities
Authentication Routes
=====================
Endpoints for user authentication, registration, and management

Author: MasterFabric
License: AGPL-3.0
"""

from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .database import get_db, User, UserStatus
from .auth import (
    UserRegister,
    UserLogin,
    Token,
    UserResponse,
    PasswordChange,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    create_user,
    generate_api_key,
    get_current_user,
    get_current_active_user,
    require_admin,
    get_password_hash,
    verify_password,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Create router
router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


# ============================================================================
# Authentication Endpoints
# ============================================================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user
    
    Creates a new user account with the provided information.
    
    - **username**: Unique username (3-50 characters)
    - **email**: Valid email address
    - **password**: Strong password (minimum 8 characters)
    - **full_name**: Optional full name
    - **company**: Optional company name
    - **phone**: Optional phone number
    
    Returns the created user information (without password).
    """
    user = create_user(db, user_data)
    return user


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    User login
    
    Authenticate with username/email and password.
    Returns JWT access token and refresh token.
    
    - **username**: Username or email
    - **password**: User password
    
    Returns JWT tokens for authenticated requests.
    """
    user = authenticate_user(db, credentials.username, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "role": user.role.value
        }
    )
    
    refresh_token = create_refresh_token(
        data={
            "sub": user.username,
            "user_id": user.id
        }
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information
    
    Returns the authenticated user's profile information.
    Requires valid JWT token.
    """
    return current_user


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    User logout
    
    Logout current user. Client should discard tokens.
    """
    return {
        "message": "Successfully logged out",
        "username": current_user.username
    }


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
    
    Change the current user's password.
    
    - **old_password**: Current password
    - **new_password**: New password (minimum 8 characters)
    """
    # Verify old password
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.post("/api-key")
async def create_api_key(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate API key
    
    Generate a new API key for the current user.
    This will replace any existing API key.
    """
    api_key = generate_api_key(db, current_user)
    
    return {
        "message": "API key generated successfully",
        "api_key": api_key,
        "warning": "Store this key securely. It won't be shown again."
    }


# ============================================================================
# User Management Endpoints (Admin Only)
# ============================================================================

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all users (Admin only)
    
    Retrieve a list of all registered users.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get user by ID (Admin only)
    
    Retrieve detailed information about a specific user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete user (Admin only)
    
    Delete a user account. This action cannot be undone.
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent self-deletion
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Soft delete by changing status
    user.status = UserStatus.DELETED
    user.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": "User deleted successfully",
        "user_id": user_id
    }


@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    new_status: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update user status (Admin only)
    
    Change a user's status (active, inactive, suspended).
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate status
    try:
        status_enum = UserStatus(new_status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {[s.value for s in UserStatus]}"
        )
    
    user.status = status_enum
    user.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": "User status updated successfully",
        "user_id": user_id,
        "new_status": new_status
    }

