"""
Example usage of Redis and PostgreSQL in FastAPI endpoints.
This demonstrates how to use both databases in your application.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import json

from database.database import get_db
from database.redis_client import get_redis, RedisCache
import redis

router = APIRouter()

@router.get("/example/cache-test")
async def cache_test(redis_client = Depends(get_redis)):
    """Test Redis connection and basic operations."""
    if redis_client is None:
        return {
            "redis_status": "not_available",
            "message": "Redis caching is not available in this environment",
            "basic_test": None,
            "json_test": None,
            "cache_exists": False
        }
    
    try:
        # Test basic Redis operations
        redis_client.set("test_key", "Hello Redis!", ex=60)
        value = redis_client.get("test_key")
        
        # Test JSON caching
        test_data = {"message": "Hello from Redis", "timestamp": "2024-01-01"}
        RedisCache.set_json("test_json", test_data, expire=300)
        cached_data = RedisCache.get_json("test_json")
        
        return {
            "redis_status": "connected",
            "basic_test": value,
            "json_test": cached_data,
            "cache_exists": RedisCache.exists("test_json")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")

@router.get("/example/database-test")
async def database_test(db: Session = Depends(get_db)):
    """Test PostgreSQL connection and basic operations."""
    try:
        # Test database connection
        result = db.execute("SELECT version()").fetchone()
        
        # Test table creation (example)
        db.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert test data
        db.execute("""
            INSERT INTO test_table (name) VALUES ('Test Entry')
            ON CONFLICT DO NOTHING
        """)
        
        # Query test data
        test_data = db.execute("SELECT * FROM test_table LIMIT 5").fetchall()
        
        db.commit()
        
        return {
            "database_status": "connected",
            "version": result[0] if result else "Unknown",
            "test_data": [dict(row._mapping) for row in test_data]
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/example/combined-test")
async def combined_test(
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis)
):
    """Test both PostgreSQL and Redis working together."""
    try:
        # Check cache first (if Redis is available)
        cache_key = "user_stats"
        cached_stats = None
        cache_available = redis_client is not None
        
        if cache_available:
            cached_stats = RedisCache.get_json(cache_key)
        
        if cached_stats:
            return {
                "source": "cache",
                "data": cached_stats,
                "cache_hit": True,
                "cache_available": cache_available
            }
        
        # If not in cache, query database
        result = db.execute("""
            SELECT 
                COUNT(*) as total_records,
                MAX(created_at) as latest_record
            FROM test_table
        """).fetchone()
        
        stats = {
            "total_records": result[0] if result else 0,
            "latest_record": str(result[1]) if result and result[1] else None,
            "generated_at": "2024-01-01T00:00:00"
        }
        
        # Cache the result for 5 minutes (if Redis is available)
        if cache_available:
            RedisCache.set_json(cache_key, stats, expire=300)
        
        return {
            "source": "database",
            "data": stats,
            "cache_hit": False,
            "cached_for": "5 minutes"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Combined test error: {str(e)}")

@router.post("/example/rate-limit-test")
async def rate_limit_test(
    user_id: str,
    redis_client = Depends(get_redis)
):
    """Example of using Redis for rate limiting."""
    if redis_client is None:
        return {
            "allowed": True,
            "message": "Rate limiting not available (Redis not connected)",
            "requests_count": 1,
            "limit": "unlimited",
            "window": "N/A"
        }
    
    try:
        rate_limit_key = f"rate_limit:user:{user_id}"
        current_requests = redis_client.get(rate_limit_key)
        
        if current_requests is None:
            # First request in the time window
            redis_client.setex(rate_limit_key, 60, 1)  # 1 minute window
            return {
                "allowed": True,
                "requests_count": 1,
                "limit": 10,
                "window": "1 minute"
            }
        
        current_count = int(str(current_requests))
        if current_count >= 10:  # Rate limit: 10 requests per minute
            return {
                "allowed": False,
                "requests_count": current_count,
                "limit": 10,
                "message": "Rate limit exceeded"
            }
        
        # Increment counter
        new_count = redis_client.incr(rate_limit_key)
        
        return {
            "allowed": True,
            "requests_count": new_count,
            "limit": 10,
            "window": "1 minute"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rate limit error: {str(e)}")

@router.delete("/example/clear-cache")
async def clear_cache(redis_client = Depends(get_redis)):
    """Clear test cache entries."""
    if redis_client is None:
        return {
            "message": "Cache clearing not available (Redis not connected)",
            "deleted_keys": 0,
            "keys": []
        }
    
    try:
        keys_to_delete = ["test_key", "test_json", "user_stats"]
        deleted_count = 0
        
        for key in keys_to_delete:
            if redis_client.delete(key):
                deleted_count += 1
        
        return {
            "message": "Cache cleared",
            "deleted_keys": deleted_count,
            "keys": keys_to_delete
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache clear error: {str(e)}")

