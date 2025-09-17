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
        
        while True:
            mode = input("Is your data supervised? (y/n): ").lower().strip()
            if mode in ['y', 'yes']:
                self.is_supervised = True
                break
            elif mode in ['n', 'no']:
                self.is_supervised = False
                break
            else:
                print("Please enter 'y' for yes or 'n' for no.")
        
        if self.is_supervised:
            self._setup_supervised_mode()
        else:
            print("🔍 Unsupervised mode selected - no ground truth labels available.")
    
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
            print("   Isolation Forest is typically used for binary anomaly detection.")
    
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
        
        # Remove high cardinality columns
        if self.high_cardinality_columns:
            logger.info(f"Removing high cardinality columns: {self.high_cardinality_columns}")
            self.processed_data = self.processed_data.drop(columns=self.high_cardinality_columns)
        
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
            contamination_levels: List of contamination levels to test
            
        Returns:
            Dictionary of trained models
        """
        if contamination_levels is None:
            contamination_levels = [0.01, 0.05, 0.1]
        
        logger.info(f"Training Isolation Forest models with contamination levels: {contamination_levels}")
        
        # Prepare features (exclude label if supervised)
        if self.is_supervised and self.label_column in self.processed_data.columns:
            X = self.processed_data.drop(columns=[self.label_column])
            y = self.processed_data[self.label_column]
        else:
            X = self.processed_data
            y = None
        
        self.models = {}
        
        for contamination in contamination_levels:
            logger.info(f"Training model with contamination: {contamination}")
            
            model = IsolationForest(
                contamination=contamination,
                random_state=self.random_state,
                n_estimators=100,
                max_samples='auto',
                max_features=1.0,
                bootstrap=False,
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
    
    def evaluate_models(self) -> Dict:
        """
        Evaluate models and return performance metrics.
        
        Returns:
            Dictionary of evaluation results
        """
        if not self.is_supervised:
            logger.info("Unsupervised mode - skipping supervised evaluation")
            return {}
        
        logger.info("Evaluating models with supervised metrics...")
        
        y_true = self.processed_data[self.label_column]
        self.results = {}
        
        for contamination, model in self.models.items():
            predictions = self.predictions[contamination]
            scores = self.anomaly_scores[contamination]
            
            # Convert predictions to binary (0: normal, 1: anomaly)
            binary_predictions = (predictions == -1).astype(int)
            
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
        
        plt.show()
    
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
            results_df['is_fraud'] = (predictions == -1).astype(int)
            
            # Add risk score (normalized anomaly score)
            scores = self.anomaly_scores[contamination]
            min_score, max_score = scores.min(), scores.max()
            results_df['risk_score'] = (scores - min_score) / (max_score - min_score)
            
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
            'label_column': self.label_column,
            'primary_keys': self.primary_keys,
            'categorical_columns': self.categorical_columns,
            'numerical_columns': self.numerical_columns,
            'high_cardinality_columns': self.high_cardinality_columns,
            'low_variance_columns': self.low_variance_columns,
            'contamination_levels': list(self.models.keys())
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
        
        print(f"\n🤖 Models Trained: {len(self.models)} contamination levels")
        
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
        
        # Step 5: Train models
        print("\n🤖 Training Isolation Forest models...")
        contamination_levels = [0.01, 0.05, 0.1]
        detector.train_models(contamination_levels)
        
        # Step 6: Evaluate models (if supervised)
        if detector.is_supervised:
            print("\n📊 Evaluating models...")
            detector.evaluate_models()
        
        # Step 7: Create visualizations
        print("\n📈 Creating visualizations...")
        detector.create_visualizations(save_plots=True)
        
        # Step 8: Export results
        print("\n💾 Exporting results...")
        detector.export_results()
        
        # Step 9: Print summary
        detector.print_summary()
        
        print("\n✅ Fraud detection analysis completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        print(f"\n❌ Error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
