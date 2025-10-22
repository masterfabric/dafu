"""
DAFU - Data Analytics Functional Utilities
Log Management Routes
=====================
Endpoints for system and user activity logging

Author: MasterFabric
License: AGPL-3.0
"""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from .database import get_db, User, Log, LogLevel
from .auth import get_current_user, require_admin, require_analyst

# Create router
router = APIRouter(prefix="/api/v1/logs", tags=["Logs"])


# ============================================================================
# Pydantic Models
# ============================================================================

class LogCreate(BaseModel):
    """Log creation model"""
    level: str = Field(..., description="Log level: debug, info, warning, error, critical")
    message: str = Field(..., min_length=1, max_length=5000)
    module: Optional[str] = Field(None, max_length=100)
    function: Optional[str] = Field(None, max_length=100)
    endpoint: Optional[str] = Field(None, max_length=255)
    method: Optional[str] = Field(None, max_length=10)
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    ip_address: Optional[str] = Field(None, max_length=50)
    user_agent: Optional[str] = Field(None, max_length=255)
    extra_data: Optional[dict] = Field(default_factory=dict)
    stack_trace: Optional[str] = None


class LogResponse(BaseModel):
    """Log response model"""
    id: int
    user_id: Optional[int]
    level: str
    message: str
    module: Optional[str]
    function: Optional[str]
    endpoint: Optional[str]
    method: Optional[str]
    status_code: Optional[int]
    response_time_ms: Optional[float]
    ip_address: Optional[str]
    user_agent: Optional[str]
    extra_data: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True


class LogStats(BaseModel):
    """Log statistics model"""
    total_logs: int
    by_level: dict
    by_module: dict
    avg_response_time_ms: Optional[float]
    error_rate: float
    time_period: str


# ============================================================================
# Log Endpoints
# ============================================================================

@router.post("/", response_model=LogResponse, status_code=status.HTTP_201_CREATED)
async def create_log(
    log_data: LogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new log entry
    
    Record system or application events.
    
    - **level**: Log level (debug, info, warning, error, critical)
    - **message**: Log message
    - **module**: Module/component name
    - **function**: Function name
    - **extra_data**: Additional metadata (JSON)
    """
    # Validate log level
    try:
        log_level = LogLevel(log_data.level.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid log level. Must be one of: {[l.value for l in LogLevel]}"
        )
    
    # Create log entry
    db_log = Log(
        user_id=current_user.id,
        level=log_level,
        message=log_data.message,
        module=log_data.module,
        function=log_data.function,
        endpoint=log_data.endpoint,
        method=log_data.method,
        status_code=log_data.status_code,
        response_time_ms=log_data.response_time_ms,
        ip_address=log_data.ip_address,
        user_agent=log_data.user_agent,
        extra_data=log_data.extra_data,
        stack_trace=log_data.stack_trace
    )
    
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    
    return db_log


@router.get("/", response_model=List[LogResponse])
async def get_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    level: Optional[str] = None,
    module: Optional[str] = None,
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db)
):
    """
    Get logs with filtering
    
    Retrieve system logs with various filters.
    Requires analyst or admin role.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return (1-1000)
    - **level**: Filter by log level
    - **module**: Filter by module name
    - **user_id**: Filter by user ID
    - **start_date**: Filter logs after this date
    - **end_date**: Filter logs before this date
    """
    query = db.query(Log)
    
    # Apply filters
    if level:
        try:
            log_level = LogLevel(level.lower())
            query = query.filter(Log.level == log_level)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid log level. Must be one of: {[l.value for l in LogLevel]}"
            )
    
    if module:
        query = query.filter(Log.module == module)
    
    if user_id:
        query = query.filter(Log.user_id == user_id)
    
    if start_date:
        query = query.filter(Log.created_at >= start_date)
    
    if end_date:
        query = query.filter(Log.created_at <= end_date)
    
    # Order by most recent first
    query = query.order_by(desc(Log.created_at))
    
    # Apply pagination
    logs = query.offset(skip).limit(limit).all()
    
    return logs


@router.get("/my-logs", response_model=List[LogResponse])
async def get_my_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    level: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's logs
    
    Retrieve logs created by the authenticated user.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return (1-1000)
    - **level**: Filter by log level
    """
    query = db.query(Log).filter(Log.user_id == current_user.id)
    
    if level:
        try:
            log_level = LogLevel(level.lower())
            query = query.filter(Log.level == log_level)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid log level. Must be one of: {[l.value for l in LogLevel]}"
            )
    
    query = query.order_by(desc(Log.created_at))
    logs = query.offset(skip).limit(limit).all()
    
    return logs


@router.get("/stats", response_model=LogStats)
async def get_log_stats(
    hours: int = Query(24, ge=1, le=720),
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db)
):
    """
    Get log statistics
    
    Get aggregated statistics for logs within a time period.
    Requires analyst or admin role.
    
    - **hours**: Time period in hours (1-720, default: 24)
    """
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    # Get logs within time period
    logs = db.query(Log).filter(Log.created_at >= start_time).all()
    
    total_logs = len(logs)
    
    # Count by level
    by_level = {}
    for level in LogLevel:
        count = sum(1 for log in logs if log.level == level)
        by_level[level.value] = count
    
    # Count by module
    by_module = {}
    for log in logs:
        if log.module:
            by_module[log.module] = by_module.get(log.module, 0) + 1
    
    # Calculate average response time
    response_times = [log.response_time_ms for log in logs if log.response_time_ms is not None]
    avg_response_time = sum(response_times) / len(response_times) if response_times else None
    
    # Calculate error rate
    error_count = by_level.get('error', 0) + by_level.get('critical', 0)
    error_rate = (error_count / total_logs * 100) if total_logs > 0 else 0.0
    
    return LogStats(
        total_logs=total_logs,
        by_level=by_level,
        by_module=by_module,
        avg_response_time_ms=avg_response_time,
        error_rate=error_rate,
        time_period=f"Last {hours} hours"
    )


@router.get("/{log_id}", response_model=LogResponse)
async def get_log(
    log_id: int,
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db)
):
    """
    Get log by ID
    
    Retrieve a specific log entry by its ID.
    Requires analyst or admin role.
    """
    log = db.query(Log).filter(Log.id == log_id).first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log not found"
        )
    
    return log


@router.delete("/cleanup")
async def cleanup_old_logs(
    days: int = Query(90, ge=1, le=365),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Cleanup old logs (Admin only)
    
    Delete logs older than specified number of days.
    
    - **days**: Delete logs older than this many days (1-365)
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Count logs to be deleted
    count = db.query(Log).filter(Log.created_at < cutoff_date).count()
    
    # Delete old logs
    db.query(Log).filter(Log.created_at < cutoff_date).delete()
    db.commit()
    
    return {
        "message": f"Successfully deleted logs older than {days} days",
        "deleted_count": count,
        "cutoff_date": cutoff_date.isoformat()
    }

