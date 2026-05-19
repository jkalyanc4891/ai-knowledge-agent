from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" # Prevents crashing if extra vars are in Render
    )
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

    # ==========================================
    # VALIDATORS (Strips accidental whitespaces,
    # newlines (\n), and carriage returns (\r)
    # from the API key to prevent HTTP Header protocol errors.)
    # ==========================================
    @field_validator("OPENAI_API_KEY")
    @classmethod
    def sanitize_api_key(cls, v: str | None) -> str | None:
        if v:
            return v.strip().replace("\n", "").replace("\r", "")
        return v

settings = Settings()