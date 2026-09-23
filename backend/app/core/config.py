import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_uri: str = ""
    google_api_key: str = ""
    gemini_api_key: str = ""
    anthropic_api_key: str = ""
    cors_origins: str = "*"
    mock_llm: bool = False

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def effective_gemini_key(self) -> str:
        """Return either google_api_key or gemini_api_key, checking env vars as well."""
        return (
            self.google_api_key
            or self.gemini_api_key
            or os.getenv("GOOGLE_API_KEY", "")
            or os.getenv("GEMINI_API_KEY", "")
        )

    @property
    def effective_anthropic_key(self) -> str:
        """Return anthropic_api_key, checking env vars as well."""
        return self.anthropic_api_key or os.getenv("ANTHROPIC_API_KEY", "")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
