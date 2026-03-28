import json
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_redis
from app.db.session import get_db
from app.models.schemas import (
    ChatRequest,
    ConversationDetailResponse,
    ConversationResponse,
)
from app.services.cache import get_cached_response, set_cached_response
from app.services.history import (
    add_message,
    create_conversation,
    delete_conversation,
    get_conversation_with_messages,
    get_conversations,
    get_recent_messages,
)
from app.services.rag_chain import (
    condense_question,
    extract_sources,
    format_context,
    generate_response,
    retrieve_documents,
)

logger = structlog.get_logger()
router = APIRouter(tags=["chat"])


@router.post("/chat")
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    redis = await get_redis()

    # Get or create conversation
    if request.conversation_id:
        conversation = await get_conversation_with_messages(db, request.conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        title = request.message[:60].strip()
        conversation = await create_conversation(db, title=title)

    conversation_id = conversation.id

    # Save user message
    await add_message(db, conversation_id, "user", request.message)

    # Get chat history for condensing
    history = await get_recent_messages(db, conversation_id, limit=10)

    async def event_generator():
        # Condense question with history
        standalone_question = await condense_question(request.message, history[:-1])

        # Check cache
        cached = await get_cached_response(redis, standalone_question) if settings.cache_enabled else None
        if cached:
            # Stream cached response token by token (simulate streaming)
            for word in cached["response"].split(" "):
                yield {"event": "token", "data": json.dumps({"token": word + " "})}
            yield {"event": "sources", "data": json.dumps(cached["sources"])}
            # Save assistant message
            msg = await add_message(
                db, conversation_id, "assistant", cached["response"], cached["sources"]
            )
            yield {
                "event": "done",
                "data": json.dumps({
                    "message_id": str(msg.id),
                    "conversation_id": str(conversation_id),
                }),
            }
            return

        # Retrieve relevant documents
        docs_with_scores = retrieve_documents(standalone_question)
        sources = extract_sources(docs_with_scores)
        context = format_context(docs_with_scores)

        # Stream LLM response
        full_response = ""
        async for token in generate_response(standalone_question, context):
            full_response += token
            yield {"event": "token", "data": json.dumps({"token": token})}

        # Send sources
        yield {"event": "sources", "data": json.dumps(sources)}

        # Cache the response
        if settings.cache_enabled:
            await set_cached_response(redis, standalone_question, full_response, sources)

        # Save assistant message
        msg = await add_message(db, conversation_id, "assistant", full_response, sources)

        yield {
            "event": "done",
            "data": json.dumps({
                "message_id": str(msg.id),
                "conversation_id": str(conversation_id),
            }),
        }

    return EventSourceResponse(event_generator())


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(db: AsyncSession = Depends(get_db)):
    return await get_conversations(db)


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(conversation_id: UUID, db: AsyncSession = Depends(get_db)):
    conversation = await get_conversation_with_messages(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.delete("/conversations/{conversation_id}")
async def remove_conversation(conversation_id: UUID, db: AsyncSession = Depends(get_db)):
    deleted = await delete_conversation(db, conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "deleted"}
