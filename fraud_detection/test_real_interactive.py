#!/usr/bin/env python3
"""
Real interactive test - simulates exactly what user does
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'models'))

from anomaly_detection import IsolationForestFraudDetector

def test_real_interactive():
    """Test exactly like user would"""
    
    print("🔍 REAL Interactive Test for Anomaly Detection")
    print("=" * 60)
    
    # Initialize detector
    detector = IsolationForestFraudDetector(random_state=42)
    
    # Simulate user inputs step by step
    print("Step 1: Setup prediction mode")
    detector.prediction_mode = 'batch'  # User would choose 1
    
    print("Step 2: Load data")
    detector.load_and_analyze_data("sample_fraud_data.csv")
    
    print("Step 3: Check data suitability")
    if not detector.check_data_suitability():
        print("Data suitability check failed, but continuing...")
    
    print("Step 4: Setup learning mode")
    detector.is_supervised = True
    detector.label_column = 'fraud_label'
    detector.use_labels_for_training = True
    
    print("Step 5: Setup fine-tuning parameters")
    detector.detection_method = 'classic'
    detector.contamination_levels = [0.1]
    detector.n_estimators = 100
    detector.max_samples = 'auto'
    detector.max_features = 1.0
    detector.bootstrap = False
    detector.use_risk_score_threshold = False
    
    print("Step 6: Preprocess data")
    detector.preprocess_data()
    
    print("Step 7: Train models")
    detector.train_models()
    
    print("Step 8: Evaluate models")
    detector.evaluate_models()
    
    print("Step 9: Create visualizations")
    print("Simulating user choice: 'n' for no interactive plots")
    show_interactive = False
    
    try:
        detector.create_visualizations(save_plots=True, show_interactive=show_interactive)
        print("✅ Visualization completed successfully!")
    except Exception as e:
        print(f"❌ Visualization failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("Step 10: Export results")
    detector.export_results()
    
    print("Step 11: Model saving")
    print("Simulating user choice: 'y' and model name 'test_model'")
    model_name = 'test_model'
    
    try:
        saved_path = detector.save_model(model_name)
        print(f"✅ Model saved successfully as: {saved_path}")
        
        # Clean up
        if os.path.exists(saved_path):
            os.remove(saved_path)
            print(f"🧹 Cleaned up: {saved_path}")
            
    except Exception as e:
        print(f"❌ Model saving failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("Step 12: Print summary")
    detector.print_summary()
    
    print("\n✅ Real interactive test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_real_interactive()
    if success:
        print("\n🎉 Real interactive test passed!")
    else:
        print("\n❌ Real interactive test failed!")
        sys.exit(1)
