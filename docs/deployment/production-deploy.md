# Production Deployment Guide

This guide covers deploying DataAptor AI to a production environment.

## Prerequisites

- Kubernetes cluster (1.24+) or Docker Swarm
- PostgreSQL 14+ (managed service recommended)
- S3-compatible object storage (AWS S3, MinIO, etc.)
- Domain name with SSL certificate
- Load balancer (AWS ALB, nginx, etc.)

## Security Checklist

Before deploying to production, ensure you have:

- [ ] Changed all default passwords
- [ ] Generated secure JWT secrets (minimum 32 characters)
- [ ] Configured SSL/TLS certificates
- [ ] Set up network policies to restrict service communication
- [ ] Enabled audit logging
- [ ] Configured backup procedures for PostgreSQL and object storage
- [ ] Set up monitoring and alerting

## Environment Configuration

### Required Environment Variables

Create a `.env` file with production values:

```bash
# Database
POSTGRES_HOST=your-postgres-host.rds.amazonaws.com
POSTGRES_DB=dataaptor
POSTGRES_USER=dataaptor_user
POSTGRES_PASSWORD=<secure-password>

# Authentication
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=<secure-admin-password>
KC_DB_USERNAME=keycloak_user
KC_DB_PASSWORD=<secure-keycloak-password>
JWT_SECRET=<secure-jwt-secret-minimum-32-characters>

# Object Storage
MINIO_ROOT_USER=<access-key>
MINIO_ROOT_PASSWORD=<secret-key>
S3_ENDPOINT=https://s3.amazonaws.com
S3_BUCKET=dataaptor-storage

# Application
NODE_ENV=production
API_URL=https://api.yourdomain.com
```

### Secrets Management

For production, use a secrets manager instead of environment files:

- **AWS**: AWS Secrets Manager or Parameter Store
- **GCP**: Google Secret Manager
- **Azure**: Azure Key Vault
- **Kubernetes**: External Secrets Operator or Sealed Secrets

## Kubernetes Deployment

### 1. Create Namespace

```bash
kubectl create namespace dataaptor
```

### 2. Create Secrets

```bash
kubectl create secret generic dataaptor-secrets \
  --from-literal=postgres-password=<password> \
  --from-literal=jwt-secret=<secret> \
  --from-literal=keycloak-admin-password=<password> \
  -n dataaptor
```

### 3. Deploy Services

```bash
# Apply configurations
kubectl apply -f deployment/k8s/configmaps.yaml -n dataaptor
kubectl apply -f deployment/k8s/services.yaml -n dataaptor
kubectl apply -f deployment/k8s/deployments.yaml -n dataaptor
kubectl apply -f deployment/k8s/ingress.yaml -n dataaptor
```

### 4. Configure Ingress

Example nginx ingress configuration:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: dataaptor-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
    - hosts:
        - api.yourdomain.com
        - app.yourdomain.com
      secretName: dataaptor-tls
  rules:
    - host: api.yourdomain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: api-gateway
                port:
                  number: 8000
    - host: app.yourdomain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: web-ui
                port:
                  number: 80
```

## Docker Swarm Deployment

### 1. Initialize Swarm

```bash
docker swarm init
```

### 2. Create Secrets

```bash
echo "<password>" | docker secret create postgres_password -
echo "<secret>" | docker secret create jwt_secret -
```

### 3. Deploy Stack

```bash
docker stack deploy -c docker-compose.prod.yml dataaptor
```

## Database Setup

### PostgreSQL Configuration

For production PostgreSQL:

```sql
-- Create databases
CREATE DATABASE dataaptor;
CREATE DATABASE keycloak;

-- Create users with limited privileges
CREATE USER dataaptor_user WITH ENCRYPTED PASSWORD '<password>';
GRANT ALL PRIVILEGES ON DATABASE dataaptor TO dataaptor_user;

CREATE USER keycloak_user WITH ENCRYPTED PASSWORD '<password>';
GRANT ALL PRIVILEGES ON DATABASE keycloak TO keycloak_user;
```

### Connection Pooling

Use PgBouncer or similar for connection pooling:

```ini
[databases]
dataaptor = host=postgres port=5432 dbname=dataaptor

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
```

## Monitoring

### Health Checks

All services expose `/health` endpoints:

```bash
# Check all services
for service in api-gateway orchestration ingestion assessment scoring reporting; do
  curl -s https://api.yourdomain.com/$service/health
done
```

### Prometheus Metrics

Services expose metrics at `/metrics` (when enabled):

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'dataaptor'
    static_configs:
      - targets:
          - 'api-gateway:8000'
          - 'orchestration-service:8001'
          - 'ingestion-service:8002'
          - 'assessment-service:8003'
          - 'scoring-service:8004'
          - 'reporting-service:8005'
```

### Logging

Configure centralized logging with ELK stack or similar:

```yaml
# filebeat.yml
filebeat.inputs:
  - type: container
    paths:
      - '/var/lib/docker/containers/*/*.log'
    processors:
      - add_kubernetes_metadata:
          host: ${NODE_NAME}
          matchers:
            - logs_path:
                logs_path: "/var/lib/docker/containers/"
```

## Backup and Recovery

### PostgreSQL Backups

```bash
# Daily backup script
pg_dump -h $POSTGRES_HOST -U $POSTGRES_USER -d dataaptor | gzip > backup_$(date +%Y%m%d).sql.gz

# Upload to S3
aws s3 cp backup_$(date +%Y%m%d).sql.gz s3://dataaptor-backups/
```

### Object Storage Backups

Use S3 versioning and cross-region replication for object storage backups.

## Scaling

### Horizontal Pod Autoscaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-gateway-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

## Troubleshooting

### Common Issues

1. **Services not starting**: Check health check endpoints and database connectivity
2. **Authentication failures**: Verify Keycloak realm configuration and JWT secrets
3. **Slow assessments**: Check resource limits and consider scaling assessment service
4. **Storage errors**: Verify S3 credentials and bucket permissions

### Debug Mode

Enable debug logging temporarily:

```bash
kubectl set env deployment/api-gateway LOG_LEVEL=DEBUG -n dataaptor
```

## See Also

- [Quick Deploy Guide](quick-deploy.md) - Local development deployment
- [Security Practices](../user-guides/security-practices.md) - Security best practices
- [Architecture Documentation](../architecture/ArchitectureDocument.md) - System architecture
