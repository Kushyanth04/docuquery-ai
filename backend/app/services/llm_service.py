"""
LLM service supporting Google Gemini (free) and OpenAI GPT (optional).
Gemini used as default for zero-cost operation.
"""

from typing import List, Dict, AsyncGenerator
from app.config import get_settings





async def generate_answer_groq(
    question: str,
    context_chunks: List[Dict],
    stream: bool = False,
) -> str | AsyncGenerator[str, None]:
    """Generate answer using Groq API (FREE tier).

    Model: llama-3.3-70b-versatile
    Free tier: 30 requests/minute, 14.4K requests/day
    """
    from groq import Groq

    settings = get_settings()
    client = Groq(api_key=settings.groq_api_key)

    context = "\n\n---\n\n".join([
        f"[Source: {chunk['source']}, Page: {chunk.get('page', 'N/A')}]\n{chunk['text']}"
        for chunk in context_chunks
    ])

    messages = [
        {
            "role": "system",
            "content": (
                "You are DocuQuery AI, a helpful document Q&A assistant. "
                "Answer questions based ONLY on the provided context. "
                "If the answer is not in the context, say so. "
                "Always cite source documents and page numbers."
            ),
        },
        {
            "role": "user",
            "content": f"CONTEXT:\n{context}\n\nQUESTION: {question}",
        },
    ]

    if stream:
        async def _stream():
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                stream=True,
                temperature=0.3,
                max_tokens=1024,
            )
            for chunk in response:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield delta.content
        return _stream()
    else:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3,
            max_tokens=1024,
        )
        return response.choices[0].message.content


async def generate_answer(
    question: str,
    context_chunks: List[Dict],
    stream: bool = False,
    provider: str = None,
) -> str | AsyncGenerator[str, None]:
    """Generate answer using Groq API.

    Args:
        question: User's question
        context_chunks: List of dicts with 'text', 'source', 'page' keys
        stream: If True, returns an async generator for streaming
        provider: Ignored (forced to Groq)
    """
    return await generate_answer_groq(question, context_chunks, stream)
