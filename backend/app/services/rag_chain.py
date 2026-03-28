import structlog
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.core.dependencies import get_vector_store
from app.models.database import Message

logger = structlog.get_logger()

CONDENSE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", (
        "Given the following conversation history and a follow-up question, "
        "rephrase the follow-up question to be a standalone question that "
        "captures all necessary context."
    )),
    MessagesPlaceholder("chat_history"),
    ("human", "{question}"),
])

RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", (
        "You are a helpful company knowledge assistant. Answer the question "
        "using ONLY the provided context from company documents. "
        "If the context does not contain enough information to answer, "
        "say so clearly — never make up information.\n\n"
        "Always cite which document(s) you used in your answer.\n\n"
        "Context:\n{context}"
    )),
    ("human", "{question}"),
])


def _get_llm(streaming: bool = False) -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.llm_model,
        temperature=0,
        streaming=streaming,
        api_key=settings.openai_api_key,
    )


def _format_chat_history(messages: list[Message]) -> list:
    history = []
    for msg in messages:
        if msg.role == "user":
            history.append(HumanMessage(content=msg.content))
        else:
            history.append(AIMessage(content=msg.content))
    return history


async def condense_question(question: str, chat_history: list[Message]) -> str:
    if not chat_history:
        return question

    llm = _get_llm(streaming=False)
    chain = CONDENSE_PROMPT | llm | StrOutputParser()

    condensed = await chain.ainvoke({
        "chat_history": _format_chat_history(chat_history),
        "question": question,
    })
    logger.info("Condensed question", original=question[:50], condensed=condensed[:50])
    return condensed


def retrieve_documents(question: str, k: int | None = None) -> list:
    vector_store = get_vector_store()
    k = k or settings.retrieval_k
    docs = vector_store.similarity_search_with_score(question, k=k)
    logger.info("Retrieved documents", question=question[:50], count=len(docs))
    return docs


def extract_sources(docs_with_scores: list) -> list[dict]:
    sources = []
    for doc, score in docs_with_scores:
        sources.append({
            "document_id": doc.metadata.get("document_id", ""),
            "filename": doc.metadata.get("source_filename", "unknown"),
            "category": doc.metadata.get("category", ""),
            "chunk_text": doc.page_content[:200],
            "score": round(float(score), 4),
        })
    return sources


def format_context(docs_with_scores: list) -> str:
    parts = []
    for doc, _score in docs_with_scores:
        source = doc.metadata.get("source_filename", "unknown")
        parts.append(f"[Source: {source}]\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


async def generate_response(question: str, context: str):
    llm = _get_llm(streaming=True)
    chain = RAG_PROMPT | llm

    async for chunk in chain.astream({"question": question, "context": context}):
        if chunk.content:
            yield chunk.content
