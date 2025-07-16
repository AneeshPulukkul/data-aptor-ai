"""
Automated test script for the DataAptor CLI

This script tests the DataAptor CLI against the mock API server.
It runs a series of CLI commands and validates the responses.

Usage:
1. Start the mock API server: python tests/mock_api_server.py
2. Run this script: python tests/test_cli.py
"""

import os
import subprocess
import time
import json
import sys
from pathlib import Path

# Configuration
API_URL = "http://localhost:8000"
SAMPLE_DATASET = "tests/sample_dataset.csv"
TEST_OUTPUT_DIR = Path("./test_output")
TEST_OUTPUT_DIR.mkdir(exist_ok=True)

def run_command(cmd, show_output=True):
    """Run a CLI command and return the output"""
    print(f"\n\033[1;34m> {cmd}\033[0m")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if show_output:
        if result.returncode == 0:
            print(f"\033[32m{result.stdout}\033[0m")
        else:
            print(f"\033[31mError: {result.stderr}\033[0m")
    
    return result

def test_cli():
    """Run a series of tests for the DataAptor CLI"""
    
    print("\n\033[1;33m===== TESTING DATAAPTOR CLI =====\033[0m\n")
    
    # Check if CLI is installed
    result = run_command("dataaptor --help")
    if result.returncode != 0:
        print("\033[31mDataAptor CLI not installed or not in PATH. Please install it first.\033[0m")
        return False
    
    # Configure API URL
    run_command(f"dataaptor config --set api_url --value {API_URL}")
    
    # Check current configuration
    run_command("dataaptor config --list")
    
    # Step 1: Upload dataset
    print("\n\033[1;33m----- TESTING DATASET UPLOAD -----\033[0m")
    result = run_command(f"dataaptor upload {SAMPLE_DATASET}")
    
    # Extract dataset_id from output
    dataset_id = None
    for line in result.stdout.split('\n'):
        if "Dataset ID:" in line:
            parts = line.split(":")
            if len(parts) > 1:
                dataset_id = parts[1].strip()
                break
    
    if not dataset_id:
        print("\033[31mFailed to get dataset_id from upload command\033[0m")
        return False
    
    print(f"\033[32mUploaded dataset with ID: {dataset_id}\033[0m")
    
    # Step 2: List datasets
    print("\n\033[1;33m----- TESTING DATASET LISTING -----\033[0m")
    run_command("dataaptor list")
    
    # Get dataset in different formats
    run_command("dataaptor list --output json")
    run_command("dataaptor list --output csv")
    
    # Step 3: Get dataset details
    print("\n\033[1;33m----- TESTING DATASET INFO -----\033[0m")
    run_command(f"dataaptor info {dataset_id}")
    
    # Step 4: Trigger assessment
    print("\n\033[1;33m----- TESTING ASSESSMENT TRIGGER -----\033[0m")
    result = run_command(f"dataaptor assess {dataset_id} --no-wait")
    
    # Extract assessment_id from output
    assessment_id = None
    for line in result.stdout.split('\n'):
        if "Assessment ID:" in line:
            parts = line.split(":")
            if len(parts) > 1:
                assessment_id = parts[1].strip()
                break
    
    if not assessment_id:
        print("\033[31mFailed to get assessment_id from assess command\033[0m")
        return False
    
    print(f"\033[32mTriggered assessment with ID: {assessment_id}\033[0m")
    
    # Step 5: Check assessment status (initially in_progress)
    print("\n\033[1;33m----- TESTING ASSESSMENT STATUS -----\033[0m")
    run_command(f"dataaptor status {assessment_id}")
    
    # Wait for assessment to complete (simulated by the mock server)
    print("\n\033[1;33m----- WAITING FOR ASSESSMENT TO COMPLETE -----\033[0m")
    for i in range(12):  # Wait up to 12 seconds
        result = run_command(f"dataaptor status {assessment_id}", show_output=False)
        if "COMPLETED" in result.stdout:
            print("\033[32mAssessment completed!\033[0m")
            run_command(f"dataaptor status {assessment_id}")
            break
        print(f"Waiting... {i+1}/12")
        time.sleep(1)
    
    # Step 6: List assessments
    print("\n\033[1;33m----- TESTING ASSESSMENTS LISTING -----\033[0m")
    run_command("dataaptor assessments")
    run_command(f"dataaptor assessments --dataset-id {dataset_id}")
    
    # Step 7: Get assessment report
    print("\n\033[1;33m----- TESTING ASSESSMENT REPORT -----\033[0m")
    run_command(f"dataaptor report {assessment_id}")
    
    # Step 8: Export assessment report in different formats
    print("\n\033[1;33m----- TESTING REPORT EXPORT -----\033[0m")
    formats = ["pdf", "html", "json", "csv"]
    
    for format in formats:
        output_file = TEST_OUTPUT_DIR / f"report_{assessment_id}.{format}"
        run_command(f"dataaptor export {assessment_id} --format {format} --output {output_file}")
        
        if output_file.exists():
            print(f"\033[32mSuccessfully exported {format} report to {output_file}\033[0m")
        else:
            print(f"\033[31mFailed to export {format} report\033[0m")
    
    # Step 9: Delete dataset
    print("\n\033[1;33m----- TESTING DATASET DELETION -----\033[0m")
    run_command(f"dataaptor delete {dataset_id} --force")
    
    # Check if deletion was successful by listing datasets
    result = run_command("dataaptor list", show_output=False)
    if dataset_id in result.stdout:
        print(f"\033[31mDataset {dataset_id} was not deleted successfully\033[0m")
    else:
        print(f"\033[32mDataset {dataset_id} was deleted successfully\033[0m")
    
    print("\n\033[1;33m===== TEST SUMMARY =====\033[0m")
    print("\033[32mAll tests completed. Check the output above for any errors.\033[0m")
    print(f"\033[32mExported reports can be found in the {TEST_OUTPUT_DIR} directory.\033[0m")
    
    return True

if __name__ == "__main__":
    test_cli()
