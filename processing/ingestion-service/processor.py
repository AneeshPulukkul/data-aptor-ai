import pandas as pd
import numpy as np
import json
import os
from typing import Dict, Any, List, Optional
import config

class DataProcessor:
    """Class for processing different types of datasets"""
    
    @staticmethod
    def process_csv(file_path: str) -> Dict[str, Any]:
        """Process a CSV file and extract metadata
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Dict containing metadata about the CSV file
        """
        try:
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Extract basic metadata
            metadata = DataProcessor._extract_dataframe_metadata(df)
            metadata['format'] = 'csv'
            
            # Add CSV-specific metadata
            metadata['delimiter'] = ','  # Assuming standard CSV
            metadata['has_header'] = True  # Assuming header is present
            
            return metadata
        except Exception as e:
            return {
                'error': str(e),
                'format': 'csv',
                'processing_status': 'failed'
            }
    
    @staticmethod
    def process_json(file_path: str) -> Dict[str, Any]:
        """Process a JSON file and extract metadata
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Dict containing metadata about the JSON file
        """
        try:
            # Read the JSON file
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Determine structure type
            if isinstance(data, list):
                # JSON array of objects
                if len(data) > 0 and isinstance(data[0], dict):
                    # Convert to DataFrame for consistent processing
                    df = pd.DataFrame(data)
                    metadata = DataProcessor._extract_dataframe_metadata(df)
                    metadata['structure'] = 'array_of_objects'
                    metadata['item_count'] = len(data)
                else:
                    # Array of values
                    metadata = {
                        'structure': 'array_of_values',
                        'row_count': len(data),
                        'column_count': 1,
                        'columns': ['value'],
                        'data_types': {'value': type(data[0]).__name__ if len(data) > 0 else 'unknown'},
                        'sample_data': data[:5] if len(data) > 0 else []
                    }
            elif isinstance(data, dict):
                # Single JSON object
                # Convert to DataFrame for consistent processing
                df = pd.DataFrame([data])
                metadata = DataProcessor._extract_dataframe_metadata(df)
                metadata['structure'] = 'object'
                metadata['key_count'] = len(data.keys())
            else:
                # Single value
                metadata = {
                    'structure': 'value',
                    'row_count': 1,
                    'column_count': 1,
                    'columns': ['value'],
                    'data_types': {'value': type(data).__name__},
                    'sample_data': [data]
                }
            
            metadata['format'] = 'json'
            return metadata
        except Exception as e:
            return {
                'error': str(e),
                'format': 'json',
                'processing_status': 'failed'
            }
    
    @staticmethod
    def process_txt(file_path: str) -> Dict[str, Any]:
        """Process a text file and extract metadata
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Dict containing metadata about the text file
        """
        try:
            # Read the text file
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            # Extract metadata
            metadata = {
                'format': 'txt',
                'row_count': len(lines),
                'column_count': 1,
                'columns': ['text'],
                'data_types': {'text': 'string'},
                'sample_data': [{'text': line.strip()} for line in lines[:5]],
                'line_length_stats': DataProcessor._calculate_line_stats(lines),
                'estimated_tokens': DataProcessor._estimate_tokens(lines)
            }
            
            return metadata
        except Exception as e:
            return {
                'error': str(e),
                'format': 'txt',
                'processing_status': 'failed'
            }
    
    @staticmethod
    def _extract_dataframe_metadata(df: pd.DataFrame) -> Dict[str, Any]:
        """Extract metadata from a pandas DataFrame
        
        Args:
            df: Pandas DataFrame
            
        Returns:
            Dict containing metadata about the DataFrame
        """
        # Get basic info
        metadata = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': df.columns.tolist(),
            'data_types': {col: str(df[col].dtype) for col in df.columns},
            'sample_data': df.head(5).to_dict(orient='records'),
            'statistics': {}
        }
        
        # Calculate statistics for numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        for col in numeric_columns:
            metadata['statistics'][col] = {
                'min': float(df[col].min()) if not pd.isna(df[col].min()) else None,
                'max': float(df[col].max()) if not pd.isna(df[col].max()) else None,
                'mean': float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
                'median': float(df[col].median()) if not pd.isna(df[col].median()) else None,
                'std': float(df[col].std()) if not pd.isna(df[col].std()) else None,
                'null_count': int(df[col].isna().sum()),
                'null_percentage': float(df[col].isna().mean() * 100)
            }
        
        # Calculate counts for categorical columns
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
        for col in categorical_columns:
            value_counts = df[col].value_counts().head(10).to_dict()
            # Convert keys to strings to ensure JSON serialization
            value_counts = {str(k): int(v) for k, v in value_counts.items()}
            
            metadata['statistics'][col] = {
                'unique_count': int(df[col].nunique()),
                'null_count': int(df[col].isna().sum()),
                'null_percentage': float(df[col].isna().mean() * 100),
                'top_values': value_counts
            }
        
        # Calculate completeness score
        metadata['completeness'] = {
            'overall_missing_percentage': float(df.isna().mean().mean() * 100),
            'columns_with_nulls': int((df.isna().sum() > 0).sum()),
            'rows_with_nulls': int((df.isna().any(axis=1)).sum())
        }
        
        return metadata
    
    @staticmethod
    def _calculate_line_stats(lines: List[str]) -> Dict[str, Any]:
        """Calculate statistics about line lengths
        
        Args:
            lines: List of lines from a text file
            
        Returns:
            Dict containing statistics about line lengths
        """
        if not lines:
            return {
                'min': 0,
                'max': 0,
                'mean': 0,
                'median': 0,
                'std': 0
            }
        
        line_lengths = [len(line) for line in lines]
        return {
            'min': min(line_lengths),
            'max': max(line_lengths),
            'mean': sum(line_lengths) / len(line_lengths),
            'median': sorted(line_lengths)[len(line_lengths) // 2],
            'std': (sum((x - (sum(line_lengths) / len(line_lengths))) ** 2 for x in line_lengths) / len(line_lengths)) ** 0.5
        }
    
    @staticmethod
    def _estimate_tokens(lines: List[str]) -> Dict[str, Any]:
        """Estimate the number of tokens in the text
        
        Args:
            lines: List of lines from a text file
            
        Returns:
            Dict containing token estimates
        """
        text = ' '.join([line.strip() for line in lines])
        # Rough estimate: 1 token ≈ 4 characters
        estimated_tokens = len(text) // 4
        return {
            'estimated_total': estimated_tokens,
            'estimation_method': 'character_based',
            'characters': len(text)
        }
