# Replit AI Agent Prompt: Cue MVP FastAPI Backend (API Gateway Module)

**Objective:** Create a robust and scalable FastAPI backend application for the Cue MVP. This application will serve as the API Gateway Module, handling all backend logic, data processing, and integrations. The primary goal is to provide a pure API service that seamlessly integrates with the existing React frontend module. **Crucially, this application MUST NOT include any User Interface (UI) components or frontend rendering logic.**

**Non-Goals:**
*   **NO UI:** The Replit agent MUST NOT generate any HTML, CSS, JavaScript for UI, or any templating engines for server-side rendering. This is a headless API service.
*   **NO Frontend Assets:** Do not include any static file serving for frontend assets.
*   **NO Database UI/Admin Panels:** While a database will be used, do not generate any UI for database management.

**Context:**
*   **Existing Frontend:** A React-based frontend module already exists and is responsible for all user interface interactions. The backend must be designed to communicate effectively with this frontend. The frontend code can be found at: `https://github.com/Abzali8806/Cue-MVP-dev.git`. The deployed frontend URL is: `https://cue-tracker-abzali20.replit.app/`.
*   **Architecture:** This FastAPI application is part of a modular monolith architecture, acting as the API Gateway. It will house various backend services (e.g., OAuth, workflow generation, validation) internally.

**Key Requirements for Seamless Frontend Integration:**
*   **CORS Configuration:** Proper Cross-Origin Resource Sharing (CORS) configuration is essential to allow the React frontend (running on a different origin) to make requests to this FastAPI backend.
*   **JSON Responses:** All API endpoints must return JSON responses.
*   **Authentication:** Implement JWT (JSON Web Token) based authentication for protected routes, issued upon successful OAuth login.
*   **OAuth Callbacks:** Specific endpoints are required to handle OAuth callbacks from Google and GitHub, as initiated by the frontend.





## Core Functionalities and API Endpoints

The FastAPI backend must implement the following core functionalities, each exposed via well-defined API endpoints. **All responses must be in JSON format.**

