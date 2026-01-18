#!/bin/bash
# Quick test script for Docker container

set -e

echo "=========================================="
echo "Testing mdconv Docker Container"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    exit 1
fi

# Build the image
echo -e "${YELLOW}Building Docker image...${NC}"
docker build -t mdconv-api .

# Start container in background
echo -e "${YELLOW}Starting container...${NC}"
docker run -d --name mdconv-test -p 8000:8000 mdconv-api

# Wait for container to be ready
echo -e "${YELLOW}Waiting for API to be ready...${NC}"
sleep 5

# Test health endpoint
echo -e "${YELLOW}Testing health endpoint...${NC}"
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Health check passed${NC}"
else
    echo -e "${RED}✗ Health check failed${NC}"
    docker logs mdconv-test
    docker stop mdconv-test
    docker rm mdconv-test
    exit 1
fi

# Test formats endpoint
echo -e "${YELLOW}Testing formats endpoint...${NC}"
if curl -f http://localhost:8000/formats > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Formats endpoint working${NC}"
else
    echo -e "${RED}✗ Formats endpoint failed${NC}"
fi

# Run Python test script if available
if [ -f "test_docker_conversions.py" ]; then
    echo -e "${YELLOW}Running comprehensive conversion tests...${NC}"
    python test_docker_conversions.py --all-formats || true
fi

# Cleanup
echo -e "${YELLOW}Stopping and removing container...${NC}"
docker stop mdconv-test
docker rm mdconv-test

echo ""
echo -e "${GREEN}=========================================="
echo "Docker test completed!"
echo "==========================================${NC}"
