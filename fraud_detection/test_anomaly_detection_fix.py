#!/usr/bin/env python3
"""
Test script for anomaly_detection.py fixes
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'models'))

from anomaly_detection import IsolationForestFraudDetector
import pandas as pd

def test_anomaly_detection_fixes():
    """Test the visualization and model saving fixes"""
    
    print("🔍 Testing Anomaly Detection Fixes")
    print("=" * 50)
    
    # Initialize detector
    detector = IsolationForestFraudDetector(random_state=42)
    
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
    
    # Setup method (Classic)
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
        saved_path = detector.save_model("test_model")
        print(f"✅ Model saved as: {saved_path}")
        assert saved_path == "test_model.joblib", f"Expected 'test_model.joblib', got '{saved_path}'"
        
        # Test with extension (should use as-is)
        saved_path2 = detector.save_model("test_model2.pkl")
        print(f"✅ Model saved as: {saved_path2}")
        assert saved_path2 == "test_model2.pkl", f"Expected 'test_model2.pkl', got '{saved_path2}'"
        
        # Clean up
        for path in [saved_path, saved_path2]:
            if os.path.exists(path):
                os.remove(path)
                print(f"🧹 Cleaned up: {path}")
        
        print("✅ Model saving fix working!")
        
    except Exception as e:
        print(f"❌ Model saving fix failed: {e}")
        return False
    
    print("\n✅ All anomaly detection fixes working correctly!")
    return True

if __name__ == "__main__":
    success = test_anomaly_detection_fixes()
    if success:
        print("\n🎉 Anomaly Detection fixes verified successfully!")
    else:
        print("\n❌ Anomaly Detection fixes failed!")
        sys.exit(1)
