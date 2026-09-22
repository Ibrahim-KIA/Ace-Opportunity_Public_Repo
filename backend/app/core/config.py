from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_uri: str = ""
    anthropic_api_key: str = ""
    cors_origins: str = "*"

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
