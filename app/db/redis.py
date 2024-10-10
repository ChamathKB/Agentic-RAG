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
    return redis.redis