from motor.motor_asyncio import AsyncIOMotorClient
from app.configs import MONGO_URL, MONGO_DB_NAME
from app.models.schema import DocIds
from typing import Dict
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


async def add_uploaded_docs_to_db(db, collection_name: str, filename: str, doc_ids: DocIds):
    """
    Inserts document metadata into MongoDB after successful upload.

    Args:
        db (Database): The MongoDB database object.
        collection_name (str): The name of the Qdrant collection.
        filename (str): The name of the uploaded file.
        doc_ids (List[str]): List of document IDs created in Qdrant.
    """
    upload_entry = {
        "collection_name": collection_name,
        "filename": filename,
        "doc_ids": doc_ids,
        "uploaded_at": datetime.utcnow()
    }

    await db["document_uploads"].insert_one(upload_entry)


async def delete_docs_from_db(db, collection_name: str, ids: DocIds) -> Dict:
    """
    Removes document metadata from MongoDB after deletion from Qdrant.

    Args:
        db (Database): The MongoDB database object.
        collection_name (str): The name of the Qdrant collection.
        ids (List[str]): List of document IDs to delete.

    Returns:
        dict: A dictionary confirming the deletion.
    """
    delete_result = await db["document_uploads"].update_one(
        {"collection_name": collection_name},
        {"$pull": {"doc_ids": {"$in": ids}}}
    )

    if delete_result.modified_count == 0:
        return {"message": "No documents found to delete in MongoDB"}
    
    return {"message": f"Deleted {len(ids)} documents from MongoDB for collection {collection_name}"}