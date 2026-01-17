#!/bin/bash
# Run unit tests for all services

set -e

echo "Running DataAptor AI Unit Tests"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Track test results
FAILED=0

# Function to run tests for a service
run_tests() {
    local service_name=$1
    local service_path=$2
    
    echo ""
    echo "Testing $service_name..."
    echo "------------------------"
    
    if [ -d "$service_path" ]; then
        cd "$service_path"
        
        # Check if there's a tests directory or test files
        if [ -d "tests" ] || ls test_*.py 1> /dev/null 2>&1; then
            # Create virtual environment if it doesn't exist
            if [ ! -d "venv" ]; then
                python3 -m venv venv
            fi
            
            # Activate virtual environment
            source venv/bin/activate
            
            # Install dependencies
            if [ -f "requirements.txt" ]; then
                pip install -q -r requirements.txt
            fi
            pip install -q pytest pytest-cov
            
            # Run tests
            if pytest --cov=. --cov-report=term-missing -v; then
                echo -e "${GREEN}$service_name tests passed${NC}"
            else
                echo -e "${RED}$service_name tests failed${NC}"
                FAILED=1
            fi
            
            deactivate
        else
            echo "No tests found for $service_name"
        fi
        
        cd - > /dev/null
    else
        echo "Service path not found: $service_path"
    fi
}

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Run tests for each service
run_tests "Ingestion Service" "$PROJECT_ROOT/processing/ingestion-service"
run_tests "Assessment Service" "$PROJECT_ROOT/processing/assessment-service"
run_tests "Scoring Service" "$PROJECT_ROOT/processing/scoring-service"
run_tests "Reporting Service" "$PROJECT_ROOT/processing/reporting-service"
run_tests "API Gateway" "$PROJECT_ROOT/api-gateway"
run_tests "Orchestration Service" "$PROJECT_ROOT/orchestration-service"

# Run CLI tests
echo ""
echo "Testing CLI..."
echo "--------------"
if [ -d "$PROJECT_ROOT/client/cli" ]; then
    cd "$PROJECT_ROOT/client/cli"
    if [ -f "run_tests.sh" ]; then
        if ./run_tests.sh; then
            echo -e "${GREEN}CLI tests passed${NC}"
        else
            echo -e "${RED}CLI tests failed${NC}"
            FAILED=1
        fi
    fi
    cd - > /dev/null
fi

# Summary
echo ""
echo "================================"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
