import os
import sys
import pytest
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np

# Add the parent directory to sys.path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from processor import DataProcessor
from service import IngestionService
from database import Dataset

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "test_data"
os.makedirs(TEST_DATA_DIR, exist_ok=True)

# Create test data files
def create_test_csv():
    """Create a test CSV file for testing"""
    file_path = TEST_DATA_DIR / "test.csv"
    df = pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'age': [25, 30, 35, 40, 45],
        'email': ['alice@example.com', 'bob@example.com', 'charlie@example.com', 'david@example.com', 'eve@example.com'],
        'score': [85.5, 90.0, 82.5, 95.5, 88.0]
    })
    df.to_csv(file_path, index=False)
    return file_path

def create_test_json():
    """Create a test JSON file for testing"""
    file_path = TEST_DATA_DIR / "test.json"
    data = [
        {'id': 1, 'name': 'Alice', 'age': 25, 'email': 'alice@example.com', 'score': 85.5},
        {'id': 2, 'name': 'Bob', 'age': 30, 'email': 'bob@example.com', 'score': 90.0},
        {'id': 3, 'name': 'Charlie', 'age': 35, 'email': 'charlie@example.com', 'score': 82.5},
        {'id': 4, 'name': 'David', 'age': 40, 'email': 'david@example.com', 'score': 95.5},
        {'id': 5, 'name': 'Eve', 'age': 45, 'email': 'eve@example.com', 'score': 88.0}
    ]
    with open(file_path, 'w') as f:
        json.dump(data, f)
    return file_path

def create_test_txt():
    """Create a test TXT file for testing"""
    file_path = TEST_DATA_DIR / "test.txt"
    lines = [
        "This is line 1 of the test file.",
        "This is line 2 of the test file.",
        "This is line 3 of the test file.",
        "This is line 4 of the test file.",
        "This is line 5 of the test file."
    ]
    with open(file_path, 'w') as f:
        f.write('\n'.join(lines))
    return file_path

# Test the DataProcessor class
class TestDataProcessor:
    """Tests for the DataProcessor class"""
    
    def setup_method(self):
        """Set up test data before each test"""
        self.csv_path = create_test_csv()
        self.json_path = create_test_json()
        self.txt_path = create_test_txt()
    
    def teardown_method(self):
        """Clean up test data after each test"""
        for file in [self.csv_path, self.json_path, self.txt_path]:
            if os.path.exists(file):
                os.remove(file)
    
    def test_process_csv(self):
        """Test CSV processing"""
        metadata = DataProcessor.process_csv(self.csv_path)
        
        # Check basic metadata
        assert metadata['format'] == 'csv'
        assert metadata['row_count'] == 5
        assert metadata['column_count'] == 5
        assert set(metadata['columns']) == {'id', 'name', 'age', 'email', 'score'}
        
        # Check data types
        assert 'int' in metadata['data_types']['id'].lower()
        assert 'object' in metadata['data_types']['name'].lower() or 'string' in metadata['data_types']['name'].lower()
        assert 'float' in metadata['data_types']['score'].lower()
        
        # Check sample data
        assert len(metadata['sample_data']) == 5
        assert metadata['sample_data'][0]['name'] == 'Alice'
    
    def test_process_json(self):
        """Test JSON processing"""
        metadata = DataProcessor.process_json(self.json_path)
        
        # Check basic metadata
        assert metadata['format'] == 'json'
        assert metadata['structure'] == 'array_of_objects'
        assert metadata['row_count'] == 5
        assert metadata['column_count'] == 5
        assert set(metadata['columns']) == {'id', 'name', 'age', 'email', 'score'}
        
        # Check sample data
        assert len(metadata['sample_data']) == 5
        assert metadata['sample_data'][0]['name'] == 'Alice'
    
    def test_process_txt(self):
        """Test TXT processing"""
        metadata = DataProcessor.process_txt(self.txt_path)
        
        # Check basic metadata
        assert metadata['format'] == 'txt'
        assert metadata['row_count'] == 5
        assert metadata['column_count'] == 1
        assert metadata['columns'] == ['text']
        
        # Check sample data
        assert len(metadata['sample_data']) == 5
        assert metadata['sample_data'][0]['text'] == 'This is line 1 of the test file.'
        
        # Check line statistics
        assert 'line_length_stats' in metadata
        assert metadata['line_length_stats']['min'] > 0
        assert metadata['line_length_stats']['max'] > 0
        
        # Check token estimates
        assert 'estimated_tokens' in metadata
        assert metadata['estimated_tokens']['estimated_total'] > 0

