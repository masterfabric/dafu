"""
Preprocessing module for customer analytics data.
Handles CSV input validation, sessionization, and session aggregation.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional, Dict, Union
from pathlib import Path


# Expected column names and types
REQUIRED_COLUMNS = {
    "timestamp": "int64",
    "visitorid": "int64",
    "itemid": "int64",
    "event": "object",
    "categoryid": "object",
    "price": "float64",
    "datetime": "object",
    "row_number": "int64",
}

# Expected unique event values
EXPECTED_EVENTS = {"view", "addtocart", "transaction"}

# Session timeout in minutes
SESSION_TIMEOUT_MINUTES = 15


class DataFormatError(Exception):
    """Raised when data format validation fails."""
    pass


def validate_data_format(df: pd.DataFrame) -> Tuple[bool, Optional[str]]:
    """
    Validate that the DataFrame matches the expected format.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if all required columns exist
    missing_columns = set(REQUIRED_COLUMNS.keys()) - set(df.columns)
    if missing_columns:
        error_msg = (
            f"Missing required columns: {', '.join(sorted(missing_columns))}\n"
            f"Expected columns: {', '.join(sorted(REQUIRED_COLUMNS.keys()))}\n"
            f"Received columns: {', '.join(sorted(df.columns))}"
        )
        return False, error_msg
    
    # Check column types (basic check - object types are flexible)
    type_issues = []
    for col, expected_type in REQUIRED_COLUMNS.items():
        if expected_type == "object":
            continue  # Skip object type checks
        actual_type = str(df[col].dtype)
        if expected_type not in actual_type and actual_type not in ["int64", "float64"]:
            type_issues.append(f"{col}: expected {expected_type}, got {actual_type}")
    
    if type_issues:
        error_msg = (
            f"Column type mismatches:\n" + "\n".join(type_issues) + "\n"
            f"Expected format:\n"
            f"  timestamp: int64\n"
            f"  visitorid: int64\n"
            f"  itemid: int64\n"
            f"  event: object (must contain: 'view', 'addtocart', 'transaction')\n"
            f"  categoryid: object\n"
            f"  price: float64\n"
            f"  datetime: object\n"
            f"  row_number: int64"
        )
        return False, error_msg
    
    # Check event column values
    if "event" in df.columns:
        unique_events = set(df["event"].dropna().unique())
        invalid_events = unique_events - EXPECTED_EVENTS
        if invalid_events:
            error_msg = (
                f"Invalid event values found: {', '.join(sorted(invalid_events))}\n"
                f"Expected event values: {', '.join(sorted(EXPECTED_EVENTS))}\n"
                f"Found event values: {', '.join(sorted(unique_events))}"
            )
            return False, error_msg
    
    return True, None


def preprocess_data(
    input_path: str,
    output_path: Optional[str] = None,
    session_timeout_minutes: int = SESSION_TIMEOUT_MINUTES,
    return_sessionized: bool = False
) -> Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]]:
    """
    Preprocess customer analytics data: validate, sessionize, and aggregate.
    
    Args:
        input_path: Path to input CSV file
        output_path: Path to save aggregated sessions CSV (optional)
        session_timeout_minutes: Minutes of inactivity before starting new session
        return_sessionized: If True, return both aggregated and sessionized data
        
    Returns:
        If return_sessionized=False: DataFrame with aggregated session features
        If return_sessionized=True: Tuple of (aggregated_sessions, sessionized_data)
        
    Raises:
        DataFormatError: If data format validation fails
        FileNotFoundError: If input file doesn't exist
    """
    # Read CSV file
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    df = pd.read_csv(input_path)
    
    # Validate data format
    is_valid, error_msg = validate_data_format(df)
    if not is_valid:
        raise DataFormatError(f"Data format validation failed:\n{error_msg}")
    
    # Convert datetime column to datetime type
    df["datetime"] = pd.to_datetime(df["datetime"])
    
    # Sort by visitorid and datetime to ensure proper sessionization
    df = df.sort_values(["visitorid", "datetime"]).reset_index(drop=True)
    
    # Sessionization: New session starts when visitor changes or timeout occurs
    # Visitor changed flag
    df["vis_diff"] = df["visitorid"].shift(1).ne(df["visitorid"]).fillna(True)
    
    # Time difference flag (15+ minutes or NaN datetime)
    df["time_diff"] = (
        df["datetime"].diff().dt.total_seconds().div(60).gt(session_timeout_minutes)
        | df["datetime"].isna()
    )
    
    # Identify session boundaries (where new session starts)
    groups = df[df["vis_diff"] | df["time_diff"]].copy()
    groups["row_end"] = groups["row_number"].shift(-1)
    groups.loc[groups["row_end"].isna(), "row_end"] = len(df)
    groups["sessionid"] = np.arange(len(groups))
    groups = groups.rename(columns={"row_number": "row_start"})[
        ["visitorid", "sessionid", "row_start", "row_end"]
    ]
    
    # Assign session IDs to each event by merging and filtering
    df = df.merge(groups, on="visitorid", how="left")
    df = df[
        (df["row_number"] >= df["row_start"])
        & (df["row_number"] < df["row_end"])
    ]
    
    # Clean up temporary columns
    df = df.drop(columns=["vis_diff", "time_diff", "row_start", "row_end"])
    
    # Aggregate session features
    aggregated_sessions = aggregate_sessions(df)
    
    # Calculate major spend ratio
    aggregated_sessions["major_spend_r"] = (
        aggregated_sessions["major_spend"] / aggregated_sessions["tran_sp"].replace(0, np.nan)
    )
    
    # Save to CSV if output path is provided
    if output_path:
        aggregated_sessions.to_csv(output_path, index=False)
    
    if return_sessionized:
        return aggregated_sessions, df
    return aggregated_sessions


def aggregate_sessions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate session-level features from event-level data.
    
    Args:
        df: DataFrame with sessionized events
        
    Returns:
        DataFrame with aggregated session features
    """
    def compute_session_features(group_df: pd.DataFrame) -> pd.Series:
        """Compute features for a single session."""
        features = {}
        
        # Item and category counts
        features["item_n"] = group_df["itemid"].nunique()
        features["cat_n"] = group_df["categoryid"].nunique()
        features["int_n"] = len(group_df)
        
        # Event counts
        features["view_n"] = (group_df["event"] == "view").sum()
        features["cart_n"] = (group_df["event"] == "addtocart").sum()
        features["tran_n"] = (group_df["event"] == "transaction").sum()
        
        # Spending by event type
        features["view_sp"] = group_df.loc[group_df["event"] == "view", "price"].sum()
        features["cart_sp"] = group_df.loc[group_df["event"] == "addtocart", "price"].sum()
        features["tran_sp"] = group_df.loc[group_df["event"] == "transaction", "price"].sum()
        
        # Session timing
        features["start_time"] = group_df["datetime"].min()
        features["end_time"] = group_df["datetime"].max()
        features["len"] = features["end_time"] - features["start_time"]
        
        # Major spending (largest transaction, 0 if no transactions)
        transaction_prices = group_df.loc[group_df["event"] == "transaction", "price"]
        features["major_spend"] = transaction_prices.max() if not transaction_prices.empty else 0
        
        return pd.Series(features)
    
    # Group by visitor and session, then aggregate
    aggregated = (
        df.groupby(["visitorid", "sessionid"])
        .apply(compute_session_features)
        .reset_index()
    )
    
    return aggregated

