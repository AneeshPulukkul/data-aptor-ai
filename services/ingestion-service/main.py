import os
import json
import uuid
import time
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
import shutil
from typing import List, Optional
from datetime import datetime

import config
from database import Dataset, init_db, engine
from storage import StorageClient
from processor import DataProcessor
from service import IngestionService
from schemas import DatasetResponse, DatasetList, HealthCheckResponse, ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=config.API_TITLE,
    description=config.API_DESCRIPTION,
    version=config.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Initialize database
init_db()

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize service
ingestion_service = IngestionService()

# Record start time for uptime calculation
start_time = time.time()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_model=dict)
async def read_root():
    """Root endpoint with service information"""
    return {
        "message": "Welcome to DataAptor AI Ingestion Service",
        "version": config.API_VERSION,
        "docs": "/docs",
    }

@app.get("/health", response_model=HealthCheckResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint for monitoring service status"""
    # Check database connection
    db_connection = True
    try:
        # Execute a simple query to check database connection
        db.execute(select(1)).scalar_one()
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        db_connection = False
    
    # Check storage connection
    storage_connection = True
    try:
        # Try to list buckets to check storage connection
        ingestion_service.storage_client._ensure_bucket_exists()
    except Exception as e:
        logger.error(f"Storage connection error: {str(e)}")
        storage_connection = False
    
    return {
        "status": "healthy" if db_connection and storage_connection else "unhealthy",
        "version": config.API_VERSION,
        "uptime": time.time() - start_time,
        "database_connection": db_connection,
        "storage_connection": storage_connection,
    }

@app.post("/upload", response_model=DatasetResponse, responses={413: {"model": ErrorResponse}, 415: {"model": ErrorResponse}})
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a dataset file for AI readiness assessment
    
    This endpoint accepts file uploads for assessment. It validates the file type and size,
    extracts metadata, and stores the file in object storage.
    """
    # Validate file size
    file_size = 0
    temp_file_path = config.TEMP_UPLOAD_DIR / f"{uuid.uuid4()}_{file.filename}"
    
    # Ensure temp directory exists
    os.makedirs(config.TEMP_UPLOAD_DIR, exist_ok=True)
    
    # Save uploaded file temporarily
    try:
        with open(temp_file_path, "wb") as buffer:
            # Read and write the file in chunks to avoid memory issues
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                file_size += len(chunk)
                if file_size > config.MAX_UPLOAD_SIZE:
                    # Clean up the temp file
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large. Maximum size is {config.MAX_UPLOAD_SIZE/(1024*1024)}MB"
                    )
                buffer.write(chunk)
    except Exception as e:
        logger.error(f"Error saving uploaded file: {str(e)}")
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f"Error saving uploaded file: {str(e)}")
    
    # Validate file type
    file_ext = os.path.splitext(file.filename)[1].lower().lstrip(".")
    content_type = file.content_type
    
    valid_type = False
    for supported_ext, mime_types in config.SUPPORTED_FILE_TYPES.items():
        if file_ext == supported_ext or content_type in mime_types:
            valid_type = True
            file_ext = supported_ext  # Normalize extension
            break
    
    if not valid_type:
        # Clean up the temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type. Supported types: {', '.join(config.SUPPORTED_FILE_TYPES.keys())}"
        )
    
    try:
        # Process the file using the service
        dataset_id, metadata = await ingestion_service.process_file(
            file_path=str(temp_file_path),
            original_filename=file.filename,
            file_size=file_size,
            file_type=file_ext,
            db=db
        )
        
        # Add task to remove temporary file
        background_tasks.add_task(os.remove, temp_file_path)
        
        # Get the dataset from the database
        dataset = ingestion_service.get_dataset(dataset_id, db)
        
        # Return the response
        return {
            "id": dataset.id,
            "name": dataset.name,
            "file_type": dataset.file_type,
            "file_size": dataset.file_size,
            "file_path": dataset.file_path,
            "created_at": dataset.created_at,
            "metadata": dataset.metadata
        }
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        # Clean up the temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/datasets/{dataset_id}", response_model=DatasetResponse, responses={404: {"model": ErrorResponse}})
async def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """Get dataset details by ID
    
    This endpoint retrieves the details of a specific dataset by its ID.
    """
    dataset = ingestion_service.get_dataset(dataset_id, db)
    
    if not dataset:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset with ID {dataset_id} not found"
        )
    
    return {
        "id": dataset.id,
        "name": dataset.name,
        "file_type": dataset.file_type,
        "file_size": dataset.file_size,
        "file_path": dataset.file_path,
        "created_at": dataset.created_at,
        "metadata": dataset.metadata
    }

@app.get("/datasets", response_model=DatasetList)
async def list_datasets(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """List all datasets with pagination
    
    This endpoint retrieves a paginated list of all datasets.
    """
    datasets, total = ingestion_service.list_datasets(skip, limit, db)
    
    return {
        "datasets": [
            {
                "id": dataset.id,
                "name": dataset.name,
                "file_type": dataset.file_type,
                "file_size": dataset.file_size,
                "file_path": dataset.file_path,
                "created_at": dataset.created_at,
                "metadata": dataset.metadata
            }
            for dataset in datasets
        ],
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit
    }

@app.delete("/datasets/{dataset_id}", response_model=dict, responses={404: {"model": ErrorResponse}})
async def delete_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """Delete a dataset by ID
    
    This endpoint deletes a dataset and its associated file from storage.
    """
    # Get the dataset
    dataset = ingestion_service.get_dataset(dataset_id, db)
    
    if not dataset:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset with ID {dataset_id} not found"
        )
    
    try:
        # Delete the file from storage
        ingestion_service.storage_client.client.delete_object(
            Bucket=config.DATASET_BUCKET,
            Key=dataset.file_path
        )
        
        # Delete the dataset from the database
        db.delete(dataset)
        db.commit()
        
        return {"message": f"Dataset with ID {dataset_id} successfully deleted"}
    except Exception as e:
        logger.error(f"Error deleting dataset: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting dataset: {str(e)}")

# Run the application
if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting ingestion service on {config.HOST}:{config.PORT}")
    uvicorn.run(app, host=config.HOST, port=config.PORT)
