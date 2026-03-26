"""
Document classification router.
Standalone endpoint for classifying text/document content into categories.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict

from app.services.classifier import classify_document, get_category_probabilities, CATEGORIES

router = APIRouter(prefix="/classify", tags=["Classification"])


# ==================== Models ====================

class ClassifyRequest(BaseModel):
    text: str


class ClassifyResponse(BaseModel):
    category: str
    confidence: float
    probabilities: Dict[str, float]
    categories: list


# ==================== Endpoints ====================

@router.post("/", response_model=ClassifyResponse)
async def classify_text(request: ClassifyRequest):
    """Classify text content into a document category.

    Uses TfidfVectorizer + MultinomialNB pipeline.
    Categories: legal, medical, technical, financial, general
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text content is required")

    try:
        category, confidence = classify_document(request.text)
        probabilities = get_category_probabilities(request.text)

        return ClassifyResponse(
            category=category,
            confidence=confidence,
            probabilities=probabilities,
            categories=CATEGORIES,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


@router.get("/categories")
async def list_categories():
    """List all available document categories."""
    return {"categories": CATEGORIES}
