import os
import sys
import psycopg2
import boto3
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection parameters
DB_PARAMS = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'database': os.getenv('POSTGRES_DB', 'dataaptor'),
    'user': os.getenv('POSTGRES_USER', 'dataaptor'),
    'password': os.getenv('POSTGRES_PASSWORD', 'dataaptor')
}

# MinIO connection parameters
MINIO_PARAMS = {
    'endpoint_url': f"http://{os.getenv('MINIO_HOST', 'localhost')}:{os.getenv('MINIO_PORT', '9000')}",
    'aws_access_key_id': os.getenv('MINIO_ROOT_USER', 'minioadmin'),
    'aws_secret_access_key': os.getenv('MINIO_ROOT_PASSWORD', 'minioadmin'),
    'region_name': 'us-east-1'  # Placeholder region for MinIO
}

# Required buckets
REQUIRED_BUCKETS = ['datasets', 'reports', 'visualizations']

def create_tables():
    """Create the necessary database tables if they don't exist"""
    conn = None
    try:
        # Connect to the database
        print("Connecting to PostgreSQL database...")
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
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
        """)
        
        cursor.execute("""
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
        """)
        
        cursor.execute("""
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
        """)
        
        cursor.execute("""
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
        """)
        
        cursor.execute("""
        -- Create users table
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(100) NOT NULL,
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Commit the changes
        conn.commit()
        print("Database tables created successfully!")
        
    except Exception as e:
        print(f"Error creating database tables: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            cursor.close()
            conn.close()
    
    return True

def create_buckets():
    """Create the required MinIO buckets if they don't exist"""
    try:
        print("Connecting to MinIO...")
        s3_client = boto3.client('s3', **MINIO_PARAMS)
        
        # List existing buckets
        response = s3_client.list_buckets()
        existing_buckets = [bucket['Name'] for bucket in response['Buckets']]
        
        # Create buckets if they don't exist
        for bucket_name in REQUIRED_BUCKETS:
            if bucket_name not in existing_buckets:
                print(f"Creating bucket: {bucket_name}")
                s3_client.create_bucket(Bucket=bucket_name)
            else:
                print(f"Bucket already exists: {bucket_name}")
        
        print("MinIO buckets created successfully!")
        return True
    
    except Exception as e:
        print(f"Error creating MinIO buckets: {e}")
        return False

def main():
    """Main function to initialize the database and storage"""
    print("Starting DataAptor AI initialization...")
    
    # Create database tables
    if not create_tables():
        sys.exit(1)
    
    # Create MinIO buckets
    if not create_buckets():
        sys.exit(1)
    
    print("DataAptor AI initialization completed successfully!")

if __name__ == "__main__":
    main()
