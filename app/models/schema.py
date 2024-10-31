from pydantic import BaseModel

class Query(BaseModel):
    query: str

class DocIds(BaseModel):
    ids: list[str]