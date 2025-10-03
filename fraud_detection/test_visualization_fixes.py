#!/usr/bin/env python3
"""
Test script to verify visualization fixes for all models.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_isolation_forest_visualization():
    """Test IsolationForest visualization fixes."""
    print("🧪 TESTING ISOLATION FOREST VISUALIZATION FIXES")
    print("="*60)
    
    try:
        from models.anomaly_detection import IsolationForestFraudDetector
        import pandas as pd
        
        detector = IsolationForestFraudDetector(random_state=42)
        
        # Load sample data
        data_path = "sample_fraud_data.csv"
        if not os.path.exists(data_path):
            print(f"❌ Sample data not found: {data_path}")
            return False
        
        detector.load_and_analyze_data(data_path)
        
        # Set up for testing
        detector.is_supervised = True
        detector.label_column = 'fraud_label'
        detector.use_labels_for_training = False
        detector.use_risk_score_threshold = False
        detector.contamination_levels = [0.1]
        
        # Preprocess data
        detector.preprocess_data()
        
        # Train models
        print("🤖 Training models...")
        detector.train_models()
        
        # Test visualization with show_interactive=False
        print("📈 Testing visualization (non-interactive)...")
        detector.create_visualizations(save_plots=True, show_interactive=False)
        
        print("✅ IsolationForest visualization test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ IsolationForest visualization test failed: {e}")
        return False

def test_sequence_models_visualization():
    """Test sequence models visualization fixes."""
    print("\n🧪 TESTING SEQUENCE MODELS VISUALIZATION FIXES")
    print("="*60)
    
    try:
        from models.sequence_models import SequenceFraudDetector
        import pandas as pd
        
        detector = SequenceFraudDetector(random_state=42, sequence_length=5)
        
        # Load sample data
        data_path = "sample_fraud_data.csv"
        if not os.path.exists(data_path):
            print(f"❌ Sample data not found: {data_path}")
            return False
        
        detector.load_and_analyze_data(data_path)
        
        # Set up for testing
        detector.is_supervised = True
        detector.label_column = 'fraud_label'
        detector.use_labels_for_training = False
        detector.selected_models = ['LSTM']  # Test with just LSTM for speed
        detector.epochs = 2  # Very short training for testing
        detector.batch_size = 16
        
        # Preprocess data
        detector.preprocess_data()
        
        # Prepare sequences
        print("📏 Preparing sequences...")
        detector.prepare_sequences()
        
        # Split data
        detector.split_data()
        
        # Train models
        print("🤖 Training LSTM model...")
        detector.train_models()
        
        # Test visualization with show_interactive=False
        print("📈 Testing visualization (non-interactive)...")
        detector.create_visualizations(save_plots=True, show_interactive=False)
        
        print("✅ Sequence models visualization test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Sequence models visualization test failed: {e}")
        return False

def main():
    """Run all visualization tests."""
    print("🔍 TESTING VISUALIZATION FIXES FOR ALL MODELS")
    print("="*60)
    
    # Test IsolationForest
    isolation_success = test_isolation_forest_visualization()
    
    # Test Sequence Models
    sequence_success = test_sequence_models_visualization()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    print(f"IsolationForest Visualization: {'✅ PASS' if isolation_success else '❌ FAIL'}")
    print(f"Sequence Models Visualization: {'✅ PASS' if sequence_success else '❌ FAIL'}")
    
    if isolation_success and sequence_success:
        print("\n🎉 All visualization fixes working correctly!")
        print("\n📝 Fixed Issues:")
        print("   • Added show_interactive parameter to create_visualizations")
        print("   • User can choose whether to show interactive plots")
        print("   • Terminal no longer blocks when interactive plots are disabled")
        print("   • Works for both IsolationForest and Sequence models")
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")

if __name__ == "__main__":
    main()
