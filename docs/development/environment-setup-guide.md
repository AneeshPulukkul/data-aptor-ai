# Development Environment Setup Guide

This guide provides step-by-step instructions for setting up the development environment for DataAptor AI.

## Prerequisites

Before starting, ensure you have the following installed:

- [Docker](https://www.docker.com/products/docker-desktop/) (version 20.10.0 or higher)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 2.0.0 or higher)
- [Python](https://www.python.org/downloads/) (version 3.10 or higher)
- [Node.js](https://nodejs.org/) (version 18.0.0 or higher)
- [npm](https://www.npmjs.com/) (version 9.0.0 or higher)
- [Git](https://git-scm.com/downloads) (version 2.30.0 or higher)

## Setting Up Local Development Environment

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/data-aptor-ai.git
cd data-aptor-ai
```

### 2. Environment Variables

Create a `.env` file in the root directory with the following variables:

```
# Database Configuration
POSTGRES_USER=dataaptor
POSTGRES_PASSWORD=yourpassword
POSTGRES_DB=dataaptor
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# MinIO Configuration
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_HOST=minio
MINIO_PORT=9000

# API Configuration
API_GATEWAY_PORT=8000
AUTH_SERVICE_PORT=8001
INGESTION_SERVICE_PORT=8002
ASSESSMENT_SERVICE_PORT=8003
SCORING_SERVICE_PORT=8004
REPORTING_SERVICE_PORT=8005

# Web UI Configuration
WEB_UI_PORT=3000

# JWT Configuration
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600
```

### 3. Start Docker Services

From the project root directory, run:

```bash
docker-compose up -d
```

This will start all the required services:
- PostgreSQL for metadata storage
- MinIO for object storage (S3-compatible)
- All microservices (as defined in docker-compose.yml)

### 4. Set Up Backend Services

For local development without Docker, you can set up the Python environment for each service:

```bash
# Navigate to the service directory (repeat for each service)
cd services/ingestion-service

# Create and activate a virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the service
uvicorn main:app --reload --port 8002
```

### 5. Set Up Frontend Development

```bash
# Navigate to the client directory
cd client

# Install dependencies
npm install

# Start the development server
npm run dev
```

## Database Setup

The PostgreSQL database will be initialized automatically by Docker Compose. However, you can manually set up the database schema using:

```bash
# Navigate to the scripts directory
cd scripts

# Run the database initialization script
python init_db.py
```

## Storage Setup

MinIO provides S3-compatible storage and will be initialized automatically by Docker Compose. The following buckets will be created:

- `datasets`: For storing uploaded datasets
- `reports`: For storing generated reports
- `visualizations`: For storing generated visualizations

## Testing the Setup

### 1. Verify API Gateway

Open your browser and navigate to:
```
http://localhost:8000/docs
```
You should see the Swagger UI documentation for the API Gateway.

### 2. Verify MinIO

Open your browser and navigate to:
```
http://localhost:9001
```
Log in with the credentials specified in the `.env` file.

### 3. Verify Frontend

Open your browser and navigate to:
```
http://localhost:3000
```
You should see the DataAptor AI web interface.

## Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Implement your feature
   - Write tests
   - Ensure all tests pass

3. **Submit a pull request**:
   - Push your changes to the remote repository
   - Create a pull request for review

## Troubleshooting

### Docker Issues

If you encounter issues with Docker services:

```bash
# Check the status of all containers
docker-compose ps

# View logs for a specific service
docker-compose logs <service-name>

# Restart a specific service
docker-compose restart <service-name>

# Rebuild a specific service
docker-compose up -d --build <service-name>
```

### Database Connection Issues

If you encounter issues connecting to the database:

```bash
# Check if the database container is running
docker-compose ps postgres

# Access the PostgreSQL CLI
docker-compose exec postgres psql -U dataaptor -d dataaptor
```

### API Connection Issues

If you encounter issues with the API services:

```bash
# Check if the service is running
docker-compose ps <service-name>

# View the service logs
docker-compose logs <service-name>

# Access the service container
docker-compose exec <service-name> /bin/bash
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/getting-started.html)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [MinIO Documentation](https://docs.min.io/)
