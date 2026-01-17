#!/bin/bash
# Build Docker images for all DataAptor AI services

set -e

echo "Building DataAptor AI Docker Images"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default registry and tag
REGISTRY=${DOCKER_REGISTRY:-""}
TAG=${IMAGE_TAG:-"latest"}

# Function to build an image
build_image() {
    local service_name=$1
    local context_path=$2
    local image_name="dataaptor-$service_name"
    
    if [ -n "$REGISTRY" ]; then
        image_name="$REGISTRY/$image_name"
    fi
    
    echo ""
    echo "Building $service_name..."
    echo "------------------------"
    
    if [ -d "$context_path" ] && [ -f "$context_path/Dockerfile" ]; then
        if docker build -t "$image_name:$TAG" "$context_path"; then
            echo -e "${GREEN}Successfully built $image_name:$TAG${NC}"
            
            # Also tag as latest if not already
            if [ "$TAG" != "latest" ]; then
                docker tag "$image_name:$TAG" "$image_name:latest"
            fi
        else
            echo -e "${RED}Failed to build $image_name${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}Skipping $service_name - no Dockerfile found${NC}"
    fi
}

# Parse command line arguments
PUSH=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --push)
            PUSH=true
            shift
            ;;
        --registry)
            REGISTRY="$2"
            shift 2
            ;;
        --tag)
            TAG="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--push] [--registry REGISTRY] [--tag TAG]"
            exit 1
            ;;
    esac
done

# Build all service images
cd "$PROJECT_ROOT"

build_image "web-ui" "./client"
build_image "api-gateway" "./api-gateway"
build_image "orchestration-service" "./orchestration-service"
build_image "ingestion-service" "./processing/ingestion-service"
build_image "assessment-service" "./processing/assessment-service"
build_image "scoring-service" "./processing/scoring-service"
build_image "reporting-service" "./processing/reporting-service"

# Push images if requested
if [ "$PUSH" = true ]; then
    echo ""
    echo "Pushing images to registry..."
    echo "-----------------------------"
    
    if [ -z "$REGISTRY" ]; then
        echo -e "${RED}Error: --registry is required when using --push${NC}"
        exit 1
    fi
    
    for service in web-ui api-gateway orchestration-service ingestion-service assessment-service scoring-service reporting-service; do
        image_name="$REGISTRY/dataaptor-$service"
        echo "Pushing $image_name:$TAG..."
        docker push "$image_name:$TAG"
        if [ "$TAG" != "latest" ]; then
            docker push "$image_name:latest"
        fi
    done
fi

# List built images
echo ""
echo "===================================="
echo "Built Images:"
echo "===================================="
docker images | grep dataaptor | head -20

echo ""
echo -e "${GREEN}Build complete!${NC}"
