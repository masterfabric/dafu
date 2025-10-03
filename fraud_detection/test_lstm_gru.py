#!/usr/bin/env python3
"""
Test script for LSTM/GRU sequence models
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'models'))

from sequence_models import SequenceFraudDetector

def test_lstm_gru():
    """Test LSTM/GRU sequence models"""
    
    print("🔍 Testing LSTM/GRU Sequence Models")
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
    
    # Test visualization fix
    print("\n📈 Testing visualization fix...")
    try:
        detector.create_visualizations(save_plots=True, show_interactive=False)
        print("✅ LSTM/GRU visualization fix working - no blocking!")
    except Exception as e:
        print(f"❌ LSTM/GRU visualization fix failed: {e}")
        return False
    
    # Test model saving fix
    print("\n💾 Testing model saving fix...")
    try:
        saved_path = detector.save_model("test_lstm_gru")
        print(f"✅ LSTM/GRU model saved as: {saved_path}")
        
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
        
        print("✅ LSTM/GRU model saving fix working!")
        
    except Exception as e:
        print(f"❌ LSTM/GRU model saving fix failed: {e}")
        return False
    
    print("\n✅ LSTM/GRU sequence models fixes working correctly!")
    return True

if __name__ == "__main__":
    success = test_lstm_gru()
    if success:
        print("\n🎉 LSTM/GRU fixes verified successfully!")
    else:
        print("\n❌ LSTM/GRU fixes failed!")
        sys.exit(1)
