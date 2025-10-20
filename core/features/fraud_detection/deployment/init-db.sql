-- ============================================================================
-- DAFU - Data Analytics Functional Utilities
-- Database Initialization
-- ============================================================================
-- 
-- This script initializes the database schema for the DAFU platform
-- 
-- Tables:
-- - transactions: Transaction records
-- - fraud_predictions: Model predictions
-- - users: User information
-- - merchants: Merchant information
-- - models: ML model metadata
-- - api_keys: API authentication keys
-- 
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pg_stat_statements for query performance monitoring
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- ============================================================================
-- Users Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    account_created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    risk_level VARCHAR(50) DEFAULT 'low',
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_user_id ON users(user_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_risk_level ON users(risk_level);

-- ============================================================================
-- Merchants Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS merchants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    merchant_id VARCHAR(255) UNIQUE NOT NULL,
    merchant_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    country VARCHAR(100),
    risk_score DECIMAL(5,4),
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_merchants_merchant_id ON merchants(merchant_id);
CREATE INDEX idx_merchants_category ON merchants(category);
CREATE INDEX idx_merchants_risk_score ON merchants(risk_score);

-- ============================================================================
-- Transactions Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    merchant_id VARCHAR(255) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    transaction_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    device_fingerprint VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    location_lat DECIMAL(10,8),
    location_lon DECIMAL(11,8),
    payment_method VARCHAR(50),
    is_fraud BOOLEAN,
    fraud_type VARCHAR(100),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id) ON DELETE CASCADE
);

CREATE INDEX idx_transactions_transaction_id ON transactions(transaction_id);
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_merchant_id ON transactions(merchant_id);
CREATE INDEX idx_transactions_timestamp ON transactions(transaction_timestamp DESC);
CREATE INDEX idx_transactions_amount ON transactions(amount);
CREATE INDEX idx_transactions_is_fraud ON transactions(is_fraud);
CREATE INDEX idx_transactions_created_at ON transactions(created_at DESC);

-- ============================================================================
-- Fraud Predictions Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS fraud_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id VARCHAR(255) NOT NULL,
    model_id VARCHAR(255) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    risk_score DECIMAL(5,4) NOT NULL,
    is_fraud BOOLEAN NOT NULL,
    confidence DECIMAL(5,4),
    prediction_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processing_time_ms DECIMAL(10,2),
    explanations JSONB,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE
);

CREATE INDEX idx_fraud_predictions_transaction_id ON fraud_predictions(transaction_id);
CREATE INDEX idx_fraud_predictions_model_id ON fraud_predictions(model_id);
CREATE INDEX idx_fraud_predictions_risk_score ON fraud_predictions(risk_score DESC);
CREATE INDEX idx_fraud_predictions_is_fraud ON fraud_predictions(is_fraud);
CREATE INDEX idx_fraud_predictions_timestamp ON fraud_predictions(prediction_timestamp DESC);

-- ============================================================================
-- ML Models Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS ml_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id VARCHAR(255) UNIQUE NOT NULL,
    model_name VARCHAR(255) NOT NULL,
    model_type VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    model_path TEXT,
    status VARCHAR(50) DEFAULT 'active',
    accuracy DECIMAL(5,4),
    precision_score DECIMAL(5,4),
    recall DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    training_date TIMESTAMP WITH TIME ZONE,
    deployment_date TIMESTAMP WITH TIME ZONE,
    last_evaluation_date TIMESTAMP WITH TIME ZONE,
    parameters JSONB,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ml_models_model_id ON ml_models(model_id);
CREATE INDEX idx_ml_models_status ON ml_models(status);
CREATE INDEX idx_ml_models_model_type ON ml_models(model_type);

-- ============================================================================
-- API Keys Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    api_key VARCHAR(255) UNIQUE NOT NULL,
    api_key_hash VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    rate_limit INTEGER DEFAULT 1000,
    expires_at TIMESTAMP WITH TIME ZONE,
    last_used_at TIMESTAMP WITH TIME ZONE,
    usage_count INTEGER DEFAULT 0,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_api_keys_api_key_hash ON api_keys(api_key_hash);
