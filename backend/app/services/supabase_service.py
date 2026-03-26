"""
Supabase service for authentication, database operations, and file storage.
"""

from typing import Optional, Dict, List
from supabase import create_client, Client
from app.config import get_settings

_supabase_client: Optional[Client] = None


def init_supabase() -> Client:
    """Initialize Supabase client."""
    global _supabase_client
    settings = get_settings()
    _supabase_client = create_client(settings.supabase_url, settings.supabase_key)
    return _supabase_client


def get_supabase() -> Client:
    """Get the Supabase client instance."""
    global _supabase_client
    if _supabase_client is None:
        return init_supabase()
    return _supabase_client


# ==================== Authentication ====================

async def signup_user(email: str, password: str) -> Dict:
    """Sign up a new user with Supabase Auth."""
    client = get_supabase()
    response = client.auth.sign_up({"email": email, "password": password})
    return {
        "user": {
            "id": response.user.id,
            "email": response.user.email,
        } if response.user else None,
        "session": {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
        } if response.session else None,
    }


async def login_user(email: str, password: str) -> Dict:
    """Login user with email and password."""
    client = get_supabase()
    response = client.auth.sign_in_with_password({
        "email": email,
        "password": password,
    })
    return {
        "user": {
            "id": response.user.id,
            "email": response.user.email,
        },
        "session": {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
        },
    }


async def get_user_from_token(token: str) -> Optional[Dict]:
    """Verify JWT token and return user info."""
    client = get_supabase()
    try:
        response = client.auth.get_user(token)
        if response.user:
            return {
                "id": response.user.id,
                "email": response.user.email,
            }
        return None
    except Exception:
        return None


# ==================== Database Operations ====================

async def save_upload_record(
    user_id: str,
    filename: str,
    document_id: str,
    category: str,
    chunk_count: int,
    file_size: int,
    storage_path: str,
) -> Dict:
    """Save document upload metadata to Supabase."""
    client = get_supabase()
    data = {
        "user_id": user_id,
        "filename": filename,
        "document_id": document_id,
        "category": category,
        "chunk_count": chunk_count,
        "file_size": file_size,
        "storage_path": storage_path,
    }
    result = client.table("upload_history").insert(data).execute()
    return result.data[0] if result.data else {}


async def get_upload_history(user_id: str) -> List[Dict]:
    """Get upload history for a user."""
    client = get_supabase()
    result = (
        client.table("upload_history")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data or []


async def delete_upload_record(document_id: str, user_id: str) -> bool:
    """Delete an upload record."""
    client = get_supabase()
    result = (
        client.table("upload_history")
        .delete()
        .eq("document_id", document_id)
        .eq("user_id", user_id)
        .execute()
    )
    return len(result.data) > 0 if result.data else False


async def save_chat_message(
    user_id: str,
    document_id: str,
    question: str,
    answer: str,
    sources: List[Dict],
    cached: bool = False,
) -> Dict:
    """Save a chat Q&A pair to history."""
    client = get_supabase()
    data = {
        "user_id": user_id,
        "document_id": document_id,
        "question": question,
        "answer": answer,
        "sources": sources,
        "cached": cached,
    }
    result = client.table("chat_history").insert(data).execute()
    return result.data[0] if result.data else {}


async def get_chat_history(user_id: str, document_id: str = None) -> List[Dict]:
    """Get chat history for a user, optionally filtered by document."""
    client = get_supabase()
    query = (
        client.table("chat_history")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(50)
    )
    if document_id:
        query = query.eq("document_id", document_id)
    result = query.execute()
    return result.data or []


# ==================== File Storage ====================

async def upload_file_to_storage(
    file_bytes: bytes,
    file_path: str,
    content_type: str = "application/pdf",
) -> str:
    """Upload file to Supabase Storage.

    Args:
        file_bytes: File content
        file_path: Path in storage bucket (e.g., "user_id/filename.pdf")
        content_type: MIME type

    Returns:
        Public URL of the uploaded file
    """
    client = get_supabase()
    bucket_name = "documents"

    # Upload file
    client.storage.from_(bucket_name).upload(
        path=file_path,
        file=file_bytes,
        file_options={"content-type": content_type},
    )

    # Get public URL
    url = client.storage.from_(bucket_name).get_public_url(file_path)
    return url


async def delete_file_from_storage(file_path: str) -> bool:
    """Delete file from Supabase Storage."""
    client = get_supabase()
    try:
        client.storage.from_("documents").remove([file_path])
        return True
    except Exception:
        return False
