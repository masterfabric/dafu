"""
DAFU - Data Analytics Functional Utilities
Report Management Routes
========================
Endpoints for fraud detection and analytics reports

Author: MasterFabric
License: AGPL-3.0
"""

from datetime import datetime
from typing import List, Optional
import os
import json

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import desc

from .database import get_db, User, Report, ReportStatus
from .auth import get_current_user, require_analyst

# Create router
router = APIRouter(prefix="/api/v1/reports", tags=["Reports"])


# ============================================================================
# Pydantic Models
# ============================================================================

class ReportCreate(BaseModel):
    """Report creation model"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    report_type: str = Field(..., description="fraud_detection, analytics, risk_analysis, etc.")
    config: Optional[dict] = Field(default_factory=dict, description="Report configuration")
    filters: Optional[dict] = Field(default_factory=dict, description="Data filters")


class ReportResponse(BaseModel):
    """Report response model"""
    id: int
    user_id: int
    name: str
    description: Optional[str]
    report_type: str
    status: str
    progress: float
    config: Optional[dict]
    filters: Optional[dict]
    results: Optional[dict]
    metrics: Optional[dict]
    file_path: Optional[str]
    total_records: Optional[int]
    processed_records: Optional[int]
    error_message: Optional[str]
    processing_time_seconds: Optional[float]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ReportUpdate(BaseModel):
    """Report update model"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = None


class ReportStats(BaseModel):
    """Report statistics model"""
    total_reports: int
    by_status: dict
    by_type: dict
    avg_processing_time_seconds: Optional[float]
    success_rate: float


# ============================================================================
# Helper Functions
# ============================================================================

async def process_report_background(report_id: int, db: Session):
    """
    Background task to process report
    This is a placeholder - implement actual report generation logic
    """
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            return
        
        # Update status to processing
        report.status = ReportStatus.PROCESSING
        report.started_at = datetime.utcnow()
        report.progress = 0.0
        db.commit()
        
        # TODO: Implement actual report generation logic
        # This could involve:
        # 1. Loading data based on filters
        # 2. Running fraud detection models
        # 3. Generating analytics
        # 4. Creating visualizations
        # 5. Saving results to file
        
        # Simulate processing
        import time
        start_time = time.time()
        
        # Mock results
        report.progress = 50.0
        db.commit()
        
        # Simulate more processing
        time.sleep(1)
        
        # Complete
        report.status = ReportStatus.COMPLETED
        report.progress = 100.0
        report.completed_at = datetime.utcnow()
        report.processing_time_seconds = time.time() - start_time
        report.total_records = 1000
        report.processed_records = 1000
        report.results = {
            "summary": "Report generation completed successfully",
            "fraud_detected": 50,
            "fraud_rate": 5.0
        }
        report.metrics = {
            "accuracy": 0.95,
            "precision": 0.92,
            "recall": 0.88
        }
        
        db.commit()
        
    except Exception as e:
        # Handle errors
        report.status = ReportStatus.FAILED
        report.error_message = str(e)
        report.completed_at = datetime.utcnow()
        db.commit()


# ============================================================================
# Report Endpoints
# ============================================================================

@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    report_data: ReportCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new report
    
    Create a fraud detection or analytics report.
    The report will be processed asynchronously in the background.
    
    - **name**: Report name
    - **description**: Report description
    - **report_type**: Type of report (fraud_detection, analytics, risk_analysis)
    - **config**: Report configuration parameters
    - **filters**: Data filters to apply
    
    Returns report information including ID for tracking progress.
    """
    # Create report
    db_report = Report(
        user_id=current_user.id,
        name=report_data.name,
        description=report_data.description,
        report_type=report_data.report_type,
        status=ReportStatus.PENDING,
        progress=0.0,
        config=report_data.config,
        filters=report_data.filters
    )
    
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    
    # Schedule background processing
    background_tasks.add_task(process_report_background, db_report.id, db)
    
    return db_report


@router.get("/", response_model=List[ReportResponse])
async def get_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    report_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's reports
    
    Retrieve reports created by the authenticated user.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return (1-1000)
    - **report_type**: Filter by report type
    - **status**: Filter by status (pending, processing, completed, failed)
    """
    query = db.query(Report).filter(Report.user_id == current_user.id)
    
    # Apply filters
    if report_type:
        query = query.filter(Report.report_type == report_type)
    
    if status:
        try:
            status_enum = ReportStatus(status.lower())
            query = query.filter(Report.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {[s.value for s in ReportStatus]}"
            )
    
    # Order by most recent first
    query = query.order_by(desc(Report.created_at))
    
    # Apply pagination
    reports = query.offset(skip).limit(limit).all()
    
    return reports


