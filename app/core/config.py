from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "AI Knowledge & Decision Support System"
    APP_ENV: str = Field("local", description="Environment: local | dev | prod")

    # --- API ---
    API_V1_PREFIX: str = "/api"

    # --- Vector DB Backend ---
    VECTOR_DB_BACKEND: str = Field("chroma", description="Vector store backend")

    # --- OpenAI / LLM ---
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-5.4-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-large"

    # --- Logging ---
    LOG_LEVEL: str = "INFO"

    # --- Chroma Persistence ---
    CHROMA_PERSIST_DIR: str | None = ".chroma"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()