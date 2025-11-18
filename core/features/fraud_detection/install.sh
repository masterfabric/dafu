#!/bin/bash

# Fraud Detection Service Installation Script
# ===========================================

echo "🚀 Installing Fraud Detection Service Dependencies"
echo "=================================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $PYTHON_VERSION detected. Python 3.8+ is required."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Use project root requirements.txt
REQUIREMENTS_FILE="$PROJECT_ROOT/requirements.txt"
REQUIREMENTS_MINIMAL_FILE="$SCRIPT_DIR/requirements-minimal.txt"

# Create virtual environment if it doesn't exist
if [ ! -d "fraud_detection_env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv fraud_detection_env
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source fraud_detection_env/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
if [ "$1" = "minimal" ]; then
    echo "   Installing minimal requirements..."
    if [ -f "$REQUIREMENTS_MINIMAL_FILE" ]; then
        pip install -r "$REQUIREMENTS_MINIMAL_FILE"
    else
        echo "   ⚠️  Minimal requirements file not found, using project requirements..."
        pip install -r "$REQUIREMENTS_FILE"
    fi
else
    echo "   Installing full requirements from project root..."
    if [ -f "$REQUIREMENTS_FILE" ]; then
        pip install -r "$REQUIREMENTS_FILE"
    else
        echo "   ⚠️  Project requirements not found, using local requirements.txt..."
        pip install -r requirements.txt
    fi
fi

# Verify installation
echo "🔍 Verifying installation..."
python3 -c "
try:
    import pandas as pd
    import numpy as np
    from sklearn.ensemble import IsolationForest
    import matplotlib.pyplot as plt
    import seaborn as sns
    print('✅ All core packages installed successfully!')
except ImportError as e:
    print(f'❌ Installation failed: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Installation completed successfully!"
    echo ""
    echo "To activate the virtual environment:"
    echo "  source fraud_detection_env/bin/activate"
    echo ""
    echo "To run the fraud detection system:"
    echo "  python src/models/anomaly_detection.py"
    echo ""
    echo "To deactivate the virtual environment:"
    echo "  deactivate"
else
    echo "❌ Installation failed. Please check the error messages above."
    exit 1
fi
