from fastapi import FastAPI
# from contextlib import asynccontextmanager
from app.db.mongodb import mongodb
from app.db.redis import redis
from app.routes import queries

app = FastAPI()

app.include_router(queries.router, prefix="/queries")


@app.on_event("startup")
async def startup_db():
    await mongodb.connect()
    await redis.connect()


@app.on_event("shutdown")
async def shutdown_db():
    await mongodb.close()
    await redis.close()

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     await startup_db()
#     yield
#     await shutdown_db()

# app = FastAPI(lifespan=lifespan)

@app.get("/")
def root():
    return {"message": "Welcome to Agentic RAG"}