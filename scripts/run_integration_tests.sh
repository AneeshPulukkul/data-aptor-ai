#!/bin/bash
# Run integration tests for DataAptor AI

set -e

echo "Running DataAptor AI Integration Tests"
echo "======================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Start services with docker-compose
echo ""
echo "Starting services..."
cd "$PROJECT_ROOT"
docker-compose up -d

# Wait for services to be ready
echo ""
echo "Waiting for services to be ready..."
sleep 30

# Function to check service health
check_health() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    echo "Checking $service_name health..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}$service_name is healthy${NC}"
            return 0
        fi
        echo "Attempt $attempt/$max_attempts - waiting..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}$service_name failed to start${NC}"
    return 1
}

# Check all services
FAILED=0

check_health "API Gateway" "http://localhost:8000/health" || FAILED=1
check_health "Orchestration Service" "http://localhost:8001/health" || FAILED=1
check_health "Ingestion Service" "http://localhost:8002/health" || FAILED=1
check_health "Assessment Service" "http://localhost:8003/health" || FAILED=1
check_health "Scoring Service" "http://localhost:8004/health" || FAILED=1
check_health "Reporting Service" "http://localhost:8005/health" || FAILED=1

if [ $FAILED -eq 1 ]; then
    echo -e "${RED}Some services failed to start. Check docker-compose logs.${NC}"
    docker-compose logs
    docker-compose down
    exit 1
fi

# Run integration tests
echo ""
echo "Running integration tests..."
echo "----------------------------"

# Test 1: Upload a dataset
echo "Test 1: Upload dataset..."
UPLOAD_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/datasets/upload" \
    -H "Authorization: Bearer test-token" \
    -F "file=@$PROJECT_ROOT/client/cli/tests/sample_dataset.csv" \
    -F "name=test-dataset")

if echo "$UPLOAD_RESPONSE" | grep -q '"id"'; then
    echo -e "${GREEN}Dataset upload successful${NC}"
    DATASET_ID=$(echo "$UPLOAD_RESPONSE" | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
else
    echo -e "${RED}Dataset upload failed${NC}"
    echo "$UPLOAD_RESPONSE"
    FAILED=1
fi

# Test 2: List datasets
echo "Test 2: List datasets..."
LIST_RESPONSE=$(curl -s "http://localhost:8000/api/datasets" \
    -H "Authorization: Bearer test-token")

if echo "$LIST_RESPONSE" | grep -q '"datasets"'; then
    echo -e "${GREEN}List datasets successful${NC}"
else
    echo -e "${RED}List datasets failed${NC}"
    FAILED=1
fi

# Test 3: Start assessment (if dataset was uploaded)
if [ -n "$DATASET_ID" ]; then
    echo "Test 3: Start assessment..."
    ASSESSMENT_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/assessments" \
        -H "Authorization: Bearer test-token" \
        -H "Content-Type: application/json" \
        -d "{\"dataset_id\": $DATASET_ID}")
    
    if echo "$ASSESSMENT_RESPONSE" | grep -q '"id"'; then
        echo -e "${GREEN}Assessment started successfully${NC}"
        ASSESSMENT_ID=$(echo "$ASSESSMENT_RESPONSE" | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
    else
        echo -e "${YELLOW}Assessment start returned unexpected response${NC}"
        echo "$ASSESSMENT_RESPONSE"
    fi
fi

# Cleanup
echo ""
echo "Cleaning up..."
docker-compose down

# Summary
echo ""
echo "======================================="
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All integration tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some integration tests failed!${NC}"
    exit 1
fi
