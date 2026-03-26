"""
Embedding service supporting HuggingFace (free) and OpenAI (optional).
Hugging Face sentence-transformers used as default for cost optimization.
"""

import numpy as np
from typing import List
from app.config import get_settings

# Lazy-loaded model instance
_hf_model = None


def _get_hf_model():
    """Lazy-load HuggingFace sentence-transformer model to avoid memory overhead."""
    global _hf_model
    if _hf_model is None:
        from sentence_transformers import SentenceTransformer
        _hf_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _hf_model


async def get_embeddings_huggingface(texts: List[str]) -> List[List[float]]:
    """Generate embeddings using HuggingFace sentence-transformers (FREE).

    Model: all-MiniLM-L6-v2
    Dimension: 384
    """
    model = _get_hf_model()
    embeddings = model.encode(texts, show_progress_bar=False)
    return embeddings.tolist()


async def get_embeddings_openai(texts: List[str]) -> List[List[float]]:
    """Generate embeddings using OpenAI text-embedding-ada-002 (paid).

    Model: text-embedding-ada-002
    Dimension: 1536
    Cost: $0.0001 per 1K tokens
    """
    from openai import OpenAI
    settings = get_settings()
    client = OpenAI(api_key=settings.openai_api_key)

    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=texts,
    )
    return [item.embedding for item in response.data]


async def get_embeddings(texts: List[str], provider: str = None) -> List[List[float]]:
    """Generate embeddings using the configured provider.

    Args:
        texts: List of text strings to embed
        provider: Override provider ("huggingface" or "openai"). If None, uses config.

    Returns:
        List of embedding vectors
    """
    settings = get_settings()
    provider = provider or settings.embedding_provider

    if provider == "openai":
        return await get_embeddings_openai(texts)
    else:
        return await get_embeddings_huggingface(texts)


def get_embedding_dimension(provider: str = None) -> int:
    """Return the embedding dimension for the given provider."""
    settings = get_settings()
    provider = provider or settings.embedding_provider
    return 1536 if provider == "openai" else 384
