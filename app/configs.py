import os

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "agentic_rag_db")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")

UPLOAD_DIR = "uploads"

SERPER_API_KEY = os.getenv("SERPER_API_KEY")