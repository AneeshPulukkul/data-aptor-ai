#!/bin/bash
# Test script for DataAptor CLI
# This script runs the mock API server and tests the CLI against it

echo "Setting up testing environment..."

# Check for required Python packages
pip install -q fastapi uvicorn python-multipart colorama

# Create test directories
mkdir -p mock_data
mkdir -p test_output

echo "Starting mock API server..."
python tests/mock_api_server.py & 
SERVER_PID=$!

# Wait for server to start
echo "Waiting for server to start..."
sleep 3

echo "Running CLI tests..."
python tests/test_cli.py

echo "Tests completed."
echo "Press Ctrl+C to stop the mock server..."

# Clean up when script is terminated
trap "kill $SERVER_PID; echo 'Mock server stopped'; exit" INT TERM EXIT

# Wait for user to stop the script
wait $SERVER_PID
