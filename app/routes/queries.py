from fastapi import APIRouter, Depends, HTTPException
from app.agent import ask_agent
from app.models.schema import Query
from app.db.mongodb import get_mongodb, add_conversation_to_db
from typing import Dict

router = APIRouter()


@router.post("/ask")
async def ask(query: Query, sender_id: str, collection_name: str) -> Dict:
    """
    Handles queries and returns the response from the agent.

    Args:
        query (Query): The query object containing the user's query.
        collection_name (str): The collection name for the agent to use.

    Returns:
        dict: A dictionary containing the agent's response.
    """
    try:
        response = ask_agent(query, collection_name)

        db = await get_mongodb()

        await add_conversation_to_db(db, sender_id, collection_name, query, response)

        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))