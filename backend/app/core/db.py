from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .config import get_settings

_client: AsyncIOMotorClient | None = None


def _get_client() -> AsyncIOMotorClient:
    global _client
    settings = get_settings()
    if not settings.mongodb_uri:
        raise RuntimeError(
            "MONGODB_URI is not configured. Set it in your .env file or environment."
        )
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongodb_uri)
    return _client


def get_database() -> AsyncIOMotorDatabase:
    """Return the 'nextstep' database handle."""
    return _get_client()["nextstep"]
