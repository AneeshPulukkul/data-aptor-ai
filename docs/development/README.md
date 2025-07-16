# Development Guide

This guide provides instructions for setting up the DataAptor AI development environment and contributing to the project.

## Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Node.js 14+
- PostgreSQL (for local development without Docker)
- AWS CLI (for S3 integration testing)

## Setup

1. Clone the repository
   ```bash
   git clone https://github.com/AneeshPulukkul/data-aptor-ai.git
   cd data-aptor-ai
   ```

2. Start the development environment
   ```bash
   docker-compose up -d
   ```

3. Access the services
   - Web UI: http://localhost:3000
   - API Gateway: http://localhost:8000/docs
   - Keycloak Admin: http://localhost:8080/admin

## Development Workflow

1. Branch from main for new features
2. Follow the code style guidelines below
3. Write tests for new functionality
4. Submit pull requests with appropriate descriptions

## Project Structure

For a detailed understanding of the project structure, please refer to the [Project Structure Documentation](project-structure.md).

## Code Style Guidelines

### Python

- Follow PEP 8 style guide
- Use type hints
- Document functions and classes with docstrings
- Use pytest for testing

### JavaScript/React

- Follow ESLint configuration
- Use functional components with hooks
- Use TypeScript for type safety
- Use Jest for testing

## Testing

- Run unit tests: `scripts/run_unit_tests.sh`
- Run integration tests: `scripts/run_integration_tests.sh`
- Run end-to-end tests: `scripts/run_e2e_tests.sh`

## Building for Production

- Build Docker images: `scripts/build_images.sh`
- Deploy to Kubernetes: `scripts/deploy_to_k8s.sh`

## Microservices Development

Each microservice has its own directory with a README.md file containing service-specific development instructions.

## Contributing

Please see the [Contributing Guide](CONTRIBUTING.md) for details on how to contribute to the project.
