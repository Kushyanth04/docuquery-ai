"""
Pinecone vector storage service for document embeddings.
Uses namespaces to separate documents by category (legal, medical, technical, etc.).
"""

from typing import List, Dict, Optional
from pinecone import Pinecone, ServerlessSpec
from app.config import get_settings

_pinecone_index = None


def init_pinecone():
    """Initialize Pinecone client and ensure index exists."""
    global _pinecone_index
    settings = get_settings()

    pc = Pinecone(api_key=settings.pinecone_api_key)

    # Check if index exists, create if not
    existing_indexes = [idx.name for idx in pc.list_indexes()]
    if settings.pinecone_index not in existing_indexes:
        from app.services.embeddings import get_embedding_dimension
        dimension = get_embedding_dimension()
        pc.create_index(
            name=settings.pinecone_index,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )

    _pinecone_index = pc.Index(settings.pinecone_index)
    return _pinecone_index


def get_index():
    """Get the Pinecone index instance."""
    global _pinecone_index
    if _pinecone_index is None:
        return init_pinecone()
    return _pinecone_index


async def upsert_vectors(
    vectors: List[List[float]],
    metadata_list: List[Dict],
    ids: List[str],
    namespace: str = "general",
) -> Dict:
    """Upsert embedding vectors into Pinecone.

    Args:
        vectors: List of embedding vectors
        metadata_list: List of metadata dicts (text, source, page, user_id, etc.)
        ids: List of unique vector IDs
        namespace: Pinecone namespace (document category)

    Returns:
        Upsert response from Pinecone
    """
    index = get_index()

    # Batch upsert (Pinecone recommends batches of 100)
    batch_size = 100
    results = []
    for i in range(0, len(vectors), batch_size):
        batch = list(zip(
            ids[i:i + batch_size],
            vectors[i:i + batch_size],
            metadata_list[i:i + batch_size],
        ))
        result = index.upsert(vectors=batch, namespace=namespace)
        results.append(result)

    return {"upserted_count": sum(r.get("upserted_count", 0) for r in results)}


async def query_vectors(
    query_embedding: List[float],
    namespace: str = "general",
    top_k: int = 5,
    filter_dict: Optional[Dict] = None,
) -> List[Dict]:
    """Query Pinecone for similar vectors.

    Args:
        query_embedding: Query embedding vector
        namespace: Pinecone namespace to search
        top_k: Number of results to return
        filter_dict: Optional metadata filter

    Returns:
        List of matches with score, metadata, and id
    """
    index = get_index()

    results = index.query(
        vector=query_embedding,
        namespace=namespace,
        top_k=top_k,
        include_metadata=True,
        filter=filter_dict,
    )

    matches = []
    for match in results.get("matches", []):
        matches.append({
            "id": match["id"],
            "score": match["score"],
            "text": match["metadata"].get("text", ""),
            "source": match["metadata"].get("source", "Unknown"),
            "page": match["metadata"].get("page", "N/A"),
            "document_id": match["metadata"].get("document_id", ""),
        })

    return matches


async def delete_vectors(
    document_id: str,
    namespace: str = "general",
) -> None:
    """Delete all vectors associated with a document.

    Args:
        document_id: The document ID whose vectors should be deleted
        namespace: Pinecone namespace
    """
    index = get_index()
    # Delete by metadata filter
    index.delete(
        filter={"document_id": document_id},
        namespace=namespace,
    )
