from typing import Any
from uuid import uuid4

from langchain.tools.retriever import create_retriever_tool
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from app.configs import EMBEDDING_MODEL, QDRANT_URL

client = QdrantClient(location=QDRANT_URL)

embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)


class VectorStore:
    """
    Class for managing vector store operations.
    """

    def __init__(self, collection_name: str):
        """
        Initialize the VectorStore with a collection name.
        Args:
            collection_name (str) : vector database collection
        """
        if not isinstance(collection_name, str):
            raise ValueError("collection_name must be a string.")

        self.collection_name = collection_name
        self.client = client
        self.embeddings = embeddings

    def create_collection(self) -> None:
        """
        Create a new collection in the vector store.
        """
        if not isinstance(self.collection_name, str):
            raise ValueError("collection_name must be a string.")

        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
            )

    def get_vector_store(self) -> QdrantVectorStore:
        """
        Get the vector store for the specified collection.
        Returns:
            QdrantVectorStore: The vector store for the specified collection.
        """
        vector_store = QdrantVectorStore(
            collection_name=self.collection_name,
            client=self.client,
            embedding=self.embeddings,
        )
        return vector_store

    def add_documents(self, docs: list[dict]) -> list[str]:
        """
        Add documents to the vector store.
        Args:
            docs (list[dict]): List of documents to be added.
        Returns:
            list[str]: List of document IDs.
        """
        # if not isinstance(docs, list) or not all(isinstance(doc, dict) for doc in docs):
        #     raise ValueError("docs must be a list of dictionaries.")

        vector_store = self.get_vector_store()
        ids = [str(uuid4()) for _ in range(len(docs))]
        vector_store.add_documents(documents=docs, ids=ids)
        return ids

    def delete_documents(self, ids: list[str]) -> None:
        """
        Delete documents from the vector store.
        Args:
            ids (list[str]): List of document IDs to be deleted.
        """
        if not isinstance(ids, list) or not all(isinstance(doc_id, str) for doc_id in ids):
            raise ValueError("ids must be a list of strings.")

        vector_store = self.get_vector_store()
        vector_store.delete(ids)

    def retrieve(self, query: str, k: int = 2) -> Any:
        """
        Retrieve documents from the vector store based on a query.
        Args:
            query (str): The query string.
            k (int, optional): The number of documents to retrieve. Defaults to 2.
        Returns:
            Any: The retrieved documents.
        Raises:
            ValueError: If the query is not a string or k is not a positive integer.
        """
        if not isinstance(query, str):
            raise ValueError("query must be a string.")
        if not isinstance(k, int) or k <= 0:
            raise ValueError("k must be a positive integer.")

        vector_store = self.get_vector_store()
        return vector_store.similarity_search(query, k=k)

    def content_retriever_tool(self):
        """
        Create a retriever tool for the vector store.
        Returns:
            Any: The retriever tool.
        """
        vector_store = self.get_vector_store()
        retriever = vector_store.as_retriever()
        retriever_tool = create_retriever_tool(
            retriever,
            name="query_tool",
            description="Use this tool when you need to answer questions about the context provided.",
        )

        return retriever_tool
