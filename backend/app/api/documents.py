from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.database import Document
from app.models.schemas import DocumentResponse, IngestResponse
from app.services.ingestion import ingest_documents

logger = structlog.get_logger()
router = APIRouter(tags=["documents"])


@router.post("/documents/ingest", response_model=IngestResponse)
async def ingest(db: AsyncSession = Depends(get_db)):
    logger.info("Starting document ingestion")
    result = await ingest_documents(db)
    return IngestResponse(**result)


@router.get("/documents", response_model=list[DocumentResponse])
async def list_documents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).order_by(Document.category, Document.filename))
    return list(result.scalars().all())


@router.get("/documents/{document_id}/preview")
async def preview_document(document_id: UUID, db: AsyncSession = Depends(get_db)):
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    media_types = {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "md": "text/markdown",
        "txt": "text/plain",
    }
    media_type = media_types.get(doc.file_type, "application/octet-stream")
    return FileResponse(doc.file_path, media_type=media_type, filename=doc.filename)
