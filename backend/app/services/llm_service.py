"""
LLM service supporting Google Gemini (free) and OpenAI GPT (optional).
Gemini used as default for zero-cost operation.
"""

from typing import List, Dict, AsyncGenerator
from app.config import get_settings


async def generate_answer_gemini(
    question: str,
    context_chunks: List[Dict],
    stream: bool = False,
) -> str | AsyncGenerator[str, None]:
    """Generate answer using Google Gemini API (FREE tier).

    Model: gemini-2.0-flash
    Free tier: 15 requests/minute
    """
    import google.generativeai as genai

    settings = get_settings()
    genai.configure(api_key=settings.google_api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    context = "\n\n---\n\n".join([
        f"[Source: {chunk['source']}, Page: {chunk.get('page', 'N/A')}]\n{chunk['text']}"
        for chunk in context_chunks
    ])

    prompt = f"""You are a helpful document Q&A assistant called DocuQuery AI. 
Answer the user's question based ONLY on the provided document context below. 
If the answer cannot be found in the context, say "I couldn't find the answer in the uploaded documents."
Always cite which source document and page the information came from.

CONTEXT:
{context}

QUESTION: {question}

Provide a clear, well-structured answer with source citations."""

    if stream:
        async def _stream():
            response = model.generate_content(prompt, stream=True)
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        return _stream()
    else:
        response = model.generate_content(prompt)
        return response.text


async def generate_answer_openai(
    question: str,
    context_chunks: List[Dict],
    stream: bool = False,
) -> str | AsyncGenerator[str, None]:
    """Generate answer using OpenAI GPT-3.5-turbo (paid).

    Model: gpt-3.5-turbo
    Cost: ~$0.0005 per 1K tokens
    """
    from openai import OpenAI

    settings = get_settings()
    client = OpenAI(api_key=settings.openai_api_key)

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
                model="gpt-3.5-turbo",
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
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.3,
            max_tokens=1024,
        )
        return response.choices[0].message.content


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
    """Generate answer using the configured LLM provider.

    Args:
        question: User's question
        context_chunks: List of dicts with 'text', 'source', 'page' keys
        stream: If True, returns an async generator for streaming
        provider: Override provider ("groq", "gemini", or "openai")
    """
    settings = get_settings()
    provider = provider or settings.llm_provider

    if provider == "openai":
        return await generate_answer_openai(question, context_chunks, stream)
    elif provider == "gemini":
        return await generate_answer_gemini(question, context_chunks, stream)
    else:
        return await generate_answer_groq(question, context_chunks, stream)
