from langchain_core.documents import Document
from pydantic import BaseModel, Field


class Query(BaseModel):
    query: str = Field(
        ...,
        description="The query to be answered by the agent",
    )


class Response(BaseModel):
    response: str = Field(
        ...,
        description="The response from the agent",
    )


class DocIds(BaseModel):
    ids: list[str] = Field(
        ...,
        description="The ids of the documents to be retrieved",
    )


class Docs(BaseModel):
    docs: list[Document] = Field(
        ...,
        description="List of documents to be retrieved",
    )


class GetCurrentWeatherCheckInput(BaseModel):
    # Check the input for Weather
    location: str = Field(
        ...,
        description="The name of the location name for which we need to find the weather",
    )
