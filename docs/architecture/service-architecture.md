# DataAptor AI Service Architecture

This document outlines the architecture and relationships between services in the DataAptor AI platform.

## Service Map

```
                   ┌─────────────┐
                   │    Client   │
                   │  (Web/CLI)  │
                   └──────┬──────┘
                          │
                          ▼
                   ┌─────────────┐
                   │ API Gateway │
                   └──────┬──────┘
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
┌──────────────────┐             ┌─────────────────┐
│  Authentication  │◄────────────┤  Orchestration  │
│     Service      │             │     Service     │
└──────────────────┘             └────────┬────────┘
                                          │
                 ┌────────────────────────┼────────────────────────┐
                 ▼                        ▼                        ▼
        ┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐
        │    Ingestion    │────►│    Assessment    │────►│     Scoring      │
        │     Service     │     │     Service      │     │     Service      │
        └────────┬────────┘     └──────────────────┘     └─────────┬────────┘
                 │                                                  │
                 ▼                                                  ▼
        ┌─────────────────┐                                ┌──────────────────┐
        │    Temporary    │                                │    Reporting     │
        │     Storage     │                                │     Service      │
        └─────────────────┘                                └─────────┬────────┘
                                                                     │
                                                                     ▼
                                                           ┌──────────────────┐
                                                           │     Report       │
                                                           │     Storage      │
                                                           └──────────────────┘
```

## Service Responsibilities

### Client Layer

- **Web UI**: User interface for dataset upload, configuration, and results visualization
- **CLI**: Command-line interface for programmatic access

### Application Layer

- **API Gateway**: Entry point for all client requests, handles authentication, rate limiting, and routing
- **Authentication Service**: Manages user authentication, authorization, and role-based access control
- **Orchestration Service**: Coordinates workflow between services, manages state and configuration

### Processing Layer

- **Ingestion Service**: Validates dataset formats, extracts metadata, and manages dataset storage
- **Assessment Service**: Evaluates datasets across multiple criteria:
  - Data Quality (completeness, accuracy, consistency, timeliness)
  - Accessibility (availability, volume)
  - Governance (privacy, licensing)
  - AI Compatibility (relevance, labeling, feature richness, preprocessing)
  - Diversity/Bias (representativeness, diversity)
- **Scoring Service**: Calculates AI readiness scores based on weighted assessment criteria
- **Reporting Service**: Generates reports, visualizations, and actionable recommendations

### Data Storage Layer

- **Metadata Database**: Stores assessment results, user configurations, and system metadata
- **Temporary Storage**: Stores uploaded datasets during processing
- **Report Storage**: Stores generated reports and visualizations

## Service Interaction Workflows

### Dataset Assessment Workflow

1. **Client** uploads dataset via Web UI or CLI
2. **API Gateway** authenticates request and forwards to Orchestration Service
3. **Orchestration Service** triggers Ingestion Service
4. **Ingestion Service** validates dataset, stores in Temporary Storage, extracts metadata
5. **Orchestration Service** triggers Assessment Service modules
6. **Assessment Service** analyzes dataset across all metrics
7. **Assessment results** are forwarded to Scoring Service
8. **Scoring Service** calculates AI readiness score
9. **Scoring results** are forwarded to Reporting Service
10. **Reporting Service** generates reports and visualizations
11. **Reports** are stored in Report Storage
12. **Orchestration Service** notifies API Gateway
13. **API Gateway** returns results to Client

### Integration Workflow

1. **External system** authenticates with API Gateway
2. **API Gateway** validates request and forwards to Orchestration Service
3. **Orchestration Service** coordinates with relevant services
4. **Results** are returned to external system via API Gateway

## Service Communication

- **REST API**: Primary communication method between services
- **JWT**: Used for authentication between services
- **Event-based**: Optional publish/subscribe pattern for asynchronous processing

## Scaling Considerations

- **Horizontal Scaling**: All services can be horizontally scaled via containerization
- **Statelessness**: Services are designed to be stateless for easy scaling
- **Database Scaling**: Metadata DB can be scaled via sharding or read replicas
- **Storage Scaling**: S3-compatible storage scales automatically

## Security Considerations

- **Authentication**: OAuth 2.0 and JWT for secure authentication
- **Authorization**: Role-based access control for fine-grained permissions
- **Encryption**: TLS for all service communication, encryption at rest for data
- **PII Detection**: Automatic detection and handling of sensitive information

## Deployment Configuration

### Service Ports

| Service | Port | Health Check Endpoint |
|---------|------|----------------------|
| Web UI | 3000 | `http://localhost:3000/` |
| API Gateway | 8000 | `http://localhost:8000/health` |
| Keycloak (Auth) | 8080 | `http://localhost:8080/health/ready` |
| Orchestration Service | 8001 | `http://localhost:8001/health` |
| Ingestion Service | 8002 | `http://localhost:8002/health` |
| Assessment Service | 8003 | `http://localhost:8003/health` |
| Scoring Service | 8004 | `http://localhost:8004/health` |
| Reporting Service | 8005 | `http://localhost:8005/health` |
| PostgreSQL | 5432 | `pg_isready` |
| MinIO (S3) | 9000, 9001 | `http://localhost:9000/minio/health/live` |

### Docker Compose Deployment

The platform is deployed using Docker Compose with health checks and proper service dependencies:

```bash
# Quick start
cp .env.example .env
# Edit .env with your settings
docker-compose up -d
```

Services start in the following order based on health check dependencies:
1. PostgreSQL and MinIO (storage layer)
2. Keycloak (authentication)
3. Processing services (Ingestion, Assessment, Scoring, Reporting)
4. Orchestration Service
5. API Gateway
6. Web UI

### Environment Configuration

All services use environment variables for configuration. See `.env.example` for the full list of configurable options:

- **Database**: `POSTGRES_*` variables for PostgreSQL connection
- **Authentication**: `KEYCLOAK_*` and `KC_*` variables for Keycloak
- **Storage**: `MINIO_*` variables for object storage
- **Security**: `JWT_SECRET` for API authentication

### Storage Layer

- **PostgreSQL**: Metadata database for datasets, assessments, scores, and reports
- **MinIO**: S3-compatible object storage for dataset files and generated reports (can be replaced with AWS S3, GCS, or Azure Blob in production)

## Related Documentation

- [Quick Deploy Guide](../deployment/quick-deploy.md) - Local development deployment
- [Production Deployment Guide](../deployment/production-deploy.md) - Production deployment
- [API Documentation](../api/README.md) - API reference
