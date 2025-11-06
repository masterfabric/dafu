"""
Feature engineering module for customer analytics.
Creates customer-level features from session-level data and generates target variables.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional, Union
from datetime import datetime
from pathlib import Path


def calculate_automatic_split_time(
    aggregated_sessions: pd.DataFrame,
    train_ratio: float = 0.7
) -> pd.Timestamp:
    """
    Automatically calculate split_time based on data distribution.
    
    Sorts sessions by end_time and finds the timestamp at the train_ratio percentile.
    This ensures train_ratio% of sessions are used for feature calculation and
    (1-train_ratio)% are used for target evaluation.
    
    Args:
        aggregated_sessions: DataFrame with aggregated session features
        train_ratio: Ratio of data for feature calculation (default: 0.7)
        
    Returns:
        Timestamp at the train_ratio percentile
        
    Raises:
        ValueError: If aggregated_sessions is empty
    """
    if len(aggregated_sessions) == 0:
        raise ValueError("Cannot calculate split_time: aggregated_sessions is empty")
    
    # Sort sessions by end_time
    sorted_sessions = aggregated_sessions.sort_values("end_time").reset_index(drop=True)
    
    # Calculate the index at train_ratio percentile
    # Use max(1, ...) to ensure at least one session for features
    # Use min(..., len-1) to ensure at least one session for target
    split_index = max(1, min(int(len(sorted_sessions) * train_ratio), len(sorted_sessions) - 1))
    
    # Get the end_time at that index
    split_time = sorted_sessions.iloc[split_index]["end_time"]
    
    return pd.Timestamp(split_time)


def engineer_features(
    aggregated_sessions: pd.DataFrame,
    sessionized_data: pd.DataFrame,
    split_time: Optional[Union[str, pd.Timestamp]] = None,
    output_path: Optional[str] = None,
    min_sessions: int = 1,
    max_recency_days: int = 31,
    train_ratio: float = 0.7
) -> Tuple[pd.DataFrame, pd.Timestamp, Path]:
    """
    Engineer customer-level features from session data.
    
    This function performs time-based feature engineering where:
    - Features are calculated from sessions before split_time (historical behavior)
    - Target variable is determined from sessions after split_time (future behavior)
    - This creates a train/test split for churn prediction models
    
    Args:
        aggregated_sessions: DataFrame with aggregated session features from preprocessing
        sessionized_data: DataFrame with event-level sessionized data (needed for category counts)
        split_time: Timestamp to split historical features from target period. If None, automatically
                    calculated based on train_ratio (format: 'YYYY-MM-DD' or pd.Timestamp)
        output_path: Path to save final classification dataset CSV (optional)
        min_sessions: Minimum number of sessions required (default: 1)
        max_recency_days: Maximum days since last session for inclusion (default: 31)
        train_ratio: Ratio of data for feature calculation when split_time is auto-calculated (default: 0.7)
        
    Returns:
        Tuple of (DataFrame with customer-level features and target variable, split_time used, output_path)
        
    Raises:
        ValueError: If split_time format is invalid
    """
    # Calculate split_time automatically if not provided
    if split_time is None:
        split_time = calculate_automatic_split_time(aggregated_sessions, train_ratio)
    # Convert split_time to datetime if string
    elif isinstance(split_time, str):
        split_time = pd.to_datetime(split_time)
    elif not isinstance(split_time, pd.Timestamp):
        raise ValueError(f"split_time must be None, a string (YYYY-MM-DD), or pd.Timestamp, got {type(split_time)}")
    
    # Filter sessions before split_time for feature calculation
    session_features = aggregated_sessions[aggregated_sessions["end_time"] < split_time].copy()
    
    # Calculate customer-level features from historical sessions
    aggregated_customers = _calculate_customer_features(
        session_features, split_time
    )
    
    # Calculate category interaction features
    cat_customers = _calculate_category_features(
        sessionized_data, split_time
    )
    
    # Merge customer features with category features
    classification_data = aggregated_customers.merge(
        cat_customers, on="visitorid", how="left"
    )
    classification_data = classification_data.fillna(0)
    
    # Create target variable based on post-split_time activity
    target_df = _create_target_variable(
        aggregated_customers, aggregated_sessions, split_time
    )
    
    # Merge target with features
    classification_data = classification_data.merge(
        target_df, on="visitorid", how="left"
    )
    
    # Filter customers based on criteria
    classification_data = classification_data[
        (classification_data["ses_n"] > min_sessions) &
        (classification_data["ses_rec"] <= max_recency_days)
    ]
    
    # Convert target to binary (0=visited, 1=churn)
    classification_data["target_class"] = classification_data["target_class"].apply(
        lambda c: 0 if c > 0 else 1
    )
    
    # Fill remaining missing values
    classification_data = classification_data.fillna(-1)
    
    # Save to CSV
    # If output_path is provided, use it; otherwise save to results directory
    if output_path is None:
        # Get the customer_analytics directory
        current_file = Path(__file__).resolve()
        customer_analytics_dir = current_file.parent
        results_dir = customer_analytics_dir / "results"
        
        # Create results directory if it doesn't exist
        results_dir.mkdir(exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = results_dir / f"classification_data_{timestamp}.csv"
    
    # Ensure output_path is a Path object
    output_path = Path(output_path)
    
    # Create parent directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to CSV
    classification_data.to_csv(output_path, index=False)
    
    return classification_data, split_time, output_path


def _calculate_customer_features(
    session_features: pd.DataFrame,
    split_time: pd.Timestamp
) -> pd.DataFrame:
    """
    Calculate customer-level aggregated features from session data.
    
    Args:
        session_features: Session features before split_time
        split_time: Timestamp used for recency calculations
        
    Returns:
        DataFrame with customer-level features
    """
    def compute_customer_features(group_df: pd.DataFrame) -> pd.Series:
        """Compute features for a single customer."""
        # Sort by start time for recency calculations
        df_sorted = group_df.sort_values("start_time")
        
        # Calculate session recency differences (days between sessions)
        ses_rec_diff = (
            df_sorted["start_time"] - df_sorted["start_time"].shift(1)
        ).dt.days
        
        features = {}
        
        # Session recency (days since last session)
        features["ses_rec"] = (
            split_time - df_sorted["end_time"].max()
        ).days
        
        # Session recency statistics
        features["ses_rec_avg"] = ses_rec_diff.mean()
        features["ses_rec_sd"] = ses_rec_diff.std()
        features["ses_rec_cv"] = (
            features["ses_rec_sd"] / features["ses_rec_avg"]
            if features["ses_rec_avg"] not in [0, np.nan] and not pd.isna(features["ses_rec_avg"])
            else np.nan
        )
        
        # User recency (days since first session)
        features["user_rec"] = (
            split_time - df_sorted["start_time"].min()
        ).days
        
        # Session counts and ratios
        features["ses_n"] = len(df_sorted)
        features["ses_n_r"] = (
            features["ses_n"] / features["user_rec"]
            if features["user_rec"] > 0 else np.nan
        )
        
        # Interaction counts and ratios
        features["int_n"] = df_sorted["int_n"].sum()
        features["int_n_r"] = (
            features["int_n"] / features["ses_n"]
            if features["ses_n"] > 0 else np.nan
        )
        
        # Transaction counts and ratios
        features["tran_n"] = df_sorted["tran_n"].sum()
        features["tran_n_r"] = (
            features["tran_n"] / features["ses_n"]
            if features["ses_n"] > 0 else np.nan
        )
        
        # Revenue metrics
        features["rev_sum"] = df_sorted["tran_sp"].sum()
        features["rev_sum_r"] = (
            features["rev_sum"] / features["ses_n"]
            if features["ses_n"] > 0 else np.nan
        )
        
        # Major spend ratio (average across sessions)
        features["major_spend_r"] = df_sorted["major_spend_r"].mean()
        
        # Category and item diversity (averages)
        features["int_cat_n_avg"] = df_sorted["cat_n"].mean()
        features["int_itm_n_avg"] = df_sorted["item_n"].mean()
        
        # Temporal patterns (month and hour statistics)
        features["ses_mo_avg"] = df_sorted["start_time"].dt.month.mean()
        features["ses_mo_sd"] = df_sorted["start_time"].dt.month.std()
        features["ses_ho_avg"] = df_sorted["start_time"].dt.hour.mean()
        features["ses_ho_sd"] = df_sorted["start_time"].dt.hour.std()
        
        # Weekend ratio
        features["ses_wknd_r"] = (df_sorted["start_time"].dt.weekday > 4).mean()
        
        # Session length metrics
        ses_len_d = df_sorted["len"].dt.days.sum()
        ses_len_m = df_sorted["len"].dt.total_seconds().sum() / 60
        
        features["ses_len_avg"] = (
            ses_len_m / features["ses_n"]
            if features["ses_n"] > 0 else np.nan
        )
        features["time_to_int"] = (
            ses_len_m / features["int_n"]
            if features["int_n"] > 0 else np.nan
        )
        features["time_to_tran"] = (
            ses_len_d / features["tran_n"]
            if features["tran_n"] > 0 else np.nan
        )
        
        return pd.Series(features)
    
    # Group by visitor and aggregate
    aggregated_customers = (
        session_features.groupby("visitorid")
        .apply(compute_customer_features)
        .reset_index()
    )
    
    return aggregated_customers


def _calculate_category_features(
    sessionized_data: pd.DataFrame,
    split_time: pd.Timestamp
) -> pd.DataFrame:
    """
    Calculate category interaction counts per customer.
    
    Args:
        sessionized_data: Event-level sessionized data
        split_time: Timestamp to filter sessions before this date
        
    Returns:
        DataFrame with category interaction counts per customer
    """
    # Filter sessions before split_time
    pre_split_sessions = sessionized_data[
        sessionized_data["datetime"] < split_time
    ].copy()
    
    # Count category interactions per session
    session_cat_counts = (
        pre_split_sessions
        .groupby(["visitorid", "sessionid", "categoryid"])
        .size()
        .unstack(fill_value=0)
    )
    
    # Aggregate to customer level (sum across all sessions)
    cat_customers = session_cat_counts.groupby("visitorid").sum().reset_index()
    
    # Rename columns to int_catX_n format
    cat_customers = cat_customers.rename(
        columns={
            col: f"int_{col}_n"
            for col in cat_customers.columns
            if col != "visitorid"
        }
    )
    
    return cat_customers


def _create_target_variable(
    aggregated_customers: pd.DataFrame,
    aggregated_sessions: pd.DataFrame,
    split_time: pd.Timestamp
) -> pd.DataFrame:
    """
    Create target variable based on post-split_time activity.
    
    Target classes:
    - 0: Churn (no activity after split_time)
    - 1: Visited (had interactions but no transactions)
    - 2: Transacted (had transactions)
    
    Args:
        aggregated_customers: Customer features (used to get visitor IDs)
        aggregated_sessions: All session data (to check post-split activity)
        split_time: Timestamp to determine target period
        
    Returns:
        DataFrame with visitorid and target_class
    """
    # Get sessions after split_time
    post_split_sessions = aggregated_sessions[
        aggregated_sessions["end_time"] >= split_time
    ].copy()
    
    # Merge with customer list to get all customers
    target_df = aggregated_customers[["visitorid"]].merge(
        post_split_sessions,
        on="visitorid",
        how="left"
    )
    
    # Initialize target class (0 = churn)
    target_df["target_class"] = 0
    
    # Set target based on activity level
    # 1 = visited (had interactions)
    target_df.loc[target_df["int_n"] > 0, "target_class"] = 1
    
    # 2 = transacted (had transactions)
    target_df.loc[target_df["tran_n"] > 0, "target_class"] = 2
    
    # Get maximum target class per customer (2 > 1 > 0)
    target_df = target_df.groupby("visitorid")["target_class"].max().reset_index()
    
    return target_df