1.  **Authentication Module (OAuth & JWT):**
    *   **Google OAuth Callback:**
        *   **Endpoint:** `GET /auth/google/callback`
        *   **Functionality:** Handles the callback from Google after user authentication. Receives an `authorization_code` and `state` parameter. Validates the `state` parameter against a stored value (from the frontend\'s initial request). Exchanges the `authorization_code` with Google for an access token and refresh token. Fetches user profile information (email, name) from Google using the access token. Creates or retrieves a user record in the Cue database. Generates a JWT (JSON Web Token) containing user identifiers (e.g., user ID, email) and returns it to the frontend (e.g., by redirecting to a frontend URL with the token as a query parameter, or directly in the JSON response if the frontend handles the redirect).
        *   **Request (Query Params):** `code: str`, `state: str`
        *   **Success Response (Example - if returning JWT directly):** `200 OK` with `{"access_token": "your_jwt", "token_type": "bearer"}`
        *   **Error Response:** Appropriate HTTP status codes (e.g., `400 Bad Request` for invalid state, `500 Internal Server Error` for issues with Google API).
    *   **GitHub OAuth Callback:**
        *   **Endpoint:** `GET /auth/github/callback`
        *   **Functionality:** Similar to Google OAuth callback, but for GitHub. Exchanges the `authorization_code` with GitHub for an access token. Fetches user profile information (email, name/login) from GitHub. Creates or retrieves a user record. Generates and returns a JWT.
        *   **Request (Query Params):** `code: str`, `state: str`
        *   **Success Response (Example):** `200 OK` with `{"access_token": "your_jwt", "token_type": "bearer"}`
        *   **Error Response:** Appropriate HTTP status codes.
    *   **Get Current User (Protected Route):**
        *   **Endpoint:** `GET /users/me`
        *   **Functionality:** Returns the profile information of the currently authenticated user (based on the JWT sent in the `Authorization` header).
        *   **Request Headers:** `Authorization: Bearer <your_jwt>`
        *   **Success Response:** `200 OK` with `{"email": "user@example.com", "name": "User Name", ...}`
        *   **Error Response:** `401 Unauthorized` if token is missing or invalid.

2.  **Workflow Processing Module:**
    *   **Generate Workflow Code:**
        *   **Endpoint:** `POST /workflows/generate`
        *   **Functionality (High-Level):** This is the core of Cue. Receives a natural language prompt (text or transcribed speech) describing the desired workflow. Processes this prompt using an NLP engine (details below on AWS integration). Identifies triggers, steps, and third-party tools. If tools are not specified, the backend should intelligently select suitable ones. Generates Python code for the workflow, deployable on AWS Lambda. Inserts placeholders for API keys/tokens. **This endpoint will interact with AWS services for NLP and potentially for accessing pre-trained models or code generation utilities.**
        *   **Request Body (JSON):** `{"prompt": "User\'s workflow description...", "input_type": "text" | "speech_transcript"}`
        *   **Success Response:** `200 OK` with `{"workflow_id": "unique_id", "generated_code_skeleton": "python_code_string", "identified_tools": [{"name": "Tool1", "credentials_needed": ["API_KEY"]}, ...], "nodes": [...]}` (nodes for frontend visualization).
        *   **Error Response:** `400 Bad Request` for invalid input, `500 Internal Server Error` for processing failures.
    *   **Update Workflow with Credentials:**
        *   **Endpoint:** `POST /workflows/{workflow_id}/credentials`
        *   **Functionality:** Receives user-provided credentials (API keys, tokens) for a specific workflow. Updates the previously generated code skeleton by replacing placeholders with these actual values.
        *   **Request Body (JSON):** `{"credentials": {"Tool1_API_KEY": "user_value", ...}}`
        *   **Success Response:** `200 OK` with `{"workflow_id": "unique_id", "updated_code": "python_code_string_with_values"}`
        *   **Error Response:** `404 Not Found` if workflow ID is invalid, `400 Bad Request` for invalid credentials.

3.  **Code Validation Module:**
    *   **Validate Generated Code:**
        *   **Endpoint:** `POST /code/validate`
        *   **Functionality:** Receives Python code (either the initial skeleton or the code updated with credentials). Validates it for: module currency (no deprecated modules), correct syntax, and production-readiness (once placeholders are filled). **This may involve running linters, static analysis tools, or even sandboxed execution checks (potentially using AWS Lambda for sandboxing).** If validation fails, the backend might trigger regeneration (internal loop or flag to frontend).
        *   **Request Body (JSON):** `{"code_to_validate": "python_code_string", "validation_stage": "initial_skeleton" | "final_with_credentials"}`
        *   **Success Response:** `200 OK` with `{"is_valid": true | false, "validation_errors": [{"line": 10, "message": "Syntax error"}, ...], "suggestions": [...]}`
        *   **Error Response:** `500 Internal Server Error` if validation process itself fails.

4.  **Speech-to-Text Service Integration (Placeholder/Proxy):**
    *   **Endpoint:** `POST /speech/transcribe`
        *   **Functionality:** If the frontend uses a client-side speech-to-text library that requires backend processing or API key management (e.g., for Azure Speech Services, as mentioned in previous frontend prompts), this endpoint would act as a proxy. It receives audio data (or a reference to it) and forwards it to the actual speech service. **This might involve interaction with AWS Transcribe or a third-party service managed via AWS Secrets Manager.**
        *   **Request Body:** Depends on the speech service (e.g., audio blob, configuration).
        *   **Success Response:** `200 OK` with `{"transcript": "Transcribed text..."}`
        *   **Error Response:** Appropriate error codes based on the speech service.

5.  **Health Check Endpoint:**
    *   **Endpoint:** `GET /health`
    *   **Functionality:** A simple endpoint to check if the API service is running.
    *   **Success Response:** `200 OK` with `{"status": "ok"}`





## Technical Stack, Dependencies, and Project Structure

This section outlines the recommended technical stack, necessary Python dependencies, and a logical project structure for the FastAPI backend. The structure should promote modularity, maintainability, and scalability.

### 3.1. Technical Stack

*   **Web Framework:** FastAPI (Python)
*   **ASGI Server:** Uvicorn (for production deployment)
*   **HTTP Client:** `httpx` (for making asynchronous HTTP requests to external APIs like Google/GitHub OAuth, and potentially internal AWS services)
*   **Database ORM:** SQLAlchemy (with Alembic for migrations) for interacting with PostgreSQL.
*   **Authentication:** `python-jose` for JWT handling.
*   **Environment Variables:** `pydantic-settings` for managing configuration.
*   **Data Validation:** Pydantic (built-in with FastAPI).

### 3.2. Python Dependencies (`requirements.txt`)

The `requirements.txt` file should include at least the following core dependencies:

```
fastapi
uvicorn[standard]
httpx
python-jose[cryptography]
passlib[bcrypt] # For password hashing, if local user management is added later
sqlalchemy
psycopg2-binary # PostgreSQL adapter
alembic # For database migrations
pydantic-settings
python-multipart # For form data handling
```

### 3.3. Project Structure

The project should follow a clean, modular structure to separate concerns and facilitate development. The Replit agent should create directories and files as follows:

```
cue-backend/
├── main.py                 # Main FastAPI application instance, CORS setup, router inclusion
├── config.py               # Pydantic BaseSettings for environment variables and configurations
├── database/               # Database-related files
│   ├── __init__.py
│   ├── models.py           # SQLAlchemy ORM models (e.g., User model)
│   ├── database.py         # Database session management (get_db dependency)
│   └── migrations/         # Alembic migration scripts
├── auth/                   # Authentication module
│   ├── __init__.py
│   ├── router.py           # FastAPI router for authentication endpoints (OAuth callbacks, /users/me)
│   ├── services.py         # Business logic for OAuth (token exchange, user info fetching) and JWT operations
│   ├── schemas.py          # Pydantic models for auth-related data (e.g., Token, TokenData)
│   └── dependencies.py     # FastAPI dependencies for authentication (e.g., get_current_user)
├── workflows/              # Workflow processing module
│   ├── __init__.py
│   ├── router.py           # FastAPI router for workflow endpoints (generate, update credentials)
│   ├── services.py         # Business logic for workflow generation, NLP integration, code manipulation
│   └── schemas.py          # Pydantic models for workflow-related data (e.g., WorkflowInput, GeneratedCode)
├── validation/             # Code validation module
│   ├── __init__.py
│   ├── router.py           # FastAPI router for code validation endpoint
│   ├── services.py         # Business logic for code validation (syntax, module checks)
│   └── schemas.py          # Pydantic models for validation requests/responses
├── speech/                 # Speech-to-text proxy module (if needed)
│   ├── __init__.py
│   ├── router.py           # FastAPI router for speech-to-text endpoint
│   ├── services.py         # Business logic for interacting with speech-to-text APIs
│   └── schemas.py          # Pydantic models for speech-to-text requests/responses
├── core/                   # Core utilities and common components
│   ├── __init__.py
│   ├── exceptions.py       # Custom exception handlers
│   └── security.py         # JWT utility functions, password hashing (if needed)
├── .env.example            # Example environment variables file
├── Dockerfile              # Dockerfile for containerization (as previously discussed)
├── requirements.txt        # Python dependencies
└── README.md               # Project README with setup instructions
```

### 3.4. AWS Service Interaction Considerations

The FastAPI backend will interact with several AWS services, as outlined in the `VibeCodeMVPArchitectureRecommendation.pdf` and `VibeCodeMVPTechnicalBlueprint.pdf`. The Replit agent should consider the following when implementing the services:

*   **Database (PostgreSQL on RDS):** The `database/` module should be configured to connect to an external PostgreSQL database. This will involve using `psycopg2-binary` as the database adapter and configuring SQLAlchemy to connect to the RDS endpoint (via environment variables).
*   **Caching (Redis on ElastiCache):** While not explicitly detailed in the API endpoints above, consider how caching might be integrated (e.g., for session management, rate limiting, or caching frequently accessed data). This would involve a Redis client library (e.g., `redis-py`) connecting to the ElastiCache endpoint.
*   **AI/ML Services (OpenSearch, potentially SageMaker):**
    *   **OpenSearch:** The `workflows/services.py` and `validation/services.py` might interact with OpenSearch for tasks like semantic search of code snippets, storing workflow templates, or logging/monitoring. This would involve an OpenSearch client library (e.g., `opensearch-py`).
    *   **SageMaker:** For advanced NLP or code generation models, the `workflows/services.py` could potentially invoke SageMaker endpoints. This would involve using `boto3` (AWS SDK for Python) to interact with SageMaker.
*   **Secrets Management (AWS Secrets Manager):** All sensitive credentials (e.g., Google/GitHub `Client Secret`s, database credentials, API keys for external services) should be loaded from environment variables, which in a deployed AWS environment would be sourced from AWS Secrets Manager. The `config.py` should be set up to read these.
*   **Logging and Monitoring (CloudWatch):** Ensure standard Python logging is configured. In an AWS environment, logs from the FastAPI application running in ECS will automatically be sent to CloudWatch Logs. No specific `boto3` integration is typically needed for basic logging.
*   **S3 (for large files):** If workflow generation or validation involves handling large files (e.g., complex code templates, large input data), the application might interact with S3 using `boto3` for storage and retrieval.

**Note:** The Replit agent should focus on the *integration points* and *placeholders* for these AWS services (e.g., using environment variables for endpoints, including necessary client libraries). It does not need to set up the AWS infrastructure itself, as that is handled by Terraform.



## 4. Explaining Integration Points with the Frontend

Seamless communication between the FastAPI backend and the React frontend is paramount for the Cue MVP. This section details the critical integration points, ensuring that the frontend can effectively interact with the backend for authentication and data exchange.

### 4.1. Cross-Origin Resource Sharing (CORS)

Since the React frontend and the FastAPI backend will likely be served from different origins (different domains or ports), CORS must be properly configured on the FastAPI side. Without correct CORS headers, the browser will block requests from the frontend to the backend, leading to communication failures.

*   **Implementation:** The FastAPI application must include `CORSMiddleware`.
*   **Allowed Origins:** The `allow_origins` list in the CORS configuration must explicitly include all domains/ports where your React frontend will be hosted (e.g., `http://localhost:3000` for local development, `https://dev.cue-dev.com`, `https://staging.cue-dev.com`, `https://cue-prod.com` for deployed environments, and importantly, `https://cue-tracker-abzali20.replit.app/`).
*   **Allowed Methods and Headers:** Configure `allow_methods` to `["*"]` (or specific methods like `["GET", "POST", "PUT", "DELETE"]`) and `allow_headers` to `["*"]` to permit all necessary HTTP methods and headers, including the `Authorization` header for JWTs.
*   **Allow Credentials:** Set `allow_credentials=True` if you plan to use cookies for session management (though JWTs in `localStorage` are more common for SPAs).

**Example `main.py` CORS Configuration:**
```python
from fastapi.middleware.cors import CORSMiddleware

# ... (FastAPI app initialization)

origins = [
    "http://localhost:3000", # Frontend development server
    "https://dev.cue-dev.com", # Frontend dev deployment
    "https://staging.cue-dev.com", # Frontend staging deployment
    "https://cue-prod.com", # Frontend production deployment
    "https://cue-tracker-abzali20.replit.app/", # Replit deployed frontend URL
    # Add any other origins where your frontend might be hosted
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4.2. OAuth Callbacks and Redirection Flow

The OAuth login process involves a series of redirects between the frontend, the OAuth provider (Google/GitHub), and your FastAPI backend. The backend plays a crucial role in handling the intermediate steps and redirecting the user back to the frontend with the authentication token.

*   **Backend Callback Endpoints:** As detailed in Section 2 and 3, the FastAPI backend must expose specific `GET` endpoints (e.g., `/auth/google/callback`, `/auth/github/callback`) that match the `Authorized redirect URIs` configured in Google Cloud Console and GitHub OAuth Apps.
*   **Receiving Authorization Code:** These endpoints will receive the `code` and `state` parameters from the OAuth provider.
*   **Server-to-Server Token Exchange:** The backend will then use this `code` (along with its `client_id` and `client_secret`) to make a secure, server-to-server POST request to the OAuth provider\'s token endpoint to obtain the `access_token` and `refresh_token`.
*   **User Information Retrieval:** Using the `access_token`, the backend will fetch the user\'s profile information (email, name) from the OAuth provider\'s user info endpoint.
*   **User Management:** The backend will then either create a new user record in its database or retrieve an existing one based on the user\'s unique identifier from the OAuth provider.
*   **JWT Issuance and Frontend Redirection:** Upon successful authentication and user management, the backend will generate a JWT. This JWT is then passed back to the frontend. The most common and secure way for SPAs is to redirect the user\'s browser back to a specific frontend URL, appending the JWT as a query parameter or hash fragment.

**Example Backend Redirection (from `/auth/google/callback` or `/auth/github/callback`):**
```python
from fastapi.responses import RedirectResponse

# ... (after successful JWT generation)

frontend_redirect_url = f"https://cue-tracker-abzali20.replit.app/auth/callback?token={access_token}" # Updated to Replit frontend URL
return RedirectResponse(url=frontend_redirect_url)
```

*   **Frontend Callback Route:** The React frontend must have a dedicated route (e.g., `/auth/callback`) to catch this final redirect from the backend. This frontend route will then extract the JWT from the URL, store it, and navigate the user to the main application dashboard.

### 4.3. JWT-Based Authentication for Protected Routes

Once the frontend receives and stores the JWT, it will use this token to authenticate subsequent requests to protected backend API endpoints. The FastAPI backend must be configured to validate these JWTs.

*   **Frontend Request Header:** The React frontend will include the JWT in the `Authorization` header of all requests to protected routes, typically in the format `Authorization: Bearer <your_jwt_token>`.
*   **Backend JWT Validation:** The FastAPI backend will implement a dependency (e.g., `Depends(get_current_user)`) that:
    *   Extracts the JWT from the `Authorization` header.
    *   Validates the JWT\'s signature using the `SECRET_KEY`.
    *   Checks for token expiration.
    *   Decodes the JWT payload to retrieve user information (e.g., email, user ID).
    *   Raises an `HTTPException` (e.g., `401 Unauthorized`) if the token is invalid or missing.
*   **Protected Endpoints:** Any API endpoint that requires authentication (e.g., `/workflows/generate`, `/users/me`) will use this JWT validation dependency.

This robust integration strategy ensures that the frontend and backend communicate securely and effectively, providing a seamless user experience for authentication and application functionality.


## 5. Security Considerations and Final Instructions

Security is paramount for any application, especially one handling user authentication and potentially sensitive code. The Replit agent must adhere to the following security best practices during implementation.

### 5.1. Security Best Practices

*   **Environment Variables for Secrets:** All sensitive information (e.g., `GOOGLE_CLIENT_SECRET`, `GITHUB_CLIENT_SECRET`, `SECRET_KEY`, database credentials, API keys for AWS services) MUST be loaded from environment variables. Never hardcode these values in the source code. Provide clear instructions in the `README.md` on how to set these environment variables.
*   **Input Validation:** Implement robust input validation for all incoming API requests to prevent common vulnerabilities like SQL injection, cross-site scripting (though less critical for a pure API), and buffer overflows. Use Pydantic models for request body and query parameter validation.
*   **Error Handling:** Implement comprehensive error handling. Avoid exposing sensitive information in error messages. Return generic, informative error responses to the client.
*   **Logging:** Implement structured logging for all critical events (e.g., authentication attempts, API calls, errors). This will be crucial for monitoring and debugging in a production environment.
*   **CORS Security:** While `allow_origins=["*"]` might be convenient for development, for production, ensure `allow_origins` is restricted to only your trusted frontend domains.
*   **JWT Security:**
    *   Ensure the `SECRET_KEY` used for signing JWTs is strong and kept confidential.
    *   Validate JWTs for expiration, signature, and issuer on every protected endpoint.
    *   Consider token revocation mechanisms (e.g., a blacklist) for immediate invalidation of compromised tokens, although for an MVP, short token expiry might suffice.
*   **State Parameter Validation:** As emphasized in Section 4, rigorously validate the `state` parameter in OAuth callbacks to prevent CSRF attacks.
*   **HTTPS:** Although Replit environments might use HTTP, the generated code should be ready for HTTPS deployment. Mention that all production communication will occur over HTTPS.

### 5.2. Final Instructions for Replit Agent

*   **Code Quality:** Write clean, well-commented, and idiomatic Python code following FastAPI best practices.
*   **Testing:** Include basic unit tests for critical functionalities (e.g., OAuth token exchange, JWT generation/validation). (Optional for MVP, but highly recommended).
*   **README.md:** Generate a comprehensive `README.md` file that includes:
    *   Project setup instructions (how to run the FastAPI app locally).
    *   Instructions for setting up environment variables.
    *   Details on how to run tests.
    *   A list of all exposed API endpoints with example requests/responses.
    *   Instructions on how to connect it with the existing React frontend.
*   **No UI Generation:** Reiterate that no UI code, templates, or static file serving for frontend assets should be generated. The output must be a pure API service.
*   **Modularity:** Maintain the proposed project structure to ensure clear separation of concerns.

By following these detailed instructions, the Replit agent should be able to generate a high-quality, functional, and secure FastAPI backend that perfectly complements the existing Cue frontend module.

