import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # LLM Provider
    llm_provider: str = "gemini"  # "gemini" or "openai"
    google_api_key: str = ""
    openai_api_key: str = ""

    # Embedding Provider
    embedding_provider: str = "huggingface"  # "huggingface" or "openai"
    huggingface_api_key: str = ""

    # Pinecone
    pinecone_api_key: str = ""
    pinecone_index: str = "docuquery-index"
    pinecone_environment: str = "us-east-1"

    # Supabase
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_service_key: str = ""

    # Redis
    redis_url: str = "redis://localhost:6379"

    # App
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
