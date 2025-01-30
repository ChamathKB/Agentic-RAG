from pydantic import BaseModel, Field
from langchain_core.documents import Document

class Query(BaseModel):
    query: str

class Response(BaseModel):
    response: str

class DocIds(BaseModel):
    ids: list[str]

class Docs(BaseModel):
    docs: list[Document]

class GetCurrentWeatherCheckInput(BaseModel):
    # Check the input for Weather
    location: str = Field(..., description = "The name of the location name for which we need to find the weather")
