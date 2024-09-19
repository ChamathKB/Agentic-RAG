from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from engine import ask_agent

app = FastAPI()

class Query(BaseModel):
    query: str

@app.get("/")
def root():
    return {"message": "Welcome to Agentic RAG"}


@app.post("/query")
def ask(query: Query):
    response = ask_agent(query)
    return {"response": response}