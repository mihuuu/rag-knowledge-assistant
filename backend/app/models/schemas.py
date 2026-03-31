from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


# Chat
class ChatRequest(BaseModel):
    message: str
    conversation_id: UUID | None = None


# Sources
class SourceInfo(BaseModel):
    document_id: str
    filename: str
    category: str
    chunk_text: str
    score: float


# Messages
class MessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    sources: list[SourceInfo] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# Conversations
class ConversationResponse(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConversationDetailResponse(ConversationResponse):
    messages: list[MessageResponse] = []


# Documents
class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    category: str
    file_type: str
    file_size: int
    chunk_count: int
    ingested_at: datetime

    model_config = {"from_attributes": True}


class IngestResponse(BaseModel):
    ingested: int
    skipped: int = 0
    total_chunks: int


class DocumentDeleteResponse(BaseModel):
    id: UUID
    filename: str
    chunks_deleted: int


# Evaluation
class EvalResult(BaseModel):
    question: str
    answer: str
    scores: dict[str, float]


class EvalResponse(BaseModel):
    results: list[EvalResult]
    aggregate: dict[str, float]
