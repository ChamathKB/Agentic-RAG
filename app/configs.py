import os

OPENAI_MODEL=os.getenv("OPENAI_MODEL", "gpt-4o-mini")
EMBEDDING_MODEL=os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")

QDRANT_URL=os.getenv("QDRANT_URL", "http://localhost:6333")

MONGO_URL= os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB_NAME= os.getenv("MONGO_DB_NAME", "agentic_rag_db")

REDIS_URL= os.getenv("REDIS_URL", "redis://localhost:6379")

UPLOAD_DIR="uploads"