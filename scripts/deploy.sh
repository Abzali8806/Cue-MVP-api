#!/bin/bash

# Deployment script for Cue MVP FastAPI Backend

set -e

# Configuration
IMAGE_NAME="cue-backend"
CONTAINER_NAME="cue-api"
NETWORK_NAME="cue-network"

echo "Deploying Cue MVP Backend..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Creating from template..."
    cp .env.example .env
    echo "Please configure .env file with your production settings before deployment."
    exit 1
fi

# Create network if it doesn't exist
docker network create $NETWORK_NAME 2>/dev/null || true

# Stop and remove existing container
echo "Stopping existing container..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# Build production image
echo "Building production image..."
docker build -f Dockerfile.production -t $IMAGE_NAME:production .

# Run database migrations (if using local PostgreSQL)
echo "Running database migrations..."
docker run --rm --env-file .env --network $NETWORK_NAME $IMAGE_NAME:production alembic upgrade head || echo "Migrations skipped (using external database)"

# Start the application
echo "Starting application..."
docker run -d \
    --name $CONTAINER_NAME \
    --env-file .env \
    --network $NETWORK_NAME \
    -p 8000:8000 \
    --restart unless-stopped \
    $IMAGE_NAME:production

echo "Deployment complete!"
echo "Application is running at: http://localhost:8000"
echo "API documentation: http://localhost:8000/docs"
echo ""
echo "To check logs: docker logs $CONTAINER_NAME"
echo "To stop: docker stop $CONTAINER_NAME"