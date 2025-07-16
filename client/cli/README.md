# DataAptor AI CLI

A command-line interface for interacting with the DataAptor AI platform.

## Installation

```bash
# Install from the project directory
pip install -e .

# Or install directly from the repository
pip install git+https://github.com/AneeshPulukkul/data-aptor-ai.git#subdirectory=client/cli
```

## Configuration

The CLI will automatically create a configuration file at `~/.dataaptor/config.json` with default values. You can modify these values using the `config` command:

```bash
# View all configuration values
dataaptor config --list

# Set the API URL
dataaptor config --set api_url --value http://localhost:8000

# Get a specific configuration value
dataaptor config --get api_url
```

## Usage

### Uploading Datasets

```bash
# Upload a dataset file
dataaptor upload /path/to/dataset.csv
```

### Managing Datasets

```bash
# List all uploaded datasets
dataaptor list

# Get details for a specific dataset
dataaptor info 123

# Delete a dataset
dataaptor delete 123
```

### Running Assessments

```bash
# Trigger an assessment for a dataset
dataaptor assess 123

# Trigger an assessment with specific modules
dataaptor assess 123 --modules quality,accessibility

# Trigger an assessment without waiting for completion
dataaptor assess 123 --no-wait

# Check the status of an assessment
dataaptor status 456

# List all assessments
dataaptor assessments

# List assessments for a specific dataset
dataaptor assessments --dataset-id 123
```

### Viewing and Exporting Reports

```bash
# View the detailed assessment report
dataaptor report 456

# Export the assessment report as PDF (default)
dataaptor export 456

# Export the assessment report in a specific format
dataaptor export 456 --format html

# Export the assessment report to a specific file
dataaptor export 456 --format csv --output ./my_report.csv
```

### Output Formatting

You can control the output format globally or per command:

```bash
# Set the default output format to JSON
dataaptor config --set output_format --value json

# Override the output format for a specific command
dataaptor list --output json

# Available output formats
# - table (default): Formatted tables for human readability
# - json: JSON format for programmatic use
# - csv: CSV format for importing into spreadsheets
```

## Environment Variables

- `DATAAPTOR_API_URL`: The URL of the DataAptor AI API (default: http://localhost:8000)

## Development

### Prerequisites

- Python 3.8 or higher
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/AneeshPulukkul/data-aptor-ai.git
cd data-aptor-ai/client/cli

# Install dependencies
pip install -r requirements.txt

# Install the CLI in development mode
pip install -e .
```
