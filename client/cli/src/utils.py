"""
DataAptor AI CLI - Utility functions

This module provides utility functions for the DataAptor AI CLI.
"""

import json
import click
from tabulate import tabulate
from colorama import Fore, Style


def format_table(data, headers=None, tablefmt="fancy_grid"):
    """Format data as a table"""
    return tabulate(data, headers=headers, tablefmt=tablefmt)


def format_json(data, indent=2):
    """Format data as JSON"""
    return json.dumps(data, indent=indent)


def format_csv(data, headers=None):
    """Format data as CSV"""
    result = []
    
    # Add headers if provided
    if headers:
        result.append(','.join(headers))
    
    # Add rows
    for row in data:
        result.append(','.join([str(cell) for cell in row]))
    
    return '\n'.join(result)


def format_metadata(metadata, max_length=500, verbose=False):
    """Format metadata for display"""
    metadata_str = json.dumps(metadata, indent=2)
    if len(metadata_str) > max_length and not verbose:
        metadata_str = metadata_str[:max_length] + "... (use --verbose to see all)"
    
    return metadata_str


def format_status(status):
    """Format status with color"""
    status_str = status.upper()
    
    if status == 'completed':
        return f"{Fore.GREEN}{status_str}{Style.RESET_ALL}"
    elif status == 'failed':
        return f"{Fore.RED}{status_str}{Style.RESET_ALL}"
    elif status == 'in_progress':
        return f"{Fore.YELLOW}{status_str}{Style.RESET_ALL}"
    else:
        return status_str


def format_score(score):
    """Format score as a string"""
    return f"{score:.2f}/10.0" if score is not None else "N/A"


def show_pagination_info(items, total, page, limit, command):
    """Show pagination information"""
    skip = (page - 1) * limit
    
    click.echo(f"\nShowing {len(items)} of {total} items (Page {page})")
    
    if total > skip + limit:
        click.echo(f"Use '{command} --page {page + 1}' to see the next page")
