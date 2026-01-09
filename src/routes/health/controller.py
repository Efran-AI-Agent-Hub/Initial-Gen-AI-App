import logging
from fastapi import APIRouter

logger = logging.getLogger(__name__)
health_router = APIRouter()


@health_router.get("/health")
async def health_check():
    """
    Simple return to verify API is working
    """
    return {"status": "ok"}
