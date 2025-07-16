@echo off
REM Test script for DataAptor CLI
REM This script runs the mock API server and tests the CLI against it

echo Setting up testing environment...

REM Check for required Python packages
pip install -q fastapi uvicorn python-multipart colorama

REM Create test directories
mkdir mock_data 2>nul
mkdir test_output 2>nul

echo Starting mock API server...
start "DataAptor Mock API" python tests/mock_api_server.py

REM Wait for server to start
echo Waiting for server to start...
timeout /t 3 /nobreak >nul

echo Running CLI tests...
python tests/test_cli.py

echo Tests completed.
echo Press any key to stop the mock server...
pause >nul

REM Kill the mock server
taskkill /FI "WINDOWTITLE eq DataAptor Mock API" /F

echo Cleanup complete.
