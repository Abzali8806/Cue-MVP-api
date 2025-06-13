# Cue MVP FastAPI Backend (API Gateway Module)

This repository contains the FastAPI backend application for the Cue Minimum Viable Product (MVP). This application serves as the API Gateway, handling all backend logic, data processing, and integrations. It is designed to be a pure API service, providing a robust and scalable foundation for the Cue platform.

## 1. Project Overview

The Cue backend is a critical component of the overall system, responsible for:
*   **User Authentication:** Securely handling user login via Google and GitHub OAuth.
*   **Workflow Generation:** Processing natural language prompts to generate executable Python code for automated workflows.
*   **Code Validation:** Ensuring the generated code is syntactically correct, uses current modules, and is production-ready.
*   **Integration with AWS Services:** Interacting with various AWS services (e.g., RDS, ElastiCache, SageMaker, S3, Secrets Manager) to support core functionalities.
*   **API Gateway:** Exposing well-defined RESTful API endpoints for the frontend and other potential consumers.

**Important Note:** This backend is a headless API service. It does **NOT** include any User Interface (UI) components, frontend rendering logic, or static file serving for frontend assets. All UI is handled by the separate React frontend module.

## 2. Setup and Installation (Local Development)

Follow these steps to set up and run the FastAPI backend on your local machine.

### 2.1. Prerequisites

*   Python 3.11+
*   `pip` (Python package installer)
*   A PostgreSQL database instance (can be local or a cloud instance like AWS RDS).

### 2.2. Clone the Repository

```bash
git clone <repository_url> # Replace with the actual repository URL if different
cd cue-backend/
```

### 2.3. Create and Activate a Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies.

```bash
python3.11 -m venv venv
source venv/bin/activate # On Windows, use `venv\Scripts\activate`
```

### 2.4. Install Dependencies

Install all required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

## 3. Configuration (Environment Variables)

All sensitive information and configuration settings are managed via environment variables. Create a `.env` file in the root of the `cue-backend/` directory based on the `.env.example` provided.

```dotenv
# .env.example content (copy to .env and fill in)

# AWS RDS PostgreSQL Database Configuration
# Replace with your AWS RDS PostgreSQL connection details
# Format: postgresql+psycopg2://username:password@rds-endpoint:port/database_name
# Example: postgresql+psycopg2://cueuser:yourpassword@cue-db.cluster-xxxxx.us-east-1.rds.amazonaws.com:5432/cue_production
DATABASE_URL="postgresql+psycopg2://YOUR_RDS_USERNAME:YOUR_RDS_PASSWORD@YOUR_RDS_ENDPOINT:5432/YOUR_DATABASE_NAME"

# JWT Secret Key (for authentication)
SECRET_KEY="your_super_secret_jwt_key_here" # GENERATE A STRONG, RANDOM KEY
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30 # Example: 30 minutes

# Google OAuth Credentials
GOOGLE_CLIENT_ID="your_google_client_id"
GOOGLE_CLIENT_SECRET="your_google_client_secret"
GOOGLE_REDIRECT_URI="http://localhost:8000/auth/google/callback" # Update for deployed environments

# GitHub OAuth Credentials
GITHUB_CLIENT_ID="your_github_client_id"
GITHUB_CLIENT_SECRET="your_github_client_secret"
GITHUB_REDIRECT_URI="http://localhost:8000/auth/github/callback" # Update for deployed environments

# Frontend URL for Redirection (after successful OAuth)
FRONTEND_URL="http://localhost:3000" # Update for deployed environments (e.g., https://cue-tracker-abzali20.replit.app/)

# CORS Allowed Origins (comma-separated list of frontend URLs)
CORS_ALLOWED_ORIGINS="http://localhost:3000,https://cue-tracker-abzali20.replit.app/,https://dev.cue-dev.com,https://staging.cue-dev.com,https://cue-prod.com"

# AWS Service Endpoints (if applicable, for local testing or specific integrations)
# AWS_SAGEMAKER_ENDPOINT="..."
# AWS_OPENSEARCH_ENDPOINT="..."
# AWS_S3_BUCKET_NAME="..."
```

