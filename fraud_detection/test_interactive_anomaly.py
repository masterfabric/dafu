#!/usr/bin/env python3
"""
Interactive test for anomaly_detection.py to simulate real user interaction
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'models'))

from anomaly_detection import IsolationForestFraudDetector

def test_interactive_anomaly():
    """Test with simulated user inputs"""
    
    print("🔍 Interactive Test for Anomaly Detection")
    print("=" * 50)
    
    # Initialize detector
    detector = IsolationForestFraudDetector(random_state=42)
    
    # Simulate user inputs
    print("📁 Loading sample data...")
    detector.load_and_analyze_data("sample_fraud_data.csv")
    
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
    
    # Test visualization with interactive choice
    print("\n📈 Testing visualization with user choice...")
    print("This should ask: 'Show interactive plots? (y/n - default: n)'")
    
    # Simulate user choosing 'n' (no interactive)
    print("Simulating user choice: 'n'")
    show_plots = 'n'
    show_interactive = show_plots in ['y', 'yes']
    
    print(f"show_interactive = {show_interactive}")
    
    try:
        detector.create_visualizations(save_plots=True, show_interactive=show_interactive)
        print("✅ Visualization completed without blocking!")
    except Exception as e:
        print(f"❌ Visualization failed: {e}")
        return False
    
    # Test model saving
    print("\n💾 Testing model saving...")
    print("This should ask: 'Save trained model for future use? (y/n)'")
    
    # Simulate user choosing 'y' and entering model name
    print("Simulating user choice: 'y' and model name 'test_model'")
    save_model = 'y'
    
    if save_model in ['y', 'yes']:
        model_name = 'test_model'
        print(f"Model name: '{model_name}'")
        
        try:
            saved_path = detector.save_model(model_name)
            print(f"✅ Model saved successfully as: {saved_path}")
            
            # Clean up
            if os.path.exists(saved_path):
                os.remove(saved_path)
                print(f"🧹 Cleaned up: {saved_path}")
                
        except Exception as e:
            print(f"❌ Model saving failed: {e}")
            return False
    
    print("\n✅ Interactive test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_interactive_anomaly()
    if success:
        print("\n🎉 Interactive test passed!")
    else:
        print("\n❌ Interactive test failed!")
        sys.exit(1)
