# Frequently Asked Questions

## General Questions

### What is DataAptor AI?

DataAptor AI is a comprehensive platform for assessing the AI readiness of datasets. It evaluates datasets across five key dimensions: Data Quality, Accessibility, Governance, AI Compatibility, and Diversity/Bias, providing a score from 0-100 that indicates how suitable a dataset is for AI/ML workflows.

### What file formats are supported?

DataAptor AI supports a wide range of file formats:

- **Structured data**: CSV, Excel (.xlsx, .xls), SQL databases
- **Semi-structured data**: JSON, XML, YAML
- **Unstructured data**: Text files, PDF documents
- **Media files**: Images (JPEG, PNG, TIFF), Audio (WAV, MP3)

### How long does an assessment take?

Assessment time depends on the dataset size and complexity:

- Small datasets (<10MB): 1-2 minutes
- Medium datasets (10-100MB): 2-5 minutes
- Large datasets (100MB-1GB): 5-15 minutes
- Very large datasets (>1GB): 15-60 minutes

You can monitor progress in real-time through the Web UI or CLI.

## Installation & Setup

### What are the system requirements?

**Minimum requirements:**
- 4 CPU cores
- 8GB RAM
- 20GB disk space
- Docker 20.10+
- Docker Compose 2.0+

**Recommended for production:**
- 8+ CPU cores
- 16GB+ RAM
- 100GB+ SSD storage
- Kubernetes 1.24+

### How do I install DataAptor AI?

See the [Installation Guide](../user-guides/installation.md) for detailed instructions. The quickest way is using Docker Compose:

```bash
git clone https://github.com/AneeshPulukkul/data-aptor-ai.git
cd data-aptor-ai
cp .env.example .env
# Edit .env with your settings
docker-compose up -d
```

### Why won't the services start?

Common causes and solutions:

1. **Port conflicts**: Check if ports 3000, 8000-8005, 5432, 9000-9001 are available
2. **Docker not running**: Ensure Docker daemon is running
3. **Insufficient memory**: Increase Docker memory allocation to at least 8GB
4. **Missing .env file**: Copy `.env.example` to `.env` and configure

Check logs for specific errors:
```bash
docker-compose logs -f [service-name]
```

### How do I reset everything and start fresh?

```bash
# Stop all services and remove volumes
docker-compose down -v

# Remove all images (optional)
docker-compose down --rmi all

# Start fresh
docker-compose up -d
```

## Assessment Questions

### What do the readiness levels mean?

| Level | Score Range | Meaning |
|-------|-------------|---------|
| High | 80-100 | Dataset is ready for AI/ML with minimal preparation |
| Moderate | 60-79 | Dataset needs some improvements before use |
| Low | 40-59 | Significant work required to make dataset AI-ready |
| Not Ready | 0-39 | Major issues must be addressed before AI use |

### How are scores calculated?

The overall score is a weighted average of five module scores:

- **Data Quality** (40%): Completeness, accuracy, consistency, timeliness
- **Accessibility** (20%): Format compatibility, documentation, volume adequacy
- **Governance** (15%): Privacy/PII handling, licensing, compliance
- **AI Compatibility** (20%): Feature richness, labeling quality, preprocessing needs
- **Diversity/Bias** (5%): Representativeness, fairness metrics

See [Customizing Weights](../user-guides/customizing-weights.md) to adjust these weights.

### Can I run only specific assessment modules?

Yes, you can select which modules to run:

**CLI:**
```bash
dataaptor assess <dataset_id> --modules quality,accessibility
```

**API:**
```json
POST /api/assessments
{
  "dataset_id": 1,
  "modules": ["quality", "accessibility"]
}
```

### Why is my quality score low?

Common reasons for low quality scores:

1. **Missing values**: Fill or impute missing data
2. **Inconsistent formats**: Standardize date formats, units, etc.
3. **Outliers**: Review and handle extreme values
4. **Duplicate records**: Remove or deduplicate

See [Improving Readiness](../user-guides/improving-readiness.md) for detailed solutions.

### How do I improve my dataset's score?

1. Review the detailed findings in your assessment report
2. Address issues in priority order (critical → high → medium → low)
3. Re-run the assessment to verify improvements
4. Repeat until you reach your target score

See [Improving Readiness](../user-guides/improving-readiness.md) for specific strategies.

## API & Integration

### How do I authenticate with the API?

DataAptor AI uses JWT tokens for authentication:

```bash
# Get a token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "your-username", "password": "your-password"}'

# Use the token
curl http://localhost:8000/api/datasets \
  -H "Authorization: Bearer <your-token>"
```

See [Authentication Guide](../api/authentication.md) for details.

### What are the API rate limits?

Default rate limits:
- 100 requests per minute for authenticated users
- 10 requests per minute for unauthenticated requests
- File uploads limited to 1GB per file

Contact your administrator to adjust limits for your use case.

### Can I integrate with my ML pipeline?

Yes! DataAptor AI integrates with popular ML frameworks:

- **TensorFlow/Keras**: Use callbacks to validate data before training
- **PyTorch**: Integrate with DataLoader for automatic validation
- **scikit-learn**: Add to preprocessing pipelines
- **MLflow**: Use as a pre-training validation step

See [ML Pipeline Integration](../user-guides/tutorials/ml-pipeline-integration.md) for examples.

## Troubleshooting

### Assessment stuck at "Processing"

1. Check service health: `curl http://localhost:8003/health`
2. Review assessment service logs: `docker-compose logs assessment-service`
3. Verify the dataset file is accessible
4. Try restarting the assessment service

### "Connection refused" errors

1. Verify all services are running: `docker-compose ps`
2. Check if the service is healthy
3. Verify network connectivity between services
4. Check firewall rules

### Reports not generating

1. Verify the assessment completed successfully
2. Check reporting service health: `curl http://localhost:8005/health`
3. Review reporting service logs
4. Ensure sufficient disk space for report storage

### How do I get help?

1. Check this FAQ and the documentation
2. Search existing GitHub issues
3. Open a new issue with:
   - DataAptor AI version
   - Steps to reproduce
   - Error messages and logs
   - System information

## See Also

- [Quick Start Guide](../user-guides/quick-start.md)
- [Installation Guide](../user-guides/installation.md)
- [API Documentation](../api/README.md)
- [Troubleshooting Guide](../user-guides/installation.md#troubleshooting)
