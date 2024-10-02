from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
from configs import OPENAI_MODEL, UPLOAD_DIR
from pathlib import Path
from typing import Dict, List
import os
from agent import ask_agent
from vector_store import VectorStore
from data_handler import DataPreprocessor


app = FastAPI()
UPLOAD_DIR = Path(UPLOAD_DIR)
UPLOAD_DIR.mkdir(exist_ok=True)


class Query(BaseModel):
    query: str


@app.get("/")
def root():
    return {"message": "Welcome to Agentic RAG"}


@app.post("/api/query")
def ask(query: Query, collection_name: str) -> Dict:
    """
    Handles queries and returns the response from the agent.

    Args:
        query (Query): The query object containing the user's query.

    Returns:
        dict: A dictionary containing the agent's response.
    """

    response = ask_agent(query, collection_name)
    return {"response": response}


@app.post("/api/create_collection")
def create_collection(collection_name: str) -> Dict:
    """
    Creates a new Qdrant collection.

    Args:
        collection_name (str): The name of the collection to create.

    Returns:
        dict: A dictionary containing a success message.
    """
    
    vector_store = VectorStore(collection_name)
    vector_store.create_collection()
    return {"message": f"{collection_name} collection created successfully!"}


@app.post("/api/upload_docs")
async def upload_docs(file: UploadFile = File(...),
                      collection_name: str = Form(...),
                      chunk_size: int = Form(1000),
                      chunk_overlap: int = Form(50)
                      ) -> Dict:
    """
    Uploads preprocessed data with embeddings to a Qdrant collection.

    Args:
        file (UploadFile): The uploaded file containing data.
        collection_name (str): The name of the Qdrant collection to upload the data to.

    Returns:
        dict: A dictionary containing the upload status message.
    """

    filename = file.filename
    content = await file.read()

    # Save the uploaded file temporarily
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as buffer:
        buffer.write(content)

    preprocessor = DataPreprocessor(UPLOAD_DIR, filename, chunk_size, chunk_overlap)
    docs = preprocessor(filename)
    if docs is None:
        raise HTTPException(status_code=400, detail="Invalid file format")


    vector_store = VectorStore(collection_name)

    try:
        vector_store.add_documents(docs) 
        status = "SUCCESS"
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Document upload failed: {str(e)}")
    
    # Remove the temporary file
    os.remove(file_path)

    if status == "SUCCESS":
        return {"message": "Embeddings uploaded successfully!"}
    else:
        return {"message": "Upload failed."}
    

@app.delete("/api/delete_docs")
def delete_docs(collection_name: str, ids: List[str]) -> Dict:
    """
    Deletes documents from a Qdrant collection.

    Args:
        collection_name (str): The name of the collection to delete documents from.
        ids (List[str]): A list of document IDs to delete.

    Returns:
        dict: A dictionary containing a success message.
    """

    vector_store = VectorStore(collection_name)
    vector_store.delete_documents(ids)
    return {"message": f"{collection_name} collection documents deleted successfully!"}