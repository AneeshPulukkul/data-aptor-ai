# Installation Guide

This guide provides detailed instructions for installing and configuring DataAptor AI.

## System Requirements

### Minimum Requirements

- **CPU**: 4 cores
- **RAM**: 8 GB
- **Storage**: 20 GB available space
- **OS**: Linux (Ubuntu 20.04+), macOS 12+, or Windows 10+ with WSL2

### Recommended Requirements

- **CPU**: 8+ cores
- **RAM**: 16+ GB
- **Storage**: 50+ GB SSD
- **OS**: Linux (Ubuntu 22.04)

## Installation Methods

### Method 1: Docker Compose (Recommended)

This is the easiest way to get started with all services.

```bash
# Clone the repository
git clone https://github.com/AneeshPulukkul/data-aptor-ai.git
cd data-aptor-ai

# Start all services
docker-compose up -d

# Verify installation
docker-compose ps
```

Services will be available at:

| Service | URL |
|---------|-----|
| Web UI | http://localhost:3000 |
| API Gateway | http://localhost:8000 |
| Orchestration | http://localhost:8001 |
| Ingestion | http://localhost:8002 |
| Assessment | http://localhost:8003 |
| Scoring | http://localhost:8004 |
| Reporting | http://localhost:8005 |
| MinIO Console | http://localhost:9001 |

### Method 2: Kubernetes Deployment

For production environments, use Kubernetes:

```bash
# Build Docker images
./scripts/build_images.sh --registry your-registry.com

# Deploy to Kubernetes
./scripts/deploy_to_k8s.sh \
    --namespace dataaptor \
    --registry your-registry.com \
    --environment production
```

### Method 3: Local Development Setup

For development and testing:

#### Backend Services

```bash
# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies for each service
cd processing/ingestion-service
pip install -r requirements.txt

# Start the service
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

#### Web UI

```bash
cd client
npm install
npm start
```

#### CLI Tool

```bash
cd client/cli
pip install -r requirements.txt
python dataaptor.py --help
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=dataaptor
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password

# MinIO Configuration
MINIO_HOST=localhost
MINIO_PORT=9000
MINIO_ROOT_USER=minio
MINIO_ROOT_PASSWORD=your_secure_password

# JWT Configuration
JWT_SECRET=your_jwt_secret_key
JWT_ALGORITHM=HS256

# Service URLs (for inter-service communication)
INGESTION_SERVICE_URL=http://localhost:8002
ASSESSMENT_SERVICE_URL=http://localhost:8003
SCORING_SERVICE_URL=http://localhost:8004
REPORTING_SERVICE_URL=http://localhost:8005
```

### Database Initialization

The database is automatically initialized when using Docker Compose. For manual setup:

```bash
# Connect to PostgreSQL
psql -h localhost -U postgres

# Create database
CREATE DATABASE dataaptor;

# Run initialization script
psql -h localhost -U postgres -d dataaptor -f storage/metadata-db/init/01_init.sql
```

## Verification

After installation, verify all services are running:

```bash
# Check all health endpoints
curl http://localhost:8000/health  # API Gateway
curl http://localhost:8001/health  # Orchestration
curl http://localhost:8002/health  # Ingestion
curl http://localhost:8003/health  # Assessment
curl http://localhost:8004/health  # Scoring
curl http://localhost:8005/health  # Reporting
```

## Troubleshooting

### Common Issues

**Services fail to start**

Check Docker logs:
```bash
docker-compose logs -f <service-name>
```

**Database connection errors**

Ensure PostgreSQL is running and credentials are correct:
```bash
docker-compose logs postgres
```

**Port conflicts**

If ports are already in use, modify `docker-compose.yml` to use different ports.

### Getting Help

- Check the [FAQ](../development/faq.md)
- Review [GitHub Issues](https://github.com/AneeshPulukkul/data-aptor-ai/issues)
- Join our community discussions

## Next Steps

- Follow the [Quick Start Guide](quick-start.md)
- Learn about [Dataset Assessment](dataset-assessment.md)
- Explore the [API Documentation](../api/README.md)
