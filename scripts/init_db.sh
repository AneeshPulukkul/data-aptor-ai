#!/bin/bash

# Database initialization script for DataAptor AI
# This script creates the necessary database tables and initial data

# Change to the script directory
cd "$(dirname "$0")"

echo "Initializing DataAptor AI database..."

# Create SQL file with schema
cat > init_schema.sql << 'EOF'
-- Create datasets table
CREATE TABLE IF NOT EXISTS datasets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Create assessments table
CREATE TABLE IF NOT EXISTS assessments (
    id SERIAL PRIMARY KEY,
    dataset_id INTEGER REFERENCES datasets(id),
    module VARCHAR(50) NOT NULL,
    criterion VARCHAR(50) NOT NULL,
    score NUMERIC(3,1) NOT NULL,
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create scores table
CREATE TABLE IF NOT EXISTS scores (
    id SERIAL PRIMARY KEY,
    dataset_id INTEGER REFERENCES datasets(id),
    total_score NUMERIC(5,2) NOT NULL,
    quality_score NUMERIC(5,2),
    accessibility_score NUMERIC(5,2),
    weights JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create reports table
CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    dataset_id INTEGER REFERENCES datasets(id),
    score_id INTEGER REFERENCES scores(id),
    report_path VARCHAR(512),
    visualizations JSONB,
    recommendations JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
EOF

# Execute the SQL file using the PostgreSQL client
echo "Executing SQL schema..."
PGPASSWORD=${POSTGRES_PASSWORD:-dataaptor} psql -h ${POSTGRES_HOST:-localhost} -U ${POSTGRES_USER:-dataaptor} -d ${POSTGRES_DB:-dataaptor} -f init_schema.sql

# Initialize MinIO buckets using the AWS CLI
echo "Creating MinIO buckets..."

# Configure AWS CLI for MinIO
export AWS_ACCESS_KEY_ID=${MINIO_ROOT_USER:-minioadmin}
export AWS_SECRET_ACCESS_KEY=${MINIO_ROOT_PASSWORD:-minioadmin}
export AWS_DEFAULT_REGION=us-east-1

# Create required buckets
aws --endpoint-url http://${MINIO_HOST:-localhost}:${MINIO_PORT:-9000} s3 mb s3://datasets
aws --endpoint-url http://${MINIO_HOST:-localhost}:${MINIO_PORT:-9000} s3 mb s3://reports
aws --endpoint-url http://${MINIO_HOST:-localhost}:${MINIO_PORT:-9000} s3 mb s3://visualizations

echo "Database initialization completed!"

# Clean up
rm init_schema.sql
