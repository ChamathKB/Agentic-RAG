from motor.motor_asyncio import AsyncIOMotorClient
from app.configs import MONGO_URI, MONGO_DB_NAME

class MongoDB:
    
    def __init__(self):
        self.client: AsyncIOMotorClient = None

    async def connect(self):
        self.client = AsyncIOMotorClient(MONGO_URI, maxPoolSize=10)

    async def close(self):
        self.client.close()


mongodb = MongoDB()

async def get_mongodb():
    return mongodb.db