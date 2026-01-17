# Quick Start Guide

This guide will help you get started with DataAptor AI in just a few minutes.

## Prerequisites

Before you begin, ensure you have the following installed:

- Docker and Docker Compose (for running the platform)
- Python 3.9+ (for CLI usage)
- Node.js 18+ (for web UI development)

## Starting the Platform

The fastest way to get started is using Docker Compose:

```bash
# Clone the repository
git clone https://github.com/AneeshPulukkul/data-aptor-ai.git
cd data-aptor-ai

# Start all services
docker-compose up -d

# Wait for services to initialize (about 30 seconds)
sleep 30

# Verify services are running
curl http://localhost:8000/health
```

## Using the Web UI

Once the platform is running, open your browser and navigate to:

```
http://localhost:3000
```

From the web UI, you can:

1. **Upload a Dataset**: Click "Upload" and drag-and-drop your data file
2. **Start an Assessment**: Select your dataset and click "Assess"
3. **View Results**: Check the dashboard for your AI readiness score
4. **Export Reports**: Download reports in PDF, HTML, JSON, or CSV format

## Using the CLI

Install and configure the CLI tool:

```bash
# Navigate to CLI directory
cd client/cli

# Install dependencies
pip install -r requirements.txt

# Configure API endpoint
python dataaptor.py config --set api_url --value http://localhost:8000

# Upload a dataset
python dataaptor.py upload your_data.csv

# Start an assessment
python dataaptor.py assess <dataset_id>

# Check status
python dataaptor.py status <assessment_id>

# View report
python dataaptor.py report <assessment_id>
```

## Understanding Your Score

DataAptor AI evaluates datasets across five dimensions:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Quality | 40% | Completeness, accuracy, consistency, timeliness |
| Accessibility | 20% | Format compatibility, volume adequacy |
| Governance | 15% | Privacy compliance, licensing |
| AI Compatibility | 20% | Task relevance, labeling, features |
| Diversity | 5% | Representativeness, bias detection |

Your overall score (0-100) indicates AI readiness:

- **80-100**: High - Ready for AI/ML applications
- **60-79**: Moderate - Minor improvements needed
- **40-59**: Low - Significant work required
- **0-39**: Not Ready - Major issues to address

## Next Steps

- Read the [Installation Guide](installation.md) for detailed setup instructions
- Learn about [Dataset Assessment](dataset-assessment.md) in depth
- Explore [Report Interpretation](report-interpretation.md) to understand your results
- Check out [Tutorials](tutorials/) for hands-on examples

## Getting Help

If you encounter issues:

1. Check the [FAQ](../development/faq.md)
2. Review the [API Documentation](../api/README.md)
3. Open an issue on [GitHub](https://github.com/AneeshPulukkul/data-aptor-ai/issues)
