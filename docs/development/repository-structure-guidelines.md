# Repository Structure Guidelines

This document outlines the recommended patterns and best practices for organizing code and resources within the DataAptor AI repository.

## Directory Naming Conventions

- Use lowercase, hyphenated names for directories (e.g., `data-quality`, not `DataQuality` or `data_quality`)
- Service directories should have descriptive names that reflect their functionality (e.g., `ingestion-service`)
- Common modules should be grouped logically (e.g., `utils`, `models`)

## File Organization

### Service Structure

Each microservice should follow a consistent structure:

```
service-name/
├── src/                   # Source code
│   ├── main.py            # Entry point
│   ├── api/               # API endpoints
│   ├── core/              # Core business logic
│   ├── models/            # Data models
│   └── utils/             # Utility functions
├── tests/                 # Service-specific tests
├── Dockerfile             # Container definition
├── requirements.txt       # Python dependencies
└── README.md              # Service documentation
```

### Component Structure

React components in the web UI should follow this structure:

```
components/
├── ComponentName/
│   ├── index.tsx          # Component implementation
│   ├── styles.css         # Component styles (if not using Tailwind)
│   └── ComponentName.test.tsx  # Component tests
```

## Documentation Standards

- Each service should have a README.md file explaining its purpose and functionality
- API endpoints should be documented with OpenAPI/Swagger
- Code should include docstrings and comments for non-obvious logic
- Architecture decisions should be documented in docs/architecture

## Adding New Services

When adding a new service to the DataAptor AI ecosystem:

1. Create a new directory following the service structure above
2. Update docker-compose.yml to include the new service
3. Update the orchestration service to interact with the new service
4. Add appropriate tests
5. Document the service in the relevant documentation files

## Common Patterns

### Configuration

- Use environment variables for configuration
- Provide sensible defaults in a `.env.example` file
- Document all configuration options

### Error Handling

- Use consistent error formats across all services
- Log errors with appropriate context
- Return meaningful error messages to clients

### Logging

- Use structured logging (JSON format)
- Include request IDs for tracing
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)

## Maintaining the Structure

- Regular code reviews should enforce structural consistency
- CI/CD pipelines should validate adherence to structure guidelines
- Update this document as patterns evolve
