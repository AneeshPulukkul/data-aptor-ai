from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

class DatasetBase(BaseModel):
    """Base model for dataset information"""
    name: str = Field(..., description="Name of the dataset file")
    file_type: str = Field(..., description="Type of the file (csv, json, txt)")
    file_size: int = Field(..., description="Size of the file in bytes")

class DatasetCreate(DatasetBase):
    """Model for creating a new dataset record"""
    file_path: str = Field(..., description="Path to the stored file in the object storage")
    metadata: Dict[str, Any] = Field(..., description="Metadata extracted from the dataset")

class DatasetResponse(DatasetBase):
    """Model for dataset response"""
    id: int = Field(..., description="Unique identifier for the dataset")
    file_path: str = Field(..., description="Path to the stored file in the object storage")
    created_at: datetime = Field(..., description="Timestamp when the dataset was created")
    metadata: Dict[str, Any] = Field(..., description="Metadata extracted from the dataset")

    class Config:
        orm_mode = True

class DatasetList(BaseModel):
    """Model for list of datasets response"""
    datasets: List[DatasetResponse] = Field(..., description="List of datasets")
    total: int = Field(..., description="Total number of datasets")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(10, description="Number of items per page")

class ErrorResponse(BaseModel):
    """Model for error responses"""
    detail: str = Field(..., description="Error message")

class HealthCheckResponse(BaseModel):
    """Model for health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    uptime: float = Field(..., description="Service uptime in seconds")
    database_connection: bool = Field(..., description="Database connection status")
    storage_connection: bool = Field(..., description="Storage connection status")
