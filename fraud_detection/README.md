# Fraud Detection Service

A comprehensive Isolation Forest-based fraud detection system designed for enterprise-scale fraud detection and e-commerce analytics.

## 🚀 Features

### Core Capabilities
- **Automatic Data Analysis**: Intelligent column detection and data suitability assessment
- **Dual Learning Modes**: Support for both supervised and unsupervised learning
- **Dual Detection Methods**: Classic Isolation Forest predictions or Risk Score-based threshold detection
- **Advanced Preprocessing**: Automatic handling of missing values, categorical encoding, and feature standardization
- **Multi-Model Training**: Train multiple models with different contamination levels
- **Comprehensive Evaluation**: Detailed performance metrics and statistical analysis
- **Rich Visualizations**: 4-panel analysis with feature importance, score distributions, confusion matrices, and ROC curves
- **Production Ready**: Enterprise-grade logging, error handling, and result export

### Enterprise Features
- **Stateless Architecture**: Designed for microservices deployment
- **Scalable Processing**: Handles large datasets efficiently
- **Comprehensive Logging**: Structured logging with configurable levels
- **Result Export**: Multiple output formats (CSV, JSON) with timestamps
- **Risk Scoring**: Normalized risk scores for business decision making
- **Flexible Thresholding**: Custom risk score thresholds for fine-tuned anomaly detection

## 📁 Project Structure

```
fraud_detection/
├── src/
│   ├── models/
│   │   ├── anomaly_detection.py      # Main Isolation Forest implementation
│   │   ├── sequence_models.py        # LSTM, GRU for temporal patterns
│   │   ├── ensemble_models.py        # XGBoost, Random Forest
│   │   └── neural_networks.py        # Deep Neural Networks
│   ├── rules_engine/
│   │   ├── rule_processor.py         # Business rules execution
│   │   ├── rule_builder.py           # Dynamic rule creation
│   │   └── rule_optimizer.py         # Rule performance optimization
│   ├── feature_engineering/
│   │   ├── transaction_features.py   # Transaction-based features
│   │   ├── user_features.py          # User behavior features
│   │   ├── network_features.py       # Graph-based features
│   │   └── temporal_features.py      # Time-series features
│   └── api/
│       ├── fraud_scoring_api.py      # Real-time scoring endpoint
│       ├── batch_processing_api.py   # Batch analysis endpoint
│       └── model_management_api.py   # Model deployment endpoint
├── tests/
├── deployment/
│   ├── Dockerfile
│   ├── k8s-manifests/
│   └── helm-charts/
├── docs/
├── requirements.txt
├── test_anomaly_detection.py
└── README.md
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- pip or conda

### Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Or install specific packages
pip install pandas numpy scikit-learn matplotlib seaborn
```

## 🚀 Quick Start

### 1. Basic Usage

```python
from src.models.anomaly_detection import IsolationForestFraudDetector

# Initialize the detector
detector = IsolationForestFraudDetector(random_state=42)

# Load and analyze your data
detector.load_and_analyze_data('your_data.csv')

# Check data suitability
detector.check_data_suitability()

# Set learning mode (supervised/unsupervised)
detector.setup_learning_mode()

# Choose anomaly detection method (classic or risk score based)
# This will be prompted during setup_learning_mode()

# Preprocess data
detector.preprocess_data()

# Train models with different contamination levels
detector.train_models([0.01, 0.05, 0.1])

# Evaluate models (if supervised)
if detector.is_supervised:
    detector.evaluate_models()

# Create visualizations
detector.create_visualizations(save_plots=True)

# Export results
detector.export_results('fraud_detection_results')

# Print summary
detector.print_summary()
```

### 2. Run the Test Suite

```bash
# Run comprehensive tests
python test_anomaly_detection.py
```

### 3. Command Line Usage

```bash
# Run the interactive system
python src/models/anomaly_detection.py
```

### 4. Risk Score Based Detection

```python
# Example of risk score based detection
detector = IsolationForestFraudDetector(random_state=42)
detector.load_and_analyze_data('your_data.csv')

# Setup will prompt for detection method
detector.setup_learning_mode()
# Choose: 2. Risk Score based (custom threshold)
# Enter threshold: 0.7 (example)

detector.preprocess_data()
detector.train_models([0.1])
detector.evaluate_models()  # Uses risk score threshold
```

## 📊 Data Requirements

### Supported Data Types
- **CSV files** with mixed data types
- **Transaction data** with features like amount, time, merchant, etc.
- **User behavior data** with patterns and sequences
- **Any tabular data** suitable for anomaly detection

### Data Format
- **Primary Key**: Automatically detected and removed
- **Categorical Variables**: Automatically encoded using LabelEncoder
- **Numerical Variables**: Standardized using StandardScaler
- **Missing Values**: Handled automatically (median for numerical, mode for categorical)

### Minimum Requirements
- At least 100 samples
- At least 2 numerical features
- CSV format with headers

## 🎯 Learning Modes

### Supervised Mode
- Requires labeled data with fraud indicators
- Provides comprehensive evaluation metrics
- Generates confusion matrices and ROC curves
- Best for model validation and performance assessment

