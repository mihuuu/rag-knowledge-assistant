import structlog
from fastapi import APIRouter

from app.services.evaluation import run_evaluation

logger = structlog.get_logger()
router = APIRouter(tags=["evaluate"])


@router.post("/evaluate")
async def evaluate_rag(dataset_path: str | None = None):
    logger.info("Starting evaluation", dataset_path=dataset_path)
    result = await run_evaluation(dataset_path)
    return result
