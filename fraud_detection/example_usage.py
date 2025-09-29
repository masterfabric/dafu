#!/usr/bin/env python3
"""
Example usage of the enhanced Isolation Forest Fraud Detection System

This script demonstrates how to use both batch prediction and stream prediction modes.
"""

import pandas as pd
import numpy as np
from src.models.anomaly_detection import IsolationForestFraudDetector

def create_sample_data(n_samples=1000, n_features=10, fraud_rate=0.1):
    """Create sample fraud detection data for demonstration."""
    np.random.seed(42)
    
    # Generate normal data
    normal_data = np.random.normal(0, 1, (int(n_samples * (1 - fraud_rate)), n_features))
    normal_labels = np.zeros(int(n_samples * (1 - fraud_rate)))
    
    # Generate fraud data (with different distribution)
    fraud_data = np.random.normal(3, 1.5, (int(n_samples * fraud_rate), n_features))
    fraud_labels = np.ones(int(n_samples * fraud_rate))
    
    # Combine data
    X = np.vstack([normal_data, fraud_data])
    y = np.hstack([normal_labels, fraud_labels])
    
    # Create DataFrame
    feature_names = [f'feature_{i}' for i in range(n_features)]
    df = pd.DataFrame(X, columns=feature_names)
    df['fraud_label'] = y.astype(int)
    
    return df

def example_batch_prediction():
    """Example of batch prediction mode."""
    print("="*60)
    print("EXAMPLE: BATCH PREDICTION MODE")
    print("="*60)
    
    # Create sample data
    data = create_sample_data(n_samples=1000, fraud_rate=0.1)
    data.to_csv('sample_fraud_data.csv', index=False)
    print("✅ Sample data created: sample_fraud_data.csv")
    
    # Initialize detector
    detector = IsolationForestFraudDetector(random_state=42)
    
    # Load and analyze data
    detector.load_and_analyze_data('sample_fraud_data.csv')
    
    # Setup for batch prediction
    detector.prediction_mode = 'batch'
    detector.is_supervised = True
    detector.label_column = 'fraud_label'
    detector.use_labels_for_training = False  # Unsupervised learning
    detector.use_risk_score_threshold = False  # Classic method
    
    # Preprocess data
    detector.preprocess_data()
    
    # Train models
    detector.train_models()
    
    # Evaluate models
    detector.evaluate_models()
    
    # Save model
    model_path = detector.save_model('fraud_detection_model.joblib')
    print(f"✅ Model saved to: {model_path}")
    
    # Print summary
    detector.print_summary()
    
    return model_path

def example_stream_prediction(model_path):
    """Example of stream prediction mode."""
    print("\n" + "="*60)
    print("EXAMPLE: STREAM PREDICTION MODE")
    print("="*60)
    
    # Create new stream data
    stream_data = create_sample_data(n_samples=200, fraud_rate=0.15)
    stream_data.to_csv('stream_data.csv', index=False)
    print("✅ Stream data created: stream_data.csv")
    
    # Initialize new detector for stream prediction
    detector = IsolationForestFraudDetector(random_state=42)
    
    # Load pre-trained model
    detector.load_model(model_path)
    
    # Make predictions on stream data
    results = detector.predict_stream(stream_data)
    
    # Display results
    print(f"\n📊 STREAM PREDICTION RESULTS:")
    print(f"Total Records: {len(results['binary_predictions']):,}")
    print(f"Anomalies Detected: {results['binary_predictions'].sum():,}")
    print(f"Anomaly Rate: {results['binary_predictions'].mean():.2%}")
    print(f"Contamination Used: {results['contamination']}")
    
    # Export results
    detector.export_stream_results(stream_data, results, 'stream_results')
    print("✅ Stream results exported to: stream_results/")
    
    return results

def main():
    """Main example function."""
    print("🔍 ISOLATION FOREST FRAUD DETECTION - EXAMPLE USAGE")
    print("=" * 60)
    
    try:
        # Example 1: Batch prediction
        model_path = example_batch_prediction()
        
        # Example 2: Stream prediction
        results = example_stream_prediction(model_path)
        
        print("\n✅ All examples completed successfully!")
        print("\nFiles created:")
        print("  • sample_fraud_data.csv - Training data")
        print("  • stream_data.csv - Stream data")
        print("  • fraud_detection_model.joblib - Trained model")
        print("  • stream_results/ - Stream prediction results")
        
    except Exception as e:
        print(f"❌ Error in example: {str(e)}")
        raise

if __name__ == "__main__":
    main()
