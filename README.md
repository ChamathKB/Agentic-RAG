# Agentic-RAG

## Overview

The Agentic Retrieval-Augmented Generation (RAG) service is a robust and efficient solution designed to enhance the capabilities of language models through advanced orchestration, retrieval mechanisms, and observability. This system leverages cutting-edge technologies to deliver scalable, fast, and reliable services for modern AI applications.

## Key Components

1. LangChain : Acts as the orchestration layer for managing and chaining large language model (LLM) operations.

2. FastAPI : Provides a lightweight and high-performance API layer.

3. Qdrant : Serves as the vector database for efficient storage and retrieval of high-dimensional embeddings.


4. MongoDB : Acts as the primary database for storing knowledgebase source data, conversation data, and metadata.

5. Redis : Functions as a caching mechanism to improve response times and reduce database load.

6. MLflow : Provides observability for LLM operations (LLMOps).

## Core Features

Retrieval-Augmented Generation: Enhances the quality of generated content by integrating relevant external knowledge during the generation process.

Scalability: Supports horizontal scaling to handle high throughput.

Observability: MLflow integration ensures real-time monitoring and debugging of LLM operations.

Performance: Combines FastAPI, Redis, and Qdrant to deliver low-latency responses and efficient data handling.

## Deployment
### Local

Run server :

```
uvicorn app.main:app
```

Run mlflow :
```
mlflow server
```
Additionally run Qdrant, Mongodb, and Redis services.

### Docker (recommended)
Use docker compose to deploy using docker.

```
docker compose up -d
```
