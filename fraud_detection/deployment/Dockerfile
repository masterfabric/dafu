# Dockerfile for DAFU - Data Analytics Functional Utilities
# Fraud Detection Service with CLI Tool Support
# Multi-stage build for production-ready container
# ================================================

# Stage 1: Base builder stage
# ================================================
FROM python:3.9-slim as builder

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY fraud_detection/requirements.txt .
COPY fraud_detection/requirements-minimal.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Install CLI-specific dependencies
RUN pip install --no-cache-dir click>=8.0.0 rich>=13.0.0 IPython>=8.0.0

# Stage 2: Runtime stage
# ================================================
FROM python:3.9-slim

# Set metadata
LABEL maintainer="MasterFabric <dafu@masterfabric.co>"
LABEL description="DAFU - Data Analytics Functional Utilities - Fraud Detection & E-commerce Analytics"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    FRAUD_DETECTION_HOME=/app \
    MODEL_STORAGE_PATH=/app/models \
    RESULTS_PATH=/app/results \
    LOG_LEVEL=INFO

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy fraud_detection application code
COPY --chown=appuser:appuser fraud_detection /app/fraud_detection/

# Copy dafu_cli from root directory
COPY --chown=appuser:appuser dafu_cli /app/dafu_cli/
COPY --chown=appuser:appuser setup.py /app/
COPY --chown=appuser:appuser pyproject.toml /app/

# Copy entrypoint script
COPY fraud_detection/deployment/entrypoint.sh /app/entrypoint.sh

# Change to root user temporarily for pip install
USER root

# Install DAFU CLI in editable mode
RUN pip install -e /app/

# Create necessary directories and make entrypoint executable
RUN mkdir -p /app/fraud_detection/models /app/fraud_detection/results /app/fraud_detection/logs && \
    chmod +x /app/entrypoint.sh && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Add fraud_detection to Python path
ENV PYTHONPATH="${PYTHONPATH}:/app/fraud_detection:/app/fraud_detection/src"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command - CLI interactive mode
CMD ["dafu", "fraud-detection"]
