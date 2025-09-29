# Isolation Forest Fraud Detection - Model Persistence & Stream Prediction

## Overview

The enhanced Isolation Forest fraud detection system now supports two prediction modes:

1. **Batch Prediction Mode**: Train models on batch data and predict on the same data
2. **Stream Prediction Mode**: Load pre-trained models and make predictions on new stream data

## New Features

### 🔄 Batch Prediction Mode
- Train models on historical data
- Evaluate model performance
- Save trained models for future use
- Generate comprehensive reports and visualizations

### 🌊 Stream Prediction Mode
- Load pre-trained models
- Process new data in real-time
- Apply same preprocessing as training data
- Export stream prediction results

### 💾 Model Persistence
- Save complete model packages using joblib
- Include all preprocessing objects (scalers, encoders)
- Preserve model configuration and metadata
- Cross-platform compatibility

## Usage

### Interactive Mode

Run the main script for interactive mode:

```bash
python src/models/anomaly_detection.py
```

The system will ask you to choose between:
1. **Batch Prediction** - Train and evaluate models
2. **Stream Prediction** - Use pre-trained models

### Programmatic Usage

#### Batch Prediction Example

```python
from src.models.anomaly_detection import IsolationForestFraudDetector

# Initialize detector
detector = IsolationForestFraudDetector(random_state=42)

# Load and analyze data
detector.load_and_analyze_data('training_data.csv')

# Setup for batch prediction
detector.prediction_mode = 'batch'
detector.is_supervised = True
detector.label_column = 'fraud_label'

# Preprocess and train
detector.preprocess_data()
detector.train_models()
detector.evaluate_models()

# Save model
model_path = detector.save_model('my_fraud_model.joblib')
```

#### Stream Prediction Example

```python
# Initialize new detector
detector = IsolationForestFraudDetector(random_state=42)

# Load pre-trained model
detector.load_model('my_fraud_model.joblib')

# Load stream data
stream_data = pd.read_csv('new_data.csv')

# Make predictions
results = detector.predict_stream(stream_data)

# Export results
detector.export_stream_results(stream_data, results)
```

## Model Package Contents

When you save a model, it includes:

- **Trained Models**: All Isolation Forest models with different contamination levels
- **Preprocessing Objects**: StandardScaler and LabelEncoders
- **Configuration**: All model parameters and settings
- **Metadata**: Training timestamp, version, algorithm info
- **Column Information**: Feature types and preprocessing rules

## File Structure

```
fraud_detection/
├── src/models/
│   └── anomaly_detection.py          # Main fraud detection class
├── example_usage.py                  # Usage examples
├── MODEL_PERSISTENCE_README.md       # This file
└── fraud_detection_results/          # Batch prediction results
    ├── fraud_predictions_*.csv
    ├── evaluation_metrics_*.csv
    └── configuration_*.json
└── stream_prediction_results/        # Stream prediction results
    ├── stream_predictions_*.csv
    └── stream_summary_*.json
```

## Key Methods

### Batch Prediction Methods
- `load_and_analyze_data()` - Load and analyze training data
- `setup_learning_mode()` - Configure supervised/unsupervised learning
- `preprocess_data()` - Preprocess training data
- `train_models()` - Train Isolation Forest models
- `evaluate_models()` - Evaluate model performance
- `save_model()` - Save trained model package

### Stream Prediction Methods
- `load_model()` - Load pre-trained model
- `preprocess_stream_data()` - Preprocess new data using saved transformers
- `predict_stream()` - Make predictions on stream data
- `export_stream_results()` - Export stream prediction results

## Configuration Options

### Model Parameters
- `contamination_levels`: List of contamination levels to test
- `n_estimators`: Number of trees in the ensemble
- `max_samples`: Number of samples per tree
- `max_features`: Number of features per tree
- `bootstrap`: Whether to use bootstrap sampling

### Detection Methods
- **Classic**: Use Isolation Forest's built-in anomaly detection
- **Risk Score**: Use custom risk score threshold

### Learning Modes
- **Supervised**: Use labels for training and evaluation
- **Unsupervised**: Remove labels during training, compare later

## Error Handling

The system includes comprehensive error handling for:
- Missing model files
- Incompatible data formats
- Unknown categorical values in stream data
- Missing required columns
- Invalid model parameters

## Performance Considerations

### Batch Mode
- Suitable for historical data analysis
- Full model evaluation and visualization
- Model training and hyperparameter tuning

### Stream Mode
- Optimized for real-time prediction
- Minimal preprocessing overhead
- Fast model loading and prediction

## Example Workflow

1. **Training Phase (Batch Mode)**:
   ```bash
   python src/models/anomaly_detection.py
   # Choose: 1 (Batch Prediction)
   # Provide: training_data.csv
   # Configure: learning mode, parameters
   # Save: trained model
   ```

2. **Prediction Phase (Stream Mode)**:
   ```bash
   python src/models/anomaly_detection.py
   # Choose: 2 (Stream Prediction)
   # Provide: saved_model.joblib
   # Provide: stream_data.csv
   # Get: predictions and results
   ```

## Dependencies

- pandas
- numpy
- scikit-learn
- matplotlib
- seaborn
- joblib

## Notes

- Models are saved in joblib format for cross-platform compatibility
- Stream data must have compatible column structure with training data
- Unknown categorical values in stream data are handled gracefully
- All preprocessing steps are automatically applied to stream data
- Model metadata includes training timestamp and configuration details
