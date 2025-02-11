from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.mongodb import mongodb
from app.db.redis import redis
from app.routes import knowledgebases, queries


@asynccontextmanager
async def lifespan(app: FastAPI):
    await mongodb.connect()
    await redis.connect()
    yield
    await mongodb.close()
    await redis.close()


app = FastAPI(lifespan=lifespan)

app.include_router(queries.router, prefix="/queries")
app.include_router(knowledgebases.router, prefix="/knowledgebases")


@app.get("/")
def root():
    return {"message": "Welcome to Agentic RAG"}


@app.get("/health")
def health():
    return {"status": "ok"}
