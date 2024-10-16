from motor.motor_asyncio import AsyncIOMotorClient
from app.configs import MONGO_URL, MONGO_DB_NAME
from datetime import datetime

class MongoDB:
    
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.db = None


    async def connect(self):
        self.client = AsyncIOMotorClient(MONGO_URL, maxPoolSize=10)
        self.db = self.client[MONGO_DB_NAME]


    async def close(self):
        self.client.close()


    async def create_collection_entry(self, collection_name: str):
        """Create an entry for a new collection in the 'collections_metadata' collection."""
        try:
            # Check if collection already exists
            existing_collection = await self.db['collections_metadata'].find_one({"name": collection_name})
            if existing_collection:
                raise Exception("Collection already exists in metadata.")
            # Insert collection entry
            result = await self.db['collections_metadata'].insert_one({"name": collection_name})
            return result.inserted_id
        except Exception as e:
            raise Exception(f"Failed to create collection entry: {str(e)}")


    async def delete_collection_entry(self, collection_name: str):
        """Delete a collection and its metadata entry."""
        try:
            existing_collection = await self.db['collections_metadata'].find_one({"name": collection_name})
            if not existing_collection:
                raise Exception("Collection not found in metadata.")
            
            # Delete metadata entry and drop collection
            await self.db['collections_metadata'].delete_one({"name": collection_name})
            await self.db.drop_collection(collection_name)
            
            return {"message": f"Collection '{collection_name}' deleted successfully!"}
        except Exception as e:
            raise Exception(f"Failed to delete collection: {str(e)}")


mongodb = MongoDB()

async def get_mongodb():
    if mongodb.db is None:
        raise Exception("MongoDB client is not connected.")
    return mongodb.db


async def add_conversation_to_db(db, sender_id: str, collection_name: str, query, response):
    """
    Inserts or updates a conversation document in MongoDB for the given sender_id and collection_name.

    Args:
        db: The MongoDB database object.
        sender_id (str): The ID of the sender.
        collection_name (str): The collection name for the agent.
        query: The user's query (should be Pydantic model, converted to dict).
        response: The response from the agent.
    """
    conversation_entry = {
        "query": query.dict(),  # Assuming query is a Pydantic model
        "response": response,
        "timestamp": datetime.utcnow()
    }
    
    # Update the conversation in MongoDB
    await db["conversations"].update_one(
        {"sender_id": sender_id, "collection_name": collection_name},
        {"$push": {"conversations": conversation_entry}},
        upsert=True  # Creates the document if it doesn't exist
    )