**Important:** For production deployments, use a dedicated secret management service (e.g., AWS Secrets Manager) instead of `.env` files.

## 4. Database Migrations

This project uses Alembic for database migrations. After configuring your `DATABASE_URL` in `.env`, you can run migrations.

```bash
alembic upgrade head
```

## 5. Running the Application

### 5.1. Local Development

To run the FastAPI application locally using Uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

This will start the server on `http://localhost:8000`. The `--reload` flag enables auto-reloading on code changes.

### 5.2. Docker

Complete Docker configuration is provided for both development and production environments:

**Quick Start:**
```bash
# Development (includes PostgreSQL, Redis, Nginx)
docker-compose up -d

# Production (connects to AWS RDS)
docker-compose -f docker-compose.production.yml up -d
```

**Available Docker Files:**
- `Dockerfile` - Development image with hot reloading
- `Dockerfile.production` - Optimized production build
- `docker-compose.yml` - Full development stack
- `docker-compose.production.yml` - Production deployment

For complete Docker setup, deployment guides, and architecture details, see **[DOCKER_DEPLOYMENT_GUIDE.md](DOCKER_DEPLOYMENT_GUIDE.md)**.

## 6. API Endpoints

The following are the main API endpoints exposed by the backend. For detailed request/response schemas, refer to the automatically generated OpenAPI documentation (Swagger UI) at `http://localhost:8000/docs` when the server is running.

*   **Authentication & User Management:**
    *   `GET /auth/google/callback`: Google OAuth callback handler.
    *   `GET /auth/github/callback`: GitHub OAuth callback handler.
    *   `GET /users/me`: Get current authenticated user's profile.

*   **Workflow Processing:**
    *   `POST /workflows/generate`: Generate Python workflow code from natural language.
    *   `POST /workflows/{workflow_id}/credentials`: Update workflow code with user-provided credentials.

*   **Code Validation:**
    *   `POST /code/validate`: Validate generated Python code.

*   **Speech-to-Text Proxy (if implemented):**
    *   `POST /speech/transcribe`: Proxy for speech-to-text service.

*   **Health Check:**
    *   `GET /health`: Check application health status.

## 7. Frontend Integration

This backend is designed to integrate seamlessly with the React frontend module. Key integration points include:

*   **CORS:** The backend is configured with `CORSMiddleware` to allow requests from the frontend's origin(s).
*   **OAuth Flow:** The backend handles the server-side OAuth token exchange and redirects the user back to the frontend with a JWT upon successful authentication.
*   **JWT Authentication:** All protected API endpoints expect a JWT in the `Authorization: Bearer <token>` header from the frontend.

**Frontend Repository:** `https://github.com/Abzali8806/Cue-MVP-dev.git`
**Deployed Frontend URL:** `https://cue-tracker-abzali20.replit.app/`

Ensure the `FRONTEND_URL` and `CORS_ALLOWED_ORIGINS` environment variables are correctly set to match your frontend's deployment.

## 8. AWS Service Interactions

The FastAPI backend is designed to interact with various AWS services to provide its full functionality. While the backend code will contain the logic for these interactions, the AWS infrastructure itself is managed separately (e.g., via Terraform).

*   **PostgreSQL (AWS RDS):** Used as the primary database for user data, workflow metadata, etc.
*   **Redis (AWS ElastiCache):** Can be integrated for caching, session management, or rate limiting.
*   **AI/ML Services (AWS SageMaker, OpenSearch):** Potentially used for advanced NLP processing, code generation models, or semantic search capabilities.
*   **AWS Secrets Manager:** Recommended for securely storing and retrieving sensitive credentials in production environments.
*   **AWS S3:** For storing large files, such as complex code templates or user-uploaded data.
*   **AWS CloudWatch:** For centralized logging and monitoring of the application.

## 9. License

[Specify your project's license here, e.g., MIT License]

