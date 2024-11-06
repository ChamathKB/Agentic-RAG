from fastapi import APIRouter, Depends, HTTPException
from app.agent import ask_agent
from app.models.schema import Query
from app.db.mongodb import get_mongodb, add_conversation_to_db
from app.db.redis import get_redis
from typing import Dict
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/ask")
async def ask(query: Query, sender_id: str, collection_name: str, redis=Depends(get_redis)) -> Dict:
    """
    Handles queries and returns the response from the agent.

    Args:
        query (Query): The query object containing the user's query.
        collection_name (str): The collection name for the agent to use.

    Returns:
        dict: A dictionary containing the agent's response.
    """
    try:
        conversation_key = f"conversation_tracker:{sender_id}:{collection_name}"
        conversation_data = await redis.hgetall(conversation_key)

        if not conversation_data:
            conversation_data = {
                "message_count": 1,
                "last_interaction": datetime.utcnow().isoformat(),
                "status": "ongoing"
            }
            await redis.hset(conversation_key, mapping=conversation_data)
            await redis.expire(conversation_key, 900)
        else:
            conversation_data["message_count"] = int(conversation_data.get("message_count", 0)) + 1
            conversation_data["last_interaction"] = datetime.utcnow().isoformat()
            await redis.hset(conversation_key, mapping=conversation_data)
            await redis.expire(conversation_key, 900)

        response = ask_agent(query, collection_name)

        db = await get_mongodb()

        await add_conversation_to_db(db, sender_id, collection_name, query, response)

        conversation_data.update({
            "last_response": response,
            "status": "responded"
        })

        await redis.hset(conversation_key, mapping=conversation_data)
        await redis.expire(conversation_key, 900)

        return {"response": response}
    except Exception as e:
        logger.debug(f"Error in ask endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))