### Unsupervised Mode
- No labels required
- Focuses on anomaly detection
- Suitable for real-time fraud detection
- Best for production environments

## 🔍 Detection Methods

### Classic Method
- Uses Isolation Forest's built-in predictions
- Binary classification based on contamination level
- Automatic threshold determination
- Best for standard anomaly detection scenarios

### Risk Score Based Method
- Uses custom risk score thresholds (0.0 - 1.0)
- User-defined anomaly detection sensitivity
- More granular control over detection criteria
- Best for business-specific risk management

## 📈 Output and Results

### Generated Files
- **Prediction Results**: CSV files with original data + predictions
- **Evaluation Metrics**: Performance metrics for each contamination level
- **Configuration**: JSON file with analysis parameters
- **Visualizations**: PNG files with comprehensive analysis plots

### Risk Scoring
- **Anomaly Score**: Raw Isolation Forest decision function output
- **Risk Score**: Normalized score (0-1) for business interpretation
- **Binary Prediction**: 0 (normal) or 1 (fraud) classification
- **Custom Thresholding**: User-defined risk score thresholds for anomaly detection

## 🔧 Configuration

### Model Parameters
- **Contamination Levels**: [0.01, 0.05, 0.1] (customizable)
- **Random State**: 42 (for reproducibility)
- **N Estimators**: 100 (number of trees)
- **Max Samples**: 'auto' (sample size for each tree)
- **Detection Method**: Classic or Risk Score based (user selectable)
- **Risk Score Threshold**: 0.0 - 1.0 (for risk score based method)

### Preprocessing Options
- **High Cardinality Threshold**: 50% unique values
- **Low Variance Threshold**: 0.01 variance
- **Missing Value Strategy**: Median (numerical), Mode (categorical)

## 📊 Performance Metrics

### Supervised Evaluation
- **Accuracy**: Overall prediction accuracy
- **F1-Score**: Harmonic mean of precision and recall
- **Precision**: True positives / (True positives + False positives)
- **Recall**: True positives / (True positives + False negatives)
- **ROC-AUC**: Area under the ROC curve

### Unsupervised Analysis
- **Anomaly Score Distribution**: Statistical analysis of scores
- **Feature Importance**: Variance-based feature ranking
- **Risk Score Distribution**: Business-interpretable risk levels
- **Threshold-based Detection**: Custom risk score threshold analysis

## 🏗️ Enterprise Integration

### Microservices Architecture
- **Stateless Design**: No internal state, external storage for persistence
- **API Gateway Ready**: Compatible with Kong, Istio ingress
- **Container Ready**: Docker support with multi-stage builds
- **Kubernetes Ready**: Helm charts and K8s manifests included

### Monitoring and Logging
- **Structured Logging**: JSON format for centralized analysis
- **Prometheus Metrics**: Ready for monitoring integration
- **Performance Tracking**: Latency and throughput metrics
- **Error Handling**: Comprehensive exception management

## 🔒 Security and Compliance

### Data Protection
- **No Data Persistence**: Data processed in memory only
- **Secure Logging**: Sensitive data excluded from logs
- **Input Validation**: Comprehensive data validation
- **Error Sanitization**: Safe error messages without data leakage

### Compliance Ready
- **GDPR Compatible**: Data processing transparency
- **PCI DSS Ready**: Secure transaction processing
- **Audit Trail**: Complete processing logs
- **Data Lineage**: Full data transformation tracking

## 🧪 Testing

### Test Coverage
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Performance Tests**: Load and stress testing
- **Security Tests**: Vulnerability assessment

### Running Tests
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_anomaly_detection.py
```

## 📚 Documentation

### API Documentation
- **OpenAPI 3.0**: Complete API specification
- **Swagger UI**: Interactive API documentation
- **Code Examples**: Comprehensive usage examples
- **Integration Guides**: Step-by-step integration instructions

### Business Documentation
- **Fraud Detection Guide**: Business process documentation
- **Risk Management**: Risk assessment and mitigation
- **Performance Tuning**: Optimization recommendations
- **Troubleshooting**: Common issues and solutions

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Install development dependencies
4. Run tests and linting
5. Submit a pull request

### Code Standards
- **PEP 8**: Python style guidelines
- **Type Hints**: Comprehensive type annotations
- **Docstrings**: Google-style documentation
- **Testing**: 90%+ test coverage required

## 📄 License

This project is part of the Enterprise Fraud Detection Platform and follows the platform's licensing terms.

## 🆘 Support

### Getting Help
- **Documentation**: Comprehensive guides and examples
- **Issues**: GitHub issues for bug reports
- **Discussions**: Community discussions and Q&A
- **Enterprise Support**: Contact platform support team

### Common Issues
- **Data Format**: Ensure CSV format with proper headers
- **Memory Usage**: Large datasets may require chunked processing
- **Dependencies**: Ensure all required packages are installed
- **Permissions**: Check file read/write permissions
- **Risk Score Threshold**: Choose appropriate threshold (0.0-1.0) for your use case
- **Detection Method**: Select classic method for standard scenarios, risk score for custom control

---

**Enterprise Fraud Detection Platform v1.0.0**  
*Built with ❤️ for secure and scalable fraud detection*
