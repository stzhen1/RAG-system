# Enterprise RAG

Enterprise document Q&A platform — upload documents, ingest them through a Celery pipeline, and ask natural-language questions with hybrid retrieval + LLM streaming.

## Architecture

```
Upload → Parse → Chunk → Embed → Index   (Celery pipeline)
                         ↓
Query → Hybrid Search (Vector + BM25) → Rerank → Context → LLM → SSE Stream
```

| Layer | Technology |
|---|---|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS |
| API | FastAPI (Python 3.12), SSE streaming |
| Queue | Celery + Redis |
| Vector DB | Qdrant |
| Metadata / BM25 | PostgreSQL 16 (pgvector, tsvector + GIN) |
| File Store | MinIO |
| AI Providers | OpenAI, Anthropic, Ollama (adapter pattern) |
| Embedding | BGE-M3, OpenAI, Ollama |
| Reranker | BGE Reranker, Jina Reranker |

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker & Docker Compose

### 1. Start Infrastructure

```bash
cd backend
docker compose up -d postgres qdrant redis minio
```

### 2. Configure Backend

```bash
cd backend
cp .env.example .env   # edit .env with your LLM/embedding API keys
pip install -r requirements.txt
alembic upgrade head
```

### 3. Start Services

```bash
# API server (terminal 1)
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Celery worker (terminal 2)
cd backend
celery -A app.celery_app.worker worker -Q queue_parse,queue_chunk,queue_embedding,queue_index --concurrency=2
```

### 4. Start Frontend

```bash
cd frontend
npm install
npm run dev        # → http://localhost:5173
```

## Configuration

Key environment variables (in `backend/.env`):

| Variable | Description | Options |
|---|---|---|
| `LLM_PROVIDER` | Chat model provider | `openai`, `anthropic`, `ollama` |
| `EMBEDDING_PROVIDER` | Embedding model provider | `bge-m3`, `openai`, `ollama` |
| `RETRIEVAL_TOP_K` | Candidates per search path | default `30` |
| `RERANK_TOP_N` | Results after reranking | default `5` |
| `CHILD_CHUNK_SIZE` | Embedding chunk size (chars) | default `400` |
| `PARENT_CHUNK_SIZE` | Context chunk size (chars) | default `2500` |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/chat` | Chat (SSE streaming) |
| `POST` | `/api/documents/upload` | Upload document |
| `GET` | `/api/documents` | List documents |
| `GET` | `/api/documents/{id}` | Document status |
| `DELETE` | `/api/documents/{id}` | Soft-delete document |

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── adapters/      # LLM, embedding, reranker provider adapters
│   │   ├── api/           # REST endpoints
│   │   ├── celery_app/    # Celery worker + ingestion tasks
│   │   ├── core/          # Chunking, context builder
│   │   ├── db/            # SQLAlchemy models, session
│   │   ├── schemas/       # Pydantic request/response models
│   │   └── services/      # Chat, retrieval, document, parsing services
│   ├── alembic/           # Database migrations
│   ├── tests/
│   └── docker-compose.yml
└── frontend/
    └── src/
        ├── api/           # HTTP + SSE client
        ├── components/    # Chat, DocumentUpload, Layout
        ├── hooks/         # useChat state machine
        ├── types/         # TypeScript interfaces
        └── lib/           # Utilities (SSE parser, cn helper)
```

## Testing

```bash
cd backend
pytest                        # all tests
pytest tests/test_chunking.py  # single file
```

Tests use `pytest` + `pytest-asyncio`. Integration tests use `httpx.AsyncClient` with mock services — no server startup required.

## License

MIT
