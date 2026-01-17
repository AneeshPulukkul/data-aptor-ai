# Quick Deployment Guide

This guide explains how to deploy DataAptor AI using Docker Compose.

## Prerequisites

- Docker 20.10 or later
- Docker Compose 2.0 or later
- At least 8GB RAM available
- At least 10GB disk space

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/AneeshPulukkul/data-aptor-ai.git
   cd data-aptor-ai
   ```

2. Start all services:
   ```bash
   docker-compose up -d
   ```

3. Wait for all services to be healthy (this may take 2-3 minutes on first run):
   ```bash
   docker-compose ps
   ```

4. Access the application:
   - Web UI: http://localhost:3000
   - API Gateway: http://localhost:8000
   - Keycloak Admin: http://localhost:8080 (admin/admin)
   - MinIO Console: http://localhost:9001 (minio/minio123)

## Default Credentials

### Keycloak Users (change passwords on first login)

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Administrator |
| analyst | analyst123 | Analyst |
| viewer | viewer123 | Viewer |

### Service Accounts

| Service | Username | Password |
|---------|----------|----------|
| Keycloak Admin | admin | admin |
| PostgreSQL | postgres | postgres |
| MinIO | minio | minio123 |

## Service Ports

| Service | Port | Description |
|---------|------|-------------|
| Web UI | 3000 | React frontend |
| API Gateway | 8000 | Main API entry point |
| Keycloak | 8080 | Authentication service |
| Orchestration | 8001 | Workflow coordination |
| Ingestion | 8002 | Dataset upload |
| Assessment | 8003 | AI readiness assessment |
| Scoring | 8004 | Score calculation |
| Reporting | 8005 | Report generation |
| PostgreSQL | 5432 | Database |
| MinIO | 9000/9001 | Object storage |

## Health Checks

All services include health checks. You can verify service health:

```bash
# Check all services
docker-compose ps

# Check individual service health
curl http://localhost:8000/health  # API Gateway
curl http://localhost:8001/health  # Orchestration
curl http://localhost:8002/health  # Ingestion
curl http://localhost:8003/health  # Assessment
curl http://localhost:8004/health  # Scoring
curl http://localhost:8005/health  # Reporting
```

## Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose down -v
```

## Troubleshooting

### Services not starting

Check the logs:
```bash
docker-compose logs -f [service-name]
```

### Database connection issues

Ensure PostgreSQL is healthy before other services start:
```bash
docker-compose logs postgres
```

### Authentication issues

1. Access Keycloak admin console at http://localhost:8080
2. Login with admin/admin
3. Select the "dataaptor" realm
4. Check user credentials and roles

## Production Deployment

For production deployments, you should:

1. Change all default passwords in docker-compose.yml
2. Update the JWT_SECRET environment variable
3. Configure proper SSL/TLS certificates
4. Set up proper backup for PostgreSQL and MinIO
5. Configure external DNS and load balancing
6. Review and adjust resource limits

See [Production Deployment Guide](production-deploy.md) for detailed instructions.
