import os
from pathlib import Path
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.models.database import Document
from app.models.schemas import DocumentDeleteResponse, DocumentResponse, IngestResponse
from app.services.ingestion import (
    LOADER_MAP,
    delete_chunks_for_document,
    ingest_documents,
    ingest_single_document,
)

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


@router.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile,
    category: str = Form("uncategorized"),
    db: AsyncSession = Depends(get_db),
):
    ext = Path(file.filename).suffix.lower()
    if ext not in LOADER_MAP:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    # Check for duplicate filename
    existing = await db.execute(
        select(Document).where(Document.filename == file.filename)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Document with this filename already exists. Use PUT to update.")

    # Save file to data directory
    target_dir = os.path.join(settings.data_dir, category)
    os.makedirs(target_dir, exist_ok=True)
    file_path = os.path.join(target_dir, file.filename)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    logger.info("Uploading document", filename=file.filename, category=category)
    doc_record = await ingest_single_document(db, file_path, file.filename, category)
    db.add(doc_record)
    await db.commit()
    await db.refresh(doc_record)
    return doc_record


@router.put("/documents/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: UUID,
    file: UploadFile,
    category: str = Form(None),
    db: AsyncSession = Depends(get_db),
):
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    ext = Path(file.filename).suffix.lower()
    if ext not in LOADER_MAP:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    # Delete old chunks
    await delete_chunks_for_document(db, str(document_id))

    # Use existing category if not provided
    category = category or doc.category

    # Remove old file if path will change
    new_dir = os.path.join(settings.data_dir, category)
    os.makedirs(new_dir, exist_ok=True)
    new_path = os.path.join(new_dir, file.filename)
    if doc.file_path != new_path:
        try:
            os.remove(doc.file_path)
        except OSError:
            pass

    # Save new file
    content = await file.read()
    with open(new_path, "wb") as f:
        f.write(content)

    logger.info("Updating document", document_id=str(document_id), filename=file.filename)
    new_record = await ingest_single_document(db, new_path, file.filename, category, doc_id=document_id)

    # Update existing record
    doc.filename = new_record.filename
    doc.category = new_record.category
    doc.file_type = new_record.file_type
    doc.file_path = new_record.file_path
    doc.file_size = new_record.file_size
    doc.chunk_count = new_record.chunk_count

    await db.commit()
    await db.refresh(doc)
    return doc


@router.delete("/documents/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete chunks from vector store
    chunks_deleted = await delete_chunks_for_document(db, str(document_id))

    # Remove file from disk
    try:
        os.remove(doc.file_path)
    except OSError:
        logger.warning("Could not remove file from disk", file_path=doc.file_path)

    filename = doc.filename
    await db.delete(doc)
    await db.commit()

    logger.info("Deleted document", document_id=str(document_id), chunks_deleted=chunks_deleted)
    return DocumentDeleteResponse(id=document_id, filename=filename, chunks_deleted=chunks_deleted)


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
    stat = os.stat(doc.file_path)
    etag = f"{stat.st_mtime_ns:x}-{stat.st_size:x}"
    headers = {"ETag": f'"{etag}"'}
    return FileResponse(doc.file_path, media_type=media_type, filename=doc.filename, headers=headers, stat_result=stat)
