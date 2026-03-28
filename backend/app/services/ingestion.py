import os
import uuid
from pathlib import Path

import structlog
from langchain_community.document_loaders import (
    Docx2txtLoader,
    PyMuPDFLoader,
    TextLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_embeddings, get_vector_store
from app.models.database import Document

logger = structlog.get_logger()

LOADER_MAP = {
    ".pdf": PyMuPDFLoader,
    ".docx": Docx2txtLoader,
    ".md": TextLoader,
    ".txt": TextLoader,
}


def _load_file(file_path: str):
    ext = Path(file_path).suffix.lower()
    loader_cls = LOADER_MAP.get(ext)
    if loader_cls is None:
        logger.warning("Unsupported file type", file_path=file_path, ext=ext)
        return []
    loader = loader_cls(file_path)
    return loader.load()


def _get_text_splitter(category: str) -> RecursiveCharacterTextSplitter:
    if category == "faqs":
        return RecursiveCharacterTextSplitter(
            separators=["Q:", "\n\n", "\n", ". ", " ", ""],
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            keep_separator=True,
        )
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )


async def ingest_documents(db: AsyncSession, data_dir: str | None = None) -> dict:
    data_dir = data_dir or settings.data_dir
    vector_store = get_vector_store()

    ingested = 0
    total_chunks = 0

    for root, _, files in os.walk(data_dir):
        for filename in files:
            if filename.startswith("."):
                continue

            file_path = os.path.join(root, filename)
            category = Path(root).name
            if category == Path(data_dir).name:
                category = "uncategorized"

            ext = Path(filename).suffix.lower()
            if ext not in LOADER_MAP:
                continue

            file_size = os.path.getsize(file_path)
            doc_id = uuid.uuid4()

            logger.info("Loading document", filename=filename, category=category)

            # Load document
            raw_docs = _load_file(file_path)
            if not raw_docs:
                continue

            # Enrich metadata
            for doc in raw_docs:
                doc.metadata.update({
                    "document_id": str(doc_id),
                    "source_filename": filename,
                    "category": category,
                    "file_type": ext.lstrip("."),
                })

            # Chunk
            splitter = _get_text_splitter(category)
            chunks = splitter.split_documents(raw_docs)
            chunk_count = len(chunks)

            logger.info("Chunked document", filename=filename, chunks=chunk_count)

            # Embed and store in PGVector
            if chunks:
                vector_store.add_documents(chunks)

            # Record in documents table
            existing = await db.execute(
                select(Document).where(Document.filename == filename)
            )
            doc_record = existing.scalar_one_or_none()

            if doc_record:
                doc_record.chunk_count = chunk_count
                doc_record.file_size = file_size
                doc_record.file_path = file_path
            else:
                doc_record = Document(
                    id=doc_id,
                    filename=filename,
                    category=category,
                    file_type=ext.lstrip("."),
                    file_path=file_path,
                    file_size=file_size,
                    chunk_count=chunk_count,
                )
                db.add(doc_record)

            ingested += 1
            total_chunks += chunk_count

    await db.commit()
    logger.info("Ingestion complete", ingested=ingested, total_chunks=total_chunks)
    return {"ingested": ingested, "total_chunks": total_chunks}
