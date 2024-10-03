import aioredis
from app.configs import REDIS_URL


class Redis:

    def __init__(self):
        self.redis = None

    async def connect(self):
        self.redis = await aioredis.create_redis_pool(REDIS_URL, minsize=5, maxsize=10)

    async def close(self):
        self.redis.close()
        await self.redis.wait_closed()

redis = Redis()

async def get_redis():
    await redis.redis