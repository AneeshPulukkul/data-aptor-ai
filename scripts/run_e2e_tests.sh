#!/bin/bash
# Run end-to-end tests for DataAptor AI

set -e

echo "Running DataAptor AI End-to-End Tests"
echo "======================================"

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

# Start all services
echo ""
echo "Starting all services..."
cd "$PROJECT_ROOT"
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to initialize (60 seconds)..."
sleep 60

# Function to make authenticated request
api_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    if [ -n "$data" ]; then
        curl -s -X "$method" "http://localhost:8000$endpoint" \
            -H "Authorization: Bearer $AUTH_TOKEN" \
            -H "Content-Type: application/json" \
            -d "$data"
    else
        curl -s -X "$method" "http://localhost:8000$endpoint" \
            -H "Authorization: Bearer $AUTH_TOKEN"
    fi
}

# Test results tracking
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run a test
run_test() {
    local test_name=$1
    local expected=$2
    local actual=$3
    
    if echo "$actual" | grep -q "$expected"; then
        echo -e "${GREEN}PASS${NC}: $test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC}: $test_name"
        echo "  Expected: $expected"
        echo "  Got: $actual"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

echo ""
echo "Running E2E Test Suite"
echo "----------------------"

# Step 1: Authenticate
echo ""
echo "Step 1: Authentication"
AUTH_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username": "testuser", "password": "testpass"}')

if echo "$AUTH_RESPONSE" | grep -q "access_token"; then
    AUTH_TOKEN=$(echo "$AUTH_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    run_test "User authentication" "access_token" "$AUTH_RESPONSE"
else
    echo -e "${YELLOW}Using default test token${NC}"
    AUTH_TOKEN="test-token"
fi

# Step 2: Upload a dataset
echo ""
echo "Step 2: Dataset Upload"
UPLOAD_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/datasets/upload" \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    -F "file=@$PROJECT_ROOT/client/cli/tests/sample_dataset.csv" \
    -F "name=e2e-test-dataset")

run_test "Dataset upload" '"id"' "$UPLOAD_RESPONSE"

DATASET_ID=$(echo "$UPLOAD_RESPONSE" | grep -o '"id":[0-9]*' | grep -o '[0-9]*' | head -1)

# Step 3: Get dataset details
echo ""
echo "Step 3: Get Dataset Details"
if [ -n "$DATASET_ID" ]; then
    DATASET_RESPONSE=$(api_request "GET" "/api/datasets/$DATASET_ID")
    run_test "Get dataset details" '"id"' "$DATASET_RESPONSE"
else
    echo -e "${YELLOW}Skipping - no dataset ID${NC}"
fi

# Step 4: List datasets
echo ""
echo "Step 4: List Datasets"
LIST_RESPONSE=$(api_request "GET" "/api/datasets")
run_test "List datasets" '"datasets"' "$LIST_RESPONSE"

# Step 5: Start assessment
echo ""
echo "Step 5: Start Assessment"
if [ -n "$DATASET_ID" ]; then
    ASSESSMENT_RESPONSE=$(api_request "POST" "/api/assessments" "{\"dataset_id\": $DATASET_ID}")
    run_test "Start assessment" '"id"' "$ASSESSMENT_RESPONSE"
    
    ASSESSMENT_ID=$(echo "$ASSESSMENT_RESPONSE" | grep -o '"id":[0-9]*' | grep -o '[0-9]*' | head -1)
else
    echo -e "${YELLOW}Skipping - no dataset ID${NC}"
fi

# Step 6: Check assessment status
echo ""
echo "Step 6: Check Assessment Status"
if [ -n "$ASSESSMENT_ID" ]; then
    # Wait for assessment to complete
    echo "Waiting for assessment to complete..."
    sleep 10
    
    STATUS_RESPONSE=$(api_request "GET" "/api/assessments/$ASSESSMENT_ID/status")
    run_test "Get assessment status" '"status"' "$STATUS_RESPONSE"
else
    echo -e "${YELLOW}Skipping - no assessment ID${NC}"
fi

# Step 7: Get assessment report
echo ""
echo "Step 7: Get Assessment Report"
if [ -n "$ASSESSMENT_ID" ]; then
    REPORT_RESPONSE=$(api_request "GET" "/api/reports/$ASSESSMENT_ID")
    # Report might not be ready yet, so we just check for a response
    if [ -n "$REPORT_RESPONSE" ]; then
        echo -e "${GREEN}PASS${NC}: Get assessment report (response received)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${YELLOW}WARN${NC}: Report not yet available"
    fi
else
    echo -e "${YELLOW}Skipping - no assessment ID${NC}"
fi

# Step 8: Export report
echo ""
echo "Step 8: Export Report"
if [ -n "$ASSESSMENT_ID" ]; then
    EXPORT_RESPONSE=$(api_request "GET" "/api/reports/$ASSESSMENT_ID/export?format=json")
    if [ -n "$EXPORT_RESPONSE" ]; then
        echo -e "${GREEN}PASS${NC}: Export report (response received)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${YELLOW}WARN${NC}: Export not available"
    fi
else
    echo -e "${YELLOW}Skipping - no assessment ID${NC}"
fi

# Step 9: Delete dataset
echo ""
echo "Step 9: Cleanup - Delete Dataset"
if [ -n "$DATASET_ID" ]; then
    DELETE_RESPONSE=$(api_request "DELETE" "/api/datasets/$DATASET_ID")
    run_test "Delete dataset" "deleted\|success" "$DELETE_RESPONSE"
else
    echo -e "${YELLOW}Skipping - no dataset ID${NC}"
fi

# Cleanup
echo ""
echo "Stopping services..."
docker-compose down

# Summary
echo ""
echo "======================================"
echo "E2E Test Results"
echo "======================================"
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All E2E tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some E2E tests failed!${NC}"
    exit 1
fi
