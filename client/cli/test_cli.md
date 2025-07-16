# DataAptor CLI Testing Guide

This script will guide you through testing the DataAptor CLI locally. Run each command step-by-step to test different aspects of the CLI.

## Prerequisites

1. The API Gateway should be running locally (or accessible at the configured URL)
2. The CLI should be installed in development mode using `pip install -e .`

## Test Commands

### 1. Check CLI Help

```bash
dataaptor --help
```

This should display all available commands and options.

### 2. Configure CLI

```bash
# View current configuration
dataaptor config --list

# Set API URL (if needed)
dataaptor config --set api_url --value http://localhost:8000
```

### 3. Upload Dataset

```bash
# Upload the sample dataset
dataaptor upload tests/sample_dataset.csv
```

This should return a dataset ID, which you'll use in subsequent commands. Make note of it.

### 4. List Datasets

```bash
# List all uploaded datasets
dataaptor list
```

### 5. Get Dataset Details

```bash
# Replace 123 with the actual dataset ID from step 3
dataaptor info 123
```

### 6. Trigger Assessment

```bash
# Replace 123 with the actual dataset ID from step 3
dataaptor assess 123

# For a non-blocking assessment
dataaptor assess 123 --no-wait

# To specify modules
dataaptor assess 123 --modules quality,accessibility
```

### 7. Check Assessment Status

```bash
# Replace 456 with the actual assessment ID from step 6
dataaptor status 456
```

### 8. List Assessments

```bash
# List all assessments
dataaptor assessments

# List assessments for a specific dataset
dataaptor assessments --dataset-id 123
```

### 9. View Assessment Report

```bash
# Replace 456 with the actual assessment ID from step 6
dataaptor report 456
```

### 10. Export Assessment Report

```bash
# Replace 456 with the actual assessment ID from step 6
dataaptor export 456 --format pdf

# Export to different formats
dataaptor export 456 --format html
dataaptor export 456 --format json
dataaptor export 456 --format csv

# Export to a specific file
dataaptor export 456 --format csv --output ./my_report.csv
```

### 11. Delete Dataset

```bash
# Replace 123 with the actual dataset ID
dataaptor delete 123
```

## Output Format Options

You can change the output format for any command:

```bash
# JSON output
dataaptor list --output json

# CSV output
dataaptor list --output csv

# Table output (default)
dataaptor list --output table
```

## Troubleshooting

If you encounter errors:

1. Ensure the API Gateway is running
2. Check the API URL configuration: `dataaptor config --get api_url`
3. Look for error messages in the command output
4. Check the server logs for API-related issues
