#!/usr/bin/env python3
"""
Test script for sequence_models.py with simulated user inputs
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from models.sequence_models import SequenceFraudDetector

def test_sequence_models_interactive():
    """Test sequence models with simulated user inputs"""
    print("🔍 Testing Sequence Models with Simulated Inputs")
    print("=" * 60)
    
    # Create test data
    print("📊 Creating test data...")
    np.random.seed(42)
    
    # Generate synthetic fraud detection data
    n_samples = 1000
    data = {
        'transaction_id': range(1, n_samples + 1),
        'user_id': np.random.randint(1, 100, n_samples),
        'amount': np.random.exponential(100, n_samples),
        'hour_of_day': np.random.randint(0, 24, n_samples),
        'day_of_week': np.random.randint(0, 7, n_samples),
        'location': np.random.choice(['NY', 'LA', 'CH', 'HO', 'DA'], n_samples),
        'device_info': np.random.choice(['mobile', 'desktop', 'tablet'], n_samples),
        'transaction_type': np.random.choice(['online', 'pos'], n_samples),
        'is_new_device': np.random.randint(0, 2, n_samples),
        'is_foreign_ip': np.random.randint(0, 2, n_samples),
        'login_frequency': np.random.rand(n_samples) * 10,
        'time_since_last_transaction': np.random.rand(n_samples) * 1000,
        'distance_from_last_location': np.random.rand(n_samples) * 500,
        'is_fraud': np.random.randint(0, 2, n_samples)  # Label column
    }
    
    test_df = pd.DataFrame(data)
    test_csv_path = "test_sequence_data.csv"
    test_df.to_csv(test_csv_path, index=False)
    print(f"✅ Test data created: {test_csv_path}")
    
    # Test 1: Supervised Learning (Use Labels for Training)
    print("\n" + "="*60)
    print("🔬 TEST 1: Supervised Learning (Use Labels for Training)")
    print("="*60)
    
    detector1 = SequenceFraudDetector(random_state=42, sequence_length=5)
    
    # Load data
    detector1.load_and_analyze_data(test_csv_path)
    
    # Simulate user input for supervised learning
    detector1.is_supervised = True
    detector1.label_column = 'is_fraud'
    detector1.use_labels_for_training = True
    
    print(f"✅ Configuration:")
    print(f"   - Label column: {detector1.label_column}")
    print(f"   - Use labels for training: {detector1.use_labels_for_training}")
    print(f"   - Mode: {'Supervised' if detector1.is_supervised else 'Unsupervised'}")
    
    # Process data
    detector1.preprocess_data()
    detector1.prepare_sequences()
    detector1.split_data()
    
    print("\n🤖 Training models (2 epochs for quick test)...")
    detector1.train_models(epochs=2, batch_size=32)
    
    print("\n📊 Evaluating models...")
    detector1.evaluate_models()
    
    print("\n📋 RESULTS:")
    for model_name, metrics in detector1.results.items():
        print(f"\n{model_name} Model:")
        if 'accuracy' in metrics:
            print(f"  • Accuracy:  {metrics['accuracy']:.4f}")
            print(f"  • F1-Score:  {metrics['f1_score']:.4f}")
            print(f"  • Precision: {metrics['precision']:.4f}")
            print(f"  • Recall:    {metrics['recall']:.4f}")
            print(f"  • ROC-AUC:   {metrics['roc_auc']:.4f}")
            
            if 'confusion_matrix' in metrics:
                cm = metrics['confusion_matrix']
                tn, fp, fn, tp = cm.ravel()
                print(f"\n  📋 CONFUSION MATRIX:")
                print(f"    • True Negative  (TN): {tn:,}")
                print(f"    • False Positive (FP): {fp:,}")
                print(f"    • False Negative (FN): {fn:,}")
                print(f"    • True Positive  (TP): {tp:,}")
        else:
            print("  • No evaluation metrics available")
    
    print("\n✅ Test 1 completed successfully!")
    
    # Test 2: Unsupervised Learning (Remove Labels During Training)
    print("\n" + "="*60)
    print("🔬 TEST 2: Unsupervised Learning (Remove Labels During Training)")
    print("="*60)
    
    detector2 = SequenceFraudDetector(random_state=42, sequence_length=5)
    
    # Load data
    detector2.load_and_analyze_data(test_csv_path)
    
    # Simulate user input for unsupervised learning on supervised data
    detector2.is_supervised = True
    detector2.label_column = 'is_fraud'
    detector2.use_labels_for_training = False  # Key difference
    
    print(f"✅ Configuration:")
    print(f"   - Label column: {detector2.label_column}")
    print(f"   - Use labels for training: {detector2.use_labels_for_training}")
    print(f"   - Mode: {'Supervised' if detector2.is_supervised else 'Unsupervised'}")
    print(f"   - (Labels will be removed during training but used for evaluation)")
    
    # Process data
    detector2.preprocess_data()
    detector2.prepare_sequences()
    detector2.split_data()
    
    print("\n🤖 Training models (2 epochs for quick test)...")
    detector2.train_models(epochs=2, batch_size=32)
    
    print("\n📊 Evaluating models...")
    detector2.evaluate_models()
    
    print("\n📋 RESULTS:")
    for model_name, metrics in detector2.results.items():
        print(f"\n{model_name} Model:")
        if 'accuracy' in metrics:
            print(f"  • Accuracy:  {metrics['accuracy']:.4f}")
            print(f"  • F1-Score:  {metrics['f1_score']:.4f}")
            print(f"  • Precision: {metrics['precision']:.4f}")
            print(f"  • Recall:    {metrics['recall']:.4f}")
            print(f"  • ROC-AUC:   {metrics['roc_auc']:.4f}")
            
            if 'confusion_matrix' in metrics:
                cm = metrics['confusion_matrix']
                tn, fp, fn, tp = cm.ravel()
                print(f"\n  📋 CONFUSION MATRIX:")
                print(f"    • True Negative  (TN): {tn:,}")
                print(f"    • False Positive (FP): {fp:,}")
                print(f"    • False Negative (FN): {fn:,}")
                print(f"    • True Positive  (TP): {tp:,}")
        else:
            print("  • No evaluation metrics available")
    
    print("\n✅ Test 2 completed successfully!")
    
    # Clean up
    os.remove(test_csv_path)
    print(f"\n🧹 Cleaned up {test_csv_path}")
    
    print("\n🎉 All tests completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    test_sequence_models_interactive()
