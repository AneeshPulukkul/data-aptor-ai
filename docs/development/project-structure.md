# Project Structure Documentation

This document provides a comprehensive overview of the DataAptor AI project structure and the purpose of each directory and key file.

## Directory Structure Overview

```
data-aptor-ai/
├── client/                          # Client Layer (Web UI + CLI)
├── api-gateway/                     # Application Layer - API Gateway (port 8000)
├── auth-service/                    # Application Layer - Keycloak config (port 8080)
├── orchestration-service/           # Application Layer - Orchestration Service (port 8001)
├── processing/                      # Processing Layer services
│   ├── ingestion-service/           # Data ingestion (port 8002)
│   ├── assessment-service/          # AI readiness assessment (port 8003)
│   ├── scoring-service/             # Scoring service (port 8004)
│   └── reporting-service/           # Reporting service (port 8005)
├── storage/                         # Data Storage Layer components
├── docs/                            # Documentation
├── scripts/                         # Utility scripts
├── .env.example                     # Environment variables template
├── .gitignore                       # Git ignore file
├── README.md                        # Project overview
├── LICENSE                          # License information
└── docker-compose.yml               # Docker Compose configuration
```

## Detailed Structure

### Client Layer (client/)

```
client/
├── public/                          # Static assets
│   └── index.html                   # SPA entry point
├── src/                             # React application source code
│   ├── assets/                      # Images, logos
│   ├── components/                  # Reusable UI components
│   │   ├── Alert.js                 # Notification component
│   │   ├── Button.js                # Interactive button
│   │   ├── Card.js                  # Container component
│   │   ├── LoadingSpinner.js        # Loading indicator
│   │   └── Navbar.js                # Navigation header
│   ├── pages/                       # Page components
│   │   ├── Dashboard.js             # Dataset overview
│   │   ├── Upload.js                # Dataset upload wizard
│   │   ├── Assessment.js            # Assessment configuration
│   │   └── Reports.js               # Report visualization
│   ├── services/
│   │   └── api.js                   # Centralized API client
│   ├── utils/
│   │   └── helpers.js               # Utility functions
│   └── mocks/                       # Development mock data
├── cli/                             # Python CLI tool
│   ├── dataaptor.py                 # CLI entry point (Click)
│   ├── src/                         # CLI source code
│   │   ├── api_client.py            # HTTP client for API
│   │   ├── commands.py              # CLI command implementations
│   │   └── utils.py                 # Output formatting
│   ├── tests/                       # CLI tests
│   └── run_tests.sh                 # Test runner
├── package.json                     # NPM dependencies
├── Dockerfile                       # Container definition
├── tailwind.config.js               # Tailwind CSS configuration
└── README.md                        # Web UI documentation
```

The client layer contains all user-facing interfaces:

- **Web UI**: React.js-based web application with Tailwind CSS and Chart.js for visualizations
- **CLI**: Python-based command-line interface using Click library for programmatic access

### Application Layer

#### API Gateway (api-gateway/)

```
api-gateway/
├── main.py                          # FastAPI application entry point
├── src/                             # Additional source code
├── tests/                           # Unit tests
├── Dockerfile                       # Container definition
└── requirements.txt                 # Python dependencies
```

The API Gateway service (using FastAPI) handles authentication, rate limiting, and routing of API requests to the appropriate microservices. It runs on port 8000.

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
├── main.py                          # FastAPI application entry point
├── src/                             # Additional source code
├── tests/                           # Unit tests
├── Dockerfile                       # Container definition
└── requirements.txt                 # Python dependencies
```

The Orchestration Service (using FastAPI) coordinates workflow management between services, handling user configurations and service coordination. It runs on port 8001.

### Processing Layer (processing/)

```
processing/
├── ingestion-service/               # Ingestion Service (port 8002)
│   ├── main.py                      # FastAPI application entry point
│   ├── processor.py                 # Data processing logic
│   ├── service.py                   # Service layer
│   ├── storage.py                   # Storage operations
│   ├── schemas.py                   # Pydantic models
│   ├── config.py                    # Configuration
│   ├── database.py                  # Database operations
│   ├── tests/                       # Unit tests
│   ├── Dockerfile                   # Container definition
│   └── requirements.txt             # Python dependencies
│
├── assessment-service/              # Assessment Service (port 8003)
│   ├── main.py                      # FastAPI application entry point
│   ├── tests/                       # Unit tests
│   ├── Dockerfile                   # Container definition
│   └── requirements.txt             # Python dependencies
│
├── scoring-service/                 # Scoring Service (port 8004)
│   ├── main.py                      # FastAPI application entry point
│   ├── tests/                       # Unit tests
│   ├── Dockerfile                   # Container definition
│   └── requirements.txt             # Python dependencies
│
└── reporting-service/               # Reporting Service (port 8005)
    ├── main.py                      # FastAPI application entry point
    ├── tests/                       # Unit tests
    ├── Dockerfile                   # Container definition
    └── requirements.txt             # Python dependencies
```

The Processing Layer contains the core services that perform dataset assessment:

- **ingestion-service/**: Handles file format validation, metadata extraction, and dataset storage management
- **assessment-service/**: Performs assessment across multiple dimensions (quality, accessibility, governance, AI compatibility, diversity)
- **scoring-service/**: Calculates AI readiness scores based on weighted criteria
- **reporting-service/**: Generates reports, visualizations, and recommendations

### Data Storage Layer (storage/)

```
storage/
└── metadata-db/                     # PostgreSQL database scripts
    └── init/                        # Initialization scripts
```

The Data Storage Layer manages persistent storage:

- **metadata-db/**: PostgreSQL database initialization scripts for metadata, assessment results, and user configurations
- **MinIO**: S3-compatible object storage for datasets and reports (configured in docker-compose.yml)

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

### Scripts (scripts/)

```
scripts/
├── init_db.py                       # Database initialization (Python)
├── init_db.sh                       # Database initialization (Shell)
├── build_images.sh                  # Build Docker images
├── deploy_to_k8s.sh                 # Deploy to Kubernetes
├── run_unit_tests.sh                # Run unit tests
├── run_integration_tests.sh         # Run integration tests
└── run_e2e_tests.sh                 # Run end-to-end tests
```

The Scripts directory contains utility scripts for development and operations:

- **init_db**: Database initialization scripts
- **build_images.sh**: Build all Docker images
- **deploy_to_k8s.sh**: Deploy to Kubernetes cluster
- **run_*_tests.sh**: Test runner scripts

**Note:** Tests are located within each service directory (e.g., `api-gateway/tests/`, `processing/assessment-service/tests/`) rather than in a centralized `tests/` directory.

## Key Files

- **.env.example**: Environment variables template (copy to `.env` and configure)
- **.gitignore**: Specifies files to be ignored by Git
- **README.md**: Project overview and documentation
- **LICENSE**: MIT License
- **docker-compose.yml**: Docker Compose configuration for all services

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