@router.get("/all", response_model=List[ReportResponse])
async def get_all_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    report_type: Optional[str] = None,
    status: Optional[str] = None,
    user_id: Optional[int] = None,
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db)
):
    """
    Get all reports (Analyst/Admin only)
    
    Retrieve all reports from all users.
    Requires analyst or admin role.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return (1-1000)
    - **report_type**: Filter by report type
    - **status**: Filter by status
    - **user_id**: Filter by user ID
    """
    query = db.query(Report)
    
    # Apply filters
    if report_type:
        query = query.filter(Report.report_type == report_type)
    
    if status:
        try:
            status_enum = ReportStatus(status.lower())
            query = query.filter(Report.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {[s.value for s in ReportStatus]}"
            )
    
    if user_id:
        query = query.filter(Report.user_id == user_id)
    
    # Order by most recent first
    query = query.order_by(desc(Report.created_at))
    
    # Apply pagination
    reports = query.offset(skip).limit(limit).all()
    
    return reports


@router.get("/stats", response_model=ReportStats)
async def get_report_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get report statistics
    
    Get aggregated statistics for user's reports.
    """
    # Get all user's reports
    reports = db.query(Report).filter(Report.user_id == current_user.id).all()
    
    total_reports = len(reports)
    
    # Count by status
    by_status = {}
    for status in ReportStatus:
        count = sum(1 for report in reports if report.status == status)
        by_status[status.value] = count
    
    # Count by type
    by_type = {}
    for report in reports:
        by_type[report.report_type] = by_type.get(report.report_type, 0) + 1
    
    # Calculate average processing time
    completed_reports = [r for r in reports if r.processing_time_seconds is not None]
    avg_processing_time = (
        sum(r.processing_time_seconds for r in completed_reports) / len(completed_reports)
        if completed_reports else None
    )
    
    # Calculate success rate
    completed_count = by_status.get('completed', 0)
    success_rate = (completed_count / total_reports * 100) if total_reports > 0 else 0.0
    
    return ReportStats(
        total_reports=total_reports,
        by_status=by_status,
        by_type=by_type,
        avg_processing_time_seconds=avg_processing_time,
        success_rate=success_rate
    )


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get report by ID
    
    Retrieve a specific report by its ID.
    Users can only access their own reports.
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check ownership (allow analysts/admins to view any report)
    if report.user_id != current_user.id and current_user.role.value not in ['admin', 'analyst']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return report


@router.put("/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: int,
    report_data: ReportUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update report
    
    Update report information.
    Users can only update their own reports.
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check ownership
    if report.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Update fields
    if report_data.name is not None:
        report.name = report_data.name
    
    if report_data.description is not None:
        report.description = report_data.description
    
    if report_data.status is not None:
        try:
            status_enum = ReportStatus(report_data.status.lower())
            report.status = status_enum
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {[s.value for s in ReportStatus]}"
            )
    
    db.commit()
    db.refresh(report)
    
    return report


@router.delete("/{report_id}")
async def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete report
    
    Delete a report and its associated files.
    Users can only delete their own reports.
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check ownership (allow admins to delete any report)
    if report.user_id != current_user.id and current_user.role.value != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Delete associated file if exists
    if report.file_path and os.path.exists(report.file_path):
        try:
            os.remove(report.file_path)
        except Exception:
            pass  # Ignore file deletion errors
    
    # Delete report from database
    db.delete(report)
    db.commit()
    
    return {
        "message": "Report deleted successfully",
        "report_id": report_id
    }


@router.post("/{report_id}/retry")
async def retry_report(
    report_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retry failed report
    
    Retry processing a failed report.
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check ownership
    if report.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Check if report is failed
    if report.status != ReportStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only retry failed reports"
        )
    
    # Reset report status
    report.status = ReportStatus.PENDING
    report.progress = 0.0
    report.error_message = None
    db.commit()
    
    # Schedule background processing
    background_tasks.add_task(process_report_background, report_id, db)
    
    return {
        "message": "Report retry scheduled",
        "report_id": report_id
    }

