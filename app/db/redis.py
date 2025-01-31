import aioredis

from app.configs import REDIS_URL


class Redis:

    def __init__(self):
        self.redis = None

    async def connect(self):
        self.redis = aioredis.Redis.from_url(REDIS_URL, max_connections=10)

    async def close(self):
        if self.redis:
            await self.redis.close()


redis = Redis()


async def get_redis():
    """
    Returns the Redis connection instance.

    Returns:
        aioredis.Redis: The Redis connection object used for interacting with Redis.
        None: If Redis connection has not been established yet.
    """
    return redis.redis
