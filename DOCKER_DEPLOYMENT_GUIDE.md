# Docker Deployment Guide for Cue MVP FastAPI Backend

This guide covers the complete Docker configuration for deploying the Cue MVP FastAPI Backend.

## Quick Start

### Development Environment
```bash
# Start all services including PostgreSQL and Redis
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### Production Environment
```bash
# Build and deploy
./scripts/build.sh
./scripts/deploy.sh

# Or use docker-compose for production
docker-compose -f docker-compose.production.yml up -d
```

## Docker Configuration Files

### Core Files
- `Dockerfile` - Development image with hot reloading
- `Dockerfile.production` - Optimized multi-stage production build
- `docker-requirements.txt` - Python dependencies for Docker builds
- `.dockerignore` - Excludes unnecessary files from Docker context

### Compose Files
- `docker-compose.yml` - Development stack (app + PostgreSQL + Redis + Nginx)
- `docker-compose.production.yml` - Production deployment (app only, uses AWS RDS)
- `docker-compose.override.yml.example` - Template for local development overrides

### Configuration
- `nginx/nginx.conf` - Reverse proxy with rate limiting and security headers
- `database/init/01-init.sql` - PostgreSQL initialization for development
- `scripts/build.sh` - Automated build script
- `scripts/deploy.sh` - Automated deployment script

## Architecture

### Development Stack
```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│    Nginx    │───▶│   FastAPI    │───▶│ PostgreSQL  │
│   (Port 80) │    │  (Port 8000) │    │ (Port 5432) │
└─────────────┘    └──────────────┘    └─────────────┘
                           │
                   ┌──────────────┐
                   │    Redis     │
                   │ (Port 6379)  │
                   └──────────────┘
```

### Production Stack
```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│    Nginx    │───▶│   FastAPI    │───▶│  AWS RDS    │
│   (Port 80) │    │  (Port 8000) │    │ PostgreSQL  │
└─────────────┘    └──────────────┘    └─────────────┘
```

## Environment Configuration

### Required Environment Variables
Copy `.env.example` to `.env` and configure:

```bash
# Database (AWS RDS for production)
DATABASE_URL=postgresql://username:password@host:port/database

# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# AWS
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1

# Optional: Azure Speech Services
AZURE_SPEECH_KEY=your-azure-speech-key
AZURE_SPEECH_REGION=your-azure-region
```

## Production Deployment

### Prerequisites
1. AWS RDS PostgreSQL instance configured
2. Environment variables properly set in `.env`
3. Docker and Docker Compose installed
4. SSL certificates (for HTTPS with Nginx)

### Option 1: Using Scripts
```bash
# Build images
./scripts/build.sh

# Deploy application
./scripts/deploy.sh
```

### Option 2: Using Docker Compose
```bash
# Production deployment
docker-compose -f docker-compose.production.yml up -d

# Check status
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f
```

### Option 3: Manual Docker Commands
```bash
# Build production image
docker build -f Dockerfile.production -t cue-backend:production .

# Run with environment file
docker run -d \
  --name cue-api \
  --env-file .env \
  -p 8000:8000 \
  --restart unless-stopped \
  cue-backend:production
```

## Development Workflow

### Hot Reloading Setup
1. Copy override template:
   ```bash
   cp docker-compose.override.yml.example docker-compose.override.yml
   ```

2. Start development environment:
   ```bash
   docker-compose up -d
   ```

3. Code changes will automatically reload the application

### Database Management
```bash
# Access development database
docker-compose exec db psql -U cue_user -d cue_development

# Run migrations
docker-compose exec app alembic upgrade head

# Create new migration
docker-compose exec app alembic revision --autogenerate -m "description"
```

## Monitoring and Troubleshooting

### Health Checks
- Application: `http://localhost:8000/health`
- API Documentation: `http://localhost:8000/docs`

### Log Access
```bash
# Application logs
docker-compose logs -f app

# Database logs
docker-compose logs -f db

# All services
docker-compose logs -f
```

### Common Issues

#### Database Connection Issues
```bash
# Check database status
docker-compose exec db pg_isready -U cue_user

# Verify environment variables
docker-compose exec app env | grep DATABASE_URL
```

#### Performance Monitoring
```bash
# Check resource usage
docker stats

# Check container health
docker-compose ps
```

## Security Considerations

### Production Security
1. Use strong, unique secret keys
2. Configure SSL/TLS certificates in Nginx
3. Set up proper firewall rules
4. Use AWS IAM roles instead of access keys when possible
5. Regularly update Docker base images

### Environment Variables
- Never commit `.env` files to version control
- Use Docker secrets or AWS Parameter Store for production
- Rotate secrets regularly

## Scaling

### Horizontal Scaling
```bash
# Scale FastAPI instances
docker-compose -f docker-compose.production.yml up -d --scale app=3
```

### Load Balancing
- Nginx is configured for load balancing multiple app instances
- Rate limiting configured (10 requests/second per IP)
- Health checks ensure traffic only goes to healthy instances

## Backup and Recovery

### Database Backups
```bash
# Backup development database
docker-compose exec db pg_dump -U cue_user cue_development > backup.sql

# Restore from backup
docker-compose exec -T db psql -U cue_user cue_development < backup.sql
```

### Volume Management
```bash
# List volumes
docker volume ls

# Backup volume data
docker run --rm -v cue_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
```

## CI/CD Integration

### Example GitHub Actions Workflow
```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Build and Deploy
      run: |
        docker build -f Dockerfile.production -t cue-backend:latest .
        # Add your deployment commands here
```

For more detailed configuration information, see `CONFIGURATION_GUIDE.md`.