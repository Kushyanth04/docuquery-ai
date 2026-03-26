"""
Document upload and management router.
Handles PDF upload → text extraction → chunking → classification → embedding → storage pipeline.
"""

import uuid
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from io import BytesIO

from app.routers.auth import get_current_user
from app.services.embeddings import get_embeddings
from app.services.pinecone_service import upsert_vectors, delete_vectors
from app.services.classifier import classify_document
from app.services.supabase_service import (
    save_upload_record,
    get_upload_history,
    delete_upload_record,
    upload_file_to_storage,
    delete_file_from_storage,
)
from app.services.redis_cache import invalidate_cache

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents"])


# ==================== Models ====================

class UploadResponse(BaseModel):
    document_id: str
    filename: str
    category: str
    confidence: float
    chunk_count: int
    message: str


class DocumentRecord(BaseModel):
    id: Optional[int] = None
    document_id: str
    filename: str
    category: str
    chunk_count: int
    file_size: int
    storage_path: str
    created_at: Optional[str] = None


class DeleteResponse(BaseModel):
    message: str
    document_id: str


# ==================== Helper Functions ====================

def extract_text_from_pdf(file_bytes: bytes) -> List[dict]:
    """Extract text from PDF file, returning text per page.

    Args:
        file_bytes: Raw PDF file bytes

    Returns:
        List of dicts with 'text' and 'page' keys
    """
    reader = PdfReader(BytesIO(file_bytes))
    pages = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            pages.append({
                "text": text.strip(),
                "page": i + 1,
            })

    return pages


def chunk_text(pages: List[dict], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[dict]:
    """Split page texts into smaller chunks using LangChain.

    Args:
        pages: List of page dicts from extract_text_from_pdf
        chunk_size: Maximum chunk size in characters
        chunk_overlap: Overlap between chunks

    Returns:
        List of chunk dicts with 'text', 'page', and 'chunk_index' keys
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = []
    chunk_index = 0

    for page_data in pages:
        page_chunks = splitter.split_text(page_data["text"])
        for chunk_text_content in page_chunks:
            chunks.append({
                "text": chunk_text_content,
                "page": page_data["page"],
                "chunk_index": chunk_index,
            })
            chunk_index += 1

    return chunks


# ==================== Endpoints ====================

@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    """Upload a PDF document for processing.

    Pipeline:
    1. Extract text from PDF (PyPDF2)
    2. Classify document category (scikit-learn)
    3. Chunk text (LangChain RecursiveCharacterTextSplitter)
    4. Generate embeddings (HuggingFace/OpenAI)
    5. Store vectors in Pinecone (namespace by category)
    6. Save metadata to Supabase
    7. Upload PDF to Supabase Storage
    """
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        # Read file
        file_bytes = await file.read()
        file_size = len(file_bytes)
        document_id = str(uuid.uuid4())

        # Step 1: Extract text from PDF
        logger.info(f"Extracting text from {file.filename}")
        pages = extract_text_from_pdf(file_bytes)
        if not pages:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")

        full_text = " ".join([p["text"] for p in pages])

        # Step 2: Classify document
        logger.info("Classifying document...")
        category, confidence = classify_document(full_text)
        logger.info(f"Document classified as '{category}' ({confidence:.2%})")

        # Step 3: Chunk text
        logger.info("Chunking text with LangChain...")
        chunks = chunk_text(pages)
        logger.info(f"Generated {len(chunks)} chunks")

        # Step 4: Generate embeddings
        logger.info("Generating embeddings...")
        chunk_texts = [c["text"] for c in chunks]
        embeddings = await get_embeddings(chunk_texts)

        # Step 5: Store in Pinecone (namespace = category)
        logger.info(f"Storing {len(embeddings)} vectors in Pinecone namespace '{category}'")
        vector_ids = [f"{document_id}_{i}" for i in range(len(chunks))]
        metadata_list = [
            {
                "text": chunk["text"],
                "source": file.filename,
                "page": chunk["page"],
                "chunk_index": chunk["chunk_index"],
                "document_id": document_id,
                "user_id": user["id"],
                "category": category,
            }
            for chunk in chunks
        ]
        await upsert_vectors(embeddings, metadata_list, vector_ids, namespace=category)

        # Step 6: Upload PDF to Supabase Storage
        storage_path = f"{user['id']}/{document_id}/{file.filename}"
        await upload_file_to_storage(file_bytes, storage_path)

        # Step 7: Save metadata to Supabase DB
        await save_upload_record(
            user_id=user["id"],
            filename=file.filename,
            document_id=document_id,
            category=category,
            chunk_count=len(chunks),
            file_size=file_size,
            storage_path=storage_path,
        )

        # Invalidate cache (new documents might change answers)
        await invalidate_cache()

        return UploadResponse(
            document_id=document_id,
            filename=file.filename,
            category=category,
            confidence=confidence,
            chunk_count=len(chunks),
            message=f"Document uploaded and indexed successfully. Classified as '{category}'.",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/history", response_model=List[DocumentRecord])
async def get_documents(user: dict = Depends(get_current_user)):
    """Get the current user's upload history."""
    try:
        history = await get_upload_history(user["id"])
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{document_id}", response_model=DeleteResponse)
async def delete_document(
    document_id: str,
    user: dict = Depends(get_current_user),
):
    """Delete a document and its vectors."""
    try:
        # Get document record to find category/namespace and storage path
        history = await get_upload_history(user["id"])
        doc_record = next(
            (d for d in history if d["document_id"] == document_id),
            None,
        )

        if not doc_record:
            raise HTTPException(status_code=404, detail="Document not found")

        # Delete vectors from Pinecone
        await delete_vectors(document_id, namespace=doc_record["category"])

        # Delete file from Supabase Storage
        await delete_file_from_storage(doc_record["storage_path"])

        # Delete DB record
        await delete_upload_record(document_id, user["id"])

        # Invalidate cache
        await invalidate_cache()

        return DeleteResponse(
            message="Document deleted successfully",
            document_id=document_id,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
