from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.configs import MONGO_URL, MONGO_DB_NAME
from app.models.schema import DocIds, Query, Response
from typing import Dict
from datetime import datetime

COLLECTION_CONVERSATIONS = "conversations"
COLLECTION_DOCUMENT_UPLOADS = "document_uploads"


class MongoDB:
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.db: AsyncIOMotorDatabase = None

    async def connect(self):
        if self.client is None:
            self.client = AsyncIOMotorClient(MONGO_URL, maxPoolSize=10)
            self.db = self.client[MONGO_DB_NAME]

    async def close(self):
        if self.client:
            self.client.close()
            self.client = None


mongodb = MongoDB()


async def get_mongodb() -> AsyncIOMotorDatabase:
    """
    Get MongoDB database connection
    Returns:
        AsyncIOMotorDatabase: MongoDB database connection object
    Raises:
        Exception: If MongoDB client is not connected
    """
    if mongodb.db is None:
        raise Exception("MongoDB client is not connected.")
    return mongodb.db


async def add_conversation_to_db(
    db: AsyncIOMotorDatabase, sender_id: str, collection_name: str, query: Query, response: Response
) -> Dict:
    """
    Add conversation to database
    Args:
        db (AsyncIOMotorDatabase): Database connection object
        sender_id (str): Unique identifier of the user/sender
        collection_name (str): Name of the collection being queried
        query (Query): User's query object
        response (Response): LLM Agent response object 
    Returns:
        Dict: Dictionary containing number of modified documents
              {"modified_count": int}       
    Raises:
        Exception: If there is an error adding conversation to database
    """
    try:
        conversation_entry = {
            "query": query.dict(),  
            "response": response,
            "timestamp": datetime.utcnow(),
        }
        result = await db[COLLECTION_CONVERSATIONS].update_one(
            {"sender_id": sender_id, "collection_name": collection_name},
            {"$push": {"conversations": conversation_entry}},
            upsert=True,
        )
        return {"modified_count": result.modified_count}
    except Exception as e:
        raise Exception(f"Failed to add conversation: {e}")


async def add_uploaded_docs_to_db(
    db: AsyncIOMotorDatabase, collection_name: str, filename: str, doc_ids: DocIds
) -> Dict:
    """
    Add uploaded docs to database
    Args:
        db (AsyncIOMotorDatabase) : database
        collection_name (str) : collection name quried
        filename (str) : uploaded file name
        doc_ids (DocIds) : UUIDs of documnets uploaded
    Return:
        Dict : Dictionary containing the inserted document's ID
              {"inserted_id": ObjectId} on success
    Raises:
        Exception: If there is an error adding documents to database
    """
    try:
        upload_entry = {
            "collection_name": collection_name,
            "filename": filename,
            "doc_ids": doc_ids,
            "uploaded_at": datetime.utcnow(),
        }
        result = await db[COLLECTION_DOCUMENT_UPLOADS].insert_one(upload_entry)
        return {"inserted_id": result.inserted_id}
    except Exception as e:
        raise Exception(f"Failed to add uploaded docs: {e}")


async def delete_docs_from_db(
    db: AsyncIOMotorDatabase, collection_name: str, ids: DocIds
) -> Dict:
    """
    Delete documents from database
    Args:
        db (AsyncIOMotorDatabase): Database connection object
        collection_name (str): Name of the collection being queried
        ids (DocIds): List of document IDs to delete
    Returns:
        Dict: Dictionary containing deletion status message and count
              {"message": str, "deleted_count": int} on success
              {"message": str} if no documents found
    Raises:
        Exception: If there is an error deleting documents from database
    """
    try:
        delete_result = await db[COLLECTION_DOCUMENT_UPLOADS].update_one(
            {"doc_ids": {"$in": ids}},
            {"$pull": {"doc_ids": {"$in": ids}}},
        )
        if delete_result.modified_count == 0:
            return {"message": "No documents found to delete in MongoDB"}
        return {"message": f"Deleted {len(ids)} documents from MongoDB for collection {collection_name}",
                "deleted_count": delete_result.modified_count,
                }
    except Exception as e:
        raise Exception(f"Failed to delete documents: {e}")
