import time

import structlog
from langchain_cohere import CohereRerank
from langsmith import traceable
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.core.config import settings
from app.core.dependencies import get_vector_store
from app.core.model_factory import get_chat_model
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
    ("system",
        "You are a grounded company knowledge assistant. "
        "Always base answers strictly on the provided context. "
        "If the context does not contain enough information to answer, "
        "say so clearly — never make up information. "
        "Be concise and direct. No titles, headings, or preamble."
    ),
    ("human", "Context:\n{context}\n\nQuestion: {question}"),
])


def _get_condense_llm():
    return get_chat_model(settings.get_condense_model(), streaming=False)


def _get_generation_llm():
    return get_chat_model(settings.get_generation_model(), streaming=True)


def _format_chat_history(messages: list[Message]) -> list:
    history = []
    for msg in messages:
        if msg.role == "user":
            history.append(HumanMessage(content=msg.content))
        else:
            history.append(AIMessage(content=msg.content))
    return history


@traceable(name="condense_question", run_type="chain")
async def condense_question(question: str, chat_history: list[Message]) -> str:
    if not chat_history:
        return question

    llm = _get_condense_llm()
    chain = CONDENSE_PROMPT | llm | StrOutputParser()

    condensed = await chain.ainvoke({
        "chat_history": _format_chat_history(chat_history),
        "question": question,
    })
    logger.info("Condensed question", original=question[:50], condensed=condensed[:50])
    return condensed


@traceable(name="retrieve_documents", run_type="retriever")
async def retrieve_documents(question: str, k: int | None = None) -> list:
    vector_store = await get_vector_store()
    k = k or settings.retrieval_k

    if not settings.cohere_api_key:
        logger.warning("No Cohere API key set, skipping rerank")
        docs = await vector_store.asimilarity_search_with_score(question, k=k)
        logger.info("Retrieved docs", question=question[:50], count=len(docs))
        return docs

    # Over-fetch candidates for reranking
    n = settings.rerank_candidates
    candidates = await vector_store.asimilarity_search_with_score(
        question, k=n
    )
    logger.info("Retrieved candidates", question=question[:50], count=len(candidates))

    # Rerank with Cohere
    reranker = CohereRerank(
        cohere_api_key=settings.cohere_api_key,
        model=settings.rerank_model,
        top_n=k,
    )
    docs_only = [doc for doc, _score in candidates]
    for attempt in range(5):
        try:
            reranked = reranker.compress_documents(docs_only, query=question)
            break
        except Exception as e:
            if "429" in str(e) and attempt < 4:
                wait = 10 * (attempt + 1)
                logger.warning("Cohere rate limited, retrying", wait=wait, attempt=attempt + 1)
                time.sleep(wait)
            else:
                logger.error("Rerank failed, falling back to similarity order", error=str(e))
                return candidates[:k]
    logger.info("Reranked documents", count=len(reranked))

    # Convert back to (Document, relevance_score) tuples
    results = []
    for rdoc in reranked:
        score = rdoc.metadata.get("relevance_score", 0.0)
        doc = Document(page_content=rdoc.page_content, metadata=rdoc.metadata)
        results.append((doc, score))
    return results


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


@traceable(name="generate_response", run_type="chain")
async def generate_response(question: str, context: str):
    llm = _get_generation_llm()
    chain = RAG_PROMPT | llm

    async for chunk in chain.astream({"question": question, "context": context}):
        if chunk.content:
            yield chunk.content
