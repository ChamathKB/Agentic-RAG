from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain.tools.retriever import create_retriever_tool

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from typing import List, Any
from configs import QDRANT_URL, EMBEDDING_MODEL


client = QdrantClient(url=QDRANT_URL, 
                      path="./qdrant_data")

embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)


class VectorStore:
    def __init__(self, collection_name: str):
        if not isinstance(collection_name, str):
            raise ValueError("collection_name must be a string.")
        
        self.collection_name = collection_name
        self.client = client
        self.embeddings = embeddings

    def create_collection(self) -> None:
        if not isinstance(self.collection_name, str):
            raise ValueError("collection_name must be a string.")

        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=3072, distance=Distance.COSINE)
            )

    def get_vector_store(self) -> QdrantVectorStore:
        vector_store = QdrantVectorStore(
            collection_name=self.collection_name,
            client=self.client,
            embedding=self.embeddings
        )
        return vector_store

    def add_documents(self, docs: List[dict]) -> None:
        if not isinstance(docs, list) or not all(isinstance(doc, dict) for doc in docs):
            raise ValueError("docs must be a list of dictionaries.")

        vector_store = self.get_vector_store()
        vector_store.add_documents(docs)

    def delete_documents(self, ids: List[str]) -> None:
        if not isinstance(ids, list) or not all(isinstance(doc_id, str) for doc_id in ids):
            raise ValueError("ids must be a list of strings.")

        vector_store = self.get_vector_store()
        vector_store.delete_documents(ids)

    def retrieve(self, query: str, k: int = 2) -> Any:
        if not isinstance(query, str):
            raise ValueError("query must be a string.")
        if not isinstance(k, int) or k <= 0:
            raise ValueError("k must be a positive integer.")

        vector_store = self.get_vector_store()
        return vector_store.similarity_search(query, k=k)
    
    def content_retriever_tool(self):
        vector_store = self.get_vector_store()
        retriever = vector_store.as_retriever()
        retriever_tool = create_retriever_tool(
            retriever,
            name="query_tool",
            description="Use this tool when you need to answer questions about the context provided."
            )
        
        return retriever_tool
