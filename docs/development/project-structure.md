# Project Structure Documentation

This document provides a comprehensive overview of the DataAptor AI project structure and the purpose of each directory and key file.

## Directory Structure Overview

```
data-aptor-ai/
├── .github/                         # GitHub workflows and CI/CD configurations
├── client/                          # Client Layer components
├── api-gateway/                     # Application Layer - API Gateway
├── auth-service/                    # Application Layer - Authentication Service
├── orchestration-service/           # Application Layer - Orchestration Service
├── processing/                      # Processing Layer services
├── storage/                         # Data Storage Layer components
├── integrations/                    # External Integrations Layer
├── common/                          # Shared libraries and utilities
├── docs/                            # Documentation
├── tests/                           # Automated tests
├── deployment/                      # Deployment configurations
├── scripts/                         # Utility scripts
├── .gitignore                       # Git ignore file
├── README.md                        # Project overview
├── LICENSE                          # License information
└── docker-compose.yml               # Development environment setup
```

## Detailed Structure

### GitHub Workflows (.github/)

```
.github/
└── workflows/                       # CI/CD workflow definitions
```

This directory contains GitHub Actions workflow configurations for continuous integration and deployment processes.

### Client Layer (client/)

```
client/
├── web-ui/                          # React.js web interface
│   ├── public/                      # Static assets
│   ├── src/                         # Source code
│   │   ├── components/              # Reusable UI components
│   │   ├── pages/                   # Page components (Dashboard, Upload, Results)
│   │   ├── services/                # API client services
│   │   └── utils/                   # Utility functions
│   ├── package.json                 # Dependencies and scripts
│   └── README.md                    # Web UI documentation
│
└── cli/                             # Python CLI tool
    ├── src/                         # CLI source code
    ├── setup.py                     # Package installation
    └── README.md                    # CLI documentation
```

The client layer contains all user-facing interfaces:

- **web-ui/**: React.js-based web application with Tailwind CSS and Chart.js for visualizations
- **cli/**: Python-based command-line interface using Click library for programmatic access

### Application Layer

#### API Gateway (api-gateway/)

```
api-gateway/
├── src/                             # Gateway source code
│   ├── routes/                      # API route definitions
│   ├── middleware/                  # Authentication, rate limiting
│   └── utils/                       # Utility functions
├── Dockerfile                       # Container definition
├── requirements.txt                 # Python dependencies
└── README.md                        # Gateway documentation
```

The API Gateway service (using FastAPI) handles authentication, rate limiting, and routing of API requests to the appropriate microservices.

#### Authentication Service (auth-service/)

```
auth-service/
├── config/                          # Keycloak configuration
├── Dockerfile                       # Container definition
└── README.md                        # Auth service documentation
```

The Authentication Service (based on Keycloak) provides OAuth 2.0 and JWT-based authentication, user management, and role-based access control.

#### Orchestration Service (orchestration-service/)

```
orchestration-service/
├── src/                             # Service source code
│   ├── workflows/                   # Workflow definitions
│   ├── config/                      # Service configuration
│   └── utils/                       # Utility functions
├── Dockerfile                       # Container definition
├── requirements.txt                 # Python dependencies
└── README.md                        # Orchestration documentation
```

The Orchestration Service (using FastAPI) coordinates workflow management between services, handling user configurations and service coordination.

### Processing Layer (processing/)

```
processing/
├── ingestion-service/               # Ingestion Service
│   ├── src/                         # Service source code
│   │   ├── parsers/                 # Format-specific parsers
│   │   │   ├── structured/          # CSV, tabular parsers
│   │   │   ├── semi_structured/     # JSON, XML parsers
│   │   │   └── unstructured/        # Text, image, audio parsers
│   │   ├── validators/              # Data validation
│   │   └── utils/                   # Utility functions
│   ├── Dockerfile                   # Container definition
│   ├── requirements.txt             # Python dependencies
│   └── README.md                    # Ingestion documentation
│
├── assessment-service/              # Assessment Service
│   ├── src/                         # Service source code
│   │   ├── modules/                 # Assessment modules
│   │   │   ├── data_quality/        # Quality assessment
│   │   │   ├── accessibility/       # Accessibility assessment
│   │   │   ├── governance/          # Governance assessment
│   │   │   ├── ai_compatibility/    # AI compatibility assessment
│   │   │   └── diversity/           # Diversity assessment
│   │   └── utils/                   # Utility functions
│   ├── Dockerfile                   # Container definition
│   ├── requirements.txt             # Python dependencies
│   └── README.md                    # Assessment documentation
│
├── scoring-service/                 # Scoring Service
│   ├── src/                         # Service source code
│   │   ├── algorithms/              # Scoring algorithms
│   │   ├── weightings/              # Default and custom weightings
│   │   └── utils/                   # Utility functions
│   ├── Dockerfile                   # Container definition
│   ├── requirements.txt             # Python dependencies
│   └── README.md                    # Scoring documentation
│
└── reporting-service/               # Reporting Service
    ├── src/                         # Service source code
    │   ├── templates/               # Report templates
    │   ├── visualizations/          # Chart generation
    │   ├── recommendations/         # Recommendation engine
    │   └── utils/                   # Utility functions
    ├── Dockerfile                   # Container definition
    ├── requirements.txt             # Python dependencies
    └── README.md                    # Reporting documentation
```

The Processing Layer contains the core services that perform dataset assessment:

- **ingestion-service/**: Handles file format validation, metadata extraction, and dataset storage management
- **assessment-service/**: Performs assessment across multiple dimensions with specialized modules
- **scoring-service/**: Calculates AI readiness scores based on weighted criteria
- **reporting-service/**: Generates reports, visualizations, and recommendations

### Data Storage Layer (storage/)

```
storage/
├── metadata-db/                     # PostgreSQL database scripts
│   ├── migrations/                  # Schema migrations
│   ├── init/                        # Initialization scripts
│   └── README.md                    # Database documentation
│
└── storage-connectors/              # Storage service connectors
    ├── src/                         # Connector source code
    │   ├── temp_storage/            # Temporary storage
    │   └── report_storage/          # Report storage
    ├── Dockerfile                   # Container definition
    ├── requirements.txt             # Python dependencies
    └── README.md                    # Storage documentation
```

The Data Storage Layer manages persistent and temporary storage:

- **metadata-db/**: PostgreSQL database for metadata, assessment results, and user configurations
- **storage-connectors/**: Connectors for temporary dataset storage and report storage (using AWS S3 or compatible storage)

### External Integrations Layer (integrations/)

```
integrations/
├── cloud-storage/                   # Cloud storage connectors
│   ├── src/                         # Connector source code
│   ├── Dockerfile                   # Container definition
│   └── requirements.txt             # Python dependencies
│
├── databases/                       # Database connectors
│   ├── src/                         # Connector source code
│   ├── Dockerfile                   # Container definition
│   └── requirements.txt             # Python dependencies
│
├── ai-pipelines/                    # AI/ML pipeline integrations
│   ├── src/                         # Integration source code
│   ├── Dockerfile                   # Container definition
│   └── requirements.txt             # Python dependencies
│
└── external-apis/                   # External API integrations
    ├── src/                         # Integration source code
    ├── Dockerfile                   # Container definition
    └── requirements.txt             # Python dependencies
```

The External Integrations Layer provides connections to external systems:

- **cloud-storage/**: Connectors for AWS S3, Google Cloud Storage, Azure Blob Storage
- **databases/**: Connectors for external databases (MySQL, PostgreSQL, MongoDB)
- **ai-pipelines/**: Integrations with AI/ML pipelines (TensorFlow, PyTorch, SageMaker)
- **external-apis/**: RESTful API for external system access

### Common Libraries (common/)

```
common/
├── models/                          # Shared data models
├── utils/                           # Shared utility functions
└── constants/                       # Common constants and definitions
```

The Common directory contains shared code used across multiple services:

- **models/**: Shared data models and schemas
- **utils/**: Utility functions for logging, error handling, etc.
- **constants/**: Common constants and configurations

### Documentation (docs/)

```
docs/
├── architecture/                    # Architecture documentation
├── api/                             # API documentation
├── user-guides/                     # User guides
└── development/                     # Development guides
```

The Documentation directory contains comprehensive documentation for the project:

- **architecture/**: System architecture, component diagrams, and design decisions
- **api/**: API specifications, endpoints, and usage examples
- **user-guides/**: End-user documentation and tutorials
- **development/**: Developer guidelines and setup instructions

### Tests (tests/)

```
tests/
├── unit/                            # Unit tests
├── integration/                     # Integration tests
├── e2e/                             # End-to-end tests
└── performance/                     # Performance tests
```

The Tests directory contains automated tests for the application:

- **unit/**: Unit tests for individual components
- **integration/**: Tests for service interactions
- **e2e/**: End-to-end tests for complete workflows
- **performance/**: Performance and load testing

### Deployment (deployment/)

```
deployment/
├── kubernetes/                      # Kubernetes manifests
├── docker-compose/                  # Docker Compose files
└── terraform/                       # Infrastructure as Code
```

The Deployment directory contains configuration for deploying the application:

- **kubernetes/**: Kubernetes manifests for container orchestration
- **docker-compose/**: Docker Compose files for deployment scenarios
- **terraform/**: Infrastructure as Code for cloud provisioning

### Scripts (scripts/)

```
scripts/
├── setup/                           # Setup scripts
└── maintenance/                     # Maintenance scripts
```

The Scripts directory contains utility scripts for development and operations:

- **setup/**: Environment setup and initialization scripts
- **maintenance/**: Database maintenance, backups, and other operational tasks

## Key Files

- **.gitignore**: Specifies files to be ignored by Git
- **README.md**: Project overview and documentation
- **LICENSE**: MIT License
- **docker-compose.yml**: Development environment configuration

## Service Interaction

The DataAptor AI services interact in the following workflow:

1. The client (Web UI or CLI) sends a request to the API Gateway
2. The API Gateway authenticates the request via the Authentication Service
3. The Orchestration Service coordinates the assessment workflow
4. The Ingestion Service validates and stores the dataset
5. The Assessment Service analyzes the dataset across all metrics
6. The Scoring Service calculates the AI readiness score
7. The Reporting Service generates reports and recommendations
8. Results are returned to the client via the API Gateway

## Development Environment

The development environment is configured using Docker Compose, which sets up:

- All microservices with appropriate port mappings
- PostgreSQL database for metadata
- MinIO for S3-compatible storage
- Keycloak for authentication

## Production Deployment

For production, the application is designed to be deployed using Kubernetes, with:

- Horizontal scaling of services
- External managed databases
- Cloud storage integration
- CI/CD pipeline for automated deployment
