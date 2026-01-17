# Security Practices

This guide covers security best practices when using DataAptor AI for dataset assessment.

## Overview

DataAptor AI handles potentially sensitive data during assessment. This guide covers:

1. Data protection during upload and processing
2. Authentication and authorization
3. PII handling and compliance
4. Secure deployment practices

## Data Protection

### Encryption in Transit

All data transmitted to DataAptor AI should use HTTPS:

```bash
# Configure CLI to use HTTPS
python dataaptor.py config --set api_url --value https://your-domain.com

# Verify SSL certificate
curl -v https://your-domain.com/health
```

### Encryption at Rest

Data stored in DataAptor AI is encrypted:

- **MinIO/S3**: Server-side encryption (SSE-S3)
- **PostgreSQL**: Transparent Data Encryption (TDE)

Configure encryption for self-hosted deployments:

```yaml
# docker-compose.yml
minio:
  environment:
    - MINIO_KMS_SECRET_KEY=your-encryption-key
```

### Data Retention

Configure data retention policies:

```bash
# Set retention period (days)
python dataaptor.py config --set data_retention_days --value 30

# Enable automatic cleanup
python dataaptor.py config --set auto_cleanup --value true
```

Delete data after assessment:

```bash
# Delete dataset and all associated data
python dataaptor.py delete <dataset_id> --force

# Delete assessment results only
python dataaptor.py delete-assessment <assessment_id>
```

## Authentication

### API Authentication

DataAptor AI uses JWT-based authentication:

```bash
# Login and get token
curl -X POST https://your-domain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'

# Use token in requests
curl https://your-domain.com/api/datasets \
  -H "Authorization: Bearer <your-token>"
```

### CLI Authentication

```bash
# Configure API key
python dataaptor.py config --set api_key --value your-api-key

# Or use environment variable
export DATAAPTOR_API_KEY=your-api-key
```

### Token Management

- Tokens expire after 1 hour by default
- Refresh tokens before expiration
- Never share or commit tokens to version control

```python
from dataaptor import DataAptorClient

client = DataAptorClient()
client.login(username="user", password="pass")

# Token is automatically refreshed
client.upload("data.csv")
```

## Authorization

### Role-Based Access Control

DataAptor AI supports role-based access:

| Role | Permissions |
|------|-------------|
| Admin | Full access to all features |
| Analyst | Upload, assess, view reports |
| Viewer | View reports only |

### API Permissions

```bash
# Create user with specific role
curl -X POST https://your-domain.com/api/admin/users \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{"username": "analyst1", "role": "analyst"}'
```

## PII Handling

### Pre-Upload Anonymization

Always anonymize PII before uploading:

```python
import pandas as pd
import hashlib

def anonymize_pii(df):
    # Hash identifiers
    if 'email' in df.columns:
        df['email'] = df['email'].apply(
            lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:16]
        )
    
    # Remove sensitive columns
    sensitive_cols = ['ssn', 'credit_card', 'password']
    df = df.drop(columns=[c for c in sensitive_cols if c in df.columns])
    
    return df

df = pd.read_csv("raw_data.csv")
df_safe = anonymize_pii(df)
df_safe.to_csv("safe_data.csv", index=False)
```

### PII Detection Settings

Configure PII detection sensitivity:

```bash
# Enable strict PII detection
python dataaptor.py config --set pii_detection_level --value strict

# Levels: strict, moderate, minimal
```

### Compliance Modes

Enable compliance-specific modes:

```bash
# GDPR compliance mode
python dataaptor.py config --set compliance_mode --value gdpr

# HIPAA compliance mode
python dataaptor.py config --set compliance_mode --value hipaa

# CCPA compliance mode
python dataaptor.py config --set compliance_mode --value ccpa
```

## Secure Deployment

### Docker Security

```yaml
# docker-compose.yml security settings
services:
  api-gateway:
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
    user: "1000:1000"
```

### Kubernetes Security

```yaml
# Security context for pods
apiVersion: v1
kind: Pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
  containers:
  - name: api-gateway
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
          - ALL
```

### Network Security

```yaml
# Network policy to restrict traffic
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: dataaptor-network-policy
spec:
  podSelector:
    matchLabels:
      app: dataaptor
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: dataaptor
    ports:
    - port: 8000
```

## Audit Logging

### Enable Audit Logs

```bash
# Enable comprehensive audit logging
python dataaptor.py config --set audit_logging --value true
python dataaptor.py config --set audit_log_level --value detailed
```

### Log Contents

Audit logs capture:
- User authentication events
- Dataset uploads and deletions
- Assessment requests
- Report exports
- Configuration changes

### Log Storage

```yaml
# Configure log shipping
logging:
  driver: "json-file"
  options:
    max-size: "100m"
    max-file: "5"
```

## Secret Management

### Environment Variables

Never hardcode secrets:

```bash
# Use environment variables
export POSTGRES_PASSWORD=$(cat /run/secrets/db_password)
export JWT_SECRET=$(cat /run/secrets/jwt_secret)
```

### Docker Secrets

```yaml
# docker-compose.yml
services:
  api-gateway:
    secrets:
      - db_password
      - jwt_secret

secrets:
  db_password:
    file: ./secrets/db_password.txt
  jwt_secret:
    file: ./secrets/jwt_secret.txt
```

### Kubernetes Secrets

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: dataaptor-secrets
type: Opaque
data:
  postgres-password: <base64-encoded>
  jwt-secret: <base64-encoded>
```

## Security Checklist

Before deploying DataAptor AI:

- [ ] HTTPS enabled for all endpoints
- [ ] Strong passwords configured
- [ ] JWT secrets rotated
- [ ] Database encrypted at rest
- [ ] Network policies configured
- [ ] Audit logging enabled
- [ ] PII detection enabled
- [ ] Data retention policies set
- [ ] Backup procedures tested
- [ ] Security updates applied

## Incident Response

If you suspect a security incident:

1. **Isolate**: Disconnect affected systems
2. **Preserve**: Save logs and evidence
3. **Investigate**: Determine scope and impact
4. **Remediate**: Fix vulnerabilities
5. **Report**: Notify affected parties if required

## Next Steps

- Review [Installation Guide](installation.md) for secure setup
- Explore [Integration Options](integrations.md)
- Check [API Documentation](../api/README.md) for security headers
