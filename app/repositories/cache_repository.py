from typing import Optional, Any
import json
import redis.asyncio as redis
from app.core.config import settings
from app.models.security import SecurityScore
import logging

logger = logging.getLogger(__name__)


class CacheRepository:
    """Repository for Redis cache operations"""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None

    async def connect(self):
        """Connect to Redis"""
        self.redis_client = redis.from_url(
            settings.REDIS_URL, decode_responses=True)

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()

    async def get_ip_score(self, ip: str) -> Optional[SecurityScore]:
        """Get IP security score from cache"""
        try:
            if not self.redis_client:
                return None

            cached_data = await self.redis_client.get(f"ip_score:{ip}")
            if cached_data:
                data = json.loads(cached_data)
                return SecurityScore(**data)
        except Exception as e:
            logger.error(f"Error getting IP score from cache: {e}")
        return None

    async def set_ip_score(self, score: SecurityScore, ttl: int = None) -> bool:
        """Set IP security score in cache"""
        try:
            if not self.redis_client:
                return False

            cache_ttl = ttl or settings.CACHE_TTL
            data = score.model_dump()
            data['last_updated'] = data['last_updated'].isoformat()

            await self.redis_client.setex(
                f"ip_score:{score.ip}",
                cache_ttl,
                json.dumps(data)
            )
            return True
        except Exception as e:
            logger.error(f"Error setting IP score in cache: {e}")
            return False

    async def increment_counter(self, key: str, ttl: int = 3600) -> int:
        """Increment a counter with TTL"""
        try:
            if not self.redis_client:
                return 0

            pipe = self.redis_client.pipeline()
            await pipe.incr(key)
            await pipe.expire(key, ttl)
            result = await pipe.execute()
            return result[0]
        except Exception as e:
            logger.error(f"Error incrementing counter: {e}")
            return 0
