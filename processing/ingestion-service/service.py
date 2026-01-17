import os
import uuid
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import select, func

import config
from database import Dataset
from storage import StorageClient
from processor import DataProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IngestionService:
    """Service for dataset ingestion and processing"""
    
    def __init__(self):
        """Initialize the ingestion service"""
        self.storage_client = StorageClient()
    
    async def process_file(self, file_path: str, original_filename: str, file_size: int, file_type: str, db: Session) -> Tuple[int, Dict[str, Any]]:
        """Process a file and store its metadata
        
        Args:
            file_path: Path to the temporary uploaded file
            original_filename: Original name of the uploaded file
            file_size: Size of the file in bytes
            file_type: Type of the file (csv, json, txt)
            db: Database session
            
        Returns:
            Tuple containing the dataset ID and metadata
        """
        try:
            # Extract metadata based on file type
            metadata = self._extract_metadata(file_path, file_type)
            
            # Generate a unique name for storage
            storage_filename = f"{uuid.uuid4()}.{file_type}"
            
            # Upload to storage
            storage_path = self.storage_client.upload_file(file_path, storage_filename)
            
            if not storage_path:
                raise Exception("Failed to upload file to storage")
            
            # Create database record
            dataset = Dataset(
                name=original_filename,
                file_path=storage_filename,  # Store just the object name, not the full URL
                file_type=file_type,
                file_size=file_size,
                metadata=metadata
            )
            
            db.add(dataset)
            db.commit()
            db.refresh(dataset)
            
            logger.info(f"Successfully processed file: {original_filename}, dataset ID: {dataset.id}")
            
            return dataset.id, metadata
        except Exception as e:
            logger.error(f"Error processing file: {original_filename}, error: {str(e)}")
            db.rollback()
            raise
    
    def get_dataset(self, dataset_id: int, db: Session) -> Optional[Dataset]:
        """Get dataset by ID
        
        Args:
            dataset_id: ID of the dataset
            db: Database session
            
        Returns:
            Dataset object if found, None otherwise
        """
        return db.execute(select(Dataset).where(Dataset.id == dataset_id)).scalar_one_or_none()
    
    def list_datasets(self, skip: int = 0, limit: int = 100, db: Session = None) -> Tuple[List[Dataset], int]:
        """List datasets with pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            db: Database session
            
        Returns:
            Tuple containing list of datasets and total count
        """
        # Get total count
        total = db.execute(select(func.count(Dataset.id))).scalar_one()
        
        # Get datasets with pagination
        datasets = db.execute(
            select(Dataset)
            .order_by(Dataset.created_at.desc())
            .offset(skip)
            .limit(limit)
        ).scalars().all()
        
        return datasets, total
    
    def _extract_metadata(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """Extract metadata from a file based on its type
        
        Args:
            file_path: Path to the file
            file_type: Type of the file (csv, json, txt)
            
        Returns:
            Dict containing metadata about the file
        """
        if file_type == "csv":
            return DataProcessor.process_csv(file_path)
        elif file_type == "json":
            return DataProcessor.process_json(file_path)
        elif file_type == "txt":
            return DataProcessor.process_txt(file_path)
        else:
            # Unsupported file type
            return {
                "error": f"Unsupported file type: {file_type}",
                "processing_status": "failed"
            }
