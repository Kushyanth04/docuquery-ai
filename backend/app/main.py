"""
DocuQuery AI - FastAPI Application
RAG-powered document Q&A with LangChain, Pinecone, and intelligent caching.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import auth, documents, query, classify
from app.services.pinecone_service import init_pinecone
from app.services.redis_cache import init_redis, close_redis
from app.services.classifier import load_classifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize and cleanup resources."""
    logger.info("🚀 Starting DocuQuery AI...")
    settings = get_settings()

    # Initialize Pinecone
    try:
        init_pinecone()
        logger.info("✅ Pinecone initialized")
    except Exception as e:
        logger.warning(f"⚠️ Pinecone init failed: {e}")

    # Initialize Redis
    try:
        await init_redis()
        logger.info("✅ Redis initialized")
    except Exception as e:
        logger.warning(f"⚠️ Redis init failed (caching disabled): {e}")

    # Pre-load classifier
    try:
        load_classifier()
        logger.info("✅ Document classifier loaded")
    except Exception as e:
        logger.warning(f"⚠️ Classifier load failed: {e}")

    logger.info(f"📋 LLM Provider: {settings.llm_provider}")
    logger.info(f"📋 Embedding Provider: {settings.embedding_provider}")
    logger.info("🟢 DocuQuery AI is ready!")

    yield

    # Cleanup
    logger.info("Shutting down DocuQuery AI...")
    await close_redis()
    logger.info("🔴 DocuQuery AI stopped")


# Create FastAPI app
app = FastAPI(
    title="DocuQuery AI",
    description=(
        "RAG-powered document Q&A application using LangChain for PDF chunking, "
        "Pinecone for vector storage, and AI-powered semantic search with "
        "Hugging Face and OpenAI embeddings. Features intelligent Redis caching "
        "and scikit-learn document classification."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(query.router)
app.include_router(classify.router)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "service": "DocuQuery AI",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    settings = get_settings()
    return {
        "status": "healthy",
        "llm_provider": settings.llm_provider,
        "embedding_provider": settings.embedding_provider,
        "services": {
            "pinecone": "configured",
            "redis": "configured",
            "supabase": "configured",
        },
    }
