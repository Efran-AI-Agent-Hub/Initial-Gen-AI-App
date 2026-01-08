from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
import logging

from src.routes import health

from starlette.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    logger.info("Starting up FastAPI application...")
    yield
    logger.info("Shutting down FastAPI application...")

    # TODO: Perform cleanup tasks like closing connections when we get to that point

app = FastAPI(
    title="Efran's LLM Service API",
    description="Efran's scalable LLM application with RAG and agentic capabilities",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # TODO: Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(health.router, tags=["health"])


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",)

    print("hello world")