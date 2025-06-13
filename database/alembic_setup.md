# Database Setup Instructions for AWS RDS PostgreSQL

## 1. Create AWS RDS PostgreSQL Instance

Create your PostgreSQL database in AWS RDS and note the following connection details:
- **Endpoint**: Your RDS endpoint (e.g., `cue-db.cluster-xxxxx.us-east-1.rds.amazonaws.com`)
- **Port**: Usually 5432
- **Database Name**: The database name you created
- **Username**: Your database username
- **Password**: Your database password

## 2. Update Environment Variables

Update your `.env` file with the actual AWS RDS connection string:

```bash
DATABASE_URL=postgresql://your_username:your_password@your_rds_endpoint:5432/your_database_name
```

## 3. Initialize Alembic (Database Migrations)

Once your AWS RDS database is configured, initialize Alembic for database migrations:

```bash
# Initialize Alembic (only run once)
alembic init alembic

# Generate initial migration
alembic revision --autogenerate -m "Initial database schema"

# Apply migrations to your AWS RDS database
alembic upgrade head
```

## 4. Database Models Created

The following tables will be created in your AWS RDS PostgreSQL database:

- **users**: User profiles from OAuth (Google/GitHub)
- **oauth_tokens**: OAuth refresh tokens and access tokens
- **workflows**: Generated workflow code and metadata
- **workflow_credentials**: User-provided API keys for workflows
- **validation_logs**: Code validation history and results

## 5. Security Considerations

- Ensure your RDS instance has proper security groups configured
- Use AWS Secrets Manager for production credentials
- Enable SSL/TLS connections to your RDS instance
- Consider using IAM database authentication for enhanced security

## 6. Connection Testing

Test your database connection:

```python
from database.database import engine
from sqlalchemy import text

# Test connection
with engine.connect() as conn:
    result = conn.execute(text("SELECT version()"))
    print(result.fetchone())
```