CREATE INDEX idx_api_keys_is_active ON api_keys(is_active);

-- ============================================================================
-- Audit Log Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100) NOT NULL,
    event_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(255),
    api_key_id UUID,
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    action VARCHAR(100) NOT NULL,
    status VARCHAR(50),
    ip_address INET,
    user_agent TEXT,
    request_data JSONB,
    response_data JSONB,
    error_message TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_event_type ON audit_logs(event_type);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(event_timestamp DESC);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);

-- ============================================================================
-- System Metrics Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(255) NOT NULL,
    metric_value DECIMAL(15,4) NOT NULL,
    metric_unit VARCHAR(50),
    metric_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    tags JSONB,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_system_metrics_name ON system_metrics(metric_name);
CREATE INDEX idx_system_metrics_timestamp ON system_metrics(metric_timestamp DESC);

-- ============================================================================
-- Create Views
-- ============================================================================

-- Fraud detection summary view
CREATE OR REPLACE VIEW fraud_detection_summary AS
SELECT
    DATE(prediction_timestamp) as date,
    COUNT(*) as total_predictions,
    SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) as fraud_count,
    AVG(risk_score) as avg_risk_score,
    AVG(processing_time_ms) as avg_processing_time_ms,
    model_id,
    model_version
FROM fraud_predictions
GROUP BY DATE(prediction_timestamp), model_id, model_version
ORDER BY date DESC;

-- Transaction summary view
CREATE OR REPLACE VIEW transaction_summary AS
SELECT
    DATE(transaction_timestamp) as date,
    COUNT(*) as total_transactions,
    SUM(amount) as total_amount,
    AVG(amount) as avg_amount,
    SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) as fraud_count,
    SUM(CASE WHEN is_fraud THEN amount ELSE 0 END) as fraud_amount
FROM transactions
GROUP BY DATE(transaction_timestamp)
ORDER BY date DESC;

-- ============================================================================
-- Create Functions
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_merchants_updated_at BEFORE UPDATE ON merchants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ml_models_updated_at BEFORE UPDATE ON ml_models
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_api_keys_updated_at BEFORE UPDATE ON api_keys
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Insert Sample Data (Optional - for development only)
-- ============================================================================

-- Insert sample users
INSERT INTO users (user_id, email, risk_level) VALUES
    ('user_001', 'user1@example.com', 'low'),
    ('user_002', 'user2@example.com', 'medium'),
    ('user_003', 'user3@example.com', 'low')
ON CONFLICT (user_id) DO NOTHING;

-- Insert sample merchants
INSERT INTO merchants (merchant_id, merchant_name, category, country) VALUES
    ('merchant_001', 'Electronics Store', 'electronics', 'US'),
    ('merchant_002', 'Fashion Boutique', 'fashion', 'UK'),
    ('merchant_003', 'Grocery Market', 'grocery', 'US')
ON CONFLICT (merchant_id) DO NOTHING;

-- Insert sample ML model
INSERT INTO ml_models (model_id, model_name, model_type, model_version, status, accuracy) VALUES
    ('isolation_forest_v1', 'Isolation Forest', 'anomaly_detection', '1.0.0', 'active', 0.95),
    ('lstm_v1', 'LSTM Sequence Model', 'sequence_detection', '1.0.0', 'active', 0.93)
ON CONFLICT (model_id) DO NOTHING;

-- ============================================================================
-- Grant Permissions
-- ============================================================================

-- Grant permissions to application user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dafu;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dafu;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO dafu;

-- ============================================================================
-- Database Initialization Complete
-- ============================================================================

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'DAFU database initialization completed successfully!';
    RAISE NOTICE 'Database: dafu';
    RAISE NOTICE 'Tables created: %, %, %, %, %, %, %, %',
        'users', 'merchants', 'transactions', 'fraud_predictions',
        'ml_models', 'api_keys', 'audit_logs', 'system_metrics';
END
$$;
