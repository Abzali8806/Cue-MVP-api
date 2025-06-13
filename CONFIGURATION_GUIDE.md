# Cue MVP Backend Configuration Guide

This guide covers all the configuration values you need to set up for the Cue MVP FastAPI Backend.

## Required Configurations

### 1. AWS RDS PostgreSQL Database
**Location**: `DATABASE_URL` in `.env`
**Format**: `postgresql://username:password@endpoint:5432/database_name`
**Where to get**: Your AWS RDS PostgreSQL instance details

### 2. Security Keys (CRITICAL)
**Generate secure random keys using**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
- `SECRET_KEY`: Main application secret
- `JWT_SECRET_KEY`: JWT token signing key

### 3. Google OAuth (Required for Google Login)
**Where to get**: [Google Cloud Console](https://console.cloud.google.com) > APIs & Services > Credentials
**Steps**:
1. Create new project or select existing
2. Enable Google+ API
3. Create OAuth 2.0 Client ID (Web application)
4. Add authorized redirect URIs:
   - `http://localhost:8000/auth/google/callback` (development)
   - `https://your-backend-domain.com/auth/google/callback` (production)

**Required values**:
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`

### 4. GitHub OAuth (Required for GitHub Login)
**Where to get**: [GitHub](https://github.com) > Settings > Developer settings > OAuth Apps
**Steps**:
1. Click "New OAuth App"
2. Set Authorization callback URL:
   - `http://localhost:8000/auth/github/callback` (development)
   - `https://your-backend-domain.com/auth/github/callback` (production)

**Required values**:
- `GITHUB_CLIENT_ID`
- `GITHUB_CLIENT_SECRET`

### 5. AWS Credentials (Required for AWS Services)
**Where to get**: [AWS IAM](https://console.aws.amazon.com/iam/) > Users > Security credentials
**Steps**:
1. Create IAM user with programmatic access
2. Attach policies for services you'll use (RDS, S3, Secrets Manager, etc.)
3. Generate access keys

**Required values**:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION` (e.g., us-east-1)

## Optional Configurations

### 6. Azure Speech Services (Optional - for speech-to-text)
**Where to get**: [Azure Portal](https://portal.azure.com) > Cognitive Services > Speech Services
**Only needed if using speech-to-text features**:
- `AZURE_SPEECH_KEY`
- `AZURE_SPEECH_REGION`

### 7. CORS Origins (Update as needed)
**Current configured domains**:
- `https://cue-tracker-abzali20.replit.app` (your frontend)
- Local development domains

**Add additional production domains** in `config.py` if needed.

## Configuration Checklist

Before deploying to production:

- [ ] AWS RDS PostgreSQL database created and accessible
- [ ] `DATABASE_URL` updated with RDS connection string
- [ ] Secure `SECRET_KEY` and `JWT_SECRET_KEY` generated
- [ ] Google OAuth app created and credentials configured
- [ ] GitHub OAuth app created and credentials configured  
- [ ] AWS IAM user created with appropriate permissions
- [ ] AWS credentials configured
- [ ] CORS origins updated for production domains
- [ ] Environment set to "production" in deployment
- [ ] All sensitive values stored in environment variables (not in code)

## Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use AWS Secrets Manager** for production credential storage
3. **Rotate credentials regularly**
4. **Use least privilege principle** for AWS IAM permissions
5. **Enable database SSL/TLS** connections
6. **Use strong, unique passwords** for all services

## Testing Your Configuration

Run these commands to verify your setup:

```bash
# Test database connection
python -c "from database.database import engine; print('Database connected!')"

# Test OAuth endpoints (will fail without proper credentials)
curl http://localhost:8000/auth/google/callback?code=test&state=test

# Test API health
curl http://localhost:8000/health
```