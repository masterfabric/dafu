#!/usr/bin/env python3
"""
Test script to verify the final fix - visualization comes last
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'models'))

from anomaly_detection import IsolationForestFraudDetector
from sequence_models import SequenceFraudDetector

def test_anomaly_detection_final():
    """Test anomaly detection with visualization at the end"""
    
    print("🔍 Testing Anomaly Detection - Final Fix")
    print("=" * 50)
    
    # Initialize detector
    detector = IsolationForestFraudDetector(random_state=42)
    
    # Load sample data
    print("📁 Loading sample data...")
    detector.load_and_analyze_data("sample_fraud_data.csv")
    
    # Setup for batch mode
    detector.prediction_mode = 'batch'
    detector.is_supervised = True
    detector.label_column = 'fraud_label'
    detector.detection_method = 'classic'
    detector.contamination_levels = [0.1]
    detector.n_estimators = 100
    detector.max_samples = 'auto'
    detector.max_features = 1.0
    detector.bootstrap = False
    
    # Preprocess
    print("🔧 Preprocessing data...")
    detector.preprocess_data()
    
    # Train
    print("🤖 Training model...")
    detector.train_models()
    
    # Evaluate
    print("📊 Evaluating model...")
    detector.evaluate_models()
    
    # Export results
    print("💾 Exporting results...")
    detector.export_results()
    
    # Test model saving (should work now)
    print("💾 Testing model saving...")
    try:
        saved_path = detector.save_model("test_anomaly_final")
        print(f"✅ Model saved as: {saved_path}")
        
        # Clean up
        if os.path.exists(saved_path):
            os.remove(saved_path)
            print(f"🧹 Cleaned up: {saved_path}")
        
        print("✅ Model saving works correctly!")
        
    except Exception as e:
        print(f"❌ Model saving failed: {e}")
        return False
    
    # Print summary
    print("📊 Printing summary...")
    detector.print_summary()
    
    # Test visualization (should be last)
    print("\n📈 Testing visualization (should be last step)...")
    try:
        detector.create_visualizations(save_plots=True, show_interactive=False)
        print("✅ Visualization works correctly!")
        
    except Exception as e:
        print(f"❌ Visualization failed: {e}")
        return False
    
    print("✅ Anomaly Detection final fix working correctly!")
    return True

def test_sequence_models_final():
    """Test sequence models with visualization at the end"""
    
    print("\n🔍 Testing Sequence Models - Final Fix")
    print("=" * 50)
    
    # Initialize detector
    detector = SequenceFraudDetector(random_state=42, sequence_length=10)
    
    # Load sample data
    print("📁 Loading sample data...")
    detector.load_and_analyze_data("sample_fraud_data.csv")
    
    # Setup for batch mode
    detector.prediction_mode = 'batch'
    detector.is_supervised = True
    detector.label_column = 'fraud_label'
    detector.use_labels_for_training = True
    detector.selected_models = ['LSTM', 'GRU']
    
    # Setup parameters (quick test)
    detector.epochs = 2
    detector.batch_size = 32
    detector.learning_rate = 0.001
    detector.dropout_rate = 0.2
    detector.dense_units = 16
    detector.early_stopping_patience = 5
    detector.reduce_lr_patience = 3
    detector.reduce_lr_factor = 0.5
    detector.lstm_units = [32, 16]
    detector.gru_units = [32, 16]
    
    # Preprocess
    print("🔧 Preprocessing data...")
    detector.preprocess_data()
    
    # Prepare sequences
    print("📏 Preparing sequences...")
    detector.prepare_sequences()
    
    # Split data
    print("✂️ Splitting data...")
    detector.split_data()
    
    # Train models
    print("🤖 Training models...")
    detector.train_models(epochs=2, batch_size=32)
    
    # Evaluate
    print("📊 Evaluating models...")
    detector.evaluate_models()
    
    # Export results
    print("💾 Exporting results...")
    detector.export_results()
    
    # Test model saving (should work now)
    print("💾 Testing model saving...")
    try:
        saved_path = detector.save_model("test_sequence_final")
        print(f"✅ Model saved as: {saved_path}")
        
        # Clean up
        if os.path.exists(saved_path):
            os.remove(saved_path)
            print(f"🧹 Cleaned up: {saved_path}")
        
        # Clean up .h5 files
        import glob
        h5_files = glob.glob("lstm_model_*.h5") + glob.glob("gru_model_*.h5")
        for h5_file in h5_files:
            if os.path.exists(h5_file):
                os.remove(h5_file)
                print(f"🧹 Cleaned up: {h5_file}")
        
        print("✅ Model saving works correctly!")
        
    except Exception as e:
        print(f"❌ Model saving failed: {e}")
        return False
    
    # Print summary
    print("📊 Printing summary...")
    detector.print_summary()
    
    # Test visualization (should be last)
    print("\n📈 Testing visualization (should be last step)...")
    try:
        detector.create_visualizations(save_plots=True, show_interactive=False)
        print("✅ Visualization works correctly!")
        
    except Exception as e:
        print(f"❌ Visualization failed: {e}")
        return False
    
    print("✅ Sequence Models final fix working correctly!")
    return True

if __name__ == "__main__":
    print("🧪 Testing Final Fix - Visualization at the End")
    print("=" * 60)
    
    # Test anomaly detection
    anomaly_success = test_anomaly_detection_final()
    
    # Test sequence models
    sequence_success = test_sequence_models_final()
    
    print("\n" + "=" * 60)
    print("🎯 FINAL TEST RESULTS")
    print("=" * 60)
    
    if anomaly_success and sequence_success:
        print("✅ ALL TESTS PASSED!")
        print("✅ Model saving works before visualization")
        print("✅ Visualization comes last")
        print("✅ Program flow is correct")
        print("\n🎉 Final fix is working correctly!")
    else:
        print("❌ SOME TESTS FAILED!")
        if not anomaly_success:
            print("❌ Anomaly Detection test failed")
        if not sequence_success:
            print("❌ Sequence Models test failed")
        sys.exit(1)
