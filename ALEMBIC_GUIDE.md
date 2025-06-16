# Alembic Migration Setup Guide

## Overview
This FastAPI project now uses Alembic for database migrations, providing version-controlled schema management similar to Django's migration system.

## Quick Start

### Development (Docker Compose)
```bash
# Start services (migrations run automatically)
docker-compose up --build

# To run migrations manually in container
docker-compose exec app alembic upgrade head

# To create new migration
docker-compose exec app alembic revision --autogenerate -m "Description of changes"
```

### Production
```bash
# Run migrations before starting the application
alembic upgrade head

# Start the application
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Migration Commands

### Create New Migration
```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new table"

# Create empty migration file
alembic revision -m "Custom migration"
```

### Apply Migrations
```bash
# Upgrade to latest migration
alembic upgrade head

# Upgrade to specific revision
alembic upgrade <revision_id>

# Downgrade one revision
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade <revision_id>
```

### Migration History
```bash
# Show current revision
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic show <revision_id>
```

## File Structure
```
├── alembic/
│   ├── versions/           # Migration files
│   ├── env.py             # Alembic environment configuration
│   ├── script.py.mako     # Migration template
│   └── README
├── alembic.ini            # Alembic configuration
├── scripts/
│   └── migrate.sh         # Docker migration script
└── database/
    └── models.py          # SQLAlchemy models
```

## Configuration

### Environment Variables
The migration system uses the same `DATABASE_URL` from your application settings:
- **Development**: `postgresql://cue_user:cue_password@db:5432/cue_development`
- **Production**: Set via environment variable

### Alembic Configuration
- `alembic.ini`: Main configuration file
- `alembic/env.py`: Environment setup (configured to use your models and settings)

## Docker Integration

### Automatic Migrations
The Docker container automatically runs migrations on startup via `scripts/migrate.sh`:
1. Waits for database to be ready
2. Runs `alembic upgrade head`
3. Starts the FastAPI application

### Manual Migration in Docker
```bash
# Run migration in running container
docker-compose exec app alembic upgrade head

# Create new migration in container
docker-compose exec app alembic revision --autogenerate -m "New changes"
```

## Best Practices

### Development Workflow
1. Modify models in `database/models.py`
2. Generate migration: `alembic revision --autogenerate -m "Description"`
3. Review generated migration file
4. Test migration: `alembic upgrade head`
5. Commit both model changes and migration file

### Production Deployment
1. Always backup database before migrations
2. Test migrations on staging environment first
3. Run migrations before deploying new application code
4. Monitor migration execution for large tables

### Migration Guidelines
- **Always review** auto-generated migrations before applying
- **Test migrations** on development data first
- **Use descriptive names** for migration messages
- **Don't edit** applied migration files (create new ones instead)
- **Backup database** before running migrations in production

## Troubleshooting

### Common Issues
1. **"Target database is not up to date"**: Run `alembic upgrade head`
2. **"Can't locate revision"**: Check if migration files exist in `alembic/versions/`
3. **Connection errors**: Verify `DATABASE_URL` is correct
4. **Permission errors**: Ensure database user has necessary privileges

### Reset Migrations (Development Only)
```bash
# Drop all tables and start fresh
alembic downgrade base
alembic upgrade head
```

## Migration vs. create_all()

### Before (create_all)
```python
# Old approach - no version control
Base.metadata.create_all(bind=engine)
```

### After (Alembic)
```python
# New approach - version controlled
# Tables created via: alembic upgrade head
```

This provides:
- ✅ Version-controlled schema changes
- ✅ Safe production updates
- ✅ Rollback capabilities
- ✅ Team collaboration on schema changes
- ✅ Audit trail of database changes

