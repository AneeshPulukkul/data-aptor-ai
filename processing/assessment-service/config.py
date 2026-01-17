import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# API Configuration
API_TITLE = "DataAptor AI Assessment Service"
API_DESCRIPTION = "Service for assessing datasets for AI readiness"
API_VERSION = "0.1.0"

# Server Configuration
HOST = "0.0.0.0"
PORT = int(os.getenv("ASSESSMENT_SERVICE_PORT", 8003))

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
TEMP_DOWNLOAD_DIR = Path("/tmp/dataaptor/downloads")
TEMP_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Assessment modules
ASSESSMENT_MODULES = ["quality", "accessibility"]

# Quality assessment criteria
QUALITY_CRITERIA = {
    "completeness": {
        "weight": 0.3,
        "description": "Measures the presence of missing values in the dataset"
    },
    "accuracy": {
        "weight": 0.3,
        "description": "Measures the presence of outliers and type consistency"
    },
    "consistency": {
        "weight": 0.2,
        "description": "Measures the uniformity of data formats and patterns"
    },
    "timeliness": {
        "weight": 0.2,
        "description": "Measures the recency and relevance of temporal data"
    }
}

# Accessibility assessment criteria
ACCESSIBILITY_CRITERIA = {
    "availability": {
        "weight": 0.5,
        "description": "Measures the accessibility of the data format"
    },
    "volume": {
        "weight": 0.5,
        "description": "Measures the adequacy of the dataset size for AI training"
    }
}

# Database tables
DATASET_TABLE = "datasets"
ASSESSMENT_TABLE = "assessments"
