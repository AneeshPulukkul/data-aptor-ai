import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# API Configuration
API_TITLE = "DataAptor AI Ingestion Service"
API_DESCRIPTION = "Service for ingesting and processing datasets for AI readiness assessment"
API_VERSION = "0.1.0"

# Server Configuration
HOST = "0.0.0.0"
PORT = int(os.getenv("INGESTION_SERVICE_PORT", 8002))

# Database Configuration
POSTGRES_USER = os.getenv("POSTGRES_USER", "dataaptor")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "dataaptor")
POSTGRES_DB = os.getenv("POSTGRES_DB", "dataaptor")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# MinIO Configuration
MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER", "minioadmin")
MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
MINIO_HOST = os.getenv("MINIO_HOST", "localhost")
MINIO_PORT = os.getenv("MINIO_PORT", "9000")
MINIO_URL = f"http://{MINIO_HOST}:{MINIO_PORT}"
MINIO_SECURE = os.getenv("MINIO_SECURE", "False").lower() == "true"

# Storage Configuration
DATASET_BUCKET = "datasets"
TEMP_UPLOAD_DIR = Path("/tmp/dataaptor/uploads")
TEMP_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# File size limits
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100 MB

# Supported file types
SUPPORTED_FILE_TYPES = {
    "csv": ["text/csv", "application/csv", "application/vnd.ms-excel"],
    "json": ["application/json"],
    "txt": ["text/plain"],
}

# Database models
DATASET_TABLE = "datasets"
