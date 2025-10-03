#!/usr/bin/env python3
"""
Test script for sequence_models.py fixes
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'models'))

from sequence_models import SequenceFraudDetector
import pandas as pd

def test_sequence_models_fixes():
    """Test the visualization and model saving fixes"""
    
    print("🔍 Testing Sequence Models Fixes")
    print("=" * 50)
    
    # Initialize detector
    detector = SequenceFraudDetector(random_state=42, sequence_length=10)
    
    # Load sample data
    print("📁 Loading sample data...")
    sample_file = "sample_fraud_data.csv"
    if not os.path.exists(sample_file):
        print(f"❌ Sample file not found: {sample_file}")
        return False
    
    detector.load_and_analyze_data(sample_file)
    
    # Setup for batch mode
    detector.prediction_mode = 'batch'
    detector.is_supervised = True
    detector.label_column = 'fraud_label'
    detector.use_labels_for_training = True
    detector.selected_models = ['LSTM', 'GRU']
    
    # Setup parameters
    detector.epochs = 2  # Quick test
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
    
    # Train models (quick test with 2 epochs)
    print("🤖 Training models (quick test)...")
    detector.train_models(epochs=2, batch_size=32)
    
    # Evaluate
    print("📊 Evaluating models...")
    detector.evaluate_models()
    
    # Test visualization fix - NO interactive display
    print("\n📈 Testing visualization fix (no interactive display)...")
    try:
        detector.create_visualizations(save_plots=True, show_interactive=False)
        print("✅ Visualization fix working - no blocking!")
    except Exception as e:
        print(f"❌ Visualization fix failed: {e}")
        return False
    
    # Test model saving fix
    print("\n💾 Testing model saving fix...")
    try:
        # Test with just name (should add .joblib)
        saved_path = detector.save_model("test_lstm_model")
        print(f"✅ Model saved as: {saved_path}")
        assert saved_path == "test_lstm_model.joblib", f"Expected 'test_lstm_model.joblib', got '{saved_path}'"
        
        # Test with extension (should use as-is)
        saved_path2 = detector.save_model("test_gru_model.pkl")
        print(f"✅ Model saved as: {saved_path2}")
        assert saved_path2 == "test_gru_model.pkl", f"Expected 'test_gru_model.pkl', got '{saved_path2}'"
        
        # Clean up
        for path in [saved_path, saved_path2]:
            if os.path.exists(path):
                os.remove(path)
                print(f"🧹 Cleaned up: {path}")
        
        # Clean up .h5 files too
        import glob
        h5_files = glob.glob("lstm_model_*.h5") + glob.glob("gru_model_*.h5")
        for h5_file in h5_files:
            if os.path.exists(h5_file):
                os.remove(h5_file)
                print(f"🧹 Cleaned up: {h5_file}")
        
        print("✅ Model saving fix working!")
        
    except Exception as e:
        print(f"❌ Model saving fix failed: {e}")
        return False
    
    print("\n✅ All sequence models fixes working correctly!")
    return True

if __name__ == "__main__":
    success = test_sequence_models_fixes()
    if success:
        print("\n🎉 Sequence Models fixes verified successfully!")
    else:
        print("\n❌ Sequence Models fixes failed!")
        sys.exit(1)
