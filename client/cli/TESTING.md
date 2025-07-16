# Manual Testing Instructions for DataAptor CLI

These instructions will guide you through manually testing the DataAptor CLI client without requiring the full backend infrastructure.

> **IMPORTANT NOTE**: If you encounter the error `No module named 'dataaptor'` when running the CLI, use the direct Python execution method (e.g., `python dataaptor.py` instead of `dataaptor`) for all commands shown in this guide. This is due to how Python searches for modules during development.

> **UPDATE (July 16, 2025)**: The latest version includes enhanced error handling, improved output formatting, and new commands for AI readiness assessment. The Web UI client is also now available as an alternative interface.

## Prerequisites

Before testing, ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package manager)

## Step 1: Install Dependencies

First, install all the required dependencies:

```bash
# Navigate to the CLI directory
cd client/cli

# Create a virtual environment (optional but recommended)
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/Mac:
# source .venv/bin/activate

# Install the required packages
pip install fastapi uvicorn python-multipart colorama tabulate click requests

# Install the CLI in development mode (Method 1 - Recommended)
# This runs the CLI directly using the main script
pip install -e .

# If you encounter "No module named 'dataaptor'" error, try these alternatives:
# Option 1: Make sure you're in the correct directory (client/cli folder)
# Option 2: Use the direct Python execution method:
python dataaptor.py --help
```

## Step 2: Run the Mock API Server

The mock API server simulates the backend services needed by the CLI:

```bash
# From the CLI directory
python tests/mock_api_server.py
```

This will start a server at http://localhost:8000 that responds to all the API endpoints the CLI uses.

## Step 3: Test the CLI Commands (in a new terminal window)

Now you can test the CLI commands. Here are the key commands to test:

### Check if CLI is installed correctly
```bash
# If installation with pip install -e . worked:
dataaptor --help

# Alternative if you get "No module named 'dataaptor'" error:
python dataaptor.py --help
```

### Configure the CLI
```bash
# Standard command:
dataaptor config --list

# Alternative using direct Python execution:
python dataaptor.py config --list

# Set the API URL to the mock server
dataaptor config --set api_url --value http://localhost:8000
# OR
python dataaptor.py config --set api_url --value http://localhost:8000
```

### Upload a Dataset
```bash
# Upload the sample dataset
dataaptor upload tests/sample_dataset.csv
```
This will return a dataset ID. Note it down for subsequent commands.

### List Datasets
```bash
dataaptor list
```

### Get Dataset Details
```bash
# Replace 1 with your actual dataset ID
dataaptor info 1
```

### Trigger an Assessment
```bash
# Replace 1 with your actual dataset ID
dataaptor assess 1 --no-wait
```
This will return an assessment ID. Note it down for subsequent commands.

### Check Assessment Status
```bash
# Replace 1 with your actual assessment ID
dataaptor status 1
```

### List Assessments
```bash
dataaptor assessments
```

### View Assessment Report
```bash
# Replace 1 with your actual assessment ID
dataaptor report 1
```

### Export Assessment Report
```bash
# Replace 1 with your actual assessment ID
dataaptor export 1 --format pdf
dataaptor export 1 --format json --output ./my_report.json
```

### Delete a Dataset
```bash
# Replace 1 with your actual dataset ID
dataaptor delete 1 --force
```

## Step 4: Try Different Output Formats

You can change the output format for any command:

```bash
# JSON output
dataaptor list --output json

# CSV output
dataaptor list --output csv
```

## Troubleshooting

### Common Issues

#### ModuleNotFoundError: No module named 'dataaptor'

This error occurs when Python can't find the dataaptor module. There are several ways to fix this:

1. **Use direct Python execution:**
   ```bash
   # Instead of running 'dataaptor command'
   python dataaptor.py command
   ```

2. **Check your current directory:**
   Make sure you are in the `client/cli` directory when installing or running the CLI.

3. **Check installation:**
   ```bash
   # Reinstall the package
   pip uninstall dataaptor
   pip install -e .
   ```

4. **Check Python path:**
   The CLI adds its directory to the Python path in dataaptor.py, but this only works when running the script directly.

5. **Check virtual environment:**
   Make sure you're using the same virtual environment where you installed the CLI.

#### API Connection Issues

If you have trouble connecting to the API:

1. **Check that the mock API server is running**
2. **Verify the API URL**:
   ```bash
   dataaptor config --get api_url
   # or
   python dataaptor.py config --get api_url
   ```
3. **Set a different API URL if needed**:
   ```bash
   dataaptor config --set api_url --value http://localhost:8000
   # or
   python dataaptor.py config --set api_url --value http://localhost:8000
   ```

## Sample Testing Workflow

Here's a complete test workflow:

1. Start the mock server
2. Configure the CLI to use the mock server
3. Upload a sample dataset
4. Trigger an assessment
5. Check the assessment status
6. View and export the assessment report
7. Delete the dataset

This allows you to test the complete lifecycle of the CLI without needing the full backend services.

## Technical Details

### CLI Structure

The CLI client is structured as follows:

- `dataaptor.py`: Main entry point with Click command definitions
- `src/api_client.py`: API client for communicating with the backend
- `src/commands.py`: Command implementations
- `src/utils.py`: Utility functions for formatting and display
- `tests/mock_api_server.py`: Mock API server for testing
- `setup.py`: Package installation configuration

### How CLI Entry Points Work

The CLI uses Click and setuptools' entry points mechanism for installation:

1. `setup.py` defines an entry point: `dataaptor=dataaptor:cli`
2. This means when you run `dataaptor`, Python should run the `cli` function in the `dataaptor` module
3. The ModuleNotFoundError happens when Python can't find the `dataaptor` module in the Python path

### Direct Execution vs Entry Points

There are two ways to run the CLI:

1. **Entry Point (installed mode)**:
   ```bash
   dataaptor command
   ```
   This requires proper installation via pip.

2. **Direct Execution**:
   ```bash
   python dataaptor.py command
   ```
   This runs the script directly and is more reliable during development.

When you're developing or if you encounter module import issues, the direct execution method is recommended.
