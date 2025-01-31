import os
from typing import Dict

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.db.data_handler import DataPreprocessor
from app.db.mongodb import add_uploaded_docs_to_db, delete_docs_from_db, get_mongodb
from app.db.vector_store import VectorStore
from app.models.schema import DocIds

router = APIRouter()

UPLOAD_DIR = "upload"


@router.post("/create_collection")
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


@router.post("/upload_docs")
async def upload_docs(
    file: UploadFile = File(...),
    collection_name: str = Form(...),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(50),
) -> Dict:
    """
    Uploads preprocessed data with embeddings to a Qdrant collection.

    Args:
        file (UploadFile): The uploaded file containing data.
        collection_name (str): The name of the Qdrant collection to upload the data to.
        chunk_size (int): The size of chunks to break the data into.
        chunk_overlap (int): The overlap between chunks.

    Returns:
        dict: A dictionary containing the upload status message.
    """

    filename = file.filename
    content = await file.read()

    # Save the uploaded file temporarily
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        with open(file_path, "wb") as buffer:
            buffer.write(content)

        # Process the file to generate document chunks
        preprocessor = DataPreprocessor(UPLOAD_DIR, filename, chunk_size, chunk_overlap)
        docs = preprocessor.preprocess()

        if docs is None:
            raise HTTPException(status_code=400, detail="Invalid file format")

        # Upload the processed data to Qdrant
        vector_store = VectorStore(collection_name)
        doc_ids = vector_store.add_documents(docs)

        # Save metadata in MongoDB
        db = await get_mongodb()
        await add_uploaded_docs_to_db(db, collection_name, filename, doc_ids)  # type: ignore

        # Remove the temporary file after successful processing
        os.remove(file_path)
        return {"message": "Embeddings uploaded successfully!"}

    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Document upload failed: {str(e)}")


@router.delete("/delete_docs")
async def delete_docs(collection_name: str, ids: DocIds) -> Dict:
    """
    Deletes documents from a Qdrant collection.

    Args:
        collection_name (str): The name of the collection to delete documents from.
        ids (DocIds) : A list of document IDs to delete.

    Returns:
        dict: A dictionary containing a success message.
    """

    try:
        # Delete documents from Qdrant
        vector_store = VectorStore(collection_name)
        vector_store.delete_documents(ids)

        # Remove metadata from MongoDB
        db = await get_mongodb()
        result = await delete_docs_from_db(db, collection_name, ids)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document deletion failed: {str(e)}")
