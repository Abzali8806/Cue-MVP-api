-- Initial database setup for development environment
-- This file is only used for local development with docker-compose
-- Production uses AWS RDS with migrations

-- Create extensions if they don't exist
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE cue_development TO cue_user;