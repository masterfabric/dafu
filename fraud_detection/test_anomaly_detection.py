#!/usr/bin/env python3
"""
Test script for Isolation Forest Fraud Detection System

This script demonstrates how to use the fraud detection system
with sample data or your own CSV files.
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.anomaly_detection import IsolationForestFraudDetector


def create_sample_data(n_samples: int = 1000, fraud_ratio: float = 0.1) -> pd.DataFrame:
    """
    Create sample fraud detection data for testing.
    
    Args:
        n_samples: Number of samples to generate
        fraud_ratio: Ratio of fraudulent transactions
        
    Returns:
        Sample DataFrame with fraud labels
    """
    np.random.seed(42)
    
    # Generate normal transactions
    n_normal = int(n_samples * (1 - fraud_ratio))
    n_fraud = n_samples - n_normal
    
    # Normal transaction features
    normal_data = {
        'transaction_id': range(1, n_normal + 1),
        'amount': np.random.normal(100, 30, n_normal),
        'time_of_day': np.random.randint(0, 24, n_normal),
        'day_of_week': np.random.randint(0, 7, n_normal),
        'merchant_category': np.random.choice(['grocery', 'gas', 'restaurant', 'retail'], n_normal),
        'user_age': np.random.randint(18, 80, n_normal),
        'account_balance': np.random.normal(5000, 2000, n_normal),
        'transaction_count_24h': np.random.poisson(3, n_normal),
        'is_fraud': 0
    }
    
    # Fraudulent transaction features (different patterns)
    fraud_data = {
        'transaction_id': range(n_normal + 1, n_samples + 1),
        'amount': np.random.normal(500, 200, n_fraud),  # Higher amounts
        'time_of_day': np.random.choice([2, 3, 4, 5], n_fraud),  # Late night
        'day_of_week': np.random.choice([5, 6], n_fraud),  # Weekends
        'merchant_category': np.random.choice(['online', 'atm', 'foreign'], n_fraud),
        'user_age': np.random.randint(18, 30, n_fraud),  # Younger users
        'account_balance': np.random.normal(1000, 500, n_fraud),  # Lower balance
        'transaction_count_24h': np.random.poisson(10, n_fraud),  # More transactions
        'is_fraud': 1
    }
    
    # Combine data
    normal_df = pd.DataFrame(normal_data)
    fraud_df = pd.DataFrame(fraud_data)
    
    # Combine and shuffle
    combined_df = pd.concat([normal_df, fraud_df], ignore_index=True)
    combined_df = combined_df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    return combined_df


def test_unsupervised_mode():
    """Test the fraud detection system in unsupervised mode."""
    print("🧪 Testing Unsupervised Mode")
    print("=" * 50)
    
    # Create sample data
    data = create_sample_data(n_samples=500, fraud_ratio=0.15)
    
    # Remove the fraud label for unsupervised testing
    test_data = data.drop(columns=['is_fraud'])
    
    # Save to CSV
    test_file = "sample_fraud_data_unsupervised.csv"
    test_data.to_csv(test_file, index=False)
    print(f"📁 Created sample data: {test_file}")
    
    # Initialize detector
    detector = IsolationForestFraudDetector(random_state=42)
    
    try:
        # Load and analyze data
        detector.load_and_analyze_data(test_file)
        
        # Check suitability
        detector.check_data_suitability()
        
        # Set unsupervised mode
        detector.is_supervised = False
        
        # Preprocess data
        detector.preprocess_data()
        
        # Train models
        contamination_levels = [0.05, 0.1, 0.15]
        detector.train_models(contamination_levels)
        
        # Create visualizations
        detector.create_visualizations(save_plots=True)
        
        # Export results
        detector.export_results("unsupervised_test_results")
        
        # Print summary
        detector.print_summary()
        
        print("✅ Unsupervised test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in unsupervised test: {str(e)}")
        raise
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)


def test_supervised_mode():
    """Test the fraud detection system in supervised mode."""
    print("\n🧪 Testing Supervised Mode")
    print("=" * 50)
    
    # Create sample data
    data = create_sample_data(n_samples=1000, fraud_ratio=0.2)
    
    # Save to CSV
    test_file = "sample_fraud_data_supervised.csv"
    data.to_csv(test_file, index=False)
    print(f"📁 Created sample data: {test_file}")
    
    # Initialize detector
    detector = IsolationForestFraudDetector(random_state=42)
    
    try:
        # Load and analyze data
        detector.load_and_analyze_data(test_file)
        
        # Check suitability
        detector.check_data_suitability()
        
        # Set supervised mode
        detector.is_supervised = True
        detector.label_column = 'is_fraud'
        
        # Preprocess data
        detector.preprocess_data()
        
        # Train models
        contamination_levels = [0.05, 0.1, 0.2]
        detector.train_models(contamination_levels)
        
        # Evaluate models
        detector.evaluate_models()
        
        # Create visualizations
        detector.create_visualizations(save_plots=True)
        
        # Export results
        detector.export_results("supervised_test_results")
        
        # Print summary
        detector.print_summary()
        
        print("✅ Supervised test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in supervised test: {str(e)}")
        raise
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)


def main():
    """Run all tests."""
    print("🔍 ISOLATION FOREST FRAUD DETECTION - TEST SUITE")
    print("=" * 60)
    print("Enterprise Fraud Detection Platform v1.0.0")
    print("=" * 60)
    
    try:
        # Test unsupervised mode
        test_unsupervised_mode()
        
        # Test supervised mode
        test_supervised_mode()
        
        print("\n🎉 All tests completed successfully!")
        print("\n📋 Test Results:")
        print("   • Unsupervised mode: ✅")
        print("   • Supervised mode: ✅")
        print("   • Data analysis: ✅")
        print("   • Preprocessing: ✅")
        print("   • Model training: ✅")
        print("   • Evaluation: ✅")
        print("   • Visualization: ✅")
        print("   • Export: ✅")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
