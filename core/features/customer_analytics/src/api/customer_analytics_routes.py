"""
Customer Analytics API Routes
FastAPI routes for customer analytics preprocessing and feature engineering.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import pandas as pd
import tempfile
import shutil

# Add parent directories to path for imports
current_dir = Path(__file__).parent
customer_analytics_dir = current_dir.parent.parent.parent
sys.path.insert(0, str(customer_analytics_dir))

from preprocessing import preprocess_data, DataFormatError, validate_data_format
from feature_engineering import engineer_features

router = APIRouter(prefix="/api/v1/customer-analytics", tags=["Customer Analytics"])
security = HTTPBearer()




class PreprocessingResponse(BaseModel):
    """Preprocessing response model"""
    status: str = Field(..., description="Processing status")
    message: str = Field(..., description="Status message")
    input_rows: int = Field(..., description="Number of input rows")
    aggregated_sessions: int = Field(..., description="Number of aggregated sessions")
    output_path: Optional[str] = Field(None, description="Path to output file")


class FeatureEngineeringResponse(BaseModel):
    """Feature engineering response model"""
    status: str = Field(..., description="Processing status")
    message: str = Field(..., description="Status message")
    split_time_used: str = Field(..., description="Split time used for feature engineering")
    sessions_for_features: int = Field(..., description="Number of sessions used for features")
    sessions_for_target: int = Field(..., description="Number of sessions used for target")
    customers_in_dataset: int = Field(..., description="Number of customers in final dataset")
    features_calculated: int = Field(..., description="Number of features calculated")
    output_path: Optional[str] = Field(None, description="Path to output file")


@router.post("/preprocess", response_model=PreprocessingResponse, summary="Preprocess Customer Data")
async def preprocess_customer_data(
    file: UploadFile = File(..., description="CSV file with customer analytics data"),
    session_timeout: int = 15,
    save_output: bool = True,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Preprocess customer analytics data: validate, sessionize, and aggregate.
    
    **Required CSV Format:**
    - timestamp (int64)
    - visitorid (int64)
    - itemid (int64)
    - event (object: 'view', 'addtocart', 'transaction')
    - categoryid (object)
    - price (float64)
    - datetime (object)
    - row_number (int64)
    
    **Returns:**
    - Aggregated session-level features
    - Validation results
    - Output file path (if save_output=True)
    """
    # Create temporary file for uploaded data
    temp_file = None
    try:
        # Save uploaded file temporarily
        suffix = Path(file.filename).suffix if file.filename else ".csv"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_file = tmp.name
        
        # Read and validate data
        df = pd.read_csv(temp_file)
        is_valid, error_msg = validate_data_format(df)
        
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Data format validation failed: {error_msg}"
            )
        
        # Determine output path
        output_path = None
        if save_output:
            results_dir = customer_analytics_dir / "results"
            results_dir.mkdir(exist_ok=True)
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(results_dir / f"aggregated_sessions_{timestamp}.csv")
        
        # Preprocess data
        aggregated_sessions = preprocess_data(
            input_path=temp_file,
            output_path=output_path,
            session_timeout_minutes=session_timeout,
            return_sessionized=False
        )
        
        return PreprocessingResponse(
            status="success",
            message="Data preprocessing completed successfully",
            input_rows=len(df),
            aggregated_sessions=len(aggregated_sessions),
            output_path=output_path
        )
        
    except DataFormatError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file):
            os.unlink(temp_file)


@router.post("/feature-engineering", response_model=FeatureEngineeringResponse, summary="Feature Engineering")
async def feature_engineering(
    file: UploadFile = File(..., description="CSV file with customer analytics data"),
    split_time: Optional[str] = None,
    train_ratio: float = 0.7,
    min_sessions: int = 1,
    max_recency_days: int = 31,
    save_output: bool = True,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Perform feature engineering on customer analytics data.
    
    This endpoint:
    1. Preprocesses the data (sessionization)
    2. Calculates customer-level features
    3. Creates target variables for churn prediction
    4. Returns classification-ready dataset
    
    **Returns:**
    - Customer-level features
    - Target variable (churn/visit/transaction)
    - Split time information
    - Output file path (if save_output=True)
    """
    # Create temporary file for uploaded data
    temp_file = None
    try:
        # Save uploaded file temporarily
        suffix = Path(file.filename).suffix if file.filename else ".csv"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_file = tmp.name
        
        # Preprocess data (with sessionized data for feature engineering)
        aggregated_sessions, sessionized_data = preprocess_data(
            input_path=temp_file,
            output_path=None,
            session_timeout_minutes=15,
            return_sessionized=True
        )
        
        # Determine output path
        output_path = None
        if save_output:
            results_dir = customer_analytics_dir / "results"
            results_dir.mkdir(exist_ok=True)
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(results_dir / f"classification_data_{timestamp}.csv")
        
        # Perform feature engineering
        classification_data, used_split_time, saved_path = engineer_features(
            aggregated_sessions=aggregated_sessions,
            sessionized_data=sessionized_data,
            split_time=split_time,
            output_path=output_path,
            min_sessions=min_sessions,
            max_recency_days=max_recency_days,
            train_ratio=train_ratio
        )
        
        # Calculate statistics
        pre_split_count = len(aggregated_sessions[aggregated_sessions["end_time"] < used_split_time])
        post_split_count = len(aggregated_sessions[aggregated_sessions["end_time"] >= used_split_time])
        
        return FeatureEngineeringResponse(
            status="success",
            message="Feature engineering completed successfully",
            split_time_used=used_split_time.strftime("%Y-%m-%d %H:%M:%S"),
            sessions_for_features=pre_split_count,
            sessions_for_target=post_split_count,
            customers_in_dataset=len(classification_data),
            features_calculated=len(classification_data.columns) - 2,  # Exclude visitorid and target_class
            output_path=saved_path
        )
        
    except DataFormatError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file):
            os.unlink(temp_file)


@router.post("/validate", summary="Validate Data Format")
async def validate_data(
    file: UploadFile = File(..., description="CSV file to validate"),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Validate customer analytics data format without processing.
    
    **Returns:**
    - Validation status
    - Error messages (if invalid)
    - Data statistics (if valid)
    """
    temp_file = None
    try:
        # Save uploaded file temporarily
        suffix = Path(file.filename).suffix if file.filename else ".csv"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_file = tmp.name
        
        # Read and validate data
        df = pd.read_csv(temp_file)
        is_valid, error_msg = validate_data_format(df)
        
        if not is_valid:
            return {
                "status": "invalid",
                "valid": False,
                "error": error_msg,
                "rows": len(df),
                "columns": list(df.columns)
            }
        
        # Return validation success with statistics
        return {
            "status": "valid",
            "valid": True,
            "rows": len(df),
            "columns": list(df.columns),
            "column_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "event_values": df["event"].unique().tolist() if "event" in df.columns else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file):
            os.unlink(temp_file)

