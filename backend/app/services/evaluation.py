import asyncio
import json
from functools import partial
from pathlib import Path

import structlog
from ragas import evaluate
from ragas.dataset_schema import EvaluationDataset, SingleTurnSample
from ragas.metrics import (
    ContextPrecision,
    ContextRecall,
    AnswerRelevancy,
    Faithfulness,
)
from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.services.rag_chain import (
    retrieve_documents,
    format_context,
    extract_sources,
)

logger = structlog.get_logger()


def _get_eval_llm():
    return ChatOpenAI(
        model=settings.llm_model,
        temperature=0,
        api_key=settings.openai_api_key,
    )


async def run_evaluation(dataset_path: str | None = None) -> dict:
    dataset_path = dataset_path or "/app/eval/test_dataset.json"
    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    with open(path) as f:
        test_data = json.load(f)

    llm = _get_eval_llm()
    samples = []
    per_question_results = []

    for item in test_data:
        question = item["question"]
        ground_truth = item["ground_truth"]

        # Run RAG pipeline (non-streaming)
        docs_with_scores = retrieve_documents(question)
        context = format_context(docs_with_scores)
        sources = extract_sources(docs_with_scores)

        # Get answer from LLM
        from langchain_core.prompts import ChatPromptTemplate

        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are a grounded company knowledge assistant."
                "Always base answers strictly on the provided context."
                "If the context does not contain enough information to answer, "
                "say so clearly — never make up information."
                "Respond concisely and clearly\n\n"
                "Context:\n{context}"
            )),
            ("human", "{question}"),
        ])
        chain = prompt | llm
        response = await chain.ainvoke({"question": question, "context": context})
        answer = response.content

        retrieved_contexts = [doc.page_content for doc, _ in docs_with_scores]

        sample = SingleTurnSample(
            user_input=question,
            response=answer,
            retrieved_contexts=retrieved_contexts,
            reference=ground_truth,
        )
        samples.append(sample)

        per_question_results.append({
            "question": question,
            "answer": answer,
            "sources": [s["filename"] for s in sources],
        })

    eval_dataset = EvaluationDataset(samples=samples)

    metrics = [
        ContextPrecision(llm=llm),
        ContextRecall(llm=llm),
        AnswerRelevancy(llm=llm),
        Faithfulness(llm=llm),
    ]

    logger.info("Running Ragas evaluation", num_questions=len(samples))
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None, partial(evaluate, dataset=eval_dataset, metrics=metrics)
    )

    # Extract scores
    df = result.to_pandas()
    aggregate = {}
    for metric in ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]:
        if metric in df.columns:
            aggregate[metric] = round(float(df[metric].mean()), 4)

    # Merge per-question scores
    for i, row in df.iterrows():
        scores = {}
        for metric in ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]:
            if metric in df.columns:
                scores[metric] = round(float(row[metric]), 4)
        per_question_results[i]["scores"] = scores

    logger.info("Evaluation complete", aggregate=aggregate)
    return {"results": per_question_results, "aggregate": aggregate}
