#!/bin/bash
# Deploy DataAptor AI to Kubernetes

set -e

echo "Deploying DataAptor AI to Kubernetes"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default values
NAMESPACE=${K8S_NAMESPACE:-"dataaptor"}
REGISTRY=${DOCKER_REGISTRY:-""}
TAG=${IMAGE_TAG:-"latest"}
ENVIRONMENT=${ENVIRONMENT:-"staging"}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        --registry)
            REGISTRY="$2"
            shift 2
            ;;
        --tag)
            TAG="$2"
            shift 2
            ;;
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN="--dry-run=client"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--namespace NAMESPACE] [--registry REGISTRY] [--tag TAG] [--environment ENV] [--dry-run]"
            exit 1
            ;;
    esac
done

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}kubectl is not installed${NC}"
    exit 1
fi

if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}Cannot connect to Kubernetes cluster${NC}"
    exit 1
fi

echo -e "${GREEN}Prerequisites check passed${NC}"

# Create namespace if it doesn't exist
echo ""
echo "Creating namespace $NAMESPACE..."
kubectl create namespace "$NAMESPACE" $DRY_RUN --save-config 2>/dev/null || true

# Create ConfigMaps
echo ""
echo "Creating ConfigMaps..."
kubectl create configmap dataaptor-config \
    --namespace="$NAMESPACE" \
    --from-literal=ENVIRONMENT="$ENVIRONMENT" \
    --from-literal=API_GATEWAY_URL="http://api-gateway:8000" \
    --from-literal=ORCHESTRATION_URL="http://orchestration-service:8001" \
    --from-literal=INGESTION_URL="http://ingestion-service:8002" \
    --from-literal=ASSESSMENT_URL="http://assessment-service:8003" \
    --from-literal=SCORING_URL="http://scoring-service:8004" \
    --from-literal=REPORTING_URL="http://reporting-service:8005" \
    $DRY_RUN --save-config -o yaml | kubectl apply -f -

# Create Secrets (in production, use external secret management)
echo ""
echo "Creating Secrets..."
kubectl create secret generic dataaptor-secrets \
    --namespace="$NAMESPACE" \
    --from-literal=POSTGRES_PASSWORD="$(openssl rand -base64 32)" \
    --from-literal=JWT_SECRET="$(openssl rand -base64 64)" \
    --from-literal=MINIO_SECRET_KEY="$(openssl rand -base64 32)" \
    $DRY_RUN --save-config -o yaml 2>/dev/null | kubectl apply -f - || true

# Deploy services
echo ""
echo "Deploying services..."

# Function to deploy a service
deploy_service() {
    local service_name=$1
    local port=$2
    local replicas=${3:-1}
    
    local image_name="dataaptor-$service_name"
    if [ -n "$REGISTRY" ]; then
        image_name="$REGISTRY/$image_name"
    fi
    
    echo "Deploying $service_name..."
    
    cat <<EOF | kubectl apply $DRY_RUN -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: $service_name
  namespace: $NAMESPACE
  labels:
    app: $service_name
    environment: $ENVIRONMENT
spec:
  replicas: $replicas
  selector:
    matchLabels:
      app: $service_name
  template:
    metadata:
      labels:
        app: $service_name
    spec:
      containers:
      - name: $service_name
        image: $image_name:$TAG
        ports:
        - containerPort: $port
        envFrom:
        - configMapRef:
            name: dataaptor-config
        - secretRef:
            name: dataaptor-secrets
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: $port
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: $port
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: $service_name
  namespace: $NAMESPACE
spec:
  selector:
    app: $service_name
  ports:
  - port: $port
    targetPort: $port
  type: ClusterIP
EOF
}

# Deploy all services
deploy_service "api-gateway" 8000 2
deploy_service "orchestration-service" 8001 2
deploy_service "ingestion-service" 8002 2
deploy_service "assessment-service" 8003 3
deploy_service "scoring-service" 8004 2
deploy_service "reporting-service" 8005 2

# Deploy web UI with LoadBalancer
echo "Deploying web-ui..."
cat <<EOF | kubectl apply $DRY_RUN -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-ui
  namespace: $NAMESPACE
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web-ui
  template:
    metadata:
      labels:
        app: web-ui
    spec:
      containers:
      - name: web-ui
        image: ${REGISTRY:+$REGISTRY/}dataaptor-web-ui:$TAG
        ports:
        - containerPort: 3000
        env:
        - name: REACT_APP_API_URL
          value: "http://api-gateway:8000"
---
apiVersion: v1
kind: Service
metadata:
  name: web-ui
  namespace: $NAMESPACE
spec:
  selector:
    app: web-ui
  ports:
  - port: 80
    targetPort: 3000
  type: LoadBalancer
EOF

# Wait for deployments
echo ""
echo "Waiting for deployments to be ready..."
kubectl rollout status deployment/api-gateway -n "$NAMESPACE" --timeout=300s || true
kubectl rollout status deployment/web-ui -n "$NAMESPACE" --timeout=300s || true

# Show deployment status
echo ""
echo "====================================="
echo "Deployment Status"
echo "====================================="
kubectl get deployments -n "$NAMESPACE"
echo ""
kubectl get services -n "$NAMESPACE"
echo ""
kubectl get pods -n "$NAMESPACE"

echo ""
echo -e "${GREEN}Deployment complete!${NC}"
echo ""
echo "To access the application:"
echo "  kubectl get svc web-ui -n $NAMESPACE"
