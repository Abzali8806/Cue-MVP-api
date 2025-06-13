#!/bin/bash

# Docker build script for Cue MVP FastAPI Backend

set -e

echo "Building Docker images for Cue MVP Backend..."

# Build development image
echo "Building development image..."
docker build -f Dockerfile -t cue-backend:latest .

# Build production image
echo "Building production image..."
docker build -f Dockerfile.production -t cue-backend:production .

echo "Docker images built successfully!"
echo ""
echo "Available images:"
docker images | grep cue-backend

echo ""
echo "To run the application:"
echo "Development: docker-compose up"
echo "Production: docker-compose -f docker-compose.production.yml up"