"""
Isolation Forest-based Fraud Detection System

This module implements a comprehensive fraud detection system using Isolation Forest
algorithm with support for both supervised and unsupervised learning modes.

Features:
- Automatic data analysis and column detection
- Data preprocessing and feature engineering
- Multiple contamination levels for ensemble methods
- Comprehensive evaluation and visualization
- Production-ready with proper error handling

Author: Enterprise Fraud Detection Platform
Version: 1.0.0
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve
)
from sklearn.model_selection import train_test_split
import warnings
import logging
from typing import Tuple, Dict, List, Optional, Union
import os
from datetime import datetime
import json
import joblib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')


class IsolationForestFraudDetector:
    """
    Comprehensive Isolation Forest-based fraud detection system.
    
    This class provides a complete fraud detection pipeline including data analysis,
    preprocessing, model training, evaluation, and visualization capabilities.
    """
    
    def __init__(self, random_state: int = 42):
        """
        Initialize the fraud detector.
        
        Args:
            random_state: Random state for reproducibility
        """
        self.random_state = random_state
        self.data = None
        self.processed_data = None
        self.label_column = None
        self.is_supervised = False
        self.use_labels_for_training = True
        self.primary_keys = []
        self.categorical_columns = []
        self.numerical_columns = []
        self.high_cardinality_columns = []
        self.low_variance_columns = []
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.models = {}
        self.predictions = {}
        self.anomaly_scores = {}
        self.results = {}
        self.use_risk_score_threshold = False
        self.risk_score_threshold = None
        
        # Mode selection
        self.prediction_mode = None  # 'batch' or 'stream'
        self.model_save_path = None
        self.model_loaded = False
        
        # Fine-tuning parameters
        self.contamination_levels = [0.01, 0.05, 0.1]
        self.n_estimators = 100
        self.max_samples = 'auto'
        self.max_features = 1.0
        self.bootstrap = False
        
    def load_and_analyze_data(self, file_path: str) -> pd.DataFrame:
        """
        Load and analyze the dataset for fraud detection.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Loaded DataFrame
        """
        try:
            logger.info(f"Loading data from: {file_path}")
            self.data = pd.read_csv(file_path)
            logger.info(f"Data loaded successfully. Shape: {self.data.shape}")
            
            # Analyze columns
            self._analyze_columns()
            self._detect_primary_keys()
            self._detect_high_cardinality_columns()
            self._detect_low_variance_columns()
            
            # Display analysis summary
            self._display_column_analysis()
            
            return self.data
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def setup_prediction_mode(self) -> None:
        """Setup prediction mode (batch or stream)."""
        print("\n" + "="*60)
        print("🎯 PREDICTION MODE SETUP")
        print("="*60)
        print("Choose your prediction mode:")
        print("1. Batch Prediction - Train model on batch data and predict on the same data")
        print("2. Stream Prediction - Load pre-trained model and predict on new stream data")
        
        while True:
            choice = input("Enter choice (1 or 2): ").strip()
            if choice == '1':
                self.prediction_mode = 'batch'
                print("✅ Batch prediction mode selected")
                print("   - Model will be trained on the provided data")
                print("   - Predictions will be made on the same data")
                break
            elif choice == '2':
                self.prediction_mode = 'stream'
                print("✅ Stream prediction mode selected")
                print("   - Pre-trained model will be loaded")
                print("   - Predictions will be made on new stream data")
                break
            else:
                print("Please enter '1' or '2'.")
    
    def _analyze_columns(self) -> None:
        """Analyze column types and characteristics."""
        logger.info("Analyzing column types and characteristics...")
        
        for col in self.data.columns:
            if self.data[col].dtype == 'object':
                self.categorical_columns.append(col)
            else:
                self.numerical_columns.append(col)
    
    def _detect_primary_keys(self) -> None:
        """Detect potential primary key columns."""
        logger.info("Detecting primary key columns...")
        
        for col in self.data.columns:
            if (self.data[col].nunique() == len(self.data) and 
                self.data[col].dtype in ['int64', 'object']):
                self.primary_keys.append(col)
                logger.info(f"Detected primary key: {col}")
    
    def _detect_high_cardinality_columns(self) -> None:
        """Detect high cardinality categorical columns."""
        logger.info("Detecting high cardinality columns...")
        
        for col in self.categorical_columns:
            unique_ratio = self.data[col].nunique() / len(self.data)
            if unique_ratio > 0.5:  # More than 50% unique values
                self.high_cardinality_columns.append(col)
                logger.info(f"High cardinality column detected: {col} ({unique_ratio:.2%} unique)")
    
    def _detect_low_variance_columns(self) -> None:
        """Detect low variance numerical columns."""
        logger.info("Detecting low variance columns...")
        
        for col in self.numerical_columns:
            # Skip label column from low variance check
            if col == self.label_column:
                continue
                
            if self.data[col].var() < 0.01:  # Very low variance
                self.low_variance_columns.append(col)
                logger.info(f"Low variance column detected: {col} (variance: {self.data[col].var():.6f})")
    
    def _display_column_analysis(self) -> None:
        """Display comprehensive column analysis summary."""
        print("\n" + "="*80)
        print("📊 DATA ANALYSIS SUMMARY")
        print("="*80)
        
        print(f"📈 Dataset Shape: {self.data.shape[0]:,} rows × {self.data.shape[1]} columns")
        print(f"🔑 Primary Keys: {len(self.primary_keys)} - {self.primary_keys}")
        print(f"📊 Categorical Columns: {len(self.categorical_columns)} - {self.categorical_columns}")
        print(f"🔢 Numerical Columns: {len(self.numerical_columns)} - {self.numerical_columns}")
        print(f"⚠️  High Cardinality: {len(self.high_cardinality_columns)} - {self.high_cardinality_columns}")
        print(f"📉 Low Variance: {len(self.low_variance_columns)} - {self.low_variance_columns}")
        
        # Data suitability check
        print("\n" + "="*50)
        print("🔍 DATA SUITABILITY CHECK")
        print("="*50)
        
        if len(self.numerical_columns) < 2:
            print("⚠️  WARNING: Very few numerical columns. Isolation Forest works best with numerical features.")
        elif len(self.data) < 100:
            print("⚠️  WARNING: Small dataset. Results may not be reliable.")
        else:
            print("✅ Data appears suitable for Isolation Forest analysis.")
        
        # Missing values analysis
        missing_data = self.data.isnull().sum()
        missing_percent = (missing_data / len(self.data)) * 100
        missing_df = pd.DataFrame({
            'Missing Count': missing_data,
            'Missing %': missing_percent
        }).sort_values('Missing %', ascending=False)
        
        if missing_df['Missing %'].max() > 0:
            print(f"\n📋 Missing Values Analysis:")
            print(missing_df[missing_df['Missing %'] > 0].to_string())
        else:
            print("\n✅ No missing values found in the dataset.")
    
    def check_data_suitability(self) -> bool:
        """
        Check if data is suitable for Isolation Forest.
        
        Returns:
            True if suitable, False otherwise
        """
        print("\n" + "="*60)
        print("🔍 ISOLATION FOREST SUITABILITY CHECK")
        print("="*60)
        
        issues = []
        
        if len(self.numerical_columns) < 2:
            issues.append("Insufficient numerical features (need at least 2)")
        
        if len(self.data) < 100:
            issues.append("Dataset too small (need at least 100 samples)")
        
        if len(self.high_cardinality_columns) > len(self.categorical_columns) * 0.5:
            issues.append("Too many high cardinality categorical columns")
        
        if issues:
            print("❌ Data may not be suitable for Isolation Forest:")
            for issue in issues:
                print(f"   • {issue}")
            print("\n💡 Suggestions:")
            print("   • Use more numerical features")
            print("   • Consider other algorithms like One-Class SVM")
            print("   • Preprocess categorical variables differently")
            return False
        else:
            print("✅ Data appears suitable for Isolation Forest analysis!")
            return True
    
    def setup_learning_mode(self) -> None:
        """Setup supervised or unsupervised learning mode."""
        print("\n" + "="*60)
        print("🎯 LEARNING MODE SETUP")
        print("="*60)
        
        # Always ask user for label column selection
        print("📋 Available columns for label selection:")
        for i, col in enumerate(self.data.columns, 1):
            print(f"   {i}. {col}")
        
        while True:
            choice = input(f"\nEnter column number for label (1-{len(self.data.columns)}) or 'n' for no label: ").strip()
            if choice.lower() in ['n', 'no']:
                self.is_supervised = False
                print("🔍 Unsupervised mode selected - no ground truth labels available.")
                break
            else:
                try:
                    col_idx = int(choice) - 1
                    if 0 <= col_idx < len(self.data.columns):
                        self.label_column = self.data.columns[col_idx]
                        self.is_supervised = True
                        self._setup_supervised_mode()
                        break
                    else:
                        print(f"Please enter a number between 1 and {len(self.data.columns)} or 'n'")
                except ValueError:
                    print("Please enter a valid number or 'n'")
        
        # Ask for learning approach if supervised
        if self.is_supervised:
            self._setup_learning_approach()
        
        # Setup anomaly detection method
        self._setup_anomaly_detection_method()
        
        # Setup fine-tuning parameters
        self._setup_fine_tuning_parameters()
    
    def _setup_learning_approach(self) -> None:
        """Setup learning approach for supervised data."""
        print("\n" + "="*60)
        print("🎯 LEARNING APPROACH SETUP")
        print("="*60)
        print("You have supervised data with labels. Choose your approach:")
        print("1. Supervised Learning - Use labels for training and evaluation")
        print("2. Unsupervised Learning - Remove labels, train without them, then compare with actual labels")
        
        while True:
            approach = input("Enter choice (1 or 2): ").strip()
            if approach == '1':
                self.use_labels_for_training = True
                print("✅ Supervised learning selected - labels will be used for training")
                break
            elif approach == '2':
                self.use_labels_for_training = False
                print("✅ Unsupervised learning selected - labels will be removed during training")
                print("   Labels will be used only for final evaluation comparison")
                break
            else:
                print("Please enter '1' or '2'.")
    
    def _setup_supervised_mode(self) -> None:
        """Setup supervised learning mode with label analysis."""
        # Analyze label distribution
        label_counts = self.data[self.label_column].value_counts()
        label_percentages = (label_counts / len(self.data)) * 100
        
        print(f"\n📊 Label Distribution for '{self.label_column}':")
        for label, count in label_counts.items():
            percentage = label_percentages[label]
            print(f"   {label}: {count:,} ({percentage:.2f}%)")
        
        # Check if binary classification
        unique_labels = self.data[self.label_column].nunique()
        if unique_labels == 2:
            print("✅ Binary classification detected.")
        else:
            print(f"⚠️  Multi-class classification detected ({unique_labels} classes).")
            print("   Isolation Forest is typically used for binary anomaly detection.")
    
    def _setup_fine_tuning_parameters(self) -> None:
        """Setup fine-tuning parameters for Isolation Forest."""
        print("\n" + "="*60)
        print("⚙️  FINE-TUNING PARAMETERS SETUP")
        print("="*60)
        print("Configure Isolation Forest parameters for optimal performance:")
        
        # Contamination levels setup
        self._setup_contamination_levels()
        
        # n_estimators setup
        self._setup_n_estimators()
        
        # max_samples setup
        self._setup_max_samples()
        
        # max_features setup
        self._setup_max_features()
        
        # bootstrap setup
        self._setup_bootstrap()
        
        # Display final configuration
        self._display_parameter_summary()
    
    def _setup_contamination_levels(self) -> None:
        """Setup contamination levels for Isolation Forest."""
        print("\n" + "="*50)
        print("🎯 CONTAMINATION LEVELS SETUP")
        print("="*50)
        print("Contamination level: Expected proportion of outliers in the dataset")
        print("Range: 0.0 to 1.0 (0.0 = no outliers expected, 1.0 = all data are outliers)")
        print("\nExamples:")
        print("  • Single value: 0.1")
        print("  • Multiple values: 0.01,0.05,0.1,0.2")
        print("  • Range: 0.01-0.2 (will generate: 0.01, 0.05, 0.1, 0.15, 0.2)")
        print("  • Default: Use default values [0.01, 0.05, 0.1]")
        
        while True:
            choice = input("\nEnter contamination levels (or 'default' for default): ").strip()
            
            if choice.lower() in ['default', 'd']:
                self.contamination_levels = [0.01, 0.05, 0.1]
                print("✅ Using default contamination levels: [0.01, 0.05, 0.1]")
                break
            elif choice.lower() in ['range', 'r']:
                self._setup_contamination_range()
                break
            else:
                try:
                    # Parse comma-separated values
                    values = [float(x.strip()) for x in choice.split(',')]
                    if all(0.0 <= v <= 1.0 for v in values):
                        self.contamination_levels = sorted(values)
                        print(f"✅ Contamination levels set to: {self.contamination_levels}")
                        break
                    else:
                        print("❌ All values must be between 0.0 and 1.0")
                except ValueError:
                    print("❌ Invalid format. Please use comma-separated numbers (e.g., 0.01,0.05,0.1)")
    
    def _setup_contamination_range(self) -> None:
        """Setup contamination range with step size."""
        print("\n🎯 CONTAMINATION RANGE SETUP")
        print("="*40)
        
        while True:
            try:
                min_val = float(input("Enter minimum contamination (0.0-0.5): ").strip())
                if not 0.0 <= min_val <= 0.5:
                    print("❌ Minimum value must be between 0.0 and 0.5")
                    continue
                
                max_val = float(input("Enter maximum contamination (0.0-1.0): ").strip())
                if not min_val < max_val <= 1.0:
                    print("❌ Maximum value must be greater than minimum and ≤ 1.0")
                    continue
                
                step = float(input("Enter step size (e.g., 0.01): ").strip())
                if step <= 0:
                    print("❌ Step size must be positive")
                    continue
                
                # Generate range
                values = []
                current = min_val
                while current <= max_val:
                    values.append(round(current, 3))
                    current += step
                
                if len(values) > 20:
                    print(f"⚠️  Warning: This will create {len(values)} models. Continue? (y/n): ", end="")
                    if input().lower() not in ['y', 'yes']:
                        continue
                
                self.contamination_levels = values
                print(f"✅ Generated contamination levels: {self.contamination_levels}")
                break
                
            except ValueError:
                print("❌ Please enter valid numbers")
    
    def _setup_n_estimators(self) -> None:
        """Setup n_estimators parameter."""
        print("\n" + "="*50)
        print("🌲 N_ESTIMATORS SETUP")
        print("="*50)
        print("Number of base estimators (trees) in the ensemble")
        print("Higher values = better performance but slower training")
        print("\nExamples:")
        print("  • Small dataset (<1000 samples): 50-100")
        print("  • Medium dataset (1000-10000 samples): 100-200")
        print("  • Large dataset (>10000 samples): 200-500")
        print("  • Default: 100")
        
        while True:
            choice = input("\nEnter number of estimators (or 'default' for 100): ").strip()
            
            if choice.lower() in ['default', 'd']:
                self.n_estimators = 100
                print("✅ Using default n_estimators: 100")
                break
            else:
                try:
                    value = int(choice)
                    if 10 <= value <= 1000:
                        self.n_estimators = value
                        print(f"✅ n_estimators set to: {self.n_estimators}")
                        break
                    else:
                        print("❌ Value must be between 10 and 1000")
                except ValueError:
                    print("❌ Please enter a valid integer")
    
    def _setup_max_samples(self) -> None:
        """Setup max_samples parameter."""
        print("\n" + "="*50)
        print("📊 MAX_SAMPLES SETUP")
        print("="*50)
        print("Number of samples to draw from X to train each base estimator")
        print("\nOptions:")
        print("  1. 'auto' - max_samples = min(256, n_samples)")
        print("  2. 'int' - Use specific number (e.g., 1000)")
        print("  3. 'float' - Use fraction of samples (e.g., 0.8)")
        print("  4. 'default' - Use 'auto'")
        
        while True:
            choice = input("\nEnter max_samples (or 'default' for 'auto'): ").strip()
            
            if choice.lower() in ['default', 'd']:
                self.max_samples = 'auto'
                print("✅ Using default max_samples: 'auto'")
                break
            elif choice.lower() == 'auto':
                self.max_samples = 'auto'
                print("✅ max_samples set to: 'auto'")
                break
            else:
                try:
                    # Try as float first
                    value = float(choice)
                    if 0.0 < value <= 1.0:
                        self.max_samples = value
                        print(f"✅ max_samples set to: {self.max_samples} (fraction)")
                        break
                    elif value > 1.0:
                        self.max_samples = int(value)
                        print(f"✅ max_samples set to: {self.max_samples} (absolute)")
                        break
                    else:
                        print("❌ Value must be positive")
                except ValueError:
                    print("❌ Please enter 'auto', a number, or 'default'")
    
    def _setup_max_features(self) -> None:
        """Setup max_features parameter."""
        print("\n" + "="*50)
        print("🔢 MAX_FEATURES SETUP")
        print("="*50)
        print("Number of features to draw from X to train each base estimator")
        print("\nOptions:")
        print("  1. 'auto' - max_features = sqrt(n_features)")
        print("  2. 'sqrt' - max_features = sqrt(n_features)")
        print("  3. 'log2' - max_features = log2(n_features)")
        print("  4. 'int' - Use specific number (e.g., 5)")
        print("  5. 'float' - Use fraction of features (e.g., 0.8)")
        print("  6. 'default' - Use 1.0 (all features)")
        
        while True:
            choice = input("\nEnter max_features (or 'default' for 1.0): ").strip()
            
            if choice.lower() in ['default', 'd']:
                self.max_features = 1.0
                print("✅ Using default max_features: 1.0")
                break
            elif choice.lower() in ['auto', 'sqrt']:
                self.max_features = 'sqrt'
                print("✅ max_features set to: 'sqrt'")
                break
            elif choice.lower() == 'log2':
                self.max_features = 'log2'
                print("✅ max_features set to: 'log2'")
                break
            else:
                try:
                    # Try as float first
                    value = float(choice)
                    if 0.0 < value <= 1.0:
                        self.max_features = value
                        print(f"✅ max_features set to: {self.max_features} (fraction)")
                        break
                    elif value > 1.0:
                        self.max_features = int(value)
                        print(f"✅ max_features set to: {self.max_features} (absolute)")
                        break
                    else:
                        print("❌ Value must be positive")
                except ValueError:
                    print("❌ Please enter 'auto', 'sqrt', 'log2', a number, or 'default'")
    
    def _setup_bootstrap(self) -> None:
        """Setup bootstrap parameter."""
        print("\n" + "="*50)
        print("🔄 BOOTSTRAP SETUP")
        print("="*50)
        print("Whether to use bootstrap sampling for base estimators")
        print("\nOptions:")
        print("  1. False - Use all samples (recommended for Isolation Forest)")
        print("  2. True - Use bootstrap sampling")
        print("  3. Default - False")
        
        while True:
            choice = input("\nUse bootstrap sampling? (y/n or 'default' for n): ").strip().lower()
            
            if choice in ['default', 'd', 'n', 'no', 'false']:
                self.bootstrap = False
                print("✅ Bootstrap set to: False")
                break
            elif choice in ['y', 'yes', 'true']:
                self.bootstrap = True
                print("✅ Bootstrap set to: True")
                break
            else:
                print("❌ Please enter 'y' for yes, 'n' for no, or 'default'")
    
    def _display_parameter_summary(self) -> None:
        """Display summary of all fine-tuning parameters."""
        print("\n" + "="*60)
        print("📋 FINE-TUNING PARAMETERS SUMMARY")
        print("="*60)
        print(f"🎯 Contamination Levels: {self.contamination_levels}")
        print(f"🌲 N Estimators: {self.n_estimators}")
        print(f"📊 Max Samples: {self.max_samples}")
        print(f"🔢 Max Features: {self.max_features}")
        print(f"🔄 Bootstrap: {self.bootstrap}")
        print("="*60)
    
    def _setup_anomaly_detection_method(self) -> None:
        """Setup anomaly detection method (classic or risk score based)."""
        print("\n" + "="*60)
        print("🔍 ANOMALY DETECTION METHOD SETUP")
        print("="*60)
        print("Choose your anomaly detection approach:")
        print("1. Classic Method - Use Isolation Forest's built-in contamination parameter")
        print("   • Train multiple models with different contamination levels")
        print("   • Compare performance across different thresholds")
        print("   • Good for exploring optimal contamination levels")
        print()
        print("2. Risk Score Method - Use custom risk score threshold")
        print("   • Train single model with fixed contamination (0.1)")
        print("   • Apply custom threshold to risk scores (0.0-1.0)")
        print("   • More control over false positive/negative rates")
        print("   • Better for production environments")
        
        while True:
            method = input("\nEnter choice (1 or 2): ").strip()
            if method == '1':
                self.use_risk_score_threshold = False
                print("✅ Classic method selected - using Isolation Forest predictions")
                print("   Will train multiple models with different contamination levels for comparison")
                break
            elif method == '2':
                self.use_risk_score_threshold = True
                print("✅ Risk Score method selected - using custom threshold")
                print("   Will train single model and apply custom risk score threshold")
                self._setup_risk_score_threshold()
                break
            else:
                print("Please enter '1' or '2'.")
    
    def _setup_risk_score_threshold(self) -> None:
        """Setup risk score threshold for anomaly detection."""
        print("\n🎯 RISK SCORE THRESHOLD SETUP")
        print("="*50)
        print("Risk score ranges from 0.0 to 1.0:")
        print("  - 0.0 = Lowest risk (most normal)")
        print("  - 1.0 = Highest risk (most anomalous)")
        print("  - Values above threshold will be classified as anomalies")
        print("\nCommon threshold values:")
        print("  - 0.5 = Moderate sensitivity (default)")
        print("  - 0.3 = High sensitivity (more anomalies detected)")
        print("  - 0.7 = Low sensitivity (fewer false positives)")
        print("  - 0.9 = Very strict (only extreme anomalies)")
        
        while True:
            try:
                threshold_input = input("\nEnter risk score threshold (0.0-1.0) or 'default' for 0.5: ").strip()
                
                if threshold_input.lower() in ['default', 'd']:
                    threshold = 0.5
                else:
                    threshold = float(threshold_input)
                
                if 0.0 <= threshold <= 1.0:
                    self.risk_score_threshold = threshold
                    print(f"✅ Risk score threshold set to: {threshold}")
                    print(f"   Records with risk_score >= {threshold} will be classified as anomalies")
                    
                    # Provide guidance on threshold choice
                    if threshold <= 0.3:
                        print("   💡 High sensitivity: Will detect more anomalies but may have more false positives")
                    elif threshold <= 0.5:
                        print("   💡 Balanced sensitivity: Good balance between detection and false positives")
                    elif threshold <= 0.7:
                        print("   💡 Conservative: Fewer false positives but may miss some anomalies")
                    else:
                        print("   💡 Very conservative: Very strict, only extreme anomalies will be detected")
                    
                    break
                else:
                    print("❌ Please enter a value between 0.0 and 1.0")
            except ValueError:
                print("❌ Please enter a valid number or 'default'")
    
    def preprocess_data(self) -> pd.DataFrame:
        """
        Preprocess the data for Isolation Forest.
        
        Returns:
            Preprocessed DataFrame
        """
        logger.info("Starting data preprocessing...")
        self.processed_data = self.data.copy()
        
        # Remove primary key columns
        if self.primary_keys:
            logger.info(f"Removing primary key columns: {self.primary_keys}")
            self.processed_data = self.processed_data.drop(columns=self.primary_keys)
        
        # Remove high cardinality columns (but not primary keys already removed)
        if self.high_cardinality_columns:
            # Filter out primary keys from high cardinality columns to remove
            columns_to_remove = [col for col in self.high_cardinality_columns if col not in self.primary_keys]
            if columns_to_remove:
                logger.info(f"Removing high cardinality columns: {columns_to_remove}")
                self.processed_data = self.processed_data.drop(columns=columns_to_remove)
        
        # Remove low variance columns (but keep label column)
        if self.low_variance_columns:
            # Filter out label column from low variance columns to remove
            columns_to_remove = [col for col in self.low_variance_columns if col != self.label_column]
            if columns_to_remove:
                logger.info(f"Removing low variance columns: {columns_to_remove}")
                self.processed_data = self.processed_data.drop(columns=columns_to_remove)
        
        # Handle missing values
        self._handle_missing_values()
        
        # Encode categorical variables
        self._encode_categorical_variables()
        
        # Standardize numerical features
        self._standardize_numerical_features()
        
        logger.info(f"Preprocessing completed. Final shape: {self.processed_data.shape}")
        return self.processed_data
    
    def _handle_missing_values(self) -> None:
        """Handle missing values in the dataset."""
        logger.info("Handling missing values...")
        
        for col in self.processed_data.columns:
            if self.processed_data[col].isnull().sum() > 0:
                if col in self.categorical_columns:
                    # Fill with mode for categorical
                    mode_value = self.processed_data[col].mode()[0]
                    self.processed_data[col].fillna(mode_value, inplace=True)
                    logger.info(f"Filled missing values in '{col}' with mode: {mode_value}")
                else:
                    # Fill with median for numerical
                    median_value = self.processed_data[col].median()
                    self.processed_data[col].fillna(median_value, inplace=True)
                    logger.info(f"Filled missing values in '{col}' with median: {median_value:.4f}")
    
    def _encode_categorical_variables(self) -> None:
        """Encode categorical variables using LabelEncoder."""
        logger.info("Encoding categorical variables...")
        
        categorical_cols = [col for col in self.processed_data.columns 
                          if col in self.categorical_columns and col != self.label_column]
        
        for col in categorical_cols:
            le = LabelEncoder()
            self.processed_data[col] = le.fit_transform(self.processed_data[col].astype(str))
            self.label_encoders[col] = le
            logger.info(f"Encoded categorical column: {col}")
    
    def _standardize_numerical_features(self) -> None:
        """Standardize numerical features using StandardScaler."""
        logger.info("Standardizing numerical features...")
        
        numerical_cols = [col for col in self.processed_data.columns 
                         if col in self.numerical_columns and col != self.label_column]
        
        if numerical_cols:
            self.processed_data[numerical_cols] = self.scaler.fit_transform(
                self.processed_data[numerical_cols]
            )
            logger.info(f"Standardized {len(numerical_cols)} numerical columns")
    
    def train_models(self, contamination_levels: List[float] = None) -> Dict:
        """
        Train Isolation Forest models with different contamination levels.
        
        Args:
            contamination_levels: List of contamination levels to test (overrides user settings)
            
        Returns:
            Dictionary of trained models
        """
        # Use user-defined contamination levels unless overridden
        if contamination_levels is None:
            contamination_levels = self.contamination_levels
        
        # Determine contamination levels based on detection method
        if self.use_risk_score_threshold:
            # Risk score based: use single contamination level (0.1 is optimal for risk scoring)
            contamination_levels = [0.1]
            logger.info("Risk score based detection - using single contamination level: 0.1")
        else:
            # Classic method: use user-defined contamination levels
            logger.info(f"Classic detection - using contamination levels: {contamination_levels}")
        
        logger.info(f"Training Isolation Forest models with contamination levels: {contamination_levels}")
        logger.info(f"Model parameters - n_estimators: {self.n_estimators}, max_samples: {self.max_samples}, max_features: {self.max_features}, bootstrap: {self.bootstrap}")
        
        # Prepare features based on learning approach
        if self.is_supervised and self.label_column in self.processed_data.columns:
            if self.use_labels_for_training:
                # Supervised: use labels for training
                X = self.processed_data.drop(columns=[self.label_column])
                y = self.processed_data[self.label_column]
                logger.info("Using labels for supervised training")
            else:
                # Unsupervised: remove labels during training
                X = self.processed_data.drop(columns=[self.label_column])
                y = None
                logger.info("Removed labels for unsupervised training (will compare later)")
        else:
            X = self.processed_data
            y = None
        
        self.models = {}
        
        for contamination in contamination_levels:
            logger.info(f"Training model with contamination: {contamination}")
            
            # Convert max_features string to appropriate value
            max_features_value = self.max_features
            if isinstance(max_features_value, str):
                if max_features_value == 'sqrt':
                    # Calculate sqrt of number of features
                    max_features_value = int(np.sqrt(X.shape[1]))
                elif max_features_value == 'log2':
                    # Calculate log2 of number of features
                    max_features_value = int(np.log2(X.shape[1]))
                elif max_features_value == 'auto':
                    # Default to sqrt for auto
                    max_features_value = int(np.sqrt(X.shape[1]))
            
            model = IsolationForest(
                contamination=contamination,
                random_state=self.random_state,
                n_estimators=self.n_estimators,
                max_samples=self.max_samples,
                max_features=max_features_value,
                bootstrap=self.bootstrap,
                n_jobs=-1
            )
            
            model.fit(X)
            self.models[contamination] = model
            
            # Generate predictions and scores
            predictions = model.predict(X)
            scores = model.decision_function(X)
            
            self.predictions[contamination] = predictions
            self.anomaly_scores[contamination] = scores
            
            logger.info(f"Model trained successfully with contamination: {contamination}")
        
        return self.models
    
    def save_model(self, model_path: str = None) -> str:
        """
        Save the trained model and preprocessing objects to disk.
        
        Args:
            model_path: Path to save the model (optional)
            
        Returns:
            Path where the model was saved
        """
        if not self.models:
            raise ValueError("No trained models found. Please train models first.")
        
        if model_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_path = f"fraud_detection_model_{timestamp}.joblib"
        
        # Create model package
        model_package = {
            'models': self.models,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'label_column': self.label_column,
            'is_supervised': self.is_supervised,
            'use_labels_for_training': self.use_labels_for_training,
            'primary_keys': self.primary_keys,
            'categorical_columns': self.categorical_columns,
            'numerical_columns': self.numerical_columns,
            'high_cardinality_columns': self.high_cardinality_columns,
            'low_variance_columns': self.low_variance_columns,
            'use_risk_score_threshold': self.use_risk_score_threshold,
            'risk_score_threshold': self.risk_score_threshold,
            'contamination_levels': self.contamination_levels,
            'n_estimators': self.n_estimators,
            'max_samples': self.max_samples,
            'max_features': self.max_features,
            'bootstrap': self.bootstrap,
            'random_state': self.random_state,
            'model_metadata': {
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'algorithm': 'IsolationForest',
                'prediction_mode': 'batch_training'
            }
        }
        
        # Save the model
        joblib.dump(model_package, model_path)
        self.model_save_path = model_path
        
        logger.info(f"Model saved successfully to: {model_path}")
        print(f"✅ Model saved to: {model_path}")
        
        return model_path
    
    def load_model(self, model_path: str) -> None:
        """
        Load a pre-trained model and preprocessing objects from disk.
        
        Args:
            model_path: Path to the saved model
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        try:
            # Load the model package
            model_package = joblib.load(model_path)
            
            # Restore all attributes
            self.models = model_package['models']
            self.scaler = model_package['scaler']
            self.label_encoders = model_package['label_encoders']
            self.label_column = model_package['label_column']
            self.is_supervised = model_package['is_supervised']
            self.use_labels_for_training = model_package['use_labels_for_training']
            self.primary_keys = model_package['primary_keys']
            self.categorical_columns = model_package['categorical_columns']
            self.numerical_columns = model_package['numerical_columns']
            self.high_cardinality_columns = model_package['high_cardinality_columns']
            self.low_variance_columns = model_package['low_variance_columns']
            self.use_risk_score_threshold = model_package['use_risk_score_threshold']
            self.risk_score_threshold = model_package['risk_score_threshold']
            self.contamination_levels = model_package['contamination_levels']
            self.n_estimators = model_package['n_estimators']
            self.max_samples = model_package['max_samples']
            self.max_features = model_package['max_features']
            self.bootstrap = model_package['bootstrap']
            self.random_state = model_package['random_state']
            
            self.model_loaded = True
            self.model_save_path = model_path
            
            logger.info(f"Model loaded successfully from: {model_path}")
            print(f"✅ Model loaded from: {model_path}")
            
            # Display model info
            metadata = model_package.get('model_metadata', {})
            print(f"📊 Model Info:")
            print(f"   • Algorithm: {metadata.get('algorithm', 'Unknown')}")
            print(f"   • Trained on: {metadata.get('timestamp', 'Unknown')}")
            print(f"   • Contamination Levels: {list(self.models.keys())}")
            print(f"   • Risk Score Threshold: {self.risk_score_threshold if self.use_risk_score_threshold else 'Classic'}")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def preprocess_stream_data(self, stream_data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess stream data using the same preprocessing steps as training data.
        
        Args:
            stream_data: New data to preprocess
            
        Returns:
            Preprocessed DataFrame
        """
        if not self.model_loaded:
            raise ValueError("No model loaded. Please load a model first.")
        
        logger.info("Preprocessing stream data...")
        processed_stream_data = stream_data.copy()
        
        # Remove primary key columns if they exist
        if self.primary_keys:
            existing_primary_keys = [col for col in self.primary_keys if col in processed_stream_data.columns]
            if existing_primary_keys:
                logger.info(f"Removing primary key columns: {existing_primary_keys}")
                processed_stream_data = processed_stream_data.drop(columns=existing_primary_keys)
        
        # Remove high cardinality columns if they exist
        if self.high_cardinality_columns:
            existing_high_cardinality = [col for col in self.high_cardinality_columns 
                                      if col in processed_stream_data.columns and col not in self.primary_keys]
            if existing_high_cardinality:
                logger.info(f"Removing high cardinality columns: {existing_high_cardinality}")
                processed_stream_data = processed_stream_data.drop(columns=existing_high_cardinality)
        
        # Remove low variance columns if they exist (but keep label column if present)
        if self.low_variance_columns:
            existing_low_variance = [col for col in self.low_variance_columns 
                                   if col in processed_stream_data.columns and col != self.label_column]
            if existing_low_variance:
                logger.info(f"Removing low variance columns: {existing_low_variance}")
                processed_stream_data = processed_stream_data.drop(columns=existing_low_variance)
        
        # Handle missing values
        self._handle_missing_values_stream(processed_stream_data)
        
        # Encode categorical variables using saved encoders
        self._encode_categorical_variables_stream(processed_stream_data)
        
        # Standardize numerical features using saved scaler
        self._standardize_numerical_features_stream(processed_stream_data)
        
        logger.info(f"Stream data preprocessing completed. Shape: {processed_stream_data.shape}")
        return processed_stream_data
    
    def _handle_missing_values_stream(self, data: pd.DataFrame) -> None:
        """Handle missing values in stream data."""
        for col in data.columns:
            if data[col].isnull().sum() > 0:
                if col in self.categorical_columns:
                    # Use mode from training data or most frequent value
                    if col in self.label_encoders:
                        # Use the most frequent class from training
                        mode_value = data[col].mode()[0] if not data[col].mode().empty else data[col].iloc[0]
                    else:
                        mode_value = data[col].mode()[0] if not data[col].mode().empty else data[col].iloc[0]
                    data[col].fillna(mode_value, inplace=True)
                    logger.info(f"Filled missing values in '{col}' with mode: {mode_value}")
                else:
                    # Use median from training data
                    median_value = data[col].median()
                    data[col].fillna(median_value, inplace=True)
                    logger.info(f"Filled missing values in '{col}' with median: {median_value:.4f}")
    
    def _encode_categorical_variables_stream(self, data: pd.DataFrame) -> None:
        """Encode categorical variables using saved encoders."""
        categorical_cols = [col for col in data.columns 
                          if col in self.categorical_columns and col != self.label_column]
        
        for col in categorical_cols:
            if col in self.label_encoders:
                # Use saved encoder
                le = self.label_encoders[col]
                # Handle unseen categories by using the most frequent class
                data[col] = data[col].astype(str)
                unique_values = data[col].unique()
                known_values = le.classes_
                unknown_values = set(unique_values) - set(known_values)
                
                if unknown_values:
                    logger.warning(f"Unknown categories in '{col}': {unknown_values}")
                    # Replace unknown values with the most frequent known value
                    most_frequent = le.classes_[0]  # First class is usually the most frequent
                    data[col] = data[col].replace(list(unknown_values), most_frequent)
                
                data[col] = le.transform(data[col])
                logger.info(f"Encoded categorical column: {col}")
            else:
                # If no encoder found, use simple label encoding
                le = LabelEncoder()
                data[col] = le.fit_transform(data[col].astype(str))
                logger.info(f"Created new encoder for categorical column: {col}")
    
    def _standardize_numerical_features_stream(self, data: pd.DataFrame) -> None:
        """Standardize numerical features using saved scaler."""
        numerical_cols = [col for col in data.columns 
                         if col in self.numerical_columns and col != self.label_column]
        
        if numerical_cols:
            data[numerical_cols] = self.scaler.transform(data[numerical_cols])
            logger.info(f"Standardized {len(numerical_cols)} numerical columns")
    
    def predict_stream(self, stream_data: pd.DataFrame, contamination: float = None) -> Dict:
        """
        Make predictions on stream data using loaded model.
        
        Args:
            stream_data: New data to predict on
            contamination: Contamination level to use (if None, uses the first available)
            
        Returns:
            Dictionary containing predictions and scores
        """
        if not self.model_loaded:
            raise ValueError("No model loaded. Please load a model first.")
        
        if not self.models:
            raise ValueError("No models available for prediction.")
        
        # Use specified contamination or the first available
        if contamination is None:
            contamination = list(self.models.keys())[0]
        
        if contamination not in self.models:
            raise ValueError(f"Contamination level {contamination} not found in loaded models.")
        
        logger.info(f"Making predictions on stream data with contamination: {contamination}")
        
        # Preprocess the stream data
        processed_data = self.preprocess_stream_data(stream_data)
        
        # Remove label column if present (for prediction)
        if self.label_column and self.label_column in processed_data.columns:
            processed_data = processed_data.drop(columns=[self.label_column])
        
        # Get the model
        model = self.models[contamination]
        
        # Make predictions
        predictions = model.predict(processed_data)
        scores = model.decision_function(processed_data)
        
        # Get binary predictions based on selected method
        binary_predictions = self._get_risk_score_predictions_stream(scores)
        
        # Calculate risk scores
        min_score, max_score = scores.min(), scores.max()
        risk_scores = (max_score - scores) / (max_score - min_score)
        
        # Create results
        results = {
            'predictions': predictions,
            'binary_predictions': binary_predictions,
            'scores': scores,
            'risk_scores': risk_scores,
            'contamination': contamination,
            'data_shape': stream_data.shape,
            'processed_shape': processed_data.shape
        }
        
        logger.info(f"Stream predictions completed. Found {binary_predictions.sum()} anomalies out of {len(binary_predictions)} records")
        
        return results
    
    def _get_risk_score_predictions_stream(self, scores: np.ndarray) -> np.ndarray:
        """
        Get predictions based on risk score threshold for stream data.
        
        Args:
            scores: Anomaly scores from the model
            
        Returns:
            Binary predictions (0: normal, 1: anomaly)
        """
        if not self.use_risk_score_threshold:
            # Use classic Isolation Forest predictions
            return (scores < 0).astype(int)
        
        # Use risk score threshold
        min_score, max_score = scores.min(), scores.max()
        normalized_risk_scores = (max_score - scores) / (max_score - min_score)
        
        # Apply threshold
        return (normalized_risk_scores >= self.risk_score_threshold).astype(int)
    
    def export_stream_results(self, stream_data: pd.DataFrame, results: Dict, 
                            output_dir: str = "stream_prediction_results") -> None:
        """
        Export stream prediction results to CSV files.
        
        Args:
            stream_data: Original stream data
            results: Prediction results from predict_stream
            output_dir: Directory to save results
        """
        logger.info(f"Exporting stream results to: {output_dir}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create results DataFrame
        results_df = stream_data.copy()
        results_df['anomaly_prediction'] = results['predictions']
        results_df['anomaly_score'] = results['scores']
        results_df['is_fraud'] = results['binary_predictions']
        results_df['risk_score'] = results['risk_scores']
        
        # Save results
        filename = f"stream_predictions_contamination_{results['contamination']}_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)
        results_df.to_csv(filepath, index=False)
        logger.info(f"Stream results exported to: {filepath}")
        
        # Save summary
        summary = {
            'timestamp': timestamp,
            'contamination': results['contamination'],
            'total_records': len(results['binary_predictions']),
            'anomalies_detected': int(results['binary_predictions'].sum()),
            'anomaly_rate': float(results['binary_predictions'].mean()),
            'data_shape': results['data_shape'],
            'processed_shape': results['processed_shape'],
            'use_risk_score_threshold': self.use_risk_score_threshold,
            'risk_score_threshold': self.risk_score_threshold
        }
        
        summary_file = os.path.join(output_dir, f"stream_summary_{timestamp}.json")
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Stream summary exported to: {summary_file}")
    
    def _get_risk_score_predictions(self, contamination: float) -> np.ndarray:
        """
        Get predictions based on risk score threshold.
        
        Args:
            contamination: Contamination level for the model
            
        Returns:
            Binary predictions (0: normal, 1: anomaly)
        """
        if not self.use_risk_score_threshold:
            # Use classic Isolation Forest predictions
            return (self.predictions[contamination] == -1).astype(int)
        
        # Use risk score threshold
        risk_scores = self.anomaly_scores[contamination]
        min_score, max_score = risk_scores.min(), risk_scores.max()
        normalized_risk_scores = (max_score - risk_scores) / (max_score - min_score)
        
        # Apply threshold
        return (normalized_risk_scores >= self.risk_score_threshold).astype(int)
    
    def evaluate_models(self) -> Dict:
        """
        Evaluate models and return performance metrics.
        
        Returns:
            Dictionary of evaluation results
        """
        if not self.is_supervised or not self.label_column:
            logger.info("Unsupervised mode - skipping supervised evaluation")
            return {}
        
        logger.info("Evaluating models with supervised metrics...")
        
        # Get actual labels for evaluation
        y_true = self.data[self.label_column]  # Use original data labels
        self.results = {}
        
        for contamination, model in self.models.items():
            predictions = self.predictions[contamination]
            scores = self.anomaly_scores[contamination]
            
            # Get binary predictions based on selected method
            binary_predictions = self._get_risk_score_predictions(contamination)
            
            # Calculate metrics
            accuracy = accuracy_score(y_true, binary_predictions)
            f1 = f1_score(y_true, binary_predictions, average='weighted')
            precision = precision_score(y_true, binary_predictions, average='weighted')
            recall = recall_score(y_true, binary_predictions, average='weighted')
            
            # ROC AUC (convert y_true to binary if needed)
            if y_true.nunique() == 2:
                y_true_binary = (y_true == y_true.unique()[1]).astype(int)
                roc_auc = roc_auc_score(y_true_binary, scores)
            else:
                roc_auc = None
            
            # Calculate confusion matrix
            cm = confusion_matrix(y_true, binary_predictions)
            
            self.results[contamination] = {
                'accuracy': accuracy,
                'f1_score': f1,
                'precision': precision,
                'recall': recall,
                'roc_auc': roc_auc,
                'predictions': binary_predictions,
                'scores': scores,
                'confusion_matrix': cm
            }
            
            logger.info(f"Contamination {contamination}: Accuracy={accuracy:.4f}, F1={f1:.4f}")
        
        return self.results
    
    def create_visualizations(self, save_plots: bool = True, show_interactive: bool = True) -> None:
        """
        Create comprehensive visualizations for the fraud detection results.
        
        Args:
            save_plots: Whether to save plots as PNG files
            show_interactive: Whether to show interactive plots (can block terminal)
        """
        logger.info("Creating visualizations...")
        
        # Set up the plotting style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Create 4-panel visualization
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Isolation Forest Fraud Detection Analysis', fontsize=16, fontweight='bold')
        
        # 1. Feature Importance (using feature variance)
        self._plot_feature_importance(axes[0, 0])
        
        # 2. Anomaly Score Distribution
        self._plot_anomaly_scores(axes[0, 1])
        
        # 3. Confusion Matrix (if supervised)
        if self.is_supervised and self.results:
            self._plot_confusion_matrix(axes[1, 0])
        else:
            axes[1, 0].text(0.5, 0.5, 'No supervised evaluation\n(Unsupervised mode)', 
                           ha='center', va='center', transform=axes[1, 0].transAxes)
            axes[1, 0].set_title('Confusion Matrix')
        
        # 4. ROC Curve (if supervised and binary)
        if self.is_supervised and self.results and self.label_column:
            y_true = self.processed_data[self.label_column]
            if y_true.nunique() == 2:
                self._plot_roc_curve(axes[1, 1])
            else:
                axes[1, 1].text(0.5, 0.5, 'Multi-class labels\n(ROC not applicable)', 
                               ha='center', va='center', transform=axes[1, 1].transAxes)
                axes[1, 1].set_title('ROC Curve')
        else:
            axes[1, 1].text(0.5, 0.5, 'No supervised evaluation\n(Unsupervised mode)', 
                           ha='center', va='center', transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('ROC Curve')
        
        plt.tight_layout()
        
        if save_plots:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plot_path = f"fraud_detection_analysis_{timestamp}.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            logger.info(f"Plot saved as: {plot_path}")
            print(f"📊 Visualization saved as: {plot_path}")
        
        if show_interactive:
            plt.show()
        else:
            plt.close(fig)
            print("📊 Visualization created and saved (interactive display skipped)")
    
    def _plot_feature_importance(self, ax) -> None:
        """Plot feature importance based on variance."""
        if self.processed_data is None:
            return
        
        # Calculate feature variance
        feature_vars = self.processed_data.var().sort_values(ascending=True)
        
        # Plot top 10 features
        top_features = feature_vars.tail(10)
        top_features.plot(kind='barh', ax=ax, color='skyblue')
        ax.set_title('Feature Importance (Variance)')
        ax.set_xlabel('Variance')
        ax.grid(True, alpha=0.3)
    
    def _plot_anomaly_scores(self, ax) -> None:
        """Plot anomaly score distribution."""
        if not self.anomaly_scores:
            return
        
        # Use the first available contamination level
        contamination = list(self.anomaly_scores.keys())[0]
        scores = self.anomaly_scores[contamination]
        
        ax.hist(scores, bins=50, alpha=0.7, color='lightcoral', edgecolor='black')
        ax.axvline(scores.mean(), color='red', linestyle='--', 
                  label=f'Mean: {scores.mean():.3f}')
        ax.set_title(f'Anomaly Score Distribution (Contamination: {contamination})')
        ax.set_xlabel('Anomaly Score')
        ax.set_ylabel('Frequency')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_confusion_matrix(self, ax) -> None:
        """Plot confusion matrix for the best performing model."""
        if not self.results:
            return
        
        # Find best model by F1 score
        best_contamination = max(self.results.keys(), 
                               key=lambda k: self.results[k]['f1_score'])
        
        y_true = self.processed_data[self.label_column]
        y_pred = self.results[best_contamination]['predictions']
        
        cm = confusion_matrix(y_true, y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax)
        ax.set_title(f'Confusion Matrix (Contamination: {best_contamination})')
        ax.set_xlabel('Predicted')
        ax.set_ylabel('Actual')
    
    def _plot_roc_curve(self, ax) -> None:
        """Plot ROC curve for the best performing model."""
        if not self.results:
            return
        
        # Find best model by F1 score
        best_contamination = max(self.results.keys(), 
                               key=lambda k: self.results[k]['f1_score'])
        
        y_true = self.processed_data[self.label_column]
        y_true_binary = (y_true == y_true.unique()[1]).astype(int)
        scores = self.results[best_contamination]['scores']
        
        fpr, tpr, _ = roc_curve(y_true_binary, scores)
        roc_auc = roc_auc_score(y_true_binary, scores)
        
        ax.plot(fpr, tpr, color='darkorange', lw=2, 
               label=f'ROC Curve (AUC = {roc_auc:.3f})')
        ax.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.set_xlabel('False Positive Rate')
        ax.set_ylabel('True Positive Rate')
        ax.set_title(f'ROC Curve (Contamination: {best_contamination})')
        ax.legend(loc="lower right")
        ax.grid(True, alpha=0.3)
    
    def export_results(self, output_dir: str = "fraud_detection_results") -> None:
        """
        Export results to CSV files and save additional metrics.
        
        Args:
            output_dir: Directory to save results
        """
        logger.info(f"Exporting results to: {output_dir}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export main results
        for contamination, predictions in self.predictions.items():
            results_df = self.data.copy()
            results_df['anomaly_prediction'] = predictions
            results_df['anomaly_score'] = self.anomaly_scores[contamination]
            
            # Get binary predictions based on selected method
            binary_predictions = self._get_risk_score_predictions(contamination)
            results_df['is_fraud'] = binary_predictions
            
            # Add risk score (inverted normalized anomaly score for Isolation Forest)
            # Higher risk_score = Higher anomaly probability
            scores = self.anomaly_scores[contamination]
            min_score, max_score = scores.min(), scores.max()
            results_df['risk_score'] = (max_score - scores) / (max_score - min_score)
            
            filename = f"fraud_predictions_contamination_{contamination}_{timestamp}.csv"
            filepath = os.path.join(output_dir, filename)
            results_df.to_csv(filepath, index=False)
            logger.info(f"Results exported to: {filepath}")
        
        # Export evaluation metrics
        if self.results:
            metrics_data = []
            for contamination, metrics in self.results.items():
                metrics_data.append({
                    'contamination': contamination,
                    'accuracy': metrics['accuracy'],
                    'f1_score': metrics['f1_score'],
                    'precision': metrics['precision'],
                    'recall': metrics['recall'],
                    'roc_auc': metrics.get('roc_auc', None)
                })
            
            metrics_df = pd.DataFrame(metrics_data)
            metrics_file = os.path.join(output_dir, f"evaluation_metrics_{timestamp}.csv")
            metrics_df.to_csv(metrics_file, index=False)
            logger.info(f"Metrics exported to: {metrics_file}")
        
        # Export configuration
        config = {
            'timestamp': timestamp,
            'data_shape': self.data.shape,
            'processed_shape': self.processed_data.shape if self.processed_data is not None else None,
            'is_supervised': self.is_supervised,
            'use_labels_for_training': self.use_labels_for_training,
            'label_column': self.label_column,
            'primary_keys': self.primary_keys,
            'categorical_columns': self.categorical_columns,
            'numerical_columns': self.numerical_columns,
            'high_cardinality_columns': self.high_cardinality_columns,
            'low_variance_columns': self.low_variance_columns,
            'contamination_levels': list(self.models.keys()),
            'use_risk_score_threshold': self.use_risk_score_threshold,
            'risk_score_threshold': self.risk_score_threshold,
            'n_estimators': self.n_estimators,
            'max_samples': self.max_samples,
            'max_features': self.max_features,
            'bootstrap': self.bootstrap
        }
        
        config_file = os.path.join(output_dir, f"configuration_{timestamp}.json")
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2, default=str)
        logger.info(f"Configuration exported to: {config_file}")
    
    def print_summary(self) -> None:
        """Print comprehensive summary of the fraud detection analysis."""
        print("\n" + "="*80)
        print("📊 FRAUD DETECTION ANALYSIS SUMMARY")
        print("="*80)
        
        print(f"📈 Dataset: {self.data.shape[0]:,} rows × {self.data.shape[1]} columns")
        print(f"🔧 Processed: {self.processed_data.shape[0]:,} rows × {self.processed_data.shape[1]} columns")
        print(f"🎯 Mode: {'Supervised' if self.is_supervised else 'Unsupervised'}")
        if self.is_supervised:
            print(f"🎓 Learning Approach: {'Supervised' if self.use_labels_for_training else 'Unsupervised (labels removed during training)'}")
        print(f"🔍 Method: {'Risk Score Based' if self.use_risk_score_threshold else 'Classic Isolation Forest'}")
        if self.use_risk_score_threshold:
            print(f"🎯 Risk Score Threshold: {self.risk_score_threshold}")
        
        if self.is_supervised and self.label_column:
            print(f"🏷️  Label Column: {self.label_column}")
            
            # Show actual fraud/non-fraud counts
            fraud_counts = self.data[self.label_column].value_counts().sort_index()
            print(f"\n📊 ACTUAL DATA DISTRIBUTION:")
            print("-" * 40)
            for label, count in fraud_counts.items():
                percentage = (count / len(self.data)) * 100
                label_name = "FRAUD" if label == 1 else "NORMAL"
                print(f"  {label_name} ({label}): {count:,} ({percentage:.2f}%)")
        
        if self.use_risk_score_threshold:
            print(f"\n🤖 Models Trained: 1 model (risk score based detection)")
        else:
            print(f"\n🤖 Models Trained: {len(self.models)} contamination levels (classic comparison)")
        
        print(f"\n⚙️  FINE-TUNING PARAMETERS:")
        print(f"   • Contamination Levels: {self.contamination_levels}")
        print(f"   • N Estimators: {self.n_estimators}")
        print(f"   • Max Samples: {self.max_samples}")
        print(f"   • Max Features: {self.max_features}")
        print(f"   • Bootstrap: {self.bootstrap}")
        
        if self.results:
            print("\n📊 MODEL PERFORMANCE:")
            print("-" * 50)
            for contamination, metrics in self.results.items():
                print(f"Contamination {contamination}:")
                print(f"  • Accuracy:  {metrics['accuracy']:.4f}")
                print(f"  • F1-Score:  {metrics['f1_score']:.4f}")
                print(f"  • Precision: {metrics['precision']:.4f}")
                print(f"  • Recall:    {metrics['recall']:.4f}")
                if metrics.get('roc_auc'):
                    print(f"  • ROC-AUC:   {metrics['roc_auc']:.4f}")
                
                # Show confusion matrix details
                if 'confusion_matrix' in metrics:
                    cm = metrics['confusion_matrix']
                    tn, fp, fn, tp = cm.ravel()
                    print(f"\n  📋 CONFUSION MATRIX:")
                    print(f"    • True Negative  (TN): {tn:,} - Correctly predicted NORMAL")
                    print(f"    • False Positive (FP): {fp:,} - Incorrectly predicted FRAUD")
                    print(f"    • False Negative (FN): {fn:,} - Missed FRAUD")
                    print(f"    • True Positive  (TP): {tp:,} - Correctly predicted FRAUD")
                    print(f"    • Total Predictions: {tn + fp + fn + tp:,}")
                print()
        
        # Find best model
        if self.results:
            best_contamination = max(self.results.keys(), 
                                   key=lambda k: self.results[k]['f1_score'])
            print(f"🏆 Best Model: Contamination {best_contamination}")
            print(f"   F1-Score: {self.results[best_contamination]['f1_score']:.4f}")
        
        print("="*80)


def main():
    """
    Main function to run the Isolation Forest fraud detection system.
    """
    print("🔍 ISOLATION FOREST FRAUD DETECTION SYSTEM")
    print("=" * 60)
    print("Enterprise Fraud Detection Platform v1.0.0")
    print("=" * 60)
    
    # Initialize the fraud detector
    detector = IsolationForestFraudDetector(random_state=42)
    
    try:
        # Step 1: Setup prediction mode
        detector.setup_prediction_mode()
        
        if detector.prediction_mode == 'batch':
            # BATCH PREDICTION MODE
            print("\n" + "="*60)
            print("🔄 BATCH PREDICTION MODE")
            print("="*60)
            
            # Step 2: Load and analyze data
            file_path = input("📁 Enter CSV file path: ").strip()
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            detector.load_and_analyze_data(file_path)
            
            # Step 3: Check data suitability
            if not detector.check_data_suitability():
                proceed = input("\n⚠️  Continue anyway? (y/n): ").lower().strip()
                if proceed not in ['y', 'yes']:
                    print("Exiting...")
                    return
            
            # Step 4: Setup learning mode
            detector.setup_learning_mode()
            
            # Step 5: Preprocess data
            print("\n🔧 Preprocessing data...")
            detector.preprocess_data()
            
            # Step 6: Train models
            print("\n🤖 Training Isolation Forest models...")
            if detector.use_risk_score_threshold:
                print("   Using single contamination level (0.1) for risk score based detection")
            else:
                print("   Using multiple contamination levels for comparison")
            detector.train_models()
            
            # Step 7: Evaluate models (if supervised)
            if detector.is_supervised:
                print("\n📊 Evaluating models...")
                detector.evaluate_models()
            
            # Step 8: Create visualizations
            print("\n📈 Creating visualizations...")
            
            # Ask user if they want to see interactive plots
            show_plots = input("Show interactive plots? (y/n - default: n): ").lower().strip()
            show_interactive = show_plots in ['y', 'yes']
            
            detector.create_visualizations(save_plots=True, show_interactive=show_interactive)
            
            # Step 9: Export results
            print("\n💾 Exporting results...")
            detector.export_results()
            
            # Step 10: Ask if user wants to save model (for both classic and risk score methods)
            print("\n" + "="*60)
            print("💾 MODEL SAVING OPTIONS")
            print("="*60)
            save_model = input("Save trained model for future use? (y/n): ").lower().strip()
            if save_model in ['y', 'yes']:
                model_path = input("Enter model save path (or press Enter for auto-generated name): ").strip()
                if not model_path:
                    model_path = None
                detector.save_model(model_path)
                print("✅ Model saved successfully!")
            else:
                print("📝 Model not saved. You can always retrain when needed.")
            
            # Step 11: Print summary
            detector.print_summary()
            
            print("\n✅ Batch fraud detection analysis completed successfully!")
            print("📊 Results have been exported to the fraud_detection_results folder")
            if not show_interactive:
                print("📈 Visualizations have been saved as PNG files")
            
        elif detector.prediction_mode == 'stream':
            # STREAM PREDICTION MODE
            print("\n" + "="*60)
            print("🌊 STREAM PREDICTION MODE")
            print("="*60)
            
            # Step 2: Load pre-trained model
            model_path = input("📁 Enter path to saved model (.joblib file): ").strip()
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found: {model_path}")
            
            detector.load_model(model_path)
            
            # Step 3: Load stream data
            stream_file_path = input("📁 Enter CSV file path for stream data: ").strip()
            if not os.path.exists(stream_file_path):
                raise FileNotFoundError(f"Stream data file not found: {stream_file_path}")
            
            print(f"Loading stream data from: {stream_file_path}")
            stream_data = pd.read_csv(stream_file_path)
            print(f"Stream data loaded. Shape: {stream_data.shape}")
            
            # Step 4: Select contamination level (if multiple available)
            if len(detector.models) > 1:
                print(f"\nAvailable contamination levels: {list(detector.models.keys())}")
                contamination_choice = input("Enter contamination level to use (or press Enter for first available): ").strip()
                if contamination_choice:
                    try:
                        contamination = float(contamination_choice)
                        if contamination not in detector.models:
                            print(f"Contamination {contamination} not found. Using first available.")
                            contamination = None
                    except ValueError:
                        print("Invalid contamination level. Using first available.")
                        contamination = None
                else:
                    contamination = None
            else:
                contamination = None
            
            # Step 5: Make predictions
            print("\n🔮 Making predictions on stream data...")
            results = detector.predict_stream(stream_data, contamination)
            
            # Step 6: Display results summary
            print("\n📊 STREAM PREDICTION RESULTS:")
            print("-" * 40)
            print(f"Total Records: {len(results['binary_predictions']):,}")
            print(f"Anomalies Detected: {results['binary_predictions'].sum():,}")
            print(f"Anomaly Rate: {results['binary_predictions'].mean():.2%}")
            print(f"Contamination Used: {results['contamination']}")
            print(f"Data Shape: {results['data_shape']}")
            print(f"Processed Shape: {results['processed_shape']}")
            
            # Step 7: Export stream results
            print("\n💾 Exporting stream results...")
            detector.export_stream_results(stream_data, results)
            
            print("\n✅ Stream prediction completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        print(f"\n❌ Error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
