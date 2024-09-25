from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from configs import OPENAI_MODEL, UPLOAD_DIR
from pathlib import Path
from typing import Dict
import shutil
import os
from agent import ask_agent

app = FastAPI()
UPLOAD_DIR = Path(UPLOAD_DIR)
UPLOAD_DIR.mkdir(exist_ok=True)

class Query(BaseModel):
    query: str

@app.get("/")
def root():
    return {"message": "Welcome to Agentic RAG"}


@app.post("/api/query")
def ask(query: Query):
    response = ask_agent(query)
    return {"response": response}


@app.post("/api/create_collection")
def create_collection(collection_name: str):
    # TODO: add collection creating process
    return {"message": "Collection created successfully!"}


@app.post("/api/upload_docs")
async def upload_docs(file: UploadFile = File(...)) -> Dict:
    """
    Uploads preprocessed data with embeddings to a Qdrant collection.

    Args:
        file (UploadFile): The uploaded file containing data.

    Returns:
        dict: A dictionary containing the upload status message.
    """

    filename = file.filename
    content = await file.read()

    # Save the uploaded file temporarily
    with open(os.path.join(UPLOAD_DIR, filename), "wb") as buffer:
        buffer.write(content)

    # TODO: add doc uploading logic
    # uploader =
    # status =

    # Remove the temporary file
    os.remove(os.path.join(UPLOAD_DIR, filename))

    # if status == UploadStatus.SUCCESS:
    #     return {"message": "Embeddings uploaded successfully!"}
    # else:
    #     return {"message": f"Upload failed: {status.value}"}