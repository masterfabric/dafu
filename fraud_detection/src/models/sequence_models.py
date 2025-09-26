"""
LSTM and GRU-based Fraud Detection System

This module implements comprehensive fraud detection using LSTM and GRU neural networks
with support for both supervised and unsupervised learning modes.

Features:
- Automatic data analysis and sequence preparation
- Data preprocessing and feature engineering
- LSTM and GRU model training and evaluation
- Comprehensive evaluation and visualization
- Production-ready with proper error handling

Author: Enterprise Fraud Detection Platform
Version: 1.0.0
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler
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
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, GRU, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.utils import to_categorical

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Set random seeds for reproducibility
tf.random.set_seed(42)
np.random.seed(42)


class SequenceFraudDetector:
    """
    Comprehensive LSTM/GRU-based fraud detection system.
    
    This class provides a complete fraud detection pipeline including data analysis,
    sequence preparation, model training, evaluation, and visualization capabilities.
    """
    
    def __init__(self, random_state: int = 42, sequence_length: int = 10):
        """
        Initialize the fraud detector.
        
        Args:
            random_state: Random state for reproducibility
            sequence_length: Length of sequences for LSTM/GRU input
        """
        self.random_state = random_state
        self.sequence_length = sequence_length
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
        self.scaler = MinMaxScaler()
        self.sequence_scaler = MinMaxScaler()
        
        # Model storage
        self.lstm_model = None
        self.gru_model = None
        self.lstm_predictions = None
        self.gru_predictions = None
        self.lstm_scores = None
        self.gru_scores = None
        self.results = {}
        
        # Sequence data
        self.X_sequences = None
        self.y_sequences = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        
        # Fine-tuning parameters
        self.selected_models = []  # List of selected models (LSTM, GRU, or both)
        self.epochs = 50
        self.batch_size = 32
        self.learning_rate = 0.001
        self.lstm_units = [64, 32, 16]  # LSTM layer units
        self.gru_units = [64, 32, 16]   # GRU layer units
        self.dropout_rate = 0.2
        self.dense_units = 16
        self.early_stopping_patience = 10
        self.reduce_lr_patience = 5
        self.reduce_lr_factor = 0.5
        
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
        print("🔍 SEQUENCE MODEL SUITABILITY CHECK")
        print("="*50)
        
        if len(self.numerical_columns) < 2:
            print("⚠️  WARNING: Very few numerical columns. LSTM/GRU work best with numerical features.")
        elif len(self.data) < 100:
            print("⚠️  WARNING: Small dataset. Results may not be reliable.")
        elif len(self.data) < self.sequence_length * 2:
            print(f"⚠️  WARNING: Dataset too small for sequence length {self.sequence_length}.")
        else:
            print("✅ Data appears suitable for LSTM/GRU analysis.")
        
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
        Check if data is suitable for LSTM/GRU.
        
        Returns:
            True if suitable, False otherwise
        """
        print("\n" + "="*60)
        print("🔍 SEQUENCE MODEL SUITABILITY CHECK")
        print("="*60)
        
        issues = []
        
        if len(self.numerical_columns) < 2:
            issues.append("Insufficient numerical features (need at least 2)")
        
        if len(self.data) < 100:
            issues.append("Dataset too small (need at least 100 samples)")
        
        if len(self.data) < self.sequence_length * 2:
            issues.append(f"Dataset too small for sequence length {self.sequence_length}")
        
        if len(self.high_cardinality_columns) > len(self.categorical_columns) * 0.5:
            issues.append("Too many high cardinality categorical columns")
        
        if issues:
            print("❌ Data may not be suitable for LSTM/GRU:")
            for issue in issues:
                print(f"   • {issue}")
            print("\n💡 Suggestions:")
            print("   • Use more numerical features")
            print("   • Consider reducing sequence length")
            print("   • Preprocess categorical variables differently")
            return False
        else:
            print("✅ Data appears suitable for LSTM/GRU analysis!")
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
    
    def _setup_fine_tuning_parameters(self) -> None:
        """Setup fine-tuning parameters for LSTM/GRU models."""
        print("\n" + "="*60)
        print("⚙️  FINE-TUNING PARAMETERS SETUP")
        print("="*60)
        print("Configure LSTM/GRU model parameters for optimal performance:")
        
        # Model selection
        self._setup_model_selection()
        
        # Common parameters
        self._setup_common_parameters()
        
        # Model-specific parameters
        if 'LSTM' in self.selected_models:
            self._setup_lstm_parameters()
        
        if 'GRU' in self.selected_models:
            self._setup_gru_parameters()
        
        # Display final configuration
        self._display_parameter_summary()
    
    def _setup_model_selection(self) -> None:
        """Setup model selection (LSTM, GRU, or both)."""
        print("\n" + "="*50)
        print("🤖 MODEL SELECTION")
        print("="*50)
        print("Choose which models to train:")
        print("1. LSTM only - Long Short-Term Memory networks")
        print("2. GRU only - Gated Recurrent Unit networks")
        print("3. Both LSTM and GRU - Compare both models")
        print("4. Default - Use both models")
        
        while True:
            choice = input("\nEnter choice (1-4 or 'default'): ").strip()
            
            if choice.lower() in ['default', 'd', '4']:
                self.selected_models = ['LSTM', 'GRU']
                print("✅ Selected both LSTM and GRU models")
                break
            elif choice == '1':
                self.selected_models = ['LSTM']
                print("✅ Selected LSTM model only")
                break
            elif choice == '2':
                self.selected_models = ['GRU']
                print("✅ Selected GRU model only")
                break
            elif choice == '3':
                self.selected_models = ['LSTM', 'GRU']
                print("✅ Selected both LSTM and GRU models")
                break
            else:
                print("❌ Please enter '1', '2', '3', '4', or 'default'")
    
    def _setup_common_parameters(self) -> None:
        """Setup common parameters for both models."""
        print("\n" + "="*50)
        print("🔧 COMMON PARAMETERS SETUP")
        print("="*50)
        
        # Epochs setup
        self._setup_epochs()
        
        # Batch size setup
        self._setup_batch_size()
        
        # Learning rate setup
        self._setup_learning_rate()
        
        # Dropout rate setup
        self._setup_dropout_rate()
        
        # Dense units setup
        self._setup_dense_units()
        
        # Callback parameters setup
        self._setup_callback_parameters()
    
    def _setup_epochs(self) -> None:
        """Setup number of training epochs."""
        print("\n" + "="*40)
        print("🔄 EPOCHS SETUP")
        print("="*40)
        print("Number of training epochs (complete passes through the dataset)")
        print("Higher values = better training but longer time")
        print("\nExamples:")
        print("  • Quick test: 10-20 epochs")
        print("  • Standard training: 50-100 epochs")
        print("  • Thorough training: 100-500 epochs")
        print("  • Default: 50 epochs")
        
        while True:
            choice = input("\nEnter number of epochs (or 'default' for 50): ").strip()
            
            if choice.lower() in ['default', 'd']:
                self.epochs = 50
                print("✅ Using default epochs: 50")
                break
            else:
                try:
                    value = int(choice)
                    if 1 <= value <= 1000:
                        self.epochs = value
                        print(f"✅ Epochs set to: {self.epochs}")
                        break
                    else:
                        print("❌ Value must be between 1 and 1000")
                except ValueError:
                    print("❌ Please enter a valid integer")
    
    def _setup_batch_size(self) -> None:
        """Setup batch size for training."""
        print("\n" + "="*40)
        print("📦 BATCH SIZE SETUP")
        print("="*40)
        print("Number of samples per gradient update")
        print("Smaller batches = more updates but slower training")
        print("\nExamples:")
        print("  • Small dataset (<1000 samples): 16-32")
        print("  • Medium dataset (1000-10000 samples): 32-64")
        print("  • Large dataset (>10000 samples): 64-128")
        print("  • Default: 32")
        
        while True:
            choice = input("\nEnter batch size (or 'default' for 32): ").strip()
            
            if choice.lower() in ['default', 'd']:
                self.batch_size = 32
                print("✅ Using default batch size: 32")
                break
            else:
                try:
                    value = int(choice)
                    if 1 <= value <= 512:
                        self.batch_size = value
                        print(f"✅ Batch size set to: {self.batch_size}")
                        break
                    else:
                        print("❌ Value must be between 1 and 512")
                except ValueError:
                    print("❌ Please enter a valid integer")
    
    def _setup_learning_rate(self) -> None:
        """Setup learning rate for optimizer."""
        print("\n" + "="*40)
        print("📈 LEARNING RATE SETUP")
        print("="*40)
        print("Step size for weight updates during training")
        print("Higher values = faster learning but may overshoot")
        print("\nExamples:")
        print("  • Conservative: 0.0001")
        print("  • Standard: 0.001")
        print("  • Aggressive: 0.01")
        print("  • Default: 0.001")
        
        while True:
            choice = input("\nEnter learning rate (or 'default' for 0.001): ").strip()
            
            if choice.lower() in ['default', 'd']:
                self.learning_rate = 0.001
                print("✅ Using default learning rate: 0.001")
                break
            else:
                try:
                    value = float(choice)
                    if 0.0001 <= value <= 0.1:
                        self.learning_rate = value
                        print(f"✅ Learning rate set to: {self.learning_rate}")
                        break
                    else:
                        print("❌ Value must be between 0.0001 and 0.1")
                except ValueError:
                    print("❌ Please enter a valid number")
    
    def _setup_dropout_rate(self) -> None:
        """Setup dropout rate for regularization."""
        print("\n" + "="*40)
        print("🎯 DROPOUT RATE SETUP")
        print("="*40)
        print("Fraction of input units to drop for regularization")
        print("Higher values = more regularization but may underfit")
        print("\nExamples:")
        print("  • Light regularization: 0.1")
        print("  • Standard regularization: 0.2")
        print("  • Heavy regularization: 0.3-0.5")
        print("  • Default: 0.2")
        
        while True:
            choice = input("\nEnter dropout rate (or 'default' for 0.2): ").strip()
            
            if choice.lower() in ['default', 'd']:
                self.dropout_rate = 0.2
                print("✅ Using default dropout rate: 0.2")
                break
            else:
                try:
                    value = float(choice)
                    if 0.0 <= value <= 0.8:
                        self.dropout_rate = value
                        print(f"✅ Dropout rate set to: {self.dropout_rate}")
                        break
                    else:
                        print("❌ Value must be between 0.0 and 0.8")
                except ValueError:
                    print("❌ Please enter a valid number")
    
    def _setup_dense_units(self) -> None:
        """Setup dense layer units."""
        print("\n" + "="*40)
        print("🧠 DENSE UNITS SETUP")
        print("="*40)
        print("Number of units in the final dense layer")
        print("More units = more capacity but may overfit")
        print("\nExamples:")
        print("  • Simple: 8-16 units")
        print("  • Standard: 16-32 units")
        print("  • Complex: 32-64 units")
        print("  • Default: 16 units")
        
        while True:
            choice = input("\nEnter dense units (or 'default' for 16): ").strip()
            
            if choice.lower() in ['default', 'd']:
                self.dense_units = 16
                print("✅ Using default dense units: 16")
                break
            else:
                try:
                    value = int(choice)
                    if 1 <= value <= 256:
                        self.dense_units = value
                        print(f"✅ Dense units set to: {self.dense_units}")
                        break
                    else:
                        print("❌ Value must be between 1 and 256")
                except ValueError:
                    print("❌ Please enter a valid integer")
    
    def _setup_callback_parameters(self) -> None:
        """Setup callback parameters."""
        print("\n" + "="*40)
        print("⏰ CALLBACK PARAMETERS SETUP")
        print("="*40)
        print("Early stopping and learning rate reduction parameters")
        
        # Early stopping patience
        print(f"\nEarly Stopping Patience (epochs to wait before stopping):")
        print("  • Quick stop: 5-10 epochs")
        print("  • Standard: 10-20 epochs")
        print("  • Patient: 20-50 epochs")
        print("  • Default: 10 epochs")
        
        while True:
            choice = input("\nEnter early stopping patience (or 'default' for 10): ").strip()
            
            if choice.lower() in ['default', 'd']:
                self.early_stopping_patience = 10
                print("✅ Using default early stopping patience: 10")
                break
            else:
                try:
                    value = int(choice)
                    if 1 <= value <= 100:
                        self.early_stopping_patience = value
                        print(f"✅ Early stopping patience set to: {self.early_stopping_patience}")
                        break
                    else:
                        print("❌ Value must be between 1 and 100")
                except ValueError:
                    print("❌ Please enter a valid integer")
        
        # Learning rate reduction patience
        print(f"\nLearning Rate Reduction Patience (epochs to wait before reducing LR):")
        print("  • Quick reduction: 3-5 epochs")
        print("  • Standard: 5-10 epochs")
        print("  • Patient: 10-20 epochs")
        print("  • Default: 5 epochs")
        
        while True:
            choice = input("\nEnter LR reduction patience (or 'default' for 5): ").strip()
            
            if choice.lower() in ['default', 'd']:
                self.reduce_lr_patience = 5
                print("✅ Using default LR reduction patience: 5")
                break
            else:
                try:
                    value = int(choice)
                    if 1 <= value <= 50:
                        self.reduce_lr_patience = value
                        print(f"✅ LR reduction patience set to: {self.reduce_lr_patience}")
                        break
                    else:
                        print("❌ Value must be between 1 and 50")
                except ValueError:
                    print("❌ Please enter a valid integer")
        
        # Learning rate reduction factor
        print(f"\nLearning Rate Reduction Factor (multiply LR by this factor):")
        print("  • Conservative: 0.1-0.3")
        print("  • Standard: 0.5")
        print("  • Aggressive: 0.7-0.9")
        print("  • Default: 0.5")
        
        while True:
            choice = input("\nEnter LR reduction factor (or 'default' for 0.5): ").strip()
            
            if choice.lower() in ['default', 'd']:
                self.reduce_lr_factor = 0.5
                print("✅ Using default LR reduction factor: 0.5")
                break
            else:
                try:
                    value = float(choice)
                    if 0.1 <= value <= 0.9:
                        self.reduce_lr_factor = value
                        print(f"✅ LR reduction factor set to: {self.reduce_lr_factor}")
                        break
                    else:
                        print("❌ Value must be between 0.1 and 0.9")
                except ValueError:
                    print("❌ Please enter a valid number")
    
    def _setup_lstm_parameters(self) -> None:
        """Setup LSTM-specific parameters."""
        print("\n" + "="*50)
        print("🔗 LSTM PARAMETERS SETUP")
        print("="*50)
        print("Configure LSTM layer architecture")
        
        # LSTM units setup
        print(f"\nLSTM Layer Units (number of units in each LSTM layer):")
        print("  • Simple: 32,16,8")
        print("  • Standard: 64,32,16")
        print("  • Complex: 128,64,32")
        print("  • Default: 64,32,16")
        print("\nFormat: comma-separated values (e.g., 64,32,16)")
        
        while True:
            choice = input("\nEnter LSTM units (or 'default' for 64,32,16): ").strip()
            
            if choice.lower() in ['default', 'd']:
                self.lstm_units = [64, 32, 16]
                print("✅ Using default LSTM units: [64, 32, 16]")
                break
            else:
                try:
                    values = [int(x.strip()) for x in choice.split(',')]
                    if all(8 <= v <= 512 for v in values) and len(values) >= 2:
                        self.lstm_units = values
                        print(f"✅ LSTM units set to: {self.lstm_units}")
                        break
                    else:
                        print("❌ All values must be between 8 and 512, and at least 2 layers required")
                except ValueError:
                    print("❌ Please enter comma-separated integers (e.g., 64,32,16)")
    
    def _setup_gru_parameters(self) -> None:
        """Setup GRU-specific parameters."""
        print("\n" + "="*50)
        print("🔄 GRU PARAMETERS SETUP")
        print("="*50)
        print("Configure GRU layer architecture")
        
        # GRU units setup
        print(f"\nGRU Layer Units (number of units in each GRU layer):")
        print("  • Simple: 32,16,8")
        print("  • Standard: 64,32,16")
        print("  • Complex: 128,64,32")
        print("  • Default: 64,32,16")
        print("\nFormat: comma-separated values (e.g., 64,32,16)")
        
        while True:
            choice = input("\nEnter GRU units (or 'default' for 64,32,16): ").strip()
            
            if choice.lower() in ['default', 'd']:
                self.gru_units = [64, 32, 16]
                print("✅ Using default GRU units: [64, 32, 16]")
                break
            else:
                try:
                    values = [int(x.strip()) for x in choice.split(',')]
                    if all(8 <= v <= 512 for v in values) and len(values) >= 2:
                        self.gru_units = values
                        print(f"✅ GRU units set to: {self.gru_units}")
                        break
                    else:
                        print("❌ All values must be between 8 and 512, and at least 2 layers required")
                except ValueError:
                    print("❌ Please enter comma-separated integers (e.g., 64,32,16)")
    
    def _display_parameter_summary(self) -> None:
        """Display summary of all fine-tuning parameters."""
        print("\n" + "="*60)
        print("📋 FINE-TUNING PARAMETERS SUMMARY")
        print("="*60)
        print(f"🤖 Selected Models: {', '.join(self.selected_models)}")
        print(f"🔄 Epochs: {self.epochs}")
        print(f"📦 Batch Size: {self.batch_size}")
        print(f"📈 Learning Rate: {self.learning_rate}")
        print(f"🎯 Dropout Rate: {self.dropout_rate}")
        print(f"🧠 Dense Units: {self.dense_units}")
        print(f"⏰ Early Stopping Patience: {self.early_stopping_patience}")
        print(f"📉 LR Reduction Patience: {self.reduce_lr_patience}")
        print(f"🔢 LR Reduction Factor: {self.reduce_lr_factor}")
        
        if 'LSTM' in self.selected_models:
            print(f"🔗 LSTM Units: {self.lstm_units}")
        
        if 'GRU' in self.selected_models:
            print(f"🔄 GRU Units: {self.gru_units}")
        
        print("="*60)
    
    def _setup_supervised_mode(self) -> None:
        """Setup supervised learning mode with label selection."""
        print("\n📋 Available columns for label selection:")
        for i, col in enumerate(self.data.columns, 1):
            print(f"   {i}. {col}")
        
        while True:
            try:
                choice = input(f"\nEnter column number for label (1-{len(self.data.columns)}): ").strip()
                col_idx = int(choice) - 1
                if 0 <= col_idx < len(self.data.columns):
                    self.label_column = self.data.columns[col_idx]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(self.data.columns)}")
            except ValueError:
                print("Please enter a valid number.")
        
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
            print("   LSTM/GRU can handle multi-class classification.")
    
    def preprocess_data(self) -> pd.DataFrame:
        """
        Preprocess the data for LSTM/GRU.
        
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
            columns_to_remove = [col for col in self.high_cardinality_columns if col not in self.primary_keys]
            if columns_to_remove:
                logger.info(f"Removing high cardinality columns: {columns_to_remove}")
                self.processed_data = self.processed_data.drop(columns=columns_to_remove)
        
        # Remove low variance columns (but keep label column)
        if self.low_variance_columns:
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
        """Standardize numerical features using MinMaxScaler."""
        logger.info("Standardizing numerical features...")
        
        numerical_cols = [col for col in self.processed_data.columns 
                         if col in self.numerical_columns and col != self.label_column]
        
        if numerical_cols:
            self.processed_data[numerical_cols] = self.scaler.fit_transform(
                self.processed_data[numerical_cols]
            )
            logger.info(f"Standardized {len(numerical_cols)} numerical columns")
    
    def prepare_sequences(self) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Prepare sequences for LSTM/GRU training.
        
        Returns:
            Tuple of (X_sequences, y_sequences)
        """
        logger.info(f"Preparing sequences with length: {self.sequence_length}")
        
        # Prepare features based on learning approach
        if self.is_supervised and self.label_column in self.processed_data.columns:
            if self.use_labels_for_training:
                # Supervised: use labels for training
                X = self.processed_data.drop(columns=[self.label_column]).values
                y = self.processed_data[self.label_column].values
                logger.info("Using labels for supervised training")
            else:
                # Unsupervised: remove labels during training
                X = self.processed_data.drop(columns=[self.label_column]).values
                y = None
                logger.info("Removed labels for unsupervised training (will compare later)")
        else:
            X = self.processed_data.values
            y = None
        
        # Scale features for sequences
        X_scaled = self.sequence_scaler.fit_transform(X)
        
        # Create sequences
        X_sequences = []
        y_sequences = []
        
        for i in range(self.sequence_length, len(X_scaled)):
            X_sequences.append(X_scaled[i-self.sequence_length:i])
            if y is not None:
                y_sequences.append(y[i])
        
        X_sequences = np.array(X_sequences)
        y_sequences = np.array(y_sequences) if y is not None else None
        
        self.X_sequences = X_sequences
        self.y_sequences = y_sequences
        
        logger.info(f"Sequences created. Shape: {X_sequences.shape}")
        if y_sequences is not None:
            logger.info(f"Labels shape: {y_sequences.shape}")
        
        return X_sequences, y_sequences
    
    def split_data(self, test_size: float = 0.2) -> None:
        """
        Split data into train and test sets.
        
        Args:
            test_size: Proportion of data to use for testing
        """
        logger.info(f"Splitting data with test size: {test_size}")
        
        if self.y_sequences is not None:
            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                self.X_sequences, self.y_sequences, 
                test_size=test_size, 
                random_state=self.random_state,
                stratify=self.y_sequences
            )
        else:
            self.X_train, self.X_test = train_test_split(
                self.X_sequences, 
                test_size=test_size, 
                random_state=self.random_state
            )
            self.y_train = self.y_test = None
        
        logger.info(f"Training set shape: {self.X_train.shape}")
        logger.info(f"Test set shape: {self.X_test.shape}")
    
    def build_lstm_model(self, input_shape: Tuple[int, int], is_autoencoder: bool = False) -> Sequential:
        """
        Build LSTM model architecture.
        
        Args:
            input_shape: Shape of input sequences
            is_autoencoder: Whether to build autoencoder architecture for unsupervised learning
            
        Returns:
            Compiled LSTM model
        """
        logger.info("Building LSTM model...")
        
        if is_autoencoder:
            # Autoencoder architecture for unsupervised learning
            layers = []
            
            # Add LSTM layers based on user configuration
            for i, units in enumerate(self.lstm_units):
                if i == 0:
                    layers.append(LSTM(units, return_sequences=True, input_shape=input_shape))
                else:
                    layers.append(LSTM(units, return_sequences=True))
                
                layers.append(Dropout(self.dropout_rate))
                layers.append(BatchNormalization())
            
            # Output layer to reconstruct input sequence
            layers.append(Dense(input_shape[1], activation='linear'))
            
            model = Sequential(layers)
            
            model.compile(
                optimizer=Adam(learning_rate=self.learning_rate),
                loss='mse',  # Mean Squared Error for reconstruction
                metrics=['mae']  # Mean Absolute Error
            )
        else:
            # Binary classification architecture for supervised learning
            layers = []
            
            # Add LSTM layers based on user configuration
            for i, units in enumerate(self.lstm_units):
                if i == 0:
                    layers.append(LSTM(units, return_sequences=True, input_shape=input_shape))
                elif i == len(self.lstm_units) - 1:
                    layers.append(LSTM(units, return_sequences=False))
                else:
                    layers.append(LSTM(units, return_sequences=True))
                
                layers.append(Dropout(self.dropout_rate))
                layers.append(BatchNormalization())
            
            # Add dense layers
            layers.append(Dense(self.dense_units, activation='relu'))
            layers.append(Dropout(self.dropout_rate * 0.5))  # Half dropout for dense layer
            layers.append(Dense(1, activation='sigmoid'))
            
            model = Sequential(layers)
            
            model.compile(
                optimizer=Adam(learning_rate=self.learning_rate),
                loss='binary_crossentropy',
                metrics=['accuracy']
            )
        
        self.lstm_model = model
        logger.info("LSTM model built successfully")
        return model
    
    def build_gru_model(self, input_shape: Tuple[int, int], is_autoencoder: bool = False) -> Sequential:
        """
        Build GRU model architecture.
        
        Args:
            input_shape: Shape of input sequences
            is_autoencoder: Whether to build autoencoder architecture for unsupervised learning
            
        Returns:
            Compiled GRU model
        """
        logger.info("Building GRU model...")
        
        if is_autoencoder:
            # Autoencoder architecture for unsupervised learning
            layers = []
            
            # Add GRU layers based on user configuration
            for i, units in enumerate(self.gru_units):
                if i == 0:
                    layers.append(GRU(units, return_sequences=True, input_shape=input_shape))
                else:
                    layers.append(GRU(units, return_sequences=True))
                
                layers.append(Dropout(self.dropout_rate))
                layers.append(BatchNormalization())
            
            # Output layer to reconstruct input sequence
            layers.append(Dense(input_shape[1], activation='linear'))
            
            model = Sequential(layers)
            
            model.compile(
                optimizer=Adam(learning_rate=self.learning_rate),
                loss='mse',  # Mean Squared Error for reconstruction
                metrics=['mae']  # Mean Absolute Error
            )
        else:
            # Binary classification architecture for supervised learning
            layers = []
            
            # Add GRU layers based on user configuration
            for i, units in enumerate(self.gru_units):
                if i == 0:
                    layers.append(GRU(units, return_sequences=True, input_shape=input_shape))
                elif i == len(self.gru_units) - 1:
                    layers.append(GRU(units, return_sequences=False))
                else:
                    layers.append(GRU(units, return_sequences=True))
                
                layers.append(Dropout(self.dropout_rate))
                layers.append(BatchNormalization())
            
            # Add dense layers
            layers.append(Dense(self.dense_units, activation='relu'))
            layers.append(Dropout(self.dropout_rate * 0.5))  # Half dropout for dense layer
            layers.append(Dense(1, activation='sigmoid'))
            
            model = Sequential(layers)
            
            model.compile(
                optimizer=Adam(learning_rate=self.learning_rate),
                loss='binary_crossentropy',
                metrics=['accuracy']
            )
        
        self.gru_model = model
        logger.info("GRU model built successfully")
        return model
    
    def train_models(self, epochs: int = None, batch_size: int = None) -> Dict:
        """
        Train LSTM and GRU models.
        
        Args:
            epochs: Number of training epochs (overrides user settings)
            batch_size: Batch size for training (overrides user settings)
            
        Returns:
            Dictionary of training histories
        """
        # Use user-defined parameters unless overridden
        if epochs is None:
            epochs = self.epochs
        if batch_size is None:
            batch_size = self.batch_size
        
        logger.info(f"Training models: {', '.join(self.selected_models)}")
        logger.info(f"Parameters - epochs: {epochs}, batch_size: {batch_size}, learning_rate: {self.learning_rate}")
        
        input_shape = (self.X_train.shape[1], self.X_train.shape[2])
        
        # Build models based on learning approach
        is_autoencoder = (self.y_train is None)
        
        # Callbacks
        early_stopping = EarlyStopping(
            monitor='val_loss', 
            patience=self.early_stopping_patience, 
            restore_best_weights=True
        )
        reduce_lr = ReduceLROnPlateau(
            monitor='val_loss', 
            factor=self.reduce_lr_factor, 
            patience=self.reduce_lr_patience, 
            min_lr=0.0001
        )
        
        callbacks = [early_stopping, reduce_lr]
        
        # Train models based on user selection
        histories = {}
        
        if 'LSTM' in self.selected_models:
            # Train LSTM
            logger.info("Training LSTM model...")
            lstm_model = self.build_lstm_model(input_shape, is_autoencoder=is_autoencoder)
            
            if self.y_train is not None:
                # Supervised training
                lstm_history = lstm_model.fit(
                    self.X_train, self.y_train,
                    epochs=epochs,
                    batch_size=batch_size,
                    validation_split=0.2,
                    callbacks=callbacks,
                    verbose=1
                )
            else:
                # Unsupervised training (autoencoder approach)
                lstm_history = lstm_model.fit(
                    self.X_train, self.X_train,  # Autoencoder: input = target
                    epochs=epochs,
                    batch_size=batch_size,
                    validation_split=0.2,
                    callbacks=callbacks,
                    verbose=1
                )
            
            histories['lstm'] = lstm_history.history
        
        if 'GRU' in self.selected_models:
            # Train GRU
            logger.info("Training GRU model...")
            gru_model = self.build_gru_model(input_shape, is_autoencoder=is_autoencoder)
            
            if self.y_train is not None:
                # Supervised training
                gru_history = gru_model.fit(
                    self.X_train, self.y_train,
                    epochs=epochs,
                    batch_size=batch_size,
                    validation_split=0.2,
                    callbacks=callbacks,
                    verbose=1
                )
            else:
                # Unsupervised training (autoencoder approach)
                gru_history = gru_model.fit(
                    self.X_train, self.X_train,  # Autoencoder: input = target
                    epochs=epochs,
                    batch_size=batch_size,
                    validation_split=0.2,
                    callbacks=callbacks,
                    verbose=1
                )
            
            histories['gru'] = gru_history.history
        
        # Generate predictions
        if is_autoencoder:
            # For autoencoder: calculate reconstruction error as anomaly score
            if 'LSTM' in self.selected_models:
                lstm_reconstructed = lstm_model.predict(self.X_test)
                # Calculate reconstruction error (MSE per sample)
                lstm_mse = np.mean(np.square(self.X_test - lstm_reconstructed), axis=(1, 2))
                # Convert MSE to probability-like scores (higher error = higher anomaly probability)
                lstm_max_error = np.max(lstm_mse)
                self.lstm_predictions = (lstm_mse / lstm_max_error).reshape(-1, 1)
                # Convert to binary predictions using threshold
                threshold = 0.5
                self.lstm_predictions_binary = (self.lstm_predictions.flatten() > threshold).astype(int)
            
            if 'GRU' in self.selected_models:
                gru_reconstructed = gru_model.predict(self.X_test)
                # Calculate reconstruction error (MSE per sample)
                gru_mse = np.mean(np.square(self.X_test - gru_reconstructed), axis=(1, 2))
                # Convert MSE to probability-like scores (higher error = higher anomaly probability)
                gru_max_error = np.max(gru_mse)
                self.gru_predictions = (gru_mse / gru_max_error).reshape(-1, 1)
                # Convert to binary predictions using threshold
                threshold = 0.5
                self.gru_predictions_binary = (self.gru_predictions.flatten() > threshold).astype(int)
        else:
            # For supervised: use model predictions directly
            if 'LSTM' in self.selected_models:
                self.lstm_predictions = lstm_model.predict(self.X_test)
                # Convert probabilities to binary predictions
                self.lstm_predictions_binary = (self.lstm_predictions > 0.5).astype(int).flatten()
            
            if 'GRU' in self.selected_models:
                self.gru_predictions = gru_model.predict(self.X_test)
                # Convert probabilities to binary predictions
                self.gru_predictions_binary = (self.gru_predictions > 0.5).astype(int).flatten()
        
        logger.info("Model training completed")
        
        return histories
    
    def evaluate_models(self) -> Dict:
        """
        Evaluate models and return performance metrics.
        
        Returns:
            Dictionary of evaluation results
        """
        logger.info("Evaluating models...")
        
        self.results = {}
        
        # Get actual labels for evaluation
        if self.is_supervised and self.label_column in self.data.columns:
            # Get actual labels for the test set - use available predictions to determine test set size
            if self.lstm_predictions is not None:
                test_start_idx = len(self.data) - len(self.lstm_predictions)
            elif self.gru_predictions is not None:
                test_start_idx = len(self.data) - len(self.gru_predictions)
            else:
                logger.error("No model predictions available for evaluation")
                return self.results
            
            actual_labels = self.data[self.label_column].iloc[test_start_idx:].values
            
            logger.info("Evaluating with actual labels...")
            
            # Evaluate LSTM (only if LSTM was trained)
            if 'LSTM' in self.selected_models and self.lstm_predictions is not None:
                lstm_accuracy = accuracy_score(actual_labels, self.lstm_predictions_binary)
                lstm_f1 = f1_score(actual_labels, self.lstm_predictions_binary, average='weighted')
                lstm_precision = precision_score(actual_labels, self.lstm_predictions_binary, average='weighted')
                lstm_recall = recall_score(actual_labels, self.lstm_predictions_binary, average='weighted')
                lstm_roc_auc = roc_auc_score(actual_labels, self.lstm_predictions.flatten())
                lstm_cm = confusion_matrix(actual_labels, self.lstm_predictions_binary)
                
                self.results['LSTM'] = {
                    'accuracy': lstm_accuracy,
                    'f1_score': lstm_f1,
                    'precision': lstm_precision,
                    'recall': lstm_recall,
                    'roc_auc': lstm_roc_auc,
                    'predictions': self.lstm_predictions_binary,
                    'scores': self.lstm_predictions.flatten(),
                    'confusion_matrix': lstm_cm,
                    'actual_labels': actual_labels
                }
            
            # Evaluate GRU (only if GRU was trained)
            if 'GRU' in self.selected_models and self.gru_predictions is not None:
                gru_accuracy = accuracy_score(actual_labels, self.gru_predictions_binary)
                gru_f1 = f1_score(actual_labels, self.gru_predictions_binary, average='weighted')
                gru_precision = precision_score(actual_labels, self.gru_predictions_binary, average='weighted')
                gru_recall = recall_score(actual_labels, self.gru_predictions_binary, average='weighted')
                gru_roc_auc = roc_auc_score(actual_labels, self.gru_predictions.flatten())
                gru_cm = confusion_matrix(actual_labels, self.gru_predictions_binary)
                
                self.results['GRU'] = {
                    'accuracy': gru_accuracy,
                    'f1_score': gru_f1,
                    'precision': gru_precision,
                    'recall': gru_recall,
                    'roc_auc': gru_roc_auc,
                    'predictions': self.gru_predictions_binary,
                    'scores': self.gru_predictions.flatten(),
                    'confusion_matrix': gru_cm,
                    'actual_labels': actual_labels
                }
            
            # Log performance metrics for trained models
            if 'LSTM' in self.results:
                logger.info(f"LSTM - Accuracy: {self.results['LSTM']['accuracy']:.4f}, F1: {self.results['LSTM']['f1_score']:.4f}")
            if 'GRU' in self.results:
                logger.info(f"GRU - Accuracy: {self.results['GRU']['accuracy']:.4f}, F1: {self.results['GRU']['f1_score']:.4f}")
            
        else:
            logger.info("No labels available for evaluation - unsupervised mode")
            # Store basic prediction info without evaluation metrics
            if 'LSTM' in self.selected_models and self.lstm_predictions is not None:
                self.results['LSTM'] = {
                    'predictions': self.lstm_predictions_binary,
                    'scores': self.lstm_predictions.flatten()
                }
            
            if 'GRU' in self.selected_models and self.gru_predictions is not None:
                self.results['GRU'] = {
                    'predictions': self.gru_predictions_binary,
                    'scores': self.gru_predictions.flatten()
                }
        
        return self.results
    
    def create_visualizations(self, save_plots: bool = True) -> None:
        """
        Create comprehensive visualizations for the fraud detection results.
        
        Args:
            save_plots: Whether to save plots as PNG files
        """
        logger.info("Creating visualizations...")
        
        # Set up the plotting style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Create 4-panel visualization
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('LSTM/GRU Fraud Detection Analysis', fontsize=16, fontweight='bold')
        
        # 1. Model Performance Comparison
        self._plot_model_comparison(axes[0, 0])
        
        # 2. Prediction Score Distribution
        self._plot_score_distribution(axes[0, 1])
        
        # 3. Confusion Matrix (if supervised)
        if self.is_supervised and self.results:
            self._plot_confusion_matrices(axes[1, 0])
        else:
            axes[1, 0].text(0.5, 0.5, 'No supervised evaluation\n(Unsupervised mode)', 
                           ha='center', va='center', transform=axes[1, 0].transAxes)
            axes[1, 0].set_title('Confusion Matrices')
        
        # 4. ROC Curves (if supervised)
        if self.is_supervised and self.results:
            self._plot_roc_curves(axes[1, 1])
        else:
            axes[1, 1].text(0.5, 0.5, 'No supervised evaluation\n(Unsupervised mode)', 
                           ha='center', va='center', transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('ROC Curves')
        
        plt.tight_layout()
        
        if save_plots:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plot_path = f"sequence_fraud_detection_analysis_{timestamp}.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            logger.info(f"Plot saved as: {plot_path}")
        
        plt.show()
    
    def _plot_model_comparison(self, ax) -> None:
        """Plot model performance comparison."""
        if not self.results:
            return
        
        models = list(self.results.keys())
        metrics = ['accuracy', 'f1_score', 'precision', 'recall']
        
        x = np.arange(len(metrics))
        width = 0.35 if len(models) > 1 else 0.6
        
        # Plot LSTM if available
        if 'LSTM' in self.results:
            lstm_scores = [self.results['LSTM'][metric] for metric in metrics]
            ax.bar(x - width/2 if len(models) > 1 else x, lstm_scores, width, label='LSTM', alpha=0.8)
            
            # Add value labels on bars
            for i, lstm_val in enumerate(lstm_scores):
                ax.text(i - width/2 if len(models) > 1 else i, lstm_val + 0.01, f'{lstm_val:.3f}', ha='center', va='bottom')
        
        # Plot GRU if available
        if 'GRU' in self.results:
            gru_scores = [self.results['GRU'][metric] for metric in metrics]
            ax.bar(x + width/2 if len(models) > 1 else x, gru_scores, width, label='GRU', alpha=0.8)
            
            # Add value labels on bars
            for i, gru_val in enumerate(gru_scores):
                ax.text(i + width/2 if len(models) > 1 else i, gru_val + 0.01, f'{gru_val:.3f}', ha='center', va='bottom')
        
        ax.set_xlabel('Metrics')
        ax.set_ylabel('Score')
        ax.set_title('Model Performance Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(metrics)
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_score_distribution(self, ax) -> None:
        """Plot prediction score distribution."""
        if self.lstm_predictions is None and self.gru_predictions is None:
            return
        
        # Plot LSTM if available
        if self.lstm_predictions is not None:
            ax.hist(self.lstm_predictions.flatten(), bins=30, alpha=0.7, label='LSTM', color='skyblue')
        
        # Plot GRU if available
        if self.gru_predictions is not None:
            ax.hist(self.gru_predictions.flatten(), bins=30, alpha=0.7, label='GRU', color='lightcoral')
        
        ax.axvline(0.5, color='red', linestyle='--', label='Threshold (0.5)')
        ax.set_xlabel('Prediction Score')
        ax.set_ylabel('Frequency')
        ax.set_title('Prediction Score Distribution')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_confusion_matrices(self, ax) -> None:
        """Plot confusion matrices for both models."""
        if not self.results:
            ax.text(0.5, 0.5, 'No confusion matrix available', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Confusion Matrices')
            return
        
        # Check if we have any confusion matrices
        has_lstm_cm = 'LSTM' in self.results and 'confusion_matrix' in self.results['LSTM']
        has_gru_cm = 'GRU' in self.results and 'confusion_matrix' in self.results['GRU']
        
        if not has_lstm_cm and not has_gru_cm:
            ax.text(0.5, 0.5, 'No confusion matrix available', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Confusion Matrices')
            return
        
        # Determine number of subplots needed
        if has_lstm_cm and has_gru_cm:
            # Both models
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # LSTM Confusion Matrix
            lstm_cm = self.results['LSTM']['confusion_matrix']
            sns.heatmap(lstm_cm, annot=True, fmt='d', cmap='Blues', ax=ax1)
            ax1.set_title('LSTM Confusion Matrix')
            ax1.set_xlabel('Predicted')
            ax1.set_ylabel('Actual')
            
            # GRU Confusion Matrix
            gru_cm = self.results['GRU']['confusion_matrix']
            sns.heatmap(gru_cm, annot=True, fmt='d', cmap='Reds', ax=ax2)
            ax2.set_title('GRU Confusion Matrix')
            ax2.set_xlabel('Predicted')
            ax2.set_ylabel('Actual')
            
            plt.tight_layout()
            plt.show()
        else:
            # Single model
            if has_lstm_cm:
                cm = self.results['LSTM']['confusion_matrix']
                model_name = 'LSTM'
            else:
                cm = self.results['GRU']['confusion_matrix']
                model_name = 'GRU'
            
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax)
            ax.set_title(f'{model_name} Confusion Matrix')
            ax.set_xlabel('Predicted')
            ax.set_ylabel('Actual')
    
    def _plot_roc_curves(self, ax) -> None:
        """Plot ROC curves for both models."""
        if not self.results:
            ax.text(0.5, 0.5, 'No ROC curves available', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title('ROC Curves')
            return
        
        # Check if we have any ROC data
        has_lstm_roc = 'LSTM' in self.results and 'roc_auc' in self.results['LSTM']
        has_gru_roc = 'GRU' in self.results and 'roc_auc' in self.results['GRU']
        
        if not has_lstm_roc and not has_gru_roc:
            ax.text(0.5, 0.5, 'No ROC curves available', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title('ROC Curves')
            return
        
        # Get actual labels from any available model
        if has_lstm_roc:
            actual_labels = self.results['LSTM']['actual_labels']
        else:
            actual_labels = self.results['GRU']['actual_labels']
        
        # LSTM ROC Curve
        if has_lstm_roc:
            lstm_fpr, lstm_tpr, _ = roc_curve(actual_labels, self.results['LSTM']['scores'])
            lstm_auc = self.results['LSTM']['roc_auc']
            ax.plot(lstm_fpr, lstm_tpr, color='blue', lw=2, 
                   label=f'LSTM (AUC = {lstm_auc:.3f})')
        
        # GRU ROC Curve
        if has_gru_roc:
            gru_fpr, gru_tpr, _ = roc_curve(actual_labels, self.results['GRU']['scores'])
            gru_auc = self.results['GRU']['roc_auc']
            ax.plot(gru_fpr, gru_tpr, color='red', lw=2, 
                   label=f'GRU (AUC = {gru_auc:.3f})')
        
        # Random classifier line
        ax.plot([0, 1], [0, 1], color='gray', lw=2, linestyle='--', alpha=0.5)
        
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.set_xlabel('False Positive Rate')
        ax.set_ylabel('True Positive Rate')
        ax.set_title('ROC Curves Comparison')
        ax.legend(loc="lower right")
        ax.grid(True, alpha=0.3)
    
    def export_results(self, output_dir: str = "sequence_fraud_detection_results") -> None:
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
        results_df = self.data.copy()
        
        # Add predictions for the test set
        if self.lstm_predictions is not None or self.gru_predictions is not None:
            # Determine test set size from available predictions
            if self.lstm_predictions is not None:
                test_start_idx = len(self.data) - len(self.lstm_predictions)
            else:
                test_start_idx = len(self.data) - len(self.gru_predictions)
            
            # Create full-length arrays with NaN for training data
            lstm_full_predictions = np.full(len(self.data), np.nan)
            gru_full_predictions = np.full(len(self.data), np.nan)
            lstm_full_scores = np.full(len(self.data), np.nan)
            gru_full_scores = np.full(len(self.data), np.nan)
            
            # Fill test predictions for available models
            if self.lstm_predictions is not None:
                lstm_full_predictions[test_start_idx:] = self.lstm_predictions_binary
                lstm_full_scores[test_start_idx:] = self.lstm_predictions.flatten()
                results_df['lstm_prediction'] = lstm_full_predictions
                results_df['lstm_score'] = lstm_full_scores
                results_df['lstm_risk_score'] = lstm_full_scores
            
            if self.gru_predictions is not None:
                gru_full_predictions[test_start_idx:] = self.gru_predictions_binary
                gru_full_scores[test_start_idx:] = self.gru_predictions.flatten()
                results_df['gru_prediction'] = gru_full_predictions
                results_df['gru_score'] = gru_full_scores
                results_df['gru_risk_score'] = gru_full_scores
        
        filename = f"sequence_fraud_predictions_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)
        results_df.to_csv(filepath, index=False)
        logger.info(f"Results exported to: {filepath}")
        
        # Export evaluation metrics
        if self.results:
            metrics_data = []
            for model_name, metrics in self.results.items():
                metrics_data.append({
                    'model': model_name,
                    'accuracy': metrics['accuracy'],
                    'f1_score': metrics['f1_score'],
                    'precision': metrics['precision'],
                    'recall': metrics['recall'],
                    'roc_auc': metrics.get('roc_auc', None)
                })
            
            metrics_df = pd.DataFrame(metrics_data)
            metrics_file = os.path.join(output_dir, f"sequence_evaluation_metrics_{timestamp}.csv")
            metrics_df.to_csv(metrics_file, index=False)
            logger.info(f"Metrics exported to: {metrics_file}")
        
        # Export configuration
        config = {
            'timestamp': timestamp,
            'data_shape': self.data.shape,
            'processed_shape': self.processed_data.shape if self.processed_data is not None else None,
            'sequence_length': self.sequence_length,
            'is_supervised': self.is_supervised,
            'label_column': self.label_column,
            'primary_keys': self.primary_keys,
            'categorical_columns': self.categorical_columns,
            'numerical_columns': self.numerical_columns,
            'high_cardinality_columns': self.high_cardinality_columns,
            'low_variance_columns': self.low_variance_columns,
            'models_trained': list(self.results.keys()) if self.results else [],
            'selected_models': self.selected_models,
            'epochs': self.epochs,
            'batch_size': self.batch_size,
            'learning_rate': self.learning_rate,
            'dropout_rate': self.dropout_rate,
            'dense_units': self.dense_units,
            'early_stopping_patience': self.early_stopping_patience,
            'reduce_lr_patience': self.reduce_lr_patience,
            'reduce_lr_factor': self.reduce_lr_factor,
            'lstm_units': self.lstm_units,
            'gru_units': self.gru_units
        }
        
        config_file = os.path.join(output_dir, f"sequence_configuration_{timestamp}.json")
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2, default=str)
        logger.info(f"Configuration exported to: {config_file}")
    
    def print_summary(self) -> None:
        """Print comprehensive summary of the fraud detection analysis."""
        print("\n" + "="*80)
        print("📊 SEQUENCE FRAUD DETECTION ANALYSIS SUMMARY")
        print("="*80)
        
        print(f"📈 Dataset: {self.data.shape[0]:,} rows × {self.data.shape[1]} columns")
        print(f"🔧 Processed: {self.processed_data.shape[0]:,} rows × {self.processed_data.shape[1]} columns")
        print(f"📏 Sequence Length: {self.sequence_length}")
        print(f"🎯 Mode: {'Supervised' if self.is_supervised else 'Unsupervised'}")
        
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
        
        print(f"\n🤖 Models Trained: {', '.join(self.selected_models)}")
        
        print(f"\n⚙️  FINE-TUNING PARAMETERS:")
        print(f"   • Epochs: {self.epochs}")
        print(f"   • Batch Size: {self.batch_size}")
        print(f"   • Learning Rate: {self.learning_rate}")
        print(f"   • Dropout Rate: {self.dropout_rate}")
        print(f"   • Dense Units: {self.dense_units}")
        print(f"   • Early Stopping Patience: {self.early_stopping_patience}")
        print(f"   • LR Reduction Patience: {self.reduce_lr_patience}")
        print(f"   • LR Reduction Factor: {self.reduce_lr_factor}")
        
        if 'LSTM' in self.selected_models:
            print(f"   • LSTM Units: {self.lstm_units}")
        
        if 'GRU' in self.selected_models:
            print(f"   • GRU Units: {self.gru_units}")
        
        if self.results:
            print("\n📊 MODEL PERFORMANCE:")
            print("-" * 50)
            for model_name, metrics in self.results.items():
                print(f"{model_name} Model:")
                
                # Check if we have evaluation metrics
                if 'accuracy' in metrics:
                    print(f"  • Accuracy:  {metrics['accuracy']:.4f}")
                    print(f"  • F1-Score:  {metrics['f1_score']:.4f}")
                    print(f"  • Precision: {metrics['precision']:.4f}")
                    print(f"  • Recall:    {metrics['recall']:.4f}")
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
                else:
                    print("  • No evaluation metrics available (unsupervised mode)")
                print()
        
        # Find best model (only if we have evaluation metrics)
        if self.results and 'accuracy' in list(self.results.values())[0]:
            best_model = max(self.results.keys(), 
                           key=lambda k: self.results[k].get('f1_score', 0))
            print(f"🏆 Best Model: {best_model}")
            print(f"   F1-Score: {self.results[best_model]['f1_score']:.4f}")
        
        print("="*80)


def main():
    """
    Main function to run the LSTM/GRU fraud detection system.
    """
    print("🔍 LSTM/GRU FRAUD DETECTION SYSTEM")
    print("=" * 60)
    print("Enterprise Fraud Detection Platform v1.0.0")
    print("=" * 60)
    
    # Initialize the fraud detector
    detector = SequenceFraudDetector(random_state=42, sequence_length=10)
    
    try:
        # Step 1: Load and analyze data
        file_path = input("📁 Enter CSV file path: ").strip()
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        detector.load_and_analyze_data(file_path)
        
        # Step 2: Check data suitability
        if not detector.check_data_suitability():
            proceed = input("\n⚠️  Continue anyway? (y/n): ").lower().strip()
            if proceed not in ['y', 'yes']:
                print("Exiting...")
                return
        
        # Step 3: Setup learning mode
        detector.setup_learning_mode()
        
        # Step 4: Preprocess data
        print("\n🔧 Preprocessing data...")
        detector.preprocess_data()
        
        # Step 5: Prepare sequences
        print("\n📏 Preparing sequences...")
        detector.prepare_sequences()
        
        # Step 6: Split data
        print("\n✂️  Splitting data...")
        detector.split_data()
        
        # Step 7: Train models
        print("\n🤖 Training LSTM and GRU models...")
        detector.train_models()
        
        # Step 8: Evaluate models
        print("\n📊 Evaluating models...")
        detector.evaluate_models()
        
        # Step 9: Create visualizations
        print("\n📈 Creating visualizations...")
        detector.create_visualizations(save_plots=True)
        
        # Step 10: Export results
        print("\n💾 Exporting results...")
        detector.export_results()
        
        # Step 11: Print summary
        detector.print_summary()
        
        print("\n✅ Sequence fraud detection analysis completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        print(f"\n❌ Error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
