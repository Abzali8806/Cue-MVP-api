#!/bin/bash

# Database migration script for FastAPI application
# This script runs Alembic migrations to set up or update the database schema

set -e  # Exit on any error

echo "Starting database migration..."

# Wait for database to be ready
echo "Waiting for database to be ready..."
while ! pg_isready -h db -p 5432 -U cue_user; do
    echo "Database is not ready yet. Waiting..."
    sleep 2
done

echo "Database is ready. Running migrations..."

# Run Alembic migrations
alembic upgrade head

echo "Database migration completed successfully!"