# Test the IngestionService class
@pytest.mark.asyncio
class TestIngestionService:
    """Tests for the IngestionService class"""
    
    def setup_method(self):
        """Set up test data and mocks before each test"""
        self.csv_path = create_test_csv()
        self.json_path = create_test_json()
        self.txt_path = create_test_txt()
        
        # Create mock database session
        self.mock_db = MagicMock()
        self.mock_db.add = MagicMock()
        self.mock_db.commit = MagicMock()
        self.mock_db.refresh = MagicMock()
        self.mock_db.rollback = MagicMock()
        
        # Create mock dataset
        self.mock_dataset = MagicMock(spec=Dataset)
        self.mock_dataset.id = 1
        self.mock_dataset.name = "test.csv"
        self.mock_dataset.file_path = "test-uuid.csv"
        self.mock_dataset.file_type = "csv"
        self.mock_dataset.file_size = 1024
        self.mock_dataset.created_at = "2023-06-15T12:00:00"
        self.mock_dataset.metadata = {"test": "metadata"}
        
        # Configure mock db.execute().scalar_one_or_none() to return mock_dataset
        self.mock_execute_result = MagicMock()
        self.mock_execute_result.scalar_one_or_none.return_value = self.mock_dataset
        self.mock_db.execute.return_value = self.mock_execute_result
        
        # Create service with mock storage client
        self.service = IngestionService()
        self.service.storage_client = MagicMock()
        self.service.storage_client.upload_file.return_value = "s3://test-bucket/test-uuid.csv"
    
    def teardown_method(self):
        """Clean up test data after each test"""
        for file in [self.csv_path, self.json_path, self.txt_path]:
            if os.path.exists(file):
                os.remove(file)
    
    @pytest.mark.asyncio
    async def test_process_file_csv(self):
        """Test processing a CSV file"""
        # Patch the _extract_metadata method to return a fixed result
        with patch.object(IngestionService, '_extract_metadata', return_value={"test": "metadata"}):
            dataset_id, metadata = await self.service.process_file(
                file_path=str(self.csv_path),
                original_filename="test.csv",
                file_size=1024,
                file_type="csv",
                db=self.mock_db
            )
            
            # Check that the database operations were called
            self.mock_db.add.assert_called_once()
            self.mock_db.commit.assert_called_once()
            self.mock_db.refresh.assert_called_once()
            
            # Check that the storage client was called
            self.service.storage_client.upload_file.assert_called_once()
            
            # Check the returned values
            assert dataset_id == self.mock_dataset.id
            assert metadata == {"test": "metadata"}
    
    def test_get_dataset(self):
        """Test getting a dataset by ID"""
        dataset = self.service.get_dataset(1, self.mock_db)
        
        # Check that the database query was executed
        self.mock_db.execute.assert_called_once()
        
        # Check the returned dataset
        assert dataset == self.mock_dataset
    
    def test_list_datasets(self):
        """Test listing datasets with pagination"""
        # Configure mock db.execute().scalars().all() to return a list of datasets
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [self.mock_dataset, self.mock_dataset]
        self.mock_execute_result.scalars.return_value = mock_scalars
        
        # Configure mock db.execute().scalar_one() to return a count
        another_mock_execute_result = MagicMock()
        another_mock_execute_result.scalar_one.return_value = 2
        self.mock_db.execute.side_effect = [another_mock_execute_result, self.mock_execute_result]
        
        datasets, total = self.service.list_datasets(0, 10, self.mock_db)
        
        # Check that the database query was executed twice (once for count, once for data)
        assert self.mock_db.execute.call_count == 2
        
        # Check the returned values
        assert len(datasets) == 2
        assert datasets[0] == self.mock_dataset
        assert total == 2

if __name__ == "__main__":
    # Create test data directory if it doesn't exist
    os.makedirs(TEST_DATA_DIR, exist_ok=True)
    
    # Run the tests
    pytest.main(["-xvs", __file__])
