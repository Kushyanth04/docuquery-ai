"""
Query router for RAG-powered document Q&A.
Implements: cache check → embed question → Pinecone search → LLM answer → cache store.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional

from app.routers.auth import get_current_user
from app.services.embeddings import get_embeddings
from app.services.pinecone_service import query_vectors
from app.services.llm_service import generate_answer
from app.services.redis_cache import get_cached_response, set_cached_response
from app.services.supabase_service import save_chat_message, get_chat_history

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/query", tags=["Query"])


# ==================== Models ====================

class QueryRequest(BaseModel):
    question: str
    document_id: Optional[str] = None
    namespace: Optional[str] = None
    top_k: int = 5


class SourceCitation(BaseModel):
    text: str
    source: str
    page: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceCitation]
    cached: bool = False
    question: str


class ChatHistoryItem(BaseModel):
    question: str
    answer: str
    sources: list
    cached: bool
    created_at: Optional[str] = None


# ==================== Endpoints ====================

@router.post("/", response_model=QueryResponse)
async def ask_question(
    request: QueryRequest,
    user: dict = Depends(get_current_user),
):
    """Ask a question about uploaded documents.

    Pipeline:
    1. Check Redis cache for previously answered query
    2. Generate embedding for the question
    3. Search Pinecone for top-k similar chunks
    4. Pass context + question to LLM for answer generation
    5. Cache the response in Redis (1 hour TTL)
    6. Save Q&A to Supabase chat_history
    """
    namespace = request.namespace

    try:
        # Step 1: Check Redis cache
        cache_key_ns = f"{namespace or 'all'}:{request.document_id or 'all'}"
        cached = await get_cached_response(request.question, cache_key_ns)

        if cached:
            logger.info("Returning cached response")
            # Save to chat history even if cached
            await save_chat_message(
                user_id=user["id"],
                document_id=request.document_id or "",
                question=request.question,
                answer=cached["answer"],
                sources=cached["sources"],
                cached=True,
            )
            return QueryResponse(**cached, cached=True, question=request.question)

        # Step 2: Generate embedding for the question
        logger.info("Generating question embedding...")
        question_embedding = (await get_embeddings([request.question]))[0]

        # Step 3: Search Pinecone for similar chunks
        filter_dict = None
        if request.document_id:
            filter_dict = {"document_id": request.document_id}

        matches = []
        if namespace:
            # Search specific namespace
            logger.info(f"Searching Pinecone namespace '{namespace}' for top {request.top_k} matches")
            matches = await query_vectors(
                query_embedding=question_embedding,
                namespace=namespace,
                top_k=request.top_k,
                filter_dict=filter_dict,
            )
        else:
            # Search ALL namespaces and merge results
            all_namespaces = ["general", "technical", "legal", "medical", "financial"]
            logger.info(f"Searching all Pinecone namespaces for top {request.top_k} matches")
            for ns in all_namespaces:
                ns_matches = await query_vectors(
                    query_embedding=question_embedding,
                    namespace=ns,
                    top_k=request.top_k,
                    filter_dict=filter_dict,
                )
                matches.extend(ns_matches)
            # Sort by score and take top_k
            matches.sort(key=lambda m: m["score"], reverse=True)
            matches = matches[:request.top_k]

        if not matches:
            return QueryResponse(
                answer="I couldn't find any relevant documents to answer your question. Please upload some documents first.",
                sources=[],
                cached=False,
                question=request.question,
            )

        # Step 4: Generate answer with LLM
        logger.info("Generating answer with LLM...")
        context_chunks = [
            {
                "text": m["text"],
                "source": m["source"],
                "page": str(m["page"]),
            }
            for m in matches
        ]

        answer = await generate_answer(
            question=request.question,
            context_chunks=context_chunks,
            stream=False,
        )

        # Build source citations
        sources = [
            SourceCitation(
                text=m["text"][:200] + "..." if len(m["text"]) > 200 else m["text"],
                source=m["source"],
                page=str(m["page"]),
                score=m["score"],
            )
            for m in matches
        ]

        response_data = {
            "answer": answer,
            "sources": [s.model_dump() for s in sources],
        }

        # Step 5: Cache response in Redis (1 hour TTL)
        await set_cached_response(request.question, response_data, cache_key_ns)

        # Step 6: Save to chat history
        await save_chat_message(
            user_id=user["id"],
            document_id=request.document_id or "",
            question=request.question,
            answer=answer,
            sources=[s.model_dump() for s in sources],
            cached=False,
        )

        return QueryResponse(
            answer=answer,
            sources=sources,
            cached=False,
            question=request.question,
        )

    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.post("/stream")
async def ask_question_stream(
    request: QueryRequest,
    user: dict = Depends(get_current_user),
):
    """Ask a question with streaming response via Server-Sent Events (SSE).

    Same pipeline as /query but returns answer progressively via SSE.
    """
    namespace = request.namespace

    try:
        # Check cache first
        cache_key_ns = f"{namespace or 'all'}:{request.document_id or 'all'}"
        cached = await get_cached_response(request.question, cache_key_ns)

        if cached:
            async def stream_cached():
                import json
                yield f"data: {json.dumps({'type': 'sources', 'data': cached['sources']})}\n\n"
                yield f"data: {json.dumps({'type': 'answer', 'data': cached['answer']})}\n\n"
                yield f"data: {json.dumps({'type': 'done', 'cached': True})}\n\n"

            return StreamingResponse(stream_cached(), media_type="text/event-stream")

        # Generate question embedding
        question_embedding = (await get_embeddings([request.question]))[0]

        # Search Pinecone
        filter_dict = {"document_id": request.document_id} if request.document_id else None

        matches = []
        if namespace:
            matches = await query_vectors(
                query_embedding=question_embedding,
                namespace=namespace,
                top_k=request.top_k,
                filter_dict=filter_dict,
            )
        else:
            all_namespaces = ["general", "technical", "legal", "medical", "financial"]
            for ns in all_namespaces:
                ns_matches = await query_vectors(
                    query_embedding=question_embedding,
                    namespace=ns,
                    top_k=request.top_k,
                    filter_dict=filter_dict,
                )
                matches.extend(ns_matches)
            matches.sort(key=lambda m: m["score"], reverse=True)
            matches = matches[:request.top_k]

        context_chunks = [
            {
                "text": m["text"],
                "source": m["source"],
                "page": str(m["page"]),
            }
            for m in matches
        ]

        sources = [
            {
                "text": m["text"][:200] + "..." if len(m["text"]) > 200 else m["text"],
                "source": m["source"],
                "page": str(m["page"]),
                "score": m["score"],
            }
            for m in matches
        ]

        async def event_stream():
            import json
            # Send sources first
            yield f"data: {json.dumps({'type': 'sources', 'data': sources})}\n\n"

            # Stream answer chunks
            full_answer = ""
            answer_generator = await generate_answer(
                question=request.question,
                context_chunks=context_chunks,
                stream=True,
            )

            async for chunk in answer_generator:
                full_answer += chunk
                yield f"data: {json.dumps({'type': 'chunk', 'data': chunk})}\n\n"

            # Cache complete response
            await set_cached_response(
                request.question,
                {"answer": full_answer, "sources": sources},
                cache_key_ns,
            )

            # Save to chat history
            await save_chat_message(
                user_id=user["id"],
                document_id=request.document_id or "",
                question=request.question,
                answer=full_answer,
                sources=sources,
                cached=False,
            )

            yield f"data: {json.dumps({'type': 'done', 'cached': False})}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    except Exception as e:
        logger.error(f"Stream query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=List[ChatHistoryItem])
async def get_query_history(
    document_id: Optional[str] = None,
    user: dict = Depends(get_current_user),
):
    """Get chat history for the current user."""
    try:
        history = await get_chat_history(user["id"], document_id)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
