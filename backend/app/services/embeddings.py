"""
Embedding service supporting HuggingFace (free) and OpenAI (optional).
Hugging Face sentence-transformers used as default for cost optimization.
"""

import numpy as np
from typing import List
from app.config import get_settings

# Lazy-loaded model instance (legacy local method, removed to save RAM)
_hf_model = None


async def get_embeddings_huggingface(texts: List[str]) -> List[List[float]]:
    """Generate embeddings using HuggingFace Inference API (FREE).

    Model: all-MiniLM-L6-v2
    Dimension: 384
    """
    import httpx
    import asyncio
    import logging
    from app.config import get_settings
    
    settings = get_settings()
    logger = logging.getLogger(__name__)
    api_url = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2"
    headers = {"Authorization": f"Bearer {settings.huggingface_api_key}"}
    
    async with httpx.AsyncClient() as client:
        for attempt in range(3):
            try:
                response = await client.post(api_url, headers=headers, json={"inputs": texts}, timeout=30.0)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 503:
                    # Model is loading on huggingface servers
                    logger.warning("HuggingFace model loading, waiting 5s...")
                    await asyncio.sleep(5)
                    continue
                else:
                    raise Exception(f"HuggingFace API failed {response.status_code}: {response.text}")
            except httpx.ReadTimeout:
                logger.warning("HuggingFace API timeout, retrying...")
                await asyncio.sleep(2)
        raise Exception("Failed to get embeddings from HuggingFace API after retries.")


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
