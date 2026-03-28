from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.database import Conversation, Message


async def create_conversation(db: AsyncSession, title: str = "New Chat") -> Conversation:
    conversation = Conversation(title=title)
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return conversation


async def get_conversations(db: AsyncSession) -> list[Conversation]:
    result = await db.execute(
        select(Conversation).order_by(Conversation.updated_at.desc())
    )
    return list(result.scalars().all())


async def get_conversation_with_messages(db: AsyncSession, conversation_id: UUID) -> Conversation | None:
    result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .options(selectinload(Conversation.messages))
    )
    return result.scalar_one_or_none()


async def delete_conversation(db: AsyncSession, conversation_id: UUID) -> bool:
    conversation = await db.get(Conversation, conversation_id)
    if not conversation:
        return False
    await db.delete(conversation)
    await db.commit()
    return True


async def add_message(
    db: AsyncSession,
    conversation_id: UUID,
    role: str,
    content: str,
    sources: list[dict] | None = None,
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        sources=sources,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def get_recent_messages(db: AsyncSession, conversation_id: UUID, limit: int = 10) -> list[Message]:
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = list(result.scalars().all())
    messages.reverse()
    return messages
