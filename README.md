# RAG Knowledge Assistant

A full-stack RAG (Retrieval-Augmented Generation) application that answers questions based on company documents with source citations.

## Architecture

- **Backend**: LangChain + FastAPI + PostgreSQL/PGVector + Redis cache
- **Frontend**: Next.js + TypeScript + Shadcn UI
- **Observability**: LangSmith tracing + structured logging
- **Evaluation**: Ragas metrics (faithfulness, relevancy, precision, recall)

## Quick Start

1. **Copy environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your OPENAI_API_KEY and optionally LANGSMITH_API_KEY
   ```

2. **Start all services**:
   ```bash
   docker compose up --build
   ```

3. **Ingest documents**:
   ```bash
   curl -X POST http://localhost:8000/api/documents/ingest
   ```

4. **Open the app**: http://localhost:3000

## Services

| Service  | URL                   | Description            |
|----------|-----------------------|------------------------|
| Frontend | http://localhost:3000  | Chat & Docs UI         |
| Backend  | http://localhost:8000  | FastAPI REST + SSE     |
| Postgres | localhost:5432        | PGVector storage       |
| Redis    | localhost:6379        | Semantic cache         |

## API Endpoints

- `GET /health` - Health check (DB + Redis)
- `POST /api/chat` - Chat with SSE streaming
- `GET /api/conversations` - List conversations
- `GET /api/conversations/{id}` - Get conversation with messages
- `DELETE /api/conversations/{id}` - Delete conversation
- `POST /api/documents/ingest` - Ingest documents from /data
- `GET /api/documents` - List all documents
- `GET /api/documents/{id}/preview` - Preview/download document
- `POST /api/evaluate` - Run Ragas evaluation

## Evaluation

```bash
# Via API
curl -X POST http://localhost:8000/api/evaluate

# Via CLI (from project root)
python eval/run_eval.py --dataset eval/test_dataset.json --output eval/results.json
```

## Documents

Place documents in `/data` organized by category:
- `handbooks/` - Employee handbooks
- `policies/` - Company policies
- `faqs/` - FAQs
- `guides/` - Setup guides
- `announcements/` - Company announcements

Supported formats: PDF, DOCX, MD, TXT
