"""
Redis connection management and configuration.
"""
import redis
from typing import Optional
import json
import logging

from config import settings

logger = logging.getLogger(__name__)

class RedisManager:
    """Redis connection manager with connection pooling."""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.connection_pool: Optional[redis.ConnectionPool] = None
    
    def connect(self) -> Optional[redis.Redis]:
        """Create Redis connection with connection pooling."""
        try:
            if not self.connection_pool:
                self.connection_pool = redis.ConnectionPool(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    decode_responses=True,
                    max_connections=20,
                    retry_on_timeout=True,
                    socket_keepalive=True,
                    socket_keepalive_options={},
                    socket_connect_timeout=5  # 5 second timeout
                )
            
            if not self.redis_client:
                self.redis_client = redis.Redis(connection_pool=self.connection_pool)
                
                # Test connection with timeout
                self.redis_client.ping()
                logger.info(f"Connected to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
                
            return self.redis_client
            
        except redis.ConnectionError as e:
            logger.warning(f"Redis not available: {e}. Application will continue without Redis caching.")
            return None
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Application will continue without Redis caching.")
            return None
    
    def disconnect(self):
        """Close Redis connection."""
        if self.redis_client:
            self.redis_client.close()
            self.redis_client = None
        if self.connection_pool:
            self.connection_pool.disconnect()
            self.connection_pool = None
        logger.info("Disconnected from Redis")
    
    def get_client(self) -> Optional[redis.Redis]:
        """Get Redis client, creating connection if needed."""
        if not self.redis_client:
            return self.connect()
        return self.redis_client

# Global Redis manager instance
redis_manager = RedisManager()

def get_redis() -> Optional[redis.Redis]:
    """
    Dependency to get Redis client.
    This will be used as a FastAPI dependency.
    """
    return redis_manager.get_client()

# Utility functions for common Redis operations
class RedisCache:
    """Helper class for common Redis caching operations."""
    
    @staticmethod
    def set_json(key: str, value: dict, expire: int = 3600) -> bool:
        """Store JSON data in Redis with expiration."""
        try:
            redis_client = get_redis()
            if redis_client is None:
                return False
            redis_client.setex(key, expire, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"Error setting Redis key {key}: {e}")
            return False
    
    @staticmethod
    def get_json(key: str) -> Optional[dict]:
        """Retrieve JSON data from Redis."""
        try:
            redis_client = get_redis()
            if redis_client is None:
                return None
            data = redis_client.get(key)
            if data:
                return json.loads(str(data))
            return None
        except Exception as e:
            logger.error(f"Error getting Redis key {key}: {e}")
            return None
    
    @staticmethod
    def delete(key: str) -> bool:
        """Delete key from Redis."""
        try:
            redis_client = get_redis()
            if redis_client is None:
                return False
            return bool(redis_client.delete(key))
        except Exception as e:
            logger.error(f"Error deleting Redis key {key}: {e}")
            return False
    
    @staticmethod
    def exists(key: str) -> bool:
        """Check if key exists in Redis."""
        try:
            redis_client = get_redis()
            if redis_client is None:
                return False
            return bool(redis_client.exists(key))
        except Exception as e:
            logger.error(f"Error checking Redis key {key}: {e}")
            return False
    
    @staticmethod
    def set_with_ttl(key: str, value: str, ttl: int = 3600) -> bool:
        """Set string value with TTL."""
        try:
            redis_client = get_redis()
            if redis_client is None:
                return False
            redis_client.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.error(f"Error setting Redis key {key} with TTL: {e}")
            return False
    
    @staticmethod
    def increment(key: str, amount: int = 1) -> Optional[int]:
        """Increment a counter in Redis."""
        try:
            redis_client = get_redis()
            if redis_client is None:
                return None
            result = redis_client.incrby(key, amount)
            return result
        except Exception as e:
            logger.error(f"Error incrementing Redis key {key}: {e}")
            return None

