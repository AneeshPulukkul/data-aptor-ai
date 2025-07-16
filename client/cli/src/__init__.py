"""
DataAptor AI CLI - Package initialization

This module initializes the DataAptor AI CLI package.
"""

from .api_client import DataAptorClient
from .utils import (
    format_table, format_json, format_csv, format_metadata,
    format_status, format_score, show_pagination_info
)

__all__ = [
    'DataAptorClient',
    'format_table',
    'format_json',
    'format_csv',
    'format_metadata',
    'format_status',
    'format_score',
    'show_pagination_info'
]
