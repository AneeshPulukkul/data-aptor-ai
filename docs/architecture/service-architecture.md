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
