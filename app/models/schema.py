from pydantic import BaseModel
from langchain_core.documents import Document

class Query(BaseModel):
    query: str

class Response(BaseModel):
    response: str

class DocIds(BaseModel):
    ids: list[str]

class Docs(BaseModel):
    docs: list[Document]